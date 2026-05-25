---
id: ADR-012
title: Promote entry-pin-vs-PMI-1-gate-discipline to agents/critique.md Dim 9 7th sub-clause via append-new (EPGD-1)
date: 2026-05-13
slice: slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-012: Promote entry-pin-vs-PMI-1-gate-discipline to agents/critique.md Dim 9 7th sub-clause (EPGD-1)

**Note on rule-ID naming** (per slice-010 Critic B5 calibration-trail convention + slice-011 RSAD-1 -D-suffix extension; N=2 stable at slice-012 reflection): the rule is named **EPGD-1 "Entry-Pin-Gate-Discipline"** with -D suffix at end of abbreviation. The -D signals prose-heuristic / discipline semantics applied at /critique-time AND /build-slice-time, distinct from the audit-enforced gate semantics of sibling rules (BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1 — each has a corresponding `tools/*_audit.py` enforcing the rule programmatically; EPGD-1 does not — the rule lives in `agents/critique.md` Dim 9 sub-clause body prose only, applied by the Critic agent reading the sub-clause at /critique invocation time AND by the Builder reading the design.md Phase 1c plan at /build-slice). The -D convention extends slice-011's RSAD-1 -D-suffix establishment to a second prose-heuristic Discipline at N=2 stable. The methodology rule-ID naming convention now encompasses two prose-heuristic letter-conventions stably:

- **-T-** infix/suffix (MCT-1 v0.25.0): /slice-time mandatory-Critic trigger heuristic
- **-D** suffix (RSAD-1 v0.26.0 + EPGD-1 v0.28.0): /critique-time + /build-slice-time discipline heuristic; N=2 stable post-slice-013

v2 candidate at slice-N+ if drift surfaces: build `tools/epgd_1_audit.py` walking `architecture/slices/*/design.md` Phase plans and asserting the Phase 1c PMI-1 supersession Edit's `old_string` is narrow-scoped to gate function body + dedicated SECTION header only. Deferred at slice-013 to stay within the ~0.5-day budget — the rule lives in prose for now.

## Context

The Critic agent at `agents/critique.md` carries the project's adversarial review prompt with 9 named dimensions. Dimension 9 ("Cross-cutting conformance") was introduced at slice-006 (ADR-005 / CCC-1 v1) with 5 sub-clauses. Slice-009 (ADR-008 / CCC-1 v1.1) refined sub-clause 2's body inline without changing the structural-invariant count. Slice-011 (ADR-010 / RSAD-1) appended a new 6th sub-clause via PMI-1 structural-invariant supersession discipline (`_lists_five_sub_clauses` → `_lists_six_sub_clauses`).

Across slices 11-12, an empirical pattern accumulated in the reflection record that is NOT covered by any of the existing 6 sub-clauses: **entry-pin-vs-PMI-1-gate semantics conflation** — when superseding a PMI-1 versioned-gate test via the Edit tool's `old_string`/`new_string` parameters, scoping the Edit block to span an entry-pin function definition along with the PMI-1 gate function silently deletes the prior version's entry-pin function. This is an Edit-tool-scoping discipline distinct from RSAD-1's recursive-self-application (which operates at the meta level about a slice's own draft prose) and distinct from the Dim 9 sub-clauses 1-5 (which are dimension-level cross-references or N=1 standalone runtime/language sub-classes).

**N=2 cumulative evidence across two distinct outcomes**:

1. **Slice-011 N=1 build-time slip (Critic-MISSED at /critique)** — at /build-slice Phase 1c, slice-011 superseded the v0.25.0 MCT-1 PMI-1 versioned-gate test via Edit. The `old_string` spanned BOTH the v0.25.0 MCT-1 entry-pin function (`test_v_0_25_0_mct_1_entry_present_in_repo_and_installed`) AND the PMI-1 versioned-gate function (`test_plugin_yaml_version_matches_version_file_at_0_25_0`) via their shared SECTION header (drafted visually from the file's then-current contiguous block layout). Replacement deleted v0.25.0 entry-pin silently — Critic-MISSED at /critique (an Edit-tool-scoping discipline is not a design semantic the pre-EPGD-1 Critic prompt covered; the slice-011 reflection notes this as Critic blind-spot). Caught at /validate-slice Step 5.5 by shippability catalog row 10 fail (the row's pytest command listed the deleted test name; pytest returned `no match in any of...`); fixed in-line at validate-time by re-adding the v0.25.0 entry-pin function between v0.24.0 and v0.26.0 entry-pins. Full methodology suite re-ran clean post-fix (362/362 PASS; +1 from re-added test). Slice-011 reflection codified the discipline as N=1 watch-listed with explicit promotion language ("promote to Dim 9 sub-class refinement at N=2 if recurs at slice-012+").

2. **Slice-012 N=2 design-time-pre-empted success (Critic-CAUGHT M1 at /critique)** — at /design-slice, slice-012 explicitly planned Phase 1b INSERT for the new v0.27.0 BC-PROJ-2 entry-pin function under a NEW dedicated SECTION header (`# --- Slice-012 / BC-PROJ-2 entry pinning ---`), placed structurally separate from the PMI-1 gate's dedicated SECTION header (`# --- PMI-1 cleanliness gate at v0.26.0 ---`). Slice-012 Critic M1 ACCEPTED-FIXED the structural-separation discipline at /critique with explicit ACs requiring: (a) the new entry-pin function INSERT under a NEW dedicated SECTION header (Phase 1b) BEFORE (b) the PMI-1 gate Edit narrow-scoped to the gate function body + its dedicated SECTION header ONLY (Phase 1c) AFTER (c) a pre-Edit empirical structural-separation audit at /design-slice (Audit 6) confirming the two SECTION headers don't share intervening prose. Post-build empirical confirmation: all v0.22.0..v0.26.0 entry-pin functions PASS unchanged; only the PMI-1 gate function body was modified. The slice-012 reflection notes this as N=2 promotion-threshold-MET with explicit promotion language ("promote at slice-013+ via /critic-calibrate or dedicated Dim 9 sub-class refinement slice").

The slice-011 + slice-012 reflections each named the explicit promotion threshold; N=2 is met as of slice-012 completion (2026-05-13). Slice-013's mission is to codify the discipline.

Without codification, the discipline remains tacit reflection-only knowledge. Future PMI-1 versioned-gate supersession slices (every cross-cutting tooling slice — slice-014, slice-015, ... — under the existing PMI-1 supersession-per-slice convention) would not benefit from the Critic agent's adversarial prompt explicitly verifying the slice's /design-slice Phase plan separates entry-pin INSERT from PMI-1 gate supersession Edit, nor from the explicit structural-separation audit requirement. The Critic-MISSED at /critique class observed at slice-011 N=1 would recur in future slices without the codified discipline.

## Options considered

### Option 1 — Append new 7th sub-clause to Dim 9 (CHOSEN)

Append ONE new sub-clause to `agents/critique.md` Dim 9 at L173 between L172 (close of RSAD-1 sub-clause body — title `Recursive self-application discipline` lives at L168) and L174 (`### Bonus: weak graph edges` H3 anchor). Sub-clause title `Entry-pin-vs-PMI-1-gate semantics conflation`. Body names BOTH sub-modes (build-time slip + design-time-pre-empted success) with N=2 cross-slice anchors (slice-011 + slice-012). Mirrors ADR-010 RSAD-1 append-new precedent.

Dim 9 structural-invariant grows 6 → 7 sub-clauses. Test `test_critique_dim_9_lists_six_sub_clauses` REPLACED (not added alongside) by `test_critique_dim_9_lists_seven_sub_clauses` per PMI-1 versioned-gate supersession discipline applied at the structural-invariant level (slice-011 N=1 precedent; slice-013 N=2 ratchets pending empirical validation at /build-slice + /reflect — if Phase 1f structural-invariant supersession Edit cleanly succeeds AND `_lists_seven_sub_clauses` PASSES post-build, N=2 promotes to stable in slice-013 reflection.md).

**Pros**:

- Sub-clause stays within Dim 9's existing structural home; readers continue to find entry-pin-vs-PMI-1-gate cross-cutting concerns in Dim 9's enumeration without searching across dimensions.
- Mirrors ADR-010 RSAD-1 append-new precedent at one level: slice-011 grew 5 → 6 sub-clauses; slice-013 grows 6 → 7. Stylistic uniformity with the most recent similar slice. Same 5-prose-pin-tests scaffolding pattern (structural-invariant supersession + canonical-substring pin + location-pin + sub-mode pin + cross-slice anchors).
- N=2 evidence at slice-012 promotion-threshold-MET is consistent with the project's other Dim 9 sub-clause promotions (CCC-1 v1.1 sub-clause-2 design-md-tables paragraph was N=2 per slice-006 + slice-007; RSAD-1 was N=3 per slice-009 + slice-010 design-time + slice-010 build-time). N=2 is the minimum threshold per BC-1 promotion convention.
- Canonical body uses CONCRETE SECTION-header substring examples (`# --- Slice-NNN / <rule> entry pinning ---`) but ABSTRACT function-name framing (`entry-pin function`, `PMI-1 versioned-gate function`) — the canonical Critic-prompt artifact stays usable by future Critic invocations on any rule's entry-pin supersession (not tied to BC-PROJ-2 or RSAD-1 specifically). Slice-013 itself is the canonical reference instance for the discipline.
- Reversibility: cheap. Revert path is single git diff revert + superseding methodology-changelog entry retracting EPGD-1.
- EPGD-1 self-application at slice-013's own build: the Phase 1c PMI-1 supersession Edit (`_at_0_27_0` → `_at_0_28_0`) is the EXACT operation EPGD-1 governs. Slice-013 IS the canonical reference instance.

**Cons**:

- Existing test `test_critique_dim_9_lists_six_sub_clauses` requires REPLACE (not extend) — small test-churn cost ratifying the structural-invariant supersession. Mitigated by treating this as canonical methodology pattern (slice-011 N=1 precedent → slice-013 N=2 ratchets pending empirical validation; if N=2 confirms post-build, promotes to N≥3 stable if another structural-invariant supersession surfaces at slice-014+).
- The Dim 9 structural-invariant is now 7-sub-clause; future Dim 9 sub-clause additions (e.g., the case-sensitivity-canonical-literal-pin-discipline at N=2 evidence; `.find()`-collision discipline at N=2 evidence; runtime-environment N=1 → N=2 pending) would similarly grow the structural invariant. Mitigated by promotion-threshold discipline (N≥2 each, per the established precedent); section bounded by actual empirical sub-class count.

### Option 2 — Inline-refine existing RSAD-1 sub-clause body (REJECTED)

Refine existing Dim 9 sub-clause 6 ("Recursive self-application discipline" / RSAD-1) body with new sentences covering entry-pin-vs-PMI-1-gate-semantics-conflation. Preserves the 6-count structural invariant.

**Pros**: no test-churn on `_lists_six_sub_clauses`; pure inline body extension (slice-009 CCC-1 v1.1 precedent).

**Cons**: entry-pin-vs-PMI-1-gate-conflation is an EDIT-DISCIPLINE level concern (about Edit-tool `old_string`/`new_string` scoping at /build-slice Phase 1c) — distinct from RSAD-1's META-LEVEL "stress-test slice's own draft prose against the very discipline being encoded" concern. Conflating them weakens both:

- RSAD-1's meta-level scope becomes ambiguous (does it cover Edit-discipline? structural-pre-Edit audits? OR just rule-class violations in the slice's own draft prose?)
- EPGD-1's specific Edit-discipline focus gets buried inside RSAD-1's meta-level body
- Future readers of the Critic prompt won't find EPGD-1 as a peer of the other Edit-discipline-class sub-clauses (none currently exist; EPGD-1 starts the class)
- The recursive-self-application body in RSAD-1 already names sub-modes (design-time + build-time-via-/critique-fix-prose). Adding a THIRD sub-mode (Edit-scoping at /build-slice Phase 1c) would make RSAD-1's body 3-sub-mode, growing semantic ambiguity. Better: EPGD-1 is its own sub-clause with its own 2-sub-mode structure.

Rejected: distinct disciplines deserve distinct sub-clauses; inline-conflation weakens both.

### Option 3 — Add new top-level dimension (REJECTED)

Introduce a "Dim 10 Methodology Edit-discipline" at the top level alongside the existing 9 dimensions.

**Pros**: maximally visible; entry-pin-vs-PMI-1-gate-discipline gets its own dedicated dimension.

**Cons**:

