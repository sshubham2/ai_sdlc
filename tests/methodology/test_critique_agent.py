"""Pin load-bearing prose in agents/critique.md.

The Critic prompt is the most adversarially-load-bearing artifact in the pipeline.
Drift here directly degrades review quality.
"""
from tests.methodology.conftest import read_file

CRITIQUE = read_file("agents/critique.md")


def test_critique_carries_adversarial_stance():
    """The Critic must carry an explicit adversarial stance.

    Defect class: Stance softening — paraphrasing to "review the design" loses the
    adversarial property. The Critic that asks rather than attacks is a rubber stamp.
    Rule reference: META-2.
    """
    assert "Assume the design is wrong until proven right" in CRITIQUE


def test_critique_forbids_softening_findings():
    """The Critic must not soften findings to be diplomatic.

    Defect class: Diplomatic findings train the Builder to ignore the Critic, which
    breaks the calibration loop and reverts the pipeline to single-AI quality gates.
    Rule reference: META-2.
    """
    assert "Do not soften findings" in CRITIQUE


def test_critique_forbids_manufactured_findings():
    """The Critic must not manufacture findings to justify the review.

    Defect class: Manufactured findings damage the calibration loop and train the
    Builder to ignore the Critic. Manufactured findings make the Critic worse over time.
    Rule reference: META-2.
    """
    assert "Do NOT manufacture findings to justify the review" in CRITIQUE


def test_critique_lists_eight_dimensions():
    """The Critic must walk all eight review dimensions.

    Defect class: Dimension drift — collapsing the eight named dimensions into a
    single "look for issues" instruction loses the perspective-based-reading benefit.
    Rule reference: META-2.
    """
    assert "1. Unfounded assumptions" in CRITIQUE
    assert "2. Missing edge cases" in CRITIQUE
    assert "3. Over-engineering" in CRITIQUE
    assert "4. Under-engineering" in CRITIQUE
    assert "5. Contract gaps" in CRITIQUE
    assert "6. Security" in CRITIQUE
    assert "7. Drift from vault" in CRITIQUE
    assert "8. Web-known issues" in CRITIQUE


def test_critique_names_reference_frameworks():
    """The Critic must cite specific named frameworks per dimension.

    Defect class: Citation collapse — dropping named experts replaces vetted
    methodology with blended training-data heuristics.
    Rule reference: META-2.
    """
    assert "Wiegers" in CRITIQUE
    assert "Fowler" in CRITIQUE
    assert "Newman" in CRITIQUE
    assert "OWASP" in CRITIQUE
    assert "McGraw" in CRITIQUE
    assert "Hendrickson" in CRITIQUE


def test_critique_specifies_severity_levels():
    """The Critic must distinguish Blocker / Major / Minor severity.

    Defect class: Severity inflation or collapse — flat severity makes blockers
    meaningless and trains the Builder to dismiss the Critic.
    Rule reference: META-2.
    """
    assert "**Blocker**" in CRITIQUE
    assert "**Major**" in CRITIQUE
    assert "**Minor**" in CRITIQUE
