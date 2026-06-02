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
