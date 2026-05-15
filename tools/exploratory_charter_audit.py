"""Exploratory-charter audit (ETC-1).

Parses a slice's `mission-brief.md` and validates:
  - The opt-in field `**Exploratory-charter**: true | false` is recognized
  - When true, a `## Exploratory test charter` section must exist with
    a 5-column table: # | Mission | Timebox | Status | Findings
  - The table has at least one charter row
  - Mission cell non-empty
  - Status is one of {PENDING, IN-PROGRESS, COMPLETED, DEFERRED}
  - Findings cell non-empty when status is COMPLETED or DEFERRED
    (the whole point of the charter is to capture what surfaced; bare
    "done" without findings defeats the discipline)
  - With --strict-pre-finish, PENDING and IN-PROGRESS rows are
    violations; COMPLETED and DEFERRED are both accepted (DEFERRED is
    the escape hatch for charters that turned out low-value, with
    rationale captured in Findings)

Per ETC-1 (methodology-changelog.md v0.16.0). Charter-based exploratory
testing (Bach / Kaner / Hendrickson): each charter is a timeboxed
mission ("Explore X using Y to find Z"); the tester runs the session
freely within the timebox and captures findings. Distinct from
scripted testing — surfaces what's NOT in the AC, unstated assumptions,
edge cases the design didn't predict.

Default-off semantics: a brief without `**Exploratory-charter**:` (or
with false) is unaffected. ETC-1 is opt-in per slice.

NFR-1 carry-over: slices whose mission-brief.md mtime predates
`_ETC_1_RELEASE_DATE` are exempt automatically.

Usage:
    python -m tools.exploratory_charter_audit <slice-folder>
    python -m tools.exploratory_charter_audit <mission-brief.md>
    python -m tools.exploratory_charter_audit <slice-folder> --strict-pre-finish
    python -m tools.exploratory_charter_audit <slice-folder> --json
    python -m tools.exploratory_charter_audit <slice-folder> --no-carry-over

Exit codes:
    0  clean (or default-off / carry-over exempt)
    1  violations
    2  usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from tools import _stdout

# Date this rule shipped. NFR-1 carry-over.
_ETC_1_RELEASE_DATE: date = date(2026, 5, 6)

# Field-line: `**Exploratory-charter**: true`
_ETC_FIELD_RE = re.compile(
    r"^\*\*Exploratory[-\s]?charter\*\*\s*:\s*(true|false)\s*$",
    re.IGNORECASE,
)

# Section heading: `## Exploratory test charter`
_CHARTER_HEADING_RE = re.compile(
    r"^##\s+Exploratory\s+test\s+charter\s*$",
    re.IGNORECASE,
)

_OTHER_H2_RE = re.compile(r"^##\s+\S")

# Allowed statuses
_ALLOWED_STATUSES: frozenset[str] = frozenset({
    "PENDING", "IN-PROGRESS", "COMPLETED", "DEFERRED",
})

# Statuses that REQUIRE non-empty Findings (the whole point of the discipline)
_FINDINGS_REQUIRED: frozenset[str] = frozenset({"COMPLETED", "DEFERRED"})

# Statuses accepted at strict-pre-finish (charter is "done" — either by
# completion or deliberate deferral)
_STRICT_ACCEPTED: frozenset[str] = frozenset({"COMPLETED", "DEFERRED"})

_REQUIRED_COLUMNS = 5

_EMPTY_SENTINELS = frozenset({"", "—", "-", "n/a", "none", "(none)"})


@dataclass(frozen=True)
class CharterRow:
    index: str
    mission: str
    timebox: str
    status: str
    findings: str
    line: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ETCViolation:
    path: str
    line: int
    charter_index: str  # "" for section-level errors
    kind: str           # "missing-section" | "empty-table" | "missing-mission" |
                        # "missing-findings" | "invalid-status" | "format" |
                        # "missing-cells" | "non-final-pre-finish"
    severity: str       # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    exploratory_charter_enabled: bool = False
    rows: list[CharterRow] = field(default_factory=list)
    violations: list[ETCViolation] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "exploratory_charter_enabled": self.exploratory_charter_enabled,
            "rows": [r.to_dict() for r in self.rows],
            "violations": [v.to_dict() for v in self.violations],
            "carry_over_exempt": self.carry_over_exempt,
            "summary": {
                "row_count": len(self.rows),
                "by_status": {
                    s: sum(1 for r in self.rows if r.status == s)
                    for s in _ALLOWED_STATUSES
                },
                "violation_count": len(self.violations),
            },
        }


def _slice_is_carry_over(slice_folder: Path) -> bool:
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _ETC_1_RELEASE_DATE


def _detect_etc_flag(text: str) -> bool:
    for line in text.splitlines():
        m = _ETC_FIELD_RE.match(line)
        if m:
            return m.group(1).strip().lower() == "true"
    return False


def _find_charter_table_lines(text: str) -> tuple[int, list[str]] | None:
    lines = text.splitlines()
    heading_idx: int | None = None
    for i, line in enumerate(lines):
        if _CHARTER_HEADING_RE.match(line):
            heading_idx = i
            break
    if heading_idx is None:
        return None

    table_start: int | None = None
    for j in range(heading_idx + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("|"):
            table_start = j
            break
        if _OTHER_H2_RE.match(lines[j]):
            return None

    if table_start is None:
        return None

    table_lines: list[str] = []
    for j in range(table_start, len(lines)):
        if lines[j].strip().startswith("|"):
            table_lines.append(lines[j])
        else:
            break
    return (table_start, table_lines)


def _parse_table_cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _parse_table_cells(line)
    if not cells:
        return False
    for cell in cells:
        stripped = cell.replace(" ", "")
        if not stripped:
            return False
        if not set(stripped) <= set("-:"):
            return False
        if "-" not in stripped:
            return False
    return True


def _cell_is_empty(cell: str) -> bool:
    return cell.strip().lower() in _EMPTY_SENTINELS


def audit_brief_file(
    brief_path: Path,
    strict_pre_finish: bool = False,
    skip_if_carry_over: bool = True,
) -> AuditResult:
    """Audit a mission-brief.md against ETC-1."""
    result = AuditResult()

    if not brief_path.exists():
        return result

    if skip_if_carry_over:
        slice_folder = brief_path.parent
        if _slice_is_carry_over(slice_folder):
            result.carry_over_exempt = True
            return result

    text = brief_path.read_text(encoding="utf-8")
    enabled = _detect_etc_flag(text)
    result.exploratory_charter_enabled = enabled

    if not enabled:
        return result

    found = _find_charter_table_lines(text)
    if found is None:
        result.violations.append(ETCViolation(
            path=str(brief_path), line=0, charter_index="",
            kind="missing-section", severity="Important",
            message=(
                "`**Exploratory-charter**: true` is set but no "
                "`## Exploratory test charter` section with a table was "
                "found. Per ETC-1, when the field is true the brief must "
                "include a 5-column table: # | Mission | Timebox | Status "
                "| Findings."
            ),
        ))
        return result

    table_start, table_lines = found

    if len(table_lines) < 2:
        result.violations.append(ETCViolation(
            path=str(brief_path), line=table_start + 1, charter_index="",
            kind="format", severity="Important",
            message=(
                "charter table is malformed: needs header + separator at "
                "minimum (# | Mission | Timebox | Status | Findings)."
            ),
        ))
        return result

    if not _is_separator_row(table_lines[1]):
        result.violations.append(ETCViolation(
            path=str(brief_path), line=table_start + 2, charter_index="",
            kind="format", severity="Important",
            message=(
                "charter table second line must be the markdown separator "
                "(`|---|---|---|---|---|`)."
            ),
        ))
        return result

    header_cells = _parse_table_cells(table_lines[0])
    if len(header_cells) < _REQUIRED_COLUMNS:
        result.violations.append(ETCViolation(
            path=str(brief_path), line=table_start + 1, charter_index="",
            kind="format", severity="Important",
            message=(
                f"charter table needs {_REQUIRED_COLUMNS} columns (# | "
                f"Mission | Timebox | Status | Findings); found "
                f"{len(header_cells)}: {header_cells}"
            ),
        ))
        return result

    data_rows = table_lines[2:]
    if not data_rows:
        result.violations.append(ETCViolation(
            path=str(brief_path), line=table_start + 1, charter_index="",
            kind="empty-table", severity="Important",
            message=(
                "charter table has no data rows. A walking-skeleton with "
                "zero charters is opt-in-without-discipline. Per ETC-1, "
                "list at least one charter or set Exploratory-charter to "
                "false."
            ),
        ))
        return result

    for idx, raw in enumerate(data_rows, start=1):
        line_num = table_start + 2 + idx
        cells = _parse_table_cells(raw)
        if len(cells) < _REQUIRED_COLUMNS:
            result.violations.append(ETCViolation(
                path=str(brief_path), line=line_num, charter_index="",
                kind="missing-cells", severity="Important",
                message=(
                    f"row {idx}: {len(cells)} cells; expected {_REQUIRED_COLUMNS}"
                ),
            ))
            continue

        index_cell, mission, timebox, status_raw, findings = (
            c.strip() for c in cells[:_REQUIRED_COLUMNS]
        )
        if _cell_is_empty(index_cell) and _cell_is_empty(mission):
            continue

        if _cell_is_empty(mission):
            result.violations.append(ETCViolation(
                path=str(brief_path), line=line_num, charter_index=index_cell,
                kind="missing-mission", severity="Important",
                message=(
                    f"row {idx}: Mission cell is empty. Per ETC-1, every "
                    f"charter must declare what to explore (e.g., "
                    f"'Explore HEIC upload edge cases using corrupted "
                    f"files to find error-handling gaps')."
                ),
            ))
            continue

        status = status_raw.upper().strip()
        if status not in _ALLOWED_STATUSES:
            result.violations.append(ETCViolation(
                path=str(brief_path), line=line_num, charter_index=index_cell,
                kind="invalid-status", severity="Important",
                message=(
                    f"row {idx}: status '{status_raw}' not in "
                    f"{sorted(_ALLOWED_STATUSES)}."
                ),
            ))
            continue

        if status in _FINDINGS_REQUIRED and _cell_is_empty(findings):
            result.violations.append(ETCViolation(
                path=str(brief_path), line=line_num, charter_index=index_cell,
                kind="missing-findings", severity="Important",
                message=(
                    f"row {idx}: status '{status}' requires non-empty "
                    f"Findings. Per ETC-1, a COMPLETED charter without "
                    f"captured findings defeats the discipline; a "
                    f"DEFERRED charter without rationale is hand-waved."
                ),
            ))
            continue

        result.rows.append(CharterRow(
            index=index_cell, mission=mission, timebox=timebox,
            status=status, findings=findings, line=line_num,
        ))

    if strict_pre_finish:
        for row in result.rows:
            if row.status not in _STRICT_ACCEPTED:
                result.violations.append(ETCViolation(
                    path=str(brief_path), line=row.line,
                    charter_index=row.index,
                    kind="non-final-pre-finish", severity="Important",
                    message=(
                        f"row for charter '{row.mission[:60]}' status is "
                        f"{row.status}; --strict-pre-finish requires "
                        f"COMPLETED or DEFERRED. Either run the charter "
                        f"and record findings, or deliberately defer "
                        f"with rationale."
                    ),
                ))

    return result


def _format_human(result: AuditResult) -> str:
    if result.carry_over_exempt:
        return (
            "Exploratory-charter audit: slice is carry-over exempt "
            "(mission-brief.md predates ETC-1 release).\n"
        )
    if not result.exploratory_charter_enabled:
        return (
            "Exploratory-charter audit: not enabled "
            "(`**Exploratory-charter**: true` absent).\n"
        )

    if not result.violations:
        by_status = {
            s: sum(1 for r in result.rows if r.status == s)
            for s in _ALLOWED_STATUSES
        }
        return (
            f"Exploratory-charter audit: clean. {len(result.rows)} "
            f"charter(s) — COMPLETED={by_status['COMPLETED']}, "
            f"IN-PROGRESS={by_status['IN-PROGRESS']}, "
            f"DEFERRED={by_status['DEFERRED']}, "
            f"PENDING={by_status['PENDING']}.\n"
        )

    out: list[str] = [
        f"{len(result.violations)} exploratory-charter violation(s):\n\n"
    ]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) "
            f"{f'charter #{v.charter_index}' if v.charter_index else ''}\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="exploratory_charter_audit",
        description="ETC-1 charter-based exploratory testing audit",
    )
    parser.add_argument(
        "target", type=Path,
        help="Slice folder (auto-finds mission-brief.md inside) OR a mission-brief.md file",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--strict-pre-finish", action="store_true",
        help=(
            "Refuse PENDING / IN-PROGRESS rows (use at /validate-slice "
            "Step 5d); COMPLETED and DEFERRED are both accepted"
        ),
    )
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help="Disable mtime-based carry-over exemption",
    )
    args = parser.parse_args(argv)

    target: Path = args.target
    brief_path = target / "mission-brief.md" if target.is_dir() else target

    result = audit_brief_file(
        brief_path,
        strict_pre_finish=args.strict_pre_finish,
        skip_if_carry_over=not args.no_carry_over,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
