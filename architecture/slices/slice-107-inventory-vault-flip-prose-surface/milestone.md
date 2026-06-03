---
slice: slice-107-inventory-vault-flip-prose-surface
stage: build
updated: 2026-06-03
next-action: run /validate-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-107 inventory-vault-flip-prose-surface

**Stage**: build
**Next action**: run `/validate-slice`
**Updated**: 2026-06-03
**Risk tier**: medium — Critic required: yes (new `tools/*.py` classifier — in-house methodology surface; AP-4)

## Progress

- [x] /slice — 2026-06-03
- [x] /design-slice — 2026-06-03
- [x] /critique — 2026-06-03 — NEEDS-FIXES (dual review: first-Critic BLOCKED + meta-Critic EXTEND; user-triaged)
- [x] /build-slice — 2026-06-03 — SHIPPED (318 enumerated; 15/15 tool tests; full methodology suite 1404 green; 2 deviations logged + harmonized)
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual review complete + user-triaged (TRI-1). **Final verdict: NEEDS-FIXES.** 3 Blockers + 3 Majors + 2 Minors (first Critic) + 2 Majors + 1 Minor (meta-Critic), 11 findings — all ACCEPTED; 2 ACCEPTED-PENDING (B2 ruleset+test, m-add-1 bare-`diagnose-out` grep) carry to build. Design corrected in-round: boundary-free matcher (B1, corrected arithmetic 69/249/318), inline-code→`needs-human` default (B2), all-matches-per-line `re.finditer` + 5-tuple disposition key with column-offset (M-add-1), pre-finish readiness `--strict` (M1), per-class count floor (m2). User ratifications: **Test-first flipped true** (M-add-2, +11-test plan, mirror slice-100/102); **ADR-096/097 reserved for slice-107** (M3 — slice-106 → 098+, noted in `slice-queue.md` on master).

## Build obligations (ACCEPTED-PENDING — must close at /build-slice)

- **B2**: implement the expanded operational verb/sink set; write a test asserting the ~119 verb-ambiguous inline-code paths route to `needs-human` (never silent `doc-example`), proven non-vacuous by mutation.
- **m-add-1**: grep `\bdiagnose-out\b` not-followed-by-`/` across the 5 prose globs; fold operational hits into the residual list or confirm empty (pin `test_bare_vault_dir_arg_residual`).

## On resume

- **Last completed action**: /critique + /critique-review + TRI-1 triage (NEEDS-FIXES, user-ratified)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (Test-first: write the 11 plan tests failing-first, then implement; close the 2 ACCEPTED-PENDING obligations)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (first Critic + Triage)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
