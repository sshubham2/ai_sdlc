# Slice 005: add-bc-1-keyword-precision

**Mode**: Standard
**Risk tier**: low — modifies BC-1's keyword-applicability matcher in `tools/build_checks_audit.py`; no auth / contracts / data model / migrations / multi-device / external integrations / security-sensitive paths.
**Critic required**: false (low tier, no mandatory triggers). Voluntary Critic strongly recommended — slice-001 + slice-002 + slice-003 + slice-004 are N=4/4 paid off on cross-cutting low-tier slices, and 2 of 4 (slice-003 m1 false-PASS warning + slice-004 B1 fatal catch) caught design-stage failures that would have failed at build time. This slice is the 5th consecutive cross-cutting tooling slice; voluntary Critic ROI heuristic continues to apply.
**Estimated work**: <1 day (~2–3 hours)
**Risk retired**: none in `risk-register.md`. Addresses a confirmed tooling-precision pattern surfaced in slice-003 reflection ("BC-1 trigger-keyword false-positive precision issue") and re-confirmed in slice-004 reflection ("BC-1 trigger-keyword false-positive recurs — N=2"). The aggregated lessons in `slices/_index.md` flag this slice as overdue: *"BC-1 trigger-keyword precision is overdue; word-boundary or context-aware matching would silence the noise that's now firing every slice."*

**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`tools.build_checks_audit._rule_applies` matches a rule's `Trigger keywords` against the slice's `mission-brief.md` + `design.md` text using a bare case-insensitive substring check (`if kw in haystack`). This produces false positives whenever a trigger keyword appears in a semantically-unrelated context. The N=2 confirmed pattern: BC-PROJ-2 / BC-GLOBAL-1 (LLM-fence parsing rules; trigger keyword `parse`) fired on slice-003 (the word `parse` appeared in `parse_declared_deps` / `tomllib`-parses / `ast`-parses contexts) and again on slice-004 (the word `parses` appeared in `_RISK_HEADING_RE`-parses contexts). Both slices deferred-with-rationale; the noise drowns out real signal and trains the builder to ignore BC-1 surfacing.

This slice teaches the BC-1 trigger-keyword matcher to distinguish domain-relevant matches from semantically-unrelated occurrences, **silencing the recurring false-positive on slice-003 and slice-004's mission-briefs without suppressing legitimate matches** (e.g., a slice that genuinely discusses parsing LLM agent output should still trigger BC-PROJ-2 / BC-GLOBAL-1). The exact precision mechanism (word-boundary regex, multi-keyword conjunction, designated domain-anchor keywords, per-rule `Trigger requires: N` schema field, or a hybrid) is a design decision deferred to `/design-slice`.

## Acceptance criteria

1. **Slice-003 backtest clean**: re-running the BC-1 audit against `architecture/slices/archive/slice-003-add-val-1-imports-allowlist/` (with `--no-carry-over` to bypass the mtime exemption) produces **0 applications** of BC-PROJ-2 (project) and **0 applications** of BC-GLOBAL-1 (global). Today the same invocation fires both rules due to bare-substring matches on `parse`.

2. **Slice-004 backtest clean**: re-running the BC-1 audit against `architecture/slices/archive/slice-004-fix-rr1-audit-docstring-or-regex/` (with `--no-carry-over`) produces **0 applications** of BC-PROJ-2 and **0 applications** of BC-GLOBAL-1. Today the same invocation fires both due to bare-substring matches on `parse` / `parses`.

