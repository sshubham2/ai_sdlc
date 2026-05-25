# Design: Slice 014 refactor-pmi-1-gate-to-version-agnostic-shape

**Date**: 2026-05-13
**Mode**: Standard
**Rule-ID picked**: **PMI-1 v1.1** (per slice-005/008/012 BC-1 v1.x evolution precedent — refinement of an existing rule keeps the rule-ID and bumps the rule's version field within the methodology-changelog entry; introducing PMI-2 would falsely signal a structurally new rule. The methodology rule IS still "Plugin Manifest Invariant — VERSION and plugin.yaml.version must bump atomically"; only the gate-test shape changes. PMI-1 v1.1 captures the shape evolution faithfully.)
**Canonical phrase for 3-surface schema-pin**: `version-agnostic PMI-1 cleanliness gate` (substantive, 5 words, unique to this slice; pinned across ADR-013 title + in-repo methodology-changelog v0.29.0 entry + installed methodology-changelog v0.29.0 entry).

## What's new

- `architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md` — new ADR codifying the refactor decision; reversibility class `cheap` with magnitude-of-revert justification (~30 min one-time revert PLUS recurring 1-min × N future slices reintroduced).
- `methodology-changelog.md` v0.29.0 entry — codifies PMI-1 v1.1 (version-agnostic gate shape); 3-pin shape (`## v0.29.0` heading + `PMI-1 v1.1` rule-ID-with-version-bump + canonical phrase `version-agnostic PMI-1 cleanliness gate`); explicit "supersession pattern retired at slice-014" language replacing the running supersession-event counter prose that v0.22.0..v0.28.0 entries carried.
- `architecture/shippability.md` row 14 — adds the slice-014 critical-path catalog entry (8 pytest commands enumerated below in `## Shippability catalog row`).
- `tests/methodology/test_methodology_changelog.py` — NEW test functions:
  - `test_plugin_yaml_version_matches_version_file_invariant` — the version-agnostic PMI-1 gate; replaces `test_plugin_yaml_version_matches_version_file_at_0_28_0`.
  - `test_pmi_1_gate_function_is_version_agnostic_shape` — AST meta-test pinning the absence of version-literal `Constant`s inside the gate function body.
  - `test_no_per_version_pmi_1_gate_functions_remain` — AST meta-test pinning absence of any `test_plugin_yaml_version_matches_version_file_at_0_NN_0`-shaped function.
  - `test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge` — regression test using tempdir + monkeypatch to exercise the failure path; asserts pinned error-message substrings `"PMI-1"` + `"slice-006 escape"`.
  - `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` — entry-pin for the v0.29.0 changelog entry (3-pin shape).
  - `test_v_0_29_0_entry_names_supersession_pattern_retired` — prose-pin asserting the canonical phrase `supersession pattern retired at slice-014` is present in both surfaces.
  - `test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase` — ADR-pin asserting `architecture/decisions/ADR-013-*.md` exists and contains the canonical phrase `version-agnostic PMI-1 cleanliness gate`.
- New SECTION headers in `test_methodology_changelog.py`:
  - `# --- Slice-014 / PMI-1 v1.1 entry pinning ---` (above the new v0.29.0 entry-pin functions, between current line 430 and the PMI-1 gate SECTION at current line 433)
  - `# --- PMI-1 cleanliness gate (version-agnostic, slice-014 refactor; PMI-1 v1.1 per methodology-changelog.md v0.29.0) ---` (replacing the current SECTION header at line 433 above the invariant function)
  - `# --- PMI-1 v1.1 structural meta-tests (slice-014) ---` (new SECTION below the invariant function for the 2 AST meta-tests)
  - `# --- PMI-1 v1.1 regression test (slice-014) ---` (new SECTION below the meta-tests for the regression test)
  - `# --- ADR-013 pin (slice-014) ---` (new SECTION for the ADR-pin test)
- Version-file bumps: `VERSION` + `plugin.yaml.version` + `~/.claude/ai-sdlc-VERSION` all 0.28.0 → 0.29.0 (atomic per PMI-1 v1.1 invariant).

## What's reused

- `tests/methodology/conftest.py` (`REPO_ROOT`, `read_file`) — same fixtures the rest of the test module already imports.
- `tools/install_audit.py` — INST-1 install-time-rename audit (untouched); covers `~/.claude/ai-sdlc-VERSION` sync per INST-1, separate from PMI-1's in-repo-only gate.
- `tools/critique_agent_drift_audit.py` — CAD-1 byte-equality audit on `agents/critique.md` (untouched; slice-014 does not modify `agents/critique.md`).
- Existing entry-pin functions for v0.22.0..v0.28.0 in `test_methodology_changelog.py` (current lines ~85..430) — all persist untouched per EPGD-1 self-application discipline (slice-013 codification at Dim 9 7th sub-clause).
- BC-1 v1.3 / `tools/build_checks_audit.py` (untouched; slice-014's `methodology-changelog.md` v0.29.0 entry uses BC-PROJ-2's existing negative-anchor set from slice-012 to suppress noise).
- [[ADR-007]] BC-1 v1.2 final-filter, [[ADR-010]] RSAD-1, [[ADR-011]] BC-PROJ-2 migration, [[ADR-012]] EPGD-1 — all referenced from ADR-013's Options-Considered section as precedent for the rule-evolution pattern (versioned rule-IDs).
- `architecture/critic-calibration-log.md` — not modified; slice-014 ships under existing post-slice-013 errata framing (calibration was already run 2026-05-13 with zero proposals; the ≤2-target was retired by Meta-Critic as over-ambitious; qualitative trajectory is the real signal).

## Components touched

### `tests/methodology/test_methodology_changelog.py`

- **Responsibility**: Validates the methodology-changelog itself (format, version sync, dated entries) AND houses the PMI-1 cleanliness gate + every cross-slice entry-pin / prose-pin assertion. Single source of methodology-as-test enforcement for in-repo↔installed parity at the changelog level.
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (modified by this slice — additions in 3 new SECTIONs + 1 narrow-scoped Edit removing `_at_0_28_0` gate function + its SECTION header).
- **Key interactions**:
  - Imports `REPO_ROOT` + `read_file` from `tests/methodology/conftest.py`.
  - Reads `~/.claude/methodology-changelog.md` directly via `Path.home() / ".claude" / "methodology-changelog.md"`.
  - The new regression test (`test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge`) uses pytest's `monkeypatch` fixture to replace the module-level `REPO_ROOT` symbol with a tempdir.
- **Edit boundaries (EPGD-1 self-application narrow-scope)**:
  - `old_string` for the PMI-1 gate supersession Edit STARTS at the SECTION header line `# --- PMI-1 cleanliness gate at v0.28.0 ...` (current line 433) and ENDS at the final closing parenthesis of `_at_0_28_0`'s last assertion (current line 486 + closing blank line at 487).
  - `new_string` for that Edit replaces ONLY that block with the new `# --- PMI-1 cleanliness gate (version-agnostic, slice-014 refactor; PMI-1 v1.1 per methodology-changelog.md v0.29.0) ---` SECTION header + the new `test_plugin_yaml_version_matches_version_file_invariant` function body.
  - Phase 1b INSERTs (the v0.29.0 entry-pin SECTION + the 2 AST meta-test SECTION + regression-test SECTION + ADR-pin SECTION) happen via separate Edits whose `old_string` does NOT span any entry-pin function above the gate. Each INSERT uses a unique anchor — e.g., the v0.29.0 entry-pin SECTION INSERTs by matching the last 3 lines of the v0.28.0 entry-pin function's body (the existing `## v0.28.0` installed assertion + closing parenthesis line) followed by the existing `# --- PMI-1 cleanliness gate ...` SECTION header.
  - Empirical verification at /build-slice Phase 1a (pre-Edit audit): run `grep -nE "^def test_v_0_2[2-8]_0_" tests/methodology/test_methodology_changelog.py` BEFORE any Edit and confirm 7 entry-pin functions present. Re-run AFTER all Edits and confirm 8 entry-pin functions (v0.22.0..v0.29.0). 0 of 7 prior entry-pin functions touched is the EPGD-1 self-application empirical verification.

### `methodology-changelog.md` (and installed copy `~/.claude/methodology-changelog.md`)

- **Responsibility**: Canonical methodology evolution log; each `## v0.NN.0 — YYYY-MM-DD` entry codifies one rule introduction or refinement.
- **Lives at**: `methodology-changelog.md` (in-repo) + `~/.claude/methodology-changelog.md` (installed; bidirectional byte-equal per slice-005..013 forensic capture N=9 stable).
- **Key interactions**: Read by `/status`, `/triage`, `/discover`, `/critique`, every audit, every entry-pin / prose-pin test in `test_methodology_changelog.py`. After this slice's v0.29.0 entry ships, future invocations of those skills + tests see the version-agnostic PMI-1 v1.1 codification.
- **Edit boundaries**: Append-new at top of the version-entries list (mirrors slice-013 + every prior versioned slice). PRE-existing v0.22.0..v0.28.0 entries are NOT edited (their per-version supersession-pattern prose remains as historical record; the v0.29.0 entry's explicit "supersession pattern retired at slice-014" prose annotates that the running counter terminates here).

### `architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md`

- **Responsibility**: Architecture-decision record for the refactor (rationale, options-considered, reversibility class, magnitude-of-revert).
- **Lives at**: `architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md` (created by this slice).
- **Key interactions**: Referenced from methodology-changelog.md v0.29.0 entry; referenced by the ADR-pin test (`test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase`); read by future calibration runs / Critic runs as evidence of the refactor's reasoning.

### `architecture/shippability.md`

- **Responsibility**: Critical-path catalog enumerating every slice-rooted pytest invocation that must continue to pass for the system to ship.
- **Lives at**: `architecture/shippability.md` (modified — row 14 added).
- **Key interactions**: Run by `/validate-slice` Step 5.5 as a final regression gate; row 14 lists 8 pytest commands (see `## Shippability catalog row` below).

## Contracts added or changed

None. Slice-014 is an internal methodology refactor; no API endpoints, no event schemas, no external integration contracts. The implicit "contract" between PMI-1 v1.0 (per-version gate) and PMI-1 v1.1 (version-agnostic gate) is captured by the AST meta-tests + the canonical-phrase pin discipline at the methodology-changelog level.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Slice-014 introduces no new production modules — all changes are to test files + methodology-changelog + ADR + version files + shippability catalog. Wiring matrix is zero-row (header + separator only; treated as clean by `tools/wiring_matrix_audit.py`).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-013]] — Refactor PMI-1 cleanliness gate from per-version-bump shape to version-agnostic invariant; promote rule-ID to **PMI-1 v1.1** preserving lineage; defend new shape with 2 AST meta-tests; preserve "did you bump?" discipline via existing per-version entry-pin tests + mission-brief atomicity checklist. — reversibility: **cheap** (frontmatter class — matches ADRs 003/004/006/007/008/009/010/011/012 convention). Magnitude-of-revert justification documented in ADR-013's `## Reversibility` section body: ~30 min one-time revert PLUS recurring 1-min × N future slices reintroduced. Per /critique m1 ACCEPTED-FIXED — frontmatter keyword is the machine-parseable single-token class; body prose explains nuance.

## Authorization model for this slice

N/A. Internal methodology tooling, no auth surface.

## Error model for this slice

- `test_plugin_yaml_version_matches_version_file_invariant` raises `AssertionError` with pinned message naming **"PMI-1"** + **"slice-006 escape"** when `VERSION` ≠ `plugin.yaml.version`. This is the SOLE failure mode and the SOLE assertion (per AC #2 must-not-defer "the version-agnostic gate's SOLE assertion").
- AST meta-tests raise `AssertionError` with messages naming the offending function name or smuggled string-literal value when the structural invariant is violated.
- Regression test (`test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge`) uses `pytest.raises(AssertionError)` + per-substring-match assertion on the captured message; PASSES only when both pinned substrings are present. Full fixture spec in next subsection.

## Regression test fixture spec (post-/critique M2 ACCEPTED-FIXED — pin the name-resolution semantics)

Per /critique M2: the prior wording "module-level `REPO_ROOT` symbol" was ambiguous between (a) `tests.methodology.conftest.REPO_ROOT` (the imported name) and (b) `tests.methodology.test_methodology_changelog.REPO_ROOT` (the local-module rebinding). The proposed `_invariant` body uses bare `REPO_ROOT` — Python resolves the bare name at call-time from the function's enclosing-module globals, which is `test_methodology_changelog`, NOT `conftest`. Patching (a) would silently no-op (the gate would still read real VERSION/plugin.yaml files, both at 0.28.0, match → AssertionError NOT raised → `pytest.raises` raises `DID NOT RAISE`).

The regression test fixture spec is therefore pinned exactly as follows:

```python
def test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge(tmp_path, monkeypatch):
    """Regression test: gate fires with pinned error message when VERSION ≠ plugin.yaml.version.

    Defect class (per slice-007 PMI-1 closure pattern + slice-014 v1.1 refactor):
    The version-agnostic gate's correctness depends on its ability to FIRE
    when the cross-file equality is broken. This regression test exercises
    the FAILURE path with a tempdir + monkeypatch.

    Monkeypatch target name-resolution semantics (per slice-014 /critique M2):
    the bare `REPO_ROOT` reference inside the gate function resolves from
    `test_methodology_changelog`'s module globals (where `REPO_ROOT` was
    imported from `tests.methodology.conftest` at module top). Patching
    `tests.methodology.test_methodology_changelog.REPO_ROOT` (NOT the
    `conftest` original) is correct. Patching `conftest.REPO_ROOT` would
    silently no-op — the gate would still read real VERSION/plugin.yaml
    files (both at the slice's current version), match, AssertionError
    NOT raised, `pytest.raises` raises `DID NOT RAISE`, test fails for
    the wrong reason.

    Rule reference: PMI-1 v1.1 (slice-014 atomic bump + version-agnostic
    gate refactor), AC #2 regression coverage.
    """
    # Fixture: tempdir with mismatched version files
    (tmp_path / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    (tmp_path / "plugin.yaml").write_text("version: 4.5.6\n", encoding="utf-8")

    # Monkeypatch the module-local REPO_ROOT binding in
    # test_methodology_changelog (NOT conftest — see docstring).
    monkeypatch.setattr(
        "tests.methodology.test_methodology_changelog.REPO_ROOT",
        tmp_path,
    )

    # Invoke gate; expect AssertionError with both pinned substrings.
    with pytest.raises(AssertionError) as excinfo:
        test_plugin_yaml_version_matches_version_file_invariant()

    # Per-substring assertions (NOT joined by `and`) so failure message
    # distinguishes which substring is missing. Mirrors TF-1 row 3 signal
    # pin shape.
    assert "PMI-1" in str(excinfo.value), (
        f"regression error message missing 'PMI-1' substring: "
        f"{str(excinfo.value)!r}"
    )
    assert "slice-006 escape" in str(excinfo.value), (
        f"regression error message missing 'slice-006 escape' substring: "
        f"{str(excinfo.value)!r}"
    )
```

Fixture contract (pinned at design.md to bind the Builder's implementation):

- **Tempdir contents**: `(tmp_path / "VERSION").write_text("1.2.3\n", encoding="utf-8")` AND `(tmp_path / "plugin.yaml").write_text("version: 4.5.6\n", encoding="utf-8")`. The proposed `_invariant` body only accesses `plugin_manifest["version"]`, so `"version: 4.5.6\n"` alone is sufficient YAML (no other keys needed). If `plugin_manifest["version"]` were ever extended to read additional keys (out-of-scope at slice-014), this fixture's YAML body must extend in lockstep — but at slice-014 the minimum YAML shape is sufficient.
- **Monkeypatch target string**: `"tests.methodology.test_methodology_changelog.REPO_ROOT"` (exact dotted path). NOT `"tests.methodology.conftest.REPO_ROOT"` — that would silently no-op (see fixture docstring).
- **Assertion order**: `with pytest.raises(AssertionError) as excinfo:` block invokes the gate; then TWO per-substring assertions on `str(excinfo.value)` (NOT one joined `and` assertion). Each substring assertion fails independently with a pinned error message naming which substring was missing — diagnostic clarity at failure-time.
- **The gate function is imported into the regression test scope** by virtue of being a sibling function in the same module — bare-name call `test_plugin_yaml_version_matches_version_file_invariant()` resolves correctly.

## Phase plan (post-/critique M1 + m2 ACCEPTED-FIXED — explicit ordered enumeration)

Per /critique M1 (META-1 transient breakage window) + m2 (Phase labels scattered, no single ordered list): this section enumerates the canonical Phase sequence the Builder MUST follow at /build-slice. Phases are referenced from other sections of this design.md (`## Edit-discipline boundaries`, `## Empirical-verification-at-design-time audits`, `## Bidirectional sha256 forensic capture`) — those references resolve here.

**Phase 0 — sha256 forensic capture (pre-edit baseline)**

Capture sha256 of all 6 surfaces BEFORE any Edit. Log to build-log.md. Per slice-005..013 N=9-stable bidirectional sha256 capture discipline.

- `sha256sum methodology-changelog.md` (in-repo)
- `sha256sum ~/.claude/methodology-changelog.md` (installed)
- `sha256sum tests/methodology/test_methodology_changelog.py`
- `sha256sum VERSION`
- `sha256sum plugin.yaml`
- `sha256sum ~/.claude/ai-sdlc-VERSION`

Expected at Phase 0: in-repo↔installed methodology-changelog byte-equal; VERSION = plugin.yaml.version = ai-sdlc-VERSION = "0.28.0".

**Phase 1a — empirical pre-Edit audits**

Run Audit 3 from `## Empirical-verification-at-design-time audits` below (Edit narrow-scope verification on current file content):

```bash
$ grep -nE "^# --- |^def test_v_0_|^def test_plugin_yaml_version_" tests/methodology/test_methodology_changelog.py
```

Expected pre-build: 7 entry-pin SECTIONs, 7 entry-pin functions `test_v_0_22_0_..._v_0_28_0_`, 1 PMI-1 gate SECTION header (`# --- PMI-1 cleanliness gate at v0.28.0 ...`), 1 PMI-1 gate function (`test_plugin_yaml_version_matches_version_file_at_0_28_0`).

EPGD-1 self-application baseline established.

**Phase 1a' — Imports preamble Edit (post-/critique-review M-add-1 ACCEPTED-FIXED — `import pytest` + `import ast` not pre-existing in test file)**

Per /critique-review M-add-1 (DR-1 dual-review catch): the current `tests/methodology/test_methodology_changelog.py` imports block (lines 1-7) imports `re`, `pathlib.Path`, `yaml`, and `REPO_ROOT, read_file` from `conftest`. Neither `pytest` nor `ast` is currently imported. The canonical regression-test body uses `pytest.raises(AssertionError) as excinfo` (per `## Regression test fixture spec`). The 2 AST meta-tests use `ast.parse(...)` + `ast.walk(...)` + `isinstance(node, ast.Constant)` / `isinstance(node, ast.FunctionDef)`. Without explicit imports added BEFORE Phase 1b, rows 2 + 3 + 4 at the Phase 1d smoke gate would all fail with `NameError: name 'pytest' is not defined` / `NameError: name 'ast' is not defined`, which the design.md diagnostic guidance at Phase 1d would misdiagnose as EPGD-1 violation (Edit pulled adjacent SECTION content).

Phase 1a' is a 30-second narrow-scoped Edit on the imports block:

- `old_string` = the current import-block (test_methodology_changelog.py lines 1-7):
  ```
  """Validate the methodology-changelog itself: format, version sync, dated entries."""
  import re
  from pathlib import Path

  import yaml

  from tests.methodology.conftest import REPO_ROOT, read_file
  ```
- `new_string` = same with `import ast` and `import pytest` inserted in alphabetical order alongside `re`:
  ```
  """Validate the methodology-changelog itself: format, version sync, dated entries."""
  import ast
  import re

  import pytest
  import yaml

  from tests.methodology.conftest import REPO_ROOT, read_file
  ```

`ast` is stdlib (groups with `re`); `pytest` is third-party (groups with `yaml`, alphabetical). Conforms to PEP-8 import grouping (stdlib → third-party → first-party with blank-line separators) — same shape the imports block already uses.

After Phase 1a': imports block is ready for the new test functions added in Phase 1b/1c. Subsequent Phase 1d smoke gate failures (if any) cleanly distinguish "EPGD-1 narrow-scope violation" from "missing-imports runtime prerequisite" diagnostic paths.

**Phase 1b — INSERT v0.29.0 entry-pin SECTION + 2 entry-pin functions**

INSERT into `tests/methodology/test_methodology_changelog.py` between the v0.28.0 entry-pin function's closing line (current line ~430) and the PMI-1 gate SECTION header (current line 433):

- New SECTION header `# --- Slice-014 / PMI-1 v1.1 entry pinning ---`
- New function `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` — 3-pin shape (heading + rule-ID + canonical phrase) across in-repo + installed surfaces; total 6 substring assertions
- New function `test_v_0_29_0_entry_names_supersession_pattern_retired` — pins canonical phrase `supersession pattern retired at slice-014` across in-repo + installed surfaces; total 2 substring assertions

Edit `old_string` for Phase 1b: matches the last 3 lines of the v0.28.0 entry-pin function's body (the `## v0.28.0` installed assertion lines) PLUS the closing parenthesis line PLUS the existing `# --- PMI-1 cleanliness gate at v0.28.0 ...` SECTION header line — uniquely anchored on the existing gate SECTION header which is to-be-replaced in Phase 1c. `new_string` is the same anchor lines + new SECTION + 2 functions + a blank-line separator before the PMI-1 gate SECTION header (which is still the OLD `# --- PMI-1 cleanliness gate at v0.28.0 ...` text at Phase 1b — that SECTION header gets replaced in Phase 1c).

After Phase 1b: 8 entry-pin SECTIONs, 9 entry-pin functions (v0.22.0..v0.29.0 + the v0.29.0 prose-pin variant). The v0.29.0 entry-pin tests are WRITTEN-FAILING because the v0.29.0 changelog entry doesn't yet exist.

**Phase 1c — PMI-1 gate Edit (narrow-scoped per EPGD-1)**

Edit boundaries (EPGD-1 self-application narrow-scope):

- `old_string` STARTS at the SECTION header line `# --- PMI-1 cleanliness gate at v0.28.0 ...` and ENDS at the closing parenthesis of `_at_0_28_0`'s last assertion + the closing blank line (current line 487).
- `new_string` is the new SECTION header `# --- PMI-1 cleanliness gate (version-agnostic, slice-014 refactor; PMI-1 v1.1 per methodology-changelog.md v0.29.0) ---` followed by the new `test_plugin_yaml_version_matches_version_file_invariant` function body (see `## Empirical-verification-at-design-time audits` Audit 1 for the canonical proposed body).

Then 3 more INSERTs below the new `_invariant` function for the 3 new SECTIONs:
- `# --- PMI-1 v1.1 structural meta-tests (slice-014) ---` + 2 functions (`_is_version_agnostic_shape` + `_no_per_version_pmi_1_gate_functions_remain`)
- `# --- PMI-1 v1.1 regression test (slice-014) ---` + 1 function (`_fails_with_pinned_message_when_version_files_diverge` — full spec in `## Regression test fixture spec`)
- `# --- ADR-013 pin (slice-014) ---` + 1 function (`_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase`)

After Phase 1c: 4 new test functions live below the gate. The regression test, ADR-pin test are WRITTEN-FAILING because ADR-013 doesn't yet exist. The 2 AST meta-tests are PASSING (the gate function meets both structural invariants at Phase 1c — no version literal in `_invariant`'s body, no `_at_0_NN_0`-shaped function remains).

**Phase 1d — mid-slice smoke gate**

Run the 4 mid-slice-smoke pytest commands from the mission brief:

```bash
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_function_is_version_agnostic_shape -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_no_per_version_pmi_1_gate_functions_remain -v
```

Expected at Phase 1d:
- Row 1 (`_invariant`) — PASSES (VERSION="0.28.0" == plugin.yaml.version="0.28.0").
- Row 2 (`_is_version_agnostic_shape`) — PASSES.
- Row 3 (regression `_fails_with_pinned_message`) — PASSES (independent of ambient VERSION value because monkeypatch isolates).
- Row 4 (`_no_per_version_pmi_1_gate_functions_remain`) — PASSES.

The v0.29.0 entry-pin + supersession-retired prose-pin + ADR-pin tests remain WRITTEN-FAILING at Phase 1d because Phase 2 hasn't run yet. If Phase 1d's 4 smoke tests don't all PASS: STOP, diagnose (most likely cause: Phase 1c Edit pulled adjacent entry-pin SECTION content — EPGD-1 violation; re-verify the Edit `old_string` boundaries on the actual built file).

**Phase 2 — ATOMIC commit (post-/critique M1 ACCEPTED-FIXED — META-1 atomicity preservation)**

Per /critique M1: `test_version_matches_most_recent_changelog_entry` (`test_methodology_changelog.py:33`) fires the moment a v0.29.0 changelog entry exists in `methodology-changelog.md` if VERSION still says "0.28.0", and conversely if VERSION is bumped first but the changelog still has v0.28.0 as the latest heading. Phase 2 packages ALL atomicity-bound operations as a SINGLE atomic build operation — the full test suite is NOT run between these steps.

Phase 2 operations (executed in build-log.md as a single contiguous block):

1. Write the v0.29.0 entry into in-repo `methodology-changelog.md` at the top of the version-entries list. Entry content per `## Components touched / methodology-changelog.md` + `## N-surface schema-pin discipline` requirements: includes the `## v0.29.0 — 2026-05-13` heading, `PMI-1 v1.1` rule-ID, canonical phrase `version-agnostic PMI-1 cleanliness gate`, and the supersession-retirement phrase `supersession pattern retired at slice-014`.
2. Forward-sync the in-repo entry to `~/.claude/methodology-changelog.md` (installed) via copy — bidirectional byte-equal byte preserved.
3. Bump `VERSION` 0.28.0 → 0.29.0.
4. Bump `plugin.yaml.version` 0.28.0 → 0.29.0.
5. Bump `~/.claude/ai-sdlc-VERSION` 0.28.0 → 0.29.0.
6. Write `architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md` (this file already exists from /design-slice — re-verify content + commit if not yet committed).

The atomicity discipline: these 6 operations form ONE Phase. The full test suite is NOT run after step 1 alone (would fail META-1 transient), or after step 1+2 alone (META-1 still failing), or after step 3 but not 4 (PMI-1 transient mismatch). The first full-suite invocation happens at Phase 3.

**Phase 3 — full test suite**

Run the full methodology test suite + shippability catalog row 14:

```bash
$PY -m pytest tests/methodology/ -v
# Plus the 8 shippability-row-14 pytest commands from `## Shippability catalog row` below.
```

Expected at Phase 3: ALL tests PASS — PMI-1 v1.1 invariant + 2 AST meta-tests + regression test + entry-pin + prose-pin + ADR-pin + META-1 invariant (`VERSION="0.29.0"` == latest changelog heading `"0.29.0"`) + every prior entry-pin function for v0.22.0..v0.28.0.

**Phase 4 — sha256 forensic capture (post-edit)**

Capture sha256 of the same 6 surfaces from Phase 0. Log to build-log.md. Expected: in-repo↔installed methodology-changelog byte-equal at the new content; VERSION = plugin.yaml.version = ai-sdlc-VERSION = "0.29.0".

EPGD-1 self-application empirical verification at Phase 4: re-run Phase 1a's grep — expected to show 8 entry-pin SECTIONs + 9 entry-pin function definitions (v0.22.0..v0.28.0 prior entries untouched + 2 new v0.29.0 entries) + 1 new PMI-1 gate SECTION header + 1 new `_invariant` gate function + 3 new SECTIONs below the gate. 0 of 7 prior entry-pin function names changed (verified by diff inspection of the test file).

N=10 stable bidirectional sha256 capture post-slice-014.

## Edit-discipline boundaries (EPGD-1 self-application — slice-013 codification at Dim 9 7th sub-clause)

Slice-014 IS the canonical reference instance for **(a) the discipline EPGD-1 governs** AND **(b) the refactor that retires the supersession pattern EPGD-1 governs going forward**. Both apply simultaneously:

- **(a) EPGD-1 governs this slice's Edits at /build-slice**: the PMI-1 gate supersession Edit (Phase 1c) MUST narrow-scope `old_string` to the gate function body + its dedicated SECTION header only — never spanning any entry-pin function above. The v0.29.0 entry-pin INSERT (Phase 1b) MUST happen UNDER ITS OWN dedicated `# --- Slice-014 / PMI-1 v1.1 entry pinning ---` SECTION header, structurally separate from the gate's SECTION. Build-time empirical verification (Phase 1a + Phase 4): pre-Edit grep confirms 7 entry-pin functions (v0.22.0..v0.28.0); post-Edit grep confirms 8 entry-pin functions (v0.22.0..v0.29.0). 0 of 7 prior entry-pin functions touched by slice-014's Edits.

- **(b) Slice-014 retires the supersession pattern EPGD-1 governs**: from slice-015 onwards, the PMI-1 gate function is no longer superseded per-version; future slices' version bumps update `VERSION` + `plugin.yaml.version` + `ai-sdlc-VERSION` and the gate continues to pass without modification. The PMI-1 versioned-gate supersession-event counter (N=6 at slice-013) terminates at N=6; future slices DO NOT ratchet it. The N=6 supersession-events stable count is the canonical historical record; v0.29.0's entry annotates this termination explicitly. EPGD-1 itself continues to govern entry-pin / structural-invariant-supersession Edits at other surfaces (e.g., `_lists_N_sub_clauses` structural invariant in `test_critique_agent.py`; slice-013 N=2 instances stable).

The (a) ↔ (b) duality is exactly the recursive-self-application pattern (RSAD-1, slice-011) at the methodology-evolution level: the slice authoring the retirement of a discipline-as-pattern IS the canonical reference instance of the discipline's last application. Slice-014 IS to PMI-1-version-gate supersession what slice-011 was to RSAD-1 codification — the authoring slice IS the canonical reference instance.

## AC-trace table (Wiegers — slice-008 M1 codification, slice-014 N=4 cumulative)

| AC | Design element |
|----|----------------|
| AC #1 | `test_plugin_yaml_version_matches_version_file_invariant` function + `test_pmi_1_gate_function_is_version_agnostic_shape` AST meta-test + SECTION header `# --- PMI-1 cleanliness gate (version-agnostic, slice-014 refactor; PMI-1 v1.1 per methodology-changelog.md v0.29.0) ---` |
| AC #2 | Invariant function's SOLE assertion `assert version_file == plugin_version, f"PMI-1 mismatch ... slice-006 escape recurred."` + `test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge` regression test (tempdir + monkeypatch + `pytest.raises(AssertionError)` + substring assertions for `"PMI-1"` + `"slice-006 escape"`) |
| AC #3 | EPGD-1 narrow-scoped Edit removing the `_at_0_28_0` function + its SECTION header + `test_no_per_version_pmi_1_gate_functions_remain` AST meta-test pinning absence of `_at_0_NN_0`-shaped function names |
| AC #4 | methodology-changelog.md v0.29.0 entry (3-pin: `## v0.29.0` heading + `PMI-1 v1.1` rule-ID + canonical phrase `version-agnostic PMI-1 cleanliness gate`) + `## Supersession pattern retired at slice-014` prose-line + ADR-013 + entry-pin test `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` + prose-pin test `test_v_0_29_0_entry_names_supersession_pattern_retired` + ADR-pin test `test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase` |
| AC #5 | Atomic version bumps to `VERSION` + `plugin.yaml.version` + `~/.claude/ai-sdlc-VERSION` (all 0.28.0 → 0.29.0) + re-invocation of the unchanged `_invariant` function PASSing post-bump (empirical proof — same test code, different file content, still PASSES) |

Reverse trace (every design element → driving AC):
- `_invariant` function → AC #1 + AC #2 + AC #5
- `_is_version_agnostic_shape` AST meta-test → AC #1
- `_fails_with_pinned_message_when_version_files_diverge` regression → AC #2
- `_no_per_version_pmi_1_gate_functions_remain` AST meta-test → AC #3
- v0.29.0 entry-pin + prose-pin tests → AC #4
- ADR-013 + ADR-pin test → AC #4
- Atomic version bumps → AC #5
- New SECTION headers + EPGD-1 Edit boundaries → AC #1 (semantic anchor) + AC #3 (negative-anchor for legacy header)

No design elements lack a driving AC. No ACs lack covering design elements.

## Empirical-verification-at-design-time audits (N=12 stable post-slice-013 → ratchets at slice-014)

Per slice-008..013 design-time empirical audit discipline (currently N=12 stable). Slice-014 runs THREE audits BEFORE locking ACs:

### Audit 1 — version-literal absence in proposed gate function body

Verify the design-level proposed body of `test_plugin_yaml_version_matches_version_file_invariant` contains ZERO `r"\d+\.\d+\.\d+"` regex matches. The proposed body is documented inline below:

```python
def test_plugin_yaml_version_matches_version_file_invariant():
    """VERSION file content == plugin.yaml.version (PMI-1 v1.1 invariant).

    Defect class (per slice-006 B1 escape, slice-007 PMI-1 closure pattern):
    PMI-1 invariant requires `plugin.yaml.version` and the in-repo `VERSION`
    file to bump atomically. Without this gate, an out-of-band /reflect or
    commit could leave one file lagging — the slice-006 escape recurrence
    pattern.

    Version-agnostic shape (PMI-1 v1.1 per slice-014 refactor): no hardcoded
    version literal. The cross-file equality invariant IS the defect class
    this gate exists to catch. The "did you bump at all?" discipline is
    carried by per-version entry-pin tests (test_v_0_NN_0_*) + each slice's
    mission-brief atomic-bump checklist. See methodology-changelog.md v0.29.0
    + ADR-013 for the supersession pattern retirement rationale.

    Rule reference: PMI-1 v1.1 (slice-014 atomic bump + version-agnostic gate
    refactor).
    """
    version_file = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    plugin_manifest = yaml.safe_load(
        (REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    )
    plugin_version = plugin_manifest["version"]

    assert version_file == plugin_version, (
        f"PMI-1 mismatch: VERSION={version_file!r} != "
        f"plugin.yaml.version={plugin_version!r}. The slice-006 escape "
        f"recurred — atomic bump discipline broken."
    )
```

Grep proposed body for version-literal: NONE. Audit PASSES at design time. Post-build empirical re-verification at Phase 4: re-run the AST meta-test on the actually-built file; both invariant assertions and the absence of version literals must hold.

### Audit 2 — pinned error-message substring presence

Verify the proposed assertion's error-message format contains BOTH `"PMI-1"` substring AND `"slice-006 escape"` substring. From Audit 1's proposed body:

- `"PMI-1 mismatch: ..."` — `"PMI-1"` substring PRESENT ✓
- `"The slice-006 escape recurred ..."` — `"slice-006 escape"` substring PRESENT ✓

Audit PASSES at design time. Build-time confirmation by the regression test asserting both substrings against the actual `AssertionError.args[0]`.

### Audit 3 — Edit narrow-scope verification on current file content

Pre-Phase-1c empirical audit: grep current file structure to confirm the EPGD-1 Edit boundaries.

```bash
$ grep -nE "^# --- |^def test_v_0_|^def test_plugin_yaml_version_" tests/methodology/test_methodology_changelog.py
```

Expected pre-build output: 7 entry-pin SECTIONs (Slice-008..013, plus the pre-Slice-008 ones), 7 entry-pin function definitions (`test_v_0_22_0_..._v_0_28_0_`), 1 PMI-1 gate SECTION header (`# --- PMI-1 cleanliness gate at v0.28.0 ...`), 1 PMI-1 gate function (`test_plugin_yaml_version_matches_version_file_at_0_28_0`).

Expected post-build output: 8 entry-pin SECTIONs (with new Slice-014 / PMI-1 v1.1 SECTION inserted), 8 entry-pin function definitions (`test_v_0_22_0_..._v_0_29_0_`), 1 PMI-1 gate SECTION header (new wording `# --- PMI-1 cleanliness gate (version-agnostic ...) ---`), 1 PMI-1 gate function (`test_plugin_yaml_version_matches_version_file_invariant`). Plus 3 new SECTIONs below the gate: structural-meta + regression + ADR-pin.

EPGD-1 self-application verification: 0 of 7 prior entry-pin function names changed. The diff post-build confirms this empirically.

Audit PASSES at design time pending Phase 1a pre-Edit re-confirmation.

## Test-first plan (TF-1 row plan; consolidated from mission brief 11 rows → 9 rows)

Per **TF-1** (`methodology-changelog.md` v0.13.0). Statuses progress PENDING → WRITTEN-FAILING → PASSING; `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| Row | AC | Test type | Test path | Test function | Status |
|-----|----|-----------|-----------|---------------|--------|
| 1 | AC 1 + 2 + 5 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PENDING |
| 2 | AC 1 | AST meta-test | tests/methodology/test_methodology_changelog.py | test_pmi_1_gate_function_is_version_agnostic_shape | PENDING |
| 3 | AC 2 | unit (regression) | tests/methodology/test_methodology_changelog.py | test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge | PENDING |
| 4 | AC 3 | AST meta-test | tests/methodology/test_methodology_changelog.py | test_no_per_version_pmi_1_gate_functions_remain | PENDING |
| 5 | AC 4 | entry-pin + prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed | PENDING |
| 6 | AC 4 | prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_29_0_entry_names_supersession_pattern_retired | PENDING |
| 7 | AC 4 | adr-pin | tests/methodology/test_methodology_changelog.py | test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase | PENDING |

Note: 7 rows total. Mission brief's 11-row plan listed AC #4 with 5 separate tests; design.md consolidates to 3 (entry-pin + prose-pin in row 5 combines the 3-pin shape per N-surface schema-pin convention into ONE function reading both surfaces — same pattern as the existing `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` function at current line 368). Mission brief's optional mini-CAD-1 row (row 11 install_audit) is DROPPED per design-slice scope decision (Out of scope: tools/install_audit.py untouched). Row 1 = THE invariant test (the same function runs at the start of TF-1 progression as WRITTEN-FAILING because `_at_0_28_0` still exists and `_invariant` doesn't; transitions to PASSING after Phase 1c Edit completes; and re-validates post-version-bump WITHOUT code change as AC #5 empirical proof).

### TF-1 row status pin signals (per slice-008 M2 / TF-1 PENDING → WRITTEN-FAILING transition discipline N=9 stable post-slice-013)

| Row | WRITTEN-FAILING signal (pinned in TF-1 audit) | PASSING signal |
|-----|----------------------------------------------|----------------|
| 1 | `NameError: name 'test_plugin_yaml_version_matches_version_file_invariant' is not defined` (function not yet written) OR `AssertionError "..."` if written with wrong body before file Edit | Pytest invocation returns exit 0 |
| 2 | `AssertionError: PMI-1 gate function contains version-literal Constant: '0.28.0' at line N` (regex matches `\d+\.\d+\.\d+` inside function body's AST) | Pytest invocation returns exit 0 (no Constants matching regex inside gate body) |
| 3 | `AssertionError: AssertionError message missing 'PMI-1' substring` OR `... missing 'slice-006 escape' substring` (depending on which is missing) | Pytest invocation returns exit 0 (regression test PASSES when gate raises with both substrings) |
| 4 | `AssertionError: per-version PMI-1 gate function still present: test_plugin_yaml_version_matches_version_file_at_0_28_0 at line N` (legacy function detected by AST walk) | Pytest invocation returns exit 0 (zero legacy functions detected) |
| 5 | `AssertionError "in-repo methodology-changelog.md missing v0.29.0 entry"` OR `... missing PMI-1 v1.1 rule reference` OR `... missing canonical phrase 'version-agnostic PMI-1 cleanliness gate'` | Pytest invocation returns exit 0 |
| 6 | `AssertionError "methodology-changelog.md missing canonical phrase 'supersession pattern retired at slice-014'"` | Pytest invocation returns exit 0 |
| 7 | `AssertionError "ADR-013 not found at architecture/decisions/ADR-013-*.md"` OR `... missing canonical phrase 'version-agnostic PMI-1 cleanliness gate'` | Pytest invocation returns exit 0 |

## Shippability catalog row (architecture/shippability.md row 14)

Row 14 critical-path enumeration:

```
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_function_is_version_agnostic_shape -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_no_per_version_pmi_1_gate_functions_remain -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_29_0_entry_names_supersession_pattern_retired -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase -v
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant -v  # post-bump re-pass (AC #5 empirical proof)
```

8 pytest commands total; expected to run in ≤4s aggregate (well under shippability's 2-min target).

## Recursive-self-application audit (RSAD-1 — slice-011 codification at Dim 9 6th sub-clause)

Slice-014's design itself is stress-tested against the discipline it implements:

- **Q1**: Does this design.md commit version-literal pinning that slice-014's own refactor would refuse? **A**: `0.29.0` appears in this design (in AC #5, version-bump section, TF-1 row 5 signal). All occurrences are about THE EVENT this slice executes (the atomic bump 0.28.0 → 0.29.0) and the corresponding entry-pin for the v0.29.0 changelog entry. They are NOT inside the proposed `_invariant` function body (Audit 1 verified). The version-agnostic-shape rule applies to the gate test, NOT to entry-pin tests (which ARE per-version by definition and persist across all versions per EPGD-1). No internal inconsistency.

- **Q2**: Does this design retire a discipline it depends on? **A**: Slice-014 retires the PMI-1 *versioned-gate supersession* pattern. The PMI-1 *invariant* (atomic bump) is preserved. Slice-014 STILL relies on the discipline of pinning v0.29.0 changelog entry across in-repo + installed (entry-pin discipline, distinct from PMI-1 versioned-gate). The retirement is narrow and surgical; no transitive dependency on the retired pattern.

- **Q3**: Does this slice ship its own ADR-013 using the very ADR-pin convention it depends on for AC #4? **A**: Yes — ADR-013 is created by this slice AND row 7 of the TF-1 plan asserts ADR-013 exists. The ADR-pin test PASSES only after the ADR file is committed. This is canonical recursive-self-application — the slice authoring the refactor IS the canonical reference instance of the discipline's last application (per "(b) Slice-014 retires the supersession pattern" framing in `## Edit-discipline boundaries`).

RSAD-1 stress-test PASSES at design time.

## N-surface schema-pin discipline (N=2 instances stable post-slice-013 → N=3 if applied at slice-014)

Canonical phrase `version-agnostic PMI-1 cleanliness gate` pinned across:

- (1) ADR-013 title + body (`title:` frontmatter + first paragraph of `# ADR-013:` H1 below)
- (2) in-repo `methodology-changelog.md` v0.29.0 entry body
- (3) installed `~/.claude/methodology-changelog.md` v0.29.0 entry body

3-surface shape per slice-011 RSAD-1 precedent + slice-013 EPGD-1 second instance. Slice-014 ratchets the N-surface schema-pin 3-surface shape from **N=2 instances stable** to **N=3 instances stable** post-slice-014 (RSAD-1 v0.26.0 + EPGD-1 v0.28.0 + PMI-1-v1.1 v0.29.0).

The 3-surface-pin makes drift impossible without breaking ≥2 tests simultaneously. Row 5 + row 7 of the TF-1 plan jointly enforce the pin: row 5 checks the canonical phrase across (2) + (3); row 7 checks across (1).

## Bidirectional sha256 forensic capture (N=9 stable post-slice-013 → N=10 at slice-014)

Per slice-005..013 N=9-stable bidirectional sha256 capture discipline. At /build-slice Phase 0 (BEFORE any Edit) and Phase 4 (AFTER all Edits + version bumps + commits), capture and log to build-log.md:

- `sha256sum methodology-changelog.md` (in-repo)
- `sha256sum ~/.claude/methodology-changelog.md` (installed)
- `sha256sum tests/methodology/test_methodology_changelog.py`
- `sha256sum VERSION`
- `sha256sum plugin.yaml`
- `sha256sum ~/.claude/ai-sdlc-VERSION`

Forensic record proves byte-equal in-repo↔installed at Phase 0 and Phase 4 separately. N=10 stable post-slice-014.

## Out-of-scope source-of-truth migration (PMI-1 v2 candidate; deferred per mission brief)

Per mission brief: Migrating PMI-1 to a stronger source-of-truth contract — where methodology-changelog.md's latest `## v0.NN.0` heading IS the source of truth, and `VERSION` + `plugin.yaml.version` MUST derive from it — is OUT OF SCOPE for slice-014.

Design rationale for the v2 deferral:

- Slice-014's v1.1 refactor retires the per-version-bump test churn (the N=6 supersession friction). It does NOT plug the "did you bump at all?" hole (a malicious or absent-minded slice that adds a v0.29.0 changelog entry but FORGETS to bump `VERSION` would still pass the v1.1 invariant because both files still equal "0.28.0"). The mission brief acknowledged this hole.
- The "did you bump?" discipline is preserved by:
  - The per-version entry-pin test (row 5 of TF-1 plan: `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed`) — fails until the v0.29.0 changelog entry exists in both surfaces.
  - Each slice's mission-brief atomic-bump checklist (must-not-defer item: "Atomic version bump across ALL three surfaces").
  - The CAD-1 / install_audit / cross_spec_parity audits — cross-check installed-vs-in-repo at the file-content level (not version-level).
- The hole is bounded: a slice can mismatch ONLY if it (a) creates a v0.29.0 changelog entry AND (b) deliberately/accidentally fails to bump VERSION. The mission-brief atomicity checklist + the existing META-1 `test_version_matches_most_recent_changelog_entry` test (currently at line 33-N of `test_methodology_changelog.py`) catches the v0.29.0-entry-but-VERSION-not-bumped case at the META-1 test level, not the PMI-1 level.

So the slice-014 v1.1 refactor is correct as scoped: PMI-1 covers atomic-bump-cross-file-equality, META-1 covers VERSION-matches-latest-changelog-entry, INST-1 covers installed-vs-in-repo-version-sync. The 3 invariants compose to cover "did you bump?" + "did you bump atomically?" + "did the installed copy receive the bump?". No additional v2 refactor needed at slice-014.

v2 candidate (PMI-1 v2: methodology-changelog as source-of-truth) deferred to a future slice IF cross-cutting friction surfaces between v1.1 META-1 PMI-1 INST-1 interactions. ~1-2 hour slice at minimum (introduces a parse step on the methodology-changelog markdown structure).

## Pre-finish gate (from mission brief, updated)

- [ ] All 5 acceptance criteria PASS with evidence in validation.md (per the AC-trace table above)
- [ ] All 7 must-not-defer items addressed (per mission brief list)
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes (every TF-1 row PASSING per the 7-row plan above)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes after version bump + methodology-changelog edits (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full test suite passes
- [ ] Shippability catalog row 14 written + catalog re-run all PASS
- [ ] Bidirectional sha256 capture in build-log.md (Phase 0 + Phase 4) for all 6 surfaces (methodology-changelog.md × 2 + test file + VERSION + plugin.yaml + ai-sdlc-VERSION)
- [ ] ADR-013 written with reversibility class `cheap with magnitude-of-revert justification` per slice-010/011/012/013 ADR convention
- [ ] EPGD-1 self-application empirical verification at Phase 4: pre-Edit grep 7 entry-pin functions; post-Edit grep 8 entry-pin functions; 0 of 7 prior entry-pin functions touched (verified by diff inspection)
