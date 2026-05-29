# Slice queue

_Generated: 2026-05-29T10:45:08+00:00 by /slice during slice-081 definition_

## Candidates

### fix-drift-check-enforcement-gap

- **Source:** user-reported defect
- **Blast-radius:** `skills/build-slice/SKILL.md`, `tools/drift_check_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### harden-pcr-1-soft-regen-corner-case

- **Source:** risk-register R-21
- **Blast-radius:** `tools/parallel_conflict_resolve.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### extend-osdg-1-to-slice-candidates

- **Source:** risk-register R-13
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/methodology/skill_drift_equality.py`, `tests/skill_drift_equality.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-diagnose-cwd-mismatch-runtime-test

- **Source:** risk-register R-2
- **Blast-radius:** `skills/diagnose/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### harden-pcr-2a-clock-skew-winner

- **Source:** risk-register R-23
- **Blast-radius:** `tools/parallel_conflict_resolve.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW
