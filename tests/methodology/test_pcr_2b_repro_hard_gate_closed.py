"""PCR-2b (slice-083 / ADR-075) AC#5 repro — the HARD gate is closed.

Confirms PCR-2b ships a real gate (not the pre-slice-083 bare deferral): a
HARD-class conflict returns a STOP ResolutionResult whose reason names the
gate-on-hand-resolve flow + TRI-RESOLVE-1, and resolve_hard_conflict NEVER
auto-continues the rebase.
"""

import subprocess

from tools.parallel_conflict_resolver import (
    ConflictClass,
    diagnose_conflict,
    resolve_hard_conflict,
)


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True
    )


def _stage_rebase(tmp_path, rel_path, *, branchA, master):
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# stub\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    target.write_text(branchA, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    target.write_text(master, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)


def test_hard_gate_closed_returns_stop_resolution_result(tmp_path):
    _stage_rebase(
        tmp_path,
        "methodology-changelog.md",
        branchA="## v0.77.0 — A\n",
        master="## v0.77.0 — B\n",
    )
    diag = diagnose_conflict(tmp_path)
    result = resolve_hard_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.HARD
    reason = result.reason or ""
    assert "gate-on-hand-resolve" in reason
    assert "TRI-RESOLVE-1" in reason
    assert "never auto-merges" in reason.lower()
    # Never auto-continues — rebase still in progress.
    assert (tmp_path / ".git" / "rebase-merge").exists() or (
        tmp_path / ".git" / "rebase-apply"
    ).exists()
