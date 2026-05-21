"""R-15 archive-aware vault-test discipline tests (slice-056).

Pins the ``_resolve_slice_dir(slice_number: int) -> Path`` helper added
to ``tests.methodology.conftest`` by slice-056. The helper is the
mitigation pattern for R-15 (archive-aware vault-test discipline) —
tests pinning invariants on their own slice's vault files MUST resolve
the slice folder through this helper so the post-/reflect-archival
``architecture/slices/<active>`` → ``architecture/slices/archive/<active>``
relocation doesn't break them.

R-15 retirement gate (per ``architecture/risk-register.md:259``) is
TWO-part: (a) slice-056 ships the fix + the resolver helper [satisfied
by THIS slice], AND (b) a future slice authoring a similar vault-pin
test demonstrably uses the helper [pending — likely the slice-034
retrofit nominated under slice-056 mission-brief Out-of-scope]. R-15
STAYS ``**Status**: mitigating`` after slice-056 ships (per /critique m2
ACCEPTED-FIXED). The corpus class-closure backstop test below provides
a SECOND structural mechanism for R-15 part-(b) retirement: when the
slice-034 retrofit lands and the whitelist shrinks to empty, the
backstop assertion structurally satisfies "no R-15-class literals
remain" without waiting for cross-slice observational evidence.

Rule references:
- R-15 (slice-055-discovered; mitigating after slice-056 ship)
- BFRD-1 (slice-056 reproduction: ``tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant``
  FAILING on master pre-fix; PASSING post-fix is the BFRD-1 invariant)
- TPHD-1 (slice-017): test-function names match mission-brief TF-1 plan rows
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.methodology import conftest as conftest_mod
from tests.methodology.conftest import REPO_ROOT, _resolve_slice_dir


# ---------------------------------------------------------------------------
# AC2 — helper-import / symbol-presence pin
# ---------------------------------------------------------------------------


def test_helper_is_importable_from_conftest() -> None:
    """``_resolve_slice_dir`` is importable from ``tests.methodology.conftest``
    AND is callable. Symbol-presence pin per slice-056 AC2.
    """
    # Re-import explicitly to defend against module-cache surprises (pytest
    # collects test files in arbitrary order; the top-level import above
    # might not be the only entry path future maintainers consider).
    from tests.methodology.conftest import _resolve_slice_dir as imported

    assert callable(imported), "_resolve_slice_dir must be a callable"
    assert imported is _resolve_slice_dir, (
        "the imported _resolve_slice_dir must be the same object as the "
        "module-level binding (no shadowing)"
    )


# ---------------------------------------------------------------------------
# AC3 — structural pin: BCR-1 module no longer carries the literal RHS
# ---------------------------------------------------------------------------


def test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir() -> None:
    """``tests/methodology/test_bcr_1_round_trip_end_to_end.py`` no longer
    carries the archive-fragile literal-path RHS
    ``REPO_ROOT / "architecture" / "slices" / "slice-054`` (per slice-056
    AC3 ACCEPTED-FIXED + /critique m1 wording harmonization).

    Wrapped forms (``SLICE_054_DIR = _resolve_slice_dir(54)``) are
    ACCEPTED — the structural pin asserts absence of the LITERAL-PATH form,
    not absence of the ``SLICE_054_DIR`` symbol name.
    """
    bcr_1_path = REPO_ROOT / "tests" / "methodology" / "test_bcr_1_round_trip_end_to_end.py"
    assert bcr_1_path.is_file(), (
        f"slice-054-authored BCR-1 test module missing at {bcr_1_path}"
    )
    text = bcr_1_path.read_text(encoding="utf-8")

    forbidden_literal = 'REPO_ROOT / "architecture" / "slices" / "slice-054'
    assert forbidden_literal not in text, (
        f"archive-fragile literal-path RHS '{forbidden_literal}' "
        f"re-introduced into test_bcr_1_round_trip_end_to_end.py — "
        f"this is the slice-054-class R-15 regression slice-056 ships to "
        f"prevent. Use _resolve_slice_dir(54) instead."
    )


# ---------------------------------------------------------------------------
# AC4 row 1 — archive-path branch on a real archived slice
# ---------------------------------------------------------------------------


def test_resolves_archived_slice_054() -> None:
    """``_resolve_slice_dir(54)`` resolves to the archived slice-054 folder
    via the archive-glob branch (AC4 row 1).

    Slice-054 was archived by /reflect after shipping, so the active glob
    ``architecture/slices/slice-054-*`` misses (no active directory) and
    the archive glob ``architecture/slices/archive/slice-054-*`` hits.
    """
    resolved = _resolve_slice_dir(54)

    assert resolved.is_dir(), (
        f"_resolve_slice_dir(54) returned {resolved!r} which is not a directory"
    )
    assert resolved.name == "slice-054-fix-pyproject-toml-version-drift", (
        f"expected slice-054-fix-pyproject-toml-version-drift, got {resolved.name!r}"
    )
    assert resolved.parent.name == "archive", (
        f"expected archive parent, got {resolved.parent.name!r} — "
        f"slice-054 should resolve via the archive-glob branch since it "
        f"has shipped through /reflect"
    )


# ---------------------------------------------------------------------------
# AC4 row 2 — active-path branch via tmp_vault fixture
# ---------------------------------------------------------------------------


def test_resolves_active_slice_via_tmp_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``_resolve_slice_dir(N)`` resolves via the ACTIVE-glob branch when
    ``architecture/slices/slice-NNN-*/`` exists at REPO_ROOT (AC4 row 2).

    Uses ``monkeypatch.setattr`` on ``tests.methodology.conftest.REPO_ROOT``
    to point the helper at a tmp vault. This relies on the helper reading
    ``REPO_ROOT`` at function-call-time (Python's natural module-globals
    binding semantics) — pinned at slice-056 /critique M2 ACCEPTED-FIXED.
    """
    # Build a tmp vault with one active slice folder.
    active_dir = tmp_path / "architecture" / "slices" / "slice-001-tmp-fixture"
    active_dir.mkdir(parents=True)

    # Repoint REPO_ROOT at the tmp vault. The helper reads REPO_ROOT at
    # call-time via module-globals, so this affects the next call.
    monkeypatch.setattr(conftest_mod, "REPO_ROOT", tmp_path)

    resolved = _resolve_slice_dir(1)

    assert resolved == active_dir, (
        f"_resolve_slice_dir(1) returned {resolved!r}; expected {active_dir!r} "
        f"via the active-glob branch under the monkeypatched REPO_ROOT"
    )
    assert resolved.is_dir(), (
        f"_resolve_slice_dir(1) returned {resolved!r} which is not a directory"
    )
    # The active branch wins: parent is "slices" (NOT "archive") — verifies
    # the active-glob fires BEFORE the archive-glob.
    assert resolved.parent.name == "slices", (
        f"expected active-glob parent 'slices', got {resolved.parent.name!r}"
    )


