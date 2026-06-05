"""Tests for tools.walking_skeleton_audit (WS-1).

Validates that the audit correctly:
- Detects the opt-in `**Walking-skeleton**: true | false` field
- Treats absent / false flag as "default-off, no violation"
- When true, requires a `## Architectural layers exercised` section with
  a 5-column table and at least one data row
- Validates Status vocabulary {PENDING, EXERCISED}
- Flags rows with empty Verification cells
- Refuses non-EXERCISED rows when --strict-pre-finish (used at /validate-slice)
- Honors NFR-1 carry-over exemption

Pins skill prose in /slice + /validate-slice + templates/mission-brief.

Rule reference: WS-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.walking_skeleton_audit import (
    _WS_1_RELEASE_DATE,
    _WS_FIELD_RE,
    _detect_ws_flag,
    audit_brief_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "walking_skeleton"


# --- File-level audit tests ---

def test_clean_brief_passes():
    """A walking-skeleton brief with all EXERCISED rows passes.

    Defect class: The most common case (walking-skeleton opt-in, all
    layers exercised) must audit cleanly.
    Rule reference: WS-1.
    """
    result = audit_brief_file(FIXTURES / "clean_brief.md")
    assert result.walking_skeleton_enabled is True
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.rows) == 5
    statuses = {r.status for r in result.rows}
    assert statuses == {"EXERCISED"}


def test_walking_skeleton_off_is_silent():
    """A brief without `**Walking-skeleton**: true` produces no violations.

    Defect class: An audit that fires regardless of opt-in would force
    every project to adopt walking-skeleton on every slice.
    Rule reference: WS-1.
    """
    result = audit_brief_file(FIXTURES / "walking_skeleton_off.md")
    assert result.walking_skeleton_enabled is False
    assert result.violations == []


def test_missing_section_when_ws_true_flagged():
    """Walking-skeleton true without a `## Architectural layers exercised` fails.

    Defect class: Opting in but skipping the section defeats the rule.
    Rule reference: WS-1.
    """
    result = audit_brief_file(FIXTURES / "missing_section_brief.md")
    assert any(v.kind == "missing-section" for v in result.violations)


def test_empty_table_flagged():
    """Header + separator only (zero data rows) is a violation.

    Defect class: A walking-skeleton with no layers is a contradiction —
    that's a standard slice. The audit forces explicit layer enumeration.
    Rule reference: WS-1.
    """
    result = audit_brief_file(FIXTURES / "empty_table_brief.md")
    assert any(v.kind == "empty-table" for v in result.violations)


def test_missing_verification_flagged():
    """A row with an empty Verification cell is flagged.

    Defect class: A layer claimed without a runtime verification can't
    be confirmed at /validate-slice; the row is decoration, not discipline.
    Rule reference: WS-1.
    """
    result = audit_brief_file(FIXTURES / "missing_verification_brief.md")
    missing = [v for v in result.violations if v.kind == "missing-verification"]
    assert len(missing) == 1
    assert "API" in missing[0].message


def test_invalid_status_flagged():
    """Status outside {PENDING, EXERCISED} is flagged.

    Defect class: An open status vocabulary lets the lifecycle decay
    into ad-hoc strings; the gate becomes meaningless.
    Rule reference: WS-1.
    """
    result = audit_brief_file(FIXTURES / "invalid_status_brief.md")
    assert any(v.kind == "invalid-status" for v in result.violations)


def test_strict_pre_finish_refuses_non_exercised():
    """--strict-pre-finish flags PENDING rows as violations.

    Defect class: /validate-slice declaring "done" while a layer hasn't
    been reached at runtime is exactly what walking-skeleton is meant
    to prevent.
    Rule reference: WS-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=True,
    )
    non_exercised = [
        v for v in result.violations
        if v.kind == "non-exercised-pre-finish"
    ]
    # 2 rows are PENDING in the fixture
    assert len(non_exercised) == 2


def test_strict_pre_finish_default_does_not_refuse():
    """Without --strict-pre-finish, PENDING rows are allowed.

    Defect class: Refusing PENDING during /design or /critique would
    block legitimate workflows where rows haven't yet been exercised.
    Rule reference: WS-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=False,
    )
    non_exercised = [
        v for v in result.violations
        if v.kind == "non-exercised-pre-finish"
    ]
    assert non_exercised == []


def test_missing_brief_is_silent():
    """A missing mission-brief.md produces no violations (default-off).

    Defect class: A linter that crashes on missing input is hostile.
    Rule reference: WS-1.
    """
    result = audit_brief_file(REPO_ROOT / "does-not-exist-ws.md")
    assert result.walking_skeleton_enabled is False
    assert result.violations == []


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_briefs(tmp_path: Path):
    """Briefs whose mtime predates WS-1 are exempt automatically.

    Defect class: Retroactively applying WS-1 to old slices would refuse
    archived briefs that have ad-hoc walking-skeleton labels.
    Rule reference: WS-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Walking-skeleton**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _WS_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief)
    assert result.carry_over_exempt is True
    assert result.violations == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Without an override, archive scans can't reach pre-rule
    slices.
    Rule reference: WS-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Walking-skeleton**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _WS_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief, skip_if_carry_over=False)
    assert result.carry_over_exempt is False
    assert any(v.kind == "missing-section" for v in result.violations)


