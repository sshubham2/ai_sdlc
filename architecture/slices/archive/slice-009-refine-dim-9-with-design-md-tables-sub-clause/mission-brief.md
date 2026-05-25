# Slice 009: refine-dim-9-with-design-md-tables-sub-clause

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: MEDIUM — closes the design.md-mechanical-tables-vs-canonical-inventories miss sub-class at promotion threshold N=2 (slice-006 DEVIATION-1 + DEVIATION-2 INST-1 canonical inventory drift + slice-007 Critic B1 in-repo `VERSION` → installed `ai-sdlc-VERSION` install-time rename mismatch). Reinforced empirically by slice-008 M1 (Wiegers AC-trace) and M2 (TWO-surface schema-pin discipline generalization to N-surface). The current Dim 9 "Tooling-doc-vs-implementation parity" sub-clause cross-references the Dim 1 surgical sub-bullet which covers SOURCE-CODE-LEVEL drift (tool docstring vs regex/parser/keyword-list); it does NOT cover DESIGN-DOC-LEVEL drift (design.md mechanical tables vs methodology canonical inventories / install-time renames). Slice-009 extends the Dim 9 sub-clause body inline with the design-doc-level case, keeping the Dim 1 surgical bullet narrow (source-code-level) and the cross-reference structure intact.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Extend `agents/critique.md` Dimension 9's "Tooling-doc-vs-implementation parity" sub-clause body with a new paragraph covering "design.md mechanical tables vs methodology canonical inventories / install-time renames", grounded in two concrete cross-slice examples (slice-006 INST-1 canonical inventory drift + slice-007 install-time rename mismatch). This is a **refinement** of the existing sub-clause body — NOT a new 6th sub-clause — preserving the 5-sub-clause structural invariant pinned by `test_critique_dim_9_lists_five_sub_clauses`. The refinement gives the Critic a single Dim 9 retrieval surface to ask: "when this slice's design.md contains a mechanical table (forward-sync targets, prerequisites, dependencies, install-time renames), does each row match the canonical reference for that domain (INST-1 `_CANONICAL_*` inventories, `methodology-changelog.md` install-time conventions, etc.)?" Per slice-007 reflection's explicit promotion language ("Refine Dim 9 sub-clause 'Tooling-doc-vs-implementation parity' to include 'design.md mechanical tables vs methodology canonical references / install-time renames'"). Authored as **CCC-1 v1.1** in `methodology-changelog.md` per BC-1's versioning convention.

## Acceptance criteria

