---
slice: slice-105-decouple-slice-loop-from-diagnose-out
stage: build
updated: 2026-06-03
next-action: build Batch D — vault/config (shippability + changelog + R-20 + CLAUDE.md + v0.82.0 tests)
risk-tier: high
critic-required: true
---

# Milestone: slice-105 decouple-slice-loop-from-diagnose-out

**Stage**: critique
**Next action**: run `/build-slice`
**Updated**: 2026-06-03
**Risk tier**: high — Critic required: yes (mandatory: touches `tools/**/*.py` + `skills/*/SKILL.md` + `methodology-changelog.md`; partial-supersedes two codified ADRs — ADR-090 seed-step + ADR-055 round-trip half)

## Progress

- [x] /slice — 2026-06-03
- [x] /design-slice — 2026-06-03
- [x] /critique — 2026-06-03 — CLEAN (first Critic BLOCKED → dual-review EXTEND → 13 findings ACCEPTED-FIXED, user-ratified)
- [ ] /build-slice — in progress: Batches A/B/C done (3/6); D/E/F remain
- [ ] /validate-slice
- [ ] /reflect

## Current focus

**Build in progress — Batches A/B/C done + verified.** The 3 atomic prose↔test batches (the structurally trickiest parts) are complete: A = seed removal in `_worktree_paths.py` + `test_worktree_paths.py` + 2 deleted test files + `test_resolve_slice_dir.py` guard + `slice/SKILL.md` Step 5.5; B = `build-slice/SKILL.md` seed/cp-r removal; C = `reflect/SKILL.md` round-trip→retired + `test_bcr_1_backlog_round_trip.py` #4-#8 removal. Suite collects 1385, consume-side green. **Next: Batch D** (vault/config), then E (version+mirror), F (audits+validate).

## On resume

- **Last completed action**: /build-slice Batches A+B+C (seed removal + 3 SKILL.md surgical edits + test cleanups), all verified green except the expected unmirrored-drift fails.
- **Current work**: none — paused at the Batch C→D boundary.
- **Next immediate step — Batch D** (vault/config, in the worktree):
  1. `architecture/risk-register.md` R-20 → closure note via `vault_edit rewrite` CAS (capture base with `--out-file`, edit copy, rewrite; status stays `retired`, broaden to "fully closed — seed mechanism removed").
  2. `architecture/shippability.md` (giant file — edit by token, NEVER delete rows): row #54 (L64) + #56 (L66) drop `test_bcr_1_round_trip_end_to_end.py::...` token from BOTH command-cell copies + reword round-trip narrative past-tense (keep PVFS-1/SC-001 on #54, R-15 on #56); row #79 (L87) drop `test_build_slice_skill_cp_r_step.py` token (keep 4 survivors); row #107 (L116) rewrite narrative (drop "seeds via seed_derived_dirs"/"cp -r count is 2" + their regression clauses; keep BRANCH-3/ADR-090/R-31/pick); catalog row #53 (L63) narrow to consume-side; ADD new Row #105 (cite ADR-094/ADR-095/R-20/consume-only + runnable command).
  3. `methodology-changelog.md` (repo root): add `## v0.82.0 — 2026-06-03` entry citing ADR-094/ADR-095/BCR-1/R-20/consume-only + a `Rule reference` line (META-1).
  4. `CLAUDE.md` (project): BCR-1 paragraph in `## Self-hosting discipline` → consume-only wording.
  5. `tests/methodology/test_methodology_changelog.py`: add `test_v_0_82_0_decouple_entry_present_in_repo` + `test_v_0_82_0_decouple_shippability_consumer_propagation` (mirror slice-099 `test_v_0_81_0_branch_3_*` at :5603/:5672).
- **Then Batch E** (version + mirror): bump 5 surfaces 0.81.0→0.82.0 (VERSION, plugin.yaml, pyproject, ~/.claude/ai-sdlc-VERSION, ~/.claude/methodology-changelog.md); `$PY -m pip install --upgrade .` (TVFS-1); OSDG-1 mirror `skills/{slice,build-slice,reflect}/SKILL.md` → `~/.claude/skills/.../SKILL.md` (fixes the 3 expected drift fails); verify ADR-055/ADR-090 byte-unmodified.
- **Then Batch F** (gates): mid-slice seedless-parity smoke (rename diagnose-out/graphify-out aside → `pytest tests/methodology -q` green); full suite + ~18 pre-finish audits (BC-1, WIRE-1, BRANCH, UTF8, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, DCE-1, SVW-1, PMI-1) iterating to green; `/drift-check` full mode + DCE-1; then `/validate-slice`.
- **Watch**: STP-1 may flag any test still pinning removed seed/round-trip prose (none expected — cp_r test deleted, reflect #4-#8 removed); the `**Closes:** SC-` literal is still referenced by consume-side test #? — verify it's only the reflect side that's gone.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-094](../../decisions/ADR-094-retire-worktree-derived-dir-seed.md), [ADR-095](../../decisions/ADR-095-redefine-bcr-1-consume-only.md)
- [critique.md](critique.md) — CLEAN (post-TRI-1)
- [critique-review.md](critique-review.md) — EXTEND (dual-review)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
