---
slice: slice-084-harden-pcr-2a-clock-skew-winner
stage: critique
updated: 2026-05-30
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-084 harden-pcr-2a-clock-skew-winner

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-30
**Risk tier**: medium — Critic required: yes (methodology surface: `tools/*.py` + PCR-2a contract change)

## Progress

- [x] /slice — 2026-05-30
- [x] /design-slice — 2026-05-30
- [x] /critique — 2026-05-30 — CLEAN (2 Blockers + 2 Majors + 2 Minors, all ACCEPTED-FIXED)
- [x] /critique-review — 2026-05-30 — EXTEND (all 6 VALID; +2 missed Minors, ACCEPTED-FIXED)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual Critic pass complete, verdict CLEAN (user-ratified TRI-1). Design hardened by
8 findings (all ACCEPTED-FIXED): B1 tz-naive→STOP (no TypeError crash) + B2 `Z`→`+00:00`
normalize (3.10-floor-safe) + M1 reframe "narrowed not retired" (R-23 stays open,
staler-but-past residual undetectable) + M2 resolver-now trust assumption documented +
m1 boundary tests + m2 three-site parity + m-add-1 dropped dead `loser` param + m-add-2
pinned audit `now` to `.isoformat()`. Ready to build (test-first, 12 TF rows).

## Resolved design question

The independent signal = **the resolver's own wall-clock at merge time**, NOT git
commit dates (same skewed clock → no signal) and NOT a Claim-seq counter
(per-machine, not cross-machine comparable — rejected at /slice). A claim is made
before it is merged, so a future-dated winner is physically impossible from a
synced clock → unambiguous skew evidence. Load-bearing tunable: `_CLOCK_SKEW_
TOLERANCE_SECONDS = 300` — flagged for /critique scrutiny (AC-3 over-trigger vs
under-detect tradeoff).

## On resume

- **Last completed action**: /critique + /critique-review (CLEAN, user-ratified TRI-1)
- **Current work**: none
- **Next immediate step**: run `/build-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-076](../../decisions/ADR-076-pcr-2a-clock-skew-guard-resolver-now.md)
- [critique.md](critique.md) — CLEAN (user-ratified)
- [critique-review.md](critique-review.md) — EXTEND
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
