"""Validate the methodology-changelog itself: format, version sync, dated entries."""
import re
from pathlib import Path

import yaml

from tests.methodology.conftest import REPO_ROOT, read_file


def test_version_file_is_semver():
    """VERSION must contain a semver-shaped string.

    Defect class: Non-semver versions (e.g., "next" or "latest") break
    /status surfacing and downstream tooling that parses the file.
    Rule reference: META-1.
    """
    version = read_file("VERSION").strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:-[\w.]+)?", version), \
        f"VERSION not semver-shaped: {version!r}"


def test_changelog_has_at_least_one_dated_entry():
    """methodology-changelog.md must have at least one dated entry.

    Defect class: Empty or unstructured changelog provides no audit trail.
    Rule reference: META-1.
    """
    changelog = read_file("methodology-changelog.md")
    match = re.search(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, re.MULTILINE)
    assert match, "No dated `## v<version> — YYYY-MM-DD` entry found"


def test_version_matches_most_recent_changelog_entry():
    """VERSION must match the most-recent changelog entry's version.

    Defect class: Drift between VERSION and changelog headers means /status
    surfaces stale info. The match is the canonical truth check.
    Rule reference: META-1.
    """
    version = read_file("VERSION").strip()
    changelog = read_file("methodology-changelog.md")
    # Find first (most recent — descending order convention) `## v<version> — <date>` heading
    match = re.search(r"^## v(\S+) — \d{4}-\d{2}-\d{2}", changelog, re.MULTILINE)
    assert match, "No dated entry to compare against"
    most_recent = match.group(1)
    assert version == most_recent, (
        f"VERSION ({version}) does not match most recent changelog entry "
        f"({most_recent}). Either bump VERSION or add a new changelog entry."
    )


def test_each_changelog_entry_carries_rule_reference():
    """Every entry's Added/Changed/Retired bullet should carry a Rule reference.

    Defect class: Entries without rule references break cross-linking from
    SKILL.md prose and from later supersession entries.
    Rule reference: META-1.
    """
    changelog = read_file("methodology-changelog.md")
    # Find each `## v...` block and check it has at least one **Rule reference**:
    sections = re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)
    # First split element is preamble; remaining are entry bodies
    for i, body in enumerate(sections[1:], start=1):
        # Stop at next ## heading (already split, so just check this body)
        # An entry must reference at least one rule
        assert "Rule reference" in body or "rule reference" in body.lower(), (
            f"Changelog entry #{i} has no `Rule reference` line. "
            f"Each entry must cite at least one rule ID."
        )


# --- Slice-007 / CAD-1 entry pinning (AC #4) ---

def test_v_0_22_0_cad_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.22.0 / CAD-1 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1): if the entry exists
    only in-repo and the forward-sync was forgotten, every future
    /critic-calibrate run on the installed copy reads stale methodology
    (no CAD-1 visible). The bidirectional check catches this directly.

    Rule reference: CAD-1, AC #4.
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.22.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.22.0 entry"
    )
    assert "CAD-1" in in_repo, (
        "in-repo methodology-changelog.md missing CAD-1 rule reference"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.22.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.22.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "CAD-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing CAD-1 rule reference"
    )


# --- AC #5: PMI-1 cleanliness (closes slice-006 escape) ---

def test_plugin_yaml_version_matches_version_file_at_0_22_0():
    """plugin.yaml.version == VERSION file content == '0.22.0' post-build.

    Defect class (per Critic B2): slice-006 left a PMI-1 escape — plugin.yaml
    version was '0.20.0' while VERSION was '0.21.0'. The slice's design
    promised the bump from '0.21.0' → '0.22.0' would close the escape, but
    no AC gated it pre-Critic. This test is the gate.

    Rule reference: CAD-1, AC #5 (closes slice-006 PMI-1 escape).
    """
    version_file = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    plugin_manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    plugin_version = plugin_manifest["version"]

    assert version_file == "0.22.0", (
        f"VERSION file content is {version_file!r}, expected '0.22.0'. "
        f"Slice-007 must bump from 0.21.0 → 0.22.0."
    )
    assert plugin_version == "0.22.0", (
        f"plugin.yaml.version is {plugin_version!r}, expected '0.22.0'. "
        f"Slice-007 must bump from 0.20.0 (slice-006 escape) → 0.22.0 "
        f"atomically with VERSION."
    )
    assert version_file == plugin_version, (
        f"PMI-1 mismatch: VERSION={version_file!r} != plugin.yaml.version="
        f"{plugin_version!r}. The slice-006 escape recurred."
    )
