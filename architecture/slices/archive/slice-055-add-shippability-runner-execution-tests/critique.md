# Critique: Slice 055 add-shippability-runner-execution-tests

**Critic reviewed**: mission-brief.md, design.md, new ADRs (none — slice deliberately mints none)
**Date**: 2026-05-21
**Result**: CLEAN

## Summary

Strong intent and well-scoped premise (close SC-005 with real execution tests, no rule minting). However the design as-drafted contains one **Blocker** that would crash the FAIL-branch test at runtime, one **Blocker** that weakens the BCR-1 position-pin contract relative to the slice-054 precedent it explicitly mirrors, and three **Majors** (FBCD-1 cross-file naming inconsistency, PowerShell-unfriendly grep, brittle substring assertion). Both Blockers verified empirically before applying fixes. Fix Builder-applied for all 5 Critic findings except m1 (OVERRIDDEN); m2 ACCEPTED-FIXED.

## Findings

### Blockers (must address before /build-slice)

#### B1: FAIL-branch test's `<interp> -c "import sys; sys.exit(1)"` machine_cmd will crash inside `run_catalog` with `ValueError: No closing quotation` — not exercise the FAIL branch as AC2 claims

- **Claim under review**: design.md "Subprocess invocations" table, row `test_run_catalog_fail_row_records_fail`: `<sys.executable> -c "import sys; sys.exit(1)"` returncode 1. mission-brief AC2 + Must-not-defer: tmp-cell uses `<interp> -c "import sys; sys.exit(1)"` (or equivalent).
- **Issue**: `tools.shippability_decoupling_audit._segments` (which `runner` reuses verbatim per `shippability_runner.py:50`) does a NAIVE `machine_cmd.split(";")` BEFORE any shell-aware parsing. The `;` inside the python `-c` body gets split. Builder empirically verified:
  ```
  cell = '<interp> -c "import sys; sys.exit(1)"'
  _segments() → ['<interp> -c "import sys', 'sys.exit(1)"']
  seg[0] shlex.split → ValueError: No closing quotation
  seg[1] shlex.split → ValueError: No closing quotation
  ```
  The test would NOT assert `"segment exited 1" in result.rows[0].detail` (AC2) — it would raise a Python `ValueError` inside `run_catalog` and fail with a stack trace, NOT with the FAIL branch's `f"segment exited {proc.returncode}: {seg!r}"` detail string.
- **Evidence**:
  - `tools/shippability_decoupling_audit.py:212` — `for raw in machine_cmd.split(";"):` (naive split, no shell awareness)
  - `tools/shippability_runner.py:140-141` — `for seg in _segments(cell): argv = _normalize_interp(shlex.split(seg, posix=True))`
  - Builder empirical reproduction: `& $PY -c "from tools.shippability_decoupling_audit import _segments; import shlex; cell = '<interp> -c \"import sys; sys.exit(1)\"'; print(_segments(cell)); [print(shlex.split(s, posix=True)) for s in _segments(cell)]"` — both halves raise `ValueError: No closing quotation`
- **Proposed fix**: use a `;`-free form: `<interp> -c "raise SystemExit(1)"` (preferred; verified to round-trip cleanly: one segment, `shlex.split` → `['<interp>', '-c', 'raise SystemExit(1)']`). Update mission-brief AC2, mission-brief Must-not-defer (NEW guard bullet), design.md "Error model" + "Subprocess invocations" table, and design.md `_make_catalog` helper-signature constraint paragraph.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md AC2 + AC3 + Must-not-defer (added explicit `;`-free guard); design.md "Error model" + "Subprocess invocations" table + "Helper signature" `machine_cmd` constraint paragraph. Empirical verification: post-fix `_segments('`<interp> -c "raise SystemExit(1)"`')` → `['<interp> -c "raise SystemExit(1)"']` (one segment, `shlex.split` clean → `['<interp>', '-c', 'raise SystemExit(1)']`).

#### B2: AC5 position-pin uses `block.rfind('**Evidence:**')` (header position), regressing the BCR-1 "AFTER Evidence sub-list" semantic that slice-054 AC4 explicitly established

- **Claim under review**: mission-brief Verification plan row 5: `ev = block.rfind('**Evidence:**'); addr = block.find('- **Addressed:** slice-055-...'); assert ev > 0 and addr > ev`. design.md "BCR-1 round-trip plumbing": "inject ... immediately AFTER the last `**Evidence:**` bullet AND BEFORE the next `### SC-006 ` header" + "mirroring slice-054".
- **Issue**: `rfind('**Evidence:**')` returns the position of the literal `**Evidence:**` *header label* (line 14 of SC-005 block in `diagnose-out/backlog.md`) — NOT the position of the last Evidence sub-list bullet (line 16). `assert addr > ev` passes for ANY position after the `**Evidence:**` header — INCLUDING positions interleaved between the two evidence sub-bullets (lines 15, 16) or before the first bullet. The check does not actually pin "AFTER the Evidence sub-list" — the position-pin contract claimed by design.md is materially weaker than implemented. Per the slice-054 reflection ("**AC4 (M4 BCR-1 grep position-semantic gap): VALIDATED — the position-pinned awk + line-number check ACTUALLY caught the BCR-1 invariant ... A content-only `grep -A 30` would have passed for ANY position in next 30 lines — the position-pin was the right contract for the first BCR-1 dogfood**"), slice-054 explicitly pinned `evidence_last_line=$(grep -n "^  - " /tmp/sc001.txt | tail -1 | cut -d: -f1)` — the LAST evidence sub-bullet line. Slice-055 had REGRESSED that pin to the (weaker) Evidence header position.
- **Evidence**:
  - `diagnose-out/backlog.md` SC-005 block — `**Evidence:**` header label at internal line 14; sub-bullets at lines 15-16 (last bullet is at 16)
  - `architecture/slices/archive/slice-054-fix-pyproject-toml-version-drift/mission-brief.md:46` — slice-054 AC4 uses `grep -n "^  - "` + `tail -1` to anchor on the LAST evidence sub-bullet
  - `architecture/slices/archive/slice-054-fix-pyproject-toml-version-drift/reflection.md:42` — VALIDATED record of why position-pin (vs content-only / header-only) matters
- **Proposed fix**: anchor on the last `^  - ` sub-bullet position via `re.finditer(r'^  - ', block, re.MULTILINE)` + `[-1].start()`.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md Verification plan row 5 + Must-not-defer (added explicit position-pin guard bullet); design.md "BCR-1 round-trip plumbing" paragraph rewritten to spell out the layered semantic ("**Evidence:**" header position is INSUFFICIENT — anchor must be on the LAST `^  - ` sub-bullet position). Empirical pre-/reflect verification: `last_ev_pos=1185, addr_pos=-1` (Addressed not yet injected — expected — anchor mechanic confirmed against real SC-005 block).

### Majors (address this slice)

#### M1: Mid-slice smoke gate uses test names `test_run_catalog_pass_row` / `test_run_catalog_fail_row` — but design.md "What's new" + verification plan + design.md "Error model" all use the longer `_records_pass` / `_records_fail` suffix. The smoke gate would fail to collect any tests.

- **Claim under review**: mission-brief "Mid-slice smoke gate" code block (short names) vs. mission-brief AC2 + design.md throughout (long names with `_records_pass` / `_records_fail` suffix).
- **Issue**: cross-site name drift (FBCD-1, Dim 9). pytest's `::` selector requires exact function name match — the smoke gate would emit `no tests ran in ...` (or `ERROR: not found`) and the operator running the mid-slice gate would see a confusing "0 tests collected" output instead of the intended PASS/FAIL signal.
- **Evidence**:
  - mission-brief.md pre-fix "Mid-slice smoke gate" code block — SHORT names
  - mission-brief.md AC2 + Verification plan row 2 — LONG name `test_run_catalog_fail_row_records_fail`
  - design.md "What's new" + "Error model" + "Subprocess invocations" table — all LONG names
- **Proposed fix**: update mission-brief Mid-slice smoke gate to use the LONG names.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md Mid-slice smoke gate code block — replaced both short names with `test_run_catalog_pass_row_records_pass` + `test_run_catalog_fail_row_records_fail`.

#### M2: AC1 verification plan uses `grep -c "^def test_"` — PowerShell-unfriendly

- **Claim under review**: mission-brief Verification plan row 1: `AND grep -c "^def test_" ... ≥4`.
- **Issue**: `grep` is not a PowerShell builtin; the rest of the verification plan uses `& $PY ...` style. A bare `grep` invocation is inconsistent and may not execute on a stock Windows PowerShell environment. The PRIMARY `--collect-only -q` check is sufficient, but a count assertion via `& $PY -c "..."` is cross-shell.
- **Evidence**:
  - mission-brief Verification plan row 1 pre-fix — `grep -c` secondary check
  - All other rows use PowerShell-shaped `& $PY ...`
- **Proposed fix**: replace the secondary `grep -c` with a PowerShell-clean `& $PY -c "import ast, pathlib; ..."` AST-based count assertion.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md Verification plan row 1 — replaced `grep -c "^def test_"` with `& $PY -c "import ast, pathlib; t = ast.parse(...); tests = [n.name for n in t.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]; assert len(tests) >= 4, ...; print(f'OK {len(tests)} tests')"`.

#### M3: AC2's substring assertion `"segment exited 1" in result.rows[0].detail` is brittle to format-string changes; missing structural pin

- **Claim under review**: mission-brief AC2 pre-fix: `"segment exited 1" in result.rows[0].detail` only.
- **Issue**: per slice-038 m2 load-bearing-test lesson, a substring brittle to a debug-style format-string edit is the kind of vacuous pin slice-038 m2 warned against. The runner's format at `tools/shippability_runner.py:151-152` is `f"segment exited {proc.returncode}: {seg!r}\n{tail.strip()}"`. A future edit to append more context could leave the substring passing while the actual structural FAIL behavior regresses (or vice versa).
- **Evidence**:
  - `tools/shippability_runner.py:151-152` — current format string
  - mission-brief AC2 pre-fix + design.md "Error model" — substring-only check
- **Proposed fix**: add structural assertions (`result.rows[0].status == "FAIL"`, `result.rows[0].line > 0`, `result.rows[0].detail` truthy) alongside a narrower substring pin scoped to the FIRST line of detail (`detail.split("\n", 1)[0]`) so future tail-content appends don't false-pass the substring.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md AC2 + design.md "Error model" table — added structural pins (`status="FAIL"`, `line > 0`, `detail` truthy) and narrowed substring pin to first line (`detail.split("\n", 1)[0]`).

### Minors (log; address if cheap)

#### m1: design.md "Risk surface for the Critic" forecast may seed confirmation bias

