# Slice queue

_Generated: 2026-05-27T18:07:34+00:00 by /slice during slice-073 definition_

## Candidates

### add-rebase-and-conflict-discipline

- **Source:** slice-067 + slice-072 standing nomination (PSQ-3: /commit-slice rebases default before merge)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/branch_workflow_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### codify-branch-2-cp-r-tax

- **Source:** risk-register R-20 (gitignored diagnose-out/ + graphify-out/ cp-r tax N=7; user-flagged 'we need a better solution')
- **Blast-radius:** `skills/build-slice/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### bundle-072-code-critic-cleanup

- **Source:** slice-072 reflection L88 (voluntary-restraint N=13; 9 code-Critic advisories + R-20 + BC-GLOBAL-2 carve-out)
- **Blast-radius:** `tools/slice_queue_claim.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### critic-calibrate-tphd-bc-global-ac-count

- **Source:** slice-072 reflection L84 (TPHD-1 N=6 + BC-GLOBAL-2 N=4 + AC-count N=2 promotion signals; /critic-calibrate is genuinely overdue)
- **Blast-radius:** `agents/critique.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### implement-or-downgrade-drift-check

- **Source:** diagnose-out/backlog.md SC-006 + SC-007 + SC-008 (documented-but-unenforced-gate cluster; HIGH severity)
- **Blast-radius:** `skills/drift-check/SKILL.md`, `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### extend-osdg-1-to-slice-candidates

- **Source:** risk-register R-13 (OSDG-1 drift guard not yet extended to /slice-candidates)
- **Blast-radius:** `skills/slice-candidates/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-WS-1-ETC-1-TFFL-1-extension

- **Source:** slice-066 + slice-067 standing /critic-calibrate nomination (R-7-class silent-default-off bug witnessed at WS-1)
- **Blast-radius:** `tools/exploratory_charter_audit.py`, `tools/walking_skeleton_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### extract-shared-repo-root-helper

- **Source:** diagnose-out/backlog.md SC-019 (repo-root sentinel inconsistent across audits)
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

- **Source:** diagnose-out/backlog.md SC-010 (audit_critique_file CC=37 230 LOC on TRI-1 gate path)
- **Blast-radius:** `tools/triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM
