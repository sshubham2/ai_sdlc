# Critique Review: Slice 036 fix-rr1-audit-status-filter

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-17
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's six findings are all VALID with correct severities, and the Builder's applied fixes are internally coherent (no stale "live corruption" claim survives; the CSP-1 strike is complete). However, the B2 replacement parity mechanism over-claims: it cited `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` as a parity-enforcement leg, but those tests do not pin the load-bearing skill prose the design's "code-conformance-to-doc" argument depends on. One missed finding (M-add-1) is added.

## Confirmed findings

- **B1** (Intent "corrupts risk-driven slice selection" contradicts authoritative R-9) — confirmed; Blocker appropriate. Verified vs `risk-register.md` L170 ("Current consumers are unaffected … read the per-risk status/band fields") and L172 ("low — no current correctness impact"). Reframe complete across mission-brief Intent, design.md header blockquote, ADR-036 Context; no stale corruption claim remains; reflection.md guard correctly carried.
- **B2** (CSP-1 mis-cited as parity mechanism) — confirmed; Blocker appropriate. Verified vs `tools/cross_spec_parity_audit.py` L1-17 (Heavy-mode-only, "returns clean (no-op)" in Standard). Strike complete across mission-brief, design.md, ADR-036.
- **M1** (no-flag ordering change not regression-pinned) — confirmed; Major appropriate. `filter_and_sort` default `sort_by="score"`; pin via `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id` correct.
- **M2** (band/top under-covered; real-register test fragile) — confirmed; Major appropriate. Fixture stable-oracle + real-register invariant-only split follows slice-004 precedent.
- **m1** (stale line numbers) — confirmed; symbol-anchoring correct.
- **m2** (AC#3 no-regression command unnamed) — confirmed; now explicit.

## Suspicious findings

None. All six first-Critic findings corroborated by the real files. Independent re-verifications check out: repro genuineness (asserts `out["risks"]`, `rc==0` separate, fails pre-fix via `clean_register.md` R3 retired leak — VALIDATED); summary register-wide invariant (`to_dict()` L119-137 over `self.risks`, unchanged — VALIDATED); view-removal safety (grep across all repo `.md` returned zero `view`/consumer matches — VALIDATED).

## Missed findings

- **M-add-1: B2's replacement parity mechanism over-claims — the cited prose-pin tests do not pin the load-bearing prose** — Major. The design's central B2 argument is "skills already document `--json --filter-status open --sort score [--top N]` + 'Retired/accepted excluded automatically' / 'scored, sorted output' prose → no skill-prose edit required (code-conformance-to-doc fix)." That argument's soundness depends on the skill prose being the pinned spec the code conforms to. `test_slice_skill_references_rr_1` (`test_risk_register_audit.py` L356-367) and `test_pulse_skill_references_rr_1` (L370-381) assert ONLY `"RR-1" in text` + `"risk_register_audit" in text` — NOT the invocation flags nor the "excluded automatically" / "scored, sorted" prose. mission-brief AC4 / Must-not-defer / ADR-036 listed these tests as a parity-enforcement leg they do not provide — false comfort (Newman: a contract claim must name a check that fails when the contract drifts; Wiegers: verification must trace to the asserted invariant). A future SKILL.md edit removing "excluded automatically" or changing flags would silently un-spec the code and no cited test would fail. **Proposed fix (Builder, via TRI-1)**: (a, preferred) extend AC4 with a test asserting both SKILL.md contain `--filter-status open` AND the exclusion/sorted prose (genuine prose-pin); OR (b) downgrade the claim to "those tests pin only RR-1/module ref; flag+prose parity by manual re-read only". Option (a) preferred — manual re-read is not a durable guard for the contract this slice's whole thesis rests on.

## Severity adjustments

None. B1/B2 are genuine artifact-self-contradiction / mechanism-category-error Blockers; M1/M2 regression-class Majors; m1/m2 cosmetic/clarity Minors. M-add-1 filed Major (weakens the slice's durability thesis but does not break the code fix's correctness or repro genuineness).

## Notes

Confidence: high. All claims verified vs real `tools/risk_register_audit.py`, `risk-register.md` R-9, `cross_spec_parity_audit.py`, both SKILL.md, `test_risk_register_audit.py` (repro L227-264 + prose-pin tests L356-381). First-Critic per-slice calibration is good: zero false positives, correct severity throughout. The one blind spot is recursive — the first Critic verified B2's mis-citation was struck but did not verify B2's *replacement* mechanism enforces what it claims. Calibration signal for `agents/critique.md`: when a finding is ACCEPTED-FIXED by substituting mechanism A for mis-cited mechanism B, the Critic must verify A enforces the invariant (read the cited tests' assertion bodies), not merely that A exists and is named. EXTEND (not ACCEPT/ADJUST) is correct: M-add-1 does not block code correctness but weakens the durability claim that is this methodology slice's reason for existing.
