# Critique: Slice 016 refine-dim-9-with-runtime-prerequisite-completeness-sub-class

**Critic reviewed**: mission-brief.md, design.md, ADR-015
**Date**: 2026-05-13
**Result**: CLEAN (post-Builder-fix-prose + user-owned triage per TRI-1; all 7 findings ACCEPTED-FIXED)

## Summary

The codification template (methodology-changelog v0.31.0 + ADR-015 + pin-tests + entry-pin + atomic version bump + shippability propagation) is canonically applied, with substantive-discipline anchor tuple `["import", "_ALLOWED_STATUSES", "sibling", "end_anchor"]` empirically verified (all 4 literals present at L186 of `agents/critique.md`) and shippability.md consumer scan empirically complete (rows 6, 11, 13, 15). However, two BLOCKER-class defects existed in AC #4(c) / Phase 1e / Audit 7 of the original draft: the end_anchor tighten plan targeted the WRONG TWO TESTS (`_location_pinned` siblings at L173 + L304, neither of which should be tightened per the slice-013 / slice-015 precedent) AND SKIPPED the THREE CORRECT TESTS (slice-015 SCPD-1's `_names_both_sub_modes` at L519 + `_paragraph_cites_slice_013_and_014` at L554 + `_cites_at_least_two_cross_slice_anchors` at L594). Additionally, the test names in AC #4(c) and TF-1 plan referenced non-existent functions. The slice itself IS an RPCD-1 codification slice with high recursive-self-application prior — and the design.md committed an RPCD-1 sub-mode (c) sibling-grep miss on its own body-bound-test plan AND an RPCD-1 sub-mode (b) factual-error on the `_ALLOWED_STATUSES` allowlist composition. All 7 findings ACCEPTED-FIXED at /critique fix-prose Phase — pending user-owned triage.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC #4(c) / Phase 1e / Audit 7 end_anchor tighten mis-identifies BOTH target tests; mis-attributes EPGD-1's `_location_pinned` to slice-015 SCPD-1; SKIPS the actual three SCPD-1 body-bound tests
- **Claim under review**: design.md (pre-fix) "End_anchor tighten Edit on slice-011 RSAD-1 body-bound test at L173/177 ... End_anchor tighten Edit on slice-015 SCPD-1 body-bound test at L304/308"; Audit 7 pre-fix "L173/177 — slice-011 RSAD-1 `_present` test ... L304/308 — slice-015 SCPD-1 `_present` test"; mission-brief AC #4(c).
- **Issue**: Three structurally-distinct empirical errors compound:
  1. **L173 belongs to `test_critique_dim_9_recursive_self_application_location_pinned`** (RSAD-1 `_location_pinned`, NOT `_present` as Audit 7 claimed). Per slice-013 M1 + slice-015 M1, `_location_pinned` tests are NEVER tightened — their `### Bonus:` end_anchor is structurally load-bearing.
  2. **L304 belongs to `test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned`** — the EPGD-1 `_location_pinned` test, NOT slice-015 SCPD-1. Audit 7's classification was empirically false on TWO counts: (a) L304's actual `start_anchor = "Recursive self-application discipline"`, and (b) L304's containing function is `_entry_pin_vs_pmi_1_gate_location_pinned`. The Builder mis-attributed an EPGD-1 test to slice-015 SCPD-1.
  3. **The actual slice-015 SCPD-1 body-bound tests requiring end_anchor tighten per generic methodology recurrence N=2 → N=3 stable are at L519, L554, and L594** — `_names_both_sub_modes`, `_paragraph_cites_slice_013_and_014`, `_cites_at_least_two_cross_slice_anchors`. After slice-016 inserts RPCD-1 between SCPD-1's close and the H3, these three tests' search bodies widen to include RPCD-1's body too. The slice-016 plan tightened ZERO of them.
- **Evidence**:
  - `tests/methodology/test_critique_agent.py:158-183` (RSAD-1 `_location_pinned` body containing L173 end_anchor)
  - `tests/methodology/test_critique_agent.py:286-314` (EPGD-1 `_location_pinned` body containing L304 end_anchor)
  - `tests/methodology/test_critique_agent.py:505-614` (the 3 actual SCPD-1 body-bound tests at L519/554/594)
  - Slice-015 reflection Aggregated-lessons #40 ("every future Dim 9 sub-clause append MUST tighten its predecessor's body-bound tests' end_anchors to the new sub-clause's title")
  - `methodology-changelog.md` v0.30.0 L45 (canonical slice-015 record naming the 3 EPGD-1 tests tightened at slice-015)
