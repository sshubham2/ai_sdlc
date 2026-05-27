# Code Review: Slice 073 add-rebase-and-conflict-discipline

**code-Critic reviewed**: slice diff vs base `b589acb` (filtered to in-scope paths)
**Date**: 2026-05-28
**Result**: FINDINGS (advisory per CRSI-1 v1 walking-skeleton)

## Summary

**0 Blockers / 1 Major / 3 minors**. The Major is a real load-bearing cross-spec parity defect: the canonical 2-step default-branch resolution literal in sub-step 2.5 is NOT byte-identical to sub-step 3 (sub-step 2.5 has `2>/dev/null` on both legs; sub-step 3 has neither — though Step 5d sub-step 2 also has the redirected form, making sub-step 3 the pre-existing divergent leg). The three minors are: (m1) substring-leak co-occurrence-not-co-location risk in `test_step_5b_conflict_stops_with_porcelain_u_entries`, (m2) cross-document 3-Critic-stack N-count off-by-one in shippability row #73 (should be N=9 not N=10), (m3) `git rebase --continue` literal in SOAD-1 option (b) is not pinned by any structural-pin test. The slice's actual behavior is correct; all 8 new tests PASS; the version-file legs synchronize at 0.72.0. **All 4 findings DEFER to slice-074+ bundled-cleanup nomination per voluntary-restraint precedent N=14 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073).

## Changed files (in-scope)

```
VERSION
methodology-changelog.md
plugin.yaml
pyproject.toml
skills/commit-slice/SKILL.md
tests/methodology/test_methodology_changelog.py
architecture/slices/slice-073-add-rebase-and-conflict-discipline/build-log.md
tests/methodology/test_commit_slice_skill_rebase_flag.py
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

#### M1: Cross-spec parity violation between sub-step 2.5 and sub-step 3 canonical 2-step default-branch resolution literals — `2>/dev/null` divergence creates the "footgun" design.md §Contracts L74 explicitly proscribes

- **Claim under review**: `skills/commit-slice/SKILL.md` sub-step 2.5 (NEW per PSQ-3) declares the canonical 2-step resolution as `default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')`; fallback `default=$(git config init.defaultBranch 2>/dev/null)`. But sub-step 3 (pre-existing) declares it as `default=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')`; fallback `default=$(git config init.defaultBranch)` — NEITHER leg has `2>/dev/null`.
- **Issue**: The two literals are NOT byte-identical. The introductory prose at sub-step 2.5 explicitly claims "identical to sub-step 3's pattern below"; design.md §Contracts L74 explicitly mandates: *"The default-branch resolution at sub-step 2.5 MUST use the same 2-step pattern as sub-step 3 — divergent resolution would create a footgun where rebase targets a different default than merge."* Step 5d sub-step 2 also uses the redirected form — so the canonical convention IS the `2>/dev/null` form, making sub-step 3 the pre-existing divergent leg. PSQ-3 inherited the canonical form from Step 5d but did not retroactively harmonize sub-step 3. Strict-mode shells (`set -o pipefail`) and CI environments that fail on stderr would see DIFFERENT behavior between the two sites. `test_step_5b_rebase_target_resolved_via_canonical_2_step` passes because it asserts the unredirected substrings — substring-contained in BOTH forms, so the test is too lenient.
- **Evidence**: `skills/commit-slice/SKILL.md` sub-step 2.5 has `2>/dev/null`; sub-step 3 doesn't; Step 5d sub-step 2 has it (canonical); design.md L74 contract surface.
- **Proposed fix**: Update sub-step 3 to add `2>/dev/null` to both legs (improves pre-existing leg, aligns 3 sites). Add a tighter pin test asserting `section.count("git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null") == 2`. Or strip `2>/dev/null` from sub-step 2.5 (worse — diverges from Step 5d canonical).
- **Disposition**: DEFER to slice-074+ bundled-cleanup nomination per voluntary-restraint precedent N=14 cumulative + CRSI-1 v1 advisory-only walking-skeleton.

### Minors

#### m1: `test_step_5b_conflict_stops_with_porcelain_u_entries` asserts co-occurrence not co-location — weaker than docstring implies

- **Claim under review**: `tests/methodology/test_commit_slice_skill_rebase_flag.py` `test_step_5b_conflict_stops_with_porcelain_u_entries` asserts BOTH `"git status --porcelain" in section` AND `"U-prefixed" in section`. The test's own docstring notes the substring-overlap risk: `git status --porcelain` appears at L168 (WT-clean guardrail, pre-existing) AND in sub-step 2.5 (NEW).
- **Issue**: A future regression deleting the PSQ-3 conflict-STOP block entirely but leaving the WT-clean guardrail intact AND introducing `U-prefixed` elsewhere in Step 5b (e.g., a future merge-conflict diagnostic at sub-step 3) would still pass the test. Co-occurrence ≠ co-location.
- **Proposed fix**: Tighten to require the two substrings appear in the SAME sub-step 2.5 sub-section (find sub-step 2.5 boundary markers + assert both substrings within that narrower window).
- **Disposition**: DEFER to slice-074+ bundled-cleanup nomination.

#### m2: shippability row #73 3-Critic-stack N-count off-by-one — should be N=9 not N=10

- **Claim under review**: `architecture/shippability.md` row #73 states "3-Critic stack N=10 cumulative (slice-063 through slice-073)". methodology-changelog v0.71.0 anchor (slice-072) at L51 states "**3-Critic stack N=8 cumulative** (slice-063 → slice-072 inclusive)" — that's 10 slices for N=8 (2 slices in the range didn't trigger all 3 Critics). Slice-073 adds N=1 → expected N=9.
- **Issue**: shippability row #73 over-counts by 1. Documentary drift; does not affect runtime behavior or test pass/fail, but the off-by-one is exactly the BC-PROJ-9 inventory-count class N=2 cumulative pattern (slice-050 N=1 + slice-069 N=2 — slice-073 extends to N=3).
- **Proposed fix**: Update shippability row #73 "N=10 cumulative" → "N=9 cumulative" to match the predecessor v0.71.0 anchor + slice-073 +1 increment.
- **Disposition**: DEFER to slice-074+ bundled-cleanup nomination.

#### m3: `git rebase --continue` literal in SOAD-1 option (b) is not pinned by any structural-pin test — recovery path silently regression-able

- **Claim under review**: `skills/commit-slice/SKILL.md` sub-step 2.5 SOAD-1 option (b) prose contains `git rebase --continue` (recovery path for manual conflict resolution). None of the 5 structural-pin tests in `test_commit_slice_skill_rebase_flag.py` assert presence of this literal.
- **Issue**: A future edit removing option (b) (e.g., a rewrite collapsing 3 options to 2) would silently degrade PSQ-3 from 3-option to 2-option recovery surface. shippability row #73 regression-set explicitly enumerates `git rebase --abort` disappearance — `--continue` is the equally-important sibling recovery path, undefended.
- **Proposed fix**: Add a 6th prose-pin test `test_step_5b_conflict_offers_git_rebase_continue_recovery_path` asserting `"git rebase --continue" in section`.
- **Disposition**: DEFER to slice-074+ bundled-cleanup nomination.

## Dimensions checked

- [x] Unfounded assumptions — m2 (the N=10 cumulative anchor in shippability row #73 is unfounded against predecessor v0.71.0 L51 anchor of N=8 for slices 063-072).
- [x] Missing edge cases — M1 (strict-shell / CI-stderr-fail edge case where `2>/dev/null` redirection presence/absence diverges runtime behavior).
- [x] Over-engineering — none. Sub-step 2.5 is exactly the minimum surface change the design.md scope-narrowing prescribed.
- [x] Under-engineering — m3 (option (b)'s `git rebase --continue` recovery path documented but not pinned by structural-pin test).
- [x] Contract gaps — M1 (design.md L74 "MUST use the same 2-step pattern" contract violated at byte level by `2>/dev/null` divergence).
- [x] Security — none. PSQ-3 is local-git-operation contract; no auth surface; cooperative-not-adversarial model per ADR-068 §Adversarial model.
- [x] Drift from vault — m2 (shippability row #73 N-count drifts from predecessor methodology-changelog anchor); M1 has drift component (design.md §Contracts L74 vs SKILL.md implementation).
- [x] Web-known issues — Skipped — WebSearch not invoked; the slice uses standard long-stable git CLI surfaces (no recent deprecations); not a high-value WebSearch target.
- [x] Cross-cutting conformance — M1 has cross-cutting component (3-site asymmetry: sub-step 2.5 + Step 5d sub-step 2 use redirected form; sub-step 3 doesn't — pre-existing divergent leg). RPCD-1 satisfied for `git rebase` literal but NOT for canonical 2-step resolution literal. APED-1 vacuous (no parse-rule changes). RSAD-1 vacuous (no new audit/linter).
