# Validation: Slice 098 route-or-retire-git-coupled-vault-tools

**Date**: 2026-06-02
**Result**: PASS

This is local developer tooling (no deployment target) — "real environment" = executing the tools against real git/vault state + the full test suite (1450 PASS) + the external-root subprocess probe (real `AI_SDLC_VAULT_ROOT` injection at a process boundary). Per-criterion evidence below.

## Per-criterion results

### AC1: Class-A vault-path routing (no `architecture/<vault-content>` literal in a Path.__truediv__ position; verified by a precisely-predicated AST scan, mutation-proven non-vacuous)
- **Status**: PASS
- **Evidence**: `test_slice_098_vault_routing.py::test_no_unrouted_vault_literal_in_class_a_position[parallel_conflict_resolver|stranded_slice_audit|pulse_worktree_resolver]` — all 3 PASS (scanner finds zero Class-A `architecture` literals). Non-vacuity: `test_scanner_non_vacuous_direct` + `test_scanner_non_vacuous_variable_mediated` (M-add-3 one-hop) both confirm the scanner FLAGS a re-introduced un-routed literal. Class-B git-string identities (21 in PCR) carry the slice-068 `# NOT VAULT_ROOT-routed` marker; orphan-literal audit (`test_vault_root_constant.py::test_no_orphan_architecture_literal_in_migrated_tools`) PASS.
- **Notes**: AC1 guarantee is honestly bounded (per /code-review M1) to the `Path / 'architecture'` div-form + one-hop alias; `joinpath`/`os.path.join`/2-hop are a named residual (none present in the 3 tools — Grep-verified).

### AC2: Git-coupling classified ROUTE/RETIRE/KEEP + binding RETIRE signal enforced by a test
- **Status**: PASS
- **Evidence**: design.md per-site table + ADR-089 classify every site. Binding signal `vault_is_external` enforced: `test_vault_is_external_signal_logic` (default/abs-under-repo/relative/abs-outside) PASS; PCR `_retire_if_vault_external` STOP + stranded INDETERMINATE both pinned by `test_external_root_flip_readiness_and_retire`. `_MIGRATION_SITE_ALLOWLIST` 11→14 (the 3 tools migrated); `test_all_tools_modules_import_vault_root` PASS.

### AC3: External-root flip-readiness (subprocess env-injection — Class-A located there, Class-B RETIRE visibly)
- **Status**: PASS
- **Evidence**: `test_external_root_flip_readiness_and_retire` spawns a fresh `python` subprocess with `AI_SDLC_VAULT_ROOT=<tmp external dir>` and asserts: `VAULT_ROOT == ext`; pulse `_resolve_milestone_path` resolves the milestone UNDER the external root; `vault_is_external(repo)` is True; PCR `_retire_if_vault_external(repo)` returns STOP with "external" in the reason. Probe prints `EXTERNAL_PROBE_OK`, returncode 0. (Subprocess boundary required — the consumer-freeze cascade means in-process monkeypatch does NOT propagate to frozen VAULT_ROOT.)

### AC4: No-flip safety contract (env unset → full suite unchanged, tools byte-identical, incl. `_AUDIT_LOG_PATH`)
- **Status**: PASS
- **Evidence**: full suite **1450 PASS / 0 FAIL** with `AI_SDLC_VAULT_ROOT` unset (default `architecture/`). `test_audit_log_path_no_flip_byte_identity` confirms `repo_root / _AUDIT_LOG_PATH == repo_root / "architecture" / "parallel-conflict-resolution-log.md"`. Mid-slice smoke captured pulse byte-identity on the live repo. The 2 changed pin-files transitioned (11→14) are expected state-transitions, not regressions.

### AC5: No silent misbehavior on RETIRE (fail VISIBLY before composing any out_path/relative_to)
- **Status**: PASS
- **Evidence**: PCR — `_retire_if_vault_external` is the FIRST statement after the `repo_root` default in both `resolve_soft_conflict` + `resolve_vault_claim_conflict` (code-Critic confirmed: strictly before classify/out_path/relative_to). stranded — `vault_is_external` guard returns `DivergenceClass.INDETERMINATE` (a `_HALT_CLASSES` member) with a visible reason, never a silent `False`/ORPHANED. M-add-1 — diagnose-time reads protected by U-file-absence→UNKNOWN, pinned non-vacuously by `test_diagnose_time_git_show_stage_not_called_without_vault_ufile` (call-spy on a live `diagnose_conflict`).

## VAL-1 layered safety checks (Step 5b)
- **Layer A (credential scan)**: 0 secrets. PASS.
- **Layer B (dependency hallucination)**: 0 import findings (`--imports-allowlist tests`). PASS.

## Walking-skeleton (WS-1) / Exploratory-charter (ETC-1)
- Not applicable — mission-brief `Walking-skeleton: false`, `Exploratory-charter: false`.

## Multi-instance validation
- **Required?**: no (local single-process dev tooling; no multi-user/device/account surface).
- **Result**: not-applicable.

## Shippability catalog regression check (Step 5.5)
- Pre-gates: SCMD-1 exit 0, PTFCD-1 exit 0, SVW-1 exit 0.
- Runner: **104 rows, 104 PASS, 0 FAIL**. No past slice regressed.

## Reality surprises
- None at validation. (The two build-time design-vs-reality refinements — the per-pathspec tracked-check being unsound for both tools → unified `vault_is_external` — were surfaced and user-ratified DURING build, documented in build-log/ADR-089/design.md, not at validation.)

## Note for /reflect
- Consider adding a shippability catalog row for the no-flip + RETIRE safety property (e.g. `test_slice_098_vault_routing.py::test_external_root_flip_readiness_and_retire` + the AST-scan), so a future slice cannot silently break the R-32-mitigation routing/RETIRE contract. (Catalog edits are /reflect Step 5b's job.)
- R-32 stays `mitigating` (advances toward retirement-at-flip; the actual flip is slice-099+). The flip slice consumes `vault_pathspec_is_tracked` (m1) or retires it.
