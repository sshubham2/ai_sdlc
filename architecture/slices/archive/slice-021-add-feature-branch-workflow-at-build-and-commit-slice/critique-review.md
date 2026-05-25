# Critique Review: Slice 021 add-feature-branch-workflow-at-build-and-commit-slice (RERUN-2)

**Reviewed by**: critique-review agent (DR-1) — second invocation (on /critique rerun)
**Date**: 2026-05-14
**First-Critic verdict**: CLEAN
**Dual-review verdict**: EXTEND

(Note: this file overwrites the prior /critique-review pass which had EXTEND verdict + 4 missed findings on the FIRST /critique. Git history preserves the prior. This rerun reviews the SECOND /critique.)

## Summary

The rerun /critique's 11 findings are all VALID with correct severities — grep verification against the post-fix artifacts confirms each empirical claim. 7 of the 11 ACCEPTED-FIXED closures landed cleanly (B1-residual 22-site sweep, B2-residual zero-external-consumers retraction, M1-residual item 11 retirement, M2-new canonical-phrase-pin, M3-new "All 20" count, M4-new ADR enumeration cross-reference, m1 typo, m3 "warns on", m2 + m4 by composition). However, **3 of the 11 fix-blocks failed to fully propagate to surfaces named in the rerun /critique's own evidence section** — exactly the empirical pattern the rerun /critique was warning about. The B3-new fix did not propagate to milestone.md L43 (still claims "7 whole-file + 7 `::test_*`"), the M1-residual fix did not propagate to milestone.md L46 ("key redesign decisions" still describes the RETIRED item 11 as load-bearing), and the M1-residual + B3-new N-ratchet landed in ADR-019 L158 but did NOT land in design.md L197/L209 (still N=22 + N=5→N=7 + slice-024+ promotion target). The rerun's grep-before-claiming approach was applied to mission-brief.md + design.md (mostly Files-changed + Limitations sections) + ADR-019, but treated milestone.md as a passive log rather than as a load-bearing claims surface — the same blind spot the prior /critique-review's M-add-3 identified for Must-not-defer in mission-brief.md. The CLEAN verdict was mechanically correct from the triage table, but the post-fix grep verification was incomplete on 2 named surfaces (milestone.md + design.md Cumulative-Critic-influence note section).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1-residual** (22-site vocabulary sweep including ADR title): VALID Blocker. Post-fix grep against ADR-019 returns 2 hits at L38 + L186 — both legitimate quoted meta-references. ADR-019 title at L3 correctly reads "Prerequisite check + /commit-slice --merge". mission-brief.md hits at L16/L19/L78 + design.md hits at L8/L36/L181/L258 all legitimate meta-references. Sweep landed cleanly. ADR title was the highest-cited surface and is now retired-vocabulary-free.
- **B2-residual** ("zero external consumers" retraction): VALID Blocker. Post-fix `grep "zero external consumers"` returns ZERO matches. Replaced with "zero non-repo consumers" at all 4 cited sites.
- **B3-new** (7+7 vs 8+6 + 28 vs 30 TF-1 rows): VALID Blocker. design.md L262-277 Command cell is 8 whole-file + 6 `::test_*` = 14 total. mission-brief.md TF-1 plan rows count = 29 (matches "29 + 1 reserved = 30").
- **M1-residual** (aspirational item 11 retired): VALID Major. Item 11 correctly retired from Pre-finish gate + Limitations item 11 in design.md L225. Watch-list promotion target ELEVATED to slice-022 in ADR-019 L158.
- **M2-new** (default-branch resolution canonical-phrase pin): VALID Major. mission-brief.md L85 carries the new Must-not-defer item.
- **M3-new** ("All 18" → "All 20"): VALID Major. mission-brief.md L164 reads "All 20"; empirical count of `^- \[ \]` items = 20.
- **M4-new** (ADR-019 magnitude enumeration cross-reference): VALID Major. ADR-019 L154 says "See [[design.md#Files changed (estimated count)]] for the full 30-item enumeration".
- **m1** (`devation` → `deviation` typo): VALID Minor. `grep "devation"` returns 0 matches.
- **m2 + m4** (covered by B1-residual sweep): VALID Minor.
- **m3** (BRANCH-1 "catches" → "warns on"): VALID Minor. design.md L184 correctly reads "(BRANCH-1 audit *warns on* this — per /critique-rerun m3 ACCEPTED-FIXED ...)".

