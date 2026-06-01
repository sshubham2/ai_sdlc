---
slice: slice-095-harden-skill-driven-vault-writes
stage: build
updated: 2026-06-01
next-action: /build-slice in progress — Phases A–D done (mid-slice smoke PASS); Phase E (wire) + F (version fan-out) + G (pre-finish) remain
risk-tier: medium
critic-required: true
---

# Milestone: slice-095 harden-skill-driven-vault-writes

**Stage**: build
**Next action**: `/build-slice` — Phases A–D DONE (2 tools + 2 tests + routing; mid-slice smoke PASS, 19 tests green). Remaining: Phase E (wire audit into build-slice/validate-slice gate rosters), Phase F (plugin.yaml + install_audit + cp1252-list + VERSION 0.79.0 + changelog + shippability + ~/.claude forward-sync + pip upgrade), Phase G (16 pre-finish audits + full suite + git merge master reconcile)
**Updated**: 2026-06-01
**Risk tier**: medium — Critic required: **yes** (mandatory trigger: in-house methodology surfaces `skills/*/SKILL.md` + two new `tools/**/*.py` modules; reinforced by vault data-integrity / concurrency sensitivity + the ADR-worthy mechanism decision locked in [[ADR-087]])

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-06-01
- [x] /critique — 2026-06-01 — NEEDS-FIXES (dual-review: design-Critic 2B/3M/2m + meta-Critic EXTEND +2; all 9 ACCEPTED, user-ratified TRI-1)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic review COMPLETE + user-ratified (TRI-1: NEEDS-FIXES). design-Critic 2B/3M/2m + meta-Critic EXTEND (+M-add-1/M-add-2). 8 of 9 findings ACCEPTED-FIXED in design.md/ADR-087 this round; **M1 (matcher FP/FN measurement) is the only ACCEPTED-PENDING → applied at /build-slice**. Enumeration of skill-driven mutators is now COMPLETE (26 skills, re-grepped): routed appends = `/reflect`+`/reduce`+`/repro`+`/validate-slice`+`/user-test`+`/archive`; deferred RMW = `/reflect`+`/archive`+`/supersede-slice`; exempt project-open = `/triage`+`/discover`+`/risk-spike`. What's new: `tools/vault_edit.py` (`append`-only CLI over `safe_append_text`) + `tools/skill_vault_write_safety_audit.py` (fail-closed lexical audit: directive-shape matcher + closed reason-enum + pinned exemption allowlist) + 2 tests. MEPD-1 **INCLUDE** (SVW-1, v0.80.0, 2-tool PMI-1 fan-out).

**Build must-dos carried from critique** (the non-obvious ones): (M1) EXECUTE the matcher against all 26 skills, record FP/FN in build-log, `build-slice:394` must be CLEAN without exemption; (M3) ship the closed reason-enum + `_REGISTERED_SKILL_EXEMPTIONS` allowlist pin; (B1) the audit is honestly scoped to the prose-detection surface (NOT a completeness guarantee over writes); concurrency test = N concurrent `vault_edit append` SUBPROCESSES, mutation-proof; cp1252-safe (RSAD-1); 2-tool count fan-out (plugin.yaml/install_audit/INSTALL.md/cp1252-parametrize/inventory-pin).

**Brief amendment (design-time)**: AC4/Intent "RETIRE R-32" → "**NARROW** R-32" — the append axis closes (094+095), but a skill-driven read-modify-write/lost-update residual (`_index.md` recent-10; in-place risk-status flips) defers to the flip slice. R-32 stays `mitigating` at /reflect.

**Sequencing note**: parallel slice-094 (Python-writer sub-class) shares coordination files (`risk-register.md`, `shippability.md`, gate-roster SKILL.md) — **NOT cleanly non-overlapping**. 095 sits above 094's in-flight claims: **ADR-087** (094=086), **v0.80.0** (094 plans v0.79.0), RULE-ID **SVW-1** (094=VWS-1). Reconcile via PCR / `git merge master` before pre-finish (slice-092/R-33 lesson).

## On resume

- **Last completed action**: /critique + /critique-review (dual review; TRI-1 user-ratified NEEDS-FIXES)
- **Current work**: none — awaiting user approval of the build plan before /build-slice (per the present-build-plan-after-critique-review discipline)
- **Next immediate step**: run `/build-slice` (after the user approves the build plan). Apply M1 (matcher FP/FN execution) during build; 8 other findings already fixed in design.
- **Build note**: real BRANCH-2 worktree at `C:/Users/sshub/ai_sdlc-wt/slice-095-harden-skill-driven-vault-writes` (already isolated, branch `slice/095-…`); NOT WORKTREE=skip. Reconcile with master before pre-finish full-suite (parallel slice-094; slice-092/R-33 lesson).

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (design-Critic 2B/3M/2m, all ACCEPTED; TRI-1 user-ratified)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic +M-add-1/M-add-2, both ACCEPTED-FIXED)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
