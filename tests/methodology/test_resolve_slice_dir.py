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
# (slice-105 / ADR-095 removed the AC3 structural pin
# `test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir` here: its
# target `tests/methodology/test_bcr_1_round_trip_end_to_end.py` is deleted by
# slice-105 — the BCR-1 round-trip the module verified is retired — so the pinned
# contract (that module no longer carries the archive-fragile literal RHS) no
# longer has a subject. `_resolve_slice_dir(54)` itself stays exercised by the
# archived-slice resolution tests below.)
# ---------------------------------------------------------------------------


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
#
# Retirement-discharge witness (slice-057, 2026-05-21): the whitelist is now
# empty because slice-057 retrofitted the lone deferred R-15-class entry (the
# PTFFD-1 corpus regression test's slice-034 archive-path reference) to use
# the slice-056 _resolve_slice_dir helper. Empty whitelist + empty match-set
# means BOTH halves of the backstop assertion are trivially satisfied today,
# AND any future R-15-class literal added anywhere under tests/methodology
# will trip the unexpected-matches half (the durable forever-pin). The
# missing_whitelist half stays as a regression-tripwire if a future
# maintainer adds a stale whitelist entry (a tuple referring to a file or
# line that no longer carries the offending construction).
#
# This is the M-add-2 structural closure mechanism per slice-056
# critique-review.md M-add-2 ACCEPTED-FIXED: whitelist-shrinkage to the
# empty set is the structural witness for R-15 part-(b) retirement, without
# waiting for cross-slice observational evidence.
#
# R-15 is RETIRED in architecture/risk-register.md as of slice-057
# (retirement-discharge class — no methodology-changelog entry / no ADR / no
# VERSION bump per slice-040 R-10 / slice-043 R-6 / slice-045 R-11 / slice-
# 056 R-15-part-(a) N=4 precedent; MEPD-1(b) discharged-by-name against the
# META-1 vacuous-satisfaction assertion at test_methodology_changelog.py).
_R15_CORPUS_WHITELIST: set[tuple[str, int]] = set()

# Regex for R-15-class archive-fragile literal-path-RHS: matches both active
# (``REPO_ROOT / "architecture" / "slices" / "slice-NNN-...``) AND archive
# (``REPO_ROOT / "architecture" / "slices" / "archive" / "slice-NNN-...``)
# shapes anchored on a 3-digit slice number suffix. Whitespace-tolerant.
_R15_LITERAL_PATH_RE = re.compile(
    r'REPO_ROOT\s*/\s*"architecture"\s*/\s*"slices"\s*/\s*(?:"archive"\s*/\s*)?"slice-\d{3}-'
)


def _scan_corpus_for_r15_literals(corpus_dir: Path) -> set[tuple[str, int]]:
    """Scan a test corpus directory for R-15-class archive-fragile
    literal-path-RHS substrings; return the set of (relative-posix-path,
    line-number) match sites.

    Per slice-062 / ADR-060 (extends slice-056 backstop scope from
    ``tests/methodology/*.py`` to all three test corpora —
    ``tests/methodology/**`` + ``tests/skills/**`` + ``tests/agents/**``).
    Helper extracted from the original inlined body of
    ``test_no_new_archive_fragile_literals_in_methodology_corpus`` per
    /design-slice ADR-060 §"Decision" option 3 (extract helper + 3
    per-corpus test functions + 1 aggregated whitelist-integrity test;
    walk-proof falls out structurally because each per-corpus test's
    pytest collection + pass IS the proof its corpus is walked).

    Encapsulates: ``sorted(rglob('*.py'))`` walk, self-skip (this very
    file is excluded — the whitelist + regex constants ARE the literal
    patterns the regex matches, so including them creates false-positive
    self-match; the skip is meaningful for the methodology-corpus scan
    and a no-op for skills/agents scans where this file does not live),
    ``_R15_LITERAL_PATH_RE.finditer(text)`` over the whole file (Python
    ``\\s*`` spans newlines so multi-line constructions like the
    slice-034 ``test_ptffd1_no_false_positive.py:70-71`` construction
    match — slice-056 N=1 lesson), line-number-from-offset compute, and
    repo-relative POSIX path normalization.

    NO behavior change vs the prior inlined logic at the methodology-corpus
    call site — per-line equivalent refactor (verified at /design-slice
    empirical pass).

    Args:
        corpus_dir: absolute Path to the test corpus directory to scan
            (e.g., ``REPO_ROOT / "tests" / "methodology"``). MUST exist
            as a directory; caller asserts via ``corpus_dir.is_dir()``
            before invoking.

    Returns:
        Set of (relative-posix-path, line-number) tuples naming every
        R-15-class match found. Empty set on a clean corpus.
    """
    matches: set[tuple[str, int]] = set()
    for py_file in sorted(corpus_dir.rglob("*.py")):
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
    return matches


