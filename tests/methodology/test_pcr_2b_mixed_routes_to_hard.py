"""PCR-2b (slice-083 / ADR-075) AC#4 — MIXED routes through the HARD path with
NO partial SOFT auto-resolve (atomicity per ADR-069 MIXED row)."""

import subprocess

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.parallel_conflict_resolver as _pcr

# slice-110 / [[ADR-101]]: location-agnostic VAULT_ROOT pin (see autouse_pin).
_pin_vault = vi.autouse_pin(
    _vgit, _pcr,
    derived=[(_pcr, "_AUDIT_LOG_PATH",
              lambda vr: vr / "parallel-conflict-resolution-log.md")],
)

from tools.parallel_conflict_resolver import (
    ConflictClass,
    classify_conflict,
    diagnose_conflict,
    resolve_soft_conflict,
)


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True
    )


def _write(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_mixed_class_routes_through_hard_no_partial_soft(tmp_path):
    """A MIXED conflict (SOFT slice-queue.md + non-SOFT tools/foo.py both U)
    routes to STOP class MIXED; the SOFT file is NOT regenerated (atomicity)."""
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    _write(tmp_path, "architecture/slice-queue.md", "# stub\n")
    _write(tmp_path, "tools/foo.py", "# stub\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    _write(tmp_path, "architecture/slice-queue.md", "# queue A\n\n## Candidates\n")
    _write(tmp_path, "tools/foo.py", "A_IMPL = 1\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    _write(tmp_path, "architecture/slice-queue.md", "# queue B\n\n## Candidates\n")
    _write(tmp_path, "tools/foo.py", "B_IMPL = 2\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)

    diag = diagnose_conflict(tmp_path)
    assert classify_conflict(diag) is ConflictClass.MIXED
    result = resolve_soft_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.MIXED
    # Atomicity: SOFT slice-queue.md NOT regenerated.
    assert result.regenerated_files == ()
    # The SOFT file is left untouched (still carries conflict markers from rebase).
    queue_text = (tmp_path / "architecture" / "slice-queue.md").read_text(encoding="utf-8")
    assert "<<<<<<<" in queue_text
