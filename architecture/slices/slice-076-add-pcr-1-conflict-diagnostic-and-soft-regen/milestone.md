---
slice: slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen
stage: build
updated: 2026-05-28
next-action: Phase E (SKILL.md edit at sub-step 2.5 + v0.73.0 methodology-changelog entry + ADR-069 forward-sync + shippability row #76). Phase D (mid-slice smoke gate) was intentionally folded into Phase E since the smoke-gate assertions (rule entry present + ADR exists + diagnostic prose + entry-pin tests collectable) require Phase E artifacts to be meaningful. Resume from worktree C:/Users/sshub/ai_sdlc-wt/slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen.
risk-tier: medium
critic-required: true
---

# Milestone: slice-076 add-pcr-1-conflict-diagnostic-and-soft-regen

**Stage**: build (Phases A+B+C complete; Phase D folded into Phase E; resume Phase E)
**Next action**: Phase E — SKILL.md edit at Step 5b sub-step 2.5 + v0.73.0 changelog entry + ADR-069 forward-sync + shippability row #76
**Updated**: 2026-05-28
**Risk tier**: medium — Critic required: **yes** (touches in-house methodology surfaces `skills/commit-slice/SKILL.md` + mints new rule PCR-1 + new ADR-069; mandatory-Critic trigger fires)

## Progress

- [x] /slice — 2026-05-28
- [x] /design-slice — 2026-05-28
- [x] /critique — 2026-05-28 — NEEDS-FIXES (4B / 7M / 5m; ACCEPTED-FIXED dispositions applied to design + ADR + mission-brief)
- [x] /critique-review — 2026-05-28 — EXTEND (0 suspicious / 5 missed / 1 severity-adjustment; all 5 M-add ACCEPTED-FIXED at TRI-1)
- [x] TRI-1 user ratification — 2026-05-28 — final verdict NEEDS-FIXES (16 ACCEPTED-FIXED + 2 ACCEPTED-PENDING + 1 OVERRIDDEN + 5 M-add ACCEPTED-FIXED = 19 dispositioned findings; 2 ACCEPTED-PENDING apply at /build-slice Phase A: M2 stage-missing catch + m5 R-21 risk-register entry)
- [ ] /build-slice — IN PROGRESS: Phases A+B+C complete (HEAD fc3358e + Phase C uncommitted). TF-1 plan: 25 PASSING / 6 WRITTEN-FAILING (all Phase E+F) / 1 PENDING (manual end-to-end). Full pytest: 1028/1036 PASS; 6 failures are Phase E+F deliverables + 2 are pre-existing Phase-A skeleton-without-registration audits (resolve at Phase F 5-inventory bump). Phases E-G PENDING (D folded into E).
- [ ] /code-review (CRSI-1 v1 walking-skeleton; advisory-only post-build)
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Phase B complete. 28 PCR-1 tests authored across 9 new test files + 3 v0.73.0 entry-pin tests appended to existing `test_methodology_changelog.py`. Test scaffold is genuinely WRITTEN-FAILING (NotImplementedError from Phase A skeleton). R-21 latent bug (`### R-21` → `## R-21` heading) fixed in-band.

Ready for `/build-slice` Phase C: implement the 10 helper functions in `tools/parallel_conflict_resolver.py` per design.md § Components touched.

**Design summary**:
- 3-class taxonomy (SOFT / VAULT_CLAIM / HARD; UNKNOWN + MIXED fail-closed) declared inline in ADR-069 § Decision per /design-slice Step 2 clarifying ask
- SOFT file-set = `{architecture/slice-queue.md, architecture/shippability.md}` (**2 files** post /critique B3 ACCEPTED-FIXED; `_index.md` dropped because `/archive`'s regen is Haiku-LLM-dispatched per COST-1; `methodology-changelog.md` deliberately HARD per /design-slice clarifying ask 1)
- New helper `tools/parallel_conflict_resolver.py` (~400 LOC est.) with library API (diagnose_conflict / classify_conflict / resolve_soft_conflict) + CLI (--diagnose / --classify / --resolve-soft / --json)
- `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 Conflict path strictly additive: PCR-1 branch inserted BEFORE existing SOAD-1 STOP; existing 3-option ask + `git rebase --abort` recovery hint preserved verbatim
- New audit log `architecture/parallel-conflict-resolution-log.md` (lazy-created; append-only; mirrors critic-calibration-log.md pattern) per /design-slice Step 2 clarifying ask
- VAULT_CLAIM + HARD + MIXED classes declared and reserved; resolution paths deferred to PCR-2 / slice-077
- ADR-069 reversibility: **expensive** (5+ surface revert + SUP-1 chain; not irreversible)
- MEPD-1 (a) rule path; PMI-1 5-leg atomic bump 0.72.0 → 0.73.0; BC-PROJ-10 paired-pin tests; BC-PROJ-9 5-inventory for new tool module

Closes the 5-session parallel-slice deadlock-on-soft-conflict gap surfaced 2026-05-28 by minting PCR-1 (parallel-conflict-resolution v1) — first rule on the parallel-conflict-resolution axis, sibling to PSQ-3 but distinct layer (PSQ-3 = detect; PCR-1 = resolve). Ships:

1. PCR-1 rule + 3-class taxonomy (SOFT / VAULT_CLAIM / HARD) + ADR-069
2. Enhanced full-detail diagnostic at /commit-slice Step 5b sub-step 2.5 conflict-STOP
3. Soft-conflict auto-regen path — **2 canonical files** (slice-queue.md, shippability.md) per /critique B2 + B3 ACCEPTED-FIXED (`_index.md` dropped: `/archive` Haiku-LLM-dispatched per COST-1; `methodology-changelog.md` dropped: PMI-1 atomic-bump risk per /design-slice clarifying answer)
4. New helper `tools/parallel_conflict_resolver.py` with library API + CLI
5. PMI-1 5-part atomic bump 0.72.0 → 0.73.0

Defers VAULT_CLAIM + HARD resolution (including Critic stack on resolution) to **PCR-2 / slice-077**.

## Re-scoping history

This slice was scaffolded 3× in succession during the 2026-05-28 conversation:
- Initial scaffold (commit `2c91238`): `slice-076-bundle-074-code-critic-cleanup` — close P1.1 + P3.10 + slice-074 m1-m5 footguns
- Re-scoped to `slice-076-add-slice-pick-skill` (uncommitted) — auto-pick ergonomics
- Final scope (this version): `slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen` — conflict-resolution v1 (more critical than pick ergonomics; pick ergonomics defers to slice-078)

The bundle-074-code-critic-cleanup work is re-queued at this slice's scaffold; ships at slice-079+ unless empirical refutation surfaces in the interim.

## On resume

- **Last completed action**: /build-slice Phase C (tools/parallel_conflict_resolver.py full impl — ~600 LOC across 11 functions + _SoftResolutionError + helpers; mission-brief TF-1 plan flipped 18 rows WRITTEN-FAILING → PASSING; build-log events appended; corrected test_overlay_claims_on_queue_text.py fixtures to real `- **Claimed-by:**` format).
- **Current work**: none — Phase C about to be committed.
- **Next immediate step**: `/build-slice` Phase E — (1) edit skills/commit-slice/SKILL.md Step 5b sub-step 2.5 to insert PCR-1 resolver dispatch BEFORE existing SOAD-1 STOP (mirror PSQ-3 prose-pin precedent); (2) append v0.73.0 entry to methodology-changelog.md (PCR-1 + ADR-069 + parallel-conflict-resolution + mints a new rule + 5-part PMI-1 atomic bump + Rule reference); (3) add shippability row #76 with PCR-1 + ADR-069 + paired-pin test names + parallel_conflict_resolver substring; (4) OSDG-1 forward-sync of commit-slice SKILL.md to installed copy at ~/.claude/skills/commit-slice/SKILL.md. Phase D mid-slice smoke folded into Phase E (smoke-gate assertions per mission-brief.md L107-127 require Phase E artifacts). After Phase E lands all 6 SKILL-prose + changelog + shippability tests should PASS, leaving only the 5-inventory + version-sync tests for Phase F.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — pending
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending (CRSI-1 v1 advisory)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
