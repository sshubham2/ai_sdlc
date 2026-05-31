# Slice queue

_Generated: 2026-05-31T17:53:38+00:00 by /slice during slice-094 definition_

## Candidates

### harden-vault-skill-write-discipline

- **Source:** risk-register R-32 skill-driven residual
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/reflect/SKILL.md`, `tools/_vault_write.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### audit-cp1252-decode-pattern-across-tools

- **Source:** risk-register R-30 (slice-090)
- **Blast-radius:** `tools/project_frame_synth.py`, `tools/pulse_worktree_resolver.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### fix-install-completeness-verification-gap

- **Source:** risk-register R-29
- **Blast-radius:** `tools/install_audit.py`, `tools/plugin_manifest_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### harden-parallel-install-contention

- **Source:** risk-register R-28
- **Blast-radius:** `tools/critique_agent_drift_audit.py`, `tools/install_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### extend-osdg-1-to-slice-candidates

- **Source:** risk-register R-13
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/skill_drift_equality.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2
- **Blast-radius:** `skills/diagnose/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-claim-sequence-number-for-clock-skew-detection

- **Source:** risk-register R-23
- **Blast-radius:** `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-index-md-soft-promotion-or-light-hard-path

- **Source:** deferred ADR-075 (slice-083 M4)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW
