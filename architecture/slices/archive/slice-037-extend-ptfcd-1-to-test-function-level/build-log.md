# Build log: Slice 037 extend-ptfcd-1-to-test-function-level

**Date**: 2026-05-17
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-17 00:00 BUILD: branch slice/037-extend-ptfcd-1-to-test-function-level created from master (clean WT)
- 2026-05-17 00:00 BUILD: CRP-1 prerequisite clean; TPHD-1 pre-flight clean
- 2026-05-17 00:01 DEVIATION: plan-mode correction — spec cited non-existent tests/tools/; relocating to tests/methodology/ (repo convention; slice-027-B1 phantom-path-convention class) — harmonized in same fix block per TPHD-1
- 2026-05-17 00:01 BUILD: plan approved by user
- 2026-05-17 00:10 BUILD: tools/_pyfn.py created; adversarial-corpus self-check PASS (prose rejected, idents accepted, tri-state correct)
- 2026-05-17 00:20 BUILD: test_first_audit.py + shippability_path_audit.py extended (missing-test-function kind, skip_notes, M3 precedence, _format_human skip-note)
- 2026-05-17 00:25 TEST: 15 new PTFFD-1 tests PASS; 25 FILE-level PTFCD-1 regression tests PASS (no regression)
- 2026-05-17 00:30 SMOKE: mid-slice BC-PROJ-4 gate PASS — (1) crafted phantom-fn fixture → exit 1 + missing-test-function; (2) real shippability.md clean 36 rows/228 tokens (zero false positives); (3) own slice-037 brief clean under its own function-level audit (only expected non-passing-pre-finish for PENDING rows — recursive self-application clean)
- 2026-05-17 00:50 BUILD: critique.md Dim 9 refined N=2→N=3 + function-level layer + PTFFD-1; CAD-1 clean (forward-synced); AC4 content-pins added; v0.50.0 changelog + 4-part PMI-1 bump (0.49.0→0.50.0); entry-pins added
- 2026-05-17 00:55 BUILD: shippability row 37 appended LAST (M-add-2 ordering); function-level audit clean on own catalog 37 rows/239 tokens (second-order self-application closed)
- 2026-05-17 01:00 TEST: pre-finish audit battery — TF-1 19/19 PASSING, BRANCH-1/UTF8-STDOUT-1/CRP-1/PCA-1/BCI-1/PMI-1(0.50.0)/critique_review/triage/WIRE-1/BC-1/LINT-MOCK/INST-1 all clean
- 2026-05-17 01:02 FINDING: full pytest — 1 FAIL test_shippability_decoupling_audit::test_real_catalog_scmd1_clean — row 37 Machine-cmd cited test_slice034_prose_test_function_is_not_false_positive which reads the GITIGNORED archive corpus → SCMD-1 incidental-coupling violation (slice-029/R-4 class; slice-022 self-violation law fired again — pre-finish gate caught it, NOT a deferral)
- 2026-05-17 01:05 BUILD: FIX — removed the archive-coupled AC3 selector from row 37 Command + Machine-cmd; AC3 archive-reading tests remain in the suite (SCMD-1 forbids only the CATALOG-row citation, not the test's existence); kept the SCMD-1-clean test_real_shippability_and_full_tf1_corpus_clean_under_func_level

## Summary (filled at slice end)

### Plan executed
9 tasks, all complete: (1) spec harmonization tests/tools→tests/methodology; (2) tools/_pyfn.py shared tri-state helper; (3) test_first_audit.py function-level layer + skip_notes + M3 precedence; (4) shippability_path_audit.py selector capture + kind field + skip-note; (5) 3 PTFFD-1 test files (15 tests) + mid-slice smoke gate PASS; (6) critique.md Dim 9 N=2→N=3 + PTFFD-1 + CAD-1 forward-sync; (7) AC4 content-pins; (8) v0.50.0 changelog + 4-part PMI-1 bump + 2 entry-pins; (9) shippability row 37 (last) + pre-finish.

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: crafted phantom-fn fixture → exit 1 + `missing-test-function`; real shippability.md clean 36 rows/228 tokens (zero false positives); own slice-037 brief clean under its own function-level audit (recursive self-application clean).

### Pre-finish gate
- [x] All ACs pass with evidence — TF-1 19/19 PASSING; 682/682 pytest; smoke gate PASS — see validation.md
- [x] Must-not-defer addressed — back-compat degrade, selector shapes, unparseable graceful+skip-note, observability (file+function in message, skip-note renders), RULE-ID/entry-pin/version pre-decided (ADR-038)
- [x] drift-check pass — forward-sync byte-equal (changelog + critique.md), CAD-1/PMI-1 clean, VERSION=plugin.yaml=ai-sdlc-VERSION=0.50.0
- [x] Smoke regression check pass (re-verified post-fix)
- [x] No debug code / TODO / FIXME
- [x] Audits: TF-1, BRANCH-1, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, PMI-1, BC-1, WIRE-1, LINT-MOCK-1, INST-1, critique_review, triage — all clean

### Deferrals (if any)
(none)

### Design deviations (if any)
- Plan-mode: spec cited non-existent `tests/tools/`; relocated to `tests/methodology/` (repo convention; slice-027-B1 phantom-path-convention class). Spec harmonized in same fix block (TPHD-1). Design intent unchanged — only the directory.
- Pre-finish SCMD-1 catch (slice-022 self-violation law fired; the backstop worked): row 37's Machine-cmd cited `test_slice034_prose_test_function_is_not_false_positive`, which reads the gitignored archive corpus → SCMD-1 incidental-coupling. FIXED in-gate: removed the archive-coupled AC3 selector from row 37 (the test still exists/runs in the suite — SCMD-1 forbids only the catalog-row citation, per the slice-029/R-4 lesson). Not a deferral.

### Files changed
- `tools/_pyfn.py` (new), `tools/test_first_audit.py`, `tools/shippability_path_audit.py`
- `agents/critique.md` (+ forward-sync `~/.claude/agents/critique.md`)
- `methodology-changelog.md` (+ forward-sync `~/.claude/methodology-changelog.md`), `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml`
- `architecture/shippability.md` (row 37)
- `tests/methodology/test_ptffd1_test_first_audit.py` (new), `test_ptffd1_shippability_path_audit.py` (new), `test_ptffd1_no_false_positive.py` (new)
- `tests/methodology/test_critique_agent.py` (+2 AC4 pins), `tests/methodology/test_methodology_changelog.py` (+2 entry-pins +constants)
- vault: `architecture/slices/slice-037-*/{mission-brief,design,critique,critique-review,milestone,build-log}.md`, `architecture/decisions/ADR-037,ADR-038`
