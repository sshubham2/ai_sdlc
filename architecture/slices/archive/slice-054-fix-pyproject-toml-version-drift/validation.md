# Validation: Slice 054 fix-pyproject-toml-version-drift

**Date**: 2026-05-21
**Result**: PASS

## Per-criterion results

### AC1: `pyproject.toml` `[project].version` literal equals trimmed contents of `VERSION`

- **Status**: PASS
- **Evidence**:
  - Real `VERSION` file content: `0.62.0`
  - Real `pyproject.toml` line 20: `version = "0.62.0"`
  - `$PY -m pytest tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file -v` → `1 passed in 0.04s`
  - Pre-fix (BFRD-1 /repro WRITTEN-FAILING evidence): `'0.20.0' == '0.61.0'` AssertionError on initial run; non-tautological FAIL→PASS contrast confirmed at slice-054 /build-slice Phase B mid-slice smoke gate.
- **Notes**: PVFS-1 invariant verified on the actual files; mirrors PMI-1's plugin.yaml↔VERSION gate pattern (verified independently by `PMI-1 plugin manifest audit: clean. … version 0.62.0`).

### AC2: Shippability row #54 PASSES under the SRSC-1 runner

- **Status**: PASS
- **Evidence**:
  - `$PY -m tools.shippability_runner architecture/shippability.md` → `Shippability catalog run: 54 row(s), 54 PASS, 0 FAIL`
  - Row #54 cites 4 pytests (AC1 repro + AC3 stale-literal pin + 2 entry-pin tests for v0.62.0 + BCR-1 input-contract); all 4 PASS within the runner.
  - SCMD-1 pre-gate: `clean. 54 row(s); 515 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=513.`
  - PTFCD-1 pre-gate: `clean. 54 row(s), 303 test-path token(s) — all files and cited functions exist.`
- **Notes**: Closes the SC-001 ungated stale-pip-artifact class structurally — a future `pyproject.toml [project].version` drift will FAIL the catalog runner at row #54, blocking /validate-slice.

### AC3: `pyproject.toml` carries no stale `0.20.0` / `13 audit modules` / `13 tool modules` literals

- **Status**: PASS
- **Evidence**:
  - `Select-String -Path pyproject.toml -Pattern '0\.20\.0|13 audit|13 tool' -AllMatches` → no matches.
  - `$PY -m pytest tests/methodology/test_pyproject_version_matches_version_file.py::test_pyproject_has_no_stale_0_20_0_or_count_literals -v` → `1 passed in 0.04s`
  - 3 scrubbed sites verified clean: line 3 (`Per INST-1 (methodology-changelog.md v0.20.0)` → `Per INST-1`), line 6 (`13 audit modules under tools/` → `audit modules under tools/ — see plugin.yaml for the canonical inventory`), line 66 (`no non-Python data files in v0.20.0` → `no non-Python data files`).
  - Line 20 (the AC1 fix substance, `version = "0.62.0"`) coincidentally cleared the 4th `0.20.0` site as a side effect of Phase A.3.
- **Notes**: M1 universal pin test (`"0.20.0" not in pyproject_text`) catches all 4 sites including any future re-leak. SC-024 (parallel `install_audit.py:25` stale `"all 13 tool modules"` literal) intentionally out-of-scope per mission-brief — separate future slice.

### AC4: `/reflect` round-trips the `**Addressed:**` line into `### SC-001` block of `diagnose-out/backlog.md` AFTER `**Evidence:**`

