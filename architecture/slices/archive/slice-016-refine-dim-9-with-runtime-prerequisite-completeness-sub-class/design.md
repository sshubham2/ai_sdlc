# Design: Slice 016 refine-dim-9-with-runtime-prerequisite-completeness-sub-class

**Date**: 2026-05-13
**Mode**: Standard

## What's new

- `architecture/methodology-changelog.md` gains v0.31.0 entry codifying rule `RPCD-1: Runtime-prerequisite completeness on proposed fixes` with the three named sub-modes ((a) NEW-symbol import-audit, (b) NEW-status/token allowlist-audit, (c) NEW-anchor sibling-grep) — mirrors RSAD-1 (v0.26.0) / EPGD-1 (v0.28.0) / SCPD-1 (v0.30.0) entry shape including substantive canonical phrase pinned across N=3 surfaces + cross-slice anchors + Limitations note (-D suffix convention; no audit-enforced gate)
- `architecture/decisions/ADR-015-promote-runtime-prerequisite-completeness-discipline-to-critique-dim-9-sub-clause.md` (NEW file) — reversibility `cheap` with magnitude-of-revert justification ~13-15 sites, same class as ADR-010/012/014
- `tests/methodology/test_critique_agent.py` modifications:
  - PMI-1 structural-invariant supersession: `test_critique_dim_9_lists_eight_sub_clauses` (line 115) → `test_critique_dim_9_lists_nine_sub_clauses`; canonical-literal assertion list bumped from 8 sub-clause titles to 9 (adds `"Runtime-prerequisite completeness on proposed fixes"`)
  - NEW body-bound test `test_critique_dim_9_runtime_prerequisite_completeness_sub_clause_present` — **bare-substring pin** (matches slice-015 SCPD-1 `_sub_clause_present` L463 semantic): `assert "Runtime-prerequisite completeness on proposed fixes" in CRITIQUE` — verifies the sub-clause title appears at least once in the file. Per slice-016 /critique-review M-add-1 ACCEPTED-FIXED clarification (slice-015 L463 precedent).
  - NEW body-bound test `test_critique_dim_9_runtime_prerequisite_completeness_location_pinned` — **scoped-find pin** (matches slice-015 SCPD-1 `_location_pinned` L475 semantic): scoped find between `start_anchor = "Shippability-catalog consumer-reference propagation"` (the PREVIOUS sub-clause title — RPCD-1 follows SCPD-1) and `end_anchor = "### Bonus: weak graph edges"`; assertion: `"Runtime-prerequisite completeness on proposed fixes"` is found in `CRITIQUE[start_idx:end_idx]`. Per slice-016 /critique-review M-add-1 ACCEPTED-FIXED — defends against future Dim 9 restructuring drifting RPCD-1 out of Dim 9 (e.g., into Dim 8 or the `### Bonus` section). Completes the N=3 stable `_sub_clause_present` + `_location_pinned` duality (slice-011 L146/158 + slice-013 L270/286 + slice-015 L463/475 + slice-016 → N=4 stable).
  - NEW body-bound test `test_critique_dim_9_runtime_prerequisite_completeness_names_three_sub_modes` — pins sub-modes `(a)` import + `(b)` `_ALLOWED_STATUSES` + `(c)` sibling-grep canonical literals
  - NEW body-bound test `test_critique_dim_9_runtime_prerequisite_completeness_paragraph_cites_slice_013_014_015` — pins strict-3-of-3 cross-slice anchors `["slice-013", "slice-014", "slice-015"]`
  - NEW body-bound test `test_critique_dim_9_runtime_prerequisite_completeness_cites_substantive_discipline_anchors` — pins ≥3-of-4 substantive-discipline anchor tuple from canonical-body literal-substring set `["import", "_ALLOWED_STATUSES", "sibling", "end_anchor"]` (all 4 verified present at slice-016 start sha256 `f34c967eaaa34413...`)
  - End_anchor tighten Edits on the **three slice-015 SCPD-1 body-bound tests** (per slice-016 /critique B1 ACCEPTED-FIXED):
    - `test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes` (end_anchor at L519) → `Runtime-prerequisite completeness on proposed fixes`
    - `test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014` (end_anchor at L554) → `Runtime-prerequisite completeness on proposed fixes`
    - `test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors` (end_anchor at L594) → `Runtime-prerequisite completeness on proposed fixes`
  - The three `_location_pinned` siblings (`_recursive_self_application_location_pinned` at L173, `_entry_pin_vs_pmi_1_gate_location_pinned` at L304, `_shippability_catalog_propagation_location_pinned` at L492) are **NOT tightened** — their `### Bonus: weak graph edges` end_anchor is structurally load-bearing (verifies the sub-clause title falls BEFORE the H3) per slice-013 + slice-015 precedent
- `tests/methodology/test_methodology_changelog.py` modifications:
  - NEW SECTION header `# --- Slice-016 / RPCD-1 entry pinning ---` (placed after the existing `# --- Slice-015 / SCPD-1 entry pinning ---` section — Phase 1b INSERT per EPGD-1 narrow-scope discipline)
  - NEW entry-pin function `test_v_0_31_0_rpcd_1_entry_present_in_repo_and_installed` — bidirectional check (in-repo + installed) for v0.31.0 entry with `RPCD-1` rule-ID + canonical phrase `Runtime-prerequisite completeness on proposed fixes`
  - NEW entry-pin function `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` — bidirectional check for (a)/(b)/(c) sub-mode anchors
  - NEW ADR-pin function `test_adr_015_exists_and_names_rpcd_1_canonical_phrase` — mirrors `test_adr_014_exists_and_names_scpd_1_canonical_phrase` (slice-015 row 15 precedent)
  - PMI-1 v1.1 invariant gate body (`test_plugin_yaml_version_matches_version_file_invariant`) **UNCHANGED** — empirical retirement-proof N=2 → N=3 stable
- `plugin.yaml`, `VERSION`, `ai-sdlc-VERSION` atomic version bump 0.30.0 → 0.31.0 (PMI-1 v1.1 — single atomic commit; gate continues to PASS without modification)
- `architecture/shippability.md` row 16 added for slice-016 critical-path commands (mirrors slice-015 row 15 structure)
- SCPD-1 proactive-application mode propagation: rows 6, 11, 13, 15 (4 consumer references to `_lists_eight_sub_clauses`) updated in-line to `_lists_nine_sub_clauses` in the same /build-slice block BEFORE /validate-slice catalog run

## What's reused

- [[components/agents-critique]] — Dim 9 9th sub-clause `Runtime-prerequisite completeness on proposed fixes` already edited live during /critic-calibrate 2026-05-13 (post-slice-015) Step 4 apply; CAD-1 byte-equal verified at slice-016 start (sha256 `f34c967eaaa34413...`). Slice-016 does NOT modify `agents/critique.md` content unless /critique fixes require it.
- `tools/critique_agent_drift_audit.py` — CAD-1 byte-equality check; reused as mid-slice smoke gate + pre-finish gate
- `tools/test_first_audit.py` — TF-1 audit including `_ALLOWED_STATUSES` allowlist (which now includes `WRITTEN-AS-EDIT` per slice-015 M-add-1 fix); reused for `--strict-pre-finish` gate
- `tools/risk_register_audit.py` — RR-1 audit (no risk-register edits in this slice)
- `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` — mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern N=7 → N=8 stable
- `tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant` — PMI-1 v1.1 invariant gate; body unchanged for atomic bump
- [[decisions/ADR-005]] — original CCC-1 Dim 9 9-dimension structure (parent ADR for all Dim 9 sub-class refinements)
- [[decisions/ADR-006]] — CAD-1 hybrid (prose + audit) for byte-equality
- [[decisions/ADR-010]] — RSAD-1 codification precedent (reversibility=cheap with magnitude justification)
- [[decisions/ADR-012]] — EPGD-1 codification precedent
- [[decisions/ADR-013]] — PMI-1 v1.1 version-agnostic gate refactor (enables zero-test-body-modification atomic version bump)
- [[decisions/ADR-014]] — SCPD-1 codification precedent (most-recent Dim 9 sub-clause codification — closest template)
- [[architecture/critic-calibration-log]] — 2026-05-13 (post-slice-015) run already records ACCEPTED proposal; slice-016 ratifies via methodology-changelog stack
- Methodology rules referenced: **TF-1** (test-first, v0.13.0), **PMI-1 v1.1** (v0.29.0), **CCC-1 v1.1** (v0.24.0), **RSAD-1** (v0.26.0), **EPGD-1** (v0.28.0), **SCPD-1** (v0.30.0), **CAD-1** (v0.22.0), **META-1** (atomicity), **META-2** (bidirectional sha256), **META-3** (validate-using-your-own-ship), **MCT-1** (v0.25.0), **BC-1 v1.3** (v0.27.0)

## Components touched

### `agents/critique.md` (modified pre-slice via /critic-calibrate apply step)
- **Responsibility**: Adversarial Critic agent prompt; defines 9 review dimensions including Dim 9 cross-cutting conformance with 9 sub-clauses
- **Lives at**: `<HOME>\ai_sdlc\agents\critique.md` (canonical, in-repo) and `<HOME>\.claude\agents\critique.md` (installed runtime copy)
- **Key interactions**: invoked by `/critique` skill via Agent tool; byte-equality enforced by CAD-1 audit
- **Slice-016 disposition**: Dim 9 9th sub-clause already live; no further modification expected at /build-slice unless /critique fix-prose introduces one (in which case end_anchor-tighten must be coordinated with that Edit)

### `architecture/methodology-changelog.md`
- **Responsibility**: Versioned changelog of methodology rules (rule-IDs, semantics, evidence anchors); canonical source for what disciplines apply to which slice ranges
- **Lives at**: `<HOME>\ai_sdlc\architecture\methodology-changelog.md` (in-repo) and `<HOME>\.claude\plugins\cache\<github-user>\ai-sdlc\methodology-changelog.md` (installed); bidirectional byte-equality enforced by `test_v_0_NN_0_*_entry_present_in_repo_and_installed` family
- **Key interactions**: read by skills + audit tools to know which rules are active; the file's monotonic version sequence (each slice bumps minor version) is gated by PMI-1 v1.1
- **Slice-016 modification**: append v0.31.0 entry with RPCD-1 definition (in-repo only at Phase 1a; forward-sync at Phase 3)

### `tests/methodology/test_critique_agent.py`
- **Responsibility**: Pin-tests for `agents/critique.md` structural invariants (9 dimensions + 9 Dim 9 sub-clauses + cross-references + sub-clause bodies)
- **Lives at**: `<HOME>\ai_sdlc\tests\methodology\test_critique_agent.py`
- **Key interactions**: invoked by pytest at /validate-slice; rows in `architecture/shippability.md` reference specific tests by qualified name
- **Slice-016 modifications**: PMI-1 structural-invariant supersession (1 rename + canonical-literal bump) + 4 NEW body-bound tests (sub-clause-present + names-three-sub-modes + cites-slice-013-014-015 + cites-substantive-discipline-anchors) + 2 end_anchor-tighten Edits (slice-011 RSAD-1 _present test + slice-015 SCPD-1 _present test)

### `tests/methodology/test_methodology_changelog.py`
- **Responsibility**: Pin-tests for `architecture/methodology-changelog.md` byte-equality + version invariants + entry-pin per slice
- **Lives at**: `<HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py`
- **Key interactions**: invoked by pytest at /validate-slice; PMI-1 v1.1 invariant gate `test_plugin_yaml_version_matches_version_file_invariant` is version-agnostic (zero-test-body-modification for atomic version bumps)
- **Slice-016 modifications**: NEW SECTION header + 3 NEW test functions (entry-pin present + entry-pin three-sub-modes + ADR-pin) under EPGD-1 narrow-scope discipline; 0 of 10 prior entry-pin functions touched (v0.22.0..v0.30.0 spans 9 minor versions; v0.29.0 has 2 entry-pin functions per slice-014 (a)↔(b) duality); PMI-1 invariant gate body UNCHANGED. Per slice-016 /critique M2 ACCEPTED-FIXED.

