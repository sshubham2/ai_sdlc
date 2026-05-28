# Slice 074: codify-cp-r-in-branch-2-skill (expanded at /build-slice plan-mode: + switch-commit-switch-worktree codification)

**Mode**: Standard
**Estimated work**: ~2-3 hours (SMALL-MEDIUM — two-codification single-surface; cp -r addition + switch-commit-switch addition + 4 structural-pin tests + R-20 status flip + OSDG-1 sync)
**Risk retired**: R-20 (`mitigating` → `retired`) — gitignored `diagnose-out/` + `graphify-out/` cp -r tax at every BRANCH-2 slice (N=9 cumulative through slice-074 inclusive; "SEVERELY OVERDUE" per slice-073 reflection L28, L38). Switch-commit-switch codification does NOT retire a separate tracked risk (the pattern is an empirical-recurrence codification, not a risk-register-tracked class; N=5 cumulative slice-070/071/072/073/074).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false
**Scope-expansion note**: original slice-074 scope was cp -r codification ONLY (AC#1-AC#4). User approved scope expansion at /build-slice plan-mode (PCA-1 gate) to ALSO codify the switch-commit-switch-worktree pattern (AC#5-AC#6). The expansion was re-Critic'd via /critique + /critique-review run on the AC#5+AC#6 delta; dispositions ratified at TRI-1-EXT before /build-slice execution began. The original AC#1-AC#4 dual-Critic clearance remains valid.

## Intent

**Two adjacent codifications in `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section** — both operationalize empirically-stable patterns, neither mints a new methodology rule:

1. **Operationalize R-20 candidate fix (a)** — codify the `cp -r ../<main>/diagnose-out ../<main>/graphify-out ./` step into the bash codefence at point 1 (after `cd "$wt_base/slice-NNN-<slice-name>"`). Removes the "I forgot to cp" per-slice failure mode at /build-slice prerequisite check; structurally retires the cp -r tax that has surfaced at every post-vault-in-git BRANCH-2 slice since slice-067 (N=9 cumulative through slice-074 inclusive). Cheapest of the four R-20 candidate fix classes.

2. **Codify the switch-commit-switch-worktree pattern** as the canonical resolution recipe at point 4 ("If working tree is dirty in the main tree"), replacing the current "STOP, ask user to commit or stash" prose with the 4-step sequence empirically-stable across N=5 cumulative slices (slice-070/071/072/073/074): `git switch -c slice/NNN-<name>` (carries dirty state to slice branch) → commit scaffolding → `git switch <default>` (back to clean) → `git worktree add <wt-path> slice/NNN-<name>` (no `-b` — branch already exists). Removes the "STOP and ask user" punt for post-vault-in-git slices where the dirty state is always scaffolding-by-design (mission-brief.md + design.md + critique.md + critique-review.md + milestone.md written before /build-slice).

Why now: slice-073 reflection promoted both as "slice-074+ candidate". Doing nothing means slice-075 will be N=10 cp-r and N=6 switch-commit-switch. Same SKILL.md surface, same fix-block, same dual-Critic + OSDG-1 sync mechanics — codifying both in one slice is more efficient than two consecutive single-codification slices.

## Acceptance criteria

(6 ACs — per slice-072 reflection L97 carve-out: AC count > 5 is permissible when AC6 is exclusively an additional structural-pin meta-AC, which applies here for AC#6's no-`-b` form distinction.)

1. `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section's numbered point 1 ("If on default branch") bash codefence contains `cp -r` invocations for `diagnose-out/` AND `graphify-out/`, placed AFTER the `cd "$wt_base/slice-NNN-<slice-name>"` line and BEFORE the codefence close, with reference to risk-register R-20 (e.g., a `# Seed gitignored derived dirs from main tree (R-20)` comment) so future readers can trace the codification's origin.
2. The codified cp -r prose handles source-dir-absence gracefully — uses the set-e-safe `if [ -d "$repo_root/<dir>" ]; then cp -r "$repo_root/<dir>" ./; fi` POSIX guard (per /critique m3 — the `&&` chained form leaks exit-status 1 on guard-skip and would fail loudly under future `set -e` hardening; `if/then/fi` is exit-status-neutral on the false branch) so a fresh project that has never run `/diagnose` or `graphify code` does NOT fail at /build-slice prerequisite check; structural-pin test asserts the `if [ -d ... ]; then cp -r` guard literal is present on each `cp -r` line.
3. OSDG-1 forward-sync verified post-edit: installed `~/.claude/skills/build-slice/SKILL.md` content-equal modulo line endings to in-repo copy; `tests/methodology/test_build_slice_skill_drift.py` PASSES against the new prose.
4. R-20 status flipped `mitigating` → `retired` in `architecture/risk-register.md`; `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status retired` includes R-20 in its output; the retiring slice cited as `slice-074-codify-cp-r-in-branch-2-skill`.
5. `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section's numbered point 4 ("If working tree is dirty in the main tree") replaces the current "STOP, ask user to commit or stash on the main tree. NO auto-stash." prose with the canonical switch-commit-switch-worktree 4-step sequence (N=5 cumulative slice-070/071/072/073/074); structural-pin test asserts the 4 ordered tokens are present in point 4: `git switch -c slice/NNN-<slice-name>` → commit token → `git switch "$default"` → `git worktree add` (no `-b`).
6. SKILL.md `### Branch state` documents BOTH worktree-create forms — the new-branch form `git worktree add ... -b slice/NNN-<name> "$default"` at point 1 (current behavior) AND the existing-branch form `git worktree add ... slice/NNN-<name>` (no `-b`) at point 4 — so a reader following the switch-commit-switch sequence at point 4 does NOT mistakenly include `-b` (which would cause `fatal: A branch named 'slice/NNN-...' already exists`); structural-pin test asserts both forms are documented and distinguishable.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0): each AC maps to one or more failing tests written BEFORE the SKILL.md / risk-register edits. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural-pin | tests/methodology/test_build_slice_skill_cp_r_step.py | test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd | PASSING |
| 1 | structural-pin | tests/methodology/test_build_slice_skill_cp_r_step.py | test_cp_r_lines_reference_r_20_in_comment | PASSING |
| 2 | structural-pin | tests/methodology/test_build_slice_skill_cp_r_step.py | test_cp_r_lines_use_if_then_guard_for_source_dir_absence | PASSING |
| 3 | drift (existing class) | tests/methodology/test_build_slice_skill_drift.py | test_build_slice_skill_md_in_repo_byte_equal_installed | PASSING |
| 4 | structural-pin | tests/methodology/test_r_20_retired.py | test_r_20_status_is_retired_in_risk_register | PASSING |
| 5 | structural-pin | tests/methodology/test_build_slice_skill_dirty_tree_resolution.py | test_point_4_contains_switch_commit_switch_worktree_sequence_in_order | PASSING |
| 5 | structural-pin | tests/methodology/test_build_slice_skill_dirty_tree_resolution.py | test_point_4_codefence_does_not_contain_git_stash | PASSING |
| 6 | structural-pin | tests/methodology/test_build_slice_skill_dirty_tree_resolution.py | test_both_worktree_create_forms_documented_dash_b_and_no_dash_b | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | cp -r prose codified | Run `tests/methodology/test_build_slice_skill_cp_r_step.py::test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd` + `..._references_r_20_in_comment` — both must PASS. Additionally, `grep -A 20 '^### Branch state' skills/build-slice/SKILL.md \| grep -E '\bcp -r\b.*(diagnose-out\|graphify-out)' \| wc -l` reports ≥2. |
| 2 | source-dir-absence handled | Run `tests/methodology/test_build_slice_skill_cp_r_step.py::test_cp_r_lines_use_if_then_guard_for_source_dir_absence` — must PASS. Cross-check: `grep -E 'if \[ -d.*\]; then cp -r' skills/build-slice/SKILL.md` finds both occurrences. |
| 3 | OSDG-1 sync clean | After `cp skills/build-slice/SKILL.md "$env:USERPROFILE\.claude\skills\build-slice\SKILL.md"`, run `$PY -m pytest tests/methodology/test_build_slice_skill_drift.py -v` — expect 1 PASS. |
| 4 | R-20 retired | Run `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status retired \| Select-String 'R-20'` — match present. Also `$PY -m pytest tests/methodology/test_r_20_retired.py -v` — expect 1 PASS. |
| 5 | switch-commit-switch sequence codified | Run `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py::test_point_4_contains_switch_commit_switch_worktree_sequence_in_order` AND `..._does_not_contain_git_stash` — both must PASS. Cross-check: `grep -A 20 'If working tree is dirty' skills/build-slice/SKILL.md` shows the 4 ordered tokens (`git switch -c slice/`, `git commit -m "scaffold(slice-NNN):`, `git switch "$default"`, `git worktree add`) inside a bash codefence AND `grep 'git stash' skills/build-slice/SKILL.md` returns nothing in point-4 region. |
| 6 | both worktree-create forms documented | Run `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py::test_both_worktree_create_forms_documented_dash_b_and_no_dash_b` — must PASS. Cross-check: point 1 has `git worktree add ... -b slice/NNN-<slice-name>` AND point 4 has `git worktree add ... slice/NNN-<slice-name>` (no `-b`). |

## Must-not-defer

- [ ] Codified `cp -r` step is **idempotent** (re-running on existing worktree overwrites cleanly — confirmed by POSIX `cp -r` semantics; no extra `--update` or `--no-clobber` flags needed because derived artifacts are regeneratable).
- [ ] Codified switch-commit-switch-worktree sequence (point 4) is **NOT idempotent by design** — re-running after a session death mid-scaffolding-commit must fail LOUDLY at `git switch -c slice/NNN-<name>` with `fatal: A branch named 'slice/NNN-...' already exists`; recovery is via point 2 ("If the worktree already exists") handle, NOT silent re-creation. Prose explicitly notes the non-idempotency rather than papering over it (so a Builder doesn't get confused by the failure).
- [ ] **Recursive self-application — BOOTSTRAP exception** (per /critique M1 ACCEPTED-FIXED, mirroring CRP-1 / ADR-024 slice-026 bootstrap exception precedent): slice-074 is the BOOTSTRAP instance. At slice-074's own Phase A prerequisite check, `/build-slice` reads the INSTALLED `~/.claude/skills/build-slice/SKILL.md` which is still the pre-slice (v0.72.0) prose — the codified `if [ -d ... ]; then cp -r ...; fi` step does NOT yet exist in Claude's reading. The cp -r that runs at slice-074 Phase A is the same MANUAL cp -r that has run at slices 067-073 (R-20 N=8). The OSDG-1 forward-sync (Phase B/C) propagates the codification to the installed copy AFTER prereq check has already passed. **Canonical first-governed-slice (N+1) demonstration is slice-075's /build-slice Phase A** — the build-log Events line documenting `if/then/fi cp -r` running from the codified SKILL.md prose lives at slice-075, not slice-074. Slice-074's discharge of recursive-self-application is: (a) OSDG-1 forward-sync at Phase B/C lands the prose in the installed copy; (b) the 3 structural-pin tests PASS against the in-repo SKILL.md; (c) the manual Phase A cp -r still works as it has for slices 067-073.
- [ ] Mid-slice smoke gate (~50% of build) verifies the structural-pin test ASSERTIONS match the SKILL.md prose byte-for-byte (no whitespace-stripping mismatch; cf. slice-071 M6 sentinel-test docstring/assertion verbatim mismatch class — RSAD-1 prevention).
- [ ] Windows compatibility verified — `cp -r` works under Git for Windows MSYS bash per the existing SKILL.md L62 convention; structural-pin test asserts the POSIX `cp -r` literal (NOT PowerShell `Copy-Item -Recurse`) so the codification stays consistent with the surrounding shell-bash prose.
- [ ] OSDG-1 forward-sync runs in the SAME slice (not deferred) — installed copy MUST land via `cp skills/build-slice/SKILL.md "$env:USERPROFILE\.claude\skills\build-slice\SKILL.md"` before /commit-slice; AVFS-1 / MCFS-1 / TVFS-1 audits all pass.

## Out of scope

- **R-20 candidate (b) symlink discipline** — Windows junction/symlink fragility per slice-066 critique-review B2 lineage; cross-platform symlink-creation requires elevated privileges on Windows pre-Developer-Mode. Deferred unless the codified cp -r approach later proves inadequate.
- **R-20 candidate (c) un-gitignore `graphify-out/` + `diagnose-out/`** — violates derived-artifacts-shouldn't-be-tracked principle (~5-15MB churn per `/diagnose` run; environment-dependent graph state). ADR-066 vault-in-git philosophy explicitly excludes derived artifacts.
- **R-20 candidate (d) audit gate that auto-runs cp -r** — escalation reserved for the case where the codified-prose approach surfaces N≥3 additional "I forgot to read the SKILL.md" failures. The codified prose with explicit graceful-absence guards is sufficient unless empirical use refutes it.
- **Changes to `/commit-slice` Step 5b worktree-teardown** — worktree-remove already removes the cp-r'd dirs cleanly; no asymmetric teardown step needed.
- **Audit module to ENFORCE the cp -r ran on disk** — Phase E mid-slice smoke gate ALREADY catches a missing-diagnose-out/-graphify-out via existing BCR-1 test failures (e.g., slice-071 surfaced this exact way); structural codification at /build-slice prerequisite is the structural fix.
- **Extending the codification to other gitignored-derived directories beyond `diagnose-out/` + `graphify-out/`** — these are the only two surfaced in R-20's N=9 cumulative observations; adding speculative directories now would violate slice-022 "codify exactly what reality has demanded" pattern.
- **Retroactive cp -r in BRANCH-1 fallback path** — BRANCH-1 single-tree-only path doesn't have a worktree-vs-main-tree gap; cp -r is moot there.
- **Auto-stash inside the switch-commit-switch sequence** — the current point 4 prose explicitly says "NO auto-stash"; the codified sequence preserves this discipline by requiring the Builder to explicitly stage + commit the scaffolding (not silently shelve it via `git stash`). The codification ADDS the recipe but does NOT relax the no-auto-stash discipline. Auto-stash class deferred indefinitely (slice-022 codify-empirical-pattern, no demand for auto-stash).
- **Switch-commit-switch tooling automation** — e.g., a `tools/scaffold_commit.py` helper that runs the 4-step sequence automatically. The codification is prose-only; automation would be a separate slice if empirical use shows the manual sequence is error-prone (no evidence yet — Builders have executed it correctly N=5 cumulative).
- **Close-merge-substep-3-worktree-collision-stop-asymmetry** (queue candidate #7 in `architecture/slice-queue.md`) — slice-073 design.md tracks this as a separate concern touching `skills/commit-slice/SKILL.md` Step 5b sub-step 3. Different surface, different scope; deferred to slice-075+.

## Dependencies

- Prior slices:
  - [[slice-066-add-worktree-per-slice-discipline]] — minted BRANCH-2 / ADR-063; provides the `## Prerequisite check ### Branch state` sub-section being amended.
  - [[slice-069-track-vault-in-git]] — minted ADR-066 vault-in-git philosophy; established the derived-artifacts-stay-gitignored principle that R-20 documents and that this slice operationalizes within.
  - [[slice-071-bundle-066-to-070-code-critic-cleanup]] — promoted R-20 from recurring-class observation (N=6) to risk-register tracked entry with 4 candidate fix classes.
  - [[slice-073-add-rebase-and-conflict-discipline]] — R-20 N=8 cumulative; "SEVERELY OVERDUE" nomination text (reflection L28, L38).
- Vault refs:
  - [[architecture/risk-register#R-20]] — the cp-r tax risk this slice retires.
  - [[architecture/decisions/ADR-063]] — BRANCH-2 contract being extended.
  - [[architecture/decisions/ADR-066]] — vault-in-git philosophy that constrains the fix to candidate (a) over (c).
  - [[skills/build-slice/SKILL.md#Branch state]] — surface being amended.
- Risk register:
  - [[risk-register#R-20]] — `mitigating` → `retired` is AC#4.

## Mid-slice smoke gate

At ~50% of build (after TF-1 Phase A RED tests authored + Phase B SKILL.md prose edits landed for BOTH codifications, BEFORE Phase C OSDG-1 sync + R-20 status flip):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_build_slice_skill_cp_r_step.py tests/methodology/test_build_slice_skill_dirty_tree_resolution.py -v
```

Expected: 6 PASS (3 cp-r structural-pin tests + 3 switch-commit-switch structural-pin tests — order-tokens-in-codefence + no-`-b` form pin + no-`git stash` discipline pin). If any FAIL: STOP, inspect SKILL.md prose vs test assertions for byte-level mismatch (whitespace, comment-marker drift, regex-vs-literal substring). Do not proceed to Phase C until all 6 PASS — the canonical RSAD-1 prevention pattern from slice-071 M6.

Additionally, demonstrate the codified cp -r step actually works in a real worktree context — Phase A's /build-slice prerequisite check for slice-074 itself ran the codified step (recursive self-application per slice-022 law); the build-log Events line documents this with a timestamp + cwd context.

## Pre-finish gate

- [ ] All 6 acceptance criteria PASS with evidence in validation.md
- [ ] All 6 must-not-defer items addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression in the 6 structural-pin tests — 3 cp-r + 3 switch-commit-switch)
- [ ] OSDG-1 audit on `build-slice` SKILL.md clean post-sync (no CRLF/LF false-positives; EOL-agnostic per ADR-033)
- [ ] BC-1 Step 6 audit run; any false-positives documented as defer-with-rationale per N=5 cumulative BC-GLOBAL-2 prose-vs-automation class (slice-073 reflection L29)
- [ ] PMI-1 audit clean — **MEPD-1 EXCLUDE is the chosen stance** per design.md §"MEPD-1 stance: EXCLUDE" (post-/design-slice decision; ships at v0.72.0 unchanged; no PMI-1 bump; no BC-PROJ-10 paired-pin obligation; no shippability row #74). (Contingency: if /critique re-opens the EXCLUDE choice and demands INCLUDE — verdict not BLOCKED, but a Major demanding stance reversal — fall back to the 5-part atomic bump 0.72.0 → 0.73.0 + BC-PROJ-10 paired-pin path; m2 ACCEPTED-FIXED at /critique demoted this branch to a frozen contingency.)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full pytest **>= 995/995 PASS** post-slice (slice-073 baseline was 995/995; this slice adds 7 new tests → expect ~1002/1002 PASS — 4 cp-r-scope tests + 3 switch-commit-switch-scope tests including no-stash discipline pin)
- [ ] Shippability runner clean (MEPD-1 EXCLUDE → 73/73 PASS unchanged; no shippability row added)