# ---------------------------------------------------------------------------
# AC4 row 3 — AssertionError with cause-naming diagnostic when neither found
# ---------------------------------------------------------------------------


def test_raises_assertion_with_diagnostic_when_neither_found() -> None:
    """``_resolve_slice_dir(N)`` raises AssertionError with a single-line
    diagnostic naming BOTH attempted glob patterns + the slice number when
    neither active nor archive glob matches (AC4 row 3).

    Uses slice-000 — reserved by BRANCH-1 but no folder exists in this
    repo's history, so both globs miss. The diagnostic-message format is
    pinned (per /critique m4 ACCEPTED-FIXED) to use forward-slash glob
    patterns regardless of platform (Windows-vs-POSIX safe).
    """
    with pytest.raises(AssertionError) as exc_info:
        _resolve_slice_dir(0)

    message = str(exc_info.value)

    # Cause-name diagnostic prefix (slice number padded to 3 digits)
    assert "neither active nor archive resolution succeeded for slice-000" in message, (
        f"expected cause-name diagnostic prefix, got: {message!r}"
    )

    # Both glob patterns named — as FORWARD-SLASH strings (per /critique m4).
    # On Windows, str(Path(...)) produces backslash-separated text; the
    # helper formats via raw f-string templates, NOT str(Path(...)), so
    # these substring assertions hold identically on Windows and POSIX.
    assert "architecture/slices/slice-000-*" in message, (
        f"diagnostic must name the ACTIVE glob pattern (forward-slash form); "
        f"got: {message!r}"
    )
    assert "architecture/slices/archive/slice-000-*" in message, (
        f"diagnostic must name the ARCHIVE glob pattern (forward-slash form); "
        f"got: {message!r}"
    )


# ---------------------------------------------------------------------------
# AC4 row 4 — corpus class-closure backstop (per /critique-review M-add-2)
# ---------------------------------------------------------------------------


