# Slice queue

_Generated: 2026-05-25T05:07:48+00:00 by /slice during slice-069 definition_

## Candidates

### rename-architecture-to-sdlc

- **Source:** user-intent (query-design 2026-05-25; second half of original rename-and-track candidate, split per slice-069 Step 5 scope check)
- **Blast-radius:** `.gitignore`, `CLAUDE.md`, `pipeline.md`, `tools/_vault_paths.py`, `tutorial.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** NONE

### add-LOCAL-slice-queue-claim-state-machine

- **Source:** slice-067 plan (original PSQ-2 nominee; now scoped to local-only same-machine sessions per query-design 2026-05-25 finding)
- **Blast-radius:** `tools/slice_queue_writer.py`, `{'id': 'slice_queue_writer_rationale_1', 'label': 'Parallel-slice queue writer (PSQ-1).  Per **PSQ-1** (`methodology-changelog.md', 'type': '', 'path': ''}`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### fix-psq-1-slice-queue-writer-raw-dict-leak

- **Source:** diagnose-out/backlog.md SC-027 (slice-068 critique m2 ACCEPTED-PENDING + critique-review m2 severity adjustment)
- **Blast-radius:** `tools/slice_queue_writer.py`, `{'id': 'slice_queue_writer_rationale_1', 'label': 'Parallel-slice queue writer (PSQ-1).  Per **PSQ-1** (`methodology-changelog.md', 'type': '', 'path': ''}`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### harden-slice-068-test-vault-root-constant

- **Source:** diagnose-out/backlog.md SC-028 (slice-068 code-review 4 test-quality gaps bundle)
- **Blast-radius:** `tests/methodology/test_vault_root_constant.py`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-rebase-and-conflict-discipline

- **Source:** slice-067 plan (original PSQ-3 nominee; /commit-slice rebases default before merge + structured-options ASK on conflict)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/branch_workflow_audit.py`, `{'id': 'branch_workflow_audit_rationale_1', 'label': 'Branch workflow audit (BRANCH-1).  Validates that the current git branch match', 'type': '', 'path': ''}`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### remote-cross-machine-slice-claim-semantics

- **Source:** user-intent (query-design 2026-05-25; candidate #3 of cross-machine-parallel chain; needs /risk-spike)
- **Blast-radius:** `tools/slice_queue_writer.py`, `{'id': 'slice_queue_writer_rationale_1', 'label': 'Parallel-slice queue writer (PSQ-1).  Per **PSQ-1** (`methodology-changelog.md', 'type': '', 'path': ''}`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** HIGH

### rescope-or-rename-claim-state-machine

- **Source:** user-intent (query-design 2026-05-25; depends on remote-claim-semantics outcome; candidate #4 of cross-machine-parallel chain)
- **Blast-radius:** `unknown`
- **Parallel-safety:** UNKNOWN-NO-HINT-FILES
- **Effort:** SMALL
- **Risk-retired:** LOW

### extend-osdg-1-to-slice-candidates

- **Source:** risk-register R-13 (OSDG-1 drift guard not yet extended to /slice-candidates)
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/methodology/test_slice_candidates_skill_drift.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2 (no programmatic test ensures /diagnose emits cwd-mismatch warning at runtime)
- **Blast-radius:** `skills/diagnose/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-shippability-runner-cli-tests

- **Source:** diagnose-out/backlog.md SC-014/SC-015/SC-016/SC-020/SC-021 cluster (CLI exit-1 path untested systemic theme)
- **Blast-radius:** `tools/branch_workflow_audit.py`, `tools/critique_review_audit.py`, `tools/cross_spec_parity_audit.py`, `tools/shippability_path_audit.py`, `tools/wiring_matrix_audit.py`, `{'id': 'branch_workflow_audit_rationale_1', 'label': 'Branch workflow audit (BRANCH-1).  Validates that the current git branch match', 'type': '', 'path': ''}`, `{'id': 'critique_review_audit_rationale_1', 'label': "Critique-review structural audit (DR-1).  Validates that a slice's `critique-r", 'type': '', 'path': ''}`, `{'id': 'cross_spec_parity_audit_rationale_1', 'label': 'Cross-spec parity audit (CSP-1).  Walks the Heavy-mode artifacts (`architectur', 'type': '', 'path': ''}`, `{'id': 'shippability_path_audit_rationale_1', 'label': 'Shippability-catalog test-path existence audit (PTFCD-1, sub-mode (b)).  Parse', 'type': '', 'path': ''}`, `{'id': 'wiring_matrix_audit_rationale_1', 'label': "Wiring matrix audit (WIRE-1).  Parses the wiring matrix from a slice's design.", 'type': '', 'path': ''}`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW
