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
- 2026-06-05 07:10 BUILD: A3 — promoted the ADR-104 op-gate to a /build-slice Step-6 gate (NO new RULE-ID — references ADR-104, promoted by ADR-107); `--op-gate --strict` exit 0 (floors 6/0/34/0). /validate-slice already enforces via Step 5.5 shippability (row 117). DEVIATION-note: slice-111 row-117 said "NOT a Step-6 gate" — slice-115 promotes it (the flip drains DEFERRED, leaving the OP_UNROUTED protection worth first-class gating); both phases now gate it. ADR-106 left UNEDITED (immutable historical ADR — its 6/11/23 is accurate at slice-113). Shippability row 121 + the 117/119 count-note updates BATCHED into Phase C (with the VERSION cascade). build-slice SKILL.md edit → OSDG-1 forward-sync pending (Phase C). Phase A3 DONE.
- 2026-06-05 07:30 BUILD: A4 reconnaissance — APED-1 inventory split confirmed: 65 convert (operational-reference + architecture/) vs 62 keep (37 git-pathspec all in code-review/SKILL.md + 25 diagnose-out). Prototyped + reverted a conversion script to keep a clean A3 checkpoint before the careful re-pin.
- 2026-06-05 08:15 BUILD: A4 — converted 62 operational `architecture/` refs → `<vault>/` across 12 loop skills + 3 agents (line+value-targeted). KEY FINDING: the class-4 worktree-composed refs needed a BEHAVIORAL rewrite (ADR-107 partial-supersedes BRANCH-3) — slice/SKILL.md scaffold paths `<wt_path>/architecture/slices/…` → `<vault>/slices/…` (post-flip the scaffold + queue resolve to the EXTERNAL store, not the worktree). slice/SKILL.md M5: removed the commit-on-master mechanic (`git add architecture/slice-queue.md` + commit) at 5 sites — the queue WRITE (CAS, slice-109) stays, no default-branch commit post-flip. m1: the slice:264 ellipsis rewritten to explicit `<vault>/slices/slice-NNN-<name>/` (classifies via active-folder branch) + dead allowlist entry removed. INSTALL/README correctly NOT converted (out of ADR-105 <vault>/ scope). code-review/SKILL.md operational refs converted but file stays un-ratcheted (slice-113 git-pathspec collision precedent); its 37 git-pathspec stay concrete (git needs concrete paths).
- 2026-06-05 08:18 BUILD: A4 re-pin — inventory EXPECTED_TOTAL 131→69, _CLASS_COUNT_FLOOR[rewrite-at-flip] 127→65, _BASELINE_SHA256→b02f4507; op-gate _OP_CLASS_FLOOR[OUT_OF_SCOPE] 34→33 (M5 removed 1 git-add op); _CONVERTED_FILES += critique-review skill + agent. inventory --strict + op-gate --strict BOTH exit 0; 51 inventory/op-gate/seam tests PASS. Skill/agent drift tests (OSDG-1/CAD-1) expected-red until the forward-sync (batched pre-smoke). Phase A4 DONE.

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