1. After this slice ships, `agents/critique.md` Dimension 9 sub-clause "Tooling-doc-vs-implementation parity" body contains a new design-doc-level paragraph that names: (a) the canonical literal substring `design.md mechanical tables`, (b) the canonical literal substring `canonical inventor` (matches both `inventory` / `inventories`), (c) the canonical literal substring `install-time rename`. The 5-sub-clause structural invariant is preserved (`test_critique_dim_9_lists_five_sub_clauses` continues to PASS unchanged — Dim 9 still enumerates exactly 5 sub-clauses).
2. After this slice ships, the new paragraph carries TWO concrete cross-slice examples grounded in the project's reflection record: slice-006 (DEVIATION-1: `plugin.yaml` on INST-1 do-not-copy list mistakenly listed in design.md forward-sync table; DEVIATION-2: `ai-sdlc-VERSION` missed from design.md forward-sync table despite being an INST-1 installed metadata file) AND slice-007 (Critic B1: design.md "Out-of-repo files touched" table named in-repo file `ai-sdlc-VERSION` instead of `VERSION` — install-time rename mismatch). Both example pins are case-sensitive literal substrings.
3. After this slice ships, `python -m tools.critique_agent_drift_audit` from project root exits 0 (sha256 byte-equality holds between in-repo `agents/critique.md` and `~/.claude/agents/critique.md`). The CAD-1 audit confirms forward-sync atomicity at slice end.
4. After this slice ships, `methodology-changelog.md` (BOTH in-repo at `architecture/../methodology-changelog.md` AND installed at `~/.claude/methodology-changelog.md`) contains a new `## v0.24.0 — <YYYY-MM-DD>` entry naming **CCC-1 v1.1** as the refinement rule reference (mirrors BC-1 v1.1 → v1.2 versioning convention from slice-005 → slice-008). The entry's Validation section names this slice's new test (`test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables`) and the bidirectional changelog-pin test (`test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed`).
5. PMI-1 invariant atomic post-build: `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml.version` all equal `0.24.0`. Verified via `python -m tools.plugin_manifest_audit --root .` exit 0 AND `test_plugin_yaml_version_matches_version_file_at_0_24_0` PASSING (supersedes slice-008's `_at_0_23_0` PMI-1 versioned-gate per the N=2-stable supersession pattern from slice-007 + slice-008).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007 | PASSING |
| 3 | integration | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_at_0_24_0 | PASSING |

**Notes**:
- TF-1 PENDING -> WRITTEN-FAILING transitions MUST be genuine per slice-003..008 lesson. Pin specific failure signals:
  - AC #1 first row fails pre-fix with `AssertionError: 'design.md mechanical tables' not in CRITIQUE` (canonical literal not yet present in Dim 9 body).
  - AC #1 second row (the existing `_lists_five_sub_clauses`) MUST continue to PASS — it acts as a regression-guard against accidentally adding a 6th sub-clause. PENDING here means "test exists, runs, and must remain green through the refinement"; transition to PASSING after Phase 2 forward-sync.
  - AC #2 fails pre-fix with `AssertionError: 'slice-006' not in CRITIQUE` OR `'DEVIATION-1' not in CRITIQUE` (concrete cross-slice examples not present).
  - AC #3 fails pre-fix with `RuntimeError: sha256 mismatch` (in-repo edited; installed not yet forward-synced).
  - AC #4 fails pre-fix because v0.24.0 entry doesn't exist yet (either file).
  - AC #5 fails pre-fix because `plugin.yaml.version` and `VERSION` are still `0.23.0` (slice-008's bumped state).
- Per slice-007 + slice-008 PMI-1 versioned-gate pattern (slice-007 introduced `_at_0_22_0`; slice-008 first-superseded with `_at_0_23_0` = N=1 supersession event); slice-009 ratchets to N=2 supersession events on completion (per Critic M5). The supersession ACT itself is justified by slice-008 reflection's explicit choice + the in-repo VERSION file's monotonicity invariant — NOT by N=2 stability of supersession-events (slice-009 itself creates the N=2). Delete old `_at_0_23_0` test row; add new `_at_0_24_0`. No two version-gates coexist.
- TF-1 plan starts at 6 rows. May grow at /design-slice (Critic majors typically generate additional must-not-defer rows; slice-008 grew 5→7→9 across mission-brief → design → post-Critic).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Dim 9 sub-clause body extended with 3 canonical substrings | `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables` PASS; `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_lists_five_sub_clauses` PASS (regression-guard for 5-sub-clause structural invariant) |
| 2 | Two concrete cross-slice examples present | `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007` PASS; asserts canonical substrings `slice-006`, `DEVIATION-1`, `DEVIATION-2`, `slice-007`, `ai-sdlc-VERSION` (install-time rename anchor) all present |
| 3 | CAD-1 byte-equality audit clean | `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exits 0; `pytest tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` PASS |
| 4 | v0.24.0 CCC-1 v1.1 entry pinned bidirectionally | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo_and_installed` PASS; asserts in-repo `methodology-changelog.md` AND `~/.claude/methodology-changelog.md` both contain `## v0.24.0 —`, `CCC-1 v1.1`, and the canonical rule-name substring chosen at /design-slice |
| 5 | PMI-1 atomic at 0.24.0 | `python -m tools.plugin_manifest_audit --root .` exits 0; `pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_at_0_24_0` PASS; slice-008's `_at_0_23_0` test removed in the same commit (no two version-gates coexist per PMI-1 supersession pattern) |

## Must-not-defer

- [ ] TF-1 PENDING -> WRITTEN-FAILING genuine transitions per slice-003..008 lesson N=5 stable. Pin specific failure signals (substring absent, sha256 mismatch, version mismatch); no coincidental passes.
- [ ] 5-sub-clause structural invariant preserved. The slice REFINES the existing Tooling-doc-vs-impl parity sub-clause body — does NOT add a 6th sub-clause to Dim 9. `test_critique_dim_9_lists_five_sub_clauses` MUST continue to PASS unchanged at every gate (mid-slice smoke + pre-finish). Any temptation to "add a new sub-clause" is a design-stage red flag — refuse and refine inline.
- [ ] TWO-surface schema-pin discipline atomically: changes to `agents/critique.md` AND `~/.claude/agents/critique.md` ship in the same slice. The two files are bidirectionally synced via CAD-1 byte-equality audit (slice-007 ground; sha256 forensic capture per slice-006/007/008 N=3 stable lesson).
- [ ] CCC-1 v1.1 entry appended to `methodology-changelog.md` (in-repo) AND `~/.claude/methodology-changelog.md` atomically. Per slice-007 PMI-1 escape closure lesson: claim made in `## Vault updates made` MUST be verifiable by audit (`tools.plugin_manifest_audit` + `tools.critique_agent_drift_audit`).
- [ ] PMI-1 audit clean post-build (`python -m tools.plugin_manifest_audit --root .` exits 0). Atomic version bump: `VERSION` + `ai-sdlc-VERSION` + `plugin.yaml.version` all to `0.24.0`. Slice-008's `_at_0_23_0` PMI-1 versioned-gate test replaced (NOT additive) by `_at_0_24_0` per N=2-stable supersession pattern from slice-007 + slice-008.
- [ ] Bidirectional sha256 forensic capture in `build-log.md` for `~/.claude/agents/critique.md` + `~/.claude/methodology-changelog.md` + `~/.claude/ai-sdlc-VERSION` (Phase 0 + Phase 4 pattern, N=3 stable lesson per slice-006 + slice-007 + slice-008). Capture in-repo + installed sha256 BEFORE and AFTER the edits. Slice's git diff alone is insufficient evidence for out-of-repo edits.
- [ ] Backward-compat covenant: the existing 13 tests in `tests/methodology/test_critique_agent.py` continue to PASS unchanged (per Critic B1 — actual count verified via `grep -c '^def test_' tests/methodology/test_critique_agent.py`). The slice adds 2 new tests (+ 1 location-pin per Critic M1 = 3 new total); it MUST NOT modify or delete any existing test (except the version-gate supersession in `test_methodology_changelog.py`).
- [ ] No regression on the broader methodology suite (`pytest tests/methodology/ -q` clean). The slice's surface is narrow (prompt-prose refinement + changelog entry + version bump); broader breakage indicates an unintended scope creep.
- [ ] Cross-reference structure preserved: Dim 9 sub-clause 2's "see Dimension 1 sub-bullet — Verify by reading the implementation" cross-reference text is NOT removed or weakened. The new design-doc-level paragraph is ADDITIVE to the existing source-code-level cross-reference, not a replacement. Verified by `test_critique_dim_9_cross_references_resolve` continuing to PASS unchanged.
- [ ] Shippability catalog row 9 added at `architecture/shippability.md` naming this slice's critical path (Dim 9 refinement + CAD-1 byte-equality on agents/critique.md + v0.24.0 entry + PMI-1 0.24.0 invariant). Slice-007 PMI-1 versioned-gate supersession example: row N's command lists the CURRENT-version PMI-1 gate, not the obsoleted prior version.
- [ ] Self-application check: this slice's own mission-brief.md + design.md mention BC-1 false-positive anchors (`Dim 9`, `back-sync`, `forward-sync`, `aggregated lessons`, `meta-discussion`, `vocabulary`); BC-1 v1.2's negative-anchor mechanism (slice-008) MUST silence BC-PROJ-1 + BC-GLOBAL-1 cleanly without manual defer-with-rationale. Validates BC-1 v1.2's "validate using your own ship" pattern N=6 + closes the noise loop at slice-009. Self-application result captured in `build-log.md`.

## Out of scope

- **Adding a NEW 6th sub-clause to Dim 9** — explicitly out of scope. The slice REFINES the existing Tooling-doc-vs-impl parity sub-clause body inline (slice-007 reflection lesson framing). A 6th sub-clause would break the 5-sub-clause structural invariant and is the wrong intervention level for this miss class.
- **Wiegers AC-trace sub-class promotion (slice-008 M1, N=1)** — defer to slice-010+ at N=2. The N=1 evidence is insufficient per BC-1's promotion convention.
- **BC-PROJ-2 negative-anchor migration (N=1 at slice-008)** — defer to slice-010+ at N=2 per slice-008 reflection.
- **`refactor-pmi-1-gate-to-version-agnostic-shape`** — no version-bump churn friction yet (N=2 supersessions only); defer indefinitely until N≥4 friction surfaces.
- **INST-2 generalization** (general content-equality across all installed files) — slice-007 carryover; still N=1 evidence; defer to N=2 (drift on `agents/critique-review.md`, `agents/critic-calibrate.md`, or `~/.claude/build-checks.md`).
- **R-1 deeper fix for /diagnose cwd-mismatch** — risk-register HIGH-band open; documented-constraint workaround acceptable per slice-002; needs `/risk-spike` first to disambiguate cwd vs parallel-spawn-cascade hypotheses.
- **`fix-bc-1-archived-slice-heuristic`** — slice-005 carryover; --changed-files workaround acceptable; this slice's verification uses prose-substring greps + audits that don't depend on the heuristic.
- **`add-csp-1-docstring-or-regex`** — slice-005 carryover sibling tooling-bug pattern; not at promotion threshold; defer.
- **Refining Dim 1's surgical sub-bullet body** — the design-doc-level case lives in Dim 9 (cross-cutting view) per slice-006 + slice-007 reflection framing; Dim 1's source-code-level sub-bullet stays narrow as designed. Cross-reference structure (Dim 9 → Dim 1) preserved unchanged.
- **Promoting voluntary-Critic-on-cross-cutting-tooling to /slice default heuristic (N=8/8)** — separate methodology-doc slice; out of scope here.
- **Promoting "ZERO build-deviation slice via strong /critique" tracking-as-metric (N=1)** — defer to N=2 per slice-008 lesson.
- **Em-dash → cp1252 / prose-pin substring uniqueness migration** — both N=1; watch.

## Dependencies

- Prior slices: [[slice-006-update-critic-with-cross-cutting-conformance-dimension]] — Dim 9 baseline (CCC-1 v1; the 5 sub-clauses this slice refines without expanding); [[slice-007-add-critique-agent-content-equality-audit]] — CAD-1 byte-equality audit + skill-prose forward-sync ground; [[slice-008-refine-bc-1-anchors-with-negative-context]] — BC-1 v1.2 negative-anchor mechanism that silences methodology-vocabulary false positives on this slice's own ship; PMI-1 supersession pattern.
- Vault refs: [[agents/critique.md]] Dimension 9 body lines 152-166; [[decisions/ADR-005-add-cross-cutting-conformance-9th-critic-dimension]] (CCC-1 v1; this slice's refinement to v1.1 is additive to ADR-005, not superseding); [[architecture/critic-calibration-log.md]] 2026-05-10 calibration run + user-override + the slice-009 success-criterion data point (cross-cutting miss rate at slice-009 vs ≤2-across-slices-6-15 target); [[methodology-changelog.md]] v0.21.0 (CCC-1) + upcoming v0.24.0 (CCC-1 v1.1) entry.
- Risk register: none (slice doesn't retire R-1 or R-2; both are /diagnose-related).
- Tooling: `agents/critique.md` (Dim 9 sub-clause body refinement); `~/.claude/agents/critique.md` (Phase 2 forward-sync target); `methodology-changelog.md` + `~/.claude/methodology-changelog.md` (v0.24.0 entry); `VERSION` + `~/.claude/ai-sdlc-VERSION` (atomic bump to 0.24.0); `plugin.yaml` (version field bump); `tests/methodology/test_critique_agent.py` (extend from 13 → 16 tests — 2 substring tests for AC #1 + AC #2; 1 location-pin per Critic M1); `tests/methodology/test_methodology_changelog.py` (replace `_at_0_23_0` with `_at_0_24_0`; add `_v_0_24_0_ccc_1_v_1_1_entry` bidirectional pin); `architecture/shippability.md` (add row 9). No code-tooling logic changes (no `.py` audit module modified); the slice is a prompt-prose refinement.

## Mid-slice smoke gate

At ~50% of build (after `agents/critique.md` is edited in-repo and the 2 new test functions are added, but BEFORE Phase 2 forward-sync to `~/.claude/agents/critique.md`):

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_critique_agent.py -q
```

Expected: All 16 tests run; the 3 new tests (`test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables` + `test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007` + `test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph` per Critic M1) PASS against in-repo (because in-repo is edited); the 13 existing tests PASS unchanged. CAD-1 drift audit (`python -m tools.critique_agent_drift_audit`) reports `content-drift` exit 1 (in-repo edited; installed not yet forward-synced) — this is EXPECTED at this gate; CAD-1 must report clean exit 0 only at pre-finish gate after Phase 2 forward-sync.

If any of the 13 existing tests breaks (especially `test_critique_dim_9_lists_five_sub_clauses` or `test_critique_dim_9_cross_references_resolve`): STOP, diagnose. Likely root causes:
- Accidentally added a 6th sub-clause to Dim 9 — refine inline instead.
- Removed or weakened a Dim 9 → Dim 1 cross-reference text — re-add.
- Edited a Dim 1 sub-bullet or Dim 4 sub-bullet body that broke the cross-reference target — revert; refine only Dim 9.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (TF-1 genuineness, 5-sub-clause invariant, TWO-surface pin, CCC-1 v1.1 changelog entry, PMI-1 clean at 0.24.0, sha256 forensic capture, backward-compat on 11 existing tests, no methodology-suite regression, cross-reference structure preserved, shippability row 9, self-application clean)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 audit clean: `python -m tools.plugin_manifest_audit --root .` exits 0
- [ ] CAD-1 audit clean at slice end: `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exits 0
- [ ] Existing 13 `test_critique_agent.py` tests still pass; new 3 tests PASSING (per Critic B1 + M1)
- [ ] Methodology suite clean: `<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/ -q` exits 0 (no regression on the broader suite)
- [ ] Shippability catalog clean: row 9 added; row 8's slice-008 reference updated to note slice-009 supersession of the PMI-1 versioned-gate (mirrors slice-008's row 7 update for slice-007's v0.22.0 gate)
- [ ] Self-application check: post-slice-009 BC-1 audit on THIS slice's own mission-brief.md + design.md does NOT fire BC-PROJ-1 or BC-GLOBAL-1 (negative-anchor mechanism silences them; closes the noise loop on the slice's own ship). Result captured in `build-log.md` Phase 4.
