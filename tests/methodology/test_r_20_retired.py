"""Audit-runtime test pinning R-20's `retired` status against silent un-retirement.

Per slice-074 design.md AC#4: R-20 status flipped `mitigating` -> `retired` in
`architecture/risk-register.md`. The audit's `--filter-status retired` output is the
verification surface — invokes `tools.risk_register_audit` as a subprocess, parses
JSON output, asserts `R-20` is in the retired risks list.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tools._vault_paths import VAULT_ROOT

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_r_20_status_is_retired_in_risk_register():
    """AC#4: risk-register R-20 entry has status: retired (was mitigating pre-slice-074)."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.risk_register_audit",
            str(REPO_ROOT / VAULT_ROOT / "risk-register.md"),
            "--json",
            "--filter-status",
            "retired",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    # Fix F (slice-074 m5): explicit returncode + stderr assertion instead of `check=True`.
    # `check=True` raises a bare CalledProcessError whose message omits the audit's stderr,
    # making CI failures opaque. Surface stderr in the assertion message instead.
    assert proc.returncode == 0, (
        f"risk_register_audit failed (exit {proc.returncode}): stderr={proc.stderr!r}"
    )
    data = json.loads(proc.stdout)
    risk_ids = [r["risk_id"] for r in data.get("risks", [])]
    assert "R-20" in risk_ids, f"R-20 not in retired risks; got {sorted(risk_ids)}"


def test_audit_failure_surfaces_stderr():
    """Fix F (slice-074 m5): on audit failure the explicit `capture_output=True` pattern
    surfaces stderr — unlike `check=True`, which raises a bare CalledProcessError that
    swallows it. Exercised with an invalid `--filter-status` choice (argparse exits 2).
    """
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.risk_register_audit",
            str(REPO_ROOT / VAULT_ROOT / "risk-register.md"),
            "--filter-status",
            "bogus-not-a-status",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert proc.returncode != 0, "expected nonzero exit for invalid --filter-status choice"
    assert proc.stderr, (
        "Fix F regression: audit failure produced no captured stderr — the explicit "
        "capture_output=True pattern must surface stderr (check=True would swallow it)"
    )
    assert "invalid choice" in proc.stderr, (
        f"expected argparse 'invalid choice' diagnostic in stderr, got {proc.stderr!r}"
    )
