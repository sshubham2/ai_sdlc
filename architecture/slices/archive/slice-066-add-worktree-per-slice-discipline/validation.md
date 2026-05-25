# Validation: Slice 066 add-worktree-per-slice-discipline

**Date**: 2026-05-24
**Result**: PASS

## Per-criterion results

### AC1: `/build-slice` prereq creates worktree at `<main-parent>/<main-name>-wt/slice-NNN-<name>` (replaces `git checkout -b`)
- **Status**: PASS
- **Evidence**:
  - Prose-pin tests PASS:
    ```
    $PY -m pytest tests/methodology/test_build_slice_skill.py::test_branch_state_subsection_invokes_git_worktree_add tests/methodology/test_build_slice_skill.py::test_branch_state_subsection_uses_sibling_wt_path_shape tests/methodology/test_build_slice_skill.py::test_branch_state_subsection_does_not_use_bare_checkout_b -q
    → 3 passed in 0.05s
    ```
  - Direct read of `skills/build-slice/SKILL.md:42-67` confirms the Branch state sub-section invokes `git worktree add "$wt_base/slice-NNN-<slice-name>" -b slice/NNN-<slice-name> "$default"` + `cd "$wt_base/slice-NNN-<slice-name>"`; `git checkout -b slice/` is absent from this sub-section.
  - OSDG-1 drift test PASS (`test_build_slice_skill_drift.py` 1/1 passed); installed `~/.claude/skills/build-slice/SKILL.md` content-equal modulo line endings.
- **Notes**: BRANCH-2 sub-mode (a) partial-supersedes ADR-019 sub-mode (a). Slice-066 itself runs WITHOUT worktree mode (bootstrap; canonical `WORKTREE=skip-bootstrap` line in build-log.md Events). Every slice from slice-067 onward inherits a self-gating BRANCH-2 audit.

### AC2: `/commit-slice --merge` + `/commit-slice --sync-after-pr` tear worktree down post-merge in order `git worktree remove` BEFORE `git branch -d`
- **Status**: PASS
- **Evidence**:
  - Prose-pin tests PASS:
    ```
    $PY -m pytest tests/methodology/test_commit_slice_skill_merge_flag.py::test_merge_mode_invokes_git_worktree_remove_post_merge tests/methodology/test_commit_slice_skill_merge_flag.py::test_teardown_order_pins_remove_before_branch_delete tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py::test_sync_after_pr_mode_invokes_git_worktree_remove_post_merge -q
    → 3 passed in 0.04s
    ```
  - Direct read of `skills/commit-slice/SKILL.md`:
    - Step 5b sub-step 5 inserted: idempotent worktree-remove guard (LOG-and-skip if absent; covers slice-066 bootstrap + future WORKTREE=skip slices) followed by `git worktree remove "$wt_path"`.
    - Step 5b sub-step 6 (existing): `git branch -d slice/NNN-<name>` with order-load-bearing prose.
    - Step 5d sub-step 5 inserted: same idempotent guard + `git worktree remove`.
  - OSDG-1 drift test PASS (`test_commit_slice_skill_drift.py` 1/1 passed); forward-sync to `~/.claude/skills/commit-slice/SKILL.md` clean.
- **Notes**: `--push` UNCHANGED (worktree stays alive through PR-review window; mirrors slice branch lifecycle). Order-load-bearing per [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree) — `git branch -d` refuses on a branch checked out in a worktree.

### AC3: `tools/branch_workflow_audit.py` gains 4 new violation kinds + 4 new helpers + WORKTREE=skip escape-hatch grammar
- **Status**: PASS
- **Evidence**:
  - All 16 audit tests PASS:
    ```
    $PY -m pytest tests/methodology/test_branch_workflow_audit.py -q
    → 16 passed in 8.69s
    ```
  - 4 new violation kinds present (`worktree-not-registered`, `worktree-cwd-mismatch`, `worktree-path-shape-violation`, `worktree-skip-malformed`) — verified by grep on `tools/branch_workflow_audit.py`.
  - 5 new helpers present (`_is_repo_root_a_worktree`, `_resolve_expected_worktree_path`, `_paths_equivalent`, `_worktree_registered`, `_slice_branch_in_worktree`) + 1 new escape-hatch helper (`_check_worktree_skip_line`).
  - New `_WORKTREE_SKIP_LINE_RE` regex mirrors `_BRANCH_SKIP_LINE_RE`'s shape; cross-spec parity test PASS (`test_worktree_skip_grammar_pinned_across_three_surfaces`).
  - BRANCH-2 audit run from inside slice-066 (main-tree mode, slice/066-... branch, WORKTREE=skip-bootstrap Events line) → exit 0 clean: `Branch workflow audit: clean. On branch 'slice/066-add-worktree-per-slice-discipline' (matches expected 'slice/066-add-worktree-per-slice-discipline').`
- **Notes**: BRANCH-2 EXTENDS BRANCH-1 sub-mode (c) audit-time refusal in place via the 4 new violation kinds — does NOT supersede sub-mode (c).

### AC4: ADR-063 mints BRANCH-2 + methodology-changelog v0.68.0 + CLAUDE.md L32 rewrite + 5-part PMI-1 bump 0.67.0 → 0.68.0
- **Status**: PASS
- **Evidence**:
  - ADR-063 frontmatter + body tests PASS (3/3):
    ```
    $PY -m pytest tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py -q
    → 3 passed in 0.04s
    ```
    Asserts `supersedes: ADR-019` (NOT ADR-021); ADR-019 unmodified (append-only invariant held across N=2 supersessions: ADR-020 sub-mode (b), ADR-063 sub-mode (a)); ADR-021 anti-anchor (verifies ADR-021 is utf8-stdout-1, unrelated).
  - methodology-changelog v0.68.0 entry-pin tests PASS (2/2 — BC-PROJ-10 paired entry-pin):
    ```
    $PY -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_68_0_branch_2_entry_present_in_repo tests/methodology/test_methodology_changelog.py::test_v_0_68_0_branch_2_shippability_consumer_propagation -q
    → 2 passed in 0.05s
    ```
  - CLAUDE.md L32 rewrite test PASS:
    ```
    $PY -m pytest tests/methodology/test_root_claude_md_branch_per_slice_rule.py -q
    → 4 passed in 0.05s
    ```
    Asserts: "Worktree-per-slice" present; "BRANCH-2" cited; "ADR-063" cited; "v0.68.0" cited; historical anchor "Branch-per-slice" preserved.
  - 5-part PMI-1 atomic bump 0.67.0 → 0.68.0 verified via PMI-1 audit:
    ```
    $PY -m tools.plugin_manifest_audit
    → PMI-1 plugin manifest audit: clean. 26 skill(s), 6 agent(s), 28 tool(s); version 0.68.0.
    ```
    All 5 legs: `VERSION`=0.68.0 ✓; `plugin.yaml.version`=0.68.0 ✓; `pyproject.toml [project].version`=0.68.0 ✓; `## v0.68.0` header in methodology-changelog.md ✓; installed `~/.claude/ai-sdlc-VERSION`=0.68.0 ✓ (AVFS-1 PASS).
  - CLAUDE.md edit + shippability row #66 = separate BC-PROJ-9 / BC-PROJ-10 consumer-propagation surfaces (NOT PMI-1 parts; corrected per slice-066 /build-slice Phase A Builder-self-catch).
- **Notes**: ADR-063 is the N=2 application of the slice-022 ADR-020 partial-supersession encoding pattern; ADR-019 stays unmodified across N=2 partial supersessions per append-only rule.

### AC5: R-17 risk-register entry transitions `mitigating` → `retired` with slice-066 citation
- **Status**: PASS
- **Evidence**:
  - R-17 retirement tests PASS (2/2):
    ```
    $PY -m pytest tests/methodology/test_r17_retirement.py -q
    → 2 passed in 0.97s
    ```
  - Direct read of `architecture/risk-register.md:284-298` confirms:
    - `**Status**: retired` (was `mitigating` pre-slice-066)
    - `**Retired**: slice-066-add-worktree-per-slice-discipline (2026-05-24; ADR-063 / BRANCH-2 / methodology v0.68.0)` line
    - Retirement paragraph naming candidate-fix-(b) closure + acknowledging candidate-fix-(a) declined as redundant defense-in-depth per ADR-063 §"Options considered" option 3
  - Risk-register audit:
    ```
    $PY -m tools.risk_register_audit architecture/risk-register.md --filter-status open --json --top 10
    → R-17 absent from open-filter output (open count: 2 — R-13 + R-2 unchanged)
    ```
- **Notes**: R-17 candidate-fix-(b) verbatim from `risk-register.md:295` shipped; uncommitted-slice-A-WIP-contaminates-slice-B class closed structurally via worktree filesystem isolation.

## Multi-instance validation

**Required?**: no — methodology-internal tooling slice with no multi-user / multi-device / multi-account surface. The worktree discipline DOES enable future multi-session parallel-slice work (slice-067/068/069 nominees), but slice-066 itself ships the foundational mechanics, not the parallelism.

**Result**: not-applicable

**Evidence**: mission-brief.md Out of scope explicitly defers Slice A (parallel-slice queue file) / Slice B (claim state machine) / Slice D (rebase + conflict discipline) to nominated sibling slices.

## Reality surprises

- **WS-1 audit has the R-7 silent-default-off class bug TF-1 fixed via TFFL-1** (slice-034). When mission-brief frontmatter has `**Walking-skeleton**: true  <!-- comment -->`, WS-1's anchored regex breaks → reports "not enabled" → silently default-off (gate vacuously passes). The same trailing-comment pattern TF-1 supports broke WS-1. **Builder self-catch #11** during /validate-slice Step 5c. Workaround applied: removed HTML comments from frontmatter. **`/critic-calibrate` candidate for slice-067+**: extend TFFL-1's fix (relaxed anchored regex + value-agnostic field-present malformed branch) to WS-1 + ETC-1 audits. N=2 in this class so far (TF-1 retired at slice-034 / R-7; WS-1 now witnessed N=1).

- **APED-1 for new audit predicate is structurally exercisable on the slice's own self-test** — slice-066's `tools/branch_workflow_audit.py` worktree-mode audit was end-to-end exercised via 8 tests using real `tmp_path` + real git subprocess; the audit's predicates aren't merely unit-tested but exercised against real `.git` file shapes, real `git worktree list --porcelain` output, real `_paths_equivalent` Windows-path-comparison. Closes the slice-064 / slice-065 advisory-feedback-loop pattern that surfaced "byte-identical regex inheritance still needs empirical demonstration on canonical sample" (M-add-5 from /critique-review).

- **Code-Critic surfaced 2 Majors + 4 minors deferred to slice-067+ bundled cleanup** per CRSI-1 v1 advisory + slice-064/065 precedent. Most consequential: M1 (`_is_repo_root_a_worktree` walks off filesystem on shallow gitdir; 2-line guard fix) + M2 (SKILL.md `wt_base` from `$(pwd)` diverges from audit's `.git`-ancestor walk; `git rev-parse --show-toplevel` fix). See `code-review.md` Disposition section.

## Shippability regressions

None. Shippability runner exit 0:
```
$PY -m tools.shippability_runner architecture/shippability.md
→ Shippability catalog run: 66 row(s), 66 PASS, 0 FAIL
```

All 65 pre-existing rows PASS + new row #66 PASS (BRANCH-2 / ADR-063 / R-17 traceability axis verified per BCR-1).

## Layered safety checks (VAL-1)

```
$PY -m tools.validate_slice_layers --slice architecture/slices/slice-066-add-worktree-per-slice-discipline --changed-files <16 in-scope files> --imports-allowlist tests
→ VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted). Clean — both layers passed.
```

## Walking-skeleton audit (WS-1)

```
$PY -m tools.walking_skeleton_audit architecture/slices/slice-066-add-worktree-per-slice-discipline --strict-pre-finish
→ Walking-skeleton audit: clean. 5 layer(s) — EXERCISED=5, PENDING=0.
```

All 5 layers EXERCISED:
1. Skill prose `skills/build-slice/SKILL.md` Branch-state sub-section — prose-pin tests pass
2. Skill prose `skills/commit-slice/SKILL.md` --merge + --sync-after-pr — order-pin tests pass
3. Audit `tools/branch_workflow_audit.py` worktree-mode acceptance — 16 audit tests pass on real git tempdirs
4. Git plumbing `git worktree add` / `git worktree remove` / `git worktree list --porcelain` — exercised by audit tests on real tempdirs
5. Vault ADR-063 + methodology-changelog v0.68.0 + CLAUDE.md edit + R-17 retirement — all audits clean

## Pipeline position

- **predecessor**: `/code-review`
- **successor**: `/reflect`
- **auto-advance**: true
- **on-clean-completion**: validation.md written with aggregate Result: PASS; auto-advance to `/reflect`.