- **Status**: PASS (input-contract axis verified at /validate-slice; output-axis verified at /reflect — see Notes)
- **Evidence**:
  - **Input-contract axis (verifiable at /validate-slice)**: `$PY -m pytest tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant -v` → `1 passed in 0.03s`. Verifies all 3 BCR-1 preconditions: (a) mission-brief.md carries `**Closes:** SC-001` sentinel at L10, (b) backlog.md has `### SC-001 —` block, (c) SC-001 block has `**Evidence:**` anchor for BCR-1 strict-path insertion-position resolution.
  - **Output-contract axis (verifiable post-/reflect)**: the position-pinned awk + line-number grep from mission-brief.md verification-plan row 4 is structurally a /reflect-time check — `/reflect` injects the `- **Addressed:** slice-054-fix-pyproject-toml-version-drift on 2026-05-21` line, then the awk script (a) extracts the SC-001 block, (b) captures `evidence_last_line` + `addressed_line`, (c) ASSERTs `addressed_line > evidence_last_line` AND `addressed_line < next_sc_header_line`. The awk script will be invoked at /reflect Step 2 post-injection (and any subsequent /validate-slice run on this slice).
- **Notes**:
  - This is the **first end-to-end BCR-1 round-trip dogfood** (BCR-1 was minted at slice-053; slice-054 is its first real exercise).
  - The bifurcation is deliberate and documented in design.md§Mid-slice-smoke-gate-operational-expansion + the mission-brief TF-1 row 4 Notes block. PCA-1 auto-advance preserved because the verifiable portion at /validate-slice PASSES; the output-axis check is recorded as `/reflect`-time work item.
  - At /reflect, if the position-pinned awk + line-number grep returns non-zero (Addressed line at wrong position OR missing OR SC-002 header out of expected order), that is a BCR-1 implementation defect in `/reflect` itself — would be classified as a *reality surprise* on slice-053's BCR-1 wire and surface a follow-up slice. The structural test `test_bcr_1_sc054_round_trip_inputs_invariant` is itself re-runnable across the /build → /validate → /reflect → /validate boundary (slice-053 m5: multiple `**Addressed:**` lines per candidate are valid — APPEND, never replace).

## Layered safety checks (Step 5b — VAL-1)

- **Layer A (Credential scan)**: clean — 0 secrets detected across changed files
- **Layer B (Dependency hallucination)**: clean — 0 import findings (with `--imports-allowlist tests` per slice-003 ADR-002 convention root)
- **Invocation**: `$PY -m tools.validate_slice_layers --slice ... --changed-files <9 files> --imports-allowlist tests` → `0 secret(s), 0 import finding(s), 0 suppressed (allowlisted). Clean — both layers passed.`

## Walking-skeleton layers audit (Step 5c — WS-1)

- **Walking-skeleton**: false (per mission-brief.md L7) — gate skipped; not a foundation/skeleton slice.

## Exploratory test charter audit (Step 5d — ETC-1)

- **Exploratory-charter**: false (per mission-brief.md L8) — gate skipped; deterministic conformance fix / methodology-rule-minting slice with no UX-uncertainty surface to explore.

## Shippability catalog regression check (Step 5.5)

- **Pre-gates**:
  - SCMD-1: `clean. 54 row(s); 515 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=513.`
  - PTFCD-1: `clean. 54 row(s), 303 test-path token(s) — all files and cited functions exist.`
- **Runner (SRSC-1)**: `$PY -m tools.shippability_runner architecture/shippability.md` → `Shippability catalog run: 54 row(s), 54 PASS, 0 FAIL`
- **Result**: PASS — no past slice was silently broken by this slice's edits. All 53 prior slices' critical paths green; row #54 (new this slice) green via its 4 cited pytests.
- **Runtime**: catalog ran in ~30s total (well under 2-minute target).

## Multi-instance validation

- **Required?**: no — slice scope is static-file invariant gates (pyproject↔VERSION lock-step + stale-literal scrub) + methodology-changelog entry + ADR. No multi-user / multi-device / sharing / sync surface.
- **Result**: not-applicable

## Reality surprises

(none) — all 4 ACs PASS with real-environment evidence. The slice's structural deliverables (PVFS-1 rule + ADR-056 + v0.62.0 entry + row #54 enrichment + AC3 pin test + BCR-1 input-contract test) all behave as designed. The /reflect-time BCR-1 round-trip is the first real exercise of slice-053's wire and represents the only remaining unverified surface at /validate-slice time (deliberate; awaits /reflect).
