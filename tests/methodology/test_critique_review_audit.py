"""Tests for tools.critique_review_audit (DR-1).

Validates that the audit correctly:
- Accepts clean critique-review.md (4 required sections + 4 header fields
  + valid verdicts)
- Flags missing required sections
- Flags missing header fields
- Flags invalid verdict values
- Honors NFR-1 carry-over exemption

Plus skill prose pins for /critique-review SKILL + agents/critique-review.md
+ AUTHORING.md.

Rule reference: DR-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.critique_review_audit import (
    _DR_1_RELEASE_DATE,
    audit_review_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "critique_review"


# --- File-level audit tests ---

def test_clean_review_passes():
    """A critique-review.md with all 4 sections + valid verdicts has no violations.

    Defect class: An audit that flags well-formed reviews trains users
    to ignore it.
    Rule reference: DR-1.
    """
    result = audit_review_file(FIXTURES / "clean_review.md")
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert result.first_verdict == "NEEDS-FIXES"
    assert result.dual_verdict == "EXTEND"


def test_missing_sections_flagged():
    """Missing required H2 sections (Missed findings + Severity adjustments) flagged.

    Defect class: A meta-review without the full 4-section structure
    leaves the user's TRI-1 triage step without the data it needs to
    reconcile both passes.
    Rule reference: DR-1.
    """
    result = audit_review_file(FIXTURES / "missing_section_review.md")
    missing = [v for v in result.violations if v.kind == "missing-section"]
    assert len(missing) == 2  # missed-findings + severity-adjustments


def test_invalid_verdict_flagged():
    """Verdict values outside the allowed sets are flagged.

    Defect class: APPROVED (the pre-TRI-1 verdict name) and MAYBE
    (ad-hoc) would silently bypass the structural gate; downstream
    consumers can't enumerate verdicts.
    Rule reference: DR-1.
    """
    result = audit_review_file(FIXTURES / "invalid_verdict_review.md")
    invalid = [v for v in result.violations if v.kind == "invalid-verdict"]
    assert len(invalid) == 2  # both verdicts invalid


def test_missing_verdict_fields_flagged():
    """Missing First-Critic verdict + Dual-review verdict header fields flagged.

    Defect class: Without the verdict fields, /reflect calibration can't
    classify the meta-Critic's outcome (validated-on-reconsideration etc.).
    Rule reference: DR-1.
    """
    result = audit_review_file(FIXTURES / "missing_verdict_review.md")
    missing = [v for v in result.violations if v.kind == "missing-field"]
    field_names = {v.message.lower() for v in missing}
    assert any("first-critic verdict" in m for m in field_names)
    assert any("dual-review verdict" in m for m in field_names)


def test_audit_handles_missing_review_md_gracefully():
    """Missing critique-review.md emits no-file violation, not a crash.

    Defect class: A linter that crashes on missing input is hostile.
    Rule reference: DR-1.
    """
    result = audit_review_file(REPO_ROOT / "does-not-exist-dr.md")
    assert any(v.kind == "no-file" for v in result.violations)


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_slices(tmp_path: Path):
    """Slice with mission-brief.md mtime predating DR-1 is exempt.

    Defect class: Retroactively applying DR-1 to old slices would refuse
    archived critique-review.md files (if any exist) authored before the
    rule shipped.
    Rule reference: DR-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text("# old slice", encoding="utf-8")
    _set_brief_mtime(brief, _DR_1_RELEASE_DATE - timedelta(days=30))

    review = slice_folder / "critique-review.md"
    review.write_text("# Old review (no structure)\n", encoding="utf-8")

    result = audit_review_file(review)
    assert result.carry_over_exempt is True
    assert result.violations == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Without override, archive scans can't reach pre-rule slices.
    Rule reference: DR-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text("# old slice", encoding="utf-8")
    _set_brief_mtime(brief, _DR_1_RELEASE_DATE - timedelta(days=30))

    review = slice_folder / "critique-review.md"
    review.write_text("# Old review (no structure)\n", encoding="utf-8")

    result = audit_review_file(review, skip_if_carry_over=False)
    assert result.carry_over_exempt is False
    assert any(v.kind == "missing-section" for v in result.violations)


# --- Skill + agent prose pins ---

def test_critique_review_skill_references_dr_1():
    """skills/critique-review/SKILL.md must reference DR-1 + the agent.

    Defect class: Without the skill referencing DR-1, the rule is
    advisory; without the agent reference, dispatch fails.
    Rule reference: DR-1.
    """
    text = (REPO_ROOT / "skills" / "critique-review" / "SKILL.md").read_text(encoding="utf-8")
    assert "DR-1" in text, "no DR-1 reference in /critique-review SKILL.md"
    assert "subagent_type" in text, (
        "no subagent_type reference (agent dispatch missing)"
    )
    assert "critique-review" in text


def test_critique_review_agent_carries_meta_critic_stance():
    """agents/critique-review.md must carry the meta-Critic stance + scoring vocab.

    Defect class: Stance softening — paraphrasing to "review the
    critique" loses the adversarial-meta property. Without the scoring
    vocab pinned, the output format drifts and the audit can't
    structurally validate it.
    Rule reference: DR-1 (META-2 pattern).
    """
    text = (REPO_ROOT / "agents" / "critique-review.md").read_text(encoding="utf-8")
    assert "Meta-Critic" in text or "meta-Critic" in text
    # Scoring vocabulary
    for token in ("VALID", "SUSPICIOUS", "SEVERITY-WRONG"):
        assert token in text, f"scoring token '{token}' missing from agent prompt"
    # Verdict vocabulary
    for verdict in ("ACCEPT", "ADJUST", "EXTEND"):
        assert verdict in text, f"verdict '{verdict}' missing from agent prompt"
    # Specificity rule
    assert "Specificity rule" in text or "Vague meta-findings are useless" in text


def test_critique_review_agent_uses_critique_review_subagent_type():
    """The /critique-review skill must dispatch via subagent_type=critique-review.

    Defect class: Wrong subagent_type causes the harness to spawn the
    wrong agent; the meta-Critic prompt never runs.
    Rule reference: DR-1.
    """
    text = (REPO_ROOT / "skills" / "critique-review" / "SKILL.md").read_text(encoding="utf-8")
    assert '"critique-review"' in text or "'critique-review'" in text
