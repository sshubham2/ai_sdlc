"""SCMD-1 check (b) — incidental-decoupling invariant.

Per SCMD-1 (slice-031, split-label 030B; ADR-030 + ADR-031). Covers AC1/AC2/AC4
+ v2-M1 (closed-world under indirection), v2-M2 (concrete allowlist), v2-M4
(non-vacuous env-independence), v2-m2 (bidirectional corpus-completeness).

TF-1: the load-bearing failing-first tests use a SYNTHETIC catalog that cites
the REAL `tests/methodology/test_build_checks_audit.py` archive-backtests, so
they are WRITTEN-FAILING pre-T5 (those fns still read gitignored archive /
live build-checks) and PASSING post-T5 (repointed to tracked fixtures+corpus),
deterministically — independent of the real catalog's column rollout.
"""
from __future__ import annotations

import ast
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools import shippability_decoupling_audit as scmd
from tools.shippability_decoupling_audit import (
    _ALLOWLIST_SYMBOLS,
    _RESOLVE_THROUGH,
    audit,
    classify_fn,
    _index_module,
)

_BC_MODULE = "tests/methodology/test_build_checks_audit.py"
_CHANGELOG_MODULE = "tests/methodology/test_methodology_changelog.py"
_CORPUS_DIR = REPO_ROOT / "tests" / "methodology" / "fixtures" / \
    "archive_backtest_corpus"


def _synthetic_catalog(tmp_path: Path, rows: list[str]) -> Path:
    cat = tmp_path / "shippability.md"
    header = ("| # | Slice | Critical path | Command | Runtime | "
              "Machine-cmd |\n"
              "|---|-------|---------------|---------|---------|---------|\n")
    cat.write_text(header + "".join(rows), encoding="utf-8")
    return cat


def _row(n: int, machine_cmd: str) -> str:
    return f"| {n} | slice-{n} | crit | c | <2s | {machine_cmd} |\n"


# --------------------------------------------------------------------------- #
# AC1 — mechanical derivation from ALL rows (not a hand-coded subset)          #
# --------------------------------------------------------------------------- #
def test_cited_fn_set_derived_from_all_rows_not_enumerated(tmp_path: Path):
    """SCMD-1 derives the cited-fn set from EVERY row's Machine-cmd cell."""
    cat = _synthetic_catalog(tmp_path, [
        _row(1, f"`<interp> -m pytest {_BC_MODULE}::"
                f"test_slice_001_archive_still_fires_legitimate_rules -q`"),
        _row(2, f"`<interp> -m pytest {_CHANGELOG_MODULE}::"
                f"test_v_0_22_0_cad_1_entry_present_in_repo_and_installed -q`"),
    ])
    result = audit(cat, repo_root=REPO_ROOT)
    assert result.rows_scanned == 2
    assert result.cited_fns >= 2, (
        "derivation must span all rows, not a subset"
    )


# --------------------------------------------------------------------------- #
# AC1/AC2 — no incidental cited fn remains coupled (WRITTEN-FAILING pre-T5)    #
# --------------------------------------------------------------------------- #
def test_no_incidental_cited_fn_remains_coupled(tmp_path: Path):
    """The real archive-backtests, cited via a synthetic catalog, must NOT
    classify `incidental` (they must be decoupled to tracked fixtures+corpus).
    WRITTEN-FAILING pre-T5; PASSING post-T5."""
    cat = _synthetic_catalog(tmp_path, [
        _row(1, f"`<interp> -m pytest {_BC_MODULE}::"
                f"test_slice_001_archive_still_fires_legitimate_rules -q`"),
        _row(2, f"`<interp> -m pytest {_BC_MODULE}::"
                f"test_slice_005_archive_no_longer_fires_proj1_or_global1 -q`"),
    ])
    result = audit(cat, repo_root=REPO_ROOT)
    incidental = [v for v in result.violations
                  if v.kind == "incidental-coupling"]
    assert not incidental, (
        f"{len(incidental)} cited fn(s) still incidental/unresolved — first: "
        f"{incidental[0].detail}"
    )


# --------------------------------------------------------------------------- #
# v2-M1 — closed-world catches CONSTANT/CROSS-MODULE INDIRECTION               #
# --------------------------------------------------------------------------- #
def test_indirected_path_home_read_is_caught(tmp_path: Path):
    """A fn reading `~/.claude/build-checks.md` via a module-level constant
    (the real coupling shape: `_GLOBAL_BUILD_CHECKS = Path.home()/...`) MUST
    be caught — a naive literal-AST scan of the fn body alone would miss it."""
    mod = tmp_path / "test_indirect_fixture.py"
    mod.write_text(
        "from pathlib import Path\n"
        '_HIDDEN = Path.home() / ".claude" / "build-checks.md"\n'
        "def test_reads_indirected():\n"
        "    assert _HIDDEN.read_text()\n",
        encoding="utf-8",
    )
    idx = _index_module(mod)
    cls = classify_fn(idx.funcs["test_reads_indirected"], idx)
    assert cls == "incidental", (
        f"constant-indirected ~/.claude/build-checks.md read must classify "
        f"incidental; got {cls!r}"
    )


def test_clean_fn_reaching_only_allowlisted_symbol_is_clean(tmp_path: Path):
    mod = tmp_path / "test_clean_fixture.py"
    mod.write_text(
        "_CANONICAL_PROJECT_FIXTURE = object()\n"
        "def test_clean():\n"
        "    assert _CANONICAL_PROJECT_FIXTURE is not None\n",
        encoding="utf-8",
    )
    idx = _index_module(mod)
    assert classify_fn(idx.funcs["test_clean"], idx) == "clean"


# --------------------------------------------------------------------------- #
# essential entry-pin fns are RECOGNIZED and NOT flagged (030C domain)         #
# --------------------------------------------------------------------------- #
def test_essential_entry_pin_fn_recognized_not_flagged(tmp_path: Path):
    cat = _synthetic_catalog(tmp_path, [
        _row(1, f"`<interp> -m pytest {_CHANGELOG_MODULE}::"
                f"test_v_0_22_0_cad_1_entry_present_in_repo_and_installed -q`"),
    ])
    result = audit(cat, repo_root=REPO_ROOT)
    assert result.essential, "entry-pin fn must be classified essential"
    assert not any(v.kind == "incidental-coupling" for v in result.violations), (
        "essential entry-pin reads of ~/.claude/methodology-changelog.md must "
        "NOT be flagged here (chartered to 030C per the R-4 sub-entry)"
    )


# --------------------------------------------------------------------------- #
# v2-M4 — non-vacuous: decoupled fns have NO `.exists()`-gated skip            #
# --------------------------------------------------------------------------- #
_INCIDENTAL_BACKTEST_FNS = (
    "test_slice_001_archive_still_fires_legitimate_rules",
    "test_slice_003_archive_backtest_no_bc_proj_2_or_global_1_applications",
    "test_slice_005_archive_no_longer_fires_proj1_or_global1",
)


def _fn_source(fn_name: str) -> ast.FunctionDef:
    idx = _index_module(REPO_ROOT / _BC_MODULE)
    return idx.funcs[fn_name]


def test_decoupled_incidental_fns_have_no_exists_skip_guard():
    """v2-M4: post-decouple the archive-backtests must hard-assert — no
    `if _GLOBAL_BUILD_CHECKS.exists():`-gated skip remains. WRITTEN-FAILING
    pre-T5 (guards present), PASSING post-T5."""
    offenders: list[str] = []
    for fname in _INCIDENTAL_BACKTEST_FNS:
        fn = _fn_source(fname)
        for node in ast.walk(fn):
            if isinstance(node, ast.If):
                cond_src = ast.dump(node.test)
                if "exists" in cond_src and "_GLOBAL_BUILD_CHECKS" in cond_src:
                    offenders.append(fname)
                    break
    assert not offenders, (
        f"{offenders} still gate assertions behind "
        f"`if _GLOBAL_BUILD_CHECKS.exists():` — env-unavailable run would pass "
        f"vacuously (v2-M4)"
    )


