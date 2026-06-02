# Validation: Slice 102 vault-flip-readiness-tests

**Date**: 2026-06-02
**Result**: PASS

Read-only static-analysis CLI slice — the "real environment" is the audit run as a real CLI against the real repo tree + the real test suite executed. All evidence below is from live runs against the worktree, not mocks.

## Per-criterion results

### AC1: scans `tests/**/*.py` + deterministic classified inventory with `path:line`; production-surface `(path,value,klass)` byte-identical to slice-100
- **Status**: PASS
- **Evidence**: live `audit_root` over the worktree — 247 files scanned; tests-surface occurrences carry `surface=="tests"` + `path:line`; production `baseline_tuple() == _BASELINE` (4 `project_frame_synth.py` sites) with 0 production needs-human; output byte-deterministic across runs (`test_output_is_deterministic_across_runs`). `test_tests_surface_scanned_and_classified` + `test_production_baseline_unchanged_vs_slice100` + `test_must_rewrite_baseline_pinned` all PASS.
- **Notes**: the `write_text`/`write_bytes` content-arg correctness fix verified NOT to perturb the production baseline (4/0 unchanged).

### AC2: two distinct named tests classes (`test-update-at-flip` vs `test-collection-pathspec`), neither flattened into production `must-rewrite`; ambiguous → `needs-human`
- **Status**: PASS
- **Evidence**: live counts — `test-update-at-flip` 160 (path-resolves) / `test-collection-pathspec` 49 (git-pathspec/Class-B mirrors), distinct classes; the identical literal classifies `must-rewrite` (production) vs `test-update-at-flip` (tests) vs `needs-human` (production collection) vs `test-collection-pathspec` (tests collection) — verified by `test_tests_path_resolve_is_test_update_at_flip` + `test_tests_collection_pathspec_is_review_not_checklist`. A genuinely-unclassifiable literal routes to `needs-human` (fail-closed) — the seeded demo below.

### AC3: regression pin keyed `(relpath,value,klass)` — fail-closed completeness + non-vacuity + per-class floors
- **Status**: PASS
- **Evidence**: tests-surface `needs-human` == ∅ (`test_tests_surface_needs_human_empty`); non-vacuity — an injected dynamic-fragment-in-path on the tests surface produces `needs-human` (`test_tests_surface_needs_human_pin_non_vacuous`, and the live seeded CLI demo: `tests/methodology/dyn.py:3 (dynamic-fragment)` → `needs-human`); per-class floors `test-update-at-flip` 160 ≥ 120 AND `test-collection-pathspec` 49 ≥ 30 (`test_tests_surface_class_floors`). Three documented residuals each pinned (`test_documented_residual_fully_dynamic_path_invisible`, `test_fixtures_dir_vault_literal_out_of_scope`, `test_collection_member_genuine_resolve_is_review_residual`).

### AC4: CLI gate covers both surfaces — exit 0 clean, exit 2 on `needs-human` / `--strict` production drift
- **Status**: PASS
- **Evidence**: `vault_flip_readiness_audit --repo-root <worktree>` → exit **0** (clean tree, both surfaces, 0 needs-human); a seeded tmp repo with a tests-surface dynamic-fragment → exit **2** (`seeded-needs-human exit=2`); `--strict` on the real tree → exit **0** (production baseline unchanged); `test_cli_exit_zero_when_no_needs_human` + `test_cli_strict_nonzero_on_baseline_drift` PASS.

### AC5: capability-without-flip — `_vault_paths` default `Path("architecture")` untouched; full suite + shippability green
- **Status**: PASS
- **Evidence**: `tools/_vault_paths.py` retains `_DEFAULT = "architecture"` (unchanged); `test_vault_paths_default_unchanged` PASS; full methodology suite **1373 passed** (exit 0); shippability catalog **108 rows, 108 PASS, 0 FAIL**.

## VAL-1 layered safety checks
- **Layer A (credential scan)**: PASS (exit 0) — no committed secrets in the changed files.
- **Layer B (dependency hallucination)**: PASS (exit 0) — no undeclared/hallucinated imports (`--imports-allowlist tests`).

## WS-1 / ETC-1
- Walking-skeleton: **false** → WS-1 skipped clean (not applicable).
- Exploratory-charter: **false** → ETC-1 skipped clean (not applicable).

## Shippability catalog (regression check)
- Pre-gates: SCMD-1 exit 0, PTFCD-1 exit 0, SVW-1 exit 0.
- `tools.shippability_runner architecture/shippability.md` → **108 row(s), 108 PASS, 0 FAIL** (exit 0). No past slice regressed. New row #109 (slice-102 tests-surface guarantee) passes.

## Multi-instance validation
**Required?**: no (single-process read-only static-analysis CLI; no multi-user/device/account surface).
**Result**: not-applicable.

## Reality surprises
- None. The build's mid-slice smoke + the 3-Critic stack had already surfaced the substantive issues (M1 collection-mirror mislabel, M2 AC4 contradiction, M-add-1 heterogeneity, the `write_text` false-positive). Validation confirmed the shipped behavior matches design with no new surprises.
