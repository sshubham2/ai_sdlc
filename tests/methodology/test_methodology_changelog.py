"""Validate the methodology-changelog itself: format, version sync, dated entries."""
import ast
import re
from pathlib import Path

import pytest
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


# --- Slice-013 / EPGD-1 entry pinning ---

def test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.28.0 / EPGD-1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no EPGD-1 discipline visible to /status).

    Substantive canonical phrase pinned per slice-011 RSAD-1 3-surface
    schema-pin precedent (N=2 instances stable at slice-013: RSAD-1 +
    EPGD-1): `Entry-pin-vs-PMI-1-gate semantics conflation` is the
    canonical phrase pinned across N=3 surfaces — (1) agents/critique.md
    Dim 9 7th sub-clause title + (2) in-repo methodology-changelog.md
    v0.28.0 entry + (3) installed methodology-changelog.md v0.28.0 entry.
    3-pin shape: `## v0.28.0` heading + `EPGD-1` rule-ID + canonical
    phrase across both bidirectional surfaces of the changelog.

    Edit discipline (per slice-011 NEW Dim 9 sub-class N=1 + slice-012 N=2
    promotion-threshold-met entry-pin-vs-PMI-1-gate-semantics-conflation,
    codified at slice-013 as EPGD-1): this function lives under its OWN
    `# --- Slice-013 / EPGD-1 entry pinning ---` SECTION header above —
    structurally separate from the PMI-1 versioned-gate's own SECTION
    header below. Entry-pin functions persist across ALL versions
    (v0.22.0..v0.27.0 entry-pin functions above are NOT touched by
    slice-013); only PMI-1 versioned-gate tests supersede latest-only.
    The N=2 ratchet promotion-threshold-met at slice-012 is confirmed
    empirically at slice-013 if all v0.22.0..v0.27.0 entry-pin functions
    remain intact at slice-end (canonical reference instance of EPGD-1
    self-application; RSAD-1 self-application N=5 cumulative).

    Rule reference: EPGD-1 (slice-013 AC #4).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.28.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.28.0 entry"
    )
    assert "EPGD-1" in in_repo, (
        "in-repo methodology-changelog.md missing EPGD-1 rule reference"
    )
    assert "Entry-pin-vs-PMI-1-gate semantics conflation" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'Entry-pin-vs-PMI-1-gate semantics conflation' (per slice-011 RSAD-1 "
        "3-surface schema-pin precedent; N=2 instances stable at slice-013)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.28.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.28.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "EPGD-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing EPGD-1 rule reference"
    )
    assert "Entry-pin-vs-PMI-1-gate semantics conflation" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'Entry-pin-vs-PMI-1-gate semantics conflation' "
        "(per slice-011 RSAD-1 3-surface schema-pin precedent)"
    )


# --- Slice-014 / PMI-1 v1.1 entry pinning ---