### `plugin.yaml` + `VERSION` + `ai-sdlc-VERSION`
- **Responsibility**: Plugin version triple; atomic bump enforced by PMI-1 v1.1 invariant gate
- **Lives at**: `plugin.yaml` (repo root), `VERSION` (repo root), `ai-sdlc-VERSION` (repo root)
- **Slice-016 modification**: 0.30.0 → 0.31.0 in single atomic commit (Phase 2)

### `architecture/shippability.md`
- **Responsibility**: Catalog of critical-path pytest commands per slice; run at /validate-slice Step 5.5 as final shipping gate
- **Lives at**: `<HOME>\ai_sdlc\architecture\shippability.md`
- **Key interactions**: each row pins specific test functions by qualified name; SCPD-1 governs propagation when test function names are superseded
- **Slice-016 modifications**: (a) SCPD-1 PROACTIVE: rows 6, 11, 13, 15 pytest commands propagated `_lists_eight_sub_clauses` → `_lists_nine_sub_clauses` in same /build-slice block at Phase 5 BEFORE /validate-slice catalog run; (b) NEW row 16 with slice-016 critical-path commands (mirrors slice-015 row 15 structure — 10 pytest commands including PMI-1 invariant gate + ADR-pin)

## Contracts added or changed

None. Slice introduces no API contracts, endpoints, events, or external integrations. Methodology codification only.

## Data model deltas

None. No schema changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Slice introduces **no new modules** — only edits to existing files (methodology-changelog, test files, plugin metadata, shippability catalog) and one NEW ADR file (which is documentation, not a runnable module). The audit treats zero-row matrices as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero rows — header + separator only, audit clean.)

## Decisions made (ADRs)

- [[ADR-015]] — Promote runtime-prerequisite-completeness discipline (RPCD-1) to `agents/critique.md` Dim 9 9th sub-clause — reversibility: **cheap** (with magnitude-of-revert justification ~13-15 sites; same class as ADR-010 / ADR-012 / ADR-014)

## Authorization model for this slice

N/A — internal methodology codification; no user-facing actions, no auth surface, no role gates.

## Error model for this slice

N/A — no error codes introduced. Methodology-changelog parsing relies on existing pytest-based assertion failures (informative AssertionError messages for each pin-test). Standard Python exception model.

## Phase plan

Mirrors slice-015 phase structure with SCPD-1 proactive-application coordinated at Phase 5.

| # | Phase | Files touched | Pre-conditions | Post-conditions |
|---|-------|---------------|----------------|-----------------|
| **1a** | Append methodology-changelog v0.31.0 entry (in-repo only) | `architecture/methodology-changelog.md` | v0.30.0 entry is current top entry | v0.31.0 entry inserted at top of changelog body; RPCD-1 rule-ID + canonical phrase + 3 sub-modes + cross-slice anchors `slice-013/014/015` + ADR-015 forward-ref present |
| **1b** | Entry-pin INSERT under NEW SECTION header (test_methodology_changelog.py) | `tests/methodology/test_methodology_changelog.py` | Phase 1a complete; v0.30.0 SCPD-1 entry-pin section is the last existing SECTION | NEW SECTION header `# --- Slice-016 / RPCD-1 entry pinning ---` + 3 NEW test functions (entry-pin present + entry-pin three-sub-modes + ADR-pin) per EPGD-1 narrow-scope discipline; 0 of 8 prior entry-pin functions (v0.22.0..v0.30.0) touched; PMI-1 invariant gate body unchanged |
| **1c** | PMI-1 structural-invariant supersession in test_critique_agent.py | `tests/methodology/test_critique_agent.py` | Phase 1b complete; agents/critique.md has 9 Dim 9 sub-clauses (verified at /critic-calibrate apply step + CAD-1 audit) | `_lists_eight_sub_clauses` → `_lists_nine_sub_clauses` (function rename + canonical-literal list bumped 8 → 9; appends `"Runtime-prerequisite completeness on proposed fixes"`); function comment updated to reference slice-016 supersession |
| **1d** | NEW body-bound tests in test_critique_agent.py | `tests/methodology/test_critique_agent.py` | Phase 1c complete | **5 NEW test functions** appended after Phase 1c's renamed test (post-/critique-review M-add-1 ACCEPTED-FIXED — completes the N=3 stable `_sub_clause_present` + `_location_pinned` duality): (1) `_sub_clause_present` bare-substring, (2) `_location_pinned` scoped-find with `Shippability-catalog consumer-reference propagation` start_anchor + `### Bonus: weak graph edges` end_anchor, (3) `_names_three_sub_modes`, (4) `_paragraph_cites_slice_013_014_015`, (5) `_cites_substantive_discipline_anchors` |
| **1e** | End_anchor tighten Edits (per slice-016 /critique B1 ACCEPTED-FIXED) | `tests/methodology/test_critique_agent.py` | Phase 1d complete | THREE slice-015 SCPD-1 body-bound tests' end_anchors tightened from `### Bonus: weak graph edges` → `Runtime-prerequisite completeness on proposed fixes`: `_shippability_catalog_propagation_names_both_sub_modes` (L519), `_paragraph_cites_slice_013_and_014` (L554), `_cites_at_least_two_cross_slice_anchors` (L594). The three `_location_pinned` siblings (L173 RSAD-1, L304 EPGD-1, L492 SCPD-1) are NOT touched — their `### Bonus:` end_anchor is structurally load-bearing. Function comments updated with slice-016 /critique B1 ACCEPTED-FIXED tighten provenance (mirrors slice-013 M1 + slice-015 M1 convention) |
| **1f** | ADR-015 written | `architecture/decisions/ADR-015-promote-runtime-prerequisite-completeness-discipline-to-critique-dim-9-sub-clause.md` | Phases 1a-1e complete | ADR-015 file exists with required sections (Status, Context, Options considered, Decision, Consequences, Reversibility, Supersedes); canonical phrase `Runtime-prerequisite completeness on proposed fixes` pinned |
| **2** | Atomic version bump | `plugin.yaml`, `VERSION`, `ai-sdlc-VERSION` | Phases 1a-1f complete | All 3 files read 0.31.0 in single commit; PMI-1 v1.1 invariant gate continues to PASS without test-body modification (empirical retirement-proof N=2 → N=3 stable) |
| **3** | Forward-sync methodology-changelog.md to installed | `<HOME>\.claude\plugins\cache\<github-user>\ai-sdlc\methodology-changelog.md` | Phase 2 complete | Installed copy byte-equal to in-repo (sha256 captured); `test_v_0_31_0_rpcd_1_entry_present_in_repo_and_installed` PASSES |
| **4** | SCPD-1 proactive scan + identify consumers | `architecture/shippability.md` (read-only) | Phase 3 complete | Rows 6, 11, 13, 15 identified as consumers of `_lists_eight_sub_clauses`; propagation Edits prepared (4 edits) |
| **5** | SCPD-1 proactive propagation + new row 16 | `architecture/shippability.md` | Phase 4 complete | Rows 6, 11, 13, 15 pytest commands updated `_lists_eight_sub_clauses` → `_lists_nine_sub_clauses`; NEW row 16 added with slice-016 critical-path pytest commands mirroring slice-015 row 15 structure; SCPD-1 self-application N=1 → N=2 stable post-codification (slice-015 was first canonical reference; slice-016 is second — confirms SCPD-1 N=2 cross-slice stability post-codification) |
| **6** | Pre-finish gates | (audit-only) | Phase 5 complete | `python -m tools.test_first_audit --strict-pre-finish` exit 0; `python -m tools.critique_agent_drift_audit` exit 0; `/drift-check` clean; mid-slice smoke re-run clean; methodology-changelog byte-equality re-verified at slice end (sha256 captured) |

## Design-time audits (RSAD-1 self-application + concrete N=N stability targets)

Per RSAD-1 design-time discipline + slice-013/014/015 precedent N=6/7 audits.

### Audit 1 — RPCD-1 self-application on slice-016's own design.md / mission-brief / ADR-015 (sub-mode (a) NEW-symbol import audit)

**Question**: Does any NEW symbol introduced in this slice's own draft fail import-completeness?
**Evidence**: This slice's NEW test functions (4 in test_critique_agent.py + 3 in test_methodology_changelog.py) all use existing imports already present in their respective test files (`CRITIQUE`, `re`, `pathlib.Path`, `sys`, `_load_text`, etc. per slice-015 precedent). NO new top-level imports introduced. PASS.

### Audit 2 — RPCD-1 self-application sub-mode (b) NEW-status/token allowlist-audit

**Question**: Does any NEW status string / enum value / token introduced in this slice's TF-1 plan fail allowlist-membership?
**Evidence**: TF-1 plan uses statuses from `_ALLOWED_STATUSES` exclusively (`PENDING` / `WRITTEN-FAILING` / `PASSING`). Empirically verified at `tools/test_first_audit.py:65` — `_ALLOWED_STATUSES = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})` (3-element). The slice-015 M-add-1 meta-Critic fix per methodology-changelog v0.30.0 was a "flip 3 rows from `WRITTEN-AS-EDIT` → `PASSING` matching slice-013 precedent" — i.e., the meta-Critic fix AVOIDED introducing a new status by flipping the rows, NOT by adding `WRITTEN-AS-EDIT` to the allowlist. Slice-016 reuses the unchanged 3-element allowlist. NO new tokens introduced. PASS. Per slice-016 /critique M1 ACCEPTED-FIXED.

### Audit 3 — RPCD-1 self-application sub-mode (c) NEW-anchor sibling-grep audit

**Question**: Does any NEW start_anchor / end_anchor / body-bound introduced cause sibling-test false-positive matches?
**Pre-empt Edit at Phase 1e**: The 4 NEW body-bound tests use `Runtime-prerequisite completeness on proposed fixes` as start_anchor — verified unique in critique.md (appears once at the 9th sub-clause title, nowhere else). End_anchor is `### Bonus: weak graph edges` — also appears once at the H3. Sibling tests sharing the same anchor pair: only the 2 EXISTING body-bound tests being tightened in Phase 1e (slice-011 RSAD-1 _present + slice-015 SCPD-1 _present). After Phase 1e tighten, NO sibling tests share the new anchor pair. **PRE-EMPTED via Phase 1e** ahead of Phase 1d body-bound test additions; design.md sequencing ensures Phase 1d tests are written AFTER Phase 1c structural-invariant rename but BEFORE Phase 1e tightens (so Phase 1d's new tests do NOT collide with the not-yet-tightened sibling tests' anchor pair). PASS.

### Audit 4 — EPGD-1 self-application structural separation

**Question**: Does Phase 1b's entry-pin INSERT preserve all 10 prior entry-pin functions (v0.22.0..v0.30.0 spans 9 minor versions; v0.29.0 carries 2 functions per slice-014 (a)↔(b) duality) and Phase 1c's structural-invariant supersession preserve the PMI-1 v1.1 invariant gate body?
**Evidence**: Phase 1b creates a NEW SECTION header `# --- Slice-016 / RPCD-1 entry pinning ---` placed AFTER the existing slice-015 SCPD-1 section. Phase 1c is a function-body Edit on `test_critique_dim_9_lists_eight_sub_clauses`'s containing module — narrow-scoped to the function body + name; the 10 prior entry-pin functions live in `test_methodology_changelog.py` (different module — `test_v_0_22_0_*` at L76 through `test_v_0_30_0_*` at L747, including the v0.29.0 doubled entry-pin functions at L437 + L499 per slice-014 (a)↔(b) duality), zero risk of accidental deletion. PMI-1 invariant gate `test_plugin_yaml_version_matches_version_file_invariant` is in `test_methodology_changelog.py` — different module, untouched. EPGD-1 self-application N=4 → N=5 stable. PRE-EMPTED via cross-module separation. PASS. Per slice-016 /critique M2 ACCEPTED-FIXED.

### Audit 5 — PMI-1 v1.1 version-agnostic invariant gate empirical retirement-proof

**Question**: Will the atomic version bump 0.30.0 → 0.31.0 in Phase 2 succeed with ZERO test body modification on `test_plugin_yaml_version_matches_version_file_invariant`?
**Evidence**: PMI-1 v1.1 (slice-014 ADR-013) refactored the gate to read `plugin.yaml.version` + `VERSION` and assert equality — no version literal in body. Slice-015 was the first empirical retirement-proof (N=1 standalone); slice-016 is the **second cross-slice retirement-proof (N=2 → N=3 stable)**. Phase 2 atomic bump touches 3 files, gate body unchanged. PASS expected.

### Audit 6 — N-surface schema-pin canonical phrase across 3 surfaces

**Question**: Is canonical phrase `Runtime-prerequisite completeness on proposed fixes` pinned across 3 surfaces (ADR-015 + in-repo methodology-changelog v0.31.0 + installed methodology-changelog v0.31.0)?
**Evidence**: AC #1 (in-repo methodology-changelog v0.31.0) + Phase 3 (forward-sync to installed) + ADR-015 Status section + Decision section (Phase 1f) jointly pin the phrase. N-surface schema-pin 4-instance pattern N=4 → **N=5 stable** post-codification (RSAD-1 + EPGD-1 + PMI-1 v1.1 + SCPD-1 + RPCD-1).

### Audit 7 — End_anchor tighten completeness (slice-015 generic methodology recurrence N=2 → N=3 stable) — REVISED per slice-016 /critique B1 + M3 ACCEPTED-FIXED

**Question**: Have ALL body-bound tests currently using `### Bonus: weak graph edges` as end_anchor been identified for tightening to `Runtime-prerequisite completeness on proposed fixes`? (Excluding `_location_pinned` siblings whose `### Bonus:` end_anchor is structurally load-bearing — verifies the sub-clause title falls BEFORE the H3 — per slice-013 + slice-015 precedent.)

**Empirical scan** (`grep -n 'end_anchor = "### Bonus: weak graph edges"' tests/methodology/test_critique_agent.py` returns 6 hits):

