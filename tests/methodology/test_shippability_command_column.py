"""SCMD-1 check (a) — machine-stable command column.

Per SCMD-1 (slice-031, split-label 030B; ADR-031). Covers AC3 + the v2-M-add-A
prose-discrimination negative fixtures. Written test-first (TF-1):

- `test_every_row_has_machine_stable_command_or_violation` is WRITTEN-FAILING
  until T3 adds the 6th `Machine-cmd` column to the real catalog (pre-T3 the
  audit reports `missing-machine-cmd` for every row).
- The synthetic-fixture behavior pins (missing-column, leading-bareword prose,
  two-clean-`;`-pass) exercise the net-new discriminator deterministically and
  are the M-add-A regression guard (the shared `_TEST_PATH_RE` predicate
  provably cannot reject prose — only SCMD-1's anchored segment validator can).
"""
from __future__ import annotations

from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.shippability_decoupling_audit import audit, _SEGMENT_RE, _segments

_CATALOG = REPO_ROOT / "architecture" / "shippability.md"


def _kinds(violations) -> set[str]:
    return {v.kind for v in violations}


def test_every_row_has_machine_stable_command_or_violation():
    """WRITTEN-FAILING until T3: every catalog data row must carry a
    grammar-conformant Machine-cmd cell — no `missing-machine-cmd` and no
    `prose-segment` violations against the real catalog."""
    result = audit(_CATALOG)
    bad = [v for v in result.violations
           if v.kind in {"missing-machine-cmd", "prose-segment"}]
    assert not bad, (
        f"{len(bad)} machine-cmd structural violation(s) — first: "
        f"{bad[0].kind} row {bad[0].row}: {bad[0].detail}"
    )


def test_missing_column_is_violation_not_silent_ptfcd_skip(tmp_path: Path):
    """A data row with only 5 columns (no Machine-cmd) MUST raise a
    `missing-machine-cmd` violation — never a silent skip (a silent skip would
    also disable PTFCD-1 for that row — B3)."""
    cat = tmp_path / "shippability.md"
    cat.write_text(
        "# Shippability Catalog\n\n"
        "| # | Slice | Critical path | Command | Runtime |\n"
        "|---|-------|---------------|---------|---------|\n"
        "| 1 | slice-x | crit | `python -m pytest tests/x.py -q` | <1s |\n",
        encoding="utf-8",
    )
    result = audit(cat)
    assert result.rows_scanned == 1
    assert "missing-machine-cmd" in _kinds(result.violations), (
        "a 5-column data row must be a missing-machine-cmd violation, "
        "not silently skipped"
    )


def test_leading_bareword_prose_cell_is_violation(tmp_path: Path):
    """v2-M-add-A: a prose cell like `Commands: \\`python -m pytest ...\\``
    MUST be rejected. The shared `_TEST_PATH_RE` predicate would NOT reject
    it (it finds `pytest` and extracts the token, ignoring the prefix); only
    SCMD-1's interpreter-anchored full-cell validator rejects it."""
    cat = tmp_path / "shippability.md"
    cat.write_text(
        "| # | Slice | Critical path | Command | Runtime | Machine-cmd |\n"
        "|---|-------|---------------|---------|---------|-------------|\n"
        "| 1 | slice-x | crit | c | <1s | "
        "Commands: `python -m pytest tests/x.py -q` |\n",
        encoding="utf-8",
    )
    result = audit(cat)
    assert "prose-segment" in _kinds(result.violations), (
        "a leading-bareword prose Machine-cmd cell must be a prose-segment "
        "violation"
    )


def test_two_clean_semicolon_separated_invocations_pass(tmp_path: Path):
    """v2-M1/M-add-A: row #28's two distinct invocations must be expressible
    as a `;`-separated Machine-cmd WITHOUT a lossy single-`pytest` merge —
    both segments are clean → no prose/missing violation for this row."""
    cat = tmp_path / "shippability.md"
    cat.write_text(
        "| # | Slice | Critical path | Command | Runtime | Machine-cmd |\n"
        "|---|-------|---------------|---------|---------|-------------|\n"
        "| 28 | slice-028 | crit | c | <5s | "
        "`<interp> -m pytest tests/methodology/test_utf8_stdout_regression.py "
        "-q` ; `<interp> -m pytest "
        "tests/methodology/test_methodology_changelog.py -k v_0_42_0 -q` |\n",
        encoding="utf-8",
    )
    result = audit(cat)
    row28 = [v for v in result.violations if v.row == "28"
             and v.kind in {"missing-machine-cmd", "prose-segment"}]
    assert not row28, (
        f"two clean ;-separated invocations must pass check (a); got {row28}"
    )


def test_segment_regex_rejects_prose_accepts_clean():
    """Direct unit pin on the net-new discriminator (M-add-A): the anchored
    `_SEGMENT_RE` accepts a clean invocation and rejects a prose prefix."""
    assert _SEGMENT_RE.fullmatch(
        "<interp> -m pytest tests/methodology/test_x.py::test_y -q")
    assert _SEGMENT_RE.fullmatch(
        "C:/u/.venv/Scripts/python.exe -m pytest tests/a/b.py --no-header -q")
    assert not _SEGMENT_RE.fullmatch(
        "Commands: `python -m pytest tests/x.py -q`")
    assert not _SEGMENT_RE.fullmatch("see the docs for how to run this")
    # `;`-split happens before regex; each segment trimmed:
    segs = _segments("`<interp> -m pytest tests/a.py -q` ; "
                     "`<interp> -m pytest tests/b.py -q`")
    assert len(segs) == 2 and all(_SEGMENT_RE.fullmatch(s) for s in segs)
