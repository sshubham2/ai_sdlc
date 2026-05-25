# Build log: Slice 005 add-bc-1-keyword-precision

**Date**: 2026-05-10
**Result**: SHIPPED-WITH-DEFERRALS

## Summary

### Plan executed

Plan saved at `<HOME>\.claude\plans\kind-skipping-manatee.md`. 8 tasks, all completed.

| # | Task | Status |
|---|------|--------|
| T1 | Write 7 PENDING tests (TF-1 PENDING → WRITTEN-FAILING transitions, genuine per slice-003 lesson) | ✓ done |
| T2 | Lock canonical schema-prose substrings (`Trigger anchors`, `word-boundary`) | ✓ done |
| T3 | Modify `tools/build_checks_audit.py` (BuildCheckRule + _parse_rules + _rule_applies + module docstring) | ✓ done |
| T4 | Mid-slice smoke gate — surfaced expected mid-slice state (word-boundary alone insufficient; matches design empirical-verification table) + bonus discovery: `audit_slice` heuristic broken for archived slice paths | ✓ done |
| T5 | Migrate BC-PROJ-1, BC-PROJ-2 (project), BC-GLOBAL-1 (global ~/.claude); schema description prose updates in both files; **DEVIATION**: BC-GLOBAL-1's `Applies to: always: true` → `Applies to: **` to make anchor filter effective | ✓ done |
| T6 | Self-application — applicable={BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1} (expected per Critic B1 meta-references); shippability catalog 59/59; `-W error::SyntaxWarning` 25/25 | ✓ done |
| T7 | Pre-finish gates — TF-1 strict-pre-finish refused initially due to AC #4 regression-guard pattern (slice-002+slice-004 lesson); demoted AC #4; renumbered schema-pin from #5 → #4. Final: TF-1 ✓ WIRE-1 ✓ mock-budget ✓ shippability ✓ no TODO/FIXME ✓; drift-check skipped-with-rationale (tooling-only slice). 352/352 full suite pass | ✓ done |
| T8 | This Summary section + ~/.claude/build-checks.md out-of-repo diff capture | ✓ done |

### Mid-slice smoke gate

**Result**: PASS (with informative discovery — see Events log T4 timestamps)

**Evidence**: BC-1 audit run against slice-003 + slice-004 archive folders (with explicit `--project-checks architecture/build-checks.md` to work around the heuristic bug). Post-T3 (word-boundary alone, no anchors yet): both BC-PROJ-2 + BC-GLOBAL-1 still fire on slice-003 + slice-004 — confirms design.md empirical-verification table prediction that word-boundary alone is insufficient. T5 anchor migration is what closes the gap. Post-T5: backtest tests pass, BC-PROJ-2 + BC-GLOBAL-1 silenced.

**Bonus discovery**: `audit_slice` default heuristic `slice_folder.parent.parent / "build-checks.md"` resolves wrong for archived slices (one path-segment too deep — `archive/` violates the depth assumption). Pre-existing bug, NOT slice-005's scope. Workaround: pass `--project-checks` explicitly. Logged for slice-006+ candidate (`fix-bc-1-archived-slice-heuristic`, ~30 min slice).

### Pre-finish gate

- [x] All 4 ACs (renumbered 1, 2, 3, 4 post-T7 demotion) PASS — see Events log T1-T7 + validation.md (pending)
- [x] Must-not-defer items addressed (regression-guard now in verification-plan + must-not-defer track per the demotion; backwards-compat ✓; carry-over preserved ✓; glob path unaffected ✓; no false fourth-rule on slice-005 self-application ✓; input validation on Trigger anchors via `anchor-not-in-keywords` violation kind ✓)
- [x] /drift-check — skipped-with-rationale (tooling-only slice; no architecture/components or contracts touched)
- [x] Mid-slice smoke regression-check passes after final cleanup (slice-003 + slice-004 archive backtests both clean; slice-005 self-application = expected meta-references)
- [x] No new TODOs / FIXMEs / debug prints (grep verified zero matches in tools/build_checks_audit.py + tests/methodology/test_build_checks_audit.py)
- [x] LINT-MOCK-1 mock-budget lint clean (no mocks introduced)
- [x] WIRE-1 wiring matrix audit clean (empty matrix accepted; no new modules)
- [x] BC-1 build-checks audit on slice-005's own files — applicable={BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1}, exactly 3 (Critic B1 expected meta-references; not a regression)
- [x] TF-1 test-first audit `--strict-pre-finish` clean — 7 rows, all PASSING
- [x] Shippability catalog regression check (4 entries) — 59/59 pass
- [x] -W error::SyntaxWarning pytest pass (slice-004 Python 3.12+ lesson honored)

### Deferrals

- **m4 (Critic minor)** — schema-pin global-file CI gap (`~/.claude/build-checks.md` test path skips when file absent in CI). User-approved at /critique triage. Action carried to /validate-slice — capture global-file pin manual run pass/fail in validation.md evidence section. design.md Builder notes documents the gap with three mitigations. NOT a build-blocking deferral.

### Design deviations

- **DEVIATION-1 (T5)**: BC-GLOBAL-1's `Applies to: always: true` changed to `Applies to: **` (universal-glob-on-any-changed-file). Reason: `always: true` short-circuits before the anchor filter, making AC #1+#2 unachievable (BC-GLOBAL-1 was un-silenceable). Three options surfaced to user (hardcoded language list rejected as brittle; algorithm change rejected as semantic break; `**` glob accepted). Real-world fire behavior on slices that touch any code is unchanged (`/build-slice` always passes `--changed-files`); backtests on archive folders correctly fall through to anchor-filtered keyword path. design.md "What's new" section updated with full rationale; ADR-004 unchanged (decision-level intent unchanged; this is a tactical tweak to the migration target).
- **DEVIATION-2 (T7)**: AC #4 (regression-guard "no regression in existing 18 BC-1 tests") DEMOTED from numbered-AC list to verification-plan + must-not-defer track. Original AC #5 (schema-pin) renumbered to AC #4. Reason: TF-1 strict-pre-finish refused with `ac-without-row` because regression-guard ACs cannot have a meaningful TF-1 row (would be circular meta-AC per slice-002+slice-004 lessons). mission-brief.md + design.md test list updated; TF-1 plan rows now reference AC #4 instead of AC #5.

### Files changed

**In-repo**:
- `tools/build_checks_audit.py` — BuildCheckRule.trigger_anchors field; _parse_rules reads Trigger anchors + emits anchor-not-in-keywords violation; _rule_applies word-boundary regex + anchor filter; module docstring updated
- `architecture/build-checks.md` — L3 schema description (word-boundary + Trigger anchors paragraphs); BC-PROJ-1 +Trigger anchors: subagent, fan-out; BC-PROJ-2 +Trigger anchors: fence, code-block, llm
- `tests/methodology/test_build_checks_audit.py` — +import pytest; +7 new tests after line 368
- `architecture/slices/slice-005-add-bc-1-keyword-precision/mission-brief.md` — AC #4 demoted; ACs renumbered 1-4; TF-1 plan grew 4 → 7 rows during /critique then status updated to PASSING during /build-slice
- `architecture/slices/slice-005-add-bc-1-keyword-precision/design.md` — DEVIATION-1 rationale appended to BC-GLOBAL-1 surface change section
- `architecture/slices/slice-005-add-bc-1-keyword-precision/critique.md` — Triage table populated (NEEDS-FIXES; user-ratified)
- `architecture/slices/slice-005-add-bc-1-keyword-precision/build-log.md` — this file
- `architecture/slices/slice-005-add-bc-1-keyword-precision/milestone.md` — stage advanced to build → pre-validate
- `architecture/decisions/ADR-004-bc-1-keyword-precision-via-word-boundary-and-anchors.md` — m2 inline citations added during /critique triage
- `architecture/slices/_index.md` — Active slice table updated by /slice

**Out-of-repo (not in git diff — captured here as forensic evidence per Critic m4)**:
- `~/.claude/build-checks.md` BEFORE: L3 ended at "...promotion is manual at /reflect Step 5b" (3 lines pre-rule); L11-14 BC-GLOBAL-1 had `Severity: Important / Applies to: always: true / Promoted from: ai_sdlc / slice-001-... / Trigger keywords: parse, fence, code-block, ...`
- `~/.claude/build-checks.md` AFTER: L3 prelude got NEW paragraph mentioning `word-boundary` + `Trigger anchors:` (the schema-pin substrings); BC-GLOBAL-1's `Applies to:` value changed `always: true` → `**` (DEVIATION-1); `Promoted from:` paragraph extended with slice-005 design-deviation rationale; new line `Trigger anchors: fence, code-block, llm, structured-output`

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-10 00:55 BUILD: T1 start — appending 7 PENDING tests to tests/methodology/test_build_checks_audit.py
- 2026-05-10 01:02 TEST: T1 verify-failing — 6 of 7 FAIL in genuine failure modes (AttributeError on trigger_anchors; AssertionError on BC-PROJ-2 in applicable; missing schema substring; missing violation kind). Test #3 (positive case) PASSES pre-fix (regression-guard shape, expected). TF-1 transitions PENDING → WRITTEN-FAILING genuine (slice-003 lesson honored).
- 2026-05-10 01:03 BUILD: T1 done. T2 start — locking schema-prose substrings ("Trigger anchors" + "word-boundary").
- 2026-05-10 01:04 BUILD: T2 done (substrings confirmed). T3 start — modifying tools/build_checks_audit.py (BuildCheckRule + _parse_rules + _rule_applies + module docstring).
- 2026-05-10 01:08 TEST: post-T3 full BC-1 suite — 20 passed, 5 failed. Failures are 5 expected pre-T5 (anchors not migrated): tests #1, #2 (backtests), #4, #5 (schema-pin), #6 (anchor tuples). Tests #3 (positive case) + #7 (anchor-not-in-keywords) PASS. All 18 existing tests PASS — zero regression (must-not-defer #4 satisfied).
- 2026-05-10 01:09 SMOKE: T4 mid-slice smoke gate start — running BC-1 audit against slice-003 + slice-004 archive folders (real CLI invocation, not pytest).
- 2026-05-10 01:11 FINDING: `audit_slice` default heuristic `slice_folder.parent.parent / "build-checks.md"` resolves to `architecture/slices/build-checks.md` for archived slices (one level too deep — `archive/` subfolder violates the depth assumption). Pre-existing bug, NOT slice-005's scope. Workaround: pass `--project-checks architecture/build-checks.md` explicitly when smoking against archived slices. Log for slice-006+ candidate (`fix-bc-1-archived-slice-heuristic` or absorb into a broader robustness fix).
- 2026-05-10 01:12 SMOKE: T4 result — slice-003 + slice-004 archives (with explicit --project-checks): applicable=[BC-PROJ-2, BC-GLOBAL-1], skipped=[BC-PROJ-1]. **Expected mid-slice state**: word-boundary alone is insufficient (matches design.md empirical-verification table prediction); T5 anchor migration is what closes the gap. PASS — gate value confirmed.
- 2026-05-10 01:13 BUILD: T4 done. T5 start — migrating BC-PROJ-1, BC-PROJ-2 (architecture/build-checks.md) + BC-GLOBAL-1 (~/.claude/build-checks.md) to use Trigger anchors; updating L3 schema description prose in both files.
- 2026-05-10 01:18 DEVIATION: BC-GLOBAL-1's `Applies to: always: true` short-circuits before the anchor filter, making AC #1+#2 unachievable as-locked. Surfaced to user; user approved option 3 (change `Applies to: **` — language-agnostic) over hardcoding extension lists. design.md updated with full rationale + 3-option alternatives.
- 2026-05-10 01:19 TEST: post-deviation — full BC-1 suite **25/25 PASS** (18 existing + 7 new, all green). All TF-1 PASSING.
- 2026-05-10 01:20 BUILD: T5 done. T6 start — self-application + shippability regression check.
- 2026-05-10 01:22 SMOKE: T6 self-application — slice-005's own files trigger {BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1} (exactly 3 rules; matches Critic B1 expectation: meta-references — slice's domain is rule-definition, not LLM-fence-parsing). NOT a regression; no fourth rule appearing.
- 2026-05-10 01:23 TEST: shippability catalog (4 entries × tests) — 59 passed.
- 2026-05-10 01:24 TEST: -W error::SyntaxWarning pytest pass — 25/25; slice-004 Python 3.12+ lesson honored (no escape-sequence violations in new docstrings/comments).
- 2026-05-10 01:25 BUILD: T6 done. T7 start — pre-finish gates.
- 2026-05-10 01:27 FINDING: TF-1 strict refused initial run with `ac-without-row` violation on AC #4 ("no regression in existing 18 BC-1 tests"). Per slice-002+slice-004 lessons, regression-guard invariants belong in verification-plan + must-not-defer track, NOT as numbered ACs. Demoted AC #4 from numbered list; renumbered original AC #5 (schema-pin) as new AC #4. TF-1 plan rows updated to reference AC #4 instead of AC #5.
- 2026-05-10 01:28 TEST: TF-1 strict pre-finish — clean: 7 rows, all PASSING.
- 2026-05-10 01:29 TEST: WIRE-1 audit — clean (empty matrix accepted; no new modules).
- 2026-05-10 01:30 TEST: mock_budget_lint — clean (no mocks introduced in tools/build_checks_audit.py or tests/methodology/test_build_checks_audit.py).
- 2026-05-10 01:31 TEST: full pytest tests/methodology/ tests/skills/ — 352 passed (zero regression on whole suite).
- 2026-05-10 01:32 DEFERRAL: /drift-check — skipped with rationale. Slice-005 is tooling-only; no architecture/components or architecture/contracts files modified; thin vault state matches code by construction. Per slice-005 plan T7 step 6, this skip-with-rationale is logged here.
- 2026-05-10 01:33 BUILD: T7 done — all pre-finish gates clear (TF-1 ✓ WIRE-1 ✓ mock-budget ✓ shippability ✓ SyntaxWarning ✓ no TODO/FIXME ✓ drift-check skipped-with-rationale). T8 start — Summary section.
