# Slice 034: fix-tf1-audit-field-line-regex

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-7 (TF-1 audit field-line regex silently disables the gate on an annotated `**Test-first**: true`)
**Test-first**: true
<!-- BARE field-line intentional — DO NOT annotate this line with a trailing parenthetical.
     This slice fixes R-7, whose defect is that the CURRENTLY-INSTALLED buggy
     `tools/test_first_audit.py` silently default-offs on an annotated field-line.
     Until the fix lands, an annotated form here would make /build-slice Step 6
     silently bypass TF-1 on the very slice fixing it (R-7 recurrence N+2;
     slice-022 self-violation law / slice-033 lesson). Annotation lives in this
     HTML comment per the slice-031/033 documented remedy. -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`tools/test_first_audit.py` silently treats a genuinely test-first slice as "not enabled" whenever its `**Test-first**: true` field-line carries a trailing annotation — the idiomatic `/slice` mission-brief template form `**Test-first**: true  (per TF-1 — …)`. The `$`-anchored `_TEST_FIRST_FIELD_RE` (`tools/test_first_audit.py:54`) fails to match, `_detect_test_first_flag` returns False, and the audit exits 0 on the silent default-off path — bypassing the entire TF-1 gate. This slice hardens the field-line parsing so an annotated declaration engages the gate, and a present-but-malformed declaration fails *loudly* instead of silently, closing the latent gate-bypass that until now was caught only manually by the BC-PROJ-4 real-artifact gate run.

## Acceptance criteria

1. The repro test `tests/methodology/test_tf1_field_line_annotation_regression.py` (both functions) PASSES: an annotated `**Test-first**: true  (per TF-1 — …)` field-line is detected as test-first ENABLED, and `audit_brief_file` does not take the silent default-off path on such a brief.
2. No false-positive regression: a genuinely-absent `**Test-first**:` field still yields legitimate default-off (clean, exit 0, no violation); bare `**Test-first**: true` and `**Test-first**: false` keep their current correct detection.
3. No silent bypass on malformed input: a field-line that IS present but whose value/format is unparseable (e.g. `**Test-first**: maybe`, empty value) does NOT take the silent default-off path — it surfaces loudly (a violation, or an engaged gate), per the R-7 fix recommendation distinguishing "field absent" from "field present-but-broken".
4. Non-regression: the full `tests/methodology/test_test_first_audit.py` suite and the entire shippability catalog (including `--strict-pre-finish` and carry-over-exemption paths) stay green at `/validate-slice`.
5. R-7 is escalated to `retired` in `architecture/risk-register.md` with a slice-034 reference and a citation of the catalogued regression test as the durable guard.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_tf1_field_line_annotation_regression.py | test_detect_test_first_flag_honors_trailing_annotation | PASSING |
| 1 | integration | tests/methodology/test_tf1_field_line_annotation_regression.py | test_annotated_brief_does_not_silently_default_off | PASSING |
| 2 | unit | tests/methodology/test_test_first_audit.py | test_absent_field_stays_default_off_clean | PASSING |
| 2 | unit | tests/methodology/test_test_first_audit.py | test_present_false_field_is_not_malformed | PASSING |
| 3 | unit | tests/methodology/test_test_first_audit.py | test_present_but_malformed_field_is_loud_not_silent | PASSING |
| 3 | unit | tests/methodology/test_test_first_audit.py | test_malformed_suffix_value_is_loud_not_silent | PASSING |
| 4 | regression | tests/methodology/test_test_first_audit.py | (full existing module — non-regression) | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_48_0_tffl_1_entry_present_in_repo_and_installed | PASSING |
| 5 | unit | tests/methodology/test_tf1_field_line_annotation_regression.py | test_r7_retired_in_risk_register | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Annotated field-line detected as enabled | `pytest tests/methodology/test_tf1_field_line_annotation_regression.py -q` → 2 PASS (was 2 FAIL) |
| 2 | Absent / bare forms non-regressed | `pytest tests/methodology/test_test_first_audit.py -q` green; new absent-stays-clean test PASS |
| 3 | Malformed field is loud, not silent | New test: a `**Test-first**: maybe` brief produces a non-zero violation / non-silent signal (assert NOT the "not enabled" silent message + exit 0) |
| 4 | Whole catalog non-regressed | `/validate-slice` Step 5.5 — shippability 34/34 (or current count) PASS incl. row #34 now green |
| 5 | R-7 retired | `grep -A3 '## R-7' architecture/risk-register.md` shows `**Status**: retired` + slice-034 reference; `tools.risk_register_audit --filter-status open` no longer lists R-7 |

