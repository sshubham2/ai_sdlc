---
slice: slice-095-harden-skill-driven-vault-writes
stage: slice
updated: 2026-05-31
next-action: run /design-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-095 harden-skill-driven-vault-writes

**Stage**: slice
**Next action**: run `/design-slice`
**Updated**: 2026-05-31
**Risk tier**: medium — Critic required: **yes** (mandatory trigger: in-house methodology surfaces `skills/*/SKILL.md` + a new `tools/**/*.py` audit; reinforced by vault data-integrity / concurrency sensitivity + an ADR-worthy wrapper-vs-discipline design decision)

## Progress

- [x] /slice — 2026-05-31
- [ ] /design-slice
- [ ] /critique
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Slice defined (user-directed: "define new slice-095" in parallel with the already-defined slice-094). Closes the SECOND R-32 sub-class — skill-driven `Write` / `Edit` vault mutations (Claude editing vault files per SKILL.md prose, bypassing `_vault_write`). Establishes a concurrency-safe path + fail-closed audit + concurrency proof → with slice-094 (Python-writer sub-class) RETIRES R-32, unblocking the external-vault flip. Ready for design.

**Sequencing note**: R-32 retirement is gated on BOTH slice-094 (Python-writer) and slice-095 (skill-driven) merging. 095 can be designed/built in a parallel BRANCH-2 worktree but shares coordination files (`risk-register.md`, `shippability.md`, gate-roster SKILL.md) with 094 — additive, PCR-resolvable overlap, **NOT cleanly non-overlapping**. The wrapper-tool-vs-discipline+audit mechanism is an OPEN, ADR-worthy decision for `/design-slice`.

## On resume

- **Last completed action**: /slice (mission brief + milestone created)
- **Current work**: none
- **Next immediate step**: run `/design-slice`
- **Build note**: use a real BRANCH-2 worktree (NOT WORKTREE=skip) per the slice-090/093/094 directive; isolate from the parallel slice-094 worktree.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