def _assert_corpus_clean(
    matches: set[tuple[str, int]], corpus_label: str
) -> None:
    """Assert helper-output ``matches`` is a subset of the whitelist;
    raise AssertionError with the canonical R-15 diagnostic + mitigation
    hint on violation.

    Shared by the 3 per-corpus test wrappers
    (``test_no_new_archive_fragile_literals_in_<corpus>_corpus``). The
    ``corpus_label`` is interpolated into the diagnostic message so the
    failing test names its corpus unambiguously.
    """
    unexpected = matches - _R15_CORPUS_WHITELIST
    assert not unexpected, (
        f"R-15-class archive-fragile literal-path-RHS detected in "
        f"{corpus_label} corpus at non-whitelisted sites: "
        f"{sorted(unexpected)}. "
        f"Use _resolve_slice_dir(NNN) from tests.methodology.conftest "
        f"instead of hardcoding the slice path. See R-15 in "
        f"architecture/risk-register.md."
    )


def test_no_new_archive_fragile_literals_in_methodology_corpus() -> None:
    """Corpus class-closure backstop for R-15 — ``tests/methodology/`` arm.

    Per slice-056 /critique-review M-add-2 ACCEPTED-FIXED (the original
    methodology-corpus backstop) + slice-062 ADR-060 (extracted-helper
    wrapper shape; existing function name PRESERVED per ADR-060 §"Decision"
    paragraph 3 — the scope-claiming suffix ``_in_methodology_corpus`` is
    locally accurate; the wider-scope coverage is delivered via two NEW
    per-corpus test functions below).

    Scans every ``tests/methodology/*.py`` file via the shared
    ``_scan_corpus_for_r15_literals`` helper and asserts the match-set is
    a subset of the shared ``_R15_CORPUS_WHITELIST``. The aggregated
    whitelist-orphan check (``_R15_CORPUS_WHITELIST ⊆ union(all 3
    corpora matches)``) lives in
    ``test_r15_corpus_whitelist_has_no_orphan_entries`` below — moved
    out-of-line per ADR-060 §"Decision" paragraph 2 (the per-function
    shrinkage check would be incorrect on a per-wrapper basis after
    extraction, since the shared whitelist might contain documented-
    deferred sites from other corpora).
    """
    methodology_dir = REPO_ROOT / "tests" / "methodology"
    assert methodology_dir.is_dir(), (
        f"tests/methodology/ directory missing at {methodology_dir}"
    )
    matches = _scan_corpus_for_r15_literals(methodology_dir)
    _assert_corpus_clean(matches, "tests/methodology/")


