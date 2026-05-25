# Slice 023: audit-tools-default-utf8-stdout

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: Windows cp1252 console encoding class (N=6 cumulative recurrence across slices 007, 016, 018, 020, 021, 022; structurally overdue per slice-022 aggregated lessons). Not tracked in `risk-register.md` as a named risk entry — recurrence is documented in archived `reflection.md` DEVIATIONs + `_index.md` aggregated lessons rather than as an R-N entry.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Every `tools/*.py` audit currently inherits the platform-default console encoding. On Windows that's `cp1252`, which lacks U+2192 (`→`) and other interpolated symbols that legitimately appear in audit output (TF-1 status transitions echoed back from mission-brief content, branch names, etc.). Slices 007 / 016 / 018 / 020 / 021 / 022 each hit this and worked around it with inline `$env:PYTHONIOENCODING="utf-8"`. This slice retires the recurrence by reconfiguring stdout / stderr to UTF-8 inside every audit tool's `main()` via a shared helper, and codifies a structural audit (UTF8-STDOUT-1) that refuses any new `tools/*.py` with a `main()` that doesn't call it.

## Acceptance criteria

1. A shared helper `tools/_stdout.py` exposes `reconfigure_stdout_utf8()` that (a) calls `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` and the same for `sys.stderr` when the streams expose `reconfigure`, (b) is a no-op when streams have already been reconfigured or lack `reconfigure` (test-capture streams under pytest), (c) is idempotent under repeat invocation.
2. Every `tools/*.py` module exposing a `main(argv: list[str] | None = None) -> int` function calls `_stdout.reconfigure_stdout_utf8()` as the first statement of `main()` (before `argparse` parsing) — verified by a structural audit run over the `tools/` directory.
3. A new structural audit `tools/utf8_stdout_audit.py` enumerates every `tools/*.py` module exposing a `main()` function (excluding `_stdout.py` itself and `__init__.py`), and emits one violation per module where the first executable statement of `main()` is not the canonical `reconfigure_stdout_utf8()` call. Exit code 1 on any violation; 0 on clean. `--json` flag emits structured output; default emits human-readable text.
4. A behavioural regression test invokes each audit tool via `subprocess.run(..., text=True, encoding="utf-8", errors="replace", env={"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0", ...})` with fixture input containing U+2192 — every audit must complete without `UnicodeEncodeError` / `UnicodeDecodeError` traceback in stderr (assertion is on encoding-survival, NOT exit code 0, because synthetic fixture slices may legitimately return exit 1 on non-encoding violations like PENDING TF-1 rows). Test lives at `tests/methodology/test_utf8_stdout_regression.py` (split from audit unit tests per M5 ACCEPTED-FIXED for runtime isolation; 17×subprocess ≈ 5–17s). Per-tool argv strategy enumerated in design.md "Error model" surface 3.
5. `methodology-changelog.md` v0.37.0 entry codifies rule **UTF8-STDOUT-1** with N-surface schema-pin: (a) `tools/_stdout.py` helper presence + idempotency contract, (b) `tools/utf8_stdout_audit.py` structural rule, (c) one-line invocation pattern at top of every `main()`. ADR-021 (reversibility: cheap) accepted. Shippability catalog row 23 added pointing at the new audit + regression test.

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation per **TF-1**. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools.test_first_audit --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_stdout_helper.py | test_reconfigure_called_on_real_streams_with_reconfigure | PASSING |
| 1 | unit | tests/methodology/test_stdout_helper.py | test_reconfigure_noop_on_streams_without_reconfigure_attribute | PASSING |
| 1 | unit | tests/methodology/test_stdout_helper.py | test_reconfigure_idempotent_under_repeat_invocation | PASSING |
| 1 | unit | tests/methodology/test_stdout_helper.py | test_reconfigure_sets_errors_replace_not_strict | PASSING |
| 1 | unit | tests/methodology/test_stdout_helper.py | test_reconfigure_overrides_prior_errors_strict_to_errors_replace | PASSING |
| 2 | structural | tests/methodology/test_utf8_stdout_audit.py | test_every_tool_with_main_calls_reconfigure_first | PASSING |
| 2 | structural | tests/methodology/test_utf8_stdout_audit.py | test_stdout_helper_module_itself_exempt | PASSING |
| 2 | structural | tests/methodology/test_utf8_stdout_audit.py | test_every_tool_uses_canonical_from_tools_import_stdout | PASSING |
| 3 | unit | tests/methodology/test_utf8_stdout_audit.py | test_audit_flags_tool_missing_reconfigure_call | PASSING |
| 3 | unit | tests/methodology/test_utf8_stdout_audit.py | test_audit_flags_tool_with_reconfigure_after_argparse | PASSING |
| 3 | unit | tests/methodology/test_utf8_stdout_audit.py | test_audit_clean_on_canonical_pattern | PASSING |
| 3 | unit | tests/methodology/test_utf8_stdout_audit.py | test_audit_json_output_shape | PASSING |
| 3 | unit | tests/methodology/test_utf8_stdout_audit.py | test_audit_exit_code_zero_on_clean_one_on_violation | PASSING |
| 3 | unit | tests/methodology/test_utf8_stdout_audit.py | test_output_contract_invariant | PASSING |
| 4 | regression | tests/methodology/test_utf8_stdout_regression.py | test_every_audit_tool_survives_cp1252_stdout_with_u2192_input | PASSING |
| 5 | prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_37_0_utf8_stdout_1_entry_names_all_three_surfaces | PASSING |
| 5 | prose-pin | tests/methodology/test_methodology_changelog.py | test_v_0_37_0_utf8_stdout_1_entry_pins_canonical_invocation_pattern | PASSING |
| 5 | prose-pin | tests/methodology/test_methodology_changelog.py | test_adr_021_present_and_reversibility_cheap | PASSING |
| 5 | structural | tests/methodology/test_plugin_manifest_audit.py | test_plugin_yaml_lists_utf8_stdout_audit | PASSING |
| 5 | structural | tests/methodology/test_plugin_manifest_audit.py | test_list_actual_tools_filters_leading_underscore_helpers | PASSING |
| 5 | structural | tests/methodology/test_install_audit.py | test_install_audit_enumerates_utf8_stdout_audit | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `_stdout.reconfigure_stdout_utf8()` helper exists with idempotency + duck-typing | Run `pytest tests/methodology/test_stdout_helper.py -v`; all 4 cases PASS. |
| 2 | Every audit tool with `main()` calls the helper first | Run `& $PY -m tools.utf8_stdout_audit`; exit 0, JSON output (with `--json`) reports `tools_scanned: 17, tools_with_main: 17, tools_clean: 17, status: clean` (per B5 ACCEPTED-FIXED canonical counts — post-slice tools/ has 19 .py files; exclusion list `_stdout.py` + `__init__.py`; 17 scanned, all with main(), all clean). |
| 3 | New audit tool emits violations for non-conforming tools | Run audit against synthetic fixture tool missing the call → exit 1 + violation message naming `main()` line. |
| 4 | All audit tools survive cp1252 stdout with U+2192 input | Run `pytest tests/methodology/test_utf8_stdout_regression.py::test_every_audit_tool_survives_cp1252_stdout_with_u2192_input -v`; assertion is `"UnicodeEncodeError" not in result.stderr and "UnicodeDecodeError" not in result.stderr`, NOT exit-code-0 (per M1 + M-add-4 ACCEPTED-FIXED). |
| 5 | Methodology surfaces in sync | `& $PY -m tools.plugin_manifest_audit` PASS (new tool added); `& $PY -m tools.cross_spec_parity_audit` PASS; `& $PY -m tools.install_audit` PASS; methodology-changelog v0.37.0 prose-pin tests PASS; ADR-021 file present with `reversibility: cheap`. |

## Must-not-defer

- [ ] **Idempotency**: helper must be safe to call multiple times — a tool whose `main()` invokes another tool's `main()` (or pytest re-imports a module) must not raise from double-reconfigure.
- [ ] **Test-capture compatibility**: helper must NOT crash when `sys.stdout` is pytest's `_pytest.capture.EncodedFile` or a plain `StringIO` without `reconfigure`. Duck-type the call.
- [ ] **`errors="replace"` not `errors="strict"`**: if an out-of-band non-UTF-8 character somehow appears, audit output should degrade gracefully (print `?` or `�`) rather than crash. Per slice's whole point — replace cp1252 crash with graceful output.
- [ ] **`--json` output integrity**: reconfigure happens BEFORE any `sys.stdout.write(json.dumps(...))` so JSON parsers downstream see valid UTF-8 byte sequences.
- [ ] **PMI-1 (plugin manifest)**: `plugin.yaml` `tools:` list enumerates `- path: tools/utf8_stdout_audit.py / rule: UTF8-STDOUT-1` (canonical shape per M3 ACCEPTED-FIXED — NOT `- id:`). `tools/install_audit.py` `_CANONICAL_TOOLS` adds `tools.utf8_stdout_audit`. Per B2 ACCEPTED-PENDING, `tools/plugin_manifest_audit.py:_list_actual_tools` is extended this slice with a leading-underscore filter (`if p.name != "__init__.py" and not p.name.startswith("_")`) so `tools/_stdout.py` doesn't trigger an `orphan-tool` violation. PMI-1 v1.1 retirement-proof invariant preserved (gate body unchanged; only the discovery filter narrows).
- [ ] **INST-1 (install audit) parity**: `_CANONICAL_TOOLS` matches `plugin.yaml` exactly.
- [ ] **mini-CAD-for-build-checks**: `architecture/build-checks.md` (if it enumerates audits) gets one new row for UTF8-STDOUT-1.
- [ ] **No regression in existing audits**: full `pytest` suite (≥497 tests per slice-022 baseline) PASS in <60s.
- [ ] **CAD-1 byte-equality preserved**: `agents/critique.md` untouched (no Critic-agent edit); hash stays at slice-017 ship `f34c967eaaa34413...`.
- [ ] **N-surface schema-pin shape**: methodology-changelog v0.37.0 entry names all 3 surfaces (`tools/_stdout.py`, `tools/utf8_stdout_audit.py`, `main()` invocation pattern) — pinned by prose-pin test.

