# Slice 004: fix-rr1-audit-docstring-or-regex

**Mode**: Standard
**Risk tier**: low — single-file tooling cleanup in `tools/risk_register_audit.py`; no auth / contracts / data model / migrations / multi-device / external integrations / security-sensitive paths.
**Critic required**: false (low tier, no mandatory triggers). Voluntary Critic recommended — 4th consecutive low-tier slice touching tooling-conformance, the exact miss-class confirmed at N=3 in slice-003 reflection. Voluntary Critic ROI is now 3/3 across slice-001 + slice-002 + slice-003.
**Estimated work**: <1 day (~30–60 minutes)
**Risk retired**: none in `risk-register.md`. Addresses a confirmed tooling-conformance gap surfaced in slice-002 reflection: `tools/risk_register_audit.py`'s docstring and inline regex comment both show `## R-NN -- <title>` (double-dash) as a canonical heading format, but the actual regex `_RISK_HEADING_RE` (`r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$"`) is a single-character class — only single em-dash `—` or single hyphen `-` matches. A `--` heading silently produces 0 risks. Slice-002 hit this exact bug at format-conversion time and recovered by switching to em-dash; slice-003's reflection ranked the cleanup as a clear next-slice candidate.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`tools/risk_register_audit.py` claims (in its docstring at L17–L27 "Format" section AND in the inline comment at L55 just above the regex) that headings of the form `## R-NN -- <title>` are valid. The regex accepts only single-character separators between the ID and the title — `—` or `-`, not `--`. The contradiction silently produces 0 risks when a user follows the documentation literally. This slice eliminates the contradiction by aligning all three sources (docstring "Format" section, inline regex comment, regex behavior) on a single source of truth and adds a regression-guard test that prevents future drift in either direction. The exact path (widen the regex to also accept `--` vs. fix the documentation to match the regex's strictness vs. some hybrid) is a design decision deferred to `/design-slice`.

## Acceptance criteria

1. **Docstring–regex consistency**: every heading-shaped example shown in `tools/risk_register_audit.py`'s module docstring (currently the "Format" section at L17–L27) successfully matches `_RISK_HEADING_RE` after this slice. No example in the docstring describes a format the regex doesn't actually accept. Examples MUST use a digit-bearing risk ID (e.g., `R-1`, `R-12`) — not letter placeholders like `R-NN` — because the regex requires `R-?\d+`. *(Critic B1: empirically verified `## R-NN — title` returns NO-MATCH; `## R-1 — title` returns MATCH.)*
2. **Inline-comment–regex consistency**: every heading-shaped example shown in the inline comment immediately above `_RISK_HEADING_RE` (currently L55) successfully matches `_RISK_HEADING_RE` after this slice. The extraction logic catches both `"..."`-quoted (Python string literal convention) AND `` `...` ``-quoted (markdown code-span convention) example shapes. *(Critic M3 robustness fix: covers more realistic future drift cases than `"..."` alone.)*
3. **risk-register.md schema-description consistency**: `architecture/risk-register.md`'s opening description prose (currently L3) shows the canonical heading shape using `_RISK_HEADING_RE`-matching examples. Today it says `## R-N -- <title>` (double-dash, doesn't match); after this slice it says a digit-bearing example with the canonical em-dash separator. *(Critic M2: this is the third documentation surface — the user-facing one. Slice fixes all three or none.)*

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_risk_register_audit.py | test_docstring_format_examples_match_actual_regex | PASSING |
| 2 | unit | tests/methodology/test_risk_register_audit.py | test_inline_regex_comment_examples_match_actual_regex | PASSING |
| 3 | unit | tests/methodology/test_risk_register_audit.py | test_risk_register_md_schema_description_examples_match_actual_regex | PASSING |

Test-first authoring discipline (per slice-003's TF-1 false-PASS lesson): each test must fail BEFORE implementation in a way that distinguishes "fix not applied" from "fix doesn't exist". For all 3 tests, that means asserting on the SPECIFIC heading examples currently in their respective documentation surfaces (which today contain `--`); the tests should literally fail because today's `--`-style examples don't parse through `_RISK_HEADING_RE`.

(Per Critic M1: the original AC #3 — "existing R-1/R-2 parses unchanged" — was a regression-guard invariant, not a behavior-delivery AC; demoted to verification-plan + must-not-defer entry below. The slice's invariant is preserved without burdening TF-1's PENDING → WRITTEN-FAILING → PASSING tracker with a row that can't legitimately reach WRITTEN-FAILING.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Docstring–regex consistency | `test_docstring_format_examples_match_actual_regex` reads `inspect.getdoc(tools.risk_register_audit)`, extracts every stripped line that begins with `## R-`, runs each through `_RISK_HEADING_RE.match(...)`, asserts each matches. Failing pre-fix because today's `## R-NN -- <title>` example doesn't match (NN is not `\d+`; `--` is two characters). |
| 2 | Inline-comment–regex consistency | `test_inline_regex_comment_examples_match_actual_regex` reads `tools/risk_register_audit.py` source, walks backward from `_RISK_HEADING_RE = re.compile(...)` over consecutive `#`-prefixed lines, extracts every `"..."`-quoted AND `` `...` ``-quoted (markdown code-span) heading shape, runs each through `_RISK_HEADING_RE.match(...)`, asserts each matches. Test docstring explicitly notes that unquoted prose examples (e.g., `# Also accepts ## R-1 — title`) silently bypass coverage — known coverage gap acknowledged for future hardening. |
| 3 | risk-register.md schema-description consistency | `test_risk_register_md_schema_description_examples_match_actual_regex` reads `architecture/risk-register.md`, scans the opening description prose (lines before first `## R-` heading) for `` ` ``-quoted heading-shape examples, extracts each via `re.findall(r'\`(## R-[^\`]+)\`', text)`, asserts each matches `_RISK_HEADING_RE`. Failing pre-fix because today's L3 contains `` `## R-N -- <title>` `` (single `R-N` is also problematic since `N` isn't `\d+`, AND `--` is two characters — both reasons fail). |
| Regression-guard (not test-first) | Backwards compatibility | A non-AC invariant test `test_slice_004_no_regression_in_existing_risk_register` (in `tests/methodology/test_risk_register_audit_real_file.py`) calls `tools.risk_register_audit` on `architecture/risk-register.md` and asserts R-1.score=6/band=high + R-2.score=2/band=low. This is a regression-guard, NOT a TF-1 row — the test passes from creation (no behavior change in this slice means no transition through WRITTEN-FAILING). Lives outside the test-first plan per Critic M1. Manual smoke at validate-time: re-run `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --sort score --top 5` and compare against the slice-003 baseline output. |

## Must-not-defer

- [ ] **No regression in R-1/R-2 parsing** — verified by the regression-guard test `test_slice_004_no_regression_in_existing_risk_register` in `tests/methodology/test_risk_register_audit_real_file.py`. R-1 must still return score=6/band=high; R-2 must still return score=2/band=low. *(Demoted from original AC #3 per Critic M1 — invariant assertion, not behavior-delivery; lives outside TF-1 plan.)*
- [ ] **risk-register.md L3 schema-description prose** updated to use a digit-bearing canonical heading example with em-dash separator. The actual R-1 / R-2 entries below it remain untouched (they already use em-dash with digits; verified). *(Per Critic M2: third documentation surface; in-scope this slice.)*
- [ ] Existing `tests/methodology/test_risk_register_audit.py` test suite continues to pass without modification (verify after change; capture pre-slice baseline)
- [ ] If the design narrows toward "widen regex": a deprecation-style hint should still surface for users who unknowingly use `--` (avoid silent acceptance of the format we're trying to avoid making canonical) — concrete shape decided by `/design-slice`
- [ ] `--warn-legacy` flag's "table-format detection" path (per the docstring at L29–L31) is unaffected — the slice's changes apply only to the H2-structured heading regex, not the legacy-table detection regex

## Out of scope

- Migrating any existing `--`-style risk-register entries (none exist; slice-002 already migrated R-1, R-2 to em-dash)
- Changes to other RR-1 fields (Likelihood, Impact, Status, etc.) or their parsing
- Changes to legacy-table-row detection (`_LEGACY_ROW_RE`)
- Changes to other audits (BC-1, TF-1, WIRE-1, TRI-1, VAL-1) that use similar field-line patterns — RR-1's regex is independent
- **`tools/cross_spec_parity_audit.py` (CSP-1) has the IDENTICAL bug class** — its docstring at L21 shows `## REQ-NN -- <title>` and inline comment at L67 shows `"## TM-NN -- title" / "## REQ-NN -- title" / "## NFR-NN -- title"`, while its regex at L69 is the same `[—\-]` single-character class. **Future slice candidate**: `fix-csp-1-docstring-or-regex` mirroring slice-004's pattern. Not addressed here per Critic m2 (kept slice scope tight; flagged for follow-up).
- Bumping RR-1 to a new minor version in `methodology-changelog.md` — slice's changes are cosmetic/clarifying for the audit's documentation, not a semantic change to the rule. `/reflect` decides whether to log a v0.20.x changelog bullet
- Adding new risk-heading format variants beyond what slice-004's design narrows down (no `==` separator, no other novelty)
- Hardening AC #2's extraction logic against ALL realistic future drift (e.g., unquoted prose examples in inline comments, multi-block comments separated by blank lines). Per Critic M3: the slice covers backtick-quoted + double-quoted shapes; unquoted prose is a documented coverage gap, not silently ignored. Tightening further is a follow-on if drift recurs.

## Dependencies

- Prior slices: [[slice-002-fix-diagnose-contract-and-cwd-mismatch]] (introduced RR-1 schema migration; surfaced this bug; risk-register.md migrated to em-dash there)
- Vault refs: [[tools/risk_register_audit.py]] (the only file modified), [[tests/methodology/test_risk_register_audit.py]] (existing tests; new tests added), [[tests/methodology/test_risk_register_audit_real_file.py]] (existing real-file integration test; new regression-guard test added)
- Risk register: none directly retired
- Methodology: `methodology-changelog.md` v0.12.0 (RR-1 origin)

## Mid-slice smoke gate

At ~50% of build (after the new failing tests are written + the chosen fix path is partially applied), run from project root (single-line; PowerShell- and Bash-compatible, per slice-001 + slice-003 cross-shell lesson):

```
$PY -m pytest tests/methodology/test_risk_register_audit.py tests/methodology/test_risk_register_audit_real_file.py --no-header -q
```

Expected: at this midpoint, the 3 NEW tests transition from FAILING (pre-fix) toward PASSING. Existing tests in both files continue to PASS (no regression).

If this fails: STOP. Diagnose whether the chosen fix path is creating a new regression in existing tests, OR whether one of the new test assertions itself needs revision.

Cardinal real-CLI smoke (per slice-003 lesson — pytest passing isn't enough):

```
$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --sort score --top 5
```

Expected: byte-identical JSON output to today's baseline (R-1 + R-2 with their current scores). If output diverges, the design's fix path inadvertently changed parsing behavior.

## Pre-finish gate

- [ ] All 3 ACs PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (4 items)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression after final cleanup)
- [ ] Full `tests/methodology/test_risk_register_audit.py` test suite green
- [ ] Full `tests/methodology/test_risk_register_audit_real_file.py` test suite green
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes — all 3 test-first rows PASSING
- [ ] No new TODOs / FIXMEs / debug prints in `tools/risk_register_audit.py`
- [ ] Shippability catalog regression check (run all entries in `architecture/shippability.md` — slice-001 + slice-002 + slice-003 critical paths)
