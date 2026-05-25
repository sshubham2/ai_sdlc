# Slice 019: harden-diagnose-layering-evidence

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: NEW class — the `/diagnose` 03f-layering pass (sole emitter of `category: layering-violation` per `schema/finding.yaml:21-32` enum + `passes/03f-layering.md:47` ground-truth grep) emits HIGH-severity findings from graphify symbol-edges without textual import-verification, producing false-positive findings that erode trust in the forensic pass and that `/slice-candidates` would treat as confirmable
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

User observed a HIGH-severity `/diagnose` finding `F-LAYER-bca9c001` claiming "45 frontend files import `src/workflow/adapters/types.ts` directly, bypassing the HTTP boundary." Manual grep verification disproved the finding: zero frontend files reach into `src/` via relative path or `@/*` alias (`tsconfig.json` maps `@/*` to `frontend/` root). The actual code shape was a parallel type file (`frontend/lib/workflow/types.ts`, 537 LOC, hand-maintained copy of backend domain enums with identical names — `NodeType`, `TaskType`, `AssigneeType`). Graphify's symbol-resolution apparently collapsed cross-file same-name symbol references into phantom import edges, and the layering pass trusted those edges at HIGH severity without grep-verifying an actual `import` statement.

This slice closes the false-positive class at the `/diagnose` pass-template level: any pass that emits a layering / boundary / cross-tier / import-violation finding MUST grep-verify a textual import statement in the cited evidence file. No textual `import` → downgrade severity to LOW or skip the finding. The fix is at the pass-template prose layer (not graphify-level) because (a) it's cheaper, (b) reversible, (c) doesn't break other graphify consumers, and (d) graphify symbol-conflation may have legitimate uses elsewhere.

## Acceptance criteria

1. The `/diagnose` 03f-layering pass template — the sole emitter of `category: layering-violation` per `schema/finding.yaml:21-32` enum (ground-truth verified 2026-05-13: `grep '^- \`category\`:' skills/diagnose/passes/*.md` returns exactly one match at `passes/03f-layering.md:47`) — carries explicit prose: **"Before emitting a HIGH-severity layering-violation finding, the pass MUST grep-verify the import statement in the evidence file. If no textual `import` matches, downgrade severity to LOW or skip the finding."** Prose carried at SKILL.md Step 5 contract + the 03f-layering pass template + installed copies, bidirectional sha256 byte-equal per CAD-1 / mini-CAD precedent (slice-007 + slice-010). Per `design.md` "Step 5 dispatch enumeration" subsection, the other 10 passes (`01-intent`, `02-architecture`, `03a-dead-code`, `03b-duplicates`, `03c-size-outliers`, `03d-half-wired`, `03e-contradictions`, `03g-dead-config`, `03h-test-coverage`, `04-ai-bloat`) are explicitly OUT of LAYER-EVID-1 scope with rationale grounded in finding-category emission shape; R-3 captures the broader-class escalation path if symbol-conflation false-positives surface in any of those passes (N≥2 distinct slices required for promotion).
2. Regression integration test against a synthetic fixture codebase (`tests/skills/diagnose/fixtures/parallel_types_no_import/`) reproducing the F-LAYER-bca9c001 shape (backend `src/types.ts` + frontend `lib/types.ts` defining same-named enums, zero frontend-to-`src/` imports) confirms the layering pass emits ZERO HIGH-severity boundary findings post-fix; pre-fix the same fixture would have fired one (captured as the failing-baseline test row before the prose change).
3. methodology-changelog `v0.33.0` / `LAYER-EVID-1` entry present in-repo + installed with substantive canonical phrase `textual import-evidence requirement` pinned across N=3 surfaces (SKILL.md Step 5 + affected pass template + in-repo + installed entries) per slice-016 RPCD-1 / slice-017 TPHD-1 3-surface precedent (N=6 → N=7 cumulative).
4. `ADR-017` exists at `architecture/decisions/ADR-017-textual-evidence-requirement-for-diagnose-boundary-findings.md` documenting the design decision (pass-template-level rule vs graphify-level fix, reversibility=cheap, supersession path if graphify symbol-conflation is later fixed upstream).
5. `R-3` added to `architecture/risk-register.md` per RR-1 schema documenting the broader class (graphify symbol-resolution may conflate same-named cross-file symbols into phantom edges; mitigation = textual-evidence rule at `/diagnose` pass layer; reversibility=cheap; status=mitigating).

## Test-first plan

