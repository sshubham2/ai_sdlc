---
slice: slice-081-fix-drift-check-enforcement-gap
stage: critique
updated: 2026-05-29
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-081 fix-drift-check-enforcement-gap

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-29
**Risk tier**: medium — Critic required: yes (touches methodology surfaces: `skills/build-slice/SKILL.md`, new `tools/*.py`, new rule DCE-1 + ADR-073)

## Progress

- [x] /repro — 2026-05-29 (failing repro established: `tests/bugs/test_drift_check_enforcement_gap.py`, shippability row 86)
- [x] /slice — 2026-05-29
- [x] /design-slice — 2026-05-29 (DCE-1 procedural gate; ADR-073)
- [x] /critique — 2026-05-29 — NEEDS-FIXES (2 blockers, 3+1 majors, 3+1 minors; user-triaged TRI-1)
- [x] /critique-review — 2026-05-29 — EXTEND (M1 re-graded Minor; M-add-1 false-ACCEPT + m-add-1 added)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual review complete; final verdict NEEDS-FIXES (user-ratified all dispositions). DCE-1 (Drift-Check Enforcement): new `tools/drift_check_audit.py` procedural "was-it-marked" gate (CRP-1 pattern), wired into `/build-slice` Step 6 after a full-mode `/drift-check`. Matcher is line-anchored to `**Trigger**:` lines (M-add-1) + slice-number-anchored. ADR-073 (cheap). Target v0.76.0. Bootstrap discharges on slice-081's own build.

## Pending fixes to apply at /build-slice (ACCEPTED-PENDING)

- B1: line-anchored + tolerant matcher + canonicalize `skills/drift-check/SKILL.md:114` template + pin test.
- B2: add `drift-check-skip:` to `skills/build-slice/SKILL.md` Step 7b preserved-keys (~L494) + `~/.claude/templates/milestone.md`; accept/malformed fixtures.
- M1: copy CRP-1 literals byte-faithfully + `grep -n` byte-faithfulness check.
- M2: full-mode `/drift-check` requirement in the Step 6 sub-block prose.
- M-add-1: implement the `**Trigger**:`-line-anchored matcher + negative fixture (cross-mention → exit 1).
- m-add-1: APED-1 assertion that slice-081's own written entry (with a `**Trigger**: slice-081` line) exits 0.
- (ACCEPTED-FIXED already applied: M3 AC restructure, m2 citation, m3 ADR clause.)

## On resume

- **Last completed action**: /critique + /critique-review (critique.md + critique-review.md written; TRI-1 ratified; both structural audits clean)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (apply the ACCEPTED-PENDING fixes above)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
