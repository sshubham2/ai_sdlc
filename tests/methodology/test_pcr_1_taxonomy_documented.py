"""PCR-1 3-class taxonomy documentation pin (slice-076).

Per **PCR-1** (`methodology-changelog.md` v0.73.0; ADR-069 § Decision § 5-class
taxonomy table; slice-076). The 3 load-bearing classes (SOFT / VAULT_CLAIM /
HARD) MUST be documented as table rows in ADR-069 with their distinguishing
properties: shipped-in slice (SOFT=076, VAULT_CLAIM=077, HARD=077),
resolution path summary, and Critic involvement level.

This is the user-visible taxonomy contract — distinct from the
machine-actionable enum pin in
`tests/skills/parallel_conflict_resolver/test_soft_file_set.py`
(which guards the runtime SOFT file-set frozenset).

The MIXED + UNKNOWN classes are fail-closed variants and not separately
pinned here per design.md L155 — they're tested via behavior
(`test_classify_conflict_returns_unknown_when_rebase_state_empty` +
`test_classify_conflict_returns_mixed_when_soft_and_hard_coexist`).
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


_ADR_PATH = "architecture/decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen.md"


def test_three_class_taxonomy_lists_soft_vault_claim_hard():
    """ADR-069 § Decision must document the 3-class taxonomy with each
    class name + its shipped-in slice + Critic involvement.

    Pinned literals (per design.md L131-137 + ADR-069 § Decision § 5-class
    taxonomy table at L51-59):
      - ``SOFT`` (the auto-regen-shipped class — slice-076)
      - ``VAULT_CLAIM`` (deferred to PCR-2 / slice-077; timestamp-winner +
        light Critic resolution)
      - ``HARD`` (deferred to PCR-2 / slice-077; full Critic stack +
        TRI-RESOLVE-1)
      - ``slice-076`` (the SOFT-shipping slice)
      - ``slice-077`` OR ``PCR-2`` (the deferral target for VAULT_CLAIM + HARD)
      - ``Critic`` (involvement-level column anchor)

    The literals appear in ADR-069's Decision section taxonomy table; this
    test ensures the table is not silently degraded by a future edit.
    """
    body = read_file(_ADR_PATH)
    assert "SOFT" in body, (
        "ADR-069 must document the SOFT class (the auto-regen-shipped class "
        "in slice-076) per design.md L131"
    )
    assert "VAULT_CLAIM" in body, (
        "ADR-069 must document the VAULT_CLAIM class (deferred to PCR-2 / "
        "slice-077 for timestamp-winner resolution) per design.md L131"
    )
    assert "HARD" in body, (
        "ADR-069 must document the HARD class (deferred to PCR-2 / "
        "slice-077 for full Critic stack) per design.md L131"
    )
    assert "slice-076" in body, (
        "ADR-069 taxonomy must reference slice-076 as the SOFT-shipping slice"
    )
    assert ("slice-077" in body) or ("PCR-2" in body), (
        "ADR-069 taxonomy must reference slice-077 OR PCR-2 as the deferral "
        "target for VAULT_CLAIM + HARD"
    )
    assert "Critic" in body, (
        "ADR-069 taxonomy must reference 'Critic' (Critic involvement is the "
        "load-bearing column distinguishing SOFT from VAULT_CLAIM from HARD)"
    )
