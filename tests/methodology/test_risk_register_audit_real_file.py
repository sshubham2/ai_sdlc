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


def test_r_3_added_post_slice_019_with_graphify_symbol_conflation_class():
    """R-3 must be added to risk-register.md per slice-019 AC #5,
    parsing cleanly under RR-1 with status=mitigating.

    Per slice-019 AC #5 + ADR-017: R-3 documents the broader-class concern
    that graphify symbol-resolution may conflate same-name cross-file
    symbols into phantom edges. LAYER-EVID-1 is the witness-scoped
    mitigation at the /diagnose 03f-layering pass-template level (NOT
    the graphify-level fix); R-3 tracks the broader class with
    escalation criteria documented.

    Defect class: forgetting to add R-3 leaves the broader-class risk
    untracked; future /critic-calibrate cannot promote a follow-on slice
    to extend LAYER-EVID-1 to other passes or fix graphify upstream
    because the risk isn't in the register.

    Rule reference: slice-019 AC #5 (RR-1 schema for new entry).
    """
    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    result = audit_register(register_path)
    by_id = {r.risk_id: r for r in result.risks}
    assert "R-3" in by_id, (
        "R-3 missing from risk-register parse — slice-019 AC #5 not yet "
        "shipped, or R-3 heading format doesn't match RR-1 schema"
    )
    r3 = by_id["R-3"]
    assert r3.status == "mitigating", (
        f"R-3 status expected 'mitigating' (not 'retired' because graphify-"
        f"level root cause is untouched); got {r3.status!r}"
    )
    assert r3.reversibility == "cheap", (
        f"R-3 reversibility expected 'cheap' (LAYER-EVID-1 pass-template "
        f"prose can be retired in <1 day if graphify is later fixed); "
        f"got {r3.reversibility!r}"
    )
    # The title should signal the broader class — symbol-conflation /
    # phantom edges. Keyword check (lenient — any of these words signal
    # the right concern class).
    title_lower = r3.title.lower()
    assert any(kw in title_lower for kw in ("symbol", "conflate", "phantom", "graphify")), (
        f"R-3 title {r3.title!r} doesn't signal the broader-class concern "
        f"(graphify symbol-resolution / phantom edges / conflation). Check "
        f"AC #5 wording match."
    )


def test_r_4_subentry_charters_030c_and_stays_mitigating():
    """R-4 must remain `mitigating` (NOT `retired`) after slice-031 ships,
    with a sub-entry that charters slice-030C for the essential-coupling
    reframe and carries M-add-1 forward.

    Per slice-031 (split-label 030B) AC #5 + the user-ratified b-split: 030B
    decouples ONLY the incidental class; the essential entry-pin reframe is
    030C's chartered scope. Escalating R-4 to `retired` while the ~20 entry-
    pin rows remain coupled would be the D-3 "silently weakened" failure.

    Defect class: a future edit silently flipping R-4 to `retired` without
    030C shipping would falsely assert the catalog is fully decoupled while
    rows 7-30's essential entry-pins still read untracked
    `~/.claude/methodology-changelog.md`.

    Rule reference: slice-031 AC #5 (R-4 sub-entry per RR-1; SCMD-1).
    """
    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    result = audit_register(register_path)
    by_id = {r.risk_id: r for r in result.risks}
    assert "R-4" in by_id, "R-4 missing from risk-register parse"
    assert by_id["R-4"].status == "mitigating", (
        f"R-4 must stay 'mitigating' until slice-030C ships (incidental-only "
        f"030B does NOT retire R-4); got {by_id['R-4'].status!r}"
    )
    text = register_path.read_text(encoding="utf-8")
    assert "slice-030C" in text or "slice-030c" in text, (
        "R-4 sub-entry must charter slice-030C for the essential-coupling "
        "reframe (the R-4 -> retired path)"
    )
    assert "M-add-1" in text, (
        "R-4 sub-entry must carry M-add-1 forward (DEFERRED at slice-031 "
        "TRI-1, not closed by the b-split)"
    )
