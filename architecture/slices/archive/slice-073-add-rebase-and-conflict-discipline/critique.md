# Critique: Slice 073 add-rebase-and-conflict-discipline

**Critic reviewed**: mission-brief.md, design.md, ADR-068-mint-psq-3-rebase-and-conflict-discipline.md
**Date**: 2026-05-27
**Result**: BLOCKED (pre-triage; expected NEEDS-FIXES or CLEAN post-Builder-fix-block)

## Summary

Sixteen findings: **6 Blockers + 6 Majors + 4 minors**. The dominant pattern is TPHD-1 sub-mode (a) cross-doc harmonization caught at first-Critic time (the design narrowed scope in two places but the mission-brief was not back-propagated — leaving the test-first plan, Must-not-defer items, Verification plan, Mid-slice smoke gate, AC1 prose, AC3 prose, ADR filename citation, and paired-pin test name all stale). 14 of 16 findings cluster on this single root cause; M1/M2/M3/M4/M6 are independent design-shape concerns. The aggregated-lessons N=6 cumulative TPHD-1 sub-mode (a) pattern is empirically present *before* meta-Critic this slice — first-Critic catch.

## Findings

### Blockers (must address before /build-slice)

#### B1: PTFCD-1 phantom test-file directory — `tests/skills/commit_slice/` does not exist on disk

- **Claim under review** (mission-brief.md L30-32, test-first plan): `tests/skills/commit_slice/test_commit_slice_skill.py` cited as test path for 3 AC1+AC2 rows.
- **Issue**: The directory `tests/skills/commit_slice/` does not exist on disk. The actual convention for commit-slice tests is the family at `tests/methodology/test_commit_slice_skill_*_flag.py` (verified: `tests/methodology/test_commit_slice_skill_merge_flag.py`, `_push_flag.py`, `_sync_after_pr_flag.py`, `_drift.py` all exist). design.md L34-38 correctly cites `tests/methodology/test_commit_slice_skill_rebase_flag.py`, but the mission-brief test-first plan still points at the phantom `tests/skills/commit_slice/` directory. PTFCD-1 violation; would trigger `missing-test-path-file` at `/build-slice` Step 6.
- **Evidence**: mission-brief.md L30-32; design.md L34, L37 (correct path); filesystem check confirmed no `tests/skills/commit_slice/`; existing convention at `tests/methodology/test_commit_slice_skill_*_flag.py`.
- **Proposed fix**: Update mission-brief.md L30-32 to cite `tests/methodology/test_commit_slice_skill_rebase_flag.py` matching design.md + existing convention.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L29-38 (full test-first plan rewrite — incorporates B1+B2+B3+B5+m4 in one fix block per TPHD-1 sub-mode (a) discipline).

#### B2: AC3 design narrowing not back-propagated to test-first plan — 3 cited tests reference an audit module the design eliminates

- **Claim under review**: mission-brief.md L33-35 test-first plan rows for AC3 cite `tests/methodology/test_psq_3_rebase_audit.py`; mission-brief AC3 prose at L18 also still says "pin in `tools/branch_workflow_audit.py` (or a new sibling helper)".
- **Issue**: design.md L127-130 + ADR-068 L33 explicitly remove the audit-tool module. Three test-first rows + AC3 prose still demand it; two of the rows test the audit module itself (cannot exist if no module).
- **Evidence**: mission-brief.md L18, L33-35; design.md L127-130; ADR-068 L33; design.md L11 + L96-100 wiring matrix vacuous.
- **Proposed fix**: Rewrite AC3 prose to match design narrowing; replace 3 AC3 test-first rows with structural-pin test rows pointing at `tests/methodology/test_commit_slice_skill_rebase_flag.py`.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L18 (AC3 text rewritten) + L29-38 (test-first plan rewritten).

#### B3: AC1 scope contradiction — design narrows to `--merge` only but mission-brief AC1, test-first plan row, and Must-not-defer items all still demand `--sync-after-pr` coverage

- **Claim under review**: mission-brief.md L16 AC1 says both `--merge` AND `--sync-after-pr`; test-first row L31 names `test_skill_md_sync_after_pr_mode_rebases_default_before_merge`.
- **Issue**: design.md L86 + L129 + ADR-068 L52 explicitly exclude `--sync-after-pr`. Canonical TPHD-1 sub-mode (a) defect — design narrowed scope, mission-brief not edited.
- **Evidence**: mission-brief.md L16, L31; design.md L86, L129; ADR-068 L52; milestone.md L30 acknowledges narrowing in prose but mission-brief itself not updated.
- **Proposed fix**: Rewrite AC1 to `--merge` only with explicit `--push`/`--sync-after-pr` out-of-scope pointer to design.md; delete `_sync_after_pr_` test row.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L16 (AC1 text) + L29-38 (test-first plan).

#### B4: Must-not-defer items 3 + 4 still demand an audit module the design eliminates

- **Claim under review**: mission-brief.md L54-55 "Audit injection seam preserved" + "PSQ-3 audit emits binary exit".
- **Issue**: Both items presuppose audit module; design eliminates it (design.md L92, L127-130; ADR-068 L33). TPHD-1 sub-mode (a) sibling-sweep.
- **Evidence**: mission-brief.md L54-55; design.md L92, L127-130; ADR-068 L33.
- **Proposed fix**: Delete both items; replace with structural-pin convention item.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L52-59 (Must-not-defer rewritten).

#### B5: AC4 paired-pin test name divergence — mission-brief says `_in_changelog`, design and ADR-068 say `_in_repo`

- **Claim under review**: mission-brief.md L19 + L36 use `_entry_present_in_changelog`; design.md L14 + L47 + L123 + ADR-068 L55 + L66 use `_entry_present_in_repo`; slice-072's existing precedent uses `_in_repo`.
- **Issue**: FBCD-1 sub-mode (a) cross-file naming inconsistency; the `_in_repo` form matches existing convention.
- **Evidence**: mission-brief.md L19, L36; design.md L14, L47, L123; ADR-068 L55, L66; precedent at slice-072 shippability row #72.
- **Proposed fix**: Standardize on `_in_repo` (matches existing convention); update mission-brief L19 + L36.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L19 + L29-38 (in the test-first plan rewrite).

#### B6: ADR-068 filename divergence — mission-brief cites `ADR-068-add-rebase-and-conflict-discipline.md`, actual file is `ADR-068-mint-psq-3-rebase-and-conflict-discipline.md`

- **Claim under review**: mission-brief.md L18 cites `ADR-068-add-rebase-and-conflict-discipline.md`; actual file is `ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` (design.md L51, L54 cite the extant form).
- **Issue**: PTFCD-1 file-level variant; slice-072's analogous `mint-psq-2-…` form establishes the convention.
- **Evidence**: mission-brief.md L18; filesystem check; design.md L51, L54; slice-072 ADR-067 precedent.
- **Proposed fix**: Update mission-brief.md L18 to cite `ADR-068-mint-psq-3-rebase-and-conflict-discipline.md`.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L18.

### Majors (address this slice)

#### M1: Worktree-vs-main-tree `git checkout $default` collision unaddressed

- **Claim under review**: design.md L21 says rebase runs inside the worktree; doesn't address the subsequent `git checkout $default` interaction with BRANCH-2.
- **Issue**: The existing sub-step 3 `git checkout $default` can fail when $default is checked out in the main tree (existing SKILL.md L259 STOP path). Design doesn't say rebase doesn't introduce a new edge case here, or that the existing STOP still suffices.
- **Evidence**: design.md L21, L74; SKILL.md L259; ADR-063.
- **Proposed fix**: Add paragraph to design.md §Contracts clarifying rebase preserves slice-branch checkout + existing STOP path for sub-step 3 collision still applies.
- **Builder draft**: ACCEPTED-FIXED at design.md §Contracts (paragraph added after L78).

#### M2: Conflict-STOP re-entry semantics undefined

- **Claim under review**: design.md L78 + ADR-068 L51 — option (b) "resolve conflicts manually + run `git rebase --continue` outside the skill" leaves rebase-in-progress state; what happens on re-invocation of `/commit-slice --merge` is unspecified.
- **Issue**: After manual `git rebase --continue` + re-invoke, the slice branch is at new rebased state. WT-clean guardrail passes, but does sub-step 2 try to commit again? Does sub-step 2.5 rebase again (no-op)? Edge case under Dim 2.
- **Evidence**: design.md L78; SKILL.md L172-174 sub-step 2 commit logic; ADR-068 L51.
- **Proposed fix**: Add "Re-entry semantics" paragraph to design.md §Error model specifying: WT-clean guardrail passes; sub-step 2 detects no un-staged files (build-log Files changed list already committed pre-rebase) and skips the commit; sub-step 2.5 fast-forward no-ops; flow proceeds.
- **Builder draft**: ACCEPTED-FIXED at design.md §Error model.

#### M3: Mid-skill SOAD-1 invocation is the first instance in `/commit-slice` — design doesn't justify the precedent

- **Claim under review**: design.md L78 introduces SOAD-1 structured options at conflict-STOP; existing /commit-slice uses raw `(yes/no)` confirmation prompts elsewhere.
- **Issue**: Convention asymmetry; design doesn't explain why this 3-option decision warrants SOAD-1 vs the existing yes/no shape used at 5 other confirmation sites.
- **Evidence**: skills/commit-slice/SKILL.md (0 SOAD-1 references via grep); design.md L78; ADR-068 L51; CLAUDE.md L24-29 SOAD-1 rule.
- **Proposed fix**: Add justification to design.md: SOAD-1 is the right form precisely because the conflict-STOP requires a 3-option decision tree (abort / continue-out-of-skill / cancel-merge-entirely) that doesn't model as binary yes/no — exactly SOAD-1's primary-form-of-ask scope per ADR-050. Existing yes/no prompts elsewhere are binary confirmations and stay as-is (NOT scope-creep into this slice).
- **Builder draft**: ACCEPTED-FIXED at design.md §Contracts.

#### M4: Slice-064 precedent claim misleading — slice-064 did NOT mint a new RULE-ID

- **Claim under review**: ADR-068 L33 + design.md L130 cite slice-064 as the "rule mint without new tool" precedent.
- **Issue**: slice-064 was a scope-extension (ADR-062 "mints no new rule; supersedes nothing") — applied an existing rule to a new surface. PSQ-3 IS a new-RULE-ID mint; the closer precedents (PSQ-1 / PSQ-2) BOTH minted a `tools/*.py` module. The slice-064 appeal is not apples-to-apples.
- **Evidence**: ADR-068 L33; design.md L130; slice-064 reflection L9 + ADR-062 frontmatter (no rule mint); PSQ-1 + PSQ-2 (both with new tool modules).
- **Proposed fix**: Replace the slice-064 precedent appeal with the actual rebase-specific argument: `git rebase` is a no-op fast-forward at-tip / runs cleanly behind / exits non-zero with conflict — IT IS the runtime gate; an audit module would duplicate it. Structural-pin tests on SKILL.md catch drift in the invocation analogously to how `git merge --no-ff` invocation is pinned via prose-pin tests at `test_commit_slice_skill_merge_flag.py` rather than a separate merge-audit module.
- **Builder draft**: ACCEPTED-FIXED at design.md L130 + ADR-068 L33.

#### M5: Mission-brief Verification plan row 3 still cites `$PY -m tools.branch_workflow_audit` live invocation

- **Claim under review**: mission-brief.md L46 "Live invocation via `$PY -m tools.branch_workflow_audit` (or sibling) on a constructed worktree."
- **Issue**: Same FBCD-1 sub-mode (a) class as B2 + B4 + m2. Verification of an audit that doesn't exist.
- **Evidence**: mission-brief.md L46; design.md L127-130.
- **Proposed fix**: Rewrite L46 to describe structural-pin test verification + live exercise of `/commit-slice --merge` against synthetic divergence.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L41-48 (Verification plan rewritten).

#### M6: ADR-068 option (c) "cancel slice merge entirely" operational path undefined

- **Claim under review**: design.md L78 + ADR-068 L51 option (c).
- **Issue**: What does "cancel slice merge entirely" mean operationally? `git rebase --abort` then keep branch? Force-delete via `git branch -D` (forbidden by skill critical rules)? Undefined Dim 5 contract gap.
- **Evidence**: design.md L78; ADR-068 L51; SKILL.md L181-184 (no `-D` rule).
- **Proposed fix**: Specify in design.md §Error model: option (c) means user runs `git rebase --abort` to restore pre-rebase slice branch, then either keeps the slice branch (for later re-attempt) OR manually `git branch -D slice/NNN-<name>` outside the skill (skill never force-deletes per Critical rules). Skill exits cleanly without state mutation.
- **Builder draft**: ACCEPTED-FIXED at design.md §Error model.

### Minors (log; address if cheap)

#### m1: Risk-retired line rhetorical overshoot — "closes the parallel-slice family's coordination axis at merge time" while ADR-068 itself anticipates PSQ-4+

- **Claim under review**: mission-brief.md L5 "closes the coordination axis"; ADR-068 L84-86 enumerates PSQ-4/5/6 future.
- **Proposed fix**: Soften to "closes the parallel-slice family's *local-merge* coordination axis; sibling on the rebase-discipline axis adjacent to PSQ-1/PSQ-2/BRANCH-2; `--push` time + `--sync-after-pr` time rebase deferred to future PSQ-4+ per ADR-068."
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L5.

#### m2: Mid-slice smoke gate L82 invokes `pytest tests/methodology/test_psq_3_rebase_audit.py`

- **Claim under review**: mission-brief.md L82.
- **Issue**: Fourth surface (after AC3 prose, test-first rows, Must-not-defer items, Verification row) carrying the stale audit-module assumption.
- **Proposed fix**: Replace with `test_commit_slice_skill_rebase_flag.py` invocation.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L80-83.

#### m3: Pre-finish gate "14+ Step-6 audits" count is loose

- **Claim under review**: mission-brief.md L95 — 18 audit names listed under "14+".
- **Proposed fix**: Replace "14+" with "18 (listed below)" — accurate count; keep names.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md L95.

#### m4: design.md doesn't enumerate the 5-7 structural-pin tests by name

- **Claim under review**: design.md L11, L36 says "~5-7 tests" but doesn't enumerate.
- **Proposed fix**: Enumerate 5 tests in design.md AND mission-brief test-first plan: `test_step_5b_contains_git_rebase_invocation`, `test_step_5b_rebase_precedes_no_ff_merge`, `test_step_5b_rebase_target_resolved_via_canonical_2_step`, `test_step_5b_conflict_stops_with_porcelain_u_entries`, `test_step_5b_conflict_surfaces_git_rebase_abort_hint`.
- **Builder draft**: ACCEPTED-FIXED at design.md L11 + L36 + mission-brief test-first plan rewrite (B1+B2+B3+B5+m4 single fix block).

## Dimensions checked

- [x] Unfounded assumptions — B3, B6, M4 (the slice-064 precedent claim was unfounded under examination).
- [x] Missing edge cases — M1, M2, M6, M3.
- [x] Over-engineering — none.
- [x] Under-engineering — B2, B4, M5.
- [x] Contract gaps — M2, M6, M1.
- [x] Security — none. Local git op under user's identity; cooperative-not-adversarial model.
- [x] Drift from vault — B5, B6, B1, B3, B4, m2 (FBCD-1 sub-mode (a) cluster); also slice-064 precedent claim drift (M4).
- [x] Web-known issues — skipped (WebSearch unavailable).
- [x] Cross-cutting conformance — FBCD-1 sub-mode (a) cluster of 6+ findings is the empirical canonical instance of the aggregated-lessons TPHD-1 sub-mode (a) pattern at first-Critic time (N=6 cumulative-meta-Critic-caught predecessor pattern; this slice carries the pattern at first-Critic).

## Triage

**Triaged by**: user
**Date**: 2026-05-28
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | mission-brief.md L30-32 test-first plan repointed to `tests/methodology/test_commit_slice_skill_rebase_flag.py` (matches existing `_merge_flag.py` / `_push_flag.py` / `_sync_after_pr_flag.py` family convention) |
| B2 | Blocker | ACCEPTED-FIXED | mission-brief AC3 rewritten + 3 stale test-first rows replaced with structural-pin tests; aligned with design.md §Scope narrowing + ADR-068 §Options-#3 (no audit-tool module; `git rebase` IS the runtime gate) |
| B3 | Blocker | ACCEPTED-FIXED | mission-brief AC1 rewritten to `--merge` only with explicit `--push`/`--sync-after-pr` out-of-scope pointer; `_sync_after_pr_mode_rebases_default_before_merge` row deleted |
| B4 | Blocker | ACCEPTED-FIXED | Must-not-defer items L54-55 deleted; replaced with structural-pin convention item referencing `tests.methodology.conftest.read_file` pattern |
| B5 | Blocker | ACCEPTED-FIXED | mission-brief L19 + L36 standardized on `_entry_present_in_repo` (matches 51-instance convention in `test_methodology_changelog.py`) |
| B6 | Blocker | ACCEPTED-FIXED | mission-brief L18 corrected to cite extant `ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` |
| M1 | Major | ACCEPTED-FIXED | design.md §Contracts gains Worktree-vs-main-tree interaction paragraph; M-add-2 corrects the SKILL.md L259 citation error in the Builder fix |
| M2 | Major | ACCEPTED-FIXED | design.md §Error model gains Re-entry semantics paragraph covering all 3 SOAD-1 options |
| M3 | Major | ACCEPTED-FIXED | design.md §Contracts gains SOAD-1 justification paragraph (3-option decision tree doesn't model as binary yes/no) |
| M4 | Major | ACCEPTED-FIXED | design.md L156 replaces slice-064 precedent appeal with rebase-specific argument; M-add-1 completes the sweep across two ADR-068 sites the Builder fix initially missed |
| M5 | Major | ACCEPTED-FIXED | mission-brief Verification plan row 3 rewritten — structural-pin test verification + live exercise of `/commit-slice --merge` against synthetic divergence |
| M6 | Major | ACCEPTED-FIXED | option (c) "cancel slice merge entirely" operational path specified in design.md §Re-entry semantics |
| m1 | minor | ACCEPTED-FIXED | mission-brief L5 softened to "local-merge coordination axis" with PSQ-4+ future-flexibility caveat |
| m2 | minor | ACCEPTED-FIXED | Mid-slice smoke gate L80-83 invocation corrected to `test_commit_slice_skill_rebase_flag.py` |
| m3 | minor | ACCEPTED-FIXED | Pre-finish gate "14+" → "18" (matches the named audit list) |
| m4 | minor | ACCEPTED-FIXED | 5 test functions enumerated in design.md L11 + L38-43 + mission-brief test-first plan |
| M-add-1 | Major | ACCEPTED-FIXED | ADR-068 L29 Pros bullet + L53 Decision § both rewritten with rebase-specific argument (slice-064 appeal fully retired across all 3 surfaces — design.md L156 + ADR-068 L29 + ADR-068 L53); TPHD-1 sub-mode (a) Builder-fix-block N+1 regression pattern extends to N=7 cumulative |
| M-add-2 | Major | ACCEPTED-FIXED | design.md L100 restated to acknowledge asymmetry — `--sync-after-pr` Step 5d has explicit STOP at L259; `--merge` Step 5b does NOT have an equivalent explicit STOP today; PSQ-3 preserves the pre-existing gap; closing the asymmetry is tracked as `/critic-calibrate` candidate |
| m-add-1 | minor | ACCEPTED-FIXED | design.md L104 corrected to "six confirmation sites" (verified via grep — L173/L175/L202/L203/L205/L255) |
| m-add-2 | minor | ACCEPTED-FIXED | design.md L158 rewritten to past tense reflecting completed /critique + /critique-review reviews |
| m-add-3 | minor | ACCEPTED-FIXED | ADR-068 L37 corrected from N=10 to N=11 (matches L91 + 11-item enumeration) |
| m-add-4 | minor | ACCEPTED-FIXED | design.md L81-84 outcome paths split into "Fast-forward no-op" (default has not advanced) + "Clean replay" (default advanced + slice replays cleanly) |
