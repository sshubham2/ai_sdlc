# Critique Review: Slice 060 add-code-review-skill

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-23
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 5 Blockers + 5 Majors + 4 Minors are all VALID with correct severities — every cited claim verified against live disk state (post-fix-prose). The Builder's ACCEPTED-FIXED edits discharge the cited concerns. However, a second-pass re-application of the 8 review dimensions against the POST-fix-prose state surfaces TWO missed Majors and one Minor — all in the new appended `## Build-phase sequence` and TF-1 plan sections (Builder's own /critique fix-prose, the slice-049 / slice-042 "design correction is itself an unguarded adversarial surface" class, N≥4).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1**: Alphabetical insertion points — confirmed; `code-review` < `commit-slice` (`d` < `m` after `co` tie) AND `code-review` < `critic-calibrate` (`o` < `r`). The live `_CANONICAL_SKILLS` is in fact non-strictly-alphabetical (`pulse` is misplaced at position 19), but the insertion-target ASCII comparison for `code-review` is correct as drafted. Severity Blocker appropriate.
- **B2**: PVFS-1 5-part bump — confirmed; `pyproject.toml:20` verified at `version = "0.63.0"`; slice-059 5-part precedent verified. Severity Blocker appropriate.
- **B3**: `tests/agents/` + `tests/skills/code_review/` phantom paths — confirmed via `ls -la` (neither directory exists); `tests/methodology/__init__.py` + `tests/skills/__init__.py` + `tests/skills/diagnose/__init__.py` precedent verified. Severity Blocker appropriate (PTFCD-1 class).
- **B4**: 4-vs-5 tool-count drift — confirmed; mission-brief AC #2 (post-fix) lists 5 tools; design.md L142 lists 5 tools verbatim with `agents/critique.md:4` parity. The `test_agent_md_read_only_tools_pinned` positive+negative substring pattern (slice-007 M2 / slice-053 M-add-4) correctly applied. Severity Blocker appropriate.
- **B5**: 6 hardcoded "8" sites — confirmed via grep on live disk; ALL 6 sites exist exactly as enumerated: `tools/pipeline_chain_audit.py:56` ("all 8 blocks well-formed"), `:225` ("8 covered skills"), `:309` ("8-skill pipeline-chain auto-advance"), `tools/install_audit.py:84` ("verify the 8-skill"), `tests/methodology/test_pipeline_chain_audit.py:4` + `:66`, `tests/methodology/test_pipeline_position_block_drift.py:3` + `:58`. SCPD-1 sub-mode (b) propagation onto shippability row #27 verified. Severity Blocker appropriate.
- **M1**: 9-dimensions-vs-CODE reframe table — confirmed; design.md L277-293 carries the reframe table per /critique M1; content-bearing test spec at L293 cites the specific substrings to assert (slice-037 M-add-1 tautologically-green discipline preserved).
- **M2**: Build-phase sequence — confirmed; design.md L295-307 enumerates A→B→C→D→E with explicit ordering rationale; TF-1 row 3 reclassified `integration → unit` (artifact-existence-and-content check).
- **M3**: Empty-diff in-scope path enumeration — confirmed; design.md L116-122 enumerates 5 in-scope categories.
- **M4**: v0.64.0 entry-pin substring assertions — confirmed; design.md L15 enumerates 8 substring assertions; name shape `test_v_0_64_0_crsi_1_entry_present_in_repo` matches slice-059 precedent verbatim.
- **M5**: Shippability row #60 design — confirmed; design.md L309-330 enumerates 5 Command-cell selectors + tripwire description + runtime budget + pipe-escape discipline (BC-PROJ-7).
- **m1, m2, m3, m4** — all VALID; ACCEPTED-FIXED edits verified in design.md / ADR-059 at cited locations.

## Suspicious findings

No suspicious findings. Every finding the first Critic raised survives independent recomputation against live disk state.

## Missed findings

