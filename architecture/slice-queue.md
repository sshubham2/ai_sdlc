# Slice queue

_Generated: 2026-06-03T09:37:29+00:00 by /slice during slice-107 definition_

## Candidates

### add-diagnose-cwd-warning-test

- **Source:** risk-register R-2
- **Blast-radius:** `skills/diagnose/SKILL.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### harden-forward-sync-parallel-contention

- **Source:** risk-register R-28
- **Blast-radius:** `tools/critique_agent_drift_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### fix-version-keyed-install-blindspot

- **Source:** risk-register R-29
- **Blast-radius:** `tools/install_audit.py`, `tools/plugin_manifest_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
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

## ADR number reservations (cross-session coordination)

Parallel slices author ADRs in their own worktrees and cannot see each other's uncommitted ADR numbers. To avoid max+1 collisions, reservations are recorded here (slice-107 dual-review M3 / ADR-079 stranded-slice-coordination spirit):

- **ADR-096, ADR-097** — reserved for **slice-107-inventory-vault-flip-prose-surface** (authored in its worktree, not yet merged). The parallel **slice-106** session MUST mint **ADR-098+** when it runs `/design-slice` (master tops at ADR-095; both M1 siblings reach for 096+ otherwise).
