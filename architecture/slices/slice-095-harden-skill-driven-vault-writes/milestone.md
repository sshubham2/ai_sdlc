---
slice: slice-095-harden-skill-driven-vault-writes
stage: design
updated: 2026-06-01
next-action: run /critique
risk-tier: medium
critic-required: true
---

# Milestone: slice-095 harden-skill-driven-vault-writes

**Stage**: design
**Next action**: run `/critique`
**Updated**: 2026-06-01
**Risk tier**: medium — Critic required: **yes** (mandatory trigger: in-house methodology surfaces `skills/*/SKILL.md` + two new `tools/**/*.py` modules; reinforced by vault data-integrity / concurrency sensitivity + the ADR-worthy mechanism decision now locked in [[ADR-087]])

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-06-01
- [ ] /critique
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Design complete (ADR-087 / SVW-1). User ratified the 3 open forks at design: **wrapper CLI + static audit** (mechanism), **shared-aggregate files only** (scope), **defer the rewrite/lost-update class → narrow R-32** (not full-retire). What's new: `tools/vault_edit.py` (`append`-only CLI over `safe_append_text`) + `tools/skill_vault_write_safety_audit.py` (fail-closed lexical SKILL.md audit, two tripwires + `<!-- vault-write-safe: -->` exemption marker) + 2 new tests; routes `/reflect`+`/reduce`+`/archive` append-class prose. MEPD-1 **INCLUDE** (SVW-1, v0.80.0, 2-tool PMI-1 fan-out).

**Brief amendment (design-time)**: AC4/Intent "RETIRE R-32" → "**NARROW** R-32" — the append axis closes (094+095), but a skill-driven read-modify-write/lost-update residual (`_index.md` recent-10; in-place risk-status flips) defers to the flip slice. R-32 stays `mitigating` at /reflect.

**Sequencing note**: parallel slice-094 (Python-writer sub-class) shares coordination files (`risk-register.md`, `shippability.md`, gate-roster SKILL.md) — **NOT cleanly non-overlapping**. 095 sits above 094's in-flight claims: **ADR-087** (094=086), **v0.80.0** (094 plans v0.79.0), RULE-ID **SVW-1** (094=VWS-1). Reconcile via PCR / `git merge master` before pre-finish (slice-092/R-33 lesson).

## On resume

- **Last completed action**: /design-slice (design.md + ADR-087 written; milestone advanced)
- **Current work**: none
- **Next immediate step**: run `/critique` (critic-required: true — mandatory; the design carries an APED-1 prose-audit obligation + the honest static-vs-runtime-obedience residual for the Critic to probe)
- **Build note**: real BRANCH-2 worktree at `C:/Users/sshub/ai_sdlc-wt/slice-095-…` (already isolated); NOT WORKTREE=skip.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
