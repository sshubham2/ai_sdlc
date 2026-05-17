"""PTFFD-1 (slice-037) function-level tests for tools.test_first_audit.

PTFFD-1 ("Phantom-Test-Function-citation Discipline"; ADR-038) extends
FILE-level PTFCD-1 (slice-025) to the test-FUNCTION level: a PASSING TF-1
plan row whose cited test FILE exists but whose cited test FUNCTION does not
is a `missing-test-function` violation under --strict-pre-finish.

Covers mission-brief AC1. Rule reference: PTFFD-1 (slice-037; ADR-037/038;
refines PTFCD-1 in place, supersedes nothing).
"""
from pathlib import Path

from tools.test_first_audit import _format_human, audit_brief_file


def _write_brief(tmp_path, rows: list[tuple[str, str, str, str, str]]) -> Path:
    """(ac, test_type, test_path, test_function, status) tuples → brief."""
    table = "\n".join(
        f"| {ac} | {tt} | {tp} | {tf} | {st} |" for (ac, tt, tp, tf, st) in rows
    )
    brief = (
        "# Slice 999: ptffd fixture\n\n"
        "**Test-first**: true\n\n"
        "## Acceptance criteria\n\n"
        "1. the thing\n\n"
        "## Test-first plan\n\n"
        "| AC | Test type | Test path | Test function | Status |\n"
        "|----|-----------|-----------|---------------|--------|\n"
        f"{table}\n\n"
        "## Out of scope\n\n- nothing\n"
    )
    p = tmp_path / "mission-brief.md"
    p.write_text(brief, encoding="utf-8")
    return p


def _testfile(tmp_path, name: str, body: str) -> Path:
    f = tmp_path / name
    f.write_text(body, encoding="utf-8")
    return f


def test_phantom_function_in_existing_file_is_violation(tmp_path):
    """File exists, cited function absent → missing-test-function.

    Defect class: the function-level phantom-citation class missed by the
    Critic stack at slice-025 AC3 / slice-026 AC5 / slice-027 B1.
    Rule reference: PTFFD-1 (AC1).
    """
    tf = _testfile(tmp_path, "test_real_only.py", "def test_real():\n    pass\n")
    brief = _write_brief(
        tmp_path, [("1", "unit", str(tf), "test_phantom", "PASSING")]
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" in kinds, (
        f"expected missing-test-function; got {kinds}"
    )


def test_present_function_in_existing_file_is_clean(tmp_path):
    """File exists, cited function present → NO missing-test-function.

    Defect class: a false-positive on a real, present test function would
    make the audit unusable.
    Rule reference: PTFFD-1 (AC1).
    """
    tf = _testfile(tmp_path, "test_present.py", "def test_real():\n    pass\n")
    brief = _write_brief(
        tmp_path, [("1", "unit", str(tf), "test_real", "PASSING")]
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" not in kinds, (
        f"present function must not be flagged; got {kinds}"
    )


def test_empty_test_function_sentinel_keeps_file_level_only(tmp_path):
    """Sentinel Test function + no `::` selector → FILE-level-only,
    function layer not entered, no violation (back-compat).

    Rule reference: PTFFD-1 (AC1; back-compat must-not-defer).
    """
    tf = _testfile(tmp_path, "test_sent.py", "def test_real():\n    pass\n")
    brief = _write_brief(
        tmp_path, [("1", "unit", str(tf), "—", "PASSING")]
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" not in kinds, (
        f"sentinel function column must degrade to FILE-level-only; got {kinds}"
    )


def test_prose_test_function_value_degrades_to_file_level_only(tmp_path):
    """A real-corpus prose value (slice-034's
    `(full existing module — non-regression)`) is NOT a checkable
    identifier → degrade to FILE-level-only, NOT a false-positive (B2).

    Rule reference: PTFFD-1 (AC1/AC3; B2 zero-false-positive linchpin).
    """
    tf = _testfile(tmp_path, "test_prose.py", "def test_real():\n    pass\n")
    brief = _write_brief(
        tmp_path,
        [("1", "regression", str(tf),
          "(full existing module — non-regression)", "PASSING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" not in kinds, (
        f"prose function value must not false-positive; got {kinds}"
    )


def test_path_column_selector_used_when_function_column_empty(tmp_path):
    """Function column sentinel BUT Test path carries `::selector`
    → fallback resolves the fn from the path `::`-tail (M3); a phantom
    there is still caught.

    Rule reference: PTFFD-1 (AC1; M3 double-source-escape closure).
    """
    tf = _testfile(tmp_path, "test_pathsel.py", "def test_real():\n    pass\n")
    brief = _write_brief(
        tmp_path,
        [("1", "unit", f"{tf}::test_phantom", "—", "PASSING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" in kinds, (
        f"path-column ::selector phantom must be caught via M3 fallback; "
        f"got {kinds}"
    )


def test_unparseable_test_file_skips_function_check_no_violation(tmp_path):
    """Cited file exists but is not parseable Python → tri-state None →
    NO violation (ADR-037 skip-with-note).

    Rule reference: PTFFD-1 (AC1; ADR-037).
    """
    tf = _testfile(tmp_path, "test_broken.py", "def (:\n  not python\n")
    brief = _write_brief(
        tmp_path, [("1", "unit", str(tf), "test_x", "PASSING")]
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" not in kinds, (
        f"unparseable file must NOT emit a function violation; got {kinds}"
    )


def test_unparseable_file_emits_skip_note_in_human_output(tmp_path):
    """The skip is VISIBLE, not silent — Option 3 genuinely rejected (M2).

    Rule reference: PTFFD-1 (AC1; ADR-037 M2 observability).
    """
    tf = _testfile(tmp_path, "test_broken2.py", "def (:\n  nope\n")
    brief = _write_brief(
        tmp_path, [("1", "unit", str(tf), "test_x", "PASSING")]
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    assert result.skip_notes, "expected a skip-note for the unparseable file"
    human = _format_human(result)
    assert "function-check skipped (file unparseable)" in human, (
        f"skip-note must render in human output; got:\n{human}"
    )


def test_async_def_and_nested_class_method_resolve_true(tmp_path):
    """`async def test_x` and a method inside `class TestC` both resolve
    True — the AST walk is nesting-depth-agnostic (m2).

    Rule reference: PTFFD-1 (AC1; m2).
    """
    body = (
        "async def test_async_thing():\n    pass\n\n"
        "class TestGroup:\n"
        "    def test_method_thing(self):\n        pass\n"
    )
    tf = _testfile(tmp_path, "test_async_nested.py", body)
    brief = _write_brief(
        tmp_path,
        [("1", "unit", str(tf), "test_async_thing", "PASSING"),
         ("1", "unit", str(tf), "test_method_thing", "PASSING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-function" not in kinds, (
        f"async def + nested class method must resolve True; got {kinds}"
    )
