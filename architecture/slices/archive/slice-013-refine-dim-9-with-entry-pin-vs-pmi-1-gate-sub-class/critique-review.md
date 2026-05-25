# Critique Review: Slice 013 refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-13
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively sound — B1 catches a real rule-ID drift; M1/M2/M3 are real correctness concerns with appropriate Major severity; m1/m2/m3 are accurate cosmetic catches. One missed finding surfaces: M1's precision-degradation analysis applies symmetrically to a sibling slice-011 test (`_cites_at_least_two_cross_slice_anchors` at `tests/methodology/test_critique_agent.py` L209-241) that uses the SAME body bounds as `_names_both_sub_modes` — the first Critic flagged only one of the two affected tests. One minor evidence inaccuracy in B1 (claims 22 EPG-1 occurrences in mission-brief; actual count is 17) — does not invalidate the finding but should be corrected at TRI-1.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1: Rule-ID drift EPG-1 vs EPGD-1** — VALID; severity Blocker is appropriate. Empirically confirmed: `mission-brief.md` contains 17 `EPG-1` occurrences and 0 `EPGD-1` (the Critic's claim of 22 is overcounted but directionally correct); `design.md` contains 21 `EPGD-1` and 0 `EPG-1`; `ADR-012` contains 13 `EPGD-1`. The drift includes test function names (`_epg_1_` vs `_epgd_1_`) which would create Builder ambiguity at /build-slice Phase 1b test creation — TF-1 rows reference different function names than design.md / ADR-012. Blocker severity is justified because the Builder cannot proceed deterministically without resolution. Wiegers' SRS-completeness framework: conflicting requirement statements in primary specifications constitute Type-A defects that must block build.

- **M1: `_names_both_sub_modes` precision-degradation** — VALID; severity Major is appropriate. Empirically confirmed against `tests/methodology/test_critique_agent.py` L178-206: the test body-bounds with `start_anchor = "Recursive self-application discipline"` (L192) and `end_anchor = "### Bonus: weak graph edges"` (L193). Once slice-013 inserts the 7th sub-clause between L172 and L174 of `agents/critique.md`, the body widens to include the new sub-clause body which contains the literal substrings `Build-time slip mode` and `Design-time-pre-empted success mode` (design.md L106-L107). The slice-011 test's semantic intent — verifying ONLY RSAD-1 covers both sub-modes — is silently undermined. The mid-slice smoke gate (mission-brief L129) only runs the suite for PASS/FAIL, not for body-bound semantic correctness, so it would NOT catch this implicit regression. Major (not Blocker) is correct: it's a guard-precision degradation, not a current-build failure.

- **M2: `_paragraph_cites_slice_011_and_012` anchor-list under-specified** — VALID; severity Major is appropriate. design.md L8 lists anchors in narrative prose only ("Cross-slice anchors: `slice-011`, `slice-012`, `Phase 1b INSERT`, ..."); mission-brief AC #2 + verification plan row 2 defer to "per /design-slice choice" — but /design-slice did not formalize the strict-both / ≥k-of-n semantics that slice-011's `_cites_at_least_two_cross_slice_anchors` (L209-241) used as precedent. This is an under-engineering / contract-gap concern per Newman's "specs must constrain implementer choice deterministically." Not over-specification: slice-011's analogous test had this exact discipline (strict-both for cross-slice + ≥1-of-6 for sub-class).

- **M3: N-surface count drift (N=2 vs actual N=3)** — VALID; severity Major is appropriate. Empirically confirmed against `tests/methodology/test_methodology_changelog.py` L263: "ONE canonical phrase pinned across N=3 surfaces: agents/critique.md..." The mission-brief AC #4 (L19) miscounts to N=2 by omitting the `agents/critique.md` Dim 9 7th sub-clause title surface. This is more than documentation precision: it under-specifies the schema-pin invariant the slice ratchets, and the Builder writing `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` docstring + AC #4 wording would propagate the miscount. Major is correct because the N-discipline lineage tracking (slice-008..012 cumulative) depends on numerical accuracy for /critic-calibrate later.

