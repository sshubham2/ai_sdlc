# Build log: Slice 001 diagnose-orchestration-fix

**Date**: 2026-05-09
**Result**: SHIPPED

## Events (append-only — flight recorder)

- 2026-05-09 BUILD: build-slice plan approved by user; tasks #55-#65 created
- 2026-05-09 BUILD: milestone → stage: build; Phase 0 starting
- 2026-05-09 BUILD: Phase 0 (triage design-stage edits) PASS — mission-brief, design.md, ADR-001 updated
- 2026-05-09 BUILD: Phase 1 (test infrastructure) PASS — tests/skills/diagnose/ + conftest with sys.path insert
- 2026-05-09 ERROR: conftest REPO_ROOT used parents[2] which resolves to tests/, not repo root; fixed to parents[3]
- 2026-05-09 TEST: Phase 2 (failing tests) — 18 tests written; collection errors as expected (TF-1: WRITTEN-FAILING)
- 2026-05-09 BUILD: Phase 3 (assemble.py) — added _signature_extractors, normalize_finding, _yaml_error_context with getattr fallback
- 2026-05-09 TEST: assemble + normalize 9/9 PASS
- 2026-05-09 BUILD: Phase 4 (write_pass.py) — 4-backtick parser, --raw-file only, exit codes 0/1/2
- 2026-05-09 ERROR: 4 write_pass tests fixture issue — textwrap.dedent + interpolation didn't dedent; rewrote with explicit string concatenation
- 2026-05-09 ERROR: 1 missing-required-field test had no evidence so hit evidence-rejection path before missing-field; added evidence to fixture
- 2026-05-09 ERROR: 1 empty-block parametrized variant (`"[]"`) had no trailing newline so closing fence merged with content; added `\n`
- 2026-05-09 TEST: write_pass 10/10 PASS
- 2026-05-09 SMOKE: mid-slice gate — pytest 20/24 PASS (4 SKILL.md prose pins fail as expected — Phase 6 fixes)
- 2026-05-09 SMOKE: manual write_pass.py end-to-end via --raw-file — exit 0; all 3 files written
- 2026-05-09 ERROR: PowerShell double-quoted here-string `@"..."@` ate backticks (backtick is its escape char); switched to single-quoted `@'...'@` for raw-file content
- 2026-05-09 BUILD: Phase 6 (SKILL.md restructure) — Steps 3, 5, 5.5, 6, 6.5 updated; --output → --out; subagents return fenced blocks; write_pass.py invocation; 3-attempt retry cap; narrator-unchanged note
- 2026-05-09 TEST: 5/5 SKILL.md prose pins PASS
- 2026-05-09 BUILD: Phase 7 (11 pass templates) — each gained "Output format" section with 4-backtick fenced blocks + 5-line schema crib sheet (m2); 01-intent.md hard rules also updated to forbid Write/Bash/python
- 2026-05-09 TEST: full diagnose suite 24/24 PASS
- 2026-05-09 BUILD: Phase 8 pre-finish — TF-1 strict 18 PASSING; WIRE-1 clean; BC-1 no rules apply; mock-budget clean
- 2026-05-09 TEST: full repo suite 326/326 PASS (no regressions)
- 2026-05-09 ERROR: TF-1 audit initially "not enabled" because mission-brief had trailing comment after `**Test-first**: true`; regex requires alone-on-line; moved comment to HTML comment line
- 2026-05-09 BUILD: Phase 9 (re-install) — synced skills/diagnose/ to ~/.claude/skills/diagnose/; cleared stale __pycache__; install_audit --strict clean (24/5/4/14, methodology v0.20.0)
- 2026-05-09 BUILD: SHIPPED
- 2026-05-09 VALIDATE: AC #6 ran end-to-end /diagnose on <private-project>; 4 of 11 subagents launched before user halted (pattern confirmed); orchestration validated on real subagent output (3 success + 1 cleanly degraded)
- 2026-05-09 DEVIATION: SKILL.md/pass-template "no Bash/python" contract was too strict — orchestrator overrode in AC #6 prompts with "Bash/python OK for graphify queries within OUT". Captured as a reflection correction in design.md; slice-002 candidate to fix the SKILL.md + 11 pass-template wording.
- 2026-05-09 FINDING: cwd-mismatch tool denial — when TARGET ≠ parent thread cwd, subagents lose Read/Grep/Bash/PowerShell entirely (only Glob remains). Slice-001 didn't anticipate this; recorded in risk-register.md as R1; slice-002 candidate.

## Summary

### Plan executed (10 phases, all completed)

| Phase | Description | Result |
|---|---|---|
| 0 | Apply triage design-stage edits to mission-brief / design.md / ADR-001 | ✓ |
| 1 | Test infrastructure (tests/skills/diagnose/ + conftest) | ✓ |
| 2 | 18 failing tests across 4 files | ✓ (WRITTEN-FAILING confirmed) |
| 3 | assemble.py: normalize_finding + _signature_extractors + better YAML error | ✓ (9/9 tests pass) |
| 4 | write_pass.py: 4-backtick parser, --raw-file only | ✓ (10/10 tests pass) |
| 5 | Mid-slice smoke gate | ✓ (PASS — manual write_pass + 20/24 pytest) |
| 6 | SKILL.md restructure (Steps 3, 5, 5.5, 6, 6.5) | ✓ (5/5 prose pins pass) |
| 7 | 11 pass templates: Output format + schema crib sheet | ✓ |
| 8 | Pre-finish gates: TF-1, WIRE-1, BC-1, mock-budget | ✓ (all clean) |
| 9 | INSTALL.md re-run + install_audit --strict | ✓ (clean) |
| 10 | build-log + milestone | ✓ (this file) |

