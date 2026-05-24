"""Pin R-17 status retired post-slice-066.

Per slice-066 /critique AC #5: R-17 (mitigating → retired) — `tools/branch_workflow_audit.py`
gains the missing pre-create-cleanliness backstop via worktree-isolation; the candidate fix (b)
named verbatim at `risk-register.md:295`. Retirement citation: slice-066-add-worktree-per-slice-discipline
(2026-05-24; ADR-063 / BRANCH-2 / methodology v0.68.0).

Rule reference: R-17 retired by BRANCH-2 (slice-066; ADR-063).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RISK_REGISTER_PATH = REPO_ROOT / "architecture" / "risk-register.md"


def test_r17_status_is_retired_post_slice_066() -> None:
    """R-17 risk-register entry must declare `**Status**: retired` + cite slice-066.

    Defect class: pre-slice-066, R-17 was `**Status**: mitigating` — the prose dirty-tree
    check at /build-slice Prerequisite worked but the audit at Step 6 pre-finish didn't
    enforce pre-create cleanliness. Post-slice-066 worktree-per-slice (BRANCH-2 / ADR-063)
    closes the class structurally — uncommitted slice-A WIP cannot reach slice-B's
    worktree filesystem.

    This test pins both the status flip AND the `**Retired**: slice-066-...` citation line.
    """
    assert RISK_REGISTER_PATH.exists(), (
        f"architecture/risk-register.md must exist at {RISK_REGISTER_PATH}"
    )
    content = RISK_REGISTER_PATH.read_text(encoding="utf-8")
    r17_idx = content.find("## R-17")
    assert r17_idx > 0, (
        "R-17 entry must be present in risk-register.md (discovered slice-061; status now retired)"
    )
    # Extract the R-17 block (until next ## R-NN header or EOF).
    next_header_idx = content.find("\n## R-", r17_idx + 5)
    r17_block = content[r17_idx:next_header_idx] if next_header_idx > 0 else content[r17_idx:]
    assert "**Status**: retired" in r17_block, (
        "R-17 status must be `**Status**: retired` post-slice-066 (was `mitigating` pre-slice-066). "
        "Per slice-066 /critique AC #5 + ADR-063 §Decision."
    )
    assert "slice-066" in r17_block, (
        "R-17 retirement paragraph must cite slice-066-add-worktree-per-slice-discipline in the "
        "`**Retired**:` line per slice-066 /critique AC #5"
    )
    assert "ADR-063" in r17_block, (
        "R-17 retirement paragraph must cite ADR-063 (the BRANCH-2 mint that retires R-17)"
    )
    assert "BRANCH-2" in r17_block or "v0.68.0" in r17_block, (
        "R-17 retirement paragraph must cite either BRANCH-2 rule reference or methodology v0.68.0"
    )


def test_r17_absent_from_risk_register_audit_filter_status_open() -> None:
    """`risk_register_audit --filter-status open --json` must NOT list R-17 post-slice-066.

    Defect class: R-9 (slice-036-retired) fixed `--filter-status open` so it actually filters
    by status. Post-slice-036, retired risks are correctly excluded from the open filter.
    R-17's transition `mitigating → retired` must remove it from the open-filter output.

    This is the canonical regression: any future drift that re-opens R-17 OR reverts R-9's
    filter fix would surface here.
    """
    assert RISK_REGISTER_PATH.exists(), f"architecture/risk-register.md must exist at {RISK_REGISTER_PATH}"
    # Use the same interpreter pytest is running under.
    env = os.environ.copy()
    result = subprocess.run(
        [
            sys.executable, "-m", "tools.risk_register_audit",
            str(RISK_REGISTER_PATH),
            "--json", "--filter-status", "open",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(REPO_ROOT),
    )
    # Exit code may be 0 (clean) or 1 (open-band risks present); both emit JSON on stdout.
    # Failure to emit JSON (e.g., exit 2 usage-error) is a separate problem.
    assert result.stdout.strip(), (
        f"tools.risk_register_audit emitted no JSON output; stderr: {result.stderr!r}"
    )
    data = json.loads(result.stdout)
    risk_ids = [r["risk_id"] for r in data.get("risks", [])]
    assert "R-17" not in risk_ids, (
        f"R-17 must NOT appear in `risk_register_audit --filter-status open` output post-slice-066 "
        f"(transitioned mitigating → retired). Got open-filter risk_ids: {risk_ids}. "
        f"Per slice-066 /critique AC #5 + slice-036/R-9 filter-by-status fix."
    )
