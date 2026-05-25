---
id: ADR-048
title: Reclassify the BFRD-1 STOP-route from an unconditional user hand-off to a conditional confirm-then-auto-invoke /repro edge
date: 2026-05-19
slice: slice-046-add-conditional-repro-auto-advance
reversibility: cheap
status: accepted
supersedes: ADR-018
---

# ADR-048: Reclassify BFRD-1's STOP-route to a conditional confirm-then-auto-invoke `/repro` edge

**Supersession scope** (partial, per slice-022 ADR-020 partial-supersession precedent — single `supersedes:` slot + body-level scope enumeration): this ADR supersedes **only** ADR-018's Option-1 item 3 ("STOP-and-route behavior" — the verbatim *"run `/repro <issue>` … then re-invoke `/slice`"* unconditional hand-off). ADR-018's detection sub-modes (a)/(b), the `shippability.md grep verification` mechanism, the verbal-claim-with-path fallback, the one-surface `/slice` Step 3c placement, the one-way `/slice → /repro` coupling, and the BFRD-1 rule-ID itself are **inherited unchanged**. ADR-018 stays `status: accepted` (append-only ADR discipline; this ADR carries the `supersedes: ADR-018` slot and the scope note).

## Context

BFRD-1 (slice-020, ADR-018, `methodology-changelog.md` v0.34.0) codified the bug-fix repro prelude at `/slice` Step 3c. Its terminal action when detection fires and no failing repro test exists is an **unconditional STOP**: `/slice` emits a verbatim instruction telling the user to *go run `/repro <issue>` themselves and then re-invoke `/slice`*.

Two things changed since slice-020:

1. **PCA-1** (slice-027, `methodology-changelog.md` v0.41.0) established the pipeline auto-advance philosophy: in-loop skills auto-invoke their successor on clean completion; mechanical user hand-offs are removed wherever a lighter checkpoint suffices. BFRD-1's STOP-route is now the single largest residual mechanical hand-off inside the per-slice loop — it dead-ends every bug-fix slice and forces a manual `/repro` round-trip plus a manual `/slice` re-invocation.
2. **User directive (2026-05-19)** (recorded in memory `repro-confirm-then-auto-invoke`): `/slice` should distill the bug description, present it for confirm/modify, then auto-invoke `/repro` itself — never punt the sub-skill back to the user.

The **sole legitimate reason** the gate was unconditional (ADR-018 Failure-mode-2: an auto-generated test could reproduce the *wrong* failure signature, falsely greening a bug as "fixed and tested") is fully mitigated by a lightweight **confirm-the-distilled-description checkpoint** — the user still authorizes the exact signature `/repro` will target; only the mechanical hand-off is removed.

## Options considered

