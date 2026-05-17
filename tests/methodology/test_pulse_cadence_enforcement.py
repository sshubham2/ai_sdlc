"""Verify CAL-1 — explicit critic-calibrate cadence enforcement in /pulse.

Per CAL-1 (methodology-changelog.md v0.5.0), /pulse categorizes calibration
cadence as: within window (0-9) / approaching (10-14) / recommended (15-20) /
overdue (>20). Overdue surfaces as top recommendation overriding others.

Rule reference: CAL-1. Skill renamed /status→/pulse at slice-035 (SRCD-1).
"""
from tests.methodology.conftest import read_file

PULSE = read_file("skills/pulse/SKILL.md")


def test_pulse_names_four_cadence_categories():
    """All four cadence states must be named in the SKILL.md prose.

    Defect class: A cadence check that doesn't enumerate states falls back
    to vague "if many slices have passed, suggest running" — which is what
    we had before. Four-state categorization is what makes enforcement
    deterministic.
    Rule reference: CAL-1.
    """
    assert "within window" in PULSE
    assert "approaching" in PULSE
    assert "recommended" in PULSE
    assert "overdue" in PULSE


def test_pulse_pins_threshold_numbers():
    """The literal threshold numbers (10-20) must be in the SKILL.md.

    Defect class: Threshold drift — "every 10-20 slices" is the canonical
    rule from /critic-calibrate; if /pulse uses different numbers, the
    cadence enforcement disagrees with the meta-skill itself.
    Rule reference: CAL-1.
    """
    assert "10-20" in PULSE


def test_pulse_overdue_overrides_other_recommendations():
    """When overdue, calibration must surface as top recommendation.

    Defect class: An overdue ⚠️⚠️ flag buried in a metrics section won't
    actually move users to act. Promoting it to override "Recommended next
    action" is what closes the cadence loop.
    Rule reference: CAL-1.
    """
    text_lower = PULSE.lower()
    has_override_language = (
        "supersede" in text_lower
        or "overrides" in text_lower
        or "override" in text_lower
        or "top line" in text_lower
    )
    assert has_override_language, (
        "no override/promotion language for overdue calibration found in /pulse"
    )


def test_pulse_handles_empty_calibration_log_gracefully():
    """First-run case (empty log + <10 archived slices) must not flag overdue.

    Defect class: Treating an empty calibration log as "infinitely overdue"
    creates noise in fresh projects. The deferred-first-run rule prevents
    this false positive.
    Rule reference: CAL-1.
    """
    text = PULSE.lower()
    has_first_run_language = (
        "first calibration deferred" in text
        or "first-run" in text
        or "first run" in text
        or "<10 archived slices" in text
    )
    assert has_first_run_language, (
        "no deferred-first-run language for fresh projects found in /pulse"
    )


def test_pulse_references_cal_1_rule():
    """SKILL.md must cross-reference the CAL-1 rule for traceability.

    Defect class: Rule changes that aren't traceable to the changelog can't
    be evaluated for impact. A `CAL-1` reference lets readers trace
    rationale.
    Rule reference: CAL-1.
    """
    assert "CAL-1" in PULSE, "no CAL-1 reference found in /pulse SKILL.md"


def test_pulse_uses_emoji_severity_distinction():
    """The two warning levels (⚠️ recommended vs ⚠️⚠️ overdue) must be
    visually distinct.

    Defect class: One-emoji-fits-all flagging hides the difference between
    "approaching threshold" (info) and "well past threshold" (act now).
    The double-emoji escalation makes overdue impossible to miss in
    /pulse output.
    Rule reference: CAL-1.
    """
    # Single warning emoji should appear at least twice (recommended + overdue use it)
    # Double emoji should appear at least once (overdue exclusively)
    assert PULSE.count("⚠️") >= 2, "expected at least 2 occurrences of warning emoji"
    assert "⚠️⚠️" in PULSE, "no double-warning escalation found for overdue state"
