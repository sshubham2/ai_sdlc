"""APED-1 empirical-execution battery for slice-077 / ADR-070.

Per mission-brief must-not-defer #3 + design.md L243. Executes ≥13 enumerated
cases against real synthetic git fixtures (tmp_path + git init + git worktree
add) and asserts observed-behavior matches expected per case.

Cases:
- detect_active_worktrees: 6 cases
  1. empty (no slice worktrees) → []
  2. one-slice-worktree → [WorktreeInfo(slice-077-test)]
  3. multiple-slice-worktrees → 2 entries
  4. non-slice-branch-filtered → main branch other than slice/* filtered out
  5. mixed-slice-and-non-slice → only slice/* entries returned
  6. stale-prunable → prunable entry filtered out
- classify_worktree_state: 7 cases
  1. IN_PROGRESS (stage=build, head whatever)
  2. BUILT_BUT_NOT_MERGED (stage=reflect, head not-ancestor)
  3. MERGED (stage=reflect, head is-ancestor)
  4. UNKNOWN-no-milestone (milestone path None)
  5. UNKNOWN-malformed-frontmatter (file exists but no stage: field)
  6. UNKNOWN-git-merge-base-error (head sha invalid)
  7. UNKNOWN-head-unresolvable (head_sha empty)

APED-1 catches design→code translation gaps that mock-based unit tests can
miss (e.g., the _resolve_milestone_path scan-root bug found at mid-slice
smoke — unit tests using fake fixtures with milestone present at repo_root
passed, but real worktree milestones live in the worktree's filesystem).

Usage: `python architecture/slices/slice-077-.../aped_1_battery.py`
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Callable

# Allow running from anywhere
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.pulse_worktree_resolver import (  # noqa: E402
    WorktreeInfo,
    WorktreeState,
    WorktreeStateClassification,
    classify_worktree_state,
    detect_active_worktrees,
)


@dataclass
class Case:
    name: str
    expected: str
    observed: str = ""
    passed: bool = False


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo_root: Path) -> str:
    """Init git repo at repo_root on master with one commit. Returns HEAD sha."""
    repo_root.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "master", str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", "test", cwd=repo_root)
    _git("config", "user.email", "test@example.com", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial", cwd=repo_root)
    return _git("rev-parse", "HEAD", cwd=repo_root).stdout.strip()


def _write_milestone(slice_dir: Path, stage: str) -> Path:
    slice_dir.mkdir(parents=True, exist_ok=True)
    p = slice_dir / "milestone.md"
    p.write_text(
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
    return p


# ----------------------------- detect cases -----------------------------


def detect_empty(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    result = detect_active_worktrees(repo)
    return f"len={len(result)}"


def detect_one_slice_worktree(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    wt = tmp / "repo-wt" / "slice-077-test"
    _git("worktree", "add", str(wt), "-b", "slice/077-test", "master", cwd=repo)
    result = detect_active_worktrees(repo)
    if not result:
        return "len=0 (expected 1)"
    return f"len={len(result)} branch={result[0].branch} num={result[0].slice_num} name={result[0].slice_name}"


def detect_multiple_slice_worktrees(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    _git("worktree", "add", str(tmp / "repo-wt" / "slice-077-foo"), "-b", "slice/077-foo", "master", cwd=repo)
    _git("worktree", "add", str(tmp / "repo-wt" / "slice-078-bar"), "-b", "slice/078-bar", "master", cwd=repo)
    result = detect_active_worktrees(repo)
    return f"len={len(result)} branches={sorted(w.branch for w in result)}"


def detect_non_slice_branch_filtered(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    _git("worktree", "add", str(tmp / "feature-wt"), "-b", "feature/foo", "master", cwd=repo)
    result = detect_active_worktrees(repo)
    return f"len={len(result)}"


def detect_mixed_slice_and_non_slice(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    _git("worktree", "add", str(tmp / "repo-wt" / "slice-077-test"), "-b", "slice/077-test", "master", cwd=repo)
    _git("worktree", "add", str(tmp / "feature-wt"), "-b", "feature/foo", "master", cwd=repo)
    result = detect_active_worktrees(repo)
    branches = sorted(w.branch for w in result)
    return f"len={len(result)} branches={branches}"


def detect_stale_prunable(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    wt = tmp / "repo-wt" / "slice-077-test"
    _git("worktree", "add", str(wt), "-b", "slice/077-test", "master", cwd=repo)
    # Forcibly remove the worktree dir to make it prunable (git tracks but disk gone)
    shutil.rmtree(wt)
    # Now `git worktree list --porcelain` will mark it `prunable` or the path won't exist
    result = detect_active_worktrees(repo)
    return f"len={len(result)} (prunable should be filtered)"


# ----------------------------- classify cases -----------------------------


def classify_in_progress(tmp: Path) -> str:
    repo = tmp / "repo"
    head = _init_repo(repo)
    milestone = _write_milestone(repo / "architecture" / "slices" / "slice-077-test", "build")
    info = WorktreeInfo(
        path=str(repo), branch="slice/077-test", head_sha=head,
        slice_num="077", slice_name="test", milestone_path=milestone,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} stage={cls.milestone_stage}"


def classify_built_but_not_merged(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    _git("checkout", "-b", "slice/077-test", cwd=repo)
    (repo / "new.md").write_text("slice work\n", encoding="utf-8")
    _git("add", "new.md", cwd=repo)
    _git("commit", "-m", "slice commit", cwd=repo)
    head = _git("rev-parse", "HEAD", cwd=repo).stdout.strip()
    milestone = _write_milestone(repo / "architecture" / "slices" / "slice-077-test", "reflect")
    _git("add", "architecture", cwd=repo)
    _git("commit", "-m", "reflect milestone", cwd=repo)
    head = _git("rev-parse", "HEAD", cwd=repo).stdout.strip()
    info = WorktreeInfo(
        path=str(repo), branch="slice/077-test", head_sha=head,
        slice_num="077", slice_name="test", milestone_path=milestone,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} stage={cls.milestone_stage}"


def classify_merged(tmp: Path) -> str:
    repo = tmp / "repo"
    head = _init_repo(repo)
    milestone = _write_milestone(repo / "architecture" / "slices" / "slice-077-test", "reflect")
    # HEAD == master tip → IS ancestor of master
    info = WorktreeInfo(
        path=str(repo), branch="slice/077-test", head_sha=head,
        slice_num="077", slice_name="test", milestone_path=milestone,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} stage={cls.milestone_stage}"


def classify_unknown_no_milestone(tmp: Path) -> str:
    repo = tmp / "repo"
    head = _init_repo(repo)
    info = WorktreeInfo(
        path=str(repo), branch="slice/077-test", head_sha=head,
        slice_num="077", slice_name="test", milestone_path=None,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} reason={cls.reason}"


def classify_unknown_malformed_frontmatter(tmp: Path) -> str:
    repo = tmp / "repo"
    head = _init_repo(repo)
    # Write malformed milestone (no stage: field)
    slice_dir = repo / "architecture" / "slices" / "slice-077-test"
    slice_dir.mkdir(parents=True)
    milestone = slice_dir / "milestone.md"
    milestone.write_text("---\nno: stage: field\n---\n# malformed\n", encoding="utf-8")
    info = WorktreeInfo(
        path=str(repo), branch="slice/077-test", head_sha=head,
        slice_num="077", slice_name="test", milestone_path=milestone,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} reason={cls.reason}"


def classify_unknown_merge_base_error(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    milestone = _write_milestone(repo / "architecture" / "slices" / "slice-077-test", "reflect")
    # Inject a non-existent SHA to force merge-base error
    info = WorktreeInfo(
        path=str(repo), branch="slice/077-test",
        head_sha="0000000000000000000000000000000000000000",  # non-existent sha
        slice_num="077", slice_name="test", milestone_path=milestone,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} reason={cls.reason}"


def classify_unknown_head_unresolvable(tmp: Path) -> str:
    repo = tmp / "repo"
    _init_repo(repo)
    milestone = _write_milestone(repo / "architecture" / "slices" / "slice-077-test", "reflect")
    # Empty head_sha + worktree path doesn't actually exist as a git repo →
    # git rev-parse HEAD will fail
    info = WorktreeInfo(
        path=str(tmp / "nonexistent"),  # not a git repo
        branch="slice/077-test", head_sha="",
        slice_num="077", slice_name="test", milestone_path=milestone,
    )
    cls = classify_worktree_state(info, "master", repo)
    return f"state={cls.state.value} reason={cls.reason}"


# ----------------------------- runner -----------------------------


CASES: list[tuple[str, Callable[[Path], str], str]] = [
    # detect cases (6)
    ("detect/empty", detect_empty, "len=0"),
    ("detect/one-slice-worktree", detect_one_slice_worktree, "len=1 branch=slice/077-test num=077 name=test"),
    ("detect/multiple-slice-worktrees", detect_multiple_slice_worktrees, "len=2 branches=['slice/077-foo', 'slice/078-bar']"),
    ("detect/non-slice-branch-filtered", detect_non_slice_branch_filtered, "len=0"),
    ("detect/mixed-slice-and-non-slice", detect_mixed_slice_and_non_slice, "len=1 branches=['slice/077-test']"),
    ("detect/stale-prunable", detect_stale_prunable, "len=0 (prunable should be filtered)"),
    # classify cases (7)
    ("classify/IN_PROGRESS", classify_in_progress, "state=IN_PROGRESS stage=build"),
    ("classify/BUILT_BUT_NOT_MERGED", classify_built_but_not_merged, "state=BUILT_BUT_NOT_MERGED stage=reflect"),
    ("classify/MERGED", classify_merged, "state=MERGED stage=reflect"),
    ("classify/UNKNOWN-no-milestone", classify_unknown_no_milestone, "state=UNKNOWN reason=fresh-worktree-no-milestone"),
    ("classify/UNKNOWN-malformed-frontmatter", classify_unknown_malformed_frontmatter, "state=UNKNOWN reason=milestone-frontmatter-malformed"),
    ("classify/UNKNOWN-merge-base-error", classify_unknown_merge_base_error, "state=UNKNOWN reason=merge-base-error"),
    ("classify/UNKNOWN-head-unresolvable", classify_unknown_head_unresolvable, "state=UNKNOWN reason=head-unresolvable"),
]


def run_battery() -> int:
    # UTF8-STDOUT-1 shim for Windows cp1252 console safety
    from tools import _stdout
    _stdout.reconfigure_stdout_utf8()
    print(f"APED-1 Battery: {len(CASES)} cases\n")
    results: list[Case] = []
    for name, fn, expected in CASES:
        c = Case(name=name, expected=expected)
        with tempfile.TemporaryDirectory() as td:
            try:
                c.observed = fn(Path(td))
                c.passed = c.observed == expected
            except Exception as e:
                c.observed = f"EXCEPTION: {type(e).__name__}: {e}"
                c.passed = False
        marker = "PASS" if c.passed else "FAIL"
        print(f"  [{marker}] {c.name}")
        if not c.passed:
            print(f"      expected: {c.expected}")
            print(f"      observed: {c.observed}")
        results.append(c)
    passed = sum(1 for c in results if c.passed)
    total = len(results)
    print(f"\n{passed}/{total} cases passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_battery())
