# Validation: Slice 055 add-shippability-runner-execution-tests

**Date**: 2026-05-21
**Result**: PASS (5/5 ACs PASS for slice's own scope; one user-approved-deferred shippability regression on an unrelated pre-existing failure — confirmed not a slice-055 regression by reproduction on `master`)

## Per-criterion results

### AC1: New test module exists with ≥4 distinct test functions exercising `run_catalog()` (PASS + FAIL branches) AND `main()` (exit codes 0 / 1 / 2)

- **Status**: PASS
- **Evidence**:

```
$ & $PY -m pytest tests/methodology/test_shippability_runner_execution.py --collect-only -q
tests/methodology/test_shippability_runner_execution.py::test_run_catalog_pass_row_records_pass
tests/methodology/test_shippability_runner_execution.py::test_run_catalog_fail_row_records_fail
tests/methodology/test_shippability_runner_execution.py::test_main_returns_0_on_all_pass
tests/methodology/test_shippability_runner_execution.py::test_main_returns_1_on_any_fail
tests/methodology/test_shippability_runner_execution.py::test_main_returns_2_on_missing_catalog

5 tests collected in 0.04s

$ & $PY -c "import ast, pathlib; t = ast.parse(...); tests = [n.name for n in t.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]; assert len(tests) >= 4, ...; print(f'OK {len(tests)} tests')"
OK 5 tests
```

- **Notes**: 5 tests collected (≥4 minimum). All test names match the design.md `What's new` enumeration (long-form `_records_pass` / `_records_fail` suffix per Critic M1 ACCEPTED-FIXED — would have collected zero if the short-form drift had survived).

### AC2: FAIL branch records `failed=1, passed=0, rows_run=1, status=="FAIL", line>0, detail` truthy + first-line substring `"segment exited 1"`

- **Status**: PASS
- **Evidence**:

```
$ & $PY -m pytest tests/methodology/test_shippability_runner_execution.py::test_run_catalog_fail_row_records_fail -v
tests/methodology/test_shippability_runner_execution.py::test_run_catalog_fail_row_records_fail PASSED [100%]
============================== 1 passed in 0.14s ==============================
```

- **Notes**: Structural + narrow first-line substring assertions both green. The test uses `<interp> -c "raise SystemExit(1)"` (`;`-free per Critic B1 fix), so `_segments` produces 1 segment, `shlex.split` returns `['<interp>', '-c', 'raise SystemExit(1)']`, `_normalize_interp` substitutes `sys.executable`, subprocess exits with returncode 1, FAIL branch records `f"segment exited 1: '...'\n..."` — the first line contains `"segment exited 1"` literally. Format-string regression at `tools/shippability_runner.py:151` would be caught by either the structural pins OR the narrow first-line check (defense in depth per slice-038 m2 lesson).

### AC3: `main()` returns 0 / 1 / 2 for the three documented paths

- **Status**: PASS
- **Evidence**:

```
$ & $PY -m pytest \
    tests/methodology/test_shippability_runner_execution.py::test_main_returns_0_on_all_pass \
    tests/methodology/test_shippability_runner_execution.py::test_main_returns_1_on_any_fail \
    tests/methodology/test_shippability_runner_execution.py::test_main_returns_2_on_missing_catalog -v

tests/methodology/test_shippability_runner_execution.py::test_main_returns_0_on_all_pass PASSED [ 33%]
tests/methodology/test_shippability_runner_execution.py::test_main_returns_1_on_any_fail PASSED [ 66%]
tests/methodology/test_shippability_runner_execution.py::test_main_returns_2_on_missing_catalog PASSED [100%]
============================== 3 passed in 0.24s ==============================
```

- **Notes**: Three direct `runner.main([args])` calls exercise (a) `return 1 if result.failed else 0` exit-0 path (no failed rows), (b) same line's exit-1 path (≥1 failed row — the line SC-005 evidence specifically names), (c) `usage error: catalog not found → return 2` path at `tools/shippability_runner.py:193-195`. All three pre-fix-untested CLI exit paths are now pinned.

### AC4: `run_catalog` AND `main` invoked directly (not only via subprocess)

- **Status**: PASS
- **Evidence**:

```
$ & $PY -c "import ast, pathlib; t = ast.parse(pathlib.Path('tests/methodology/test_shippability_runner_execution.py').read_text(encoding='utf-8')); names = {n.id if isinstance(n, ast.Name) else (n.attr if isinstance(n, ast.Attribute) else '') for n in ast.walk(t)}; assert 'run_catalog' in names and 'main' in names; print(f'OK both symbols present in {pathlib.Path(\"tests/methodology/test_shippability_runner_execution.py\").name}')"
OK both symbols present in test_shippability_runner_execution.py
```

- **Notes**: AST walk confirms both symbols appear in the test module. Closes the literal SC-005 evidence-line claim `"run_catalog() is never called in any test"` — it is now called by 2 tests (AC1/AC2) directly with `repo_root=tmp_path`, and `main` is called by 3 tests (AC3) directly with CLI-style argv lists. No subprocess wrapping; in-process semantics fully exercised.

### AC5: BCR-1 round-trip closes SC-005 — input-axis verified at /validate; output-axis fires at /reflect

- **Status**: PASS (input-axis at /validate; output-axis /reflect-deferred per design.md "BCR-1 round-trip plumbing" bifurcation)
- **Evidence (input-axis at /validate-time)**:

```
$ grep -n "^\*\*Closes:\*\* SC-005" architecture/slices/slice-055-add-shippability-runner-execution-tests/mission-brief.md
3:**Closes:** SC-005
  -> sentinel present at mission-brief

$ & $PY -c "import re, pathlib; ... last_ev_pos = evidence_bullets[-1]; addr_pos = block.find('- **Addressed:** slice-055-...'); ..."
  -> anchor mechanic clean: last_ev_pos=1185; addr_pos=-1 (expected -1 pre-/reflect; injection fires at /reflect)
```

- **Evidence (output-axis at /reflect-time — will fire on next skill)**:
  - mission-brief.md Verification plan row 5 carries the canonical python one-liner that, on `/reflect` injection, will assert `addr_pos > last_ev_pos` against the real backlog.md SC-005 block.
  - Mechanic re-verified pre-/reflect: anchor `re.finditer(r'^  - ', block, re.MULTILINE)[-1]` resolves to position 1185 (the LAST `^  - ` Evidence sub-bullet of the SC-005 block), which is what the post-/reflect Addressed-line position must exceed.

- **Notes**: AC5 bifurcates per slice-054 AC4 precedent — input-contract (sentinel present + anchor mechanic clean) verifiable at /validate-slice; output-contract (actual Addressed-line injected at the right position) verifiable at /reflect-time only. Per the skill bifurcation pattern (slice-054 reflection "Aggregated lessons": "AC4-class /reflect-deferred output-axis verification pattern works"), input-axis PASS here is the correct disposition; /reflect's Step 5b machinery (per ADR-055 / BCR-1) will execute the injection and verify the output contract.

## Multi-instance validation

**Required?**: no (test-coverage slice; no multi-user, multi-device, or sync surface)

**Result**: not-applicable

## VAL-1 layered safety checks (Step 5b)

```
$ & $PY -m tools.validate_slice_layers \
    --slice architecture/slices/slice-055-add-shippability-runner-execution-tests \
    --changed-files tests/methodology/test_shippability_runner_execution.py \
    --imports-allowlist tests

VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).

Clean — both layers passed.
```

Layer A (credential scan): clean — no secrets in the new file.
Layer B (dependency hallucination): clean — all imports (`pathlib.Path`, `tools.shippability_runner`) resolve to stdlib or declared-internal modules.

## WS-1 walking-skeleton audit (Step 5c)

Not applicable (`**Walking-skeleton**: false` in mission-brief frontmatter). Audit returns `not enabled`; gate passes silently per default-off semantics.

## ETC-1 exploratory-charter audit (Step 5d)

Not applicable (`**Exploratory-charter**: false` in mission-brief frontmatter). Audit returns `not enabled`; gate passes silently per default-off semantics.

## Shippability regressions (Step 5.5)

**Pre-catalog gates**:

```
$ & $PY -m tools.shippability_decoupling_audit architecture/shippability.md
SCMD-1 audit: clean. 54 row(s); 515 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=513.

$ & $PY -m tools.shippability_path_audit architecture/shippability.md
Shippability path audit (PTFCD-1/PTFFD-1): clean. 54 row(s), 303 test-path token(s) — all files and cited functions exist.
```

Both pre-catalog gates pass — the catalog itself is well-formed; the regression below is in the cited test's logic, not in the catalog row's shape.

**SRSC-1 canonical runner**:

```
$ & $PY -m tools.shippability_runner architecture/shippability.md
Shippability catalog run: 54 row(s), 53 PASS, 1 FAIL

FAILED:
  ... tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant ...
Cannot proceed to /reflect. Fix the regression, OR get user approval to defer the fix to a new slice.

Exit code: 1
```

**Single failing row**: `tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant`

**Root cause**: stale hard-coded path. The test reads:

```python
# tests/methodology/test_bcr_1_round_trip_end_to_end.py:43
SLICE_054_DIR = REPO_ROOT / "architecture" / "slices" / "slice-054-fix-pyproject-toml-version-drift"
```

But slice-054 has been archived by `/reflect` to `architecture/slices/archive/slice-054-fix-pyproject-toml-version-drift/`. The `SLICE_054_DIR` constant needs an `archive/` insertion.

**Origin**: introduced by slice-054 (a BCR-1 first-dogfood input-axis invariant pin); the archival post-slice-054 broke the path.

**Pre-existence proof**: at /build-slice time, checked out `master` (with `git stash --include-untracked` of slice-055's new test file + vault changes) and reran the failing test — same FAILURE on `master` with zero slice-055 changes applied. Then `git checkout slice/055-...` + `git stash pop` restored slice-055's state intact (all 5 slice-055 tests still pass post-roundtrip). Confirmed NOT a slice-055 regression.

**Slice-055's interaction**: zero. The slice did not modify, import from, or otherwise interact with `tests/methodology/test_bcr_1_round_trip_end_to_end.py` or with slice-054's location. Slice-055's new tests in `tests/methodology/test_shippability_runner_execution.py` are entirely independent.

**Disposition**: **DEFERRED — user-approved** at /build-slice TRI-1 structured-options gate ("Defer to next slice"). The fix targets the `SLICE_054_DIR` path constant (a one-line edit) and an archive-aware probe to prevent recurrence, scoped to a tiny fix slice (likely slice-056). Per CLAUDE.md "Refactors need a slice", the fix cannot ride along in slice-055.

**Why this validates as PASS aggregate**: slice-055's own scope (5 ACs) is fully delivered; the runner's detection of this pre-existing failure is precisely what the new test coverage was *for* — the runner correctly returned exit code 1 with the right detail format, which is itself slice-055's load-bearing contract (my `test_main_returns_1_on_any_fail` would catch a regression on that exit-code contract). The shippability catalog is doing its job; the failing row is a separate latent defect from an earlier slice's `/reflect` archival, with user-approved deferral logged here per the skill's "Fix OR user-approved deferral" protocol.

## Reality surprises

None of slice-055's own work surfaced surprises — the design's empirical pre-grounding (Critic B1 + B2 caught and fixed pre-build via empirical execution) meant the build executed cleanly with zero deviation.

The shippability regression (above) **is** a reality surprise from the systemic perspective — it surfaces that `/reflect`'s archival of slice-054 broke a test from slice-054 itself that hard-coded the pre-archival path. The implication for `/reflect` and the test-authoring discipline:

- Tests that pin invariants on a slice's own vault files MUST be archive-aware — either use a path-resolving helper that handles both active and archive locations, OR run only at /reflect time (before archival), OR the test should be marked as "pre-archive only" and the catalog row should reflect that.
- This is a class signal worth a future `/critic-calibrate` discussion (N=1 today; if a second archive-class regression emerges, it warrants a new methodology rule).

**Recommendation for /reflect**: capture this as a discovered class (archive-aware vault-test discipline) and surface to the user; the slice-056 fix should both repair the SLICE_054_DIR path AND introduce the archive-aware-probe pattern so the next BCR-1 round-trip pin slice doesn't repeat the trap.

## Aggregate verdict

**PASS**. All 5 ACs of slice-055's own scope are fully delivered with evidence. The shippability runner self-dogfood correctly detected one pre-existing failure (not introduced by slice-055; verified on master); user-approved deferral logged per skill protocol. Auto-advance to `/reflect` is appropriate.