Concerns surfaced from independent re-review of the POST-fix-prose state (Builder's own /critique fix-prose is the unguarded adversarial surface per slice-049 / slice-042 N≥4 lineage):

### M-add-1: Phase B forward-sync omits the edited `skills/build-slice/SKILL.md` and `skills/validate-slice/SKILL.md`

- **Claim under review**: design.md "## Build-phase sequence" Phase B enumerates `cp` operations for `skills/code-review/SKILL.md`, `agents/code-review.md`, `methodology-changelog.md`, `VERSION`, plus `pip install --upgrade .` for TVFS-1.
- **Issue**: Phase B does NOT enumerate `cp skills/build-slice/SKILL.md ~/.claude/skills/build-slice/SKILL.md` or `cp skills/validate-slice/SKILL.md ~/.claude/skills/validate-slice/SKILL.md`. But both files ARE edited at design.md "Components touched / skills/build-slice/SKILL.md (MODIFY)" + "skills/validate-slice/SKILL.md (MODIFY)" — build-slice's `successor:` flips to `/code-review`; validate-slice's `predecessor:` flips to `/code-review`. Both have full-file drift guards:
  - `tests/methodology/test_build_slice_skill_drift.py:24-30` asserts full-file content-equality in-repo↔installed (verified live; comparator is `assert_md_forward_synced`).
  - `tests/methodology/test_pipeline_position_block_drift.py:34-69` is parametrized over `_CANONICAL_CHAIN` (which now grows from 8 to 9 entries — including `code-review` AND continuing to include `build-slice` + `validate-slice`) AND asserts `in_repo_sec == installed_sec` on the `## Pipeline position` section.
- Without forward-syncing the edited build-slice + validate-slice SKILL.md files, both tests FAIL at Phase D / Phase E. Per **Fowler — refactoring discipline** ("when you edit a canonical surface that has replicas, propagate to all replicas in lock-step") and the slice-049 / slice-051 OSDG-1 family-add lineage. Same defect class as B2 (Builder enumerated a partial fan-out) — caught at Builder's OWN fix-prose, classic slice-042 "design correction is itself an unguarded adversarial surface" surface, N=4+ recurrence.
- **Severity**: **Major** — pre-finish gate failure, recoverable mid-build (one-line addition to Phase B's cp list) but if undetected the slice ships with broken byte-equality on the in-loop chain skills — the exact "stale installed pipeline directive" class the slice-026 M-add-1 watch-list and slice-027 PCA-1 drift-guard added.
- **Proposed fix**: Extend design.md Phase B to enumerate `cp skills/build-slice/SKILL.md ~/.claude/skills/build-slice/SKILL.md` AND `cp skills/validate-slice/SKILL.md ~/.claude/skills/validate-slice/SKILL.md` (and any other in-loop skill SKILL.md the slice edits — none other on inspection).

### M-add-2: TF-1 plan omits the paired `test_v_0_64_0_crsi_1_shippability_consumer_propagation` test (BC-PROJ-10 violation)

- **Claim under review**: design.md "What's new" L15-16 enumerates two new tests under `tests/methodology/test_methodology_changelog.py`: `test_v_0_64_0_crsi_1_entry_present_in_repo` AND `tests/methodology/test_shippability_runner_segment_contract.py::test_code_review_dogfood_row_runs_clean`.
- **Issue**: Every prior version-bump slice ships a paired `_entry_present_in_repo` + `_shippability_consumer_propagation` test set under `test_methodology_changelog.py`. Verified live: **17 `_shippability_consumer_propagation` test functions** + **43 `_entry_present_in_repo` test functions** in `tests/methodology/test_methodology_changelog.py`. Examples (per grep): `test_v_0_40_0_crp_1_*`, `test_v_0_41_0_pca_1_*`, `test_v_0_50_0_*`, `test_v_0_51_0_*`, `test_v_0_52_0_*`, `test_v_0_53_0_*`, `test_v_0_54_0_*`, `test_v_0_58_0_*`, `test_v_0_59_0_*`, `test_v_0_60_0_*`, `test_v_0_62_0_*`, `test_v_0_63_0_*` — N≥12 instances stable. **BC-PROJ-10** (architecture/build-checks.md:173) literally cites: *"the conventional `test_v_0_NN_0_*_entry_present_in_repo` + `*_shippability_consumer_propagation` test pair"* — verbatim verified. Slice-060 introduces row #60 referencing CRSI-1 + `tools.shippability_runner` consumer; without the propagation test the SCPD-1 axis for row #60 is unpinned — silent regression if row #60 is renamed or loses its `CRSI-1` literal or its `code_review_*` references. Per **Newman — `Building Microservices`** (consumer-driven contracts) + BCR-1 / SCPD-1 lineage.
- **Severity**: **Major** — TF-1 plan undercounts by one row; BC-PROJ-10 build-check trigger fires; if not added, slice ships missing the conventional companion pin and breaks the N≥12 pair-precedent. BC-PROJ-10 is a CRITICAL severity (build-check rule, "MUST"), making the omission a blocker-class concern for the bump path; meta-Critic classifies Major because the fix is trivial (one TF-1 row + one test function definition) and the SCPD-1 axis can recover quickly.
- **Proposed fix**: Add a TF-1 row for `tests/methodology/test_methodology_changelog.py::test_v_0_64_0_crsi_1_shippability_consumer_propagation` asserting (a) `architecture/shippability.md` contains the literal `CRSI-1`, (b) the catalog contains the `tools.shippability_runner` or pytest-based consumer reference for the new row, (c) the catalog references the `code_review_skill_drift` / `code_review_agent_drift` test modules. Add to design.md "What's new" as a paired test. Add the test to the shippability row #60 Command-cell selector list (M5 sub-section) as the 6th selector.

### m-add-1: Dim 9 reframe table elides code-side PTFCD-class concerns

- **Claim under review**: design.md "## 9 dimensions reframed for code" Dim 9 declares **PTFCD-1, PTFFD-1, MEPD-1** out-of-scope for `/code-review`, rationale: "all properties of mission-brief / design / catalog row prose, not code".
- **Issue**: The rationale is correct for the SUB-mode (a) phantom-test-path-in-DESIGN.md class — that genuinely is design-time and reviewed by `/critique`. But there's a code-side analog the reframe table does not name: a NEW `tests/<...>.py` module that the slice writes which CITES a path/function that doesn't exist (phantom-import inside test code), or a `tools/<...>.py` module that imports a name that no longer exists. That IS code-as-artifact (a `.py` file the slice authored). The reframe table currently signals to the `/code-review` agent at runtime "skip all PTFCD-class concerns" — risking the agent failing to flag a phantom-import in actual `.py` code under review. Per **Sommerville — `Software Engineering`, Ch. 24 (software inspection coverage)** "the inspection coverage matrix must explicitly say which sub-modes apply to each artifact class".
- **Severity**: **Minor** — the agent will likely still catch a phantom-import via Dim 5 (Contract gaps) or Dim 1 (Unfounded assumptions); the dimension elision is a clarity gap, not a coverage hole.
- **Proposed fix**: Amend design.md Dim 9 reframe entry to split: "PTFCD-1 sub-mode (a) [phantom-test-path-in-design] out-of-scope; phantom-import-in-`.py`-code IS in-scope under Dim 1 / Dim 5". One-sentence clarification, no test impact.

## Severity adjustments

No severity adjustments. All first-Critic severities (5 Blockers / 5 Majors / 4 Minors) match the defect classes verified against live disk state and prior-slice precedent.

## Notes

Confidence in this meta-review: **high on M-add-1** (the missed forward-sync of edited build-slice + validate-slice SKILL.md files is a concrete, verifiable, recurring-class defect — same as slice-059's 4-vs-5-part PMI-1 bump, slice-050's INSTALL.md leg, slice-052's bump-classification miss; the first Critic flagged B2 (PVFS-1 leg) and B5 (6 sites) but did not extend the same fan-out check to the edited canonical-replica SKILL.md files). **High on M-add-2** (the missed `_shippability_consumer_propagation` pair is N≥17 instances stable across the changelog test module, BC-PROJ-10-literal verbatim cited in build-checks.md:173, and easily grep-verifiable). **Moderate on m-add-1** (interpretability/clarity gap in Dim 9 reframe prose that the agent itself may navigate around at runtime).

Calibration observation: the first Critic's pattern on this slice fits the slice-037/053/059 build-time-unreachable / fan-out-undercount blind-spot class — the Critic recomputed all 6 chain-length "8" sites for B5 but did not transfer the same fan-out discipline to the SKILL.md forward-sync surface (Phase B) NOR the changelog test-pair precedent (TF-1 row #14). Both misses are surfaces the first Critic CAN reach (no runtime dependency); both surfaces emerged in Builder's own /critique fix-prose (the new appended "## Build-phase sequence" section + the TF-1 plan table edits). This is the slice-049 / slice-032 / slice-042 "the design correction is itself an unguarded adversarial surface" class, N=4+ counting this slice — a candidate for `/critic-calibrate` once enough single-slice misses accumulate.

Files inspected:
- <HOME>\ai_sdlc\architecture\slices\slice-060-add-code-review-skill\mission-brief.md
- <HOME>\ai_sdlc\architecture\slices\slice-060-add-code-review-skill\design.md
- <HOME>\ai_sdlc\architecture\decisions\ADR-059-add-code-review-skill.md
- <HOME>\ai_sdlc\tools\install_audit.py
- <HOME>\ai_sdlc\tools\pipeline_chain_audit.py
- <HOME>\ai_sdlc\tools\critique_agent_drift_audit.py
- <HOME>\ai_sdlc\tools\shippability_decoupling_audit.py
- <HOME>\ai_sdlc\pyproject.toml (L20)
- <HOME>\ai_sdlc\VERSION
- <HOME>\ai_sdlc\plugin.yaml
- <HOME>\ai_sdlc\methodology-changelog.md
- <HOME>\ai_sdlc\skills\build-slice\SKILL.md
- <HOME>\ai_sdlc\skills\validate-slice\SKILL.md
- <HOME>\ai_sdlc\architecture\build-checks.md (L173 BC-PROJ-10 literal)
- <HOME>\ai_sdlc\architecture\shippability.md (row #27)
- <HOME>\ai_sdlc\tests\methodology\test_pipeline_chain_audit.py
- <HOME>\ai_sdlc\tests\methodology\test_pipeline_position_block_drift.py
- <HOME>\ai_sdlc\tests\methodology\test_build_slice_skill_drift.py
- <HOME>\ai_sdlc\tests\methodology\test_validate_slice_skill.py
- <HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py (lines 120-3914; 43 `_entry_present_in_repo` + 17 `_shippability_consumer_propagation` test functions counted live)

## Builder drafts (for the 3 new missed findings — to be ratified at /critique Step 4.5 TRI-1)

- **M-add-1**: **ACCEPTED-FIXED** at design.md "## Build-phase sequence" Phase B — added `cp skills/build-slice/SKILL.md ~/.claude/skills/build-slice/SKILL.md` AND `cp skills/validate-slice/SKILL.md ~/.claude/skills/validate-slice/SKILL.md` to the forward-sync list. Verified live: both installed copies exist (`-rw-r--r-- ... ~/.claude/skills/build-slice/SKILL.md`, `~/.claude/skills/validate-slice/SKILL.md`); both have full-file drift guards.
- **M-add-2**: **ACCEPTED-FIXED** at mission-brief.md TF-1 plan (new row 19) + design.md "What's new" (paired test) + design.md "## Shippability catalog row #60 design" (add as 6th Command-cell selector) + BC-PROJ-10 explicit citation in design.md "What's reused". N≥17 propagation-test instances + BC-PROJ-10:173 verbatim verified.
- **m-add-1**: **ACCEPTED-FIXED** at design.md Dim 9 reframe — single-sentence amendment splitting PTFCD-1 sub-mode (a) (design-time, out-of-scope for `/code-review`) from phantom-import-in-`.py`-code (in-scope under Dim 1 / Dim 5).

Per TPHD-1 sub-mode (b), the M-add-2 TF-1 plan row addition is harmonized in this /critique-review fix block alongside the design.md edits.
