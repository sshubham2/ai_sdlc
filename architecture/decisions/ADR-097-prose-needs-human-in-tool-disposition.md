---
id: ADR-097
title: needs-human prose literals are resolved by an in-tool disposition table keyed on normalized line-context, not by editing the prose
date: 2026-06-03
slice: slice-107-inventory-vault-flip-prose-surface
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-097: In-tool disposition table for prose needs-human resolution

## Context

`vault_flip_readiness_audit.py` (the production/tests surfaces, [[ADR-091]]/[[ADR-092]]) drives its fail-closed `needs-human` bucket to empty by a human adding an **inline source marker** (e.g. a `Class-B git identity (ADR-089)` comment on the literal's line); the ordered ruleset then routes the marked literal definitively. This works because the scanned surface is *editable code* the slice owns.

The prose surface is different: editing the prose to add classification markers is **explicitly out of scope** — the actual prose rewrite is the M4 flip, and slice-107 is inventory-only (touching prose here would (a) pre-empt M4, (b) pollute the very corpus being inventoried, (c) risk corrupting historical-anchor citations). So the readiness-audit's inline-marker resolution mechanism cannot be reused. Yet the fail-closed contract still requires a way to resolve a genuinely-ambiguous `needs-human` literal to a definite class, or the tool can never reach a clean (exit 0) baseline.

## Options considered

1. **Inline markers in the prose** (mirror `readiness_audit`) — rejected: violates the inventory-only / no-prose-edit scope; pollutes the corpus; risks mangling historical anchors.
2. **A sidecar disposition file** (e.g. `architecture/vault-flip-prose-dispositions.md`) — pro: human-readable; con: a second artifact to keep in sync with the tool, drift-prone, and itself a vault-located file that the flip would have to move; weaker test-pinning.
3. **An in-tool `_DISPOSITION` table** — a module-level tuple of `(relpath, normalized-line-context, assigned-class)` rows consulted as the ruleset's highest-precedence rule; the human resolves a `needs-human` literal by adding one row (in the tool, not the prose), pinned by the methodology test. Keyed on **normalized line-context** (whitespace-collapsed line text), NOT line number — stable across unrelated edits elsewhere in the file; if the disposed line itself changes, the row no longer matches and the literal correctly re-surfaces as `needs-human` (fail-closed re-review).

## Decision

Option 3. A `needs-human` prose literal is resolved by adding a row to the in-tool `_DISPOSITION` table in `tools/vault_flip_prose_inventory.py`, keyed on the 5-tuple `(relpath, normalized-line-context, fence-state, ordinal-among-identical-lines, column-offset)` → assigned class. The table is rule 1 (highest precedence) of the classification ruleset. Prose is never edited by this slice.

**Duplicate-line disambiguation (M2 + M-add-1 / slice-107 dual review):** whitespace-collapsed line text ALONE collides in TWO ways. **(M2) cross-line**: identical lines recur within one file (`architecture/slices/slice-NNN-` appears 10× in `skills/build-slice/SKILL.md`), and two same-text lines can need different classes (one inside a fenced example, one a live instruction) — so the key carries **fence-state** (inside / outside a ```` ``` ```` block) + the **ordinal** of the occurrence among identical-text lines in the file. **(M-add-1) intra-line**: a SINGLE line can carry multiple matches needing different classes — `skills/code-review/SKILL.md:103` has **5** `architecture/` matches (a `:(glob)architecture/*.md` pathspec → `rewrite-at-flip` alongside prose mentions), and 24 lines corpus-wide carry >1 match (32 extra occurrences). The cross-line ordinal cannot separate these (they share the same line), so the key adds **column-offset** (the match's start column). Two pins: `test_no_ambiguous_duplicate` (cross-line) AND `test_no_intra_line_ambiguous_multimatch` (intra-line — `code-review.md:103` is the canonical fixture) both assert the current corpus has no two occurrences sharing the full 5-tuple key yet requiring different classes (proving collision-freedom, not merely asserting it). NOTE: this also requires the scanner to enumerate ALL matches per line (`re.finditer`), not one `re.search` per line.

## Consequences

- The tool can reach a clean baseline (drive `needs-human` → empty) without touching prose — the inventory-only scope holds.
- The disposition table is a **first-class part of the pinned baseline**: it is curated by a human, frozen by `tests/methodology/test_vault_flip_prose_inventory.py`, and changes to it are visible in diffs + gated by `--strict`.
- The normalized-line-context key gives the right fail-closed behavior: editing a disposed prose line (which may change its flip-disposition) re-surfaces it for review rather than silently retaining a stale class.
- Identity-model note: the disposition keys on the per-occurrence 5-tuple `(relpath, normalized-line-context, fence-state, ordinal-among-identical-lines, column-offset)` while the `--strict` baseline keys on the coarser line-independent `(relpath, value, klass)` multiset (plus the m2 per-class total-count floor); the two compose (disposition assigns the per-occurrence class; the baseline aggregates) and are independently pinned.
- Residual: the ordinal component is stable only while the *set* of identical-text lines in a file does not reorder; a reordering edit re-surfaces the affected occurrences as `needs-human` (fail-closed re-review) rather than silently mis-assigning — the safe failure direction.
- At M4, the disposition table doubles as the authoritative rewrite/preserve checklist for the prose surface.

## Reversibility

**Cheap**. The `_DISPOSITION` table is a tool-internal constant; changing its key model, or migrating to a sidecar file later, is a contained edit to one module + its one test. Nothing external depends on its shape.
