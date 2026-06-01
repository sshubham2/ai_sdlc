---
slice: slice-098-route-or-retire-git-coupled-vault-tools
stage: complete
updated: 2026-06-02
next-action: none (slice complete — run /commit-slice to merge + generate the audit commit)
risk-tier: medium
critic-required: true
worktree: C:/Users/sshub/ai_sdlc-wt/slice-098-route-or-retire-git-coupled-vault-tools
---

# Milestone: slice-098 route-or-retire-git-coupled-vault-tools

**Stage**: complete
**Next action**: none (slice complete) — run `/commit-slice` to merge the worktree + generate the audit commit
**Updated**: 2026-06-02
**Risk tier**: medium — Critic required: yes (mandatory trigger: in-house methodology surface `tools/*.py` + R-32 concurrent-write safety path)

## Progress

- [x] /slice — 2026-06-01
- [x] /design-slice — 2026-06-01
- [x] /critique — 2026-06-01 — NEEDS-FIXES (first Critic BLOCKED: 2B/5M/2m all VALID; meta-Critic EXTEND: +3 Major; user-triaged, all ACCEPTED-FIXED/PENDING)
- [x] /build-slice — 2026-06-02 — SHIPPED (6/6 tasks; full suite 1450 PASS; all Step-6 gates green)
- [x] /code-review — 2026-06-02 — FINDINGS 0B/2M/4m (advisory; M1/M2/m3 fixed, m4 dispositioned, m1/m2 acknowledged)
- [x] /validate-slice — 2026-06-02 — PASS (5/5 ACs; VAL-1 clean; shippability 104/104; full suite 1450)
- [x] /reflect — 2026-06-02 — vault updated (R-32 narrowed via CAS, lessons, shippability #106); 3-Critic calibration captured; archived

## Current focus

Build SHIPPED. The as-built model (after 2 user-ratified build deviations):
- **Two literal classes**: Class-A filesystem-path literals → ROUTE through `VAULT_ROOT`; Class-B git-string identities (`_SOFT_FILE_SET`, git pathspecs, `git add` args, `qrel`/`srel`) → NEVER routed; carry the slice-068 `# NOT VAULT_ROOT-routed` marker (21 in PCR).
- **Binding RETIRE signal = `vault_is_external(repo_root)`** (store-location), UNIFIED across PCR + stranded — supersedes the r2/r3 per-pathspec `git ls-files` tracked-check, which missed PCR's B2 (external-abs-but-still-tracked) corruption AND over-RETIRED stranded's branch-only-content fixtures. `vault_pathspec_is_tracked` retained as a tested primitive for the flip slice.
- **M-add-1**: PCR diagnose-time reads protected by U-file-absence→UNKNOWN (call-spy test, no redundant guard); equivalence-guard reads by the `_retire_if_vault_external` resolve-entry guard (before `out_path`/`relative_to`, B2).
- **M-add-2**: stranded `archive_path`/`milestone_path` materialized twice (git pathspec + routed Path).
- **No-flip safety contract** holds by construction (env unset → `vault_is_external`=False → every current path unchanged); full suite 1450 PASS.

Migration pins transitioned: `_MIGRATION_SITE_ALLOWLIST` 11→14; slice-093 AC4 test → 14 + positive asserts. MEPD-1 EXCLUDE (underscore module, no VERSION bump). R-32 stays `mitigating` (advances toward retirement-at-flip).

## Next: /code-review (in-loop adversarial code-Critic on the slice diff), then /validate-slice, then /reflect.

## On resume

- **Last completed action**: /critique + /critique-review (dual review; TRI-1 ratified NEEDS-FIXES)
- **Current work**: none — awaiting build-plan approval
- **Next immediate step**: run `/build-slice` IN the existing worktree (`C:/Users/sshub/ai_sdlc-wt/slice-098-...`, branch `slice/098-route-or-retire-git-coupled-vault-tools`). Worktree already created (slice-time); do NOT re-create. Master is clean.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — r3 (post-dual-review)
- [critique.md](critique.md) — NEEDS-FIXES (TRI-1 triaged)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic +3 Major)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
