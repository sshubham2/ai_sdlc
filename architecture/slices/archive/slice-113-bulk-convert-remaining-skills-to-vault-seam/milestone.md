---
slice: slice-113-bulk-convert-remaining-skills-to-vault-seam
stage: complete
updated: 2026-06-04
next-action: none (slice complete)
risk-tier: medium
critic-required: true
---

# Milestone: slice-113 bulk-convert-remaining-skills-to-vault-seam

**Stage**: complete
**Next action**: none (slice complete — run `/commit-slice` to generate the audit-grade commit)
**Updated**: 2026-06-04
**Risk tier**: medium — Critic required: yes (methodology surfaces `skills/*/SKILL.md` + `tools/*.py`)

## Progress

- [x] /slice — 2026-06-04
- [x] /design-slice — 2026-06-04
- [x] /critique — 2026-06-04 — NEEDS-FIXES (dual-review EXTEND; all ACCEPTED)
- [x] /build-slice — 2026-06-04 — SHIPPED
- [x] /code-review — 2026-06-04 — B1 + m1 ACCEPTED-FIXED
- [x] /validate-slice — 2026-06-04 — PASS (5/5 ACs, VAL-1 clean, shippability 118/118)
- [x] /reflect — 2026-06-04

## Current focus

Slice shipped. Lessons captured. Auto-archived.

## On resume

- **Last completed action**: /reflect (reflection.md written; vault updated; slice auto-archived)
- **Current work**: none — slice complete
- **Next immediate step**: run `/commit-slice` (user-invoked) to generate the audit-grade commit + `--merge` back to master

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — SHIPPED
- [code-review.md](code-review.md) — FINDINGS (B1+m1 fixed)
- [validation.md](validation.md) — PASS
- [reflection.md](reflection.md) — YES-WITH-DEFERRALS

## Decisions (ADRs)

- [ADR-106](../../../decisions/ADR-106-op-gate-seam-aware-sink-detection.md) — op-gate sink-detector seam-aware (matcher + extractor); reversibility: cheap.

## Final counts

- Converted: 171 skill-prose refs → `<vault>/`; carve-outs: 116. `EXPECTED_TOTAL`=132, rewrite-at-flip floor=130, doc-example=2. Op-gate `{6,11,23,0}` stable. `_CONVERTED_FILES`=24 (code-review un-ratcheted), `_CONVERTED_CARVEOUTS`=43.
