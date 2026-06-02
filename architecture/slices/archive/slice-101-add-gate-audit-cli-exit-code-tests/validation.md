# Validation: Slice 101 add-gate-audit-cli-exit-code-tests

**Date**: 2026-06-02
**Result**: PASS

The "real environment" for this methodology-test slice is the actual gate-audit CLIs executed against real fixtures + the full methodology suite + the shippability catalog — all exercised below, not mocked.

## Per-criterion results

### AC1: Block-path coverage — all 8 gate-audit CLIs have a test invoking the CLI entrypoint on a violating input asserting the non-zero block exit (1; +2 usage for branch_workflow)
- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_gate_audit_cli_exit_codes.py -q` → **18 passed** (from clean bytecode). The 8 block-path tests (`test_pmi1_…`, `test_tri1_…`, `test_lintmock_…`, `test_dr1_…`, `test_wire1_…`, `test_csp1_…`, `test_ptfcd1_…blocks…`, `test_branch1_…blocks…`) each assert `_run_main(main, argv) == 1`. The two exit-2 usage paths (`test_ptfcd1_cli_usage_error_on_missing_catalog`, `test_branch1_cli_usage_error_on_nonconforming_folder`) assert `== 2`.
- **Notes**: in-process `main(argv)` exercises the real violations→exit-code mapping (`sys.exit(main())` is unbreakable glue). All 8 `main()` confirmed to return the code (not exit internally).

### AC2: Non-vacuity by mutation — each block-path test proven to FAIL when its tool's `main()` is forced to `return 0`
- **Status**: PASS
- **Evidence**: build-log.md §"AC2 non-vacuity by mutation (8-row evidence)" — the mutation harness forced each of the 8 tools' `main()` violations→block-code to `return 0`, ran the corresponding block test, and recorded `ALL NON-VACUOUS + ALL REVERTED: True` (all 8 tests FAILED under mutation; all 8 tools reverted, `git diff tools/` empty). Independently, the `/code-review` code-Critic re-confirmed non-vacuity for PTFCD-1, LINT-MOCK, WIRE-1, BRANCH-1 by direct probe (each `main()` returns 1 strictly because violations are non-empty, 0 when clean).
- **Notes**: mutation proves int-DEPENDENCE; the paired kind-assert proves CAUSE-pinning. Row 2 (TRI-1) cause-pin is the `is_file()` precondition (a missing file also yields `no-section`).

### AC3: Cause-pinned + pass-discriminating — each fixture triggers the audit's real target violation; each audit has a conforming-input exit-0 case
- **Status**: PASS
- **Evidence**: each block test pairs the int-assert with `target_kind in {v.kind for v in <audit_fn>(fixture).violations}` (PMI-1 `orphan-skill`, TRI-1 `no-section`, LINT-MOCK `mock-budget`, DR-1 `missing-section`, WIRE-1 `missing-cells`, CSP-1 `broken-ref`, PTFCD-1 `missing-test-file`, BRANCH-1 `on-default-branch`). The 6 clean-path tests (`…clean…`) assert `== 0` on conforming input, forcing `--no-carry-over` so exit 0 reflects a real parse not an exemption short-circuit. The `/code-review` code-Critic verified the SOLE-kind property holds against every fixture (no co-firing kinds).
- **Notes**: `/code-review` m1 (PTFCD-1 clean-test repo-root env-dependence) was ACCEPTED-FIXED in-slice — `_scmd1_catalog` now seeds a `VERSION` sentinel at `tmp_path` so `_find_repo_root` deterministically anchors there. Module re-verified 18/18.

### AC4: Parallel-safe & green — diff touches only `tests/methodology/test_*.py`; `tools/**`/`skills/**`/`plugin.yaml`/`INSTALL.md`/`shippability.md`/`VERSION` unchanged; suite + shippability_runner green
- **Status**: PASS
- **Evidence**:
  - In-scope diff = `tests/methodology/test_gate_audit_cli_exit_codes.py` ONLY (`git diff $base --name-only -- ':(exclude)architecture/**'` + `git ls-files --others tests/**`).
  - `git diff $base --stat -- tools/ skills/ plugin.yaml INSTALL.md architecture/shippability.md VERSION` → **empty** (all unchanged). `VERSION` stays `0.81.0`.
  - Full methodology suite: `$PY -m pytest tests/methodology -q` → **1345 passed** (from clean bytecode).
  - Shippability catalog: `$PY -m tools.shippability_runner architecture/shippability.md` → **106 row(s), 106 PASS, 0 FAIL** (exit 0).
- **Notes**: fully disjoint from parallel slice-100 (whose surface is `tools/vault_flip_readiness_audit.py` + its own new test + the registration files this slice never touches). No `VERSION` bump → zero R-28 forward-sync contention.

## Layered safety checks (VAL-1)
- **Layer A (credential scan)**: PASS — no secrets in the changed test module.
- **Layer B (dependency hallucination)**: PASS — all imports resolve (`tools.*` via package, `tests.*` via `--imports-allowlist tests`, `yaml`→pyyaml alias, stdlib `shutil`/`subprocess`/`pathlib`).
- Invocation: `$PY -m tools.validate_slice_layers --slice <sd> --changed-files tests/methodology/test_gate_audit_cli_exit_codes.py --imports-allowlist tests` → exit 0.

## Walking-skeleton audit (WS-1)
**Required?**: no (`**Walking-skeleton**: false`) — N/A, audit skipped by opt-in gate.

## Exploratory-charter audit (ETC-1)
**Required?**: no (`**Exploratory-charter**: false`) — N/A, audit skipped by opt-in gate.

## Multi-instance validation
**Required?**: no (test-only methodology slice; no multi-user/device/account surface).
**Result**: not-applicable

## Shippability catalog (regression check)
- Pre-catalog gates: SCMD-1 (exit 0), PTFCD-1 (exit 0), SVW-1 (exit 0) — all clean.
- Runner: `$PY -m tools.shippability_runner architecture/shippability.md` → **106 PASS, 0 FAIL** (exit 0). No past slice's critical path regressed.
- No shippability row added for this slice (deliberate — AC4 parallel-safety forbids touching `shippability.md`; the new tests are covered by the existing "methodology suite green" catalog claim).

## Reality surprises
- The build-time stale-`.pyc` incident (mutation harness's byte-length-identical `1`→`0` defeating Python's mtime+size cache check) — already diagnosed/resolved at build (cleared `__pycache__`); not a validation-time surprise, recorded here for the /reflect lesson trail.
