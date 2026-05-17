"""QD-1 prose-contract structural pin for `skills/query-design/SKILL.md`.

Per slice-032 / ADR-032 + /critique B3: `/query-design` is an LLM-prose
skill — the SKILL.md prose IS the executed artifact (Claude reads the
installed markdown at runtime and acts on it). There is no separate
behavioral implementation that could drift from the prose, so the
strongest deterministic guarantee available is (a) the in-repo<->installed
byte-equality drift test (test_query_design_skill_drift.py) PLUS (b) this
prose-pin asserting the load-bearing contract clauses are present. A
"dry-run a conversational skill" AC has no deterministic pass/fail
predicate (slice-022 self-violation) — this pin is its deterministic
replacement.

Per /critique-review-v2 M-add-v2-1: this test also pins the QD-1 canonical
phrase in the SKILL.md (site (ii) of the 2-site canonical-phrase pin;
site (i) is the changelog body, pinned by
test_v_0_46_0_qd_1_entry_present_in_repo_and_installed). The literal below
MUST stay byte-identical to `_QD1_PHRASE` in test_methodology_changelog.py
— a reword in either fails a gate, closing the silent-prose-drift surface
the M1-v2 fix would otherwise have introduced.

Rule reference: QD-1 (slice-032; ADR-032); /critique B3; /critique-review
-v2 M-add-v2-1.
"""
from tests.methodology.conftest import REPO_ROOT

# MUST stay byte-identical to `_QD1_PHRASE` in
# tests/methodology/test_methodology_changelog.py (M-add-v2-1, 2-site pin).
_QD1_PHRASE = "read-only, delegation-only codebase Q&A"

_SKILL = REPO_ROOT / "skills" / "query-design" / "SKILL.md"


def _read() -> str:
    assert _SKILL.exists(), f"in-repo SKILL.md missing: {_SKILL}"
    return _SKILL.read_text(encoding="utf-8")


def test_grounding_contract_present():
    """SKILL.md MUST pin the grounding contract: read repo evidence before
    answering, cite specific files/symbols, never ungrounded recall.

    Defect class: an answer from training-data recall with no repo evidence
    is silent inaccuracy — the exact failure /query-design exists to prevent.
    """
    body = _read()
    assert "## The grounding contract" in body, (
        "SKILL.md missing the '## The grounding contract' section"
    )
    assert "never ungrounded recall" in body, (
        "SKILL.md grounding contract missing the 'never ungrounded recall' "
        "prohibition"
    )
    assert "Cite specific evidence" in body, (
        "SKILL.md grounding contract missing the cite-specific-evidence "
        "requirement (path:line / symbol / ADR / rule-ID)"
    )


def test_readonly_invariant_present_and_unconditional():
    """SKILL.md MUST state the read-only invariant unambiguously with no
    'may edit if...' loophole — the load-bearing safety property (ADR-032).
    """
    body = _read()
    assert "The read-only invariant" in body, (
        "SKILL.md missing the read-only invariant section"
    )
    assert "MUST NOT" in body and "Write, Edit, or NotebookEdit" in body, (
        "SKILL.md read-only invariant must explicitly forbid "
        "Write/Edit/NotebookEdit"
    )
    assert "no exception, escape hatch, or" in body, (
        "SKILL.md read-only invariant must state there is NO exception / "
        "escape hatch / 'may edit if' loophole (must-not-defer)"
    )


def test_delegation_contract_offer_not_author():
    """SKILL.md MUST pin the delegation contract: OFFER /slice, declinable,
    never author files, never auto-invoke.
    """
    body = _read()
    assert "## Handoff (delegation-only" in body, (
        "SKILL.md missing the '## Handoff (delegation-only...' section"
    )
    assert "never authors" in body, (
        "SKILL.md handoff section must state it never authors a "
        "slice/candidate/backlog file"
    )
    assert "never auto-invoke" in body, (
        "SKILL.md handoff section must state it never auto-invokes /slice"
    )


def test_three_error_model_clauses_present():
    """SKILL.md MUST address the 3 error-model clauses: stale/missing graph,
    unanswerable-from-evidence, declined-handoff -> zero side effect.
    """
    body = _read()
    assert "graphify graph stale or missing" in body, (
        "SKILL.md error model missing clause 1 (stale/missing graph -> "
        "instruct rebuild, do not answer ungrounded)"
    )
    assert "Question unanswerable from repo evidence" in body, (
        "SKILL.md error model missing clause 2 (unanswerable -> say so, no "
        "speculation)"
    )
    assert "Handoff declined" in body and "zero side effects" in body, (
        "SKILL.md error model missing clause 3 (declined handoff -> "
        "terminate with zero side effects)"
    )


def test_qd1_canonical_phrase_pinned_in_skill_md():
    """SKILL.md MUST contain the QD-1 canonical phrase verbatim — site (ii)
    of the 2-site canonical-phrase pin (/critique-review-v2 M-add-v2-1).

    Defect class: the M1-v2 fix obligated `_QD1_PHRASE` in both the
    changelog AND SKILL.md but originally pinned only the changelog. An
    unpinned SKILL.md occurrence recreates the silent-prose-drift class this
    slice exists to prevent (N=2 recurrence of v1 M-add-1). Pinning here
    makes QD-1's guard strictly stronger than the bci_1/scmd_1 precedent
    (anti-silent-weakening applied to the runtime artifact, not just the
    changelog).
    """
    body = _read()
    assert _QD1_PHRASE in body, (
        f"SKILL.md missing the QD-1 canonical phrase {_QD1_PHRASE!r} "
        f"verbatim — site (ii) of the 2-site pin. A reword here (or in "
        f"_QD1_PHRASE in test_methodology_changelog.py) silently erodes the "
        f"QD-1 read-only invariant."
    )


def test_no_pipeline_position_block():
    """SKILL.md MUST NOT carry a `## Pipeline position` block — /query-design
    is out-of-loop (ADR-032; /critique M3). Adding one is harmless to PCA-1
    but misrepresents the out-of-loop class and misleads future readers.
    """
    body = _read()
    # A `## Pipeline position` *section heading* is a line whose stripped
    # content starts with the heading marker. Descriptive prose that mentions
    # the phrase inline (e.g. backtick-wrapped "no `## Pipeline position`
    # block") is NOT a section and is permitted — mirrors how
    # tools/pipeline_chain_audit.py:_extract_section detects the heading.
    heading_lines = [
        ln for ln in body.splitlines()
        if ln.strip().startswith("## Pipeline position")
    ]
    assert not heading_lines, (
        "skills/query-design/SKILL.md MUST NOT have a '## Pipeline position' "
        f"section heading — it is out-of-loop (ADR-032), not a "
        f"_CANONICAL_CHAIN member. Found heading line(s): {heading_lines!r}"
    )
