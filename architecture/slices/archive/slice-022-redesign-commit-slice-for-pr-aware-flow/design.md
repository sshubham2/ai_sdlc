# Design: Slice 022 redesign-commit-slice-for-pr-aware-flow

**Date**: 2026-05-14
**Mode**: Standard

## What's new

- `skills/commit-slice/SKILL.md` (modified): frontmatter `argument-hint` expanded `[--merge | --push | --sync-after-pr]`; new "## When to use which mode" guidance section between "## Argument modes" and "## Prerequisite check"; Step 5 restructured into 4 lettered sub-steps (5a default, 5b `--merge` unchanged, 5c `--push` NEW, 5d `--sync-after-pr` NEW); description updated to enumerate all 3 modes.
- `architecture/decisions/ADR-020-pr-aware-commit-slice-modes.md` (NEW): `supersedes: ADR-019` (partial — sub-mode (b) only); 3-mode taxonomy; post-PR-merge detection mechanism rationale.
- `methodology-changelog.md` v0.36.0 entry (NEW in-repo + installed; bidirectional sha256 byte-equality per TPHD-1).
- `tests/methodology/test_commit_slice_skill_push_flag.py` (NEW): prose-pin tests for `--push` flag surface.
- `tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py` (NEW): prose-pin tests for `--sync-after-pr` flag surface.
- `tests/methodology/test_adr_020_pr_aware_commit_slice_modes.py` (NEW): structural pins for ADR-020 supersession link + 3-mode enumeration.
- `tests/methodology/test_commit_slice_skill_merge_flag.py` (extended — slice-021): new test `test_skill_md_documents_when_to_use_which_mode_section` + `test_skill_md_merge_flow_5_steps_unchanged` (regression guard — verifies slice-021's 5-step merge body unchanged).
- `tests/methodology/test_methodology_changelog.py` (extended): `test_v_0_36_0_pr_aware_commit_slice_entry_present_in_repo_and_installed` + `test_v_0_36_0_entry_names_three_modes_in_repo_and_installed` (EPGD-1 self-application N=8 → N=9 stable target — counter aligned with methodology-changelog v0.35.0 framing per /critique M3 ACCEPTED-FIXED).
- `architecture/shippability.md` row 22 (NEW): invocation surface for all 3 modes via the slice-022 prose-pin test set.
- `plugin.yaml.version` + `VERSION` bumped 0.35.0 → 0.36.0 (PMI-1 atomic version-bump pattern N=7 → N=8).

## What's reused

- [[architecture/decisions/ADR-019-branch-per-slice-workflow]] — sub-modes (a) + (c) inherited unchanged; sub-mode (b) is what this slice supersedes.
- [[methodology-changelog.md]] — v0.35.0 entry preserved; v0.36.0 entry added below it (append-only).
- `skills/commit-slice/SKILL.md` Steps 1-4 (target slice identification + vault artifact reading + classification + Haiku-dispatch message generation) — reused unchanged for `--merge` + `--push` (skipped entirely by `--sync-after-pr` because no commit happens).
- `tools/branch_workflow_audit.py` (slice-021) — NOT modified; no new violation classes; audit's prose-pin checks for `--merge` continue to pass; audit does NOT pin `--push` or `--sync-after-pr` (out-of-scope for this slice; the audit's contract per slice-021 ADR-019 is build-time + commit-time-merge-only; PR-aware modes are post-/reflect cleanup operations, not slice-lifecycle audit targets).
- `tests/methodology/test_commit_slice_skill_drift.py` (slice-021 mini-CAD-1) — continues PASSING; byte-equality on `skills/commit-slice/SKILL.md` after each in-repo / installed sync.
- `tests/methodology/test_commit_slice_skill_merge_flag.py` (slice-021) — extended, not rewritten.
- BRANCH-1 default-branch resolution helper canonical phrase (`git symbolic-ref refs/remotes/origin/HEAD` → fallback `git config init.defaultBranch` → STOP if neither) — applied verbatim across `--merge` + `--push` + `--sync-after-pr`.

## Components touched

### `skills/commit-slice/SKILL.md`

