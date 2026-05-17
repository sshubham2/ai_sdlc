"""Install audit (INST-1).

Validates that an installed `~/.claude/` matches the canonical inventory
of skills, agents, templates, and methodology files for AI SDLC v0.20.0.
Cross-checks the pip-installed `tools` package by importing each declared
module.

Per INST-1 (methodology-changelog.md v0.20.0). The rule's purpose:
- After INSTALL.md runs, an audit confirms the install is complete and
  source-independent. Catches partial installs (skill copied but tools
  package not pip-installed; old skills present but new ones missing
  from a stale source folder; agent file deleted by a manual cleanup
  that broke the install).
- Provides a runtime-self-check the user can invoke without the source
  folder.

Canonical inventory is hardcoded here (paired test in
test_install_audit.py verifies it matches plugin.yaml; drift between
the two surfaces as a test failure).

Usage:
    python -m tools.install_audit
    python -m tools.install_audit --claude-dir ~/.claude
    python -m tools.install_audit --json
    python -m tools.install_audit --strict      # also verify all 13 tool modules import

Exit codes:
    0  clean — install matches canonical inventory
    1  violations
    2  usage error / unrecoverable failure
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from tools import _stdout

# --- Canonical inventory for AI SDLC v0.20.0 ---
# Paired with plugin.yaml; drift between the two is a test failure.

_CANONICAL_SKILLS: tuple[str, ...] = (
    "adopt", "archive", "build-slice", "commit-slice", "critic-calibrate",
    "critique", "critique-review", "design-slice", "diagnose", "discover",
    "drift-check", "heavy-architect", "reduce", "reflect", "repro",
    "risk-spike", "slice", "slice-candidates", "status", "supersede-slice",
    "sync", "triage", "user-test", "validate-slice",
)

_CANONICAL_AGENTS: tuple[str, ...] = (
    "critic-calibrate", "critique", "critique-review",
    "diagnose-narrator", "field-recon",
)

_CANONICAL_TEMPLATES: tuple[str, ...] = (
    "mission-brief.md", "milestone.md", "critique-report.md", "reflection.md",
)

_CANONICAL_METADATA: tuple[str, ...] = (
    "methodology-changelog.md", "ai-sdlc-VERSION",
)

# The 20 tool modules post-slice-027 (18 audits + lint + install_audit itself).
# Slice-007 added tools.critique_agent_drift_audit (CAD-1 — Critic Agent Drift).
# Slice-021 added tools.branch_workflow_audit (BRANCH-1 — branch-per-slice workflow).
# Slice-023 added tools.utf8_stdout_audit (UTF8-STDOUT-1 — default UTF-8 stdout
# in audit tools); tools._stdout is a helper module (no main()) excluded from
# this canonical list by leading-underscore convention.
# Slice-026 added tools.critique_review_prerequisite_audit (CRP-1 — refuse
# /build-slice on a skipped mandatory /critique-review).
# Slice-027 added tools.pipeline_chain_audit (PCA-1 — verify the 8-skill
# pipeline-chain auto-advance directives match the canonical loop).
_CANONICAL_TOOLS: tuple[str, ...] = (
    "tools.branch_workflow_audit",
    "tools.build_checks_audit",
    "tools.build_checks_integrity",
    "tools.critique_agent_drift_audit",
    "tools.critique_review_audit",
    "tools.critique_review_prerequisite_audit",
    "tools.cross_spec_parity_audit",
    "tools.exploratory_charter_audit",
    "tools.install_audit",
    "tools.mock_budget_lint",
    "tools.pipeline_chain_audit",
    "tools.plugin_manifest_audit",
    "tools.risk_register_audit",
    "tools.shippability_decoupling_audit",
    "tools.shippability_path_audit",
    "tools.supersede_audit",
    "tools.test_first_audit",
    "tools.triage_audit",
    "tools.utf8_stdout_audit",
    "tools.validate_slice_layers",
    "tools.walking_skeleton_audit",
    "tools.wiring_matrix_audit",
)


@dataclass(frozen=True)
class InstallViolation:
    path: str
    kind: str       # "missing-skill" | "missing-agent" | "missing-template" |
                    # "missing-metadata" | "missing-tool-module" | "no-claude-dir"
    severity: str   # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    claude_dir: str = ""
    methodology_version: str = ""
    found_skills: list[str] = field(default_factory=list)
    found_agents: list[str] = field(default_factory=list)
    found_templates: list[str] = field(default_factory=list)
    found_metadata: list[str] = field(default_factory=list)
    importable_tools: list[str] = field(default_factory=list)
    violations: list[InstallViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "claude_dir": self.claude_dir,
            "methodology_version": self.methodology_version,
            "canonical": {
                "skills": list(_CANONICAL_SKILLS),
                "agents": list(_CANONICAL_AGENTS),
                "templates": list(_CANONICAL_TEMPLATES),
                "metadata": list(_CANONICAL_METADATA),
                "tools": list(_CANONICAL_TOOLS),
            },
            "found": {
                "skills": list(self.found_skills),
                "agents": list(self.found_agents),
                "templates": list(self.found_templates),
                "metadata": list(self.found_metadata),
                "importable_tools": list(self.importable_tools),
            },
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len(self.violations),
                "skills_complete": (
                    set(self.found_skills) >= set(_CANONICAL_SKILLS)
                ),
                "agents_complete": (
                    set(self.found_agents) >= set(_CANONICAL_AGENTS)
                ),
                "templates_complete": (
                    set(self.found_templates) >= set(_CANONICAL_TEMPLATES)
                ),
                "metadata_complete": (
                    set(self.found_metadata) >= set(_CANONICAL_METADATA)
                ),
                "tools_complete": (
                    set(self.importable_tools) >= set(_CANONICAL_TOOLS)
                ),
            },
        }


def _check_skills(claude_dir: Path) -> tuple[list[str], list[InstallViolation]]:
    """Walk ~/.claude/skills/ for canonical skill folders + SKILL.md."""
    skills_dir = claude_dir / "skills"
    found: list[str] = []
    violations: list[InstallViolation] = []
    for skill_id in _CANONICAL_SKILLS:
        skill_md = skills_dir / skill_id / "SKILL.md"
        if skill_md.exists():
            found.append(skill_id)
        else:
            violations.append(InstallViolation(
                path=str(skill_md), kind="missing-skill",
                severity="Important",
                message=(
                    f"canonical skill '{skill_id}' missing — expected at "
                    f"{skill_md}. Re-run INSTALL.md Step 3f."
                ),
            ))
    return found, violations


def _check_agents(claude_dir: Path) -> tuple[list[str], list[InstallViolation]]:
    """Walk ~/.claude/agents/ for canonical agent .md files."""
    agents_dir = claude_dir / "agents"
    found: list[str] = []
    violations: list[InstallViolation] = []
    for agent_id in _CANONICAL_AGENTS:
        agent_md = agents_dir / f"{agent_id}.md"
        if agent_md.exists():
            found.append(agent_id)
        else:
            violations.append(InstallViolation(
                path=str(agent_md), kind="missing-agent",
                severity="Important",
                message=(
                    f"canonical agent '{agent_id}' missing — expected at "
                    f"{agent_md}. Re-run INSTALL.md Step 3f."
                ),
            ))
    return found, violations


def _check_templates(
    claude_dir: Path,
) -> tuple[list[str], list[InstallViolation]]:
    """Walk ~/.claude/templates/ for canonical template files."""
    templates_dir = claude_dir / "templates"
    found: list[str] = []
    violations: list[InstallViolation] = []
    for template in _CANONICAL_TEMPLATES:
        template_path = templates_dir / template
        if template_path.exists():
            found.append(template)
        else:
            violations.append(InstallViolation(
                path=str(template_path), kind="missing-template",
                severity="Important",
                message=(
                    f"canonical template '{template}' missing — expected at "
                    f"{template_path}. Re-run INSTALL.md Step 3f."
                ),
            ))
    return found, violations


def _check_metadata(
    claude_dir: Path,
) -> tuple[list[str], list[InstallViolation], str]:
    """Check methodology-changelog.md + ai-sdlc-VERSION present."""
    found: list[str] = []
    violations: list[InstallViolation] = []
    version_str = ""
    for filename in _CANONICAL_METADATA:
        path = claude_dir / filename
        if path.exists():
            found.append(filename)
            if filename == "ai-sdlc-VERSION":
                try:
                    version_str = path.read_text(encoding="utf-8").strip()
                except OSError:
                    pass
        else:
            violations.append(InstallViolation(
                path=str(path), kind="missing-metadata",
                severity="Important",
                message=(
                    f"runtime metadata file '{filename}' missing — expected at "
                    f"{path}. Re-run INSTALL.md Step 3f."
                ),
            ))
    return found, violations, version_str


def _check_tool_modules(
    strict: bool = True,
) -> tuple[list[str], list[InstallViolation]]:
    """Verify each canonical tool module can be imported.

    When strict=True (the default), every module in _CANONICAL_TOOLS must
    import. When strict=False, importability is best-effort: failures are
    silently ignored (used by /status to surface a soft warning rather
    than a hard fail).
    """
    importable: list[str] = []
    violations: list[InstallViolation] = []
    for module_name in _CANONICAL_TOOLS:
        try:
            importlib.import_module(module_name)
            importable.append(module_name)
        except ImportError as e:
            if strict:
                violations.append(InstallViolation(
                    path=module_name, kind="missing-tool-module",
                    severity="Important",
                    message=(
                        f"tool module '{module_name}' not importable: {e}. "
                        f"Re-run INSTALL.md Step 3g (`pip install --upgrade "
                        f"$AI_SDLC_DIR`). Confirm the source folder has a "
                        f"current pyproject.toml."
                    ),
                ))
    return importable, violations


def run_audit(
    claude_dir: Path,
    strict: bool = True,
) -> AuditResult:
    """Run the INST-1 install audit."""
    result = AuditResult()
    result.claude_dir = str(claude_dir)

    if not claude_dir.exists():
        result.violations.append(InstallViolation(
            path=str(claude_dir), kind="no-claude-dir",
            severity="Important",
            message=(
                f"Claude directory not found: {claude_dir}. INSTALL.md has "
                f"not been run, or the path is wrong. Override with "
                f"--claude-dir <path>."
            ),
        ))
        return result

    skills, skill_v = _check_skills(claude_dir)
    agents, agent_v = _check_agents(claude_dir)
    templates, template_v = _check_templates(claude_dir)
    metadata, metadata_v, version_str = _check_metadata(claude_dir)
    tool_modules, tool_v = _check_tool_modules(strict=strict)

    result.found_skills = skills
    result.found_agents = agents
    result.found_templates = templates
    result.found_metadata = metadata
    result.importable_tools = tool_modules
    result.methodology_version = version_str
    result.violations.extend(skill_v)
    result.violations.extend(agent_v)
    result.violations.extend(template_v)
    result.violations.extend(metadata_v)
    result.violations.extend(tool_v)

    return result


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        return (
            f"INST-1 install audit: clean. "
            f"{len(result.found_skills)}/{len(_CANONICAL_SKILLS)} skills, "
            f"{len(result.found_agents)}/{len(_CANONICAL_AGENTS)} agents, "
            f"{len(result.found_templates)}/{len(_CANONICAL_TEMPLATES)} templates, "
            f"{len(result.importable_tools)}/{len(_CANONICAL_TOOLS)} tool modules"
            f"{f'; methodology v{result.methodology_version}' if result.methodology_version else ''}.\n"
        )

    out: list[str] = [
        f"{len(result.violations)} install violation(s) at {result.claude_dir}:\n\n"
    ]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path} ({v.kind})\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="install_audit",
        description="INST-1 install parity audit (~/.claude/ vs canonical inventory)",
    )
    parser.add_argument(
        "--claude-dir", type=Path, default=Path.home() / ".claude",
        help="Path to ~/.claude/ (default: $HOME/.claude)",
    )
    parser.add_argument(
        "--strict", action="store_true", default=True,
        help="Verify all canonical tool modules import (default: on)",
    )
    parser.add_argument(
        "--no-strict", dest="strict", action="store_false",
        help="Skip tool import checks (skills + agents + templates only)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    result = run_audit(claude_dir=args.claude_dir, strict=args.strict)

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