1. **Status quo — unconditional STOP-and-route.** Pros: simplest; user always in the loop. Cons: the exact mechanical-hand-off PCA-1 exists to remove; contradicts the standing user directive; a manual `/repro` + manual `/slice` re-invocation per bug-fix slice. Rejected.
2. **Unconditional auto-invoke `/repro` (no confirm gate).** Pros: maximal automation. Cons: re-opens ADR-018 Failure-mode-2 — `/slice`'s distilled description could target the wrong signature and `/repro` would establish a test for the wrong bug, silently. Rejected: removes the gate's only load-bearing protection.
3. **Conditional confirm-then-auto-invoke edge (CHOSEN).** `/slice` distills a one-line bug description, presents it via `AskUserQuestion` structured options (Confirm / Modify / Not-a-bug-cancel); on Confirm/Modify it auto-invokes `/repro` with the confirmed string and continues; on cancel it fails closed (no auto-`/repro`, no silent proceed). Pros: removes the mechanical hand-off (PCA-1-aligned, satisfies the user directive) while preserving Failure-mode-2 protection via the confirm checkpoint; structured options notify the user (memory `ask-via-structured-options` — free-text prompts don't). Cons: one new conditional branch + a fail-closed path in Step 3c prose. Accepted.
4. **Mint a new audit-enforced rule ID for the edge.** Rejected: no new programmatic gate is introduced (reuses PCA-1 `pipeline_chain_audit`, mini-CAD `test_slice_skill_drift`, STP-1 `state_transition_pin_audit`). Per the ADR-038 `-D`-vs-`vN.N` convention + ADR-047 option-4 reasoning, a new bare gate ID is reserved for a new programmatic gate. This is a refinement of BFRD-1's terminal action; the changelog `Rule reference:` line carries `BFRD-1 (slice-046; ADR-048 partial-supersedes ADR-018 STOP-route; refines BFRD-1, mints no new rule)`.

## Decision

Adopt Option 3. Rewrite ONLY the "STOP-and-route behavior" sub-block of `skills/slice/SKILL.md` Step 3c into a **conditional confirm-then-auto-invoke** flow (canonical phrase `conditional confirm-then-auto-invoke`, pinned across N=3 surfaces: SKILL.md Step 3c prose + in-repo `methodology-changelog.md` v0.55.0 + this ADR). Preserve verbatim: the `### Step 3c: Bug-fix prelude (BFRD-1)` section title, the `bug-fix repro prelude discipline` opener phrase, detection sub-modes (a)/(b), the `shippability.md grep verification` mechanism, the verbal-claim-with-path fallback, and the Step 3b/Step 4 section anchors. Update the `## Pipeline position` BFRD-1 user-input-gate line so the HALT is the confirm/modify prompt only (on Confirm, `/slice` auto-invokes `/repro` and continues — no route-back-to-user); PCA-1 chain shape (`successor: /design-slice`, `auto-advance: true`) is unchanged. 4-part atomic version bump `0.54.0 → 0.55.0` (PMI-1).

## Consequences

- `skills/slice/SKILL.md` Step 3c terminal sub-block rewritten; forward-synced to `~/.claude/skills/slice/SKILL.md` (mini-CAD-1 EOL-agnostic content-equality, ADR-033, preserved).
- `skills/slice/SKILL.md` `## Pipeline position` BFRD-1 gate line reworded; PCA-1 `pipeline_chain_audit` stays clean (it parses only the 4 required fields + the `**user-input gates**` literal, not gate-list contents).
- **STP-1 Sub-form A** (slice-044) stays clean by construction: all pre-existing `test_slice_skill.py` BFRD-1 positive-pin literals + section anchors are preserved; the new positive pin's literal is the deliverable; the new negative pin is an `ast.NotIn` node (STP-1-excluded per ADR-047 §residual-B1 / DR-1 B-add-1). Zero pre-existing test realignment.
- `methodology-changelog.md` v0.55.0 entry (in-repo + installed) with a `Rule reference:` line; 1 new entry-pin test in `test_methodology_changelog.py`; 1 new prose-pin test in `test_slice_skill.py`; `architecture/shippability.md` row 46. `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml:version` → `0.55.0`.
- Every future bug-fix `/slice` invocation that lacks a failing repro test now confirms-then-auto-invokes `/repro` instead of dead-ending; the manual `/repro` + manual `/slice` re-invocation round-trip is removed. The repo becomes canonical for the directive in memory `repro-confirm-then-auto-invoke` (that memory degrades to reinforcing context).

### Introduced residual (the failure surface this change creates)

A new fail-closed branch exists: at the confirm gate, "Not a bug — cancel" MUST NOT auto-invoke `/repro` and MUST NOT silently proceed. If this branch were mis-specified to fall through to Step 4, BFRD-1's Failure-mode-2 protection would be lost (a non-bug slice proceeds with no guard, or a wrong-signature test gets auto-established). Bounded in design.md "Error model for this slice" + mission-brief must-not-defer + the new `test_slice_skill.py` negative pin (old unconditional-punt instruction absent) + positive pin (conditional phrase present). Not deferred.

## Reversibility

**cheap.** The change is a single Step 3c sub-block rewrite + one `## Pipeline position` line + an append-only superseding changelog entry + an atomic version bump + two appended test functions + one shippability row — the same magnitude class as ADR-018 itself (~10 sites) and the slice-040/043 conformance-edit precedent. Revert path: restore the STOP blockquote sub-block + the prior gate line, append a superseding changelog entry, remove the two new test functions, forward-sync, atomic bump. No persistent state, no data/runtime surface, no consumer outside `/slice` Step 3c + the PCA-1/mini-CAD/STP-1 audits (all reused unchanged). The append-only v0.55.0 entry and the empirical record of bug-fix slices that took the new edge are documentation-record-class (do not block revert).
