# Design: Slice 011 promote-recursive-self-application-discipline-to-critique-skill-prose

**Date**: 2026-05-13
**Mode**: Standard

## What's new

- **One new 6th sub-clause body** appended to `agents/critique.md` Dim 9 ("Cross-cutting conformance"), inserted at L167 between the existing L166 `Language-version conformance` sub-clause and the existing L168 `### Bonus: weak graph edges` H3 anchor. Sub-clause title `Recursive self-application discipline` (capitalized R bullet-title form mirroring existing sub-clause titles). Body names BOTH sub-modes (design-time + build-time-via-/critique-fix-prose) with N=3 cross-slice anchors (slice-009 M2 + slice-010 design-time stress-test catches B1/M1/B5 + slice-010 build-time DEVIATION-3). Canonical body documented under [Sub-clause canonical body](#sub-clause-canonical-body-to-insert-in-agentscritiquemd-l167) below.
- **One new methodology rule** **RSAD-1** ("Recursive Self-Application Discipline") in `methodology-changelog.md` v0.26.0 — the -D suffix signals discipline / prose-heuristic semantics distinct from audit-enforced gate semantics (extends the B5 calibration-trail convention slice-010 introduced for MCT-1's -T- suffix). Bidirectional in-repo + installed pin per slice-008/009/010 N-substring + N-surface schema-pin discipline. Limitations note explicitly acknowledging RSAD-1 is /critique-time adversarial-prompt heuristic prose only, NOT an audit-enforced gate.
- **5 new prose-pin tests** in `tests/methodology/test_critique_agent.py`:
  - `test_critique_dim_9_lists_six_sub_clauses` REPLACES `test_critique_dim_9_lists_five_sub_clauses` (structural-invariant supersession; no two coexist — applies PMI-1 versioned-gate supersession discipline at the structural-invariant level).
  - `test_critique_dim_9_recursive_self_application_sub_clause_present` (canonical literal pin).
  - `test_critique_dim_9_recursive_self_application_location_pinned` (location-pin per slice-009 M1 + slice-010 M1 convention with scoped `.find()` per slice-009 DEVIATION-2 + slice-010 anchor-uniqueness pre-emption).
  - `test_critique_dim_9_recursive_self_application_names_both_sub_modes` (both sub-mode canonical substrings).
  - `test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors` (≥2 of {`slice-009`, `slice-010`} + ≥1 of {`M2`, `DEVIATION-3`, `BC-PROJ-2`, `B1`, `B5`, `M1`}).
- **1 new bidirectional changelog-pin test** in `tests/methodology/test_methodology_changelog.py`: `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` (asserts `## v0.26.0`, `RSAD-1`, AND substantive canonical phrase `Recursive self-application discipline` in BOTH in-repo + installed `methodology-changelog.md` per slice-008 M2 / slice-009 M3 / slice-010 M3 N-surface pin).
- **PMI-1 versioned-gate supersession** in `tests/methodology/test_methodology_changelog.py`: REPLACE `test_plugin_yaml_version_matches_version_file_at_0_25_0` with `test_plugin_yaml_version_matches_version_file_at_0_26_0` (slice-011 = N=4 supersession event; slice-007 introduced → slice-008/009/010/011 superseded). No two version-gates coexist.
- **Atomic version bump**: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.25.0 → 0.26.0 (PMI-1 invariant per slice-007 escape-closure pattern).
- **Shippability catalog row 11** at `architecture/shippability.md`: critical path = Dim 9 6th sub-clause `Recursive self-application discipline` (5 prose-pin tests including M1 location-pin + sub-mode + cross-slice anchor pins) + existing CAD-1 byte-equality on `agents/critique.md` (slice-007 introduction; reused) + bidirectional v0.26.0 entry pin + PMI-1 0.26.0 atomicity. Updates row 10 (slice-010) to note PMI-1 version-gate supersession at slice-011 (mirrors slice-009/010 row-update precedent).

## What's reused

- [[agents/critique.md]] Dim 9 5-sub-clause structure (slice-006 CCC-1 v1 + slice-009 CCC-1 v1.1 refinement) — slice-011 appends ONE new sub-clause preserving the existing 5 bit-for-bit.
- [[skills/critique/SKILL.md]] — orchestrator only; not touched by slice-011 (per Critic agent vs skill separation-of-concerns rule documented in skill prose: "edit the agent file, not this skill").
- [[methodology-changelog.md]] v0.25.0 MCT-1 entry — slice-010 codification establishes the -T-suffix prose-heuristic convention; slice-011 extends with -D-suffix RSAD-1 convention parallel.
- [[architecture/decisions/ADR-006-critique-agent-drift-detection-via-hybrid-prose-and-audit.md]] — CAD-1 byte-equality audit via `tools/critique_agent_drift_audit.py` + `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` — slice-011 reuses for AC #4 (per-file mini-CAD-1 byte-equality on `agents/critique.md`; PASSING → WRITTEN-FAILING → PASSING transition per slice-007/009/010 row 3 precedent at N=3 stable).
- [[architecture/decisions/ADR-007-bc-1-negative-context-anchors-via-final-filter.md]] — BC-1 v1.2 negative-anchor mechanism (slice-008). Slice-011's mission-brief + design.md contain methodology-vocabulary negative anchors (`Dim 9`, `aggregated lessons`, `forward-sync`, `defer-with-rationale`, `vocabulary`) at high density so BC-GLOBAL-1 silences cleanly.
- [[architecture/decisions/ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class.md]] — CCC-1 v1.1 inline-refinement precedent (slice-009; ~5-sentence Dim 9 sub-clause body refinement). Slice-011 mirrors structurally: Dim 9 sub-clause body extension, but APPEND-NEW vs INLINE-REFINEMENT (slice-011 grows the structural-invariant count 5 → 6; slice-009 preserved count at 5).
- [[architecture/decisions/ADR-009-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic.md]] — MCT-1 codification (slice-010). Slice-011 IS the FIRST slice to operate under MCT-1 default (`critic-required: true` auto-set because slice modifies `agents/critique.md` + `methodology-changelog.md` — both in MCT-1 trigger glob). Recursive: slice-011 ALSO modifies the Critic agent prompt to add a new sub-clause governing recursive-self-application — meta-recursive at the methodology-creation level.
- [[architecture/slices/_index.md]] Aggregated lessons section (line 27 + line 40 of recent-10 reflection list explicitly recommend `promote-recursive-self-application-discipline-to-critique-skill-prose` at slice-011+ when N=3 evidence threshold met; slice-010 reflection met the threshold).
- `tools/test_first_audit.py` — TF-1 strict-pre-finish (slice-003 introduction). Slice-011 follows the 8-row TF-1 plan with status progressions PENDING/PASSING → WRITTEN-FAILING → PASSING per N=7 stable lesson.
- `tools/plugin_manifest_audit.py` — PMI-1 atomic invariant (slice-007 introduction); slice-011 versioned-gate test supersession ratchets N=4 supersession events.

## Components touched

### `agents/critique.md` (modified)

- **Responsibility**: defines the Critic AI persona's adversarial system prompt — 9 review dimensions, specificity/honesty rules, output format, calibration awareness.
- **Lives at**: `agents/critique.md` (in-repo canonical source); `~/.claude/agents/critique.md` (forward-sync mirror).
- **Key interactions**: `skills/critique/SKILL.md` invokes the agent via `subagent_type: "critique"` and passes slice inputs; the agent prompt itself is referenced by `skills/critic-calibrate/SKILL.md:107-114` as the canonical-source forward-sync target (CAD-1 hybrid via ADR-006).
- **What this slice does**: appends ONE new sub-clause body at L167 within Dim 9 ("Cross-cutting conformance") between the existing L166 `Language-version conformance` sub-clause close and the existing L168 `### Bonus: weak graph edges` H3 anchor. Sub-clause body details below at [Sub-clause canonical body](#sub-clause-canonical-body-to-insert-in-agentscritiquemd-l167).

### Sub-clause canonical body to insert in `agents/critique.md` L167

The exact prose to append at L167 (between current L166 `Language-version conformance` body end and current L168 `### Bonus: weak graph edges` H3):

```markdown
- **Recursive self-application discipline** — N=3 sub-clause (slice-009 M2 design-time + slice-010 /critique design-time stress-test + slice-010 build-time DEVIATION-3); peer cross-reference: none — operates at the meta level above the other five Dim 9 sub-clauses. When a slice authors a methodology refinement (rule, audit, prompt addition, dimension or sub-clause extension), the Critic should EXPECT to find rule-class violations in the slice's own artifacts (mission-brief, design.md, ADRs, and any /critique fix prose subsequently added). Two distinct sub-modes:
  - **Design-time mode** — the Critic stress-tests the slice's own draft prose against the very discipline being encoded; a slice authoring rule X should be examined under rule X at design-time. Concrete catches: slice-009 M2 (slice's own design.md committed the exact class of drift the slice was encoding into Dim 9 sub-clause 2); slice-010 B1 + M1 + B5 (the slice authoring MCT-1 had its own SKILL.md bullet draft caught for internal-inconsistency + bullet-style asymmetry vs the existing 7 sibling bullets + rule-naming convention break — three rule-class violations in the slice's own prose, all caught at /critique design-time stress-test).
  - **Build-time-via-/critique-fix-prose mode** — when /critique fix prose empirically describes a build-check rule's positive-anchor strings (the substring literals the rule fires on), the prose itself may RE-INTRODUCE those substrings into the slice's mission-brief or design.md, firing the rule at /build-slice Phase 4 self-application audit at build-time. Concrete miss: slice-010 DEVIATION-3 (Critic-MISSED at /critique) — a /critique B4 fix paragraph empirically describing BC-PROJ-2's positive-anchor strings RE-INTRODUCED those strings into the slice's mission-brief and design.md, triggering BC-PROJ-2's anchor path at Phase 4 BC-1 self-application audit. The fix prose was recursive-self-application at one level deeper than design-time.

  When reviewing a slice that authors a methodology refinement, the Critic SHOULD: (1) stress-test the slice's draft prose against the very discipline being encoded — examine the slice's own mission-brief, design, and ADR text for rule-class violations the new rule would catch in other slices; (2) anticipate that any /critique fix prose introducing empirical examples (anchor substrings, trigger keywords, regex patterns) may RE-INTRODUCE those same triggers into the slice's artifacts, firing the rule at build time — flag draft fix prose adding empirical-rebuttal anchor descriptions WITHOUT explicit awareness of the recursive trigger risk.

```

**Notes on canonical-body content**:
- The body deliberately uses ABSTRACT descriptions of anchor STRINGS (`positive-anchor strings`, `the substring literals the rule fires on`, `anchor substrings`, `trigger keywords`, `regex patterns`) rather than naming concrete BC-PROJ-2 anchor literals (`fence`, `code-block`, `llm`) cited in slice-010's reflection. **The rationale is stylistic / reusable-artifact-readability** (per slice-011 Critic M1 correction): the canonical Critic-prompt artifact at `agents/critique.md` is consumed by every future Critic invocation; abstract framing of anchor strings reads better there, while the literal anchor strings belong in slice-N reflection records as empirical primary sources where they have retrieval traction. **The earlier-drafted "meta-meta-recursive build-time fire on `agents/critique.md` content" framing was based on a misreading of BC-1's audit scope** — BC-1 reads `mission-brief.md` + `design.md` of the slice being audited (per `tools/build_checks_audit.py::_read_slice_text` L435-L442), NOT the content of changed files like `agents/critique.md`. So the canonical body's content has no BC-1-firing role regardless. The rule-ID `BC-PROJ-2` IS named explicitly in the body (matches existing Dim 9 sub-clause convention naming `BC-1`, `RR-1`, `TF-1`, `INST-1`, `WIRE-1`, `NFR-1`, `VAL-1`, `CSP-1` by ID); only the anchor STRINGS stay abstract. The slice's transient artifacts (mission-brief + design.md + ADR-010) DO carry the concrete anchor strings for empirical evidence of the build-time sub-mode — but the canonical body keeps the anchor strings abstract for readability.
- The body contains `Dim 9` (one explicit "Dim 9 sub-clauses" reference) — `Dim 9` is BC-GLOBAL-1's negative anchor (BC-1 v1.2 / slice-008). Per slice-011 Critic M1: this property is mostly irrelevant since BC-1 doesn't audit `agents/critique.md` content directly, but is a cheap belt-and-suspenders alignment with the project's methodology-vocabulary negative-anchor convention.
- **B1 pre-emption (slice-009 DEVIATION-1 case-sensitivity trap)**: sub-mode bullet titles are capitalized form (`**Design-time mode**`, `**Build-time-via-/critique-fix-prose mode**`) honoring markdown bullet-start sentence convention. Lowercase compound forms `design-time` and `build-time` appear MID-sentence in the bullet bodies (e.g., "examined under rule X at design-time"; "at /build-slice Phase 4 self-application audit at build-time") where the test's case-sensitive `in` operator finds them. Per slice-011 Critic B1 catch on the original draft: the original placed `**design-time mode**` / `**build-time-... mode**` at bullet-start with lowercase first word — exactly the DEVIATION-1 trap class. The revision capitalizes titles + relocates lowercase canonical substrings to mid-sentence positions.
- Indentation: ONE leading dash level (`- **Recursive...`) at L167 to match the 5 existing sibling sub-clauses; nested sub-mode bullets use 2-space indent (`  - **Design-time mode**`) matching the existing nested-bullet convention in Dim 1 sub-bullets (e.g., L91-93 "TF-1 row coverage" nested under "Methodology-audit conformance").

## Contracts added or changed

None. Slice-011 does not introduce any new endpoint, event, or external contract. The change is entirely prose-level in the Critic agent's adversarial system prompt + methodology-changelog entry + atomic version bump.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Slice-011 introduces no new modules — only prose changes to `agents/critique.md`, an entry append to `methodology-changelog.md`, and 5 new test functions in EXISTING test files (`tests/methodology/test_critique_agent.py` + `tests/methodology/test_methodology_changelog.py`). No new `src/` modules; no new `tools/` modules.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(empty matrix; WIRE-1 treats zero-row matrices as clean per design)

## Decisions made (ADRs)

- [[ADR-010]] — Promote recursive-self-application discipline to `agents/critique.md` Dim 9 6th sub-clause via append-new (Option 1 over inline-refinement Option 2 vs new-top-level-dimension Option 3); RSAD-1 rule reference with -D-suffix prose-heuristic convention extending slice-010's MCT-1 -T-suffix B5 calibration-trail convention — reversibility: cheap (with magnitude justification: ~12 sites, same class as ADR-007/009).

## Authorization model for this slice

N/A — slice-011 is a methodology-prose refinement, not a runtime feature. No new endpoints, no authz decisions, no data access paths. The "authorization" of the rule itself is the Critic agent reading the new sub-clause at /critique invocation time — purely prose-driven behavior.

## Error model for this slice

N/A — slice-011 introduces no runtime error paths. Build-time error paths inherited from existing tooling:
- TF-1 strict-pre-finish refuses any non-PASSING row at `/build-slice` Phase 6 (existing).
- PMI-1 atomicity refuses on version-file divergence (existing).
- CAD-1 mini-byte-equality test refuses on `agents/critique.md` in-repo↔installed sha256 mismatch (existing, slice-007 introduction).
- The 5 new prose-pin tests raise `AssertionError` with specific pinned-substring failure messages on prose drift (per TF-1 PENDING → WRITTEN-FAILING genuineness lesson at N=7 stable).

## Test impl notes (slice-009/010 DEVIATION pre-emption applied)

**Location-pin test impl** (`test_critique_dim_9_recursive_self_application_location_pinned`):

```python
def test_critique_dim_9_recursive_self_application_location_pinned():
    """The new 6th sub-clause must fall between Language-version conformance and the Bonus H3.

    Defect class: a future drift moving the new sub-clause out of Dim 9 (e.g., into Dim 8
    or the Bonus section) would silently pass substring-only pin tests; the location-pin
    guard catches it. Per slice-009 M1 + slice-010 M1 location-pin convention; per
    slice-009 DEVIATION-2 + slice-010 anchor-uniqueness pre-emption: anchors verified
    unique pre-AC-lock; scoped .find() to avoid first-occurrence-wins collision.
    Rule reference: META-2 + CCC-1 + RSAD-1.
    """
    start_anchor = "Language-version conformance"
    end_anchor = "### Bonus: weak graph edges"
    canonical = "Recursive self-application discipline"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )
```

Scoped `.find(substring, start_idx, end_idx)` avoids slice-009 DEVIATION-2 `.find()`-collision class — no first-occurrence-wins ambiguity. Anchor uniqueness empirically verified pre-AC-lock via grep (both substrings appear exactly once in `agents/critique.md`).

**Sub-mode pin test impl** (`test_critique_dim_9_recursive_self_application_names_both_sub_modes`):

```python
def test_critique_dim_9_recursive_self_application_names_both_sub_modes():
    """Sub-clause body must name BOTH design-time and build-time sub-modes.

    Defect class: a body that only names design-time loses the build-time-via-/critique-
    fix-prose sub-mode (slice-010 DEVIATION-3 evidence) — incomplete coverage of the N=3
    cumulative evidence base.
    Per slice-009 DEVIATION-1 case-sensitivity mitigation: canonical substrings
    `design-time` AND `build-time` are lowercase compound forms placed mid-sentence in
    the body prose; tests assert exact case-sensitive match.
    Rule reference: META-2 + CCC-1 + RSAD-1.
    """
    start_anchor = "Recursive self-application discipline"
    end_anchor = "### Bonus: weak graph edges"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1
    body = CRITIQUE[start_idx:end_idx]
    assert "design-time" in body, "sub-clause body missing canonical substring 'design-time'"
    assert "build-time" in body, "sub-clause body missing canonical substring 'build-time'"
```

**Cross-slice anchor pin test impl** (`test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors`):

```python
def test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors():
    """Sub-clause body must cite ≥2 cross-slice anchors + ≥1 sub-class anchor.

    Defect class: descriptive sub-class text drifts unpinned to abstract framings without
    concrete traceability — readers lose the path back to the empirical evidence base.
    Pinned at N=3 evidence (slice-009 M2 + slice-010 design-time + slice-010 build-time).
    Per slice-008 M2 + slice-009 M3 + slice-010 M3 N-substring + N-surface schema-pin discipline.
    Rule reference: META-2 + CCC-1 + RSAD-1.
    """
    start_anchor = "Recursive self-application discipline"
    end_anchor = "### Bonus: weak graph edges"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-009", "slice-010"]
    sub_class = ["M2", "DEVIATION-3", "BC-PROJ-2", "B1", "B5", "M1"]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sc_count = sum(1 for anchor in sub_class if anchor in body)
    assert cs_count >= 2, (
        f"insufficient cross-slice anchors — need ≥2 of {cross_slice}, "
        f"got {cs_count} in sub-clause body"
    )
    assert sc_count >= 1, (
        f"insufficient sub-class instance anchors — need ≥1 of {sub_class}, "
        f"got {sc_count} in sub-clause body"
    )
```

**Note on `BC-PROJ-2` substring in test impl**: the cross-slice-anchor test's `sub_class` allowlist contains the literal string `BC-PROJ-2`. The test FILE `tests/methodology/test_critique_agent.py` is NOT in `--changed-files` patterns BC-1 audits typically target (BC-1 v1.2's BC-PROJ-2 fires on slice mission-brief + design.md patterns per slice-010 reflection; not on test files). Safe substring.

## Pre-AC-lock empirical audits (per slice-009 N=8 → slice-010 N=9 → slice-011 N=10 stable lesson)

**Audit 1: Canonical-literal absence verification** (pre-empts slice-009 DEVIATION-1 case-sensitivity-at-sentence-start trap).

Empirical grep on `agents/critique.md` for canonical literal `Recursive self-application discipline` BEFORE the slice's edit: ZERO matches confirmed. The PENDING → WRITTEN-FAILING transition for AC #1 + AC #3 will be authentic.

Empirical grep for lowercase compound forms `design-time` and `build-time` within `agents/critique.md`: present in OTHER contexts (e.g., Dim 1's "design-time" or similar). The new sub-clause body MUST keep these phrases mid-sentence per slice-009 DEVIATION-1 lesson; the location-pin test scopes the search to the new sub-clause body bounds to avoid false positives from other Dim sections.

**Audit 2: Location-pin anchor uniqueness verification** (pre-empts slice-009 DEVIATION-2 `.find()`-collision trap).

Empirical grep on `agents/critique.md` for both location-pin anchors:
- `Language-version conformance` — appears EXACTLY ONCE at L166 (verified at design time).
- `### Bonus: weak graph edges` — appears EXACTLY ONCE at L168 (verified at design time).

Both anchors unique; scoped `.find(end_anchor, start_idx)` test impl pre-empts collision class.

**Audit 3: Self-application BC-1 prediction on slice-011's TRANSIENT artifacts** (corrected per slice-011 Critic M1 + M2 catches).

**Important correction (per slice-011 Critic M1)**: BC-1 reads `mission-brief.md` + `design.md` of the SLICE being audited (per `tools/build_checks_audit.py::_read_slice_text` L435-L442), NOT the content of `agents/critique.md` or any other changed file. The earlier-drafted "meta-meta-recursive build-time fire on `agents/critique.md` content" framing was based on a misreading of BC-1 semantics. The canonical sub-clause body's content has no BC-1-firing role regardless; only the slice's mission-brief.md + design.md text matter for BC-1 audits.

Empirical scan of slice-011's TRANSIENT artifacts (mission-brief.md + design.md + ADR-010) for BC-PROJ-1's positive anchors (`subagent`, `fan-out`) + BC-PROJ-2's positive anchors (`fence`, `code-block`, `llm`):
- `subagent` — ≥1 match in design.md (this Audit 3 section's listing).
- `fan-out` — ≥1 match in design.md (this Audit 3 section's listing).
- `fence` — ≥1 match in mission-brief.md + design.md + ADR-010 (empirical-evidence descriptions of the build-time sub-mode).
- `code-block` — ≥1 match in mission-brief.md + design.md + ADR-010.
- `llm` — ≥1 match in mission-brief.md + design.md + ADR-010.

**Phase 4 BC-1 audit predicted outcome** (corrected per slice-011 Critic M2 — BC-GLOBAL-1's path is `Applies to: **` glob, NOT `always: true` short-circuit; slice-005 made this change):

- **BC-PROJ-1**: positive trigger fires via `subagent` / `fan-out` substrings in design.md Audit 3 listing → BC-1 v1.2 negative-anchor filter checks methodology-vocabulary anchors (`Dim 9`, `aggregated lessons`, `forward-sync`, `back-sync`, `vocabulary`, `meta-discussion`, `defer-with-rationale`) which slice-011's mission-brief + design.md contain at high density per slice-008 BC-PROJ-1 v1.2 migration → BC-PROJ-1 SILENCED via negative-anchor filter. Expected: `applicable: []` for BC-PROJ-1.
- **BC-PROJ-2**: positive trigger fires via `fence` / `code-block` / `llm` substrings in mission-brief + design.md + ADR-010 → BC-PROJ-2 has NO negative anchors yet (slice-008 deferred BC-PROJ-2 negative-anchor migration to N=2; slice-011 ratchets to N=2 evidence; separate slice-011+ candidate not bundled here) → BC-PROJ-2 POSITIVELY FIRES on slice-011's artifacts. Expected: `applicable: [BC-PROJ-2]` per slice-010 DEVIATION-3 precedent, **dispositioned defer-with-rationale at /validate-slice** per BC-1 Important semantics. This is the empirical demonstration of the build-time-via-/critique-fix-prose sub-mode that RSAD-1 encodes — slice-011 is the canonical reference instance.
- **BC-GLOBAL-1**: positive trigger fires via `Applies to: **` GLOB match against `--changed-files` (slice-005 changed `Applies to: always: true` → `Applies to: **` per `~/.claude/build-checks.md` L18-L19; `_rule_applies` glob path matches against `--changed-files` when non-empty). When `--changed-files` is non-empty (real /build-slice invocations always pass it), the keyword path checks slice mission-brief + design.md → methodology-vocabulary substrings present → BC-1 v1.2 negative-anchor filter checks `aggregated lessons` / `forward-sync` / `back-sync` / `Dim 9` / `vocabulary` / `meta-discussion` / `defer-with-rationale` (all present in slice-011's prose at high density) → BC-GLOBAL-1 SILENCED via negative-anchor filter. Expected: `applicable: []` for BC-GLOBAL-1.

**Net expected Phase 4 BC-1 self-application result**: `applicable: [BC-PROJ-2]`. Slice-011 demonstrates the build-time-via-/critique-fix-prose sub-mode by intentionally triggering BC-PROJ-2 on its own transient artifacts while the canonical Critic-prompt sub-clause body (in `agents/critique.md`) stays stylistically clean of anchor literals. The two-tier discipline (canonical reads abstractly / transient demonstrates concretely) makes slice-011 the canonical reference instance of the rule it encodes.

**Acknowledgment per Critic M1 + M2 catches**: these two catches are themselves recursive-self-application instances at slice-011's /critique time — slice-011 (encoding RSAD-1) had its own design.md committed a misframing about BC-1 audit scope (M1) AND a misframing about BC-GLOBAL-1's `Applies to:` path (M2). Strongest single-slice in-context demonstration that RSAD-1's design-time sub-mode is load-bearing.

## Pre-existing branch interactions (slice-005 algorithm-path-conformance lesson)

`tests/methodology/test_critique_agent.py` line 115 currently defines `test_critique_dim_9_lists_five_sub_clauses`. Slice-011 REPLACES (deletes + adds) this with `test_critique_dim_9_lists_six_sub_clauses` — same shape, 6 substrings asserted (the 5 existing + new `Recursive self-application discipline`).

Per PMI-1 versioned-gate supersession discipline (slice-007/008/009/010 N=3-events stable; slice-011 ratchets to N=4): the OLD test `_lists_five_sub_clauses` is DELETED in the same commit that introduces `_lists_six_sub_clauses`. No two structural-invariant tests coexist (mirrors the PMI-1 version-gate convention applied at the structural-invariant level).

Other existing Dim 9-related tests stay UNCHANGED:
- `test_critique_dim_9_cross_references_resolve` (L131) — UNCHANGED (still resolves Dim 4 + Dim 1 cross-references; new 6th sub-clause has no cross-reference; `peer cross-reference: none — operates at the meta level`).
- `test_critique_dim_9_citation_is_deliberate` (L147) — UNCHANGED (Kiczales + honest-out citation preserved at Dim 9 preamble; new sub-clause doesn't touch the citation).
- `test_critique_lists_nine_dimensions` (L41) — UNCHANGED (Dim 9 title unchanged; only sub-clause body grows).

Regression-guard: `pytest tests/methodology/test_critique_agent.py -q` after slice-011 build must show 6 NEW PASSING (5 prose-pin + the replaced `_lists_six_sub_clauses`) + ALL existing tests PASSING (zero regression). Slice-010's existing test count baseline + 5 net additions = expected count.

## Out-of-repo file forensic capture plan (slice-005..010 N=6 stable lesson)

Per slice-005 + slice-006 + slice-007 + slice-008 + slice-009 + slice-010 N=6 stable bidirectional sha256 forensic-capture pattern, `build-log.md` Phase 0 (pre-edit) + Phase 4 (post-forward-sync) capture sha256 for:

| File pair | Phase 0 (pre-edit) | Phase 4 (post-forward-sync) |
|-----------|--------------------|----------------------------|
| `agents/critique.md` (in-repo) | sha256_a0 | sha256_a4 (≠ sha256_a0) |
| `~/.claude/agents/critique.md` (installed) | sha256_a0 (= in-repo at slice start, CAD-1 invariant from slice-007) | sha256_a4 (= in-repo at slice end, CAD-1 invariant) |
| `methodology-changelog.md` (in-repo) | sha256_b0 | sha256_b4 (≠ sha256_b0) |
| `~/.claude/methodology-changelog.md` (installed) | sha256_b0 (= in-repo at slice start) | sha256_b4 (= in-repo at slice end) |
| `~/.claude/ai-sdlc-VERSION` (installed; in-repo equivalent is `VERSION`) | sha256_c0 (= `0.25.0\n` hash) | sha256_c4 (= `0.26.0\n` hash) |

Slice's git diff alone is insufficient evidence for out-of-repo edits to `~/.claude/...`; Phase 0 + Phase 4 sha256 captures record bidirectional state in `build-log.md`. N=7 stable post-slice-011.

## Mode

Standard. Per [[architecture/slices/archive/slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic/mission-brief.md]] precedent, Standard mode applies (slice-006..010 all Standard for cross-cutting tooling slices). No upfront `/heavy-architect` vault expected.

Thin-vault discipline: no `components/<name>.md` / `contracts/<name>.md` / `schemas/<entity>.md` files created. Code (and Critic agent prose) is the source of truth; design.md references locations.
