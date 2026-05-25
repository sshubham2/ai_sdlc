# Critique Review: Slice 063 add-build-slice-new-agent-warning

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-23
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is structurally strong — all 10 findings are VALID with correct severities, all 10 ACCEPTED-FIXED dispositions are properly applied across mission-brief.md + design.md + ADR-061, and B1's proposed three-source fix mechanism is empirically correct (verified by reproducing untracked + staged add states against a synthetic git repo). TF-1 audit re-verified clean (9 rows / 5 ACs / 0 violations) — no RSAD-1 self-violation on the fix block. However, three missed findings surface from independent re-review: a 5-part PMI-1 leg enumeration drift in design.md L17 vs ADR-061 L85 + slice-060/062 precedent (5 legs canonically; design.md lists 7), an incomplete EPGD-1 entry-pin anchor list missing the META-1-mandatory "Rule reference" literal + `"## v0.66.0"` header, and a Step 6 audit-count enumeration drift (design.md L218 says "14 audits" and incorrectly includes `plugin_manifest`, but `skills/build-slice/SKILL.md` Step 6 has only 13).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1**: Audit's `git diff <base>...HEAD` cannot observe uncommitted slice work — VALID, Blocker severity correct. Empirically reproduced: a `slice/feature` branch with an untracked `agents/new.md` returns EMPTY from `git diff --name-only --diff-filter=A master -- 'agents/*.md'` BEFORE staging, but POPULATED after `git add`; `git ls-files --others` covers the untracked-only state. Proposed three-source union is empirically sound. Per Fowler / Newman the design rests on an unverified upstream-mechanism assumption that real execution falsifies — Blocker is correct.
- **M1**: Phantom `tests/methodology/test_risk_register.py` — VALID, Major correct. `Glob tests/methodology/test_risk_register*.py` returns only `test_risk_register_audit.py` + `test_risk_register_audit_real_file.py`; post-fix mission-brief L38 correctly cites the latter. PTFCD-1 class is properly characterised.
- **M2**: `--strict-pre-finish` flag drift mission-brief ↔ design.md — VALID, Major correct. Mission-brief Must-not-defer item rewritten cleanly; remaining `--strict-pre-finish` references at mission-brief L102 + design.md L217 are for `tools/test_first_audit.py` (legitimately a slice-folder audit with that flag), not the new audit — no residual drift.
- **M3**: BRANCH-1 "fallback `main`" misattribution — VALID, Major correct. Verified at `tools/branch_workflow_audit.py:127-146`: `_resolve_default_branch` returns `None` after both `git symbolic-ref` and `init.defaultBranch` fail; there is NO `"main"` literal fallback. Post-fix design.md L25 + ADR-061 L65 prose now correctly reads `None ⇒ usage error exit 2`.
- **M4**: AC#2 test housed in wrong file — VALID, Major correct. `tests/methodology/test_build_slice_skill_drift.py` is single-test content-equality (Mini-CAD-1); `tests/methodology/test_build_slice_skill.py` exists separately for structural-anchor pins. Post-fix mission-brief L32 correctly cites the latter.
- **m1**: BC-PROJ-9 precedent misattribution — VALID, Minor correct. Design.md L16 post-fix correctly attributes "slice-059 precedent on the 5-inventory completeness; slice-050 AVFS-1 tool-addition precedent on the 4-inventory subset".
- **m2**: `agents/*.md` pathspec overbroad — VALID, Minor correct. `agents/AUTHORING.md` empirically present and not in `_CANONICAL_AGENTS` (`tools/install_audit.py:61-64`); accepted as known-false-positive class in ADR-061 L106.
- **m3**: Bootstrap-brittle self-application test — VALID, Minor correct. Post-fix mission-brief L37 + design.md L61 + ADR-061 L107 consistently rename to `test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents` with `added_files_resolver` seam-driven approach (TPHD-1 sub-mode (a) harmonization clean).
- **m4**: CAD-1/OSDG-1 family-confusion phrasing — VALID, Minor correct. Mission-brief L105 pre-finish gate now clearly distinguishes Mini-CAD-1 / OSDG-1 build_slice variant from CAD-1 (agents/critique.md).
- **m5**: Missing entry-pin anchor list — VALID, Minor correct (but anchor list is incomplete — see Missed M-add-2 below).

## Suspicious findings