| Line | Containing function | Classification | Action |
|------|---------------------|----------------|--------|
| L173 | `test_critique_dim_9_recursive_self_application_location_pinned` (RSAD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L304 | `test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned` (EPGD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L492 | `test_critique_dim_9_shippability_catalog_propagation_location_pinned` (SCPD-1) | `_location_pinned` sibling | KEEP — `### Bonus:` is load-bearing |
| L519 | `test_critique_dim_9_shippability_catalog_propagation_names_both_sub_modes` (SCPD-1) | body-bound | **TIGHTEN at Phase 1e** |
| L554 | `test_critique_dim_9_shippability_catalog_propagation_paragraph_cites_slice_013_and_014` (SCPD-1) | body-bound | **TIGHTEN at Phase 1e** |
| L594 | `test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors` (SCPD-1) | body-bound | **TIGHTEN at Phase 1e** |

**Result**: 3 of 6 queued for Phase 1e end_anchor tighten (the 3 slice-015 SCPD-1 body-bound tests). The 3 `_location_pinned` siblings stay at `### Bonus: weak graph edges` per slice-013 + slice-015 precedent. Generic recurrence N=2 → **N=3 stable** post-codification at slice-016 (slice-013 tightened slice-011's body-bound tests when 7th sub-clause appended; slice-015 tightened slice-013's body-bound tests when 8th sub-clause appended; slice-016 tightens slice-015's body-bound tests when 9th sub-clause appended).

**Meta-note**: this audit's original (pre-fix) draft enumerated only 2 of 6 sites and misclassified BOTH targets as body-bound — an RPCD-1 sub-mode (c) sibling-grep failure that the first Critic caught at slice-016 /critique B1 + M3. The corrected audit now demonstrates RPCD-1 sub-mode (c) self-application post-fix: enumerate ALL sites, classify each. The slice authoring RPCD-1 produced an RPCD-1 self-defect on its own draft AND now demonstrates the corrected discipline — empirical recursive-self-application N=7 → N=8 cumulative post-codification.

### Audit 8 — SCPD-1 proactive-application scan completeness (cross-Phase consumer-reference propagation)

**Question**: Have ALL consumer references to `_lists_eight_sub_clauses` been identified for propagation to `_lists_nine_sub_clauses` BEFORE /validate-slice catalog run?
**Empirical scan** (grep `_lists_eight_sub_clauses` in `architecture/shippability.md`):
- Row 6 (slice-006) — pytest command includes the literal
- Row 11 (slice-011) — pytest command includes the literal
- Row 13 (slice-013) — pytest command includes the literal
- Row 15 (slice-015) — pytest command includes the literal
**Result**: 4 rows identified; all queued for Phase 5 propagation in same /build-slice block BEFORE /validate-slice Step 5.5 catalog run. SCPD-1 proactive-application self-application N=1 → **N=2 stable** post-codification (slice-015 was first canonical reference instance; slice-016 is second). **Also confirms SCPD-1's three sub-modes coverage** — slice-016 uses Proactive-application sub-mode (slice-015 N=2 evidence-anchored sub-mode).

## Risk register impact

No new risks. R-1 (cwd-mismatch /diagnose) and R-2 (no programmatic /diagnose warning test) remain open but untouched by this slice (out-of-scope per mission brief).

## Cost summary

- **Implementation**: ~30-45 min (mirrors slice-015 cycle time)
- **Reversibility**: **cheap** with magnitude-of-revert justification ~13-15 sites:
  - 1 methodology-changelog entry (revert: delete entry)
  - 1 ADR file (revert: delete file)
  - 1 entry-pin SECTION + 3 functions in test_methodology_changelog.py (revert: delete section)
  - 1 PMI-1 structural-invariant supersession in test_critique_agent.py (revert: rename back + canonical-literal list 9 → 8)
  - 5 NEW body-bound tests in test_critique_agent.py (revert: delete functions)
  - 3 end_anchor tighten Edits (revert: change anchor back to `### Bonus: weak graph edges`)
  - 1 atomic version bump (revert: 0.31.0 → 0.30.0 in 3 files)
  - 1 forward-sync to installed (revert: re-sync from prior in-repo state)
  - 4 shippability.md row propagations + 1 new row 16 (revert: rename back + delete row 16)
  Same magnitude class as ADR-010 (RSAD-1) / ADR-012 (EPGD-1) / ADR-014 (SCPD-1).
- **Irreversibles**: archived /critique outputs from slice-016 onward that file findings under Dim 9's 9th sub-clause are filed permanently; in-context conditioning of the 9-dim-with-9th-sub-clause Critic on its runs across slice-017+ accumulates. Same class as ADR-005 / ADR-008 / ADR-010 / ADR-012 / ADR-014 irreversibles. Net-zero impossible after ~3-5 post-codification slices; refinement-over-revert is the canonical recovery path.

## Open questions

None. Mission brief + design captures all known scope. Critic invocation (mandatory per MCT-1) at /critique + /critique-review (DR-1) provides the adversarial cross-check.
