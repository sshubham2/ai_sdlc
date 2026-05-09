"""Integration test: project's real risk-register.md is RR-1-audit clean.

Slice-002 AC #3. Runs `tools.risk_register_audit` against the project's
actual `architecture/risk-register.md` and asserts:
- ≥1 risk parsed (the file is NOT silently empty / legacy-format)
- zero parse violations (file conforms to RR-1 H2-structured schema)

This is a *meta* test on the project's vault — when future slices add
risks, the test still passes as long as the format is clean. If a future
slice adds a malformed entry, this test surfaces the issue at /build-slice
pre-finish, forcing the offending slice to fix the format before /reflect
can land.

Rule reference: slice-002 AC #3.
"""
from tests.methodology.conftest import REPO_ROOT
from tools.risk_register_audit import audit_register


def test_project_risk_register_audit_clean():
    """The project's risk-register.md must parse cleanly under RR-1.

    Defect class: a risk-register entry with a non-RR-1 format (legacy
    H3, missing required fields, invalid status enum value) is silently
    invisible to /slice's risk-first ranking. Slice-002 converts the
    file to RR-1; this test guards against future regressions.
    """
    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    assert register_path.exists(), (
        f"risk-register.md not found at {register_path}; "
        "expected by slice-002 AC #3"
    )
    result = audit_register(register_path)
    assert len(result.risks) >= 1, (
        f"risk-register.md parsed {len(result.risks)} risks; expected ≥1. "
        "Either the file is empty, in legacy table format, or all entries "
        "have malformed headings."
    )
    assert result.violations == [], (
        f"risk-register.md has {len(result.violations)} parse violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_slice_004_no_regression_in_existing_risk_register():
    """slice-004's docstring/comment/risk-register.md changes don't change R-1 / R-2 parsing.

    Regression-guard invariant (NOT a TF-1 AC row per Critic M1):
    existing em-dash entries return identical scores+bands pre/post
    slice-004. Slice-004 makes zero behavior changes — purely
    documentation-only edits to the audit's docstring + inline comment
    + risk-register.md L3 prelude prose. If a future slice changes
    regex behavior in a way that affects scoring, this test fails
    loudly rather than silently shifting risk rankings.

    Slice-004 must-not-defer item #1.
    Rule reference: RR-1.
    """
    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    result = audit_register(register_path)
    by_id = {r.risk_id: r for r in result.risks}
    assert "R-1" in by_id, "R-1 missing from risk-register parse"
    assert "R-2" in by_id, "R-2 missing from risk-register parse"
    assert by_id["R-1"].score == 6 and by_id["R-1"].band == "high", (
        f"R-1 expected score=6 band=high; got "
        f"score={by_id['R-1'].score} band={by_id['R-1'].band}"
    )
    assert by_id["R-2"].score == 2 and by_id["R-2"].band == "low", (
        f"R-2 expected score=2 band=low; got "
        f"score={by_id['R-2'].score} band={by_id['R-2'].band}"
    )
