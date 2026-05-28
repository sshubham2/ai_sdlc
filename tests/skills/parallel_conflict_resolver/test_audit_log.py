"""Audit-log append tests (PCR-1 / slice-076 / ADR-069).

Per AC3 unit / audit logging per mission-brief row + design.md § New audit
log file: ``_append_audit_log`` writes to ``architecture/parallel-conflict-
resolution-log.md`` after every SOFT-class auto-resolution. Lazy-create on
first append (writes the canonical header per ``_AUDIT_LOG_HEADER``).

Mirrors the ``architecture/critic-calibration-log.md`` pattern: append-only,
human-readable markdown with one H2 section per resolution event.

The audit log is best-effort (per design.md § Error model): write failures
log to stderr but do NOT block resolution (the rebase has already been
continued at append-time). Auditability is desirable but not load-bearing
per ADR-069 § Audit log race-acceptance.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.parallel_conflict_resolver import (
    ConflictClass,
    ConflictDiagnostic,
    ResolutionResult,
    _AUDIT_LOG_PATH,
    _append_audit_log,
)


def test_soft_conflict_resolution_appends_to_parallel_conflict_resolution_log(tmp_path) -> None:
    """``_append_audit_log`` writes a canonical entry to
    ``architecture/parallel-conflict-resolution-log.md``.

    AC3 unit / audit logging per mission-brief row. The contract:
      - Lazy-create the file on first append with the canonical header
        (``_AUDIT_LOG_HEADER``).
      - Append ONE H2 section per resolution event with the canonical fields:
        ISO-8601 UTC timestamp, U-files resolved, concerned slices,
        per-file resolution actions.
      - Append-only: existing content MUST be preserved (no overwrite).

    Uses tmp_path-rooted fake repo to verify the lazy-create + append
    behavior without polluting the real audit log.
    """
    (tmp_path / "architecture").mkdir()
    log_path = tmp_path / _AUDIT_LOG_PATH

    # File should NOT exist before first append.
    assert not log_path.exists(), (
        f"Pre-test: {log_path} must not exist (lazy-create on first append)"
    )

    diag = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md", "architecture/shippability.md"),
        concerned_slices={},
        claim_history=(),
    )
    result = ResolutionResult(
        action="APPLIED",
        conflict_class=ConflictClass.SOFT,
        regenerated_files=("architecture/slice-queue.md", "architecture/shippability.md"),
        reason=None,
    )
    _append_audit_log(tmp_path, diag, result)

    # File MUST exist after first append.
    assert log_path.exists(), (
        f"_append_audit_log MUST lazy-create {log_path} on first append"
    )
    content = log_path.read_text(encoding="utf-8")
    # Header MUST be present (lazy-created).
    assert "Parallel-conflict-resolution log" in content, (
        "Lazy-created audit log MUST contain the canonical header "
        "(per _AUDIT_LOG_HEADER constant)"
    )
    # Resolution event entry MUST cite the resolved files.
    assert "architecture/slice-queue.md" in content, (
        "Audit log entry MUST cite resolved U-files (slice-queue.md)"
    )
    assert "architecture/shippability.md" in content, (
        "Audit log entry MUST cite resolved U-files (shippability.md)"
    )