No suspicious findings — every first-Critic finding traces to specific design/mission/ADR evidence verified by Read/Grep/empirical execution.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

- **M-add-1 (Major) — 5-part PMI-1 leg enumeration drift between design.md and ADR-061**:
  - **Design.md L17** enumerates **7 things** and calls them "5-part PMI-1 atomic bump": `VERSION + plugin.yaml.version + pyproject.toml.version + ## v0.66.0 header + ~/.claude/ai-sdlc-VERSION (AVFS-1) + ~/.claude/methodology-changelog.md (MCFS-1) + ai-sdlc-tools 0.66.0 (TVFS-1)`.
  - **ADR-061 L85** correctly enumerates **5 legs**: `VERSION + plugin.yaml.version + pyproject.toml.version + ## v0.66.0 header + ~/.claude/ai-sdlc-VERSION`. TVFS-1 + MCFS-1 are bucketed under BC-PROJ-9 fan-out, NOT as PMI-1 legs.
  - **Precedent (slice-060 / slice-062 / methodology-changelog v0.64.0 + v0.65.0)** consistently treats the "5 legs" as `VERSION + plugin.yaml.version + pyproject.toml.version + ## vNN header + ~/.claude/ai-sdlc-VERSION`. MCFS-1 + TVFS-1 are separate forward-syncs.
  - **Framework**: Wiegers / Hendrickson cross-document consistency — the same defect class as slice-062 /critique-review M-add-2 (cross-document option-enumeration drift). At /build-slice the entry-pin test `test_v_0_66_0_naw_1_entry_present_in_repo` will assert `"5-part PMI-1 atomic bump"` literally per slice-062 m3 stale-carry guard, but the v0.66.0 changelog entry body authored from design.md L17's "7-thing" interpretation will either (a) miscount as "5-part" and contradict the explicit leg list, or (b) be miswritten as "7-part" and fail the entry-pin.
  - **Proposed fix**: Align design.md L17 with ADR-061 L85's authoritative 5-leg enumeration: drop the MCFS-1 + TVFS-1 legs from the "5-part PMI-1 atomic bump" sentence; document them separately as BC-PROJ-9 fan-out / forward-sync obligations (mission-brief.md L56 already does this correctly — "AVFS-1 + MCFS-1 + TVFS-1 forward-syncs" listed as a separate must-not-defer bullet). Severity: Major (PMI-1 atomic-bump leg-count drift is the slice-060 B2 + slice-062 B1 + slice-054 / slice-058 lineage's central recurring defect class; an authoring miss here propagates to the v0.66.0 entry text and would fail the entry-pin test).
  - **Builder draft**: ACCEPTED-FIXED — design.md L17 rewritten in this fix block to drop MCFS-1 + TVFS-1 from the 5-part leg enumeration; documents both separately as post-bump forward-sync obligations (matches mission-brief L56 + ADR-061 L85 verbatim 5-leg shape).

- **M-add-2 (Minor) — EPGD-1 entry-pin anchor list incomplete: missing `Rule reference` (META-1 mandatory) + `## v0.66.0` header anchors**:
  - **Design.md item 8** enumerates 6 anchors: `"NAW-1"` + `"ADR-061"` + `"New-Agent Warning"` + `"mints a new rule"` + `"supersedes nothing"` + `"5-part PMI-1 atomic bump"`.
  - **Slice-062 / v0.65.0 entry-pin (`tests/methodology/test_methodology_changelog.py:4060-4109`)** asserts 8 anchors including (a) `## v0.65.0` header presence + (g) `Rule reference` literal — the META-1 enforcing-assertion at `tests/methodology/test_methodology_changelog.py:136` REQUIRES `Rule reference` in each `## vN.NN.0` section.
  - **Slice-060 / v0.64.0 entry-pin** likewise asserts (a) `## v0.64.0` header + (g) `Rule reference` per the same META-1 obligation.
  - **Framework**: EPGD-1 design-time pre-emption discipline (slice-062 m2 lesson) — explicit anchor enumeration at design-time should mirror the precedent's set exactly, not a subset.
  - **Proposed fix**: Extend design.md item 8's anchor list to 8 anchors: add `"## v0.66.0"` header anchor + `"Rule reference"` literal (META-1 obligation). Without these, the `entry_present_in_repo` test as written at /build-slice may either (a) be authored with only the 6 design-cited anchors → drift from slice-062 precedent shape, or (b) be authored ad-hoc with extra anchors → silent design-vs-test drift the first Critic m5 was trying to prevent. Severity: Minor (no production-impact path; only a methodology-test-pin completeness issue).
  - **Builder draft**: ACCEPTED-FIXED — design.md item 8 anchor list extended in this fix block from 6 → 8 anchors (adds `"## v0.66.0"` header anchor + `"Rule reference"` literal per META-1 obligation at `test_methodology_changelog.py:136`).

- **M-add-3 (Minor) — Design.md L218 Step 6 audit count miscount: enumerates `plugin_manifest` as if in Step 6, but `skills/build-slice/SKILL.md` Step 6 checklist has 13 items (no PMI-1)**:
  - **Design.md L218 ("Validation strategy" step 2)**: lists 14 audits `(branch_workflow / utf8_stdout / critique_review_prerequisite / pipeline_chain / build_checks_integrity / methodology_changelog_forward_sync / state_transition_pin / ai_sdlc_version_forward_sync / ai_sdlc_tools_version_forward_sync / mock_budget_lint / wiring_matrix / build_checks / test_first / plugin_manifest)` — counted 14, last item is `plugin_manifest`.
  - **`skills/build-slice/SKILL.md` Step 6 (L138-155)**: 13 items, no `plugin_manifest`/PMI-1 line. `grep -n "plugin_manifest" skills/build-slice/SKILL.md` returns empty.
  - **Framework**: Wiegers cross-doc consistency / Newman contract-doc-vs-implementation parity. Post-NAW-1 the actual Step 6 has 14 items (13 existing + NAW-1), not 14 + NAW-1 = 15 as L218 implies.
  - **Proposed fix**: Drop `plugin_manifest` from design.md L218's audit list (and re-verify against SKILL.md L138-155); the post-NAW-1 Step 6 count is 14 audits, not 15. Alternatively, if the author intends to include PMI-1 as a Step 6 audit that is invoked indirectly via `build_checks_audit`, that should be made explicit. Severity: Minor (cosmetic drift; no implementation impact — the actual `/build-slice` Step 6 runner is driven by SKILL.md, not design.md prose).
  - **Builder draft**: ACCEPTED-FIXED — design.md L218 (Validation strategy step 2) rewritten in this fix block to enumerate the actual 13 audits in `skills/build-slice/SKILL.md` Step 6 (L138-155) + the new NAW-1 = 14 audits post-slice-063. `plugin_manifest` dropped (PMI-1 is enforced via paired tests, not a Step 6 checklist line).

## Severity adjustments

No severity adjustments — every first-Critic finding's severity is appropriate (B1 correctly Blocker on the falsifier class per Dim 1 + Dim 8; M1-M4 correctly Major on cross-doc drift + phantom-citation class; m1-m5 correctly Minor on attribution + cosmetic-prose class).

## Notes

Confidence: high on B1's empirical correctness (reproduced both untracked + staged source detection against a synthetic git repo; the proposed three-source union is sound). Confidence: high on the 10 ACCEPTED-FIXED dispositions being correctly applied (`grep` confirmed cross-file consistency on `strict-pre-finish`, `fallback main`, `test_risk_register`, `test_self_application_*`, `5-part`/`4-part` anchors, `test_build_slice_skill.py` vs `test_build_slice_skill_drift.py`). TF-1 audit re-verified empirically clean post-fix (`violation_count: 0`, 9 rows, 5 ACs) — confirms NO slice-022 RSAD-1 self-violation pattern on the same-fix-block edits (the N=2 slice-056 + slice-062 lesson the meta-Critic was hunting for). M-add-1's 5-part-leg-miscount is the strongest of the missed findings and the same class as slice-060 B2 / slice-062 B1 — a recurring lineage defect the first Critic's Dimension 7 (Drift from vault) check should have caught at the cross-doc consistency layer between design.md L17 and ADR-061 L85. M-add-2 and M-add-3 are smaller misses but together suggest the first Critic's Dimension 9 (Cross-cutting conformance) coverage on N-part-bump precedent enumeration + Step 6 audit-list completeness could be tighter on this slice class. The slice mints NAW-1 cleanly and the core mechanism is now empirically sound — the missed findings are authoring-completeness issues, not load-bearing-design issues.

Sources:
- https://git-scm.com/docs/git-diff
- https://git-scm.com/docs/git-ls-files
