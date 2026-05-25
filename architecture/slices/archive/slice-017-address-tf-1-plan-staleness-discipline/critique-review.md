# Critique Review: Slice 017 address-tf-1-plan-staleness-discipline

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-13
**First-Critic verdict**: CLEAN
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 7 findings (B1 / M1-M3 / m1-m3) are all VALID with appropriate severities — empirical re-verification at the cited source line ranges confirms each substantive claim (especially B1's load-bearing TF-1-audit-semantics correction at `tools/test_first_audit.py:65/320/350-364`). However, a meta-Critic re-application of RPCD-1 sub-mode (b) NEW-status/token allowlist-audit AND Wiegers regression-guard coverage-symmetry to slice-017's own design.md Audit 4 surfaces one missed Minor: design.md L204 + L208 + 4 other sites cite "11 prior entry-pin functions" for v_0_22_0..v_0_31_0 but the actual count in `tests/methodology/test_methodology_changelog.py` is 12 (v0.31.0 is doubled per slice-016 N=4 stable `_present_in_repo_and_installed` + `_names_three_sub_modes_in_repo_and_installed` duality, the same way v0.29.0 was doubled per slice-014 (a)↔(b) duality). The slice codifies TPHD-1; missing this recursive-self-application N=2 entry-pin-duality count drift on its own draft is exactly the class TPHD-1 sub-mode (c) prerequisite-check pre-flight harmonization is designed to catch — **slice-017 IS the canonical reference instance #1 demonstrating TPHD-1 sub-mode (a) self-application at /critique-review fix-prose** (count correction harmonized across 6 sites: mission-brief.md L66 + design.md L32 + L92 + L138 + L206 + L208 + critique.md L87).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1: ADR-016 Context misrepresents `tools/test_first_audit.py --strict-pre-finish` semantics** — VALID; severity Blocker is appropriate. Empirically verified at `tools/test_first_audit.py:65` (3-element `_ALLOWED_STATUSES`) + `tools/test_first_audit.py:350-364` (`--strict-pre-finish` clause checks `row.status != "PASSING"` only; no AST/grep introspection of test bodies). The third-clause hallucination in the original ADR-016 L17 was load-bearing because it shaped the entire lesson framing. Post-fix ADR-016 L17 (re-read at current state) now correctly describes status-only check + reframes TPHD-1's value proposition as prophylactic against an audit gap. Per CCC-1 v1.1 sub-clause 1 (tooling-doc-vs-impl-parity) Blocker severity is appropriate because all three sub-modes' value propositions depended on it.

- **M1: Magnitude inconsistency (~3-5 sites vs ~13-16 sites)** — VALID; severity Major is appropriate. Empirically verified at design.md L124 (now post-fix `~13-16 sites`) + ADR-016 L141-L154 (14-site enumeration). Per slice-013 B1 rule-ID-drift class generalized to "internal-numeric-consistency", filing as Major matches precedent. CCC-1 v1.1 sub-clause 2 doc-vs-canonical-inventory parity.

- **M2: `### Step 0` placement vs existing `## Prerequisite check` fold** — VALID; severity Major is appropriate. Empirically verified at `skills/build-slice/SKILL.md:17-22` (existing Prerequisite check section) + step numbering 1,2,3,4,5,6,7,7b,7c,8 (no Step 0). Post-fix references throughout mission-brief + design.md + ADR-016 now consistently use "NEW bullet INTO existing `## Prerequisite check` section". TPHD-1 sub-mode (a) self-application empirically demonstrated by the fix block itself harmonizing TF-1 rows 8-9 function name renames in lockstep.

- **M3: Audit 6 BC-1 reasoning lists wrong trigger keywords / negative anchors** — VALID; severity Major is appropriate. Empirically verified at `architecture/build-checks.md:33-35` (BC-PROJ-2 trigger keywords `parse, fence, code-block, backtick, llm, agent, prompt, output, response` + trigger anchors `fence, code-block, llm` + 9 negative anchors). Original Audit 6 named wrong tokens that aren't in BC-PROJ-2's rule body. Post-fix Audit 6 is empirically grounded. CCC-1 v1.1 Dim 9 sub-clause "tooling-doc-vs-impl-parity".

- **m1: Rule-ID drift negative-example anchors create RSAD-1 sub-mode (b) re-introduction** — VALID; severity Minor is appropriate. Per slice-011 RSAD-1 sub-mode (b) re-introduction class (N=2 at slice-010 DEVIATION-3 + slice-011 codification body). Post-fix mission-brief.md must-not-defer #1 + design.md "Rule-ID drift" bullet use positive-form assertion.

- **m2: Mid-slice smoke gate references non-existent Phase 1f** — VALID; severity Minor is appropriate. Pure textual drift; no functional impact. Post-fix mission-brief L94 now reads "Phase 1a-1e".

- **m3: AC #5 SCPD-1 N=2 → N=3 stable counter increment unfounded** — VALID; severity Minor is appropriate. SCPD-1 proactive-application requires an active propagation event; slice-017 has no `_lists_N_sub_clauses` supersession (per AC #5 itself); counter integrity preserved by dropping increment.

## Suspicious findings

No suspicious findings. All 7 first-Critic findings empirically re-verify against source.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

### m-add-1: design.md Audit 4 entry-pin function count drift (11 vs actual 12) — recursive-self-application of TPHD-1 sub-mode (c) on the slice's own draft

- **Claim under review**: design.md L204 + L208 (and 4 other sites): `11 prior entry-pin functions exist for v_0_22_0..v_0_31_0 (v0.29.0 doubled per slice-014 (a)↔(b) duality)`.
- **Issue**: Empirical grep on `tests/methodology/test_methodology_changelog.py` returns 12 `def test_v_0_*` functions, not 11:
  - 8 singles: v0.22.0 (L76) + v0.23.0 (L111) + v0.24.0 (L152) + v0.25.0 (L202) + v0.26.0 (L250) + v0.27.0 (L304) + v0.28.0 (L370) + v0.30.0 (L747) = 8
  - v0.29.0 doubled (L437 `_present_in_repo_and_installed` + L499 `_entry_names_supersession_pattern_retired`) per slice-014 (a)↔(b) duality = +2
  - v0.31.0 doubled (L844 `_rpcd_1_entry_present_in_repo_and_installed` + L910 `_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed`) per slice-016 RPCD-1 (a)↔(b) duality = +2
  - **Total: 12 entry-pin functions**, not 11.
- **Evidence**: `grep "^def test_v_0_" tests/methodology/test_methodology_changelog.py` returns 12 matches at lines 76 / 111 / 152 / 202 / 250 / 304 / 370 / 437 / 499 / 747 / 844 / 910.
- **Severity**: Minor. Same class as the first Critic's m3 (counter-integrity / numerical-drift) and m2 (textual-drift / Phase-range off-by-one). The EPGD-1 self-application discipline guarantee ("0 of N prior entry-pin functions touched") still holds at the corrected N=12 — the slice doesn't ship with a broken artifact; it ships with a count-drift in a self-application audit table. But per slice-013 B1 internal-numeric-consistency class generalized AND given that slice-017 codifies TPHD-1 precisely to catch this category of TF-1-plan-vs-actual-state staleness, this drift on slice-017's own draft is the canonical recursive-self-application instance.
- **Recursive-self-application class**: this is structurally a Wiegers regression-guard coverage symmetry omission (slice-016 M-add-1 class N=1 → **N=2 cumulative** if user accepts) — design.md Audit 5 enumerates the duality discipline AND correctly catches itself on entry-pin Wiegers asymmetry exception, but design.md Audit 4 misses the N=2 doubling pattern at v0.31.0 mirroring v0.29.0. Per the meta-Critic's mandate to track the slice-016 M-add-1 watch-list class — this finding ratchets the class to **N=2 cumulative** post-codification.
- **Proposed fix**: Update design.md L204 + L208 + 4 other sites: `11 prior entry-pin functions` → `12 prior entry-pin functions` and `(v0.29.0 doubled per slice-014 (a)↔(b) duality)` → `(v0.29.0 doubled per slice-014 (a)↔(b) duality; v0.31.0 doubled per slice-016 RPCD-1 (a)↔(b) duality)`. Also update mission-brief.md L66 + critique.md L87 with the same correction. Verify count post-Phase 1b at /build-slice will be 12 + 3 = 15 (not 11 + 3 = 14).
- **Builder draft**: ACCEPTED-FIXED at `mission-brief.md L66` + `design.md L32 + L92 + L138 + L206 + L208` + `critique.md L87` — count corrected from 11 → 12 across all 6 sites; v0.31.0 doubling parenthetical added matching v0.29.0 doubling acknowledgement pattern. **TPHD-1 sub-mode (a) self-application empirically demonstrated** at /critique-review fix-prose: since the count change does NOT rename any test function names in TF-1 plan rows, no TF-1 plan harmonization required. EPGD-1 self-application guarantee 0/N preserved at corrected N=12. Post-slice-017 count will be 12 + 3 NEW v0.32.0 functions = 15 entry-pin functions total.

## Severity adjustments

No severity adjustments. All 7 first-Critic findings are filed at appropriate severities matching the established slice-011/013/015/016 codification-slice precedent band.

## Notes

Confidence in this meta-review: **high** on the missed-finding m-add-1 (empirically reproducible at lines 76/111/152/202/250/304/370/437/499/747/844/910 = 12 matches). Confidence on first-Critic's 7 findings being all VALID at correct severity: **high** — empirical re-read of the post-fix ADR-016 / design.md / mission-brief.md confirms each fix-prose change applied accurately at the cited line ranges.

Calibration observations: the first Critic's coverage of slice-017 was empirically dense (N=7 self-defect catches in the N=4-7 band for codification slices — slice-017 matches the slice-013 N=7 high-water mark). However, the first Critic's design.md Audit 4 (EPGD-1 self-application) was NOT scrutinized — Audit 4 received only validation that the discipline holds (0 of N touched), not validation of N itself. The same N=2 entry-pin-doubling pattern that slice-014 introduced at v0.29.0 and slice-016 introduced at v0.31.0 was missed in the design.md prose. This is exactly the design-doc-level mechanical-table-vs-canonical-inventory asymmetry per CCC-1 v1.1 sub-clause 2 surface — i.e., slice-016 M-add-1 watch-list class (Wiegers regression-guard coverage symmetry omission at design-doc-level mechanical inventories). At N=1 (slice-016) this was a watch-list candidate; **at slice-017 m-add-1 if user accepts at TRI-1, this ratchets to N=2** which is the typical promotion threshold for /critic-calibrate Step 5 aggregation.

DR-1 catch-class diversification stability post-slice-017: prior 3 DR-1 catches were RPCD-1 sub-mode (a/b/c) instances at slices 013/014/015 (N=3 baseline); slice-016 M-add-1 was Wiegers coverage symmetry at design-doc-level mechanical-table-vs-canonical-inventory; **slice-017 m-add-1 is the SAME Wiegers coverage symmetry class at design-doc-level mechanical-table-vs-canonical-inventory (Audit 4 EPGD-1-self-application inventory count) — N=2 in the watch-list class**, ratchets the class toward eligibility for a future Dim 9 sub-clause refinement at N=3 if recurs at slice-018+.

**Per TPHD-1 sub-mode (a) self-application empirical demonstration**: this /critique-review fix block IS the canonical reference instance #1 of TPHD-1 sub-mode (b) — when meta-Critic m-add-1 ACCEPTED-FIXED applied count correction across 6 sites in same fix block, the mission-brief TF-1 plan rows did NOT need harmonization because the count drift didn't change test function names. Sub-mode (b)'s discipline "harmonize TF-1 plan IF fix-prose changes function names" was correctly applied — confirmed N/A for this finding.

Reservation: m-add-1 is genuinely close to the m-class severity threshold (could be argued as a "documentation-record drift on a vacuously satisfied audit" — the EPGD-1 guarantee 0/12 holds at correct N). Builder should verify the count at /build-slice Phase 1b pre-Edit and if 12 is empirically confirmed, harmonize design.md L204 + L208 + mission-brief.md L66 in the same fix block per **TPHD-1 sub-mode (a) self-application** — the discipline this slice codifies catches exactly this class of count-drift on the slice's own draft.
