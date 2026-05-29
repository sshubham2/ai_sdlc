---
slice: slice-080-harden-bc1-critical-rules-exit-gate
stage: code-review
updated: 2026-05-29
next-action: run /validate-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-080 harden-bc1-critical-rules-exit-gate

**Stage**: code-review
**Next action**: run `/validate-slice`
**Updated**: 2026-05-29
**Risk tier**: medium — Critic required: yes (touches `tools/build_checks_audit.py` + `skills/build-slice/SKILL.md` — in-house methodology surfaces, always-mandatory Critic trigger)

## Progress

- [x] /repro — 2026-05-29 (BFRD-1 prelude: `tests/bugs/test_bc1_critical_rule_exit_gate.py` FAILING as expected; shippability row #85)
- [x] /slice — 2026-05-29
- [x] /design-slice — 2026-05-29
- [x] /critique — 2026-05-29 — NEEDS-FIXES (first-Critic 3B/3M/2m all VALID + meta-Critic EXTEND: 0 suspicious, 1 missed Minor; dual-review verdict EXTEND; user-ratified TRI-1)
- [x] /build-slice — 2026-05-29 — SHIPPED (1136 pytest PASS; 14 Step-6 audits clean; BC-1 self-dogfood --strict --ack-critical BC-PROJ-3 BC-GLOBAL-2 exit 0)
- [x] /code-review — 2026-05-29 — FINDINGS (0B/1M/2m; M1+m1 fixed in-band, m2 deferred-cosmetic)
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Build complete in worktree `ai_sdlc-wt/slice-080-...`. BCSG-1 shipped: `--strict` + `--ack-critical` make unacknowledged applicable Critical rules into violations → exit 1; default-off byte-unchanged. All 6 ACCEPTED-PENDING critique items built (B2 test rename+propagation+BC-PROJ-10 pair; B3 Step 6 wiring+ack+attestation; M2 diagnostic; M3 append-placement+global-source test; m1 example ordering; m2 docstring). v0.75.0 5-leg PMI-1 bump + MCFS-1/AVFS-1/TVFS-1/OSDG-1 forward-syncs. Full suite 1136 PASS.

## On resume

- **Last completed action**: /build-slice (BCSG-1 implemented; pre-finish gate fully passed; build-log SHIPPED)
- **Current work**: none
- **Next immediate step**: run `/code-review` (in-loop adversarial code-Critic on the slice diff)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — SHIPPED
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
