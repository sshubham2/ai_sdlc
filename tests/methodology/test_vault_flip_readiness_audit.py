"""Tests for the vault-flip readiness audit (slice-100 / ADR-091).

Pins the context-aware ordered ruleset, the must-rewrite + needs-human baseline
(AC3), CLI gate semantics (AC4), and the capability-without-flip invariant (AC5).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.vault_flip_readiness_audit import (
    audit_file,
    audit_root,
    MUST_REWRITE,
    ALREADY_SEAM_ROUTED,
    DOC_EXAMPLE_SAFE,
    NEEDS_HUMAN,
    TEST_UPDATE_AT_FLIP,
    TEST_COLLECTION_PATHSPEC,
    _ALL_CLASSES,
    _BASELINE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


def _write_tool(tmp_path: Path, name: str, content: str) -> Path:
    tools = tmp_path / "tools"
    tools.mkdir(exist_ok=True)
    p = tools / name
    p.write_text(content, encoding="utf-8")
    return p


# ── AC1: inventory + classification ──────────────────────────────────────────
def test_emits_classified_inventory_with_evidence():
    result = audit_root(REPO_ROOT)
    assert result.files_scanned > 0
    assert result.occurrences, "expected a non-empty classified inventory"
    for o in result.occurrences:
        assert o.path and o.line >= 1 and o.col >= 0
        assert o.klass in _ALL_CLASSES
        assert o.reason
    classes = {o.klass for o in result.occurrences}
    assert MUST_REWRITE in classes
    assert ALREADY_SEAM_ROUTED in classes
    assert DOC_EXAMPLE_SAFE in classes


def test_every_hit_has_exactly_one_class(tmp_path):
    p = _write_tool(tmp_path, "x.py", 'import pathlib\nP = pathlib.Path("architecture/triage.md")\n')
    occ = audit_file(p, "tools/x.py")
    assert len(occ) == 1
    assert occ[0].klass == MUST_REWRITE
    assert occ[0].reason == "path-construction"


def test_unmarked_git_pathspec_routes_to_needs_human(tmp_path):
    p = _write_tool(tmp_path, "h.py", 'S = ("architecture/shippability.md",)\n')
    occ = audit_file(p, "tools/h.py")
    assert len(occ) == 1
    assert occ[0].klass == NEEDS_HUMAN
    assert occ[0].reason == "unmarked-collection-pathspec"


# ── AC2: fail-closed + deterministic ─────────────────────────────────────────
def test_ambiguous_literal_routes_to_needs_human_not_dropped(tmp_path):
    p = _write_tool(tmp_path, "g.py", 'S = frozenset({"architecture/slice-queue.md"})\n')
    occ = audit_file(p, "tools/g.py")
    assert len(occ) == 1, "ambiguous literal must be reported, never silently dropped"
    assert occ[0].klass == NEEDS_HUMAN


def test_output_is_deterministic_across_runs():
    assert audit_root(REPO_ROOT).to_dict() == audit_root(REPO_ROOT).to_dict()


# ── AC3: baseline pin + non-vacuity by two mutations ─────────────────────────
def test_must_rewrite_baseline_pinned():
    live = audit_root(REPO_ROOT).baseline_tuple()
    assert live == tuple(sorted(_BASELINE)), (
        "must-rewrite + needs-human baseline drifted; route the new literal through "
        "VAULT_ROOT (or mark it Class-B), or update _BASELINE deliberately. live=" + repr(live)
    )


def test_new_unrouted_literal_fails_gate(tmp_path):
    # non-vacuity (a): a bare-"architecture" /-BinOp path-construction MUST enter must-rewrite (B-add-1)
    p = _write_tool(tmp_path, "new.py",
                    'import pathlib\nq = pathlib.Path("/root") / "architecture" / "x.md"\n')
    must = [o for o in audit_file(p, "tools/new.py") if o.klass == MUST_REWRITE]
    assert must, "a bare-segment path-construction literal must classify must-rewrite (B-add-1)"
    assert must[0].value == "architecture"


def test_error_message_literal_not_must_rewrite(tmp_path):
    # non-vacuity (b) / B1 guard: an error-MESSAGE vault literal MUST NOT be must-rewrite
    p = _write_tool(tmp_path, "msg.py",
                    'def f(register):\n'
                    '    return f"architecture/risk-register.md not found at {register}"\n')
    occ = audit_file(p, "tools/msg.py")
    assert len(occ) == 1
    assert occ[0].klass == DOC_EXAMPLE_SAFE
    assert occ[0].klass != MUST_REWRITE


def test_class_b_marker_routes_to_already_seam_routed(tmp_path):
    # rule 2 (marker) precedes rule 4 (collection) — a marked git-pathspec is routed, not needs-human
    p = _write_tool(tmp_path, "cb.py",
                    'S = frozenset({\n'
                    '    "architecture/slice-queue.md",  # Class-B git identity (ADR-089)\n'
                    '})\n')
    occ = audit_file(p, "tools/cb.py")
    assert occ[0].klass == ALREADY_SEAM_ROUTED
    assert occ[0].reason == "class-b-marked"


# ── AC4: CLI gate semantics ──────────────────────────────────────────────────
def test_cli_exit_zero_when_no_needs_human():
    proc = subprocess.run([PY, "-m", "tools.vault_flip_readiness_audit"],
                          cwd=REPO_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_cli_strict_nonzero_on_baseline_drift(tmp_path):
    _write_tool(tmp_path, "drift.py",
                'import pathlib\np = pathlib.Path("/r") / "architecture" / "z.md"\n')
    proc = subprocess.run(
        [PY, "-m", "tools.vault_flip_readiness_audit", "--strict", "--repo-root", str(tmp_path)],
        cwd=REPO_ROOT, capture_output=True, text=True)
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)


# ── AC5: capability-without-flip ─────────────────────────────────────────────
def test_vault_paths_default_unchanged():
    src = (REPO_ROOT / "tools" / "_vault_paths.py").read_text(encoding="utf-8")
    assert '_DEFAULT = "architecture"' in src
    from tools import _vault_paths
    assert _vault_paths.VAULT_ROOT == Path("architecture")


# ── documented residual (slice-095 honest-contract) ──────────────────────────
def test_documented_residual_fully_dynamic_path_invisible(tmp_path):
    # a path with NO single architecture/diagnose-out string-literal segment is invisible
    p = _write_tool(tmp_path, "dyn.py",
                    'import pathlib\nseg = "arch" + "itecture"\n'
                    'p = pathlib.Path("/r") / seg / "x.md"\n')
    occ = audit_file(p, "tools/dyn.py")
    assert all(o.value != "architecture" for o in occ)


# ── code-review in-slice hardening (M1 / M2 / M3 / m1) ───────────────────────
def test_module_level_assigned_name_flows_to_path(tmp_path):
    # M1: a MODULE-level constant assigned the bare segment, then used in a /-BinOp,
    # must classify must-rewrite (was dead — _enclosing_func is None at module scope).
    p = _write_tool(tmp_path, "modlevel.py",
                    'import pathlib\n_DIR = "architecture"\n'
                    'P = pathlib.Path("/r") / _DIR / "x.md"\n')
    occ = [o for o in audit_file(p, "tools/modlevel.py") if o.klass == MUST_REWRITE]
    assert occ, "module-level assigned-name flow into a path must classify must-rewrite (M1)"
    assert occ[0].reason == "path-construction-1hop"


def test_prose_marker_comment_does_not_false_route_path_construction(tmp_path):
    # M2 (slice-099 whole-line-substring lesson): a prose comment mentioning a marker
    # on a real RESOLVING line must NOT route the path-construction to already-routed.
    p = _write_tool(tmp_path, "marker_false.py",
                    'P = open("architecture/x.md")  # see the Class-B git identity (ADR-089) convention\n')
    assert audit_file(p, "tools/marker_false.py")[0].klass == MUST_REWRITE
    p2 = _write_tool(tmp_path, "vroot_false.py",
                     'P = open("architecture/x.md")  # not VAULT_ROOT-routed yet\n')
    assert audit_file(p2, "tools/vroot_false.py")[0].klass == MUST_REWRITE


def test_dynamic_fragment_in_path_routes_to_needs_human(tmp_path):
    # M3: a partial-constant path fragment flowing into a path context is fail-closed.
    p = _write_tool(tmp_path, "fstr.py",
                    'import pathlib\ndef f(name):\n    return pathlib.Path("/r") / f"architecture/{name}"\n')
    occ = [o for o in audit_file(p, "tools/fstr.py") if o.klass == NEEDS_HUMAN]
    assert occ and occ[0].reason == "dynamic-fragment"
    p2 = _write_tool(tmp_path, "concat.py",
                     'def f(name):\n    return open("architecture/" + name)\n')
    occ2 = [o for o in audit_file(p2, "tools/concat.py") if o.klass == NEEDS_HUMAN]
    assert occ2 and occ2[0].reason == "dynamic-fragment"


def test_os_path_join_and_open_are_path_construction(tmp_path):
    # m1: os.path.join + builtin open are silent-breakage path-construction sinks.
    p = _write_tool(tmp_path, "ospj.py",
                    'import os\nP = os.path.join("architecture", "triage.md")\n')
    assert audit_file(p, "tools/ospj.py")[0].klass == MUST_REWRITE
    p2 = _write_tool(tmp_path, "openb.py", 'P = open("architecture/x.md")\n')
    assert audit_file(p2, "tools/openb.py")[0].klass == MUST_REWRITE


# ══ slice-102 / [[ADR-092]]: the tests/**/*.py surface ════════════════════════
# Floors are emptiness/collapse guards (m1), set comfortably below the measured
# live counts at slice-102 (test-update-at-flip 160; test-collection-pathspec 49);
# they catch a silent collapse of EITHER classification branch, NOT exact membership.
FLOOR_TEST_UPDATE_AT_FLIP = 120
FLOOR_TEST_COLLECTION_PATHSPEC = 30


# ── AC1: tests surface scanned + classified; production unchanged ─────────────
def test_tests_surface_scanned_and_classified():
    result = audit_root(REPO_ROOT)
    tests_occ = [o for o in result.occurrences if o.surface == "tests"]
    assert tests_occ, "the tests/**/*.py surface must be scanned and classified"
    for o in tests_occ:
        assert o.path.startswith("tests/")
        assert o.line >= 1 and o.col >= 0 and o.reason
        assert o.klass in _ALL_CLASSES
    klasses = {o.klass for o in tests_occ}
    assert TEST_UPDATE_AT_FLIP in klasses
    assert TEST_COLLECTION_PATHSPEC in klasses


def test_production_baseline_unchanged_vs_slice100():
    # AC1: extending to the tests surface must NOT perturb the production classification.
    result = audit_root(REPO_ROOT)
    prod_baseline = tuple(sorted(
        o.key() for o in result.occurrences
        if o.surface == "production" and o.klass in (MUST_REWRITE, NEEDS_HUMAN)))
    assert prod_baseline == tuple(sorted(_BASELINE))
    assert not [o for o in result.occurrences
                if o.surface == "production" and o.klass == NEEDS_HUMAN], \
        "slice-100 invariant: production needs-human is empty"


# ── AC2: loud-vs-silent two-class fidelity + write_text-content fix ───────────
def test_tests_path_resolve_is_test_update_at_flip(tmp_path):
    # a path-CONSTRUCTION literal the test resolves → the loud-breakage update checklist;
    # the IDENTICAL literal on production stays the silent must-rewrite class.
    p = _write_tool(tmp_path, "x.py", 'import pathlib\nP = pathlib.Path("architecture/triage.md")\n')
    occ = audit_file(p, "tests/methodology/x.py")
    assert len(occ) == 1
    assert occ[0].klass == TEST_UPDATE_AT_FLIP and occ[0].surface == "tests"
    assert audit_file(p, "tools/x.py")[0].klass == MUST_REWRITE


def test_tests_collection_pathspec_is_review_not_checklist(tmp_path):
    # a collection-member git-pathspec/Class-B mirror → the REVIEW list, distinct from
    # the update checklist AND from fail-closed needs-human; on production it is needs-human.
    p = _write_tool(tmp_path, "h.py", 'S = ("architecture/shippability.md",)\n')
    occ = audit_file(p, "tests/skills/parallel_conflict_resolver/h.py")
    assert len(occ) == 1
    assert occ[0].klass == TEST_COLLECTION_PATHSPEC
    assert occ[0].klass not in (TEST_UPDATE_AT_FLIP, NEEDS_HUMAN)
    assert audit_file(p, "tools/h.py")[0].klass == NEEDS_HUMAN


def test_write_text_content_is_not_path(tmp_path):
    # ADR-092 correctness fix: the write_text/write_bytes ARG is content, not a path —
    # on BOTH surfaces it must NOT be a resolving-path class (the receiver still is).
    p = _write_tool(tmp_path, "wt.py",
                    'def f(p):\n    return p.write_text("see architecture/triage.md")\n')
    assert audit_file(p, "tools/wt.py")[0].klass == DOC_EXAMPLE_SAFE
    assert audit_file(p, "tests/methodology/wt.py")[0].klass == DOC_EXAMPLE_SAFE
    # the f-string-content shape (the real test_drift_check_audit.py:35) — not needs-human
    p2 = _write_tool(tmp_path, "wt2.py",
                     'def f(p, mode):\n    return p.write_text(f"Mode {mode} see architecture/triage.md")\n')
    assert audit_file(p2, "tests/methodology/wt2.py")[0].klass == DOC_EXAMPLE_SAFE


# ── AC3: fail-closed completeness invariant + non-vacuity + per-class floors ──
def test_tests_surface_needs_human_empty():
    # fail-closed completeness: every tests-surface vault literal lands in a definite
    # class; nothing unclassifiable silently slips. Keyed (relpath, value, klass).
    result = audit_root(REPO_ROOT)
    leftover = [o.key() for o in result.occurrences
                if o.surface == "tests" and o.klass == NEEDS_HUMAN]
    assert leftover == [], f"tests-surface needs-human must be empty; got {leftover}"


def test_tests_surface_needs_human_pin_non_vacuous(tmp_path):
    # non-vacuity: a genuinely-unclassifiable tests literal (dynamic-fragment in a path
    # context) MUST land in needs-human → the empty-pin above is not vacuously true.
    p = _write_tool(tmp_path, "dyn.py",
                    'import pathlib\ndef f(name):\n    return pathlib.Path("/r") / f"architecture/{name}"\n')
    nh = [o for o in audit_file(p, "tests/methodology/dyn.py") if o.klass == NEEDS_HUMAN]
    assert nh and nh[0].reason == "dynamic-fragment"


def test_tests_surface_class_floors():
    # m1 — per-class non-vacuity floors guard a silent collapse of EITHER branch
    # (a single aggregate floor would miss 209→160). Floors < measured live counts.
    result = audit_root(REPO_ROOT)
    n_update = len(result.by_class(TEST_UPDATE_AT_FLIP))
    n_coll = len(result.by_class(TEST_COLLECTION_PATHSPEC))
    assert n_update >= FLOOR_TEST_UPDATE_AT_FLIP, f"test-update-at-flip={n_update}"
    assert n_coll >= FLOOR_TEST_COLLECTION_PATHSPEC, f"test-collection-pathspec={n_coll}"


# ── documented residuals (m3 + M-add-1; slice-095 honest-contract pattern) ────
def test_fixtures_dir_vault_literal_out_of_scope(tmp_path):
    # m3: a vault literal inside tests/**/fixtures/ is intentionally OUT of scan scope
    # (fixture dirs hold test-INPUT artifacts, not vault-resolving logic).
    (tmp_path / "tools").mkdir()
    fx = tmp_path / "tests" / "methodology" / "fixtures"
    fx.mkdir(parents=True)
    (fx / "f.py").write_text('import pathlib\nP = pathlib.Path("architecture/triage.md")\n',
                             encoding="utf-8")
    result = audit_root(tmp_path)
    assert not [o for o in result.occurrences if "fixtures" in o.path], \
        "fixtures/ vault literals must be out of scan scope (documented residual)"


def test_collection_member_genuine_resolve_is_review_residual(tmp_path):
    # M-add-1 (meta-Critic): a GENUINE path-resolve that is a bare collection-display
    # member is classified test-collection-pathspec (REVIEW, not the checklist, not
    # fail-closed) — the documented heterogeneity residual. Acceptable because the tests
    # surface breaks LOUDLY at flip; flip-execute MUST consume the review list too.
    p = _write_tool(tmp_path, "loop.py",
                    'import pathlib\n'
                    'for rel in ["architecture/slice-queue.md", "architecture/shippability.md"]:\n'
                    '    pathlib.Path("/r", rel).write_text("x")\n')
    occ = audit_file(p, "tests/methodology/loop.py")
    klasses = {o.klass for o in occ}
    assert klasses == {TEST_COLLECTION_PATHSPEC}, klasses
    assert TEST_UPDATE_AT_FLIP not in klasses and NEEDS_HUMAN not in klasses
