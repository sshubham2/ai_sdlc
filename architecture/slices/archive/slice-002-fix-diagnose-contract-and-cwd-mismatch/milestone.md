---
slice: slice-002-fix-diagnose-contract-and-cwd-mismatch
stage: complete
updated: 2026-05-09
next-action: none (slice complete)
risk-tier: low
critic-required: false
---

# Milestone: slice-002 fix-diagnose-contract-and-cwd-mismatch

**Stage**: complete
**Next action**: none (slice complete; auto-archived next)
**Updated**: 2026-05-09
**Risk tier**: low — Critic not required (no mandatory triggers)

## Progress

- [x] /slice — 2026-05-09
- [x] /design-slice — 2026-05-09 (design.md; no new ADRs, no new code modules; pure prose-correction slice)
- [x] /critique — 2026-05-09 — NEEDS-FIXES (voluntary on low-tier; 0 blockers + 4 majors + 4 minors; all ACCEPTED-PENDING after triage). Standout finding M1: Critic surfaced GitHub issue #57037 showing the cwd-mismatch causal claim is hypothesis, not confirmed root cause
- [x] /build-slice — 2026-05-09 — SHIPPED-WITH-DEFERRALS (8 critique fixes applied; 3 BC-1 Important rules deferred-with-rationale; ACs collapsed 5 → 3 mid-build; full test suite 333/333; install_audit --strict clean)
- [x] /validate-slice — 2026-05-09 — PASS (3/3 ACs + deferred manual smoke + shippability catalog 30/30 + WS-1/ETC-1 silent + VAL-1 Layer B 3 deferred-with-rationale per slice-001 precedent)
- [x] /reflect — 2026-05-09 — discoveries captured in lessons-learned.md (recurring VAL-1 Layer B + Critic miss-class accumulating); shippability.md entry #2 added; risk-register R-2 added during build; slice-003 candidates surfaced (val-1-imports-allowlist, fix-rr1-audit-docstring)

## Current focus

Cleanup slice that closes two carryover items from slice-001 + a small bonus:
1. Document the cwd-must-match-TARGET constraint in `/diagnose` SKILL.md Step 1 + emit at-spawn warning when TARGET ≠ $PWD (the cheapest fix path for R1)
2. Relax the over-strict "Do NOT call Write, Bash, or python" wording in SKILL.md Step 5 + 11 pass-template "Output format" sections (closes the design correction noted in archived slice-001/design.md)
3. Convert `architecture/risk-register.md` to the RR-1 audit's expected schema so R1 surfaces in `/slice` ranking

5 ACs, all small in scope. Test-first applies (3 prose-pin tests + 1 negative pin + 2 step-1 pins + 1 risk-register integration test = ~6 new tests).

## On resume

- **Last completed action**: /design-slice — design.md complete (no ADRs, empty wiring matrix, no new code modules — pure prose corrections)
- **Current work**: none
- **Next immediate step**: run `/build-slice`. The build will: (a) write 6 failing tests first per TF-1; (b) edit SKILL.md Step 1 + Step 5; (c) edit 11 pass templates' Output format sections; (d) convert risk-register.md to RR-1 format; (e) verify all gates clean.

## Voluntary Critic note

Critic-required is `false` per methodology (low tier; no auth/contracts/data-model/multi-device/external-integration/security triggers). However, slice-001 ran `/critique` voluntarily on a low-tier slice and the call paid off (12 findings, 2 real blockers caught). For slice-002 the surface is much narrower (text edits + format conversion + 6 test functions; no new modules, no new contracts), so voluntary Critic is lower-yield this time. Recommendation: skip Critic; if anything feels off in build, invoke `/critique --force`.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending (skip per low tier OR invoke voluntarily; user's call at /critique time)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
