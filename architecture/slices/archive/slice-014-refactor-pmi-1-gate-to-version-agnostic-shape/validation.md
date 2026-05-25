# Validation: Slice 014 refactor-pmi-1-gate-to-version-agnostic-shape

**Date**: 2026-05-13
**Result**: PASS

**Real-environment note**: Slice-014 is a methodology-internal refactor — no UI, no device, no external user surface. The "real environment" for this slice IS the actual file system (real `tests/methodology/test_methodology_changelog.py` + real `methodology-changelog.md` in-repo + installed + real `VERSION` / `plugin.yaml` / `ai-sdlc-VERSION`) running the actual pytest suite. Evidence = pytest outputs against real files + grep verification of structural invariants + sha256 byte-equality of bidirectional surfaces. No mocks at the system boundary; the gate function reads the actual VERSION + plugin.yaml files on disk at runtime. This is the "real environment" the validate-slice skill requires for methodology-tooling slices.

## Per-criterion results

### AC #1: single version-agnostic gate function with no `_at_0_NN_0` suffix and no hardcoded version literal in body

- **Status**: PASS
- **Evidence**:
  - `grep -nE "^def test_plugin_yaml_version_matches_version_file" tests/methodology/test_methodology_changelog.py` returns EXACTLY ONE line:
    ```
    541:def test_plugin_yaml_version_matches_version_file_invariant():
    ```
  - Grep for `r"\d+\.\d+\.\d+"` pattern inside gate body (lines 541-575): **ZERO occurrences** in body — version-agnostic shape confirmed.
  - `test_pmi_1_gate_function_is_version_agnostic_shape` (AST meta-test): **PASSES** in 0.04s. Walks the module's AST, locates the `_invariant` FunctionDef, walks body for any `Constant(value=str)` matching `r"^\d+\.\d+\.\d+$"`, asserts NONE found. Empirically PASSES against the actual built test file.
- **Notes**: AC #1 has 3-layer defense — (a) the function exists with the canonical name, (b) no version literal in its body, (c) AST meta-test pins this against future regression.

### AC #2: cross-file equality invariant + pinned error message naming "PMI-1" + "slice-006 escape"

- **Status**: PASS
- **Evidence**:
  - `test_plugin_yaml_version_matches_version_file_invariant` (the invariant test): **PASSES** in 0.04s. Reads real `VERSION` (0.29.0) and real `plugin.yaml` (version: 0.29.0), asserts cross-file equality.
  - `test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge` (regression test): **PASSES** in 0.05s. Exercises the FAILURE path with `tmp_path` + `monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)` — writes mismatched `VERSION` (1.2.3) and `plugin.yaml` (version: 4.5.6) to tempdir, invokes the gate, asserts `AssertionError` raises with both `"PMI-1"` and `"slice-006 escape"` substrings present in the message.
  - Independent per-substring assertions (not joined by `and`) — failure mode would clearly distinguish which substring was missing if regression were ever triggered.
- **Notes**: Object-form monkeypatch via `sys.modules[__name__]` per slice-014 build-time DEVIATION-1 (pytest namespace-package import-mode root cause).

### AC #3: legacy `_at_0_NN_0`-shaped PMI-1 gate function deleted

- **Status**: PASS
- **Evidence**:
  - `grep -nE "_at_0_[0-9]+_0" tests/methodology/test_methodology_changelog.py` returns ONLY prose mentions (lines 506, 630) inside docstrings — NOT FunctionDefs. Specifically: line 506 is inside `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed`'s docstring referencing the historical supersession pattern; line 630 is inside `test_no_per_version_pmi_1_gate_functions_remain`'s docstring giving the example regression class (`test_..._at_0_30_0`).
  - `test_no_per_version_pmi_1_gate_functions_remain` (AST meta-test): **PASSES** in 0.04s. AST-walks the module looking for any `FunctionDef.name` matching `r"^test_plugin_yaml_version_matches_version_file_at_0_\d+_0$"`, asserts the list is EMPTY. Correctly distinguishes function definitions from docstring prose.
- **Notes**: AST meta-test's stricter pattern (anchored `^...$`) is the structural defense; raw-grep on the test file can produce noise from documentation comments which is expected and acceptable.

### AC #4: methodology-changelog v0.29.0 entry codifies PMI-1 v1.1 + 3-surface canonical-phrase pin + ADR-013

