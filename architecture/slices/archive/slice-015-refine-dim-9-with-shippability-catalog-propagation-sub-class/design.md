# Design: Slice 015 refine-dim-9-with-shippability-catalog-propagation-sub-class

**Date**: 2026-05-13
**Mode**: Standard

## What's new

- A new **8th sub-clause** appended to `agents/critique.md` Dimension 9 ("Cross-cutting conformance") with canonical literal title `Shippability-catalog consumer-reference propagation`, placed BETWEEN the existing 7th sub-clause `Entry-pin-vs-PMI-1-gate semantics conflation` close (currently ~L178) and the existing `### Bonus: weak graph edges` H3 (currently L180). Body documents BOTH sub-modes: **reactive-catch mode** (slice-013 N=1) + **proactive-application mode** (slice-014 N=2). Cross-slice anchors formalized per slice-011 / slice-013 `_cites_at_least_two_cross_slice_anchors` precedent (post-M2 ACCEPTED-FIXED at /critique):
  - **Cross-slice anchors (strict-both)**: `["slice-013", "slice-014"]` — both MUST be present in the 8th sub-clause body
  - **Substantive-discipline anchors (≥2 of 4)**: `["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]` — at least 2 of these 4 MUST be present in the 8th sub-clause body. Locked at /critique B1 ACCEPTED-FIXED per empirical verification against the canonical body (design.md "Sub-clause canonical body" section): `"Phase 5"` appears at body L123 + L125; `"shippability.md"` appears at L122 + L124 + L125 + L126; `"/validate-slice Step 5.5"` appears at L124 + L126 (slice-013 reactive anchor); `"supersession"` appears at L122 ("PMI-1 structural-invariant supersession") + L122 ("rename-driven supersession discipline"). All 4 anchors empirically present → ≥2-of-4 test robustly PASSES post-build. Original tuple `["Phase 5", "shippability catalog", "consumer reference", "rename propagation"]` was Blocker-rejected because body uses hyphenated forms `shippability-catalog` / `consumer-reference` and never uses literal `rename propagation` — 3 of 4 absent. Slice-013 critique M2 precedent N=1 stable; slice-015 B1 ratchets the anchor-list-empirical-verification discipline to N=2 stable.
- A new `~/.claude/agents/critique.md` mirror (Phase 2 forward-sync target; CAD-1 byte-equality invariant from slice-007 + slice-009..014 N=6 successful syncs).
- A new `methodology-changelog.md` v0.30.0 entry naming **SCPD-1** as the new methodology rule reference (in-repo + installed). Rule-ID convention: **SCPD** = Shippability-Catalog Propagation Discipline; -D suffix per slice-011 RSAD-1 + slice-013 EPGD-1 calibration-trail convention N=2 stable (signals prose-heuristic applied at /critique-time + /build-slice-time, distinct from audit-enforced-gate sibling rules BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1, each of which has a corresponding `tools/*_audit.py`). The -D rule-ID convention reaches N=3 stable at slice-015 (RSAD-1 + EPGD-1 + SCPD-1).
- 5 new test functions in `tests/methodology/test_critique_agent.py`:
  - `test_critique_dim_9_shippability_catalog_propagation_sub_clause_present` (canonical-literal substring pin)
  - `test_critique_dim_9_shippability_catalog_propagation_location_pinned` (location pin between 7th sub-clause close and `### Bonus: weak graph edges` H3 — slice-009 M1 + slice-013 location-pin shape with `text.find()` and verified-unique anchors per slice-009 DEVIATION-2 / slice-010 anchor-uniqueness pre-emption)
  - `test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes` (literal `Reactive-catch mode` + `Proactive-application mode` strict-both pin per slice-011 / slice-013 sub-mode-pin shape)
  - `test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014` (cross-slice anchor pin — strict-both per slice-013 EPGD-1 cross-slice anchor convention)
  - `test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors` (≥2-of-4 substantive-discipline anchor pin per slice-013 Critic M2 ACCEPTED-FIXED precedent — final anchor tuple locked at /critique)
