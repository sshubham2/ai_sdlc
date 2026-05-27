---
id: ADR-068
title: Mint PSQ-3 — rebase-onto-default discipline at /commit-slice --merge with stop-on-conflict semantics
date: 2026-05-27
slice: slice-073-add-rebase-and-conflict-discipline
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-068: Mint PSQ-3 — Rebase-and-Conflict Discipline at /commit-slice --merge

## Context

Slice-066 ([[ADR-063]], BRANCH-2) made parallel-slice work *physically possible* via per-slice worktree isolation. Slice-067 ([[ADR-064]], PSQ-1) made parallel-safe candidates *discoverable* via `architecture/slice-queue.md`. Slice-072 ([[ADR-067]], PSQ-2) added *coordination* — git-identity-anchored claim machinery so two Claude sessions don't pick the same candidate.

But the merge-time surface is still load-bearing on no-one-conflicts-with-anyone-else: two parallel slice branches that both run `/commit-slice --merge` against the same default branch sequentially will, on the second invocation, run `git merge --no-ff` against a default-branch tip that has advanced since the slice branch was branched off. If the two slices touched overlapping files, the second `--merge` STOPS at the conflicted no-ff merge with the default branch in conflicted state — the existing Step 5b sub-step 3 behavior at `skills/commit-slice/SKILL.md:174`.

This works correctly (no data loss; no silent corruption; STOP is the right verb) but the conflict surface is **aggregated all-at-once** at merge-time — every file conflict that accumulated across the slice's commit history surfaces simultaneously against the new default tip. Resolving a multi-commit slice's all-at-once aggregate conflict is harder than resolving commit-by-commit during a rebase: the developer cannot tell which specific slice commit introduced which specific conflict; they see the aggregate of the entire slice's diff against the new default's intervening commits in one pile.

Standard Linux-kernel-style discipline (the most widely-adopted parallel-development convention) is to rebase the topic branch onto the integration branch BEFORE attempting the integration merge. Rebase surfaces conflicts **per-commit, in slice-author order**, with each conflict scoped to one slice commit's diff against one intervening default commit. The developer resolves narrower diffs more confidently; the slice's history is also linearized atop the new default tip, producing a cleaner merge graph after the subsequent `git merge --no-ff`.

The slice-067 reflection nominated this exact follow-up: "PSQ-3 (slice-069 nominee): rebase + conflict discipline at /commit-slice". Slice-072's reflection re-confirmed the nomination: "The natural next slice is PSQ-3 (rebase + conflict discipline at /commit-slice)."

The decision facing this slice: **where to insert the rebase step, what to do on rebase conflict, what surface (skill prose vs new tool), and which `/commit-slice` sub-modes are in scope**.

## Options considered

1. **Rebase at /commit-slice --merge Step 5b sub-step 2.5 + stop-on-conflict + skill-prose only + structural-pin tests** (CHOSEN). Insert a new sub-step between the existing sub-step 2 (commit on slice branch) and sub-step 3 (default-branch resolution + no-ff merge). Run `git rebase <default>` on the slice branch in the worktree; surface conflict (STOP + recovery hint + SOAD-1 options) without auto-resolve. Scope to `--merge` only (`--push` delegates rebase to GitHub's PR merge-queue; `--sync-after-pr` is post-PR-merge cleanup where rebase is moot). No new tool module — the `git rebase` invocation IS the runtime gate; structural-pin tests in `tests/methodology/test_commit_slice_skill_rebase_flag.py` catch SKILL.md drift. Pros: minimal surface change (one sub-step + tests); preserves existing 5-step flow + worktree-isolation + safe-delete order; rebase-specific runtime-gate argument (`git rebase` is a no-op fast-forward at-tip / runs cleanly + exits 0 when behind without conflict / exits non-zero with U-prefixed conflicting files via `git status --porcelain` when behind with conflict — an audit-tool would duplicate `git rebase`'s own behavior with no additional safety; structural pins on SKILL.md prose mirror the existing `test_commit_slice_skill_merge_flag.py::test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete` precedent for prose-pinning a git-command invocation rather than a separate audit module); cheap reversibility (one sub-step revert); cooperative-not-adversarial threat model (PSQ-3 is for cooperating Claude sessions on the same machine — the user can always `git rebase --abort` and revisit). Cons: opinionated — overrides the developer's natural `git merge --no-ff`-only preference if they had one; rebase rewrites slice-branch history (the same commits get new SHAs atop the new default tip), which is invisible locally but matters if the slice branch was previously pushed via `--push` (PSQ-3 is `--merge` only precisely to avoid this rabbit hole).

2. **Rebase at all three sub-modes (`--merge` + `--push` + `--sync-after-pr`)**. Surface rebase across the full `/commit-slice` surface. Pros: maximal coverage; --push-time rebase produces clean PR linear history without relying on GitHub's PR merge-queue. Cons: `--push` time rebase rewrites slice history that the developer may have already pushed via an earlier `--push` (or that a CI run already consumed); `--sync-after-pr` is post-PR-merge — the PR is already integrated on GitHub, rebase is moot. Surfacing rebase at `--push` creates a force-push trap (the second `--push` would refuse non-ff push, per the existing Step 5c sub-step 3 error sub-path) and would push PSQ-3 into the `--force-with-lease` thicket. Best deferred: scope v1 to `--merge` only; add `--push` time rebase as a future PSQ-4 if real demand emerges.

3. **New audit-tool module `tools/psq_3_rebase_audit.py`** wired into `/commit-slice` Step 5b sub-step 2.5 as a callable runtime gate (exit 0 if at-tip / exit 1 if behind / exit 2 if default-unresolvable), with SKILL.md prose invoking the tool BEFORE `git rebase` to decide whether to even attempt the rebase. Pros: explicit audit-tool surface mirrors NAW-1 / PSQ-1 / PSQ-2 each-rule-gets-its-own-tool pattern. Cons: the tool would duplicate what `git rebase` already does — `git rebase` IS the runtime gate by construction. It is a no-op fast-forward when the slice branch is at default tip (exit 0, no state mutation); it runs cleanly + exits 0 when behind without conflict; it exits non-zero with U-prefixed conflicting files identifiable via `git status --porcelain` when behind with conflict. The audit-tool adds a syscall + module + PMI-1 fan-out (BC-PROJ-9 5-inventory propagation, INST-1 tool-list update, plugin.yaml registration, install_audit.py addition, INSTALL.md tool-count literal × 2 sites — N=10 cumulative inclusive precedent burden) for zero behavioral gain. Structural pins on SKILL.md prose (PSQ-3 v1 approach) catch drift in the skill's invocation of `git rebase` — analogous to how `--merge`'s `git merge --no-ff` invocation is pinned via prose-pin tests at `tests/methodology/test_commit_slice_skill_merge_flag.py::test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete` rather than a separate merge-audit module. The cross-family precedent in the parallel-slice rule family is mixed: PSQ-1 + PSQ-2 minted new tool modules because they had non-trivial library APIs to ship (queue write + claim CLI); PSQ-3 has neither — its entire surface is one extra `git rebase` invocation in SKILL.md prose, so the tool-module shape genuinely buys no additional verification surface.

4. **Rebase + auto-resolve via `-X theirs` or `-X ours`**. Run `git rebase -X theirs <default>` to resolve conflicts in favor of the default branch (or `-X ours` for slice branch). Pros: zero stops; full automation. Cons: auto-resolve is exactly the anti-pattern slice-021's `/commit-slice` Must-not-defer block forbids ("NEVER auto-resolve merge conflicts" — preserved across slice-022 + slice-072). Silently resolving a conflict in favor of one side discards real intent from the other side; the slice's tests may pass after `-X theirs` resolves slice's changes to defaults, but the production behavior is broken. This option is structurally incompatible with the existing safety contract.

