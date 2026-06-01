---
slice: slice-097-harden-skill-driven-vault-rewrites
stage: complete
updated: 2026-06-01
next-action: none (slice complete) — run /commit-slice to generate the audit-grade commit
risk-tier: high
critic-required: true
---

# Milestone: slice-097 harden-skill-driven-vault-rewrites

**Stage**: complete
**Next action**: run `/commit-slice` to generate the audit-grade commit (+ `--merge` to integrate + tear down the worktree)
**Updated**: 2026-06-01
**Risk tier**: high — Critic required: yes (write-safety/data-integrity + in-house methodology surfaces: `tools/**/*.py` + `skills/*/SKILL.md`)
**Worktree**: `C:/Users/sshub/ai_sdlc-wt/slice-097-harden-skill-driven-vault-rewrites` on branch `slice/097-harden-skill-driven-vault-rewrites` (BRANCH-2; scaffolding commit bb8c05b)

## Progress

- [x] /slice — 2026-06-01
- [x] /design-slice — 2026-06-01
- [x] /critique — 2026-06-01 — NEEDS-FIXES (3-Critic stack: design-Critic 3B/3M/2m + meta-Critic EXTEND +1B/+1M/+3m; all VALIDATED, zero suspicious)
- [x] /build-slice — 2026-06-01 — SHIPPED (6/6 tasks; mid-slice smoke PASS; all Step-6 gates clean)
- [x] /code-review — 2026-06-01 — 6 findings (2B/2M/2m), ALL VALIDATED + ACCEPTED-FIXED in-slice (advisory v1)
- [x] /validate-slice — 2026-06-01 — PASS (5/5 ACs; VAL-1 0/0; shippability 103/103; multi-instance N=6 spawn proof)
- [x] /reflect — 2026-06-01 — R-32 narrowed via dogfooded vault_edit rewrite on the real 137KB CRLF risk-register.md (m-add-2 live-fire); lessons + shippability #105 appended; slice archived

## Current focus

Slice shipped + reflected. R-32's 3rd/final write-safety sub-class CLOSED; R-32 stays `mitigating` (residual = flip mechanics only). Live-fire dogfood of `vault_edit rewrite` on the real CRLF risk-register.md succeeded byte-faithfully. Run `/commit-slice --merge` to integrate + tear down the worktree.

## Build plan (approved 2026-06-01)

1. `_vault_write.py`: `safe_rewrite_text` + `_normalize_eol` (CRLF→LF only) + `StaleVaultBaseError` + units (B1, M-add-1)
2. `vault_edit.py`: `rewrite`+`read` subcommands, binary `--base-file`, docstring fix + CLI tests (B1, M2)
3. NEW `test_skill_vault_rewrite_concurrency.py`: spawn+barrier CAS proof, CRLF fixture, mutation arm (M1)
   → **MID-SLICE SMOKE GATE** (~50%): proof passes (0 lost CAS / ≥1 naive) + units
4. `skill_vault_write_safety_audit.py`: op-class-aware (retire bare token), enum/allowlist 12→3 + tests (B2, B-add-1, m1)
5. Route 9 SKILL.md sites + forward-sync installs (B3, m-add-1/2/3)
6. R-32 update (m2) + drift-check + all Step-6 audits + full suite → /validate-slice

## Current focus

Critique complete, verdict **NEEDS-FIXES** (user-ratified TRI-1, all 13 dispositions as drafted). Dual stack worked: design-Critic caught B1 (CRLF byte-exact CAS false-conflict + corruption), B2 (audit can't tell rewrite- from append-routing), B3 (Haiku-subagent has no home for the CAS loop); meta-Critic EXTEND caught **B-add-1** (my B2 fix didn't sever the bare-`tools.vault_edit` flat-OR — a fresh-claim catch) + M-add-1 (`_normalize_eol` silent-overwrite edge). Design.md + ADR-088 carry all fix-deltas.

**Build fix-list (4 ACCEPTED-PENDING):** B1 EOL-normalized-compare + EOL-preserving-write (vs real CRLF `_index.md`/`risk-register.md`); B2/B-add-1 op-class discriminator (retire bare token, classify subcommand, asymmetric verdict, bare-token-severance adversarial proof); M-add-1 `_normalize_eol` = CRLF→LF-only both-direction tests. Plus the ACCEPTED-FIXED items already in design.

## On resume

- **Last completed action**: /validate-slice — PASS (5/5 ACs with real-CLI evidence; VAL-1 0 secrets/0 imports; shippability 103/103; multi-instance N=6 spawn proof)
- **Current work**: none — build+fix artifacts uncommitted in the worktree (committed by /commit-slice after /reflect)
- **Next immediate step**: run `/validate-slice`, then /reflect → /commit-slice --merge
- **code-review fixes applied**: B1 `read --out-file` (no PowerShell `>` byte corruption) + concurrency worker uses it; M1 distinct per-target archive base files; M2 reflect:56 "Rewrite … in place" + "rewrite" added to `_DIRECTIVE_VERBS` (now detected + rewrite-class) + regression test; m1 reflect:143 de-staled; m2 docstring
- **Deferred to /reflect**: R-32 register-note narrowing + `_index.md` regen via `vault_edit rewrite` (the m-add-2 live-fire dogfood on the real CRLF files)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-088](../../decisions/ADR-088-close-skill-rmw-vault-writes-via-cas.md)
- [critique.md](critique.md) — NEEDS-FIXES (8 findings, triaged)
- [critique-review.md](critique-review.md) — EXTEND (5 missed findings)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