def test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.29.0 / PMI-1 v1.1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no PMI-1 v1.1 refactor visible to /status).

    Substantive canonical phrase pinned per slice-011 RSAD-1 + slice-013
    EPGD-1 3-surface schema-pin precedent (N=2 instances stable at
    slice-013 -> N=3 stable at slice-014): the canonical phrase
    `version-agnostic PMI-1 cleanliness gate` is pinned across N=3
    surfaces — (1) ADR-013 title + body + (2) in-repo methodology-changelog
    v0.29.0 entry + (3) installed methodology-changelog v0.29.0 entry.
    3-pin shape: `## v0.29.0` heading + `PMI-1 v1.1` rule-ID + canonical
    phrase across both bidirectional surfaces of the changelog.

    Edit discipline (per slice-013 EPGD-1 Dim 9 7th sub-clause): this
    function lives under its OWN `# --- Slice-014 / PMI-1 v1.1 entry
    pinning ---` SECTION header above — structurally separate from any
    PMI-1 gate SECTION header. Entry-pin functions persist across ALL
    versions (v0.22.0..v0.28.0 entry-pin functions above are NOT touched
    by slice-014); only PMI-1 versioned-gate tests supersede latest-only
    — and at slice-014 the versioned-gate supersession pattern itself is
    RETIRED (see test_plugin_yaml_version_matches_version_file_invariant
    below + methodology-changelog v0.29.0 entry).

    Rule reference: PMI-1 v1.1 (slice-014 AC #4).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.29.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.29.0 entry"
    )
    assert "PMI-1 v1.1" in in_repo, (
        "in-repo methodology-changelog.md missing PMI-1 v1.1 rule reference"
    )
    assert "version-agnostic PMI-1 cleanliness gate" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'version-agnostic PMI-1 cleanliness gate' (per slice-013 EPGD-1 "
        "3-surface schema-pin precedent; slice-014 ratchets N=2 -> N=3 instances stable)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.29.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.29.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "PMI-1 v1.1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing PMI-1 v1.1 rule reference"
    )
    assert "version-agnostic PMI-1 cleanliness gate" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'version-agnostic PMI-1 cleanliness gate' "
        "(per slice-013 EPGD-1 3-surface schema-pin precedent)"
    )


def test_v_0_29_0_entry_names_supersession_pattern_retired():
    """methodology-changelog v0.29.0 entry MUST contain the canonical phrase
    `supersession pattern retired at slice-014` in BOTH in-repo + installed
    surfaces.

    Defect class (slice-014-specific): the PMI-1 versioned-gate supersession
    counter ran at N=6 events stable across slices 007-013 (slice-007
    introduced _at_0_22_0; slices 008-013 superseded sequentially). At
    slice-014 the pattern is retired: future slices' version bumps do NOT
    supersede the gate function. The v0.29.0 changelog entry MUST annotate
    this termination explicitly so future readers + /status + /critique
    + /critic-calibrate distinguish "this is the LAST slice in the pattern"
    from "this is yet another supersession slice".

    Distinct from the canonical-phrase 3-pin (heading + rule-ID + phrase
    `version-agnostic PMI-1 cleanliness gate`) tested above; this pins a
    DIFFERENT canonical phrase carrying the supersession-retirement
    annotation.

    Rule reference: PMI-1 v1.1 (slice-014 AC #4) + N=6 versioned-gate
    supersession counter termination.
    """
    in_repo = read_file("methodology-changelog.md")
    assert "supersession pattern retired at slice-014" in in_repo, (
        "in-repo methodology-changelog.md v0.29.0 entry missing canonical "
        "phrase 'supersession pattern retired at slice-014' — annotation "
        "of N=6 PMI-1 versioned-gate supersession counter termination is "
        "missing"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    installed = installed_path.read_text(encoding="utf-8")
    assert "supersession pattern retired at slice-014" in installed, (
        "installed ~/.claude/methodology-changelog.md v0.29.0 entry missing "
        "canonical phrase 'supersession pattern retired at slice-014' — "
        "forward-sync after in-repo edit forgot the supersession-retirement "
        "annotation"
    )


# --- PMI-1 cleanliness gate (version-agnostic, slice-014 refactor; PMI-1 v1.1 per methodology-changelog.md v0.29.0) ---

def test_plugin_yaml_version_matches_version_file_invariant():
    """VERSION file content == plugin.yaml.version (PMI-1 v1.1 invariant).

    Defect class (per slice-006 B1 escape, slice-007 PMI-1 closure pattern):
    PMI-1 invariant requires `plugin.yaml.version` and the in-repo `VERSION`
    file to bump atomically. Without this gate, an out-of-band /reflect or
    commit could leave one file lagging — the slice-006 escape recurrence
    pattern.

    Version-agnostic shape (PMI-1 v1.1 per slice-014 refactor): no hardcoded
    version literal. The cross-file equality invariant IS the defect class
    this gate exists to catch. The "did you bump at all?" discipline is
    carried by per-version entry-pin tests (test_v_0_NN_0_*) + each slice's
    mission-brief atomic-bump checklist + META-1
    (test_version_matches_most_recent_changelog_entry). See
    methodology-changelog.md v0.29.0 + ADR-013 for the supersession pattern
    retirement rationale.

    Rule reference: PMI-1 v1.1 (slice-014 atomic bump + version-agnostic
    gate refactor).
    """
    version_file = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    plugin_manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    plugin_version = plugin_manifest["version"]

    assert version_file == plugin_version, (
        f"PMI-1 mismatch: VERSION={version_file!r} != "
        f"plugin.yaml.version={plugin_version!r}. The slice-006 escape "
        f"recurred — atomic bump discipline broken."
    )


# --- PMI-1 v1.1 structural meta-tests (slice-014) ---

def test_pmi_1_gate_function_is_version_agnostic_shape():
    """AST-walk test_methodology_changelog.py's module, locate the
    test_plugin_yaml_version_matches_version_file_invariant FunctionDef,
    walk its body for any Constant(value=str) matching
    r"^\\d+\\.\\d+\\.\\d+$", assert NONE found.

    Defect class (slice-014-specific): a future regression could smuggle
    a version literal back into the gate function's body (e.g., by adding
    an "extra safety" assertion like `assert version_file == "0.29.0"`).
    This AST meta-test pins the version-agnostic shape against that class
    of regression — structural defense at the AST level, robust against
    prose rephrasing.

    Rule reference: PMI-1 v1.1 (slice-014 AC #1 — version-agnostic gate
    function structural invariant).
    """
    source = (REPO_ROOT / "tests" / "methodology" / "test_methodology_changelog.py").read_text(encoding="utf-8")
    module = ast.parse(source)

    gate_fn = None
    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef) and node.name == "test_plugin_yaml_version_matches_version_file_invariant":
            gate_fn = node
            break
    assert gate_fn is not None, (
        "PMI-1 v1.1 gate function "
        "test_plugin_yaml_version_matches_version_file_invariant not found "
        "in tests/methodology/test_methodology_changelog.py"
    )

    version_literal_re = re.compile(r"^\d+\.\d+\.\d+$")
    smuggled_literals = []
    for node in ast.walk(gate_fn):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if version_literal_re.match(node.value):
                smuggled_literals.append((node.value, node.lineno))

    assert smuggled_literals == [], (
        f"PMI-1 v1.1 gate function contains version-literal Constant(s) "
        f"matching r'^\\d+\\.\\d+\\.\\d+$' (version-agnostic shape "
        f"violated): {smuggled_literals!r}. The slice-014 refactor's "
        f"structural invariant is broken — a future regression smuggled "
        f"a version literal back into the gate body."
    )


