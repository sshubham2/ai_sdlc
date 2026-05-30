---
slice: slice-085-harden-pcr-1-truncated-baseline
stage: critique
updated: 2026-05-30
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-085 harden-pcr-1-truncated-baseline

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-30
**Risk tier**: medium — Critic required: yes (touches `tools/parallel_conflict_resolver.py`, an in-house methodology surface — mandatory trigger)

## Progress

- [x] /slice — 2026-05-30
- [x] /design-slice — 2026-05-30
- [x] /critique — 2026-05-30 — NEEDS-FIXES (dual-review EXTEND; 0 blockers, 3 majors, 5 minors; all triaged)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic complete (first Critic NEEDS-FIXES + meta-Critic EXTEND), TRI-1 ratified. **Two user decisions ratified**: m1 → **Option 4** (claim-loss-discriminated, **orphan-gated**: claimed candidate dropped from a tail-truncation-shaped baseline → STOP; orphan-on-well-formed → WARN; no-provable-claim-drop → auto-merge); M1 → **(a) document as residual** (the claim-only-on-a-truncated-branch case is invisible to merged_claims; carried as a named R-24 residual, NOT closed — doubly-rare at low/low; the meta-Critic's per-claim (b) mechanism was also flawed). Design ([[ADR-077]]) reconciled to Option-4-orphan-gated. R-24 → **narrowed** (orphan-branch claim-loss-on-truncation detected; residuals: clean-block-boundary cut + M1 invisible-claim + VAULT_CLAIM sibling). MEPD-1 = EXCLUDE per slice-082/084 precedent. Build must apply the ACCEPTED-PENDING items: M3 render-from-constant + parity pin, m3 APED-1 battery (empty/CRLF). M1 is DEFERRED (no build work — residual only).

## On resume

- **Last completed action**: /critique + /critique-review + TRI-1 triage (verdict NEEDS-FIXES; critique.md + critique-review.md written; audits clean)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (apply the 3 ACCEPTED-PENDING fixes; test-first per TF-1)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-077](../../decisions/ADR-077-scope-pcr-1-baseline-integrity-to-claim-loss.md)
- [critique.md](critique.md) — NEEDS-FIXES (0 blockers, 3 majors, 5 minors)
- [critique-review.md](critique-review.md) — dual-review EXTEND (confirmed all, +2 missed minors)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
