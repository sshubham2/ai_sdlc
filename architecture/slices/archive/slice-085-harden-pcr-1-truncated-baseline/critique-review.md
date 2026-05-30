# Critique Review: Slice 085 harden-pcr-1-truncated-baseline

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-30
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is strong: M1's "no-STOP" trace is verifiably correct against the code, M2 and M3 are accurate, and all six findings have appropriate severity. The meta-Critic adds two missed findings (one minor parallel exposure in the VAULT_CLAIM sibling path; one minor MEPD-1/PMI-1 discharge-tracking gap) and defends the "no blockers" verdict the prompt asked it to challenge. The first Critic was neither lenient nor aggressive — calibration is sound. (It also caught that the main-thread placeholder's "B2" was backwards.)

## Confirmed findings (VALID + correct severity)

- **M1** (orphan-branch leaves a claim-loss path uncovered) — confirmed; Major correct. Trace verified end-to-end: `merged_claims` (`:1744`) ← `_extract_claim_diff` ← per-stage `parse_queue_text` (`slice_queue_claim.py:835/844`); a claim cut from text_3 and never in text_2 is absent from `claims_3`, absent from `claimed_names` (`:1756`) → enters neither the `:1775` `& baseline_headings` STOP loop nor the `:1790` orphan branch. The surviving block keeps all 5 PSQ-1 labels (claim lines render AFTER `Risk-retired`, `slice_queue_writer.py:646-648`) → not "truncation-shaped". **No STOP — trace is exactly as M1 states; harm is real, not overstated.**
- **M2** (harm model omits the git commit) — confirmed; Major correct. AUTO_MERGE writes (`:392`) then `git add` + `git rebase --continue` (`:397-408`) with no intervening guard; "self-heals only at next /slice" is eventually-consistent, not nil-harm. Builder's ACCEPTED-FIXED correction is accurate.
- **M3** (`_RENDERED_FIELD_LABELS` SSoT-in-name-only unless `_format_entry` renders from it) — confirmed; Major correct. `_format_entry` (`slice_queue_writer.py:622-639`) hard-codes the labels; `slice_queue_claim.py:107-109` independently defines prefix constants. Fix triple (render-from-constant + parity pin + note existing prefixes) is the right closure.
- **m1** (Hybrid vs Option 4 — ratify) — confirmed; Minor correct. ADR-077 §Decision correctly PROVISIONAL; SOAD-1/TRI-1 ratification is right.
- **m2** (O(blocks×labels) bound) — confirmed; Minor correct.
- **m3** (APED-1 battery: empty baseline, CRLF, trailing-space heading) — confirmed; Minor correct. `parse_queue_text` normalizes CRLF (`:240`) + short-circuits empty (`:236-237`); the new helper must mirror both or it false-STOPs a legitimate empty/`_(no candidates)_` queue.

## Suspicious findings

None. Every first-Critic finding survives a code-level re-trace. The prompt's hypothesis that M1 might be unreachable (because `git show :N:` returns a complete blob) does NOT hold: a "truncated" stage requires a genuinely-committed corrupt queue — the **identical** precondition R-24 assigns to the variant the slice DOES catch. M1's variant is no less reachable than the slice's own target.

## Missed findings

- **m-add-1 (Minor): the VAULT_CLAIM sibling path (`resolve_vault_claim_conflict`) carries the same baseline-truncation claim-loss exposure; the slice's reframing should name it as a parallel residual.** `resolve_vault_claim_conflict` takes `baseline_text` verbatim (`:1323`), overlays only the *winner's* claim, and its post-overlay regex (`:1351-1365`) STOPs only when the *winner's* claim fails to land — it never integrity-checks the baseline and never runs `_verify_soft_equivalence` (that runs only on the SOFT path, `:374`). A truncated baseline in the VAULT_CLAIM path dropping a *third* claimed candidate's lines is committed silently. Correctly OUT of scope for this slice's fix, BUT the design asserts a general principle ("the only non-self-healing harm is claim-loss → must STOP") that the VAULT_CLAIM path visibly does not honor. **Proposed fix**: one sentence in ADR-077 §Consequences / R-24 residual list naming the VAULT_CLAIM parallel exposure as a sibling residual deferred to future PCR-2a hardening — so the principle and its scope boundary are stated together, not silently asymmetric. Minor (out-of-scope-by-design; documentation-completeness).
- **m-add-2 (Minor): MEPD-1 changelog/PMI-1 obligation is flagged in ADR-077 but has no discharge tracking in the pre-finish gate.** ADR-077 identifies the behavior change but the pre-finish gate (mission-brief) enumerates drift-check/TF-1/R-24-narrowed, NOT a MEPD-1 changelog entry or version/PMI-1 determination. A behavior change could land without the changelog entry and still pass the checklist. **Proposed fix**: add an explicit pre-finish row recording the MEPD-1 determination. **Meta-Critic flagged uncertainty**: an in-place logic edit to an already-manifested tool may owe only the changelog half (or nothing, per the slice-082/084 risk-fix EXCLUDE precedent), NOT a manifest bump — the Builder must resolve whether PMI-1 even fires rather than asserting both halves are owed.

## Severity adjustments

None. M1/M2/M3 correctly Major (addressable within the architecture → not Blocker; concrete impact path → not Minor). On the prompt's challenge — *is "no blockers" honest given M1 is an uncovered instance of the slice's OWN target?* — concur: **no Blocker.** M1's variant needs (a) a committed corrupt baseline AND (b) the dropped claim existing *only* on that branch — strictly narrower than the caught variant, under the cooperative model (ADR-067). It is a *narrowing-residual*, not a false claim of closure, PROVIDED the design names it — which it now does (design.md residual (ii); ADR-077). A Blocker would be warranted only if the design asserted the class fully closed while silently leaving M1 open; it does not. Disposition (a) is correctly calibrated; (b) is legitimate but not required.

## Notes

Confidence high: every first-Critic finding re-traced against actual code, not the prompt summary. The first Critic resisted both over-reach (no manufactured Blocker on M1) and under-reach (caught the subtle M1 trace the placeholder got backwards). Both added findings are Minor + documentation/gating-completeness — a thorough first pass leaves thin residue. One reservation: m-add-2's PMI-1 half is flagged *uncertain*, not asserted — an in-place logic edit may owe only the changelog entry (or be EXCLUDE per slice-082/084); the Builder resolves at build.