- **m1: ADR-012 L40 line-number phrasing ambiguity** — VALID; severity Minor is appropriate. ADR-012 L40 phrases as if `Recursive self-application discipline` literal lives at L172 (it's at L168; L172 is the close-line of the sub-clause body). Cosmetic accuracy fix.

- **m2: ADR-012 "N=2 stable" pre-empts post-validation language** — VALID; severity Minor is appropriate. ADR-012 uses "N=2 stable" at L42, L55, L89 — design-stage artifact using post-empirical-validation language. m2's proposed fix is accurate.

- **m3: Verification plan row 4 EPG-1 hedge** — VALID; severity Minor is appropriate. Folded into B1's sweep correctly.

## Suspicious findings

No suspicious findings. Every first-Critic finding maps to verifiable evidence in the slice's artifacts.

## Missed findings

- **M-add-1: `_cites_at_least_two_cross_slice_anchors` carries the SAME body-bound precision-degradation as M1's `_names_both_sub_modes`** — `tests/methodology/test_critique_agent.py` L209-241 (`test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors`) uses identical `start_anchor = "Recursive self-application discipline"` + `end_anchor = "### Bonus: weak graph edges"` body bounds (L225-L226). After slice-013 appends the 7th sub-clause body between these anchors, the body widens to include design.md L105-L109 prose — which contains the literal substring `M1` (in "Critic M1 ACCEPTED-FIXED" at L107). The test's `sub_class = ["M2", "DEVIATION-3", "BC-PROJ-2", "B1", "B5", "M1"]` allowlist's `sc_count >= 1` assertion would falsely satisfy if the 6th sub-clause body lost ALL its sub-class anchors — `M1` would leak in from the 7th sub-clause body. The cross-slice strict-both `["slice-009", "slice-010"]` assertion is robust (those substrings don't appear in 7th sub-clause body), so cs_count==2 stays correct — but sc_count's regression-guard is silently undermined.

  Framework: Hendrickson, "test bodies should be scoped to the unit under test; widening body-bounds across unrelated content erodes diagnostic value." Severity: Major (same severity class as M1; symmetric defect class).

  Proposed fix: extend M1's `end_anchor` tightening to BOTH affected tests. Tighten `_cites_at_least_two_cross_slice_anchors` end_anchor at L226 from `"### Bonus: weak graph edges"` to `"Entry-pin-vs-PMI-1-gate semantics conflation"` symmetrically, AND add slice-013's symmetric test `test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors` (cross-slice strict-both `["slice-011", "slice-012"]`, sub-class allowlist per design.md formalization from M2). TF-1 plan grows 8 → 12 rows total post-Critic (M1 contributed +2; M-add-1 contributes +2 more).

  This finding is the strongest meta-Critic catch because it surfaces a pattern-blindness in the first Critic: having identified the precision-degradation class on `_names_both_sub_modes`, the first Critic did NOT search for sibling tests sharing the same body-bound pattern. A single grep on `end_anchor = "### Bonus: weak graph edges"` would have surfaced both affected tests.

## Severity adjustments

No severity adjustments. All seven first-Critic findings are filed at appropriate severities.

## Notes

Meta-Critic confidence: HIGH. The first Critic's review is empirically grounded — every claim was independently verified against the actual artifacts (mission-brief grep counts, test source line numbers, slice-011 docstring text, design.md sub-clause body content). The one missed finding (M-add-1) is a symmetric sibling to M1 that a more systematic scan would have surfaced — calibration observation: first Critic correctly identified the precision-degradation defect CLASS on one instance but did not generalize the search across all body-bound sibling tests with identical anchors. This is a single-slice pattern-blindness, not a systemic Critic-prompt gap; the discipline of "having found a body-bound widening defect, grep for all tests sharing those anchors" could be added to Dim 9 sub-clause 2 (canonical inventories) at a future /critic-calibrate. The 1B/3M/3m severity distribution is calibrated (NOT inflated) — slice-013 carries one substantive Blocker-class defect (rule-ID drift creating build ambiguity), three real Major-class concerns (one Hendrickson body-bound, one Newman contract-gap, one Wiegers numerical-spec drift), and three real cosmetic Minor-class fixes. The recursive-self-application N=5 empirical-validation claim in critique.md L11 + L28 + L119 is defensible: rule-ID drift between primary specifications IS a Type-A specification defect of the class RSAD-1 was codified to catch ("slice authoring rule X had its own prose checked under rule X"), not merely a documentation inconsistency. One small caveat: the Critic's "22 occurrences" evidence in B1 is overcounted (actual: 17); Builder should use the corrected number at TRI-1 triage.
