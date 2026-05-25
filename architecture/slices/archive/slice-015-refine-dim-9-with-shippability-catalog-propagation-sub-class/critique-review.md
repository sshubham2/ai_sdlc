# Critique Review: Slice 015 refine-dim-9-with-shippability-catalog-propagation-sub-class

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-13
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's six findings (B1 / M1 / M2 / M3 / m1 / m2) are all VALID with appropriate severities — every claim was independently verifiable against the actual artifacts (empirical anchor counts in canonical body, test source line numbers, shippability.md row 13 dual-reference, slice-013 cross-references). However, the M1 disposition (introduce `WRITTEN-AS-EDIT` rows + grow TF-1 plan 10 → 13) creates a NEW Blocker the first Critic did not anticipate: `WRITTEN-AS-EDIT` is not in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist, so `--strict-pre-finish` will fail with 11 violations at /build-slice Step 6. This is the symmetric-runtime-prerequisite-completeness blind spot the meta-Critic flagged at slice-014 (M-add-1 `import pytest`/`import ast` missing) — N=3 stable pattern across consecutive cross-cutting tooling slices: "first Critic catches the design-semantic issue at the canonical body but misses the runtime-prerequisite at the canonical body's surrounding context."

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1: Substantive-discipline anchor list (≥2 of 4) literal-substring drift** — VALID; severity Blocker is appropriate. Empirically verified post-disposition revision: of `["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]`, the canonical body section in `design.md` L122-126 shows counts 2 / 7 / 3 / 12 respectively (all ≥1, robust to multi-occurrence drift). The original tuple `["Phase 5", "shippability catalog", "consumer reference", "rename propagation"]` would have yielded 2 / 0 / 0 / 0 (3 of 4 absent), causing the AC #2 `_cites_at_least_two_cross_slice_anchors` test to FAIL at /build-slice Phase 1f with `sub_count == 1 < 2`. Wiegers' SRS-completeness: the assertion tuple must match the literal canonical body it pins. The disposition's revised tuple is sound.

- **M1: Slice-013's 3 body-bound tests precision-degrade after 8th sub-clause inserted between L172-L180** — VALID; severity Major is appropriate. Empirical: grep on `tests/methodology/test_critique_agent.py` for `end_anchor = "### Bonus: weak graph edges"` returns exactly 5 hits — L168 (slice-011 location-pin), L299 (slice-013 location-pin), L331 / L364 / L413 (slice-013 body-bound tests). The 2 LOCATION-pin tests correctly use the wide bound by design (pin position within Dim 9). The 3 body-bound tests (L331/L364/L413) match the first Critic's named targets exactly — no additional sibling tests missed. This is the symmetric application of the slice-013 M1 + M-add-1 catch (Hendrickson body-bound discipline). The fix (3 end_anchor tightening Edits) is structurally correct, but introduces its own follow-on issue — see M-add-1 below.

- **M2: Mission-brief AC #2 doesn't formalize the strict-both / ≥k-of-n anchor list semantics** — VALID; severity Major is appropriate. Pre-disposition mission-brief.md L18 named "slice-013 + slice-014 anchors" without the strict-both `["slice-013", "slice-014"]` tuple or ≥2-of-4 substantive tuple. Slice-013 critique M2 ACCEPTED-FIXED established this propagation discipline at N=1 stable; slice-015 mission-brief recurrence ratchets it to N=2 stable. Newman: spec must constrain implementer choice deterministically. The disposition's mission-brief.md edit (folded with B1) is correct.

- **M3: Canonical body "SAME Phase" wording empirically falsified by both N=1 + N=2 reference instances** — VALID; severity Major is appropriate. Pre-disposition body said "the SAME Phase explicitly propagates" — empirically false against slice-014 (Phase 1c supersession + Phase 4 propagation; reflection.md L16) and slice-015's own plan (Phase 1f supersession + Phase 5 propagation; design.md L139/L143). Post-disposition body uses "the same /build-slice block (before /validate-slice catalog run)" — empirical grep returns 4 occurrences of "same /build-slice block" and 0 of "SAME Phase" / "same Phase" in canonical body section. Fowler / Dim 1 doc-vs-impl parity — the discipline-prose-vs-empirical-practice drift at the moment of codification was a real CCC-1 v1.1 class defect. Fix is sound.

- **m1: N-surface schema-pin grep verification missing from pre-finish gate** — VALID; severity Minor is appropriate. Cheap explicit `grep -rn "Shippability-catalog consumer-reference propagation"` returning ≥4 hits adds defense-in-depth for the N=3 surface invariant.

- **m2: Phase 5 step (b) row 13 dual-reference clarification** — VALID; severity Minor is appropriate. Row 13 of `architecture/shippability.md` empirically carries BOTH `_invariant` (slice-014) AND `_lists_seven_sub_clauses` (slice-013 lineage) per grep. The clarification preserves `_invariant` while updating only the structural-invariant reference. Cosmetic but accurate.

## Suspicious findings

No suspicious findings. All six first-Critic findings are well-grounded; none reach over-reach territory.

## Missed findings

- **M-add-1: `WRITTEN-AS-EDIT` status string introduced by M1 disposition is not in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist — TF-1 strict-pre-finish will fail at /build-slice Step 6 with 11 violations** — empirically verified by running `<HOME>/.claude/.venv/Scripts/python.exe -m tools.test_first_audit <slice-015-folder> --strict-pre-finish` against the post-disposition mission-brief: returns 11 Important violations:
  - 3 × `kind=invalid-status` on rows 41, 42, 43 (`status 'WRITTEN-AS-EDIT' not in ['PASSING', 'PENDING', 'WRITTEN-FAILING']`)
  - 8 × `kind=non-passing-pre-finish` on rows 38-49 (PENDING rows; expected pre-build)

  **Issue**: `tools/test_first_audit.py` L65 defines `_ALLOWED_STATUSES: frozenset[str] = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})`. The first Critic's M1 disposition introduced `WRITTEN-AS-EDIT` as a new status to represent "this row is an Edit on a pre-existing PASSING test, not a new test transitioning PENDING → WRITTEN-FAILING → PASSING." The intent is reasonable (slice-014 mission-brief tracked similar Edits as separate concerns elsewhere; never in the TF-1 table), but the status string is not implemented in the audit tool. Slice-013's mission-brief never used this status — slice-013 marked existing tests with `PASSING` and noted end_anchor tightening only in must-not-defer prose (verified: `grep WRITTEN-AS-EDIT` returns only slice-015 + slice-015 critique.md). Slice-015 is the FIRST slice introducing `WRITTEN-AS-EDIT`.

  Additionally, mission-brief.md L130 pre-finish gate reads "accepts 10/10 TF-1 rows as PASSING" — but the actual TF-1 plan post-disposition is 13 rows. The hard-coded "10/10" is a stale count from the pre-disposition plan size; the M1 disposition grew the plan but didn't update this line. This compounds the audit-failure mode: even after adopting `PASSING` for the 3 edit rows, the 10/10 vs 13/13 drift indicates the disposition wasn't propagated fully through the pre-finish gate checkboxes.

  **Framework**: Sommerville (build-step completeness — every status string referenced in a methodology artifact must be implemented in the audit tool); Hendrickson (operational invariants — strict-pre-finish gates must accept the statuses the mission-brief is allowed to assert). This is the EXACT pattern slice-014 M-add-1 surfaced (canonical-body imports missing): "the first Critic catches the design-semantic issue at the canonical body but misses the runtime-prerequisite at the canonical body's surrounding context." N=3 stable across consecutive cross-cutting tooling slices.

  **Severity**: Major. Would cause /build-slice Phase 6 pre-finish gate to halt with `tools/test_first_audit.py` exit 1, blocking the slice from completing. Builder would need to either (a) revise `tools/test_first_audit.py` to add `WRITTEN-AS-EDIT` to `_ALLOWED_STATUSES` (cross-cutting methodology-tooling change requiring its own /critique trigger via MCT-1; should be a SEPARATE slice), or (b) flip the 3 rows to `PASSING` (matching the post-tightening end-state, matching slice-013's pattern), or (c) refactor the 3 rows out of the TF-1 table entirely (track end_anchor tightening as must-not-defer items, as slice-013 did). Option (b) is the slice-013 precedent and cheapest fix; option (a) is a methodology-tooling cross-cutting change that conflicts with the slice's ~0.5-day budget and adds CSP-1 / Dim 9 sub-clause 2 doc-vs-impl-parity surface (the audit's `_ALLOWED_STATUSES` constant + the docstring at L9 listing only 3 statuses + the L9 docstring would need updating too). Recommend option (b) at TRI-1 reconciliation: status `PASSING` (matching slice-013's `PASSING` for pre-existing tests), with the end_anchor tightening tracked in must-not-defer as slice-013 did (mission-brief L70-71 already lists it as must-not-defer).

  Additional propagation: pre-finish gate L130 must update from "10/10" to "13/13" (or whatever post-revision count holds).

## Severity adjustments

No severity adjustments. The first Critic's Blocker/Major/Minor assignments are well-calibrated against impact. B1 is genuinely Blocker (silent build-time failure); M1/M2/M3 are genuinely Major (precision-degradation + spec-drift + doc-vs-impl parity); m1/m2 are genuinely Minor (cosmetic + defense-in-depth).

## Notes

Meta-Critic confidence: HIGH on M-add-1 (empirically verified by directly running `tools.test_first_audit` against the post-disposition mission-brief — 11 violations reproduced, exact rows + line numbers captured); HIGH on the six first-Critic disposition confirmations (canonical body anchor counts independently verified; row 13 dual-reference verified by grep on shippability.md; "SAME Phase" → "same /build-slice block" verified by grep on design.md; slice-013 body-bound test count verified by grep).

Calibration observation: this is the **third consecutive cross-cutting tooling slice** (post-slice-013 + slice-014) where the meta-Critic surfaces a runtime-prerequisite-completeness blind spot that the first Critic missed. The pattern is now **N=3 stable**:
- Slice-013 M-add-1: sibling-test completeness (grep across body-bound siblings)
- Slice-014 M-add-1: import-statement completeness (canonical body uses `pytest`/`ast` but module never imports them)
- Slice-015 M-add-1: audit-allowlist completeness (canonical disposition introduces `WRITTEN-AS-EDIT` but `_ALLOWED_STATUSES` never widened)

Each instance has the same shape: the first Critic correctly identifies the design-semantic defect AND a structurally sound fix, but the fix introduces a NEW runtime-prerequisite gap because the surrounding tooling/context wasn't audited symmetrically. This is now a strong candidate for /critic-calibrate aggregation at slice-016+ if it recurs — proposed prompt update to `agents/critique.md` Dim 9: "When proposing a fix that introduces new tokens / status strings / imports / vocabulary, verify the surrounding audit tools / module-scope imports / allowlist constants already accept those new tokens; if not, the fix needs to bundle the tooling/scope-widening change OR file it as a separate slice." The first-Critic instruction to "audit the fix's runtime prerequisites" is currently implicit; making it explicit would close this recurring class. (Per /critic-calibrate trigger discipline: this is N=3 — at the threshold; a fourth recurrence at slice-016 would justify a calibration run.)

Reservation: M-add-1 here is genuinely missed and would cause a hard build-time failure, but the fix is cheap (flip 3 statuses to PASSING per slice-013 precedent + update L130 "10/10" → "13/13"). The first-Critic's instinct to introduce a new status was reasonable design-wise — slice-013's choice of tracking end_anchor tightening only in must-not-defer (not as TF-1 rows) was arguably under-tracking, and the first-Critic's `WRITTEN-AS-EDIT` reflects a more complete bookkeeping. But the audit-tooling reality forces option (b). Builder should verify by running `tools.test_first_audit` empirically at /build-slice Phase 0 before Phase 1f begins — `WRITTEN-AS-EDIT` → `PASSING` is a 30-second edit that retires the entire risk class.
