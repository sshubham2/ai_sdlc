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
    """Step 5.5 catalog execution is the INVOKED pinned runner, not a
    hand-rolled prose loop (slice-038 / SRSC-1 / ADR-039).

    Supersession lineage: this pin was originally the slice-031 SCMD-1 B2-v1
    prose-pin asserting `Run each entry's **Machine-cmd** column` — the dead
    wording from when Step 5.5 described a hand-rolled loop over the
    Machine-cmd cell. slice-038 (SRSC-1; ADR-039; methodology v0.51.0) closed
    the R-8 false-FAIL class by making the catalog executor an INVOKED tool
    (`tools.shippability_runner`, which itself reuses SCMD-1 `_segments()`)
    instead of a per-slice description — so the slice-031 phrase no longer
    exists in SKILL.md and this pin had been FAILing slice-innocently on
    master since slice-038 (risk-register R-10; realigned by slice-040).

    Defect class still guarded: B2-v1 — the *actual* /validate-slice catalog
    executor is what SKILL.md Step 5.5 prescribes. The pin now asserts the
    SRSC-1 contract (Step 5.5 INVOKES the canonical pinned runner; an ad-hoc
    hand-rolled loop is forbidden) at the live wording. Both anchors are
    SRSC-1-exclusive and absent from the pre-SRSC-1 slice-031 wording, so the
    pin remains non-tautological: a regression of Step 5.5 to the pre-SRSC-1
    hand-rolled-loop prose FAILs it. Mini-CAD anchor for the runner-side
    half of AC3.
    Rule reference: SRSC-1 (supersedes the slice-031 SCMD-1 B2-v1 pin;
    ADR-039 / ADR-031).
    """
    assert "$PY -m tools.shippability_runner architecture/shippability.md" in VALIDATE, (
        "Step 5.5 must INVOKE the canonical pinned runner "
        "`$PY -m tools.shippability_runner architecture/shippability.md` "
        "(SRSC-1 / ADR-039), not hand-roll the catalog execution loop"
    )
    assert "canonical pinned runner" in VALIDATE, (
        "Step 5.5 must name the SRSC-1 `canonical pinned runner` contract "
        "(ADR-039) — guards the 'do NOT hand-roll the execution loop' invariant"
    )
    assert "tools.shippability_decoupling_audit" in VALIDATE, (
        "SCMD-1 must be wired as a non-opt-out Step 5.5 pre-catalog gate"
    )
    # PTFCD-1 must now read the Machine-cmd cell, not the Command cell.
    assert "every row's **Machine-cmd** cell resolves" in VALIDATE


def test_validate_slice_predecessor_is_code_review():
    """Per CRSI-1 (slice-060 / methodology-changelog v0.64.0 / ADR-059):
    skills/validate-slice/SKILL.md Pipeline-position MUST declare
    `predecessor: /code-review` post-slice-060 (was `/build-slice` before).
    """
    assert "## Pipeline position" in VALIDATE, (
        "skills/validate-slice/SKILL.md missing `## Pipeline position` block"
    )
    assert "**predecessor**: `/code-review`" in VALIDATE, (
        "skills/validate-slice/SKILL.md Pipeline-position `predecessor:` field "
        "must point to `/code-review` per CRSI-1 (slice-060)"
    )
    idx = VALIDATE.find("## Pipeline position")
    pp_block = VALIDATE[idx:]
    assert "**predecessor**: `/build-slice`" not in pp_block, (
        "skills/validate-slice/SKILL.md Pipeline-position has stale "
        "`predecessor: /build-slice` (pre-slice-060) — re-apply CRSI-1 flip"
    )
