# Slice queue

_Generated: 2026-05-26T09:25:24+00:00 by /slice during slice-071 definition_

## Candidates

### implement-or-downgrade-drift-check

- **Source:** diagnose-out/backlog.md SC-006 + SC-007 + SC-008 (documented-but-unenforced-gate cluster; HIGH severity)
- **Blast-radius:** `skills/drift-check/SKILL.md`, `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### add-LOCAL-slice-queue-claim-state-machine

- **Source:** slice-067 standing nomination (original PSQ-2 nominee; local-only same-machine sessions)
- **Blast-radius:** `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-rebase-and-conflict-discipline

- **Source:** slice-067 standing nomination (original PSQ-3 nominee; /commit-slice rebases default before merge)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/branch_workflow_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

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

### rename-architecture-to-sdlc

- **Source:** user-intent (carry-over; now structurally tractable post-slice-069 vault-in-git + slice-068 VAULT_ROOT seam)
- **Blast-radius:** `.gitignore`, `CLAUDE.md`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** NONE

### extract-shared-repo-root-helper

- **Source:** diagnose-out/backlog.md SC-019 (repo-root sentinel inconsistent across audits)
- **Blast-radius:** `tools/branch_workflow_audit.py`, `tools/critique_review_prerequisite_audit.py`, `tools/pipeline_chain_audit.py`, `tools/shippability_path_audit.py`, `tools/test_first_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-shippability-runner-cli-tests-bundle

- **Source:** diagnose-out/backlog.md SC-004 + SC-011 + SC-013 + SC-014 + SC-015 + SC-016 + SC-020 + SC-021 (CLI exit-1 untested 8 findings batch)
- **Blast-radius:** `tests/methodology/test_mock_budget_lint.py`, `tests/methodology/test_plugin_manifest_audit.py`, `tests/methodology/test_triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-WS-1-ETC-1-TFFL-1-extension

- **Source:** slice-066 + slice-067 standing /critic-calibrate nomination (R-7-class silent-default-off bug witnessed at WS-1; apply slice-034 TFFL-1 pattern verbatim)
- **Blast-radius:** `tools/exploratory_charter_audit.py`, `tools/walking_skeleton_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### address-SC-010-triage-audit-monolith

- **Source:** diagnose-out/backlog.md SC-010 (audit_critique_file CC=37 230 LOC on TRI-1 gate path; HIGH severity)
- **Blast-radius:** `tools/triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM
