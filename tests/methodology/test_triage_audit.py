"""Tests for tools.triage_audit (TRI-1).

Validates that the triage audit correctly:
- Accepts clean critiques (CLEAN with no findings, NEEDS-FIXES with mixed
  dispositions, BLOCKED with ESCALATED)
- Flags missing triage section (Step 4.5 not run)
- Flags missing required header fields (Triaged by / Date / Final verdict)
- Flags invalid final verdicts (outside CLEAN | NEEDS-FIXES | BLOCKED)
- Flags findings declared in body without triage rows
- Flags invalid dispositions
- Flags OVERRIDDEN / DEFERRED / ESCALATED rows with empty rationale
- Flags verdict-pattern mismatch
- Honors NFR-1 carry-over exemption

Pins skill-prose references in /critique + /reflect.

Rule reference: TRI-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.triage_audit import (
    _TRI_1_RELEASE_DATE,
    _expected_verdict,
    audit_critique_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "triage"


# --- Verdict computation unit tests ---

def test_expected_verdict_no_findings_is_clean():
    """Empty disposition map -> CLEAN.

    Defect class: A critique with no findings should default to CLEAN; without
    this, downstream gates would refuse a perfectly clean review.
    Rule reference: TRI-1.
    """
    assert _expected_verdict({}) == "CLEAN"


def test_expected_verdict_escalated_dominates():
    """Any ESCALATED -> BLOCKED, regardless of other dispositions.

    Defect class: An ESCALATED finding means a known-unknown the slice can't
    proceed past. If verdict were anything other than BLOCKED, /build-slice
    would run on a foundation the user already flagged as unsettled.
    Rule reference: TRI-1.
    """
    dispositions = {
        "B1": "ESCALATED",
        "M1": "ACCEPTED-FIXED",
        "m1": "DEFERRED",
    }
    assert _expected_verdict(dispositions) == "BLOCKED"


def test_expected_verdict_pending_means_needs_fixes():
    """ACCEPTED-PENDING (no escalation) -> NEEDS-FIXES.

    Defect class: A pending fix is an obligation; CLEAN would let the user
    skip the work. NEEDS-FIXES forces /build-slice to track the obligation.
    Rule reference: TRI-1.
    """
    dispositions = {
        "B1": "ACCEPTED-PENDING",
        "M1": "OVERRIDDEN",
    }
    assert _expected_verdict(dispositions) == "NEEDS-FIXES"


def test_expected_verdict_settled_only_is_clean():
    """All ACCEPTED-FIXED / OVERRIDDEN / DEFERRED -> CLEAN.

    Defect class: If every finding is already settled (fixed, dismissed, or
    explicitly punted), the gate should not block /build-slice on bookkeeping.
    Rule reference: TRI-1.
    """
    dispositions = {
        "B1": "ACCEPTED-FIXED",
        "M1": "OVERRIDDEN",
        "m1": "DEFERRED",
    }
    assert _expected_verdict(dispositions) == "CLEAN"


# --- File-level audit tests ---

def test_clean_critique_passes():
    """Critique with no findings + CLEAN verdict has zero violations.

    Defect class: An audit that flags clean reviews as violations trains
    users to ignore it.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "clean_critique.md")
    assert result.violations == [], (
        f"clean critique had unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert result.declared_verdict == "CLEAN"
    assert result.expected_verdict == "CLEAN"


def test_needs_fixes_critique_passes():
    """Critique with mixed dispositions + NEEDS-FIXES verdict passes.

    Defect class: Common mid-spectrum case (one ACCEPTED-PENDING, one
    OVERRIDDEN, one DEFERRED) must audit clean.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "needs_fixes_critique.md")
    assert result.violations == [], (
        f"needs-fixes critique had unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert result.declared_verdict == "NEEDS-FIXES"
    assert result.expected_verdict == "NEEDS-FIXES"


def test_blocked_critique_passes():
    """Critique with one ESCALATED + BLOCKED verdict passes.

    Defect class: BLOCKED with proper escalation must NOT be flagged as a
    violation; it represents a legitimate gate.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "blocked_critique.md")
    assert result.violations == [], (
        f"blocked critique had unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert result.declared_verdict == "BLOCKED"
    assert result.expected_verdict == "BLOCKED"


def test_missing_triage_section_flagged():
    """critique.md lacking the Triage heading is flagged no-section.

    Defect class: Step 4.5 (user triage) skipped silently — Builder
    dispositions become final without user ratification, violating TRI-1's
    user-owned-triage discipline.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "no_triage_section_critique.md")
    assert any(v.kind == "no-section" for v in result.violations), (
        f"expected no-section violation; got "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_missing_disposition_row_flagged():
    """A finding declared in body but absent from the triage table is flagged.

    Defect class: Findings that escape user triage become unauditable —
    the gate cannot tell whether the user accepted, overrode, or punted.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "missing_disposition_critique.md")
    missing = [v for v in result.violations if v.kind == "missing-row"]
    assert len(missing) == 1, (
        f"expected 1 missing-row; got {len(missing)}: "
        f"{[v.message for v in result.violations]}"
    )
    assert missing[0].finding_id == "B2"


