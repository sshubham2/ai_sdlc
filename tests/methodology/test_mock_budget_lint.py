"""Tests for tools.mock_budget_lint - LINT-MOCK-1 (TDD-2 enforcement).

Validates that the mock-budget linter correctly flags:
- More than 1 mock per test function (mock-budget violation)
- Mocking internal classes (internal-mock violation, Important)
- Mocking documented cross-chunk seams (internal-mock, Critical when in allowlist)
- Graceful handling of syntax errors and missing files

Rule reference: LINT-MOCK-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.mock_budget_lint import (
    _BOUNDARY_DEFAULTS,
    LintViolation,
    lint_file,
    lint_files,
    load_seam_allowlist,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures"


def test_clean_file_has_no_violations():
    """A test file with one boundary mock passes TDD-2.

    Defect class: A linter that flags valid patterns (e.g., a single mock
    at a network boundary) creates noise that trains users to ignore it.
    Rule reference: LINT-MOCK-1.
    """
    violations = lint_file(FIXTURES / "mock_budget_clean.py")
    assert violations == [], (
        f"clean file had unexpected violations: "
        f"{[(v.kind, v.severity, v.message) for v in violations]}"
    )


def test_too_many_mocks_flags_mock_budget():
    """Test functions with >1 mock should be flagged with kind=mock-budget.

    Defect class: Multiple mocks per test bypass multiple seams; the test
    no longer verifies any single behavior. The budget rule keeps tests
    focused.
    Rule reference: LINT-MOCK-1.
    """
    violations = lint_file(FIXTURES / "mock_budget_too_many.py")
    budget = [v for v in violations if v.kind == "mock-budget"]
    assert len(budget) == 1, (
        f"expected exactly 1 mock-budget violation; got {len(budget)}: "
        f"{[v.message for v in budget]}"
    )
    assert budget[0].severity == "Important"


def test_internal_class_mock_flags_internal_mock():
    """Mocking an internal class is flagged with kind=internal-mock.

    Defect class: Mocking internal classes bypasses the integration seam
    the test pretends to verify. The internal-mock rule is what prevents
    silent protocol drift.
    Rule reference: LINT-MOCK-1.
    """
    violations = lint_file(FIXTURES / "mock_budget_internal.py")
    internal = [v for v in violations if v.kind == "internal-mock"]
    assert len(internal) == 1, (
        f"expected exactly 1 internal-mock violation; got {len(internal)}"
    )
    assert internal[0].severity == "Important"
    assert "src.services.user_service.UserService" in internal[0].message


def test_seam_allowlist_escalates_to_critical():
    """Targets in the seam allowlist escalate to Critical severity.

    Defect class: Mocking a documented cross-chunk seam is structurally
    worse than mocking an arbitrary internal class - it bypasses a
    contract the project explicitly tracked. Critical severity blocks
    pre-finish.
    Rule reference: LINT-MOCK-1.
    """
    seam_allowlist = frozenset({"src.api.receipts.upload_receipt"})
    violations = lint_file(FIXTURES / "mock_budget_seam.py", seam_allowlist)
    critical = [
        v for v in violations
        if v.kind == "internal-mock" and v.severity == "Critical"
    ]
    assert len(critical) == 1, (
        f"expected 1 Critical internal-mock; got {len(critical)}"
    )


def test_seam_without_allowlist_stays_important():
    """Without the allowlist, an internal mock on a seam stays at Important.

    Defect class: Without an allowlist, the linter can't know which targets
    are documented seams. Default severity must be Important so projects
    that haven't built the allowlist yet still see findings.
    Rule reference: LINT-MOCK-1.
    """
    violations = lint_file(FIXTURES / "mock_budget_seam.py")  # no allowlist
    assert violations, "expected at least one violation"
    assert all(v.severity == "Important" for v in violations), (
        f"expected all Important without allowlist; got "
        f"{[v.severity for v in violations]}"
    )


def test_syntax_error_emits_parse_error_finding():
    """Files with syntax errors emit a parse-error finding (not a crash).

    Defect class: A linter that crashes on a syntax error blocks every
    other lint. Graceful degradation surfaces the syntax error as a
    finding so the file gets fixed without halting other lint progress.
    Rule reference: LINT-MOCK-1.
    """
    violations = lint_file(FIXTURES / "syntax_error.py")
    assert any(v.kind == "parse-error" for v in violations), (
        f"expected a parse-error finding; got {[v.kind for v in violations]}"
    )


def test_nonexistent_file_emits_parse_error_finding():
    """Missing files emit a parse-error finding (not a crash).

    Defect class: Linter invoked with a stale file list (e.g., file deleted
    in a slice's plan-mode revision) shouldn't crash; it should report
    the missing path so the runner can investigate.
    Rule reference: LINT-MOCK-1.
    """
    violations = lint_file(REPO_ROOT / "does-not-exist-anywhere-xyz.py")
    assert any(v.kind == "parse-error" for v in violations)


def test_lint_files_aggregates_across_files():
    """lint_files combines violations from multiple files."""
    violations = lint_files([
        FIXTURES / "mock_budget_clean.py",
        FIXTURES / "mock_budget_too_many.py",
    ])
    paths = {v.path for v in violations}
    assert any("mock_budget_too_many.py" in p for p in paths)


def test_load_seam_allowlist_strips_comments_and_blanks(tmp_path: Path):
    """The seam allowlist loader honors # comments, blank lines, and trailing whitespace."""
    allowlist_file = tmp_path / "seams"
    allowlist_file.write_text(
        "# Documented cross-chunk seams\n"
        "src.a.foo\n"
        "\n"
        "src.b.bar\n"
        "  # indented comment line\n"
        "src.c.baz   \n",
        encoding="utf-8",
    )
    loaded = load_seam_allowlist(allowlist_file)
    assert loaded == frozenset({"src.a.foo", "src.b.bar", "src.c.baz"})


def test_load_seam_allowlist_missing_file_returns_empty():
    """A missing allowlist file returns an empty frozenset, not an error.

    Defect class: A missing allowlist is the common case (most projects
    won't have one); making this an error would be hostile.
    Rule reference: LINT-MOCK-1.
    """
    assert load_seam_allowlist(Path("does-not-exist-xyz")) == frozenset()


def test_boundary_defaults_includes_common_modules():
    """Sanity check: the boundary defaults cover common HTTP/DB/cloud modules.

    Defect class: Drift in _BOUNDARY_DEFAULTS - if a future commit removes
    a common module (e.g., 'requests'), legitimate boundary mocks will
    suddenly flag as internal mocks. Pinning the must-have set prevents that.
    Rule reference: LINT-MOCK-1.
    """
    must_have = {"requests", "httpx", "subprocess", "os", "sqlalchemy", "boto3"}
    missing = must_have - _BOUNDARY_DEFAULTS
    assert not missing, f"missing required boundary defaults: {missing}"


def test_build_slice_skill_references_lint_mock_1():
    """skills/build-slice/SKILL.md must reference LINT-MOCK-1 in its pre-finish gate.

    Defect class: A linter without integration is shelfware. The
    /build-slice pre-finish gate must run mock-budget lint and refuse
    on Critical findings. Without the rule reference, the integration
    isn't traceable from skill prose to changelog.
    Rule reference: LINT-MOCK-1.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "LINT-MOCK-1" in text, "no LINT-MOCK-1 reference in /build-slice SKILL.md"
    assert "mock_budget_lint" in text, (
        "no `mock_budget_lint` module reference in /build-slice SKILL.md"
    )


# ---------------------------------------------------------------------------
# LINT-MOCK-2 — TypeScript / JavaScript extension
# ---------------------------------------------------------------------------


def test_ts_clean_file_has_no_violations():
    """A TS test file with one boundary mock passes TDD-2.

    Defect class: Same as LINT-MOCK-1 but for TS — false positives on a
    valid pattern train users to ignore the linter.
    Rule reference: LINT-MOCK-2.
    """
    violations = lint_file(FIXTURES / "mock_budget_clean.ts")
    assert violations == [], (
        f"clean TS file had unexpected violations: "
        f"{[(v.kind, v.severity, v.message) for v in violations]}"
    )


def test_ts_too_many_mocks_flags_mock_budget():
    """TS test functions with >1 mock should be flagged with kind=mock-budget."""
    violations = lint_file(FIXTURES / "mock_budget_too_many.ts")
    budget = [v for v in violations if v.kind == "mock-budget"]
    assert len(budget) == 1, (
        f"expected exactly 1 mock-budget violation; got {len(budget)}: "
        f"{[v.message for v in budget]}"
    )
    assert budget[0].severity == "Important"


def test_ts_internal_target_flags_internal_mock():
    """Mocking a relative-path TS module is flagged as internal-mock."""
    violations = lint_file(FIXTURES / "mock_budget_internal.ts")
    internal = [v for v in violations if v.kind == "internal-mock"]
    assert len(internal) == 1, (
        f"expected exactly 1 internal-mock; got {len(internal)}"
    )
    assert internal[0].severity == "Important"
    assert "./services/user-service" in internal[0].message


def test_ts_seam_allowlist_escalates_to_critical():
    """TS targets in the seam allowlist escalate to Critical severity."""
    seam_allowlist = frozenset({"./api/receipts"})
    violations = lint_file(FIXTURES / "mock_budget_seam.ts", seam_allowlist)
    critical = [
        v for v in violations
        if v.kind == "internal-mock" and v.severity == "Critical"
    ]
    assert len(critical) == 1, (
        f"expected 1 Critical TS internal-mock; got {len(critical)}"
    )


def test_ts_seam_without_allowlist_stays_important():
    """Without allowlist, internal TS mock on a seam stays at Important."""
    violations = lint_file(FIXTURES / "mock_budget_seam.ts")
    assert violations, "expected at least one violation"
    assert all(v.severity == "Important" for v in violations)


def test_ts_syntax_error_emits_parse_error_finding():
    """TS files with syntax errors emit a parse-error finding (not a crash)."""
    violations = lint_file(FIXTURES / "syntax_error.ts")
    assert any(v.kind == "parse-error" for v in violations), (
        f"expected a parse-error finding; got {[v.kind for v in violations]}"
    )


def test_ts_boundary_defaults_includes_common_packages():
    """Sanity: TS boundary defaults cover common HTTP/DB/cloud npm packages.

    Defect class: Drift in _TS_BOUNDARY_DEFAULTS - removing a common package
    (e.g., 'axios') would suddenly flag legitimate boundary mocks as internal.
    Rule reference: LINT-MOCK-2.
    """
    from tools.mock_budget_lint import _TS_BOUNDARY_DEFAULTS
    must_have = {
        "axios", "node-fetch", "node:fs", "fs", "pg", "mongodb",
        "@aws-sdk", "stripe", "node:child_process",
    }
    missing = must_have - _TS_BOUNDARY_DEFAULTS
    assert not missing, f"missing required TS boundary defaults: {missing}"


def test_unsupported_extension_emits_parse_error():
    """The dispatcher flags unsupported extensions, not crash.

    Defect class: A user accidentally passing a .md or other non-test file
    should get a clear error, not a crash that hides the true issue.
    Rule reference: LINT-MOCK-2.
    """
    violations = lint_file(REPO_ROOT / "README.md")
    assert any(
        v.kind == "parse-error" and "unsupported file extension" in v.message
        for v in violations
    )


def test_build_slice_skill_references_lint_mock_2():
    """skills/build-slice/SKILL.md must reference LINT-MOCK-2 (TS extension).

    Defect class: A TS extension that isn't referenced in the build-slice
    gate is invisible to executors — they won't know to lint TS files.
    Rule reference: LINT-MOCK-2.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "LINT-MOCK-2" in text, "no LINT-MOCK-2 reference in /build-slice SKILL.md"