- **Proposed fix**: Replace AC #4(c), Phase 1e, and Audit 7 with the empirically-correct targets — tighten the 3 SCPD-1 body-bound tests at L519/554/594; leave the 3 `_location_pinned` siblings (L173, L304, L492) at `### Bonus:`.
- **Builder draft**: **ACCEPTED-FIXED** at `mission-brief.md` AC #4(c) + TF-1 plan rows + `design.md` "What's new" bullet + Phase 1e + Audit 7 (all 5 fix-refs applied during /critique fix-prose Phase 2026-05-13).

#### B2: TF-1 plan uses test function names that don't exist in `tests/methodology/test_critique_agent.py`
- **Claim under review**: mission-brief TF-1 plan rows (pre-fix) for AC #4 referenced `test_critique_dim_9_rsad_1_body_pins_design_time_and_build_time_sub_modes` and `test_critique_dim_9_scpd_1_body_pins_both_sub_modes`.
- **Issue**: NEITHER test name exists in `tests/methodology/test_critique_agent.py`. Per Wiegers (every claim traces to evidence), the design must reference real artifacts. A `--strict-pre-finish` TF-1 audit at /build-slice Phase 6 would map the planned test names to nothing. This is itself an RPCD-1 sub-mode (c) self-application violation: NEW row names introduced without grep-verifying they match existing sibling functions.
- **Evidence**: Empirical grep at `tests/methodology/test_critique_agent.py` returns L505, L535, L577 as the canonical slice-015 SCPD-1 body-bound test function names.
- **Proposed fix**: Replace the two TF-1 plan rows with three rows naming the actual SCPD-1 body-bound test function names being tightened.
- **Builder draft**: **ACCEPTED-FIXED** at `mission-brief.md` TF-1 plan rows 7-9 (fix-ref applied during /critique fix-prose Phase; replaced with 3 actual function names — `_names_both_sub_modes`, `_paragraph_cites_slice_013_and_014`, `_cites_at_least_two_cross_slice_anchors`).

### Majors (address this slice)

#### M1: Design Audit 2 falsely claims `WRITTEN-AS-EDIT` is in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist — empirically contradicted
- **Claim under review**: design.md Audit 2 (pre-fix) "TF-1 plan uses statuses from `_ALLOWED_STATUSES` exclusively (PENDING / WRITTEN-FAILING / PASSING / WRITTEN-AS-EDIT). The `WRITTEN-AS-EDIT` status was added to `_ALLOWED_STATUSES` at slice-015 M-add-1; slice-016 reuses without modification."
- **Issue**: `tools/test_first_audit.py:65` reads `_ALLOWED_STATUSES = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})` — `WRITTEN-AS-EDIT` is NOT in the allowlist. Slice-015 M-add-1 per methodology-changelog v0.30.0 L47 was the opposite: "Fixed per Option (b): flipped 3 rows to `PASSING` matching slice-013 precedent" — meta-Critic fix AVOIDED introducing `WRITTEN-AS-EDIT`. The slice-016 TF-1 plan itself uses only PENDING/WRITTEN-FAILING/PASSING (so no audit violation), but the provenance claim is factually wrong AND this is an RPCD-1 sub-mode (b) self-application factual error in the slice's own design.md.
- **Evidence**: `tools/test_first_audit.py:65` literal + methodology-changelog v0.30.0 L47.
- **Proposed fix**: Correct Audit 2's claim to reflect the 3-element allowlist and the slice-015 M-add-1 flip-to-PASSING resolution.
- **Builder draft**: **ACCEPTED-FIXED** at `design.md` Audit 2 (fix-ref applied during /critique fix-prose Phase; now states the 3-element allowlist with empirical citation to L65 + the slice-015 flip-to-PASSING resolution).

#### M2: Entry-pin function count claim off-by-1 to off-by-2
- **Claim under review**: mission-brief Must-not-defer + design.md "Slice-016 modifications" + Audit 4 + ADR-015 — all stated "0 of 8 prior entry-pin functions (v0.22.0..v0.30.0)".
- **Issue**: v0.22.0..v0.30.0 spans 9 minor versions (0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30). Additionally `tests/methodology/test_methodology_changelog.py` contains 10 entry-pin functions because v0.29.0 has 2 (`_pmi_1_v1_1_entry_present` at L437 + `_entry_names_supersession_pattern_retired` at L499) per slice-014 (a)↔(b) duality. The 8-claim is off-by-1 (vs 9 versions) or off-by-2 (vs 10 functions). Empirical safety remains intact — Phase 1b INSERT under NEW SECTION header is structurally separated — but the count claim is a numerical-inflation defect (Wiegers AC-trace class; slice-012 M2 sibling).
- **Evidence**: Grep `^def test_v_0_\d+_0_` at `tests/methodology/test_methodology_changelog.py` returns 10 functions at L76, 111, 152, 202, 250, 304, 370, 437, 499, 747.
- **Proposed fix**: Change all 4 occurrences to "0 of 10 prior entry-pin functions (v0.22.0..v0.30.0 spans 9 minor versions; v0.29.0 has 2 entry-pin functions per slice-014 (a)↔(b) duality)".
- **Builder draft**: **ACCEPTED-FIXED** at `mission-brief.md` Must-not-defer + `design.md` Components-touched test_methodology_changelog.py bullet + Audit 4 (3 fix-refs applied during /critique fix-prose Phase; corrected to "0 of 10 prior entry-pin functions" with full evidence chain).