- **Status**: PASS
- **Evidence**:
  - **Surface 1 (ADR-013)**: `architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md` exists; canonical phrase `version-agnostic PMI-1 cleanliness gate` appears **3 times** (title + body classification + ADR text).
  - **Surface 2 (in-repo `methodology-changelog.md`)**: v0.29.0 heading at line 37; canonical phrase appears **2 times**; `PMI-1 v1.1` rule-ID appears **8 times** across the entry; explicit `supersession pattern retired at slice-014` marker appears **1 time** (per slice-014's new prose-pin test discipline).
  - **Surface 3 (installed `~/.claude/methodology-changelog.md`)**: v0.29.0 heading at line 37; canonical phrase appears **2 times**; supersession-retired marker appears **1 time**. Byte-equal with in-repo at sha256 `7aa14cf5604d3f114d01780b13225d950744817dabe450a162adf1556aa0e9f1`.
  - All 3 AC #4 tests PASS in 0.05s aggregate:
    - `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` — 3-pin shape across both surfaces (heading + rule-ID + canonical phrase × 2 surfaces = 6 substring assertions; all PASS)
    - `test_v_0_29_0_entry_names_supersession_pattern_retired` — supersession-retired marker phrase pinned across both surfaces (2 substring assertions; all PASS)
    - `test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase` — ADR-013 glob matches exactly one file + canonical phrase asserted
- **Notes**: N-surface schema-pin 3-surface shape ratchets from **N=2 instances stable** (RSAD-1 v0.26.0 + EPGD-1 v0.28.0) to **N=3 instances stable** at slice-014 (PMI-1-v1.1 v0.29.0). The 3-surface-pin makes drift impossible without breaking ≥2 tests simultaneously per the design.md `## N-surface schema-pin discipline` section.

### AC #5: atomic version bump 0.28.0 → 0.29.0 across all three surfaces + post-bump self-test PASSES without code change

- **Status**: PASS
- **Evidence**:
  - `cat VERSION` → `0.29.0`
  - `grep "^version:" plugin.yaml` → `version: 0.29.0  # synced with VERSION file (PMI-1 audit enforces)`
  - `cat ~/.claude/ai-sdlc-VERSION` → `0.29.0`
  - **Post-bump self-test**: `test_plugin_yaml_version_matches_version_file_invariant` (the SAME function from AC #1) PASSES at the bumped version 0.29.0 WITHOUT any modification to the test function body since Phase 1c — empirical proof the refactor retires future per-version-bump supersession churn. The gate function reads CURRENT real `VERSION` and `plugin.yaml`, computes equality, returns clean.
  - **META-1 invariant cross-check**: `test_version_matches_most_recent_changelog_entry` PASSES — verifies `VERSION` matches the latest `## v0.NN.0` heading in `methodology-changelog.md`. Confirms META-1 atomicity preserved across slice-014's Phase 2 single atomic commit per /critique M1 ACCEPTED-FIXED discipline.
  - **PMI-1 plugin_manifest_audit**: `PMI-1 plugin manifest audit: clean. 24 skill(s), 5 agent(s), 15 tool(s); version 0.29.0.`
  - **INST-1 install_audit**: `INST-1 install audit: clean. 24/24 skills, 5/5 agents, 4/4 templates, 15/15 tool modules; methodology v0.29.0.`
- **Notes**: This is the empirical retirement-proof of the PMI-1 versioned-gate supersession-event counter. At slice-013 the gate was `_at_0_28_0` (per-version literal pin); at slice-014 it's `_invariant` (version-agnostic). The atomic bump 0.28.0 → 0.29.0 succeeded WITHOUT any test code change — first such bump under PMI-1 v1.1.

## Multi-instance validation

**Required?**: no — slice-014 is methodology-internal tooling; no users, no devices, no sharing/sync/collaboration features.

**Result**: not-applicable

## VAL-1 layered safety checks (Step 5b)

- **Layer A (Credential scan)**: 0 secrets found. CLEAN.
- **Layer B (Dependency hallucination check)**: 0 import findings. CLEAN.
- **Suppressed (allowlisted)**: 0 (intra-repo `tests` package handled via `--imports-allowlist tests` per VAL-1 Layer B canonical handling; N=11 → **N=12 cumulative recurrence** of the false-positive class — handled cleanly).

```
VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).
Clean — both layers passed.
```

## WS-1 / ETC-1 audits (Steps 5c + 5d)

- **WS-1 walking_skeleton_audit**: not-enabled. `**Walking-skeleton**: false` in mission-brief. Silent-skip per WS-1 default-off semantics.
- **ETC-1 exploratory_charter_audit**: not-enabled. `**Exploratory-charter**: false` in mission-brief. Silent-skip per ETC-1 default-off semantics.

## Shippability catalog regression check (Step 5.5)

**Result**: 14/14 PASS (no regressions introduced by slice-014)

Aggregate: **114 underlying tests across 14 rows in ~8.5s** (well under the catalog's <2-min target).

| Row | Slice | Critical-path tests | Runtime |
|-----|-------|--------------------|---------| 
| 1 | slice-001-diagnose-orchestration-fix | 30 PASS | 1.84s |
| 2 | slice-002-fix-diagnose-contract-and-cwd-mismatch | 4 PASS | 0.37s |
| 3 | slice-003-add-val-1-imports-allowlist | 3 PASS | 0.55s |
| 4 | slice-004-fix-rr1-audit-docstring-or-regex | 4 PASS | 0.39s |
| 5 | slice-005-add-bc-1-keyword-precision | 5 PASS | 0.42s |
| 6 | slice-006-update-critic-with-cross-cutting-conformance-dimension | 8 PASS | 0.38s |
| 7 | slice-007-add-critique-agent-content-equality-audit | 7 PASS | 1.15s |
| 8 | slice-008-refine-bc-1-anchors-with-negative-context | 10 PASS | 0.49s |
| 9 | slice-009-refine-dim-9-with-design-md-tables-sub-clause | 5 PASS | 0.51s |
| 10 | slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic | 7 PASS | 0.40s |
| 11 | slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose | 7 PASS | 0.50s |
| 12 | slice-012-bc-proj-2-negative-anchor-migration | 5 PASS | 0.42s |
| 13 | slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class | 9 PASS | 0.52s |
| 14 | slice-014-refactor-pmi-1-gate-to-version-agnostic-shape | 7 PASS | 0.42s |

Row 13's pytest command was updated at slice-014 Phase 4 to reference `test_plugin_yaml_version_matches_version_file_invariant` (replacing the deleted `_at_0_28_0`) — consumer-reference propagation per slice-013's N=1 watch-list class generic methodology lesson. **N=2 promotion threshold MET** for `shippability-catalog-consumer-reference-propagation-after-PMI-1-structural-invariant-supersession` — promote to Dim 9 sub-class refinement at slice-015. Caught proactively at slice-014 Phase 4 (vs slice-013 caught reactively at /validate-slice Step 5.5) by applying the slice-013 generic methodology lesson during /build-slice.

## Reality surprises

- **DEVIATION-1 surfaced at slice-014 Phase 1d** (build-time, not validate-time — already captured in build-log.md): `monkeypatch.setattr` dotted-string-form does NOT take effect on the running pytest test module when `tests/` is a namespace package without `__init__.py`. Pytest's import-mode places the running module under `methodology.test_methodology_changelog` (bare key), while the dotted-string `tests.methodology.test_methodology_changelog` fetches a separate importlib copy. /critique M2 + /critique-review M-add-1 came close but didn't anticipate the namespace-package interaction. Fix: object form `monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)`. **No new surprises at /validate-slice — DEVIATION-1 was already captured at /build-slice and its mitigation is the canonical regression test fixture spec moving forward.**

- **Slice-013 N=1 watch-list class N=2 promotion threshold MET (proactive catch at slice-014 /build-slice Phase 4)**: `shippability-catalog-consumer-reference-propagation-after-PMI-1-structural-invariant-supersession`. Already captured in build-log.md. **No new surprises at /validate-slice — caught at build, propagated at build.**

## Per-criterion summary

| AC | Status | Real-env evidence |
|----|--------|------------------|
| 1 | PASS | Single `_invariant` function exists; AST meta-test confirms zero version literals in body |
| 2 | PASS | Invariant test PASSES against real VERSION + plugin.yaml; regression test PASSES with pinned "PMI-1" + "slice-006 escape" substrings on per-substring asserts |
| 3 | PASS | AST meta-test confirms zero `_at_0_NN_0`-shaped FunctionDefs; docstring prose mentions correctly excluded |
| 4 | PASS | Canonical phrase pinned across N=3 surfaces (ADR-013 + in-repo + installed); 3 AC #4 tests + entry-pin + supersession-retired marker + ADR-pin all PASS |
| 5 | PASS | VERSION = plugin.yaml.version = ai-sdlc-VERSION = 0.29.0; `_invariant` PASSES post-bump with zero code change since Phase 1c (empirical retirement-proof); META-1 invariant preserved; PMI-1 + INST-1 audits clean at v0.29.0 |

**All 5 ACs PASS with concrete real-environment evidence. No PARTIAL, no FAIL. No new reality surprises beyond those already captured at /build-slice. Shippability catalog 14/14 PASS — no regressions. Proceeding to /reflect.**
