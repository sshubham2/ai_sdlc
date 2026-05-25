---
id: ADR-014
title: Promote shippability-catalog consumer-reference propagation discipline to agents/critique.md Dim 9 8th sub-clause via append-new (SCPD-1)
date: 2026-05-13
slice: slice-015-refine-dim-9-with-shippability-catalog-propagation-sub-class
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-014: Promote shippability-catalog consumer-reference propagation discipline to agents/critique.md Dim 9 8th sub-clause (SCPD-1)

**Note on rule-ID naming** (per slice-010 Critic B5 calibration-trail convention + slice-011 RSAD-1 -D-suffix extension + slice-013 EPGD-1 -D-suffix N=2 stable confirmation; N=3 stable at slice-015): the rule is named **SCPD-1 "Shippability-Catalog Propagation Discipline"** with -D suffix at end of abbreviation. The -D signals prose-heuristic / discipline semantics applied at /critique-time AND /build-slice-time, distinct from the audit-enforced gate semantics of sibling rules (BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1 — each has a corresponding `tools/*_audit.py` enforcing the rule programmatically; SCPD-1 does not — the rule lives in `agents/critique.md` Dim 9 sub-clause body prose only, applied by the Critic agent reading the sub-clause at /critique invocation time AND by the Builder reading the design.md Phase plan at /build-slice). The -D convention extends slice-011's RSAD-1 -D-suffix establishment and slice-013's EPGD-1 -D-suffix confirmation to a third prose-heuristic Discipline at N=3 stable. The methodology rule-ID naming convention now encompasses two prose-heuristic letter-conventions stably:

- **-T-** infix/suffix (MCT-1 v0.25.0): /slice-time mandatory-Critic trigger heuristic
- **-D** suffix (RSAD-1 v0.26.0 + EPGD-1 v0.28.0 + SCPD-1 v0.30.0): /critique-time + /build-slice-time discipline heuristic; **N=3 stable post-slice-015**

v2 candidate at slice-N+ if drift surfaces: build `tools/scpd_1_audit.py` walking `architecture/slices/*/design.md` Phase plans and asserting that any Phase plan superseding a test function name in `tests/methodology/*.py` also enumerates a same-Phase propagation step on `architecture/shippability.md` rows referencing the superseded name. Deferred at slice-015 to stay within the ~0.5-day budget — the rule lives in prose for now.

## Context

The Critic agent at `agents/critique.md` carries the project's adversarial review prompt with 9 named dimensions. Dimension 9 ("Cross-cutting conformance") was introduced at slice-006 (ADR-005 / CCC-1 v1) with 5 sub-clauses. Slice-009 (ADR-008 / CCC-1 v1.1) refined sub-clause 2's body inline without changing the structural-invariant count. Slice-011 (ADR-010 / RSAD-1) appended a new 6th sub-clause via PMI-1 structural-invariant supersession discipline (`_lists_five_sub_clauses` → `_lists_six_sub_clauses`). Slice-013 (ADR-012 / EPGD-1) appended a new 7th sub-clause via the same PMI-1 structural-invariant supersession discipline applied at structural-invariant level (`_lists_six_sub_clauses` → `_lists_seven_sub_clauses`).

Across slices 13-14, an empirical pattern accumulated in the reflection record that is NOT covered by any of the existing 7 sub-clauses: **shippability-catalog consumer-reference propagation** — when a slice supersedes a test function name in `tests/methodology/*.py` (via PMI-1 versioned-gate supersession, PMI-1 structural-invariant supersession, or any other rename-driven supersession discipline) at /build-slice Phase 1, downstream consumers of that test function name in `architecture/shippability.md` (the catalog of critical-path commands run at /validate-slice pre-finish) carry stale references unless the SAME Phase explicitly propagates the rename across all consumer rows. This is a cross-Phase consumer-reference-propagation discipline distinct from RSAD-1's recursive-self-application (which operates at the meta level about a slice's own draft prose) AND distinct from EPGD-1's Edit-discipline-level entry-pin-vs-PMI-1-gate semantics conflation (which operates at Edit-tool `old_string`/`new_string` scoping at /build-slice Phase 1c).

**N=2 cumulative evidence across two distinct outcomes**:

1. **Slice-013 N=1 reactive-catch (Critic-MISSED at /critique AND /critique-review)** — at /build-slice Phase 1f, slice-013 superseded the Dim 9 structural-invariant test `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` per PMI-1 structural-invariant supersession discipline applied at the structural-invariant level (slice-011 N=1 precedent). Phase 5 (shippability.md updates) appended row 13 but did NOT scan existing rows 1-12 for stale references to the deleted `_lists_six_sub_clauses`. Rows 6 + 11 pytest commands still referenced the deleted test name; BOTH rows FAILED at /validate-slice Step 5.5 catalog run (pytest returned `no match in any of...`). Critic-MISSED at BOTH /critique AND /critique-review levels — neither first-Critic nor meta-Critic generalized the supersession-discipline → consumer-reference-propagation lesson to shippability.md (per slice-013 reflection.md). Fixed in-line at /validate-slice time by updating both rows' pytest commands to reference `_lists_seven_sub_clauses`. Slice-013 reflection codified the discipline as N=1 watch-listed with explicit promotion language ("promote at N=2 if recurs at slice-014+").

2. **Slice-014 N=2 proactive-application (no /critique miss)** — at /build-slice Phase 4 (before /validate-slice catalog run), slice-014 explicitly scanned `architecture/shippability.md` for stale references to the v0.28.0 PMI-1 versioned-gate function name `_at_0_28_0` (which slice-014's PMI-1 v1.1 refactor was about to retire). Identified row 13 pytest command referencing `_at_0_28_0`; updated row 13's pytest command in-line at Phase 4 (in the SAME phase as the PMI-1 v1.1 supersession Edit) to reference the new `_invariant` version-agnostic gate; ran shippability catalog at /validate-slice with 14/14 PASS no regressions. Slice-013's reactive lesson was applied PROACTIVELY at slice-014 Phase 4 — **N=2 promotion threshold MET** across two consecutive cross-cutting-tooling slices (slice-013 reactive + slice-014 proactive). The slice-014 reflection records this as N=2 stable with explicit promotion language ("Strongest slice-015 candidate: `refine-dim-9-with-shippability-catalog-propagation-sub-class` — N=2 promotion threshold MET; ~30 min skill scope; mirrors slice-009/010/011/013 Dim 9 sub-class refinement pattern").

The slice-013 + slice-014 reflections each named the explicit promotion threshold; N=2 is met as of slice-014 completion (2026-05-13). Slice-015's mission is to codify the discipline.

Without codification, the discipline remains tacit reflection-only knowledge. Future test-function-rename-driven supersession slices (every cross-cutting tooling slice that supersedes any test function name in `tests/methodology/*.py` — slice-016, slice-017, ... — including Dim 9 sub-clause refinements like potential 9th sub-clause for 3-layer-critic-stack or namespace-package-import-mode if those promote to N=2 in the future) would not benefit from the Critic agent's adversarial prompt explicitly verifying the slice's /design-slice Phase plan enumerates the supersession Phase AND the shippability.md propagation Phase as distinct, same-Phase steps. The Critic-MISSED at BOTH /critique AND /critique-review class observed at slice-013 N=1 would recur in future slices without the codified discipline.

## Options considered

### Option 1 — Append new 8th sub-clause to Dim 9 (CHOSEN)

Append ONE new sub-clause to `agents/critique.md` Dim 9 between the close of EPGD-1 sub-clause body (currently ~L178) and the `### Bonus: weak graph edges` H3 anchor (currently L180). Sub-clause title `Shippability-catalog consumer-reference propagation`. Body names BOTH sub-modes (reactive-catch + proactive-application) with N=2 cross-slice anchors (slice-013 + slice-014). Mirrors ADR-010 RSAD-1 + ADR-012 EPGD-1 append-new precedent.

Dim 9 structural-invariant grows 7 → 8 sub-clauses. Test `test_critique_dim_9_lists_seven_sub_clauses` REPLACED (not added alongside) by `test_critique_dim_9_lists_eight_sub_clauses` per PMI-1 structural-invariant supersession discipline applied at structural-invariant level (slice-011 N=1 + slice-013 N=2 → slice-015 N=3 stable precedent; no two structural-invariant tests coexist).

**Pros**:

- Sub-clause stays within Dim 9's existing structural home; readers continue to find shippability-catalog-propagation cross-cutting concerns in Dim 9's enumeration without searching across dimensions.
- Mirrors ADR-010 RSAD-1 + ADR-012 EPGD-1 append-new precedent at two prior levels: slice-011 grew 5 → 6 sub-clauses; slice-013 grew 6 → 7; slice-015 grows 7 → 8. Stylistic uniformity with the most recent similar slice. Same 5-prose-pin-tests scaffolding pattern (structural-invariant supersession + canonical-substring pin + location-pin + sub-mode pin + cross-slice anchors).
- N=2 evidence at slice-014 promotion-threshold-MET is consistent with the project's other Dim 9 sub-clause promotions (CCC-1 v1.1 sub-clause-2 design-md-tables paragraph was N=2 per slice-006 + slice-007; EPGD-1 was N=2 per slice-011 + slice-012; RSAD-1 was N=3 per slice-009 + slice-010 design-time + slice-010 build-time). N=2 is the minimum threshold per BC-1 promotion convention.
- Canonical body uses CONCRETE function-name substrings (`_lists_six_sub_clauses`, `_lists_seven_sub_clauses`, `_at_0_28_0`, `_invariant`) — necessary because the discipline's verifiability depends on recognizing test-function-rename patterns; abstract framing would lose retrieval traction. Slice-015 itself is the canonical reference instance for the discipline (its own Phase 1f supersedes `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` requiring Phase 5 propagation to rows 6 + 11 + 13).
- Reversibility: cheap. Revert path is single git diff revert + superseding methodology-changelog entry retracting SCPD-1.
- SCPD-1 self-application at slice-015's own build: the Phase 1f PMI-1 structural-invariant supersession + Phase 5 shippability.md propagation is the EXACT operation SCPD-1 governs. Slice-015 IS the canonical reference instance.

**Cons**:

- Existing test `test_critique_dim_9_lists_seven_sub_clauses` requires REPLACE (not extend) — small test-churn cost ratifying the structural-invariant supersession. Mitigated by treating this as canonical methodology pattern (slice-011 N=1 + slice-013 N=2 → slice-015 N=3 stable precedent).
- The Dim 9 structural-invariant is now 8-sub-clause; future Dim 9 sub-clause additions (e.g., the 3-layer-critic-stack-accountability-lineage at N=2 evidence; pytest-namespace-package-import-mode at N=2 evidence; case-sensitivity-canonical-literal-pin-discipline at N=2 evidence) would similarly grow the structural invariant. Mitigated by promotion-threshold discipline (N≥2 each, per the established precedent); section bounded by actual empirical sub-class count.

### Option 2 — Inline-refine existing EPGD-1 sub-clause body (REJECTED)

Refine existing Dim 9 sub-clause 7 ("Entry-pin-vs-PMI-1-gate semantics conflation" / EPGD-1) body with new sentences covering shippability-catalog consumer-reference propagation. Preserves the 7-count structural invariant.

**Pros**: no test-churn on `_lists_seven_sub_clauses`; pure inline body extension (slice-009 CCC-1 v1.1 precedent).

**Cons**: shippability-catalog consumer-reference propagation is a CROSS-PHASE PROPAGATION level concern (about Phase 1 supersession + Phase 5 propagation cross-Phase coordination at /build-slice) — distinct from EPGD-1's EDIT-DISCIPLINE level concern (about Edit-tool `old_string`/`new_string` scoping at /build-slice Phase 1c). Conflating them weakens both:

- EPGD-1's Edit-discipline scope becomes ambiguous (does it cover cross-Phase propagation? shippability.md catalog? OR just Edit-tool scoping within a single Phase?)
- SCPD-1's specific cross-Phase propagation focus gets buried inside EPGD-1's Edit-discipline body
- Future readers of the Critic prompt won't find SCPD-1 as a peer of the other cross-Phase-discipline-class sub-clauses (none currently exist; SCPD-1 starts the class)
- The Edit-discipline body in EPGD-1 already names sub-modes (build-time slip + design-time-pre-empted success) operating at Edit-tool scope. Adding a THIRD sub-mode at cross-Phase scope (Phase 1 supersession + Phase 5 propagation) would make EPGD-1's body 3-sub-mode across two distinct scopes, growing semantic ambiguity. Better: SCPD-1 is its own sub-clause with its own 2-sub-mode structure at cross-Phase scope.

Rejected: distinct disciplines deserve distinct sub-clauses; inline-conflation weakens both.

### Option 3 — Add new top-level dimension (REJECTED)

Introduce a "Dim 10 Cross-Phase coordination discipline" at the top level alongside the existing 9 dimensions.

**Pros**: maximally visible; shippability-catalog consumer-reference propagation gets its own dedicated dimension.

**Cons**:

- N=2 evidence for a new top-level DIMENSION is far below the threshold the project applies for promoting dimensions (Dim 9 itself accumulated N=10 sub-class hits across 5 distinct slices before the 2026-05-10 /critic-calibrate user-override promoted it). Two instances is sub-class-scale, not dimension-scale.
- Existing test `test_critique_lists_nine_dimensions` would need REPLACE → `lists_ten_dimensions`; multiple prose-pin sites referencing "9 dimensions" across `agents/critique.md` + `skills/critique/SKILL.md` would need updates. ~20+ surface sites. Magnitude scales to ADR-005-class (expensive with irreversible portion).
- Shippability-catalog consumer-reference propagation is intrinsically a SUB-class of cross-cutting-conformance (cross-cuts in-house catalog consumer references) — promoting to peer-dimension loses the semantic relationship.

Rejected: scale and semantics both argue for sub-clause not dimension.

## Decision

**Adopt Option 1** — append a new 8th sub-clause `Shippability-catalog consumer-reference propagation` to `agents/critique.md` Dim 9 between the existing `Entry-pin-vs-PMI-1-gate semantics conflation` sub-clause close and the `### Bonus: weak graph edges` H3 anchor. Sub-clause body documented under `## Sub-clause canonical body` in [[slice-015-refine-dim-9-with-shippability-catalog-propagation-sub-class/design.md]] (the same prose appended verbatim to `agents/critique.md`). Codify as new methodology rule **SCPD-1** in `methodology-changelog.md` v0.30.0 under `### Added` with explicit Limitations note (acknowledging /critique-time + /build-slice-time adversarial-prompt + Phase-plan-discipline semantics; no audit-enforced gate; v2 candidate `tools/scpd_1_audit.py` if drift surfaces). PMI-1 v1.1 atomic version bump 0.29.0 → 0.30.0 with NO versioned-gate supersession needed (PMI-1 v1.1 version-agnostic gate from slice-014 body unchanged through atomic bump). Replace existing structural-invariant test `_lists_seven_sub_clauses` with `_lists_eight_sub_clauses` per PMI-1 structural-invariant supersession discipline applied at the structural-invariant level — slice-015 ratchets this structural-invariant-supersession pattern to N=3 stable (slice-011 N=1 + slice-013 N=2 + slice-015 N=3).

The canonical body uses CONCRETE function-name substrings (`_lists_six_sub_clauses`, `_lists_seven_sub_clauses`, `_at_0_28_0`, `_invariant`) because the discipline's verifiability depends on recognizing test-function-rename patterns; abstract framing would lose retrieval traction. Rule-IDs `PMI-1` IS named explicitly in the body (matches existing Dim 9 sub-clause convention naming rules by ID; mirrors ADR-010 RSAD-1 + ADR-012 EPGD-1 sub-clause naming PMI-1); concrete row numbers (rows 6, 11, 13) ARE named in the slice-013 + slice-014 anchor descriptions because they provide retrievable empirical anchors. These substrings are NOT BC-1 positive anchors (BC-PROJ-1/2/GLOBAL-1's positive sets don't include row-number indices or test-function-rename suffixes); no BC-1 self-application firing expected at /build-slice Phase 4 per design.md Audit 3 prediction.

Slice-015's TRANSIENT artifacts (mission-brief.md + design.md + ADR-014) DO carry concrete anchors (`_lists_seven_sub_clauses`, `_lists_eight_sub_clauses`, slice-013/014 row numbers) for empirical evidence of the SCPD-1 discipline at slice-013 N=1 + slice-014 N=2 cross-slice anchors. These substrings are NOT BC-1 positive anchors; no BC-1 self-application firing expected.

## Consequences

**Immediate** (slice-015 ship):

- `agents/critique.md` Dim 9 section grows 7 → 8 sub-clauses; sub-clause body inserted between 7th-sub-clause-close and `### Bonus: weak graph edges` H3 anchor.
- `~/.claude/agents/critique.md` byte-equal post-forward-sync (CAD-1 invariant from slice-007).
- `methodology-changelog.md` v0.30.0 entry appended (in-repo + installed) with SCPD-1 rule reference + explicit Limitations note + N=2 cross-slice anchor citations (slice-013 + slice-014).
- `tests/methodology/test_critique_agent.py` gains 5 net new tests (5 added: `_shippability_catalog_propagation_sub_clause_present` + `_location_pinned` + `_names_both_sub_modes` + `_paragraph_cites_slice_013_and_014` + `_cites_at_least_two_cross_slice_anchors`; 1 superseded: `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`; 1 mini-CAD-1 row 3 regression-guard: `_in_repo_and_installed_critique_agent_are_content_equal` PASSING throughout).
- `tests/methodology/test_methodology_changelog.py` gains 2 new tests (1 entry-pin: `test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed` + 1 ADR-pin: `test_adr_014_exists_and_names_scpd_1_canonical_phrase`). ZERO supersession; ZERO entry-pin deletion risk; PMI-1 v1.1 version-agnostic gate body unchanged. ALL 7 prior entry-pin functions (v_0_22_0..v_0_29_0) persist untouched.
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.30.0. Second version bump under PMI-1 v1.1 (first was slice-014's 0.28.0→0.29.0); empirical retirement-proof of PMI-1 v1.1 N=1 → N=2 stable.
- `architecture/shippability.md` row 15 added + rows 6 + 11 + 13 propagated (`_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`) via SCPD-1 self-application at Phase 5.

**Downstream** (slice-016 and beyond):

- Every Critic /critique invocation reads the new 8th sub-clause when applying Dim 9 to the slice under review. For ANY slice that supersedes any test function name in `tests/methodology/*.py` (PMI-1 versioned-gate, PMI-1 structural-invariant test, or any other rename-driven supersession), the Critic is now explicitly directed to: (1) require the design.md phase plan to enumerate the supersession Phase AND the shippability.md propagation Phase as distinct, named steps; (2) require the propagation Phase to execute in the SAME Phase block as the supersession Edit (not deferred to /validate-slice); (3) require a pre-Phase empirical scan of `architecture/shippability.md` for ALL consumer references to the test name being superseded; (4) flag absent or aspirational propagation plans as Major findings.
- Cross-cutting Dim 9 catch rate projected to improve at slice-016+: slice-013 reflection records the trajectory at 87.5% (7 of 8 sub-class hits caught at /critique + /critique-review combined). The 1 build-time miss at slice-013 (shippability-catalog-propagation) was the exact phenomenon SCPD-1 codifies. Future test-function-rename-driven supersession slices with /design-slice Phase plans that fail to enumerate same-Phase propagation should see the build-time row-stale-reference risk caught at /critique time rather than at /validate-slice Step 5.5 catalog regression check.
- `/critic-calibrate` next-run trigger: per Meta-Critic 2026-05-13 recommendation, calibration is held until slice-021+ OR earlier if any watch-list N=1 sub-class hits N=3 distinct-slice recurrence. SCPD-1 codification at slice-015 closes the N=2 promotion threshold; the remaining watch-list (3-layer-critic-stack-accountability-lineage + pytest-namespace-package-import-mode) stays at N=1 awaiting slice-016+ recurrence.
- The methodology rule-ID -D-suffix convention is N=3 stable at slice-015 completion (RSAD-1 v0.26.0 + EPGD-1 v0.28.0 + SCPD-1 v0.30.0). The B5 calibration-trail discipline (slice-010 introduction → slice-011 -D-suffix extension → slice-013 -D-suffix N=2 stable confirmation → slice-015 -D-suffix N=3 stable confirmation) ratchets to N=4 evidence at the rule-ID convention level. Future prose-heuristic Discipline rules SHOULD adopt -D suffix; this is now a canonical project convention.
- Recursive-self-application N=6 → N=7 cumulative post-RSAD-1 codification (slice-015 itself is the 7th instance — see design.md "Recursive self-application N=6 → N=7 cumulative" section).
- PMI-1 v1.1 version-agnostic gate empirical retirement-proof N=1 → N=2 stable (slice-014 first bump + slice-015 second bump under v1.1; ZERO test code modification on gate body across both).

**Cumulative-Critic-influence note**: SCPD-1 is applied prospectively — slice-016 onward. Past slices (slice-001..015) retain their original /critique outputs (the discipline existed implicitly via slice-013 + slice-014 reflection records but was not codified in the Critic agent prompt at /critique time). The methodology-changelog entry documents this as the new behavior at slice-016+; no retroactive re-evaluation of past slices' /critique outputs.

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 Critic M4 + slice-010 Critic m3 + slice-011 ADR-010 + slice-012 ADR-011 + slice-013 ADR-012 + slice-014 ADR-013 precedent).

**Magnitude estimate** (~13-15 sites total):

1. `agents/critique.md` — sub-clause body append at 7th-sub-clause-close ↔ `### Bonus: weak graph edges` H3 boundary (1 site, ~15 lines of prose)
2. `~/.claude/agents/critique.md` — forward-sync mirror (1 site)
3. `methodology-changelog.md` — v0.30.0 entry (1 site, ~30 lines)
4. `~/.claude/methodology-changelog.md` — forward-sync mirror (1 site)
5. `VERSION` — bump 0.29.0 → 0.30.0 (1 site)
6. `~/.claude/ai-sdlc-VERSION` — forward-sync mirror (1 site)
7. `plugin.yaml.version` — bump 0.29.0 → 0.30.0 (1 site)
8. `tests/methodology/test_critique_agent.py` — replace `_lists_seven_sub_clauses` with `_lists_eight_sub_clauses` + add 5 SCPD-1-specific tests (5 net additions; 1 supersession in same commit)
9. `tests/methodology/test_methodology_changelog.py` — add `test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed` (Phase 1b INSERT under NEW SECTION header) + add `test_adr_014_exists_and_names_scpd_1_canonical_phrase` — 2 sub-edits in 1 file under structurally-separated SECTION headers; ZERO supersession; ZERO entry-pin deletion risk
10. `architecture/shippability.md` — add row 15 + update row 14 header + propagate rows 6 + 11 + 13 `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` (5 sub-edits in 1 file; SCPD-1 self-application at Phase 5)
11. `architecture/decisions/ADR-014-*.md` — this file itself
12. `architecture/slices/slice-015-.../` — mission-brief.md + design.md + milestone.md + (eventually) critique.md + critique-review.md + build-log.md + validation.md + reflection.md (slice's own artifact folder)

**Comparison to prior ADRs**:

- ADR-005 (CCC-1 v1, slice-006) — **expensive** with irreversible portion. ~30+ sites.
- ADR-006 (CAD-1, slice-007) — **cheap** with 5 enumerated irreversibles. ~5-10 sites.
- ADR-007 (BC-1 v1.2, slice-008) — **cheap**. ~10-15 sites.
- ADR-008 (CCC-1 v1.1 inline refinement, slice-009) — **cheap** with magnitude justification. ~5 sites.
- ADR-009 (MCT-1, slice-010) — **cheap** with magnitude justification. ~11-13 sites.
- ADR-010 (RSAD-1, slice-011) — **cheap** with magnitude justification. ~12 sites.
- ADR-011 (BC-PROJ-2 negative-anchor migration, slice-012) — **cheap** (~10 sites).
- ADR-012 (EPGD-1, slice-013) — **cheap** with magnitude justification. ~12 sites.
- ADR-013 (PMI-1 v1.1 refactor, slice-014) — **cheap** with magnitude-of-revert justification.
- **ADR-014 (this) — cheap with magnitude justification**. ~13-15 sites; same magnitude class as **ADR-010 (RSAD-1, ~12 sites)** + **ADR-012 (EPGD-1, ~12 sites)** — the closest structural-analog precedents (all three append-new sub-clauses to Dim 9 with PMI-1 structural-invariant supersession + 5-prose-pin-tests scaffolding + bidirectional changelog entry). The +1-3 site delta vs ADR-012 reflects the additional Phase 5 shippability.md row-propagation surgery (rows 6 + 11 + 13 + new row 15 = 4 sub-edits vs ADR-012's 2 sub-edits). Still cheap on reversibility because each site is small and the revert path is git-diff-revert + superseding changelog entry.

**Revert path**:

1. Git diff revert of slice-015's commits (single-slice revert is clean since no in-flight cross-slice dependencies exist).
2. Append a superseding methodology-changelog entry retracting SCPD-1 (e.g., `## v0.31.0 — <date>` with `### Retired` section naming SCPD-1 + rationale for retirement). Per PMI-1 + changelog inclusion heuristic.
3. Remove the 5 new test functions + reinstate `_lists_seven_sub_clauses` (delete `_lists_eight_sub_clauses`). Reinstate `_at_0_29_0`-style PMI-1 versioned-gate function or keep PMI-1 v1.1 version-agnostic gate (depends on whether ADR-013 is also reverted — independently revertable).
4. Remove the v_0_30_0 SCPD-1 entry-pin function + the ADR-014 pin function from `tests/methodology/test_methodology_changelog.py` (Phase 1b reversal).
5. Revert `architecture/shippability.md`: drop row 15 + un-update row 14 header + propagate rows 6 + 11 + 13 `_lists_eight_sub_clauses` → `_lists_seven_sub_clauses`.
6. Forward-sync the reverted `agents/critique.md` + `methodology-changelog.md` to `~/.claude/`. Confirm byte-equality.

**Irreversible portion** (minor, append-only):

- The `methodology-changelog.md` v0.30.0 entry itself, once committed, becomes part of the append-only changelog history. A retraction is a SUPERSEDING entry, NOT a deletion.
- Cumulative slice-016+ Critic invocations that ran (and the artifacts they produced) under SCPD-1's shippability-catalog-propagation discipline are part of the project's empirical record.
- The SCPD-1 -D-suffix rule-ID naming convention's N=3-stable confirmation (slice-015 confirms RSAD-1's N=1 + EPGD-1's N=2 -D-suffix establishment). A retraction of SCPD-1 itself doesn't retract the N=1 + N=2 stable; future prose-heuristic rules may still use -D suffix.
- The PMI-1-structural-invariant-supersession-at-Dim-9-sub-clause-count N=3 ratchet (slice-011 N=1 → slice-013 N=2 → slice-015 N=3 pending empirical validation at /reflect). A retraction of SCPD-1 reverts the structural-invariant count to 7 but doesn't un-establish the supersession pattern as canonical methodology practice.

Both irreversible portions are documentation-record-class (not functional-behavior-class).

**Conclusion**: Reversibility is **cheap**. Magnitude is ~13-15 sites (same class as ADR-010 / ADR-012). Revert path is well-trodden. Adopt Option 1.
