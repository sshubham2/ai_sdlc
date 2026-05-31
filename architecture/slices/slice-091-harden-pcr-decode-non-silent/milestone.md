---
slice: slice-091-harden-pcr-decode-non-silent
stage: critique
updated: 2026-05-31
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-091 harden-pcr-decode-non-silent

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-31
**Risk tier**: medium — Critic required: yes (touches `tools/*.py` — in-house methodology surface, always-mandatory Critic trigger)

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-05-31
- [x] /critique — 2026-05-31 — NEEDS-FIXES (dual-review ADJUST; 1 Blocker FIXED, 3 Major [1 FIXED/1 PENDING/1 OVERRIDDEN], 4 Minor)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic complete, NEEDS-FIXES, user-ratified. Blocker B1 (repro staging dead on Windows git.exe) FIXED in-round — repro rewritten to a real rebase conflict + fixture-guard, verified failing for the right reason. M2 OVERRIDDEN (no JSON round-trip path; meta-Critic confirmed). Pending build fixes: **M1** (add shippability #100 for the decode-fail-closed guard) + **m1** (invert `_git_show_stage` docstring contract). design.md carries the full fix spec incl. m-add-1 (constructor-time set of `claim_extraction_degraded` — frozen+slots) and m-add-2 (catch wraps both stage-2 & stage-3 reads).

## On resume

- **Last completed action**: /critique + /critique-review (NEEDS-FIXES, TRI-1 ratified by user)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (in a real BRANCH-2 worktree — no WORKTREE=skip per slice-090 directive); apply ACCEPTED-PENDING M1 + m1 during build
- **Pending build items**: M1 (shippability #100), m1 (docstring inversion), plus the core fix + AC2/AC3 test `tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (user-triaged)
- [critique-review.md](critique-review.md) — ADJUST (dual-review clean)
- [build-log.md](build-log.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
