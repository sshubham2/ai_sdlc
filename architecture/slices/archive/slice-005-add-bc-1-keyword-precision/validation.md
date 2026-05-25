# Validation: Slice 005 add-bc-1-keyword-precision

**Date**: 2026-05-10
**Result**: PASS

## Per-criterion results

### AC #1: Slice-003 backtest clean — `0 applications` of BC-PROJ-2 + BC-GLOBAL-1

- **Status**: PASS
- **Evidence**:

```
$PY -m tools.build_checks_audit \
  --slice architecture/slices/archive/slice-003-add-val-1-imports-allowlist \
  --project-checks architecture/build-checks.md \
  --no-carry-over --json
```

Output (parsed):
```
applicable: []
skipped: ['BC-GLOBAL-1', 'BC-PROJ-1', 'BC-PROJ-2']
```

All 3 rules appear in `skipped` (all parsed correctly; none fired). Slice-003's bare-substring `parse` matches in `parse_declared_deps` / `tomllib`-parses / `ast`-parses contexts — once a false-positive class — are silenced. The `BC-PROJ-2 in skipped` half-assertion confirms the failure-mode-distinction discipline (slice-003 lesson on TF-1 PENDING → WRITTEN-FAILING genuineness): the rule was parsed and considered, but didn't apply because anchors `fence/code-block/llm` don't match slice-003's text.

- **Notes**: Real CLI invocation with explicit `--project-checks` (workaround for the pre-existing `audit_slice` heuristic bug discovered at /build-slice T4 — the heuristic resolves to `architecture/slices/build-checks.md` for archived slice paths). The bug is logged for slice-006+ candidate (`fix-bc-1-archived-slice-heuristic`); not in scope for this slice.

### AC #2: Slice-004 backtest clean — `0 applications` of BC-PROJ-2 + BC-GLOBAL-1

- **Status**: PASS
- **Evidence**:

```
$PY -m tools.build_checks_audit \
  --slice architecture/slices/archive/slice-004-fix-rr1-audit-docstring-or-regex \
  --project-checks architecture/build-checks.md \
  --no-carry-over --json
```

Output (parsed):
```
applicable: []
skipped: ['BC-GLOBAL-1', 'BC-PROJ-1', 'BC-PROJ-2']
```

Slice-004's bare-word `parse`, `backtick`, `output` matches in regex/markdown/CLI contexts — the second false-positive instance — are silenced. Word-boundary alone was insufficient (verified at /build-slice T4 mid-slice smoke: parse=1, backtick=6, output=1 all word-boundary-match in slice-004's design.md); the anchor filter (`fence/code-block/llm` — none match) is what closes the gap. Confirms the design.md empirical-verification table prediction.

- **Notes**: Same workaround for the heuristic bug as AC #1.

### AC #3: Positive case preserved — synthetic LLM-fence brief still triggers BC-PROJ-2 + BC-GLOBAL-1

- **Status**: PASS
- **Evidence**:

Synthetic mission-brief.md text (per Critic B2 — the canonical sentence locked at /critique triage):

> Parse the LLM agent's fenced output for nested triple-backtick code-block sections.

```
$PY -m tools.build_checks_audit --slice <tmp> --project-checks architecture/build-checks.md \
  --no-carry-over --json
```

Output (parsed):
```
applicable: ['BC-GLOBAL-1', 'BC-PROJ-2']
```

Both rules fire. Word-boundary anchor matches: `\bllm\b` (1 hit on "LLM") + `\bcode-block\b` (1 hit on "code-block"). The `fence` anchor does NOT match `fenced` (per Critic B2 documentation; the deferred-work caveat about morphological variants is real and acknowledged) — but `llm` and `code-block` are sufficient.

- **Notes**: Confirms the precision mechanism doesn't over-suppress legitimate matches. The double-anchor design (multiple anchor words per rule) provides redundancy for English morphological variants — a slice can use any of {fence, code-block, llm, structured-output} for BC-GLOBAL-1 to fire.

### AC #4: Schema-pin (TWO surfaces) in BOTH project + global build-checks files

- **Status**: PASS
- **Evidence**:

| File | `Trigger anchors` substring present | `word-boundary` substring present |
|------|--------------------------------------|------------------------------------|
| `architecture/build-checks.md` | ✓ | ✓ |
| `~/.claude/build-checks.md` | ✓ | ✓ |

Verified two ways:
1. PowerShell `Get-Content -Raw | .Contains("...")` against both files — all 4 cells return True.
2. pytest `test_build_checks_schema_documents_trigger_anchors_field_name` + `test_build_checks_schema_documents_word_boundary_semantics` — both pass; both files exercised (no skip-marker fired because global file IS present in this environment).

```
tests/methodology/test_build_checks_audit.py::test_build_checks_schema_documents_trigger_anchors_field_name PASSED
tests/methodology/test_build_checks_audit.py::test_build_checks_schema_documents_word_boundary_semantics PASSED
```

- **Notes**: Per Critic m4 ACCEPTED-PENDING — the global-file pin manual run pass/fail is captured here. Both prose-pin tests pass against `<HOME>\.claude\build-checks.md` (file present locally; pytest.skip path NOT exercised). CI gap (`pytest.skip` when global file absent in CI) is documented in design.md Builder notes; this validation establishes that locally the pins do work end-to-end. **m4 ACCEPTED-PENDING resolved at /validate-slice — evidence captured.**