#### M3: Audit 7 grep-completeness claim is empirically incomplete — only enumerated 2 of 6 `end_anchor = "### Bonus: weak graph edges"` assignments in test_critique_agent.py
- **Claim under review**: design.md Audit 7 (pre-fix) enumerated only L173/177 and L304/308.
- **Issue**: A literal grep returns 6 hits: L173, L304, L492, L519, L554, L594. Audit 7's grep result was incomplete. This is an RPCD-1 sub-mode (c) sibling-grep failure on the slice's own audit — the very discipline the slice codifies, inadequately applied. Per RSAD-1 design-time mode + RPCD-1 sub-mode (c) recursive-self-application probe (high prior, N=7 cumulative post-RSAD-1).
- **Evidence**: `grep -n 'end_anchor = "### Bonus: weak graph edges"' tests/methodology/test_critique_agent.py` returns 6 lines.
- **Proposed fix**: Re-write Audit 7 enumerating all 6 sites, classifying each as `_location_pinned`-class (KEEP) or body-bound-class (TIGHTEN). Result: 3 of 6 tighten (L519, L554, L594); 3 of 6 KEEP (L173, L304, L492).
- **Builder draft**: **ACCEPTED-FIXED** at `design.md` Audit 7 (fix-ref applied during /critique fix-prose Phase; revised to full 6-site enumeration with line-by-line classification table + meta-note explaining the self-defect-and-recovery as RPCD-1 sub-mode (c) self-application).

### Minors (log; address if cheap)

#### m1: ADR-015 Consequences section claims "PMI-1 structural-invariant supersession N=3 → N=4 stable" but supporting evidence is N=4 events (slice-011 + slice-013 + slice-015 + slice-016)
- **Claim under review**: ADR-015 Consequences (pre-fix) — N=3 → N=4 claim without cross-references.
- **Issue**: Citation-completeness — claim is directionally correct but missing the evidence-chain links to slice-011 N=1 + slice-013 N=2 + slice-015 N=3 + slice-016 N=4. Minor.
- **Proposed fix**: Add evidence-chain cross-references.
- **Builder draft**: **ACCEPTED-FIXED** at `ADR-015` Consequences (fix-ref applied during /critique fix-prose Phase; added full slice-011 → slice-016 evidence chain).

#### m2: "M0 tighten provenance" terminology in design.md Phase 1e is unusual
- **Claim under review**: design.md Phase 1e (pre-fix) "function comment updated with slice-016 M0 tighten provenance".
- **Issue**: Per slice-013/015 precedent, end_anchor tighten provenance was labeled "slice-013 M1" / "slice-015 M1" because the discipline was promulgated AT /critique time. "M0" suggested pre-/critique provenance which is now structurally incorrect since the Critic DID catch it (as B1). Per slice-013/015 convention, this should be "slice-016 /critique B1 ACCEPTED-FIXED tighten provenance".
- **Proposed fix**: Rename to slice-013/015 convention.
- **Builder draft**: **ACCEPTED-FIXED** at `design.md` Phase 1e (fix-ref applied during /critique fix-prose Phase; revised provenance label to "slice-016 /critique B1 ACCEPTED-FIXED tighten provenance (mirrors slice-013 M1 + slice-015 M1 convention)").

### Missed findings (added by meta-Critic at /critique-review per DR-1)

