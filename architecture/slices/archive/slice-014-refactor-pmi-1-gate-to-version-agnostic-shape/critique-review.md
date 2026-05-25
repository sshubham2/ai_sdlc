# Critique Review: Slice 014 refactor-pmi-1-gate-to-version-agnostic-shape

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-13
**First-Critic verdict**: CLEAN
**Dual-review verdict**: EXTEND

## Summary

First Critic's coverage on the build-phase ordering (M1), the monkeypatch name-resolution (M2), and the artifact-consistency issues (m1/m2/m3) is sharp and the dispositions all correctly ACCEPTED-FIXED. One concrete missed concern surfaces from a second-pass read of the canonical proposed function bodies + design.md "Edit boundaries": neither `import pytest` nor `import ast` is named in design.md's "What's new" / Edit-discipline boundaries, yet the canonical regression-test body uses `pytest.raises` and two TF-1 rows (2 + 4) describe AST-walking. Existing `tests/methodology/test_methodology_changelog.py` does not import either symbol.

## Confirmed findings

All five first-Critic findings are VALID with correct severities:

- **M1**: META-1 transient breakage window — confirmed VALID; Major is appropriate. design.md `## Phase plan` post-fix lines 167-273 explicitly enumerates Phase 0..4 with Phase 2 as the single atomic-commit step packaging changelog write + forward-sync + 3 version bumps + ADR-013 write. The mission-brief must-not-defer item (line 72) names "META-1 invariant atomicity (post-/critique M1 ACCEPTED-FIXED)" with reference to design.md Phase plan. Cross-referenced against `test_methodology_changelog.py:33-49` (`test_version_matches_most_recent_changelog_entry`) — META-1 would fire at any intermediate state. Framework: Hendrickson (operational invariants under partial-state transitions).
- **M2**: Monkeypatch target name-resolution semantics — confirmed VALID; Major is appropriate. Verified at `test_methodology_changelog.py:7` (`from tests.methodology.conftest import REPO_ROOT`) and conftest.py:6 (`REPO_ROOT = Path(__file__).resolve().parents[2]`). The bare `REPO_ROOT` reference inside `_invariant`'s body (design.md line 335-337) resolves from `test_methodology_changelog`'s module globals, NOT from `conftest`. Patching `conftest.REPO_ROOT` would indeed silently no-op (the gate would still read real VERSION/plugin.yaml files both at 0.28.0 → match → AssertionError NOT raised → `pytest.raises` raises `DID NOT RAISE` → test fails for the wrong reason). The post-fix `## Regression test fixture spec` (design.md lines 103-165) pins the target string `"tests.methodology.test_methodology_changelog.REPO_ROOT"` correctly. Framework: Newman / Fowler (test-isolation contract pinning).
- **m1**: ADR-013 reversibility frontmatter vs body — confirmed VALID; Minor is appropriate. Verified ADR-013 frontmatter line 6 reads `reversibility: cheap` (single token) and body line 150 says `Class: cheap.` with magnitude-of-revert justification following in prose. Option (c) disposition correctly preserves single-token convention; ADR-012 (just verified at line 6) is the cited precedent and uses the same shape.
- **m2**: Phase labels scattered — confirmed VALID; Minor is appropriate. design.md `## Phase plan` section now exists at lines 167-273 with 8 phases explicitly enumerated.
- **m3**: TF-1 row-count divergence between mission-brief (11 rows) and design.md (7 rows) — confirmed VALID; Minor is appropriate. Verified mission-brief.md lines 26-47 now hold the 7-row consolidated plan with function names matching design.md TF-1 table (lines 379-389) exactly. `tools/test_first_audit.py` exists at `tools/test_first_audit.py` (parses mission-brief.md per the first Critic's claim). Framework: Wiegers AC-trace (single-source-of-truth for TF-1 row enumeration).

## Suspicious findings

No suspicious findings. All 5 first-Critic findings are well-grounded; none reach over-reach territory.

## Missed findings

**M-add-1: `import pytest` and `import ast` not pinned in design.md "Edit boundaries" or "What's new" — canonical test bodies will NameError at Phase 1d smoke gate**

- **Claim under review**: design.md `## What's new` (lines 13-20) enumerates 7 new test functions; `## Components touched / tests/methodology/test_methodology_changelog.py / Edit boundaries (EPGD-1 self-application narrow-scope)` (lines 49-53) names the gate-supersession Edit + Phase 1b INSERTs; `## Regression test fixture spec` (lines 109-158) pins the canonical regression-test function body using `pytest.raises(AssertionError) as excinfo`; Audit 1 (lines 315-346) pins the canonical `_invariant` body. Two TF-1 rows describe AST-walking: row 2 ("AST-walks `test_methodology_changelog.py`'s module looking for any `Constant(value=str)` matching ...", mission-brief line 40, design.md line 16/313) and row 4 ("AST-walks the module looking for any `FunctionDef.name` matching ...", mission-brief line 42, design.md line 16).
- **Issue**: Empirically verified in `tests/methodology/test_methodology_changelog.py` — current file has no `import pytest` and no `import ast` statement (Grep confirmed: zero matches for `^import pytest`, zero for `^import ast`, zero for `pytest\.` anywhere in the file). The canonical regression-test body (design.md line 144) calls `pytest.raises(AssertionError) as excinfo`; the two AST meta-tests require `ast.parse(...)` + `ast.walk(...)` to walk the module. Neither symbol is pre-imported. design.md `## What's new` lists new functions but does NOT list `import pytest` or `import ast` as additions; `## Edit-discipline boundaries` Phase 1b/1c describe `old_string` / `new_string` boundaries on SECTION-header-anchored function-bodies but never include the imports header (top of file, line 1-7).
- **Evidence**:
  - Grep on `tests/methodology/test_methodology_changelog.py` for `^import pytest` → zero matches
  - Grep on same file for `^import ast` → zero matches
  - Grep on same file for `pytest\.` → zero matches (confirms not even a transitive usage)
  - design.md line 144: `with pytest.raises(AssertionError) as excinfo:` — canonical body uses `pytest` as a bare module-level name
  - design.md line 16: `test_pmi_1_gate_function_is_version_agnostic_shape — AST meta-test pinning the absence of version-literal Constants inside the gate function body` — requires `ast` module
  - design.md line 40 (mission-brief): "AST-walks `test_methodology_changelog.py`'s module looking for any `Constant(value=str)` matching `r"^\d+\.\d+\.\d+$"`" — requires `ast.parse` + `ast.walk` + `isinstance(node, ast.Constant)`
  - Phase 1d expected outcome (design.md line 234-237) claims row 2 (`_is_version_agnostic_shape`), row 3 (regression), and row 4 (`_no_per_version_pmi_1_gate_functions_remain`) all PASS at the mid-slice smoke gate. With `import pytest` and `import ast` missing, row 2 + row 3 + row 4 would all fail with `NameError: name 'pytest' is not defined` / `NameError: name 'ast' is not defined` at collection or first call — Phase 1d would STOP with "most likely cause: Edit pulled adjacent SECTION content" (per design.md line 239), which would be a misdiagnosis. The real root cause is missing imports never added by Phase 1b/1c Edits.
- **Framework**: Sommerville (build-step completeness — every dependency introduced by a new test function must be explicitly added before test execution); Fowler (test-isolation prerequisite — imports are the runtime contract of a test module, never implicit).
- **Proposed fix**: Add to design.md `## Components touched / tests/methodology/test_methodology_changelog.py / Edit boundaries` (or `## What's new`) an explicit additional Edit before Phase 1b: `old_string` = the current import-block (lines 1-7: `"""Validate the methodology-changelog itself: format, version sync, dated entries."""\nimport re\nfrom pathlib import Path\n\nimport yaml\n\nfrom tests.methodology.conftest import REPO_ROOT, read_file\n`); `new_string` = same plus `import ast\nimport pytest\n` inserted in alphabetical order. Alternatively, package these into Phase 1b's INSERT preamble. Pin this in the Phase plan as Phase 1a' (sub-phase between 1a empirical audit and 1b INSERT) so the smoke-gate at Phase 1d cleanly distinguishes "EPGD-1 violation" from "missing imports" diagnostic paths. Severity: **Major** — silently misdiagnoses Phase 1d failure as EPGD-1 violation, exactly the diagnostic-clarity discipline EPGD-1 was codified to preserve (slice-013 codification context); a Builder seeing 3 of 4 smoke-gate rows fail at NameError would default to "I broke the Edit narrow-scope" and re-verify boundaries on already-correct Edits, burning ~10-15 min before reaching the real diagnosis.

## Severity adjustments

No severity adjustments. The first Critic's Blocker/Major/Minor assignments are well-calibrated against impact.

## Notes

Confidence in this meta-review: high on M-add-1 (empirically verified via Grep across the entire `tests/` tree — no `import pytest` and no `import ast` in the target file; current `pytest.` usages in sibling files confirm pytest is consistently imported explicitly per-module rather than transitively); medium-high on the 5 first-Critic dispositions (all five fix paths are sound; M1's Phase plan + M2's regression-test-fixture-spec are particularly thorough additions). Calibration observation: the first Critic's slice-014 review continues the slice-006-013 cumulative 67/67 streak on confirmed findings, but exhibits the same blind spot the meta-Critic caught at slice-013 (M-add-1 there) — namely, symmetric-supporting-code completeness checks across the canonical body the design pins. Two slices in a row now show "the first Critic catches the design-semantic issue at the canonical body but misses the runtime-prerequisite at the canonical body's surrounding context". This is a candidate pattern for `/critic-calibrate` aggregation if it surfaces at slice-015 — would propose codifying "canonical-body imports-and-fixtures completeness check" as a Dim 9 sub-clause refinement under structural-prerequisites. Reservation: M-add-1 is genuinely missed but the cost is moderate (10-15 min misdiagnosis at Phase 1d, not a structural defect at /validate-slice or beyond); calling it Major (not Minor) hinges on the diagnostic-clarity-discipline framing — EPGD-1 self-application makes failure-mode-ambiguity at smoke gate more costly than usual on this particular slice. Builder should verify the imports issue empirically at Phase 1a before Phase 1b begins — adding `import ast` + `import pytest` is a 30-second Edit that retires the entire risk class.

Relevant absolute file paths examined:
- <HOME>\ai_sdlc\architecture\slices\slice-014-refactor-pmi-1-gate-to-version-agnostic-shape\mission-brief.md
- <HOME>\ai_sdlc\architecture\slices\slice-014-refactor-pmi-1-gate-to-version-agnostic-shape\design.md
- <HOME>\ai_sdlc\architecture\slices\slice-014-refactor-pmi-1-gate-to-version-agnostic-shape\critique.md
- <HOME>\ai_sdlc\architecture\decisions\ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md
- <HOME>\ai_sdlc\architecture\decisions\ADR-012-promote-entry-pin-vs-pmi-1-gate-discipline-to-critique-dim-9-sub-clause.md
- <HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py
- <HOME>\ai_sdlc\tests\methodology\conftest.py
- <HOME>\ai_sdlc\methodology-changelog.md
