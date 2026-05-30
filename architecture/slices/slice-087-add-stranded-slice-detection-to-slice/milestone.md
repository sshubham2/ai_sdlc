---
slice: slice-087-add-stranded-slice-detection-to-slice
stage: critique
updated: 2026-05-30
next-action: PARKED — reframe design parallel-safe (4-class model) then re-run /critique; do NOT /build-slice as-is
risk-tier: medium
critic-required: true
---

# Milestone: slice-087 add-stranded-slice-detection-to-slice

**Stage**: critique (PARKED — design reframe required)
**Next action**: ⚠ **PARKED — do NOT `/build-slice` as-is.** Reframe `design.md` / `ADR-079` / `mission-brief.md` around the parallel-safe **4-class divergence model** (see the PARKED banner at the top of `design.md`), then re-run `/critique`. The current design flags ALL unmerged `slice/*` branches as "stranded" → breaks the parallel-slice execution model (cry-wolf on every in-flight parallel slice). USER caught it after `/critique-review`.
**Updated**: 2026-05-30
**Risk tier**: medium — Critic required: yes (methodology surface: `skills/slice/SKILL.md` + `skills/pulse/SKILL.md` + `tools/*.py`)

## Progress

- [x] /slice — 2026-05-30
- [x] /design-slice — 2026-05-30
- [x] /critique — 2026-05-30 — NEEDS-FIXES (first-Critic 1B/4M/2m all VALID; dual-review EXTEND +2 missed; user-ratified)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

⚠ **PARKED at NEEDS-FIXES — needs a parallel-safety design reframe before any build.** `tools/stranded_slice_audit.py` detects stranded prior slice work consulted by `/slice` + `/pulse` (motivated by slice-086's stranded state). `/critique` (NEEDS-FIXES, 1B/4M/2m all reconciled; reshaped to reuse `pulse_worktree_resolver`) + `/critique-review` (EXTEND, +2) are DONE. **Then the USER caught a design flaw both Critic layers missed**: flag-ALL-unmerged-`slice/*` cry-wolfs on every in-flight parallel slice under PSQ/BRANCH-2. **Resume by reframing to the 4-class divergence model** (STRANDED-COMPLETE / ORPHANED → halt; IN-PROGRESS / CLAIMED-BY-OTHER → informational) per the PARKED banner in `design.md`, then re-run `/critique`. This same miss hardened the Critic (Dim-7 probe, committed `64f6ea3`) — the reframed slice is Part B's first live test.

## On resume

- **Last completed action**: /critique + /critique-review (dual review, NEEDS-FIXES user-ratified) — then user-caught parallel-safety flaw (in-conversation, now persisted to design.md PARKED banner).
- **Current work**: none (PARKED).
- **Next immediate step**: REFRAME `design.md`/`ADR-079`/`mission-brief.md` to the 4-class divergence model (cross-reference vault `milestone.stage` + `archive/` + PSQ-2 `slice-queue.md` claims, not just git), then re-run `/critique`. **Do NOT `/build-slice` the current design.**
- **Sibling thread (separate slice, not yet defined)**: the **project-frame synthesizer** (Part A) — ephemeral per-slice frame (identity + trajectory + pending slice-queue + risks) fed to `/design-slice` + `/critique` + `/critique-review`. Captured in `architecture/critic-calibration-log.md` (2026-05-30 run).

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — ⚠ has PARKED reframe banner at top
- [critique.md](critique.md) — NEEDS-FIXES (user-ratified)
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — pending (BLOCKED on reframe)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
