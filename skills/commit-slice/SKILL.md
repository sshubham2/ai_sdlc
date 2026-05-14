---
name: commit-slice
description: "Generate an audit-grade commit message from a just-completed slice's vault artifacts. Pulls subject/body/refs from mission-brief.md, build-log.md, validation.md, and new ADRs. Produces conventional-commit-style output with slice folder reference, ADR IDs, AC count, Critic blockers addressed, and shippability entry — no hand-crafting required. Run right before committing code (after /reflect, which auto-archives the slice). Three mutually-exclusive mode flags (per ADR-020): with --merge (BRANCH-1 sub-mode (b) — local-merge into default + safe-delete; solo-dev / no-protected-branch path); with --push (push slice branch to origin + display PR-creation URL hint; PR-based workflow path); with --sync-after-pr (post-PR-merge local cleanup via two-signal merged-state detection + safe-delete; post-PR-merge cleanup path). No-flag invocation preserves slice-021 generate-only default. Trigger phrases: '/commit-slice', 'generate commit message', 'audit commit', 'slice commit message', '/commit-slice --merge', '/commit-slice --push', '/commit-slice --sync-after-pr'."
user_invokable: true
argument-hint: [--merge | --push | --sync-after-pr]
---

# /commit-slice — Audit-Grade Commit from Vault

You generate a commit message for the just-completed slice, pulling structured content from the slice's vault artifacts. No hand-crafting. No "wip" commits. Every slice gets a clean, consistent, audit-ready commit.

## Where this fits

Runs after `/reflect` (which auto-archives the slice). The slice folder is now at `architecture/slices/archive/slice-NNN-<name>/`.

Also useful mid-slice: `/commit-slice` can generate intermediate commits using the partial state (build-log so far + ACs passed so far), but those are optional; most value is at slice completion.

Heavy mode benefits most — compliance trails want consistent commit format referencing slices + ADRs.

## Argument modes

- `/commit-slice` — generate the message, show it to user, user copies to `git commit -m` (no-flag default; slice-021 generate-only behavior preserved per ADR-020)
- `/commit-slice --merge` — generate + run `git add` + `git commit` on the current slice branch + no-ff merge into default branch + safe-delete the slice branch (per **BRANCH-1** sub-mode (b))
- `/commit-slice --push` — generate + run `git add` + `git commit` on the current slice branch + `git push -u origin slice/NNN-<name>` + display PR-creation URL hint (per **ADR-020**; PR-based workflow path; never merges locally, never deletes)
- `/commit-slice --sync-after-pr` — post-PR-merge local cleanup (no commit; skips Steps 1-4): two-signal merged-state detection then safe `git checkout <default> + git pull --ff-only + git branch -d slice/NNN-<name>` (per **ADR-020**; post-PR-merge cleanup workflow)

The 3 mode flags are **mutually exclusive** — passing two or more → STOP with "Mode flags `--merge`, `--push`, `--sync-after-pr` are mutually exclusive; pass exactly one (or none for the slice-021 generate-only default)."

Default: generate only. Mode flags require user confirmation at multiple checkpoints before executing git commands; see Step 5 for the per-mode flows.

## When to use which mode

Pick the mode that matches your repo's contribution workflow:

- **`--merge`** — **solo-dev / no-protected-branch path**. Use when you have direct push access to the default branch AND there's no required-PR / required-review / CI-gate policy. The fastest path: local merge + safe-delete the slice branch in one skill invocation. Don't use if your team has protected branches or required PR review — your local merge will fail at `git push` (or worse, succeed locally and diverge from origin's required-review-gated state).

- **`--push`** — **PR-based workflow path**. Use when the default branch is protected OR your team requires PR review OR CI must evaluate the slice branch in isolation. The skill pushes the slice branch to `origin/slice/NNN-<name>` and displays a `gh pr create` command + (for GitHub.com remotes) a raw compare URL. You open the PR (manually or via the displayed `gh` command), reviewers approve, the PR merges on GitHub, the origin branch is auto-deleted. Local cleanup happens later via `--sync-after-pr`.

- **`--sync-after-pr`** — **post-PR-merge local cleanup path**. Use AFTER your PR (opened post-`--push`) has been merged AND the origin slice branch has been auto-deleted. The skill detects the merged state via two independent signals (remote-branch absence via `git ls-remote` + commit-reachability on `origin/<default>` via `git cherry` Pass 1 + aggregate-tree-diff Pass 2 fallback for multi-commit GitHub squash-merge) and, on confirmation, runs `git checkout <default> + git pull --ff-only + git branch -d slice/NNN-<name>`. STOPs with diagnostic if either signal disagrees.

Per **ADR-020** the 3 modes are mutually exclusive; the no-flag default (generate only, no git operations) remains the slice-021 behavior unchanged.

## Prerequisite check

- Most recently archived slice folder exists (`architecture/slices/archive/slice-NNN-*/`)
- That folder has `reflection.md` (slice completed)
- OR an active slice exists with `build-log.md` (for mid-slice commits)

If no slice artifacts found: stop. Tell user to run `/reflect` first (or if mid-slice: no data yet).

## Your task

### Step 1: Identify the target slice

Default: most recently archived slice (highest slice number in `slices/archive/`).

If `--merge` and multiple uncommitted slices exist: ask user which to commit (or commit them in order, one per commit).

### Step 2: Read vault artifacts

From the target slice folder, read:

- `mission-brief.md` → intent (first paragraph), acceptance criteria (count)
- `critique.md` (if exists) → blocker count + "addressed" status
- `build-log.md` → files changed, deferrals (if any)
- `validation.md` → per-AC PASS/FAIL, shippability regression status
- `reflection.md` → "Validated" items, any design corrections

Also read:
- New ADRs that reference this slice (`grep -l "slice: slice-NNN" architecture/decisions/`)
- Relevant shippability.md entry (added by this slice)

### Step 3: Classify the slice type

Pick the conventional commit type from mission brief intent:

- "add X" → `feat`
- "fix X" → `fix`
- "refactor X" / "reduce X" → `refactor`
- "improve X" / performance → `perf`
- "update tests" / "add tests" → `test`
- "migrate X" → `chore` (or `feat` if user-facing)
- "update docs" → `docs`

If ambiguous: `feat` is the default.

Scope: derived from slice name area (e.g., `slice-023-add-receipt-ocr` → scope `receipt`).

### Step 4: Generate the commit message via Haiku dispatch

Per **COST-1** (cost-optimized model selection — `methodology-changelog.md` v0.4.0), this step is template-filling and dispatches to a Haiku subagent rather than running on the main thread's model.

**Dispatch:**
- Use the Agent tool with `subagent_type: "general-purpose"` and `model: haiku`.
- Hand the agent a structured input dict gathered in Step 2: `{type, scope, slice_id, slice_path, intent_one_line, body_2_3_sentences, ac_pass, ac_total, critic_blockers, adrs, shippability_entry_n, shippability_entry_text, deferrals, regressions, mode, do_commit_flag}`.
- Hand the agent the template + example below as the spec it fills.
- The agent returns the commit message string. Main thread either presents it (default) or runs the 5-step merge flow (Step 5 with `--merge`).

The main thread does not generate the message text — Haiku does. The main thread is responsible for input gathering (Step 2) and execution (Step 5).

**Why Haiku**: this is structured-data → template rendering. The cognitive demand is filling slots from the input dict, not synthesis or reasoning. Haiku is faster and cheaper for this; quality is unchanged because no judgment is required.

**Format** (the dispatched agent fills this):

```
<type>(<scope>): slice-NNN — <one-line intent from mission brief>

<body paragraph: what was built / changed, in 2-3 sentences>

Slice: [slice-NNN-<name>](architecture/slices/archive/slice-NNN-<name>/)
Acceptance criteria: <X>/<Y> PASS (see validation.md)
Critic blockers addressed: <list or "none">
ADRs: <ADR-NNN, ADR-MMM> (or "none")
Shippability entry: #<N> — <one-line>
<if deferrals: "Deferred: <summary> (see reflection.md)">
<if regressions caught: "Regression caught: <summary>">
```

Example output:

```
feat(receipt): slice-023 — HEIC/PNG/JPEG receipt upload with thumbnail

Adds POST /transactions/:id/receipt accepting images up to 10MB
with authorization restricted to transaction owner. Generates
200x200 WebP thumbnails via Pillow + pyheif (for HEIC).

Slice: architecture/slices/archive/slice-023-add-receipt-upload/
Acceptance criteria: 5/5 PASS (see validation.md)
Critic blockers addressed: B1 (authz check), B2 (MIME validation strategy)
ADRs: ADR-008 (object-storage-thumbnails)
Shippability entry: #15 — POST /receipts HEIC with correct EXIF preserved
Deferred: re-invitation cancellation flow (→ slice-024 candidate)
```

For Heavy mode: add extra lines for compliance:

```
Reviewer sign-offs: <from critique.md + validation.md>
Compliance: <applicable frameworks from non-functional.md>
```

### Step 5: Present or execute

The 3 mode flags are **mutually exclusive** (per ADR-020 + /critique B4 ACCEPTED-FIXED). If the user passes two or more, STOP with diagnostic: "Mode flags `--merge`, `--push`, `--sync-after-pr` are mutually exclusive; pass exactly one (or none for the slice-021 generate-only default)."

#### Step 5a: Default (no flag)

Show the message to user with instruction:

```
Copy this to your commit command:

git commit -m "$(cat <<'EOF'
<full message>
EOF
)"
```

Note: HEREDOC format to preserve newlines and special characters. The no-flag default preserves slice-021 generate-only behavior — no git operations are executed.

#### Step 5b: With `--merge` (per **BRANCH-1** sub-mode (b), `methodology-changelog.md` v0.35.0 — solo-dev / no-protected-branch path)

Per slice-022 AC #1 + ADR-020: the slice-021 `--merge` 5-step flow + 2 pre-flight guardrails are preserved verbatim. Behavior is unchanged; what's superseded is the implicit claim that `--merge` is the only post-/reflect cleanup path.

Pre-flight guardrails (run BEFORE any state change):
1. **Stale-slice-branch check** (per /critique B5 ACCEPTED-PENDING — refuse if prior conflict-recovery left orphan branches): `git for-each-ref --format='%(refname)' refs/heads/slice/` — if any non-current `slice/*` branches return, STOP. Print: "Stale slice branches detected: `<list>`. For legitimate post-PR-merge stragglers, run `/commit-slice --sync-after-pr` on each. For other artefacts of prior unresolved conflicts, resolve manually (`git branch -d` each, after verifying merged) before retrying `--merge`."
2. **WT-clean check** (per /critique M5 ACCEPTED-PENDING — closes silent-WT-discard local-state-loss path): `git status --porcelain` MUST return empty. If non-empty, STOP. Print: "Uncommitted changes detected. Commit or stash before `--merge` (closes silent-WT-discard path)."

Then the 5-step merge flow:

1. Show the message + show which files will be staged (`git status` before commit) on the current slice branch.
2. Ask: "Confirm commit on `<current slice branch>`? (yes/no)" — on yes: `git add` the relevant files (source code touched in this slice — from build-log.md's "Files changed" section), then `git commit -m "..."` on the slice branch with the generated message.
3. Resolve default branch (per **BRANCH-1** + /critique M1 ACCEPTED-PENDING — no hard-coded `master`/`main`): `default=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')`; fallback `default=$(git config init.defaultBranch)`. STOP if neither resolves. Then `git checkout $default` + `git merge --no-ff slice/NNN-<name> -m "Merge slice/NNN-<name>: <intent>"`. If conflict: STOP. Leave default-branch in conflicted state. Print: "Merge conflict at `<files>`. Resolve manually, then `git commit` to finalize the merge. Do NOT re-run `/commit-slice --merge` post-conflict — the slice branch will linger; cleanup is manual in v1 (recovery flow deferred to follow-on slice `add-merge-conflict-recovery-to-commit-slice-merge`)."
4. Ask explicit confirmation (per /critique M5 ACCEPTED-PENDING — closes unrecoverable-without-push local-state-loss path): "Confirm merge + delete? (yes/no)" — on no: ABORT skill cleanly, leave merged slice branch present for user inspection.
5. `git branch -d slice/NNN-<name>` (safe-delete, local only; NEVER `-D`; if `-d` refuses, STOP and print: "Safe-delete refused (branch has unmerged commits). Inspect with `git log <default>..slice/NNN-<name>`. Do NOT use `-D` without understanding what's being discarded.").
6. Show `git log -1` + `git log --graph --oneline -5` to confirm merge commit + slice attribution preserved.

**Critical rules for `--merge`**:
- NEVER `git push`, NEVER `git push --force`, NEVER remote-delete (push is a separate user-driven action — use `--push` for PR-based workflows).
- NEVER `git branch -D` (force-delete) — safe-delete only.
- NEVER auto-resolve merge conflicts.
- NEVER `--no-verify` to bypass pre-commit hooks.

Do NOT push. Push is a separate action with its own confirmation flow (use `--push`).

#### Step 5c: With `--push` (per **ADR-020**, `methodology-changelog.md` v0.36.0 — PR-based workflow path)

`--push` commits on the current slice branch and pushes to `origin/slice/NNN-<name>` for downstream PR creation. Never merges locally, never deletes the slice branch, never touches the default branch.

Pre-flight guardrails (run BEFORE any state change):

1. **WT-clean check**: `git status --porcelain` MUST return empty. If non-empty, STOP. Print: "Uncommitted changes detected. Commit or stash before `--push`."
2. **Stale-slice-branch check**: `git for-each-ref --format='%(refname)' refs/heads/slice/` — if any non-current `slice/*` branches return, STOP. Print: "Stale slice branches detected: `<list>`. For legitimate post-PR-merge stragglers, run `/commit-slice --sync-after-pr` on each. For other artefacts, resolve manually before retrying `--push`."
3. **Current-branch-is-slice-branch**: `git symbolic-ref --short HEAD` MUST start with `slice/`. Otherwise STOP. Print: "`--push` must be invoked from a `slice/*` branch; you are on `<current branch>`."
4. **Origin-remote presence**: `git remote get-url origin` MUST succeed. If it fails, STOP. Print: "No `origin` remote configured. `/commit-slice --push` requires an `origin` remote; configure it (`git remote add origin <url>`) before retrying. `--push` never falls back to alternate remotes silently."

Then the 5-step push flow:

1. Show the message + show which files will be staged (`git status` before commit) on the current slice branch.
2. Ask: "Confirm commit on `<current slice branch>`? (yes/no)" — on yes: `git add` the relevant files (source code touched in this slice — from build-log.md's "Files changed" section), then `git commit -m "..."` on the slice branch with the generated message.
3. Ask: "Confirm push to `origin/<current slice branch>`? (yes/no)" — on yes: `git push -u origin slice/NNN-<name>` (first-push semantics; sets upstream tracking). NEVER `--force`, NEVER `--force-with-lease`. Two error sub-paths (per /critique M4 ACCEPTED-FIXED):
   - **Non-ff push** (remote ref has diverged from local — typically rebase/amend after prior `--push`): STOP. Print: "Remote `origin/slice/NNN-<name>` has diverged from local. This typically means local history was rebased/amended after a prior push. Resolve manually (force-push intentionally via `git push --force-with-lease origin slice/NNN-<name>` if you confirm the rebase was correct, or `git pull --rebase` if remote has new commits). `/commit-slice --push` never force-pushes."
   - **Fast-forward re-push** (remote ref exists and local is ahead by N commits): ASK explicit confirmation: "Remote ref `origin/slice/NNN-<name>` already exists and local is ahead by N commits. Confirm fast-forward re-push? (yes/no)" — on no: ABORT cleanly.
4. On push success: display the PR-creation hint block.
   - **GitHub.com origin remote** (URL matches `git@github.com:OWNER/REPO`, `https://github.com/OWNER/REPO[.git]`, or `ssh://git@github.com/OWNER/REPO`): display BOTH:
     - `gh pr create --base <default> --head slice/NNN-<name> --web` (command form — works for any `gh`-supported host including GitHub Enterprise via `gh` config)
     - `https://github.com/OWNER/REPO/compare/<default>...slice/NNN-<name>` (raw browser-openable compare URL)
   - **Non-GitHub.com remotes** (GitLab, Bitbucket, GitHub Enterprise custom-host — Enterprise URL derivation deferred per ADR-020 to follow-on slice `add-github-enterprise-url-derivation`): display ONLY `gh pr create --base <default> --head slice/NNN-<name> --web` + a note "Or open the PR via your hosting UI (compare URL format varies per platform — slice's out-of-scope for multi-remote URL derivation in v1)."
5. Show `git log -1 origin/slice/NNN-<name>` to confirm remote received the commit.

**What `--push` does NOT do**: NOT `git checkout <default>`, NOT `git merge`, NOT `git branch -d`, NOT remote-delete. The slice branch stays present locally and remotely until the PR is merged and `/commit-slice --sync-after-pr` is invoked. `--push` is NOT merged locally and NOT deleted; default branch is NOT touched.

**Critical rules for `--push`**:
- NEVER `git push --force`, NEVER `git push --force-with-lease` (force-push remains user-driven manual action).
- NEVER auto-create the PR via `gh pr create` execution — display the command/URL only.
- NEVER push to a remote other than `origin`.
- NEVER `--no-verify` to bypass pre-commit hooks.

#### Step 5d: With `--sync-after-pr` (per **ADR-020**, `methodology-changelog.md` v0.36.0 — post-PR-merge local cleanup path)

`--sync-after-pr` is the resolution path for the PR-based workflow: dev ran `--push`, opened PR, reviewers approved, PR merged on GitHub, origin slice branch auto-deleted. `--sync-after-pr` detects the merged state and cleans up local default + slice branch.

`--sync-after-pr` SKIPS Steps 1-4 (no commit message is generated — the PR has already been merged externally; this mode is local-state cleanup only).

Pre-flight guardrails (run BEFORE any state change):

1. **WT-clean check**: `git status --porcelain` MUST return empty. If non-empty, STOP. Print: "Uncommitted changes detected. Commit or stash before `--sync-after-pr`."
2. **Current-branch-is-slice-branch**: `git symbolic-ref --short HEAD` MUST start with `slice/`. Otherwise STOP. Print: "`--sync-after-pr` must be invoked from the slice branch you intend to clean up; you are on `<current branch>`."
3. **Origin-remote presence**: `git remote get-url origin` MUST succeed (same as `--push`).
4. **Slice branch has upstream tracking**: `git rev-parse --abbrev-ref --symbolic-full-name @{u}` MUST succeed (i.e., `--push` was run for this branch previously). Otherwise STOP. Print: "Slice branch has no upstream — was `/commit-slice --push` ever run? Use `/commit-slice --merge` for solo workflows or `--push` to push first."

Then the cleanup flow:

1. **Sync remote refs**: `git fetch --prune origin <default> slice/NNN-<name>` (explicit refspec per /critique M1 ACCEPTED-FIXED — Signal B requires fresh local view of `origin/<default>`; the explicit form ensures it regardless of remote.fetch config).
2. **Resolve default branch** (per BRANCH-1 canonical helper — same N=3 surfaces as `--merge` + `--push`):
   ```
   default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
   # STOP if neither resolves
   ```
3. **Two-signal merged-state detection**:
   - **Signal A**: `git ls-remote --exit-code origin slice/NNN-<name>` returns non-zero (remote branch absent — pruned because PR merged and remote auto-deleted).
   - **Signal B (two-pass — per /critique B2 ACCEPTED-FIXED + /critique-review M-add-5 ACCEPTED-FIXED — handles GitHub squash-merge of N>1-commit slice branches)**:
     - **Pass 1 (per-commit cherry-pick equivalence)**: `git cherry origin/<default> slice/NNN-<name>` returns no lines starting with `+` → Signal B=YES (every commit individually represented; covers plain merge-commit + rebase-merge + cherry-pick-equivalence + single-commit-squash).
     - **Pass 2 (aggregate-tree-diff fallback, when Pass 1 reports `+` lines)**: compute `BASE=$(git merge-base origin/<default> slice/NNN-<name>)`; build the slice's full file-set `FILES=$(git diff --name-only BASE..slice/NNN-<name>)`. Three guards apply:
       - **Empty-FILES guard** (closes data-loss false-YES path): if `FILES` is empty (slice net-changes nothing — e.g., file added then removed, or intermediate-commit churn nets to zero) → Signal B Pass 2 = **NO**; STOP with diagnostic "Slice has empty net file-set — `--sync-after-pr` cannot verify merge via Pass 2. Manually verify PR-merged state and use `git branch -D` only if confirmed."
       - **Perf bound** (closes unbounded-scan path): Pass 2 scan is bounded to the most recent N=500 commits on `BASE..origin/<default>`. If `BASE..origin/<default>` exceeds 500 commits → STOP with diagnostic "Slice base is older than 500 commits behind `origin/<default>` (long-lived slice on busy default). Pass 2 scan exceeds perf bound. Manually verify PR-merged state via your PR UI and `git log origin/<default>` inspection, then use `git branch -D slice/NNN-<name>` after confirmation."
       - **Predicate** (after both guards pass): for each commit C on `BASE..origin/<default>` (within the 500-commit bound) check whether C's **touched-file set is a superset of `FILES`** (touched ⊇ FILES — allows GitHub conflict-resolution to touch additional files during the PR merge) AND C's **tree-state at the paths in `FILES`** (intersection only) equals `slice/NNN-<name>^{tree}` at those same paths. If ANY such C exists → Signal B Pass 2 = **YES** (squash-merge detected; the matching C is the squash commit). Else → Signal B Pass 2 = **NO**.
   - **Both signals MUST agree YES** → proceed to cleanup flow.
   - **Signal A=NO** (remote branch still exists at `origin/slice/NNN-<name>`): STOP. Print: "Remote slice branch still exists at `origin/slice/NNN-<name>`. PR may be open / unmerged / approved-but-not-merged. Resolve via your PR UI before retrying `--sync-after-pr`."
   - **Signal B=NO** (neither Pass 1 nor Pass 2 matched — commits NOT yet on `origin/<default>`): STOP. Print: "Slice branch's commits are NOT yet on `origin/<default>`. PR likely not merged yet. Re-run after PR is merged. (Detected via `git cherry` Pass 1 + aggregate-tree-diff Pass 2 — both failed.)"
   - **Signal A=YES + Signal B=NO has two common causes** (per /critique M5 ACCEPTED-FIXED): (1) PR commits don't represent the slice branch's full work — verify via `git log origin/<default>` vs `git log slice/...` AND aggregate-tree-diff at `FILES`; (2) abandoned/force-deleted PR where commits were never merged. STOP regardless and ask user to disambiguate via the printed `git diff` hints.
4. **Cleanup flow**: ask: "Slice branch's PR appears merged + remote-deleted. Confirm local cleanup (checkout `<default>` + pull --ff-only + safe-delete `slice/NNN-<name>`)? (yes/no)" — on no: ABORT cleanly.
5. On yes: `git checkout <default>` → `git pull --ff-only origin <default>` (explicit `--ff-only` per /critique B1 ACCEPTED-FIXED — `git pull`'s default is MERGE not ff-only; if pull is non-ff or conflicts, STOP and leave repo state intact per slice-021's NEVER-auto-resolve rule) → `git branch -d slice/NNN-<name>` (safe-delete; if `-d` refuses, STOP and print "Safe-delete refused — branch has unmerged commits. Inspect with `git log <default>..slice/NNN-<name>`. Do NOT use `-D` without understanding what's being discarded.").
6. Show `git log -1` + `git log --graph --oneline -5` to confirm local default branch advanced past the merged slice commits.

If `git checkout <default>` fails because `<default>` is already checked out in another worktree, STOP and print git's stderr + add: "Resolve via `git worktree remove <conflicting-path>` if intentional, or run `--sync-after-pr` from the worktree where `<default>` lives."

**What `--sync-after-pr` does NOT do**: NOT a new commit (skips Steps 1-4), NOT a push, NOT a force-pull. It is local-state-cleanup AFTER an external PR merge.

**Critical rules for `--sync-after-pr`**:
- NEVER `git branch -D` (force-delete) — safe-delete only; if `-d` refuses, STOP with diagnostic.
- NEVER auto-resolve merge/rebase conflicts during `git pull --ff-only` — STOP, leave repo in conflicted state.
- NEVER omit the explicit `--ff-only` flag from `git pull` — `git pull`'s default is MERGE, which would silently create a merge commit on the local default branch.
- NEVER omit the explicit fetch refspec — Signal B requires fresh local view of `origin/<default>`.
- NEVER skip the two-signal AND (Signal A AND Signal B both YES) — destructive `git branch -d` requires both signals confirming.
- NEVER `--no-verify` to bypass pre-commit hooks.

### Step 6: Handle edge cases

- **Slice has deferrals**: note them in commit body; they're part of the audit trail
- **Shippability regression caught**: if /validate-slice caught + fixed a regression during this slice, note it in the body ("Caught and fixed regression in slice-018's sync test")
- **No new ADRs**: state "ADRs: none" — don't omit the line (audit expects consistent format)
- **Critic CLEAN with no fixes**: "Critic blockers addressed: none (design passed review)"

## Critical rules

- NEVER fabricate content. Every field comes from an actual vault file.
- If a field is missing (e.g., no critique.md in Minimal mode): say "Critic: skipped (Minimal mode)" not omit.
- With `--merge`: always show the message + staged files BEFORE committing on the slice branch; show the merge plan BEFORE `git checkout <default>`; show the safe-delete plan BEFORE `git branch -d`. Wait for explicit "yes" at each checkpoint.
- NEVER `--no-verify`. Pre-commit hooks (like `/drift-check`) exist for a reason; don't bypass.
- NEVER push. Push requires user decision.
- CONSISTENT FORMAT. Every slice's commit looks the same shape. Audit tools scan for these patterns.

## For Minimal mode

Slices in Minimal often skip /critique. Commit message adapts:

```
feat(scan): slice-001 — folder scan with duplicate CSV report

Walks directory, computes perceptual hash via imagehash, groups by distance.
Emits CSV with cluster_id, file_path, hash.

Slice: architecture/slices/archive/slice-001-scan-folder-emit-csv/
Acceptance criteria: 5/5 PASS
Critic: skipped (Minimal mode)
ADRs: ADR-001 (phash-library)
Shippability entry: #1 — scan-folder produces expected CSV for 50-file test set
```

## For brownfield / bug-fix slices

When the slice was preceded by `/repro`: note the reproduction in the body.

```
fix(receipt): slice-024 — HEIC >5MB upload no longer times out

Reproduction established in /repro (failing test in tests/bugs/). Fix:
switch from sync S3 PUT to multipart upload for files >5MB; bump timeout
to 60s. Reproduction test now passes.

Slice: architecture/slices/archive/slice-024-fix-heic-timeout/
Acceptance criteria: 3/3 PASS
Critic blockers addressed: B1 (progress feedback to client during multipart)
ADRs: ADR-014 (multipart-upload-threshold)
Shippability entry: #23 — POST /receipts HEIC >5MB returns 201 within 10s
Reproduction test added: tests/bugs/test_receipt_upload_heic_timeout.py
```

## Anti-patterns

- **Hand-editing the generated message**: if something feels off, fix the underlying vault file (mission-brief, reflection) — the message is a view; inconsistency means the vault is inconsistent.
- **Amending past commits with updated messages**: don't. The commit is a snapshot of what was true at commit time.
- **Multiple slices per commit**: one slice per commit. If two are ready: two commits.

## Next step

- Message shown → user commits (or skill commits + merges + safe-deletes with `--merge`)
- After commit: next slice begins via `/slice` (or `/status` to re-orient)
