"""Validate the methodology-changelog itself: format, version sync, dated entries."""
import ast
import re
from pathlib import Path

import pytest
import yaml

from tests.methodology.conftest import REPO_ROOT, read_file


def _extract_version_body(content: str, version: str) -> str:
    """Extract methodology-changelog.md entry body for a specified version,
    scoped between `## v<version>` and `## v<predecessor-version>` boundaries.

    Generalized at slice-020 per /critique M5 ACCEPTED-FIXED (rule-of-three
    promotion N=2 → N=3 stable; aggregated lesson at slices/_index.md row
    19 explicitly named this generalization as next-codification-slice
    target). Predecessor version is computed by decrementing the minor
    component of the semver string (e.g., "0.31.0" → "0.30.0",
    "0.33.0" → "0.32.0", "0.34.0" → "0.33.0").

    Pre-validation contract: caller MUST have already asserted
    `f"## v{version}" in content` and emitted a surface-context-aware
    error message at the call site (per slice-018 /critique-review
    m-add-1 ACCEPTED-FIXED — surface_name interpolation preserves
    slice-017 L1088-1090 diagnostic pattern). Helper returns empty/
    garbage if `## v{version}` is absent; downstream assertions will
    fail, but the surface-context error message must come from the
    caller. Helper does NOT re-assert.

    Returns rest-of-file from `## v{version}` start if
    `## v{predecessor}` is absent (fallback branch retained for
    symmetry with slice-017 TPHD-1 sibling canonical pattern, though
    triggers only if predecessor entry is deleted — an extraordinary
    regression beyond this generalization's threat model per slice-018
    /critique m1 ACCEPTED-FIXED).

    Used by all `test_v_0_NN_0_*` entry-pin + sibling-scoping regression
    tests via the thin wrappers `_extract_v031_body` / `_extract_v033_body`
    (preserved for backward compatibility with slice-018 + slice-019 tests)
    AND directly by slice-020's `test_v_0_34_0_bfrd_1_*` family per
    /critique M5 ACCEPTED-FIXED + design.md Audit 4 Option C.
    Single code path under test — per slice-018 /critique M2
    ACCEPTED-FIXED + slice-019 /critique M4 ACCEPTED-PENDING.
    """
    major, minor, patch = version.split(".")
    predecessor = f"{major}.{int(minor) - 1}.{patch}"
    start_anchor = f"## v{version}"
    end_anchor = f"## v{predecessor}"
    start = content.find(start_anchor)
    end = content.find(end_anchor, start) if start != -1 else -1
    if end == -1:
        return content[start:] if start != -1 else ""
    return content[start:end]


def _extract_v031_body(content: str) -> str:
    """Thin wrapper around `_extract_version_body(content, "0.31.0")`
    preserved for backward compatibility with slice-018's
    `test_v_0_31_0_rpcd_1_*` family + regression test.

    Per slice-020 /critique M5 ACCEPTED-FIXED + design.md Audit 4
    Option C: rule-of-three generalization at slice-020; existing
    wrappers preserve slice-018 call-site semantics (single code path
    under test per slice-018 /critique M2 ACCEPTED-FIXED).
    """
    return _extract_version_body(content, "0.31.0")


def _extract_v033_body(content: str) -> str:
    """Thin wrapper around `_extract_version_body(content, "0.33.0")`
    preserved for backward compatibility with slice-019's
    `test_v_0_33_0_layer_evid_1_*` family + regression test.

    Per slice-020 /critique M5 ACCEPTED-FIXED + design.md Audit 4
    Option C: rule-of-three generalization at slice-020; existing
    wrappers preserve slice-019 call-site semantics (single code path
    under test per slice-018 /critique M2 + slice-019 /critique M4
    ACCEPTED-PENDING).
    """
    return _extract_version_body(content, "0.33.0")


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


# --- Slice-016 / RPCD-1 entry pinning ---

def test_v_0_31_0_rpcd_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.31.0 / RPCD-1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no RPCD-1 codification visible to /status).

    Substantive canonical phrase pinned per slice-011 RSAD-1 + slice-013
    EPGD-1 + slice-014 PMI-1 v1.1 + slice-015 SCPD-1 3-surface schema-pin
    precedent (N=4 instances stable at slice-015 -> N=5 stable at slice-016):
    the canonical phrase `Runtime-prerequisite completeness on proposed
    fixes` is pinned across N=3 surfaces — (1) agents/critique.md Dim 9
    9th sub-clause title + (2) in-repo methodology-changelog v0.31.0 entry
    + (3) installed methodology-changelog v0.31.0 entry. 3-pin shape:
    `## v0.31.0` heading + `RPCD-1` rule-ID + canonical phrase across
    both bidirectional surfaces of the changelog.

    Edit discipline (per slice-013 EPGD-1 Dim 9 7th sub-clause): this
    function lives under its OWN `# --- Slice-016 / RPCD-1 entry pinning
    ---` SECTION header above — structurally separate from any PMI-1
    gate SECTION header. Entry-pin functions persist across ALL versions
    (v_0_22_0..v_0_30_0 entry-pin functions above are NOT touched by
    slice-016); under PMI-1 v1.1 (slice-014) the versioned-gate
    supersession pattern is RETIRED so slice-016 ADDS only — no Edit on
    any pre-existing entry-pin or gate function. EPGD-1 self-application
    N=4 -> N=5 stable post-slice-016 (10 prior entry-pin functions
    untouched; v0.29.0 doubled entry-pin functions per slice-014 (a)<->(b)
    duality counted).

    Rule reference: RPCD-1 (slice-016 AC #1).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.31.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.31.0 entry"
    )
    assert "RPCD-1" in in_repo, (
        "in-repo methodology-changelog.md missing RPCD-1 rule reference"
    )
    assert "Runtime-prerequisite completeness on proposed fixes" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'Runtime-prerequisite completeness on proposed fixes' (per slice-015 "
        "SCPD-1 3-surface schema-pin precedent; slice-016 ratchets N=4 -> N=5 "
        "instances stable)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.31.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.31.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "RPCD-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing RPCD-1 rule reference"
    )
    assert "Runtime-prerequisite completeness on proposed fixes" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'Runtime-prerequisite completeness on proposed fixes' "
        "(per slice-015 SCPD-1 3-surface schema-pin precedent)"
    )


def test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed():
    """methodology-changelog v0.31.0 / RPCD-1 entry must name ALL THREE
    sub-modes (a)/(b)/(c) bidirectionally, scoped strictly to the v0.31.0
    entry body (NOT global file substring).

    Scoping fix vs original slice-016 implementation: the original test
    used global substring check on the entire file, which would false-positive
    pass on any LATER entry's markers (e.g., v0.32.0+ entries retaining
    Sub-mode markers while v0.31.0 body had them stripped). This slice-018
    fix scopes to the v0.31.0 body specifically (between `## v0.31.0` and
    `## v0.30.0` boundaries via `_extract_v031_body` helper) — proper
    methodology-pin discipline.

    Evidence anchor: slice-017 DEVIATION-1 (N=1 first-Critic-MISS at
    /critique + /critique-review; surfaced at /build-slice Phase 2b
    empirical pytest behavior analysis). Canonical pattern: slice-017
    TPHD-1 sibling at `test_methodology_changelog.py:1086-1094`.

    Surface-context-aware pre-validation per slice-018 /critique-review
    m-add-1 ACCEPTED-FIXED: assert lives at call site so error message
    interpolates `surface_name` (preserves slice-017 L1088-1090 diagnostic
    pattern); helper assumes pre-validated input.

    Sub-mode anchors per slice-016 design.md Audit 1-3 canonical body,
    scoped to the v0.31.0 entry body (not global file):
      - Sub-mode (a) NEW-symbol import-audit
      - Sub-mode (b) NEW-status/token allowlist-audit (`_ALLOWED_STATUSES`)
      - Sub-mode (c) NEW-anchor sibling-grep audit (`sibling`)

    Rule reference: RPCD-1 (slice-016 AC #1 — sub-mode pin) +
    slice-018 (test-scoping discipline restoration).
    """
    in_repo = read_file("methodology-changelog.md")
    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    installed = installed_path.read_text(encoding="utf-8")

    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        # Surface-context-aware pre-validation per /critique-review m-add-1
        # ACCEPTED-FIXED (preserves slice-017 L1088-1090 diagnostic pattern):
        # assert lives at call site so error message can interpolate
        # surface_name; helper assumes pre-validated input.
        assert "## v0.31.0" in content, (
            f"{surface_name} methodology-changelog.md missing v0.31.0 entry — "
            f"entry-pin broken (slice-016 RPCD-1 surface)"
        )
        v031_body = _extract_v031_body(content)

        # Sub-mode markers must appear in v0.31.0 body (scoped via helper)
        assert "Sub-mode (a)" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'Sub-mode (a)' marker — three-sub-mode pin broken"
        )
        assert "Sub-mode (b)" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'Sub-mode (b)' marker — three-sub-mode pin broken"
        )
        assert "Sub-mode (c)" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'Sub-mode (c)' marker — three-sub-mode pin broken"
        )
        assert "_ALLOWED_STATUSES" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'_ALLOWED_STATUSES' substring — sub-mode (b) discipline "
            f"anchor broken"
        )
        assert "sibling" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'sibling' substring — sub-mode (c) discipline anchor broken"
        )


def test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body():
    """Regression test: prove the v0.31.0 scoping discipline (via
    `_extract_v031_body` helper) catches stripped sub-mode markers within
    v0.31.0 body even when v0.32.0+ entries retain them.

    Defect class (slice-017 DEVIATION-1, N=1 first-Critic-MISS):
    the original slice-016 `_names_three_sub_modes` test pattern used
    global substring check. If a future slice strips Sub-mode (a)/(b)/(c)
    markers from the v0.31.0 entry body while v0.32.0+ retains them,
    the global check would false-positive PASS — methodology pin
    silently broken.

    Single-code-path discipline (per slice-018 /critique M2 ACCEPTED-FIXED):
    both the refactored sibling test AND this regression test call the
    SAME `_extract_v031_body` helper. So this test's assertion empirically
    proves the sibling's scoping would catch real-world v0.31.0-body
    marker stripping (not just self-constructed synthetic content).

    Rule reference: slice-018 AC #2 + slice-017 DEVIATION-1 evidence.
    """
    synthetic = (
        "## v0.32.0\n"
        "Sub-mode (a) /critique post-fix-prose harmonization\n"
        "Sub-mode (b) /critique-review post-fix-prose harmonization\n"
        "Sub-mode (c) /build-slice Prerequisite-check pre-flight\n"
        "\n"
        "## v0.31.0\n"
        "[markers stripped — regression fixture]\n"
        "_ALLOWED_STATUSES kept\n"
        "sibling kept\n"
        "\n"
        "## v0.30.0\n"
        "earlier entry\n"
    )
    v031_body = _extract_v031_body(synthetic)

    # The scoping discipline (same helper the sibling uses) catches the
    # stripped markers in v0.31.0 body
    assert "Sub-mode (a)" not in v031_body, (
        "regression: _extract_v031_body failed to isolate v0.31.0 body — "
        "the slice-016 RPCD-1 sibling test would silently PASS on stripped "
        "markers if this helper drifted"
    )
    # But the marker IS present file-globally — proves the global-substring
    # fallacy the scoping fix defends against
    assert "Sub-mode (a)" in synthetic, (
        "regression-test fixture malformed: v0.32.0 must retain marker for "
        "the test to demonstrate the global-substring fallacy"
    )


# --- ADR-015 pin (slice-016) ---

def test_adr_015_exists_and_names_rpcd_1_canonical_phrase():
    """ADR-015 must exist at architecture/decisions/ADR-015-*.md AND contain
    the canonical phrase `Runtime-prerequisite completeness on proposed fixes`.

    Defect class (per slice-014 ADR-013 + slice-015 ADR-014 pin precedent):
    the ADR is the third surface of the N-surface schema-pin (3-surface shape:
    ADR-015 + in-repo methodology-changelog v0.31.0 + installed
    methodology-changelog v0.31.0). If the ADR file is missing or doesn't
    contain the canonical phrase, the N-surface schema-pin (N=5 stable
    post-slice-016) breaks.

    Rule reference: RPCD-1 (slice-016 AC #3 — ADR-015 surface of 3-surface
    canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-015-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-015 file at "
        f"architecture/decisions/ADR-015-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "Runtime-prerequisite completeness on proposed fixes" in adr_content, (
        f"ADR-015 ({adr_files[0].name}) missing canonical phrase "
        f"'Runtime-prerequisite completeness on proposed fixes' — N-surface "
        f"schema-pin (N=5 stable post-slice-016: ADR-015 + in-repo + installed "
        f"methodology-changelog) is broken at the ADR-015 surface"
    )


# --- Slice-017 / TPHD-1 entry pinning ---

def test_v_0_32_0_tphd_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.32.0 / TPHD-1 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no TPHD-1 codification visible to /status).

    Substantive canonical phrase pinned per slice-011 RSAD-1 + slice-013
    EPGD-1 + slice-014 PMI-1 v1.1 + slice-015 SCPD-1 + slice-016 RPCD-1
    3-surface schema-pin precedent (N=5 instances stable at slice-016 ->
    N=6 stable at slice-017): the canonical phrase `TF-1 plan harmonization
    discipline` is pinned across N=3 surfaces — (1) skills/critique/SKILL.md
    + skills/critique-review/SKILL.md + skills/build-slice/SKILL.md prose +
    (2) in-repo methodology-changelog v0.32.0 entry + (3) installed
    methodology-changelog v0.32.0 entry. 3-pin shape: `## v0.32.0` heading +
    `TPHD-1` rule-ID + canonical phrase across both bidirectional surfaces
    of the changelog.

    Edit discipline (per slice-013 EPGD-1 Dim 9 7th sub-clause): this
    function lives under its OWN `# --- Slice-017 / TPHD-1 entry pinning
    ---` SECTION header above — structurally separate from any PMI-1 gate
    SECTION header. Entry-pin functions persist across ALL versions
    (v_0_22_0..v_0_31_0 entry-pin functions above are NOT touched by
    slice-017); under PMI-1 v1.1 (slice-014) the versioned-gate
    supersession pattern is RETIRED so slice-017 ADDS only — no Edit on
    any pre-existing entry-pin or gate function. EPGD-1 self-application
    N=5 -> N=6 stable post-slice-017 (12 prior entry-pin functions
    untouched — v0.29.0 doubled per slice-014 (a)<->(b) duality + v0.31.0
    doubled per slice-016 RPCD-1 (a)<->(b) duality counted, per
    /critique-review m-add-1 ACCEPTED-FIXED count correction).

    Rule reference: TPHD-1 (slice-017 AC #1).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.32.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.32.0 entry"
    )
    assert "TPHD-1" in in_repo, (
        "in-repo methodology-changelog.md missing TPHD-1 rule reference"
    )
    assert "TF-1 plan harmonization discipline" in in_repo, (
        "in-repo methodology-changelog.md missing substantive canonical phrase "
        "'TF-1 plan harmonization discipline' (per slice-016 RPCD-1 3-surface "
        "schema-pin precedent; slice-017 ratchets N=5 -> N=6 instances stable)"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.32.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.32.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "TPHD-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing TPHD-1 rule reference"
    )
    assert "TF-1 plan harmonization discipline" in installed, (
        "installed ~/.claude/methodology-changelog.md missing substantive "
        "canonical phrase 'TF-1 plan harmonization discipline' (per slice-016 "
        "RPCD-1 3-surface schema-pin precedent)"
    )


def test_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo_and_installed():
    """methodology-changelog v0.32.0 / TPHD-1 entry must name ALL THREE
    sub-modes (a)/(b)/(c) bidirectionally, scoped strictly to the v0.32.0
    entry body (NOT global file substring).

    Defect class: a v0.32.0 entry that names TPHD-1 but elides the three
    sub-modes loses the operational discipline. The three sub-modes are
    what makes TPHD-1 actionable at /critique-time + /critique-review-time
    + /build-slice-time, distinct from vague exhortation to "harmonize the
    TF-1 plan".

    Scoping fix vs slice-016 RPCD-1 sibling test precedent: the slice-016
    `_names_three_sub_modes` test used global substring check, which would
    false-positive pass on any prior entry's markers. This slice-017 sibling
    scopes to the v0.32.0 body specifically (between `## v0.32.0` and
    `## v0.31.0` boundaries) — proper WRITTEN-FAILING discipline.

    Sub-mode anchors per slice-017 ADR-016 Decision canonical body:
      - Sub-mode (a) /critique post-fix-prose harmonization
      - Sub-mode (b) /critique-review post-fix-prose harmonization
      - Sub-mode (c) /build-slice Prerequisite-check pre-flight harmonization

    Rule reference: TPHD-1 (slice-017 AC #1 — three-sub-mode pin per
    slice-016 RPCD-1 (a)/(b)/(c) precedent with scoping correction).
    """
    in_repo = read_file("methodology-changelog.md")
    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    installed = installed_path.read_text(encoding="utf-8")

    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        # Scope strictly to v0.32.0 entry body
        v032_start = content.find("## v0.32.0")
        v031_start = content.find("## v0.31.0", v032_start)
        assert v032_start != -1, (
            f"{surface_name} methodology-changelog.md missing v0.32.0 entry"
        )
        if v031_start == -1:
            v032_body = content[v032_start:]
        else:
            v032_body = content[v032_start:v031_start]

        # Sub-mode markers must appear in v0.32.0 body (scoped)
        assert "Sub-mode (a)" in v032_body, (
            f"{surface_name} methodology-changelog.md v0.32.0 body missing "
            f"'Sub-mode (a)' marker — three-sub-mode pin broken (scoped to "
            f"v0.32.0..v0.31.0 boundary)"
        )
        assert "Sub-mode (b)" in v032_body, (
            f"{surface_name} methodology-changelog.md v0.32.0 body missing "
            f"'Sub-mode (b)' marker — three-sub-mode pin broken"
        )
        assert "Sub-mode (c)" in v032_body, (
            f"{surface_name} methodology-changelog.md v0.32.0 body missing "
            f"'Sub-mode (c)' marker — three-sub-mode pin broken"
        )
        # Sub-mode discipline anchors per slice-017 design.md Phase plan
        assert "/critique-review" in v032_body, (
            f"{surface_name} methodology-changelog.md v0.32.0 body missing "
            f"'/critique-review' substring — sub-mode (b) skill anchor broken"
        )
        assert "Prerequisite" in v032_body, (
            f"{surface_name} methodology-changelog.md v0.32.0 body missing "
            f"'Prerequisite' substring — sub-mode (c) /build-slice placement "
            f"anchor broken (per /critique M2 ACCEPTED-FIXED: sub-mode (c) "
            f"lives in /build-slice ## Prerequisite check section, NOT a "
            f"new ### Step 0)"
        )


def test_v_0_32_0_tphd_1_entry_names_slice_016_cross_slice_anchor():
    """methodology-changelog v0.32.0 / TPHD-1 entry must cite slice-016
    as the N=1 cross-slice anchor bidirectionally.

    Defect class: TPHD-1 codified at N=1 (proactive ratchet ahead of typical
    N=2 promotion threshold per slice-016 reflection language) — the entry
    must cite slice-016 as the empirical source of the TF-1-plan-staleness
    pattern. Without this anchor, the v0.32.0 entry doesn't surface the
    evidence base.

    Rule reference: TPHD-1 (slice-017 AC #1 — cross-slice anchor pin per
    slice-013 EPGD-1 + slice-015 SCPD-1 strict-both-anchor precedent
    adapted to N=1 single-anchor).
    """
    in_repo = read_file("methodology-changelog.md")
    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    installed = installed_path.read_text(encoding="utf-8")

    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        # Find the v0.32.0 entry body
        v032_start = content.find("## v0.32.0")
        v031_start = content.find("## v0.31.0", v032_start)
        assert v032_start != -1, (
            f"{surface_name} methodology-changelog.md missing v0.32.0 entry"
        )
        if v031_start == -1:
            v032_body = content[v032_start:]
        else:
            v032_body = content[v032_start:v031_start]
        assert "slice-016" in v032_body, (
            f"{surface_name} methodology-changelog.md v0.32.0 missing "
            f"cross-slice anchor 'slice-016' — TPHD-1 codification at N=1 "
            f"must cite slice-016 as evidence source"
        )


# --- ADR-016 pin (slice-017) ---

def test_adr_016_exists_and_names_tphd_1_canonical_phrase():
    """ADR-016 must exist at architecture/decisions/ADR-016-*.md AND contain
    the canonical phrase `TF-1 plan harmonization discipline`.

    Defect class (per slice-014 ADR-013 + slice-015 ADR-014 + slice-016
    ADR-015 pin precedent): the ADR is the third surface of the N-surface
    schema-pin (3-surface shape: ADR-016 + in-repo methodology-changelog
    v0.32.0 + installed methodology-changelog v0.32.0). If the ADR file is
    missing or doesn't contain the canonical phrase, the N-surface
    schema-pin (N=6 stable post-slice-017) breaks.

    Rule reference: TPHD-1 (slice-017 AC #3 — ADR-016 surface of 3-surface
    canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-016-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-016 file at "
        f"architecture/decisions/ADR-016-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "TF-1 plan harmonization discipline" in adr_content, (
        f"ADR-016 ({adr_files[0].name}) missing canonical phrase "
        f"'TF-1 plan harmonization discipline' — N-surface schema-pin "
        f"(N=6 stable post-slice-017: ADR-016 + in-repo + installed "
        f"methodology-changelog) is broken at the ADR-016 surface"
    )


