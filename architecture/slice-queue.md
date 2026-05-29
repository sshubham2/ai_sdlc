# Slice queue

_Generated: 2026-05-29T17:20:55+00:00 by /slice during slice-083 definition_

## Candidates

### add-pcr-2b-hard-class-conflict-resolution

- **Source:** slice-queue top / deferred ADR-069 ADR-071 PCR-2 HARD-class path
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** NONE

### add-claim-sequence-number-for-clock-skew-detection

- **Source:** risk-register R-23
- **Blast-radius:** `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### harden-pcr-2a-clock-skew-winner

- **Source:** risk-register R-23
- **Blast-radius:** `tools/parallel_conflict_resolver.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

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

### add-psq-4-push-time-rebase

- **Source:** deferred ADR-068 Options-#2
- **Blast-radius:** `skills/commit-slice/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** NONE

### add-index-md-soft-promotion-or-light-hard-path

- **Source:** deferred ADR-075 Consequences (slice-083 /critique M4) — `_index.md`-sole HARD conflict is high-frequency; two-pass Critic cost is heavy for the dominant case
- **Blast-radius:** `tools/parallel_conflict_resolver.py`, `skills/commit-slice/SKILL.md`, `skills/archive/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** NONE
