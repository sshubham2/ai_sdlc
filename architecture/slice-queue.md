# Slice queue

_Generated: 2026-05-26T03:45:25+00:00 by /slice during slice-070 definition_

## Candidates

### bundle-066-to-070-code-critic-cleanup

- **Source:** Accumulated code-Critic advisory backlog across slice-066/067/068/069 (19 findings)
- **Blast-radius:** `C:/Users/sshub/ai_sdlc/tools/branch_workflow_audit.py`, `C:/Users/sshub/ai_sdlc/tools/slice_queue_writer.py`, `C:/Users/sshub/ai_sdlc/tools/validate_slice_layers.py`, `tests/methodology/test_vault_root_constant.py`, `tools/branch_workflow_audit.py`, `tools/slice_queue_writer.py`, `tools/validate_slice_layers.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** NONE

### implement-or-downgrade-drift-check

- **Source:** diagnose-out/backlog.md SC-006 + SC-007 + SC-008 (documented-but-unenforced-gate cluster; HIGH severity)
- **Blast-radius:** `C:/Users/sshub/ai_sdlc/tools/build_checks_audit.py`, `skills/drift-check/SKILL.md`, `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### harden-slice-068-test-vault-root-constant

- **Source:** diagnose-out/backlog.md SC-028 (slice-068 code-review 4 test-quality gaps bundle)
- **Blast-radius:** `tests/methodology/test_vault_root_constant.py`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-LOCAL-slice-queue-claim-state-machine

- **Source:** slice-067 plan (original PSQ-2 nominee; now scoped to local-only same-machine sessions)
- **Blast-radius:** `C:/Users/sshub/ai_sdlc/tools/slice_queue_writer.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-rebase-and-conflict-discipline

- **Source:** slice-067 plan (original PSQ-3 nominee; /commit-slice rebases default before merge)
- **Blast-radius:** `C:/Users/sshub/ai_sdlc/tools/branch_workflow_audit.py`, `skills/commit-slice/SKILL.md`, `tools/branch_workflow_audit.py`
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

- **Source:** user-intent (carry-over from slice-069 slice-queue; now structurally tractable post-slice-069)
- **Blast-radius:** `.gitignore`, `CLAUDE.md`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** NONE

### extract-shared-repo-root-helper

- **Source:** diagnose-out/backlog.md SC-019 (repo-root sentinel inconsistent across audits)
- **Blast-radius:** `C:/Users/sshub/ai_sdlc/tools/branch_workflow_audit.py`, `C:/Users/sshub/ai_sdlc/tools/critique_review_prerequisite_audit.py`, `C:/Users/sshub/ai_sdlc/tools/pipeline_chain_audit.py`, `C:/Users/sshub/ai_sdlc/tools/shippability_path_audit.py`, `C:/Users/sshub/ai_sdlc/tools/test_first_audit.py`, `tools/branch_workflow_audit.py`, `tools/critique_review_prerequisite_audit.py`, `tools/pipeline_chain_audit.py`, `tools/shippability_path_audit.py`, `tools/test_first_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-shippability-runner-cli-tests-bundle

- **Source:** diagnose-out/backlog.md SC-004 + SC-011 + SC-013 + SC-014 + SC-015 + SC-016 + SC-020 + SC-021 (CLI exit-1 untested 8 findings batch)
- **Blast-radius:** `C:/Users/sshub/ai_sdlc/tests/methodology/test_mock_budget_lint.py`, `C:/Users/sshub/ai_sdlc/tests/methodology/test_plugin_manifest_audit.py`, `C:/Users/sshub/ai_sdlc/tests/methodology/test_triage_audit.py`, `tests/methodology/test_mock_budget_lint.py`, `tests/methodology/test_plugin_manifest_audit.py`, `tests/methodology/test_triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM
