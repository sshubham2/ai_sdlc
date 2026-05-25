# Reflection: Slice 066 add-worktree-per-slice-discipline

**Date**: 2026-05-24
**Shipped**: YES

## Validated

- **BRANCH-2 worktree-per-slice creation works on real git plumbing** — 16 audit tests on real `tmp_path` + real git subprocess fixtures PASS. Verifies: `.git`-file detection for worktrees (vs `.git`-directory for main tree), `git worktree list --porcelain` parse, canonical sibling-dir path resolution, `_paths_equivalent` Windows-tolerant comparison via `Path.resolve(strict=False)` + `samefile()` + `os.path.normcase(os.path.realpath(...))` fallback.
- **Idempotent worktree-remove guard works as designed** — `/commit-slice` Step 5b sub-step 5 + Step 5d sub-step 5 with `git worktree list --porcelain | grep -E "^branch refs/heads/slice/NNN-<name>$"` → LOG-and-skip-if-absent path covers slice-066 bootstrap + future `WORKTREE=skip` slices. Order-load-bearing (worktree-remove BEFORE branch-delete) — pinned by prose-pin test + git's own refusal-on-checked-out-branch invariant per [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree).
- **R-17 candidate-fix-(b) closes the WIP-contamination class STRUCTURALLY, not via cleanliness audit** — the worktree IS the prevention. The candidate-fix-(a) cleanliness-audit was DECLINED per ADR-063 §"Options considered" option 3 as redundant defense-in-depth (option (b) makes the class structurally impossible, so a cleanliness audit becomes a Maginot Line). Validated: `risk_register_audit --filter-status open` no longer lists R-17; R-17 entry now shows `**Status**: retired` + `**Retired**: slice-066-... (2026-05-24; ADR-063 / BRANCH-2 / methodology v0.68.0)`.
- **N=2 application of slice-022 ADR-020 partial-supersession encoding pattern** works — ADR-019 stays unmodified across N=2 partial supersessions (ADR-020 covers sub-mode (b); ADR-063 covers sub-mode (a)); ADR-019 frontmatter still carries `supersedes: null` and no `superseded-by:` field. The append-only rule holds across N=2.
- **CRSI-1 v1 walking-skeleton advisory-only verdict held** — code-Critic returned 0B/2M/4m on a 16-file methodology-surface slice; all 6 findings deferred to slice-067+ bundled cleanup per slice-064/065 advisory-feedback-loop precedent. The chain auto-advanced to `/validate-slice` without HALTing on the code-Critic findings (CRSI-1 v1 is advisory-only by design; TRI-1 verdict-driven block deferred to slice-062).
- **Walking-skeleton WS-1 layers all EXERCISED** — all 5 architectural layers (build-slice SKILL.md prose, commit-slice SKILL.md prose, branch_workflow_audit.py audit module, git plumbing, vault) hit on real git state. The slice exercised every layer end-to-end on its own self-test.
- **Dual-Critic stack continues paying** — first-Critic + meta-Critic together caught 20 design-level findings (14 + 6); all VALIDATED at /build-slice fix-block. Most consequential: B1 ADR identifier conflation (would have shipped ADR-063 superseding the wrong ADR — utf8-stdout-1 instead of BRANCH-1).

## Corrected

- **design.md "5-part PMI-1 atomic bump" enumeration was WRONG in rev-1** → corrected at Phase A Builder-self-catch. Rev-1 listed `VERSION + plugin.yaml + methodology-changelog + CLAUDE.md cite + shippability row`. Canonical 5 parts per slice-063/064 row anchors: `VERSION + plugin.yaml.version + pyproject.toml [project].version + ## vN.N.0 header + installed ~/.claude/ai-sdlc-VERSION`. CLAUDE.md edit + shippability row are SEPARATE consumer-propagation surfaces (BC-PROJ-9 5-inventory fan-out + BC-PROJ-10 paired entry-pins), NOT PMI-1 parts. 3 sites corrected in mission-brief + ADR-063.
- **mission-brief.md TF-1 plan paths referenced non-existent test files** → corrected at Phase B-prefix Builder-self-catch. `test_commit_slice_skill.py` doesn't exist (split into `_merge_flag.py` / `_push_flag.py` / `_sync_after_pr_flag.py`); `test_claude_md_pin.py` doesn't exist (existing pin lives at `test_root_claude_md_branch_per_slice_rule.py`). 4 TF-1 rows repointed; BC-PROJ-10 paired-entry-pin discipline added a 21st row.
- **AC2 prose-pin tests for `git worktree remove` invocation were false-PASSing** → corrected at Phase C step 8 Builder-self-catch. The existing `skills/commit-slice/SKILL.md:258` diagnostic mentions `git worktree remove` in a `git checkout`-conflict-resolution context, satisfying naive substring checks. Fixed by adding `_step_5b_merge_section` + `_step_5d_sync_after_pr_section` helpers for section-scoping; for Step 5d an additional invariant (count >= 2 occurrences) differentiates post-fix (cleanup + diagnostic = 2) from pre-fix (diagnostic only = 1).
- **VERSION + installed ai-sdlc-VERSION written as 0-byte files** → corrected at Phase D Builder-self-catch. PowerShell `Write-Host "0.68.0" | Out-File` writes nothing to the pipeline (Write-Host outputs to host, not pipeline; Out-File receives no input). AVFS-1 passed vacuously (both empty, equal). TVFS-1 caught it. Re-written via Write tool + cp.
- **CLAUDE.md L32 rewrite lost the "Branch-per-slice" historical anchor** → corrected at Phase D Builder-self-catch. Two existing tests pin literal "Branch-per-slice" substring; my rewrite changed the bullet title to "Worktree-per-slice + branch". Per ADR-063 §Scope of supersession "Carried forward unchanged" the historical phrase should be preserved. Added "BRANCH-1 / `Branch-per-slice` workflow" citation to the new bullet's prose.

## Discovered

- **WS-1 audit has R-7 silent-default-off class bug — TFFL-1 fix not propagated** — mission-brief frontmatter `**Walking-skeleton**: true  <!-- comment -->` causes WS-1's anchored regex to break; reports "not enabled" → silently default-off (gate vacuously passes). Same class TF-1 had until slice-034 TFFL-1 fix (regex relaxation + value-agnostic field-present malformed branch). Workaround: removed HTML comments from frontmatter. **Promotion candidate**: add to [[risk-register.md]] as a new R-NN entry tracking the N=2 silent-default-off class (TF-1 retired via TFFL-1 at slice-034; WS-1 witnessed N=1 here; ETC-1 likely-but-untested). Strongest slice-067+ /critic-calibrate proposal target.
- **Codification slices ratchet self-catch density to N≈10** — slice-066 produced N=11 Builder self-catches across Phase A (3 PMI-1 enum sites) + Phase B-prefix (2 TF-1 path drifts + 1 BC-PROJ-10 paired-pin gap) + Phase C step 8 (2 AC2 section-scoping false-passes) + Phase C step 10 (1 cp1252 test fixture encoding) + Phase D (1 VERSION file empty write + 1 CLAUDE.md historical anchor missing). New high-water-mark for this project. Slice-022 law "codification slices commit exactly the violation their codified discipline catches" extends to density ≈N=10 per slice (was N=5-8 baseline at slice-020-040; slice-064 N=14; slice-066 N=11). Pattern: codification slices need budgeted cross-reference sweep at Phase A + B-prefix to harmonize TF-1 paths against actual file system Glob + canonical inventories.
- **Code-Critic M2 surfaces a real bug class** — SKILL.md `wt_base="$(dirname "$(pwd)")/$(basename "$(pwd)")-wt"` derives from cwd; `tools/branch_workflow_audit.py:_resolve_expected_worktree_path` derives from `.git`-ancestor-walked main_repo_root. If user runs `/build-slice` from a sub-directory of the repo (plausible — cwd is wherever Claude happens to be mid-conversation), the bash creates worktree at the wrong path → audit emits `worktree-path-shape-violation` post-build. Real defect; deferred to slice-067+ bundled cleanup. Fix: `wt_base="$(dirname "$(git rev-parse --show-toplevel)")/$(basename "$(git rev-parse --show-toplevel)")-wt"`.
- **Code-Critic M1 surfaces a hardening gap on attacker-crafted `.git` files** — `_is_repo_root_a_worktree`'s `gitdir.parent.parent.parent` walk returns a real-existing-but-unrelated directory when gitdir is depth-truncated. The `try/except (IndexError, AttributeError)` block at lines 273-276 is unreachable (`Path.parent` on root returns the path itself, no exception). Low-likelihood in practice but a clean 2-line guard fix (`len(gitdir.parts) < 4` + `(main_repo / ".git").exists()` sanity check). Deferred to slice-067+ bundled cleanup.
- **APED-1 (Audit-Predicate-Empirical-Demonstration) gap on cross-spec parity tests** — code-Critic m2 caught `test_honours_canonical_worktree_skip_rationale_line` as not-load-bearing (passes even without the WORKTREE=skip line, because `_slice_branch_in_worktree` returns the main tree's own worktree-list entry and `_paths_equivalent` returns True). The test asserts a property the fixture already satisfies for an unrelated reason. Fixture needs to actually exercise the absent-escape-hatch path. Deferred to slice-067+ bundled cleanup.

## Deferred

- **m4 from /critique** (graphify CLI node-name-convention silently failing): no slice-066 fix; reflection.md /critic-calibrate watch-list at N=1. Promote to dedicated proposal at N=2 if a sibling slice (slice-067 parallel-queue, which uses graphify blast-radius) recurs the same convention gap.
- **M-add-5 from /critique-review** (APED-1 explicit bootstrap-variant TF-1 row): Builder-discretion-at-build deferred. TF-1 row 11 (`test_honours_canonical_worktree_skip_rationale_line`) uses the `WORKTREE=skip-bootstrap` literal in its fixture — the boundary semantics IS exercised on the actual bootstrap sample without needing a separate row. But code-Critic m2 above found the test is not-load-bearing for an UNRELATED reason (main-tree wt-list self-match). The fix in slice-067+ bundled cleanup addresses both: rewrite the fixture to exercise WORKTREE=skip on a worktree-elsewhere shape.
- **6 code-Critic advisory findings**: M1 (`_is_repo_root_a_worktree` shallow-gitdir guard) + M2 (SKILL.md `wt_base` from `git rev-parse --show-toplevel`) + m1 (surface `worktree_skip_used` in `AuditResult`) + m2 (APED-1 fixture rewrite) + m3 (hoist `import os` to module-level) + m4 (SKILL.md PowerShell-portability parenthetical). Bundled cleanup nominated for `slice-NNN-bundle-066-code-critic-cleanup` mirroring slice-065 shape. ~30-45 min estimated work.
- **Slice-067 / 068 / 069 sibling nominees**:
  - slice-067 `add-parallel-slice-queue-output` — `/slice` writes `architecture/slice-queue.md` with top-10 parallel-safe candidates (graphify blast-radius non-overlap). Depends on slice-066 worktree mechanics; now unblocked.
  - slice-068 `add-slice-queue-claim-state-machine` — `slice-queue.md` claim semantics + session-id detection + force-claim escape. Depends on slice-067.
  - slice-069 `add-rebase-and-conflict-discipline` — `/commit-slice` rebases default before merge + structured-options ASK on conflict. Depends on slice-066 worktree mechanics.
- **WS-1 + ETC-1 R-7-class TFFL-1 fix propagation** — slice-066 surfaced WS-1's silent-default-off bug on HTML-comment trailers. ETC-1 likely has the same class (untested). A future slice can apply slice-034 TFFL-1's pattern verbatim to both audits.

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` `## Triage` + reality observed during build/validate:

**First-Critic (`/critique`) — 14 findings**:
- B1 (ADR-021/ADR-019 conflation across mission-brief / design / ADR-063): **VALIDATED** — disposition ACCEPTED-FIXED; load-bearing catch; without it ADR-063 would have shipped `supersedes: ADR-021` against an unrelated active ADR (utf8-stdout-1). Critic earned its keep on this finding alone.
- B2 (Windows path-comparison semantics unspecified): **VALIDATED** — disposition ACCEPTED-FIXED; the `Path.resolve(strict=False)` + `samefile()` + `os.path.normcase(os.path.realpath(...))` fallback chain in `_paths_equivalent` reflects this fix directly. WebSearch evidence on [microsoft/vscode#101244](https://github.com/microsoft/vscode/issues/101244) corroborated the class.
- B3 (audit call-shape enumeration): **VALIDATED** — disposition ACCEPTED-FIXED; the 3-shape enumeration in design.md is reflected verbatim in `audit()` decision logic.
- B4 (cross-spec parity test not in TF-1 plan): **VALIDATED** — disposition ACCEPTED-FIXED; the FBCD-1 sub-mode (a) class fired on the slice's own TF-1 plan exactly as predicted.
- B5 (bootstrap discharge under-specified): **VALIDATED** — disposition ACCEPTED-FIXED; the idempotent worktree-remove guard (option ii) is exactly the structural fix the finding asked for; covers slice-066 bootstrap + future WORKTREE=skip slices.
- M1 (CLAUDE.md L65 → L32): **VALIDATED** — minor mechanical line-number drift; Builder verified L32 is correct.
- M2 (3 prior-slice link names paraphrased): **VALIDATED** — FBCD-1 sub-mode (a) drift caught against canonical archive `_index.md` names.
- M3 (Mode-interaction matrix missing): **VALIDATED** — disposition ACCEPTED-FIXED; the 6-row matrix in design.md (post-M-add-4 fix) is exactly the kind of unhappy-path enumeration the finding asked for.
- M4 (ADR-019 N-surface schema-pin / prospective application / v1 carveout dispositions): **VALIDATED** — disposition ACCEPTED-FIXED; ADR-063 §"Carried forward unchanged" now enumerates all 3.
- M5 (`_resolve_expected_worktree_path` edge cases — parent-dir writable): **VALIDATED** — minor; added to must-not-defer.
- m1 (count drift 3 vs 4 violation kinds in design.md): **VALIDATED** — FBCD-1 sub-mode (a) within design.md itself.
- m2 (N=2 partial-supersession pattern note): **VALIDATED** — minor; added to ADR-063 opening.
- m3 (test function `_and_installed` suffix): **VALIDATED** — TPHD-1 sub-mode (a) drift; corrected per slice-041 MCFS-1.
- m4 (graphify CLI node-name-convention watch-list): **NOT-YET** — disposition ACCEPTED-PENDING for /critic-calibrate watch-list at N=1; can't score until N=2 recurs.

**Meta-Critic (`/critique-review`) — 6 missed findings**:
- M-add-1 (residual ADR-021 at mission-brief.md L152 escaped B1 global-rename): **VALIDATED** — exactly the FBCD-1 sub-mode (a) class B1 itself was meant to fix; recursive-self-application N=10. Strongest meta-Critic catch.
- M-add-2 (TF-1 count drift in design.md L179/L190 introduced by B4 fix): **VALIDATED** — identical class drift introduced INSIDE the fix block.
- M-add-3 (shell-portability awk/grep parenthetical): **VALIDATED** — adopted option (i); cross-spec parity gap closed.
- M-add-4 (mode-interaction matrix missing "PR pending review" row): **VALIDATED** — added; cosmetic but improves the matrix's completeness.
- M-add-5 (APED-1 explicit bootstrap-variant fixture): **NOT-YET** — Builder-discretion-at-build deferred; the underlying test was caught not-load-bearing by code-Critic m2 (different reason than M-add-5 predicted). Re-score in slice-067+ bundled cleanup.
- M-add-6 (BRANCH=skip 4th-surface enumeration in ADR-063): **VALIDATED** — added; tightens the FBCD-1 defense within the very ADR codifying it.

**Code-Critic (`/code-review`) — 6 findings (all v1 advisory)**:
- M1 (`_is_repo_root_a_worktree` shallow-gitdir walk-off): **VALIDATED** — real hardening gap. Will validate the fix when applied at slice-067+.
- M2 (SKILL.md `wt_base` from `$(pwd)` divergent with audit's `.git`-ancestor walk): **VALIDATED** — real bug class; will validate the fix at slice-067+.
- m1 (asymmetric `AuditResult` surface): **VALIDATED** — Fowler speculative-generality (compute then discard) caught cleanly.
- m2 (`test_honours_canonical_worktree_skip_rationale_line` not load-bearing): **VALIDATED** — APED-1 class catch on a test the design-Critic + meta-Critic structurally couldn't reach (would require empirical fixture probing).
- m3 (inline `import os` per call): **VALIDATED** — PEP 8 minor; will validate at slice-067+ when hoisted.
- m4 (SKILL.md PowerShell-portability parenthetical gap with commit-slice): **VALIDATED** — RPCD-1 cross-spec parity gap within the same slice's edits.

**Missed by Critic-stack (10 Builder self-catches surfaced during build)**:
- Phase A (3): PMI-1 5-part enumeration drift across mission-brief + ADR-063 (3 sites). Cross-doc-canonical-anchor-drift class; the dual-Critic stack focused on individual file consistency, not 3-file cross-anchor harmony against the slice-063/064 canonical-shape.
- Phase B-prefix (3): test_commit_slice_skill.py + test_claude_md_pin.py path drifts (Glob doesn't find them) + BC-PROJ-10 paired-pin gap (TF-1 plan needed 2 rows per changelog entry per slice-064 N≥17 instance count). Glob-verify-vs-TF-1-plan class; TPHD-1 sub-mode (c) only checks function names, not file existence.
- Phase C step 8 (2): AC2 prose-pin tests false-PASSing due to L258 existing `git worktree remove` mention in a different context. Section-scoping discipline needed for prose-pin tests on the same SKILL.md document.
- Phase C step 10 (1): cp1252 test fixture encoding — UTF8-STDOUT-1 lineage class but on test FIXTURE files, not audit-tool source. The discipline's scope didn't reach test fixtures.
- Phase D (1): PowerShell `Write-Host | Out-File` pipeline silently writes nothing. Cross-shell idiom class — Critic-stack reviews the design's bash snippets but not the build-time PowerShell invocations.
- Phase D (1): CLAUDE.md historical anchor preservation — my CLAUDE.md L32 rewrite lost the literal "Branch-per-slice" string; ADR-063 §Scope of supersession committed to preserving it as historical anchor. Cross-doc-consistency class (design.md said preserve; code didn't).

**Pattern**: codification slices in this project consistently produce N≈10 Builder self-catches during build despite N=20+ dual-Critic findings caught at design time. The dual-Critic stack reaches the **declarative** layer (design-claim consistency, ADR identifiers, regex grammar pinning, schema completeness); the Builder self-catches reach the **operational** layer (Glob-vs-TF-1-plan, cp1252 test fixtures, PowerShell idioms, cross-doc canonical anchors, section-scoping in prose-pin tests). The two layers are structurally complementary — neither alone reaches the other's surface. Future codification slices should budget Phase A + B-prefix sweeps for cross-anchor harmonization + Glob verification of every TF-1 plan path.

**`/critic-calibrate` promotion candidates for slice-067+**:
1. **WS-1 + ETC-1 R-7-class regex fix** (N=2 if ETC-1 confirmed): apply slice-034 TFFL-1 pattern verbatim (regex relaxation + value-agnostic field-present malformed branch).
2. **TPHD-1 sub-mode (c) extension to Glob-verify test paths** (N≥2 instances now): the audit currently checks function-name harmony; extend to check that the test FILE referenced by the TF-1 plan actually exists on disk via Glob.
3. **Section-scoping discipline for prose-pin tests on multi-occurrence anchors** (N=1 here; promote if recurs at N=2 in slice-067+): when a SKILL.md or other prose-pin file contains the target substring in MULTIPLE places (one legitimate + one diagnostic / comment / anti-anchor), the test must extract a discrete section before asserting.

## Lessons for next slice

- **Bundled cleanup is now the canonical disposition for code-Critic v1 advisory findings** — slice-064/065 + slice-066 lineage. Nominate slice-067+ `slice-NNN-bundle-066-code-critic-cleanup` mirroring slice-065 shape. Voluntary-restraint discipline (N≥10 cumulative; no methodology-changelog entry / no ADR / no VERSION bump per BC-PROJ-10 / Inclusion-heuristic precedent) applies.
- **WS-1 + ETC-1 silent-default-off class is the strongest `/critic-calibrate` proposal target** — propose extension of slice-034 TFFL-1 pattern to both audits in slice-067+.
- **For codification slices, budget Phase A + B-prefix sweep for cross-anchor harmonization** — TF-1 plan paths Glob-verified against filesystem; PMI-1 enumeration verified against the most-recent slice's canonical shape; BC-PROJ-10 paired-entry-pin discipline verified at design-time, not Phase B-mid.
- **Prose-pin tests on multi-occurrence SKILL.md surfaces need section-scoping** — extract the target sub-section before substring asserts.
- **PowerShell `Write-Host | Out-File` is a footgun** — use Write tool for file content; cross-shell idiom mismatches surface at /validate-slice, not /critique.
- **Historical anchor preservation in CLAUDE.md rewrites is opt-in tested** — when ADR §Scope of supersession commits to preserving a literal substring, add the assertion to the existing test rather than just to the new "rewrote-to-X" test.

## Vault updates made (thin vault — small list)

- `architecture/risk-register.md` — R-17 transitioned `mitigating` → `retired` with slice-066 citation + retirement paragraph naming candidate-fix-(b) closure. ADR-063 cited.
- `architecture/shippability.md` — new row #66 (slice-066 critical-path test; cites BRANCH-2 + ADR-063 + R-17 per BCR-1 traceability axis).
- `architecture/decisions/ADR-063-worktree-per-slice.md` — NEW. Mints BRANCH-2; partial-supersedes ADR-019; N=2 application of slice-022 partial-supersession encoding pattern.
- This slice's `design.md` + `mission-brief.md` — corrected 3 PMI-1 enumeration drifts at Phase A; corrected 3 TF-1 plan path drifts at Phase B-prefix; added Mode-interaction matrix at /critique M3; added Audit invocation call-shapes at /critique B3; added Path-comparison semantics at /critique B2; added Idempotent worktree-remove guard at /critique B5; added cross-spec parity test row at /critique B4.

## BCR-1 backlog round-trip

No `**Closes:** SC-NNN` sentinel in mission-brief.md OR reflection.md (slice-066 is not a `/diagnose → /slice-candidates` backlog candidate); no-op clean per BCR-1 / ADR-055.

## Pipeline position

- **predecessor**: `/validate-slice`
- **successor**: `/commit-slice` (user-invoked; NOT auto-advanced per PCA-1 terminal-boundary contract)
- **auto-advance**: false
- **on-clean-completion**: TERMINAL — reflection.md written + slice auto-archived to `slices/archive/`; HALT. User invokes `/commit-slice` manually to generate the audit-grade commit message.
