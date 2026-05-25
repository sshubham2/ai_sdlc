# Build log: Slice 032 add-query-design-skill

**Date**: 2026-05-17
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-05-17 00:00 DEVIATION: DEVIATION-1 — /critique m1 disposition cited a false precedent (slice-029/v0.43.0 DOES have an entry-pin test; 24/24 universal). Surfaced at /build-slice plan-mode design-is-wrong gate; user chose correct-design + re-critique-on-delta. Re-critique loop ran (critique-v2.md NEEDS-FIXES + critique-review-v2.md EXTEND) → all ACCEPTED-FIXED, v2 verdict CLEAN, user-ratified.
- 2026-05-17 00:01 BUILD: plan approved (11 tasks); branch slice/032-add-query-design-skill; CRP-1 + triage + critique-review audits clean pre-build
- 2026-05-17 00:02 DEVIATION: install_audit _CANONICAL_SKILLS insertion corrected to after heavy-architect (design hint said after drift-check; alpha h<q<r; INST-1 sorts both sides — placement-only, no re-critique)
- 2026-05-17 00:10 BUILD: tasks 1-2 — skills/query-design/SKILL.md created + forward-synced (sha256 MATCH b66ba8255679)
- 2026-05-17 00:14 BUILD: tasks 3-6 — _CANONICAL_SKILLS +query-design; plugin.yaml +id +version 0.46.0; VERSION 0.46.0 + ai-sdlc-VERSION synced; methodology-changelog v0.46.0/QD-1 entry + forward-synced (4-part PMI-1 bump complete)
- 2026-05-17 00:18 BUILD: tasks 7-9 — test_query_design_skill_drift.py + test_query_design_skill.py + test_methodology_changelog _V046/_QD1_PHRASE + test_v_0_46_0_qd_1 (rule-ID-bearing 4-assertion, mirrors scmd_1)
- 2026-05-17 00:20 FINDING: test_no_pipeline_position_block false-positived on SKILL.md's own descriptive prose ("no `## Pipeline position` block"); fixed test to detect heading-at-line-start not bare substring
- 2026-05-17 00:21 TEST: 8/8 query-design tests PASS post-fix
- 2026-05-17 00:24 BUILD: tasks 10-11 — shippability row #32 (6-cell, prose-free Machine-cmd); INSTALL.md L19/L185/L218 count-agnostic
- 2026-05-17 00:26 SMOKE: mid-slice PASS — plugin_manifest_audit clean (25 skills v0.46.0); install_audit clean (25/25); shippability_decoupling_audit clean (32 rows, incidental=0 — B2 empirically confirmed new Path.home() drift test classifies clean, no allowlist edit); INSTALL.md stale-count guard clean
- 2026-05-17 00:30 TEST: pre-finish — BRANCH-1/CRP-1/PCA-1/UTF8-STDOUT-1/BCI-1/WIRE-1/triage all clean; mock-budget clean; full methodology suite 601 passed 0 failed
- 2026-05-17 00:31 DEFERRAL: none — BC-1 surfaced BC-PROJ-3/BC-GLOBAL-2 (Critical, hazard-avoidance: no git checkout/restore/stash on slice paths — satisfied by compliance) + BC-PROJ-4 (Important: real-artifact gates run at prereq+pre-finish+~50% smoke — satisfied). No deferrals.

## Summary

### Plan executed (11 tasks, all complete)

1. ✅ skills/query-design/SKILL.md — read-only/grounding/delegation/3-error-clauses, `_QD1_PHRASE` verbatim, NO Pipeline position block
2. ✅ forward-sync ~/.claude/skills/query-design/SKILL.md (byte-equal)
3. ✅ tools/install_audit.py `_CANONICAL_SKILLS` +query-design (after heavy-architect)
4. ✅ plugin.yaml +id:query-design +version 0.46.0
5. ✅ VERSION 0.46.0 + ~/.claude/ai-sdlc-VERSION synced
6. ✅ methodology-changelog.md v0.46.0/QD-1 entry (Added + Rule reference + Defect class + Validation) + forward-synced
7. ✅ tests/methodology/test_query_design_skill_drift.py (sha256 byte-equality)
8. ✅ tests/methodology/test_query_design_skill.py (prose-pin + `_QD1_PHRASE` site ii + heading-not-substring fix)
9. ✅ test_methodology_changelog.py `_V046`/`_QD1_PHRASE` + test_v_0_46_0_qd_1 (rule-ID-bearing 4-assertion, mirrors scmd_1)
10. ✅ architecture/shippability.md row #32 (6-cell, prose-free Machine-cmd)
11. ✅ INSTALL.md L19/L185/L218 count-agnostic

### Mid-slice smoke gate

**Result**: PASS. plugin_manifest_audit clean (25 skills, v0.46.0); install_audit clean (25/25 skills, methodology v0.46.0); shippability_decoupling_audit clean (32 rows, **incidental=0** — B2 empirically confirmed: new `Path.home()` drift test classifies clean without an allowlist edit); INSTALL.md stale-count guard clean.

### Pre-finish gate

- [x] All 5 ACs pass with evidence — see validation.md
- [x] Must-not-defer addressed (read-only invariant; PMI-1/INST-1/CSP-1; 4-part PMI-1 bump; v0.46.0 format-conformant; `_QD1_PHRASE` 2-site pin; 6-cell SCMD-1 row; INSTALL 3 sites; declinable handoff; grounding; no Pipeline position block)
- [x] Drift-check pass (vault matches code; the pinning tests ARE the drift surface — all green)
- [x] Smoke regression check pass (full methodology suite 601 passed, 0 failed)
- [x] No debug code (new files contain no TODO/FIXME/print)
- [x] BRANCH-1 / CRP-1 / PCA-1 / UTF8-STDOUT-1 / BCI-1 / WIRE-1 / mock-budget / triage all clean
- [x] BC-1: BC-PROJ-3 / BC-GLOBAL-2 (Critical, hazard-avoidance) satisfied by compliance — no destructive git revert on slice paths; BC-PROJ-4 (Important) satisfied — real-artifact gates run at prereq + pre-finish + ~50% smoke
- [x] TF-1: n/a (Test-first: false)

### Design deviations

- **DEVIATION-1** (surfaced at /critique m1 false-precedent, corrected at /build-slice plan-mode; full re-critique loop ran v2 → CLEAN, user-ratified). design.md + mission-brief updated. Net effect: m1 reversed; 4-part PMI-1 atomic bump enumerated; rule-ID-bearing 4-assertion entry-pin spec; 2-site `_QD1_PHRASE` pin (changelog + SKILL.md). All in design.md.
- **install_audit placement**: design hint "after drift-check" → corrected to alphabetical "after heavy-architect" (INST-1 sorts both sides; functionally inert). Recorded here, not re-critiqued (placement-only).
- **test_no_pipeline_position_block**: initial bare-substring check false-positived on SKILL.md's own descriptive prose; corrected to heading-at-line-start detection (mirrors `pipeline_chain_audit._extract_section`). No design impact.

### Deferrals

None.

### Files changed

- `skills/query-design/SKILL.md` (new) + `~/.claude/skills/query-design/SKILL.md` (installed)
- `tools/install_audit.py`
- `plugin.yaml`
- `VERSION` + `~/.claude/ai-sdlc-VERSION`
- `methodology-changelog.md` + `~/.claude/methodology-changelog.md`
- `tests/methodology/test_query_design_skill_drift.py` (new)
- `tests/methodology/test_query_design_skill.py` (new)
- `tests/methodology/test_methodology_changelog.py`
- `architecture/shippability.md`
- `INSTALL.md`
- vault: `architecture/slices/slice-032-add-query-design-skill/*` + `architecture/decisions/ADR-032-query-design-readonly-delegation-only.md`
