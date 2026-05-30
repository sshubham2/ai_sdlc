---
id: ADR-079
title: A read-only git-state detector surfaces stranded prior slice work (unmerged slice/* branches + slice/* worktrees) at /slice open and /pulse, advisory-not-blocking
date: 2026-05-30
slice: slice-087-add-stranded-slice-detection-to-slice
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-079: Stranded-slice detection at /slice open

## Context

The pipeline decides "what slice is active" purely from the **vault** — `slices/_index.md`'s Active table and `milestone.stage`. When a session builds a slice to completion but the session dies before `/commit-slice`, the vault marks the slice shipped/archived while git still holds an **unmerged `slice/NNN-*` branch + a live worktree**. That git-vs-vault divergence is invisible to every vault-based check.

This failed live this session: a prior session completed AND archived slice-086 but never committed/merged it. A fresh `/slice` redefined slice-086 from scratch, ran a full design→critique→critique-review cycle, and only collided with the stranded branch/worktree deep inside `/build-slice`'s BRANCH-2 setup (`fatal: a branch named 'slice/086-…' already exists` / `worktree … already exists`). The wasted cycle is the cost of having no git-aware open-time check. Registered as R-26.

`tools/branch_workflow_audit.py` already has a `stale-slice-branch` **warning** concept, but it only fires at `/build-slice` Step 6 (too late) and is scoped to conflict-recovery stragglers, not "a completed slice nobody committed."

## Options considered

1. **Hard Step-6 gate that refuses on any unmerged `slice/*` branch.** Pros: impossible to ignore. Cons: fires too late (after a wasted cycle), and a hard refuse breaks deliberate parallel-slice workflows (PSQ-1/PSQ-2 explicitly support multiple concurrent slices). Wrong altitude + wrong severity.
2. **Open-time advisory detector consulted by `/slice` (+ surfaced by `/pulse`).** Pros: catches the divergence at the earliest point (before redefining), structured-options halt lets the operator Resume / Continue-build / Proceed-anyway, never blocks a deliberate parallel slice. Cons: advisory can be dismissed — acceptable, since the goal is *surfacing*, not enforcement.
3. **Make `/slice` vault-check also scan git inline (no separate tool).** Pros: no new module. Cons: untestable in isolation, duplicates git logic into prose, and `/pulse` would need its own copy — exactly the divergence this project's audit-tool convention avoids.

## Decision

Adopt **Option 2**. Ship a read-only `tools/stranded_slice_audit.py` that **reuses** slice-077's `pulse_worktree_resolver.detect_active_worktrees` (+ `_resolve_default_branch`) for the worktree side rather than re-implementing porcelain/ancestry parsing (a third copy — B1), and ADDS the genuinely-new **bare unmerged `slice/*` branch without a worktree** case via `git for-each-ref refs/heads/slice/` + `git merge-base --is-ancestor`. Returns `status ∈ {clean, stranded}` with per-entry `{branch, worktree_path, ahead, dirty, indeterminate}` (a per-branch merge-base error is `indeterminate`, not a run failure).

### Relationship to R-22 (M3)

R-22 (retired by slice-077) covered `/pulse` mis-reporting the BRANCH-2 *worktree* window; `pulse_worktree_resolver` retired it by detecting/classifying `BUILT_BUT_NOT_MERGED` worktrees and surfacing them in `/pulse`. R-26 is the residual R-22 did NOT close: (i) **`/slice` never consults git state at open** (R-22 was `/pulse`-scoped), and (ii) the **bare unmerged `slice/*` branch WITHOUT a live worktree** — `pulse_worktree_resolver` walks `git worktree list` only, never `for-each-ref refs/heads/slice/`, so a committed-but-unmerged branch whose worktree was removed (e.g. a partial `--merge` cleanup) is invisible to it. R-26 is registered with this clause; it does not contradict or re-open R-22 (SUP-1 append-only). `/slice`'s Prerequisite check consults it BEFORE candidate-gathering and, on `stranded`, HALTs with an `AskUserQuestion` structured-options gate (Resume via `/commit-slice` / continue that build / proceed with a new slice anyway — proceed-anyway always offered). `/pulse` surfaces the same `status` at session start.

Shipped **MEPD-1 EXCLUDE** — no new RULE-ID, no methodology-changelog entry, no VERSION bump (consistent with the slice-086 adoption precedent and the project's "MEPD-1 EXCLUDE for risk-closing fix-slices" lesson, N≥4). The detector is an advisory open-time aid pinned by a behavioral test + structural-pin + OSDG-1 drift, not a versioned discipline.

Hard non-goals (must-not-defer): **no false positives** (`recovery/*` and merged `slice/*` branches and the main worktree must never be flagged), **advisory-never-blocking** (proceed-anyway always available), **fail-visible** (git/default-resolution failure → exit 2 surfaced, never a silent skip).

## Consequences

- New read-only tool (reusing `pulse_worktree_resolver`) + two SKILL.md edits (`slice`, `pulse`) + tests + R-26 (mitigating). Installed copies forward-synced (OSDG-1).
- **BC-PROJ-9 5-surface inventory fan-out (M1)** — a new `tools/*.py` propagates across all five, independent of any VERSION bump (this is what a "no version bump" MEPD-1-EXCLUDE slice still touches): (1) `plugin.yaml` tools block, (2) `tools/install_audit.py::_CANONICAL_TOOLS`, (3) `INSTALL.md` count literal "33 … tools"→34 at L22 + L166, (4) `tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS` (sound only because the tool gains a `--root` alias reaching stdout — M2), (5) `architecture/shippability.md` row.
- `/slice` gains a git dependency at open (already implicitly present via BRANCH-2). On a non-git project the detector exits 2 and `/slice` surfaces + continues.
- Future: a `--strict` blocking variant, or extending the scan to remote branches, are separate follow-on slices if warranted.

## Reversibility

**Cheap.** A read-only tool + additive prose in two skills + tests. Reverting is deleting the tool, the two prose blocks, and the tests, and removing the inventory entries — a sub-hour change with no data/schema/contract-consumer migration. The decision locks no expensive surface.