## Regression-guard (demoted from numbered AC list — verification-plan + must-not-defer track per slice-002 + slice-004 lessons)

The original AC #4 ("no regression in existing 18 BC-1 tests") was demoted to verification-plan + must-not-defer at /build-slice T7 because TF-1 strict-pre-finish refused with `ac-without-row` for regression-guard ACs. Verification:

- **Evidence**: Full BC-1 suite — 25 passed (18 existing + 7 new from this slice).

```
$PY -m pytest tests/methodology/test_build_checks_audit.py --no-header -q
.........................                                                [100%]
25 passed in 0.15s
```

All 18 existing tests continue to pass. The substring → word-boundary tightening is non-controversial (no existing keyword vocabulary intends substring-only match — verified inline in ADR-004 Consequences during /critique triage). Must-not-defer regression-guard satisfied.

## Layered safety checks (VAL-1)

```
$PY -m tools.validate_slice_layers \
  --slice architecture/slices/slice-005-add-bc-1-keyword-precision \
  --changed-files tools/build_checks_audit.py tests/methodology/test_build_checks_audit.py architecture/build-checks.md \
  --imports-allowlist tests \
  --no-carry-over
```

Output:
```
VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).
Clean — both layers passed.
```

- **Layer A (credentials)**: 0 findings — no committed secrets in slice-005's changed files.
- **Layer B (Python dep hallucination)**: 0 findings — all imports resolve cleanly. The new `pytest` import in `tests/methodology/test_build_checks_audit.py` resolves via `[project.optional-dependencies]` (test deps); other imports unchanged from existing patterns.
- **`--imports-allowlist tests`**: reused per slice-003+slice-004 "Validate using your own ship" pattern — N=3 stable now.

## Walking-skeleton audit (WS-1)

Mission brief declares `**Walking-skeleton**: false`. Audit returns clean and the gate passes silently per WS-1's opt-in semantics. Not applicable.

## Exploratory-charter audit (ETC-1)

Mission brief declares `**Exploratory-charter**: false`. Audit returns clean and the gate passes silently per ETC-1's opt-in semantics. Not applicable.

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: Slice-005 is offline methodology tooling (`tools/build_checks_audit.py` + 2 markdown files). No user-facing UI, no multi-device, no multi-user, no sharing/collaboration, no external integrations. Single-environment validation is sufficient and complete.

## Reality surprises

- **Discovery (mid-build, NOT slice-005's scope)**: `audit_slice` default heuristic `slice_folder.parent.parent / "build-checks.md"` resolves wrong for archived slice paths — one segment too deep because `archive/` violates the depth assumption. Workaround: pass `--project-checks` explicitly. Logged in build-log.md Events at /build-slice T4 timestamps. Slice-006+ candidate (`fix-bc-1-archived-slice-heuristic`, ~30 min effort).

- **Design defect surfaced at T5 (resolved as DEVIATION-1)**: BC-GLOBAL-1's `Applies to: always: true` short-circuits before the anchor filter, making AC #1 + AC #2 unachievable as locked in mission-brief. Critic missed this; Builder missed this; surfaced empirically when post-T5 tests still showed BC-GLOBAL-1 firing on slice-003 + slice-004. **Calibration class: this is a `_rule_applies` algorithm-vs-AC interaction surface that the empirical-verification-at-design-time discipline DID NOT cover** — the design's empirical verification only counted anchor matches, not the always-true short-circuit. User approved option 3 (`Applies to: **`); design.md updated; build-log.md captured the deviation. **Lesson for slice-006+ /reflect**: empirical verification at design-time should also exercise the algorithm path-by-path (always-true → glob → keyword), not just the keyword anchor counts in isolation.

- **TF-1 plan vs AC structure refinement (resolved as DEVIATION-2)**: AC #4 (regression-guard) demoted from numbered ACs to verification-plan + must-not-defer track; TF-1 strict-pre-finish refused initially with `ac-without-row`. Same calibration class as slice-002 + slice-004 lessons-learned about meta-ACs. **Lesson for slice-006+ /reflect**: regression-guard ACs in mission-brief should be authored directly into verification-plan + must-not-defer, NOT into the numbered-AC list, to avoid the audit-refusal cycle.

## Shippability regressions

**None.** All 4 shippability catalog entries pass (41 tests total):

| # | Slice | Tests | Result |
|---|-------|-------|--------|
| 1 | slice-001-diagnose-orchestration-fix | 30 | PASS |
| 2 | slice-002-fix-diagnose-contract-and-cwd-mismatch | 4 | PASS |
| 3 | slice-003-add-val-1-imports-allowlist | 3 | PASS |
| 4 | slice-004-fix-rr1-audit-docstring-or-regex | 4 (with `-W error::SyntaxWarning`) | PASS |

Catalog runtime: ~2.2 seconds total (well under the <2 minute budget).

## Verdict

All 4 ACs PASS. Demoted regression-guard verified. VAL-1 clean. WS-1 + ETC-1 opt-out. No multi-instance applicable. No shippability regressions.

**Slice-005 is validated. Proceed to `/reflect`.**

The 2 design deviations (BC-GLOBAL-1 `Applies to` + AC #4 demotion) are both fully captured here + in build-log.md; `/reflect` will categorize them in the validated/corrected/discovered axes. The 1 mid-build discovery (`audit_slice` archive-path heuristic bug) carries forward as a slice-006+ candidate.
