---
id: ADR-053
title: Extend the OSDG-1 guarded set to include the in-loop reflect skill; classify the member-addition as a methodology-surface behavior change taking the 4-part PMI-1 bump path, minting no new RULE-ID
date: 2026-05-19
slice: slice-051-extend-osdg-1-to-reflect-skill
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-053: Extend OSDG-1 to `reflect/SKILL.md`

## Context

OSDG-1 (slice-049; ADR-051) extended the mini-CAD / CAD-1 / EOL-DRIFT-1
drift-guard family to the two pipeline-opener skills `/triage` and
`/adopt`. As of slice-050 the guarded set is `agents/critique.md` (CAD-1)
plus the in-loop skills `slice` / `build_slice` / `commit_slice` /
`query_design` / `critique` / `diagnose` plus the openers `triage` /
`adopt` (OSDG-1) — but **not** `reflect`.

slice-050 added a `Step 5b-avfs` block to `skills/reflect/SKILL.md` (the
`/reflect` arm of the AVFS-1 `ai-sdlc-VERSION` forward-sync gate). That
made `reflect/SKILL.md` load-bearing: Claude reads the **installed** copy
at `/reflect` runtime, so a forward-sync miss would let the AVFS-1 gate's
`/reflect` arm silently skip on a stale install (the `/build-slice` arm
lives in OSDG-1-guarded `build-slice/SKILL.md`, so the gate is not fully
defeated — exposure is bounded but real). slice-050's meta-Critic (M-add-1)
caught this and the reflection recorded it as an N=1 latent exposure +
explicit strong next-slice candidate: extend OSDG-1's guarded set to
include `reflect/SKILL.md`, using the clean slice-049 member-addition
pattern. This slice closes it.

Two sub-decisions: (1) does adding a guarded member mint a new RULE-ID or
extend OSDG-1; (2) does the member-addition require the 4-part PMI-1 bump +
changelog entry + entry-pin, or only a slice-vault record.

## Options considered

1. **No changelog / no VERSION bump; slice-vault record only** — pros:
   minimal. Cons: this is exactly the rev-0 pre-decision the slice-049
   first Critic (B2) proved false on recompute. A new permanent pipeline
   HALT member is a behavior change under this project's published
   Inclusion heuristic ("acceptable yesterday, refused today ⇒ changelog
   entry"): a `reflect/SKILL.md` forward-sync miss was acceptable-yesterday
   (no gate caught it) and is refused-today (the new test FAILs the suite +
   HALTs PCA-1). slice-050 lesson line 60 codified this: a drift-guard
   family member-addition whose slice has no other bump reason **is** a
   methodology-surface behavior change. Rejected.
2. **Mint a new RULE-ID for the reflect member** — pros: superficially
   parallel to OSDG-1's own minting. Cons: OSDG-1 already names the
   in-repo↔installed content-equality invariant for guarded SKILL.md
   files; `reflect` is one more member of OSDG-1's set, not a new rule. A
   new ID would fragment a single coherent invariant across IDs. Rejected.
3. **Extend OSDG-1's guarded set to `reflect`; mint no new RULE-ID; take
   the 4-part PMI-1 bump + `## v0.59.0` changelog entry + content-bearing
   entry-pin + this ADR (extends ADR-051; supersedes nothing)** — pros:
   honest under the Inclusion heuristic; one invariant, one ID, an
   enumerated member set; reuses the slice-049 proven shape verbatim
   (test = structural twin reusing `assert_md_forward_synced`; zero new
   comparison logic). Cons: a ~6-surface inventory fan-out for a one-line
   conceptual change — accepted as the cost of the lineage's integrity.
   **Chosen.**

## Decision

Add `skills/reflect/SKILL.md` to the OSDG-1 guarded set via a new
structural-twin test `tests/methodology/test_reflect_skill_drift.py`
(reusing `tests/skill_drift_equality.py::assert_md_forward_synced`
verbatim, EOL-agnostic per EOL-DRIFT-1 / ADR-033). Classify the
member-addition as a methodology-surface behavior change: apply the 4-part
PMI-1 bump (in-repo `VERSION`, installed `~/.claude/ai-sdlc-VERSION`,
`plugin.yaml.version`, forward-synced `~/.claude/methodology-changelog.md`)
to `0.59.0`, add a `## v0.59.0` changelog entry describing the OSDG-1
member-addition, add a content-bearing in-repo-only entry-pin, update the
CLAUDE.md "Mini-CAD / OSDG-1" enumeration, and add a shippability
critical-path row for the new test. No new RULE-ID is minted — OSDG-1 is
extended, not superseded; this ADR extends the ADR-051 OSDG-1 lineage
(and through it the slice-007 CAD-1 / slice-010 mini-CAD / slice-033
EOL-DRIFT-1 lineage) with `supersedes: null`.

## Consequences

- Every methodology-suite run and every PCA-1 auto-advance now
  deterministically fails if `reflect/SKILL.md` drifts from its installed
  copy — the slice-050 M-add-1 N=1 exposure is retired by a gate, not by
  human discipline.
- Future drift-guard member-additions have a third confirming precedent
  (slice-049 triage/adopt → slice-051 reflect) for the
  "member-addition = methodology-surface behavior change ⇒ 4-part-bump
  path, no new RULE-ID" treatment.
- The guarded set now spans openers (`triage`/`adopt`) AND an in-loop
  skill (`reflect`); OSDG-1's "Opener-Skill" name is now a historical
  label, not a scope boundary — the changelog v0.59.0 entry records this
  so the name does not mislead future readers.
- Inventory fan-out, grouped (m1 critique fix — tightened for calibration
  traceability):
  - **PMI-1 version legs (4)**: in-repo `VERSION`, installed
    `~/.claude/ai-sdlc-VERSION`, `plugin.yaml.version`, forward-synced
    `~/.claude/methodology-changelog.md` (the changelog leg counts once;
    the in-repo `methodology-changelog.md` `## v0.59.0` entry is a content
    leg below).
  - **Content legs (3)**: the CLAUDE.md "Mini-CAD / OSDG-1" enumeration,
    the in-repo `methodology-changelog.md` `## v0.59.0` entry, the
    `test_methodology_changelog.py` content-bearing entry-pin; plus the
    shippability critical-path row (RPCD-1/SCPD-1). The new test file
    itself is the deliverable, not a fan-out surface.
  - **N/A (no `tools/*.py` added — verified)**: `plugin.yaml` tool-path
    leg, `install_audit._CANONICAL_TOOLS`, `test_utf8 _ROOT_ONLY_TOOLS`,
    and the INSTALL.md "N executable methodology tools" count (×2) are
    all untouched because this slice adds a `tests/` file, not a tool.

## Reversibility

**cheap**. Deleting the test file + reverting the CLAUDE.md line + the
changelog/entry-pin/shippability row + the VERSION fan-out is a
~30-minute mechanical revert with no downstream consumers (the test has
no importers; the invariant is self-contained). Tagged cheap and locked
now because the slice needs it and the cost of carrying the gate is near
zero while the cost of the unguarded exposure recurs every `/reflect`
invocation on a stale install.
