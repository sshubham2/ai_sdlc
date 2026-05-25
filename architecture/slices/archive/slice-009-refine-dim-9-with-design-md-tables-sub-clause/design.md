# Design: Slice 009 refine-dim-9-with-design-md-tables-sub-clause

**Date**: 2026-05-11
**Mode**: Standard (per slice-008 archive — most recent active mode)
**Risk tier**: medium; **critic-required**: true (voluntary, per slice-008 aggregated-lessons #1 — cross-cutting tooling slices N=8/8 paid off with 8/8 design-stage catches; running 25/25 Critic-VALIDATED across slices 6-8)

## What's new

- **CCC-1 v1.1 — Dim 9 sub-clause 2 body refinement** (additive prose extension). `agents/critique.md` line 160's "Tooling-doc-vs-implementation parity" sub-clause body gains ~5 appended sentences naming the **design-doc-level surface** as the sibling of the source-code-level surface already covered by Dim 1's surgical sub-bullet (line 58). The new sentences (per Critic M2 — distinguish positive-inclusion from negative-exclusion canonical surfaces):
  - Name `design.md mechanical tables` as the canonical phrase for the design-doc-level surface.
  - Name `methodology canonical inventories` (plural) as the canonical reference target — enumerating TWO distinct surface families for installed-files tables: (a) **positive-inclusion** surface — `tools/install_audit.py` `_CANONICAL_*` tuples (`_CANONICAL_SKILLS`, `_CANONICAL_AGENTS`, `_CANONICAL_TEMPLATES`, `_CANONICAL_METADATA`, `_CANONICAL_TOOLS`) enumerate what IS installed; (b) **negative-exclusion** surface — `INSTALL.md` Step 3f "do not copy" list enumerates what is intentionally NOT installed. Also: `methodology-changelog.md` versioned-entry conventions for version-bump slices (PMI-1); `plugin.yaml` for plugin manifest entries; in-repo `VERSION` vs installed `~/.claude/ai-sdlc-VERSION` install-time rename surface.
  - Carry the two concrete cross-slice examples at N=2, each correctly mapped to its canonical inventory surface (per Critic M2 — slice-009's design originally conflated these; correction recursive-self-applies the discipline): **slice-006 DEVIATION-1** (design.md listed `plugin.yaml` in its forward-sync table, but `plugin.yaml` is on `INSTALL.md` Step 3f's do-not-copy list — exercises the **negative-exclusion** surface) + **slice-006 DEVIATION-2** (design.md missed `ai-sdlc-VERSION` from its forward-sync table despite `ai-sdlc-VERSION` being in INST-1's `_CANONICAL_METADATA` tuple — exercises the **positive-inclusion** surface); **slice-007 Critic B1** (design.md "Out-of-repo files touched" table named in-repo `ai-sdlc-VERSION` instead of in-repo `VERSION` — exercises the **install-time-rename** surface).
  - Frame the discipline: "every mechanical row of every design.md table must be cell-verifiable against the canonical inventory — and where the canonical inventory has multiple surfaces (positive-inclusion vs. negative-exclusion; in-repo name vs. installed renamed name), the Critic must consult ALL applicable surfaces."
- **`~/.claude/agents/critique.md`** (out-of-repo) — Phase 2 forward-sync target. Same edit applied; CAD-1 byte-equality verified at slice end.
- **`tests/methodology/test_critique_agent.py`** — add 2 new test functions:
  - `test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables` (AC #1) — asserts 3 canonical literals present in `CRITIQUE`: `design.md mechanical tables`, `canonical inventor` (prefix matches both `canonical inventory` / `canonical inventories`), `install-time rename`.
  - `test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007` (AC #2) — asserts 5 example-anchor literals: `slice-006`, `DEVIATION-1`, `DEVIATION-2`, `slice-007`, `ai-sdlc-VERSION`.
- **`methodology-changelog.md`** (in-repo + `~/.claude/`) — new H2 entry `## v0.24.0 — 2026-05-11` under `### Changed` (refinement vs. `### Added` for new mechanisms — distinguishes CCC-1 v1.1 body-refinement from BC-1 v1.2's new-mechanism additions). Body documents CCC-1 v1.1 + cites slice-009 + ADR-008.
- **`tests/methodology/test_methodology_changelog.py`** — add `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` (bidirectional pin per slice-007/008 precedent); REPLACE `test_plugin_yaml_version_matches_version_file_at_0_23_0` with `test_plugin_yaml_version_matches_version_file_at_0_24_0` (PMI-1 versioned-gate supersession per slice-007/008 N=2-stable pattern — no two version-gates coexist).
- **`VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`**: atomic bump 0.23.0 → 0.24.0 (PMI-1 invariant per slice-007 escape-closure pattern).
- **`architecture/shippability.md`** — add row 9 naming slice-009's critical path: Dim 9 sub-clause 2 design-doc-level refinement + CAD-1 byte-equality + v0.24.0 entry + PMI-1 0.24.0 supersession. Note in row 8 (slice-008) header that slice-008's `_at_0_23_0` gate is superseded by slice-009 row 9 (mirrors slice-008's row 7 update for slice-007's v0.22.0 gate).
- New ADR: [[ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class]] — reversibility: **cheap** (with minor irreversible portion: append-only changelog + cumulative slice-009-N Critic outputs influenced by v1.1 framing; same shape as ADR-005 but smaller magnitude).

## What's reused

- CCC-1 v1 ground (`agents/critique.md` Dim 9 + the 5 sub-clauses) — slice-009 extends sub-clause 2's body inline; does NOT replace the dimension or add a 6th sub-clause. The 5-sub-clause structural invariant pinned by `test_critique_dim_9_lists_five_sub_clauses` is preserved.
- Dim 1 surgical sub-bullet at line 58 (`agents/critique.md`) — unchanged. The source-code-level surface stays narrow in Dim 1; the design-doc-level surface is the cross-cutting view in Dim 9. Cross-reference text (`see Dimension 1 sub-bullet`) preserved.
- CAD-1 byte-equality audit (`tools/critique_agent_drift_audit.py`, slice-007) — used unchanged as AC #3 verification + pre-finish gate. Confirms in-repo↔installed sha256 byte-equality on `agents/critique.md` after Phase 2 forward-sync.
- BC-1 v1.2 negative-anchor mechanism (slice-008) — silences BC-PROJ-1 + BC-GLOBAL-1 on this slice's mission-brief + design (which contains methodology-vocabulary anchors `aggregated lessons`, `meta-discussion`, `vocabulary`, `back-sync`, `forward-sync`, `Dim 9`). Empirically verified at design-time (see "Empirical verification" section below). Self-application clean — closes the noise loop.
- PMI-1 atomic version bump pattern (slice-007/008 N=2 stable) — atomic across `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`.
- PMI-1 versioned-gate test supersession pattern (slice-007 introduced `_at_0_22_0`; slice-008 first-superseded with `_at_0_23_0` = N=1 supersession event per Critic M5 — slice-009 ratchets to N=2 supersession events on completion) — slice-009 supersedes slice-008's `_at_0_23_0` gate with `_at_0_24_0`. The supersession act is justified by slice-008 reflection's explicit choice + the in-repo VERSION file's monotonicity invariant, NOT by N=2 stability of supersession-events (slice-009 itself is creating that N=2). Single un-versioned gate is a deferred refactor candidate (per slice-008 reflection — `refactor-pmi-1-gate-to-version-agnostic-shape`; defer indefinitely unless version-bump churn becomes friction).
- TWO-surface schema-pin discipline generalization to N-surface (slice-007 + slice-008 lesson) — slice-009 has TWO new test substring surfaces in AC #1 (`design.md mechanical tables` + `install-time rename`) and FIVE example-anchor substrings in AC #2. Per slice-008 M2: N-substring discipline for any AC with multi-substring coverage.
- Bidirectional sha256 forensic capture pattern (slice-006 + slice-007 + slice-008 N=3 stable) — slice-009 captures sha256 for `agents/critique.md` (in-repo) + `~/.claude/agents/critique.md` (installed) + `methodology-changelog.md` (in-repo + installed) + `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) BEFORE Phase 2 forward-sync (Phase 0) and AFTER (Phase 4). Out-of-repo edits require explicit forensic capture per N=4 stable lesson (slice-005..008).
- The 13 existing `tests/methodology/test_critique_agent.py` tests as regression-guard for backward-compat (per ADR-005 + ADR-008 implicit covenant: refinement is additive, not breaking). Slice-009 adds 2 new tests; modifies 0 existing tests. The 5-sub-clause invariant test, the cross-reference resolution test, and the citation-deliberate test all continue to PASS unchanged through Phase 1-4.
- "Validate using your own ship" pattern (N=6 stable across slice-003..008) — slice-009 self-applies the BC-1 v1.2 negative-anchor mechanism (closes the noise loop on its own ship; empirically verified pre-design).
- Empirical-verification-at-design-time discipline (N=7 stable across slices) — slice-009 runs the BC-1 audit against THIS slice's own mission-brief + design BEFORE locking ACs (see "Empirical verification" section).

## Components touched

### `agents/critique.md` (modified — in-repo canonical)

- **Responsibility**: Critic agent prompt; carries 9 review dimensions (1-8 from META-2 + 9 from CCC-1 v1). Dim 9 has 5 sub-clauses; sub-clause 2 is "Tooling-doc-vs-implementation parity" cross-referencing Dim 1.
- **Lives at**: `agents/critique.md`
- **Key interactions**: read by the `critique` subagent at /critique invocation; pinned by `tests/methodology/test_critique_agent.py` (13 existing prose-pin tests verified via `grep -c '^def test_'`; ratcheting to 16 after slice-009 per Critic B1 + M1); installed at `~/.claude/agents/critique.md` via INST-1; byte-equality verified by `tools.critique_agent_drift_audit` (CAD-1).
- **What changes**:
  - Dim 9 sub-clause 2 body (~line 160) extends by ~5 appended sentences. The bullet's title (`- **Tooling-doc-vs-implementation parity** —`) is unchanged. The first sentence ("see Dimension 1 sub-bullet for full examples") preserved unchanged. The closing example sentence ("Concrete misses: slice-002 RR-1 docstring vs `_RISK_HEADING_RE` regex; slice-003 BC-1 trigger-keyword false positives.") preserved unchanged. New sentences appended after the existing closing.
  - **No changes to**: Dim 1, Dim 2-8, Dim 9 paragraph 1 (header), Dim 9 paragraph 2 (Kiczales citation), Dim 9 sub-clauses 1 / 3 / 4 / 5, Bonus weak-edges section, Specificity rule, Honesty rule, Severity rules, Output format, "What you DO NOT do", Common failure modes, Calibration awareness.

### `~/.claude/agents/critique.md` (modified — out-of-repo Phase 2 forward-sync target)

- **Responsibility**: installed runtime copy of `agents/critique.md`. Read by the `critique` subagent's prompt loader at /critique invocation.
- **Lives at**: `~/.claude/agents/critique.md` (installed via INST-1 per `tools/install_audit.py`).
- **Key interactions**: byte-equality with in-repo verified by CAD-1 (`tools.critique_agent_drift_audit`); pinned by `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal`.
- **What changes**: same body refinement as in-repo `agents/critique.md`. Phase 2 forward-sync (Copy-Item from in-repo) after in-repo edits are validated via mid-slice smoke gate.

### `methodology-changelog.md` (in-repo + `~/.claude/`) — append-only entry

- **Responsibility**: methodology rule changelog; pinned by PMI-1 + bidirectional changelog-entry-pin tests.
- **What changes**: new H2 entry `## v0.24.0 — 2026-05-11` under `### Changed` (refinement) — title: "CCC-1 v1.1 — Dim 9 sub-clause 2 body refinement covering design.md mechanical tables vs methodology canonical inventories". Body includes:
  - One-paragraph summary (mirrors v0.21.0 / v0.22.0 / v0.23.0 prose pattern).
  - Bullet documenting the refinement scope (design-doc-level sub-class of Tooling-doc-vs-impl parity; promotion at N=2 per slice-007 reflection; reinforced by slice-008 M1 + M2).
  - **Rule reference**: CCC-1 v1.1.
  - **Substantive canonical phrase** (per Critic M3 — mirrors slice-008's `Negative anchors` substantive content anchor for v0.23.0 BC-1 v1.2 entry per N-surface schema-pin discipline): `design.md mechanical tables`. The v0.24.0 entry MUST contain this exact substring in BOTH in-repo and installed copies — reuses the same canonical phrase already pinned in critique.md AC #1's `test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables`. Two surfaces × one substring = consistent contract per slice-008 M2 N-surface lesson.
  - **Defect class**: Per slice-007 reflection lesson "design.md mechanical tables (forward-sync, prerequisites, dependencies, install-time renames) need verification against in-house methodology rules' canonical inventories AND install-time conventions — N=2 stable at slice-007 (slice-006 DEVIATION-1+2 + slice-007 B1)". Reinforced by slice-008 reflection lessons on Wiegers AC-trace (M1) + N-surface schema-pin (M2).
  - **Validation**: `tests/methodology/test_critique_agent.py::test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables` (new, AC #1) + `test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007` (new, AC #2) + `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` (CAD-1, AC #3) + `tests/methodology/test_methodology_changelog.py::test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` (bidirectional entry pin, AC #4) + `test_plugin_yaml_version_matches_version_file_at_0_24_0` (PMI-1 supersession of slice-008's `_at_0_23_0`, AC #5).
  - Limitations (v1.1, documented in the entry): bullet body grows ~3→8 lines (slight readability cost vs separate sub-clause); slice-009 v1.1 effectiveness check at next /critic-calibrate run (slices 9-15 design-doc-tables miss-rate vs slice-006/007 baseline of 1-per-slice); no automated audit (Critic prompt addition only — same caveat as CCC-1 v1 limitations); refinement-favored-over-revert per ADR-008 cost summary.

### `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml.version` — atomic version bumps

- **What changes**: 0.23.0 → 0.24.0 in all three locations. PMI-1 invariant per slice-007/008 escape-closure pattern. `~/.claude/ai-sdlc-VERSION` is the install-time-renamed copy of in-repo `VERSION` per INST-1 (slice-007 Critic B1 + slice-009 Dim 9 v1.1 design.md mechanical-tables sub-class — the canonical example case of an install-time rename).

### `tests/methodology/test_critique_agent.py` (modified — additive)

- **Responsibility**: pin load-bearing prose in `agents/critique.md`; regression-guard the Critic agent prompt contract.
- **Lives at**: `tests/methodology/test_critique_agent.py`
- **Key interactions**: imports `CRITIQUE = read_file("agents/critique.md")` from `tests/methodology/conftest.py`; runs as part of methodology suite (`tests/methodology/`).
- **What changes**: append 3 new test functions (per Critic B1 + M1) placed after `test_critique_dim_9_citation_is_deliberate` line 165 — preserving the 5-sub-clause / cross-reference / citation cluster ordering. Existing 13 tests unchanged. Test count: 13 → 16 (2 substring tests for AC #1 + AC #2; 1 location-pin test for Critic M1).

### `tests/methodology/test_methodology_changelog.py` (modified — supersession)

- **Responsibility**: pin methodology-changelog entries bidirectionally (in-repo + `~/.claude/`); regression-guard PMI-1 atomic version invariant.
- **Lives at**: `tests/methodology/test_methodology_changelog.py`
- **Key interactions**: imports `tools.plugin_manifest_audit` (PMI-1 reference impl); reads `methodology-changelog.md` + `~/.claude/methodology-changelog.md`.
- **What changes**:
  - ADD `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` (bidirectional entry pin per slice-007/008 precedent).
  - REPLACE `test_plugin_yaml_version_matches_version_file_at_0_23_0` with `test_plugin_yaml_version_matches_version_file_at_0_24_0`. The replacement is single-function: the prior test's body checks `plugin.yaml.version == "0.23.0"`; the new test's body checks `== "0.24.0"`. Per slice-007 + slice-008 PMI-1 versioned-gate pattern (slice-007 introduced; slice-008 first-superseded = N=1 supersession event per Critic M5), slice-009 ratchets to N=2 supersession events. No two version-gates coexist (the in-repo VERSION file is monotonic; running both gates would double-count the invariant and create maintenance churn).

### `architecture/shippability.md` (modified)

- **Responsibility**: critical-path tests catalog; `/validate-slice` runs each row at pre-finish to catch slice-induced regressions.
- **Lives at**: `architecture/shippability.md`.
- **What changes**:
  - APPEND row 9 (slice-009): critical path = Dim 9 sub-clause 2 design-doc-level refinement (2 new tests) + CAD-1 byte-equality on `agents/critique.md` + bidirectional v0.24.0 entry pin + PMI-1 0.24.0 atomicity. Command: `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables tests/methodology/test_critique_agent.py::test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007 tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal tests/methodology/test_methodology_changelog.py::test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_at_0_24_0 --no-header -q`. Expected runtime: <2s.
  - UPDATE row 8 (slice-008) Critical path text to note PMI-1 version-gate supersession at slice-009 (mirrors slice-008's row 7 update for slice-007's `_at_0_22_0` gate).

## Algorithm-path conformance (per slice-005 lesson; generalized at slice-008 N=2 stable)

Every existing `tests/methodology/test_critique_agent.py` test traced against the refinement to confirm no breakage. The 13 existing tests' assertion targets are mapped against the new Dim 9 sub-clause 2 body and the rest of `agents/critique.md`:

| Test function | Asserts (substring) | Pre-slice-009 location | Post-slice-009 status | Algorithm-path verdict |
|----------------|----------------------|-------------------------|------------------------|------------------------|
| `test_critique_carries_adversarial_stance` | `Assume the design is wrong until proven right` | Stance section (line 12) | unchanged | ✓ stays green |
| `test_critique_forbids_softening_findings` | `Do not soften findings` | "What you DO NOT do" section | unchanged | ✓ stays green |
| `test_critique_forbids_manufactured_findings` | `Do NOT manufacture findings to justify the review` | Honesty rule section | unchanged | ✓ stays green |
| `test_critique_lists_nine_dimensions` | `1. Unfounded assumptions` ... `9. Cross-cutting conformance` (9 dimension headers) | Lines 48-56 | unchanged | ✓ stays green |
| `test_critique_names_reference_frameworks` | `Wiegers`, `Fowler`, `Newman`, `OWASP`, `McGraw`, `Hendrickson` | Reference frameworks table | unchanged | ✓ stays green |
| `test_critique_specifies_severity_levels` | `**Blocker**`, `**Major**`, `**Minor**` | Severity rules section | unchanged | ✓ stays green |
| `test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet` | `Verify by reading the implementation`, `TF-1, RR-1, BC-1, WIRE-1, NFR-1, VAL-1, CSP-1` | Dim 1 sub-bullet (line 58) | unchanged | ✓ stays green |
| `test_critique_dim_4_has_methodology_audit_conformance_sub_bullet` | `Methodology-audit conformance`, `TF-1 row coverage`, `Algorithm-path-conformance with pre-existing branches` | Dim 4 sub-bullet (line 90+) | unchanged | ✓ stays green |
| **`test_critique_dim_9_lists_five_sub_clauses`** | `Methodology-audit conformance`, `Tooling-doc-vs-implementation parity`, `Algorithm-path-conformance`, `Runtime-environment`, `Language-version conformance` | Dim 9 sub-clause titles (lines 158-166) | unchanged — 5 sub-clause TITLES preserved, only sub-clause 2's BODY grows | ✓ **stays green (regression-guard)** |
| **`test_critique_dim_9_cross_references_resolve`** | `see Dimension 4 sub-bullet`, `Methodology-audit conformance`, `see Dimension 1 sub-bullet`, `Verify by reading the implementation` | Dim 9 sub-clauses 1+2 cross-references (lines 158-160) + Dim 1 sub-bullet body (line 58) | unchanged — cross-reference text + target text both preserved | ✓ **stays green (cross-reference integrity)** |
| `test_critique_dim_9_citation_is_deliberate` | `Kiczales`, (`no peer-level evidence-framework` OR `no specific evidence-framework`) | Dim 9 paragraph 2 (line 156) | unchanged | ✓ stays green |
| `test_critique_output_format_lists_nine_dimensions` | 9 `- [x] <dimension>` lines in `## Dimensions checked` block | Output format section | unchanged | ✓ stays green |
| `test_no_in_repo_drift_on_eight_dimensions_phrase` | No `8 dimensions` substring in `agents/`, `skills/`, `plugin.yaml`, `tutorial-site/` (excluding methodology-changelog.md + architecture/) | Whole-file scan | unchanged (refinement adds prose under "9th dimension"; doesn't reintroduce "8 dimensions" anywhere) | ✓ stays green |

**Conclusion**: all 13 existing tests algorithm-path-conformant with the refinement. The refinement is **additive within sub-clause 2's bullet body**; no enumeration count change, no cross-reference removal, no citation alteration. The 3 new tests (`_covers_design_md_tables` substring pin for AC #1 + `_cites_slice_006_and_007` substring pin for AC #2 + `_sub_clause_2_body_contains_design_md_table_paragraph` location pin per Critic M1) target NEW substrings/locations introduced by the refinement; they fail pre-fix and PASS post-fix (genuine TF-1 PENDING → WRITTEN-FAILING → PASSING transition).

## Empirical verification at design-time (per slice-008 N=7 discipline)

Per the empirical-verification-at-design-time lesson (slice-008 N=7 stable; "running the audit against representative archives BEFORE locking the verification plan; surfaced that slice-007 keyword-only backtest wouldn't be genuine-WRITTEN-FAILING. Cost ~30 sec; saved entire failed-design cycle"):

### 1. BC-1 self-application check (closes noise loop pre-design)

`python -m tools.build_checks_audit --slice architecture/slices/slice-009-refine-dim-9-with-design-md-tables-sub-clause --project-checks architecture/build-checks.md --changed-files agents/critique.md methodology-changelog.md --no-carry-over --json` returns:

- **applicable**: `[]`
- **skipped**: BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1
- Reason: BC-PROJ-1 + BC-GLOBAL-1 both carry the 9-token negative-anchor list from slice-008; the slice's mission-brief.md + design.md contain ≥3 negative-anchor matches (`aggregated lessons`, `meta-discussion`, `vocabulary`, `back-sync`, `forward-sync`, `Dim 9`). BC-PROJ-2's glob (`skills/**/*.py, tools/**/*.py`) doesn't match this slice's `agents/critique.md` + `methodology-changelog.md` changed-files.

**Self-application clean.** No manual defer-with-rationale needed. Closes the noise loop on the slice's own ship — "validate using your own ship" pattern N=6 stable (slice-003..008 N=6; slice-009 ratchets to N=7 post-build).

### 2. Test-pin substring conflict scan (pre-write check)

Grep across `agents/critique.md` for the 8 canonical literals slice-009 introduces:

| Substring | Pre-slice-009 occurrence count in `agents/critique.md` | Source |
|-----------|----------------------------------------------------------|--------|
| `design.md mechanical tables` | 0 | new at slice-009 |
| `canonical inventories` | 0 | new at slice-009 |
| `install-time rename` | 0 | new at slice-009 |
| `slice-006` | 0 | new at slice-009 in critique.md |
| `DEVIATION-1` | 0 | new at slice-009 |
| `DEVIATION-2` | 0 | new at slice-009 |
| `slice-007` | 0 | new at slice-009 |
| `ai-sdlc-VERSION` | 0 | new at slice-009 in critique.md |
| `INSTALL.md` | 0 | new at slice-009 (per Critic M2 — distinguishes do-not-copy surface from `_CANONICAL_*` positive-inclusion surface) |

All 9 canonical literals absent pre-slice-009 in `agents/critique.md` (8 from the original design + 1 added per Critic M2 distinguishing INSTALL.md surface from `_CANONICAL_*` surface). The 3 new tests (per Critic B1 + M1) will fail with `AssertionError: '<literal>' not in CRITIQUE` (or location-pin AssertionError for M1's row) pre-fix; PASS post-fix. **Genuine TF-1 PENDING → WRITTEN-FAILING → PASSING transition confirmed per substring + location anchor.**

### 3. Existing-test-substring scan (regression-safety check)

Grep across `agents/critique.md` for existing-test substring assertions across 13 distinct test functions (per Critic B1 — actual count via `grep -c '^def test_'`):

- All 13+ substrings present in current `agents/critique.md`.
- Refinement adds prose; doesn't remove or alter existing substring sites.
- Algorithm-path table above confirms zero-regression on the 13 existing tests.

### 4. Pre-slice-009 PMI-1 audit baseline

`python -m tools.plugin_manifest_audit --root .` exit 0 (currently clean at 0.23.0). Post-slice-009 atomic bump to 0.24.0 expected to remain exit 0.

### 5. Pre-slice-009 CAD-1 audit baseline

`python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exit 0 (currently clean — slice-008 ended with byte-equality on `agents/critique.md`). Phase 1 in-repo edit → exit 1 (content-drift, EXPECTED at mid-slice smoke gate) → Phase 2 forward-sync → exit 0 (CAD-1 audit clean post-sync, pre-finish gate).

## Contracts added or changed

**None.** Slice modifies a prompt-prose file (`agents/critique.md`) + tests + changelog + version files. No new endpoints, events, schemas, or API surfaces. The Critic agent prompt itself IS a contract (consumed by the `critique` subagent at /critique invocations), but this slice doesn't change its frontmatter / tools list / model field / fundamental shape — only refines body content within an existing dimension's sub-clause.

## Data model deltas

**None.** No dataclasses, DB migrations, schema changes, or model file modifications.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces no new modules — all changes are extensions of existing files (`agents/critique.md`, `methodology-changelog.md`, `tests/methodology/test_critique_agent.py`, `tests/methodology/test_methodology_changelog.py`, `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml`, `architecture/shippability.md`) + a new ADR file (`architecture/decisions/ADR-008-*.md` — vault document, not a runtime module). Empty-matrix posture (header + separator only — accepted by audit per slice-005 / slice-008 fixture pattern).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class]] at `architecture/decisions/ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class.md` (per Critic m3 — explicit file path pinned) — adopt Option 3 from the 5-options analysis: refine Dim 9 sub-clause 2 "Tooling-doc-vs-implementation parity" body inline (preserves 5-sub-clause structural invariant; cross-reference structure preserved; design-doc-level extension appended to source-code-level cross-reference). Reversibility: **cheap** (with minor irreversible portion — append-only changelog + cumulative slice-009-N Critic outputs influenced by v1.1 framing; magnitude justification added to ADR-008 Reversibility section per Critic M4).

## Authorization model for this slice

N/A — slice modifies a methodology-prose file (Critic agent prompt) + test pins + changelog entries + version files. No auth/authz surface. The Critic agent runs locally on the developer's machine via subagent invocation; no network calls; no user-data flow; no authentication.

## Error model for this slice

N/A — no new error codes. Affected audits (`tools.critique_agent_drift_audit`, `tools.plugin_manifest_audit`) preserve their existing exit-code semantics (0 clean / 1 drift OR version-mismatch / 2 path-missing OR usage-error). No new error path introduced.

## Test-first plan refinement (post-design; 6 rows)

Mission-brief TF-1 plan had 6 rows. Design.md confirms 6 rows; one row in the original plan (`test_critique_dim_9_lists_five_sub_clauses` listed under AC #1) is **moved to the must-not-defer + verification-plan slots** per the slice-002 / slice-004 / slice-005 lesson "Regression-guard ACs MUST be authored into verification-plan + must-not-defer, NOT into the numbered-AC list. TF-1 strict-pre-finish refuses with `ac-without-row` for regression-guard ACs". The 5-sub-clause invariant test EXISTS PRE-SLICE; it must STAY PASSING through the refinement. TF-1 PENDING → WRITTEN-FAILING is undefined for tests that are already-PASSING regression-guards; they don't transition. Correcting this from the mission-brief draft:

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables | PENDING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph | PENDING (added per Critic M1 — location-pin guard) |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007 | PENDING |
| 3 | integration | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal | PENDING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed | PENDING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_at_0_24_0 | PENDING |
| (must-not-defer) | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_lists_five_sub_clauses | (existing — regression-guard; NOT a TF-1 row per slice-002/004/005 lesson) |

**Genuine PENDING → WRITTEN-FAILING transitions** per row (per slice-003..008 lesson N=5 stable):

- **Row 1a** (AC #1, substring pin): `test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables` — fails pre-fix with `AssertionError: 'design.md mechanical tables' not in CRITIQUE` (canonical literal absent until Phase 1 edit applies). Post-fix: PASS after Phase 1 in-repo edit; remains PASS after Phase 2 forward-sync (CRITIQUE reads in-repo via conftest).
- **Row 1b** (AC #1, location pin per Critic M1): `test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph` — fails pre-fix with `AssertionError: 'design.md mechanical tables' index not between 'Tooling-doc-vs-implementation parity' index and 'Algorithm-path-conformance' index` (canonical literal absent + location anchor enforced). Post-fix: PASS after Phase 1 in-repo edit. Anchors the new paragraph's location to sub-clause 2's body; prevents silent paragraph-relocation drift across future refinements.
- **Row 2** (AC #2): `test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007` — fails pre-fix with `AssertionError: 'DEVIATION-1' not in CRITIQUE` (example-anchor literal absent until Phase 1 edit applies). Post-fix: PASS after Phase 1.
- **Row 3** (AC #3): `test_in_repo_and_installed_critique_agent_are_content_equal` — fails pre-fix with `AssertionError: in-repo critique.md hash != installed critique.md hash` (in-repo edited in Phase 1; installed not yet forward-synced). Post-fix: PASS after Phase 2 forward-sync. **Note**: this is the existing CAD-1 test (slice-007). It's currently PASSING (slice-008 ended byte-equal). It will go PASS → FAILING → PASSING across Phase 1 → Phase 2 of THIS slice. The TF-1 row entry distinguishes the temporary regression as the genuine WRITTEN-FAILING signal for this slice's AC #3.
- **Row 4** (AC #4): `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` — fails pre-fix with `AssertionError: '## v0.24.0' or 'CCC-1 v1.1' or 'design.md mechanical tables' not in changelog text` (entry doesn't exist pre-edit; substantive canonical phrase `design.md mechanical tables` pinned per Critic M3). Post-fix: PASS after Phase 3 changelog append (both in-repo + `~/.claude/`).
- **Row 5** (AC #5): `test_plugin_yaml_version_matches_version_file_at_0_24_0` — fails pre-fix with `AssertionError: plugin.yaml.version != '0.24.0' (currently '0.23.0')` (atomic bump not yet applied). Post-fix: PASS after Phase 4 atomic version bump.

Per slice-007 + slice-008 PMI-1 supersession pattern (per Critic M5 — slice-007 introduced `_at_0_22_0`; slice-008 first-superseded with `_at_0_23_0` = N=1 supersession event; slice-009 ratchets to N=2 supersession events on completion): the prior `test_plugin_yaml_version_matches_version_file_at_0_23_0` from slice-008 is **deleted** in the same commit that adds `_at_0_24_0` — no two version-gates coexist (the VERSION file is monotonic; running both gates would double-count). The supersession ACT is justified by slice-008 reflection's explicit choice + VERSION-file monotonicity invariant, NOT by N=2 supersession-event stability (slice-009 itself creates the N=2).

**TF-1 plan grew 6 → 7 rows at /critique** per M1 (location-pin guard for AC #1's new paragraph). Mission-brief had 6 rows; design.md narrowed to 6 (moved regression-guard to must-not-defer); /critique ratcheted to 7 (added location-pin row 1b). Slice-008 grew 5 → 7 → 9 across the same gates; slice-009 grew 6 → 6 → 7. Pattern: post-Critic TF-1 plan ratchets when Critic majors demand must-not-defer test rows.

## Phase plan (slice-006/007/008 bidirectional-sync N=3 stable pattern)

### Phase 0 — Bidirectional sha256 forensic capture (pre-edit baseline)

Capture in-repo + installed sha256 BEFORE any edits for forensic evidence (per N=4 stable lesson on out-of-repo edits):

- `agents/critique.md` (in-repo) AND `~/.claude/agents/critique.md` (installed) — currently byte-equal (slice-008 ended clean).
- `methodology-changelog.md` (in-repo) AND `~/.claude/methodology-changelog.md` (installed) — currently byte-equal.
- `VERSION` (in-repo) AND `~/.claude/ai-sdlc-VERSION` (installed) — currently byte-equal at "0.23.0".
- `plugin.yaml` (in-repo only) — version field currently "0.23.0".

Captured in `build-log.md` Phase 0.

### Phase 1 — In-repo canonical edits

- Edit `agents/critique.md` Dim 9 sub-clause 2 body (line 160) — append ~5 sentences per the refinement plan above.
- Add 2 new test functions to `tests/methodology/test_critique_agent.py`.
- Add `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` to `tests/methodology/test_methodology_changelog.py`.
- Replace `_at_0_23_0` with `_at_0_24_0` in same test file (single-function supersession).

### Phase 1b — Mid-slice smoke gate (per Critic m1)

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_critique_agent.py tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal -q
```

Expected:
- 13 existing `test_critique_agent.py` tests PASS unchanged (regression-safety).
- 3 new `test_critique_agent.py` tests PASS against in-repo `agents/critique.md` (Phase 1 edits applied) — `_covers_design_md_tables` + `_design_md_tables_paragraph_cites_slice_006_and_007` + `_sub_clause_2_body_contains_design_md_table_paragraph` (Critic M1 location-pin).
- 16 of 17 collected tests PASS.
- 1 test FAILS at this gate: `test_in_repo_and_installed_critique_agent_are_content_equal` (in-repo edited Phase 1; installed not yet forward-synced Phase 2). This is the **genuine WRITTEN-FAILING signal** for AC #3 row 3 — intentional per Critic m1.
- CAD-1 audit (`python -m tools.critique_agent_drift_audit`) reports `content-drift` exit 1 — **EXPECTED at this gate**, resolves at Phase 2 forward-sync.

If any existing test breaks: STOP per mission-brief mid-slice smoke gate guidance. Likely root cause: accidentally added a 6th sub-clause / removed cross-reference text / dropped Kiczales citation. Revert and refine inline.

### Phase 2 — Out-of-repo forward-sync

- Forward-sync `agents/critique.md` to `~/.claude/agents/critique.md` (Copy-Item).
- Capture in-repo + installed sha256 AFTER forward-sync.
- Verify byte-equality via `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exit 0.

### Phase 3 — Methodology changelog + bidirectional sync

- Append `## v0.24.0 — 2026-05-11` entry to in-repo `methodology-changelog.md`.
- Forward-sync to `~/.claude/methodology-changelog.md`.
- Capture in-repo + installed sha256 for `methodology-changelog.md`.
- Verify bidirectional content-equality via the new `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` (Phase 3 → PASS).

### Phase 4 — PMI-1 atomic version bump + final forensic capture

- Edit `VERSION` 0.23.0 → 0.24.0.
- Edit `~/.claude/ai-sdlc-VERSION` 0.23.0 → 0.24.0.
- Edit `plugin.yaml.version` 0.23.0 → 0.24.0.
- Capture in-repo + installed sha256 for all three files.
- Verify PMI-1 audit clean via `python -m tools.plugin_manifest_audit --root .` exit 0.
- Verify `test_plugin_yaml_version_matches_version_file_at_0_24_0` PASS.

### Phase 5 — Shippability catalog + final pre-finish gate

- Append row 9 to `architecture/shippability.md` (slice-009).
- Update row 8 (slice-008) Critical path text to note PMI-1 version-gate supersession at slice-009 (mirrors slice-008's row 7 update for slice-007).
- Run full methodology suite: `pytest tests/methodology/ -q` — expected clean.
- Run shippability catalog: 9 rows / N tests / N PASS in <2 min.
- Self-application BC-1 audit on slice-009's own mission-brief + design — expected `applicable: []` (negative anchors silence BC-PROJ-1 + BC-GLOBAL-1).

## Mid-slice smoke gate (refinement)

Confirmed in Phase 1b above (per Critic m1). Single command:

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_critique_agent.py tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal -q
```

Expected: 17 tests collected from the combined invocation; 13 existing `test_critique_agent.py` PASS unchanged; 3 new PASS post-Phase-1-edit (per Critic B1 + M1); 1 CAD-1 byte-equality test FAILS (genuine WRITTEN-FAILING for AC #3 row 3 — drift expected pre-Phase-2 forward-sync). CAD-1 standalone audit (`python -m tools.critique_agent_drift_audit`) reports exit 1 (drift expected pre-Phase-2).

## Pre-finish gate

(per mission-brief + design.md refinements)

- All 5 ACs PASS with evidence in `validation.md` (5 numbered AC test functions PASS; 1 regression-guard `_lists_five_sub_clauses` continues to PASS through Phases 1-4).
- **7 TF-1 rows** all PASSING (5 numbered-AC + 1 split-AC #1 location-pin per Critic M1 + 0 must-not-defer-driven at /design-slice; ratcheted 6 → 7 at /critique per M1).
- All must-not-defer items addressed (TF-1 genuineness; 5-sub-clause invariant; TWO-surface forward-sync atomicity; CCC-1 v1.1 changelog bidirectional pin; PMI-1 clean at 0.24.0; sha256 forensic capture across 5 file pairs; backward-compat on 13 existing tests; no methodology-suite regression; cross-reference structure preserved; shippability row 9; self-application clean).
- `/drift-check` passes.
- Mid-slice smoke still passes (no regression).
- No new TODOs / FIXMEs / debug prints.
- PMI-1 audit clean: `python -m tools.plugin_manifest_audit --root .` exits 0.
- CAD-1 audit clean at slice end: `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exits 0.
- Existing 13 `test_critique_agent.py` tests still pass; new 3 tests PASSING (per Critic B1 + M1).
- Methodology suite clean: `pytest tests/methodology/ -q` exits 0 (no regression on the broader suite).
- Shippability catalog 9 rows / clean pass under 2-minute target.
- Self-application: post-slice-009 BC-1 audit on THIS slice's own mission-brief.md + design.md returns `applicable: []` (BC-PROJ-1 + BC-GLOBAL-1 silenced by negative anchors `aggregated lessons`, `meta-discussion`, `vocabulary`, `back-sync`, `forward-sync`, `Dim 9`). Result captured in `build-log.md` Phase 4. Validates BC-1 v1.2's "validate using your own ship" pattern N=7 (slice-003..009 stable).
