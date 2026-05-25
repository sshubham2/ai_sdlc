# Critique: Slice 013 refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class

**Critic reviewed**: mission-brief.md, design.md, ADR-012, milestone.md
**Date**: 2026-05-13
**Result**: NEEDS-FIXES

## Summary

Design is structurally sound (EPGD-1 codification follows slice-011 RSAD-1 precedent cleanly; self-application Audits 4+5 are concrete and empirically pre-verified against current `tests/methodology/test_methodology_changelog.py` SECTION-header layout; BC-1 self-application audit predicted-clean was verified to actually be clean). One Blocker: rule-ID inconsistency between mission-brief (`EPG-1`, 22 occurrences) and design.md + ADR-012 + milestone.md (`EPGD-1`, locked). Three Majors: (1) latent precision-degradation of slice-011's `_names_both_sub_modes` regression-guard once slice-013 widens the body bounds to include the new 7th sub-clause; (2) `test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012` substantive-anchor list under-specified for /build-slice author; (3) mission-brief N-surface count ("N=2 surfaces") undercounts the actual N=3 surfaces (critique.md + in-repo changelog + installed changelog).

Recursive-self-application N=5 cumulative confirmed: the slice authoring EPGD-1 has its own draft showing rule-ID drift between artifacts — the exact class RSAD-1 was codified to catch (Dim 9 sub-clause 6, design-time mode: "slice authoring rule X had its own prose checked under rule X"). Strongest single recursive-self-application catch at slice-013.

## Findings

### Blockers (must address before /build-slice)

#### B1: Rule-ID drift between mission-brief and design.md/ADR-012/milestone.md (EPG-1 vs EPGD-1)

- **Claim under review** (mission-brief.md L12): "Rule reference candidate **EPG-1** (Entry-Pin-vs-Gate; /critique-time adversarial-prompt + /build-slice-time Edit-discipline; suffix convention deferred to /design-slice per slice-010 B5 + slice-011 -D-suffix calibration-trail discipline at N=2 stable)."
- **Claim under review** (design.md L10): "A new `methodology-changelog.md` v0.28.0 entry naming **EPGD-1** as the new methodology rule reference."
- **Claim under review** (milestone.md L29): "Rule ID locked: **EPGD-1** (Entry-Pin-Gate-Discipline; -D suffix per slice-011 RSAD-1 -D-suffix N=2 stable confirmation)."
- **Issue**: /design-slice locked the rule ID to `EPGD-1` (per milestone.md + design.md + ADR-012 — 29 occurrences in design.md, 31 in ADR-012, 0 of `EPG-1`). Mission-brief was NOT updated to reflect the lock — still uses `EPG-1` in 22 places (test-first plan, verification plan, must-not-defer items, dependencies, pre-finish gates). Concretely:
  - Mission-brief test-first plan row 4 (line 36): `test_v_0_28_0_epg_1_entry_present_in_repo_and_installed`
  - Design.md L14: `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed`
  - Mission-brief AC #4 (line 19): "names **EPG-1** (or final rule ID chosen at /design-slice)" — parenthetical hedge no longer applies post-lock
- **Evidence**: `grep -c "EPG-1" mission-brief.md` → 22; same file `grep -c "EPGD-1"` → 0. `grep -c "EPGD-1" design.md` → 29; `grep -c "EPG-1" design.md` → 0. ADR-012 → 31 `EPGD-1` / 0 `EPG-1`. milestone.md L29 says "Rule ID locked: **EPGD-1**".
- **Proposed fix**: Update mission-brief.md in-place — rename all 22 `EPG-1` occurrences to `EPGD-1` (test function names `_epg_1_` → `_epgd_1_`, narrative `EPG-1` → `EPGD-1`). Without this fix, the Builder receives conflicting instructions about both the rule ID in the methodology-changelog entry AND the exact test function name to create.
- **Builder draft**: ACCEPTED-FIXED — apply mission-brief.md global rename `EPG-1` → `EPGD-1` in this round (pre-build). Mission-brief is the artifact that drifted. RSAD-1 (Dim 9 sub-clause 6 design-time mode) self-application catch — exactly the class the discipline was codified for. **N=5 recursive-self-application instance confirmed empirically; not just hypothesized at design.md L169-178**.

### Majors (address this slice)

#### M1: slice-011 `_names_both_sub_modes` regression-guard precision degrades silently once 7th sub-clause appended

