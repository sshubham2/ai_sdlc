# Slice 076: add-pcr-1-conflict-diagnostic-and-soft-regen

**Mode**: Standard
**Estimated work**: ~1 day (MEDIUM — new rule + new helper + commit-slice SKILL.md enhancement + tests + PMI-1 bump)
**Risk retired**: 5-session parallel-slice workflow deadlock at `/commit-slice --merge` — every parallel slice regenerates `architecture/slice-queue.md` + `architecture/slices/_index.md` + appends rows to `architecture/shippability.md` + adds entries to `methodology-changelog.md`. PSQ-3 currently STOPs on every such rebase conflict and asks for manual resolution. For a 5-session pipeline, that's 4+ manual STOPs per merge sequence — defeats the parallel-slice value proposition. This slice ships the soft-conflict auto-regen path + the full-detail diagnostic for ALL conflict classes, closing the most-common conflict shape silently while preserving the safe STOP for source-code conflicts.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Mint a new rule **PCR-1** (parallel-conflict-resolution v1) — first rule on the parallel-conflict-resolution axis, sibling to PSQ-3 (rebase-and-conflict-discipline) but distinct layer (PSQ-3 = detect conflict; PCR-1 = resolve conflict). Define the 3-class taxonomy (soft / vault-claim / hard) with worked examples. Ship the diagnostic + soft-conflict-resolution paths in this slice; defer vault-claim + hard-conflict + TRI-RESOLVE-1 to PCR-2 (slice-077).

After this slice ships: a 5-session parallel-slice workflow whose only conflict surface is auto-regenerated state files (slice-queue / _index / shippability / methodology-changelog) merges automatically with no human prompt. Source-code conflicts STOP loud with the full-detail diagnostic (which slices, which files, which lines, claim history, last-commit time, mission-brief links) — slice-077 will then plug the Critic stack into the STOP path.

## Acceptance criteria

1. **PCR-1 rule minted + 3-class taxonomy documented**: new methodology-changelog v0.73.0 entry naming `PCR-1` as the rule reference + ADR-069 (number assigned at /design) authoring the parallel-conflict-resolution-mechanism architectural decision. 3-class taxonomy (`SOFT` / `VAULT_CLAIM` / `HARD`) defined with worked examples (which files fall into each, why) — either inline in ADR-069 or as a new vault file `architecture/parallel-conflict-resolution.md` (decision at /design). `SOFT` class is the auto-regen path shipped in this slice; `VAULT_CLAIM` + `HARD` are explicitly declared "defer to PCR-2 / slice-077".

2. **Enhanced conflict-STOP diagnostic at `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5**: when rebase conflicts surface, the existing STOP block is enhanced to print a structured diagnostic for each U-prefixed file: (a) which active slices have that file in their declared blast-radius (from `architecture/slice-queue.md` if it was a candidate, OR from each active slice's `mission-brief.md` TF-1 plan / Dependencies if it's an active slice); (b) claim history (Claimed-by, Claimed-at if vault-claim conflict on slice-queue.md); (c) last-commit time per concerned slice (`git log -1 --format="%cI" <slice-branch>`); (d) mission-brief.md link for each concerned slice (markdown-rendered relative path). This diagnostic fires for ALL classes (SOFT / VAULT_CLAIM / HARD) — it's the universal "what's actually conflicting" surface.

3. **Soft-conflict auto-regen path**: when `git status --porcelain` U-prefixed entries are ALL members of the SOFT-class file set (`architecture/slice-queue.md`, `architecture/shippability.md`) AND nothing else, the new helper auto-resolves: dispatch to the appropriate resolution tool for each file (for `slice-queue.md`: take the rebase-target branch's queue as candidate baseline + merge claims from BOTH branches via `tools.slice_queue_claim.parse_queue_text` + write via `tools.slice_queue_writer.write_slice_queue` — candidates that exist only on the rebased branch are dropped, will re-surface at next `/slice` regen; for `shippability.md`: row-union merge by slice number + ascending sort) + `git add` the resolved files + `git rebase --continue`. NO SOAD-1 prompt; logged to a new `architecture/parallel-conflict-resolution-log.md` for audit. If any non-SOFT file is among the U-entries, the soft-regen path is BYPASSED and the full conflict-STOP fires (deferred to PCR-2 for vault-claim + hard). **`architecture/slices/_index.md` is NOT in SOFT** — the `/archive` skill's `_index.md` regen is Haiku-LLM-dispatched per COST-1 (not deterministic); PCR-1 cannot auto-reproduce Haiku output, so `_index.md` conflicts fall to HARD-class until PCR-2 (or a manual `/archive` re-run post-merge). **`methodology-changelog.md` is NOT in SOFT** — PMI-1 5-leg atomic-bump risks subtle inconsistency on concurrent bumps (different RULE-IDs, paired-pin names, ADR refs).

4. **NEW helper `tools/parallel_conflict_resolver.py`** exposing library API + CLI: (a) `diagnose_conflict(repo_root: Path) -> ConflictDiagnostic` returning structured `ConflictDiagnostic` with U-files + concerned-slices map + claim-history + commit-times + mission-brief-links; (b) `classify_conflict(diag: ConflictDiagnostic) -> ConflictClass` returning `SOFT` / `VAULT_CLAIM` / `HARD` / `MIXED`; (c) `resolve_soft_conflict(diag: ConflictDiagnostic) -> ResolutionResult` for SOFT class only — VAULT_CLAIM + HARD + MIXED return early with `ResolutionResult(action="STOP", reason=...)`. CLI: `python -m tools.parallel_conflict_resolver [--diagnose | --classify | --resolve-soft] [--json]`. The `--resolve-soft` path is what `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 dispatches to BEFORE falling through to the existing SOAD-1 STOP block.

5. **End-to-end ship + regression-free**: PMI-1 5-part atomic bump 0.72.0 → 0.73.0 (`VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## v0.73.0` header + installed `~/.claude/ai-sdlc-VERSION`); BC-PROJ-10 paired-pin tests `test_v_0_73_0_pcr_1_entry_present_in_repo` + `test_v_0_73_0_pcr_1_shippability_consumer_propagation`; BC-PROJ-9 5-inventory for new `tools/parallel_conflict_resolver.py` (plugin.yaml tools + `_CANONICAL_TOOLS` + INSTALL.md tool-count + this shippability row + test-utf8 root-only-tools); shippability row added for slice-076; CAD-1 byte-equality on `skills/commit-slice/SKILL.md` repo↔installed; pytest 100% PASS (no regression vs slice-075 baseline + ~10-12 new tests added); 14 Step-6 audits clean; 3-Critic stack disposition recorded.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology / v0.73.0 entry-pin | tests/methodology/test_methodology_changelog.py | test_v_0_73_0_pcr_1_entry_present_in_repo | WRITTEN-FAILING |
| 1 | methodology / v0.73.0 shippability | tests/methodology/test_methodology_changelog.py | test_v_0_73_0_pcr_1_shippability_consumer_propagation | WRITTEN-FAILING |
| 1 | methodology / PMI-1 5-part atomic | tests/methodology/test_methodology_changelog.py | test_version_files_synchronized_at_v_0_73_0 | WRITTEN-FAILING |
| 1 | methodology / ADR existence | tests/methodology/test_pcr_1_adr_present.py | test_adr_069_parallel_conflict_resolution_mechanism_exists | PASSING |
| 1 | methodology / taxonomy doc | tests/methodology/test_pcr_1_taxonomy_documented.py | test_three_class_taxonomy_lists_soft_vault_claim_hard | PASSING |
| 2 | methodology / commit-slice SKILL.md prose | tests/methodology/test_commit_slice_skill_pcr_1_diagnostic.py | test_step_5b_substep_2_5_emits_full_concerned_slice_diagnostic | WRITTEN-FAILING |
| 2 | methodology / commit-slice SKILL.md prose | tests/methodology/test_commit_slice_skill_pcr_1_diagnostic.py | test_diagnostic_includes_blast_radius_claim_history_commit_time_mission_brief_link | WRITTEN-FAILING |
| 3 | unit / soft-regen | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_dispatches_to_slice_queue_writer_for_slice_queue_conflict | PASSING |
| 3 | unit / soft-regen | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_appends_shippability_rows_from_both_branches | PASSING |
| 3 | unit / soft-regen | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_shippability | PASSING |
| 3 | unit / soft-regen | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_slice_queue | PASSING |
| 3 | unit / claim overlay | tests/skills/parallel_conflict_resolver/test_overlay_claims_on_queue_text.py | test_overlay_claims_on_queue_text_inserts_claimed_by_under_risk_retired_for_new_claim | PASSING |
| 3 | unit / claim overlay | tests/skills/parallel_conflict_resolver/test_overlay_claims_on_queue_text.py | test_overlay_claims_on_queue_text_replaces_existing_claim_with_newer_claimed_at | PASSING |
| 3 | unit / claim overlay | tests/skills/parallel_conflict_resolver/test_overlay_claims_on_queue_text.py | test_overlay_claims_on_queue_text_drops_claims_for_candidates_absent_from_target_text | PASSING |
| 3 | unit / soft-regen | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_bypassed_when_mixed_with_hard_file | PASSING |
| 3 | unit / soft-regen | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_aborts_when_post_merge_claim_dict_has_same_candidate_different_identities | PASSING |
| 3 | unit / SOFT file-set pin | tests/skills/parallel_conflict_resolver/test_soft_file_set.py | test_soft_file_set_is_two_canonical_files_forward_slash_keyed | PASSING |
| 3 | unit / audit logging | tests/skills/parallel_conflict_resolver/test_audit_log.py | test_soft_conflict_resolution_appends_to_parallel_conflict_resolution_log | PASSING |
| 4 | unit / helper library API | tests/skills/parallel_conflict_resolver/test_diagnose_conflict.py | test_diagnose_conflict_returns_conflict_diagnostic_with_concerned_slices_map | PASSING |
| 4 | unit / classify_conflict | tests/skills/parallel_conflict_resolver/test_classify_conflict.py | test_classify_conflict_returns_soft_when_all_u_files_are_in_two_member_soft_set | PASSING |
| 4 | unit / classify_conflict | tests/skills/parallel_conflict_resolver/test_classify_conflict.py | test_classify_conflict_returns_hard_when_any_source_file_present | PASSING |
| 4 | unit / classify_conflict | tests/skills/parallel_conflict_resolver/test_classify_conflict.py | test_classify_conflict_returns_mixed_when_soft_and_hard_coexist | PASSING |
| 4 | unit / classify_conflict | tests/skills/parallel_conflict_resolver/test_classify_conflict.py | test_classify_conflict_returns_mixed_when_soft_and_vault_claim_coexist | PASSING |
| 4 | unit / classify_conflict | tests/skills/parallel_conflict_resolver/test_classify_conflict.py | test_classify_conflict_returns_vault_claim_when_same_candidate_claimed_by_different_identities_across_branches | PASSING |
| 4 | unit / classify_conflict fail-closed | tests/skills/parallel_conflict_resolver/test_classify_conflict.py | test_classify_conflict_returns_unknown_when_rebase_state_empty | PASSING |
| 4 | unit / resolve_soft_conflict fail-closed | tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py | test_resolve_soft_conflict_returns_stop_on_unknown_class | PASSING |
| 4 | unit / Windows path normalization | tests/skills/parallel_conflict_resolver/test_soft_file_set.py | test_soft_file_set_membership_uses_forward_slash_keys_on_windows_paths | PASSING |
| 4 | unit / CLI | tests/skills/parallel_conflict_resolver/test_cli.py | test_cli_emits_json_when_json_flag_passed | PASSING |
| 4 | unit / CLI | tests/skills/parallel_conflict_resolver/test_cli.py | test_cli_resolve_soft_exits_zero_on_successful_soft_regen | PASSING |
| 5 | methodology / BC-PROJ-9 5-inventory | tests/methodology/test_parallel_conflict_resolver_tool_inventory.py | test_parallel_conflict_resolver_in_canonical_tools_plugin_manifest_install_md_at_l22_and_l166 | WRITTEN-FAILING |
| 5 | methodology / CAD-1 commit-slice drift | tests/methodology/test_commit_slice_skill_drift.py | test_in_repo_and_installed_commit_slice_skill_md_are_content_equal | PASSING |
| 5 | end-to-end regression | (manual) | full pytest + shippability + 14 Step-6 audits | PENDING |

<!-- TF-1 status legend: PASSING = test exists and passes today (pinning Phase A scaffolding OR a pre-existing canonical test re-verified post-edit). WRITTEN-FAILING = test exists at Phase B and fails for the right reason (NotImplementedError from skeleton, or missing-prose/missing-anchor that Phase C-F will resolve). PENDING = test not yet authored (e.g., the manual end-to-end row at AC5). The PASSING status on the CAD-1 row is the canonical re-verify-existing-test annotation per slice-026 / ADR-024 precedent: an existing test exercised by this slice but not authored by it; it must continue passing after the SKILL.md edit at Phase E. -->


## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Rule + ADR + taxonomy | Read methodology-changelog v0.73.0 entry; read ADR-069; verify 3-class taxonomy documented with examples for each class; pytest entry-pin tests PASS. |
| 2 | Enhanced diagnostic | Synthetic conflict fixture: induce a rebase conflict on slice-queue.md + a source file; run /commit-slice --merge; assert printed STOP block contains the 4 structured fields (concerned slices, blast-radii, claim history, commit times, mission-brief links) for EACH U-file. |
| 3 | Soft-conflict auto-regen | Synthetic conflict fixture: 2 slice branches both touching ONLY slice-queue.md + shippability.md (no source files); rebase one onto the other; assert auto-regen dispatched, files staged, `git rebase --continue` succeeded WITHOUT human prompt; assert audit log entry written. Negative test: same fixture + 1 source file added → auto-regen BYPASSED, full STOP fires. |
| 4 | Helper API + CLI | `python -c "from tools.parallel_conflict_resolver import diagnose_conflict, classify_conflict, resolve_soft_conflict, ConflictDiagnostic, ConflictClass, ResolutionResult"`; CLI `--json` returns parseable JSON; `--resolve-soft` exits 0 on success, non-zero with diagnostic on failure. |
| 5 | Ship + regression | `pytest --no-header -q` ⇒ 100% PASS; shippability catalog all rows PASS; methodology-changelog v0.73.0 + ADR-069 + PCR-1 pinned by tests; 14 Step-6 audits clean; CAD-1 byte-equality on commit-slice SKILL.md. |

## Must-not-defer

- [ ] **CAD-1 byte-equality** for `skills/commit-slice/SKILL.md` repo↔installed after the Step 5b sub-step 2.5 edits; forward-sync via `cp -p skills/commit-slice/SKILL.md ~/.claude/skills/commit-slice/SKILL.md` and verify with `$PY -m tools.commit_slice_skill_drift_audit` (or symmetric OSDG-1 invocation).
- [ ] **PMI-1 5-part atomic bump** 0.72.0 → 0.73.0 (all 5 legs in lockstep) + methodology-changelog v0.73.0 entry + BC-PROJ-10 paired-pin functions.
- [ ] **BC-PROJ-9 5-inventory** for new `tools/parallel_conflict_resolver.py` module (plugin.yaml tools block + `_CANONICAL_TOOLS` + INSTALL.md tool-count literal NN → NN+1 + this shippability row + `_ROOT_ONLY_TOOLS` test-utf8 inclusion).
- [ ] **APED-1 empirical execution** on FOUR minted predicates (per /critique M1 + /critique-review M-add-5 ACCEPTED-FIXED — APED-1 just-extended scope covers all parse-time-evaluated patterns the slice mints): (1) `_SOFT_FILE_SET` membership predicate; (2) `classify_conflict` 5-way classification logic; (3) `_extract_claim_diff` parser predicate (materially affects VAULT_CLAIM detection per /critique B4); (4) `_merge_shippability` row-union predicate. Real-corpus inputs for (1)+(2): synthetic conflict touching ONLY slice-queue.md (expected SOFT); ONLY shippability.md (expected SOFT); ONLY _index.md (expected HARD — not in SOFT-set); ONLY methodology-changelog.md (expected HARD); ONLY a source file (expected HARD); SOFT+HARD mix (expected MIXED); SOFT+VAULT_CLAIM mix (expected MIXED); same-candidate-different-identity claim collision (expected VAULT_CLAIM); empty rebase state (expected UNKNOWN — fail-closed); dotfile/hidden-path in U-set (expected HARD by default-deny since not in 2-member SOFT-set); Windows-backslash-path vs forward-slash-path representations of the same file (membership must be normalized — per M1 fix). Real-corpus inputs for (3) `_extract_claim_diff`: empty queue text → empty diff dict; queue with no claims → empty diff; queue with same-candidate-same-identity claims on both branches (newer timestamp → diff captures the newer); same-candidate-DIFFERENT-identity → diff flags VAULT_CLAIM trigger; cp1252 mojibake in `Claimed-by:` value → parser tolerates or fails-closed loudly. Real-corpus inputs for (4) `_merge_shippability`: two branches with disjoint slice-number row additions → row-union with both; two branches with same-slice-number row + same content → idempotent; two branches with same-slice-number row + different content → STOP with HARD diagnostic (per design.md Edge-cases column); empty header on one side → preserved from the other; non-`| <NN> |` rows (header / separator / footer) → preserved verbatim. Per Dim 9 sub-clause #12 (APED-1) §When reviewing a slice that mints any parse-time-evaluated pattern: execute the predicates against this adversarial battery and state observed behavior "executed not reasoned" in the build-log.
- [ ] **MEPD-1 (a) rule path declared** in design.md — this slice mints a new rule (PCR-1) on a new family axis (parallel-conflict-resolution); take the RULE-ID + entry-pin + PMI-1 atomic-bump path, NOT the documented-why-none path.
- [ ] **PCA-1 pipeline position UNCHANGED** for `/commit-slice` — `auto-advance: false` (always user-invoked) per ADR-020; PCR-1 enhances Step 5b sub-step 2.5 within the same skill, doesn't change the skill's auto-advance contract.
- [ ] **Conflict-class fail-closed** — if `classify_conflict` cannot determine a class (e.g., U-entries empty when rebase is in progress, or unexpected git state), return `UNKNOWN` and STOP loud with diagnostic; never silent-default to SOFT (avoid auto-regen of unintended files). APED-1's silent-disable / default-off-on-malformed criterion applies directly.
- [ ] **Forward references to PCR-2 (slice-077)** explicit in PCR-1 prose — the VAULT_CLAIM + HARD classes are explicitly declared "STOP for now; PCR-2 will plug in resolution paths"; no silent gap.

## Out of scope

