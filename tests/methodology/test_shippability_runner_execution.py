"""SC-005 — execution-level pins for `tools.shippability_runner.run_catalog`
and `main`. Slice-055 (see `architecture/slices/slice-055-...`); closes the
owner-confirmed `diagnose-out/backlog.md` SC-005 ("HIGH severity, large blast,
zero-dep") — `run_catalog()` shells out every command in the shippability
catalog and decides pass/fail per row, yet today only the `_segments()`
parsing helper is exercised (by `test_shippability_runner_segment_contract`);
`run_catalog()` and `main()` themselves have **zero** test-module predecessors
in the graphify graph. The pipeline guarantee "shippability regressions block
/reflect" rests entirely on that untested execution logic — until now.

Pinned contracts (one path per test):

1. `run_catalog(catalog, repo_root=tmp_path)` PASS branch — a tmp catalog
   whose single data row's Machine-cmd cell exits 0 records `passed += 1`
   on the live `subprocess.run` round-trip.
2. `run_catalog(catalog, repo_root=tmp_path)` FAIL branch — a tmp catalog
   whose data row exits non-zero records `failed += 1` with the canonical
   `f"segment exited {rc}: {seg!r}\\n{tail.strip()}"` detail format. Both
   structural (`status="FAIL"`, `line>0`, `detail` truthy) AND a narrow
   first-line substring `"segment exited 1"` are asserted, so the test
   fails informatively if the runner's debug-format string is later
   edited (slice-038 m2 load-bearing-test lesson — narrow-only substring
   pins are brittle; structural + narrow together survive cosmetic format
   changes).
3. `main([passing_catalog]) == 0`  — exit-code 0 path.
4. `main([failing_catalog]) == 1`  — exit-code 1 path (the literal
   `return 1 if result.failed else 0` line at
   `tools/shippability_runner.py:203` that SC-005 evidence names).
5. `main([nonexistent_path]) == 2` — exit-code 2 path (the
   `usage error: catalog not found` line at
   `tools/shippability_runner.py:194-195` that SC-005 evidence names).

The tmp catalog uses a real-shaped 6-column shippability table parseable by
`tools.shippability_decoupling_audit._catalog_rows` (`_MACHINE_CMD_IDX=5`).
Machine-cmd cells use the `<interp>` canonical interpreter placeholder so
`_normalize_interp` substitutes `sys.executable` — the normalization itself
is exercised, not bypassed.

**Important fixture constraint** (slice-055 /critique B1, empirically verified):
`_segments` does a naive `machine_cmd.split(";")` at
`tools/shippability_decoupling_audit.py:212` BEFORE any shell-aware
tokenization. So a Machine-cmd cell like `<interp> -c "import sys; sys.exit(1)"`
would split into `['<interp> -c "import sys', 'sys.exit(1)"']` and BOTH halves
`ValueError` on `shlex.split`. FAIL-branch fixtures MUST therefore use a
`;`-free Python statement — `<interp> -c "raise SystemExit(1)"` or
`<interp> -c "exit(1)"`. Any future test that adds a multi-statement Python
body MUST either be `;`-free or split deliberately into multiple
semicolon-separated backtick-wrapped sub-commands.

Per BCR-1 (ADR-055): mission-brief carries `**Closes:** SC-005` sentinel
header; `/reflect` round-trips the candidate via the BCR-1-mandated
position-pinned injection at the LAST `^  - ` Evidence sub-bullet of the
SC-005 block in `diagnose-out/backlog.md`.
"""
from __future__ import annotations

from pathlib import Path

import tools.shippability_runner as runner


# --- Tmp-catalog fixture helper ----------------------------------------------

def _make_catalog(tmp_path: Path, machine_cmd: str) -> Path:
    """Write a minimum-viable 6-column shippability-catalog markdown into
    `tmp_path` and return its path.

    `machine_cmd` is the bare command (no surrounding backticks); the helper
    wraps it in the cell-level backticks the catalog convention uses
    (`_catalog_rows` itself parses unconditionally — backticks are stripped
    later per-segment by `_segments` at
    `tools/shippability_decoupling_audit.py:213`; the wrap exists so the
    fixture matches real-row shape, not because the parser rejects bare cells
    — per slice-055 /critique m2 layering clarification).

    **`machine_cmd` constraint** (slice-055 /critique B1): MUST be `;`-free
    OR explicitly split into backtick-wrapped sub-commands separated by `;`.
    `_segments` does `machine_cmd.split(";")` BEFORE `shlex.split` — any
    bare `;` inside a Python `-c` body crashes both halves' `shlex.split`
    with `ValueError: No closing quotation`. Use
    `<interp> -c "raise SystemExit(N)"` for single-statement non-zero exits.
    """
    catalog = tmp_path / "shippability.md"
    # Real-shaped 6-column table matching architecture/shippability.md row #1
    # exactly (cells: # | Slice | Description | Human-cmd | Time | Machine-cmd).
    catalog.write_text(
        "# Test catalog\n"
        "\n"
        "| # | Slice | Description | Human-cmd | Time | Machine-cmd |\n"
        "|---|-------|-------------|-----------|------|-------------|\n"
        f"| 1 | slice-055-add-shippability-runner-execution-tests | "
        f"tmp catalog row | `human form` | <1s | `{machine_cmd}` |\n",
        encoding="utf-8",
    )
    return catalog


# --- AC1 / AC2: run_catalog PASS branch + FAIL branch ------------------------

def test_run_catalog_pass_row_records_pass(tmp_path: Path):
    """A tmp catalog whose data row's Machine-cmd cell exits 0 records
    `passed += 1` via the live `subprocess.run` round-trip.

    Pins the PASS branch path (`tools/shippability_runner.py:155-157`):
    `if row_ok: result.passed += 1; result.rows.append(RowResult(row, "PASS", line))`.
    """
    catalog = _make_catalog(tmp_path, '<interp> -c "pass"')

    result = runner.run_catalog(catalog, repo_root=tmp_path)

    assert result.rows_run == 1, result
    assert result.passed == 1, result
    assert result.failed == 0, result
    assert len(result.rows) == 1, result
    assert result.rows[0].status == "PASS", result.rows[0]
    assert result.rows[0].line > 0, result.rows[0]


def test_run_catalog_fail_row_records_fail(tmp_path: Path):
    """A tmp catalog whose data row's Machine-cmd cell exits non-zero records
    `failed += 1` with the canonical `f"segment exited {rc}: {seg!r}\\n..."`
    detail format. Asserts BOTH structural fields AND the narrow first-line
    substring so the test fails informatively if the format string at
    `tools/shippability_runner.py:151-152` is later edited (slice-038 m2
    load-bearing-test lesson).

    Note: the Machine-cmd cell uses `raise SystemExit(1)` rather than
    `import sys; sys.exit(1)` because `_segments` does a naive `;`-split
    BEFORE `shlex.split` (slice-055 /critique B1, empirically verified).
    """
    catalog = _make_catalog(tmp_path, '<interp> -c "raise SystemExit(1)"')

    result = runner.run_catalog(catalog, repo_root=tmp_path)

    # Structural pins (survive cosmetic format-string edits at runner:151-152)
    assert result.rows_run == 1, result
    assert result.failed == 1, result
    assert result.passed == 0, result
    assert len(result.rows) == 1, result
    assert result.rows[0].status == "FAIL", result.rows[0]
    assert result.rows[0].line > 0, result.rows[0]
    assert result.rows[0].detail, result.rows[0]

    # Narrow format pin scoped to FIRST line only (survives future tail
    # appends; catches direct edits to the leading f-string format).
    first_line = result.rows[0].detail.split("\n", 1)[0]
    assert "segment exited 1" in first_line, (
        f"FAIL detail's first line must contain 'segment exited 1' "
        f"(format pin on tools/shippability_runner.py:151); got: "
        f"{first_line!r}"
    )


# --- AC3: main() returns 0 / 1 / 2 for the three documented paths ------------

def test_main_returns_0_on_all_pass(tmp_path: Path):
    """`main()` returns 0 when every data row's Machine-cmd cell exits 0
    (`tools/shippability_runner.py:203`: `return 1 if result.failed else 0`,
    no failed rows → 0)."""
    catalog = _make_catalog(tmp_path, '<interp> -c "pass"')

    rc = runner.main([str(catalog)])

    assert rc == 0, f"main with all-pass catalog must return 0, got {rc}"


def test_main_returns_1_on_any_fail(tmp_path: Path):
    """`main()` returns 1 when at least one data row's Machine-cmd cell exits
    non-zero (`tools/shippability_runner.py:203` literal:
    `return 1 if result.failed else 0`, ≥1 failed → 1). This is the line
    SC-005 evidence specifically names as untested."""
    catalog = _make_catalog(tmp_path, '<interp> -c "raise SystemExit(1)"')

    rc = runner.main([str(catalog)])

    assert rc == 1, f"main with any-fail catalog must return 1, got {rc}"


def test_main_returns_2_on_missing_catalog(tmp_path: Path):
    """`main()` returns 2 (usage error) when the catalog path does not exist
    (`tools/shippability_runner.py:193-195`:
    `if not catalog_path.is_file(): sys.stderr.write(...); return 2`)."""
    nonexistent = tmp_path / "no-such-catalog.md"
    assert not nonexistent.exists(), "tmp_path pre-state must be clean"

    rc = runner.main([str(nonexistent)])

    assert rc == 2, f"main with missing catalog must return 2, got {rc}"