#### M-add-1: Missing `test_critique_dim_9_runtime_prerequisite_completeness_location_pinned` — regression-guard coverage gap vs N=3 stable `_sub_clause_present` + `_location_pinned` duality
- **Surfaced by**: meta-Critic at /critique-review (DR-1 verdict EXTEND; see `critique-review.md` Missed-findings section).
- **Claim under review**: `design.md` (pre-fix) L11-15 enumerated 4 NEW body-bound tests for RPCD-1: `_sub_clause_present`, `_names_three_sub_modes`, `_paragraph_cites_slice_013_014_015`, `_cites_substantive_discipline_anchors`. The conspicuously ABSENT test is `_location_pinned`.
- **Issue**: Slice-011 RSAD-1 (L146 `_sub_clause_present` + L158 `_location_pinned`), slice-013 EPGD-1 (L270 + L286), and slice-015 SCPD-1 (L463 + L475) ALL carry the `_sub_clause_present` + `_location_pinned` duality. Slice-016 specified only `_sub_clause_present` AND described it ambiguously with scoped-find semantics (which is `_location_pinned`'s convention per slice-015 L475, NOT `_sub_clause_present` bare-substring per slice-015 L463). Either coverage gap (missing `_location_pinned`) or naming confusion — both readings are a regression-guard preservation defect. Per slice-009 M1 + slice-010 M1 location-pin convention: the `_location_pinned` test specifically defends against "a future drift moving the new sub-clause out of Dim 9 silently passing substring-only pin tests" (verbatim from RSAD-1 `_location_pinned` docstring L161-163).
- **Evidence**: `tests/methodology/test_critique_agent.py:146-183` (RSAD-1 duality) + `:270-314` (EPGD-1 duality) + `:463-502` (SCPD-1 duality); slice-016 `design.md` pre-fix L11-15.
- **Framework**: Wiegers (regression-guard coverage symmetry across N=3 prior reference instances) + CCC-1 v1.1 sub-clause 2 design-doc-level surface (mechanical-row symmetry asymmetry: slice-016 design.md mechanical enumeration should mirror canonical-inventory across slice-011/013/015).
- **Severity**: Major. Location-pin is regression-guard not blocker; slice ships without it but loses defense against future Dim 9 restructuring drifting RPCD-1 out of Dim 9. NOT Blocker because /build-slice still ships (omission is coverage gap, not wrong-target).
- **Pattern significance**: structurally distinct from prior N=3 DR-1 catches (slice-013/014/015 M-add-1 all RPCD-1 sub-mode (a/b/c)). This M-add-1 is a Wiegers-class regression-guard coverage symmetry omission — design-doc-level mechanical-table-vs-canonical-inventory asymmetry. Watch-list candidate at N=1 for future /critic-calibrate aggregation.
- **Proposed fix**: Add 5th body-bound test `test_critique_dim_9_runtime_prerequisite_completeness_location_pinned` mirroring slice-015 L475 — scoped-find with `start_anchor = "Shippability-catalog consumer-reference propagation"` + `end_anchor = "### Bonus: weak graph edges"` + `canonical = "Runtime-prerequisite completeness on proposed fixes"`. Clarify `_sub_clause_present` semantics as bare-substring per slice-015 L463. Update mission-brief AC #4(b) + TF-1 plan + shippability row 16 pytest commands.
- **Builder draft**: **ACCEPTED-FIXED** at `design.md` "What's new" bullet + Phase 1d + `mission-brief.md` AC #4(b) + TF-1 plan rows (5 body-bound rows added) + design.md + ADR-015 cost summaries (4 → 5 NEW body-bound tests). 5-test pattern now mirrors slice-013 + slice-015 precedent; `_sub_clause_present` + `_location_pinned` duality N=3 → N=4 stable post-codification.

## Dimensions checked

- [x] **Unfounded assumptions** — Found: M1 (Audit 2 `_ALLOWED_STATUSES` false claim; sub-mode (b) self-application miss); B2 (TF-1 plan uses non-existent test function names); M3 (Audit 7 grep-completeness incomplete — 2 of 6 enumerated). Substantive-discipline anchor tuple `["import", "_ALLOWED_STATUSES", "sibling", "end_anchor"]` empirically VALIDATED via grep against `agents/critique.md` L186 (all 4 literals present). Shippability.md scan rows 6, 11, 13, 15 empirically VALIDATED. Anchor-uniqueness for `Runtime-prerequisite completeness on proposed fixes` (1 occurrence at L186) + `### Bonus: weak graph edges` (1 occurrence at L188) VALIDATED.
- [x] **Missing edge cases** — None applicable. Methodology codification with no I/O surface, no concurrency, no platform layer.
- [x] **Over-engineering** — None. Standard codification template, no speculative generality.
- [x] **Under-engineering** — Found: B1 + B2 are direct AC #4(c) under-engineering — Wiegers AC-to-design-element traceability broken because Phase 1e Edits targeted wrong line numbers / wrong functions; methodology-audit conformance: slice's own design+TF-1 plan would have failed --strict-pre-finish.
- [x] **Contract gaps** — None. No API contracts, endpoints, events.
- [x] **Security** — None. No auth surface, no user input, no secrets, no IDOR.
- [x] **Drift from vault** — None. ADR-015 references ADR-005/006/010/012/013/014 — all valid extant ADRs. methodology-changelog v0.31.0 entry plan extends v0.30.0 entry shape — consistent.
- [x] **Web-known issues** — Skipped — methodology codification with no external technology. Per dimension's honest-out: no specific framework applied.
- [x] **Cross-cutting conformance** — Found: B1 + B2 + M1 + M3 are all RPCD-1-class self-defects (sub-mode (b) factual error M1; sub-mode (c) sibling-grep incompleteness B1+M3; sub-mode (a)-adjacent symbol-reference completeness B2). The slice authoring RPCD-1 committed RPCD-1-class self-defects on its own draft — recursive-self-application discipline N=7 → N=8 cumulative post-RSAD-1 codification empirically VALIDATED at /critique design-time. EPGD-1 narrow-scope discipline empirically applied correctly (off-by-1 count M2 is the only EPGD-1-related concern). SCPD-1 proactive-application empirically VALIDATED (rows 6, 11, 13, 15 complete consumer set). RPCD-1 sub-modes (a) PASS, (b) FAIL (M1), (c) FAIL (B1+M3) — slice ratifies the discipline by exemplifying it on its own draft.

## Triage

**Triaged by**: user
**Date**: 2026-05-13
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Fix-ref: mission-brief.md AC #4(c) + design.md "What's new" bullet + Phase 1e + Audit 7. Empirically-correct targets: tighten 3 SCPD-1 body-bound tests at L519/554/594; KEEP 3 `_location_pinned` siblings (L173 RSAD-1 + L304 EPGD-1 + L492 SCPD-1) at `### Bonus:` per slice-013 + slice-015 precedent. |
| B2 | Blocker  | ACCEPTED-FIXED | Fix-ref: mission-brief.md TF-1 plan rows 7-9. Replaced non-existent function names with 3 actual SCPD-1 body-bound function names verified by grep at `tests/methodology/test_critique_agent.py` L505/535/577. |
| M1 | Major    | ACCEPTED-FIXED | Fix-ref: design.md Audit 2. Corrected to 3-element allowlist (`PENDING/WRITTEN-FAILING/PASSING`) with empirical citation to `tools/test_first_audit.py:65` + slice-015 M-add-1 flip-to-PASSING resolution citing methodology-changelog v0.30.0 L47. |
| M2 | Major    | ACCEPTED-FIXED | Fix-ref: mission-brief.md Must-not-defer + design.md Components-touched bullet + Audit 4. Corrected to "0 of 10 prior entry-pin functions touched (v0.22.0..v0.30.0 spans 9 minor versions; v0.29.0 has 2 entry-pin functions per slice-014 (a)↔(b) duality)" with grep evidence at L76/111/152/202/250/304/370/437/499/747. |
| M3 | Major    | ACCEPTED-FIXED | Fix-ref: design.md Audit 7. Revised to full 6-site enumeration table (L173/304/492 `_location_pinned`-class KEEP; L519/554/594 body-bound-class TIGHTEN) + meta-note on RPCD-1 sub-mode (c) self-defect-and-recovery (recursive-self-application N=7 → N=8 cumulative empirically VALIDATED). |
| m1 | Minor    | ACCEPTED-FIXED | Fix-ref: ADR-015 Consequences. Added PMI-1 structural-invariant supersession evidence chain (slice-011 N=1 → slice-013 N=2 → slice-015 N=3 → slice-016 N=4) for citation completeness. |
| m2 | Minor    | ACCEPTED-FIXED | Fix-ref: design.md Phase 1e. Renamed "M0 tighten provenance" → "slice-016 /critique B1 ACCEPTED-FIXED tighten provenance (mirrors slice-013 M1 + slice-015 M1 convention)" per established Dim 9 codification convention. |
| M-add-1 | Major (meta-Critic /critique-review per DR-1) | ACCEPTED-FIXED | Fix-ref: design.md "What's new" bullet + Phase 1d + mission-brief.md AC #4(b) + TF-1 plan (5 body-bound rows; was 1) + design.md & ADR-015 cost summaries (4 → 5 NEW body-bound tests). Added 5th body-bound test `_runtime_prerequisite_completeness_location_pinned` (scoped-find with `Shippability-catalog consumer-reference propagation` start_anchor + `### Bonus: weak graph edges` end_anchor) mirroring slice-015 L475 precedent; clarified `_sub_clause_present` as bare-substring per slice-015 L463. Completes N=3 stable `_sub_clause_present` + `_location_pinned` duality → N=4 stable post-codification. |
