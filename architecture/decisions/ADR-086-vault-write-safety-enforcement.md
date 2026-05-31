---
id: ADR-086
title: Enforce vault-write-safety via a fail-closed closed-world AST audit (VWS-1), keyed on the VAULT_ROOT-import tripwire + literal-vault-path secondary
date: 2026-05-31
slice: slice-094-harden-vault-write-safety
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-086: Vault-write-safety enforcement (VWS-1)

## Context

slice-093 ([[ADR-085]]) shipped the R-32 write-safety *primitives* (`tools/_vault_write.py`: `safe_write_text`, `safe_append_text`) but left the actual `tools/*.py` vault writers writing files directly via raw `write_text`/`open(...,'a')`. The primitives are useless until every writer routes through them — and "every writer routes through them" must be a *machine-checked invariant*, not a convention, or R-32 silently re-opens the first time a new tool writes a vault file the old way. R-32 is the load-bearing blocker for the external-vault flip (a shared mutable vault turns loud git merge-conflicts into silent Windows lost-update / atomic-rename-EPERM corruption — the `.claude.json`/OneDrive class), so the enforcement must be relocation-proof and fail-closed.

The codebase forbids prose-only methodology rules (every load-bearing rule has a runnable audit). So vault-write-safety needs an audit. The design question is HOW the audit decides a write is "a vault write that bypassed the primitives."

## Options considered

1. **Runtime path-dataflow analysis** — statically resolve each write target `Path` expression and check whether it lands under the resolved `VAULT_ROOT`. *Pros*: precise. *Cons*: paths are composed at runtime from `VAULT_ROOT` + slice IDs + env; static resolution is undecidable in general → either false-negatives (misses computed paths) or a heavy, fragile abstract interpreter. Over-engineered for a ≤1-day slice.
2. **Honour-system convention** — a CLAUDE.md rule "always use `safe_write_text`", no audit. *Pros*: zero code. *Cons*: violates the project's "no prose-only methodology rule" discipline; the first forgetful new tool silently re-opens R-32. Rejected outright.
3. **Closed-world AST audit with a VAULT_ROOT-import tripwire + literal-vault-path secondary (CHOSEN)** — AST-scan `tools/*.py`; a module is a candidate vault writer iff it imports `VAULT_ROOT`/`_vault_paths`; any raw write op in a candidate that is not a call to a safe primitive is a VIOLATION. A secondary tripwire flags any raw write whose target literal names a known vault file or contains `architecture/`, catching a writer that hardcodes a vault path without importing the seam. `tools/_vault_write.py` (the primitive impl) is the sole module-name exemption. *Pros*: tractable, fail-closed, relocation-proof, mirrors the slice-041 `_REGISTERED_INSTALLED_READERS` closed-world precedent; the VAULT_ROOT-import discriminator empirically isolates EXACTLY the 3 real writers and excludes the 6 other write/import-only tools (verified by grep at design time). *Cons*: a writer that BOTH avoids the `VAULT_ROOT` import AND uses no literal vault filename (e.g. a fully runtime-computed path string) escapes both tripwires — accepted residual (an anti-pattern the seam already discourages; the cooperative model means this is data-integrity, not an adversarial bypass surface).

## Decision

Adopt Option 3. Ship `tools/vault_write_safety_audit.py` implementing the two-tripwire, fail-closed, closed-world AST model; route the 3 enumerated raw writers (`slice_queue_writer`, `slice_queue_claim`, `parallel_conflict_resolver`) through the `_vault_write` primitives; wire the audit into `/build-slice` Step 6 + `/validate-slice` + `architecture/shippability.md`. Mint RULE-ID **VWS-1** (MEPD-1 INCLUDE — the BCI-1/SRSC-1 gate-wired-audit shape).

## Consequences

- A new `tools/*.py` that writes a vault file via the `VAULT_ROOT` seam (the canonical way) and forgets the primitive is caught at `/build-slice` Step 6 — R-32's Python-writer sub-class cannot silently regress.
- The audit is a newly-minted AST parser → bound by BC-PROJ-13 (APED-1): the build executes it against the real `tools/` corpus + an adversarial battery (planted-raw-write caught, routed-write clean, non-vault-write clean, primitive-impl exempt) before declaring done.
- The exemption is a single module name (`_vault_write.py`), not per-line `# noqa`-style suppressions — keeping the safe channel auditable and singular.
- R-32 is **narrowed, not retired**: the skill-driven Write/Edit sub-class (Claude editing vault files directly per SKILL.md prose, bypassing Python entirely) is untouched by a Python-AST audit. That residual is documented and queued (`harden-vault-skill-write-discipline`, slice-095 candidate); the external-vault flip stays gated until it closes too.
- New-tool count fan-out (N≥3 lesson): `plugin.yaml` (PMI-1), `tools/install_audit.py` + `INSTALL.md` counts (INST-1), the cp1252 parametrize list, and any per-tool inventory-pin test all enumerate the new audit.

## Reversibility

**Cheap.** VWS-1 is an additive audit + three transparent call-site swaps. Removing it = delete the audit, unwire two SKILL.md gate lines, drop the shippability row; the routed writers keep working unchanged (the primitives are a strict superset of the raw write behaviour when there is no contention). No contract consumers, no data migration, no persisted state depends on it.
