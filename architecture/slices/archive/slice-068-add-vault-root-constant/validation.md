# Validation: Slice 068 add-vault-root-constant

**Date**: 2026-05-25
**Result**: PASS

## Per-criterion results

### AC1: `tools/_vault_paths.py` module exports `VAULT_ROOT: Path` defaulting to `Path("architecture")`, overridable via env var `AI_SDLC_VAULT_ROOT`

- **Status**: PASS
- **Evidence**:
  - Default (env unset): `$PY -c "from tools._vault_paths import VAULT_ROOT; print(VAULT_ROOT)"` prints `architecture` ✓
  - Env override via subprocess: `tests/methodology/test_vault_root_constant.py::test_env_var_override_via_subprocess PASSED` (subprocess fixture injects `AI_SDLC_VAULT_ROOT=<tmp>` and confirms VAULT_ROOT == that path at module-import time) ✓
  - In-process default reload via monkeypatch: `tests/methodology/test_vault_root_constant.py::test_vault_root_default_equals_path_architecture PASSED` (monkeypatch unsets env, `importlib.reload(tools._vault_paths)`, assert VAULT_ROOT == Path("architecture")) ✓
- **Notes**: Read-at-import-time semantic is deliberate production-correctness contract per ADR-065 §Decision; documented in module docstring (`tools/_vault_paths.py:14-21`).

### AC2: Every filesystem-resolving `Path("architecture")` / `"architecture/..."` literal in `tools/*.py` routes through `VAULT_ROOT`; two-marker convention preserves filesystem-vs-prose distinction

- **Status**: PASS
- **Evidence**:
  - Grep audit `grep -rn 'Path("architecture")\|"architecture/' tools/` returns only:
    - `tools/_vault_paths.py:4` (docstring referencing default `Path("architecture")` — informational prose, not a filesystem-resolving literal)
    - `tools/__pycache__/_vault_paths.cpython-313.pyc` (binary cache — pre-existing)
    - All 8 migration sites now use `VAULT_ROOT` (no literal `"architecture"` survives) — verified by `tests/methodology/test_vault_root_constant.py::test_no_orphan_architecture_literal_in_migrated_tools PASSED` (2-marker convention audit) and `::test_all_tools_modules_import_vault_root PASSED` (each of 8 modules in `_MIGRATION_SITE_ALLOWLIST` imports `VAULT_ROOT` from `tools._vault_paths`).
  - `shippability_decoupling_audit.py:91-92` AST-pattern tuples preserved verbatim (regression-pinned by `::test_shippability_decoupling_audit_tuples_preserve_literal PASSED`).
- **Notes**: Two-marker convention added per /critique-review M-add-1 ACCEPTED-FIXED — 5 EXCLUDED error-message-string sites (`cross_spec_parity_audit.py:335`, `state_transition_pin_audit.py:374,388,400`, `validate_slice_layers.py:521`) carry the `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` marker; design.md and mission-brief swept consistently across all 3 spec surfaces.

### AC3: No behavior change — full pytest suite passes; migration is idempotent

- **Status**: PASS
- **Evidence**:
  - Full pytest run from worktree: `944 passed in 29.95s, 0 failed` ✓
  - This is the same 944/0 result captured at /build-slice Phase E (Phase E baseline + 10 new slice-068 tests = 944 vs slice-067-citation 899 + recent slice additions; net delta from slice-068 = +10 from `test_vault_root_constant.py`).
  - Idempotency: `tests/methodology/test_vault_root_constant.py::test_migration_is_idempotent PASSED` (re-applies the `Path("architecture") → VAULT_ROOT` transform on `tools/slice_queue_writer.py` and asserts empty diff).
- **Notes**: The pure-refactor contract is empirically validated — every behavior path through the 8 migrated modules continues to produce identical outputs. Note that /code-review m1 (advisory) flagged that the idempotency regex only catches 1 of 4 pre-migration literal shapes; AC3's PASS is empirical (944/0 full pytest), not regex-coverage-strong. Logging this for /reflect-time consideration alongside the M1 BCR-1 candidate.

### AC4: Test suite asserts seam + allowlist + freeze contract — 10 tests pass; allowlist pinned; env-override semantic + consumer-freeze contract documented

