# Validation: Slice 003 add-val-1-imports-allowlist

**Date**: 2026-05-09
**Result**: PASS

All 4 ACs verified with both pytest assertions AND real-CLI subprocess invocation from project root. VAL-1 self-application surfaced 1 Important finding (defer-resolved by exercising the slice's own new feature). Shippability catalog (slice-001 + slice-002 critical paths) 33/33 PASS — no regression.

## Per-criterion results

### AC #1: `parse_declared_deps` reads `[tool.setuptools] packages` from pyproject.toml

- **Status**: PASS
- **Evidence (pytest)**:
  ```
  tests/methodology/test_validate_slice_layers.py::test_parse_declared_deps_reads_setuptools_packages PASSED
  tests/methodology/test_validate_slice_layers.py::test_setuptools_packages_resolves_internal_import PASSED
  ```
- **Evidence (real CLI from project root)**: invoked against this repo's own `pyproject.toml` (which declares `[tool.setuptools] packages = ["tools"]` per INST-1):
  ```
  $PY -m tools.validate_slice_layers --slice /tmp/val_ac1_slice \
    --changed-files /tmp/val_ac1/uses_tools.py --no-carry-over --skip-secrets --json
  ```
  Output (relevant fields):
  ```json
  {
    "import_findings": [],
    "declared_deps": ["pytest", "pyyaml", "tools", "tree_sitter", "tree_sitter_go", "tree_sitter_typescript"],
    "summary": {"important_count": 0, "total_findings": 0}
  }
  ```
  `tools` appears in `declared_deps` — the auto-read picked it up. `from tools.validate_slice_layers import …` resolves cleanly with NO `--imports-allowlist` flag.
- **Notes**: Behavior matches design (lenient PEP 621 + Poetry + setuptools-packages + requirements.txt union). Fixture pyproject `pyproject_with_setuptools_packages.toml` declares `my_internal_pkg`; both unit tests confirm presence in declared set.

### AC #2: `--imports-allowlist <name>` flag (repeatable)

- **Status**: PASS
- **Evidence (pytest)**:
  ```
  test_imports_allowlist_flag_resolves_listed_name PASSED
  test_imports_allowlist_flag_repeatable_accumulates PASSED
  test_cli_imports_allowlist_rejects_empty_string PASSED
  test_cli_imports_allowlist_clean_on_internal_imports PASSED
  ```
- **Evidence (real CLI — strict-empty rejection)**:
  ```
  $PY -m tools.validate_slice_layers --slice /tmp/val_ac2_slice --imports-allowlist ""
  validate_slice_layers: error: --imports-allowlist requires a non-empty package name
  ```
  Canonical error message emitted; argparse exits with code 2 (verified via SystemExit in pytest).
- **Evidence (real CLI — `--help`)**: `python -m tools.validate_slice_layers --help` shows:
  ```
  --imports-allowlist NAME
                        Additional package name to treat as resolved by Layer
                        B (repeatable). Useful for non-pip-installed
                        conventional roots like 'tests'. Values are
                        name-normalized. Empty / whitespace-only values are
                        rejected at parse time.
  ```
  Flag appears in usage line: `[--imports-allowlist NAME]`. Help text accurate.
- **Notes**: Lenient/strict asymmetry verified — Python API silently skips empty-after-normalize entries (per ADR-002); CLI rejects via parser.error. Repeatable usage `--imports-allowlist tests --imports-allowlist scripts` accumulates both names into `declared` (verified by `test_imports_allowlist_flag_repeatable_accumulates`).

### AC #3: slice-002 archive replay returns 0 Layer B findings

- **Status**: PASS (with reality-surprise observation — see below)
- **Evidence (pytest)**:
  ```
  test_slice_002_archive_replay_zero_findings_with_allowlist PASSED
  ```
- **Evidence (real CLI from project root, single-line PowerShell-friendly)**:
  ```
  $PY -m tools.validate_slice_layers \
    --slice architecture/slices/archive/slice-002-fix-diagnose-contract-and-cwd-mismatch \
    --changed-files tests/methodology/test_validate_slice_layers.py \
                    tests/skills/diagnose/test_skill_md_pins.py \
                    tests/methodology/test_risk_register_audit_real_file.py \
    --no-carry-over --skip-secrets --imports-allowlist tests
  ```
  Output:
  ```
  VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).

  Clean — both layers passed.
  ```
  Exit code 0. Cardinal verification PASS.
- **Evidence (control — same invocation WITHOUT `--imports-allowlist`)**:
  ```
  VAL-1 layered safety checks: 0 secret(s), 3 import finding(s), 0 suppressed (allowlisted).
  Important (Layer B — dependency hallucination):
    [Important] tests\methodology\test_validate_slice_layers.py:27 (hallucinated-import) `tests`
    [Important] tests\skills\diagnose\test_skill_md_pins.py:15 (hallucinated-import) `tests`
    [Important] tests\methodology\test_risk_register_audit_real_file.py:16 (hallucinated-import) `tests`
  ```
  Exit code 1. Three remaining `tests` findings — exactly what `--imports-allowlist tests` is designed to silence.
- **Notes**: Reality surprise — control finding count is 3, not 5 as the mission brief baseline predicted. Reason: the setuptools-packages auto-read (AC #1) now resolves the 2 `tools` findings WITHOUT needing the flag. So pre-fix baseline was `5 = 3 (tests) + 2 (tools)`; post-fix-without-flag is `3 = 3 (tests) + 0 (tools auto-resolved)`; post-fix-with-flag is `0`. The AC's actual claim ("0 Layer B findings with the flag") is satisfied. The "vs 5" baseline shifted because AC #1 turned out to be more powerful than strictly needed. **Net effect: the slice does MORE than the AC required, not less. Surprise is positive.**

### AC #4: SKILL.md Step 5b prose documents both new resolution paths

- **Status**: PASS
- **Evidence (pytest)**:
  ```
  test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages PASSED
  ```
- **Evidence (literal substring presence in `skills/validate-slice/SKILL.md`)**:
  - Line 130: `**Two extension points for project-internal imports** (per slice-003, ADR-002): (a)` `[tool.setuptools] packages` `is auto-read — if your project declares its own pip-shipped package there, internal `from <self_pkg>.X import …` resolves without any flag; (b)` `--imports-allowlist <name>` `(repeatable) extends the resolved set per-invocation for non-pip-installed conventional roots.`
  - Line 128: existing Layer B description now also mentions `[tool.setuptools] packages` (extended in place).
  - Line 136: canonical invocation example with `--imports-allowlist tests`.
  - Line 139: lenient/strict asymmetry note.
  - Line 143: extended refusal-semantics resolution path mentions both new options.
- **Notes**: Existing `test_validate_slice_skill_references_val_1` continues to PASS — no regression on prior prose-pin substrings (`VAL-1`, `validate_slice_layers`, `credential scan`, `hallucinat`).

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: Slice modifies a synchronous CLI tool + skill prose. No multi-user, multi-device, multi-account, sync, sharing, or collaboration surface. Single-instance validation is appropriate.

## VAL-1 self-application (Step 5b)

The methodology demands that /validate-slice run VAL-1 on this slice's changed files. Doing so on slice-003's changed files produced **1 Important finding** on the new fixture file:

```
[Important] tests\methodology\fixtures\validate_layers\imports_internal_pkg.py:4
  (hallucinated-import) `my_internal_pkg`
  `from my_internal_pkg.x import …` references package 'my_internal_pkg' not declared
  in pyproject.toml or requirements.txt.
```

**Disposition**: defer-with-rationale (allowed per VAL-1 protocol for Important findings). Rationale: `my_internal_pkg` is a fake package name that exists ONLY inside the fixture's own `pyproject_with_setuptools_packages.toml`, which is itself test data. The fixture's import statement is never executed at runtime — it's read as text by `scan_imports` to verify the audit's behavior. From the perspective of THIS repo's pyproject.toml (which is what VAL-1 reads at validate-time), `my_internal_pkg` is genuinely undeclared, so the finding is "correct in shape, irrelevant in semantics".

**Resolution exercised**: re-ran VAL-1 with the slice's own new feature — `--imports-allowlist tests --imports-allowlist my_internal_pkg`:

```
$PY -m tools.validate_slice_layers --slice architecture/slices/slice-003-add-val-1-imports-allowlist \
  --changed-files tools/validate_slice_layers.py tests/methodology/test_validate_slice_layers.py \
                  skills/validate-slice/SKILL.md \
                  tests/methodology/fixtures/validate_layers/pyproject_with_setuptools_packages.toml \
                  tests/methodology/fixtures/validate_layers/imports_internal_pkg.py \
  --imports-allowlist tests --imports-allowlist my_internal_pkg
```

Output:
```
VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).

Clean — both layers passed.
```

The slice validates cleanly using its own ship — pleasing self-referential symmetry. Note for future canonical /validate-slice invocations against this repo: `--imports-allowlist tests` is the standard; fixture-validating slices may need additional allowlist entries.

## Walking-skeleton audit (Step 5c)

Not applicable — `**Walking-skeleton**: false` in mission brief frontmatter. WS-1 audit returns clean silently per default-off semantics.

## Exploratory-charter audit (Step 5d)

Not applicable — `**Exploratory-charter**: false` in mission brief frontmatter. ETC-1 audit returns clean silently per default-off semantics.

## Shippability catalog regression check (Step 5.5)

| # | Slice | Critical-path test | Result | Runtime |
|---|-------|---------------------|--------|---------|
| 1 | slice-001-diagnose-orchestration-fix | `pytest tests/skills/diagnose/` | **30/30 PASS** | 1.66s |
| 2 | slice-002-fix-diagnose-contract-and-cwd-mismatch | `pytest tests/methodology/test_risk_register_audit_real_file.py tests/skills/diagnose/test_skill_md_pins.py::test_pass_templates_match_skill_md_step5_contract tests/skills/diagnose/test_skill_md_pins.py::test_no_legacy_no_bash_no_python_phrase` | **3/3 PASS** | 0.04s |

Total: 33/33 PASS, ~1.7s wall clock. No regression.

## Reality surprises

1. **AC #3 baseline shifted from 5 to 3 because AC #1 is more powerful than strictly required**: the `[tool.setuptools] packages` auto-read alone eliminates the `tools` findings without the flag. Pre-fix baseline 5 = 3 `tests` + 2 `tools`; post-fix without flag: 3 (only `tests` remain); post-fix with `--imports-allowlist tests`: 0. The AC's actual claim is satisfied; only the framing of "vs 5" shifted. Positive surprise — the implementation does MORE than promised.

2. **VAL-1 self-application meta-irony**: validating a slice that ships a fixture-with-fake-package using the same VAL-1 audit produces 1 Important finding on that fixture's import statement. Defer-with-rationale (the fixture's package isn't declared in THIS repo's pyproject; it's intentionally fake). Resolution exercised by using the slice's own `--imports-allowlist` flag — pleasing self-referential symmetry.

Both surprises are observations, not problems. No risk-register additions warranted. No follow-on slice triggered.

## Pre-finish gate (terminal)

- [x] All 4 ACs PASS with evidence (above)
- [x] Must-not-defer addressed (4 items, all SATISFIED — see build-log.md T21)
- [x] /drift-check passes (manual scan: vault and code aligned)
- [x] Mid-slice smoke still passes (re-verified during /validate-slice)
- [x] Full `test_validate_slice_layers.py` test suite green (32/32)
- [x] TF-1 audit `--strict-pre-finish` clean (8/8 PASSING)
- [x] WIRE-1 audit clean
- [x] Mock-budget lint clean
- [x] BC-1 audit applies 3 Important rules — all keyword-trigger false positives, deferred-with-rationale (see build-log.md T22)
- [x] Shippability catalog regression (slice-001 + slice-002): 33/33 PASS
- [x] VAL-1 self-application: defer-resolved via `--imports-allowlist`

**Verdict: PASS — proceed to /reflect.**
