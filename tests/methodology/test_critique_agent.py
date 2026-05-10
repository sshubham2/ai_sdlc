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


def test_critique_dim_9_lists_five_sub_clauses():
    """Dim 9 (Cross-cutting conformance) must enumerate all 5 sub-clause titles.

    Defect class: a Dim 9 body that drops sub-clauses loses the unified-pattern surface
    (e.g., dropping runtime-environment leaves slice-001-class misses without a home).
    The 5 sub-clauses are: 3 cross-references to Dim 1/4 surgical sub-bullets +
    2 N=1 standalone sub-clauses (runtime-environment, language-version).
    Rule reference: META-2 + CCC-1.
    """
    assert "Methodology-audit conformance" in CRITIQUE
    assert "Tooling-doc-vs-implementation parity" in CRITIQUE
    assert "Algorithm-path-conformance" in CRITIQUE
    assert "Runtime-environment" in CRITIQUE
    assert "Language-version conformance" in CRITIQUE


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
