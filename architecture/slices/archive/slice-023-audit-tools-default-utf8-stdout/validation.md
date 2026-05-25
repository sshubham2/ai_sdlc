# Validation: Slice 023 audit-tools-default-utf8-stdout

**Date**: 2026-05-15
**Result**: PASS

## Per-criterion results

### AC1: A shared helper `tools/_stdout.py` exposes `reconfigure_stdout_utf8()` with idempotency + duck-typing + errors="replace"

- **Status**: PASS
- **Evidence**:
  ```
  $ $PY -m pytest tests/methodology/test_stdout_helper.py -v --no-header

  tests/methodology/test_stdout_helper.py::test_reconfigure_called_on_real_streams_with_reconfigure PASSED [ 20%]
  tests/methodology/test_stdout_helper.py::test_reconfigure_noop_on_streams_without_reconfigure_attribute PASSED [ 40%]
  tests/methodology/test_stdout_helper.py::test_reconfigure_idempotent_under_repeat_invocation PASSED [ 60%]
  tests/methodology/test_stdout_helper.py::test_reconfigure_sets_errors_replace_not_strict PASSED [ 80%]
  tests/methodology/test_stdout_helper.py::test_reconfigure_overrides_prior_errors_strict_to_errors_replace PASSED [100%]

  5 passed in 0.08s
  ```
  All 5 unit tests pass, covering the AC sub-clauses (a) real-stream reconfigure / (b) duck-typed no-op / (c) idempotency / (d) errors="replace" not "strict" / and the M6 ACCEPTED-FIXED extension (e) overrides prior errors="strict" state.
- **Notes**: Helper is ~25 LOC at `tools/_stdout.py`; docstring inline-cites the slice-023 design rationale. Test scope chosen to lock the public contract — additional internal-state tests not needed (the function is intentionally minimal).

### AC2: Every `tools/*.py` module with `main()` calls `_stdout.reconfigure_stdout_utf8()` as first executable statement; verified by structural audit

- **Status**: PASS
- **Evidence**:
  ```
  $ $PY -m tools.utf8_stdout_audit
  UTF8-STDOUT-1 audit: clean. 17 tool(s) scanned; 17 with main(); 17 clean.

  $ $PY -m tools.utf8_stdout_audit --json
  {
    "tools_scanned": 17,
    "tools_with_main": 17,
    "tools_clean": 17,
    "violations": [],
    "status": "clean"
  }
  ```
  17/17/17 matches the canonical contract pinned at design.md "Output contract invariant" + mission-brief AC #2 verification cell. Self-application N=1 confirmed: `tools/utf8_stdout_audit.py` itself conforms; the audit is not exempt from its own rule.
- **Notes**: Exit code 0 on clean run; JSON output shape matches the regression-guard prose-pin (tools_scanned == tools_with_main + helper_count; tools_clean == tools_with_main - len(violations); status == "clean" iff len(violations) == 0). All three invariants enforced by `test_output_contract_invariant`.

### AC3: New audit `tools/utf8_stdout_audit.py` emits one violation per module where first executable statement is not the canonical call; exit code 1 on violation; `--json` flag works

- **Status**: PASS
- **Evidence**:
  ```
  $ $PY -m pytest tests/methodology/test_utf8_stdout_audit.py -v --no-header

  test_every_tool_with_main_calls_reconfigure_first PASSED          [self-application against real repo]
  test_stdout_helper_module_itself_exempt PASSED                    [helper excluded from scan]
  test_every_tool_uses_canonical_from_tools_import_stdout PASSED    [M4 canonical import form pin]
  test_audit_flags_tool_missing_reconfigure_call PASSED             [synthetic non-conforming tool → violation]
  test_audit_flags_tool_with_reconfigure_after_argparse PASSED      [delayed-reconfigure → violation]
  test_audit_clean_on_canonical_pattern PASSED                      [synthetic conforming tool → clean]
  test_audit_json_output_shape PASSED                               [JSON keys match canonical shape]
  test_audit_exit_code_zero_on_clean_one_on_violation PASSED        [exit 0 / 1 semantics]
  test_output_contract_invariant PASSED                             [B5 regression-guard invariant]

  9 passed in 0.44s
  ```
- **Notes**: The audit is AST-based (not regex) per design.md L102-109. It excludes `__init__.py` + leading-underscore helpers; accepts both `_stdout.reconfigure_stdout_utf8()` and `reconfigure_stdout_utf8()` (from-import variant). Self-exemption clause holds: `utf8_stdout_audit.py` itself must conform AND does.

