# Reflection: Slice 046 add-conditional-repro-auto-advance

**Date**: 2026-05-19
**Shipped**: YES

## Validated

- **STP-1 Sub-form A "clean by construction" is the correct pattern for a prose-repoint of a pinned `SKILL.md` section** — design preserved all 3 pre-existing `test_slice_skill.py` BFRD-1 positive-pin literals (`bug-fix repro prelude discipline`, `shippability.md grep verification`) + the Step 3b/3c/4 anchors verbatim; the new positive pin's literal is the deliverable; the new negative pin is `ast.NotIn`-excluded. Validated by reality: `tools.state_transition_pin_audit` clean on the real artifact, all 12 `test_slice_skill.py` pins green, **zero pre-existing test realignment**.
- **PCA-1 parser contract-safety** — design claimed `pipeline_chain_audit` reads only the 4 required fields + the `**user-input gates**` literal (not gate-list contents), so rewording the BFRD-1 gate line is safe. Validated: gate line reworded, PCA-1 audit clean.
- **mini-CAD-1 EOL-agnostic forward-sync** — drift test FAILed pre-sync (mid-slice smoke, as predicted) → PASSed post-sync.
- **Genuine-contrast test-first on a prose AC** — the positive pin (`conditional confirm-then-auto-invoke` absent pre-edit) + negative pin (`` re-invoke `/slice` `` present pre-edit) gave an independently grep-verifiable, non-tautological FAIL→PASS with no revert needed.
- **N=3 canonical-phrase schema-pin** — `conditional confirm-then-auto-invoke` present in all 3 surfaces (SKILL.md Step 3c / changelog v0.55.0 / ADR-048), validated by the entry-pin + prose-pin tests.

## Corrected

- None. The slice shipped exactly per design.md with **zero deviations**. design.md was already corrected pre-build by the dual-Critic loop (M1 negative-anchor literal, m1 META-1 header shape) and DR-1 (m-add-1 bounded auto-invoke) — so the design reflected reality before the first code edit. The memory note `repro-confirm-then-auto-invoke` anticipated this codification landing in "slice-047"; the authoritative slice-045 Deferred numbering put it at slice-046 — corrected by shipping it as slice-046 (slice-047 remains `add-two-scope-install`). The memory is now reinforcing-context-only (the repo is canonical).

## Discovered

- **First-Critic blind-spot on behavior-reclassification slices**: the first Critic's energy went to the mechanical surface (prose-pin negative-anchor literal M1, changelog header shape m1) and it MISSED the unbounded re-entrancy on the NEW auto-invoke control-flow edge — the slice's entire raison d'être. DR-1 caught it (m-add-1). Pattern (N=1, `/critic-calibrate` watch-list): on a slice that *reclassifies an existing gate's behavior*, task the Critic explicitly to trace the new edge's termination/loop semantics, not only the pin/changelog mechanics. The durable backstop remains DR-1, not a new first-Critic dimension (slice-037 law).
- **PCA-1's "lighter checkpoint beats hand-off" philosophy generalizes to gates with a genuine safety rationale**, not just mechanical gates: BFRD-1's STOP existed for a real reason (ADR-018 Failure-mode-2), yet a confirm-the-distilled-description checkpoint fully preserves that protection while removing the mechanical punt. Confirms the auto-advance philosophy is not limited to no-op gates.

## Deferred

