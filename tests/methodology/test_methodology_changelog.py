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
    /pulse surfacing and downstream tooling that parses the file.
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

    Defect class: Drift between VERSION and changelog headers means /pulse
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

def test_v_0_22_0_cad_1_entry_present_in_repo():
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


# --- Slice-008 / BC-1 v1.2 entry pinning ---

def test_v_0_23_0_bc_1_v_1_2_entry_present_in_repo():
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


# --- Slice-009 / CCC-1 v1.1 entry pinning ---

def test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo():
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


# --- Slice-010 / MCT-1 entry pinning (re-added at slice-011 validation: entry pins persist across version supersessions; only PMI-1 version-gate test supersedes) ---

def test_v_0_25_0_mct_1_entry_present_in_repo():
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


# --- Slice-011 / RSAD-1 entry pinning ---

def test_v_0_26_0_rsad_1_entry_present_in_repo():
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


# --- Slice-012 / BC-PROJ-2 entry pinning ---

def test_v_0_27_0_bc_proj_2_entry_present_in_repo():
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


# --- Slice-013 / EPGD-1 entry pinning ---

def test_v_0_28_0_epgd_1_entry_present_in_repo():
    """methodology-changelog v0.28.0 / EPGD-1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no EPGD-1 discipline visible to /pulse).

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


# --- Slice-014 / PMI-1 v1.1 entry pinning ---

def test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo():
    """methodology-changelog v0.29.0 / PMI-1 v1.1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no PMI-1 v1.1 refactor visible to /pulse).

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


def test_v_0_29_0_entry_names_supersession_pattern_retired():
    """methodology-changelog v0.29.0 entry MUST contain the canonical phrase
    `supersession pattern retired at slice-014` in BOTH in-repo + installed
    surfaces.

    Defect class (slice-014-specific): the PMI-1 versioned-gate supersession
    counter ran at N=6 events stable across slices 007-013 (slice-007
    introduced _at_0_22_0; slices 008-013 superseded sequentially). At
    slice-014 the pattern is retired: future slices' version bumps do NOT
    supersede the gate function. The v0.29.0 changelog entry MUST annotate
    this termination explicitly so future readers + /pulse + /critique
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

def test_v_0_30_0_scpd_1_entry_present_in_repo():
    """methodology-changelog v0.30.0 / SCPD-1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no SCPD-1 codification visible to /pulse).

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

def test_v_0_31_0_rpcd_1_entry_present_in_repo():
    """methodology-changelog v0.31.0 / RPCD-1 entry must exist in BOTH
    the in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no RPCD-1 codification visible to /pulse).

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


def test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo():
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

    for surface_name, content in [("in-repo", in_repo)]:
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

def test_v_0_32_0_tphd_1_entry_present_in_repo():
    """methodology-changelog v0.32.0 / TPHD-1 entry must exist in BOTH the
    in-repo file AND the installed `~/.claude/methodology-changelog.md`.

    Defect class (per slice-006 B1 + slice-007 CAD-1, generalized): if the
    entry exists only in-repo and the forward-sync was forgotten, every
    future read of the installed methodology-changelog reads stale
    methodology (no TPHD-1 codification visible to /pulse).

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


def test_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo():
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

    for surface_name, content in [("in-repo", in_repo)]:
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

    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_33_0_layer_evid_1_entry_present_in_repo():
    """methodology-changelog v0.33.0 / LAYER-EVID-1 entry MUST be present in
    both in-repo and installed copies of methodology-changelog.md,
    bidirectionally sha256 byte-equal at slice-019 ship hash (N=14 -> N=15
    forensic capture).

    Defect class (per slice-019 /critique B1 + AC #3): forgotten
    forward-sync after in-repo edit leaves installed methodology-changelog
    stale; /critic-calibrate + /pulse surfacing references stale data;
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

    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_34_0_bfrd_1_entry_present_in_repo():
    """v0.34.0 BFRD-1 entry exists in both in-repo + installed methodology-
    changelog.md with bidirectional sha256 byte-equality (CAD-1 invariant).

    Defect class: if the in-repo and installed copies diverge, Claude reads
    stale prose at /pulse or /slice invocation. Bidirectional pin enforced
    by reading both files and asserting both contain the v0.34.0 entry
    header.
    Rule reference: BFRD-1 (slice-020 AC #1).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_35_0_branch_1_entry_present_in_repo():
    """v0.35.0 BRANCH-1 entry exists in both in-repo + installed methodology-
    changelog.md.

    Defect class: if the in-repo and installed copies diverge, Claude reads
    stale prose at /pulse or /slice invocation. Bidirectional pin enforced
    by reading both files and asserting both contain the v0.35.0 entry
    header AND the BRANCH-1 rule ID.

    Rule reference: BRANCH-1 (slice-021 AC #5).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V035}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V035} entry "
            f"header — slice-021 BRANCH-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V035)
        assert "BRANCH-1" in body, (
            f"{surface_name} v{_V035} entry body missing rule-ID 'BRANCH-1' — "
            f"entry-pin broken at the rule-ID layer"
        )


def test_v_0_35_0_branch_1_entry_names_three_sub_modes_in_repo():
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


def test_v_0_36_0_pr_aware_commit_slice_entry_present_in_repo():
    """v0.36.0 PR-aware /commit-slice entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge, Claude
    reads stale prose at /pulse or /slice. Enforced by reading both and
    asserting both contain the v0.36.0 entry header AND the canonical phrase.

    Rule reference: slice-022 AC #5 (methodology-changelog v0.36.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_36_0_entry_names_three_modes_in_repo():
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


def test_v_0_37_0_utf8_stdout_1_entry_present_in_repo():
    """v0.37.0 UTF8-STDOUT-1 entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge, Claude
    reads stale prose at /pulse or /slice. Enforced by reading both and
    asserting both contain the v0.37.0 entry header AND the canonical phrase.

    Rule reference: slice-023 AC #5 (methodology-changelog v0.37.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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
# ADDS-only; 0 of 17 prior _entry_present_in_repo-family functions
# touched). ADR-pin follows the convention N=10 stable (NOT a separate
# tests/decisions/ file).
#
# Section header `# --- Slice-024 / FBCD-1 entry pinning ---` deferred to the
# `# ===` border + description comment style established at slice-021/022/023
# (empirical reality vs design.md's `# ---` hint per CLAUDE.md "code is truth").


_V038 = "0.38.0"
_V039 = "0.39.0"
_V040 = "0.40.0"


def test_v_0_38_0_fbcd_1_entry_present_in_repo():
    """v0.38.0 FBCD-1 entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge, Claude
    reads stale prose at /pulse or /slice. Enforced by reading both and
    asserting both contain the v0.38.0 entry header AND the canonical phrase.

    Rule reference: slice-024 AC #3 (methodology-changelog v0.38.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_39_0_ptfcd_1_entry_present_in_repo():
    """v0.39.0 PTFCD-1 entry exists in both in-repo + installed
    methodology-changelog.md.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. Enforced by reading both
    and asserting both contain the v0.39.0 entry header AND the canonical
    rule ID AND the canonical phrase.

    Rule reference: slice-025 AC #4 (methodology-changelog v0.39.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_40_0_crp_1_entry_present_in_repo():
    """v0.40.0 CRP-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the canonical rule ID + canonical phrase
    + the NON-`-D` audit-enforced-gate naming-class conformance prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. Also pins the B1
    correction (CRP-1 is audit-enforced, NON-`-D`, per ADR-019) so a future
    edit cannot silently reintroduce a `-D` naming-class contradiction.

    Rule reference: slice-026 AC #3 (methodology-changelog v0.40.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_41_0_pca_1_entry_present_in_repo():
    """v0.41.0 PCA-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the canonical rule ID + canonical
    phrase + the NON-`-D` audit-enforced-gate naming-class conformance
    prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. Also pins the
    audit-enforced / NON-`-D` (per ADR-019) conformance so a future edit
    cannot silently reintroduce a `-D` naming-class contradiction.

    Rule reference: slice-027 AC #5 (methodology-changelog v0.41.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_42_0_utf8_stdout_1_v1_1_entry_present_in_repo():
    """v0.42.0 UTF8-STDOUT-1 v1.1 entry exists in both in-repo + installed
    methodology-changelog.md, with the canonical rule ID + canonical phrase
    + the rule-ID-lineage-preserved prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. Also pins the rule-ID
    lineage (UTF8-STDOUT-1 v1.1, NOT a new rule ID — mirroring PMI-1 v1.x /
    ADR-013) so a future edit cannot silently mint a spurious new rule ID.
    UTF8-STDOUT-1 v1.1 is a rule-version evolution, not an audit-enforced
    gate — this pin deliberately does NOT assert the NON-`-D` audit-gate
    naming prose (that is CRP-1/PCA-1-class, not applicable here).

    Rule reference: slice-028 AC #5 (methodology-changelog v0.42.0 entry).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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

# --- Slice-033 / v0.47.0 EOL-DRIFT-1 .md-drift-guards-EOL-agnostic entry pin ---
_V047 = "0.47.0"
_EOL_DRIFT1_PHRASE = "content-equal modulo line endings"

# --- Slice-034 / v0.48.0 TFFL-1 TF-1-field-line-robustness entry pin ---
_V048 = "0.48.0"
_TFFL1_PHRASE = "**Test-first** field-line value must be a standalone boolean token"

# --- Slice-035 / v0.49.0 SRCD-1 skill-rename-collision-discipline entry pin ---
_V049 = "0.49.0"
_SRCD1_PHRASE = "skill name MUST NOT collide with a Claude Code built-in command name"

# --- Slice-037 / v0.50.0 PTFFD-1 phantom-test-function-citation entry pin ---
_V050 = "0.50.0"
_PTFFD1_PHRASE = (
    "the cited test FUNCTION (not only the FILE) must exist in an "
    "otherwise-present test file"
)

# --- Slice-038 / v0.51.0 SRSC-1 pinned-shippability-runner entry pin ---
_V051 = "0.51.0"
_SRSC1_PHRASE = "do NOT hand-roll the execution loop"
_SRSC1_REUSE_PHRASE = "reuses SCMD-1 _segments()"


def test_v_0_44_0_bci_1_entry_present_in_repo():
    """v0.44.0 BCI-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the BCI-1 rule reference, the canonical
    full-structural-identity phrase, and the deterministic-downstream-gate
    framing (ADR-028 + ADR-029 lineage).

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. Pins that BCI-1 is a
    minted audited rule (NOT rule-ID-set-only — meta-M-add-2) so a future
    edit cannot silently weaken the invariant to an ID-set check.

    Rule reference: BCI-1 (slice-030A; ADR-028 + ADR-029).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_45_0_scmd_1_entry_present_in_repo():
    """v0.45.0 SCMD-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the SCMD-1 rule reference, the canonical
    `machine-stable command column` phrase, and the ADR-030/ADR-031 lineage.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. (This NEW entry-pin is a
    fresh essential-class member consistent with the existing pattern; the
    *existing* entry-pin reframe is chartered to slice-030C — adding one more
    in the established shape is normal propagation, classified essential by
    SCMD-1 and NOT flagged.)

    Rule reference: SCMD-1 (slice-031, split-label 030B; ADR-030 + ADR-031).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_46_0_qd_1_entry_present_in_repo():
    """v0.46.0 QD-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the QD-1 rule reference, the canonical
    `read-only, delegation-only codebase Q&A` phrase, and the ADR-032
    decision lineage.

    RULE-ID-BEARING shape (mirrors test_v_0_44_0_bci_1 / test_v_0_45_0_scmd_1,
    NOT the rule-ID-LESS test_v_0_43_0 shape): QD-1 is a minted audited rule
    (slice-032), so the pin asserts the QD-1 token + canonical phrase +
    ADR-032, and MUST NOT assert any 'no rule-ID' prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /query-design. The canonical
    phrase assertion is the anti-silent-weakening guard (bci_1 meta-M-add-2
    rationale applied to QD-1): a future edit cannot silently erode QD-1 to
    a non-read-only rule. This is site (i) of the 2-site canonical-phrase
    pin (site (ii) = skills/query-design/SKILL.md via
    test_query_design_skill.py::test_qd1_canonical_phrase_pinned_in_skill_md).

    Rule reference: QD-1 (slice-032; ADR-032).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


def test_v_0_47_0_eol_drift_1_entry_present_in_repo():
    """v0.47.0 EOL-DRIFT-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the EOL-DRIFT-1 rule reference, the
    canonical `content-equal modulo line endings` phrase, and the ADR-033
    decision lineage.

    RULE-ID-BEARING shape (mirrors test_v_0_44_0_bci_1 / test_v_0_45_0_scmd_1
    / test_v_0_46_0_qd_1, NOT the rule-ID-LESS test_v_0_43_0 shape):
    EOL-DRIFT-1 is a minted audited rule (slice-033), so the pin asserts the
    EOL-DRIFT-1 token + canonical phrase + ADR-033, and MUST NOT assert any
    'no rule-ID' prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse. The canonical-phrase assertion is
    the anti-silent-weakening guard (bci_1 meta-M-add-2 rationale applied to
    EOL-DRIFT-1): a future edit cannot silently revert EOL-DRIFT-1 to a
    raw-byte rule. (m-add-1 fix: pin-fn name derives from the minted RULE-ID
    per the v0.46.0 `qd_1` precedent, restoring 007–032 naming parity.)

    Rule reference: EOL-DRIFT-1 (slice-033; ADR-033).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V047}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V047} entry "
            f"header — slice-033 EOL-DRIFT-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V047)
        assert "EOL-DRIFT-1" in body, (
            f"{surface_name} v{_V047} entry body missing the 'EOL-DRIFT-1' "
            f"rule reference — entry-pin broken at the rule-reference layer"
        )
        assert _EOL_DRIFT1_PHRASE in body, (
            f"{surface_name} v{_V047} entry body missing canonical phrase "
            f"{_EOL_DRIFT1_PHRASE!r} — a future edit could silently revert "
            f"EOL-DRIFT-1 to a raw-byte rule (anti-silent-weakening guard)"
        )
        assert "ADR-033" in body, (
            f"{surface_name} v{_V047} entry body missing the ADR-033 "
            f"decision lineage"
        )


def test_v_0_49_0_srcd_1_entry_present_in_repo():
    """v0.49.0 SRCD-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the SRCD-1 rule reference, the canonical
    `skill name MUST NOT collide with a Claude Code built-in command name`
    phrase, and the ADR-035 decision lineage.

    RULE-ID-BEARING shape (mirrors test_v_0_45_0_scmd_1 / test_v_0_46_0_qd_1
    / test_v_0_47_0_eol_drift_1 / test_v_0_48_0_tffl_1, NOT the rule-ID-LESS
    test_v_0_43_0 shape): SRCD-1 is a new minted rule (slice-035) that
    supersedes nothing, so the pin asserts the SRCD-1 token + canonical
    phrase + ADR-035, and MUST NOT assert any 'no rule-ID' prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse. The canonical-phrase assertion is
    the anti-silent-weakening guard (a future edit cannot silently dilute
    SRCD-1 to a soft "try not to collide" suggestion). Pin-fn name derives
    from the minted RULE-ID per the v0.46.0 `qd_1` / v0.47.0 `eol_drift_1` /
    v0.48.0 `tffl_1` precedent (007–035 naming parity).

    Rule reference: SRCD-1 (slice-035; ADR-035; new minted rule, supersedes
    nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V049}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V049} entry "
            f"header — slice-035 SRCD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V049)
        assert "SRCD-1" in body, (
            f"{surface_name} v{_V049} entry body missing the 'SRCD-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _SRCD1_PHRASE in body, (
            f"{surface_name} v{_V049} entry body missing canonical phrase "
            f"{_SRCD1_PHRASE!r} — a future edit could silently dilute SRCD-1 "
            f"to a soft suggestion (anti-silent-weakening guard)"
        )
        assert "ADR-035" in body, (
            f"{surface_name} v{_V049} entry body missing the ADR-035 "
            f"decision lineage"
        )


def test_v_0_48_0_tffl_1_entry_present_in_repo():
    """v0.48.0 TFFL-1 entry exists in both in-repo + installed
    methodology-changelog.md, with the TFFL-1 rule reference, the canonical
    `**Test-first** field-line value must be a standalone boolean token`
    phrase, and the ADR-034 decision lineage.

    RULE-ID-BEARING shape (mirrors test_v_0_45_0_scmd_1 / test_v_0_46_0_qd_1
    / test_v_0_47_0_eol_drift_1, NOT the rule-ID-LESS test_v_0_43_0 shape):
    TFFL-1 is a minted rule (slice-034) that refines TF-1 in place, so the
    pin asserts the TFFL-1 token + canonical phrase + ADR-034, and MUST NOT
    assert any 'no rule-ID' prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse. The canonical-phrase assertion is
    the anti-silent-weakening guard (a future edit cannot silently revert
    TFFL-1 to the `\\b`-over-matching / silent-default-off behavior R-7
    documents). Pin-fn name derives from the minted RULE-ID per the v0.46.0
    `qd_1` / v0.47.0 `eol_drift_1` precedent (007–034 naming parity).

    Rule reference: TFFL-1 (slice-034; ADR-034; refines TF-1, supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V048}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V048} entry "
            f"header — slice-034 TFFL-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V048)
        assert "TFFL-1" in body, (
            f"{surface_name} v{_V048} entry body missing the 'TFFL-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _TFFL1_PHRASE in body, (
            f"{surface_name} v{_V048} entry body missing canonical phrase "
            f"{_TFFL1_PHRASE!r} — a future edit could silently revert TFFL-1 "
            f"to the R-7 silent-default-off behavior (anti-silent-weakening guard)"
        )
        assert "ADR-034" in body, (
            f"{surface_name} v{_V048} entry body missing the ADR-034 "
            f"decision lineage"
        )


# --- Slice-029 / v0.43.0 /diagnose sequential-dispatch-default entry pin ---

_V043 = "0.43.0"
_DSEQ_PHRASE = "sequential by default"


def test_v_0_43_0_diagnose_sequential_dispatch_entry_present_in_repo():
    """v0.43.0 /diagnose sequential-dispatch entry exists in both in-repo +
    installed methodology-changelog.md, with the canonical phrase, the
    ADR-027 reference, AND the explicit no-rule-ID-lineage prose.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse or /slice. Also pins that this is
    a `### Changed` behavior entry with NO minted rule-ID (per /critique
    M2 + /critique-review M2 re-scope, TRI-1 option B) so a future edit
    cannot silently mint a spurious audited rule-ID — mirroring the
    v0.42.0 'NOT a new rule ID' lineage guard.

    Rule reference: ADR-027 (slice-029; deliberately no minted rule-ID).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
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


# --- Slice-037 / v0.50.0 PTFFD-1 entry pin + shippability propagation ---


def test_v_0_50_0_ptffd_1_entry_present_in_repo():
    """v0.50.0 PTFFD-1 entry exists in BOTH in-repo + installed
    methodology-changelog.md, with the PTFFD-1 rule reference, the
    canonical anti-silent-weakening phrase, and the ADR-037 + ADR-038
    decision lineage.

    RULE-ID-BEARING shape (mirrors test_v_0_48_0_tffl_1): PTFFD-1 is a
    minted `-D` rule (slice-037) that refines PTFCD-1 in place, supersedes
    nothing — the pin asserts the PTFFD-1 token + canonical phrase +
    ADR-038, and MUST NOT assert any `PTFCD-1 v1.1` version label (B3 /
    ADR-038: the `vN.N` label is reserved for the NON-`-D` audit-gate
    naming class).

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse. The canonical-phrase assertion is
    the anti-silent-weakening guard (a future edit cannot silently revert
    PTFFD-1 to FILE-level-only — re-opening the slice-025/026/027
    function-level blind spot).

    Rule reference: PTFFD-1 (slice-037; ADR-037 + ADR-038; refines
    PTFCD-1 in place, supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V050}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V050} entry "
            f"header — slice-037 PTFFD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V050)
        assert "PTFFD-1" in body, (
            f"{surface_name} v{_V050} entry body missing the 'PTFFD-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _PTFFD1_PHRASE in body, (
            f"{surface_name} v{_V050} entry body missing canonical phrase "
            f"{_PTFFD1_PHRASE!r} — a future edit could silently revert "
            f"PTFFD-1 to FILE-level-only (anti-silent-weakening guard)"
        )
        assert "ADR-038" in body, (
            f"{surface_name} v{_V050} entry body missing the ADR-038 "
            f"decision lineage (the -D-vs-vN.N rule-ID decision)"
        )
        assert "supersedes nothing" in body, (
            f"{surface_name} v{_V050} entry must state PTFFD-1 supersedes "
            f"nothing (refines PTFCD-1 in place — lineage preserved)"
        )


def test_v_0_50_0_ptffd_1_shippability_consumer_propagation():
    """architecture/shippability.md carries a PTFFD-1 row whose Machine-cmd
    references the function-level consumer tests (RPCD-1 / SCPD-1
    consumer-reference propagation).

    Defect class: a new audit rule whose consumer references do not
    propagate into the shippability catalog can silently regress without
    /validate-slice catching it. SCPD-1 requires the propagation.

    Rule reference: slice-037 AC5 (shippability consumer propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "PTFFD-1" in catalog, (
        "architecture/shippability.md missing a PTFFD-1 row — SCPD-1 "
        "consumer-reference propagation broken"
    )
    assert "test_ptffd1_test_first_audit.py" in catalog, (
        "architecture/shippability.md PTFFD-1 row does not reference the "
        "test_ptffd1_test_first_audit.py consumer — SCPD-1 propagation "
        "incomplete"
    )
    assert "test_ptffd1_shippability_path_audit.py" in catalog, (
        "architecture/shippability.md PTFFD-1 row does not reference the "
        "test_ptffd1_shippability_path_audit.py consumer — SCPD-1 "
        "propagation incomplete"
    )


# --- Slice-038 / v0.51.0 SRSC-1 entry pin + shippability propagation ---


def test_v_0_51_0_srsc_1_entry_present_in_repo():
    """v0.51.0 SRSC-1 entry exists in BOTH in-repo + installed
    methodology-changelog.md, with the SRSC-1 rule reference, the canonical
    anti-silent-weakening phrases, the ADR-039 decision lineage, and the
    'supersedes nothing' clause.

    NON-`-D` RULE-ID-bearing shape (mirrors test_v_0_50_0_ptffd_1): SRSC-1 is
    a NEW non-`-D` `vN.N` audit/runner-gate-class rule (slice-038) that does
    NOT refine SCMD-1 and supersedes nothing — the pin asserts the SRSC-1
    token + canonical phrases + ADR-039 + 'supersedes nothing'.

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse. The canonical-phrase assertions are
    the anti-silent-weakening guard: a future edit cannot silently revert
    SRSC-1 to a prose-only ('hand-rolled loop is fine') or re-derived
    ('the runner reimplements the split-strip') form — re-opening the R-8
    false-FAIL class.

    Rule reference: SRSC-1 (slice-038; ADR-039; new non-`-D` `vN.N` rule,
    does NOT refine SCMD-1, supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V051}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V051} entry "
            f"header — slice-038 SRSC-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V051)
        assert "SRSC-1" in body, (
            f"{surface_name} v{_V051} entry body missing the 'SRSC-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _SRSC1_PHRASE in body, (
            f"{surface_name} v{_V051} entry body missing canonical phrase "
            f"{_SRSC1_PHRASE!r} — a future edit could silently revert SRSC-1 "
            f"to a prose-only hand-rolled loop (anti-silent-weakening guard)"
        )
        assert _SRSC1_REUSE_PHRASE in body, (
            f"{surface_name} v{_V051} entry body missing canonical phrase "
            f"{_SRSC1_REUSE_PHRASE!r} — a future edit could silently let the "
            f"runner re-derive the split-strip (CSP-1 divergence guard)"
        )
        assert "ADR-039" in body, (
            f"{surface_name} v{_V051} entry body missing the ADR-039 "
            f"decision lineage"
        )
        assert "supersedes nothing" in body, (
            f"{surface_name} v{_V051} entry must state SRSC-1 supersedes "
            f"nothing (new non-`-D` rule, does NOT refine SCMD-1)"
        )


def test_v_0_51_0_srsc_1_shippability_consumer_propagation():
    """architecture/shippability.md carries an SRSC-1 row whose Machine-cmd
    references the runner-segment-contract consumer test (RPCD-1 / SCPD-1
    consumer-reference propagation).

    Defect class: a new audit/runner rule whose consumer references do not
    propagate into the shippability catalog can silently regress without
    /validate-slice catching it. SCPD-1 requires the propagation.

    Rule reference: slice-038 AC4 (shippability consumer propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "SRSC-1" in catalog, (
        "architecture/shippability.md missing an SRSC-1 row — SCPD-1 "
        "consumer-reference propagation broken"
    )
    assert "test_shippability_runner_segment_contract.py" in catalog, (
        "architecture/shippability.md SRSC-1 row does not reference the "
        "test_shippability_runner_segment_contract.py consumer — SCPD-1 "
        "propagation incomplete"
    )


# --- Slice-039 / v0.52.0 APED-1 + MEPD-1 entry pin + SCPD-1 propagation ---

_V052 = "0.52.0"
# Canonical anti-silent-weakening phrases (slice-037 M-add-1 law): if a future
# edit silently weakens the obligation, _extract_version_body loses the phrase
# and the entry-pin FAILs (not a tautological byte-equality green).
_APED1_PHRASE = "Bash-execute a changed audit parse-rule against an adversarial battery"
_MEPD1_PHRASE = "verified against the actual `tests/methodology/test_methodology_changelog.py`"


def test_v_0_52_0_aped_1_entry_present_in_repo():
    """v0.52.0 APED-1 entry exists in BOTH in-repo + installed
    methodology-changelog.md, with the APED-1 rule reference, the canonical
    anti-silent-weakening phrase, the ADR-040 + ADR-041 lineage, and the
    'supersedes nothing' clause.

    NEW minted `-D` RULE-ID shape (mirrors test_v_0_50_0_ptffd_1): APED-1 is
    a new minted `-D` rule (slice-039) that refines nothing and supersedes
    nothing — the pin asserts the APED-1 token + canonical phrase + ADR-040
    + 'supersedes nothing', and MUST NOT assert any `vN.N` label (ADR-040:
    the `vN.N` label is reserved for the NON-`-D` audit-gate naming class).

    Defect class: bidirectional pin — if in-repo and installed diverge,
    Claude reads stale prose at /pulse. The canonical-phrase assertion is
    the anti-silent-weakening guard (a future edit cannot silently revert
    APED-1's Bash-execute obligation to reason-only).

    Rule reference: APED-1 (slice-039; ADR-040 + ADR-041; refines nothing,
    supersedes nothing; 2026-05-17 /critic-calibrate Proposal 1).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V052}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V052} entry "
            f"header — slice-039 APED-1/MEPD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V052)
        assert "APED-1" in body, (
            f"{surface_name} v{_V052} entry body missing the 'APED-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _APED1_PHRASE in body, (
            f"{surface_name} v{_V052} entry body missing canonical phrase "
            f"{_APED1_PHRASE!r} — a future edit could silently weaken APED-1 "
            f"from Bash-execute to reason-only (anti-silent-weakening guard)"
        )
        assert "ADR-040" in body, (
            f"{surface_name} v{_V052} entry body missing the ADR-040 "
            f"decision lineage (the -D-vs-vN.N + behavioral-class decision)"
        )
        assert "supersedes nothing" in body, (
            f"{surface_name} v{_V052} entry must state APED-1 supersedes "
            f"nothing (new minted -D rule — lineage clean)"
        )


def test_v_0_52_0_mepd_1_entry_present_in_repo():
    """v0.52.0 MEPD-1 entry exists in BOTH in-repo + installed
    methodology-changelog.md, with the MEPD-1 rule reference, the canonical
    anti-silent-weakening phrase (the (b)-branch verified-against-artifact
    obligation), the ADR-040 lineage, and the 'supersedes nothing' clause.

    NEW minted `-D` RULE-ID shape — MEPD-1 is the FIRST deliberately
    non-Dim-9 `-D` rule (ADR-040: the `-D` suffix denotes the behavioral
    class "/critique-time prose-heuristic discipline", NOT Dim-9 membership).

    Defect class: bidirectional pin + the canonical-phrase assertion is the
    anti-silent-weakening guard — a future edit cannot silently drop the
    (b)-branch "verified against the actual enforcing assertion" obligation
    (which would re-open the slice-032 m1 false-precedent rubber-stamp).

    Rule reference: MEPD-1 (slice-039; ADR-040 + ADR-041; first non-Dim-9
    `-D` rule, refines nothing, supersedes nothing; 2026-05-17
    /critic-calibrate Proposal 2).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert f"## v{_V052}" in content, (
            f"{surface_name} methodology-changelog.md missing v{_V052} entry "
            f"header — slice-039 APED-1/MEPD-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, _V052)
        assert "MEPD-1" in body, (
            f"{surface_name} v{_V052} entry body missing the 'MEPD-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert _MEPD1_PHRASE in body, (
            f"{surface_name} v{_V052} entry body missing canonical phrase "
            f"{_MEPD1_PHRASE!r} — a future edit could silently drop the "
            f"(b)-branch verified-against-artifact obligation"
        )
        assert "ADR-040" in body, (
            f"{surface_name} v{_V052} entry body missing the ADR-040 "
            f"decision lineage (first non-Dim-9 `-D` rule decision)"
        )
        assert "supersedes nothing" in body, (
            f"{surface_name} v{_V052} entry must state MEPD-1 supersedes "
            f"nothing (new minted -D rule — lineage clean)"
        )


def test_v_0_52_0_critique_proposals_shippability_consumer_propagation():
    """architecture/shippability.md (i) has ZERO surviving
    `::test_critique_dim_9_lists_eleven_sub_clauses` SELECTOR tokens, (ii)
    carries `::test_critique_dim_9_lists_twelve_sub_clauses` in all 14 LIVE
    selector positions, (iii) PRESERVES the frozen line-34 slice-025
    `_lists_ten → _lists_eleven` historical-narrative occurrence UNCHANGED,
    and (iv) carries a v0.52.0 APED-1/MEPD-1 catalog row.

    DR-1 meta-Critic M-add-1 reformulation (supersedes the original Critic-m2
    `"_lists_eleven_sub_clauses" not in catalog` formulation, which was a
    GUARANTEED false-FAIL on the legitimately-preserved line-34 frozen
    narrative): the selector-prefix `::test_critique_dim_9_` is the
    discriminator between a LIVE pytest selector token (rename target) and
    the frozen backticked prose narrative (a bare backticked
    _lists_eleven_sub_clauses with NO ::test_critique_dim_9_ prefix)
    (slice-025's own ten→eleven supersession record — preserving it is the
    same frozen-history class as the changelog:266 v0.39.0 occurrence).

    Defect class: a structural-invariant supersession whose consumer
    references don't propagate (SCPD-1) silently regresses at /validate-slice;
    AND a blanket substring rename corrupts the frozen slice-025 history
    (M-add-1). Both are pinned here.

    Rule reference: SCPD-1 (slice-015) + APED-1/MEPD-1 (slice-039 AC5;
    DR-1 M-add-1 selector-token discriminator).
    """
    catalog = read_file("architecture/shippability.md")
    LIVE_OLD = "::test_critique_dim_9_lists_eleven_sub_clauses"
    LIVE_NEW = "::test_critique_dim_9_lists_twelve_sub_clauses"
    FROZEN = "`_lists_ten_sub_clauses` -> `_lists_eleven_sub_clauses`"
    # (i) zero surviving LIVE old selector tokens.
    assert LIVE_OLD not in catalog, (
        f"architecture/shippability.md still carries a LIVE "
        f"{LIVE_OLD!r} selector token — SCPD-1 propagation incomplete "
        f"(the `_lists_eleven`→`_lists_twelve` rename did not reach every "
        f"live pytest selector)"
    )
    # (ii) propagation floor: ≥14 LIVE new selector tokens (the 7 propagated
    # rows 6/11/13/15/16/24/25 = 6 rows × 2 + line-34 row × 2 = 14, the
    # mechanically-verified M-add-1 map). It is `>= 14` not `== 14` because
    # row 39 (this slice's own SCPD-1 consumer-propagation row) legitimately
    # re-cites the superseded `_lists_twelve` count test in its validation
    # battery (Command + Machine-cmd cells = +2). Assertion (i) — zero
    # surviving LIVE *old* selector tokens — is the load-bearing
    # propagation-complete guarantee; this floor guards under-propagation.
    n_new = catalog.count(LIVE_NEW)
    assert n_new >= 14, (
        f"expected ≥14 LIVE {LIVE_NEW!r} selector tokens "
        f"(7 propagated rows: 6 rows × 2 + line-34 row × 2 = 14 floor; "
        f"+2 for row 39's own battery), found {n_new} — SCPD-1 "
        f"propagation incomplete (M-add-1 mechanical map under-propagated)"
    )
    # (iii) the frozen line-34 slice-025 historical narrative is PRESERVED.
    assert FROZEN in catalog, (
        f"the frozen line-34 slice-025 {FROZEN!r} historical-narrative "
        f"occurrence was renamed — this CORRUPTS slice-025's own ten→eleven "
        f"supersession record (DR-1 M-add-1 frozen-history preservation)"
    )
    # (iv) the new v0.52.0 APED-1/MEPD-1 catalog row exists.
    assert "APED-1" in catalog and "MEPD-1" in catalog, (
        "architecture/shippability.md missing the v0.52.0 APED-1/MEPD-1 "
        "catalog row — SCPD-1 consumer-reference propagation for the two "
        "new rules incomplete"
    )


def test_v_0_53_0_mcfs_1_entry_present_in_repo():
    """methodology-changelog v0.53.0 / MCFS-1 entry-pin.

    **In-repo-only body (M3 / slice-041, split-lineage label "030C")**: per
    ADR-042 + ADR-043 the per-version installed-changelog read-leg is
    decoupled (forward-sync re-homed onto the non-catalog MCFS-1 gate
    `tools/methodology_changelog_forward_sync.py`); this entry-pin therefore
    asserts ONLY the git-tracked in-repo entry (the META-1 invariant) and
    reads NO `Path.home()` path, so `shippability_decoupling_audit.classify_fn`
    classifies it `clean` — authoring it in the old installed-reading shape
    would re-introduce an essential-class cited fn and self-violate AC3
    (slice-037 three-layer self-application). The installed↔in-repo
    forward-sync of THIS very entry is covered by MCFS-1's whole-file
    content-equality gate, not by a per-version installed read here.

    The name was realigned by slice-042 — the chartered follow-up
    identifier-truth slice that slice-041's TRI-1 scope-cut deferred this
    rename to. The over-claiming `_and_installed` suffix was dropped so the
    name asserts exactly what the body checks: in-repo presence only.
    ADR-044 holds the canonical pre-rename→post-rename mapping; ADR-045 the
    live-vs-frozen boundary that kept shipped history intact.

    Defect class: the v0.53.0 MCFS-1 entry silently lost / never added →
    R-4-retirement provenance + the MCFS-1 rule reference unrecoverable from
    the changelog; bidirectional forward-sync now enforced by MCFS-1, not
    this pin.

    Rule reference: MCFS-1 (slice-041; ADR-042 + ADR-043; new minted rule,
    refines nothing, supersedes nothing; completes the slice-030 split
    030A→030B→030C, retires R-4).
    """
    in_repo = read_file("methodology-changelog.md")
    for surface_name, content in [("in-repo", in_repo)]:
        assert "## v0.53.0" in content, (
            f"{surface_name} methodology-changelog.md missing v0.53.0 entry "
            f"header — slice-041 MCFS-1 entry was not added or was lost"
        )
        body = _extract_version_body(content, "0.53.0")
        assert "MCFS-1" in body, (
            f"{surface_name} v0.53.0 entry body missing the 'MCFS-1' rule "
            f"reference — entry-pin broken at the rule-reference layer"
        )
        assert "the read **registered** not **absent**" in body, (
            f"{surface_name} v0.53.0 entry body missing the canonical R-4 "
            f"charter phrase 'the read **registered** not **absent**' — a "
            f"future edit could silently drop the closed-world-allowlist "
            f"rationale that distinguishes MCFS-1 from rev-1's falsified "
            f"empty-allowlist branch"
        )
        assert "ADR-042" in body and "ADR-043" in body, (
            f"{surface_name} v0.53.0 entry body missing the ADR-042/ADR-043 "
            f"decision lineage"
        )
        assert "supersedes nothing" in body, (
            f"{surface_name} v0.53.0 entry must state MCFS-1 supersedes "
            f"nothing (new minted rule — lineage clean)"
        )


def test_v_0_53_0_mcfs_1_shippability_consumer_propagation():
    """SCPD-1/RPCD-1 consumer-reference propagation: the MCFS-1 rule's
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #41) so the slice-041 critical path can never silently
    regress (RPCD-1: every new audit rule propagates into the shippability
    catalog).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Defect class: the v0.53.0 MCFS-1 catalog row dropped / never added →
    the decouple + closed-world-allowlist + R-4 retirement regress
    undetected by `/validate-slice`'s catalog runner (the exact
    slice-038→R-10 ~5-slice detection-latency class the slice-040 lesson
    warns about).

    Rule reference: MCFS-1 (slice-041; ADR-042 + ADR-043; RPCD-1/SCPD-1
    consumer-reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "| 41 | slice-041-reframe-installed-pin-forward-sync-invariant" \
        in catalog, (
            "architecture/shippability.md missing catalog row #41 for "
            "slice-041 — RPCD-1/SCPD-1 MCFS-1 consumer-reference propagation "
            "incomplete (the /validate-slice catalog runner cannot guard the "
            "MCFS-1 critical path)"
        )
    assert "MCFS-1" in catalog, (
        "architecture/shippability.md row #41 missing the 'MCFS-1' rule "
        "reference — consumer-reference propagation broken at the rule-ID "
        "layer"
    )
    # m-add-2 negative invariant: the MCFS-1 regression suite (reads
    # installed) MUST NOT be catalog-cited — only the in-repo-only entry-pin
    # + this consumer-propagation pin carry the row.
    assert "test_methodology_changelog_forward_sync" not in catalog, (
        "architecture/shippability.md cites the MCFS-1 regression suite — it "
        "reads ~/.claude/methodology-changelog.md and would classify "
        "essential-unregistered (exit 1 self-violation); m-add-2 negative "
        "invariant: the row cites ONLY the in-repo-only-body entry-pin + "
        "this consumer-propagation pin"
    )


def test_v_0_54_0_stp_1_entry_present_in_repo():
    """methodology-changelog v0.54.0 / STP-1 entry-pin.

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean` —
    authoring it in an installed-reading shape would re-introduce an
    essential-class cited fn and self-violate AC3. The installed↔in-repo
    forward-sync of THIS entry is covered by MCFS-1's whole-file gate.

    Defect class: the v0.54.0 STP-1 entry silently lost / never added →
    the STP-1 rule reference + the slice-044 git-independence-deviation
    provenance unrecoverable from the changelog.

    Rule reference: STP-1 (slice-044; ADR-047; new minted NON-`-D` `vN.N`
    audit-gate rule, refines nothing, supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.54.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.54.0 entry header — "
        "slice-044 STP-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.54.0")
    assert "STP-1" in body, (
        "v0.54.0 entry body missing the 'STP-1' rule reference — entry-pin "
        "broken at the rule-reference layer"
    )
    assert "ADR-047" in body, (
        "v0.54.0 entry body missing the ADR-047 decision lineage"
    )
    assert "refines nothing, supersedes nothing" in body, (
        "v0.54.0 entry must state STP-1 refines/supersedes nothing (new "
        "minted rule — lineage clean)"
    )
    assert "git-diff-independent" in body or "git-free" in body, (
        "v0.54.0 entry must record the slice-044 git-independence deviation "
        "(Sub-form B re-spec — the `architecture/`-gitignored root cause)"
    )
    assert "skip-with-" in body and "ADR-037" in body, (
        "v0.54.0 entry must record the per-file-SyntaxError skip-with-note "
        "discipline inherited from ADR-037/PTFFD-1 (targeted-critique B1/B2)"
    )


def test_v_0_54_0_stp_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the STP-1 rule's
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #44) so the slice-044 critical path can never silently
    regress (the slice-040 lesson — an uncatalogued audit's breakage is
    invisible to the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: STP-1 (slice-044; ADR-047; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "| 44 | slice-044-add-state-transition-stale-pin-audit" in catalog, (
        "architecture/shippability.md missing catalog row #44 for slice-044 "
        "— RPCD-1/SCPD-1 STP-1 consumer-reference propagation incomplete "
        "(the /validate-slice catalog runner cannot guard the STP-1 "
        "critical path)"
    )
    assert "STP-1" in catalog, (
        "architecture/shippability.md row #44 missing the 'STP-1' rule "
        "reference — consumer-reference propagation broken at the rule-ID "
        "layer"
    )


# --- Slice-046 / BFRD-1 conditional-confirm-then-auto-invoke entry pinning ---

def test_v_0_55_0_bfrd_1_reclassification_entry_present_in_repo():
    """methodology-changelog v0.55.0 / BFRD-1-reclassification entry-pin.

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate.

    Defect class: the v0.55.0 entry silently lost / never added → the
    BFRD-1 reclassification (STOP-route → conditional confirm-then-auto-
    invoke), its ADR-048 partial-supersession lineage, and the
    no-new-rule treatment become unrecoverable from the changelog.

    Rule reference: BFRD-1 (slice-046; ADR-048 partial-supersedes
    ADR-018 STOP-route decision; refines BFRD-1 terminal action, mints
    no new rule).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.55.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.55.0 entry header — "
        "slice-046 BFRD-1-reclassification entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.55.0")
    assert "conditional confirm-then-auto-invoke" in body, (
        "v0.55.0 entry body missing the canonical phrase "
        "'conditional confirm-then-auto-invoke' — the slice-046 "
        "reclassification's discriminating literal (N=3 surface schema-pin: "
        "SKILL.md Step 3c + this entry + ADR-048)"
    )
    assert "BFRD-1" in body, (
        "v0.55.0 entry body missing the 'BFRD-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-048" in body and "partial-supersedes ADR-018" in body, (
        "v0.55.0 entry body must record the ADR-048 partial-supersession "
        "of ADR-018's STOP-route decision (lineage)"
    )
    assert "refines BFRD-1 terminal action, mints no new rule" in body, (
        "v0.55.0 entry must state the no-new-rule treatment (refinement "
        "of BFRD-1's terminal action per the ADR-038/ADR-047 convention)"
    )
    assert "Rule reference" in body, (
        "v0.55.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


# --- Slice-048 / SOAD-1 structured-options-ask discipline entry pinning ---


def test_v_0_56_0_soad_1_entry_present_in_repo():
    """methodology-changelog v0.56.0 / SOAD-1 entry-pin.

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate.

    Defect class: the v0.56.0 entry silently lost / never added → the
    SOAD-1 rule reference, its ADR-050-generalizes-ADR-048 lineage, and
    the new-rule (supersedes-nothing) treatment become unrecoverable
    from the changelog.

    Rule reference: SOAD-1 (slice-048; ADR-050 generalizes ADR-048's
    gate-specific structured-options-ask requirement; mints a new rule;
    supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.56.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.56.0 entry header — "
        "slice-048 SOAD-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.56.0")
    assert "SOAD-1" in body, (
        "v0.56.0 entry body missing the 'SOAD-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-050" in body and "generalizes ADR-048" in body, (
        "v0.56.0 entry body must record the ADR-050 generalization of "
        "ADR-048's gate-specific structured-options-ask requirement "
        "(lineage)"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.56.0 entry must state SOAD-1's new-rule / supersedes-nothing "
        "treatment (lineage clean — generalizes, does not supersede, "
        "ADR-048)"
    )
    assert "Rule reference" in body, (
        "v0.56.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_56_0_soad_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the SOAD-1 rule's
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #48) so the slice-048 critical path can never silently
    regress (the slice-040 lesson — an uncatalogued pin's breakage is
    invisible to the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: SOAD-1 (slice-048; ADR-050; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert "| 48 | slice-048-codify-structured-options-ask-rule" in catalog, (
        "architecture/shippability.md missing catalog row #48 for "
        "slice-048 — RPCD-1/SCPD-1 SOAD-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "SOAD-1 critical path)"
    )
    assert "SOAD-1" in catalog, (
        "architecture/shippability.md row #48 missing the 'SOAD-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


def test_v_0_57_0_osdg_1_entry_present_in_repo():
    """methodology-changelog v0.57.0 / OSDG-1 entry-pin.

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate.

    Defect class: the v0.57.0 entry silently lost / never added → the
    OSDG-1 rule reference, its ADR-051 extends-CAD-1/mini-CAD/EOL-DRIFT-1
    lineage, and the new-rule (supersedes-nothing) treatment become
    unrecoverable from the changelog.

    Rule reference: OSDG-1 (slice-049; ADR-051 extends slice-007 CAD-1 /
    slice-010 mini-CAD / slice-033 EOL-DRIFT-1; mints a new rule;
    supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.57.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.57.0 entry header — "
        "slice-049 OSDG-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.57.0")
    assert "OSDG-1" in body, (
        "v0.57.0 entry body missing the 'OSDG-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-051" in body and "extends" in body, (
        "v0.57.0 entry body must record the ADR-051 extension of the "
        "slice-007 CAD-1 / slice-010 mini-CAD / slice-033 EOL-DRIFT-1 "
        "drift-guard lineage"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.57.0 entry must state OSDG-1's new-rule / supersedes-nothing "
        "treatment (lineage clean — extends, does not supersede, the "
        "CAD-1/mini-CAD/EOL-DRIFT-1 family)"
    )
    assert "Rule reference" in body, (
        "v0.57.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_57_0_osdg_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the OSDG-1 rule's
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #49) so the slice-049 critical path can never silently
    regress (the slice-040 lesson — an uncatalogued pin's breakage is
    invisible to the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: OSDG-1 (slice-049; ADR-051; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 49 | slice-049-add-triage-adopt-skill-drift-guards" in catalog
    ), (
        "architecture/shippability.md missing catalog row #49 for "
        "slice-049 — RPCD-1/SCPD-1 OSDG-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "OSDG-1 critical path)"
    )
    assert "OSDG-1" in catalog, (
        "architecture/shippability.md row #49 missing the 'OSDG-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


# --- Slice-050 / v0.58.0 AVFS-1 entry pin + shippability propagation ---


def test_v_0_58_0_avfs_1_entry_present_in_repo():
    """methodology-changelog v0.58.0 / AVFS-1 entry-pin (content-bearing —
    B1: NOT a thin presence check; STP-1/MCFS-1 entry-pin depth).

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate (NOT a per-version installed read here).

    Defect class: the v0.58.0 entry silently lost / never added → the
    AVFS-1 rule reference, its ADR-052 lineage, the standalone-clone
    (not-folded-into-MCFS-1) decision, and the canonical attribution
    phrase become unrecoverable from the changelog.

    Rule reference: AVFS-1 (slice-050; ADR-052; extends the slice-041
    MCFS-1 forward-sync-via-deterministic-downstream-gate lineage; mints a
    new rule; supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.58.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.58.0 entry header — "
        "slice-050 AVFS-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.58.0")
    assert "AVFS-1" in body, (
        "v0.58.0 entry body missing the 'AVFS-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-052" in body, (
        "v0.58.0 entry body missing the ADR-052 decision lineage"
    )
    assert "supersedes nothing" in body, (
        "v0.58.0 entry must state AVFS-1 mints a new rule / supersedes "
        "nothing (lineage clean — extends, does not supersede, the "
        "MCFS-1 forward-sync-gate lineage)"
    )
    assert "NOT a slice regression" in body, (
        "v0.58.0 entry must carry the canonical attribution phrase 'NOT a "
        "slice regression' (the _ATTRIB rationale a future Builder reads "
        "when AVFS-1 HALTs — a tautological presence check would miss this)"
    )
    assert "standalone" in body and "MCFS-1" in body, (
        "v0.58.0 entry must record the ADR-052 standalone-clone decision "
        "(not folded into MCFS-1's whole-file gate) — the load-bearing "
        "design choice distinguishing the AVFS-1 deliverable"
    )
    assert "Rule reference" in body, (
        "v0.58.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_58_0_avfs_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the AVFS-1 rule's
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #50) so the slice-050 critical path can never silently
    regress (the slice-040 lesson — an uncatalogued pin's breakage is
    invisible to the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: AVFS-1 (slice-050; ADR-052; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 50 | slice-050-add-ai-sdlc-version-forward-sync-gate" in catalog
    ), (
        "architecture/shippability.md missing catalog row #50 for "
        "slice-050 — RPCD-1/SCPD-1 AVFS-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "AVFS-1 critical path)"
    )
    assert "AVFS-1" in catalog, (
        "architecture/shippability.md row #50 missing the 'AVFS-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


# --- Slice-051 / v0.59.0 OSDG-1 reflect-member entry pin + shippability ---


def test_v_0_59_0_osdg_1_reflect_member_entry_present_in_repo():
    """methodology-changelog v0.59.0 / OSDG-1 reflect-member entry-pin
    (content-bearing — M2: NOT a thin presence check; the OSDG-1-membership
    content surface that, with the CLAUDE.md enumeration prose-pin and the
    collected+catalog-rowed drift test, defeats the slice-037 M-add-1
    tautological-green class for the slice's primary deliverable).

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate (NOT a per-version installed read here).

    Defect class: the v0.59.0 entry silently lost / never added → the
    OSDG-1 reflect-membership, its ADR-053-extends-ADR-051/OSDG-1 lineage,
    the no-new-RULE-ID treatment, and the "Opener-Skill name is now a
    historical label not a scope boundary" decoupling become
    unrecoverable from the changelog.

    Rule reference: OSDG-1 (slice-049; ADR-051; member-added at slice-051 /
    ADR-053; extends slice-007 CAD-1 / slice-010 mini-CAD / slice-033
    EOL-DRIFT-1 / slice-049 OSDG-1; mints no new rule; supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.59.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.59.0 entry header — "
        "slice-051 OSDG-1 reflect-member entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.59.0")
    assert "OSDG-1" in body, (
        "v0.59.0 entry body missing the 'OSDG-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-053" in body and "extends" in body, (
        "v0.59.0 entry body must record the ADR-053 extension of the "
        "slice-049/ADR-051 OSDG-1 (and slice-007 CAD-1 / slice-010 "
        "mini-CAD / slice-033 EOL-DRIFT-1) drift-guard lineage"
    )
    assert "reflect" in body, (
        "v0.59.0 entry body missing the 'reflect' member — the entry must "
        "name the in-loop skill added to the OSDG-1 guarded set (M2 "
        "content-bearing membership pin, not a tautological presence check)"
    )
    assert "supersedes nothing" in body and "no new rule" in body, (
        "v0.59.0 entry must state OSDG-1 is extended (no new RULE-ID — the "
        "literal 'no new rule') and supersedes nothing (lineage clean — "
        "extends, does not supersede, the CAD-1/mini-CAD/EOL-DRIFT-1/OSDG-1 "
        "family)"
    )
    assert "historical label" in body, (
        "v0.59.0 entry must record the ADR-053 decoupling — OSDG-1's "
        "'Opener-Skill' name is now a historical label, not a scope "
        "boundary (the guarded set now spans a non-opener in-loop skill); "
        "a tautological presence check would miss this load-bearing note"
    )
    assert "Rule reference" in body, (
        "v0.59.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_59_0_osdg_1_reflect_member_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the OSDG-1
    reflect-member consumer reference MUST propagate into
    `architecture/shippability.md` (catalog row #51) so the slice-051
    critical path can never silently regress (the slice-040 lesson — an
    uncatalogued pin's breakage is invisible to the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: OSDG-1 (slice-049; ADR-051; member-added at slice-051 /
    ADR-053; RPCD-1/SCPD-1 consumer-reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 51 | slice-051-extend-osdg-1-to-reflect-skill" in catalog
    ), (
        "architecture/shippability.md missing catalog row #51 for "
        "slice-051 — RPCD-1/SCPD-1 OSDG-1 reflect-member consumer-reference "
        "propagation incomplete (the /validate-slice catalog runner cannot "
        "guard the OSDG-1 reflect critical path)"
    )
    assert "OSDG-1" in catalog, (
        "architecture/shippability.md row #51 missing the 'OSDG-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


def test_v_0_60_0_obo_entry_present_in_repo():
    """methodology-changelog v0.60.0 / ADR-054 --obo entry-pin
    (content-bearing — NOT a thin presence check; pins the load-bearing
    surface that, with shippability row #52 and the collected
    `test_slice_candidates_obo.py`, defeats the slice-037 M-add-1
    tautological-green class for this slice's primary deliverable).

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`). The
    installed↔in-repo forward-sync of THIS entry is covered by MCFS-1's
    whole-file gate, not a per-version installed read here.

    Defect class: the v0.60.0 entry silently lost / never added → the
    `--obo` capability, the ADR-054 Hard-rule-#2 carve-out, the
    mechanical-not-honour-system scoped-peek enforcement, and the
    behavior-change (Inclusion-heuristic) justification become
    unrecoverable from the changelog.

    Rule reference: ADR-054 (slice-052; bounded /slice-candidates
    Hard-rule-#2 deviation for --obo "Validate then approve"; mints no
    new RULE-ID; supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.60.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.60.0 entry header — "
        "slice-052 --obo / ADR-054 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.60.0")
    assert "ADR-054" in body, (
        "v0.60.0 entry body missing the 'ADR-054' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "--obo" in body and "slice-candidates" in body, (
        "v0.60.0 entry body must name the new --obo mode on /slice-candidates "
        "(content-bearing capability pin, not a tautological presence check)"
    )
    assert "Behavior change" in body, (
        "v0.60.0 entry must state this is a Behavior change (Inclusion "
        "heuristic — 'New skills … qualify'; slice-049/ADR-051 law that a "
        "methodology-surface behavior change with no other bump reason still "
        "takes the ## vN + 4-part PMI-1 bump path)"
    )
    assert "mechanical, not honour-system" in body, (
        "v0.60.0 entry must record that the ADR-054 scoped-peek boundary is "
        "enforced mechanically (--obo-peek Path.resolve() containment), not "
        "by honour-system prose — the M4 load-bearing note"
    )
    assert "supersedes nothing" in body and "NO new RULE-ID" in body, (
        "v0.60.0 entry must state ADR-054 mints no new RULE-ID and supersedes "
        "nothing (lineage clean — a new skill capability + one ADR)"
    )
    assert "Rule reference" in body, (
        "v0.60.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_60_0_obo_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the ADR-054 --obo
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #52) so the slice-052 critical path can never silently
    regress (slice-040 lesson — an uncatalogued pin's breakage is invisible
    to the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: ADR-054 (slice-052; RPCD-1/SCPD-1 consumer-reference
    propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 52 | slice-052-add-slice-candidates-obo-mode" in catalog
    ), (
        "architecture/shippability.md missing catalog row #52 for "
        "slice-052 — RPCD-1/SCPD-1 ADR-054 --obo consumer-reference "
        "propagation incomplete (the /validate-slice catalog runner cannot "
        "guard the --obo operational-parity / scoped-peek critical path)"
    )
    assert "ADR-054" in catalog, (
        "architecture/shippability.md row #52 missing the 'ADR-054' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


# --- Slice-053 / v0.61.0 BCR-1 backlog-round-trip entry pin + shippability ---


def test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo():
    """methodology-changelog v0.61.0 / BCR-1 backlog-round-trip entry-pin
    (content-bearing — slice-051 precedent; NOT a thin presence check; pins
    the load-bearing surface that, with the CLAUDE.md enumeration prose-pin
    and the collected+catalog-rowed `test_bcr_1_backlog_round_trip.py`,
    defeats the slice-037 M-add-1 tautological-green class for the slice's
    primary deliverable).

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate (NOT a per-version installed read here).

    Defect class: the v0.61.0 entry silently lost / never added → the
    BCR-1 minting, its ADR-055-extends-BC-PROJ-10/Inclusion-heuristic
    lineage, the two SKILL.md surfaces it covers (`/slice` consume +
    `/reflect` round-trip), the new-rule-supersedes-nothing treatment, and
    the M4 closes-sentinel trigger refinement all become unrecoverable
    from the changelog.

    Rule reference: BCR-1 (slice-053; ADR-055 extends the BC-PROJ-10 /
    Inclusion-heuristic lineage; mints a new rule; supersedes nothing).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.61.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.61.0 entry header — "
        "slice-053 BCR-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.61.0")
    assert "BCR-1" in body, (
        "v0.61.0 entry body missing the 'BCR-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-055" in body and "extends" in body, (
        "v0.61.0 entry body must record the ADR-055 extension of the "
        "BC-PROJ-10 / Inclusion-heuristic lineage (slice-052)"
    )
    assert "BC-PROJ-10" in body, (
        "v0.61.0 entry body missing the 'BC-PROJ-10' lineage anchor — "
        "the slice-052 Inclusion-heuristic precedent must be cited so "
        "future readers can trace why BCR-1 is in the methodology-surface "
        "behavior-change class"
    )
    assert "Inclusion-heuristic" in body or "Inclusion heuristic" in body, (
        "v0.61.0 entry body missing the 'Inclusion-heuristic' / 'Inclusion "
        "heuristic' anchor — the slice-052 BC-PROJ-10 dischargement law "
        "(this slice IS a methodology-surface behavior change → 4-part "
        "PMI-1 bump path) must be named explicitly"
    )
    assert "/slice" in body and "/reflect" in body, (
        "v0.61.0 entry body missing one or both of the two SKILL.md "
        "surfaces (/slice consume + /reflect round-trip) — the M2 "
        "content-bearing two-surface membership pin, NOT a tautological "
        "presence check"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.61.0 entry must state BCR-1 'mints a new rule' (NOT '-D' "
        "refinement, NOT extension-without-new-RULE-ID) AND 'supersedes "
        "nothing' (lineage clean — extends BC-PROJ-10, does not supersede "
        "the Inclusion-heuristic family)"
    )
    assert "Closes:" in body, (
        "v0.61.0 entry must record the M4 closes-sentinel trigger "
        "refinement — `**Closes:** SC-\\d{3}` sentinel-anchored regex, "
        "NOT bare `SC-\\d{3}` (mentioned-vs-closes disambiguation per "
        "slice-053 /critique M4 ACCEPTED-FIXED)"
    )
    assert "Rule reference" in body, (
        "v0.61.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_61_0_bcr_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the BCR-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #53) so the slice-053 critical path can never silently regress
    (slice-040 lesson — an uncatalogued pin's breakage is invisible to
    the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: BCR-1 (slice-053; ADR-055; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 53 | slice-053-wire-backlog-md-into-slice-and-reflect" in catalog
    ), (
        "architecture/shippability.md missing catalog row #53 for "
        "slice-053 — RPCD-1/SCPD-1 BCR-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "BCR-1 backlog-consume + round-trip critical path)"
    )
    assert "BCR-1" in catalog, (
        "architecture/shippability.md row #53 missing the 'BCR-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


def test_v_0_62_0_pvfs_1_entry_present_in_repo():
    """methodology-changelog v0.62.0 / PVFS-1 entry-pin (content-bearing
    per slice-051 precedent; NOT a thin presence check; pins the
    load-bearing surface that, with the shippability-consumer-propagation
    pin and the catalog-rowed `test_pyproject_version_matches_version_file.py`,
    defeats the slice-037 M-add-1 tautological-green class for the slice's
    primary deliverable).

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate (NOT a per-version installed read here).

    Defect class: the v0.62.0 entry silently lost / never added → the
    PVFS-1 minting, its ADR-056 / new-rule-supersedes-nothing lineage,
    the 4-part PMI-1 atomic bump anchor, the Rule reference META-1
    entry-pin obligation, AND the Pyproject Version Forward Sync
    rule-name expansion all become unrecoverable from the changelog.

    Rule reference: PVFS-1 (slice-054; ADR-056; mints a new rule;
    supersedes nothing; extends the PMI-1 / AVFS-1 / MCFS-1 forward-sync
    family on the pyproject.toml leg).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.62.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.62.0 entry header — "
        "slice-054 PVFS-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.62.0")
    assert "PVFS-1" in body, (
        "v0.62.0 entry body missing the 'PVFS-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-056" in body, (
        "v0.62.0 entry body must record the ADR-056 minting decision "
        "(the slice-054 Inclusion-heuristic route-B selection)"
    )
    assert "Pyproject Version Forward Sync" in body, (
        "v0.62.0 entry body missing the 'Pyproject Version Forward Sync' "
        "rule-name expansion — future readers parsing the changelog "
        "alone must be able to find the rule by full name, not just ID"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.62.0 entry must state PVFS-1 'mints a new rule' (NOT '-D' "
        "refinement, NOT extension-without-new-RULE-ID) AND 'supersedes "
        "nothing' (lineage clean — extends the PMI-1 / AVFS-1 / MCFS-1 "
        "forward-sync family, does not supersede any of them)"
    )
    assert "4-part PMI-1 atomic bump" in body, (
        "v0.62.0 entry body missing the '4-part PMI-1 atomic bump' "
        "anchor — the slice-054 atomic-bump-leg discipline (VERSION + "
        "plugin.yaml.version + ## v0.62.0 header + ~/.claude/ai-sdlc-"
        "VERSION) must be named so a future reader sees the 4-leg "
        "obligation, not just the rule mint"
    )
    assert "Rule reference" in body, (
        "v0.62.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_62_0_pvfs_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the PVFS-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #54) so the slice-054 critical path can never silently regress
    (slice-040 lesson — an uncatalogued pin's breakage is invisible to
    the catalog runner).

    Per /critique-review M-add-1 (slice-054): row #54 MUST cite BOTH
    `PVFS-1` (the new RULE-ID) AND `SC-001` (the originating BCR-1
    finding ID) — slice-054 is the first end-to-end BCR-1 round-trip
    dogfood, so the SC-NNN trace axis MUST be regression-pinned on the
    slice that mints it. A future row rewrite that drops the SC-001 cite
    would silently sever the `/diagnose → /slice → /reflect` traceability
    axis slice-053 BCR-1 just shipped to enforce.

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: PVFS-1 (slice-054; ADR-056; RPCD-1/SCPD-1 consumer-
    reference propagation; M-add-1 BCR-1-traceability-axis expansion).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 54 | slice-054-fix-pyproject-toml-version-drift" in catalog
    ), (
        "architecture/shippability.md missing catalog row #54 for "
        "slice-054 — RPCD-1/SCPD-1 PVFS-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "PVFS-1 pyproject↔VERSION critical path)"
    )
    assert "PVFS-1" in catalog, (
        "architecture/shippability.md row #54 missing the 'PVFS-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )
    assert "SC-001" in catalog, (
        "architecture/shippability.md row #54 missing the 'SC-001' "
        "originating-finding reference — slice-054 is the first BCR-1 "
        "round-trip dogfood, so the SC-NNN trace axis MUST be "
        "regression-pinned on the row that exists because of the SC-NNN "
        "(per /critique-review M-add-1)"
    )


def test_shippability_row_56_present_and_cites_r15():
    """SCPD-1 consumer-reference propagation: shippability row #56 MUST
    cite BOTH `slice-056` AND `R-15` so the slice-056 R-15-mitigation
    audit trail survives future row rewrites (slice-054 /critique-review
    M-add-1 BCR-1-traceability-axis pin discipline applied analogously to
    risk-register-driven slices per slice-056 design.md L23/L185).

    Slice-056 ships the R-15 part-(a) fix (the `_resolve_slice_dir(NNN)`
    helper + the BCR-1 test repoint). R-15 STAYS `**Status**: mitigating`
    after slice-056 (per /critique m2 ACCEPTED-FIXED — retirement gate is
    two-part). The shippability row #56 IS the structural audit trail
    that slice-056 retired the R-15 part-(a) class; severing the R-15 cite
    via a future row rewrite would silently break the audit trail.

    A future row rewrite that drops the R-15 cite must FAIL this assertion
    — preserves the slice-056 / R-15 trace axis even as the catalog
    evolves.

    Rule reference: slice-056 (SCPD-1 consumer-reference propagation;
    R-15 retirement part-(a) audit trail; slice-054 M-add-1 traceability-
    axis pin discipline analogously applied to risk-register-driven slices).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 56 | slice-056-fix-bcr1-round-trip-test-archive-paths" in catalog
    ), (
        "architecture/shippability.md missing catalog row #56 for "
        "slice-056 — R-15 mitigation audit trail incomplete (the "
        "/validate-slice catalog runner cannot guard the slice-056 "
        "R-15 part-(a) critical path)"
    )
    assert "R-15" in catalog, (
        "architecture/shippability.md row #56 missing the 'R-15' rule "
        "reference — consumer-reference propagation broken at the "
        "risk-register-ID layer (a future row rewrite that drops the "
        "R-15 cite would silently sever the slice-056 R-15 retirement "
        "audit trail per slice-054 /critique-review M-add-1 traceability-"
        "axis pin discipline)"
    )


def test_shippability_row_57_present_and_cites_r15():
    """SCPD-1 consumer-reference propagation: shippability row #57 MUST
    cite BOTH `slice-057` AND `R-15` so the slice-057 R-15-retirement
    audit trail survives future row rewrites (slice-054 /critique-review
    M-add-1 BCR-1-traceability-axis pin discipline applied analogously to
    risk-register-driven slices, per slice-056 design.md L23/L185
    precedent — extended at slice-057 from R-15-mitigation to R-15-
    retirement-discharge framing).

    Slice-057 ships the R-15 part-(b) fix (the `_resolve_slice_dir(34)`
    retrofit + the `_R15_CORPUS_WHITELIST` shrink to `set()`). R-15
    transitions `**Status**: mitigating` → `retired` at architecture/
    risk-register.md as of slice-057 ship (closes the two-part retirement
    gate slice-056 pre-engineered). The shippability row #57 IS the
    structural audit trail that slice-057 discharged the R-15 part-(b)
    class; severing the R-15 cite via a future row rewrite would silently
    break the audit trail.

    A future row rewrite that drops the R-15 cite must FAIL this
    assertion — preserves the slice-057 / R-15 trace axis even as the
    catalog evolves.

    Rule reference: slice-057 (SCPD-1 consumer-reference propagation;
    R-15 retirement part-(b) audit trail; slice-054 M-add-1 traceability-
    axis pin discipline analogously applied to risk-register-driven
    slices per slice-056 row-#56 precedent).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 57 | slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit" in catalog
    ), (
        "architecture/shippability.md missing catalog row #57 for "
        "slice-057 — R-15 retirement audit trail incomplete (the "
        "/validate-slice catalog runner cannot guard the slice-057 "
        "R-15 part-(b) critical path)"
    )
    assert "R-15" in catalog, (
        "architecture/shippability.md row #57 missing the 'R-15' rule "
        "reference — consumer-reference propagation broken at the "
        "risk-register-ID layer (a future row rewrite that drops the "
        "R-15 cite would silently sever the slice-057 R-15 retirement "
        "audit trail per slice-054 /critique-review M-add-1 traceability-"
        "axis pin discipline)"
    )


def test_v_0_63_0_tvfs_1_entry_present_in_repo():
    """methodology-changelog v0.63.0 / TVFS-1 entry-pin (content-bearing
    per slice-051 precedent; NOT a thin presence check).

    **In-repo-only body** (slice-041 M3 discipline): reads ONLY the
    git-tracked in-repo entry via `read_file` (no `Path.home()`), so
    `shippability_decoupling_audit.classify_fn` classifies it `clean`.
    The installed↔in-repo forward-sync of THIS entry is covered by
    MCFS-1's whole-file gate (NOT a per-version installed read here).

    Defect class: the v0.63.0 entry silently lost / never added → the
    TVFS-1 minting, its ADR-058 / new-rule-supersedes-nothing lineage,
    the 4-part PMI-1 atomic bump anchor, the Rule reference META-1
    entry-pin obligation, AND the `ai-sdlc-tools Version Forward-Sync`
    rule-name expansion all become unrecoverable from the changelog.

    Rule reference: TVFS-1 (slice-059; ADR-058; mints a new rule;
    supersedes nothing; extends the PMI-1 / PVFS-1 / AVFS-1 / MCFS-1
    forward-sync family onto the installed-pip-artifact leg).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.63.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.63.0 entry header — "
        "slice-059 TVFS-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.63.0")
    assert "TVFS-1" in body, (
        "v0.63.0 entry body missing the 'TVFS-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-058" in body, (
        "v0.63.0 entry body must record the ADR-058 minting decision "
        "(the slice-059 Route-C standalone-tool selection)"
    )
    assert "ai-sdlc-tools Version Forward-Sync" in body, (
        "v0.63.0 entry body missing the 'ai-sdlc-tools Version "
        "Forward-Sync' rule-name expansion — future readers parsing the "
        "changelog alone must be able to find the rule by full name, not "
        "just ID"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.63.0 entry must state TVFS-1 'mints a new rule' AND "
        "'supersedes nothing' (lineage clean — extends the PMI-1 / "
        "PVFS-1 / AVFS-1 / MCFS-1 forward-sync family, does not "
        "supersede any of them)"
    )
    assert "4-part PMI-1 atomic bump" in body, (
        "v0.63.0 entry body missing the '4-part PMI-1 atomic bump' "
        "anchor — the slice-059 atomic-bump-leg discipline (VERSION + "
        "plugin.yaml.version + pyproject.toml.version + ## v0.63.0 "
        "header + ~/.claude/ai-sdlc-VERSION) must be named so a future "
        "reader sees the bump obligation, not just the rule mint"
    )
    assert "Rule reference" in body, (
        "v0.63.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_63_0_tvfs_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the TVFS-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #59) so the slice-059 critical path can never silently regress
    (slice-040 lesson — an uncatalogued pin's breakage is invisible to
    the catalog runner).

    In-repo-only (reads the git-tracked catalog via `read_file`; no
    `Path.home()` — classifies `clean`).

    Rule reference: TVFS-1 (slice-059; ADR-058; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 59 | slice-059-add-tools-package-version-gate" in catalog
    ), (
        "architecture/shippability.md missing catalog row #59 for "
        "slice-059 — RPCD-1/SCPD-1 TVFS-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "TVFS-1 installed-pip-package critical path)"
    )
    assert "TVFS-1" in catalog, (
        "architecture/shippability.md row #59 missing the 'TVFS-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )


# --- Slice-060 / CRSI-1 entry pinning ---

def test_v_0_64_0_crsi_1_entry_present_in_repo():
    """methodology-changelog v0.64.0 / CRSI-1 entry-pin (content-bearing
    per slice-051 / slice-058 / slice-059 precedent; NOT a thin presence
    check).

    Asserts 8 substring presences in the v0.64.0 entry body (per
    /critique M4 design.md "What's new" enumeration):
      (a) `## v0.64.0` header
      (b) `CRSI-1` rule ID
      (c) `ADR-059` reference
      (d) `Code-Review Skill Insertion` full rule-name expansion
      (e) `mints a new rule` + `supersedes nothing` lineage clauses
      (f) `5-part PMI-1 atomic bump` (per critique B2 5-part-bump fix)
      (g) `Rule reference` literal (META-1 enforcing-assertion obligation
          at tests/methodology/test_methodology_changelog.py:136)
      (h) OSDG-1 / CAD-1 lineage anchor (drift-guard family-add)

    Rule reference: CRSI-1 (slice-060; ADR-059; mints a new rule;
    supersedes nothing; extends the dual-Critic design-review family +
    OSDG-1 / CAD-1 drift-guard families onto code-as-artifact).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.64.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.64.0 entry header — "
        "slice-060 CRSI-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.64.0")
    assert "CRSI-1" in body, (
        "v0.64.0 entry body missing the 'CRSI-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-059" in body, (
        "v0.64.0 entry body must record the ADR-059 minting decision"
    )
    assert "Code-Review Skill Insertion" in body, (
        "v0.64.0 entry body missing the 'Code-Review Skill Insertion' "
        "rule-name expansion — future readers parsing the changelog "
        "alone must be able to find the rule by full name, not just ID"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.64.0 entry must state CRSI-1 'mints a new rule' AND "
        "'supersedes nothing' (lineage clean — extends the dual-Critic "
        "design-review family + OSDG-1 / CAD-1 drift-guard families)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.64.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — the slice-060 PVFS-1 leg discipline (VERSION + "
        "plugin.yaml.version + pyproject.toml.version + ## v0.64.0 "
        "header + ~/.claude/ai-sdlc-VERSION) must be named"
    )
    assert "Rule reference" in body, (
        "v0.64.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    # OSDG-1 + CAD-1 lineage anchor (drift-guard family-add evidence)
    assert "OSDG-1" in body and "CAD-1" in body, (
        "v0.64.0 entry must record the OSDG-1 (skill-drift) + CAD-1 "
        "(agent-drift) family-add lineage — the slice-049/051 + "
        "slice-007 precedent chain"
    )


def test_v_0_64_0_crsi_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the CRSI-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #60) so the slice-060 critical path can never silently regress
    (slice-040 lesson + BC-PROJ-10:173 verbatim pair-precedent — an
    uncatalogued pin's breakage is invisible to the catalog runner).

    Per /critique-review M-add-2: this paired test was missed by the
    first Critic; meta-Critic EXTEND caught it via BC-PROJ-10 N≥17 stable
    pair precedent across the changelog test module.

    Rule reference: CRSI-1 (slice-060; ADR-059; RPCD-1/SCPD-1 consumer-
    reference propagation).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 60 | slice-060-add-code-review-skill" in catalog
    ), (
        "architecture/shippability.md missing catalog row #60 for "
        "slice-060 — RPCD-1/SCPD-1 CRSI-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard the "
        "CRSI-1 critical path)"
    )
    assert "CRSI-1" in catalog, (
        "architecture/shippability.md row #60 missing the 'CRSI-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )
    assert "ADR-059" in catalog, (
        "architecture/shippability.md row #60 missing the 'ADR-059' "
        "reference — BCR-1 traceability axis broken (per slice-054 "
        "/critique-review M-add-1 BCR-1-traceability axis pin discipline)"
    )
    # Verify the new drift-guard test modules are catalog-referenced
    # (SCPD-1: silent regression on test module rename caught here)
    assert "code_review_skill_drift" in catalog, (
        "architecture/shippability.md row #60 missing reference to the "
        "test_code_review_skill_drift module — OSDG-1 family-add "
        "propagation broken"
    )
    assert "code_review_agent_drift" in catalog, (
        "architecture/shippability.md row #60 missing reference to the "
        "test_code_review_agent_drift module — CAD-1 family-add "
        "propagation broken"
    )


# --- Slice-062 / R-15-scope-extension entry pinning ---

def test_v_0_65_0_r15_scope_extension_entry_present_in_repo():
    """methodology-changelog v0.65.0 / R-15-scope-extension entry-pin
    (content-bearing per slice-051 / slice-058 / slice-059 / slice-060
    precedent; NOT a thin presence check).

    Asserts 8 substring presences in the v0.65.0 entry body:
      (a) `## v0.65.0` header
      (b) `R-15` rule ID
      (c) `ADR-060` reference
      (d) `R-15 corpus class-closure backstop scope extension` rule-name
          expansion (full rule-name + scope-extension qualifier)
      (e) `mints no new rule` + `supersedes nothing` lineage clauses
          (slice-062 extends an existing rule's scope; does NOT mint)
      (f) `5-part PMI-1 atomic bump` (per /critique B1 5-part-bump fix —
          mirrors slice-060 v0.64.0 entry-pin assertion (f) at L3989)
      (g) `Rule reference` literal (META-1 enforcing-assertion obligation
          at tests/methodology/test_methodology_changelog.py:136)
      (h) ADR-053 naming-class-peer lineage anchor (slice-062 ADR-060
          extends-not-mints the OSDG-1-member-addition shape)

    Rule reference: ADR-060 (slice-062; mints no new rule; supersedes
    nothing; extends the slice-056 / slice-057 R-15 backstop scope to
    wider test corpora — naming-class peer of ADR-053 which extended
    OSDG-1's guarded set without minting a new rule).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.65.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.65.0 entry header — "
        "slice-062 R-15-scope-extension entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.65.0")
    assert "R-15" in body, (
        "v0.65.0 entry body missing the 'R-15' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-060" in body, (
        "v0.65.0 entry body must record the ADR-060 minting decision"
    )
    assert "R-15 corpus class-closure backstop scope extension" in body, (
        "v0.65.0 entry body missing the 'R-15 corpus class-closure "
        "backstop scope extension' rule-name expansion — future readers "
        "parsing the changelog alone must be able to find the slice's "
        "intent by full name, not just by ID"
    )
    assert "mints no new rule" in body and "supersedes nothing" in body, (
        "v0.65.0 entry must state ADR-060 'mints no new rule' AND "
        "'supersedes nothing' (lineage clean — extends the slice-056 / "
        "slice-057 R-15 backstop scope; does NOT mint a new rule)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.65.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — the slice-062 PVFS-1 leg discipline (VERSION + "
        "plugin.yaml.version + pyproject.toml.version + ## v0.65.0 "
        "header + ~/.claude/ai-sdlc-VERSION) must be named (per "
        "/critique B1 fix-block 5-part-bump propagation discipline)"
    )
    assert "Rule reference" in body, (
        "v0.65.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    # ADR-053 naming-class-peer lineage anchor (slice-062 ADR-060
    # extends-not-mints shape inherits the slice-051/ADR-053 OSDG-1
    # member-addition precedent)
    assert "ADR-053" in body, (
        "v0.65.0 entry must record the ADR-053 naming-class-peer "
        "lineage — slice-062 ADR-060 follows the slice-051 / ADR-053 "
        "extends-not-mints precedent shape"
    )


def test_v_0_65_0_r15_scope_extension_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the R-15-scope-
    extension consumer reference MUST propagate into
    `architecture/shippability.md` (catalog row #62) so the slice-062
    critical path can never silently regress (slice-040 lesson +
    BC-PROJ-10:173 verbatim pair-precedent — an uncatalogued pin's
    breakage is invisible to the catalog runner).

    Per /critique-review M-add-2 (BC-PROJ-10 N>=17 stable pair precedent
    across the changelog test module): mirrors slice-060 row #60 paired
    pin shape verbatim.

    Rule reference: ADR-060 (slice-062; RPCD-1/SCPD-1 consumer-reference
    propagation onto the R-15-scope-extension critical path).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 62 | slice-062-extend-r15-corpus-class-closure-scope" in catalog
    ), (
        "architecture/shippability.md missing catalog row #62 for "
        "slice-062 — RPCD-1/SCPD-1 R-15-scope-extension consumer-"
        "reference propagation incomplete (the /validate-slice catalog "
        "runner cannot guard the R-15-scope-extension critical path)"
    )
    assert "R-15" in catalog, (
        "architecture/shippability.md row #62 missing the 'R-15' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )
    assert "ADR-060" in catalog, (
        "architecture/shippability.md row #62 missing the 'ADR-060' "
        "reference — BCR-1 traceability axis broken (per slice-054 "
        "/critique-review M-add-1 BCR-1-traceability axis pin "
        "discipline; row MUST cite BOTH R-15 AND ADR-060)"
    )
    # Verify the new corpus-extension test functions are catalog-referenced
    # (SCPD-1: silent regression on test function rename caught here)
    assert "test_no_new_archive_fragile_literals_in_tests_skills_corpus" in catalog, (
        "architecture/shippability.md row #62 missing reference to the "
        "test_no_new_archive_fragile_literals_in_tests_skills_corpus "
        "function — R-15 backstop scope-extension propagation broken on "
        "the tests/skills/ arm"
    )
    assert "test_no_new_archive_fragile_literals_in_tests_agents_corpus" in catalog, (
        "architecture/shippability.md row #62 missing reference to the "
        "test_no_new_archive_fragile_literals_in_tests_agents_corpus "
        "function — R-15 backstop scope-extension propagation broken on "
        "the tests/agents/ arm"
    )
    assert "test_r15_corpus_whitelist_has_no_orphan_entries" in catalog, (
        "architecture/shippability.md row #62 missing reference to the "
        "test_r15_corpus_whitelist_has_no_orphan_entries function — "
        "aggregated whitelist-integrity check propagation broken"
    )


# --- Slice-063 / NAW-1 entry pinning ---

def test_v_0_66_0_naw_1_entry_present_in_repo():
    """methodology-changelog v0.66.0 / NAW-1 entry-pin (content-bearing
    per slice-051 / slice-058 / slice-059 / slice-060 / slice-062
    precedent; NOT a thin presence check).

    Asserts 8 substring presences in the v0.66.0 entry body (per design.md
    item 8 + critique-review M-add-2 fix — META-1 mandatory + slice-060
    + slice-062 precedent anchor set):
      (a) `## v0.66.0` header (slice-060 + slice-062 precedent header
          anchor; M-add-2 critique fix)
      (b) `NAW-1` rule ID
      (c) `ADR-061` reference
      (d) `New-Agent Warning` rule-name expansion (full rule-name)
      (e) `mints a new rule` + `supersedes nothing` lineage clauses
      (f) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`; M-add-2
          critique fix)
      (g) `5-part PMI-1 atomic bump` (5-part, NOT 4-part — slice-063
          ships a NEW `tools/*.py` so PMI-1 leg count matches slice-060
          / slice-062 5-part precedent; the anchor literal MUST be
          `5-part` to avoid the slice-062 M-add-3 stale-carry class)

    Rule reference: NAW-1 (slice-063; ADR-061; mints a new rule;
    supersedes nothing — the first audit-enforced gate on the
    discovery-gate axis adjacent to but NOT extending the PMI-1 /
    PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1 forward-sync family).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.66.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.66.0 entry header — "
        "slice-063 NAW-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.66.0")
    assert "NAW-1" in body, (
        "v0.66.0 entry body missing the 'NAW-1' rule reference — "
        "entry-pin broken at the rule-reference layer"
    )
    assert "ADR-061" in body, (
        "v0.66.0 entry body must record the ADR-061 minting decision"
    )
    assert "New-Agent Warning" in body, (
        "v0.66.0 entry body missing the 'New-Agent Warning' rule-name "
        "expansion — future readers parsing the changelog alone must be "
        "able to find the slice's intent by full name, not just by ID"
    )
    assert "mints a new rule" in body and "supersedes nothing" in body, (
        "v0.66.0 entry must state ADR-061 'mints a new rule' AND "
        "'supersedes nothing' (the slice-049 / slice-050 / slice-054 / "
        "slice-059 / slice-060 new-RULE-ID precedent shape)"
    )
    assert "Rule reference" in body, (
        "v0.66.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet (slice-062 /critique-review "
        "M-add-2 ACCEPTED-FIXED discipline)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.66.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — slice-063 ships a NEW `tools/*.py` (NAW-1 audit) so "
        "PMI-1 leg count matches slice-060 / slice-062 5-part precedent "
        "(NOT slice-059 4-part). The anchor literal MUST be `5-part` to "
        "avoid the slice-062 M-add-3 stale-carry class."
    )


def test_v_0_66_0_naw_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the NAW-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #63) so the slice-063 critical path can never silently regress
    (slice-040 lesson + BC-PROJ-10:173 verbatim pair-precedent — an
    uncatalogued pin's breakage is invisible to the catalog runner).

    BCR-1 traceability axis (per slice-054 first-dogfood precedent + the
    slice-056 row-#56 / slice-062 row-#62 lineage): row #63 MUST cite
    BOTH the new `NAW-1` rule-ID AND the retired `R-18` risk-ID AND the
    `ADR-061` minting decision.

    Rule reference: NAW-1 (slice-063; RPCD-1/SCPD-1 consumer-reference
    propagation onto the NAW-1 critical path).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 63 | slice-063-add-build-slice-new-agent-warning" in catalog
    ), (
        "architecture/shippability.md missing catalog row #63 for "
        "slice-063 — RPCD-1/SCPD-1 NAW-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard "
        "the NAW-1 critical path)"
    )
    assert "NAW-1" in catalog, (
        "architecture/shippability.md row #63 missing the 'NAW-1' rule "
        "reference — consumer-reference propagation broken at the "
        "rule-ID layer"
    )
    assert "R-18" in catalog, (
        "architecture/shippability.md row #63 missing the 'R-18' risk "
        "reference — BCR-1 traceability axis broken (row MUST cite BOTH "
        "NAW-1 AND R-18 per slice-054 first-dogfood + slice-056 / "
        "slice-062 lineage precedent)"
    )
    assert "ADR-061" in catalog, (
        "architecture/shippability.md row #63 missing the 'ADR-061' "
        "reference — BCR-1 traceability axis broken at the ADR layer"
    )
    # SCPD-1: silent regression on test function rename caught here
    assert "test_new_agent_warning_audit" in catalog, (
        "architecture/shippability.md row #63 missing reference to the "
        "test_new_agent_warning_audit module — NAW-1 audit-test "
        "propagation broken"
    )
    assert "test_build_slice_step_6_invokes_new_agent_warning_audit" in catalog, (
        "architecture/shippability.md row #63 missing reference to the "
        "test_build_slice_step_6_invokes_new_agent_warning_audit "
        "function — NAW-1 Step 6 wiring pin propagation broken"
    )
    assert "test_r_18_retired_post_slice_063" in catalog, (
        "architecture/shippability.md row #63 missing reference to the "
        "test_r_18_retired_post_slice_063 function — R-18 retirement "
        "pin propagation broken"
    )


def test_v_0_67_0_naw_extend_entry_present_in_repo():
    """methodology-changelog v0.67.0 / extend-NAW-1-to-/code-review
    entry-pin (content-bearing per slice-051 / slice-058 / slice-059 /
    slice-060 / slice-062 / slice-063 precedent; NOT a thin presence
    check).

    Asserts 8 substring presences in the v0.67.0 entry body (per
    design.md L18 / critique-review M-add-2 + M-add-3 fixes; treats the
    lineage clauses as compound single anchor per slice-063 precedent):
      (a) `## v0.67.0` header
      (b) `NAW-1` rule reference (the canonical pattern, not minted)
      (c) `Extend NAW-1 union-of-three-sources to /code-review`
          rule-name expansion (slice-063 anchor (d) precedent applied
          to scope-extension entries; first scope-extension entry that
          doesn't mint a new rule needs the rule-name expansion to
          disambiguate "extends NAW-1" vs "is a NAW-1 surface")
      (d) `ADR-062` reference
      (e) `5-part PMI-1 atomic bump`
      (f) `/code-review` surface
      (g) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
      (h) `mints no new rule` AND `supersedes nothing` compound lineage
          clauses (slice-063 v0.66.0 precedent treats this pair as a
          single compound anchor — N=8 inclusive of this slice on the
          scope-extension class; slice-049/050/051/057/058/059/062 + 064)

    Rule reference: extension of NAW-1 union-of-three-sources read
    mechanism (slice-064; ADR-062; mints no new rule; supersedes
    nothing — the slice-064 entry is a sibling-surface application of
    NAW-1's pattern, NOT a retirement-discharge / pure-conformance
    shape; Inclusion-heuristic firing on scope-extension precedent
    N=8 cumulative inclusive).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.67.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.67.0 entry header — "
        "slice-064 extend-NAW-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.67.0")
    assert "NAW-1" in body, (
        "v0.67.0 entry body missing the 'NAW-1' rule reference — "
        "entry-pin broken at the rule-reference layer (the canonical "
        "pattern this slice extends)"
    )
    assert "Extend NAW-1 union-of-three-sources to /code-review" in body, (
        "v0.67.0 entry body missing the 'Extend NAW-1 union-of-three-"
        "sources to /code-review' rule-name expansion — slice-064 is "
        "the first scope-extension entry that doesn't mint a new rule, "
        "so the rule-name expansion disambiguates 'extends NAW-1' vs "
        "'is a NAW-1 surface' for future readers (slice-063 anchor (d) "
        "precedent applied to scope-extension entries; /critique-review "
        "M-add-3 ACCEPTED-FIXED)"
    )
    assert "ADR-062" in body, (
        "v0.67.0 entry body must record the ADR-062 reference"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.67.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — slice-064 does NOT add a new `tools/*.py`, but the "
        "PMI-1 leg count is 5 (VERSION + plugin.yaml + pyproject.toml + "
        "## v0.67.0 header + installed ai-sdlc-VERSION) per slice-060 / "
        "slice-062 / slice-063 5-part precedent for SKILL.md-touching "
        "slices"
    )
    assert "/code-review" in body, (
        "v0.67.0 entry body missing the '/code-review' surface anchor — "
        "the SKILL.md surface being modified must be named explicitly"
    )
    assert "Rule reference" in body, (
        "v0.67.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    assert "mints no new rule" in body and "supersedes nothing" in body, (
        "v0.67.0 entry must state ADR-062 'mints no new rule' AND "
        "'supersedes nothing' (the slice-049 / slice-051 / slice-057 / "
        "slice-062 scope-extension-no-new-RULE-ID precedent shape; "
        "slice-063 v0.66.0 precedent treats this pair as a single "
        "compound anchor)"
    )


def test_v_0_67_0_naw_extend_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the extend-NAW-1
    consumer reference MUST propagate into `architecture/shippability.md`
    (catalog row #64) so the slice-064 critical path can never silently
    regress (slice-040 lesson + BC-PROJ-10:173 verbatim pair-precedent —
    an uncatalogued pin's breakage is invisible to the catalog runner).

    BCR-1 traceability axis (per slice-054 first-dogfood precedent +
    slice-056/062/063 lineage): row #64 MUST cite BOTH the new
    `ADR-062` reference AND the existing `NAW-1` rule-ID (the canonical
    pattern being extended) AND `ADR-061` (NAW-1's minting decision).

    Rule reference: extension of NAW-1 union-of-three-sources read
    mechanism (slice-064; ADR-062; RPCD-1/SCPD-1 consumer-reference
    propagation onto the slice-064 critical path).
    """
    catalog = read_file("architecture/shippability.md")
    assert (
        "| 64 | slice-064-fix-code-review-diff-resolution-falsifier" in catalog
    ), (
        "architecture/shippability.md missing catalog row #64 for "
        "slice-064 — RPCD-1/SCPD-1 consumer-reference propagation "
        "incomplete (the /validate-slice catalog runner cannot guard "
        "the slice-064 critical path)"
    )
    assert "ADR-062" in catalog, (
        "architecture/shippability.md row #64 missing the 'ADR-062' "
        "reference — BCR-1 traceability axis broken at the ADR layer"
    )
    assert "NAW-1" in catalog, (
        "architecture/shippability.md row #64 missing the 'NAW-1' "
        "rule reference — BCR-1 traceability axis broken at the "
        "rule-ID layer (the canonical pattern being extended)"
    )
    assert "ADR-061" in catalog, (
        "architecture/shippability.md row #64 missing the 'ADR-061' "
        "reference — BCR-1 traceability axis broken at the canonical-"
        "ADR-being-extended layer"
    )
    # SCPD-1: silent regression on test function rename caught here
    assert "test_skill_md_step_1_diff_resolution_uses_union_of_three_sources" in catalog, (
        "architecture/shippability.md row #64 missing reference to the "
        "BFRD-1 repro test — SCPD-1 consumer-reference propagation "
        "broken"
    )


def test_v_0_68_0_branch_2_entry_present_in_repo():
    """methodology-changelog v0.68.0 / BRANCH-2 worktree-per-slice
    entry-pin (content-bearing per slice-051 / slice-058 / slice-059 /
    slice-060 / slice-062 / slice-063 / slice-064 precedent; NOT a thin
    presence check).

    Asserts substring presences in the v0.68.0 entry body (per
    design.md / ADR-063 §Decision):
      (a) `## v0.68.0` dated header
      (b) `BRANCH-2` rule reference (the new RULE-ID this entry mints)
      (c) `ADR-063` reference
      (d) `Worktree-per-slice + branch` canonical-phrase anchor
      (e) `supersedes ADR-019` lineage (the N=2 partial-supersession)
      (f) `5-part PMI-1 atomic bump` (slice-063/064 canonical anchor —
          VERSION + plugin.yaml.version + pyproject.toml [project].version
          + ## v0.68.0 header + installed ~/.claude/ai-sdlc-VERSION;
          CLAUDE.md edit + shippability row #66 are SEPARATE BC-PROJ-9
          / BC-PROJ-10 consumer-propagation surfaces, NOT PMI-1 parts —
          per slice-066 /build-slice Phase A Builder-self-catch)
      (g) `R-17` reference (the retired risk this BRANCH-2 closes)
      (h) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
      (i) `mints a new rule` AND `supersedes` (compound lineage clauses;
          mints BRANCH-2 NEW rule, supersedes ADR-019 sub-mode (a))

    Rule reference: BRANCH-2 (slice-066; ADR-063; partial-supersedes
    ADR-019 sub-mode (a); extends sub-mode (c); methodology v0.68.0;
    N=2 application of slice-022 partial-supersession encoding pattern).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.68.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.68.0 entry header — "
        "slice-066 BRANCH-2 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.68.0")
    assert "BRANCH-2" in body, (
        "v0.68.0 entry body missing the 'BRANCH-2' rule reference — "
        "entry-pin broken at the rule-reference layer (this slice MINTS "
        "BRANCH-2 as a new audit-enforced rule)"
    )
    assert "ADR-063" in body, (
        "v0.68.0 entry body must reference ADR-063 (the partial-supersession of ADR-019 sub-mode (a))"
    )
    assert "Worktree-per-slice" in body, (
        "v0.68.0 entry body missing the 'Worktree-per-slice' canonical "
        "phrase anchor — BRANCH-2's name is `Worktree-per-slice + branch`"
    )
    assert "ADR-019" in body, (
        "v0.68.0 entry body must reference ADR-019 (the BRANCH-1 mint that BRANCH-2 partial-supersedes)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.68.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — slice-066 ships a 5-part bump (VERSION + plugin.yaml + "
        "pyproject.toml + ## v0.68.0 header + installed ai-sdlc-VERSION) "
        "per slice-063/064 canonical anchor. CLAUDE.md + shippability "
        "row #66 are SEPARATE consumer-propagation surfaces (BC-PROJ-9 "
        "/ BC-PROJ-10), NOT PMI-1 parts (per slice-066 /build-slice "
        "Phase A Builder-self-catch)"
    )
    assert "R-17" in body, (
        "v0.68.0 entry body must reference R-17 (the risk-register entry "
        "this BRANCH-2 retires — uncommitted-slice-A-WIP-contaminates-"
        "slice-B class closed structurally via worktree isolation)"
    )
    assert "Rule reference" in body, (
        "v0.68.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    assert "mints a new rule" in body, (
        "v0.68.0 entry must state 'mints a new rule' (BRANCH-2 is a NEW "
        "audit-enforced rule, NOT a scope-extension; slice-063 v0.66.0 "
        "/ NAW-1 mint precedent applies to slice-066 / BRANCH-2 mint)"
    )
    assert "supersedes" in body, (
        "v0.68.0 entry must reference the supersedes lineage — ADR-063 "
        "partial-supersedes ADR-019 sub-mode (a) (slice-022 partial-"
        "supersession encoding pattern, N=2 application)"
    )


def test_v_0_68_0_branch_2_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the BRANCH-2 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #66) so the slice-066 critical path can never silently regress
    (slice-040 lesson + BC-PROJ-10:173 verbatim pair-precedent — an
    uncatalogued pin's breakage is invisible to the catalog runner).

    BCR-1 traceability axis (per slice-054 first-dogfood precedent +
    slice-056/062/063/064 lineage): row #66 MUST cite BOTH the new RULE-ID
    (BRANCH-2) AND the new ADR (ADR-063) AND the retired risk (R-17) —
    severing any of these axes silently breaks traceability from the
    catalog row to the methodology-changelog entry to the ADR to the
    risk-register.

    Rule reference: BC-PROJ-10:173 (paired entry-pin precedent N≥17
    inclusive of this slice); BCR-1 traceability axis.
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-066-add-worktree-per-slice-discipline" in catalog, (
        "architecture/shippability.md must contain a slice-066 row "
        "(catalog row #66 per BC-PROJ-10:173 paired-entry-pin discipline; "
        "an uncatalogued pin is invisible to the catalog runner)"
    )
    # Locate the slice-066 row (single line in pipe-table format).
    row_start = catalog.find("slice-066-add-worktree-per-slice-discipline")
    # Find the row boundary: next ` | ` separating columns suggests we're in the row;
    # take a generous window since rows are very long single-line narratives.
    row_end = catalog.find("\n| ", row_start)
    row = catalog[row_start:row_end] if row_end > 0 else catalog[row_start:row_start + 8000]
    assert "BRANCH-2" in row, (
        "shippability.md row #66 must cite BRANCH-2 (the new RULE-ID) per "
        "BCR-1 traceability axis"
    )
    assert "ADR-063" in row, (
        "shippability.md row #66 must cite ADR-063 (the new ADR) per "
        "BCR-1 traceability axis"
    )
    assert "R-17" in row, (
        "shippability.md row #66 must cite R-17 (the retired risk this "
        "BRANCH-2 closes) per BCR-1 traceability axis"
    )
    assert "worktree" in row.lower(), (
        "shippability.md row #66 must reference 'worktree' (the discipline "
        "this row pins) for catalog-runner discoverability"
    )


def test_v_0_69_0_psq_1_entry_present_in_repo():
    """methodology-changelog v0.69.0 / PSQ-1 parallel-slice queue entry-pin
    (content-bearing per slice-051 / slice-058 / slice-059 / slice-060 /
    slice-062 / slice-063 / slice-064 / slice-066 precedent; NOT a thin
    presence check).

    Asserts substring presences in the v0.69.0 entry body (per
    design.md / ADR-064 §Decision):
      (a) `## v0.69.0` dated header
      (b) `PSQ-1` rule reference (the new RULE-ID this entry mints)
      (c) `ADR-064` reference
      (d) `Parallel-slice queue output` canonical-phrase anchor
      (e) `mints a new rule` (PSQ-1 is the first rule on parallel-slice
          family axis; supersedes nothing per ADR-064)
      (f) `5-part PMI-1 atomic bump` (slice-063/064/066 canonical anchor —
          VERSION + plugin.yaml.version + pyproject.toml [project].version
          + ## v0.69.0 header + installed ~/.claude/ai-sdlc-VERSION;
          shippability row #67 is a SEPARATE BC-PROJ-10 consumer-propagation
          surface, NOT a PMI-1 part — per slice-066 / slice-067 /critique-
          review M-add-4 ADR-064 L50 fix Builder-self-catch)
      (g) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
      (h) `NON-OVERLAPPING` AND `UNKNOWN-NO-HINT-FILES` AND
          `UNKNOWN-NO-GRAPH` (4-value Parallel-safety enum members — the
          stable on-disk format contract slice-068 PSQ-2 extends additively)

    Rule reference: PSQ-1 (slice-067; ADR-064 mints a new rule; first rule
    on parallel-slice family axis; methodology v0.69.0).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.69.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.69.0 entry header — "
        "slice-067 PSQ-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.69.0")
    assert "PSQ-1" in body, (
        "v0.69.0 entry body missing the 'PSQ-1' rule reference — "
        "entry-pin broken at the rule-reference layer (this slice MINTS "
        "PSQ-1 as a new audit-enforced rule)"
    )
    assert "ADR-064" in body, (
        "v0.69.0 entry body must reference ADR-064 (the new ADR minting PSQ-1)"
    )
    assert "Parallel-slice queue output" in body, (
        "v0.69.0 entry body missing the 'Parallel-slice queue output' "
        "canonical phrase anchor — PSQ-1's name"
    )
    assert "mints a new rule" in body, (
        "v0.69.0 entry must state 'mints a new rule' (PSQ-1 is a NEW "
        "audit-enforced rule; first on parallel-slice family axis; "
        "supersedes nothing per ADR-064)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.69.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — slice-067 ships a 5-part bump (VERSION + plugin.yaml + "
        "pyproject.toml + ## v0.69.0 header + installed ai-sdlc-VERSION) "
        "per slice-063/064/066 canonical anchor. Shippability row #67 + "
        "venv ai-sdlc-tools are SEPARATE consumer-propagation surfaces "
        "(BC-PROJ-10 / TVFS-1), NOT PMI-1 parts (per slice-067 /critique-"
        "review M-add-4 ADR-064 L50 fix Builder-self-catch)"
    )
    assert "Rule reference" in body, (
        "v0.69.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    assert "NON-OVERLAPPING" in body, (
        "v0.69.0 entry must enumerate the NON-OVERLAPPING Parallel-safety "
        "enum value (the stable on-disk format contract slice-068 PSQ-2 "
        "extends additively per ADR-064 §Consequences)"
    )
    assert "UNKNOWN-NO-HINT-FILES" in body, (
        "v0.69.0 entry must enumerate the UNKNOWN-NO-HINT-FILES "
        "Parallel-safety enum value (per AC4-(d) collision rule + "
        "/critique-review B2 ACCEPTED-FIXED 4-value enum harmonization)"
    )
    assert "UNKNOWN-NO-GRAPH" in body, (
        "v0.69.0 entry must enumerate the UNKNOWN-NO-GRAPH Parallel-safety "
        "enum value (per AC4-(c) missing-graph degraded-mode behaviour)"
    )


def test_v_0_69_0_psq_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the PSQ-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #67) so the slice-067 critical path can never silently regress
    (slice-040 lesson + BC-PROJ-10:173 verbatim pair-precedent — an
    uncatalogued pin's breakage is invisible to the catalog runner).

    BCR-1 traceability axis (per slice-054 first-dogfood precedent +
    slice-056/062/063/064/066 lineage): row #67 MUST cite BOTH the new
    RULE-ID (PSQ-1) AND the new ADR (ADR-064) AND the two BC-PROJ-10
    paired-pin test function names — severing any of these axes silently
    breaks traceability from the catalog row to the methodology-changelog
    entry to the ADR to the entry-pin tests.

    Rule reference: BC-PROJ-10:173 (paired entry-pin precedent N≥18
    inclusive of this slice); BCR-1 traceability axis.
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-067-add-parallel-slice-queue-output" in catalog, (
        "architecture/shippability.md must contain a slice-067 row "
        "(catalog row #67 per BC-PROJ-10:173 paired-entry-pin discipline; "
        "an uncatalogued pin is invisible to the catalog runner)"
    )
    # Locate the slice-067 row (single line in pipe-table format).
    row_start = catalog.find("slice-067-add-parallel-slice-queue-output")
    row_end = catalog.find("\n| ", row_start)
    row = catalog[row_start:row_end] if row_end > 0 else catalog[row_start:row_start + 8000]
    assert "PSQ-1" in row, (
        "shippability.md row #67 must cite PSQ-1 (the new RULE-ID) per "
        "BCR-1 traceability axis"
    )
    assert "ADR-064" in row, (
        "shippability.md row #67 must cite ADR-064 (the new ADR) per "
        "BCR-1 traceability axis"
    )
    assert "test_v_0_69_0_psq_1_entry_present_in_repo" in row, (
        "shippability.md row #67 must cite the entry-pin test function "
        "by canonical name (BC-PROJ-10 paired-pin schema; severing this "
        "axis silently breaks the catalog-row→test traceability)"
    )
    assert "test_v_0_69_0_psq_1_shippability_consumer_propagation" in row, (
        "shippability.md row #67 must cite the shippability-consumer-"
        "propagation test function by canonical name (BC-PROJ-10 paired-"
        "pin schema)"
    )
    assert ("queue" in row.lower()) or ("parallel" in row.lower()), (
        "shippability.md row #67 must reference 'queue' or 'parallel' "
        "(the discipline this row pins) for catalog-runner discoverability"
    )


# ─── slice-071 / slice-069 M2 paired-pin completion ────────────────────


def test_v_0_70_0_adr_066_entry_present_in_repo():
    """methodology-changelog v0.70.0 / ADR-066 entry-pin (content-bearing
    per slice-051 / slice-058 / slice-059 / slice-060 / slice-062 /
    slice-063 / slice-064 / slice-066 / slice-067 precedent).

    slice-071 / slice-069 M2 FIX (paired-pin completion per slice-069
    code-Critic M2): slice-069 shipped MEPD-1 INCLUDE posture but did NOT
    ship the BC-PROJ-10 paired-entry-pin pair that every prior INCLUDE-
    posture slice (slice-067 / slice-066 / slice-058 / slice-052) carries.
    This test (+ its consumer-propagation sibling below) closes the gap.

    Asserts substring presences in the v0.70.0 entry body (per
    methodology-changelog.md `## v0.70.0` + ADR-066 §Decision):
      (a) `## v0.70.0` dated header
      (b) `ADR-066` reference (the new architectural philosophy this entry mints)
      (c) `vault-in-git` canonical-phrase anchor
      (d) `BC-PROJ-8` reference (the supersession target)
      (e) `STP-1 Sub-form B docstring` (canonical reframing anchor)
      (f) `M5 INCLUDE direction` (the /code-review SKILL.md scope shift)
      (g) `5-part PMI-1 atomic bump` (slice-063/064/066/067 canonical anchor)
      (h) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
      (i) `partial supersession` (ADR-028 §Options-#1 only — preserves
          BCI-1 Decisions 1-3 unchanged per ADR-066 frontmatter)

    Rule reference: ADR-066 (slice-069; mints a new architectural philosophy;
    partial supersession of ADR-028 §Options-#1 only; methodology v0.70.0).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.70.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.70.0 entry header — "
        "slice-069 ADR-066 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.70.0")
    assert "ADR-066" in body, (
        "v0.70.0 entry body missing the 'ADR-066' architectural-philosophy "
        "reference (this slice MINTS ADR-066 as the vault-in-git philosophy)"
    )
    assert "vault-in-git" in body or "vault in git" in body.lower(), (
        "v0.70.0 entry body missing the 'vault-in-git' canonical phrase anchor"
    )
    assert "BC-PROJ-8" in body, (
        "v0.70.0 entry body must reference BC-PROJ-8 (the rule whose content "
        "is superseded per ADR-066 §Decision)"
    )
    assert "STP-1 Sub-form B docstring" in body, (
        "v0.70.0 entry body missing the 'STP-1 Sub-form B docstring' "
        "canonical reframing anchor"
    )
    assert "M5 INCLUDE direction" in body, (
        "v0.70.0 entry body missing the 'M5 INCLUDE direction' "
        "/code-review SKILL.md scope-shift anchor"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.70.0 entry body missing the '5-part PMI-1 atomic bump' "
        "anchor — slice-069 ships a 5-part bump (VERSION + plugin.yaml + "
        "pyproject.toml + ## v0.70.0 header + installed ai-sdlc-VERSION)"
    )
    assert "Rule reference" in body, (
        "v0.70.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    assert "partial supersession" in body or "partial-supersedes" in body or "partial-supersession" in body, (
        "v0.70.0 entry must state 'partial supersession' (ADR-028 §Options-#1 "
        "only; BCI-1 Decisions 1-3 remain accepted unchanged per ADR-066 "
        "§Supersession scope)"
    )


def test_v_0_70_0_adr_066_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the ADR-066 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #69) so the slice-069 critical path can never silently regress.

    slice-071 / slice-069 M2 FIX (paired-pin completion per slice-069
    code-Critic M2): slice-069 /reflect Step 5.3 added the shippability
    row #69 (partial-discharge — the row exists), but the row's BC-PROJ-10
    paired-pin test function name citations were deferred since the test
    functions themselves did not exist until this slice. slice-071 closes
    the gap by adding both the test functions (this test + its sibling
    above) AND citing them in row #69 (mandatory per BC-PROJ-10:173
    paired-pin schema).

    BCR-1 traceability axis: row #69 MUST cite the new ADR (ADR-066) AND
    the two BC-PROJ-10 paired-pin test function names.

    Rule reference: BC-PROJ-10:173 (paired entry-pin precedent N≥19
    inclusive of this slice); BCR-1 traceability axis.
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-069-track-vault-in-git" in catalog, (
        "architecture/shippability.md must contain a slice-069 row "
        "(catalog row #69 per BC-PROJ-10:173 paired-entry-pin discipline)"
    )
    # Locate the slice-069 row (single line in pipe-table format).
    row_start = catalog.find("slice-069-track-vault-in-git")
    row_end = catalog.find("\n| ", row_start)
    row = catalog[row_start:row_end] if row_end > 0 else catalog[row_start:row_start + 8000]
    assert "ADR-066" in row, (
        "shippability.md row #69 must cite ADR-066 (the new architectural "
        "philosophy) per BCR-1 traceability axis"
    )
    assert "test_v_0_70_0_adr_066_entry_present_in_repo" in row, (
        "shippability.md row #69 must cite the entry-pin test function "
        "by canonical name (BC-PROJ-10 paired-pin schema; severing this "
        "axis silently breaks the catalog-row→test traceability). "
        "slice-071 / slice-069 M2 FIX adds this citation."
    )
    assert "test_v_0_70_0_adr_066_shippability_consumer_propagation" in row, (
        "shippability.md row #69 must cite the shippability-consumer-"
        "propagation test function by canonical name (BC-PROJ-10 paired-"
        "pin schema). slice-071 / slice-069 M2 FIX adds this citation."
    )


# ─── slice-072 / PSQ-2 paired-pin (AC6) ────────────────────────────────


def test_v_0_71_0_psq_2_entry_present_in_repo():
    """methodology-changelog v0.71.0 / PSQ-2 parallel-slice queue claim
    machinery entry-pin (content-bearing per slice-067/069 PSQ-1 precedent).

    Asserts substring presences in the v0.71.0 entry body (per ADR-067
    §Decision + design.md §"What's new"):
      (a) `## v0.71.0` dated header
      (b) `PSQ-2` rule reference (the new RULE-ID this entry mints)
      (c) `ADR-067` reference
      (d) `claim machinery` canonical-phrase anchor
      (e) `mints a new rule` (PSQ-2 is a sibling on parallel-slice family
          axis; supersedes nothing per ADR-067 frontmatter)
      (f) `5-part PMI-1 atomic bump` (slice-063/064/066/067/069 canonical
          anchor — VERSION + plugin.yaml.version + pyproject.toml
          [project].version + ## v0.71.0 header + installed
          ~/.claude/ai-sdlc-VERSION; shippability row #72 + venv
          ai-sdlc-tools are SEPARATE consumer-propagation surfaces, NOT
          PMI-1 parts per slice-067 M-add-4 leg-enumeration discipline)
      (g) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
      (h) `Claimed-by` AND `Claimed-at` (the 2 additive schema field
          literals — the stable on-disk contract PSQ-2 ships)
      (i) `git config user` (git-identity-only ownership model per
          ADR-067 §"Options considered" Option 1)
      (j) `R-19` (the risk this slice retires)

    Rule reference: PSQ-2 (slice-072; ADR-067 mints a new rule; sibling on
    parallel-slice family axis; methodology v0.71.0).
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.71.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.71.0 entry header — "
        "slice-072 PSQ-2 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.71.0")
    assert "PSQ-2" in body, (
        "v0.71.0 entry body missing the 'PSQ-2' rule reference — "
        "entry-pin broken at the rule-reference layer (this slice MINTS "
        "PSQ-2 as a new audit-enforced rule)"
    )
    assert "ADR-067" in body, (
        "v0.71.0 entry body must reference ADR-067 (the new ADR minting PSQ-2)"
    )
    assert "claim machinery" in body.lower(), (
        "v0.71.0 entry body missing the 'claim machinery' canonical phrase "
        "anchor — PSQ-2's name"
    )
    assert "mints a new rule" in body, (
        "v0.71.0 entry must state 'mints a new rule' (PSQ-2 is a NEW "
        "audit-enforced rule; sibling on parallel-slice family axis; "
        "supersedes nothing per ADR-067)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.71.0 entry body missing the '5-part PMI-1 atomic bump' anchor "
        "— slice-072 ships a 5-part bump (VERSION + plugin.yaml + "
        "pyproject.toml + ## v0.71.0 header + installed ai-sdlc-VERSION) "
        "per slice-063/064/066/067/069 canonical anchor."
    )
    assert "Rule reference" in body, (
        "v0.71.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    assert "Claimed-by" in body, (
        "v0.71.0 entry must enumerate the 'Claimed-by' schema field "
        "literal (the stable on-disk contract PSQ-2 ships)"
    )
    assert "Claimed-at" in body, (
        "v0.71.0 entry must enumerate the 'Claimed-at' schema field "
        "literal (the stable on-disk contract PSQ-2 ships)"
    )
    assert "git config user" in body, (
        "v0.71.0 entry must reference 'git config user' (git-identity-only "
        "ownership model per ADR-067 §Options considered Option 1)"
    )
    assert "R-19" in body, (
        "v0.71.0 entry must cite R-19 (the risk this slice retires)"
    )


def test_v_0_71_0_psq_2_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the PSQ-2 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #72) so the slice-072 critical path can never silently regress.

    BCR-1 traceability axis: row #72 MUST cite the new RULE-ID (PSQ-2)
    AND the new ADR (ADR-067) AND the two BC-PROJ-10 paired-pin test
    function names.

    Rule reference: BC-PROJ-10:173 (paired entry-pin precedent N≥20
    inclusive of this slice); BCR-1 traceability axis.
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-072-add-psq-2-claim-machinery" in catalog, (
        "architecture/shippability.md must contain a slice-072 row "
        "(catalog row #72 per BC-PROJ-10:173 paired-entry-pin discipline)"
    )
    row_start = catalog.find("slice-072-add-psq-2-claim-machinery")
    row_end = catalog.find("\n| ", row_start)
    row = catalog[row_start:row_end] if row_end > 0 else catalog[row_start:row_start + 8000]
    assert "PSQ-2" in row, (
        "shippability.md row #72 must cite PSQ-2 (the new RULE-ID) per "
        "BCR-1 traceability axis"
    )
    assert "ADR-067" in row, (
        "shippability.md row #72 must cite ADR-067 (the new ADR) per "
        "BCR-1 traceability axis"
    )
    assert "test_v_0_71_0_psq_2_entry_present_in_repo" in row, (
        "shippability.md row #72 must cite the entry-pin test function "
        "by canonical name (BC-PROJ-10 paired-pin schema)"
    )
    assert "test_v_0_71_0_psq_2_shippability_consumer_propagation" in row, (
        "shippability.md row #72 must cite the shippability-consumer-"
        "propagation test function by canonical name (BC-PROJ-10 "
        "paired-pin schema)"
    )
    assert ("claim" in row.lower()) or ("psq-2" in row.lower()), (
        "shippability.md row #72 must reference 'claim' or 'PSQ-2' for "
        "catalog-runner discoverability"
    )


def test_v_0_72_0_psq_3_entry_present_in_repo():
    """methodology-changelog v0.72.0 / PSQ-3 rebase-and-conflict discipline
    entry-pin (content-bearing per slice-072 PSQ-2 / slice-067 PSQ-1 precedent).

    Asserts substring presences in the v0.72.0 entry body (per ADR-068
    §Decision + design.md §"What's new"):
      (a) `## v0.72.0` dated header
      (b) `PSQ-3` rule reference (the new RULE-ID this entry mints)
      (c) `ADR-068` reference
      (d) `rebase-and-conflict` OR `rebase-onto-default` canonical-phrase
          anchor (PSQ-3's name)
      (e) `mints a new rule` (PSQ-3 is a sibling on parallel-slice family
          axis; supersedes nothing per ADR-068 frontmatter)
      (f) `5-part PMI-1 atomic bump` (slice-063/064/066/067/069/072
          canonical anchor — VERSION + plugin.yaml.version + pyproject.toml
          [project].version + ## v0.72.0 header + installed
          ~/.claude/ai-sdlc-VERSION; shippability row #73 + venv
          ai-sdlc-tools are SEPARATE consumer-propagation surfaces, NOT
          PMI-1 parts per slice-067 M-add-4 leg-enumeration discipline)
      (g) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
      (h) `git rebase` (the runtime gate literal — PSQ-3's behavior surface)
      (i) `git rebase --abort` (the recovery hint literal — PSQ-3's
          conflict-STOP surface)
      (j) `Step 5b` (the insertion site — PSQ-3 inserts sub-step 2.5 between
          existing sub-step 2 and sub-step 3 of /commit-slice --merge)
      (k) `--merge` (the scope-limited sub-mode — out-of-scope: --push and
          --sync-after-pr per ADR-068 §Options-#2)
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.72.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.72.0 entry header — "
        "slice-073 PSQ-3 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.72.0")
    assert "PSQ-3" in body, (
        "v0.72.0 entry body missing the 'PSQ-3' rule reference — "
        "entry-pin broken at the rule-reference layer (this slice MINTS "
        "PSQ-3 as a new audit-enforced rule)"
    )
    assert "ADR-068" in body, (
        "v0.72.0 entry body must reference ADR-068 (the new ADR minting PSQ-3)"
    )
    body_lower = body.lower()
    assert ("rebase-and-conflict" in body_lower) or ("rebase-onto-default" in body_lower), (
        "v0.72.0 entry body missing the 'rebase-and-conflict' OR "
        "'rebase-onto-default' canonical phrase anchor — PSQ-3's name"
    )
    assert "mints a new rule" in body, (
        "v0.72.0 entry must state 'mints a new rule' (PSQ-3 is a NEW "
        "audit-enforced rule; sibling on parallel-slice family axis; "
        "supersedes nothing per ADR-068)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.72.0 entry body missing the '5-part PMI-1 atomic bump' anchor "
        "— slice-073 ships a 5-part bump (VERSION + plugin.yaml + "
        "pyproject.toml + ## v0.72.0 header + installed ai-sdlc-VERSION) "
        "per slice-063/064/066/067/069/072 canonical anchor."
    )
    assert "Rule reference" in body, (
        "v0.72.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )
    assert "git rebase" in body, (
        "v0.72.0 entry must reference 'git rebase' (the runtime gate "
        "literal — PSQ-3's behavior surface; design.md L74 invocation)"
    )
    assert "git rebase --abort" in body, (
        "v0.72.0 entry must reference 'git rebase --abort' (the recovery "
        "hint literal — PSQ-3's conflict-STOP surface; design.md §Error model)"
    )
    assert "Step 5b" in body, (
        "v0.72.0 entry must reference 'Step 5b' (the insertion site for "
        "PSQ-3's new sub-step 2.5)"
    )
    assert "--merge" in body, (
        "v0.72.0 entry must reference '--merge' (the scope-limited sub-mode; "
        "--push + --sync-after-pr are out of scope per ADR-068 §Options-#2)"
    )


def test_v_0_72_0_psq_3_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the PSQ-3 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #73) so the slice-073 critical path can never silently regress.

    BCR-1 traceability axis: row #73 MUST cite the new RULE-ID (PSQ-3)
    AND the new ADR (ADR-068) AND the two BC-PROJ-10 paired-pin test
    function names AND the structural-pin test module name.

    Rule reference: BC-PROJ-10:173 (paired entry-pin precedent N≥21
    inclusive of this slice); BCR-1 traceability axis.
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-073-add-rebase-and-conflict-discipline" in catalog, (
        "architecture/shippability.md must contain a slice-073 row "
        "(catalog row #73 per BC-PROJ-10:173 paired-entry-pin discipline)"
    )
    row_start = catalog.find("slice-073-add-rebase-and-conflict-discipline")
    row_end = catalog.find("\n| ", row_start)
    row = catalog[row_start:row_end] if row_end > 0 else catalog[row_start:row_start + 8000]
    assert "PSQ-3" in row, (
        "shippability.md row #73 must cite PSQ-3 (the new RULE-ID) per "
        "BCR-1 traceability axis"
    )
    assert "ADR-068" in row, (
        "shippability.md row #73 must cite ADR-068 (the new ADR) per "
        "BCR-1 traceability axis"
    )
    assert "test_v_0_72_0_psq_3_entry_present_in_repo" in row, (
        "shippability.md row #73 must cite the entry-pin test function "
        "by canonical name (BC-PROJ-10 paired-pin schema)"
    )
    assert "test_v_0_72_0_psq_3_shippability_consumer_propagation" in row, (
        "shippability.md row #73 must cite the shippability-consumer-"
        "propagation test function by canonical name (BC-PROJ-10 "
        "paired-pin schema)"
    )
    assert "test_commit_slice_skill_rebase_flag" in row, (
        "shippability.md row #73 must cite the structural-pin test module "
        "name (`test_commit_slice_skill_rebase_flag.py` / 5 prose-pin tests) "
        "— the runtime invocation gate"
    )
    assert ("rebase" in row.lower()) or ("psq-3" in row.lower()), (
        "shippability.md row #73 must reference 'rebase' or 'PSQ-3' for "
        "catalog-runner discoverability"
    )


# Note: test_version_files_synchronized_at_v_0_72_0 (slice-073) deleted at
# slice-076 / PCR-1 PMI-1 5-leg bump 0.72.0 → 0.73.0 per the time-locked
# version-sync test convention (only the latest version's sync test exists;
# prior bumps' sync tests are deleted at each bump per slice-073/074
# precedent). The current-version sync test is
# test_version_files_synchronized_at_v_0_73_0 below.


# --- Slice-076 / PCR-1 entry pinning ---

def test_v_0_73_0_pcr_1_entry_present_in_repo():
    """methodology-changelog v0.73.0 / PCR-1 parallel-conflict-resolution v1
    entry-pin (content-bearing per slice-073 PSQ-3 / slice-072 PSQ-2 / slice-067
    PSQ-1 precedent).

    Asserts the 5 load-bearing substring anchors specified at design.md L21
    (per /critique m3 ACCEPTED-FIXED + /critique-review M-add-3 precedent
    harmonization), plus the META-1 mandatory enforcing-assertion + the
    canonical 5-part PMI-1 atomic bump phrase:
      (a) `## v0.73.0` dated header
      (b) `PCR-1` rule reference (the new RULE-ID this entry mints)
      (c) `ADR-069` reference
      (d) `parallel-conflict-resolution` canonical phrase (PCR-1's family axis)
      (e) `mints a new rule` (PCR-1 is the first rule on a new family axis
          sibling to PSQ-N; supersedes nothing per ADR-069 frontmatter)
      (f) `5-part PMI-1 atomic bump` (slice-063/064/066/067/069/072/073
          canonical 5-part anchor — VERSION + plugin.yaml.version +
          pyproject.toml [project].version + ## v0.73.0 header + installed
          ~/.claude/ai-sdlc-VERSION; shippability row #76 + venv ai-sdlc-tools
          are SEPARATE consumer-propagation surfaces, NOT PMI-1 parts per
          slice-067 M-add-4 leg-enumeration discipline)
      (g) `Rule reference` literal (META-1 mandatory enforcing-assertion
          obligation at `test_methodology_changelog.py:136`)
    """
    in_repo = read_file("methodology-changelog.md")
    assert "## v0.73.0" in in_repo, (
        "in-repo methodology-changelog.md missing v0.73.0 entry header — "
        "slice-076 PCR-1 entry was not added or was lost"
    )
    body = _extract_version_body(in_repo, "0.73.0")
    assert "PCR-1" in body, (
        "v0.73.0 entry body missing the 'PCR-1' rule reference — "
        "entry-pin broken at the rule-reference layer (this slice MINTS "
        "PCR-1 as a new rule on the parallel-conflict-resolution family axis)"
    )
    assert "ADR-069" in body, (
        "v0.73.0 entry body must reference ADR-069 (the new ADR minting PCR-1)"
    )
    assert "parallel-conflict-resolution" in body, (
        "v0.73.0 entry body missing the 'parallel-conflict-resolution' "
        "canonical phrase anchor — PCR-1's family axis name"
    )
    assert "mints a new rule" in body, (
        "v0.73.0 entry must state 'mints a new rule' (PCR-1 is the first "
        "rule on the parallel-conflict-resolution family axis sibling to "
        "PSQ-N; supersedes nothing per ADR-069)"
    )
    assert "5-part PMI-1 atomic bump" in body, (
        "v0.73.0 entry body missing the '5-part PMI-1 atomic bump' anchor "
        "— slice-076 ships a 5-part bump (VERSION + plugin.yaml + "
        "pyproject.toml + ## v0.73.0 header + installed ai-sdlc-VERSION) "
        "per slice-063/064/066/067/069/072/073 canonical anchor."
    )
    assert "Rule reference" in body, (
        "v0.73.0 entry missing the literal 'Rule reference' line — "
        "META-1 entry-pin obligation unmet"
    )


def test_v_0_73_0_pcr_1_shippability_consumer_propagation():
    """RPCD-1/SCPD-1 consumer-reference propagation: the PCR-1 consumer
    reference MUST propagate into `architecture/shippability.md` (catalog
    row #76) so the slice-076 critical path can never silently regress.

    BCR-1 traceability axis: row #76 MUST cite the new RULE-ID (PCR-1)
    AND the new ADR (ADR-069) AND the two BC-PROJ-10 paired-pin test
    function names AND the structural-pin test module name.

    Rule reference: BC-PROJ-10:176 (paired entry-pin precedent N≥22
    inclusive of this slice); BCR-1 traceability axis.
    """
    catalog = read_file("architecture/shippability.md")
    assert "slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen" in catalog, (
        "architecture/shippability.md must contain a slice-076 row "
        "(catalog row #76 per BC-PROJ-10:176 paired-entry-pin discipline)"
    )
    row_start = catalog.find("slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen")
    row_end = catalog.find("\n| ", row_start)
    row = catalog[row_start:row_end] if row_end > 0 else catalog[row_start:row_start + 8000]
    assert "PCR-1" in row, (
        "shippability.md row #76 must cite PCR-1 (the new RULE-ID) per "
        "BCR-1 traceability axis"
    )
    assert "ADR-069" in row, (
        "shippability.md row #76 must cite ADR-069 (the new ADR) per "
        "BCR-1 traceability axis"
    )
    assert "test_v_0_73_0_pcr_1_entry_present_in_repo" in row, (
        "shippability.md row #76 must cite the entry-pin test function "
        "by canonical name (BC-PROJ-10 paired-pin schema)"
    )
    assert "test_v_0_73_0_pcr_1_shippability_consumer_propagation" in row, (
        "shippability.md row #76 must cite the shippability-consumer-"
        "propagation test function by canonical name (BC-PROJ-10 "
        "paired-pin schema)"
    )
    assert "parallel_conflict_resolver" in row, (
        "shippability.md row #76 must reference 'parallel_conflict_resolver' "
        "(the new tool module) for catalog-runner discoverability"
    )


def test_version_files_synchronized_at_v_0_73_0():
    """AC5 — 5-part PMI-1 atomic bump 0.72.0 → 0.73.0.

    Verifies the 5 canonical version-bearing legs are synchronized at
    `0.73.0` post-bump:
      (1) `VERSION` file
      (2) `plugin.yaml` version field
      (3) `pyproject.toml [project].version` field (PVFS-1)
      (4) `## v0.73.0` header in `methodology-changelog.md`
      (5) installed `~/.claude/ai-sdlc-VERSION` (AVFS-1; verified separately
          by the AVFS-1 audit; this test asserts legs 1-4 only — leg 5 is
          environment-dependent and may be absent on a fresh checkout,
          where AVFS-1 returns WARN per slice-030A meta-M3 parity)

    Per slice-063/064/066/067/069/072/073 canonical 5-part PMI-1 anchor. The
    test is intentionally tolerant of leg 5's absence — that leg is gated
    by AVFS-1's own deterministic downstream gate at /build-slice Step 6.
    """
    version = read_file("VERSION").strip()
    assert version == "0.73.0", (
        f"VERSION file must equal '0.73.0' post-bump; got {version!r}. "
        "5-part PMI-1 leg 1 broken — re-run the bump or fix VERSION manually."
    )
    plugin_yaml = read_file("plugin.yaml")
    assert "version: 0.73.0" in plugin_yaml or 'version: "0.73.0"' in plugin_yaml, (
        "plugin.yaml must contain 'version: 0.73.0' post-bump (5-part PMI-1 leg 2)"
    )
    pyproject = read_file("pyproject.toml")
    assert 'version = "0.73.0"' in pyproject, (
        "pyproject.toml [project].version must equal '0.73.0' post-bump (PVFS-1; "
        "5-part PMI-1 leg 3)"
    )
    changelog = read_file("methodology-changelog.md")
    assert "## v0.73.0" in changelog, (
        "methodology-changelog.md must contain '## v0.73.0' header post-bump "
        "(5-part PMI-1 leg 4)"
    )
