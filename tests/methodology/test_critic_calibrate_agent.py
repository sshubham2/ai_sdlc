"""Pin load-bearing prose in agents/critic-calibrate.md."""
from tests.methodology.conftest import read_file

CALIBRATE = read_file("agents/critic-calibrate.md")


def test_calibrate_requires_three_distinct_slices():
    """A category needs ≥3 entries across distinct slices to warrant a proposal.

    Defect class: Pattern manufacturing — proposing prompt changes from anecdote
    bloats the Critic prompt with one-off accommodations. The threshold is what
    makes calibration evidence-based.
    Rule reference: META-2.
    """
    assert "≥3 entries across distinct slices" in CALIBRATE


def test_calibrate_caps_at_three_proposals():
    """Cap at 3 proposals per run.

    Defect class: Bloated Critic prompts get skimmed; signal density matters more
    than coverage. Without a cap, calibration runs accumulate weak proposals.
    Rule reference: META-2.
    """
    assert "Cap at 3 proposals" in CALIBRATE


def test_calibrate_honesty_over_volume():
    """Zero proposals is a valid result.

    Defect class: Manufactured proposals to justify the run damage the calibration
    loop. Honest-zero must be acceptable.
    Rule reference: META-2.
    """
    assert "Honesty over volume" in CALIBRATE
