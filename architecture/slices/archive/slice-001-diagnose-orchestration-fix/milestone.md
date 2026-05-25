---
slice: slice-001-diagnose-orchestration-fix
stage: complete
updated: 2026-05-09
next-action: none (slice complete)
risk-tier: low
critic-required: false
---

# Milestone: slice-001 diagnose-orchestration-fix

**Stage**: complete
**Next action**: none (slice complete; auto-archived next)
**Updated**: 2026-05-09
**Risk tier**: low

## Progress

- [x] /slice — 2026-05-09 (mission-brief drafted from in-session diagnostic)
- [x] /design-slice — 2026-05-09 (design.md, ADR-001)
- [x] /critique — 2026-05-09 — NEEDS-FIXES (2 blockers + 6 majors + 4 minors; all ACCEPTED-PENDING after user triage)
- [x] /build-slice — 2026-05-09 — SHIPPED (all 12 critique dispositions resolved; pre-finish gates clean; install_audit --strict clean)
- [x] /validate-slice — 2026-05-09 — PASS (6/6 ACs; AC #6 confirmed by end-to-end /diagnose on <private-project>: 4 launched subagents, orchestration handled all 4 outcomes correctly — 3 success + 1 cleanly degraded)
- [x] /reflect — 2026-05-09 — discoveries captured in risk-register.md (R1: cwd-mismatch tool denial), lessons-learned.md, shippability.md (entry #1: diagnose test suite); slice-002 candidates surfaced

## Current focus

Build complete. Net deliverables:
- `skills/diagnose/write_pass.py` (NEW; 188 LOC) — 4-backtick parser, --raw-file only, exit codes 0/1/2
- `skills/diagnose/assemble.py` (MODIFIED) — added `normalize_finding` + `_signature_extractors` + better YAML error
- `skills/diagnose/SKILL.md` (RESTRUCTURED) — Steps 3, 5, 5.5, 6, 6.5 implement subagent-text-in-result + main-thread-writes pattern; 3-attempt retry cap
- 11 pass templates (MODIFIED) — "Output format" section with 4-backtick fences + 5-line schema crib sheet
- `tests/skills/diagnose/` (NEW) — 24 tests across 4 files; all PASSING

Test counts: full repo suite 326/326 PASS. Diagnose suite alone 24/24. TF-1 strict 18 PASSING. INST-1 install audit clean (24/5/4/14, methodology v0.20.0).

ADR-001 (subagent I/O contract) is locked: text-only subagent results, main-thread file writes via write_pass.py. Reversibility: cheap.

## On resume

If session resumes mid-slice, this section tells the next session where to pick up:

- **Last completed action**: /build-slice — SHIPPED. All 12 critique dispositions applied (B1, B2, M1-M6, m1-m4). Pre-finish gates clean. INSTALL.md re-run; install_audit --strict clean.
- **Current work**: none
- **Next immediate step**: `/validate-slice`. Validation needs to run /diagnose end-to-end on a real target codebase to confirm the fenced-block contract holds when actual subagents are spawned (not just in fixture-driven unit tests). Expected: 11 pass output files (sections + findings + summary) + 1 narrator overview = 34 files in `<target>/diagnose-out/`. Smoke target candidate: a small Python project (any small repo with code in it).

## Phase artifacts (sources of truth)

- [mission-brief.md](mission-brief.md) — 5 ACs, 18-test test-first plan (all PASSING), 5 must-not-defer items
- [design.md](design.md) — 1 new module + 1 modified module + 12 modified prose files; updated by Phase 0 with B1/B2/M4/M5 design-stage edits
- [../../decisions/ADR-001-diagnose-subagent-io-contract.md](../../decisions/ADR-001-diagnose-subagent-io-contract.md) — Reversibility: cheap; Consequences widened (M6); Option 4 added
- [critique.md](critique.md) — NEEDS-FIXES; 12 dispositions ACCEPTED-PENDING; triage_audit clean; all dispositions resolved by build
- [build-log.md](build-log.md) — SHIPPED; events log + summary
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## Critic-required determination

Mandatory Critic triggers per `/slice` skill: auth, contracts, data-model, multi-device, external integrations, security.

The slice introduces an *internal* contract (subagent ↔ orchestrator fenced-block format), not a public API. Combined with `risk-tier: low`, Critic was skippable per the methodology. User invoked `/critique` voluntarily as a safety check — and the call paid off (B1 nested-fence collision was a real bug the design glossed over). For future low-tier slices that introduce a non-trivial new internal contract, consider treating that as a soft trigger for voluntary critique even when not mandatory.
