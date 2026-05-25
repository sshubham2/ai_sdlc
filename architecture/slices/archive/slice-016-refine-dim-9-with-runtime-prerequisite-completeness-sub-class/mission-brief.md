# Slice 016: refine-dim-9-with-runtime-prerequisite-completeness-sub-class

**Mode**: Standard
**Estimated work**: 0.5 day (~30-45 min build + Critic + validate)
**Risk retired**: none direct from `architecture/risk-register.md` (R-1 + R-2 untouched); methodology evolution closes the /critic-calibrate 2026-05-13 (post-slice-015) accepted-proposal loop — codifies RPCD-1 as `agents/critique.md` Dimension 9 9th sub-clause `Runtime-prerequisite completeness on proposed fixes` (prompt edit already live + CAD-1 byte-equal verified; methodology-changelog + pin-tests + ADR + entry-pin remaining)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The /critic-calibrate 2026-05-13 (post-slice-015) run identified a DR-1 dual-review pattern reaching N=3 distinct-slice promotion threshold — first-Critic-MISS / meta-Critic-CATCH across slice-013 M-add-1 (sibling-test grep absent) + slice-014 M-add-1 (missing `import pytest` + `import ast`) + slice-015 M-add-1 (`WRITTEN-AS-EDIT` not in `_ALLOWED_STATUSES`). Proposal accepted; `agents/critique.md` Dimension 9 9th sub-clause was edited live and CAD-1-audited byte-equal across in-repo↔installed during the /critic-calibrate apply step. This slice formalizes the rule — methodology-changelog v0.31.0 + ADR-015 + pin-tests + entry-pin + plugin.yaml/VERSION/ai-sdlc-VERSION atomic version bump + shippability catalog row — mirroring the RSAD-1 (slice-011) / EPGD-1 (slice-013) / SCPD-1 (slice-015) Dim 9 sub-clause codification template. Rule-ID `RPCD-1` per -D-suffix convention N=3 stable (RSAD-1 + EPGD-1 + SCPD-1).

Slice-015 reflection flagged a **generic methodology recurrence at N=2 stable**: every future Dim 9 sub-clause append MUST tighten its predecessor's body-bound tests' end_anchors from `### Bonus: weak graph edges` to the new sub-clause's title. With RPCD-1 inserted between SCPD-1 close and the `### Bonus` H3 anchor, the slice-011 RSAD-1 body-bound test (`tests/methodology/test_critique_agent.py:173/177`) AND the slice-015 SCPD-1 body-bound test (`:304/308`) currently search a widened window that now includes RPCD-1 body — this slice closes that drift in-line.

## Acceptance criteria

1. `architecture/methodology-changelog.md` v0.31.0 entry codifies rule `RPCD-1: Runtime-prerequisite completeness on proposed fixes` with rule-text naming the three sub-modes (a) NEW-symbol import-audit (b) NEW-status/token allowlist-audit (c) NEW-anchor sibling-grep — and cross-slice anchors `["slice-013", "slice-014", "slice-015"]` strict-3-of-3 + substantive-discipline anchors covering the three sub-modes (e.g., `["import", "_ALLOWED_STATUSES", "sibling", "end_anchor"]` ≥3-of-4); methodology-changelog.md byte-equal in-repo↔installed at slice end (sha256 captured).
2. `plugin.yaml.version` 0.30.0 → 0.31.0 atomic with `VERSION` + `ai-sdlc-VERSION` (per META-1 atomicity + PMI-1 v1.1 invariant gate — zero test body modification on `test_plugin_yaml_version_matches_version_file_invariant`).
3. `architecture/decisions/ADR-015-promote-runtime-prerequisite-completeness-discipline-to-critique-dim-9-sub-clause.md` written: reversibility `cheap` with magnitude-of-revert justification ~13-15 sites (same class as ADR-010 / ADR-012 / ADR-014); supersedes: null; status: accepted.
4. `tests/methodology/test_critique_agent.py` updated: (a) PMI-1 structural-invariant supersession `test_critique_dim_9_lists_eight_sub_clauses` → `test_critique_dim_9_lists_nine_sub_clauses` per PMI-1 v1.1 structural-invariant supersession discipline (N=3 → N=4 stable); (b) **5 NEW body-bound tests** pinning RPCD-1 canonical anchors per N=3 stable `_sub_clause_present` + `_location_pinned` duality (slice-011 + slice-013 + slice-015 precedent; slice-016 → N=4 stable per slice-016 /critique-review M-add-1 ACCEPTED-FIXED): `_sub_clause_present` (bare-substring) + `_location_pinned` (scoped-find with `Shippability-catalog consumer-reference propagation` start_anchor + `### Bonus: weak graph edges` end_anchor) + `_names_three_sub_modes` + `_paragraph_cites_slice_013_014_015` (cross-slice 3-of-3 strict on `["slice-013", "slice-014", "slice-015"]`) + `_cites_substantive_discipline_anchors` (substantive-discipline ≥3-of-4); (c) end_anchor tighten Edits on the **three slice-015 SCPD-1 body-bound tests** — `test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes` (L519), `test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014` (L554), `test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors` (L594) — current end_anchor `### Bonus: weak graph edges` → `Runtime-prerequisite completeness on proposed fixes` (slice-013 + slice-015 precedent: `_location_pinned` siblings at L173 + L304 + L492 are NOT tightened — their `### Bonus:` end_anchor is structurally load-bearing); test_first audit `--strict-pre-finish` clean. Per slice-016 /critique B1 ACCEPTED-FIXED.
5. `tests/methodology/test_methodology_changelog.py` gains new SECTION header `# --- Slice-016 / RPCD-1 entry pinning ---` + entry-pin function `test_v_0_31_0_rpcd_1_entry_present_in_repo_and_installed` per EPGD-1 narrow-scope discipline (0 of 8 prior entry-pin functions touched); PMI-1 v1.1 invariant gate body unchanged; `architecture/shippability.md` catalog 15 → 16 rows (per SCPD-1 proactive-application mode — scan executed at design-time for any consumer of superseded `_lists_eight_sub_clauses` name BEFORE /validate-slice catalog run); all catalog rows PASS at /validate-slice Step 5.5.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0), each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology-pin | tests/methodology/test_methodology_changelog.py | test_v_0_31_0_rpcd_1_entry_present_in_repo_and_installed | PASSING |
| 1 | methodology-pin | tests/methodology/test_methodology_changelog.py | test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed | PASSING |
| 2 | methodology-pin | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |
| 3 | adr-pin | tests/methodology/test_methodology_changelog.py | test_adr_015_exists_and_names_rpcd_1_canonical_phrase | PASSING |
| 4 | structural-invariant | tests/methodology/test_critique_agent.py | test_critique_dim_9_lists_nine_sub_clauses | PASSING |
| 4 | body-bound | tests/methodology/test_critique_agent.py | test_critique_dim_9_runtime_prerequisite_completeness_sub_clause_present | PASSING |
| 4 | body-bound | tests/methodology/test_critique_agent.py | test_critique_dim_9_runtime_prerequisite_completeness_location_pinned | PASSING |
| 4 | body-bound | tests/methodology/test_critique_agent.py | test_critique_dim_9_runtime_prerequisite_completeness_names_three_sub_modes | PASSING |
| 4 | body-bound | tests/methodology/test_critique_agent.py | test_critique_dim_9_runtime_prerequisite_completeness_paragraph_cites_slice_013_014_015 | PASSING |
| 4 | body-bound | tests/methodology/test_critique_agent.py | test_critique_dim_9_runtime_prerequisite_completeness_cites_substantive_discipline_anchors | PASSING |
| 4 | end_anchor-tighten | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes | PASSING |
| 4 | end_anchor-tighten | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014 | PASSING |
| 4 | end_anchor-tighten | tests/methodology/test_critique_agent.py | test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors | PASSING |
| 5 | structural-invariant | tests/methodology/test_critique_agent.py | test_critique_dim_9_cross_references_resolve | PASSING |
| 5 | shippability-catalog | architecture/shippability.md (row 16) | row 16 catalog command runs 11 pytest commands enumerating slice-016 critical path (test_critique_dim_9_lists_nine_sub_clauses + 5 RPCD-1 body-bound tests + test_in_repo_and_installed_critique_agent_are_content_equal + test_v_0_31_0_rpcd_1_entry_present + test_v_0_31_0_rpcd_1_entry_names_three_sub_modes + test_adr_015_exists_and_names_rpcd_1_canonical_phrase + test_plugin_yaml_version_matches_version_file_invariant) | PASSING |

(Mini-CAD-1 row 3 transition: PMI-1 invariant gate transitions PASSING → WRITTEN-FAILING (after `VERSION` bump but before `plugin.yaml` bump) → PASSING (after atomic bump completes) — N=7 → N=8 stable per slice-007/009/010/011/012/013/015 precedent.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | methodology-changelog v0.31.0 entry + byte-equality | Grep both `architecture/methodology-changelog.md` (in-repo) and `~/.claude/plugins/cache/<github-user>/ai-sdlc/methodology-changelog.md` (installed) for the v0.31.0 entry + RPCD-1 rule-ID + three sub-modes; sha256 byte-equality check at slice end |
| 2 | atomic version bump | Inspect `plugin.yaml`, `VERSION`, `ai-sdlc-VERSION` all reading 0.31.0 in a single commit; `test_plugin_yaml_version_matches_version_file_invariant` PASSING |
| 3 | ADR-015 file existence + content | `ls architecture/decisions/ADR-015-*.md`; read for required sections (Status, Context, Decision, Cost summary, Reversibility, Supersedes); ADR-pin test (AC #3 row) PASSING |
| 4 | Pin-tests on `agents/critique.md` Dim 9 | `pytest tests/methodology/test_critique_agent.py -v` → all body-bound + structural-invariant tests PASSING; specifically `_lists_nine_sub_clauses` PASSING AND `_lists_eight_sub_clauses` (renamed) does NOT appear in file; CAD-1 audit `python -m tools.critique_agent_drift_audit` exit 0 |
| 5 | Entry-pin + shippability catalog row 16 | `grep "test_v_0_31_0_rpcd_1_entry_present"` in test_methodology_changelog.py + new SECTION header present; v0.22.0..v0.30.0 entry-pin functions ALL preserved (8 functions verified via AST scan post-Edit per EPGD-1 narrow-scope); shippability catalog has row 16 with `_lists_nine_sub_clauses` + RPCD-1 body-bound pytest commands; /validate-slice Step 5.5 reports all rows PASS |

## Must-not-defer

- [ ] **Atomicity (META-1)**: `plugin.yaml.version` + `VERSION` + `ai-sdlc-VERSION` bumped in a single commit; PMI-1 v1.1 invariant gate PASSING at slice end with ZERO test body modification (N=2 → N=3 stable retirement-proof)
- [ ] **EPGD-1 narrow-scope discipline**: Phase 1 entry-pin INSERT under NEW SECTION header `# --- Slice-016 / RPCD-1 entry pinning ---`; Phase 2 PMI-1 gate Edit (if needed) scoped to gate body only; 0 of 10 prior entry-pin functions touched (v0.22.0..v0.30.0 spans 9 minor versions; v0.29.0 carries 2 entry-pin functions per slice-014 (a)↔(b) duality — `test_v_0_29_0_pmi_1_v1_1_entry_present` + `test_v_0_29_0_entry_names_supersession_pattern_retired`) verified empirically at Phase 4 diff inspection. Per slice-016 /critique M2 ACCEPTED-FIXED.
- [ ] **SCPD-1 proactive-application mode**: scan `architecture/shippability.md` for ALL rows referencing `_lists_eight_sub_clauses` (the test function name being superseded at AC #4); propagate to `_lists_nine_sub_clauses` in same /build-slice block BEFORE /validate-slice catalog run (per SCPD-1 v0.30.0 codification — slice-016 is N=2 → N=3 stable post-codification reference instance)
- [ ] **RSAD-1 design-time discipline**: slice's own mission-brief + design.md + ADR-015 audited for own-draft commits of the same defect-class RPCD-1 codifies (e.g., do mission-brief/design.md commit symbols/statuses/anchors that this slice's own tooling wouldn't accept?); design-time audit recorded in design.md
- [ ] **Bidirectional sha256 forensic capture (META-2 + CAD-1)**: methodology-changelog.md AND agents/critique.md byte-equal in-repo↔installed at slice end with sha256 captured; CAD-1 audit (`python -m tools.critique_agent_drift_audit`) exit 0
- [ ] **N-surface schema-pin discipline**: canonical phrase `Runtime-prerequisite completeness on proposed fixes` pinned across 3 surfaces (ADR-015 + in-repo methodology-changelog.md v0.31.0 + installed methodology-changelog.md v0.31.0); N=4 → N=5 stable instances (RSAD-1 + EPGD-1 + PMI-1 v1.1 + SCPD-1 + RPCD-1)
- [ ] **End_anchor tighten discipline (slice-015 generic methodology recurrence N=2 → N=3 stable)**: every body-bound test currently pointing at `### Bonus: weak graph edges` as end_anchor is tightened to `Runtime-prerequisite completeness on proposed fixes` (slice-011 RSAD-1 body-bound test + slice-015 SCPD-1 body-bound test minimum; grep for all matches)
- [ ] **Validate-using-your-own-ship (META-3)**: this slice itself triggers MCT-1 (touches `agents/critique.md` + `methodology-changelog.md` + `tests/methodology/*.py` + `plugin.yaml`); `critic-required: true` auto-set; /critique runs; /critique-review (DR-1) runs given the slice IS the codification of an RPCD-1-class pattern (recursive-self-application probe for RPCD-1 sub-modes on slice-016's own design.md and ADR-015)
- [ ] **RPCD-1 self-application audit at design-time**: at /design-slice, audit the slice's own design.md + ADR-015 + mission-brief for (a) any NEW symbols introduced — verify imports; (b) any NEW status/token strings — verify allowlist membership; (c) any NEW end_anchors — grep for sibling-test conflicts (Audit 6 in design.md)
- [ ] **CCC-1 Dim 9 → Dim 1/4 cross-reference structural test PASSING**: `test_critique_dim_9_cross_references_resolve` PASSING at slice end (RPCD-1 body's `RSAD-1` + `SCPD-1` cross-references must resolve)
- [ ] **No new TODOs / FIXMEs / debug prints**

## Out of scope

- DR-1 dual-review pattern itself (continues as second-layer safety net; not retired by RPCD-1 codification — DR-1 catches remaining N=1 watch-list patterns and any 4th+ RPCD-1 sub-mode that emerges)
- `refine-dim-9-with-3-layer-critic-stack-accountability-sub-class` (N=1 watch-list; defer to N=2 promotion)
- `refine-dim-9-with-namespace-package-import-mode-sub-class` (N=1 watch-list; defer to N=2 promotion)
- VAL-1 v2 `[tool.pytest.ini_options]` testpaths auto-allow (deferred per slice-015 reflection — cumulative friction ~13s aggregate, below threshold)
- Open risk R-1 (cwd-mismatch for /diagnose) — stale since slice-001/002; needs `/repro` first if pursued
- `tools/rpcd_1_audit.py` standalone audit (no audit-tooling planned at codification time; RPCD-1 is prose-heuristic per -D-suffix convention; v2 candidate if audit-enforcement becomes warranted)

## Dependencies

- Prior slices:
  - [[slice-015-refine-dim-9-with-shippability-catalog-propagation-sub-class]] — the SCPD-1 body-bound test end_anchor tightened here was last set at slice-015 M1; canonical reference instance for the codification template
  - [[slice-014-refactor-pmi-1-gate-to-version-agnostic-shape]] — PMI-1 v1.1 invariant gate established here; this slice exercises retirement-proof N=2 → N=3 stable (third atomic version bump with zero gate body change)
  - [[slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class]] — EPGD-1 narrow-scope discipline established here; this slice exercises N=4 stable application
  - [[slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose]] — RSAD-1 body-bound test end_anchor (currently `### Bonus: weak graph edges`) tightened here
  - The DR-1 catches at slice-013/014/015 M-add-1 collectively form the N=3 evidence base for RPCD-1
- Vault refs:
  - [[components/agents-critique]] — Dim 9 9th sub-clause already edited live; CAD-1 verified byte-equal
  - [[methodology-changelog]] — v0.30.0 → v0.31.0 entry
  - [[architecture/critic-calibration-log]] — 2026-05-13 (post-slice-015) run already records ACCEPTED proposal; slice ratifies via methodology-changelog
  - [[shippability]] — catalog 15 → 16 rows
- Risk register: none (no new risks; methodology evolution closes the calibration loop)
- Methodology rules referenced: TF-1, PMI-1 v1.1, CCC-1, RSAD-1, EPGD-1, SCPD-1, RPCD-1 (newly codified), CAD-1, META-1, META-2, META-3, MCT-1, BC-1

## Mid-slice smoke gate

At ~50% of build (after methodology-changelog v0.31.0 entry written + atomic version bump done + pin-tests written-failing, BEFORE entry-pin / shippability propagation), run:

```
python -m tools.critique_agent_drift_audit
python -m tools.test_first_audit architecture/slices/slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class/mission-brief.md
pytest tests/methodology/test_critique_agent.py -v
pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant -v
```

Expected:
- CAD-1 exit 0 (byte-equal in-repo↔installed for `agents/critique.md`)
- TF-1 audit reports rows for AC #1-#5 with statuses progressing (some WRITTEN-FAILING, some PASSING)
- `test_critique_agent.py` body-bound tests reach WRITTEN-FAILING state on the renamed `_lists_nine_sub_clauses` + RPCD-1 canonical anchors tests (proof the new sub-clause IS pinned and the rename PMI-1-structural-invariant-supersedes the prior)
- PMI-1 invariant gate continues to PASS (zero-test-body-modification proof for atomic version bump)

If any fails: STOP, diagnose root cause, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed
- [ ] `python -m tools.test_first_audit --strict-pre-finish` clean (all TF-1 rows PASSING)
- [ ] `python -m tools.critique_agent_drift_audit` exit 0 (CAD-1 clean)
- [ ] `/drift-check` clean (vault ↔ code)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Shippability catalog row 16 PASSES at /validate-slice Step 5.5 + ALL prior rows continue to PASS (per SCPD-1 proactive-application — `_lists_eight_sub_clauses` references propagated to `_lists_nine_sub_clauses` BEFORE catalog run)
- [ ] methodology-changelog.md byte-equal in-repo↔installed (sha256 captured in validation.md)
- [ ] agents/critique.md byte-equal in-repo↔installed (sha256 captured in validation.md; should match the slice-016-start sha256 `f34c967eaaa34413...` unless further /critique fixes apply)
- [ ] N-surface schema-pin verified: canonical phrase pinned across 3 surfaces (ADR-015 + in-repo + installed methodology-changelog v0.31.0)
- [ ] PMI-1 v1.1 retirement-proof empirically verified at slice-016: ZERO modification to `test_plugin_yaml_version_matches_version_file_invariant` body since slice-014 (N=3 stable post-codification — atomic bump 0.30.0 → 0.31.0)
