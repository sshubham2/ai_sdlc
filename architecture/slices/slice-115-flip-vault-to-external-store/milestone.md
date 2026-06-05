---
slice: slice-115-flip-vault-to-external-store
stage: design
updated: 2026-06-05
next-action: run /critique
risk-tier: high
critic-required: true
---

# Milestone: slice-115 flip-vault-to-external-store

**Stage**: design
**Next action**: run `/critique`
**Updated**: 2026-06-05
**Risk tier**: high — Critic required: yes (capstone flip; touches skills/tools/agents methodology surfaces → mandatory regardless of tier; full 3-Critic stack)

## Progress

- [x] /slice — 2026-06-05
- [x] /design-slice — 2026-06-05
- [ ] /critique
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Design complete. **Option A (whole vault external) + plain directory** locked with the user (ADR-107).
- R-32.a/.b dissolved by Option A (single resolution domain; archival is an in-store move).
- New helper `tools/_vault_flip.py` (flip + scripted rollback — tested-reversibility).
- `/commit-slice` PCR vault-conflict RETIRE = `vault_is_external` guard (no-op); PSQ-3 rebase + HARD code-file resolution stay.
- Carve-out prose classes 4–6 → `<vault>/`; class 7 (diagnose-out) stays concrete.
- Self-referential bootstrap (slice-115 lives through its own flip) is the highest-risk part — design.md §The flip sequence.

## On resume

- **Last completed action**: /design-slice (design.md + ADR-107 written in the worktree)
- **Current work**: none
- **Next immediate step**: run `/critique` (mandatory — high tier + methodology surfaces; full 3-Critic stack)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-107](../../decisions/ADR-107-flip-vault-to-external-store.md)
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
