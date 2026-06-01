---
slice: slice-095-harden-skill-driven-vault-writes
stage: code-review
updated: 2026-06-01
next-action: DECIDE code-review majors (harden M1/M2/M3 now vs accept-advisory → /validate-slice)
risk-tier: medium
critic-required: true
---

# Milestone: slice-095 harden-skill-driven-vault-writes

**Stage**: code-review (COMPLETE — advisory findings; PENDING USER DECISION)
**Next action**: **DECIDE** — harden the 3 code-review majors (M1/M2/M3) now, OR accept advisory (CRSI-1 v1) and run `/validate-slice`. See `code-review.md`.
**Updated**: 2026-06-01
**Risk tier**: medium — Critic required **yes** (in-house methodology surfaces `skills/*/SKILL.md` + 2 new `tools/*.py`; ADR-worthy mechanism locked in [[ADR-087]])

> **Build SHIPPED** (full suite **1335 pass / 2 skip / 0 fail**; all 16 Step-6 audits green; shared `~/.claude` install forward-synced to **v0.79.0**, user-approved). **code-review = FINDINGS 0B/3M/4m (advisory).**

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-06-01 (ADR-087 / SVW-1)
- [x] /critique — 2026-06-01 — NEEDS-FIXES (design-Critic 2B/3M/2m + meta-Critic EXTEND +2; 9/9 ACCEPTED, TRI-1 user-ratified)
- [x] /build-slice — 2026-06-01 — SHIPPED (1335 pass; 16 Step-6 audits green; M1 matcher executed FP=0 vs real 26-skill corpus)
- [x] /code-review — 2026-06-01 — FINDINGS (0B/3M/4m, advisory): M1 route-token false-CLEAN on negation; M2 narrow 6-verb lexicon fail-OPEN for unlisted verbs; M3 `(file,reason)` pin not site-count; m1 tilde-fence, m2 typo-creates-file, m3 vault-root-not-rejected, m4 empty-no-op
- [ ] /validate-slice
- [ ] /reflect
- [ ] /commit-slice (user-invoked; v0.79.0 — parallel slice-094 will need v0.80.0 + reconcile)

## Current focus — RESUME HERE

**Pending user decision** (asked at end of /code-review, user deferred to a fresh session): the code-Critic (0B/3M/4m, advisory in CRSI-1 v1) found 3 fail-OPEN holes in the SVW-1 matcher that undercut AC2's "never a silent pass":
- **M1** — `_verdict` (`skill_vault_write_safety_audit.py:196`) is a naive line-local substring; a line naming the route token while instructing a RAW write (`"...raw (do NOT use tools.vault_edit append)"`) false-CLEANs. Fix: route token must appear AFTER the file-ref (govern) + treat negations (`do NOT`/`never`/`by hand`/`not via`) as VIOLATION.
- **M2** (most important) — `_DIRECTIVE_VERBS` (`:82-84`) is only 6 verbs; `insert/replace/log/record/note/set/mark/put/create/amend` all pass CLEAN (fail-OPEN). Fix: expand lexicon AND honestly document the lexicon-bound residual (the audit is "fail-closed for RECOGNIZED sites"; recognition is lexicon-bounded).
- **M3** — `_REGISTERED_SKILL_EXEMPTIONS` (`:102-115`) pins `(file,reason)` pairs (5), not the 11 site-lines; a future editor can add unlimited new `deferred-rmw` markers to reflect/archive without tripping `test_exemption_allowlist_pinned`. Fix: per-`(file,reason)`-COUNT pin.
- **Plus cheap minors**: m1 (`_FENCE_RE` match `~~~` too), m3 (reject `--file .`/vault-root in `_resolve_in_vault`). **Defer** m2 (typo-creates-file) + m4 (empty no-op) — cooperative model bounds them.
- **APED-1 gap**: my battery (`test_skill_vault_write_safety_audit.py`) tested documented FP shapes but NOT the negated-route / unlisted-verb / tilde-fence cases — add those if hardening.

**Two resume paths** (full detail + proposed fixes in `code-review.md`):
1. **Harden now** (recommended): apply M1/M2/M3 + m1/m3 + APED-1 tests to `tools/skill_vault_write_safety_audit.py` + `tools/vault_edit.py` + the test files; re-run `$PY -m tools.skill_vault_write_safety_audit` (must stay exit 0) + the 2 SVW test files + full suite; re-verify all Step-6 audits; commit; then `/validate-slice`.
2. **Accept advisory** → `/validate-slice` now; queue a follow-up `harden-svw-1-matcher-fail-open` slice; the residual is documented in code-review.md + carries to /reflect calibration.

## On resume (fresh session after /clear)

- **Worktree**: `C:/Users/sshub/ai_sdlc-wt/slice-095-harden-skill-driven-vault-writes` (branch `slice/095-harden-skill-driven-vault-writes`, base master `5f13582`). Run all build/test/audit cmds in a subshell `cd`'d to the worktree (cwd wins on sys.path; the venv `ai-sdlc-tools` is NON-editable, refreshed to 0.79.0).
- **State**: build SHIPPED + code-review done, all COMMITTED (last commit `cfc43c5` + the code-review round). master clean.
- **R-20 seed already done**: `diagnose-out/` + `graphify-out/` seeded into the worktree (gitignored).
- **Shared install is at v0.79.0** (forward-synced). Parallel **slice-094** (parked at critique, still 0.78.0) must take **v0.80.0** + reconcile AVFS/MCFS/TVFS/OSDG when it builds (second-merger checklist in design.md §Sequencing).
- **Next immediate step**: resolve the pending decision above (harden vs accept-advisory), then `/validate-slice` → `/reflect` → `/commit-slice --merge`.
- **Discovered (logged in drift-log.md, for follow-up)**: triage/SKILL.md unclosed ```` ```markdown ```` fence (~:142); an R-15 archive-path fragility in test_external_vault_adr_and_risk.py (fixed in-place).

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — note: §Sequencing says "v0.80.0" but BUILT as **v0.79.0** (user choice at build gate; logged in build-log Events)
- [critique.md](critique.md) — NEEDS-FIXES (design-Critic 2B/3M/2m, TRI-1 user-ratified)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic +M-add-1/M-add-2)
- [build-log.md](build-log.md) — SHIPPED (full Events trail of the build + forward-sync + fan-out fixes)
- [code-review.md](code-review.md) — FINDINGS 0B/3M/4m (advisory; the 3 majors + proposed fixes)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
