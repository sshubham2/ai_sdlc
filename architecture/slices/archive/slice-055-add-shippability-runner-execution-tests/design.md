# Design: Slice 055 add-shippability-runner-execution-tests

**Date**: 2026-05-21
**Mode**: Standard

## What's new

- One new pytest module: `tests/methodology/test_shippability_runner_execution.py`
- 5 new test functions exercising the two structurally untested entrypoints of `tools/shippability_runner.py`:
  - `test_run_catalog_pass_row_records_pass` — PASS branch via real `subprocess.run`
  - `test_run_catalog_fail_row_records_fail` — FAIL branch via real `subprocess.run`
  - `test_main_returns_0_on_all_pass` — `main()` exit-code 0 path
  - `test_main_returns_1_on_any_fail` — `main()` exit-code 1 path (the `return 1 if result.failed else 0` line SC-005 names)
  - `test_main_returns_2_on_missing_catalog` — `main()` exit-code 2 path (the `usage error: catalog not found` line SC-005 names)
- One in-module helper `_make_catalog(tmp_path, machine_cmd: str) -> Path` that writes a minimum-viable 6-column shippability table (header + separator + one data row) parseable by `tools.shippability_decoupling_audit._catalog_rows`. The helper IS internal to the test file — not exported, not reused by other tests.

## What's reused

- `tools/shippability_runner.py` — `run_catalog`, `main`, `_normalize_interp`, `RunResult`, `RowResult` (production code unchanged — this slice introduces zero `tools/` modifications)
- `tools.shippability_decoupling_audit._catalog_rows` / `_machine_cmd_cell` (transitively via runner) — the catalog markdown parser the runner consumes
- `tools.shippability_path_audit._find_repo_root` (transitively via `main`, which calls `run_catalog` without an explicit `repo_root`)
- `pytest`'s `tmp_path` fixture (already used pervasively under `tests/methodology/`)
- `sys.executable` for cross-platform interpreter resolution — `<interp>` placeholder in tmp Machine-cmd cells maps to `sys.executable` via `_normalize_interp` (proves the normalization is exercised, not bypassed)
- Direct-call pattern: `assert main([str(path)]) == exit_code` per `tests/methodology/test_critique_review_prerequisite_audit.py:74,94,196,213` (zero subprocess wrapping of `main` itself — `main` is the function under test, not invoked through `python -m`)
- [[ADR-039]] — SRSC-1 minted the runner; this slice closes the SRSC-1-era follow-on test gap
- [[ADR-055]] — BCR-1 round-trip discipline; the `**Closes:** SC-005` mission-brief sentinel triggers `/reflect`'s injection at slice end
- `diagnose-out/backlog.md` — SC-005 candidate block (consumed; round-tripped via `/reflect`)

## Components touched

### `tests/methodology/test_shippability_runner_execution.py` (NEW)

- **Responsibility**: pin `tools.shippability_runner.run_catalog()` and `main()` against real subprocess execution paths. Establishes that (a) the PASS branch of `run_catalog`'s row-loop records `passed += 1` on `proc.returncode == 0`, (b) the FAIL branch records `failed += 1` with a `"segment exited N"` detail string on non-zero returncode, (c) `main()` returns exit codes 0 / 1 / 2 for the three documented paths (`exit codes` section of `tools/shippability_runner.py:31-34`).
- **Lives at**: `tests/methodology/test_shippability_runner_execution.py` (created by this slice)
- **Key interactions**:
  - Imports `tools.shippability_runner as runner` (direct symbol calls, not subprocess wrapping)
  - Spawns real subprocesses via `runner.run_catalog` and `runner.main` — those internally do `subprocess.run([sys.executable, "-c", "pass" | "import sys; sys.exit(1)"], cwd=...)`. The new tests do NOT mock `subprocess.run` (mocking would defeat the entire point of SC-005, which is exactly about "untested EXECUTION logic").
  - No reach into network / filesystem outside `tmp_path` (deterministic, isolated)

## Contracts added or changed

**None.** This slice adds tests against existing-stable contracts. The SRSC-1 contract (per [[ADR-039]]) is unchanged: `run_catalog` returns a `RunResult` dataclass; `main` returns `int` (0 / 1 / 2). The new tests pin those contracts; they do not modify them.

## Data model deltas

**None.** No production-code change. The in-test helper `_make_catalog` constructs an ephemeral 6-column markdown table inside `tmp_path` — this is test fixture data, not a vault-managed entity.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_shippability_runner_execution.py` | — | — | test module — rationale: this slice introduces a TEST module (pytest is the consumer; the file IS the test). The WIRE-1 "consumer entry point + consumer test" demand is for new RUNTIME modules — peer test modules under `tests/methodology/` (e.g., `test_critique_review_prerequisite_audit.py`, `test_branch_workflow_audit.py`) follow the same convention. The production runtime module being covered (`tools/shippability_runner.py`) is unchanged. |

## Decisions made (ADRs)

**None.** This slice deliberately mints no rule and locks no decision. Per the slice-037 / slice-046 / slice-050 / slice-052 voluntary-restraint discipline ("when test-coverage retires a finding, that IS the right move — don't extend a rule, don't mint a new one"), the right artifact is the test module itself, not a methodology rule.

This is the deliberate contrast to slice-054 (which minted PVFS-1): rule-minting-and-extension only happens when a recurring failure-class needs deterministic enforcement. SC-005 is a one-shot test-coverage gap on an existing rule (SRSC-1, ADR-039 — already pinned). The right action is to write the missing tests, full stop.

## Authorization model for this slice

N/A — test-only slice. No production authorization surface touched.

## Error model for this slice

The slice does not introduce new error paths in production code. It **pins** the existing error paths of `tools.shippability_runner`:

| Path | Pinned by | What's asserted |
|------|-----------|-----------------|
| `subprocess.run(..., returncode == 0)` → row PASS | `test_run_catalog_pass_row_records_pass` | `result.passed == 1`, `result.failed == 0`, `result.rows[0].status == "PASS"`, `result.rows[0].line > 0` |
| `subprocess.run(..., returncode != 0)` → row FAIL with `f"segment exited {rc}: {seg!r}\n{tail.strip()}"` detail | `test_run_catalog_fail_row_records_fail` | structural pin: `result.failed == 1`, `result.passed == 0`, `result.rows[0].status == "FAIL"`, `result.rows[0].line > 0`, `result.rows[0].detail` truthy; narrow-format pin (separately): `"segment exited 1" in result.rows[0].detail.split("\n", 1)[0]` (the FIRST line of the detail string only — survives future appends to the tail) |
| `main()` `return 1 if result.failed else 0` (the line SC-005 evidence names) | `test_main_returns_0_on_all_pass` + `test_main_returns_1_on_any_fail` | `main([passing_catalog]) == 0`; `main([failing_catalog]) == 1` |
| `main()` `usage error: catalog not found → return 2` | `test_main_returns_2_on_missing_catalog` | `main([nonexistent_path]) == 2` |

## Test design (mechanical detail)

### Tmp catalog shape

The 6-column shippability-catalog table the runner consumes (per `tools.shippability_decoupling_audit._catalog_rows`):

```
| # | Slice | Description | Human-cmd | Time | Machine-cmd |
|---|-------|-------------|-----------|------|-------------|
| 1 | slice-055-add-shippability-runner-execution-tests | tmp PASS/FAIL row | `human form` | <1s | `<interp> -c "pass"` |
```

The Machine-cmd cell (cell 5, the last) is what `_machine_cmd_cell` returns; `_segments` splits on `;` and strips ``` `…` ``` per segment. The `<interp>` token in `_INTERP_TOKENS` (`tools/shippability_runner.py:58`) is substituted to `sys.executable` by `_normalize_interp` — the normalization itself is exercised.

### Helper signature (internal to the test file)

```python
def _make_catalog(tmp_path: Path, machine_cmd: str) -> Path:
    """Write a minimum-viable 6-column shippability-catalog markdown into tmp_path
    and return its path. machine_cmd is the bare command (no surrounding backticks);
    the helper wraps it in the cell-level backticks the catalog convention uses
    (`_catalog_rows` itself parses unconditionally — backticks are stripped later
    per-segment by `_segments` at tools/shippability_decoupling_audit.py:213; the
    wrap exists so the fixture matches real-row shape, not because the parser
    rejects bare cells — per Critic m2 layering clarification)."""
