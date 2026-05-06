"""Wiring matrix audit (WIRE-1).

Parses the wiring matrix from a slice's design.md and validates that every
new module declared in the slice has either:
  (a) a consumer entry point AND a consumer test, OR
  (b) an explicit exemption with rationale

Per WIRE-1 (methodology-changelog.md v0.9.0). The rule's purpose: prevent
dead-modules-with-green-tests by requiring consumer-side demand for every
producer (Freeman & Pryce, GOOS — "the consumer demand precedes the producer").

NFR-1 carry-over: slices whose mission-brief.md mtime predates the rule's
release date (_WIRE_1_RELEASE_DATE) are exempt automatically — the rule
applies to slices authored on or after the rule release.

v1 enforces format validation only:
  - Wiring matrix heading present
  - Markdown table well-formed (header + separator + 0+ data rows)
  - Each data row has 4 cells (New module | Consumer entry point |
    Consumer test | Exemption)
  - For each row: either (entry point + consumer test) OR (exemption with
    'rationale:' substring)

A v2 will add existence/import audits — verify entry-point files exist,
grep for module imports inside them. Those checks need real project context
that doesn't fixture cleanly.

Usage:
    python -m tools.wiring_matrix_audit <slice-folder>
    python -m tools.wiring_matrix_audit <design.md>
    python -m tools.wiring_matrix_audit --json <slice-folder>
    python -m tools.wiring_matrix_audit --no-carry-over <slice-folder>

Exit codes:
    0  clean (or carry-over exempt)
    1  format violations
    2  usage error / unrecoverable failure
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

# Date this rule shipped. Slices with mission-brief.md mtime BEFORE this date
# are carry-over exempt automatically. NFR-1 pattern from GVM.
_WIRE_1_RELEASE_DATE: date = date(2026, 5, 6)

# Wiring matrix heading in design.md (must match exactly, including capitalization)
_MATRIX_HEADING = "## Wiring matrix"

# Sentinel cell values treated as empty (markdown convention for "n/a")
_EMPTY_SENTINELS = frozenset({"", "—", "-", "n/a", "none", "(none)"})

# Required column count for the matrix
_REQUIRED_COLUMNS = 4

# Substring required in an exemption cell to qualify as a real exemption
_RATIONALE_MARKER = "rationale:"


@dataclass(frozen=True)
class WireViolation:
    """A finding emitted by the audit."""
    path: str        # design.md path
    line: int        # 1-based line number; 0 if file-level
    row_index: int   # 1-based data-row index; 0 if not row-specific
    kind: str        # "no-matrix" | "format" | "missing-cells" | "missing-rationale"
    severity: str    # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def _slice_is_carry_over(slice_folder: Path) -> bool:
    """True if the slice was authored before WIRE-1 (mtime carry-over)."""
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _WIRE_1_RELEASE_DATE


def _find_matrix_lines(design_text: str) -> tuple[int, list[str]] | None:
    """Find the wiring matrix table after the heading.

    Returns (table_start_line_index, list_of_table_lines), or None if no matrix.
    Indices are 0-based against the source lines.
    """
    lines = design_text.splitlines()
    heading_idx: int | None = None
    for i, line in enumerate(lines):
        if line.strip() == _MATRIX_HEADING:
            heading_idx = i
            break
    if heading_idx is None:
        return None

    # Walk forward looking for the first table line (starts with `|`).
    # Stop early if we hit another section heading.
    table_start: int | None = None
    for j in range(heading_idx + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("|"):
            table_start = j
            break
        if stripped.startswith("## ") or stripped.startswith("# "):
            return None  # next heading without finding table

    if table_start is None:
        return None

    # Collect contiguous table lines
    table_lines: list[str] = []
    for j in range(table_start, len(lines)):
        if lines[j].strip().startswith("|"):
            table_lines.append(lines[j])
        else:
            break

    return (table_start, table_lines)


def _parse_table_cells(line: str) -> list[str]:
    """Split a markdown table row into stripped cell texts."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def _is_separator_row(line: str) -> bool:
    """Is this line a markdown table separator (---, :---, etc.)?"""
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
    """Is this cell empty (per markdown 'n/a' conventions)?"""
    return cell.strip().lower() in _EMPTY_SENTINELS


def _exemption_has_rationale(cell: str) -> bool:
    """Does this exemption cell contain the required 'rationale:' marker?"""
    return _RATIONALE_MARKER in cell.lower()


def audit_design_file(
    design_path: Path,
    skip_if_carry_over: bool = True,
) -> list[WireViolation]:
    """Audit a single design.md against WIRE-1 format rules."""
    if not design_path.exists():
        return [WireViolation(
            path=str(design_path), line=0, row_index=0,
            kind="no-matrix", severity="Important",
            message=f"design.md not found: {design_path}",
        )]

    if skip_if_carry_over:
        slice_folder = design_path.parent
        if _slice_is_carry_over(slice_folder):
            return []  # carry-over exempt — rule didn't exist when slice was authored

    text = design_path.read_text(encoding="utf-8")
    found = _find_matrix_lines(text)
    if found is None:
        return [WireViolation(
            path=str(design_path), line=0, row_index=0,
            kind="no-matrix", severity="Important",
            message=(
                f"no `{_MATRIX_HEADING}` heading found in design.md (or no "
                f"table follows it). Per WIRE-1, every slice's design.md "
                f"must include a wiring matrix."
            ),
        )]

    table_start, table_lines = found

    # Need at least header + separator
    if len(table_lines) < 2:
        return [WireViolation(
            path=str(design_path), line=table_start + 1, row_index=0,
            kind="format", severity="Important",
            message=(
                "wiring matrix is malformed: fewer than 2 lines (need header "
                "+ separator at minimum)"
            ),
        )]

    # Validate separator
    if not _is_separator_row(table_lines[1]):
        return [WireViolation(
            path=str(design_path), line=table_start + 2, row_index=0,
            kind="format", severity="Important",
            message=(
                "wiring matrix second line must be the markdown separator "
                "(`|---|---|---|---|`)"
            ),
        )]

    # Validate header column count
    header_cells = _parse_table_cells(table_lines[0])
    if len(header_cells) < _REQUIRED_COLUMNS:
        return [WireViolation(
            path=str(design_path), line=table_start + 1, row_index=0,
            kind="format", severity="Important",
            message=(
                f"wiring matrix needs {_REQUIRED_COLUMNS} columns "
                f"(New module | Consumer entry point | Consumer test | Exemption); "
                f"found {len(header_cells)}: {header_cells}"
            ),
        )]

    # Validate each data row
    violations: list[WireViolation] = []
    for idx, raw in enumerate(table_lines[2:], start=1):
        line_num = table_start + 2 + idx  # 1-based line number in source
        cells = _parse_table_cells(raw)

        if len(cells) < _REQUIRED_COLUMNS:
            violations.append(WireViolation(
                path=str(design_path), line=line_num, row_index=idx,
                kind="format", severity="Important",
                message=f"row {idx} has {len(cells)} cells; expected {_REQUIRED_COLUMNS}",
            ))
            continue

        new_module, entry_point, consumer_test, exemption = cells[:_REQUIRED_COLUMNS]

        if _cell_is_empty(new_module):
            violations.append(WireViolation(
                path=str(design_path), line=line_num, row_index=idx,
                kind="missing-cells", severity="Important",
                message=f"row {idx}: 'New module' cell is empty",
            ))
            continue

        has_consumer = (
            not _cell_is_empty(entry_point)
            and not _cell_is_empty(consumer_test)
        )
        has_exemption = not _cell_is_empty(exemption)

        if not has_consumer and not has_exemption:
            violations.append(WireViolation(
                path=str(design_path), line=line_num, row_index=idx,
                kind="missing-cells", severity="Important",
                message=(
                    f"row {idx} ('{new_module}'): missing consumer entry point "
                    f"or consumer test. Either both must be filled, or carry "
                    f"an exemption with rationale (e.g., 'internal helper, no "
                    f"consumer demanded — rationale: ...')."
                ),
            ))
            continue

        if has_exemption and not _exemption_has_rationale(exemption):
            violations.append(WireViolation(
                path=str(design_path), line=line_num, row_index=idx,
                kind="missing-rationale", severity="Important",
                message=(
                    f"row {idx} ('{new_module}'): exemption present but "
                    f"missing 'rationale:' substring. Per WIRE-1, exemptions "
                    f"must include explicit rationale."
                ),
            ))

    return violations


def _format_human(violations: list[WireViolation]) -> str:
    if not violations:
        return "No wiring matrix violations.\n"
    lines: list[str] = [f"{len(violations)} wiring matrix findings:\n\n"]
    for v in violations:
        lines.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) row {v.row_index}\n"
            f"    {v.message}\n\n"
        )
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="wiring_matrix_audit",
        description="WIRE-1 wiring matrix audit — format validation v1",
    )
    parser.add_argument(
        "target", type=Path,
        help=(
            "Path to a slice folder (auto-finds design.md inside) OR a "
            "design.md file directly"
        ),
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output findings as JSON (machine-readable)",
    )
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help=(
            "Disable mtime-based carry-over exemption (audit even old slices)"
        ),
    )
    args = parser.parse_args(argv)

    target: Path = args.target
    design_path = target / "design.md" if target.is_dir() else target

    violations = audit_design_file(
        design_path,
        skip_if_carry_over=not args.no_carry_over,
    )

    if args.json:
        sys.stdout.write(json.dumps({
            "violations": [v.to_dict() for v in violations],
            "summary": {"total": len(violations)},
        }, indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(violations))

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
