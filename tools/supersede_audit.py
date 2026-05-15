"""Slice supersession audit (SUP-1).

Walks the project's active and archived slices and validates the
bidirectional consistency of slice supersession links.

Active slice mission-brief.md may declare:

    **Supersedes**: slice-NNN-<name>

Archived slice reflection.md may include:

    ## Supersession

    **Superseded by**: slice-NNN-<name>
    **Reason**: <one paragraph>

Per SUP-1 (methodology-changelog.md v0.19.0). The rule's purpose:
when a shipped slice's design turns out wrong (reality contradicts
the original assumptions), the new fix slice doesn't just exist as
"another slice"; it's explicitly linked as the supersession of the
old one. The audit catches:

  - Active slices claiming supersession of nonexistent archived slices
  - Archived slices marked superseded-by a slice that doesn't exist
    in active or archive
  - One-way links (active claims, archive doesn't acknowledge — or
    vice versa)

The audit is project-wide; not gated by Heavy mode.

Layout assumed (default):
  architecture/slices/slice-NNN-<name>/                  active slices
  architecture/slices/archive/slice-NNN-<name>/          archived slices
  architecture/slices/_index.md                          ignored

Usage:
    python -m tools.supersede_audit
    python -m tools.supersede_audit --root <project-root>
    python -m tools.supersede_audit --json

Exit codes:
    0  clean (or no supersession links found)
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

# Field-line patterns
_SUPERSEDES_RE = re.compile(
    r"^\*\*Supersedes\*\*\s*:\s*(slice-\d+-?[\w-]*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_SUPERSEDED_BY_RE = re.compile(
    r"^\*\*Superseded\s+by\*\*\s*:\s*(slice-\d+-?[\w-]*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class SupersessionLink:
    direction: str    # "supersedes" (active -> archived) | "superseded-by" (archived -> any)
    source: str       # slice id of the source
    target: str       # slice id of the target
    source_path: str  # file path that declared the link
    line: int         # line number in source file

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SUPViolation:
    path: str
    line: int
    source: str       # slice id of the source slice
    target: str       # slice id the source claims
    kind: str         # "missing-target" | "one-way-link"
    severity: str     # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    links: list[SupersessionLink] = field(default_factory=list)
    violations: list[SUPViolation] = field(default_factory=list)
    active_slices: list[str] = field(default_factory=list)
    archived_slices: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "links": [l.to_dict() for l in self.links],
            "violations": [v.to_dict() for v in self.violations],
            "active_slices": list(self.active_slices),
            "archived_slices": list(self.archived_slices),
            "summary": {
                "link_count": len(self.links),
                "violation_count": len(self.violations),
            },
        }


def _list_active_slices(slices_dir: Path) -> list[Path]:
    if not slices_dir.exists():
        return []
    return [
        p for p in sorted(slices_dir.iterdir())
        if p.is_dir() and p.name.startswith("slice-") and p.name != "archive"
    ]


def _list_archived_slices(archive_dir: Path) -> list[Path]:
    if not archive_dir.exists():
        return []
    return [
        p for p in sorted(archive_dir.iterdir())
        if p.is_dir() and p.name.startswith("slice-")
    ]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _find_supersedes(brief_path: Path) -> tuple[str, int] | None:
    """Find `**Supersedes**: slice-NNN-<name>` in mission-brief.md."""
    if not brief_path.exists():
        return None
    text = brief_path.read_text(encoding="utf-8", errors="replace")
    m = _SUPERSEDES_RE.search(text)
    if m:
        # Locate line number
        idx = m.start()
        line_no = text[:idx].count("\n") + 1
        return (m.group(1), line_no)
    return None


def _find_superseded_by(reflection_path: Path) -> tuple[str, int] | None:
    """Find `**Superseded by**: slice-NNN-<name>` in reflection.md."""
    if not reflection_path.exists():
        return None
    text = reflection_path.read_text(encoding="utf-8", errors="replace")
    m = _SUPERSEDED_BY_RE.search(text)
    if m:
        idx = m.start()
        line_no = text[:idx].count("\n") + 1
        return (m.group(1), line_no)
    return None


def run_audit(project_root: Path) -> AuditResult:
    """Run SUP-1 audit across active + archived slices."""
    result = AuditResult()

    slices_dir = project_root / "architecture" / "slices"
    archive_dir = slices_dir / "archive"

    active_paths = _list_active_slices(slices_dir)
    archived_paths = _list_archived_slices(archive_dir)
    result.active_slices = [p.name for p in active_paths]
    result.archived_slices = [p.name for p in archived_paths]

    all_known_ids: set[str] = set(result.active_slices) | set(result.archived_slices)

    # Walk active slices for Supersedes claims
    forward_claims: dict[str, tuple[str, str, int]] = {}
    # source_id -> (target_id, source_path, line)
    for slice_dir in active_paths:
        brief = slice_dir / "mission-brief.md"
        link = _find_supersedes(brief)
        if link is None:
            continue
        target, line_no = link
        result.links.append(SupersessionLink(
            direction="supersedes",
            source=slice_dir.name, target=target,
            source_path=str(brief), line=line_no,
        ))
        forward_claims[slice_dir.name] = (target, str(brief), line_no)

        if target not in all_known_ids:
            result.violations.append(SUPViolation(
                path=str(brief), line=line_no,
                source=slice_dir.name, target=target,
                kind="missing-target", severity="Important",
                message=(
                    f"slice {slice_dir.name} declares "
                    f"`**Supersedes**: {target}` but no slice with that id "
                    f"exists in active or archive. Either fix the target "
                    f"id or remove the claim."
                ),
            ))

    # Walk archived slices for Superseded-by acknowledgments
    backward_acks: dict[str, tuple[str, str, int]] = {}
    # archived_id -> (source_id, ack_path, line)
    for slice_dir in archived_paths:
        reflection = slice_dir / "reflection.md"
        link = _find_superseded_by(reflection)
        if link is None:
            continue
        source, line_no = link
        result.links.append(SupersessionLink(
            direction="superseded-by",
            source=slice_dir.name, target=source,
            source_path=str(reflection), line=line_no,
        ))
        backward_acks[slice_dir.name] = (source, str(reflection), line_no)

        if source not in all_known_ids:
            result.violations.append(SUPViolation(
                path=str(reflection), line=line_no,
                source=slice_dir.name, target=source,
                kind="missing-target", severity="Important",
                message=(
                    f"archived slice {slice_dir.name} declares "
                    f"`**Superseded by**: {source}` but no slice with that "
                    f"id exists in active or archive. Either fix the id or "
                    f"remove the claim."
                ),
            ))

    # Validate bidirectional consistency:
    # if active A claims supersedes B, archived B should have superseded-by A
    for source_id, (target_id, source_path, line_no) in forward_claims.items():
        if target_id not in result.archived_slices:
            continue  # already flagged above as missing-target
        ack = backward_acks.get(target_id)
        if ack is None or ack[0] != source_id:
            result.violations.append(SUPViolation(
                path=source_path, line=line_no,
                source=source_id, target=target_id,
                kind="one-way-link", severity="Important",
                message=(
                    f"slice {source_id} claims `**Supersedes**: {target_id}` "
                    f"but archived slice {target_id}'s reflection.md does "
                    f"NOT acknowledge it via `**Superseded by**: {source_id}`. "
                    f"Per SUP-1, both ends of the link must agree. Run "
                    f"`/supersede-slice {target_id}` to add the "
                    f"`## Supersession` section to its reflection.md."
                ),
            ))

    # Reverse direction: archived B says superseded-by A, but A doesn't claim it
    for target_id, (source_id, ack_path, line_no) in backward_acks.items():
        # Source might be active or archived
        if source_id in result.active_slices:
            forward = forward_claims.get(source_id)
            if forward is None or forward[0] != target_id:
                result.violations.append(SUPViolation(
                    path=ack_path, line=line_no,
                    source=target_id, target=source_id,
                    kind="one-way-link", severity="Important",
                    message=(
                        f"archived slice {target_id} declares "
                        f"`**Superseded by**: {source_id}` but slice "
                        f"{source_id}'s mission-brief.md does NOT have "
                        f"`**Supersedes**: {target_id}`. Add the field to "
                        f"close the bidirectional link."
                    ),
                ))

    return result


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        if not result.links:
            return (
                f"SUP-1 supersession audit: clean. No supersession links "
                f"found ({len(result.active_slices)} active + "
                f"{len(result.archived_slices)} archived slices walked).\n"
            )
        return (
            f"SUP-1 supersession audit: clean. {len(result.links)} link(s) "
            f"validated across "
            f"{len(result.active_slices)} active + "
            f"{len(result.archived_slices)} archived slices.\n"
        )

    out: list[str] = [f"{len(result.violations)} supersession violation(s):\n\n"]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) "
            f"{v.source} -> {v.target}\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="supersede_audit",
        description="SUP-1 slice supersession audit",
    )
    parser.add_argument(
        "--root", type=Path, default=Path("."),
        help="Project root (default: cwd)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    result = run_audit(project_root=args.root)

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
