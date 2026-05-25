# Critique: Slice 003 add-val-1-imports-allowlist

**Critic reviewed**: mission-brief.md, design.md, ADR-002-val-1-imports-allowlist-explicit-flag.md
**Date**: 2026-05-09
**Result**: CLEAN (post-triage; all 7 findings ACCEPTED-FIXED)
**Voluntary**: yes — risk-tier=low, critic-required=false; user invoked `/critique` anyway, consistent with slice-001 + slice-002 voluntary-Critic pattern (3rd consecutive low-tier slice using voluntary Critic).

## Summary

Design is small, additive, and well-scoped. The contract is correct, the AC #3 finding-count math (5 today → 0 after fix) checks out, and the approach is consistent with the existing `_normalize_pkg` / `_check_import_resolves` patterns. **0 blockers, 2 majors, 5 minors**. Two real issues stand out: (M1) **methodology-conformance miss** — the must-not-defer item "SKILL.md Step 5b prose updated" had no test-first row protecting it, replicating the slice-001/slice-002 Critic miss-class flagged in calibration awareness; (M2) **internal contradiction** — design.md described the Python API's empty-entry handling two contradictory ways. Plus a handful of minors (PEP 503 mislabeling, runtime-environment quoting on Windows, dotted-package edge case, error-model row clarity, implementation-sketch insertion-point ambiguity).

**Calibration win**: M1 confirms the "methodology-conformance" miss-class pattern (N=3 across slice-001 + slice-002 + slice-003) — `/critic-calibrate` threshold (≥3 distinct slices) is now reached.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: must-not-defer item "SKILL.md Step 5b prose updated" has no test-first row — methodology-conformance gap
- **Claim under review**: mission-brief.md must-not-defer item #4: *"`skills/validate-slice/SKILL.md` Step 5b prose updated to document both new resolution paths (setuptools-packages auto-read + `--imports-allowlist` flag) so the methodology stays self-documenting"*; design.md "What's new" similarly says the SKILL.md prose is updated.
- **Issue**: The test-first plan (mission-brief.md AC #1–#3, 7 rows) maps every AC to a test, but **no row covers the prose update**. The existing prose-pin `test_validate_slice_skill_references_val_1` (in `tests/methodology/test_validate_slice_layers.py:404`) only asserts `"VAL-1"`, `"validate_slice_layers"`, `"credential scan"`, `"hallucinat"` substrings — none of which exercise the new prose. Pre-finish gate item "Must-not-defer list fully addressed" has no programmatic check; an implementer who forgets to update SKILL.md still passes every gate. This exactly replicates the Critic miss-class flagged in calibration awareness ("methodology-conformance: design's claim about how tools work doesn't match implementation"; the symmetric form here is "design's must-not-defer claim about prose update has no enforcement"). The slice's own milestone.md Critic-target item (c) explicitly anticipates this drift risk.
- **Evidence**: `tests/methodology/test_validate_slice_layers.py:404-417` — current prose-pin scope; mission-brief.md "Test-first plan" (pre-fix) — 7 rows, none for SKILL.md prose; mission-brief.md "Must-not-defer" item #4 (pre-fix); calibration awareness note "methodology-conformance accumulating, N=2".
- **Proposed fix**: Promote must-not-defer item #4 to AC #4 with its own test-first row (`test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages` — asserts both literal substrings `--imports-allowlist` AND `[tool.setuptools] packages` appear in `skills/validate-slice/SKILL.md`).
- **Builder draft**: ACCEPTED-FIXED — applied to `mission-brief.md` (new AC #4 + new test-first row #8 + verification-plan row + must-not-defer item demoted to parenthetical) and `design.md` (What's new updated; testing strategy updated; reference to the new test). 4 ACs / 8 rows now; pre-finish gate updated.

#### M2: design.md contradicts itself on Python-API empty-entry handling — pick one, stick with it
- **Claim under review**: design.md "Contracts added or changed" → "run_layers Python API" → *"invalid entries (after `_normalize_pkg` returns empty) raise `ValueError` to surface programmer error"*; vs. design.md "Error model for this slice" → table row *"`imports_allowlist=[\"\"]` (Python API) | run_layers | values that normalize to empty are silently skipped (be liberal in what you accept programmatically; strict only at the CLI boundary). No `ValueError` in v1"*.
- **Issue**: These are not reconcilable. One says raise; the other says silently skip. The implementation sketch in design.md shows `if normalized: declared.add(normalized)` — silently skipping. The test-first plan has `test_imports_allowlist_rejects_empty_string` — that test name is ambiguous (rejects how? raise, or via `parser.error`?). Without disambiguation, the implementer will likely write the test for whichever side they read first, and the artifact / behavior will diverge from the contract.
- **Evidence**: design.md "Contracts added or changed" subsection (Python API error cases, pre-fix); design.md "Error model for this slice" table (3rd row); design.md "Implementation sketch" (run_layers body); mission-brief.md test-first plan row 5 (`test_imports_allowlist_rejects_empty_string` — venue ambiguous pre-fix).
- **Proposed fix**: Align contract with implementation sketch and "be liberal" principle — Python API silently skips empty-after-normalize; ONLY the CLI rejects via `parser.error()`. Rename test-first row to `test_cli_imports_allowlist_rejects_empty_string` (CLI-level explicit). Update design.md "Contracts added or changed" to drop the "raise `ValueError`" claim.
- **Builder draft**: ACCEPTED-FIXED — applied to `design.md` "Contracts added or changed" section (Python API now explicitly lenient; CLI explicitly strict; asymmetry rationale added) and `mission-brief.md` test-first row #5 (renamed to `test_cli_imports_allowlist_rejects_empty_string`; type changed to integration; verification-plan entry updated).

### Minors (log; address if cheap)

#### m1: "PEP 503-normalized" wording is technically wrong — the codebase normalizes to underscores, PEP 503 specifies hyphens
- **Claim under review**: design.md (multiple places) and ADR-002 ("Decision" section) state values are *"PEP 503-normalized via `_normalize_pkg`"*.
- **Issue**: PEP 503: *"The name should be lowercased with all runs of the characters `.`, `-`, or `_` replaced with a single `-` character."* The codebase's `_normalize_pkg` replaces with `_`. Documentation/citation accuracy bug.
- **Evidence**: `tools/validate_slice_layers.py:258-260` (`re.sub(r"[-_.]+", "_", name.strip().lower())`); [PEP 503 § Normalized Names](https://peps.python.org/pep-0503/).
- **Proposed fix**: Rename phrasing to "name-normalized via `_normalize_pkg`" with a one-line note explaining the codebase deviates from strict PEP 503 (uses `_` not `-`).
- **Builder draft**: ACCEPTED-FIXED — applied to `design.md` (all 3 occurrences) and `ADR-002` (Decision section now carries the explicit codebase-vs-PEP-503 note + cites PEP 503). Mission-brief must-not-defer item also updated. Did NOT change `_normalize_pkg` behavior — that would silently break existing tests; this is a doc-accuracy fix only.

#### m2: mid-slice smoke command uses Bash line-continuation `\` but the user is on Windows / PowerShell
- **Claim under review**: mission-brief.md "Mid-slice smoke gate" code block used `\` continuation (Bash syntax).
- **Issue**: User's environment is Windows PowerShell. Backslash `\` is Bash; in PowerShell it's literal. Copy-paste produces parse errors. Runtime-environment miss-class flagged in calibration awareness; slice-001 + slice-002 explicitly captured this lesson.
- **Evidence**: mission-brief.md "Mid-slice smoke gate" (pre-fix); CLAUDE.md `# Shell preference`; slice-001 lessons-learned PowerShell here-string entry.
- **Proposed fix**: Collapse to a single line — at <300 chars it fits. Shell-agnostic.
- **Builder draft**: ACCEPTED-FIXED — applied to `mission-brief.md` "Mid-slice smoke gate" — single-line invocation with explicit "works in PowerShell AND Bash" note + slice-001 cross-shell lesson cited.

#### m3: setuptools-packages reading handles flat package list but quietly underserves dotted-only declarations
- **Claim under review**: design.md "Implementation sketch" #1 — flat-list reading.
- **Issue**: For `packages = ["mypkg.sub"]` with no bare `"mypkg"`, `mypkg_sub` is added to `declared` but `from mypkg.sub.x import y` resolves on `import_top = "mypkg"` which is not in `declared`. ADR-002 Consequences claimed "Future projects ... using [tool.setuptools.packages.find] will see false-positive findings"; did not warn about the parallel dotted-only case.
- **Evidence**: `tools/validate_slice_layers.py:315-329` (`_check_import_resolves` uses `top` only); [setuptools docs](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).
- **Proposed fix**: Document as a known limitation in ADR-002 Consequences with the workaround (`--imports-allowlist mypkg`). Don't add the top-component-derive logic — that's the same kind of magic ADR-002 explicitly rejects for the `tests` case (consistency win).
- **Builder draft**: ACCEPTED-FIXED — applied to `ADR-002` Consequences (new bullet documenting the dotted-only case + workaround + rationale for not auto-deriving).

#### m4: design.md error-model row "imports_allowlist=[\"\"] (Python API)" doesn't explicitly mention whitespace-only API path
- **Claim under review**: design.md "Error model for this slice" 3rd row covered only the empty-string API case.
- **Issue**: A future reader might assume API rejects whitespace too. CLI strips before validating; API normalizes (which calls `.strip()` internally inside `_normalize_pkg`). Behaviors are aligned (silent-skip in API), but row label was incomplete.
- **Evidence**: `tools/validate_slice_layers.py:258-260` (`_normalize_pkg` calls `.strip()`); design.md "Error model" table.
- **Proposed fix**: Extend row label to mention whitespace-only and `None`-like inputs.
- **Builder draft**: ACCEPTED-FIXED — applied to `design.md` "Error model" table — row 3 expanded.

#### m5: implementation sketch for `parse_declared_deps` insertion point is ambiguous about scope (inside vs outside the `if pyproject_path` branch)
- **Claim under review**: design.md "Implementation sketch" #1: *"after the Poetry block (around line 302), before the requirements.txt block"*.
- **Issue**: Line 302 is INSIDE the `if pyproject_path and ... :` block. New code uses `data.get(...)` — `data` is only defined inside that branch. An implementer interpreting the location as outer-scope-between-blocks gets `NameError`.
- **Evidence**: `tools/validate_slice_layers.py:263-312` — function structure.
- **Proposed fix**: Reword location guidance to be explicit about the branch.
- **Builder draft**: ACCEPTED-FIXED — applied to `design.md` "Implementation sketch" #1 — reworded to "inside the existing `if pyproject_path ...` block, after the Poetry-dev-deps loop".

## Dimensions checked

- [x] **Unfounded assumptions** — m1 (PEP 503 mislabeled). AC #3's "5 → 0" math independently verified by counting top-level imports across the 3 referenced files (3 `tests` + 2 `tools` after dedup = 5).
- [x] **Missing edge cases** — m3 (dotted-only setuptools packages), m4 (whitespace handling clarity).
- [x] **Over-engineering** — none. ~30 lines of production code, 8 tests; well-scoped. ADR-002 explicitly rejects 4 alternative-design options; chose smallest defensible delta.
- [x] **Under-engineering** — M1 (must-not-defer item without test row).
- [x] **Contract gaps** — M2 (Python API error-handling self-contradiction); m4 (whitespace path under-described).
- [x] **Security** — none. No auth, secrets handling, IDOR, or injection paths introduced. The `_normalize_pkg("*") = "*"` worst-case adds a literal `*` to a `set` — only resolves imports of literal `*` (syntax error). No exploit surface.
- [x] **Drift from vault** — none material. INST-1 (v0.20.0) cited correctly; ADR-002 doesn't supersede ADR-001; no R-3 risk-register entry needed (methodology-gap fix, not risk-retire). m5 (implementation-sketch location wording) is the only minor drift-from-implementation hand-wave.
- [x] **Web-known issues** — m1 (PEP 503 normalization spec mismatch). [Setuptools 82.0.1 docs](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html): explicit `packages = [...]` and auto-`find` are mutually exclusive — design's choice to read only the explicit-list form is internally safe (a `find`-mode project will never have a non-empty `packages` list to confuse the parser). [Setuptools issue #4703](https://github.com/pypa/setuptools/issues/4703) supports the design's choice to NOT touch `find`. No current deprecations of the explicit-list form. tomllib stable.

## Triage

**Triaged by**: user
**Date**: 2026-05-09
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major    | ACCEPTED-FIXED | Promoted must-not-defer item #4 to AC #4 + new test-first row #8 (prose-pin); applied to mission-brief.md + design.md |
| M2 | Major    | ACCEPTED-FIXED | Aligned contract with lenient-API/strict-CLI implementation; renamed test row #5 to CLI-explicit; applied to design.md + mission-brief.md |
| m1 | Minor    | ACCEPTED-FIXED | Renamed "PEP 503-normalized" → "name-normalized" with explanatory note in design.md + ADR-002 |
| m2 | Minor    | ACCEPTED-FIXED | Mid-slice smoke command collapsed to single line; applied to mission-brief.md |
| m3 | Minor    | ACCEPTED-FIXED | Documented dotted-only limitation in ADR-002 Consequences with workaround |
| m4 | Minor    | ACCEPTED-FIXED | Error-model row 3 expanded to cover whitespace + None-like inputs in design.md |
| m5 | Minor    | ACCEPTED-FIXED | Reworded `parse_declared_deps` insertion-point guidance in design.md to be explicit about branch scope |