- **slice-047 `add-two-scope-install`** — user-level (`~/.claude`) vs project-level (`<proj>/.claude`) install scope chosen interactively. Reason: structural, high-care (INST-1/CAD-1/PMI-1 self-hosting contracts become scope-dependent), needs its own design.md + `/critique` + ADR. Lands in: next slice (queued; was slice-045 Deferred #2, now #1).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` + reality during build/validate:

- **M1** (genuine-contrast negative-anchor literal unspecified): **VALIDATED** — disposition ACCEPTED-FIXED; reality confirmed the concern was load-bearing — the test-first FAIL captured exactly because the positive literal was absent and (had the negative literal been ill-chosen) the AC1 guard would have been tautological. The pinned `` re-invoke `/slice` `` literal flipped FAIL→PASS cleanly.
- **m1** (v0.55.0 header must match META-1 em-dash+ISO regex): **VALIDATED** — disposition ACCEPTED-FIXED; the v0.55.0 entry was authored with em-dash U+2014 + ISO date and `test_each_changelog_entry_carries_rule_reference` (META-1) passed. A hyphen would have silently skipped the block, exactly as flagged.
- **m2** (design.md embeds a stale ADR-048 full-text excerpt): **FALSE-ALARM** — disposition OVERRIDDEN; reality (grep of design.md: only thin `[[ADR-048]]` refs, no `## ADR-048 (full text)` block) confirmed the override. The first Critic misattributed the `/critique` skill's agent-input paste template to design.md. DR-1 independently confirmed correctly-overridden false positive.
- **m-add-1** (unbounded post-auto-invoke re-verification loop): **VALIDATED (via DR-1)** — MISSED by the first Critic; caught by the meta-Critic; disposition ACCEPTED-FIXED. Reality confirmed it was a genuine prose-ambiguity on the slice's core new path (the design did not state whether a still-missing `tests/bugs/*` row after `/repro` falls through to the fallback, loops, or fail-closes). Fixed pre-build.

**Missed by Critic**: m-add-1 — the unbounded auto-invoke re-verification edge. The first Critic reviewed the prose-pin + changelog-header mechanics thoroughly (3/3 VALID, no over-reach besides the m2 false positive) but did not trace the termination semantics of the NEW control-flow edge that is the slice's purpose.

**Pattern**: DR-1 dual-review keeps paying decisively on methodology-codification/reclassification slices (N+1 to the standing 026/029/038/039 pattern — here a *reclassification* sub-class). The first Critic's structural blind spot on these slices is the novel behavioral edge itself; its precision on the mechanical pin/changelog surface stays high. Recommend `/critic-calibrate` watch-list entry: "behavior-reclassification slice → first Critic under-weights the new edge's loop/termination semantics; DR-1 is the backstop." N=1.

## Lessons for next slice

- **For a slice that reclassifies an existing gate's behavior (not a new rule), the first Critic optimizes the mechanical pin/changelog surface and under-weights the NOVEL control-flow edge that is the slice's raison d'être** — budget DR-1 as the structural backstop for the new edge's re-entrancy/termination (m-add-1 was caught exactly there, missed by the first Critic). `/critic-calibrate` watch-list, N=1.
- **Genuine-contrast test-first works cleanly for a prose-reclassification AC without reverting anything**: pin a positive (the new canonical phrase, grep-verified absent pre-edit) + a negative (the exact old literal taken verbatim from the file, grep-verified present pre-edit). Both flip in one direction when the edit lands — a non-tautological FAIL→PASS that is cheaper than the slice-045 revert-2-edits technique and independently verifiable per-literal.
- **STP-1 Sub-form A "clean by construction" is the validated pattern for any prose-repoint of a pinned `SKILL.md` section**: preserve every pre-existing positive-pin literal + section anchor verbatim, make the new positive pin's literal the deliverable, and keep the new negative pin an `ast.NotIn` node (Sub-form-A-excluded). Zero stale-pin realignment. The "rule minted in slice N is a blind spot on N+1" risk (STP-1 minted slice-044, slice-046 is an early governed slice) was pre-empted explicitly in design and held in practice.
- **PCA-1's lighter-checkpoint-beats-hand-off principle extends to safety-rationale gates**: when retiring a mechanical hand-off that guards a real failure mode, replace it with a *confirm-the-specific-input* checkpoint (structured options, per `ask-via-structured-options`) — the protection survives, the punt does not.

## Vault updates made (thin vault — small list)

- This slice's [[design.md]] — M1/m1 (pre-build, /critique) + m-add-1 (pre-build, /critique-review) ACCEPTED-FIXED edits; reflects shipped reality (no post-build correction needed).
- [[decisions/ADR-048]] — created, `supersedes: ADR-018` (partial — STOP-route decision only); ADR-018 left `status: accepted` per append-only + ADR-020 partial-supersession precedent (the superseded ADR keeps its status; the new ADR carries the slot + body scope).
- `methodology-changelog.md` — v0.55.0 entry (in-repo + installed forward-synced; MCFS-1 PASS).
- [[risk-register.md]] — no entry (methodology-friction codification per standing user directive; no open risk retired, no new risk surfaced — the discovered first-Critic-blind-spot pattern is a `/critic-calibrate` watch-list item, not a code/risk surface).
- [[shippability.md]] — row 46 (the new BFRD-1-reclassification content-pin + v0.55.0 entry-pin; per the slice-038→R-10 lesson the Step 5.3 entry IS the added mini-CAD/content pin itself).
- Memory `repro-confirm-then-auto-invoke` — now reinforcing-context-only (repo is canonical); the slice-046-not-047 numbering is recorded here.
