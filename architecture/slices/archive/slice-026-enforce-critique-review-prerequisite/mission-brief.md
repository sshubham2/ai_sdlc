# Slice 026: enforce-critique-review-prerequisite

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: Closes the "mandatory-but-structurally-unenforced `/critique-review`" gap named verbatim as the "Strongest slice-026 candidate" in slice-025 reflection (`_index.md` Aggregated lessons L37). DR-1 / slice-010 / CLAUDE.md make `/critique-review` mandatory in Standard mode for mandatory-Critic slices, but nothing structurally detects a skip of it — slice-025 skipped it and was caught only by a coincidental hand-authored AC.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`/critique-review` (DR-1) is mandatory in Standard mode for any slice with mandatory-Critic triggers (CLAUDE.md "Builder ↔ Critic separation"; slice-010 default heuristic), but enforcement is prose-only and manual — `methodology-changelog.md` v0.17.0 records DR-1 as "Manual invocation only". `tools/critique_review_audit.py` is invoked from exactly one place (`skills/critique-review/SKILL.md`), so it only runs *inside* `/critique-review` and provides **no skip-detection** — there is no `/validate-slice`-side net. slice-025 skipped `/critique-review` and the skip was caught **only** because AC4 coincidentally hand-authored a "DR-1 clean" assertion whose own verification failed at `/validate-slice`; absent that AC the skip ships unnoticed. This slice codifies the **first structural skip-detector**: a prerequisite-check at `/build-slice` (rule-ID **CRP-1** — audit-enforced-gate naming class, NON-`-D`, per ADR-019, alongside BRANCH-1 / BC-1 / PMI-1) that refuses to start the build when a mandatory `/critique-review` is absent and unrationalised — mirroring the BRANCH-1 / TPHD-1 sub-mode (c) `## Prerequisite check` placement precedent. A documented escape-hatch (canonical `critique-review-skip` frontmatter key in `milestone.md`, same `rationale:` spirit as BRANCH-1's `BRANCH=skip`) preserves the deliberate-skip path.

## Acceptance criteria

1. `skills/build-slice/SKILL.md` `## Prerequisite check` refuses to proceed — with a verbatim STOP message routing the user to run `/critique-review` — when ALL hold: mode ∈ {Standard, Heavy} AND `milestone.md` `critic-required: true` AND `critique-review.md` is absent AND no canonical CRP-1 skip frontmatter key present. The CRP-1 check runs AFTER the existing L22 `critique.md`-exists gate (no critique-review without a critique).
2. A canonical documented skip escape-hatch — the `critique-review-skip` frontmatter key in `milestone.md` whose value matches `^skip — rationale: .+` (same `rationale:` spirit as BRANCH-1 `BRANCH=skip — rationale: <text>`) — is recognised by the enforcing audit; when present, `/build-slice` proceeds and the skip is auditable. A malformed `critique-review-skip` value (key present, off-canonical value) is an Important violation (mirrors BRANCH-1 malformed handling).
3. The discipline is codified in `methodology-changelog.md` as a new versioned entry (v0.40.0, rule-ID **CRP-1**) carrying rule-reference, defect-class, validation, and limitations sections consistent with the **audit-enforced-gate** entry shape (e.g. BRANCH-1 v0.35.0 / UTF8-STDOUT-1 v0.37.0), explicitly NON-`-D` per ADR-019; `VERSION` + `plugin.yaml.version` bump in lockstep (PMI-1).
4. `architecture/shippability.md` gains a CRP-1 row and the enforcing audit's consumer references propagate into the catalog, per RPCD-1 / SCPD-1 consumer-propagation discipline.
5. The CRP-1 prerequisite-check prose and enforcement behaviour are pinned by tests (refuse-on-absent-mandatory, accept-on-present, accept-on-documented-skip, malformed-skip) plus the existing mini-CAD byte-equality drift gate on `skills/build-slice/SKILL.md`. Recursive self-application (slice-026 is CRP-1 **bootstrap-reference instance #1**, mirroring slice-021/BRANCH-1): the prerequisite sub-block cannot self-gate this very build (it does not exist in `skills/build-slice/SKILL.md` until this build authors it); self-application is satisfied by (a) `/critique-review` run manually on slice-026 and (b) `python -m tools.critique_review_prerequisite_audit` run against slice-026's own folder once `critique-review.md` exists.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Paths/function names below are provisional at `/slice` time; `/design-slice` + `/critique` finalise them and `/build-slice` Prerequisite-check TPHD-1 sub-mode (c) harmonises this table before plan-mode entry. Existing files confirmed present: `tests/methodology/test_build_slice_skill.py`, `tests/methodology/test_build_slice_skill_drift.py`, `tests/methodology/test_critique_review_audit.py`, `tests/methodology/test_methodology_changelog.py`. New file created by this slice: `tests/methodology/test_critique_review_prerequisite_audit.py`.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | prose-pin | tests/methodology/test_build_slice_skill.py | test_build_slice_prereq_crp_1_refuses_on_absent_mandatory_critique_review | PASSING |
| 1 | unit | tests/methodology/test_critique_review_prerequisite_audit.py | test_refuses_when_standard_mandatory_and_absent | PASSING |
| 2 | unit | tests/methodology/test_critique_review_prerequisite_audit.py | test_accepts_documented_skip_frontmatter_canonical_shape | PASSING |
| 2 | unit | tests/methodology/test_critique_review_prerequisite_audit.py | test_accepts_when_critique_review_md_present | PASSING |
| 2 | unit | tests/methodology/test_critique_review_prerequisite_audit.py | test_malformed_skip_value_is_important_violation | PASSING |
| 3 | prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_40_0_crp_1_entry_present_in_repo_and_installed | PASSING |
| 4 | prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_40_0_crp_1_shippability_consumer_propagation | PASSING |
| 5 | drift | tests/methodology/test_build_slice_skill_drift.py | test_build_slice_skill_md_in_repo_byte_equal_installed | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Refuse on absent mandatory | Run the enforcing audit against a synthetic slice fixture (Standard + critic-required:true + no critique-review.md + no skip key) → exit 1 + STOP message naming which condition held; prose-pin test asserts the verbatim routing message in `skills/build-slice/SKILL.md`. |
| 2 | Documented-skip escape-hatch | Audit vs fixture with canonical `critique-review-skip` frontmatter value → exit 0; vs fixture with `critique-review.md` present → exit 0; vs fixture with malformed `critique-review-skip` value → exit 1 (Important). |
| 3 | Methodology entry | `& $PY -m pytest tests/methodology/test_methodology_changelog.py -k crp_1` green; `& $PY -m tools.plugin_manifest_audit` clean; `VERSION`==`plugin.yaml.version`==0.40.0. |
| 4 | Shippability propagation | Grep `architecture/shippability.md` for the CRP-1 row + the enforcing audit module reference; `& $PY -m tools.shippability_path_audit` clean. |
| 5 | Self-application + drift | `/critique` + `/critique-review` both ran on slice-026 (artifacts present); `& $PY -m tools.critique_review_prerequisite_audit architecture/slices/slice-026-enforce-critique-review-prerequisite` exits 0 against slice-026's own folder once `critique-review.md` exists; `& $PY -m tools.critique_agent_drift_audit --repo-root .` clean; mini-CAD byte-equality drift test green. |

## Must-not-defer

- [ ] Escape-hatch parity: the CRP-1 documented-skip key MUST be a single canonical shape the audit accepts (no ambiguous free-text), same `rationale:` spirit as BRANCH-1's Step-7c-pinned `BRANCH=skip` — under-specifying it re-opens the silent-skip hole.
- [ ] Escape-hatch survives Step 7b: the skip key MUST live in a `milestone.md` location `/build-slice` Step 7b's continuous milestone.md rewrite preserves (frontmatter key, not free-form body line) so the Step 6 defense-in-depth re-run does not false-refuse a legitimately escape-hatched build.
- [ ] Mode/trigger detection correctness: the refuse condition MUST read mode from the vault (triage.md frontmatter `mode:` → fallback CLAUDE.md `**Mode**:`) and `critic-required` from `milestone.md` frontmatter — not infer from heuristics; a false-negative here is the exact slice-025 failure recurring.
- [ ] Recursive self-application (bootstrap-aware): `/critique-review` MUST run on slice-026 itself AND the audit MUST be run against slice-026's own folder (RSAD-1); the prerequisite sub-block itself cannot self-gate this bootstrap build (documented in design.md + ADR-024).
- [ ] No false-refuse on legitimately-exempt slices: low-tier slices with `critic-required:false` (and Minimal mode) MUST NOT be blocked — over-enforcement would make the gate get routinely escape-hatched, defeating it.
- [ ] Logging/observability: the refuse path MUST state which of the four conditions triggered (mode / critic-required / absent file / missing rationale) so the user can act, not just "blocked".

## Out of scope

- Auto-*invoking* `/critique-review` from `/critique` or `/build-slice` (DR-1 v2 `**Dual-review**: true` auto-trigger candidate) — this slice enforces presence, it does not automate execution.
- Cross-referencing finding IDs between `critique.md` and `critique-review.md` (separate DR-1 v2 limitation).
- Extending CAD-1 byte-equality to `agents/critique-review.md` (separate narrow-scope item noted in methodology-changelog v0.22.0 limitations).
- Any change to `skills/critique-review/SKILL.md` task body or the `critique-review` agent prompt — this is a one-way coupling (build-slice enforces; critique-review unchanged).

## Dependencies

- Prior slices: [[slice-025-add-test-file-existence-check-for-non-pytest-rows]] — reflection L37 names this candidate; [[slice-021-add-feature-branch-workflow-at-build-and-commit-slice]] (BRANCH-1) — the audit-enforced-gate structural template + non-`-D` naming-class precedent + bootstrap-reference-instance precedent this slice mirrors; [[slice-017-address-tf-1-plan-staleness-discipline]] (TPHD-1 sub-mode (c)) — the `## Prerequisite check` placement precedent; [[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] — the mandatory-Critic default heuristic this enforces.
- Vault refs: [[skills/build-slice/SKILL.md]] (`## Prerequisite check` + Step 6 + Step 7b), [[tools/critique_review_audit.py]] (unchanged; structure validator, not skip-detector), [[architecture/decisions/ADR-019-branch-per-slice-workflow]] (non-`-D` naming-class authority), [[methodology-changelog.md]] DR-1 v0.17.0 entry, [[architecture/shippability.md]], [[CLAUDE.md]] "Builder ↔ Critic separation".
- Risk register: no open register risk (this closes a methodology-process gap surfaced in reflection, not a registered R-N).

## Mid-slice smoke gate

At ~50% of build (enforcing audit written + `skills/build-slice/SKILL.md` prose added, before methodology-changelog + shippability propagation), run:
```
& $PY -m pytest tests/methodology/test_critique_review_prerequisite_audit.py -q
& $PY -m pytest tests/methodology/test_build_slice_skill.py -k crp_1 -q
```
Expected: AC1/AC2 audit + prose-pin tests transition PENDING → WRITTEN-FAILING → PASSING; the audit refuses the synthetic absent-mandatory fixture and accepts the present / documented-skip fixtures and Important-fails the malformed-skip fixture. If the audit accepts an absent-mandatory fixture (false-negative): STOP, diagnose the mode/trigger detection — that is the slice-025 failure recurring.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/critique` AND `/critique-review` ran on slice-026 itself; audit run against slice-026's own folder (bootstrap-aware self-application)
- [ ] `/drift-check` passes; CAD-1 + PMI-1 + INST-1 + mini-CAD byte-equality clean
- [ ] TF-1 plan all PASSING (`tools/test_first_audit.py --strict-pre-finish`)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
