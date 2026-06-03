# Slice queue

_Generated: 2026-06-03T09:30:26+00:00 by /slice during slice-106 definition_

## Candidates

### inventory-vault-flip-prose-surface

- **Source:** vault-flip-readiness / ADR-091 deferred prose surface (~285 literals: SKILL.md 262, agents 16, CLAUDE.md 6, INSTALL.md)
- **Blast-radius:** `plugin.yaml`, `tools/install_audit.py`, `tools/vault_flip_prose_inventory.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### add-version-bump-obligations-checklist

- **Source:** slice-105 Discovered + Critic-calibration Pattern (version-bump mechanics blind spot, N>=11 test-rename)
- **Blast-radius:** `tools/build_checks_audit.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** MEDIUM
- **Risk-retired:** LOW

### fix-val1-layer-b-silent-disable-on-py310

- **Source:** diagnose backlog SC-002 (tomllib absent on py3.10 silently disables VAL-1 Layer B)
- **Blast-radius:** `pyproject.toml`, `tools/validate_slice_layers.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** MEDIUM

### fix-version-keyed-install-blindspot

- **Source:** risk-register R-29 (tool added without version bump invisible to TVFS-1 + INST-1)
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
