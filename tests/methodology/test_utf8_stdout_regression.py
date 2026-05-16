"""UTF8-STDOUT-1 behavioural regression test (AC #4).

Invokes every audit tool via subprocess under a simulated Windows cp1252
parent-shell encoding. Confirms each tool's `_stdout.reconfigure_stdout_utf8()`
helper engages and U+2192 / U+2014 output survives without
UnicodeEncodeError / UnicodeDecodeError.

Per M1 + M-add-2 ACCEPTED-FIXED at slice-023: per-tool argv strategy
reflects each tool's verified argparse contract; failure assertion
targets "UnicodeEncodeError"/"UnicodeDecodeError" in stderr, NOT
exit code (synthetic fixtures may legitimately return exit 1 on
non-encoding violations like PENDING TF-1 rows or missing required
fields).

Split from `test_utf8_stdout_audit.py` per M5 ACCEPTED-FIXED for
runtime isolation (17×subprocess invocations ≈ 5-17s on Windows).
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "methodology" / "fixtures" / "utf8_stdout" / "slice-fixture"
PY = sys.executable


def _run_under_cp1252(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a subprocess simulating Windows cp1252 parent shell.

    Parent-side: text=True + encoding="utf-8" + errors="replace" so the
    parent's own decode doesn't crash on child's UTF-8 output.
    Child-side env: PYTHONIOENCODING=cp1252 + PYTHONUTF8=0 — simulates
    Windows default console encoding that the slice's helper fixes.
    """
    env = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(cwd) if cwd else None,
    )


def _assert_no_encoding_error(proc: subprocess.CompletedProcess, tool: str) -> None:
    """Assert subprocess produced no UnicodeEncodeError/UnicodeDecodeError."""
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "UnicodeEncodeError" not in combined, (
        f"{tool}: UnicodeEncodeError in output:\n{combined}"
    )
    assert "UnicodeDecodeError" not in combined, (
        f"{tool}: UnicodeDecodeError in output:\n{combined}"
    )


# Per-tool argv strategy per M1 + M-add-2 ACCEPTED-FIXED.
# Each entry: (tool-module, argv-construction-callable taking fixture_dir + tmp_path → argv-list)
# All argvs MUST resolve to a real input shape that reaches the tool's
# stdout-emitting code path.

def _positional_slice_argv(tool: str, fixture_dir: Path, tmp_path: Path) -> list[str]:
    return [PY, "-m", tool, str(fixture_dir)]


def _root_only_argv(tool: str, fixture_dir: Path, tmp_path: Path) -> list[str]:
    return [PY, "-m", tool, "--root", str(REPO_ROOT)]


# Tools requiring positional slice-folder
_POSITIONAL_SLICE_TOOLS = [
    "tools.branch_workflow_audit",
    "tools.test_first_audit",
    "tools.wiring_matrix_audit",
    "tools.walking_skeleton_audit",
    "tools.exploratory_charter_audit",
    "tools.build_checks_audit",
    "tools.triage_audit",
    "tools.cross_spec_parity_audit",
    "tools.supersede_audit",
    "tools.critique_review_prerequisite_audit",
]

# Tools with --root only
_ROOT_ONLY_TOOLS = [
    "tools.plugin_manifest_audit",
    "tools.utf8_stdout_audit",
    "tools.pipeline_chain_audit",
]


@pytest.mark.parametrize("tool", _POSITIONAL_SLICE_TOOLS)
def test_positional_slice_tool_survives_cp1252_with_u2192(tool):
    proc = _run_under_cp1252(_positional_slice_argv(tool, FIXTURE_DIR, REPO_ROOT))
    _assert_no_encoding_error(proc, tool)


@pytest.mark.parametrize("tool", _ROOT_ONLY_TOOLS)
def test_root_only_tool_survives_cp1252_with_u2192(tool):
    proc = _run_under_cp1252(_root_only_argv(tool, FIXTURE_DIR, REPO_ROOT))
    _assert_no_encoding_error(proc, tool)


def test_install_audit_survives_cp1252_with_u2192(tmp_path):
    """install_audit takes --claude-dir, NOT --root (per M-add-2)."""
    # Use the real ~/.claude dir to ensure the tool reaches the
    # surface-rename-emitting code path. install_audit returns exit 0/1
    # based on installed-vs-canonical match; we only care about encoding.
    proc = _run_under_cp1252(
        [PY, "-m", "tools.install_audit",
         "--claude-dir", str(Path.home() / ".claude")],
    )
    _assert_no_encoding_error(proc, "tools.install_audit")


def test_mock_budget_lint_survives_cp1252_with_u2192(tmp_path):
    """mock_budget_lint requires positional `files` (nargs="+") per M-add-2."""
    # Synthetic test file with U+2192 in a comment
    test_file = tmp_path / "test_synthetic.py"
    test_file.write_text(
        "# Synthetic test with arrow → and em-dash —\n"
        "from unittest.mock import patch\n"
        "def test_x(): pass\n",
        encoding="utf-8",
    )
    proc = _run_under_cp1252(
        [PY, "-m", "tools.mock_budget_lint", str(test_file)],
    )
    _assert_no_encoding_error(proc, "tools.mock_budget_lint")


def test_validate_slice_layers_survives_cp1252_with_u2192():
    """validate_slice_layers requires --slice (required=True) per M-add-2."""
    proc = _run_under_cp1252(
        [PY, "-m", "tools.validate_slice_layers", "--slice", str(FIXTURE_DIR)],
    )
    _assert_no_encoding_error(proc, "tools.validate_slice_layers")


def test_risk_register_audit_survives_cp1252_with_u2192(tmp_path):
    """risk_register_audit takes positional path to risk-register.md."""
    risk_file = tmp_path / "risk-register.md"
    risk_file.write_text(
        "# Risk Register\n\n"
        "## R-1 — Synthetic risk with U+2192 → arrow and U+2014 — em-dash\n\n"
        "**Likelihood**: low\n"
        "**Impact**: low\n"
        "**Status**: open\n",
        encoding="utf-8",
    )
    proc = _run_under_cp1252(
        [PY, "-m", "tools.risk_register_audit", str(risk_file)],
    )
    _assert_no_encoding_error(proc, "tools.risk_register_audit")


def test_critique_agent_drift_audit_survives_cp1252_with_u2192():
    """critique_agent_drift_audit takes --repo-root."""
    proc = _run_under_cp1252(
        [PY, "-m", "tools.critique_agent_drift_audit", "--repo-root", str(REPO_ROOT)],
    )
    _assert_no_encoding_error(proc, "tools.critique_agent_drift_audit")


def test_critique_review_audit_survives_cp1252_with_u2192():
    """critique_review_audit takes positional slice folder."""
    proc = _run_under_cp1252(
        [PY, "-m", "tools.critique_review_audit", str(FIXTURE_DIR)],
    )
    _assert_no_encoding_error(proc, "tools.critique_review_audit")


def test_shippability_path_audit_survives_cp1252_with_u2192(tmp_path):
    """shippability_path_audit takes a positional catalog path (slice-025).

    Synthetic catalog with U+2192 / U+2014 in the Critical-path cell and a
    real test-path token in the Command cell exercises the tool's
    stdout-emitting path under cp1252.
    """
    catalog = tmp_path / "shippability.md"
    catalog.write_text(
        "# Shippability Catalog\n\n"
        "| # | Slice | Critical path | Command | Runtime |\n"
        "|---|-------|--------------|---------|---------|\n"
        "| 1 | slice-x | arrow → and em-dash — in path | "
        "python -m pytest tests/methodology/test_stdout_helper.py -q | <1s |\n",
        encoding="utf-8",
    )
    proc = _run_under_cp1252(
        [PY, "-m", "tools.shippability_path_audit", str(catalog)],
    )
    _assert_no_encoding_error(proc, "tools.shippability_path_audit")


