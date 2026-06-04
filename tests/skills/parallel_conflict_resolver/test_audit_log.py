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

import sys

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.parallel_conflict_resolver as _pcr

# slice-110 / [[ADR-101]]: location-agnostic VAULT_ROOT pin (see autouse_pin).
# This file also imports _AUDIT_LOG_PATH by name and builds `tmp / _AUDIT_LOG_PATH`
# (L56), so the test module's OWN frozen copy is re-derived too — not just the
# resolver's module attribute.
_pin_vault = vi.autouse_pin(
    _vgit, _pcr,
    derived=[
        (_pcr, "_AUDIT_LOG_PATH",
         lambda vr: vr / "parallel-conflict-resolution-log.md"),
        (sys.modules[__name__], "_AUDIT_LOG_PATH",
         lambda vr: vr / "parallel-conflict-resolution-log.md"),
    ],
)

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


def test_append_audit_log_writes_lf_only_no_crlf_translation(tmp_path) -> None:
    """Regression for M1 / EOL-DRIFT-1 / ADR-033 (code-review fix).

    `_append_audit_log` MUST emit LF-only byte-deterministic output even on
    Windows. Pre-fix, the lazy-create branch used `Path.write_text(...)` and
    the append branch used `open("a", encoding=...)` — both default to
    `newline=None` which on Windows translates `\\n` → `\\r\\n`. The
    sibling PSQ-2 modules (`tools/slice_queue_writer.py:790` +
    `tools/slice_queue_claim.py:535`) explicitly use `newline=""` for the
    same LF-only invariant; PCR-1 now matches.

    Asserts the on-disk bytes contain NO `\\r\\n` (CRLF) sequence after both
    lazy-create + append branches execute. Single-open append refactor
    (m6 fix) also covered here — both paths emit LF.
    """
    (tmp_path / "architecture").mkdir()
    log_path = tmp_path / _AUDIT_LOG_PATH
    assert not log_path.exists(), "pre-test: log file must not exist"

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

    # First call exercises the lazy-create branch (single-open with header).
    _append_audit_log(tmp_path, diag, result)
    assert log_path.exists()
    bytes_after_first = log_path.read_bytes()
    assert b"\r\n" not in bytes_after_first, (
        f"Lazy-create branch produced CRLF bytes — EOL-DRIFT-1 / ADR-033 "
        f"violation. First 200 bytes: {bytes_after_first[:200]!r}"
    )

    # Second call exercises the append branch (header NOT re-written).
    _append_audit_log(tmp_path, diag, result)
    bytes_after_second = log_path.read_bytes()
    assert b"\r\n" not in bytes_after_second, (
        f"Append branch produced CRLF bytes — EOL-DRIFT-1 / ADR-033 "
        f"violation. First 200 bytes: {bytes_after_second[:200]!r}"
    )
    # Header MUST appear exactly once (not re-written on append).
    assert bytes_after_second.count(b"Parallel-conflict-resolution log") == 1, (
        "Header MUST appear exactly once; append branch should NOT re-write header"
    )
