---
slice: slice-084-harden-pcr-2a-clock-skew-winner
stage: complete
updated: 2026-05-30
next-action: none (slice complete) — run /commit-slice to generate the audit-grade commit
risk-tier: medium
critic-required: true
---

# Milestone: slice-084 harden-pcr-2a-clock-skew-winner

**Stage**: complete
**Next action**: none (slice complete) — run `/commit-slice` to generate the audit-grade commit
**Updated**: 2026-05-30
**Risk tier**: medium — Critic required: yes (methodology surface: `tools/*.py` + PCR-2a contract change)

## Progress

- [x] /slice — 2026-05-30
- [x] /design-slice — 2026-05-30
- [x] /critique — 2026-05-30 — CLEAN (2 Blockers + 2 Majors + 2 Minors, all ACCEPTED-FIXED)
- [x] /critique-review — 2026-05-30 — EXTEND (all 6 VALID; +2 missed Minors, ACCEPTED-FIXED)
- [x] /build-slice — 2026-05-30 — SHIPPED (full suite 1213 PASS; all Step 6 gates green)
- [x] /code-review — 2026-05-30 — FINDINGS (2 Majors + 3 Minors, all ADDRESSED-IN-SLICE; suite now 1217 PASS)
- [x] /validate-slice — 2026-05-30 — PASS (4/4 ACs; VAL-1 clean; SRSC-1 89/89; full suite 1217)
- [x] /reflect — 2026-05-30 — vault updated (R-23 narrowed); BC-GLOBAL-4 promoted; lessons captured

## Current focus

Slice shipped. Lessons captured. Auto-archiving next. R-23 narrowed (future-dated sub-case caught;
staler-but-past residual stays open). BC-GLOBAL-4 promoted (ISO-8601 parse traps) — fixture + live +
BCI-1 PASS. Run `/commit-slice` to generate the audit-grade commit + merge the worktree.

## Reflect outputs
- reflection.md written; lessons-learned.md appended (self-validating-slice N=5; "Critic's-own-fix" + regex-APED-1 fused)
- risk-register.md R-23 narrowed (Status stays open/downgraded; fix-candidate #1 marked REJECTED)
- BC-GLOBAL-4 promoted to `~/.claude/build-checks.md` + canonical fixture; BCI-1 PASS; build-checks tests 55 PASS
- shippability row 90 (added at build); SRSC-1 89/89

## Resolved design question

The independent signal = **the resolver's own wall-clock at merge time**, NOT git
commit dates (same skewed clock → no signal) and NOT a Claim-seq counter
(per-machine, not cross-machine comparable — rejected at /slice). A claim is made
before it is merged, so a future-dated winner is physically impossible from a
synced clock → unambiguous skew evidence. Load-bearing tunable: `_CLOCK_SKEW_
TOLERANCE_SECONDS = 300` — flagged for /critique scrutiny (AC-3 over-trigger vs
under-detect tradeoff).

## On resume

- **Last completed action**: /validate-slice (PASS — 4/4 ACs; SRSC-1 89/89; full suite 1217)
- **Current work**: none — build changes uncommitted in worktree (committed at /commit-slice)
- **Next immediate step**: run `/reflect` (capture learnings; downgrade R-23 + register residual)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-076](../../decisions/ADR-076-pcr-2a-clock-skew-guard-resolver-now.md)
- [critique.md](critique.md) — CLEAN (user-ratified)
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — SHIPPED
- [code-review.md](code-review.md) — FINDINGS (all ADDRESSED-IN-SLICE)
- [validation.md](validation.md) — PASS
- [reflection.md](reflection.md) — pending
