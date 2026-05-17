"""Tests for tools.risk_register_audit (RR-1).

Validates that the audit correctly:
- Parses H2-structured risks with required + optional fields
- Computes Score = Likelihood * Impact (low=1, medium=2, high=3 -> 1..9)
- Maps Score -> Band (1-2 low, 3-4 medium, 6-9 high)
- Flags missing required fields, invalid values, duplicate IDs
- Returns empty result for empty/missing files (no false alarms)
- Optionally surfaces deprecation for legacy table format (--warn-legacy)
- Sorts and filters for downstream /slice + /pulse consumption

Pins skill prose in /triage, /slice, /pulse referencing RR-1.

Rule reference: RR-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
import json

from tools.risk_register_audit import (
    _RISK_HEADING_RE,
    _band_for_score,
    audit_register,
    filter_and_sort,
    main,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "risk_register"


# --- Score / band unit tests ---

def test_band_low_for_score_1_2():
    """Score 1 and 2 -> low band.

    Defect class: A scoring scale that doesn't match common risk-management
    conventions (low=non-actionable nuisance) trains users to ignore the
    band and reason from raw L*I numbers.
    Rule reference: RR-1.
    """
    assert _band_for_score(1) == "low"
    assert _band_for_score(2) == "low"


def test_band_medium_for_score_3_4():
    """Score 3 and 4 -> medium band.

    Defect class: A scale that conflates medium and high turns most risks
    into "high"; band loses meaning.
    Rule reference: RR-1.
    """
    assert _band_for_score(3) == "medium"
    assert _band_for_score(4) == "medium"


def test_band_high_for_score_6_9():
    """Score 6 and 9 -> high band (5 isn't reachable from 1-3 levels).

    Defect class: Without a clear high cutoff, the audit can't reliably
    pull "the top N concerns" for /pulse / /slice.
    Rule reference: RR-1.
    """
    assert _band_for_score(6) == "high"
    assert _band_for_score(9) == "high"


# --- File-level audit tests ---

def test_clean_register_parses_all_risks():
    """A valid register with 4 risks parses cleanly with computed scores.

    Defect class: A parser that mis-counts or skips risks would cause
    /slice and /pulse to show wrong rankings.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.risks) == 4
    by_id = {r.risk_id: r for r in result.risks}
    # R1: high*high=9 -> high
    assert by_id["R1"].score == 9
    assert by_id["R1"].band == "high"
    # R2: medium*medium=4 -> medium
    assert by_id["R2"].score == 4
    assert by_id["R2"].band == "medium"
    # R3: low*high=3 -> medium
    assert by_id["R3"].score == 3
    assert by_id["R3"].band == "medium"
    # R4: low*low=1 -> low
    assert by_id["R4"].score == 1
    assert by_id["R4"].band == "low"


def test_optional_fields_are_captured():
    """Reversibility, Mitigation, Discovered, Notes are parsed when present.

    Defect class: Optional fields silently dropped means /pulse couldn't
    surface mitigation status or discovery context.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    by_id = {r.risk_id: r for r in result.risks}
    assert by_id["R1"].reversibility == "expensive"
    assert "spike-002" in by_id["R1"].mitigation
    assert "triage" in by_id["R1"].discovered
    # R3 has Notes
    assert "Verified across" in by_id["R3"].notes
    # R4 has no optional fields
    assert by_id["R4"].mitigation == ""
    assert by_id["R4"].notes == ""


def test_missing_required_field_is_violation():
    """Missing Likelihood is a violation, not a silent zero.

    Defect class: A risk without Likelihood that gets a default of 0
    would silently rank lowest and be ignored — exactly the opposite of
    what's typically the case (missing fields signal an unfinished entry).
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "missing_likelihood.md")
    missing = [v for v in result.violations if v.kind == "missing-field"]
    assert len(missing) == 1
    assert "likelihood" in missing[0].message.lower()


def test_invalid_status_is_violation():
    """Status outside the allowed vocabulary is flagged.

    Defect class: An open vocabulary lets statuses drift to "maybe" /
    "kind of" / "later" — undermining filter-by-status.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "invalid_status.md")
    invalid = [v for v in result.violations if v.kind == "invalid-value"]
    assert any("status" in v.message.lower() for v in invalid), (
        f"expected status invalid-value; got "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_duplicate_id_is_violation():
    """Duplicate risk IDs are flagged.

    Defect class: Two risks sharing an ID corrupt every downstream lookup
    (which one does R7 refer to?). Detect at parse-time.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "duplicate_id.md")
    dup = [v for v in result.violations if v.kind == "duplicate-id"]
    assert len(dup) == 1
    # Only the first risk should be parsed
    assert len(result.risks) == 1


def test_empty_register_is_clean_with_zero_risks():
    """An empty register parses cleanly with zero risks, no violation.

    Defect class: A new project's empty register shouldn't flood logs
    with violations. Empty is normal.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "empty_register.md")
    assert result.risks == []
    assert result.violations == []


def test_missing_register_file_is_silent():
    """Missing register.md returns empty result, not crash, not violation.

    Defect class: A linter that crashes on a missing input is hostile.
    Many projects won't have a register at all.
    Rule reference: RR-1.
    """
    result = audit_register(REPO_ROOT / "does-not-exist-xyz-rr.md")
    assert result.risks == []
    assert result.violations == []


def test_legacy_format_silent_by_default():
    """Legacy table format yields zero risks but NO violation by default.

    Defect class: A breaking refusal would force every project to migrate
    immediately; opt-in migration via --warn-legacy is gentler.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "legacy_register.md", warn_legacy=False)
    assert result.risks == []
    assert result.violations == []


def test_legacy_format_flagged_with_warn_legacy():
    """--warn-legacy surfaces a deprecation violation for the old table.

    Defect class: Without an opt-in warning, projects never realize their
    register isn't being scored.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "legacy_register.md", warn_legacy=True)
    legacy = [v for v in result.violations if v.kind == "legacy-format"]
    assert len(legacy) == 1
    assert "RR-1" in legacy[0].message


# --- Filter / sort tests ---

def test_filter_status_open_excludes_retired():
    """filter_status='open' returns only open-status risks.

    Defect class: /slice and /pulse need to ignore retired/accepted risks
    when ranking; filter must work correctly.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, filter_status="open")
    statuses = {r.status for r in view}
    assert statuses == {"open"}, (
        f"expected only open status, got {statuses}"
    )


def test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks(capsys):
    """REPRO (R-9): `--filter-status open --json` must not surface retired risks
    in the list downstream consumers read.

    Bug: in `main()` JSON mode, `out = result.to_dict()` emits the FULL
    unfiltered risk list under `out["risks"]`; the status/band/top filter is
    only applied to `out["view"]`. /pulse and /slice (and the RR-1 usage
    documented in their SKILL.md) consume `d["risks"]`, so retired risks
    leak into the "open" view used for slice-candidate ranking.

    Expected: with `--filter-status open`, the risk list a consumer reads
    contains zero `retired`-status risks.
    Actual (pre-fix): `out["risks"]` includes R3 (Status: retired) from
    clean_register.md because the filter never touches `out["risks"]`.

    Reproduces the live observation: `--filter-status open` against the real
    architecture/risk-register.md returned retired R-5/R-7 in JSON output.

    Fix slice: slice-036-fix-rr1-audit-status-filter.
    Rule reference: R-9 / RR-1.
    """
    rc = main([
        str(FIXTURES / "clean_register.md"),
        "--json",
        "--filter-status", "open",
    ])
    assert rc == 0, f"clean register should have no violations, rc={rc}"

    out = json.loads(capsys.readouterr().out)
    consumed = out["risks"]
    leaked = sorted(
        r["risk_id"] for r in consumed if r["status"] != "open"
    )
    assert leaked == [], (
        "JSON consumers read out['risks'] for the --filter-status open view; "
        f"non-open risks leaked: {leaked} "
        "(clean_register.md R3 is Status: retired)"
    )


# --- Slice-036 / R-9: --json consumed `risks` key honours filter/sort/top ---

def _json_risks(capsys, *argv):
    """Invoke main() and return (rc, parsed_out, risk_ids)."""
    rc = main(list(argv))
    out = json.loads(capsys.readouterr().out)
    return rc, out, [r["risk_id"] for r in out["risks"]]


def test_json_filter_band_and_top_applied_to_consumed_risks_fixture(capsys):
    """AC2 (R-9 / ADR-036): --json `risks` reflects --filter-band and --top.

    Stable fixture oracle (clean_register.md, scores verified via
    _band_for_score): R1 open high×high=9 (high band), R2 mitigating
    med×med=4 (medium), R3 retired low×high=3 (MEDIUM, not high), R4 open
    low×low=1 (low). --filter-band high -> {R1} only; --top 2 --sort score
    -> [R1, R2] (9, 4 desc). Pre-fix out["risks"] was unfiltered (all 4).
    Rule reference: R-9 / RR-1.
    """
    fx = str(FIXTURES / "clean_register.md")

    rc, out, ids = _json_risks(capsys, fx, "--json", "--filter-band", "high")
    assert rc == 0
    assert "view" not in out, "redundant `view` key must be removed (ADR-036)"
    assert ids == ["R1"], f"--filter-band high should yield only R1, got {ids}"

    rc, out, ids = _json_risks(capsys, fx, "--json", "--top", "2", "--sort", "score")
    assert rc == 0
    assert ids == ["R1", "R2"], f"--top 2 --sort score should be [R1,R2], got {ids}"


def test_json_filter_status_open_excludes_non_open_real_register_invariant(capsys):
    """AC2 (R-9): against the real register, --filter-status open yields
    ONLY open risks in the consumed list.

    Scoped to the INVARIANT only (zero non-open) — never a count/ordering
    that mutates as risks are added/retired (slice-004 real-file scoping
    discipline). Pre-fix R-5/R-7 (retired) leaked here.
    Rule reference: R-9 / RR-1.
    """
    real = str(REPO_ROOT / "architecture" / "risk-register.md")
    rc, out, _ = _json_risks(capsys, real, "--json", "--filter-status", "open")
    assert rc == 0, f"real register should have no violations, rc={rc}"
    leaked = sorted(
        r["risk_id"] for r in out["risks"] if r["status"] != "open"
    )
    assert leaked == [], f"non-open risks leaked into consumed list: {leaked}"
    assert "view" not in out


def test_json_consumed_risks_contract_pinned_against_unfiltered_regression(capsys):
    """AC4 (R-9 / ADR-036): a filter MUST strictly reduce the consumed
    `risks` list vs the unfiltered invocation — guards silent
    re-introduction of an unfiltered consumed key.
    Rule reference: R-9 / RR-1.
    """
    fx = str(FIXTURES / "clean_register.md")

    _, out_all, ids_all = _json_risks(capsys, fx, "--json")
    assert set(ids_all) == {"R1", "R2", "R3", "R4"}, ids_all

    _, out_open, ids_open = _json_risks(capsys, fx, "--json", "--filter-status", "open")
    assert set(ids_open) < set(ids_all), (
        "filtered consumed list must be a strict subset of unfiltered "
        f"(got filtered={ids_open}, all={ids_all}) — R-9 regression"
    )
    assert {"R3"}.isdisjoint(ids_open), "retired R3 must not be in --filter-status open"
    assert "view" not in out_all and "view" not in out_open


def test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id(capsys):
    """AC4 (per Critic M1): with NO filter flags, --json `risks` is
    (-score, risk_id) ordered — pins the ADR-036-documented
    register-order -> score-desc behaviour change so it cannot silently
    revert. Fixture order: R1(9), R2(4), R3(3), R4(1).
    Rule reference: R-9 / RR-1.
    """
    _, out, ids = _json_risks(capsys, str(FIXTURES / "clean_register.md"), "--json")
    expected = [
        r["risk_id"]
        for r in sorted(out["risks"], key=lambda r: (-r["score"], r["risk_id"]))
    ]
    assert ids == expected, f"no-flag consumed order not score-desc-then-id: {ids}"
    assert ids == ["R1", "R2", "R3", "R4"], ids


def test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose():
    """AC4 (per meta-Critic M-add-1): the durable prose-pin.

    The pre-existing test_pulse_skill_references_rr_1 /
    test_slice_skill_references_rr_1 assert only the bare
    "RR-1"/"risk_register_audit" substrings — they do NOT pin the
    --filter-status flag or the exclusion/sorted prose this slice's
    "code-conformance-to-doc" thesis depends on. Pin it here so a future
    SKILL.md edit cannot silently un-spec the code.
    Rule reference: R-9 / RR-1.
    """
    slice_md = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    pulse_md = (REPO_ROOT / "skills" / "pulse" / "SKILL.md").read_text(encoding="utf-8")

    assert "--filter-status open" in slice_md, (
        "/slice SKILL.md must document --filter-status open (RR-1 consumed contract)"
    )
    assert "Retired / accepted risks are excluded automatically" in slice_md, (
        "/slice SKILL.md must document the exclusion prose the fix conforms to"
    )
    assert "--filter-status open" in pulse_md, (
        "/pulse SKILL.md must document --filter-status open (RR-1 consumed contract)"
    )
    assert "scored, sorted" in pulse_md, (
        "/pulse SKILL.md must document the scored, sorted output prose"
    )


def test_filter_band_high_returns_only_high():
    """filter_band='high' returns only high-band risks.

    Defect class: A "show me the top concerns" view that includes mediums
    is noise.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, filter_band="high")
    bands = {r.band for r in view}
    assert bands == {"high"}


def test_sort_by_score_desc_then_id():
    """Sort by score (desc), then risk_id (asc) for ties.

    Defect class: Inconsistent sort order means /pulse and /slice show
    different "top risks" run-to-run, undermining trust in the ranking.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, sort_by="score")
    scores = [r.score for r in view]
    assert scores == sorted(scores, reverse=True), (
        f"expected score desc; got {scores}"
    )
    # First should be R1 (score 9)
    assert view[0].risk_id == "R1"


def test_top_n_limits_output():
    """top=2 returns only the 2 highest-scored risks.

    Defect class: /pulse surfacing all risks instead of top-N is noise.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    view = filter_and_sort(result, sort_by="score", top=2)
    assert len(view) == 2


def test_summary_counts_by_band_and_status():
    """to_dict() summary aggregates band / status counts correctly.

    Defect class: Wrong aggregates would mislead /pulse into reporting
    e.g. "5 high open" when only 1 is actually high+open.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "clean_register.md")
    summary = result.to_dict()["summary"]
    assert summary["total"] == 4
    assert summary["by_band"]["high"] == 1
    assert summary["by_band"]["medium"] == 2
    assert summary["by_band"]["low"] == 1
    assert summary["by_status"]["open"] == 2
    assert summary["by_status"]["mitigating"] == 1
    assert summary["by_status"]["retired"] == 1
    assert summary["open_high_count"] == 1


def test_all_retired_register_has_zero_open_high():
    """If everything is retired/accepted, open_high_count is 0.

    Defect class: A register with no active concerns shouldn't surface
    fake "top risks" — /pulse would mislead the user.
    Rule reference: RR-1.
    """
    result = audit_register(FIXTURES / "all_retired.md")
    summary = result.to_dict()["summary"]
    assert summary["open_high_count"] == 0
    assert summary["by_status"]["open"] == 0


# --- Skill prose pins ---

def test_triage_skill_references_rr_1():
    """skills/triage/SKILL.md must reference RR-1 + the new H2 format.

    Defect class: Without /triage emitting the new format, RR-1 is
    inert; legacy table rows accumulate and the audit yields no risks.
    Rule reference: RR-1.
    """
    text = (REPO_ROOT / "skills" / "triage" / "SKILL.md").read_text(encoding="utf-8")
    assert "RR-1" in text, "no RR-1 reference in /triage SKILL.md"
    assert "Likelihood" in text and "Impact" in text, (
        "Likelihood / Impact fields not documented in /triage"
    )


def test_slice_skill_references_rr_1():
    """skills/slice/SKILL.md must reference RR-1 + the audit module.

    Defect class: /slice candidate-gathering not consuming scored risks
    means risk-first ordering reverts to ad-hoc keyword scanning.
    Rule reference: RR-1.
    """
    text = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "RR-1" in text, "no RR-1 reference in /slice SKILL.md"
    assert "risk_register_audit" in text, (
        "no risk_register_audit module reference in /slice"
    )


def test_pulse_skill_references_rr_1():
    """skills/pulse/SKILL.md must reference RR-1.

    Defect class: /pulse not surfacing scored top-N undermines the daily
    risk-awareness signal RR-1 is meant to provide.
    Rule reference: RR-1. Skill renamed `/status`→`/pulse` at slice-035 (SRCD-1).
    """
    text = (REPO_ROOT / "skills" / "pulse" / "SKILL.md").read_text(encoding="utf-8")
    assert "RR-1" in text, "no RR-1 reference in /pulse SKILL.md"
    assert "risk_register_audit" in text, (
        "no risk_register_audit module reference in /pulse"
    )


# --- Slice-004: docstring/comment/risk-register.md prose-vs-regex consistency ---

def test_docstring_format_examples_match_actual_regex():
    """Module docstring's 'Format' section heading example matches _RISK_HEADING_RE.

    Defect class: slice-002 hit silent 0-risks because the docstring
    showed `## R-NN -- <title>` (double-dash; ALSO `R-NN` letters not
    digits) but the regex required `R-?\\d+` AND single-character
    separator. This test guards against future drift in either
    direction.

    Coverage gap intentionally accepted: the negative counterexample
    `## R-1 -- <title>` lives INSIDE backticks within continuous
    paragraph prose — never as a line's leading non-whitespace token —
    so it's not picked up by `startswith("## R-")` after `.strip()`.
    If a future maintainer reformats the prose such that a backticked
    counterexample begins a stripped line, this test would extract it
    and fail loudly (regex correctly rejects `--` two-character form).
    Failing-loudly on counterexample-leakage is acceptable test
    behavior.

    Slice-004 AC #1.
    Rule reference: RR-1.
    """
    import inspect
    import tools.risk_register_audit as audit_module

    docstring = inspect.getdoc(audit_module) or ""
    candidates = [
        line.strip()
        for line in docstring.splitlines()
        if line.strip().startswith("## R-")
    ]
    assert candidates, "no `## R-...` heading example found in docstring"
    for heading in candidates:
        assert _RISK_HEADING_RE.match(heading), (
            f"docstring example heading {heading!r} does NOT match "
            f"_RISK_HEADING_RE — docstring/regex contradiction (the "
            f"slice-002 silent-zero-risks bug). Common causes: letter "
            f"placeholder like `R-NN` (regex requires R-?\\d+); "
            f"double-hyphen `--` (regex character class is single-char)."
        )


def test_inline_regex_comment_examples_match_actual_regex():
    """Inline comment above _RISK_HEADING_RE shows only formats the regex actually accepts.

    Coverage: extracts BOTH "..."-quoted (Python string literal
    convention) AND `...`-quoted (markdown code-span convention)
    heading shapes from the immediately-adjacent `#`-prefixed comment
    block above the regex.

    Known coverage gap (Critic M3): unquoted prose examples like
    `# Also accepts ## R-1 — title` (no quotes) silently bypass this
    test. If a future maintainer adds an unquoted example, the test
    won't catch a `--`-vs-em-dash mismatch in that example. Acceptable
    trade-off: tightening to also catch unquoted shapes risks false
    positives on comment lines that happen to mention `## R-` in
    non-example contexts. Address in a follow-on slice if drift recurs.

    Slice-004 AC #2.
    Rule reference: RR-1.
    """
    import re as re_module

    src = (
        REPO_ROOT / "tools" / "risk_register_audit.py"
    ).read_text(encoding="utf-8")

    # Find the line containing `_RISK_HEADING_RE = re.compile(`.
    lines = src.splitlines()
    target_idx = None
    for i, line in enumerate(lines):
        if "_RISK_HEADING_RE = re.compile(" in line:
            target_idx = i
            break
    assert target_idx is not None, "_RISK_HEADING_RE assignment line not found"

    # Walk backwards over consecutive `#` comment lines to gather the
    # inline doc block. NOTE: stops at the first non-`#`-prefixed line.
    # Multi-block comments separated by blank line have only the
    # immediate block scanned. Intentional scoping — the test inspects
    # what's adjacent to the regex.
    comment_lines = []
    j = target_idx - 1
    while j >= 0 and lines[j].lstrip().startswith("#"):
        comment_lines.insert(0, lines[j])
        j -= 1
    assert comment_lines, "no inline comment found above _RISK_HEADING_RE"

    comment_blob = "\n".join(comment_lines)
    # Extract every `## R-...`-shaped example, whether double-quoted or
    # backtick-quoted. Per Critic M3: backtick-quoted is markdown
    # convention; covering both shapes catches more realistic drift.
    quoted_examples = re_module.findall(r'[`"](## R-[^`"]+)[`"]', comment_blob)
    assert quoted_examples, (
        f"no `## R-...` quoted example found in inline comment block:\n"
        f"{comment_blob!r}"
    )
    for heading in quoted_examples:
        assert _RISK_HEADING_RE.match(heading), (
            f"inline-comment example heading {heading!r} does NOT match "
            f"_RISK_HEADING_RE — inline-comment/regex contradiction."
        )


def test_risk_register_md_schema_description_examples_match_actual_regex():
    """architecture/risk-register.md prelude prose's heading shape examples match _RISK_HEADING_RE.

    Defect class (Critic M2): the user-facing risk-register.md file's
    OPENING DESCRIPTION PROSE — the prelude before the first `## R-`
    heading — is the third documentation surface (after the audit's
    docstring + inline comment). Today (pre-slice-004) it shows
    `## R-N -- <title>` (double-dash; ALSO `R-N` is a single letter,
    not `\\d+`). A user reading this file follows the example, types
    the same shape into a new entry, runs the audit, gets silent
    0-risks. This test enforces the prelude prose stays consistent
    with the audit's behavior.

    Coverage: scans LINES BEFORE the first `## R-` heading (the
    prelude); extracts backtick-quoted `## R-...` shapes; runs each
    through _RISK_HEADING_RE.match; asserts each matches.

    Slice-004 AC #3.
    Rule reference: RR-1.
    """
    import re as re_module

    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    text = register_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # The prelude is everything before the first H2 risk heading.
    prelude_end = None
    for i, line in enumerate(lines):
        if line.startswith("## R-") or line.startswith("## R"):
            prelude_end = i
            break
    assert prelude_end is not None, (
        "no `## R-...` heading found in risk-register.md"
    )
    prelude = "\n".join(lines[:prelude_end])

    # Extract every backtick-quoted `## R-...` shape.
    quoted_examples = re_module.findall(r"`(## R-[^`]+)`", prelude)
    assert quoted_examples, (
        f"no backtick-quoted `## R-...` example found in risk-register.md "
        f"prelude:\n{prelude!r}"
    )
    for heading in quoted_examples:
        assert _RISK_HEADING_RE.match(heading), (
            f"risk-register.md prelude example {heading!r} does NOT match "
            f"_RISK_HEADING_RE — user-facing schema documentation "
            f"contradicts the audit's actual behavior."
        )
