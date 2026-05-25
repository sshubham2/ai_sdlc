# Build log: Slice 038 pin-shippability-runner-segment-contract

**Date**: 2026-05-17
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-17 00:00 BUILD: branch slice/038-pin-shippability-runner-segment-contract created from master (BRANCH-1); vault gitignored, tree clean
- 2026-05-17 00:01 BUILD: CRP-1 prereq clean; plan approved by user (incl. AC5 TF-1-row correction — dropped risk_register repro row, remapped AC5→AC2 catalogued runner test)
- 2026-05-17 00:02 DEVIATION: B1 applied-fix said add runner to _POSITIONAL_SLICE_TOOLS — WRONG (that list passes a slice-folder arg; runner takes a catalog path). Siblings shippability_path_audit/decoupling_audit are NOT in that list — they use a bespoke cp1252 test feeding covered_set via mechanism (ii). Corrected T3 to sibling precedent; B1 intent (runner ∈ covered_set, parity holds) preserved. Conformance-strengthening, well-precedented, no re-critique.
- 2026-05-17 00:10 BUILD: T1 tools/shippability_runner.py created (reuses SCMD-1 _segments/_catalog_rows/_machine_cmd_cell; exit 0/1/2; --json); import+CLI OK
- 2026-05-17 00:14 TEST: T2 test_shippability_runner_segment_contract.py 3/3 PASS (incl. load-bearing naive-strip-vs-_segments contrast on real row #28)
- 2026-05-17 00:18 TEST: T3 UTF8-STDOUT-1 bespoke test added (sibling precedent, NOT _POSITIONAL_SLICE_TOOLS); 27/27 utf8 tests PASS; utf8_stdout_audit 23/23 clean
- 2026-05-17 00:22 SMOKE: mid-slice gate PASS — new runner ran real catalog 37/37 rows PASS, row #28 (lone multi-segment, R-8 target) PASS, no WinError 2
- 2026-05-17 00:30 BUILD: T5 SKILL.md Step 5.5 repoint (+installed); methodology-changelog v0.51.0 SRSC-1 entry (+installed); 4-part PMI-1 bump VERSION+ai-sdlc-VERSION+plugin.yaml:15 → 0.51.0
- 2026-05-17 00:36 BUILD: T6 paired SRSC-1 changelog tests (_V051/_SRSC1_PHRASE + entry_present content-pin + shippability_consumer_propagation); dual enumeration install_audit._CANONICAL_TOOLS + plugin.yaml
- 2026-05-17 00:40 BUILD: T7 shippability row #38 appended (single-segment, real ::selectors); R-8 → retired in risk-register.md (slice-038 + ADR-039)
- 2026-05-17 00:44 BUILD: AC#3 SKILL.md content-pin test added (test_validate_slice_skill_pins_runner_invocation, in-repo+installed); TF-1 plan +AC3 row, all 8 rows → PASSING
- 2026-05-17 00:50 TEST: pre-finish audits all green — TF-1 8/8 PASSING, BRANCH-1, CRP-1, PCA-1, BCI-1, SCMD-1, WIRE-1, UTF8-STDOUT-1, PMI-1 (v0.51.0 23 tools), INST-1 (v0.51.0), BC-1 (no Critical), mock-budget (0)
- 2026-05-17 00:54 SMOKE: SRSC-1 dogfood — new runner ran full real 38-row catalog 38/38 PASS, 0 FAIL (incl. new row #38, recursion handled)
- 2026-05-17 00:56 TEST: /drift-check CLEAN (0 blockers, 0 majors — all slice-038 vault claims verify against code)

## Summary

### Plan executed
1. ✅ `tools/shippability_runner.py` created — reuses SCMD-1 `_segments`/`_catalog_rows`/`_machine_cmd_cell` (object-identity verified), per-row per-segment subprocess exec from repo root, exit 0/1/2, `--json`.
2. ✅ `tests/methodology/test_shippability_runner_segment_contract.py` — 4 tests incl. the load-bearing `test_naive_outer_strip_runner_is_rejected` (naive-outer-strip-vs-`_segments()` contrast on REAL row #28; both branches exercised) + AC3 SKILL.md content-pin.
3. ✅ UTF8-STDOUT-1 propagation — bespoke `test_shippability_runner_survives_cp1252_with_u2192` (sibling precedent; corrected from the B1 `_POSITIONAL_SLICE_TOOLS` instruction). `discovered==covered` parity holds; audit 23/23.
4. ✅ Mid-slice smoke gate PASS (37/37, row #28 PASS).
5. ✅ SKILL.md Step 5.5 repoint + no-hand-roll/reuse pins (+installed forward-sync); methodology-changelog v0.51.0 SRSC-1 (+installed); 4-part PMI-1 bump.
6. ✅ Paired SRSC-1 changelog tests (content-pin + SCPD-1 propagation); dual enumeration (install_audit `_CANONICAL_TOOLS` + plugin.yaml).
7. ✅ Shippability row #38; R-8 → retired; full pre-finish gate.

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `$PY -m tools.shippability_runner architecture/shippability.md` → 37/37 rows PASS (pre-row-#38), row #28 (lone multi-segment, R-8 target) PASS, no WinError 2.

### Pre-finish gate
- [x] All ACs pass with evidence — TF-1 8/8 PASSING; load-bearing contract test + SRSC-1 dogfood (38/38)
- [x] Must-not-defer addressed — contract CONSUMED by SKILL.md invocation; regression catalogued (row #38); tool on plugin.yaml + install_audit; negative fixture load-bearing (not tautological); changelog forward-synced + 4-part PMI-1
- [x] /drift-check pass — CLEAN
- [x] Smoke regression check pass — full catalog 38/38 via new runner
- [x] No debug code / TODO / FIXME
- [x] All Step 6 audits green — TF-1, BRANCH-1, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, PMI-1, INST-1, BC-1, WIRE-1, SCMD-1, mock-budget

### Deferrals
- (none)

### Design deviations
- B1 applied-fix specified `_POSITIONAL_SLICE_TOOLS` membership for the runner — corrected at build to the catalog-path-tool sibling precedent (bespoke cp1252 test feeding covered_set via ADR-026 mechanism (ii)), because `_POSITIONAL_SLICE_TOOLS` passes a slice-folder arg a catalog-path tool cannot consume. B1 intent (runner ∈ covered_set; `discovered==covered` parity preserved) fully met. Conformance-strengthening, well-precedented (path_audit/decoupling_audit do exactly this); no re-critique needed. Updated in design.md? No — design.md §What's new still cites `_POSITIONAL_SLICE_TOOLS`; the deviation is recorded here + will be captured in /reflect (the design's *intent* — runner in covered_set — held; only the mechanism corrected).
- AC5 TF-1 row corrected (plan-mode, user-ratified): dropped `test_risk_register_audit.py::test_repro_r8_retired_with_slice_and_adr` (R-8 is a runner-contract risk, not an audit-behavior bug; such a test = environment-fragile vault bookkeeping). AC5 remapped to the AC2 catalogued runner-contract test. R-8 retirement = vault bookkeeping + changelog/ADR cite (mirrors slices 033/034). Updated in mission-brief? Yes (TF-1 plan + HTML-comment rationale).

### Files changed
- Created: `tools/shippability_runner.py`, `tests/methodology/test_shippability_runner_segment_contract.py`
- Modified (tracked): `tests/methodology/test_utf8_stdout_regression.py`, `tests/methodology/test_methodology_changelog.py`, `skills/validate-slice/SKILL.md`, `methodology-changelog.md`, `plugin.yaml`, `tools/install_audit.py`, `VERSION`
- Modified (installed, forward-sync): `~/.claude/skills/validate-slice/SKILL.md`, `~/.claude/methodology-changelog.md`, `~/.claude/ai-sdlc-VERSION`
- Modified (gitignored vault): `architecture/shippability.md` (row #38), `architecture/risk-register.md` (R-8 retired), `architecture/drift-log.md`, slice-038 vault artifacts
