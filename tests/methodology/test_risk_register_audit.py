"""Tests for tools.risk_register_audit (RR-1).

Validates that the audit correctly:
- Parses H2-structured risks with required + optional fields
- Computes Score = Likelihood * Impact (low=1, medium=2, high=3 -> 1..9)
- Maps Score -> Band (1-2 low, 3-4 medium, 6-9 high)
- Flags missing required fields, invalid values, duplicate IDs
- Returns empty result for empty/missing files (no false alarms)
- Optionally surfaces deprecation for legacy table format (--warn-legacy)
- Sorts and filters for downstream /slice + /status consumption

Pins skill prose in /triage, /slice, /status referencing RR-1.

Rule reference: RR-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.risk_register_audit import (
    _band_for_score,
    audit_register,
    filter_and_sort,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "risk_register"


# --- Score / band unit tests ---

def test_band_low_for_score_1_2():
    """Score 1 and 2 -> low band.

    Defect class: A scoring scale that doesn't match common risk-management
    conventions (low=non-actionable nuisance) trains users to ignore the
    band and reason from raw L*I numbers.
    Rule reference: RR-1.
    """
    assert _band_for_score(1) == "low"
    assert _band_for_score(2) == "low"


def test_band_medium_for_score_3_4():
    """Score 3 and 4 -> medium band.

    Defect class: A scale that conflates medium and high turns most risks
    into "high"; band loses meaning.
    Rule reference: RR-1.
    """
    assert _band_for_score(3) == "medium"
    assert _band_for_score(4) == "medium"


def test_band_high_for_score_6_9():
    """Score 6 and 9 -> high band (5 isn't reachable from 1-3 levels).

    Defect class: Without a clear high cutoff, the audit can't reliably
    pull "the top N concerns" for /status / /slice.
    Rule reference: RR-1.
    """
    assert _band_for_score(6) == "high"
    assert _band_for_score(9) == "high"


# --- File-level audit tests ---

def test_clean_register_parses_all_risks():
    """A valid register with 4 risks parses cleanly with computed scores.

    Defect class: A parser that mis-counts or skips risks would cause
    /slice and /status to show wrong rankings.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.risks) == 4
    by_id = {r.risk_id: r for r in result.risks}
    # R1: high*high=9 -> high
    assert by_id["R1"].score == 9
    assert by_id["R1"].band == "high"
    # R2: medium*medium=4 -> medium
    assert by_id["R2"].score == 4
    assert by_id["R2"].band == "medium"
    # R3: low*high=3 -> medium
    assert by_id["R3"].score == 3
    assert by_id["R3"].band == "medium"
    # R4: low*low=1 -> low
    assert by_id["R4"].score == 1
    assert by_id["R4"].band == "low"


def test_optional_fields_are_captured():
    """Reversibility, Mitigation, Discovered, Notes are parsed when present.

    Defect class: Optional fields silently dropped means /status couldn't
    surface mitigation status or discovery context.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    by_id = {r.risk_id: r for r in result.risks}
    assert by_id["R1"].reversibility == "expensive"
    assert "spike-002" in by_id["R1"].mitigation
    assert "triage" in by_id["R1"].discovered
    # R3 has Notes
    assert "Verified across" in by_id["R3"].notes
    # R4 has no optional fields
    assert by_id["R4"].mitigation == ""
    assert by_id["R4"].notes == ""


def test_missing_required_field_is_violation():
    """Missing Likelihood is a violation, not a silent zero.

    Defect class: A risk without Likelihood that gets a default of 0
    would silently rank lowest and be ignored — exactly the opposite of
    what's typically the case (missing fields signal an unfinished entry).
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "missing_likelihood.md")
    missing = [v for v in result.violations if v.kind == "missing-field"]
    assert len(missing) == 1
    assert "likelihood" in missing[0].message.lower()


def test_invalid_status_is_violation():
    """Status outside the allowed vocabulary is flagged.

    Defect class: An open vocabulary lets statuses drift to "maybe" /
    "kind of" / "later" — undermining filter-by-status.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "invalid_status.md")
    invalid = [v for v in result.violations if v.kind == "invalid-value"]
    assert any("status" in v.message.lower() for v in invalid), (
        f"expected status invalid-value; got "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_duplicate_id_is_violation():
    """Duplicate risk IDs are flagged.

    Defect class: Two risks sharing an ID corrupt every downstream lookup
    (which one does R7 refer to?). Detect at parse-time.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "duplicate_id.md")
    dup = [v for v in result.violations if v.kind == "duplicate-id"]
    assert len(dup) == 1
    # Only the first risk should be parsed
    assert len(result.risks) == 1


def test_empty_register_is_clean_with_zero_risks():
    """An empty register parses cleanly with zero risks, no violation.

    Defect class: A new project's empty register shouldn't flood logs
    with violations. Empty is normal.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "empty_register.md")
    assert result.risks == []
    assert result.violations == []


def test_missing_register_file_is_silent():
    """Missing register.md returns empty result, not crash, not violation.

    Defect class: A linter that crashes on a missing input is hostile.
    Many projects won't have a register at all.
    Rule reference: RR-1.
    """
    result = audit_register(REPO_ROOT / "does-not-exist-xyz-rr.md")
    assert result.risks == []
    assert result.violations == []


def test_legacy_format_silent_by_default():
    """Legacy table format yields zero risks but NO violation by default.

    Defect class: A breaking refusal would force every project to migrate
    immediately; opt-in migration via --warn-legacy is gentler.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "legacy_register.md", warn_legacy=False)
    assert result.risks == []
    assert result.violations == []


def test_legacy_format_flagged_with_warn_legacy():
    """--warn-legacy surfaces a deprecation violation for the old table.

    Defect class: Without an opt-in warning, projects never realize their
    register isn't being scored.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "legacy_register.md", warn_legacy=True)
    legacy = [v for v in result.violations if v.kind == "legacy-format"]
    assert len(legacy) == 1
    assert "RR-1" in legacy[0].message


# --- Filter / sort tests ---

def test_filter_status_open_excludes_retired():
    """filter_status='open' returns only open-status risks.

    Defect class: /slice and /status need to ignore retired/accepted risks
    when ranking; filter must work correctly.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, filter_status="open")
    statuses = {r.status for r in view}
    assert statuses == {"open"}, (
        f"expected only open status, got {statuses}"
    )


def test_filter_band_high_returns_only_high():
    """filter_band='high' returns only high-band risks.

    Defect class: A "show me the top concerns" view that includes mediums
    is noise.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, filter_band="high")
    bands = {r.band for r in view}
    assert bands == {"high"}


def test_sort_by_score_desc_then_id():
    """Sort by score (desc), then risk_id (asc) for ties.

    Defect class: Inconsistent sort order means /status and /slice show
    different "top risks" run-to-run, undermining trust in the ranking.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, sort_by="score")
    scores = [r.score for r in view]
    assert scores == sorted(scores, reverse=True), (
        f"expected score desc; got {scores}"
    )
    # First should be R1 (score 9)
    assert view[0].risk_id == "R1"


def test_top_n_limits_output():
    """top=2 returns only the 2 highest-scored risks.

    Defect class: /status surfacing all risks instead of top-N is noise.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, sort_by="score", top=2)
    assert len(view) == 2


def test_summary_counts_by_band_and_status():
    """to_dict() summary aggregates band / status counts correctly.

    Defect class: Wrong aggregates would mislead /status into reporting
    e.g. "5 high open" when only 1 is actually high+open.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    summary = result.to_dict()["summary"]
    assert summary["total"] == 4
    assert summary["by_band"]["high"] == 1
    assert summary["by_band"]["medium"] == 2
    assert summary["by_band"]["low"] == 1
    assert summary["by_status"]["open"] == 2
    assert summary["by_status"]["mitigating"] == 1
    assert summary["by_status"]["retired"] == 1
    assert summary["open_high_count"] == 1


def test_all_retired_register_has_zero_open_high():
    """If everything is retired/accepted, open_high_count is 0.

    Defect class: A register with no active concerns shouldn't surface
    fake "top risks" — /status would mislead the user.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "all_retired.md")
    summary = result.to_dict()["summary"]
    assert summary["open_high_count"] == 0
    assert summary["by_status"]["open"] == 0


# --- Skill prose pins ---

def test_triage_skill_references_rr_1():
    """skills/triage/SKILL.md must reference RR-1 + the new H2 format.

    Defect class: Without /triage emitting the new format, RR-1 is
    inert; legacy table rows accumulate and the audit yields no risks.
    Rule reference: RR-1.
    """
    text = (REPO_ROOT / "skills" / "triage" / "SKILL.md").read_text(encoding="utf-8")
    assert "RR-1" in text, "no RR-1 reference in /triage SKILL.md"
    assert "Likelihood" in text and "Impact" in text, (
        "Likelihood / Impact fields not documented in /triage"
    )


def test_slice_skill_references_rr_1():
    """skills/slice/SKILL.md must reference RR-1 + the audit module.

    Defect class: /slice candidate-gathering not consuming scored risks
    means risk-first ordering reverts to ad-hoc keyword scanning.
    Rule reference: RR-1.
    """
    text = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "RR-1" in text, "no RR-1 reference in /slice SKILL.md"
    assert "risk_register_audit" in text, (
        "no risk_register_audit module reference in /slice"
    )


def test_status_skill_references_rr_1():
    """skills/status/SKILL.md must reference RR-1.

    Defect class: /status not surfacing scored top-N undermines the daily
    risk-awareness signal RR-1 is meant to provide.
    Rule reference: RR-1.
    """
    text = (REPO_ROOT / "skills" / "status" / "SKILL.md").read_text(encoding="utf-8")
    assert "RR-1" in text, "no RR-1 reference in /status SKILL.md"
    assert "risk_register_audit" in text, (
        "no risk_register_audit module reference in /status"
    )