## Out of scope

- **CRLF / LF line-ending drift**: slice-022 D-4 surfaced this on `skills/build-slice/SKILL.md`; separate `investigate-crlf-lf-drift-on-installed-skills` candidate, do not bundle.
- **Non-tools/ surfaces**: skills, agents, templates — those are pure markdown; not affected by cp1252. This slice scopes strictly to `tools/*.py`.
- **`graphify` (external package)**: shipped editable from `~/.claude/packages/graphify`, not part of `tools/` — out of scope. If `graphify` console output hits cp1252 in future, that's a graphify upstream fix.
- **Test fixture files written with `encoding="utf-8"`**: slice-021 D-3 + tests/methodology/test_branch_workflow_audit.py:111 already cover the file-write side; this slice is the **stdout** side.
- **`$env:PYTHONIOENCODING` removal from any external doc / CI config**: there isn't one currently; if there were, dropping it is a follow-on cleanup.
- **Pipeline-wide branch discipline upstream extension** (slice-022 candidate (d)): structurally separate, LARGE, must split.

## Dependencies

- Prior slices:
  - [[slice-007-codify-cad-1-critic-agent-drift-audit]] — first cp1252 instance; recurrence baseline established
  - [[slice-018-cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw]] — cp1252 N=3 promotion-threshold crossed
  - [[slice-021-add-feature-branch-workflow-at-build-and-commit-slice]] — cp1252 N=5, first instance of `encoding="utf-8"` discipline on file writes (companion side)
  - [[slice-022-redesign-commit-slice-for-pr-aware-flow]] — cp1252 N=6 at TF-1 audit U+2192 arrow; elevated to highest priority
- Vault refs: [[methodology-changelog.md]] (will add v0.37.0 entry), [[decisions/ADR-021]] (new), [[shippability.md]] (row 23 new), [[architecture/build-checks.md]] (UTF8-STDOUT-1 new row if applicable)
- Risk register: no R-N entry — recurrence-class slice, not risk-retiring slice

## Mid-slice smoke gate

At ~50% of build (helper + 2-3 tools wired):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_stdout_helper.py -v
& $PY -m tools.test_first_audit architecture/slices/slice-023-audit-tools-default-utf8-stdout/ 2>&1
# Then with simulated cp1252 stdout (mid-slice smoke):
$env:PYTHONIOENCODING = "cp1252"
& $PY -m tools.test_first_audit architecture/slices/slice-023-audit-tools-default-utf8-stdout/
if ($env:PYTHONIOENCODING) { Remove-Item env:PYTHONIOENCODING }  # m4 ACCEPTED-FIXED — conditional remove
```

Expected: helper tests PASS; test_first_audit emits row table with U+2192 → without crash under PYTHONIOENCODING=cp1252.

If fails: STOP — helper's reconfigure isn't actually engaging, or `errors="replace"` not wired. Diagnose before wiring more tools.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (idempotency / test-capture / errors=replace / JSON integrity / PMI-1 / INST-1 / build-checks / no regression / CAD-1 / N-surface schema-pin)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `tools.test_first_audit --strict-pre-finish` PASS — all 21 TF-1 rows at PASSING (per TPHD-1 sub-mode (c) pre-flight harmonization at /build-slice entry — 3 additional rows added from /critique disposition promises: AC #1 +1 row M6, AC #2 +1 row M4, AC #3 +1 row B5; final count 5×AC1 + 3×AC2 + 6×AC3 + 1×AC4 + 6×AC5 = 21)
- [ ] `tools.branch_workflow_audit` PASS — slice-023 ran on `slice/023-audit-tools-default-utf8-stdout` branch per BRANCH-1 (no `BRANCH=skip` DEVIATION required; this isn't a /repro or bootstrap slice)
- [ ] `tools.utf8_stdout_audit` PASS on its own codebase — recursive-self-application N=1 canonical-reference-instance-at-codification-time per slice-015 / slice-017 / slice-019 / slice-020 precedent
- [ ] `tools.plugin_manifest_audit` PASS — UTF8-STDOUT-1 audit + helper listed
- [ ] `tools.install_audit` PASS — `_CANONICAL_TOOLS` extended
- [ ] CAD-1 byte-equality preserved on `agents/critique.md` (hash check)
- [ ] Full pytest suite ≥497 tests PASS in <60s
