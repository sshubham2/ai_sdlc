# Slice queue

_Generated: 2026-05-27T14:33:31+00:00 by /slice during slice-072 definition_

## Candidates

### implement-or-downgrade-drift-check

- **Source:** diagnose-out/backlog.md SC-006 + SC-007 + SC-008 (documented-but-unenforced-gate cluster; HIGH severity)
- **Blast-radius:** `skills/drift-check/SKILL.md`, `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### add-rebase-and-conflict-discipline

- **Source:** slice-067 standing nomination (original PSQ-3 nominee; /commit-slice rebases default before merge)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/branch_workflow_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### extend-osdg-1-to-slice-candidates

- **Source:** risk-register R-13 (OSDG-1 drift guard not yet extended to /slice-candidates; explicit "Strong next-slice candidate")
- **Blast-radius:** `skills/slice-candidates/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### codify-branch-2-cp-r-tax

- **Source:** risk-register R-20 (gitignored diagnose-out/ + graphify-out/ cp-r tax; user-flagged "we need a better solution" at slice-071)
- **Blast-radius:** `skills/build-slice/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### add-WS-1-ETC-1-TFFL-1-extension

- **Source:** slice-066 + slice-067 standing /critic-calibrate nomination (R-7-class silent-default-off bug witnessed at WS-1; apply slice-034 TFFL-1 pattern verbatim)
- **Blast-radius:** `tools/exploratory_charter_audit.py`, `tools/walking_skeleton_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### extract-shared-repo-root-helper

- **Source:** diagnose-out/backlog.md SC-019 (repo-root sentinel inconsistent: .git OR VERSION vs .git only across audits)
- **Blast-radius:** `tools/branch_workflow_audit.py`, `tools/critique_review_prerequisite_audit.py`, `tools/pipeline_chain_audit.py`, `tools/shippability_path_audit.py`, `tools/test_first_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2 (no programmatic test ensures /diagnose emits cwd-mismatch warning at runtime)
- **Blast-radius:** `skills/diagnose/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### address-SC-010-triage-audit-monolith

- **Source:** diagnose-out/backlog.md SC-010 (audit_critique_file CC=37 230 LOC on TRI-1 gate path; HIGH severity)
- **Blast-radius:** `tools/triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-shippability-runner-cli-tests-bundle

- **Source:** diagnose-out/backlog.md SC-004 + SC-011 + SC-013 + SC-014 + SC-015 + SC-016 + SC-020 + SC-021 (CLI exit-1 untested 8 findings batch)
- **Blast-radius:** `tests/methodology/test_mock_budget_lint.py`, `tests/methodology/test_plugin_manifest_audit.py`, `tests/methodology/test_triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### cleanup-sc-022-supersede-audit-dead-read-text

- **Source:** diagnose-out/backlog.md SC-022 (dead _read_text helper in supersede_audit.py; BCR-1 round-trip candidate)
- **Blast-radius:** `tools/supersede_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW
