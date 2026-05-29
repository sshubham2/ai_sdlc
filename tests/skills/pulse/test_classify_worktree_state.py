"""Unit tests for classify_worktree_state covering 4 WorktreeState values
+ UNKNOWN sub-reasons per slice-077 design.md § Fail-closed paths.

Per design.md § 4-state worktree taxonomy + ADR-070 L46-58. Tests use
synthetic git fixtures via tmp_path + subprocess.run('git init') + worktree
manipulation. Helper invocations use monkeypatch where needed to simulate
specific failure modes (e.g., dirty WT, malformed milestone.md).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from textwrap import dedent

from tools.pulse_worktree_resolver import (
    WorktreeInfo,
    WorktreeState,
    classify_worktree_state,
)


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo_root: Path, default_branch: str = "master") -> None:
    """Initialize a git repo at `repo_root` on the given default branch with
    one initial commit. Configures user.name/email so commits succeed in CI."""
    _git("init", "-b", default_branch, str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", "test", cwd=repo_root)
    _git("config", "user.email", "test@example.com", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial commit", cwd=repo_root)


def _write_milestone(slice_dir: Path, stage: str) -> Path:
    """Write a minimal milestone.md with the given stage frontmatter field."""
    slice_dir.mkdir(parents=True, exist_ok=True)
    milestone = slice_dir / "milestone.md"
    milestone.write_text(
        dedent(
            f"""\
            ---
            slice: slice-077-test
            stage: {stage}
            updated: 2026-05-28
            ---
            # test milestone
            """
        ),
        encoding="utf-8",
    )
    return milestone


def test_classify_returns_in_progress_when_milestone_stage_is_pre_reflect(tmp_path: Path):
    """Worktree with milestone.md stage=`build` (or any non-reflect stage) →
    IN_PROGRESS per ADR-070."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    slice_dir = repo_root / "architecture" / "slices" / "slice-077-test"
    milestone = _write_milestone(slice_dir, stage="build")
    head_sha = _git("rev-parse", "HEAD", cwd=repo_root).stdout.strip()
    info = WorktreeInfo(
        path=str(repo_root),
        branch="slice/077-test",
        head_sha=head_sha,
        slice_num="077",
        slice_name="test",
        milestone_path=milestone,
    )
    cls = classify_worktree_state(info, default_branch="master", repo_root=repo_root)
    assert cls.state == WorktreeState.IN_PROGRESS, f"got {cls.state} reason={cls.reason!r}"
    assert cls.milestone_stage == "build"


def test_classify_returns_built_but_not_merged_when_reflect_stage_and_head_not_ancestor_of_default(
    tmp_path: Path,
):
    """Worktree with milestone.md stage=`reflect` AND HEAD NOT ancestor of
    default → BUILT_BUT_NOT_MERGED per ADR-070. Simulate by creating a slice
    branch with a commit master doesn't have."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    # Create a slice branch with a commit master doesn't have
    _git("checkout", "-b", "slice/077-test", cwd=repo_root)
    (repo_root / "new.md").write_text("slice work\n", encoding="utf-8")
    _git("add", "new.md", cwd=repo_root)
    _git("commit", "-m", "slice commit", cwd=repo_root)
    head_sha = _git("rev-parse", "HEAD", cwd=repo_root).stdout.strip()
    slice_dir = repo_root / "architecture" / "slices" / "slice-077-test"
    milestone = _write_milestone(slice_dir, stage="reflect")
    _git("add", "architecture", cwd=repo_root)
    _git("commit", "-m", "add reflect milestone", cwd=repo_root)
    head_sha = _git("rev-parse", "HEAD", cwd=repo_root).stdout.strip()
    info = WorktreeInfo(
        path=str(repo_root),
        branch="slice/077-test",
        head_sha=head_sha,
        slice_num="077",
        slice_name="test",
        milestone_path=milestone,
    )
    cls = classify_worktree_state(info, default_branch="master", repo_root=repo_root)
    assert cls.state == WorktreeState.BUILT_BUT_NOT_MERGED, (
        f"got {cls.state} reason={cls.reason!r}"
    )
    assert cls.milestone_stage == "reflect"


def test_classify_returns_merged_when_head_reachable_from_default(tmp_path: Path):
    """Worktree HEAD reachable from default → MERGED (transient cleanup-candidate
    state per ADR-070; can persist after --push + /sync-after-pr or --merge
    worktree-remove failure)."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    # HEAD on master IS ancestor of master's tip
    head_sha = _git("rev-parse", "HEAD", cwd=repo_root).stdout.strip()
    slice_dir = repo_root / "architecture" / "slices" / "slice-077-test"
    milestone = _write_milestone(slice_dir, stage="reflect")
    info = WorktreeInfo(
        path=str(repo_root),
        branch="slice/077-test",
        head_sha=head_sha,
        slice_num="077",
        slice_name="test",
        milestone_path=milestone,
    )
    cls = classify_worktree_state(info, default_branch="master", repo_root=repo_root)
    assert cls.state == WorktreeState.MERGED, f"got {cls.state} reason={cls.reason!r}"


def test_classify_returns_unknown_on_unparseable_git_state(tmp_path: Path):
    """milestone.md absent → UNKNOWN with reason `fresh-worktree-no-milestone`
    per design.md § Fail-closed paths. Closes the witnessed-gap class (fresh
    BRANCH-2 worktree pre-scaffold) per M3 ACCEPTED-FIXED."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    head_sha = _git("rev-parse", "HEAD", cwd=repo_root).stdout.strip()
    info = WorktreeInfo(
        path=str(repo_root),
        branch="slice/077-test",
        head_sha=head_sha,
        slice_num="077",
        slice_name="test",
        milestone_path=None,  # no milestone — pre-scaffold worktree
    )
    cls = classify_worktree_state(info, default_branch="master", repo_root=repo_root)
    assert cls.state == WorktreeState.UNKNOWN
    assert cls.reason == "fresh-worktree-no-milestone", (
        f"expected fresh-worktree-no-milestone reason; got {cls.reason!r}"
    )
