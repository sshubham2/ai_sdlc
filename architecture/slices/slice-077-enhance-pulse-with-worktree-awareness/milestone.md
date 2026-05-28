---
slice: slice-077-enhance-pulse-with-worktree-awareness
stage: critique
updated: 2026-05-28
next-action: run /build-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-077 enhance-pulse-with-worktree-awareness

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-28
**Risk tier**: medium — Critic required: **yes** (touches in-house methodology surface `skills/pulse/SKILL.md` + ships new helper `tools/pulse_worktree_resolver.py`; mandatory-Critic trigger fires regardless of tier)

## Progress

- [x] /slice — 2026-05-28
- [x] /design-slice — 2026-05-28
- [x] /critique — 2026-05-28 — CLEAN (19 first-Critic findings: 4B/9M/6m, all VALIDATED at TRI-1; 17 ACCEPTED-FIXED + 2 DEFERRED)
- [x] /critique-review — 2026-05-28 — EXTEND (3 missed findings M-add-1/M-add-2/M-add-3, all ACCEPTED-FIXED in-band)
- [ ] /build-slice
- [ ] /code-review (CRSI-1 v1 walking-skeleton; advisory-only post-build)
- [ ] /validate-slice
- [ ] /reflect

## Current focus

3-Critic stack pass complete (design-Critic + meta-Critic). 22 findings dispositioned (19 first-Critic + 3 meta-Critic missed); 20 ACCEPTED-FIXED applied in-band + 2 DEFERRED (m2 _index.md staleness; m4 parser extraction → parity-audit slice). User ratified en bloc at TRI-1. Final verdict: **CLEAN**. Ready for build.

**R-22 registered** at /design per /critique-review M-add-2 ACCEPTED-FIXED (RR-1 conformance — mission-brief L5 "Risk retired: R-22"; mirrors slice-076 R-21 precedent). Status: open; retires at slice-077 /reflect.

**MEPD-1 path**: EXCLUDE confirmed per ADR-070 § Honest precedent inspection (load-bearing cross-skill criterion; slice-058 closer precedent than slice-074/075 — those shipped zero helper modules; slice-076 is the structural twin but INCLUDE-shaped because PCR-1 IS cross-skill load-bearing). Ships at v0.73.0 unchanged.

**Key design decisions** (post-TRI-1):
1. 4-state worktree taxonomy with fail-closed UNKNOWN; all 4 surfaced (UNKNOWN as one-line WARN-not-silent with 8 enumerated sub-reasons per M3 ACCEPTED-FIXED)
2. Override-precedence: full 4×CAL-1 table; Step-2 deterministic resolver feeds Step-3 Haiku-render (per M4 ACCEPTED-FIXED)
3. Drift-flag suppression: 3-surface all-match + content-equal-modulo-EOL per ADR-033 / EOL-DRIFT-1 (per B3 ACCEPTED-FIXED)
4. Cross-spec parity with `tools/parallel_conflict_resolver.py` (PCR-1) pinned in design.md § Cross-spec parity (per M7 + M-add-1 ACCEPTED-FIXED)
5. RSAD-1 design-time pre-empt: prose-pin discipline table with per-literal anchoring (per M9 ACCEPTED-FIXED; addresses slice-075 N=3 recurrence pattern)
6. APED-1 battery raised from ≥6 to ≥13 enumerated cases (per M8 ACCEPTED-FIXED; slice-076's 28-case precedent)

New artifacts: `tools/pulse_worktree_resolver.py` + 6 test modules + ADR-070 + shippability row #77 + R-22 in risk-register.md.

Closes the post-slice-076 /pulse skill-correctness gap witnessed firsthand this session: `/pulse` reads only the main-tree `architecture/slices/<active>/milestone.md`, so when a BRANCH-2 worktree holds a built / validated / reflected / auto-archived slice while master is still on the scaffold commit, `/pulse` mis-reports stage + recommends the wrong next action AND raises a false-positive "vault forward-population" drift flag for the same root cause (installed methodology-changelog forward-synced from worktree vs master's stale changelog). After this slice ships: `/pulse` runs during a BRANCH-2 worktree window correctly classify worktree-state (`in-progress` / `built-but-not-merged` / `merged` / fail-closed `UNKNOWN`), override the recommended-next-action when `built-but-not-merged`, and suppress the false-positive drift flag.

Ships:
1. `/pulse` SKILL.md Step 1 worktree-detection augmentation (`git worktree list --porcelain` parsing as pre-read step)
2. 4-state worktree-state classification (`IN_PROGRESS` / `BUILT_BUT_NOT_MERGED` / `MERGED` / `UNKNOWN`)
3. Recommended-next-action override (precedes over CAL-1 cadence-overdue when `BUILT_BUT_NOT_MERGED` observed)
4. Drift-flag false-positive suppression (installed-matches-worktree case during `BUILT_BUT_NOT_MERGED` window)
5. NEW helper `tools/pulse_worktree_resolver.py` with library API + CLI

## Re-scoping note

Slice-076 reflection nominated slice-077 for PCR-2 (VAULT_CLAIM + HARD-conflict full Critic stack + TRI-RESOLVE-1 + MIXED partial-resolution). User explicitly chose `enhance-pulse-with-worktree-awareness` for slice-077 because the gap was witnessed firsthand during the slice-076 merge sequence (post-merge `/pulse` run showed wrong stage + false-positive drift flag) AND the fix is bounded SMALL effort. PCR-2 is now slice-078 at the head of `architecture/slice-queue.md`.

## On resume

- **Last completed action**: /critique-review (3 missed findings ACCEPTED-FIXED in-band; user ratified all 22 dispositions en bloc at TRI-1; verdict CLEAN)
- **Current work**: none
- **Next immediate step**: run `/build-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-070](../../decisions/ADR-070-worktree-awareness-in-pulse.md)
- [critique.md](critique.md) — CLEAN (4B/9M/6m all dispositioned)
- [critique-review.md](critique-review.md) — EXTEND (3 missed findings M-add-1/M-add-2/M-add-3 all ACCEPTED-FIXED)
- R-22 in [risk-register.md](../../risk-register.md) — open (retires at /reflect)
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending (CRSI-1 v1 advisory)
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
