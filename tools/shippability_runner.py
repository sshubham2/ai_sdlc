"""SRSC-1 — the canonical /validate-slice Step-5.5 shippability-catalog runner.

Per SRSC-1 (methodology-changelog.md v0.51.0; slice-038; [[ADR-039]]).

R-8: the Step-5.5 catalog-execution loop was hand-rolled per slice from
`skills/validate-slice/SKILL.md` prose. A naive runner that strips only the
OUTER markdown fence of a whole `Machine-cmd` cell mangles segment 2 of the
lone multi-segment row (#28) into `argv[0] = `<interp>...` -> WinError 2 -- a
false-FAIL that recurred N=2 (slice-032, slice-033) DESPITE the SKILL.md
prose already saying "deterministically ;-split + interpreter-anchored".
Prose binds nothing executable.

This module is the single canonical executor: `/validate-slice` Step 5.5
INVOKES it instead of describing a loop. It does NOT re-derive the split /
strip -- it REUSES `tools.shippability_decoupling_audit._segments()` (the
SCMD-1 canonical per-`;`-segment backtick+whitespace strip) plus that audit's
catalog row / Machine-cmd-cell parsing. The shared artifact is the same
CSP-1 cross-`tools` private-reuse pattern `shippability_decoupling_audit`
itself uses to consume `shippability_path_audit`.

Pre-condition (documented, NOT re-validated here -- duplicating SCMD-1's
grammar check would be the CSP-1 divergence this slice exists to avoid):
Step 5.5 runs the SCMD-1 pre-catalog gate (item 3a) as a hard STOP BEFORE
this runner. The runner trusts that gate for cell well-formedness and
focuses solely on correct per-segment execution.

Usage:
    python -m tools.shippability_runner architecture/shippability.md
    python -m tools.shippability_runner architecture/shippability.md --json

Exit codes:
    0  every data row PASSED (or empty / zero-row catalog)
    1  >=1 data row FAILED (a regression -- blocks /reflect)
    2  usage error (catalog missing/unreadable)
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout
from tools.shippability_decoupling_audit import (  # canonical, NOT re-derived
    _catalog_rows,
    _machine_cmd_cell,
    _segments,
)
from tools.shippability_path_audit import _find_repo_root

# Tokens that introduce the canonical interpreter placeholder. SCMD-1 permits
# `<interp>` (the SKILL.md-prose convention), a bare `python`, or an absolute
# `.../python.exe`. The runner normalizes ALL three to the live interpreter so
# the catalog never embeds a machine-specific path (SCMD-1 / ADR-031).
_INTERP_TOKENS = frozenset({"<interp>", "python", "python.exe", "python3"})


def _normalize_interp(tokens: list[str]) -> list[str]:
    """Replace the leading interpreter token with the live interpreter.

    `<interp> -m pytest ...` / `python -m pytest ...` /
    `C:/.../python.exe -m pytest ...` all become
    `<sys.executable> -m pytest ...`. Anything else is left as-is (SCMD-1's
    pre-catalog gate has already proven each segment is an interpreter-anchored
    pytest invocation, so token[0] is always an interpreter form here)."""
    if not tokens:
        return tokens
    head = tokens[0]
    is_interp = (
        head in _INTERP_TOKENS
        or head.endswith("python")
        or head.endswith("python.exe")
        or head.endswith("python3")
    )
    if is_interp:
        return [sys.executable, *tokens[1:]]
    return tokens


@dataclass(frozen=True)
class RowResult:
    row: str
    status: str          # "PASS" | "FAIL"
    line: int
    detail: str = ""

    def to_dict(self) -> dict:
        return {"row": self.row, "status": self.status,
                "line": self.line, "detail": self.detail}


@dataclass
class RunResult:
    rows_run: int = 0
    passed: int = 0
    failed: int = 0
    rows: list[RowResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rows_run": self.rows_run,
            "passed": self.passed,
            "failed": self.failed,
            "rows": [r.to_dict() for r in self.rows],
            "summary": {"failed_count": self.failed},
        }


def run_catalog(catalog_path: Path, repo_root: Path | None = None) -> RunResult:
    """Execute every catalog data row's Machine-cmd cell, per-segment.

    Each row's cell is split via the CANONICAL `_segments()` (split on `;`,
    then strip backticks + ws PER segment -- the R-8 fix). Every segment of a
    row must exit 0 for the row to PASS; the first failing segment fails the
    row but the run continues so the full regression picture is reported."""
    result = RunResult()
    text = catalog_path.read_text(encoding="utf-8")
    if repo_root is None:
        repo_root = _find_repo_root(catalog_path)

    for line, cells in _catalog_rows(text):
        row = cells[0]
        result.rows_run += 1
        cell = _machine_cmd_cell(cells)
        if not cell:
            # SCMD-1 pre-catalog gate (Step 5.5 item 3a) should have STOPped
            # before us; defensively record rather than crash.
            result.failed += 1
            result.rows.append(RowResult(
                row, "FAIL", line,
                "no Machine-cmd cell (SCMD-1 pre-catalog gate should have "
                "caught this -- did Step 5.5 item 3a run?)"))
            continue

        row_ok = True
        fail_detail = ""
        for seg in _segments(cell):  # CANONICAL per-;-segment strip (R-8 fix)
            argv = _normalize_interp(shlex.split(seg, posix=True))
            if not argv:
                continue
            proc = subprocess.run(
                argv, cwd=str(repo_root),
                capture_output=True, text=True,
            )
            if proc.returncode != 0:
                row_ok = False
                tail = (proc.stdout or "")[-500:] + (proc.stderr or "")[-500:]
                fail_detail = (f"segment exited {proc.returncode}: {seg!r}\n"
                               f"{tail.strip()}")
                break  # row already failed; no need to run later segments

        if row_ok:
            result.passed += 1
            result.rows.append(RowResult(row, "PASS", line))
        else:
            result.failed += 1
            result.rows.append(RowResult(row, "FAIL", line, fail_detail))

    return result


def _format_human(r: RunResult) -> str:
    head = (f"Shippability catalog run: {r.rows_run} row(s), "
            f"{r.passed} PASS, {r.failed} FAIL\n")
    if not r.failed:
        return head
    out = [head, "\nFAILED:\n"]
    for row in r.rows:
        if row.status == "FAIL":
            out.append(f"  #{row.row} (shippability.md:{row.line})\n"
                       f"    {row.detail}\n\n")
    out.append("Cannot proceed to /reflect. Fix the regression, OR get user "
               "approval to defer the fix to a new slice.\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="shippability_runner",
        description="SRSC-1 canonical Step-5.5 shippability-catalog runner "
                    "(per-;-segment backtick-strip; reuses SCMD-1 _segments())",
    )
    parser.add_argument("catalog", type=Path,
                        help="Path to architecture/shippability.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    catalog_path: Path = args.catalog
    if not catalog_path.is_file():
        sys.stderr.write(f"usage error: catalog not found: {catalog_path}\n")
        return 2

    result = run_catalog(catalog_path)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_format_human(result), end="")
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
