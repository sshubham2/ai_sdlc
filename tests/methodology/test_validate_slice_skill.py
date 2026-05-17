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


def test_step4_5_5_consumes_machine_stable_command():
    """Step 5.5 runner consumes the machine-stable command column, NOT the
    prose `Command` column (slice-031 / SCMD-1 / ADR-031, v2-B2).

    Defect class: B2-v1 — the *actual* /validate-slice runner is this SKILL.md
    Step 5.5 prose. If it still said "Run each entry's Command column", the
    rows #28/#29 narrative-prose-as-command footgun (D-2) would remain at the
    real execution site even though the tools were repointed. This prose-pin
    is the mini-CAD anchor for the runner-side half of AC3.
    Rule reference: SCMD-1.
    """
    assert "Run each entry's **Machine-cmd** column" in VALIDATE, (
        "Step 5.5 runner must consume the Machine-cmd column (B2-v1)"
    )
    assert "tools.shippability_decoupling_audit" in VALIDATE, (
        "SCMD-1 must be wired as a non-opt-out Step 5.5 pre-catalog gate"
    )
    # PTFCD-1 must now read the Machine-cmd cell, not the Command cell.
    assert "every row's **Machine-cmd** cell resolves" in VALIDATE
