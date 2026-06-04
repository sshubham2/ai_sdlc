# Slice queue

_Generated: 2026-06-04T18:19:34+00:00 by /slice during slice-114 definition_

## Candidates

### convert-agent-prose-to-vault-seam

- **Source:** reflection slice-113 Deferred (M1/TRI-1-ratified) + risk-register R-32
- **Blast-radius:** `agents/code-review.md`, `agents/critic-calibrate.md`, `agents/critique-review.md`, `agents/diagnose-narrator.md`, `architecture/risk-register.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** R-32 (agent-prose residual)

### flip-vault-to-external-store

- **Source:** risk-register R-32 (physical move â€” sole remaining pre-move residual after slice-114)
- **Blast-radius:** `CLAUDE.md`, `architecture/risk-register.md`, `tools/project_frame_synth.py`, `tools/vault_flip_prose_inventory.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** LARGE
- **Risk-retired:** R-32 (retires at the move)

### apply-critic-calibrate-proposals

- **Source:** action-points AP-21 (critic-calibrate overdue, N>=3 calibration signals)
- **Blast-radius:** `agents/critique-review.md`, `agents/critique.md`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** none (Critic blind-spot reduction)

### harden-parallel-version-bump-audit-fragility

- **Source:** risk-register R-28 (open, low-band)
- **Blast-radius:** `tools/critique_agent_drift_audit.py`, `tools/install_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** R-28 (low)

### close-version-keyed-install-completeness-gap

- **Source:** risk-register R-29 (open, low-band)
- **Blast-radius:** `tools/install_audit.py`, `tools/plugin_manifest_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** R-29 (low)

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
- slice-110-make-pipeline-vault-location-agnostic — picked 2026-06-04T02:22:15+00:00 by Shubhendu Shubham s2.shubh2@gmail.com (re-scoped in place from flip-vault-to-external-store at TRI-1; flip deferred to a follow-on slice)
- slice-111-route-in-loop-skill-vault-ops-via-seam — picked 2026-06-04T09:22:48+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-112-make-prose-vault-location-agnostic — picked 2026-06-04T12:16:09+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-113-bulk-convert-remaining-skills-to-vault-seam — picked 2026-06-04T15:36:06+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
- slice-114-convert-agent-prose-to-vault-seam — picked 2026-06-04T18:19:45+00:00 by Shubhendu Shubham s2.shubh2@gmail.com
