---
id: ADR-107
title: Flip the vault to an external shared store (whole vault external, plain directory)
date: 2026-06-05
slice: slice-115-flip-vault-to-external-store
reversibility: cheap
status: accepted
supersedes: null
partial-supersedes: ADR-090
---

# ADR-107: Flip the vault to an external shared store (whole vault external, plain directory)

## Context

The external-shared-vault initiative (slices 093→114) built every piece of flip-readiness so that the **physical move** would be the sole residual to retire **R-32** (concurrent-write lost-update / atomic-rename-EPERM corruption on a shared mutable vault). All three write-safety sub-classes (094/095/097), the 3 git-coupled tools (098), the post-flip queue CAS (109), the location-agnostic suite (110), production reads (106), the op-gate (111), and the entire `<vault>/` prose seam (112–114) are closed. This ADR records the flip's two binding decisions, settled with the user at `/design-slice`.

Two coupled questions remained (the R-32.a / R-32.b sub-entries):
- **R-32.a** — where do per-slice ACTIVE slice folders live after the move?
- **R-32.b** — how does the archive `move` stay coherent across stores?

Plus a third: should the external store keep its own version history?

## Options considered

1. **Option A — whole vault external** (chosen). All of `architecture/` (shared-aggregates + per-slice active folders + archive) → `~/.aisdlc/<project>/`; `git rm -r --cached architecture/` + gitignore. Single resolution domain; `vault_edit move` stays single-store so **R-32.b dissolves**. Cons: vault artifacts (mission-brief/design/critique/reflection) leave the repo's git history — a partial-supersede of BRANCH-3's vault-artifact-in-worktree tracking.
2. **Option B — hybrid** (rejected). Only the contended shared-aggregates go external; per-slice folders stay worktree-local/tracked/merged. Pros: preserves the self-hosting audit trail (vault artifacts in the merge diff). Cons: a selective `.gitignore` + a dual-root `vault_edit` (active/archive worktree-local vs shared-aggregate external); the archive `move` becomes cross-store.
3. **Plain external directory** (chosen for the history question) vs. **git-init the external store** (rejected). Plain dir: simplest; writes mediated only by the R-32 CAS/lock channel. git-init: recovers an independent vault history but adds a second git surface to maintain.

## Decision

Adopt **Option A (whole vault external)** with a **plain external directory** (no independent git history). The entire `architecture/` directory relocates to `~/.aisdlc/<project>/` (base `~/.aisdlc` per ADR-085 §Install enhancement; `<project>` = bounded hash of the canonicalized git-common-dir, MAX_PATH-safe), is removed from git tracking (`git rm -r --cached architecture/`), and is gitignored. `VAULT_ROOT` resolves to the external store via ADR-085 tier-2 config (`$GIT_COMMON_DIR/aisdlc/vault-root`); `vault_is_external()` returns `True`.

Rationale for A over B: the initiative's stated intent across the whole arc (ADR-085 "relocate the vault `architecture/`"; ADR-103's single-`VAULT_ROOT` archive move) is the *whole* vault external; A is mechanically simplest, dissolves R-32.b, and most fully delivers "one live vault view" (active slices are visible cross-worktree too). The audit-trail cost is acceptable for a solo-dev local-merge workflow and is mitigated structurally — the move is byte-faithful and reversible.

## Consequences

- **BRANCH-3 partial-supersede**: vault artifacts no longer land in the worktree's git / the slice branch / the merge diff. The worktree stays the unit of **code** isolation (tools/skills/agents/tests); vault writes follow `VAULT_ROOT` to the external store. BRANCH-3's worktree-per-slice + branch-per-slice for *code* is unchanged.
- **R-32.b dissolves**: `vault_edit move` resolves both archive endpoints under the single external `VAULT_ROOT`; archival is an in-store move. No cross-store machinery.
- **`/slice` Step 6.5 change**: "commit slice-queue.md on master" retires (the queue is external/untracked); the CAS-mediated queue write + pick-log (slice-109) stay.
- **`/commit-slice` vault-conflict RETIRE** (consumes ADR-089): PCR's SOFT/VAULT_CLAIM vault-file regeneration becomes a `vault_is_external`-guarded no-op (vault files are untracked → never rebase U-files). PSQ-3 rebase + HARD *code*-file resolution stay live.
- **Class 4–6 carve-out prose** converts to `<vault>/`; the `vault_flip_prose_inventory` ratchet re-pins; `OP_DEFERRED_TO_FLIP` → ∅. Class 7 (diagnose-out) stays concrete (out of scope; no seam).
- **Self-referential bootstrap**: slice-115 is the first slice to live through the flip — its own active folder migrates to the external store mid-build (design.md §The flip sequence).
- **R-32 retires** at the move.

## Reversibility

**Cheap.** `tools/_vault_flip.py --rollback` is the scripted inverse: move `<external>/*` back to `architecture/`, unset the `aisdlc/vault-root` config, reverse the `git rm --cached` (re-track) + remove the `.gitignore` entry; the prose/guard changes revert via `git revert`. No data is lost (the migration is a verified byte-faithful copy; the in-tree copy is removed only after the verify passes). Tagged `cheap` consistent with the R-32 register entry, with the caveat that the surface is wide — the rollback tool is what keeps it genuinely cheap rather than a manual 1091-file scramble.
