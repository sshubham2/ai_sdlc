# Slice 089: make-commit-slice-stale-branch-check-parallel-slice-aware

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none formally registered — closes the parallel-unaware stale-slice-branch guardrail false-positive observed firsthand on 2026-05-31 merging slice-088 while slice-087 was an active parallel slice (the guardrail refused `--merge`, requiring a user-authorized manual override). Thematically continues the parallel-slice-awareness arc of slice-087 (stranded detector / R-26) + slice-088 (project-frame).
**Test-first**: true  (per TF-1 — behavioral guardrail change with crisp pass/fail assertions)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`/commit-slice`'s stale-slice-branch pre-flight guardrail (in `--merge` Step 5b sub-step 1 AND `--push` Step 5c pre-flight #2) refuses if **any** non-current `slice/*` branch exists. That heuristic was correct in the single-slice era (catch orphan branches from failed merges) but under the PSQ-1 / PSQ-2 / BRANCH-2 parallel-slice model a concurrent `slice/NNN` branch **with its own live worktree** is the NORMAL state, not a conflict artifact. This slice makes the guardrail parallel-aware: refuse only on a `slice/*` branch that has **no live worktree** (a genuine orphan), and treat a worktree-backed `slice/*` branch as a legitimate concurrent slice — surfacing it as an informational note, not a STOP. Crucially, this is a prerequisite for slice-090 (`add-rebase-and-conflict-resolve-to-commit-slice-push`): today the guardrail STOPs `--merge`/`--push` at pre-flight *before* the PSQ-3 rebase can run, so the existing rebase-and-resolve machinery is unreachable while any peer slice is in flight.

## Acceptance criteria

1. The `--merge` stale-branch guardrail (Step 5b sub-step 1) refuses ONLY on `slice/*` branches with no live worktree; a `slice/*` branch backed by a live worktree does NOT trigger STOP and is surfaced as a one-line informational note (e.g. "N parallel slice(s) in flight: <list>").
2. The `--push` stale-branch guardrail (Step 5c pre-flight #2) applies the identical parallel-awareness — symmetric behavior across both modes (no divergence between the two guardrail surfaces).
3. A genuinely orphaned `slice/*` branch (exists with NO worktree — e.g. left by a failed prior merge) STILL triggers the existing STOP with its current actionable message (the genuine-stale protection is preserved, not weakened).
4. An automated test asserts both directions: a worktree-backed `slice/*` branch → guardrail allows (no STOP); a worktree-less `slice/*` branch → guardrail refuses (STOP). The classification logic is exercised, not just the prose.
5. Both `skills/commit-slice/SKILL.md` (in-repo) and the installed `~/.claude/skills/commit-slice/SKILL.md` document the parallel-awareness and remain content-equal modulo EOL (OSDG-1 / `test_commit_slice_skill_drift.py` passes).

## Test-first plan

Each AC maps to failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1,2 | unit | tests/methodology/test_stale_branch_parallel_aware.py | test_worktree_backed_slice_branch_is_allowed | PENDING |
| 3 | unit | tests/methodology/test_stale_branch_parallel_aware.py | test_orphan_slice_branch_still_refused | PENDING |
| 1 | unit | tests/methodology/test_stale_branch_parallel_aware.py | test_current_slice_own_worktree_excluded_by_path | PENDING |
| 1,3 | unit | tests/methodology/test_stale_branch_parallel_aware.py | test_noncanonical_named_worktree_backed_branch_allowed_not_orphan | PENDING |
| 1,2 | unit | tests/methodology/test_stale_branch_parallel_aware.py | test_merge_and_push_guardrails_symmetric | PENDING |
| 1 | unit | tests/methodology/test_stale_branch_parallel_aware.py | test_worktree_backing_uses_short_form_not_raw_refname | PENDING |
| 2,5 | drift | tests/methodology/test_commit_slice_skill_drift.py | (existing) in-repo == installed SKILL.md | PENDING |
| 2 | parity | tests/methodology/test_stale_branch_parallel_aware.py | test_merge_and_push_stale_check_prose_byte_identical | PENDING |

Added at /critique (post-fix harmonization, TPHD-1): `test_current_slice_own_worktree_excluded_by_path` (Critic B1; per meta-Critic M-add-1 this MUST exercise a case/separator-mismatched current_path so the branch-exclusion belt is proven to cover a path-equality miss), `test_noncanonical_named_worktree_backed_branch_allowed_not_orphan` (Critic B3), `test_merge_and_push_stale_check_prose_byte_identical` (Critic M2.1 / FBCD-1), `test_worktree_backing_uses_short_form_not_raw_refname` (meta-Critic **B-add-1** — asserts the `refs/heads/` strip lands `backed` in short form against a REAL porcelain fixture, NOT a pre-stripped stub; pairs with B2's fixture). Boundary cases (meta-Critic m-add-1) — zero-slice-refs → allow, worktree-on-default ignored — are asserted in the same module. The classifier ships as `tools/stale_branch_classifier.py` (design.md); a real two-worktree fixture execution (Critic B2) is the /build-slice kickoff + mid-slice-smoke evidence.

## Architectural layers exercised

(not a walking-skeleton slice)

## Exploratory test charter

(not a charter slice)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `--merge` allows worktree-backed peer branch | Test: stub `git worktree list --porcelain` to include a peer `slice/*` branch with a worktree; assert classifier returns allow + informational note string present |
| 2 | `--push` guardrail symmetric | Test: same stub, assert `--push` pre-flight path classifies identically (shared helper, no divergence) |
| 3 | orphan branch still refused | Test: stub a `slice/*` branch absent from `git worktree list`; assert classifier returns STOP with the existing message |
| 4 | classifier exercised | `pytest tests/methodology/test_stale_branch_parallel_aware.py` — all pass |
| 5 | no skill drift | `pytest tests/methodology/test_commit_slice_skill_drift.py` passes; `$PY -m tools.install_audit` install-parity OK |

## Must-not-defer

- [ ] Genuine-stale (worktree-less orphan) refusal path MUST remain — do NOT weaken the original protection the guardrail exists for.
- [ ] Cross-platform worktree detection: `git worktree list --porcelain` parsing MUST work on Windows (Git-for-Windows bundled bash) — same dependency convention the skill already uses at Step 5b sub-step 5.
- [ ] Observability: when the guardrail skips a worktree-backed branch, surface a one-line note naming the parallel slice(s) — never silently swallow (R-7 silent-disable class).
- [ ] Coordinate semantics with R-26 stranded-slice detector: a worktree-backed branch is "active parallel" here AND "in-progress" there; do not let this change reclassify a genuinely-stranded (committed-but-unmerged, worktree-removed) branch as safe-to-ignore.
- [ ] Do NOT auto-delete or auto-resolve any branch — guardrail only classifies allow/refuse.

## Out of scope

- The `--push` rebase-and-conflict-resolve extension (queued as slice-090 `add-rebase-and-conflict-resolve-to-commit-slice-push`) — this slice only makes the guardrail parallel-aware so that path becomes reachable.
- Any change to PSQ-3 rebase logic or the PCR-1/2a/2b conflict-resolution machinery.
- The `--sync-after-pr` path (it has no stale-branch guardrail in this shape — cleanup-only).
- Changing the stranded-slice detector (`tools/stranded_slice_audit.py`) — only consume/align with its classification, don't modify it.

## Dependencies

- Prior slices: [[slice-087-add-stranded-slice-detection-to-slice]] (4-class divergence model — align worktree-backed == in-progress), [[slice-088-add-project-frame-synthesizer]] (parallel-slice arc)
- Vault refs: [[skills/commit-slice/SKILL.md]] Step 5b sub-step 1 + Step 5c pre-flight #2, [[decisions/ADR-063]] (BRANCH-2 worktree model), [[decisions/ADR-064]] (PSQ-1)
- Methodology: OSDG-1 (`test_commit_slice_skill_drift.py` content-equality gate)

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m pytest tests/methodology/test_stale_branch_parallel_aware.py -x
```
Expected: the worktree-backed-allowed + orphan-refused tests exist and the previously-failing ones now pass for the implemented direction. If the orphan-refusal test regresses (genuine-stale protection lost): STOP, do not continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (orphan refusal preserved; cross-platform; observability note; R-26 alignment)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] OSDG-1: in-repo SKILL.md == installed SKILL.md (modulo EOL); install-parity OK
