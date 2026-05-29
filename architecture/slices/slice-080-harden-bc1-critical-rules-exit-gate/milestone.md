---
slice: slice-080-harden-bc1-critical-rules-exit-gate
stage: critique
updated: 2026-05-29
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-080 harden-bc1-critical-rules-exit-gate

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-29
**Risk tier**: medium — Critic required: yes (touches `tools/build_checks_audit.py` + `skills/build-slice/SKILL.md` — in-house methodology surfaces, always-mandatory Critic trigger)

## Progress

- [x] /repro — 2026-05-29 (BFRD-1 prelude: `tests/bugs/test_bc1_critical_rule_exit_gate.py` FAILING as expected; shippability row #85)
- [x] /slice — 2026-05-29
- [x] /design-slice — 2026-05-29
- [x] /critique — 2026-05-29 — NEEDS-FIXES (first-Critic 3B/3M/2m all VALID + meta-Critic EXTEND: 0 suspicious, 1 missed Minor; dual-review verdict EXTEND; user-ratified TRI-1)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic review complete; TRI-1 ratified NEEDS-FIXES. Pre-build fixes applied: B1 (5-leg PMI-1 enumeration in design.md + ADR-072), M1 (shippability row #85 rewritten to acknowledgment contract), m-add-1 (repro docstrings). Six items fold into /build-slice: B2 (version-sync test rename + shippability propagation + BC-PROJ-10 pair), B3 (Step 6 ack list BC-PROJ-3+BC-GLOBAL-2 + enumerate-then-ack pattern + build-log attestation), M2 (_format_human ack diagnostic), M3 (append after both loops + global-source test), m1 (Step 6 example ordering), m2 (docstring comments). Plus the full BCSG-1 implementation + v0.75.0 5-leg PMI-1 bump.

## On resume

- **Last completed action**: /critique + /critique-review (critique.md + critique-review.md written; TRI-1 ratified NEEDS-FIXES; both audits clean)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (implement BCSG-1 + apply the 6 ACCEPTED-PENDING fixes)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
