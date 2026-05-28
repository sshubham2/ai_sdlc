# Slice queue

_Generated: 2026-05-28T05:23:56+00:00 by /slice during slice-075 definition_

## Candidates

### bundle-074-code-critic-cleanup

- **Source:** enable-parallel-slice-pending-items.txt P1.1 + slice-074 code-Critic m1-m5 deferrals + P3.10 cp1252 mojibake fix (severely overdue voluntary-restraint bundle N=15 cumulative)
- **Blast-radius:** `skills/build-slice/SKILL.md`, `tests/methodology/test_slice_queue_writer.py`, `tools/slice_queue_writer.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### critic-calibrate-five-simultaneous-signals

- **Source:** slice-074 reflection — /critic-calibrate SEVERELY OVERDUE at 5 signals (TPHD-1 N=7 + BC-GLOBAL-2 N=6 + AC-count>5 N=3 + MEPD-1-EXCLUDE-vs-shippability-row N=1 + scope-expansion-at-plan-mode N=1)
- **Blast-radius:** `agents/critique.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### retrofit-soad-1-in-commit-slice-yes-no-prompts

- **Source:** enable-parallel-slice-pending-items.txt P2.2 (6 raw yes/no prompts at skills/commit-slice/SKILL.md L173/L175/L202/L203/L205/L255 — SOAD-1 retrofit)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_soad_1.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### extend-tffl-1-to-ws-1-and-etc-1-audits

- **Source:** enable-parallel-slice-pending-items.txt P3.7 (silent-default-off class extends to WS-1 + ETC-1 audits — apply slice-034 TFFL-1 pattern verbatim)
- **Blast-radius:** `tools/exploratory_charter_audit.py`, `tools/walking_skeleton_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### extend-osdg-1-to-slice-candidates

- **Source:** risk-register R-13 (OSDG-1 drift guard not yet extended to /slice-candidates skill)
- **Blast-radius:** `skills/slice-candidates/SKILL.md`, `tests/methodology/test_slice_candidates_skill_drift.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### parallel-slice-family-parity-audit

- **Source:** enable-parallel-slice-pending-items.txt P3.6 (BRANCH-2 + PSQ-1 + PSQ-2 + PSQ-3 cross-spec parity audit — same default-resolution helper + canonical worktree path + SOAD-1 form + WORKTREE=skip grammar across 4 SKILL.md surfaces)
- **Blast-radius:** `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `tools/parallel_slice_family_parity_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### close-psq-3-conflict-stop-re-entry-semantics

- **Source:** enable-parallel-slice-pending-items.txt P2.3 (PSQ-3 conflict-STOP at sub-step 2.5 re-entry semantics undefined — design.md tracks but doesn't pin; slice-074's PSQ-3 was fast-forward no-op so re-entry NOT exercised)
- **Blast-radius:** `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### r-2-programmatic-test-for-diagnose-cwd-mismatch-warning

- **Source:** risk-register R-2 (no programmatic test ensures /diagnose emits cwd-mismatch warning at runtime; open low-band since slice-002)
- **Blast-radius:** `skills/diagnose/SKILL.md`, `tests/skills/diagnose/test_cwd_mismatch_warning.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### implement-or-downgrade-drift-check

- **Source:** diagnose-out/backlog.md SC-006 + SC-007 + SC-008 (documented-but-unenforced-gate cluster; HIGH severity per BCR-1 round-trip)
- **Blast-radius:** `skills/drift-check/SKILL.md`, `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### worktree-cleanup-audit

- **Source:** enable-parallel-slice-pending-items.txt P3.9 (worktree disk-space accumulation on aborted slices; theoretical risk — empirical N=0)
- **Blast-radius:** `tools/worktree_cleanup_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW
