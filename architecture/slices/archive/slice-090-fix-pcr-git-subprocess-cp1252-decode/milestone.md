---
slice: slice-090-fix-pcr-git-subprocess-cp1252-decode
stage: complete
updated: 2026-05-31
next-action: none (slice complete)
risk-tier: low
critic-required: true
---

# Milestone: slice-090 fix-pcr-git-subprocess-cp1252-decode

**Stage**: critique
**Next action**: run `/critique-review`, then TRI-1 user triage
**Updated**: 2026-05-31
**Risk tier**: low — Critic required: YES. Tier is low (localized bug fix: add `encoding="utf-8"` to git subprocess calls), but the slice touches an in-house methodology surface (`tools/parallel_conflict_resolver.py`), so the mandatory-Critic trigger fires regardless of tier.

## Progress

- [x] /repro — 2026-05-31 (failing repro established: `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py`; shippability #95)
- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-05-31
- [x] /critique — 2026-05-31 — NEEDS-FIXES (Critic verdict; 1B/3M/2m, B1/M1/M2/M3 doc-fixes applied)
- [x] /critique-review — 2026-05-31 — EXTEND (6 confirmed, 0 suspicious, 2 missed [M-add-1/2], 2 severity adj [B1↓Major, m1↑Major])
- [x] TRI-1 user triage — 2026-05-31 — NEEDS-FIXES (all 8 dispositions ratified as drafted)
- [x] /build-slice — 2026-05-31 — SHIPPED (WORKTREE=skip; 9 sites encoded + AST guard; 16 Step-6 gates green; full suite 1270 pass / 2 sibling-induced fail deferred per R-28)
- [x] /code-review — 2026-05-31 — FINDINGS (0 blockers, 0 majors, 2 minors — both applied in-slice: docstring precision on _git_show_stage None-passthrough)
- [x] /validate-slice — 2026-05-31 — PARTIAL→cleared (3 ACs PASS + VAL-1 clean; shippability 92 PASS / 3 sibling-induced FAIL R-28 USER-APPROVED DEFERRAL; zero slice-090 regressions)
- [x] /reflect — 2026-05-31 — R-30/R-31 registered; BC-PROJ-15 + BC-GLOBAL-5 promoted (BCI-1 green); lessons captured
- [ ] /reflect
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Design complete. Fix = add `encoding="utf-8"` (strict) to every output-capturing git `subprocess.run` in `tools/parallel_conflict_resolver.py` (~10 sites), recurrence-guarded by an AST source-scan test. ADR-082 (cheap) records the per-call-not-wrapper + strict-errors decision. No contract/data-model/CLI change. Ready for Critic (mandatory — touches `tools/`).

## On resume

- **Last completed action**: /design-slice (design.md + ADR-082 written)
- **Current work**: none
- **Next immediate step**: run `/critique`
- **Parallel-slice note**: slice-089 is also active (stage=design). `_index.md` "Active" table is stale (shows none) — authoritative state is the slice folders' milestone.md files.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-082](../../decisions/ADR-082-utf8-strict-git-subprocess-decode-in-pcr.md)
- [critique.md](critique.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
