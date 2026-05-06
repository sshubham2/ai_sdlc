"""Verify all named subagent files conform to the documented frontmatter shape.

Per agents/AUTHORING.md, every named subagent must have:
- name: kebab-case matching filename stem
- description: substantive single paragraph (>50 chars)
- tools: non-empty (comma-separated string or list)
- model: one of opus | sonnet | haiku | inherit

Rule reference: META-3.
"""
import re
from pathlib import Path

import pytest
import yaml

from tests.methodology.conftest import REPO_ROOT

AGENT_DIR = REPO_ROOT / "agents"
ALLOWED_MODELS = {"opus", "sonnet", "haiku", "inherit"}

# All .md files in agents/, excluding the authoring guide itself
NAMED_AGENT_FILES = sorted(
    p for p in AGENT_DIR.glob("*.md") if p.stem.lower() != "authoring"
)


def parse_frontmatter(file_path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file with `---` delimiters."""
    text = file_path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.+?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"{file_path.name}: no YAML frontmatter found")
    return yaml.safe_load(match.group(1))


def _normalize_tools(tools) -> list[str]:
    """Tools may be a comma-separated string or a YAML list. Return list of names."""
    if isinstance(tools, str):
        return [t.strip() for t in tools.split(",") if t.strip()]
    if isinstance(tools, list):
        return [str(t).strip() for t in tools if str(t).strip()]
    return []


def test_at_least_one_named_agent_exists():
    """Sanity check: the agents/ directory has at least one named-subagent file.

    Defect class: An empty agents/ directory means /critique, /critic-calibrate,
    /diagnose, /risk-spike all fail at dispatch — pipeline broken.
    Rule reference: META-3.
    """
    assert len(NAMED_AGENT_FILES) >= 1, (
        "No named subagent files found in agents/ (excluding AUTHORING.md)"
    )


@pytest.mark.parametrize("agent_file", NAMED_AGENT_FILES, ids=lambda p: p.stem)
def test_agent_has_required_frontmatter(agent_file: Path):
    """Every agent file must declare name, description, tools, model.

    Defect class: Missing frontmatter breaks subagent dispatch (the harness
    can't route the work without `name` and can't pick a model without `model`).
    Rule reference: META-3.
    """
    frontmatter = parse_frontmatter(agent_file)
    for field in ("name", "description", "tools", "model"):
        assert field in frontmatter, (
            f"{agent_file.name} missing required field: {field}"
        )


@pytest.mark.parametrize("agent_file", NAMED_AGENT_FILES, ids=lambda p: p.stem)
def test_agent_name_matches_filename(agent_file: Path):
    """Agent's `name:` must match the filename stem.

    Defect class: Mismatched name/filename means subagent dispatch routes to
    the wrong agent or fails. The match is what makes `subagent_type:` reliable.
    Rule reference: META-3.
    """
    frontmatter = parse_frontmatter(agent_file)
    assert frontmatter["name"] == agent_file.stem, (
        f"{agent_file.name}: name '{frontmatter['name']}' != filename stem "
        f"'{agent_file.stem}'"
    )


@pytest.mark.parametrize("agent_file", NAMED_AGENT_FILES, ids=lambda p: p.stem)
def test_agent_model_is_allowed(agent_file: Path):
    """Agent's `model:` must be one of opus/sonnet/haiku/inherit.

    Defect class: Invalid model values fail at dispatch time. Catching at
    static check is cheaper.
    Rule reference: META-3.
    """
    frontmatter = parse_frontmatter(agent_file)
    assert frontmatter["model"] in ALLOWED_MODELS, (
        f"{agent_file.name}: model '{frontmatter['model']}' not in {ALLOWED_MODELS}"
    )


@pytest.mark.parametrize("agent_file", NAMED_AGENT_FILES, ids=lambda p: p.stem)
def test_agent_tools_is_non_empty(agent_file: Path):
    """Agent's `tools:` must be non-empty.

    Defect class: An agent with no tools cannot do work. Empty tools list is a
    misconfiguration.
    Rule reference: META-3.
    """
    frontmatter = parse_frontmatter(agent_file)
    tools_list = _normalize_tools(frontmatter["tools"])
    assert len(tools_list) > 0, (
        f"{agent_file.name}: tools list is empty (got {frontmatter['tools']!r})"
    )


@pytest.mark.parametrize("agent_file", NAMED_AGENT_FILES, ids=lambda p: p.stem)
def test_agent_description_is_substantive(agent_file: Path):
    """Agent's `description:` must be substantive (>50 chars).

    Defect class: Trivial descriptions ('does X') don't help the spawning
    agent decide when to invoke; the harness shows the description on every
    consideration so substance matters.
    Rule reference: META-3.
    """
    frontmatter = parse_frontmatter(agent_file)
    description = str(frontmatter["description"])
    assert len(description) > 50, (
        f"{agent_file.name}: description too short ({len(description)} chars; "
        f"need >50)"
    )


def test_authoring_guide_exists_and_pins_canonical_sections():
    """agents/AUTHORING.md must exist and contain the documented section anchors.

    Defect class: Without an authoring guide, future named subagents drift
    from established conventions (frontmatter shape, tool-selection discipline,
    prompt structure). Pinning section names prevents the guide itself from
    rotting.
    Rule reference: META-3.
    """
    authoring = AGENT_DIR / "AUTHORING.md"
    assert authoring.exists(), "agents/AUTHORING.md not found"
    text = authoring.read_text(encoding="utf-8")
    # Pin canonical section headers / phrases that should not drift away
    assert "Frontmatter spec" in text
    assert "Tool-selection rules" in text
    assert "Prompt structure conventions" in text
    assert "Calibration awareness pattern" in text
    assert "Self-tests are required" in text
    assert "Three patterns for delegating work" in text
