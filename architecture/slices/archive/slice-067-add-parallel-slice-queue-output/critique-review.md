# Critique Review: Slice 067 add-parallel-slice-queue-output

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-25
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

First Critic's 8 findings (2B/3M/3m) are substantively sound on their merits; B1 + B2 in particular are textbook BC-PROJ-10 / enum-drift catches that the Builder applied cleanly. However, the meta-Critic surfaces **4 missed findings** the first Critic did not catch: (1) AC6 addition violates the /slice skill's hard ≤5-AC rule (SKILL.md L174/L208/L295) without a deviation rationale; (2) mission-brief L96 Pre-finish gate "All 5 acceptance criteria" was not updated when AC6 was added by the B1 fix-block (Builder-fix-introduced internal-drift defect — TPHD-1 sub-mode (a)); (3) design.md L21 retains the "dogfood seed" residual phrase despite M2 ACCEPTED-FIXED claiming the dogfood-seed hedge was dropped (TPHD-1 sub-mode (a) residual-site survival, slice-022 / slice-064 / slice-066 N≥3 cumulative class); (4) ADR-064 L50 5-part PMI-1 leg enumeration drifts vs mission-brief L102 + design.md L159-164 (substitutes `venv ai-sdlc-tools` for the canonical `## v0.69.0 header` 5th leg — slice-066 /build-slice Phase A Builder-self-catch precedent class). One severity adjustment also: M1 OVERRIDE is defensible on cost-benefit but the Builder's rationale citing existing-test-suite backstop misrepresents what `tests/methodology/test_bcr_1_backlog_round_trip.py` actually pins (it pins prose-presence anchors, not runtime no-trigger behavior).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1 (BC-PROJ-10 paired-pin discipline gap)** — confirmed; severity Blocker is appropriate. All 4 sub-claims verified: canonical naming `test_v_0_NN_0_<rule>_entry_present_in_repo` cross-checked against `tests/methodology/test_methodology_changelog.py:4433` + `:4513` matches; Builder-applied fix at mission-brief.md L40-41 + design.md L128 cites both paired tests with correct underscore pattern + suffixes matching slice-066 v0.68.0 BRANCH-2 precedent.
- **B2 (`compute_parallel_safety()` enum drift + zero-active-AND-empty-hint collision)** — confirmed; severity Blocker is appropriate. All 5 sub-fixes verified: AC2 4-value enum at L17, AC4 sub-(d) at L19, precedence rule at design.md L80, TF-1 row `test_empty_hint_files_overrides_zero_active_slices_to_unknown_no_hint_files` at L37.
- **M2 (Mid-slice smoke bootstrap-impossible)** — confirmed; severity Major is appropriate. Mission-brief.md L107-112 + design.md L213-234 (new ImportError guard subsection) applied correctly. (See M-add-3 below — residual site survival is a fix-block-edit-introduced regression, NOT a flaw in M2 itself.)
- **M3 (SKILL.md insertion position unspecified)** — confirmed; severity Major is appropriate. Pin at SKILL.md:378-379 cross-verified against actual SKILL.md L378 ``` close-fence + L379 blank + L380 `## Critical rules` header.
- **m1 (ADR-064 L58 enum drift)** — confirmed; severity Minor is appropriate (auto-closes via B2 fix).
- **m2 (fsync gap on atomic-write)** — confirmed; severity Minor is appropriate. design.md L116 OUT-OF-SCOPE note applied.
- **m3 (R-19 hedge)** — confirmed; severity Minor is appropriate. design.md L194 hedge dropped.

## Suspicious findings

No suspicious findings. Every first-Critic finding the meta-Critic re-verified against design.md / mission-brief.md / ADR-064 stands on its merits; none over-reached.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

### M-add-1: AC6 addition violates the /slice skill's hard ≤5-AC rule without a deviation rationale

- **Claim under review**: Builder added AC6 (v0.69.0 entry-pin meta-AC) at mission-brief.md L21 to satisfy B1 ACCEPTED-FIXED.
- **Issue**: `skills/slice/SKILL.md` mandates ≤5 ACs at THREE pinned locations: L174 (`**Acceptance criteria**: testable, observable, ≤5 items.`), L208 (`- ≤5 acceptance criteria`), L295 (`4. (max 5)` in the mission-brief template). Recent precedent slice-060/063/066 mission-briefs all ship exactly 5 ACs. AC6 addition is an undisclosed deviation.
- **Evidence**: mission-brief.md L21 (new AC6) vs `skills/slice/SKILL.md` L174/L208/L295.
- **Proposed fix options**: (a) 1-sentence rationale note in mission-brief.md after AC6 explaining the deviation; OR (b) structural fix folding AC6 into existing AC; OR (c) new ADR documenting the new-mechanism-mint convention. **Recommended**: option (a) — cheapest + honest + flags for /critic-calibrate if pattern recurs at slice-068+.
- **Severity**: Major (rule deviation without rationale is a discoverability defect).

### M-add-2: Mission-brief.md L96 Pre-finish gate "All 5 acceptance criteria" not updated when AC6 was added (TPHD-1 sub-mode (a) Builder-fix-introduced internal-drift)

- **Claim under review**: Mission-brief.md L96 Pre-finish gate count literal `- [ ] All 5 acceptance criteria PASS with evidence in `validation.md``.
- **Issue**: B1 ACCEPTED-FIXED added AC6 + 2 TF-1 rows but the Pre-finish gate L96 still cites "5". Same defect class as slice-049 N+1 doctrine + slice-064 B1-fix-leaves-3-residual-sites + slice-066 ADR-021-survived-global-rename — Builder fix-block edits ARE an unguarded adversarial surface.
- **Evidence**: mission-brief.md L96 vs L14-22 (AC1-AC6).
- **Proposed fix**: update L96 from `All 5 acceptance criteria` → `All 6 acceptance criteria` (or whatever count survives M-add-1 resolution).
- **Severity**: Major (count drift breaks pre-finish gate enforcement).

### M-add-3: Design.md L21 "dogfood seed" residual phrase survives despite M2 ACCEPTED-FIXED claiming the dogfood-seed hedge was dropped (TPHD-1 sub-mode (a) residual-site survival, N≥4 cumulative)

- **Claim under review**: design.md L21 still reads: `**New runtime artifact** architecture/slice-queue.md — written first at this slice's /build-slice mid-slice smoke (dogfood seed); slice-068+'s /slice invocations regenerate it routinely.`
- **Issue**: M2 Builder draft claimed "Mission-brief L107 rewritten to drop the dogfood-seed branch and explicitly cite bootstrap-discharge" — mission-brief L107-112 was correctly updated, but design.md L21 retains the contradictory "(dogfood seed)" parenthetical (the helper does NOT exist at /slice time, so this slice's mid-slice-smoke IS the first write — that's bootstrap-discharge, not dogfood-seed). Same defect class extended to N=4 (slice-022 RSAD-1 + slice-064 B1-leaves-3-residuals + slice-066 ADR-021-survived + slice-067 M-add-3 here).
- **Evidence**: design.md L21 vs mission-brief.md L112 (post-fix bootstrap-discharge framing).
- **Proposed fix**: update design.md L21 to drop "(dogfood seed)" and replace with "(bootstrap-discharge instance #1 per slice-066 WORKTREE=skip-bootstrap precedent)" matching mission-brief.md L112.
- **Severity**: Major (cross-doc semantic drift between mission-brief and design.md on a load-bearing bootstrap-discharge concept; future readers + the meta-Critic itself flagged the inconsistency).

### M-add-4: ADR-064 L50 5-part PMI-1 leg enumeration drifts vs mission-brief.md L102 + design.md L159-164 (slice-063 / slice-060 / slice-066 N≥3 cumulative cross-doc enumeration drift class; first Critic's claim "5-part PMI-1 leg enumeration consistent" was FALSE-CLEAN)

