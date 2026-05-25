# Slice 022: redesign-commit-slice-for-pr-aware-flow

**Mode**: Standard
**Estimated work**: ~6 hours (1 day max)
**Risk retired**: corrects slice-021 ADR-019 Option 1 sub-mode (b) — `/commit-slice --merge` local-only flow is structurally wrong for non-solo / protected-branch / PR-required workflows (slice-021 DEVIATION-5; all 4 Critic-stack passes missed it). Closes the `opinionated-merge-default-vs-team-workflow` design gap.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`/commit-slice` post-`/reflect` cleanup currently exposes only `--merge` (local merge into default branch + safe-delete slice branch). This is correct for solo dev with no protected master, but breaks the dominant PR-based workflow: dev cannot push to protected master, must open a PR, and after the remote merges + deletes the origin slice branch the local-state-cleanup surface is undefined. This slice keeps `--merge` (for solo) and adds a PR-aware mode that pushes the slice branch to origin (showing a PR-creation hint) plus a post-PR-merge local-cleanup mode that detects whether the local slice branch's commits have landed on `origin/<default>` (via `git branch --merged` against `origin/<default>` or equivalent) and offers a safe sync (`checkout <default>` + `pull` + safe-delete local slice branch). Together the 3 modes cover solo + PR-based + post-PR-cleanup workflows without forcing the user back to manual git.

## Acceptance criteria

1. `/commit-slice` argument contract correctly documented (per /critique B4 ACCEPTED-FIXED — folds no-flag default + mutual-exclusion into AC #1 to stay within ≤5 hard limit): (a) no-flag invocation `/commit-slice` preserves slice-021 generate-only behavior (show message + HEREDOC instruction; no git operations); (b) `/commit-slice --merge` remains functional with the slice-021 5-step flow + 2 pre-flight guardrails unchanged; (c) the 3 mode flags (`--merge`, `--push`, `--sync-after-pr`) are mutually exclusive (any combination of 2+ → STOP with explicit diagnostic); (d) `skills/commit-slice/SKILL.md` adds a prominent "When to use which mode" guidance section naming each mode's use case (`--merge` solo-dev / no-protected-branch; `--push` PR-based-workflow; `--sync-after-pr` post-PR-merge local cleanup).
2. `/commit-slice --push` flag added: runs the same WT-clean + stale-`slice/*`-branch pre-flight guardrails, then commits on the current slice branch with the generated message, then `git push -u origin slice/NNN-<name>`, then displays a PR-creation URL hint (`gh pr create` invocation OR the GitHub/GitLab compare-link URL derived from `git remote get-url origin`); the slice branch is NOT merged locally and NOT deleted; default branch is NOT touched.
3. `/commit-slice --sync-after-pr` flag added: detects whether the current local slice branch's HEAD commit is reachable from `origin/<default>` (per BRANCH-1 default-branch resolution: `git symbolic-ref refs/remotes/origin/HEAD` → fallback `git config init.defaultBranch`); if YES → offer `git checkout <default> + git pull + git branch -d slice/NNN-<name>` flow with explicit confirmation prompt; if NO → STOP with diagnostic "Local slice branch's commits NOT yet on `origin/<default>`. PR likely not merged yet. Re-run after PR is merged."; default branch resolution failure → STOP per BRANCH-1.
4. ADR-020 written at `architecture/decisions/ADR-020-pr-aware-commit-slice-modes.md` with `supersedes: ADR-019` (partial — supersedes Option 1 sub-mode (b) only; sub-modes (a) build-time branch-create + (c) audit-time pre-finish refusal stay unchanged); documents the 3-mode taxonomy + rationale for keeping `--merge` rather than dropping it + the post-PR-merge detection mechanism choice.
5. `methodology-changelog.md` v0.36.0 entry added (in-repo + installed copies, bidirectional sha256 byte-equality) naming the 3 modes; `tests/methodology/test_commit_slice_skill_merge_flag.py` extended with prose-pin tests for `--push` + `--sync-after-pr` flags; mini-CAD-1 byte-equality for `skills/commit-slice/SKILL.md` continues PASSING; shippability catalog row 22 added covering the 3-mode invocation surface.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

(Harmonized per /build-slice TPHD-1 sub-mode (c) Prerequisite-check pre-flight, 2026-05-15: TF-1 plan function-name + test-path conventions aligned with actual project convention — (a) tests in existing `test_commit_slice_skill_merge_flag.py` use `test_commit_slice_skill_md_*` prefix per slice-021 ship convention; (b) mini-CAD function in `test_commit_slice_skill_drift.py` is `test_commit_slice_skill_md_in_repo_byte_equal_installed`; (c) ADR tests live in `test_methodology_changelog.py` per slice-013 through slice-021 precedent, not separate ADR-NNN test file; (d) row 18 shippability-catalog verification follows slice-021 row 21 precedent — grep-verification embedded in shippability row's Command cell, no separate `test_shippability_*.py` file. 18 rows preserved; function-name prefix harmonized.)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_documents_when_to_use_which_mode_section | PASSING |
| 1 | prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_merge_flow_5_steps_unchanged | PASSING |
| 1 | prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_documents_no_flag_default_mode | PASSING |
| 1 | prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_documents_mutual_exclusion_of_three_mode_flags | PASSING |
| 2 | prose-pin | tests/methodology/test_commit_slice_skill_push_flag.py | test_skill_md_documents_push_flag_in_frontmatter_and_step_5 | PASSING |
| 2 | prose-pin | tests/methodology/test_commit_slice_skill_push_flag.py | test_skill_md_push_flag_does_not_merge_or_delete | PASSING |
| 2 | prose-pin | tests/methodology/test_commit_slice_skill_push_flag.py | test_skill_md_push_flag_displays_pr_creation_hint | PASSING |
| 3 | prose-pin | tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py | test_skill_md_documents_sync_after_pr_flag | PASSING |
| 3 | prose-pin | tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py | test_skill_md_sync_after_pr_uses_two_signal_detection | PASSING |
| 3 | prose-pin | tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py | test_skill_md_sync_after_pr_stops_if_not_merged | PASSING |
| 3 | prose-pin | tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py | test_skill_md_sync_after_pr_uses_branch_d_not_force_delete | PASSING |
| 3 | prose-pin | tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py | test_skill_md_sync_after_pr_uses_ff_only_pull | PASSING |
| 4 | structural | tests/methodology/test_methodology_changelog.py | test_adr_020_exists_and_supersedes_adr_019 | PASSING |
| 4 | structural | tests/methodology/test_methodology_changelog.py | test_adr_020_documents_three_mode_taxonomy | PASSING |
| 5 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_36_0_pr_aware_commit_slice_entry_present_in_repo_and_installed | PASSING |
| 5 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_36_0_entry_names_three_modes_in_repo_and_installed | PASSING |
| 5 | mini-CAD | tests/methodology/test_commit_slice_skill_drift.py | test_commit_slice_skill_md_in_repo_byte_equal_installed | PASSING |
| 5 | structural | architecture/shippability.md row 22 | grep-verification per slice-021 row 21 precedent | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `--merge` flow preserved + "When to use which mode" section added | `grep -E "When to use (which mode\|--merge\|--push)" skills/commit-slice/SKILL.md`; pytest `test_skill_md_documents_when_to_use_which_mode_section` + `test_skill_md_merge_flow_5_steps_unchanged` pass |
| 2 | `--push` flag works end-to-end | In a sandbox repo: create slice branch, run `/commit-slice --push`, verify `git ls-remote origin slice/<name>` returns the pushed ref AND default branch HEAD is unchanged AND local slice branch still exists AND PR URL hint printed; pytest `test_skill_md_documents_push_flag_in_frontmatter_and_step_5` + `test_skill_md_push_flag_does_not_merge_or_delete` + `test_skill_md_push_flag_displays_pr_creation_hint` pass |
| 3 | `--sync-after-pr` detects merged + cleans up | In a sandbox repo: simulate PR-merged state (cherry-pick or squash slice commits onto `origin/<default>`, then delete `origin/slice/<name>`), run `/commit-slice --sync-after-pr`, verify local slice branch deleted + local default branch updated; second sandbox repo with unmerged slice branch → run same command, verify STOP with "Local slice branch's commits NOT yet on `origin/<default>`" diagnostic; pytest sync-after-pr prose-pin tests pass |
| 4 | ADR-020 documents the 3-mode supersession | `grep -E "supersedes: ADR-019" architecture/decisions/ADR-020-pr-aware-commit-slice-modes.md` + pytest `test_adr_020_file_exists_and_supersedes_adr_019` + `test_adr_020_documents_three_mode_taxonomy` pass |
| 5 | v0.36.0 changelog entry + tests + mini-CAD + shippability row 22 | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_36_0_pr_aware_commit_slice_entry_present_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_v_0_36_0_entry_names_three_modes_in_repo_and_installed tests/methodology/test_commit_slice_skill_drift.py --no-header -q` all PASS; row 22 of `architecture/shippability.md` invocable end-to-end via the catalog's Command cell convention |

## Must-not-defer

- [ ] **WT-clean pre-flight on ALL 3 modes** (`--merge`, `--push`, `--sync-after-pr`): `git status --porcelain` MUST return empty; non-empty → STOP with diagnostic (carries forward slice-021 BRANCH-1 sub-mode (b) M5 ACCEPTED-PENDING guardrail).
- [ ] **Stale-slice-branch detection refresh**: the existing slice-021 guardrail ("refuse if non-current `slice/*` branches exist") MUST handle the post-PR-merge case explicitly — a slice branch lingering after remote-deletion is a legitimate state, NOT a "prior conflict-recovery artefact"; `--sync-after-pr` is precisely the mechanism that resolves it. Update the guardrail's diagnostic prose so users routed there understand to run `--sync-after-pr` instead of manual `git branch -d`.
- [ ] **Default-branch resolution failure path** (per BRANCH-1): all 3 modes use `git symbolic-ref refs/remotes/origin/HEAD` → fallback `git config init.defaultBranch` → STOP if neither resolves; no hard-coded `master`/`main` anywhere.
- [ ] **NEVER `git push --force`, NEVER `git push --force-with-lease`, NEVER remote-delete from `--push`**: `--push` is `git push -u origin slice/NNN-<name>`; first-push OR fast-forward re-push semantics ONLY; non-ff push (diverged history from rebase/amend) → STOP with documented diagnostic per /critique M4 ACCEPTED-FIXED (do NOT auto-force); user-driven force-push or remote-delete stays manual.
- [ ] **NEVER `git branch -D`**: `--sync-after-pr` uses `git branch -d` (safe-delete); if `-d` refuses, STOP with "Safe-delete refused — branch has unmerged commits. Inspect with `git log <default>..slice/NNN-<name>`. Do NOT use `-D` without understanding what's being discarded."
- [ ] **NEVER auto-resolve push conflicts / pull conflicts**: any merge/rebase conflict during `--sync-after-pr`'s `git pull` → STOP, leave repo in conflicted state for manual resolution.
- [ ] **`--sync-after-pr`'s pull invocation MUST use `--ff-only` explicitly** (per /critique B1 ACCEPTED-FIXED — `git pull`'s default is MERGE not ff-only; relying on user `pull.ff` config is brittle): the exact invocation is `git pull --ff-only origin <default>`; non-ff or conflict → STOP (do not silently create a merge commit on local default).
- [ ] **`--sync-after-pr`'s fetch invocation MUST use explicit refspec covering both `<default>` and slice branch** (per /critique M1 ACCEPTED-FIXED): the exact invocation is `git fetch --prune origin <default> slice/NNN-<name>`; Signal B requires fresh local view of `origin/<default>` regardless of remote.fetch config.
- [ ] **Mutual exclusion of mode flags** (per /critique B4 ACCEPTED-FIXED): the 3 mode flags (`--merge`, `--push`, `--sync-after-pr`) are mutually exclusive; any combination of 2+ → STOP with "Mode flags are mutually exclusive; pass exactly one (or none for the slice-021 generate-only default)." No-flag invocation preserves slice-021 generate-only behavior.
- [ ] **NEVER `--no-verify` to bypass pre-commit hooks** (carries forward from slice-021).
- [ ] **Explicit confirmation prompts on all destructive actions**: `--push`'s push action + `--sync-after-pr`'s local-branch-delete action both require explicit "yes" confirmation; non-yes → ABORT cleanly.
- [ ] **Authorization-equivalent surface**: `--push` MUST NOT silently push to a remote that isn't `origin`; if `git remote get-url origin` fails (no origin remote configured) → STOP with diagnostic, do NOT fall back to other remotes.
- [ ] **Logging**: build-log.md DEVIATION line discipline per BRANCH-1 sub-mode (a) carries forward to all 3 modes; if user skips any mode (e.g., commits manually), canonical `BRANCH=skip — rationale: <text>` line shape applies.
- [ ] **Stale shippability claim sweep**: shippability row 21 (slice-021) explicitly invokes `tests/methodology/test_commit_slice_skill_merge_flag.py` — confirm row 21's Command cell remains valid (test names not deleted) OR update row 21 in lockstep if any merge-flag prose-pin tests get refactored.

## Out of scope

- Auto-creating the PR via `gh pr create` execution (only the URL hint / command suggestion is in scope; auto-creation is a separate slice candidate — different blast radius and needs gh CLI presence detection).
- GitHub Enterprise URL derivation (per /critique B3 DEFERRED — follow-on slice `add-github-enterprise-url-derivation`): v1 handles `github.com` literal host only. Enterprise users hit the non-GitHub fallback which shows `gh pr create --base <default> --head slice/NNN --web` (works for any `gh`-configured host including Enterprise) + a "use your hosting UI" note. The raw compare URL `https://<host>/OWNER/REPO/compare/...` is NOT derived for Enterprise in v1; user opens via UI or via `gh pr create --web` browser launch. Widening to `*github*` host class deferred to the follow-on slice.
- Pipeline-wide branch discipline at upstream skills (`/slice`, `/design-slice`, `/critique`, `/critique-review`) — deferred to `add-pipeline-wide-branch-discipline-to-upstream-slice-skills` per slice-021 M-add-4 ESCALATED carveout.
- `audit-tools-default-utf8-stdout` cp1252 → utf-8 fix (N=5 cumulative; separate slice candidate).
- `/critic-calibrate slice-022 codification` of Wiegers + auto-mode-classifier-as-Critic-stack-layer + opinionated-merge-default observations (separate slice candidate; this slice produces the EMPIRICAL EVIDENCE for the codification but does not perform it).
- ADR-019 Option 1 sub-modes (a) build-time branch-create + (c) audit-time pre-finish refusal — unchanged; this slice supersedes ONLY sub-mode (b).
- Multi-remote support (slice presumes `origin` is the canonical remote; multi-remote handling = separate slice if ever needed).
- Squash-merge vs merge-commit detection nuance in `--sync-after-pr`: the detection mechanism (`git branch --merged origin/<default>` OR `git log` reachability check) is design-time choice in `/design-slice`; mission brief just commits to "detects whether slice branch's commits are on `origin/<default>`".
- `--merge` for non-solo workflows: slice-021's existing `--merge` flow is preserved AS-IS for the solo use case; the "STRUCTURALLY WRONG for non-solo" framing from slice-021 reflection is addressed by adding `--push` (the right tool for that workflow), not by removing `--merge`.

## Dependencies

- Prior slices:
  - [[architecture/slices/archive/slice-021-add-feature-branch-workflow-at-build-and-commit-slice]] — BRANCH-1 sub-modes (a) + (c) inherited unchanged; sub-mode (b) is what this slice redesigns; DEVIATION-5 is the candidate source.
  - [[architecture/slices/archive/slice-017-address-tf-1-plan-staleness-discipline]] — TPHD-1 3-surface skill-prose discipline applies (in-repo SKILL.md + installed SKILL.md + methodology-changelog harmony).
  - [[architecture/slices/archive/slice-018-cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw]] — RPCD-1 sibling-test-scoping precedent for any test-fixture state changes.
- Vault refs:
  - [[architecture/decisions/ADR-019-branch-per-slice-workflow]] — partially superseded by ADR-020 (sub-mode (b) only); supersession encoded one-directionally via ADR-020's `supersedes: ADR-019` frontmatter slot per ADR family convention (SUP-1 does NOT apply — that rule scopes to /supersede-slice for archived-slice reflection.md links, NOT ADRs; per /critique-review M-add-1 ACCEPTED-FIXED).
  - [[architecture/shippability.md]] — row 21 (slice-021) sibling; row 22 (slice-022) added per RPCD-1 / SCPD-1.
  - [[methodology-changelog.md]] — v0.35.0 (BRANCH-1) → v0.36.0 (PR-aware modes); 3-surface skill-prose harmony per TPHD-1.
- Risk register: no direct entry (slice-021 DEVIATION-5 is the source — registered as design correction, not a register risk).
- Test infrastructure:
  - `tests/methodology/test_commit_slice_skill_merge_flag.py` (slice-021) — extended with `--merge` preservation tests.
  - `tests/methodology/test_commit_slice_skill_push_flag.py` (NEW).
  - `tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py` (NEW).
  - `tests/methodology/test_adr_020_pr_aware_commit_slice_modes.py` (NEW).
  - `tests/methodology/test_commit_slice_skill_drift.py` (slice-021) — mini-CAD-1 byte-equality continues.
  - `tests/methodology/test_methodology_changelog.py` — v0.36.0 entries.

## Mid-slice smoke gate

At ~50% of build (after `--push` flow is in `skills/commit-slice/SKILL.md` + the `--push` prose-pin tests are PASSING, BEFORE `--sync-after-pr` work begins):

In a throwaway sandbox repo:
```powershell
# Setup
git init sandbox && cd sandbox
git remote add origin <test-remote-url-or-fixture>
git commit --allow-empty -m "init"
git checkout -b slice/099-smoke-test
git commit --allow-empty -m "smoke commit"

# Exercise
& $PY -m pytest tests/methodology/test_commit_slice_skill_push_flag.py tests/methodology/test_commit_slice_skill_merge_flag.py --no-header -q
& $PY -m tools.branch_workflow_audit  # slice-021 audit must still pass
```

Expected: all prose-pin tests PASS for `--push` flag; BRANCH-1 audit returns 0 violations; `--merge` flow tests remain GREEN (no regression). If any fails: STOP, diagnose, don't continue to `--sync-after-pr`.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md` (curl / git command output / pytest names per AC).
- [ ] Must-not-defer list fully addressed (14 items above all checked — count corrected per /critique-review M-add-3-sibling propagation sweep: 11 original + 3 added at /critique B1+M1+B4 ACCEPTED-FIXED).
- [ ] `/drift-check` passes (no stale references to "`--merge` is the only post-/reflect cleanup mode" anywhere — per /critique-review M-add-4 ACCEPTED-FIXED; phantom `--do-commit` parenthetical dropped since that flag never existed in the codebase).
- [ ] Mid-slice smoke still passes after `--sync-after-pr` work (no `--push` regression).
- [ ] No new TODOs / FIXMEs / debug prints in `skills/commit-slice/SKILL.md` or new test files.
- [ ] `tools/branch_workflow_audit.py` (slice-021) returns 0 violations against this slice's own /build-slice run (BRANCH-1 self-application — slice-022 IS the **first** non-bootstrap canonical-reference-instance after slice-021's bootstrap; per /critique-review M-add-2 ACCEPTED-FIXED sibling-site propagation of /critique m2 off-by-one correction).
- [ ] mini-CAD-1 byte-equality on `skills/commit-slice/SKILL.md` PASSING at slice ship.
- [ ] CAD-1 byte-equality on `agents/critique.md` preserved (untouched — slice does not modify Critic agent).
- [ ] PMI-1 + INST-1 audits clean (`plugin.yaml.version == VERSION` if a version bump is part of this slice; check at /design-slice).
- [ ] TF-1 audit `--strict-pre-finish` returns 0 PENDING / WRITTEN-FAILING rows.
- [ ] ADR-020's `supersedes: ADR-019` frontmatter slot is verified by `test_adr_020_file_exists_and_supersedes_adr_019` (one-directional encoding per ADR family convention — verified across ADR-001 through ADR-020; ADR-019 stays unmodified per append-only; SUP-1 does NOT apply because that rule scopes to /supersede-slice for archived-slice reflection.md links, NOT ADRs; per /critique-review M-add-1 ACCEPTED-FIXED).
- [ ] Shippability row 22 invocable end-to-end (Command cell runs ≤10s and exits 0).
