# Slice 073: add-rebase-and-conflict-discipline

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: PSQ-3 closes the parallel-slice family's *local-merge* coordination axis; sibling on the rebase-discipline axis adjacent to PSQ-1 (queue) + PSQ-2 (claim machinery) + BRANCH-2 (worktree isolation); `--push` time and `--sync-after-pr` time rebase deferred to future PSQ-4+ per ADR-068.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

PSQ-3 codifies rebase-onto-default discipline at `/commit-slice --merge` (sub-mode b only) to prevent silent merge conflicts between parallel slices that share the default branch. BRANCH-2 (physical worktree isolation) + PSQ-1 (queue discoverability) + PSQ-2 (claim machinery) make parallel work safe and discoverable; PSQ-3 closes the local-merge coordination surface — the second-to-merge slice must rebase cleanly onto the freshly-updated default rather than discovering conflicts mid-merge. Conflict-on-rebase STOPS the skill and surfaces SOAD-1 structured-option recovery to the user; no auto-resolve. `--push` and `--sync-after-pr` sub-modes are explicitly out of scope (see `design.md §Out of scope` + `ADR-068 §Options-#2`).

## Acceptance criteria

1. `/commit-slice --merge` (sub-mode b) performs an explicit `git rebase <resolved-default>` of the slice branch BEFORE the existing no-ff merge / safe-delete step, with the rebase outcome surfaced to the user (clean / fast-forward no-op / conflict). `--push` (sub-mode a) and `--sync-after-pr` (sub-mode d) are explicitly out of scope — see `design.md §'Scope narrowing from mission brief'` + `ADR-068 §Options-#2`.
2. On rebase conflict, `/commit-slice --merge` STOPS — surfaces conflicting file paths (from `git status --porcelain` U-prefixed entries) + `git rebase --abort` recovery hint + a 3-option SOAD-1 structured-options ask (abort / resolve-out-of-skill+continue / cancel-merge-entirely) + does NOT proceed to default-checkout, merge, worktree-remove, or branch-delete. No auto-resolve.
3. PSQ-3 minted in `methodology-changelog.md v0.72.0` + new ADR (`ADR-068-mint-psq-3-rebase-and-conflict-discipline.md`) + structural-pin tests in NEW `tests/methodology/test_commit_slice_skill_rebase_flag.py` (no new audit-tool module — `git rebase` itself is the runtime gate at sub-step 2.5; structural-pin precedent matches the existing sibling `test_commit_slice_skill_merge_flag.py` / `_push_flag.py` / `_sync_after_pr_flag.py` family).
4. BC-PROJ-10 paired-pin: `test_v_0_72_0_psq_3_entry_present_in_repo` + `test_v_0_72_0_psq_3_shippability_consumer_propagation` both PASS under `--strict-pre-finish`; shippability row #73 added citing both tests + the new structural-pin test module.
5. 5-part PMI-1 atomic bump 0.71.0 → 0.72.0 (`VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## v0.72.0` header in `methodology-changelog.md` + installed `~/.claude/ai-sdlc-<VERSION>` directory).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural | tests/methodology/test_commit_slice_skill_rebase_flag.py | test_step_5b_contains_git_rebase_invocation | PENDING |
| 1 | structural | tests/methodology/test_commit_slice_skill_rebase_flag.py | test_step_5b_rebase_precedes_no_ff_merge | PENDING |
| 1 | structural | tests/methodology/test_commit_slice_skill_rebase_flag.py | test_step_5b_rebase_target_resolved_via_canonical_2_step | PENDING |
| 2 | structural | tests/methodology/test_commit_slice_skill_rebase_flag.py | test_step_5b_conflict_stops_with_porcelain_u_entries | PENDING |
| 2 | structural | tests/methodology/test_commit_slice_skill_rebase_flag.py | test_step_5b_conflict_surfaces_git_rebase_abort_hint | PENDING |
| 3 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_72_0_psq_3_entry_present_in_repo | PENDING |
| 4 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_72_0_psq_3_shippability_consumer_propagation | PENDING |
| 5 | structural | tests/methodology/test_methodology_changelog.py | test_version_files_synchronized_at_v_0_72_0 | PENDING |

