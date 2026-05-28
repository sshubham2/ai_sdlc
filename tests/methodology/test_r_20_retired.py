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

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_r_20_status_is_retired_in_risk_register():
    """AC#4: risk-register R-20 entry has status: retired (was mitigating pre-slice-074)."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.risk_register_audit",
            str(REPO_ROOT / "architecture" / "risk-register.md"),
            "--json",
            "--filter-status",
            "retired",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=True,
    )
    data = json.loads(proc.stdout)
    risk_ids = [r["risk_id"] for r in data.get("risks", [])]
    assert "R-20" in risk_ids, f"R-20 not in retired risks; got {sorted(risk_ids)}"
