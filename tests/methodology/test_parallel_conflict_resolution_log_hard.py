"""PCR-2b (slice-083 / ADR-075) AC#5 — HARD audit-log section + `_index.md`-sole.

Drives _record_hard_resolution (the `--record-hard-resolution` core) and asserts
the `## Hard-conflict resolution - <ISO>` section is appended with the uniform
hyphen-space separator + verdict + TRI-RESOLVE-1 disposition fields. Also
exercises the dominant `_index.md`-sole HARD scenario (M4 fix).
"""

import subprocess

from tools.parallel_conflict_resolver import (
    ConflictClass,
    ConflictDiagnostic,
    classify_conflict,
    diagnose_conflict,
    resolve_soft_conflict,
    _record_hard_resolution,
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


def test_hard_conflict_audit_section_appended(tmp_path):
    _stage_rebase(tmp_path, "tools/foo.py", branchA="a = 1\n", master="b = 2\n")
    diag = diagnose_conflict(tmp_path)
    _record_hard_resolution(
        tmp_path, diag, verdict="CLEAN (no blockers)", disposition="apply"
    )
    log = (tmp_path / "architecture" / "parallel-conflict-resolution-log.md").read_text(
        encoding="utf-8"
    )
    # Uniform hyphen-space separator; section-type by prefix word.
    assert "## Hard-conflict resolution - " in log
    assert "**code-review verdict**: CLEAN (no blockers)" in log
    assert "**TRI-RESOLVE-1 disposition**: apply" in log
    assert "gate-on-hand-resolve (PCR-2b)" in log
    # U-files captured (recorded mid-rebase, before continue).
    assert "tools/foo.py" in log


def test_index_md_sole_hard_scenario_drives_gate(tmp_path):
    """The dominant real HARD case (M4): an `_index.md`-sole conflict classifies
    HARD (never SOFT — Haiku-regen) and routes to the gate STOP."""
    _stage_rebase(
        tmp_path,
        "architecture/slices/_index.md",
        branchA="# Slices Index\n\nA-lessons\n",
        master="# Slices Index\n\nB-lessons\n",
    )
    diag = diagnose_conflict(tmp_path)
    assert classify_conflict(diag) is ConflictClass.HARD
    result = resolve_soft_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.HARD
    assert result.regenerated_files == ()