### AC4: Behavioural regression test invokes each audit tool's `main()` under simulated `cp1252` encoding with U+2192 input; every audit completes without `UnicodeEncodeError` / `UnicodeDecodeError`

- **Status**: PASS
- **Evidence**:
  ```
  $ $PY -m pytest tests/methodology/test_utf8_stdout_regression.py -v --no-header

  test_positional_slice_tool_survives_cp1252_with_u2192[tools.branch_workflow_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.test_first_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.wiring_matrix_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.walking_skeleton_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.exploratory_charter_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.build_checks_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.triage_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.cross_spec_parity_audit] PASSED
  test_positional_slice_tool_survives_cp1252_with_u2192[tools.supersede_audit] PASSED
  test_root_only_tool_survives_cp1252_with_u2192[tools.plugin_manifest_audit] PASSED
  test_root_only_tool_survives_cp1252_with_u2192[tools.utf8_stdout_audit] PASSED
  test_install_audit_survives_cp1252_with_u2192 PASSED
  test_mock_budget_lint_survives_cp1252_with_u2192 PASSED
  test_validate_slice_layers_survives_cp1252_with_u2192 PASSED
  test_risk_register_audit_survives_cp1252_with_u2192 PASSED
  test_critique_agent_drift_audit_survives_cp1252_with_u2192 PASSED
  test_critique_review_audit_survives_cp1252_with_u2192 PASSED
  test_every_audit_tool_survives_cp1252_stdout_with_u2192_input PASSED

  18 passed in 2.54s
  ```
- **Notes**: All 17 audit tools survive the simulated Windows cp1252 environment with U+2192 fixture content. Per M1 + M-add-2 ACCEPTED-FIXED, the per-tool argv strategy reflects each tool's verified argparse contract (positional-slice-folder for 9 / `--root` for 2 / `--claude-dir` for install_audit / positional-files for mock_budget_lint / `--slice` for validate_slice_layers / positional risk-register.md for risk_register_audit / `--repo-root` for critique audits). Failure assertion targets `"UnicodeEncodeError" not in stderr and "UnicodeDecodeError" not in stderr`, NOT exit-code-0 — the slice-022 D-5 crash class is precisely this exception type. Roll-up `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` confirms 17 tools exist post-slice.

### AC5: methodology-changelog v0.37.0 entry codifies UTF8-STDOUT-1 with N-surface schema-pin; ADR-021 accepted; shippability row 23 added pointing at new audit + regression test

- **Status**: PASS
- **Evidence**:
  ```
  $ $PY -m tools.plugin_manifest_audit
  PMI-1 plugin manifest audit: clean. 24 skill(s), 5 agent(s), 17 tool(s); version 0.37.0.

  $ $PY -m tools.install_audit
  INST-1 install audit: clean. 24/24 skills, 5/5 agents, 4/4 templates, 17/17 tool modules; methodology v0.37.0.

  $ $PY -m pytest \
      tests/methodology/test_methodology_changelog.py::test_v_0_37_0_utf8_stdout_1_entry_present_in_repo_and_installed \
      tests/methodology/test_methodology_changelog.py::test_v_0_37_0_utf8_stdout_1_entry_names_all_three_surfaces \
      tests/methodology/test_methodology_changelog.py::test_v_0_37_0_utf8_stdout_1_entry_pins_canonical_invocation_pattern \
      tests/methodology/test_methodology_changelog.py::test_adr_021_present_and_reversibility_cheap \
      tests/methodology/test_install_audit.py::test_install_audit_enumerates_utf8_stdout_audit \
      tests/methodology/test_plugin_manifest_audit.py::test_plugin_yaml_lists_utf8_stdout_audit \
      tests/methodology/test_plugin_manifest_audit.py::test_list_actual_tools_filters_leading_underscore_helpers \
      --no-header -q

  7 passed in 0.09s
  ```
  ADR-021 frontmatter:
  ```yaml
  ---
  id: ADR-021
  title: UTF8-STDOUT-1 — every tools/*.py with a main() reconfigures sys.stdout / sys.stderr to UTF-8 via a shared helper as the first executable statement
  date: 2026-05-15
  slice: slice-023-audit-tools-default-utf8-stdout
  reversibility: cheap
  status: accepted
  supersedes: null
  ---
  ```
- **Notes**: 7/7 methodology-surface tests pass: 3 v0.37.0 entry-pin tests (presence + 3-surface enumeration + canonical-invocation-pattern pin) + 1 ADR-pin test + 1 INST-1 enumeration test + 2 PMI-1 tests (plugin.yaml list + leading-underscore filter). Bidirectional sha256 byte-equality on methodology-changelog.md in-repo ↔ installed: confirmed (slice-022 v0.36.0 + new v0.37.0 entry both present in both surfaces). PMI-1 manifest version 0.37.0 matches VERSION 0.37.0 (PMI-1 v1.1 retirement-proof N=8 → N=9 stable; ninth atomic version bump with zero gate-body modification).

## VAL-1 layered safety checks (Step 5b)

```
$ $PY -m tools.validate_slice_layers \
    --slice architecture/slices/slice-023-audit-tools-default-utf8-stdout \
    --changed-files <18 .py files + 3 test files> \
    --imports-allowlist tests

VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).
Clean — both layers passed.
```

- **Layer A (Critical, blocks)**: 0 secrets detected across 21 changed files. No AWS keys, GitHub PATs, JWTs, PEM, API keys, or generic `api_key=` literals.
- **Layer B (Important, surfaces)**: 0 hallucinated imports. Every Python import in the changed files resolves cleanly against `pyproject.toml` / `requirements.txt` / stdlib / `tests` namespace package allowlist.

## Walking-skeleton audit (WS-1)

Skipped: `**Walking-skeleton**: false` in mission-brief.md (slice is a methodology codification, not a walking-skeleton vertical).

## Exploratory-charter audit (ETC-1)

Skipped: `**Exploratory-charter**: false` in mission-brief.md.

## Shippability catalog regression (Step 5.5)

```
Running 23 shippability rows...
  Row 1: PASS (1.98s)
  Row 2: PASS (0.41s)
  Row 3: PASS (0.43s)
  Row 4: PASS (0.39s)
  Row 5: PASS (0.45s)
  Row 6: PASS (0.42s)
  Row 7: PASS (1.34s)
  Row 8: PASS (0.53s)
  Row 9: PASS (0.53s)
  Row 10: PASS (0.42s)
  Row 11: PASS (0.52s)
  Row 12: PASS (0.50s)
  Row 13: PASS (0.58s)
  Row 14: PASS (0.45s)
  Row 15: PASS (0.55s)
  Row 16: PASS (0.56s)
  Row 17: PASS (0.42s)
  Row 18: PASS (0.53s)
  Row 19: PASS (0.43s)
  Row 20: PASS (0.43s)
  Row 21: PASS (4.94s)
  Row 22: PASS (0.62s)
  Row 23: PASS (3.25s)
Total: 23 rows in 20.67s (0 FAIL)
All shippability rows PASS.
```

23/23 PASS in 20.67s — well under 2-minute target. No past slice silently broken by slice-023. Row 23 (slice-023's own critical path) runs in 3.25s and is the dominant row — within target.

Note on row 1 runtime (1.98s — highest non-self row): runs the `/diagnose` orchestration test suite under `tests/skills/diagnose/`; unaffected by slice-023 changes. Row 7 runtime (1.34s) runs `test_critique_agent_drift.py` + canonical-tools-match-plugin-yaml; the latter now reflects v0.37.0 + the new `utf8_stdout_audit` entry — still PASS.

## Multi-instance validation

**Required?**: no — slice changes are local-only tooling (no user-facing surface, no API, no auth, no sync). The `_stdout.reconfigure_stdout_utf8()` helper mutates process-local stdout state only.
**Result**: not-applicable
**Evidence**: design.md "Authorization model for this slice" + "Limitations" sections explicitly scope to single-process tooling.

## Reality surprises

**Empirical recursive-self-application closure observed at /build-slice + /validate-slice**:

The TF-1 audit output emitted `Test-first audit: clean. 18 row(s) � PASSING=...` (mojibake `�` for em-dash) BEFORE Phase 3 wiring during /build-slice plan-mode entry — exactly the slice-022 D-5 crash class. AFTER Phase 3 wiring, the same audit invocation under `PYTHONIOENCODING=cp1252` emits `Test-first audit: clean. 21 row(s) — PASSING=21, WRITTEN-FAILING=0, PENDING=0.` (em-dash rendered correctly). The cp1252 class was hit LIVE during the very build that codified UTF8-STDOUT-1, then retired in real-time as Phase 3 wired the 16 audit tools.

This isn't a "surprise" in the sense of an unanticipated bug — it's empirical evidence that the slice's value proposition holds. The class wasn't theoretical; it was actively recurring at /build-slice's own pre-flight audits, and the slice's own Phase 3 retired it. Captured here so future slices have the witness anchor.

**No reality surprises that affect risk-register or future slices.**

## Decision

All 5 ACs PASS with evidence. VAL-1 clean. Shippability catalog 23/23 PASS. No multi-instance applicability. No reality surprises requiring follow-up.

**Next action**: run `/reflect` to capture lessons learned and update the vault.
