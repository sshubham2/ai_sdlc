"""PTFFD-1 (slice-037) function-level tests for tools.shippability_path_audit.

Extends FILE-level PTFCD-1 sub-mode (b) to the test-FUNCTION level: a
shippability `Machine-cmd` pytest selector `path::fn` whose FILE exists but
whose terminal `::`-function is absent is a `missing-test-function`
PhantomCitation. Pre-existing FILE-level phantoms keep `kind="missing-test-file"`
(m1 legacy-direction pin) and `to_dict()` retains every prior key.

Covers mission-brief AC2. Rule reference: PTFFD-1 (slice-037; ADR-037/038).
"""
from pathlib import Path

from tools.shippability_path_audit import audit_catalog_file


def _catalog(tmp_path, machine_cmd: str) -> Path:
    """A minimal SCMD-1 6-column catalog with one data row whose
    Machine-cmd (col 6) is `machine_cmd`. `_find_repo_root` resolves to
    tmp_path (no .git/VERSION above it), so `tests/...` tokens resolve
    relative to tmp_path.
    """
    text = (
        "# Shippability\n\n"
        "| # | Slice | Critical path | Command | Runtime | Machine-cmd |\n"
        "|---|-------|---------------|---------|---------|-------------|\n"
        f"| 1 | slice-x | crit | cmd | <1s | {machine_cmd} |\n"
    )
    p = tmp_path / "shippability.md"
    p.write_text(text, encoding="utf-8")
    return p


def _known_testfile(tmp_path) -> None:
    d = tmp_path / "tests" / "methodology"
    d.mkdir(parents=True, exist_ok=True)
    (d / "test_known.py").write_text(
        "def test_real():\n    pass\n\n"
        "class TestGroup:\n"
        "    def test_method(self):\n        pass\n",
        encoding="utf-8",
    )


def test_phantom_function_selector_is_violation(tmp_path):
    """File exists, `::test_phantom` absent → missing-test-function.

    Rule reference: PTFFD-1 (AC2).
    """
    _known_testfile(tmp_path)
    cat = _catalog(
        tmp_path,
        "interp -m pytest tests/methodology/test_known.py::test_phantom "
        "--no-header -q",
    )
    result = audit_catalog_file(cat)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" in kinds, (
        f"expected missing-test-function; got {kinds}"
    )


def test_present_function_selector_is_clean(tmp_path):
    """File exists, `::test_real` present → no violation.

    Rule reference: PTFFD-1 (AC2; false-positive avoidance).
    """
    _known_testfile(tmp_path)
    cat = _catalog(
        tmp_path,
        "interp -m pytest tests/methodology/test_known.py::test_real "
        "--no-header -q",
    )
    result = audit_catalog_file(cat)
    assert result.violations == [], (
        f"present function must be clean; got "
        f"{[(v.kind, v.token) for v in result.violations]}"
    )


def test_class_method_selector_resolves_terminal_name(tmp_path):
    """`::TestGroup::test_method` resolves the terminal `::`-segment
    (`test_method`) which exists as a class method → no violation.

    Rule reference: PTFFD-1 (AC2; selector-shape handling).
    """
    _known_testfile(tmp_path)
    cat = _catalog(
        tmp_path,
        "interp -m pytest "
        "tests/methodology/test_known.py::TestGroup::test_method "
        "--no-header -q",
    )
    result = audit_catalog_file(cat)
    assert result.violations == [], (
        f"class::method terminal name must resolve True; got "
        f"{[(v.kind, v.token) for v in result.violations]}"
    )


def test_legacy_file_level_phantom_keeps_missing_test_file_kind(tmp_path):
    """A pre-existing FILE-level phantom (file absent) still emits
    kind='missing-test-file' and `to_dict()` retains every prior key
    (m1 — additive-superset contract, legacy direction pinned).

    Rule reference: PTFFD-1 (AC2; m1).
    """
    cat = _catalog(
        tmp_path,
        "interp -m pytest tests/methodology/test_NOPE_xyz.py::test_x "
        "--no-header -q",
    )
    result = audit_catalog_file(cat)
    assert len(result.violations) == 1, result.violations
    v = result.violations[0]
    assert v.kind == "missing-test-file", (
        f"file-absent phantom must keep legacy kind; got {v.kind}"
    )
    d = v.to_dict()
    for key in ("row", "token", "resolved", "line", "kind"):
        assert key in d, f"to_dict() lost prior key {key!r}: {d}"
