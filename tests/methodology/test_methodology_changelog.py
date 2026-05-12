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


# --- Slice-008 / BC-1 v1.2 entry pinning ---

def test_v_0_23_0_bc_1_v_1_2_entry_present_in_repo_and_installed():
    """methodology-changelog v0.23.0 / BC-1 v1.2 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no BC-1 v1.2 visible). Bidirectional check catches this.

    Rule reference: BC-1 v1.2 (slice-008).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.23.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.23.0 entry"
    )
    assert "BC-1 v1.2" in in_repo, (
        "in-repo methodology-changelog.md missing BC-1 v1.2 rule reference"
    )
    assert "Negative anchors" in in_repo, (
        "in-repo methodology-changelog.md missing Negative anchors field doc"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.23.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.23.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "BC-1 v1.2" in installed, (
        "installed ~/.claude/methodology-changelog.md missing BC-1 v1.2 rule reference"
    )
    assert "Negative anchors" in installed, (
        "installed ~/.claude/methodology-changelog.md missing Negative anchors field doc"
    )


# --- Slice-009 / CCC-1 v1.1 entry pinning ---

def test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.24.0 / CCC-1 v1.1 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no CCC-1 v1.1 visible). Bidirectional check catches this.

    Substantive canonical phrase pinned per Critic M3 at slice-009 (mirrors
    slice-008's `Negative anchors` substantive anchor for v0.23.0 BC-1 v1.2
    entry per N-surface schema-pin discipline): `design.md mechanical tables`
    is the canonical phrase the CCC-1 v1.1 entry MUST contain — reuses the
    same canonical phrase pinned in critique.md AC #1's
    test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables.

    Rule reference: CCC-1 v1.1 (slice-009).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.24.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.24.0 entry"
    )
    assert "CCC-1 v1.1" in in_repo, (
        "in-repo methodology-changelog.md missing CCC-1 v1.1 rule reference"
    )
    assert "design.md mechanical tables" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'design.md mechanical tables' (per Critic M3 N-surface pin discipline)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.24.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.24.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "CCC-1 v1.1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing CCC-1 v1.1 rule reference"
    )
    assert "design.md mechanical tables" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive canonical phrase "
        "'design.md mechanical tables' (per Critic M3 N-surface pin discipline)"
    )


# --- Slice-010 / MCT-1 entry pinning (re-added at slice-011 validation: entry pins persist across version supersessions; only PMI-1 version-gate test supersedes) ---

def test_v_0_25_0_mct_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.25.0 / MCT-1 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no MCT-1 visible). Bidirectional check catches this.

    Substantive canonical phrase pinned per Critic M3 at slice-009 +
    slice-010 N-surface schema-pin discipline: `In-house methodology surfaces`
    is the canonical phrase the MCT-1 entry MUST contain.

    Rule reference: MCT-1 (slice-010).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.25.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.25.0 entry"
    )
    assert "MCT-1" in in_repo, (
        "in-repo methodology-changelog.md missing MCT-1 rule reference"
    )
    assert "In-house methodology surfaces" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'In-house methodology surfaces' (per slice-010 N-surface pin discipline)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.25.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.25.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "MCT-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing MCT-1 rule reference"
    )
    assert "In-house methodology surfaces" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'In-house methodology surfaces' (per slice-010 "
        "N-surface pin discipline)"
    )


# --- Slice-011 / RSAD-1 entry pinning ---

def test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.26.0 / RSAD-1 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no RSAD-1 visible). Bidirectional check catches this.

    Substantive canonical phrase pinned per Critic M3 at slice-009 +
    slice-010 M3 + slice-011 N-surface schema-pin discipline:
    `Recursive self-application discipline` is the canonical phrase the
    RSAD-1 entry MUST contain — reuses the same canonical phrase pinned in
    `test_critique_agent.py` AC #1 row 1
    (`test_critique_dim_9_recursive_self_application_sub_clause_present`).
    ONE canonical phrase pinned across N=3 surfaces: agents/critique.md
    Dim 9 6th sub-clause title + in-repo methodology-changelog.md +
    installed methodology-changelog.md.

    Rule reference: RSAD-1 (slice-011).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.26.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.26.0 entry"
    )
    assert "RSAD-1" in in_repo, (
        "in-repo methodology-changelog.md missing RSAD-1 rule reference"
    )
    assert "Recursive self-application discipline" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'Recursive self-application discipline' (per slice-011 N-surface pin discipline)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.26.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.26.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "RSAD-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing RSAD-1 rule reference"
    )
    assert "Recursive self-application discipline" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'Recursive self-application discipline' (per slice-011 "
        "N-surface pin discipline)"
    )


# --- Slice-012 / BC-PROJ-2 entry pinning ---

def test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed():
    """methodology-changelog v0.27.0 / BC-PROJ-2 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no BC-PROJ-2 migration visible). Bidirectional check
    catches this.

    Substantive canonical phrase pinned per slice-008 M2 + slice-009 M3 +
    slice-010 M3 + slice-011 N-surface schema-pin discipline (N=3 stable;
    slice-012 ratchets to N=4 per /critique m1 ACCEPTED-FIXED):
    `BC-PROJ-2 negative-anchor migration` is the canonical phrase the
    v0.27.0 entry MUST contain — the changelog entry title. 3-pin shape:
    `## v0.27.0` heading + `BC-PROJ-2` rule-ID + canonical phrase
    `BC-PROJ-2 negative-anchor migration` across N=2 surfaces (in-repo +
    installed methodology-changelog).

    Edit discipline (per /critique M1 ACCEPTED-FIXED + slice-011 NEW Dim 9
    sub-class N=1 entry-pin-vs-PMI-1-gate-semantics-conflation): this
    function lives under its OWN `# --- Slice-012 / BC-PROJ-2 entry pinning
    ---` SECTION header above. Entry-pin functions persist across ALL
    versions (v0.22.0 / v0.23.0 / v0.24.0 / v0.25.0 / v0.26.0 functions
    above are NOT touched by slice-012); only PMI-1 versioned-gate tests
    supersede latest-only. The N=2 promotion probe for the entry-pin-vs-
    PMI-1-gate-conflation Dim 9 sub-class candidate is whether slice-012
    ships clean — N=1 ratchets to N=2 if the v0.26.0 RSAD-1 entry-pin
    function above remains intact at slice-end.

    Rule reference: BC-1 v1.3 (slice-012 AC #5 row 1).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.27.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.27.0 entry"
    )
    assert "BC-PROJ-2" in in_repo, (
        "in-repo methodology-changelog.md missing BC-PROJ-2 rule reference"
    )
    assert "BC-PROJ-2 negative-anchor migration" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'BC-PROJ-2 negative-anchor migration' (per /critique m1 ACCEPTED-FIXED "
        "N-surface schema-pin discipline; slice-012 ratchets N=3 -> N=4)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.27.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.27.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "BC-PROJ-2" in installed, (
        "installed ~/.claude/methodology-changelog.md missing BC-PROJ-2 rule reference"
    )
    assert "BC-PROJ-2 negative-anchor migration" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'BC-PROJ-2 negative-anchor migration' (per /critique "
        "m1 ACCEPTED-FIXED N-surface pin discipline)"
    )


