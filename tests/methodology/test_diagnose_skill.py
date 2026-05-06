"""Pin load-bearing prose in skills/diagnose/SKILL.md."""
from tests.methodology.conftest import read_file

DIAGNOSE = read_file("skills/diagnose/SKILL.md")


def test_diagnose_never_modifies_source():
    """Diagnose never modifies source files in the target repo.

    Defect class: A diagnostic that mutates the analyzed code is no longer
    diagnostic — it's a refactor. The non-mutation rule is what makes the
    deliverable trustworthy as a forensic snapshot.
    Rule reference: META-2.
    """
    assert "Never modify source files in the target repo" in DIAGNOSE


def test_diagnose_no_documentation_reads():
    """Diagnose reads code only — no documentation reads from the target.

    Defect class: Trusting README leads to documenting what docs claim instead
    of what code does. The doc-skip rule is the cure for the brownfield
    "trust the docs" failure mode.
    Rule reference: META-2.
    """
    assert "No documentation reads from the target codebase" in DIAGNOSE


def test_diagnose_never_invents_findings():
    """Diagnose never invents findings to fill quota.

    Defect class: Manufactured findings damage the deliverable's signal-to-noise
    and waste owner annotation effort. Empty is a valid result.
    Rule reference: META-2.
    """
    assert "Never invent findings" in DIAGNOSE


def test_diagnose_pipeline_agnostic_output():
    """Diagnose output must be pipeline-agnostic.

    Defect class: SDLC-specific terminology in the deliverable couples the
    forensic report to a specific toolchain, defeating its value as an
    independent diagnostic.
    Rule reference: META-2.
    """
    assert "All output is pipeline-agnostic" in DIAGNOSE