- **Claim under review**: ADR-064 L50: `VERSION / plugin.yaml / pyproject.toml / installed ~/.claude/ai-sdlc-VERSION / venv ai-sdlc-tools` (5-part PMI-1 atomic bump enumeration).
- **Issue**: The canonical 5 legs per slice-066 /build-slice Phase A Builder-self-catch (verified at slice-066's v0.68.0 entry-pin) are: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## vN.NN.N` header in `methodology-changelog.md` + installed `~/.claude/ai-sdlc-VERSION`. Mission-brief L102 enumerates correctly; design.md L159-164 enumerates correctly. ADR-064 L50 **substitutes the 5th leg**: `venv ai-sdlc-tools` is the TVFS-1 re-install (a separate BC-PROJ-9 consumer-propagation surface per design.md L167 step #6), NOT a PMI-1 part. The first Critic claimed at critique.md L123 "5-part PMI-1 leg enumeration consistent" — false-clean.
- **Evidence**: ADR-064 L50 vs mission-brief.md L102 vs design.md L159-164 vs slice-066 /build-slice Phase A Builder-self-catch class signal.
- **Proposed fix**: update ADR-064 L50 from `VERSION / plugin.yaml / pyproject.toml / installed ~/.claude/ai-sdlc-VERSION / venv ai-sdlc-tools` → `VERSION / plugin.yaml.version / pyproject.toml [project].version / methodology-changelog.md ## v0.69.0 header / installed ~/.claude/ai-sdlc-VERSION`; separately note TVFS-1 re-install of `ai-sdlc-tools` as a BC-PROJ-9 consumer-propagation surface (NOT a PMI-1 part) per slice-066 precedent.
- **Severity**: Major (cross-doc enumeration drift on a load-bearing methodology rule, recurring class slice-063/060/066/067 N=4 cumulative).

## Severity adjustments

### M1 (BCR-1 round-trip non-trigger declaration) — SEVERITY-WRONG-ON-RATIONALE

- **First-Critic finding**: M1 Major — prose-only BCR-1 no-trigger declaration lacks structural verification.
- **Builder OVERRIDE rationale (under review)**: "the BCR-1 audit test runs in the full pytest suite at /validate-slice Step 5 and would catch a regression in BCR-1's no-op-on-no-sentinel behavior structurally."
- **Meta-Critic assessment**: OVERRIDE outcome (no per-slice empirical test) is defensible on cost-benefit grounds at N=15 cumulative codification slices' worth of evidence. BUT the stated rationale **misrepresents what `tests/methodology/test_bcr_1_backlog_round_trip.py` actually pins**. Empirically verified: the file's 8 tests at L115/L143/L190/L221/L247/L296/L331/L366 ALL pin **prose-presence anchors inside scoped SKILL.md sections** (consume-side + round-trip-side prose contracts) — NONE pin the runtime no-trigger-on-absent-sentinel behavior class. A regression where /reflect spuriously triggered BCR-1 on a slice with no `**Closes:** SC-NNN` sentinel would NOT be caught by this test file.
- **Proposed adjustment**: Keep the OVERRIDDEN disposition but correct the rationale to: **"BCR-1's trigger discipline is enforced by /reflect's own runtime logic — a spurious trigger on absent sentinel would fail visibly at /reflect time when it attempted to round-trip a non-existent SC-NNN entry; per-slice empirical pre-pin is cost-benefit-negative at N=15 cumulative."** Flag for /critic-calibrate as a "Builder OVERRIDDEN rationale mis-citing what existing test pins" pattern that may warrant a calibration check across future BCR-1 round-trip-class declarations.

## Notes

Meta-Critic confidence: **HIGH** on the 4 missed findings (3 are structural cross-document drifts verifiable by literal grep against the post-fix artifacts; the AC-count rule violation is a literal cite against `skills/slice/SKILL.md` L174/L208/L295). **MEDIUM-HIGH** on the M1 severity-adjustment — the OVERRIDE outcome is correct but the rationale is structurally inaccurate (verifiable by reading the cited test file's 8 test functions, none of which exercise runtime no-trigger behavior).

**Calibration observation**: The first Critic was thorough and correct on dimensions 1-5 that the Builder explicitly nominated (TPHD-1 cross-file harmonization, BC-PROJ-10 paired-pin, enum-drift, MEPD-1 Inclusion-heuristic, BC-PROJ-9 5-inventory fan-out), but had a **systematic blind spot on Builder-fix-block-introduced regressions** (M-add-2 + M-add-3 are direct consequences of the Builder applying B1 + M2 fixes without sweeping all sibling-cell sites). This is the slice-062 + slice-064 M-add-1 precedent (meta-Critic catches Builder fix-block-edit-introduced regressions) extending to **N=3 cumulative on BRANCH-2 first-governed-slice N+1 (slice-067)**.

**Reservations**: M-add-1 (AC6 violates ≤5-AC rule) may be the kind of methodology-rule deviation that should be formally codified rather than dispositioned per-slice — flag for /critic-calibrate aggregation if this pattern recurs on slice-068+ new-mechanism mints.

## Sources

- `architecture/slices/slice-067-add-parallel-slice-queue-output/mission-brief.md` (L17, L19, L21, L40-41, L96, L102, L107-112)
- `architecture/slices/slice-067-add-parallel-slice-queue-output/design.md` (L16, L21, L80, L116, L128, L159-164, L213-234)
- `architecture/slices/slice-067-add-parallel-slice-queue-output/critique.md` (L34, L57-58, L69, L77-79, L113)
- `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md` (L50, L58)
- `skills/slice/SKILL.md` (L174, L208, L295, L378-380)
- `tests/methodology/test_methodology_changelog.py:4433` + `:4513` (BC-PROJ-10 paired-pin canonical precedent)
- `tests/methodology/test_slice_skill_drift.py:28` (OSDG-1 test function name verified)
- `tests/methodology/test_bcr_1_backlog_round_trip.py:115/143/190/221/247/296/331/366` (8 prose-pin tests; NONE exercise runtime no-trigger behavior — M1 rationale evidence)
- `tools/branch_workflow_audit.py:280-287` (`_resolve_expected_worktree_path` — worktree path literal cross-check)
