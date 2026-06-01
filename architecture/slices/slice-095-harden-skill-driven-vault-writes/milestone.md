---
slice: slice-095-harden-skill-driven-vault-writes
stage: validate
updated: 2026-06-01
next-action: run /reflect (validate PASS — 5/5 ACs, VAL-1 clean, WS-1/ETC-1 n/a, shippability 101/101)
risk-tier: medium
critic-required: true
---

# Milestone: slice-095 harden-skill-driven-vault-writes

**Stage**: validate (PASS — 5/5 ACs, VAL-1 clean, shippability 101/101)
**Next action**: run `/reflect`. (Code-review majors hardened + validated; SVW audit clean exit 0 — 22 sites / 10 routed / 12 exempted; full suite 1367 pass.)
**Updated**: 2026-06-01
**Risk tier**: medium — Critic required **yes** (in-house methodology surfaces `skills/*/SKILL.md` + 2 new `tools/*.py`; ADR-worthy mechanism locked in [[ADR-087]])

> **Build SHIPPED + code-review HARDENED** (full suite **1367 pass / 0 fail**; SVW audit clean; shared `~/.claude` install forward-synced — v0.79.0 + this round's triage/build-slice/changelog count reconciliation). code-review was 0B/3M/4m (advisory); all 3 majors + m1/m3 + APED-1 gaps now closed in-slice.

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-06-01 (ADR-087 / SVW-1)
- [x] /critique — 2026-06-01 — NEEDS-FIXES (design-Critic 2B/3M/2m + meta-Critic EXTEND +2; 9/9 ACCEPTED, TRI-1 user-ratified)
- [x] /build-slice — 2026-06-01 — SHIPPED (1335 pass; 16 Step-6 audits green; M1 matcher executed FP=0 vs real 26-skill corpus)
- [x] /code-review — 2026-06-01 — FINDINGS (0B/3M/4m, advisory) → **HARDENED in-slice**: M1 (route-token: backtick/marker-scoped + negation-aware), M2 (lexicon +6 verbs + documented residual), M3 (per-(file,reason) count pin), m1 (CommonMark fence tracker — surfaced+exempted triage:179), m3 (vault_edit vault-root reject). m2 (typo-creates-file) + m4 (empty-no-op) DEFERRED per code-review (cooperative model bounds them).
- [x] /validate-slice — 2026-06-01 — **PASS** (5/5 ACs PASS w/ evidence; VAL-1 0 secrets/0 imports; WS-1/ETC-1 n/a; shippability 101/101; SVW audit clean 22/10/12)
- [ ] /reflect ← **next**
- [ ] /commit-slice (user-invoked; v0.79.0 — parallel slice-094 will need v0.80.0 + reconcile)

## Current focus — code-review majors HARDENED (next: /validate-slice)

**RESOLVED** — user chose "harden now" (was deferred to a fresh session). All 3 code-Critic majors + cheap minors m1/m3 + the APED-1 gaps are addressed in-slice (SVW audit clean 22/10/12; full suite 1367 pass). What was fixed (the 3 fail-OPEN holes in the SVW-1 matcher that undercut AC2's "never a silent pass"):
- **M1** — `_verdict` (`skill_vault_write_safety_audit.py:196`) is a naive line-local substring; a line naming the route token while instructing a RAW write (`"...raw (do NOT use tools.vault_edit append)"`) false-CLEANs. Fix: route token must appear AFTER the file-ref (govern) + treat negations (`do NOT`/`never`/`by hand`/`not via`) as VIOLATION.
- **M2** (most important) — `_DIRECTIVE_VERBS` (`:82-84`) is only 6 verbs; `insert/replace/log/record/note/set/mark/put/create/amend` all pass CLEAN (fail-OPEN). Fix: expand lexicon AND honestly document the lexicon-bound residual (the audit is "fail-closed for RECOGNIZED sites"; recognition is lexicon-bounded).
- **M3** — `_REGISTERED_SKILL_EXEMPTIONS` (`:102-115`) pins `(file,reason)` pairs (5), not the 11 site-lines; a future editor can add unlimited new `deferred-rmw` markers to reflect/archive without tripping `test_exemption_allowlist_pinned`. Fix: per-`(file,reason)`-COUNT pin.
- **Plus cheap minors**: m1 (`_FENCE_RE` match `~~~` too), m3 (reject `--file .`/vault-root in `_resolve_in_vault`). **Defer** m2 (typo-creates-file) + m4 (empty no-op) — cooperative model bounds them.
- **APED-1 gap**: my battery (`test_skill_vault_write_safety_audit.py`) tested documented FP shapes but NOT the negated-route / unlisted-verb / tilde-fence cases — add those if hardening.

**Resolution** — Path 1 (harden now) taken. Applied M1/M2/M3 + m1/m3 + APED-1 tests across `tools/skill_vault_write_safety_audit.py` + `tools/vault_edit.py` + the test files; SVW audit stays exit 0; the 2 SVW test files + new `tests/methodology/test_vault_edit_cli.py` + full suite (1367 pass) green; guarded-skill drift (triage/build-slice) + changelog forward-synced. **m1 side effect**: the CommonMark fence fix surfaced triage:179 (a real project-open risk-register write previously hidden by triage's malformed nested fence) → exempted `project-open-single-shot` + allowlist-pinned (reversed the build-time fence-bug-reliance — visible residual now); counts 11→12 exempt / 21→22 sites reconciled in changelog/build-slice/risk-register. m2 (typo-creates-file) + m4 (empty no-op) DEFERRED per code-review. Next: `/validate-slice`.

## On resume (fresh session after /clear)

- **Worktree**: `C:/Users/sshub/ai_sdlc-wt/slice-095-harden-skill-driven-vault-writes` (branch `slice/095-harden-skill-driven-vault-writes`, base master `5f13582`). Run all build/test/audit cmds in a subshell `cd`'d to the worktree (cwd wins on sys.path; the venv `ai-sdlc-tools` is NON-editable, refreshed to 0.79.0).
- **State**: build SHIPPED + code-review HARDENED. The code-review-remediation round (M1/M2/M3 + m1/m3 + APED-1) committed on the slice branch; master clean.
- **R-20 seed already done**: `diagnose-out/` + `graphify-out/` seeded into the worktree (gitignored).
- **Shared install forward-synced**: v0.79.0 + this round's triage/build-slice OSDG-1 + methodology-changelog MCFS-1 count reconciliation (12 exempt / 22 sites). Parallel **slice-094** (parked at critique) must take **v0.80.0** + reconcile AVFS/MCFS/TVFS/OSDG when it builds — and now also sees 095's triage/build-slice/changelog edits on master (second-merger checklist in design.md §Sequencing).
- **Next immediate step**: `/validate-slice` → `/reflect` → `/commit-slice --merge`.
- **Discovered (logged in drift-log.md, for follow-up)**: triage/SKILL.md malformed nested ```` ```markdown ```` fence (~:142) — STILL OPEN (this round exempted the surfaced :179 but did NOT repair the template fence; :163 stays fence-hidden); an R-15 archive-path fragility in test_external_vault_adr_and_risk.py (fixed in-place).

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — note: §Sequencing says "v0.80.0" but BUILT as **v0.79.0** (user choice at build gate; logged in build-log Events)
- [critique.md](critique.md) — NEEDS-FIXES (design-Critic 2B/3M/2m, TRI-1 user-ratified)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic +M-add-1/M-add-2)
- [build-log.md](build-log.md) — SHIPPED (full Events trail of the build + forward-sync + fan-out fixes)
- [code-review.md](code-review.md) — FINDINGS 0B/3M/4m (advisory; the 3 majors + proposed fixes)
- [validation.md](validation.md) — PASS (5/5 ACs, VAL-1 clean, WS-1/ETC-1 n/a, shippability 101/101)
- [reflection.md](reflection.md) — pending
