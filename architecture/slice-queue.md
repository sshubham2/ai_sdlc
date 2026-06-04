# Slice queue

_Generated: 2026-06-04T02:22:00+00:00 by /slice during slice-110 definition_

## Candidates

### rewrite-vault-prose-references-for-flip

- **Source:** external-vault M4 / slice-107 prose inventory (318 sites)
- **Blast-radius:** `CLAUDE.md`, `agents/critique.md`, `skills/slice/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** MEDIUM

### implement-drift-check-enforcement

- **Source:** diagnose backlog SC-007 (HIGH — documented-but-unenforced gate)
- **Blast-radius:** `skills/drift-check/SKILL.md`, `skills/triage/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### add-count-pin-fanout-build-check

- **Source:** slice-108 reflection deferral (AP-10 recurring N=5+)
- **Blast-radius:** `agents/critique.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM

### fix-validate-layers-tomllib-fallback

- **Source:** diagnose backlog SC-002 (VAL-1 Layer B silently disabled on Py3.10)
- **Blast-radius:** `pyproject.toml`, `tools/validate_slice_layers.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### reduce-dead-code-bundle

- **Source:** diagnose backlog SC-022/024/025 (dead code + stale header)
- **Blast-radius:** `skills/diagnose/assemble.py`, `skills/diagnose/write_pass.py`, `tests/skills/diagnose/test_assemble_errors.py`, `tests/skills/diagnose/test_normalize_finding.py`, `tools/install_audit.py`, `tools/supersede_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** NONE

### refactor-triage-audit-critique-file

- **Source:** diagnose backlog SC-010 (HIGH — CC=37 on TRI-1 gate path)
- **Blast-radius:** `tools/triage_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### refactor-mock-budget-lint-linters

- **Source:** diagnose backlog SC-012 (HIGH — CC=39/36 multi-language linters)
- **Blast-radius:** `tools/mock_budget_lint.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### extract-shared-mdtable-helper

- **Source:** diagnose backlog SC-017 (6-way table-helper duplication)
- **Blast-radius:** `tools/cross_spec_parity_audit.py`, `tools/exploratory_charter_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### reconcile-repo-root-sentinel

- **Source:** diagnose backlog SC-019 (.git-OR-VERSION vs .git-only divergence)
- **Blast-radius:** `tools/branch_workflow_audit.py`, `tools/shippability_path_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### reconcile-reflect-successor-prose

- **Source:** diagnose backlog SC-018 (/reflect declares two successors)
- **Blast-radius:** `skills/reflect/SKILL.md`, `tools/pipeline_chain_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

## Pick log

- slice-100-add-vault-flip-readiness-audit — picked 2026-06-02T03:43:15+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-101-add-gate-audit-cli-exit-code-tests — picked 2026-06-02T04:14:17+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-102-vault-flip-readiness-tests — picked 2026-06-02T13:20:30+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-103-thin-vault-index-routers-and-enforce — picked 2026-06-02T17:53:56+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-104-fix-record-pick-identity-format — picked 2026-06-02T18:08:40+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-105-decouple-slice-loop-from-diagnose-out — picked 2026-06-03T06:00:57+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-106-route-project-frame-synth-via-vault-root — picked 2026-06-03T09:30:31+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-107-inventory-vault-flip-prose-surface — picked 2026-06-03T09:37:32+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-108-add-fbcd-1-cardinality-fanout-sub-mode — picked 2026-06-03T15:12:27+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-109-add-post-flip-vault-conflict-safety — picked 2026-06-03T18:16:28+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-110-flip-vault-to-external-store — picked 2026-06-04T02:22:15+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
