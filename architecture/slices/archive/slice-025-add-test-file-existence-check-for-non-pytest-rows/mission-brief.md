# Slice 025: add-test-file-existence-check-for-non-pytest-rows

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: developer-process calibration — the *phantom-test-file-citation* (PTFCD) class. N=2 distinct cross-slice (slice-023 B4 `test_row_*.py` doesn't exist, caught at /critique; slice-024 `test_shippability_catalog.py` doesn't exist, caught only at /validate-slice Step 5.5). Not a `risk-register.md` entry — slice-024 reflection explicitly classifies it as developer-process calibration, not a project risk.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The Critic stack reviews TF-1 plan rows and shippability `Command`-cell paths for name-harmonization, status, and cross-file consistency, but **no surface verifies the cited test file actually exists on disk**. This blind spot survived 19 Critic-stack findings + 2 Critic layers at slice-024 and only died at real-command execution. This slice codifies a test-file-existence check at two audit surfaces plus a Critic Dim 9 sub-clause, so the phantom-test-file-citation class is caught at `/build-slice` Step 6 (and at the Critic layer) instead of leaking to `/validate-slice` or shipping. Now, because slice-023 lesson 5 explicitly foreshadowed this and named the recurrence site, the project's own "promote at N=2 when foreshadowed" convention (aggregated-lessons) is met.

## Acceptance criteria

1. `tools/test_first_audit.py` emits a violation at `--strict-pre-finish` when any TF-1 plan row cites a `Test path` whose file does not exist on disk, covering pytest AND non-pytest (`grep-verification` / `catalog-verification` / `git-diff-verification`) rows. Non-strict (mid-slice) runs do NOT flag — PENDING test-first rows legitimately reference not-yet-created files.
2. A check verifies every `architecture/shippability.md` `Command`-cell that references a test-file path points to an existing file (catching the `test_shippability_catalog.py` / `test_row_*.py` phantom class), with markdown-backtick stripping applied before path resolution (folds in the slice-024 validation.md footgun).
3. The PTFCD class is codified as a new `agents/critique.md` Dim 9 sub-clause instructing the Critic to verify cited test-file existence — closing the structural blind spot at the Critic prompt layer. CAD-1 byte-equality (in-repo ↔ installed `~/.claude/agents/critique.md`) preserved.
4. `methodology-changelog.md` v0.39.0 entry (rule ID `PTFCD-1`) + new ADR (reversibility: cheap) authored; atomic version triple (`VERSION` == ai-sdlc-VERSION == `plugin.yaml`) bumped to 0.39.0; PMI-1 / INST-1 / DR-1 audits clean.
5. Recursive-self-application closure: this slice's own TF-1 plan rows AND any shippability rows it appends pass the new existence check at strict-pre-finish.

## Test-first plan

Each AC maps to failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_test_first_audit.py | test_strict_pre_finish_flags_missing_test_path_file | PASSING |
| 1 | unit | tests/methodology/test_test_first_audit.py | test_non_strict_does_not_flag_pending_missing_file | PASSING |
| 1 | unit | tests/methodology/test_test_first_audit.py | test_existence_check_covers_non_pytest_rows | PASSING |
| 1 | unit | tests/methodology/test_test_first_audit.py | test_pending_row_missing_file_emits_exactly_one_violation | PASSING |
| 2 | unit | tests/methodology/test_shippability_path_existence.py | test_flags_phantom_command_cell_test_path | PASSING |
| 2 | unit | tests/methodology/test_shippability_path_existence.py | test_strips_backticks_before_path_resolution | PASSING |
| 2 | unit | tests/methodology/test_shippability_path_existence.py | test_interpreter_and_dash_m_dash_q_tokens_not_flagged | PASSING |
| 3 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_phantom_test_file_citation_sub_clause_present | PASSING |
| 3 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_phantom_test_file_citation_location_pinned | PASSING |
| 3 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_phantom_test_file_citation_names_both_sub_modes | PASSING |
| 3 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_phantom_test_file_citation_paragraph_cites_slice_023_024 | PASSING |
| 3 | structural-invariant | tests/methodology/test_critique_agent.py | test_critique_dim_9_lists_eleven_sub_clauses (supersedes _lists_ten; PMI-1 structural-invariant + SCPD-1 consumer-propagation to shippability rows referencing _lists_ten) | PASSING |
| 3 | grep-verification | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal (existing — CAD-1 byte-equality, content-agnostic; auto-covers the new sub-clause, no new fn) | PASSING |
| 4 | grep-verification | tests/methodology/test_methodology_changelog.py | test_v_0_39_0_ptfcd_1_entry_present_in_repo_and_installed | PASSING |
| 4 | grep-verification | tests/methodology/test_methodology_changelog.py | test_adr_023_present_and_reversibility_cheap | PASSING |
| 5 | catalog-verification | architecture/shippability.md | new PTFCD-1 row Command self-applies cleanly | PASSING |

(Exact test-file names/paths confirmed at `/design-slice`; per TPHD-1 sub-mode (c) any /critique-disposition-promised test must be enumerated here before `/build-slice`.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | strict-pre-finish flags missing `Test path` file | `$PY -m tools.test_first_audit <brief-with-phantom-row> --strict-pre-finish` exits non-zero with a PTFCD violation naming the missing path; non-strict run exits 0 on same input |
| 2 | shippability Command-cell path existence + backtick-strip | run the new check against a synthetic catalog row citing `test_row_999.py` (absent) → flagged; against a backtick-wrapped real path → resolves and passes |
| 3 | Critic Dim 9 PTFCD sub-clause + CAD-1 | prose-pin test PASSES on live `agents/critique.md`; `$PY -m tools.critique_agent_drift_audit --repo-root .` reports byte-equal |
| 4 | changelog v0.39.0 + ADR + version triple | `$PY -m tools.plugin_manifest_audit` clean; changelog/ADR tests PASS; `VERSION`==`plugin.yaml`.version==ai-sdlc-VERSION==0.39.0 |
| 5 | self-application closure | this slice's TF-1 plan + appended shippability rows pass `tools/test_first_audit.py --strict-pre-finish` and the new shippability check |

## Must-not-defer

- [ ] False-positive avoidance: non-strict / PENDING test-first rows MUST NOT be flagged (only `--strict-pre-finish`).
- [ ] Markdown-backtick stripping before path resolution (slice-024 footgun — produced 23 spurious FAILs without it).
- [ ] CAD-1 byte-equality on `agents/critique.md` (in-repo == installed) after the Dim 9 edit.
- [ ] PMI-1 / INST-1 / DR-1 / BC-1 audits clean before pre-finish.
- [ ] RPCD-1 / SCPD-1: new audit rule propagates its consumer reference into `architecture/shippability.md`.

## Out of scope

- ADR-pin-by-test-name existence verification beyond file-level (function-name resolution inside an existing file is a separate refinement — file existence is the N=2 witnessed class; function-level is N=0).
- Refactoring `test_first_audit.py` table-parsing beyond what the existence check needs (no "while I'm here" cleanup — slice-018 precedent).
- Running `/critic-calibrate` (the alternative disposition named in slice-024 discovery) — this slice takes the audit-refinement fork, not the calibration fork.
- R-1 / R-2 / R-3 `/diagnose` work (different slices).

## Dependencies

- Prior slices: [[slice-024-refine-dim-9-with-fix-block-completeness-sub-clause]] — supplies the N=2 witness + foreshadowed promotion target; [[slice-023-audit-tools-default-utf8-stdout]] — supplies N=1 (B4) and the backtick-strip footgun.
- Failing repro test: N/A — codification slice, not a code-defect bug fix (BFRD-1 Step 3c does not fire; tests-first satisfied via TF-1 plan per project precedent slices 013–024).
- Vault refs: [[tools/test_first_audit.py]], [[agents/critique.md]] (Dim 9), [[architecture/shippability.md]], [[methodology-changelog.md]] (v0.39.0).
- Methodology: FBCD-1 / RPCD-1 Dim 9 sub-clause precedent; TPHD-1 sub-mode (c) prerequisite-check coupling.

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m tools.test_first_audit <fixture brief with one phantom non-pytest Test path> --strict-pre-finish
```
Expected: non-zero exit + a PTFCD violation naming the missing file; same fixture under a non-strict run exits 0. If strict fails to flag OR non-strict false-positives: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] CAD-1 / PMI-1 / INST-1 / DR-1 / BC-1 / TF-1 (strict-pre-finish) all clean
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