- **Claim under review**: design.md final section forecasts 4 concerns the Critic might raise.
- **Issue**: forecasting CAN seed confirmation bias on the Critic side. The actual Blockers (B1 + B2) were NOT in the forecast — empirically demonstrating the Critic's independent traversal does useful work. Either keep as transparent pre-flight or trim.
- **Evidence**: design.md "Risk surface for the Critic" — 4-bullet forecast list.
- **Proposed fix**: optional.
- **Builder draft**: **OVERRIDDEN** — the forecast section IS valuable as a transparent pre-flight FOR THE USER (helps the user evaluate the Critic's work), and the empirical demonstration in this very critique (B1 + B2 NOT in the forecast list, found independently) is itself evidence that the forecast is non-binding on the Critic. Rationale for override: removing the section trades a small (theoretical) Critic-bias risk for a real user-visibility cost; the Critic in fact found 2 Blockers outside the forecast list, so the bias-seeding concern is not empirically supported on this slice.

#### m2: design.md "Helper signature" docstring misstates `_catalog_rows` backtick requirement

- **Claim under review**: design.md pre-fix helper signature paragraph: "the helper wraps it in the cell-level backticks `_catalog_rows` expects".
- **Issue**: `_catalog_rows` (line 179-193 of `shippability_decoupling_audit.py`) just parses the markdown table cells — it does NOT require backticks. The backticks are stripped LATER by `_segments` (line 213). Minor doc inaccuracy.
- **Evidence**:
  - `tools/shippability_decoupling_audit.py:179-193` — `_catalog_rows` (no backtick stripping)
  - `tools/shippability_decoupling_audit.py:213` — backtick strip in `_segments`
- **Proposed fix**: clarify the helper doc.
- **Builder draft**: **ACCEPTED-FIXED** at design.md "Helper signature" section — clarified that backticks are stripped by `_segments` per-segment, not required by `_catalog_rows`, and that the wrap exists so the fixture matches real-row shape.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (the `<interp> -c "import sys; sys.exit(1)"` claim was reasoned-not-executed against `_segments`'s naive `;`-split); m2 (helper doc misstates `_catalog_rows`'s backtick requirement). Per APED-1 sub-clause: B1's trap was reachable only by executing the design's literal cell through the implementation's parse pipeline.
- [x] **Missing edge cases** — empty catalog / multi-row catalog / race-concurrency / permission-denied / platform-specific — none constitute findings (analyzed and out-of-scope per SC-005 evidence wording; runner is stateless sequential).
- [x] **Over-engineering** — none. Slice deliberately limited to 5 tests, no production-code touch, no rule mint, voluntary-restraint discipline correctly applied.
- [x] **Under-engineering** — none on AC delivery. Every AC has a design element. TF-1 N/A (`Test-first: false`). AC5 /reflect-deferred per slice-054 pattern.
- [x] **Contract gaps** — none. Test-only slice; pinned contracts (RunResult, main → int 0/1/2) are unchanged.
- [x] **Security** — N/A. Tests run in `tmp_path`; subprocess invocations are pure-Python no-ops; no network / PII / auth.
- [x] **Drift from vault** — WIRE-1 exemption row carries `rationale:` (verified). PMI-1 / INST-1 / CSP-1 unaffected. No new ADRs (correctly justified). BCR-1 sentinel `**Closes:** SC-005` present at mission-brief line 3 — verified against `diagnose-out/backlog.md` SC-005 block existing. B2 is the BCR-1 contract-strength regression filed under Blockers.
- [x] **Web-known issues** — skipped honestly: no novel external-tech surface. Python stdlib (pytest tmp_path, subprocess.run, shlex.split) + internal helpers only.
- [x] **Cross-cutting conformance** — FBCD-1 (M1 cross-site naming drift); APED-1 generalized (Critic's empirical execution of design.md's literal cell caught B1); load-bearing-test discipline (M3 brittleness pin); slice-054 dogfood precedent (B2 contract regression). All other sub-clauses examined and clean.

## Triage

**Triaged by**: user
**Date**: 2026-05-21
**Final verdict**: CLEAN

(Meta-Critic dual-review verdict: ACCEPT — all 7 first-Critic findings VALID at correct severity; 0 suspicious / 0 missed / 0 severity adjustments. User ratified all Builder drafts via TRI-1 structured-options gate.)

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | `;`-free `raise SystemExit(1)` substitution applied at mission-brief AC2/AC3/Must-not-defer + design.md Error model + Subprocess invocations + Helper signature; empirically verified clean `_segments` + `shlex.split` round-trip. Meta-Critic VALIDATED. |
| B2 | Blocker  | ACCEPTED-FIXED | `re.finditer(r'^  - ', block, re.MULTILINE)[-1]` anchor restores slice-054 AC4 contract; mission-brief AC5 + Must-not-defer + design.md BCR-1 plumbing rewritten; pre-/reflect anchor mechanic verified against real SC-005 block. Meta-Critic VALIDATED. |
| M1 | Major    | ACCEPTED-FIXED | Mid-slice smoke gate names updated to `_records_pass` / `_records_fail` long form, matching design.md throughout (FBCD-1 cross-file consistency). Meta-Critic VALIDATED. |
| M2 | Major    | ACCEPTED-FIXED | `grep -c` replaced with PowerShell-clean `& $PY -c "import ast, ..."` AST-based count (cross-shell). Meta-Critic VALIDATED. |
| M3 | Major    | ACCEPTED-FIXED | Added structural pins (`status`, `line`, `detail` truthiness) alongside narrowed first-line substring pin (slice-038 m2 load-bearing-test lesson). Meta-Critic VALIDATED. |
| m1 | Minor    | OVERRIDDEN | The Critic-forecast section in design.md is for USER transparency, not Critic conditioning; this very critique's B1 + B2 (NOT in the forecast list) empirically demonstrate the forecast is non-binding. Meta-Critic VALIDATED the override. |
| m2 | Minor    | ACCEPTED-FIXED | Helper signature docstring clarified to attribute backtick stripping to `_segments`, not `_catalog_rows`. Meta-Critic VALIDATED. |