- **Responsibility**: skill prose driving `/commit-slice` invocation; declares arguments, prerequisites, steps, mode-specific flows, and critical rules; consumed by Claude Code at runtime.
- **Lives at**: `skills/commit-slice/SKILL.md` (in-repo); `~/.claude/skills/commit-slice/SKILL.md` (installed — mini-CAD-1 byte-equal).
- **Key interactions**: invoked post-`/reflect`; reads `architecture/slices/archive/slice-NNN-*/` artifacts (Steps 1-2); dispatches to Haiku via Agent tool for message generation (Step 4); calls `git` for state-changing operations (Step 5b/5c/5d); references slice-021's `tools/branch_workflow_audit.py` only indirectly (audit runs at /build-slice, not /commit-slice).

### `architecture/decisions/ADR-020-pr-aware-commit-slice-modes.md` (NEW)

- **Responsibility**: documents the 3-mode taxonomy decision + rationale for keeping `--merge` (rather than slice-021 reflection's "drop --merge" plan) + post-PR-merge detection mechanism choice.
- **Lives at**: created by this slice.
- **Key interactions**: superseded link from ADR-019 (frontmatter `supersedes: ADR-019`; partial — body enumerates which sub-modes); referenced from methodology-changelog v0.36.0 entry; referenced from `skills/commit-slice/SKILL.md` "When to use which mode" section.

### `methodology-changelog.md`

- **Responsibility**: append-only changelog; v0.36.0 entry names the 3 modes + the supersession scope; canonical phrase pinning per TPHD-1.
- **Lives at**: repo root `methodology-changelog.md` (in-repo); `~/.claude/methodology-changelog.md` (installed — bidirectional sha256 byte-equality per TPHD-1).
- **Key interactions**: entry-pin function `_v_0_36_0_pr_aware_commit_slice_*` per EPGD-1; ADDS-only (does NOT modify slice-021's v0.35.0 entry).

## Contracts added or changed

This slice does NOT add or change any network endpoints / API contracts / event contracts. The "contracts" introduced are **command-line interface contracts** at `/commit-slice`:

### `/commit-slice --merge` (preserved from slice-021)

- **Invocation**: `/commit-slice --merge` (no positional args)
- **Behavior**: slice-021 BRANCH-1 sub-mode (b) 5-step flow + 2 pre-flight guardrails — UNCHANGED.
- **Diagnostic prose update**: the stale-slice-branch guardrail's STOP message gains a sentence pointing users to `--sync-after-pr` for post-PR-merge stragglers (legitimate state, not artefact).

### `/commit-slice --push` (NEW)

- **Invocation**: `/commit-slice --push` (no positional args)
- **Pre-flight guardrails** (run BEFORE any state change):
  1. **WT-clean check** (per slice-021 sub-mode (b) M5): `git status --porcelain` MUST return empty; non-empty → STOP.
  2. **Stale-slice-branch check** (per slice-021 sub-mode (b) Step 1): `git for-each-ref --format='%(refname)' refs/heads/slice/` — if any non-current `slice/*` branches return, STOP with diagnostic naming `--sync-after-pr` as the resolution path (NEW prose vs slice-021's "manual cleanup" diagnostic).
  3. **Origin-remote presence**: `git remote get-url origin` MUST succeed; failure → STOP with "No `origin` remote configured. `/commit-slice --push` requires an `origin` remote; configure it (`git remote add origin <url>`) before retrying."
  4. **Current-branch-is-slice-branch**: `git symbolic-ref --short HEAD` MUST start with `slice/`; otherwise → STOP. Mirrors slice-021's branch-naming discipline.
- **Flow**:
  1. Show the message + show which files will be staged on the current slice branch.
  2. Ask: "Confirm commit on `<current slice branch>`? (yes/no)" — on yes: `git add` relevant files + `git commit -m "..."` on the slice branch.
  3. Ask: "Confirm push to `origin/<current slice branch>`? (yes/no)" — on yes: `git push -u origin slice/NNN-<name>` (first-push semantics; sets upstream tracking). NEVER `--force`, NEVER `--force-with-lease`.
  4. On push success: display PR-creation hint block (see "PR-URL-hint derivation" below).
  5. Show `git log -1 origin/slice/NNN-<name>` to confirm remote received the commit.
- **PR-URL-hint derivation**:
  - Parse `git remote get-url origin`:
    - GitHub patterns (`git@github.com:OWNER/REPO.git`, `https://github.com/OWNER/REPO.git`, `https://github.com/OWNER/REPO`) → display BOTH:
      - `gh pr create --base <default> --head slice/NNN-<name> --web` (command form)
      - `https://github.com/OWNER/REPO/compare/<default>...slice/NNN-<name>` (raw compare URL)
    - Non-GitHub remote → display:
      - `gh pr create --base <default> --head slice/NNN-<name> --web` (works for any `gh`-supported host)
      - "Or open the PR via your hosting UI (compare URL format varies per platform — slice's out-of-scope for multi-remote URL derivation in v1)."
- **What `--push` does NOT do**: NOT `git checkout <default>`, NOT `git merge`, NOT `git branch -d`, NOT remote-delete. The slice branch stays present locally and remotely until the PR is merged and `/commit-slice --sync-after-pr` is invoked.

### `/commit-slice --sync-after-pr` (NEW)

- **Invocation**: `/commit-slice --sync-after-pr` (no positional args)
- **Skipped Steps**: Steps 1-4 of the skill (target slice identification, vault read, classification, message generation) are SKIPPED — no commit happens in this mode.
- **Pre-flight guardrails**:
  1. **WT-clean check**: `git status --porcelain` MUST return empty; non-empty → STOP.
  2. **Current-branch-is-slice-branch**: `git symbolic-ref --short HEAD` MUST start with `slice/`; otherwise → STOP with "`--sync-after-pr` must be invoked from the slice branch you intend to clean up; you are on `<current branch>`."
  3. **Origin-remote presence**: same as `--push`.
  4. **Slice branch has upstream tracking**: `git rev-parse --abbrev-ref --symbolic-full-name @{u}` MUST succeed (i.e., `--push` was run for this branch); failure → STOP with "Slice branch has no upstream — was `/commit-slice --push` ever run? Use `/commit-slice --merge` for solo workflows or `--push` to push first."
- **Flow**:
  1. **Sync remote refs**: `git fetch --prune origin <default> slice/NNN-<name>` (explicit refspec — Signal B requires fresh local view of `origin/<default>`; the explicit form ensures it regardless of remote.fetch config per /critique M1 ACCEPTED-FIXED).
  2. **Resolve default branch** (canonical helper — same N=3 surfaces as `--merge` + `--push`): `git symbolic-ref refs/remotes/origin/HEAD` → fallback `git config init.defaultBranch` → STOP if neither resolves.
  3. **Two-signal merged-state detection** (see "Post-PR-merge detection mechanism" below):
     - Signal A: `git ls-remote --exit-code origin slice/NNN-<name>` returns non-zero (remote branch absent — pruned because PR merged and remote auto-deleted).
     - Signal B (two-pass per /critique B2 ACCEPTED-FIXED — handles GitHub squash-merge of N>1-commit slice branches):
       - **Pass 1 (per-commit cherry-pick equivalence)**: `git cherry origin/<default> slice/NNN-<name>` returns no lines starting with `+` → Signal B=YES (every commit individually represented; covers plain merge-commit + rebase-merge + cherry-pick-equivalence + single-commit-squash).
       - **Pass 2 (aggregate-tree-diff fallback, when Pass 1 reports `+` lines)**: compute `BASE=$(git merge-base origin/<default> slice/NNN-<name>)`; build the slice's full file-set `FILES=$(git diff --name-only BASE..slice/NNN-<name>)`. Three guards apply per /critique-review M-add-5 ACCEPTED-FIXED:
         - **Empty-FILES guard** (closes data-loss false-YES path): if `FILES` is empty (slice net-changes nothing — e.g., file added then removed, or intermediate-commit churn nets to zero) → Signal B Pass 2 = **NO** (cannot determine merge state without files to compare); STOP with diagnostic "Slice has empty net file-set — `--sync-after-pr` cannot verify merge via Pass 2. Manually verify PR-merged state and use `git branch -D` only if confirmed." Do NOT proceed to destructive cleanup.
         - **Perf bound** (closes unbounded-scan path): Pass 2 scan is bounded to the most recent N=500 commits on `BASE..origin/<default>`. If `BASE..origin/<default>` exceeds 500 commits → STOP with diagnostic "Slice base is older than 500 commits behind `origin/<default>` (long-lived slice on busy default). Pass 2 scan exceeds perf bound. Manually verify PR-merged state via your PR UI and `git log origin/<default>` inspection, then use `git branch -D slice/NNN-<name>` after confirmation."
         - **Predicate (after both guards pass)**: for each commit C on `BASE..origin/<default>` (within the 500-commit bound) check whether C's **touched-file set is a superset of `FILES`** (touched ⊇ FILES — allows GitHub conflict-resolution to touch additional files during the PR merge) AND C's **tree-state at the paths in `FILES`** (intersection only) equals `slice/NNN-<name>^{tree}` at those same paths. If ANY such C exists → Signal B Pass 2 = **YES** (squash-merge detected; the matching C is the squash commit). Else → Signal B Pass 2 = **NO**.
     - **Both signals MUST agree YES** → proceed to cleanup flow.
     - **Signal A=NO** (remote branch still exists): STOP with "Remote slice branch still exists at `origin/slice/NNN-<name>`. PR may be open / unmerged / approved-but-not-merged. Resolve via your PR UI before retrying `--sync-after-pr`."
     - **Signal B=NO** (neither per-commit cherry-pick equivalence nor aggregate-tree-diff fallback matched): STOP with "Slice branch's commits are NOT yet on `origin/<default>`. PR likely not merged yet. Re-run after PR is merged. (Detected via `git cherry` Pass 1 + aggregate-tree-diff Pass 2 — both failed.)"
     - Note: Signal A=YES + Signal B=NO has two common causes (per /critique M5 ACCEPTED-FIXED): (1) PR commits don't represent the slice branch's full work — verify via `git log origin/<default>` vs `git log slice/...` AND aggregate-tree-diff at `FILES`; (2) abandoned/force-deleted PR where commits were never merged. STOP regardless and ask user to disambiguate via the printed `git diff` hints.
  4. **Cleanup flow**: ask: "Slice branch's PR appears merged + remote-deleted. Confirm local cleanup (checkout `<default>` + pull + safe-delete `slice/NNN-<name>`)? (yes/no)" — on no: ABORT cleanly.
  5. On yes: `git checkout <default>` → `git pull --ff-only origin <default>` (explicit `--ff-only` per /critique B1 ACCEPTED-FIXED — `git pull` defaults to MERGE not ff-only; if pull is non-ff or conflicts, STOP and leave repo state intact per slice-021's NEVER-auto-resolve rule) → `git branch -d slice/NNN-<name>` (safe-delete; if `-d` refuses, STOP and print the same "Safe-delete refused — inspect with `git log <default>..slice/NNN-<name>`" diagnostic as `--merge`).
  6. Show `git log -1` + `git log --graph --oneline -5` to confirm local default branch advanced past the merged slice commits.
- **What `--sync-after-pr` does NOT do**: NOT a new commit, NOT a push, NOT a force-pull. It is local-state-cleanup AFTER an external PR merge.

## Post-PR-merge detection mechanism

The mission brief notes the user's instinct: `git log --graph --oneline --all` would visually show whether origin's default branch contains the slice's commits. That works for human inspection but isn't programmatically robust — it's a renderer, not a predicate. Three programmatic candidates were considered:

| # | Mechanism | Strength | Weakness |
|---|-----------|----------|----------|
| A | `git branch --merged origin/<default> slice/...` | Simple; native git semantic | FAILS for squash-merge + rebase-merge (commit hashes differ); only catches plain merge-commit PRs |
| B | `git log origin/<default> --grep="<slice-id>"` | Catches commit-message references | Brittle — depends on PR title/squash-message format containing slice ID; user can override |
| C | `git cherry origin/<default> slice/...` | Cherry-pick aware at the **per-commit** level — reports `-` for individual commits whose patch is already represented | **Fails for GitHub squash-merge of N>1-commit slice branches** (squash combines N commits into 1; per-commit `patch-id` cannot match aggregate `patch-id`); slightly slower than (A); requires post-`git fetch` freshness |
| C+D | `git cherry` (Pass 1) + aggregate-tree-diff search (Pass 2) | Pass 1 covers single-commit-squash + merge-commit + rebase-merge + cherry-pick; Pass 2 detects multi-commit squash-merge via `git diff --name-only` file-set + tree-state comparison at touched paths | Implementation complexity higher than (C) alone; aggregate-tree-diff scan is O(commits on default since slice base) — bounded acceptably for typical repos |

**Chosen**: combine the two-pass Signal B (Mechanism C+D — `git cherry` Pass 1 + aggregate-tree-diff Pass 2 fallback) with remote-branch-absence (Signal A) — two independent signals, both must agree YES. Rationale:
- Signal A alone is insufficient: a user could `git push origin --delete slice/...` without ever merging the PR (Signal B catches that — commits not on default).
- Signal B Pass 1 alone (plain `git cherry`) is insufficient: per /critique B2 ACCEPTED-FIXED, GitHub squash-merge of N>1-commit slice branches produces precisely Signal B Pass 1 = NO even though the PR was correctly merged. Pass 2 (aggregate-tree-diff) repairs the squash-merge happy path.
- Signal B Pass 2 alone (aggregate-tree-diff scan) is more expensive than necessary for the common cases (merge-commit, rebase-merge, cherry-pick-equivalent); Pass 1 fast-paths those.
- Together: false-positive rate near zero across plain-merge, squash-merge, rebase-merge, cherry-pick-equivalence; both signals must agree for the destructive `git branch -d` action.
- (A) was rejected because the dominant PR-merge style on GitHub (the user's stated platform) is squash-merge — failing for squash-merge would be a load-bearing failure mode.
- (B) was rejected as a candidate at all (brittle prose-matching).
- (C) alone was rejected after /critique B2 demonstrated structural failure on N>1-commit squash-merge — Pass 2 fallback is mandatory.

**Reversibility note**: the two-pass Signal B (`git cherry` Pass 1 + aggregate-tree-diff Pass 2) was the chosen mechanism in v1. If Pass 2 shows performance issues at scale (very large default branch history since slice base), the aggregate-tree-diff scan can be swapped to `git log --cherry-pick --right-only origin/<default>...slice/...` (Pass 1's alternative form) bounded by a date-cutoff heuristic, OR a more sophisticated patch-id-aggregation approach. The public contract (`--sync-after-pr`'s STOP messages + two-signal semantics) is invariant under such swaps — mechanism is internal; not part of the ADR-020 commitment.

## Data model deltas

None. This slice modifies skill prose, adds an ADR, adds methodology-changelog entry, adds test files. No persistent state, no schema, no migration.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Empty (zero rows) because this slice introduces **no new Python / source modules**. All changes are skill-prose + markdown ADR + markdown changelog entry + pytest files (consumer entry points: the test framework auto-discovers `tests/methodology/test_*.py`; no additional consumer wiring required).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero-row matrix is clean per WIRE-1 audit's "zero-row clean" handling. Test files themselves are not "new modules" under WIRE-1's contract — they ARE consumer tests; their wiring is the pytest collection mechanism.)

## Decisions made (ADRs)

- [[architecture/decisions/ADR-020-pr-aware-commit-slice-modes]] — Adopt 3-mode taxonomy for `/commit-slice` post-/reflect cleanup (`--merge` for solo, `--push` for PR-based, `--sync-after-pr` for post-PR-merge local cleanup); partially supersedes ADR-019 Option 1 sub-mode (b) — reversibility: **cheap**.

**Reversibility rationale for ADR-020**: changes are confined to (i) skill prose at one SKILL.md surface in-repo + installed copy, (ii) one new ADR file, (iii) one methodology-changelog entry, (iv) 3 new test files + 2 test-file extensions, (v) one shippability row, (vi) one VERSION + plugin.yaml.version bump. No migration cost; no consumer-API change beyond the new CLI flags themselves (additive — `--merge` users see no breaking change). A future supersession (ADR-021 dropping `--merge`, or swapping detection mechanism) is similarly cheap. Total surface ≤ 30 touches matching slice-021's reversibility tag for ADR-019.

## Authorization model for this slice

- `/commit-slice --merge`: slice-021 model preserved — explicit "yes" confirmation at each of 5 merge steps; never push; never force-delete.
- `/commit-slice --push`: explicit "yes" confirmations at (a) commit-on-slice-branch step + (b) push-to-origin step; push uses `-u origin slice/...` (first-push semantics, NEVER `--force`, NEVER `--force-with-lease`); requires `origin` remote present (refuses to push to alternate remotes silently).
- `/commit-slice --sync-after-pr`: explicit "yes" confirmation at cleanup-confirm step; cleanup uses `git branch -d` (safe-delete, NEVER `-D`); pull uses **explicit `--ff-only` flag** (per /critique B1 — `git pull`'s default is MERGE not ff-only; non-ff or conflict → STOP); never deletes the branch from origin (origin-side deletion is the PR merge platform's job).

No authorization is introduced for code paths or services — this is a developer-tooling skill; "authorization" here = explicit user confirmation gates on state-changing git operations.

## Error model for this slice

| Mode | Error condition | Behavior |
|------|----------------|----------|
| any | Two or more mode flags passed (`--merge` + `--push`, etc.) | STOP — "Mode flags `--merge`, `--push`, `--sync-after-pr` are mutually exclusive; pass exactly one (or none for the slice-021 generate-only default)." (per /critique B4 ACCEPTED-FIXED) |
| `--merge` | (slice-021 errors unchanged) | (slice-021 behavior unchanged) |
| `--merge` | Stale slice branches present | STOP — diagnostic NOW points to `--sync-after-pr` for legitimate post-PR-merge stragglers (vs slice-021's "manual cleanup" prose) |
| `--push` | WT not clean | STOP — "Uncommitted changes detected. Commit or stash before `--push`." |
| `--push` | Stale slice branches present | STOP — same diagnostic as `--merge` (points to `--sync-after-pr`) |
| `--push` | Not on a `slice/*` branch | STOP — "`--push` must be invoked from a `slice/*` branch; you are on `<current branch>`." |
| `--push` | No `origin` remote configured | STOP — "No `origin` remote configured. `/commit-slice --push` requires an `origin` remote." |
| `--push` | `git push` fails (auth, network, protected-branch refusal) | STOP — propagate git's stderr verbatim; do NOT retry; do NOT `--force`. |
| `--push` | Non-ff push (remote ref has diverged from local — rebase/amend after prior push) | STOP — "Remote `origin/slice/...` has diverged from local. This typically means local history was rebased/amended after a prior push. Resolve manually (force-push intentionally via `git push --force-with-lease origin slice/...` if you confirm the rebase was correct, or `git pull --rebase` if remote has new commits). `/commit-slice --push` never force-pushes." (per /critique M4 ACCEPTED-FIXED) |
| `--push` | Fast-forward re-push (remote ref exists, local ahead by N commits) | ALLOW with explicit prompt — "Remote ref `origin/slice/...` already exists and local is ahead by N commits. Confirm fast-forward re-push? (yes/no)" — on no: ABORT cleanly. (per /critique M4 ACCEPTED-FIXED) |
| `--sync-after-pr` | WT not clean | STOP — "Uncommitted changes detected. Commit or stash before `--sync-after-pr`." |
| `--sync-after-pr` | Not on a `slice/*` branch | STOP — "`--sync-after-pr` must be invoked from the slice branch you intend to clean up; you are on `<current branch>`." |
| `--sync-after-pr` | No upstream tracking | STOP — "Slice branch has no upstream — was `/commit-slice --push` ever run? Use `--merge` for solo workflows." |
| `--sync-after-pr` | Default branch unresolvable | STOP — per BRANCH-1 canonical helper. |
| `--sync-after-pr` | Signal A=NO (remote slice branch still exists) | STOP — "Remote slice branch still exists at `origin/slice/...`. PR may be open / unmerged / approved-but-not-merged." |
| `--sync-after-pr` | Signal B=NO (neither Pass 1 nor Pass 2 matched — commits not on `origin/<default>`) | STOP — "Slice branch's commits NOT yet on `origin/<default>`. PR likely not merged yet." |
| `--sync-after-pr` | Pass 2 empty-FILES guard tripped (slice net-changes nothing) | STOP — "Slice has empty net file-set — `--sync-after-pr` cannot verify merge via Pass 2. Manually verify PR-merged state and use `git branch -D` only if confirmed." (per /critique-review M-add-5 ACCEPTED-FIXED) |
| `--sync-after-pr` | Pass 2 perf bound exceeded (slice base > 500 commits behind default) | STOP — "Slice base is older than 500 commits behind `origin/<default>` (long-lived slice on busy default). Pass 2 scan exceeds perf bound. Manually verify PR-merged state via your PR UI and `git log origin/<default>` inspection, then use `git branch -D slice/NNN-<name>` after confirmation." (per /critique-review M-add-5 ACCEPTED-FIXED) |
| `--sync-after-pr` | `git pull --ff-only` non-fast-forward (someone else pushed to default) | STOP — "Pull is non-fast-forward — `origin/<default>` has diverged. Resolve manually via `git pull --rebase` or `git merge`, then re-run `--sync-after-pr`." (per /critique B1 ACCEPTED-FIXED — explicit `--ff-only` makes this an explicit STOP, not a silent merge-commit) |
| `--sync-after-pr` | `git pull` conflict | STOP — leave repo in conflicted state; "Resolve manually, then re-run `--sync-after-pr` after `git pull` completes." |
| `--sync-after-pr` | `git checkout <default>` fails (worktree conflict — `<default>` already checked out elsewhere) | STOP — propagate git's stderr verbatim + add: "Resolve via `git worktree remove <conflicting-path>` if intentional, or run `--sync-after-pr` from the worktree where `<default>` lives." (per /critique m4 ACCEPTED-FIXED) |
| `--sync-after-pr` | `git branch -d` refuses (unmerged commits) | STOP — "Safe-delete refused — branch has unmerged commits. Inspect with `git log <default>..slice/...`. Do NOT use `-D`." |

No error path introduces a new exception class or a new structured error code — STOPs are user-facing diagnostic strings printed by the skill.

## Self-application checklist (in-house methodology)

- **TPHD-1 (3-surface harmony)**: 3 surfaces to keep harmonized at /build-slice:
  1. `skills/commit-slice/SKILL.md` (in-repo)
  2. `~/.claude/skills/commit-slice/SKILL.md` (installed; mini-CAD-1 byte-equal)
  3. `methodology-changelog.md` v0.36.0 entry (in-repo + installed; bidirectional sha256 byte-equality)
- **CAD-1**: `agents/critique.md` UNCHANGED; byte-equality on installed copy preserved (current ship hash continues).
- **PMI-1**: `plugin.yaml.version` bumped 0.35.0 → 0.36.0 at /build-slice; PMI-1 atomic-bump pattern N=7 → N=8 stable. No skill/agent/tool added or removed; PMI-1 enumeration unchanged.
- **INST-1**: `_CANONICAL_TOOLS` UNCHANGED (no new audit tool). `_CANONICAL_SKILLS` UNCHANGED (no new skill). Drift-clean.
- **EPGD-1**: new entry-pin function `_v_0_36_0_pr_aware_commit_slice_*` per pattern (slice-021 added `_v_0_35_0_branch_1_*`); ADDS-only.
- **WIRE-1**: zero new modules → empty matrix → clean per WIRE-1 zero-row handling.
- **TF-1**: 18 test-first rows (5 ACs × ~3-4 rows each — expanded from 15 to 18 per /critique B1+B4 ACCEPTED-FIXED adding 3 new rows: `test_skill_md_sync_after_pr_uses_ff_only_pull` + `test_skill_md_documents_no_flag_default_mode` + `test_skill_md_documents_mutual_exclusion_of_three_mode_flags`); `tools/test_first_audit.py --strict-pre-finish` at /build-slice pre-finish.
- **BRANCH-1**: slice-022 IS the **first** non-bootstrap canonical-reference-instance of branch-per-slice workflow (slice-021 was the bootstrap-reference-instance #1; slice-022 is the next non-/repro slice = first non-bootstrap canonical-reference-instance) — per /critique m2 ACCEPTED-FIXED off-by-one correction. slice-022 itself will run on a `slice/022-redesign-commit-slice-for-pr-aware-flow` branch per sub-mode (a); commit-time will exercise `--merge` (since slice-022 is a methodology-development project = solo dev = `--merge` is the right mode for THIS slice's own commit), validating slice-021's preservation guarantee.
- **VAL-1**: 19 enumerated changed files (per Files-changed section below) + standard slice-lifecycle file updates; standard Layer A + B sweep at /validate-slice Step 5b with `--imports-allowlist tests` (N=19 cumulative — promote-to-default candidate continues). Count aligned with L202+L226 per /critique-review M-add-3 ACCEPTED-FIXED.
- **SCPD-1 / RPCD-1**: shippability row 22 added per cross-spec parity; Command cell enumerates all prose-pin test invocations end-to-end.
- **Recursive-self-application**: slice-022 redesigns `/commit-slice` itself; slice-022's own commit will use the redesigned `/commit-slice` (specifically `--merge`, since solo-dev applies — this repo's dev model). Slice-022 thereby exercises sub-mode (b) preservation as a self-test at slice-ship.

## Files changed (summary — total 19 enumerated touches + standard slice-lifecycle file updates)

(Enumerated specifically per /critique m3 ACCEPTED-FIXED — placeholder ranges replaced with named surfaces.)

1. `skills/commit-slice/SKILL.md` (in-repo) — modified (frontmatter + new mode section + Step 5 restructure + description)
2. `~/.claude/skills/commit-slice/SKILL.md` (installed) — synced (mini-CAD-1)
3. `architecture/decisions/ADR-020-pr-aware-commit-slice-modes.md` — created
4. `methodology-changelog.md` (in-repo) — v0.36.0 entry appended
5. `~/.claude/methodology-changelog.md` (installed) — synced (TPHD-1)
6. `plugin.yaml` — version 0.35.0 → 0.36.0
7. `VERSION` — 0.35.0 → 0.36.0
8. `tests/methodology/test_commit_slice_skill_push_flag.py` — created
9. `tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py` — created
10. `tests/methodology/test_adr_020_pr_aware_commit_slice_modes.py` — created
11. `tests/methodology/test_commit_slice_skill_merge_flag.py` — extended (4 new tests per /critique B1+B4 ACCEPTED-FIXED: when-to-use-section + merge-5-steps-unchanged + no-flag-default + mutual-exclusion)
12. `tests/methodology/test_methodology_changelog.py` — extended (2 new entry-pin tests)
13. `architecture/shippability.md` — row 22 appended
14. `architecture/slices/_index.md` — slice-022 row appended (Active → 1 entry while building; archive on /reflect)
15. `architecture/slices/slice-022-redesign-commit-slice-for-pr-aware-flow/build-log.md` — created by /build-slice; appended through build phase
16. `architecture/slices/slice-022-redesign-commit-slice-for-pr-aware-flow/validation.md` — created by /validate-slice
17. `architecture/slices/slice-022-redesign-commit-slice-for-pr-aware-flow/reflection.md` — created by /reflect (archived afterward)
18. `architecture/slices/slice-022-redesign-commit-slice-for-pr-aware-flow/milestone.md` — updated continuously through slice lifecycle (already created by /slice)
19. `architecture/slices/slice-022-redesign-commit-slice-for-pr-aware-flow/critique-review.md` — created by /critique-review (mandatory per medium-tier + methodology-surface trigger)

Magnitude 19 enumerated touches matches reversibility=cheap tag. ADR-019 is NOT modified (append-only respected; SUP-1's supersession link is encoded via ADR-020's `supersedes: ADR-019` frontmatter slot alone, which the new test `test_adr_020_file_exists_and_supersedes_adr_019` discovers).
