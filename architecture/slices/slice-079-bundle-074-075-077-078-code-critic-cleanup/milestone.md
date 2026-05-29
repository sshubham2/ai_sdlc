---
slice: slice-079-bundle-074-075-077-078-code-critic-cleanup
stage: build
updated: 2026-05-29
next-action: Phase B — regression test scaffolding (write FAILING tests for fixes A-S)
risk-tier: medium
critic-required: true
---

# Milestone: slice-079 bundle-074-075-077-078-code-critic-cleanup

**Stage**: build (Phase A complete; Phase B pending)
**Next action**: Phase B — regression test scaffolding (write FAILING tests for fixes A-S; verify all FAIL pre-fix)
**Updated**: 2026-05-29
**Risk tier**: medium — Critic required: yes
**Worktree**: `C:\Users\sshub\ai_sdlc-wt\slice-079-bundle-074-075-077-078-code-critic-cleanup` on branch `slice/079-bundle-074-075-077-078-code-critic-cleanup`

## Progress

- [x] /slice — 2026-05-29
- [x] /critic-calibrate — 2026-05-29 (Proposal 1 ACCEPTED+applied: APED-1 self-application clause-5)
- [x] /design-slice — 2026-05-29 (19 in-scope fixes A-S; 6 DEFER-with-rationale; 0 ADRs)
- [x] /critique — 2026-05-29 NEEDS-FIXES (first-Critic 2B+3M+6m all VALID; APED-1 clause-5 first-governed-slice empirically effective)
- [x] /critique-review — 2026-05-29 EXTEND (+1 MISSED Minor M-add-1 signature-citation drift)
- [x] TRI-1 — 2026-05-29 (user accept-all 12 dispositions; final verdict NEEDS-FIXES)
- [ ] /build-slice — in progress: Phase A of I complete (1/9 phases ≈ 11%)
  - [x] Phase A — Setup + m6 discharge (shippability rows 79-84 enumerated; milestone + build-log scaffolded)
  - [ ] Phase B — Regression test scaffolding (write FAILING for fixes A-S)
  - [ ] Phase C — `skills/build-slice/SKILL.md` fixes A-F + OSDG-1 forward-sync
  - [ ] Phase D — `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` Fix G
  - [ ] **MID-SLICE SMOKE GATE** (after Phase D ~50%)
  - [ ] Phase E — `tools/pulse_worktree_resolver.py` fixes K-N
  - [ ] Phase F — pulse tests cleanup (fixes H, I, J)
  - [ ] Phase G — `tools/parallel_conflict_resolver.py` fixes O-R
  - [ ] Phase H — `tools/slice_queue_writer.py` Fix S structural-pin
  - [ ] Phase I — Pre-finish gate (Step 6 audits + full pytest + build-log Summary)
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Phase A complete. m6 ACCEPTED-PENDING discharge done — 6 shippability catalog rows enumerated (rows 79-84) covering:
- Row 79: build-slice SKILL.md prose-fix cluster (A+B+C+D+E+F)
- Row 80: commit-slice test-pin fix (G)
- Row 81: pulse_worktree_resolver fix cluster (K+L+M+N)
- Row 82: pulse tests cleanup (H+I+J)
- Row 83: parallel_conflict_resolver PCR-2a fix cluster (O+P+Q+R, signature corrected per M-add-1)
- Row 84: slice_queue_writer UTF-8 structural-pin (S)

SCPD-1 propagation verified in same Phase block: rows added before fix execution (proactive-application sub-mode); each row cites the specific test paths that will be created in Phases B-H. Catalog grammar SCMD-1 + SRSC-1 compliant.

Phase B next: scaffold the regression test files cited in the catalog rows (write FAILING; verify FAIL pre-fix → PASS post-fix contrast empirically established before Phase C edits begin).

## On resume

- **Last completed action**: Phase A — shippability rows 79-84 enumerated + scaffold commit pending
- **Current work**: Phase A scaffold commit (m6 + milestone + build-log)
- **Next immediate step**: Phase B regression test scaffolding — create the new test files cited in shippability rows 79-84 (write FAILING):
  - `tests/methodology/test_build_slice_skill_branch_state_preamble.py` (Fix A)
  - `tests/methodology/test_skill_parse_helpers.py` (Fix E)
  - `tests/skills/pulse/test_unknown_warn_templates.py` (Fix K)
  - `tests/skills/pulse/test_detect_active_worktrees_bare_repo.py` (Fix L)
  - `tests/skills/pulse/test_parse_milestone_stage_bom_tolerance.py` (Fix M+N)
  - `tests/methodology/test_pulse_tests_have_no_unused_imports.py` (Fix I+J)
  - `tests/methodology/test_pcr_2a_audit_formatter_signature.py` (Fix O)
  - `tests/methodology/test_pcr_2a_parse_queue_missing_field_sentinel.py` (Fix P)
  - `tests/methodology/test_pcr_2a_step_5_atomicity_docstring.py` (Fix Q)
  - `tests/methodology/test_pcr_2a_vault_claim_dispatch_comment.py` (Fix R)
  - `tests/methodology/test_slice_queue_writer_utf8_encoding.py` (Fix S)
- **/pulse-resume-readiness**: milestone.md + build-log.md events capture state; PWA-1 (slice-077) worktree-aware /pulse reads worktree's milestone.md so resume from main-repo `/pulse` invocation will correctly identify slice-079 stage=build + next-action=Phase B

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES; 11 findings triaged
- [critique-review.md](critique-review.md) — EXTEND; 1 missed finding (M-add-1) surfaced + ACCEPTED-FIXED
- [build-log.md](build-log.md) — Phase A events recorded; Summary pending Phase I
- [code-review.md](code-review.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
