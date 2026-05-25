---
slice: slice-054-fix-pyproject-toml-version-drift
stage: complete
updated: 2026-05-21
next-action: none (slice complete) — run /commit-slice (user-invoked) to generate the audit-grade commit
risk-tier: low
critic-required: true
---

# Milestone: slice-054 fix-pyproject-toml-version-drift

**Stage**: complete (SHIPPED; BCR-1 round-trip dogfooded; archiving next)
**Next action**: run `/commit-slice` (user-invoked by contract — never auto-advances)
**Updated**: 2026-05-21
**Risk tier**: low — Critic required: **yes** (methodology-surface rule-minting slice; Route B classification minted PVFS-1)

## Progress

- [x] /repro — 2026-05-21 (BFRD-1 reproduction; test FAILS with `'0.20.0' == '0.61.0'`; shippability row #54 added)
- [x] /slice — 2026-05-21
- [x] /design-slice — 2026-05-21 (Route B chosen: mint PVFS-1 + ADR-056 + methodology-changelog v0.62.0 + 4-part PMI-1 atomic bump)
- [x] /critique — 2026-05-21 — NEEDS-FIXES (0B / 4M / 2m; all 4 Majors ACCEPTED-FIXED in-round; 1 Minor ACCEPTED-FIXED, 1 Minor DEFERRED to `/critic-calibrate`)
- [x] /critique-review — 2026-05-21 — EXTEND (6/6 first-Critic findings VALID + 0 suspicious + 0 severity adjustments; +1 Major missed M-add-1 ACCEPTED-FIXED + 1 Minor missed m-add-1 ACCEPTED-FIXED + 1 self-withdrawn m-add-2 transparently recorded)
- [x] TRI-1 user-owned triage — 2026-05-21 — CLEAN (user ratified all 8 dispositions: 7 ACCEPTED-FIXED + 1 DEFERRED; triage_audit clean)
- [x] /build-slice — 2026-05-21 — SHIPPED (19/19 tasks; all 22 pre-finish audits PASS; 820/820 pytest; shippability 54/54; BC-1 0 violations)
- [x] /validate-slice — 2026-05-21 — PASS (4/4 ACs PASS with real-environment evidence; VAL-1 clean; SCMD-1+PTFCD-1 pre-gates clean; SRSC-1 runner 54/54 PASS 0 FAIL; AC4 input-contract verified — output-axis verifies at /reflect)
- [x] /reflect — 2026-05-21 — SHIPPED (BCR-1 first end-to-end round-trip dogfood SUCCESS; AC4 output-axis PASS at BCR-1-mandated position; MCFS-1 + AVFS-1 forward-syncs PASS; lessons appended; no BC-1 promotion — N=1 patterns; reflection.md written)

## Current focus

First-Critic returned NEEDS-FIXES with 4 Majors (M1-M4) + 2 Minors. All 4 Majors **ACCEPTED-FIXED in this round** (design.md + mission-brief.md edited):

- **M1** (AC3 pin test "TBD" gap): minted `test_pyproject_has_no_stale_v_0_20_0_or_count_literals` co-located in existing `test_pyproject_version_matches_version_file.py`; TPHD-1 sub-mode (a) harmonized mission-brief TF-1 row 3.
- **M2** (3-of-3 stale literal sites): design.md "What's new" enumerates lines 3 + 6 + 66 with per-site refactor targets.
- **M3** (FBCD-1 cross-file smoke-gate literal inconsistency): mission-brief.md smoke-gate updated to `'0.62.0' == '0.62.0'` + cross-link.
- **M4** (AC4 position-semantic gap on BCR-1 first dogfood): mission-brief.md AC4 verification-plan tightened to position-pinned awk + line-number check.
- **m1** (stale `VERSION = 0.59.0` heading): DEFERRED — BCR-1 append-only correct; `/critic-calibrate` candidate.
- **m2** (Components-touched parenthetical hedge): ACCEPTED-FIXED — rewritten as clean bullet list inventory.

Next: `/critique-review` runs the meta-Critic pass to surface false positives + missed findings; then TRI-1 user-owned triage (HALT) ratifies/replaces the Builder draft dispositions; then `/build-slice`.

## On resume

- **Last completed action**: /critique (NEEDS-FIXES; Builder drafts written; ACCEPTED-FIXED edits applied in-round)
- **Current work**: none
- **Next immediate step**: run `/critique-review` (per Standard-mode methodology-surface dual-Critic policy)

## Phase artifacts

- [mission-brief.md](mission-brief.md) — updated in-round (M1 TF-1 row 3, M3 smoke-gate, M4 AC4 verification)
- [design.md](design.md) — updated in-round (M1 AC3 pin test mint, M2 3-site enumeration, m2 Components-touched rewrite)
- [critique.md](critique.md) — NEEDS-FIXES (0B / 4M / 2m; all Builder drafts written; Triage table pending TRI-1)
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## ADRs introduced this slice

- [ADR-056](../../decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md) — Mint PVFS-1 (Pyproject Version Forward Sync); cheap reversibility; new rule, supersedes nothing

## Discovered (pending /reflect Step 5)

- **`/critic-calibrate` candidate (per /critique m1, DEFERRED)**: should BCR-1 round-trip soft-warn on stale literals in closed-candidate headings? Current behavior is correctly append-only per slice-053 ADR-055 — a heading carrying `VERSION = 0.59.0` while current VERSION is 0.62.0 stays unrewritten. Worth a methodology-refinement discussion at the next `/critic-calibrate` pass.
