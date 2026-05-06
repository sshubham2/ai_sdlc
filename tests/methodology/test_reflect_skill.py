"""Pin load-bearing prose in skills/reflect/SKILL.md."""
from tests.methodology.conftest import read_file

REFLECT = read_file("skills/reflect/SKILL.md")


def test_reflect_four_categories():
    """Reflection categorizes observations into Validated / Corrected / Discovered / Deferred.

    Defect class: Free-form reflection becomes a victory lap. The four-category
    discipline forces honesty about what reality refuted, what surprised, and
    what was punted.
    Rule reference: META-2.
    """
    assert "#### Validated" in REFLECT
    assert "#### Corrected" in REFLECT
    assert "#### Discovered" in REFLECT
    assert "#### Deferred" in REFLECT


def test_reflect_honesty_discipline():
    """Reflection is not a victory lap.

    Defect class: "All ACs passed, no issues" reflections teach nothing for
    the next slice. Critic calibration data isn't generated.
    Rule reference: META-2.
    """
    assert "HONESTY DISCIPLINE: this is not a victory lap" in REFLECT


def test_reflect_adrs_append_only():
    """Superseded ADRs are append-only history.

    Defect class: Editing ADRs in place destroys the decision record. The
    supersession protocol (status: superseded + supersedes/superseded-by) is
    what makes the vault usable as audit trail.
    Rule reference: META-2.
    """
    assert "DO NOT edit superseded ADRs" in REFLECT
