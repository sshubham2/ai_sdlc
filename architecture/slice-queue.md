# Slice queue

_Generated: 2026-05-31T18:21:04+00:00 by /slice during slice-096 definition_

## Candidates

### add-slice-candidates-drift-guard

- **Source:** risk-register R-13
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/methodology/test_slice_candidates_skill_drift.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2
- **Blast-radius:** `skills/diagnose/SKILL.md`, `tests/skills/diagnose/test_skill_md_pins.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### audit-cp1252-decode-pattern-across-tools

- **Source:** risk-register R-30
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

### add-claim-sequence-number-for-clock-skew-detection

- **Source:** risk-register R-23
- **Blast-radius:** `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### harden-pcr-1-soft-baseline-corruption

- **Source:** risk-register R-24
- **Blast-radius:** `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-project-frame-degrade-signal

- **Source:** risk-register R-26
- **Blast-radius:** `tools/project_frame_synth.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### flip-vault-to-external-shared-root

- **Source:** external-vault initiative (blocked on R-32: 094+095)
- **Blast-radius:** `INSTALL.md`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** NONE

### add-index-md-soft-promotion-or-light-hard-path

- **Source:** deferred ADR-075 (slice-083 M4)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW
