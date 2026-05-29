# Slice queue

_Generated: 2026-05-29T04:46:43+00:00 by /slice during slice-079 definition_

## Candidates

### add-pcr-2b-hard-conflict-critic-stack

- **Source:** Phase 1 parallel-slice readiness — promoted from PCR-2 split at slice-078 (2026-05-28). Closes HARD-conflict path: spawns design-Critic + meta-Critic agents on proposed merge resolution + TRI-RESOLVE-1 user triage gate mirroring TRI-1.
- **Blast-radius:** `agents/critique-review.md`, `agents/critique.md`, `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** HIGH

### add-sp-1-slice-pick-auto-pick-via-slice-no-arg

- **Source:** Phase 1 ergonomics — slice-077 reflection's slice-079 nomination + RE-DEMONSTRATED LIVE at slice-079 /slice invocation (no-arg /slice required hand-ranking). /slice with no arg → invoke tools/slice_pick.py helper → pick highest-priority unclaimed NON-OVERLAPPING candidate → handle claim-race with structured ask.
- **Blast-radius:** `skills/slice/SKILL.md`, `tools/slice_pick.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### parallel-slice-family-parity-audit

- **Source:** Phase 1 — slice-077 reflection's Deferred extraction-trigger. N=3 worktree-list-porcelain parsers Python-side post-slice-077; cross-spec parity for BRANCH-2 + PSQ-1/2/3 + PCR-1/2a (now 6-member family). Same default-resolution helper + canonical worktree path + SOAD-1 form + WORKTREE=skip grammar across now-6 SKILL.md surfaces.
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `skills/pulse/SKILL.md`, `tools/parallel_slice_family_parity_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### close-psq-3-conflict-stop-re-entry-semantics

- **Source:** Phase 1 — source-pending-items.txt P2.3. PSQ-3 conflict-STOP at sub-step 2.5 re-entry semantics undefined; user manually resolves + re-invokes /commit-slice --merge → skill should detect rebase-in-progress + SKIP sub-step 2 commit attempt. Orthogonal to PCR-1's auto-regen (different code path).
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### add-psq-4-push-time-rebase

- **Source:** Phase 2 PR-workflow — source-pending-items.txt P2.1. PSQ-4: --push does NOT rebase slice/NNN onto default before push; PR-based workflows that require clean history will need this — symmetric copy of PSQ-3 sub-step 2.5.
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_push_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### bcr-1-dual-tree-replication

- **Source:** Phase 2 BCR-1 — source-pending-items.txt P3.3. BCR-1 round-trip dual-tree replication: diagnose-out/backlog.md edits in worktree don't propagate to main tree via --merge; N=2 cumulative slice-070/071.
- **Blast-radius:** `.gitignore`, `skills/commit-slice/SKILL.md`, `tools/bcr_1_dual_tree_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### cross-worktree-race-hardening

- **Source:** Phase 3 cross-machine — source-pending-items.txt P3.5. Concurrent /build-slice invocations across worktrees: graphify-out + diagnose-out per-worktree no convergence; slice-queue.md last-write-wins; risk-register.md SAME risk ID conflict. PCR-1's soft-regen auto-resolves most of this for slice-queue.md / _index.md / shippability.md; cross-worktree-race-hardening covers the residual.
- **Blast-radius:** `skills/build-slice/SKILL.md`, `tools/slice_queue_claim.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** MEDIUM

### add-psq-5-rebase-merges-strategy

- **Source:** Phase 3 complex-topology — source-pending-items.txt P3.1. PSQ-5: --rebase-merges strategy for preserving merge-commit topology when rebasing branches that already merged subsidiary lineage.
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_psq_5.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-psq-6-merge-driver-registration

- **Source:** Phase 3 generated-files — source-pending-items.txt P3.2. PSQ-6: merge-driver registration for automated handling of specific files during merge conflicts; e.g., always-take-theirs for generated files, custom drivers for serialized state. Largely subsumed by PCR-1 soft-regen for the canonical state-file set; PSQ-6 covers the long-tail custom-driver case.
- **Blast-radius:** `.gitattributes`, `skills/commit-slice/SKILL.md`, `tools/psq_6_merge_driver_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-claim-sequence-number-for-clock-skew-detection

- **Source:** R-23 corrigibility hook per PCR-2a (slice-078) m9 ACCEPTED-PENDING + /critique-review M-add-2 ACCEPTED-FIXED precedent. Adds a monotonic **Claim-seq:** field to PSQ-2 claim records; PCR-2a switches from strict-newer Claimed-at to strict-greater Claim-seq. Removes clock-skew dependence in cross-machine cooperative-not-adversarial parallel-slice workflow.
- **Blast-radius:** `architecture/slice-queue.md`, `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW
