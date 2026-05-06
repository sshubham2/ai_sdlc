"""Tests for tools.test_first_audit (TF-1).

Validates that the audit correctly:
- Detects the opt-in `**Test-first**: true | false` field
- Treats absent / false flag as "default-off, no violation"
- When true, requires a `## Test-first plan` section with a 5-column table
- Validates Status vocabulary {PENDING, WRITTEN-FAILING, PASSING}
- Flags ACs in the brief without at least one test-first row
- Refuses non-PASSING rows when --strict-pre-finish (used at /build-slice)
- Honors NFR-1 carry-over exemption

Pins skill prose in /slice + /build-slice.

Rule reference: TF-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.test_first_audit import (
    _TF_1_RELEASE_DATE,
    _normalize_ac_label,
    audit_brief_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "test_first"


# --- Unit tests ---

def test_normalize_ac_label_handles_common_forms():
    """'AC#1', 'ac 1', '1' all normalize to '1'.

    Defect class: An AC reference that's spelled 'AC#1' in the body but
    '1' in the table would be treated as different ACs and the orphan
    detection would fire spuriously.
    Rule reference: TF-1.
    """
    assert _normalize_ac_label("AC#1") == "1"
    assert _normalize_ac_label("ac 1") == "1"
    assert _normalize_ac_label("1") == "1"
    assert _normalize_ac_label("AC#10") == "10"


# --- File-level audit tests ---

def test_clean_brief_passes():
    """A test-first brief with all ACs covered + statuses valid passes.

    Defect class: The most common case (test-first opt-in, all rows
    PASSING) must audit cleanly.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "clean_brief.md")
    assert result.test_first_enabled is True
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.rows) == 4
    statuses = {r.status for r in result.rows}
    assert statuses == {"PASSING"}


def test_test_first_off_is_silent():
    """A brief without `**Test-first**: true` produces no violations.

    Defect class: An audit that fires on every brief regardless of opt-in
    would force every project to adopt test-first immediately.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "test_first_off.md")
    assert result.test_first_enabled is False
    assert result.violations == []


def test_missing_section_when_test_first_true_flagged():
    """`**Test-first**: true` without a `## Test-first plan` section fails.

    Defect class: Opting into test-first but skipping the plan defeats
    the rule's purpose; the audit must catch the inconsistency.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "missing_section_brief.md")
    assert any(v.kind == "missing-section" for v in result.violations)


def test_invalid_status_flagged():
    """Status outside {PENDING, WRITTEN-FAILING, PASSING} is flagged.

    Defect class: An open status vocabulary lets the lifecycle decay
    into ad-hoc strings; the gate becomes meaningless.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "invalid_status_brief.md")
    assert any(v.kind == "invalid-status" for v in result.violations)


def test_ac_without_row_flagged():
    """An AC declared in the brief body without any test-first row fails.

    Defect class: Orphan ACs slip through to /build-slice without
    any test coverage planned — TF-1's coverage guarantee is silently
    violated.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "ac_without_row_brief.md")
    orphans = [v for v in result.violations if v.kind == "ac-without-row"]
    assert len(orphans) == 1
    assert orphans[0].ac == "2"


def test_strict_pre_finish_refuses_non_passing():
    """--strict-pre-finish flags PENDING + WRITTEN-FAILING rows as violations.

    Defect class: /build-slice declaring "done" while tests are still
    failing is exactly what test-first is supposed to prevent. Strict
    mode is the gate that catches it.
    Rule reference: TF-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=True,
    )
    non_passing = [v for v in result.violations if v.kind == "non-passing-pre-finish"]
    # 2 rows are non-PASSING (one WRITTEN-FAILING, one PENDING)
    assert len(non_passing) == 2


def test_strict_pre_finish_default_does_not_refuse():
    """Without --strict-pre-finish, non-PASSING rows are allowed.

    Defect class: Refusing PENDING / WRITTEN-FAILING during /design-slice
    or /critique would block legitimate workflows where rows haven't yet
    been brought to PASSING.
    Rule reference: TF-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=False,
    )
    non_passing = [v for v in result.violations if v.kind == "non-passing-pre-finish"]
    assert non_passing == []


def test_missing_brief_is_silent():
    """A missing mission-brief.md produces no violations (default-off).

    Defect class: A linter that crashes on missing input is hostile.
    Rule reference: TF-1.
    """
    result = audit_brief_file(REPO_ROOT / "does-not-exist-tf.md")
    assert result.test_first_enabled is False
    assert result.violations == []


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_briefs(tmp_path: Path):
    """Briefs whose mtime predates TF-1 are exempt automatically.

    Defect class: Retroactively applying TF-1 to old slices would refuse
    every archived brief that has `Test-first: true` set ad-hoc.
    Rule reference: TF-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Test-first**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _TF_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief)
    assert result.carry_over_exempt is True
    assert result.violations == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Without an override, archive scans can't reach pre-rule
    slices.
    Rule reference: TF-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Test-first**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _TF_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief, skip_if_carry_over=False)
    assert result.carry_over_exempt is False
    assert any(v.kind == "missing-section" for v in result.violations)


# --- Skill prose pins ---

def test_slice_skill_references_tf_1():
    """skills/slice/SKILL.md must reference TF-1 + the Test-first option.

    Defect class: Without /slice documenting the option, projects don't
    know they can opt in; TF-1 sits unused.
    Rule reference: TF-1.
    """
    text = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "TF-1" in text, "no TF-1 reference in /slice SKILL.md"
    assert "Test-first" in text, "no Test-first option in /slice"


def test_build_slice_references_tf_1():
    """skills/build-slice/SKILL.md must reference TF-1 + the audit.

    Defect class: Without /build-slice running the strict-pre-finish
    audit, slices declaring test-first ship with PENDING/WRITTEN-FAILING
    rows.
    Rule reference: TF-1.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "TF-1" in text, "no TF-1 reference in /build-slice SKILL.md"
    assert "test_first_audit" in text, (
        "no test_first_audit module reference in /build-slice"
    )


def test_mission_brief_template_documents_test_first():
    """templates/mission-brief.md must document the Test-first field + section.

    Defect class: Without the template referencing TF-1, project owners
    creating briefs by hand miss the option.
    Rule reference: TF-1.
    """
    text = (REPO_ROOT / "templates" / "mission-brief.md").read_text(encoding="utf-8")
    assert "Test-first" in text
    assert "TF-1" in text