## Suspicious findings

No suspicious findings. Every rerun /critique finding holds up to post-fix verification.

## Severity adjustments

No severity adjustments. The rerun's 3 Blockers (B1-residual / B2-residual / B3-new) are each structurally load-bearing.

## Missed findings

Concerns the rerun /critique didn't flag but the meta-Critic surfaces from independent re-review of the post-fix state. Each is the same class — fix-block-completeness recursion within the rerun's own fix-block — at surfaces the rerun's grep scope excluded:

### M-add-1-rerun (Major — B3-new fix did NOT propagate to milestone.md L43; still says "7 whole-file + 7 `::test_*`")

- **Claim under review**: Rerun critique.md L51 enumerated 5 surfaces for the B3-new "7+7" violation including **milestone.md L43**. Triage row claims "harmonized at 5 surfaces".
- **Issue**: Post-fix grep against milestone.md L43 returns: `- **M-add-1 canonical count**: shippability row-21 Command cell enumerates **14 invocation targets** (7 whole-file + 7 ``::test_*``) harmonized across design.md + mission-brief.md Must-not-defer + Command cell.` The OLD wrong count survives at the 5th cited surface. ACCEPTED-FIXED was empirically a 4-of-5 fix.
- **Evidence**: `grep -nE "7\+7|7 whole-file" milestone.md` returns L43 verbatim with the old count.
- **Severity**: Major. Same Wiegers coverage-symmetry class as B3-new applied to milestone surface.
- **Framework**: Wiegers regression-guard coverage-symmetry; rerun /critique's own B3-new framing.
- **Proposed fix**: milestone.md L43: `(7 whole-file + 7 ::test_*)` → `(8 whole-file + 6 ::test_*)`. 1-line edit.

### M-add-2-rerun (Major — M1-residual item-11 retirement did NOT propagate to milestone.md L46)

- **Claim under review**: Rerun critique.md L72 + L162: "Pre-finish-gate item 11 + Limitations item 11 retired as aspirational". M1-residual ACCEPTED-FIXED option (a) closure.
- **Issue**: milestone.md L46 still reads: `- **Design-time fix-block-completeness guard (Wiegers N=7 mitigation)**: NEW Limitations item 11 + Pre-finish-gate item 11 — scan every ACCEPTED-FIXED disposition fix-block for TPHD-1 + count-symmetry before declaring done.` Describes the RETIRED item 11 as a "key redesign decision" with OLD N=7 count.
- **Evidence**: milestone.md L46 verbatim.
- **Severity**: Major. Reader-facing milestone summary contradicts the rerun's M1-residual closure.
- **Framework**: Wiegers claims-to-evidence; Sommerville requirements-to-design traceability.
- **Proposed fix**: Replace milestone.md L46 with: `- **Design-time fix-block-completeness guard RETIRED** (per /critique-rerun M1-residual ACCEPTED-FIXED option (a)): item 11 was aspirational and falsified at the rerun that authored it; watch-list elevated to /critic-calibrate slice-022 (Wiegers N=9 cumulative).`

### M-add-3-rerun (Major — N-ratchet landed in ADR-019 L158 but NOT in design.md L197/L209/L211 Cumulative-Critic-influence section)

- **Claim under review**: Rerun critique.md L143: "Cumulative-Critic-influence note claim N=22 is empirically closer to N=28 cumulative". Rerun M1-residual disposition L162: "empirical N=9 cumulative". ADR-019 L158 correctly says "N=17 → N=28 cumulative HWM" + "Wiegers N=9 cumulative" + "Promotion ELEVATED to slice-022".
- **Issue**: design.md L197 still reads `Recursive-self-application N=17 → **N=22 cumulative** at slice-021 codification`. design.md L209 still reads `Wiegers regression-guard coverage-symmetry watch-list **N=5 → N=7 cumulative** ... promotion-eligible for Dim 9 sub-clause refinement at /critic-calibrate at **slice-024+**`. design.md L211 still says DR-1 promotion target "slice-024+".
- **Evidence**: design.md L197 / L209 / L211 vs ADR-019 L158. 3-site cross-surface drift.
- **Severity**: Major. The Cumulative-Critic-influence note is load-bearing for /reflect's calibration notes + /critic-calibrate slice-022's promotion-input.
- **Framework**: Wiegers regression-guard coverage-symmetry.
- **Proposed fix**: design.md L197 `N=22` → `N=28 cumulative HWM`. design.md L209 `N=5 → N=7 cumulative` → `N=5 → N=9 cumulative` + `at /critic-calibrate at slice-024+` → `at /critic-calibrate at slice-022 (ELEVATED from slice-024+ per /critique-rerun M1-residual ACCEPTED-FIXED)`. L211 same.

### M-add-4-rerun (Minor — design.md L205 "TPHD-1 N=4 → N=5 stable" claim falsified by M-add-1/2/3-rerun)

- **Claim under review**: design.md L205: "TPHD-1 self-application N=4 → N=5 stable: /critique + /design-slice-rerun fix-prose modifying mission-brief AC / design.md TF-1 plan / test function names harmonizes all 3 surfaces in same fix block (this design.md /design-slice rerun IS the canonical reference instance #5 at sub-mode (a))".
- **Issue**: TPHD-1 sub-mode (a) requires harmonization across ALL relevant surfaces in the SAME fix block. The rerun's fix-block produced 3 fresh cross-surface drifts (milestone.md L43, milestone.md L46, design.md L197/L209). The "N=5 stable" claim is empirically falsified.
- **Evidence**: 3 missed findings above; design.md L205 verbatim.
- **Severity**: Minor. Descriptive meta-claim, not load-bearing for downstream gates.
- **Framework**: TPHD-1 sub-mode (a); RSAD-1 at the calibration-meta-claim layer.
- **Proposed fix**: Soften design.md L205 to: "TPHD-1 self-application N=4 → N=5 partial: /critique + /design-slice-rerun + /critique-rerun fix-prose harmonized the 3 named surfaces (mission-brief.md + design.md Files-changed + ADR-019) but milestone.md L43/L46 + design.md L197/L209 carried residual stale counts caught at /critique-review-rerun M-add-1/2/3-rerun (now swept at TRI-1 inline). Honest status: N=5 reached via 2 passes of fix + meta-review, not via a single Builder-self-check. The /critic-calibrate slice-022 sub-clause promotion is the structural closure for the class."

## Notes

High confidence in this meta-review. The rerun /critique's grep-before-claiming approach was an improvement over the prior round — and it shows: 7 of 11 named ACCEPTED-FIXED edits land cleanly. The 4 missed findings cluster around two predictable surfaces the rerun /critique's grep scope did NOT include (milestone.md as a whole + the Cumulative-Critic-influence note section of design.md L186-L211). The rerun /critique scoped grep to mission-brief.md + design.md Files-changed/Limitations + ADR-019, but treated milestone.md as a passive log rather than as a load-bearing claims surface — exactly the same blind-spot class as the prior /critique-review's M-add-3 finding (Phase 0 survival in Must-not-defer block). The empirical pattern continues: every fix-block that asserts "harmonized at N surfaces" without grep verification on every named surface produces ~1 residual instance per fix-block. The rerun /critique's L143 prediction "class is empirically the dominant recurrence class for codification slices" is now empirically validated at +4 (the 4 missed findings of THIS meta-review). The honest closure is: surface the 4 missed findings at TRI-1, apply 1-line fixes each (~5 minutes total), accept that the /critic-calibrate slice-022 promotion target is the right structural framing because the recurrence is provably outside any single Builder-self-check's reach. ACCEPT would be wrong here; EXTEND with 4 missed findings is the calibrated call. M-add-1/2/3-rerun ride on a single combined fix-block at TRI-1; M-add-4-rerun is the meta-claim that they falsify and is itself a 1-line softening.
