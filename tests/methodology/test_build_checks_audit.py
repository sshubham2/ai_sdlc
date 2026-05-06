"""Tests for tools.build_checks_audit (BC-1).

Validates that the build-checks audit correctly:
- Parses H2 rules with required fields (Severity, Applies to, Check)
- Flags missing required fields and invalid severities (parse violations)
- Resolves applicability via globs, trigger keywords, and `always: true`
- Reads project + global build-checks together
- Honors NFR-1 carry-over exemption (mtime check on mission-brief.md)
- Pins skill-prose references in /build-slice + /reflect

Rule reference: BC-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.build_checks_audit import (
    _BC_1_RELEASE_DATE,
    _matches_glob,
    audit_slice,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "build_checks"


def _make_slice(tmp_path: Path, brief_text: str = "# slice", mtime_date=None) -> Path:
    """Create a temp slice folder with mission-brief.md + design.md."""
    slice_folder = tmp_path / "slice-001-test"
    slice_folder.mkdir(parents=True, exist_ok=True)
    brief = slice_folder / "mission-brief.md"
    brief.write_text(brief_text, encoding="utf-8")
    design = slice_folder / "design.md"
    design.write_text("# design\n", encoding="utf-8")
    if mtime_date is not None:
        target_dt = datetime.combine(mtime_date, datetime.min.time().replace(hour=12))
        ts = target_dt.timestamp()
        os.utime(brief, (ts, ts))
    return slice_folder


# --- Glob matcher unit tests ---

def test_glob_simple_segment_match():
    """`src/api/*.py` matches `src/api/foo.py` but not `src/api/v1/foo.py`.

    Defect class: A `*` glob that escapes path segments would match too
    broadly and surface rules unrelated to the changed file.
    Rule reference: BC-1.
    """
    assert _matches_glob("src/api/foo.py", "src/api/*.py") is True
    assert _matches_glob("src/api/v1/foo.py", "src/api/*.py") is False


def test_glob_double_star_matches_multi_segment():
    """`src/api/**` matches one or more segments under `src/api/`.

    Defect class: Without `**` support, a rule scoped to a directory tree
    would have to enumerate depths; that's brittle.
    Rule reference: BC-1.
    """
    assert _matches_glob("src/api/foo.py", "src/api/**") is True
    assert _matches_glob("src/api/v1/foo.py", "src/api/**") is True
    assert _matches_glob("src/api/v1/v2/foo.py", "src/api/**") is True
    assert _matches_glob("src/services/foo.py", "src/api/**") is False


def test_glob_substring_within_filename():
    """`src/services/*upload*.py` matches `src/services/file_upload.py`.

    Defect class: A glob that can't match substring patterns within filenames
    would force rule authors to use ** or list files exhaustively.
    Rule reference: BC-1.
    """
    assert _matches_glob("src/services/file_upload.py", "src/services/*upload*.py") is True
    assert _matches_glob("src/services/download.py", "src/services/*upload*.py") is False


def test_glob_handles_windows_separators():
    """Windows-style backslashes normalize to forward slashes for matching.

    Defect class: A glob matcher that breaks on Windows path separators
    would silently mis-classify rules in the Windows dev environment.
    Rule reference: BC-1.
    """
    assert _matches_glob(r"src\api\foo.py", "src/api/**") is True


# --- Parsing tests ---

def test_clean_file_with_no_rules_yields_no_applicable(tmp_path: Path):
    """Empty rules section produces zero applicable rules (no violations).

    Defect class: A bootstrap file with no rules yet must not trip the audit.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "clean_project_checks.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert result.applicable == []
    assert result.violations == []


def test_always_true_rule_always_applies(tmp_path: Path):
    """`Applies to: always: true` surfaces regardless of changed_files / text.

    Defect class: An always-on guard (e.g., 'every endpoint needs auth test')
    must surface even when no obvious file glob matches.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=[],
    )
    assert len(result.applicable) == 1
    rule = result.applicable[0]
    assert rule.rule_id == "BC-PROJ-1"
    assert rule.severity == "Critical"
    assert rule.applies_to == ("always",)


def test_glob_applies_to_matches_changed_files(tmp_path: Path):
    """A rule with `Applies to: src/api/uploads/**` fires when a matching file changed.

    Defect class: Glob-scoped rules must NOT fire on unrelated slices, only
    when the file pattern matches the slice's changed files.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "glob_match.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/api/uploads/receipts.py"],
    )
    assert len(result.applicable) == 1
    assert result.applicable[0].rule_id == "BC-PROJ-2"


def test_glob_applies_to_does_not_match_unrelated_files(tmp_path: Path):
    """A glob-scoped rule must NOT fire on unrelated slices.

    Defect class: A rule firing on every slice (regardless of relevance) is
    noise; the builder learns to ignore it.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "glob_match.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/database/migrations/001.sql"],
    )
    assert result.applicable == []
    assert len(result.skipped) == 1


def test_keyword_match_via_mission_brief(tmp_path: Path):
    """A keyword in mission-brief.md fires the rule even with no matching glob.

    Defect class: Some rules apply by topic, not by file path (e.g., 'auth
    rework slice should run pen-test'). Without keyword matching, the rule
    can't be triggered by mission-brief alone.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(
        tmp_path,
        brief_text="# Slice\n\nRework JWT token refresh handling for the auth flow.",
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "keyword_only.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=[],  # no glob hits
    )
    assert len(result.applicable) == 1
    assert result.applicable[0].rule_id == "BC-PROJ-3"


def test_missing_severity_field_yields_violation(tmp_path: Path):
    """A rule missing the Severity field is flagged as a parse violation.

    Defect class: A malformed rule that's silently parsed with default
    severity would let authors skip the field by accident; making it a
    violation forces explicit severity.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "missing_severity.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.kind == "missing-field"
    assert "severity" in v.message.lower()


def test_invalid_severity_yields_violation(tmp_path: Path):
    """Severity outside {Critical, Important} is flagged.

    Defect class: An open severity vocabulary lets rules drift to 'Suggested'
    / 'Nice-to-have' / 'Maybe' and the gate becomes meaningless.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "invalid_severity.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert any(v.kind == "invalid-severity" for v in result.violations)


def test_multi_rules_filtered_by_applicability(tmp_path: Path):
    """3 rules: always-true fires; glob-only fires only on payments; keyword-only fires only on migration text.

    Defect class: An audit that surfaces every rule defeats the targeting
    purpose. Applicability filtering is the value of the audit.
    Rule reference: BC-1.
    """
    # First scenario: changed payments file, no migration in brief
    slice_payments = _make_slice(tmp_path / "a", brief_text="# slice\nadd payment processor.")
    result = audit_slice(
        slice_folder=slice_payments,
        project_checks=FIXTURES / "multi_rules.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/payments/stripe_adapter.py"],
    )
    rule_ids = {r.rule_id for r in result.applicable}
    assert "BC-PROJ-6" in rule_ids  # always
    assert "BC-PROJ-7" in rule_ids  # glob match
    assert "BC-PROJ-8" not in rule_ids  # no keyword

    # Second scenario: brief mentions migration, no payments file
    slice_migration = _make_slice(
        tmp_path / "b",
        brief_text="# slice\nadd alembic migration for users table schema.",
    )
    result2 = audit_slice(
        slice_folder=slice_migration,
        project_checks=FIXTURES / "multi_rules.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/users/model.py"],
    )
    rule_ids2 = {r.rule_id for r in result2.applicable}
    assert "BC-PROJ-6" in rule_ids2
    assert "BC-PROJ-7" not in rule_ids2
    assert "BC-PROJ-8" in rule_ids2  # keyword hit


def test_global_and_project_checks_combine(tmp_path: Path):
    """Project + global build-checks are merged in the result.

    Defect class: If global and project checks aren't combined, cross-project
    rules (e.g., 'never commit secrets') would be invisible at /build-slice.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=FIXTURES / "global_checks.md",
    )
    sources = {r.source for r in result.applicable}
    assert "project" in sources
    assert "global" in sources


def test_carry_over_exempts_old_slices(tmp_path: Path):
    """Slice whose mission-brief.md mtime predates BC-1 is exempt.

    Defect class: Retroactively applying BC-1 to slices authored before
    the rule existed would refuse old archived slices. NFR-1 carry-over
    via mtime check exempts them.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(
        tmp_path,
        mtime_date=_BC_1_RELEASE_DATE - timedelta(days=30),
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert result.carry_over_exempt is True
    assert result.applicable == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """`skip_if_carry_over=False` audits even old slices.

    Defect class: Without an override, archive scans (CI / catalog audits)
    can't reach pre-rule slices.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(
        tmp_path,
        mtime_date=_BC_1_RELEASE_DATE - timedelta(days=30),
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=Path("/nonexistent/global.md"),
        skip_if_carry_over=False,
    )
    assert result.carry_over_exempt is False
    assert len(result.applicable) == 1


def test_missing_project_checks_file_handled_gracefully(tmp_path: Path):
    """Missing project checks file is fine — no rules to surface.

    Defect class: A linter that crashes on a missing input is hostile;
    most projects won't have build-checks.md until rules accumulate.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=Path("/nonexistent/project.md"),
        global_checks=Path("/nonexistent/global.md"),
    )
    assert result.applicable == []
    assert result.violations == []


# --- Skill prose pins ---

def test_build_slice_skill_references_bc_1():
    """skills/build-slice/SKILL.md must reference BC-1 + the audit module.

    Defect class: Without the pre-finish gate referencing BC-1 + the tool
    name, the rule is advisory. The skill prose must name both.
    Rule reference: BC-1.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "BC-1" in text, "no BC-1 reference in /build-slice SKILL.md"
    assert "build_checks_audit" in text, (
        "no build_checks_audit module reference in /build-slice"
    )


def test_reflect_skill_references_bc_1():
    """skills/reflect/SKILL.md must reference BC-1 in the promotion step.

    Defect class: Without /reflect documenting promotion, recurring
    patterns stay buried in lessons-learned and never become checks.
    Rule reference: BC-1.
    """
    text = (REPO_ROOT / "skills" / "reflect" / "SKILL.md").read_text(encoding="utf-8")
    assert "BC-1" in text, "no BC-1 reference in /reflect SKILL.md"
    assert "build-checks" in text, (
        "no build-checks reference in /reflect"
    )
    # Pin the promotion-prompt language so it can't be paraphrased away
    assert "recurring pattern" in text.lower(), (
        "promotion prompt should mention 'recurring pattern'"
    )
