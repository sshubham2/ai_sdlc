# Slice queue

_Generated: 2026-05-29T08:57:24+00:00 by /slice during slice-080 definition_

## Candidates

### fix-drift-check-enforcement-gap

- **Source:** diagnose-out/backlog.md SC-007 (F-HALF-3a7f1c8e) — HIGH severity: /drift-check mandated before commit but no backing tool/hook/installer
- **Blast-radius:** `skills/adopt/SKILL.md`, `skills/drift-check/SKILL.md`, `skills/triage/SKILL.md`, `tools/drift_check.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### add-sp-1-slice-pick-auto-pick-via-slice-no-arg

- **Source:** slice-queue + slice-077 reflection; RE-DEMONSTRATED LIVE at slice-080 /slice (no-arg required hand-ranking)
- **Blast-radius:** `skills/slice/SKILL.md`, `tools/slice_pick.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-pcr-2b-hard-conflict-critic-stack

- **Source:** slice-queue Phase 1 — PCR-2 split at slice-078; HARD-conflict Critic-stack path (planned slice-080 in source-pending, deferred)
- **Blast-radius:** `agents/critique-review.md`, `agents/critique.md`, `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** HIGH

### fix-val1-tomllib-silent-disable

- **Source:** diagnose-out/backlog.md SC-002 (F-CONFIG-ed3ebdfd) — VAL-1 Layer B silently disabled on Python 3.10 (tomllib 3.11+, no tomli backport)
- **Blast-radius:** `pyproject.toml`, `tools/validate_slice_layers.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### extend-osdg-1-drift-guard-to-slice-candidates

- **Source:** risk-register R-13 (open) — OSDG-1 drift guard not yet extended to /slice-candidates
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/methodology/test_slice_candidates_skill_drift.py`, `tools/install_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### parallel-slice-family-parity-audit

- **Source:** slice-queue Phase 1 — slice-077 reflection extraction-trigger; cross-spec parity for the 6-member parallel-slice family
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `skills/pulse/SKILL.md`, `tools/parallel_slice_family_parity_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### close-psq-3-conflict-stop-re-entry-semantics

- **Source:** slice-queue Phase 1 — source-pending P2.3; PSQ-3 conflict-STOP re-entry semantics undefined
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### find-real-mojibake-source

- **Source:** source-pending-items.txt P3.10' (routed from P3.10 per slice-079 /critique B2) — cp1252 mojibake root cause is upstream of slice_queue_writer
- **Blast-radius:** `skills/slice/SKILL.md`, `tools/slice_pick.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### bcr-1-dual-tree-replication

- **Source:** slice-queue Phase 2 — source-pending P3.3; diagnose-out/backlog.md worktree edits don't propagate to main tree via --merge (N=2 slice-070/071)
- **Blast-radius:** `.gitignore`, `skills/commit-slice/SKILL.md`, `tools/bcr_1_dual_tree_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-claim-sequence-number-for-clock-skew-detection

- **Source:** risk-register R-23 (open) — PCR-2a clock-skew; add monotonic Claim-seq field
- **Blast-radius:** `architecture/slice-queue.md`, `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW
