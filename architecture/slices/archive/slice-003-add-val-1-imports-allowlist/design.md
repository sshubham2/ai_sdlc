# Design: Slice 003 add-val-1-imports-allowlist

**Date**: 2026-05-09
**Mode**: Standard (per `architecture/triage.md` is absent — pipeline mode is Standard by convention; risk-tier `low` per mission brief)

## What's new

- `tools/validate_slice_layers.py`:
  - `parse_declared_deps` gains a new code path that reads `[tool.setuptools] packages` (the explicit-list form) and adds each entry to the returned `deps` set, name-normalized via `_normalize_pkg` (codebase convention — lowercase + collapse `[-_.]+` to single `_`; not strict PEP 503 which mandates hyphens).
  - `run_layers` gains a new keyword argument `imports_allowlist: list[str] | None = None`; values are name-normalized via `_normalize_pkg` and merged into the `declared` set before it's passed to `scan_imports`. The Python API is **lenient**: entries that normalize to empty are silently skipped (be liberal in what you accept programmatically).
  - `main` (CLI) gains a `--imports-allowlist <name>` flag with `action="append"`, populated into a list and forwarded to `run_layers(imports_allowlist=…)`. The CLI is **strict**: empty / whitespace-only values are rejected at parse time with `parser.error(...)` → exit 2. The lenient/strict asymmetry mirrors stdlib argparse conventions.
- `tests/methodology/fixtures/validate_layers/pyproject_with_setuptools_packages.toml`: new fixture pyproject declaring `[tool.setuptools] packages = ["my_internal_pkg"]` for the AC #1 unit test.
- `tests/methodology/fixtures/validate_layers/imports_internal_pkg.py`: new fixture `.py` with `from my_internal_pkg.x import y` to drive the resolution test (mirrors existing `imports_clean.py` pattern).
- `tests/methodology/test_validate_slice_layers.py`: 8 new test functions per the test-first plan (4 unit + 3 CLI-level + 1 archive-replay integration). The 8th is `test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages` — a prose-pin against `skills/validate-slice/SKILL.md` for AC #4 (per Critic M1).
- `skills/validate-slice/SKILL.md` Step 5b prose: documents the two new resolution paths (auto-read of `[tool.setuptools] packages`; `--imports-allowlist <name>` repeatable flag) directly under the Layer B description. **AC #4** locks both literal substrings via the new prose-pin test (`--imports-allowlist` AND `[tool.setuptools] packages` must appear).
- `architecture/decisions/ADR-002-val-1-imports-allowlist-explicit-flag.md`: records the explicit-flag-over-auto-derive choice for future maintainers.

## What's reused

- [[ADR-001]] (no relationship; just noting it's the only existing ADR)
- `_normalize_pkg(name)` at `tools/validate_slice_layers.py:258` — applied to setuptools-packages entries AND `--imports-allowlist` entries for consistency with the existing `declared` set's PEP 503 normalization
- `_check_import_resolves(import_top, declared)` at `tools/validate_slice_layers.py:315` — signature unchanged; the `declared` set passed to it grows transparently
- `scan_imports(file_paths, declared_deps)` at `tools/validate_slice_layers.py:332` — signature unchanged
- `_KNOWN_ALIASES` table at `tools/validate_slice_layers.py:102` — unchanged; aliases continue to resolve via the existing path
- Existing fixture `pyproject_fixture.toml` — left alone; new fixture is a sibling so existing tests don't shift behavior
- Existing TOML parser path (`tomllib`) — same `try / except` block
- `tests/methodology/conftest.py:REPO_ROOT` — used by the archive-replay integration test
- `architecture/slices/archive/slice-002-fix-diagnose-contract-and-cwd-mismatch/` — the AC #3 reference target; its three changed test files (`test_validate_slice_layers.py`, `test_skill_md_pins.py`, `test_risk_register_audit_real_file.py`) are the source files that today produce 5 Layer B findings and after the fix should produce 0
- `methodology-changelog.md` v0.14.0 (VAL-1 origin) and v0.20.0 (INST-1 — confirms `[tool.setuptools] packages = ["tools"]` is the canonical declaration in this repo)

## Components touched

### `tools/validate_slice_layers.py` (modified)
- **Responsibility**: VAL-1 layered safety checks — Layer A (regex credential scan) + Layer B (Python import vs declared-deps resolution). This slice extends Layer B's resolution rules.
- **Lives at**: `tools/validate_slice_layers.py`
- **Key interactions**:
  - Reads `pyproject.toml` (PEP 621 + Poetry + setuptools-packages now)
  - Reads `requirements.txt` (legacy projects)
  - ast-parses `.py` files via `scan_imports`
  - Called by `skills/validate-slice/SKILL.md` Step 5b at /validate-slice time
  - Tested by `tests/methodology/test_validate_slice_layers.py` (30+ existing tests must remain green)

### `skills/validate-slice/SKILL.md` (modified)
- **Responsibility**: Skill prose — drives `/validate-slice`'s real-environment validation flow, including Step 5b which invokes `tools.validate_slice_layers`.
- **Lives at**: `skills/validate-slice/SKILL.md`
- **Key interactions**: Read by Claude main thread when `/validate-slice` runs. Step 5b prose tells Claude to invoke `validate_slice_layers` and refuse `/reflect` on Critical findings.

### `tests/methodology/test_validate_slice_layers.py` (modified)
- **Responsibility**: Unit + integration tests for `tools/validate_slice_layers.py`. This slice adds 7 test functions covering the new behavior.
- **Lives at**: `tests/methodology/test_validate_slice_layers.py`
- **Key interactions**: Imports `from tools.validate_slice_layers import …` (which today is one of the false-positive findings the slice fixes — pleasing self-referential symmetry).

## Contracts added or changed

### `run_layers` Python API (additive kwarg)
- **Defined in code at**: `tools/validate_slice_layers.py:397`
- **Change**: new `imports_allowlist: list[str] | None = None` keyword parameter, default `None`. Values are name-normalized via `_normalize_pkg` and merged into `declared` set before `scan_imports` is called. Existing callers (zero outside this module + its tests) continue to work unchanged.
- **Auth model**: N/A (library function)
- **Error cases (lenient — be liberal in what you accept)**: `None` → no merge; empty list → no merge (no-op); non-empty list → each entry normalized + added; entries that normalize to empty (`""`, whitespace-only, etc.) are silently skipped. **No `ValueError` raised** — the library never decides whether the caller's input is "valid"; that's the CLI boundary's job. Programmer error of passing `[""]` produces an observable no-op that an integration test can detect (the entry doesn't show up in `result.declared_deps`), but doesn't crash.

### CLI surface (additive flag)
- **Endpoint**: `python -m tools.validate_slice_layers --imports-allowlist <name>` (repeatable)
- **Defined in code at**: `tools/validate_slice_layers.py:469` (`main`)
- **Auth model**: N/A (CLI)
- **Error cases**:
  - Empty string (`--imports-allowlist ""`) → `parser.error("--imports-allowlist requires a non-empty package name")`, exit code 2
  - Whitespace-only (`--imports-allowlist "  "`) → same; reject after `.strip()`
  - Duplicate entries (`--imports-allowlist tests --imports-allowlist tests`) → silently deduped by set membership in `declared`; not an error
  - Mixed case (`--imports-allowlist Tests`) → normalized to `tests` via `_normalize_pkg`; resolves identically

### Backwards compatibility
- All three changes are additive: when `imports_allowlist=None` (Python API) or no `--imports-allowlist` flag is passed (CLI), behavior is byte-identical to today. Existing 30+ tests must continue passing without modification — slice-003's pre-finish gate verifies this.
- Existing CLI invocations (e.g., from `skills/validate-slice/SKILL.md` Step 5b's example) continue to work; `--imports-allowlist` is opt-in.

## Data model deltas

None. This slice is library / CLI logic only.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces zero new modules — all changes are modifications to existing files (`validate_slice_layers.py`, `test_validate_slice_layers.py`, `validate-slice/SKILL.md`). Two new fixture files are added, but per WIRE-1 convention, test fixtures don't require consumer entry points (they're consumed by the test functions that reference them). The matrix is empty by design; the audit treats zero-row matrices as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-002-val-1-imports-allowlist-explicit-flag]] — choose explicit `--imports-allowlist <name>` over auto-derived (e.g., from pytest `testpaths` or `tests/__init__.py` presence) — reversibility: **cheap**

## Authorization model for this slice

N/A — `validate_slice_layers` is a methodology tool with no auth surface. CLI runs as the invoking user; library API is in-process. No multi-tenant / multi-user concerns.

## Error model for this slice