def test_missing_rationale_flagged():
    """OVERRIDDEN / DEFERRED / ESCALATED rows with empty rationale are flagged.

    Defect class: A bare OVERRIDDEN with no reasoning recapitulates the
    pre-TRI-1 problem of unaudited Builder dispositions. Rationale-required
    is the user's accountability mechanism.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "missing_rationale_critique.md")
    missing = [v for v in result.violations if v.kind == "missing-rationale"]
    assert len(missing) == 2, (
        f"expected 2 missing-rationale (B1 OVERRIDDEN, M1 DEFERRED); got "
        f"{len(missing)}: {[v.message for v in result.violations]}"
    )
    finding_ids = {v.finding_id for v in missing}
    assert finding_ids == {"B1", "M1"}


def test_invalid_disposition_flagged():
    """A disposition outside the allowed vocabulary is flagged.

    Defect class: An open vocabulary lets dispositions drift to
    ad-hoc strings ("maybe", "later", "TBD") and the gate becomes
    meaningless.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "invalid_disposition_critique.md")
    invalid = [v for v in result.violations if v.kind == "invalid-disposition"]
    assert len(invalid) == 1, (
        f"expected 1 invalid-disposition; got "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_verdict_mismatch_flagged():
    """Declared verdict CLEAN with ESCALATED disposition is flagged.

    Defect class: Verdict drift from disposition pattern lets users
    bypass BLOCKED by mis-declaring CLEAN. The audit recomputes from
    dispositions and refuses on mismatch.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(FIXTURES / "verdict_mismatch_critique.md")
    mismatches = [v for v in result.violations if v.kind == "verdict-mismatch"]
    assert len(mismatches) == 1, (
        f"expected 1 verdict-mismatch; got "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert result.declared_verdict == "CLEAN"
    assert result.expected_verdict == "BLOCKED"


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_slices(tmp_path: Path):
    """Slice with mission-brief.md mtime predating TRI-1 is exempt.

    Defect class: Retroactively applying TRI-1 to slices authored before
    the rule existed would refuse every old archived critique.md.
    Rule reference: TRI-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text("# old slice", encoding="utf-8")
    _set_brief_mtime(brief, _TRI_1_RELEASE_DATE - timedelta(days=30))

    # critique.md without a triage section (would normally fail)
    critique = slice_folder / "critique.md"
    critique.write_text(
        "# Critique: Slice old\n\n**Result**: CLEAN\n",
        encoding="utf-8",
    )

    result = audit_critique_file(critique)
    assert result.carry_over_exempt is True
    assert result.violations == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Without an override, archive scans (CI / catalog audits)
    can't reach pre-rule slices.
    Rule reference: TRI-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text("# old slice", encoding="utf-8")
    _set_brief_mtime(brief, _TRI_1_RELEASE_DATE - timedelta(days=30))

    critique = slice_folder / "critique.md"
    critique.write_text(
        "# Critique: Slice old\n\n**Result**: CLEAN\n",
        encoding="utf-8",
    )

    result = audit_critique_file(critique, skip_if_carry_over=False)
    assert result.carry_over_exempt is False
    assert any(v.kind == "no-section" for v in result.violations)


def test_audit_handles_missing_critique_md_gracefully(tmp_path: Path):
    """Missing critique.md emits no-section violation, not a crash.

    Defect class: A linter that crashes on missing input is hostile;
    graceful 'file not found' lets other gates continue.
    Rule reference: TRI-1.
    """
    result = audit_critique_file(tmp_path / "does-not-exist.md")
    assert any(v.kind == "no-section" for v in result.violations)


# --- Skill prose pins ---

def test_critique_skill_references_tri_1():
    """skills/critique/SKILL.md must reference TRI-1 + the audit module.

    Defect class: Without the skill referencing TRI-1 + the audit, Step 4.5
    becomes optional in practice; users skip the user-triage gate.
    Rule reference: TRI-1.
    """
    text = (REPO_ROOT / "skills" / "critique" / "SKILL.md").read_text(encoding="utf-8")
    assert "TRI-1" in text, "no TRI-1 reference in /critique SKILL.md"
    assert "triage_audit" in text, "no triage_audit module reference"
    assert "Step 4.5" in text, "Step 4.5 heading missing in /critique SKILL.md"
    assert "User-owned triage" in text, "Step 4.5 title language drifted"


def test_critique_skill_pins_disposition_vocabulary():
    """The disposition vocabulary must be enumerated explicitly.

    Defect class: A skill that doesn't name the disposition vocabulary lets
    paraphrase rot replace it with ad-hoc strings, defeating the audit.
    Rule reference: TRI-1.
    """
    text = (REPO_ROOT / "skills" / "critique" / "SKILL.md").read_text(encoding="utf-8")
    for disp in ("ACCEPTED-FIXED", "ACCEPTED-PENDING", "OVERRIDDEN", "DEFERRED", "ESCALATED"):
        assert disp in text, f"disposition '{disp}' missing from /critique SKILL.md"


def test_critique_skill_uses_new_verdicts():
    """The skill uses the renamed three verdicts, not the old APPROVED.

    Defect class: Mixed-vocabulary skill is confusing and breaks the audit
    expectation that critique.md uses the new verdicts.
    Rule reference: TRI-1.
    """
    text = (REPO_ROOT / "skills" / "critique" / "SKILL.md").read_text(encoding="utf-8")
    assert "CLEAN" in text
    assert "NEEDS-FIXES" in text
    assert "BLOCKED" in text
    assert "APPROVED" not in text, (
        "old verdict 'APPROVED' still present in /critique SKILL.md"
    )


def test_critique_agent_uses_new_verdicts():
    """The agent prompt uses the renamed three verdicts.

    Defect class: A drift between the skill's expected verdicts and what the
    agent emits would cause the audit to fail every critique.
    Rule reference: TRI-1.
    """
    text = (REPO_ROOT / "agents" / "critique.md").read_text(encoding="utf-8")
    assert "CLEAN" in text
    assert "NEEDS-FIXES" in text
    assert "APPROVED" not in text


def test_reflect_skill_pins_calibration_vocabulary():
    """The reflect calibration step must enumerate the new vocab.

    Defect class: Without OVERRIDE-MISJUDGED in /reflect, the user-side
    calibration signal is lost and the post-TRI-1 calibration becomes
    indistinguishable from pre-TRI-1.
    Rule reference: TRI-1.
    """
    text = (REPO_ROOT / "skills" / "reflect" / "SKILL.md").read_text(encoding="utf-8")
    assert "TRI-1" in text, "no TRI-1 reference in /reflect SKILL.md"
    for state in ("VALIDATED", "FALSE-ALARM", "OVERRIDE-MISJUDGED", "NOT-YET", "MISSED"):
        assert state in text, f"calibration state '{state}' missing from /reflect"
