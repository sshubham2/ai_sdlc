# Design: Slice 073 add-rebase-and-conflict-discipline

**Date**: 2026-05-27
**Mode**: Standard

## What's new

- **PSQ-3** rule mint on the parallel-slice family axis — first rule on the *rebase-discipline* axis adjacent to (not extending) BRANCH-2 (worktree-isolation), PSQ-1 (queue-output), and PSQ-2 (claim-machinery).
- `skills/commit-slice/SKILL.md` Step 5b (the `--merge` sub-mode) gains a **NEW sub-step 2.5** that runs `git rebase <default>` on the slice branch BEFORE the existing default-branch checkout + no-ff merge (current Step 5b sub-step 3). Rebase outcome is surfaced to the user (clean / conflict / no-op fast-forward).
- Conflict handling: on rebase conflict the skill STOPS — does NOT proceed to default-branch checkout, merge, worktree-remove, or branch-delete. The conflicting file paths + `git rebase --abort` recovery hint are printed; SOAD-1 structured options surface next-step choice to the user.
- New structural-pin test module `tests/methodology/test_commit_slice_skill_rebase_flag.py` (5 tests enumerated below) pins the rebase invocation literal + ordering + conflict-STOP language + recovery-hint literal in `skills/commit-slice/SKILL.md`. The 5 tests are: `test_step_5b_contains_git_rebase_invocation` (AC1), `test_step_5b_rebase_precedes_no_ff_merge` (AC1), `test_step_5b_rebase_target_resolved_via_canonical_2_step` (AC1), `test_step_5b_conflict_stops_with_porcelain_u_entries` (AC2), `test_step_5b_conflict_surfaces_git_rebase_abort_hint` (AC2).
- New ADR `ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` (reversibility: cheap) documenting the chosen design + options considered + adversarial framing.
- methodology-changelog.md `## v0.72.0` entry minting PSQ-3 + 5-part PMI-1 atomic bump 0.71.0 → 0.72.0.
- BC-PROJ-10 paired-pin tests in `tests/methodology/test_methodology_changelog.py`: `test_v_0_72_0_psq_3_entry_present_in_repo` + `test_v_0_72_0_psq_3_shippability_consumer_propagation`.
- shippability.md row #73 citing both paired-pin tests + the new structural-pin module.

## What's reused

- [[skills/commit-slice/SKILL.md]] — existing Step 5b 5-step flow (commit on slice branch → resolve default → checkout default → no-ff merge → idempotent worktree-remove → safe-delete) is preserved verbatim; sub-step 2.5 is inserted between sub-step 2 (commit on slice branch) and sub-step 3 (default-branch resolution + merge).
- [[tools/branch_workflow_audit.py]] — existing `_resolve_default_branch()` helper at `tools/branch_workflow_audit.py:162` is reused (NOT duplicated) — SKILL.md prose names the identical 2-step resolution shape (primary `git symbolic-ref refs/remotes/origin/HEAD` + fallback `git config init.defaultBranch`) so the rebase target stays consistent with the existing merge target.
- [[decisions/ADR-063]] — BRANCH-2 worktree-isolation; rebase runs INSIDE the worktree, not the main tree. The worktree's git index is already cwd-bound by `/build-slice` Prerequisite check.
- [[decisions/ADR-064]] — PSQ-1 queue mechanism (sibling rule; rebase is independent of queue/claim machinery — PSQ-3 governs `/commit-slice`, PSQ-1/PSQ-2 govern `/slice`).
- [[decisions/ADR-067]] — PSQ-2 claim machinery (sibling rule).
- Test fixture helpers `_init_repo_on_default_branch()` + `_make_slice_folder()` + `_run_git()` at `tests/methodology/test_branch_workflow_audit.py:31-67` are reused (NOT duplicated) for the new structural-pin test module's git-fixture needs IF runtime tests are added. For pure prose-pin tests, `tests.methodology.conftest.read_file` is sufficient (same pattern as `test_commit_slice_skill_merge_flag.py:11`).

## Components touched

### `skills/commit-slice/SKILL.md` (modified, OSDG-1-guarded)

- **Responsibility**: drive the `--merge` sub-mode through commit + rebase + merge + cleanup, with explicit user-confirmation checkpoints and stop-on-conflict semantics. PSQ-3 inserts the rebase step at sub-step 2.5; the surrounding flow is unchanged.
- **Lives at**: `skills/commit-slice/SKILL.md` (modified) + `~/.claude/skills/commit-slice/SKILL.md` (OSDG-1 forward-sync at /build-slice Phase F, per slice-072 OSDG-1 discipline).
- **Key interactions**: git CLI (`git rebase`, `git rebase --abort`, plus existing `git status`, `git add`, `git commit`, `git symbolic-ref`, `git checkout`, `git merge --no-ff`, `git worktree remove`, `git branch -d`); the user (SOAD-1 structured options on conflict; explicit "yes" confirmation prompts).

### `tests/methodology/test_commit_slice_skill_rebase_flag.py` (NEW, 5 tests, ~120 LOC)

- **Responsibility**: pin the rebase invocation literal + ordering + conflict-STOP language + recovery-hint literal in `skills/commit-slice/SKILL.md` Step 5b. Mirrors the pattern at `tests/methodology/test_commit_slice_skill_merge_flag.py` (prose-pin only — `read_file()` helper from conftest; no git fixtures needed).
- **Lives at**: `tests/methodology/test_commit_slice_skill_rebase_flag.py` (created by this slice).
- **Test functions** (locked, per TF-1 plan):
  1. `test_step_5b_contains_git_rebase_invocation` — asserts `git rebase` literal appears in Step 5b section of SKILL.md.
  2. `test_step_5b_rebase_precedes_no_ff_merge` — asserts the file-offset of `git rebase` is LESS than the file-offset of `git merge --no-ff` (ordering invariant; rebase happens first).
  3. `test_step_5b_rebase_target_resolved_via_canonical_2_step` — asserts the canonical 2-step default-branch resolution literal (`git symbolic-ref refs/remotes/origin/HEAD` primary + `git config init.defaultBranch` fallback) appears in Step 5b sub-step 2.5.
  4. `test_step_5b_conflict_stops_with_porcelain_u_entries` — asserts the `git status --porcelain` literal AND the U-prefixed-entries language is present in the conflict-STOP block.
  5. `test_step_5b_conflict_surfaces_git_rebase_abort_hint` — asserts `git rebase --abort` literal is present in the conflict-STOP block.
- **Key interactions**: reads `skills/commit-slice/SKILL.md` via `tests.methodology.conftest.read_file`; asserts string substrings + ordering invariants.

### `methodology-changelog.md` (appended)

- **Responsibility**: ship the `## v0.72.0 — 2026-05-27` entry minting PSQ-3 in the canonical entry shape (one-paragraph summary + 5-part PMI-1 atomic-bump leg enumeration + Critic disposition density + Validation block).
- **Lives at**: `methodology-changelog.md` (new section appended; existing entries preserved verbatim per append-only discipline) + `~/.claude/methodology-changelog.md` (MCFS-1 forward-sync; NOT a PMI-1 leg per slice-063 M-add-1 leg-enumeration discipline).

### `tests/methodology/test_methodology_changelog.py` (extended)

- **Responsibility**: gain BC-PROJ-10 paired-pin pair `test_v_0_72_0_psq_3_entry_present_in_repo` + `test_v_0_72_0_psq_3_shippability_consumer_propagation` (the paired-pin discipline is N≥19 cumulative across the project; slice-072 added the v0.71.0 pair).
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (modified).
- **Key interactions**: pattern-matches `## v0.72.0` header presence + `PSQ-3` substring + `shippability.md` row #73 cross-reference symmetry.

### `architecture/decisions/ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` (NEW)

- **Responsibility**: document the PSQ-3 design decision — chosen option (rebase-before-merge at /commit-slice --merge only), 4-5 options considered with pros/cons, Consequences (components affected, contracts implied, future flexibility), Reversibility tag (cheap).
- **Lives at**: `architecture/decisions/ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` (created by this slice).
- **Key interactions**: cross-references ADR-063 (BRANCH-2) + ADR-064 (PSQ-1) + ADR-067 (PSQ-2) as sibling rules on the parallel-slice family axis.

### `architecture/shippability.md` (row #73 added)

- **Responsibility**: declare the "rebase-onto-default discipline at /commit-slice --merge must never silently regress" claim as a shippability invariant; cite the structural-pin test module + paired-pin tests.
- **Lives at**: `architecture/shippability.md` (row added; existing rows preserved).

### `VERSION` / `plugin.yaml` / `pyproject.toml` / installed `~/.claude/ai-sdlc-0.72.0` (5-part PMI-1 atomic bump)

- **Responsibility**: 5-part PMI-1 atomic version bump 0.71.0 → 0.72.0 covering all 5 canonical version-bearing legs (VERSION, plugin.yaml.version, pyproject.toml [project].version, `## v0.72.0` header, installed `~/.claude/ai-sdlc-VERSION` directory). MCFS-1 + OSDG-1 + TVFS-1 forward-syncs run separately (NOT PMI-1 legs per slice-063 M-add-1 leg-enumeration discipline).

## Contracts added or changed

### PSQ-3 — rebase-onto-default at /commit-slice --merge

- **Surface**: `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 (NEW; between existing sub-step 2 commit-on-slice-branch and sub-step 3 default-branch-resolution + no-ff merge).
- **Defined in**: `skills/commit-slice/SKILL.md` (modified by this slice).
- **Behavior contract**:
  1. After the slice-branch commit lands (sub-step 2), resolve the default branch using the canonical 2-step pattern (primary: `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'`; fallback: `git config init.defaultBranch`; STOP if neither resolves).
  2. Run `git rebase <default>` on the slice branch (slice branch is the current checkout per BRANCH-2 worktree contract).
  3. Three outcome paths:
     - **Fast-forward no-op**: default has not advanced since the slice's branch-point (i.e., slice's branch-point IS default's tip); `git rebase` exits 0 without replay. Proceed to sub-step 3.
     - **Clean replay**: default has advanced past the slice's branch-point but slice's commits replay cleanly atop the new default tip (the common second-to-merge case). Proceed to sub-step 3 (default checkout + no-ff merge).
     - **Conflict**: STOP. Print conflicting file paths (from `git status --porcelain` filtered to U-prefixed entries) + `git rebase --abort` recovery hint. Surface SOAD-1 structured options to user: (a) abort rebase + investigate; (b) resolve conflicts manually + run `git rebase --continue` outside the skill; (c) cancel slice merge entirely. Do NOT proceed to sub-step 3 (default-checkout); do NOT delete worktree or branch.
- **Auth model**: no auth surface — local git operation only; the worktree is filesystem-owned by the user invoking the skill (per BRANCH-2 worktree-isolation contract).
- **Error cases**:
  - Default-branch-unresolvable → STOP with diagnostic (mirrors existing Step 5b sub-step 3 STOP).
  - Rebase conflict → STOP per contract above; recovery is user-driven, not auto-resolved.
  - Non-conflict rebase failure (e.g., detached HEAD, missing commits, broken HEAD reference) → STOP with `git rebase --abort` hint + git's stderr printed verbatim.
- **Out of scope**:
  - `--push` sub-mode (a): rebase delegated to GitHub's PR merge-queue / `gh pr merge --rebase` / reviewer-side rebase. Local pre-push rebase is opinionated; deferred to a future PSQ-4 if user demand emerges.
  - `--sync-after-pr` sub-mode (d): post-PR-merge cleanup — the PR was already merged on GitHub; rebase is moot at this point (local default is fast-forwarded via `git pull --ff-only`; slice branch is being safe-deleted).
  - Auto-resolution of conflicts (`-X theirs` / `-X ours` / merge drivers): NEVER. PSQ-3 STOPS at conflict.
  - Rebase strategy customization (`--rebase-merges`, `--interactive`, `--onto`): out of scope. PSQ-3 invokes plain `git rebase <default>`.

### Worktree-vs-main-tree interaction contract (per /critique M1 ACCEPTED-FIXED)

The rebase invocation runs on the slice branch within its BRANCH-2 worktree. The slice branch is the worktree's checked-out branch (BRANCH-2 contract at [[ADR-063]]); `git rebase <default>` does NOT switch branches — it replays the slice's commits atop the default tip while keeping the slice branch checked out (per git-scm.com/docs/git-rebase: "If `<branch>` is specified, `git rebase` will perform an automatic `git switch <branch>` before doing anything else. Otherwise it remains on the current branch."). Since PSQ-3's invocation is `git rebase <default>` WITHOUT a `<branch>` argument, the slice branch stays checked out.

The subsequent sub-step 3 `git checkout <default>` is UNCHANGED by PSQ-3. **Note on the existing flow's asymmetry** (per /critique-review M-add-2 ACCEPTED-FIXED): `skills/commit-slice/SKILL.md` Step 5d (`--sync-after-pr`) has an explicit STOP-with-diagnostic at L259 for the `git checkout <default>`-collides-with-main-tree case ("If `git checkout <default>` fails because `<default>` is already checked out in another worktree, STOP and print git's stderr + add: 'Resolve via `git worktree remove <conflicting-path>` if intentional, or run `--sync-after-pr` from the worktree where `<default>` lives.'"). The corresponding `--merge` Step 5b sub-step 3 does NOT have an equivalent explicit STOP today — the failure surfaces only via git's own non-zero exit. PSQ-3 preserves this pre-existing asymmetry (it does NOT introduce the symmetric STOP for `--merge`; the rebase step does not alter the post-rebase checkout surface). Closing the asymmetry is out of scope for this slice; tracked as a `/critic-calibrate` candidate for future codification. PSQ-3 introduces no new edge case at the checkout step; it only inserts the rebase step earlier in the flow.

### SOAD-1 justification at conflict-STOP (per /critique M3 ACCEPTED-FIXED)

PSQ-3 is the first SOAD-1 invocation in `/commit-slice` (the existing `--merge` / `--push` / `--sync-after-pr` flows use raw `(yes/no)` confirmation prompts at all six confirmation sites — verified via grep of SKILL.md: L173, L175, L202, L203, L205, L255). The SOAD-1 invocation at conflict-STOP is justified because the conflict-decision is a 3-option decision tree (abort / resolve-out-of-skill+continue / cancel-merge-entirely) that does not model as binary yes/no — exactly SOAD-1's primary-form-of-ask scope per [[ADR-050]]. The existing yes/no prompts elsewhere in `/commit-slice` are binary confirmations and stay as-is; retrofitting them to SOAD-1 form is scope-creep tracked as a future `/critic-calibrate` candidate, NOT in this slice (out of scope per mission-brief.md §Out of scope).

## Data model deltas

None. PSQ-3 modifies SKILL.md prose + adds methodology-changelog entry + ADR + tests + 5 PMI-1 legs + shippability row. No new modules, no schema changes, no on-disk-format contracts.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). PSQ-3 introduces ZERO new tool modules (the structural-pin test is a `tests/methodology/*.py` consumer of `skills/commit-slice/SKILL.md`, NOT a new tool). The wiring matrix is therefore vacuous; the audit treats zero-row matrices as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-068]] — Mint PSQ-3 (rebase-onto-default at /commit-slice --merge) — reversibility: **cheap**

## Authorization model for this slice

PSQ-3 surfaces are skill-prose + structural tests + methodology metadata. No authorization surface. The skill operates in the user's local worktree under the user's git identity; PSQ-3 does NOT introduce new permissions, new file-access patterns, or new external-system contracts beyond `git rebase` invocation (which already requires git-repo write permission — same as the existing `git merge` invocation at sub-step 3).

## Error model for this slice

PSQ-3 adds three new STOP conditions to `/commit-slice --merge` Step 5b:

1. **Default-branch-unresolvable at rebase-time**: same diagnostic shape as the existing sub-step 3 STOP — `default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved` (NAW-1 ADR-061 §Decision exit-2 contract verbiage). Exit cleanly without state mutation.
2. **Rebase conflict**: print `git status --porcelain` U-prefixed entries + `git rebase --abort` recovery hint + SOAD-1 structured options. Slice branch is left in conflict state (rebase in progress); user must `--abort` or manually continue OUTSIDE the skill.
3. **Non-conflict rebase failure**: print `git rebase --abort` hint + git's stderr verbatim. Exit without further state mutation.

All three STOPs preserve the existing /commit-slice "never auto-resolve, never bypass hooks, never force" critical-rules block.

### Re-entry semantics on user-side recovery (per /critique M2 + M6 ACCEPTED-FIXED)

The 3 SOAD-1 options at conflict-STOP each have a defined operational re-entry path:

- **Option (a) "abort rebase + investigate"**: user runs `git rebase --abort` outside the skill (or accepts the SOAD-1 option which prints the abort command for them to run). Slice branch is restored to its pre-rebase state. Worktree is clean. On re-invocation of `/commit-slice --merge`: WT-clean guardrail passes; sub-step 2 detects no un-staged files (the build-log "Files changed" list was committed in the FIRST invocation BEFORE the rebase attempt, so it is now in the slice branch's commit history and `git status --porcelain` is empty); sub-step 2 SKIPS the commit attempt; sub-step 2.5 runs `git rebase <default>` and is now subject to whatever has changed since the first attempt (if default has advanced further, may re-conflict; if user has resolved the underlying source issue in `<default>` or in slice branch, may succeed). Flow proceeds normally on success.
- **Option (b) "resolve conflicts manually + run `git rebase --continue` outside the skill"**: user resolves each U-entry file, `git add`s the resolutions, and runs `git rebase --continue` outside the skill until rebase completes. Slice branch is now at new rebased commits atop the latest default tip. On re-invocation of `/commit-slice --merge`: WT-clean guardrail passes (rebase complete); sub-step 2 detects no un-staged files (Files changed list already committed); sub-step 2 SKIPS the commit; sub-step 2.5 runs `git rebase <default>` which is now a fast-forward no-op (slice branch is at default tip post-manual-continue); flow proceeds to sub-step 3 normally + completes the merge.
- **Option (c) "cancel slice merge entirely"**: user runs `git rebase --abort` to restore the slice branch to its pre-rebase state. The skill exits cleanly leaving the worktree state unchanged from the pre-/commit-slice-invocation state. The slice branch is preserved. If the user subsequently wants to discard the slice branch entirely, they must run `git branch -D slice/NNN-<name>` manually OUTSIDE the skill (per `/commit-slice` Critical rules, the skill NEVER force-deletes). If the user wants to retry the merge later, they re-invoke `/commit-slice --merge` and start from sub-step 1.

In all three cases, the skill itself NEVER force-deletes branches, NEVER auto-resolves conflicts, and NEVER bypasses hooks — preserving the existing /commit-slice Critical rules block verbatim.

## PSQ-3 — Rule reference

- **Rule reference**: PSQ-3 (slice-073; ADR-068 mints a new rule; sibling on parallel-slice family axis; supersedes nothing; methodology v0.72.0; first rule on the *rebase-discipline* axis adjacent to PSQ-1 *queue-output* axis [[ADR-064]] + PSQ-2 *claim-machinery* axis [[ADR-067]] + BRANCH-2 *worktree-isolation* axis [[ADR-063]]).
- **Defect class**: two parallel slice branches merged sequentially into the default branch via `/commit-slice --merge` may produce silent merge conflicts at sub-step 3 (the no-ff merge), leaving the default branch in conflicted state. Without rebase-onto-default discipline, the second-to-merge slice discovers conflicts AT merge-time (all-at-once aggregate diff) rather than rebase-time (per-commit granular diff). Rebase-at-/commit-slice surfaces conflicts in the more diagnostic per-commit shape AND linearizes slice history before merge.
- **Validation**: `tests/methodology/test_commit_slice_skill_rebase_flag.py` (5 structural tests enumerated at design.md §Components — `test_step_5b_contains_git_rebase_invocation`, `test_step_5b_rebase_precedes_no_ff_merge`, `test_step_5b_rebase_target_resolved_via_canonical_2_step`, `test_step_5b_conflict_stops_with_porcelain_u_entries`, `test_step_5b_conflict_surfaces_git_rebase_abort_hint`) + `tests/methodology/test_methodology_changelog.py::test_v_0_72_0_psq_3_entry_present_in_repo` + `test_v_0_72_0_psq_3_shippability_consumer_propagation` + shippability.md row #73.

## Scope narrowing from mission brief

Mission brief AC1 said "`/commit-slice --merge` AND `/commit-slice --sync-after-pr` perform rebase before merge"; mission brief AC3 said "pin in `tools/branch_workflow_audit.py` (or a new sibling helper)". This design narrows both:

- **AC1 narrowed to `--merge` only**: `--sync-after-pr` is post-PR-merge cleanup; the PR was already merged on GitHub, and the local default is being fast-forwarded via `git pull --ff-only`. A rebase at this point would be moot (the slice branch is about to be safe-deleted). Documenting --sync-after-pr as explicitly out-of-scope (above).
- **AC3 narrowed to structural-pin tests only — NO new audit-tool module**: `git rebase` itself IS the runtime gate. It is a no-op fast-forward when the slice branch is at default tip; runs cleanly + exits 0 when behind without conflict; exits non-zero with U-prefixed conflicting files identifiable via `git status --porcelain` when behind with conflict. A separate audit-tool would duplicate `git rebase`'s own behavior with no additional safety. Structural-pin tests on SKILL.md prose catch drift in the skill's invocation of `git rebase` — analogous to how `--merge`'s `git merge --no-ff` invocation is pinned via prose-pin tests at `tests/methodology/test_commit_slice_skill_merge_flag.py` rather than a separate merge-audit module (per the existing `test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete` precedent at L44). The cross-family precedent in the parallel-slice rule family is mixed (PSQ-1 + PSQ-2 minted new tool modules because they had non-trivial library APIs to ship — queue write + claim CLI; PSQ-3 has neither — its entire surface is one extra `git rebase` invocation in SKILL.md prose).

Both narrowings were reviewed at /critique (B2 + B3 ACCEPTED-FIXED via mission-brief back-propagation; design narrowing preserved). Meta-Critic at /critique-review confirmed the narrowings and surfaced 6 additional missed findings (M-add-1 + M-add-2 + m-add-1 through m-add-4) all ACCEPTED-FIXED in-band — see `critique-review.md`. Final ratification awaits TRI-1 user triage.
