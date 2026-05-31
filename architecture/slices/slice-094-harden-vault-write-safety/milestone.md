---
slice: slice-094-harden-vault-write-safety
stage: design
updated: 2026-05-31
next-action: run /critique
risk-tier: medium
critic-required: true
---

# Milestone: slice-094 harden-vault-write-safety

**Stage**: design
**Next action**: run `/critique`
**Updated**: 2026-05-31
**Risk tier**: medium — Critic required: **yes** (mandatory trigger: in-house methodology surfaces `tools/**/*.py` + new audit; reinforced by vault data-integrity / concurrency sensitivity)

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-05-31
- [ ] /critique
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Design complete. Route 3 grounded raw vault-write call sites through `_vault_write` (`slice_queue_writer.py:107` + `slice_queue_claim.py:232` → `safe_write_text`; `parallel_conflict_resolver.py:303` → `safe_append_text`); ship `tools/vault_write_safety_audit.py` (**VWS-1**, MEPD-1 INCLUDE) — a fail-closed closed-world AST audit (VAULT_ROOT-import tripwire + literal-vault-path secondary; `_vault_write.py` exempt; [[ADR-086]]); ship a mutation-proven concurrency test; discharge the slice-093 m3 `.lock`-accumulation residual via `.gitignore`. NARROWS R-32 (Python sub-class); skill-driven residual → slice-095. **1 new ADR (ADR-086).**

**Sequencing note**: the external-vault initiative is re-sequenced — the originally-planned "slice-094 = the flip" cannot land until R-32 retires. R-32 retirement needs both the Python-writer sub-class (THIS slice) and the skill-driven Write/Edit sub-class (slice-095 candidate). The flip follows both.

## On resume

- **Last completed action**: /design-slice (design.md + ADR-086 written)
- **Current work**: none
- **Next immediate step**: run `/critique` (mandatory — critic-required: true)
- **Build note**: use a real BRANCH-2 worktree (NOT WORKTREE=skip) per the slice-090/093 directive.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — written 2026-05-31
- [ADR-086](../../decisions/ADR-086-vault-write-safety-enforcement.md) — vault-write-safety enforcement (VWS-1)
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