```

The helper is single-purpose, single-call-site-per-test, and lives in the test module — not under `tools/` (where it would create a new runtime surface this slice doesn't need) and not under `tests/conftest.py` (where it would be a cross-test fixture this slice's 5 tests don't justify).

**`machine_cmd` constraint (per Critic B1)**: callers MUST pass a `;`-free Python `-c` body OR an explicitly multi-segment command separated by `;` between backtick-wrapped sub-commands. `_segments` does a naive `machine_cmd.split(";")` at `tools/shippability_decoupling_audit.py:212` BEFORE any shell-aware tokenization — so any `;` inside a single Python statement (like `<interp> -c "import sys; sys.exit(1)"`) splits the cell into two halves that each `ValueError` on `shlex.split`. Use `<interp> -c "raise SystemExit(1)"` (or `<interp> -c "exit(1)"`) for single-statement non-zero exits.

### `repo_root` argument convention

- `run_catalog()` tests pass `repo_root=tmp_path` explicitly — avoids any environmental ambiguity around `_find_repo_root`'s walk-up behavior.
- `main()` tests do NOT pass `repo_root` (CLI doesn't accept it) — `main` internally calls `run_catalog(catalog_path)` which triggers `_find_repo_root(tmp_catalog)`. On the C: tmp_path hierarchy (no `.git` / `VERSION` upstream), `_find_repo_root` falls through its loop and returns `start.resolve().parent` (the catalog's parent directory, i.e., `tmp_path` itself) — same effective `cwd` as the explicit `repo_root=tmp_path` path. Tested behavior is identical; the `main` tests just exercise the discovery-fallback edge as a bonus.

### Subprocess invocations the tests will spawn

Five fast subprocess invocations across the 5 tests:

| Test | Spawned command | Expected returncode |
|------|----------------|--------------------|
| `test_run_catalog_pass_row_records_pass` | `<sys.executable> -c "pass"` | 0 |
| `test_run_catalog_fail_row_records_fail` | `<sys.executable> -c "raise SystemExit(1)"` (NOT `import sys; sys.exit(1)` — `_segments` naive-`;`-split would crash; Critic B1) | 1 |
| `test_main_returns_0_on_all_pass` | `<sys.executable> -c "pass"` | 0 |
| `test_main_returns_1_on_any_fail` | `<sys.executable> -c "raise SystemExit(1)"` | 1 |
| `test_main_returns_2_on_missing_catalog` | *(none — exit-2 path returns before `run_catalog` is invoked)* | n/a |

Each subprocess invocation is sub-100ms; total test runtime budget < 2s (well under the implicit per-file budget the existing test suite carries).

## Defensive / out-of-scope branches (not pinned by this slice)

`run_catalog` carries a third branch at `tools/shippability_runner.py:127-136` — "no Machine-cmd cell → record FAIL with the SCMD-1 pre-catalog gate warning detail". This branch is the defensive fallback for malformed rows that the SCMD-1 pre-catalog gate (`/validate-slice` Step 5.5 item 3a) is supposed to STOP before reaching the runner. Pinning it would test "what happens if the upstream gate is bypassed" — a hypothetical the SC-005 evidence does not name as the gap, and that's already covered upstream by the SCMD-1 gate's own tests. **Deliberate out-of-scope**: add later if a SCMD-1-bypass scenario actually surfaces; over-engineering to pin it pre-emptively here.

`_format_human` (the human-readable output formatter) is also untested. Out-of-scope: cosmetic; no behavioral guarantee at risk. SC-005 evidence does not name it.

## BCR-1 round-trip plumbing

This slice is the second end-to-end BCR-1 dogfood after slice-054's first.

- **Trigger**: `**Closes:** SC-005` sentinel header in `mission-brief.md` (line 3) — the canonical sentinel form per [[ADR-055]] / slice-053 M4.
- **Anchored extraction**: `/reflect` will grep `diagnose-out/backlog.md` for `### SC-005 ` (note trailing space — the SC-NNN block delimiter), locate the `**Evidence:**` sub-list, and inject `- **Addressed:** slice-055-add-shippability-runner-execution-tests on YYYY-MM-DD` immediately AFTER the **last `**Evidence:**` sub-list bullet** AND BEFORE the next `### SC-006 ` header.
- **Verification** (mission-brief AC5): a position-pinned check that anchors on the LAST `^  - ` evidence sub-bullet position via `re.finditer(r'^  - ', block, re.MULTILINE)` + `[-1]`, NOT on the `**Evidence:**` header position. The Critic B2 fix preserves the slice-054 AC4 contract: a check anchored on the `**Evidence:**` header would silently pass with `Addressed` placed BETWEEN the header and the first sub-bullet (verified by reading SC-005's actual structure in `diagnose-out/backlog.md`: line 14 is the `**Evidence:**` header, lines 15-16 are the two sub-bullets — a regression like injecting at line-15-position would falsely pass a header-only pin). The python one-liner in mission-brief.md row 5 of the verification table is the canonical form.

Per slice-053's `mentioned-vs-closes` disambiguation (M4): the trigger is the **sentinel header**, not bare mentions. The string `SC-005` appears in this design.md many times, but only the `**Closes:** SC-005` line in mission-brief.md (and re-asserted in reflection.md) fires the round-trip. The other mentions are descriptive prose, not triggers — by design.

## Risk surface for the Critic

The mandatory Critic triggers fire on `tools/**/*.py` (in-house methodology surface). This slice modifies zero `tools/` files but the *coverage target* IS `tools/shippability_runner.py` — the in-house-methodology-surface trigger still applies under the spirit of "Critic mandatory when slice scope is methodology-critical". Per the slice-006-through-slice-054 pattern (N=9+ voluntary Critic on cross-cutting methodology slices: 9/9 VALIDATED post-build with zero FALSE-ALARMs), the Critic will likely find:

- Whether the tmp-catalog markdown shape is faithful enough to a real catalog row that the parse path is genuinely exercised (slice-038's load-bearing-test lesson: a test that exercises only a fixture-shape can be vacuous if the fixture differs from the real consumer's shape).
- Whether the `"segment exited 1" in result.rows[0].detail` substring assertion is brittle to future detail-format changes (the runner currently writes `f"segment exited {proc.returncode}: {seg!r}"` plus `f"{tail.strip()}"`).
- Whether the 5-test coverage is sufficient given the SC-005 evidence wording "structurally untested" — or whether a 6th test on the no-Machine-cmd-cell defensive branch belongs in this slice (vs. out-of-scope deferral above).
- Whether the BCR-1 round-trip verification (AC5) is position-pinned strongly enough to catch the slice-053 multi-site-literal-contrast edge — slice-054's first dogfood used a position-pinned awk + line-number check; this slice's AC5 uses a python position-comparison check.

These are the surfaces I expect adversarial review to attack. Pre-emptive responses are NOT written here (the Critic gets a clean adversarial read); this section is forecast for the user, not the Critic.
