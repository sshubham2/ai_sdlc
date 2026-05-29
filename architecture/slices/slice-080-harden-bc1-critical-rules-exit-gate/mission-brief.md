# Slice 080: harden-bc1-critical-rules-exit-gate

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: `diagnose-out/backlog.md` SC-008 (finding F-HALF-9b2e44d1) — BC-1 enforcement-correctness gap. No registered R-NN (the defect is a documented v1 limitation, not a tracked risk).
**Test-first**: false  (BFRD-1 repro prelude already established — see Dependencies)
**Walking-skeleton**: false
**Exploratory-charter**: false

**Closes:** SC-008

## Intent

The BC-1 build-checks audit prints "Per BC-1, Critical rules MUST be addressed before /build-slice declares the slice done" and `/build-slice` SKILL.md states "Critical rules are not deferrable" — but `tools/build_checks_audit.py:619` ends in `return 1 if result.violations else 0`, where `result.violations` holds only parse errors (malformed build-checks.md), never the applicable Critical rules themselves. An applicable non-deferrable Critical rule therefore produces **exit 0**: a tooling consumer that treats the exit code as the BC-1 gate signal silently passes a slice that violates a Critical rule. This slice makes the exit code honestly reflect unaddressed Critical applicability via an opt-in `--strict` flag (mirroring `test_first_audit` / `walking_skeleton_audit`'s `--strict-pre-finish`), wired into `/build-slice` Step 6 so the project's own load-bearing gate stops being honor-system-only.

**Central design question (for `/design-slice` + `/critique`, NOT pre-decided here):** `critical_applicable` counts Critical rules that *apply* (via glob / keyword / `always`), not rules that are *unaddressed* — applicability does not disappear when the builder satisfies the rule (v1 has no "addressed" signal; that auto-verification is the self-acknowledged v2 gap). So a naive `--strict → nonzero whenever critical_applicable > 0` would make every slice touching an always-on Critical rule un-passable. `/design-slice` must decide how a slice legitimately clears the gate after addressing its Critical rules (e.g., an explicit acknowledgment flag, a builder sign-off recorded in validation.md, or Step-6 surfacing-for-confirmation rather than hard-halt). The repro test deliberately exercises the *unacknowledged* case (applicable Critical + no sign-off → nonzero), so it stays valid under any acknowledgment design.

## Acceptance criteria

1. `tools/build_checks_audit.main()` accepts a `--strict` flag; under `--strict`, an invocation whose audit yields an applicable Critical-severity rule (`summary.critical_applicable > 0`) and no clearing acknowledgment returns gate-failure **exit 1** (consistent with the existing parse-violation exit code).
2. Under `--strict`, an invocation with no applicable Critical rule and no parse violations returns **exit 0** (no false-fire).
3. Default (no `--strict`) exit behavior is unchanged: the gate is opt-in; a bare invocation still returns `1 if result.violations else 0`, and applicable Critical rules remain informational on that path (backward-compatible with all current callers).
4. `/build-slice` Step 6 pre-finish invokes `build_checks_audit` with `--strict` (the gate is wired in, not merely available), with the in-repo `skills/build-slice/SKILL.md` edit OSDG-1 lock-step forward-synced to the installed `~/.claude/skills/build-slice/SKILL.md`.
5. The failing repro `tests/bugs/test_bc1_critical_rule_exit_gate.py` PASSES at slice end.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `--strict` exit 1 on applicable Critical | `pytest tests/bugs/test_bc1_critical_rule_exit_gate.py::test_strict_exits_nonzero_on_applicable_critical_rule` PASSES (currently FAILs: argparse rejects `--strict`, exit 2) |
| 2 | `--strict` no false-fire | `pytest tests/bugs/test_bc1_critical_rule_exit_gate.py::test_strict_exits_zero_when_no_critical_applicable` PASSES |
| 3 | Default behavior unchanged | Full existing `tests/methodology/test_build_checks_audit.py` suite stays green; a bare-mode test asserts an applicable Critical rule still exits 0 without `--strict` |
| 4 | Step 6 wired + synced | Prose-pin test asserts `skills/build-slice/SKILL.md` Step 6 invokes `build_checks_audit ... --strict`; mini-CAD / OSDG-1 drift test (`test_build_slice_skill_drift`) stays green |
| 5 | Repro passes | `$PY -m pytest tests/bugs/test_bc1_critical_rule_exit_gate.py --no-header -q` → 2 passed |

## Must-not-defer

- [ ] Existing parse-violation semantics preserved: bare and `--strict` invocations both still return nonzero on parse violations (malformed build-checks.md).
- [ ] Combined case defined: under `--strict`, violations AND `critical_applicable > 0` together must still be nonzero (no masking either signal).
- [ ] Output unchanged: human-readable + `--json` output still emitted on all paths; `--strict` changes only the exit code, never suppresses the surfaced-rules report.
- [ ] OSDG-1 / mini-CAD: any `skills/build-slice/SKILL.md` edit forward-synced to the installed copy byte-equal modulo EOL (CAD-1 / EOL-DRIFT-1).
- [ ] PMI-1 / INST-1: no new tool module is added (modifying existing `build_checks_audit.py`), so confirm no inventory bump is required and both audits stay clean.

## Out of scope

- The broader SC-006 / SC-007 / SC-009 enforcement-gap cluster (drift-check has no backing tool, etc.) — separate slices.
- Structural refactor of `build_checks_audit.run_audit` / module decomposition (SC-003 class).
- v2 auto-verification of *whether* a Critical rule's required check was actually performed (semantic content analysis of the slice's tests/diff) — this slice gates on applicability + acknowledgment only, not on proving the rule was satisfied.
- Changing which rules are Critical or the BC-1 rule corpus itself.

## Dependencies

- Failing repro (BFRD-1 prelude, established this session): `tests/bugs/test_bc1_critical_rule_exit_gate.py::test_strict_exits_nonzero_on_applicable_critical_rule` + `::test_strict_exits_zero_when_no_critical_applicable` — both FAIL on master (argparse rejects `--strict`), catalogued as shippability row #85.
- Code under change: `tools/build_checks_audit.py` (`main()` exit logic + new `--strict` arg), `skills/build-slice/SKILL.md` (Step 6 invocation) + installed copy.
- Pattern references: `tools/test_first_audit.py` / `tools/walking_skeleton_audit.py` `--strict-pre-finish` exit-gate idiom (the convention `--strict` mirrors).
- Vault refs: [[diagnose-out/backlog.md#SC-008]]; BC-1 (`methodology-changelog.md` v0.10.0); shippability row #85.

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m pytest tests/bugs/test_bc1_critical_rule_exit_gate.py --no-header -q
```
Expected: both tests PASS once `--strict` is implemented (before SKILL.md wiring). If still failing with `unrecognized arguments: --strict` after the audit code change: STOP, the flag wasn't registered. Also run `$PY -m pytest tests/methodology/test_build_checks_audit.py --no-header -q` to confirm no default-path regression.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] BC-1 self-dogfood: run `$PY -m tools.build_checks_audit --slice <this-slice> --strict` on slice-080's own folder and read the output (BC-PROJ-4 real-artifact discipline)
- [ ] No new TODOs / FIXMEs / debug prints
