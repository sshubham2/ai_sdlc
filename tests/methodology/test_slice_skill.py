"""Pin load-bearing prose in skills/slice/SKILL.md."""
from tests.methodology.conftest import read_file

SLICE = read_file("skills/slice/SKILL.md")


def test_slice_scope_limits():
    """A slice is ≤5 acceptance criteria and ≤1 day of AI work.

    Defect class: Slice bloat — a 12-AC, 3-day slice defeats mid-slice smoke
    gates and reflection. Without enforced limits, slices grow into sprints.
    Rule reference: META-2.
    """
    assert "≤5 acceptance criteria" in SLICE
    assert "≤1 day of AI implementation work" in SLICE


def test_slice_lists_mandatory_critic_triggers():
    """Always-mandatory Critic triggers must include the load-bearing categories.

    Defect class: Trigger erosion — quietly dropping any of these triggers
    means a low-tier slice that touches auth/contracts/data/sync skips the
    Critic. That's exactly the case where the Critic earns its keep.
    Rule reference: META-2.
    """
    # Find the Always-mandatory section and verify all triggers present
    assert "Always mandatory Critic" in SLICE
    # Trigger list — these substrings appear in the bulleted triggers
    assert "Auth / authz" in SLICE
    assert "API contracts" in SLICE
    assert "Data model changes" in SLICE
    assert "Multi-device" in SLICE
    assert "External integrations" in SLICE


def test_slice_verb_object_naming_rule():
    """Slice names must be verb-object, not phase-N or vague nouns.

    Defect class: Vague slice names (`phase-2`, `slice-N`, `improvements`)
    defeat the discipline of mission-brief intent and verification planning.
    Rule reference: META-2.
    """
    assert "VERB-OBJECT names only" in SLICE