3. **Positive case preserved**: a synthetic mission-brief.md that legitimately discusses LLM-fence parsing (e.g., **"Parse the LLM agent's fenced output for nested triple-backtick code-block sections"** — note the canonical anchor words `llm` and `code-block` appear as bare word-boundary tokens; `fence` matches via `code-block` redundancy even though `fenced` itself doesn't word-boundary-match `\bfence\b`) DOES trigger BC-PROJ-2 and BC-GLOBAL-1. The precision mechanism doesn't suppress legitimate matches. Per Critic B2 (slice-005): the canonical example and the design.md empirical-verification table MUST agree byte-for-byte on the test string.

4. **Build-checks schema documentation pin (TWO surfaces)**: the precision mechanism introduces TWO contract surfaces that BOTH require schema-description prose updates and BOTH require prose-pin tests in BOTH `architecture/build-checks.md` AND `~/.claude/build-checks.md`:
   - (a) the **`Trigger anchors:` field name** — pinned by a literal substring `Trigger anchors`
   - (b) the **word-boundary semantics** — pinned by a literal substring identifying word-boundary matching, e.g., `word-boundary` or `whole-word` (exact substring locked at /design-slice; per Critic M3, a single canonical phrase that appears in both files).

   (Per slice-002 + slice-003 + slice-004 pattern: methodology-tooling slices add prose-pin tests for every contract surface they change. Per Critic M3 (slice-005): two new surfaces means two pins, not one.)

(Note: the original AC #4 — "no regression in existing 18 BC-1 tests" — was demoted from the numbered-AC list to the verification-plan + must-not-defer track per slice-002+slice-004 lessons-learned. Surfaced at /build-slice T7 by `tools/test_first_audit.py --strict-pre-finish` which refused because TF-1 had no row for it. Regression-guard invariants live outside TF-1 to avoid the meta-AC anti-pattern. The numbered ACs are now 1, 2, 3, 4 — schema-pin became AC #4 instead of AC #5.)

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | integration | tests/methodology/test_build_checks_audit.py | test_slice_003_archive_backtest_no_bc_proj_2_or_global_1_applications | PASSING |
| 2 | integration | tests/methodology/test_build_checks_audit.py | test_slice_004_archive_backtest_no_bc_proj_2_or_global_1_applications | PASSING |
| 3 | unit | tests/methodology/test_build_checks_audit.py | test_legitimate_llm_fence_brief_still_triggers_bc_proj_2_and_global_1 | PASSING |
| 4 | unit | tests/methodology/test_build_checks_audit.py | test_build_checks_schema_documents_trigger_anchors_field_name | PASSING |
| 4 | unit | tests/methodology/test_build_checks_audit.py | test_build_checks_schema_documents_word_boundary_semantics | PASSING |
| migration | unit | tests/methodology/test_build_checks_audit.py | test_migrated_rules_have_expected_anchors | PASSING |
| validation | unit | tests/methodology/test_build_checks_audit.py | test_anchor_not_in_keywords_yields_violation | PASSING |

**Notes:**
- AC #4 (no regression in existing 18 BC-1 tests) is a regression-guard invariant, not a behavior-delivery AC; per slice-002 + slice-004 lessons it lives in the verification-plan + must-not-defer track, not in the TF-1 plan.
- The Critic explicitly asked at slice-004 (B1 + slice-003 m1 false-PASS) for empirical verification at design-time. /design-slice MUST run the proposed precision mechanism against slice-003 + slice-004 mission-briefs literally before locking the design — see Verification plan for the empirical-verification gate.
- Per slice-003 lesson (TF-1 false-PASS pitfall), each test's PENDING → WRITTEN-FAILING transition must fail in a way that distinguishes "fix not applied" from "fix doesn't exist". For the backtest tests, the failure signature is "rule applied = True" pre-fix vs "rule applied = False" post-fix on the same archive folder; for the positive-case test the signature is "rule applied = True" both pre- and post-fix (regression-guard shape).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Slice-003 backtest clean | `test_slice_003_archive_backtest_no_bc_proj_2_or_global_1_applications` invokes `audit_slice` against the slice-003 archive folder with `skip_if_carry_over=False`; asserts BC-PROJ-2 not in `applicable` AND BC-GLOBAL-1 not in `applicable`. Manual smoke at validate-time: real-CLI invocation `$PY -m tools.build_checks_audit --slice architecture/slices/archive/slice-003-add-val-1-imports-allowlist --no-carry-over --json` from project root; observe BC-PROJ-2 / BC-GLOBAL-1 absent from `applicable` array. |
| 2 | Slice-004 backtest clean | `test_slice_004_archive_backtest_no_bc_proj_2_or_global_1_applications` mirrors test #1 against slice-004 archive folder. Manual smoke: real-CLI invocation against slice-004 archive folder. |
| 3 | Positive case preserved | `test_legitimate_llm_fence_brief_still_triggers_bc_proj_2_and_global_1` constructs a tmp slice with mission-brief.md containing a domain-coherent LLM-fence sentence; asserts BC-PROJ-2 + BC-GLOBAL-1 both in `applicable`. |
| 4 | No regression on existing 18 BC-1 tests (regression-guard invariant per Critic-equivalent demotion at slice-002 + slice-004 lessons) | Full `pytest tests/methodology/test_build_checks_audit.py` passes 18+/18+ rows including `test_keyword_match_via_mission_brief`, `test_glob_applies_to_matches_changed_files`, `test_always_true_rule_always_applies`, `test_global_and_project_checks_combine`. |
| 5 | Schema documentation pin | `test_build_checks_schema_documents_precision_mechanism` reads `architecture/build-checks.md` AND `~/.claude/build-checks.md` (or, if `~/.claude` not present in test environment, only the project copy with a skip-marker); asserts the canonical precision-mechanism documentation substring appears. The exact substring is locked at /design-slice time and pinned by this test. |
| **Empirical verification gate (per slice-004 B1 lesson)** | Before /critique submits design.md, run the proposed precision algorithm against slice-003 + slice-004 mission-brief.md text LITERALLY (Python one-liner, ~30 seconds). Confirm: (a) BC-PROJ-2 / BC-GLOBAL-1 do NOT fire on those texts, AND (b) BC-PROJ-1 (the subagent rule) STILL fires on slice-001's mission-brief (legitimate match). Per slice-004's "empirical verification at design-time costs ~30 seconds and saves entire slice cycles" lesson — N=3 across slices now, treat as standard discipline. |

## Must-not-defer

- [ ] Backwards-compatibility: existing `architecture/build-checks.md` and `~/.claude/build-checks.md` content (BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1) must parse without violations after the change. If a new schema field is added, existing rules without it MUST behave as if the new field had its safe default (= old behavior preserved on rules that don't opt in).
- [ ] Carry-over exemption (`_slice_is_carry_over`) preserved — new precision logic must not bypass NFR-1.
- [ ] Glob-applicability path unaffected — precision logic applies ONLY to the `Trigger keywords` branch; `Applies to: <globs>` and `Applies to: always: true` paths remain unchanged.
- [ ] No regression in existing 18 BC-1 tests in `test_build_checks_audit.py` — full module passes after changes.
- [ ] **BC-1 self-application produces ONLY expected meta-references on slice-005's own files** (per Critic B1 — slice-005). Slice-005's mission-brief.md + design.md are ABOUT BC-PROJ-1 / BC-PROJ-2 / BC-GLOBAL-1 (the rule definitions), so meta-references to their anchor keywords (`subagent`, `fan-out`, `fence`, `code-block`, `llm`) WILL fire all three rules under both old and new logic. This is **expected and not a regression** — the slice's domain is defining/editing those rules. Item is satisfied if: (a) the rules that fire on slice-005's files are exactly {BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1} (no fourth rule appearing); (b) build-log.md at T-final enumerates them with the rationale "expected meta-reference fire — slice domain is rule definition, not LLM-fence parsing"; (c) defer-with-rationale at pre-finish gate. Per Critic B1, the previous wording ("no false positives... must NOT regress") was self-contradictory and unverifiable.
- [ ] Input validation on any new `build-checks.md` schema field (per slice-003 + slice-004 pattern: methodology audits enforce strict CLI / schema validation; lenient API only when justified by a documented asymmetry).

## Out of scope

- **Auto-detecting recurring patterns from `lessons-learned.md`** to propose new build-checks rules (deferred to `/critic-calibrate` v2 extension per `methodology-changelog.md` v0.10.0 BC-1 v1 limitations).
- **Brace-expansion / negation / `?` single-char globs** in `Applies to:` (deferred per BC-1 v1 limitations).
- **`Trigger keywords` migration script** that converts existing rule trigger-keyword lists to the new schema if a new schema field is introduced — manual one-time migration of 3 existing rules (BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1) is in scope; an automated migration tool is not.
- **`/critic-calibrate` invocation** — this slice does NOT run `/critic-calibrate`; that is a separate next-slice candidate (the ≥5-archived-slices threshold trips when slice-005 archives, making it the strongest candidate for slice-006).
- **Promoting BC-1 to v0.21.x in `methodology-changelog.md`** — the change is precision-additive (existing rules continue to fire on legitimate matches; only false positives are silenced) and within the existing v0.10.0 BC-1 contract; `/reflect` decides whether to log a changelog bullet.
- **`add-csp-1-docstring-or-regex`** — sibling tooling slice flagged in slice-004 deferrals (`tools/cross_spec_parity_audit.py` has the IDENTICAL bug pattern as slice-004's fix). Independent of this slice; carries forward to slice-006+ candidate list.

## Dependencies

- Prior slices: [[slice-003-add-val-1-imports-allowlist]] (first false-positive occurrence; introduced "Defer-with-rationale is the right disposition" pattern), [[slice-004-fix-rr1-audit-docstring-or-regex]] (second occurrence; promoted slice to "overdue" status in aggregated lessons)
- Vault refs: [[tools/build_checks_audit.py]] (`_rule_applies` is the modification target), [[architecture/build-checks.md]] (project rules; potentially updated schema), [[~/.claude/build-checks.md]] (global rules; potentially updated schema), [[tests/methodology/test_build_checks_audit.py]] (test home)
- Risk register: none directly retired (this is a methodology-precision fix, not a risk retirement)
- Methodology: `methodology-changelog.md` v0.10.0 (BC-1 origin; the v1 limitations explicitly contemplated this kind of precision improvement as a v2 enhancement)

## Mid-slice smoke gate

At ~50% of build (after the precision logic is implemented in `_rule_applies` + at least the 2 backtest tests are passing, before the schema-documentation test is wired), run from project root (single line — works in PowerShell AND Bash; per slice-001 cross-shell lesson, avoid Bash `\` continuation in commands the user may copy-paste):

```
$PY -m tools.build_checks_audit --slice architecture/slices/archive/slice-003-add-val-1-imports-allowlist --no-carry-over --json
```

Expected: the `applicable` array does NOT contain `BC-PROJ-2` or `BC-GLOBAL-1`. Exit code 0.

If this fails: STOP. Either the precision logic isn't reaching `_rule_applies`, or the algorithm is too aggressive (or too lax). Diagnose by comparing the slice-003 mission-brief text against the precision rule's expected behavior; re-running with `--json` reveals which rules ARE applying and why.

Re-run the same command on slice-004 archive folder to cross-verify. Both should be clean.

## Pre-finish gate

- [ ] All 4 ACs PASS with evidence in `validation.md` (AC #4 invariant tracked in regression-guard track per Must-not-defer; ACs #1, #2, #3, #5 carry their TF-1 rows)
- [ ] Must-not-defer list fully addressed (6 items)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes after final cleanup (no regression on either slice-003 or slice-004 backtest)
- [ ] Full `tests/methodology/test_build_checks_audit.py` test suite green (no regression on existing 18 tests; new tests pass)
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes — all 4 test-first rows PASSING
- [ ] No new TODOs / FIXMEs / debug prints in `tools/build_checks_audit.py` or `tests/methodology/test_build_checks_audit.py`
- [ ] Shippability catalog regression check (run all 4 entries in `architecture/shippability.md`)
- [ ] **BC-1 self-application on slice-005's own files produces exactly {BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1}** (per Critic B1): re-run BC-1 audit on slice-005's OWN mission-brief.md + design.md with `--no-carry-over`. Expected: those three rules apply (meta-reference fire — slice's own files mention the rules' anchor keywords as meta-discussion). Build-log.md at T-final captures the rule list + the meta-reference rationale + defer-with-rationale disposition. NOT a false positive; NOT a regression. If a fourth rule appears, that IS a regression.
