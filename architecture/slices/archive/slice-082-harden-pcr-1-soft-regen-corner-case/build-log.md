# Build log: Slice 082 harden-pcr-1-soft-regen-corner-case

**Date**: 2026-05-29
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-05-29 PREREQ: CRP-1 clean (critique-review.md present); on master + dirty tree → BRANCH-2 dirty-tree sequence
- 2026-05-29 BUILD: worktree created at ../ai_sdlc-wt/slice-082-... on slice/082-harden-pcr-1-soft-regen-corner-case; scaffolding committed (b79708a)
- 2026-05-29 TEST: wrote test_pcr_1_soft_regen_equivalence_guard.py (test-first)
- 2026-05-29 SMOKE: mid-slice gate — corner-case test RED pre-guard (resolver APPLIES + silently drops add-foo claim; want STOP) — R-21 reproduced
- 2026-05-29 FINDING: rebase stage inversion — `git show :2:`=master, `:3:`=branchA(baseline); `_merge_claim_dicts` keeps stage-2 entry when stage-3 claimed_at absent. Fixture branch-sides corrected (helper renamed to branchA=/master= kwargs)
- 2026-05-29 BUILD: implemented _verify_soft_equivalence + _append_equivalence_stop_audit; wired read-only call-site after empty-check (:302) before write loop
- 2026-05-29 TEST: new module 8/8 PASS; full PCR + related suite 159/159 (no regression)
- 2026-05-29 BUILD: shippability row 88 + AC-5 pin test added; mission-brief TF-1 rows → PASSING
- 2026-05-29 TEST: BC-1 strict (ack BC-PROJ-3/7/GLOBAL-2) exit 0; TF-1 strict 6/6 PASSING; mock-budget clean
- 2026-05-29 BUILD: /drift-check full mode — 0 blockers/0 majors/1 minor (line-citation offset); DCE-1 trigger written + audit clean
- 2026-05-29 TEST: full suite 1172 passed; all Step 6 audits green
- 2026-05-29 FINDING: /code-review code-Critic — 0B/1M/3m. M1: invariant #1 heading regex `^### (.+)$` not rstripped (trailing-space baseline heading bypasses the fail-closed claim check) — defeats R-21 / violates must-not-defer #1
- 2026-05-29 BUILD: fixed M1 (strip all 3 heading captures) + m1 (#2 round-trip-backstop docstring) + m2 (`_fail -> NoReturn`) + m3 (`baseline_is_stage3 = bool(text_3)`); added adversarial test_trailing_whitespace_heading_still_stops
- 2026-05-29 TEST: new module 9/9; TF-1 7/7 PASSING; full suite 1173 passed

## Summary

### Plan executed
- **Phase A — worktree setup**: DONE. Scaffolding committed to `slice/082-...`; worktree at `../ai_sdlc-wt/slice-082-...`.
- **Phase B — test-first RED**: DONE. `test_pcr_1_soft_regen_equivalence_guard.py` reproduced R-21 (corner-case APPLIED-not-STOP) — mid-slice smoke gate.
- **Phase C — guard**: DONE. `_verify_soft_equivalence` (read-only, 3 invariants, fail-closed STOP via reused `_SoftResolutionError`) + `_append_equivalence_stop_audit`; call-site pinned after the empty-check, before the write loop (M3).
- **Phase D — pending dispositions**: DONE. M2 loud cross-stage-claim-drop warn (no STOP); m2 grep confirmed no closed-set audit-heading assertion (positive `in` membership only) + unmutated-scope clarified in design; MEPD-1 → EXCLUDE (no new RULE-ID, no VERSION bump).
- **Phase E — pre-finish gate**: DONE. All gates green.

### Dispositions realized (from critique.md + critique-review.md)
- B1 (re-parse plan): guard re-derives merged_claims via `_git_show_stage`+`_extract_claim_diff`+`_merge_claim_dicts`, baseline headings via regex, `parse_queue_text` for pending claim presence. ✓
- M1 (symmetric invariant #3): implemented as `set(nonblank prelude_2)==set(nonblank prelude_3)` + output preservation; `test_equivalence_guard_stops_on_unprovable_equivalence` (prelude divergence) + `test_shippability_happy_path_guard_transparent` (no false-STOP). ✓
- M2 (orphan exemption bound): loud `cross-stage-claim-drop` stderr warn (NOT STOP); `test_cross_stage_claim_drop_warns_not_stops`. Truncated-baseline residual → PCR-2b, register at /reflect. ✓
- M3 (call-site/atomicity): pinned read-only call-site after empty-check before write loop; `test_stop_leaves_repo_state_unmutated` asserts U-file conflict markers + rebase-in-progress preserved. ✓
- m1 (reuse `_SoftResolutionError`): no new exception class. ✓
- m2 (audit variant + unmutated scope): `(equivalence-guard STOP)` variant added; no closed-set heading assertion to widen (verified); design Error-model clarifies audit append excluded from unmutated guarantee. ✓
- M-add-1 (claimed-subset domain): invariant #1 domain = `{n for n,d in merged_claims.items() if d.get("claimed_by")}`; `test_happy_path_equivalence_holds_guard_transparent` (mixed claimed+unclaimed → APPLIED). ✓

### Mid-slice smoke gate
**Result**: PASS (as a test-first RED) — `test_corner_case_soft_regen_diverges_from_baseline` returned APPLIED with the claim silently dropped pre-guard (R-21 reproduced); GREEN (STOP) post-guard.

### Pre-finish gate
- [x] All ACs pass with evidence — 8/8 tests in the new module; AC1-5 mapped
- [x] Must-not-defer addressed (fail-closed; no partial writes; audit trail; happy-path preserved; APED-1 battery)
- [x] /drift-check full mode — 0 blockers/0 majors/1 cosmetic minor; DCE-1 audit clean
- [x] Mid-slice smoke regression — full PCR suite 159/159, full suite 1172 passed
- [x] No new TODOs/FIXMEs/debug prints (the two `print(..., file=sys.stderr)` are intentional diagnostics matching existing PCR patterns)
- [x] BC-1 strict (ack BC-PROJ-3/BC-PROJ-7/BC-GLOBAL-2), WIRE-1, TF-1, BRANCH-2, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, DCE-1, mock-budget — all green

### BC-1 Critical acknowledgments
- BC-PROJ-3 + BC-GLOBAL-2 (no destructive git revert): slice performs no `git checkout`/`restore`/`stash` of uncommitted work; tests use isolated `tmp_path` repos; the guard never reverts via git. Addressed.
- BC-PROJ-7 (new `tools/*.py` self-application): **vacuously satisfied** — slice adds NO new tools module (modifies existing `parallel_conflict_resolver.py`); over-fired on keyword/glob. Acknowledged.

### Deferrals
- None for this slice. The genuinely-corrupt-baseline (truncated stage-3) residual of R-21 is a narrow named sub-residual deferred to PCR-2b's HARD-class path (per M2); to be registered in the risk-register at /reflect.

### Design deviations
- design.md said the guard-STOP "routes through the already-present except clause (L288-300) with zero except-ladder change." Reality: the pinned post-empty-check call-site is OUTSIDE the original loop-try, so a LOCAL `try/except _SoftResolutionError` at the call-site was required. This still reuses `_SoftResolutionError` (no new exception type — m1 intent preserved) and keeps the M3 pinned location. Logged here; the design's "What's new" + Error-model wording was updated in the same edit to say "caught by this local try/except."
- design.md absolute line citations are now approximate post-insertion (drift-log minor; non-behavioral; not churned per thin-vault).

### Files changed
- `tools/parallel_conflict_resolver.py` — added `_verify_soft_equivalence` + `_append_equivalence_stop_audit`; wired the guard call-site in `resolve_soft_conflict`.
- `tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py` — new APED-1 battery (8 tests).
- `architecture/shippability.md` — row 88 (equivalence-guard pin).
- `architecture/slices/slice-082-.../mission-brief.md` — TF-1 rows → PASSING; AC-5 row added.
- `architecture/slices/slice-082-.../design.md` — B1/M1/M2/M3/m1/m2/M-add-1 fixes (applied during /critique + this build).
- `architecture/drift-log.md` — slice-082 audit entry + DCE-1 trigger marker.
- `architecture/slices/slice-082-.../milestone.md` — stage transitions.