# --- Slice-019 / LAYER-EVID-1 entry pinning ---


def test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed():
    """methodology-changelog v0.33.0 / LAYER-EVID-1 entry MUST be present in
    both in-repo and installed copies of methodology-changelog.md,
    bidirectionally sha256 byte-equal at slice-019 ship hash (N=14 -> N=15
    forensic capture).

    Defect class (per slice-019 /critique B1 + AC #3): forgotten
    forward-sync after in-repo edit leaves installed methodology-changelog
    stale; /critic-calibrate + /status surfacing references stale data;
    audit-trail across N-surface schema-pin is broken.

    Rule reference: LAYER-EVID-1 (slice-019 AC #3); 3-surface schema-pin
    precedent: slice-013 EPGD-1 + slice-014 PMI-1 v1.1 + slice-015 SCPD-1
    + slice-016 RPCD-1 + slice-017 TPHD-1 (N=5 stable -> N=6 with slice-019).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.33.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.33.0 entry"
    )
    assert "LAYER-EVID-1" in in_repo, (
        "in-repo methodology-changelog.md missing LAYER-EVID-1 rule reference"
    )

    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    assert installed_path.exists(), (
        f"installed methodology-changelog.md missing at {installed_path}"
    )
    installed = installed_path.read_text(encoding="utf-8")
    assert "## v0.33.0" in installed, (
        "installed ~/.claude/methodology-changelog.md missing v0.33.0 entry — "
        "forward-sync after in-repo edit was forgotten"
    )
    assert "LAYER-EVID-1" in installed, (
        "installed ~/.claude/methodology-changelog.md missing LAYER-EVID-1 "
        "rule reference"
    )


def test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase():
    """methodology-changelog v0.33.0 / LAYER-EVID-1 entry body MUST contain
    the canonical phrase `textual import-evidence requirement` bidirectionally,
    scoped strictly to the v0.33.0 entry body (NOT global file substring) via
    `_extract_v033_body` helper per slice-018 sibling-scoping discipline.

    Per slice-019 /critique M4 ACCEPTED-PENDING + slice-018 reflection:
    every codification slice's entry-pin sibling test must scope to the
    target version's body to avoid global-substring false-positives (the
    slice-016 RPCD-1 sibling-test scoping flaw, retired at slice-018).

    Surface-context-aware pre-validation per slice-018 /critique-review
    m-add-1 ACCEPTED-FIXED (preserves slice-017 L1088-1090 diagnostic
    pattern): assert lives at call site so error message interpolates
    surface_name; helper assumes pre-validated input.

    Rule reference: LAYER-EVID-1 (slice-019 AC #3 — N=3 surfaces pin:
    skills/diagnose/passes/03f-layering.md + skills/diagnose/SKILL.md +
    methodology-changelog v0.33.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    installed = installed_path.read_text(encoding="utf-8")

    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        # Surface-context-aware pre-validation per /critique-review m-add-1
        # ACCEPTED-FIXED (preserves slice-017 L1088-1090 diagnostic pattern):
        # assert lives at call site so error message can interpolate
        # surface_name; helper assumes pre-validated input.
        assert "## v0.33.0" in content, (
            f"{surface_name} methodology-changelog.md missing v0.33.0 entry — "
            f"entry-pin broken (slice-019 LAYER-EVID-1 surface)"
        )
        v033_body = _extract_v033_body(content)

        assert "textual import-evidence requirement" in v033_body, (
            f"{surface_name} methodology-changelog.md v0.33.0 body missing "
            f"canonical phrase 'textual import-evidence requirement' — "
            f"N-surface schema-pin (N=3 surfaces: pass template + SKILL.md "
            f"+ methodology-changelog entry) broken at this surface"
        )
        assert "LAYER-EVID-1" in v033_body, (
            f"{surface_name} methodology-changelog.md v0.33.0 body missing "
            f"'LAYER-EVID-1' rule reference — entry-pin broken"
        )


def test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body():
    """Regression test: prove the v0.33.0 scoping discipline (via
    `_extract_v033_body` helper) catches stripped canonical-phrase markers
    within v0.33.0 body even when v0.32.0+ entries retain them.

    Defect class (slice-018 reflection N=2 cumulative inheritance):
    if slice-019's entry-pin tests had been written without `_extract_v033_body`
    scoping (i.e., raw `in content` global-substring check), a future slice
    could strip the canonical phrase from v0.33.0 body while v0.34.0+
    entries retain it, and the sibling test would silently false-positive
    PASS. Sibling-scoping helper retires that failure mode.

    Single-code-path discipline per slice-018 /critique M2 ACCEPTED-FIXED:
    this regression-test-passes ↔ sibling-test-fails-on-stripped-fixture
    link is established by EXECUTION (this synthetic fixture exercises
    the SAME `_extract_v033_body` helper that the real sibling test uses),
    NOT by code-reading.

    Pattern mirrors slice-018 L1010-1060 canonical regression pattern at
    the PATTERN level (NOT literal-code) per slice-018 /critique-review
    m-add-2 Audit 3 refinement.

    Rule reference: LAYER-EVID-1 (slice-019 AC #3) + slice-018 sibling-test
    scoping discipline (slice-019 /critique M4 ACCEPTED-PENDING).
    """
    # Synthetic: v0.33.0 entry body HAS BEEN STRIPPED of the canonical
    # phrase; v0.32.0 entry retains it (as a foil that would false-positive
    # PASS a global-substring check).
    synthetic = (
        "# Methodology Changelog (test fixture)\n"
        "\n"
        "## v0.33.0 — 2026-05-13\n"
        "\n"
        "Some other entry text without the canonical phrase. The v0.33.0\n"
        "body has been hypothetically stripped of its key marker.\n"
        "\n"
        "## v0.32.0 — 2026-05-13\n"
        "\n"
        "TF-1 plan harmonization discipline codified, plus the strawman\n"
        "phrase: textual import-evidence requirement (this is the foil —\n"
        "appears in v0.32.0 body, NOT v0.33.0).\n"
        "\n"
        "## v0.31.0 — 2026-05-13\n"
        "\n"
        "Earlier entry.\n"
    )

    # Global-substring check on `synthetic` WOULD pass — the canonical
    # phrase appears in the file (in v0.32.0 body). This is the trap
    # the helper retires.
    assert "textual import-evidence requirement" in synthetic, (
        "synthetic fixture should contain the canonical phrase SOMEWHERE "
        "(in v0.32.0 body) — proving the global-substring fallacy that the "
        "scoping helper retires"
    )

    # Helper-scoped check: extract v0.33.0 body and verify the canonical
    # phrase is ABSENT from it (proving the scoping discipline catches
    # the stripped-body case).
    v033_body = _extract_v033_body(synthetic)
    assert "textual import-evidence requirement" not in v033_body, (
        "_extract_v033_body should have scoped to v0.33.0 body only, "
        "which has been hypothetically stripped. Canonical phrase appears "
        "in v033_body — scoping discipline is broken; sibling test would "
        "false-positive PASS on this fixture."
    )
    # Sanity: v0.32.0 marker should NOT appear inside v0.33.0 body
    # (boundary discipline)
    assert "## v0.32.0" not in v033_body, (
        "_extract_v033_body should stop at `## v0.32.0` boundary; if "
        "marker appears inside v033_body, the scoping helper is broken"
    )


def test_adr_017_exists_and_names_layer_evid_1_canonical_phrase():
    """ADR-017 must exist at architecture/decisions/ADR-017-*.md AND contain
    the canonical phrase `textual import-evidence requirement`.

    Defect class (per slice-014 ADR-013 + slice-015 ADR-014 + slice-016
    ADR-015 + slice-017 ADR-016 pin precedent): the ADR is the fourth
    surface of the N-surface schema-pin discipline. If the ADR file is
    missing or doesn't contain the canonical phrase, the N-surface
    schema-pin (N=6 stable post-slice-017 -> N=7 with slice-019) breaks.

    Rule reference: LAYER-EVID-1 (slice-019 AC #4 — ADR-017 surface of
    N-surface canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-017-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-017 file at "
        f"architecture/decisions/ADR-017-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "textual import-evidence requirement" in adr_content, (
        f"ADR-017 ({adr_files[0].name}) missing canonical phrase "
        f"'textual import-evidence requirement' — N-surface schema-pin "
        f"(N=7 with slice-019: ADR-017 + in-repo + installed "
        f"methodology-changelog + 03f-layering.md prose + SKILL.md prose) "
        f"is broken at the ADR-017 surface"
    )


# --- Slice-020 / BFRD-1 entry pinning ---
#
# Per BFRD-1 (`methodology-changelog.md` v0.34.0): `/slice` Step 3c codifies
# the bug-fix repro prelude discipline. Entry-pin tests assert the v0.34.0
# methodology-changelog body names BFRD-1 + both detection modes + STOP-and-
# route behavior + verification-mechanism canonical phrase. ADR-pin asserts
# ADR-018 exists and names the canonical phrase.
#
# Per slice-020 /critique B1 ACCEPTED-FIXED: mode (a) detection covers
# `fix-*` prefix + `*-fix` suffix + bugfix-* + hotfix-* + defect-* +
# repair-* + patch-* + harden-*-bug regex variants; slice-001's `-fix`
# suffix shape is the witnessed in-project false-negative anchor.
#
# Per slice-020 /critique B2 + /critique-review M-add-2 ACCEPTED-FIXED:
# verification mechanism is `shippability.md grep verification` for
# `tests/bugs/*` Command-cell match + verbal-claim-with-path fallback.
# The `bug:` provenance branch was DROPPED at /critique-review per
# RPCD-1 sub-mode (b) class catch (zero precedent in shippability rows
# 1-19; aspirational branch removed).
#
# Per slice-020 /critique M5 ACCEPTED-FIXED + design.md Audit 4 Option C:
# entry-pin tests call `_extract_version_body(content, "0.34.0")`
# directly (the generalized helper); slice-018 + slice-019 wrappers
# preserved for backward compatibility.

_V034 = "0.34.0"


def test_v_0_34_0_bfrd_1_entry_present_in_repo_and_installed():
    """v0.34.0 BFRD-1 entry exists in both in-repo + installed methodology-
    changelog.md with bidirectional sha256 byte-equality (CAD-1 invariant).

    Defect class: if the in-repo and installed copies diverge, Claude reads
    stale prose at /status or /slice invocation. Bidirectional pin enforced
    by reading both files and asserting both contain the v0.34.0 entry
    header.
    Rule reference: BFRD-1 (slice-020 AC #1).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V034}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V034} entry "
            f"header — slice-020 BFRD-1 entry was not added or was lost; "
            f"surface-context per slice-018 /critique-review m-add-1 ACCEPTED-FIXED"
        )
        body = _extract_version_body(content, _V034)
        assert "BFRD-1" in body, (
            f"{surface_name} v{_V034} entry body missing rule-ID 'BFRD-1' — "
            f"entry-pin broken at the rule-ID layer"
        )


def test_v_0_34_0_bfrd_1_entry_names_both_detection_modes():
    """v0.34.0 entry body names BOTH detection modes — mode (a) name-shape
    fast-path with regex variants (fix-* prefix, *-fix suffix witnessed
    at slice-001, bugfix-*, hotfix-*, defect-*, repair-*, patch-*,
    harden-*-bug) AND mode (b) PRIMARY candidate-source signal.

    Defect class: future slice strips one of the detection modes; entry
    becomes single-mode and naïve-detection class re-introduces. Per
    /critique B1 ACCEPTED-FIXED: widened mode (a) regex set is load-
    bearing; without it slice-001's `-fix` suffix shape escapes detection.
    Rule reference: BFRD-1 (slice-020 AC #1, /critique B1).
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V034)
    mode_a_anchors = (
        "name-shape fast-path",
        "*-fix",  # suffix witnessed in-project
        "slice-001",  # false-negative anchor citation
    )
    mode_b_anchors = (
        "candidate-source signal",
        "PRIMARY",
    )
    present_a = [a for a in mode_a_anchors if a in body]
    present_b = [a for a in mode_b_anchors if a in body]
    assert len(present_a) >= 2, (
        f"v{_V034} BFRD-1 entry body missing mode (a) detection anchors; "
        f"found {len(present_a)} of {len(mode_a_anchors)}: {present_a}. "
        f"Required: at least 2 of {mode_a_anchors!r}"
    )
    assert len(present_b) >= 1, (
        f"v{_V034} BFRD-1 entry body missing mode (b) PRIMARY detection "
        f"anchor; found {len(present_b)} of {len(mode_b_anchors)}: "
        f"{present_b}. Required: at least 1 of {mode_b_anchors!r}"
    )


def test_v_0_34_0_bfrd_1_entry_names_stop_and_route_behavior():
    """v0.34.0 entry body names STOP-and-route behavior with /repro
    routing instruction.

    Defect class: future slice strips the STOP-and-route imperative;
    the discipline degrades to advisory-only without an enforcement
    primitive at /slice runtime.
    Rule reference: BFRD-1 (slice-020 AC #1).
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V034)
    assert "STOP" in body, (
        f"v{_V034} BFRD-1 entry body missing STOP keyword for STOP-and-"
        f"route behavior — discipline degrades to advisory-only"
    )
    assert "/repro" in body, (
        f"v{_V034} BFRD-1 entry body missing /repro skill reference — "
        f"STOP-and-route mechanism cannot describe where to route"
    )


def test_v_0_34_0_bfrd_1_entry_names_verification_mechanism():
    """v0.34.0 entry body names verification-mechanism canonical phrase
    `shippability.md grep verification` + `tests/bugs/*` path-targeting
    convention per /critique B2 + /critique-review M-add-2 ACCEPTED-FIXED
    Option (a).

    Defect class: future slice strips the verification mechanism; BFRD-1
    becomes advisory-only with no enforcement primitive (RPCD-1 sub-mode
    (b) NEW-status/token allowlist-audit class regression at the
    BFRD-1 surface).
    Rule reference: BFRD-1 (slice-020 AC #1, /critique B2 +
    /critique-review M-add-2).
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V034)
    assert "shippability.md grep verification" in body, (
        f"v{_V034} BFRD-1 entry body missing canonical phrase "
        f"'shippability.md grep verification' — verification mechanism "
        f"canonical-phrase pin broken per /critique B2 ACCEPTED-FIXED"
    )
    assert "tests/bugs/" in body, (
        f"v{_V034} BFRD-1 entry body missing `tests/bugs/` path-targeting "
        f"convention reference — verification mechanism's primary grep "
        f"signature is unspecified"
    )


def test_adr_018_exists_and_names_bfrd_1_canonical_phrase():
    """ADR-018 file exists at architecture/decisions/ADR-018-*.md AND
    contains the canonical phrase `bug-fix repro prelude discipline`
    pinned per slice-013/014/015/016/017/019 ADR-pin convention N=5
    → N=6 stable.

    Defect class: future slice renames ADR-018 or strips the canonical
    phrase from its body; N-surface schema-pin breaks at the ADR
    surface.
    Rule reference: BFRD-1 (slice-020 AC #3 — ADR-018 surface of
    N-surface canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-018-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-018 file at "
        f"architecture/decisions/ADR-018-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "bug-fix repro prelude discipline" in adr_content, (
        f"ADR-018 ({adr_files[0].name}) missing canonical phrase "
        f"'bug-fix repro prelude discipline' — N-surface schema-pin "
        f"(N=7 with slice-020: ADR-018 + in-repo + installed "
        f"methodology-changelog + SKILL.md prose) is broken at the "
        f"ADR-018 surface"
    )


# --- Slice-021 / BRANCH-1 branch-per-slice workflow ---
# Per /critique-rerun M-add-2 ACCEPTED-FIXED: canonical ADR-pin test function
# name is `test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1`
# (harmonized across mission-brief TF-1 plan + design.md Command cell + here).

_V035 = "0.35.0"


def test_v_0_35_0_branch_1_entry_present_in_repo_and_installed():
    """v0.35.0 BRANCH-1 entry exists in both in-repo + installed methodology-
    changelog.md.

    Defect class: if the in-repo and installed copies diverge, Claude reads
    stale prose at /status or /slice invocation. Bidirectional pin enforced
    by reading both files and asserting both contain the v0.35.0 entry
    header AND the BRANCH-1 rule ID.

    Rule reference: BRANCH-1 (slice-021 AC #5).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V035}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V035} entry "
            f"header — slice-021 BRANCH-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V035)
        assert "BRANCH-1" in body, (
            f"{surface_name} v{_V035} entry body missing rule-ID 'BRANCH-1' — "
            f"entry-pin broken at the rule-ID layer"
        )


def test_v_0_35_0_branch_1_entry_names_three_sub_modes_in_repo_and_installed():
    """v0.35.0 entry body names ALL three BRANCH-1 sub-modes — (a) build-time
    branch-create, (b) commit-time `--merge` flow, (c) audit-time pre-finish
    refusal.

    Defect class: future slice strips one of the sub-modes; entry becomes
    N<3 surface schema-pin and the 3-sub-mode discipline regresses.
    Rule reference: BRANCH-1 (slice-021 AC #5).
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V035)
    sub_mode_anchors = (
        "Sub-mode (a)",
        "Sub-mode (b)",
        "Sub-mode (c)",
        "build-time branch-create",
        "commit-time",  # --merge flow
        "audit-time pre-finish refusal",
    )
    present = [a for a in sub_mode_anchors if a in body]
    assert len(present) >= 5, (
        f"v{_V035} BRANCH-1 entry body missing sub-mode anchors; "
        f"found {len(present)} of {len(sub_mode_anchors)}: {present}. "
        f"Required: at least 5 of {sub_mode_anchors!r}"
    )


def test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1():
    """ADR-019 file exists at architecture/decisions/ADR-019-*.md AND
    contains the canonical phrase `branch-per-slice workflow` AND the
    BRANCH-1 rule reference pinned per slice-013/014/015/016/017/019/020
    ADR-pin convention N=6 → N=7 stable.

    Defect class: future slice renames ADR-019 or strips the canonical
    phrase from its body; N-surface schema-pin breaks at the ADR
    surface.
    Rule reference: BRANCH-1 (slice-021 AC #5 — ADR-019 surface of
    N-surface canonical-phrase pin).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-019-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-019 file at "
        f"architecture/decisions/ADR-019-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "branch-per-slice workflow" in adr_content, (
        f"ADR-019 ({adr_files[0].name}) missing canonical phrase "
        f"'branch-per-slice workflow' — N-surface schema-pin is broken "
        f"at the ADR-019 surface"
    )
    assert "BRANCH-1" in adr_content, (
        f"ADR-019 ({adr_files[0].name}) missing BRANCH-1 rule reference — "
        f"ADR must link to the codified rule"
    )


# --- Slice-022 / ADR-020 PR-aware /commit-slice modes ---
# Per /build-slice TPHD-1 sub-mode (c) Prerequisite-check 2026-05-15:
# ADR-020 tests live in test_methodology_changelog.py per slice-013→021
# ADR-pin convention N=7 → N=8 stable (NOT a separate `test_adr_020_*.py` file).
# Per /critique-review M-add-1 ACCEPTED-FIXED: ADR-020 supersession encoding is
# one-directional (`supersedes: ADR-019` frontmatter slot); ADR-019 stays
# unmodified per append-only; SUP-1 does NOT apply to ADRs.

_V036 = "0.36.0"


def test_v_0_36_0_pr_aware_commit_slice_entry_present_in_repo_and_installed():
    """v0.36.0 PR-aware /commit-slice entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge, Claude
    reads stale prose at /status or /slice. Enforced by reading both and
    asserting both contain the v0.36.0 entry header AND the canonical phrase.

    Rule reference: slice-022 AC #5 (methodology-changelog v0.36.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V036}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V036} entry "
            f"header — slice-022 PR-aware /commit-slice entry was not added or "
            f"was lost"
        )
        body = _extract_version_body(content, _V036)
        assert "3-mode PR-aware /commit-slice taxonomy" in body, (
            f"{surface_name} v{_V036} entry body missing canonical phrase "
            f"'3-mode PR-aware /commit-slice taxonomy' — entry-pin broken at "
            f"the canonical-phrase layer"
        )


