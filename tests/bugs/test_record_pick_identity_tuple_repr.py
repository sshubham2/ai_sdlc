"""Bug: /slice Step 6.5 pick-provenance writer emits a Python tuple repr.

Slice: slice-104-fix-record-pick-identity-format

``tools/slice_queue_writer.record_pick(picker_identity)`` f-string-renders its
arg directly into ``- <slice> — picked <ts> by <picker_identity>``. The
documented ``/slice`` Step 6.5 invocation passes
``tools/slice_queue_claim.read_git_config_user()``, which returns a
``(name, email)`` TUPLE — so the line serializes as ``by ('Name', 'email')``
instead of the well-formed ``by Name email``.

Expected: given the ``(name, email)`` tuple identity that
``read_git_config_user`` returns, ``record_pick`` writes a well-formed
``by <name> <email>`` line (space-joined, matching the live slice-100/101/102
pick-log lines).
Actual (pre-fix): writes ``by ('<name>', '<email>')`` (Python tuple repr).

Observed: the live slice-103 pick (hand-corrected in slice-queue.md) and prior
picks per the repo owner.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from tools.slice_queue_writer import _extract_pick_log_block, record_pick

_T = datetime(2026, 6, 2, 9, 0, 0, tzinfo=timezone.utc)
# The exact shape tools/slice_queue_claim.read_git_config_user() returns.
_IDENTITY_TUPLE = ("Shubhendu Shubham", "s2.shubh2@gmail.com")


def _seed_queue(tmp_path: Path) -> Path:
    q = tmp_path / "slice-queue.md"
    q.write_text(
        "# Slice queue\n\n## Candidates\n\n_(no candidates)_\n", encoding="utf-8"
    )
    return q


def test_record_pick_with_identity_tuple_emits_well_formed_line(tmp_path: Path):
    """A (name, email) tuple identity must NOT serialize as a Python tuple repr."""
    q = _seed_queue(tmp_path)
    record_pick(
        tmp_path,
        "slice-104-fix-record-pick-identity-format",
        _IDENTITY_TUPLE,
        _T,
        out_path=q,
    )
    block = _extract_pick_log_block(q.read_text(encoding="utf-8"))
    pick_line = next(
        ln for ln in block.splitlines() if ln.startswith("- slice-104")
    )
    identity_tail = pick_line.split(" by ", 1)[1]
    # Well-formed: space-joined "name email" (matches slice-100/101/102 lines).
    assert identity_tail == "Shubhendu Shubham s2.shubh2@gmail.com", pick_line
    # Regression guard: the Python tuple repr must never appear.
    assert "(" not in identity_tail and "'" not in identity_tail, pick_line
