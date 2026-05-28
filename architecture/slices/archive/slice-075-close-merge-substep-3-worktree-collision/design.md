# Design: Slice 075 close-merge-substep-3-worktree-collision

**Date**: 2026-05-28
**Mode**: Standard
**Parents**: [[ADR-063]] BRANCH-2 worktree-per-slice, [[ADR-068]] PSQ-3 rebase-and-conflict discipline, [[ADR-020]] /commit-slice 3-mode taxonomy
**Source-document anchor**: `enable-parallel-slice-pending-items.txt` P1.2 + P2.4

## What's new

- `skills/commit-slice/SKILL.md` Step 5b prose surgery (2 edits, ~10-15 lines net change):
  - **Sub-step 3 main-tree-transition prepend**: add explicit `cd "$main_tree"` (with canonical `$main_tree` resolution via `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'`) BEFORE the existing `git checkout $default` invocation, closing the BRANCH-2 worktree-vs-main-tree `git checkout` collision (P1.2).
  - **WT-clean check repositioning**: lift the WT-clean preflight (currently L168) out of "Pre-flight guardrails" and reposition as a NEW sub-step **2.1. (post-commit WT-clean guardrail)** between sub-step 2 (commit on slice branch) and sub-step 2.5 (PSQ-3 rebase), closing the WT-clean-vs-sub-step-2-commit-ordering contradiction (P2.4) while preserving the silent-WT-discard local-state-loss protection intent (per /critique M5 ACCEPTED-PENDING). The decimal `2.1.` marker mirrors the slice-073 PSQ-3 sub-step 2.5 precedent for inserting an intermediate sub-step between integer-numbered steps (preserves Markdown ordered-list rendering — per /critique m2 ACCEPTED-FIXED, rejecting earlier "2-bis" draft which CommonMark renders as bold prose, not list item).
- `tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py` (NEW; ~80-120 LOC): 2 structural-pin test functions covering AC#1 + AC#3 (paired pin).
- `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` (NEW; ~80-120 LOC): 2 structural-pin test functions covering AC#2 + AC#4 (paired pin).
- `architecture/shippability.md` +1 row (row #74 — empirical baseline 73 per `$PY -m tools.shippability_runner architecture/shippability.md` output `73 row(s), 73 PASS, 0 FAIL`; per /critique M1 ACCEPTED-FIXED): one representative new structural-pin test added per RPCD-1 / SCPD-1 propagation. Pick `test_substep_3_includes_main_tree_transition_before_checkout` as the catalog representative (the P1.2 fix is the higher-acuity defect).

## What's reused

- [[skills/commit-slice/SKILL.md]] Step 5b sub-steps 1, 2, 2.5, 3, 4, 5, 6, 7 — prose surgery is **additive** at sub-step 3 (prepend cd) + **lift-and-shift** for the WT-clean preflight (no semantic change to its assertion, only repositioned and renumbered to `2.1.` decimal marker). All other sub-step prose preserved verbatim.
- [[skills/commit-slice/SKILL.md]] Step 5b sub-step 5 (`idempotent worktree-remove guard`) and sub-step 6 (`git branch -d`) ordering — load-bearing per ADR-063 §Decision; this slice MUST NOT touch.
- [[skills/commit-slice/SKILL.md]] Step 5b sub-step 2.5 (PSQ-3 rebase) and its re-entry semantics per [[ADR-068]] §Re-entry semantics — sub-step 2.1. insertion MUST NOT regress the re-entry SKIP-on-clean-WT path (post-rebase-resolve re-invocation must still fast-forward through sub-step 2 SKIP → sub-step 2.1. CLEAN → sub-step 2.5 fast-forward no-op → sub-step 3).
- `tests/methodology/conftest.py::read_file` helper — every existing `tests/methodology/test_commit_slice_skill_*.py` uses this; new tests follow suit.
- `tests/methodology/test_commit_slice_skill_rebase_flag.py::_step_5b_section()` helper pattern — section-scoped extraction (`#### Step 5b:` → `#### Step 5c:`) prevents false-positives from a stray `git rebase`/`cd` mention elsewhere. **Section-scoping is mandatory** for all 4 new test functions in this slice (AC#1, AC#3 in main_tree_transition module + AC#2, AC#4 in wt_clean_preflight_ordering module) — per /critique M2 ACCEPTED-FIXED, the literal anchor `Pre-flight guardrails (run BEFORE any state change):` appears 3× in SKILL.md (L166 Step 5b + L207 Step 5c + L242 Step 5d) and Steps 5c + 5d legitimately retain WT-clean `git status --porcelain` pre-flight checks (--push and --sync-after-pr have no commit step), so any whole-file assertion would false-FAIL. New tests duplicate `_step_5b_section()` helper via a local per module (per Fowler "Duplicated Code" trade-off: cross-module shared helpers in conftest.py would be a follow-on consolidation slice, not in scope here — N=4 cumulative recurrence on cross-module section-extractor duplication would warrant the consolidation; current N=2 with rebase_flag + N=2 new modules = N=4 total at slice-076+ candidate trigger).
- [[ADR-024]] CRP-1 (Critic-as-runtime-policy) — methodology-revision slice convention: prose change + structural-pin test, no runtime code.
- [[ADR-051]] OSDG-1 mini-CAD skill-drift content-equality (commit-slice guarded via `tests/methodology/test_commit_slice_skill_drift.py`) — in-repo / installed parity MUST hold post-slice.

## Components touched

### `skills/commit-slice/SKILL.md` (modified)
- **Responsibility**: declarative skill prose driving `/commit-slice` 3-mode flow (--merge / --push / --sync-after-pr); the prose IS executable contract (Claude reads it and acts on the literal sub-step instructions)
- **Lives at**: `C:\Users\sshub\ai_sdlc\skills\commit-slice\SKILL.md`
- **Edit surfaces (this slice)**:
  - Pre-flight guardrails block (currently L166-168): remove the WT-clean check from this block; keep only the Stale-slice-branch check (1 guardrail, not 2).
  - Insert new sub-step **2.1. (post-commit WT-clean guardrail)** between sub-step 2 (L172-173) and sub-step 2.5 (L174). Decimal `2.1.` marker mirrors slice-073 PSQ-3 sub-step `2.5.` precedent for inserting intermediate sub-steps between integer-numbered steps (CommonMark ordered-list compliant — per /critique m2 ACCEPTED-FIXED). Body: `git status --porcelain` MUST return empty NOW (after sub-step 2's commit). If non-empty, STOP. Print: "WT non-empty after sub-step 2 commit. Unexpected un-committed files: `<list>`. Commit or discard before proceeding (preserves silent-WT-discard local-state-loss protection per /critique M5 ACCEPTED-PENDING)."
  - Sub-step 3 (currently L189): prepend `main_tree=$(git worktree list --porcelain | awk '/^worktree / {print $2; exit}')` resolution + `cd "$main_tree"` transition BEFORE the existing default-branch resolution + `git checkout $default` + `git merge --no-ff`. Body change is ~3 lines added at the head of sub-step 3.
  - Rename of Pre-flight section heading from "Pre-flight guardrails (run BEFORE any state change):" → "Pre-flight guardrails (run BEFORE any state change):" (preserved verbatim — the 1 remaining guardrail is still pre-flight; the lifted WT-clean check becomes a numbered sub-step not a guardrail).
- **Key interactions**: read by Claude at `/commit-slice --merge` invocation; mirror-installed copy at `~/.claude/skills/commit-slice/SKILL.md` must stay content-equal per SCMD-1.

### `tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py` (created)
- **Responsibility**: pin AC#1 (main-tree-transition present in sub-step 3 BEFORE `git checkout $default`) + AC#3 (canonical `git worktree list --porcelain | awk ...` extraction shape)
- **Lives at**: `C:\Users\sshub\ai_sdlc\tests\methodology\test_commit_slice_skill_merge_substep_3_main_tree_transition.py`
- **Key interactions**: uses `tests.methodology.conftest.read_file`; defines local `_step_5b_section()` helper modeled after `tests/methodology/test_commit_slice_skill_rebase_flag.py::_step_5b_section()` (extracts `#### Step 5b:` → `#### Step 5c:` boundary); ALL section-scoped assertions on `skills/commit-slice/SKILL.md` Step 5b — mandatory per /critique M2 ACCEPTED-FIXED because `Pre-flight guardrails (run BEFORE any state change):` header appears 3× in SKILL.md
- **Test functions**:
  1. `test_substep_3_includes_main_tree_transition_before_checkout` (AC#1): asserts `cd "$main_tree"` appears in Step 5b section (via `_step_5b_section()`) AND appears BEFORE the literal `git checkout` in sub-step 3 ordering (offset-comparison: `section.find('cd "$main_tree"') < section.find('git checkout')`)
  2. `test_substep_3_main_tree_transition_uses_canonical_worktree_list_awk_extraction` (AC#3, paired pin): asserts the literal `git worktree list --porcelain` + `awk '/^worktree / {print $2; exit}'` appear in Step 5b section as the `$main_tree` resolution mechanism (section-scoped via `_step_5b_section()`)

### `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` (created)
- **Responsibility**: pin AC#2 (WT-clean check repositioned to post-sub-step-2) + AC#4 (silent-WT-discard local-state-loss protection intent preserved)
- **Lives at**: `C:\Users\sshub\ai_sdlc\tests\methodology\test_commit_slice_skill_merge_wt_clean_preflight_ordering.py`
- **Key interactions**: uses `tests.methodology.conftest.read_file`; defines local `_step_5b_section()` helper modeled after `tests/methodology/test_commit_slice_skill_rebase_flag.py::_step_5b_section()` (extracts `#### Step 5b:` → `#### Step 5c:` boundary); ALL section-scoped assertions on Step 5b only — mandatory per /critique M2 ACCEPTED-FIXED because Steps 5c (--push L207-209) + 5d (--sync-after-pr L242-244) legitimately retain WT-clean pre-flight `git status --porcelain` checks (those flows have no commit step) and any whole-file assertion would false-FAIL
- **Test functions** (assertions anchored on the unique post-fix `2.1.` sub-step marker per /critique-review M-add-1 + M-add-2 ACCEPTED-FIXED — the `2.1.` literal is unique to post-fix Step 5b prose because pre-fix Step 5b has no `2.1.` sub-step; this guarantees TF-1 WRITTEN-FAILING semantics; previously-drafted assertion shapes were too weak because (a) pre-fix L168 already contains `silent-WT-discard` + `STOP` + `Print:` literals — so AC#4 whole-section presence-check would PASS pre-fix, and (b) pre-fix L181 PSQ-3 conflict-STOP block already contains `git status --porcelain` AFTER sub-step 2's L173 `git commit` — so AC#2 sub-assertion (b) offset-check would PASS pre-fix; both violate TF-1's "test must FAIL pre-fix" invariant):
  1. `test_wt_clean_preflight_does_not_contradict_substep_2_commit` (AC#2): three sub-assertions, all Step-5b-section-scoped via `_step_5b_section()`: (a) the contiguous Pre-flight-guardrails sub-block (from literal `Pre-flight guardrails (run BEFORE any state change):` header through the blank line preceding `Then the 5-step merge flow:`) MUST NOT contain `git status --porcelain` (i.e., WT-clean check is no longer pre-flight); (b) the literal `2.1.` sub-step marker MUST appear in Step 5b section (anchor unique to post-fix prose; prelude guard `two_one_pos = section.find("2.1."); assert two_one_pos != -1, "Step 5b section must contain a '2.1.' sub-step marker (post-fix prose required per /critique-review M-add-2 ACCEPTED-FIXED)"` for clean WRITTEN-FAILING diagnostic pre-fix); (c) within the contiguous block `section[two_one_pos:section.find("2.5.", two_one_pos)]` (the 2.1. sub-step block extracted via post-fix-anchor + next-sub-step bound), the literal `git status --porcelain` MUST appear (i.e., the lifted WT-clean check lives inside the new sub-step 2.1. block, not at any pre-existing site).
  2. `test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent` (AC#4, paired pin): section-scoped via `_step_5b_section()` AND further sub-step-scoped via the `2.1.` anchor (same extraction shape as test 1 sub-assertion (c) — extract contiguous block via `two_one_pos = section.find("2.1."); two_five_pos = section.find("2.5.", two_one_pos); block = section[two_one_pos:two_five_pos]` with prelude guard `assert two_one_pos != -1, "Step 5b section must contain a '2.1.' sub-step marker (post-fix prose required per /critique-review M-add-1 ACCEPTED-FIXED)"` for clean WRITTEN-FAILING diagnostic); asserts that `block` contains "silent-WT-discard" (or equivalent intent-preserving phrase like "local-state-loss") AND retains STOP semantic (literal `STOP`) + diagnostic-print pattern (literal `Print:` or `Print "`). The `2.1.` sub-step-scoping makes the assertion FAIL pre-fix (no `2.1.` anchor exists → prelude guard raises) and PASS post-fix (the lifted prose lives inside the new 2.1. block with all three intent literals preserved per M5 ACCEPTED-PENDING shape).

## Contracts added or changed

### `/commit-slice --merge` Step 5b behavior contract (modified, in-band)
- **Defined in skill prose at**: `skills/commit-slice/SKILL.md` L162-201 (Step 5b section)
- **What changes (behavior-contract, not invocation-shape)**:
  - **OLD pre-flight ordering**: stale-slice-branch check → WT-clean check → (5-step merge flow) → ...; the WT-clean check incorrectly required empty `git status --porcelain` BEFORE sub-step 2's `git add` + `git commit` could execute (logical contradiction — /build-slice produces uncommitted slice work for sub-step 2 to commit).
  - **NEW pre-flight ordering**: stale-slice-branch check → (sub-step 1 show message + staged files) → (sub-step 2 confirm + commit) → **NEW sub-step 2.1. post-commit WT-clean guardrail** → (sub-step 2.5 PSQ-3 rebase) → **(sub-step 3 NEW: main-tree transition prepend)** → (sub-step 3 existing: resolve default + checkout + no-ff merge) → ...; the WT-clean assertion now fires AFTER commit (semantically meaningful: catches "sub-step 2 missed files") AND main-tree transition happens before `git checkout` (resolves BRANCH-2 collision).
  - **Silent-WT-discard local-state-loss protection (per /critique M5 ACCEPTED-PENDING)**: intent preserved at the new sub-step 2.1. position. STOP semantic + diagnostic-print pattern preserved verbatim modulo position.
  - **PSQ-3 sub-step 2.5 re-entry semantics (per [[ADR-068]])**: unchanged — sub-step 2.1. sits BETWEEN sub-step 2 and sub-step 2.5, and on a clean-WT re-entry (post-rebase-resolve re-invocation), sub-step 2 SKIPs (nothing to commit) → sub-step 2.1. passes trivially (WT was already clean before sub-step 2 SKIP) → sub-step 2.5 fast-forwards → sub-step 3 proceeds. The new sub-step 2.1. is **vacuous on re-entry** by construction.
  - **Sub-step 5 idempotent worktree-remove ordering (per [[ADR-063]])**: unchanged — sub-step 5 still precedes sub-step 6 (`git branch -d`); main-tree transition at sub-step 3 means sub-step 5+6 also execute from main tree, which is the correct context for `git worktree remove "$wt_path"` (worktree-remove is repo-wide, but `git branch -d` cleaner from main tree where the branch isn't checked out anywhere).
- **Auth model**: N/A (skill prose, no runtime auth)
- **Error cases**:
  - Sub-step 2.1. WT-non-empty: STOP with diagnostic listing uncommitted files (preserves M5 silent-WT-discard intent)
  - Sub-step 3 `main_tree` resolution empty (e.g., bare repo or worktree-list returns nothing): STOP. New diagnostic: "main-tree resolution failed via `git worktree list --porcelain` extraction. Worktree may be detached or repo state corrupt. Resolve manually before retrying `/commit-slice --merge`."
  - Sub-step 3 `cd "$main_tree"` failure (e.g., path doesn't exist on disk — should be impossible if `git worktree list` returned it, but defensive): STOP with git's stderr verbatim + diagnostic hint.

## Data model deltas

None. This slice modifies only skill prose + adds test modules. No new entities, fields, or schemas.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py` | `tools/shippability_runner.py` (catalog row #74 added per RPCD-1/SCPD-1; empirical baseline 73 confirmed via runner output `73 row(s), 73 PASS, 0 FAIL`) + pytest collection | `tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py::test_substep_3_includes_main_tree_transition_before_checkout` (the module IS the test; self-consuming per existing tests/methodology/test_commit_slice_skill_*.py precedent) | — |
| `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` | pytest collection (no shippability row; AC#2's intent is repositioning-not-introduction so the catalog row at AC#1's test is sufficient per "1 representative per slice" convention) | `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py::test_wt_clean_preflight_does_not_contradict_substep_2_commit` (self-consuming) | `internal structural-pin test, self-consuming per tests/methodology/* precedent — rationale: methodology-prose-pin tests don't have downstream consumers; they ARE the consumer of skills/commit-slice/SKILL.md` |

The shippability catalog row addition propagates per RPCD-1 / SCPD-1: 1 representative new test row per slice. The 2nd new test module gets an explicit exemption rationale per WIRE-1's exemption-cell contract.

## Decisions made (ADRs)

**None.** This slice is in-band methodology-prose-fix to existing contracts [[ADR-063]] BRANCH-2 + [[ADR-068]] PSQ-3 + [[ADR-020]] commit-slice 3-mode. MEPD-1 EXCLUDE per mission-brief: no methodology-changelog entry, no PMI-1 bump, ships at v0.72.0 unchanged.

### Options considered (for design.md audit-trail; no ADR mint)

**Question A: Main-tree transition mechanism at sub-step 3**
- (a) **`cd "$main_tree"` prepend** (CHOSEN) — minimal prose change (~3 lines). The `$main_tree` resolution `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'` is a **SIBLING-BUT-DISTINCT idiom** from sub-step 5's extraction `awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}'` — they share the `/^worktree /` regex anchor but the AWK action differs because they solve different problems (sub-step 3 returns the FIRST worktree = main tree per git porcelain ordering invariant; sub-step 5 returns the path for a SPECIFIC branch). Per /critique m1 ACCEPTED-FIXED (earlier "reuses sub-step 5's existing awk extraction" framing was misleading: false substring-check `"awk '/^worktree / {print $2; exit}'" in <sub-step-5-awk>` → False). Both idioms grounded in the same git-porcelain output format documented at [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree); no new helper introduced; cwd change harmless because subsequent sub-steps (5 worktree-remove, 6 branch-delete, 7 git-log) all work correctly from main tree.
- (b) `git -C "$main_tree" ...` prefix on every sub-step 3 invocation — no cwd change but heavier prose rewrite (every `git checkout`, `git merge`, sub-step 5's `git worktree remove`, sub-step 6's `git branch -d`, sub-step 7's `git log` would need `-C` prefix for consistency)
- (c) "Tear down worktree before sub-step 3 default-checkout" — would reshuffle sub-step ordering; sub-step 5's `git worktree remove` ordering relative to sub-step 6's `git branch -d` is load-bearing per [[ADR-063]] §Decision (worktree must be removed BEFORE branch-delete because a checked-out branch refuses safe-delete); reshuffling cascades into ADR-063's ordering contract — **explicitly out of scope** per mission-brief

**Question B: WT-clean preflight repositioning**
- (a) **Lift to NEW sub-step 2.1. (post-commit guardrail)** (CHOSEN) — preserves M5 silent-WT-discard intent verbatim; clean numbered-sub-step insertion using decimal `2.1.` marker (mirrors slice-073 PSQ-3 sub-step `2.5.` precedent for intermediate sub-step insertion between integer-numbered steps; CommonMark ordered-list compliant — per /critique m2 ACCEPTED-FIXED rejecting earlier "2-bis" draft which Markdown renders as bold prose, not list item); semantically meaningful (post-commit "did sub-step 2 commit everything?" check); vacuous on PSQ-3 re-entry by construction
- (b) Reframe WT-non-empty as expected + introduce NEW preflight checking "WT contains EXPECTED slice work" (matches build-log.md "Files changed") — heavier rewrite; introduces a new audit-shape (build-log.md parsing in /commit-slice runtime); pulls in dependencies on build-log.md format stability
- (c) Just remove the WT-clean preflight entirely + rely on sub-step 2's user-confirmation prompt — drops M5 silent-WT-discard protection; **violates Must-not-defer item "silent-WT-discard protection intent preserved"**

**Question C: ADR mint vs in-band correction**
- (a) **No new ADR (in-band correction)** (CHOSEN) — slice mints no new rule; closes existing-contract gap by adding prose-prescribed steps within established BRANCH-2 + PSQ-3 + ADR-020 contracts; precedent: slice-074 R-20 codification at /build-slice point 1 (no new ADR, just operationalized R-20 candidate (a)); MEPD-1 EXCLUDE
- (b) Mint new "CMS-3 (commit-slice main-tree-transition discipline)" ADR — would be a NEW rule at the parallel-slice family axis; would require PMI-1 atomic bump v0.72.0 → v0.73.0 + methodology-changelog entry + shippability row + structural-pin test propagation; **scope-inflated**, the prose-fix is not load-bearing enough to mint a rule (it's defect-closure, not rule-introduction)

**Question D: AC count carve-out (5 vs 6 ACs)**
- (a) **5 ACs without AC#6 meta-AC** (CHOSEN) — reverts the slice-067/072/074 AC-count > 5 N=3 promotion signal; this slice has no rule mint or PMI-1 atomic bump that would force AC#6
- (b) Add AC#6 meta-AC for paired-pin coverage — would reinforce the N=3 carve-out signal; unnecessary because paired pins live as separate test functions within AC#3 + AC#4 (already explicit ACs)

## Authorization model for this slice

N/A — skill-prose surgery only. No runtime code, no auth surface.

## Error model for this slice

Three new error paths introduced in `skills/commit-slice/SKILL.md` Step 5b (all STOP-with-diagnostic; no auto-recovery per the existing "NEVER auto-resolve" Critical rules block):

1. **Sub-step 2.1. WT-non-empty after sub-step 2 commit**: STOP. Print uncommitted-files list + diagnostic preserving M5 silent-WT-discard local-state-loss protection intent.
2. **Sub-step 3 `main_tree` resolution empty**: STOP. Print diagnostic "main-tree resolution failed via `git worktree list --porcelain` extraction. Worktree may be detached or repo state corrupt."
3. **Sub-step 3 `cd "$main_tree"` failure**: STOP. Print git's stderr verbatim + actionable hint.

No new exit codes are introduced; STOP semantics follow the existing Step 5b convention (exit non-zero, leave repo state intact, no auto-mutation).

## Audit / shippability propagation

- `architecture/shippability.md` +1 row (row #74; empirical baseline 73 per `$PY -m tools.shippability_runner architecture/shippability.md` output `73 row(s), 73 PASS, 0 FAIL` — per /critique M1 ACCEPTED-FIXED) representative test: `tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py::test_substep_3_includes_main_tree_transition_before_checkout` — per RPCD-1 / SCPD-1 "every new audit rule's consumer reference propagates to the catalog". The P1.2 fix (main-tree-transition) is the higher-acuity defect (literal `git checkout` failure) so its test is the catalog representative. The AC#2 (WT-clean repositioning) test is a peer-pin not duplicated in the catalog.
- `tools/test_first_audit.py --strict-pre-finish` (TF-1): all 4 test rows in mission-brief Test-first plan progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle.
- `tools/build_checks_audit.py` (BC-1): expect `BC-GLOBAL-2 prose-vs-automation false-positive` to fire on this slice's design.md (it discusses repositioning the WT-clean check); defer-with-rationale per N=6 cumulative class precedent (slice-069/070/071/072/073/074 lineage; `/critic-calibrate` proposal target P4.2).
- `tools/pmi_audit.py` (PMI-1): MEPD-1 EXCLUDE — no PMI-1 bump expected; audit MUST report v0.72.0 unchanged.
- `tools/critique_agent_drift_audit.py` (CAD-1): unchanged — slice doesn't touch `agents/critique.md`.
- `tests/methodology/test_commit_slice_skill_drift.py` (SCMD-1 / OSDG-1 mini-CAD): MUST PASS after slice — in-repo `skills/commit-slice/SKILL.md` content-equal modulo line endings to installed `~/.claude/skills/commit-slice/SKILL.md`.
- `tools/branch_workflow_audit.py` (BRANCH-2): slice runs under worktree-per-slice + branch-per-slice; build-log Events MUST record worktree path + branch creation; merge-back via `/commit-slice --merge` MUST execute correctly under the NEW prose (dogfooding gate — this slice's `/commit-slice --merge` IS the first empirical test of the fix).
