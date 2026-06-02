"""Structural-pin tests for the R-20 derived-dir seed in skills/build-slice/SKILL.md
`## Prerequisite check ### Branch state`.

BRANCH-3 (slice-099): the R-20 seed is now split across the reordered numbered points —
the PRIMARY create path (point 2) seeds via the shared `seed_derived_dirs` helper; the
LEGACY dirty-dance (point 4) retains its 2 inline guarded `cp -r` lines. Pre-slice-099
the seed was 2 inline `cp -r` lines in the point-1 create case + 2 in point 4 (== 4).

Per slice-074 design.md §"Test contracts (the structural-pin shape)" — operationalizes
R-20 candidate fix (a). The 3 tests cover AC#1 + AC#2:

  - test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd
    (R-20 seed: point 2 via seed_derived_dirs + legacy point 4 retains 2 guarded cp -r)
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

from tests.methodology._skill_parse_helpers import _branch_state_section

SKILL_PATH = Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"


def test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd():
    """R-20 seed coverage under BRANCH-3 (slice-099): the PRIMARY create path (point 2)
    seeds the gitignored derived dirs via the shared `seed_derived_dirs` helper (single
    source of truth — AC5); the LEGACY dirty-dance (point 4) retains its 2 inline guarded
    `cp -r` lines (m2 self-containment carve-out). Both diagnose-out + graphify-out covered.

    Pre-slice-099: point 1 (create) carried 2 inline `cp -r` lines. slice-099 moved the
    primary-path seed to `seed_derived_dirs` so `/slice` Step 5.5 + `/build-slice` share
    ONE seed mechanism (closes the slice-093 L47 / slice-088 L71 silent-seed-drop gap);
    `cp -r` survives only in the legacy point-4 escape-hatch.

    Per /critique pass-1 M3 ACCEPTED-FIXED: the legacy regex still requires the
    `if [ -d ... ]; then cp -r` guard prefix (NOT bare `cp -r [^\\n]*<dir>`) to forestall
    comment-substring leaks.
    """
    section = _branch_state_section(SKILL_PATH.read_text(encoding="utf-8"))
    # Primary create path (point 2) seeds via the shared helper:
    assert "seed_derived_dirs" in section, (
        "BRANCH-3 regression: the primary create path (point 2) must seed R-20 derived "
        "dirs via tools._worktree_paths.seed_derived_dirs (the shared helper), not inline cp -r"
    )
    # Legacy point-4 dirty-dance retains its 2 guarded cp -r lines (diagnose-out + graphify-out):
    diagnose_pattern = re.compile(
        r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*diagnose-out', re.MULTILINE
    )
    graphify_pattern = re.compile(
        r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*graphify-out', re.MULTILINE
    )
    assert diagnose_pattern.search(section) is not None, (
        "legacy point-4 diagnose-out cp -r seed missing (or not guarded by "
        "`if [ -d ...]; then cp -r` prefix per /critique pass-1 M3)"
    )
    assert graphify_pattern.search(section) is not None, (
        "legacy point-4 graphify-out cp -r seed missing (or not guarded by "
        "`if [ -d ...]; then cp -r` prefix per /critique pass-1 M3)"
    )


def test_cp_r_lines_reference_r_20_in_comment():
    """AC#1: a comment referencing R-20 is co-located with the cp -r lines
    (anchors codification origin)."""
    section = _branch_state_section(SKILL_PATH.read_text(encoding="utf-8"))
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
    section = _branch_state_section(SKILL_PATH.read_text(encoding="utf-8"))
    guard_pattern = re.compile(
        r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*;\s*fi', re.MULTILINE
    )
    matches = guard_pattern.findall(section)
    # Fix C (slice-074 m2): tightened `>= 2` -> exact count to trip any drift in the
    # intentional duplication count (the prior `>= 2` tolerance silently accepted a 5th
    # accidental copy-paste line).
    # BRANCH-3 (slice-099): exact count lowered `== 4` -> `== 2`. Pre-slice-099 there were
    # 4 guarded cp -r lines (2 in the point-1 create case + 2 in the point-4 dirty-tree
    # case). slice-099 moved the PRIMARY create-path seed to the shared `seed_derived_dirs`
    # helper (point 2), leaving inline `cp -r` ONLY in the legacy point-4 escape-hatch
    # (2 lines: diagnose-out + graphify-out). The `== 2` invariant still trips any drift.
    assert len(matches) == 2, (
        f"expected exactly 2 `if [ -d ... ]; then cp -r ...; fi` guarded lines "
        f"(BRANCH-3 / slice-099: only legacy point 4 retains inline cp -r; point 2's "
        f"primary create path seeds via seed_derived_dirs), found {len(matches)}"
    )
