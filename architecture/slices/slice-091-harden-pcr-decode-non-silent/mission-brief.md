# Slice 091: harden-pcr-decode-non-silent

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-30 residual #1 (the only open Major-severity finding) — the non-UTF-8 silent claim-drop that re-admits the VAULT_CLAIM bypass slice-090 closed only for the host-locale (cp1252) case.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-090 added `encoding="utf-8"` to the resolver's git subprocess decode sites, closing the host-locale (cp1252) crash. But a **genuinely** non-UTF-8 git payload still defeats the strict UTF-8 decode, and `_git_show_stage` handles it the wrong way: a swallowed pipe-reader thread (Windows) yields a falsy `''`/`None` that the caller's `parse_queue_text(text) if text else {}` guard silently drops — re-opening the exact VAULT_CLAIM claim-drop bypass — or an uncaught `UnicodeDecodeError` escapes (POSIX), since `_git_show_stage` catches only `CalledProcessError`/`FileNotFoundError`. This slice makes the resolver's conflict-stage decode **fail closed and loud** on non-UTF-8 bytes instead of dropping a claim silently.

## Acceptance criteria

1. The failing repro test `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` PASSES at slice end (BFRD-1 mandatory).
2. `_git_show_stage` on a **present but non-UTF-8** conflict stage produces a controlled fail-closed outcome — distinguishable from the legitimate empty-`""` "stage absent" sentinel — never a silent falsy claim-drop and never an uncaught `UnicodeDecodeError`.
3. The claim-extraction caller path (`diagnose_conflict` / `_extract_claim_diff`) treats that fail-closed signal as a STOP (does NOT auto-resolve or drop the claim) and records an audit breadcrumb naming the undecodable stage + path — the failure is visible, not silent.
4. No regression: slice-090's cp1252 behavioral repro (shippability #95) stays green; the AST encoding count-pin (#96) is **deliberately updated 9→8 decode / 4→5 byte-mode** (the fix converts `_git_show_stage` to a byte-read-decode site — see design.md / [[ADR-083]]) and passes; the full `parallel_conflict_resolver` test suite stays green.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0) — the AC1 repro is already WRITTEN-FAILING (established by `/repro` before this slice).

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | bug-repro | tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py | test_git_show_stage_fails_closed_on_non_utf8_stage | WRITTEN-FAILING |
| 2 | unit | tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py | test_present_stage_distinguished_from_absent_stage | PENDING |
| 3 | unit | tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py | test_undecodable_stage_records_audit_breadcrumb | PENDING |
| 4 | regression | tests/bugs/test_pcr_git_subprocess_cp1252_decode.py | (slice-090 cp1252 behavioral repro — unchanged) | PASSING |
| 4 | count-pin update | tests/methodology/test_parallel_conflict_resolver_git_encoding.py | (slice-090 AST pin — updated 9→8 / 4→5 by this slice) | PENDING |

(Test paths/names for AC2/AC3 are provisional — `/design-slice` finalizes them.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Repro passes | `$PY -m pytest tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py -q` → 1 passed |
| 2 | Present≠absent fail-closed | Unit test: a stage populated with invalid UTF-8 bytes yields the STOP signal; an absent stage still yields `""`; the two are distinguishable by the caller |
| 3 | Caller STOP + breadcrumb | Unit test on `diagnose_conflict`/`_extract_claim_diff`: an undecodable claim stage produces a STOP (no auto-resolve) and an audit-log line naming stage+path |
| 4 | No regression + count-pin update | `$PY -m pytest tests/bugs/test_pcr_git_subprocess_cp1252_decode.py tests/methodology/test_parallel_conflict_resolver_git_encoding.py -q` green (the latter updated to 8/5); full resolver suite green |

## Must-not-defer

- [ ] Distinguish "stage absent" (legitimate `""`) from "stage present but undecodable" (fail-closed STOP) — conflating the two is the trap that produced this residual.
- [ ] Observability: an audit/log breadcrumb on every fail-closed decode path (never silent).
- [ ] Rewrite `_git_show_stage`'s docstring (L709-716) to **invert** the caller-tolerance contract (per /critique-review m1 elevation): post-fix it must document "present-but-undecodable → raises `_StageDecodeError`", NOT the current "callers must tolerate a falsy value (`parse_queue_text(text) if text else {}`)". The stale sentence documents the *exact removed dangerous contract* and would guide a future caller back into the falsy-tolerant trap that re-opens R-30 residual #1 — a correctness-adjacent doc defect, not cosmetic trim.
- [ ] Cover BOTH manifestations — the swallowed-reader-thread falsy return (Windows) AND the propagated `UnicodeDecodeError` (POSIX). NOTE (design M3): the bytes-mode fix **converges** both into one main-thread `UnicodeDecodeError → _StageDecodeError` path, so this is discharged by the pre-fix repro (documents both) + ONE post-fix converged-raise test — NOT a monkeypatched synthetic "Windows-falsy" post-fix test (it would assert an unreachable state).
- [ ] Do NOT add `encoding=` to the byte-mode STAGING sites (they correctly do not decode). slice-090's AST count-pin moves 9→8 decode / 4→5 byte-mode because `_git_show_stage` becomes a byte-read-decode site (carrying no `encoding=`, decoding explicitly); the 4 staging sites stay untouched.

## Out of scope

- Repo-wide `text=True`-without-`encoding=` sweep across other `tools/*.py` — that is the queued `audit-cp1252-decode-pattern-across-tools` candidate (R-30 discovery), not this slice.
- R-30 residual #2 (the UTF-8 CI behavioral-coverage limitation) — a separate concern.
- The resolver's non-claim-bearing decode sites (HEAD sha, `git status --porcelain`, diff scans), UNLESS the chosen fix is a shared decode helper that naturally subsumes them (design's call) — no separate ACs are claimed for them here.

## Dependencies

- Prior slices: [[slice-090-fix-pcr-git-subprocess-cp1252-decode]] — this hardens the residual its `encoding="utf-8"` fix left open; reuses ADR-082's "predicate kernel as reuse seam".
- Failing repro (BFRD-1): `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py::test_git_show_stage_fails_closed_on_non_utf8_stage`
- Vault refs: [[risk-register#R-30]] (residual #1), [[decisions/ADR-082]]
- Code: `tools/parallel_conflict_resolver.py` (`_git_show_stage` L708, `_extract_claim_diff` L808, `diagnose_conflict`)

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m pytest tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py tests/methodology/test_parallel_conflict_resolver_git_encoding.py -q
```
Expected: the repro now PASSES and the slice-090 AST count-pin PASSES at its **updated** 8-decode/5-byte-mode values. If the counts land anywhere other than 8/5 (e.g. a staging site lost its byte-mode, or a second decode site was converted): STOP — the fix changed a site's mode incorrectly.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints

## Branch / worktree note

Per the slice-090 `/reflect` directive (and memory `next-slice-use-worktree-not-skip`): this slice MUST run in a real BRANCH-2 worktree at `/build-slice` — **no `WORKTREE=skip`**. slice-090's in-place build was forced by entangled parallel scaffolds; the tree is clean now (verified `git status` at `/slice`), so there is no blocker to a proper worktree.