# Whitelist for the corpus backstop. Each entry is (relative_path, line_number).
# This is the explicit deferral surface for R-15-class instances slice-056
# acknowledges-but-does-not-fix.
#
# Whitelist-shrinkage mechanism for R-15 part-(b) retirement: when the
# slice-034 retrofit ships and removes the slice-034 literal from
# test_ptffd1_no_false_positive.py, REMOVE the entry below + the assertion
# becomes "match-set ⊆ ∅" → empty match-set required → R-15 part-(b)
# structurally satisfied without waiting for cross-slice observational
# evidence. This is the M-add-2 closure mechanism per slice-056
# critique-review.md.
_R15_CORPUS_WHITELIST: set[tuple[str, int]] = {
    # slice-034 archive-path reference in PTFFD-1 corpus regression test.
    # Already on the archive side, not breaking today, latent under slice-034
    # rename pressure only. Deferred to the slice-034 retrofit slice per
    # slice-056 /critique M1 ACCEPTED-FIXED.
    ("tests/methodology/test_ptffd1_no_false_positive.py", 70),
}

# Regex for R-15-class archive-fragile literal-path-RHS: matches both active
# (``REPO_ROOT / "architecture" / "slices" / "slice-NNN-...``) AND archive
# (``REPO_ROOT / "architecture" / "slices" / "archive" / "slice-NNN-...``)
# shapes anchored on a 3-digit slice number suffix. Whitespace-tolerant.
_R15_LITERAL_PATH_RE = re.compile(
    r'REPO_ROOT\s*/\s*"architecture"\s*/\s*"slices"\s*/\s*(?:"archive"\s*/\s*)?"slice-\d{3}-'
)


def test_no_new_archive_fragile_literals_in_methodology_corpus() -> None:
    """Corpus class-closure backstop for R-15 (per /critique-review M-add-2
    ACCEPTED-FIXED).

    Scans every ``tests/methodology/*.py`` file for R-15-class
    archive-fragile literal-path-RHS substrings and asserts the match-set
    is a subset of the known whitelist. The whitelist explicitly tracks
    deferred R-15-class instances slice-056 acknowledges-but-does-not-fix.

    When a new test module hardcodes a ``REPO_ROOT / "architecture" /
    "slices" / [archive/] "slice-NNN-..."`` literal-path-RHS, this test
    FAILs with a clear diagnostic naming the offending file + line.
    Mitigation: use ``_resolve_slice_dir(NNN)`` from
    ``tests.methodology.conftest`` instead.

    Whitelist-shrinkage is the M-add-2 structural mechanism for R-15
    part-(b) retirement (slice-056 /critique m2 + M-add-2 combined).
    """
    methodology_dir = REPO_ROOT / "tests" / "methodology"
    assert methodology_dir.is_dir(), (
        f"tests/methodology/ directory missing at {methodology_dir}"
    )

    matches: set[tuple[str, int]] = set()
    for py_file in sorted(methodology_dir.rglob("*.py")):
        # Skip this file itself (the whitelist + regex constants ARE the
        # literal patterns the regex matches; including them would create
        # a false-positive self-match — verified at design-time).
        if py_file.resolve() == Path(__file__).resolve():
            continue

        text = py_file.read_text(encoding="utf-8")
        rel = py_file.relative_to(REPO_ROOT).as_posix()
        # Scan the whole file text in one pass so multi-line constructions
        # (e.g., `slice034 = (\n    REPO_ROOT / "architecture" / "slices"
        # / "archive"\n    / "slice-034-..."` at test_ptffd1_no_false_positive.py:70-71)
        # match — the regex's ``\s*`` segments span newlines by default in
        # Python re. Line number is derived from the match start offset.
        for m in _R15_LITERAL_PATH_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            matches.add((rel, line_no))

    unexpected = matches - _R15_CORPUS_WHITELIST
    assert not unexpected, (
        f"R-15-class archive-fragile literal-path-RHS detected in "
        f"tests/methodology/ corpus at non-whitelisted sites: "
        f"{sorted(unexpected)}. "
        f"Use _resolve_slice_dir(NNN) from tests.methodology.conftest "
        f"instead of hardcoding the slice path. See R-15 in "
        f"architecture/risk-register.md."
    )

    # Also assert the whitelist hasn't grown stale: every whitelisted entry
    # must still exist in the corpus. A whitelist entry pointing at a
    # already-fixed surface is dead code that should be pruned.
    missing_whitelist = _R15_CORPUS_WHITELIST - matches
    assert not missing_whitelist, (
        f"_R15_CORPUS_WHITELIST contains entries no longer present in the "
        f"corpus: {sorted(missing_whitelist)}. The whitelist has shrunk — "
        f"remove these entries. If the whitelist is now empty, R-15 part-(b) "
        f"is structurally satisfied; consider transitioning R-15 to retired "
        f"in architecture/risk-register.md."
    )
