# Slice 075: close-merge-substep-3-worktree-collision

**Mode**: Standard
**Estimated work**: 0.5 day (~1-1.5 hr — prose surgery + 2 structural-pin tests + paired pins)
**Risk retired**: P1.2 + P2.4 from `enable-parallel-slice-pending-items.txt` (HIGH-priority parallel-slice operational defects in `/commit-slice --merge` Step 5b)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Close the two adjacent prose defects in `skills/commit-slice/SKILL.md` Step 5b that block a fresh Builder from running `/commit-slice --merge` under BRANCH-2 without an undocumented ad-hoc cd-to-main-tree workaround. (1) Sub-step 3's `git checkout $default` fails with `fatal: '<default>' is already checked out at '<main-tree-path>'` because the worktree holds `slice/NNN-<name>` and the main tree holds `<default>` — the prose lacks any main-tree-transition step. (2) Step 5b's pre-flight WT-clean check requires empty `git status --porcelain` BEFORE sub-step 2 runs, contradicting sub-step 2's expectation that the slice work is uncommitted (else there's nothing to `git add` + `git commit`). Slice-074's `--merge` worked ONLY because Claude pragmatically deviated from the literal prose — a fresh Builder following the skill literally hits both walls.

## Acceptance criteria

1. `skills/commit-slice/SKILL.md` Step 5b sub-step 3 prose includes an explicit main-tree-transition step BEFORE `git checkout <default>`, using a canonical worktree-aware form (`cd "$main_tree"` with `$main_tree` resolved via `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'`, OR equivalent `git -C "$main_tree" checkout` invocation pattern — no hard-coded path, no shell `~` expansion).
2. `skills/commit-slice/SKILL.md` Step 5b pre-flight WT-clean check (currently at L168) no longer contradicts sub-step 2's commit semantics — either repositioned to fire AFTER sub-step 2 (post-commit, pre-sub-step-3) with explicit ordering note, OR reframed to treat WT-non-empty as the EXPECTED pre-flight state with the silent-WT-discard local-state-loss protection preserved by an alternative gate (per /critique M5 ACCEPTED-PENDING intent).
3. Structural-pin test `tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py` asserts AC#1's main-tree-transition pattern is present in sub-step 3 prose AND uses the canonical `git worktree list --porcelain | awk ...` extraction shape (paired pin: prose-present + canonical-form).
4. Structural-pin test `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` asserts AC#2's WT-clean check is positioned correctly relative to sub-step 2 AND that the silent-WT-discard local-state-loss protection intent is preserved (paired pin: ordering + intent-preservation).
5. /validate-slice CLEAN: full pytest ≥1004/1004 PASS (1002 baseline + ≥2 new structural-pin tests including paired pins); shippability runner ≥74/74 PASS (1 new row for one representative new structural-pin test per RPCD-1 / SCPD-1 propagation; catalog grows 73 → 74; row #74 added per /critique M1 ACCEPTED-FIXED — empirical baseline confirmed via `$PY -m tools.shippability_runner architecture/shippability.md`); existing `tests/methodology/test_commit_slice_skill_merge_flag.py` PASSES (no regression in sub-step 3's overall structure); SCMD-1 + CAD-1 SKILL.md drift audits CLEAN; 16+ Step-6 audits all CLEAN.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Each AC maps to ≥1 failing test written BEFORE the SKILL.md prose change. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py | test_substep_3_includes_main_tree_transition_before_checkout | PENDING |
| 3 | methodology (paired-pin for AC#1) | tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py | test_substep_3_main_tree_transition_uses_canonical_worktree_list_awk_extraction | PENDING |
| 2 | methodology | tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py | test_wt_clean_preflight_does_not_contradict_substep_2_commit | PENDING |
| 4 | methodology (paired-pin for AC#2) | tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py | test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent | PENDING |

(Test-first plan deliberately maps AC#3 + AC#4 to paired-pin functions in the same test modules as AC#1 + AC#2 respectively — convention follows slice-067/072/073 paired-pin precedent. AC#5 is a meta-AC covering /validate-slice CLEAN at slice-finish; not test-first-pinnable except via the shippability catalog runner which is an existing audit.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Main-tree-transition prose present in sub-step 3 | Read `skills/commit-slice/SKILL.md` ~L188-189 vicinity; manually confirm `cd "$main_tree"` (or `git -C "$main_tree"`) precedes `git checkout <default>`; run `python -m pytest tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py::test_substep_3_includes_main_tree_transition_before_checkout -v` → PASS |
| 2 | WT-clean preflight ordering contradiction resolved | Read `skills/commit-slice/SKILL.md` ~L166-173 vicinity; manually confirm the preflight no longer requires empty `git status --porcelain` before sub-step 2's commit; run `python -m pytest tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py::test_wt_clean_preflight_does_not_contradict_substep_2_commit -v` → PASS |
| 3 | Paired pin: canonical extraction shape | `python -m pytest tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py::test_substep_3_main_tree_transition_uses_canonical_worktree_list_awk_extraction -v` → PASS |
| 4 | Paired pin: intent-preservation for WT-clean | `python -m pytest tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py::test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent -v` → PASS |
| 5 | /validate-slice CLEAN | `python -m pytest` → ≥1004/1004 PASS; `$PY -m tools.shippability_runner architecture/shippability.md` → ≥74/74 PASS (empirical baseline 73 per /critique M1 ACCEPTED-FIXED); SCMD-1 + CAD-1 audits CLEAN; 16+ Step-6 audits CLEAN |

## Must-not-defer

- [ ] **Main-tree resolution canonical form**: `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'` — extracts first-listed worktree = main tree per git porcelain ordering invariant (per [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree): "The main worktree is listed first, followed by each of the linked worktrees"). **SIBLING-BUT-DISTINCT idiom** from Step 5b sub-step 5 + Step 5d sub-step 5 which extract a SPECIFIC-branch worktree path via `awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}'`. Shared regex anchor `/^worktree /` with divergent AWK action because divergent semantics. No new helper, no hard-coded path, no shell `~` expansion. (Per /critique m1 ACCEPTED-FIXED.)
- [ ] **Silent-WT-discard protection intent preserved**: original /critique M5 ACCEPTED-PENDING intent (prevent silent local-state-loss) MUST survive — repositioning OK, intent-removal NOT OK; document new gate location explicitly in prose
- [ ] **Test-first discipline**: structural-pin tests written FIRST in Phase B (MUST FAIL against current SKILL.md), then prose change in Phase B makes them PASS — per TF-1; build-log Events MUST record both states
- [ ] **SCMD-1 mini-CAD content-equality**: in-repo `skills/commit-slice/SKILL.md` MUST stay content-equal modulo line endings to installed `~/.claude/skills/commit-slice/SKILL.md` per ADR-051 / OSDG-1 lineage (commit-slice is guarded via `tests/methodology/test_commit_slice_skill_drift.py`)
- [ ] **PSQ-3 re-entry semantics preserved**: per ADR-068 §Re-entry semantics — the prose change MUST NOT break sub-step 2.5 fast-forward no-op path OR sub-step 2's SKIP-on-clean-WT path after rebase-conflict-resolve
- [ ] **Sub-step 5 idempotent worktree-remove ordering preserved**: per ADR-063 §Decision sub-step ordering — worktree-remove MUST still precede branch-delete (sub-step 5 before sub-step 6); the main-tree-transition added at sub-step 3 MUST NOT cascade into sub-step 5 ordering changes
- [ ] **New shippability row**: 1 representative new structural-pin test row added per RPCD-1 / SCPD-1 propagation (every new audit rule's consumer reference propagates to the catalog)

## Out of scope

- **P1.1 (build-slice point 4 variable-scope code-Critic M1)** — separate surface (`skills/build-slice/SKILL.md`), separate slice: `slice-NNN-bundle-074-code-critic-cleanup`. Not bundled because that bundle also folds in slice-074's m1-m5 + P3.10 cp1252 mojibake fix — different blast-radius.
- **P2.2 (SOAD-1 retrofit for 6 raw yes/no prompts at L173/L175/L202/L203/L205/L255)** — same SKILL.md surface but separate concern (~1-2hr scope); separate slice: `slice-NNN-retrofit-soad-1-in-commit-slice-yes-no-prompts`.
- **`/critic-calibrate` run** — separate user-invokable meta-skill (not routed through /design-slice); user invokes independently. SEVERELY OVERDUE at FIVE simultaneous signals per slice-074 reflection, but mechanically not a /slice candidate.
- **Approach (c) "tear down worktree before checkout"** — would reshuffle sub-step 3 ↔ sub-step 5 ordering; the existing ordering (merge first, worktree-remove after) is load-bearing per ADR-063 §Decision sub-step ordering. Defer indefinitely.
- **Approach (b) `git -C "$main_tree"` heavier rewrite** — viable alternative to approach (a) `cd "$main_tree"`, but heavier prose change; defer unless approach (a) proves insufficient at design or build time.
- **Mirror-fix at `--sync-after-pr` Step 5d** — L274 already has a reactive STOP for the symmetric `git checkout <default>` collision; not in defect-scope (works today via the reactive STOP). Re-evaluate at /critique if cross-spec parity surfaces it.
- **Cross-spec parity audit module** (P3.6) — separate slice: `slice-NNN-parallel-slice-family-parity-audit`.
- **New rule mint / PMI-1 atomic bump** — this is methodology-prose-fix only (in-band correction to existing PSQ-3 / BRANCH-1 / BRANCH-2 contracts); MEPD-1 EXCLUDE → no methodology-changelog leg, no PMI-1 bump, ships at v0.72.0 unchanged.
- **The uncommitted source file `enable-parallel-slice-pending-items.txt` at repo root** — disposition (commit to slice scaffold / move into slice dir / leave as untracked source) deferred to /design-slice or /build-slice Phase A.

## Dependencies

- Prior slices: [[slice-073-add-rebase-and-conflict-discipline]] (PSQ-3 sub-step 2.5 + re-entry contract — slice-075 prose changes MUST NOT regress this), [[slice-066-add-branch-2-worktree-isolation]] (BRANCH-2 worktree-per-slice + sub-step 5 idempotent worktree-remove ordering — slice-075 MUST NOT cascade into sub-step 5 changes), [[slice-074-codify-cp-r-in-branch-2-skill]] (switch-commit-switch-worktree codification at /build-slice point 4 — empirical precedent for main-tree-aware prose)
- Vault refs: [[skills/commit-slice/SKILL.md]] Step 5b sub-steps 2/3/5 (the surfaces being edited), [[ADR-063]] BRANCH-2 §Decision sub-step ordering (sub-step 5 ordering MUST stay preserved), [[ADR-068]] PSQ-3 §Re-entry semantics (re-entry path MUST stay intact)
- Source-document anchor: `enable-parallel-slice-pending-items.txt` P1.2 + P2.4 (this slice closes both)
- Empirical anchor: slice-074 `/commit-slice --merge` build-log Event — Builder cd'd to main tree before sub-step 3 as undocumented workaround; this slice codifies the workaround into prose

## Notes

### BFRD-1 disposition

Sub-mode (a) name-shape: `close-*` is NOT in the canonical fix-*/bugfix-*/hotfix-*/defect-*/repair-*/patch-*/harden-*-bug list → does NOT fire.

Sub-mode (b) candidate-source signal: the source document `enable-parallel-slice-pending-items.txt` uses "Defect:" for P1.2 + P2.4 → literally fires.

**Disposition (analogous to slice-071 `close-tffl-1` + slice-073 PSQ-3 + slice-074 R-20 codification precedents)**: this is a **methodology-prose-defect**, not an application-bug. `/repro`'s `tests/bugs/*` convention is for application bug-fixes reproducible via runtime tests; methodology-prose-defects pin to `tests/methodology/test_*_skill_*.py` structural-pin tests written test-first per **TF-1**. The TF-1 plan above (4 structural-pin tests WRITTEN-FAILING before SKILL.md prose change) provides equivalent rigor — failing test established BEFORE fix, then made to PASS by the fix. BFRD-1 confirm gate NOT fired because the convention is well-established (3 prior precedents N=3) and the BFRD-1 application-bug heuristic over-fires on methodology-prose-defect surfaces. Watch-list signal for /critic-calibrate proposal: N=4 if this disposition recurs; consider formalizing "methodology-prose-defect ≠ application-bug, route to TF-1 not /repro" carve-out in BFRD-1 prose.

### Slice-074 lineage signal preservation

This slice does NOT address:
- TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions (held at N=7 cumulative; no new instance expected in a 5-AC test-first slice)
- AC-count > 5 carve-out (this slice deliberately uses 5 ACs without meta-AC #6 → reverts the slice-067/072/074 N=3 promotion signal IF clean)
- /critic-calibrate severely-overdue signal (separate skill invocation)
- MEPD-1-EXCLUDE-vs-shippability-row-disentanglement N=1 (this slice IS MEPD-1 EXCLUDE + DOES add a shippability row — N=2 confirmation that the two axes are independent)

### Source-document disposition

`enable-parallel-slice-pending-items.txt` is currently uncommitted untracked at repo root. Disposition deferred to /design-slice or /build-slice Phase A: candidates are (a) move to `architecture/slices/slice-075-close-merge-substep-3-worktree-collision/source-pending-items.txt` (audit-trail; becomes part of slice evidence); (b) leave at repo root as untracked source-material (lightweight but loses audit trail after `/commit-slice`); (c) leave at repo root and add to `.gitignore` (explicit untracked-source convention). Recommend (a) at design-time for audit-trail integrity.

## Mid-slice smoke gate

At ~50% of build (after 4 test files written + before SKILL.md prose change applied):

```bash
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py -v
& $PY -m pytest tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py -v
& $PY -m pytest tests/methodology/test_commit_slice_skill_merge_flag.py -v
```

Expected:
- New 2 test files: BOTH FAIL with structural-pin assertion errors against current SKILL.md (per TF-1 WRITTEN-FAILING state)
- Existing `test_commit_slice_skill_merge_flag.py`: STILL PASSES (no regression from preparatory edits — prose change not yet applied)

If new tests PASS prematurely against current SKILL.md: STOP — test assertions are too lax; tighten before continuing. If existing test FAILS: STOP — preparatory edits unexpectedly broke sub-step 3's overall structure; diagnose before continuing.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (especially: silent-WT-discard protection preserved; PSQ-3 re-entry intact; sub-step 5 ordering preserved)
- [ ] `/drift-check` passes
- [ ] SCMD-1: in-repo `skills/commit-slice/SKILL.md` content-equal modulo line endings to installed `~/.claude/skills/commit-slice/SKILL.md`
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Shippability runner: ≥74/74 PASS (1 new row #74 added for one of the new structural-pin tests; empirical baseline 73 → 74 per /critique M1 ACCEPTED-FIXED)
- [ ] Full pytest: ≥1004/1004 PASS (baseline 1002 + ≥2 new structural-pin tests; ≥4 if all paired pins count as separate test functions)
- [ ] 16+ Step-6 audits all CLEAN (TF-1 + BRANCH-2 + UTF8-STDOUT-1 + CRP-1 + PCA-1 + BCI-1 + MCFS-1 + STP-1 + AVFS-1 + TVFS-1 + NAW-1 + WIRE-1 + LINT-MOCK-1 + INST-1 + PMI-1 v0.72.0 unchanged + CAD-1 + SCMD-1 + critique-review + shippability runner)
- [ ] Critic disposition recorded in build-log.md + reflection.md (mandatory triggers: methodology surface `skills/commit-slice/SKILL.md` → critic-required: true regardless of tier)
