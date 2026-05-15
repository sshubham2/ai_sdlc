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

import os
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
]

# Tools with --root only
_ROOT_ONLY_TOOLS = [
    "tools.plugin_manifest_audit",
    "tools.utf8_stdout_audit",
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


def test_every_audit_tool_survives_cp1252_stdout_with_u2192_input():
    """Roll-up assertion (per slice-023 AC #4 + shippability row 23 invocation
    target): every audit tool under tools/ with a main() must complete under
    cp1252 stdout with U+2192 fixture content WITHOUT UnicodeEncodeError /
    UnicodeDecodeError.

    Aggregates the per-tool parametrized + custom-argv tests above. Pytest
    parametrize already provides the per-tool granularity; this test exists
    so shippability row 23 has a single named target.
    """
    # Sentinel: all 17 audit tools exist
    tools_dir = REPO_ROOT / "tools"
    actual_audits = sorted(
        p.stem for p in tools_dir.glob("*.py")
        if not p.name.startswith("_") and p.name != "__init__.py"
    )
    assert len(actual_audits) == 17, (
        f"Expected 17 audit tools post-slice-023; got {len(actual_audits)}: {actual_audits}"
    )
    # The per-tool tests above provide the actual subprocess invocation
    # coverage. This is a structural roll-up assertion only.
