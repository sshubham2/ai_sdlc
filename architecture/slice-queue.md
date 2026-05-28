# Slice queue

_Generated: 2026-05-28T20:30:00+00:00 by /slice during slice-077 definition_

## Candidates

### add-pcr-2-vault-claim-and-hard-conflict-critic-stack

- **Source:** Phase 1 parallel-slice readiness — PCR-2 closes the conflict-resolution story slice-076 started. Vault-claim timestamp-winner + light Critic + auto-re-pick; hard-conflict full /critique + /critique-review on proposed resolution + TRI-RESOLVE-1 user triage. Without PCR-2, hard conflicts still STOP and hand off to user.
- **Blast-radius:** `agents/critique-review.md`, `agents/critique.md`, `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** HIGH

### bundle-074-code-critic-cleanup

- **Source:** Re-queued from original slice-076 scope (deferred during 2026-05-28 conversation). Closes P1.1 (build-slice point-4 variable-scope footgun; fresh-shell unbound $wt_base/$repo_root/$default) + P3.10 (cp1252 mojibake in tools/slice_queue_writer.py) + slice-074 code-Critic m1-m5 deferrals. Known footguns; ship after PCR-2.
- **Blast-radius:** `skills/build-slice/SKILL.md`, `tests/methodology/test_build_slice_skill_cp_r_step.py`, `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py`, `tests/methodology/test_r_20_retired.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### add-sp-1-slice-pick-auto-pick-via-slice-no-arg

- **Source:** Phase 1 ergonomics — closes the 5-session auto-pick gap surfaced 2026-05-28. /slice with no arg → invoke tools/slice_pick.py helper → pick highest-priority unclaimed NON-OVERLAPPING candidate → handle claim-race with structured ask. /slice <name> behavior preserved. NEW tools/slice_pick.py library + CLI for direct invocation outside /slice.
- **Blast-radius:** `skills/slice/SKILL.md`, `tools/slice_pick.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### close-psq-3-conflict-stop-re-entry-semantics

- **Source:** Phase 1 — source-pending-items.txt P2.3 (PSQ-3 conflict-STOP at sub-step 2.5 re-entry semantics undefined; slice-074's PSQ-3 was fast-forward no-op so re-entry not exercised; user manually resolves + re-invokes /commit-slice --merge → skill should detect rebase-in-progress + SKIP sub-step 2 commit attempt). Orthogonal to PCR-1's auto-regen (different code path).
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### parallel-slice-family-parity-audit

- **Source:** Phase 1 — source-pending-items.txt P3.6 (BRANCH-2 + PSQ-1 + PSQ-2 + PSQ-3 + PCR-1 cross-spec parity audit — same default-resolution helper + canonical worktree path + SOAD-1 form + WORKTREE=skip grammar across now-5 SKILL.md surfaces). PCR-1 adds a 5th member to the parallel-slice rule family; parity audit becomes more valuable.
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `tools/parallel_slice_family_parity_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-psq-4-push-time-rebase

- **Source:** Phase 2 PR-workflow — source-pending-items.txt P2.1 (PSQ-4: --push does NOT rebase slice/NNN onto default before push; PR-based workflows that require clean history will need this — symmetric copy of PSQ-3 sub-step 2.5). Note: PSQ-N continues the parallel-slice-queue rule family; PCR-N is a sibling family (parallel-conflict-resolution).
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_push_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### bcr-1-dual-tree-replication

- **Source:** Phase 2 BCR-1 — source-pending-items.txt P3.3 (BCR-1 round-trip dual-tree replication: diagnose-out/backlog.md edits in worktree don't propagate to main tree via --merge; N=2 cumulative slice-070/071).
- **Blast-radius:** `.gitignore`, `skills/commit-slice/SKILL.md`, `tools/bcr_1_dual_tree_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### cross-worktree-race-hardening

- **Source:** Phase 3 cross-machine — source-pending-items.txt P3.5 (concurrent /build-slice invocations across worktrees: graphify-out + diagnose-out per-worktree no convergence; slice-queue.md last-write-wins; risk-register.md SAME risk ID conflict). PCR-1's soft-regen auto-resolves most of this for slice-queue.md / _index.md / shippability.md; cross-worktree-race-hardening covers the residual.
- **Blast-radius:** `skills/build-slice/SKILL.md`, `tools/slice_queue_claim.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** MEDIUM

### add-psq-5-rebase-merges-strategy

- **Source:** Phase 3 complex-topology — source-pending-items.txt P3.1 (PSQ-5: --rebase-merges strategy for preserving merge-commit topology when rebasing branches that already merged subsidiary lineage).
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_psq_5.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-psq-6-merge-driver-registration

- **Source:** Phase 3 generated-files — source-pending-items.txt P3.2 (PSQ-6: merge-driver registration for automated handling of specific files during merge conflicts; e.g., always-take-theirs for generated files, custom drivers for serialized state). Largely subsumed by PCR-1 soft-regen for the canonical state-file set; PSQ-6 covers the long-tail custom-driver case.
- **Blast-radius:** `.gitattributes`, `skills/commit-slice/SKILL.md`, `tools/psq_6_merge_driver_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### bundle-075-code-critic-cleanup

- **Source:** Phase 1 — re-queued from slice-076 reflection's Deferred section. Closes slice-075's 2 code-Critic findings (m1 substring-vs-line-start anchor analysis on `_extract_substep_2_1_block` helper unanchored `find("2.1.")` substring + m2 file-move stale-anchor sweep in mission-brief.md / design.md). Companion candidate to bundle-074-code-critic-cleanup (same target slice in slice-079+ bundle).
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_substep_2_1_block.py`, mission-brief.md anchor refs in archived slice-075 vault files
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM
