"""Behavioral tests for tools/stranded_slice_audit.py (slice-087).

The detector CLASSIFIES every unmerged `slice/*` branch into a 4-class
divergence model (+ INDETERMINATE) and halts `/slice` only on genuine
divergence (STRANDED-COMPLETE / ORPHANED / INDETERMINATE). A healthy in-flight
parallel slice (own worktree, mid-stage) classifies as IN-PROGRESS and does NOT
halt — the binding parallel-safety property the slice-087 reframe exists to
guarantee (case 4c).

Cases (per mission-brief AC4):
- 4a STRANDED-COMPLETE — archived slice with an unmerged branch, archive entry
  committed ONLY on that branch (the M1 cross-tree case) → halt, divergent.
- 4b ORPHANED — unmerged slice/* branch with no vault story → halt.
- 4c IN-PROGRESS parallel-safety pin — worktree at a mid-stage → no halt, clean.
- 4d CLAIMED-BY-OTHER — branch whose queue key carries a foreign claim → no halt.
- 4e clean — no slice/* branches.
- 4f recovery/* + merged slice/* are not flagged.
- 4g malformed milestone → per-entry INDETERMINATE (halt), not whole-run exit-2.
- 4h own pushed-but-unmerged (vault archived, claim by ME) → STRANDED-COMPLETE
  (resumable, EXPECTED — not suppressed by a self-claim).
- 4i bare branch with the PRODUCTION terminal vocabulary → STRANDED-COMPLETE.

Branchless-in-flight cases (slice-092 / ADR-084 — the 5th INFORMATIONAL class):
- 4j a branchless `slice-NNN/` folder (non-terminal milestone, NO `slice/*` ref)
  → exactly one BRANCHLESS_IN_FLIGHT entry, halt=False, status clean, vault_state
  starts with `folder:` and names the stage (m1 pin).
- 4k dedup vs a BARE matching branch → reported once via the branch, zero
  BRANCHLESS.
- 4l a terminal branchless folder (`stage: complete`) → NOT surfaced as in-flight.
- 4m absent / malformed milestone + stray non-conforming dirs/files / `archive/`
  → all skipped, no raise (fail-open).
- 4n NON-VACUOUS worktree-key dedup: a worktree's own foldered+branched slice,
  classify_branches invoked FROM the worktree → one IN-PROGRESS, zero BRANCHLESS
  (a `wt.slice_name`-alone mis-key would fail this — B2 / M-add-1).
- 4o stage-less-but-parseable milestone → skipped, never `vault_state="folder:None"`.

Fixtures build synthetic git repos via tmp_path + `git worktree add`, matching
the idiom in tests/skills/pulse/test_detect_active_worktrees.py.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.pulse_worktree_resolver as _pwr
import tools.stranded_slice_audit as _ssa

# slice-110 / [[ADR-101]]: setattr-pin VAULT_ROOT (in-tree relative) on the
# stranded detector + _vault_git (its `vault_is_external` STOP guard at
# stranded_slice_audit.py:328) + pulse_worktree_resolver (its
# `classify_worktree_state` resolves the worktree milestone via VAULT_ROOT,
# :482 / :222) so all reads resolve under each test's own tmp repo/worktree —
# green under default AND an external AI_SDLC_VAULT_ROOT override (the flip sim).
_pin_vault = vi.autouse_pin(_vgit, _pwr, _ssa)

from tools.stranded_slice_audit import (
    DivergenceClass,
    classify_branches,
    compute_status,
)


# --------------------------- git fixture helpers ---------------------------


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def _init_repo(repo_root: Path, *, name: str = "test", email: str = "test@example.com") -> None:
    """Init a git repo at `repo_root` on master with one commit + an identity."""
    repo_root.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "master", str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", name, cwd=repo_root)
    _git("config", "user.email", email, cwd=repo_root)
    # No `origin` remote in the fixture → `_resolve_default_branch` falls back to
    # `git config init.defaultBranch`; set it locally so resolution is deterministic.
    _git("config", "init.defaultBranch", "master", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial", cwd=repo_root)


def _write_files(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def _make_bare_branch(repo_root: Path, tmp_path: Path, branch: str, files: dict[str, str]) -> None:
    """Create `branch` carrying `files`, committed, with NO live worktree.

    Uses a throwaway worktree to author the commit, then removes it — leaving a
    bare unmerged branch (the no-worktree case the detector's `for-each-ref`
    enumeration owns).
    """
    scratch = tmp_path / "_scratch" / branch.replace("/", "_")
    _git("worktree", "add", str(scratch), "-b", branch, "master", cwd=repo_root)
    _write_files(scratch, files)
    _git("add", "-A", cwd=scratch)
    _git("commit", "-m", f"scaffold {branch}", cwd=scratch)
    _git("worktree", "remove", str(scratch), "--force", cwd=repo_root)


def _add_live_worktree(
    repo_root: Path, tmp_path: Path, branch: str, files: dict[str, str]
) -> Path:
    """Create `branch` with a LIVE worktree at the canonical BRANCH-2 sibling path."""
    slice_dir = branch.replace("slice/", "slice-")
    wt_path = tmp_path / f"{repo_root.name}-wt" / slice_dir
    _git("worktree", "add", str(wt_path), "-b", branch, "master", cwd=repo_root)
    _write_files(wt_path, files)
    _git("add", "-A", cwd=wt_path)
    _git("commit", "-m", f"build {branch}", cwd=wt_path)
    return wt_path


def _milestone(slice_id: str, stage: str, next_action: str = "build") -> str:
    return (
        f"---\nslice: {slice_id}\nstage: {stage}\n"
        f"next-action: {next_action}\nrisk-tier: medium\ncritic-required: true\n---\n\n"
        f"# Milestone: {slice_id}\n"
    )


# ------------------------------- the cases -------------------------------


def test_stranded_complete_branch_halts(tmp_path: Path):
    """4a: a slice archived ONLY on its unmerged branch → STRANDED-COMPLETE (M1)."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    # Archive entry committed on the branch's own tree (NOT on master).
    _make_bare_branch(
        repo,
        tmp_path,
        "slice/200-foo",
        {
            "architecture/slices/archive/slice-200-foo/milestone.md": _milestone(
                "slice-200-foo", "reflect", "run /commit-slice --merge"
            )
        },
    )
    entries = classify_branches(repo)
    by_branch = {e.branch: e for e in entries}
    assert "slice/200-foo" in by_branch, f"branch not classified: {entries!r}"
    e = by_branch["slice/200-foo"]
    assert e.klass is DivergenceClass.STRANDED_COMPLETE, f"klass={e.klass!r} reason={e.reason!r}"
    assert e.halt is True
    assert compute_status(entries) == "divergent"


def test_complete_stage_bare_branch_is_stranded_complete(tmp_path: Path):
    """4i (B1/M1 — code-review): a bare branch carrying the PRODUCTION terminal
    milestone vocabulary (`stage: complete` / `next-action: none (slice complete)`,
    written by skills/reflect/SKILL.md, NOT archived) → STRANDED-COMPLETE, halt.

    This is the slice-086-class incident's general form (completed-but-unmerged,
    milestone NOT archived). It fails against the pre-fix `_TERMINAL_STAGES =
    {"reflect"}` (which the vault never writes at terminal) and passes post-fix."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    # Active (non-archived) milestone on the branch's own tree, real terminal vocabulary.
    _make_bare_branch(
        repo,
        tmp_path,
        "slice/206-realdone",
        {
            "architecture/slices/slice-206-realdone/milestone.md": _milestone(
                "slice-206-realdone", "complete", "none (slice complete)"
            )
        },
    )
    entries = classify_branches(repo)
    by_branch = {e.branch: e for e in entries}
    assert "slice/206-realdone" in by_branch
    e = by_branch["slice/206-realdone"]
    assert e.klass is DivergenceClass.STRANDED_COMPLETE, (
        f"a bare branch with the real terminal `stage: complete` must be STRANDED-COMPLETE, "
        f"not {e.klass!r} (reason={e.reason!r})"
    )
    assert e.halt is True
    assert compute_status(entries) == "divergent"


def test_orphaned_branch_halts(tmp_path: Path):
    """4b: an unmerged slice/* branch with no vault story → ORPHANED."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _make_bare_branch(
        repo, tmp_path, "slice/201-bar", {"junk.txt": "no vault story here\n"}
    )
    entries = classify_branches(repo)
    by_branch = {e.branch: e for e in entries}
    assert "slice/201-bar" in by_branch
    e = by_branch["slice/201-bar"]
    assert e.klass is DivergenceClass.ORPHANED, f"klass={e.klass!r} reason={e.reason!r}"
    assert e.halt is True
    assert compute_status(entries) == "divergent"


def test_in_progress_parallel_slice_does_not_halt(tmp_path: Path):
    """4c (BINDING parallel-safety pin): a worktree at a mid-stage → IN-PROGRESS,
    no halt, status clean. Must FAIL against a flag-all design, PASS here."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _add_live_worktree(
        repo,
        tmp_path,
        "slice/202-baz",
        {
            "architecture/slices/slice-202-baz/milestone.md": _milestone(
                "slice-202-baz", "design"
            )
        },
    )
    entries = classify_branches(repo)
    by_branch = {e.branch: e for e in entries}
    assert "slice/202-baz" in by_branch, f"worktree branch not classified: {entries!r}"
    e = by_branch["slice/202-baz"]
    assert e.klass is DivergenceClass.IN_PROGRESS, f"klass={e.klass!r} reason={e.reason!r}"
    assert e.halt is False
    assert compute_status(entries) == "clean", "a healthy parallel slice must NOT make /slice divergent"


def test_claimed_by_other_is_informational(tmp_path: Path):
    """4d: a branch whose queue key carries a claim by a DIFFERENT git identity
    → CLAIMED-BY-OTHER (informational, no halt). Synthetic queue (B1 honesty)."""
    repo = tmp_path / "repo"
    _init_repo(repo, name="test", email="test@example.com")
    # Branch is vault-done (would otherwise be STRANDED-COMPLETE) but claimed by
    # another identity → CLAIMED-BY-OTHER wins (precedence #1).
    _make_bare_branch(
        repo,
        tmp_path,
        "slice/203-qux",
        {
            "architecture/slices/archive/slice-203-qux/milestone.md": _milestone(
                "slice-203-qux", "reflect", "run /commit-slice"
            )
        },
    )
    _write_files(
        repo,
        {
            "architecture/slice-queue.md": (
                "# Slice queue\n\n## Candidates\n\n"
                "### qux\n\n"
                "- **Source:** test\n"
                "- **Risk-retired:** NONE\n"
                "- **Claimed-by:** Other Dev other@example.com\n"
                "- **Claimed-at:** 2026-05-31T00:00:00+00:00\n"
            )
        },
    )
    entries = classify_branches(repo)
    by_branch = {e.branch: e for e in entries}
    assert "slice/203-qux" in by_branch
    e = by_branch["slice/203-qux"]
    assert e.klass is DivergenceClass.CLAIMED_BY_OTHER, f"klass={e.klass!r} reason={e.reason!r}"
    assert e.halt is False
    assert e.claimed_by == "Other Dev other@example.com"
    assert compute_status(entries) == "clean"


def test_clean_when_no_slice_branches(tmp_path: Path):
    """4e: a repo with no slice/* branches → no entries, status clean."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    entries = classify_branches(repo)
    assert entries == [], f"expected no entries; got {entries!r}"
    assert compute_status(entries) == "clean"


def test_ignores_recovery_and_merged_branches(tmp_path: Path):
    """4f: recovery/* (outside the refs/heads/slice/ glob) and merged slice/*
    (ancestor of default) are NOT flagged → status clean."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    # recovery/* branch — must be excluded structurally by the ref-glob.
    _git("branch", "recovery/slice-211-x", "master", cwd=repo)
    # merged slice/* branch: author a commit then merge into master so it's an ancestor.
    _make_bare_branch(repo, tmp_path, "slice/210-merged", {"feat.txt": "done\n"})
    _git("merge", "--no-ff", "slice/210-merged", "-m", "merge 210", cwd=repo)
    entries = classify_branches(repo)
    flagged = {e.branch for e in entries}
    assert "recovery/slice-211-x" not in flagged, "recovery/* must not be enumerated"
    assert "slice/210-merged" not in flagged, "a merged slice/* branch must be skipped"
    assert compute_status(entries) == "clean", f"unexpected entries: {entries!r}"


def test_malformed_milestone_is_indeterminate(tmp_path: Path):
    """4g: a worktree whose milestone frontmatter is malformed → classify_worktree_state
    UNKNOWN → INDETERMINATE (halt, fail-closed) — NOT a whole-run exit-2."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _add_live_worktree(
        repo,
        tmp_path,
        "slice/204-broken",
        {
            # No parseable `stage:` → _parse_milestone_stage returns None → UNKNOWN.
            "architecture/slices/slice-204-broken/milestone.md": "no frontmatter at all\n"
        },
    )
    entries = classify_branches(repo)  # must not raise
    by_branch = {e.branch: e for e in entries}
    assert "slice/204-broken" in by_branch
    e = by_branch["slice/204-broken"]
    assert e.klass is DivergenceClass.INDETERMINATE, f"klass={e.klass!r} reason={e.reason!r}"
    assert e.halt is True
    assert compute_status(entries) == "divergent"


def test_own_pushed_unmerged_branch_is_stranded_complete_resumable(tmp_path: Path):
    """4h (m-add-1): the slice's OWN pushed-but-unmerged branch (vault archived,
    claim by ME) → STRANDED-COMPLETE/resumable. A self-claim must NOT suppress the
    halt (CLAIMED-BY-OTHER fires only on a FOREIGN identity)."""
    repo = tmp_path / "repo"
    _init_repo(repo, name="test", email="test@example.com")
    _make_bare_branch(
        repo,
        tmp_path,
        "slice/205-mine",
        {
            "architecture/slices/archive/slice-205-mine/milestone.md": _milestone(
                "slice-205-mine", "reflect", "run /commit-slice --sync-after-pr"
            )
        },
    )
    _write_files(
        repo,
        {
            "architecture/slice-queue.md": (
                "# Slice queue\n\n## Candidates\n\n"
                "### mine\n\n"
                "- **Source:** test\n"
                "- **Risk-retired:** NONE\n"
                "- **Claimed-by:** test test@example.com\n"
                "- **Claimed-at:** 2026-05-31T00:00:00+00:00\n"
            )
        },
    )
    entries = classify_branches(repo)
    by_branch = {e.branch: e for e in entries}
    assert "slice/205-mine" in by_branch
    e = by_branch["slice/205-mine"]
    assert e.klass is DivergenceClass.STRANDED_COMPLETE, (
        f"a self-claim must not suppress the halt; klass={e.klass!r} reason={e.reason!r}"
    )
    assert e.halt is True
    assert compute_status(entries) == "divergent"


# ------------------- branchless-in-flight cases (slice-092 / ADR-084) -------------------


def test_branchless_in_flight_slice_is_informational_status_clean(tmp_path: Path):
    """4j (AC2 surface + AC3 informational + m1): an untracked `slice-NNN-<name>/`
    folder with a non-terminal milestone and NO `slice/NNN-*` branch → exactly ONE
    BRANCHLESS_IN_FLIGHT entry, halt=False, status clean, and `vault_state`
    starts with `folder:` naming the stage (m1 prefix pin)."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _write_files(
        repo,
        {
            "architecture/slices/slice-220-branchless/milestone.md": _milestone(
                "slice-220-branchless", "design", "run /critique"
            ),
            "architecture/slices/slice-220-branchless/mission-brief.md": "# Slice 220\n",
        },
    )
    # Sanity: genuinely no slice/220-* branch.
    assert _git("branch", "--list", "slice/220-*", cwd=repo).stdout.strip() == ""

    entries = classify_branches(repo)
    branchless = [e for e in entries if e.klass is DivergenceClass.BRANCHLESS_IN_FLIGHT]
    assert len(branchless) == 1, f"expected exactly one branchless entry; got {entries!r}"
    e = branchless[0]
    assert e.halt is False, f"a branchless in-flight slice must be informational; halt={e.halt!r}"
    assert "220-branchless" in e.branch, f"entry must name the slice (folder-form id); branch={e.branch!r}"
    assert e.vault_state.startswith("folder:"), f"vault_state must start with `folder:` (m1); got {e.vault_state!r}"
    assert "design" in e.vault_state, f"vault_state must name the stage; got {e.vault_state!r}"
    assert compute_status(entries) == "clean", (
        f"surfacing a branchless in-flight slice must NOT make /slice divergent; entries={entries!r}"
    )


def test_branchless_slice_not_double_reported_when_bare_branch_exists(tmp_path: Path):
    """4k (B2 dedup — BARE variant): a slice with BOTH a `slice-NNN/` folder in the
    invoking tree AND a matching BARE `slice/NNN` branch → reported EXACTLY ONCE
    (via the branch path); zero BRANCHLESS_IN_FLIGHT for it."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    # Bare branch with a non-terminal milestone on its OWN tree → IN-PROGRESS.
    _make_bare_branch(
        repo,
        tmp_path,
        "slice/221-dup",
        {"architecture/slices/slice-221-dup/milestone.md": _milestone("slice-221-dup", "build")},
    )
    # The SAME slice's folder also present (untracked) in the invoking tree.
    _write_files(
        repo,
        {"architecture/slices/slice-221-dup/milestone.md": _milestone("slice-221-dup", "build")},
    )
    entries = classify_branches(repo)
    for_221 = [e for e in entries if "221-dup" in (e.branch or "")]
    assert len(for_221) == 1, f"slice-221-dup must be reported exactly once; got {for_221!r}"
    assert for_221[0].branch == "slice/221-dup", (
        f"the single entry must be the BRANCH entry, not the folder-form id; got {for_221[0].branch!r}"
    )
    assert not [
        e for e in entries if e.klass is DivergenceClass.BRANCHLESS_IN_FLIGHT and "221-dup" in e.branch
    ], "the folder must be deduped against its bare branch"


def test_branchless_terminal_folder_not_surfaced_as_in_flight(tmp_path: Path):
    """4l (AC4): a branchless folder whose milestone uses the PRODUCTION terminal
    vocabulary (`stage: complete` / `next-action: none (slice complete)`) is NOT
    surfaced as in-flight (zero BRANCHLESS_IN_FLIGHT); status clean."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _write_files(
        repo,
        {
            "architecture/slices/slice-222-done/milestone.md": _milestone(
                "slice-222-done", "complete", "none (slice complete)"
            )
        },
    )
    entries = classify_branches(repo)
    assert [e for e in entries if e.klass is DivergenceClass.BRANCHLESS_IN_FLIGHT] == []
    assert not [e for e in entries if "222-done" in (e.branch or "")], (
        f"a terminal branchless folder must not be surfaced; got {entries!r}"
    )
    assert compute_status(entries) == "clean"


def test_branchless_absent_or_malformed_milestone_and_stray_dirs_fail_open(tmp_path: Path):
    """4m (AC4 robustness): a folder with NO milestone, one with unparseable
    frontmatter, a non-conforming dir (`slice-bad`), a stray file (`_index.md`),
    and `archive/` are all skipped — no entry, no raise (fail-open)."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _write_files(
        repo,
        {
            "architecture/slices/slice-230-nomilestone/mission-brief.md": "# no milestone here\n",
            "architecture/slices/slice-231-badfm/milestone.md": "no frontmatter at all\n",
            "architecture/slices/slice-bad/milestone.md": _milestone("slice-bad", "design"),
            "architecture/slices/_index.md": "# index\n",
            "architecture/slices/archive/slice-099-old/milestone.md": _milestone(
                "slice-099-old", "design"
            ),
        },
    )
    entries = classify_branches(repo)  # must not raise
    branchless = [e for e in entries if e.klass is DivergenceClass.BRANCHLESS_IN_FLIGHT]
    assert branchless == [], (
        f"fail-open / non-conforming / archived folders must not surface; got {branchless!r}"
    )
    assert compute_status(entries) == "clean"


def test_branchless_dedup_against_worktree_branch_is_non_vacuous(tmp_path: Path):
    """4n (B1 context-2 + M-add-1, NON-VACUOUS): a worktree's OWN foldered+branched
    slice, with classify_branches invoked FROM the worktree (where the folder AND
    the live worktree-branch coexist) → exactly one IN-PROGRESS entry, zero
    BRANCHLESS_IN_FLIGHT.

    This genuinely exercises the worktree-key dedup (B2): the folder IS scanned
    (it lives in the worktree's tree) but suppressed because the worktree branch
    key `slice/240-selfwt`[6:] == `240-selfwt` matches the folder key. A
    `wt.slice_name`-alone derivation (`selfwt`) would NOT match and a spurious
    BRANCHLESS entry would surface — failing this test (the vacuity guard)."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    wt_path = _add_live_worktree(
        repo,
        tmp_path,
        "slice/240-selfwt",
        {"architecture/slices/slice-240-selfwt/milestone.md": _milestone("slice-240-selfwt", "build")},
    )
    # Invoke from INSIDE the worktree — the folder lives here, not in the main tree.
    entries = classify_branches(wt_path)
    for_240 = [e for e in entries if "240-selfwt" in (e.branch or "")]
    assert len(for_240) == 1, f"slice-240-selfwt must be reported exactly once; got {entries!r}"
    e = for_240[0]
    assert e.klass is DivergenceClass.IN_PROGRESS, f"klass={e.klass!r} reason={e.reason!r}"
    assert e.branch == "slice/240-selfwt", (
        f"the single entry must be the worktree BRANCH, not the folder-form id; got {e.branch!r}"
    )
    assert [x for x in entries if x.klass is DivergenceClass.BRANCHLESS_IN_FLIGHT] == [], (
        "the worktree's own folder must be DEDUPED against its worktree branch (B2 worktree-key); "
        f"got {entries!r}"
    )


def test_branchless_stageless_milestone_emits_no_folder_none(tmp_path: Path):
    """4o (m-add-2): a branchless folder whose milestone has well-formed `---`
    frontmatter but NO `stage:` field → treated as incomplete and SKIPPED; it
    must NEVER emit the literal `vault_state="folder:None"`."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _write_files(
        repo,
        {
            "architecture/slices/slice-250-nostage/milestone.md": (
                "---\nslice: slice-250-nostage\nnext-action: run /critique\n"
                "risk-tier: medium\ncritic-required: true\n---\n\n# Milestone\n"
            )
        },
    )
    entries = classify_branches(repo)
    assert not [e for e in entries if "250-nostage" in (e.branch or "")], (
        f"a stage-less milestone must be skipped, not surfaced; got {entries!r}"
    )
    assert not [e for e in entries if e.vault_state == "folder:None"], (
        f"must never emit the literal `folder:None`; got {entries!r}"
    )
