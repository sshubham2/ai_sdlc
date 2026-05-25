# Critique Review: Slice 055 add-shippability-runner-execution-tests

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-21
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: ACCEPT

## Summary

The first Critic's review on slice-055 is exceptionally strong: both Blockers (B1 fail-branch `;`-split crash; B2 BCR-1 position-pin regression) were caught empirically with code citations and reproduced before filing; all three Majors (cross-site name drift, PowerShell-unfriendly grep, brittle substring) hit real concerns; and the m1 OVERRIDE is well-justified. The meta-Critic independently re-verified the post-fix artifacts empirically and independently re-traversed all 8 dimensions. No new findings of Blocker/Major severity surface; the slice is build-ready.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (FAIL-branch `;`-split crash) — confirmed; severity Blocker is appropriate. Re-verified empirically: `_segments('<interp> -c "import sys; sys.exit(1)"')` → 2 segments, both crash on `shlex.split`. The post-fix substitution `<interp> -c "raise SystemExit(1)"` re-verified clean (1 segment, `shlex.split` → `['<interp>', '-c', 'raise SystemExit(1)']`). The Builder applied the fix at mission-brief AC2 + AC3 + Must-not-defer + design.md `Subprocess invocations` table + `Helper signature` constraint paragraph faithfully. Framework: APED-1 (audit-parse empirical execution); a documented helper grammar that contradicts the implementation's literal parse is a classic real-not-imagined defect.

- **B2** (BCR-1 position-pin regression) — confirmed; severity Blocker is appropriate. `block.rfind('**Evidence:**')` anchors on the header label (internal line 14 of SC-005 block), NOT the last sub-bullet (internal line 16). Confirmed against `diagnose-out/backlog.md` lines 175-177 that the SC-005 block has `**Evidence:**` header followed by two `  - ` sub-bullets, so a header-only pin would silently pass with `Addressed` injected BEFORE the first sub-bullet. The post-fix `re.finditer(r'^  - ', block, re.MULTILINE)[-1]` correctly anchors on the last sub-bullet (regex confirmed not to match the `- **Addressed:**` line itself, since the latter starts at column 0 not `  -`). Slice-054 precedent independently verified at line 107 of backlog.md showing Addressed-line shape. Framework: contract-drift-from-precedent — when mirroring an established pattern, mirror the contract, not the symptom.

- **M1** (cross-site smoke-gate name drift) — confirmed; severity Major is appropriate. pytest `::` collector requires exact name match; the short-form `test_run_catalog_pass_row` would have collected zero items at mid-slice gate runtime. Builder fix re-syncs to `_records_pass` / `_records_fail` long form consistent with design.md throughout. Framework: FBCD-1 cross-file consistency (slice-009 Dim-9 sub-clause).

- **M2** (PowerShell-unfriendly `grep -c`) — confirmed; severity Major is appropriate. The rest of the verification plan uses `& $PY ...` PowerShell-shape; a bare `grep` would not execute on a stock Win11 PowerShell shell (per `~/.claude/CLAUDE.md` Shell preference). Builder fix substitutes a `& $PY -c "import ast, ..."` AST-based count, fully cross-shell. Framework: cross-platform-tool-discipline (CLAUDE.md PowerShell-first preference + shared-interpreter rule).

- **M3** (brittle substring assertion) — confirmed; severity Major is appropriate. The slice-038 m2 load-bearing-test lesson is directly applicable: a substring-only pin on a debug-style format string can false-pass under cosmetic edits or false-fail under benign tail appends. Builder's fix (structural pins on `status` / `line` / `detail`-truthy + narrowed substring scoped to `detail.split("\n", 1)[0]`) is the canonical answer to that lesson — structural pin survives format edits, narrow first-line substring catches the specific format-string regression. Framework: load-bearing-test discipline (Hendrickson; slice-038 reflection citation).

- **m1** (forecast section seeding bias) — confirmed VALID-with-OVERRIDE; severity Minor is appropriate. The Builder's OVERRIDE rationale (the very fact that B1+B2 were found OUTSIDE the forecast list empirically demonstrates non-binding) is sound and self-validating from this critique's own evidence. Keeping the forecast section as user-transparency is the right call.

- **m2** (helper-signature backtick attribution) — confirmed; severity Minor is appropriate. `_catalog_rows` at `tools/shippability_decoupling_audit.py:179-193` does not strip backticks; `_segments` at line 213 does the per-segment strip. Builder fix clarifies the layering correctly.

## Suspicious findings

No suspicious findings. Every first-Critic finding is empirically grounded and the Builder fixes are faithful.

## Missed findings

No missed findings of Blocker or Major severity. Two Minor-or-below observations from independent re-traversal that the meta-Critic evaluated and decided NOT to file:

1. **AC1 (PASS) under-pinned relative to AC2 (FAIL)**: mission-brief AC1 says only "records `passed += 1`" without explicit `result.rows[0].status == "PASS"` / `result.rows[0].line > 0` structural pins, whereas AC2 (FAIL) carries full structural + narrow pins. Design.md `Error model` row 1 does pin the PASS structurals (`passed == 1`, `failed == 0`, `status == "PASS"`, `line > 0`). The asymmetry is cosmetic — design.md is binding for the Builder's test code; mission-brief AC1's softer language is a minor specification gap but doesn't change the test the Builder will write. Below Minor threshold.

2. **Multi-segment row not pinned**: `run_catalog` carries first-segment-fails-then-break semantics for multi-segment rows (`tools/shippability_runner.py:140-153`). The new tests pin single-segment rows only. The current `architecture/shippability.md` has at least one multi-segment row (#28 per the runner's module docstring R-8 history). SC-005 evidence specifies "shells out every command... decides pass/fail per row" without explicitly demanding multi-segment coverage. Filing as missed would over-reach the SC-005 scope; if a regression on multi-segment break semantics ever surfaces, that's its own future slice. Below threshold by reference to SC-005 evidence wording and the slice's deliberate "5 tests, no more" scoping (design.md `Defensive / out-of-scope branches` section, which is itself a thoughtful scope-discipline anchor).

The first Critic's coverage is complete given SC-005's evidence wording.

## Severity adjustments

No severity adjustments. All seven finding severities are appropriately calibrated.

## Notes

Confidence: high. The first Critic's pattern on this slice — empirical reproduction of both Blockers before filing, citation discipline (file:line for every claim), Builder-fix verification with post-fix empirical round-trip, and a Minor that gets overridden with reasoned rationale — is calibrated well. The forecast vs. actual-findings split is a clean empirical demonstration that confirms m1's OVERRIDE.

One calibration observation: the first Critic's "Dimensions checked" section is unusually thorough for a 0.5-day test-only slice, with each dimension carrying either a positive finding or an explicit N/A rationale. That depth-of-pass on the dimensions matrix is exactly the discipline that catches B1 and B2 (both required cross-file empirical execution against the implementation's literal parse, not just static design.md reading). Recommend this pattern as a positive exemplar for future Critic calibration.

No reservations on the Builder's draft dispositions — 5 ACCEPTED-FIXED + 1 OVERRIDDEN-with-rationale + 1 ACCEPTED-FIXED on m2 all hold up under second-pass scrutiny. Dual-review verdict: **ACCEPT**.

Files consulted during meta-review:
- `architecture/slices/slice-055-add-shippability-runner-execution-tests/mission-brief.md`
- `architecture/slices/slice-055-add-shippability-runner-execution-tests/design.md`
- `architecture/slices/slice-055-add-shippability-runner-execution-tests/critique.md`
- `tools/shippability_runner.py`
- `tools/shippability_decoupling_audit.py` (lines 170-217)
- `tools/shippability_path_audit.py` (lines 80-119)
- `diagnose-out/backlog.md` (SC-005 block lines 162-178; slice-054 precedent line 107)
- `tests/methodology/test_critique_review_prerequisite_audit.py` (direct-call citations at lines 74, 94, 196, 213)
