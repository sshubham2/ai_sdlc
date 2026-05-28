# Slice queue

_Generated: 2026-05-28T09:48:11+00:00 by /slice during slice-076 definition_

## Candidates

### close-psq-3-conflict-stop-re-entry-semantics

- **Source:** Phase 1 readiness — source-pending-items.txt P2.3 (PSQ-3 conflict-STOP at sub-step 2.5 re-entry semantics undefined; slice-074's PSQ-3 was fast-forward no-op so re-entry not exercised)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### parallel-slice-family-parity-audit

- **Source:** Phase 1 readiness — source-pending-items.txt P3.6 (BRANCH-2 + PSQ-1 + PSQ-2 + PSQ-3 cross-spec parity audit — same default-resolution helper + canonical worktree path + SOAD-1 form + WORKTREE=skip grammar across 4 SKILL.md surfaces)
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `tools/parallel_slice_family_parity_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-psq-4-push-time-rebase

- **Source:** Phase 2 PR-workflow — source-pending-items.txt P2.1 (PSQ-4: --push does NOT rebase slice/NNN onto default before push; PR-based workflows that require clean history will need this — symmetric copy of PSQ-3 sub-step 2.5)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_push_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### bcr-1-dual-tree-replication

- **Source:** Phase 2 BCR-1 — source-pending-items.txt P3.3 (BCR-1 round-trip dual-tree replication: diagnose-out/backlog.md edits in worktree don't propagate to main tree via --merge; N=2 cumulative slice-070/071)
- **Blast-radius:** `.gitignore`, `skills/commit-slice/SKILL.md`, `tools/bcr_1_dual_tree_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-psq-5-rebase-merges-strategy

- **Source:** Phase 3 complex-topology — source-pending-items.txt P3.1 (PSQ-5: --rebase-merges strategy for preserving merge-commit topology when rebasing branches that already merged subsidiary lineage)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_psq_5.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-psq-6-merge-driver-registration

- **Source:** Phase 3 generated-files — source-pending-items.txt P3.2 (PSQ-6: merge-driver registration for automated handling of specific files during merge conflicts; e.g., always-take-theirs for generated files, custom drivers for serialized state)
- **Blast-radius:** `.gitattributes`, `skills/commit-slice/SKILL.md`, `tools/psq_6_merge_driver_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### cross-worktree-race-hardening

- **Source:** Phase 3 cross-machine — source-pending-items.txt P3.5 (concurrent /build-slice invocations across worktrees: graphify-out + diagnose-out per-worktree no convergence; slice-queue.md last-write-wins; risk-register.md SAME risk ID conflict)
- **Blast-radius:** `skills/build-slice/SKILL.md`, `tools/slice_queue_claim.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** MEDIUM

### retrofit-soad-1-in-commit-slice-yes-no-prompts

- **Source:** Carry-over P2.2 (6 raw yes/no prompts at skills/commit-slice/SKILL.md L173/L175/L202/L203/L205/L255 — SOAD-1 retrofit)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_soad_1.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### extend-tffl-1-to-ws-1-and-etc-1-audits

- **Source:** Carry-over P3.7 (silent-default-off class extends to WS-1 + ETC-1 audits — apply slice-034 TFFL-1 pattern verbatim)
- **Blast-radius:** `tools/exploratory_charter_audit.py`, `tools/walking_skeleton_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### extend-osdg-1-to-slice-candidates

- **Source:** Carry-over risk-register R-13 (OSDG-1 drift guard not yet extended to /slice-candidates skill)
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/methodology/test_slice_candidates_skill_drift.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW
