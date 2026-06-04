"""PCR-2a vault-claim resolver tests (slice-078 / ADR-071).

Per AC#1 mission-brief rows: ``resolve_vault_claim_conflict`` returns a
``ResolutionResult`` whose preserved identity is the strictly-newer
``Claimed-at`` winner regardless of which stage (2 or 3) holds the
winner. Auto-re-picks the loser's replacement from the post-overlay
in-memory queue text (per M-add-2 — NOT disk-read during VAULT_CLAIM
rebase-in-progress). Defensive post-overlay verification catches
silent-drop on malformed candidate blocks (per M-add-1).

Tests exercise predicates + integration via in-memory queue fixtures.
The full integration path (atomic write + git rebase --continue + audit
log append) is covered by test_pcr_2a_regen_slice_queue_dispatch.py.
"""
from __future__ import annotations

import subprocess

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.parallel_conflict_resolver as _pcr

# slice-110 / [[ADR-101]]: setattr-pin VAULT_ROOT (in-tree relative) on the
# resolver + _vault_git (vault_is_external gate) + re-derive frozen _AUDIT_LOG_PATH
# so the resolver reads/writes the test's own tmp fixtures under default AND an
# external AI_SDLC_VAULT_ROOT override (the flip simulation).
_pin_vault = vi.autouse_pin(
    _vgit, _pcr,
    derived=[(_pcr, "_AUDIT_LOG_PATH",
              lambda vr: vr / "parallel-conflict-resolution-log.md")],
)

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    ResolutionResult,
    _collect_same_candidate_different_identity,
    _has_same_candidate_different_identity,
    _parse_queue_candidates_for_replacement,
    _pick_loser_replacement,
    _select_timestamp_winner,
    resolve_vault_claim_conflict,
)


# ---------------------------------------------------------------------------
# Fixtures + helpers
# ---------------------------------------------------------------------------

def _claim(name: str, by: str, at: str, stage: int) -> ClaimEntry:
    return ClaimEntry(
        candidate_name=name,
        claimed_by=by,
        claimed_at=at,
        branch_stage=stage,
    )


def _queue_text(candidates: list[dict]) -> str:
    """Synthesize a slice-queue.md text with N candidates.

    Each candidate dict carries: name, parallel_safety (default NON-OVERLAPPING),
    claimed_by (optional, defaults to None = unclaimed).
    """
    parts = ["# Slice queue\n\n## Candidates\n"]
    for c in candidates:
        block = [f"\n### {c['name']}\n"]
        block.append(f"\n- **Source:** synthetic\n")
        block.append(f"- **Blast-radius:** `nothing`\n")
        block.append(f"- **Parallel-safety:** {c.get('parallel_safety', 'NON-OVERLAPPING')}\n")
        block.append(f"- **Effort:** SMALL\n")
        block.append(f"- **Risk-retired:** LOW\n")
        if c.get("claimed_by"):
            block.append(f"- **Claimed-by:** {c['claimed_by']}\n")
            block.append(f"- **Claimed-at:** {c.get('claimed_at', '2026-05-29T12:00:00+00:00')}\n")
        parts.append("".join(block))
    return "".join(parts)


# ---------------------------------------------------------------------------
# AC#1 — _collect_same_candidate_different_identity (m2 helper)
# ---------------------------------------------------------------------------

def test_collect_returns_empty_when_no_collision() -> None:
    """No same-candidate-different-identity pairs → empty list."""
    history = (
        _claim("add-foo", "alice <alice@example.com>", "2026-05-29T10:00:00+00:00", 2),
        _claim("add-bar", "bob <bob@example.com>", "2026-05-29T11:00:00+00:00", 3),
    )
    assert _collect_same_candidate_different_identity(history) == []
    # bool-wrapper preserves API for classify_conflict consumer
    assert _has_same_candidate_different_identity(history) is False


def test_collect_returns_single_collision() -> None:
    """One same-candidate-different-identity collision → list of 1."""
    history = (
        _claim("add-foo", "alice <alice@example.com>", "2026-05-29T10:00:00+00:00", 2),
        _claim("add-foo", "bob <bob@example.com>", "2026-05-29T11:00:00+00:00", 3),
    )
    collisions = _collect_same_candidate_different_identity(history)
    assert len(collisions) == 1
    name, e2, e3 = collisions[0]
    assert name == "add-foo"
    assert e2.branch_stage == 2 and e3.branch_stage == 3
    assert _has_same_candidate_different_identity(history) is True


def test_collect_returns_multiple_collisions() -> None:
    """N>1 collisions surface for multi-candidate STOP path."""
    history = (
        _claim("add-foo", "alice <a@example.com>", "2026-05-29T10:00:00+00:00", 2),
        _claim("add-foo", "bob <b@example.com>", "2026-05-29T11:00:00+00:00", 3),
        _claim("add-bar", "carol <c@example.com>", "2026-05-29T10:30:00+00:00", 2),
        _claim("add-bar", "dave <d@example.com>", "2026-05-29T11:30:00+00:00", 3),
    )
    collisions = _collect_same_candidate_different_identity(history)
    assert len(collisions) == 2
    assert {c[0] for c in collisions} == {"add-foo", "add-bar"}


# ---------------------------------------------------------------------------
# AC#1 — _select_timestamp_winner (strict-newer + tie + multi STOP sentinels)
# ---------------------------------------------------------------------------

def test_timestamp_winner_when_newer_in_stage_3() -> None:
    """Strict-newer winner identification when newer claim is in rebase-target (stage 3)."""
    e2 = _claim("add-foo", "alice <a@example.com>", "2026-05-29T10:00:00+00:00", 2)
    e3 = _claim("add-foo", "bob <b@example.com>", "2026-05-29T11:00:00+00:00", 3)
    result = _select_timestamp_winner([("add-foo", e2, e3)])
    assert result is not None
    winner, loser = result
    assert winner is e3, "stage-3 has strictly-newer Claimed-at; must win"
    assert loser is e2


def test_timestamp_winner_when_newer_in_stage_2() -> None:
    """Strict-newer winner identification when newer claim is in slice-branch (stage 2).

    Critical: without this case, the M4 fix (winner-identity-written-regardless-of-stage)
    is unverified — `_regen_slice_queue:614` defaults baseline_text=text_3 which
    would silently demote a stage-2 winner.
    """
    e2 = _claim("add-foo", "alice <a@example.com>", "2026-05-29T12:00:00+00:00", 2)
    e3 = _claim("add-foo", "bob <b@example.com>", "2026-05-29T11:00:00+00:00", 3)
    result = _select_timestamp_winner([("add-foo", e2, e3)])
    assert result is not None
    winner, loser = result
    assert winner is e2, "stage-2 has strictly-newer Claimed-at; must win"
    assert loser is e3


def test_claimed_at_tie_returns_none() -> None:
    """Equal Claimed-at → strict-newer rule yields no winner → STOP sentinel (None)."""
    same_ts = "2026-05-29T10:00:00+00:00"
    e2 = _claim("add-foo", "alice <a@example.com>", same_ts, 2)
    e3 = _claim("add-foo", "bob <b@example.com>", same_ts, 3)
    result = _select_timestamp_winner([("add-foo", e2, e3)])
    assert result is None, "claimed_at-tie defers to PCR-2b — no auto-winner"


# ---------------------------------------------------------------------------
# AC#1 — _parse_queue_candidates_for_replacement (B1 file-local parser)
# ---------------------------------------------------------------------------

def test_parse_queue_extracts_name_safety_claimed() -> None:
    """Parser surfaces per-candidate (name, parallel_safety, is_claimed) in file order."""
    text = _queue_text([
        {"name": "add-foo", "parallel_safety": "NON-OVERLAPPING"},
        {"name": "add-bar", "parallel_safety": "OVERLAPS-WITH-slice-077"},
        {"name": "add-baz", "parallel_safety": "NON-OVERLAPPING", "claimed_by": "alice <a@example.com>"},
    ])
    candidates = _parse_queue_candidates_for_replacement(text)
    assert candidates == [
        ("add-foo", "NON-OVERLAPPING", False),
        ("add-bar", "OVERLAPS-WITH-slice-077", False),
        ("add-baz", "NON-OVERLAPPING", True),
    ]


