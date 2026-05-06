"""Pin load-bearing prose in skills/build-slice/SKILL.md."""
from tests.methodology.conftest import read_file

BUILD = read_file("skills/build-slice/SKILL.md")


def test_build_requires_plan_mode_first():
    """Build-slice must enter plan mode before editing.

    Defect class: Skipping plan mode produces edits against assumptions rather
    than actual code. Plan mode is what gives the Builder groundedness.
    Rule reference: META-2.
    """
    assert "ENTER PLAN MODE FIRST" in BUILD


def test_build_forbids_silent_deferral():
    """Must-not-defer items cannot be silently deferred.

    Defect class: Silent deferral of auth/validation/error-handling items is
    how production-affecting gaps ship. The skill must require explicit user
    approval to defer, not allow silent skipping.
    Rule reference: META-2.
    """
    assert "DO NOT silently defer must-not-defer items" in BUILD


def test_build_smoke_gate_required():
    """Mid-slice smoke gate is non-skippable.

    Defect class: Skipping the smoke gate at ~50% of work means the slice
    builds on a broken base. The gate catches "builds but doesn't work" before
    more is built.
    Rule reference: META-2.
    """
    assert "DO NOT skip the mid-slice smoke gate" in BUILD


def test_build_log_events_before_risky_calls():
    """Append events to build-log.md before risky tool calls.

    Defect class: Tool failures (corrupted binaries, parser errors) can erase
    in-memory context. Events written before the risky call survive on disk.
    Rule reference: META-2.
    """
    assert "APPEND TO build-log.md events BEFORE risky tool calls" in BUILD
