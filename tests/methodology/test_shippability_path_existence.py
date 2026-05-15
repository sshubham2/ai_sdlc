"""Tests for tools.shippability_path_audit (PTFCD-1 sub-mode (b)).

Validates that the audit:
- Flags a phantom `tests/<...>.py` token in a shippability Command cell
- Strips markdown backticks before resolving a path (slice-024 footgun)
- Does NOT flag the interpreter path, `-m`, `pytest`, `-q`, `--no-header`
  (M2-pinned predicate: only post-`pytest` tests/<...>.py tokens)

Rule reference: PTFCD-1 (slice-025 AC #2).
"""
from pathlib import Path

from tools.shippability_path_audit import audit_catalog_file

_HEADER = (
    "# Shippability Catalog\n\n"
    "| # | Slice | Critical path | Command | Runtime |\n"
    "|---|-------|--------------|---------|---------|\n"
)


def _write_catalog(tmp_path: Path, command_cell: str) -> Path:
    """Write a one-row shippability catalog whose Command cell is `command_cell`."""
    cat = _HEADER + f"| 1 | slice-x | crit path | {command_cell} | <1s |\n"
    p = tmp_path / "shippability.md"
    p.write_text(cat, encoding="utf-8")
    return p


def test_flags_phantom_command_cell_test_path(tmp_path):
    """A Command cell citing a non-existent tests/<...>.py token is flagged.

    Defect class: slice-024 cited tests/methodology/test_shippability_catalog.py
    (no such file) and it survived the whole Critic stack, dying only at
    real-command execution.
    Rule reference: PTFCD-1 (slice-025 AC #2).
    """
    catalog = _write_catalog(
        tmp_path,
        "`python -m pytest tests/methodology/test_row_999_phantom.py -q`",
    )
    result = audit_catalog_file(catalog)
    assert len(result.violations) == 1, (
        f"expected exactly one phantom citation, got {result.to_dict()}"
    )
    assert result.violations[0].token == "tests/methodology/test_row_999_phantom.py"


def test_strips_backticks_before_path_resolution(tmp_path):
    """A real path wrapped in markdown backticks resolves clean (no
    spurious FAIL from the backtick characters).

    Defect class: slice-024's first Step 5.5 run produced 23 spurious FAILs
    because Command cells were not backtick-stripped before resolution.
    Rule reference: PTFCD-1 (slice-025 AC #2; must-not-defer backtick-strip).
    """
    real = tmp_path / "tests" / "realdir"
    real.mkdir(parents=True)
    (real / "test_real_thing.py").write_text("def test_x(): pass\n", encoding="utf-8")
    # Catalog lives at tmp_path/shippability.md → repo-root fallback resolves
    # tokens relative to tmp_path. Backtick-wrap the real repo-relative path.
    catalog = _write_catalog(
        tmp_path,
        "`python -m pytest tests/realdir/test_real_thing.py::test_x -q`",
    )
    result = audit_catalog_file(catalog)
    assert result.violations == [], (
        f"backtick-wrapped real path must resolve clean; got {result.to_dict()}"
    )
    assert result.tokens_checked == 1


def test_interpreter_and_dash_m_dash_q_tokens_not_flagged(tmp_path):
    """The interpreter path, `-m`, `pytest`, `-q`, `--no-header` are NOT
    treated as test-file paths — only post-`pytest` tests/<...>.py tokens.

    Defect class (Critic M2): a broad `\\S+\\.py` predicate could mis-treat
    the interpreter path or a `-m tools.x` token as a test path and
    false-positive (slice-024 23-spurious-FAIL footgun class).
    Rule reference: PTFCD-1 (slice-025 AC #2; Critic M2 ACCEPTED-FIXED).
    """
    real = tmp_path / "tests"
    real.mkdir(parents=True)
    (real / "test_only_real.py").write_text("def test_x(): pass\n", encoding="utf-8")
    catalog = _write_catalog(
        tmp_path,
        "`C:/Users/x/.venv/Scripts/python.exe -m pytest "
        "tests/test_only_real.py --no-header -q`",
    )
    result = audit_catalog_file(catalog)
    # Only tests/test_only_real.py is a test-path token; it exists → clean.
    assert result.tokens_checked == 1, (
        f"interpreter path / -m / pytest / -q / --no-header must not be "
        f"counted as test paths; tokens_checked={result.tokens_checked}, "
        f"{result.to_dict()}"
    )
    assert result.violations == [], (
        f"the one real token exists; expected clean, got {result.to_dict()}"
    )