def test_no_per_version_pmi_1_gate_functions_remain():
    """AST-walk test_methodology_changelog.py's module, locate any
    FunctionDef.name matching
    r"^test_plugin_yaml_version_matches_version_file_at_0_\\d+_0$",
    assert the list is EMPTY.

    Defect class (slice-014-specific): a future regression could re-introduce
    the per-version PMI-1 gate shape (e.g., test_..._at_0_30_0). This AST
    meta-test pins the slice-014 deletion of all _at_0_NN_0-shaped gate
    functions against that class of regression — structural counter-anchor
    to the legacy shape.

    Rule reference: PMI-1 v1.1 (slice-014 AC #3 — legacy _at_0_NN_0
    shape deletion).
    """
    source = (REPO_ROOT / "tests" / "methodology" / "test_methodology_changelog.py").read_text(encoding="utf-8")
    module = ast.parse(source)

    legacy_pattern = re.compile(r"^test_plugin_yaml_version_matches_version_file_at_0_\d+_0$")
    legacy_funcs = []
    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef) and legacy_pattern.match(node.name):
            legacy_funcs.append((node.name, node.lineno))

    assert legacy_funcs == [], (
        f"Per-version PMI-1 gate function(s) still present (slice-014 "
        f"deletion incomplete): {legacy_funcs!r}. The slice-014 refactor "
        f"requires ALL test_plugin_yaml_version_matches_version_file_at_0_NN_0 "
        f"functions to be deleted; only "
        f"test_plugin_yaml_version_matches_version_file_invariant remains."
    )


