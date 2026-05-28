"""ADR-069 presence + canonical-name pin for PCR-1 (slice-076).

Per **PCR-1** (`methodology-changelog.md` v0.73.0; ADR-069; slice-076; mints
a new rule on the parallel-conflict-resolution family axis sibling to PSQ-N).
This test guards that ADR-069 exists at its canonical location, parses with
the standard frontmatter shape (id / title / date / slice / reversibility /
status / supersedes), and carries the canonical title naming PCR-1 +
parallel-conflict-resolution as a fixed-string anchor.

Mirror of ADR-existence test convention used by methodology slices (PSQ-1
ADR-064, PSQ-2 ADR-067, PSQ-3 ADR-068, BRANCH-2 ADR-063) — content-bearing
prose-pin tests rather than registry-membership-only tests, so the ADR's
key claims are reproducible from the pinned literals alone.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT, read_file


_ADR_PATH = "architecture/decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen.md"


def test_adr_069_parallel_conflict_resolution_mechanism_exists():
    """ADR-069 must exist at its canonical filename + carry the canonical
    title + frontmatter declaring PCR-1 mints a new rule (supersedes: null).

    Pins the following invariants:
      (a) File exists at ``architecture/decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen.md``
      (b) Frontmatter ``id: ADR-069``
      (c) Title literal contains ``PCR-1`` + ``parallel-conflict-resolution``
      (d) Frontmatter ``supersedes: null`` (PCR-1 mints a new rule on a new
          family axis; supersedes nothing per slice-076 design.md L5)
      (e) Frontmatter ``reversibility: expensive`` (per design.md L130 — once
          parallel sessions rely on soft-regen path, reverting is costly)
      (f) Frontmatter ``slice: slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen``
      (g) Body references the 3-class taxonomy by name (SOFT / VAULT_CLAIM /
          HARD as the load-bearing classes; MIXED + UNKNOWN are fail-closed
          variants)
    """
    adr_path = REPO_ROOT / _ADR_PATH
    assert adr_path.exists(), (
        f"ADR-069 must exist at {_ADR_PATH} — PCR-1 mints a new ADR per "
        "design.md L5 and the 3-class taxonomy reference layer"
    )
    body = read_file(_ADR_PATH)
    assert "id: ADR-069" in body, (
        "ADR-069 frontmatter must contain 'id: ADR-069' per ADR schema"
    )
    assert "PCR-1" in body, (
        "ADR-069 must reference PCR-1 (the rule it mints) — title + body anchor"
    )
    assert "parallel-conflict-resolution" in body, (
        "ADR-069 must reference 'parallel-conflict-resolution' (the family "
        "axis canonical phrase)"
    )
    assert "supersedes: null" in body, (
        "ADR-069 frontmatter must declare 'supersedes: null' (PCR-1 mints a "
        "new rule on a new family axis; does NOT supersede an existing rule)"
    )
    assert "reversibility: expensive" in body, (
        "ADR-069 frontmatter must declare 'reversibility: expensive' per "
        "design.md L130 — soft-regen path becomes load-bearing audit trail "
        "at first append"
    )
    assert "slice: slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen" in body, (
        "ADR-069 frontmatter must declare its authoring slice as "
        "slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen"
    )
    assert "SOFT" in body, (
        "ADR-069 body must reference SOFT class (the auto-regen-shipped class)"
    )
    assert "VAULT_CLAIM" in body, (
        "ADR-069 body must reference VAULT_CLAIM class (deferred to PCR-2)"
    )
    assert "HARD" in body, (
        "ADR-069 body must reference HARD class (deferred to PCR-2 Critic stack)"
    )
