---
slice: slice-089-make-commit-slice-stale-branch-check-parallel-slice-aware
stage: critique
updated: 2026-05-31
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-31
**Risk tier**: medium — Critic required: yes (in-house methodology surface: `skills/commit-slice/SKILL.md` + new `tools/stale_branch_classifier.py`)

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-05-31
- [x] /critique — 2026-05-31 — NEEDS-FIXES (dual-review EXTEND; 4 blockers / 4 majors / 4 minors, all ACCEPTED; user-triaged)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic complete. design.md + ADR-081 updated with all ACCEPTED-FIXED edits. New read-only helper `tools/stale_branch_classifier.py` reuses the RAW `pulse_worktree_resolver._parse_worktree_porcelain` (not the name-filtered `detect_active_worktrees` — Critic B3) to classify local `slice/*` branches by worktree-backing; strips `refs/heads/`→short-form before set ops (meta-Critic B-add-1); path-equality + branch self-exclusion of the current slice; exit 0/1/2 sibling parity; bootstrap-fallback to legacy flag-all-minus-current. Both `--merge` + `--push` guardrails invoke a byte-identical block. **Build must discharge ACCEPTED-PENDING: B2 (real two-worktree fixture, mid-slice smoke) + M2 (FBCD-1 prose-parity test).**

## On resume

- **Last completed action**: /critique + /critique-review (dual-review EXTEND; TRI-1 ratified NEEDS-FIXES)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (discharge B2 fixture + M2 parity test during build)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (first Critic)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
