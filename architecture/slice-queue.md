# Slice queue

_Generated: 2026-06-01T17:37:16+00:00 by /slice during slice-098 definition_

## Candidates

### isolate-per-worktree-install

- **Source:** risk-register R-28+R-29
- **Blast-radius:** `tools/critique_agent_drift_audit.py`, `tools/install_audit.py`, `tools/plugin_manifest_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### flip-vault-to-external-shared-root

- **Source:** external-vault initiative (R-32 final, blocked on slice-098)
- **Blast-radius:** `INSTALL.md`, `tools/_vault_paths.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** MEDIUM

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2
- **Blast-radius:** `skills/diagnose/SKILL.md`, `tests/skills/diagnose/test_skill_md_pins.py`
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

### fix-pyproject-version-drift

- **Source:** diagnose-out backlog SC-001
- **Blast-radius:** `pyproject.toml`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### declare-tomllib-dependency

- **Source:** diagnose-out backlog SC-002
- **Blast-radius:** `pyproject.toml`, `tools/validate_slice_layers.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW
