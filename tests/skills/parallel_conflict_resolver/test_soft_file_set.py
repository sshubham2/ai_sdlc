"""SOFT-class file-set pin (PCR-1 / slice-076 / ADR-069).

Per PCR-1: the canonical 2-member SOFT file-set is the runtime contract
that determines which conflicts auto-resolve vs STOP. Drift in this set
silently expands or contracts the auto-resolution surface — both directions
are load-bearing risks:

  - Adding a file (e.g., methodology-changelog.md) → auto-merging that file
    could silently violate BC-PROJ-10 paired-pin discipline.
  - Dropping a file (e.g., slice-queue.md) → re-introduces the 5-session
    parallel-slice deadlock this slice retires.

The forward-slash-key convention is also pinned: git status --porcelain
emits forward-slash on all OSes, but ``str(Path)`` on Windows produces
backslashes — using ``Path`` objects for membership checks silently misses
the frozenset on Windows. Per /critique M1 ACCEPTED-FIXED (Windows
backslash bug) + design.md L52.
"""
from __future__ import annotations

from pathlib import Path

from tools.parallel_conflict_resolver import _SOFT_FILE_SET


def test_soft_file_set_is_two_canonical_files_forward_slash_keyed() -> None:
    """``_SOFT_FILE_SET`` MUST be exactly the 2 canonical forward-slash-keyed paths.

    AC3 + AC4 per mission-brief.md (SOFT file-set pin row + classify_conflict
    SOFT-when-all-u-files-in-two-member-soft-set row). The 2-member contract
    is:

      - ``architecture/slice-queue.md``
      - ``architecture/shippability.md``

    Per ADR-069 § Decision § 5-class taxonomy / SOFT row + design.md L50:
      - ``_index.md`` dropped per /critique B3 ACCEPTED-FIXED (Haiku-LLM-
        dispatched by /archive per COST-1; not deterministic; PCR-1 cannot
        reproduce Haiku's lessons-block synthesis).
      - ``methodology-changelog.md`` dropped per /design-slice clarifying
        answer (PMI-1 5-leg atomic-bump risk on concurrent bumps).

    Drift in either direction is a regression: shrinking the set re-opens
    the parallel-slice deadlock; growing it silently expands the auto-merge
    surface to files whose merge semantics are NOT mechanical.
    """
    expected = frozenset({
        "architecture/slice-queue.md",
        "architecture/shippability.md",
    })
    assert _SOFT_FILE_SET == expected, (
        f"PCR-1 SOFT file-set drift: expected exactly {sorted(expected)}, "
        f"got {sorted(_SOFT_FILE_SET)}. ADR-069 § Decision § 5-class taxonomy "
        f"/ SOFT row pins the 2-member contract; drift in either direction is "
        f"load-bearing (shrinking re-opens slice-076 deadlock; growing "
        f"silently expands auto-merge surface)."
    )


def test_soft_file_set_membership_uses_forward_slash_keys_on_windows_paths() -> None:
    """SOFT-set membership MUST be insensitive to Path-vs-string representation
    drift on Windows.

    AC4 per mission-brief.md (Windows path normalization row). The bug being
    pinned: on Windows, ``str(Path("architecture/slice-queue.md"))`` produces
    ``"architecture\\slice-queue.md"`` (backslash), which does NOT match the
    forward-slash-keyed frozenset. Code that uses ``str(Path(...))`` for
    membership checks silently misses on Windows.

    Per /critique M1 ACCEPTED-FIXED + design.md L52: membership checks MUST
    use raw forward-slash strings (from ``git status --porcelain`` which
    emits forward-slash on all OSes per git docs) OR ``Path.as_posix()``
    normalization. Direct ``str(Path)`` casts are the bug.

    This test pins the contract by asserting that the documented-correct
    forms (raw forward-slash + ``.as_posix()``) work, AND that the
    documented-buggy form (``str(Path)`` on Windows) DOES NOT silently pass.
    """
    # Documented-correct form #1: raw forward-slash string (what git emits)
    assert "architecture/slice-queue.md" in _SOFT_FILE_SET, (
        "Raw forward-slash string 'architecture/slice-queue.md' MUST be in "
        "_SOFT_FILE_SET — this is the canonical key format (git status "
        "--porcelain emits forward-slash on all OSes per git docs)"
    )
    assert "architecture/shippability.md" in _SOFT_FILE_SET, (
        "Raw forward-slash string 'architecture/shippability.md' MUST be in "
        "_SOFT_FILE_SET — canonical key format"
    )
    # Documented-correct form #2: Path(...).as_posix() normalization
    assert Path("architecture/slice-queue.md").as_posix() in _SOFT_FILE_SET, (
        "Path(...).as_posix() MUST normalize to a key present in "
        "_SOFT_FILE_SET — this is the documented internal normalization "
        "path per design.md L52"
    )
    # Membership keys MUST contain forward-slash (not backslash); if any
    # entry contains backslash the set was constructed wrong.
    for entry in _SOFT_FILE_SET:
        assert "\\" not in entry, (
            f"_SOFT_FILE_SET entry {entry!r} contains backslash — keys MUST "
            f"be forward-slash-keyed (Windows-portability invariant per "
            f"design.md L52 / /critique M1)"
        )
        assert "/" in entry, (
            f"_SOFT_FILE_SET entry {entry!r} missing forward-slash — keys "
            f"are repo-root-relative forward-slash paths per git porcelain "
            f"output convention"
        )
