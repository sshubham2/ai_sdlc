"""slice-089 — parallel-aware stale-branch classifier (ADR-081).

Per Critic B2 (APED-1): these tests exercise `classify_stale_branches` against a
REAL git repo with REAL `git worktree add` worktrees — NOT a stub that pre-strips
or pre-classifies. A stub would mask the meta-Critic B-add-1 raw-vs-short refname
set-key mismatch (the single most dangerous defect of this slice).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tools.stale_branch_classifier import classify_stale_branches, main

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _REPO_ROOT / "skills" / "commit-slice" / "SKILL.md"


# ----------------------------- git fixture helpers -----------------------------


def _git(cwd: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return out.stdout


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q", "-b", "master")
    _git(path, "config", "user.email", "t@t.test")
    _git(path, "config", "user.name", "Test")
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-q", "-m", "seed")
    return path


def _add_worktree(repo: Path, wt_path: Path, branch: str) -> None:
    """git worktree add <wt_path> -b <branch> (creates branch + live worktree)."""
    _git(repo, "worktree", "add", str(wt_path), "-b", branch)


def _add_orphan_branch(repo: Path, branch: str) -> None:
    """git branch <branch> (a local branch with NO worktree)."""
    _git(repo, "branch", branch)


# ----------------------------- the tests -----------------------------


def test_worktree_backed_slice_branch_is_allowed(tmp_path):
    repo = _init_repo(tmp_path / "main")
    _add_worktree(repo, tmp_path / "wt-101", "slice/101-foo")

    v = classify_stale_branches(repo)

    assert "slice/101-foo" in v.parallel_slices
    assert v.orphan_branches == []
    assert v.verdict == "allow"


def test_orphan_slice_branch_still_refused(tmp_path):
    repo = _init_repo(tmp_path / "main")
    _add_orphan_branch(repo, "slice/102-bar")  # no worktree

    v = classify_stale_branches(repo)

    assert v.orphan_branches == ["slice/102-bar"]
    assert v.parallel_slices == []
    assert v.verdict == "refuse"


def test_mixed_backed_and_orphan_refuses_on_the_orphan_only(tmp_path):
    repo = _init_repo(tmp_path / "main")
    _add_worktree(repo, tmp_path / "wt-101", "slice/101-foo")  # legit parallel
    _add_orphan_branch(repo, "slice/102-bar")  # genuine orphan

    v = classify_stale_branches(repo)

    assert v.parallel_slices == ["slice/101-foo"]
    assert v.orphan_branches == ["slice/102-bar"]
    assert v.verdict == "refuse"  # refuse iff ANY orphan, despite the legit peer


def test_worktree_backing_uses_short_form_not_raw_refname(tmp_path):
    """meta-Critic B-add-1: the porcelain parser returns the RAW refname
    `refs/heads/slice/...`; if the classifier failed to strip it to short form,
    the set-intersection with for-each-ref's short refs would be empty and the
    worktree-backed peer would false-classify as an orphan. Prove the strip."""
    repo = _init_repo(tmp_path / "main")
    _add_worktree(repo, tmp_path / "wt-101", "slice/101-foo")

    v = classify_stale_branches(repo)

    # short form present where expected ...
    assert "slice/101-foo" in v.parallel_slices
    # ... and NO raw-refname leaked into ANY field (the set-key-mismatch signature).
    for field in (v.parallel_slices, v.orphan_branches, v.noncanonical_backed):
        assert not any(b.startswith("refs/heads/") for b in field), field
    # the canonical regression: a backed peer must NOT be a false orphan.
    assert "slice/101-foo" not in v.orphan_branches


def test_noncanonical_named_worktree_backed_branch_allowed_not_orphan(tmp_path):
    """Critic B3: a worktree-backed branch with a non-canonical name (no -suffix,
    filtered out by detect_active_worktrees' _SLICE_BRANCH_RE) must be recognized
    as backed (ALLOW) — not silently dropped into the orphan set."""
    repo = _init_repo(tmp_path / "main")
    _add_worktree(repo, tmp_path / "wt-077", "slice/077")  # no -name suffix

    v = classify_stale_branches(repo)

    assert "slice/077" in v.parallel_slices
    assert "slice/077" in v.noncanonical_backed  # flagged for the rename hint
    assert "slice/077" not in v.orphan_branches  # NOT a false orphan
    assert v.verdict == "allow"


def test_current_slice_own_worktree_excluded_by_path(tmp_path):
    """Critic B1: run from the current slice's OWN worktree; it must not appear in
    parallel_slices NOR orphan_branches. A peer worktree still surfaces as parallel."""
    repo = _init_repo(tmp_path / "main")
    self_wt = tmp_path / "wt-089"
    _add_worktree(repo, self_wt, "slice/089-self")
    _add_worktree(repo, tmp_path / "wt-101", "slice/101-foo")

    v = classify_stale_branches(self_wt)  # cwd = the current slice's worktree

    assert v.current_branch == "slice/089-self"
    assert "slice/089-self" not in v.parallel_slices
    assert "slice/089-self" not in v.orphan_branches
    assert "slice/101-foo" in v.parallel_slices
    assert v.verdict == "allow"


def test_self_exclusion_branch_belt_covers_path_equality_miss(tmp_path, monkeypatch):
    """meta-Critic M-add-1: if path-equality self-exclusion slips (Windows case /
    8.3 / separator mismatch), the current-branch belt MUST still exclude self.
    Simulate a total path-equality failure by breaking _norm_path's determinism."""
    import tools.stale_branch_classifier as sbc

    repo = _init_repo(tmp_path / "main")
    self_wt = tmp_path / "wt-089"
    _add_worktree(repo, self_wt, "slice/089-self")
    _add_worktree(repo, tmp_path / "wt-101", "slice/101-foo")  # co-resident peer

    # Force path-equality to NEVER match: every call returns a distinct string.
    counter = {"n": 0}

    def _never_equal(p: str) -> str:
        counter["n"] += 1
        return f"{p}::{counter['n']}"

    monkeypatch.setattr(sbc, "_norm_path", _never_equal)

    v = classify_stale_branches(self_wt)

    # path-equality is now broken, yet the branch belt still excludes self ...
    assert "slice/089-self" not in v.parallel_slices
    assert "slice/089-self" not in v.orphan_branches
    # ... and is SURGICAL — the co-resident peer is NOT over-excluded (m2):
    assert "slice/101-foo" in v.parallel_slices


def test_zero_slice_branches_allows(tmp_path):
    """meta-Critic m-add-1 boundary: no slice/* refs at all -> allow, silent."""
    repo = _init_repo(tmp_path / "main")

    v = classify_stale_branches(repo)

    assert v.parallel_slices == []
    assert v.orphan_branches == []
    assert v.noncanonical_backed == []
    assert v.verdict == "allow"


def test_worktree_on_default_or_nonslice_branch_ignored(tmp_path):
    """meta-Critic m-add-1 boundary: the main worktree (master) and a non-slice
    feature worktree must NOT count as backing any slice, nor as orphans."""
    repo = _init_repo(tmp_path / "main")
    _add_worktree(repo, tmp_path / "wt-feature", "feature/x")  # non-slice branch

    v = classify_stale_branches(repo)

    assert v.parallel_slices == []
    assert v.orphan_branches == []
    assert v.verdict == "allow"


def test_cli_json_contract_and_exit_zero(tmp_path, capsys):
    """CSP-1: --json emits the action+verdict payload; exit 0 on success."""
    repo = _init_repo(tmp_path / "main")
    _add_orphan_branch(repo, "slice/102-bar")

    rc = main(["--repo-root", str(repo), "--json"])
    out = capsys.readouterr().out

    assert rc == 0
    import json as _json

    payload = _json.loads(out)
    assert payload["action"] == "classify-stale-branches"
    assert payload["verdict"] == "refuse"
    assert payload["orphan_branches"] == ["slice/102-bar"]


def test_cli_malformed_args_exit_2(capsys):
    """CSP-1: argparse rejects an unknown flag with exit 2 (malformed CLI args)."""
    with pytest.raises(SystemExit) as exc:
        main(["--no-such-flag"])
    assert exc.value.code == 2


# --------------- SKILL.md prose-parity tests (FBCD-1, Critic M2) ---------------

_BLOCK_RE = re.compile(
    r"<!-- STALE-BRANCH-CHECK:BEGIN -->(.*?)<!-- STALE-BRANCH-CHECK:END -->",
    re.DOTALL,
)


def _stale_check_blocks() -> list[str]:
    text = _SKILL.read_text(encoding="utf-8").replace("\r\n", "\n")
    return _BLOCK_RE.findall(text)


def test_merge_and_push_guardrails_symmetric():
    """Critic M2: BOTH the --merge and --push stale-branch surfaces invoke the
    one classifier — the block appears exactly twice (one per surface)."""
    blocks = _stale_check_blocks()
    assert len(blocks) == 2, f"expected 2 sentinel-delimited stale-check blocks, found {len(blocks)}"
    for b in blocks:
        assert "python -m tools.stale_branch_classifier" in b


def test_merge_and_push_stale_check_prose_byte_identical():
    """Critic M2.1 / FBCD-1: the two stale-check blocks are byte-identical
    (modulo EOL) so a future edit to one site that misses the other is caught."""
    blocks = _stale_check_blocks()
    assert len(blocks) == 2
    assert blocks[0] == blocks[1], "the two stale-branch-check blocks have diverged"
