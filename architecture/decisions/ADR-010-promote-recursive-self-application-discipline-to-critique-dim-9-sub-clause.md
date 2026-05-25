---
id: ADR-010
title: Promote recursive-self-application discipline to agents/critique.md Dim 9 6th sub-clause via append-new (RSAD-1)
date: 2026-05-13
slice: slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-010: Promote recursive-self-application discipline to agents/critique.md Dim 9 6th sub-clause (RSAD-1)

**Note on rule-ID naming** (per slice-010 Critic B5 calibration-trail convention extension): the rule is named **RSAD-1 "Recursive Self-Application Discipline"** with -D suffix at end of abbreviation. The -D signals prose-heuristic / discipline semantics, distinct from the audit-enforced gate semantics of sibling rules (BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1 — each has a corresponding `tools/*_audit.py` enforcing the rule programmatically; RSAD-1 does not — the rule lives in `agents/critique.md` Dim 9 sub-clause body prose only, depending on the Critic agent reading the sub-clause at /critique invocation time). The -D convention extends slice-010's -T-suffix convention (MCT-1 "Mandatory Critic Trigger"; -T for /slice-time prose-heuristic) to discipline-class prose-heuristics applied at /critique-time within the adversarial agent prompt. v2 candidate at slice-N+ if drift surfaces: build `tools/rsad_1_audit.py` walking `architecture/slices/*/critique.md` and asserting cross-cutting tooling slices' Critic actually probed the slice's own artifacts for rule-class violations. Deferred at slice-011 to stay within the ~0.5-day budget.

## Context

The Critic agent at `agents/critique.md` carries the project's adversarial review prompt with 9 named dimensions. Dimension 9 ("Cross-cutting conformance") was introduced at slice-006 (ADR-005 / CCC-1 v1) with 5 sub-clauses (3 cross-references to Dim 1/4 surgical sub-bullets + 2 N=1 standalone sub-clauses: runtime-environment, language-version). Slice-009 (ADR-008 / CCC-1 v1.1) refined sub-clause 2's body inline without changing the 5-count structural invariant.

Across slices 9-10, an empirical pattern accumulated in the reflection record that is NOT covered by any of the existing 5 sub-clauses: **recursive self-application** — slices that author methodology refinements have their own artifacts (mission-brief, design.md, ADRs, /critique fix prose) containing instances of the defect class the slice is encoding.

**N=3 cumulative evidence across two distinct phases**:

1. **Slice-009 M2 (design-time; N=1)** — slice-009 authored CCC-1 v1.1 refining Dim 9 sub-clause 2 with the "design.md mechanical tables vs methodology canonical inventories" surface (positive-inclusion + negative-exclusion + install-time-rename + plugin manifest + changelog-versioned-entry conventions, naming FIVE canonical inventory surfaces). The Critic at /critique caught slice-009's own design.md committing the EXACT class of design-doc-vs-canonical-inventory drift the slice was encoding — slice's own draft demonstrated the defect class in the artifact authoring the refinement. Strongest single-instance methodology-internalization observation in the project at slice-009. Promoted from N=1 watch-list to N=2 candidate.

2. **Slice-010 design-time stress-test catches B1 + M1 + B5 (N=2 cumulative)** — slice-010 authored MCT-1 ("Mandatory Critic Trigger" for in-house methodology surfaces). The Critic at /critique caught THREE rule-class violations in slice-010's own draft:
   - **B1 "8 of 9 design-stage catches" framing** — the slice's own bullet body draft contained an internally-inconsistent counter claim that, if shipped, would have canonized the inconsistency into the canonical SKILL.md + append-only changelog.
   - **M1 bullet-style asymmetry** — the slice's own SKILL.md bullet body draft was ~3x longer / ~5x more syntactically complex than the existing 7 sibling bullets the slice was extending; the Critic catch enforced stylistic uniformity with the existing list members.
   - **B5 rule-naming convention break** — the slice's own changelog draft named the new rule "MCR-1 Mandatory Critic Rule" which would have conflated audit-enforced-gate semantics (the existing BC-1/PMI-1/CAD-1/TF-1/RR-1/INST-1/VAL-1/WIRE-1 convention, each paired with `tools/*_audit.py`) with /slice-time prose-heuristic semantics (no audit). The Critic catch forced rename to MCT-1 with -T-suffix to signal the new prose-heuristic class.
   All three are rule-class violations in the slice's own prose, caught at /critique design-time stress-test. Slice-010 ratcheted the cumulative phenomenon evidence to N=2 across two slices (slice-009 + slice-010 design-time).

3. **Slice-010 build-time DEVIATION-3 (N=3 cumulative; Critic-MISSED at /critique)** — at /critique B4 fix step, slice-010 appended an empirical-rebuttal prose paragraph to mission-brief.md L81 + design.md L193 EXPLICITLY DESCRIBING BC-PROJ-2's positive-anchor strings (the literal substrings `fence`, `code-block`, `llm`) as evidence that BC-PROJ-2 would not positively fire on slice-010's pre-/critique prose. The fix prose ITSELF contained those substrings — RE-INTRODUCING the trigger anchors into the slice's artifacts. At /build-slice Phase 4 BC-1 self-application audit, BC-PROJ-2's anchor path POSITIVELY FIRED on slice-010's own mission-brief + design.md via the fix prose's literal substrings — a build-time recursive-self-application phenomenon at one level deeper than the design-time mode. Critic-MISSED at /critique time (the Critic stress-tested the pre-fix prose but did not anticipate that the fix prose ITSELF would introduce the trigger anchors). Slice-010 ratcheted the cumulative phenomenon evidence to N=3 across two distinct phases: design-time (slice-009 M2 + slice-010 B1/M1/B5) + build-time-via-/critique-fix-prose (slice-010 DEVIATION-3).

The slice-009 + slice-010 reflections each named the explicit promotion threshold: "Promote `recursive-self-application-discipline` to /critique skill prose at N=3 if a third instance surfaces at slice-011+". The N=3 threshold is met as of slice-010 completion (2026-05-12); slice-011's mission is to codify the discipline.

Without codification, the discipline remains tacit reflection-only knowledge. Future cross-cutting tooling slices (modifying skill prose, agent prompts, in-house audits, or methodology rules) would not benefit from the Critic agent's adversarial prompt explicitly stress-testing the slice's own draft against the very discipline being encoded, NOR from the explicit build-time recursive-self-application sub-mode that catches /critique fix prose introducing anchor substrings into the slice's artifacts. The Critic-MISSED at /critique class observed at slice-010 DEVIATION-3 (the build-time sub-mode) would recur in future slices without the codified discipline.

## Options considered

### Option 1 — Append new 6th sub-clause to Dim 9 (CHOSEN)

Append ONE new sub-clause to `agents/critique.md` Dim 9 ("Cross-cutting conformance") at L167 between the existing L166 `Language-version conformance` sub-clause close and the existing L168 `### Bonus: weak graph edges` H3 anchor. Sub-clause title `Recursive self-application discipline`. Body names BOTH sub-modes (design-time + build-time-via-/critique-fix-prose) with N=3 cross-slice anchors and abstract descriptions (avoiding literal BC-PROJ-2 anchor substrings to keep the canonical Critic-prompt body BC-1-clean at future audit runs on `agents/critique.md`).

Dim 9 structural-invariant grows 5 → 6 sub-clauses. Test `test_critique_dim_9_lists_five_sub_clauses` REPLACED (not added alongside) by `test_critique_dim_9_lists_six_sub_clauses` per PMI-1 versioned-gate supersession discipline applied at the structural-invariant level. No two structural-invariant tests coexist.