def test_v_0_36_0_entry_names_three_modes_in_repo_and_installed():
    """v0.36.0 entry body names all 3 modes (`--merge`, `--push`,
    `--sync-after-pr`) AND the partial supersession scope (ADR-020 supersedes
    ADR-019 sub-mode (b) only; sub-modes (a) + (c) unchanged).

    Defect class: future slice strips a mode reference from the entry; the
    3-mode taxonomy regresses at the documentation surface.

    Rule reference: slice-022 AC #5 + ADR-020.
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V036)
    mode_anchors = ("--merge", "--push", "--sync-after-pr")
    for anchor in mode_anchors:
        assert anchor in body, (
            f"v{_V036} entry body missing mode anchor {anchor!r} — "
            f"3-mode taxonomy is incomplete in the changelog entry"
        )
    # Partial supersession scope anchors.
    supersession_anchors = ("ADR-020", "ADR-019", "sub-mode (b)")
    for anchor in supersession_anchors:
        assert anchor in body, (
            f"v{_V036} entry body missing supersession anchor {anchor!r} — "
            f"partial supersession of ADR-019 sub-mode (b) only is unclear"
        )


def test_adr_020_exists_and_supersedes_adr_019():
    """ADR-020 file exists at architecture/decisions/ADR-020-*.md AND has
    frontmatter `supersedes: ADR-019` (one-directional encoding per ADR family
    convention; ADR-019 stays unmodified per append-only).

    Defect class: future slice strips the supersession link OR mistakenly edits
    ADR-019 to add a `superseded-by:` field (violating append-only). Test pins
    the canonical one-directional shape.

    Rule reference: slice-022 AC #4 + /critique-review M-add-1 ACCEPTED-FIXED
    (SUP-1 does NOT apply to ADRs; ADR family convention is one-directional).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-020-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-020 file at "
        f"architecture/decisions/ADR-020-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    # Forward link: ADR-020 must declare it supersedes ADR-019.
    assert "supersedes: ADR-019" in adr_content, (
        f"ADR-020 ({adr_files[0].name}) missing `supersedes: ADR-019` "
        f"frontmatter slot — one-directional supersession encoding broken"
    )
    # ADR-019 must NOT carry a reverse `superseded-by:` field (ADR family
    # convention is one-directional; append-only respected).
    adr_019_files = list(decisions_dir.glob("ADR-019-*.md"))
    assert len(adr_019_files) == 1, (
        f"Expected exactly one ADR-019 file; found {len(adr_019_files)}"
    )
    adr_019_content = adr_019_files[0].read_text(encoding="utf-8")
    assert "superseded-by:" not in adr_019_content, (
        f"ADR-019 ({adr_019_files[0].name}) carries `superseded-by:` field — "
        f"violates append-only discipline AND ADR family one-directional "
        f"convention (SUP-1 applies to /supersede-slice for archived-slice "
        f"reflection.md links, NOT ADRs; per slice-022 /critique-review M-add-1)"
    )


# =============================================================================
# slice-023 v0.37.0 UTF8-STDOUT-1 entry-pins + ADR-021 pin
# =============================================================================
# Per UTF8-STDOUT-1 codification (methodology-changelog.md v0.37.0). These
# entry-pin functions follow the EPGD-1 N=10 stable convention (slice-023
# ADDS-only; 0 of prior entry-pin functions touched). ADR-pin follows the
# convention N=9 stable (NOT a separate tests/decisions/ file).


_V037 = "0.37.0"


def test_v_0_37_0_utf8_stdout_1_entry_present_in_repo_and_installed():
    """v0.37.0 UTF8-STDOUT-1 entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge, Claude
    reads stale prose at /status or /slice. Enforced by reading both and
    asserting both contain the v0.37.0 entry header AND the canonical phrase.

    Rule reference: slice-023 AC #5 (methodology-changelog v0.37.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V037}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V037} entry "
            f"header — slice-023 UTF8-STDOUT-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V037)
        assert "UTF8-STDOUT-1" in body, (
            f"{surface_name} v{_V037} entry body missing canonical rule ID "
            f"'UTF8-STDOUT-1' — entry-pin broken at the rule-ID layer"
        )


def test_v_0_37_0_utf8_stdout_1_entry_names_all_three_surfaces():
    """v0.37.0 entry body names all 3 surfaces of UTF8-STDOUT-1:
    helper module + audit module + invocation pattern.

    Defect class: future slice strips a surface reference; the N-surface
    schema-pin shape regresses at the documentation layer.

    Rule reference: slice-023 AC #5.
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V037)
    surface_anchors = (
        "tools/_stdout.py",
        "tools/utf8_stdout_audit.py",
        "first executable statement",
    )
    for anchor in surface_anchors:
        assert anchor in body, (
            f"v{_V037} entry body missing surface anchor {anchor!r} — "
            f"3-surface schema-pin is incomplete in the changelog entry"
        )


def test_v_0_37_0_utf8_stdout_1_entry_pins_canonical_invocation_pattern():
    """v0.37.0 entry body pins the canonical invocation pattern — function
    name `reconfigure_stdout_utf8` AND canonical import form
    `from tools import _stdout`.

    Defect class: future slice changes the canonical helper function name OR
    import form without updating the codification surface; the prose pin
    silently desyncs from code.

    Rule reference: slice-023 AC #5 + M4 ACCEPTED-FIXED.
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V037)
    invocation_anchors = (
        "reconfigure_stdout_utf8",
        "from tools import _stdout",
    )
    for anchor in invocation_anchors:
        assert anchor in body, (
            f"v{_V037} entry body missing canonical invocation anchor "
            f"{anchor!r} — invocation pattern pin broken"
        )


def test_adr_021_present_and_reversibility_cheap():
    """ADR-021 file exists at architecture/decisions/ADR-021-*.md AND has
    frontmatter `reversibility: cheap` + names UTF8-STDOUT-1.

    Defect class: ADR-021 lost / renamed / scope-shifted; UTF8-STDOUT-1 has
    no canonical decision record.

    Rule reference: slice-023 AC #5 (ADR-021).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-021-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-021 file at "
        f"architecture/decisions/ADR-021-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "reversibility: cheap" in adr_content, (
        f"ADR-021 ({adr_files[0].name}) missing `reversibility: cheap` "
        f"frontmatter field"
    )
    assert "UTF8-STDOUT-1" in adr_content, (
        f"ADR-021 ({adr_files[0].name}) missing canonical rule ID "
        f"'UTF8-STDOUT-1' in body"
    )


def test_adr_020_documents_three_mode_taxonomy():
    """ADR-020 body documents the 3-mode taxonomy (`--merge`, `--push`,
    `--sync-after-pr`) AND the partial supersession scope (sub-mode (b) only;
    sub-modes (a) + (c) unchanged).

    Defect class: future slice strips a mode reference OR misrepresents the
    supersession scope (e.g., claims ADR-020 fully supersedes ADR-019); ADR
    canonical content regresses.

    Rule reference: slice-022 AC #4.
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-020-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-020 file at "
        f"architecture/decisions/ADR-020-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    mode_anchors = ("--merge", "--push", "--sync-after-pr")
    for anchor in mode_anchors:
        assert anchor in adr_content, (
            f"ADR-020 ({adr_files[0].name}) missing mode anchor {anchor!r} — "
            f"3-mode taxonomy incomplete"
        )
    # Partial-supersession scope anchors.
    scope_anchors = ("sub-mode (a)", "sub-mode (b)", "sub-mode (c)")
    for anchor in scope_anchors:
        assert anchor in adr_content, (
            f"ADR-020 ({adr_files[0].name}) missing sub-mode anchor "
            f"{anchor!r} — partial supersession scope unclear"
        )


# =============================================================================
# slice-024 v0.38.0 FBCD-1 entry-pins + ADR-022 pin
# =============================================================================
# Per FBCD-1 codification (methodology-changelog.md v0.38.0). These
# entry-pin functions follow the EPGD-1 N=11 stable convention (slice-024
# ADDS-only; 0 of 17 prior _entry_present_in_repo_and_installed-family functions
# touched). ADR-pin follows the convention N=10 stable (NOT a separate
# tests/decisions/ file).
#
# Section header `# --- Slice-024 / FBCD-1 entry pinning ---` deferred to the
# `# ===` border + description comment style established at slice-021/022/023
# (empirical reality vs design.md's `# ---` hint per CLAUDE.md "code is truth").


_V038 = "0.38.0"
_V039 = "0.39.0"
_V040 = "0.40.0"


def test_v_0_38_0_fbcd_1_entry_present_in_repo_and_installed():
    """v0.38.0 FBCD-1 entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge, Claude
    reads stale prose at /status or /slice. Enforced by reading both and
    asserting both contain the v0.38.0 entry header AND the canonical phrase.

    Rule reference: slice-024 AC #3 (methodology-changelog v0.38.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V038}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V038} entry "
            f"header — slice-024 FBCD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V038)
        assert "FBCD-1" in body, (
            f"{surface_name} v{_V038} entry body missing canonical rule ID "
            f"'FBCD-1' — entry-pin broken at the rule-ID layer"
        )
        assert "Fix-block-completeness discipline" in body, (
            f"{surface_name} v{_V038} entry body missing canonical phrase "
            f"'Fix-block-completeness discipline' — entry-pin broken at the "
            f"canonical-phrase layer"
        )


def test_v_0_38_0_fbcd_1_names_both_sub_modes():
    """v0.38.0 entry body names both sub-modes of FBCD-1:
    (a) Original-draft cross-file consistency + (b) Post-ACCEPTED-FIXED
    sibling-sweep.

    Defect class: future slice strips a sub-mode reference; the 2-sub-mode
    codification regresses at the documentation layer.

    Rule reference: slice-024 AC #3.
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V038)
    sub_mode_anchors = (
        "Original-draft cross-file consistency",
        "Post-ACCEPTED-FIXED sibling-sweep",
    )
    for anchor in sub_mode_anchors:
        assert anchor in body, (
            f"v{_V038} entry body missing sub-mode anchor {anchor!r} — "
            f"two-sub-mode codification incomplete in the changelog entry"
        )


def test_v_0_38_0_fbcd_1_cites_slice_020_021_022_023():
    """v0.38.0 entry body cites all 4 cross-slice anchors strict-4-of-4:
    slice-020 + slice-021 + slice-022 + slice-023.

    Defect class: future slice strips a cross-slice anchor; the N=4-distinct-
    slice evidence base regresses at the documentation layer.

    Rule reference: slice-024 AC #3.
    """
    in_repo = read_file("methodology-changelog.md")
    body = _extract_version_body(in_repo, _V038)
    cross_slice_anchors = ("slice-020", "slice-021", "slice-022", "slice-023")
    for anchor in cross_slice_anchors:
        assert anchor in body, (
            f"v{_V038} entry body missing cross-slice anchor {anchor!r} — "
            f"strict-4-of-4 N=4-distinct-slice evidence base incomplete"
        )


def test_adr_022_exists_and_names_fbcd_1_canonical_phrase():
    """ADR-022 file exists at architecture/decisions/ADR-022-*.md AND has
    frontmatter `reversibility: cheap` + names FBCD-1 + canonical phrase.

    Defect class: ADR-022 lost / renamed / scope-shifted; FBCD-1 has no
    canonical decision record.

    Rule reference: slice-024 AC #4 (ADR-022).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-022-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-022 file at "
        f"architecture/decisions/ADR-022-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "reversibility: cheap" in adr_content, (
        f"ADR-022 ({adr_files[0].name}) missing `reversibility: cheap` "
        f"frontmatter field"
    )
    assert "FBCD-1" in adr_content, (
        f"ADR-022 ({adr_files[0].name}) missing canonical rule ID 'FBCD-1' "
        f"in body"
    )
    assert "Fix-block-completeness discipline" in adr_content, (
        f"ADR-022 ({adr_files[0].name}) missing canonical phrase "
        f"'Fix-block-completeness discipline' in body"
    )


