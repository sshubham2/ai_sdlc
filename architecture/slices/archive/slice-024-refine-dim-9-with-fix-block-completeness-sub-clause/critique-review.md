# Critique Review: Slice 024 refine-dim-9-with-fix-block-completeness-sub-clause

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-15
**First-Critic verdict**: NEEDS-FIXES

**First-Critic disposition summary**: 3 Blockers + 7 Majors + 6 Minors; 11 ACCEPTED-FIXED applied in-round; 1 ACCEPTED-PENDING (m1); 3 OVERRIDDEN (m2/m3/m6); 1 DEFERRED (m5)
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 16 findings are all VALID with correct severities — every B/M reflects a real FBCD-1 sub-mode (a) catch on the slice's own drafts, and the three OVERRIDDEN minor dispositions (m2/m3/m6) correctly honour the Critic's own honesty rule. Builder's 11-site ACCEPTED-FIXED sweep was disciplined and reached most sibling sites. However, second-pass grep-verification surfaces **three missed FBCD-1 sub-mode (b) sibling-sweep gaps** on the Builder's own coordinated fix-block — exactly the empirical confirmation FBCD-1's codification predicts. The most serious is a TPHD-1 sub-mode (c) gap that the first Critic's Audit 8 self-applied PASSED erroneously: TF-1 plan AC #4 row's test-function name does not match the function name in design.md L28 + Must-not-defer L62. The other two are residual `Phase 4 scan` references in Cost-summary sections (design.md L242 + ADR-022 L83) that the B3 fix-block missed. Recursive-self-application closure: FBCD-1's codifying slice demonstrates FBCD-1 sub-mode (b) on its own fix-block at the meta-Critic layer — exactly as Must-not-defer L65 predicted ("Empirically expected N≥1 FBCD-1 catch on slice's own drafts").

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (Cumulative-count N=9 → N=10 across 11 sites) — confirmed; severity Blocker appropriate; Builder's 11-site sweep verified clean by independent grep `N=9` — only critique.md historical quotes remain; design.md L29/L138/L176 hits are the unrelated PMI-1 retirement-proof N=9→N=10 atomic-bump count; design.md L42/L140 hits are the mini-CAD-1 N=8→N=9 count; design.md L58 is the sub-clause-count N=9→N=10. PASS verification.
- **B2** (Phase 1c misattribution — PMI-1 versioned-gate vs structural-invariant supersession) — confirmed; severity Blocker appropriate; mission-brief.md L62 correctly rewritten to distinguish Phase 1b entry-pin INSERT (EPGD-1 narrow-scope applies) from Phase 1c structural-invariant supersession (different module/discipline class).
- **B3** (Phase numbering drift — SCPD-1 propagation at Phase 4 vs Phase 5) — confirmed; severity Blocker appropriate; fix applied at design.md L32/L141/L206 + mission-brief.md L63. **HOWEVER**: see MISS-1 below for residual Cost-summary sites the Builder's sweep missed.
- **M1** (Phantom Phase 8 → Phase 4 at mission-brief.md L60) — confirmed; severity Major appropriate; grep verifies zero hits in current mission-brief.md / design.md / ADR-022.
- **M2** (Supersession event-count drift mission-brief L34 N=3 vs design N=5) — confirmed; severity Major appropriate; mission-brief L34 corrected with full chain.
- **M3** (Sub-mode (a) count harmonization N=2 + M5 reclassified to sub-mode (b)) — confirmed; severity Major appropriate.
- **M4** (Audit 1 line-citation L7 → L5) — confirmed; severity Major appropriate.
- **M5** (Strict-4-of-4 semantic disambiguation) — confirmed; severity Major appropriate; design.md L155-L156 disambiguates strict-4-of-4-cross-slice-anchors-at-test-pin vs strict-5-of-5-surface-sites-for-cross-file-consistency cleanly.
- **M6** (Cross-reference encoding by canonical title strings, not ordinal position) — confirmed; severity Major appropriate; design.md L8 + Phase 1g notes + ADR-022 L64 all consistent.
- **M7** (Substantive-anchor hyphenation "fix block" → "fix-block") — confirmed; severity Major appropriate; design.md L17 anchor tuple correctly `"fix-block"`. Grep verifies bare "fix block" (space) appears 0 times outside historical critique.md quotes; the 1 ADR-022 L19 hit is correctly preserved as slice-020 M-add-1 historical prose quote.
- **m1** (META-1/2/3 mnemonic spot-check) — confirmed; ACCEPTED-PENDING acceptable.
- **m4** (Must-not-defer count 11 → 10) — confirmed; mission-brief L120 = "10 items" matches enumerated count.
- **m2 / m3 / m6 OVERRIDDEN** — confirmed correct application of Critic's own honesty rule. The first Critic explicitly noted "No fix needed" / "False alarm" / "Consistent. No fix needed." — these are legitimate non-findings, not findings the Builder dismissed by abusing override. PASS.
- **m5 DEFERRED** — confirmed; cosmetic-only prose tightening; defer reasonable.

## Suspicious findings

No suspicious findings. Every first-Critic B/M reflects a real cross-file drift verifiable by grep; every Minor with OVERRIDDEN disposition correctly applies the Critic's own honesty rule. Note in particular that m2/m3/m6 OVERRIDDEN are not abuse — the Critic explicitly noted "No fix needed" in its own finding body, signaling these were logged for visibility only. The Builder is not dismissing legitimate concerns; they respect the Critic's self-assessment.

## Missed findings

Three FBCD-1 sub-mode (b) sibling-sweep gaps that the Builder's 11-site sweep AND the first Critic missed — exactly the empirical confirmation FBCD-1's codification predicts:

### M-add-1: Phase 4 → Phase 5 SCPD-1 propagation incomplete in Cost-summary sections

- **Severity**: Major (FBCD-1 sub-mode (b) on Builder's own B3 fix-block; CCC-1 / Sommerville)
- **Issue**: The B3 fix-block sweep propagated `Phase 4` → `Phase 5` to design.md L32 + design.md L141 (Phase plan) + design.md L206 (Audit 7) + mission-brief.md L63. But **design.md L242 (Cost summary) AND ADR-022 L83 (Cost summary)** BOTH still say `"N shippability.md row propagations + 1 new row 24 (revert: rename back + delete row 24; N determined at /build-slice Phase 4 scan)"`. The SCPD-1 row-propagation scan happens at Phase 5 per the Phase plan; Cost summary's stale `Phase 4 scan` is the exact FBCD-1 sub-mode (b) class — Builder's coordinated grep on bare `Phase 4` (B3) and bare `Phase 8` (M1) missed the qualifier-prefixed `Phase 4 scan` occurrences. Recursive-self-application closure observed at meta-Critic layer.
- **Evidence**: design.md L242 + ADR-022 L83.
- **Proposed fix**: design.md L242 + ADR-022 L83: `Phase 4 scan` → `Phase 5 scan`.

### M-add-2: TF-1 plan row AC #4 test-function name mismatch with design.md L28 + Must-not-defer L62 + slice-016 precedent

- **Severity**: Major (TPHD-1 sub-mode (c); Wiegers AC-traceability)
- **Issue**: mission-brief.md L45 (TF-1 plan AC #4 row) names the test function `test_adr_022_present_and_reversibility_cheap`. But design.md L28 names the ADR-pin function as `test_adr_022_exists_and_names_fbcd_1_canonical_phrase` (mirroring `test_adr_015_exists_and_names_rpcd_1_canonical_phrase` slice-016 row 16 precedent), and mission-brief.md L62 (EPGD-1 Must-not-defer enumeration) ALSO names this function `test_adr_022_exists_and_names_fbcd_1_canonical_phrase`. The first Critic's Audit 8 TPHD-1 sub-mode (c) self-application PASSED erroneously (design.md L220-L221 says `AC #4 tests: 1 ADR-022 entry-pin test — design.md L33 → CHECK ✓` but didn't verify the actual function name string-match across the three surfaces). At /build-slice, Builder following TF-1 plan would write the wrong name. TPHD-1 sub-mode (c) class: a disposition-promised test is not enumerated in TF-1 plan with the same name.
- **Evidence**: mission-brief.md L45 vs design.md L28 vs mission-brief.md L62.
- **Proposed fix**: mission-brief.md L45 TF-1 plan row test-function column: `test_adr_022_present_and_reversibility_cheap` → `test_adr_022_exists_and_names_fbcd_1_canonical_phrase`. Verification plan L55 uses the `adr_022` keyword for pytest -k, so the renamed function still resolves under keyword invocation — but the TF-1 plan must name the actual function or TF-1 audit's row-vs-implementation cross-check fails.

### M-add-3: Entry-pin function-count internal inconsistency at design.md L78

- **Severity**: Minor (FBCD-1 sub-mode (a); Wiegers Unfounded assumptions)
- **Issue**: design.md L78 says `0 of 16 prior entry-pin functions touched (v0.22.0..v0.37.0 spans 16 minor versions; v0.29.0 has 2 entry-pin functions per slice-014 (a)↔(b) duality)` — if v0.29.0 contributes 2 entry-pin functions then total prior count ≥ 17, not 16. mission-brief.md L126 separately says `entry-pin functions count = 16 → 17 stable` (consistent only IF "entry-pin" narrowly means `_entry_present_in_repo_and_installed` family — empirically 16 such functions exist in test_methodology_changelog.py for v0.22.0..v0.37.0). Two different counting conventions in adjacent files; design.md L78's parenthetical qualifier contradicts its own leading "16 prior" count.
- **Evidence**: design.md L78 vs mission-brief.md L126 vs `grep -c "^def test_v_0_.*_entry_present_in_repo_and_installed" tests/methodology/test_methodology_changelog.py`.
- **Proposed fix**: design.md L78: either drop the `(v0.29.0 has 2)` qualifier (narrow-count semantics preserved at 16) OR rewrite to `0 of 17 prior _entry_present_in_repo_and_installed-family functions touched (16 minor versions + 1 extra at v0.29.0 per slice-014 (a)↔(b) duality)`. Minor severity — internally consistent under narrow interpretation; clarification eliminates ambiguity for future readers.

## Severity adjustments

No severity adjustments. All first-Critic severities (3 Blockers, 7 Majors, 6 Minors) are appropriate to the issues raised.

## Notes

This is a high-quality first-Critic pass. Coverage of FBCD-1 sub-mode (a) catches on the slice's own drafts is thorough (10 of 13 catches in B1-M7+m4 are sub-mode (a) cross-file drifts), severities are calibrated, and the OVERRIDDEN minors correctly honour the Critic's own honesty rule rather than manufacturing findings. The Builder's coordinated 11-site sweep on the fix-block was disciplined and reached most sibling sites cleanly — verified by independent grep for `N=9` (only historical-quote hits), `Phase 8` (only historical-quote hits), `"fix block"` (space; only ADR-022 L19 historical slice-020 quote remains), and slice-021 N=2 anchor (clean). Three sub-mode (b) gaps that survived the sweep (M-add-1 + M-add-3 are FBCD-1 sub-modes b/a; M-add-2 is TPHD-1 sub-mode (c) on the first Critic's own Audit 8) are exactly the recursive-self-application closure the slice predicted at Must-not-defer L65 — codifying FBCD-1's own slice MUST commit ≥1 FBCD-1 violation on its own drafts for the empirical anchor to hold, and the meta-Critic layer is where the residual gap surfaces. Empirical confirmation: codification slice exhibits the discipline it codifies at the meta-Critic layer, matching slice-009..023 N=33 cumulative HWM recursive-self-application precedent. The slice-021 aggregated lesson ("Cross-Critic-stack scopes its grep verification to mission-brief + design + ADR but consistently misses milestone.md") was avoided this round — milestone.md was correctly included in the Builder's sweep — but M-add-1 reveals a **NEW Critic-stack blind spot**: Cost-summary sections of design.md AND ADR-022 contain Phase-numbering claims that the B3 sweep missed. Confidence: high — all three missed findings are concrete, line-cited, grep-verifiable, and Builder-actionable in a single mechanical sweep extension. None are slice-blocking; all are appropriate triage at TRI-1 for ACCEPTED-FIXED in-round.
