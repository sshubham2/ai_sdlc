---
id: ADR-103
title: Route the in-loop skill archive move through a vault_edit `move` subcommand (the vault_edit shell seam-CLI)
date: 2026-06-04
slice: slice-111-route-in-loop-skill-vault-ops-via-seam
reversibility: cheap
status: accepted
---

# ADR-103: `vault_edit move` — seam-routed directory move for the in-loop archive op

> **Refined at /critique (slice-111)**: the originally-drafted `vault_edit root` subcommand was DROPPED (B1 — its only consumer, `/design-slice`'s `graphify vault` "target", turned out to be prose, not an executable invocation; there is NO in-loop `graphify vault` builder, so `root` would have been an orphan subcommand). The dest-exists guard contract was corrected (M2 — it checks the final landing path, not the `--to` directory). This ADR now scopes a single subcommand: `move`.

## Context

slice-106 routed the production-code (`tools/*.py`) vault reads through the `VAULT_ROOT` seam ([[ADR-065]] / [[ADR-085]]); slice-110 made the test suite location-agnostic ([[ADR-101]]). The remaining un-routed surface is the **in-loop SKILL.md prose**: skills perform vault file-system ops via literal in-tree paths that hardcode the location and silently break (or silently write to the wrong place) once the vault relocates to the external store (the R-32 flip).

The vault-file *content* RMWs (`_index.md`, `archive/_index.md`, `risk-register.md`) were already routed at slice-095/097 through `tools/vault_edit.py` (`append`/`rewrite`/`read`, `--file` resolved under `VAULT_ROOT`). The `drift-log.md` append routes through the existing `vault_edit append`. What is NOT yet routable through a seam channel:

- The **archive `mv`** (`/reflect:320`, `/archive:51`) — a directory *move* (`slices/slice-NNN/` → `slices/archive/`), not a content edit. `vault_edit` has no move op, so the prose carries a bare in-tree `mv architecture/slices/...` that breaks at flip.

## Options considered

1. **Add a `move` subcommand to `vault_edit`** (the existing routed channel) — pro: one shell seam-CLI for vault ops; the op-gate's "routed" signal is uniformly the `vault_edit` token; `move` resolves BOTH endpoints under `VAULT_ROOT` (cross-store coherence) + reuses `vault_edit`'s existing `_resolve_in_vault` escape/outside-root guard + keeps the `/archive:56` dest-exists semantics. Con: grows `vault_edit`'s surface by one subcommand.
2. **A `--print-root` CLI on `tools/_vault_paths.py` + raw shell `mv $(root)/...`** — con: pollutes the dependency leaf; a raw shell `mv` loses the dest-exists guard; two routing idioms the op-gate must both recognize.
3. **Document the op "flip-aware" without routing** — con: a documented-but-unrouted op still breaks at flip; the silent-residual anti-pattern the op-gate ([[ADR-104]]) exists to prevent.

## Decision

Extend `tools/vault_edit.py` with **`vault_edit move --from <vault-rel> --to <vault-rel>`**:

- Resolves both `--from` and `--to` under `VAULT_ROOT` via the existing `_resolve_in_vault` guard (empty path / vault-root-itself / outside-root → exit 2, same as `--file`).
- **Dest-exists guard (M2)**: the archive idiom is `move --from slices/slice-NNN --to slices/archive/`, where `--to` (`slices/archive/`) is a directory that *always exists*. Matching `shutil.move` directory semantics (src is moved INSIDE an existing dst dir; the in-dir landing path must not pre-exist), the guard checks the **final landing path** `(<--to> / basename(<--from>))`, NOT the `--to` directory itself. Exit 2 iff `<--to>/<src-name>` already exists (preserves the `/archive:56` "stop if `slices/archive/<same-name>/` exists" semantic). A naive `if Path(--to).exists(): exit 2` would wrongly refuse EVERY archive — explicitly rejected.
- On success: `shutil.move` (handles same-store rename AND the cross-filesystem copy+remove fallback), exit 0.
- **No CAS/lock**: a directory move is a one-shot rename, not a content read-modify-write; concurrent archival of the *same* folder is implausible (a slice is archived once) and distinct destinations never collide. The dest-exists guard covers the rare manual-edit collision. (The slice-094/097 `_vault_write` CAS/lock machinery guards content RMW lost-updates — a different hazard class.)

`tools/_vault_paths.py` stays the untouched dependency leaf. Routed sites: `/reflect:320` + `/archive:51` archive `mv` → `vault_edit move`. The op-gate ([[ADR-104]]) treats a `vault_edit`/`VAULT_ROOT` token in an op's anchored region as the **routed** signal.

## Consequences

- The archive `mv` resolves both endpoints under one `VAULT_ROOT` — within-store on the in-tree default AND a wholly-external post-flip vault. **Cross-store coherence residual (R-32.b)**: IF the flip slice keeps per-slice ACTIVE folders worktree-local, `move --from slices/slice-NNN` resolves external and fails **loud** (source-not-found) — visible, never a silent mis-write; the flip slice MUST resolve it (recorded as an R-32 sub-entry, [[ADR-104]] / risk-register).
- Routing the `mv` removes its `architecture/...` literals from the slice-107 prose-inventory baseline (they become vault-relative `slices/...`) — the `_BASELINE_SHA256` / `_CLASS_COUNT_FLOOR` / `EXPECTED_TOTAL` pins are re-derived in the same slice (M1; see design.md Phase A).
- OSDG-1-guarded edited skill re-synced: `/reflect` (archive `mv`) — the ONLY guarded skill edited. The unguarded edited skills `/archive` + `/drift-check` **DO have installed copies** (m-add-5 — the earlier "no installed copy" rationale was false); they simply lack a `*_skill_drift.py` content-equality test, so their installed `~/.claude/skills/` copies are **hand-synced** this slice with a documented no-enforcement residual. (`/commit-slice` is NOT edited — its archived-read routing was deferred to the prose-rewrite slice per M-add-2; build-slice/validate-slice are NOT edited — the [[ADR-104]] op-gate is suite-test-enforced, not Step-6-wired, per m2.)
- No `VAULT_ROOT` resolution-logic change; reversible by `git revert`.

## Reversibility

**Cheap** — an additive subcommand on an existing tool + prose edits that resolve through it. No data migration, no behavior change on the in-tree default. A revert restores the literal-path prose.