Each AC maps to failing tests written BEFORE implementation. Per TF-1 + TPHD-1 (slice-017), function names + AC row references in this plan must stay harmonized with `design.md` through any `/critique` / `/critique-review` fix-prose.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_step5_documents_textual_evidence_rule | PASSING |
| 1 | unit | tests/skills/diagnose/test_skill_md_pins.py | test_layering_pass_template_emits_textual_evidence_rule | PASSING |
| 1 | unit | tests/skills/diagnose/test_skill_md_pins.py | test_textual_evidence_rule_byte_equal_across_n_3_surfaces | PASSING |
| 1 | integration | tests/skills/diagnose/test_diagnose_skill_drift.py | test_in_repo_and_installed_diagnose_skill_md_are_content_equal | PASSING |
| 1 | integration | tests/skills/diagnose/test_diagnose_skill_drift.py | test_in_repo_and_installed_diagnose_03f_layering_md_are_content_equal | PASSING |
| 2 | integration | tests/skills/diagnose/test_layering_pass_textual_evidence.py | test_synthetic_parallel_types_no_import_yields_zero_high_layering_findings | PASSING |
| 2 | integration | tests/skills/diagnose/test_layering_pass_textual_evidence.py | test_synthetic_real_cross_tier_import_still_fires_high_layering_finding | PASSING |
| 3 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed | PASSING |
| 3 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase | PASSING |
| 3 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_adr_017_exists_and_names_layer_evid_1_canonical_phrase | PASSING |
| 5 | unit | tests/methodology/test_risk_register_audit_real_file.py | test_r_3_added_post_slice_019_with_graphify_symbol_conflation_class | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Textual-evidence prose carried at N=3 surfaces, bidirectional byte-equal | `pytest tests/skills/diagnose/test_skill_md_pins.py::test_skill_md_step5_documents_textual_evidence_rule tests/skills/diagnose/test_skill_md_pins.py::test_layering_pass_template_emits_textual_evidence_rule tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces tests/skills/diagnose/test_diagnose_skill_drift.py` |
| 2 | F-LAYER-bca9c001-class false-positive no longer fires; true-positive cross-tier import still does | `pytest tests/skills/diagnose/test_layering_pass_textual_evidence.py` |
| 3 | methodology-changelog `v0.33.0` LAYER-EVID-1 entry in-repo + installed with canonical phrase | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant` |
| 4 | ADR-017 present + names canonical phrase | `pytest tests/methodology/test_methodology_changelog.py::test_adr_017_exists_and_names_layer_evid_1_canonical_phrase` |
| 5 | R-3 added to risk-register.md per RR-1 schema | `pytest tests/methodology/test_risk_register_audit_real_file.py::test_r_3_added_post_slice_019_with_graphify_symbol_conflation_class`; cross-check `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --sort score` shows R-3 present |

## Must-not-defer

- [ ] Textual-evidence rule MUST propagate to ALL `/diagnose` passes that emit boundary / cross-tier / import-violation findings, not just the layering pass — design.md must enumerate the affected passes from Step 5 dispatch table; failing to propagate means the false-positive class just migrates to a sibling pass
- [ ] methodology-changelog `v0.33.0` LAYER-EVID-1 entry MUST be byte-equal in-repo ↔ installed (bidirectional sha256 forensic capture N=14 → N=15)
- [ ] `agents/critique.md` byte-equal in-repo ↔ installed preserved at slice-017 ship hash `f34c967eaaa34413` (no Critic-agent edit this slice)
- [ ] `/diagnose` SKILL.md byte-equal in-repo ↔ installed (mini-CAD precedent slice-007 + slice-010)
- [ ] `plugin.yaml.version == VERSION == 0.33.0` atomic bump under PMI-1 v1.1 version-agnostic-gate (5th atomic bump post-slice-014 retirement; N=4 → N=5 stable)
- [ ] R-3 entry parses cleanly under RR-1 audit (correct heading format, all required fields)
- [ ] TPHD-1 (slice-017) self-application at all 3 sub-modes during `/critique` and `/critique-review` fix-prose if function names / AC row references change
- [ ] SCPD-1 (slice-015) propagation: shippability.md gains row 19 with the slice-019 critical-path pytest command BEFORE `/validate-slice` Step 5.5 catalog run
- [ ] Authorization / validation / error-paths: N/A — this slice modifies prose contracts + adds tests, no runtime code paths that handle user data or auth
- [ ] Logging: the new layering-pass evidence-check should emit a `note:` field on any downgraded/skipped finding explaining "skipped: no textual import grep-match" so users can audit the decision

## Out of scope

- **Graphify-level fix to symbol-resolution conflation across same-name cross-file symbols.** The root cause hypothesis is in `graphify-out/graph.json` resolving type-symbol references too aggressively. Fixing graphify would have broad blast radius (affects all consumers — `/architect`, `/validate`, `/discuss`, `/sprint-runner`, etc.) and is reversible cheaply. R-3 captures this as a tracked broader-class risk; a future slice may take it up if `/critic-calibrate` flags symbol-conflation false-positives in other passes too.
- **Other `/diagnose` pass false-positive classes** (e.g., the duplicate-detection pass possibly missing the parallel-type-file as duplication because graphify collapsed the symbols — separate concern, different evidence shape, different fix surface).
- **Refactoring the parallel type file** (`frontend/lib/workflow/types.ts` as hand-maintained copy of backend types) — that's the user's target-project concern, not a pipeline-self-improvement slice.
- **Adding the textual-evidence rule to other audits** beyond `/diagnose` (e.g., `tools/build_checks_audit.py`'s import-related rules) — different code path, different test surface.

## Dependencies

- Prior slices:
  - [[slice-001-diagnose-orchestration-fix]] — established the `/diagnose` pass-template contract that this slice extends
  - [[slice-002-fix-diagnose-contract-and-cwd-mismatch]] — established SKILL.md Step 1 cwd-mismatch warning pattern; this slice's pass-template prose follows similar surgical-prose-pin discipline
  - [[slice-007-add-critique-agent-content-equality-audit]] — established CAD-1 bidirectional byte-equality pattern; this slice reuses mini-CAD shape for `/diagnose` SKILL.md
  - [[slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class]] — RPCD-1 sub-mode (a) NEW-symbol import-audit applies: any new pytest function name introduced in this slice's TF-1 plan must exist on-disk by `/build-slice` Phase 6
  - [[slice-017-address-tf-1-plan-staleness-discipline]] — TPHD-1 applies at all 3 sub-modes for this slice's `/critique` + `/critique-review` + `/build-slice` Prerequisite check
- Vault refs:
  - [[decisions/ADR-001-diagnose-subagent-io-contract]] — base contract for `/diagnose` pass templates
  - [[shippability]] — row 19 to be added per SCPD-1 sub-mode (b) proactive-application
- Risk register:
  - [[risk-register#R-1]] — open cwd-mismatch class on `/diagnose`, NOT addressed by this slice (separate fix surface)
  - [[risk-register#R-3]] — NEW entry added by this slice

## Mid-slice smoke gate

At ~50% of build (after textual-evidence prose written into SKILL.md Step 5 + layering pass template, before regression-fixture and methodology-changelog work), run:

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/skills/diagnose/test_skill_md_pins.py::test_skill_md_step5_documents_textual_evidence_rule `
  tests/skills/diagnose/test_skill_md_pins.py::test_layering_pass_template_emits_textual_evidence_rule `
  --no-header -q
```

