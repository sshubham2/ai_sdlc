# Slice 066: add-worktree-per-slice-discipline

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-17 (mitigating → retired) — `tools/branch_workflow_audit.py` gains the missing pre-create-cleanliness backstop via worktree-isolation; the candidate fix (b) named verbatim at `risk-register.md:295`. (BRANCH-1 was minted by [[ADR-019]], not ADR-021 — the project's actual ADR-021 is utf8-stdout-1, unrelated to branch discipline. Slice-066 partial-supersedes ADR-019 sub-mode (a) only; sub-mode (b) was already partial-superseded by ADR-020.)
**Test-first**: true
**Walking-skeleton**: true
**Exploratory-charter**: false

## Intent

Replace `/build-slice`'s `git checkout -b slice/NNN-<name>` on the main working tree with `git worktree add ../<repo>-wt/slice-NNN-<name> -b slice/NNN-<name> <default>`, so every slice runs in its own filesystem-isolated worktree. `/commit-slice --merge` and `/commit-slice --sync-after-pr` tear the worktree down post-merge alongside branch deletion. The current `BRANCH-1` discipline ([[methodology-changelog.md#v0.35.0]] + ADR-021) is superseded by `BRANCH-2` (worktree-per-slice + branch). This **retires R-17** explicitly — uncommitted slice-A WIP can no longer contaminate slice-B because slice-B's filesystem is a physically distinct worktree.

This slice is **foundational** for the user's parallel-slice-queue vision (slices A/B/D nominated post-066). Without worktrees, parallelism is a paper feature — two sessions sharing one working tree corrupt each other on the first `checkout -b`. This slice makes parallelism *physically possible*; the queue file + claim semantics + rebase discipline layer on top.

## Acceptance criteria

1. `/build-slice` `## Prerequisite check ### Branch state` sub-section creates a git worktree at `../<repo-name>-wt/slice-NNN-<name>` (sibling-directory convention) with the slice branch checked out, replacing the current `git checkout -b` on the main tree; SKILL.md prose rewritten + a prose-pin test asserts the new worktree-create invocation literal (`git worktree add` + the sibling-path shape) and the absence of the bare `git checkout -b slice/` pattern in that sub-section.
2. `/commit-slice --merge` (and `/commit-slice --sync-after-pr`) tears the worktree down post-merge in the order `cd <main-tree> → git worktree remove <wt-path> → git branch -d slice/NNN-<name>` (worktree-remove BEFORE branch-delete because the worktree pins its branch); SKILL.md prose updated for both modes + prose-pin tests asserting the teardown invocations + a test asserting the order constraint is documented.
3. `tools/branch_workflow_audit.py` accepts the new worktree path shape (cwd matches `<wt-base>/slice-NNN-<name>` AND the slice is registered via `git worktree list --porcelain`); the existing branch-name + default-branch-resolution checks are preserved; canonical `WORKTREE=skip — rationale: <text>` escape-hatch line shape (mirrors `BRANCH=skip` per slice-021) is honoured in `build-log.md` Events; regression tests cover accept-worktree-path / reject-bare-main-tree-with-slice-branch / accept-skip-line.
4. ADR-063 mints **BRANCH-2** (worktree-per-slice + branch), supersedes **ADR-019** (BRANCH-1 — sub-mode (a) build-time branch-create only; sub-mode (b) was already partial-superseded by ADR-020 at slice-022 and remains so; sub-mode (c) audit-time pre-finish refusal is EXTENDED in place via 4 new violation kinds, not superseded) via the slice-022 ADR-020 partial-supersession encoding pattern (`supersedes: ADR-019` frontmatter slot + body-scope enumeration; this is the N=2 application of the pattern in this codebase, after slice-022 ADR-020 partial-superseding the same ADR-019 sub-mode (b)); `methodology-changelog.md` v0.68.0 entry with `Rule reference: BRANCH-2`; CLAUDE.md "Branch-per-slice" paragraph rewritten to "Worktree-per-slice + branch" with BRANCH-2 cite; **5-part PMI-1 atomic bump** 0.67.0 → 0.68.0 — canonical 5 parts per slice-063/064 anchor: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## v0.68.0` header in `methodology-changelog.md` + installed `~/.claude/ai-sdlc-VERSION` (corrected from rev-1's "VERSION + plugin.yaml + methodology-changelog + CLAUDE.md cite + shippability row" per slice-066 /build-slice Phase A Builder-self-catch — CLAUDE.md edits + shippability row are SEPARATE consumer-propagation surfaces per **BC-PROJ-9** 5-inventory fan-out + **BC-PROJ-10** paired entry-pins, NOT PMI-1 parts).
5. R-17 risk-register entry transitions `**Status**: mitigating` → `**Status**: retired` with a `**Retired**: slice-066-add-worktree-per-slice-discipline (2026-05-24; ADR-063 / BRANCH-2 / methodology v0.68.0)` line; the slice-066 entry verifies on the real register via `$PY -m tools.risk_register_audit ... --filter-status open --json` no longer listing R-17 post-fix.

## Test-first plan

Per **TF-1** ([[methodology-changelog.md#v0.13.0]]). Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | regression | tests/methodology/test_build_slice_skill.py | test_branch_state_subsection_invokes_git_worktree_add | PASSING |
| 1 | regression | tests/methodology/test_build_slice_skill.py | test_branch_state_subsection_uses_sibling_wt_path_shape | PASSING |
| 1 | regression | tests/methodology/test_build_slice_skill.py | test_branch_state_subsection_does_not_use_bare_checkout_b | PASSING |
| 2 | regression | tests/methodology/test_commit_slice_skill_merge_flag.py | test_merge_mode_invokes_git_worktree_remove_post_merge | PASSING |
| 2 | regression | tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py | test_sync_after_pr_mode_invokes_git_worktree_remove_post_merge | PASSING |
| 2 | regression | tests/methodology/test_commit_slice_skill_merge_flag.py | test_teardown_order_pins_remove_before_branch_delete | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_accepts_cwd_in_worktree_sibling_path | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_accepts_worktree_registered_via_git_worktree_list_porcelain | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_rejects_main_tree_cwd_when_worktree_registered_elsewhere | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_accepts_invocation_from_inside_worktree_with_relative_slice_folder | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_emits_worktree_path_shape_violation_on_non_canonical_wt_path | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_honours_canonical_worktree_skip_rationale_line | PASSING |
| 3 | unit | tests/methodology/test_branch_workflow_audit.py | test_emits_worktree_skip_malformed_on_off_canonical_line | PASSING |
| 3 | regression | tests/methodology/test_branch_workflow_audit.py | test_worktree_skip_grammar_pinned_across_three_surfaces | PASSING |
| 4 | regression | tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py | test_adr_063_present_with_supersedes_adr_019_frontmatter | PASSING |
| 4 | regression | tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py | test_adr_019_unmodified_per_append_only_rule | PASSING |
| 4 | regression | tests/methodology/test_methodology_changelog.py | test_v_0_68_0_branch_2_entry_present_in_repo | PASSING |
| 4 | regression | tests/methodology/test_methodology_changelog.py | test_v_0_68_0_branch_2_shippability_consumer_propagation | PASSING |
| 4 | regression | tests/methodology/test_root_claude_md_branch_per_slice_rule.py | test_branch_per_slice_paragraph_rewritten_to_worktree_per_slice | PASSING |
| 5 | regression | tests/methodology/test_r17_retirement.py | test_r17_status_is_retired_post_slice_066 | PASSING |
| 5 | regression | tests/methodology/test_r17_retirement.py | test_r17_absent_from_risk_register_audit_filter_status_open | PASSING |

## Architectural layers exercised

Per **WS-1** ([[methodology-changelog.md#v0.15.0]]). Walking-skeleton: the slice itself exercises every layer of the build→commit worktree chain end-to-end on real git state.

| # | Layer | Component | Verification | Status |
|---|-------|-----------|--------------|--------|
| 1 | Skill prose | `skills/build-slice/SKILL.md` Branch-state sub-section | Worktree invocation literal present + prose-pin tests pass | EXERCISED |
| 2 | Skill prose | `skills/commit-slice/SKILL.md` --merge + --sync-after-pr | Worktree-teardown invocations present + order-pin tests pass | EXERCISED |
| 3 | Audit | `tools/branch_workflow_audit.py` worktree-mode acceptance | Audit run from a real worktree (the slice's own) exits 0; from main-tree-with-slice-branch exits non-zero | EXERCISED |
| 4 | Git plumbing | `git worktree add` / `git worktree remove` / `git worktree list --porcelain` | The slice's own /build-slice creates `../ai_sdlc-wt/slice-066-add-worktree-per-slice-discipline` worktree; `git worktree list` shows it | EXERCISED |
| 5 | Vault | ADR-063 + methodology-changelog v0.68.0 + CLAUDE.md edit + R-17 retirement | `$PY -m tools.risk_register_audit ... --filter-status open --json` no longer lists R-17; PMI-1 audit clean post-bump | EXERCISED |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `/build-slice` creates worktree on slice start | (a) Prose-pin tests above PASS; (b) sandbox dogfood — manually run the prerequisite-check on a throwaway slice folder and confirm `git worktree list --porcelain` shows the new worktree at `../ai_sdlc-wt/slice-XXX-throwaway`; (c) the slice-066 build itself is a dogfood (Bootstrap-reference instance) — see Bootstrap clause below. |
| 2 | `/commit-slice --merge` tears down post-merge | (a) Prose-pin tests above PASS; (b) sandbox dogfood — manually merge a throwaway slice branch back to default and confirm both `git worktree list --porcelain` no longer shows it AND `git branch --list slice/XXX-*` is empty AND the worktree directory is gone from disk; (c) slice-066's own merge at /commit-slice --merge demonstrates teardown on a real slice. |
| 3 | `branch_workflow_audit.py` accepts worktree mode | `$PY -m tools.branch_workflow_audit` run from inside `../ai_sdlc-wt/slice-066-add-worktree-per-slice-discipline` exits 0; same audit run from the main `ai_sdlc/` checkout with HEAD on `slice/066-...` exits non-zero (the rejected case); the `WORKTREE=skip` escape-hatch test demonstrates the canonical line shape lets a deviating slice through. |
| 4 | ADR-063 + methodology-changelog v0.68.0 + CLAUDE.md + PMI-1 bump | `$PY -m tools.plugin_manifest_audit` exit 0 (version 0.68.0 matches plugin.yaml + VERSION); `$PY -m tools.methodology_changelog_forward_sync` exit 0 (v0.68.0 entry in repo + installed); CAD-1 + OSDG-1 drift audits exit 0 (CLAUDE.md change forward-synced where required); `tests/methodology/test_adr_063_*` PASS. |
| 5 | R-17 retired | `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --top 5` returns risks NOT including R-17 (current open set = R-13 + R-2 → unchanged); `$PY -m tools.risk_register_audit ... --filter-status retired --json` lists R-17 with `"retired": "slice-066-..."` line; `tests/methodology/test_r17_retirement.py` PASS. |

## Must-not-defer

- [ ] **Worktree-cleanup must run on /commit-slice success path AND on partial-failure path**: if merge succeeds but `git worktree remove` fails (locked / dirty / sub-process holding handle), surface a loud user-actionable message (`worktree-remove-failed: <wt-path>; manual cleanup required: git worktree remove --force <wt-path>`) — never silently leave an orphan worktree on disk, never swallow the error.
- [ ] **Audit STOPs if cwd is the main working tree but the slice branch is checked out**: a Claude that forgot to `cd` into the worktree must hit a loud refusal at `tools/branch_workflow_audit.py` Step 6 pre-finish — not a silent pass. The reject-bare-main-tree-with-slice-branch regression test pins this.
- [ ] **Bootstrap discipline (slice-066 only)**: per the slice-021 BRANCH-1 bootstrap precedent + slice-026 CRP-1 bootstrap-reference-instance pattern, slice-066 itself runs in a worktree **after** the SKILL.md edits land, NOT before — the slice cannot self-apply the worktree discipline at its own `## Prerequisite check ### Branch state` because that sub-section is what this slice authors. The canonical `WORKTREE=skip-bootstrap — rationale: slice-066 authors the worktree-create prose; bootstrap-reference instance #1` DEVIATION line documents the gap in `build-log.md` Events. Every slice from slice-067 onward inherits a self-gating BRANCH-2 audit.
- [ ] **`WORKTREE=skip — rationale: <text>` escape-hatch is honoured consistently across build + commit + audit**: the canonical line shape (Step 7c-pinned, mirroring `BRANCH=skip` from slice-021) is documented in build-slice SKILL.md + commit-slice SKILL.md + branch_workflow_audit.py, and a regression test asserts all three surfaces accept the same exact grammar (RPCD-1 / cross-spec parity).
- [ ] **Forward-sync to installed `~/.claude/skills/build-slice/SKILL.md` + `~/.claude/skills/commit-slice/SKILL.md`**: OSDG-1 in-repo↔installed content-equality forward-sync is mandatory for both edited skills (post-EOL-DRIFT-1 EOL-agnostic; per `tests/methodology/test_build_slice_skill_drift.py` + `tests/methodology/test_commit_slice_skill_drift.py`).
- [ ] **shippability.md row added** for the new audit contract (RPCD-1 / SCPD-1 consumer-reference propagation — every new audit rule propagates into the shippability catalog).
- [ ] **Input validation on worktree-path resolution**: refuse on (a) `<wt-base>` directory traversal (`..` segments past sibling), (b) wt-path matching the main repo path (would alias the main tree), (c) wt-path already exists as a non-worktree directory (would clobber on `git worktree add`), (d) wt-path parent directory is not writable or does not exist (surface git's stderr verbatim + actionable hint pointing at the deferred env-var override path — per slice-066 /critique M5 ACCEPTED-FIXED).
- [ ] **Path-comparison semantics MUST tolerate Windows case-insensitivity and treat junctions/symlinks as equivalent to their targets**: `_worktree_registered`'s path comparison uses `Path.resolve(strict=False)` on both sides + `samefile()` where both paths exist, with documented fallback to `os.path.normcase(os.path.realpath(...))` string equality where one side doesn't exist (the worktree-not-registered detection path). A regression-test fixture covers the symlink-equivalence case (skippable on non-Windows runners) — per slice-066 /critique B2 ACCEPTED-FIXED.
- [ ] **Logging at worktree create + worktree remove invocation sites** — both events visible in `build-log.md` Events so a post-incident forensic can reconstruct what happened.
- [ ] **Bootstrap discharge covers all three slice-066 skill invocations**: slice-066's own `/build-slice` Events line declares `WORKTREE=skip-bootstrap — rationale: slice-066 authors the worktree-create prose; bootstrap-reference instance #1`. `/validate-slice` runs the new audit unchanged — the audit's reject-bare-main-tree path honours the build-log `WORKTREE=skip` line and clean-exits. `/commit-slice --merge` invokes the post-edit commit-slice SKILL.md prose, which (per slice-066 /critique B5 ACCEPTED-FIXED) checks `git worktree list --porcelain | grep "slice/NNN-"` BEFORE attempting `git worktree remove`; if no worktree exists for the slice (the bootstrap case AND any future `WORKTREE=skip` slice), it LOGs `slice/NNN-<name> worktree absent — skip worktree-remove (BRANCH-1 bootstrap or WORKTREE=skip slice)` and proceeds to branch-delete. The idempotent guard makes the cleanup safe across the bootstrap window AND any future skip-slice without requiring three separate `WORKTREE=skip-bootstrap` lines.

## Out of scope

- **Slice A (parallel-slice queue file)**: `/slice` writing `architecture/slice-queue.md` with top-10 parallel-safe candidates and the graphify blast-radius-non-overlap computation — a separate next slice (`add-parallel-slice-queue-output`), depends on slice-066 only for the worktree mechanics (claim semantics need physical isolation).
- **Slice B (claim state machine)**: `slice-queue.md` `Claimed-by/-at/Force-claim` schema + `/slice --claim` + `/slice --force-claim` — a separate next slice (`add-slice-queue-claim-state-machine`), depends on Slice A.
- **Slice D (rebase + conflict discipline)**: `/commit-slice --merge` rebasing onto default before merge + structured-options ASK on conflict + new `/rebase-slice` step — a separate next slice (`add-rebase-and-conflict-discipline`), depends on slice-066 worktree mechanics. **Note**: slice-066 does NOT introduce rebase logic into `/commit-slice --merge`; the existing no-ff-merge contract from BRANCH-1 carries forward unchanged. Conflict handling becomes urgent only when parallel slices ship; defer to Slice D.
- **Worktree cleanup on `/commit-slice --push` (PR-based path)**: `--push` leaves the worktree alive because the PR isn't merged yet; `--sync-after-pr` (covered in AC2) is where the post-PR cleanup happens. The interactive `--push`-to-`--sync-after-pr` workflow is NOT changed by this slice.
- **Migration of in-progress slices**: there are zero active slices at slice-066 start (verified via `/pulse` + `architecture/slices/_index.md` `## Active` empty), so no migration scaffold is needed.
- **Worktree pruning / garbage-collection on stale worktrees**: out-of-band hygiene (`git worktree prune`) is not wired by this slice; defer if N=2 stale-worktree incidents emerge.
- **Cross-platform worktree-path quirks beyond Windows + POSIX**: only Windows (the project's primary dev env per `~/.claude/CLAUDE.md`) and POSIX paths via `pathlib.Path` are exercised; WSL / Cygwin / network drives are not in scope.
- **Touching `tools/critique_review_prerequisite_audit.py` / CRP-1**: independent prerequisite-class discipline, not worktree-aware; unchanged.

## Dependencies

- Prior slices: [[slice-021-add-feature-branch-workflow-at-build-and-commit-slice]] — the BRANCH-1 baseline (ADR-019) that this slice partial-supersedes via BRANCH-2; [[slice-022-redesign-commit-slice-for-pr-aware-flow]] — minted ADR-020 (the partial-supersession encoding pattern + the three-mode `/commit-slice` design this slice extends with worktree-teardown; ADR-020 already partial-supersedes ADR-019 sub-mode (b)); [[slice-026-enforce-critique-review-prerequisite]] — CRP-1 bootstrap-reference-instance precedent for "this slice authors prose it cannot self-apply at its own prerequisite-check".
- Vault refs: [[components/build-slice]], [[components/commit-slice]], [[components/branch_workflow_audit]], [[decisions/ADR-019]] (BRANCH-1, to be partial-superseded; sub-mode (a) only — sub-mode (b) already covered by ADR-020), [[decisions/ADR-020]] (3-mode `/commit-slice` taxonomy + partial-supersession encoding precedent), CLAUDE.md "Branch-per-slice" paragraph (at CLAUDE.md L32).
- Risk register: [[risk-register#R-17]] — the candidate fix (b) explicitly named; this slice retires it.
- Methodology-changelog: current VERSION 0.67.0 → 0.68.0; new RULE-ID `BRANCH-2`.

## Mid-slice smoke gate

At ~50% of build (after TF-1 plan rows for AC1 + AC3 flip to WRITTEN-FAILING, and after the first SKILL.md edit lands for AC1):

```bash
# Run the new prose-pin tests on the just-edited build-slice SKILL.md
$PY -m pytest tests/methodology/test_build_slice_skill.py::test_branch_state_subsection_invokes_git_worktree_add -xvs

# Sanity-check git worktree on a throwaway folder
git worktree add ../ai_sdlc-wt-smoke -b slice/smoke-test master
git worktree list --porcelain
git worktree remove ../ai_sdlc-wt-smoke
git branch -D slice/smoke-test
```

Expected: prose-pin test PASSES; worktree create/list/remove cycle completes without error; `git worktree list --porcelain` shows the smoke worktree mid-cycle then doesn't post-remove. If any step fails: STOP, diagnose (most likely: path-quoting on Windows, or stale `slice/smoke-test` branch from a prior smoke run — clean up + retry once).

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes (vault claims match code)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `$PY -m tools.test_first_audit --strict-pre-finish` exit 0 (all 21 TF-1 rows PASSING — 16 original + 1 cross-spec parity (B4 ACCEPTED-FIXED) + 3 audit call-shape rows (B3 ACCEPTED-FIXED) + 1 BC-PROJ-10 paired-entry-pin shippability_consumer_propagation row (slice-066 /build-slice Phase B Builder-self-catch))
- [ ] `$PY -m tools.walking_skeleton_audit --strict-pre-finish` exit 0 (all 5 layers EXERCISED)
- [ ] `$PY -m tools.plugin_manifest_audit` exit 0 (5-part PMI-1 bump consistent per slice-063/064 anchor: `VERSION` 0.68.0 ≡ `plugin.yaml.version` ≡ `pyproject.toml [project].version` ≡ `## v0.68.0` header in methodology-changelog ≡ installed `~/.claude/ai-sdlc-VERSION`); CLAUDE.md L32 + shippability row #66 = separate BC-PROJ-9 / BC-PROJ-10 consumer-propagation surfaces (corrected per slice-066 /build-slice Phase A Builder-self-catch)
- [ ] `$PY -m tools.methodology_changelog_forward_sync` exit 0 (in-repo + installed `~/.claude/methodology-changelog.md` carry the v0.68.0 entry)
- [ ] `$PY -m tools.critique_agent_drift_audit --repo-root .` exit 0 (CAD-1 unaffected — slice does not edit Critic agent)
- [ ] `tests/methodology/test_build_slice_skill_drift.py` + `test_commit_slice_skill_drift.py` PASS (OSDG-1 forward-sync after the SKILL.md edits)
- [ ] `$PY -m tools.branch_workflow_audit` exit 0 (run from inside the slice-066 worktree — the slice's own dogfood; the WORKTREE=skip-bootstrap line covers the prose-not-yet-shipped window)
- [ ] R-17 absent from `$PY -m tools.risk_register_audit ... --filter-status open --json`
- [ ] No orphan worktree under `../ai_sdlc-wt/` after `/commit-slice --merge` (visual check + `git worktree list --porcelain` shows only the main tree)

## Pipeline position

- **predecessor**: `/reflect` (loop entry from slice-065 → slice-066)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission brief + milestone.md written; user-confirmed Slice C selection (the AskUserQuestion above); auto-invoke `/design-slice` via Skill tool without further prompt.
- **user-input gates** (halt auto-advance):
  - Candidate selection — DISCHARGED (user explicit pick: "Slice C: worktree-per-slice").
  - BFRD-1 bug-fix confirm gate — N/A (this is a discipline-ratchet slice, not a bug fix; no `tests/bugs/*` row needed).

Per PCA-1 ([[methodology-changelog.md#v0.41.0]]). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive read at skill-completion.

## Next step

`/design-slice` — turn the mission brief into a just-enough spec covering: worktree-path resolution helper shape, BRANCH-2 ADR body, branch_workflow_audit.py cwd-detection + `git worktree list --porcelain` parse, CLAUDE.md rewrite scope, partial-supersession encoding (ADR-063 → ADR-019; corrected from rev-1's `ADR-021` per slice-066 /critique B1 ACCEPTED-FIXED + /critique-review M-add-1 ACCEPTED-FIXED residual-rename closure), bootstrap DEVIATION line shape, and the test scaffolding for AC1-5.
