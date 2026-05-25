# Validation: Slice 013 refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class

**Date**: 2026-05-13
**Result**: PASS (with 1 implementation-bug discovery + in-line fix at Step 5.5)

## Per-criterion results

### AC #1: 7th sub-clause present + structural-invariant supersession + location pin + regression-guard

- **Status**: PASS
- **Evidence**:
  ```
  pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_lists_seven_sub_clauses \
                ::test_critique_dim_9_entry_pin_vs_pmi_1_gate_sub_clause_present \
                ::test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned \
                ::test_critique_dim_9_recursive_self_application_sub_clause_present \
  → 4 passed in 0.03s
  ```
- **Notes**: All 7 sub-clause titles asserted by `_lists_seven_sub_clauses` (Methodology-audit conformance, Tooling-doc-vs-implementation parity, Algorithm-path-conformance, Runtime-environment, Language-version conformance, Recursive self-application discipline, Entry-pin-vs-PMI-1-gate semantics conflation). Mini-CAD-1 row 3 regression-guard (`_recursive_self_application_sub_clause_present` — slice-011's 6th-sub-clause-substring-pin) PASSING throughout. Structural-invariant supersession `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` confirmed clean (no two structural-invariant tests coexist).

### AC #2: Strict-both cross-slice anchors + ≥2-of-4 substantive-discipline anchors + M1/M-add-1 narrow-scope edits

- **Status**: PASS
- **Evidence**:
  ```
  pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012 \
                ::test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors \
                ::test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors \
                ::test_critique_dim_9_recursive_self_application_names_both_sub_modes \
                ::test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes \
  → 5 passed in 0.03s
  ```
- **Notes**: M1 + M-add-1 narrow-scope end_anchor tighten VALIDATED at both pre-7th-sub-clause append (slice-011 `_names_both_sub_modes` + `_cites_at_least_two_cross_slice_anchors` with `end_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"` — scopes 6th sub-clause body cleanly) AND post-append (new slice-013 symmetric `_names_both_sub_modes` + `_cites_at_least_two_cross_slice_anchors` with `end_anchor = "### Bonus: weak graph edges"` — scopes 7th sub-clause body cleanly). M2 anchor list formalization (strict-both + ≥2-of-4) operates on 7th sub-clause body per design.md "What's new" formalization.

### AC #3: CAD-1 byte-equality

- **Status**: PASS
- **Evidence**:
  ```
  $PY -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude
  → CAD-1: clean - agents/critique.md byte-equal across in-repo (agents\critique.md) and installed (<HOME>\.claude\agents\critique.md); sha256: 0346d39ef988fa61...
  → exit=0

  pytest tests/methodology/test_critique_agent_drift.py
  → 5 passed in 0.78s
  ```
- **Notes**: CAD-1 audit clean. Bidirectional sha256 forensic capture N=9 stable (baseline `2EC35939576CDEB0` → post-edit `0346D39EF988FA61` byte-equal in-repo↔installed; Phase 0 + Phase 4 forensic captures recorded in build-log.md Events).

### AC #4: methodology-changelog.md v0.28.0 entry — 3-pin shape bidirectional + N=3 surfaces

- **Status**: PASS
- **Evidence**:
  ```
  pytest tests/methodology/test_methodology_changelog.py::test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed
  → 1 passed in 0.04s
  ```
- **Notes**: 3-pin shape verified bidirectionally (`## v0.28.0` heading + `EPGD-1` rule-ID + substantive canonical phrase `Entry-pin-vs-PMI-1-gate semantics conflation`). N=3 surfaces (agents/critique.md Dim 9 7th sub-clause title + in-repo methodology-changelog.md v0.28.0 entry + installed ~/.claude/methodology-changelog.md v0.28.0 entry). N=2 instances stable at slice-013 (slice-011 RSAD-1 3-surface pin + slice-013 EPGD-1 3-surface pin).

### AC #5: PMI-1 atomic at 0.28.0 + EPGD-1 self-application empirical confirmation

- **Status**: PASS
- **Evidence**:
  ```
  pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_at_0_28_0
  → 1 passed in 0.05s

  $PY -m tools.plugin_manifest_audit --root .
  → PMI-1 plugin manifest audit: clean. 24 skill(s), 5 agent(s), 15 tool(s); version 0.28.0.

  pytest tests/methodology/test_methodology_changelog.py -k "v_0_2 and entry_present or version_matches"
  → 9 passed in 0.05s
  ```
  Per-test breakdown of EPGD-1 self-application empirical confirmation:
  ```
  test_v_0_22_0_cad_1_entry_present_in_repo_and_installed       PASSED  ✅ (untouched)
  test_v_0_23_0_bc_1_v_1_2_entry_present_in_repo_and_installed  PASSED  ✅ (untouched)
  test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed PASSED  ✅ (untouched)
  test_v_0_25_0_mct_1_entry_present_in_repo_and_installed       PASSED  ✅ (untouched)
  test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed      PASSED  ✅ (untouched)
  test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed   PASSED  ✅ (untouched)
  test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed      PASSED  ✅ (new at slice-013)
  test_plugin_yaml_version_matches_version_file_at_0_28_0       PASSED  ✅ (new at slice-013; supersedes _at_0_27_0)
  test_version_matches_most_recent_changelog_entry              PASSED  ✅
  ```
- **Notes**: **EPGD-1 self-application EMPIRICALLY VALIDATED at /build-slice + /validate-slice**. 7 entry-pin functions present (v_0_22_0..v_0_28_0); exactly 1 PMI-1 versioned-gate (`_at_0_28_0`); **0 of 6 prior entry-pin functions touched by Phase 1c narrow-scope Edit** (the very EPGD-1 discipline this slice authors). Slice-013 IS the canonical reference instance of the discipline it authors (recursive-self-application N=5 cumulative post-RSAD-1 codification at slice-011). PMI-1 versioned-gate supersession N=6 events stable post-slice-013 (slice-007 introduced → slice-008..013 superseded).

## Multi-instance validation

**Required?**: no (slice is methodology prose + canonical changelog entry + version bump; no runtime multi-device / multi-user / sync surfaces)
**Result**: not-applicable
**Evidence**: Slice modifies prose content in canonical methodology files (`agents/critique.md`, `methodology-changelog.md`) and atomically-versioned manifest files (`VERSION`, `ai-sdlc-VERSION`, `plugin.yaml`). No API endpoints, events, external integrations, or authorization paths introduced (design.md L67-69, L77-81, L87-89 + ADR-012 explicit). The "two-surface" bidirectional pin (in-repo + installed mirrors) is verified by CAD-1 + entry-pin bidirectional tests, not multi-instance runtime validation.

## VAL-1 layered safety checks (Step 5b)

- **Layer A — Credential scan**: ✅ clean (0 secrets in changed files)
- **Layer B — Dependency hallucination check**: ✅ clean (0 hallucinated imports with `--imports-allowlist tests` handling N=11 cumulative intra-repo `tests` package false-positive class)
- **Command**: `$PY -m tools.validate_slice_layers --slice architecture/slices/slice-013-... --changed-files agents/critique.md methodology-changelog.md tests/methodology/test_critique_agent.py tests/methodology/test_methodology_changelog.py VERSION plugin.yaml --imports-allowlist tests`
- **Output**: `VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted). Clean — both layers passed.`

**VAL-1 Layer B intra-repo `tests` package false-positive class N=11 cumulative recurrence** (was N=10 at slice-012; ratchets stable). Handled cleanly via `--imports-allowlist tests`. v2 candidate `[tool.pytest.ini_options]` testpaths auto-allow still deferred — cumulative friction ~1 sec per slice; not yet at meaningful threshold for promotion.

## Shippability catalog regression check (Step 5.5)

**Result**: 13 rows / **all PASS post-fix** — 1 implementation-bug discovery surfaced + fixed in-line at validate-time.

| # | Slice | Status | Runtime |
|---|-------|--------|---------|
| 1 | slice-001 /diagnose orchestration | ✅ 30/30 PASS | 1.77s |
| 2 | slice-002 risk-register + diagnose contract | ✅ 4/4 PASS | 0.04s |
| 3 | slice-003 VAL-1 Layer B | ✅ 3/3 PASS | 0.05s |
| 4 | slice-004 RR-1 | ✅ 4/4 PASS | 0.04s |
| 5 | slice-005 BC-1 keyword precision | ✅ 5/5 PASS | 0.08s |
| 6 | slice-006 9 dimensions | ⚠️ **FAIL initially → ✅ 8/8 PASS post-fix** | 0.06s |
| 7 | slice-007 CAD-1 | ✅ 7/7 PASS | 0.82s |
| 8 | slice-008 BC-1 v1.2 | ✅ 10/10 PASS | 0.13s |
| 9 | slice-009 CCC-1 v1.1 | ✅ 5/5 PASS | 0.18s |
| 10 | slice-010 MCT-1 | ✅ 7/7 PASS | 0.06s |
| 11 | slice-011 RSAD-1 | ⚠️ **FAIL initially → ✅ 7/7 PASS post-fix** | 0.18s |
| 12 | slice-012 BC-PROJ-2 | ✅ 5/5 PASS | 0.09s |
| 13 | slice-013 EPGD-1 | ✅ 9/9 PASS | 0.19s |

**Total**: 84/84 tests pass post-fix in ~3.85s aggregate (well under 2-min target).

### Shippability regressions (in-line fixed at validate-time)

**REGRESSION #1**: Row 6 (`slice-006`) — `tests/methodology/test_critique_agent.py::test_critique_dim_9_lists_six_sub_clauses` not found
- **Pre-fix output**: `ERROR: not found: ...test_critique_dim_9_lists_six_sub_clauses (no match in any of [<Module test_critique_agent.py>])`
- **Cause**: Implementation bug (consumer-reference propagation slip) — slice-013 Phase 1f superseded the structural-invariant test `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` per PMI-1 versioned-gate supersession discipline applied at the structural-invariant level (N=2 stable: slice-011 N=1 + slice-013 N=2), but Phase 5 (`shippability.md` updates) added row 13 + updated row 12 header WITHOUT propagating the rename to row 6's pytest command. Row 6 still referenced the deleted test name.
- **Fix applied at validate-time**: row 6's command + row 6's header updated. Command's `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` (subsumes slice-011's 6-sub-clause assertion by asserting all 7 titles including the 6th `Recursive self-application discipline`). Row 6's header noted "slice-013 second-superseded `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` at slice-013 row 13 — N=2 stable structural-invariant supersession events".

**REGRESSION #2**: Row 11 (`slice-011`) — same defect class as REGRESSION #1
- **Pre-fix**: Row 11's pytest command referenced `test_critique_dim_9_lists_six_sub_clauses` (slice-011's critical-path test, now superseded)
- **Cause**: Same implementation bug class as REGRESSION #1
- **Fix applied at validate-time**: row 11's command's `_lists_six_sub_clauses` → `_lists_seven_sub_clauses`; row 11's header noted slice-013 supersession discipline applied at structural-invariant level

### Classification of regression class

These are sibling defect class to EPGD-1 (which targets PMI-1 versioned-gate Edits in `test_methodology_changelog.py`). The shippability-catalog version concerns **consumer-reference propagation after PMI-1 structural-invariant supersessions**. Distinct from EPGD-1 in two ways: (1) the surface is `architecture/shippability.md` not `tests/methodology/test_methodology_changelog.py`; (2) the discipline is rename-propagation across rows that reference the superseded test name, not Edit-scoping at the supersession site itself.

**N=1 cumulative evidence post-slice-013** for the new sub-class candidate. Slice-011 successfully propagated `_lists_five_sub_clauses` → `_lists_six_sub_clauses` at row 6 during its own build (verified by slice-011 + slice-012 validate-time runs not failing on row 6). Slice-013 is the N=1 case where this propagation was MISSED — caught at /validate-slice Step 5.5 by row 6 + row 11 failures.

**Critic MISS classification at slice-cycle level**: this defect class was MISSED at both /critique (first Critic) AND /critique-review (meta-Critic). Both passes focused on the test_critique_agent.py + test_methodology_changelog.py + EPGD-1 Edit-scoping discipline; neither generalized the "supersession → consumer-reference-propagation" lesson to shippability.md. The first Critic's M1 + M-add-1 caught the analogous body-bound widening defect class on slice-011's test bodies; the meta-Critic's M-add-1 generalized it across siblings — but neither generalized FURTHER to the shippability catalog surface.

**Calibration observation logged for /critic-calibrate at slice-014**: candidate Dim 9 sub-class refinement at N=1 (promote at N=2 if recurs): **"PMI-1 structural-invariant supersession requires consumer-reference propagation across ALL surfaces, not just the test file — at minimum: shippability.md rows referencing the superseded test name"**. Distinct from EPGD-1 (which is Edit-scope discipline at the supersession site) and distinct from M1/M-add-1 (which is body-bound test scoping). New sub-class triple stacked at slice-013 evidence base.

## Reality surprises

1. **Consumer-reference propagation slip for PMI-1 structural-invariant supersessions surfaces ONLY at /validate-slice Step 5.5** — neither the methodology pytest suite nor the pre-finish gates (TF-1 / PMI-1 / CAD-1 / WIRE-1 / TRI-1 / DR-1 / mock-budget / BC-1) catch the stale test-name reference in shippability.md row commands, because none of those audits parse `shippability.md` to execute its row commands. The shippability catalog regression check is structurally the ONLY layer that catches this class.

2. **Defense-in-depth proven**: 4-layer Critic stack at slice-013 — first Critic + meta-Critic + slice's own design-stage audits + validate-slice shippability catalog — found 8 total catches at slice-013 (7 first-Critic findings ratified VALID + 1 meta-Critic missed-finding M-add-1 + 1 validate-time shippability regression discovery + in-line fix). All caught BEFORE /reflect. **First instance in the project of THREE defect classes caught in a single slice across all 4 layers, including validate-time as the final-line-of-defense layer**.

3. **Confirmation of /critic-calibrate urgency at slice-014**: cumulative cross-cutting Critic misses at slice-013 = 11 across slices 6-13 (was 10 at slice-012; slice-013 adds 1 — the shippability-propagation slip). 2 slices remaining in the slice-006-15 window. Target ≤2 across slices 6-15 is now significantly missed (5.5× target). /critic-calibrate at slice-014 boundary is mandatory.
