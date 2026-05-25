---
id: ADR-051
title: Extend the mini-CAD / EOL-DRIFT-1 drift-guard family to the pipeline-opener skills (triage, adopt) by minting OSDG-1, classified as a methodology-surface behavior change
date: 2026-05-19
slice: slice-049-add-triage-adopt-skill-drift-guards
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-051: Extend the drift-guard family to the opener skills (OSDG-1)

## Context

The mini-CAD / CAD-1 / EOL-DRIFT-1 drift-guard family asserts that each
in-repo canonical `.md` is forward-synced to the installed copy Claude
actually reads at runtime. As of slice-048 the family covered
`agents/critique.md` (CAD-1, slice-007) and the in-loop skills
`slice` / `build_slice` / `commit_slice` / `query_design` / `critique` /
`diagnose` — but **not** the two pipeline-opener skills `/triage`
(greenfield) and `/adopt` (brownfield), even though both have an in-repo
`skills/<name>/SKILL.md` and an installed `~/.claude/skills/<name>/SKILL.md`.

slice-048's reflection "Discovered" section recorded this as an N=1 latent
exposure: a forgotten forward-sync on either opener would be caught by
nothing but human discipline (slice-048 must-not-defer #3 was the only
control and it is human-dependent). slice-049 closes that gap.

The load-bearing decision is **not** "add two test files" (mechanical) — it
is whether adding two permanent pipeline HALT members constitutes a
*methodology-surface behavior change* requiring a changelog entry + RULE-ID
+ 4-part PMI-1 bump, or a mere coverage addition recorded only in the slice
vault. slice-049's rev-0 design pre-decided "no bump" on a precedent that
the Critic (B2) proved false on recompute: the cited "slice-035 added
build/commit drift tests with no independent bump" is wrong — those tests
were first added by **slice-021** and rode slice-021/**BRANCH-1**'s
*existing* v0.35.0 4-part PMI-1 bump (`methodology-changelog.md:474`;
`git log --diff-filter=A` → commit `8823c53` "slice-021 — BRANCH-1").
That is no precedent for a no-bump member-addition.

## Options considered

1. **No changelog / no VERSION bump; record only in the slice vault**
   (rev-0 pre-decision) — pros: minimal; cons: rests on a false precedent
   (Critic B2, verified); violates the changelog's own Inclusion heuristic
   ("acceptable yesterday, refused today ⇒ changelog entry"); leaves a
   permanent new pipeline HALT surface undocumented in the canonical
   changelog. Rejected.
2. **Mint OSDG-1; ship a `## v0.57.0` entry + 4-part PMI-1 bump +
   entry-pin + this ADR** — pros: honest under the project's published
   Inclusion criterion; the new HALT members are documented where every
   future slice looks; consistent with the slice-032 (QD-1) / slice-033
   (EOL-DRIFT-1) precedent that a drift-family *surface* change carries a
   changelog entry + RULE-ID + bump + ADR; cons: ~2 extra mechanical hours.
   **Chosen.**
3. **Supersede EOL-DRIFT-1 / fold triage+adopt into CAD-1's text** —
   rejected: this is an *extension* of the family, not a semantic change to
   any existing guard; superseding would misrepresent the lineage and force
   needless churn on the existing rule-IDs.

## Decision

slice-049 mints **OSDG-1 — Opener-Skill Drift Guard**: the in-repo
`skills/triage/SKILL.md` and `skills/adopt/SKILL.md` MUST be content-equal
modulo line endings (EOL-agnostic per [[ADR-033]] / EOL-DRIFT-1) to their
installed `~/.claude/skills/<name>/SKILL.md` copies, enforced by
`tests/methodology/test_triage_skill_drift.py` and
`tests/methodology/test_adopt_skill_drift.py` (each a structural twin of
the existing `test_slice_skill_drift.py`, reusing
`tests/skill_drift_equality.py::assert_md_forward_synced` verbatim — zero
new comparison logic).

This is classified a **methodology-surface behavior change** by the
`methodology-changelog.md` Inclusion heuristic and therefore ships with: a
`## v0.57.0` changelog entry carrying `Rule reference: OSDG-1`; a 4-part
PMI-1 atomic bump 0.56.0→0.57.0 (`VERSION` + `~/.claude/ai-sdlc-VERSION` +
`plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`);
`test_v_0_57_0_osdg_1_entry_present_in_repo` +
`test_v_0_57_0_osdg_1_shippability_consumer_propagation` pins; two
`architecture/shippability.md` rows; and a CLAUDE.md `## Self-hosting
discipline` Mini-CAD-bullet generalization. INST-1 is **unchanged** — no
new skill/agent/tool is added (only two `tests/` modules + this ADR).

OSDG-1 is a plain (non-`-D`, non-`-T`) RULE-ID — a pytest-regression-
enforced invariant like its siblings CAD-1 / MCT-1 / QD-1. It **extends**,
does not supersede, the CAD-1 (slice-007) / mini-CAD (slice-010) /
EOL-DRIFT-1 (slice-033, [[ADR-033]]) lineage; `supersedes: null`.

## Consequences

- Two new permanent members of the drift-guard family; the methodology
  suite + PCA-1 now HALT on a triage/adopt forward-sync miss (the
  slice-048-discovered exposure is closed).
- The `.gitattributes` glob `skills/**/SKILL.md` already pins both new
  surfaces `text eol=lf` (verified — no `.gitattributes` gap); the two new
  guards behave identically to the five existing ones.
- Future opener-skill edits MUST be forward-synced before slice finish or
  the suite fails — same discipline already in force for the in-loop skills.
- Sets the precedent that a drift-guard *family member-addition* whose slice
  has no other bump reason is itself a behavior change (resolving the
  ambiguity slice-049 rev-0 got wrong; future member-additions follow
  Option 2, not Option 1).

## Reversibility

**cheap.** Reverting is: delete the two test modules, the two shippability
rows, the `## v0.57.0` entry + entry-pin, this ADR, and roll the 4-part
version back to 0.56.0. No data migration, no contract consumer, no
runtime-code surface — purely additive methodology guardrail.
