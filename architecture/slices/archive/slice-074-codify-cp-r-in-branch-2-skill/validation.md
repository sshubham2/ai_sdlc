# Validation: Slice 074 codify-cp-r-in-branch-2-skill (expanded)

**Date**: 2026-05-28
**Result**: PASS

## Per-criterion results

### AC#1: `skills/build-slice/SKILL.md` `### Branch state` point 1 bash codefence contains cp -r invocations for `diagnose-out/` AND `graphify-out/`, after the `cd` line and BEFORE point 2, with R-20 reference comment

- **Status**: PASS
- **Evidence**:
  - Pytest: `test_build_slice_skill_cp_r_step.py::test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd PASSED` + `test_cp_r_lines_reference_r_20_in_comment PASSED`
  - Grep: `skills/build-slice/SKILL.md:62-63` shows the two if-then-fi guarded cp -r lines, positioned AFTER `cd "$wt_base/slice-NNN-<slice-name>"` (L60) and BEFORE codefence-close (L64) and point 2 (L67)
  - R-20 reference comment at SKILL.md L61: `# Seed gitignored derived dirs from main tree (R-20): /diagnose + graphify outputs`
- **Notes**: cp -r prose physically landed at the canonical insertion site per design.md §"What's new". Recursive-self-application bootstrap exception per CRP-1/ADR-024 honored — codified prose was NOT exercised at slice-074's own /build-slice Phase A (the installed SKILL.md was still pre-slice during prereq check; manual cp -r at R-20 N=9 cumulative); canonical N+1 first-governed-slice demo is slice-075's Phase A.

### AC#2: cp -r prose handles source-dir-absence gracefully via set-e-safe `if [ -d "$repo_root/<dir>" ]; then cp -r "$repo_root/<dir>" ./; fi`

- **Status**: PASS
- **Evidence**:
  - Pytest: `test_cp_r_lines_use_if_then_guard_for_source_dir_absence PASSED`
  - Manual POSIX semantic walk-through: `if [ -d "/nonexistent" ]; then cp -r "/nonexistent" ./; fi` — `[ -d ]` test returns 1 (false), `then` branch not executed, `if` statement returns 0 overall. Exit-status-neutral on source-absent path. set-e-safe per /critique pass-1 m3 ACCEPTED-FIXED.
- **Notes**: Switched from `[ -d ... ] && cp -r` chained form (which leaks exit 1 on guard-skip) per /critique pass-1 m3. Single-line `if/then/fi` form pinned via RSAD-1 byte-exact-match discipline per /critique-review pass-1 m-add-1.

### AC#3: OSDG-1 forward-sync verified — installed `~/.claude/skills/build-slice/SKILL.md` content-equal modulo line endings to in-repo copy

- **Status**: PASS
- **Evidence**:
  - Pytest: `test_build_slice_skill_drift.py::test_build_slice_skill_md_in_repo_byte_equal_installed PASSED`
  - Sync command: `Copy-Item C:\Users\sshub\ai_sdlc-wt\slice-074-codify-cp-r-in-branch-2-skill\skills\build-slice\SKILL.md C:\Users\sshub\.claude\skills\build-slice\SKILL.md -Force`
  - CAD-1 audit corroborates: `agents/critique.md` content-equal (EOL-agnostic) across in-repo + installed; same discipline applies to SKILL.md surfaces.
- **Notes**: Installed copy carries the codified cp -r + switch-commit-switch prose post-sync. Slice-075's /build-slice Phase A prereq will read this codified prose at the worktree-create step.

### AC#4: R-20 status flipped `mitigating` → `retired` in `architecture/risk-register.md`; audit emits R-20 in retired list

- **Status**: PASS
- **Evidence**:
  - Pytest: `test_r_20_retired.py::test_r_20_status_is_retired_in_risk_register PASSED`
  - Audit output: `[medium] R-20 score=3 (highxlow) status=retired - Gitignored 'diagnose-out/' + 'graphify-out/' directories require manual 'cp -r' from main tree to worktree at every BRANCH-2 slice (post-vault-in-git cp-r tax residual)`
  - Risk-register.md L344 shows `**Status**: retired` (was `mitigating` pre-slice); L346 has new `**Retired**: slice-074-codify-cp-r-in-branch-2-skill (2026-05-28) — candidate fix (a) operationalized; ... slice-074 itself is the bootstrap instance (mirrors CRP-1 / ADR-024 slice-026 bootstrap exception)` paragraph.
- **Notes**: R-20 retirement paragraph explicitly cites the bootstrap-exception framing per /critique pass-1 M1 ACCEPTED-FIXED so future readers don't conflate slice-074 with the N+1 first-governed-slice demonstration (slice-075).

### AC#5: SKILL.md `### Branch state` point 4 contains the canonical switch-commit-switch-worktree 4-step sequence in order, inside a bash codefence (with NO `git stash`)

- **Status**: PASS
- **Evidence**:
  - Pytest: `test_point_4_contains_switch_commit_switch_worktree_sequence_in_order PASSED` + `test_point_4_codefence_does_not_contain_git_stash PASSED`
  - Grep `skills/build-slice/SKILL.md` for canonical tokens — order verified:
    - L77 (token 1): `git switch -c slice/NNN-<slice-name>          # carry dirty state to slice branch`
    - L79 (token 2): `git commit -m "scaffold(slice-NNN): mission-brief + design + critique + ..."  # scaffolding commit on slice branch` (within bash codefence at L73-86)
    - L80 (token 3): `git switch "$default"                           # back to clean default`
    - L81 (token 4): `git worktree add "$wt_base/slice-NNN-<slice-name>" slice/NNN-<slice-name>   # no -b; branch exists`
  - `grep "git stash" skills/build-slice/SKILL.md` finds 0 matches in point-4 codefence body (NO-auto-stash discipline structurally pinned per /critique-review pass-2 m2 ACCEPTED-FIXED)
- **Notes**: Codified inside a bash codefence per /critique pass-2 M1 ACCEPTED-FIXED (forecloses prose-only-narrative false-pass). Includes the scaffold-commit body shape `git commit -m "scaffold(slice-NNN):` as 5th anchor token. Canonical-origin comment cites slice-070 reflection L127 per /critique pass-2 m1 ACCEPTED-FIXED.

### AC#6: SKILL.md `### Branch state` documents BOTH worktree-create forms — new-branch `git worktree add ... -b slice/NNN-<name> "$default"` at point 1 AND existing-branch `git worktree add ... slice/NNN-<name>` (no `-b`) at point 4

- **Status**: PASS
- **Evidence**:
  - Pytest: `test_both_worktree_create_forms_documented_dash_b_and_no_dash_b PASSED`
  - Grep `skills/build-slice/SKILL.md`:
    - L59 (point 1, `-b` form): `git worktree add "$wt_base/slice-NNN-<slice-name>" -b slice/NNN-<slice-name> "$default"`
    - L81 (point 4 codefence, no-`-b` form): `git worktree add "$wt_base/slice-NNN-<slice-name>" slice/NNN-<slice-name>   # no -b; branch exists`
- **Notes**: Both forms documented and structurally distinguishable. The trailing `# no -b; branch exists` comment is preserved through /critique pass-2 B1 ACCEPTED-FIXED (comment-aware lookahead `(?!(?:[^#\n]*?)-b\s)` correctly excludes the comment's `-b;` literal).

## Multi-instance validation

**Required?**: no — this slice's surface is a single SKILL.md file + 3 test modules + 1 risk-register status flip; no multi-user / multi-device / multi-account semantics. The codified `cp -r` step DOES involve two filesystem trees (main + worktree) but that's intra-machine filesystem coordination, not multi-instance distributed semantics.

**Result**: not-applicable

## Layered safety checks (VAL-1)

**Layer A — Credential scan**: PASS — 0 secrets detected across 13 changed files.
**Layer B — Dependency hallucination check**: PASS — 0 import findings (3 new test modules use only stdlib + `tests` namespace allowlist; no new dependencies introduced).

## Shippability catalog regression check (Step 5.5)

**SCMD-1 pre-gate**: PASS — 73 rows / 779 cited fns clean (2 essential_registered, 0 essential_unregistered, 0 incidental).
**PTFCD-1 sub-mode (b) pre-gate**: PASS — 73 rows / 379 test-path tokens all resolve to existing files.
**Shippability runner**: **73/73 PASS, 0 FAIL** — no past slice was silently regressed by slice-074's edits.

## Reality surprises

None this slice. Both codifications landed as designed; all 7 new structural-pin tests + the existing OSDG-1 drift test PASS; all 73 shippability catalog rows PASS unchanged from slice-073's baseline. The code-Critic M1 finding (point-4 codefence variable-scope assumption) is a real defect but is bounded (loud failure not silent) and deferred to slice-075+ `bundle-074-code-critic-cleanup` per voluntary-restraint discipline N=15 cumulative — not a "reality surprise" because it was caught at /code-review pre-validation. Slice-075 will be the empirical first-governed-slice for both R-20 candidate (a) AND the switch-commit-switch codification — if M1's variable-scope defect materializes, slice-075's Phase A prereq will surface it loud-and-clear, which is the canonical slice-040 N+1 first-governed-slice catch surface.

## Decision

All ACs PASS + VAL-1 clean + shippability runner clean → auto-advance to `/reflect` per PCA-1 (no FAIL / PARTIAL gates fire).
