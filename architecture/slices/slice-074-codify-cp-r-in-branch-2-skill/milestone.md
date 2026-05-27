---
slice: slice-074-codify-cp-r-in-branch-2-skill
stage: critique
updated: 2026-05-28
next-action: run /build-slice (TRI-1 CLEAN verdict ratified)
risk-tier: low
critic-required: true
---

# Milestone: slice-074 codify-cp-r-in-branch-2-skill

**Stage**: critique (post-TRI-1)
**Next action**: run `/build-slice` — TRI-1 verdict CLEAN ratified (10 dispositions all ACCEPTED-FIXED in-band; M4 severity Major→Minor accepted)
**Updated**: 2026-05-28
**Risk tier**: low — Critic required: yes (in-house methodology surface — `skills/build-slice/SKILL.md` — triggers always-mandatory Critic regardless of tier; OSDG-1 / CAD-1 family)

## Progress

- [x] /slice — 2026-05-28
- [x] /design-slice — 2026-05-28
- [x] /critique — 2026-05-28 — CLEAN (post-TRI-1; 10 dispositions all ACCEPTED-FIXED in-band; M4 severity Major→Minor at TRI-1 per /critique-review SEVERITY-WRONG accepted)
- [x] /critique-review — 2026-05-28 — ADJUST (0 suspicious / 2 missed Minor m-add-1+m-add-2 both ACCEPTED-FIXED in-band on design.md / 1 M4 severity adjustment accepted at TRI-1)
- [ ] /build-slice
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Critic returned 0 Blockers / 4 Majors / 4 Minors. Builder draft: all 8 ACCEPTED-FIXED in-band on mission-brief.md + design.md. Key changes applied: (a) M1 — reframed must-not-defer #2 as bootstrap exception mirroring CRP-1 / ADR-024 slice-026; added design.md §"Bootstrap framing"; canonical first-governed-slice (N+1) demo deferred to slice-075. (b) M2 — section-extraction regex tightened to `(?=^## [A-Z])` (require capital after H2 marker). (c) M3 — AC#1 test regex anchored to `^\s*if \[ -d ... \]; then cp -r` guard prefix (forestalls comment-substring leak). (d) M4 — design.md §MEPD-1 EXCLUDE gains explicit rule-mint-vs-surface-class differentiating-axis sentence citing slice-066. (e) m1 — design.md test-count framed as "+4 NEW; 5 TF-1 rows total". (f) m2 — mission-brief pre-finish gate reframed as post-EXCLUDE-decision; INCLUDE demoted to contingency. (g) m3 — switched `[ -d ...] && cp -r` to `if [ -d ...]; then cp -r ...; fi` per-line form (set-e-safe). (h) m4 — TF-1 row 4 cites actual function `test_build_slice_skill_md_in_repo_byte_equal_installed`. Test function rename: `test_cp_r_lines_use_dash_d_guard_for_source_dir_absence` → `test_cp_r_lines_use_if_then_guard_for_source_dir_absence`. Next: meta-Critic review then user-owned TRI-1 ratification.

## On resume

- **Last completed action**: /critique Step 4.5 TRI-1 user-owned triage (verdict CLEAN ratified by user; M4 severity demotion accepted)
- **Current work**: none
- **Next immediate step**: run `/build-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [critique.md](critique.md) — CLEAN (post-TRI-1; 10 dispositions all ACCEPTED-FIXED)
- [critique-review.md](critique-review.md) — ADJUST (M4 severity Major→Minor; m-add-1 + m-add-2 missed Minor both ACCEPTED-FIXED in-band)
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
