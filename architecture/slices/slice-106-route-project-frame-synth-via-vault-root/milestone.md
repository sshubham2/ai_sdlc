---
slice: slice-106-route-project-frame-synth-via-vault-root
stage: build
updated: 2026-06-03
next-action: run /validate-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-106 route-project-frame-synth-via-vault-root

**Stage**: build
**Next action**: run `/validate-slice`
**Updated**: 2026-06-03
**Risk tier**: medium — Critic required: yes (touches `tools/*.py` — in-house methodology surface, mandatory-Critic trigger regardless of tier)

## Progress

- [x] /slice — 2026-06-03
- [x] /design-slice — 2026-06-03
- [x] /critique — 2026-06-03 — NEEDS-FIXES (1B/2M/2m; dual-review ACCEPT; triaged by user)
- [x] /build-slice — 2026-06-03 — SHIPPED (6 tasks; full suite 1529/0; all Step 6 gates green)
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Critique + dual-review (DR-1) complete; TRI-1 ratified by user → **NEEDS-FIXES**. The first Critic caught a verified build-breaker (**B1**: routing must-rewrite→0 reds `test_emits_classified_inventory_with_evidence`); meta-Critic returned **ACCEPT** (all 5 findings VALID, no over-reach, no misses). 2 ACCEPTED-PENDING fixes for /build-slice (B1 synthetic-fixture rework + M2 stale-narrative repointing); 3 ACCEPTED-FIXED already in design/mission-brief (M1 AC reword, m1 number-distinction, m2 MEPD-1 note).

**Build plan — four-file coupled chain** (+ shippability): (1) `project_frame_synth.py` route 4 sites + L44 docstring; (2) `vault_flip_readiness_audit.py` `_BASELINE→()` + comment; (3) `test_vault_flip_readiness_audit.py` B1 synthetic-fixture rework + comment; (4) `test_vault_root_constant.py` allowlist 15→16 + "14"→16 prose, **don't** touch `==15` test-count pin; (5) `shippability.md` repoint 2 stale row narratives. **Mid-slice smoke tripwire**: `vault_flip_readiness_audit` → `[production] 0 must-rewrite` AND `project_frame_synth` output byte-identical.

This is the **M1 production cut** of the external-shared-vault flip roadmap (production surface 4 → 0). Parallel sibling slice-107 `inventory-vault-flip-prose-surface` (registered in `slice-queue.md`, picked in a separate session) — disjoint blast radius.

## On resume

- **Last completed action**: /build-slice — SHIPPED (4-file coupled chain + 1 build-discovered count-pin consumer; full suite 1529/0; all Step 6 gates green; BC-1 acks BC-PROJ-3/7 + BC-GLOBAL-2)
- **Current work**: none — code + vault changes committed on `slice/106-…` (wip build commit)
- **Next immediate step**: run `/validate-slice` (per-AC reality check: 0 production must-rewrite + byte-identical frame + suite green)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — written (no ADRs)
- [critique.md](critique.md) — written (NEEDS-FIXES; user-triaged)
- [critique-review.md](critique-review.md) — written (dual-review ACCEPT)
- [build-log.md](build-log.md) — written (SHIPPED; 6 tasks; all Step 6 gates green)
- [validation.md](validation.md) — pending
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