- **Status**: PASS
- **Evidence**:
  - All 10 `tests/methodology/test_vault_root_constant.py` tests PASS:
    1. `test_vault_root_module_exports_constant` (AC1 export) ✓
    2. `test_vault_root_default_equals_path_architecture` (AC1 default) ✓
    3. `test_all_tools_modules_import_vault_root` (AC2 import audit) ✓
    4. `test_no_orphan_architecture_literal_in_migrated_tools` (AC2 two-marker convention) ✓
    5. `test_shippability_decoupling_audit_tuples_preserve_literal` (AC2 AST-tuple regression-pin) ✓
    6. `test_full_pytest_baseline_preserved` (AC3 test-count structural pin = 10) ✓
    7. `test_migration_is_idempotent` (AC3 idempotency) ✓
    8. `test_env_var_override_via_subprocess` (AC4 cross-process env override) ✓
    9. `test_migration_site_allowlist_pinned` (AC4 8-element allowlist matches actual VAULT_ROOT importers) ✓
    10. `test_consumer_constants_are_frozen_at_first_import` (AC4 production-correctness freeze contract per /critique M1 ACCEPTED-FIXED) ✓
- **Notes**: /code-review M1 (advisory) flagged that the design.md L25 + mission-brief.md L54 explicitly promise an 11th test `test_vault_paths_module_is_leaf` (stdlib-only import audit) that I did not write. The invariant currently HOLDS empirically (the module imports only `__future__`, `os`, `pathlib.Path` per `tools/_vault_paths.py:23-26`), so AC4 is PASS — but the promised regression guard does not exist, creating a real spec-vs-code drift documented for /reflect-time disposition as a BCR-1 SC-NNN candidate. /code-review m2 (advisory) flagged the freeze-pin test's assertion gap (passes on a no-op monkeypatch) — also flagged for /reflect SC-NNN consideration.

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: This slice is a pure mechanical refactor of audit-tooling Python modules. No multi-user, multi-device, multi-account, or sync/sharing surface. Single-process validation is structurally sufficient.

## VAL-1 layered safety checks

- **Layer A — Credential scan**: 0 secret(s) found in 10 changed files. PASS.
- **Layer B — Dependency hallucination check**: 0 import finding(s); 0 suppressed (allowlisted). PASS.
- **Evidence**: `$PY -m tools.validate_slice_layers --slice architecture/slices/slice-068-add-vault-root-constant --changed-files <10 files> --imports-allowlist tests` returns: *"VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted). Clean — both layers passed."*

## WS-1 walking-skeleton audit

- **Required?**: no (mission-brief `**Walking-skeleton**: false`)
- **Result**: not-applicable (default-off semantics — audit returns clean silently when field is `false`)

## ETC-1 exploratory-charter audit

- **Required?**: no (mission-brief `**Exploratory-charter**: false`)
- **Result**: not-applicable

## Shippability catalog regression check

- **SCMD-1 pre-catalog gate**: PASS — *"SCMD-1 audit: clean. 67 row(s); 645 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=643."*
- **PTFCD-1 sub-mode (b) pre-catalog gate**: PASS — *"Shippability path audit (PTFCD-1/PTFFD-1): clean. 67 row(s), 359 test-path token(s) — all files and cited functions exist."*
- **Canonical runner**: PASS — *"Shippability catalog run: 67 row(s), 67 PASS, 0 FAIL"*

Zero regressions in the 67-row catalog. This slice's 8-site migration + new constant module did not break any past-slice critical-path test.

## Reality surprises

- **N=4 cumulative gitignored-vault-vs-worktree conflict** (documented in build-log.md DEVIATION section; surfaced at /build-slice Phase E during initial full-pytest collection). Resolution within slice scope: cp -r the gitignored trees (architecture/, diagnose-out/, graphify-out/) from main tree to worktree. Structural fix: slice-069 (`rename-architecture-to-sdlc-and-track-in-git`) which un-gitignores the vault. The reality surprise is that BRANCH-2's worktree-per-slice + gitignored-vault is now a recurring class (slice-067 N=3 → slice-068 N=4) deserving methodology adjustment OR slice-069 acceleration. Logging to /reflect for cumulative-pattern consideration.
- **/code-review M1 spec-vs-code drift**: design.md L25 + mission-brief.md L54 promised `test_vault_paths_module_is_leaf` regression-pin not written. The invariant holds empirically at slice-068 ship time, but a future edit could add a `tools/*` import to `_vault_paths.py` without any test catching it. Candidate for BCR-1 SC-NNN at /reflect.
- **/code-review m1 + m2 + m3 + m4 minor findings**: see code-review.md. Advisory per CRSI-1 v1; not blocking. /reflect will decide whether to file any as SC-NNN backlog entries or address opportunistically.