# --- PMI-1 cleanliness gate at v0.27.0 (supersedes _at_0_26_0 per slice-007/008/009/010/011 N=4 supersession pattern; slice-012 ratchets to N=5 supersession events) ---

def test_plugin_yaml_version_matches_version_file_at_0_27_0():
    """plugin.yaml.version == VERSION file content == '0.27.0' post-build.

    Defect class (per slice-006 B1 escape, slice-007 PMI-1 closure pattern):
    PMI-1 invariant requires `plugin.yaml.version` and the in-repo `VERSION`
    file to bump atomically. Slice-012 bumps both from '0.26.0' → '0.27.0'.
    Without this gate, an out-of-band /reflect or commit could leave the
    plugin.yaml lagging (the slice-006 escape recurrence pattern).

    Per slice-007 + slice-008 + slice-009 + slice-010 + slice-011 PMI-1
    versioned-gate supersession pattern (slice-007 introduced `_at_0_22_0`;
    slice-008 first-superseded with `_at_0_23_0`; slice-009 second-superseded
    with `_at_0_24_0`; slice-010 third-superseded with `_at_0_25_0`;
    slice-011 fourth-superseded with `_at_0_26_0` = N=4 supersession events
    post-slice-011). Slice-012 ratchets to N=5 supersession events on
    completion. No two version-gates coexist — `_at_0_26_0` is deleted
    in the same commit as this `_at_0_27_0` is added.

    Edit discipline (per /critique M1 ACCEPTED-FIXED + slice-011 NEW Dim 9
    sub-class N=1 entry-pin-vs-PMI-1-gate-semantics-conflation): this
    function lives under its OWN `# --- PMI-1 cleanliness gate at v0.27.0 ---`
    SECTION header above — separate from any entry-pin function's
    `# --- Slice-NNN / RULE entry pinning ---` SECTION header. The
    supersession Edit at slice-012 narrow-scoped to ONLY this function's
    body + its dedicated SECTION header, NEVER spanning any entry-pin
    function above. Entry-pin functions for v0.22.0..v0.26.0 persist
    untouched per the N=2 promotion-threshold probe of the slice-011
    sub-class candidate.

    Rule reference: PMI-1 invariant (slice-012 atomic bump).
    """
    version_file = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    plugin_manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    plugin_version = plugin_manifest["version"]

    assert version_file == "0.27.0", (
        f"VERSION file content is {version_file!r}, expected '0.27.0'. "
        f"Slice-012 must bump from 0.26.0 → 0.27.0."
    )
    assert plugin_version == "0.27.0", (
        f"plugin.yaml.version is {plugin_version!r}, expected '0.27.0'. "
        f"Slice-012 must bump atomically with VERSION."
    )
    assert version_file == plugin_version, (
        f"PMI-1 mismatch: VERSION={version_file!r} != plugin.yaml.version="
        f"{plugin_version!r}. The slice-006 PMI-1 escape recurred."
    )
