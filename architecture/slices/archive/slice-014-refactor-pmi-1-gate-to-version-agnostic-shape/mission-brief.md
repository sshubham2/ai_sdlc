# Slice 014: refactor PMI-1 gate to version-agnostic shape

**Mode**: Standard
**Estimated work**: 0.5 day (~30-45 min skill scope per slice-013 reflection sizing)
**Risk retired**: Mechanical-feel friction at N=6 PMI-1 versioned-gate supersession events stable (slice-007 introduced `_at_0_22_0` → slice-008/009/010/011/012/013 superseded → currently `_at_0_28_0`). Per slice-013 reflection (corrected post-errata): **"the version-gate function exists-in-name-only feels increasingly mechanical at N=6"**. Refactor retires per-version-bump supersession churn permanently (1 min × every future slice → 0 min).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Refactor `tests/methodology/test_methodology_changelog.py`'s PMI-1 cleanliness gate from a per-version-bump shape (currently `test_plugin_yaml_version_matches_version_file_at_0_28_0` — version embedded in function name + three hardcoded `"0.28.0"` assertions) to a single **version-agnostic invariant test** that asserts only the cross-file equality `VERSION == plugin.yaml.version` (the actual PMI-1 invariant the gate exists to protect). After this slice ships, no future slice ever supersedes the PMI-1 gate function again — version-bumps update `VERSION` + `plugin.yaml.version` + `ai-sdlc-VERSION` and the gate test continues to pass without modification. The "did you bump at all?" discipline is preserved by methodology-changelog.md's entry-pin tests (per-version) + atomic-bump checklist in the mission brief (per-slice). The PMI-1 invariant is preserved by the cross-file equality assertion (which IS the defect class the slice-006 escape introduced).

## Acceptance criteria

1. `tests/methodology/test_methodology_changelog.py` contains a single version-agnostic PMI-1 gate function named `test_plugin_yaml_version_matches_version_file_invariant` with no `_at_0_NN_0` suffix and no hardcoded version literal anywhere in its body.
2. The version-agnostic gate asserts `VERSION` file content equals `plugin.yaml.version` (the cross-file equality invariant), and fails with a pinned error message naming "PMI-1" + "slice-006 escape" when violated.
3. The legacy `_at_0_NN_0`-shaped PMI-1 gate function is deleted (no `test_plugin_yaml_version_matches_version_file_at_0_28_0` and no `_at_0_27_0` etc. remain anywhere in the test file).
4. `methodology-changelog.md` v0.29.0 entry codifies the refactor as **PMI-1 v1.1** (or **PMI-2** if rule-ID convention prefers — design-slice picks) with: rationale (N=6 supersession events → mechanical friction); 3-surface canonical-phrase pin per N-surface schema-pin discipline at N=2 stable (RSAD-1 + EPGD-1); explicit "supersession pattern retired at slice-014" note replacing the running supersession-event counter language carried by entries v0.22.0..v0.28.0. ADR-013 records the refactor decision (reversibility class to be set at /design-slice; reverting requires re-introducing per-version supersession across every future slice, so likely **expensive with explicit irreversible portion** — the prose history loss in v0.22.0..v0.28.0 entries is structurally bounded if not edited).
5. Atomic version bump: `VERSION` (in-repo) + `plugin.yaml.version` + `~/.claude/ai-sdlc-VERSION` (installed) all bump 0.28.0 → 0.29.0. The version-agnostic gate from AC #1 passes post-bump WITHOUT any test code changes — empirical proof the refactor retires future supersession churn.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0): every AC maps to ≥1 failing test written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

