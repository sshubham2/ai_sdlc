# Reflection: Slice 073 add-rebase-and-conflict-discipline

**Date**: 2026-05-28
**Shipped**: YES

## Validated

- **PSQ-3 minted as the third rule on the parallel-slice family axis** — sibling to PSQ-1 (queue-output / ADR-064) + PSQ-2 (claim-machinery / ADR-067) + BRANCH-2 (worktree-isolation / ADR-063); first rule on the *rebase-discipline* axis. Validated by ADR-068 + methodology-changelog v0.72.0 entry + structural-pin tests landing in tests/methodology/test_commit_slice_skill_rebase_flag.py.
- **`/commit-slice --merge` Step 5b sub-step 2.5 contract holds** — validated by 5 structural-pin tests (test_step_5b_contains_git_rebase_invocation + _rebase_precedes_no_ff_merge + _rebase_target_resolved_via_canonical_2_step + _conflict_stops_with_porcelain_u_entries + _conflict_surfaces_git_rebase_abort_hint). The `git rebase <default>` literal appears in Step 5b BEFORE `git merge --no-ff` (ordering invariant); the canonical 2-step default-branch resolution is present; conflict-STOP surfaces `git status --porcelain` U-entries + `git rebase --abort` recovery hint.
- **5-part PMI-1 atomic bump 0.71.0 → 0.72.0** — validated by test_version_files_synchronized_at_v_0_72_0 (legs 1-4) + AVFS-1 audit (leg 5 installed `~/.claude/ai-sdlc-VERSION`) + TVFS-1 audit (post-bump pip install upgraded ai-sdlc-tools to 0.72.0).
- **BC-PROJ-10 paired-pin discipline** — validated by 2 paired-pin tests (test_v_0_72_0_psq_3_entry_present_in_repo + test_v_0_72_0_psq_3_shippability_consumer_propagation) + shippability row #73 (citing both paired-pin tests + the structural-pin test module).
- **Three-Critic stack value-validation extends to N=9 cumulative** (slice-063 → slice-073 inclusive) — first-Critic caught 16 design defects (6B/6M/4m all VALID); meta-Critic surfaced 6 additional missed findings (2M + 4m all VALID); code-Critic surfaced 4 code-level findings (1M + 3m all VALID). Each Critic surfaced a structurally-distinct defect class the others could not reach.
- **Scope narrowing held at /critique** — AC1 narrowed from --merge + --sync-after-pr → --merge only; AC3 narrowed from "audit-tool pin" → "structural-pin tests only (no new audit-tool module — `git rebase` IS the runtime gate)". Both narrowings ratified at TRI-1; both held through /build-slice + /code-review.
- **R-20 cp-r workaround applied successfully** — N=8 cumulative manual `cp -r diagnose-out/ graphify-out/` at /build-slice prerequisite check; vault state available in worktree for VAL-1 + shippability runner + BCR-1 round-trip surface (none triggered this slice).
- **Switch-commit-switch-worktree pattern N=4 cumulative** (slice-070/071/072/073) — canonical post-vault-in-git sequence for handling dirty pre-build state on master is stable; codification in BRANCH-2 SKILL.md remains a slice-074+ candidate.

## Corrected

- **Design narrowed twice from mission-brief at /critique** (B2 + B3 ACCEPTED-FIXED in-band before /build-slice) — already corrected via mission-brief.md + design.md + ADR-068 harmonization. Not a post-build correction; the corrections landed before code was written. Documented in critique.md Triage section.
- **Builder fix-block M4 sweep was INCOMPLETE at /critique** — meta-Critic at /critique-review caught two ADR-068 sites (L29 + L53) still carrying the slice-064 precedent appeal that M4 retired. ALREADY-FIXED-AT-/critique-review (M-add-1 ACCEPTED-FIXED in-band). Not a post-build correction; this was the canonical N+1 regression caught at the meta-Critic layer.
- **Stale "5-7 tests" anchor in design.md L149 + ADR-068 L63** caught by Builder during /critique-review fix-block preparation (before meta-Critic spawn) — design.md + ADR-068 harmonized to enumerate the 5 specific test function names. Not a post-build correction.
- **No vault file corrections** — code IS the truth (thin vault). All design-time corrections landed in-band during /critique + /critique-review. Post-build reality confirmed design verbatim.

## Discovered

- **TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions pattern extends to N=7 cumulative** (slice-062/064/067/070/071/072/073) — the canonical instance on this slice: Builder applied M4's slice-064-precedent retirement at design.md L156 cleanly but missed two ADR-068 sites carrying the same defect class. Meta-Critic caught at /critique-review. **The pattern is now empirically stable across 7 consecutive slices — `/critic-calibrate` slice-074+ proposal target is severely overdue.** Proposed Critic-prompt addition: "after applying any fix that retires a named precedent or anchor, perform a `grep -n <precedent-name>` across ALL three surfaces (mission-brief.md + design.md + new ADR) and verify zero stale citations remain."
- **Code-Critic M1: `2>/dev/null` cross-spec parity violation between sub-step 2.5 (redirected; canonical) and sub-step 3 (unredirected; pre-existing divergent leg)** — slice-073 inherited the canonical form from Step 5d sub-step 2 (also redirected) but did not retroactively harmonize sub-step 3. design.md §Contracts L74 "MUST use the same 2-step pattern" violated at byte level. Real defect with strict-mode / CI-stderr-fail edge cases; deferred to slice-074+ bundle per voluntary-restraint discipline N=14 cumulative.
- **R-20 cp-r tax extends to N=8 cumulative across TWO surfaces** (slice-067 N=3 / slice-068 N=4 / slice-069 N=5 / slice-070 N=5 / slice-071 N=6 / slice-072 N=7 / slice-073 N=8) — pattern is now structurally stable across 7 consecutive post-vault-in-git slices. User-flagged at slice-071 "we need a better solution." **Slice-074+ structural-fix nomination via R-20 candidate (a) codify-cp-r-in-BRANCH-2-SKILL.md is severely overdue; each subsequent slice adds cumulative pain.** Three candidate fix classes carried forward to risk-register: (a) codify cp-r in BRANCH-2 SKILL.md `## Prerequisite check ### Branch state`; (b) post-/build-slice symlink; (c) un-gitignore derived dirs.
- **BC-1 BC-GLOBAL-2 prose-vs-automation false-positive class extends to N=5 cumulative** (slice-069/070/071/072/073) — the BC-GLOBAL-2 keyword-trigger fires on PSQ-3 prose mentioning `git rebase --abort` recovery hint (documentation), not on git-mutate-then-revert automation. Pattern is now well past the N=3 promotion threshold; `/critic-calibrate` slice-074+ proposal target: BC-1 negative-anchor refinement (e.g., negative anchors for `recovery hint`, `prose mentioning`, `ADR §Reversibility`, `documented recovery path`).
- **Three /critic-calibrate-fit signals now genuinely overdue at the same time**: (1) TPHD-1 sub-mode (a) N=7 cumulative; (2) BC-1 BC-GLOBAL-2 prose-vs-automation N=5 cumulative; (3) AC-count > 5 N=2 promotion of slice-067 pattern (slice-072 has 6 ACs; new-mechanism mints with paired-pin meta-AC + PMI-1 atomic-bump leg meta-AC genuinely need 6 ACs). **`/critic-calibrate` is the strongest slice-074 candidate.**
- **Voluntary-restraint discipline extends to N=14 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073) — code-Critic v1 advisory findings consistently route to next-slice bundled cleanup; structurally stable across 8 consecutive cycles. Next bundled-cleanup-at-N+1 opportunity is slice-NNN-bundle-073-code-critic-cleanup (~4 findings: M1 + m1 + m2 + m3 from code-review.md).
- **Code-Critic m2: shippability row #73 says "3-Critic stack N=10 cumulative" but predecessor v0.71.0 anchor at methodology-changelog L51 says N=8 through slice-072; slice-073 should be N=9** — off-by-one count claim. Documentary only; does NOT affect runtime behavior. The Validated bullet above states the correct N=9. **Update needed at slice-074+ bundle:** shippability row #73 N=10 → N=9.
- **AVFS-1 leg 5 manual sync workaround** — installed `~/.claude/ai-sdlc-VERSION` was synced via PowerShell `Copy-Item` (not via INSTALL.md `$PY -m pip install --upgrade .` which only bumps the tools package). This is the documented Phase F1 / F2 forward-sync pattern; not a defect. The 5-part PMI-1 leg 5 is environment-dependent and needs explicit manual sync at every version-bumping slice. No risk-register addition needed.

## Deferred

- **Code-Critic M1 + m1 + m2 + m3** (4 findings) → slice-074+ `slice-NNN-bundle-073-code-critic-cleanup` per voluntary-restraint discipline N=14 cumulative + CRSI-1 v1 walking-skeleton advisory-only.
- **R-20 cp-r tax structural fix** → slice-074+ structural-fix nomination via R-20 candidate (a) (most likely path: codify-cp-r-in-BRANCH-2-SKILL.md). **SEVERELY OVERDUE** at N=8 cumulative.
- **`/critic-calibrate` proposal target** → slice-074+ run with three accumulated signals (TPHD-1 N=7 + BC-GLOBAL-2 N=5 + AC-count N=2). **The strongest slice-074 candidate.**
- **Closing the `--merge` Step 5b sub-step 3 worktree-collision STOP asymmetry** (design.md §"Worktree-vs-main-tree interaction contract" tracks this as out-of-scope this slice) → slice-074+ `/critic-calibrate` candidate.
- **Retrofit existing 6 raw `(yes/no)` confirmation prompts in /commit-slice to SOAD-1 form** → slice-074+ `/critic-calibrate` candidate (per design.md §"SOAD-1 justification" — scope-creep tracked as future candidate).
- **`--push` time rebase (PSQ-4)** + **`--rebase-merges` strategy (PSQ-5)** + **merge-driver registration (PSQ-6)** → enumerated in ADR-068 §"Future flexibility"; deferred until real user demand emerges.
- **BC-1 BC-GLOBAL-2 defer-with-rationale** → routine; documented in build-log.md DEFERRAL line; resolution path is the `/critic-calibrate` slice-074+ proposal.

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` + `critique-review.md` + `code-review.md` + reality observed during build/validate:

**First-Critic (design-Critic) findings — 16 total**:
- B1 (PTFCD-1 phantom test-file directory): **VALIDATED** — disposition ACCEPTED-FIXED; filesystem-verified `tests/skills/commit_slice/` did not exist; convention is `tests/methodology/test_commit_slice_skill_*_flag.py`.
- B2 (AC3 design-narrowing not back-propagated): **VALIDATED** — disposition ACCEPTED-FIXED.
- B3 (AC1 scope contradiction): **VALIDATED** — disposition ACCEPTED-FIXED.
- B4 (Must-not-defer items demand audit module): **VALIDATED** — disposition ACCEPTED-FIXED.
- B5 (paired-pin name divergence _in_changelog vs _in_repo): **VALIDATED** — disposition ACCEPTED-FIXED; convention is `_in_repo`.
- B6 (ADR-068 filename divergence): **VALIDATED** — disposition ACCEPTED-FIXED.
- M1 (worktree-vs-main-tree collision unaddressed): **VALIDATED** — disposition ACCEPTED-FIXED; but Builder fix introduced citation error caught at meta-Critic as M-add-2.
- M2 (conflict-STOP re-entry semantics undefined): **VALIDATED** — disposition ACCEPTED-FIXED.
- M3 (SOAD-1 mid-skill unjustified): **VALIDATED** — disposition ACCEPTED-FIXED.
- M4 (slice-064 precedent claim misleading): **VALIDATED** — disposition ACCEPTED-FIXED; but Builder fix-block was INCOMPLETE — meta-Critic caught M-add-1 (two ADR-068 sites still carried the appeal).
- M5 (Verification plan row 3 cites stale audit): **VALIDATED** — disposition ACCEPTED-FIXED.
- M6 (ADR-068 option (c) operational path undefined): **VALIDATED** — disposition ACCEPTED-FIXED.
- m1-m4 (risk-retired overshoot / mid-slice smoke gate / pre-finish 14+ count / 5-7 test enumeration): **ALL VALIDATED** — all disposition ACCEPTED-FIXED.

**Meta-Critic (/critique-review) missed findings — 6 total**:
- M-add-1 (M4 sweep regression — ADR-068 L29 + L53 stale precedent appeal): **VALIDATED** — disposition ACCEPTED-FIXED in-band; the canonical TPHD-1 sub-mode (a) N=7 cumulative instance.
- M-add-2 (M1 fix introduced citation error — SKILL.md L259 misattribution): **VALIDATED** — disposition ACCEPTED-FIXED in-band.
- m-add-1 (off-by-one "5 confirmation sites" should be "6"): **VALIDATED** — disposition ACCEPTED-FIXED in-band.
- m-add-2 (stale "open to /critique review" post-/critique prose): **VALIDATED** — disposition ACCEPTED-FIXED in-band.
- m-add-3 (ADR-068 L37 N=10 vs 11-item enumeration): **VALIDATED** — disposition ACCEPTED-FIXED in-band.
- m-add-4 (fast-forward no-op framing inverted): **VALIDATED** — disposition ACCEPTED-FIXED in-band.

**Code-Critic findings — 4 total (advisory)**:
- M1 (`2>/dev/null` cross-spec parity violation): **VALIDATED** — disposition DEFERRED to slice-074+ bundle; real defect, valid in scope.
- m1 (co-occurrence-not-co-location risk on U-entries test): **VALIDATED** — disposition DEFERRED.
- m2 (3-Critic stack N=10 off-by-one count claim): **VALIDATED** — disposition DEFERRED; real documentary drift.
- m3 (`git rebase --continue` not pinned by any structural-pin test): **VALIDATED** — disposition DEFERRED; real structural-pin gap.

**Missed by Critic**: None this slice. The 3-Critic stack caught every defect surfacing at build/validate; no defects post-validate surfaced unflagged. The N=9 cumulative complementarity of the 3-Critic stack continues to be the highest-signal review surface for in-house methodology slices.

**Pattern**:
- **TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions: N=7 cumulative meta-Critic catches** (slice-062/064/067/070/071/072/073). First-Critic consistently misses peripheral prose anchors in fix-block sweeps; meta-Critic consistently catches them. `/critic-calibrate` proposal target: instruct first-Critic to perform a `grep -n <retired-precedent-name>` sweep across mission-brief + design + new-ADR after authoring each fix disposition that retires a named precedent or anchor.
- **3-Critic stack value-validation N=9 cumulative**: design-Critic catches conceptual + ADR identifier + citation hygiene + missing-cases; meta-Critic catches Builder fix-block sweep gaps + sibling-cell-survival regressions + count-vs-enumeration drift; code-Critic catches cross-spec parity at byte level + ordering invariants + structural-pin gaps. Each Critic finds a different class. Do NOT collapse the stack.
- **Zero FALSE-ALARMs this slice**. All 26 findings (16 first-Critic + 6 meta-Critic + 4 code-Critic) reality-confirmed.

## Lessons for next slice

- **`/critic-calibrate` is now genuinely overdue at three simultaneous signals**: TPHD-1 sub-mode (a) N=7 + BC-GLOBAL-2 prose-vs-automation N=5 + AC-count > 5 N=2. **`/critic-calibrate` is the strongest slice-074 candidate.**
- **R-20 cp-r tax structural fix is severely overdue at N=8 cumulative**. User-flagged at slice-071; 3 candidate fix classes enumerated; ~6 hours of compounding manual friction across slices 067-073. **Slice-074 candidate: codify-cp-r-in-BRANCH-2-SKILL.md (R-20 candidate (a)).**
- **For slices that mint a new RULE-ID + inherit a canonical form from a sibling site**, run a `grep -n <canonical-form-literal>` across ALL sibling sites (here: Step 5b sub-step 3 + Step 5d sub-step 2 vs sub-step 2.5) and verify byte-level identity. The slice-073 code-Critic M1 catch (`2>/dev/null` divergence) shows the design-Critic stack cannot reach this — only post-code code-Critic can. APED-1 scope-extension class N=3 cumulative.
- **The "scope-narrowing in design.md but mission-brief not back-propagated" pattern is the canonical TPHD-1 sub-mode (a) trigger** — 14 of 16 first-Critic findings on this slice fell in this single class. Future slices that narrow scope at design time should immediately edit mission-brief.md in the same fix block (sub-mode (a)) — leave nothing for /critique to catch.
- **Bundled-cleanup-at-N+1 disposition shape is reusable**. Current accumulated backlog for slice-NNN-bundle-073: 4 code-Critic findings (M1 + m1 + m2 + m3). If next slice is /critic-calibrate, the bundled cleanup waits until slice-075+; if next slice is R-20 structural fix, same deferral. Voluntary-restraint discipline holds.

## Vault updates made (thin vault — small list)

- [[risk-register.md]] — R-20 cumulative count updated to **N=8 across two surfaces**; structural-fix nomination remains active (no status change; still `mitigating`)
- [[methodology-changelog.md]] — new `## v0.72.0 — 2026-05-28` entry minting PSQ-3 (already landed at /build-slice Phase C)
- [[architecture/shippability.md]] — row #73 added citing PSQ-3 + ADR-068 + 2 paired-pin tests + structural-pin test module (already landed at /build-slice Phase C3)
- [[architecture/decisions/ADR-068-mint-psq-3-rebase-and-conflict-discipline.md]] — NEW (created during scaffolding; harmonized at /critique + /critique-review)
- This slice's [[design.md]] — no post-build corrections; all design narrowings landed in-band at /critique
- [[VERSION]] / [[plugin.yaml]] / [[pyproject.toml]] — 5-part PMI-1 atomic bump 0.71.0 → 0.72.0
- Forward-syncs to `~/.claude/`: methodology-changelog.md (MCFS-1) + skills/commit-slice/SKILL.md (OSDG-1) + ai-sdlc-VERSION (AVFS-1) + installed ai-sdlc-tools 0.72.0 (TVFS-1)

NOT a BCR-1 round-trip — zero `**Closes:** SC-NNN` sentinels in mission-brief.md or this reflection.md. The slice is risk-register-driven (PSQ-3 standing nomination from slice-067 + slice-072 reflections), not backlog-driven.
