# Build log: Slice 043 codify-split-slice-folder-naming-convention

**Date**: 2026-05-18
**Result**: SHIPPED-WITH-DEFERRALS (m2 ACCEPTED-PENDING applied this slice; no carry-forward)

## Events (append-only — written DURING build per Step 7c)

- 2026-05-18 PREREQ: CRP-1 clean (critique-review.md present); WT clean; on master → created branch `slice/043-codify-split-slice-folder-naming-convention`
- 2026-05-18 BUILD: methodology why-none re-verified by Builder vs REAL assertions — META-1 `test_methodology_changelog.py:136` `re.split` iterates existing `## v` only; PMI-1 `branch_workflow_audit.py` already at plugin.yaml:91, modified-not-added; VERSION==most_recent unchanged → no rule-ID/no changelog/no bump confirmed (must-not-defer #1 discharged)
- 2026-05-18 TEST: new test module run against UNMODIFIED audit → 3 FAILED (ii/iii/v) + 2 PASSED (i/iv) — AC3 genuine-contrast confirmed
- 2026-05-18 BUILD: `_SPLIT_SLICE_FOLDER_RE` (uppercase-only `^slice-(\d{3})([A-Z]+)-(.+)$`) + branched usage-error message added to tools/branch_workflow_audit.py (kind + exit-2 unchanged; strict `_SLICE_FOLDER_RE` untouched)
- 2026-05-18 TEST: new module + test_branch_workflow_audit.py (8) + test_root_claude_md_branch_per_slice_rule.py → 13 passed, 1 fail (CLAUDE.md pin — Task 3 pending, expected)
- 2026-05-18 SMOKE: mid-slice — `branch_workflow_audit` on synthetic `slice-030B-...` folder → exit 2 usage-error with NEW actionable convention message (names convention + `030B` + next-free-number remedy + ADR-046/BRANCH-1); NOT the old generic message → PASS
- 2026-05-18 BUILD: CLAUDE.md Branch-per-slice split-slice convention sub-clause added (Task 3)
- 2026-05-18 BUILD: R-6 retirement — `**Status**: open`→`retired` + verbose `**Retired**:` line (R-4/R-5 precedent shape) in architecture/risk-register.md (Task 4)
- 2026-05-18 BUILD: shippability.md row 43 added cataloguing the new test module (m2 ACCEPTED-PENDING discharged this slice — closes slice-038→R-10 detection-latency class)
- 2026-05-18 TEST: BC-PROJ-4 — risk_register_audit --json → R-6.status=="retired"; absent from --filter-status open (present pre-slice); retired 6→7
- 2026-05-18 TEST: full tests/methodology/ suite → 679 passed, 0 failed (R-10-class master-green guard; slice-042 baseline 674 + 5 new fns)
- 2026-05-18 BUILD: all Step-6 audits clean — BRANCH-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / WIRE-1 / BC-1 / LINT-MOCK-1 all exit 0
- 2026-05-18 BUILD: git state verified — architecture/ is .gitignore:11 (local-only vault by design); tracked deliverable = CLAUDE.md + tools/branch_workflow_audit.py + new test module (3 files); consistent with repo model

## Summary

### Plan executed

| Task | Status |
|------|--------|
| 1. Write regression test module FIRST (AC3 genuine-contrast) | ✅ 5 fns; FAILed pre-impl (ii/iii/v), PASSed (i/iv) |
| 2. `_SPLIT_SLICE_FOLDER_RE` + branched usage-error in branch_workflow_audit.py | ✅ uppercase-only; strict accept regex unchanged; kind/exit-2 unchanged |
| Mid-slice smoke gate | ✅ PASS (synthetic slice-030B-... → new actionable message, exit 2) |
| 3. CLAUDE.md Branch-per-slice convention sub-clause | ✅ |
| 4. R-6 `**Status**:` flip → retired + `**Retired**:` line (M2 two-part shape) | ✅ |
| 5. shippability.md row 43 (m2 ACCEPTED-PENDING) | ✅ discharged this slice |

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `$PY -m tools.branch_workflow_audit <tmp>/architecture/slices/slice-030B-complete-shippability-decoupling --root <tmp>` → exit 2; `[Important] usage-error: split-slice follow-up folder name not accepted: 'slice-030B-complete-shippability-decoupling'. Per ADR-046 / BRANCH-1, split-slice follow-up folders are numeric \`slice-NNN-\`; the \`NNNx\` letter (here \`030B\`) is a prose lineage label only … Rename to the next free numeric slice number …`. The NEW convention message, not the OLD generic one.

### Pre-finish gate
- [x] All ACs pass with evidence — see validation.md (AC1 convention codified+pinned; AC2 deterministic actionable behavior; AC3 regression pin genuine-contrast 3-FAIL→PASS; AC4 R-6 retired verified via risk_register_audit --json)
- [x] Must-not-defer addressed — (1) methodology-obligation Builder-verified vs REAL META-1/PMI-1 (not precedent); (2) state-transition pre-grep: no test pins R-6 `open` state (independently re-confirmed by Builder + dual-Critic); (3) CAD-1: CLAUDE.md not installed-mirrored (no CAD-1 surface) + full methodology suite green incl. all drift guards; (4) regression test genuine contrast confirmed
- [x] Drift-check — covered by 679-test methodology suite green (CAD-1/PMI-1/mini-CAD/BCI-1/MCFS-1 drift guards) + clean BCI-1/MCFS-1/PMI-1 audits
- [x] Smoke regression check — re-passes via 14-test targeted run + audit CLI
- [x] No debug code — `print(` in branch_workflow_audit.py is pre-existing legitimate `main()` CLI output; Task 2 added none
- [x] LINT-MOCK-1 / WIRE-1 (zero-row) / BC-1 / BRANCH-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 — all clean
- [x] TF-1 — N/A (`Test-first: false`)

### Deferrals
- m2 (shippability cataloguing) was ACCEPTED-PENDING at TRI-1 → **discharged within this slice** (row 43 added at Task 5). No carry-forward.

### Design deviations
None. Built exactly to design.md / ADR-046 (option (a), uppercase-only `_SPLIT_SLICE_FOLDER_RE`, R-6 two-part `**Status**:`-flip retirement).

### Files changed
**Tracked (the slice deliverable)**:
- `tools/branch_workflow_audit.py` — added `_SPLIT_SLICE_FOLDER_RE` constant + branched folder-name `usage-error` message (strict `_SLICE_FOLDER_RE` accept unchanged; kind/exit-2 unchanged)
- `CLAUDE.md` — Branch-per-slice split-slice folder-naming convention sub-clause
- `tests/methodology/test_branch_workflow_split_slice_folder_convention.py` (NEW) — 5-fn regression pin

**Local vault (gitignored `architecture/` per .gitignore:11 — by design)**:
- `architecture/risk-register.md` — R-6 `open → retired`
- `architecture/shippability.md` — row 43 (new pin catalogued; m2)
- `architecture/decisions/ADR-046-split-slice-folder-naming-convention.md` (NEW)
- `architecture/slices/slice-043-*/` — mission-brief, design, critique, critique-review, milestone, build-log
- `architecture/slices/_index.md` — Active row
