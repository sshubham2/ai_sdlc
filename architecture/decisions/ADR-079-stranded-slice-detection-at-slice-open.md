---
id: ADR-079
title: A read-only git-vs-vault classifier surfaces stranded prior slice work across a 4-class divergence model at /slice open and /pulse, halting only on genuine divergence (parallel-safe), advisory-not-blocking
date: 2026-05-30
revised: 2026-05-31
slice: slice-087-add-stranded-slice-detection-to-slice
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-079: Stranded-slice detection at /slice open

> **Revised 2026-05-31 (pre-ship, in-slice draft).** The originally-accepted decision was an existence-based detector that flagged *every* unmerged `slice/*` branch. During TRI-1 reconciliation the USER caught that this cry-wolfs on every healthy in-flight parallel slice (PSQ-1/PSQ-2/BRANCH-2 make concurrent unmerged `slice/*` the normal state). This ADR is revised in place (the slice has not shipped/merged, so the decision is still a draft, not an append-only post-ship record) to the **classify-don't-flag-all** model below; the flag-all approach is now **rejected Option 4**.

## Context

The pipeline decides "what slice is active" purely from the **vault** — `slices/_index.md`'s Active table and `milestone.stage`. When a session builds a slice to completion but the session dies before `/commit-slice`, the vault marks the slice shipped/archived while git still holds an **unmerged `slice/NNN-*` branch + a live worktree**. That git-vs-vault divergence is invisible to every vault-based check.

This failed live this session: a prior session completed AND archived slice-086 but never committed/merged it. A fresh `/slice` redefined slice-086 from scratch, ran a full design→critique→critique-review cycle, and only collided with the stranded branch/worktree deep inside `/build-slice`'s BRANCH-2 setup (`fatal: a branch named 'slice/086-…' already exists` / `worktree … already exists`). The wasted cycle is the cost of having no git-aware open-time check. Registered as R-27.

`tools/branch_workflow_audit.py` already has a `stale-slice-branch` **warning** concept, but it only fires at `/build-slice` Step 6 (too late) and is scoped to conflict-recovery stragglers, not "a completed slice nobody committed."

## Options considered

1. **Hard Step-6 gate that refuses on any unmerged `slice/*` branch.** Pros: impossible to ignore. Cons: fires too late (after a wasted cycle), and a hard refuse breaks deliberate parallel-slice workflows (PSQ-1/PSQ-2 explicitly support multiple concurrent slices). Wrong altitude + wrong severity.
2. **Open-time advisory detector consulted by `/slice` (+ surfaced by `/pulse`), that CLASSIFIES each unmerged `slice/*` branch into a divergence model and halts only on genuine divergence.** Pros: catches divergence at the earliest point (before redefining); structured-options halt lets the operator Resume / Continue-build / Proceed-anyway; **never halts on a healthy in-flight parallel slice** because it distinguishes "vault-says-done-but-git-unmerged" (stranded) from "vault-says-in-flight" (normal parallel work). Cons: needs to cross-reference vault state + PSQ-2 claims, not just git — bigger than a pure-git detector, mitigated by reusing slice-077's `classify_worktree_state` + slice-072's `parse_queue_text`.
3. **Make `/slice` vault-check also scan git inline (no separate tool).** Pros: no new module. Cons: untestable in isolation, duplicates git logic into prose, and `/pulse` would need its own copy — exactly the divergence this project's audit-tool convention avoids.
4. **(REJECTED — the originally-accepted approach) Existence-based detector that flags EVERY unmerged `slice/*` branch as stranded.** Pros: trivial to implement (pure git, no vault/claim cross-reference). Cons — **fatal**: under PSQ-1/PSQ-2/BRANCH-2, multiple concurrent unmerged `slice/*` branches is the NORMAL state, so this flags every in-flight parallel slice at every `/slice` open → cry-wolf → the operator silent-disables the gate (R-7 class), AND it actively contradicts the project's parallel-slice strategic direction. The USER caught this at TRI-1; it is the miss that motivated the `agents/critique.md` Dim-7 strategic-direction-fit + architectural-concurrency probe (`64f6ea3`). Option 2's classification model exists precisely to avoid this.

## Decision

Adopt **Option 2 — classify, don't flag-all.** Ship a read-only `tools/stranded_slice_audit.py` that classifies each unmerged `slice/*` branch into one of four divergence classes (+ INDETERMINATE for fail-closed unknowns) and halts `/slice` only on the two genuine-divergence classes:

| # | Class | Condition (first match wins) | `/slice` | `halt` |
|---|-------|------------------------------|----------|--------|
| 1 | **CLAIMED-BY-OTHER** | PSQ-2 `Claimed-by` git identity ≠ mine | informational | no |
| 2 | **IN-PROGRESS** | live worktree `classify_worktree_state`=`IN_PROGRESS` (stage ∈ slice…validate), or active milestone non-terminal | informational | no |
| 3 | **STRANDED-COMPLETE** | git-unmerged AND vault says DONE (`BUILT_BUT_NOT_MERGED` worktree, or `archive/slice-NNN-*` present, or milestone terminal/next-action=commit) | **HALT** | yes |
| 4 | **ORPHANED** | git-unmerged AND no vault story anywhere | **HALT** | yes |
| 5 | **INDETERMINATE** | classification could not complete (`UNKNOWN`/`merge-base-error`/malformed milestone) | **HALT** (surfaced w/ sub-reason) | yes (fail-closed) |

Precedence is load-bearing — CLAIMED-BY-OTHER outranks STRANDED-COMPLETE so another session's committed-but-unmerged work never halts *my* `/slice` (cross-session cry-wolf); IN-PROGRESS outranks STRANDED-COMPLETE so a pre-reflect parallel slice (ancestry-irrelevant per ADR-070) is never flagged. For the **solo-dev case this repo is**, CLAIMED-BY-OTHER never fires (one identity), so vault-done-but-unmerged branches correctly surface as STRANDED-COMPLETE.

**CLAIMED-BY-OTHER resolution + scope (B1, re-`/critique` — executed against the live queue).** The branch→queue mapping is `slice/NNN-<name>` → key `<name>`. `slice-queue.md` keys by `### <candidate-name>` and PSQ-1 regenerates it from the backlog top-10, so an in-flight slice's candidate is frequently **absent** from the queue (verified: `add-project-frame-synthesizer` is not a key; no present entry carries `Claimed-by`). Key-absent OR present-but-unclaimed ⇒ the class does not fire ⇒ **correct fall-through** to IN-PROGRESS/STRANDED-COMPLETE/ORPHANED (NOT a silent miss). The class fires only on a genuine foreign claim for `<name>` — the multi-session race it provisions for; in solo-dev + the current PSQ-1 lifecycle it is **largely inert**, and the load-bearing parallel-safety class is IN-PROGRESS, not CLAIMED-BY-OTHER. (Declinable TRI-1 alternative: demote CLAIMED-BY-OTHER to a deferred follow-on and ship a 3-active-class model.)

The tool **reuses** slice-077's `pulse_worktree_resolver.detect_active_worktrees` + **`classify_worktree_state`** (+ `_resolve_default_branch`) for any branch with a live worktree (mapping `IN_PROGRESS`→IN-PROGRESS, `BUILT_BUT_NOT_MERGED`→STRANDED-COMPLETE, `MERGED`→skip, `UNKNOWN`→INDETERMINATE) rather than re-implementing porcelain/ancestry parsing (B1), and slice-072's `slice_queue_claim.parse_queue_text` for the claim cross-reference. The genuinely-new code is the **bare unmerged `slice/*` branch without a worktree** case (via `git for-each-ref refs/heads/slice/` + `git merge-base --is-ancestor`, classified by reading **the branch's own tree** via `git ls-tree`/`git show <branch>:…` — M1, because the stranded archive/milestone state of a committed-but-unmerged slice lives on that branch, not the invoking tree) + the claim comparison + the `/slice`-open consult. Returns `status ∈ {clean, divergent}` (divergent ⟺ ≥1 `halt: true` entry; IN-PROGRESS/CLAIMED-BY-OTHER entries are listed but do not make the run divergent) with per-entry `{branch, worktree_path|null, klass, halt, vault_state, claimed_by|null, ahead, dirty, reason}` (a per-branch merge-base error is `INDETERMINATE`, not a run failure).

### Relationship to R-22 (M3)

R-22 (retired by slice-077) covered `/pulse` mis-reporting the BRANCH-2 *worktree* window; `pulse_worktree_resolver` retired it by detecting/classifying `BUILT_BUT_NOT_MERGED` worktrees and surfacing them in `/pulse`. R-27 is the residual R-22 did NOT close: (i) **`/slice` never consults git state at open** (R-22 was `/pulse`-scoped), and (ii) the **bare unmerged `slice/*` branch WITHOUT a live worktree** — `pulse_worktree_resolver` walks `git worktree list` only, never `for-each-ref refs/heads/slice/`, so a committed-but-unmerged branch whose worktree was removed (e.g. a partial `--merge` cleanup) is invisible to it. R-27 is registered with this clause; it does not contradict or re-open R-22 (SUP-1 append-only). `/slice`'s Prerequisite check consults it BEFORE candidate-gathering and, on `status: divergent` (≥1 STRANDED-COMPLETE / ORPHANED / INDETERMINATE entry), HALTs with an `AskUserQuestion` structured-options gate (Resume via `/commit-slice` / continue that build / proceed with a new slice anyway — proceed-anyway always offered); on `status: clean` with informational IN-PROGRESS / CLAIMED-BY-OTHER entries it surfaces a one-line note and proceeds without a gate (the parallel-safe path). `/pulse` surfaces the same `status` + per-entry `klass` at session start.

Shipped **MEPD-1 EXCLUDE** — no new RULE-ID, no methodology-changelog entry, no VERSION bump (consistent with the slice-086 adoption precedent and the project's "MEPD-1 EXCLUDE for risk-closing fix-slices" lesson, N≥4). The detector is an advisory open-time aid pinned by a behavioral test + structural-pin + OSDG-1 drift, not a versioned discipline.

Hard non-goals (must-not-defer): **no false positives** (`recovery/*` and merged `slice/*` branches and the main worktree must never be flagged), **advisory-never-blocking** (proceed-anyway always available), **fail-visible** (git/default-resolution failure → exit 2 surfaced, never a silent skip).

## Consequences

- New read-only tool (reusing `pulse_worktree_resolver`) + two SKILL.md edits (`slice`, `pulse`) + tests + R-27 (mitigating). Installed copies forward-synced (OSDG-1).
- **BC-PROJ-9 5-surface inventory fan-out (M1)** — a new `tools/*.py` propagates across all five, independent of any VERSION bump (this is what a "no version bump" MEPD-1-EXCLUDE slice still touches): (1) `plugin.yaml` tools block, (2) `tools/install_audit.py::_CANONICAL_TOOLS`, (3) `INSTALL.md` count literal "33 … tools"→34 at L22 + L166, (4) `tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS` (sound only because the tool gains a `--root` alias reaching stdout — M2), (5) `architecture/shippability.md` row.
- `/slice` gains a git dependency at open (already implicitly present via BRANCH-2). On a non-git project the detector exits 2 and `/slice` surfaces + continues.
- Future: a `--strict` blocking variant, or extending the scan to remote branches, are separate follow-on slices if warranted.

## Reversibility

**Cheap.** A read-only tool + additive prose in two skills + tests. Reverting is deleting the tool, the two prose blocks, and the tests, and removing the inventory entries — a sub-hour change with no data/schema/contract-consumer migration. The decision locks no expensive surface.
