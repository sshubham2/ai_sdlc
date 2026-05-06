"""Tests for tools.exploratory_charter_audit (ETC-1).

Validates that the audit correctly:
- Detects the opt-in `**Exploratory-charter**: true | false` field
- Treats absent / false flag as "default-off, no violation"
- When true, requires a `## Exploratory test charter` section with a
  5-column table and at least one charter row
- Validates Status vocabulary {PENDING, IN-PROGRESS, COMPLETED, DEFERRED}
- Requires non-empty Findings when status COMPLETED or DEFERRED
- Refuses PENDING / IN-PROGRESS at --strict-pre-finish; accepts COMPLETED
  AND DEFERRED (DEFERRED is the escape hatch with rationale)
- Honors NFR-1 carry-over exemption

Pins skill prose in /slice + /validate-slice + templates/mission-brief.

Rule reference: ETC-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.exploratory_charter_audit import (
    _ETC_1_RELEASE_DATE,
    audit_brief_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "exploratory_charter"


# --- File-level audit tests ---

def test_clean_brief_passes():
    """A charter brief with COMPLETED + DEFERRED rows (Findings present) passes.

    Defect class: The most common case (some charters completed, one
    deliberately deferred with rationale) must audit cleanly.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "clean_brief.md")
    assert result.exploratory_charter_enabled is True
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.rows) == 3
    statuses = {r.status for r in result.rows}
    assert statuses == {"COMPLETED", "DEFERRED"}


def test_exploratory_off_is_silent():
    """A brief without `**Exploratory-charter**: true` produces no violations.

    Defect class: An audit firing on every brief regardless of opt-in
    would force every project to adopt the discipline immediately.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "exploratory_off.md")
    assert result.exploratory_charter_enabled is False
    assert result.violations == []


def test_missing_section_when_etc_true_flagged():
    """Exploratory-charter true without section fails.

    Defect class: Opting in but skipping the section defeats the rule.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "missing_section_brief.md")
    assert any(v.kind == "missing-section" for v in result.violations)


def test_empty_table_flagged():
    """Header + separator only is a violation.

    Defect class: Opt-in without any charters is opt-in-without-discipline.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "empty_table_brief.md")
    assert any(v.kind == "empty-table" for v in result.violations)


def test_missing_mission_flagged():
    """A row with empty Mission cell is flagged.

    Defect class: A charter without a mission statement is undirected
    exploration; the timebox can't focus on anything specific.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "missing_mission_brief.md")
    assert any(v.kind == "missing-mission" for v in result.violations)


def test_completed_without_findings_flagged():
    """COMPLETED row with empty Findings is flagged.

    Defect class: A "completed" charter without recorded findings
    defeats the discipline — the whole point is to capture what
    surfaced. A bare COMPLETED is performance theater.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "completed_no_findings_brief.md")
    missing = [v for v in result.violations if v.kind == "missing-findings"]
    assert len(missing) == 2  # one COMPLETED, one DEFERRED, both empty


def test_invalid_status_flagged():
    """Status outside the allowed vocabulary is flagged.

    Defect class: Open vocabulary lets statuses drift to ad-hoc strings.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(FIXTURES / "invalid_status_brief.md")
    assert any(v.kind == "invalid-status" for v in result.violations)


def test_strict_pre_finish_refuses_pending_and_in_progress():
    """--strict-pre-finish flags PENDING + IN-PROGRESS but accepts
    COMPLETED + DEFERRED.

    Defect class: A slice declaring "validation done" while charters
    haven't been run defeats the gate. But a DEFERRED charter (with
    rationale) is a deliberate kick-down-the-road, not unfinished work.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=True,
    )
    non_final = [v for v in result.violations if v.kind == "non-final-pre-finish"]
    # Fixture: 1 COMPLETED + 1 IN-PROGRESS + 1 PENDING + 1 DEFERRED.
    # IN-PROGRESS + PENDING should fire (2 violations); COMPLETED + DEFERRED accepted.
    assert len(non_final) == 2


def test_strict_pre_finish_default_does_not_refuse():
    """Without --strict-pre-finish, non-final rows are allowed.

    Defect class: Refusing PENDING during /design or /critique would
    block legitimate workflows where charters haven't run yet.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=False,
    )
    non_final = [v for v in result.violations if v.kind == "non-final-pre-finish"]
    assert non_final == []


def test_missing_brief_is_silent():
    """A missing mission-brief.md produces no violations (default-off).

    Defect class: A linter that crashes on missing input is hostile.
    Rule reference: ETC-1.
    """
    result = audit_brief_file(REPO_ROOT / "does-not-exist-etc.md")
    assert result.exploratory_charter_enabled is False
    assert result.violations == []


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_briefs(tmp_path: Path):
    """Briefs whose mtime predates ETC-1 are exempt automatically.

    Defect class: Retroactively applying ETC-1 to old slices would refuse
    archived briefs.
    Rule reference: ETC-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Exploratory-charter**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _ETC_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief)
    assert result.carry_over_exempt is True
    assert result.violations == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Without override, archive scans can't reach pre-rule slices.
    Rule reference: ETC-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Exploratory-charter**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _ETC_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief, skip_if_carry_over=False)
    assert result.carry_over_exempt is False
    assert any(v.kind == "missing-section" for v in result.violations)


# --- Skill prose pins ---

def test_slice_skill_references_etc_1():
    """skills/slice/SKILL.md must reference ETC-1 + the Exploratory-charter option.

    Defect class: Without /slice documenting the option, projects don't
    know they can opt in.
    Rule reference: ETC-1.
    """
    text = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "ETC-1" in text, "no ETC-1 reference in /slice SKILL.md"
    assert "Exploratory-charter" in text


def test_validate_slice_references_etc_1():
    """skills/validate-slice/SKILL.md must reference ETC-1 + the audit.

    Defect class: Without /validate-slice running --strict-pre-finish,
    charters can be left PENDING and the slice ships incomplete.
    Rule reference: ETC-1.
    """
    text = (REPO_ROOT / "skills" / "validate-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "ETC-1" in text, "no ETC-1 reference in /validate-slice SKILL.md"
    assert "exploratory_charter_audit" in text, (
        "no exploratory_charter_audit module reference"
    )


def test_mission_brief_template_documents_exploratory_charter():
    """templates/mission-brief.md must document the field + section.

    Defect class: Without the template referencing ETC-1, project owners
    creating briefs by hand miss the option.
    Rule reference: ETC-1.
    """
    text = (REPO_ROOT / "templates" / "mission-brief.md").read_text(encoding="utf-8")
    assert "Exploratory-charter" in text
    assert "ETC-1" in text
