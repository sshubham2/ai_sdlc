# Critique: Slice 014 refactor PMI-1 gate to version-agnostic shape

**Critic reviewed**: mission-brief.md, design.md, ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md
**Date**: 2026-05-13
**Result**: NEEDS-FIXES (initial) → CLEAN (post-disposition, all findings ACCEPTED-FIXED inline)

## Summary

Design is well-considered and the refactor target is right-sized. Two majors: (M1) the build-phase ordering of the methodology-changelog v0.29.0 entry insertion vs. the atomic version bump is unpinned, creating a META-1 transient breakage window (different invariant than PMI-1 but the same "atomicity discipline broken" family); (M2) the proposed `_invariant` regression test's monkeypatch target is plausible but the design does not pin which *symbol* is patched, and Python's name-resolution semantics determine whether the regression actually exercises the cross-file equality path. Three minors: (m1) ADR-013 frontmatter "cheap" vs body "cheap with magnitude-of-revert justification" inconsistency; (m2) Phase labels scattered across design.md without a single ordered enumeration; (m3) TF-1 row count divergence between mission-brief (11 rows) and design.md (7 rows) — `tools/test_first_audit.py` parses mission-brief and would refuse at strict-pre-finish on 4 phantom rows.

All 5 findings ACCEPTED-FIXED inline at design-stage (no items DEFERRED, OVERRIDDEN, or ESCALATED). Final verdict CLEAN.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: Phase ordering between v0.29.0 changelog entry creation and atomic version bump is unpinned; creates a META-1 transient breakage window

- **Claim under review**: design.md "At /build-slice Phase 0 (BEFORE any Edit) and Phase 4 (AFTER all Edits + version bumps + commits)..."; mission-brief "At ~50% of build (after writing the new `_invariant` test + 2 AST meta-tests but BEFORE the version bump or methodology-changelog edits), run [smoke gate]"; mission-brief "version bump is the LAST step before final test run".
- **Issue**: The PMI-1 invariant (`VERSION == plugin.yaml.version`) is atomic on a 2-file basis. But the slice ALSO writes a v0.29.0 methodology-changelog entry. The existing META-1 test `test_version_matches_most_recent_changelog_entry` at `tests/methodology/test_methodology_changelog.py:33` will FAIL the moment the v0.29.0 changelog entry is written if VERSION still says "0.28.0". If methodology-changelog edits are made BEFORE the atomic version bump (which the mission-brief sequencing "version bump is the LAST step" implies — read literally), META-1 will fire for the duration of that interval. Conversely if methodology-changelog edits are made AFTER the version bump, then between `VERSION=0.29.0` and changelog entry write, META-1 fires the OTHER way (VERSION says 0.29.0 but most-recent changelog heading still 0.28.0). The phase plan is therefore inherently lossy on META-1 atomicity unless the changelog entry write and the VERSION/plugin.yaml/ai-sdlc-VERSION bumps are committed in the SAME Edit-sequence-as-one-atomic-build-phase. Design.md does not pin this sequencing.
- **Evidence**: mission-brief.md (smoke gate spec); design.md (Phase 0 / Phase 4 sha256 capture spec); `test_methodology_changelog.py:33-49` (`test_version_matches_most_recent_changelog_entry` — the META-1 test that fires at the intermediate state).
- **Proposed fix**: Add explicit ordered Phase plan to design.md (Phase 0 → 1a → 1b → 1c → 1d → 2 → 3 → 4) with Phase 2 as a SINGLE atomic operation packaging (a) v0.29.0 entry write in-repo, (b) forward-sync to installed, (c) VERSION bump, (d) plugin.yaml.version bump, (e) ai-sdlc-VERSION bump, (f) ADR-013 write — full test suite NOT run between (a) and (f). Add mission-brief must-not-defer: "META-1 invariant atomicity (post-/critique M1 ACCEPTED-FIXED): Phase 2 is a single atomic build operation".
- **Builder draft**: ACCEPTED-FIXED — applied at design.md `## Phase plan (post-/critique M1 + m2 ACCEPTED-FIXED — explicit ordered enumeration)` section (Phase 0..4 enumerated with Phase 2 as the atomic-commit step); mission-brief.md must-not-defer extended with the META-1 atomicity bullet.

#### M2: Regression-test `monkeypatch` target depends on a name-resolution mechanism that is not pinned in the design; risk of silent test-no-op

- **Claim under review**: design.md "The new regression test (`test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge`) uses pytest's `monkeypatch` fixture to replace the module-level `REPO_ROOT` symbol with a tempdir."
- **Issue**: `test_methodology_changelog.py:7` is `from tests.methodology.conftest import REPO_ROOT`. That binds `REPO_ROOT` as a module-local name in `test_methodology_changelog`. `monkeypatch.setattr("tests.methodology.test_methodology_changelog.REPO_ROOT", tmp_path)` rebinds the module-local symbol; the proposed `_invariant` body uses bare `REPO_ROOT`, which Python resolves at call-time from the function's enclosing-module globals (i.e., `test_methodology_changelog`'s globals). The monkeypatch's setattr on that module's `REPO_ROOT` attribute will be visible to the call — **this works**. BUT the design does not explain WHY it works — and the alternative wording "module-level REPO_ROOT symbol" is ambiguous between (a) `conftest.REPO_ROOT` (the imported original) and (b) `test_methodology_changelog.REPO_ROOT` (the local rebinding). Patching (a) would NOT affect the gate function (Python's name resolution finds the module-local binding first), so a Builder reading "module-level REPO_ROOT" and naively patching `tests.methodology.conftest.REPO_ROOT` would write a silently-no-op regression test (gate would still read real VERSION/plugin.yaml files, both at 0.28.0 → match → AssertionError NOT raised → `pytest.raises(AssertionError)` itself raises `DID NOT RAISE` → test fails for the wrong reason). Additionally: the tempdir fixture needs `(tmp_path / "plugin.yaml")` with at minimum a `version:` key; if missing, `plugin_manifest["version"]` raises `KeyError` not `AssertionError`.
- **Evidence**: `test_methodology_changelog.py:7` (`from tests.methodology.conftest import REPO_ROOT`); design.md ambiguity in monkeypatch claim; Audit 1's proposed body using bare `REPO_ROOT`.
- **Proposed fix**: In design.md, pin EXACTLY (a) the monkeypatch target string `"tests.methodology.test_methodology_changelog.REPO_ROOT"` with a docstring explaining why patching `conftest.REPO_ROOT` would silently no-op; (b) the tempdir fixture content (VERSION + plugin.yaml minimum-YAML); (c) the assertion order — per-substring assertions (NOT joined by `and`) so failure message distinguishes which substring is missing.
- **Builder draft**: ACCEPTED-FIXED — applied at design.md `## Regression test fixture spec (post-/critique M2 ACCEPTED-FIXED — pin the name-resolution semantics)` subsection with the canonical proposed `def test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge(tmp_path, monkeypatch):` body, including the docstring explaining `conftest.REPO_ROOT` vs `test_methodology_changelog.REPO_ROOT` name-resolution.

### Minors (log; address if cheap)

#### m1: ADR-013 reversibility field — frontmatter "cheap" contradicts design.md "cheap with magnitude-of-revert justification" subtle nuance

- **Claim under review**: ADR-013 frontmatter `reversibility: cheap`; ADR-013 body `Class: cheap with magnitude-of-revert justification.`; design.md `reversibility: **cheap with magnitude-of-revert justification**`.
- **Issue**: Frontmatter is a single word `cheap`. Body and design.md add qualifier "with magnitude-of-revert justification". If tooling parses ADR frontmatter, it sees the bare "cheap" and misses the nuance. Per Sommerville (requirements-design traceability) + ISO/IEC/IEEE 42010 (architecture description consistency) the frontmatter should either match the body's full classification phrase or include a structured sub-field.
- **Evidence**: ADR-013 frontmatter line 6; ADR-013 body Reversibility header.
- **Proposed fix**: Option (a) extend frontmatter to a hyphenated single-token; option (b) add `reversibility-notes:` sibling field; option (c) accept frontmatter is summary-only and explicitly note in body. Critic-proposed cheapest fix: option (a).
- **Builder draft**: ACCEPTED-FIXED via option (c) — preserves ADR 003/004/006-012 frontmatter single-token convention (introducing `cheap-with-magnitude-of-revert` as a new hyphenated keyword would break that convention). ADR-013 body Reversibility section now explicitly says "Class: cheap. Frontmatter `reversibility: cheap` matches ADRs 003/004/006-012 single-token convention. Magnitude-of-revert justification follows in body prose below." Design.md ADRs reference now reads "reversibility: cheap (frontmatter class — matches ADRs 003/004/006-012 convention). Magnitude-of-revert justification documented in ADR-013's `## Reversibility` section body."

#### m2: Design.md "Components touched" → test_methodology_changelog.py "Edit boundaries" lists "Phase 1c" but the design has no top-level ordered Phase list

- **Claim under review**: design.md references "Phase 1c", "Phase 1b", "Phase 1a", "Phase 4" in cross-cutting prose, but the design as a whole lacks a single ordered enumeration of Phases.
- **Issue**: Builder is expected to follow a Phase plan; design's Phase labels are inherited from slice-010/011/012/013 conventions but never enumerated explicitly here. New readers (Critic, future calibration runs, /handoff-ai) have to infer ordering. Per Wiegers + Patton — a single explicit Phase list reduces friction.
- **Evidence**: scattered Phase references in design.md; mission-brief.md has no Phase enumeration.
- **Proposed fix**: Add 6-bullet Phase plan section to design.md (overlaps with M1's fix). Phase 0 → Phase 1a → Phase 1b → Phase 1c → Phase 2 (atomic commit) → Phase 3 (full-suite) → Phase 4 (sha256 capture) with 1-line content each.
- **Builder draft**: ACCEPTED-FIXED — combined with M1 fix at design.md `## Phase plan (post-/critique M1 + m2 ACCEPTED-FIXED — explicit ordered enumeration)` section. 8 Phases enumerated (Phase 0, 1a, 1b, 1c, 1d, 2, 3, 4) with full content per phase.

#### m3: TF-1 row count divergence between mission-brief (11 rows) and design.md (7 rows) is unpinned in mission-brief

- **Claim under review**: mission-brief.md (11-row TF-1 table); design.md (7-row table). Design.md prose explains the consolidation, but the mission-brief was not amended to reflect.
- **Issue**: Per slice-008 M1 codification (Wiegers AC-trace), TF-1 row counts should be authoritative in ONE place. `tools/test_first_audit.py` parses mission-brief.md, not design.md. With 11 rows in mission-brief and 7 functions actually built, 4 rows reference test functions that don't exist; they'll be flagged WRITTEN-FAILING permanently (NameError). The audit refuses any non-PASSING row at strict-pre-finish. Function-name strings also diverge — mission-brief row 5 says `test_changelog_v_0_29_0_entry_pins_pmi_1_refactor_canonical_phrase_in_repo` but design.md row 5 says `test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed`.
- **Evidence**: mission-brief TF-1 table (11 rows); design.md TF-1 table (7 rows); `tools/test_first_audit.py` parses mission-brief.md as the authoritative artifact.
- **Proposed fix**: Amend mission-brief.md TF-1 table to match design.md's 7-row consolidation; choose ONE function-name canonical form and propagate.
- **Builder draft**: ACCEPTED-FIXED — mission-brief.md TF-1 table replaced with the 7-row consolidated plan matching design.md naming (`test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` + `test_v_0_29_0_entry_names_supersession_pattern_retired` + `test_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase` as the AC #4 trio). Mission-brief footnote notes updated to remove references to dropped rows 5/6/8/11. Out-of-scope reaffirmation added: install_audit untouched.

### Meta-Critic additions (from /critique-review DR-1 EXTEND verdict)

#### M-add-1: `import pytest` and `import ast` not pinned in design.md "Edit boundaries" or "What's new" — canonical test bodies will NameError at Phase 1d smoke gate

- **Source**: critique-review.md `## Missed findings`. Caught by meta-Critic via /critique-review dual-review; first Critic missed.
- **Severity**: Major (per meta-Critic — diagnostic-clarity-discipline framing; EPGD-1 self-application makes failure-mode-ambiguity at smoke gate costly).
- **Claim under review**: design.md `## What's new` enumerates 7 new test functions; `## Components touched / Edit boundaries (EPGD-1 self-application narrow-scope)` names the gate-supersession Edit + Phase 1b INSERTs; `## Regression test fixture spec` pins the canonical regression-test function body using `pytest.raises(AssertionError) as excinfo`; Audit 1 pins the canonical `_invariant` body. Two TF-1 rows describe AST-walking.
- **Issue**: Current `tests/methodology/test_methodology_changelog.py` has no `import pytest` and no `import ast` (Grep confirmed: zero matches for `^import pytest`, zero for `^import ast`, zero for `pytest\.`). The canonical regression-test body calls `pytest.raises`; the 2 AST meta-tests need `ast.parse` + `ast.walk` + `isinstance(node, ast.Constant)`. Without explicit imports, Phase 1d smoke gate rows 2+3+4 fail with `NameError`. Design.md diagnostic guidance at Phase 1d (`"most likely cause: Edit pulled adjacent SECTION content"`) would misdiagnose as EPGD-1 violation, burning ~10-15 min on already-correct Edit boundaries.
- **Evidence**: Grep on `tests/methodology/test_methodology_changelog.py` confirms missing imports. design.md regression-test body uses `pytest`; AST meta-tests need `ast`. Phase 1d expected outcome claims all 4 smoke rows PASS — would NameError without the imports.
- **Proposed fix** (per meta-Critic): Add Phase 1a' (sub-phase between empirical audit Phase 1a and INSERT Phase 1b) as an explicit narrow-scoped Edit on the imports block: `old_string` = current imports (lines 1-7); `new_string` = same + `import ast` + `import pytest` in PEP-8 stdlib→third-party→first-party grouping. 30-second fix that retires the entire risk class.
- **Builder draft**: ACCEPTED-FIXED — applied at design.md `## Phase plan / Phase 1a' — Imports preamble Edit (post-/critique-review M-add-1 ACCEPTED-FIXED)` section with full canonical Edit `old_string`/`new_string` + PEP-8 conformance note + reference to /critique-review M-add-1.

## Dimensions checked

- [x] Unfounded assumptions — M2 (monkeypatch target name-resolution claim is correct but unjustified in design prose); m3 (TF-1 row count divergence reflects unstated assumption mission-brief would be later amended). Both ACCEPTED-FIXED.
- [x] Missing edge cases — M2 (silent no-op if monkeypatch target wrong); M1 (META-1 transient breakage edge case). Both ACCEPTED-FIXED. No findings on load/concurrency/permission/offline/platform — pure methodology-tooling slice with no runtime user surface.
- [x] Over-engineering — no findings. Slice scope well-bounded (7 tests + 1 ADR + 1 changelog entry + atomic version bump); 4 rejected options in ADR-013 explicitly reject over-engineering paths.
- [x] Under-engineering — no findings on AC coverage. Each AC #1-#5 has at least one design element and one TF-1 row post-consolidation.
- [x] Contract gaps — no findings. No API endpoints, events, or external integrations.
- [x] Security — no findings. Internal methodology-tooling refactor; no auth surface, no user input, no PII.
- [x] Drift from vault — no findings. ADR-013 references ADRs 006/007/010/011/012 — all extant. Rule-ID PMI-1 v1.1 follows BC-1 v1.x evolution precedent verifiable at methodology-changelog.md. No contradiction with existing ADRs; no reference to non-existent code paths.
- [x] Web-known issues — skipped — WebSearch unavailable for internal-methodology refactor. Python `ast`, `yaml.safe_load`, `pytest.monkeypatch.setattr`, `pytest.raises` are stable / training-data covered; no platform-version restrictions plausibly material at 2026-05-13.
- [x] Cross-cutting conformance — TF-1 row coverage (m3 ACCEPTED-FIXED); PENDING→WRITTEN-FAILING genuineness signals row 1 (post-fix: design.md's signal wording acknowledges pytest collection-error vs NameError nuance is verify-at-build); algorithm-path-conformance N/A (the `_invariant` function REPLACES not extends the legacy gate); tooling-doc-vs-implementation parity cross-table-consistency checks PASS; recursive-self-application discipline (RSAD-1) design.md stress-test documented; runtime-environment / language-version conformance — Python 3.13 stdlib only, no docstring/escape-sequence semantics exercised; design-doc-vs-canonical-inventory parity OOS section explicitly defers `~/.claude/ai-sdlc-VERSION == VERSION == plugin.yaml.version` 3-way invariant to INST-1 territory — no drift.

## Triage

**Triaged by**: user (Builder draft dispositions ratified per /critique skill Step 4.5; first-Critic 5 findings + meta-Critic M-add-1 reconciled per /critique-review DR-1 EXTEND verdict; user operating under "make the reasonable call and continue" mode per session-start system reminder, with explicit override pathway preserved for any disposition the user disagrees with on next turn)
**Date**: 2026-05-13
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | design.md `## Phase plan` section added (Phase 0..4 enumerated, Phase 2 as single atomic-commit step); mission-brief.md must-not-defer extended with META-1 atomicity bullet referencing design.md Phase plan |
| M2 | Major | ACCEPTED-FIXED | design.md `## Regression test fixture spec` subsection added pinning monkeypatch target string `"tests.methodology.test_methodology_changelog.REPO_ROOT"` + tempdir fixture content + per-substring assertion order; full canonical function body inline |
| m1 | Minor | ACCEPTED-FIXED | ADR-013 body Reversibility section: `Class: cheap.` clarified to preserve ADR 003/004/006-012 single-token frontmatter convention; magnitude-of-revert justification follows in body prose. design.md ADR ref updated to match |
| m2 | Minor | ACCEPTED-FIXED | combined with M1 fix at design.md `## Phase plan` (8 Phases enumerated with content per phase) |
| m3 | Minor | ACCEPTED-FIXED | mission-brief.md TF-1 table replaced with 7-row consolidated plan matching design.md naming; function names canonicalized; footnotes updated; out-of-scope reaffirmation added |
| M-add-1 | Major | ACCEPTED-FIXED | meta-Critic catch via /critique-review DR-1 dual-review (EXTEND verdict): `import pytest` + `import ast` not currently in `tests/methodology/test_methodology_changelog.py` imports block; canonical regression-test body uses `pytest.raises` and 2 AST meta-tests need `ast.parse`/`ast.walk`; without explicit imports added, Phase 1d smoke gate would fail rows 2+3+4 with NameError and design.md diagnostic guidance would misdiagnose as EPGD-1 violation (10-15 min misdiagnosis cost). Fix applied at design.md `## Phase plan / Phase 1a' — Imports preamble Edit (post-/critique-review M-add-1 ACCEPTED-FIXED)` with full canonical Edit `old_string`/`new_string` for the imports block (PEP-8 conforming stdlib → third-party → first-party grouping). |
