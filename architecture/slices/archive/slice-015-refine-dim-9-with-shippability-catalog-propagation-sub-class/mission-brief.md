# Slice 015: refine-dim-9-with-shippability-catalog-propagation-sub-class

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: closes slice-013 N=1 Dim 9 sub-class candidate at N=2 promotion threshold (slice-013 reactive catch at /validate-slice Step 5.5 + slice-014 proactive same-Phase propagation pre-/validate-slice) — codifies the cross-cutting tooling-slice discipline as new 8th sub-clause in `agents/critique.md` Dim 9 (mirrors slice-009/011/013 Dim 9 sub-class refinement pattern). New rule-ID proposal: **SCPD-1** (Shippability-Catalog Propagation Discipline) — `-D` suffix per RSAD-1 / EPGD-1 calibration-trail convention (prose-heuristic discipline, no audit-enforced gate; design-slice may revise).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

When a cross-cutting tooling slice supersedes a test function name (e.g., `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` at slice-013; `_at_0_28_0` → `_invariant` at slice-014) per any structural-invariant or version-gate supersession discipline, the slice's `/build-slice` Phase MUST scan `architecture/shippability.md` for any existing catalog rows referencing the deleted/renamed test name AND propagate the rename in the SAME Phase as the supersession Edit. Slice-013 was the canonical reactive miss (Phase 1f superseded; Phase 5 missed propagation; both rows 6 + 11 failed at /validate-slice Step 5.5; fixed in-line). Slice-014 was the canonical proactive application (row 13 pytest command updated to reference `_invariant` BEFORE running shippability catalog). N=2 promotion threshold MET; codify into `agents/critique.md` Dim 9 8th sub-clause so future cross-cutting tooling slices catch this class at /critique-time.

## Acceptance criteria

1. `agents/critique.md` Dim 9 (Cross-cutting conformance) gains new 8th sub-clause `Shippability-catalog consumer-reference propagation` inserted between existing 7th sub-clause `Entry-pin-vs-PMI-1-gate semantics conflation` close and existing `### Bonus: weak graph edges` H3 anchor; the structural-invariant test in `tests/methodology/test_critique_agent.py` transitions 7→8 sub-clauses (mini-PMI-1-style structural-invariant supersession at the test level — `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`; per PMI-1 versioned-gate supersession discipline applied at structural-invariant level — slice-011 N=1 + slice-013 N=2 stable precedent).

2. The new 8th sub-clause body names BOTH sub-modes with explicit cross-slice anchors at N=2 cumulative evidence: (a) **Reactive-catch mode** — slice-013 N=1 build-time slip surfaced at /validate-slice Step 5.5 by shippability catalog rows 6 + 11 FAILING; fixed in-line at validate-time; Critic-MISSED at both /critique AND /critique-review levels; (b) **Proactive-application mode** — slice-014 N=2 design-time-pre-empted success at /build-slice Phase 4 (row 13 pytest command propagated from `_at_0_28_0` → `_invariant` BEFORE running shippability catalog at /validate-slice; 14/14 PASS no regressions). Both sub-modes pinned via dedicated prose-pin tests with formalized anchor lists (per /critique M2 ACCEPTED-FIXED — propagates design.md L8-10 formalization up to AC layer per slice-013 M2 mitigation precedent N=1 → **N=2 stable at slice-015**):
   - **Cross-slice anchors (strict-both)**: `["slice-013", "slice-014"]` — both MUST be present in the 8th sub-clause body
   - **Substantive-discipline anchors (≥2 of 4)**: `["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]` — at least 2 of these 4 MUST be present in the 8th sub-clause body (locked at /critique B1 ACCEPTED-FIXED per empirical substring verification against canonical body; original tuple `["Phase 5", "shippability catalog", "consumer reference", "rename propagation"]` was Blocker-rejected because 3 of 4 hyphenation-forms or absent — `shippability-catalog` / `consumer-reference` not space-separated; `rename propagation` literal never present)

   (Mirrors slice-011 RSAD-1 `_names_both_sub_modes` + `_cites_at_least_two_cross_slice_anchors` test shape and slice-013 EPGD-1 sub-mode + slice-anchor pin shape.)

3. `methodology-changelog.md` v0.30.0 / SCPD-1 entry present in-repo + installed with substantive canonical phrase `Shippability-catalog consumer-reference propagation` pinned across N=3 surfaces per slice-013 EPGD-1 3-surface precedent (agents/critique.md 8th sub-clause title + in-repo entry + installed entry); Limitations note per slice-011 B5 / slice-013 calibration-trail convention extension acknowledging `-D` suffix signals /build-slice + /validate-slice cross-Phase discipline heuristic with no audit-enforced gate; CAD-1 byte-equality on `agents/critique.md` preserved post-forward-sync (mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern N=6 → **N=7 stable**).

4. `architecture/decisions/ADR-014-codify-shippability-catalog-propagation-discipline.md` exists with reversibility classification (cheap, ~12-15 sites — mirrors ADR-010/012/013 magnitude class) + explicit magnitude-of-revert justification (per slice-013 ADR-012 + slice-014 ADR-013 magnitude-justification convention N=2 stable).

5. `plugin.yaml.version` + `VERSION` + installed `ai-sdlc-VERSION` atomic bump 0.29.0 → 0.30.0 (second version bump under PMI-1 v1.1 version-agnostic gate — first was slice-014's 0.28.0 → 0.29.0); PMI-1 v1.1 version-agnostic gate `test_plugin_yaml_version_matches_version_file_invariant` continues passing with ZERO test code modification (empirical retirement-proof N=1 → N=2 stable post-slice-014).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 pre-finish runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

Rows are split one-row-per-AC per slice-014 generic methodology lesson — TF-1 audit's first-integer-only AC parsing of multi-AC cells (N=1 at slice-014; flat-row-only convention until N=2 promotion).

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_lists_eight_sub_clauses | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_sub_clause_present | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_location_pinned | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | (Edit) test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes — tighten end_anchor `"### Bonus: weak graph edges"` → `"Shippability-catalog consumer-reference propagation"` per /critique M1 ACCEPTED-PENDING | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | (Edit) test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012 — tighten end_anchor `"### Bonus: weak graph edges"` → `"Shippability-catalog consumer-reference propagation"` per /critique M1 ACCEPTED-PENDING | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | (Edit) test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors — tighten end_anchor `"### Bonus: weak graph edges"` → `"Shippability-catalog consumer-reference propagation"` per /critique M1 ACCEPTED-PENDING | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014 | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors | PASSING |
| 3 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed | PASSING |
| 3 | unit | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_adr_014_exists_and_names_scpd_1_canonical_phrase | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |

TF-1 plan grew 10 → 13 rows per /critique M1 ACCEPTED-PENDING (3 WRITTEN-AS-EDIT rows tightening slice-013's body-bound test end_anchors from `"### Bonus: weak graph edges"` to `"Shippability-catalog consumer-reference propagation"` — exact slice-013 M1 + M-add-1 recurrence; canonical methodology lesson at slice-015 N=2 stable: EVERY future Dim 9 sub-clause append must tighten its predecessor's body-bound tests' end_anchors).

Mini-CAD-1 row 11 (above) is the row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern N=6 → N=7 stable: PASSES at /design-slice (pre-Phase-1), FAILS during Phase 1 (in-repo critique.md edited; installed copy stale), PASSES again at end of Phase 2 (forward-sync to `~/.claude/agents/critique.md`).

Row 13 (`test_plugin_yaml_version_matches_version_file_invariant`) is PASSING throughout — version-agnostic gate established at slice-014 PMI-1 v1.1 verifies the invariant continues to hold through Phase 3 atomic bump 0.29.0 → 0.30.0 with zero test code modification (slice-014 AC #5 empirical retirement-proof N=1 → N=2 stable).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | 8th sub-clause inserted at correct location; structural-invariant test transitioned 7→8 | `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_lists_eight_sub_clauses tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_sub_clause_present tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_location_pinned --no-header -q` returns 3/3 PASS |
| 2 | Both sub-modes named; cross-slice anchors at N=2 (slice-013 + slice-014) pinned | `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014 tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors --no-header -q` returns 3/3 PASS |
| 3 | v0.30.0 entry in-repo + installed; canonical phrase pinned across N=3 surfaces; CAD-1 byte-equality preserved | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal --no-header -q` returns 2/2 PASS; `sha256sum agents/critique.md ~/.claude/agents/critique.md` byte-equal |
| 4 | ADR-014 exists with canonical phrase + magnitude-justification | `pytest tests/methodology/test_methodology_changelog.py::test_adr_014_exists_and_names_scpd_1_canonical_phrase --no-header -q` returns 1/1 PASS; manual read confirms reversibility classification with sites enumerated |
| 5 | 0.29.0 → 0.30.0 atomic bump under PMI-1 v1.1 with zero test code modification | `pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant --no-header -q` returns 1/1 PASS; `git diff tests/methodology/` shows zero changes to PMI-1 gate function body between v0.29.0 ship and v0.30.0 ship (empirical retirement-proof N=2) |

## Must-not-defer

- [ ] Mini-CAD-1 row 3 transition PASSING → WRITTEN-FAILING → PASSING (Phase 1 in-repo edit then Phase 2 forward-sync — pattern N=6 → N=7 stable; row 3 catches forgotten Phase 2 forward-sync)
- [ ] **Slice-013 body-bound tests' end_anchors tightened** from `"### Bonus: weak graph edges"` to `"Shippability-catalog consumer-reference propagation"` on ALL 3 of `_names_both_sub_modes` + `_paragraph_cites_slice_011_and_012` + `_cites_at_least_two_cross_slice_anchors` (test_critique_agent.py:312/347/387) per /critique M1 ACCEPTED-PENDING — slice-013 M1 + M-add-1 generic methodology lesson N=2 stable at slice-015; EVERY future Dim 9 sub-clause append must apply this discipline
- [ ] N-surface schema-pin: canonical phrase `Shippability-catalog consumer-reference propagation` pinned across N=3 surfaces (agents/critique.md 8th sub-clause title + in-repo methodology-changelog entry + installed methodology-changelog entry) per slice-013 EPGD-1 3-surface precedent; **explicit post-Phase-5 grep verification** per /critique m1 ACCEPTED-PENDING: `grep -rn "Shippability-catalog consumer-reference propagation"` across `agents/critique.md` + `methodology-changelog.md` + `~/.claude/agents/critique.md` + `~/.claude/methodology-changelog.md` returns ≥4 hits (in-repo critique title + installed critique title + in-repo changelog entry + installed changelog entry)
- [ ] PMI-1 v1.1 version-agnostic gate continues passing through 0.29.0 → 0.30.0 atomic bump with ZERO test code modification (empirical retirement-proof N=2)
- [ ] EPGD-1 self-application: if any PMI-1 supersession Edit (no longer needed under v1.1 but if any entry-pin / structural-invariant supersession is done) — Phase 1c narrow-scope; 0 of N prior entry-pin functions touched empirically verified
- [ ] RSAD-1 self-application: slice's own draft stress-tested against the discipline being encoded — verify Phase 5 propagates `architecture/shippability.md` updates for the new row 15 add AND for any references to the superseded `_lists_seven_sub_clauses` structural-invariant test in existing rows (scan rows 6 + 11 + 13 for stale references)
- [ ] Bidirectional sha256 forensic capture: `agents/critique.md` + `methodology-changelog.md` byte-equal in-repo ↔ installed at slice end (N=10 → N=11 stable)
- [ ] CCC-1 v1.1 design.md mechanical tables vs canonical inventories: any mechanical table in design.md (e.g., "Out-of-repo files touched", "Forward-sync targets") must be cell-verifiable against canonical inventories (INST-1 `_CANONICAL_*` tuples + INSTALL.md Step 3f do-not-copy list + install-time-rename `VERSION`↔`ai-sdlc-VERSION`)
- [ ] BC-1 v1.3 negative-anchor migration self-application: slice's own mission-brief + design.md vocabulary may trigger BC-PROJ-1/BC-PROJ-2/BC-GLOBAL-1; expect negative-anchor final filter to silence (validate-using-your-own-ship N=12 → N=13 stable)
- [ ] /critique mandatory (MCT-1) — slice touches `agents/critique.md` + `methodology-changelog.md` + `tests/methodology/test_critique_agent.py` + `architecture/decisions/`; In-house methodology surfaces trigger fires (`agents/*.md` glob + `methodology-changelog.md` exact); `critic-required: true`
- [ ] /critique-review (DR-1) dual review per slice-013 + slice-014 N=2 stable post-codification: meta-Critic catches pattern-blindness on cross-cutting tooling slices
- [ ] No new TODOs / FIXMEs / debug prints; no `print(` statements introduced

## Out of scope

- Adding an audit-enforced gate for SCPD-1 (prose-heuristic discipline by design, per RSAD-1 + EPGD-1 -D-suffix precedent N=2 stable; tool-enforced shippability-propagation gate is a v2 candidate if N=3+ recurrence post-codification)
- Promoting watch-list N=1 Dim 9 sub-class candidates: `3-layer-critic-stack-accountability-lineage` (slice-014 N=1) + `pytest-namespace-package-import-mode-defeats-dotted-string-monkeypatch-target` (slice-014 N=1) — separate future slices when each hits N=2
- Refactoring `architecture/shippability.md` catalog schema (discipline operates on rename-propagation, not catalog schema)
- Promoting BC-1 v1.3 negative-anchor methodology-vocabulary token list (separate maintenance slice if N=3 false-positive class recurs post-slice-012)
- Running `/critic-calibrate` (next trigger: slice-021+ per Meta-Critic 2026-05-13 recommendation OR earlier if any watch-list N=1 hits N=3)
- Fixing VAL-1 Layer B intra-repo `tests` namespace via pytest testpaths (N=12 cumulative recurrence; deferred — friction trivial; separate QoL slice)

## Dependencies

- Prior slices: [[slice-009-refine-dim-9-with-design-md-tables-sub-clause]] (CCC-1 v1.1 — first Dim 9 sub-class refinement precedent), [[slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose]] (RSAD-1 — 6th sub-clause; -D suffix convention introduction; mini-CAD-1 row 3 transition pattern N=4), [[slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class]] (EPGD-1 — 7th sub-clause; reactive shippability propagation miss = N=1 evidence anchor), [[slice-014-refactor-pmi-1-gate-to-version-agnostic-shape]] (PMI-1 v1.1 version-agnostic gate baseline; proactive shippability propagation = N=2 evidence anchor)
- Vault refs: [[agents/critique.md]] (Dim 9 — 7 sub-clauses post-slice-013), [[methodology-changelog.md]] (v0.29.0 baseline; v0.30.0 entry slot), [[architecture/shippability.md]] (catalog with 14 rows post-slice-014; row 15 add target; rows 6 + 11 + 13 may reference structural-invariant test names), [[tests/methodology/test_critique_agent.py]] (structural-invariant + sub-clause prose-pin tests), [[architecture/decisions/]] (ADR-014 slot)
- Risk register: none retired by this slice (R-1 + R-2 about /diagnose; orthogonal)

## Mid-slice smoke gate

At ~50% of build (after Phase 1 — `agents/critique.md` Dim 9 8th sub-clause inserted + `tests/methodology/test_critique_agent.py` structural-invariant test transitioned 7→8 + new prose-pin tests written WRITTEN-FAILING then PASSING), run:

```bash
<HOME>/.claude/.venv/Scripts/python.exe -m pytest \
  tests/methodology/test_critique_agent.py::test_critique_dim_9_lists_eight_sub_clauses \
  tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_sub_clause_present \
  tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_location_pinned \
  tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes \
  tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014 \
  tests/methodology/test_critique_agent.py::test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors \
  --no-header -q
```

Expected: 6/6 PASS. If any FAIL: STOP, diagnose, don't continue. Specifically: if `_lists_eight_sub_clauses` fails, structural-invariant supersession Phase 1f Edit is wrong (mirrors slice-011 + slice-013 mini-PMI-1-style supersession). If `_location_pinned` fails, the 8th sub-clause was inserted at the wrong location (must be between 7th sub-clause close and `### Bonus: weak graph edges` H3 anchor). If `_names_both_sub_modes` fails, body is missing `Reactive-catch mode` or `Proactive-application mode` literal phrases.

Additionally, run mini-CAD-1 row 3 to confirm in-repo ↔ installed drift was introduced (expected FAIL pre-Phase-2):

```bash
<HOME>/.claude/.venv/Scripts/python.exe -m pytest \
  tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal \
  --no-header -q
```

Expected: 1/1 FAIL with byte-diff signature (mini-CAD-1 row 3 PASSING → WRITTEN-FAILING transition mid-Phase-1). This confirms Phase 2 forward-sync is still needed.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes (vault claims match code reality)
- [ ] `tools/test_first_audit.py --strict-pre-finish` accepts 13/13 TF-1 rows as PASSING (post-disposition count per /critique M1 + /critique-review M-add-1 ACCEPTED-FIXED — TF-1 plan grew 10 → 13 rows; the 3 slice-013 body-bound-test end_anchor-tightening rows carry status `PASSING` per /critique-review M-add-1 ACCEPTED-FIXED option (b) — `WRITTEN-AS-EDIT` was not in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist; reverted to `PASSING` matching slice-013 precedent + end_anchor tightening tracked in must-not-defer)
- [ ] Mid-slice smoke still passes (no regression after Phase 2 forward-sync + Phase 3 atomic bump)
- [ ] Mini-CAD-1 row 3 transitioned back to PASSING post-Phase-2 forward-sync
- [ ] Shippability catalog all 14 rows + new row 15 PASS in <2 min aggregate; rows 6 + 11 + 13 inspected for any structural-invariant test name references requiring propagation per the SCPD-1 discipline this slice authors (self-application of the new rule)
- [ ] Bidirectional sha256 forensic captured for both `agents/critique.md` AND `methodology-changelog.md` at slice end
- [ ] No new TODOs / FIXMEs / debug prints / `print(` statements introduced

## Next step

`/design-slice` — turn the mission brief into a just-enough spec. Specifically: lock the rule-ID (`SCPD-1` proposed; -D-suffix convention per RSAD-1/EPGD-1 N=2 stable; design-slice may revise), draw the 8th sub-clause body draft, plan the Phase 1 mini-PMI-1-style structural-invariant supersession (`_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`), enumerate the 3 N-surface canonical-phrase pin sites, and plan a pre-Phase-5 empirical scan of `architecture/shippability.md` rows for stale `_lists_seven_sub_clauses` references (self-application of the SCPD-1 discipline being encoded — RSAD-1 design-time stress-test pattern).
