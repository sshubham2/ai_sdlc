---
slice: slice-072-add-psq-2-claim-machinery
stage: critique
updated: 2026-05-27
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-072 add-psq-2-claim-machinery

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-27
**Risk tier**: medium — Critic required: yes (in-house methodology surfaces touched: `tools/slice_queue_writer.py`, new `tools/slice_queue_claim.py`, `skills/slice/SKILL.md` Step 6.5, methodology-changelog, ADR-067; multi-session shared state contract)

## Progress

- [x] /slice — 2026-05-27
- [x] /design-slice — 2026-05-27
- [x] /critique — 2026-05-27 — CLEAN
- [x] /critique-review — 2026-05-27 — EXTEND
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Design complete; first Critic + meta-Critic both reviewed; Builder fix-block applied 11+3=14 ACCEPTED-FIXED edits in-band. PSQ-2 schema: 2 optional field lines per entry (`Claimed-by:` + `Claimed-at:`) + forward-compat `_extra_field_lines` pass-through after `Risk-retired:`; new `tools/slice_queue_claim` CLI (claim / release / force-claim / --queue); `tools/slice_queue_writer.write_slice_queue` modified to merge existing claims + forward-compat lines on regen with `newline=""` LF-only atomic write. New ADR-067 mints PSQ-2 (cheap reversibility; supersedes nothing; sibling to PSQ-1 on parallel-slice family axis; §Lineage divergence note disambiguates ADR-064 L37 + R-19 stale session-id forward-references). **6 ACs** (AC5 R-19 retirement / AC6 v-section meta + paired-pin tests + PMI-1 atomic bump) per slice-067 N=1 → slice-072 N=2 documented AC-count-rule deviation per Critic M4 ACCEPTED-FIXED. 18 TF-1 rows. Ready for TRI-1 user-owned triage.

## On resume

- **Last completed action**: /critique-review + TRI-1 ratification (CLEAN; 14/14 ACCEPTED-FIXED — 11 first-Critic + 3 meta-Critic missed; all fixes landed in-band on mission-brief/design/ADR-067/milestone)
- **Current work**: none
- **Next immediate step**: run `/build-slice`

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
