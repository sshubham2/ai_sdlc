"""Tests for tools.install_audit (INST-1).

Validates that the audit correctly:
- Detects missing skills, agents, templates, metadata files
- Reports each missing artifact as a separate violation
- Returns clean when ~/.claude/ matches the canonical inventory
- Handles a missing ~/.claude/ directory gracefully (no-claude-dir)
- Verifies the canonical inventory matches plugin.yaml exactly (drift
  between the two = failed test, forcing co-update)

Plus prose pins for INSTALL.md (INST-1 reference + pip install +
verify-step additions).

Rule reference: INST-1.
"""
from pathlib import Path

import yaml

from tests.methodology.conftest import REPO_ROOT
from tools.install_audit import (
    _CANONICAL_AGENTS,
    _CANONICAL_METADATA,
    _CANONICAL_SKILLS,
    _CANONICAL_TEMPLATES,
    _CANONICAL_TOOLS,
    run_audit,
)


def _seed_claude_dir(
    tmp_path: Path,
    skills: tuple[str, ...] = _CANONICAL_SKILLS,
    agents: tuple[str, ...] = _CANONICAL_AGENTS,
    templates: tuple[str, ...] = _CANONICAL_TEMPLATES,
    metadata: tuple[str, ...] = _CANONICAL_METADATA,
) -> Path:
    """Build a fake ~/.claude/ tree under tmp_path with the listed artifacts."""
    claude = tmp_path / ".claude"
    (claude / "skills").mkdir(parents=True)
    (claude / "agents").mkdir(parents=True)
    (claude / "templates").mkdir(parents=True)

    for skill_id in skills:
        folder = claude / "skills" / skill_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")

    for agent_id in agents:
        (claude / "agents" / f"{agent_id}.md").write_text(
            f"# {agent_id}\n", encoding="utf-8"
        )

    for template in templates:
        (claude / "templates" / template).write_text(
            f"# {template}\n", encoding="utf-8"
        )

    if "methodology-changelog.md" in metadata:
        (claude / "methodology-changelog.md").write_text("# changelog\n", encoding="utf-8")
    if "ai-sdlc-VERSION" in metadata:
        (claude / "ai-sdlc-VERSION").write_text("0.20.0\n", encoding="utf-8")

    return claude


# --- Audit behavior tests ---

def test_missing_claude_dir_flagged(tmp_path: Path):
    """A nonexistent ~/.claude/ produces a no-claude-dir violation.

    Defect class: Crashing on missing input is hostile; users without
    a previous install need a clear "INSTALL.md hasn't been run" signal.
    Rule reference: INST-1.
    """
    result = run_audit(
        claude_dir=tmp_path / "nonexistent",
        strict=False,
    )
    assert any(v.kind == "no-claude-dir" for v in result.violations)


def test_complete_install_under_strict_false_clean(tmp_path: Path):
    """Complete ~/.claude/ with strict=False (skip tool import) is clean.

    Defect class: The audit must accept a fully-populated ~/.claude/ as
    OK. Strict=False is used in tests because we can't easily mock
    importability of every canonical tool module.
    Rule reference: INST-1.
    """
    claude = _seed_claude_dir(tmp_path)
    result = run_audit(claude_dir=claude, strict=False)
    skill_violations = [v for v in result.violations if v.kind == "missing-skill"]
    agent_violations = [v for v in result.violations if v.kind == "missing-agent"]
    template_violations = [v for v in result.violations if v.kind == "missing-template"]
    metadata_violations = [v for v in result.violations if v.kind == "missing-metadata"]
    assert skill_violations == []
    assert agent_violations == []
    assert template_violations == []
    assert metadata_violations == []


def test_missing_skill_flagged(tmp_path: Path):
    """A skill from the canonical list missing on disk is flagged.

    Defect class: A user re-running INSTALL.md after a partial cleanup
    (or with a stale source folder missing a new skill) needs the audit
    to surface what's gone.
    Rule reference: INST-1.
    """
    claude = _seed_claude_dir(
        tmp_path,
        skills=tuple(s for s in _CANONICAL_SKILLS if s != "supersede-slice"),
    )
    result = run_audit(claude_dir=claude, strict=False)
    missing = [v for v in result.violations if v.kind == "missing-skill"]
    assert len(missing) == 1
    assert "supersede-slice" in missing[0].message


def test_missing_agent_flagged(tmp_path: Path):
    """A canonical agent file missing is flagged.

    Defect class: A previous install at a pre-DR-1 version doesn't have
    critique-review.md; re-running INSTALL.md should detect and copy it.
    The audit catches the case where the cp didn't reach.
    Rule reference: INST-1.
    """
    claude = _seed_claude_dir(
        tmp_path,
        agents=tuple(a for a in _CANONICAL_AGENTS if a != "critique-review"),
    )
    result = run_audit(claude_dir=claude, strict=False)
    missing = [v for v in result.violations if v.kind == "missing-agent"]
    assert len(missing) == 1
    assert "critique-review" in missing[0].message


def test_missing_template_flagged(tmp_path: Path):
    """A canonical template file missing is flagged.

    Defect class: Templates are referenced by skill prose; missing
    templates would cause downstream skill failures.
    Rule reference: INST-1.
    """
    claude = _seed_claude_dir(
        tmp_path,
        templates=tuple(t for t in _CANONICAL_TEMPLATES if t != "milestone.md"),
    )
    result = run_audit(claude_dir=claude, strict=False)
    missing = [v for v in result.violations if v.kind == "missing-template"]
    assert len(missing) == 1


def test_missing_metadata_flagged(tmp_path: Path):
    """methodology-changelog.md or ai-sdlc-VERSION missing is flagged.

    Defect class: /status reads these for the version pulse; absence
    causes /status to render incomplete output.
    Rule reference: INST-1.
    """
    claude = _seed_claude_dir(
        tmp_path,
        metadata=("methodology-changelog.md",),  # VERSION missing
    )
    result = run_audit(claude_dir=claude, strict=False)
    missing = [v for v in result.violations if v.kind == "missing-metadata"]
    assert len(missing) == 1
    assert "ai-sdlc-VERSION" in missing[0].message


def test_methodology_version_extracted_when_present(tmp_path: Path):
    """When ai-sdlc-VERSION exists, the audit reports the version string.

    Defect class: Without surfacing the version, users can't tell if
    the install matches their expected methodology version.
    Rule reference: INST-1.
    """
    claude = _seed_claude_dir(tmp_path)
    result = run_audit(claude_dir=claude, strict=False)
    assert result.methodology_version == "0.20.0"


# --- Canonical inventory must match plugin.yaml ---

def test_canonical_skills_match_plugin_yaml():
    """install_audit's canonical skill list must match plugin.yaml exactly.

    Defect class: If install_audit's hardcoded list drifts from
    plugin.yaml (PMI-1's manifest), one of the two is wrong. The audit
    is the runtime check against ~/.claude/; plugin.yaml is the source
    manifest. They must agree.
    Rule reference: INST-1 (depends on PMI-1).
    """
    manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    declared = sorted(
        entry["id"] for entry in manifest["skills"]
    )
    canonical = sorted(_CANONICAL_SKILLS)
    assert declared == canonical, (
        f"plugin.yaml skills {declared} != install_audit canonical {canonical}"
    )


def test_canonical_agents_match_plugin_yaml():
    """install_audit's canonical agent list must match plugin.yaml.

    Defect class: drift between the runtime audit's expectation and
    the source-side manifest leads to false-positive / false-negative
    install audits.
    Rule reference: INST-1 (depends on PMI-1).
    """
    manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    declared = sorted(entry["id"] for entry in manifest["agents"])
    canonical = sorted(_CANONICAL_AGENTS)
    assert declared == canonical, (
        f"plugin.yaml agents {declared} != install_audit canonical {canonical}"
    )


def test_canonical_tools_match_plugin_yaml():
    """install_audit's canonical tool list must match plugin.yaml.

    Defect class: a tool added to plugin.yaml but not install_audit
    (or vice versa) means new audits ship without the install-parity
    check.
    Rule reference: INST-1 (depends on PMI-1).
    """
    manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    declared_paths = sorted(entry["path"] for entry in manifest["tools"])
    # Convert _CANONICAL_TOOLS ('tools.foo') to plugin.yaml form ('tools/foo.py')
    canonical_paths = sorted(
        m.replace(".", "/", 1) + ".py" for m in _CANONICAL_TOOLS
    )
    assert declared_paths == canonical_paths, (
        f"plugin.yaml tools {declared_paths} != "
        f"install_audit canonical (converted) {canonical_paths}"
    )


# --- INSTALL.md prose pins ---

def test_install_md_references_inst_1_and_pip_install():
    """INSTALL.md must reference INST-1 + the pip install step.

    Defect class: Without the prose, users running INSTALL.md verbatim
    miss the new package install. The pipeline appears installed but
    the audit tools don't import.
    Rule reference: INST-1.
    """
    text = (REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    assert "INST-1" in text, "INSTALL.md missing INST-1 reference"
    assert "pip install" in text, "INSTALL.md missing pip install instruction"
    assert "ai-sdlc-tools" in text, (
        "INSTALL.md doesn't name the ai-sdlc-tools package"
    )


def test_install_md_step_4_verifies_new_artifacts():
    """INSTALL.md Step 4 verify must check critique-review agent +
    supersede-slice skill + tool import.

    Defect class: Verify steps that don't check the new artifacts
    let partial installs report as OK.
    Rule reference: INST-1.
    """
    text = (REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    assert "critique-review.md" in text
    assert "supersede-slice" in text
    assert "tools.build_checks_audit" in text or "ai-sdlc-tools" in text
    assert "install_audit" in text or "install-parity" in text


def test_install_md_documents_source_independence():
    """INSTALL.md must explicitly state the source folder can be deleted.

    Defect class: Without an explicit guarantee, users hesitate to
    clean up the source dir, leaving stale copies that drift.
    Rule reference: INST-1.
    """
    text = (REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    assert "source-independent" in text.lower() or "source independence" in text.lower()
    assert "rm -rf" in text or "delete" in text.lower()


def test_pyproject_toml_declares_tools_package():
    """pyproject.toml must declare `tools` as the only shipped package.

    Defect class: If pyproject.toml drifts, the pip install ships the
    wrong contents (e.g., installs tests/, or fails to install tools/).
    Rule reference: INST-1.
    """
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "ai-sdlc-tools"' in text
    assert 'packages = ["tools"]' in text
    assert "build-backend" in text
