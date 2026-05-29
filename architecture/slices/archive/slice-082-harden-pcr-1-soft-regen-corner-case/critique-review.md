# Critique Review: Slice 082 harden-pcr-1-soft-regen-corner-case

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-29
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary
The first Critic's six findings are all VALID with correct severities, and its empirical claims (the `:830-841` claim-drop and `:1242` prelude-drop vectors) reproduce against live source. But a second pass on the *fixed* design surfaces one missed Major: invariant #1's domain (`merged_claims`) provably includes UNCLAIMED candidates, so the invariant as worded false-STOPs the canonical happy path (breaks AC-4). The Builder's M2 disposition (loud-audit-not-STOP) is correct.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (invariant #1 re-parse can't use named field-stripping helpers) — confirmed; Blocker appropriate. Verified empirically: `_regen_slice_queue` returns only `(Path,str)` (:666-727) and `_parse_queue_candidates_for_replacement` (:846-913) strips claim metadata. The accepted fix (re-derive via `_extract_claim_diff`/`_merge_claim_dicts` + local heading regex + `parse_queue_text` for pending presence) is correct — `parse_queue_text` (slice_queue_claim.py:201-303) does return `claimed_by`, and its only documented raise (`ClaimUsageError`) is caught by the design's "re-parse raises → STOP" leg.
- **M1** (invariant #2/#3 miss non-numbered row content-mutation) — confirmed; Major appropriate. Verified: `_parse_shippability_rows` (:1270) keys numbered rows on `^\|\s*(\d+)\s*\|`; `| 5,6 |` / `| 030C |` rows land in prelude, and the same-number HARD escalation (:1232-1239) only fires on numbered rows. The symmetric-invariant-#3 fix closes it, and does NOT false-STOP the canonical happy path (both stages share an identical title/prose/header/separator prelude — branch-invariant).
- **M2** (orphan-exemption can hide truncated-baseline drop) — confirmed; Major appropriate; and the Builder's *rejection of the Critic's literal STOP fix* is correct (see Notes).
- **M3** (atomicity claim relied on unstated placement/ordering fact) — confirmed; Major appropriate. Verified: `_VaultClaimDispatch` (:280-287) and `_SoftResolutionError` (:288-300) handlers both `return` before the post-loop region, the empty-check returns at :302-308, and the write loop starts at :316-320 — so the pinned call-site (after :308, before :316) is read-only and runs only on the all-helpers-succeeded path.
- **m1** (reuse `_SoftResolutionError`, not a new class) — confirmed; Minor appropriate. The catch-order invariant at :371-381 + single `except _SoftResolutionError` at :288 make a new sibling class a real silent-fall-through risk.
- **m2** (audit-log section variant + STOP-path append are new) — confirmed; Minor appropriate. Verified: `_append_audit_log` runs only on APPLIED (:355-362); no SOFT STOP path logs today.

## Suspicious findings

No suspicious findings. Every first-Critic finding survives a closer reading of design.md and the live source. The first Critic did not over-reach.

## Missed findings

- **M-add-1: Invariant #1's domain includes UNCLAIMED candidates → false-STOP on the canonical happy path (breaks AC-4).** `merged_claims` is built by `_merge_claim_dicts` (:730-749), which copies *all* entries from `claims_2`/`claims_3`. Those come from `_extract_claim_diff` → `parse_queue_text` (slice_queue_claim.py:201-303), which returns **ALL** queue entries — claimed AND unclaimed — with `claimed_by` ABSENT for unclaimed ones. Design.md§equivalence-class invariant #1 (L55) read: "every candidate name in `merged_claims` that is ALSO present as a `### <name>` heading in `baseline_text` MUST appear in `pending_claims` **carrying its `claimed_by`**." An unclaimed candidate present in the queue is a `merged_claims` key, IS a `baseline_heading`, and will never carry `claimed_by` in pending (the overlay at :810-821 only inserts claim lines when `claimed_by and claimed_at` are both truthy) → invariant #1 STOPs. Any happy-path queue with even one unclaimed candidate (the normal case — the queue is mostly unclaimed top-10) false-STOPs, violating AC-4 "byte-unchanged when equivalence holds." B1 fixed *how* inputs are derived but not that the derived `merged_claims` over-includes. **Proposed fix**: restrict invariant #1's domain to candidates that carry `claimed_by` in `merged_claims` (i.e. `{name for name,d in merged_claims.items() if d.get("claimed_by")}`), not all keys; pin it with an explicit APED-1 happy-path fixture containing a mix of claimed + unclaimed candidates asserting the guard is transparent.

## Severity adjustments

No severity adjustments. All six first-Critic findings are filed at the correct severity.

## Notes

Confidence is high on M-add-1 — grounded in the live `_merge_claim_dicts`/`parse_queue_text` contract, not speculation, and directly testable at build (the AC-4 happy-path fixture will go RED if invariant #1 is implemented literally over all `merged_claims` keys). On the targeted questions: (1) **M2 disposition is correct** — the Builder did NOT talk itself out of a blocker. Legitimate top-10 churn IS a cross-stage candidate drop and is the dominant case; the Critic's literal STOP-on-cross-stage-drop would false-STOP nearly every SOFT merge. Loud-audit + a named PCR-2b residual is the right line; M2 correctly stays a Major. (2) **Symmetric invariant #3 does NOT introduce a false-STOP regression** — the canonical shippability prelude is branch-invariant; the AC-4 risk lives in invariant #1, not #3. (3) The `_merge_shippability` same-number HARD escalation (:1232-1239) interacts cleanly with invariant #2 — invariant #2 is in fact **tautologically true** on the all-helpers-succeeded path (`merged_rows` is exactly `numbered_2 | numbered_3` by construction at :1244-1245), so it is a harmless future-proofing backstop, not a defect. The MEPD-1 version-bump question was handled correctly: no hard test forces a changelog entry per ADR (MCFS-1 only sync-checks in-repo↔installed), so "check the actual test, don't assume" is the right disposition. Reservation: M-add-1 must be validated empirically at build (APED-1, per the N=3 miss record) before relying on the "happy path byte-unchanged" claim.