def test_parse_queue_returns_empty_on_empty_text() -> None:
    """Empty queue text yields empty candidate list."""
    assert _parse_queue_candidates_for_replacement("") == []
    assert _parse_queue_candidates_for_replacement("# Slice queue\n\n## Candidates\n") == []


# ---------------------------------------------------------------------------
# AC#1 — _pick_loser_replacement (in-memory text input per M-add-2)
# ---------------------------------------------------------------------------

def test_loser_auto_re_pick_returns_highest_priority_unclaimed_non_overlapping() -> None:
    """Pick first candidate (file-order = priority) that is NON-OVERLAPPING + unclaimed."""
    text = _queue_text([
        {"name": "add-foo", "parallel_safety": "NON-OVERLAPPING", "claimed_by": "alice <a@example.com>"},
        {"name": "add-bar", "parallel_safety": "OVERLAPS-WITH-slice-077"},
        {"name": "add-baz", "parallel_safety": "NON-OVERLAPPING"},
        {"name": "add-qux", "parallel_safety": "NON-OVERLAPPING"},
    ])
    result = _pick_loser_replacement(queue_text=text, exclude_names=set())
    assert result == "add-baz", "first unclaimed NON-OVERLAPPING wins (add-foo claimed; add-bar overlapping)"


def test_loser_auto_re_pick_skips_claimed_candidates() -> None:
    """Already-claimed candidates skipped regardless of file-order priority."""
    text = _queue_text([
        {"name": "add-foo", "parallel_safety": "NON-OVERLAPPING", "claimed_by": "alice <a@example.com>"},
        {"name": "add-bar", "parallel_safety": "NON-OVERLAPPING", "claimed_by": "bob <b@example.com>"},
        {"name": "add-baz", "parallel_safety": "NON-OVERLAPPING"},
    ])
    result = _pick_loser_replacement(queue_text=text, exclude_names=set())
    assert result == "add-baz"


def test_loser_auto_re_pick_skips_non_parallel_safe_candidates() -> None:
    """Parallel-safety != NON-OVERLAPPING skipped (UNKNOWN-NO-GRAPH, OVERLAPS-WITH-*, etc.)."""
    text = _queue_text([
        {"name": "add-foo", "parallel_safety": "OVERLAPS-WITH-slice-077"},
        {"name": "add-bar", "parallel_safety": "UNKNOWN-NO-GRAPH"},
        {"name": "add-baz", "parallel_safety": "UNKNOWN-NO-HINT-FILES"},
        {"name": "add-qux", "parallel_safety": "NON-OVERLAPPING"},
    ])
    result = _pick_loser_replacement(queue_text=text, exclude_names=set())
    assert result == "add-qux"


def test_loser_auto_re_pick_skips_exclude_names() -> None:
    """exclude_names set blocks the winner's own candidate from being re-picked."""
    text = _queue_text([
        {"name": "add-winner", "parallel_safety": "NON-OVERLAPPING"},
        {"name": "add-other", "parallel_safety": "NON-OVERLAPPING"},
    ])
    result = _pick_loser_replacement(
        queue_text=text, exclude_names={"add-winner"}
    )
    assert result == "add-other"


def test_no_available_when_queue_empty() -> None:
    """Empty queue → None (audit-row sentinel 'none-available')."""
    assert _pick_loser_replacement(queue_text="", exclude_names=set()) is None


def test_no_available_when_all_overlapping() -> None:
    """All candidates non-parallel-safe → None."""
    text = _queue_text([
        {"name": "add-foo", "parallel_safety": "OVERLAPS-WITH-slice-077"},
        {"name": "add-bar", "parallel_safety": "UNKNOWN-NO-GRAPH"},
    ])
    assert _pick_loser_replacement(queue_text=text, exclude_names=set()) is None


def test_no_available_when_all_claimed() -> None:
    """All NON-OVERLAPPING candidates already claimed → None."""
    text = _queue_text([
        {"name": "add-foo", "parallel_safety": "NON-OVERLAPPING", "claimed_by": "alice <a@example.com>"},
        {"name": "add-bar", "parallel_safety": "NON-OVERLAPPING", "claimed_by": "bob <b@example.com>"},
    ])
    assert _pick_loser_replacement(queue_text=text, exclude_names=set()) is None


def _diag(
    u_files: tuple[str, ...] = (),
    claim_history: tuple[ClaimEntry, ...] = (),
) -> ConflictDiagnostic:
    return ConflictDiagnostic(
        u_files=u_files,
        concerned_slices={},
        claim_history=claim_history,
    )


def _stage_rebase_with_queue_collision(
    tmp_path,
    text_2: str,
    text_3: str,
) -> "tuple[ConflictDiagnostic, str]":
    """Initialize a tmp git repo + simulate a rebase-in-progress on slice-queue.md.

    Returns (diag, repo_root_str) — the diag carries the collision pair.
    """
    subprocess.run(["git", "init", "-q", "-b", "master"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "architecture").mkdir()
    qpath = tmp_path / "architecture" / "slice-queue.md"
    qpath.write_text("# Slice queue\n\n## Candidates\n", encoding="utf-8")
    subprocess.run(["git", "add", "architecture/slice-queue.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)

    # Create branch A (slice/078) with text_2
    subprocess.run(["git", "checkout", "-q", "-b", "branchA"], cwd=tmp_path, check=True)
    qpath.write_text(text_2, encoding="utf-8")
    subprocess.run(["git", "add", "architecture/slice-queue.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "A"], cwd=tmp_path, check=True)

    # Create branch B (master tip) with text_3
    subprocess.run(["git", "checkout", "-q", "master"], cwd=tmp_path, check=True)
    qpath.write_text(text_3, encoding="utf-8")
    subprocess.run(["git", "add", "architecture/slice-queue.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "B"], cwd=tmp_path, check=True)

    # Rebase A onto master -> conflict (text_2 vs text_3 on same lines)
    subprocess.run(["git", "checkout", "-q", "branchA"], cwd=tmp_path, check=True)
    proc = subprocess.run(["git", "rebase", "master"], cwd=tmp_path, capture_output=True)
    # Expect failure (conflict) — but rebase is now in progress with stage 2 + stage 3 populated
    return tmp_path


def test_claimed_at_tie_returns_stop(tmp_path) -> None:
    """Equal Claimed-at across the collision pair → ResolutionResult(STOP, VAULT_CLAIM)."""
    same_ts = "2026-05-29T10:00:00+00:00"
    diag = _diag(
        u_files=("architecture/slice-queue.md",),
        claim_history=(
            _claim("add-foo", "alice <a@example.com>", same_ts, 2),
            _claim("add-foo", "bob <b@example.com>", same_ts, 3),
        ),
    )
    result = resolve_vault_claim_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class == ConflictClass.VAULT_CLAIM
    assert "tie" in result.reason.lower(), f"reason should cite tie; got {result.reason!r}"


def test_multi_candidate_collision_returns_stop(tmp_path) -> None:
    """N>1 same-candidate-different-identity collisions → STOP deferring to PCR-2b."""
    diag = _diag(
        u_files=("architecture/slice-queue.md",),
        claim_history=(
            _claim("add-foo", "alice <a@example.com>", "2026-05-29T10:00:00+00:00", 2),
            _claim("add-foo", "bob <b@example.com>", "2026-05-29T11:00:00+00:00", 3),
            _claim("add-bar", "carol <c@example.com>", "2026-05-29T10:30:00+00:00", 2),
            _claim("add-bar", "dave <d@example.com>", "2026-05-29T11:30:00+00:00", 3),
        ),
    )
    result = resolve_vault_claim_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class == ConflictClass.VAULT_CLAIM
    assert "multi-candidate" in result.reason.lower()


def test_no_collision_diag_returns_unknown_stop(tmp_path) -> None:
    """Caller misuse: VAULT_CLAIM dispatched but claim_history has no collision pair."""
    diag = _diag(
        u_files=("architecture/slice-queue.md",),
        claim_history=(),
    )
    result = resolve_vault_claim_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class == ConflictClass.UNKNOWN
    assert "disagree" in result.reason.lower() or "fail-closed" in result.reason.lower()


def test_overlay_silently_dropped_returns_stop(tmp_path) -> None:
    """M-add-1: post-overlay defensive regex must catch silent-drop of winner claim.

    Fixture: stage 3 has a candidate block that LACKS the canonical
    `- **Risk-retired:**` pivot line. _overlay_claims_on_queue_text walks
    line-by-line and only inserts new Claimed-by/Claimed-at AFTER seeing
    Risk-retired; without it, the new claim is silently dropped.
    """
    # Malformed stage 3 baseline — candidate block lacks Risk-retired pivot
    text_3 = (
        "# Slice queue\n\n## Candidates\n\n"
        "### add-foo\n\n"
        "- **Source:** synthetic\n"
        "- **Blast-radius:** `nothing`\n"
        "- **Parallel-safety:** NON-OVERLAPPING\n"
        "- **Effort:** SMALL\n"
        "- **Claimed-by:** old <old@example.com>\n"
        "- **Claimed-at:** 2026-05-29T10:00:00+00:00\n"
    )
    text_2 = text_3.replace(
        "- **Claimed-by:** old <old@example.com>\n"
        "- **Claimed-at:** 2026-05-29T10:00:00+00:00\n",
        "- **Claimed-by:** newer <newer@example.com>\n"
        "- **Claimed-at:** 2026-05-29T12:00:00+00:00\n",
    )
    _stage_rebase_with_queue_collision(tmp_path, text_2, text_3)
    diag = _diag(
        u_files=("architecture/slice-queue.md",),
        claim_history=(
            _claim("add-foo", "old <old@example.com>", "2026-05-29T10:00:00+00:00", 3),
            _claim("add-foo", "newer <newer@example.com>", "2026-05-29T12:00:00+00:00", 2),
        ),
    )
    result = resolve_vault_claim_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class == ConflictClass.VAULT_CLAIM
    assert (
        "silently-dropped" in result.reason
        or "Risk-retired" in result.reason
    ), f"reason should cite silent-drop or Risk-retired pivot; got {result.reason!r}"


def test_pick_loser_replacement_reads_resolved_text_not_disk(tmp_path) -> None:
    """M-add-2 load-bearing test: helper reads ONLY the in-memory queue_text arg.

    Fixture: disk holds a conflict-marker'd queue file (simulates VAULT_CLAIM
    rebase-in-progress state). In-memory text holds the post-overlay clean
    resolution. Helper must return the disk-ignored result.

    Without this discipline, the helper would read git's conflict-markered
    on-disk file during VAULT_CLAIM rebase-in-progress and silently fail to
    parse → return None even when valid candidates exist (the dominant
    real-world scenario per M-add-2).
    """
    # Disk: conflict markers around the candidates block (would break parser)
    disk_text = (
        "# Slice queue\n\n"
        "## Candidates\n"
        "<<<<<<< HEAD\n"
        "### add-from-stage-2\n"
        "- **Parallel-safety:** NON-OVERLAPPING\n"
        "=======\n"
        "### add-from-stage-3\n"
        "- **Parallel-safety:** NON-OVERLAPPING\n"
        ">>>>>>> origin/master\n"
    )
    (tmp_path / "architecture").mkdir()
    (tmp_path / "architecture" / "slice-queue.md").write_text(disk_text, encoding="utf-8")

    # In-memory: clean post-overlay text with valid candidate
    in_memory_text = _queue_text([
        {"name": "add-valid", "parallel_safety": "NON-OVERLAPPING"},
    ])

    # Helper accepts queue_text arg ONLY; does NOT take repo_root → disk read impossible
    result = _pick_loser_replacement(queue_text=in_memory_text, exclude_names=set())
    assert result == "add-valid", (
        "_pick_loser_replacement must read from queue_text arg (in-memory overlay), "
        "NOT from architecture/slice-queue.md on disk during VAULT_CLAIM rebase-in-progress"
    )
