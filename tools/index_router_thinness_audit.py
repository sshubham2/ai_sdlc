"""Index-router thinness audit (ADR-093, slice-103).

Fail-closed enforcement that the two hot vault index routers stay THIN routers,
plus the standalone cross-slice action-points register stays bounded — so the
"thin" contract that `skills/archive/SKILL.md` asserts in prose (L113 "one-line
summary, trimmed to one line"; L115/L120 "~10 from recent reflections") but
that was enforced by NOTHING (it drifted to 319.5 KB / 414.1 KB) cannot silently
re-bloat.

MEPD-1 EXCLUDE (ADR-093): this enforces an already-documented prose contract +
adds a tool; it mints no new methodology RULE-ID / changelog entry / VERSION bump
(slice-100 `vault_flip_readiness_audit` precedent — a new audit tool added
EXCLUDE, enumerated in plugin.yaml + install_audit, no VERSION change). Wired
shippability-only (a regression-catalog row run at `/validate-slice` pre-finish),
NOT a `####` Step-6 gate-roster entry.

Region-anchored, NOT whole-file token scans (per the slice-099/100 "a
marker/token detector must be region-anchored, not `marker in line_text`" lesson,
N=4; mission-brief Must-not-defer):

- `_index.md` "## Most recent 10" table — data rows (the `|`-lines between the
  table header+separator and the next non-pipe line / next `## ` heading), each
  ≤ `_MAX_ROW_CHARS`; at most `_MAX_RECENT_ROWS` data rows.
- `archive/_index.md` catalog — the file has NO `## ` heading (H1 + prose + one
  table), so the region anchor is the contiguous block of `|`-lines FOLLOWING the
  `| # | Slice | Shipped | ... |` header row (header + `|---|` separator excluded,
  terminated at the first non-pipe line or EOF). A `|`-containing prose line BEFORE
  the header is NOT counted (M3).
- `action-points.md` register (B1 — a STANDALONE file the `_index.md` regen never
  touches, so preservation is structural, not prose) — `1 ≤ entries ≤
  _MAX_ACTION_POINTS`, each entry (`- **AP-<n>**` line) carrying exactly one
  `[<verdict>]` tag ∈ `_VALID_VERDICTS`.
- Total-file-size backstops on both index files (catches a NEW bloated section the
  region checks don't anchor on — defense in depth).

Resolves all three files via `tools/_vault_paths.VAULT_ROOT` (flip-safe routing,
consistent with slice-093/098/100/102). No bare `architecture` path literal in
this module — see the VAULT_ROOT-routed `_router_paths` (flip-readiness, M5).

Usage:
    python -m tools.index_router_thinness_audit
    python -m tools.index_router_thinness_audit --json
    python -m tools.index_router_thinness_audit --root <repo-root>

Exit codes:
    0  clean (both routers thin + register bounded/tagged)
    1  violations (a row over cap, recent-10 > 10, register missing/over/untagged,
       file over the size backstop, or a required region/file absent)
    2  usage error (repo root unresolvable)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools import _stdout
from tools._vault_paths import VAULT_ROOT

# --- Tunable thinness budgets (SSoT — SKILL.md prose cites these by NAME) -------
_MAX_ROW_CHARS = 500            # m3: per-row cap (raised from 400 for the worst-case
                                # folder-name row, where a 64-char name appears twice
                                # in the link markup). Today's rows are 1,250-13,720.
_MAX_RECENT_ROWS = 10           # m1: "Most recent 10" must be exactly that.
_MAX_ACTION_POINTS = 25         # bounded synthesized register.
_VALID_VERDICTS = frozenset(
    {"already-a-gate", "build-check-candidate", "critic-calibrate-probe", "cultural"}
)
_MAX_INDEX_BYTES = 65_536       # _index.md size backstop (~64 KB).
_MAX_ARCHIVE_BYTES = 163_840    # archive/_index.md size backstop (~160 KB).

# --- Region anchors -------------------------------------------------------------
# A markdown table data row is a `|`-prefixed line (after lstrip) that is NOT the
# `|---|`/`| :--- |` separator. Header detection is structural (the first `|`-line
# of a table block) for recent-10; for the heading-less archive catalog the header
# is matched explicitly by its column labels.
_PIPE_LINE_RE = re.compile(r"^\s*\|")
_SEPARATOR_RE = re.compile(r"^\s*\|[\s:|-]+\|?\s*$")   # | --- | :---: | etc.
_HEADING_RE = re.compile(r"^\s*##\s")
_RECENT10_HEADING_RE = re.compile(r"^\s*##\s+Most recent 10\b", re.IGNORECASE)
# The archive catalog header row: `| # | Slice | Shipped | ... |`.
_ARCHIVE_HEADER_RE = re.compile(r"^\s*\|\s*#\s*\|\s*Slice\s*\|\s*Shipped\b", re.IGNORECASE)
# A register entry line: `- **AP-<n>** ...`.
_AP_ENTRY_RE = re.compile(r"^\s*-\s+\*\*AP-\d+\*\*")
# M2: the verdict tag is anchored to the LEADING position right after the `**AP-n**`
# marker (`- **AP-n** [verdict] ...`) — NOT scanned across the whole line. A
# whole-line scan would also count a descriptive `[verdict]` word mentioned later in
# the entry's prose (or inside a markdown link / inline code), re-introducing the
# slice-099/100 `marker in line_text` anti-pattern that AP-1 itself warns against and
# false-failing a future descriptive re-synthesis of the register.
_AP_LEADING_TAG_RE = re.compile(r"^\s*-\s+\*\*AP-\d+\*\*\s+\[([a-z][a-z-]*)\]")


@dataclass(frozen=True)
class IRTViolation:
    kind: str       # row-too-long | recent-10-too-many | recent-10-section-missing |
                    # archive-catalog-missing | register-missing | register-too-many |
                    # register-untagged | file-too-large | usage-error
    severity: str   # "Important" (all IRT-thinness violations refuse)
    message: str
    locus: str = ""  # "path:line" or "path"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    repo_root: str = ""
    index_path: str = ""
    archive_path: str = ""
    register_path: str = ""
    recent_row_count: int = 0
    archive_row_count: int = 0
    register_entry_count: int = 0
    violations: list[IRTViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": "IRT (ADR-093)",
            "repo_root": self.repo_root,
            "index_path": self.index_path,
            "archive_path": self.archive_path,
            "register_path": self.register_path,
            "recent_row_count": self.recent_row_count,
            "archive_row_count": self.archive_row_count,
            "register_entry_count": self.register_entry_count,
            "budgets": {
                "max_row_chars": _MAX_ROW_CHARS,
                "max_recent_rows": _MAX_RECENT_ROWS,
                "max_action_points": _MAX_ACTION_POINTS,
                "max_index_bytes": _MAX_INDEX_BYTES,
                "max_archive_bytes": _MAX_ARCHIVE_BYTES,
            },
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len(self.violations),
                "clean": not self.violations,
            },
        }


# --- Pure region extractors (testable on text, no repo needed) ------------------

def _lines(text: str) -> list[str]:
    """Split into logical lines, CRLF-aware, WITHOUT splitting on the exotic
    Unicode line boundaries `str.splitlines()` honours (`\\v \\f \\x1c-\\x1e \\x85
    U+2028 U+2029`) — m1: a row containing one of those must NOT be split into
    sub-cap fragments that evade the per-row cap. `\\n` split + `\\r` strip covers
    LF and CRLF; nothing else is treated as a line boundary."""
    return [ln.rstrip("\r") for ln in text.split("\n")]


def _data_rows_after(lines: list[str], start_idx: int) -> tuple[bool, list[tuple[int, str]]]:
    """Return ``(table_header_found, [(1-based line number, line), ...])`` for the
    contiguous table DATA rows starting at the table whose first `|`-line is at/after
    ``start_idx``.

    The block is: first `|`-line (header) + the `|---|` separator + subsequent
    `|`-lines, terminated at the first non-pipe line. Header + separator excluded.
    Blank lines between the heading and the table header are skipped.

    ``table_header_found`` is False when NO `|`-line exists under the region before
    the next `## ` heading / EOF — i.e. the table structure is absent entirely
    (M1: a region whose table was lost in a regen, distinct from a present-but-empty
    table which is a legitimate fresh-project 0-row state).
    """
    i = start_idx
    n = len(lines)
    # Advance to the first pipe-line (the header).
    while i < n and not _PIPE_LINE_RE.match(lines[i]):
        # Stop if we hit the next section before any table materialises.
        if _HEADING_RE.match(lines[i]) and i != start_idx:
            return False, []
        i += 1
    if i >= n:
        return False, []
    # i = header row (table structure present). Skip header.
    i += 1
    # Skip the separator row if present.
    if i < n and _SEPARATOR_RE.match(lines[i]):
        i += 1
    rows: list[tuple[int, str]] = []
    while i < n and _PIPE_LINE_RE.match(lines[i]):
        if not _SEPARATOR_RE.match(lines[i]):
            rows.append((i + 1, lines[i]))
        i += 1
    return True, rows


def check_recent_10(index_text: str, index_label: str) -> tuple[int, list[IRTViolation]]:
    """Check the `## Most recent 10` table: each data row ≤ cap, ≤ 10 rows."""
    violations: list[IRTViolation] = []
    lines = _lines(index_text)
    heading_idx = next(
        (idx for idx, ln in enumerate(lines) if _RECENT10_HEADING_RE.match(ln)), None
    )
    if heading_idx is None:
        violations.append(
            IRTViolation(
                kind="recent-10-section-missing",
                severity="Important",
                message="no `## Most recent 10` section found in _index.md (fail-closed)",
                locus=index_label,
            )
        )
        return 0, violations
    found_header, rows = _data_rows_after(lines, heading_idx + 1)
    if not found_header:
        # M1: heading present but NO table structure under it (regen lost the table).
        # A present-but-empty table (header + 0 rows) is a legitimate fresh-project
        # state and is NOT flagged — only a wholly-absent table is fail-closed.
        violations.append(
            IRTViolation(
                kind="recent-10-section-missing",
                severity="Important",
                message="`## Most recent 10` heading present but no table found beneath it (fail-closed)",
                locus=index_label,
            )
        )
        return 0, violations
    for lineno, row in rows:
        if len(row) > _MAX_ROW_CHARS:
            violations.append(
                IRTViolation(
                    kind="row-too-long",
                    severity="Important",
                    message=f"recent-10 row is {len(row)} chars (cap {_MAX_ROW_CHARS})",
                    locus=f"{index_label}:{lineno}",
                )
            )
    if len(rows) > _MAX_RECENT_ROWS:
        violations.append(
            IRTViolation(
                kind="recent-10-too-many",
                severity="Important",
                message=f"`## Most recent 10` has {len(rows)} data rows (max {_MAX_RECENT_ROWS})",
                locus=index_label,
            )
        )
    return len(rows), violations


def check_archive_catalog(archive_text: str, archive_label: str) -> tuple[int, list[IRTViolation]]:
    """Check the heading-less archive catalog: data rows after the `| # | Slice |
    Shipped` header, each ≤ cap. A `|`-prose line BEFORE the header is not counted."""
    # m2: the archive catalog row COUNT is intentionally unbounded — it is a
    # newest-first chronological ledger that grows by one thin row per slice
    # (unlike the fixed-window recent-10). Only the per-row char cap + the total
    # `_MAX_ARCHIVE_BYTES` backstop bound it; there is deliberately no `_MAX_ARCHIVE_ROWS`.
    violations: list[IRTViolation] = []
    lines = _lines(archive_text)
    header_idx = next(
        (idx for idx, ln in enumerate(lines) if _ARCHIVE_HEADER_RE.match(ln)), None
    )
    if header_idx is None:
        violations.append(
            IRTViolation(
                kind="archive-catalog-missing",
                severity="Important",
                message="no `| # | Slice | Shipped | ... |` catalog header row found (fail-closed)",
                locus=archive_label,
            )
        )
        return 0, violations
    # Data rows = contiguous pipe-lines after header (+ separator), excluding separator.
    i = header_idx + 1
    if i < len(lines) and _SEPARATOR_RE.match(lines[i]):
        i += 1
    rows: list[tuple[int, str]] = []
    while i < len(lines) and _PIPE_LINE_RE.match(lines[i]):
        if not _SEPARATOR_RE.match(lines[i]):
            rows.append((i + 1, lines[i]))
        i += 1
    for lineno, row in rows:
        if len(row) > _MAX_ROW_CHARS:
            violations.append(
                IRTViolation(
                    kind="row-too-long",
                    severity="Important",
                    message=f"archive catalog row is {len(row)} chars (cap {_MAX_ROW_CHARS})",
                    locus=f"{archive_label}:{lineno}",
                )
            )
    return len(rows), violations


def check_register(register_text: str | None, register_label: str) -> tuple[int, list[IRTViolation]]:
    """Check the standalone action-points register: 1..25 entries, each carrying
    exactly one valid `[verdict]` tag. Absent/empty file → register-missing."""
    violations: list[IRTViolation] = []
    if register_text is None or not register_text.strip():
        violations.append(
            IRTViolation(
                kind="register-missing",
                severity="Important",
                message="action-points.md register is absent or empty (fail-closed)",
                locus=register_label,
            )
        )
        return 0, violations
    lines = _lines(register_text)
    entries = [(idx + 1, ln) for idx, ln in enumerate(lines) if _AP_ENTRY_RE.match(ln)]
    if not entries:
        violations.append(
            IRTViolation(
                kind="register-missing",
                severity="Important",
                message="action-points.md has no `- **AP-<n>**` register entries (fail-closed)",
                locus=register_label,
            )
        )
        return 0, violations
    if len(entries) > _MAX_ACTION_POINTS:
        violations.append(
            IRTViolation(
                kind="register-too-many",
                severity="Important",
                message=f"register has {len(entries)} entries (max {_MAX_ACTION_POINTS})",
                locus=register_label,
            )
        )
    for lineno, entry in entries:
        m = _AP_LEADING_TAG_RE.match(entry)  # M2: leading-anchored, not whole-line scan
        if m is None or m.group(1) not in _VALID_VERDICTS:
            found = m.group(1) if m else "(none)"
            violations.append(
                IRTViolation(
                    kind="register-untagged",
                    severity="Important",
                    message=(
                        f"register entry must carry exactly one verdict tag "
                        f"∈ {sorted(_VALID_VERDICTS)} as the LEADING `[tag]` right after "
                        f"`**AP-n**`; found {found!r}"
                    ),
                    locus=f"{register_label}:{lineno}",
                )
            )
    return len(entries), violations


def _check_size(path: Path, limit: int, label: str) -> list[IRTViolation]:
    if not path.exists():
        return []  # absence handled by the region checks (fail-closed there)
    size = path.stat().st_size
    if size > limit:
        return [
            IRTViolation(
                kind="file-too-large",
                severity="Important",
                message=f"{label} is {size} bytes (backstop {limit})",
                locus=label,
            )
        ]
    return []


def _router_paths(repo_root: Path) -> tuple[Path, Path, Path]:
    """VAULT_ROOT-routed paths for the two index files + the register (flip-safe;
    no bare `architecture` literal — M5)."""
    slices = repo_root / VAULT_ROOT / "slices"
    return (
        slices / "_index.md",
        slices / "archive" / "_index.md",
        slices / "action-points.md",
    )


def audit(
    repo_root: Path | None = None,
    *,
    index_path: Path | None = None,
    archive_path: Path | None = None,
    register_path: Path | None = None,
) -> AuditResult:
    """Run the index-router thinness audit.

    Tests pass explicit ``index_path`` / ``archive_path`` / ``register_path`` to
    audit fixtures; the CLI resolves them from ``repo_root`` via VAULT_ROOT.
    """
    if index_path is None or archive_path is None or register_path is None:
        if repo_root is None:
            for parent in [Path.cwd()] + list(Path.cwd().parents):
                if (parent / ".git").exists():
                    repo_root = parent
                    break
        if repo_root is None:
            return AuditResult(
                violations=[
                    IRTViolation(
                        kind="usage-error",
                        severity="Important",
                        message="repo root unresolvable (no --root and no .git ancestor of cwd)",
                    )
                ]
            )
        repo_root = Path(repo_root).resolve()
        ip, ap, rp = _router_paths(repo_root)
        index_path = index_path or ip
        archive_path = archive_path or ap
        register_path = register_path or rp

    result = AuditResult(
        repo_root=str(repo_root) if repo_root else "",
        index_path=str(index_path),
        archive_path=str(archive_path),
        register_path=str(register_path),
    )

    # _index.md recent-10
    if index_path.exists():
        idx_text = index_path.read_text(encoding="utf-8")
        result.recent_row_count, viols = check_recent_10(idx_text, str(index_path))
        result.violations.extend(viols)
        result.violations.extend(_check_size(index_path, _MAX_INDEX_BYTES, str(index_path)))
    else:
        result.violations.append(
            IRTViolation(
                kind="recent-10-section-missing",
                severity="Important",
                message=f"_index.md not found: {index_path}",
                locus=str(index_path),
            )
        )

    # archive/_index.md catalog
    if archive_path.exists():
        arc_text = archive_path.read_text(encoding="utf-8")
        result.archive_row_count, viols = check_archive_catalog(arc_text, str(archive_path))
        result.violations.extend(viols)
        result.violations.extend(_check_size(archive_path, _MAX_ARCHIVE_BYTES, str(archive_path)))
    else:
        result.violations.append(
            IRTViolation(
                kind="archive-catalog-missing",
                severity="Important",
                message=f"archive/_index.md not found: {archive_path}",
                locus=str(archive_path),
            )
        )

    # action-points.md register (B1 — standalone)
    reg_text = register_path.read_text(encoding="utf-8") if register_path.exists() else None
    result.register_entry_count, viols = check_register(reg_text, str(register_path))
    result.violations.extend(viols)

    return result


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="index_router_thinness_audit",
        description="IRT audit (ADR-093): pin the thinness of the two hot vault index routers + the action-points register.",
    )
    parser.add_argument("--root", type=Path, default=None, help="Repo root (default: ancestor with .git).")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args(argv)

    try:
        result = audit(repo_root=args.root)
    except Exception as e:  # noqa: BLE001 — top-level CLI guard
        print(f"index_router_thinness_audit: error: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.violations:
            for v in result.violations:
                loc = f" ({v.locus})" if v.locus else ""
                print(f"[{v.severity}] {v.kind}: {v.message}{loc}")
        else:
            print(
                f"IRT audit: clean. recent-10={result.recent_row_count} rows, "
                f"archive={result.archive_row_count} rows, register={result.register_entry_count} entries "
                f"(caps: row≤{_MAX_ROW_CHARS}, recent≤{_MAX_RECENT_ROWS}, register≤{_MAX_ACTION_POINTS})."
            )

    if any(v.kind == "usage-error" for v in result.violations):
        return 2
    if result.violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
