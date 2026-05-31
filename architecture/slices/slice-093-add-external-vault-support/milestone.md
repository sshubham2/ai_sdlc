---
slice: slice-093-add-external-vault-support
stage: slice
updated: 2026-05-31
next-action: run /design-slice
risk-tier: high
critic-required: true
---

# Milestone: slice-093 add-external-vault-support

**Stage**: slice
**Next action**: run `/design-slice`
**Updated**: 2026-05-31
**Risk tier**: high — Critic required: yes (In-house methodology surfaces: `tools/*.py`, `INSTALL.md`, new ADR; + novel cross-cutting change to the vault-root seam)

## Progress

- [x] /slice — 2026-05-31
- [ ] /design-slice
- [ ] /critique
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Slice defined (capability cut, flip deferred). Mission brief written. Grounded in spike `external-shared-vault` (CONDITIONAL — GO with constraints C1–C5). **BRANCH-2 worktree created early at `/slice` (user-directed) and scaffold relocated off master — master is clean.** Ready for design, in the worktree.

## On resume

- **Last completed action**: /risk-spike (CONDITIONAL/GO) → /slice (mission brief + milestone created) → BRANCH-2 worktree created EARLY at /slice (user-directed) + scaffold relocated off master + scaffold-committed on `slice/093`
- **Current work**: none
- **Next immediate step**: run `/design-slice` — must resolve the C5 history fork framing (own-repo vs sync-back, though the DECISION lands at slice-094) and the resolution-precedence design (env → pointer/`--git-common-dir`-derived → `architecture/` default) + the C2 safe-write contract
- **Worktree**: ALREADY CREATED at `/slice` (user-directed early creation — dogfooding the worktree-at-`/slice` change this slice proposes) at `C:\Users\sshub\ai_sdlc-wt\slice-093-add-external-vault-support`, branch `slice/093-add-external-vault-support`, off master `19d7d6a`. ALL subsequent skills (`/design-slice`, `/critique`, `/build-slice`, `/validate`, `/reflect`) run IN this worktree; master stays clean. Do NOT `WORKTREE=skip`. slice-092 still in flight in its own worktree — re-run the stranded-slice consult before `/commit-slice --merge`.
- **Scope guard**: DEFAULT MUST STAY `architecture/`. No SKILL-prose rewrite, no physical move — those are slice-094.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## Spike provenance

- [spike-external-shared-vault.md](../../spikes/spike-external-shared-vault.md) — CONDITIONAL/GO; constraints C1 (keying), C2 (write-safety / R-32), C3 (placement), C4 (completeness / the scope driver), C5 (history fork)
- field-recon.md is REQUIRED READING for `/critique` (authoritative-contradiction gate)
