---
slice: slice-093-add-external-vault-support
stage: critique
updated: 2026-05-31
next-action: run /build-slice
risk-tier: high
critic-required: true
---

# Milestone: slice-093 add-external-vault-support

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-31
**Risk tier**: high — Critic required: yes (In-house methodology surfaces: `tools/*.py`, `INSTALL.md`, new ADR; + novel cross-cutting change to the vault-root seam)

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-05-31
- [x] /critique — 2026-05-31 — CLEAN (first pass NEEDS-FIXES → all fixed at TRI-1; dual-review EXTEND)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Critique CLEAN (post-TRI-1). Dual-Critic stack: first-Critic 2B/4M/3m all VALID (zero false positives) → meta-Critic EXTEND (+B-add-1 caught my own B1-fix residual at `ADR-085:57`; +m-add-1 pre-existing comment drift). All 11 findings ratified by user: 10 ACCEPTED-FIXED + m-add-1 DEFERRED. rev-2 design/mission-brief/ADR-085 incorporate every fix (added `safe_append_text`, MEPD-1→EXCLUDE, count-pin 12→15, sidecar-lock terminology, `tests/methodology/`). Ready for `/build-slice`.

## On resume

- **Last completed action**: /critique + /critique-review — CLEAN (dual-review EXTEND); all 11 findings fixed in rev-2 + ratified at TRI-1
- **Current work**: none
- **Next immediate step**: run `/build-slice` (in THIS worktree). **R-33 sync**: slice/093 branched off `19d7d6a` but master is now at `e738c09` — rebase/merge master into slice/093 before the pre-finish suite; check for blast-radius conflicts on `tools/_vault_paths.py` / `INSTALL.md` / `tests/methodology/test_vault_root_constant.py`. slice-092 is reflect-complete pending `--merge` (its `stranded_slice_audit.py` edit is EXCLUDED from 093's migration → no code overlap).
- **Worktree**: ALREADY CREATED at `/slice` (user-directed early creation — dogfooding the worktree-at-`/slice` change this slice proposes) at `C:\Users\sshub\ai_sdlc-wt\slice-093-add-external-vault-support`, branch `slice/093-add-external-vault-support`, off master `19d7d6a`. ALL subsequent skills (`/design-slice`, `/critique`, `/build-slice`, `/validate`, `/reflect`) run IN this worktree; master stays clean. Do NOT `WORKTREE=skip`. slice-092 still in flight in its own worktree — re-run the stranded-slice consult before `/commit-slice --merge`.
- **Scope guard**: DEFAULT MUST STAY `architecture/`. No SKILL-prose rewrite, no physical move — those are slice-094.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — CLEAN (post-TRI-1)
- [critique-review.md](critique-review.md) — EXTEND (DR-1 dual review)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## Spike provenance

- [spike-external-shared-vault.md](../../spikes/spike-external-shared-vault.md) — CONDITIONAL/GO; constraints C1 (keying), C2 (write-safety / R-32), C3 (placement), C4 (completeness / the scope driver), C5 (history fork)
- field-recon.md is REQUIRED READING for `/critique` (authoritative-contradiction gate)
