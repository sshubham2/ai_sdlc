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

Fixtures build synthetic git repos via tmp_path + `git worktree add`, matching
the idiom in tests/skills/pulse/test_detect_active_worktrees.py.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

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
