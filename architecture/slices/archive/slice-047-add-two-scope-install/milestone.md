---
slice: slice-047-add-two-scope-install
stage: complete
updated: 2026-05-19
next-action: none (slice complete — decision-only / withdrawn-feature; archived)
risk-tier: high
critic-required: true
outcome: decision-only / withdrawn-feature
---

# Milestone: slice-047 add-two-scope-install

**Stage**: complete — decision-only / withdrawn-feature (TRI-1, 2026-05-19); lessons captured, auto-archiving
**Next action**: none (slice complete)
**Updated**: 2026-05-19
**Risk tier**: high — Critic was required and ran (BLOCKED → user-abandoned the feature)

## Progress

- [x] /slice — 2026-05-19
- [x] /design-slice — 2026-05-19
- [x] /critique — 2026-05-19 — **BLOCKED** (B1 ESCALATED)
- [x] /critique-review — 2026-05-19 — **EXTEND** (M-add-1 reinforces B1)
- [x] TRI-1 user triage — 2026-05-19 — **feature ABANDONED as platform-infeasible**
- [x] ADR-049 rewritten in place → global-only decision record (2026-05-19)
- [ ] /build-slice — **NOT run** (feature withdrawn; no build)
- [ ] /validate-slice — **NOT run** (no build to validate)
- [x] /reflect — 2026-05-19 — decision-only closeout; BC-GLOBAL-3 promoted; auto-archiving

## Current focus

Slice closed out as decision-only / withdrawn-feature. Platform-precedence
learnings captured (reflection.md + lessons-learned.md); BC-GLOBAL-3 promoted
(external-platform behavior must be official-doc-verified before design lock);
shippability row 47 added. Auto-archiving next.

## (historical) Current focus

**Closed out.** The `add-two-scope-install` *feature* was abandoned at TRI-1
(2026-05-19) as platform-infeasible: B1 (skills — personal `~/.claude/`
overrides project `.claude/`; Builder-confirmed via WebFetch) + M-add-1
(agents — project `.claude/agents/` overrides user, the inverse → a
split-resolution runtime state that INST-1's on-disk audit false-greens;
Builder-confirmed via WebFetch). The salvaged value is preserved: **ADR-049
has been rewritten in place** from a feature-design ADR into a **global-only
decision record** that retires the standing slice-045/046 scope-blindness
deferral by deciding it (global-only) and names the only future path
(plugin re-architecture, namespaced `plugin-name:skill-name`). No INSTALL.md
change, no VERSION bump, no v0.56.0 changelog entry, no shippability row
(no-behavior-change / decision-only class — slice-043/045 precedent). M1/M2/
M3/m1/m-add-2 DEFERRED-moot; m2 ACCEPTED-PENDING (the reversibility-precision
wording is folded into the rewritten ADR-049).

## On resume

- **Last completed action**: ADR-049 rewritten → global-only decision record; this milestone updated to `closed`
- **Current work**: slice-047 closeout complete on the artifact side; awaiting `/reflect`
- **Next immediate step**: run `/reflect` — capture the platform-precedence learnings (load-bearing platform assumption that survived design + first-Critic; caught only by Builder WebFetch + meta-Critic asymmetry analysis → strong `/critic-calibrate` input) + auto-archive slice-047; then `/slice` for a fresh next candidate

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — superseded by the TRI-1 abandon decision (feature not built)
- [decisions/ADR-049](../../decisions/ADR-049-two-scope-install-content-vs-global-boundary.md) — rewritten → global-only **decision record**
- [critique.md](critique.md) — BLOCKED; carries the full TRI-1 disposition table
- [critique-review.md](critique-review.md) — EXTEND (M-add-1)
- build-log.md — not created (feature withdrawn; /build-slice NOT run)
- validation.md — not created (no build to validate)
- reflection.md — pending (/reflect)