# --- Skill prose pins ---

def test_slice_skill_references_ws_1():
    """skills/slice/SKILL.md must reference WS-1 + the Walking-skeleton option.

    Defect class: Without /slice documenting the option, projects don't
    know they can opt in; WS-1 sits unused.
    Rule reference: WS-1.
    """
    text = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "WS-1" in text, "no WS-1 reference in /slice SKILL.md"
    assert "Walking-skeleton" in text


def test_validate_slice_references_ws_1():
    """skills/validate-slice/SKILL.md must reference WS-1 + the audit.

    Defect class: Without /validate-slice running --strict-pre-finish,
    walking-skeleton slices ship with PENDING layers.
    Rule reference: WS-1.
    """
    text = (REPO_ROOT / "skills" / "validate-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "WS-1" in text, "no WS-1 reference in /validate-slice SKILL.md"
    assert "walking_skeleton_audit" in text, (
        "no walking_skeleton_audit module reference"
    )


def test_mission_brief_template_documents_walking_skeleton():
    """templates/mission-brief.md must document the field + section.

    Defect class: Without the template referencing WS-1, project owners
    creating briefs by hand miss the option.
    Rule reference: WS-1.
    """
    text = (REPO_ROOT / "templates" / "mission-brief.md").read_text(encoding="utf-8")
    assert "Walking-skeleton" in text
    assert "WS-1" in text


# --- Annotated-flag detection (slice-116 / R-36 fix-the-class; WS-1 sibling of
#     the ETC-1 vacuous-pass) ---
#
# The mission-brief template writes the opt-in flag with a trailing inline
# annotation: `**Walking-skeleton**: true  (optional; per WS-1 — …)`. The
# pre-fix `_WS_FIELD_RE` anchored the value with `(true|false)\s*$`, so the
# annotation made `.match` fail and `_detect_ws_flag` returned False — a vacuous
# pass identical to ETC-1's R-36. The fix mirrors TF-1's lookahead
# `(true|false)(?=[\s(]|$)`. These FAIL pre-fix on the annotated-true cases.

_WS_ANNOTATED_TRUE = (
    "**Walking-skeleton**: true  "
    "(optional; per WS-1 — opt-in walking-skeleton variant)"
)
_WS_ANNOTATED_FALSE = (
    "**Walking-skeleton**: false  "
    "(optional; per WS-1 — opt-in walking-skeleton variant)"
)


def test_annotated_walking_skeleton_true_is_detected_enabled():
    """An annotated `**Walking-skeleton**: true  (…)` line must read as enabled.

    Fails pre-fix — `(true|false)\\s*$` rejects the trailing annotation (R-36
    sibling defect). Rule reference: WS-1.
    """
    assert _detect_ws_flag(_WS_ANNOTATED_TRUE) is True


def test_audit_brief_with_annotated_walking_skeleton_true_reports_enabled(tmp_path):
    """End-to-end: a brief carrying the annotated `true` flag surfaces enabled.

    Fails pre-fix (reports False → the WS-1 gate silently enforces nothing
    despite authored layers). Rule reference: WS-1.
    """
    brief = tmp_path / "mission-brief.md"
    brief.write_text(
        "# Slice 999: demo-walking-skeleton-slice\n\n"
        f"{_WS_ANNOTATED_TRUE}\n\n"
        "## Architectural layers exercised\n\n"
        "| # | Layer | Component | Verification | Status |\n"
        "|---|-------|-----------|--------------|--------|\n"
        "| 1 | API | src/api/server.py | curl /healthz 200 | EXERCISED |\n",
        encoding="utf-8",
    )
    result = audit_brief_file(brief)
    assert result.walking_skeleton_enabled is True


def test_annotated_walking_skeleton_false_is_disabled():
    """Control: an annotated `false` must resolve to disabled (no over-correction)."""
    assert _detect_ws_flag(_WS_ANNOTATED_FALSE) is False


def test_walking_skeleton_malformed_suffix_is_not_a_valid_boolean():
    """Guard: a malformed-suffix value must NOT be accepted as a boolean.

    Pins the fix toward TF-1's lookahead `(true|false)(?=[\\s(]|$)` rather than a
    loose `(true|false).*$` (R-7 / TFFL-1 silent-bypass). Passes pre- and
    post-fix; must keep passing. Rule reference: WS-1.
    """
    assert _detect_ws_flag("**Walking-skeleton**: trueish") is False
    assert _detect_ws_flag("**Walking-skeleton**: false-positive") is False
    # _WS_FIELD_RE is the same predicate _detect_ws_flag consults; pin it directly.
    assert _WS_FIELD_RE.match("**Walking-skeleton**: trueish") is None
