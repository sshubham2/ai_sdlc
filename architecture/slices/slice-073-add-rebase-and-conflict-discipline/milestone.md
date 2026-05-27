---
slice: slice-073-add-rebase-and-conflict-discipline
stage: triage
updated: 2026-05-28
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-073 add-rebase-and-conflict-discipline

**Stage**: triage (CLEAN)
**Next action**: run `/build-slice`
**Updated**: 2026-05-28
**Risk tier**: medium — Critic required: yes (in-house methodology surfaces: `skills/commit-slice/SKILL.md`)

## Progress

- [x] /slice — 2026-05-27
- [x] /design-slice — 2026-05-27
- [x] /critique — 2026-05-27 — 6B/6M/4m all ACCEPTED-FIXED in-band
- [x] /critique-review — 2026-05-28 — dual-review verdict EXTEND: 16 first-Critic CONFIRMED VALID + 6 meta-Critic missed (2 Major + 4 minor) all ACCEPTED-FIXED in-band
- [x] TRI-1 user-owned triage — 2026-05-28 — final verdict **CLEAN**; 22 dispositions ratified by user; triage_audit + critique_review_audit both PASS
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

TRI-1 ratified all 22 dispositions as ACCEPTED-FIXED. Final verdict CLEAN. Slice is ready for /build-slice. Design surface is settled: PSQ-3 ships as `--merge`-only rebase-onto-default at `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 + structural-pin tests at `tests/methodology/test_commit_slice_skill_rebase_flag.py` + ADR-068 + v0.72.0 methodology entry + 5-part PMI-1 bump + shippability row #73. Calibration note: aggregated-lessons "Builder fix-block introduces N+1 regressions in same class" pattern empirically extends to **N=7 cumulative** (slice-062/064/067/070/071/072/073) — `/critic-calibrate` proposal target post-slice-073 is "post-fix-block grep -n on the precedent name OR audit anchor across all 3 surfaces (mission-brief + design + ADR)".

## On resume

- **Last completed action**: TRI-1 user-owned triage (CLEAN)
- **Current work**: none — ready for /build-slice
- **Next immediate step**: run `/build-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-068](../../decisions/ADR-068-mint-psq-3-rebase-and-conflict-discipline.md)
- [critique.md](critique.md) — 6B/6M/4m all ACCEPTED-FIXED in-band; final verdict pending TRI-1
- [critique-review.md](critique-review.md) — dual-review verdict EXTEND; 6 missed findings all ACCEPTED-FIXED in-band; final verdict pending TRI-1
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
