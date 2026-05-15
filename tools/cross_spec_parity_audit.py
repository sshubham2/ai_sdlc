"""Cross-spec parity audit (CSP-1).

Walks the Heavy-mode artifacts (`architecture/threat-model.md`,
`architecture/requirements.md`, `architecture/nfrs.md`) and validates
that each item is structurally well-formed AND its `Implementation:`
(threats, requirements) or `Verification:` (NFRs) cross-reference
points to a real file under the project root.

Per CSP-1 (methodology-changelog.md v0.18.0). The rule's purpose:
keep human-authored Heavy artifacts in parity with code-derived
facts. Threats / requirements / NFRs that claim mitigations or
verifications must reference paths that actually exist; otherwise
the artifact is decoration, not discipline.

Heavy-mode-only. In Minimal / Standard mode the artifacts don't
exist; the audit returns clean (no-op).

Item structure (H2-driven, matching BC-1 / RR-1 / TRI-1 conventions):

    ## TM-NN -- <title>           (threats; threat-model.md)
    ## REQ-NN -- <title>          (requirements; requirements.md)
    ## NFR-NN -- <title>          (NFRs; nfrs.md)

Required fields per item:
  - Status: <vocabulary depends on artifact type>
  - Implementation (TM/REQ) OR Verification (NFR): file path or `n/a`

Status vocabulary:
  - Threats:       mitigated | accepted | open
  - Requirements:  implemented | pending | deferred
  - NFRs:          met | unmet | unverified

Statuses that REQUIRE a non-empty file path:
  - mitigated, implemented, met

Statuses that ACCEPT an empty / `n/a` field:
  - accepted, open, pending, deferred, unmet, unverified

Path resolution: Implementation / Verification cell is parsed as
`<file>:<func>` (or just `<file>`). The file part is resolved
relative to --root (default: cwd). Existence of the file is verified.
Function names within the file are NOT verified in v1.

NFR-1 carry-over: not applicable here — this is project-level, not
per-slice. The audit is gated by Heavy mode (via triage.md detection).

Usage:
    python -m tools.cross_spec_parity_audit
    python -m tools.cross_spec_parity_audit --root /path/to/project
    python -m tools.cross_spec_parity_audit --threats <path> --requirements <path> --nfrs <path>
    python -m tools.cross_spec_parity_audit --json

Exit codes:
    0  clean (or non-Heavy / no artifacts found)
    1  violations
    2  usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from tools import _stdout

# H2 item heading: "## TM-NN -- title" / "## REQ-NN -- title" / "## NFR-NN -- title"
_ITEM_HEADING_RE = re.compile(
    r"^##\s+((?:TM|REQ|NFR)-?\d+)\s+[—\-]\s+(.+?)\s*$"
)

# Field-line: "**Name**: value"
_FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z\s\-]*)\*\*\s*:\s*(.*?)\s*$")

# Status vocabulary by artifact prefix
_STATUS_BY_PREFIX: dict[str, frozenset[str]] = {
    "TM": frozenset({"mitigated", "accepted", "open"}),
    "REQ": frozenset({"implemented", "pending", "deferred"}),
    "NFR": frozenset({"met", "unmet", "unverified"}),
}

# Statuses that REQUIRE a non-empty Implementation / Verification path
_REQUIRES_PATH: frozenset[str] = frozenset({"mitigated", "implemented", "met"})

# Sentinel values treated as "no path provided"
_PATH_SENTINELS = frozenset({"", "—", "-", "n/a", "none", "(none)", "tbd"})

# Field that holds the cross-reference, by prefix
_REF_FIELD_BY_PREFIX: dict[str, str] = {
    "TM": "implementation",
    "REQ": "implementation",
    "NFR": "verification",
}


@dataclass(frozen=True)
class CSPItem:
    artifact: str       # "threat-model.md" | "requirements.md" | "nfrs.md"
    item_id: str        # "TM-1", "REQ-7", "NFR-3"
    prefix: str         # "TM" | "REQ" | "NFR"
    title: str
    status: str
    ref_field: str      # "implementation" | "verification"
    ref_value: str      # file:func form or sentinel
    line: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CSPViolation:
    artifact: str
    line: int
    item_id: str        # "" for artifact-level errors
    kind: str           # "missing-field" | "invalid-status" | "broken-ref" |
                        # "missing-ref" | "format"
    severity: str       # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    items: list[CSPItem] = field(default_factory=list)
    violations: list[CSPViolation] = field(default_factory=list)
    artifacts_scanned: list[str] = field(default_factory=list)
    heavy_mode: bool = False  # whether we detected Heavy mode

    def to_dict(self) -> dict:
        return {
            "items": [i.to_dict() for i in self.items],
            "violations": [v.to_dict() for v in self.violations],
            "artifacts_scanned": list(self.artifacts_scanned),
            "heavy_mode": self.heavy_mode,
            "summary": {
                "item_count": len(self.items),
                "violation_count": len(self.violations),
                "by_prefix": {
                    p: sum(1 for i in self.items if i.prefix == p)
                    for p in ("TM", "REQ", "NFR")
                },
            },
        }


def _detect_heavy_mode(root: Path) -> bool:
    """True if architecture/triage.md declares mode: Heavy."""
    triage = root / "architecture" / "triage.md"
    if not triage.exists():
        return False
    text = triage.read_text(encoding="utf-8", errors="replace")
    # Match `**Mode**: Heavy` or `Mode: Heavy` (lenient)
    if re.search(r"^\s*(?:\*\*Mode\*\*|Mode)\s*:\s*Heavy\b", text, re.MULTILINE | re.IGNORECASE):
        return True
    return False


def _normalize_id(raw: str) -> str:
    """Normalize 'TM-01' / 'TM01' / 'tm-1' -> 'TM-1'."""
    m = re.match(r"^(TM|REQ|NFR)-?(\d+)$", raw, re.IGNORECASE)
    if not m:
        return raw
    prefix = m.group(1).upper()
    num = int(m.group(2))
    return f"{prefix}-{num}"


def _is_empty_path(value: str) -> bool:
    return value.strip().lower() in _PATH_SENTINELS


def _parse_artifact(
    path: Path,
    project_root: Path,
) -> tuple[list[CSPItem], list[CSPViolation]]:
    """Parse a Heavy artifact file."""
    items: list[CSPItem] = []
    violations: list[CSPViolation] = []

    if not path.exists():
        return items, violations  # silent — artifact may not exist yet

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    headings: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        m = _ITEM_HEADING_RE.match(line)
        if m:
            headings.append((i, _normalize_id(m.group(1)), m.group(2)))

    for idx, (heading_line, item_id, title) in enumerate(headings):
        body_end = (
            headings[idx + 1][0]
            if idx + 1 < len(headings)
            else len(lines)
        )
        body_lines = lines[heading_line + 1:body_end]

        prefix = item_id.split("-", 1)[0]
        ref_field_name = _REF_FIELD_BY_PREFIX.get(prefix, "implementation")

        fields: dict[str, str] = {}
        for body_line in body_lines:
            m = _FIELD_RE.match(body_line)
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()

        # Validate Status
        if "status" not in fields:
            violations.append(CSPViolation(
                artifact=str(path), line=heading_line + 1, item_id=item_id,
                kind="missing-field", severity="Important",
                message=(
                    f"item {item_id}: missing required `Status` field. "
                    f"Allowed values for {prefix}: "
                    f"{sorted(_STATUS_BY_PREFIX.get(prefix, set()))}."
                ),
            ))
            continue

        status = fields["status"].strip().lower()
        allowed_statuses = _STATUS_BY_PREFIX.get(prefix, frozenset())
        if status not in allowed_statuses:
            violations.append(CSPViolation(
                artifact=str(path), line=heading_line + 1, item_id=item_id,
                kind="invalid-status", severity="Important",
                message=(
                    f"item {item_id}: status '{status}' not in "
                    f"{sorted(allowed_statuses)}."
                ),
            ))
            continue

        # Validate Implementation / Verification field
        ref_value = fields.get(ref_field_name, "")
        ref_empty = _is_empty_path(ref_value)

        if status in _REQUIRES_PATH and ref_empty:
            violations.append(CSPViolation(
                artifact=str(path), line=heading_line + 1, item_id=item_id,
                kind="missing-ref", severity="Important",
                message=(
                    f"item {item_id} (status={status}) requires non-empty "
                    f"`{ref_field_name.capitalize()}` field. "
                    f"For {status} items, Implementation/Verification must "
                    f"reference real code or test paths."
                ),
            ))
            continue

        items.append(CSPItem(
            artifact=str(path), item_id=item_id, prefix=prefix,
            title=title, status=status,
            ref_field=ref_field_name, ref_value=ref_value,
            line=heading_line + 1,
        ))

        # Path existence check (only when ref is non-empty)
        if not ref_empty:
            file_part = ref_value.split(":", 1)[0].strip()
            file_part = file_part.split("#", 1)[0].strip()  # strip URL fragment
            if file_part:
                # Resolve relative to project_root
                resolved = (project_root / file_part).resolve()
                if not resolved.exists():
                    violations.append(CSPViolation(
                        artifact=str(path), line=heading_line + 1,
                        item_id=item_id,
                        kind="broken-ref", severity="Important",
                        message=(
                            f"item {item_id}: "
                            f"`{ref_field_name.capitalize()}: {ref_value}` "
                            f"references a path that does not exist "
                            f"(resolved to {resolved}). Either fix the "
                            f"path, change the status, or use `n/a`."
                        ),
                    ))

    return items, violations


def run_audit(
    project_root: Path,
    threats_path: Path | None = None,
    requirements_path: Path | None = None,
    nfrs_path: Path | None = None,
    skip_heavy_check: bool = False,
) -> AuditResult:
    """Run the CSP-1 audit across all three Heavy artifacts."""
    result = AuditResult()

    is_heavy = skip_heavy_check or _detect_heavy_mode(project_root)
    result.heavy_mode = is_heavy

    if not is_heavy:
        return result  # silent in Minimal / Standard modes

    paths_to_scan: list[Path] = []
    if threats_path is None:
        threats_path = project_root / "architecture" / "threat-model.md"
    if requirements_path is None:
        requirements_path = project_root / "architecture" / "requirements.md"
    if nfrs_path is None:
        nfrs_path = project_root / "architecture" / "nfrs.md"

    for p in (threats_path, requirements_path, nfrs_path):
        paths_to_scan.append(p)
        if p.exists():
            result.artifacts_scanned.append(str(p))

    for path in paths_to_scan:
        items, violations = _parse_artifact(path, project_root)
        result.items.extend(items)
        result.violations.extend(violations)

    return result


def _format_human(result: AuditResult) -> str:
    if not result.heavy_mode:
        return (
            "CSP-1 cross-spec parity audit: not Heavy mode "
            "(no architecture/triage.md or mode != Heavy). Skipped.\n"
        )

    if not result.artifacts_scanned:
        return (
            "CSP-1 cross-spec parity audit: no Heavy artifacts found "
            "(threat-model.md / requirements.md / nfrs.md absent under "
            "architecture/).\n"
        )

    if not result.violations:
        by_prefix = {
            p: sum(1 for i in result.items if i.prefix == p)
            for p in ("TM", "REQ", "NFR")
        }
        return (
            f"CSP-1 cross-spec parity audit: clean. "
            f"{len(result.items)} item(s) — TM={by_prefix['TM']}, "
            f"REQ={by_prefix['REQ']}, NFR={by_prefix['NFR']}.\n"
        )

    out: list[str] = [
        f"{len(result.violations)} cross-spec parity violation(s):\n\n"
    ]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.artifact}:{v.line} ({v.kind}) "
            f"{f'item {v.item_id}' if v.item_id else ''}\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="cross_spec_parity_audit",
        description="CSP-1 cross-spec parity audit (Heavy mode only)",
    )
    parser.add_argument(
        "--root", type=Path, default=Path("."),
        help="Project root for resolving Implementation paths (default: cwd)",
    )
    parser.add_argument(
        "--threats", type=Path, default=None,
        help="Path to threat-model.md (default: <root>/architecture/threat-model.md)",
    )
    parser.add_argument(
        "--requirements", type=Path, default=None,
        help="Path to requirements.md (default: <root>/architecture/requirements.md)",
    )
    parser.add_argument(
        "--nfrs", type=Path, default=None,
        help="Path to nfrs.md (default: <root>/architecture/nfrs.md)",
    )
    parser.add_argument(
        "--skip-heavy-check", action="store_true",
        help="Force-run even if triage.md doesn't declare Heavy mode (testing/CI)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    result = run_audit(
        project_root=args.root,
        threats_path=args.threats,
        requirements_path=args.requirements,
        nfrs_path=args.nfrs,
        skip_heavy_check=args.skip_heavy_check,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
