"""Pin load-bearing prose in agents/critique.md.

The Critic prompt is the most adversarially-load-bearing artifact in the pipeline.
Drift here directly degrades review quality.
"""
from tests.methodology.conftest import read_file

CRITIQUE = read_file("agents/critique.md")


def test_critique_carries_adversarial_stance():
    """The Critic must carry an explicit adversarial stance.

    Defect class: Stance softening — paraphrasing to "review the design" loses the
    adversarial property. The Critic that asks rather than attacks is a rubber stamp.
    Rule reference: META-2.
    """
    assert "Assume the design is wrong until proven right" in CRITIQUE


def test_critique_forbids_softening_findings():
    """The Critic must not soften findings to be diplomatic.

    Defect class: Diplomatic findings train the Builder to ignore the Critic, which
    breaks the calibration loop and reverts the pipeline to single-AI quality gates.
    Rule reference: META-2.
    """
    assert "Do not soften findings" in CRITIQUE


def test_critique_forbids_manufactured_findings():
    """The Critic must not manufacture findings to justify the review.

    Defect class: Manufactured findings damage the calibration loop and train the
    Builder to ignore the Critic. Manufactured findings make the Critic worse over time.
    Rule reference: META-2.
    """
    assert "Do NOT manufacture findings to justify the review" in CRITIQUE


def test_critique_lists_nine_dimensions():
    """The Critic must walk all nine review dimensions.

    Defect class: Dimension drift — collapsing the nine named dimensions into a
    single "look for issues" instruction loses the perspective-based-reading benefit.
    Rule reference: META-2 + CCC-1 (slice-006 added Dim 9 cross-cutting conformance).
    """
    assert "1. Unfounded assumptions" in CRITIQUE
    assert "2. Missing edge cases" in CRITIQUE
    assert "3. Over-engineering" in CRITIQUE
    assert "4. Under-engineering" in CRITIQUE
    assert "5. Contract gaps" in CRITIQUE
    assert "6. Security" in CRITIQUE
    assert "7. Drift from vault" in CRITIQUE
    assert "8. Web-known issues" in CRITIQUE
    assert "9. Cross-cutting conformance" in CRITIQUE


def test_critique_names_reference_frameworks():
    """The Critic must cite specific named frameworks per dimension.

    Defect class: Citation collapse — dropping named experts replaces vetted
    methodology with blended training-data heuristics.
    Rule reference: META-2.
    """
    assert "Wiegers" in CRITIQUE
    assert "Fowler" in CRITIQUE
    assert "Newman" in CRITIQUE
    assert "OWASP" in CRITIQUE
    assert "McGraw" in CRITIQUE
    assert "Hendrickson" in CRITIQUE


def test_critique_specifies_severity_levels():
    """The Critic must distinguish Blocker / Major / Minor severity.

    Defect class: Severity inflation or collapse — flat severity makes blockers
    meaningless and trains the Builder to dismiss the Critic.
    Rule reference: META-2.
    """
    assert "**Blocker**" in CRITIQUE
    assert "**Major**" in CRITIQUE
    assert "**Minor**" in CRITIQUE


def test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet():
    """Dim 1 must carry the tooling-doc-vs-implementation parity surgical sub-bullet.

    Defect class: in-house audit docstrings drift from their regex/parser/keyword-list
    implementations; the Critic must explicitly verify implementation, not documentation,
    when design.md cites an existing audit's expected format. Promoted from /critic-calibrate
    2026-05-10 ACCEPTED proposal (3 misses across slice-001/002/003); back-synced from
    installed copy to in-repo canonical source per /critique 2026-05-10 B1.
    Rule reference: META-2 + CCC-1.
    """
    assert "Verify by reading the implementation" in CRITIQUE
    assert "TF-1, RR-1, BC-1, WIRE-1, NFR-1, VAL-1, CSP-1" in CRITIQUE


def test_critique_dim_4_has_methodology_audit_conformance_sub_bullet():
    """Dim 4 must carry the methodology-audit conformance surgical sub-bullet with three sub-sub-bullets.

    Defect class: slices' designs and test-first plans fail in-house audits at /build-slice
    pre-finish (TF-1 row coverage, TF-1 PENDING→WRITTEN-FAILING genuineness, algorithm-path
    interaction with pre-existing branches). Promoted from /critic-calibrate 2026-05-10
    ACCEPTED proposal (3 misses across slice-002/003/005); back-synced from installed copy
    to in-repo canonical source per /critique 2026-05-10 B1.
    Rule reference: META-2 + CCC-1.
    """
    assert "Methodology-audit conformance" in CRITIQUE
    assert "TF-1 row coverage" in CRITIQUE
    assert "Algorithm-path-conformance with pre-existing branches" in CRITIQUE


def test_critique_dim_9_lists_eleven_sub_clauses():
    """Dim 9 (Cross-cutting conformance) must enumerate all 11 sub-clause titles.

    Defect class: a Dim 9 body that drops sub-clauses loses the unified-pattern surface
    (e.g., dropping runtime-environment leaves slice-001-class misses without a home).
    The 11 sub-clauses are: 3 cross-references to Dim 1/4 surgical sub-bullets +
    2 N=1 standalone sub-clauses (runtime-environment, language-version) +
    1 N=3 meta-level sub-clause (recursive self-application discipline; slice-011) +
    1 N=2 Edit-discipline sub-clause (entry-pin-vs-PMI-1-gate semantics conflation;
    slice-013) +
    1 N=2 cross-Phase-propagation sub-clause (shippability-catalog consumer-reference
    propagation; slice-015) +
    1 N=3 runtime-prerequisite-completeness sub-clause (runtime-prerequisite completeness
    on proposed fixes; slice-016) +
    1 N=10-cumulative-cross-instance / N=4-distinct-slice fix-block-completeness sub-clause
    (fix-block-completeness discipline; slice-024) +
    1 N=2-distinct-slice phantom-test-file-citation sub-clause (phantom test-file
    citation discipline; slice-025).

    Supersedes `test_critique_dim_9_lists_ten_sub_clauses` per PMI-1 versioned-gate
    supersession discipline applied at the structural-invariant level (slice-011 N=1
    precedent + slice-013 N=2 + slice-015 N=3 + slice-016 N=4 + slice-024 N=5 +
    slice-025 N=6 stable — no two structural-invariant tests coexist).

    Rule reference: META-2 + CCC-1 + RSAD-1 (slice-011) + EPGD-1 (slice-013) + SCPD-1
    (slice-015) + RPCD-1 (slice-016) + FBCD-1 (slice-024) + PTFCD-1 (slice-025).
    """
    assert "Methodology-audit conformance" in CRITIQUE
    assert "Tooling-doc-vs-implementation parity" in CRITIQUE
    assert "Algorithm-path-conformance" in CRITIQUE
    assert "Runtime-environment" in CRITIQUE
    assert "Language-version conformance" in CRITIQUE
    assert "Recursive self-application discipline" in CRITIQUE
    assert "Entry-pin-vs-PMI-1-gate semantics conflation" in CRITIQUE
    assert "Shippability-catalog consumer-reference propagation" in CRITIQUE
    assert "Runtime-prerequisite completeness on proposed fixes" in CRITIQUE
    assert "Fix-block-completeness discipline" in CRITIQUE
    assert "Phantom test-file citation discipline" in CRITIQUE


def test_critique_dim_9_recursive_self_application_sub_clause_present():
    """The new 6th Dim 9 sub-clause must carry the canonical literal title.

    Defect class: a Dim 9 body that has the substring but not as a sub-clause title
    (e.g., embedded in narrative prose elsewhere) would silently pass without
    encoding the discipline as a structural sub-clause. The canonical literal pin
    is a substring assertion; the location-pin test (below) enforces position.
    Rule reference: META-2 + CCC-1 + RSAD-1.
    """
    assert "Recursive self-application discipline" in CRITIQUE


def test_critique_dim_9_recursive_self_application_location_pinned():
    """The new 6th sub-clause must fall between Language-version conformance and the Bonus H3.

    Defect class: a future drift moving the new sub-clause out of Dim 9 (e.g., into Dim 8
    or the Bonus section) would silently pass substring-only pin tests; the location-pin
    guard catches it. Per slice-009 M1 + slice-010 M1 location-pin convention; per
    slice-009 DEVIATION-2 + slice-010 anchor-uniqueness pre-emption: anchors verified
    unique pre-AC-lock; scoped .find() to avoid first-occurrence-wins collision.

    Location pin: sub-clause title MUST appear BETWEEN start anchor
    `Language-version conformance` AND end anchor `### Bonus: weak graph edges`.

    Rule reference: META-2 + CCC-1 + RSAD-1.
    """
    start_anchor = "Language-version conformance"
    end_anchor = "Phantom test-file citation discipline"
    canonical = "Recursive self-application discipline"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )


def test_critique_dim_9_recursive_self_application_names_both_sub_modes():
    """Sub-clause body must name BOTH design-time and build-time sub-modes.

    Defect class: a body that only names design-time loses the build-time-via-/critique-
    fix-prose sub-mode (slice-010 DEVIATION-3 evidence) — incomplete coverage of the N=3
    cumulative evidence base.

    Per slice-009 DEVIATION-1 case-sensitivity mitigation: canonical substrings
    `design-time` AND `build-time` are lowercase compound forms placed mid-sentence in
    the body prose (per slice-011 Critic B1 catch + fix: bullet titles capitalized,
    lowercase canonical substrings relocated to mid-sentence positions).

    Per slice-013 /critique M1 ACCEPTED-PENDING: end_anchor tightened from
    `### Bonus: weak graph edges` → `Entry-pin-vs-PMI-1-gate semantics conflation`
    (the new 7th sub-clause title) so body bounds remain scoped to ONLY the 6th
    sub-clause (RSAD-1) — preserves regression-guard precision after slice-013's
    7th sub-clause append. Symmetric pin for the new 7th sub-clause body lives in
    `test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes` below.

    Rule reference: META-2 + CCC-1 + RSAD-1 + EPGD-1 (slice-013 M1 end_anchor tighten).
    """
    start_anchor = "Recursive self-application discipline"
    end_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER sub-clause start"
    body = CRITIQUE[start_idx:end_idx]
    assert "design-time" in body, (
        "sub-clause body missing canonical substring 'design-time' "
        "(case-sensitive; must appear mid-sentence per slice-009 DEVIATION-1 mitigation)"
    )
    assert "build-time" in body, (
        "sub-clause body missing canonical substring 'build-time' "
        "(case-sensitive; must appear mid-sentence per slice-009 DEVIATION-1 mitigation)"
    )


def test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors():
    """Sub-clause body must cite BOTH cross-slice anchors + ≥1 sub-class anchor.

    Defect class: descriptive sub-class text drifts unpinned to abstract framings without
    concrete traceability — readers lose the path back to the empirical evidence base.
    Pinned at N=3 evidence (slice-009 M2 + slice-010 design-time + slice-010 build-time).

    Per slice-011 Critic m2 catch + fix: with 2-element cross-slice allowlist, the
    `≥2 of 2` semantics is strict-both not permissive — body must cite BOTH slice-009
    AND slice-010 (not "at least 2 of {slice-009, slice-010}").

    Per slice-008 M2 + slice-009 M3 + slice-010 M3 N-substring + N-surface schema-pin
    discipline.

    Per slice-013 /critique M-add-1 ACCEPTED-PENDING (meta-Critic catch, missed by
    first Critic): end_anchor tightened from `### Bonus: weak graph edges` →
    `Entry-pin-vs-PMI-1-gate semantics conflation` (the new 7th sub-clause title)
    so body bounds remain scoped to ONLY the 6th sub-clause (RSAD-1). Without this
    tighten, the `M1` substring leaks from slice-013's 7th sub-clause body into the
    sc_count regression-guard, silently satisfying `sc_count >= 1` if the 6th
    sub-clause body lost all its sub-class anchors. Symmetric pin for the new 7th
    sub-clause body lives in
    `test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors`.

    Rule reference: META-2 + CCC-1 + RSAD-1 + EPGD-1 (slice-013 M-add-1 end_anchor
    tighten, dual-review catch per DR-1).
    """
    start_anchor = "Recursive self-application discipline"
    end_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-009", "slice-010"]
    sub_class = ["M2", "DEVIATION-3", "BC-PROJ-2", "B1", "B5", "M1"]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sc_count = sum(1 for anchor in sub_class if anchor in body)
    assert cs_count == 2, (
        f"strict-both cross-slice anchor requirement — need BOTH of {cross_slice}, "
        f"got {cs_count} present in sub-clause body"
    )
    assert sc_count >= 1, (
        f"insufficient sub-class instance anchors — need ≥1 of {sub_class}, "
        f"got {sc_count} in sub-clause body"
    )


def test_critique_dim_9_entry_pin_vs_pmi_1_gate_sub_clause_present():
    """The new 7th Dim 9 sub-clause must carry the canonical literal title.

    Defect class: a Dim 9 body that has the substring but not as a sub-clause title
    (e.g., embedded in narrative prose elsewhere) would silently pass without
    encoding the discipline as a structural sub-clause. The canonical literal pin
    is a substring assertion; the location-pin test (below) enforces position.

    Slice-013's own ship is the canonical reference instance of EPGD-1 self-application
    (RSAD-1 self-application N=5 cumulative).

    Rule reference: META-2 + CCC-1 + EPGD-1 (slice-013).
    """
    assert "Entry-pin-vs-PMI-1-gate semantics conflation" in CRITIQUE


def test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned():
    """The new 7th sub-clause must fall between RSAD-1 sub-clause close and the Bonus H3.

    Defect class: a future drift moving the new sub-clause out of Dim 9 (e.g., into Dim 8
    or the Bonus section) would silently pass substring-only pin tests; the location-pin
    guard catches it. Per slice-009 M1 + slice-010 M1 + slice-011 location-pin convention;
    per slice-009 DEVIATION-2 + slice-010 anchor-uniqueness pre-emption: anchors verified
    unique pre-AC-lock at /design-slice Audit 1 (`Recursive self-application discipline`
    appears exactly once at L168; `### Bonus: weak graph edges` appears exactly once at
    pre-Phase-1a L174 → post-Phase-1a L180); scoped .find() to avoid first-occurrence-wins
    collision.

    Location pin: 7th sub-clause title MUST appear BETWEEN start anchor
    `Recursive self-application discipline` AND end anchor `### Bonus: weak graph edges`.

    Rule reference: META-2 + CCC-1 + EPGD-1.
    """
    start_anchor = "Recursive self-application discipline"
    end_anchor = "Phantom test-file citation discipline"
    canonical = "Entry-pin-vs-PMI-1-gate semantics conflation"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )


def test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes():
    """7th sub-clause body must name BOTH build-time slip + design-time-pre-empted success sub-modes.

    Defect class: a body that only names build-time-slip loses the
    design-time-pre-empted-success sub-mode (slice-012 N=2 evidence) — incomplete
    coverage of the N=2 cumulative evidence base. Symmetric pin for the new 7th
    sub-clause body (mirrors slice-011's `_names_both_sub_modes` for the 6th
    sub-clause body), per slice-013 /critique M1 ACCEPTED-PENDING extension to
    the new sub-clause.

    Per slice-009 DEVIATION-1 case-sensitivity mitigation: canonical substrings
    `Build-time slip mode` AND `Design-time-pre-empted success mode` are
    capitalized bullet titles per slice-011 Critic B1 catch + fix (bullet titles
    capitalized, lowercase canonical substrings relocated to mid-sentence
    positions).

    Per slice-015 /critique M1 ACCEPTED-PENDING: end_anchor tightened from
    `### Bonus: weak graph edges` → `Shippability-catalog consumer-reference propagation`
    (the new 8th sub-clause title) so body bounds remain scoped to ONLY the 7th
    sub-clause (EPGD-1) — preserves regression-guard precision after slice-015's
    8th sub-clause append. Mirrors slice-013 M1 mitigation pattern applied to
    slice-011's body-bound tests at slice-013 — generic methodology recurrence:
    every future Dim 9 sub-clause append tightens its predecessor's body-bound
    tests' end_anchors to the new sub-clause's title.

    Rule reference: META-2 + CCC-1 + EPGD-1 (slice-013 M1 symmetric add) + SCPD-1
    (slice-015 M1 end_anchor tighten).
    """
    start_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"
    end_anchor = "Shippability-catalog consumer-reference propagation"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER sub-clause start"
    body = CRITIQUE[start_idx:end_idx]
    assert "Build-time slip mode" in body, (
        "sub-clause body missing canonical substring 'Build-time slip mode' "
        "(case-sensitive bullet title per slice-011 Critic B1 fix)"
    )
    assert "Design-time-pre-empted success mode" in body, (
        "sub-clause body missing canonical substring 'Design-time-pre-empted success mode' "
        "(case-sensitive bullet title per slice-011 Critic B1 fix)"
    )


def test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012():
    """7th sub-clause body must cite BOTH cross-slice anchors + ≥2 substantive-discipline anchors.

    Defect class: descriptive sub-class text drifts unpinned to abstract framings without
    concrete traceability — readers lose the path back to the empirical evidence base.
    Pinned at N=2 evidence (slice-011 N=1 build-time slip + slice-012 N=2 design-time-
    pre-empted success).

    Per slice-013 /critique M2 ACCEPTED-FIXED (anchor list formalization per slice-011
    `_cites_at_least_two_cross_slice_anchors` precedent):
      - Cross-slice anchors (strict-both): ["slice-011", "slice-012"] — both MUST be present
      - Substantive-discipline anchors (≥2 of 4): ["Phase 1b INSERT",
        "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]

    Per slice-015 /critique M1 ACCEPTED-PENDING: end_anchor tightened from
    `### Bonus: weak graph edges` → `Shippability-catalog consumer-reference
    propagation` (the new 8th sub-clause title) per generic methodology recurrence.

    Rule reference: META-2 + CCC-1 + EPGD-1 (slice-013 AC #2 + M2 ACCEPTED-FIXED) +
    SCPD-1 (slice-015 M1 end_anchor tighten).
    """
    start_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"
    end_anchor = "Shippability-catalog consumer-reference propagation"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-011", "slice-012"]
    substantive = [
        "Phase 1b INSERT",
        "Phase 1c narrow-scope Edit",
        "Audit 6 structural-separation",
        "SECTION header",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 2, (
        f"strict-both cross-slice anchor requirement — need BOTH of {cross_slice}, "
        f"got {cs_count} present in 7th sub-clause body"
    )
    assert sub_count >= 2, (
        f"insufficient substantive-discipline anchors — need ≥2 of {substantive}, "
        f"got {sub_count} in 7th sub-clause body"
    )


def test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors():
    """Symmetric anchor-citation pin for 7th sub-clause body (mirror of slice-011 test).

    Defect class: symmetric to slice-011's `_cites_at_least_two_cross_slice_anchors`
    on the 6th sub-clause body. Per slice-013 /critique M-add-1 ACCEPTED-PENDING
    (meta-Critic catch via DR-1, missed by first Critic): the 7th sub-clause body
    needs its own symmetric cross-slice + substantive-discipline anchor pin matching
    the discipline applied to the 6th sub-clause body. Without this pin, slice-014+
    refinements to the 7th sub-clause body could drift unpinned to abstract framings
    losing concrete traceability to slice-011 + slice-012 empirical evidence base.

    Per slice-013 /critique M2 ACCEPTED-FIXED anchor list formalization:
      - Cross-slice anchors (strict-both): ["slice-011", "slice-012"]
      - Substantive-discipline anchors (≥2 of 4): ["Phase 1b INSERT",
        "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]

    NOTE: this test's assertions overlap with `_paragraph_cites_slice_011_and_012`
    above — they're intentional duplicates. The naming convention mirrors slice-011's
    test name structure for cross-slice readability (any future Dim 9 sub-clause N+1
    test would similarly mirror this shape). The DEFECT CLASS each catches differs:
    `_paragraph_cites` is the AC #2 acceptance test; this `_cites_at_least_two_cross_slice_anchors`
    is the symmetric-to-slice-011 sibling matching the regression-guard pattern.

    Per slice-015 /critique M1 ACCEPTED-PENDING: end_anchor tightened from
    `### Bonus: weak graph edges` → `Shippability-catalog consumer-reference
    propagation` (the new 8th sub-clause title) per generic methodology recurrence.

    Rule reference: META-2 + CCC-1 + EPGD-1 (slice-013 M-add-1 symmetric add per DR-1) +
    SCPD-1 (slice-015 M1 end_anchor tighten).
    """
    start_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"
    end_anchor = "Shippability-catalog consumer-reference propagation"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-011", "slice-012"]
    substantive = [
        "Phase 1b INSERT",
        "Phase 1c narrow-scope Edit",
        "Audit 6 structural-separation",
        "SECTION header",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 2, (
        f"strict-both cross-slice anchor requirement — need BOTH of {cross_slice}, "
        f"got {cs_count} present in 7th sub-clause body"
    )
    assert sub_count >= 2, (
        f"insufficient substantive-discipline anchors — need ≥2 of {substantive}, "
        f"got {sub_count} in 7th sub-clause body"
    )


# --- Slice-015 / SCPD-1 (8th sub-clause) prose-pin tests ---

def test_critique_dim_9_shippability_catalog_propagation_sub_clause_present():
    """The new 8th Dim 9 sub-clause must carry the canonical literal title.

    Defect class: a Dim 9 body that has the substring but not as a sub-clause title
    would silently pass without encoding the discipline as a structural sub-clause.
    The canonical literal pin is a substring assertion; the location-pin test (below)
    enforces position.
    Rule reference: META-2 + CCC-1 + SCPD-1.
    """
    assert "Shippability-catalog consumer-reference propagation" in CRITIQUE


def test_critique_dim_9_shippability_catalog_propagation_location_pinned():
    """The new 8th sub-clause must fall between EPGD-1 (7th sub-clause) and the Bonus H3.

    Defect class: a future drift moving the new sub-clause out of Dim 9 (e.g., into Dim 8
    or the Bonus section) would silently pass substring-only pin tests; the location-pin
    guard catches it. Per slice-009 M1 + slice-010 M1 + slice-013 location-pin convention.
    Per slice-009 DEVIATION-2 + slice-010 + slice-013 anchor-uniqueness pre-emption:
    anchors verified unique pre-AC-lock; scoped .find() to avoid first-occurrence-wins
    collision.

    Location pin: sub-clause title MUST appear BETWEEN start anchor
    `Entry-pin-vs-PMI-1-gate semantics conflation` (7th sub-clause title — slice-013)
    AND end anchor `### Bonus: weak graph edges`.

    Rule reference: META-2 + CCC-1 + SCPD-1.
    """
    start_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"
    end_anchor = "Phantom test-file citation discipline"
    canonical = "Shippability-catalog consumer-reference propagation"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )


def test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes():
    """8th sub-clause body must name BOTH reactive-catch + proactive-application sub-modes.

    Defect class: a body that only names one sub-mode loses coverage of the N=2 cumulative
    evidence base (slice-013 reactive + slice-014 proactive). Symmetric pin for the new 8th
    sub-clause body (mirrors slice-011 RSAD-1 `_names_both_sub_modes` for 6th + slice-013
    EPGD-1 `_names_both_sub_modes` for 7th sub-clause body shapes).

    Per slice-011 Critic B1 + slice-013 case-sensitivity mitigation: canonical substrings
    `Reactive-catch mode` AND `Proactive-application mode` are capitalized bullet titles.

    Per slice-016 /critique B1 ACCEPTED-FIXED tighten provenance (mirrors slice-013 M1 +
    slice-015 M1 convention): end_anchor tightened from `"### Bonus: weak graph edges"` to
    `"Runtime-prerequisite completeness on proposed fixes"` (the 9th sub-clause title;
    slice-016 RPCD-1 codification) to preserve 8th sub-clause regression-guard precision
    after 9th sub-clause append. Generic methodology recurrence N=2 -> N=3 stable.

    Rule reference: META-2 + CCC-1 + SCPD-1 (slice-015 AC #2) + RPCD-1 (slice-016 end_anchor
    tighten per /critique B1 ACCEPTED-FIXED).
    """
    start_anchor = "Shippability-catalog consumer-reference propagation"
    end_anchor = "Runtime-prerequisite completeness on proposed fixes"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER sub-clause start"
    body = CRITIQUE[start_idx:end_idx]
    assert "Reactive-catch mode" in body, (
        "sub-clause body missing canonical substring 'Reactive-catch mode' "
        "(case-sensitive bullet title per slice-011 Critic B1 fix)"
    )
    assert "Proactive-application mode" in body, (
        "sub-clause body missing canonical substring 'Proactive-application mode' "
        "(case-sensitive bullet title per slice-011 Critic B1 fix)"
    )


def test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014():
    """8th sub-clause body must cite BOTH cross-slice anchors + ≥2 substantive-discipline anchors.

    Defect class: descriptive sub-class text drifts unpinned to abstract framings without
    concrete traceability — readers lose the path back to the empirical evidence base.
    Pinned at N=2 evidence (slice-013 N=1 reactive-catch + slice-014 N=2 proactive-application).

    Per slice-015 /critique M2 ACCEPTED-FIXED anchor list formalization (mirrors slice-013
    M2 mitigation precedent N=1 → N=2 stable):
      - Cross-slice anchors (strict-both): ["slice-013", "slice-014"] — both MUST be present
      - Substantive-discipline anchors (≥2 of 4): ["Phase 5", "shippability.md",
        "/validate-slice Step 5.5", "supersession"] — empirically locked at /critique B1
        ACCEPTED-FIXED per literal-substring verification against canonical body (original
        tuple `["Phase 5", "shippability catalog", "consumer reference", "rename propagation"]`
        Blocker-rejected because 3 of 4 use hyphenated or never-present forms)

    Per slice-016 /critique B1 ACCEPTED-FIXED tighten provenance (mirrors slice-013 M1 +
    slice-015 M1 convention): end_anchor tightened from `"### Bonus: weak graph edges"` to
    `"Runtime-prerequisite completeness on proposed fixes"`. Generic methodology recurrence
    N=2 -> N=3 stable.

    Rule reference: META-2 + CCC-1 + SCPD-1 (slice-015 AC #2 + B1 + M2 ACCEPTED-FIXED) +
    RPCD-1 (slice-016 end_anchor tighten per /critique B1 ACCEPTED-FIXED).
    """
    start_anchor = "Shippability-catalog consumer-reference propagation"
    end_anchor = "Runtime-prerequisite completeness on proposed fixes"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-013", "slice-014"]
    substantive = [
        "Phase 5",
        "shippability.md",
        "/validate-slice Step 5.5",
        "supersession",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 2, (
        f"strict-both cross-slice anchor requirement — need BOTH of {cross_slice}, "
        f"got {cs_count} present in 8th sub-clause body"
    )
    assert sub_count >= 2, (
        f"insufficient substantive-discipline anchors — need ≥2 of {substantive}, "
        f"got {sub_count} in 8th sub-clause body"
    )


def test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors():
    """Symmetric anchor-citation pin for 8th sub-clause body (mirror of slice-011 + slice-013 tests).

    Defect class: symmetric to slice-011's `_cites_at_least_two_cross_slice_anchors` on
    the 6th sub-clause body + slice-013's same on the 7th sub-clause body. Per slice-013
    DR-1 codification (meta-Critic-catching-pattern-blindness): every sub-clause body
    needs its own symmetric cross-slice + substantive-discipline anchor pin so future
    refinements don't drift unpinned.

    NOTE: this test's assertions overlap with `_paragraph_cites_slice_013_and_014` above
    — intentional duplicates per slice-013 EPGD-1 convention. The DEFECT CLASS each catches
    differs: `_paragraph_cites` is the AC #2 acceptance test; this `_cites_at_least_two_*`
    is the symmetric-to-slice-011 + slice-013 sibling matching the regression-guard pattern.

    Per slice-016 /critique B1 ACCEPTED-FIXED tighten provenance (mirrors slice-013 M1 +
    slice-015 M1 convention): end_anchor tightened from `"### Bonus: weak graph edges"` to
    `"Runtime-prerequisite completeness on proposed fixes"`. Generic methodology recurrence
    N=2 -> N=3 stable.

    Rule reference: META-2 + CCC-1 + SCPD-1 (slice-015 symmetric add per DR-1 N=3 stable) +
    RPCD-1 (slice-016 end_anchor tighten per /critique B1 ACCEPTED-FIXED).
    """
    start_anchor = "Shippability-catalog consumer-reference propagation"
    end_anchor = "Runtime-prerequisite completeness on proposed fixes"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-013", "slice-014"]
    substantive = [
        "Phase 5",
        "shippability.md",
        "/validate-slice Step 5.5",
        "supersession",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 2, (
        f"strict-both cross-slice anchor requirement — need BOTH of {cross_slice}, "
        f"got {cs_count} present in 8th sub-clause body"
    )
    assert sub_count >= 2, (
        f"insufficient substantive-discipline anchors — need ≥2 of {substantive}, "
        f"got {sub_count} in 8th sub-clause body"
    )


# --- Slice-016 / RPCD-1 (9th sub-clause) prose-pin tests ---

def test_critique_dim_9_runtime_prerequisite_completeness_sub_clause_present():
    """The new 9th Dim 9 sub-clause must carry the canonical literal title.

    Defect class: a Dim 9 body that has the substring but not as a sub-clause title
    would silently pass without encoding the discipline as a structural sub-clause.
    The canonical literal pin is a substring assertion (per slice-015 L463 bare-substring
    precedent); the `_location_pinned` test (below) enforces position. N=3 -> N=4 stable
    `_sub_clause_present` + `_location_pinned` duality post-slice-016 (slice-011 + slice-013
    + slice-015 + slice-016 each carry both tests).

    Rule reference: META-2 + CCC-1 + RPCD-1.
    """
    assert "Runtime-prerequisite completeness on proposed fixes" in CRITIQUE


def test_critique_dim_9_runtime_prerequisite_completeness_location_pinned():
    """The new 9th sub-clause must fall between SCPD-1 (8th sub-clause) and the Bonus H3.

    Defect class: a future drift moving the new sub-clause out of Dim 9 (e.g., into Dim 8
    or the Bonus section) would silently pass substring-only pin tests; the location-pin
    guard catches it. Per slice-009 M1 + slice-010 M1 + slice-013 + slice-015 location-pin
    convention; slice-016 /critique-review M-add-1 ACCEPTED-FIXED — N=3 -> N=4 stable
    `_sub_clause_present` + `_location_pinned` duality (slice-011 L146/158 + slice-013
    L270/286 + slice-015 L463/475 + slice-016).

    Per slice-009 DEVIATION-2 + slice-010/011/013/015 anchor-uniqueness pre-emption:
    anchors verified unique pre-AC-lock; scoped .find() to avoid first-occurrence-wins
    collision.

    Location pin: sub-clause title MUST appear BETWEEN start anchor
    `Shippability-catalog consumer-reference propagation` (8th sub-clause title — slice-015)
    AND end anchor `### Bonus: weak graph edges`.

    Rule reference: META-2 + CCC-1 + RPCD-1.
    """
    start_anchor = "Shippability-catalog consumer-reference propagation"
    end_anchor = "Phantom test-file citation discipline"
    canonical = "Runtime-prerequisite completeness on proposed fixes"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )


def test_critique_dim_9_runtime_prerequisite_completeness_names_three_sub_modes():
    """9th sub-clause body must name ALL THREE sub-modes (a) + (b) + (c).

    Defect class: a body that names only one or two sub-modes loses coverage of the N=3
    cumulative evidence base (slice-013 N=1 sub-mode (c) + slice-014 N=1 sub-mode (a) +
    slice-015 N=1 sub-mode (b)). Symmetric pin for the new 9th sub-clause body (mirrors
    slice-011 RSAD-1 `_names_both_sub_modes` for 6th sub-clause + slice-013 EPGD-1 +
    slice-015 SCPD-1 `_names_both_sub_modes` for 7th/8th sub-clause body shapes —
    extended to three sub-modes given RPCD-1's N=3 evidence base, not two).

    Per slice-011 Critic B1 + slice-013 case-sensitivity mitigation: canonical literals
    `(a)` + `_ALLOWED_STATUSES` + `sibling` are case-sensitive sub-mode anchors derived
    from the canonical body literal-substring set (all 3 verified present at slice-016
    start sha256 `f34c967eaaa34413...`).

    Rule reference: META-2 + CCC-1 + RPCD-1 (slice-016 AC #4). End_anchor
    tightened from `### Bonus: weak graph edges` → `Fix-block-completeness
    discipline` per slice-024 Phase 1e (generic methodology recurrence N=3 → N=4
    stable — every Dim 9 sub-clause append tightens its predecessor's body-bound
    tests' end_anchors to the new sub-clause title; the `_location_pinned`
    sibling keeps `### Bonus:` as structurally load-bearing).
    """
    start_anchor = "Runtime-prerequisite completeness on proposed fixes"
    end_anchor = "Fix-block-completeness discipline"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER sub-clause start"
    body = CRITIQUE[start_idx:end_idx]
    assert "(a)" in body, (
        "9th sub-clause body missing sub-mode (a) marker — "
        "three-sub-mode pin broken"
    )
    assert "_ALLOWED_STATUSES" in body, (
        "9th sub-clause body missing `_ALLOWED_STATUSES` substring — "
        "sub-mode (b) NEW-status/token allowlist-audit discipline anchor broken"
    )
    assert "sibling" in body, (
        "9th sub-clause body missing `sibling` substring — "
        "sub-mode (c) NEW-anchor sibling-grep audit discipline anchor broken"
    )


def test_critique_dim_9_runtime_prerequisite_completeness_paragraph_cites_slice_013_014_015():
    """9th sub-clause body must cite ALL THREE cross-slice anchors + ≥3 substantive-discipline anchors.

    Defect class: descriptive sub-class text drifts unpinned to abstract framings without
    concrete traceability — readers lose the path back to the empirical evidence base.
    Pinned at N=3 evidence (slice-013 N=1 sibling-grep + slice-014 N=1 missing-imports +
    slice-015 N=1 audit-allowlist non-membership).

    Cross-slice anchors (strict-3-of-3): ["slice-013", "slice-014", "slice-015"] — all THREE
    MUST be present (mirrors slice-015 `_paragraph_cites_slice_013_and_014` strict-both
    precedent, extended to strict-three for RPCD-1's N=3 evidence base).

    Substantive-discipline anchors (≥3-of-4): ["import", "_ALLOWED_STATUSES", "sibling",
    "end_anchor"] — empirically verified all 4 present at slice-016 start sha256
    `f34c967eaaa34413...`. Pin at ≥3-of-4 (not strict-4-of-4) to leave one degree of freedom
    for future refinement.

    Rule reference: META-2 + CCC-1 + RPCD-1 (slice-016 AC #4). End_anchor
    tightened from `### Bonus: weak graph edges` → `Fix-block-completeness
    discipline` per slice-024 Phase 1e (generic methodology recurrence N=3 → N=4
    stable).
    """
    start_anchor = "Runtime-prerequisite completeness on proposed fixes"
    end_anchor = "Fix-block-completeness discipline"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-013", "slice-014", "slice-015"]
    substantive = [
        "import",
        "_ALLOWED_STATUSES",
        "sibling",
        "end_anchor",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 3, (
        f"strict-three cross-slice anchor requirement — need ALL of {cross_slice}, "
        f"got {cs_count} present in 9th sub-clause body"
    )
    assert sub_count >= 3, (
        f"insufficient substantive-discipline anchors — need ≥3 of {substantive}, "
        f"got {sub_count} in 9th sub-clause body"
    )


def test_critique_dim_9_runtime_prerequisite_completeness_cites_substantive_discipline_anchors():
    """Symmetric anchor-citation pin for 9th sub-clause body (mirror of slice-011/013/015 tests).

    Defect class: symmetric to slice-011's `_cites_at_least_two_cross_slice_anchors` on
    the 6th sub-clause body + slice-013's same on the 7th sub-clause body + slice-015's
    same on the 8th sub-clause body. Per slice-013 DR-1 codification (meta-Critic-catching-
    pattern-blindness): every sub-clause body needs its own symmetric cross-slice +
    substantive-discipline anchor pin so future refinements don't drift unpinned.

    NOTE: this test's assertions overlap with `_paragraph_cites_slice_013_014_015` above
    — intentional duplicates per slice-013 EPGD-1 + slice-015 SCPD-1 convention. The
    DEFECT CLASS each catches differs: `_paragraph_cites` is the AC #4 acceptance test;
    this `_cites_substantive_discipline_anchors` is the symmetric-to-slice-011/013/015
    sibling matching the regression-guard pattern.

    Rule reference: META-2 + CCC-1 + RPCD-1 (slice-016 symmetric add per DR-1 N=4 stable
    post-slice-016 + Wiegers regression-guard coverage symmetry per /critique-review
    M-add-1). End_anchor tightened from `### Bonus: weak graph edges` →
    `Fix-block-completeness discipline` per slice-024 Phase 1e (generic
    methodology recurrence N=3 → N=4 stable).
    """
    start_anchor = "Runtime-prerequisite completeness on proposed fixes"
    end_anchor = "Fix-block-completeness discipline"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-013", "slice-014", "slice-015"]
    substantive = [
        "import",
        "_ALLOWED_STATUSES",
        "sibling",
        "end_anchor",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 3, (
        f"strict-three cross-slice anchor requirement — need ALL of {cross_slice}, "
        f"got {cs_count} present in 9th sub-clause body"
    )
    assert sub_count >= 3, (
        f"insufficient substantive-discipline anchors — need ≥3 of {substantive}, "
        f"got {sub_count} in 9th sub-clause body"
    )


# =============================================================================
# slice-024 FBCD-1 — Dim 9 10th sub-clause body-bound tests
# =============================================================================
# Per FBCD-1 codification (methodology-changelog.md v0.38.0 / ADR-022). The
# `_sub_clause_present` + `_location_pinned` duality ratchets N=4 → N=5 stable
# post-slice-024 (slice-011 RSAD-1 + slice-013 EPGD-1 + slice-015 SCPD-1 +
# slice-016 RPCD-1 + slice-024 FBCD-1). Two sub-modes (not three like RPCD-1)
# given FBCD-1's N=10-cumulative-cross-instance / N=4-distinct-slice base.


def test_critique_dim_9_fix_block_completeness_sub_clause_present():
    """The new 10th Dim 9 sub-clause must carry the canonical literal title.

    Defect class: a Dim 9 body that has the substring but not as a sub-clause
    title would silently pass without encoding the discipline structurally.
    Bare-substring pin per slice-015 SCPD-1 + slice-016 RPCD-1 `_sub_clause_present`
    precedent; the location-pin test (below) enforces position.

    Rule reference: META-2 + CCC-1 + FBCD-1 (slice-024 AC #1).
    """
    assert "Fix-block-completeness discipline" in CRITIQUE


def test_critique_dim_9_fix_block_completeness_location_pinned():
    """The new 10th sub-clause must fall between RPCD-1 (9th sub-clause) and the
    Bonus H3.

    Defect class: a future drift moving FBCD-1 out of Dim 9 (e.g., into Dim 8 or
    the `### Bonus` section) would silently pass substring-only pin tests; the
    location-pin guard catches it. Per slice-016 RPCD-1 `_location_pinned`
    scoped-find precedent; anchors verified unique pre-AC-lock; scoped .find()
    to avoid first-occurrence-wins collision.

    Location pin: sub-clause title MUST appear BETWEEN start anchor
    `Runtime-prerequisite completeness on proposed fixes` (the PREVIOUS sub-clause
    title — FBCD-1 follows RPCD-1) AND end anchor `Phantom test-file citation
    discipline` (the NEXT sub-clause title — PTFCD-1 follows FBCD-1). The
    end_anchor was tightened from `### Bonus: weak graph edges` to the PTFCD-1
    title at slice-025 per the slice-018 RPCD-1 sibling-scoping discipline so
    this FBCD-1 body window stays scoped to FBCD-1 only after PTFCD-1's
    insertion between FBCD-1 and the Bonus H3.

    Rule reference: META-2 + CCC-1 + FBCD-1 (slice-024 AC #1) + slice-025
    sibling-scoping tightening.
    """
    start_anchor = "Runtime-prerequisite completeness on proposed fixes"
    end_anchor = "Phantom test-file citation discipline"
    canonical = "Fix-block-completeness discipline"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )


def test_critique_dim_9_fix_block_completeness_names_both_sub_modes():
    """10th sub-clause body must name BOTH sub-modes (a) + (b).

    Defect class: a body that names only one sub-mode loses coverage of the
    temporal axis (sub-mode (a) original-draft cross-file consistency at
    first-Critic time + sub-mode (b) post-ACCEPTED-FIXED sibling-sweep at
    meta-Critic time). Symmetric pin for the new 10th sub-clause body (mirrors
    slice-011 RSAD-1 + slice-013 EPGD-1 + slice-015 SCPD-1 `_names_both_sub_modes`
    body shapes — two sub-modes given FBCD-1's N=10-cumulative-cross-instance
    evidence base, not three like RPCD-1).

    Canonical sub-mode anchors are case-sensitive substrings derived from the
    canonical body literal-substring set.

    Rule reference: META-2 + CCC-1 + FBCD-1 (slice-024 AC #1).
    """
    start_anchor = "Fix-block-completeness discipline"
    end_anchor = "Phantom test-file citation discipline"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER sub-clause start"
    body = CRITIQUE[start_idx:end_idx]
    assert "Original-draft cross-file consistency" in body, (
        "10th sub-clause body missing sub-mode (a) anchor "
        "'Original-draft cross-file consistency' — two-sub-mode pin broken"
    )
    assert "Post-ACCEPTED-FIXED sibling-sweep" in body, (
        "10th sub-clause body missing sub-mode (b) anchor "
        "'Post-ACCEPTED-FIXED sibling-sweep' — two-sub-mode pin broken"
    )


def test_critique_dim_9_fix_block_completeness_paragraph_cites_slice_020_021_022_023():
    """10th sub-clause body must cite ALL FOUR cross-slice anchors + ≥3
    substantive-discipline anchors.

    Defect class: descriptive sub-class text drifts unpinned to abstract
    framings without concrete traceability — readers lose the path back to the
    empirical evidence base. Pinned at N=4-distinct-slice evidence (slice-020
    M-add-1 + slice-021 M-add-1/2/3-rerun + slice-022 M-add-2/3 + slice-023
    M-add-1/2/3/4).

    Cross-slice anchors (strict-4-of-4): ["slice-020", "slice-021", "slice-022",
    "slice-023"] — all FOUR MUST be present (strict-four, not strict-three like
    slice-016 RPCD-1, reflecting FBCD-1's N=4-distinct-slice evidence base — one
    anchor per distinct slice).

    Substantive-discipline anchors (≥3-of-4): ["ACCEPTED-FIXED", "sibling",
    "mission-brief", "fix-block"] — hyphenated "fix-block" matches the dominant
    rendering `fix-block-completeness`. Pin at ≥3-of-4 to leave one degree of
    freedom for future refinement.

    Rule reference: META-2 + CCC-1 + FBCD-1 (slice-024 AC #1).
    """
    start_anchor = "Fix-block-completeness discipline"
    end_anchor = "Phantom test-file citation discipline"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-020", "slice-021", "slice-022", "slice-023"]
    substantive = [
        "ACCEPTED-FIXED",
        "sibling",
        "mission-brief",
        "fix-block",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 4, (
        f"strict-four cross-slice anchor requirement — need ALL of {cross_slice}, "
        f"got {cs_count} present in 10th sub-clause body"
    )
    assert sub_count >= 3, (
        f"insufficient substantive-discipline anchors — need ≥3 of {substantive}, "
        f"got {sub_count} in 10th sub-clause body"
    )


def test_critique_dim_9_fix_block_completeness_cites_substantive_discipline_anchors():
    """Symmetric anchor-citation pin for 10th sub-clause body (mirror of
    slice-011/013/015/016 tests).

    Defect class: symmetric to slice-011's `_cites_at_least_two_cross_slice_anchors`
    on the 6th sub-clause body + slice-013/015/016 same on 7th/8th/9th sub-clause
    bodies. Per slice-013 DR-1 codification (meta-Critic-catching-pattern-
    blindness): every sub-clause body needs its own symmetric cross-slice +
    substantive-discipline anchor pin so future refinements don't drift unpinned.

    NOTE: this test's assertions overlap with `_paragraph_cites_slice_020_021_022_023`
    above — intentional duplicates per slice-013 EPGD-1 + slice-015 SCPD-1 +
    slice-016 RPCD-1 convention. The DEFECT CLASS each catches differs:
    `_paragraph_cites` is the AC #1 acceptance test; this
    `_cites_substantive_discipline_anchors` is the symmetric-to-slice-011/013/015/016
    sibling matching the regression-guard pattern (Wiegers coverage-symmetry).

    Rule reference: META-2 + CCC-1 + FBCD-1 (slice-024 symmetric add per DR-1
    N=5 stable post-slice-024 + Wiegers regression-guard coverage symmetry).
    """
    start_anchor = "Fix-block-completeness discipline"
    end_anchor = "Phantom test-file citation discipline"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-020", "slice-021", "slice-022", "slice-023"]
    substantive = [
        "ACCEPTED-FIXED",
        "sibling",
        "mission-brief",
        "fix-block",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 4, (
        f"strict-four cross-slice anchor requirement — need ALL of {cross_slice}, "
        f"got {cs_count} present in 10th sub-clause body"
    )
    assert sub_count >= 3, (
        f"insufficient substantive-discipline anchors — need ≥3 of {substantive}, "
        f"got {sub_count} in 10th sub-clause body"
    )


def test_critique_dim_9_phantom_test_file_citation_sub_clause_present():
    """The new 11th Dim 9 sub-clause must carry the canonical literal title.

    Defect class: a Dim 9 body with the substring but not as a sub-clause
    title would silently pass without encoding the discipline structurally.
    Bare-substring pin per slice-016 RPCD-1 + slice-024 FBCD-1
    `_sub_clause_present` precedent; the location-pin test enforces position.

    Rule reference: META-2 + CCC-1 + PTFCD-1 (slice-025 AC #3).
    """
    assert "Phantom test-file citation discipline" in CRITIQUE


def test_critique_dim_9_phantom_test_file_citation_location_pinned():
    """The new 11th sub-clause must fall between FBCD-1 (10th sub-clause)
    and the Bonus H3.

    Defect class: a future drift moving PTFCD-1 out of Dim 9 (e.g., into the
    `### Bonus` section) would silently pass substring-only pins; the
    location-pin guard catches it. Per slice-016/024 `_location_pinned`
    scoped-find precedent.

    Location pin: sub-clause title MUST appear BETWEEN start anchor
    `Fix-block-completeness discipline` (the PREVIOUS sub-clause title —
    PTFCD-1 follows FBCD-1) AND end anchor `### Bonus: weak graph edges`.

    Rule reference: META-2 + CCC-1 + PTFCD-1 (slice-025 AC #3).
    """
    start_anchor = "Fix-block-completeness discipline"
    end_anchor = "### Bonus: weak graph edges"
    canonical = "Phantom test-file citation discipline"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"start anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER {start_anchor!r}"
    canonical_idx = CRITIQUE.find(canonical, start_idx, end_idx)
    assert canonical_idx != -1, (
        f"{canonical!r} not found between {start_anchor!r} and {end_anchor!r} "
        f"in agents/critique.md — sub-clause location drifted"
    )


def test_critique_dim_9_phantom_test_file_citation_names_both_sub_modes():
    """11th sub-clause body must name BOTH sub-modes (a) + (b).

    Defect class: a body naming only one sub-mode loses coverage of one
    citation surface (sub-mode (a) TF-1-plan-path existence at /build-slice
    Step 6 + sub-mode (b) shippability-Command-cell-path existence at
    /validate-slice Step 5.5). Two-sub-mode pin per slice-024 FBCD-1
    `_names_both_sub_modes` precedent.

    Rule reference: META-2 + CCC-1 + PTFCD-1 (slice-025 AC #3).
    """
    start_anchor = "Phantom test-file citation discipline"
    end_anchor = "### Bonus: weak graph edges"
    start_idx = CRITIQUE.find(start_anchor)
    assert start_idx != -1, f"sub-clause anchor {start_anchor!r} not found"
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    assert end_idx != -1, f"end anchor {end_anchor!r} not found AFTER sub-clause start"
    body = CRITIQUE[start_idx:end_idx]
    assert "TF-1-plan-path existence" in body, (
        "11th sub-clause body missing sub-mode (a) anchor "
        "'TF-1-plan-path existence' — two-sub-mode pin broken"
    )
    assert "shippability-Command-cell-path existence" in body, (
        "11th sub-clause body missing sub-mode (b) anchor "
        "'shippability-Command-cell-path existence' — two-sub-mode pin broken"
    )


def test_critique_dim_9_phantom_test_file_citation_paragraph_cites_slice_023_024():
    """11th sub-clause body must cite BOTH cross-slice anchors + ≥3
    substantive-discipline anchors.

    Defect class: descriptive sub-class text drifts unpinned to abstract
    framings without concrete traceability. Pinned at N=2-distinct-slice
    evidence (slice-023 B4 + slice-024).

    Cross-slice anchors (strict-2-of-2): ["slice-023", "slice-024"] — both
    MUST be present (one per distinct slice in PTFCD-1's N=2 evidence base).

    Substantive-discipline anchors (≥3-of-4): ["missing-test-path-file",
    "shippability", "test_first_audit", "RPCD-1"]. Pin at ≥3-of-4 to leave
    one degree of freedom for future refinement.

    Rule reference: META-2 + CCC-1 + PTFCD-1 (slice-025 AC #3).
    """
    start_anchor = "Phantom test-file citation discipline"
    end_anchor = "### Bonus: weak graph edges"
    start_idx = CRITIQUE.find(start_anchor)
    end_idx = CRITIQUE.find(end_anchor, start_idx)
    body = CRITIQUE[start_idx:end_idx]
    cross_slice = ["slice-023", "slice-024"]
    substantive = [
        "missing-test-path-file",
        "shippability",
        "test_first_audit",
        "RPCD-1",
    ]
    cs_count = sum(1 for anchor in cross_slice if anchor in body)
    sub_count = sum(1 for anchor in substantive if anchor in body)
    assert cs_count == 2, (
        f"strict-two cross-slice anchor requirement — need ALL of {cross_slice}, "
        f"got {cs_count} present in 11th sub-clause body"
    )
    assert sub_count >= 3, (
        f"insufficient substantive-discipline anchors — need ≥3 of {substantive}, "
        f"got {sub_count} in 11th sub-clause body"
    )


def test_critique_dim_9_cross_references_resolve():
    """Dim 9's 'see Dimension N sub-bullet' pointers must resolve to actual sub-bullet text.

    Defect class: dangling cross-references — Dim 9 says "see Dimension 4 sub-bullet"
    but the referenced sub-bullet doesn't exist in-file. This is the exact tooling-doc-
    vs-implementation parity defect class the slice exists to mitigate; if Dim 9 itself
    ships with this defect, the slice fails to deliver its own intent.
    Per /critique 2026-05-10 B2: each pointer paired with the actual referenced text.
    Rule reference: META-2 + CCC-1.
    """
    assert "see Dimension 4 sub-bullet" in CRITIQUE
    assert "Methodology-audit conformance" in CRITIQUE
    assert "see Dimension 1 sub-bullet" in CRITIQUE
    assert "Verify by reading the implementation" in CRITIQUE


def test_critique_dim_9_citation_is_deliberate():
    """Dim 9 must carry both Kiczales (vocabulary anchor) AND honest-out (evidence basis).

    Defect class: silent omission of citation choice would degrade Dim 9 to a
    floating-vocabulary dimension without retrieval traction. Both halves must hold:
    Kiczales gives the Critic a retrieval key for "cross-cutting concerns" terminology;
    honest-out preserves epistemic accuracy on evidence basis (mirrors Dim 8's pattern).
    Per /critique 2026-05-10 M3: precision-tightening of the Kiczales claim — the AOP
    body of work originating with Kiczales 1997 ECOOP, where "cross-cutting concerns"
    became a frozen term-of-art within ~2-3 years (NOT a single coined phrase in the
    1997 paper). A future drift that drops either half breaks the structural symmetry.
    Rule reference: META-2 + CCC-1.
    """
    assert "Kiczales" in CRITIQUE
    # Honest-out for evidence basis — accept either canonical phrasing
    assert ("no peer-level evidence-framework" in CRITIQUE
            or "no specific evidence-framework" in CRITIQUE), \
        "Dim 9 must carry an explicit honest-out for evidence basis (mirroring Dim 8 pattern)"


def test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables():
    """Dim 9 sub-clause 2 (Tooling-doc-vs-impl parity) must cover the design-doc-level
    surface — design.md mechanical tables vs methodology canonical inventories.

    Defect class: design.md mechanical tables (forward-sync targets, prerequisites,
    install-time renames, dependencies) drift from methodology canonical inventories
    in their corresponding implementation source. Promoted at N=2 per slice-007
    reflection (slice-006 DEVIATION-1+2 INST-1 inventory drift + slice-007 Critic B1
    install-time rename inversion); reinforced by slice-008 M1 (Wiegers AC-trace) +
    M2 (TWO-surface schema-pin generalization to N-surface). Per CCC-1 v1.1 /
    methodology-changelog.md v0.24.0 — extends the source-code-level cross-reference
    to Dim 1 surgical sub-bullet with the design-doc-level sibling.
    Rule reference: META-2 + CCC-1 v1.1.
    """
    assert "design.md mechanical tables" in CRITIQUE
    # Prefix match covers both `canonical inventory` (singular) + `canonical inventories` (plural)
    assert "canonical inventor" in CRITIQUE
    assert "install-time rename" in CRITIQUE


def test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph():
    """The design.md mechanical-tables paragraph must live INSIDE Dim 9 sub-clause 2
    (Tooling-doc-vs-implementation parity), NOT in a different sub-clause or dimension.

    Defect class: substring-only pin tests don't enforce location. A future drift
    moving the new paragraph to a different sub-clause body or dimension would
    silently pass test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables.
    Per Critic M1 at slice-009: anchor the canonical literal `design.md mechanical
    tables` between the sub-clause 2 title and the sub-clause 3 title to detect
    structural relocation.
    Rule reference: META-2 + CCC-1 v1.1 (slice-009 location-pin guard).
    """
    # Use Dim 9 sub-clause titles in their canonical "- **<Title>**" bullet form to avoid
    # collision with body-text occurrences of the same words elsewhere in the file
    # (e.g., "Algorithm-path-conformance" also appears in Dim 4 sub-bullet body — same
    # bullet syntax with `:` separator, vs Dim 9 sub-clause 3's ` — ` em-dash separator).
    # Anchor on Dim 9 sub-clause 3's unique cross-reference text.
    sub_clause_2_title_idx = CRITIQUE.find("- **Tooling-doc-vs-implementation parity**")
    sub_clause_3_title_idx = CRITIQUE.find(
        "Algorithm-path-conformance with pre-existing branches** — see Dimension 4 sub-bullet for full body"
    )
    canonical_phrase_idx = CRITIQUE.find("design.md mechanical tables")
    assert sub_clause_2_title_idx != -1, "sub-clause 2 bullet title missing"
    assert sub_clause_3_title_idx != -1, "sub-clause 3 bullet title missing"
    assert canonical_phrase_idx != -1, "design.md mechanical tables phrase missing"
    assert sub_clause_2_title_idx < canonical_phrase_idx < sub_clause_3_title_idx, (
        f"'design.md mechanical tables' (idx={canonical_phrase_idx}) must fall between "
        f"Dim 9 sub-clause 2 bullet title (idx={sub_clause_2_title_idx}) "
        f"and Dim 9 sub-clause 3 bullet title (idx={sub_clause_3_title_idx})"
    )


def test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007():
    """The design.md mechanical-tables paragraph must carry concrete cross-slice
    examples at N=2: slice-006 (DEVIATION-1 + DEVIATION-2) + slice-007 (B1 with
    ai-sdlc-VERSION install-time rename anchor).

    Defect class: bare claims without exemplars degrade Critic retrieval. The
    existing Dim 9 sub-clauses each carry slice-NNN example anchors (slice-001
    cwd-mismatch, slice-002 RR-1 docstring vs regex, slice-005 BC-GLOBAL-1 always-true).
    The design.md-tables sub-class promotion must follow the same example-carrying
    pattern. N=2 evidence: slice-006 INST-1 inventory drift + slice-007 install-time
    rename inversion.
    Rule reference: META-2 + CCC-1 v1.1.
    """
    assert "slice-006" in CRITIQUE
    assert "DEVIATION-1" in CRITIQUE
    assert "DEVIATION-2" in CRITIQUE
    assert "slice-007" in CRITIQUE
    assert "ai-sdlc-VERSION" in CRITIQUE


def test_critique_output_format_lists_nine_dimensions():
    """Output format `## Dimensions checked` example must list all 9 dimensions.

    Defect class: if the example block only shows 8 items, the Critic at runtime may
    produce a critique.md output with only 8 `- [x]` lines, and the user reading that
    output won't see Dim 9 was actually walked. The example is the canonical
    template the Critic copies; drift here corrupts every produced critique.
    Rule reference: META-2 + CCC-1.
    """
    # Find the ## Output format section
    assert "## Output format" in CRITIQUE
    assert "## Dimensions checked" in CRITIQUE
    # All 9 dimensions must appear in the output-format example
    assert "- [x] Unfounded assumptions" in CRITIQUE
    assert "- [x] Missing edge cases" in CRITIQUE
    assert "- [x] Over-engineering" in CRITIQUE
    assert "- [x] Under-engineering" in CRITIQUE
    assert "- [x] Contract gaps" in CRITIQUE
    assert "- [x] Security" in CRITIQUE
    assert "- [x] Drift from vault" in CRITIQUE
    assert "- [x] Web-known issues" in CRITIQUE
    assert "- [x] Cross-cutting conformance" in CRITIQUE


def test_no_in_repo_drift_on_eight_dimensions_phrase():
    """No in-repo file outside historical/vault content may say "8 dimensions" anymore.

    Defect class: tooling-doc-vs-implementation parity drift. After CCC-1 (slice-006),
    the Critic walks 9 dimensions; any file claiming "8 dimensions" is a doc-vs-impl
    contradiction that the dimension-1 surgical sub-bullet would correctly flag.
    Scope: agents/, skills/, plugin.yaml, tutorial-site/. Excludes:
    methodology-changelog.md (historical record — append-only by inclusion heuristic);
    architecture/ vault (slice artifacts, calibration log, ADRs — historical content);
    tests/ (this file's defensive grep would self-flag).
    Rule reference: META-2 + CCC-1 (parity-sweep).
    """
    from pathlib import Path
    REPO_ROOT = Path(__file__).resolve().parents[2]
    scan_dirs = [
        REPO_ROOT / "agents",
        REPO_ROOT / "skills",
        REPO_ROOT / "tutorial-site",
    ]
    scan_files = [REPO_ROOT / "plugin.yaml"]
    extensions = {".md", ".yaml", ".yml", ".html"}
    targets = list(scan_files)
    for d in scan_dirs:
        if d.exists():
            targets.extend(p for p in d.rglob("*") if p.is_file() and p.suffix in extensions)
    drift = []
    for path in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if "8 dimensions" in text:
            drift.append(str(path.relative_to(REPO_ROOT)))
    assert not drift, (
        f"Stale '8 dimensions' references found (CCC-1 expected 9 dimensions everywhere): "
        f"{drift}"
    )