- N=2 evidence for a new top-level DIMENSION is far below the threshold the project applies for promoting dimensions (Dim 9 itself accumulated N=10 sub-class hits across 5 distinct slices before the 2026-05-10 /critic-calibrate user-override promoted it; even then it was Meta-Critic-declined initially). Two instances is sub-class-scale, not dimension-scale.
- Existing test `test_critique_lists_nine_dimensions` would need REPLACE → `lists_ten_dimensions`; multiple prose-pin sites referencing "9 dimensions" across `agents/critique.md` + `skills/critique/SKILL.md` would need updates. ~20+ surface sites. Magnitude scales to ADR-005-class (expensive with irreversible portion).
- Entry-pin-vs-PMI-1-gate-conflation is intrinsically a SUB-class of cross-cutting-conformance (cross-cuts in-house methodology audits' Edit-discipline) — promoting to peer-dimension loses the semantic relationship.

Rejected: scale and semantics both argue for sub-clause not dimension.

## Decision

**Adopt Option 1** — append a new 7th sub-clause `Entry-pin-vs-PMI-1-gate semantics conflation` to `agents/critique.md` Dim 9 between the existing `Recursive self-application discipline` sub-clause close (L172) and the `### Bonus: weak graph edges` H3 anchor (L174). Sub-clause body documented under `## Sub-clause canonical body` in [[slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class/design.md]] (the same prose appended verbatim to `agents/critique.md`). Codify as new methodology rule **EPGD-1** in `methodology-changelog.md` v0.28.0 under `### Added` with explicit Limitations note (acknowledging /critique-time + /build-slice-time adversarial-prompt + Phase-plan-discipline semantics; no audit-enforced gate; v2 candidate `tools/epgd_1_audit.py` if drift surfaces). PMI-1 atomic version bump 0.27.0 → 0.28.0 with versioned-gate supersession (slice-012's `_at_0_27_0` → slice-013's `_at_0_28_0`; N=6 supersession event post-completion). Replace existing structural-invariant test `_lists_six_sub_clauses` with `_lists_seven_sub_clauses` per PMI-1 versioned-gate supersession discipline applied at the structural-invariant level — slice-013 ratchets this structural-invariant-supersession pattern to N=2 stable (slice-011 N=1 + slice-013 N=2).

The canonical body uses CONCRETE SECTION-header substring examples (the exact SECTION-header convention `# --- Slice-NNN / <rule> entry pinning ---`) because the discipline's verifiability depends on the SECTION-header convention being recognizable; abstract framing would lose retrieval traction. Rule-IDs `BC-PROJ-1`, `BC-PROJ-2`, `BC-GLOBAL-1`, `MCT-1`, `RSAD-1`, `BC-1`, `PMI-1` ARE named explicitly in the body (matches existing Dim 9 sub-clause convention naming rules by ID; mirrors ADR-010 RSAD-1 sub-clause naming `BC-PROJ-2`); only the function NAMES stay abstract (`entry-pin function`, `PMI-1 versioned-gate function`) — this lets the sub-clause generalize across all rule families' entry-pin supersession.

Slice-013's TRANSIENT artifacts (mission-brief.md + design.md + ADR-012) DO carry concrete version-number substrings (`v0.22.0..v0.27.0` entry-pin function names + `_at_0_27_0` PMI-1 gate function name) for empirical evidence of the EPGD-1 discipline at slice-011 N=1 + slice-012 N=2 cross-slice anchors. These substrings are NOT BC-1 positive anchors (BC-PROJ-1/2/GLOBAL-1's positive sets don't include function-name version-suffixes); no BC-1 self-application firing expected at /build-slice Phase 4 per design.md Audit 6 prediction.

## Consequences

**Immediate** (slice-013 ship):

- `agents/critique.md` Dim 9 section grows 6 → 7 sub-clauses; sub-clause body inserted at L173.
- `~/.claude/agents/critique.md` byte-equal post-forward-sync (CAD-1 invariant from slice-007).
- `methodology-changelog.md` v0.28.0 entry appended (in-repo + installed) with EPGD-1 rule reference + explicit Limitations note + N=2 cross-slice anchor citations (slice-011 + slice-012).
- `tests/methodology/test_critique_agent.py` gains 3 net new tests (3 added: `_entry_pin_vs_pmi_1_gate_sub_clause_present` + `_location_pinned` + `_paragraph_cites_slice_011_and_012`; 1 superseded: `_lists_six_sub_clauses` → `_lists_seven_sub_clauses`; 1 mini-CAD-1 row 3 regression-guard: `_recursive_self_application_sub_clause_present` PASSING throughout).
- `tests/methodology/test_methodology_changelog.py` gains 1 bidirectional changelog-pin test (`test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed`) + 1 PMI-1 versioned-gate test (`_at_0_28_0` supersedes slice-012's `_at_0_27_0`) via NARROW-SCOPE Edit per EPGD-1 self-application. ALL 6 prior entry-pin functions (v_0_22_0..v_0_27_0) persist untouched.
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.28.0.
- `architecture/shippability.md` row 13 added; row 12 header updated.

**Downstream** (slice-014 and beyond):

- Every Critic /critique invocation reads the new 7th sub-clause when applying Dim 9 to the slice under review. For ANY slice that supersedes a PMI-1 versioned-gate (every cross-cutting tooling slice under current convention), the Critic is now explicitly directed to: (1) verify Phase 1b INSERT + Phase 1c narrow-scope Edit structural separation; (2) verify Phase 1c Edit `old_string` doesn't span entry-pin function definitions; (3) require pre-Edit empirical structural-separation audit at /design-slice.
- Cross-cutting Dim 9 catch rate projected to improve at slice-014+: slice-011 reflection records the trajectory at 80% (4 of 5 sub-class hits caught at /critique), slice-012 at 80-100% (4 of 4 design-time + 4 of 5 including M2). The 1 build-time miss at slice-011 (entry-pin-vs-PMI-1-gate-conflation) was the exact phenomenon EPGD-1 codifies. Future PMI-1 supersession slices with /design-slice phase plans that fail to separate Phase 1b INSERT from Phase 1c Edit should see the build-time entry-pin-deletion risk caught at /critique time rather than at /validate-slice Step 5.5 shippability catalog regression check.
- `/critic-calibrate` next-run effectiveness check (per slice-009/010/011/012 reflections at slice-014+ boundary now): the cumulative cross-cutting miss count through slice-012 is 10 misses (5× the ≤2 target across slices 6-15; 3 slices remaining in window after slice-013 ships). EPGD-1 codification is one calibration-response candidate (refining the Critic prompt with the new sub-clause); the other is recalibrating the quantitative target downward. /critic-calibrate at slice-014 (slice-012 reflection's strongest displaced #1 candidate; deferred from slice-013 by user choice to codify EPGD-1 first) will assess.
- The methodology rule-ID -D-suffix convention is N=2 stable at slice-013 completion (RSAD-1 v0.26.0 + EPGD-1 v0.28.0). The B5 calibration-trail discipline (slice-010 introduction → slice-011 -D-suffix extension → slice-013 -D-suffix N=2 stable confirmation) ratchets to N=3 evidence at the rule-ID convention level. Future prose-heuristic Discipline rules SHOULD adopt -D suffix; this is now a canonical project convention.
- Recursive-self-application N=5 cumulative post-RSAD-1 codification (slice-013 itself is the 5th instance — see design.md "Recursive self-application N=5 cumulative" section).

**Cumulative-Critic-influence note**: EPGD-1 is applied prospectively — slice-014 onward. Past slices (slice-001..013) retain their original /critique outputs (the discipline existed implicitly via slice-011 + slice-012 reflection records but was not codified in the Critic agent prompt at /critique time). The methodology-changelog entry documents this as the new behavior at slice-014+; no retroactive re-evaluation of past slices' /critique outputs.

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 Critic M4 + slice-010 Critic m3 + slice-011 ADR-010 + slice-012 ADR-011 precedent).

**Magnitude estimate** (~12 sites total):

1. `agents/critique.md` — sub-clause body append at L173 (1 site, ~15 lines of prose)
2. `~/.claude/agents/critique.md` — forward-sync mirror (1 site)
3. `methodology-changelog.md` — v0.28.0 entry (1 site, ~30 lines)
4. `~/.claude/methodology-changelog.md` — forward-sync mirror (1 site)
5. `VERSION` — bump 0.27.0 → 0.28.0 (1 site)
6. `~/.claude/ai-sdlc-VERSION` — forward-sync mirror (1 site)
7. `plugin.yaml.version` — bump 0.27.0 → 0.28.0 (1 site)
8. `tests/methodology/test_critique_agent.py` — replace `_lists_six_sub_clauses` with `_lists_seven_sub_clauses` + add 3 EPGD-1-specific tests (3 net additions; 1 supersession in same commit)
9. `tests/methodology/test_methodology_changelog.py` — add `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` (Phase 1b INSERT under NEW SECTION header) + replace `_at_0_27_0` with `_at_0_28_0` (Phase 1c narrow-scope Edit per EPGD-1 self-application) — 2 sub-edits in 1 file under structurally-separated SECTION headers
10. `architecture/shippability.md` — add row 13 + update row 12 header (2 sub-edits in 1 file)
11. `architecture/decisions/ADR-012-*.md` — this file itself
12. `architecture/slices/slice-013-.../` — mission-brief.md + design.md + milestone.md + (eventually) critique.md + critique-review.md + build-log.md + validation.md + reflection.md (slice's own artifact folder)

**Comparison to prior ADRs**:

- ADR-005 (CCC-1 v1, slice-006) — **expensive** with irreversible portion. ~30+ sites.
- ADR-006 (CAD-1, slice-007) — **cheap** with 5 enumerated irreversibles. ~5-10 sites.
- ADR-007 (BC-1 v1.2, slice-008) — **cheap**. ~10-15 sites.
- ADR-008 (CCC-1 v1.1 inline refinement, slice-009) — **cheap** with magnitude justification. ~5 sites.
- ADR-009 (MCT-1, slice-010) — **cheap** with magnitude justification. ~11-13 sites.
- ADR-010 (RSAD-1, slice-011) — **cheap** with magnitude justification. ~12 sites.
- ADR-011 (BC-PROJ-2 negative-anchor migration, slice-012) — **cheap** (~10 sites).
- **ADR-012 (this) — cheap with magnitude justification**. ~12 sites; same magnitude class as **ADR-010 (RSAD-1, ~12 sites)** — the closest structural-analog precedent (both append-new sub-clauses to Dim 9 with PMI-1 structural-invariant supersession + 5-prose-pin-tests scaffolding + bidirectional changelog entry). Still cheap on reversibility because each site is small and the revert path is git-diff-revert + superseding changelog entry.

**Revert path**:

1. Git diff revert of slice-013's commits (single-slice revert is clean since no in-flight cross-slice dependencies exist).
2. Append a superseding methodology-changelog entry retracting EPGD-1 (e.g., `## v0.29.0 — <date>` with `### Retired` section naming EPGD-1 + rationale for retirement). Per PMI-1 + changelog inclusion heuristic.
3. Remove the 3 new test functions + reinstate `_lists_six_sub_clauses` (delete `_lists_seven_sub_clauses`). Reinstate `_at_0_27_0` PMI-1 versioned-gate (or supersede to whatever VERSION ends up at).
4. Remove the v_0_28_0 EPGD-1 entry-pin function from `tests/methodology/test_methodology_changelog.py` (Phase 1b reversal).
5. Forward-sync the reverted `agents/critique.md` + `methodology-changelog.md` to `~/.claude/`. Confirm byte-equality.

**Irreversible portion** (minor, append-only):

- The `methodology-changelog.md` v0.28.0 entry itself, once committed, becomes part of the append-only changelog history. A retraction is a SUPERSEDING entry, NOT a deletion.
- Cumulative slice-014+ Critic invocations that ran (and the artifacts they produced) under EPGD-1's entry-pin-vs-PMI-1-gate discipline are part of the project's empirical record.
- The EPGD-1 -D-suffix rule-ID naming convention's N=2-stable confirmation (slice-013 confirms RSAD-1's N=1 -D-suffix establishment). A retraction of EPGD-1 itself doesn't retract the N=1 stable; future prose-heuristic rules may still use -D suffix.
- The PMI-1-structural-invariant-supersession-at-Dim-9-sub-clause-count N=2 ratchet (slice-011 N=1 → slice-013 N=2 pending empirical validation at /reflect). A retraction of EPGD-1 reverts the structural-invariant count to 6 but doesn't un-establish the supersession pattern as canonical methodology practice.

Both irreversible portions are documentation-record-class (not functional-behavior-class).

**Conclusion**: Reversibility is **cheap**. Magnitude is ~12 sites (same class as ADR-010). Revert path is well-trodden. Adopt Option 1.
