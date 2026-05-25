---
id: ADR-022
title: Promote fix-block-completeness discipline (FBCD-1) to agents/critique.md Dim 9 10th sub-clause
date: 2026-05-15
slice: slice-024-refine-dim-9-with-fix-block-completeness-sub-clause
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-022: Promote fix-block-completeness discipline (FBCD-1) to agents/critique.md Dim 9 10th sub-clause

## Context

Across slices 020-023 a recurring meta-Critic catch-class has dominated `/critique-review` output: **fix-block-completeness on Builder's own ACCEPTED-FIXED sweeps**. The pattern: first-Critic correctly identifies a defect AND proposes a structurally sound fix; Builder applies the fix at one site at /critique-disposition time; sibling sites in OTHER files (mission-brief.md vs design.md vs ADR vs milestone.md vs critique.md fix prose) carrying the SAME claim/path/count/literal are NOT updated. Meta-Critic catches at /critique-review by grepping the anchor substring across all slice-authoring files.

**Cross-slice cumulative evidence (N=10 instances across N=4 distinct slices)** — pre-codification:

- **slice-020 M-add-1** (N=1): "Same class as B3 recurring in fix block" — Builder's B3 ACCEPTED-FIXED at one site missed sibling occurrences in mission-brief.
- **slice-021 M-add-1-rerun, M-add-2-rerun, M-add-3-rerun** (N=3 within-slice): "B3-new fix did NOT propagate to milestone.md L43"; "M1-residual item-11 retirement did NOT propagate to milestone.md L46"; "N-ratchet landed in ADR-019 L158 but NOT in design.md L197/L209/L211". (Cross-Critic-stack scopes its grep verification to mission-brief + design + ADR but consistently misses milestone.md — slice-021 aggregated-lessons.)
- **slice-022 M-add-2, M-add-3** (N=2 within-slice): "fix-block-completeness gap — m2 fix-block-completeness gap second sibling site un-propagated"; "fix-block-completeness on m3 — Count-drift between 22+ changed files (design.md L198) and 19 enumerated touches (design.md L202 + L226)".
- **slice-023 M-add-1, M-add-2, M-add-3, M-add-4** (N=4 within-slice): four distinct fix-block-completeness gaps on Builder's own ACCEPTED-FIXED sweeps for B1/B5/M5/M-add-3 spanning mission-brief + design.md + ADR-021.

Per the slice-023 reflection (`architecture/slices/archive/slice-023-audit-tools-default-utf8-stdout/reflection.md`) Pattern 3 + Pattern 4 explicit promotion-eligibility tag: **`PROMOTION-ELIGIBLE for /critic-calibrate slice-024 Dim 9 sub-clause`**.

This rule does NOT have a prior dedicated /critic-calibrate run authorizing its codification — slice-024 is the **first codification slice that applies the project's N=2-cross-slice proactive codification convention WITHOUT a dedicated calibration run** (per EPGD-1 / SCPD-1 precedent — both were codified at N=2 cross-slice without dedicated /critic-calibrate Proposal entries). The empirical basis is the cumulative N=10 evidence above (well past N=2 threshold) + the slice-023 reflection's explicit promotion-eligibility tag.

Per /critique-review (DR-1) trajectory: meta-Critic has empirically caught all N=10 instances at layer 2 (post-first-Critic). Codifying FBCD-1 at layer 1 (first-Critic via `agents/critique.md` Dim 9 10th sub-clause) shifts the catch earlier — reducing the DR-1 dependency for this specific class while preserving DR-1 as the safety net for sub-mode (c+) emergence.

This ADR ratifies the rule via the methodology stack: methodology-changelog v0.38.0 entry + pin-tests + entry-pin + atomic version bump 0.37.0 → 0.38.0 + shippability catalog row 24. Mirrors slice-011 (RSAD-1 / ADR-010), slice-013 (EPGD-1 / ADR-012), slice-015 (SCPD-1 / ADR-014), and slice-016 (RPCD-1 / ADR-015) Dim 9 sub-clause codification template.

## Options considered

