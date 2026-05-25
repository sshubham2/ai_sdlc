---
slice: slice-030-repair-build-checks-vault-and-harden-shippability
stage: complete
updated: 2026-05-16
next-action: none (slice complete — run /commit-slice to generate the audit-grade commit)
risk-tier: medium
critic-required: true
---

# Milestone: slice-030 repair-build-checks-vault-and-harden-shippability

**Stage**: critique (v3/030A — CLEAN, user-ratified)
**Next action**: run `/build-slice` on the bounded 030A scope
**Updated**: 2026-05-16
**Risk tier**: medium — Critic required: yes (touches in-house methodology surfaces: `skills/reflect/SKILL.md`, `tests/methodology/`, build-checks fixtures; mandatory-Critic trigger regardless of tier)

## Progress

- [x] /slice — 2026-05-16
- [x] /design-slice — 2026-05-16 (v1)
- [x] /critique — 2026-05-16 — BLOCKED (dual-review EXTEND, +M-add-1)
- [x] /design-slice — 2026-05-16 (v2)
- [x] /critique — 2026-05-16 — BLOCKED (re-critique; dual-review EXTEND, +M-add-1/2/3; non-convergence signal)
- [x] USER DECISION — split (AskUserQuestion, 2026-05-16)
- [x] /design-slice — 2026-05-16 (v3 — split to 030A scope)
- [x] /critique — 2026-05-16 — **CLEAN** (v3 re-critique NEEDS-FIXES → all 6 ACCEPTED-FIXED + applied; dual-review ADJUST, sole adjustment applied; user-ratified TRI-1; triage_audit clean)
- [x] /build-slice — 2026-05-16 — **SHIPPED** (9/9 tasks; mid-slice smoke 39/0; pre-finish gate fully passed; full methodology suite 573/0; BCI-1 self-run exit 0; PMI-1/INST-1 clean v0.44.0)
- [x] /validate-slice — 2026-05-16 — **PASS** (5/5 ACs PASS + VAL-1/PTFCD-1 clean; shippability 25/29 — #1/#19 spurious CRLF/LF artifact (content byte-identical, slice-030A innocent) + #28/#29 runner artifacts → **user-approved deferral** at PCA-1 gate; drift-test CRLF/LF fragility → /reflect Discovered + future slice)
- [x] /reflect — 2026-05-16 (reflection.md written; R-4 open→mitigating; R-5 added; lessons-learned + shippability row 30; build-checks promotion skipped per recommendation; slice auto-archiving)

## Current focus

**v3 / 030A redesign complete (split per user decision).** Two BLOCKED loops + meta-Critic non-convergence signal → user chose split. 030A = minimal emergency: tracked canonical fixtures + an **all-5-rule literal-constant tracked oracle** (incl. NEW pins for BC-PROJ-3/BC-GLOBAL-2 from their surviving uncorrupted bodies — closes meta-M-add-3) + a non-opt-out **full-structural-identity** BCI-1 gate (`rule_id,severity,applies_to,trigger_keywords,trigger_anchors,negative_anchors`+non-empty check — closes meta-M-add-2/v2-B2) wired at /build-slice pre-finish + Step5b post-write; absent-global=WARN, empty-global=HALT (meta-M3); propagation file-locations corrected (meta-M2). DEFERRED to 030B: shippability rows #5/#8/#12 + `test_methodology_changelog.py` decoupling (v2-B1/meta-M-add-1) + archive-backtest fidelity (meta-M1′). Process errors recorded for /reflect: rubber-stamped 2 loops; overwrote v1 audit trail (restored in critique-history-v1.md); silently weakened a ratified disposition.

## On resume

- **Last completed action**: /build-slice plan approved + task-1 recovery inputs gathered; CHECKPOINT before authoring the 3 lost rules' severity/trigger_keywords (highest-fidelity-risk; not rushed at end of long session)
- **Current work**: build task 1 (recover canonical rule bodies) — paused mid-task, NO code/tracked-file edits yet
- **Next immediate step**: RESUME task 1 — read gitignored archived slice-005 (BC-GLOBAL-1, slice-005-add-bc-1-keyword-precision), slice-008 (BC-PROJ-1 negative-context), slice-012 (BC-PROJ-2 negative-anchor migration) reflections+designs+build-logs for the 3 lost rules' exact `Severity`/`Applies to`/`Trigger keywords`; cross-check anchors are a subset of keywords; then tasks 2-9 per the approved plan in build-log.md
- **Branch**: `slice/030-repair-build-checks-vault-and-harden-shippability` (created; no commits yet — vault edits are gitignored)
- **Approved plan**: 9 tasks, mid-slice smoke at task 5 (`pytest test_build_checks_audit.py` → 0 failed + `BC-GLOBAL-1.applies_to == ("**",)` cross-check) — see build-log.md Events

## Phase artifacts

- [mission-brief.md](mission-brief.md) — v3/030A (split-scoped; "Deferred to 030B")
- [design.md](design.md) — v3/030A
- [ADR-028](../../decisions/ADR-028-bc1-tests-assert-tracked-fixture-not-gitignored-vault.md) — v3 (revised in-slice; decoupling claim removed → 030B)
- [ADR-029](../../decisions/ADR-029-bc1-integrity-enforced-by-deterministic-gate-not-llm-prose.md) — updated (full structural identity)
- [critique.md](critique.md) — v2 re-critique BLOCKED (triage pending re-critique of v3)
- [critique-review.md](critique-review.md) — v2 dual-review EXTEND (audit clean)
- [critique-history-v1.md](critique-history-v1.md) — RESTORED v1 audit trail
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
