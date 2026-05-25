# Critique: Slice 030A repair-build-checks-vault (v3 RE-CRITIQUE)

> **Authoritative current verdict = v3 RE-CRITIQUE (NEEDS-FIXES).** History: v1 BLOCKED + v2 re-critique BLOCKED (`critique-history-v1.md` = restored v1 trail; this file previously held the v2 re-critique, now superseded by v3 — v2 findings B1/B2/B3 closed/folded into the split). User decision 2026-05-16: SPLIT → 030A scope. `critique-review.md` = v2 dual-review (EXTEND).

**Critic reviewed**: mission-brief.md (v3/030A), design.md (v3/030A), ADR-028 (v3), ADR-029 (updated); verified vs live build-checks files, test_build_checks_audit.py, test_methodology_changelog.py, shippability.md rows #5/#8/#12, slice-005/008/028 archives, install_audit.py, test_utf8_stdout_regression.py.
**Date**: 2026-05-16
**Result**: NEEDS-FIXES

## Summary

The split is structurally sound and **030A is independently shippable on this machine** — the Critic traced rows #5/#8/#12 end-to-end: reconstruction-only satisfies them (build-checks functions parse correctly post-reconstruction; the two `test_methodology_changelog.py` functions already pass here). The flaw did NOT relocate into the 030A/030B seam (the Critic specifically attacked that hypothesis and it failed). Propagation file-locations verified correct (meta-M2 resolved). Two blockers + two majors remain — all additive artifact-text / AC-scope corrections, no redesign.

## Findings

### Blockers (must address before /build-slice)

#### B1: ADR-029 still says "rule-ID set" + "(c) shippability catalog row" — v2-B2 contradiction NOT purged; mission-brief L38 falsely attests it was
- **Issue**: ADR-029 Decision/Options text still specifies the rejected rule-ID-set mechanism and a "(c) as a shippability catalog row" wiring — contradicting ADR-029's own "never rule-ID-set-only" line, design.md L77 ("No shippability catalog row for BCI-1 in 030A"), and ADR-029's "three wiring points" cross-ref. mission-brief L38 must-not-defer asserts the contradiction is "closed" across "ADR-029" — a false self-attestation (recursive-self-application class).
- **Builder draft**: **ACCEPTED-FIXED** — edit ADR-029 Decision+Options: "rule-ID set" → "full per-rule structural identity `(rule_id,severity,applies_to,trigger_keywords,trigger_anchors,negative_anchors)` + non-empty check"; "(c) shippability catalog row" → "two wiring points in 030A (non-opt-out /build-slice pre-finish + Step5b post-write); catalog row → 030B"; "three wiring points" → "two (030A); catalog → 030B". Re-verify mission-brief L38 by actual grep post-edit and reword to match real file state.

#### B2: literal oracle has no applies_to/trigger_keywords pins for 3 of 5 rules — full-structural-identity oracle circular for the fields rows #8/#12 depend on
- **Issue**: existing tracked literal constants pin only `trigger_anchors`/`negative_anchors` for BC-PROJ-1/2/BC-GLOBAL-1; NO `applies_to`/`trigger_keywords` literals. BCI-1's full-structural-identity check + rows #8/#12 (which depend on BC-GLOBAL-1 `applies_to == ("**",)` — the slice-005 DEVIATION-1 value, NOT `always:true`) would be validated against a Builder-authored fixture with no independent oracle for those fields → `applies_to` mis-reconstruction passes coincidentally (`_rule_applies` L413-431: `always:true` and glob both route through `not _negative_anchor_match`, so slice-005 still lands in `skipped`).
- **Builder draft**: **ACCEPTED-FIXED with source correction** — accept the finding (extend literal-constant pins to `applies_to`+`trigger_keywords` for ALL 5 rules; add a verification row asserting reconstructed BC-GLOBAL-1 `applies_to == ("**",)`). **Correcting the Critic's source premise**: the Critic calls `architecture/slices/archive/slice-005-.../build-log.md` a "git-tracked verbatim source" — but `git ls-files architecture/` → 0; the entire archive is gitignored, same trust class as the suspect live file (just unlikely to have been hit by R-4's specific last-rule truncation). The **tracked oracle is the test-file literal constant itself** (`tests/` IS git-tracked); the archive build-log/design is best-effort *recovery input* for authoring those constants, NOT itself a tracked oracle. Framing fixed accordingly in design.md M3 table (no false "git-tracked archive" claim); residual (no pre-R-4 byte-tracked oracle for the lost rules' applies_to/keywords) named honestly, same class as M1, accepted because BCI-1 makes any *future* drift loud.

### Majors (address this slice)

#### M1: "lossless — R-4 kept them" asserted not verified; deviation from dual-review's "slice-028 archive" source mandate undocumented
- **Issue**: critique-review.md M-add-3 mandated BC-PROJ-3/BC-GLOBAL-2 pins "from slice-028 archive (non-live origin)"; 030A sources from the surviving live body (the suspect file). The Critic verified the slice-028 archive holds only *prose* (reflection.md L16/L43), not the rule bodies — so 030A's deviation is defensible but undocumented; "lossless" is unfalsifiable (R-4's whole-file regeneration could have subtly altered the survivor).
- **Builder draft**: **ACCEPTED-FIXED** — design.md M3 + ADR-028: acknowledge the deviation + verified reason (slice-028 archive = prose only, insufficient for a structural pin); replace "lossless — R-4 kept them" with "best-recoverable; survived R-4 truncation; cross-corroborated vs slice-028 reflection L16/L43 + shippability.md L43; residual: no byte-level pre-R-4 oracle for these two — accepted, BCI-1 makes future drift loud". Reflection records the residual.

#### M2: mid-slice smoke gate can't catch a same-source circular mis-reconstruction
- **Issue**: smoke gate (`pytest test_build_checks_audit.py` → 0 failed) is satisfiable by a structurally wrong reconstruction if the Builder authored both fixture and literal pin from the same wrong source (B2 coincidental-pass path); BCI-1 is built *after* the smoke gate.
- **Builder draft**: **ACCEPTED-FIXED** — add to the mid-slice smoke gate an explicit cross-check of reconstructed BC-GLOBAL-1 `applies_to == ("**",)` (best-effort source: slice-005 archive build-log; oracle: the new tracked test-file literal constant from B2) authored/verified against a *different* artifact than the fixture body, breaking same-source circularity at the gate.

### Minors
#### m1: stale scope/effort + intent paragraph still describe pre-split v2 scope
- **Builder draft**: ACCEPTED-FIXED — mission-brief L4 → "~0.5–1 day"; L12 intent → 030A scope (drop "hardens the three brittle shippability rows" → 030B qualifier).
#### m2: design.md slice-028 cross-ref doesn't note it lacks the rule body
- **Builder draft**: ACCEPTED-FIXED — annotate "(promotion record corroborates trigger intent + keywords; not the structural body — see M1)".

## Dimensions checked
- [x] Unfounded assumptions — B1, B2, M1
- [x] Missing edge cases — M2; absent/empty-global WARN-vs-HALT verified correct
- [x] Over-engineering — none
- [x] Under-engineering — B2 (incomplete oracle)
- [x] Contract gaps — none new (BCI-1 CLI exit contract fully specified)
- [x] Security — none (methodology tooling, read-only)
- [x] Drift from vault — B1 (ADR-029 internal contradiction), M1 (undocumented deviation from ratified mandate); propagation file-locations VERIFIED CORRECT
- [x] Web-known issues — none (self-contained)
- [x] Cross-cutting conformance — B1 (recursive-self-application design-time), B2 (algorithm-path coincidental-pass), M2 (circular smoke gate); **highest-value check resolved IN 030A's favor — flaw did NOT relocate into the seam**

## Triage

**Triaged by**: user (explicit AskUserQuestion ratification 2026-05-16 — "Ratify all → CLEAN → build"; reconciled with v3 dual-review ADJUST, whose sole adjustment (M1→ADR-028 L29 propagation) was applied before this ratification)
**Date**: 2026-05-16
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | ADR-029 contradiction purged (meta-verified complete, no fresh drift); false self-attestation → build-time grep verification task in must-not-defer |
| B2 | Blocker | ACCEPTED-FIXED | `applies_to`+`trigger_keywords` literal pins extended to all 5 rules; Critic's "git-tracked archive" premise corrected (meta-Critic independently verified `git ls-files architecture/`→0; Builder pushback correct — log for /reflect Critic-calibration as first-Critic factual over-reach, Builder-caught); tracked oracle = test-file literal constant, residual honestly named |
| M1 | Major | ACCEPTED-FIXED | "lossless"→"best-recoverable" honest framing in design.md + mission-brief + **ADR-028 §Decision item 2** (the v3-dual-review ADJUST completion); deviation from M-add-3 documented with verified reason |
| M2 | Major | ACCEPTED-FIXED | Mid-slice smoke gate anti-circularity cross-check (`BC-GLOBAL-1.applies_to == ("**",)` vs a different recovery artifact) |
| m1 | Minor | ACCEPTED-FIXED | Scope/effort + intent rescoped to 030A |
| m2 | Minor | ACCEPTED-FIXED | design.md slice-028 cross-ref annotated (prose-only, not structural body) |
