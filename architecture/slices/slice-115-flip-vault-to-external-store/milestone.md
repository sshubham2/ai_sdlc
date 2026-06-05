---
slice: slice-115-flip-vault-to-external-store
stage: critique
updated: 2026-06-05
next-action: run /build-slice
risk-tier: high
critic-required: true
---

# Milestone: slice-115 flip-vault-to-external-store

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-06-05
**Risk tier**: high — Critic required: yes (capstone flip; full 3-Critic stack ran)

## Progress

- [x] /slice — 2026-06-05
- [x] /design-slice — 2026-06-05
- [x] /critique — 2026-06-05 — NEEDS-FIXES (first Critic BLOCKED; 3B/5M/2m)
- [x] /critique-review — 2026-06-05 — EXTEND (meta-Critic: 3 missed + 1 severity-adj; 0 suspicious)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic complete; TRI-1 ratified → **NEEDS-FIXES**. Design.md / ADR-107 / mission-brief carry all ACCEPTED-FIXED edits (B1–B3, M1–M5, m1–m2, M-add-1/2, m-add-3, M3-adj). ACCEPTED-PENDING items implemented during `/build-slice`:
- B1: `_vault_flip` migrate = rebase-then-full-branch-tree (carries ADR-107 + risk-register edit).
- B2 + M-add-1: op-gate reclassify active-folder → OUT_OF_SCOPE (sink-keyed), re-pin BOTH floors (DEFERRED 11→0, OUT_OF_SCOPE 23→~34), wire `--op-gate --strict` into build/validate + shippability, non-vacuity proofs.
- B3 + M-add-2: full-manifest LF-normalized verify; LF-normalize text on migrate; re-home ADR-098 byte-identity precondition.
- M3 + M3-adj: pre-flip quiesce guard via `stranded_slice_audit` (catches BRANCHLESS_IN_FLIGHT data-loss).
- M5: 5-site Step-6.5 retire + `git add` removal. m1: render slice:264 cleanly.

## On resume

- **Last completed action**: /critique + /critique-review (both committed; TRI-1 ratified NEEDS-FIXES)
- **Current work**: awaiting explicit go-ahead to launch /build-slice (LARGE capstone — plan-mode + the self-referential flip)
- **Next immediate step**: run `/build-slice` (enters plan mode; presents a build plan for approval)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-107](../../decisions/ADR-107-flip-vault-to-external-store.md)
- [critique.md](critique.md) — NEEDS-FIXES (triage ratified)
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
