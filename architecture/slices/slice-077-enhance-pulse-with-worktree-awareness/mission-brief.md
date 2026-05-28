# Slice 077: enhance-pulse-with-worktree-awareness

**Mode**: Standard
**Estimated work**: ~0.5 day (SMALL — /pulse SKILL.md prose enhancement + new helper module + tests; MEPD-1 path decided at /design — EXCLUDE preview, /design may upgrade to mint PWA-1 if rule-class evidence accumulates)
**Risk retired**: **R-22** (`/pulse` mis-reports active-slice state during BRANCH-2 worktree window) — registered at /design per /critique-review M-add-2 ACCEPTED-FIXED (RR-1 semantic conformance: the L5 field cites the R-NN entry that flips to `status: retired` at /reflect). R-22 covers the skill-correctness gap witnessed firsthand during the slice-076 merge sequence: post-slice-076 `/pulse` reported stage `slice` while slice-076 was fully built / validated / reflected / auto-archived in worktree `C:/Users/sshub/ai_sdlc-wt/slice-076-...` (HEAD = reflect commit; VERSION=0.73.0; 1039/1039 pytest; BC-PROJ-12 promoted) — and raised a false-positive "vault forward-population" drift flag from the same root cause (installed `~/.claude/methodology-changelog.md` forward-synced by the worktree's `/reflect` step vs master's stale changelog). Every future post-merge `/pulse` during a BRANCH-2 worktree window would repeat both errors without this slice. R-22 registration mirrors slice-076's R-21 precedent (also at /design, also for a witnessed-during-build gap).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Enhance `/pulse` so that BRANCH-2 worktree state is a first-class input to its macro-state read. When a non-main worktree on a `slice/NNN-<name>` branch exists, `/pulse` reads that worktree's `milestone.md` (active or auto-archived), classifies the slice as `in-progress` / `built-but-not-merged` / `merged`, and overrides the recommended-next-action + drift-flag heuristics accordingly. New helper `tools/pulse_worktree_resolver.py` exposes a library API + CLI for the detection logic. After this slice ships: post-merge `/pulse` runs during a worktree window correctly report the slice's true stage AND suppress the master-vs-installed false-positive drift flag.

## Re-scoping note

Slice-076 reflection nominated slice-077 for PCR-2 (VAULT_CLAIM + HARD-conflict full Critic stack + TRI-RESOLVE-1). The user explicitly chose `enhance-pulse-with-worktree-awareness` for slice-077 because the gap was witnessed firsthand during the slice-076 merge sequence AND the fix is bounded (SMALL effort). PCR-2 is re-queued at the head of `architecture/slice-queue.md` as slice-078; the underlying methodology axis is unchanged.

## Acceptance criteria

1. **Worktree detection in `/pulse` Step 1**: `skills/pulse/SKILL.md` Step 1 enumerates `git worktree list --porcelain` parsing as a mandatory pre-read step BEFORE reading the main-tree `architecture/slices/<active>/milestone.md`. If a non-main worktree on a `slice/NNN-<name>` branch exists, `/pulse` reads that worktree's `architecture/slices/<active>/milestone.md` (if `<active>` is `slice-NNN-<name>`) OR `architecture/slices/archive/slice-NNN-<name>/milestone.md` (if the slice was auto-archived by the worktree's `/reflect` step). Prose-pin tests on SKILL.md verify the Step 1 augmentation literal-presence + ordering invariant (`git worktree list` mention precedes the main-tree milestone.md read instruction).

2. **Built-but-not-merged state classification**: a new function `classify_worktree_state(worktree: WorktreeInfo, default_branch: str, repo_root: Path) -> WorktreeStateClassification` returns a frozen dataclass with `.state: WorktreeState` (one of four values) + `.reason: str` (human-readable rationale for debugging). The four values: `IN_PROGRESS` (worktree HEAD points at a pre-build commit per milestone.md `stage:` ≠ `reflect`), `BUILT_BUT_NOT_MERGED` (milestone.md stage = `reflect` AND worktree HEAD is not reachable from `<default>`'s tip via `git merge-base --is-ancestor`), `MERGED` (worktree HEAD reachable from `<default>` — transient under `--merge` happy path; can persist legitimately after `--push` + `/sync-after-pr` workflows or `--merge` worktree-remove failure; surfaced as a CLEANUP-CANDIDATE warning when observed), or `UNKNOWN` (fail-closed default on any parse failure: milestone.md missing in a fresh worktree, milestone.md frontmatter malformed, detached HEAD, dirty worktree blocks classification, stale-prunable registration, etc. — each surfaced as a one-line WARN in `/pulse`'s Drift & flags section, never silently dropped). Unit tests cover all four states + the enumerated UNKNOWN sub-reasons.

3. **Recommended next action override**: when `BUILT_BUT_NOT_MERGED` is detected for any active-slice worktree, `/pulse` Step 3 output's "Recommended next action" line is overridden to `Run \`cd <worktree-path> && /commit-slice --merge\`` as the primary suggestion, AND the active-slice section reports the worktree's stage (`reflect` — fully built) instead of the main-tree milestone.md's stale stage. SKILL.md prose-pin tests verify the override-clause literal-presence + the precedence over the cadence-overdue critic-calibrate override (worktree-built-but-not-merged supersedes calibration cadence: the user can't pick the next slice until the current one is merged).

4. **Drift-flag false-positive suppression**: `/pulse`'s "Drift & flags" section gains a guard — when `BUILT_BUT_NOT_MERGED` is observed for an active-slice worktree AND the installed copies (`~/.claude/methodology-changelog.md` / `~/.claude/ai-sdlc-VERSION` / installed SKILL.md files) match the WORKTREE's content rather than the main tree's, the master-vs-installed divergence is the EXPECTED state (the worktree's `/reflect` step forward-synced; master is behind by design) — SUPPRESS the "vault forward-population" flag. Unit test verifies suppression fires only when worktree-state is `BUILT_BUT_NOT_MERGED` AND installed-content matches worktree (not when installed is otherwise-divergent).

5. **NEW helper `tools/pulse_worktree_resolver.py`** + end-to-end ship: library API exports `detect_active_worktrees(repo_root: Path) -> list[WorktreeInfo]` (returns each non-main worktree's path + branch + HEAD-sha + milestone.md path resolved to active OR archived) + `classify_worktree_state(worktree, default_branch, repo_root) -> WorktreeStateClassification` + frozen dataclasses (`WorktreeInfo`, `WorktreeStateClassification`) + enum `WorktreeState` (IN_PROGRESS / BUILT_BUT_NOT_MERGED / MERGED / UNKNOWN). CLI: `python -m tools.pulse_worktree_resolver [--detect | --classify <slice-NNN>] [--json] [--repo-root <path>]`. Cross-spec parity with `tools/parallel_conflict_resolver.py` (PCR-1 sibling helper) per design.md § Cross-spec parity: argparse mutually-exclusive group required, `--repo-root` default `Path(".").resolve()`, JSON output keys `{action, ...}` + `{error, ...}` on stderr, Exit 0/1/2 semantics, `_stdout.reconfigure_stdout_utf8()` at top of `main()`. BC-PROJ-9 5-inventory for the new module (plugin.yaml tools + `_CANONICAL_TOOLS` + INSTALL.md tool-count `31 → 32` at L22 AND L166 + shippability row #77 + `_ROOT_ONLY_TOOLS` test-utf8 inclusion). CAD-1 / OSDG-1 byte-equality on `skills/pulse/SKILL.md` repo↔installed after edits. APED-1 empirical battery on `detect_active_worktrees` + `classify_worktree_state` against **≥13 enumerated fixtures**: detect {empty / one-slice-worktree / multiple-slice-worktrees / non-slice-branch-filtered / mixed-slice-and-non-slice / stale-prunable} = 6 + classify {IN_PROGRESS / BUILT_BUT_NOT_MERGED / MERGED / UNKNOWN-no-milestone / UNKNOWN-malformed-frontmatter / UNKNOWN-git-merge-base-error / UNKNOWN-head-unresolvable} = 7. Pytest 100% PASS (no regression vs slice-076 baseline + ~8-12 new tests added); 14+ Step-6 audits clean; 3-Critic stack disposition recorded. MEPD-1 path decided at /design (EXCLUDE — no methodology-changelog entry, no PMI-1 bump; rationale honest-precedent rewrite in ADR-070 § Decision).

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology / pulse SKILL.md prose | tests/methodology/test_pulse_skill_worktree_awareness.py | test_step_1_documents_git_worktree_list_pre_read | PENDING |
| 1 | methodology / pulse SKILL.md prose | tests/methodology/test_pulse_skill_worktree_awareness.py | test_worktree_milestone_read_precedes_main_tree_milestone_read | PENDING |
| 2 | unit / state classification | tests/skills/pulse/test_classify_worktree_state.py | test_classify_returns_in_progress_when_milestone_stage_is_pre_reflect | PENDING |
| 2 | unit / state classification | tests/skills/pulse/test_classify_worktree_state.py | test_classify_returns_built_but_not_merged_when_reflect_stage_and_head_not_ancestor_of_default | PENDING |
| 2 | unit / state classification | tests/skills/pulse/test_classify_worktree_state.py | test_classify_returns_merged_when_head_reachable_from_default | PENDING |
| 2 | unit / state classification | tests/skills/pulse/test_classify_worktree_state.py | test_classify_returns_unknown_on_unparseable_git_state | PENDING |
| 3 | methodology / pulse SKILL.md override | tests/methodology/test_pulse_skill_worktree_awareness.py | test_built_but_not_merged_overrides_recommended_next_action_with_commit_slice_merge | PENDING |
| 3 | methodology / pulse SKILL.md override | tests/methodology/test_pulse_skill_worktree_awareness.py | test_worktree_override_takes_precedence_over_calibration_cadence_override | PENDING |
| 4 | unit / drift-flag suppression | tests/skills/pulse/test_drift_flag_suppression.py | test_suppress_vault_forward_population_when_built_but_not_merged_and_installed_matches_worktree | PENDING |
| 4 | unit / drift-flag suppression | tests/skills/pulse/test_drift_flag_suppression.py | test_do_not_suppress_when_installed_diverges_from_both_worktree_and_main | PENDING |
| 5 | unit / helper library API | tests/skills/pulse/test_detect_active_worktrees.py | test_detect_returns_empty_list_when_only_main_worktree_present | PENDING |
| 5 | unit / helper library API | tests/skills/pulse/test_detect_active_worktrees.py | test_detect_returns_worktree_info_for_slice_branch_worktree | PENDING |
| 5 | unit / helper CLI | tests/skills/pulse/test_cli.py | test_cli_detect_json_emits_parseable_worktree_list | PENDING |
| 5 | unit / helper CLI | tests/skills/pulse/test_cli.py | test_cli_classify_json_returns_state_for_given_slice | PENDING |
| 5 | methodology / BC-PROJ-9 5-inventory | tests/methodology/test_pulse_worktree_resolver_tool_inventory.py | test_pulse_worktree_resolver_in_canonical_tools_plugin_manifest_install_md_at_l22_and_l166 | PENDING |
| 3 | unit / Step-2 state-dict contract | tests/skills/pulse/test_state_dict_shape.py | test_step_2_state_dict_includes_worktrees_field_with_worktreeinfo_list | PENDING |
| 4 | unit / drift-flag suppression (EOL) | tests/skills/pulse/test_drift_flag_suppression.py | test_suppression_predicate_is_eol_agnostic_per_eol_drift_1 | PENDING |
| 5 | methodology / CAD-1 pulse drift | tests/methodology/test_pulse_skill_drift.py | test_in_repo_and_installed_pulse_skill_md_byte_equal | EXISTING (verify still passes post-edit) |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Worktree detection in Step 1 | Read `skills/pulse/SKILL.md` Step 1; assert `git worktree list` literal present BEFORE the main-tree `milestone.md` read instruction; assert worktree-aware milestone-path resolution clause (active OR archived); pytest prose-pin tests PASS. |
| 2 | State classification | Synthetic worktree fixtures (in-progress + built-but-not-merged + merged + zero-worktree); invoke `classify_worktree_state`; assert correct `WorktreeState` returned per fixture; assert fail-closed `UNKNOWN` on unparseable git state. |
| 3 | Recommended next action override | Synthetic fixture: BRANCH-2 worktree with milestone.md `stage: reflect` AND worktree HEAD ahead of default. Invoke `/pulse` against this state (or its rendering primitive); assert "Recommended next action" line cites `cd <worktree-path> && /commit-slice --merge`; assert override precedence over calibration cadence (calibration-overdue + built-but-not-merged → built-but-not-merged wins). |
| 4 | Drift-flag suppression | Synthetic fixture: BRANCH-2 worktree built-but-not-merged + installed methodology-changelog matches worktree's; invoke `/pulse`'s drift section rendering; assert NO "vault forward-population" flag emitted. Negative test: installed diverges from both worktree AND main → flag IS emitted. |
| 5 | Ship + regression | `pytest --no-header -q` ⇒ 100% PASS; shippability catalog all rows PASS; BC-PROJ-9 5-inventory pin PASSES for new module; CAD-1 byte-equality on `skills/pulse/SKILL.md`; 14+ Step-6 audits clean; APED-1 battery shows observed ≡ expected across ≥3 fixtures. |

## Must-not-defer

- [ ] **CAD-1 / OSDG-1 byte-equality** for `skills/pulse/SKILL.md` repo↔installed after Step 1 edits; forward-sync via `cp -p skills/pulse/SKILL.md ~/.claude/skills/pulse/SKILL.md` and verify with `$PY -m tools.pulse_skill_drift_audit` (or symmetric `assert_md_forward_synced` invocation per slice-049 OSDG-1 pattern).
- [ ] **BC-PROJ-9 5-inventory** for new `tools/pulse_worktree_resolver.py` module (plugin.yaml tools block + `_CANONICAL_TOOLS` + INSTALL.md tool-count literal `31 → 32` at BOTH L22 AND L166 + shippability row #77 + `_ROOT_ONLY_TOOLS` test-utf8 inclusion — helper uses `--repo-root` with no positional slice arg → root-only bucket per slice-067 / parallel_conflict_resolver precedent).
- [ ] **APED-1 empirical execution** on `detect_active_worktrees` + `classify_worktree_state` against **≥13 enumerated synthetic-worktree fixtures**: detect {empty, one-slice-worktree, multiple-slice-worktrees, non-slice-branch-filtered, mixed-slice-and-non-slice, stale-prunable} = 6 + classify {IN_PROGRESS, BUILT_BUT_NOT_MERGED, MERGED, UNKNOWN-no-milestone, UNKNOWN-malformed-frontmatter, UNKNOWN-git-merge-base-error, UNKNOWN-head-unresolvable} = 7. Verify observed-behavior matches expected per fixture. Captured in `architecture/slices/slice-077-enhance-pulse-with-worktree-awareness/aped_1_battery.py`. Floor raised from `≥6` per slice-076 28-case precedent + critique M8 ACCEPTED-FIXED.
- [ ] **MEPD-1 path declared in design.md** — EXCLUDE preview at mission-brief authoring time (no methodology-changelog entry, no PMI-1 bump; skill behavior enhancement bounded to `/pulse` Step 1 read-path; OSDG-1 / CAD-1 already cover the SKILL.md drift discipline). /design may upgrade to mint PWA-1 (Pulse Worktree-Awareness rule) if /critique surfaces rule-class evidence (e.g., cross-skill propagation need, or rule-axis sibling-rule visibility benefit); upgrade triggers PMI-1 5-leg bump 0.73.0 → 0.74.0 + ADR-070.
- [ ] **PCA-1 pipeline position UNCHANGED** for `/pulse` — `auto-advance: false` (terminal observability skill; hands off to next-skill suggestion as text, never auto-invokes); PWA enhances Step 1 within the same skill, doesn't change auto-advance contract.
- [ ] **Fail-closed on UNKNOWN worktree state** — if `git worktree list --porcelain` parsing fails OR returns unexpected schema OR the resolved milestone.md path doesn't exist on disk, FALL BACK to main-tree-only behavior (current `/pulse` behavior preserved on parse failure) AND surface a one-line WARN in `/pulse`'s Drift & flags section noting the detection failure. Never read from an undetermined worktree path; never silent-default to "merged" or "built-but-not-merged" on UNKNOWN.
- [ ] **Worktree-aware override is additive to existing /pulse output** — does NOT remove main-tree milestone.md reading (preserved for the no-worktree case + cross-comparison); does NOT remove the cadence-overdue critic-calibrate override mechanism (preserved as a lower-precedence alternative when no worktree-state override fires).

## Out of scope

- **VAULT_CLAIM / HARD conflict resolution** — slice-078 (PCR-2) per slice-076 Deferred.
- **Cross-worktree state aggregation** for ≥2 simultaneous slice-* worktrees — v1 detects + surfaces each independently; no graph-aware aggregation. If a user has multiple parallel slice worktrees, /pulse lists them all with their individual states but does NOT compose a unified recommendation across them. Deferred to a future slice if multi-worktree scenarios surface as a real-use pain point.
- **Worktree-aware drift-check / build-check audit propagation** — `/drift-check` and `/build-checks` audits continue to read from cwd; no worktree-awareness added there.
- **`/pulse --full` mode worktree-specific enhancements** — v1 surfaces basic worktree-state info in default + `--full` modes uniformly. Mode-specific expansions deferred.
- **Worktree HEAD-vs-default classification beyond the 3-state taxonomy** — no `STALE` / `DETACHED` / `DIRTY` sub-states in v1. Fail-closed `UNKNOWN` covers all corner cases; sub-states can be promoted later if observed pattern justifies.

## Dependencies

- Prior slices: [[slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen]] — established the BRANCH-2 worktree-during-build workflow as the canonical pattern that surfaced this gap; [[slice-066-add-branch-2-worktree-isolation]] (or its lineage) — defines BRANCH-2 worktree-path + branch-name conventions.
- Vault refs: [[skills/pulse/SKILL.md]] (modified), [[decisions/ADR-063]] (BRANCH-2), [[methodology-changelog#v0.50.0]] (CAL-1 cadence-overdue override — preserved as lower-precedence fallback).
- Risk register: no entry currently tracks the witnessed gap; /design may register an R-NN entry OR fold the witnessing into the slice's reflection as a Discovered-class observation.

## Mid-slice smoke gate

At ~50% of build (helper module + classify_worktree_state implemented; SKILL.md edits not yet finalized), run:

```
$PY -m tools.pulse_worktree_resolver --detect --json
```

Expected: from main repo with no slice-* worktree → `{"action": "DETECT", "worktrees": []}` exit 0. From a synthetic worktree fixture → `{"action": "DETECT", "worktrees": [{"path": "...", "branch": "slice/NNN-...", "head_sha": "...", "milestone_path": "..."}]}` exit 0. If output doesn't parse as JSON or `--detect` exits non-zero on a clean repo: STOP, diagnose before continuing.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (CAD-1 / OSDG-1 byte-equality + BC-PROJ-9 5-inventory + APED-1 battery + MEPD-1 declared + PCA-1 unchanged + fail-closed UNKNOWN + additive-to-existing-output)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] 14+ Step-6 audits clean (TF-1 + BRANCH-2 + UTF8-STDOUT-1 + CRP-1 + PCA-1 + BCI-1 + MCFS-1 + STP-1 + AVFS-1 + TVFS-1 + NAW-1 + CAD-1 + PMI-1 v0.73.0 unchanged-if-EXCLUDE / v0.74.0-if-PWA-1-minted + SCMD-1 + shippability runner)
- [ ] CAD-1 / OSDG-1 byte-equality verified post-Step 1 edit; installed `~/.claude/skills/pulse/SKILL.md` byte-equal-modulo-EOL to in-repo
- [ ] 3-Critic stack disposition recorded (design-Critic + meta-Critic at /critique-review + code-Critic at /code-review) per CRSI-1 v1 advisory-only + voluntary-restraint precedent
