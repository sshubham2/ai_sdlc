---
slice: slice-083-add-pcr-2b-hard-class-conflict-resolution
stage: critique
updated: 2026-05-29
next-action: run /build-slice
risk-tier: high
critic-required: true
---

# Milestone: slice-083 add-pcr-2b-hard-class-conflict-resolution

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-05-29
**Risk tier**: high — Critic required: yes (mandatory triggers: in-house methodology surfaces `skills/commit-slice/SKILL.md` + `tools/parallel_conflict_resolver.py` + new ADR + `methodology-changelog.md`; judgment-heavy HARD conflict-resolution semantics)

## Progress

- [x] /slice — 2026-05-29
- [x] /design-slice — 2026-05-29
- [x] /critique — 2026-05-29 — NEEDS-FIXES (2B/4M/3m first Critic + EXTEND meta-Critic 2 MISSED; all VALID; verdict NEEDS-FIXES)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Critique complete — verdict **NEEDS-FIXES** (user-ratified TRI-1 2026-05-29). Dual-review ran: first Critic 2B/4M/3m (all VALID, no over-reach); meta-Critic EXTEND with 2 MISSED findings re-interrogating the Builder's fixes. All 11 findings ACCEPTED-FIXED except m2 + M-add-2 (ACCEPTED-PENDING, applied at build). Key design changes from review: (B1+M-add-2) Critic mechanism is the **`code-review` agent** (single pass, diff-calibrated) — the named critique agents fail-stop on missing slice artifacts; (B2+M-add-1) `--verify-resolution` keys on line-anchored `<<<<<<<`/`>>>>>>>` openers (NOT `=======`/`git diff --cached --check`, which false-STOP on Markdown setext); (M2) skill keys gate-entry on returned `conflict_class`; (M3) TRI-RESOLVE-1 fail-closed mechanism pinned; (M4) `_index.md` high-frequency framing corrected + lighter-path queued.

Pending for /build-slice: m2 (update stale `slice-079` forward-ref in SKILL.md + resolver docstring); M-add-2 (wire the `code-review` agent into SKILL.md sub-step 2.5). APED-1 obligation: verify the marker-detection rule against the repo markdown corpus (setext headings must be CLEAN) and quote in build-log.md.

## On resume

- **Last completed action**: /critique + /critique-review (critique.md + critique-review.md written; TRI-1 ratified NEEDS-FIXES; design.md + ADR-075 + mission-brief updated with all fixes)
- **Current work**: none
- **Next immediate step**: run `/build-slice` (NEEDS-FIXES — apply ACCEPTED-PENDING m2 + M-add-2 during build)

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — NEEDS-FIXES (first Critic)
- [critique-review.md](critique-review.md) — EXTEND (meta-Critic, 2 MISSED)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
