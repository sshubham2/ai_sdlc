"""PCR-2b (slice-083 / ADR-075) AC#3 — TRI-RESOLVE-1 SKILL.md-prose structural pins.

TRI-RESOLVE-1 is orchestrated by skills/commit-slice/SKILL.md sub-step 2.5 prose
(Python cannot spawn skill agents / present an AskUserQuestion). These pins are
the SKILL.md-prose-as-executable-contract structural guards: the SOAD-1
structured-options form, the fail-closed no-silent-continue contract, and the
code-review-agent-not-critique-agents decision. Literals chosen UNIQUE-TO-THE-
INVOCATION per the slice-075 RSAD-1 lesson.
"""

from pathlib import Path


def _skill_text() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    return (repo_root / "skills" / "commit-slice" / "SKILL.md").read_text(encoding="utf-8")


def test_tri_resolve_1_soad1_structured_options_form_pinned():
    """The TRI-RESOLVE-1 gate is a SOAD-1 structured-options ask (AskUserQuestion),
    NEVER free-text, with the three canonical options."""
    text = _skill_text()
    assert "TRI-RESOLVE-1 user-triage gate" in text, (
        "commit-slice SKILL.md must name the TRI-RESOLVE-1 user-triage gate"
    )
    assert "structured-options via the `AskUserQuestion` tool, NEVER a free-text prompt" in text, (
        "TRI-RESOLVE-1 must be pinned as structured-options (SOAD-1), never free-text"
    )
    # Three canonical options.
    assert "Apply resolution (continue rebase)" in text
    assert "Re-resolve (edit again)" in text
    assert "Abort rebase" in text


def test_tri_resolve_1_fail_closed_no_silent_continue_pinned():
    """Fail-closed: every non-Apply option + any interrupt maps to STOP-no-continue;
    two-condition apply (explicit Apply AND non-blocking verdict)."""
    text = _skill_text()
    assert (
        "every non-`Apply` option AND any interrupt / no-selection / session-end "
        "maps to STOP-no-continue" in text
    ), "TRI-RESOLVE-1 fail-closed (non-Apply/interrupt -> STOP) prose pin missing"
    assert "two-condition apply" in text, (
        "TRI-RESOLVE-1 two-condition apply (explicit Apply + non-blocking verdict) pin missing"
    )
    assert "no default-accept" in text, (
        "TRI-RESOLVE-1 must pin 'no default-accept' (no silent auto-continue)"
    )


def test_pcr_2b_uses_code_review_agent_not_critique_agents():
    """Per ADR-075 M-add-2: the HARD-resolution Critic is the diff-calibrated
    `code-review` agent, NOT the design-calibrated `/critique` agents."""
    text = _skill_text()
    assert 'subagent_type: "code-review"' in text, (
        "PCR-2b gate must spawn the code-review agent (subagent_type: code-review)"
    )
    assert "the `/critique` + `/critique-review` agents are NOT and fail-stop on a missing slice `design.md`" in text, (
        "PCR-2b prose must record WHY the critique agents are not used (M-add-2)"
    )


def test_pcr_2b_verify_resolution_keys_on_openers_not_equals():
    """Per ADR-075 B2/M-add-1: --verify-resolution keys on the <<<<<<</>>>>>>>
    openers, NOT `=======`, so Markdown setext headings do not false-STOP."""
    text = _skill_text()
    assert "keyed on the openers, NOT `=======`, so Markdown setext headings do NOT false-STOP" in text, (
        "PCR-2b verify-resolution prose must pin the openers-not-equals fix (B2/M-add-1)"
    )


def test_pcr_2b_bootstrap_fallback_to_soad1_pinned():
    """Bootstrap defense: missing/failing resolver helper -> unchanged SOAD-1 STOP."""
    text = _skill_text()
    assert "Bootstrap guard" in text and "fall through to the existing SOAD-1 3-option block" in text, (
        "PCR-2b gate must preserve the bare SOAD-1 STOP as the bootstrap fallback"
    )