5. **Skill prose only — no structural-pin tests + no methodology-changelog entry + no ADR + no version bump**. Treat rebase-at-/commit-slice as a quiet skill-prose addition without minting a new rule. Pros: minimum overhead. Cons: violates MEPD-1 (Inclusion-heuristic firing on new-mechanism slices is N=11 cumulative — slice-049/050/051/057/058/059/060/063/064/067/072 precedent); the rebase step is behavior-changing (a slice acceptable yesterday — direct no-ff merge from outdated slice branch — would be refused today via the conflict-STOP gate); the changelog entry IS the audit trail for behavior changes per the file's own opening "If a slice acceptable yesterday would be refused today (or vice versa), it's a changelog entry." Skipping the changelog entry would orphan the rule from the methodology audit surface.

## Decision

Adopt **Option 1: rebase at /commit-slice --merge Step 5b sub-step 2.5 + stop-on-conflict + skill-prose only + structural-pin tests**.

This decision **mints PSQ-3 (Parallel-Slice Queue Rebase-and-Conflict Discipline)** — a new RULE-ID on the parallel-slice family axis, sibling to PSQ-1 (queue-output) + PSQ-2 (claim-machinery). PSQ-3 refines NO existing rule, supersedes nothing, and is the first rule on the *rebase-discipline* axis adjacent to (not extending) the *queue-output* axis (PSQ-1) + *claim-machinery* axis (PSQ-2) + *worktree-isolation* axis (BRANCH-2).

Concrete shape:

- `skills/commit-slice/SKILL.md` Step 5b gains a NEW sub-step 2.5 between existing sub-step 2 (commit on slice branch) and sub-step 3 (default-branch resolution + checkout + no-ff merge). The new sub-step:
  1. Resolves the default branch using the canonical 2-step pattern (primary `git symbolic-ref refs/remotes/origin/HEAD` + fallback `git config init.defaultBranch`; STOP exit 2 if neither resolves — same diagnostic shape as NAW-1's ADR-061 §Decision exit-2 contract).
  2. Runs `git rebase <default>` on the slice branch (slice branch is the current worktree checkout per BRANCH-2).
  3. On clean rebase or fast-forward no-op: proceed to sub-step 3 (unchanged).
  4. On rebase conflict: STOP. Print conflicting file paths (from `git status --porcelain` U-prefixed entries) + `git rebase --abort` recovery hint. Surface SOAD-1 structured options: (a) abort rebase + investigate; (b) resolve conflicts manually + run `git rebase --continue` outside the skill; (c) cancel slice merge entirely. Do NOT proceed to sub-step 3 (default-checkout), do NOT delete worktree or branch.
- Scope is **`--merge` only**. `--push` and `--sync-after-pr` are explicitly out of scope (documented in §Consequences below + design.md §Out of scope).
- NO new tool module — the `git rebase` invocation IS the runtime gate. Structural pins in NEW `tests/methodology/test_commit_slice_skill_rebase_flag.py` catch SKILL.md drift. This mirrors the existing `test_commit_slice_skill_merge_flag.py::test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete` precedent — `--merge`'s `git merge --no-ff` invocation is pinned via prose-pin tests rather than a separate merge-audit module. The cross-family precedent in the parallel-slice rule family is mixed (PSQ-1 + PSQ-2 minted new tool modules because they had non-trivial library APIs to ship — queue write + claim CLI; PSQ-3 has neither — its entire surface is one extra `git rebase` invocation in SKILL.md prose, so the tool-module shape genuinely buys no additional verification surface).
- methodology-changelog.md gains a `## v0.72.0` entry minting PSQ-3 + 5-part PMI-1 atomic bump 0.71.0 → 0.72.0 (VERSION + plugin.yaml.version + pyproject.toml [project].version + `## v0.72.0` header + installed `~/.claude/ai-sdlc-VERSION`).
- BC-PROJ-10 paired-pin pair: `test_v_0_72_0_psq_3_entry_present_in_repo` + `test_v_0_72_0_psq_3_shippability_consumer_propagation` in `tests/methodology/test_methodology_changelog.py`.
- shippability.md row #73 citing both paired-pin tests + the new structural-pin module.

## Consequences

**Components affected**:

- `skills/commit-slice/SKILL.md` (MODIFIED, OSDG-1-guarded): Step 5b sub-step 2.5 insertion + cross-link to ADR-068 + cross-link to PSQ-3 rule reference. Step 5c (`--push`) + Step 5d (`--sync-after-pr`) UNCHANGED.
- `tests/methodology/test_commit_slice_skill_rebase_flag.py` (NEW, 5 structural tests enumerated at design.md §Components, ~120 LOC): prose-pin tests for the rebase invocation literal + ordering + canonical-2-step default-branch resolution + conflict-STOP language + recovery-hint literal.
- `methodology-changelog.md` (NEW v0.72.0 entry) mints PSQ-3.
- `architecture/decisions/ADR-068-mint-psq-3-rebase-and-conflict-discipline.md` (NEW — this file).
- `tests/methodology/test_methodology_changelog.py` gains BC-PROJ-10 paired-pin pair `test_v_0_72_0_psq_3_entry_present_in_repo` + `test_v_0_72_0_psq_3_shippability_consumer_propagation`.
- `architecture/shippability.md` row #73 (NEW) — citing both paired-pin tests + the new structural-pin module.
- `VERSION` / `plugin.yaml.version` / `pyproject.toml [project].version` / `methodology-changelog.md ## v0.72.0` header / installed `~/.claude/ai-sdlc-VERSION` bumped 0.71.0 → 0.72.0 (5-part PMI-1 atomic per slice-067/072 v0.71.0 canonical legs).
- Separately, post-bump TVFS-1 re-install of `ai-sdlc-tools` (`$PY -m pip install --upgrade .`) + MCFS-1 forward-sync of `methodology-changelog.md` → `~/.claude/methodology-changelog.md` + OSDG-1 forward-sync of `skills/commit-slice/SKILL.md` → `~/.claude/skills/commit-slice/SKILL.md` — NOT PMI-1 legs (per slice-063 M-add-1 leg-enumeration discipline).

**Contracts implied**:

- The rebase invocation MUST appear in `skills/commit-slice/SKILL.md` Step 5b AFTER sub-step 2 (commit on slice branch) and BEFORE sub-step 3 (default checkout + no-ff merge). Ordering is load-bearing — rebase BEFORE default-checkout ensures the slice branch is the rebase subject (a rebase from the default branch would mis-rebase the wrong direction).
- The default-branch resolution at sub-step 2.5 MUST use the same 2-step pattern as sub-step 3 (primary `git symbolic-ref refs/remotes/origin/HEAD` + fallback `git config init.defaultBranch`) — divergent resolution would create a footgun where rebase targets a different default than merge.
- The conflict-STOP path MUST NOT proceed to default-checkout, merge, worktree-remove, or branch-delete. The slice branch is left in rebase-in-progress state; user-driven recovery is the only path forward. This preserves the existing /commit-slice Must-not-defer "NEVER auto-resolve" contract.
- A future PSQ-4+ slice MAY extend rebase to `--push` (with force-push-with-lease semantics for re-pushes) or `--sync-after-pr`. PSQ-3 v1 scope is **only `--merge`**; future expansion is allowed but not required.

**Identity model implications**: PSQ-3 has no ownership/identity contract — it's a procedural rule (run rebase before merge). PSQ-2's git-identity claim mechanism is independent of PSQ-3; the two rules layer cleanly (PSQ-2 prevents two sessions from picking the same candidate; PSQ-3 cleans up after both sessions when their separately-claimed slices integrate sequentially).

**Adversarial model**: PSQ-3 is cooperative-not-adversarial, mirroring PSQ-2's threat model (per ADR-067 §"Identity model implications"). The rule's purpose is to make sequential `--merge`s from cooperating Claude sessions reliable; a malicious actor with local write access to the worktree can always bypass any methodology rule by editing files directly. PSQ-3 is NOT a security boundary; it's a coordination convention.

**Future flexibility**:

- A future PSQ-4 could add `--push` time rebase (with `--force-with-lease` for re-pushes) — explicitly deferred from v1 per §Options-#2.
- A future PSQ-5 could add `--rebase-merges` strategy preservation for slices with merge commits inside their own history — currently a non-issue because slices have linear history by convention.
- A future PSQ-6 could add merge-driver registration for known-safe auto-resolution patterns (e.g., methodology-changelog.md additive append) — currently forbidden per the "NEVER auto-resolve" critical-rules block.
- If PSQ-3 turns out to be wrong (e.g., the rebase rewrites cause downstream consumer breakage), the rollback is: revert the SKILL.md sub-step 2.5 insertion (~10-line revert) + delete the structural-pin test module + remove the v0.72.0 entry from methodology-changelog.md + revoke PSQ-3 via a new ADR superseding this one + revert the PMI-1 atomic bump 0.72.0 → 0.71.0. Cheap by every axis.

**Lineage**: PSQ-3 is the third rule on the parallel-slice family axis (PSQ-1 minted by slice-067; PSQ-2 by slice-072; PSQ-3 by this slice). The four layers are structurally complementary, not nested: BRANCH-2 (physical isolation) + PSQ-1 (discoverability) + PSQ-2 (coordination) + PSQ-3 (merge-conflict resolution) collectively shape multi-session parallel work. [[ADR-064]] §Decision predicted this lineage at L37 ("PSQ-3 (slice-069 nominee): rebase + conflict discipline at /commit-slice"); slice-072 reflection re-confirmed the nomination. PSQ-3 v1 closes the local-merge surface; the post-PR-merge surface (via GitHub PR merge-queue) is intentionally delegated to GitHub.

**Inclusion-heuristic posture**: this slice mints a new RULE-ID + adds new user-visible behavior at `/commit-slice --merge` (a slice acceptable yesterday — direct merge of an outdated slice branch — gains a new conflict-STOP gate today) + extends the methodology-changelog stable surface additively. Per the slice-049/050/051/057/058/059/060/063/064/067/072 precedent for new-mechanism slices (N=11 cumulative inclusive precedent), full Inclusion-heuristic firing applies: methodology-changelog entry + new ADR (this one) + 5-part PMI-1 atomic bump + new shippability row + BC-PROJ-10 paired-pin pair. NOT a voluntary-restraint slice (voluntary-restraint applies to retirement-discharge / in-family-extension shapes; PSQ-3 is a new-mechanism mint on a new rule-axis).

## Reversibility

**Cheap**. Rollback cost:

- Revert `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 insertion (~10-line revert) + OSDG-1 forward-sync re-do (~1-line installed-copy revert).
- Delete `tests/methodology/test_commit_slice_skill_rebase_flag.py` (~120 LOC).
- Remove the v0.72.0 entry from `methodology-changelog.md` (append-only retroactive removal is permitted ONLY when the rule it minted is itself revoked — per slice-071 SUP-1 §Append-only-of-DECISIONS-not-of-FACTS interpretation precedent).
- Remove the BC-PROJ-10 paired-pin pair from `tests/methodology/test_methodology_changelog.py`.
- Revoke PSQ-3 via a new ADR superseding this one (ADR-068 stays per append-only ADR discipline; the new ADR documents the revocation rationale).
- Remove `architecture/shippability.md` row #73.
- Revert PMI-1 atomic bump 0.72.0 → 0.71.0 (all 5 legs).
- Optional cleanup: revert MCFS-1 + OSDG-1 forward-syncs (low cost; auto-resyncs on next install).

Total estimated rollback: ~1 hour of mechanical work, no consumer migrations (no downstream PSQ-4+ shipped that depends on PSQ-3), no data conversions, no API surface breakage.

The cheap reversibility tag is **load-bearing**: PSQ-3 deliberately ships rebase-at-`--merge`-only as a *narrow* v1 surface so that if real-world usage surfaces a structural issue (e.g., rebase-rewrites-cause-CI-breakage-on-some-orgs), we can iterate cheaply on the rule shape without rework on PSQ-1 / PSQ-2 / BRANCH-2. The four parallel-slice family rules are deliberately four separate ADRs — not one combined ADR — precisely to preserve this iteration option (per the slice-067 reflection nomination + slice-072 reflection re-confirmation + ADR-064 §Decision lineage).
