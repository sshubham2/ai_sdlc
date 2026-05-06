"""Pin load-bearing prose in skills/validate-slice/SKILL.md."""
from tests.methodology.conftest import read_file

VALIDATE = read_file("skills/validate-slice/SKILL.md")


def test_validate_requires_real_environments():
    """Validation runs on real environments, not mocks.

    Defect class: Tests-pass-but-feature-broken — mocks return what the test
    expects, not what the real API does. Real-environment validation is the
    single most load-bearing rule in this skill.
    Rule reference: META-2.
    """
    assert "USE REAL ENVIRONMENTS" in VALIDATE


def test_validate_multi_instance_for_multi_user():
    """Multi-instance validation is mandatory for multi-user/device features.

    Defect class: Single-instance passing for sync/sharing/multi-user features
    is the exact failure mode the Google Drive `drive.file` incident exposed.
    The rule is non-negotiable.
    Rule reference: META-2.
    """
    assert "MULTI-INSTANCE for multi-user/device features" in VALIDATE
    assert "ALWAYS" in VALIDATE  # the emphatic force on the rule


def test_validate_partial_is_partial():
    """A partial criterion cannot be passed as PASS.

    Defect class: Optimistic verdicts let half-broken work ship. Partial must
    surface its partiality so /reflect can capture the deferred gap.
    Rule reference: META-2.
    """
    assert "DO NOT pass a partial criterion as PASS" in VALIDATE
