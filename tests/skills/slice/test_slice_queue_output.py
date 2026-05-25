"""PSQ-1 — Parallel-slice queue output (slice-067).

Per PSQ-1 (`methodology-changelog.md` v0.69.0; [[ADR-064]]; slice-067 mints a
new rule; supersedes nothing). PSQ-1 is the first rule on the parallel-slice
family axis (adjacent to BRANCH family; BRANCH-2 makes parallel work
physically possible, PSQ-1 makes it discoverable).

Tests pin the behavior contract for `tools/slice_queue_writer.py`:

  AC1 — /slice Step 6.5 writes architecture/slice-queue.md (top-10 cap)
  AC2 — each entry has 5 required fields with 4-value Parallel-safety enum
  AC3 — 4-way classification + precedence (graph > hint > overlap > non-overlap)
  AC4 — edge cases (zero candidates, zero active slices, missing graph, empty hint_files)
  AC5 — idempotent overwrite + provenance line

Note: AC6 entry-pin pair (`test_v_0_69_0_psq_1_entry_present_in_repo` +
`test_v_0_69_0_psq_1_shippability_consumer_propagation`) lives in
`tests/methodology/test_methodology_changelog.py` per BC-PROJ-10 paired-pin
schema.

Note: AC5's existing OSDG-1 anchor test
(`tests/methodology/test_slice_skill_drift.py
::test_in_repo_and_installed_slice_skill_md_are_content_equal`) transitively
guards the new Step 6.5 prose; not re-tested here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.slice_queue_writer import (
    write_slice_queue,
    compute_parallel_safety,
    format_queue_md,
    derive_active_slice_blast_radius,
)


_FIXED_TS = datetime(2026, 5, 25, 18, 0, 0, tzinfo=timezone.utc)


def _candidate(
    name: str,
    source: str = "risk-register R-13",
    hint_files: list[str] | None = None,
    effort: str = "SMALL",
    risk_retired: str = "LOW",
) -> dict:
    return {
        "name": name,
        "source": source,
        "hint_files": list(hint_files) if hint_files is not None else [],
        "effort": effort,
        "risk_retired": risk_retired,
    }


# --------------------------------------------------------------------- AC1


def test_slice_step_6_writes_slice_queue_md(tmp_path):
    (tmp_path / "architecture").mkdir()
    candidates = [_candidate("add-foo", hint_files=["tools/foo.py"])]

    out = write_slice_queue(
        repo_root=tmp_path,
        candidates=candidates,
        active_slice_num=67,
        graph_path=None,
        now=_FIXED_TS,
    )

    assert out == tmp_path / "architecture" / "slice-queue.md"
    assert out.exists(), "PSQ-1: architecture/slice-queue.md must be created"
    body = out.read_text(encoding="utf-8")
    assert "# Slice queue" in body
    assert "## Candidates" in body
    assert "### add-foo" in body


def test_slice_queue_top_10_cap(tmp_path):
    (tmp_path / "architecture").mkdir()
    candidates = [_candidate(f"add-cand-{i:02d}") for i in range(15)]

    out = write_slice_queue(
        repo_root=tmp_path,
        candidates=candidates,
        active_slice_num=67,
        graph_path=None,
        now=_FIXED_TS,
    )

    body = out.read_text(encoding="utf-8")
    # Top-10 cap: at most 10 `### ` entry blocks
    entry_count = body.count("\n### ")
    assert entry_count <= 10, (
        f"PSQ-1 top-10 cap: expected ≤10 entries, got {entry_count}"
    )
    # First 10 candidates (by input order) should appear; 11+ should not.
    for i in range(10):
        assert f"### add-cand-{i:02d}" in body
    for i in range(10, 15):
        assert f"### add-cand-{i:02d}" not in body


# --------------------------------------------------------------------- AC2


def test_each_entry_has_required_fields(tmp_path):
    (tmp_path / "architecture").mkdir()
    candidates = [
        _candidate(
            "add-bar",
            source="diagnose-out backlog SC-006",
            hint_files=["tools/bar.py"],
            effort="MEDIUM",
            risk_retired="HIGH",
        ),
    ]

    out = write_slice_queue(
        repo_root=tmp_path,
        candidates=candidates,
        active_slice_num=67,
        graph_path=None,
        now=_FIXED_TS,
    )

    body = out.read_text(encoding="utf-8")
    # Per PSQ-1 AC2: 5 required field lines per entry.
    for field in (
        "**Source:**",
        "**Blast-radius:**",
        "**Parallel-safety:**",
        "**Effort:**",
        "**Risk-retired:**",
    ):
        assert field in body, f"PSQ-1 AC2: missing required field {field}"

    # Parallel-safety must be one of 4 enum values.
    enum_values = (
        "NON-OVERLAPPING",
        "OVERLAPS-WITH-slice-",
        "UNKNOWN-NO-HINT-FILES",
        "UNKNOWN-NO-GRAPH",
    )
    assert any(v in body for v in enum_values), (
        "PSQ-1 AC2: Parallel-safety must use one of the 4 canonical enum values"
    )


# --------------------------------------------------------------------- AC3


def test_parallel_safety_flags_overlapping_active_slice():
    # Candidate touches tools/A.py + tools/C.py; active slice-99 declares
    # blast {tools/A.py, tools/B.py} → non-empty intersection ⇒ OVERLAPS.
    candidate_files = {"tools/A.py", "tools/C.py"}
    active_blasts = {99: {"tools/A.py", "tools/B.py"}}

    flag, overlapping = compute_parallel_safety(
        candidate_files, active_blasts, graph_missing=False
    )

    # Canonical 3-digit padding per slice-NNN convention (BRANCH-1 / BRANCH-2
    # `slice/NNN-<name>` branch shape + slice-folder naming).
    assert flag.startswith("OVERLAPS-WITH-slice-099"), (
        f"PSQ-1 AC3: expected OVERLAPS-WITH-slice-099 (3-digit padding), got {flag}"
    )
    assert overlapping == [99]


def test_parallel_safety_flags_non_overlapping():
    # Candidate touches tools/D.py + tools/E.py; active slice-99 declares
    # blast {tools/A.py, tools/B.py} → empty intersection ⇒ NON-OVERLAPPING.
    candidate_files = {"tools/D.py", "tools/E.py"}
    active_blasts = {99: {"tools/A.py", "tools/B.py"}}

    flag, overlapping = compute_parallel_safety(
        candidate_files, active_blasts, graph_missing=False
    )

    assert flag == "NON-OVERLAPPING", (
        f"PSQ-1 AC3: expected NON-OVERLAPPING, got {flag}"
    )
    assert overlapping == []


# --------------------------------------------------------------------- AC4


def test_zero_candidates_writes_placeholder(tmp_path):
    (tmp_path / "architecture").mkdir()

    out = write_slice_queue(
        repo_root=tmp_path,
        candidates=[],
        active_slice_num=67,
        graph_path=None,
        now=_FIXED_TS,
    )

    body = out.read_text(encoding="utf-8")
    assert "_(no candidates)_" in body, (
        "PSQ-1 AC4-(a): zero candidates must write `_(no candidates)_` placeholder"
    )
    assert "Generated:" in body, "Provenance line must remain present"


def test_zero_active_slices_non_overlapping_for_non_empty_hint_files():
    # Candidate has non-empty hint_files but there are no active slices
    # at all → empty intersection with empty union ⇒ NON-OVERLAPPING.
    candidate_files = {"tools/D.py", "tools/E.py"}
    active_blasts: dict[int, set[str]] = {}  # zero active slices

    flag, overlapping = compute_parallel_safety(
        candidate_files, active_blasts, graph_missing=False
    )

    assert flag == "NON-OVERLAPPING", (
        f"PSQ-1 AC4-(b): non-empty hint_files + zero active slices ⇒ NON-OVERLAPPING, got {flag}"
    )
    assert overlapping == []


def test_missing_graph_emits_warn_and_unknown_flags(tmp_path):
    (tmp_path / "architecture").mkdir()
    candidates = [
        _candidate("add-foo", hint_files=["tools/foo.py"]),
        _candidate("add-bar", hint_files=["tools/bar.py"]),
    ]

    # graph_path pointing to a nonexistent file simulates AC4-(c).
    nonexistent_graph = tmp_path / "graphify-out" / "graph.json"

    out = write_slice_queue(
        repo_root=tmp_path,
        candidates=candidates,
        active_slice_num=67,
        graph_path=nonexistent_graph,
        now=_FIXED_TS,
    )

    body = out.read_text(encoding="utf-8")
    assert "WARN: graphify graph missing" in body, (
        "PSQ-1 AC4-(c): missing graph must emit top-of-file WARN line"
    )
    # Every entry's Parallel-safety must be UNKNOWN-NO-GRAPH
    # (precedence: graph > hint > overlap > non-overlap).
    assert body.count("UNKNOWN-NO-GRAPH") >= 2, (
        "PSQ-1 AC4-(c): each entry must flag UNKNOWN-NO-GRAPH when graph missing"
    )
    # And Blast-radius cells should be `unknown`
    assert body.count("**Blast-radius:** `unknown`") >= 2 or (
        body.count("**Blast-radius:** unknown") >= 2
    ), "PSQ-1 AC4-(c): Blast-radius cells must read `unknown` when graph missing"


def test_empty_hint_files_overrides_zero_active_slices_to_unknown_no_hint_files():
    # Candidate has EMPTY hint_files. Per AC3 precedence (graph > hint >
    # overlap > non-overlap), this must classify as UNKNOWN-NO-HINT-FILES
    # even when active_blasts is empty (collision case explicit in design.md L80).
    candidate_files: set[str] = set()  # empty hint_files
    active_blasts: dict[int, set[str]] = {}  # zero active slices

    flag, overlapping = compute_parallel_safety(
        candidate_files, active_blasts, graph_missing=False
    )

    assert flag == "UNKNOWN-NO-HINT-FILES", (
        f"PSQ-1 AC4-(d) collision rule: empty hint_files + zero active slices ⇒ UNKNOWN-NO-HINT-FILES (NOT NON-OVERLAPPING), got {flag}"
    )
    assert overlapping == []


# --------------------------------------------------------------------- AC5


def test_idempotent_overwrite_with_provenance_line(tmp_path):
    (tmp_path / "architecture").mkdir()
    candidates = [_candidate("add-foo", hint_files=["tools/foo.py"])]

    # First run.
    out1 = write_slice_queue(
        repo_root=tmp_path,
        candidates=candidates,
        active_slice_num=67,
        graph_path=None,
        now=_FIXED_TS,
    )
    body1 = out1.read_text(encoding="utf-8")
    size1 = out1.stat().st_size

    # Second run with a later timestamp.
    later_ts = datetime(2026, 5, 25, 18, 5, 0, tzinfo=timezone.utc)
    out2 = write_slice_queue(
        repo_root=tmp_path,
        candidates=candidates,
        active_slice_num=67,
        graph_path=None,
        now=later_ts,
    )
    body2 = out2.read_text(encoding="utf-8")
    size2 = out2.stat().st_size

    # Idempotent overwrite (not append): size should not grow beyond ~one
    # line's worth of timestamp delta.
    assert abs(size2 - size1) < 100, (
        f"PSQ-1 AC5: second run must OVERWRITE not append (size delta {size2 - size1})"
    )
    # Provenance line must update timestamp on second run.
    assert "2026-05-25T18:00:00" in body1
    assert "2026-05-25T18:05:00" in body2
    assert "2026-05-25T18:00:00" not in body2, (
        "PSQ-1 AC5: second run must overwrite the old provenance line"
    )
    # Candidate-set content is equal modulo timestamp.
    body1_no_ts = body1.replace("2026-05-25T18:00:00", "<TS>")
    body2_no_ts = body2.replace("2026-05-25T18:05:00", "<TS>")
    assert body1_no_ts == body2_no_ts, (
        "PSQ-1 AC5: consecutive runs must produce equivalent content modulo timestamp"
    )
