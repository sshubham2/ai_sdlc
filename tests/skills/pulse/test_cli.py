"""Unit tests for the pulse_worktree_resolver CLI per slice-077 AC#5 +
design.md § Cross-spec parity.

Tests --detect + --classify modes with --json output. Use subprocess to
invoke `python -m tools.pulse_worktree_resolver` from a synthetic git repo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "master", str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", "test", cwd=repo_root)
    _git("config", "user.email", "test@example.com", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial", cwd=repo_root)


_REPO_ROOT = Path(__file__).resolve().parents[3]


def _run_cli(
    *args: str, cwd: Path, extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Invoke `python -m tools.pulse_worktree_resolver` with given args.

    The cwd parameter is used for the subprocess working directory; PYTHONPATH
    is set to the slice worktree root so `tools.pulse_worktree_resolver` is
    importable regardless of where the synthetic repo sits. `extra_env` overlays
    additional environment variables (e.g. GIT_CONFIG_GLOBAL/SYSTEM isolation so
    a machine-level `init.defaultBranch` cannot leak into default-branch
    resolution — Fix H).
    """
    import os
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(_REPO_ROOT) + (os.pathsep + existing if existing else "")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-m", "tools.pulse_worktree_resolver", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_cli_detect_json_emits_parseable_worktree_list(tmp_path: Path):
    """`--detect --json --repo-root <root>` emits parseable JSON with action='detect'
    + 'worktrees' key (list)."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    proc = _run_cli("--detect", "--json", "--repo-root", str(repo_root), cwd=repo_root)
    assert proc.returncode == 0, f"exit {proc.returncode}; stderr={proc.stderr!r}"
    data = json.loads(proc.stdout)
    assert data["action"] == "detect"
    assert "worktrees" in data
    assert isinstance(data["worktrees"], list)


def test_cli_classify_json_returns_state_for_given_slice(tmp_path: Path):
    """`--classify slice-077-test --json --repo-root <root>` exits 0 and emits
    parseable JSON with action='classify' + a concrete (non-UNKNOWN) classification.

    Fix H (slice-077 M2): the prior `pytest.skip` fallback (fired when the synthetic
    repo had no resolvable default branch) is dropped. The synthetic repo now (a)
    configures `init.defaultBranch=master` so `_resolve_default_branch`'s fallback leg
    resolves deterministically, and (b) seeds a `stage: build` milestone.md in the
    worktree so classification yields IN_PROGRESS (exit 0), exercising the real
    success path instead of skipping.
    """
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    # Fix H: deterministic default-branch resolution (fallback leg of
    # _resolve_default_branch — `git config init.defaultBranch`).
    _git("config", "init.defaultBranch", "master", cwd=repo_root)
    # Create the slice worktree so --classify has a target.
    wt_path = tmp_path / "repo-wt" / "slice-077-test"
    _git("worktree", "add", str(wt_path), "-b", "slice/077-test", "master", cwd=repo_root)
    # Seed a milestone.md in the worktree so classification is concrete (stage=build ->
    # IN_PROGRESS), not UNKNOWN (which would exit 1).
    milestone = wt_path / "architecture" / "slices" / "slice-077-test" / "milestone.md"
    milestone.parent.mkdir(parents=True, exist_ok=True)
    milestone.write_text(
        "---\nslice: slice-077-test\nstage: build\n---\n", encoding="utf-8"
    )
    proc = _run_cli(
        "--classify", "slice-077-test", "--json", "--repo-root", str(repo_root), cwd=repo_root
    )
    assert proc.returncode == 0, f"exit {proc.returncode}; stderr={proc.stderr!r}"
    data = json.loads(proc.stdout)
    assert data["action"] == "classify"
    assert "classification" in data
    assert data["classification"]["state"] == "IN_PROGRESS", (
        f"expected IN_PROGRESS for a stage=build worktree, got {data['classification']}"
    )


def test_cli_classify_returns_error_on_unresolvable_default_branch(tmp_path: Path):
    """Fix H (slice-077 M2): when the default branch cannot be resolved (no
    origin/HEAD AND no init.defaultBranch), --classify emits a
    `default-branch-unresolvable` error to stderr and exits 1 with no stdout.

    GIT_CONFIG_GLOBAL/SYSTEM are isolated to nonexistent paths so a machine-level
    `init.defaultBranch` cannot leak into the resolution and mask the error path.
    """
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    wt_path = tmp_path / "repo-wt" / "slice-077-test"
    _git("worktree", "add", str(wt_path), "-b", "slice/077-test", "master", cwd=repo_root)
    isolated = {
        "GIT_CONFIG_GLOBAL": str(tmp_path / "no-global-gitconfig"),
        "GIT_CONFIG_SYSTEM": str(tmp_path / "no-system-gitconfig"),
    }
    proc = _run_cli(
        "--classify", "slice-077-test", "--json", "--repo-root", str(repo_root),
        cwd=repo_root, extra_env=isolated,
    )
    assert proc.returncode == 1, (
        f"expected exit 1 for unresolvable default branch; got {proc.returncode}; "
        f"stdout={proc.stdout!r}"
    )
    assert not proc.stdout.strip(), (
        f"expected no stdout on the error path; got {proc.stdout!r}"
    )
    err_data = json.loads(proc.stderr.strip().splitlines()[0])
    assert err_data["action"] == "classify"
    assert "default-branch-unresolvable" in err_data["error"], (
        f"expected default-branch-unresolvable error token, got {err_data!r}"
    )
