---
slice: slice-082-harden-pcr-1-soft-regen-corner-case
stage: critique
updated: 2026-05-29
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-082 harden-pcr-1-soft-regen-corner-case

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-29
**Risk tier**: medium — Critic required: yes (touches `tools/**/*.py` in-house methodology surface + the parallel-slice rule family; mandatory regardless of tier)

## Progress

- [x] /slice — 2026-05-29
- [x] /design-slice — 2026-05-29
- [x] /critique — 2026-05-29 — NEEDS-FIXES (1B/3M/2m) + /critique-review EXTEND (+1 missed Major M-add-1); TRI-1 user-ratified (all as drafted)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual review complete. First Critic: NEEDS-FIXES (B1 + M1/M2/M3 + m1/m2). Meta-Critic: EXTEND — confirmed all 6, zero over-reach, +1 missed Major (M-add-1: invariant #1 domain must exclude unclaimed candidates or it false-STOPs the happy path / breaks AC-4). Design edited for B1/M1/M3/m1/M-add-1 (ACCEPTED-FIXED); M2 (loud-audit-not-STOP) + m2 (grep-at-build) are ACCEPTED-PENDING. TRI-1 user-ratified all as drafted (2026-05-29); triage_audit clean; verdict NEEDS-FIXES. Ready for build.

**Carry into /build-slice** (ACCEPTED-PENDING work): (1) M2 — implement loud audit-log warn on cross-stage claim-drop (no STOP); register narrow truncated-baseline R-21 residual → PCR-2b at /reflect. (2) m2 — grep `tests/` for any closed-set assertion over audit section headings before adding the `(equivalence-guard STOP)` variant. (3) M-add-1 — APED-1 happy-path fixture with MIXED claimed+unclaimed candidates asserting the guard is transparent. (4) MEPD-1 — at build, check the actual `test_methodology_changelog.py` assertion to decide whether ADR-074 needs a changelog entry/version bump (don't assume).

## On resume

- **Last completed action**: /critique + /critique-review + TRI-1 user triage (verdict NEEDS-FIXES; both audits clean)
- **Current work**: none
- **Next immediate step**: run `/build-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (TRI-1 pending)
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
