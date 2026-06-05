---
slice: slice-115-flip-vault-to-external-store
stage: slice
updated: 2026-06-05
next-action: run /design-slice
risk-tier: high
critic-required: true
---

# Milestone: slice-115 flip-vault-to-external-store

**Stage**: slice
**Next action**: run `/design-slice`
**Updated**: 2026-06-05
**Risk tier**: high — Critic required: yes (capstone flip; touches skills/tools/agents methodology surfaces → mandatory regardless of tier; full 3-Critic stack)

## Progress

- [x] /slice — 2026-06-05
- [ ] /design-slice
- [ ] /critique
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Slice defined — the capstone physical move that retires R-32. Mission brief written with 5 ACs (config flip, move+untrack, R-32.a drain, R-32.b drain, prose+commit-slice+retire) and 3 exploratory charters. The two crux design questions (R-32.a active-folder location, R-32.b archive-`mv` source routing) are deliberately left for `/design-slice`. Ready for design.

## Current focus — design questions to resolve in /design-slice

- **R-32.a**: active-slice folders worktree-local vs in the external store (settles `OP_DEFERRED_TO_FLIP` → ∅).
- **R-32.b**: route archive-`mv` source coherently across stores vs keep active folders external (coupled to R-32.a).
- **git-untrack**: `git rm -r --cached architecture/` + gitignore; confirm history retention vs clean-cut.
- **Store path**: base `~/.aisdlc` (user-confirmed at /slice); per-project subdir = bounded hash of canonicalized common-dir (ADR-085).
- New ADR (ADR-107+) records all of the above.

## On resume

- **Last completed action**: /slice (mission brief and milestone created in the slice-115 worktree)
- **Current work**: none
- **Next immediate step**: run `/design-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