| Trigger | Layer | Behavior |
|---------|-------|----------|
| `--imports-allowlist ""` | CLI | `parser.error(...)` → exit 2 (usage error) |
| `--imports-allowlist`-only-whitespace (e.g., `--imports-allowlist "   "`) | CLI | same as above (CLI runs `.strip()` before the empty check) |
| `imports_allowlist=[""]` or `imports_allowlist=["   "]` or `imports_allowlist=[None-like]` (Python API) | run_layers | values that normalize to empty are silently skipped (be liberal in what you accept programmatically; strict only at the CLI boundary). No `ValueError` raised — surfaces as "this allowlist entry didn't resolve anything," which is observable via `result.declared_deps` (the entry isn't there) but not fatal |
| Malformed pyproject.toml `[tool.setuptools] packages` (e.g., `packages = "tools"` not a list) | parse_declared_deps | wrap the read in the same `try / except (tomllib.TOMLDecodeError, OSError)` block already protecting the file read; on `TypeError` from non-list value, swallow + skip (no crash). Existing PEP 621 / Poetry reads use the same defensive pattern |
| Setuptools `find` auto-discovery (`[tool.setuptools.packages.find]`) | parse_declared_deps | not handled in v1 (out-of-scope per mission brief). Falls through silently — the `find`-based project still gets stdlib + PEP 621 deps + alias resolution + `--imports-allowlist`, just not the auto-derived package list |
| `[tool.setuptools]` table entirely absent | parse_declared_deps | no-op (the table read is a `dict.get(..., {})` chain that returns empty cleanly) |

## Implementation sketch

The fix is small. Three localized edits in `tools/validate_slice_layers.py`:

1. **`parse_declared_deps`**, **inside the existing `if pyproject_path and pyproject_path.exists() and tomllib is not None:` block** (currently spans L270-L301), **after the Poetry-dev-deps loop** (after `deps.add(_normalize_pkg(name))` at the end of that loop, before the block closes at L301):
   ```python
   # setuptools (explicit list form only; `find` auto-discovery is v2).
   # Lives inside the `if pyproject_path ...` branch — `data` is only defined here.
   setuptools_packages = (
       data.get("tool", {}).get("setuptools", {}).get("packages", [])
   )
   if isinstance(setuptools_packages, list):
       for name in setuptools_packages:
           if isinstance(name, str) and name:
               deps.add(_normalize_pkg(name))
   ```

2. **`run_layers`**, signature + body:
   ```python
   def run_layers(
       slice_folder: Path,
       changed_files: list[Path],
       secrets_allowlist: Path | None = None,
       pyproject: Path | None = None,
       requirements: Path | None = None,
       skip_secrets: bool = False,
       skip_deps: bool = False,
       skip_if_carry_over: bool = True,
       imports_allowlist: list[str] | None = None,  # NEW
   ) -> LayersResult:
       ...
       if not skip_deps:
           declared = parse_declared_deps(pyproject, requirements)
           for name in imports_allowlist or []:
               normalized = _normalize_pkg(name)
               if normalized:
                   declared.add(normalized)
           result.declared_deps = sorted(declared)
           result.import_findings = scan_imports(changed_files, declared)
       ...
   ```

3. **`main`**, after the `--skip-deps` flag definition:
   ```python
   parser.add_argument(
       "--imports-allowlist", action="append", default=None,
       metavar="NAME",
       help=(
           "Additional package names to treat as resolved (repeatable). "
           "Useful for non-pip-installed conventional roots like 'tests'. "
           "Values are PEP 503 normalized."
       ),
   )
   ```
   Then validate non-empty + forward:
   ```python
   if args.imports_allowlist is not None:
       cleaned = [s.strip() for s in args.imports_allowlist]
       if any(not c for c in cleaned):
           parser.error(
               "--imports-allowlist requires a non-empty package name"
           )
       args.imports_allowlist = cleaned
   ...
   result = run_layers(
       ...
       imports_allowlist=args.imports_allowlist,
   )
   ```

The skill-prose update for `skills/validate-slice/SKILL.md` Step 5b appends two short paragraphs after the existing Layer B description — one for setuptools-packages (auto, no flag), one for `--imports-allowlist` with the canonical `tests` example.

## Testing strategy

Unit + CLI + archive-replay + prose-pin layering, mapped 1-to-1 from the test-first plan in mission-brief.md:

- AC #1 — 2 unit tests (`test_parse_declared_deps_reads_setuptools_packages`, `test_setuptools_packages_resolves_internal_import`)
- AC #2 — 4 tests (2 unit on the function-API lenient path; 2 CLI-level via `main(argv=[...])` — one for strict empty-string rejection, one for clean resolution end-to-end)
- AC #3 — 1 integration test (archive-replay against slice-002 archive folder)
- AC #4 — 1 prose-pin test (`test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages` — analogous to existing `test_validate_slice_skill_references_val_1`; asserts both literal substrings `--imports-allowlist` AND `[tool.setuptools] packages` appear in `skills/validate-slice/SKILL.md`)

The archive-replay test reads the slice-002 archive's three changed test files via `REPO_ROOT / "tests" / "methodology" / "..."` etc., calls `main(["--slice", str(slice_002_archive_folder), "--changed-files", ...]) ` (capturing stdout to verify "0 import finding(s)"), and asserts the integer return is 0.

All 8 tests are PENDING at the start of build (per TF-1); they progress to WRITTEN-FAILING in early build, then PASSING at end. `tools/test_first_audit.py --strict-pre-finish` enforces this at /build-slice pre-finish.

## Reflection-corrected notes

(none — this is the initial design pre-build; if `/build-slice` discovers something this design got wrong, the deviation goes in `build-log.md` and a "Reflection-corrected" note appended here.)
