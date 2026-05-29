"""Pin slice-079 Fix P (slice-078 m2): `_parse_queue_candidates_for_replacement` MISSING-FIELD sentinel.

Slice-078 m2: a candidate block missing the `**Parallel-safety:**` field-line silently became
`"UNKNOWN-NO-GRAPH"` — overloading a real PSQ-1 enumeration sentinel. Fix P uses distinct
`"MISSING-FIELD"` sentinel; downstream filter still rejects both equivalent.
"""
from __future__ import annotations

from tools.parallel_conflict_resolver import _parse_queue_candidates_for_replacement


def test_candidate_without_parallel_safety_line_returns_missing_field() -> None:
    """Fix P: candidate block missing `**Parallel-safety:**` field gets MISSING-FIELD sentinel."""
    queue_text = (
        "# Slice queue\n\n"
        "## Candidates\n\n"
        "### candidate-without-safety-line\n\n"
        "- **Source:** test\n"
        "- **Blast-radius:** `tools/foo.py`\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n\n"
    )
    candidates = _parse_queue_candidates_for_replacement(queue_text)
    matches = [c for c in candidates if c.name == "candidate-without-safety-line"]
    assert matches, f"Sanity: expected to parse 'candidate-without-safety-line'; got {[c.name for c in candidates]}"
    safety = matches[0].parallel_safety
    assert safety == "MISSING-FIELD", (
        f"Fix P regression: candidate without Parallel-safety line should yield MISSING-FIELD sentinel, "
        f"got {safety!r}. (Pre-fix this returned 'UNKNOWN-NO-GRAPH', overloading the real PSQ-1 sentinel.)"
    )


def test_candidate_with_unknown_no_graph_value_still_returns_unknown_no_graph() -> None:
    """Fix P: real `UNKNOWN-NO-GRAPH` value preserved (semantically distinct from MISSING-FIELD)."""
    queue_text = (
        "# Slice queue\n\n"
        "## Candidates\n\n"
        "### candidate-with-no-graph\n\n"
        "- **Source:** test\n"
        "- **Blast-radius:** `tools/foo.py`\n"
        "- **Parallel-safety:** UNKNOWN-NO-GRAPH\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n\n"
    )
    candidates = _parse_queue_candidates_for_replacement(queue_text)
    matches = [c for c in candidates if c.name == "candidate-with-no-graph"]
    assert matches, "Sanity: expected to parse candidate-with-no-graph"
    assert matches[0].parallel_safety == "UNKNOWN-NO-GRAPH", (
        "Fix P regression: real UNKNOWN-NO-GRAPH value mis-mapped to MISSING-FIELD; "
        "the two sentinels must remain semantically distinct"
    )
