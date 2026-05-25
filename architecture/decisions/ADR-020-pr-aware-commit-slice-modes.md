---
id: ADR-020
title: /commit-slice supports 3 post-/reflect modes — --merge for solo, --push for PR-based, --sync-after-pr for post-PR-merge local cleanup
date: 2026-05-14
slice: slice-022-redesign-commit-slice-for-pr-aware-flow
reversibility: cheap
status: accepted
supersedes: ADR-019
---

# ADR-020: PR-aware /commit-slice modes (--merge | --push | --sync-after-pr)

## Context

Slice-021 (ADR-019) introduced `/commit-slice --merge` as the post-/reflect slice-branch cleanup mode under BRANCH-1 sub-mode (b). The flow: commit on slice branch → `git checkout <default>` → `git merge --no-ff slice/...` → safe-delete slice branch. All 4 Critic-stack passes during slice-021 evaluated `--merge` as a self-contained local-only flow and missed that local-only semantics is **structurally wrong** for the dominant team workflow:

1. **Protected-branch repos** — `git checkout master + git merge` will succeed locally but `git push origin master` will fail (or worse, succeed-but-blocked-by-branch-protection-policy server-side, leaving local + remote out of sync).
2. **Required-PR repos** — local merge bypasses required code review (whether human or CI-gated).
3. **CI-gated repos** — local merge skips CI evaluation on the slice branch in isolation (the very point of feature-branch CI).

The realization surfaced as slice-021 DEVIATION-5 ("`/commit-slice --merge` is structurally wrong for non-solo projects") and was queued for slice-022 as HIGHEST PRIORITY.

The slice-021 reflection's initial slice-022 plan was: **DROP `--merge` entirely; replace with `--push`** (push slice branch to origin, user opens PR + merges via UI).

Refined position (this slice): the solo-dev case is real (this very repo is solo-dev with no protected branches and no required PRs); `--merge` is correct AND fast there; dropping it would force solo users into 2 extra ceremonial steps (push + UI merge) with no quality gain. The right move is to ADD `--push` rather than REPLACE `--merge`. A third mode (`--sync-after-pr`) closes the post-PR-merge local-state-cleanup gap that `--push` alone leaves open: dev pushes via `--push`, opens PR, PR gets merged + remote-branch-deleted server-side, but local slice branch + local default branch are now stale.

## Options considered

1. **Drop `--merge`, replace with `--push` only** (slice-021 reflection's initial plan) — pros: forces "right way" for team projects; one less mode to maintain. Cons: punishes solo-dev case (this repo's own dev model); adds 2 ceremonial steps per slice with no quality gain; leaves post-PR-merge local-cleanup undefined.

2. **Keep `--merge`, add `--push`, add `--sync-after-pr`** (chosen) — pros: covers all 3 real workflows (solo, PR-based, post-PR cleanup); `--merge` preservation means slice-022 itself ships via `--merge` (self-application validates preservation); `--sync-after-pr` closes the post-PR-merge gap explicitly. Cons: 3 modes is more SKILL.md surface to maintain; 3-mode taxonomy must be documented prominently so users pick the right one.

3. **Keep `--merge`, add `--push` only** (no `--sync-after-pr`) — pros: 2-mode is simpler. Cons: post-PR-merge local cleanup remains undefined; users have to `git checkout default && git pull && git branch -d slice/...` manually + must figure out whether the PR was merged (especially under squash-merge where commit hashes differ); the very BRANCH-1 audit's stale-slice-branch refusal will fire on legitimate post-PR-merge stragglers and the diagnostic has no resolution path to point at.

4. **Keep `--merge`, add `--push`, defer `--sync-after-pr` to a follow-on slice** — pros: ships value sooner. Cons: leaves slice-022's own consumers (PR-workflow users) with an obvious gap on day 1; the slice-021 stale-slice-branch refusal diagnostic has no resolution path; deferral surface area is small (`--sync-after-pr` is ~80 lines of skill prose + 4 prose-pin tests). Not worth splitting.

## Decision

**Adopt 3-mode taxonomy**:

- `/commit-slice --merge` — solo-dev / no-protected-branch path. Slice-021 BRANCH-1 sub-mode (b) 5-step flow + 2 pre-flight guardrails UNCHANGED.
- `/commit-slice --push` — PR-based-workflow path. WT-clean + stale-branch + origin-present + slice-branch-name pre-flight guardrails; commit on slice branch; push to `origin/slice/NNN-<name>` with `-u` (first-push); display PR-creation URL hint + `gh pr create` command. Never merges, never deletes, never touches default branch.
- `/commit-slice --sync-after-pr` — post-PR-merge local-cleanup path. Skips message-generation steps. Pre-flight: WT-clean + slice-branch + origin-present + upstream-tracking. Two-signal merged-state detection: (A) `git ls-remote origin slice/NNN-<name>` returns non-zero (remote branch absent — pruned because PR merged + remote auto-deleted) AND (B) two-pass commit-reachability — Pass 1 `git cherry origin/<default> slice/NNN-<name>` returns no `+` lines (per-commit cherry-pick equivalence — covers plain merge-commit + rebase-merge + cherry-pick + single-commit-squash); Pass 2 fallback aggregate-tree-diff search (`git diff --name-only BASE..slice/NNN` file-set + tree-state comparison at touched paths against `BASE..origin/<default>` commits — covers GitHub squash-merge of N>1-commit slice branches per /critique B2 ACCEPTED-FIXED). Both signals must agree YES; otherwise STOP with specific diagnostic. On YES: explicit-confirm + `git checkout <default>` + `git pull --ff-only` (explicit flag per /critique B1 ACCEPTED-FIXED — `git pull`'s default is MERGE not ff-only) + `git branch -d` (safe-delete).

**Mutual exclusion**: the 3 mode flags (`--merge`, `--push`, `--sync-after-pr`) are mutually exclusive (per /critique B4 ACCEPTED-FIXED). Combining any 2 → STOP with diagnostic. No-flag invocation preserves slice-021 generate-only behavior (show message + HEREDOC instruction; no git operations).

**Post-PR-merge detection mechanism**: two-signal (`git ls-remote` for remote-absence + two-pass `git cherry` + aggregate-tree-diff for commit-reachability). The naive single-pass `git cherry` was rejected during /critique B2 because `git cherry`'s patch-equivalence is **per-commit** — GitHub's "Squash and merge" produces ONE combined commit whose aggregate diff cannot match any individual slice-branch commit's `patch-id` when N>1 commits are squashed. The two-pass Signal B repairs this: Pass 1 (`git cherry`) is the fast path for plain merge-commit / rebase-merge / cherry-pick-equivalence / single-commit-squash; Pass 2 (aggregate-tree-diff search) catches the dominant GitHub squash-merge-of-multi-commit-slice happy path. The two-signal approach (A + B) guards against either-signal false positives.

## Consequences

**Supersession scope (partial)**:
- ADR-019 Option 1 **sub-mode (a)** [build-time branch-create at /build-slice ## Prerequisite check ### Branch state] — UNCHANGED. Slice-022 inherits and exercises this sub-mode at its own /build-slice.
- ADR-019 Option 1 **sub-mode (b)** [commit-time `--merge` flow] — SUPERSEDED in scope: ADR-020 introduces 3 modes where ADR-019 had 1. The `--merge` flow's BEHAVIOR is preserved verbatim; what's superseded is the IMPLICIT CLAIM that `--merge` is the only / default post-/reflect cleanup path. Under ADR-020, `--merge` is one of three explicit modes.
- ADR-019 Option 1 **sub-mode (c)** [audit-time pre-finish refusal in /build-slice Step 6 via `tools/branch_workflow_audit.py`] — UNCHANGED. The audit's scope remains build-time + commit-time-merge-only; `--push` + `--sync-after-pr` are post-/reflect operations that fall OUTSIDE the audit's contract.

**Downstream effects**:
- `skills/commit-slice/SKILL.md` gains a "## When to use which mode" guidance section and a restructured Step 5 (5a default / 5b `--merge` / 5c `--push` / 5d `--sync-after-pr`).
- `methodology-changelog.md` v0.36.0 entry names all 3 modes + the partial-supersession scope.
- `tools/branch_workflow_audit.py` (slice-021) is NOT modified. Its contract (build-time branch-create discipline + commit-time `--merge` flow integrity) is invariant under ADR-020 because `--merge` is preserved verbatim.
- New prose-pin tests at `tests/methodology/test_commit_slice_skill_push_flag.py` + `tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py` + structural pin at `tests/methodology/test_adr_020_pr_aware_commit_slice_modes.py`.
- `architecture/shippability.md` row 22 covers all 3 modes' prose-pin test surface.
- Slice-021's deferred candidate `add-merge-conflict-recovery-to-commit-slice-merge` is downgraded — `--push`'s flow has no merge-conflict surface, so users hitting `--merge` conflicts can now switch to `--push` + PR-based resolution as the workaround. Conflict recovery in `--merge` itself remains deferred (not blocking under ADR-020).

**Scope limitations (v1 — per /critique B3 DEFERRED)**: PR-creation URL derivation in `--push` handles `github.com` literal host only. GitHub Enterprise Server / Enterprise Cloud custom-host users see the non-GitHub fallback which displays `gh pr create --base <default> --head slice/NNN --web` (this command works for any `gh`-configured host, including Enterprise) + a "use your hosting UI" note. The raw compare URL (`https://<host>/OWNER/REPO/compare/<default>...slice/NNN`) is NOT derived for Enterprise in v1. Widening to `*github*` host class (e.g., via `gh repo view --json url` delegation or wider regex) is deferred to follow-on slice `add-github-enterprise-url-derivation`. Rationale: this repo's own dev environment is github.com; `gh pr create --web` works for Enterprise users; the cost of Enterprise URL derivation is non-trivial (~1hr + tests + Enterprise CI fixture); better as a focused slice with explicit Enterprise validation.

**Surface area**: ≤ 30 file touches (per design.md "Files changed" summary). Matches the cheap-reversibility tag.

## Reversibility

**Tag: cheap.** Justification:

- Public CLI contract change is purely **additive** for `--merge` users (the flag still works identically; `--push` + `--sync-after-pr` are new). No migration cost for existing solo-dev workflows.
- All changes are confined to: 1 skill prose surface (in-repo + installed copy), 1 new ADR, 1 changelog entry, 3 new test files + 2 test-file extensions, 1 shippability row, 1 version bump. No source-code module added; no compiled artefact; no persistent state; no consumer API beyond the CLI flags themselves.
- Future supersession path (e.g., dropping `--merge` after N=∞ slices of solo-dev validation, OR swapping the two-pass detection mechanism's Pass 2 from aggregate-tree-diff scan to a patch-id-aggregation approach) is similarly cheap: write ADR-021 with `supersedes: ADR-020`, update SKILL.md prose, version-bump, ship. No state-migration concern.
- The mechanism choice (two-pass `git cherry` + aggregate-tree-diff Pass 2) is documented as INTERNAL — swapping either pass to an equivalent primitive (e.g., Pass 1 to `git log --cherry-pick --right-only origin/<default>...slice/...`; Pass 2 to a different file-set / tree-state comparison strategy) is not an ADR-level change because the user-facing STOP messages and two-signal semantics are unchanged. The reversibility statement covers the 3-mode taxonomy commitment + the two-pass discipline, not the specific primitive choice within each pass.
- The GitHub Enterprise URL derivation limitation (v1 scope) is documented as a follow-on slice candidate, not a permanent contract; widening from `github.com` literal to `*github*` host class costs ~1hr and is reversibility-cheap.

A future move from 3 modes to 2 (dropping `--merge` if solo-dev disappears as a use case) or 3 to 4 (adding `--rebase-onto-default` for the squash-merge-resistant case) would each be a similar-cost cheap supersession. ADR-020 commits the project to 3 modes for the foreseeable horizon but doesn't lock the door against future evolution.
