---
slice: slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen
stage: slice
updated: 2026-05-28
next-action: run /design-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-076 add-pcr-1-conflict-diagnostic-and-soft-regen

**Stage**: slice
**Next action**: run `/design-slice`
**Updated**: 2026-05-28
**Risk tier**: medium — Critic required: **yes** (touches in-house methodology surfaces `skills/commit-slice/SKILL.md` + mints new rule PCR-1 + new ADR-069; mandatory-Critic trigger fires)

## Progress

- [x] /slice — 2026-05-28
- [ ] /design-slice
- [ ] /critique
- [ ] /critique-review
- [ ] /build-slice
- [ ] /code-review (CRSI-1 v1 walking-skeleton; advisory-only post-build)
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Slice defined. Mission brief written. Ready for design.

Closes the 5-session parallel-slice deadlock-on-soft-conflict gap surfaced 2026-05-28 by minting PCR-1 (parallel-conflict-resolution v1) — first rule on the parallel-conflict-resolution axis, sibling to PSQ-3 but distinct layer (PSQ-3 = detect; PCR-1 = resolve). Ships:

1. PCR-1 rule + 3-class taxonomy (SOFT / VAULT_CLAIM / HARD) + ADR-069
2. Enhanced full-detail diagnostic at /commit-slice Step 5b sub-step 2.5 conflict-STOP
3. Soft-conflict auto-regen path (slice-queue.md, _index.md, shippability.md, methodology-changelog.md)
4. New helper `tools/parallel_conflict_resolver.py` with library API + CLI
5. PMI-1 5-part atomic bump 0.72.0 → 0.73.0

Defers VAULT_CLAIM + HARD resolution (including Critic stack on resolution) to **PCR-2 / slice-077**.

## Re-scoping history

This slice was scaffolded 3× in succession during the 2026-05-28 conversation:
- Initial scaffold (commit `2c91238`): `slice-076-bundle-074-code-critic-cleanup` — close P1.1 + P3.10 + slice-074 m1-m5 footguns
- Re-scoped to `slice-076-add-slice-pick-skill` (uncommitted) — auto-pick ergonomics
- Final scope (this version): `slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen` — conflict-resolution v1 (more critical than pick ergonomics; pick ergonomics defers to slice-078)

The bundle-074-code-critic-cleanup work is re-queued at this slice's scaffold; ships at slice-079+ unless empirical refutation surfaces in the interim.

## On resume

- **Last completed action**: /slice (mission brief + milestone created; slice-queue.md regenerated for slice-076 + new follow-on candidates added per re-scoped roadmap)
- **Current work**: none
- **Next immediate step**: run `/design-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending (CRSI-1 v1 advisory)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
