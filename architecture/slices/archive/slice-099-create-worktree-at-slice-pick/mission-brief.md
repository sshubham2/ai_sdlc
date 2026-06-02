# Slice 099: create-worktree-at-slice-pick

**Mode**: Standard
**Estimated work**: 1 day (split-watch: AC2 pick-provenance may fast-follow as slice-100 if `/design-slice` finds the combined cut >1 day)
**Risk retired**: R-31 (stranded_slice_audit cannot see branchless in-progress slices) — attacked at the **root cause**: slices are branchless *because* `/slice` + `/design-slice` run on the default branch before any `slice/NNN-*` branch exists. Creating the worktree at pick-time eliminates the branchless-in-flight state in the normal flow, moving R-31 from `mitigating` toward retirement. Also closes the **pre-build residual of R-17** (clean-tree contamination): BRANCH-2/ADR-063 isolates `/build-slice` in a worktree, but `/slice` + `/design-slice` still mutate the shared default branch — landing mission-brief.md, design.md, and new ADRs on master. Live evidence: slice-098's scaffold + ADR-089 landed uncommitted on master under the current build-time-worktree timing (2026-06-01).
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

BRANCH-2 (slice-066 / ADR-063) made `/build-slice` run in a filesystem-isolated worktree, but the worktree is not created until `/build-slice` — so every prior step (`/slice` writing the mission brief + milestone, `/design-slice` writing design.md + new ADRs, `/critique` writing critique.md) mutates the shared default branch (master). This is the recurring "master never stays clean" failure: scaffold and design artifacts accumulate as uncommitted/untracked files on master, and the slice exists as a *branchless* in-flight folder that `stranded_slice_audit` can only see weakly (R-31). This slice moves worktree+branch creation **forward to the moment a candidate is settled in `/slice`**, and writes every downstream artifact into that worktree — so the default branch is never touched by slice authoring. It also records pick provenance (when + by whom a candidate was picked) in `slice-queue.md`, closing the audit gap on who started a slice and when.

## Acceptance criteria

1. **Worktree-at-pick** — when `/slice` settles on a candidate (explicit `/slice "<intent>"`, picked from the ranked list, or "you pick"/autonomous), it creates the BRANCH-2 worktree + `slice/NNN-<name>` branch at the canonical sibling path `<main-parent>/<main-name>-wt/slice-NNN-<name>` **before** writing `mission-brief.md` + `milestone.md`, and writes those artifacts (and all downstream `/design-slice`/`/critique` artifacts) **into the worktree**. After `/slice` completes, the default branch's working tree is clean — the scaffold exists only in the worktree.
2. **Pick-provenance in slice-queue.md** — `/slice` records, for the picked candidate, the pick timestamp (ISO-8601 UTC) and picker git identity (`user.name` + `user.email`) into `slice-queue.md`. Fail-visible if git identity is unset (no silent skip — reuses PSQ-2's `read_git_config_user` raise-on-unset contract).
3. **`/build-slice` worktree-create is idempotent** — `/build-slice`'s existing BRANCH-2 worktree creation detects a `/slice`-created worktree and does NOT double-create or error; when no worktree exists (legacy slice, or `WORKTREE=skip`), it falls back to today's create-at-build behavior. No double-creation, no collision.
4. **Audit + ADR alignment** — `tools/branch_workflow_audit.py` accepts the new pick-time worktree timing without emitting false violations, and a new ADR partial-supersedes ADR-063 recording the build→pick shift (append-only per SUP-1). The `WORKTREE=skip` escape-hatch remains honored. CLAUDE.md's BRANCH-2 prose is updated to reflect pick-time creation.
5. **No-regression + no-duplication** — the full methodology suite stays green (BRANCH-2, PSQ-1/PSQ-2, stranded-audit, drift tests for `slice`/`build-slice` SKILL.md), and the canonical worktree-path computation **on the primary (non-legacy) create path** is a single shared source used by both `/slice` and `/build-slice` (the legacy `WORKTREE=skip`/dirty-default escape-hatch prose may retain its inline convention for self-containment — per /critique m2).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Worktree-at-pick | A test (or scripted simulation) settles a candidate via `/slice`, then asserts: (a) `git worktree list` shows the new `slice/NNN-*` worktree; (b) `mission-brief.md` + `milestone.md` exist under the worktree path, NOT under the default tree; (c) `git -C <default> status --porcelain` is empty. |
| 2 | Pick-provenance | A test asserts the picked candidate's `slice-queue.md` entry carries a pick timestamp (ISO-8601 UTC) + picker identity; a second test with `git config user.name` unset asserts a *visible* failure (non-zero / explicit STOP), never a silent skip. |
| 3 | build-slice idempotency | Run `/build-slice` logic against a slice-099-shaped pre-created worktree → succeeds, does not re-create / error. Run against a no-worktree slice → falls back to create. Both pinned by `tools/branch_workflow_audit.py` expectations + a test. |
| 4 | Audit + ADR | `$PY -m tools.branch_workflow_audit` passes on a pick-time-worktree slice; new ADR file exists with `supersedes: ADR-063`; `grep` CLAUDE.md shows BRANCH-2 prose names pick-time creation. |
| 5 | No-regression + no-duplication | `$PY -m pytest tests/methodology -q` green; `slice`/`build-slice` SKILL.md drift tests green; a source check shows the worktree-path/branch-name convention is referenced from one shared helper, not duplicated across the two skills' prose-driven invocations. |

## Must-not-defer

- [ ] **Fail-visible pick-provenance** — git identity unset → surface the failure, never silently skip the provenance write (R-7 silent-disable class; reuse PSQ-2 `read_git_config_user`).
- [ ] **`WORKTREE=skip` escape-hatch preserved** — bootstrap / exceptional slices (incl. this slice's own bootstrap, see below) must still be able to opt out via the canonical `WORKTREE=skip — rationale: <text>` DEVIATION line; `/slice` must honor it too, not just `/build-slice`.
- [ ] **Abandoned-pick handling (downscoped per /critique M1)** — a picked-but-never-built slice shows as `IN_PROGRESS:slice` **informational** (`halt: false`) in `stranded_slice_audit` — it is *listed*, not surfaced as an anomaly. This slice adds NO new detection class; a real abandoned-pick discriminator is DEFERRED to a follow-up `abandoned-pick-detection` candidate (BRANCH-3 raises the abandon rate — worktree created before build-commitment — so the follow-up is warranted). Do not claim detectability the code does not deliver.
- [ ] **Single source of truth for the worktree path** — `/slice` and `/build-slice` MUST compute the canonical `<main-parent>/<main-name>-wt/slice-NNN-<name>` path + `slice/NNN-<name>` branch from one shared helper; no duplicated convention.
- [ ] **Encoding discipline** — any new/moved git subprocess passes `encoding="utf-8"` (BC-GLOBAL-5 / cp1252 class); no new bare `print()` at import (RSAD-1).
- [ ] **ADR for the BRANCH-2 timing change** — append-only supersession of ADR-063 (never edit in place; SUP-1).

## Out of scope

- The external-vault flip (slice-098 routes the 3 git-coupled tools; the physical move is a later slice).
- Changing the canonical worktree path convention or branch-naming scheme — they stay exactly as BRANCH-2 defines (`<main-parent>/<main-name>-wt/slice-NNN-<name>` + `slice/NNN-<name>`).
- Redefining PSQ-2's claim model — pick-provenance may *reuse or extend* the existing `Claimed-by`/`Claimed-at` field machinery, but the cooperative git-identity ownership model (ADR-067) is not re-litigated here.
- Full automatic garbage-collection of abandoned-pick worktrees beyond detectability/classification (a separate slice if the abandon rate warrants it).
- Moving `/commit-slice`'s worktree teardown (already correct under BRANCH-2 — teardown stays at merge time).

## Dependencies

- Prior slices: [[slice-066-add-worktree-per-slice-discipline]] (BRANCH-2 / [[decisions/ADR-063]] — the worktree-at-build discipline this refines), [[slice-067-add-parallel-slice-queue-output]] (PSQ-1 — `slice-queue.md` writer), [[slice-072-add-psq-2-claim-machinery]] ([[decisions/ADR-067]] — `Claimed-by`/`Claimed-at` field machinery + `read_git_config_user`), [[slice-087-add-stranded-slice-detection-to-slice]] / [[slice-092-fix-stranded-audit-branchless-blindspot]] (the branchless-in-flight class this eliminates at the source).
- Vault refs: [[decisions/ADR-063]] (BRANCH-2 — partial-superseded by this slice's new ADR), [[decisions/ADR-064]] (PSQ-1), [[decisions/ADR-067]] (PSQ-2 identity model).
- Risk register: [[risk-register#R-31]] (root-cause retirement), [[risk-register#R-17]] (pre-build residual), [[risk-register#R-27]] (uncommitted-work-invisible-at-/slice-open).
- Parallel-slice note: NON-OVERLAPPING with active [[slice-098-route-or-retire-git-coupled-vault-tools]] — disjoint file sets (098 = the 3 git-coupled tools + `_vault_paths.py`; 099 = `skills/slice` + `skills/build-slice` SKILL.md + `branch_workflow_audit.py` + `slice_queue_writer.py`/`slice_queue_claim.py`). Only semantic interaction: 099 reduces how often `stranded_slice_audit`'s branchless-in-flight class fires; 098 only *routes* that tool's vault paths. No merge conflict; merge in any order.

## Bootstrap exemption (self-application)

Like slice-067 (PSQ-1 helper could not exist at its own `/slice` time) and slice-098, this slice cannot self-apply its own deliverable: the worktree-at-pick behavior does not exist when slice-099 itself is picked. Therefore:
- slice-099's worktree (`<...>-wt/slice-099-create-worktree-at-slice-pick` on `slice/099-create-worktree-at-slice-pick`) was created **manually** at pick-time in this conversation (2026-06-01) — the bootstrap instance demonstrating the target behavior.
- slice-099's own pick-provenance (AC2) is recorded in this brief + milestone.md rather than via the not-yet-built `slice-queue.md` stamping. The PSQ-1 Step 6.5 queue regeneration is bootstrap-skipped for this pick (non-fatal per ADR-064; consistent with the slice-067 PSQ-1 bootstrap precedent).
- **Pick provenance (manual bootstrap record)**: picked 2026-06-01 by Shubhendu Shubham &lt;contact@sshubham.me&gt;, source = user-stated intent ("once slice is picked, create a worktree + record pick time/owner in slice-queue.md").

## Mid-slice smoke gate

At ~50% of build (after `/slice` worktree-creation + provenance wiring, before `/build-slice` idempotency + audit alignment):
```
$PY -m tools.branch_workflow_audit                       # no false violations on pick-time timing
$PY -m pytest tests/methodology -k "branch or worktree or slice_queue or stranded" -q
# Manual: simulate a candidate pick → assert default-branch `git status` clean + scaffold only in worktree
```
Expected: targeted tests green; a simulated pick leaves the default branch clean with the scaffold in the worktree only. If a pick mutates the default branch: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `slice`/`build-slice` SKILL.md drift tests green (OSDG-1 / mini-CAD); installed copies re-synced
- [ ] New ADR-090 present (partial-supersedes ADR-063); CLAUDE.md BRANCH-2 prose updated to pick-time
- [ ] **Methodology version-bump fan-out (per /critique B3)** — BRANCH-3 changelog entry @ v0.81.0 + `test_v_0_81_0_branch_3_entry_present...` entry-pin + atomic 4-part PMI-1 bump (`VERSION`/`~/.claude/ai-sdlc-VERSION`/`plugin.yaml`/installed changelog) + MCFS-1 + both version forward-sync audits green
