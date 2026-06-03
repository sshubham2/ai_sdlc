# Build log: Slice 106 route-project-frame-synth-via-vault-root

**Date**: 2026-06-03
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-06-03 BUILD: plan approved (6 tasks; smoke gate at task 3); NEEDS-FIXES from /critique (B1 + M2 ACCEPTED-PENDING)
- 2026-06-03 BUILD: tasks 1-5 applied (route 4 sites + L44 docstring; _BASELINE→(); B1 drop assert MUST_REWRITE; allowlist 15→16 + "14"→16; shippability rows #108/#109 repointed)
- 2026-06-03 SMOKE: mid-slice gate PASS — readiness suite 27/27, [production] 0 must-rewrite, frame byte-identical (SHA 97340A02…)
- 2026-06-03 FINDING: full suite caught a 2ND count-pin consumer NOT enumerated by /critique or design — test_external_vault_adr_and_risk.py::test_no_new_tool_migration_and_classification_map_documented hard-pins VAULT_ROOT-importer count == 15; adding project_frame_synth → 16. AP-10 count-literal fan-out recurrence. /critic-calibrate signal.
- 2026-06-03 BUILD: count-pin fixed (15→16 + message + "to 14" docstring + project_frame_synth membership assert); repo-wide grep confirms no 3rd consumer; full suite 1529/0
- 2026-06-03 TEST: full methodology suite 1529 passed / 0 failed (138s)
- 2026-06-03 BUILD: Step 6 audits PASS — DCE-1, BRANCH-1, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, SVW-1, PMI-1, INST-1, PTFFD-1, WIRE-1, TF-1, CAD-1, UTF8-STDOUT-1, LINT-MOCK
- 2026-06-03 BUILD: BC-1 Critical attestations — BC-PROJ-3 + BC-GLOBAL-2: NO destructive `git checkout`/`restore`/`stash` revert of uncommitted slice work (the only mutate-then-rerun was running `project_frame_synth` twice for the AC3 byte-hash; no source revert; temp output in $TEMP). BC-PROJ-7: N/A — slice adds NO new `tools/*.py` module (it modifies existing project_frame_synth.py + vault_flip_readiness_audit.py); rule fired on a trigger-keyword match against the design's `tools/*` prose, not a new-tool add — the test_utf8_stdout_regression argv-list + PMI-1/INST-1 inventory obligations do not apply.
- 2026-06-03 BUILD: BC-1 --strict --ack-critical BC-PROJ-3 BC-PROJ-7 BC-GLOBAL-2 → exit 0

## Summary

### Plan executed (6 tasks — all complete)
1. **`tools/project_frame_synth.py`** — added `from tools._vault_paths import VAULT_ROOT`; routed the 4 vault reads (concept/triage/slice-queue/risk-register) → `repo_root / VAULT_ROOT / "<file>"`; rephrased L44 docstring example (dropped the quote-prefixed `architecture/` literal). ✅
2. **`tools/vault_flip_readiness_audit.py`** — `_BASELINE → ()` + reworded the comment (M2d). ✅
3. **`tests/methodology/test_vault_flip_readiness_audit.py`** — **B1**: dropped the now-false `assert MUST_REWRITE in classes` in `test_emits_classified_inventory_with_evidence` (classifier non-vacuity preserved by the synthetic `test_new_unrouted_literal_fails_gate`); reworded `test_production_baseline_unchanged_vs_slice100` comment (M2c). ✅
4. **`tests/methodology/test_vault_root_constant.py`** — added `tools/project_frame_synth.py` to `_MIGRATION_SITE_ALLOWLIST` (15→16); corrected "14"→"16" prose at L41 + L291 (m1); left the `test_count == 15` function-count pin untouched. ✅
5. **`architecture/shippability.md`** — repointed the stale "4 sites" narrative in rows #108/#109 (M2a/M2b); grep-confirmed no test pins the prose first. ✅
6. **`tests/methodology/test_external_vault_adr_and_risk.py`** — *build-discovered* 2nd count-pin consumer (NOT in design/Critic enumeration; AP-10): `test_no_new_tool_migration_and_classification_map_documented` hard-pinned the VAULT_ROOT-importer count `== 15` → updated to 16 (+ project_frame_synth membership assert + corrected the stale "to 14" docstring). ✅

### Mid-slice smoke gate
**Result**: PASS — readiness suite 27/27, `[production] 0 must-rewrite`, frame output byte-identical (SHA `97340A02…` before == after).

### Pre-finish gate
- [x] All ACs pass with evidence (AC1 4 sites routed / 0 must-rewrite; AC2 `_BASELINE=()` + `--strict` exit 0; AC3 byte-identical frame; AC4 existing allowlist+orphan guards cover project_frame_synth, mutation-non-vacuous; AC5 full suite 1529/0 + shippability unregressed, no new row)
- [x] Must-not-defer addressed (consume seam only; no silent fallback to `"architecture"`; `_read` error model unchanged; no new TODO/debug)
- [x] Drift-check full mode pass (DCE-1 marker written; CLEAN)
- [x] Mid-slice smoke still passes (no regression)
- [x] No new TODOs / FIXMEs / debug prints
- [x] All Step 6 audits PASS: DCE-1, BRANCH-1, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, SVW-1, PMI-1, INST-1, PTFFD-1, WIRE-1 (zero-row), TF-1 (N/A), CAD-1, UTF8-STDOUT-1, LINT-MOCK, BC-1 `--strict`

### Deferrals
- None.

### Design deviations
- None to the design's shape. One **enumeration gap closed at build**: the design (and both Critic passes) named the readiness-audit + allowlist consumers but missed `test_external_vault_adr_and_risk.py`'s `== 15` VAULT_ROOT-importer count-pin. Caught by the full suite (BC-PROJ-4) and fixed in-slice; repo-wide grep confirms no third consumer. Recorded as an AP-10 `/critic-calibrate` signal for `/reflect`. No design.md edit needed (the design's "What's new" + §Build-time-checks already anticipated the count-literal fan-out class; this is one more site of it).

### Files changed
- `tools/project_frame_synth.py`, `tools/vault_flip_readiness_audit.py`
- `tests/methodology/test_vault_flip_readiness_audit.py`, `tests/methodology/test_vault_root_constant.py`, `tests/methodology/test_external_vault_adr_and_risk.py`
- `architecture/shippability.md` (rows #108/#109), `architecture/drift-log.md` (slice-106 audit entry)
