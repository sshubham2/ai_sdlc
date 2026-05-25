# Validation: Slice 038 pin-shippability-runner-segment-contract

**Date**: 2026-05-17
**Result**: PASS

## Per-criterion results

### AC1: Step-5.5 multi-segment runner contract pinned in a single canonical place that /validate-slice Step 5.5 consumes
- **Status**: PASS
- **Evidence**: `tools/shippability_runner.py` is the single canonical executor; `skills/validate-slice/SKILL.md:213-219` invokes `$PY -m tools.shippability_runner architecture/shippability.md` (grep confirmed). Runner REUSES SCMD-1 `_segments` by object identity (`tools.shippability_runner._segments is tools.shippability_decoupling_audit._segments` → `REUSE-VERIFIED`), not re-derived.
- **Notes**: per-`;`-segment backtick+ws strip is single-sourced; CSP-1 reuse pattern matches the precedent (`shippability_decoupling_audit` consumes `shippability_path_audit`).

### AC2: Catalogued regression proves correct per-segment parse on real row #28 AND naive outer-strip demonstrably rejected (load-bearing, not tautological)
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_shippability_runner_segment_contract.py -v` → 4/4 PASS. `test_naive_outer_strip_runner_is_rejected` exercises BOTH branches on the REAL row #28: `_naive_outer_strip(cell)[1].startswith("\`")` is True (R-8 bug reproduced) AND `runner._segments(cell)[1].startswith("\`")` is False (canonical correct) — the green is a contract-boundary proof, not a tautology over the already-correct helper.
- **Notes**: SRSC-1 dogfood (below) is the runtime complement — the runner actually executes row #28's two segments with no WinError 2.

### AC3: skills/validate-slice/SKILL.md Step 5.5 prose explicitly pins the runner-segment contract (canonical mechanism)
- **Status**: PASS
- **Evidence**: `skills/validate-slice/SKILL.md:213` carries `do NOT hand-roll the execution loop` + `reuses SCMD-1 _segments()` + SRSC-1 + ADR-039 (grep confirmed). `test_validate_slice_skill_pins_runner_invocation` asserts all canonical-mechanism strings present in BOTH in-repo AND installed copies (content pin, not change-detection) → PASS.

### AC4: methodology-changelog.md (in-repo + installed) new RULE-ID + ADR + PMI-1/INST-1/RPCD-1/SCPD-1 atomic + shippability row
- **Status**: PASS
- **Evidence**: `test_v_0_51_0_srsc_1_entry_present_in_repo_and_installed` (content pin: SRSC-1 + `do NOT hand-roll the execution loop` + `reuses SCMD-1 _segments()` + ADR-039 + "supersedes nothing", in-repo AND installed) + `test_v_0_51_0_srsc_1_shippability_consumer_propagation` (SCPD-1: SRSC-1 + `test_shippability_runner_segment_contract.py` in catalog) + `test_shippability_runner_survives_cp1252_with_u2192` → 3/3 PASS. PMI-1 clean (25 skills, 5 agents, **23 tools**, version **0.51.0**). INST-1 clean (23/23 tool modules, methodology **v0.51.0**). 4-part PMI-1 bump verified (VERSION + ~/.claude/ai-sdlc-VERSION + plugin.yaml:15 + forward-synced installed changelog all 0.51.0). Runner enumerated on BOTH surfaces (install_audit `_CANONICAL_TOOLS` + plugin.yaml). Shippability row #38 present.

### AC5: R-8 retired in risk-register.md citing slice-038 + ADR; catalogued regression makes false-FAIL class non-silently-recurrable
- **Status**: PASS
- **Evidence**: `risk_register_audit --json --filter-status open` → open risks `['R-2','R-6']`; **R-8 absent (retired)**. `architecture/risk-register.md` R-8 `Status: retired` + slice-038 + [[ADR-039]] + RULE-ID SRSC-1 cite. `ADR-039-srsc-1-pinned-shippability-runner.md` exists. Non-recurrable: the load-bearing `test_naive_outer_strip_runner_is_rejected` + catalogued shippability row #38 fail loudly if the contract regresses.

## Step 5b — VAL-1 layered safety checks
**Result**: PASS — `VAL-1: 0 secret(s), 0 import finding(s), 0 suppressed.` Both layers clean (changed files: `tools/shippability_runner.py`, `tools/install_audit.py`, 3 test modules; `--imports-allowlist tests`).

## Step 5.5 — Shippability catalog regression check
**Pre-catalog gates**:
- SCMD-1: clean — `38 row(s); 398 cited fn(s) — incidental=0 essential=35 clean=363` (new row #38 incidental=0)
- PTFCD-1/PTFFD-1: clean — `38 row(s), 244 test-path token(s) — all files and cited functions exist` (row #38's `::`-selectors all resolve)

**Catalog run (via the canonical `tools.shippability_runner` — the SRSC-1 dogfood; Step 5.5 now invokes the very tool this slice shipped)**:
```
Shippability catalog run: 38 row(s), 38 PASS, 0 FAIL
```
**Result**: PASS — 38/38, zero regressions. Row #28 (the lone multi-segment row, the R-8 target) PASS with no WinError 2; new row #38 (recursion: the runner runs its own contract test as a catalog row) PASS.

## Multi-instance validation
**Required?**: no — local developer CLI tool; no multi-user / multi-device / sync / sharing surface.
**Result**: not-applicable

## Reality surprises
- None. One build-time mechanism deviation (B1's `_POSITIONAL_SLICE_TOOLS` instruction corrected to the catalog-path-tool sibling-precedent bespoke cp1252 test — `_POSITIONAL_SLICE_TOOLS` passes a slice-folder arg a catalog-path tool can't consume). B1 intent (`discovered==covered` parity; runner ∈ covered_set) fully preserved and verified (utf8_stdout_audit 23/23, parity test green). Well-precedented (path_audit/decoupling_audit do exactly this), conformance-strengthening, recorded in build-log.md for /reflect — not a reality surprise affecting the next slice.
