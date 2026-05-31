---
slice: slice-088-add-project-frame-synthesizer
stage: complete
updated: 2026-05-31
next-action: none (slice complete) — run /commit-slice to generate the audit-grade commit
risk-tier: medium
critic-required: true
---

# Milestone: slice-088 add-project-frame-synthesizer

**Stage**: critique (NEEDS-FIXES, user-ratified)
**Next action**: run `/build-slice` — design spec is corrected; implement the tool + tests + skill/agent edits per the dual-Critic-hardened design. Register the m2 risk-register entry during build.
**Updated**: 2026-05-31
**Risk tier**: medium — Critic required: yes (methodology surfaces)

## Progress

- [x] /slice — 2026-05-30
- [x] /design-slice — 2026-05-31
- [x] /critique — 2026-05-31 — NEEDS-FIXES (dual-Critic: first 3B/6M/2m all VALID; meta EXTEND +2; 13 findings, 12 ACCEPTED-FIXED + 1 ACCEPTED-PENDING; user-ratified; triage_audit clean)
- [x] /build-slice — 2026-05-31 — SHIPPED (5 phases; cp1252 reconfigure-stdout deviation user-approved; all Step-6 gates green; full suite 1253 passed; mid-slice smoke PASS)
- [x] /code-review — 2026-05-31 — FINDINGS (0B/2M/3m; cp1252 deviation confirmed sound by code-Critic; M1 letter-suffix regex + M2 budget-clamp + m1/m2/m3 ALL fixed in-slice; full suite 1255 passed)
- [x] /validate-slice — 2026-05-31 — PASS (5/5 ACs with evidence; VAL-1 clean; shippability 92/92, 0 regressions)
- [x] /reflect — 2026-05-31 — shipped; learnings captured; R-26 added; lessons-learned appended; auto-archived
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic complete with **zero false positives across both layers**. First Critic: cp1252 stdout crash (B1), wrong cp1252 test bucket (B2), unspecified consumption contract (B3), + 6 Majors + 2 minors. Meta-Critic EXTEND: M-add-1 (em-dash from EXTRACTED source text still crashes — the sharp single-hop miss) + M-add-2 (bespoke-test rollup token + em-dash fixture). All ACCEPTED-FIXED applied to design.md/mission-brief.md except m2 (ACCEPTED-PENDING — register R-7-class silent-degrade risk at build). Design spec is now build-ready.

**Key locked decisions** (carry into build): deterministic tool, ephemeral **stdout-only**, `_ascii_fold()` over the FULL frame before stdout (covers extracted text), `_MAX_FRAME_LINES=40`, synthesis-property test (rule-FAMILY dedup + score-sorted risks + named candidates), 3 NEW OSDG-1 drift tests + OSDG-1 extension folded into PFS-1 v0.78.0 changelog entry, BC-PROJ-9 5-surface fan-out (bespoke cp1252 test, NOT `_ROOT_ONLY_TOOLS`), 5-part PMI-1 bump 0.77.0→0.78.0, ADR-080 (not 079 — slice-087 holds 079).

## On resume

- **Last completed action**: /critique + /critique-review (dual review, NEEDS-FIXES, user-ratified at TRI-1; triage_audit clean).
- **Current work**: none — HALTED at the build-plan presentation boundary (awaiting user go-ahead before /build-slice).
- **Next immediate step**: user approves the build plan → run `/build-slice` in this worktree. TF-1 plan has 13 test rows (4 behavioral incl. synthesis-property + cp1252; 3 structural-pin; 3 OSDG-1 drift; 1 entry-pin; 1 inventory-pin... see mission-brief).
- **Parallel sibling**: slice-087 (PARKED awaiting parallel-safety reframe) — independent.

## Phase artifacts

- [mission-brief.md](mission-brief.md) — corrected (AC#1/#2 reworded; smoke cmd; TF-1 plan expanded)
- [design.md](design.md) — dual-Critic-hardened
- [ADR-080](../../decisions/ADR-080-project-frame-synthesizer-pfs1.md)
- [critique.md](critique.md) — NEEDS-FIXES (dual-Critic + TRI-1 triage table; audit clean)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