**Pros**:
- Sub-clause stays within Dim 9's existing structural home; readers continue to find recursive-self-application cross-cutting concerns in Dim 9's enumeration without searching across dimensions.
- Slice-009 (CCC-1 v1.1) precedent for refining Dim 9 sub-clause bodies inline; slice-011 extends to APPEND-NEW (one level beyond inline refinement). Both stay within the Dim 9 surface — no churn to Dim 1-8.
- Mirrors slice-010 MCT-1's structural style: rule-ID + Limitations note + 5 prose-pin tests pattern + bidirectional changelog-pin + PMI-1 versioned-gate supersession. Stylistic uniformity with the most recent similar slice.
- Canonical body uses ABSTRACT descriptions of build-check rule anchors (`positive-anchor strings`, `the substring literals the rule fires on`) instead of literal anchor values. The canonical Critic-prompt artifact stays BC-1-clean at future audit runs on `agents/critique.md` itself (the slice-010 DEVIATION-3 build-time recursive-self-application phenomenon is pre-empted on the canonical body; only slice-011's TRANSIENT artifacts — mission-brief + design.md + this ADR — carry the literal anchors for empirical evidence, dispositioned defer-with-rationale at /validate-slice per BC-1 Important semantics).
- Reversibility: cheap. Revert path is single git diff revert + superseding methodology-changelog entry retracting RSAD-1.
- Test scaffolding fits slice-007/009/010 prose-pin convention: 1 structural-invariant supersession + 1 canonical-literal substring pin + 1 location-pin (per slice-009 M1 + DEVIATION-2 pre-emption with scoped `.find()`) + 1 sub-mode pin (both `design-time` AND `build-time` substrings) + 1 cross-slice anchor pin (≥2 of slice-009/slice-010 + ≥1 of M2/DEVIATION-3/BC-PROJ-2/B1/B5/M1 = 5 prose-pin tests total).

**Cons**:
- Existing test `test_critique_dim_9_lists_five_sub_clauses` requires REPLACE (not extend) — slight test-churn cost ratifying the structural-invariant supersession. Mitigated by treating this as canonical methodology pattern (mirrors PMI-1 versioned-gate supersession at the structural-invariant level; N=1 occurrence at slice-011; promotes to N≥2 stable if another structural-invariant supersession surfaces).
- The Dim 9 structural-invariant is now 6-sub-clause; future Dim 9 sub-clause additions (e.g., the case-sensitivity-canonical-literal-pin-discipline at N=2 evidence; `.find()`-collision discipline at N=2 evidence) would similarly grow the structural invariant. Mitigated by promotion-threshold discipline (N≥3 each, per the precedent set at slice-011); section bounded by actual empirical sub-class count.

### Option 2 — Inline-refine existing Dim 9 sub-clause body (REJECTED)

Refine existing Dim 9 sub-clause 1 ("Methodology-audit conformance") or sub-clause 2 ("Tooling-doc-vs-implementation parity") body with new sentences covering recursive-self-application phenomenon. Preserves the 5-count structural invariant.

**Pros**: no test-churn on `_lists_five_sub_clauses`; pure inline body extension (slice-009 CCC-1 v1.1 precedent).

**Cons**: recursive-self-application is a META-LEVEL discipline (it operates ON ANY sub-clause / dimension / rule the slice is encoding) — fitting it into ANY of the 5 existing sub-clauses miscategorizes it as a peer-of-the-cross-references rather than the meta-level discipline it is. None of the 5 existing sub-clauses semantically fits: Methodology-audit conformance (Dim 4 surgical sub-bullet refinement); Tooling-doc-vs-implementation parity (Dim 1 surgical sub-bullet); Algorithm-path-conformance (Dim 4 surgical sub-bullet); Runtime-environment (slice-001 N=1); Language-version (slice-004 N=1). The phenomenon operates above these, not within any one. Rejected: meta-level discipline deserves its own structural slot.

### Option 3 — Add new top-level dimension (REJECTED)

Introduce a "Dim 10 Recursive self-application" at the top level alongside the existing 9 dimensions.

**Pros**: maximally visible; recursive-self-application gets its own dedicated section.

**Cons**:
- N=3 evidence for a new top-level DIMENSION is far below the threshold the project applies for promoting dimensions (Dim 9 itself accumulated N=10 sub-class hits across 5 distinct slices before the 2026-05-10 /critic-calibrate user-override promoted it; even then it was Meta-Critic-declined initially). Three instances is sub-class-scale, not dimension-scale.
- Existing test `test_critique_lists_nine_dimensions` would need REPLACE → `lists_ten_dimensions`; multiple prose-pin sites referencing "9 dimensions" across `agents/critique.md` + `skills/critique/SKILL.md` would need updates. Per slice-006 reflection (`s/8 dimensions/9 dimensions/` at 7 prose-parity sites): the dimension-count update is a multi-site change with cross-skill drift potential. ~20+ surface sites. Magnitude scales to ADR-005-class (expensive with irreversible portion).
- Recursive self-application is a META concern about cross-cutting (does THIS slice cross-cut itself with the rule it's encoding?) — it's intrinsically a SUB-class of cross-cutting-conformance, not a peer dimension to it. Promoting to peer-dimension loses the semantic relationship.
Rejected: scale and semantics both argue for sub-clause not dimension.

## Decision

**Adopt Option 1** — append a new 6th sub-clause `Recursive self-application discipline` to `agents/critique.md` Dim 9 between the existing `Language-version conformance` sub-clause close and the `### Bonus: weak graph edges` H3 anchor. Sub-clause body documented under "What's new" in [[slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose/design.md]] § Sub-clause canonical body. Codify as new methodology rule **RSAD-1** in `methodology-changelog.md` v0.26.0 under `### Added` with explicit Limitations note (acknowledging /critique-time adversarial-prompt heuristic prose semantics; no audit-enforced gate; v2 candidate `tools/rsad_1_audit.py` if drift surfaces). PMI-1 atomic version bump 0.25.0 → 0.26.0 with versioned-gate supersession (slice-010's `_at_0_25_0` → slice-011's `_at_0_26_0`; N=4 supersession event post-completion). Replace existing structural-invariant test `_lists_five_sub_clauses` with `_lists_six_sub_clauses` per PMI-1 versioned-gate supersession discipline applied at the structural-invariant level.

The canonical body uses ABSTRACT descriptions of build-check rule anchor STRINGS (`positive-anchor strings`, `the substring literals the rule fires on`) rather than literal anchor values — the rationale is **stylistic / reusable-artifact-readability** (per slice-011 Critic M1 correction): the canonical Critic-prompt artifact at `agents/critique.md` is consumed by every future Critic invocation, so abstract framing of anchor strings reads better there, while the literal anchor strings belong in slice-N reflection records as empirical primary sources where they have retrieval traction. The rule-ID `BC-PROJ-2` IS named explicitly in the body (matches existing Dim 9 sub-clause convention naming `BC-1`, `RR-1`, `TF-1`, etc. by ID); only the anchor STRINGS stay abstract. **Note** (per slice-011 Critic M1 correction): an earlier-drafted rationale claiming "canonical-body abstract framing keeps `agents/critique.md` BC-1-clean at future audit runs" was based on a misreading of BC-1's audit scope — BC-1 reads `mission-brief.md` + `design.md` of the slice being audited (per `tools/build_checks_audit.py::_read_slice_text` L435-L442), NOT the content of `agents/critique.md` or any other changed file. So the canonical body's content has no BC-1-firing role regardless; abstract framing is purely a readability choice.

Slice-011's TRANSIENT artifacts (mission-brief.md + design.md + this ADR) DO carry the literal BC-PROJ-2 anchor strings (`fence`, `code-block`, `llm`) for empirical evidence of the build-time-via-/critique-fix-prose sub-mode; dispositioned defer-with-rationale at /validate-slice per BC-1 Important semantics (BC-PROJ-2 negative-anchor migration is a separate slice-011+ candidate at N=2 evidence threshold now met: slice-005 + slice-011; not bundled here). The two-tier discipline (canonical reads abstractly / transient demonstrates concretely) makes slice-011 the canonical reference instance of the rule it encodes.

## Consequences

**Immediate** (slice-011 ship):
- `agents/critique.md` Dim 9 section grows 5 → 6 sub-clauses; sub-clause body inserted at L167.
- `~/.claude/agents/critique.md` byte-equal post-forward-sync (CAD-1 invariant from slice-007).
- `methodology-changelog.md` v0.26.0 entry appended (in-repo + installed) with RSAD-1 rule reference + explicit Limitations note.
- `tests/methodology/test_critique_agent.py` gains 5 net new tests (5 added: `_lists_six_sub_clauses` + 4 RSAD-1-specific; 1 removed: `_lists_five_sub_clauses`).
- `tests/methodology/test_methodology_changelog.py` gains 1 bidirectional changelog-pin test (`test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed`) + 1 PMI-1 versioned-gate test (`_at_0_26_0` supersedes slice-010's `_at_0_25_0`).
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.26.0.
- `architecture/shippability.md` row 11 added; row 10 header updated.

**Downstream** (slice-012 and beyond):
- Every Critic /critique invocation reads the new 6th sub-clause when applying Dim 9 to the slice under review. For cross-cutting tooling slices (matching MCT-1 trigger glob from slice-010), the Critic is now explicitly directed to: (1) stress-test the slice's draft prose against the very discipline being encoded; (2) anticipate /critique fix prose introducing empirical examples may RE-INTRODUCE triggers into the slice's artifacts.
- Cross-cutting Dim 9 catch rate projected to improve at slice-012+: slice-010 reflection records the trajectory at 87.5% (7 of 8 sub-class hits caught at /critique); the 1 build-time miss at slice-010 (DEVIATION-3) was the exact phenomenon RSAD-1 codifies. Future cross-cutting tooling slices with empirical-rebuttal /critique fix prose should see the build-time recursive-self-application sub-mode caught at /critique time rather than at /build-slice Phase 4.
- `/critic-calibrate` next-run effectiveness check (per slice-010 reflection at slice-012-015 boundary): the cumulative cross-cutting miss count through slice-010 is 9 misses (4.5x the ≤2 target across slices 6-15; 5 slices remaining in window). RSAD-1 codification is one calibration-response candidate (refining the Critic prompt with the new sub-clause); the other is recalibrating the quantitative target downward. /critic-calibrate at slice-012-015 will assess whether RSAD-1 alone has moved the catch rate sufficiently OR whether further refinements / quantitative-target adjustments are needed.
- The methodology rule-ID naming convention now encompasses TWO prose-heuristic letter-conventions:
  - **-T-** infix/suffix (MCT-1 v0.25.0): /slice-time mandatory-Critic trigger heuristic; reads prose at /slice invocation.
  - **-D** suffix (RSAD-1 v0.26.0): /critique-time adversarial-prompt discipline heuristic; reads prose at /critique invocation.
  Future prose-heuristic rules can use either convention based on phase semantics; audit-enforced gates remain in the existing letter convention (BC-1 / PMI-1 / etc.). Generic methodology pattern; the B5 calibration-trail discipline (slice-010) is now extended to N=2 evidence at the rule-ID convention level.

**Cumulative-Critic-influence note**: RSAD-1 is applied prospectively — slice-012 onward. Past slices (slice-001..011) retain their original /critique outputs (the discipline existed implicitly via slice-009 + slice-010 reflection records but was not codified in the Critic agent prompt). The methodology-changelog entry documents this as the new behavior at slice-011+; no retroactive re-evaluation of past slices' /critique outputs.

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 Critic M4 + slice-010 Critic m3 precedent).

**Magnitude estimate** (~12 sites total):

1. `agents/critique.md` — sub-clause body append at L167 (1 site, ~12 lines of prose)
2. `~/.claude/agents/critique.md` — forward-sync mirror (1 site)
3. `methodology-changelog.md` — v0.26.0 entry (1 site, ~30 lines)
4. `~/.claude/methodology-changelog.md` — forward-sync mirror (1 site)
5. `VERSION` — bump 0.25.0 → 0.26.0 (1 site)
6. `~/.claude/ai-sdlc-VERSION` — forward-sync mirror (1 site)
7. `plugin.yaml.version` — bump 0.25.0 → 0.26.0 (1 site)
8. `tests/methodology/test_critique_agent.py` — replace `_lists_five_sub_clauses` with `_lists_six_sub_clauses` + add 4 RSAD-1-specific tests (5 net additions; 1 deletion in same commit)
9. `tests/methodology/test_methodology_changelog.py` — add `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` + replace `_at_0_25_0` with `_at_0_26_0` (2 sub-edits in 1 file)
10. `architecture/shippability.md` — add row 11 + update row 10 header (2 sub-edits in 1 file)
11. `architecture/decisions/ADR-010-*.md` — this file itself
12. `architecture/slices/slice-011-.../` — mission-brief.md + design.md + milestone.md + (eventually) critique.md + build-log.md + validation.md + reflection.md (slice's own artifact folder)

**Comparison to prior ADRs**:
- ADR-005 (CCC-1 v1, slice-006) — **expensive** with irreversible portion. Added entire 9th Critic dimension + 7 prose-parity sites + Kiczales citation; surface area ~30+ sites.
- ADR-006 (CAD-1, slice-007) — **cheap** with 5 enumerated irreversibles. Surface area ~5-10 sites.
- ADR-007 (BC-1 v1.2, slice-008) — **cheap**. Surface area ~10-15 sites.
- ADR-008 (CCC-1 v1.1 inline refinement, slice-009) — **cheap** with magnitude justification. Surface area ~5 sites.
- ADR-009 (MCT-1, slice-010) — **cheap** with magnitude justification. Surface area ~11-13 sites.
- **ADR-010 (this) — cheap with magnitude justification**. ~12 sites; closer in magnitude to **ADR-009 (~11-13 sites)** and **ADR-007 (~10-15 sites)** than to ADR-008's ~5-site inline-refinement. The append-new + 5 prose-pin tests + bidirectional changelog + atomic version bump puts slice-011 in the BC-1-v1.2 / MCT-1 magnitude class. Still cheap on reversibility because each site is small and the revert path is git-diff-revert + superseding changelog entry.

**Revert path**:
1. Git diff revert of slice-011's commits (single-slice revert is clean since no in-flight cross-slice dependencies exist).
2. Append a superseding methodology-changelog entry retracting RSAD-1 (e.g., `## v0.27.0 — <date>` with `### Retired` section naming RSAD-1 + rationale for retirement). Per PMI-1 + changelog inclusion heuristic.
3. Remove the 5 new test functions + reinstate `_lists_five_sub_clauses`. Reinstate `_at_0_25_0` PMI-1 versioned-gate (or supersede to whatever VERSION ends up at).
4. Forward-sync the reverted `agents/critique.md` + `methodology-changelog.md` to `~/.claude/`. Confirm byte-equality.

**Irreversible portion** (minor, append-only):
- The `methodology-changelog.md` v0.26.0 entry itself, once committed, becomes part of the append-only changelog history. A retraction is a SUPERSEDING entry, NOT a deletion. Reading the file historically will always show "RSAD-1 was added at slice-011 and retired at slice-N".
- Cumulative slice-011-N Critic invocations that ran (and the artifacts they produced) under RSAD-1's recursive-self-application discipline are part of the project's empirical record. The Critic invocations themselves can't be un-invoked.
- The RSAD-1 -D-suffix rule-ID naming convention itself, once introduced into the changelog, establishes a precedent future readers may apply when interpreting other rule-IDs. A retraction of RSAD-1 doesn't retract the convention; future prose-heuristic rules may still use -D suffix.

Both irreversible portions are documentation-record-class (not functional-behavior-class). Neither prevents revert; they only mean the project's history would record RSAD-1 as having existed.

**Conclusion**: Reversibility is **cheap**. Magnitude is ~12 sites (same class as ADR-007 / ADR-009; larger than ADR-008's inline-refinement). Revert path is well-trodden (single-slice git diff revert + superseding changelog entry). Adopt Option 1.