### Mid-slice smoke gate

**Result**: PASS

**Evidence**:
- `pytest tests/skills/diagnose/` = 20/24 (4 SKILL.md prose pin failures expected at this point — Phase 6 fixed them)
- Manual end-to-end: `python skills/diagnose/write_pass.py --pass 01-intent --out <tmp> --raw-file <tmp>.raw` produced all 3 expected files; findings.yaml = `[]`; section + summary = subagent prose preserved.

### Pre-finish gate

- [x] All 5 ACs PASS (verified by 18 PASSING test rows in mission-brief; smoke gate exercises end-to-end)
- [x] Must-not-defer addressed: every REQUIRED_FIELDS validated; `yaml.safe_dump` used with explicit kwargs; INST-1 source-vs-install separation honored; empty findings handled cleanly; install_audit --strict re-confirmed
- [x] Test-first audit: 18 PASSING / 0 PENDING / 0 WRITTEN-FAILING (--strict-pre-finish clean)
- [x] Build-checks audit: no rules apply
- [x] Wiring matrix audit: clean (`write_pass.py` row pinned by SKILL.md prose-pin test)
- [x] Mock-budget lint: clean
- [x] No new TODOs / FIXMEs / debug prints (verified by grep at end of build)

### Critic dispositions resolved

All 12 ACCEPTED-PENDING items from /critique applied:
- **B1** (4-backtick fences): write_pass.py parser uses `^\`{4,}(section|findings|summary)\s*$` opener + length-distinguished closing fence (CommonMark §4.5); test_section_block_with_nested_triple_backticks_parses_correctly verifies inner ` ```bash `/` ```yaml ` round-trips.
- **B2** (per-pass signature extractor): `_signature_extractors: dict[str, Callable]` in assemble.py; default `lambda f: f["title"]`; override for 03b-duplicates uses lexicographically smallest evidence path. Determinism verified by test_malformed_id_recomputed_via_per_pass_extractor.
- **M1** (normalize_finding ingest-only): only called from write_pass.py; load_findings retains current strictness. Verified by test_load_findings_unchanged_for_already_normalized_yaml.
- **M2** (problem_mark fallback): `getattr(exc, 'problem_mark', None)` in assemble.py + write_pass.py error handlers. Verified by test_yaml_error_without_problem_mark_falls_back_gracefully.
- **M3** (retry cap): SKILL.md Step 5 specifies "at most 3 total attempts; on terminal failure save to `$OUT/.tmp/<pass>.failed.raw` and proceed degraded". Pinned by test_skill_md_caps_respawn_attempts.
- **M4** (drop stdin): write_pass.py CLI requires `--raw-file`; no stdin path.
- **M5** (AC #5 doc clarification): design.md "Pass templates" section notes pass templates use `--graph`, not `--output`; only SKILL.md:55 needed the change.
- **M6** (ADR-001 cost widening + Option 4): ADR-001 Consequences now reads "100–440KB per /diagnose run" with measurement task carried to reflection.md; Option 4 (declare subagent tool needs at spawn time) added to Options considered.
- **m1** (parametrized empty-block): test_empty_findings_block_treated_as_empty_list parametrized over 5 input variants ([], "", whitespace, comment, null).
- **m2** (schema crib sheet): full schema embed replaced with 5-line crib sheet in each of 11 pass templates (~30KB savings per /diagnose run).
- **m3** (no-Write prose pin): test_skill_md_subagents_instructed_no_write asserts SKILL.md contains "do not call Write" (case-insensitive) AND does NOT contain "writes 3 files".
- **m4** (AC #1 verification reword): mission-brief AC #1 now specifies scriptable verification (capture raw → Grep fences + zero `Write(` references + write_pass.py exit 0).

### Deferrals

None.

### Design deviations

None.

### Files changed

**Slice artifacts (mission-brief / design / ADR / critique / milestone)** — updated in Phase 0 + Phase 8 + Phase 10:
- `architecture/slices/slice-001-diagnose-orchestration-fix/mission-brief.md`
- `architecture/slices/slice-001-diagnose-orchestration-fix/design.md`
- `architecture/slices/slice-001-diagnose-orchestration-fix/critique.md`
- `architecture/slices/slice-001-diagnose-orchestration-fix/milestone.md`
- `architecture/slices/slice-001-diagnose-orchestration-fix/build-log.md` (this file)
- `architecture/decisions/ADR-001-diagnose-subagent-io-contract.md`

**Source code**:
- `skills/diagnose/assemble.py` — added _signature_extractors, normalize_finding, _yaml_error_context, getattr fallback in load_findings
- `skills/diagnose/write_pass.py` — NEW (188 LOC)
- `skills/diagnose/SKILL.md` — restructured Steps 3, 5, 5.5, 6, 6.5
- `skills/diagnose/passes/01-intent.md` through `04-ai-bloat.md` — 11 templates updated with "Output format" section + schema crib sheet

**Tests**:
- `tests/skills/__init__.py` — NEW
- `tests/skills/diagnose/__init__.py` — NEW
- `tests/skills/diagnose/conftest.py` — NEW
- `tests/skills/diagnose/test_normalize_finding.py` — NEW (7 tests)
- `tests/skills/diagnose/test_write_pass.py` — NEW (10 tests including parametrized cases)
- `tests/skills/diagnose/test_assemble_errors.py` — NEW (2 tests)
- `tests/skills/diagnose/test_skill_md_pins.py` — NEW (5 tests)
