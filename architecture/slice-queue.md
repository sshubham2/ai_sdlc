# Slice queue

_Generated: 2026-05-27T19:53:31+00:00 by /slice during slice-074 definition_

## Candidates

### critic-calibrate-tphd-bc-global-ac-count

- **Source:** slice-073 reflection L30 (TPHD-1 N=7 + BC-GLOBAL-2 N=5 + AC-count>5 N=2; /critic-calibrate severely overdue)
- **Blast-radius:** `agents/critique.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### bundle-073-code-critic-cleanup

- **Source:** slice-073 reflection L37 (voluntary-restraint N=14; 4 code-Critic advisories M1+m1+m2+m3 from slice-073)
- **Blast-radius:** `architecture/shippability.md`, `skills/commit-slice/SKILL.md`, `tests/methodology/test_commit_slice_skill_rebase_flag.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### extend-tffl-1-to-ws-1-and-etc-1-audits

- **Source:** slice-066 reflection (R-7 silent-default-off class extends to WS-1 + ETC-1 audits; apply slice-034 TFFL-1 pattern verbatim)
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

### implement-or-downgrade-drift-check

- **Source:** diagnose-out/backlog.md SC-006 + SC-007 + SC-008 (documented-but-unenforced-gate cluster; HIGH severity)
- **Blast-radius:** `skills/drift-check/SKILL.md`, `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** HIGH

### retrofit-soad-1-in-commit-slice-yes-no-prompts

- **Source:** slice-073 reflection L41 (6 raw (yes/no) prompts in /commit-slice at SKILL.md L173/L175/L202/L203/L205/L255 â€” retrofit to SOAD-1 structured-options form)
- **Blast-radius:** `skills/commit-slice/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### close-merge-substep-3-worktree-collision-stop-asymmetry

- **Source:** slice-073 design.md Â§'Worktree-vs-main-tree interaction contract' (--merge Step 5b sub-step 3 missing the worktree-vs-main-tree collision STOP that sub-step 2.5 added)
- **Blast-radius:** `skills/commit-slice/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### r-2-programmatic-test-for-diagnose-cwd-mismatch-warning

- **Source:** risk-register R-2 (no programmatic test ensures /diagnose emits cwd-mismatch warning at runtime; open low-band since slice-002)
- **Blast-radius:** `skills/diagnose/SKILL.md`, `tests/skills/diagnose/test_cwd_mismatch_warning.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW
