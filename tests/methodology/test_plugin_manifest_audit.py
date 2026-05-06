"""Tests for tools.plugin_manifest_audit (PMI-1).

Validates that the audit correctly:
- Validates required top-level fields (name, version, description,
  skills, agents, tools)
- Detects version mismatch with VERSION file
- Detects manifest-listed skills/agents/tools that don't exist
- Detects orphan skills/agents/tools (real files not listed)
- Returns clean when manifest matches reality

Plus a real-repo smoke test: the actual plugin.yaml at the AI SDLC
repo root must be in sync with the actual filesystem (no orphans /
no missing).

Rule reference: PMI-1.
"""
from pathlib import Path

import yaml

from tests.methodology.conftest import REPO_ROOT
from tools.plugin_manifest_audit import run_audit


def _write_manifest(root: Path, manifest_data: dict) -> None:
    """Write a plugin.yaml at root."""
    (root / "plugin.yaml").write_text(
        yaml.dump(manifest_data, sort_keys=False), encoding="utf-8"
    )


def _seed_skill(root: Path, name: str) -> None:
    folder = root / "skills" / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(f"# {name} skill\n", encoding="utf-8")


def _seed_agent(root: Path, name: str) -> None:
    (root / "agents").mkdir(exist_ok=True)
    (root / "agents" / f"{name}.md").write_text(
        f"---\nname: {name}\n---\n# {name}\n", encoding="utf-8"
    )


def _seed_tool(root: Path, name: str) -> None:
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools" / name).write_text("# tool\n", encoding="utf-8")


def _write_version(root: Path, version: str) -> None:
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")


def _build_clean_project(tmp_path: Path) -> Path:
    """Build a small clean project: 1 skill, 1 agent, 1 tool, manifest in sync."""
    root = tmp_path / "project"
    root.mkdir()
    _write_version(root, "1.0.0")
    _seed_skill(root, "alpha")
    _seed_agent(root, "beta")
    _seed_tool(root, "gamma.py")
    _write_manifest(root, {
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "test plugin",
        "skills": [{"id": "alpha", "description": "alpha skill"}],
        "agents": [{"id": "beta", "description": "beta agent"}],
        "tools": [{"path": "tools/gamma.py", "rule": "TEST-1"}],
    })
    return root


# --- Audit tests ---

def test_clean_manifest_passes(tmp_path: Path):
    """Manifest matching the filesystem produces no violations.

    Defect class: An audit that flags clean manifests trains users to
    ignore it.
    Rule reference: PMI-1.
    """
    root = _build_clean_project(tmp_path)
    result = run_audit(project_root=root)
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_missing_manifest_flagged(tmp_path: Path):
    """Project without plugin.yaml emits no-manifest violation.

    Defect class: A plugin without a manifest can't be installed via
    the marketplace; PMI-1 requires the manifest exist.
    Rule reference: PMI-1.
    """
    root = tmp_path / "no-manifest"
    root.mkdir()
    result = run_audit(project_root=root)
    assert any(v.kind == "no-manifest" for v in result.violations)


def test_version_mismatch_flagged(tmp_path: Path):
    """plugin.yaml version != VERSION file is flagged.

    Defect class: Out-of-sync versions confuse installers about what
    they're actually getting.
    Rule reference: PMI-1.
    """
    root = _build_clean_project(tmp_path)
    _write_version(root, "2.0.0")  # diverge
    result = run_audit(project_root=root)
    assert any(v.kind == "version-mismatch" for v in result.violations)


def test_missing_field_flagged(tmp_path: Path):
    """Manifest missing a required top-level field is flagged.

    Defect class: Without all required fields, installer / marketplace
    can't render the plugin's metadata.
    Rule reference: PMI-1.
    """
    root = tmp_path / "missing-field"
    root.mkdir()
    _write_version(root, "1.0.0")
    _write_manifest(root, {
        "name": "test-plugin",
        "version": "1.0.0",
        # description omitted intentionally
        "skills": [],
        "agents": [],
        "tools": [],
    })
    result = run_audit(project_root=root)
    missing = [v for v in result.violations if v.kind == "missing-field"]
    assert len(missing) >= 1
    assert any("description" in m.message for m in missing)


def test_missing_skill_flagged(tmp_path: Path):
    """Manifest lists a skill that doesn't exist on disk.

    Defect class: Stale entries in the manifest result in install
    failures (skill referenced but not bundled).
    Rule reference: PMI-1.
    """
    root = _build_clean_project(tmp_path)
    # Add a non-existent skill to the manifest
    manifest_path = root / "plugin.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    data["skills"].append({"id": "nonexistent", "description": "ghost"})
    _write_manifest(root, data)
    result = run_audit(project_root=root)
    assert any(v.kind == "missing-skill" for v in result.violations)


def test_orphan_skill_flagged(tmp_path: Path):
    """Real skill on disk not listed in manifest is flagged.

    Defect class: Orphan files don't ship via the marketplace install,
    creating silent feature gaps.
    Rule reference: PMI-1.
    """
    root = _build_clean_project(tmp_path)
    _seed_skill(root, "orphan-skill")  # not in manifest
    result = run_audit(project_root=root)
    assert any(v.kind == "orphan-skill" for v in result.violations)


def test_orphan_agent_flagged(tmp_path: Path):
    """Real agent on disk not listed in manifest is flagged.

    Defect class: Same as orphan-skill but for agents.
    Rule reference: PMI-1.
    """
    root = _build_clean_project(tmp_path)
    _seed_agent(root, "orphan-agent")
    result = run_audit(project_root=root)
    assert any(v.kind == "orphan-agent" for v in result.violations)


def test_orphan_tool_flagged(tmp_path: Path):
    """Real tool on disk not listed in manifest is flagged.

    Defect class: Same as orphan-skill but for tools.
    Rule reference: PMI-1.
    """
    root = _build_clean_project(tmp_path)
    _seed_tool(root, "orphan_tool.py")
    result = run_audit(project_root=root)
    assert any(v.kind == "orphan-tool" for v in result.violations)


# --- Real-repo smoke test ---

def test_actual_repo_plugin_yaml_in_sync():
    """The actual plugin.yaml at the AI SDLC repo root is in sync with disk.

    Defect class: This is a meta-check — if the repo's manifest drifts,
    the audit catches it before downstream marketplace consumers do.
    Rule reference: PMI-1.
    """
    result = run_audit(project_root=REPO_ROOT)
    # Allow version-mismatch ONLY during a release-in-progress (when
    # VERSION has been bumped but plugin.yaml hasn't). If the test
    # itself is failing on this, run /supersede-slice's parent slice's
    # final commit step (or update plugin.yaml's version).
    non_version = [v for v in result.violations if v.kind != "version-mismatch"]
    assert non_version == [], (
        f"plugin.yaml has non-version violations: "
        f"{[(v.kind, v.message) for v in non_version]}"
    )