- 1 superseded structural-invariant test in `tests/methodology/test_critique_agent.py`: `test_critique_dim_9_lists_eight_sub_clauses` replaces `test_critique_dim_9_lists_seven_sub_clauses` (PMI-1 structural-invariant supersession discipline per slice-011 N=1 + slice-013 N=2 stable precedent — no two structural-invariant tests coexist; `_lists_eight_sub_clauses` subsumes slice-013's 7-sub-clause assertion by asserting all 8 titles including the 8th `Shippability-catalog consumer-reference propagation`).
- 1 mini-CAD-1 row 3 regression-guard test PASSING throughout (sliced-013 N=6 → slice-015 N=7 stable transition pattern PASSING → WRITTEN-FAILING → PASSING).
- 1 new test in `tests/methodology/test_methodology_changelog.py`: `test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed` (3-pin shape: `## v0.30.0` heading + `SCPD-1` rule-ID + substantive canonical phrase `Shippability-catalog consumer-reference propagation`).
- 1 new test in `tests/methodology/test_methodology_changelog.py`: `test_adr_014_exists_and_names_scpd_1_canonical_phrase` (mirrors slice-014 ADR-013 pin shape).
- Atomic version bump: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all `0.29.0` → `0.30.0`. Under PMI-1 v1.1 version-agnostic gate (slice-014) — second version bump under v1.1 (slice-014's 0.28.0 → 0.29.0 was the first); empirical retirement-proof of PMI-1 v1.1 N=1 → N=2 stable.
- `architecture/shippability.md` row 15 added; row 14 header updated to reflect slice-015's structural-invariant supersession.
- **Phase 5 SCPD-1 self-application**: rows 6 + 11 + 13 of `architecture/shippability.md` carry stale references to `_lists_seven_sub_clauses` from slices 6/11/13 respectively; slice-015's structural-invariant supersession `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` requires the SAME Phase to propagate the rename across all 3 rows. **This is the canonical reference instance of SCPD-1 — the slice authoring the rule IS itself bound by the rule** (mirrors slice-011 RSAD-1 self-application + slice-013 EPGD-1 self-application).
- ADR-014 — Promote shippability-catalog consumer-reference propagation discipline to agents/critique.md Dim 9 8th sub-clause via append-new (SCPD-1).

## What's reused

- [[agents/critique.md]] — the canonical Critic-prompt body; slice-015 appends ONLY at the 7th-sub-clause-close ↔ `### Bonus: weak graph edges` H3 boundary; existing 7 sub-clauses + Dim 1-8 + Bonus section untouched.
- [[architecture/decisions/ADR-005-add-cross-cutting-conformance-9th-critic-dimension]] — CCC-1 v1 introduced Dim 9 with 5 sub-clauses. SCPD-1 extends Dim 9's enumeration to 8 sub-clauses (slice-011 grew 5→6; slice-013 grew 6→7; slice-015 grows 7→8) — additive sibling, not superseding ADR-005.
- [[architecture/decisions/ADR-010-promote-recursive-self-application-discipline-to-critique-dim-9-sub-clause]] — RSAD-1 (slice-011); canonical -D-suffix rule-ID convention + append-new sub-clause structural-shape reference for slice-015.
- [[architecture/decisions/ADR-012-promote-entry-pin-vs-pmi-1-gate-discipline-to-critique-dim-9-sub-clause]] — EPGD-1 (slice-013); the most direct structural-shape reference for slice-015 (append-new sub-clause + 6 prose-pin tests scaffold + 7→8 mini-PMI-1-style structural-invariant supersession + N=2-evidence-threshold-promotion pattern + -D-suffix rule-ID convention).
- [[architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape]] — PMI-1 v1.1 (slice-014); the new version-agnostic gate baseline. Slice-015 is the second bump under v1.1 (first was slice-014's 0.28.0→0.29.0); empirical retirement-proof N=1→N=2 stable.
- `tests/methodology/test_critique_agent.py` — existing 25+ tests from slice-006..013 (the structural-invariant `_lists_seven_sub_clauses` + location-pin + canonical-substring + cross-slice anchors). Slice-015 supersedes `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`; adds 5 new tests; deletes 0 (existing tests preserved per backward-compat covenant per slice-011 + slice-012 + slice-013 Critic findings B1 class).
- `tests/methodology/test_methodology_changelog.py` — existing 7 entry-pin functions for v_0_22_0..v_0_29_0 post-slice-014 (one per shipped versioned changelog entry) + 1 PMI-1 v1.1 version-agnostic gate `test_plugin_yaml_version_matches_version_file_invariant` + 2 AST meta-tests (`_is_version_agnostic_shape` + `_no_per_version_pmi_1_gate_functions_remain`) + 1 regression test from slice-014. Slice-015 ADDS 1 entry-pin function (`test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed`) + 1 ADR-pin function (`test_adr_014_exists_and_names_scpd_1_canonical_phrase`); deletes 0; supersedes 0. **No PMI-1 gate Edit needed at slice-015** — PMI-1 v1.1 version-agnostic gate body unchanged through atomic version bump (canonical reference of empirical retirement of versioned-gate supersession pattern per slice-014 (a) ↔ (b) duality).
- `tools/plugin_manifest_audit.py` — PMI-1 audit; reused unchanged. Verifies `VERSION` + `ai-sdlc-VERSION` + `plugin.yaml.version` atomicity post-bump.
- `tools/critique_agent_drift_audit.py` — CAD-1 audit; reused unchanged. Verifies in-repo↔installed `agents/critique.md` byte-equality.
- `tools/build_checks_audit.py` — BC-1 audit; reused unchanged. Negative-anchor mechanism (BC-1 v1.3 / slice-012) silences slice-015's own mission-brief + design.md methodology-vocabulary firing.
- `tools/test_first_audit.py` — TF-1 audit; reused unchanged. Verifies 10-row TF-1 plan at pre-finish (one row per AC per slice-014 generic methodology lesson on first-integer-only AC parsing).
- [[methodology-changelog.md]] — v0.21.0 (CCC-1 v1) + v0.24.0 (CCC-1 v1.1) + v0.26.0 (RSAD-1) + v0.28.0 (EPGD-1) lineage; v0.30.0 (SCPD-1) is the next entry. PMI-1 v1.1 atomic version-bump invariant continues from slice-014.
- `architecture/shippability.md` — 14-row catalog from slice-014; rows 6 + 11 + 13 reference `_lists_seven_sub_clauses` and require Phase 5 propagation; row 15 appended per slice-008/009/010/011/012/013/014 convention.
- `~/.claude/CLAUDE.md` + `~/.claude/skills/critic-calibrate/SKILL.md` — unchanged. Slice-015 does NOT touch the calibration log or critic-calibrate skill prose.

## Components touched

### `agents/critique.md` — Dim 9 sub-clause enumeration

- **Responsibility**: canonical Critic-prompt body read by every `/critique` invocation. Dim 9 enumerates cross-cutting-conformance sub-classes; slice-015 adds the 8th.
- **Lives at**: `agents/critique.md` (modified — single append between 7th sub-clause close and `### Bonus: weak graph edges` H3)
- **Key interactions**: read by `agents/critique.md`'s consumer (the `Agent({subagent_type: "critique"})` invocation in `~/.claude/skills/critique/SKILL.md`); byte-equal mirror at `~/.claude/agents/critique.md` (forward-sync target).

### `~/.claude/agents/critique.md` — installed mirror

- **Responsibility**: byte-equal mirror of in-repo `agents/critique.md`; the file actually read by the Critic agent at runtime.
- **Lives at**: `~/.claude/agents/critique.md` (modified — full replacement to match in-repo post-edit)
- **Key interactions**: read by Claude Code's Agent dispatcher at /critique invocation; sha256 byte-equality enforced by CAD-1 audit (`tools/critique_agent_drift_audit.py`).

### `methodology-changelog.md` — v0.30.0 entry

- **Responsibility**: append-only changelog of behavior-changing rules in the AI SDLC pipeline. v0.30.0 entry codifies SCPD-1.
- **Lives at**: `methodology-changelog.md` (in-repo) + `~/.claude/methodology-changelog.md` (installed mirror)
- **Key interactions**: read by `/status` for surfacing methodology metadata; pinned bidirectionally by `tests/methodology/test_methodology_changelog.py` entry-pin functions; PMI-1 v1.1 atomic version-bump invariant continues from slice-014.

### `tests/methodology/test_critique_agent.py` — 5 new test functions + 1 superseded structural-invariant

- **Responsibility**: prose-pin tests on `agents/critique.md` body. Asserts canonical literal substrings + structural invariants + location pins.
- **Lives at**: `tests/methodology/test_critique_agent.py` (modified — 5 added + 1 replaced)
- **Key interactions**: loaded by pytest; reads in-repo `agents/critique.md` content via module-level `CRITIQUE = (Path(__file__).parents[2] / "agents" / "critique.md").read_text(encoding="utf-8")`.

### `tests/methodology/test_methodology_changelog.py` — 2 new functions (entry-pin + ADR-pin)

- **Responsibility**: bidirectional changelog-entry pins (per shipped version) + ADR-pin functions.
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (modified — 2 added; ZERO supersession; ZERO entry-pin deletion risk; PMI-1 v1.1 version-agnostic gate body unchanged)
- **Key interactions**: loaded by pytest; reads in-repo + installed `methodology-changelog.md` for entry-pin asserts; reads `architecture/decisions/ADR-014-*.md` for ADR-pin assert.

### `architecture/shippability.md` — row 15 added + rows 6 + 11 + 13 propagated (SCPD-1 self-application)

- **Responsibility**: 14-row catalog from slice-014 grows to 15-row catalog at slice-015; rows 6 + 11 + 13 carry stale references to `_lists_seven_sub_clauses` requiring same-Phase propagation to `_lists_eight_sub_clauses`.
- **Lives at**: `architecture/shippability.md` (modified — 1 row added + 3 rows propagated)
- **Key interactions**: read by `/validate-slice` Step 5.5 (pre-finish catalog run); all 15 rows must PASS in <2 min aggregate post-Phase-5.

## Contracts added or changed

None. Slice introduces no API endpoints, events, or external integrations. Pure prompt-prose addition + changelog entry + version bump + shippability-catalog propagation.

## Data model deltas

None. No DB schema, no migration, no data-model field changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Slice introduces NO new `.py` modules. Empty matrix is treated as clean by `tools/wiring_audit.py`.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-014]] — Promote shippability-catalog consumer-reference propagation discipline to agents/critique.md Dim 9 8th sub-clause via append-new (SCPD-1) — reversibility: cheap

## Authorization model for this slice

Not applicable. Slice modifies prose content in canonical methodology files; no runtime authorization decisions are introduced. Edits to `agents/critique.md` + `methodology-changelog.md` + `VERSION` + `architecture/shippability.md` are governed by repository write access (existing — slice-015 is authored by the project owner per the existing developer flow).

## Error model for this slice

Slice introduces no runtime error codes. Build-time error surfaces are existing audit failures:

- **CAD-1 byte-equality failure** (`tools/critique_agent_drift_audit.py` exit 1 with `content-drift`) — fires at /build-slice Phase 2 mid-slice smoke if in-repo `agents/critique.md` edited but installed mirror not yet forward-synced. Expected at mid-slice gate; must be exit 0 at pre-finish gate.
- **PMI-1 v1.1 atomicity failure** (`tools/plugin_manifest_audit.py` exit 1 with version mismatch) — fires if `VERSION` / `ai-sdlc-VERSION` / `plugin.yaml.version` get out of sync at Phase 1d. Mitigation: atomic 3-file edit in single commit per slice-007 escape-closure pattern + PMI-1 v1.1 version-agnostic gate (slice-014) verifies the invariant continues to hold with ZERO test code modification.
- **TF-1 strict-pre-finish failure** (`tools/test_first_audit.py --strict-pre-finish` exit 1) — fires if any TF-1 row is non-PASSING at Phase 6 pre-finish. Mitigation: 10-row TF-1 plan locked at mission-brief; transitions tracked per slice-011/012/013/014 PENDING → WRITTEN-FAILING → PASSING discipline.
- **BC-1 self-application firing** (`tools/build_checks_audit.py --slice architecture/slices/slice-015-...` reports `applicable=[BC-PROJ-1]` Important or similar) — slice's own mission-brief + design.md carry methodology-vocabulary anchors. Mitigation: BC-1 v1.3 negative-anchor mechanism (slice-008 + slice-012 — uniform 9-token set on BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1) silences ALL three project-relevant rules. Expected post-build result: `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` per slice-012/013/014 self-application pattern N=11 → N=12 → N=13 ratchet.
- **SCPD-1 self-application failure** (post-Phase 1f mini-PMI-1-style structural-invariant supersession, any of shippability.md rows 6 + 11 + 13 still reference `_lists_seven_sub_clauses`) — fires at /validate-slice Step 5.5 if rows 6 + 11 + 13 are not propagated to `_lists_eight_sub_clauses` in the SAME Phase as the supersession Edit. Mitigation: Phase 5 plan (below) explicitly enumerates the 3-row propagation BEFORE running shippability catalog. **This is the slice's own canonical reference-instance verification of the SCPD-1 discipline it authors** (RSAD-1 self-application N=6 → N=7 cumulative). Empirical pre-verification: Audit 4 below.
- **EPGD-1 self-application N/A** — slice-015 does NOT supersede any PMI-1 versioned-gate or PMI-1 structural-invariant function in `test_methodology_changelog.py`; only ADDS entry-pin + ADR-pin functions (Phase 1b). PMI-1 v1.1 version-agnostic gate (slice-014) body unchanged through atomic version bump. Slice-014's empirical retirement-proof of versioned-gate supersession pattern continues at slice-015 (N=1 → N=2 stable post-v1.1).

## Sub-clause canonical body (the exact prose appended to critique.md Dim 9)

For Critic reviewability, the canonical body of the new 8th sub-clause is reproduced here. The actual append insertion point is `agents/critique.md` at the 7th-sub-clause-close ↔ `### Bonus: weak graph edges` H3 boundary.

```markdown
- **Shippability-catalog consumer-reference propagation** — N=2 sub-clause (slice-013 N=1 reactive-catch at /validate-slice Step 5.5 + slice-014 N=2 proactive-application at /build-slice Phase 4 pre-/validate-slice); peer cross-reference: none — operates at the cross-Phase consumer-reference-propagation discipline level, distinct from the meta-level recursive-self-application discipline and the Edit-discipline-level entry-pin-vs-PMI-1-gate semantics conflation above. When a slice supersedes a test function name in `tests/methodology/*.py` (via PMI-1 versioned-gate supersession, PMI-1 structural-invariant supersession applied at the structural-invariant level, or any other rename-driven supersession discipline) at /build-slice Phase 1, downstream consumers of that test function name in `architecture/shippability.md` (the catalog of critical-path commands run at /validate-slice pre-finish) carry stale references unless the same /build-slice block (before /validate-slice catalog run) explicitly propagates the rename across all consumer rows. Two distinct sub-modes:
  - **Reactive-catch mode** — at /build-slice Phase 1, a structural-invariant or versioned-gate test function is superseded; the /build-slice block (Phase 5 shippability.md updates or earlier) does NOT scan existing catalog rows for stale references to the deleted/renamed name; rows whose pytest commands still reference the deleted name FAIL at /validate-slice Step 5.5 catalog run; fixed in-line at validate-time. Concrete miss: slice-013 N=1 (Critic-MISSED at BOTH /critique AND /critique-review levels — neither first-Critic nor meta-Critic generalized the supersession-discipline → consumer-reference-propagation lesson to shippability.md). Phase 1f superseded `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` per PMI-1 structural-invariant supersession discipline applied at structural-invariant level; rows 6 + 11 pytest commands still referenced the deleted `_lists_six_sub_clauses`; BOTH rows FAILED at /validate-slice Step 5.5 catalog run; fixed in-line at validate-time by updating both rows' pytest commands.
  - **Proactive-application mode** — within the same /build-slice block as the supersession Edit and BEFORE the /validate-slice catalog run (typically Phase 4 or Phase 5 of the /build-slice plan, not necessarily the same numbered Phase as the supersession Edit itself), the slice authoring a supersession explicitly scans `architecture/shippability.md` for ANY rows referencing the deleted/renamed test name AND updates each row's pytest command in-line. Concrete catch: slice-014 N=2 (proactive — supersession Edit at Phase 1c; row 13 pytest command propagated from `_at_0_28_0` to `_invariant` at Phase 4 BEFORE running shippability catalog at /validate-slice; 14/14 PASS no regressions). The slice-013 reactive lesson was applied PROACTIVELY at slice-014 — **N=2 promotion threshold MET** (slice-013 reactive + slice-014 proactive across two consecutive cross-cutting-tooling slices).

  When reviewing a slice that supersedes any test function name in `tests/methodology/*.py` (PMI-1 versioned-gate, PMI-1 structural-invariant test, or any other rename-driven supersession), the Critic SHOULD: (1) require the design.md phase plan to enumerate the supersession Phase AND the shippability.md propagation Phase as distinct, named steps within the same /build-slice block; (2) require the propagation Phase to execute in the same /build-slice block as the supersession Edit and BEFORE the /validate-slice catalog run (not deferred to /validate-slice reactive time or "fixed-when-fails"); (3) require a pre-Phase empirical scan of `architecture/shippability.md` for ALL consumer references to the test name being superseded (mirrors slice-014 row 13 proactive scan); (4) flag absent or aspirational propagation plans as Major findings — the slice-013 reactive miss empirically demonstrated that Critic-stack layers 1 + 2 (first Critic + /critique-review meta-Critic) BOTH missed the lesson generalization to shippability.md, so codification at Dim 9 sub-class level is the canonical mitigation.
```

## Phase plan (informs /build-slice)

Detailed for the Critic + Builder. Annotated with where SCPD-1 self-application applies.

- **Phase 0** — sha256 forensic capture (baseline). Capture in-repo + installed sha256 for: `agents/critique.md`, `methodology-changelog.md`, `ai-sdlc-VERSION`. Captured in `build-log.md`.
- **Phase 1a** — Edit `agents/critique.md` at the 7th-sub-clause-close ↔ `### Bonus: weak graph edges` H3 boundary inserting the 8th sub-clause canonical body. Verify location-pin anchors unique at this stage.
- **Phase 1b** — INSERT new entry-pin function `test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed` in `tests/methodology/test_methodology_changelog.py` under a NEW dedicated SECTION header `# --- Slice-015 / SCPD-1 entry pinning ---`. **No PMI-1 versioned-gate supersession needed at slice-015** (PMI-1 v1.1 version-agnostic gate from slice-014 — body unchanged through atomic version bump). The new entry-pin SECTION header is placed near the v_0_29_0 entry-pin SECTION header per project convention (each version under its own dedicated SECTION header per slice-013 EPGD-1 + slice-014 N=2 stable). Also INSERT `test_adr_014_exists_and_names_scpd_1_canonical_phrase` (mirrors slice-014 ADR-013 pin).
- **Phase 1c** — N/A under PMI-1 v1.1 (versioned-gate retirement at slice-014). Atomic version bump steps continue at Phase 1d.
- **Phase 1d** — Atomic version bump: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all `0.29.0` → `0.30.0` in single commit. PMI-1 v1.1 audit clean post-edit (`python -m tools.plugin_manifest_audit --root .` exits 0; `test_plugin_yaml_version_matches_version_file_invariant` PASSES with ZERO test code modification — empirical retirement-proof N=1 → N=2 stable).
- **Phase 1e** — Append v0.30.0 entry to `methodology-changelog.md` (in-repo). Entry carries: `## v0.30.0 — 2026-05-13 — SCPD-1: Shippability-catalog consumer-reference propagation` heading + body documenting both sub-modes with slice-013 + slice-014 anchors + Limitations note acknowledging -D-suffix prose-heuristic semantics (no audit-enforced gate; v2 candidate if N=3+ recurrence post-codification).
- **Phase 1f** — Add 5 new test functions to `tests/methodology/test_critique_agent.py` (canonical-substring + location-pin + sub-mode names + cross-slice anchors + ≥2-of-4 substantive-discipline anchors). **Supersede `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`** per PMI-1 structural-invariant supersession discipline applied at structural-invariant level (delete old function, add new function — slice-011 N=1 + slice-013 N=2 → N=3 stable precedent; no two structural-invariant tests coexist). The mini-CAD-1 row 3 regression-guard test `_recursive_self_application_sub_clause_present` PASSING throughout (transitions PASSING → WRITTEN-FAILING → PASSING across Phase 1a → Phase 2 forward-sync — N=6 → N=7 stable).
- **Phase 2** — Forward-sync `agents/critique.md` + `methodology-changelog.md` to `~/.claude/`. CAD-1 audit clean post-sync (mini-CAD-1 row 3 transitions WRITTEN-FAILING → PASSING).
- **Phase 3** — Sub-build sanity: `pytest tests/methodology/test_critique_agent.py tests/methodology/test_methodology_changelog.py -q` PASS.
- **Phase 4** — Full methodology suite: `pytest tests/methodology/ -q` PASS. BC-1 self-application audit on slice-015's own mission-brief + design.md: expected `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` per BC-1 v1.3 9-of-9 over-determination + slice-013/014 N=11/N=12 stable pattern. Bidirectional sha256 forensic capture (post-edit) on `agents/critique.md` + `methodology-changelog.md`.
- **Phase 5** — Shippability catalog row 15 added + row 14 header updated. **SCPD-1 self-application** (slice's own ship is the canonical reference instance): empirically scan rows 1-14 for any pytest command referencing `_lists_seven_sub_clauses`; identified rows 6 + 11 + 13 carry stale references (per the slice-006 / slice-011 / slice-013 lineage); propagate the rename `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` in ALL 3 rows in THIS Phase 5 (NOT at /validate-slice reactive time). Phase 5 explicit step ordering: (a) scan with `grep -n "_lists_seven_sub_clauses" architecture/shippability.md` — expected: 3 hits at rows 6 + 11 + 13 pytest commands; (b) edit each row's pytest command in-line, updating ONLY the structural-invariant test ref `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` — **note (per /critique m2 ACCEPTED-FIXED)**: row 13 already carries `_invariant` from slice-014 Phase 4 propagation (slice-014 reflection.md L90) and row 13's pytest command references TWO tests (`_invariant` + `_lists_seven_sub_clauses`); slice-015 Phase 5 step (b) preserves `_invariant` and updates ONLY the structural-invariant ref on row 13; (c) re-scan with same grep — expected: 0 hits; (d) THEN append row 15.
- **Phase 6** — Pre-finish gates: TF-1 strict-pre-finish + PMI-1 v1.1 clean + CAD-1 clean + drift-check clean + SCPD-1 self-application empirical confirmation (post-Phase-5 grep returns 0 hits for `_lists_seven_sub_clauses` and 15+ hits for `_lists_eight_sub_clauses` across rows 6 + 11 + 13 + 15).

## Out-of-repo files touched

| File | Operation | Verification |
|------|-----------|--------------|
| `~/.claude/agents/critique.md` | Forward-sync from in-repo `agents/critique.md` post-edit | sha256 byte-equality via `tools/critique_agent_drift_audit.py` exit 0 |
| `~/.claude/methodology-changelog.md` | Forward-sync from in-repo `methodology-changelog.md` post-edit | sha256 byte-equality (Phase 4 forensic capture) |
| `~/.claude/ai-sdlc-VERSION` | Atomic bump from `0.29.0` to `0.30.0` (install-time rename of in-repo `VERSION`) | `python -m tools.plugin_manifest_audit --root .` exit 0 (PMI-1 v1.1 invariant — `test_plugin_yaml_version_matches_version_file_invariant` PASSES) |

Note (per slice-007 Critic B1 lesson + slice-009 CCC-1 v1.1 design-md-mechanical-tables canonical inventories sub-clause): in-repo file is `VERSION`; the install-time rename to `ai-sdlc-VERSION` happens via `INSTALL.md` Step 3f-equivalent. The "Out-of-repo files touched" table above names the INSTALLED filename `ai-sdlc-VERSION` per Dim 9 sub-clause 2's install-time-rename surface convention. `plugin.yaml` is NOT installed (on `INSTALL.md` Step 3f do-not-copy list per slice-006 DEVIATION-1 lesson); its `version` field is in-repo only.

## Pre-AC-lock empirical audits (per slice-009/010/011/012/013/014 discipline N=13 → N=14 stable)

These were run BEFORE the mission-brief ACs were locked. Documented for /critique to reference.

**Audit 1 — Location-pin anchor uniqueness** (slice-009 DEVIATION-2 + slice-010 + slice-013 anchor-uniqueness pre-emption pattern):

- Substring `Entry-pin-vs-PMI-1-gate semantics conflation` in `agents/critique.md` → exactly 1 occurrence (in 7th sub-clause title line). ✅ Unique anchor for the 7th-sub-clause-close-end boundary.
- Substring `### Bonus: weak graph edges` in `agents/critique.md` → exactly 1 occurrence (L180). ✅ Unique anchor.
- The location-pin test (AC #1 row 2) uses `text.find()` with verified-unique anchors; no first-occurrence-wins collision risk per slice-009 DEVIATION-2 lesson.

**Audit 2 — Canonical literal substring absence** (slice-010 / slice-013 absence-discipline pattern):

- Substring `Shippability-catalog consumer-reference propagation` in `agents/critique.md` → 0 occurrences (clean slate). ✅ Pre-fix, all 3 canonical-substring-pin tests (AC #1 + AC #2) genuinely FAIL with `AssertionError: '<phrase>' not in CRITIQUE` per TF-1 PENDING → WRITTEN-FAILING genuine-failure discipline N=11 stable.
- Substring `Reactive-catch mode` in `agents/critique.md` → 0 occurrences. ✅
- Substring `Proactive-application mode` in `agents/critique.md` → 0 occurrences. ✅

**Audit 3 — BC-1 self-application prediction** (slice-010 + slice-011 + slice-012 + slice-013 + slice-014 pattern N=10 stable; RSAD-1 build-time sub-mode):

- Slice-015's mission-brief + design.md + ADR-014 mention BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 positive anchors AS HISTORICAL CONTEXT for the SCPD-1 discipline. Per BC-1 v1.3's negative-anchor mechanism (slice-008 + slice-012): all 3 project-relevant rules carry the uniform 9-token methodology-vocabulary negative-anchor set (`defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`). At /build-slice Phase 4 BC-1 self-application, expected: `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` (all 3 silenced by 9-of-9 over-determination — slice-012/013/014 N=11/12/13 stable). The expectation pre-empts the slice-010 DEVIATION-3 build-time recursive-self-application sub-mode RSAD-1 codifies; slice-015 itself uses abstract anchor descriptions in the canonical critique.md body (per slice-011 Critic M1 stylistic / readability rationale + slice-010 DEVIATION-3 lesson) so the canonical `agents/critique.md` artifact is BC-1-clean at post-slice audits.

**Audit 4 — SCPD-1 self-application empirical pre-verification** (mirrors slice-012 Audit 6 + slice-013 Audit 4):

- Current `architecture/shippability.md` (post-slice-014 build) carries 14 rows. Empirical grep: `grep -n "_lists_seven_sub_clauses" architecture/shippability.md` returns 3 hits — rows 6, 11, 13 pytest commands (slice-006 + slice-011 + slice-013 lineage). At /build-slice Phase 1f, slice-015 supersedes `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` per PMI-1 structural-invariant supersession discipline applied at structural-invariant level. Post-Phase-1f structural-invariant test deletion: rows 6 + 11 + 13's pytest commands carry stale references — would FAIL at /validate-slice Step 5.5 catalog run (mirrors slice-013 N=1 reactive-catch class). **SCPD-1 self-application mitigation**: Phase 5 explicitly enumerates the 3-row propagation BEFORE the catalog run (mirrors slice-014 row 13 proactive-application class). Post-Phase-5 empirical confirmation: `grep -n "_lists_seven_sub_clauses" architecture/shippability.md` returns 0 hits; `grep -n "_lists_eight_sub_clauses" architecture/shippability.md` returns ≥3 hits (rows 6 + 11 + 13 + new row 15 if applicable).

**Audit 5 — Recursive self-application discipline self-check** (per RSAD-1 / slice-011 / slice-013):

The slice authoring SCPD-1 IS itself an instance of the discipline it encodes: at /build-slice Phase 1f, slice-015 supersedes a PMI-1 structural-invariant function (`_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`) — exactly the type of operation SCPD-1 governs. Slice-015's own ship is the canonical reference instance of SCPD-1 (mirrors slice-011's RSAD-1 self-application + slice-012's BC-PROJ-2-migration self-application + slice-013's EPGD-1 self-application + slice-014's EPGD-1 self-application at the discipline-retirement level). Audit 4 above empirically pre-verifies that slice-015's own Phase 1f + Phase 5 respect SCPD-1's same-Phase-propagation discipline. **Slice fails its own discipline at build time → SCPD-1's design-time pre-emption claim is empirically falsified at the very slice that codified it**. Critic SHOULD verify Audit 4's plan is concrete (not aspirational) — the /design-slice phase plan above specifies the exact grep command, the exact row numbers (6, 11, 13), and the exact propagation target (`_lists_eight_sub_clauses`).

**Audit 6 — EPGD-1 self-application N/A confirmation** (PMI-1 v1.1 version-agnostic gate from slice-014):

- Current `tests/methodology/test_methodology_changelog.py` (post-slice-014 build) carries 7 entry-pin functions (v_0_22_0..v_0_29_0) + 1 PMI-1 v1.1 version-agnostic gate `test_plugin_yaml_version_matches_version_file_invariant` (no version literal in body) + 2 AST meta-tests + 1 regression test. At /build-slice Phase 1b, slice-015 only ADDS entry-pin + ADR-pin functions; **no PMI-1 versioned-gate Edit is performed** (PMI-1 v1.1 gate body unchanged through atomic version bump per slice-014 retirement-proof). EPGD-1 self-application is therefore N/A at the PMI-1 versioned-gate level — only the PMI-1 structural-invariant supersession in test_critique_agent.py applies, where no entry-pin functions coexist (structural-invariant tests are sole occupants of their conceptual SECTION; no entry-pin-vs-gate confusion possible). All 7 prior entry-pin functions in test_methodology_changelog.py persist untouched post-Phase-1b empirically (no Edit operations on existing entry-pin function definitions).

**Audit 7 — RSAD-1 build-time-via-/critique-fix-prose sub-mode prediction**:

Per slice-010 DEVIATION-3 / slice-011 + slice-012 + slice-013 RSAD-1 design-time pre-emption pattern: if at /critique fix prose adds empirical-rebuttal anchor descriptions (e.g., literal BC-PROJ-1/2/GLOBAL-1 positive-anchor substrings or test function names with specific structural-invariant numbers), those substrings might trigger BC-1 audit or other audits at Phase 4 self-application. Mitigation per Audit 3: BC-1 v1.3 negative-anchor mechanism silences BC-PROJ-1/2/GLOBAL-1 on methodology-vocabulary slices; structural-invariant function-name substrings (`_lists_six_sub_clauses` / `_lists_seven_sub_clauses` / `_lists_eight_sub_clauses`) are not BC-1 positive anchors. No expected build-time recursive-self-application fire.

## Recursive self-application N=6 → N=7 cumulative

This slice (slice-015) is the **7th cumulative recursive-self-application instance** post-RSAD-1 codification:

- N=1 slice-009 M2 (design-time, pre-RSAD-1)
- N=2 slice-010 design-time stress-test B1+M1+B5 + build-time DEVIATION-3 (pre-RSAD-1)
- N=3 slice-011 (4 of 7 findings on own draft, post-RSAD-1)
- N=4 slice-012 (B1 on own draft: naive substring verification approach couldn't enforce its own data, post-RSAD-1)
- N=5 slice-013 (EPGD-1 discipline applies to slice-013's own Phase 1c PMI-1 supersession Edit; slice's own ship is canonical reference instance, post-RSAD-1)
- N=6 slice-014 (EPGD-1 discipline applies at the discipline-retirement level; slice authoring the supersession-pattern-retirement IS the canonical last application, post-RSAD-1)
- **N=7 slice-015 (this slice — the SCPD-1 discipline applies to slice-015's own Phase 1f PMI-1 structural-invariant supersession + Phase 5 shippability.md propagation; slice's own ship is the canonical reference instance of its own discipline; post-RSAD-1)**

The Critic at /critique SHOULD stress-test slice-015's design.md prose against SCPD-1 itself: does the Phase 5 plan above respect SCPD-1's same-Phase-propagation discipline? See Audit 4 + Audit 5 for the empirical pre-verification.