# --- PMI-1 v1.1 regression test (slice-014) ---

def test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge(tmp_path, monkeypatch):
    """Regression test: gate fires with pinned error message when
    VERSION != plugin.yaml.version.

    Defect class (per slice-007 PMI-1 closure pattern + slice-014 v1.1
    refactor): the version-agnostic gate's correctness depends on its
    ability to FIRE when the cross-file equality is broken. This
    regression test exercises the FAILURE path with tempdir + monkeypatch.

    Monkeypatch target name-resolution semantics (per slice-014 /critique
    M2 ACCEPTED-FIXED): the bare `REPO_ROOT` reference inside the gate
    function resolves from test_methodology_changelog's module globals
    (where REPO_ROOT was imported from tests.methodology.conftest at
    module top). Patching
    `tests.methodology.test_methodology_changelog.REPO_ROOT` (NOT the
    `conftest` original) is correct. Patching `conftest.REPO_ROOT` would
    silently no-op — gate would still read real VERSION/plugin.yaml files
    (both at slice's current version), match, AssertionError NOT raised,
    `pytest.raises` raises DID NOT RAISE, test fails for wrong reason.

    Rule reference: PMI-1 v1.1 (slice-014 atomic bump + version-agnostic
    gate refactor), AC #2 regression coverage.
    """
    (tmp_path / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    (tmp_path / "plugin.yaml").write_text("version: 4.5.6\n", encoding="utf-8")

    # Patch via the object form anchored on the running module's actual
    # sys.modules entry (slice-014 build-time DEVIATION-1): pytest's
    # discovery under a `tests/` namespace package (no __init__.py)
    # places this module in sys.modules under `methodology.test_methodology_changelog`
    # (the bare key), NOT under the fully-qualified
    # `tests.methodology.test_methodology_changelog` dotted path. A
    # monkeypatch with the dotted-string target would patch a SEPARATE
    # importlib-fetched copy of the module, leaving the running test's
    # REPO_ROOT untouched and the gate reading real VERSION/plugin.yaml
    # files (DID NOT RAISE). Using sys.modules[__name__] anchors the
    # patch on the running module regardless of pytest's import-mode key
    # choice — same fix-class as the VAL-1 Layer B `tests` namespace
    # package issue (N=11 cumulative recurrence pre-slice-014).
    import sys
    monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)

    with pytest.raises(AssertionError) as excinfo:
        test_plugin_yaml_version_matches_version_file_invariant()

    assert "PMI-1" in str(excinfo.value), (
        f"regression error message missing 'PMI-1' substring: "
        f"{str(excinfo.value)!r}"
    )
    assert "slice-006 escape" in str(excinfo.value), (
        f"regression error message missing 'slice-006 escape' substring: "
        f"{str(excinfo.value)!r}"
    )


# --- ADR-013 pin (slice-014) ---

def test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase():
    """architecture/decisions/ADR-013-*.md must exist AND contain the
    canonical phrase `version-agnostic PMI-1 cleanliness gate`.

    Defect class (slice-014-specific): the v0.29.0 changelog entry +
    ADR-013 + 3-surface canonical-phrase pin discipline requires the ADR
    artifact to carry the canonical phrase as one of the 3 surfaces
    (other 2: in-repo + installed methodology-changelog). If ADR-013 is
    missing or doesn't contain the canonical phrase, the N-surface
    schema-pin (N=3 stable post-slice-014) breaks.

    Rule reference: PMI-1 v1.1 (slice-014 AC #4 — ADR-013 surface of
    3-surface canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-013-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-013 file at "
        f"architecture/decisions/ADR-013-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "version-agnostic PMI-1 cleanliness gate" in adr_content, (
        f"ADR-013 ({adr_files[0].name}) missing canonical phrase "
        f"'version-agnostic PMI-1 cleanliness gate' — N-surface schema-pin "
        f"(N=3 stable post-slice-014: ADR-013 + in-repo + installed "
        f"methodology-changelog) is broken at the ADR-013 surface"
    )


# --- Slice-015 / SCPD-1 entry pinning ---

def test_v_0_30_0_scpd_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.30.0 / SCPD-1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no SCPD-1 codification visible to /status).

    Substantive canonical phrase pinned per slice-011 RSAD-1 + slice-013
    EPGD-1 + slice-014 PMI-1 v1.1 3-surface schema-pin precedent
    (N=3 instances stable at slice-014 -> N=4 stable at slice-015): the
    canonical phrase `Shippability-catalog consumer-reference propagation`
    is pinned across N=3 surfaces — (1) agents/critique.md Dim 9 8th
    sub-clause title + (2) in-repo methodology-changelog v0.30.0 entry +
    (3) installed methodology-changelog v0.30.0 entry. 3-pin shape:
    `## v0.30.0` heading + `SCPD-1` rule-ID + canonical phrase across
    both bidirectional surfaces of the changelog.

    Edit discipline (per slice-013 EPGD-1 Dim 9 7th sub-clause): this
    function lives under its OWN `# --- Slice-015 / SCPD-1 entry pinning
    ---` SECTION header above — structurally separate from any PMI-1
    gate SECTION header. Entry-pin functions persist across ALL versions
    (v0.22.0..v0.29.0 entry-pin functions above are NOT touched by
    slice-015); under PMI-1 v1.1 (slice-014) the versioned-gate
    supersession pattern is RETIRED so slice-015 ADDS only — no Edit on
    any pre-existing entry-pin or gate function.

    Rule reference: SCPD-1 (slice-015 AC #3).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.30.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.30.0 entry"
    )
    assert "SCPD-1" in in_repo, (
        "in-repo methodology-changelog.md missing SCPD-1 rule reference"
    )
    assert "Shippability-catalog consumer-reference propagation" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'Shippability-catalog consumer-reference propagation' (per slice-013 "
        "EPGD-1 3-surface schema-pin precedent; slice-015 ratchets N=3 -> N=4 "
        "instances stable)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.30.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.30.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "SCPD-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing SCPD-1 rule reference"
    )
    assert "Shippability-catalog consumer-reference propagation" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'Shippability-catalog consumer-reference propagation' "
        "(per slice-013 EPGD-1 3-surface schema-pin precedent)"
    )


# --- ADR-014 pin (slice-015) ---

def test_adr_014_exists_and_names_scpd_1_canonical_phrase():
    """ADR-014 must exist at architecture/decisions/ADR-014-*.md AND contain
    the canonical phrase `Shippability-catalog consumer-reference propagation`.

    Defect class (per slice-014 ADR-013 pin precedent): the ADR is the
    third surface of the N-surface schema-pin (3-surface shape:
    ADR-014 + in-repo methodology-changelog v0.30.0 + installed
    methodology-changelog v0.30.0). If the ADR file is missing or
    doesn't contain the canonical phrase, the N-surface schema-pin
    (N=4 stable post-slice-015) breaks.

    Rule reference: SCPD-1 (slice-015 AC #4 — ADR-014 surface of
    3-surface canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-014-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-014 file at "
        f"architecture/decisions/ADR-014-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "Shippability-catalog consumer-reference propagation" in adr_content, (
        f"ADR-014 ({adr_files[0].name}) missing canonical phrase "
        f"'Shippability-catalog consumer-reference propagation' — N-surface "
        f"schema-pin (N=4 stable post-slice-015: ADR-014 + in-repo + installed "
        f"methodology-changelog) is broken at the ADR-014 surface"
    )
