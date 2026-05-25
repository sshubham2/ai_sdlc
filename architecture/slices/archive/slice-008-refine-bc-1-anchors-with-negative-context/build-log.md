# Build log: Slice 008 refine-bc-1-anchors-with-negative-context

**Date**: 2026-05-10
**Result**: SHIPPED

## Events (append-only)

- 2026-05-10 T0 BUILD: Phase 0 pre-build sha256 captured: build-checks.md (in-repo) C7B5CBD58DD507E4; build_checks_audit.py 5050C4C5C6F6D4D6; test_build_checks_audit.py 2DA0E2FCC7E2ADFC; methodology-changelog.md (in-repo + installed) FD6BBC0241F03396 byte-equal; VERSION + ai-sdlc-VERSION 464863EE696CA862 byte-equal; plugin.yaml 8668135572777C30; ~/.claude/build-checks.md C62E7F94102D1DBE
- 2026-05-10 T0 TEST: PMI-1 audit clean (exit 0; 24 skills, 5 agents, 15 tools, version 0.22.0)
- 2026-05-10 T0 BUILD: pre-slice in-repo VERSION = installed ai-sdlc-VERSION = plugin.yaml.version = 0.22.0 (PMI-1 invariant clean)
- 2026-05-10 T1 TEST: 9/9 new TF-1 tests RED with genuine signatures: 3× AssertionError "BC-PROJ-1 in applicable" (slice-005/006/007 archive backtests via kw + glob paths); 2× AttributeError "negative_anchors" (AC #4 + migration-tuple — pre-fix dataclass missing field); 2× AssertionError schema-substring absent (`Negative anchors` field-name + `final filter` semantics); 1× AssertionError "BC-PROJ-99 in applicable" (always-true + negative-anchor synthetic fixture); 1× AssertionError "0 violations" (negative-anchor-overlaps-positive parse-violation channel). All non-coincidental. WRITTEN-FAILING genuineness confirmed for all 9 rows.
- 2026-05-10 T2 BUILD: tools/build_checks_audit.py modified — `BuildCheckRule.negative_anchors` field added; `to_dict` extended; `_parse_rules` reads `Negative anchors:` field + emits `negative-anchor-overlaps-positive` violations on overlap with trigger_keywords / trigger_anchors; `_negative_anchor_match` helper added (case-insensitive word-boundary regex); `_rule_applies` refactored — every positive-applicability return wrapped with `not _negative_anchor_match(...)` (uniform composition across always-true / glob / keyword paths); module docstring updated for v1.2 negative-context semantic.
- 2026-05-10 T3 BUILD: architecture/build-checks.md updated — schema-prelude TWO sentences added (`Negative anchors:` field doc + `final filter` semantics); BC-PROJ-1 gets `Negative anchors: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`. BC-PROJ-2 NOT migrated per Critic M1.
- 2026-05-10 T4 BUILD: ~/.claude/build-checks.md updated — schema-prelude TWO sentences + cross-project-applicability sentence (per Critic m1) added; BC-GLOBAL-1 gets same 9-token negative-anchor list.
- 2026-05-10 T5 SMOKE: mid-slice smoke gate PASS. slice-007 archive (--changed-files agents/critique.md skills/critic-calibrate/SKILL.md): applicable=[], skipped=[BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1], violations=0. slice-001 archive (--changed-files skills/diagnose/SKILL.md ...): applicable=[BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1] still fires (backward-compat preserved). 
- 2026-05-10 T5 TEST: 9/9 new TF-1 tests GREEN (PENDING -> WRITTEN-FAILING -> PASSING transitions complete). 0.12s.
- 2026-05-10 T6 BUILD: VERSION 0.22.0 -> 0.23.0; ~/.claude/ai-sdlc-VERSION 0.22.0 -> 0.23.0; plugin.yaml.version 0.22.0 -> 0.23.0 (atomic per slice-007 PMI-1 closure pattern).
- 2026-05-10 T7 BUILD: methodology-changelog.md v0.23.0 / BC-1 v1.2 entry appended in-repo; forward-synced to ~/.claude/methodology-changelog.md; sha256 0A7AA6CA04E372FB byte-equal both sides.
- 2026-05-10 T8 BUILD: Phase 4 forensic capture — post-build sha256: build-checks.md (in-repo) B46329E445D7A58B; build-checks.md (installed) 2D21B76751452FC7 (intentionally different — global vs project schema with BC-PROJ-1 vs BC-GLOBAL-1); build_checks_audit.py 9029A216CAF937F7; test_build_checks_audit.py 4DD3B9FBBD227E67; methodology-changelog (in-repo + installed) 0A7AA6CA04E372FB byte-equal; VERSION + ai-sdlc-VERSION D1994E4942B06EC3 byte-equal; plugin.yaml 89FBDC223F2F3102. PMI-1 invariant maintained; bidirectional sha256 forensic discipline N=3 stable post-slice-008 (slice-006 + slice-007 + slice-008).
- 2026-05-10 T9 BUILD: replaced stale slice-007 `test_plugin_yaml_version_matches_version_file_at_0_22_0` with slice-008's `test_plugin_yaml_version_matches_version_file_at_0_23_0` + added `test_v_0_23_0_bc_1_v_1_2_entry_present_in_repo_and_installed` (bidirectional changelog entry pin); test_methodology_changelog.py: 6 -> 7 tests; updated shippability.md row 7 (slice-007) to drop deleted test reference + added row 8 (slice-008) with 11 critical-path tests.
- 2026-05-10 T9 DEFERRAL: BC-1 self-application on slice-008 surfaces `BC-PROJ-2` in applicable. Acceptable per Critic M1 (BC-PROJ-2 not migrated; N=1 below BC-1 promotion threshold of N=3) AND per AC #1's explicit gating only on BC-PROJ-1 + BC-GLOBAL-1. The slice's own text contains bare-words `llm` + `code-block` (positive anchors), so BC-PROJ-2 keyword path fires. Rationale: deferring BC-PROJ-2 migration matches the slice's design (Critic M1 ACCEPTED-FIXED disposition); silenced for BC-PROJ-1 + BC-GLOBAL-1 as designed.
- 2026-05-10 T9 TEST: PMI-1 audit clean (exit 0; 24 skills, 5 agents, 15 tools, version 0.23.0); install_audit clean (24/24 skills, 5/5 agents, 4/4 templates, 15/15 tools); shippability catalog 22 critical-path tests PASS in 1.01s; full methodology suite 346/346 PASS in 1.98s; TF-1 audit --strict-pre-finish CLEAN (9 rows PASSING=9).

## Summary

### Plan executed (10 tasks)

- T0 Phase 0 forensic capture — DONE
- T1 Phase 1 RED (9 tests) — DONE (all 9 RED with genuine signatures)
- T2 Phase 2 GREEN — `tools/build_checks_audit.py` modifications — DONE
- T3 Phase 2 GREEN — `architecture/build-checks.md` schema-prelude + BC-PROJ-1 — DONE
- T4 Phase 2 GREEN — `~/.claude/build-checks.md` schema-prelude + BC-GLOBAL-1 — DONE
- T5 Phase 3 mid-slice smoke gate — PASS
- T6 Phase 2 GREEN — version bumps to 0.23.0 (atomic) — DONE
- T7 Phase 2 GREEN — methodology-changelog v0.23.0 entry — DONE (in-repo + installed byte-equal)
- T8 Phase 4 forensic capture + bidirectional verify — DONE
- T9 Phase 5/6 — shippability row + pre-finish gates — DONE

### Mid-slice smoke gate

**Result**: PASS
**Evidence**:
- slice-007 archive backtest with `--changed-files agents/critique.md skills/critic-calibrate/SKILL.md`: applicable=[], skipped=[BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1], violations=0 (target met — N=3 false-positive class silenced).
- slice-001 archive backtest with `--changed-files skills/diagnose/SKILL.md skills/diagnose/write_pass.py skills/diagnose/passes/01-intent.md`: applicable=[BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1] (backward-compat preserved per ADR-004 covenant).

### Pre-finish gate

- [x] All 5 ACs (with #5 split into 5a + 5b) PASS — see validation.md
- [x] Must-not-defer addressed — input validation (`negative-anchor-overlaps-positive` parse violation); TF-1 PASSING=9; TWO-surface × TWO-substring schema-pin (`Negative anchors` + `final filter` in BOTH project + global build-checks); methodology-changelog v0.23.0 entry in-repo + installed byte-equal; PMI-1 audit clean; bidirectional sha256 forensic capture in build-log.md (Phase 0 + Phase 4 — N=3 stable); backward-compat covenant verified via slice-001 archive backtest; no regression on existing 25 BC-1 tests + full methodology suite 346/346 PASS; BC-PROJ-2 behavior unchanged + deferral documented; out-of-repo `~/.claude/build-checks.md` edits captured.
- [x] Drift-check — methodology-changelog.md byte-equal in-repo + installed; VERSION + ai-sdlc-VERSION + plugin.yaml.version all 0.23.0 (PMI-1 invariant)
- [x] Smoke regression — both directions still pass post all subsequent edits
- [x] No debug code — none introduced
- [x] BC-1 self-application — BC-PROJ-1 + BC-GLOBAL-1 silenced (slice's own text contains `vocabulary, Dim 9, back-sync, forward-sync` per design); BC-PROJ-2 deferred-with-rationale (per Critic M1; N=1 below promotion threshold)
- [x] PMI-1 audit clean (exit 0; version 0.23.0)
- [x] TF-1 strict-pre-finish CLEAN (9 rows PASSING=9)
- [x] install_audit clean (24/24 skills, 5/5 agents, 4/4 templates, 15/15 tools, methodology v0.23.0)

### Deferrals

- **BC-PROJ-2 migration**: deferred to a future slice when N=2 promotion threshold is met. Rationale per Critic M1 ACCEPTED-FIXED disposition (slice-008 critique.md): empirical evidence shows BC-PROJ-2 fires false-positively only on slice-005 (N=1; bare-word `llm` + `code-block` keyword-path on slice-005 schema-discussion text); slice-006 + slice-007 don't trigger BC-PROJ-2 because their `--changed-files` don't match `skills/**/*.py, tools/**/*.py` glob (the rule's `Applies to:` requires a subfolder). N=1 is below the BC-1 promotion threshold of N=3 that this slice itself uses. User-approved at TRI-1 ratification (all 6 dispositions ACCEPTED-FIXED). Followup: future slice when a third methodology-vocabulary slice triggers BC-PROJ-2 specifically (N=2 → promotion threshold met).
- **Slice-007 supersession**: slice-007's `test_plugin_yaml_version_matches_version_file_at_0_22_0` (PMI-1 0.22.0 gate) is naturally stale post-slice-008's 0.23.0 bump. Replaced with slice-008's `test_plugin_yaml_version_matches_version_file_at_0_23_0`. Slice-007 archive's reflection.md may eventually warrant a `## Supersession` section (per SUP-1, `methodology-changelog.md` v0.19.0); deferred to /supersede-slice if needed — not load-bearing because slice-007 archive's other claims still hold (CAD-1 audit, sha256 byte-equality, /critic-calibrate skill prose). Captured in shippability.md row 7's parenthetical.

### Design deviations

- **None**. Critic M1/M2/M3 + m1/m2 pre-empted what would have been mid-build deviations:
  - M1 (BC-PROJ-2 deferred) was caught at /critique time, not build-time DEVIATION.
  - M2 (TWO-substring TWO-surface) was caught at /critique time, not build-time DEVIATION.
  - M3 (always-true + negative-anchor test) was caught at /critique time — the test was added to TF-1 plan before build started; built clean.
  - m3 (token spelling fragility) was pre-mitigated by existing migration-tuple test.
- **One zero-deviation build** is the inverse of slice-005..007's pattern (each had 1-2 build-time DEVIATIONs caught at mid-slice smoke or at TF-1 strict). Slice-008's clean build is empirical evidence that strong /critique catches reduce build-time deviations.

### Files changed

- `tools/build_checks_audit.py` (modified — dataclass field + parsing + helper + algorithm + docstring)
- `architecture/build-checks.md` (modified — schema-prelude TWO sentences + BC-PROJ-1 `Negative anchors:` field)
- `~/.claude/build-checks.md` (modified — schema-prelude TWO sentences + cross-project sentence + BC-GLOBAL-1 `Negative anchors:` field)
- `tests/methodology/test_build_checks_audit.py` (extended — 9 new tests for BC-1 v1.2)
- `tests/methodology/test_methodology_changelog.py` (replaced 0.22.0 PMI-1 gate with 0.23.0 PMI-1 gate; added v0.23.0 BC-1 v1.2 entry pin; net +1 test 6 → 7)
- `methodology-changelog.md` (in-repo, appended v0.23.0 entry)
- `~/.claude/methodology-changelog.md` (forward-sync; sha256 byte-equal)
- `VERSION` (0.22.0 → 0.23.0)
- `~/.claude/ai-sdlc-VERSION` (0.22.0 → 0.23.0)
- `plugin.yaml` (version 0.22.0 → 0.23.0)
- `architecture/shippability.md` (updated row 7 to drop deleted 0.22.0 test ref; added row 8 for slice-008)
- `architecture/slices/slice-008-refine-bc-1-anchors-with-negative-context/` — mission-brief.md (TF-1 statuses PENDING → PASSING; AC #5a/5b → AC #5 dual-row), design.md (locked at /critique time), critique.md (CLEAN verdict), build-log.md, milestone.md

