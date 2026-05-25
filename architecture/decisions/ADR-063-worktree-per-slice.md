---
id: ADR-063
title: Worktree-per-slice + branch partial-supersedes BRANCH-1 sub-mode (a) and extends sub-mode (c)
date: 2026-05-24
slice: slice-066-add-worktree-per-slice-discipline
reversibility: cheap
status: accepted
supersedes: ADR-019
---

# ADR-063: Worktree-per-slice + branch (BRANCH-2)

## Context

[[ADR-019]] minted **BRANCH-1** (slice-021, methodology v0.35.0) as a 3-sub-mode audit-enforced discipline: (a) build-time branch-create at `/build-slice` `## Prerequisite check ### Branch state` via `git checkout -b slice/NNN-<slice-name>` on the main working tree; (b) `/commit-slice --merge` integrates back via no-ff merge + safe-deletes the slice branch (LOCAL-ONLY-v1); (c) `/build-slice` Step 6 pre-finish refusal via `tools/branch_workflow_audit.py`.

ADR-019 sub-mode (b) was **already partial-superseded by [[ADR-020]]** at slice-022 (methodology v0.36.0 L637-638) — ADR-020 added the 3-mode `/commit-slice` taxonomy (`--merge` / `--push` / `--sync-after-pr`) but preserved the `--merge` 5-step flow's BEHAVIOR verbatim. Sub-modes (a) build-time branch-create + (c) audit-time pre-finish refusal remained unchanged through ADR-020.

Two structural exposures accumulated on the surviving sub-modes:

1. **R-17** (`risk-register.md:284`, discovered slice-061, status `mitigating`): BRANCH-1's `git checkout -b` does not mechanically verify a clean working tree before creating the slice branch. The skill prose says "STOP on dirty tree" but the audit (which runs at /build-slice Step 6 pre-finish, NOT pre-create) cannot enforce pre-create cleanliness — so uncommitted slice-A WIP on the main tree at slice-B's branch-create time silently contaminates slice-B's first commit. R-17's risk-register entry explicitly names two candidate fixes: (a) a pre-create cleanliness audit, OR (b) `git worktree add ../<repo>-wt/slice-NNN-<name> -b slice/NNN-<name>` — "the canonical git-tooling answer for 'I need to work on slice-B while slice-A WIP sits on disk'".

2. **Parallel-slice physical-isolation gap** (user-stated 2026-05-24): the project's next-quarter direction is parallel-slice work — multiple sessions/agents picking from a top-10 parallel-safe queue. BRANCH-1's single-working-tree model makes parallelism impossible: two sessions sharing one tree corrupt each other on the first `checkout -b`. Slice-067 (`add-parallel-slice-queue-output`) + slice-068 (`add-slice-queue-claim-state-machine`) + slice-069 (`add-rebase-and-conflict-discipline`) collectively layer the parallel-work capability ON TOP OF physical isolation; ADR-063 is the prerequisite.

## Options considered

1. **Fix R-17 with the candidate-fix-(a) clean-tree audit (no worktree)** — extend `tools/branch_workflow_audit.py` with a pre-create mode that refuses on non-empty `git status --porcelain` unless the dirty files are exclusively slice-internal. Pros: smaller surface change; preserves single-tree mental model. Cons: doesn't address the parallel-slice physical-isolation gap (any future parallelism slice would have to re-add worktrees on top); doesn't close the second exposure user surfaced.

2. **Fix R-17 with the candidate-fix-(b) worktree-per-slice (this ADR)** — replace `git checkout -b` on main tree with `git worktree add ../<repo>-wt/slice-NNN-<name> -b slice/NNN-<name>`; teardown via `git worktree remove` at `/commit-slice --merge` and `--sync-after-pr`. Pros: closes BOTH exposures structurally (uncommitted slice-A WIP cannot reach slice-B's worktree filesystem; parallel slices each get their own filesystem); reversibility cheap (1 ADR + 1 audit-module revert); aligns with the canonical git-tooling answer for the use case. Cons: dev mental model adds `cd <wt-path>` step; worktree teardown order is load-bearing (must precede branch-delete — confirmed via [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree)); main + worktree's `<default>` and `slice/*` can race if dev forgets to `cd` (closed via `worktree-cwd-mismatch` violation per slice-066 /critique B3 ACCEPTED-FIXED).

3. **Mint both BRANCH-2 (worktree mode) AND a clean-tree audit (defense-in-depth)** — adopt option 2 AND keep option 1's pre-create cleanliness audit. Pros: layered defense. Cons: redundant — option 2 makes the WIP-contamination class structurally impossible, so the cleanliness audit becomes a Maginot Line catching a class that can no longer fire. Over-engineering; defer to slice-067+ if a residual exposure emerges.

## Decision

Adopt **option 2**: mint **BRANCH-2** — worktree-per-slice + branch.

- `/build-slice` `## Prerequisite check ### Branch state` creates `git worktree add <main-parent>/<main-name>-wt/slice-NNN-<name> -b slice/NNN-<name> <default>` and instructs Claude to `cd` into the worktree.
- `/commit-slice --merge` cleanup: `cd <main-tree>` → `git checkout <default>` → `git merge --no-ff slice/NNN-<name>` → confirm → **idempotent worktree-remove guard** (skip if no worktree exists for the slice — covers bootstrap window + future `WORKTREE=skip` slices per slice-066 /critique B5 ACCEPTED-FIXED) → `git worktree remove <wt-path>` → `git branch -d slice/NNN-<name>`. Order is load-bearing: worktree-remove MUST precede branch-delete (a branch checked out in a worktree cannot be safely deleted).
- `/commit-slice --push` UNCHANGED: the worktree stays alive through the PR-review window, mirroring the slice branch's lifecycle (per user confirmation 2026-05-24 — symmetric with the branch's lifetime).
- `/commit-slice --sync-after-pr` cleanup: existing flow extended with `cd <main-tree>` + idempotent worktree-remove guard + `git worktree remove <wt-path>` after the existing `git pull --ff-only` and before the existing `git branch -d`.
- `tools/branch_workflow_audit.py` gains worktree-mode awareness: 4 new violation kinds (`worktree-not-registered`, `worktree-cwd-mismatch`, `worktree-path-shape-violation`, `worktree-skip-malformed` — per slice-066 /critique m1 ACCEPTED-FIXED count harmonized at 4), 3 new helpers (`_resolve_expected_worktree_path`, `_is_repo_root_a_worktree`, `_worktree_registered`), and a new `WORKTREE=skip` escape-hatch grammar (mirrors `BRANCH=skip`'s shape with a new keyword).
- The canonical worktree path convention is `<main-parent>/<main-name>-wt/slice-NNN-<name>` (sibling directory). For this project: `<HOME>\ai_sdlc-wt\slice-NNN-<name>`. Per user confirmation 2026-05-24 (option 1 of 3 in the structured ask).
- R-17 transitions `mitigating` → `retired` with citation in this ADR + the methodology-changelog v0.68.0 entry.

## Scope of supersession

Per the slice-022 [[ADR-020]] partial-supersession encoding pattern (single `supersedes:` frontmatter slot + body-level scope enumeration; ADR-019 stays unmodified per append-only). **This is the N=2 application of the pattern in this codebase** (per slice-066 /critique m2 ACCEPTED-FIXED), after slice-022 ADR-020 partial-superseding the same ADR-019 sub-mode (b) at N=1. ADR-019 is therefore now twice-partial-superseded: ADR-020 covers sub-mode (b), this ADR covers sub-mode (a) + extends sub-mode (c). The append-only rule holds across N=2 supersessions; no edit-in-place of ADR-019 occurs.

**Superseded by this ADR (ADR-019 claims that no longer hold)**:
- ADR-019 sub-mode (a) — build-time branch-create on main tree via `git checkout -b slice/NNN-<slice-name>` from current HEAD. Post-slice-066, that step is `git worktree add <main-parent>/<main-name>-wt/slice-NNN-<name> -b slice/NNN-<name> <default>` followed by `cd <wt-path>`. The slice's commits accrue in the worktree's HEAD, isolated from the main tree's filesystem.
- ADR-019's implicit claim that the `BRANCH=skip` Events-line escape-hatch is the sole skip mechanism. Post-slice-066, the new `WORKTREE=skip` escape-hatch handles the worktree-discipline-skip case (used for the slice-066 bootstrap discharge + any future legacy/edge-case slice that must run on the bare main tree); `BRANCH=skip` is preserved as a parallel legacy escape for slices that pre-dated BRANCH-2 OR explicitly opt-out of branch isolation while still using worktree mode (rare; documented but not the default escape).

**Extended in place (ADR-019 claims that BRANCH-2 keeps but augments)**:
- ADR-019 sub-mode (c) — `/build-slice` Step 6 pre-finish refusal via `tools/branch_workflow_audit.py` — REMAINS the audit-time gate; BRANCH-2 ADDS 4 new violation kinds (`worktree-not-registered`, `worktree-cwd-mismatch`, `worktree-path-shape-violation`, `worktree-skip-malformed`) to the existing 7 (`on-default-branch`, `slice-branch-mismatch`, `escape-hatch-malformed`, `default-branch-unresolvable`, `stale-slice-branch`, `usage-error`, plus the slice-043 ADR-046 split-slice-folder-convention diagnostic). The audit's binary exit-code contract (0 clean / 1 violations / 2 usage) is preserved.

**Carried forward unchanged (ADR-019 claims that BRANCH-2 inherits)**:
- The slice-branch naming convention `slice/NNN-<slice-name>` (zero-padded 3-digit; numeric-only per ADR-046 / R-6 retirement) is unchanged. The worktree's checked-out branch IS the same slice branch.
- The default-branch resolver (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → STOP) at `tools/branch_workflow_audit.py:127` is unchanged.
- The **N=3 canonical-phrase pin** for the default-branch resolver (per methodology-changelog v0.35.0 L677 — "Default-branch resolution canonical phrase pinned across N=3 surfaces") is INHERITED: BRANCH-2's new worktree-create invocation in build-slice SKILL.md uses the same `git symbolic-ref refs/remotes/origin/HEAD` literal as the existing N=3 surfaces, so the surface count remains N=3 (build-slice prereq + commit-slice 5b + commit-slice 5d, all using the same resolver). BRANCH-2 ADDS a SECOND N=3 surface pin for the NEW canonical phrase `WORKTREE=skip` literal across (1) build-slice SKILL.md Step 7c, (2) commit-slice SKILL.md `--merge` + `--sync-after-pr` reminder, (3) `tools/branch_workflow_audit.py` `_WORKTREE_SKIP_LINE_RE`. The cross-spec parity test `test_worktree_skip_grammar_pinned_across_three_surfaces` (per /critique B4 ACCEPTED-FIXED) pins this. (Per slice-066 /critique M4 ACCEPTED-FIXED.)
- The **canonical phrase `branch-per-slice workflow`** (per methodology-changelog v0.35.0 L679, N=3-surface pinned at N=8-stable) is INHERITED in historical sense; the CLAUDE.md rewrite at slice-066 changes the bullet TITLE to "Worktree-per-slice + branch" but preserves the BRANCH-1 lineage citation as historical anchor, so the phrase remains discoverable for archive Glob.
- The **prospective application clause** (per methodology-changelog v0.35.0 L685) is INHERITED: BRANCH-2 applies from slice-067 onward; slice-066 itself runs WITHOUT worktree mode at its own `/build-slice` (bootstrap-reference instance #1 — discharged via canonical `WORKTREE=skip-bootstrap` line). Every slice from slice-067 onward inherits a self-gating BRANCH-2 audit. (Per slice-066 /critique M4 ACCEPTED-FIXED.)
- The **v1 carveout** (per methodology-changelog v0.35.0 L681): the 3 sub-modes of BRANCH-1 fire only at `/build-slice` + `/commit-slice` + audit; the 4 upstream skills (`/slice`, `/design-slice`, `/critique`, `/critique-review`) have NO branch guard. BRANCH-2 INHERITS the v1 carveout — the worktree discipline fires at the same 3 surfaces; upstream skills run on whichever tree the user invokes them from (typically the main tree for `/slice` + `/design-slice`, then the user `cd`s into the worktree after `/build-slice` creates it). Pipeline-wide enforcement remains queued as the follow-on slice `add-pipeline-wide-branch-discipline-to-upstream-slice-skills`. (Per slice-066 /critique M4 ACCEPTED-FIXED.)
- The stale-slice-branch warning class (`_check_stale_slice_branches` at `tools/branch_workflow_audit.py:205`) is unchanged.
- The split-slice folder/branch numeric-only naming convention from [[ADR-046]] (slice-043 / R-6 retirement) is unchanged. The worktree path inherits the same numeric-only constraint.
- The **`BRANCH=skip — rationale: <text>` Events-line grammar** at `skills/build-slice/SKILL.md` Step 7c (pinned per ADR-019 + slice-021 /critique B1 ACCEPTED-PENDING) is INHERITED as a legacy parallel escape-hatch (per design.md "What's reused" + the new `tools/branch_workflow_audit.py` audit which preserves the existing `_BRANCH_SKIP_LINE_RE` regex unchanged). BRANCH-2 ADDS the `WORKTREE=skip` line shape with the same canonical grammar shape (HH:MM + rationale: required); both grammars coexist — `BRANCH=skip` for the rare legacy-single-tree-only escape, `WORKTREE=skip` for the worktree-discipline-skip case + the slice-066 bootstrap. The cross-spec parity test pinning the `WORKTREE=skip` literal across N=3 surfaces does NOT replace the implicit `BRANCH=skip` literal pin — both surfaces are pinned in parallel. (Per slice-066 /critique-review M-add-6 ACCEPTED-FIXED — closes the BRANCH-1 family's 4th sub-surface enumeration gap that survived first-Critic M4.)

**Not superseded — separate ADRs**:
- [[ADR-020]]'s three-mode `/commit-slice` design (`--merge` / `--push` / `--sync-after-pr` mutual exclusion + the per-mode flows) is unchanged. BRANCH-2 ADDS worktree-teardown to `--merge` + `--sync-after-pr`; the mode definitions, the mutual-exclusion contract, and the modes' pre-flight guardrails (WT-clean, stale-slice-branch, current-branch-is-slice-branch, origin-remote presence, upstream tracking) all carry forward verbatim.
- [[ADR-046]]'s split-slice folder-naming convention is unchanged.

## Consequences

**Downstream changes**:
- `tools/branch_workflow_audit.py` gains 3 worktree-aware helpers + 4 new violation kinds + 1 new escape-hatch regex.
- `skills/build-slice/SKILL.md` Branch state sub-section rewritten (replaces `git checkout -b` with `git worktree add` + `cd`).
- `skills/commit-slice/SKILL.md` Step 5b + Step 5d cleanup flows extended with idempotent worktree-remove guard.
- `methodology-changelog.md` v0.68.0 entry + RULE-ID `BRANCH-2`.
- `CLAUDE.md` "Branch-per-slice" bullet (at L32, verified 2026-05-24) rewritten to "Worktree-per-slice + branch" + BRANCH-2 citation; BRANCH-1 lineage preserved as historical anchor.
- `architecture/risk-register.md` R-17 retired (mitigating → retired).
- 5-part PMI-1 atomic bump VERSION 0.67.0 → 0.68.0 — canonical 5 parts per slice-063/064 anchor: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## v0.68.0` header in `methodology-changelog.md` + installed `~/.claude/ai-sdlc-VERSION` (corrected from rev-1 enumeration per slice-066 /build-slice Phase A Builder-self-catch); CLAUDE.md L32 edit + shippability row #66 = separate consumer-propagation surfaces (**BC-PROJ-9** 5-inventory fan-out + **BC-PROJ-10** paired entry-pins), NOT PMI-1 parts.
- New test modules `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py` + `tests/methodology/test_r17_retirement.py`; modifications to `test_build_slice_skill.py`, `test_commit_slice_skill.py`, `test_branch_workflow_audit.py`, `test_methodology_changelog.py`, `test_claude_md_pin.py`.

**Future flexibility opened**:
- Slice-067 (`add-parallel-slice-queue-output`) can compute parallel-safe candidate sets knowing two slices' worktrees physically cannot collide on disk; parallelism becomes a real capability, not an aspirational claim.
- Slice-068 (`add-slice-queue-claim-state-machine`) can introduce session-id-keyed claims knowing each session works in an isolated filesystem.
- Slice-069 (`add-rebase-and-conflict-discipline`) can rebase a worktree's branch against an advancing default without touching the main tree's checked-out state.

**Future flexibility constrained**:
- Single-tree-mental-model slices ("just `git checkout -b` and go") are no longer the default; documented escape via `WORKTREE=skip — rationale: <text>` covers the legitimate edge cases (the slice-066 bootstrap, hypothetical future single-tree-only adopter projects).
- Cross-platform worktree-path edge cases (WSL, Cygwin, network drives, UNC) are deferred; the canonical path convention assumes Windows + POSIX filesystem semantics. Per slice-066 /critique M5 ACCEPTED-FIXED, the parent-dir-not-writable case surfaces git's stderr verbatim plus an actionable hint (rather than silent corruption); the audit module's `_resolve_expected_worktree_path` helper is the single point of change for a future env-var override.

**Dogfood / bootstrap discipline**: slice-066 itself runs WITHOUT worktree mode at its own `/build-slice` (the SKILL.md prose authoring the worktree-create step does not yet exist at slice-066 start; cannot self-apply). Discharge: canonical `WORKTREE=skip-bootstrap — rationale: slice-066 authors the worktree-create prose; bootstrap-reference instance #1` line in `build-log.md` Events. The **idempotent worktree-remove guard** added at slice-066 /critique B5 ACCEPTED-FIXED additionally makes slice-066's own `/commit-slice --merge` safe — when the worktree doesn't exist (the bootstrap case), the guard logs "worktree absent — skip" and proceeds to branch-delete. Every slice from slice-067 onward inherits a self-gating BRANCH-2 audit AND uses the idempotent guard if it elects `WORKTREE=skip` for documented reasons.

## Reversibility

**cheap**: this ADR + the audit module's 4 new helpers + the 4 violation kinds + the SKILL.md edits are all isolated; revert is a single git revert of the slice-066 merge commit. The git-builtin `git worktree remove` ↔ `git branch -d` order constraint is a property of git itself, not of our codebase; reverting BRANCH-2 just re-establishes the BRANCH-1 single-tree workflow. No data migration. No external contract consumers (the audit's CLI exit-code contract is additive — existing callers see existing codes; new callers see new codes).

The reversibility-cheap tag also covers the worktree path convention choice: if `<main-parent>/<main-name>-wt/slice-NNN-<name>` proves unfriendly in practice (e.g., a user's parent dir is read-only), a follow-up ADR can re-home the convention via env-var override; the audit module's `_resolve_expected_worktree_path` helper is the single point of change.
