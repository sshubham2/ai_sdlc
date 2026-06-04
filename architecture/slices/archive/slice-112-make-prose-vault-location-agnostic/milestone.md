---
slice: slice-112-make-prose-vault-location-agnostic
stage: complete
updated: 2026-06-04
next-action: none (slice complete — run /commit-slice to integrate)
risk-tier: high
critic-required: true
---

# Milestone: slice-112 make-prose-vault-location-agnostic

**Stage**: critique
**Next action**: run `/build-slice` (NEEDS-FIXES — ACCEPTED-PENDING m2 applied during build; awaiting user build-plan approval)
**Updated**: 2026-06-04
**Risk tier**: high — Critic required: yes (methodology surface; ran + dual-reviewed)

## Progress

- [x] /slice — 2026-06-04
- [x] /design-slice — 2026-06-04
- [x] /critique — 2026-06-04 — NEEDS-FIXES (dual-reviewed; verdict EXTEND; 5B/3M/2m + 2 meta-adds, all reconciled at TRI-1)
- [x] /build-slice — 2026-06-04 — SHIPPED (full suite 1613 pass/2 skip; all Step-6 gates green)
- [x] /code-review — 2026-06-04 — 0 blockers / 1 major / 2 minors (M1 docstring FIXED; m1 claim scoped; m2 deferred-to-follow-on)
- [x] /validate-slice — 2026-06-04 — PASS (5/5 ACs; VAL-1 clean; shippability 117/117)
- [x] /reflect — 2026-06-04

## Current focus

Dual-Critic + TRI-1 complete. **Scope reduced at TRI-1** to a 2-file pilot (`CLAUDE.md` + a self-sufficient `agents/critique.md`); skill conversion (slice/reflect/bulk) + the op-gate re-pin deferred to a follow-on. design.md + ADR-105 + mission-brief reworked (the 9 ACCEPTED-FIXED edits applied); m2 is the lone ACCEPTED-PENDING (exact remainder via `--json` at build). Awaiting user approval of the build plan before `/build-slice`.

## On resume

- **Last completed action**: /critique + /critique-review + TRI-1 triage (verdict NEEDS-FIXES; design reworked)
- **Current work**: none — awaiting user build-plan approval
- **Next immediate step**: run `/build-slice` (on approval)
- **Settled decisions** (user-ratified across /slice + /design-slice + TRI-1):
  1. Framing = location-agnostic prose (flip-neutral), NOT concrete-new-path.
  2. Token = **`<vault>/`** only (`<diagnose-out>` NOT minted — no seam, B5); rule once in CLAUDE.md + embedded self-sufficient in agents (M-add-1); default → `architecture/`.
  3. Governance = **ADR-only / MEPD-1 EXCLUDE**.
  4. **Pilot = `CLAUDE.md` + a self-sufficient `agents/critique.md`** (TRI-1). Skill conversion (slice/reflect/bulk) + op-gate re-pin + skill carve-out instances = follow-on (B1/B2/B3/M1 DEFERRED).
  5. Enforcement = converted-file one-way ratchet folded into `--strict`, **independent of the re-pinnable baseline**, forward-slash-keyed (M3); definitional literals plain-prose `doc-example` (M2/M-add-2); re-pin fan-out = `_BASELINE_SHA256` + `_CLASS_COUNT_FLOOR` + `EXPECTED_TOTAL` + shippability 113/117 (B4), exact total APED-1 at build.
- **Build-time obligations**: APED-1-derive the exact conversion counts + re-pin totals against the real converted corpus; forward-sync agents/critique.md (CAD-1); mid-slice smoke captures the exact remainder (m2).

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (triage table inline)
- [critique-review.md](critique-review.md) — EXTEND (2 missed findings reconciled)
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
