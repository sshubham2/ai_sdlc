"""Test-first slice audit (TF-1).

Parses a slice's `mission-brief.md` and validates:
  - The opt-in field `**Test-first**: true | false` is recognized
  - When true, a `## Test-first plan` section must exist with a 5-column
    table: AC | Test type | Test path | Test function | Status
  - Every AC referenced in the brief body (numbered 1, 2, 3, ... in the
    Acceptance criteria section) must have at least one test-first row
  - Each row's Status must be one of {PENDING, WRITTEN-FAILING, PASSING}
  - With --strict-pre-finish, any non-PASSING row is a violation
    (used at /build-slice Step 6)
  - With --strict-pre-finish, any PASSING row whose Test path file does
    not exist on disk is a violation (PTFCD-1; kind=missing-test-path-file)

Per TF-1 (methodology-changelog.md v0.13.0). The rule's purpose: opt-in
TDD discipline — when a slice declares test-first, every AC must map to
explicit failing tests written BEFORE implementation, with statuses
tracked through the lifecycle (PENDING -> WRITTEN-FAILING -> PASSING).

Default-off semantics: a brief without `**Test-first**:` (or with
`Test-first: false`) is unaffected. Old briefs continue to work; new
slices opt in by setting the field to true.

NFR-1 carry-over: slices whose mission-brief.md mtime predates the
release date `_TF_1_RELEASE_DATE` are exempt automatically.

Usage:
    python -m tools.test_first_audit <slice-folder>
    python -m tools.test_first_audit <mission-brief.md>
    python -m tools.test_first_audit <slice-folder> --strict-pre-finish
    python -m tools.test_first_audit <slice-folder> --json
    python -m tools.test_first_audit <slice-folder> --no-carry-over

Exit codes:
    0  clean (or test-first=false / carry-over exempt)
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
_TF_1_RELEASE_DATE: date = date(2026, 5, 6)

# Field-line value pattern: `**Test-first**: true` — optionally annotated.
# Per R-7 / TFFL-1 (slice-034; ADR-034): the boolean MUST be a standalone
# token (followed by whitespace, an opening `(` for the idiomatic
# annotation, or end-of-line). NOT `(true|false)\b.*$` — `\b` matches
# between `false` and `-`, so `false-positive`/`true.`/`false; note` would
# be silently accepted as a valid boolean, re-introducing the R-7
# silent-bypass through a malformed *suffix* value. `re.match` semantics:
# the annotation remainder need not be consumed.
_TEST_FIRST_FIELD_RE = re.compile(
    r"^\*\*Test[-\s]?first\*\*\s*:\s*(true|false)(?=[\s(]|$)",
    re.IGNORECASE,
)

# Value-agnostic "is the field syntactically present?" matcher (per R-7 /
# TFFL-1 ADR-034 §2). Used ONLY to distinguish "field absent" (legitimate
# default-off) from "field present but value unparseable" (loud
# `malformed-test-first-field`). `**Test-first**: false` still SATISFIES
# `_TEST_FIRST_FIELD_RE` (group=false) → legitimate default-off, NOT
# malformed — the malformed branch consults the SAME value RE (M2 invariant).
_TEST_FIRST_FIELD_PRESENT_RE = re.compile(
    r"^\*\*Test[-\s]?first\*\*\s*:",
    re.IGNORECASE,
)

# AC list-item: `1. ...`, `2. ...`, etc.
_AC_ITEM_RE = re.compile(r"^\s*(\d+)\.\s+\S")

# Heading patterns
_AC_SECTION_HEADING = re.compile(r"^##\s+Acceptance\s+criteria\s*$", re.IGNORECASE)
_TEST_FIRST_SECTION_HEADING = re.compile(r"^##\s+Test-first\s+plan\s*$", re.IGNORECASE)
_OTHER_H2_RE = re.compile(r"^##\s+\S")

# Allowed statuses
_ALLOWED_STATUSES: frozenset[str] = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})

# Required columns for the test-first table
_REQUIRED_COLUMNS = 5

_EMPTY_SENTINELS = frozenset({"", "—", "-", "n/a", "none", "(none)"})


@dataclass(frozen=True)
class TestFirstRow:
    ac: str           # the AC reference, e.g. "AC#1" or "1"
    test_type: str    # "unit" | "integration" | "e2e" | "manual" — free text in v1
    test_path: str
    test_function: str
    status: str       # "PENDING" | "WRITTEN-FAILING" | "PASSING"
    line: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TestFirstViolation:
    path: str
    line: int
    ac: str           # may be "" for section-level errors
    kind: str         # "missing-section" | "invalid-status" | "ac-without-row" |
                      # "format" | "non-passing-pre-finish" | "missing-cells" |
                      # "missing-test-path-file"
    severity: str     # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    test_first_enabled: bool = False
    acs_in_brief: list[str] = field(default_factory=list)
    rows: list[TestFirstRow] = field(default_factory=list)
    violations: list[TestFirstViolation] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "test_first_enabled": self.test_first_enabled,
            "acs_in_brief": list(self.acs_in_brief),
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
    return mtime_date < _TF_1_RELEASE_DATE


def _detect_test_first_flag(text: str) -> bool:
    """Return True if `**Test-first**: true` is present in the field block."""
    for line in text.splitlines():
        m = _TEST_FIRST_FIELD_RE.match(line)
        if m:
            return m.group(1).strip().lower() == "true"
    return False


def _detect_malformed_test_first_field(text: str) -> tuple[int, str] | None:
    """Per R-7 / TFFL-1 (slice-034; ADR-034): return (line_number, raw_value)
    of the first line that LOOKS like the `**Test-first**:` field but whose
    value is NOT a standalone `true|false` token (e.g. `maybe`, empty,
    `false-positive`, `true.`), and where NO line carries a valid value.

    Returns None when either (a) the field is genuinely absent (legitimate
    default-off) or (b) some line DOES satisfy the value RE (incl.
    `**Test-first**: false` — which is valid, so the field is well-formed
    and disabled, NOT malformed; the M2 both-booleans invariant).
    """
    lines = text.splitlines()
    if any(_TEST_FIRST_FIELD_RE.match(ln) for ln in lines):
        return None  # a valid true|false value line exists — not malformed
    for idx, ln in enumerate(lines, start=1):
        if _TEST_FIRST_FIELD_PRESENT_RE.match(ln):
            raw_value = ln.split(":", 1)[1].strip() if ":" in ln else ""
            return (idx, raw_value)
    return None  # field genuinely absent — legitimate default-off


def _find_acs(text: str) -> list[str]:
    """Return AC labels (e.g. ['1', '2', '3']) from the Acceptance criteria section."""
    lines = text.splitlines()
    in_section = False
    found: list[str] = []
    for line in lines:
        if _AC_SECTION_HEADING.match(line):
            in_section = True
            continue
        if in_section and _OTHER_H2_RE.match(line):
            break
        if in_section:
            m = _AC_ITEM_RE.match(line)
            if m:
                found.append(m.group(1))
    return found


def _find_test_first_table_lines(text: str) -> tuple[int, list[str]] | None:
    """Locate the Test-first plan table; return (start_line_idx, table_lines) or None."""
    lines = text.splitlines()
    heading_idx: int | None = None
    for i, line in enumerate(lines):
        if _TEST_FIRST_SECTION_HEADING.match(line):
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


def _normalize_ac_label(raw: str) -> str:
    """Normalize AC labels: 'AC#1', 'AC 1', 'ac1', '1' all -> '1'."""
    s = raw.strip().lower()
    s = s.replace("ac", "").replace("#", "").replace(" ", "")
    return s


def _find_repo_root(start: Path) -> Path:
    """Walk up from `start` for a `.git` dir or `VERSION` file sentinel.

    PTFCD-1: the existence check resolves a row's Test path repo-root-relative.
    Falls back to the brief's grandparent..parent chain root if no sentinel is
    found (never raises — a wrong root just yields a not-exists violation the
    user can read and correct, which is the intended PTFCD-1 signal).
    """
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for cand in [cur, *cur.parents]:
        if (cand / ".git").exists() or (cand / "VERSION").exists():
            return cand
    return start.resolve().parent


def _resolve_test_path(test_path: str, repo_root: Path) -> Path | None:
    """Resolve a TF-1 row Test path to an on-disk Path, or None to skip.

    PTFCD-1 path-resolution rule: skip `_EMPTY_SENTINELS` (no path to check);
    strip surrounding markdown backticks; split on `::` to drop a pytest
    selector (defensive — the 5-column TF-1 schema keeps Test path / Test
    function separate, but a Command-cell-style `path::fn` is handled too);
    resolve repo-root-relative. Returns None when there is no path to verify.
    """
    raw = test_path.strip()
    if raw.lower() in _EMPTY_SENTINELS:
        return None
    raw = raw.strip("`").strip()
    raw = raw.split("::", 1)[0].strip()
    if not raw or raw.lower() in _EMPTY_SENTINELS:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate


def audit_brief_file(
    brief_path: Path,
    strict_pre_finish: bool = False,
    skip_if_carry_over: bool = True,
) -> AuditResult:
    """Audit a mission-brief.md against TF-1."""
    result = AuditResult()

    if not brief_path.exists():
        # Missing brief is silent — TF-1 is opt-in; absence isn't a violation
        return result

    if skip_if_carry_over:
        slice_folder = brief_path.parent
        if _slice_is_carry_over(slice_folder):
            result.carry_over_exempt = True
            return result

    text = brief_path.read_text(encoding="utf-8")

    enabled = _detect_test_first_flag(text)
    result.test_first_enabled = enabled
    result.acs_in_brief = _find_acs(text)

    if not enabled:
        # Per R-7 / TFFL-1: distinguish "field absent" (legitimate
        # default-off, clean) from "field present but value unparseable"
        # (loud violation — NEVER silent default-off). The malformed branch
        # runs AFTER the carry-over/missing-brief returns and AFTER
        # enabled-detection, BEFORE the silent default-off return.
        malformed = _detect_malformed_test_first_field(text)
        if malformed is not None:
            lineno, raw_value = malformed
            result.violations.append(TestFirstViolation(
                path=str(brief_path), line=lineno, ac="",
                kind="malformed-test-first-field", severity="Important",
                message=(
                    f"the `**Test-first**` field is present at line {lineno} "
                    f"but its value {raw_value!r} is not a standalone "
                    f"`true` or `false` token. Per TFFL-1 (R-7), an "
                    f"unparseable field MUST NOT silently default-off — it "
                    f"would bypass the entire TF-1 gate on a slice that "
                    f"meant to declare test-first. Accepted forms: "
                    f"`**Test-first**: true` or `**Test-first**: false`, "
                    f"optionally followed by whitespace + an annotation "
                    f"(e.g. `**Test-first**: true  (per TF-1 — ...)`)."
                ),
            ))
        return result  # default-off (now loud if a malformed field exists)

    # Test-first IS enabled — the section must exist
    found = _find_test_first_table_lines(text)
    if found is None:
        result.violations.append(TestFirstViolation(
            path=str(brief_path), line=0, ac="",
            kind="missing-section", severity="Important",
            message=(
                "`**Test-first**: true` is set but no `## Test-first plan` "
                "section with a table was found. Per TF-1, when test-first "
                "is enabled, the brief must include a 5-column table mapping "
                "every AC to its tests + status."
            ),
        ))
        return result

    table_start, table_lines = found
    if len(table_lines) < 2:
        result.violations.append(TestFirstViolation(
            path=str(brief_path), line=table_start + 1, ac="",
            kind="format", severity="Important",
            message=(
                "test-first table is malformed: needs header + separator at "
                "minimum (AC | Test type | Test path | Test function | Status)."
            ),
        ))
        return result

    if not _is_separator_row(table_lines[1]):
        result.violations.append(TestFirstViolation(
            path=str(brief_path), line=table_start + 2, ac="",
            kind="format", severity="Important",
            message=(
                "test-first table second line must be the markdown separator "
                "(`|---|---|---|---|---|`)."
            ),
        ))
        return result

    header_cells = _parse_table_cells(table_lines[0])
    if len(header_cells) < _REQUIRED_COLUMNS:
        result.violations.append(TestFirstViolation(
            path=str(brief_path), line=table_start + 1, ac="",
            kind="format", severity="Important",
            message=(
                f"test-first table needs {_REQUIRED_COLUMNS} columns "
                f"(AC | Test type | Test path | Test function | Status); "
                f"found {len(header_cells)}: {header_cells}"
            ),
        ))
        return result

    # Parse data rows
    rows_by_ac: dict[str, list[TestFirstRow]] = {}
    for idx, raw in enumerate(table_lines[2:], start=1):
        line_num = table_start + 2 + idx
        cells = _parse_table_cells(raw)
        if len(cells) < _REQUIRED_COLUMNS:
            result.violations.append(TestFirstViolation(
                path=str(brief_path), line=line_num, ac="",
                kind="missing-cells", severity="Important",
                message=(
                    f"test-first row {idx}: {len(cells)} cells; "
                    f"expected {_REQUIRED_COLUMNS}"
                ),
            ))
            continue
        ac_raw, ttype, tpath, tfunc, status_raw = (c.strip() for c in cells[:_REQUIRED_COLUMNS])
        if ac_raw.lower() in _EMPTY_SENTINELS:
            continue
        ac_norm = _normalize_ac_label(ac_raw)
        status = status_raw.upper().strip()

        if status not in _ALLOWED_STATUSES:
            result.violations.append(TestFirstViolation(
                path=str(brief_path), line=line_num, ac=ac_norm,
                kind="invalid-status", severity="Important",
                message=(
                    f"row for AC#{ac_norm}: status '{status_raw}' not in "
                    f"{sorted(_ALLOWED_STATUSES)}."
                ),
            ))
            continue

        row = TestFirstRow(
            ac=ac_norm, test_type=ttype, test_path=tpath,
            test_function=tfunc, status=status, line=line_num,
        )
        result.rows.append(row)
        rows_by_ac.setdefault(ac_norm, []).append(row)

    # Every AC in the brief must have at least one row
    for ac in result.acs_in_brief:
        if ac not in rows_by_ac:
            result.violations.append(TestFirstViolation(
                path=str(brief_path), line=table_start + 1, ac=ac,
                kind="ac-without-row", severity="Important",
                message=(
                    f"AC#{ac} is declared in the brief but has no test-first "
                    f"row. Per TF-1, every AC must map to at least one test."
                ),
            ))

    # --strict-pre-finish: every row must be PASSING
    if strict_pre_finish:
        for row in result.rows:
            if row.status != "PASSING":
                result.violations.append(TestFirstViolation(
                    path=str(brief_path), line=row.line, ac=row.ac,
                    kind="non-passing-pre-finish", severity="Important",
                    message=(
                        f"row for AC#{row.ac} ({row.test_function}) status "
                        f"is {row.status}; --strict-pre-finish requires "
                        f"PASSING. Either complete the implementation or "
                        f"remove --strict-pre-finish (only used at "
                        f"/build-slice Step 6)."
                    ),
                ))

        # PTFCD-1: every PASSING row's cited Test path must exist on disk.
        # Gated on PASSING so a still-PENDING test-first row (whose file the
        # slice itself creates later) is reported exactly once by the
        # non-passing loop above — never doubled. Non-strict runs never reach
        # here, so mid-slice PENDING rows never false-positive.
        repo_root = _find_repo_root(brief_path)
        for row in result.rows:
            if row.status != "PASSING":
                continue
            resolved = _resolve_test_path(row.test_path, repo_root)
            if resolved is None:
                continue
            if not resolved.exists():
                result.violations.append(TestFirstViolation(
                    path=str(brief_path), line=row.line, ac=row.ac,
                    kind="missing-test-path-file", severity="Important",
                    message=(
                        f"row for AC#{row.ac} ({row.test_function}) is PASSING "
                        f"but its Test path '{row.test_path}' resolves to "
                        f"'{resolved}', which does not exist on disk. "
                        f"PTFCD-1: a PASSING row may not cite a phantom "
                        f"test file (cf. slice-023 B4 / slice-024)."
                    ),
                ))

    return result


def _format_human(result: AuditResult) -> str:
    if result.carry_over_exempt:
        return (
            "Test-first audit: slice is carry-over exempt "
            "(mission-brief.md predates TF-1 release).\n"
        )
    if not result.test_first_enabled and not result.violations:
        # Per R-7 / TFFL-1: the silent "not enabled" message is reached
        # ONLY on genuine field absence. A `malformed-test-first-field`
        # violation (field present but unparseable) must render loudly via
        # the violations path below — never be masked by this short-circuit.
        return "Test-first audit: not enabled (`**Test-first**: true` absent).\n"

    if not result.violations:
        by_status = {
            s: sum(1 for r in result.rows if r.status == s)
            for s in _ALLOWED_STATUSES
        }
        return (
            f"Test-first audit: clean. {len(result.rows)} row(s) — "
            f"PASSING={by_status['PASSING']}, "
            f"WRITTEN-FAILING={by_status['WRITTEN-FAILING']}, "
            f"PENDING={by_status['PENDING']}.\n"
        )

    out: list[str] = [f"{len(result.violations)} test-first violation(s):\n\n"]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) "
            f"{f'AC#{v.ac}' if v.ac else ''}\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="test_first_audit",
        description="TF-1 test-first slice variant audit",
    )
    parser.add_argument(
        "target", type=Path,
        help="Slice folder (auto-finds mission-brief.md inside) OR a mission-brief.md file",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--strict-pre-finish", action="store_true",
        help="Refuse non-PASSING rows (use at /build-slice Step 6)",
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
