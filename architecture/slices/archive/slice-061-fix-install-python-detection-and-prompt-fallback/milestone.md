---
slice: slice-061-fix-install-python-detection-and-prompt-fallback
stage: complete
updated: 2026-05-23
next-action: none (slice complete; user invokes `/commit-slice` to ship)
risk-tier: high
critic-required: true
---

# Milestone: slice-061 fix-install-python-detection-and-prompt-fallback

**Stage**: complete (shipped with documented user-approved deferrals)
**Next action**: none — slice complete. Run `/commit-slice` to generate the audit-grade commit.
**Updated**: 2026-05-23
**Risk tier**: high — Critic required: yes (high tier + in-house methodology surface trigger per slice-010 MCT-1; INSTALL.md is the INST-1 install recipe)

## Progress

- [x] /repro — 2026-05-23 (BFRD-1 confirm gate auto-invoked one attempt; 3 assertions WRITTEN-FAILING; shippability row #61 added)
- [x] /slice — 2026-05-23
- [x] /design-slice — 2026-05-23 (no new ADRs; 3 design Qs answered with recommended options; R-16 born-retired + R-17 open-mitigating planned for `/build-slice` Phase A)
- [x] /critique — 2026-05-23 — NEEDS-FIXES (1 Blocker + 8 Majors + 3 Minors = 12 findings; ALL ACCEPTED-FIXED as Builder draft; design.md + mission-brief.md updated in same fix block)
- [x] /critique-review — 2026-05-23 — EXTEND (12 first-Critic findings all VALIDATED + 2 missed: M-add-1 INSTALL.md not in /code-review in-scope list, m-add-1 `$user_path`/`$AI_SDLC_DIR` binding mechanism unnamed; structural audit clean)
- [x] TRI-1 user triage — 2026-05-23 — CLEAN (14/14 ACCEPTED-FIXED; M-add-1 Option (b) ratified — INSTALL.md out-of-scope for /code-review v1; m-add-1 prose-templating-mechanism sentence applied; zero overrides, deferrals, escalations; triage_audit clean)
- [x] /build-slice — 2026-05-23 — SHIPPED-WITH-DEFERRALS (10 tasks PASS; mid-slice smoke 4/4; pre-finish gate 14 audits clean; 874 methodology+skills+agents tests pass; 1 user-approved deferral: pre-existing slice-060 R-15-class stale-archive-path defect in `tests/skills/code_review/` — slice-062 nominated)
- [x] /code-review — 2026-05-23 — AGENT-UNSPAWNABLE (session-cache miss: `code-review` subagent installed by slice-060 but not in this session's agent registry; user-ratified skip via structured-options at TRI-1-equivalent gate; structural coverage delegated to AC1-AC4 + slice-045/058 install tests + INST-1 audit per slice-061 M-add-1 Option (b) disposition; R-18 candidate documented for /reflect)
- [x] /validate-slice — 2026-05-23 — PASS (5/5 ACs PASS with evidence; VAL-1 clean; SCMD-1+PTFCD-1 pre-catalog gates clean; SRSC-1 1-user-approved-deferral on pre-existing slice-060 R-15-class row #60 — NOT a slice-061 regression; 2 reality surprises captured for /reflect: R-18 candidate + BC-PROJ-11 calibration watch-list)
- [x] /reflect — 2026-05-23 (reflection.md written; lessons-learned.md appended; R-18 added to risk-register.md as open-mitigating; 3 forward-sync gates PASS (MCFS-1/AVFS-1/TVFS-1); graphify refreshed; BC-1 promotion: NO this slice per user disposition; ready for auto-archive)
- [ ] /commit-slice (user-invoked; auto-advance terminus per PCA-1 v0.41.0)
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect
- [ ] /commit-slice (user-invoked)

## Current focus

Critique complete: NEEDS-FIXES verdict with 12 findings, ALL accepted as ACCEPTED-FIXED drafts. Major design corrections applied to design.md + mission-brief.md:

- **B1** (Blocker): `$BOOT_PYTHON` cross-bash-invocation persistence broken → switched to inline-recompute `$(command -v python3 || command -v python)`.
- **M1**: "I'll wait" branch retry bounded by option-removal on re-fire (only "provide path" + "abort" on retry).
- **M2**: abort-path partial-state wording precision (no NEW artifact this invocation; pre-existing state unchanged).
- **M3**: AC4 regression-guard section-scoped via new `_step_1_section` helper.
- **M4**: path-validation pinned to Bash-tool routing (Git-Bash on Windows) via bash fence in INSTALL.md.
- **M5**: Python-version floor read dynamically from `pyproject.toml` (slice-058 / BC-PROJ-11 lesson re-applies); INSTALL.md L71 stale `3.11+` sibling-literal dropped.
- **M6**: R-17 filing point pinned — appended to `risk-register.md` in `/build-slice` Phase A, NOT deferred to `/reflect`.
- **M7**: R-16 gains `Notes` paragraph naming broader-class coverage (conda-only / NixOS / Termux / Docker).
- **M8**: MEPD-1(b) discharge explicitly verified against META-1 assertion (vacuous-satisfaction phrasing added).
- **m1–m3**: WIRE-1 rationale canonicalized; ADR-justification strengthened; installer-suggestions de-versioned.

Ready for `/critique-review` (meta-Critic dual-review per slice-016 RPCD-1 / DR-1 discipline), then TRI-1 user triage gate.

## On resume

- **Last completed action**: /critique (NEEDS-FIXES; 12 findings all ACCEPTED-FIXED in draft; design.md + mission-brief.md updated in same fix block)
- **Current work**: none
- **Next immediate step**: run `/critique-review` (meta-Critic), then user TRI-1 ratification

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending (slice-060 added /code-review to canonical chain; v1 advisory)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## Pre-staged artifacts (authored at `/repro`)

- `tests/methodology/test_install_md_python_detection.py` — 3 assertions WRITTEN-FAILING (verified 2026-05-23):
  - `test_install_md_step_3a_does_not_hardcode_python3_venv` (AC1)
  - `test_install_md_step_2_no_python_branch_asks_user_for_interpreter` (AC2)
  - `test_install_md_step_2_conda_default_does_not_hardcode_python3_venv` (AC3)
- `architecture/shippability.md` row #61 — already cites the repro test file
