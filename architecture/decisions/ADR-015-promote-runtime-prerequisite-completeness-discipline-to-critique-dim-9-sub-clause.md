---
id: ADR-015
title: Promote runtime-prerequisite-completeness discipline (RPCD-1) to agents/critique.md Dim 9 9th sub-clause
date: 2026-05-13
slice: slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-015: Promote runtime-prerequisite-completeness discipline (RPCD-1) to agents/critique.md Dim 9 9th sub-clause

## Context

The /critic-calibrate 2026-05-13 (post-slice-015) run identified a **DR-1 dual-review pattern reaching N=3 distinct-slice promotion threshold** — first-Critic-MISS / meta-Critic-CATCH on the same structural defect class across three consecutive cross-cutting-tooling slices:

- **slice-013 M-add-1**: First Critic flagged body-bound widening defect on slice-011's `_names_both_sub_modes` test but did not grep for sibling tests sharing identical anchors. Meta-Critic caught `_cites_at_least_two_cross_slice_anchors` sharing same anchors → needed lockstep end_anchor tighten.
- **slice-014 M-add-1**: First Critic pinned bare-vs-conftest `REPO_ROOT` name-resolution semantics. Canonical regression-test body used `pytest` + `ast` symbols. Module did NOT import either. Meta-Critic caught missing-imports prerequisite → would have NameError'd all 3 rows at smoke gate.
- **slice-015 M-add-1**: First Critic introduced `WRITTEN-AS-EDIT` as a TF-1-row status string. First Critic did NOT check whether `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist contained the new status. Meta-Critic ran `--strict-pre-finish` empirically, surfaced 11 violations → /build-slice Phase 6 strict-pre-finish would have HARD-FAILED.

Each instance shows the same shape: **first Critic correctly identifies the design-semantic defect AND a structurally sound fix, but does NOT independently audit the runtime-prerequisite surface (tooling allowlists, module imports, sibling test files) the fix interacts with.** The DR-1 meta-Critic at /critique-review caught all three at layer 2.

The /critic-calibrate run accepted Proposal 1 (RPCD-1: Runtime-Prerequisite Completeness Discipline). The Critic prompt edit was applied live: `agents/critique.md` Dim 9 gained a 9th sub-clause titled `Runtime-prerequisite completeness on proposed fixes`, byte-equal across in-repo and installed copies per CAD-1 (sha256 verified `f34c967eaaa34413...` exit 0).

This ADR ratifies the rule via the methodology stack: methodology-changelog v0.31.0 entry + pin-tests + entry-pin + atomic version bump 0.30.0 → 0.31.0 + shippability catalog row 16. Mirrors slice-011 (RSAD-1 / ADR-010), slice-013 (EPGD-1 / ADR-012), and slice-015 (SCPD-1 / ADR-014) Dim 9 sub-clause codification template.

## Options considered

1. **Codify RPCD-1 as a 9th Dim 9 sub-clause via the canonical methodology-changelog+pin-tests+ADR template** (chosen).
   - Pros: matches the established codification pattern N=4 (CCC-1 v1.1 at slice-009 + RSAD-1 at slice-011 + EPGD-1 at slice-013 + SCPD-1 at slice-015); cross-references RSAD-1 / SCPD-1 for sub-clause-body discipline neighbors; supports three named sub-modes (a/b/c) operationalizing the rule; pin-tests prevent regression.
   - Cons: Dim 9 grows from 8 to 9 sub-clauses. Critic prompt now has 9 dimensions with the 9th dimension carrying 9 sub-clauses — total Dim 9 surface area meaningfully larger. Mitigated by sub-clauses being distinct concerns at recognizably different operational layers (methodology-audit / tooling-doc-vs-impl / algorithm-path-conformance / runtime-environment / language-version / recursive-self-application / entry-pin-vs-PMI-1-gate / shippability-catalog-propagation / runtime-prerequisite-completeness).

2. **Codify RPCD-1 as a sub-clause refinement of an existing sub-clause** (e.g., as a sub-bullet under SCPD-1's "Proactive-application mode" or under RSAD-1).
   - Pros: keeps Dim 9 sub-clause count at 8.
   - Cons: RPCD-1 operates at the fix-introduces-new-runtime-prerequisite-gap level, structurally distinct from RSAD-1 (own-draft defects in slice's own prose) and SCPD-1 (cross-Phase consumer propagation). Burying it as a sub-bullet would obscure the layer separation; sub-mode operationalization (a/b/c) doesn't fit cleanly under any existing sub-clause's intent.

3. **Defer codification — let DR-1 dual-review continue catching the pattern**.
   - Pros: zero prompt growth; DR-1 has empirically caught 3 of 3 N=3 evidence instances.
   - Cons: DR-1 catches at layer 2 (meta-Critic, after first Critic has filed its findings). Codifying at layer 1 shifts catch from /critique-review to /critique itself, reducing the meta-Critic dependency for the three named sub-modes. DR-1 remains as the safety net for the patterns that don't fit (a/b/c) — but reducing layer-2 dependency is empirically valuable: layer-1 catches catch faster, with less re-design rework. The Meta-Critic 2026-05-13 run explicitly rejected this option ("the strict ≥3-distinct-slice-MISS threshold is met by exactly one new pattern" — pattern qualifies for codification at layer 1).

4. **Codify with audit tooling (`tools/rpcd_1_audit.py`)** rather than prose-heuristic-only.
   - Pros: enforceable gate; programmatic catch at /build-slice.
   - Cons: the three sub-modes (a) NEW-symbol import audit / (b) NEW-status/token allowlist audit / (c) NEW-anchor sibling-grep audit each require context-specific implementation that varies by slice scope. Building a general-purpose audit at codification time risks under-engineering (too narrow to catch real cases) or over-engineering (broad enough to flag false positives that erode signal-to-noise). Defer audit-tooling to v2 if empirical evidence post-slice-016 shows prose-heuristic-only is insufficient. Convention: -D suffix on the rule-ID (RPCD-1) signals prose-heuristic discipline; mirrors RSAD-1 / EPGD-1 / SCPD-1 N=3 stable. Audit-tooling would justify a non-suffix rule-ID (mirrors TF-1 / BC-1 / PMI-1 / CAD-1 audit-enforced rules).

## Decision

Adopt **Option 1**. Codify RPCD-1 as `agents/critique.md` Dim 9 **9th sub-clause** `Runtime-prerequisite completeness on proposed fixes`. The Critic prompt edit was applied live during /critic-calibrate 2026-05-13 (post-slice-015) Step 4 apply; this slice ratifies via methodology stack — v0.31.0 entry + ADR-015 + pin-tests + entry-pin + atomic version bump 0.30.0 → 0.31.0 + shippability catalog row 16. Body names the three sub-modes (a) NEW-symbol import-audit / (b) NEW-status/token allowlist-audit / (c) NEW-anchor sibling-grep with N=3 cross-slice anchors (slice-013 M-add-1 + slice-014 M-add-1 + slice-015 M-add-1) and ≥3-of-4 substantive-discipline anchors `["import", "_ALLOWED_STATUSES", "sibling", "end_anchor"]`. -D suffix convention extends to N=4 instances stable (RSAD-1 + EPGD-1 + SCPD-1 + RPCD-1).

## Consequences

- **Critic-prompt expansion**: Dim 9 carries 9 sub-clauses post-slice-016. First-Critic discipline now includes runtime-prerequisite completeness check at /critique time for fix proposals (sub-modes a/b/c). DR-1 meta-Critic continues as safety net for sub-mode (d+) emergence.
- **Empirical baseline**: slice-016+ first-Critic MISSES on RPCD-1 sub-modes (a/b/c) target = 0 across slices 17-25 per /critic-calibrate effectiveness check methodology. If first-Critic-MISS ≥ 1 on any sub-mode, sub-mode wording needs refinement (per refinement-over-revert convention).
- **Cross-reference structural test load**: `test_critique_dim_9_cross_references_resolve` must continue to PASS at slice end. RPCD-1's body's references to RSAD-1 (sub-clause 6) and SCPD-1 (sub-clause 8) must resolve. Soft maintenance dependency: if future calibrations restructure Dim 9, RPCD-1's pointers need updating.
- **Methodology evolution path**: each Dim 9 sub-clause codification (5 instances now: CCC-1 v1.1, RSAD-1, EPGD-1, SCPD-1, RPCD-1) ratchets the codification template by demonstrating N=N stability counters. Slice-016 ratchets: -D suffix rule-ID convention N=3 → N=4 stable; N-surface schema-pin 3-surface shape N=4 → N=5 stable instances; PMI-1 v1.1 retirement-proof N=2 → N=3 stable; recursive-self-application N=7 → N=8 cumulative post-RSAD-1 codification; PMI-1 structural-invariant supersession N=3 → N=4 stable (evidence chain: slice-011 N=1 `_lists_five_sub_clauses` → `_lists_six_sub_clauses` + slice-013 N=2 `_lists_six` → `_lists_seven` + slice-015 N=3 `_lists_seven` → `_lists_eight` + slice-016 N=4 `_lists_eight` → `_lists_nine`). Per slice-016 /critique m1 ACCEPTED-FIXED.
- **DR-1 dual-review trajectory**: codification should reduce DR-1 catches on RPCD-1 sub-modes (a/b/c) over time as first-Critic internalizes. Empirical signal: if DR-1 catches on (a/b/c) reach 0 across slices 17-25, codification is empirically validated; if persistent ≥1 DR-1 catch per slice, sub-mode wording needs refinement.
- **No new external dependencies, no new tooling, no new audit gates**: -D suffix prose-heuristic-only per convention.

## Cost summary

- **Implementation cost**: ~30-45 min build + Critic + validate (~1 hour total) — mirrors slice-015 cycle time.
- **Revert cost (cheap with magnitude justification ~13-15 sites)**:
  - 1 methodology-changelog v0.31.0 entry (revert: delete entry)
  - 1 ADR-015 file (revert: delete file)
  - 1 entry-pin SECTION + 3 functions in `test_methodology_changelog.py` (revert: delete SECTION)
  - 1 PMI-1 structural-invariant supersession in `test_critique_agent.py` (revert: rename `_lists_nine_sub_clauses` → `_lists_eight_sub_clauses` + canonical-literal list 9 → 8)
  - 5 NEW body-bound tests in `test_critique_agent.py` (revert: delete functions)
  - 3 end_anchor tighten Edits (revert: change anchor back to `### Bonus: weak graph edges`)
  - 1 atomic version bump (revert: 0.31.0 → 0.30.0 in 3 files)
  - 1 forward-sync to installed (revert: re-sync prior in-repo state)
  - 4 shippability.md row propagations + 1 new row 16 (revert: rename back + delete row 16)
  - 1 agents/critique.md Dim 9 9th sub-clause body removal (revert: delete sub-clause body in in-repo + forward-sync)
  Total ~14 sites; same magnitude class as ADR-010 (~12 sites) / ADR-012 (~12 sites) / ADR-014 (~13-15 sites).
- **Irreversibles**: archived /critique outputs from slice-016+ that file findings under Dim 9's 9th sub-clause are filed permanently; in-context conditioning of the 9-dim-with-9-sub-clause Critic on its runs across slice-017+ accumulates monotonically. Same irreversible class as ADR-005 (9-dim Critic) / ADR-008 (CCC-1 v1.1) / ADR-010 (RSAD-1) / ADR-012 (EPGD-1) / ADR-014 (SCPD-1). Net-zero impossible after ~3-5 post-codification slices; **refinement-over-revert is the canonical recovery path**.

## Reversibility

**Cheap** with magnitude-of-revert justification ~13-15 sites (same class as ADR-010 / ADR-012 / ADR-014). All revert operations are mechanical (delete files / rename functions / change anchors back); zero load-bearing dependencies on RPCD-1's existence in slice-017+ code or vault files BEFORE slice-017 ships (post-slice-017 ships will have accumulated conditioning per Consequences section). The cheap-with-magnitude tag tracks reverting BEFORE slice-017 ships; post-slice-017, refinement-over-revert is the canonical recovery path per Cost summary irreversibles.
