"""Structural-pin tests for the switch-commit-switch-worktree codification in
skills/build-slice/SKILL.md `## Prerequisite check ### Branch state` numbered point 4.

Per slice-074 expansion scope (AC#5+AC#6 + m2 sub-claim) — codifies the N=5 cumulative
empirical pattern (slice-070/071/072/073/074) for resolving dirty pre-build state on
default branch. Replaces the current "STOP, ask user to commit or stash. NO auto-stash"
prose with the canonical 4-step recipe.

3 tests:

  - test_point_4_contains_switch_commit_switch_worktree_sequence_in_order
    (AC#5: 4 ordered tokens inside the bash codefence body of point 4)
  - test_both_worktree_create_forms_documented_dash_b_and_no_dash_b
    (AC#6: point 1 has -b form; point 4 has no-`-b` positional form)
  - test_point_4_codefence_does_not_contain_git_stash
    (AC#5 sub-claim per /critique-review pass-2 m2 ACCEPTED-FIXED: NO-auto-stash
    discipline structurally pinned, not just prose-only declared)

Per /critique pass-2 M1 + M2 ACCEPTED-FIXED (shared mechanism): the helper
`_point_4_codefence_body` extracts ONLY the bash codefence body, foreclosing both
(a) prose-only narrative false-pass + (b) future point-5 / WORKTREE=skip pollution.

Per /critique pass-2 B1 ACCEPTED-FIXED: AC#6 no-`-b` negative lookahead scoped before
`#` comment delimiter so the canonical `# no -b; branch exists` comment does not
falsify the assertion.
"""
from __future__ import annotations

import re
from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"


def _branch_state_section() -> str:
    """Extract '### Branch state' sub-section text up to the next markdown H2 heading.

    Identical extraction to test_build_slice_skill_cp_r_step.py (per /critique pass-1
    M2 ACCEPTED-FIXED — single-line constraint pinned via (?=^## [A-Z])).
    """
    text = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^### Branch state\b.*?(?=^## [A-Z])", text, re.MULTILINE | re.DOTALL)
    assert m is not None, "### Branch state sub-section not found"
    return m.group(0)


def _point_4_codefence_body(section: str) -> str:
    """Extract the bash codefence BODY within numbered point 4 ('If working tree is dirty').

    Per /critique pass-2 M1 + M2 ACCEPTED-FIXED (shared mechanism): the upper boundary
    is the codefence close (```) rather than end-of-section. This (a) forecloses M2's
    "future point-5 / WORKTREE=skip paragraph pollutes AC#5 token search" failure mode
    AND (b) forecloses M1's "prose-only narrative without codefence passes AC#5" failure
    mode in a single regex change. The structural-pin asserts the codified contract
    EXISTS as an executable bash codefence (not as a prose paragraph that narrates the
    same tokens). Returns the codefence body (between the opening ```bash and closing
    ```), NOT including the fences themselves.
    """
    m = re.search(
        r"^4\. \*\*If working tree is dirty\b.*?```bash\b(.*?)```",
        section,
        re.MULTILINE | re.DOTALL,
    )
    assert m is not None, (
        "point 4 'If working tree is dirty' does NOT contain a ```bash ...``` codefence "
        "- the switch-commit-switch codification requires the recipe to live in an "
        "executable bash codefence, not as prose narrative (per /critique pass-2 M1 "
        "ACCEPTED-FIXED)"
    )
    return m.group(1)


def test_point_4_contains_switch_commit_switch_worktree_sequence_in_order():
    """AC#5: point 4's bash codefence contains the canonical 4-step switch-commit-switch
    sequence in order, plus the scaffold-commit body shape.

    Per slice-074 design.md SwitchCommitSwitch codification: the 5 ordered anchor tokens
    that MUST appear in point 4's bash codefence in canonical order:
        1. `git switch -c slice/` (creates slice branch carrying dirty state)
        2. `git commit -m "scaffold(slice-NNN):` (scaffolding-commit body shape; added
           per /critique pass-2 M1 as the 5th anchor to discriminate narrative-only
           mentions from the codified recipe)
        3. `git switch "$default"` (back to clean default)
        4. `git worktree add` (creates worktree pointing at the already-existing branch)

    Per /critique pass-2 M1 + M2 ACCEPTED-FIXED (shared mechanism): the search scope is
    the bash CODEFENCE BODY (via `_point_4_codefence_body`), NOT the entire point-4
    block. A future Builder who reverts point 4 to STOP-prose while narrating the
    sequence as a paragraph would FAIL this test - the codefence-existence assertion
    fires in `_point_4_codefence_body` before token search runs.

    Per RSAD-1 byte-exact-match discipline (slice-071 M6 prevention pattern): asserts
    LITERAL token presence in ORDER, not POSIX-semantic equivalence. Multi-line
    equivalent forms (e.g., `git switch $default && git worktree add` chained) would
    FAIL.
    """
    codefence = _point_4_codefence_body(_branch_state_section())
    token_1 = codefence.find("git switch -c slice/")
    token_2 = (
        codefence.find('git commit -m "scaffold(slice-NNN):', token_1 + 1)
        if token_1 != -1
        else -1
    )
    token_3 = (
        codefence.find('git switch "$default"', token_2 + 1) if token_2 != -1 else -1
    )
    token_4 = codefence.find("git worktree add", token_3 + 1) if token_3 != -1 else -1
    assert token_1 != -1, "token 1 (`git switch -c slice/`) missing from point-4 codefence"
    assert token_2 != -1, (
        'token 2 (`git commit -m "scaffold(slice-NNN):`) missing or out-of-order '
        "in point-4 codefence"
    )
    assert token_3 != -1, (
        'token 3 (`git switch "$default"`) missing or out-of-order in point-4 codefence'
    )
    assert token_4 != -1, (
        "token 4 (`git worktree add`) missing or out-of-order in point-4 codefence"
    )
    assert token_1 < token_2 < token_3 < token_4, (
        f"4 ordered tokens present but out of canonical order: "
        f"got positions [{token_1}, {token_2}, {token_3}, {token_4}]"
    )


def test_both_worktree_create_forms_documented_dash_b_and_no_dash_b():
    """AC#6: both worktree-create forms documented - -b form at point 1, no-b form at
    point 4.

    Per slice-074 design.md SwitchCommitSwitch codification: a reader following the
    point-4 sequence MUST NOT include `-b` (which would cause `fatal: A branch named
    'slice/NNN-...' already exists`). The two forms must coexist:
        - Point 1 (new-branch case): `git worktree add ... -b slice/NNN-<slice-name> "$default"`
        - Point 4 (existing-branch case): `git worktree add ... slice/NNN-<slice-name>` (no -b)

    Per /critique pass-2 B1 ACCEPTED-FIXED: the no-`-b` negative lookahead is scoped
    BEFORE the `#` comment delimiter (`[^#\\n]` not `[^\\n]`) so the canonical line's
    trailing explanatory comment `# no -b; branch exists` does NOT falsify the assertion
    via embedded `-b` literal. The `-b\\s` (flag + trailing whitespace) shape is required
    in the negative lookahead so the comment's `-b;` (no trailing space; semicolon
    follows) is unambiguously excluded.
    """
    section = _branch_state_section()
    # Point 1's -b form: explicit -b flag before slice/NNN-<slice-name> branch arg + $default
    point_1_dash_b_pattern = re.compile(
        r'git worktree add[^\n]+-b slice/NNN-<slice-name>[^\n]+\$default', re.MULTILINE
    )
    point_1_match = point_1_dash_b_pattern.search(section)
    assert point_1_match is not None, (
        "point 1's `-b` form `git worktree add ... -b slice/NNN-<slice-name> ... $default` "
        "missing from ### Branch state"
    )
    # Point 4's no-b form: extract from CODEFENCE BODY (per M2 fix) + comment-aware
    # negative lookahead scoped before `#` comment delimiter (per B1 fix) + `-b\s`
    # flag shape required.
    codefence = _point_4_codefence_body(section)
    point_4_no_dash_b_pattern = re.compile(
        r'git worktree add\s+(?!(?:[^#\n]*?)-b\s)[^#\n]*slice/NNN-<slice-name>',
        re.MULTILINE,
    )
    point_4_match = point_4_no_dash_b_pattern.search(codefence)
    assert point_4_match is not None, (
        "point 4's no-`-b` form `git worktree add <path> slice/NNN-<slice-name>` "
        "(without -b flag) missing from numbered point 4's codefence body"
    )


def test_point_4_codefence_does_not_contain_git_stash():
    """AC#5 sub-claim (per /critique-review pass-2 m2 ACCEPTED-FIXED): point 4's
    codefence body does NOT contain `git stash` - structurally pins the NO-auto-stash
    discipline that mission-brief.md L75 + this slice's out-of-scope section declare
    in prose.

    Per slice-022 codify-empirical-discipline axis: if a discipline is load-bearing
    enough to declare in out-of-scope, it should be load-bearing enough to pin
    structurally. AC#1's M3 ACCEPTED-FIXED guard-prefix anchor is the precedent
    (discipline-as-regex-anchor rather than prose-only declaration).

    A future Builder who "improves" the switch-commit-switch recipe by inserting
    `git stash` between `git switch -c` and `git commit` would FAIL this test -
    surfacing the silent discipline regression at /validate-slice mid-slice smoke gate.
    """
    codefence = _point_4_codefence_body(_branch_state_section())
    assert "git stash" not in codefence, (
        "point 4's codefence contains `git stash` - but mission-brief.md L75 declares "
        "NO-auto-stash as out-of-scope; the switch-commit-switch sequence MUST require "
        "explicit `git add` + `git commit` of scaffolding, never silent shelve via stash. "
        "Per /critique-review pass-2 m2 ACCEPTED-FIXED, this structural pin elevates the "
        "prose discipline declaration to a regex-anchor."
    )
