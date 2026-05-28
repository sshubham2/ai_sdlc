"""Structural-pin tests for the R-20 cp -r codification in skills/build-slice/SKILL.md
`## Prerequisite check ### Branch state` numbered point 1.

Per slice-074 design.md §"Test contracts (the structural-pin shape)" — operationalizes
R-20 candidate fix (a). The 3 tests cover AC#1 + AC#2:

  - test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd
    (AC#1: 2 if-then-fi guarded cp -r lines, positioned AFTER cd line and BEFORE point 2)
  - test_cp_r_lines_reference_r_20_in_comment
    (AC#1: R-20 reference comment anchors codification origin)
  - test_cp_r_lines_use_if_then_guard_for_source_dir_absence
    (AC#2: each cp -r wrapped in single-line `if [ -d ... ]; then ... ; fi` set-e-safe guard)

Per /critique pass-1 M3 + m3 ACCEPTED-FIXED: regex anchors to the `if [ -d ... ]; then cp -r`
guard prefix (cross-pins AC#1 + AC#2; forecloses comment-substring leak per APED-1 evidence).

Per /critique-review pass-1 m-add-1 ACCEPTED-FIXED: single-line `if [ -d ... ]; then ... ; fi`
form is intentionally pinned (RSAD-1 byte-exact-match discipline).
"""
from __future__ import annotations

import re
from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"


def _branch_state_section() -> str:
    """Extract '### Branch state' sub-section text up to the next markdown H2 heading.

    Per /critique pass-1 M2 ACCEPTED-FIXED: the lookahead requires `## ` followed by a
    CAPITAL LETTER (markdown H2-headings convention; shell `## `-prefixed comments
    inside bash codefences are typically lowercase or arbitrary, so capital-letter
    anchor disambiguates section-end from in-fence comments). Do NOT relax to
    bare `(?=^## )` — that misfires on `## `-prefixed shell comments and silently
    truncates the section, masking real prose changes.
    """
    text = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^### Branch state\b.*?(?=^## [A-Z])", text, re.MULTILINE | re.DOTALL)
    assert m is not None, "### Branch state sub-section not found"
    return m.group(0)


def test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd():
    """AC#1: cp -r lines for both dirs present, positioned AFTER the cd line and BEFORE
    numbered point 2.

    Per /critique pass-1 M3 ACCEPTED-FIXED: the regex requires the
    `if [ -d ... ]; then cp -r` guard prefix (NOT bare `cp -r [^\\n]*<dir>`) to
    forestall comment-substring leaks (a comment mentioning `cp -r diagnose-out` would
    otherwise satisfy the assertion even if the actual functional line were deleted).
    This cross-pins AC#1 + AC#2 in a single regex shape.
    """
    section = _branch_state_section()
    cd_marker = 'cd "$wt_base/slice-NNN-<slice-name>"'
    point2_marker = "2. **If the worktree already exists**"
    cd_idx = section.find(cd_marker)
    point2_idx = section.find(point2_marker)
    assert cd_idx != -1, f"expected cd line {cd_marker!r} missing"
    assert point2_idx != -1, f"expected numbered point 2 marker {point2_marker!r} missing"
    diagnose_pattern = re.compile(
        r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*diagnose-out', re.MULTILINE
    )
    graphify_pattern = re.compile(
        r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*graphify-out', re.MULTILINE
    )
    diagnose_match = diagnose_pattern.search(section)
    graphify_match = graphify_pattern.search(section)
    assert diagnose_match is not None, (
        "diagnose-out cp -r line missing (or not guarded by "
        "`if [ -d ...]; then cp -r` prefix per /critique pass-1 M3)"
    )
    assert graphify_match is not None, (
        "graphify-out cp -r line missing (or not guarded by "
        "`if [ -d ...]; then cp -r` prefix per /critique pass-1 M3)"
    )
    assert cd_idx < diagnose_match.start() < point2_idx, (
        "diagnose-out cp -r not positioned between cd and point 2"
    )
    assert cd_idx < graphify_match.start() < point2_idx, (
        "graphify-out cp -r not positioned between cd and point 2"
    )


def test_cp_r_lines_reference_r_20_in_comment():
    """AC#1: a comment referencing R-20 is co-located with the cp -r lines
    (anchors codification origin)."""
    section = _branch_state_section()
    r20_match = re.search(r"#[^\n]*R-20", section)
    assert r20_match is not None, "no R-20 reference comment found in ### Branch state"


def test_cp_r_lines_use_if_then_guard_for_source_dir_absence():
    """AC#2: each cp -r line wrapped in `if [ -d ... ]; then ... fi` POSIX guard (set-e-safe).

    Per /critique pass-1 m3 ACCEPTED-FIXED: switched from `[ -d ... ] && cp -r` chained
    form to `if [ -d ... ]; then cp -r ...; fi` because the chained form returns
    exit-status 1 on guard-skip (would fail loudly under future `set -e` hardening of
    the codefence). The `if/then/fi` form returns 0 when the test is false (no body
    runs), which is the intended graceful-absence semantic.

    Per /critique-review pass-1 m-add-1 ACCEPTED-FIXED: **single-line
    `if [ -d ... ]; then ... ; fi` form is intentionally pinned** (semicolons +
    same-line constraint via `[^\\n]*`). Multi-line POSIX equivalents — e.g.,
    `if [ -d "$X" ]\\nthen\\n    cp -r "$X" ./\\nfi` (no `;` before `then`/`fi`, four
    lines) — are out-of-scope and will FAIL this test. This is by-design per RSAD-1
    byte-exact-match discipline (slice-071 M6 prevention pattern): the structural-pin
    asserts the prose's wire-format shape, not its POSIX semantic equivalence class.
    Future Builders refactoring the codefence for "readability" MUST preserve the
    single-line form or update both the prose AND the test in the same fix block.
    """
    section = _branch_state_section()
    guard_pattern = re.compile(
        r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*;\s*fi', re.MULTILINE
    )
    matches = guard_pattern.findall(section)
    assert len(matches) >= 2, (
        f"expected >=2 `if [ -d ... ]; then cp -r ...; fi` guarded lines, found {len(matches)}"
    )
