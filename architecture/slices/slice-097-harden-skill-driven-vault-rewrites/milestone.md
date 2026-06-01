---
slice: slice-097-harden-skill-driven-vault-rewrites
stage: critique
updated: 2026-06-01
next-action: run /build-slice
risk-tier: high
critic-required: true
---

# Milestone: slice-097 harden-skill-driven-vault-rewrites

**Stage**: critique
**Next action**: run `/build-slice` (verdict NEEDS-FIXES — apply the 4 ACCEPTED-PENDING fixes during build)
**Updated**: 2026-06-01
**Risk tier**: high — Critic required: yes (write-safety/data-integrity + in-house methodology surfaces: `tools/**/*.py` + `skills/*/SKILL.md`)

## Progress

- [x] /slice — 2026-06-01
- [x] /design-slice — 2026-06-01
- [x] /critique — 2026-06-01 — NEEDS-FIXES (3-Critic stack: design-Critic 3B/3M/2m + meta-Critic EXTEND +1B/+1M/+3m; all VALIDATED, zero suspicious)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Critique complete, verdict **NEEDS-FIXES** (user-ratified TRI-1, all 13 dispositions as drafted). Dual stack worked: design-Critic caught B1 (CRLF byte-exact CAS false-conflict + corruption), B2 (audit can't tell rewrite- from append-routing), B3 (Haiku-subagent has no home for the CAS loop); meta-Critic EXTEND caught **B-add-1** (my B2 fix didn't sever the bare-`tools.vault_edit` flat-OR — a fresh-claim catch) + M-add-1 (`_normalize_eol` silent-overwrite edge). Design.md + ADR-088 carry all fix-deltas.

**Build fix-list (4 ACCEPTED-PENDING):** B1 EOL-normalized-compare + EOL-preserving-write (vs real CRLF `_index.md`/`risk-register.md`); B2/B-add-1 op-class discriminator (retire bare token, classify subcommand, asymmetric verdict, bare-token-severance adversarial proof); M-add-1 `_normalize_eol` = CRLF→LF-only both-direction tests. Plus the ACCEPTED-FIXED items already in design.

## On resume

- **Last completed action**: /critique + /critique-review + TRI-1 (verdict NEEDS-FIXES, ratified by user)
- **Current work**: none — awaiting user approval of the build plan
- **Next immediate step**: present build plan → on approval run `/build-slice` (NOT auto-fired)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-088](../../decisions/ADR-088-close-skill-rmw-vault-writes-via-cas.md)
- [critique.md](critique.md) — NEEDS-FIXES (8 findings, triaged)
- [critique-review.md](critique-review.md) — EXTEND (5 missed findings)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
