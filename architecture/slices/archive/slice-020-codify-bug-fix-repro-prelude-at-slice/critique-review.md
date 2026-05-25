# Critique Review: Slice 020 codify-bug-fix-repro-prelude-at-slice

**Reviewed by**: critique-review agent (DR-1 N=7 stable post-slice-019)
**Date**: 2026-05-14
**First-Critic verdict**: CLEAN
**Dual-review verdict**: EXTEND

## Summary

First Critic produced strong findings on B1/B2/B3/M1/M5; coverage of the design's core risks is solid. Two concrete missed findings surface on second-pass review: M-add-1 (ADR-018 L169 Conclusion still says "Magnitude is ~8-10 sites" — the B3 fix did NOT propagate to the Conclusion paragraph; same count-drift class recurring WITHIN the B3 fix block — textbook recursive-self-application demonstration of the Wiegers regression-guard coverage-symmetry watch-list class, advancing N=4 → N=5 cumulative); M-add-2 (design.md Step 3c verification mechanism introduces NEW `bug:` provenance comment convention on shippability.md that has zero precedent in existing 19 rows AND is not codified anywhere in this slice — RPCD-1 sub-mode (b) NEW-status/token allowlist-audit class blind spot on the very rule the Critic codified at slice-016). One severity miscalibration noted on B3 (Blocker → Major). One SUSPICIOUS on M2 OVERRIDDEN rationale (canonical-phrase pinning is aspirational at design time; verification requires explicit test-assertion locking).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (detection mode (a) `fix-*` prefix-only empirically broken): VALID. slice-001 archive directory `slice-001-diagnose-orchestration-fix` empirically demonstrates the `*-fix` suffix shape. Builder's widened regex set covers `fix-*` + `*-fix` + `bugfix-*` + `hotfix-*` + `defect-*` + `repair-*` + `patch-*` + `harden-*-bug`. Archive scan shows no `rollback-*` or `revert-*` precedent in slices 001-019. Severity Blocker appropriate (load-bearing detection rule with empirical project-corpus counter-example).
- **B2** (verification mechanism unspecified): VALID. `shippability.md grep verification` + verbal fallback are now concrete (with sub-issue noted at M-add-2 below regarding the `bug:` provenance branch). Severity Blocker appropriate.
- **M1** (architectural-impossibility → contingent N/A): VALID. The rewording from "architectural impossibility" to "contingent inapplicability" is more honest and survives a hypothetical-future-bug-fix-codification-slice probe. Severity Major appropriate.
- **M4** (mid-slice smoke gate too narrow): VALID. Adding `prelude_present` to the smoke gate fixes a real coverage gap.
- **M5** (helper-generalization rule-of-three): VALID. Slice-019 reflection explicitly says "at N=3 (next codification slice), promote to `_extract_version_body(content, version)`". Slice-020 IS that slice. Builder's Option C choice is consistent with the aggregated lesson. Single-code-path discipline preserved: slice-018's `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body` still exercises the same `_extract_version_body` code path via the `_extract_v031_body` thin wrapper — wrapper-indirection does NOT break regression-test intent.
- **m2** (operational violation-detector): VALID Minor with correct severity.
- **m3** (Audit 8 framing): VALID Minor.
- **m4** (ADR-018 Option 3 rejection rationale): VALID Minor.
- **m5** (PMI-1 counter math): VALID Minor.

## Suspicious findings

First-Critic dispositions the meta-Critic challenges (likely weak rationale):

- **M2 OVERRIDDEN rationale is SUSPICIOUS**. First-Critic OVERRIDDEN rationale was "phrase `bug-fix repro prelude discipline` appears naturally in section opener". This is **aspirational, not verified** — Step 3c body has not yet been written at /critique time; the design.md describes 7-item Step 3c content structure but the prose-pin test `test_slice_skill_md_bfrd_1_prelude_present` doesn't specify which literal it asserts (`BFRD-1` rule ID, or the full canonical phrase, or both). If at /build-slice Phase 1 Claude writes Step 3c with the phrase variant (e.g., "Bug-fix prelude" or "bug-fix-repro-prelude discipline" — note ADR-018 L13 names the rule as "BFRD-1 Bug-Fix-Repro-Discipline" without "prelude" while ADR-018 L85 names canonical phrase `bug-fix repro prelude discipline` for cross-surface pinning), the N=3 schema-pin breaks at the skill-prose surface. **Recommendation**: tighten by specifying that `_prelude_present` test asserts the literal canonical phrase `bug-fix repro prelude discipline` (which then transitively requires Step 3c body to contain it, locking the design.md L93 commitment into the test). The OVERRIDE itself can stand (N=3 convention preserved) but the rationale needs concrete enforcement via the prose-pin test specification.

## Missed findings

Concerns the first Critic didn't flag but surface from independent re-review:

### M-add-1 (Blocker — same class as B3 recurring in fix block)

- **Claim under review**: ADR-018 Conclusion paragraph L169: `**Conclusion**: Reversibility is **cheap**. Magnitude is ~8-10 sites (slimmer class than ADR-014/015/016/017 codification slices because BFRD-1 spans 1 skill file vs 3 for TPHD-1 / '/diagnose' for LAYER-EVID-1). Revert path is well-trodden. Adopt Option 1...`
- **Issue**: B3 was filed precisely on this internal-inconsistency class ("11 enumerated vs ~8-10 declared"). Builder's ACCEPTED-FIXED disposition updated L132 (Magnitude estimate heading) + L153 (Comparison-to-prior-ADRs) but did NOT propagate to L169 (Conclusion paragraph). **The same count-drift class B3 named recurs WITHIN the fix block intended to retire it** — textbook recursive-self-application demonstration AND a strict-recurrence of the Wiegers regression-guard coverage-symmetry watch-list class. Pre-fix N=4 cumulative across slices 016/017/019/020; ADR-018 L169 makes it **N=5 cumulative WITHIN slice-020 itself** (slice-020 first-Critic B3 + slice-020 meta-Critic M-add-1).
- **Evidence**: `architecture/decisions/ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md` L169 (exact string "Magnitude is ~8-10 sites" still present); L132 (Magnitude estimate — UPDATED to ~11); L153 (Comparison-to-prior-ADRs ADR-018 line — UPDATED to ~11).
- **Proposed fix**: Update ADR-018 L169 from "Magnitude is ~8-10 sites" to "Magnitude is ~11 sites" matching L132 + L153.
- **Severity**: Blocker (internal inconsistency in ADR's concluding sentence on the magnitude claim that B3 was filed to retire; this is the SAME class of defect at the SAME slice's own fix-prose layer).
- **Framework**: Wiegers (Requirements traceability / count-consistency).
- **Builder draft**: ACCEPTED-FIXED at ADR-018 L169 (Conclusion paragraph updated to "Magnitude is ~11 sites"; recursive-self-application of B3 class within fix block documented as N=5 cumulative recurrence; **NEW first-Critic-MISS class candidate at N=1**: *fix-block-completeness — when a count-drift Blocker is filed, the Critic must verify the fix propagates to ALL sites in the document, not just the heading section*; promotion-eligible at N≥3 distinct-slice recurrence per /critic-calibrate aggregation).

### M-add-2 (Major — RPCD-1 sub-mode (b) NEW-status/token allowlist-audit class)

- **Claim under review**: design.md§Step 3c content structure item 4: `Claude greps architecture/shippability.md for a row whose 'Critical path' cell contains a 'bug:' provenance comment OR whose 'Command' cell targets 'tests/bugs/*' (the canonical shippability-row signature for /repro-added tests).`
- **Issue**: The verification mechanism depends on TWO grep signatures: (a) `bug:` provenance comment in Critical path cell, OR (b) `Command` cell targeting `tests/bugs/*`. Empirically verified at meta-review time:
  - **Branch (a) `bug:` provenance**: ZERO precedent. `grep -c "bug:" architecture/shippability.md` returns 0. No existing shippability row carries a `bug:` provenance comment. No /repro skill prose update in this slice mandates `bug:` provenance going forward. **The branch is purely aspirational** — when the first BFRD-1 self-application slice (slice-021+) runs the grep verification, the `bug:` provenance branch will match zero rows because /repro doesn't know to emit them.
  - **Branch (b) `tests/bugs/*`**: PARTIAL precedent. `grep -c "tests/bugs/" architecture/shippability.md` returns 0 across existing rows 1-19 (none are bug-fix rows). However, /repro skill prose (`skills/repro/SKILL.md` L87, L94, L114) explicitly documents `tests/bugs/` as the canonical location for /repro-added tests. So Branch (b) WILL match when /repro emits a row, assuming /repro places the test under `tests/bugs/`. But L87 also says "Put the test in a dedicated location: `tests/bugs/` OR project's convention for bug-fix tests" — the "OR" admits non-`tests/bugs/` paths. Branch (b) is workable but not universally complete.
- **Evidence**: `grep -c "bug:" architecture/shippability.md` = 0; `grep -c "tests/bugs/" architecture/shippability.md` = 0; `skills/repro/SKILL.md` L87+L94+L114 documents `tests/bugs/` convention with "or project's convention" caveat at L87.
- **Proposed fix**: Three options:
  - (a) DROP the `bug:` provenance branch entirely. Rely on `tests/bugs/*` Command-cell match as primary signal + verbal-claim-with-path as documented fallback for the "or project's convention" non-`tests/bugs/` case. Cleanest fix; matches /repro skill's actual documented convention.
  - (b) ADD a /repro skill prose update mandating `bug:` provenance comments going forward (2-surface scope; expands ADR-018 magnitude beyond the declared ~11 sites; would itself require recounting).
  - (c) Reframe verification to make "ask user to paste failing-test path + confirm" the PRIMARY mechanism rather than fallback; grep is supplementary.
- **Severity**: Major — discipline ships with an unenforceable verification mechanism on its primary grep branch; the `tests/bugs/*` fallback is workable but the aspirational `bug:` branch creates an N=1 instance of RPCD-1 sub-mode (b) class (NEW-status/token allowlist-audit on a mechanism that depends on non-existent state).
- **Framework**: RPCD-1 (slice-016 9th sub-clause, runtime-prerequisite completeness on proposed fixes) + Newman building-microservices runtime-contract-completeness.
- **Builder draft**: ACCEPTED-FIXED via Option (a) — DROP the `bug:` provenance branch from design.md Step 3c content structure item 4. Verification mechanism becomes: grep for Command cell targeting `tests/bugs/*` (matches /repro skill convention) OR verbal-claim-with-path fallback for "or project's convention" non-`tests/bugs/` case. Canonical phrase `shippability.md grep verification` preserved. Mission-brief AC #1 + #2 wording adjusted to reflect the simplified mechanism (no `bug:` provenance phrase in changelog entry; `tests/bugs/*` path-targeting + verbal-fallback). **RPCD-1 sub-mode (b) self-application N=2 stable post-codification at slice-016 (first canonical reference: slice-016 self-application; second: slice-020 M-add-2 catch + fix).**

### M-add-3 (Minor — cosmetic count-classification drift)

- **Claim under review**: ADR-018 L169 Conclusion: `Magnitude is ~8-10 sites (slimmer class than ADR-014/015/016/017 codification slices...)`.
- **Issue**: "Slimmer class than" implies a categorical difference, but ADR-018 (~11 sites) vs ADR-014/015/016 (~13-15 sites) vs ADR-017 (~12-14 sites) is a 1-4 site numeric difference, not a class difference. Loose phrasing feeds the same count-drift watch-list.
- **Proposed fix**: Replace "slimmer class than" with "slimmer count than" (numeric, not classificatory).
- **Severity**: Minor.
- **Builder draft**: ACCEPTED-FIXED at ADR-018 L169 alongside M-add-1 fix in same propagation pass.

## Severity adjustments

- **B3 SEVERITY-WRONG**: filed as Blocker, recommend **Major**. Rationale: B3 is a documentation count-drift in an ADR Reversibility section — not a load-bearing behavioral spec. Wiegers treats count-consistency as Major-class traceability gap, not Blocker. The Builder's ACCEPTED-FIXED inline disposition is correct treatment, but Blocker severity over-classifies. Note: M-add-1 (the missed Conclusion-paragraph instance) is correctly classified as Blocker because it's a strict-recurrence of B3 within the fix block — i.e., evidence that the B3 class is genuinely systemic in this slice, not because the count itself blocks shipment.
- **Disposition impact**: B3 severity recalibration is informational only; the ACCEPTED-FIXED disposition stands (fix has been applied per Builder's draft). For /reflect calibration tracking: count B3 as Major-level in the slice-020 first-Critic accuracy ledger; meta-Critic flagged severity miscalibration as a class observation.

## Notes

**Calibration observations on first-Critic pattern at slice-020**:

Strong empirical-evidence catches on B1 (slice-001 corpus scan) and B2 (verification primitive). Two systemic blind spots observed in this slice's first-Critic output:

1. **fix-block-completeness blind spot** — when B3 was filed for count-drift, the first Critic verified the fix happened SOMEWHERE in the ADR but did not verify the fix was complete across ALL sites in the ADR. ADR-018 L169 is a textbook missed propagation within the very fix block intended to retire the count-drift class. NEW first-Critic-MISS class candidate at N=1; promote at N≥3 distinct-slice recurrence per /critic-calibrate aggregation.
2. **proposed-mechanism-runtime-prerequisite blind spot** — the first Critic accepted B2's `shippability.md grep verification` as adequately concrete without auditing whether the project corpus actually supports the grep pattern (the `bug:` provenance comment is a unilateral new convention with zero precedent). This is RPCD-1 sub-mode (b) class — the very rule the Critic codified at slice-016 — applied here at slice-020 as recursive-self-application. Strong prior for RPCD-1-class blind spots on the Critic's own fix proposals.

Both class candidates are watchlist material for /critic-calibrate at slice-022+ if they recur at slice-021+ distinct from slice-020.

**Empirical file references** (absolute paths verified at meta-review time):
- `<HOME>\ai_sdlc\architecture\decisions\ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md` L132 (fix applied) + L153 (fix applied) + L169 (fix MISSED — M-add-1 catch)
- `<HOME>\ai_sdlc\architecture\shippability.md` grep `bug:` = 0 matches; grep `tests/bugs/` = 0 matches (M-add-2 evidence)
- `<HOME>\ai_sdlc\skills\repro\SKILL.md` L87 ("tests/bugs/ OR project's convention") + L94 + L114 (`tests/bugs/` documented convention with permissive caveat)
- `<HOME>\ai_sdlc\skills\slice\SKILL.md` L134 (Step 3b anchor) + L142 (Step 4 anchor) — Step 3c insertion location confirmed unambiguous
- `<HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py` existing `_extract_v031_body` + `_extract_v033_body` helpers — M5 generalization to `_extract_version_body(content, version)` consistent with slice-018+slice-019 single-code-path preservation
- `<HOME>\ai_sdlc\architecture\slices\archive\slice-019-harden-diagnose-layering-evidence\reflection.md` rule-of-three N=3 promotion lesson confirmed via /slices/_index.md row 19

**Dual-review verdict**: **EXTEND** — 2 missed findings (M-add-1 Blocker, M-add-2 Major), 1 missed minor (M-add-3), 1 severity adjustment (B3 Major-not-Blocker), 1 suspicious rationale (M2 OVERRIDE needs concrete enforcement via test-assertion locking).
