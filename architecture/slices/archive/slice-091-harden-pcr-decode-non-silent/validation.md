# Validation: Slice 091 harden-pcr-decode-non-silent

**Date**: 2026-05-31
**Result**: PASS

This is a library/tooling slice (PCR conflict-resolver hardening) — "real environment" = the actual `venv` Python (`~/.claude/.venv`) executing the tests against **real `git` subprocess behavior** (real rebase conflicts, real non-UTF-8 blob bytes, real reader-thread decode), not mocks. The /critique B1 finding confirmed why this matters: the staging mechanism had to be validated against the real Windows `git.exe`, not reasoned about.

## Per-criterion results

### AC1: the failing repro `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` PASSES at slice end
- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py -q` → `1 passed in 0.52s`. The repro stages a REAL rebase conflict with non-UTF-8 bytes on stage 2 (fixture-guard asserts `\xff` present at exit 0), and `_git_show_stage` now raises the typed `_StageDecodeError` (caught by the test's `except Exception` → PASS), instead of the pre-fix falsy `None`.
- **Notes**: Host-locale-independent — runs for real on this Windows host AND on POSIX CI (no skip guard).

### AC2: `_git_show_stage` on a present-but-non-UTF-8 stage → controlled fail-closed, distinguishable from absent `""`, never falsy/never raw UnicodeDecodeError
- **Status**: PASS
- **Evidence**: `test_present_stage_distinguished_from_absent_stage` in `test_parallel_conflict_resolver_decode_fail_closed.py` — present non-UTF-8 → `_StageDecodeError` (conflict_class UNKNOWN, carries stage+path, NOT a UnicodeDecodeError); absent stage → `""`. Part of `6 passed in 2.81s`.

### AC3: caller path treats it as STOP (no auto-resolve/claim-drop) + audit breadcrumb naming stage+path
- **Status**: PASS
- **Evidence**: `test_undecodable_stage_records_audit_breadcrumb` (diagnose_conflict → `claim_extraction_degraded=True` + `## Decode-failure STOP (non-UTF-8 stage)` log section naming `**Undecodable stage**: 2` + path), `test_stage_3_undecodable_also_degrades` (m-add-2 symmetry), `test_classify_degraded_diagnostic_returns_unknown`, `test_resolve_soft_on_undecodable_stage_stops_no_writes` (STOP/UNKNOWN, rebase still in progress), `test_defense_in_depth_regen_slice_queue_fail_closed` (non-degraded stale diag → STOP via existing handler). 6/6 PASS. Plus /code-review m1 closed the VAULT_CLAIM-path defense-in-depth asymmetry — the fail-closed invariant is now total.

### AC4: no regression — cp1252 repro (#95) green; count-pin (#96) updated; full suite green
- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_parallel_conflict_resolver_git_encoding.py tests/bugs/test_pcr_git_subprocess_cp1252_decode.py -q` → `4 passed`. Count-pin holds at **9 decode / 5 byte-mode** (build correction: decode unchanged — the `_append_decode_stop_audit` rev-parse decode site offsets `_git_show_stage`). Full suite: **1295 passed** (twice — post-build + post-code-review-fixes).

## VAL-1 layered safety checks
- **Layer A (credentials)**: 0 secrets.
- **Layer B (dependency hallucination)**: 0 import findings (`--imports-allowlist tests`).
- **Result**: clean — both layers passed.

## Shippability catalog (regression check)
- **Pre-gates**: SCMD-1 clean (98 rows, incidental=0); PTFCD-1 clean (98 rows, 443 test-path tokens all exist).
- **Runner**: `$PY -m tools.shippability_runner architecture/shippability.md` → **98 rows, 98 PASS, 0 FAIL** (exit 0).
- **Note**: A clean PASS (not the recent PARTIAL pattern of slices 087/090). The forward-sync rows (CAD-1/MCFS-1/AVFS-1/TVFS-1) passed because slice-091 is MEPD-1 EXCLUDE (no version bump) AND runs in an isolated BRANCH-2 worktree decoupled from the parallel slice-092 — no shared-`~/.claude/` contention (R-28) surfaced. The worktree-isolation decision (vs slice-090's WORKTREE=skip) directly produced the clean validation.

## Multi-instance validation
- **Required?**: no (single-process library; no multi-user/device/account surface — though the SUBJECT of the fix is the multi-session parallel-slice conflict resolver, the validation itself is single-process).
- **Result**: not-applicable.

## Reality surprises
- **Count-pin decode count did NOT drop** (design predicted 9→8): the new breadcrumb helper's own `git rev-parse HEAD` decode site offsets the one `_git_show_stage` relinquished. Caught at the mid-slice smoke gate, reconciled across all vault surfaces. Not a defect — a bookkeeping correction.
- **slice-092 in flight in the main tree** (R-31 stranded-audit fix, non-overlapping): handled by worktree isolation; shippability #99 reserved; shared-file reconciliation deferred to `/commit-slice --merge` (PCR).
