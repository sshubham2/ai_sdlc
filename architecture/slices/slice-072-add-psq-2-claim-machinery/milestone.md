---
slice: slice-072-add-psq-2-claim-machinery
stage: build
updated: 2026-05-27
next-action: Phase D — wire claim-aware behavior into PSQ-1 writer
risk-tier: medium
critic-required: true
---

# Milestone: slice-072 add-psq-2-claim-machinery

**Stage**: build
**Next action**: Phase D — wire claim-aware behavior into PSQ-1 writer (`tools/slice_queue_writer.py::_format_entry` + `write_slice_queue` merge)
**Updated**: 2026-05-27
**Risk tier**: medium — Critic required: yes (in-house methodology surfaces touched: `tools/slice_queue_writer.py`, new `tools/slice_queue_claim.py`, `skills/slice/SKILL.md` Step 6.5, methodology-changelog, ADR-067; multi-session shared state contract)

## Progress

- [x] /slice — 2026-05-27
- [x] /design-slice — 2026-05-27
- [x] /critique — 2026-05-27 — CLEAN
- [x] /critique-review — 2026-05-27 — EXTEND
- [ ] /build-slice — in progress: Phase A+B+C complete; D/E/F/G pending
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Phases A+B+C complete. `tools/slice_queue_claim.py` written (~430 LOC: ClaimUsageError + read_git_config_user with 3-case exit-code-based absence detection + parse_queue_text with CRLF-tolerant + _extra_field_lines forward-compat pass-through + apply_claim/apply_release/_rewrite_entry_lines + atomic _atomic_write_text with newline="" + argparse mutually-exclusive CLI). BC-PROJ-9 5-inventory fan-out applied: plugin.yaml tools block (PSQ-2), install_audit._CANONICAL_TOOLS, INSTALL.md L22+L166 (29→30). 17 unit tests in test_psq_2_claim_machinery.py (16 PASS / 1 WRITTEN-FAILING pending Phase D). Bespoke cp1252 test added per Critic B1. 2 paired-pin tests for v0.71.0 in test_methodology_changelog.py (WRITTEN-FAILING pending Phase F). 18 TF-1 rows total. Phase D next: modify tools/slice_queue_writer.py::_format_entry to insert claim lines at [-2] (per Critic m1) + write_slice_queue to merge existing claims via parse_queue_text (per AC4) + explicit newline="" on .tmp write (per Critic M1).

## On resume

- **Last completed action**: Phase B/C — wrote test_psq_2_claim_machinery.py (17 tests; 16 PASS; 1 WRITTEN-FAILING dependent on Phase D), added bespoke cp1252 test in test_utf8_stdout_regression.py, added 2 paired-pin tests in test_methodology_changelog.py for v0.71.0
- **Current work**: ready to start Phase D (PSQ-1 writer modification)
- **Next immediate step**: edit `tools/slice_queue_writer.py::_format_entry` (claim-line insertion at index [-2] preserving trailing blank) + `write_slice_queue` (claim-preservation merge via `tools.slice_queue_claim.parse_queue_text` + explicit `newline=""` at `.tmp` write); then re-run pytest to confirm AC4 test passes
- **Worktree**: `C:\Users\sshub\ai_sdlc-wt\slice-072-add-psq-2-claim-machinery` on `slice/072-add-psq-2-claim-machinery` (pre-build commit `19eb357`)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — CLEAN (11 first-Critic findings: 2B + 4M + 5m all ACCEPTED-FIXED; user-ratified at TRI-1)
- [critique-review.md](critique-review.md) — EXTEND (0 suspicious + 3 missed: 1 Major M-add-1 TPHD-1 N=6 + 2 minors all ACCEPTED-FIXED)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## New ADRs

- [ADR-067 — Mint PSQ-2 claim machinery](../../decisions/ADR-067-mint-psq-2-claim-machinery.md) — reversibility: cheap
