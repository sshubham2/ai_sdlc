"""PCR-2b (slice-083 / ADR-075) — HARD/MIXED dispatch + fail-closed gate entry.

Drives the REAL resolver against REAL tmp-repo rebase-conflict fixtures (APED-1
empirical-execution discipline): a HARD-class conflict must STOP (never
auto-continue), and the SOFT->HARD shippability-escalation path must surface a
conflict_class the skill's gate-flow entry keys on.
"""

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
    resolve_hard_conflict,
    resolve_soft_conflict,
)


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True
    )


def _init_repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")


def _stage_rebase(tmp_path, rel_path, *, branchA, master):
    """Build a tmp repo with a rebase-in-progress conflict on rel_path."""
    _init_repo(tmp_path)
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


def _rebase_in_progress(tmp_path) -> bool:
    return (tmp_path / ".git" / "rebase-merge").exists() or (
        tmp_path / ".git" / "rebase-apply"
    ).exists()


def test_hard_conflict_fail_closes_to_stop_when_unratified(tmp_path):
    """A HARD-class conflict (source file) STOPs without auto-continuing.

    PCR-2b never auto-merges HARD; the resolver returns STOP and leaves the
    rebase in progress for the skill's gate-on-hand-resolve flow.
    """
    _stage_rebase(tmp_path, "tools/foo.py", branchA="A_IMPL = 1\n", master="B_IMPL = 2\n")
    diag = diagnose_conflict(tmp_path)
    assert classify_conflict(diag) is ConflictClass.HARD
    result = resolve_soft_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.HARD
    assert result.regenerated_files == ()
    # No auto-continue: rebase is still in progress (gate-on-hand-resolve).
    assert _rebase_in_progress(tmp_path)
    # The STOP carries gate context (not a bare deferral) so the skill can route.
    assert "gate-on-hand-resolve" in (result.reason or "")


def test_resolve_hard_conflict_returns_gate_context_stop(tmp_path):
    """resolve_hard_conflict is the upfront dispatch target; returns STOP with
    the TRI-RESOLVE-1 gate context (bootstrap-fallback equivalence: a
    helper-present HARD result is STOP, identical-in-safety to the pre-PCR-2b
    bare SOAD-1 STOP — never auto-continues)."""
    _stage_rebase(tmp_path, "agents/some.md", branchA="A\n", master="B\n")
    diag = diagnose_conflict(tmp_path)
    result = resolve_hard_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.HARD
    assert "TRI-RESOLVE-1" in (result.reason or "")
    assert _rebase_in_progress(tmp_path)


def test_soft_to_hard_shippability_escalation_enters_gate(tmp_path):
    """A SOFT-looking shippability.md conflict that escalates to HARD mid-loop
    (same slice-number, different row content) surfaces conflict_class=HARD via
    the resolver's _SoftResolutionError(HARD) leg — the skill keys the gate-flow
    entry on (action==STOP AND conflict_class in {HARD,MIXED}) so this path is
    covered without passing through resolve_hard_conflict (design.md M2)."""
    header = "# Shippability\n\n| # | Slice | Claim | Command |\n|---|---|---|---|\n"
    branchA = header + "| 5 | slice-005 | claim-A | cmd-A |\n"
    master = header + "| 5 | slice-005 | claim-B-different | cmd-B |\n"
    _stage_rebase(tmp_path, "architecture/shippability.md", branchA=branchA, master=master)
    diag = diagnose_conflict(tmp_path)
    # Sole U-file is shippability.md (SOFT-set member) -> classify SOFT...
    assert classify_conflict(diag) is ConflictClass.SOFT
    # ...but _merge_shippability escalates same-number-different-content to HARD.
    result = resolve_soft_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.HARD
    # Atomicity: no SOFT file written (the escalation raised before any flush).
    assert result.regenerated_files == ()
    assert _rebase_in_progress(tmp_path)
