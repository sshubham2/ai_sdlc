"""Plugin manifest audit (PMI-1).

Validates the AI SDLC plugin manifest (`plugin.yaml` at repo root)
against the actual filesystem layout:
  - All required top-level fields present (name, version, description,
    skills, agents, tools)
  - Manifest version matches the top-level `VERSION` file
  - Every skill listed in the manifest has a corresponding
    `skills/<id>/SKILL.md`
  - Every agent listed has `agents/<id>.md`
  - Every tool listed has the file at the declared path
  - No orphan skills (real skills/<dir>/SKILL.md not in manifest)
  - No orphan agents (real agents/*.md, excluding AUTHORING.md, not
    in manifest)
  - No orphan tools (real tools/*.py, excluding __init__.py, not in
    manifest)

Per PMI-1 (methodology-changelog.md v0.19.0). The rule's purpose: a
plugin manifest that drifts from the actual distribution is worse
than no manifest — installers see "anthropic-ai-sdlc 0.19.0" with N
skills but the package contains N+M because someone added a skill
without updating the manifest. PMI-1 keeps both in sync at audit time.

The manifest format is YAML with a documented top-level shape; the
audit treats it as a starting-point format. As the Claude Code plugin
marketplace spec stabilizes, this file may be reformatted (e.g. to
`.claude-plugin/plugin.json`) and the audit regex updated.

Usage:
    python -m tools.plugin_manifest_audit
    python -m tools.plugin_manifest_audit --root <project-root>
    python -m tools.plugin_manifest_audit --json

Exit codes:
    0  clean
    1  violations
    2  usage error
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml
from tools import _stdout


_REQUIRED_TOP_FIELDS: tuple[str, ...] = (
    "name", "version", "description", "skills", "agents", "tools",
)


@dataclass(frozen=True)
class PMIViolation:
    path: str
    kind: str         # "missing-field" | "version-mismatch" | "missing-skill" |
                      # "missing-agent" | "missing-tool" | "orphan-skill" |
                      # "orphan-agent" | "orphan-tool" | "no-manifest" |
                      # "parse-error"
    severity: str     # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    manifest_path: str = ""
    name: str = ""
    version: str = ""
    declared_skills: list[str] = field(default_factory=list)
    declared_agents: list[str] = field(default_factory=list)
    declared_tools: list[str] = field(default_factory=list)
    actual_skills: list[str] = field(default_factory=list)
    actual_agents: list[str] = field(default_factory=list)
    actual_tools: list[str] = field(default_factory=list)
    violations: list[PMIViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "manifest_path": self.manifest_path,
            "name": self.name,
            "version": self.version,
            "declared": {
                "skills": list(self.declared_skills),
                "agents": list(self.declared_agents),
                "tools": list(self.declared_tools),
            },
            "actual": {
                "skills": list(self.actual_skills),
                "agents": list(self.actual_agents),
                "tools": list(self.actual_tools),
            },
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len(self.violations),
                "skills_in_sync": (
                    set(self.declared_skills) == set(self.actual_skills)
                ),
                "agents_in_sync": (
                    set(self.declared_agents) == set(self.actual_agents)
                ),
                "tools_in_sync": (
                    set(self.declared_tools) == set(self.actual_tools)
                ),
            },
        }


def _list_actual_skills(root: Path) -> list[str]:
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    return sorted(
        p.name for p in skills_dir.iterdir()
        if p.is_dir() and (p / "SKILL.md").exists()
    )


def _list_actual_agents(root: Path) -> list[str]:
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return []
    return sorted(
        p.stem for p in agents_dir.glob("*.md")
        if p.stem.lower() != "authoring"
    )


def _list_actual_tools(root: Path) -> list[str]:
    """List invocable tools (excludes __init__.py + leading-underscore helpers).

    Per UTF8-STDOUT-1 (slice-023 / B2 ACCEPTED-PENDING): leading-underscore
    modules are helpers (no main(), not invoked as `$PY -m tools._X`), so
    they MUST NOT appear in the plugin.yaml `tools:` list. The filter here
    matches that convention so PMI-1 doesn't fire an `orphan-tool`
    violation on `tools/_stdout.py` and similar helpers.
    """
    tools_dir = root / "tools"
    if not tools_dir.exists():
        return []
    return sorted(
        f"tools/{p.name}" for p in tools_dir.glob("*.py")
        if p.name != "__init__.py" and not p.name.startswith("_")
    )


def _read_version_file(root: Path) -> str:
    vfile = root / "VERSION"
    if not vfile.exists():
        return ""
    return vfile.read_text(encoding="utf-8").strip()


def run_audit(project_root: Path) -> AuditResult:
    """Run the PMI-1 manifest audit."""
    result = AuditResult()

    manifest = project_root / "plugin.yaml"
    if not manifest.exists():
        result.violations.append(PMIViolation(
            path=str(manifest), kind="no-manifest", severity="Important",
            message=(
                f"plugin.yaml not found at {manifest}. Per PMI-1, the "
                f"AI SDLC plugin must declare its contents in a manifest "
                f"that the audit cross-references against the actual "
                f"filesystem."
            ),
        ))
        return result
    result.manifest_path = str(manifest)

    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        result.violations.append(PMIViolation(
            path=str(manifest), kind="parse-error", severity="Important",
            message=f"YAML parse error: {e}",
        ))
        return result

    if not isinstance(data, dict):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="parse-error", severity="Important",
            message="manifest top level is not a YAML mapping",
        ))
        return result

    # Required fields
    for field_name in _REQUIRED_TOP_FIELDS:
        if field_name not in data:
            result.violations.append(PMIViolation(
                path=str(manifest), kind="missing-field", severity="Important",
                message=(
                    f"manifest missing required field: {field_name}. "
                    f"Required: {', '.join(_REQUIRED_TOP_FIELDS)}."
                ),
            ))

    result.name = str(data.get("name", "") or "").strip()
    result.version = str(data.get("version", "") or "").strip()

    # Version sync with VERSION file
    version_file = _read_version_file(project_root)
    if version_file and result.version and version_file != result.version:
        result.violations.append(PMIViolation(
            path=str(manifest), kind="version-mismatch", severity="Important",
            message=(
                f"plugin.yaml version '{result.version}' does not match "
                f"VERSION file '{version_file}'. PMI-1 requires both to "
                f"track methodology semver in lock-step."
            ),
        ))

    # Skills
    declared_skills = []
    for entry in data.get("skills") or []:
        if isinstance(entry, dict) and "id" in entry:
            declared_skills.append(str(entry["id"]).strip())
        elif isinstance(entry, str):
            declared_skills.append(entry.strip())
    result.declared_skills = sorted(declared_skills)
    result.actual_skills = _list_actual_skills(project_root)

    declared_set = set(result.declared_skills)
    actual_set = set(result.actual_skills)
    for missing in sorted(declared_set - actual_set):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="missing-skill", severity="Important",
            message=(
                f"manifest declares skill '{missing}' but no "
                f"skills/{missing}/SKILL.md exists."
            ),
        ))
    for orphan in sorted(actual_set - declared_set):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="orphan-skill", severity="Important",
            message=(
                f"skill 'skills/{orphan}/' exists on disk but is not "
                f"listed in plugin.yaml. Either add it to the manifest "
                f"or remove the directory."
            ),
        ))

    # Agents
    declared_agents = []
    for entry in data.get("agents") or []:
        if isinstance(entry, dict) and "id" in entry:
            declared_agents.append(str(entry["id"]).strip())
        elif isinstance(entry, str):
            declared_agents.append(entry.strip())
    result.declared_agents = sorted(declared_agents)
    result.actual_agents = _list_actual_agents(project_root)

    declared_set = set(result.declared_agents)
    actual_set = set(result.actual_agents)
    for missing in sorted(declared_set - actual_set):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="missing-agent", severity="Important",
            message=(
                f"manifest declares agent '{missing}' but no "
                f"agents/{missing}.md exists."
            ),
        ))
    for orphan in sorted(actual_set - declared_set):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="orphan-agent", severity="Important",
            message=(
                f"agent 'agents/{orphan}.md' exists on disk but is not "
                f"listed in plugin.yaml."
            ),
        ))

    # Tools
    declared_tools = []
    for entry in data.get("tools") or []:
        if isinstance(entry, dict) and "path" in entry:
            declared_tools.append(str(entry["path"]).strip())
        elif isinstance(entry, str):
            declared_tools.append(entry.strip())
    result.declared_tools = sorted(declared_tools)
    result.actual_tools = _list_actual_tools(project_root)

    declared_set = set(result.declared_tools)
    actual_set = set(result.actual_tools)
    for missing in sorted(declared_set - actual_set):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="missing-tool", severity="Important",
            message=(
                f"manifest declares tool '{missing}' but the file does "
                f"not exist at that path."
            ),
        ))
    for orphan in sorted(actual_set - declared_set):
        result.violations.append(PMIViolation(
            path=str(manifest), kind="orphan-tool", severity="Important",
            message=(
                f"tool '{orphan}' exists on disk but is not listed in "
                f"plugin.yaml's tools section."
            ),
        ))

    return result


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        return (
            f"PMI-1 plugin manifest audit: clean. "
            f"{len(result.declared_skills)} skill(s), "
            f"{len(result.declared_agents)} agent(s), "
            f"{len(result.declared_tools)} tool(s); version "
            f"{result.version}.\n"
        )

    out: list[str] = [f"{len(result.violations)} plugin manifest violation(s):\n\n"]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path} ({v.kind})\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="plugin_manifest_audit",
        description="PMI-1 plugin manifest vs filesystem parity audit",
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
