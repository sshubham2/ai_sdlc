# Validation: Slice 080 harden-bc1-critical-rules-exit-gate

**Date**: 2026-05-29
**Result**: PASS

## Per-criterion results

### AC1: `--strict` + applicable unacknowledged Critical rule → exit 1
- **Status**: PASS
- **Evidence**: `build_checks_audit --slice <slice-080> --changed-files tools/build_checks_audit.py --strict` → **exit 1** (BC-PROJ-3 + BC-GLOBAL-2 applicable, unacked → 2 `unacknowledged-critical` violations). Repro `test_strict_exits_nonzero_on_applicable_critical_rule` PASS.
- **Notes**: real CLI invocation against the live `architecture/build-checks.md` + `~/.claude/build-checks.md`.

### AC2: `--strict` + no applicable Critical rule → exit 0 (no false-fire)
- **Status**: PASS
- **Evidence**: `test_strict_exits_zero_when_no_critical_applicable` PASS (clean fixtures, `--strict`, exit 0). Unit `test_strict_no_applicable_critical_no_violation` PASS.

### AC3: default (no `--strict`) exit behavior unchanged
- **Status**: PASS
- **Evidence**: `build_checks_audit --slice <slice-080> --changed-files tools/build_checks_audit.py` (no `--strict`) → **exit 0** despite `critical_applicable: 2` (applicable Critical rules informational on the default path). All 47 pre-existing BC-1 tests PASS; `test_default_path_critical_informational_no_violation` + `test_format_human_default_path_has_no_strict_diagnostic` PASS.

### AC4: `/build-slice` Step 6 wires `--strict` + OSDG-1 forward-synced
- **Status**: PASS
- **Evidence**: `skills/build-slice/SKILL.md` Step 6 contains the `--strict --ack-critical <ids>` invocation + enumerate-then-ack pattern + mechanical refusal semantics. `test_build_slice_skill_drift.py` PASS (in-repo ≡ installed `~/.claude/skills/build-slice/SKILL.md` modulo EOL).

### AC5: failing repro `tests/bugs/test_bc1_critical_rule_exit_gate.py` PASSES at slice end
- **Status**: PASS
- **Evidence**: 2/2 PASS (FAILed pre-fix with `unrecognized arguments: --strict` exit 2).

## Multi-instance validation
**Required?**: no (local CLI audit tool; no multi-user/device/account surface).
**Result**: not-applicable

## VAL-1 layered safety checks
- **Layer A (credential scan)**: PASS — 0 secrets in changed files.
- **Layer B (dependency hallucination)**: PASS — 0 import findings (`--imports-allowlist tests`).

## Shippability catalog regression (Step 5.5)
- **SCMD-1 decoupling pre-gate**: exit 0
- **PTFCD-1 path pre-gate**: exit 0
- **Catalog runner** (`tools.shippability_runner`): **84 rows, 84 PASS, 0 FAIL** — no regression. Includes the renamed row #75 command (`test_version_files_synchronized_at_v_0_75_0`, B2 propagation) and the new row #85 (BCSG-1 repro).

## Reality surprises
None. The acknowledgment-flag design behaved exactly as specified; the code-Critic's M1 (output-mislabel) was caught + fixed in-band before validation. BC-PROJ-3 + BC-GLOBAL-2 being `always:true` Critical rules (the standing-ack consequence) was anticipated at /critique B3 and is working as designed (every slice now acknowledges them at Step 6).
