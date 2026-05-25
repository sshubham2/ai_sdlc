# Validation: Slice 021 add-feature-branch-workflow-at-build-and-commit-slice

**Date**: 2026-05-14
**Result**: PASS

## Per-criterion results

### AC1: `## Prerequisite check ### Branch state` sub-section + canonical BRANCH=skip shape

- **Status**: PASS
- **Evidence**:
  - `$PY -m pytest tests/methodology/test_build_slice_skill_branch_create.py tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py -v` → **5 passed in 0.04s**
  - All 5 prose-pin tests green: `_prerequisite_check_has_branch_state_sub_section`, `_specifies_slice_branch_name_pattern`, `_specifies_branch_escape_hatch_via_branch_skip_deviation`, `_specifies_runtime_default_branch_resolution`, `_step_7c_canonicalizes_branch_skip_deviation_line_shape`.
  - Real-environment: `git branch --show-current` reports `slice/021-add-feature-branch-workflow-at-build-and-commit-slice` (the slice's own bootstrap successfully exercised the discipline at /build-slice Step 1 plan-mode entry per the canonical `BRANCH=skip-bootstrap` DEVIATION line in build-log.md Events L4).
- **Notes**: AC #1 + AC #2 verified together since both pin SKILL.md prose; tests cover the canonical regex match for the `BRANCH=skip — rationale: <text>` shape via Step 7c body assertions.

### AC2: Step 7c canonical `BRANCH=skip — rationale: <text>` line shape pinned

- **Status**: PASS
- **Evidence**: covered by AC1 test suite (`_step_7c_canonicalizes_branch_skip_deviation_line_shape`). The audit's escape-hatch grep regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+` empirically matches the slice's own bootstrap DEVIATION line (verified by `tests/methodology/test_branch_workflow_audit.py::test_branch_workflow_audit_accepts_escape_hatch_rationale_in_build_log_events`).

### AC3: `/commit-slice --do-commit` → `--merge` swap with 2 pre-flight guardrails

- **Status**: PASS (with DEVIATION-5 limitation flagged for slice-022 redesign)
- **Evidence**:
  - `$PY -m pytest tests/methodology/test_commit_slice_skill_merge_flag.py -v` → **4 passed in 0.03s**
  - All 4 prose-pin tests green: `_documents_merge_flag`, `_removes_do_commit_flag` (zero `--do-commit` occurrences post-sweep), `_specifies_no_ff_merge_and_safe_local_branch_delete`, `_specifies_pre_flight_guardrails`.
- **Notes**: AC3 PASSES on the local-only `--merge` semantics as designed. **DEVIATION-5 (see build-log.md L19)**: the local-only merge semantics is structurally wrong for projects with protected branches / required-PR review / CI gating on origin. Slice-022 candidate `redesign-commit-slice-for-pr-aware-flow` will DROP `--merge` sub-command entirely + replace with `--push` flag that pushes the slice branch to origin (user creates PR + merges manually via UI). Slice-021 ships local-only as a documented v1 limitation per design.md Limitations item 1 (now elevated to explicit "STRUCTURALLY WRONG for non-solo projects" framing). Cause class: **spec gap** (the slice's intent included `--merge` as sub-mode (b); the gap is that v1 didn't consider non-solo projects).

### AC4: `tools/branch_workflow_audit.py` (BRANCH-1) at /build-slice Step 6

- **Status**: PASS
- **Evidence**:
  - `$PY -m pytest tests/methodology/test_branch_workflow_audit.py -v` → **8 passed in 4.05s** (5 violation classes + 3 default-branch-resolution paths)
  - Real-environment positive: `$PY -m tools.branch_workflow_audit architecture/slices/slice-021-...` on current slice/021 branch → `Branch workflow audit: clean. On branch 'slice/021-...' (matches expected 'slice/021-...').` exit 0.
  - Negative-case validation: handled by unit test `test_branch_workflow_audit_refuses_on_default_branch` via synthetic temp git repo on `master` (auto-mode classifier correctly blocked an attempt to `git stash + checkout master` mid-validate; the unit test coverage IS the real-environment validation for the negative case).
- **Notes**: BRANCH-1 audit exercised in 3 modes — automated 8/8 unit tests + real-env positive + escape-hatch acceptance via the slice's own bootstrap line in build-log.md.

### AC5: Vault propagation + 3 stale-doc surfaces + byte-equality + manifests

- **Status**: PASS
- **Evidence**:
  - `grep -l '\--do-commit' pipeline.md tutorial.md "tutorial-site/Hybrid AI SDLC Pipeline.html"` → **zero matches** (all 3 stale-doc surfaces swept).
  - `$PY -m pytest test_methodology_changelog.py::test_v_0_35_0_branch_1_* test_methodology_changelog.py::test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1 test_root_claude_md_branch_per_slice_rule.py test_build_slice_skill_drift.py test_commit_slice_skill_drift.py test_slice_skill_drift.py -v` → **7 passed in 0.11s**
  - PMI-1: `Plugin manifest audit: clean. 24 skill(s), 5 agent(s), 16 tool(s); version 0.35.0.`
  - INST-1: `Install audit: clean. 24/24 skills, 5/5 agents, 4/4 templates, 16/16 tool modules; methodology v0.35.0.`
  - CAD-1: `clean - agents/critique.md byte-equal across in-repo and installed; sha256: f34c967eaaa34413...` (preserved at slice-017 ship hash).
  - WIRE-1: `No wiring matrix violations.`
- **Notes**: PMI-1 + INST-1 + CAD-1 + WIRE-1 + mini-CAD-1 (3 drift tests: slice/build-slice/commit-slice) all clean.

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Rationale**: slice-021 is a methodology / tooling slice (skill prose + audit tool + tests + vault entries). No multi-user / multi-device / multi-account features introduced. The new `tools/branch_workflow_audit.py` exercises real git plumbing at unit-test time via temp repos but isn't a multi-instance feature itself.

## Layered safety checks (VAL-1)

**Layer A (Credential scan)**: clean — 0 secret(s) detected across 22 changed files.
**Layer B (Dependency hallucination check)**: clean — 0 hallucinated imports (after `--imports-allowlist tests` per slice-003+ documented workaround for intra-repo `tests/` namespace-package class). VAL-1 Layer B intra-repo `tests` class **N=18 → N=19 cumulative recurrence** at slice-021 (handled cleanly via the documented allowlist; class is stable; no remediation required).

Command: `$PY -m tools.validate_slice_layers --slice architecture/slices/slice-021-... --imports-allowlist tests --changed-files <22 files>` → `0 secret(s), 0 import finding(s), 0 suppressed (allowlisted). Clean — both layers passed.`

## Shippability catalog (regression check)

**Result**: PASS — **481/481 tests in full project suite green in 7.66s**.

Command: `$PY -m pytest tests/ -q --tb=no` → `481 passed in 7.66s`.

This is broader than just the shippability catalog rows 1-21 — it runs every test in the project, which is the strictest superset of the catalog. No regression introduced by slice-021. The 14-invocation-target row 21 Command cell is included in this run (verified separately at /build-slice Phase 5 pre-finish gate: 27/27 PASS in 4.38s).

## Reality surprises

1. **DEVIATION-5 elevated to slice-022 candidate**: the user surfaced (post-build, mid-/validate) that `/commit-slice --merge` local-only semantics is structurally wrong for any project with protected branches / required-PR review / CI gating. All 4 Critic-stack passes missed this — the Critic dimensions (Security / Contract gaps / Cross-cutting conformance) evaluated `--merge` AS LOCAL-ONLY without questioning whether local-only was the right scope. Slice-022 candidate `redesign-commit-slice-for-pr-aware-flow` queued: DROP `--merge` entirely + replace with `--push` flag (push slice branch to origin; user creates PR + merges manually via UI). **NEW class candidate for /critic-calibrate slice-022: `opinionated-merge-default-vs-team-workflow`** — promote at N≥3 recurrence (currently N=1 at slice-021).

2. **Auto-mode classifier as fifth-Critic-stack-layer** (extends slice-018 DEVIATION-1 + DEVIATION-2 auto-mode pattern): at /validate-slice Step 1 AC #4 negative-case attempt, the classifier blocked `git stash + checkout master` mid-slice (correctly — the user hadn't authorized switching off slice/021). This forced fallback to unit-test coverage for the negative case (which is the correct discipline anyway). Class N=2 → **N=3 cumulative** auto-mode-as-Critic-stack-layer recurrence (slice-018 DEVIATION-1/2 + slice-021 here).

3. **VAL-1 Layer B intra-repo `tests` class N=19 cumulative**: continued recurrence across all slices 003-021. Documented workaround (`--imports-allowlist tests`) is stable; the class is a known false positive that just needs the flag at every /validate-slice. Could be promoted to default-on behavior in tools/validate_slice_layers.py, but that's outside slice-021 scope.

4. **Path-bug: `methodology-changelog.md` location**: design.md repeatedly referenced `architecture/methodology-changelog.md`, but the file lives at repo root `methodology-changelog.md` (matches slice-020 + earlier convention). Test path (`tests/methodology/test_methodology_changelog.py` uses `read_file("methodology-changelog.md")`) already had the right path. Cleanup at /reflect — design.md prose should be corrected.

## Per-AC summary

| AC | Status | Cause if not PASS |
|----|--------|---|
| AC1 (Prerequisite check Branch state) | PASS | — |
| AC2 (Step 7c canonical shape) | PASS | — |
| AC3 (--merge swap + guardrails) | PASS (with DEVIATION-5) | spec gap on non-solo scope; slice-022 redesigns |
| AC4 (BRANCH-1 audit) | PASS | — |
| AC5 (vault + manifests + stale-docs) | PASS | — |

**5 of 5 ACs PASS**; 1 AC carries a documented spec-gap DEVIATION (D-5) flagged for slice-022 redesign. Per `/validate-slice` skill: spec gaps don't fix-during-validate; let `/reflect` formalize. Proceeding to `/reflect`.