- **VAULT_CLAIM conflict resolution** (timestamp-winner + light Critic) — slice-077 PCR-2.
- **HARD conflict full Critic stack** (`/critique` + `/critique-review` on proposed resolution) — slice-077 PCR-2.
- **TRI-RESOLVE-1 user triage** mirroring TRI-1 for resolution dispositions — slice-077 PCR-2.
- **`/slice` no-arg auto-pick** via `tools/slice_pick.py` (the ergonomics enhancement; user's Option C) — slice-078 SP-1.
- **Bundle-074-code-critic-cleanup** (P1.1 variable-scope footgun + P3.10 cp1252 mojibake + slice-074 m1-m5 deferrals) — slice-079+ (re-queued).
- **`/commit-slice --push`-time rebase** (the originally-reserved PSQ-4 slot) — re-numbered to PSQ-5 in the queue per the parallel-conflict-resolution family taking precedence.
- **Graphify-derived blast-radius for active slices** (calling graphify against active mission-brief data) — slice-076 uses the mission-brief data directly; graphify integration deferred to slice-078+ if false-negatives surface.
- **Pick-algorithm tuning** for the future /slice-pick — slice-078 concern.

## Dependencies

- Prior slices: [[slice-066-add-worktree-per-slice-discipline]] (BRANCH-2 — worktree isolation enabling physical parallelism); [[slice-067-add-parallel-slice-queue-output]] (PSQ-1 — queue file + Parallel-safety enum); [[slice-072-add-psq-2-claim-machinery]] (PSQ-2 — Claimed-by/Claimed-at fields, depended-on by VAULT_CLAIM class detection); [[slice-073-add-rebase-and-conflict-discipline]] (PSQ-3 — rebase at /commit-slice --merge sub-step 2.5; PCR-1 inserts the auto-regen branch BEFORE PSQ-3's existing SOAD-1 STOP).
- Vault refs: [[skills/commit-slice/SKILL.md]] (Step 5b sub-step 2.5 — edit site); [[tools/slice_queue_writer.py]] (soft-regen dispatcher for slice-queue.md); [[tools/state_transition_pin_audit.py]] (precedent for tool-as-resolver pattern); [[decisions/ADR-068]] (PSQ-3 — direct predecessor); [[decisions/ADR-067]] (PSQ-2 — Claimed-by/Claimed-at format).
- Risk register: no open HIGH-band risk retired; this slice closes the 2026-05-28-surfaced parallel-slice deadlock-on-soft-conflict gap.
- Methodology family: NEW rule family `PCR-N` (parallel-conflict-resolution) — sibling to PSQ-N (parallel-slice-queue). PCR-1 = this slice; PCR-2 = slice-077 (vault-claim + hard).
- New ADR: ADR-069-parallel-conflict-resolution-mechanism (reversibility: expensive — once the soft-regen path lands and parallel sessions rely on it, reverting requires reverting their conflict-resolution expectation).

## Mid-slice smoke gate

At ~50% of build (after AC1+AC2 land, before AC3 soft-regen + AC4 helper):

```bash
PY="$USERPROFILE/.claude/.venv/Scripts/python.exe"

# Smoke 1 — Rule entry + ADR present
grep -q "## v0.73.0" methodology-changelog.md
grep -q "PCR-1" methodology-changelog.md
test -f architecture/decisions/ADR-069-*.md

# Smoke 2 — commit-slice SKILL.md diagnostic block present
grep -q "concerned slices" skills/commit-slice/SKILL.md
grep -q "claim history" skills/commit-slice/SKILL.md
grep -q "blast-radius" skills/commit-slice/SKILL.md

# Smoke 3 — entry-pin tests defined (even if PENDING)
"$PY" -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_73_0_pcr_1_entry_present_in_repo --co -q

# Smoke 4 — SOFT file-set is the 2-member canonical set (post-Critic B3 reduction)
"$PY" -c "from tools.parallel_conflict_resolver import _SOFT_FILE_SET; assert _SOFT_FILE_SET == frozenset({'architecture/slice-queue.md', 'architecture/shippability.md'}), f'SOFT drift: {sorted(_SOFT_FILE_SET)}'"
```

If any smoke fails: STOP. Diagnose at source. Do NOT continue to AC3/AC4 on top of a missing v0.73.0 entry or absent diagnostic prose.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] Must-not-defer list (8 items above) fully addressed
- [ ] `/drift-check` passes (CAD-1 + OSDG-1 + plugin manifest + install audit all clean)
- [ ] Mid-slice smoke (rule entry + ADR + diagnostic prose + entry-pin) still passes
- [ ] No new TODOs / FIXMEs / debug prints in source diff
- [ ] 14 Step-6 audits clean (BC-1 / RR-1 / PMI-1 / CAD-1 / OSDG-1 / INST-1 / WS-1 / ETC-1 / WIRE-1 / TF-1 / VAL-1 / CSP-1 / SUP-1 / LINT-MOCK-1-2-3)
- [ ] 3-Critic stack disposition recorded: `critique.md` + `critique-review.md` + `code-review.md`; CRSI-1 v1 walking-skeleton advisory-only — code-Critic findings may defer to next bundle per voluntary-restraint discipline (N=16 cumulative if deferred)
- [ ] Slice-queue.md regenerated to ADD: bundle-074-code-critic-cleanup (re-added as candidate; the original slice-076 scope); slice-077-add-pcr-2-vault-claim-and-hard-conflict-critic-stack (PCR-2 follow-on); slice-078-add-sp-1-slice-pick-auto-pick (SP-1 follow-on); add-psq-5-push-time-rebase renumbered from prior PSQ-4 reservation
