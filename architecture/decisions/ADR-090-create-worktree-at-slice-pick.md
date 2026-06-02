---
id: ADR-090
title: Create the slice worktree at /slice pick-time; slice-queue.md stays a shared main-tree coordination ledger with an append-only Pick log
date: 2026-06-01
slice: slice-099-create-worktree-at-slice-pick
reversibility: cheap
status: accepted
supersedes: ADR-063
---

# ADR-090: Create the slice worktree at `/slice` pick-time (partial-supersede of BRANCH-2 build-time timing)

## Context

BRANCH-2 ([[ADR-063]], slice-066) made `/build-slice` run in a filesystem-isolated worktree on a dedicated `slice/NNN-<name>` branch, retiring R-17 (uncommitted slice-A WIP contaminating slice-B). But BRANCH-2 creates the worktree **at `/build-slice`** — so every step before build (`/slice` writing mission-brief + milestone, `/design-slice` writing design.md + new ADRs, `/critique` writing critique.md) executes on the **shared default branch (master)**. The result, hit repeatedly and witnessed on 2026-06-01 with slice-098 (its `mission-brief.md`/`design.md`/`milestone.md` + ADR-089 landed uncommitted on master): the default branch never stays clean, and the slice exists as a *branchless* in-flight folder that `stranded_slice_audit` can only weakly see (R-31). BRANCH-2's band-aid is a "dirty-default scaffolding dance" in `/build-slice` (`git switch -c` → commit scaffold → `git switch` back → `git worktree add`), which only moves the contamination, after the fact.

A second decision is forced by moving the worktree earlier: **where does `slice-queue.md` live?** Its entire purpose (PSQ-1/PSQ-2, [[ADR-064]]/[[ADR-067]]) is *cross-session* coordination — a second Claude session reads it to pick a parallel-safe candidate and to see in-flight claims. If it moves into the worktree like the other artifacts, that visibility dies until `/commit-slice` merges.

## Options considered

1. **Keep BRANCH-2 timing (worktree at build); strengthen the dirty-default dance** — pros: no change; cons: master stays dirty through slice/design/critique; R-31 branchless state persists; the dance is fragile (N=5 cumulative slice fixes 070–074).
2. **Worktree at pick; move `slice-queue.md` into the worktree too** — pros: maximal master-cleanliness (zero master writes at pick); cons: PSQ-2 cross-session coordination breaks until merge — two sessions can pick the same candidate; fights the parallel-slice family's reason for existing.
3. **Worktree at pick; `slice-queue.md` stays a shared main-tree ledger with an append-only `## Pick log`** (CHOSEN) — pros: slice *work* (scaffold/design/ADRs) never touches master; the queue stays visible to parallel sessions; pick provenance (who/when) is durably recorded and survives queue regeneration; cons: a narrow, intentional queue-only commit lands on master per pick, and concurrent same-machine picks rely on serialization (`_vault_write`'s sidecar lock for the queue write + git's index lock for the commit), fail-visible and retried — **NOT** PCR (see §Consequences; PCR resolves `git rebase`-stage conflicts at `/commit-slice`, a different mechanism the pick-time path never enters).

## Decision

Adopt **Option 3 (BRANCH-3)**. `/slice`, on settling a candidate (explicit intent / picked / "you pick"), creates the BRANCH-2 worktree + `slice/NNN-<name>` branch at the canonical sibling path **before** writing any slice artifact, and writes `mission-brief.md` + `milestone.md` (and all downstream `/design-slice`/`/critique` artifacts) **into the worktree**. The canonical worktree-path + branch-name computation is extracted to a single shared helper `tools/_worktree_paths.py` used by `/slice`, `/build-slice`, and `branch_workflow_audit.py`.

`slice-queue.md` is the **one** cross-session coordination artifact that remains on the default branch. At pick, `/slice` (running in the main tree on the default branch) regenerates the queue's `## Candidates` and **appends** a `## Pick log` line — `- slice-NNN-<name> — picked <ISO-8601 UTC> by <git user.name> <user.email>` — then commits **only** `slice-queue.md` on the default branch. The `## Pick log` is append-only and preserved verbatim across regenerations via a **read-tail / re-append path distinct from PSQ-2 claim-preservation** (claim-preservation keys on `### entry` headers, which a top-level `## Pick log` section lacks; `write_slice_queue` reads the literal pick-log tail before regenerating `## Candidates` and re-appends it). `record_pick` is idempotent by `- slice-NNN-<name> —` prefix-scan. Picker identity reuses `slice_queue_claim.read_git_config_user` and is **fail-visible** when git identity is unset.

`/build-slice`'s worktree handling becomes idempotent: "worktree already exists → cd + verify" is the primary path; it creates a worktree only when none exists (legacy slice / `WORKTREE=skip`). The build-time `WORKTREE=skip` escape-hatch (build-log.md) is unchanged; a pick-time `WORKTREE=skip` fallback (scaffold on main tree as pre-BRANCH-3 + recorded rationale) covers bootstrap slices that cannot use their own deliverable.

## Consequences

- The default branch stays clean of slice *work* from pick onward; R-31's branchless-in-flight state no longer occurs in the normal flow (every picked slice has a branch immediately), and R-17's pre-build residual is closed.
- `branch_workflow_audit.py` needs no violation-logic change — its end-state (registered worktree at canonical path on the matching branch) is timing-agnostic; only its path helpers move to `_worktree_paths.py` and its docstrings name BRANCH-3.
- The dirty-default scaffolding dance in `/build-slice` becomes legacy-only (fires for `WORKTREE=skip`/legacy slices, never for a BRANCH-3 pick).
- A queue-only commit lands on the default branch per pick, in the single main tree. Concurrent **same-machine** picks (the PSQ-2 model) are serialized by `_vault_write`'s sidecar lock (queue write) + git's index lock (commit), fail-visible on contention; `record_pick` prefix-scan idempotency makes a retry a no-op. **PCR is NOT involved** — it resolves `git rebase`-stage conflicts at `/commit-slice`, not pick-time commits. Cross-clone / multi-machine queue coordination is OUT OF SCOPE (ADR-067 bounds PSQ-2 to same-machine cooperation).
- New rule **BRANCH-3** in `methodology-changelog.md` (partial-supersedes ADR-063 timing; PSQ cross-reference for the `## Pick log`). CLAUDE.md BRANCH-2 prose updated.

## Reversibility

**Cheap.** The change is a skill-prose timing reorder (move worktree-create from `/build-slice` to `/slice`) plus an additive, append-only `## Pick log` section and a small shared path helper. Reverting = move the worktree-create step back to `/build-slice` and stop appending the pick-log; no data migration, no irreversible state. Append-only pick-log history is forward-compatible and harmless if the feature is rolled back.
