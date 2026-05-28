---
slice: slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen
stage: code-review
updated: 2026-05-29
next-action: run `/code-review` (CRSI-1 v1 walking-skeleton advisory-only post-build; auto-advance per PCA-1 on clean /build-slice completion). /build-slice declared done at Phase G: 1036/1036 pytest PASS + 75/75 shippability PASS + 18 Step-6 audits clean (modulo 2 BC-1 defer-with-rationale per slice-074 N=7 cumulative prose-vs-automation + keyword-false-positive class) + APED-1 4-predicate battery 28/28 expected. After /code-review: /validate-slice then /reflect.
risk-tier: medium
critic-required: true
---

# Milestone: slice-076 add-pcr-1-conflict-diagnostic-and-soft-regen

**Stage**: code-review (all 7 /build-slice phases A-G complete; PCA-1 auto-advance to /code-review)
**Next action**: run `/code-review` (CRSI-1 v1 walking-skeleton advisory-only)
**Updated**: 2026-05-28
**Risk tier**: medium — Critic required: **yes** (touches in-house methodology surfaces `skills/commit-slice/SKILL.md` + mints new rule PCR-1 + new ADR-069; mandatory-Critic trigger fires)

## Progress

- [x] /slice — 2026-05-28
- [x] /design-slice — 2026-05-28
- [x] /critique — 2026-05-28 — NEEDS-FIXES (4B / 7M / 5m; ACCEPTED-FIXED dispositions applied to design + ADR + mission-brief)
- [x] /critique-review — 2026-05-28 — EXTEND (0 suspicious / 5 missed / 1 severity-adjustment; all 5 M-add ACCEPTED-FIXED at TRI-1)
- [x] TRI-1 user ratification — 2026-05-28 — final verdict NEEDS-FIXES (16 ACCEPTED-FIXED + 2 ACCEPTED-PENDING + 1 OVERRIDDEN + 5 M-add ACCEPTED-FIXED = 19 dispositioned findings; 2 ACCEPTED-PENDING apply at /build-slice Phase A: M2 stage-missing catch + m5 R-21 risk-register entry)
- [x] /build-slice — 2026-05-29 — SHIPPED-WITH-DEFERRALS (2 BC-1 Important defer-with-rationale per slice-074 N=7 cumulative). TF-1 plan: 31/31 PASSING; full pytest 1036/1036; shippability 75/75; 18 Step-6 audits clean; APED-1 4-predicate battery 28/28 expected.
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

- **Last completed action**: /build-slice Phase F (PMI-1 5-leg atomic bump 0.72.0 → 0.73.0 + BC-PROJ-9 5-inventory bump 30 → 31 + TVFS-1 venv refresh + MCFS-1 forward-sync + stale-test-deletion `test_version_files_synchronized_at_v_0_72_0` per version-sync convention + R-10 stale-pin fix in slice-073 row #73 machine-cmd + 2 in-band Phase-E pipe-leakage fixes in shippability row #75).
- **Current work**: none — Phase F about to be committed.
- **Next immediate step**: `/build-slice` Phase G — 14+ Step-6 audit gauntlet (TF-1 + WIRE-1 + BC-1 + RR-1 + PMI-1 + CAD-1 + INST-1 + UTF8-STDOUT-1 + CRP-1 + PCA-1 + BCI-1 + MCFS-1 + STP-1 + AVFS-1 + TVFS-1 + NAW-1 + BRANCH-2 + LINT-MOCK-1) + APED-1 empirical battery on 4 minted predicates (_SOFT_FILE_SET membership against the 11-input synthetic battery per mission-brief must-not-defer + classify_conflict 5-way classification logic + _extract_claim_diff parser predicate + _merge_shippability row-union predicate) + build-log Summary section finalize (Plan executed + Mid-slice smoke gate + Pre-finish gate + Deferrals + Design deviations + Files changed). After Phase G, /build-slice declares done + hands off via PCA-1 auto-advance to /code-review (CRSI-1 v1 walking-skeleton advisory-only) then /validate-slice then /reflect.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — pending
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending (CRSI-1 v1 advisory)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
