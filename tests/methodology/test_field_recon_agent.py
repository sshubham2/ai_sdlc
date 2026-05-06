"""Pin load-bearing prose in agents/field-recon.md."""
from tests.methodology.conftest import read_file

FIELD_RECON = read_file("agents/field-recon.md")


def test_field_recon_asymmetric_drop_rule():
    """The asymmetric early-drop rule: drop only on authoritative contradiction.

    Defect class: Symmetric drop rule — recommending `drop` on confirmation
    bypasses the empirical test, which is the entire point of the spike pipeline.
    Docs lie about things working more often than they admit broken behavior.
    Rule reference: META-2.
    """
    assert "Asymmetric rule" in FIELD_RECON
    assert "OFFICIAL source" in FIELD_RECON
    assert "DIRECTLY CONTRADICTS" in FIELD_RECON


def test_field_recon_never_drop_on_confirmation():
    """Even if findings confirm the assumption, empirical test is still required.

    Defect class: Skipping the spike when docs say "this works" is the failure
    mode this skill was born from (Google Drive `drive.file` scope).
    Rule reference: META-2.
    """
    # The rule appears in `proceed` description: "Even if findings confirm the
    # assumption — docs lie." We pin the load-bearing phrase.
    assert "docs lie" in FIELD_RECON.lower()
