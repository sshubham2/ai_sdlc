---
id: ADR-081
title: The /commit-slice stale-slice-branch guardrail uses worktree-backing as the stale-vs-active-parallel discriminator
date: 2026-05-31
slice: slice-089-make-commit-slice-stale-branch-check-parallel-slice-aware
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-081: Stale-slice-branch guardrail uses worktree-backing as the discriminator

## Context

`/commit-slice`'s stale-slice-branch pre-flight guardrail (in `--merge` Step 5b sub-step 1 and `--push` Step 5c pre-flight #2) refuses if **any** non-current `slice/*` branch exists (`git for-each-ref refs/heads/slice/`). The check was minted (per `/critique` B5, slice-021/022 era) to catch orphan branches left by a failed conflict-recovery — a single-slice-era assumption that "another slice branch = stale artifact."

Under the parallel-slice family (PSQ-1 / PSQ-2 / BRANCH-2, slices 064–083) multiple concurrent unmerged `slice/*` branches — each in its own worktree — is the *normal* operating state. The guardrail therefore false-positives: it STOPed the legitimate slice-088 merge because slice-087 was an active parallel slice (2026-05-31; resolved only by user-authorized manual override). Worse, because it is a *pre-flight* gate it STOPs **before** PSQ-3's rebase (sub-step 2.5) — so the rebase-and-conflict-resolve machinery the parallel-slice family was built around is unreachable whenever a peer slice is in flight.

We need a discriminator that separates a legitimate concurrent slice from a genuine stale artifact, without weakening the original protection.

## Options considered

1. **Worktree-backing discriminator** — a `slice/*` branch with a live registered worktree is an active parallel slice (allow); a worktree-less `slice/*` branch is a genuine orphan/straggler (refuse). Reuses `pulse_worktree_resolver.detect_active_worktrees`.
   - Pros: directly models the BRANCH-2 reality (every active slice has a worktree); fully deterministic from `git worktree list`; reuses shipped, tested code; conservative on the dangerous side (stranded-complete branches are worktree-less → still refused); no default-branch resolution needed.
   - Cons: a developer who manually `git worktree remove`d an in-progress slice's worktree but kept the branch would see it reclassified as orphan (refuse) — acceptable, because that IS the ambiguous/stranded case we want to STOP on.
2. **Merge-ancestry discriminator** — refuse only on `slice/*` branches not yet merged into the default branch.
   - Pros: precisely targets "unmerged work."
   - Cons: duplicates the stranded detector's (slice-087) job; needs default-branch resolution + per-branch merge-base checks; an active parallel slice is *also* unmerged, so this does NOT actually separate active-parallel from stale — it would still false-positive on every live peer.
3. **Status-quo + permanent manual override** — keep flag-all, accept the override prompt on every parallel merge.
   - Pros: zero code.
   - Cons: trains operators to reflexively override a safety gate (the exact failure mode the gate exists to prevent); blocks the rebase path; documented as a known defect in the project's own memory.

## Decision

Adopt **Option 1**. Introduce `tools/stale_branch_classifier.py` reusing the **raw** `pulse_worktree_resolver._parse_worktree_porcelain` parser (NOT the higher-level `detect_active_worktrees`, whose slice-name-suffix filter + prunable/detached drops would silently misclassify worktree-backed branches as orphans — Critic B3). A non-current local `slice/*` branch is classified `parallel` (worktree-backed → allow, surfaced as an informational note) or `orphan` (worktree-less → contributes to a `refuse` verdict that STOPs with the existing actionable message). The current slice's own worktree is excluded by **path-equality** (`git rev-parse --show-toplevel`), with current-branch exclusion as defense-in-depth (Critic B1); the classifier runs at pre-flight while cwd is still the slice worktree. Both guardrail surfaces (`--merge`, `--push`) invoke a byte-identical block (symmetry). The CLI exit contract is 0/1/2 matching the sibling helpers (Critic M1). The verdict is conservative: worktree-less always refuses (covering both plain orphans and stranded-complete branches whose worktree was removed) — we never sub-classify worktree-less branches by merge-ancestry (that is the stranded detector's axis, not this guardrail's).

If the helper is unavailable (pre-install / import failure / exit 2), the skill falls back to the **legacy flag-all check** — strictly no weaker than today (bootstrap defense per ADR-064 / PCR-2b bootstrap-guard precedent), and fail-visible (surface the reason).

## Consequences

- `--merge` / `--push` pre-flight PASSES when all other `slice/*` branches are worktree-backed, removing the spurious override prompt and making PSQ-3's rebase reachable while peers are in flight.
- Genuine orphans and stranded-complete branches still STOP the operation (protection preserved).
- New module `tools/stale_branch_classifier.py` joins the parallel-slice tool family; wired into `skills/commit-slice/SKILL.md` (WIRE-1) and pinned by `tests/methodology/test_stale_branch_parallel_aware.py`.
- Editing SKILL.md re-triggers OSDG-1 (`test_commit_slice_skill_drift.py`) + the structural anchor tests; the existing refuse-message literals are preserved to minimize anchor churn.
- PMI-1: a new tool module → `plugin.yaml` + `tools/install_audit.py` canonical lists must enumerate it; INST-1 install-parity re-verified.

## Reversibility

**Cheap.** The change is a heuristic refinement localized to two SKILL.md prose blocks + one small read-only helper. Reverting means reverting the two SKILL.md prose blocks to the legacy `for-each-ref` check and deleting the helper + its test (and re-pinning OSDG-1 drift) — not literally one line, but cheap and self-contained (Critic m1). The bootstrap-fallback path already *is* the legacy flag-all-minus-current behavior, so the old behavior is never more than a helper-removal away. No data model, no contract, no irreversible state.
