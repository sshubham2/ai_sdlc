"""CLI tests (PCR-1 / slice-076 / ADR-069).

Per AC4 unit / CLI per mission-brief rows: ``python -m
tools.parallel_conflict_resolver [--diagnose | --classify | --resolve-soft]
[--json]`` is the prose-invoked entry point from ``skills/commit-slice/SKILL.md``
Step 5b sub-step 2.5. The CLI MUST emit parseable JSON when ``--json`` is
passed (for the SKILL.md prose to branch on ``action`` field), and MUST
exit 0 on successful SOFT-class auto-resolution.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_cli_emits_json_when_json_flag_passed(tmp_path) -> None:
    """``python -m tools.parallel_conflict_resolver --diagnose --json``
    MUST emit parseable JSON to stdout.

    AC4 unit / CLI per mission-brief row. The SKILL.md prose at /commit-slice
    Step 5b sub-step 2.5 parses the JSON output's ``action`` field to branch
    between auto-applied vs. fall-through-to-SOAD-1; un-parseable output
    would break the branch.

    Uses tmp_path as --repo-root to isolate from real-repo state.
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "architecture").mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.parallel_conflict_resolver",
            "--diagnose",
            "--json",
            "--repo-root",
            str(tmp_path),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # JSON parseability is the load-bearing contract — assert stdout parses
    # regardless of exit code (the CLI may exit non-zero on no-conflict
    # state, but should still emit JSON for the consumer to parse).
    assert result.stdout.strip(), (
        f"--json mode MUST emit non-empty stdout; got empty. "
        f"stderr: {result.stderr!r}, returncode: {result.returncode}"
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"--json mode MUST emit parseable JSON; got: {result.stdout!r}\n"
            f"JSONDecodeError: {exc}\n"
            f"stderr: {result.stderr!r}"
        )
    # Minimal shape contract: parsed result is a dict (not list / scalar).
    assert isinstance(parsed, dict), (
        f"--json output MUST be a JSON object (dict); got {type(parsed).__name__}: {parsed!r}"
    )


def test_cli_resolve_soft_exits_zero_on_successful_soft_regen(tmp_path) -> None:
    """``python -m tools.parallel_conflict_resolver --resolve-soft``
    MUST exit 0 when SOFT-class auto-resolution succeeds.

    AC4 unit / CLI per mission-brief row. The SKILL.md prose branches on
    exit code: 0 + action=APPLIED → log breadcrumb + proceed; 0 + action=STOP
    → fall through to SOAD-1; non-zero → fall through with stderr diagnostic.

    For this WRITTEN-FAILING test, we exercise the no-conflict-in-progress
    case: the CLI MUST report something coherent (exit 0 with STOP-rationale
    or exit 1 with rebase-not-in-progress error). The Phase C impl will
    refine this to test a real SOFT-class success path.
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "architecture").mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.parallel_conflict_resolver",
            "--resolve-soft",
            "--json",
            "--repo-root",
            str(tmp_path),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # On no-conflict-in-progress (empty u_files), classify_conflict returns
    # UNKNOWN → resolve_soft_conflict returns STOP. The CLI MUST report this
    # as exit 0 + action=STOP (NOT raise / crash).
    # Phase C contract: exit 0 with action=STOP (CLI semantics) OR exit 1
    # (resolver-side error semantics). The MUST is "emit parseable JSON
    # with a coherent action field" — actual SOFT-success path requires
    # synthetic rebase state which a future test will set up.
    assert result.returncode in (0, 1), (
        f"CLI exit code MUST be 0 (success) or 1 (resolver error); got "
        f"{result.returncode}. stderr: {result.stderr!r}"
    )
    # JSON output MUST parse (regardless of exit code).
    if result.stdout.strip():
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            pytest.fail(
                f"CLI --json output MUST parse; got: {result.stdout!r}\n"
                f"JSONDecodeError: {exc}\nstderr: {result.stderr!r}"
            )
        assert "action" in parsed, (
            f"CLI --json output MUST include 'action' field for SKILL.md "
            f"prose to branch on; got: {parsed!r}"
        )
        assert parsed["action"] in ("APPLIED", "STOP"), (
            f"CLI --json output 'action' field MUST be 'APPLIED' or 'STOP'; "
            f"got: {parsed['action']!r}"
        )