Consolidated 7-row plan (post-/critique m3 ACCEPTED-FIXED — mission-brief amended to match design.md's authoritative shape so `tools/test_first_audit.py --strict-pre-finish` does not refuse on phantom rows referencing test functions that aren't actually built). Function names + AC mappings are canonical for the slice.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |
| 1 | AST meta-test | tests/methodology/test_methodology_changelog.py | test_pmi_1_gate_function_is_version_agnostic_shape | PASSING |
| 2 | unit (regression) | tests/methodology/test_methodology_changelog.py | test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge | PASSING |
| 3 | AST meta-test | tests/methodology/test_methodology_changelog.py | test_no_per_version_pmi_1_gate_functions_remain | PASSING |
| 4 | entry-pin + prose-pin (3-pin shape) | tests/methodology/test_methodology_changelog.py | test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed | PASSING |
| 4 | prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_29_0_entry_names_supersession_pattern_retired | PASSING |
| 4 | adr-pin | tests/methodology/test_methodology_changelog.py | test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase | PASSING |
| 5 | unit (post-bump re-pass, no code change) | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |

Notes:
- Row 1 covers AC #1 (gate exists with canonical name), AC #2 (cross-file equality invariant assertion path — though row 3 specifically exercises the FAILURE path), AND AC #5 (post-bump re-pass without code change is empirical proof). Post-bump re-pass is the SAME test function — not a separate row.
- Row 2 (`_is_version_agnostic_shape`) AST-walks `test_methodology_changelog.py`'s module looking for any `Constant(value=str)` matching `r"^\d+\.\d+\.\d+$"` inside `test_plugin_yaml_version_matches_version_file_invariant`'s `FunctionDef.body` and asserts NONE found. Structural pin against future regression back to hardcoded-literal shape.
- Row 3 (regression test) — see design.md "Regression test fixture spec" subsection for the pinned monkeypatch target string + tempdir fixture content + assertion order. Mission brief does not duplicate the fixture spec (design.md is authoritative per M2 ACCEPTED-FIXED).
- Row 4 (`_no_per_version_pmi_1_gate_functions_remain`) AST-walks the module looking for any `FunctionDef.name` matching `r"^test_plugin_yaml_version_matches_version_file_at_0_\d+_0$"` and asserts the list is EMPTY. Structural counter-anchor to the legacy shape.
- Row 5 is ONE function carrying the 3-pin shape (heading `## v0.29.0` + rule-ID `PMI-1 v1.1` + canonical phrase `version-agnostic PMI-1 cleanliness gate`) across BOTH in-repo + installed surfaces — single function reads both files, asserts 6 substrings total (3 pins x 2 surfaces). Mirrors the existing `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` shape (`test_methodology_changelog.py:368-430`).
- Row 6 is a separate prose-pin asserting the canonical phrase `supersession pattern retired at slice-014` is present in BOTH in-repo + installed surfaces. Distinct from row 5 because it pins a different canonical phrase (the supersession-retirement marker, NOT the rule's canonical phrase).
- Row 7 is the ADR-pin: asserts `architecture/decisions/ADR-013-*.md` glob matches exactly one file AND that file contains the canonical phrase `version-agnostic PMI-1 cleanliness gate`. Single assertion-cluster.

Out-of-scope (post-/critique m3 ACCEPTED-FIXED): mission brief no longer lists rows for `test_install_audit_ai_sdlc_version_atomic_with_in_repo` (mini-CAD-1 transition into INST-1 territory) — design-slice scope decision: `tools/install_audit.py` untouched.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Single version-agnostic PMI-1 gate function exists; no version literal in body | `grep -E "def test_plugin_yaml_version_matches_version_file" tests/methodology/test_methodology_changelog.py` returns EXACTLY one match, named `_invariant` (or design-slice-picked equivalent); rg `'0\.\d+\.0'` inside its body returns ZERO matches; row-2 AST meta-test PASSES |
| 2 | Cross-file equality invariant + pinned error message | Pytest run of `test_plugin_yaml_version_matches_version_file_invariant` PASSES; row-3 regression test (mismatched-tempdir fixture) PASSES with error-message substrings `"PMI-1"` + `"slice-006 escape"` asserted |
| 3 | Legacy `_at_0_NN_0` gate functions deleted | `grep -E "_at_0_\d+_0" tests/methodology/test_methodology_changelog.py` returns ZERO matches; row-4 AST meta-test PASSES |
| 4 | v0.29.0 changelog entry + ADR-013 + 3-surface canonical-phrase pin | `head architecture/decisions/ADR-013-*.md`; visual inspection of methodology-changelog.md v0.29.0 entry in both `~/.claude/methodology-changelog.md` and in-repo; rows 5-9 PASS; sha256 byte-equal capture pre/post edit per slice-005..013 bidirectional forensic capture N=9 stable |
| 5 | Atomic version bump + post-bump self-test | Cat `VERSION` + `plugin.yaml` (line: `version: 0.29.0`) + `~/.claude/ai-sdlc-VERSION` → all show `0.29.0`; `test_plugin_yaml_version_matches_version_file_invariant` PASSES at v0.29.0 WITHOUT any modification (vs. previous slices where the test had to be edited to encode the new version); install-audit + INST-2 cross-spec parity still PASS |

## Must-not-defer

- [ ] PMI-1 invariant cross-file equality assertion is the SOLE assertion in the version-agnostic gate (no hardcoded version literal sneaks back in via "extra safety" assertion)
- [ ] Pinned error message in the regression test (AC #2) names BOTH "PMI-1" and "slice-006 escape" — preserves the defect-class trace per slice-007 PMI-1 closure pattern
- [ ] AST meta-tests (rows 2 + 4) defend against future regressions back to per-version shape — these are the structural guards making the refactor durable
- [ ] Atomic version bump across ALL three surfaces (VERSION + plugin.yaml + ai-sdlc-VERSION) — slice-006 PMI-1 escape pattern must not recur even at the slice that refactors the gate
- [ ] EPGD-1 self-application: entry-pin functions for v0.22.0..v0.28.0 remain untouched after the gate Edit. The Edit narrow-scopes to ONLY the PMI-1 gate function + its dedicated `# --- PMI-1 cleanliness gate ---` SECTION header (now version-agnostic header text); does NOT span any entry-pin SECTION above
- [ ] Bidirectional sha256 forensic capture (N=9 → N=10 stable): pre-edit hash of `~/.claude/methodology-changelog.md` and in-repo `methodology-changelog.md` captured in build-log.md; post-edit byte-equality re-verified
- [ ] N-surface schema-pin discipline (N=2 instances stable → N=3 if applied here): canonical phrase for PMI-1 v1.1 / PMI-2 (design-slice picks the rule-ID) pinned across (1) ADR-013 + (2) in-repo methodology-changelog v0.29.0 entry + (3) installed methodology-changelog v0.29.0 entry. 3-surface shape per slice-013 stability ratchet
- [ ] Shippability catalog row at `architecture/shippability.md` (row 14): critical path = version-agnostic PMI-1 gate + 2 AST meta-tests + 1 regression test + bidirectional v0.29.0 entry-pin (3-pin shape) + PMI-1 0.29.0 atomicity
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] /drift-check passes after build
- [ ] Recursive-self-application discipline (RSAD-1, codified at slice-011 Dim 9 6th sub-clause): the slice refactoring PMI-1 must not itself violate PMI-1 at any intermediate state — version bump is the LAST step before final test run
- [ ] **META-1 invariant atomicity (post-/critique M1 ACCEPTED-FIXED)**: `test_version_matches_most_recent_changelog_entry` (`test_methodology_changelog.py:33`) asserts `VERSION` matches the latest `## v0.NN.0` heading in `methodology-changelog.md`. The slice's Phase 2 (atomic-commit) MUST package methodology-changelog v0.29.0 entry write + forward-sync to installed + VERSION bump + plugin.yaml.version bump + ai-sdlc-VERSION bump + ADR-013 write as a SINGLE atomic build operation — full test suite is NOT run between these steps. Naively writing the v0.29.0 changelog entry BEFORE the version bumps creates a META-1 transient breakage window (VERSION=0.28.0 while latest changelog heading=0.29.0); the reverse order creates the opposite breakage (VERSION=0.29.0 while latest changelog heading=0.28.0). See design.md "Phase plan" section for the canonical sequence.

## Out of scope

- Refactoring `tools/install_audit.py` to add an `ai-sdlc-VERSION == VERSION == plugin.yaml.version` 3-way invariant. The installed-copy version sync is INST-1 territory; in-scope here is purely the in-repo PMI-1 gate (`VERSION` ↔ `plugin.yaml.version`).
- Re-naming the rule-ID from PMI-1 to PMI-2. Default: keep PMI-1 + version-bump the entry to **v1.1**. If /design-slice picks PMI-2 (rule-naming-convention-break category from slice-010 Critic B5 / -T- suffix discipline), the change is bounded to the methodology-changelog entry's rule-ID label and a 1-line cross-reference in v0.19.0 PMI-1 entry; not a broader rename across audit modules.
- Touching entry-pin tests for v0.22.0..v0.28.0. Per EPGD-1 self-application discipline (slice-013 codification at Dim 9 7th sub-clause), entry pins persist across all versions; ONLY the PMI-1 versioned-gate is being refactored.
- Adding `tools/pmi_1_audit.py` as a standalone audit module. PMI-1 stays prose-pin-discipline-only (single test function in `test_methodology_changelog.py`). v2 candidate; defer until N≥2 PMI-1 escape recurrences post-refactor surface.
- Migrating PMI-1 to a stronger source-of-truth contract (e.g., methodology-changelog's latest "Versions" entry IS the source-of-truth, with plugin.yaml + VERSION derived). v3 candidate; structurally bigger refactor and not driven by slice-013 friction signal.

## Dependencies

- Prior slices: [[slice-007-add-critique-agent-content-equality-audit]] — slice-007 introduced PMI-1 cleanliness gate at `_at_0_22_0` (the shape being refactored); [[slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class]] — slice-013 codified EPGD-1 (entry-pin-vs-PMI-1-gate-semantics-conflation) which constrains the Edit narrow-scope discipline for the PMI-1 gate function this slice now refactors away
- Vault refs: [[methodology-changelog#v0.19.0 PMI-1]] (rule introduction); [[methodology-changelog#v0.22.0]] (first versioned-gate); [[components/test_methodology_changelog.py]]; [[architecture/decisions/ADR-013]] (to-be-written)
- Risk register: not driven by an R-N entry; driven by Aggregated lessons friction signal at slice-013 reflection (N=6 supersession events stable, mechanical-feel feedback)

## Mid-slice smoke gate

At ~50% of build (after writing the new `_invariant` test + 2 AST meta-tests but BEFORE the version bump or methodology-changelog edits), run:

```bash
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_function_is_version_agnostic_shape -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_no_per_version_pmi_1_gate_functions_remain -v
```

Expected at smoke gate: rows 1+2+3+4 all PASS (because by then the legacy `_at_0_28_0` is deleted, the new `_invariant` is written, both AST meta-tests find what they expect, and the regression test passes against current `VERSION == plugin.yaml.version == "0.28.0"`).

If fails: STOP, diagnose. Most likely cause: the Edit deleting `_at_0_28_0` accidentally pulled adjacent entry-pin SECTION content (EPGD-1 violation — exactly the class slice-013 codified). Re-verify the Edit narrow-scope before continuing.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes (every TF-1 row PASSING)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes after version bump + methodology-changelog edits (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full test suite passes
- [ ] Shippability catalog row 14 written + catalog re-run all PASS
- [ ] Bidirectional sha256 capture in build-log.md (Phase 0 + Phase 4) for `methodology-changelog.md` in both surfaces
- [ ] ADR-013 written with reversibility class + magnitude-of-revert justification per slice-010 ADR-009 pattern
