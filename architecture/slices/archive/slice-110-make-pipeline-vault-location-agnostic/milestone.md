---
slice: slice-110-make-pipeline-vault-location-agnostic
stage: complete
updated: 2026-06-04
next-action: none (slice complete — run /commit-slice to integrate)
risk-tier: medium
critic-required: true
---

# Milestone: slice-110 make-pipeline-vault-location-agnostic

**Stage**: build (plan approved; execution pending fresh session)
**Next action**: resume `/build-slice` — execute the APPROVED Phase-1 plan in [build-log.md](build-log.md)
**Updated**: 2026-06-04
**Risk tier**: medium — Critic required: yes (mandatory trigger: in-house methodology surfaces `skills/*` + `tools/*` + a gating audit; reversible/green-throughout so not high)

## Re-scope provenance

This slice was **re-scoped in place from `flip-vault-to-external-store`** at TRI-1 (2026-06-04) after the flip design was BLOCKED by the dual-Critic stack (it would red the suite + break the in-loop skills). The reversible prep work below makes the pipeline vault-location-agnostic so the flip becomes a suite-neutral no-op; the flip + R-32 retirement are a follow-on slice. Full rationale + the superseded flip design: [`superseded-flip-design/`](superseded-flip-design/).

## Progress

- [x] /slice — 2026-06-04 (re-scoped from flip)
- [x] /design-slice — 2026-06-04
- [x] /critique — 2026-06-04 — **NEEDS-FIXES** (3 blockers, 3 majors, 3 minors; freeze-cascade mechanism EXECUTED + confirmed sound; most ACCEPTED-FIXED in design, B1+B3 build obligations)
- [x] /critique-review — 2026-06-04 — **EXTEND** (B1 corrected: empty-vault 99 → SEEDED ~74; B2 severity→Major; +3 missed Majors: reuse prose-inventory, gate-visible DEFERRED_TO_FLIP, shippability propagation — all ACCEPTED-FIXED)
- [x] TRI-1 user triage — 2026-06-04 — **NEEDS-FIXES** ratified (9 findings; triage_audit clean)
- [x] /build-slice — **Phase 1 SHIPPED 2026-06-04** (85 location breakers repointed; suite byte-identical default≡flip-sim; AC2/3/4 deferred to Phase-2 follow-on; all Step-6 audits green)
- [x] /code-review — 2026-06-04 — **0 blockers, 0 majors, 3 minors** (all addressed in-slice; code-Critic dual-world execution confirmed green + derived-probe load-bearing)
- [x] /validate-slice — 2026-06-04 — **PASS** (AC1 1575≡1575 byte-identical both modes; AC5 no production code; VAL-1 clean; shippability 114/114; AC2/3/4 deferred)
- [x] /reflect — 2026-06-04 (lessons captured; shippability row #116; Phase-2 follow-on previewed; auto-archiving)

## Current focus

**Phase 1 DONE — AC1 binding proof achieved.** Full suite: DEFAULT = 1 failed / 1574 passed; FLIP-SIM (SEEDED `AI_SDLC_VAULT_ROOT`) = byte-identical (1 failed / 1574 passed). The suite is fully location-agnostic (flip-sim ≡ default); zero regressions. 85/85 location breakers cleared via `tests/_vault_isolation.py` (`pin_vault_root` setattr-CM + `default_vault_root` + `subprocess_env` + `autouse_pin`) + `tests/conftest.py` shim + per-file autouse fixtures. **ADR-101 mechanism deviation**: reload → setattr (identity-safe), documented in ADR-101 + design.md.

**SOLE remaining red (BOTH modes) = PRE-EXISTING, not a slice-110 breaker**: `test_psq_1_blast_radius_dict_leak::test_committed_slice_queue_md_...` fails because the worktree's `architecture/slice-queue.md` (committed 51c55e8) is stale vs master's regenerated (path-shaped) queue.

**SLICE COMPLETE (Phase-1).** Shipped: location-agnostic test suite (AC1+AC5); suite byte-identical default ≡ flip-sim (1575≡1575). /code-review 0/0/3 (addressed). /validate-slice PASS. /reflect done — lessons captured (reload→setattr; worktree ledger staleness), shippability row #116, ADR-101 setattr convention established. Auto-archiving. **Next: `/commit-slice` (user-invoked) to integrate.** Phase-2 follow-on = `route-in-loop-skill-vault-ops-via-seam` (AC2 skill-op routing + AC3 `vault_flip_prose_inventory` op-gate / [[ADR-102]] impl + AC4 graphify).

## On resume (FRESH SESSION — start here)

- **Last completed action**: `/code-review` — code-Critic (agent a6a5feb3) returned 0 blockers / 0 majors / 3 minors; all 3 minors addressed in-slice (m1 doc, m2 DRY via subprocess_env, m3 _vp de-dup guard); re-verified green both worlds. Before that: `/build-slice` Phase 1 SHIPPED + all Step-6 audits green + full suite byte-identical default ≡ flip-sim.
- **Current work**: none — code-review complete. Worktree changes UNCOMMITTED (committed by `/commit-slice` later).
- **Next immediate step**: run **`/validate-slice`** (PCA-1 successor — real-environment AC validation + shippability regression). Then `/reflect` → HARD-STOP before `/commit-slice --merge`. (At `/reflect`, define the **Phase-2 follow-on slice** = route-in-loop-skill-vault-ops-via-seam, implementing AC2/AC3/AC4 + [[ADR-102]].)
- **Build-discovered deviation**: ADR-101 mechanism `importlib.reload` → `setattr`-pin (identity-safe). Documented in ADR-101 (build-time refinement §) + design.md. Watch for this in /code-review.
- **Where everything lives**: worktree `ai_sdlc-wt/slice-110-make-pipeline-vault-location-agnostic` on branch `slice/110-make-pipeline-vault-location-agnostic`. Helper: `tests/_vault_isolation.py` + `tests/conftest.py`. Build trail: `build-log.md`. Dual-review + superseded flip design: `superseded-flip-design/`. ADRs 101 (test isolation, IMPLEMENTED) + 102 (prose op-gate, DEFERRED).

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-101](../../decisions/ADR-101-test-vault-root-isolation-convention.md), [ADR-102](../../decisions/ADR-102-readiness-audit-scans-skill-prose.md)
- [critique.md](critique.md) + [critique-review.md](critique-review.md) — done (dual review, ratified)
- [build-log.md](build-log.md) — done (Phase-1 SHIPPED; gate green; BC-1 attestations + drift-check inside)
- [code-review.md](code-review.md) — done (0 blockers / 0 majors / 3 minors, all addressed in-slice)
- [validation.md](validation.md) — done (PASS; AC1 binding 1575≡1575; shippability 114/114)
- [reflection.md](reflection.md) — done (lessons + Critic calibration + Phase-2 follow-on)
- [superseded-flip-design/](superseded-flip-design/) — the BLOCKED flip design + dual-Critic review (re-scope rationale)
