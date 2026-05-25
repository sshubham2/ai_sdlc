# Design: Slice 024 refine-dim-9-with-fix-block-completeness-sub-clause

**Date**: 2026-05-15
**Mode**: Standard

## What's new

- `agents/critique.md` Dim 9 gains a **10th sub-clause** titled `Fix-block-completeness discipline` between existing sub-clause 9 (`Runtime-prerequisite completeness on proposed fixes`) and `### Bonus: weak graph edges`. Body names two sub-modes: (a) Original-draft cross-file consistency at first-Critic /critique time; (b) Post-ACCEPTED-FIXED sibling-sweep at meta-Critic /critique-review time. Cross-references existing `Tooling-doc-vs-implementation parity` sub-clause's design.md-mechanical-tables-vs-canonical-inventory body (i.e., CCC-1 v1.1, slice-009) as the EXTERNAL-inventory sibling, and existing `Runtime-prerequisite completeness on proposed fixes` sub-clause (i.e., RPCD-1, slice-016) as the structural-runtime sibling — cross-references cite by **canonical title strings** (not ordinal position), so `test_critique_dim_9_cross_references_resolve` can verify resolution. Forward-synced to installed copy per CAD-1 byte-equality.
- `methodology-changelog.md` gains v0.38.0 entry codifying rule `FBCD-1: Fix-block-completeness discipline` with both sub-modes ((a) Original-draft cross-file consistency + (b) Post-ACCEPTED-FIXED sibling-sweep) — mirrors RSAD-1 (v0.26.0) / EPGD-1 (v0.28.0) / SCPD-1 (v0.30.0) / RPCD-1 (v0.31.0) entry shape including substantive canonical phrase pinned across N=3 surfaces + cross-slice anchors (slice-020 / slice-021 / slice-022 / slice-023) + Limitations note (-D suffix convention; no audit-enforced gate).
- `architecture/decisions/ADR-022-fbcd-1-fix-block-completeness-discipline.md` (NEW file) — reversibility `cheap` with magnitude-of-revert justification ~14-16 sites, same class as ADR-010 / ADR-012 / ADR-014 / ADR-015. Empirical basis: **N=10 cumulative cross-instances across 4 distinct slices** (slice-020 N=1 + slice-021 N=3 + slice-022 N=2 + slice-023 N=4 per slice-021/022/023 critique-review.md M-add-* enumeration).
- `tests/methodology/test_critique_agent.py` modifications:
  - **PMI-1 structural-invariant supersession**: `test_critique_dim_9_lists_nine_sub_clauses` (line 115) → `test_critique_dim_9_lists_ten_sub_clauses`; canonical-literal assertion list bumped from 9 sub-clause titles to 10 (appends `"Fix-block-completeness discipline"`). N=4 → **N=5 cumulative** post-codification (slice-011 N=1 `_lists_five` → `_lists_six` + slice-013 N=2 `_lists_six` → `_lists_seven` + slice-015 N=3 `_lists_seven` → `_lists_eight` + slice-016 N=4 `_lists_eight` → `_lists_nine` + slice-024 N=5 `_lists_nine` → `_lists_ten`).
  - NEW body-bound test `test_critique_dim_9_fix_block_completeness_sub_clause_present` — **bare-substring pin** (matches slice-015 SCPD-1 + slice-016 RPCD-1 `_sub_clause_present` semantic): `assert "Fix-block-completeness discipline" in CRITIQUE`.
  - NEW body-bound test `test_critique_dim_9_fix_block_completeness_location_pinned` — **scoped-find pin** between `start_anchor = "Runtime-prerequisite completeness on proposed fixes"` (the PREVIOUS sub-clause title — FBCD-1 follows RPCD-1) and `end_anchor = "### Bonus: weak graph edges"`. Defends against future Dim 9 restructuring drifting FBCD-1 out of Dim 9. Completes the N=5 stable `_sub_clause_present` + `_location_pinned` duality post-slice-024.
  - NEW body-bound test `test_critique_dim_9_fix_block_completeness_names_both_sub_modes` — pins sub-modes `(a)` Original-draft + `(b)` Post-ACCEPTED-FIXED canonical literals (matches slice-011 RSAD-1 + slice-013 EPGD-1 + slice-015 SCPD-1 `_names_both_sub_modes` body shape — two sub-modes given FBCD-1's N=4-distinct-slice / N=10-cumulative-cross-instance evidence base, not three).
  - NEW body-bound test `test_critique_dim_9_fix_block_completeness_paragraph_cites_slice_020_021_022_023` — pins **strict-4-of-4 cross-slice anchors** `["slice-020", "slice-021", "slice-022", "slice-023"]`. Strict-four (not strict-three like slice-016 RPCD-1) reflects FBCD-1's N=4-distinct-slice evidence base (one anchor per distinct slice).
  - NEW body-bound test `test_critique_dim_9_fix_block_completeness_cites_substantive_discipline_anchors` — pins ≥3-of-4 substantive-discipline anchor tuple from canonical-body literal-substring set `["ACCEPTED-FIXED", "sibling", "mission-brief", "fix-block"]` (hyphenated to match the dominant rendering `fix-block-completeness`; all 4 expected present at slice-024 FBCD-1 body authoring).
  - End_anchor **tighten Edits** on the **three slice-016 RPCD-1 body-bound tests** (mirrors slice-016 Phase 1e tighten precedent applied to slice-015 SCPD-1 body-bound tests — generic recurrence N=3 → **N=4 stable** post-slice-024):
    - `test_critique_dim_9_runtime_prerequisite_completeness_names_three_sub_modes` (L708) → end_anchor `Fix-block-completeness discipline`
    - `test_critique_dim_9_runtime_prerequisite_completeness_paragraph_cites_slice_013_014_015` (L748) → end_anchor `Fix-block-completeness discipline`
    - `test_critique_dim_9_runtime_prerequisite_completeness_cites_substantive_discipline_anchors` (L791) → end_anchor `Fix-block-completeness discipline`
  - The **four** `_location_pinned` siblings (`_recursive_self_application_location_pinned` L173 RSAD-1, `_entry_pin_vs_pmi_1_gate_location_pinned` L304 EPGD-1, `_shippability_catalog_propagation_location_pinned` L492 SCPD-1, `_runtime_prerequisite_completeness_location_pinned` L656 RPCD-1) are **NOT tightened** — their `### Bonus: weak graph edges` end_anchor is structurally load-bearing per slice-013 + slice-015 + slice-016 precedent (verifies the sub-clause title falls BEFORE the H3).
- `tests/methodology/test_methodology_changelog.py` modifications:
  - NEW SECTION header `# --- Slice-024 / FBCD-1 entry pinning ---` (placed after the existing `# --- Slice-023 / UTF8-STDOUT-1 entry pinning ---` section — Phase 1b INSERT per EPGD-1 narrow-scope discipline — applied to test_methodology_changelog.py for entry-pin INSERT, NOT to test_critique_agent.py)
  - NEW entry-pin function `test_v_0_38_0_fbcd_1_entry_present_in_repo_and_installed` — bidirectional check (in-repo + installed) for v0.38.0 entry with `FBCD-1` rule-ID + canonical phrase `Fix-block-completeness discipline`
  - NEW entry-pin function `test_v_0_38_0_fbcd_1_names_both_sub_modes` — bidirectional check for (a) Original-draft + (b) Post-ACCEPTED-FIXED sub-mode anchors
  - NEW entry-pin function `test_v_0_38_0_fbcd_1_cites_slice_020_021_022_023` — bidirectional check for strict-4-of-4 cross-slice anchors
  - NEW ADR-pin function `test_adr_022_exists_and_names_fbcd_1_canonical_phrase` — mirrors `test_adr_015_exists_and_names_rpcd_1_canonical_phrase` (slice-016 row 16 precedent)
  - PMI-1 v1.1 invariant gate body (`test_plugin_yaml_version_matches_version_file_invariant`) **UNCHANGED** — empirical retirement-proof N=9 → **N=10 stable** (slice-007 introduction → slice-008..023 = 9 atomic bumps → slice-024 = 10th atomic bump without gate-body modification).
- `plugin.yaml`, `VERSION`, `ai-sdlc-VERSION` atomic version bump 0.37.0 → 0.38.0 (PMI-1 v1.1 — single atomic commit; gate continues to PASS without modification).
- `architecture/shippability.md` row 24 added for slice-024 critical-path commands (mirrors slice-016 row 16 / slice-023 row 23 structure — 10 pytest invocations + critique-agent drift-audit + PMI-1 invariant gate).
- **SCPD-1 proactive-application** mode propagation: scan `architecture/shippability.md` for ALL rows referencing `_lists_nine_sub_clauses`. Each consumer row's pytest command updated in-line `_lists_nine_sub_clauses` → `_lists_ten_sub_clauses` in the same /build-slice block BEFORE /validate-slice catalog run. Empirical scan target: rows referencing `_lists_nine` (count determined at /build-slice Phase 5 empirical scan; expected ≥1 based on slice-016 precedent which propagated 4 rows).

## What's reused

- [[components/agents-critique]] — Dim 9 9-sub-clause body (current state); CAD-1 byte-equal verified at slice-024 start (sha256 captured at Phase 1g pre-edit). Slice-024 IS the slice that adds the 10th sub-clause (distinct from slice-016 where the 9th sub-clause was added pre-slice via /critic-calibrate apply step — slice-024 has no prior /critic-calibrate apply step; the agent edit is part of THIS slice's deliverable).
- `tools/critique_agent_drift_audit.py` — CAD-1 byte-equality check; reused as mid-slice smoke gate + pre-finish gate
- `tools/test_first_audit.py` — TF-1 audit (`_ALLOWED_STATUSES` allowlist: `{"PENDING", "WRITTEN-FAILING", "PASSING"}` per slice-015 M-add-1 + slice-016 Audit 2 confirmation — unchanged at slice-024)
- `tools/plugin_manifest_audit.py` — PMI-1 audit (extended at slice-023 with leading-underscore filter for `_stdout.py` per B2 ACCEPTED-PENDING)
- `tools/risk_register_audit.py` — RR-1 audit (no risk-register edits in this slice)
- `tools/utf8_stdout_audit.py` — UTF8-STDOUT-1 audit (slice-023; no new audit tools introduced this slice → vacuously satisfied)
- `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` — mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern N=8 → **N=9 stable** post-slice-024
- `tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant` — PMI-1 v1.1 invariant gate; body unchanged for atomic 0.37.0 → 0.38.0 bump
- [[decisions/ADR-005]] — original CCC-1 Dim 9 9-dimension structure (parent ADR for all Dim 9 sub-class refinements)
- [[decisions/ADR-006]] — CAD-1 hybrid (prose + audit) for byte-equality
- [[decisions/ADR-008]] — CCC-1 v1.1 (Dim 9 sub-clause 2 — design.md tables vs canonical inventory; FBCD-1's EXTERNAL-inventory sibling for cross-reference)
- [[decisions/ADR-010]] — RSAD-1 codification precedent (reversibility=cheap with magnitude justification)
- [[decisions/ADR-012]] — EPGD-1 codification precedent
- [[decisions/ADR-013]] — PMI-1 v1.1 version-agnostic gate refactor
- [[decisions/ADR-014]] — SCPD-1 codification precedent
- [[decisions/ADR-015]] — RPCD-1 codification precedent (**closest structural template** — multi-sub-mode codification, 3-surface schema-pin; FBCD-1's structural-runtime sibling for cross-reference)
- [[architecture/critic-calibration-log]] — calibration runs through 2026-05-13 (post-slice-015 full window). slice-024 is the **FIRST codification slice without a prior dedicated /critic-calibrate run authorizing its codification** — empirically applies project's N=2-cross-slice proactive codification convention (per EPGD-1 / SCPD-1 precedent). The empirical basis is slice-023 reflection's explicit Pattern 3 + Pattern 4 promotion-eligibility tag. Documented at ADR-022 rationale.
- Methodology rules referenced: **TF-1** (v0.13.0), **PMI-1 v1.1** (v0.29.0), **CCC-1 v1.1** (v0.24.0), **RSAD-1** (v0.26.0), **EPGD-1** (v0.28.0), **SCPD-1** (v0.30.0), **RPCD-1** (v0.31.0), **TPHD-1** (v0.32.0), **LAYER-EVID-1** (v0.33.0), **BFRD-1** (v0.34.0), **BRANCH-1** (v0.35.0), **ADR-020 PR-aware /commit-slice modes** (v0.36.0), **UTF8-STDOUT-1** (v0.37.0), **CAD-1** (v0.22.0), **META-1** (methodology versioning + changelog; carries atomicity discipline), **META-2** (methodology self-test harness; provides bidirectional-sha256 byte-equality validation), **META-3** (named-subagent authoring guide + frontmatter conformance), **MCT-1** (v0.25.0), **BC-1 v1.3** (v0.27.0)

## Components touched

### `agents/critique.md`
- **Responsibility**: Adversarial Critic agent prompt; defines 9 review dimensions including Dim 9 cross-cutting conformance with N sub-clauses (current N=9 → N=10 post-slice-024).
- **Lives at**: `<HOME>\ai_sdlc\agents\critique.md` (canonical, in-repo) and `<HOME>\.claude\agents\critique.md` (installed runtime copy)
- **Key interactions**: invoked by `/critique` skill via Agent tool; byte-equality enforced by CAD-1 audit
- **Slice-024 modification**: Phase 1g inserts NEW 10th sub-clause body BETWEEN existing sub-clause 9 (RPCD-1 body ends around line 186 currently) AND `### Bonus: weak graph edges` (line 188 currently). Forward-synced at Phase 4 (Phase 3 forward-syncs methodology-changelog; Phase 4 forward-syncs critique.md AFTER methodology-changelog sync so CAD-1 + entry-pin tests pass together).

### `architecture/methodology-changelog.md`
- **Responsibility**: Versioned changelog of methodology rules; canonical source for what disciplines apply
- **Lives at**: `<HOME>\ai_sdlc\methodology-changelog.md` (in-repo) and `<HOME>\.claude\methodology-changelog.md` (installed); bidirectional byte-equality enforced by `test_v_0_NN_0_*_entry_present_in_repo_and_installed` family
- **Slice-024 modification**: append v0.38.0 entry with FBCD-1 definition (in-repo only at Phase 1a; forward-sync at Phase 3)

### `tests/methodology/test_critique_agent.py`
- **Responsibility**: Pin-tests for `agents/critique.md` structural invariants (9 dimensions + N Dim 9 sub-clauses + cross-references + sub-clause bodies)
- **Lives at**: `<HOME>\ai_sdlc\tests\methodology\test_critique_agent.py`
- **Key interactions**: invoked by pytest at /validate-slice; rows in `architecture/shippability.md` reference specific tests by qualified name
- **Slice-024 modifications**: PMI-1 structural-invariant supersession (1 rename + canonical-literal bump 9 → 10) + 5 NEW body-bound tests (sub-clause-present + location-pinned + names-both-sub-modes + cites-slice-020-021-022-023 + cites-substantive-discipline-anchors) + 3 end_anchor-tighten Edits (slice-016 RPCD-1 body-bound tests L708 / L748 / L791)

### `tests/methodology/test_methodology_changelog.py`
- **Responsibility**: Pin-tests for `methodology-changelog.md` byte-equality + version invariants + entry-pin per slice
- **Lives at**: `<HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py`
- **Key interactions**: invoked by pytest at /validate-slice; PMI-1 v1.1 invariant gate `test_plugin_yaml_version_matches_version_file_invariant` is version-agnostic
- **Slice-024 modifications**: NEW SECTION header `# --- Slice-024 / FBCD-1 entry pinning ---` + 4 NEW test functions (entry-pin present + names-both-sub-modes + cites-cross-slice + ADR-pin) under EPGD-1 narrow-scope discipline; 0 of 17 prior `_entry_present_in_repo_and_installed`-family functions touched (16 minor versions v0.22.0..v0.37.0 + 1 extra at v0.29.0 per slice-014 (a)↔(b) duality = 17 prior entry-pin functions); PMI-1 invariant gate body UNCHANGED. (Note: the mission-brief.md L126 "16 → 17 stable" count uses the strict v0.NN-major-version count, not the function-instance count — both reconcile against `grep -c "^def test_v_0_.*_entry_present_in_repo_and_installed" tests/methodology/test_methodology_changelog.py` empirically.)

### `plugin.yaml` + `VERSION` + `ai-sdlc-VERSION`
- **Responsibility**: Plugin version triple; atomic bump enforced by PMI-1 v1.1 invariant gate
- **Lives at**: `plugin.yaml` (repo root), `VERSION` (repo root), `ai-sdlc-VERSION` (repo root)
- **Slice-024 modification**: 0.37.0 → 0.38.0 in single atomic commit (Phase 2)

### `architecture/shippability.md`
- **Responsibility**: Catalog of critical-path pytest commands per slice; run at /validate-slice Step 5.5 as final shipping gate
- **Lives at**: `<HOME>\ai_sdlc\architecture\shippability.md`
- **Key interactions**: each row pins specific test functions by qualified name; SCPD-1 governs propagation when test function names are superseded
- **Slice-024 modifications**: (a) SCPD-1 PROACTIVE: scan for rows referencing `_lists_nine_sub_clauses`, propagate `_lists_nine_sub_clauses` → `_lists_ten_sub_clauses` in same /build-slice block at Phase 5 BEFORE /validate-slice catalog run; (b) NEW row 24 with slice-024 critical-path commands (mirrors slice-016 row 16 + slice-023 row 23 structure — ≥10 pytest commands including PMI-1 invariant gate + ADR-pin + critique-agent drift-audit)

### `architecture/decisions/ADR-022-fbcd-1-fix-block-completeness-discipline.md` (NEW)
- **Responsibility**: Decision record for FBCD-1 codification rationale (reversibility=cheap with magnitude justification, supersedes=null)
- **Lives at**: `architecture/decisions/ADR-022-fbcd-1-fix-block-completeness-discipline.md`
- **Slice-024 creation**: Phase 1f authors the ADR file with required sections (Context, Options considered, Decision, Consequences, Reversibility, Cost summary); canonical phrase `Fix-block-completeness discipline` pinned

## Contracts added or changed

None. Slice introduces no API contracts, endpoints, events, or external integrations. Methodology codification only.

## Data model deltas

None. No schema changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Slice introduces **no new modules** — only edits to existing files (agents/critique.md, methodology-changelog, test files, plugin metadata, shippability catalog) and one NEW ADR file (which is documentation, not a runnable module). The audit treats zero-row matrices as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero rows — header + separator only, audit clean.)

## Decisions made (ADRs)

- [[ADR-022]] — Promote fix-block-completeness discipline (FBCD-1) to `agents/critique.md` Dim 9 10th sub-clause — reversibility: **cheap** (with magnitude-of-revert justification ~14-16 sites; same class as ADR-010 / ADR-012 / ADR-014 / ADR-015)

## Authorization model for this slice

N/A — internal methodology codification; no user-facing actions, no auth surface, no role gates.

## Error model for this slice

N/A — no error codes introduced. Methodology-changelog parsing relies on existing pytest-based assertion failures. Standard Python exception model.

## Phase plan

Adapted from slice-016 phase structure with critique.md edit (Phase 1g) added (slice-016 had critique.md pre-edited via /critic-calibrate apply step; slice-024 has no such pre-step, so the critique.md edit is part of this slice's own phase plan). SCPD-1 proactive-application coordinated at Phase 5.

| # | Phase | Files touched | Pre-conditions | Post-conditions |
|---|-------|---------------|----------------|-----------------|
| **1a** | Append methodology-changelog v0.38.0 entry (in-repo only) | `methodology-changelog.md` | v0.37.0 entry is current top entry | v0.38.0 entry inserted at top of changelog body; FBCD-1 rule-ID + canonical phrase + 2 sub-modes + cross-slice anchors `slice-020/021/022/023` + ADR-022 forward-ref present |
| **1b** | Entry-pin INSERT under NEW SECTION header (test_methodology_changelog.py) | `tests/methodology/test_methodology_changelog.py` | Phase 1a complete; v0.37.0 UTF8-STDOUT-1 entry-pin section is the last existing SECTION | NEW SECTION header `# --- Slice-024 / FBCD-1 entry pinning ---` + 4 NEW test functions (entry-pin present + names-both-sub-modes + cites-cross-slice + ADR-pin) per EPGD-1 narrow-scope discipline; 0 of 16 prior entry-pin functions (v0.22.0..v0.37.0) touched; PMI-1 invariant gate body unchanged |
| **1c** | PMI-1 structural-invariant supersession in test_critique_agent.py | `tests/methodology/test_critique_agent.py` | Phase 1b complete; agents/critique.md still has 9 Dim 9 sub-clauses at this point (Phase 1g hasn't run yet — test will be WRITTEN-FAILING) | `_lists_nine_sub_clauses` → `_lists_ten_sub_clauses` (function rename + canonical-literal list bumped 9 → 10; appends `"Fix-block-completeness discipline"`); function comment updated to reference slice-024 supersession. Test status: WRITTEN-FAILING until Phase 1g lands. |
| **1d** | NEW body-bound tests in test_critique_agent.py | `tests/methodology/test_critique_agent.py` | Phase 1c complete | **5 NEW test functions** appended after Phase 1c's renamed test: (1) `_sub_clause_present` bare-substring, (2) `_location_pinned` scoped-find with `Runtime-prerequisite completeness on proposed fixes` start_anchor + `### Bonus: weak graph edges` end_anchor, (3) `_names_both_sub_modes` (sub-modes `(a)` Original-draft + `(b)` Post-ACCEPTED-FIXED), (4) `_paragraph_cites_slice_020_021_022_023` (strict-4-of-4 cross-slice anchors), (5) `_cites_substantive_discipline_anchors` (≥3-of-4 anchors `["ACCEPTED-FIXED", "sibling", "mission-brief", "fix-block"]` — hyphenated to match the dominant rendering `fix-block-completeness`). All 5 status: WRITTEN-FAILING until Phase 1g lands. |
| **1e** | End_anchor tighten Edits | `tests/methodology/test_critique_agent.py` | Phase 1d complete | THREE slice-016 RPCD-1 body-bound tests' end_anchors tightened from `### Bonus: weak graph edges` → `Fix-block-completeness discipline`: `_runtime_prerequisite_completeness_names_three_sub_modes` (L708), `_runtime_prerequisite_completeness_paragraph_cites_slice_013_014_015` (L748), `_runtime_prerequisite_completeness_cites_substantive_discipline_anchors` (L791). The FOUR `_location_pinned` siblings (L173 RSAD-1, L304 EPGD-1, L492 SCPD-1, L656 RPCD-1) are NOT touched — their `### Bonus:` end_anchor is structurally load-bearing. Function comments updated with slice-024 /critique-disposition-aware tighten provenance (mirrors slice-013/015/016 M1 convention). Tests stay PASSING throughout the tighten (end_anchor change is forward-compatible — the new end_anchor `Fix-block-completeness discipline` appears AFTER `Runtime-prerequisite completeness on proposed fixes` in the file, post-Phase 1g). |
| **1f** | ADR-022 written | `architecture/decisions/ADR-022-fbcd-1-fix-block-completeness-discipline.md` | Phases 1a-1e complete | ADR-022 file exists with required sections (Status, Context, Options considered, Decision, Consequences, Reversibility, Cost summary); canonical phrase `Fix-block-completeness discipline` pinned |
| **1g** | Insert NEW 10th sub-clause in critique.md (in-repo only) | `agents/critique.md` | Phases 1a-1f complete; reading critique.md to identify insertion point (after current sub-clause 9 RPCD-1 body ending at line ~186; before `### Bonus: weak graph edges` H3) | NEW 10th sub-clause body inserted with: title `Fix-block-completeness discipline`; sub-mode (a) Original-draft cross-file consistency + sub-mode (b) Post-ACCEPTED-FIXED sibling-sweep; cross-slice anchors `slice-020/021/022/023`; **cross-references by canonical title strings** (not ordinal position) — `Tooling-doc-vs-implementation parity sub-clause's design.md-mechanical-tables-vs-canonical-inventory body, i.e., CCC-1 v1.1` + `Runtime-prerequisite completeness on proposed fixes sub-clause, i.e., RPCD-1`; substantive anchors `ACCEPTED-FIXED` + `sibling` + `mission-brief` + `fix-block` (hyphenated form, will match the dominant rendering `fix-block-completeness`); rule-ID `FBCD-1` literal pinned; **all 6 Phase 1c/1d critique-agent tests transition WRITTEN-FAILING → PASSING** |
| **2** | Atomic version bump | `plugin.yaml`, `VERSION`, `ai-sdlc-VERSION` | Phases 1a-1g complete | All 3 files read 0.38.0 in single atomic commit; PMI-1 v1.1 invariant gate continues to PASS without test-body modification (empirical retirement-proof N=9 → **N=10 stable**) |
| **3** | Forward-sync methodology-changelog.md to installed | `<HOME>\.claude\methodology-changelog.md` | Phase 2 complete | Installed copy byte-equal to in-repo (sha256 captured); `test_v_0_38_0_fbcd_1_entry_present_in_repo_and_installed` PASSES (was WRITTEN-FAILING after Phase 1b) |
| **4** | Forward-sync agents/critique.md to installed | `<HOME>\.claude\agents\critique.md` | Phase 3 complete | Installed copy byte-equal to in-repo (sha256 captured); `python -m tools.critique_agent_drift_audit --repo-root .` exit 0; existing `test_in_repo_and_installed_critique_agent_are_content_equal` PASSES (mini-CAD-1 row 3 N=8 → **N=9 stable** transition) |
| **5** | SCPD-1 proactive scan + propagation + new row 24 | `architecture/shippability.md` | Phase 4 complete | (a) Empirical scan: grep `_lists_nine_sub_clauses` in `architecture/shippability.md`; (b) all consumer rows' pytest commands propagated `_lists_nine_sub_clauses` → `_lists_ten_sub_clauses` in same /build-slice block BEFORE /validate-slice catalog run; (c) NEW row 24 added with slice-024 critical-path pytest commands mirroring slice-016 row 16 + slice-023 row 23 structure; SCPD-1 self-application N=2 → **N=3 stable** post-codification (slice-015 first canonical reference + slice-016 second + slice-024 third — confirms SCPD-1 N=3 cross-slice stability post-codification) |
| **6** | Pre-finish gates | (audit-only) | Phase 5 complete | `python -m tools.test_first_audit --strict-pre-finish` exit 0; `python -m tools.critique_agent_drift_audit` exit 0; `python -m tools.plugin_manifest_audit` exit 0; `python -m tools.risk_register_audit architecture/risk-register.md` exit 0; `python -m tools.utf8_stdout_audit` exit 0; `python -m tools.branch_workflow_audit` exit 0; `/drift-check` clean; mid-slice smoke re-run clean; methodology-changelog + critique.md byte-equality re-verified at slice end (sha256 captured) |

## Design-time audits (RSAD-1 self-application + concrete N=N stability targets)

Per RSAD-1 design-time discipline + slice-013/014/015/016 precedent N=6/7/8 audits.

### Audit 1 — FBCD-1 self-application sub-mode (a) Original-draft cross-file consistency on slice-024's own mission-brief + design + ADR-022

**Question**: Does any claim in slice-024's own mission-brief.md + design.md + ADR-022 + critique.md edit drift across files?

**Empirical scan**:
- **Cumulative-count claim**: mission-brief.md L5 says "N=10 cumulative cross-instances across 4 distinct slices"; design.md MUST say the same N count + same distinct-slice count. ADR-022 Context section MUST say the same. (Per /critique B1 fix-block: N=9 → N=10 corrected at 11-site sweep; slice-021 cite from N=2 → N=3.)
- **Sub-mode names**: mission-brief.md says "(a) Original-draft cross-file consistency + (b) Post-ACCEPTED-FIXED sibling-sweep"; design.md "What's new" L1 + Phase 1g + Audit X MUST say identical strings. ADR-022 Decision section MUST say identical strings. critique.md edit body MUST contain both literal sub-mode names. Tests at Phase 1d `_names_both_sub_modes` MUST pin canonical strings literally.
- **Rule-ID literal**: `FBCD-1` literal pinned across mission-brief.md + design.md + ADR-022 + critique.md + methodology-changelog v0.38.0 + test_methodology_changelog.py + test_critique_agent.py + shippability.md row 24 — **strict-8-of-8 surface sites** (semantically distinct from the test pin's **strict-4-of-4 cross-slice anchors** at Phase 1d `_paragraph_cites_slice_020_021_022_023`; the two "strict-N-of-N" semantics are independent — one counts surface sites for cross-file consistency, the other counts cross-slice anchors within the test body). Any divergence (e.g., `FBC-D-1`, `FBCD1`, `Fix-block-completeness-discipline-1`) at any surface fails.
- **Cross-slice anchors**: `slice-020 / slice-021 / slice-022 / slice-023` — **strict-4-of-4 cross-slice anchors at test pin** (the test substantive set) PLUS **strict-5-of-5 surface sites for cross-file consistency** across mission-brief.md + design.md + ADR-022 + critique.md edit + changelog v0.38.0. Any omission/typo at any surface fails.

**Empirical PASS evidence**: At slice-024 /design-slice authoring time, design.md sentence-level review against mission-brief.md confirms all claims aligned. ADR-022 Phase 1f authoring will mirror these. FBCD-1 sub-mode (a) self-application N=1 catch on slice's own draft EXPECTED at /critique time per recursive-self-application closure observed at slice-009..023 (N=33 cumulative HWM at slice-021).

### Audit 2 — FBCD-1 self-application sub-mode (b) Post-ACCEPTED-FIXED sibling-sweep on Builder's own hypothetical fix scenarios

**Question**: If /critique produces a Blocker like "rename FBCD-1 to FBC-1 in mission-brief.md L5", does fix-block-completeness sibling-sweep enumerate ALL N=8 surface sites for propagation?

**Pre-emption**: This is exactly the class FBCD-1 codifies. At /critique-disposition time, every ACCEPTED-FIXED B/M Builder applies MUST trigger an empirical grep for the same anchor substring across all slice-authoring files. Documented at Audit 1 above with N=8 surface count. Sub-mode (b) self-application N=1 catch on slice's own ACCEPTED-FIXED sweeps EXPECTED at /critique-review time per slice-020/021/022/023 cumulative N=10 evidence base (the very evidence base FBCD-1 codifies — the slice that codifies the rule WILL EMPIRICALLY EXHIBIT cases of the rule on its own drafts). **Empirical confirmation**: this very /critique surfaced 11 catches (3 Blockers + 7 Majors + 1 actionable Minor) on the slice's own drafts; the ACCEPTED-FIXED sweep applied as one coordinated 11-site fix-block at /critique-disposition triage (B1's 11-site N count sweep) demonstrates sub-mode (b) in action.

### Audit 3 — EPGD-1 self-application structural separation

**Question**: Does Phase 1b's entry-pin INSERT preserve all 16 prior entry-pin functions (v0.22.0..v0.37.0 spans 16 minor versions; v0.29.0 carries 2 functions per slice-014 (a)↔(b) duality) and Phase 1c's structural-invariant supersession preserve the PMI-1 v1.1 invariant gate body?

**Evidence**: Phase 1b creates a NEW SECTION header `# --- Slice-024 / FBCD-1 entry pinning ---` placed AFTER the existing slice-023 UTF8-STDOUT-1 section. Phase 1c is a function-body Edit on `test_critique_dim_9_lists_nine_sub_clauses`'s containing module (`test_critique_agent.py`) — narrow-scoped to the function body + name; the 16 prior entry-pin functions live in `test_methodology_changelog.py` (different module), zero risk of accidental deletion. PMI-1 invariant gate `test_plugin_yaml_version_matches_version_file_invariant` is in `test_methodology_changelog.py` — different module, untouched. EPGD-1 self-application N=10 → **N=11 stable** post-slice-024. **PRE-EMPTED via cross-module separation.** PASS.

### Audit 4 — PMI-1 v1.1 version-agnostic invariant gate empirical retirement-proof

**Question**: Will the atomic version bump 0.37.0 → 0.38.0 in Phase 2 succeed with ZERO test body modification on `test_plugin_yaml_version_matches_version_file_invariant`?

**Evidence**: PMI-1 v1.1 (slice-014 ADR-013) refactored the gate to read `plugin.yaml.version` + `VERSION` and assert equality — no version literal in body. slice-015..023 = 9 atomic bumps without gate-body modification. slice-024 is the **10th cross-slice retirement-proof (N=9 → N=10 stable)**. Phase 2 atomic bump touches 3 files, gate body unchanged. PASS expected.

### Audit 5 — N-surface schema-pin canonical phrase across 3 surfaces

**Question**: Is canonical phrase `Fix-block-completeness discipline` pinned across 3 surfaces (in-repo methodology-changelog v0.38.0 + installed methodology-changelog v0.38.0 + ADR-022)?

**Evidence**: AC #1 (critique.md in-repo edit at Phase 1g) + AC #2 (CAD-1 byte-equal forward-sync at Phase 4) + AC #3 (in-repo methodology-changelog v0.38.0 at Phase 1a) + Phase 3 (forward-sync to installed) + ADR-022 Status section + Decision section (Phase 1f) jointly pin the phrase. N-surface schema-pin 4-instance pattern N=10 → **N=11 stable** post-codification (RSAD-1 + EPGD-1 + PMI-1 v1.1 + SCPD-1 + RPCD-1 + TPHD-1 + LAYER-EVID-1 + BFRD-1 + BRANCH-1 + UTF8-STDOUT-1 + FBCD-1).

### Audit 6 — End_anchor tighten completeness (generic methodology recurrence N=3 → N=4 stable)

**Question**: Have ALL body-bound tests currently using `### Bonus: weak graph edges` as end_anchor been identified for tightening to `Fix-block-completeness discipline`? (Excluding `_location_pinned` siblings whose `### Bonus:` end_anchor is structurally load-bearing per slice-013/015/016 precedent.)

**Empirical scan** (`grep -n 'end_anchor = "### Bonus: weak graph edges"' tests/methodology/test_critique_agent.py` returns hits):

| Line (approximate) | Containing function | Classification | Action |
|------|---------------------|----------------|--------|
| L173 | `test_critique_dim_9_recursive_self_application_location_pinned` (RSAD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L304 | `test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned` (EPGD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L492 | `test_critique_dim_9_shippability_catalog_propagation_location_pinned` (SCPD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L656 | `test_critique_dim_9_runtime_prerequisite_completeness_location_pinned` (RPCD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L708 | `test_critique_dim_9_runtime_prerequisite_completeness_names_three_sub_modes` (RPCD-1) | body-bound | **TIGHTEN at Phase 1e** |
| L748 | `test_critique_dim_9_runtime_prerequisite_completeness_paragraph_cites_slice_013_014_015` (RPCD-1) | body-bound | **TIGHTEN at Phase 1e** |
| L791 | `test_critique_dim_9_runtime_prerequisite_completeness_cites_substantive_discipline_anchors` (RPCD-1) | body-bound | **TIGHTEN at Phase 1e** |

**Result**: 3 of 7 queued for Phase 1e end_anchor tighten (the 3 slice-016 RPCD-1 body-bound tests). The 4 `_location_pinned` siblings stay at `### Bonus: weak graph edges` per slice-013/015/016 precedent (verified empirically — `### Bonus: weak graph edges` end_anchor is invariant load-bearing for location-pinned tests). Generic recurrence N=3 → **N=4 stable** post-codification at slice-024 (slice-013 tightened slice-011 body-bound; slice-015 tightened slice-013 body-bound; slice-016 tightened slice-015 body-bound; slice-024 tightens slice-016 body-bound — N=4 consecutive Dim 9 sub-clause codifications applying this discipline).

### Audit 7 — SCPD-1 proactive-application scan completeness (cross-Phase consumer-reference propagation)

**Question**: Have ALL consumer references to `_lists_nine_sub_clauses` been identified for propagation to `_lists_ten_sub_clauses` BEFORE /validate-slice catalog run?

**Empirical scan plan** (executed at Phase 5 of /build-slice, same Phase as the propagation Edit): grep `_lists_nine_sub_clauses` in `architecture/shippability.md`; enumerate ALL row numbers; apply propagation Edits in-line. **Expected count**: slice-016 propagated 4 rows (6/11/13/15); slice-024 expected similar — exact count determined at scan time.

**Result post-build**: SCPD-1 proactive-application self-application N=2 → **N=3 stable** post-codification (slice-015 first canonical reference + slice-016 second + slice-024 third).

### Audit 8 — TPHD-1 sub-mode (c) /critique-disposition-promised-test-not-enumerated-in-TF-1-plan pre-flight

**Question**: Does the TF-1 plan in mission-brief.md enumerate EVERY test whose addition will be required at /build-slice?

**Empirical scan**: mission-brief.md TF-1 plan has 13 rows. Each test function named must (a) appear in TF-1 plan AND (b) be implemented by /build-slice end (PASSING). Slice-023's TPHD-1 sub-mode (c) caught 3 dispositions promising tests that weren't in TF-1 plan; slice-024 pre-empts by enumerating ALL tests at /slice + /design-slice time.

**Mission-brief TF-1 plan enumeration vs design.md test additions**:
- AC #1 tests: 6 critique-agent prose-pin tests (`_lists_ten_sub_clauses` (renamed) + 5 body-bound) — design.md L23-26 mention same → CHECK ✓
- AC #2 tests: existing test_critique_agent_byte_equal_installed (re-run) — design.md L73 → CHECK ✓
- AC #3 tests: 3 changelog entry-pin tests + 1 PMI-1 atomic-bump invariant — design.md L29-32 → CHECK ✓
- AC #4 tests: 1 ADR-022 entry-pin test — design.md L33 → CHECK ✓
- AC #5 tests: row 24 inline Command cell executed via /validate-slice Step 5.5 catalog regression — design.md L34-35 → CHECK ✓ (NOTE: original draft cited a phantom `test_shippability_catalog.py` "structural tests"; corrected at /validate-slice — no such file exists, the catalog is validated by Step 5.5 command execution per slice-023 B4 precedent. This was an FBCD-1 sub-mode (a) miss BOTH Critics + the Builder's Audit 8 missed — recorded as a "Missed by Critic" for /reflect calibration.)

**Result**: TPHD-1 sub-mode (c) self-application was NOT fully clean — Audit 8's AC #5 row asserted a non-existent `test_shippability_catalog.py`; the first Critic's Audit 8 PASS and meta-Critic both missed this (the structural-invariant for shippability is Step 5.5 command execution, not a pytest). Corrected at /validate-slice. Empirical recursive-self-application closure: the slice codifying FBCD-1 committed a further FBCD-1 sub-mode (a) cross-file citation drift (3 sites: TF-1 row 13 + Verification plan L56 + Audit 8 L221) that surfaced only at real validation — exactly the empirical anchor FBCD-1 predicts.

## Risk register impact

No new risks. R-1 (cwd-mismatch /diagnose), R-2 (no programmatic /diagnose warning test), R-3 (graphify symbol-resolution phantom edges) remain open/mitigating but untouched by this slice (out-of-scope per mission brief).

## Cost summary

- **Implementation**: ~45-60 min build + ~30 min Critic-stack + ~15 min validate (~1.5-2 hours total) — slightly higher than slice-016 due to critique.md edit added (Phase 1g; slice-016 had this pre-applied via /critic-calibrate apply step).
- **Reversibility**: **cheap** with magnitude-of-revert justification ~14-16 sites:
  - 1 methodology-changelog v0.38.0 entry (revert: delete entry)
  - 1 ADR-022 file (revert: delete file)
  - 1 entry-pin SECTION + 4 functions in test_methodology_changelog.py (revert: delete section)
  - 1 PMI-1 structural-invariant supersession in test_critique_agent.py (revert: rename back + canonical-literal list 10 → 9)
  - 5 NEW body-bound tests in test_critique_agent.py (revert: delete functions)
  - 3 end_anchor tighten Edits on slice-016 RPCD-1 tests (revert: change anchor back to `### Bonus: weak graph edges`)
  - 1 atomic version bump (revert: 0.38.0 → 0.37.0 in 3 files)
  - 1 forward-sync methodology-changelog to installed (revert: re-sync from prior in-repo state)
  - 1 forward-sync agents/critique.md to installed (revert: re-sync from prior in-repo state)
  - N shippability.md row propagations + 1 new row 24 (revert: rename back + delete row 24; N determined at /build-slice Phase 5 scan)
  - 1 agents/critique.md Dim 9 10th sub-clause body insertion (revert: delete sub-clause body in in-repo + forward-sync)
  Total ~14-16 sites; same magnitude class as ADR-010 / ADR-012 / ADR-014 / ADR-015.
- **Irreversibles**: archived /critique outputs from slice-024 onward that file findings under Dim 9's 10th sub-clause are filed permanently; in-context conditioning of the 9-dim-with-10-sub-clause Critic on its runs across slice-025+ accumulates. Same class as ADR-005 / ADR-008 / ADR-010 / ADR-012 / ADR-014 / ADR-015 irreversibles. Net-zero impossible after ~3-5 post-codification slices; refinement-over-revert is the canonical recovery path.

## Open questions

None. Mission brief + design captures all known scope. Critic invocation (mandatory per MCT-1 — slice touches `agents/critique.md` + `methodology-changelog.md` + new ADR + test files = In-house methodology surfaces trigger) at /critique + /critique-review (DR-1) provides the adversarial cross-check. Expected Critic-stack density per slice-023 reflection observation: N≥10 first-Critic + N≥3 meta-Critic on codification slice's drafts.

## Cumulative-Critic-influence note

This slice is the **FIRST codification slice authored without a prior dedicated /critic-calibrate run**. Project convention (per EPGD-1 + SCPD-1 precedent — both codified at N=2-cross-slice without a /critic-calibrate Proposal) supports this. The empirical basis is slice-023 reflection Patterns 3 + 4 + explicit `PROMOTION-ELIGIBLE for /critic-calibrate slice-024 Dim 9 sub-clause` tag. ADR-022 documents this convention application explicitly. A future /critic-calibrate run (post-slice-024 reflection) should ratify FBCD-1's effectiveness via the same effectiveness-check methodology as RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 — target = 0 fix-block-completeness MISSES across slices 25-35.
