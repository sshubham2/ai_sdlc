# Slice 055: add-shippability-runner-execution-tests

**Closes:** SC-005

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: SC-005 (HIGH severity; large blast) — `tools/shippability_runner.run_catalog()` is the executor for `architecture/shippability.md` (the catalog CLAUDE.md calls out as "the single source of truth for must-never-silently-regress claims"). Today only `_segments()` is exercised; `run_catalog()` and `main()` are structurally untested. The pipeline guarantee "shippability regressions block /reflect" rests on untested execution logic. This slice retires that gap with direct execution-level tests against tmp catalogs.
**Test-first**: false (this slice IS adding tests against existing-correct code — there is no production-code change; TF-1's PENDING→WRITTEN-FAILING→PASSING lifecycle does not naturally apply)
**Walking-skeleton**: false (single-layer test addition)
**Exploratory-charter**: false (deterministic test addition; no user-facing UX surface)

## Intent

Close the SC-005 owner-confirmed CRITICAL-adjacent gap: write the missing execution-level tests for `tools/shippability_runner.py` so that `run_catalog()` (the SRSC-1 canonical Step-5.5 runner that decides PASS/FAIL per shippability-catalog row) and `main()` (the CLI exit-code contract `0 every row PASSED | 1 ≥1 row FAILED | 2 catalog missing`) are pinned by real subprocess execution against constructed tmp catalogs — not just the `_segments()` parsing helper. Closes the second end-to-end BCR-1 round-trip dogfood after slice-054's first, on a HIGH-severity, zero-dep candidate.

## Acceptance criteria

1. New test module `tests/methodology/test_shippability_runner_execution.py` exists with at least 4 distinct test functions that collectively exercise `run_catalog()` (PASS branch + FAIL branch) AND `main()` (all three exit codes: 0 / 1 / 2). The PASS-branch test must construct a tmp catalog whose row's Machine-cmd cell uses `<interp> -c "pass"` (or equivalent zero-exit subprocess invocation) — proving `run_catalog()` runs the subprocess, observes returncode 0, and records `passed += 1`.
2. `run_catalog()` against a tmp catalog whose single data row's Machine-cmd cell exits non-zero (e.g. `<interp> -c "raise SystemExit(1)"` — chosen because `_segments` does a naive `;`-split BEFORE `shlex.split` per `tools/shippability_decoupling_audit.py:212`, so any `;` inside a python `-c` body would crash the parse; verified empirically at /critique B1) returns a `RunResult` with `failed == 1`, `passed == 0`, `rows_run == 1`, `rows[0].status == "FAIL"`, `rows[0].line > 0`, and non-empty `rows[0].detail` whose **first line** (before the first `\n`) contains the literal substring `"segment exited 1"` — proving the FAIL branch path that today is structurally untested. Both the structural fields (`status`, `line`, `detail` truthiness) AND the narrow format substring are pinned so the test fails informatively if the runner's detail format string at `tools/shippability_runner.py:151` is later edited (slice-038 m2 load-bearing-test lesson — narrow-only substring pin is brittle; structural + narrow together survive cosmetic format changes).
3. `runner.main([str(tmp_passing_catalog)])` returns `0` (catalog contains a row whose Machine-cmd cell is `<interp> -c "pass"`), `runner.main([str(tmp_failing_catalog)])` returns `1` (catalog contains a row whose Machine-cmd cell is `<interp> -c "raise SystemExit(1)"`), and `runner.main([str(nonexistent_path)])` returns `2` — directly exercising the `return 1 if result.failed else 0` line + the `catalog not found` exit-2 line that the SC-005 finding flags as untested.
4. The new test module imports `tools.shippability_runner` and calls the symbols `runner.run_catalog` AND `runner.main` (NOT only via subprocess); coverage of these symbols is proven by direct call — closes the literal SC-005 evidence-line claim that "`run_catalog()` is never called in any test".
5. BCR-1 round-trip closes SC-005: on `/reflect`, the additive `- **Addressed:** slice-055-add-shippability-runner-execution-tests on YYYY-MM-DD` line is injected into `diagnose-out/backlog.md` at the BCR-1-mandated position — AFTER the `**Evidence:**` sub-list of the SC-005 block, BEFORE the `### SC-006` header.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | New test module exists with ≥4 tests | `& $PY -m pytest tests/methodology/test_shippability_runner_execution.py --collect-only -q` lists ≥4 test items; AND PowerShell-clean AST count check: `& $PY -c "import ast, pathlib; t = ast.parse(pathlib.Path('tests/methodology/test_shippability_runner_execution.py').read_text(encoding='utf-8')); tests = [n.name for n in t.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]; assert len(tests) >= 4, f'expected >=4 tests, got {len(tests)}: {tests}'; print(f'OK {len(tests)} tests')"` prints `OK N tests` with N≥4 |
| 2 | FAIL-branch path exercised | `& $PY -m pytest tests/methodology/test_shippability_runner_execution.py::test_run_catalog_fail_row_records_fail -q` returns 0 (test passes); the test itself asserts `result.failed == 1`, `result.passed == 0`, `result.rows[0].status == "FAIL"`, `result.rows[0].line > 0`, `result.rows[0].detail` truthy, AND `"segment exited 1" in result.rows[0].detail.split("\n", 1)[0]` (structural + narrow format pin, per Critic M3) |
| 3 | `main()` returns 0 / 1 / 2 for the three documented paths | `& $PY -m pytest tests/methodology/test_shippability_runner_execution.py::test_main_returns_0_on_all_pass tests/methodology/test_shippability_runner_execution.py::test_main_returns_1_on_any_fail tests/methodology/test_shippability_runner_execution.py::test_main_returns_2_on_missing_catalog -q` all green |
| 4 | Coverage: `run_catalog` AND `main` invoked directly | `& $PY -c "import ast, pathlib; t = ast.parse(pathlib.Path('tests/methodology/test_shippability_runner_execution.py').read_text(encoding='utf-8')); names = {n.id if isinstance(n, ast.Name) else (n.attr if isinstance(n, ast.Attribute) else '') for n in ast.walk(t)}; assert 'run_catalog' in names and 'main' in names; print('OK')"` prints `OK` |
| 5 | BCR-1 round-trip injects `- **Addressed:** slice-055-…` line at correct position | After `/reflect`, `& $PY -c "import re, pathlib; t = pathlib.Path('diagnose-out/backlog.md').read_text(encoding='utf-8'); m = re.search(r'(### SC-005 .+?)(### SC-006 )', t, re.DOTALL); assert m, 'SC-005 block not found'; block = m.group(1); evidence_bullets = [mm.start() for mm in re.finditer(r'^  - ', block, re.MULTILINE)]; assert evidence_bullets, 'no Evidence sub-list bullets in SC-005 block'; last_ev_pos = evidence_bullets[-1]; addr_pos = block.find('- **Addressed:** slice-055-add-shippability-runner-execution-tests'); assert addr_pos > last_ev_pos, f'Addressed must be AFTER last Evidence sub-bullet (addr={addr_pos}, last_ev={last_ev_pos})'; print('OK')"` prints `OK` (anchors on LAST `^  - ` sub-bullet position, restoring the slice-054 AC4 contract — Critic B2 fix) |

## Must-not-defer

- [ ] Tests use **real `subprocess.run`** through `run_catalog()` — NOT mocked (the SC-005 evidence is "untested EXECUTION logic"; mocking subprocess.run would defeat the point and the new test would be vacuous).
- [ ] The tmp-catalog markdown matches `_catalog_rows` parser expectations: a 6-column markdown table with header + `|---|...|---|` separator + at least one data row whose cells map to `[#, slice-name, description, human-cmd, time-budget, machine-cmd]`. Use a real-shaped fixture, not a one-cell hack.
- [ ] Tmp catalogs constructed in tests must use `tmp_path` (pytest fixture) — never write into the live `architecture/shippability.md`.
- [ ] Machine-cmd cells in tmp catalogs use `<interp>` (per SRSC-1's canonical interpreter placeholder, `_normalize_interp` substitutes `sys.executable`) — proves the normalization is exercised, not bypassed.
- [ ] **FAIL-branch Machine-cmd cell uses a `;`-free Python statement** (e.g. `<interp> -c "raise SystemExit(1)"`) — `tools.shippability_decoupling_audit._segments` does a naive `machine_cmd.split(";")` BEFORE `shlex.split` (verified empirically at /critique B1: `<interp> -c "import sys; sys.exit(1)"` segments to `['<interp> -c "import sys', 'sys.exit(1)"']` and both halves `ValueError` on `shlex.split`). Any future test fixture that adds a multi-statement Python body MUST either use a `;`-free form (preferred: `raise SystemExit(N)` / `exit(N)`) or split into multiple semicolon-separated segments deliberately.
- [ ] Direct symbol calls (`runner.run_catalog(...)`, `runner.main([...])`) — not only via `subprocess.run([sys.executable, "-m", "tools.shippability_runner", ...])` — so the import path and in-process state are exercised (closes the literal SC-005 evidence claim).
- [ ] BCR-1 `**Closes:** SC-005` sentinel header present in this mission-brief (above) and re-asserted in `/reflect` per slice-053 ADR-055 contract.
- [ ] BCR-1 position-pin anchors on the **last `^  - ` Evidence sub-bullet position**, NOT the `**Evidence:**` header position — preserves the slice-054 AC4 precedent (verified at /critique B2: `rfind('**Evidence:**')` would silently pass with `Addressed` placed BEFORE the first sub-bullet; only `^  - ` finditer + `[-1]` anchors on the LAST sub-bullet, restoring the contract).
- [ ] OSDG-1: no SKILL.md edits in this slice (test-only change) — no drift-guard re-sync needed; pre-flight `& $PY -m tools.skill_drift_audit` should remain clean.

## Out of scope

- Refactoring `tools/shippability_runner.py` itself (no API change; test-coverage slice only).
- Adding tests for `_format_human()` (cosmetic; not on the SC-005 finding).
- Other backlog candidates (SC-002, SC-024, etc.) — each their own slice per BCR-1.
- Promoting `_segments()` reuse-identity assertions (already pinned by `test_shippability_runner_segment_contract.py`).
- Any change to `architecture/shippability.md` (no new row needed; tests bring their own tmp catalogs).
- Minting a new methodology rule — slice-054 minted PVFS-1; slice-055 is pure test-coverage hardening of an existing gate (SRSC-1).

## Dependencies

- Prior slices:
  - [[slice-038-add-srsc-1-shippability-runner]] — minted SRSC-1, introduced `tools/shippability_runner.py` (ADR-039)
  - [[slice-053-wire-backlog-md-into-slice-and-reflect]] — wired BCR-1 sentinel → `/reflect` round-trip path used here
  - [[slice-054-fix-pyproject-toml-version-drift]] — first BCR-1 end-to-end dogfood (SC-001); this slice is the second
- Vault refs:
  - [[architecture/decisions/ADR-039]] — SRSC-1 canonical Step-5.5 runner
  - [[architecture/decisions/ADR-055]] — BCR-1 backlog round-trip discipline
- Risk register: (no active high-band risk; SC-005 itself is the retired item)
- Backlog: `diagnose-out/backlog.md` SC-005 (HIGH severity, large blast, zero-dep, owner-confirmed)

## Mid-slice smoke gate

After the PASS-branch test + FAIL-branch test are written (~50% of build, before adding `main()` exit-code tests + verification-plan rows 3/4), run:

```powershell
& $PY -m pytest tests/methodology/test_shippability_runner_execution.py::test_run_catalog_pass_row_records_pass tests/methodology/test_shippability_runner_execution.py::test_run_catalog_fail_row_records_fail -q
```

Expected: both green; PASS-row test asserts `passed=1 failed=0`; FAIL-row test asserts `failed=1 passed=0`. If either fails (e.g., tmp-catalog markdown doesn't parse, `<interp>` substitution doesn't fire, `subprocess.run` blocks): STOP, diagnose, do not continue to AC3/AC4.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] Must-not-defer list fully addressed
- [ ] `& $PY -m tools.build_checks_audit` clean (BC-1)
- [ ] `& $PY -m tools.risk_register_audit architecture/risk-register.md` clean (RR-1)
- [ ] `& $PY -m tools.critique_agent_drift_audit --repo-root .` clean (CAD-1)
- [ ] `& $PY -m tools.plugin_manifest_audit` clean (PMI-1)
- [ ] `& $PY -m tools.skill_drift_audit` clean (OSDG-1 / mini-CAD)
- [ ] `& $PY -m tools.critique_review_audit` clean (DR-1)
- [ ] `& $PY -m tools.test_first_audit` — N/A this slice (`Test-first: false`); audit should not flag
- [ ] `& $PY -m tools.walking_skeleton_audit` — N/A (`Walking-skeleton: false`)
- [ ] `& $PY -m tools.exploratory_charter_audit` — N/A (`Exploratory-charter: false`)
- [ ] `& $PY -m tools.cross_spec_parity_audit` clean (CSP-1)
- [ ] `& $PY -m tools.supersede_audit` clean (SUP-1)
- [ ] `& $PY -m tools.mock_budget_lint` clean (LINT-MOCK-1/2/3) — tests use real subprocess, no mock budget exercised
- [ ] `& $PY -m tools.shippability_runner architecture/shippability.md` clean (the runner itself — dogfood check that adding tests for it didn't break anything)
- [ ] `& $PY -m tools.branch_workflow_audit` clean (BRANCH-1) — slice ran on `slice/055-add-shippability-runner-execution-tests` branch
- [ ] `& $PY -m tools.pipeline_chain_audit` clean (PCA-1)
- [ ] `/drift-check` passes (vault ↔ code aligned)
- [ ] Mid-slice smoke still passes (no regression on AC1/AC2 tests after AC3/AC4 added)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] BCR-1 `**Closes:** SC-005` sentinel present in mission-brief (this line is the trigger for `/reflect` round-trip)
