---
id: ADR-096
title: The vault-flip prose surface gets a dedicated standalone vault_flip_prose_inventory.py (third surface), not a branch inside vault_flip_readiness_audit.py
date: 2026-06-03
slice: slice-107-inventory-vault-flip-prose-surface
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-096: Dedicated standalone tool for the vault-flip prose surface

## Context

The external-shared-vault flip (M4) relocates `architecture/` + `diagnose-out/`. Slice-100 ([[ADR-091]]) inventoried the **production-code** surface and slice-102 ([[ADR-092]]) added the **tests** surface — both in `tools/vault_flip_readiness_audit.py`, both leaning on Python's AST for context-aware classification. The remaining flip-sensitive surface is **prose**: ~318 `architecture/`+`diagnose-out/` literals across `skills/**/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `INSTALL.md`, `README.md`. Prose is Markdown — there is **no AST**; classification must be line-context-driven, a fundamentally different mechanism from the AST node-context analysis `readiness_audit` is built on.

Concurrently, the parallel sibling **slice-106** modifies `vault_flip_readiness_audit.py` (re-pinning its `_BASELINE`). The two slices are designed to run in parallel with disjoint blast radius.

## Options considered

1. **Add a third surface inside `vault_flip_readiness_audit.py`** (a `prose` branch alongside `production`/`tests`) — pro: one tool, one CLI; con: (a) forces an AST-built tool to grow an unrelated line-based Markdown scanner, bloating a tool whose every rule assumes `ast.Constant` nodes; (b) **collides head-on with slice-106**, which is re-pinning that exact file's baseline — destroying the disjoint-blast-radius that lets 106 and 107 run in parallel.
2. **A dedicated standalone `tools/vault_flip_prose_inventory.py`** that *mirrors* `readiness_audit`'s CLI/exit-code/baseline contract but implements a line-context classifier — pro: keeps the AST tool clean, preserves disjointness from slice-106, lets the prose ruleset evolve independently; con: two tools the M4 operator must run (mitigated: identical CLI surface, so "run both" is trivial).

## Decision

Option 2. The prose surface is inventoried by a new standalone `tools/vault_flip_prose_inventory.py` — the vault-flip **third surface** — with a CLI, exit-code contract (0/2/1), ordered-ruleset classification, line-number-independent multiset baseline, and `--strict` drift gate all deliberately mirroring `readiness_audit` (so the flip operator drives all three surfaces identically), but with a Markdown line-context classifier rather than AST node-context analysis. `readiness_audit` is **not** modified by this slice.

## Consequences

- The M4 flip checklist is assembled from THREE tools: `readiness_audit` (production + tests) + `vault_flip_prose_inventory` (prose). Flip-execute must consume all three.
- Disjointness from slice-106 is preserved: 107 adds a new file, 106 edits `readiness_audit` — no shared-core conflict (only append-only `shippability.md`/`plugin.yaml`/`install_audit.py` coordination at merge).
- Because `readiness_audit` scans `tools/*.py`, it will scan the *new* tool; the new tool must keep its own `architecture`/`diagnose-out` match-constants in non-resolving contexts (bare-segment frozenset / regex), or it self-trips slice-106's re-pinned production baseline. Enforced by the mid-slice smoke gate (`readiness_audit --strict` exit 0) + a disjointness test.
- A future consolidation (folding the prose scanner back into one tool once the flip lands) remains open — hence cheap reversibility.

## Reversibility

**Cheap**. Both tools are internal CLI utilities with no external consumers and identical contracts; merging or re-splitting them later is a contained refactor (move functions, repoint one test + one shippability row + one manifest entry). No data model, no persisted artifact, no API consumer is bound to the two-tool shape.
