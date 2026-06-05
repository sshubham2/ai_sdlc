# Build log: Slice 115 flip-vault-to-external-store

**Date**: 2026-06-05
**Result**: NOT-SHIPPED (in progress)

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-06-05 06:30 BUILD: plan approved (Phase A→B→C); decision: VERSION bump + methodology-changelog entry (flip is a real state change, partial-supersedes ADR-090).
- 2026-06-05 06:31 BUILD: BC-PROJ-3/BC-GLOBAL-2 attest — this slice performs NO destructive `git checkout`/`restore`/`stash` revert of uncommitted work (the flip's `git rm -r --cached` keeps working-copy files; the migrate is copy-then-verify-then-delete, source untouched until full-manifest verify passes).
- 2026-06-05 06:32 BUILD: Phase A1 start — tools/_vault_flip.py (flip + rollback engine) + test_vault_flip.py.
- 2026-06-05 06:45 TEST: test_vault_flip.py 7 passed (round-trip; LF-normalize CRLF→LF; full-manifest verify non-vacuity B3; absent-base default M1; refuse-nonempty; bounded-16-hex hash). Phase A1 DONE.
- 2026-06-05 06:55 BUILD: A2 op-gate reclassify — _classify_op clause-2 active-folder → OP_OUT_OF_SCOPE (sink-keyed, above in-loop check, M-add-1); slice:264 allowlist re-keyed; APED-1 real-corpus run → 6 routed / 0 deferred / 34 out-of-scope / 0 unrouted; floors re-pinned DEFERRED 11→0 + OUT_OF_SCOPE 23→34 (both, M-add-1).
- 2026-06-05 06:56 BUILD: A2 readiness audit — added `_vault_flip` to _SEAM_MODULE_STEMS (flip-engine `architecture` literal is seam machinery, not a must-rewrite).
- 2026-06-05 06:58 TEST: op-gate + prose-inventory + readiness suites 71 passed (5 op-gate tests updated to OUT_OF_SCOPE w/ non-vacuity preserved; floor-shrink test now the M-add-1 anti-shrink proof). Phase A2 DONE.

## Summary (filled at slice end)

### Plan executed
(Phase A pre-flip code → mid-slice smoke gate → Phase B flip → Phase C finalize; per-task status filled as we go)

### Mid-slice smoke gate
**Result**: pending

### Pre-finish gate
(pending)

### Deferrals (if any)
(none yet)

### Design deviations (if any)
(none yet)

### Files changed
(filled at slice end)
