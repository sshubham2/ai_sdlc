# Critique: Slice 004 fix-rr1-audit-docstring-or-regex

**Critic reviewed**: mission-brief.md, design.md, ADR-003-rr1-fix-docs-not-regex.md
**Date**: 2026-05-10
**Result**: CLEAN (post-triage; all 6 findings ACCEPTED-FIXED)
**Voluntary**: yes — risk-tier=low, critic-required=false; user invoked `/critique` anyway, consistent with slice-001 + slice-002 + slice-003 voluntary-Critic pattern (4th consecutive low-tier slice using voluntary Critic).

## Summary

Critic returned **1 BLOCKER, 3 MAJORS, 2 MINORS**. The blocker is fatal and a real cross-cutting-conformance miss-class catch (N=4 if treated as such): the proposed canonical examples used `R-NN` (letter placeholder), but the regex requires `R-?\d+` (digits) — empirically verified that `## R-NN — title` returns NO-MATCH, so the slice's own AC #1 + AC #2 tests would fail after the fix landed. Plus three substantial majors: AC #3 was an invariant-assertion meta-AC (slice-002 lessons-learned violation; should be demoted from TF-1 plan); a third documentation surface (`architecture/risk-register.md:3`) was missing from scope; and the AC #2 extraction logic only caught `"..."`-quoted shapes, missing markdown-convention `` `...` `` shapes. Two minors: ADR-003 reversibility wording papered over the documentation-precedent cost; CSP-1 audit has the identical bug class (out-of-scope for this slice but worth flagging).

**Fourth consecutive voluntary-Critic ROI confirmation** — N=4/4 paid off. The blocker (B1) alone would have caused slice-004's TF-1 strict gate to fail at /build-slice T5 (first run of new tests). All 6 findings ratified ACCEPTED-FIXED; mission-brief.md / design.md / ADR-003 updated before triage.

## Findings

### Blockers (must address before /build-slice)

#### B1: Proposed canonical examples `## R-NN — <title>` and `"## R-NN — title"` do not match `_RISK_HEADING_RE`

- **Claim under review**: design.md §1 "After" originally specified `## R-NN — <title>` as the canonical docstring example; design.md §2 "After" specified `"## R-NN — title"` and `"## R-NN - title"` as the inline-comment quoted examples; ADR-003 Decision section originally said "the docstring's 'Format' section shows `## R-NN — <title>` (em-dash) as canonical".
- **Issue**: `_RISK_HEADING_RE = re.compile(r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$")` requires `R-?\d+` — R, an optional dash, and one or more **digit** characters. The placeholder `NN` is two **letter** characters (uppercase N), not digits. **Empirically verified** at /critique time: `re.match(...)` against `## R-NN — title` and `## R-NN — <title>` returns `None`; against `## R-1 — title`, `## R-12 — title`, and `## R-1 - title` returns MATCH. AC #1's extraction `[line.strip() for line in docstring.splitlines() if line.strip().startswith("## R-")]` would extract the indented `## R-NN — <title>` example after `inspect.getdoc()` dedent, then the test asserts `_RISK_HEADING_RE.match(heading)` — which returns None. AC #1 fails post-"fix". AC #2 fails identically because the inline-comment quoted examples extract via `re.findall(r'"(## R-[^"]+)"', ...)` and run through the same regex. The slice as designed would land in a state where its own newly-added tests fail — TF-1 strict pre-finish refuses; the slice exists to fix the docstring/regex contradiction and would re-introduce it on Day 1.
- **Evidence**: empirical verification at /critique-time via `python -c "import re; r = re.compile(r'^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$'); print(r.match('## R-NN — title'))"` returns `None`. Against `## R-1 — title` returns a match object. Source: `tools/risk_register_audit.py:56` (regex; unchanged by this slice).
- **Proposed fix**: replace `R-NN` with `R-1` in all "After" examples in design.md (§1 docstring, §2 inline comment, ADR-003 Decision section). Use a digit-bearing example consistently. Negative counterexample stays as `## R-1 -- <title>` (which the regex correctly rejects because of the double-hyphen, not the placeholder).
- **Builder draft**: ACCEPTED-FIXED — applied to `design.md` "What's new" + Implementation sketch §1 + §2 + §3 (test code blocks); applied to `ADR-003` Decision section. All occurrences of `R-NN` → `R-1` in canonical-example positions; `R-NN -- <title>` and `R-N -- <title>` in counterexamples → `R-1 -- <title>` (still a regex-rejection by `--`).

### Majors (address this slice)

#### M1: AC #3 (regression-guard) is an invariant-assertion meta-AC — slice-002 lessons-learned violation

- **Claim under review**: original mission-brief AC #3: *"existing risk-register parses unchanged: after this slice, R-1 + R-2 entries returned with byte-identical scores+bands"*. Original design.md "Testing strategy" L249 admitted: *"AC #3 cannot reach genuine WRITTEN-FAILING without a regex change. Acceptable because AC #3 is a regression-guard, not a behavior-change AC; it asserts an invariant. The test-first row's PENDING → WRITTEN-FAILING → PASSING status sequence is technically circumvented for this row."*
- **Issue**: per slice-002's lessons-learned (`/index.md` aggregated): *"Don't write meta-ACs. ACs that assert 'tests for above ACs exist' are circular under TF-1; that's TF-1's job."* AC #3 isn't EXACTLY the meta-AC pattern slice-002 named, but it's the same family: AC #3 is satisfied iff the slice deliberately omits a behavior change. That's a backwards-mapping — the design isn't *delivering* AC #3, it's *not breaking* a pre-existing invariant. The design's own admission ("PENDING → WRITTEN-FAILING → PASSING ... is technically circumvented") is a self-acknowledged TF-1 violation. TF-1 strict pre-finish may flag it, depending on whether the audit accepts a row that goes PENDING → PASSING without WRITTEN-FAILING.
- **Evidence**: design.md L249 (verbatim self-acknowledgment); slice-002 reflection / `_index.md` aggregated lessons; TF-1 schema in `tools/test_first_audit.py`.
- **Proposed fix**: demote AC #3 from a numbered AC to a must-not-defer item with an associated regression-guard test. Drop the AC #3 row from the test-first plan table (TF-1 rows decrease from 3 → 2 + 1 new AC #3 for risk-register.md prose per M2). Add the regression-guard test as a verification-plan-only entry (not in the TF-1 PENDING → WRITTEN-FAILING tracker).
- **Builder draft**: ACCEPTED-FIXED — applied to `mission-brief.md` (test-first table now has 3 rows mapped to the 3 documentation-surface ACs; regression-guard test demoted to "Regression-guard (not test-first)" verification-plan row + new must-not-defer item) and `design.md` (Testing strategy section restructured; new regression-guard test moved out of "implementation sketch §4" into its own non-TF-1 subsection).

#### M2: Slice fixes 2 of 3 documentation surfaces; `architecture/risk-register.md:3` perpetuates the same misleading shape

- **Claim under review**: ADR-003 §"Decision" originally named two surfaces — the audit module's docstring "Format" section and the inline comment immediately above the regex — as the surfaces being fixed. mission-brief "Out of scope" was silent on a third surface.
- **Issue**: empirically verified at /critique-time: `architecture/risk-register.md:3` reads *"H2 heading `## R-N -- <title>`, with required fields..."* — this is a third documentation surface that perpetuates the exact shape the slice exists to eliminate. A user reading risk-register.md (the artifact users actually edit) would be misled in exactly the way slice-002 was misled, even after slice-004 ships. Per ISO/IEC/IEEE 42010 architecture-description consistency principle, the architecture is described across multiple views; the views must remain consistent. Slice-004 fixed (a) docstring + (b) inline comment but left (c) prose-doc inconsistent. The slice's intent ("eliminate the contradiction") wasn't fully delivered.
- **Evidence**: `architecture/risk-register.md:3` verbatim. Confirmed via Read at /critique-time.
- **Proposed fix**: extend the slice scope to also fix `architecture/risk-register.md:3` (~1-line edit to use a digit-bearing example with em-dash separator + parenthetical clarifying accepted-vs-rejected forms). Add a new AC #3 (replacing the demoted M1 AC #3) that asserts the prelude prose's `` ` ``-quoted heading-shape examples match `_RISK_HEADING_RE`. Augment the test-first plan with a 3rd row: `test_risk_register_md_schema_description_examples_match_actual_regex`.
- **Builder draft**: ACCEPTED-FIXED — applied to `mission-brief.md` (new AC #3 added; new test-first row added; new must-not-defer item; out-of-scope updated), `design.md` (What's new extended with risk-register.md L3 edit; Components touched extended; Implementation sketch §3 added; Testing strategy revised), and `ADR-003` (Decision + Consequences sections updated to reference 3 surfaces).

#### M3: Test extraction logic is brittle to realistic future drift cases

- **Claim under review**: design.md §3 (original): AC #1 extraction was `[line.strip() for line in docstring.splitlines() if line.strip().startswith("## R-")]`; AC #2 extraction was `re.findall(r'"(## R-[^"]+)"', comment_blob)` — only matched `"..."`-quoted shapes.
- **Issue**: Per Hendrickson (*Explore It!*) edge-case-discovery heuristics, three realistic future-drift scenarios silently bypass coverage. (1) A maintainer adds an unquoted prose example to the inline comment like `# Also accepts ## R-1 — title` — the `"..."`-only regex doesn't catch it. (2) A maintainer uses markdown-convention backticks `# Example: \`## R-1 — title\`` — the `"..."`-only regex doesn't catch it either. (3) Multi-block comments separated by blank line — the walk-backward stops at the blank, missing earlier examples. Cases (2) and (3) are real and likely; case (1) is an acknowledged coverage gap. The current AC #2 thinks it covers all examples but only catches `"..."`-quoted ones.
- **Evidence**: design.md §3 / §4 verbatim.
- **Proposed fix**: tighten AC #2's extraction regex to ALSO catch backtick-quoted examples — `re.findall(r'[`"](## R-[^`"]+)[`"]', comment_blob)`. Add an explicit test docstring note acknowledging that unquoted prose examples are a known coverage gap, with rationale (tightening to also catch unquoted shapes risks false positives on comment lines that happen to mention `## R-` in non-example contexts; deferred until drift recurs).
- **Builder draft**: ACCEPTED-FIXED — applied to `design.md` Implementation sketch §3 (test extraction regex widened; test docstring extended with coverage-gap acknowledgment + rationale).

### Minors (log; address if cheap)

#### m1: ADR-003's reversibility section minimizes the documentation precedent

- **Claim under review**: ADR-003 (original) "Reversibility" section described option-C migration cost as "somewhat costly" without concrete estimate.
- **Issue**: honest but understated. Slice-004 is the FIRST slice to canonicalize em-dash in the audit module's *docstring* AND in the user-facing `architecture/risk-register.md`. A future option-C slice would need to: (a) revise the docstring's "is NOT accepted" claim, (b) update the inline comment, (c) update risk-register.md L3, (d) potentially add a deprecation hint with new tests. The reversibility cost is "small documentation revision plus new tests if option-C path", not "zero". Calling it "somewhat costly" papers over the actual size.
- **Evidence**: ADR-003 (original) Reversibility section verbatim.
- **Proposed fix**: add a concrete time estimate (~30–60 minutes of doc-revision work) to ADR-003's reversibility statement. Cosmetic clarification; no behavior change.
- **Builder draft**: ACCEPTED-FIXED — applied to `ADR-003` Reversibility section (concrete estimate added; per-Critic-m1 attribution noted).

#### m2: `tools/cross_spec_parity_audit.py` has the identical bug pattern; out of scope but worth noting

- **Claim under review**: implicit in design.md "What's reused" + mission-brief "Out of scope" — slice scopes itself to `tools/risk_register_audit.py`.
- **Issue**: `tools/cross_spec_parity_audit.py:21` shows `## REQ-NN -- <title>` and `:67` shows `"## TM-NN -- title" / "## REQ-NN -- title" / "## NFR-NN -- title"`; the regex at `:69` is the same `[—\-]` single-character class. CSP-1 audit has IDENTICAL bug class as RR-1: docstring + comment claim `--` is valid; regex says no. Out of scope per slice's explicit scoping — but a missed opportunity: the slice mechanism is generally applicable, and CSP-1 will need its own slice with the same treatment. A note flagging this as a follow-up prevents the same bug recurring with a different ID.
- **Evidence**: `tools/cross_spec_parity_audit.py:21,67,69` (Critic-verified).
- **Proposed fix**: add a one-line note to mission-brief "Out of scope" flagging `add-csp-1-docstring-or-regex` as a future slice candidate mirroring slice-004's pattern.
- **Builder draft**: ACCEPTED-FIXED — applied to `mission-brief.md` "Out of scope" (CSP-1 follow-on candidate noted).

## Dimensions checked

- [x] **Unfounded assumptions** — **B1**: design assumed `## R-NN — title` matches the regex; verified empirically that it does NOT (because `NN` isn't `\d+`). Per Wiegers, every claim must trace to evidence; this claim was unverified and contradicts the regex source. Critic-miss class: testing-discipline-conformance + tooling-conformance (the slice's own tests would have caught it at /build-slice T5; better to catch at design-time).
- [x] **Missing edge cases** — **M3** covers extraction-logic edge cases (unquoted examples, multi-block comments, wrapped lines). Per Hendrickson / Bach. Other axes (load, empty, network, concurrency, platform-specific, IO failure) are not relevant to in-process Python regex/docstring work; explicitly checked. Non-ASCII separator characters (en-dash U+2013, horizontal bar U+2015) verified not accepted by current regex — design's claim of "em-dash or single hyphen" is correctly bounded.
- [x] **Over-engineering** — none. The slice is appropriately minimal: documentation-only edit, three small tests, one ADR. Per Fowler / Beck YAGNI: no speculative generality, no plugin systems, no premature abstractions.
- [x] **Under-engineering** — **M2**: `architecture/risk-register.md:3` is a third documentation surface perpetuating the bug, not addressed in the original scope. AC structure delivers AC #1 + AC #2 fully (modulo B1) but leaves the user-facing artifact (risk-register.md) inconsistent with the corrected audit-internal docs. Now extended in scope per ACCEPTED-FIXED.
- [x] **Contract gaps** — none. No new endpoints, events, or integrations. CLI surface unchanged; Python API unchanged. Per Newman / Fielding: nothing to break.
- [x] **Security** — none. The audit reads risk-register.md and emits parsed JSON; no auth surface, no input from untrusted source (the file is part of the architecture vault), no injection vectors. Per OWASP / McGraw: no defensible-attack surface added.
- [x] **Drift from vault** — **m2**: identical bug class in `tools/cross_spec_parity_audit.py` (CSP-1) is a vault-wide consistency issue. The slice's "fix docs not regex" pattern would need to repeat there. ADR-003 doesn't (originally) note this. Not a blocker; flagged as cross-cutting and added to mission-brief out-of-scope as future slice candidate. ADR numbering: ADR-003 follows ADR-001 + ADR-002 correctly.
- [x] **Web-known issues** — Python regex `r"...[—\-]..."` with em-dash literal works correctly when source file is UTF-8 (Python default since 3.0); verified the regex works with em-dash on the existing real-file test (R-1, R-2 parse). PEP 257 / `inspect.getdoc()` behavior confirmed: dedents to minimum indentation across non-blank lines, preserves relative indentation in code blocks. AC #1's extraction is consistent with that behavior. No platform-specific regex quirks for `\d+` in Python 3 (matches Unicode digits by default; if `re.ASCII` flag added later, behavior would tighten but not affect ASCII-digit examples). No deprecations or community-migration concerns relevant.

Sources:
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [Python `inspect.getdoc()` documentation](https://docs.python.org/3/library/inspect.html)
- [Python `re` module documentation](https://docs.python.org/3/library/re.html)
- [Unicode HOWTO — Python documentation](https://docs.python.org/3/howto/unicode.html)
- [textwrap.dedent / inspect.getdoc behavior — CPython issue #37069](https://github.com/python/cpython/issues/37069)

## Triage

**Triaged by**: user
**Date**: 2026-05-10
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Replaced `R-NN` letter placeholders with `R-1` digit-bearing examples in design.md §1 + §2 + §3 + ADR-003 Decision section; negative counterexamples kept as `R-1 -- <title>` (regex-rejected by `--`, not by ID format) |
| M1 | Major    | ACCEPTED-FIXED | Demoted original AC #3 (regression-guard) from TF-1 plan; moved test to verification-plan + must-not-defer; opened slot for new AC #3 (per M2). Mission-brief test-first table is now 3 rows mapped 1-to-1 to 3 documentation-surface ACs |
| M2 | Major    | ACCEPTED-FIXED | Added new AC #3 + test-first row #3 covering `architecture/risk-register.md:3` prelude prose consistency; extended slice scope to fix that L3 line; ADR-003 Decision/Consequences updated to reference 3 surfaces |
| M3 | Major    | ACCEPTED-FIXED | Tightened AC #2 extraction regex to `[`"](## R-[^`"]+)[`"]` catching markdown-convention backticks alongside Python `"..."`; added test docstring note acknowledging unquoted-prose coverage gap with rationale |
| m1 | Minor    | ACCEPTED-FIXED | ADR-003 Reversibility section refined with concrete time estimate (30–60 min doc-revision work) for option-C migration; per-Critic attribution noted |
| m2 | Minor    | ACCEPTED-FIXED | Added `add-csp-1-docstring-or-regex` future-slice candidate to mission-brief "Out of scope" flagging the parallel CSP-1 audit bug class |
