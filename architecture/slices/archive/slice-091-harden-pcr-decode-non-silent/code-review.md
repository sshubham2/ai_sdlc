# Code Review: Slice 091 harden-pcr-decode-non-silent

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-31
**Result**: FINDINGS (0 blockers / 0 majors / 3 minors — all addressed in-slice)

## Summary

The R-30 residual #1 fix is correct and well-targeted: `_git_show_stage` captures bytes and decodes explicitly in the main thread, converting the pre-fix silent reader-thread swallow (Windows `None`) / uncaught `UnicodeDecodeError` (POSIX) into a typed `_StageDecodeError` that fails closed to UNKNOWN STOP. The code-Critic validated the fix premise against the live cpython issue tracker (cpython#105312), confirmed the frozen-dataclass constructor-threading, the symmetric stage-2/stage-3 catch, and that the test fixtures exercise a REAL rebase conflict (not the dead `update-index --index-info` path — /critique B1). **0 blockers, 0 majors, 3 minors — all 3 addressed in-slice** (per the self-violation-law discipline for m2 + the "fail-closed invariant should be total" rationale for m1).

## Changed files (in-scope)
tools/parallel_conflict_resolver.py
tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py
tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py
tests/methodology/test_parallel_conflict_resolver_git_encoding.py
architecture/slices/slice-091-harden-pcr-decode-non-silent/build-log.md

## Findings

### Blockers
None.

### Majors
None.

### Minors

#### m1: `resolve_vault_claim_conflict`'s stage reads had no `_StageDecodeError` catch — defense-in-depth asymmetry vs the SOFT path
- **Claim under review**: `tools/parallel_conflict_resolver.py` `resolve_vault_claim_conflict` Step 3 stage reads.
- **Issue**: The SOFT path fails closed on a `_StageDecodeError` via the existing `except _SoftResolutionError` handler; the VAULT_CLAIM path (which auto-resolves + runs `git rebase --continue`) re-read both stages with no equivalent catch, so a `_StageDecodeError` there would propagate as an uncaught traceback rather than a controlled STOP. The Critic traced all reach-paths and confirmed it is **structurally pre-empted upstream** (a non-UTF-8 stage degrades `diagnose_conflict` → `classify_conflict` returns UNKNOWN, never VAULT_CLAIM; the collisions==0 STOP fires first) — a live defect only in the diagnose→resolve TOCTOU window (the ADR-067 cooperative-race regime). Hence Minor, not a live defect.
- **Disposition**: **ADDRESSED IN-SLICE** — wrapped the Step-3 stage reads in `try/except _StageDecodeError` → `ResolutionResult(STOP, UNKNOWN)` + best-effort `_append_decode_stop_audit`, mirroring the SOFT net. Makes the "non-UTF-8 stage always fails closed and LOUD" invariant total rather than path-dependent. No new subprocess site → count-pin unaffected. Re-ran resolver+vault_claim suite: 83 PASS.

#### m2: count-pin test docstring + assertion message said "4 byte-mode staging sites" but the constant is 5 (4 staging + 1 read-decode) — stale prose drift (self-violation)
- **Claim under review**: `tests/methodology/test_parallel_conflict_resolver_git_encoding.py:131-134` (docstring) + `:142` (assertion message).
- **Issue**: `_EXPECTED_BYTE_MODE_SITES = 5`; the 5th is `_git_show_stage`, a read-decode site, not a staging site. The module-level comment (L37-46) was correct but the test-function docstring + failure message lagged — a maintainer hitting the failure would be told to look for "staging sites." Cosmetic (the assertion compares the constant, not the prose).
- **Disposition**: **ADDRESSED IN-SLICE** — docstring → "5 byte-mode sites (4 staging + 1 read-decode `_git_show_stage`)"; assertion message → "byte-mode git sites (4 staging + 1 read-decode)". (Self-violation-law: a count-pin slice must not ship its own pin with stale count prose.)

#### m3: AC1 repro docstring's "returns None pre-fix" is a dev-host-specific historical assertion
- **Claim under review**: `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` module docstring.
- **Issue**: "returns None pre-fix" is a Windows reader-thread-local observation (the POSIX manifestation is an uncaught propagated `UnicodeDecodeError`); the post-fix test cannot re-demonstrate it. Not load-bearing — the test body handles both pre-fix manifestations and asserts only the post-fix LOUD outcome (the fixture-guard already defeats the B1 vacuous-absent-stage mode).
- **Disposition**: **ADDRESSED IN-SLICE** — softened to tag it as a dev-host (Windows) observation with the cpython#105312 reference and an explicit note that the assertion does not depend on which pre-fix manifestation occurs.

## Dimensions checked
- [x] Unfounded assumptions — m2 (count-pin "4 staging" prose vs constant 5), m3 (pre-fix `None` dev-host-specific). `_git_show_stage` decode-correctness docstring verified accurate vs implementation + live cpython issue.
- [x] Missing edge cases — none. Symmetric stage-2/stage-3 catch verified (m-add-2 `bad_stage=3` test). shippability-only conflict correctly does not read stages (degraded scoped behind the slice-queue `if`). Absent("")≠present-non-UTF-8(raise) pinned.
- [x] Over-engineering — none. `_StageDecodeError` minimal 3-line subclass reusing the existing UNKNOWN STOP channel; `_append_decode_stop_audit` mirrors `_append_skew_stop_audit`.
- [x] Under-engineering — none. All 4 ACs have delivering code; frozen+slots constructor-threading correct (no `FrozenInstanceError` mutation attempt). m1 (defense-in-depth asymmetry) addressed in-slice.
- [x] Contract gaps — none. `_StageDecodeError.__init__(message, stage, path)` super-call consistent; return contract (`""` | str | raise) documented + tested.
- [x] Security — none. Non-UTF-8 bytes are git-internal blob content treated as untrusted-and-fail-closed (secure-by-default). No secrets, no `shell=True`, breadcrumb writes only stage/path/SHA.
- [x] Drift from vault — none. MEPD-1 EXCLUDE honored (no RULE-ID/VERSION/plugin.yaml bump); ADR-082 byte-mode invariant preserved (count-pin enforces); slice-090 decode sites untouched.
- [x] Web-known issues — verified, no finding. Fix premise confirmed by cpython#105312 + bugs.python.org/issue34618; byte-capture + explicit-main-thread-decode is the community-recommended mitigation.
- [x] Cross-cutting conformance — none blocking. RSAD-1 (own count-pin green 9/5), APED-1 (executed against invalid-UTF-8 adversarial battery via real git, both stages), EOL-DRIFT-1 preserved. The m1 VAULT_CLAIM asymmetry was the one residual — addressed in-slice.

## Sources
- [cpython#105312 — subprocess.run() text encoding under Windows](https://github.com/python/cpython/issues/105312)
- [bugs.python.org issue34618 — encoding error in subprocess captured output](https://bugs.python.org/issue34618)
