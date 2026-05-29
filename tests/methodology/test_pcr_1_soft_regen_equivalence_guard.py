"""PCR-1 SOFT auto-regen equivalence guard — APED-1 empirical battery (slice-082 / R-21).

Closes R-21: PCR-1's SOFT auto-regen could emit content semantically different from a
manual-resolve baseline WITHOUT raising _SoftResolutionError, silently committing a wrong
resolution. ADR-074 adds `_verify_soft_equivalence` between the SOFT helpers' pending_writes
and the commit phase in `resolve_soft_conflict`; it proves the regenerated content is in a
deterministic equivalence class against both rebase stages along three invariants, else
fail-closed STOP (no writes).

These tests drive the REAL resolver against REAL tmp-repo rebase-conflict fixtures (APED-1
execution, not reasoned-about). Two of R-21's concrete silent-divergence vectors are
reproduced:
  - vector 1 (queue): malformed-block claim drop (`_overlay_claims_on_queue_text` :830-841)
  - vector 2 (shippability): discarded-prelude / non-numbered-row drop (`_merge_shippability` :1242)
"""
from __future__ import annotations

import pathlib
import subprocess

from tools.parallel_conflict_resolver import (
    ConflictClass,
    classify_conflict,
    diagnose_conflict,
    resolve_soft_conflict,
)

_AUDIT_LOG = "architecture/parallel-conflict-resolution-log.md"


# ---------------------------------------------------------------------------
# Fixture helpers (modeled on tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py)
# ---------------------------------------------------------------------------

def _git(tmp_path, *args, check=True):
    return subprocess.run(["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True)


def _stage_rebase(tmp_path, rel_path: str, *, branchA: str, master: str):
    """Build a tmp git repo with a rebase-in-progress conflict on rel_path.

    `branchA` content is committed on branchA; `master` content on master; then
    `git rebase master` (while on branchA) conflicts. EMPIRICALLY (verified, not
    assumed): after the conflict `git show :2:` returns the `master` content and
    `git show :3:` returns the `branchA` content — and `_regen_slice_queue` uses
    stage-3 as the overlay BASELINE. So: **branchA == stage 3 == the regen baseline**;
    **master == stage 2 == the claim-source merged in via _merge_claim_dicts**. Tests
    name args by branch to avoid the stage-number inversion trap.
    Base content is a minimal stub so both branches' full rewrites conflict.
    """
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
    # Rebase onto master → conflict on rel_path (both rewrote it from the stub).
    _git(tmp_path, "rebase", "master", check=False)


def _candidate(name: str, *, claimed_by: str | None = None, claimed_at: str | None = None,
               risk_retired: bool = True) -> str:
    """One PSQ-1 candidate block. risk_retired=False omits the Risk-retired line
    (the malformed-block shape that drops claims at _overlay_claims_on_queue_text)."""
    lines = [
        f"### {name}\n",
        "- **Source:** synthetic\n",
        "- **Blast-radius:** `nothing`\n",
        "- **Parallel-safety:** NON-OVERLAPPING\n",
        "- **Effort:** SMALL\n",
    ]
    if risk_retired:
        lines.append("- **Risk-retired:** LOW\n")
    if claimed_by and claimed_at:
        lines.append(f"- **Claimed-by:** {claimed_by}\n")
        lines.append(f"- **Claimed-at:** {claimed_at}\n")
    return "".join(lines)


def _queue(*candidate_blocks: str) -> str:
    return "# Slice queue\n\n## Candidates\n\n" + "\n".join(candidate_blocks)


def _shippability(prelude_extra: str = "", rows: tuple[str, ...] = ()) -> str:
    head = (
        "# Shippability catalog\n\n"
        "Single source of truth for must-never-regress claims.\n\n"
    )
    if prelude_extra:
        head += prelude_extra + "\n\n"
    head += "| # | Claim | Command |\n|---|-------|---------|\n"
    body = "".join(r if r.endswith("\n") else r + "\n" for r in rows)
    return head + body


def _resolve(tmp_path):
    diag = diagnose_conflict(tmp_path)
    return diag, resolve_soft_conflict(diag, tmp_path)


# ---------------------------------------------------------------------------
# AC-1 — reproduce R-21 corner case (vector 1): malformed-block claim drop
# ---------------------------------------------------------------------------

def test_corner_case_soft_regen_diverges_from_baseline(tmp_path) -> None:
    """R-21 vector 1: stage-2 claims `add-foo`; baseline (stage-3) `add-foo` block is
    missing its `- **Risk-retired:**` line, so `_overlay_claims_on_queue_text` silently
    drops the claim (stderr warn only) and the pre-guard resolver returns APPLIED with
    divergent content. POST-FIX the equivalence guard must STOP. RED before the guard.
    """
    # branchA == regen baseline: add-foo block MALFORMED (no Risk-retired) → overlay can't
    # re-insert the merged claim → claim silently dropped.
    branchA = _queue(
        _candidate("add-foo", risk_retired=False),
        _candidate("add-bar"),
    )
    # master == stage-2 claim source: add-foo CLAIMED well-formed → claim enters merged_claims.
    master = _queue(
        _candidate("add-foo", claimed_by="alice <a@example.com>",
                   claimed_at="2026-05-29T12:00:00+00:00"),
        _candidate("add-bar"),
    )
    _stage_rebase(tmp_path, "architecture/slice-queue.md", branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    # The divergence (add-foo's claim lost) must fail-closed to STOP, not silently APPLY.
    assert result.action == "STOP", (
        "R-21: malformed-block claim drop must STOP, not silently APPLY divergent content"
    )
    assert "equivalence-guard" in (result.reason or "")


def test_trailing_whitespace_heading_still_stops(tmp_path) -> None:
    """M1 (code-Critic): a baseline `### add-foo ` heading with a trailing space must NOT
    bypass invariant #1. The guard's heading regex strips to match the canonical rstripped
    parser, so the dropped claim is still caught → STOP. (Pre-fix this false-passed because
    `'add-foo '` never intersected the rstripped claimed_names.)"""
    # branchA == baseline: malformed add-foo (no Risk-retired) AND a trailing-space heading.
    branchA = _queue("### add-foo \n"  # NOTE the trailing space after the name
                     "- **Source:** synthetic\n"
                     "- **Blast-radius:** `nothing`\n"
                     "- **Parallel-safety:** NON-OVERLAPPING\n"
                     "- **Effort:** SMALL\n")
    master = _queue(_candidate("add-foo", claimed_by="alice <a@example.com>",
                               claimed_at="2026-05-29T12:00:00+00:00"))
    _stage_rebase(tmp_path, "architecture/slice-queue.md", branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "STOP", (
        "M1: a trailing-whitespace baseline heading must not bypass the claim-preservation guard"
    )
    assert "equivalence-guard" in (result.reason or "")


# ---------------------------------------------------------------------------
# AC-2 — guard fail-closes on unprovable equivalence (vector 2: prelude drop)
# ---------------------------------------------------------------------------

def test_equivalence_guard_stops_on_unprovable_equivalence(tmp_path) -> None:
    """R-21 vector 2: a non-numbered (prelude) line unique to stage-2 is lost because
    `_merge_shippability` keeps only stage-3's prelude. The symmetric invariant #3
    (M1) detects the cross-stage prelude divergence → STOP."""
    # stage-2 carries an extra non-numbered annotated row that fails the bare-int regex.
    branchA = _shippability(prelude_extra="| 5,6 | combined-slice claim | pytest -k combined |",
                            rows=("| 80 | claim80 | cmd80 |",))
    master = _shippability(rows=("| 80 | claim80 | cmd80 |",))
    _stage_rebase(tmp_path, "architecture/shippability.md", branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "STOP"
    assert "equivalence-guard" in (result.reason or "")


def test_stop_leaves_repo_state_unmutated(tmp_path) -> None:
    """A guard-STOP must not write the U-file, stage anything, or complete the rebase
    (atomicity per ADR-069). After STOP: U-file still has conflict markers, rebase still
    in progress."""
    branchA = _queue(_candidate("add-foo", risk_retired=False))
    master = _queue(_candidate("add-foo", claimed_by="alice <a@example.com>",
                               claimed_at="2026-05-29T12:00:00+00:00"))
    _stage_rebase(tmp_path, "architecture/slice-queue.md", branchA=branchA, master=master)
    _, result = _resolve(tmp_path)
    assert result.action == "STOP"
    # Rebase still in progress (not continued).
    assert (tmp_path / ".git" / "rebase-merge").exists() or (tmp_path / ".git" / "rebase-apply").exists()
    # Working-tree U-file still carries conflict markers (not overwritten by overlay).
    content = (tmp_path / "architecture" / "slice-queue.md").read_text(encoding="utf-8")
    assert "<<<<<<<" in content and ">>>>>>>" in content
    assert result.regenerated_files == ()


# ---------------------------------------------------------------------------
# AC-3 — guard STOP is recorded in the audit log with a structured reason
# ---------------------------------------------------------------------------

def test_guard_stop_logged_with_structured_reason(tmp_path) -> None:
    branchA = _queue(_candidate("add-foo", risk_retired=False))
    master = _queue(_candidate("add-foo", claimed_by="alice <a@example.com>",
                               claimed_at="2026-05-29T12:00:00+00:00"))
    _stage_rebase(tmp_path, "architecture/slice-queue.md", branchA=branchA, master=master)
    _, result = _resolve(tmp_path)
    assert result.action == "STOP"
    log = (tmp_path / _AUDIT_LOG).read_text(encoding="utf-8")
    assert "equivalence-guard STOP" in log
    assert "equivalence-guard" in log


# ---------------------------------------------------------------------------
# AC-4 / M-add-1 — happy path: equivalence holds → guard transparent (no false-STOP),
# including a MIX of claimed + unclaimed candidates (unclaimed must NOT trip invariant #1).
# ---------------------------------------------------------------------------

def test_happy_path_equivalence_holds_guard_transparent(tmp_path) -> None:
    """When the regen is faithful, the guard is transparent — resolver still APPLIES.
    The queue mixes a claimed candidate (well-formed, claim preserved) with unclaimed
    candidates; invariant #1's domain is the CLAIMED subset only (M-add-1), so the
    unclaimed candidates do not false-STOP."""
    claim = dict(claimed_by="alice <a@example.com>", claimed_at="2026-05-29T12:00:00+00:00")
    # branchA == baseline: add-foo well-formed + claimed → overlay preserves the claim.
    branchA = _queue(
        _candidate("add-foo", **claim),   # well-formed claimed block (Risk-retired present)
        _candidate("add-bar"),            # unclaimed
    )
    master = _queue(
        _candidate("add-foo", **claim),   # same claim, well-formed
        _candidate("add-baz"),            # unclaimed, different trailing candidate → conflict
    )
    _stage_rebase(tmp_path, "architecture/slice-queue.md", branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "APPLIED", (
        "M-add-1: unclaimed candidates must not false-STOP a faithful regen"
    )
    # add-foo's claim survived into the resolved file.
    resolved = (tmp_path / "architecture" / "slice-queue.md").read_text(encoding="utf-8")
    assert "alice <a@example.com>" in resolved


def test_shippability_happy_path_guard_transparent(tmp_path) -> None:
    """Symmetric invariant #3 (M1) does NOT false-STOP when both stages share an
    identical (branch-invariant) prelude — only the numbered rows differ."""
    branchA = _shippability(rows=("| 80 | c80 | x80 |", "| 81 | c81 | x81 |"))
    master = _shippability(rows=("| 80 | c80 | x80 |", "| 82 | c82 | x82 |"))
    _stage_rebase(tmp_path, "architecture/shippability.md", branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "APPLIED"
    resolved = (tmp_path / "architecture" / "shippability.md").read_text(encoding="utf-8")
    # row-union: all three numbered rows present.
    assert "| 80 |" in resolved and "| 81 |" in resolved and "| 82 |" in resolved


# ---------------------------------------------------------------------------
# M2 — cross-stage claim drop is LOUD (audit-warn) but NOT a STOP (preserves happy path)
# ---------------------------------------------------------------------------

def test_cross_stage_claim_drop_warns_not_stops(tmp_path, capfd) -> None:
    """A claimed candidate present in stage-2 but legitimately dropped from the baseline
    (top-10 churn) is an EXPECTED orphan drop — the resolver must still APPLY (no false-STOP),
    but emit a loud cross-stage-claim-drop warning so the truncated-baseline case is observable.
    """
    # branchA == baseline legitimately dropped add-foo (fell off top-10); only add-bar/add-baz.
    branchA = _queue(_candidate("add-bar"), _candidate("add-baz"))
    # master == stage-2 still claims add-foo → add-foo enters merged_claims as a claimed orphan.
    master = _queue(
        _candidate("add-foo", claimed_by="alice <a@example.com>",
                   claimed_at="2026-05-29T12:00:00+00:00"),
        _candidate("add-bar"),
    )
    _stage_rebase(tmp_path, "architecture/slice-queue.md", branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "APPLIED", "legitimate top-10 churn must not false-STOP"
    err = capfd.readouterr().err
    assert "cross-stage-claim-drop" in err and "add-foo" in err


# ---------------------------------------------------------------------------
# AC-5 — the equivalence guard is pinned in the shippability catalog (must-never-regress)
# ---------------------------------------------------------------------------

def test_shippability_pins_equivalence_guard() -> None:
    """AC-5: `architecture/shippability.md` carries a row whose Command targets this
    guard's test module, so R-21's corner-class can never silently regress."""
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    catalog = (repo_root / "architecture" / "shippability.md").read_text(encoding="utf-8")
    rows = [ln for ln in catalog.splitlines()
            if ln.startswith("|") and "slice-082-harden-pcr-1-soft-regen-corner-case" in ln]
    assert rows, "shippability.md has no row for slice-082"
    assert any("test_pcr_1_soft_regen_equivalence_guard.py" in ln for ln in rows), (
        "slice-082 shippability row(s) do not pin the equivalence-guard test"
    )
