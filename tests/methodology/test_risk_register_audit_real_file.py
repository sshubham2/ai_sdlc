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


def test_r_4_retired_by_slice_041_030c_completes_the_split():
    """R-4 MUST be `retired` after slice-041 (split-lineage label "030C")
    ships — the essential-coupling reframe that completes the slice-030
    split (030A substance → 030B incidental → 030C essential).

    Realigned in slice-041's own fix block (slice-039 same-fix-block
    discipline): the predecessor pin asserted "R-4 stays mitigating until
    030C ships" — slice-041 IS 030C, so R-4 retirement is this slice's
    deliverable; a pin still asserting `mitigating` would FAIL the slice
    that legitimately retires the risk. The non-regression invariant flips
    accordingly.

    Defect class: a future edit silently flipping R-4 back to `mitigating`
    / dropping the `**Retired**: slice-041` provenance / losing the
    030A→030B→030C lineage would falsely re-open a fully-discharged risk
    (the essential reads ARE decoupled + the cross-module pin registered).

    Rule reference: slice-041 R-4 escalation (RR-1; MCFS-1 / ADR-042 +
    ADR-043; supersedes the slice-031-era `_stays_mitigating` pin).
    """
    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    result = audit_register(register_path)
    by_id = {r.risk_id: r for r in result.risks}
    assert "R-4" in by_id, "R-4 missing from risk-register parse"
    assert by_id["R-4"].status == "retired", (
        f"R-4 must be 'retired' after slice-041 (030C) ships — the "
        f"essential-coupling reframe is complete; got "
        f"{by_id['R-4'].status!r}"
    )
    text = register_path.read_text(encoding="utf-8")
    assert "**Retired**: slice-041" in text, (
        "R-4 must carry a `**Retired**: slice-041 …` provenance line"
    )
    for tok in ("030A", "030B", "030C"):
        assert tok in text, (
            f"R-4 entry must record the {tok} split lineage (030A substance "
            f"→ 030B incidental → 030C essential)"
        )


def test_r_18_retired_post_slice_063():
    """R-18 MUST be `retired` after slice-063 (NAW-1 mint) ships — the
    new-agent session-restart warning audit IS the structural discharge
    mechanism for R-18's recurring-class signal.

    Slice-063 ships `tools/new_agent_warning_audit.py` (NAW-1) wired at
    `/build-slice` Step 6 to emit a non-blocking WARN naming the agent
    path + session-restart recommendation + R-18 cross-reference when
    the slice diff adds any `agents/*.md` file. The methodology now
    surfaces R-18's failure mode (Claude Code agent registry session-
    cache miss) BEFORE the next slice's chain runs, retiring the risk's
    `mitigating` status (N=2 cumulative recurrence at slice-061 +
    slice-062 surfaced the class methodology-discoverably).

    Defect class: a future edit silently flipping R-18 back to
    `mitigating` / dropping the `**Retired**: slice-063` provenance /
    losing the NAW-1 mechanism citation would falsely re-open a fully-
    discharged risk (the warn surface IS in place + the WIRE-1 consumer
    test asserts the SKILL.md anchor).

    Rule reference: NAW-1 (slice-063; ADR-061; methodology-changelog
    v0.66.0; mints a new rule; supersedes nothing — naming-class peer
    of CRSI-1 / TVFS-1 / PVFS-1 / AVFS-1 forward-sync family but on the
    discovery-gate axis).
    """
    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    result = audit_register(register_path)
    by_id = {r.risk_id: r for r in result.risks}
    assert "R-18" in by_id, "R-18 missing from risk-register parse"
    assert by_id["R-18"].status == "retired", (
        f"R-18 must be 'retired' after slice-063 (NAW-1) ships — the "
        f"new-agent warning audit IS the structural discharge "
        f"mechanism; got {by_id['R-18'].status!r}"
    )
    text = register_path.read_text(encoding="utf-8")
    # Provenance pin: the slice-063 retirement paragraph must cite
    # NAW-1 / new_agent_warning_audit as the discharge mechanism.
    assert "slice-063" in text, (
        "risk-register.md must reference slice-063 in the R-18 "
        "retirement paragraph"
    )
    assert "NAW-1" in text or "new_agent_warning_audit" in text, (
        "R-18 retirement paragraph must cite the NAW-1 discharge "
        "mechanism (either RULE-ID `NAW-1` or the tool name "
        "`new_agent_warning_audit`)"
    )
