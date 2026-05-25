# Design: Slice 023 audit-tools-default-utf8-stdout

**Date**: 2026-05-15
**Mode**: Standard

## What's new

- NEW `tools/_stdout.py` — shared helper module exposing `reconfigure_stdout_utf8()`. Idempotent, duck-typed (no-op when streams lack `reconfigure`), `errors="replace"` not `errors="strict"`, applied to BOTH `sys.stdout` and `sys.stderr`. ~25 LOC, no third-party deps.
- NEW `tools/utf8_stdout_audit.py` — structural audit (UTF8-STDOUT-1) that AST-parses every `tools/*.py` module, finds those exposing a `main()` function, and verifies the FIRST executable statement of `main()` is the canonical `_stdout.reconfigure_stdout_utf8()` call. CLI shape mirrors `tools/critique_agent_drift_audit.py` (positional `--root`, `--json`, exit 0/1/2). ~120 LOC.
- MODIFIED **16 existing audit tools** — each `main()` gets a single line inserted as the first statement of the function body (before `argparse.ArgumentParser(...)`):

  ```python
  def main(argv: list[str] | None = None) -> int:
      _stdout.reconfigure_stdout_utf8()
      parser = argparse.ArgumentParser(...)
  ```

  Tools touched (per `Grep "^def main\(|if __name__" tools/`):
  1. `tools/install_audit.py`
  2. `tools/build_checks_audit.py`
  3. `tools/critique_agent_drift_audit.py`
  4. `tools/risk_register_audit.py`
  5. `tools/validate_slice_layers.py`
  6. `tools/plugin_manifest_audit.py`
  7. `tools/supersede_audit.py`
  8. `tools/cross_spec_parity_audit.py`
  9. `tools/critique_review_audit.py`
  10. `tools/exploratory_charter_audit.py`
  11. `tools/walking_skeleton_audit.py`
  12. `tools/test_first_audit.py`
  13. `tools/triage_audit.py`
  14. `tools/wiring_matrix_audit.py`
  15. `tools/mock_budget_lint.py`
  16. `tools/branch_workflow_audit.py`

  Each tool also gains `from tools import _stdout` (canonical form pinned per M4 ACCEPTED-FIXED — no existing intra-`tools/` import precedent exists; this form mirrors the rest-of-codebase pattern of fully-qualified `tools.X` module references in `_CANONICAL_TOOLS`). All 17 tools (16 existing + 1 new audit) use the identical import line; pinned by `tests/methodology/test_utf8_stdout_audit.py::test_every_tool_uses_canonical_from_tools_import_stdout`.

- NEW `architecture/decisions/ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md` (reversibility: cheap; supersedes: null).
- NEW `methodology-changelog.md` v0.37.0 entry naming UTF8-STDOUT-1, its 3 surfaces (helper / structural audit / one-line `main()` invocation pattern), atomic version bump 0.36.0 → 0.37.0.
- NEW `architecture/shippability.md` row 23 enumerating UTF8-STDOUT-1 critical-path tests.
- NEW test files (split per M5 ACCEPTED-FIXED to keep unit-test runtime separate from subprocess regression runtime):
  - `tests/methodology/test_stdout_helper.py` — 4 unit tests on the helper itself (AC #1)
  - `tests/methodology/test_utf8_stdout_audit.py` — 6 audit unit tests (AC #2 + #3): AST-detection clean / violation / self-exemption / JSON shape / exit codes / canonical-import-form pin
  - `tests/methodology/test_utf8_stdout_regression.py` — NEW separate file (M5) — 1 behavioural subprocess regression test (AC #4) invoking every audit tool via subprocess under `PYTHONIOENCODING=cp1252` with U+2192 fixture content. Separated from `test_utf8_stdout_audit.py` because the 17×subprocess invocations take ~5–17s — keeping the audit unit tests fast.
- EXTENDS test files:
  - `tests/methodology/test_methodology_changelog.py` — 2 NEW entry-pin tests for v0.37.0 UTF8-STDOUT-1 entry (AC #5 — names all 3 surfaces + pins canonical invocation pattern) + 1 NEW ADR-pin test `test_adr_021_present_and_reversibility_cheap` (per ADR-pin convention — verified at slice-022 shape: `test_adr_020_exists_and_supersedes_adr_019` + `test_adr_020_documents_three_mode_taxonomy` both in `test_methodology_changelog.py`). Uses the existing `_extract_version_body(content, version)` helper introduced at slice-020 (rule-of-three originally confirmed at N=3 entries v0.33.0/v0.34.0/v0.35.0; now N=5 stable with v0.36.0 + v0.37.0 added).
  - `tests/methodology/test_install_audit.py` — 1 NEW test ensuring `_CANONICAL_TOOLS` enumerates `tools.utf8_stdout_audit`.
  - `tests/methodology/test_plugin_manifest_audit.py` — 2 NEW tests: (a) ensuring `plugin.yaml` `tools:` list enumerates `utf8_stdout_audit` (path-shape per slice-021 precedent); (b) ensuring `_list_actual_tools` filters leading-underscore helpers (one-line PMI-1 audit modification per B2 ACCEPTED-PENDING — see Components touched § `tools/plugin_manifest_audit.py` (modified)).
  - `tests/methodology/test_critique_agent_drift.py` — 1 NEW vacuously-clean assertion at slice-023 ship hash (CAD-1 invariant — `agents/critique.md` untouched).
- DROPPED per B4 ACCEPTED-FIXED: NO separate `test_row_023_utf8_stdout.py` file (shippability rows do not have per-row test files; the Command cell in shippability.md row 23 IS the test, invoked by `/validate-slice` at pre-finish). ADR-pin test convention is `tests/methodology/test_methodology_changelog.py::test_adr_NNN_*` (per B3 ACCEPTED-FIXED — there is no `tests/decisions/` directory in this repo; verified at slice-022 ADR-020 pin location).
- PLUGIN MANIFEST update: `plugin.yaml.version` 0.36.0 → 0.37.0; `tools:` list gains `- path: tools/utf8_stdout_audit.py / rule: UTF8-STDOUT-1` (canonical entry shape per M3 ACCEPTED-FIXED — NOT `- id:`; verified across plugin.yaml `tools:` section L88+). `tools/_stdout.py` is a HELPER (no `main()`) — EXCLUDED from `plugin.yaml` `tools:` list AND from `_CANONICAL_TOOLS`. Per B2 ACCEPTED-PENDING, `tools/plugin_manifest_audit.py:_list_actual_tools` is extended to filter leading-underscore helper modules (one-line change: `if p.name != "__init__.py" and not p.name.startswith("_")`), preventing the `orphan-tool` violation that would otherwise fire on `_stdout.py`. Sibling unit test added to `test_plugin_manifest_audit.py` per design.md "EXTENDS test files" above.
- VERSION bumps: in-repo `VERSION` 0.36.0 → 0.37.0; forward-sync to `~/.claude/ai-sdlc-VERSION`.
- FORWARD-SYNC: methodology-changelog.md `methodology-changelog.md` → `~/.claude/methodology-changelog.md` per slice-022 precedent.

## What's reused

- [[architecture/decisions/ADR-020-pr-aware-commit-slice-modes]] — most recent ADR; used as structural shape template for ADR-021.
- [[methodology-changelog.md]] — v0.36.0 entry (PR-aware /commit-slice) is the immediate predecessor; v0.37.0 entry follows that shape.
- [[architecture/shippability.md]] — row 22 (PR-aware /commit-slice) is the immediate predecessor; row 23 follows that single-line-per-row format.
- [[tests/methodology/conftest.py]] — `repo_root` fixture + `read_file()` helper reused by new prose-pin + entry-pin tests.
- `tools/critique_agent_drift_audit.py` — pattern reference for the new `tools/utf8_stdout_audit.py` (CLI shape: positional, `--json`, `--root`, exit codes 0/1/2, structured findings).
- `tools/branch_workflow_audit.py` — second pattern reference (slice-021; same CLI shape).
- `tools/plugin_manifest_audit.py` — reused at pre-finish to verify the new audit is enumerated.
- `tools/install_audit.py` — reused at pre-finish to verify INST-1 canonical list matches `plugin.yaml`.
- `tests/methodology/test_methodology_changelog.py` `_extract_version_body(content, version)` helper (added slice-020) — reused by new v0.37.0 entry-pin tests (rule-of-three N=3+ stable).
- [[agents/critique.md]] — NOT TOUCHED (CAD-1 byte-equality preserved at slice-017 ship hash `f34c967eaaa34413`); UTF8-STDOUT-1 is a runtime-discipline gate, not a /critique-time prose discipline (the -D suffix is reserved for /critique-time disciplines per slice-019/020 convention).
- [[skills/build-slice/SKILL.md]] — Step 6 audit list is prose-enumerated (verified at L120-129): currently 5 audits — LINT-MOCK-1, WIRE-1, BC-1, TF-1, BRANCH-1 (per M2 ACCEPTED-FIXED — NOT 7; WS-1 / ETC-1 / RR-1 / PMI-1 run at /validate-slice, not /build-slice Step 6). UTF8-STDOUT-1 is added as the 6th bullet in this list + a new `#### UTF-8 stdout audit (UTF8-STDOUT-1)` sub-section after the existing `#### Branch workflow audit (BRANCH-1)` block. Mini-CAD-1 drift test fires (bytes change) → bump expected sha256 in `tests/methodology/test_build_slice_skill_drift.py`.
- [[skills/reflect/SKILL.md]], [[skills/validate-slice/SKILL.md]], [[skills/commit-slice/SKILL.md]] — NOT TOUCHED. UTF8-STDOUT-1 is a structural rule on `tools/*.py`; no skill-prose discipline change needed.

## Components touched

### `tools/_stdout.py` (created)

- **Responsibility**: provides `reconfigure_stdout_utf8()` — the canonical one-line stdout/stderr UTF-8 reconfigure call used by every audit tool's `main()`.
- **Lives at**: `tools/_stdout.py` (created by this slice).
- **Key interactions**: imported by all 16 audit tools' `main()`; unit-tested by `tests/methodology/test_stdout_helper.py`; verified-as-called by `tools/utf8_stdout_audit.py` (which AST-parses every audit tool).
- **Public surface** (exhaustive):
  ```python
  def reconfigure_stdout_utf8() -> None:
      """Reconfigure sys.stdout and sys.stderr to UTF-8 with errors='replace'.

      No-op when streams lack `reconfigure` (test capture, StringIO).
      Idempotent: stdlib `TextIOWrapper.reconfigure` is safe to call with the
      same kwargs repeatedly. Per M6 ACCEPTED-FIXED, we deliberately do NOT
      short-circuit on `encoding == "utf-8"` because a prior call may have
      left `errors="strict"`; unconditionally reconfiguring with both
      `encoding="utf-8"` AND `errors="replace"` guarantees the post-call
      state matches the slice's required contract regardless of prior state.
      """
      for stream in (sys.stdout, sys.stderr):
          reconfigure = getattr(stream, "reconfigure", None)
          if reconfigure is None:
              continue
          reconfigure(encoding="utf-8", errors="replace")
  ```
- **Why a function not module-level side-effect**: importing `_stdout` must NOT silently reconfigure streams (would surprise tests that intentionally write cp1252 fixtures). The reconfigure is opt-in per `main()`.
- **Why `errors="replace"`**: a non-UTF-8 byte sneaking into audit output should degrade to `?` / `�` rather than crash. The whole slice's value-prop is "no more cp1252 crashes"; `errors="strict"` would just replace cp1252-crash with utf-8-crash.

### `tools/utf8_stdout_audit.py` (created)

- **Responsibility**: structural rule UTF8-STDOUT-1 — every `tools/*.py` module exposing a `main()` function MUST call `_stdout.reconfigure_stdout_utf8()` as the first executable statement of `main()`.
- **Lives at**: `tools/utf8_stdout_audit.py` (created by this slice).
- **Key interactions**: invoked at `/build-slice` Step 6 pre-finish gate via `$PY -m tools.utf8_stdout_audit`; unit-tested + behavioural-tested by `tests/methodology/test_utf8_stdout_audit.py`; enumerated in `plugin.yaml.tools` (PMI-1 gate); listed in `tools/install_audit.py` canonical list (INST-1 gate).
- **Detection mechanism** (AST-based, not regex):
  - For each `tools/*.py` (excluding `_stdout.py`, `__init__.py`, and files matching `tools/utf8_stdout_audit.py` itself's own audit self-exemption — see note below), parse with `ast.parse(source, filename=path)`.
  - Find top-level `FunctionDef` named `main` (or `AsyncFunctionDef` — not expected, but handle gracefully).
  - Identify the first executable statement in `main.body` skipping docstring (`Expr(Constant(str))`).
  - The first executable statement MUST be `Expr(Call(...))` where the callee is `Attribute(Name('_stdout'), 'reconfigure_stdout_utf8')` OR `Name('reconfigure_stdout_utf8')` (allowing both `from tools import _stdout; _stdout.reconfigure_stdout_utf8()` and `from tools._stdout import reconfigure_stdout_utf8; reconfigure_stdout_utf8()` import shapes).
  - Else → violation: `<file>:main(): first executable statement is not `_stdout.reconfigure_stdout_utf8()` (got: <repr>)`.
- **CLI shape** (mirrors `branch_workflow_audit.py`):
  - `python -m tools.utf8_stdout_audit` — scans `tools/` from repo root (auto-detected via `Path(__file__).parent.parent`).
  - `python -m tools.utf8_stdout_audit --json` — JSON output for machine-readable parse.
  - `python -m tools.utf8_stdout_audit --root <repo-root>` — explicit repo root override.
  - Exit codes: 0 clean (every audit tool conforms); 1 violation (≥1 tool non-conforming); 2 usage error (root path missing, no `tools/*.py` found, ast.parse failure).
- **Self-exemption**: `utf8_stdout_audit.py` itself MUST also call `_stdout.reconfigure_stdout_utf8()` in its own `main()` — it is not exempt from its own rule (recursive-self-application N=1 canonical reference instance at codification time per RSAD-1 + LAYER-EVID-1 / TPHD-1 / BRANCH-1 precedent). The exclusion list (`_stdout.py`, `__init__.py`) excludes ONLY helper modules with no `main()`, not the audit itself.
- **Output contract** (JSON when `--json`) — per B5 ACCEPTED-FIXED, canonical numbers are: post-slice `tools/` directory contains 19 .py files (`__init__.py` + `_stdout.py` helper + 17 audit tools with `main()`). Exclusion list: `__init__.py` + `_stdout.py` (leading-underscore helper, no `main()`). After exclusion: **17 tools scanned, all 17 with `main()`, all 17 clean on conforming codebase**:
  ```json
  {
    "tools_scanned": 17,
    "tools_with_main": 17,
    "tools_clean": 17,
    "violations": [],
    "status": "clean"
  }
  ```
  Or on violation (e.g., one tool's `main()` lacks the reconfigure call):
  ```json
  {
    "tools_scanned": 17,
    "tools_with_main": 17,
    "tools_clean": 16,
    "violations": [
      {
        "file": "tools/test_first_audit.py",
        "function": "main",
        "line": 400,
        "message": "first executable statement is not _stdout.reconfigure_stdout_utf8() (got: argparse.ArgumentParser(...))"
      }
    ],
    "status": "violation"
  }
  ```
  **Output-contract invariant (regression-guard, pinned by `tests/methodology/test_utf8_stdout_audit.py::test_output_contract_invariant`)**:
  - `tools_scanned == tools_with_main` whenever every scanned-but-non-excluded file has a `main()` (the case post-slice-023 by construction).
  - `tools_clean == tools_with_main - len(violations)`.
  - `status == "clean"` iff `len(violations) == 0`.
  This locks the count relationship across future changes.

### Existing 16 audit tools (modified, one-line addition each)

- **Responsibility**: unchanged — each tool's audit logic is untouched.
- **Lives at**: paths enumerated under "What's new" → "MODIFIED 16 existing audit tools".
- **What changes** (per tool):
  - Add `from tools import _stdout` at module top (after stdlib imports per existing import-grouping convention). Canonical pinned form per M4 ACCEPTED-FIXED — NOT `from . import _stdout`.
  - Insert `_stdout.reconfigure_stdout_utf8()` as the first statement of `main()` body (before any other statement; after docstring if `main()` has one).
- **No semantic change** — the reconfigure is a runtime stdout-encoding-only mutation; audit output (JSON / human / exit codes) is unchanged at the bytes-after-encoding layer (was cp1252-encoded ASCII / em-dash, is now UTF-8-encoded same chars + arrows + anything else).

## Contracts added or changed

### `python -m tools.utf8_stdout_audit` CLI (new)

- **Endpoint**: command-line entry point at `tools/utf8_stdout_audit.py:__main__`.
- **Auth model**: none (local development tool; no network calls; reads files via Pathlib + `ast` stdlib).
- **Input contract** (positional + flags): NO positional argument (auto-discovers `tools/` from repo root). `--root <path>` overrides; `--json` flag; `--help` flag.
- **Output contract** (JSON when `--json`): see "Output contract" under `utf8_stdout_audit.py` component above.
- **Error cases**:
  - `tools/` directory not found relative to `--root` → exit 2 + stderr "tools/ directory not found at <path>"
  - `ast.parse(file)` raises `SyntaxError` → exit 2 + stderr with file + line + cause
  - Permission denied on any `tools/*.py` → exit 2 + stderr with explicit cause

### NEW `tools._stdout.reconfigure_stdout_utf8()` Python API (new)

- **Responsibility**: documented under "Components touched → `tools/_stdout.py`".
- **Defined in code at**: `tools/_stdout.py` (created).
- **Contract**: see public surface in the component section. Stable across slice-023 → forward.

### Build-slice Step 6 pre-finish gate (extended)

- **Responsibility**: enumerates the audit list run at `/build-slice` Step 6 to refuse non-PASSING slices.
- **Defined in code at**: `skills/build-slice/SKILL.md` Step 6 audit list (verified prose-enumerated at L120-129 per M2 ACCEPTED-FIXED).
- **Contract surface**: prose-heuristic. Per M2 the audit list at L125-129 currently contains 5 audits — LINT-MOCK-1, WIRE-1, BC-1, TF-1, BRANCH-1. UTF8-STDOUT-1 is added as the 6th bullet: `- [ ] **UTF8-STDOUT-1 audit passes** — see "UTF-8 stdout audit" below`. A new `#### UTF-8 stdout audit (UTF8-STDOUT-1)` sub-section is added after the existing `#### Branch workflow audit (BRANCH-1)` block documenting the invocation `$PY -m tools.utf8_stdout_audit`.
- **Mini-CAD-1 impact**: bytes change → bump expected sha256 in `tests/methodology/test_build_slice_skill_drift.py` to the post-modification hash.

## Data model deltas

None. Pure tooling + helper-module + audit slice; no schemas, no entities, no migrations, no API surface changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_stdout.py` | `tools/install_audit.py:main`, `tools/build_checks_audit.py:main`, `tools/critique_agent_drift_audit.py:main`, `tools/risk_register_audit.py:main`, `tools/validate_slice_layers.py:main`, `tools/plugin_manifest_audit.py:main`, `tools/supersede_audit.py:main`, `tools/cross_spec_parity_audit.py:main`, `tools/critique_review_audit.py:main`, `tools/exploratory_charter_audit.py:main`, `tools/walking_skeleton_audit.py:main`, `tools/test_first_audit.py:main`, `tools/triage_audit.py:main`, `tools/wiring_matrix_audit.py:main`, `tools/mock_budget_lint.py:main`, `tools/branch_workflow_audit.py:main`, `tools/utf8_stdout_audit.py:main` | `tests/methodology/test_stdout_helper.py::test_*` (unit) + `tests/methodology/test_utf8_stdout_regression.py::test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` (behavioural integration covering all 17 consumers; split per M5 + M-add-4 ACCEPTED-FIXED) | — |
| `tools/utf8_stdout_audit.py` | `skills/build-slice/SKILL.md` Step 6 pre-finish gate | `tests/methodology/test_utf8_stdout_audit.py::test_*` | — |

The new + extended test files (test_stdout_helper.py, test_utf8_stdout_audit.py, test_utf8_stdout_regression.py, and the extends to test_methodology_changelog.py / test_install_audit.py / test_plugin_manifest_audit.py / test_critique_agent_drift.py) are CONSUMERS, not new modules requiring further consumers — they don't appear in the matrix per slice-018+ precedent. Per B4 + B3 ACCEPTED-FIXED: no separate `test_row_023_utf8_stdout.py` file; no `tests/decisions/` directory; ADR-pin lives as a NEW test function in the existing `test_methodology_changelog.py`.

## Decisions made (ADRs)

- [[ADR-021]] — UTF8-STDOUT-1: every `tools/*.py` exposing a `main()` MUST call `tools._stdout.reconfigure_stdout_utf8()` as the first executable statement of `main()`; enforced by structural audit `tools/utf8_stdout_audit.py` — reversibility: **cheap**

## Authorization model for this slice

None. Pure local-only tooling change. No user-facing surface; no API contract; no authn/authz boundary touched. Tools only read files via Pathlib + run subprocesses via `subprocess.run(..., check=False)` already (no new subprocess surfaces added).

The one local-state mutation is `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` — this affects only the process invoking the audit, not files on disk. No defense-in-depth needed (compare slice-021 which had 2 local-state-loss git paths requiring guardrails — none apply here).

## Error model for this slice

Three failure surfaces, each with explicit handling:

1. **`tools.utf8_stdout_audit` runtime errors**:
   - `tools/` directory absent at resolved root → exit 2 + stderr "tools/ directory not found at <path>". User remediation: invoke from repo root or pass `--root`.
   - `ast.parse(file)` raises SyntaxError on any `tools/*.py` → exit 2 + stderr with file + line + cause. User remediation: fix the syntax error (this is unrelated to UTF8-STDOUT-1 itself; the audit refuses to operate on a syntactically broken codebase).
   - `ast.parse` succeeds but `tools/utf8_stdout_audit.py` itself's `main()` is the one missing the reconfigure call (recursive self-application failure at codification time) → exit 1 + violation listing the audit itself. **This is intentional**: the audit refuses to declare clean when it itself is non-conforming, per LAYER-EVID-1 / BRANCH-1 / BFRD-1 canonical-reference-instance-at-codification-time precedent.

2. **`tools._stdout.reconfigure_stdout_utf8()` runtime errors**:
   - `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` raises (e.g., a custom stream that has `reconfigure` attribute but it's not callable or rejects keyword args) → the call propagates the exception. **NOT caught**, because silent-swallow would defeat the slice's whole point. Test capture streams under pytest typically lack `reconfigure` attribute entirely (the `getattr` returns `None`, function continues — handled). If a real-world stream is found that has the attribute but rejects kwargs, the failure is loud and fixable on the spot.
   - Stream already at UTF-8 encoding → no-op (idempotency path).

3. **Behavioural regression test failure surface** (per M1 ACCEPTED-FIXED — per-tool argv strategy + parent-side subprocess decoding pinned):
   - Lives at `tests/methodology/test_utf8_stdout_regression.py::test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` (split from audit unit tests per M5 ACCEPTED-FIXED for runtime isolation).
   - **Per-tool argv strategy** (per M1 + M-add-2 ACCEPTED-FIXED — verified by reading each tool's argparse block; previous grouping mis-classified 3 tools):
     - **Tools requiring a positional slice-folder** (`branch_workflow_audit`, `test_first_audit`, `wiring_matrix_audit`, `walking_skeleton_audit`, `exploratory_charter_audit`, `build_checks_audit`, `triage_audit`, `cross_spec_parity_audit`, `supersede_audit`): pass a synthetic fixture slice directory at `tests/methodology/fixtures/utf8_stdout/slice-fixture/` containing `mission-brief.md` + `design.md` whose content includes U+2192 (`PENDING → WRITTEN-FAILING → PASSING`). The fixture is constructed in the test's `tmp_path` setup via `Path.write_text(..., encoding="utf-8")`. Fixture must be syntactically valid enough for each audit's parser to reach the U+2192-emitting code path (e.g., TF-1 audit needs a parseable TF-1 plan table; WIRE-1 audit needs a parseable wiring matrix in design.md).
     - **Tools with `--root` only** (`plugin_manifest_audit`, `cross_spec_parity_audit`, `utf8_stdout_audit`): pass `--root <tmp_path>` pointing at a synthetic repo-fixture directory + manifest with U+2192 in surface paths.
     - **`install_audit`**: takes `--claude-dir <path>` (NOT `--root` — verified at `tools/install_audit.py` L344); pass `--claude-dir <tmp_path>` pointing at a synthetic install-target with U+2192 in the renamed surface.
     - **`mock_budget_lint`**: requires positional `files` (nargs="+", verified at `tools/mock_budget_lint.py` L822-825); pass at least one synthetic test file in `tmp_path` containing U+2192 (e.g., a docstring with arrows or a comment).
     - **`validate_slice_layers`**: requires `--slice <path>` (required=True, verified at `tools/validate_slice_layers.py` L507-510); pass `--slice <synthetic-fixture-slice>` with U+2192 in mission-brief.md.
     - **`risk_register_audit`**: takes positional path to risk-register.md file (per `tools.risk_register_audit architecture/risk-register.md` invocation); pass fixture risk-register.md whose body contains a U+2192.
     - **`critique_agent_drift_audit` + `critique_review_audit`**: take `--repo-root <path>` or positional repo root; same `--root` strategy applies.
     - **No tool is invoked bare** post-fix — every audit has a required argument; "no argv" group dissolved.
   - **Parent-side subprocess decoding**: `subprocess.run(...)` MUST pin `text=True, encoding="utf-8", errors="replace"` AND set `env={"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0", ...os.environ}` (`PYTHONUTF8=0` defeats Python 3.7+ UTF-8 mode override; `cp1252` simulates Windows default). Without these, the parent's default decode of child UTF-8 output would crash on Windows (the recurring class slice-022 D-5 captures at `tools/critique_agent_drift_audit.py`'s own test).
   - **Failure assertion**: the test asserts `"UnicodeEncodeError" not in result.stderr` AND `"UnicodeDecodeError" not in result.stderr` — NOT `result.returncode == 0`. Fixture slices may legitimately return exit 1 on non-encoding violations (e.g., synthetic mission-brief has TF-1 rows at PENDING status → TF-1 audit returns 1); the encoding-survival assertion is what matters.
   - Any `UnicodeEncodeError` / `UnicodeDecodeError` traceback in subprocess stderr → test FAIL with the offending tool's name + cp1252 char + line, surfaced via pytest.fail with diagnostic context.

## Self-application of UTF8-STDOUT-1 at this slice

Per RSAD-1 (recursive-self-application discipline, slice-011 / ADR-010): this slice IS the canonical reference instance #1 of UTF8-STDOUT-1. The expectation is that:

1. `tools/utf8_stdout_audit.py` itself conforms to UTF8-STDOUT-1 — its own `main()` calls `_stdout.reconfigure_stdout_utf8()` as the first executable statement.
2. The audit, invoked on the post-slice-023 codebase, returns `tools_scanned: 17, tools_with_main: 17, tools_clean: 17` across all 17 tools with `main()` (16 existing audits modified + 1 new `utf8_stdout_audit.py`). Helper module `_stdout.py` excluded from the scan via leading-underscore filter (per B2 ACCEPTED-PENDING — `_list_actual_tools` in `plugin_manifest_audit.py` extended to match).
3. The N=1 → N≥2 stable transition fires at the NEXT slice that adds a new `tools/*.py` audit tool — that tool's `main()` will conform from the start.

No bootstrap caveat (compare slice-021 BRANCH-1 which had a bootstrap-reference-instance #1 caveat because the skill prose defining branch-create was itself authored in the slice). UTF8-STDOUT-1 is a pure structural rule on Python source; the helper + audit + 16 tool modifications all happen within `/build-slice`'s plan-mode + apply phase; by Step 6 pre-finish, the audit fires against the post-modification codebase. No mid-state-self-conformance gap.

## Cumulative-Critic-influence note

**Pre-/critique prediction (Builder)**: ≤5 first-Critic findings + ≤2 meta-Critic findings; N=8 stable predicted under RSAD-1 baseline. Hypothesis-falsification clause: if Critic-stack finds N>10, the under-engineering vector is the most likely catch.

**Post-/critique actual**: **17 first-Critic findings** (5 Blockers + 8 Majors + 4 Minors; sums to 17 per M-add-5 ACCEPTED-FIXED — earlier framing's "13" implicitly excluded Minors but enumerated all three) — **prediction falsified at first-Critic alone (predicted ≤5, actual 17 = 3.4× over)**. Hypothesis-falsification clause partly validated: catches do include under-engineering vector (B2 PMI-1 hand-wave, B5 count drift, M1 subprocess strategy gap) but the DOMINANT class is **Dim 9 sub-clause 2: design.md mechanical tables vs canonical inventory drift** — 4 of 5 Blockers (B1 path / B3 tests/decisions / B4 test_row file / M2 build-slice Step 6 list) are positive-inclusion drift where the design.md claimed paths / conventions / counts that don't exist in the actual codebase. Per M8 catch: the prediction's prose-pin (the SMALL slice + mechanical extension framing) under-counted the artifact-vs-codebase-convention class.

**Post-/critique-review actual**: **6 missed by first-Critic** (M-add-1 mission-brief pre-finish row count drift + M-add-2 per-tool argv mis-grouping × 3 tools + M-add-3 ADR-021 helper-body short-circuit drift + M-add-4 M5 split-test-file 3-site sweep incomplete + M-add-5 design.md "13 findings" arithmetic + M-add-6 SUP-1 informational). All 6 ACCEPTED-FIXED inline this round. **Total Critic-stack findings: 23** (17 first-Critic + 6 meta-Critic) — well above slice-022's 18 and approaching slice-021's HWM of 28.

**Catch-class breakdown**:
- **Dim 1 (unfounded assumption) / Dim 9 sub-clause 2 (design.md vs canonical inventory)**: B1 / B3 / B4 / M2 / M4 / M7 (6 findings) — all from claims about file paths / test conventions / audit list contents that the design.md author asserted without grepping the actual codebase first. **Highest-density class** in this critique.
- **Dim 4 (under-engineering)**: B2 / B5 / M1 (3 findings) — design hand-waved fixes to /build-slice Step 1 rather than committing to them at design time.
- **Dim 5 (contract gaps)**: M3 / M5 / M6 (3 findings) — plugin.yaml shape / test-file conflation / helper idempotency edge.
- **Dim 9 sub-clauses (recursive-self-application + Wiegers regression-guard coverage-symmetry + Cross-mission-brief-vs-design-consistency)**: M8 (informational) + cross-cutting comments on B5 + M2 — codification-slice-commits-instances-of-its-own-discipline pattern reaffirmed at N=23 cumulative HWM equivalent for this slice's draft.
- **Minors**: m1 (placeholder dates) / m2 (N-conflation) / m3 (rule-of-three math) / m4 (PowerShell hygiene) — cheap fixes.

**Recursive-self-application impact at slice-023**: codification slice committed instances of its own discipline on its own draft at **17 first-Critic + 6 meta-Critic = 23 cumulative** — within the slice-020 / slice-021 / slice-022 codification-slice range (N=17 / N=28 / N=18) and approaching slice-021's HWM. The actual count refutes the SMALL-slice-low-density framing in pre-/critique prediction; SMALL is true at line-count level (helper ~25 LOC + audit ~120 LOC + 16 mechanical one-liners) but FALSE at vault-claim-density level — the design.md authored 4 Blockers worth of canonical-inventory claims without grepping the corpus, AND the Builder's ACCEPTED-FIXED sweeps were incomplete at 4 sibling-site classes that meta-Critic surfaced (M5 split-test-file, M6 helper-body drift, M-add-1 row-count, M-add-2 argv-grouping). Implication for /critic-calibrate slice-024+: the Dim 9 sub-clause 2 class is empirically the dominant recurrence class for ALL codification slices, including those tagged SMALL — AND **fix-block-completeness on first-Critic disposition sweeps** (slice-020 M-add-1 watch-list) is the dominant meta-Critic catch-class.

**Wiegers regression-guard coverage-symmetry ratchet at slice-023**: N=12 cumulative (slice-022) → N=13+ cumulative (B5 count drift across mission-brief AC #2 cell + design.md L120/121/130/131 + design.md L225 + design.md L344 + audit unit-test assertions — 6 sibling sites where the same canonical count must agree). Cross-mission-brief-vs-design-consistency-checking N=1 (slice-022) → N=3 cumulative at slice-023 (B5 count drift + B3 ADR-pin path drift across mission-brief + design + ADR-021 + M5 test-file path drift in mission-brief AC #4 vs design.md L43) — **promotion to Dim 9 sub-clause at /critic-calibrate slice-024 ELIGIBLE at N=3 threshold**.

## Limitations / explicit non-coverage

1. **`sys.stdout` / `sys.stderr` only — NOT `sys.stdin`**: the slice's scope is OUTPUT-side encoding; input-side is unaffected. If a future audit reads non-ASCII from stdin (`sys.stdin.read()` with cp1252 default), that's a separate class and a separate slice.
2. **`tools/*.py` only — NOT `tests/**/*.py`**: tests are typically invoked via pytest, which has its own capture mechanism; pytest's `--capture` modes handle encoding internally. If a test prints non-ASCII to console during the run, pytest's reporter handles encoding. Tests are out of scope.
3. **In-house `tools/` only — NOT `graphify`**: `graphify` is shipped from `~/.claude/packages/graphify` editable; if its console output hits cp1252 in future, that's an upstream-package fix, not a `tools/`-package fix.
4. **`sys.stdout` parent-process only — NOT `subprocess.run(..., stdout=PIPE)` child capture**: subprocess-captured output is encoded via the child's `sys.stdout` encoding. The child IS a `tools/*.py` invoked via `$PY -m tools.X` from `/build-slice` skill, so the child's `_stdout.reconfigure_stdout_utf8()` fires inside the child's `main()` and writes UTF-8 to its captured stdout — the parent's `subprocess.run(..., text=True, encoding="utf-8")` then decodes it correctly. **But**: if `subprocess.run` is called WITHOUT explicit `encoding="utf-8"` (relying on `locale.getpreferredencoding()` which is cp1252 on Windows), the decode FAILS at the parent. UTF8-STDOUT-1 does NOT enforce the parent's `subprocess.run(..., encoding="utf-8")` discipline. That's a separate audit class; defer.
5. **`logging` module output**: tools that use `logging.getLogger(...).info("→")` route through `logging.StreamHandler(sys.stderr)` by default; reconfiguring `sys.stderr` to UTF-8 IS sufficient to fix that class. But tools that attach a custom `FileHandler` or `RotatingFileHandler` may write to a file whose encoding is platform-default. **OUT OF SCOPE**: this slice's helper does not touch logging handlers. If a future tool emits non-ASCII to a log file via FileHandler with default encoding, the fix is `FileHandler(path, encoding="utf-8")` at the handler call site — not the `_stdout` helper.
6. **`print()` to redirected streams via shell `tools/X.py > file.txt`**: when a user redirects via shell, `sys.stdout` is no longer a TTY — it's a `io.TextIOWrapper(io.BufferedWriter(io.FileIO(...)))`. `reconfigure(encoding="utf-8")` IS supported on this stream type in Python 3.7+. Works.
7. **Pre-Python-3.7 compatibility**: `sys.stdout.reconfigure()` was added in Python 3.7. The shared interpreter is 3.13 per project CLAUDE.md global. No fallback needed.
8. **CRLF / LF line-ending drift on skill files**: separate class (slice-022 D-4); out of scope.
9. **Encoding of audit-tool fixture FILES**: file-write side already handled by slice-021 D-3 convention (`encoding="utf-8"` on `write_text`). This slice is exclusively the stdout/stderr side of the same parent class.
10. **`os.write(1, b"\xe2\x86\x92")` direct byte-mode output**: bypasses `sys.stdout`'s encoding entirely; this slice has no effect on it. No tool currently uses `os.write` directly — verified via `Grep "os\.write\(1" tools/` (returns no matches at /design-slice time per `/build-slice` Step 1 confirmation).

## Insertion points (concrete file edits)

For `/build-slice` Step 1 plan-mode entry, the canonical phrases + line ranges to pin:

1. **`tools/_stdout.py` (NEW file)** — full body as shown under "Components touched". Canonical phrases pinned by prose-pin tests on the file itself:
   - Module docstring: `"UTF8-STDOUT-1 helper"` AND `"errors=\"replace\""` AND `"idempotent"`
   - Function name: `reconfigure_stdout_utf8`
   - Function body: contains `sys.stdout`, `sys.stderr`, `getattr(stream, "reconfigure", None)`, `encoding="utf-8"`, `errors="replace"`

2. **`tools/utf8_stdout_audit.py` (NEW file)** — full body per detection mechanism in "Components touched". Canonical phrases pinned by prose-pin tests:
   - Module docstring: `"UTF8-STDOUT-1"` AND `"first executable statement"` AND `"reconfigure_stdout_utf8"`
   - Function `main` exists and conforms to UTF8-STDOUT-1 (self-application)
   - CLI flags: `--json`, `--root`, `--help`

3. **Each of 16 audit tools — `tools/<name>.py`** — 2 edits per file:
   - Import addition (after existing stdlib imports): `from tools import _stdout`. Canonical pinned form per M4 ACCEPTED-FIXED — identical across all 17 modules.
   - First-statement insertion in `main()`: `_stdout.reconfigure_stdout_utf8()` immediately after the `def main(...)` signature (and any docstring).

4. **`methodology-changelog.md` v0.37.0 entry** — prepended at file top after existing v0.36.0 entry. Canonical phrases pinned by entry-pin tests:
   - `"v0.37.0"` (version header)
   - `"UTF8-STDOUT-1"` (rule ID; ≥3 occurrences)
   - `"tools/_stdout.py"` (canonical helper path)
   - `"tools/utf8_stdout_audit.py"` (canonical audit path)
   - `"reconfigure_stdout_utf8"` (canonical function name)
   - `"first executable statement"` (canonical invocation-position phrase)
   - References to N=6 cumulative recurrence + slices 007 / 016 / 018 / 020 / 021 / 022 as discovery trail

5. **`architecture/decisions/ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md` (NEW file)** — frontmatter mirrors ADR-020 shape; body sections: Context, Options considered (3 options — module-side-effect / per-tool-inline / shared-helper-fn), Decision (Option 3 shared-helper-fn chosen), Consequences, Reversibility.

6. **`architecture/shippability.md` row 23** — single-line table row appended after current row 22. Format mirrors row 22. Command cell enumerates the canonical invocation targets (per B3 + B4 ACCEPTED-FIXED — no `tests/decisions/` directory, no `test_row_*.py` file; ADR-pin lives in `test_methodology_changelog.py`):

   ```
   $PY -m pytest \
     tests/methodology/test_stdout_helper.py \
     tests/methodology/test_utf8_stdout_audit.py \
     tests/methodology/test_utf8_stdout_regression.py \
     tests/methodology/test_methodology_changelog.py::test_v_0_37_0_utf8_stdout_1_entry_names_all_three_surfaces \
     tests/methodology/test_methodology_changelog.py::test_v_0_37_0_utf8_stdout_1_entry_pins_canonical_invocation_pattern \
     tests/methodology/test_methodology_changelog.py::test_adr_021_present_and_reversibility_cheap \
     tests/methodology/test_install_audit.py::test_install_audit_enumerates_utf8_stdout_audit \
     tests/methodology/test_plugin_manifest_audit.py::test_plugin_yaml_lists_utf8_stdout_audit \
     tests/methodology/test_plugin_manifest_audit.py::test_list_actual_tools_filters_leading_underscore_helpers \
     -v
   ```

   That's **9 invocation targets across 5 test files** (3 whole-file pytest paths + 6 `::test_*` named-function pytest paths). RPCD-1 sub-mode (b) self-application N≥3 stable.

7. **`CLAUDE.md` (root project)** — NOT TOUCHED. UTF8-STDOUT-1 is a tools-internal structural rule; it doesn't change brownfield rules for human contributors (compare BRANCH-1 which IS a human-facing rule and rightly got a Brownfield-rules bullet). If `/critique` argues otherwise, accept the bullet as a Minor.

8. **`plugin.yaml` tools list** — append `- path: tools/utf8_stdout_audit.py / rule: UTF8-STDOUT-1` (canonical entry shape per M3 ACCEPTED-FIXED — NOT `- id:`; verified at plugin.yaml `tools:` section L88+ which uses `path:` + `rule:` exclusively). Version line 0.36.0 → 0.37.0. `tools/_stdout.py` is NOT added to `tools:` list (helper, no `main()`, no rule); the PMI-1 audit `_list_actual_tools` is extended at this slice to filter leading-underscore modules (per B2 ACCEPTED-PENDING — verified at `tools/plugin_manifest_audit.py` L137-140 that current filter is `__init__.py`-only, no precedent for leading-underscore exclusion; this slice adds it).

9. **`VERSION` file** → 0.37.0. `~/.claude/ai-sdlc-VERSION` forward-sync → 0.37.0.

10. **`tools/install_audit.py` canonical list** — add `tools.utf8_stdout_audit` to the `_CANONICAL_TOOLS` tuple (full module path per existing convention in the tuple). `_stdout` excluded because `_CANONICAL_TOOLS` lists invocable audits only; helpers without `main()` are not enumerable.

11. **`skills/build-slice/SKILL.md` Step 6 audit list** — verified prose-enumerated at L120-129 (5 audits: LINT-MOCK-1, WIRE-1, BC-1, TF-1, BRANCH-1; per M2 ACCEPTED-FIXED). Add `- [ ] **UTF8-STDOUT-1 audit passes** — see "UTF-8 stdout audit" below` as the 6th bullet + new `#### UTF-8 stdout audit (UTF8-STDOUT-1)` sub-section after `#### Branch workflow audit (BRANCH-1)`. Bump expected sha256 in `tests/methodology/test_build_slice_skill_drift.py` (mini-CAD-1).

## Files changed (estimated count)

**~26 files total**. Per /critique pass + /critique-review pass these counts will harmonize across mission-brief.md TF-1 row count + design.md Files-changed + ADR-021 / methodology-changelog.md v0.37.0 sites per TPHD-1 sub-mode (a) / SCPD-1 sub-mode (b) / Wiegers-coverage-symmetry discipline. Initial enumeration:

1. `tools/_stdout.py` (NEW)
2. `tools/utf8_stdout_audit.py` (NEW)
3. `tools/install_audit.py` (modified — `_CANONICAL_TOOLS` extend + main() helper call)
4. `tools/build_checks_audit.py` (modified — main() helper call)
5. `tools/critique_agent_drift_audit.py` (modified)
6. `tools/risk_register_audit.py` (modified)
7. `tools/validate_slice_layers.py` (modified)
8. `tools/plugin_manifest_audit.py` (modified)
9. `tools/supersede_audit.py` (modified)
10. `tools/cross_spec_parity_audit.py` (modified)
11. `tools/critique_review_audit.py` (modified)
12. `tools/exploratory_charter_audit.py` (modified)
13. `tools/walking_skeleton_audit.py` (modified)
14. `tools/test_first_audit.py` (modified)
15. `tools/triage_audit.py` (modified)
16. `tools/wiring_matrix_audit.py` (modified)
17. `tools/mock_budget_lint.py` (modified)
18. `tools/branch_workflow_audit.py` (modified)
19. `plugin.yaml` (version 0.36.0 → 0.37.0 + tools list addition)
20. `VERSION` (0.36.0 → 0.37.0)
21. `~/.claude/ai-sdlc-VERSION` (forward-sync)
22. `~/.claude/methodology-changelog.md` (forward-sync)
23. `methodology-changelog.md` (v0.37.0 entry)
24. `architecture/decisions/ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md` (NEW)
25. `architecture/shippability.md` (row 23 append)
26. `tests/methodology/test_stdout_helper.py` (NEW — 4 unit tests per AC #1)
27. `tests/methodology/test_utf8_stdout_audit.py` (NEW — 6 audit unit tests per AC #2 + #3)
28. `tests/methodology/test_utf8_stdout_regression.py` (NEW — 1 behavioural subprocess regression test per AC #4; SPLIT from test_utf8_stdout_audit.py per M5 ACCEPTED-FIXED for runtime isolation)
29. `tests/methodology/test_methodology_changelog.py` (extends — 2 entry-pin tests for v0.37.0 + 1 ADR-pin test `test_adr_021_present_and_reversibility_cheap` per B3 ACCEPTED-FIXED; NO separate `tests/decisions/` file)
30. `tests/methodology/test_install_audit.py` (extends — INST-1 enumeration test)
31. `tests/methodology/test_plugin_manifest_audit.py` (extends — 2 NEW tests: `utf8_stdout_audit` enumeration + `_list_actual_tools` leading-underscore-filter regression per B2 ACCEPTED-PENDING)
32. `tools/plugin_manifest_audit.py` (modified — one-line `_list_actual_tools` extension to filter `p.name.startswith("_")` per B2 ACCEPTED-PENDING; PMI-1 v1.1 retirement-proof invariant preserved — gate body unchanged, only the discovery filter narrows)
33. `tests/methodology/test_critique_agent_drift.py` (extends — vacuously-clean CAD-1 assertion at slice-023 ship hash)
34. `skills/build-slice/SKILL.md` (extends — Step 6 audit list adds 6th bullet UTF8-STDOUT-1 + new sub-section; per M2 ACCEPTED-FIXED)
35. `tests/methodology/test_build_slice_skill_drift.py` (extends — bump expected sha256 of build-slice SKILL.md post-modification; mini-CAD-1)
36. `tests/methodology/fixtures/utf8_stdout/slice-fixture/mission-brief.md` (NEW — synthetic fixture with U+2192 in TF-1 row content for behavioural regression per M1 ACCEPTED-FIXED)

That's **~28 source/methodology files + 7 test files (new + extends) + 1 fixture file = ~36 total touches at slice-023 ship**. Within slice-023's effort budget at SMALL-to-MEDIUM (~30–60 min — 16 mechanical 2-line additions + 3 small new files including helper / audit / regression fixture + standard methodology surfaces).

**Recursive-self-application impact (post-/critique)**: N=1 canonical reference instance at codification time (the audit firing on its own conformant `main()`) — preserved despite 13 first-Critic findings on the design draft itself (the SLICE'S DRAFT committed Dim 9 sub-clause 2 instances on its own design.md / mission-brief.md / ADR-021 — see Cumulative-Critic-influence note for the catch-class breakdown). The audit-tool's own conformance is decoupled from the design-draft conformance. **Wiegers regression-guard coverage-symmetry watch-list**: N=12 (slice-022) → **N=13+ cumulative** at slice-023 (B5 count drift across 6 sibling sites — mission-brief AC #2 cell + design.md L120/121/130/131 + design.md L225 + design.md L344 + audit unit-test assertion; all swept to canonical `17/17/17` post-B5 fix). **Cross-mission-brief-vs-design-consistency-checking** (slice-022 NEW Critic-MISS class at N=1+): N=1 → **N=3 cumulative at slice-023** (B5 + B3 + M5 are three independent cross-file consistency failures within this slice's draft).