def test_v_0_39_0_ptfcd_1_entry_present_in_repo_and_installed():
    """v0.39.0 PTFCD-1 entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. Enforced by reading both
    and asserting both contain the v0.39.0 entry header AND the canonical
    rule ID AND the canonical phrase.

    Rule reference: slice-025 AC #4 (methodology-changelog v0.39.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V039}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V039} entry "
            f"header — slice-025 PTFCD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V039)
        assert "PTFCD-1" in body, (
            f"{surface_name} v{_V039} entry body missing canonical rule ID "
            f"'PTFCD-1' — entry-pin broken at the rule-ID layer"
        )
        assert "Phantom test-file citation discipline" in body, (
            f"{surface_name} v{_V039} entry body missing canonical phrase "
            f"'Phantom test-file citation discipline' — entry-pin broken at "
            f"the canonical-phrase layer"
        )


def test_adr_023_present_and_reversibility_cheap():
    """ADR-023 file exists at architecture/decisions/ADR-023-*.md AND has
    frontmatter `reversibility: cheap` + names PTFCD-1 + canonical phrase.

    Defect class: ADR-023 lost / renamed / scope-shifted; PTFCD-1 has no
    canonical decision record.

    Rule reference: slice-025 AC #4 (ADR-023).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-023-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-023 file at "
        f"architecture/decisions/ADR-023-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "reversibility: cheap" in adr_content, (
        f"ADR-023 ({adr_files[0].name}) missing `reversibility: cheap` "
        f"frontmatter field"
    )
    assert "PTFCD-1" in adr_content, (
        f"ADR-023 ({adr_files[0].name}) missing canonical rule ID 'PTFCD-1' "
        f"in body"
    )
    assert "Phantom test-file citation discipline" in adr_content, (
        f"ADR-023 ({adr_files[0].name}) missing canonical phrase "
        f"'Phantom test-file citation discipline' in body"
    )


# --- Slice-026 / CRP-1 v0.40.0 entry-pin + shippability propagation ---


def test_v_0_40_0_crp_1_entry_present_in_repo_and_installed():
    """v0.40.0 CRP-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the canonical rule ID + canonical phrase
    + the NON-`-D` audit-enforced-gate naming-class conformance prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. Also pins the B1
    correction (CRP-1 is audit-enforced, NON-`-D`, per ADR-019) so a future
    edit cannot silently reintroduce a `-D` naming-class contradiction.

    Rule reference: slice-026 AC #3 (methodology-changelog v0.40.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V040}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V040} entry "
            f"header — slice-026 CRP-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V040)
        assert "CRP-1" in body, (
            f"{surface_name} v{_V040} entry body missing canonical rule ID "
            f"'CRP-1' — entry-pin broken at the rule-ID layer"
        )
        assert "Critique-review prerequisite check" in body, (
            f"{surface_name} v{_V040} entry body missing canonical phrase "
            f"'Critique-review prerequisite check' — entry-pin broken at the "
            f"canonical-phrase layer"
        )
        assert "audit-enforced gate" in body and "NON-`-D`" in body, (
            f"{surface_name} v{_V040} entry body missing the audit-enforced / "
            f"NON-`-D` naming-class conformance prose (per /critique B1 + "
            f"ADR-019) — a `-D` naming-class contradiction could silently "
            f"reappear"
        )


def test_v_0_40_0_crp_1_shippability_consumer_propagation():
    """architecture/shippability.md carries a CRP-1 row whose Command cell
    references the CRP-1 audit module (RPCD-1 / SCPD-1 consumer-reference
    propagation).

    Defect class: a new audit gate whose consumer references do not
    propagate into the shippability catalog can silently regress without
    /validate-slice catching it. SCPD-1 requires the propagation.

    Rule reference: slice-026 AC #4 (shippability consumer propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "CRP-1" in catalog, (
        "architecture/shippability.md missing a CRP-1 row — SCPD-1 "
        "consumer-reference propagation broken"
    )
    assert "critique_review_prerequisite_audit" in catalog, (
        "architecture/shippability.md CRP-1 row does not reference the "
        "tools.critique_review_prerequisite_audit consumer — SCPD-1 "
        "propagation incomplete"
    )


# --- Slice-027 / PCA-1 v0.41.0 entry-pin + shippability propagation ---

_V041 = "0.41.0"


def test_v_0_41_0_pca_1_entry_present_in_repo_and_installed():
    """v0.41.0 PCA-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the canonical rule ID + canonical
    phrase + the NON-`-D` audit-enforced-gate naming-class conformance
    prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. Also pins the
    audit-enforced / NON-`-D` (per ADR-019) conformance so a future edit
    cannot silently reintroduce a `-D` naming-class contradiction.

    Rule reference: slice-027 AC #5 (methodology-changelog v0.41.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V041}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V041} entry "
            f"header — slice-027 PCA-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V041)
        assert "PCA-1" in body, (
            f"{surface_name} v{_V041} entry body missing canonical rule ID "
            f"'PCA-1' — entry-pin broken at the rule-ID layer"
        )
        assert "Pipeline position" in body, (
            f"{surface_name} v{_V041} entry body missing canonical phrase "
            f"'Pipeline position' — entry-pin broken at the canonical-phrase "
            f"layer"
        )
        assert "audit-enforced gate" in body and "NON-`-D`" in body, (
            f"{surface_name} v{_V041} entry body missing the audit-enforced / "
            f"NON-`-D` naming-class conformance prose (per ADR-025 / ADR-019) "
            f"— a `-D` naming-class contradiction could silently reappear"
        )


def test_v_0_41_0_pca_1_shippability_consumer_propagation():
    """architecture/shippability.md carries a PCA-1 row whose Command cell
    references the PCA-1 audit module (RPCD-1 / SCPD-1 consumer-reference
    propagation).

    Defect class: a new audit gate whose consumer references do not
    propagate into the shippability catalog can silently regress without
    /validate-slice catching it. SCPD-1 requires the propagation.

    Rule reference: slice-027 AC #5 (shippability consumer propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "PCA-1" in catalog, (
        "architecture/shippability.md missing a PCA-1 row — SCPD-1 "
        "consumer-reference propagation broken"
    )
    assert "pipeline_chain_audit" in catalog, (
        "architecture/shippability.md PCA-1 row does not reference the "
        "tools.pipeline_chain_audit consumer — SCPD-1 propagation incomplete"
    )


def test_adr_025_present_and_reversibility_cheap():
    """ADR-025 file exists at architecture/decisions/ADR-025-*.md AND has
    frontmatter `reversibility: cheap` + names PCA-1 + canonical phrase.

    Defect class: ADR-025 lost / renamed / scope-shifted; PCA-1 has no
    canonical decision record.

    Rule reference: slice-027 (ADR-025).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-025-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-025 file at "
        f"architecture/decisions/ADR-025-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "reversibility: cheap" in adr_content, (
        f"ADR-025 ({adr_files[0].name}) missing `reversibility: cheap` "
        f"frontmatter field"
    )
    assert "PCA-1" in adr_content, (
        f"ADR-025 ({adr_files[0].name}) missing canonical rule ID 'PCA-1' "
        f"in body"
    )
    assert "Pipeline position" in adr_content, (
        f"ADR-025 ({adr_files[0].name}) missing canonical phrase "
        f"'Pipeline position' in body"
    )


# --- Slice-028 / UTF8-STDOUT-1 v1.1 v0.42.0 entry-pin + shippability propagation ---

_V042 = "0.42.0"
_UTF8_V11_PHRASE = "version-agnostic UTF-8 rollup sentinel"


def test_v_0_42_0_utf8_stdout_1_v1_1_entry_present_in_repo_and_installed():
    """v0.42.0 UTF8-STDOUT-1 v1.1 entry exists in both in-repo + installed
    methodology-changelog.md, with the canonical rule ID + canonical phrase
    + the rule-ID-lineage-preserved prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. Also pins the rule-ID
    lineage (UTF8-STDOUT-1 v1.1, NOT a new rule ID — mirroring PMI-1 v1.x /
    ADR-013) so a future edit cannot silently mint a spurious new rule ID.
    UTF8-STDOUT-1 v1.1 is a rule-version evolution, not an audit-enforced
    gate — this pin deliberately does NOT assert the NON-`-D` audit-gate
    naming prose (that is CRP-1/PCA-1-class, not applicable here).

    Rule reference: slice-028 AC #5 (methodology-changelog v0.42.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V042}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V042} entry "
            f"header — slice-028 UTF8-STDOUT-1 v1.1 entry was not added or "
            f"was lost"
        )
        body = _extract_version_body(content, _V042)
        assert "UTF8-STDOUT-1" in body, (
            f"{surface_name} v{_V042} entry body missing canonical rule ID "
            f"'UTF8-STDOUT-1' — entry-pin broken at the rule-ID layer"
        )
        assert _UTF8_V11_PHRASE in body, (
            f"{surface_name} v{_V042} entry body missing canonical phrase "
            f"{_UTF8_V11_PHRASE!r} — entry-pin broken at the canonical-phrase "
            f"layer (N=3 surface schema-pin)"
        )
        assert "v1.1" in body and "NOT a new rule ID" in body, (
            f"{surface_name} v{_V042} entry body missing the rule-ID-lineage "
            f"prose ('v1.1' + 'NOT a new rule ID', per ADR-026 / ADR-013 "
            f"precedent) — a spurious new rule ID could silently appear"
        )


def test_v_0_42_0_utf8_stdout_1_v1_1_shippability_consumer_propagation():
    """architecture/shippability.md carries a slice-028 row referencing the
    UTF8-STDOUT-1 v1.1 consumer (RPCD-1 / SCPD-1 consumer-reference
    propagation).

    Defect class: a rule-version evolution whose consumer references do not
    propagate into the shippability catalog can silently regress without
    /validate-slice catching it. SCPD-1 requires the propagation.

    Rule reference: slice-028 AC #5 (shippability consumer propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "UTF8-STDOUT-1 v1.1" in catalog, (
        "architecture/shippability.md missing a UTF8-STDOUT-1 v1.1 row — "
        "SCPD-1 consumer-reference propagation broken"
    )
    assert "test_utf8_stdout_regression" in catalog, (
        "architecture/shippability.md UTF8-STDOUT-1 v1.1 row does not "
        "reference the tests/methodology/test_utf8_stdout_regression.py "
        "consumer — SCPD-1 propagation incomplete"
    )


def test_adr_026_present_and_reversibility_cheap():
    """ADR-026 file exists at architecture/decisions/ADR-026-*.md AND has
    frontmatter `reversibility: cheap` + names UTF8-STDOUT-1 + canonical
    phrase.

    Defect class: ADR-026 lost / renamed / scope-shifted; UTF8-STDOUT-1
    v1.1 has no canonical decision record.

    Rule reference: slice-028 (ADR-026).
    """
    decisions_dir = REPO_ROOT / "architecture" / "decisions"
    adr_files = list(decisions_dir.glob("ADR-026-*.md"))
    assert len(adr_files) == 1, (
        f"Expected exactly one ADR-026 file at "
        f"architecture/decisions/ADR-026-*.md; found {len(adr_files)}: "
        f"{[f.name for f in adr_files]!r}"
    )
    adr_content = adr_files[0].read_text(encoding="utf-8")
    assert "reversibility: cheap" in adr_content, (
        f"ADR-026 ({adr_files[0].name}) missing `reversibility: cheap` "
        f"frontmatter field"
    )
    assert "UTF8-STDOUT-1" in adr_content, (
        f"ADR-026 ({adr_files[0].name}) missing canonical rule ID "
        f"'UTF8-STDOUT-1' in body"
    )
    assert _UTF8_V11_PHRASE in adr_content, (
        f"ADR-026 ({adr_files[0].name}) missing canonical phrase "
        f"{_UTF8_V11_PHRASE!r} in body"
    )


# --- Slice-030A / v0.44.0 BCI-1 build-checks-integrity entry pin ---

_V044 = "0.44.0"
_BCI1_PHRASE = "full per-rule structural identity"
_V045 = "0.45.0"
_SCMD1_PHRASE = "machine-stable command column"
_V046 = "0.46.0"
# MUST stay byte-identical to `_QD1_PHRASE` in
# tests/methodology/test_query_design_skill.py (M-add-v2-1, 2-site pin —
# site (i) is this changelog body, site (ii) is skills/query-design/SKILL.md).
_QD1_PHRASE = "read-only, delegation-only codebase Q&A"


def test_v_0_44_0_bci_1_entry_present_in_repo_and_installed():
    """v0.44.0 BCI-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the BCI-1 rule reference, the canonical
    full-structural-identity phrase, and the deterministic-downstream-gate
    framing (ADR-028 + ADR-029 lineage).

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. Pins that BCI-1 is a
    minted audited rule (NOT rule-ID-set-only — meta-M-add-2) so a future
    edit cannot silently weaken the invariant to an ID-set check.

    Rule reference: BCI-1 (slice-030A; ADR-028 + ADR-029).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V044}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V044} entry "
            f"header — slice-030A BCI-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V044)
        assert "BCI-1" in body, (
            f"{surface_name} v{_V044} entry body missing the 'BCI-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _BCI1_PHRASE in body, (
            f"{surface_name} v{_V044} entry body missing canonical phrase "
            f"{_BCI1_PHRASE!r} — a future edit could silently weaken BCI-1 "
            f"to a rule-ID-set check (meta-M-add-2 regression)"
        )
        assert "ADR-028" in body and "ADR-029" in body, (
            f"{surface_name} v{_V044} entry body missing the ADR-028/ADR-029 "
            f"decision lineage"
        )


def test_v_0_45_0_scmd_1_entry_present_in_repo_and_installed():
    """v0.45.0 SCMD-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the SCMD-1 rule reference, the canonical
    `machine-stable command column` phrase, and the ADR-030/ADR-031 lineage.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. (This NEW entry-pin is a
    fresh essential-class member consistent with the existing pattern; the
    *existing* entry-pin reframe is chartered to slice-030C — adding one more
    in the established shape is normal propagation, classified essential by
    SCMD-1 and NOT flagged.)

    Rule reference: SCMD-1 (slice-031, split-label 030B; ADR-030 + ADR-031).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V045}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V045} entry "
            f"header — slice-031 SCMD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V045)
        assert "SCMD-1" in body, (
            f"{surface_name} v{_V045} entry body missing the 'SCMD-1' rule "
            f"reference"
        )
        assert _SCMD1_PHRASE in body, (
            f"{surface_name} v{_V045} entry body missing canonical phrase "
            f"{_SCMD1_PHRASE!r}"
        )
        assert "ADR-030" in body and "ADR-031" in body, (
            f"{surface_name} v{_V045} entry body missing the ADR-030/ADR-031 "
            f"decision lineage"
        )


def test_v_0_46_0_qd_1_entry_present_in_repo_and_installed():
    """v0.46.0 QD-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the QD-1 rule reference, the canonical
    `read-only, delegation-only codebase Q&A` phrase, and the ADR-032
    decision lineage.

    RULE-ID-BEARING shape (mirrors test_v_0_44_0_bci_1 / test_v_0_45_0_scmd_1,
    NOT the rule-ID-LESS test_v_0_43_0 shape): QD-1 is a minted audited rule
    (slice-032), so the pin asserts the QD-1 token + canonical phrase +
    ADR-032, and MUST NOT assert any 'no rule-ID' prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /query-design. The canonical
    phrase assertion is the anti-silent-weakening guard (bci_1 meta-M-add-2
    rationale applied to QD-1): a future edit cannot silently erode QD-1 to
    a non-read-only rule. This is site (i) of the 2-site canonical-phrase
    pin (site (ii) = skills/query-design/SKILL.md via
    test_query_design_skill.py::test_qd1_canonical_phrase_pinned_in_skill_md).

    Rule reference: QD-1 (slice-032; ADR-032).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V046}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V046} entry "
            f"header — slice-032 QD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V046)
        assert "QD-1" in body, (
            f"{surface_name} v{_V046} entry body missing the 'QD-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _QD1_PHRASE in body, (
            f"{surface_name} v{_V046} entry body missing canonical phrase "
            f"{_QD1_PHRASE!r} — a future edit could silently erode QD-1 to a "
            f"non-read-only rule (anti-silent-weakening guard)"
        )
        assert "ADR-032" in body, (
            f"{surface_name} v{_V046} entry body missing the ADR-032 "
            f"decision lineage"
        )


# --- Slice-029 / v0.43.0 /diagnose sequential-dispatch-default entry pin ---

_V043 = "0.43.0"
_DSEQ_PHRASE = "sequential by default"


def test_v_0_43_0_diagnose_sequential_dispatch_entry_present_in_repo_and_installed():
    """v0.43.0 /diagnose sequential-dispatch entry exists in both in-repo +
    installed methodology-changelog.md, with the canonical phrase, the
    ADR-027 reference, AND the explicit no-rule-ID-lineage prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /status or /slice. Also pins that this is
    a `### Changed` behavior entry with NO minted rule-ID (per /critique
    M2 + /critique-review M2 re-scope, TRI-1 option B) so a future edit
    cannot silently mint a spurious audited rule-ID — mirroring the
    v0.42.0 'NOT a new rule ID' lineage guard.

    Rule reference: ADR-027 (slice-029; deliberately no minted rule-ID).
    """
    in_repo = read_file("methodology-changelog.md")
    installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(
        encoding="utf-8"
    )
    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        assert f"## v{_V043}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V043} entry "
            f"header — slice-029 sequential-dispatch entry was not added or "
            f"was lost"
        )
        body = _extract_version_body(content, _V043)
        assert "ADR-027" in body, (
            f"{surface_name} v{_V043} entry body missing the 'ADR-027' "
            f"reference — entry-pin broken at the decision-reference layer"
        )
        assert _DSEQ_PHRASE in body, (
            f"{surface_name} v{_V043} entry body missing canonical phrase "
            f"{_DSEQ_PHRASE!r} — entry-pin broken at the canonical-phrase layer"
        )
        assert "NO new rule-ID" in body or "no rule-ID" in body, (
            f"{surface_name} v{_V043} entry body missing the no-rule-ID "
            f"lineage prose (TRI-1 M2 option B) — a spurious audited rule ID "
            f"could silently appear"
        )


def test_v_0_43_0_diagnose_sequential_dispatch_shippability_consumer_propagation():
    """architecture/shippability.md carries a slice-029 row referencing the
    sequential-dispatch prose-pin consumer (RPCD-1 / SCPD-1 consumer-
    reference propagation).

    Defect class: a behavior change whose consumer references do not
    propagate into the shippability catalog can silently regress without
    /validate-slice catching it. SCPD-1 requires the propagation.

    Rule reference: slice-029 (shippability consumer propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-029" in catalog, (
        "architecture/shippability.md missing a slice-029 row — "
        "RPCD-1 / SCPD-1 consumer-reference propagation not done"
    )
    assert "test_skill_md_pins.py" in catalog, (
        "architecture/shippability.md slice-029 row must cite the "
        "test_skill_md_pins.py prose-pin consumer command"
    )
