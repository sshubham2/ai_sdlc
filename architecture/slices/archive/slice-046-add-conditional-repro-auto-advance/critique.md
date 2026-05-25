# Critique: Slice 046 add-conditional-repro-auto-advance

**Critic reviewed**: mission-brief.md, design.md, new ADR (ADR-048)
**Date**: 2026-05-19
**Result**: NEEDS-FIXES

## Summary

The slice is well-scoped, the supersession structure is precedent-grounded, and the load-bearing audit-conformance claims (PCA-1 parser-contract-safety, STP-1 Sub-form A by-construction cleanliness, v0.34.0 entry-pin block-locality) verify against the actual implementations. One Major: the design under-specified the *behavioral content* of the new Step 3c confirm flow against the genuine-contrast test it claims to author. Two Minors around changelog META-1 header-shape conformance and a claimed stale design excerpt. No blockers.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: The genuine-contrast prose-pin test's negative-anchor literal is unspecified, risking a tautological-or-brittle AC1 guard
- **Claim under review**: design.md "Genuine-contrast build discipline" + STP-1 section's `<old unconditional-punt instruction>` placeholder.
- **Issue**: The negative pin's exact literal was left as a placeholder. AC1's genuine-contrast proof depends entirely on which substring the negative pin asserts-absent; a poorly-chosen literal either never genuinely FAILs on the unmodified file (tautological — defeats the slice-043/045 lesson the design explicitly invokes) or blocks legitimate replacement prose. Builder would have picked it ad hoc at build time — exactly the gap the slice-045 "content-bearing AC needs a CONTENT pin" lesson warns against.
- **Evidence**: `skills/slice/SKILL.md:153-155` (verbatim STOP blockquote); design.md placeholder; aggregated lesson slice-043/045.
- **Proposed fix**: Pin the exact negative-anchor literal `` re-invoke `/slice` `` (unique to the unconditional hand-off — the new confirm flow has `/slice` itself auto-invoke `/repro`, so it must NOT instruct re-invoking `/slice`). State the chosen literal in both the STP-1 section and the genuine-contrast section so they agree; assert the positive literal is absent from the unmodified file (verified zero hits — genuine FAIL).
- **Builder draft**: ACCEPTED-FIXED — design.md STP-1 Sub-form A section + genuine-contrast section both now pin the exact literal `` re-invoke `/slice` `` (verbatim from `skills/slice/SKILL.md:155`), with the positive literal `conditional confirm-then-auto-invoke` confirmed grep-absent from the unmodified file (genuine pre-edit FAIL) and a build obligation that the rewritten Step 3c contains no `` re-invoke `/slice` `` occurrence. The two sections agree verbatim.

### Minors (log; address if cheap)

#### m1: v0.55.0 changelog entry header must match the META-1 em-dash + ISO-date split regex
- **Claim under review**: mission-brief AC4 / design.md: *"`methodology-changelog.md` gains a `v0.55.0` entry carrying a Rule reference"*.
- **Issue**: `test_each_changelog_entry_carries_rule_reference` (`test_methodology_changelog.py:136`) splits on `^## v\S+ — \d{4}-\d{2}-\d{2}` (em-dash U+2014 + ISO date). An ASCII-hyphen or date-less header would make the regex skip the block — silently passing META-1 (block uncounted) while the entry-pin test + readers expect it.
- **Evidence**: `test_methodology_changelog.py:136`; existing headers `methodology-changelog.md:37,51,225` all use `—` + ISO date.
- **Proposed fix**: Add a design.md line pinning the header shape `## v0.55.0 — 2026-05-19` (em-dash + ISO date) + the exact `Rule reference:` line content.
- **Builder draft**: ACCEPTED-FIXED — design.md "Rule-ID treatment" section now carries a "META-1 header-shape requirement (m1 ACCEPTED-FIXED)" paragraph pinning the exact em-dash-U+2014 + ISO-date header shape against `test_methodology_changelog.py:136`, with a match-existing-headers instruction.