- **Claim under review** (mission-brief.md L67, must-not-defer): "Mini-CAD-1 row 3 regression-guard: `test_critique_dim_9_recursive_self_application_sub_clause_present` (slice-011's 6th-sub-clause-substring-pin) continues PASSING throughout the slice."
- **Issue**: Must-not-defer covenant tracks only ONE slice-011 test as regression-guard (substring-pin `_sub_clause_present`). Slice-011 also added `test_critique_dim_9_recursive_self_application_names_both_sub_modes` (test_critique_agent.py L178-206), body-bounded on `start_anchor = "Recursive self-application discipline"` + `end_anchor = "### Bonus: weak graph edges"`. Slice-013 appends new 7th sub-clause BETWEEN these anchors, so `body` widens to include the NEW 7th sub-clause body. The new 7th sub-clause body contains "Build-time slip mode" + "Design-time-pre-empted success mode" (design.md L106-107), so `assert "design-time" in body` + `assert "build-time" in body` would PASS even if RSAD-1's body somehow lost those substrings — slice-011 test's semantic intent (verifying RSAD-1 body covers both sub-modes) is undermined. Latent precision-degradation, not correctness regression, but weakens slice-011 regression-guard.
- **Evidence**: `tests/methodology/test_critique_agent.py:178-206`; design.md L105-109 (new sub-clause body contains both sub-mode substrings).
- **Proposed fix**: Tighten slice-011 `_names_both_sub_modes` end anchor at /build-slice — change `end_anchor = "### Bonus: weak graph edges"` to `end_anchor = "Entry-pin-vs-PMI-1-gate semantics conflation"` (new 7th sub-clause's canonical title) so body bounds stay scoped to ONLY 6th sub-clause. ADDITIONALLY add NEW slice-013 test `test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes` (start_anchor = `Entry-pin-vs-PMI-1-gate semantics conflation`, end_anchor = `### Bonus: weak graph edges`, asserts both `Build-time slip mode` AND `Design-time-pre-empted success mode`) for symmetric 7th-sub-clause sub-mode pin.
- **Builder draft**: ACCEPTED-PENDING — apply both at /build-slice. TF-1 plan grows 8 → 10 rows: add row "tests/methodology/test_critique_agent.py | (modify slice-011 test: tighten end_anchor) | WRITTEN-AS-EDIT" + row "tests/methodology/test_critique_agent.py | test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes | PENDING". Mid-slice smoke gate must verify both transitions.

#### M2: `_paragraph_cites_slice_011_and_012` substantive-anchor list under-specified; /build-slice author choice creates drift risk

- **Claim under review** (mission-brief.md L34 + L58): test "asserts canonical substrings `slice-011`, `slice-012`, AND substantive discipline anchors (per /design-slice choice) all present".
- **Issue**: "per /design-slice choice" delegates anchor selection to design phase, but design.md L8 lists anchors as prose only: "Cross-slice anchors: `slice-011`, `slice-012`, `Phase 1b INSERT`, `Phase 1c narrow-scope Edit`, `Audit 6 structural-separation`, `SECTION header`". Not formalized as strict-both / ≥k-of-n shape (slice-011's `_cites_at_least_two_cross_slice_anchors` had strict-both for cross-slice + ≥1-of-6 for sub-class). Builder may choose smaller/different anchor set at /build-slice, creating /critique→/build alignment drift.
- **Evidence**: design.md L8 (prose-only anchor list); slice-011 `_cites_at_least_two_cross_slice_anchors` (test_critique_agent.py L209-241) with explicit lists + strict semantics.
- **Proposed fix**: Formalize anchor lists in design.md with strict semantics:
  ```
  Cross-slice anchors (strict-both): ["slice-011", "slice-012"]
  Substantive-discipline anchors (≥2 of N): ["Phase 1b INSERT", "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]
  ```
  Update mission-brief AC #2 + verification plan row 2 to cite these lists with strict-both + ≥2-of-4 semantics.
- **Builder draft**: ACCEPTED-FIXED — formalize anchor lists in design.md "What's new" section with explicit strict-both + ≥2-of-4 semantics; update mission-brief AC #2 + verification plan row 2 to match.

#### M3: N-surface count drift — mission-brief says "N=2 surfaces" but discipline yields N=3 surfaces

- **Claim under review** (mission-brief.md L19, AC #4): "N-surface schema-pin discipline N=4 → N=5 ratchet: substantive canonical phrase ... pinned across N=2 surfaces (in-repo entry title + installed entry title) per slice-008/009/010/011/012 entry-pin discipline N=4 stable."
- **Issue**: Canonical phrase `Entry-pin-vs-PMI-1-gate semantics conflation` is ACTUALLY pinned across THREE surfaces in slice-013's test plan:
  1. `agents/critique.md` Dim 9 new 7th sub-clause title (via `test_critique_dim_9_entry_pin_vs_pmi_1_gate_sub_clause_present`, AC #1 row 1)
  2. In-repo `methodology-changelog.md` v0.28.0 entry (via AC #4 test)
  3. Installed `~/.claude/methodology-changelog.md` v0.28.0 entry (via AC #4 test)
  
  Mirrors slice-011 RSAD-1 3-surface pin (`test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` docstring at test_methodology_changelog.py L260-265 explicitly says "ONE canonical phrase pinned across N=3 surfaces").
- **Evidence**: tests/methodology/test_methodology_changelog.py L260-265.
- **Proposed fix**: Update mission-brief.md AC #4 (line 19) — change "pinned across N=2 surfaces" to "pinned across N=3 surfaces (agents/critique.md Dim 9 7th sub-clause title + in-repo entry + installed entry) per slice-011 RSAD-1 3-surface schema-pin precedent". The N-surface discipline lineage: slice-011 introduced 3-surface pin; slice-013 ratchets to N=2-instances-stable at 3-surface shape.
- **Builder draft**: ACCEPTED-FIXED — update mission-brief AC #4 wording to reflect actual N=3 surfaces (matching slice-011 RSAD-1 precedent). Also propagate corrected framing to test_methodology_changelog.py docstring for the new EPGD-1 entry-pin test ("ONE canonical phrase pinned across N=3 surfaces").

### Minors (log; address if cheap)

#### m1: ADR-012 § Decision uses "L172" to mean the close-line of RSAD-1 sub-clause (visually ambiguous)

- **Claim under review** (ADR-012 L40): "Append ONE new sub-clause to `agents/critique.md` Dim 9 at L173 between the existing L172 `Recursive self-application discipline` (RSAD-1) sub-clause close and the existing L174 `### Bonus: weak graph edges` H3 anchor."
- **Issue**: Phrasing reads as if "L172" is where literal title `Recursive self-application discipline` lives. Actually L168 is title-line; L172 is close of sub-clause body. Design.md L102 phrases more clearly.
- **Evidence**: agents/critique.md L168 (title) / L172 (last paragraph) / L174 (H3).
- **Proposed fix**: Rephrase ADR-012 L40: "Append ONE new sub-clause ... at L173 between L172 (close of RSAD-1 sub-clause body — title at L168) and L174 (`### Bonus: weak graph edges` H3)".
- **Builder draft**: ACCEPTED-FIXED — cosmetic rephrase of ADR-012 L40.

#### m2: ADR-012 § Options considered ratchets unclear claim ("N=2 stable") — slice-013 itself is the N=2 instance

- **Claim under review** (ADR-012 L42): "Test `test_critique_dim_9_lists_six_sub_clauses` REPLACED ... slice-011 N=1 precedent; slice-013 N=2 stable extends ..."
- **Issue**: "N=2 stable" is convention's status _after_ slice-013 ships. ADR-012 is design-stage artifact; N=2 is _pending_ ratchet. slice-011 + slice-012 reflections use "promote at N=2 if recurs at slice-NNN+"; "stable" is post-empirical-validation language.
- **Evidence**: slice-011 reflection L107.
- **Proposed fix**: ADR-012 L42 — change "slice-013 N=2 stable extends" to "slice-013 N=2 ratchets pending empirical validation at /build-slice + /reflect; if Phase 1f structural-invariant supersession Edit cleanly succeeds, N=2 promotes to stable in slice-013 reflection.md".
- **Builder draft**: ACCEPTED-FIXED — cosmetic accuracy fix.

#### m3: Verification plan row 4 still parenthetical-hedges rule ID — "the chosen rule ID (`EPG-1` or final)"

- **Claim under review** (mission-brief.md L60, verification plan row 4): "asserts in-repo + installed `methodology-changelog.md` both contain `## v0.28.0 —`, the chosen rule ID (`EPG-1` or final), AND substantive canonical phrase `Entry-pin-vs-PMI-1-gate semantics conflation`"
- **Issue**: Duplicate-instance of B1's symptom (mission-brief authored before /design-slice locked rule ID). "EPG-1 or final" parenthetical no longer applies. Flagged separately as Minor in case B1's primary remediation overlooks this site.
- **Evidence**: same as B1.
- **Proposed fix**: Replace `(EPG-1 or final)` with `EPGD-1` as part of B1 sweep.
- **Builder draft**: ACCEPTED-FIXED — folded into B1's global rename pass.

## Dimensions checked

- [x] **Unfounded assumptions** — finding B1 (rule-ID drift between mission-brief and design.md/ADR-012/milestone.md is an unfounded-assumption-class issue: mission-brief assumed "EPG-1 or final" without ratcheting after /design-slice lock). Design.md Audit 4 + Audit 5 are CONCRETE empirical predictions (pre-Edit structural-separation verified against current test_methodology_changelog.py SECTION-header layout — `# --- Slice-012 / BC-PROJ-2 entry pinning ---` at L300 + `# --- PMI-1 cleanliness gate at v0.27.0 ---` at L366 don't share intervening prose).

- [x] **Missing edge cases** — no findings beyond M1 (precision-degradation of slice-011 `_names_both_sub_modes` regression-guard). Empty/null/network/permission don't apply to a prose-prompt slice. Concurrency (two Builder agents editing simultaneously) is documented under PMI-1 atomicity.

- [x] **Over-engineering** — none. Slice is minimal append-new (Option 1 per ADR-012 L38-57; Options 2 + 3 explicitly rejected with reasoned rationale). Sub-clause body ~15 lines prose; reversibility cheap.

- [x] **Under-engineering** — findings M1 (TF-1 plan should add sub-mode pin for new 7th sub-clause symmetric to slice-011's `_names_both_sub_modes`) + M2 (substantive-anchor list under-specified for /build-slice author). Otherwise TF-1 row coverage per AC adequate at 8 rows; will grow to 10 post-M1.

- [x] **Contract gaps** — none. No new endpoints, events, or external integrations.

- [x] **Security** — none. Slice modifies prose content in canonical methodology files; no runtime authorization, no new auth paths, no PII/secrets surfaces.

- [x] **Drift from vault** — none:
  - ADR-012 supersedes: null (extends ADR-010 RSAD-1 as sibling sub-clause; verified consistent with ADR-005/008/010 lineage)
  - Code paths referenced exist: `tools/critique_agent_drift_audit.py` ✓ `tools/plugin_manifest_audit.py` ✓ `tools/build_checks_audit.py` ✓ `tools/test_first_audit.py` ✓
  - No active risk-register entry ignored
  - Design.md "Out-of-repo files touched" table cells verified against `_CANONICAL_AGENTS` + `_CANONICAL_METADATA` + INSTALL.md Step 3f do-not-copy list. **Mechanical-tables cell-verification PASSED** per Dim 9 sub-clause 2.

- [x] **Web-known issues** — skipped — methodology prose slice; no external technology, API, platform-version, quota, or vendor dependency. No realistic web-search target.

- [x] **Cross-cutting conformance**:
  - **Methodology-audit conformance**: TF-1 row coverage at 8 rows covers ACs 1-5 with PENDING genuineness pinned per row. Algorithm-path-conformance: no new branches. PMI-1 supersession Edit narrow-scope self-applied via Audit 4+5.
  - **Tooling-doc-vs-implementation parity** (Dim 9 sub-clause 2): design.md "Out-of-repo files touched" cells verified against canonical inventories. Clean.
  - **Algorithm-path-conformance**: no pre-existing branches modified.
  - **Runtime-environment** / **Language-version**: prose slice; no cwd/permission/Python-3.12 risk.
  - **Recursive self-application discipline (RSAD-1)**: B1 IS itself a recursive-self-application instance — slice authoring EPGD-1 had its own draft showing rule-ID drift between artifacts. Audit 4 + Audit 5 pre-verified EPGD-1 self-application empirically. **N=5 recursive-self-application instance confirmed empirically; not just hypothesized at design.md L169-178**. Strongest single recursive-self-application catch at slice-013.
  - **Entry-pin-vs-PMI-1-gate semantics conflation (the very rule being codified)**: pre-verified Audit 4 + Audit 5 against current test_methodology_changelog.py L300 + L366. Two SECTION headers structurally separated. Phase 1b would INSERT `# --- Slice-013 / EPGD-1 entry pinning ---` between L363 (end of slice-012 entry-pin function) and L366 (start of PMI-1 gate SECTION header). Phase 1c Edit `old_string` narrow-scopes to L366-L416 only. **Structural-separation prediction VALIDATED at design-time**.

## Triage

**Triaged by**: user
**Date**: 2026-05-13
**Final verdict**: NEEDS-FIXES

**Notes**: Triage reconciles both passes — first Critic (`critique.md`) + meta-Critic (`critique-review.md`, dual-review verdict EXTEND). All 7 first-Critic findings ratified VALID at filed severity per meta-Critic confirmation. 1 missed Major finding (**M-add-1**) added per meta-Critic dual review. B1 evidence count corrected: actual 17 EPG-1 occurrences in mission-brief (meta-Critic verified; Critic's "22" was overcounted but directionally correct; corrected number used in rationale). Final verdict NEEDS-FIXES because M1 + M-add-1 are ACCEPTED-PENDING (Builder applies at /build-slice).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Global rename mission-brief EPG-1 → EPGD-1 (17 occurrences, including test function names `_epg_1_` → `_epgd_1_`) + removed 3 "candidate" / "or final" hedge phrasings on lines 12, 19, 60 (rule ID was locked at /design-slice; mission-brief is the artifact that drifted). Verified post-fix: 0 EPG-1 / 18 EPGD-1. Meta-Critic VALID at Blocker severity (Wiegers Type-A spec defect). |
| M1 | Major | ACCEPTED-PENDING | At /build-slice: tighten slice-011 `_names_both_sub_modes` end_anchor from `### Bonus: weak graph edges` to `Entry-pin-vs-PMI-1-gate semantics conflation` (scope body to ONLY RSAD-1 sub-clause) + add symmetric NEW slice-013 test `test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes`. TF-1 plan grows 8 → 10 rows. Meta-Critic VALID at Major severity (Hendrickson body-bound discipline). |
| M-add-1 | Major | ACCEPTED-PENDING | At /build-slice: extend M1's fix symmetrically to sibling test `_cites_at_least_two_cross_slice_anchors` at test_critique_agent.py:209-241 (same body-bound defect; M1 substring leaks into sc_count regression-guard). Tighten that test's end_anchor identically + add slice-013 symmetric test `test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors` (cross-slice strict-both `["slice-011", "slice-012"]`, sub-class anchors per M2 formalization). TF-1 plan grows 10 → 12 rows. Meta-Critic finding missed by first Critic (single-slice pattern-blindness — defect class found on one instance but not generalized via grep across siblings with identical anchors). Calibration observation: candidate Dim 9 sub-class refinement at /critic-calibrate slice-014. |
| M2 | Major | ACCEPTED-FIXED | Formalized anchor lists in design.md "What's new" with strict-both `["slice-011", "slice-012"]` + ≥2-of-4 `["Phase 1b INSERT", "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]`. Propagated to mission-brief AC #2 + verification plan row 2. Meta-Critic VALID at Major severity (Newman contract-gap). |
| M3 | Major | ACCEPTED-FIXED | Updated mission-brief AC #4: corrected "N=2 surfaces (in-repo + installed entry title)" → "N=3 surfaces (agents/critique.md Dim 9 7th sub-clause title + in-repo entry + installed entry)" per slice-011 RSAD-1 3-surface precedent. N-surface discipline lineage: 3-surface shape ratchets to N=2 instances stable at slice-013 (RSAD-1 + EPGD-1). Meta-Critic VALID at Major severity (Wiegers numerical-spec drift). |
| m1 | Minor | ACCEPTED-FIXED | Cosmetic rephrase of ADR-012 L40: clarified that `Recursive self-application discipline` title lives at L168; L172 is close of sub-clause body. Meta-Critic VALID. |
| m2 | Minor | ACCEPTED-FIXED | Cosmetic accuracy fix at ADR-012 L42 + L55 + L89: changed "N=2 stable" → "N=2 ratchets pending empirical validation at /build-slice + /reflect" per slice-011 precedent. Meta-Critic VALID. |
| m3 | Minor | ACCEPTED-FIXED | Folded into B1's global rename sweep at mission-brief line 60: removed "(EPG-1 or final)" parenthetical hedge. Meta-Critic VALID. |