def test_no_new_archive_fragile_literals_in_tests_skills_corpus() -> None:
    """Corpus class-closure backstop for R-15 — ``tests/skills/`` arm
    (NEW per slice-062 ADR-060; scope-extension surface #1).

    Closes the slice-061 N=1 watch-list scope gap (slice-060's
    ``tests/skills/code_review/test_code_review_skill.py:17`` hardcoded
    archive-fragile literal that broke at first archive). Per slice-062
    Phase B, the offending literal is repointed via
    ``_resolve_slice_dir(60)`` from ``tests.methodology.conftest``;
    post-repoint, this test PASSES because the wider corpus is then
    literal-free. This test's pytest-collection + pass IS the structural
    walk-proof that ``tests/skills/**`` is actually visited by the
    backstop (per ADR-060 §"Decision" paragraph 1 walk-proof discipline).
    """
    skills_dir = REPO_ROOT / "tests" / "skills"
    assert skills_dir.is_dir(), (
        f"tests/skills/ directory missing at {skills_dir}"
    )
    matches = _scan_corpus_for_r15_literals(skills_dir)
    _assert_corpus_clean(matches, "tests/skills/")


def test_no_new_archive_fragile_literals_in_tests_agents_corpus() -> None:
    """Corpus class-closure backstop for R-15 — ``tests/agents/`` arm
    (NEW per slice-062 ADR-060; scope-extension surface #2).

    Currently clean (no R-15-class literals in ``tests/agents/`` at
    slice-062 ship time — verified empirically at /design-slice). This
    test's pytest-collection + pass IS the structural walk-proof that
    ``tests/agents/**`` is actually visited by the backstop (per ADR-060
    §"Decision" paragraph 1 walk-proof discipline).
    """
    agents_dir = REPO_ROOT / "tests" / "agents"
    assert agents_dir.is_dir(), (
        f"tests/agents/ directory missing at {agents_dir}"
    )
    matches = _scan_corpus_for_r15_literals(agents_dir)
    _assert_corpus_clean(matches, "tests/agents/")


def test_r15_corpus_whitelist_has_no_orphan_entries() -> None:
    """Aggregated whitelist-integrity check across all 3 test corpora
    (NEW per slice-062 ADR-060; replaces the prior per-function
    ``missing_whitelist`` shrinkage check from the slice-056 design).

    Asserts ``_R15_CORPUS_WHITELIST ⊆ union(matches_methodology,
    matches_skills, matches_agents)`` — i.e., every whitelisted entry
    must still exist somewhere in the scanned corpora. A whitelist entry
    pointing at a no-longer-present surface is dead code that should be
    pruned. When the whitelist becomes empty AND the corpus scans are
    clean, the M-add-2 whitelist-shrinkage mechanism structurally
    satisfies R-15 part-(b) (slice-056 /critique m2 + M-add-2 combined;
    discharged at slice-057 + extended at slice-062 to the wider scope).

    Aggregated across all 3 corpora because the whitelist is shared
    (ADR-060 §"Decision" paragraph 2): a per-corpus shrinkage check
    would falsely flag entries that live in a sibling corpus.
    """
    methodology_dir = REPO_ROOT / "tests" / "methodology"
    skills_dir = REPO_ROOT / "tests" / "skills"
    agents_dir = REPO_ROOT / "tests" / "agents"
    assert methodology_dir.is_dir(), (
        f"tests/methodology/ directory missing at {methodology_dir}"
    )
    assert skills_dir.is_dir(), (
        f"tests/skills/ directory missing at {skills_dir}"
    )
    assert agents_dir.is_dir(), (
        f"tests/agents/ directory missing at {agents_dir}"
    )
    all_matches = (
        _scan_corpus_for_r15_literals(methodology_dir)
        | _scan_corpus_for_r15_literals(skills_dir)
        | _scan_corpus_for_r15_literals(agents_dir)
    )
    missing_whitelist = _R15_CORPUS_WHITELIST - all_matches
    assert not missing_whitelist, (
        f"_R15_CORPUS_WHITELIST contains entries no longer present in any "
        f"scanned corpus: {sorted(missing_whitelist)}. The whitelist has "
        f"shrunk — remove these entries. If the whitelist is now empty AND "
        f"all 3 per-corpus tests PASS, R-15 part-(b) is structurally "
        f"satisfied for the post-slice-062 wider scope; the R-15 risk-"
        f"register entry's `**Status**:` is already `retired` (slice-057) "
        f"and the slice-062 scope-extension paragraph documents the wider "
        f"coverage."
    )
