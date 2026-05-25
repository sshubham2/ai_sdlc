# Critique v2 (DELTA-SCOPED re-critique): Slice 032 add-query-design-skill

**Scope**: DEVIATION-1 delta only (m1 reversal + 4-part PMI-1 bump + entry-pin test). v1 `critique.md` (3B/3M/2m + M-add-1, triaged CLEAN) is unchanged and NOT re-litigated.
**Trigger**: user chose "correct design + re-run /critique on the delta" at /build-slice plan-mode design-is-wrong gate.
**Critic reviewed**: design.md DEVIATION-1 sections, mission-brief delta; verified against `test_methodology_changelog.py:2500-2627`, `methodology-changelog.md:17-49`
**Date**: 2026-05-17
**Result**: NEEDS-FIXES → all ACCEPTED-FIXED at this step

## Summary

The m1 reversal is directionally correct (24/24 convention confirmed; slice-029 false-precedent confirmed false — `test_v_0_43_0` exists L2590). But the correction itself committed the slice-022 self-violation it invokes: specified a 2-assertion pin while claiming to "mirror `test_v_0_45_0_scmd_1`" which is a 4-assertion shape. Plus the bearing-vs-less shape distinction was unaddressed. Both fixed.

## Findings

### Majors

#### M1-v2: "mirrors test_v_0_45_0_scmd_1" under-specified the pin by 2 of 4 assertions — slice-022 self-violation in the correction
- **Issue**: `test_v_0_45_0_scmd_1` (L2546-2581) asserts FOUR things per surface (header, body-scoped rule-ID, canonical phrase `_SCMD1_PHRASE`, ADR lineage); the correction specified only header + `QD-1`. The correction invoked "pre-read the enforcing audit's actual assertion" but did not itself fully pre-read scmd_1.
- **Evidence**: `test_methodology_changelog.py:2546-2581`; `:2504-2505` (`_V045`/`_SCMD1_PHRASE` constant pair)
- **Builder draft**: ACCEPTED-FIXED — design.md "Exact pin shape" now specifies the full 4-assertion per-surface list + the `_V046`/`_QD1_PHRASE = "read-only, delegation-only codebase Q&A"` constant pair + `_extract_version_body` body-scoping (sibling-bleed guard) + `ADR-032` lineage assertion; mission-brief must-not-defer updated.

#### M2-v2: wrong/under-justified mirror — QD-1 is rule-ID-bearing; must take bci_1/scmd_1 shape, NOT v0.43.0 rule-ID-less
- **Issue**: Two structurally distinct precedent shapes exist: rule-ID-LESS (`test_v_0_43_0` L2590, asserts `"no rule-ID" in body`) vs rule-ID-BEARING (`bci_1` L2508 / `scmd_1` L2546). QD-1 is a minted rule → must take rule-ID-BEARING; the rule-ID-less shape would be actively wrong. Design didn't address the distinction. `bci_1` is the more precise precedent (anti-silent-weakening intent).
- **Evidence**: `test_methodology_changelog.py:2590-2627` (rule-ID-less); `:2508-2543` (bci_1 anti-weakening docstring)
- **Builder draft**: ACCEPTED-FIXED — design.md "Exact pin shape" explicitly states QD-1 takes the rule-ID-BEARING bci_1/scmd_1 shape and MUST NOT assert any `no rule-ID` prose.

### Minors

#### m1-v2: v0.46.0 entry must be format-conformant (Added + Rule reference + Defect class + Validation) — only Rule reference is generically gated
- **Issue**: `methodology-changelog.md` L17-31 mandates per-entry format; generic gate only checks rule-reference presence; `Defect class`/`Validation` absence ships silently. Pre-existing convention gap (scmd_1/bci_1 also don't assert format-completeness) → Minor.
- **Builder draft**: ACCEPTED-FIXED — mission-brief must-not-defer adds the v0.46.0 format-conformance item.

## Delta attack-scope answers

1. Corrected m1 directionally correct; reversal introduced M1/M2 under-specification (now fixed).
2. **4-part PMI-1 bump COMPLETE** — no 5th lockstep site (matches `methodology-changelog.md:49` v0.45.0 atomic-bump precedent verbatim; plugin.yaml correctly excluded from forward-sync per INST-1 do-not-copy). No finding.
3. No NEW obligation; the existing format mandate → m1-v2 (Minor).
4. Corrected m1 is Major-class, NOT Blocker (the bespoke test IS the gate; verification row 5 already wires it). No new pre-finish gate needed.
5. slice-022 self-violation in the correction: YES → M1-v2 (now fixed).

## Dimensions checked
- [x] Unfounded assumptions — M1-v2, M2-v2 (mirror claim not traced to verified test source)
- [x] Missing edge cases — none in delta (deterministic version-bump; the only edge — installed forward-sync absent — is what the fixed pin guards)
- [x] Over-engineering — none (convergence to 24/24 universal convention)
- [x] Under-engineering — M1-v2 (2-of-4 assertions), m1-v2 (format-completeness ungated)
- [x] Contract gaps — none new (delta is changelog/version-file content only)
- [x] Security — none (no auth/data/injection surface)
- [x] Drift from vault — none (4-part bump matches v0.45.0 precedent verbatim; ADR-032 `supersedes: null` conformant)
- [x] Web-known issues — n/a (internal methodology mechanics, no external surface)
- [x] Cross-cutting conformance — M1-v2/M2-v2 (recursive-self-application Dim 9: slice authoring a forward-sync pin under-specified its own pin vs cited precedent)

## Dual review (v2)

See [critique-review-v2.md](critique-review-v2.md). Verdict: **EXTEND**. All 3 v2 findings VALID (verified against real test source, not fabricated, correctly severed). 0 suspicious, 0 severity adjustments. 1 missed finding:

- **M-add-v2-1** (Major): the M1-v2 fix made `_QD1_PHRASE` an N≥3 verbatim obligation but pinned only the changelog body; SKILL.md occurrence categorically unguarded — silent-prose-drift class recurrence (N=2 of v1 M-add-1). Also corrected the design's "N≥2 pin"-vs-3-sites internal inconsistency. **Builder draft**: ACCEPTED-FIXED — design.md "Exact pin shape" item 3 rewritten to 2 test-pinned sites (changelog `### Added` block via `test_v_0_46_0_qd_1`; SKILL.md via a new explicit `test_query_design_skill.py` assertion); What's-new bullet + mission-brief must-not-defer updated. QD-1's pin is now strictly stronger than bci_1/scmd_1.

## Triage

Reconciled into [critique.md](critique.md)'s Triage table (v2 rows appended). PCA-1 TRI-1 HALT — user ratifies.
