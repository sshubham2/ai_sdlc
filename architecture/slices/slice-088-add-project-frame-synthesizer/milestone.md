---
slice: slice-088-add-project-frame-synthesizer
stage: slice
updated: 2026-05-30
next-action: run /design-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-088 add-project-frame-synthesizer

**Stage**: slice
**Next action**: run `/design-slice`
**Updated**: 2026-05-30
**Risk tier**: medium — Critic required: yes (methodology surfaces: `skills/design-slice/SKILL.md` + `skills/critique/SKILL.md` + `skills/critique-review/SKILL.md` + `agents/critique.md` + `tools/*.py`)

## Progress

- [x] /slice — 2026-05-30
- [ ] /design-slice
- [ ] /critique
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Slice defined. Part A of the 2026-05-30 `/critic-calibrate` proposal: an ephemeral, regenerated-per-slice **project-frame** (identity + trajectory + pending slice-queue + open risks + slice impact) fed to `/design-slice` (shift-left) + `/critique` + `/critique-review`, so designs/reviews are direction-aware. Closes the structural blind spot behind the slice-087 miss (review-in-isolation). Part B (the `agents/critique.md` Dim-7 probe) already shipped (`64f6ea3`); this slice hands the frame to it. **Runs in PARALLEL with slice-087** (zero blast-radius overlap; own BRANCH-2 worktree). Ready for design.

## On resume

- **Last completed action**: /slice (mission brief and milestone created)
- **Current work**: none
- **Next immediate step**: run `/design-slice` (in this slice's worktree)
- **Parallel sibling**: slice-087 (stranded detector, PARKED awaiting parallel-safety reframe) — independent; do not block on it.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
