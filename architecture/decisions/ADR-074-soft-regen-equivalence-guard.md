---
id: ADR-074
title: Add a SOFT auto-regen equivalence guard to PCR-1 — regenerated content must be provably equivalent to both input branches, else fail-closed STOP
date: 2026-05-29
slice: slice-082-harden-pcr-1-soft-regen-corner-case
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-074: SOFT auto-regen equivalence guard (R-21 fix-class (b))

## Context

PCR-1 (ADR-069) gave the parallel-conflict resolver a SOFT class that auto-regenerates `architecture/slice-queue.md` (via claim-overlay) and `architecture/shippability.md` (via row-union) on a parallel-slice rebase conflict, then stages + `git rebase --continue`s. The SOFT path uses stage-then-commit atomicity: helpers return `(Path, content)` pairs without writing, and only if ALL helpers succeed are the writes committed; any `_SoftResolutionError` / `_VaultClaimDispatch` aborts with no writes.

R-21 (open, score 4 — the highest-scored open risk) anticipated a corner case where the SOFT auto-regen produces content **semantically different** from what a human-with-Critic-stack would have produced — a *silent wrong resolution*. Reading the shipped code confirms the risk is real: two divergence vectors emit structurally-valid-but-semantically-divergent output **without** raising any `_SoftResolutionError`, so they flow straight to the commit phase today:

1. `_overlay_claims_on_queue_text` (`tools/parallel_conflict_resolver.py:830-841`) silently drops a claim whose candidate block is missing its `- **Risk-retired:**` line — it only warns to stderr and proceeds.
2. `_merge_shippability` (`:1242`) keeps only the rebase-target stage's prelude (`prelude_3 if prelude_3 else prelude_2`), silently losing any non-numbered line unique to stage-2.

R-21 enumerated three candidate fix classes: (a) tighten `classify_conflict` to route the corner case to HARD; (b) extend the SOFT-set audit with a structural equivalence verification that aborts STOP when equivalence is unclear; (c) lower the SOFT confidence threshold globally. This ADR selects **(b)**.

## Options considered

1. **Fix-class (b): structural equivalence guard, fail-closed STOP** — add a post-regen / pre-commit gate that re-parses the pending content and proves it equivalent to both input branches along deterministic invariants; STOP if unprovable.
   - Pros: minimal blast-radius (one private predicate + one call-site in `resolve_soft_conflict`, routed through the existing no-writes-occurred `except` ladder); preserves the proven SOFT happy-path byte-for-byte when equivalence holds; converts the two known silent-divergence vectors into loud STOPs without widening the SOFT/HARD class boundary; squarely matches R-21's named fix-class.
   - Cons: the equivalence class is a hand-specified invariant set, not a total content-equality proof — a divergence outside the three invariants could still slip (mitigated by fail-closed re-parse + the residual being a much narrower class than today's).
2. **Fix-class (a): tighten `classify_conflict`** — narrow the SOFT predicate so the corner-case shapes classify as HARD/MIXED and route to PCR-2b's Critic stack.
   - Pros: no new guard code; reuses the HARD escalation path.
   - Cons: PCR-2b (HARD-class resolution) is not built yet, so "route to HARD" today means "STOP with no diagnostic about *why* the content would diverge"; and `classify_conflict` keys on file-set membership, not content shape — it structurally cannot detect a malformed-block-claim-drop, which is a property of the *content*, not the U-file set. Wrong layer.
3. **Fix-class (c): lower the SOFT confidence threshold globally** — accept more STOPs across the board.
   - Pros: simplest.
   - Cons: blunt; defeats the SOFT happy-path for the common, correct case (every stale-candidate drop would STOP); trades a rare silent-divergence for frequent false-STOPs. Over-correction.

## Decision

Adopt option 1 (R-21 fix-class (b)). Add `_verify_soft_equivalence` to `tools/parallel_conflict_resolver.py`, invoked in `resolve_soft_conflict` after the `pending_writes` collection loop and **before** the write/stage/`git rebase --continue` commit phase. It proves the pending regenerated content is in a deterministic equivalence class against the stage-2 / stage-3 inputs along three invariants:

1. **Queue claim-preservation** — every candidate in `merged_claims` that is also a `### <name>` heading in the baseline queue text appears in the re-parsed output with its merged claim. (Orphan claims — candidate absent from baseline headings — remain a documented expected drop per ADR-069 and are NOT a divergence.)
2. **Shippability row-completeness** — output numbered-row slice-number set equals `set(numbered_2) | set(numbered_3)`.
3. **Shippability prelude-preservation** — every non-blank prelude line in the discarded stage also appears in the output.

If any invariant is unprovable (or the guard's own re-parse raises) → `ResolutionResult(action="STOP", conflict_class=UNKNOWN, regenerated_files=(), reason="equivalence-guard: ...")` with **no writes** (atomicity preserved), and a best-effort audit-log entry recording the divergence. When all invariants hold, the guard is transparent — the happy-path commit phase runs unchanged.

## Consequences

- The two known silent-divergence vectors become loud, audited STOPs; the residual divergence class shrinks from "any structurally-valid regen" to "a divergence outside the three invariants AND not caught by fail-closed re-parse."
- `resolve_soft_conflict`'s public contract (signature, `ResolutionResult` return type, STOP-or-APPLIED outcomes) is unchanged — this is a new STOP *trigger*, not a new contract.
- The SOFT happy-path is byte-unchanged when equivalence holds (regression-pinned by the existing PCR-1 APED-1 battery).
- A new audit-log section variant `## Soft-conflict resolution (equivalence-guard STOP) - <ts>` is appended on guard-STOP.
- Future tightening (more invariants) or PCR-2b integration (route guard-STOP into the HARD Critic stack instead of a bare STOP) can layer on without superseding this ADR.
- Closes R-21; the guard's test becomes a shippability-pinned regression so the corner-class cannot silently return.

## Reversibility

**cheap.** The guard is a single private predicate plus one call-site, adding only STOP outcomes to an existing STOP/APPLIED contract — no persisted schema, no public API, no data migration. Loosening it (removing an invariant) or removing it entirely is a localized one-function edit. It does not lock any downstream consumer. Refines ADR-069 in-place on the SOFT path; supersedes nothing.
