# Critique Review v2 (DELTA-SCOPED): Slice 032 add-query-design-skill

**Reviewed by**: critique-review agent (DR-1) — v2 dual-review, delta-scoped
**Date**: 2026-05-17
**First-Critic verdict (v2)**: NEEDS-FIXES → all ACCEPTED-FIXED
**Dual-review verdict**: EXTEND

## Summary

All three v2 Critic delta findings (M1-v2, M2-v2, m1-v2) VALID, accurately traced to real test source (none fabricated), correctly severed Major/Major/Minor. "4-part bump COMPLETE, no 5th site" sound (matches `methodology-changelog.md:49` verbatim). One missed finding: the applied M1-v2 fix introduced a new unguarded canonical-phrase propagation surface.

## Confirmed findings

- **M1-v2** — confirmed; Major appropriate. `test_v_0_45_0_scmd_1` L2546-2581 verified to assert exactly 4 per-surface things (header L2565 / body-scoped rule-ID L2569-2570 / `_SCMD1_PHRASE` L2574 / two-ADR L2578), looped in-repo+installed L2564. Original 2-assertion correction was a real slice-022 self-violation; fix specifies full 4-assertion list.
- **M2-v2** — confirmed; Major appropriate. `test_v_0_44_0_bci_1` docstring L2516-2517 encodes the "minted audited rule … cannot silently weaken" intent; `test_v_0_43_0` L2623 asserts `"no rule-ID" in body` (actively wrong for minted QD-1). bci_1 correctly the more precise precedent.
- **m1-v2** — confirmed; Minor appropriate. `methodology-changelog.md` L17-31 mandates 4-part per-entry format; scmd_1/bci_1 pin only rule-ID+phrase+ADR. Genuine pre-existing convention gap.

## Suspicious findings

None. All three v2 findings survive independent verification; none over-reach. v2 attack-scope answers (4-part bump complete; corrected m1 Major not Blocker; slice-022 self-violation in correction = YES) all independently confirmed.

## Missed findings

- **M-add-v2-1 (Major): `_QD1_PHRASE` specified as N≥3 verbatim obligation; pin guards only 1 of 3 sites — the new drift surface is itself unguarded (the defect class this slice exists to prevent).** design.md L94 obligated the literal in changelog body + QD-1 rule text + `skills/query-design/SKILL.md`, but the specified test pins only the changelog body (`_extract_version_body`-scoped). The SKILL.md occurrence is categorically uncovered; `test_query_design_skill.py` (AC4) was not specified to assert it. Internal inconsistency: design called it "N≥2 pin" while enumerating 3 sites; precedent `_SCMD1_PHRASE`/`_BCI1_PHRASE` is N=1-pinned. Structurally the same single-site-coverage blind spot as v1 critique M1 / v1 dual-review M-add-1 (INSTALL.md 1-of-3), recurring at N=2 within the same slice on a different artifact (recursive-self-application Dim 9 gap on the corrected delta). **Proposed fix**: (a) add an explicit `test_query_design_skill.py` assertion that `_QD1_PHRASE` appears in `skills/query-design/SKILL.md` (stronger, convention-consistent — makes QD-1's pin strictly better than bci_1/scmd_1); or (b) downgrade the SKILL.md verbatim obligation to non-pinned prose. **Builder draft**: ACCEPTED-FIXED (option a) — design.md "Exact pin shape" item 3 rewritten to exactly 2 test-pinned sites; What's-new bullet adds the `_QD1_PHRASE`-in-SKILL.md assertion to `test_query_design_skill.py`; mission-brief must-not-defer adds the both-sites-pinned item; N≥2-vs-3-sites inconsistency corrected.

## Severity adjustments

None. M1-v2 (Major), M2-v2 (Major), m1-v2 (Minor) all correctly filed. Fix mechanical + bespoke `test_v_0_46_0_qd_1` self-gating → correctly below Blocker. Corrected m1 reversal correctly Major-class, not Blocker.

## Notes

High confidence on the confirmation half — every v2 claim checked against literal test source (`test_methodology_changelog.py` L2502-2627) + format mandate (L17-31); v2 Critic fabricated nothing, severed correctly. M-add-v2-1 is a genuine second-order defect: correcting an under-specified pin introduced a new canonical-phrase propagation surface guarded at only 1 of 3 obligated sites — the same single-site blind spot at N=2 within this slice. The v2 Critic hunted the cited-precedent axis (4-vs-2, bearing-vs-less) correctly but did not re-derive whether the fix's own new obligations are self-guarded. "QD-1 rule text" sub-site is fragile-but-covered (inside `_extract_version_body` scope if authored in the `### Added` block); only the SKILL.md occurrence was categorically unguarded — sufficient to carry the finding.