Expected: both tests PASS (prose-pin tests for the new rule). If fails: prose wording doesn't match the test's canonical-phrase pin — refine prose, don't loosen test. If passes: continue to fixture construction + methodology-changelog work. If unexpected sibling test fails: STOP, the prose change broke an adjacent pin; diagnose before continuing.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] All must-not-defer items addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `tools/test_first_audit.py --strict-pre-finish` returns 0 (all TF-1 rows PASSING; per TPHD-1 sub-mode (c))
- [ ] `tools/walking_skeleton_audit.py --strict-pre-finish` not applicable (this slice carries `Walking-skeleton: false`)
- [ ] `tools/exploratory_charter_audit.py --strict-pre-finish` not applicable (this slice carries `Exploratory-charter: false`)
- [ ] `tools/wiring_matrix_audit.py` PASSES against `design.md`
- [ ] `tools/build_checks_audit.py` clean against slice-019 mission-brief.md + design.md (BC-PROJ-2 negative-anchor migration from slice-012 should silence methodology-vocabulary false-positives)
- [ ] `tools/plugin_manifest_audit.py` PASSES at version 0.33.0 (PMI-1 v1.1 version-agnostic gate; no skill/agent/tool added by this slice)
- [ ] `tools/critique_agent_drift_audit.py --repo-root .` PASSES at slice-017 ship hash `f34c967eaaa34413` for `agents/critique.md` (no Critic-agent edit this slice)
- [ ] `tools/risk_register_audit.py architecture/risk-register.md` PASSES with R-3 added
- [ ] shippability.md row 19 propagated per SCPD-1 sub-mode (b) BEFORE `/validate-slice` Step 5.5 catalog run
