# Slice 021: add-feature-branch-workflow-at-build-and-commit-slice

**Mode**: Standard
**Estimated work**: 0.5 day (~3–4 hours)
**Risk retired**: workflow-class — replaces "all slices commit directly to master" with branch-per-slice. Not a register entry (no R-N today); registers as ADR-019 + new BRANCH-1 discipline in `architecture/build-checks.md` if recurrence-promoted.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Today every slice's build, validate, reflect, and commit-slice commits all land directly on `master`. There is no rollback boundary for a half-finished slice and no per-slice diff surface for review. This slice introduces a `slice/NNN-<name>` branch the user works on during `/build-slice`, and adds a `--merge` flag to `/commit-slice` that commits to that branch and then no-fast-forward merges it back to master (preserving slice attribution as one merge commit). `--do-commit` is replaced by `--merge` to reflect the actual semantics of the integrated flow.

## Acceptance criteria

1. `/build-slice` SKILL.md `## Prerequisite check` H2 section gains a NEW sub-section `### Branch state` (post /critique B3 ACCEPTED-PENDING — replaces prior "Phase 0.5" framing per slice-017 TPHD-1 precedent at methodology-changelog v0.32.0 L102: build-slice step numbering is 1,2,3,4,5,6,7,7b,7c,8 with no Step 0; branch-create discipline IS a prerequisite verification). Logic: resolve repo's default branch via `git symbolic-ref refs/remotes/origin/HEAD` with `git config init.defaultBranch` fallback (per /critique M1 ACCEPTED-PENDING — replaces hard-coded `master`/`main`); if HEAD is on the resolved default branch, create `slice/NNN-<slice-name>` from HEAD and check it out; if `slice/NNN-<slice-name>` already exists, switch to it; if any other branch is currently checked out, STOP and ask the user (escape hatch: documented `BRANCH=skip` rationale recorded in `build-log.md` Events using the canonical shape pinned by AC #2 below).
2. `/build-slice` SKILL.md Step 7c flight-recorder discipline gains a canonical `BRANCH=skip` line-shape sentence (post /critique B1 ACCEPTED-PENDING — addresses fabricated-regex-vs-empirical-DEVIATION-format defect): `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` (canonical shape; NOT the empirical `BUILD/TEST/SMOKE/FINDING/ERROR/DEFERRAL/DEVIATION` HH:MM-optional convention — `BRANCH=skip` sub-shape requires HH:MM + `rationale:` token, narrowing the parent convention for audit-quality). BRANCH-1's escape-hatch grep matches exactly this shape via regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+`. New prose-pin test asserts the canonical shape sentence is present.
3. `/commit-slice` SKILL.md `--do-commit` flag is removed and replaced by `--merge`: default (no flag) still generates message only; `--merge` runs `git add` + `git commit` on the current slice branch with the generated message, then `git checkout <default-branch> && git merge --no-ff slice/NNN-<name>` with a merge-commit message referencing the slice (default-branch resolved at runtime per AC #1), then `git branch -d slice/NNN-<name>` (local delete only; never `-D`, never push, never remote-delete). Pre-flight guardrails (post /critique B5 + M5 ACCEPTED-PENDING): refuse if stale `slice/*` branches exist (artefact of prior conflict-recovery); refuse if `git status --porcelain` returns non-empty before `git checkout <default-branch>`; require explicit `Confirm merge + delete? (yes/no)` user confirmation before `git branch -d`.
4. New audit `tools/branch_workflow_audit.py` (BRANCH-1) runs at `/build-slice` Step 6 pre-finish gate (post /critique B3 ACCEPTED-PENDING — replaces prior "Phase 6" framing): refuses if the current branch is the resolved default branch (master/main/trunk/etc.) OR if it does not match `slice/<slice-number>-<slice-name>` for the active slice, unless `build-log.md` Events contains a documented `BRANCH=skip` escape-hatch line conforming to the AC #2 canonical regex. CLI shape: `$PY -m tools.branch_workflow_audit <slice-folder>` with `--json` + `--root` flags mirroring `tools/critique_agent_drift_audit.py` pattern. 3 detection-mode unit tests + 1 escape-hatch acceptance test + 3 default-branch-resolution tests (symbolic-ref path + init.defaultBranch fallback path + neither-resolves STOP path).
5. `architecture/methodology-changelog.md` gets a v0.35.0 entry naming BRANCH-1 with its 3 sub-modes (build-time branch-create + commit-time `--merge` + audit-time pre-finish refusal); `architecture/decisions/ADR-019.md` is the new ADR (reversibility: cheap; supersedes=null; option (a) `/build-slice`-only v1 with explicit Limitations carveout for upstream-pipeline scope per /critique M-add-4 ESCALATED resolution); `architecture/shippability.md` gains row 21 with a runnable Command cell enumerating 14 invocation targets (post /critique M3 + M-add-1 ACCEPTED-FIXED canonical recount: 8 whole-file targets + 6 `::test_*` named targets); root `CLAUDE.md` "Brownfield rules" section gains a `Branch-per-slice` bullet; 3 stale-doc surfaces (`pipeline.md` L97, `tutorial.md` L750, `tutorial-site/Hybrid AI SDLC Pipeline.html` L583) get `--do-commit` → `--merge` updates (post /critique B2 ACCEPTED-PENDING — retracts prior "zero external consumers" claim). Bidirectional sha256 byte-equality tests pass for `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `skills/slice/SKILL.md` (existing — must stay PASSING) against their installed copies at `~/.claude/skills/<name>/SKILL.md`; CAD-1 (`agents/critique.md` untouched this slice — must stay byte-equal at slice-017 ship hash `f34c967eaaa34413`); PMI-1 (manifest includes new `branch_workflow_audit.py`); INST-1 (`tools/install_audit.py` canonical list enumerates the new audit).

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation per **TF-1** (`methodology-changelog.md` v0.13.0). Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

**Canonical test function names** (post /critique M-add-2 ACCEPTED-PENDING harmonization across TF-1 plan + verification plan + design.md Command cell — TPHD-1 sub-mode (a) same-fix-block discipline applied at this design rerun): every named test function below appears VERBATIM in all 3 surfaces (this table + Verification plan §4 + design.md L201 Command cell + shippability row 21).

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology-prose-pin | tests/methodology/test_build_slice_skill_branch_create.py | test_build_slice_skill_md_prerequisite_check_has_branch_state_sub_section | PASSING |
| 1 | methodology-prose-pin | tests/methodology/test_build_slice_skill_branch_create.py | test_build_slice_skill_md_specifies_slice_branch_name_pattern | PASSING |
| 1 | methodology-prose-pin | tests/methodology/test_build_slice_skill_branch_create.py | test_build_slice_skill_md_specifies_branch_escape_hatch_via_branch_skip_deviation | PASSING |
| 1 | methodology-prose-pin | tests/methodology/test_build_slice_skill_branch_create.py | test_build_slice_skill_md_specifies_runtime_default_branch_resolution | PASSING |
| 2 | methodology-prose-pin | tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py | test_build_slice_skill_md_step_7c_canonicalizes_branch_skip_deviation_line_shape | PASSING |
| 3 | methodology-prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_documents_merge_flag | PASSING |
| 3 | methodology-prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_removes_do_commit_flag | PASSING |
| 3 | methodology-prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete | PASSING |
| 3 | methodology-prose-pin | tests/methodology/test_commit_slice_skill_merge_flag.py | test_commit_slice_skill_md_specifies_pre_flight_guardrails | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_refuses_on_default_branch | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_accepts_slice_branch_matching_active_slice | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_refuses_slice_branch_with_wrong_number | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_accepts_escape_hatch_rationale_in_build_log_events | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_resolves_default_branch_via_symbolic_ref | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_falls_back_to_init_default_branch | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_stops_when_neither_symbolic_ref_nor_init_default_branch_resolves | PASSING |
| 4 | unit | tests/tools/test_branch_workflow_audit.py | test_branch_workflow_audit_warns_on_stale_slice_branch_from_prior_conflict | PASSING |
| 5 | methodology-prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_35_0_branch_1_entry_present_in_repo_and_installed | PASSING |
| 5 | methodology-prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_35_0_branch_1_entry_names_three_sub_modes_in_repo_and_installed | PASSING |
| 5 | methodology-prose-pin | tests/methodology/test_methodology_changelog.py | test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1 | PASSING |
| 5 | grep-verification | architecture/shippability.md | row 21 Command cell executes clean on slice/021 branch (no separate test_row_021_*.py file per slice-020 row-20 convention DEVIATION-1) | PASSING |
| 5 | methodology-prose-pin | tests/methodology/test_root_claude_md_branch_per_slice_rule.py | test_root_claude_md_has_branch_per_slice_bullet | PASSING |
| 5 | mini-CAD | tests/methodology/test_build_slice_skill_drift.py | test_build_slice_skill_md_in_repo_byte_equal_installed | PASSING |
| 5 | mini-CAD | tests/methodology/test_commit_slice_skill_drift.py | test_commit_slice_skill_md_in_repo_byte_equal_installed | PASSING |
| 5 | mini-CAD | tests/methodology/test_slice_skill_drift.py | test_slice_skill_md_in_repo_byte_equal_installed (existing — verify still PASSING after any cross-reference edits) | PASSING |
| 5 | PMI-1 | tests/methodology/test_plugin_manifest_audit.py | test_plugin_yaml_lists_branch_workflow_audit (extends existing audit) | PASSING |
| 5 | PMI-1 | tests/methodology/test_plugin_manifest_audit.py | test_plugin_yaml_version_matches_version_file_invariant (existing — verify still PASSING after 0.34.0 → 0.35.0 atomic bump) | PASSING |
| 5 | CAD-1 | tests/methodology/test_critique_agent_drift.py | test_critique_agent_drift_audit_clean_at_slice_021_ship | PASSING |
| 5 | INST-1 | tests/methodology/test_install_audit.py | test_install_audit_enumerates_branch_workflow_audit | PASSING |

## Verification plan

(Canonical test function names per TF-1 plan above — TPHD-1 sub-mode (a) all-3-surfaces harmonization at this design rerun.)

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `/build-slice` Prerequisite check `### Branch state` sub-section + canonical BRANCH=skip shape (AC #1 + AC #2) | `$PY -m pytest tests/methodology/test_build_slice_skill_branch_create.py tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py -v` — 5/5 PASS; manual: `git checkout <default-branch> && /build-slice` on a synthetic active-slice folder creates `slice/021-<name>` branch and switches to it; `git checkout other-branch && /build-slice` STOPs with branch-mismatch prompt; `git status --porcelain` non-empty before /build-slice STOPs with dirty-WT prompt |
| 2 | `/commit-slice --merge` semantics + pre-flight guardrails (AC #3) | `$PY -m pytest tests/methodology/test_commit_slice_skill_merge_flag.py -v` — 4/4 PASS; manual: on a finished synthetic slice on `slice/021-...`, `/commit-slice --merge` produces commit on slice branch + no-ff merge commit on default-branch + local branch safe-deleted (after explicit `Confirm merge + delete? (yes/no)`); `git log --graph --oneline` shows slice attribution preserved; with a stale `slice/<other-number>-*` branch present, `--merge` STOPs pre-flight before any state change |
| 3 | `tools/branch_workflow_audit.py` (BRANCH-1) — 8 unit tests (AC #4) | `$PY -m pytest tests/tools/test_branch_workflow_audit.py -v` — 8/8 PASS (3 detection-mode + 1 escape-hatch + 3 default-branch-resolution + 1 stale-slice-branch); manual: `git checkout <default> && $PY -m tools.branch_workflow_audit architecture/slices/slice-021-...` exits 1 with "refuses on default branch"; `git checkout slice/021-... && $PY -m tools.branch_workflow_audit ...` exits 0; with a `BRANCH=skip — rationale: <text>` line in build-log.md Events on master, audit exits 0 with `escape_hatch_used: true` |
| 4 | Vault propagation: changelog + ADR + shippability + CLAUDE.md + 3 stale-doc surfaces (AC #5) | `$PY -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_35_0_branch_1_entry_present_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_v_0_35_0_branch_1_entry_names_three_sub_modes_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1 tests/methodology/test_root_claude_md_branch_per_slice_rule.py tests/shippability/test_row_021_branch_workflow.py -v` — all PASS; `grep -F "--do-commit" pipeline.md tutorial.md tutorial-site/Hybrid\ AI\ SDLC\ Pipeline.html` returns 0 matches (all replaced with `--merge`). |
| 5 | Byte-equality + manifest + INST-1 (AC #5) | `$PY -m tools.critique_agent_drift_audit --repo-root .` PASS (CAD-1, vacuously — no edit this slice); `$PY -m tools.plugin_manifest_audit` PASS (PMI-1, with new audit tool enumerated); `$PY -m tools.install_audit` PASS (INST-1, with `branch_workflow_audit` in canonical list); `$PY -m pytest tests/methodology/test_slice_skill_drift.py tests/methodology/test_build_slice_skill_drift.py tests/methodology/test_commit_slice_skill_drift.py tests/methodology/test_critique_agent_drift.py::test_critique_agent_drift_audit_clean_at_slice_021_ship tests/methodology/test_install_audit.py::test_install_audit_enumerates_branch_workflow_audit -v` 5/5 PASS |

## Must-not-defer

- [ ] **CAD-1 invariant preserved**: `agents/critique.md` MUST NOT be touched this slice (Critic-agent content-equality discipline at slice-017 ship hash `f34c967eaaa34413`). Run `$PY -m tools.critique_agent_drift_audit --repo-root .` at pre-finish.
- [ ] **PMI-1 manifest updated**: `plugin.yaml` MUST enumerate the new `tools/branch_workflow_audit.py` script; `VERSION` and `~/.claude/ai-sdlc-VERSION` bumped to 0.35.0 atomically with `plugin.yaml.version`. Run `$PY -m tools.plugin_manifest_audit` at pre-finish.
- [ ] **INST-1 canonical list updated**: `tools/install_audit.py` skill/agent/tool inventory matches `plugin.yaml`. Run `$PY -m tools.install_audit` at pre-finish.
- [ ] **Mini-CAD bidirectional sha256 capture**: build-log.md Summary records sha256 hashes for `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `skills/slice/SKILL.md` (untouched — must stay at slice-020 ship hash `cc18b5a05c2220dd`), `agents/critique.md` (untouched — must stay at slice-017 ship hash `f34c967eaaa34413`), `architecture/methodology-changelog.md` at slice ship time. Forensic-capture N=16 → N=17 stable.
- [ ] **TPHD-1 3-surface plan-harmonization discipline** (per /critique M-add-3 ACCEPTED-PENDING vocabulary sweep): any fix-prose change to mission-brief AC, design.md TF-1 plan, or test function names must harmonize all 3 surfaces in the SAME fix block. Sub-mode (c) prerequisite-check defense-in-depth runs at `/build-slice` **Prerequisite check** (pre-existing — NOT "Phase 0"; per slice-017 ADR-016 canonical naming at methodology-changelog v0.32.0 L102).
- [ ] **SCPD-1 shippability consumer-reference propagation**: row 21 added to `architecture/shippability.md` BEFORE `/validate-slice` Step 5.5 catalog run; row references BRANCH-1 audit by ID + carries a runnable Command cell.
- [ ] **SCPD-1 single-source-of-truth on shippability row 21 Command cell** (per /critique M3 ACCEPTED-FIXED + M-add-1 ACCEPTED-FIXED canonical recount): row 21's Command cell MUST enumerate **14 enumerated invocation targets** (8 whole-file targets + 6 `::test_*` named-function targets) per design.md L201 post-fix shape. Incomplete Command cell silently regresses the catalog. Wiegers regression-guard coverage-symmetry watch-list N=9 cumulative (was N=7 + 2 NEW instances within slice-021 rerun per /critique-rerun B3-new).
- [ ] **BRANCH-1 bootstrap DEVIATION line pinned** (per /critique B4 ACCEPTED-PENDING): build-log.md Events MUST contain the canonical bootstrap line conforming to AC #2 shape: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip-bootstrap — rationale: ## Prerequisite check ### Branch state sub-section prose authored this slice; manual branch-create fired before sub-section exists on disk. RSAD-1 canonical bootstrap-reference instance #1.` BRANCH-1 audit's escape-hatch grep accepts this exact line via regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+`.
- [ ] **Pre-flight WT-loss guardrail** (per /critique M5 ACCEPTED-PENDING): `/commit-slice --merge` MUST verify `git status --porcelain` returns empty BEFORE `git checkout <default-branch>` — STOP on any non-empty output. Closes silent-WT-discard local-state-loss path 1.
- [ ] **Explicit branch-delete confirmation** (per /critique M5 ACCEPTED-PENDING): `/commit-slice --merge` MUST prompt `Confirm merge + delete? (yes/no)` before `git branch -d slice/NNN-<name>`. Closes unrecoverable-without-push local-state-loss path 2.
- [ ] **Default-branch resolution** (per /critique M1 ACCEPTED-PENDING): `tools/branch_workflow_audit.py` and `/commit-slice --merge` MUST NOT hard-code `master`/`main`. Resolve via `git symbolic-ref refs/remotes/origin/HEAD` → strip `refs/remotes/origin/` prefix; fallback to `git config init.defaultBranch`; STOP if neither resolves.
- [ ] **Default-branch resolution canonical-phrase pin across N=3 surfaces** (per /critique-rerun M2-new ACCEPTED-FIXED + Fowler rule-of-three + slice-019 LAYER-EVID-1 N-surface schema-pin precedent): the resolution logic appears at 3 sites — `tools/branch_workflow_audit.py` (Python helper `_resolve_default_branch()`), `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section (prose-heuristic), `skills/commit-slice/SKILL.md` Step 5 `--merge` flow (prose-heuristic). All 3 surfaces MUST name `git symbolic-ref refs/remotes/origin/HEAD` AND `git config init.defaultBranch` in identical canonical form. Helper-extraction asymmetry (Python helper vs prose-heuristic) is unavoidable; cross-surface canonical-phrase pin closes the rule-of-three coverage at the prose level.
- [ ] **`--merge` pre-flight stale-slice-branch guardrail** (per /critique B5 ACCEPTED-PENDING option (c)): `/commit-slice --merge` MUST refuse to start if `git for-each-ref --format='%(refname)' refs/heads/slice/` returns any non-current `slice/*` branches (artefact of prior conflict-recovery state). Closes B5 merge-conflict-after-archive recovery gap by failing fast.
- [ ] **No silent `git push`, no `git push --force`, no remote-delete**: `--merge` is local-only. Pushing the merged default branch is a separate user-driven action; the skill MUST NOT push.
- [ ] **No `--no-verify`**: pre-commit hooks (drift-check etc.) run as configured; the skill MUST NOT bypass.
- [ ] **No `git branch -D`** (force-delete): the merge path uses `git branch -d` (safe-delete; refuses if unmerged). If `-d` refuses, the skill STOPs and reports — never escalates to `-D`.
- [ ] **No interactive rebase, no force-push, no merge-into-detached-HEAD**: only the no-ff merge-to-default-branch path is supported in v1.
- [ ] **Error path for "current branch is neither default-branch nor `slice/NNN-name`"**: STOP at `## Prerequisite check ### Branch state` and ask the user; never silently auto-create on top of an arbitrary branch.
- [ ] **Error path for "merge conflicts"**: if `--merge` hits a merge conflict, STOP, leave default-branch in conflicted state, instruct user to resolve manually; never auto-resolve, never abort silently. (Recovery flow itself deferred per /critique B5 ACCEPTED-PENDING option (c); v1 surfaces the limitation explicitly via design.md Limitations.)
- [ ] **Logging at every branch-state transition**: build-log.md Events records (a) `BRANCH-CREATE` event at `## Prerequisite check ### Branch state` sub-section invocation, (b) `BRANCH-COMMIT` event at `--merge` step 1, (c) `BRANCH-MERGE` event at `--merge` step 2 with merge-commit sha, (d) `BRANCH-DELETE` event at `--merge` step 3. Mirrors slice-018+ flight-recorder discipline.

## Out of scope

- **Remote push / remote-branch creation / GitHub PR integration**: `--merge` is purely local — `git push` is a separate user-driven action. PR-based review is a candidate for a follow-on slice (`add-remote-pr-flow-to-commit-slice-merge`).
- **Branch prefix variation by slice type** (e.g., `feat/`, `fix/`, `bugfix/` based on BFRD-1 classification): defer; v1 uses uniform `slice/NNN-<name>` namespace. If repeated user-friction surfaces, a later slice can layer prefix-by-classification on top.
- **Squash-merge vs no-ff merge-commit configurability**: v1 uses `--no-ff` (merge commit) only — preserves slice attribution as a discrete merge node, easier to revert. Squash is a future toggle.
- **Branch-per-`/repro`**: `/repro` produces a failing test that hands off to `/slice` then `/build-slice`. The branch is created at `/build-slice` Prerequisite check; `/repro` itself stays on master and writes its test there. If this turns out painful, a future slice can move branch-create earlier.
- **Auto-stash of uncommitted changes during Prerequisite check `### Branch state`**: if working tree is dirty at the Prerequisite check sub-section, STOP and ask user to commit or stash. Don't auto-stash silently (loses user intent).
- **Switching back to master at slice end without `--merge`**: if the user runs `/commit-slice` (no flag) and copy-pastes the message, they stay on the slice branch. Switching back is their decision. Skill prose mentions this as an explicit hand-off note, but no automation.
- **History rewriting on the slice branch** (interactive rebase, amend-then-merge): v1 forbids; the slice branch is append-only commits only. A future slice could add `--squash` to compress build-log noise into one commit before merging.
- **Methodology-changelog v0.35.0 entry's `Sub-mode (a)/(b)/(c)` cross-application to other audits**: BRANCH-1 is THIS slice's surface; promotion of the 3-sub-mode pattern to a generic class is /critic-calibrate territory at slice-024+.

## Dependencies

- Prior slices:
  - [[slice-001-diagnose-orchestration-fix]] — first `*-fix` suffix witness, anchors the "slice naming has no semantic meaning at workflow layer" lesson; branch-per-slice doesn't depend on classification.
  - [[slice-007-codify-cad-1]] — establishes the byte-equality-between-in-repo-and-installed pattern (CAD-1); slice-021 extends this discipline to 2 more skill surfaces (build-slice, commit-slice) via mini-CAD tests.
  - [[slice-010-codify-mini-cad-for-slice-skill]] — first mini-CAD instance for a skill SKILL.md (slice/SKILL.md); slice-021 replicates this exact pattern for build-slice + commit-slice.
  - [[slice-013-codify-rsad-1]] — recursive-self-application discipline; slice-021 will self-apply BRANCH-1 (this slice's own work MUST run on `slice/021-...`, will be merged back to master via `--merge` as the canonical reference instance #1).
  - [[slice-020-codify-bug-fix-repro-prelude-at-slice]] — most recent methodology slice; established the pattern of single-rule -D-suffix codification with 3 sub-modes + ADR + shippability row + methodology-changelog atomic version bump.
- Vault refs:
  - [[skills/build-slice/SKILL.md]] — `## Prerequisite check ### Branch state` sub-section addition target + Step 7c canonical BRANCH=skip shape + Step 6 pre-finish gate audit invocation
  - [[skills/commit-slice/SKILL.md]] — `--merge` replacement target
  - [[skills/slice/SKILL.md]] — only touched if Step 3c needs a cross-reference to BRANCH-1
  - [[architecture/decisions/ADR-019]] — new ADR
  - [[architecture/methodology-changelog.md]] — v0.35.0 entry
  - [[architecture/shippability.md]] — row 21
  - [[architecture/build-checks.md]] — potential evergreen rule promotion at /reflect Step 5b if pattern recurs
  - [[CLAUDE.md]] — root project CLAUDE.md "Brownfield rules" section
  - [[plugin.yaml]] — new audit script enumeration
  - [[tools/install_audit.py]] — INST-1 canonical list
- Risk register: no entry retired (R-1, R-2, R-3 all untouched). R-1 and R-2 remain stale across 20 slices.

## Mid-slice smoke gate

At ~50% of build (after the SKILL.md edits to both `/build-slice` and `/commit-slice` are drafted but BEFORE the audit tool is written), confirm slice branch state and prose-pin coverage:

```bash
# 1. Confirm working tree + branch state.
git status
git branch --show-current
# Expected: slice/021-add-feature-branch-workflow-at-build-and-commit-slice
#
# If the output is the repo's default branch (resolved via:
#   git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
# with fallback to: git config init.defaultBranch):
# STOP and fire the bootstrap branch-create per "Self-application of BRANCH-1"
# caveat 1 BEFORE running the prose-pin tests. Record as canonical DEVIATION line
# in build-log.md Events using the EXACT shape pinned in Must-not-defer:
#   "<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip-bootstrap — rationale:
#    ## Prerequisite check ### Branch state sub-section prose authored this slice;
#    manual branch-create fired before sub-section exists on disk.
#    RSAD-1 canonical bootstrap-reference instance #1."
# Then resume the smoke gate.

# 2. Prose-pin smoke: just the build-slice + commit-slice prose-pin tests, no full suite
$PY -m pytest \
  tests/methodology/test_build_slice_skill_branch_create.py \
  tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py \
  tests/methodology/test_commit_slice_skill_merge_flag.py \
  -v
```

**Expected**: 9/9 PASS (4 build-slice branch-create + 1 step-7c canonical shape + 4 commit-slice --merge). The prose-pin tests verify the SKILL.md prose changes are byte-stable and contain the canonical phrases pinning the new behavior. If any fail: STOP, diagnose, don't continue to audit-tool work.

If smoke fails (test imports fail, prose-pin asserts fail): the skill prose isn't load-bearing yet — revise before building the audit tool that depends on it.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] All 20 must-not-defer items addressed (CAD-1, PMI-1, INST-1, mini-CAD bidirectional, TPHD-1, SCPD-1 propagation, SCPD-1 single-source-of-truth on 14-target Command cell, BRANCH-1 bootstrap DEVIATION pinned, WT-loss guardrail, branch-delete confirmation, default-branch resolution, default-branch resolution canonical-phrase pin across N=3 surfaces, stale-slice-branch guardrail, no-push, no-no-verify, no-force-delete, no-history-rewrite, branch-state-error-paths, merge-conflict-error-path, branch-state-transition-logging) — per /critique-rerun M3-new ACCEPTED-FIXED count harmonization (was 18; corrected to 20 = 19 original + 1 from M2-new canonical-phrase pin).
- [ ] `/drift-check` passes (vault and code aligned)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints / `git push` calls in skill prose
- [ ] **BRANCH-1 self-application** (per RSAD-1 discipline): this slice's own commits live on `slice/021-add-feature-branch-workflow-at-build-and-commit-slice` and will be merged via `/commit-slice --merge` as canonical **bootstrap-reference** instance #1 (NOT canonical reference instance #1 per /critique m2 ACCEPTED-FIXED — softened from canonical because slice cannot self-apply the rule it is itself authoring; bootstrap is a distinct class); build-log.md Events records the 4 branch-state transitions (CREATE, COMMIT, MERGE, DELETE) for forensic capture plus the bootstrap DEVIATION line.
- [ ] **TF-1 audit** (`tools/test_first_audit.py --strict-pre-finish`) PASSES with all **30 TF-1 rows** at PASSING (29 rows in Test-first plan table + 1 row reserved for the bootstrap DEVIATION grep-verification at AC #1) — per /critique-rerun B3-new ACCEPTED-FIXED canonical recount (was 28).
- [ ] **WIRE-1 wiring matrix** in `design.md` includes a row for `tools/branch_workflow_audit.py` (consumer entry point: `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section + Step 6 pre-finish gate; consumer test: `tests/tools/test_branch_workflow_audit.py`).
- [ ] **BC-1 build-checks audit** runs clean (no Critical violations).
- [ ] **PMI-1 + INST-1** atomic with `plugin.yaml.version 0.34.0 → 0.35.0` + `VERSION` + `~/.claude/ai-sdlc-VERSION` bumps.
- [ ] **Mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition** (per slice-018+ pattern): the new build-slice + commit-slice mini-CAD tests must demonstrate the byte-equality before-and-after transition on the slice's own SKILL.md edits; existing slice/SKILL.md mini-CAD test stays PASSING.
- [ ] **Shippability catalog** runs 21/21 PASS at `/validate-slice` Step 5.5 (was 20/20 at slice-020 ship); row 21 Command cell enumerates exactly **14 invocation targets** per M-add-1 canonical count.
(Pre-finish-gate item 11 RETIRED per /critique-rerun M1-residual ACCEPTED-FIXED option (a) — empirical falsification at /design-slice rerun time + no mechanical check + "retroactively" contradicts TPHD-1 same-fix-block discipline. Replaced with watch-list entry recorded in `slices/_index.md` Aggregated lessons at /reflect time: *"Wiegers regression-guard coverage-symmetry watch-list N=9 cumulative; promotion to Dim 9 sub-clause at /critic-calibrate ELEVATED to slice-022 (from slice-024+) per /critique-rerun observation: 6 fresh RSAD instances within slice-021's own redesign + /critique rerun caught 5 more within the rerun's own fix-block — class is empirically the dominant recurrence class for codification slices; no slice-local mitigation in v1."*)
