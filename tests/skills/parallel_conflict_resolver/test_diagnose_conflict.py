"""diagnose_conflict() library-API test (PCR-1 / slice-076 / ADR-069).

Per AC4 mission-brief.md row + design.md § Components touched:
``diagnose_conflict(repo_root: Path) -> ConflictDiagnostic`` reads
``git status --porcelain`` to enumerate U-files, derives concerned-slice
metadata from ``architecture/slice-queue.md`` + each active slice's
``mission-brief.md``, and returns a frozen ``ConflictDiagnostic`` with
``u_files`` + ``concerned_slices`` + ``claim_history``.

This test uses a tmp_path-rooted synthetic git repo with a pre-staged
conflict state (U-files manually injected via the git index) to exercise
the read path without depending on a real cross-branch rebase. The helper
is verified to return a ``ConflictDiagnostic`` with the expected
``concerned_slices`` map shape.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.parallel_conflict_resolver import (
    ConcernedSlice,
    ConflictDiagnostic,
    diagnose_conflict,
)


def _init_repo_with_conflict_state(tmp_path: Path) -> Path:
    """Initialize a tmp_path-rooted git repo with a synthetic in-progress
    rebase state containing a single U-file on ``architecture/slice-queue.md``.

    The helper avoids the cost of a real cross-branch rebase by directly
    manipulating the index to add stages 2 + 3 on the conflicting path.
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    arch = tmp_path / "architecture"
    arch.mkdir()
    queue_path = arch / "slice-queue.md"
    queue_path.write_text("# Slice queue\n\n## Candidates\n", encoding="utf-8")
    subprocess.run(["git", "add", "architecture/slice-queue.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)
    return tmp_path


def test_diagnose_conflict_returns_conflict_diagnostic_with_concerned_slices_map(tmp_path) -> None:
    """``diagnose_conflict`` MUST return a frozen ``ConflictDiagnostic`` with
    populated ``u_files`` + ``concerned_slices`` map fields.

    AC4 per mission-brief.md: the diagnostic surface is the universal
    "what's actually conflicting" report fired for ALL classes; it's the
    parametric input to ``classify_conflict`` + ``resolve_soft_conflict``.

    The shape contract (per design.md § Frozen dataclasses + § Components
    touched):
      - ``u_files: tuple[str, ...]`` — forward-slash strings (per /critique M1)
      - ``concerned_slices: dict[str, tuple[ConcernedSlice, ...]]`` —
        forward-slash-keyed map from U-file to concerned-slice list
      - ``claim_history: tuple[ClaimEntry, ...]``
    """
    repo_root = _init_repo_with_conflict_state(tmp_path)
    result = diagnose_conflict(repo_root)
    assert isinstance(result, ConflictDiagnostic), (
        f"diagnose_conflict must return a ConflictDiagnostic; got {type(result).__name__}"
    )
    assert isinstance(result.u_files, tuple), (
        "ConflictDiagnostic.u_files must be a tuple (immutable per frozen dataclass)"
    )
    assert isinstance(result.concerned_slices, dict), (
        "ConflictDiagnostic.concerned_slices must be a dict mapping U-file "
        "(forward-slash str) to tuple[ConcernedSlice, ...]"
    )
    assert isinstance(result.claim_history, tuple), (
        "ConflictDiagnostic.claim_history must be a tuple"
    )
    # All u_files entries MUST be forward-slash strings (no backslash, per
    # /critique M1 Windows path normalization invariant).
    for u_file in result.u_files:
        assert isinstance(u_file, str), (
            f"ConflictDiagnostic.u_files entry {u_file!r} must be a str "
            f"(forward-slash, NOT Path) per design.md L52"
        )
        assert "\\" not in u_file, (
            f"ConflictDiagnostic.u_files entry {u_file!r} contains backslash "
            f"— u_files must be forward-slash-keyed (Windows-portability "
            f"invariant per /critique M1)"
        )