## Must-not-defer

- [ ] The fix must NOT widen the regex so loosely that (a) a non-field line (prose containing "Test-first: true" mid-sentence) is mistaken for the field — keep the `^`-anchor on the `**Test-first**:` bold token; AND (b) a malformed *suffix* value is silently accepted — the boolean must be a standalone token (whitespace / `(` / EOL after it), so `**Test-first**: false-positive` / `true.` / `false; note` fall through to the §2 malformed branch, NOT silent default-off (per /critique M1 — this is itself the R-7 class).
- [ ] Dogfood / self-violation guard: this slice's own mission-brief `**Test-first**` field stays the BARE form (no trailing annotation) until the fix lands; verify at `/build-slice` Step 6 by reading the real `test_first_audit.py` output on THIS brief (BC-PROJ-4 — the gate that is the only thing that has ever caught R-7).
- [ ] Methodology-changelog + atomic PMI-1 propagation: a brief silently-passed yesterday now engages the gate → behavior change → `methodology-changelog.md` **v0.48.0** entry under minted RULE-ID **`TFFL-1`** (refines TF-1 in place, supersedes nothing; EOL-DRIFT-1↔CAD-1 lineage precedent) + `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-sync `~/.claude/methodology-changelog.md` (4-part atomic bump); INST-1 lockstep (no new tool). Bound entry-pin `test_v_0_48_0_tffl_1_entry_present_in_repo_and_installed` + canonical-phrase pin in the entry body (per /critique-review M-add-1; avoids the slice-032 DEVIATION-1 no-rule-lineage class).
- [ ] CAD-1 / mini-CAD: confirm no `agents/*.md` or guarded `SKILL.md` content drift introduced (this slice should touch none).
- [ ] Error path: the "present-but-malformed" branch must emit an attributed, actionable message (which brief, which line, what's wrong) — not a bare stack trace or a silent skip.

## Out of scope

- Re-homing or redesigning the TF-1 audit beyond the field-line parsing fix (no broader refactor of `run_audit` / table validation).
- R-8 (Step-5.5 catalog runner `;`-split / per-segment-backtick contract) — separate open risk, separate slice.
- R-6 (BRANCH-1 numeric-NNN regex vs letter-suffixed split-slice folders) — separate concern.
- Auditing every *other* audit tool for analogous `$`-anchored field-line fragility — note as a follow-up watch-list candidate if the pattern generalizes; not this slice.

## Dependencies

- Repro (BFRD-1 prerequisite): `tests/methodology/test_tf1_field_line_annotation_regression.py` — established by `/repro` 2026-05-17, currently FAILING with `AuditResult(test_first_enabled=False)`; catalogued `architecture/shippability.md` row #34.
- Code under change: `tools/test_first_audit.py` (`_TEST_FIRST_FIELD_RE` L54; `_detect_test_first_flag` L138–144; `run_audit` default-off path L289; `_format_human` L443–444).
- Risk register: [[risk-register#R-7]] — this slice retires it.
- Prior context: slice-031 / slice-033 (R-7 discovery + N+1 recurrence; bare-field-line + HTML-comment remedy; BC-PROJ-4 as the structural backstop).

## Mid-slice smoke gate

At ~50% of build, run:
```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_tf1_field_line_annotation_regression.py -q
```
Expected: both repro functions PASS (the core fix landed). Then run the audit against THIS slice's own brief:
```
<HOME>/.claude/.venv/Scripts/python.exe -m tools.test_first_audit architecture/slices/slice-034-fix-tf1-audit-field-line-regex
```
Expected: reports test-first ENABLED with the plan table (NOT "not enabled"). If either fails: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (incl. bare-field-line dogfood verified via real audit output, and 4-part atomic version bump)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] R-7 escalated to `retired`; `tools.risk_register_audit --filter-status open` no longer returns R-7
