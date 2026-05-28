"""Prose-pin tests for PCR-1 enhanced conflict-STOP diagnostic at /commit-slice --merge.

Per slice-076 + ADR-069 (mints PCR-1): `skills/commit-slice/SKILL.md` Step 5b
sub-step 2.5 (the PSQ-3 conflict-outcome path; currently L183-186) gains a
strictly-additive paragraph BEFORE the existing SOAD-1 STOP block. The new
paragraph dispatches to `python -m tools.parallel_conflict_resolver
--resolve-soft --json` and branches on the resolver's exit code +
``action`` field:

  - exit 0 + ``action: APPLIED`` (SOFT class)  → log breadcrumb, proceed to
    sub-step 3 (existing no-ff merge path).
  - exit 0 + ``action: STOP`` (VAULT_CLAIM / HARD / MIXED / UNKNOWN) → print
    full-detail diagnostic (concerned slices + blast-radii + claim history +
    commit times + mission-brief links per U-file) AND fall through to the
    existing SOAD-1 3-option ask.

The diagnostic prose-pin mirrors the existing
``test_commit_slice_skill_rebase_flag.py`` precedent (structural-pin on
git-command invocation rather than minting a separate audit module — per
ADR-068 §Options-#3, the `python -m tools.parallel_conflict_resolver`
invocation IS the runtime gate).

The 4 literal anchors enforced by ``test_diagnostic_includes_blast_radius_*``
mirror mission-brief.md AC2 (per AC text at mission-brief.md L20:
"concerned slices, blast-radii, claim history, commit times, mission-brief
links").
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def _step_5b_section(content: str) -> str:
    """Extract the `#### Step 5b: With `--merge` ...` section.

    Section boundary: opening `#### Step 5b:` heading through (but not
    including) the next `#### Step 5c:` heading. PCR-1's invocation lives in
    this section (within sub-step 2.5); the diagnostic invariants are scoped
    here so a stray mention in Step 5c/5d cannot satisfy the assertions.

    Mirrors the canonical extractor in
    ``tests/methodology/test_commit_slice_skill_rebase_flag.py`` per
    slice-075 precedent of helper duplication across test modules (3-Critic
    code-Critic m4 deferred; voluntary-restraint N=16 cumulative).
    """
    start_marker = "#### Step 5b:"
    end_marker = "#### Step 5c:"
    start = content.find(start_marker)
    assert start != -1, (
        "skills/commit-slice/SKILL.md missing `#### Step 5b:` heading "
        "(BRANCH-1 sub-mode (b) `--merge` section); PCR-1 prose insertion "
        "site is sub-step 2.5 within this section"
    )
    end = content.find(end_marker, start)
    if end == -1:
        end = len(content)
    return content[start:end]


def test_step_5b_substep_2_5_emits_full_concerned_slice_diagnostic() -> None:
    """Step 5b sub-step 2.5 must dispatch to `python -m tools.parallel_conflict_resolver
    --resolve-soft --json` BEFORE the existing SOAD-1 STOP block.

    AC2 per mission-brief.md + design.md §"Edit to skills/commit-slice/SKILL.md":
    PCR-1 is strictly additive — the new paragraph inserts BEFORE PSQ-3's
    SOAD-1 ask, not replacing it. The runtime gate is the CLI invocation
    literal `python -m tools.parallel_conflict_resolver` AND `--resolve-soft`.

    The dispatch-then-SOAD-1 ordering is the load-bearing invariant: a
    dispatch AFTER SOAD-1 would prompt the user before the resolver had a
    chance to auto-resolve, defeating the value proposition.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "parallel_conflict_resolver" in section, (
        "skills/commit-slice/SKILL.md Step 5b must reference "
        "`parallel_conflict_resolver` (the PCR-1 helper module) per "
        "ADR-069 § Decision sub-step-2.5 contract"
    )
    assert "--resolve-soft" in section, (
        "Step 5b must reference the `--resolve-soft` CLI flag (the PCR-1 "
        "dispatch mode invoked from sub-step 2.5 conflict outcome path)"
    )
    # Ordering invariant: the PCR-1 dispatch must appear BEFORE the SOAD-1
    # block (which is what PSQ-3's existing STOP path falls through to).
    resolver_idx = section.find("parallel_conflict_resolver")
    soad_idx = section.find("SOAD-1")
    assert resolver_idx != -1, "Step 5b missing PCR-1 resolver dispatch (AC2)"
    assert soad_idx != -1, (
        "Step 5b missing SOAD-1 ask reference (existing PSQ-3 invariant — "
        "PCR-1 must NOT remove the SOAD-1 fallback)"
    )
    assert resolver_idx < soad_idx, (
        f"Step 5b ordering violation: PCR-1 resolver dispatch (offset "
        f"{resolver_idx}) must appear BEFORE the SOAD-1 fallback (offset "
        f"{soad_idx}); a dispatch-after-SOAD-1 would prompt the user "
        f"before resolution had a chance to run (ADR-069 § Decision contract)"
    )


def test_diagnostic_includes_blast_radius_claim_history_commit_time_mission_brief_link() -> None:
    """Step 5b sub-step 2.5 diagnostic must enumerate the 4 structured fields.

    AC2 per mission-brief.md L20: "the existing STOP block is enhanced to
    print a structured diagnostic for each U-prefixed file: (a) which active
    slices have that file in their declared blast-radius... (b) claim
    history... (c) last-commit time per concerned slice... (d) mission-brief.md
    link for each concerned slice".

    These 4 literal anchors MUST appear in the Step 5b section's PCR-1
    prose (the universal "what's actually conflicting" surface that fires
    for ALL non-SOFT classes — VAULT_CLAIM / HARD / MIXED / UNKNOWN).
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "blast-radius" in section or "blast-radii" in section, (
        "Step 5b sub-step 2.5 diagnostic must reference 'blast-radius' or "
        "'blast-radii' per mission-brief AC2 (a) — concerned slice blast-radius "
        "for each U-file"
    )
    assert "claim history" in section.lower(), (
        "Step 5b sub-step 2.5 diagnostic must reference 'claim history' per "
        "mission-brief AC2 (b) — PSQ-2 Claimed-by/Claimed-at on slice-queue.md"
    )
    assert "commit time" in section.lower() or "last-commit" in section.lower(), (
        "Step 5b sub-step 2.5 diagnostic must reference 'commit time' or "
        "'last-commit' per mission-brief AC2 (c) — per-concerned-slice "
        "last-commit ISO timestamp"
    )
    assert "mission-brief" in section, (
        "Step 5b sub-step 2.5 diagnostic must reference 'mission-brief' per "
        "mission-brief AC2 (d) — markdown-rendered relative path to each "
        "concerned slice's mission-brief.md"
    )
    assert "concerned slice" in section.lower(), (
        "Step 5b sub-step 2.5 diagnostic must use the 'concerned slice' "
        "phrasing per mission-brief AC2 + design.md §Edit-site canonical "
        "diagnostic vocabulary"
    )