#### m2: design.md embeds a stale ADR-048 "full text" excerpt (claimed)
- **Claim under review**: design.md "## ADR-048 (full text)" vs the authoritative on-disk `architecture/decisions/ADR-048-*.md`.
- **Issue**: Critic asserts design.md carries an abbreviated ADR-048 body that drifted from the longer on-disk file (the project's "don't carry forward stale design claims" discipline).
- **Evidence**: Critic cited design.md "## ADR-048 (full text)".
- **Proposed fix**: Replace with a reference, or sync verbatim.
- **Builder draft**: OVERRIDDEN — **false positive**. design.md contains NO `## ADR-048 (full text)` block; it carries only the thin one-line `[[ADR-048]]` reference at design.md:77 (grep-verified — see Triage rationale) plus a one-line entry under "Decisions made (ADRs)". The "## ADR-048 (full text)" block the Critic cites exists only in the `/critique` skill's agent-input prompt, where the skill pastes new ADRs verbatim for the Critic to review (per the skill's Step 2 template). It is not in design.md and never was. The thin-vault reference-not-duplicate discipline m2 advocates is already satisfied. No drift; nothing to fix.

## Dimensions checked

- [x] Unfounded assumptions — Verified, not assumed: PCA-1 parser reads only the 4 required fields + `**user-input gates**` literal (`tools/pipeline_chain_audit.py:91,235`); STP-1 excludes `ast.NotIn` own-op nodes (`state_transition_pin_audit.py:216-229`, ADR-047 §residual-B1); v0.34.0 entry-pin is scoped to the v0.34.0 block, not live SKILL.md. Baseline audits clean at 0.54.0.
- [x] Missing edge cases — Fail-closed "Not a bug — cancel" branch explicitly specified (must-not-defer + error model + ADR-048 residual). The only residual sharpness was the negative-pin literal (M1, now fixed).
- [x] Over-engineering — None. No new tool, no new rule ID (correctly reuses PCA-1 + mini-CAD + STP-1 per ADR-038/ADR-047).
- [x] Under-engineering — M1 (now ACCEPTED-FIXED): AC1 genuine-contrast guard lacked a pinned negative-anchor literal.
- [x] Contract gaps — None. PCA-1 gate-line parser-safety verified.
- [x] Security — None — methodology skill-prose + vault artifacts only.
- [x] Drift from vault — m2 (OVERRIDDEN, false positive — design.md carries no embedded ADR full text). ADR-048 supersession scope verified precisely targeted; ADR-020 partial-supersession precedent real; `test_adr_018_*` unaffected (append-only preserved).
- [x] Web-known issues — N/A (no external technology/API/library; in-repo methodology-prose + stdlib audit tooling).
- [x] Cross-cutting conformance — MEPD-1 discharged via branch (a) (no new rule; affirmative v0.55.0 entry + Rule reference + ADR-048 + PMI-1 4-part bump). STP-1 Sub-form A clean by construction. PTFCD-1: new pins target existing test files (no phantom-file). Shippability row 46 obligation noted (SCPD-1/RPCD-1).

## Triage

**Triaged by**: user
**Date**: 2026-05-19
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | design.md STP-1 Sub-form A section + genuine-contrast section both pin the exact negative-anchor literal `` re-invoke `/slice` `` (verbatim `skills/slice/SKILL.md:155`) + positive literal `conditional confirm-then-auto-invoke` grep-confirmed absent pre-edit; sections agree. |
| m1 | Minor | ACCEPTED-FIXED | design.md Rule-ID-treatment section pins the exact `## v0.55.0 — 2026-05-19` header shape (em-dash U+2014 + ISO date) against the META-1 split regex `test_methodology_changelog.py:136`. |
| m2 | Minor | OVERRIDDEN | False positive — design.md contains NO `## ADR-048 (full text)` block (only thin `[[ADR-048]]` refs at lines 11/84 + a one-line "Decisions made (ADRs)" entry). The full-text block exists only in the `/critique` skill's agent-input paste template, not design.md. Meta-Critic (DR-1) independently confirmed correctly-overridden FALSE POSITIVE. No drift; nothing to fix. |
| m-add-1 | Minor | ACCEPTED-FIXED | DR-1 meta-Critic missed-finding. design.md§"New Step 3c flow" step (4) + §"Error model" now state `/repro` is auto-invoked exactly once; a still-missing `tests/bugs/*` row routes into the preserved verbal-claim-with-path fallback (no `/repro` re-invoke, no loop) — auto-invoke edge bounded to one attempt. |
