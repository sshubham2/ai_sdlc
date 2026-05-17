# Slice 003: add-val-1-imports-allowlist

**Mode**: Standard
**Risk tier**: low — modifies a methodology audit's import-resolution logic + adds a CLI flag; no auth / contracts / data model / multi-device / external integrations / security-sensitive paths
**Critic required**: false (low tier, no mandatory triggers). Voluntary Critic recommended — touches validation-methodology + skill prose, which is cross-cutting; voluntary Critic returned real findings on slice-001 + slice-002 (2/2 confirmed pattern).
**Estimated work**: <1 day (~2–3 hours)
**Risk retired**: none in `risk-register.md`. Addresses a confirmed methodology gap (VAL-1 Layer B internal-imports recurrence flagged across slice-001 + slice-002 reflections + aggregated lessons in `slices/_index.md`).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

VAL-1 Layer B currently flags every internal `from tests.X import …` and `from tools.X import …` as a `hallucinated-import` — observed 6 findings on slice-001's changed files and 5 findings on slice-002's changed files (`assemble`, `tests`, `tools`). The defer-with-rationale ritual every slice is wasteful; the false positives drown out real signal. This slice teaches Layer B to (a) read the project's own declared `[tool.setuptools] packages` so `tools` resolves automatically in this repo, and (b) accept a repeatable `--imports-allowlist <name>` CLI flag for non-pip-installed conventional roots like `tests`. Re-running Layer B on slice-002's three changed test files with `--imports-allowlist tests` should return 0 Layer B findings (vs 5 today).

## Acceptance criteria

1. `parse_declared_deps` reads `[tool.setuptools] packages` from `pyproject.toml` and treats those entries as resolved declared packages (so `from tools.X import …` resolves without any CLI flag in this repo).
2. `validate_slice_layers` accepts a repeatable `--imports-allowlist <name>` flag whose values are added to the resolved set used by `_check_import_resolves`, alongside stdlib + declared deps + known aliases (so `--imports-allowlist tests` makes `from tests.methodology.conftest import …` resolve cleanly).
3. Re-running `python -m tools.validate_slice_layers --slice <slice-002 archive folder> --changed-files tests/methodology/test_validate_slice_layers.py tests/skills/diagnose/test_skill_md_pins.py tests/methodology/test_risk_register_audit_real_file.py --no-carry-over --skip-secrets --imports-allowlist tests` returns **exit code 0** with **0 Layer B findings** (vs 5 today on the same invocation without the flag).
4. `skills/validate-slice/SKILL.md` Step 5b prose documents both new resolution paths — i.e., the literal substrings `--imports-allowlist` AND `[tool.setuptools] packages` both appear in the file (so future contract drift is caught by the prose-pin test, consistent with how slice-002 locked the canonical Step 5 contract).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_validate_slice_layers.py | test_parse_declared_deps_reads_setuptools_packages | PASSING |
| 1 | unit | tests/methodology/test_validate_slice_layers.py | test_setuptools_packages_resolves_internal_import | PASSING |
| 2 | unit | tests/methodology/test_validate_slice_layers.py | test_imports_allowlist_flag_resolves_listed_name | PASSING |
| 2 | unit | tests/methodology/test_validate_slice_layers.py | test_imports_allowlist_flag_repeatable_accumulates | PASSING |
| 2 | integration | tests/methodology/test_validate_slice_layers.py | test_cli_imports_allowlist_rejects_empty_string | PASSING |
| 2 | integration | tests/methodology/test_validate_slice_layers.py | test_cli_imports_allowlist_clean_on_internal_imports | PASSING |
| 3 | integration | tests/methodology/test_validate_slice_layers.py | test_slice_002_archive_replay_zero_findings_with_allowlist | PASSING |
| 4 | unit | tests/methodology/test_validate_slice_layers.py | test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `[tool.setuptools] packages` honored | `test_parse_declared_deps_reads_setuptools_packages` (declares `tools` in fixture pyproject; asserts `_check_import_resolves("tools", declared)` is True without flag). |
| 2 | `--imports-allowlist <name>` plumbs through | `test_imports_allowlist_flag_resolves_listed_name` (Python API call), `test_imports_allowlist_flag_repeatable_accumulates` (multi-flag), `test_cli_imports_allowlist_rejects_empty_string` (CLI-level — calls `main(["--imports-allowlist", ""])` and asserts `SystemExit(2)` with `parser.error` message), `test_cli_imports_allowlist_clean_on_internal_imports` (CLI invocation through `main()` with full argv, captures stdout). |
| 3 | End-to-end clean replay on slice-002 archive | `test_slice_002_archive_replay_zero_findings_with_allowlist` runs the full CLI invocation against the slice-002 archive folder and asserts exit code 0 + zero Layer B findings. Manual smoke at validate-time: invoke CLI exactly as in AC #3 from project root, observe "Clean — both layers passed." line. |
| 4 | SKILL.md prose pin for new flags | `test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages` reads `skills/validate-slice/SKILL.md`, asserts both literal substrings `--imports-allowlist` AND `[tool.setuptools] packages` appear (analogous to existing `test_validate_slice_skill_references_val_1` at L404). Locks the canonical wording so future contract drift fails loudly. |

## Must-not-defer

- [ ] Input validation on `--imports-allowlist` at the CLI boundary (reject empty / whitespace-only strings via `parser.error`; dedupe naturally via set membership; name-normalize via `_normalize_pkg` — codebase convention, not strict PEP 503 — for consistency with declared-deps comparison)
- [ ] Carry-over exemption (`_slice_is_carry_over`) preserved — new code paths must not bypass NFR-1
- [ ] `--skip-deps` short-circuit preserved — when set, neither setuptools-packages reading nor allowlist plumbing should run
- [ ] No regression in existing 30+ tests in `test_validate_slice_layers.py` — full module passes after changes

(SKILL.md prose update — promoted to AC #4 per Critic finding M1; carries its own test-first row.)

## Out of scope

- TS/JS dependency hallucination (still v2-deferred per VAL-1 v1 limitations)
- Reading non-setuptools build-system tables (Hatch `[tool.hatch.build.targets.wheel] packages`, PDM, Flit) — setuptools is sufficient for this repo; multi-backend support is a follow-on if a different project hits the same gap
- Layer A (credential scan) changes — out of scope; slice is Layer-B-only
- Retroactively re-validating archived slices — slices already shipped with deferred-rationale stay shipped; the change applies forward
- Auto-derivation of `tests` as an implicit allowlist entry from pytest conventions — explicit `--imports-allowlist tests` in skill invocations is preferable to magic-default behavior
- Bumping VAL-1 to a new minor version in `methodology-changelog.md` — this is an additive enhancement, not a breaking semantic change to the rule; `/reflect` decides whether to log a v0.20.x changelog bullet

## Dependencies

- Prior slices: [[slice-001-diagnose-orchestration-fix]] (introduced VAL-1 originally), [[slice-002-fix-diagnose-contract-and-cwd-mismatch]] (confirmed the recurrence)
- Vault refs: [[skills/validate-slice/SKILL.md]] Step 5b, [[tools/validate_slice_layers.py]], [[tests/methodology/test_validate_slice_layers.py]]
- Risk register: none directly retired (this is a methodology-gap fix, not a risk retirement)
- Methodology: `methodology-changelog.md` v0.14.0 (VAL-1 origin); v0.20.0 (INST-1 — confirms `tools` package ships via pip and is declared in `[tool.setuptools] packages`)

## Mid-slice smoke gate

At ~50% of build (after `parse_declared_deps` reads setuptools-packages + `--imports-allowlist` flag is wired through, before all unit tests pass), run from project root (single line — works in PowerShell AND Bash; per slice-001 cross-shell lesson, avoid Bash `\` continuation in commands the user may copy-paste):

```
$PY -m tools.validate_slice_layers --slice architecture/slices/archive/slice-002-fix-diagnose-contract-and-cwd-mismatch --changed-files tests/methodology/test_validate_slice_layers.py tests/skills/diagnose/test_skill_md_pins.py tests/methodology/test_risk_register_audit_real_file.py --no-carry-over --skip-secrets --imports-allowlist tests
```

Expected: `0 import finding(s)` (down from `5 import finding(s)` today). Exit code 0.

If this fails: STOP. Either the setuptools-packages read isn't picking up `tools`, or the allowlist plumbing isn't reaching `_check_import_resolves`. Diagnose by re-running with `--json` and inspecting `declared_deps` in the output — `tools` should be there post-fix.

## Pre-finish gate

- [ ] All 4 ACs PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (4 items)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression after final cleanup)
- [ ] Full `test_validate_slice_layers.py` test suite green (no regression on existing 30+ tests)
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes — all 8 test-first rows PASSING
- [ ] No new TODOs / FIXMEs / debug prints in `tools/validate_slice_layers.py` or `skills/validate-slice/SKILL.md`
- [ ] Shippability catalog regression check (run all entries in `architecture/shippability.md`)