# ---------------------------------------------------------------------------
# UTF8-STDOUT-1 v1.1 — version-agnostic UTF-8 rollup sentinel
# (slice-028; ADR-026; mirrors the slice-014 / ADR-013 PMI-1 v1.0 -> v1.1
# 3-part template: derive-the-real-invariant + AST meta-test + failure-path
# regression. Rule-ID lineage preserved — UTF8-STDOUT-1, NOT a new rule ID.)
#
# The sentinel no longer asserts a hard-coded tool count (the slices
# 023/025/026/027 N=5 maintenance-tax class). It asserts BIDIRECTIONAL
# coverage-parity derived from repo state:
#
#   discovered_set == covered_set
#
# discovered_set : every tools/*.py (non-`_`, non-__init__) whose module AST
#                  has a top-level `main` FunctionDef — i.e. exactly the
#                  `tools_with_main` population UTF8-STDOUT-1 governs
#                  (utf8_stdout_audit._find_main_function semantics), NOT the
#                  looser _candidate_tools glob.
# covered_set    : tool tokens OBSERVED from this module's real cp1252 call
#                  sites — the string elements of _POSITIONAL_SLICE_TOOLS /
#                  _ROOT_ONLY_TOOLS (execution-bound: pytest parametrizes over
#                  them and runs the subprocess) UNION the second positional
#                  arg of each bespoke `_assert_no_encoding_error(proc, "<t>")`
#                  call (a source-presence proxy — the per-tool tests are the
#                  execution guarantee for that direction; the argv<->name
#                  binding is intentionally not verified here, per ADR-026).
#
# INDEPENDENT-COUNTER NOTE (relocated from the old count comment, per
# slice-028 /critique M3b): this sentinel governs `tools_with_main` cp1252
# coverage parity. It does NOT track and MUST NOT be conflated with the
# INST-1 `install_audit._CANONICAL_TOOLS` canonical-tuple inventory — that
# is a separate consumer-propagation site (slice-026 row 26 / slice-027 row
# 27 distinguish "INST-1 19->20" vs "UTF8-STDOUT-1 narrative 17->20"),
# explicitly out of slice-028's scope.
#
# Names scanned by the version-agnostic-shape meta-test (B-add-1: the parity
# assertion stays IN the sentinel body; set construction lives in the two
# helpers, which are ALSO scanned, so a count literal cannot hide in a
# helper). The counter-anchor test pins that set-construction primitives are
# confined to these two helpers.
_VERSION_AGNOSTIC_SCANNED: tuple[str, ...] = (
    "test_every_audit_tool_survives_cp1252_stdout_with_u2192_input",
    "_discovered_audit_tools",
    "_covered_tool_tokens",
)

_MODULE_PATH = Path(__file__).resolve()
_COVERED_PARAM_LISTS = ("_POSITIONAL_SLICE_TOOLS", "_ROOT_ONLY_TOOLS")
_COVERAGE_ASSERT_FUNC = "_assert_no_encoding_error"
_POST_SLICE_ANCHOR_RE = re.compile(r"post-slice-\d+")


def _discovered_audit_tools() -> frozenset[str]:
    """tools/*.py (non-`_`, non-__init__) whose AST has a top-level `main`.

    AST-only (no import of tools.*) — mirrors
    utf8_stdout_audit._find_main_function semantics so this set is exactly
    the `tools_with_main` population UTF8-STDOUT-1 actually governs.
    """
    tools_dir = REPO_ROOT / "tools"
    discovered: set[str] = set()
    for path in sorted(tools_dir.glob("*.py")):
        if path.name == "__init__.py" or path.name.startswith("_"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        has_main = any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "main"
            for node in tree.body
        )
        if has_main:
            discovered.add(f"tools.{path.stem}")
    return frozenset(discovered)


def _covered_tool_tokens() -> frozenset[str]:
    """Tool tokens observed from this module's real cp1252 call sites.

    Sources: (i) str elements of _POSITIONAL_SLICE_TOOLS / _ROOT_ONLY_TOOLS;
    (ii) the 2nd positional arg of every `_assert_no_encoding_error(proc,
    "<tool>")` call that passes a string literal (bespoke tests). Calls that
    pass the parametrize loop variable (an ast.Name) are the parametrized
    tests — their tokens come from (i), so the Name 2nd-arg is expected and
    skipped, not an error.

    FAILS CLOSED (slice-028 /critique-review M-add-1): any element of a
    covered param-list that is not a str Constant, or any
    `_assert_no_encoding_error` 2nd arg that is neither a str Constant nor a
    bare Name, raises a loud named diagnostic — it is NEVER silently
    skipped (silent-skip would drop a coverage token -> an uncovered tool
    falsely GREEN, defeating AC#2).
    """
    tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"), filename=str(_MODULE_PATH))
    covered: set[str] = set()

    for node in ast.walk(tree):
        # (i) the two module-level parametrize list constants
        if isinstance(node, ast.Assign):
            target_names = {
                t.id for t in node.targets if isinstance(t, ast.Name)
            }
            if target_names & set(_COVERED_PARAM_LISTS):
                if not isinstance(node.value, ast.List):
                    raise AssertionError(
                        f"M-add-1 fail-closed: covered param-list "
                        f"{sorted(target_names & set(_COVERED_PARAM_LISTS))} at "
                        f"line {node.lineno} is not a flat ast.List literal "
                        f"(got {type(node.value).__name__}) — the covered-set "
                        f"AST walk no longer recognizes this shape; coverage "
                        f"tokens would be silently dropped. Update "
                        f"_covered_tool_tokens deliberately."
                    )
                for elt in node.value.elts:
                    if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
                        raise AssertionError(
                            f"M-add-1 fail-closed: covered param-list element "
                            f"at line {getattr(elt, 'lineno', node.lineno)} is "
                            f"not a str Constant (got "
                            f"{type(elt).__name__}) — unrecognized shape; "
                            f"coverage token would be dropped. Update "
                            f"_covered_tool_tokens deliberately."
                        )
                    covered.add(elt.value)
        # (ii) bespoke `_assert_no_encoding_error(proc, "<tool>")` calls
        if isinstance(node, ast.Call):
            func = node.func
            is_target = (
                isinstance(func, ast.Name) and func.id == _COVERAGE_ASSERT_FUNC
            )
            if is_target and len(node.args) >= 2:
                second = node.args[1]
                if isinstance(second, ast.Constant) and isinstance(second.value, str):
                    covered.add(second.value)
                elif isinstance(second, ast.Name):
                    # parametrized loop var (e.g. `tool`) — tokens come from
                    # the param lists in branch (i); expected, skip.
                    continue
                else:
                    raise AssertionError(
                        f"M-add-1 fail-closed: {_COVERAGE_ASSERT_FUNC} 2nd arg "
                        f"at line {node.lineno} is neither a str Constant nor "
                        f"a bare Name (got {type(second).__name__}) — "
                        f"unrecognized bespoke coverage shape; the covered-set "
                        f"walk would mis-derive. Update _covered_tool_tokens "
                        f"deliberately."
                    )
    return frozenset(covered)


def test_every_audit_tool_survives_cp1252_stdout_with_u2192_input():
    """version-agnostic UTF-8 rollup sentinel (UTF8-STDOUT-1 v1.1; slice-028;
    ADR-026). Shippability row 23 single named target.

    Asserts BIDIRECTIONAL coverage-parity derived from repo state — every
    audit tool UTF8-STDOUT-1 governs (tools/*.py with a top-level `main`) is
    exercised under cp1252 somewhere in this module, and no observed
    coverage token is a phantom. NO hard-coded tool count, NO post-slice-NNN
    anchor (the slices 023/025/026/027 N=5 count-bump maintenance-tax class
    is retired). See the module-level UTF8-STDOUT-1 v1.1 block + ADR-026 for
    the discovered/covered definitions and the independent-counter note.
    """
    discovered = _discovered_audit_tools()
    covered = _covered_tool_tokens()
    uncovered = sorted(discovered - covered)
    phantom = sorted(covered - discovered)
    assert not uncovered and not phantom, (
        "version-agnostic UTF-8 rollup sentinel: cp1252 coverage parity "
        "broken.\n"
        f"  Uncovered audit tool(s) (have a main(), no cp1252 coverage — "
        f"add a parametrize-list entry or a bespoke test_*): {uncovered}\n"
        f"  Phantom coverage token(s) (referenced in a cp1252 call site, no "
        f"matching main()-bearing tools/*.py — stale after rename/removal): "
        f"{phantom}"
    )


def test_rollup_sentinel_is_version_agnostic_shape():
    """AST structural meta-test (slice-028 B-add-1; mirrors slice-014
    test_pmi_1_gate_function_is_version_agnostic_shape).

    Walks the sentinel FunctionDef body AND both set-construction helper
    bodies (_VERSION_AGNOSTIC_SCANNED) for the specific defect class. The
    int-count Compare (`len(...) == 20`) check is scoped to the SENTINEL
    body only (the helpers legitimately use arity ints like
    `len(node.args) >= 2`; slice-014's pin was likewise defect-class
    precise, not "any int"). The `post-slice-NNN` string-anchor check
    applies to all three (no false-positive risk). The B-add-1 "count
    hidden in a helper" risk is closed by the counter-anchor test (set
    construction confined to the two helpers; the assertion cannot move out
    unscanned).
    """
    module = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
    by_name = {
        n.name: n
        for n in ast.walk(module)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    sentinel_name = _VERSION_AGNOSTIC_SCANNED[0]
    offenders: list[str] = []
    for fn_name in _VERSION_AGNOSTIC_SCANNED:
        fn = by_name.get(fn_name)
        assert fn is not None, (
            f"version-agnostic-shape meta-test: scanned function {fn_name!r} "
            f"not found — _VERSION_AGNOSTIC_SCANNED is stale (B-add-1 "
            f"counter-anchor would also fail)."
        )
        for sub in ast.walk(fn):
            if fn_name == sentinel_name and isinstance(sub, ast.Compare):
                for cmp in sub.comparators:
                    if (
                        isinstance(cmp, ast.Constant)
                        and isinstance(cmp.value, int)
                        and not isinstance(cmp.value, bool)
                    ):
                        offenders.append(
                            f"{fn_name}:L{sub.lineno} int-count Compare "
                            f"comparator {cmp.value!r} (the `== N` count-literal "
                            f"class slice-028 retired)"
                        )
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                if _POST_SLICE_ANCHOR_RE.search(sub.value):
                    offenders.append(
                        f"{fn_name}:L{sub.lineno} post-slice-NNN version anchor "
                        f"in string {sub.value!r}"
                    )
    assert offenders == [], (
        "version-agnostic UTF-8 rollup sentinel shape violated — a "
        "count-literal / version-anchor regression was smuggled back into "
        "the sentinel or a scanned helper:\n  " + "\n  ".join(offenders)
    )


def test_rollup_sentinel_helpers_exist_and_are_scanned():
    """Counter-anchor meta-test (slice-028 B-add-1; mirrors slice-014
    test_no_per_version_pmi_1_gate_functions_remain).

    Pins that set-construction primitives are CONFINED to the two scanned
    helpers — defeats the "move the discovered/covered logic into a third,
    unscanned function" regression that would make
    test_rollup_sentinel_is_version_agnostic_shape pass trivially
    (fail-OPEN). Primitives: a `.glob(` call (discovered-set) or an
    `ast.parse(` call (covered-set / discovered-set AST read).
    """
    module = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
    funcs = [
        n for n in ast.walk(module)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    names = {f.name for f in funcs}
    for required in _VERSION_AGNOSTIC_SCANNED:
        assert required in names, (
            f"counter-anchor: required scanned function {required!r} missing "
            f"— the version-agnostic sentinel was dismantled or renamed."
        )

    # Set-CONSTRUCTION primitives (filesystem discovery + AST token harvest)
    # must live only in the two helpers. The three version-agnostic-shape
    # guard tests legitimately `ast.parse` THIS module for introspection —
    # they do not build the discovered/covered sets the sentinel consumes,
    # so they are allow-listed. The genuine B-add-1 leak is set-construction
    # logic in some OTHER function the sentinel would call.
    allowed = {"_discovered_audit_tools", "_covered_tool_tokens"} | set(
        _VERSION_AGNOSTIC_SCANNED
    ) | {
        "test_rollup_sentinel_is_version_agnostic_shape",
        "test_rollup_sentinel_helpers_exist_and_are_scanned",
        "test_rollup_sentinel_fails_with_tool_naming_message_on_parity_break",
    }
    leaks: list[str] = []
    for fn in funcs:
        if fn.name in allowed:
            continue
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                attr = sub.func.attr
                root = sub.func.value
                if attr == "glob":
                    leaks.append(f"{fn.name}:L{sub.lineno} .glob( call")
                if attr == "parse" and isinstance(root, ast.Name) and root.id == "ast":
                    leaks.append(f"{fn.name}:L{sub.lineno} ast.parse( call")
    assert leaks == [], (
        "counter-anchor: set-construction primitive(s) found OUTSIDE the two "
        "scanned helpers (_discovered_audit_tools / _covered_tool_tokens) — "
        "B-add-1 regression: discovered/covered logic moved to an unscanned "
        "function, so the version-agnostic-shape meta-test would pass "
        "trivially (fail-OPEN):\n  " + "\n  ".join(leaks)
    )


def test_rollup_sentinel_fails_with_tool_naming_message_on_parity_break(monkeypatch):
    """Failure-path regression test (slice-028 B-add-1; slice-014-faithful —
    monkeypatch the helpers, the parity assertion stays in-body and is
    genuinely exercised; NO logic extraction).

    Proves the sentinel FIRES with a tool-naming message in BOTH directions
    when parity is broken. Without this, a future regression that makes the
    parity assertion vacuous would ship silently.
    """
    mod = sys.modules[__name__]

    # Direction 1: an uncovered tool (discovered, not covered).
    monkeypatch.setattr(
        mod, "_discovered_audit_tools",
        lambda: frozenset({"tools.real_one", "tools.fake_uncovered"}),
    )
    monkeypatch.setattr(
        mod, "_covered_tool_tokens",
        lambda: frozenset({"tools.real_one"}),
    )
    with pytest.raises(AssertionError, match=r"fake_uncovered"):
        test_every_audit_tool_survives_cp1252_stdout_with_u2192_input()

    # Direction 2: a phantom coverage token (covered, not discovered).
    monkeypatch.setattr(
        mod, "_discovered_audit_tools",
        lambda: frozenset({"tools.real_one"}),
    )
    monkeypatch.setattr(
        mod, "_covered_tool_tokens",
        lambda: frozenset({"tools.real_one", "tools.fake_phantom"}),
    )
    with pytest.raises(AssertionError, match=r"fake_phantom"):
        test_every_audit_tool_survives_cp1252_stdout_with_u2192_input()