def test_decoupled_incidental_fns_classify_clean():
    """The real archive-backtests must classify `clean` post-decouple
    (reach only tracked-fixture/corpus symbols). WRITTEN-FAILING pre-T5."""
    idx = _index_module(REPO_ROOT / _BC_MODULE)
    bad = {fn: classify_fn(idx.funcs[fn], idx)
           for fn in _INCIDENTAL_BACKTEST_FNS
           if classify_fn(idx.funcs[fn], idx) != "clean"}
    assert not bad, f"archive-backtests not yet decoupled: {bad}"


# --------------------------------------------------------------------------- #
# AC4 + v2-m2 — bidirectional corpus completeness                             #
# --------------------------------------------------------------------------- #
def test_every_derived_archive_folder_has_tracked_corpus_fixture(
        tmp_path: Path):
    """Bidirectional corpus completeness (AC4 + v2-m2). Authoritative set =
    every `slice-*` corpus folder REFERENCED by ANY decoupled backtest across
    the catalog-cited modules (not a hand-picked sample). Forward: every
    referenced folder has a tracked fixture. Reverse (v2-m2): no orphan
    fixture for a folder no decoupled fn references. WRITTEN-FAILING pre-T5
    (corpus dir absent)."""
    assert _CORPUS_DIR.is_dir(), (
        f"tracked corpus dir absent: {_CORPUS_DIR} (created in T5)"
    )
    corpus_folders = {p.name for p in _CORPUS_DIR.iterdir() if p.is_dir()}
    referenced: set[str] = set()
    for rel in (_BC_MODULE,
                "tests/methodology/test_validate_slice_layers.py"):
        idx = _index_module(REPO_ROOT / rel)
        for fn in idx.funcs.values():
            referenced |= scmd._collect_archive_folders(fn, idx)
    missing = referenced - corpus_folders
    orphan = corpus_folders - referenced
    assert not missing, f"referenced archive folders missing corpus: {missing}"
    assert not orphan, f"orphan corpus fixtures (v2-m2): {orphan}"


# --------------------------------------------------------------------------- #
# v2-M2 — allowlist membership pinned by identity (rename trips loudly)        #
# --------------------------------------------------------------------------- #
def test_allowlist_membership_is_exactly():
    assert _ALLOWLIST_SYMBOLS == frozenset({
        "_CANONICAL_PROJECT_FIXTURE",
        "_CANONICAL_GLOBAL_FIXTURE",
        "_ARCHIVE_BACKTEST_CORPUS",
    }), "allowlist drifted — a fixture-constant rename must trip THIS test"
    assert "_GLOBAL_BUILD_CHECKS" not in _ALLOWLIST_SYMBOLS, (
        "_GLOBAL_BUILD_CHECKS is must-be-repointed, never an allowlist member"
    )
    assert {"REPO_ROOT", "read_file"} <= _RESOLVE_THROUGH


# --------------------------------------------------------------------------- #
# real-catalog end-state (WRITTEN-FAILING until T3 column + T5 decouple + T7)  #
# --------------------------------------------------------------------------- #
def test_real_catalog_scmd1_clean():
    """End-state: the real shippability.md passes SCMD-1 with zero
    violations. WRITTEN-FAILING until T3+T5+T7 complete."""
    result = audit(REPO_ROOT / "architecture" / "shippability.md")
    assert not result.violations, (
        f"{len(result.violations)} SCMD-1 violation(s); first: "
        f"{result.violations[0].kind} — {result.violations[0].detail}"
    )
