# Code Review: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-31
**Result**: FINDINGS (minors only — no blockers, no majors)

## Summary
The fix is correct, complete, and minimal. All 9 `text=True` git decode sites carry `encoding="utf-8"`; all 4 byte-mode staging sites correctly do NOT. The AST guard classifies all 13 sites accurately and the count-pins are right. The `text=True`+`encoding=` pairing is documented Python best practice (not redundant). Two minor docstring/comment imprecisions, no functional defects. Both minors applied in-slice.

## Changed files (in-scope)
```
tools/parallel_conflict_resolver.py
tests/bugs/test_pcr_git_subprocess_cp1252_decode.py
tests/methodology/test_parallel_conflict_resolver_git_encoding.py
```

## Findings

### Blockers
None.

### Majors
None.

### Minors

#### m1: test docstring conflated `_git_show_stage`'s `None` return-path with the `except → ""` branch
- **Issue**: `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` prose said "`_git_show_stage` returns `None`" without clarifying the `None` comes from `return proc.stdout` (the success path, where `proc.stdout` is `None` after the reader-thread decode failure) — NOT the `except` branch's `""`. End-state correct; mechanism prose imprecise (Wiegers Dim 1).
- **Builder disposition**: APPLIED IN-SLICE — reworded the test docstring to "`_git_show_stage`'s `return proc.stdout` (the success path — NOT the `except` branch's `""`) hands back that `None`."

#### m2: `_git_show_stage` docstring said "Returns empty string on subprocess failure" — silent on the `None` passthrough
- **Issue**: `tools/parallel_conflict_resolver.py:711` documented only the `except → ""` path; silent that `return proc.stdout` can hand back `None`. The slice's whole premise is this function's decode contract → cheapest moment to make it honest (Dim 5 / Newman; in-scope per "decode-contract slice").
- **Builder disposition**: APPLIED IN-SLICE — appended to the docstring: success returns `proc.stdout` decoded UTF-8 (per ADR-082), which may be `None`; callers must tolerate a falsy value (cross-refs `_extract_claim_diff`'s `if text else {}` guard).

## Probe responses (per the attack brief)
- **(a) All & only decode sites?** Yes — 13 total `subprocess.run`; 9 `text=True` sites all carry `encoding="utf-8"`; 4 byte-mode (`git add`/`rebase --continue`) carry neither. No Popen/check_output/communicate decode paths. (Brief's L1378/1384 were pre-edit estimates; actual byte-mode lines 1382/1388.)
- **(b) `text=True`+`encoding=` redundant?** No — documented Python best practice (`text=True` selects text mode, `encoding=` the codec); the exact remediation for cpython #105312 et al.
- **(c) AST guard classification?** Correct — keys on `text=True`-presence (not raw `capture_output`); count-pins 9/4 match; a future variable-`text` arg would fail-loud on the count mismatch.
- **(d) Repro skipif / flake?** `_host_decodes_utf8_natively()` correct (catches `UnicodeDecodeError`+`LookupError`; skip≠masked-pass); no flake — assertion keys on return value, not captured stderr; `rebase check=False` tolerates the expected conflict exit.
- **(e) Residual None on non-UTF-8 payload?** Handled — strict-decode-fail → `None` → `_extract_claim_diff` `if text else {}` → `{}`. Same graceful degradation; strict-errors sound (all content is UTF-8 vault markdown). Documented residual (m1 of /critique-review → /reflect risk).
- **(f) Idiom conformance?** Conforms — `capture_output → text → encoding → check` ordering matches the module's existing `write_text(..., encoding="utf-8")` convention.

## Dimensions checked
- [x] Unfounded assumptions — m1 (test-docstring mechanism; assertions sound)
- [x] Missing edge cases — none (empty/malformed/CRLF all handled; no concurrency surface)
- [x] Over-engineering — none (9 one-line additions; AST guard is a real recurrence guard)
- [x] Under-engineering — none (AC1/AC2/AC3 all have code/test elements)
- [x] Contract gaps — m2 (`_git_show_stage` docstring `None`-passthrough; applied)
- [x] Security — none; strict-decode narrows (not widens) the trust surface
- [x] Drift from vault — none (diff matches design.md + ADR-082; pre-edit line estimates ≠ drift)
- [x] Web-known issues — none against the fix (official Python docs + cpython #105312 / SuperClaude #492 / pip-audit #573 confirm the remediation; `text=` deprecation is a proposal, not landed)
- [x] Cross-cutting conformance — none (RSAD-1: slice's own AST audit passes on its module; APED-1: predicate checked against real 13-site battery; idiom verified)
