"""Pins the /code-review skill SKILL.md (CRSI-1; slice-060).

Asserts:
- `## Pipeline position` block is present with the canonical chain edge
  (predecessor /build-slice, successor /validate-slice, auto-advance true).
- The walking-skeleton self-dogfood produced `code-review.md` on slice-060.

Rule reference: CRSI-1 (methodology-changelog.md v0.64.0; slice-060; ADR-059).

Slice-062 / ADR-060 repoint (R-15 corpus class-closure backstop scope-
extension): the slice-060 `code-review.md` path is now resolved lazily
INSIDE the test function via ``_resolve_slice_dir(60)`` from
``tests.methodology.conftest`` (the slice-056 helper) — NOT a
module-level binding. Lazy resolution avoids the import-time
AssertionError class that would error the entire module's collection
if slice-060's archive folder were absent; the in-test-function
surface localizes the failure per ``_resolve_slice_dir``'s documented
contract (slice-056 ``test_raises_assertion_with_diagnostic_when_neither_found``).
Pre-repoint: module-level ``_SLICE_060_CODE_REVIEW`` literal carried
the active-path string ``"slice-060-add-code-review-skill"`` which
broke at slice-060 archival (slice-061 user-approved deferral). The
slice-061 N=1 scope-gap also motivated extending the R-15 corpus
class-closure backstop scope to ``tests/skills/**`` + ``tests/agents/**``
(slice-062 ADR-060 §"Decision"); this file's pre-slice-062 literal was
the lone wider-scope offender repointed at this slice.
"""
from __future__ import annotations

from pathlib import Path

from tests.methodology.conftest import _resolve_slice_dir

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SKILL_MD = _REPO_ROOT / "skills" / "code-review" / "SKILL.md"


def _read(path: Path) -> str:
    assert path.exists(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def test_skill_md_pipeline_position_block_present():
    """skills/code-review/SKILL.md must carry a well-formed `## Pipeline
    position` block (PCA-1 obligation; the audit reads this for chain-shape).
    """
    body = _read(_SKILL_MD)
    assert "## Pipeline position" in body, (
        "skills/code-review/SKILL.md missing `## Pipeline position` block"
    )
    # All 5 required fields per tools/pipeline_chain_audit.py:_REQUIRED_FIELDS
    for field in ("predecessor", "successor", "auto-advance",
                  "on-clean-completion", "user-input gates"):
        assert f"**{field}**" in body, (
            f"skills/code-review/SKILL.md `## Pipeline position` missing "
            f"required field `{field}`"
        )


def test_skill_md_successor_is_validate_slice():
    """/code-review's canonical successor MUST be /validate-slice
    (walking-skeleton CRSI-1 chain edge per design.md).
    """
    body = _read(_SKILL_MD)
    # Read the `## Pipeline position` block specifically (not random body prose)
    idx = body.find("## Pipeline position")
    assert idx >= 0
    block = body[idx:]
    # Successor field on its own line
    assert "**successor**: `/validate-slice`" in block, (
        "skills/code-review/SKILL.md Pipeline-position `successor:` field "
        "must point to `/validate-slice` per the canonical CRSI-1 chain"
    )
    assert "**predecessor**: `/build-slice`" in block, (
        "skills/code-review/SKILL.md Pipeline-position `predecessor:` field "
        "must point to `/build-slice`"
    )
    assert "**auto-advance**: true" in block, (
        "skills/code-review/SKILL.md Pipeline-position `auto-advance:` must "
        "be `true` (in-loop step; no user-input HALT in v1)"
    )


def test_skill_md_step_1_diff_resolution_uses_union_of_three_sources():
    """slice-064 BFRD-1 failing-repro pin: /code-review SKILL.md Step 1
    diff resolution MUST use the union-of-three-sources read mechanism
    (working-tree-vs-base + git ls-files --others + commits-vs-base) —
    NOT a single `git diff $base...HEAD` (commit-vs-commit only).

    Bug (B1 falsifier class, N=2 cumulative across NAW-1 + /code-review):
      `git diff "$base"...HEAD` is commit-vs-commit only. At /build-slice
      Step 6 (where /code-review auto-advances from in the canonical PCA-1
      chain) slice work is uncommitted in the working tree — commits land
      at /commit-slice per PCA-1 HARD-STOP terminal contract. The
      commit-vs-commit diff returns EMPTY and Step 1's `no-code-changes`
      branch silently writes `Result: NO-CODE-CHANGES — nothing to review`
      and auto-advances. Every governed slice's /code-review run on a
      clean-tree-from-Step-6 invocation is a silent false-positive.
    Expected: Step 1 enumerates working-tree-vs-base + untracked +
      commits-vs-base (same union-of-three-sources slice-063 ADR-061
      §Decision codified for NAW-1).
    Actual (pre-fix): Step 1 contains only `git diff "$base"...HEAD`.

    The fix slice (slice-064-fix-code-review-diff-resolution-falsifier)
    mirrors NAW-1's `_resolve_added_agent_files` union pattern into
    /code-review's Step 1 bash. This test PASSES once the SKILL.md
    Step 1 prose carries all three source commands.
    """
    body = _read(_SKILL_MD)
    # Section-scope to Step 1 (avoid matching the same strings in adjacent
    # Step 2 prompt-template prose at L85).
    step_1_idx = body.find("### Step 1: Resolve the slice's code diff")
    assert step_1_idx >= 0, (
        "skills/code-review/SKILL.md missing `### Step 1: Resolve the "
        "slice's code diff` heading — Step 1 prose-pin cannot section-scope"
    )
    step_2_idx = body.find("### Step 2:", step_1_idx)
    assert step_2_idx > step_1_idx, (
        "skills/code-review/SKILL.md missing `### Step 2:` heading after "
        "Step 1 — section-scope cannot bound"
    )
    step_1 = body[step_1_idx:step_2_idx]

    # Slice-065 AC#1: scope to the ```bash-fenced block within Step 1 to
    # retire the M1 substring-leak class (the L37 preamble prose carries the
    # unflagged `git diff "$base"...HEAD` substring; a Source-(iii) assertion
    # scoped to step_1 is satisfied by the preamble alone — deleting the L51
    # bash command would still pass). Bash-block scoping + the full
    # filter-shape literal together pin the L51 bash command structurally.
    # Per /critique B1 — empirically verified: pre-fix step_1.count
    # ('git diff "$base"') = 3 (preamble + L45 + L51); bash_block.count(...)
    # = 2 (L45 + L51 only).
    bash_start = step_1.find("```bash\n")
    bash_end = step_1.find("\n```", bash_start)
    assert bash_start >= 0 and bash_end > bash_start, (
        "skills/code-review/SKILL.md Step 1 missing ```bash-fenced block — "
        "bash-block scoping cannot bound (slice-065 AC#1)"
    )
    bash_block = step_1[bash_start:bash_end]

    # Source 1 — working-tree-vs-base (captures unstaged + staged WT changes
    # against the base; the `$base` form without `...HEAD` is the canonical
    # working-tree-vs-base diff per git diff documentation). Asserted at the
    # section-scope level: preamble prose mentioning the form is acceptable.
    assert 'git diff "$base"' in step_1 and 'git diff "$base" --name-only' in step_1, (
        "skills/code-review/SKILL.md Step 1 missing working-tree-vs-base "
        "source command `git diff \"$base\" --name-only` — the B1 falsifier "
        "class requires this source to observe uncommitted WT changes at "
        "/build-slice Step 6 (the canonical /code-review auto-advance state)"
    )
    # Source 2 — untracked files (the canonical git enumeration of files
    # that exist in WT but are not yet known to git; covers /repro-authored
    # test files at /build-slice Step 6 pre-commit).
    assert "git ls-files --others --exclude-standard" in step_1, (
        "skills/code-review/SKILL.md Step 1 missing untracked-files source "
        "command `git ls-files --others --exclude-standard` — required for "
        "union-of-three-sources read mechanism (NAW-1 / ADR-061 §Decision)"
    )
    # Source 3 — commits-vs-base (covers committed slice work; the
    # pre-existing pre-slice-064 diff line, preserved as one of three sources).
    # Slice-065 AC#1 / /critique B1 tightening: scoped to bash_block AND
    # asserts the full filter-shape literal (L37 preamble carries only the
    # unflagged form without `--name-only --diff-filter=ACMR`). Double-
    # redundant: bash-block scoping alone retires the leak; the flag-tail
    # addition catches a future regression where filter flags drop from L51.
    assert 'git diff "$base"...HEAD --name-only --diff-filter=ACMR' in bash_block, (
        "skills/code-review/SKILL.md Step 1 bash block missing commits-vs-base "
        "source command `git diff \"$base\"...HEAD --name-only "
        "--diff-filter=ACMR` — required as third source in the union-of-three-"
        "sources read mechanism. Per slice-065 AC#1 / /critique B1: asserted "
        "in bash_block (not step_1) to retire the M1 substring-leak class — "
        "L37 preamble prose mentions of the unflagged `git diff \"$base\""
        "...HEAD` form are not sufficient to satisfy this assertion."
    )


def test_skill_md_step_1_all_three_legs_share_filter_shape():
    """slice-064 AC#1: pin the filter shape of the union-of-three-sources
    bash block. The two `git diff` legs (working-tree-vs-base + commits-
    vs-base) MUST share identical `--name-only --diff-filter=ACMR` flags
    AND the architecture/docs path-exclude pathspecs. The `git ls-files`
    leg takes only `--others --exclude-standard` (no `--diff-filter`).

    Section-scoped to Step 1 to avoid matching Step 2 prompt-template
    prose at L85.
    """
    body = _read(_SKILL_MD)
    step_1_idx = body.find("### Step 1: Resolve the slice's code diff")
    step_2_idx = body.find("### Step 2:", step_1_idx)
    step_1 = body[step_1_idx:step_2_idx]

    # Slice-065 AC#2: scope to ```bash-fenced block (per /critique B1 — the
    # L37 preamble carries an unflagged `git diff "$base"...HEAD` substring
    # that leaks into a step_1.count() RHS; bash_block.count() correctly
    # counts only the L45 + L51 bash leg headers).
    bash_start = step_1.find("```bash\n")
    bash_end = step_1.find("\n```", bash_start)
    assert bash_start >= 0 and bash_end > bash_start, (
        "skills/code-review/SKILL.md Step 1 missing ```bash-fenced block — "
        "bash-block scoping cannot bound (slice-065 AC#2)"
    )
    bash_block = step_1[bash_start:bash_end]

    # Slice-065 AC#2: semantic invariant scoped to bash_block (replaces
    # the pre-slice-065 `>= 2` form which admitted a 3-leg / 2-filtered
    # regression where a future leg dropped `--diff-filter=ACMR`). The
    # invariant: every `git diff "$base"` leg header in the bash block
    # MUST be matched by a `--name-only --diff-filter=ACMR` flag pair.
    # Empirically verified on current SKILL.md: 2 == 2 PASS. Pre-slice-
    # 065 `step_1.count('git diff "$base"')` = 3 (preamble leak) would
    # have produced 2 != 3 → FAIL; bash_block scoping retires that.
    diff_with_filter = bash_block.count("--name-only --diff-filter=ACMR")
    git_diff_legs = bash_block.count('git diff "$base"')
    assert diff_with_filter == git_diff_legs, (
        "skills/code-review/SKILL.md Step 1 bash block: `--name-only "
        "--diff-filter=ACMR` count must equal `git diff \"$base\"` leg count "
        "(semantic invariant — every `git diff` leg MUST carry the filter "
        f"pair). Observed: filter pairs = {diff_with_filter}, `git diff "
        f"\"$base\"` legs = {git_diff_legs}."
    )

    # All three legs carry the architecture/docs path-exclude pathspecs
    # (inline literal on each leg, NOT a bash-array; M1 critique fix).
    exclude_arch = step_1.count("':(exclude)architecture/**'")
    exclude_docs = step_1.count("':(exclude)docs/**'")
    assert exclude_arch >= 3, (
        "skills/code-review/SKILL.md Step 1 must carry the "
        "`':(exclude)architecture/**'` pathspec on ALL three union legs "
        f"(working-tree-vs-base + ls-files + commits-vs-base) — observed "
        f"{exclude_arch} occurrences, expected ≥ 3"
    )
    assert exclude_docs >= 3, (
        "skills/code-review/SKILL.md Step 1 must carry the "
        "`':(exclude)docs/**'` pathspec on ALL three union legs — "
        f"observed {exclude_docs} occurrences, expected ≥ 3"
    )

    # The `git ls-files` leg has --others --exclude-standard (the canonical
    # untracked-file enumeration flags, NOT --diff-filter).
    assert "git ls-files --others --exclude-standard" in step_1, (
        "skills/code-review/SKILL.md Step 1 `git ls-files` leg missing "
        "the canonical `--others --exclude-standard` flag pair"
    )

    # NOT a bash array (POSIX-portable; ADR-062 M1 critique fix). The
    # inline-literal form is mandatory; an array form like `exclude=(...)`
    # followed by `"${exclude[@]}"` substitution would silently fail on
    # POSIX `sh` (no array support).
    assert "exclude=(" not in step_1, (
        "skills/code-review/SKILL.md Step 1 contains a bash-array "
        "`exclude=(...)` construct — NOT POSIX-portable. Use inline "
        "literal pathspecs on each leg per ADR-062 M1 critique fix."
    )
    assert "${exclude[@]}" not in step_1, (
        "skills/code-review/SKILL.md Step 1 contains a bash-array "
        "expansion `${exclude[@]}` — NOT POSIX-portable. Use inline "
        "literal pathspecs on each leg per ADR-062 M1 critique fix."
    )


def test_skill_md_step_1_default_branch_resolver_stops_on_empty():
    """slice-065 AC#3 + AC#4 / /critique B2: pin the SKILL.md Step 1 bash
    block STOP guard for the default-branch-unresolvable corner case. Pre-
    fix, the bash silently falls through to `git merge-base "" HEAD` when
    both default-branch resolvers (`git symbolic-ref refs/remotes/origin/
    HEAD` AND `git config init.defaultBranch`) return empty — a CI clean-
    room corner case. Post-fix, the bash block inserts an explicit
    `[ -z "$default" ] && { echo "default-branch-unresolvable: ..." >&2;
    exit 2; }` guard between the second-resolver fallback and `git
    merge-base`, mirroring NAW-1's ADR-061 §Decision exit-2 contract.

    Bug class: M1 substring-leak retired by bash_block scoping (per
    /critique B2 — section-scoped `'[ -z "$default" ]' in step_1` and
    `'default-branch-unresolvable' in step_1` both already TRUE pre-fix
    via L41 fallback resolver + L68 documented-error-case prose;
    bash_block scoping + count discipline + co-location pin actually
    distinguishes pre-fix from post-fix structurally).

    Three composable assertions per /critique B2 proposed-fix (1)+(2)+(3)
    + /critique m2 brace-group form pinning:
      (a) Count-based pin: bash_block.count('[ -z "$default" ]') >= 2
          (additive STOP guard — distinguishes pre-fix count==1 from
          post-fix count==2)
      (b) Canonical brace-group form: `&& { echo "default-branch-
          unresolvable` substring + `exit 2` literal (NAW-1 parity per
          ADR-061 §Decision; prevents `if`/`fi`-style refactor regression)
      (c) Structural co-location: STOP guard appears AFTER second-
          resolver fallback AND BEFORE `git merge-base` (pins the
          structural relationship, not just substring existence; -1
          short-circuit safety — Python `138 < -1 < 188` evaluates False
          per chained-comparison short-circuit, so absent STOP guard
          correctly fails)
    """
    body = _read(_SKILL_MD)
    step_1_idx = body.find("### Step 1: Resolve the slice's code diff")
    step_2_idx = body.find("### Step 2:", step_1_idx)
    assert step_1_idx >= 0 and step_2_idx > step_1_idx, (
        "skills/code-review/SKILL.md missing `### Step 1:` or `### Step 2:` "
        "heading — section-scope cannot bound (slice-065 AC#4)"
    )
    step_1 = body[step_1_idx:step_2_idx]

    # Bash-block scoping idiom (canonical — used by slice-065 AC#1/#2/#4).
    bash_start = step_1.find("```bash\n")
    bash_end = step_1.find("\n```", bash_start)
    assert bash_start >= 0 and bash_end > bash_start, (
        "skills/code-review/SKILL.md Step 1 missing ```bash-fenced block — "
        "bash-block scoping cannot bound (slice-065 AC#4)"
    )
    bash_block = step_1[bash_start:bash_end]

    # (a) Count-based pin — the STOP guard is ADDITIVE to the existing
    # L41 second-resolver fallback `[ -z "$default" ] && default=$(...)`.
    # Pre-fix count = 1; post-fix count = 2.
    guard_count = bash_block.count('[ -z "$default" ]')
    assert guard_count >= 2, (
        f"skills/code-review/SKILL.md Step 1 bash block must carry the "
        f"STOP guard `[ -z \"$default\" ] && {{ ... exit 2; }}` AFTER the "
        f"second resolver (slice-065 AC#3) — observed {guard_count} "
        f"`[ -z \"$default\" ]` occurrences in the bash block, expected "
        f">= 2 (one for the second-resolver fallback at L41, one for "
        f"the new STOP guard inserted between L41 and L42)"
    )

    # (b) Canonical brace-group form (NAW-1 parity per ADR-061; per
    # /critique m2 — pins the canonical shape, prevents `if`/`fi`-style
    # refactor regression that would still pass a bare `'exit 2'`
    # substring check).
    assert '&& { echo "default-branch-unresolvable' in bash_block, (
        "skills/code-review/SKILL.md Step 1 bash block missing the "
        "canonical STOP-guard brace-group form `&& { echo "
        "\"default-branch-unresolvable...\" >&2; exit 2; }` mirroring "
        "NAW-1's exit-2 contract (ADR-061 §Decision — the three-step "
        "resolver: git symbolic-ref → git config init.defaultBranch → "
        "fail-fast with exit 2 + default-branch-unresolvable stderr)"
    )
    assert "exit 2" in bash_block, (
        "skills/code-review/SKILL.md Step 1 bash block missing `exit 2` — "
        "the STOP guard must propagate the exit-2 contract from NAW-1 "
        "(ADR-061 §Decision); a `return 1` or `exit 1` would break parity "
        "with the canonical NAW-1 Python implementation at "
        "tools/new_agent_warning_audit.py:_resolve_default_branch"
    )

    # (c) Structural co-location — STOP guard between second-resolver
    # fallback (`git config init.defaultBranch`) and `git merge-base`.
    # Per /critique B2 proposed-fix (3) — pins the structural
    # relationship the AC actually wants, not just substring existence.
    # -1 short-circuit safety: if stop_idx = -1 (pre-fix), Python
    # chained comparison `138 < -1 < 188` evaluates False (138 < -1 is
    # False; short-circuits) so the assertion correctly fires.
    fallback_idx = bash_block.find("git config init.defaultBranch")
    merge_base_idx = bash_block.find("git merge-base")
    stop_idx = bash_block.find('[ -z "$default" ] && {')
    assert fallback_idx < stop_idx < merge_base_idx, (
        f"skills/code-review/SKILL.md Step 1 bash block STOP guard not "
        f"structurally co-located between second-resolver fallback "
        f"(idx={fallback_idx}, 'git config init.defaultBranch') and "
        f"git merge-base (idx={merge_base_idx}); observed stop_idx="
        f"{stop_idx} (-1 means the canonical brace-group form is "
        f"absent from the bash block — see assertion (b))"
    )


def test_skill_md_step_1_union_aggregation_prose_pinned():
    """slice-064 AC#1 sibling (per /critique M2 + /critique-review): pin
    the Step 1 post-bash-block prose carrying Claude's runtime obligation
    to union + deduplicate the three command outputs. Without this prose
    pin, a future Claude could plausibly run only Source (iii) for token
    budget, concatenate without deduplicating, intersect instead of union,
    or ignore Source (ii) — all silent failures the AC#1 filter-shape pin
    cannot reach.

    Per CLAUDE.md "skill prose IS executable contract": Claude reads
    SKILL.md at runtime, NOT ADR-062. The union obligation must be
    SKILL.md-prose-binding, not ADR-only.
    """
    body = _read(_SKILL_MD)
    step_1_idx = body.find("### Step 1: Resolve the slice's code diff")
    step_2_idx = body.find("### Step 2:", step_1_idx)
    step_1 = body[step_1_idx:step_2_idx]

    # The canonical union instruction substring (per ADR-062 §Decision
    # Step 1 — new bash block, and design.md L13 + L102).
    assert "Union the three outputs by path" in step_1, (
        "skills/code-review/SKILL.md Step 1 missing the union-aggregation "
        "instruction `Union the three outputs by path` — Claude's runtime "
        "obligation to aggregate the three command outputs is not "
        "prose-pinned. Per ADR-062 §Decision + /critique M2 fix: the "
        "instruction MUST appear in Step 1 AFTER the three bash commands "
        "so a future Claude reading SKILL.md (not ADR-062) knows to union "
        "the outputs at runtime."
    )
    # Deduplication is part of the same instruction phrase.
    assert "deduplicate" in step_1.lower(), (
        "skills/code-review/SKILL.md Step 1 union-aggregation instruction "
        "missing the `deduplicate` clause — a future Claude could union "
        "without dedup, producing duplicate review work on a file that "
        "appears in multiple union sources (e.g., a staged-then-committed "
        "file appears in Sources i + iii)."
    )


def test_skill_md_step_2_diff_content_block_aligned_with_step_1():
    """slice-064 AC#3: pin the Step 2 prompt-template `# Diff content`
    block alignment with Step 1's union-of-three-sources resolution.
    Pre-fix Step 2 said `git diff <base>...HEAD -- <files>` (aggregate,
    commit-vs-commit only) — would silently re-introduce the B1 falsifier
    downstream by running a commit-vs-commit diff on the per-file content
    even after Step 1 enumerated the file list via the WT-aware union.

    Post-fix: Step 2 references the WT-vs-base diff per file
    (`git diff "$base" -- <file>`), which observes uncommitted edits
    consistently with Step 1.

    Section-scoped to Step 2 (the `# Diff content` heading lives in the
    Step 2 prompt-template code block).
    """
    body = _read(_SKILL_MD)
    step_2_idx = body.find("### Step 2:")
    step_3_idx = body.find("### Step 3:", step_2_idx)
    assert step_2_idx >= 0 and step_3_idx > step_2_idx, (
        "skills/code-review/SKILL.md missing `### Step 2:` or `### Step 3:` "
        "headings — section-scope cannot bound"
    )
    step_2 = body[step_2_idx:step_3_idx]

    # The `# Diff content` block is the prompt-template paste-in for the
    # agent. The per-file form must reference `git diff "$base"` (no
    # `...HEAD`), aligning with Step 1's WT-aware union.
    assert "# Diff content" in step_2, (
        "skills/code-review/SKILL.md Step 2 prompt-template missing the "
        "`# Diff content` paste-in heading"
    )
    # The pre-slice-064 form was `git diff <base>...HEAD -- <files>`. The
    # post-fix form must NOT carry the `...HEAD` aggregate-only form in
    # the prompt-template paste-in.
    assert "git diff <base>...HEAD" not in step_2 and "git diff $base...HEAD" not in step_2, (
        "skills/code-review/SKILL.md Step 2 prompt-template still "
        "references the pre-slice-064 commit-vs-commit aggregate form "
        "`git diff <base>...HEAD` — would silently re-introduce the B1 "
        "falsifier downstream on the per-file diff content even after "
        "Step 1's union resolves the file list correctly."
    )


def test_self_dogfood_produces_code_review_md_on_slice_060():
    """Walking-skeleton Layer 6 proof: invoking `/code-review` against
    slice-060 itself must produce `code-review.md` with non-empty findings
    (the artifact-existence-and-content check; NOT a pytest-driven LLM
    invocation — per critique M2 reclassification).

    Per slice-060 design.md Build-phase sequence Phase C: this test
    PASSES only after the self-dogfood `/code-review` invocation against
    slice-060 has run (which itself requires Phase B forward-sync to
    have completed). slice-062 / ADR-060 repoint: the slice-060 path is
    now lazy-resolved here via ``_resolve_slice_dir(60)`` (resolves the
    archived slice-060 folder via the helper's archive-glob fallback)
    instead of a hardcoded module-level literal — closes the slice-061
    N=1 R-15-class scope-gap that motivated the slice-062 backstop
    scope-extension.
    """
    slice_060_code_review = _resolve_slice_dir(60) / "code-review.md"
    body = _read(slice_060_code_review)
    # Result line present
    assert "**Result**" in body, (
        "slice-060 code-review.md missing **Result** header — agent output "
        "either malformed or self-dogfood did not run"
    )
    # Non-empty findings: at minimum, one of the canonical section markers
    # OR a NO-CODE-CHANGES result (which is itself valid output).
    has_findings = any(
        marker in body
        for marker in ("### B", "### M", "Blockers", "Majors", "Minors")
    )
    has_no_code_changes = "NO-CODE-CHANGES" in body
    assert has_findings or has_no_code_changes, (
        "slice-060 code-review.md missing non-empty findings AND lacks the "
        "NO-CODE-CHANGES marker — agent output is unusable"
    )
    # Dimensions footer present (the agent's specificity discipline)
    assert "## Dimensions checked" in body, (
        "slice-060 code-review.md missing `## Dimensions checked` footer — "
        "agent did not emit the 9-dimensions report"
    )