Note: AC3 + AC4 share the entry-present test row (AC3 = "PSQ-3 minted in changelog"; AC4 = "BC-PROJ-10 paired-pin tests PASS"); the same `test_v_0_72_0_psq_3_entry_present_in_repo` verifies both. AC4 additionally requires `test_v_0_72_0_psq_3_shippability_consumer_propagation`.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | --merge rebases default before merge | Read updated `skills/commit-slice/SKILL.md`; locate explicit `git rebase` invocation BEFORE the no-ff merge command in Step 5b; structural tests at `tests/methodology/test_commit_slice_skill_rebase_flag.py` assert presence + ordering + canonical-2-step default resolution. Live exercise: run `/commit-slice --merge` on a synthetic slice branch with default-branch divergence; observe rebase step executed via build-log Events. |
| 2 | Conflict STOPS skill with SOAD-1 recovery | Construct a synthetic conflict (two branches edit the same file); run `/commit-slice --merge`; verify skill halts, no merge attempted, no branch deleted, U-prefixed file paths shown, `git rebase --abort` literal shown, SOAD-1 3-option ask surfaced. Structural pins at `test_step_5b_conflict_stops_with_porcelain_u_entries` + `test_step_5b_conflict_surfaces_git_rebase_abort_hint`. |
| 3 | PSQ-3 minted in methodology-changelog v0.72.0 + ADR-068 | `methodology-changelog.md` contains `## v0.72.0 — 2026-05-27` header + PSQ-3 entry; `architecture/decisions/ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` exists with `status: accepted`; structural test `test_v_0_72_0_psq_3_entry_present_in_repo` PASSES. |
| 4 | Paired-pin tests PASS | `$PY -m pytest tests/methodology/test_methodology_changelog.py -k v_0_72_0_psq_3 -v` returns 2 PASSED; shippability row #73 contains both test references + the structural-pin test module reference; `$PY -m tools.shippability_runner` exits 0 with 73/73 PASS. |
| 5 | 5-part PMI-1 atomic bump | `cat VERSION` = `0.72.0`; `plugin.yaml` version: `0.72.0`; `pyproject.toml` `[project] version` = `0.72.0`; `methodology-changelog.md` contains `## v0.72.0` header; installed `~/.claude/ai-sdlc-0.72.0/` directory exists. `$PY -m tools.plugin_manifest_audit` PASSES. |

## Must-not-defer

- [ ] Conflict surface: clear actionable recovery hint (`git rebase --abort`) — no silent halt
- [ ] Rebase failure modes other than conflict (e.g., detached HEAD, missing remote) surfaced with non-zero exit + git stderr printed verbatim
- [ ] SOAD-1 structured-options ask at conflict-STOP (3-option: abort / resolve-out-of-skill+continue / cancel-merge-entirely) — NOT a raw `(yes/no)` prompt (the conflict decision is 3-way, not binary)
- [ ] Re-entry semantics on user-side `git rebase --continue` outside skill: design.md §Error model pins the flow (sub-step 2 no-op detects no un-staged files; sub-step 2.5 fast-forwards as no-op; proceeds normally)
- [ ] Cross-spec parity (RPCD-1): `git rebase` invocation literal pinned across `skills/commit-slice/SKILL.md` + `tests/methodology/test_commit_slice_skill_rebase_flag.py` + ADR-068 + design.md (NOT in any audit tool — there is none)
- [ ] BRANCH-2 worktree compatibility: rebase runs in the slice's worktree without `git checkout` switching; existing post-rebase `git checkout $default` STOP path at SKILL.md L259 still applies if main tree has $default checked out
- [ ] Structural-pin tests in `tests/methodology/test_commit_slice_skill_rebase_flag.py` use the same `tests.methodology.conftest.read_file` pattern as the sibling `_merge_flag.py` / `_push_flag.py` / `_sync_after_pr_flag.py` files (no git-fixture harnessing — pure prose-pin assertions)
- [ ] PMI-1 atomic bump completeness: all 5 surfaces synchronized before `/validate-slice`
- [ ] OSDG-1 + CAD-1 drift-guard: `skills/commit-slice/SKILL.md` in-repo content-equal to installed copy after edit

## Out of scope

- Auto-resolve of rebase conflicts (PSQ-3 STOPS; no merge driver, no `--theirs`/`--ours` heuristics)
- Multi-default-branch repos (single resolved default per BRANCH-2 contract)
- `--push` sub-mode (a) of `/commit-slice` — PR-based workflow defers rebase responsibility to GitHub's merge-queue or reviewer's `gh pr merge --rebase`; PSQ-3 v1 governs `--merge` only. Future PSQ-4+ may extend.
- `--sync-after-pr` sub-mode (d) of `/commit-slice` — post-PR-merge cleanup; rebase moot at this point (PR already merged on GitHub; local default fast-forwards via `git pull --ff-only`). Out of scope per ADR-068 §Options-#2.
- Rebase strategy customization (`--rebase-merges`, `--interactive`) — PSQ-3 uses plain `git rebase`
- Retrofit of existing `/commit-slice` raw `(yes/no)` confirmation prompts to SOAD-1 form — scope-creep; tracked as `/critic-calibrate` candidate, not in this slice
- New audit-tool module — `git rebase` itself is the runtime gate; structural-pin tests on SKILL.md catch drift (see ADR-068 §Options-#3 for the rejected audit-tool alternative)
- Conflict-resolution UI (future PSQ-4+ if needed)

## Dependencies

- Prior slices: [[slice-066-add-worktree-per-slice-discipline]] (BRANCH-2 worktree-per-slice baseline), [[slice-067-add-parallel-slice-queue-output]] (PSQ-1 queue), [[slice-072-add-psq-2-claim-machinery]] (PSQ-2 claim mechanism)
- Vault refs: [[decisions/ADR-063]] (BRANCH-2), [[decisions/ADR-064]] (PSQ-1), [[decisions/ADR-067]] (PSQ-2), [[decisions/ADR-050]] (SOAD-1), `skills/commit-slice/SKILL.md` (target surface — Step 5b only)
- Risk register: standing nomination from slice-067 reflection + slice-072 "natural next slice is PSQ-3 (rebase + conflict discipline at /commit-slice)"

## Mid-slice smoke gate

At ~50% of build (after SKILL.md Step 5b sub-step 2.5 edit lands + structural-pin test module exists, before paired-pin tests + PMI-1 bump):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_commit_slice_skill_rebase_flag.py -v
& $PY -m pytest tests/methodology/test_methodology_changelog.py -k v_0_72_0_psq_3 -v
```

Expected: AC1 + AC2 structural tests PASS (SKILL.md edit lands cleanly). Paired-pin tests still failing at this checkpoint is acceptable (they require the v0.72.0 changelog entry which lands in Phase D); they MUST PASS by pre-finish gate. If the rebase-flag test set fails: STOP, diagnose, don't continue to PMI-1 bump.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes (vault matches code)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `/code-review` invoked + findings triaged (advisory under CRSI-1 v1)
- [ ] 18 Step-6 audits all CLEAN or deferred-with-rationale (PMI-1, AVFS-1, MCFS-1, TVFS-1, CAD-1, BRANCH-2, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, STP-1, NAW-1, WIRE-1, RR-1, INST-1, SCMD-1, PTFCD-1, critique-review)
- [ ] Full pytest suite PASSES (current baseline 987/987; expect +5-7 net new tests for PSQ-3 structural pins + 2 paired-pin)
- [ ] Shippability runner 73/73 PASS 0 FAIL post-row-add
- [ ] VAL-1 0 secrets + 0 imports