1. **Codify FBCD-1 as a 10th Dim 9 sub-clause via the canonical methodology-changelog+pin-tests+ADR template** (chosen).
   - Pros: matches the established codification pattern N=5 (CCC-1 v1.1 at slice-009 + RSAD-1 at slice-011 + EPGD-1 at slice-013 + SCPD-1 at slice-015 + RPCD-1 at slice-016); cross-references CCC-1 v1.1 (Dim 9 sub-clause 2 — EXTERNAL-inventory sibling) and RPCD-1 (Dim 9 sub-clause 9 — structural-runtime sibling) for sub-clause-body discipline neighbors; supports two named sub-modes (a Original-draft cross-file consistency + b Post-ACCEPTED-FIXED sibling-sweep); pin-tests prevent regression.
   - Cons: Dim 9 grows from 9 to 10 sub-clauses. Critic prompt now has 9 dimensions with the 9th dimension carrying 10 sub-clauses — total Dim 9 surface area larger. Mitigated by sub-clauses being distinct concerns at recognizably different operational layers; FBCD-1 specifically operates at the cross-file-consistency layer distinct from CCC-1 v1.1's external-inventory layer (CCC-1 v1.1 catches design.md tables against EXTERNAL canonical inventories like `_CANONICAL_SKILLS`; FBCD-1 catches WITHIN-slice consistency across mission-brief / design / ADR / milestone — temporally + scope-wise distinct).

2. **Codify FBCD-1 as a sub-clause refinement of an existing sub-clause** (e.g., as a sub-bullet under CCC-1 v1.1's design.md-tables sub-clause).
   - Pros: keeps Dim 9 sub-clause count at 9.
   - Cons: CCC-1 v1.1 operates at design.md-tables-vs-EXTERNAL-canonical-inventory level (positive-inclusion / negative-exclusion / install-time-rename surfaces — `tools/install_audit.py` `_CANONICAL_*` tuples; `INSTALL.md` Step 3f; `methodology-changelog.md`; `plugin.yaml`; in-repo vs installed renamed name). FBCD-1 operates at WITHIN-slice cross-file consistency level (mission-brief.md vs design.md vs ADR-NNN vs milestone.md vs critique.md fix prose). Burying FBCD-1 as a sub-bullet under CCC-1 v1.1 would conflate two distinct discipline scopes; sub-mode operationalization ((a) at first-Critic + (b) at meta-Critic) doesn't fit cleanly under CCC-1 v1.1's intent.

3. **Defer codification — let DR-1 dual-review continue catching the pattern**.
   - Pros: zero prompt growth; DR-1 has empirically caught all N=10 evidence instances.
   - Cons: DR-1 catches at layer 2 (meta-Critic, after first Critic has filed its findings). Codifying at layer 1 shifts catch from /critique-review to /critique itself, reducing the meta-Critic dependency for the two named sub-modes. DR-1 remains as the safety net for the patterns that don't fit (a/b). The cumulative N=10 cross-slice evidence well exceeds the project's N=2-cross-slice proactive codification convention (EPGD-1 / SCPD-1 precedent) — proactive codification is empirically justified. Layer-1 catches are faster, with less re-design rework.

4. **Codify with audit tooling (`tools/fbcd_1_audit.py`)** rather than prose-heuristic-only.
   - Pros: enforceable gate; programmatic catch at /build-slice.
   - Cons: the two sub-modes (a) Original-draft cross-file consistency / (b) Post-ACCEPTED-FIXED sibling-sweep each require context-specific implementation that varies by slice scope (every claim's anchor substring is unique per slice; every fix block's scope is unique per /critique disposition). Building a general-purpose audit at codification time risks under-engineering (too narrow to catch real cases) or over-engineering (broad enough to flag false positives that erode signal-to-noise). Defer audit-tooling to v2 if empirical evidence post-slice-024 shows prose-heuristic-only is insufficient. Convention: -D suffix on the rule-ID (FBCD-1) signals prose-heuristic discipline; mirrors RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 / TPHD-1 / LAYER-EVID-1 N=6 stable. Audit-tooling would justify a non-suffix rule-ID (mirrors TF-1 / BC-1 / PMI-1 / CAD-1 / BFRD-1 / BRANCH-1 / UTF8-STDOUT-1 audit-enforced rules).

5. **Codify Pattern 4 (cross-mission-brief-vs-design-consistency-checking) as a SEPARATE 11th Dim 9 sub-clause**.
   - Pros: explicit pin on first-Critic surface separately from meta-Critic surface.
   - Cons: Pattern 4 IS the temporally-earlier surface of Pattern 3 — same shape at different review stages. Two separate sub-clauses for the same discipline would duplicate cross-references and inflate Dim 9 surface area without adding distinct coverage. Folding Pattern 4 into FBCD-1 sub-mode (a) is the cleaner codification — matches RPCD-1's 3-sub-mode shape (sub-modes (a)/(b)/(c) all under one rule ID) and SCPD-1's 2-sub-mode shape ((a) Reactive-catch + (b) Proactive-application).

## Decision

Adopt **Option 1**. Codify FBCD-1 as `agents/critique.md` Dim 9 **10th sub-clause** `Fix-block-completeness discipline`. Phase 1g of /build-slice inserts the sub-clause body in-repo; Phase 4 forward-syncs to installed; this slice ratifies via methodology stack — v0.38.0 entry + ADR-022 + pin-tests + entry-pin + atomic version bump 0.37.0 → 0.38.0 + shippability catalog row 24. Body names the two sub-modes (a) Original-draft cross-file consistency + (b) Post-ACCEPTED-FIXED sibling-sweep with N=4 cross-slice anchors (slice-020 M-add-1 + slice-021 M-add-1-rerun/2-rerun/3-rerun + slice-022 M-add-2/3 + slice-023 M-add-1/2/3/4) and ≥3-of-4 substantive-discipline anchors `["ACCEPTED-FIXED", "sibling", "mission-brief", "fix-block"]` (hyphenated form matches the dominant `fix-block-completeness` rendering).

**-D suffix convention** extends to **N=7 instances stable** (RSAD-1 + EPGD-1 + SCPD-1 + RPCD-1 + TPHD-1 + LAYER-EVID-1 + FBCD-1 — note BFRD-1 and BRANCH-1 also use -D-like suffixes for non-prose-heuristic disciplines; the strict -D-suffix-for-prose-heuristic-only convention covers FBCD-1).

## Consequences

- **Critic-prompt expansion**: Dim 9 carries 10 sub-clauses post-slice-024. First-Critic discipline now includes fix-block-completeness check at /critique time for cross-file consistency (sub-mode a) + post-fix sibling-sweep awareness (sub-mode b). DR-1 meta-Critic continues as safety net for sub-mode (c+) emergence.
- **Empirical baseline**: slice-025+ first-Critic MISSES on FBCD-1 sub-modes (a/b) target = 0 across slices 25-35 per /critic-calibrate effectiveness check methodology. If first-Critic-MISS ≥ 1 on any sub-mode, sub-mode wording needs refinement (per refinement-over-revert convention).
- **Cross-reference structural test load**: `test_critique_dim_9_cross_references_resolve` must continue to PASS at slice end. FBCD-1's body's references — cited by **canonical title strings** (not ordinal position) — to the `Tooling-doc-vs-implementation parity` sub-clause's design.md-mechanical-tables-vs-canonical-inventory body (i.e., CCC-1 v1.1) and to the `Runtime-prerequisite completeness on proposed fixes` sub-clause (i.e., RPCD-1) must resolve. Soft maintenance dependency: if future calibrations rename either sub-clause title, FBCD-1's pointers need updating in lockstep — but ordinal renumbering (sub-clause N → N+1) does NOT break the canonical-title-string encoding.
- **Methodology evolution path**: each Dim 9 sub-clause codification (6 instances now: CCC-1 v1.1, RSAD-1, EPGD-1, SCPD-1, RPCD-1, FBCD-1) ratchets the codification template by demonstrating N=N stability counters. Slice-024 ratchets: -D suffix rule-ID convention N=6 → N=7 stable; N-surface schema-pin 3-surface shape N=10 → N=11 stable instances; PMI-1 v1.1 retirement-proof N=9 → N=10 stable; recursive-self-application HWM ratchets per /build-slice empirical observation (slice-021 HWM N=33; slice-024 expected ≥ N=10 within-slice on codification slice); PMI-1 structural-invariant supersession N=4 → **N=5 cumulative** (evidence chain: slice-011 N=1 `_lists_five_sub_clauses` → `_lists_six_sub_clauses` + slice-013 N=2 `_lists_six` → `_lists_seven` + slice-015 N=3 `_lists_seven` → `_lists_eight` + slice-016 N=4 `_lists_eight` → `_lists_nine` + slice-024 N=5 `_lists_nine` → `_lists_ten`).
- **DR-1 dual-review trajectory**: codification should reduce DR-1 catches on FBCD-1 sub-modes (a/b) over time as first-Critic internalizes. Empirical signal: if DR-1 catches on (a/b) reach 0 across slices 25-35, codification is empirically validated; if persistent ≥1 DR-1 catch per slice, sub-mode wording needs refinement.
- **N=2-cross-slice proactive codification convention extended**: slice-024 is the first codification slice authored without a prior dedicated /critic-calibrate run. Convention precedent: EPGD-1 (slice-013) + SCPD-1 (slice-015) both codified at N=2 cross-slice without dedicated calibration. Slice-024 extends this to N=4-distinct-slice / N=10-cumulative-cross-instance. A future /critic-calibrate run (post-slice-024 reflection) should ratify FBCD-1's effectiveness retrospectively.
- **No new external dependencies, no new tooling, no new audit gates**: -D suffix prose-heuristic-only per convention.

## Cost summary

- **Implementation cost**: ~45-60 min build + ~30 min Critic-stack + ~15 min validate (~1.5-2 hours total) — slightly higher than slice-016 due to critique.md edit added (Phase 1g; slice-016 had this pre-applied via /critic-calibrate apply step which is absent for slice-024).
- **Revert cost (cheap with magnitude justification ~14-16 sites)**:
  - 1 methodology-changelog v0.38.0 entry (revert: delete entry)
  - 1 ADR-022 file (revert: delete file)
  - 1 entry-pin SECTION + 4 functions in `test_methodology_changelog.py` (revert: delete SECTION)
  - 1 PMI-1 structural-invariant supersession in `test_critique_agent.py` (revert: rename `_lists_ten_sub_clauses` → `_lists_nine_sub_clauses` + canonical-literal list 10 → 9)
  - 5 NEW body-bound tests in `test_critique_agent.py` (revert: delete functions)
  - 3 end_anchor tighten Edits on slice-016 RPCD-1 tests (revert: change anchor back to `### Bonus: weak graph edges`)
  - 1 atomic version bump (revert: 0.38.0 → 0.37.0 in 3 files)
  - 1 forward-sync methodology-changelog to installed (revert: re-sync prior in-repo state)
  - 1 forward-sync agents/critique.md to installed (revert: re-sync prior in-repo state)
  - N shippability.md row propagations + 1 new row 24 (revert: rename back + delete row 24; N determined at /build-slice Phase 5 scan)
  - 1 `agents/critique.md` Dim 9 10th sub-clause body removal (revert: delete sub-clause body in in-repo + forward-sync)
  Total ~14-16 sites; same magnitude class as ADR-010 (~12 sites) / ADR-012 (~12 sites) / ADR-014 (~13-15 sites) / ADR-015 (~13-15 sites). N=10-cumulative-cross-instance basis (slice-020 N=1 + slice-021 N=3 + slice-022 N=2 + slice-023 N=4 per per-slice critique-review.md enumeration) means revert before slice-025 ships is still cheap; post-slice-025 the conditioning becomes irreversible.
- **Irreversibles**: archived /critique outputs from slice-024+ that file findings under Dim 9's 10th sub-clause are filed permanently; in-context conditioning of the 9-dim-with-10-sub-clause Critic on its runs across slice-025+ accumulates monotonically. Same irreversible class as ADR-005 (9-dim Critic) / ADR-008 (CCC-1 v1.1) / ADR-010 (RSAD-1) / ADR-012 (EPGD-1) / ADR-014 (SCPD-1) / ADR-015 (RPCD-1). Net-zero impossible after ~3-5 post-codification slices; **refinement-over-revert is the canonical recovery path**.

## Reversibility

**Cheap** with magnitude-of-revert justification ~14-16 sites (same class as ADR-010 / ADR-012 / ADR-014 / ADR-015). All revert operations are mechanical (delete files / rename functions / change anchors back); zero load-bearing dependencies on FBCD-1's existence in slice-025+ code or vault files BEFORE slice-025 ships (post-slice-025 ships will have accumulated conditioning per Consequences section). The cheap-with-magnitude tag tracks reverting BEFORE slice-025 ships; post-slice-025, refinement-over-revert is the canonical recovery path per Cost summary irreversibles.
