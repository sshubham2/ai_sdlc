"""Pin load-bearing prose in agents/diagnose-narrator.md."""
from tests.methodology.conftest import read_file

NARRATOR = read_file("agents/diagnose-narrator.md")


def test_narrator_tone_is_forensic():
    """The narrator must be forensic, not flattering.

    Defect class: Marketing voice — "impressive system with opportunities for
    refinement" has the same word count as "solid base drifting toward
    over-engineering" but communicates nothing. The forensic discipline is what
    makes the diagnosis useful to the owner.
    Rule reference: META-2.
    """
    assert "Forensic, not flattering" in NARRATOR


def test_narrator_target_length():
    """The narrator's target is ~500–900 words.

    Defect class: 1500-word executive summaries get skimmed; 200-word ones have
    no shape. The target length is what makes the narrative engaging.
    Rule reference: META-2.
    """
    assert "500–900 words" in NARRATOR or "500-900 words" in NARRATOR


def test_narrator_story_over_list():
    """The narrator must find the through-line, not enumerate findings.

    Defect class: Listing findings instead of telling their story produces a
    mechanical report owners skim. Story is what makes them annotate with care.
    Rule reference: META-2.
    """
    assert "Story over list" in NARRATOR
