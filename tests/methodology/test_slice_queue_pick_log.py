"""Tests for the `## Pick log` (slice-099 / BRANCH-3 / ADR-090).

Pins the DISTINCT pick-log preservation path in tools/slice_queue_writer.py:
record_pick (first-pick create + re-append + idempotency + name boundary) and
write_slice_queue carrying the pick log verbatim across `## Candidates`
regeneration (which PSQ-2 claim-preservation cannot do — it keys on `### entry`
headers a top-level `## Pick log` lacks).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from tools.slice_queue_writer import (
    _extract_pick_log_block,
    format_queue_md,
    record_pick,
    write_slice_queue,
)


_T = datetime(2026, 6, 2, 9, 0, 0, tzinfo=timezone.utc)
_PICKER = "Test User <t@example.com>"


def _q(tmp_path: Path) -> Path:
    return tmp_path / "slice-queue.md"


# ------------------------------------------------------------------
# record_pick — first-pick create / re-append / idempotency / boundary
# ------------------------------------------------------------------


def test_record_pick_first_pick_creates_section(tmp_path: Path):
    q = _q(tmp_path)
    q.write_text("# Slice queue\n\n## Candidates\n\n_(no candidates)_\n", encoding="utf-8")
    record_pick(tmp_path, "slice-099-create-worktree-at-slice-pick", _PICKER, _T, out_path=q)
    text = q.read_text(encoding="utf-8")
    assert "## Pick log" in text
    assert "- slice-099-create-worktree-at-slice-pick — picked 2026-06-02T09:00:00+00:00 by Test User <t@example.com>" in text
    # Candidates section preserved.
    assert "## Candidates" in text


def test_record_pick_appends_second_line(tmp_path: Path):
    q = _q(tmp_path)
    q.write_text("# Slice queue\n\n## Candidates\n\n_(no candidates)_\n", encoding="utf-8")
    record_pick(tmp_path, "slice-099-foo", _PICKER, _T, out_path=q)
    record_pick(tmp_path, "slice-100-bar", _PICKER, _T, out_path=q)
    block = _extract_pick_log_block(q.read_text(encoding="utf-8"))
    lines = [ln for ln in block.splitlines() if ln.startswith("- ")]
    assert len(lines) == 2
    assert any("slice-099-foo" in ln for ln in lines)
    assert any("slice-100-bar" in ln for ln in lines)


def test_record_pick_idempotent_double_pick(tmp_path: Path):
    q = _q(tmp_path)
    q.write_text("# Slice queue\n\n## Candidates\n\n_(no candidates)_\n", encoding="utf-8")
    record_pick(tmp_path, "slice-099-foo", _PICKER, _T, out_path=q)
    record_pick(tmp_path, "slice-099-foo", _PICKER, _T, out_path=q)  # repeat → no-op
    block = _extract_pick_log_block(q.read_text(encoding="utf-8"))
    lines = [ln for ln in block.splitlines() if ln.startswith("- ")]
    assert len(lines) == 1


def test_record_pick_name_boundary_no_prefix_collision(tmp_path: Path):
    """slice-009-foo must NOT be treated as already-recorded by slice-099-foo."""
    q = _q(tmp_path)
    q.write_text("# Slice queue\n\n## Candidates\n\n_(no candidates)_\n", encoding="utf-8")
    record_pick(tmp_path, "slice-099-foo", _PICKER, _T, out_path=q)
    record_pick(tmp_path, "slice-009-foo", _PICKER, _T, out_path=q)
    block = _extract_pick_log_block(q.read_text(encoding="utf-8"))
    lines = [ln for ln in block.splitlines() if ln.startswith("- ")]
    assert len(lines) == 2  # both recorded — the ` —` boundary prevents collision


# ------------------------------------------------------------------
# write_slice_queue — pick log survives `## Candidates` regeneration
# ------------------------------------------------------------------


def test_pick_log_survives_write_slice_queue_regeneration(tmp_path: Path):
    q = _q(tmp_path)
    # Seed a queue WITH a pick-log line.
    write_slice_queue(
        tmp_path,
        candidates=[{"name": "cand-a", "source": "x", "hint_files": [],
                     "effort": "SMALL", "risk_retired": "LOW"}],
        active_slice_num=99, graph_path=None, now=_T, out_path=q,
    )
    record_pick(tmp_path, "slice-099-foo", _PICKER, _T, out_path=q)
    assert "slice-099-foo" in q.read_text(encoding="utf-8")

    # Regenerate `## Candidates` with a DIFFERENT candidate set — pick log must persist.
    write_slice_queue(
        tmp_path,
        candidates=[{"name": "cand-b", "source": "y", "hint_files": [],
                     "effort": "MEDIUM", "risk_retired": "NONE"}],
        active_slice_num=100, graph_path=None, now=_T, out_path=q,
    )
    text = q.read_text(encoding="utf-8")
    assert "cand-b" in text          # new candidate present
    assert "cand-a" not in text      # old candidate gone (regenerated)
    assert "## Pick log" in text     # pick log survived
    assert "- slice-099-foo — picked" in text  # the pick line survived verbatim


def test_format_queue_md_emits_pick_log_block():
    body = format_queue_md(
        [], _T, active_slice_num=99,
        pick_log_block="## Pick log\n\n- slice-099-foo — picked 2026-06-02T09:00:00+00:00 by X <x@y.z>",
    )
    assert body.rstrip().endswith("- slice-099-foo — picked 2026-06-02T09:00:00+00:00 by X <x@y.z>")
    assert "## Pick log" in body
    # Pick log comes AFTER candidates.
    assert body.index("## Candidates") < body.index("## Pick log")
