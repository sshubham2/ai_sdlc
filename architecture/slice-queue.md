# Slice queue

_Generated: 2026-06-02T03:43:05+00:00 by /slice during slice-100 definition_

## Candidates

### execute-vault-flip

- **Source:** external-vault initiative (R-32 final; depends on slice-100 readiness audit)
- **Blast-radius:** `INSTALL.md`, `tools/_vault_git.py`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** MEDIUM

### isolate-per-worktree-install

- **Source:** risk-register R-28+R-29
- **Blast-radius:** `tools/critique_agent_drift_audit.py`, `tools/install_audit.py`, `tools/plugin_manifest_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### enforce-or-downgrade-drift-check-gate

- **Source:** diagnose-out backlog SC-007/SC-006
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/drift-check/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2
- **Blast-radius:** `skills/diagnose/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### declare-tomllib-dependency

- **Source:** diagnose-out backlog SC-002
- **Blast-radius:** `pyproject.toml`, `tools/validate_slice_layers.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### harden-pcr-1-soft-baseline-corruption

- **Source:** risk-register R-24
- **Blast-radius:** `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-claim-sequence-number-for-clock-skew-detection

- **Source:** risk-register R-23
- **Blast-radius:** `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-project-frame-degrade-signal

- **Source:** risk-register R-26
- **Blast-radius:** `tools/project_frame_synth.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-index-md-soft-promotion-or-light-hard-path

- **Source:** deferred ADR-075 (slice-083 M4)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

## Pick log

- slice-100-add-vault-flip-readiness-audit — picked 2026-06-02T03:43:15+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
