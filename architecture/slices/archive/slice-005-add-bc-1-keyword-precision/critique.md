# Critique: Slice 005 add-bc-1-keyword-precision

**Critic reviewed**: mission-brief.md, design.md, ADR-004
**Date**: 2026-05-10
**Result**: NEEDS-FIXES (user-ratified 2026-05-10)

## Summary

The design is empirically grounded (the empirical-verification table is honest and verifiable — the Critic re-ran it and counts match exactly), the algorithm is well-chosen (Option 3 dominates Option 1 + 2), and ADR-004 correctly justifies the choice. The Critic surfaced two real blockers: (B1) the meta-bootstrap self-application contradiction in must-not-defer item #5, and (B2) the AC #3 / design empirical-table wording mismatch (`fenced` vs `fence`) which means AC #3 as written is not satisfied by the `fence` keyword the design empirically verified — only by the `llm` keyword, undetected. Plus three majors (M1: no TF-1 row pins migrated anchor lists; M2: `anchor-not-in-keywords` flagged OPTIONAL but contradicts the input-validation must-not-defer item; M3: schema-pin test pins only 1 of 2 new contract surfaces) and four minors. All Builder draft dispositions are ACCEPTED-FIXED or ACCEPTED-PENDING — the Critic's findings are correct and the fixes are cheap to apply pre-build.

## Findings

### Blockers (must address before /build-slice)

#### B1: must-not-defer #5 self-application is contradicted by the slice's own files under both old AND new logic

- **Claim under review**: mission-brief.md must-not-defer item #5: *"No false positives on slice-005's own mission-brief.md / design.md — meta-bootstrap check. If this slice's brief contains words like `parse` or `keyword` that would fire BC-1 rules under either old OR new logic, the new logic must NOT regress on this brief either."*
- **Issue**: The item's headline ("No false positives") and its body ("must NOT regress") contradict each other. Empirically verified: slice-005's own mission-brief.md + design.md fire BC-PROJ-1 (`subagent`/`fan-out` anchors), BC-PROJ-2 (`fence`/`code-block`/`llm` anchors), and BC-GLOBAL-1 under BOTH old substring AND new word-boundary+anchors logic — these are meta-references because the slice IS about LLM-fence-parsing rules (it edits them). Pre-finish gate item repeats the absolute "no false positives" claim. Per Wiegers, every AC/MND must have an observable success criterion; this one is unverifiable as worded.
- **Evidence**: `re.findall(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)` against slice-005's own mission-brief.md + design.md: BC-PROJ-1 anchors `subagent`=3, `fan-out`=2 → fires; BC-PROJ-2 anchors `fence`=14, `code-block`=4, `llm`=16 → fires; BC-GLOBAL-1 same.
- **Proposed fix**: Reformulate item #5: "MND #5 is satisfied if BC-PROJ-1/2/GLOBAL-1 fire on slice-005's own files for the same reason they fire today (meta-references to rule definitions); document expected applicable rules + 'meta-reference' rationale in build-log.md and defer-with-rationale at pre-finish gate." Align pre-finish gate item with the same wording. Enumerate expected applicable rules explicitly.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md must-not-defer #5 + pre-finish gate item — reformulated both items: rules {BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1} firing on slice-005's own files is **expected** meta-reference behavior (slice domain is rule definition); a fourth rule appearing IS a regression. Build-log.md at T-final captures rule list + meta-reference rationale + defer-with-rationale.

#### B2: AC #3 example wording (`fenced`) does not match the design's anchor vocabulary (`fence`); empirical-verification table uses different wording

- **Claim under review**: mission-brief.md AC #3: *"a synthetic mission-brief.md... (e.g., 'Parse the LLM agent's **fenced** output for nested triple-backtick blocks') DOES trigger BC-PROJ-2 and BC-GLOBAL-1."* design.md "Empirical verification" row: *"Synthetic positive: 'Parse the LLM agent's **fence** output for nested triple-backtick blocks' | llm=1, fence=1 | YES (fires)"*.
- **Issue**: AC #3 uses `fenced` (past participle); design empirical-table uses `fence` (bare). Empirically verified: `\bfence\b` MISSES `fenced`; only `\bllm\b` HITS. AC #3 IS satisfiable but only via `llm` anchor, not `fence` as the design table claims. The empirical table verified the WRONG sentence. The design's deferred-work caveat ("if a future slice mentions only `fenced` not bare `fence`, defer-with-rationale") is realized RIGHT IN AC #3 ITSELF.
- **Evidence**: `re.search(r'\bfence\b', "Parse the LLM agent's fenced output...", re.IGNORECASE)` → MISS. Same call against `"...fence output..."` → HIT.
- **Proposed fix**: Update AC #3's example string to use bare `fence` matching the design empirical table: `"Parse the LLM agent's fence output for nested triple-backtick blocks"`. Also enrich the synthetic to include `code-block` for redundancy: `"Parse the LLM agent's fenced output for nested triple-backtick code-block sections"` — this matches `llm`, `code-block` anchors AND keeps the natural English `fenced`. Either path; the design's empirical-table MUST agree byte-for-byte with AC #3.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md AC #3 + design.md empirical-verification table — aligned both to single canonical sentence `"Parse the LLM agent's fenced output for nested triple-backtick code-block sections"`. Anchors `llm` (1) and `code-block` (1) match via word-boundary; `fence` does NOT match (`\bfence\b` misses `fenced`) — that's now documented in BOTH the AC #3 prose and the design empirical-table for transparency. The example is realistic English (uses natural `fenced`) AND matches ≥2 anchors via the redundant `code-block` token.

### Majors (address this slice)

#### M1: TF-1 plan has no test row for migrated rule parsing — design says migration is in scope and required for ACs #1+#2 to pass, but no test pins the migrated anchor lists

- **Claim under review**: design.md "Builder notes": *"Migration is in scope... Without migration, AC #1 + #2 backtests still fail."* TF-1 plan has 4 rows: backtest-003, backtest-004, positive-case, schema-doc-pin. None asserts the migrated rules parse to the correct anchor tuples.
- **Issue**: Per Wiegers, every contract change needs traceability to test. A typo in `architecture/build-checks.md` (e.g., `Trigger anchors: fenced, code-block, llm` instead of `fence`) would silently break: parse violation `anchor-not-in-keywords` would fire, but backtest tests still pass (slice-003+004 don't have any of these anchors anyway). Net: slice can ship with a broken anchor list undetected.
- **Proposed fix**: Add 5th TF-1 row: `test_migrated_rules_have_expected_anchors` reading `architecture/build-checks.md` via `_parse_rules` and asserting BC-PROJ-1.trigger_anchors == ('subagent', 'fan-out'), BC-PROJ-2.trigger_anchors == ('fence', 'code-block', 'llm'). Equivalent for the global file with skip-if-not-present. ~10 lines.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md TF-1 plan + design.md test list — added `test_migrated_rules_have_expected_anchors` as a TF-1 row asserting BC-PROJ-1.trigger_anchors == ('subagent', 'fan-out') AND BC-PROJ-2.trigger_anchors == ('fence', 'code-block', 'llm'). Equivalent for BC-GLOBAL-1 with skip-if-not-present.

#### M2: `anchor-not-in-keywords` violation is a new contract surface but flagged OPTIONAL outside TF-1; conflicts with must-not-defer "Input validation on any new schema field"

- **Claim under review**: design.md flags `test_anchor_not_in_keywords_yields_violation` as OPTIONAL outside TF-1; mission-brief.md must-not-defer mandates "Input validation on any new `build-checks.md` schema field".
- **Issue**: Self-contradiction. Must-not-defer says input validation IS required; design.md says the test is optional. A builder running short on time could ship without exercising the validation path, leaving the must-not-defer un-verified. Per slice-002+slice-004 lessons, this is exactly the bypass the methodology aims to close.
- **Proposed fix**: Promote `test_anchor_not_in_keywords_yields_violation` to a TF-1 row. Trivial fixture (one inline `tmp_path` rule with `Trigger anchors: foo` where `foo` isn't in keywords); test cost identical to existing `test_invalid_severity_yields_violation`.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md TF-1 plan + design.md "Components touched > test file" — promoted `test_anchor_not_in_keywords_yields_violation` to TF-1; removed the OPTIONAL framing. Closes the must-not-defer "Input validation on any new schema field" loop.

#### M3: Schema-pin test underspecifies contract surface — pins `Trigger anchors` field name only, not the word-boundary semantics prose

- **Claim under review**: AC #5 + design.md schema-pin: only the literal substring `Trigger anchors` is asserted.
- **Issue**: Two contract surfaces are added (word-boundary semantics + optional field). The pin covers only one. If a future doc refactor drops the word-boundary semantics prose but leaves `Trigger anchors`, the test passes but documentation is incomplete. Per slice-002+slice-004 aggregated lesson, methodology-tooling slices add prose-pin tests for every contract surface they change.
- **Proposed fix**: Pin two substrings: (a) `Trigger anchors` and (b) a canonical phrase identifying word-boundary semantics — e.g., `word-boundary` or `whole-word` or `\bkw\b`. ~3 lines of test additions. Update AC #5 + design.md.
- **Builder draft**: ACCEPTED-FIXED at AC #5 + design.md — pinned two substrings: (a) `Trigger anchors` for the field name, (b) `word-boundary` for the matching semantics. Two TF-1 rows (`test_build_checks_schema_documents_trigger_anchors_field_name` + `test_build_checks_schema_documents_word_boundary_semantics`) replace the original single schema-doc-pin row. Both surfaces are pinned in BOTH `architecture/build-checks.md` AND `~/.claude/build-checks.md`.

### Minors (log; address if cheap)

#### m1: design.md error-model description contradicts its own algorithm code about "valid anchors filtered through"

- **Claim under review**: design.md "Error model": *"the rule's applicability is computed using the trigger_anchors field as parsed (only valid anchors filtered through)"*. Algorithm: `if rule.trigger_anchors: return any(a in matched for a in rule.trigger_anchors)` — uses ALL anchors.
- **Issue**: Self-contradiction. Behavior is benign (invalid anchors won't match anything in `matched` because `matched` ⊂ `trigger_keywords`), but prose says one thing and code says another.
- **Proposed fix**: Clarify prose: "all anchors as parsed are checked; invalid anchors silently never match (since they aren't in trigger_keywords); the violation surfaces alongside applicability." Zero-effort.
- **Builder draft**: ACCEPTED-FIXED at design.md "Error model" — clarified: "all anchors as parsed are checked; invalid anchors silently never match (since they aren't in trigger_keywords); the violation surfaces alongside applicability via the parse-violation channel." No algorithm change.

#### m2: backward-compat claim "no existing keyword vocabulary intends substring-only match" is asserted, not measured

- **Claim under review**: ADR-004 "Consequences": *"verified across all production rules + all 8 fixture rules in `tests/methodology/fixtures/build_checks/`."*
- **Issue**: Critic re-verified the claim is true. But per Wiegers, claims should trace to evidence inline.
- **Proposed fix**: Cite the verification inline ("BC-PROJ-3 keywords `jwt, token, refresh, auth` against text `'... auth flow'` matches under both substring and word-boundary"). OR leave as-is — minor.
- **Builder draft**: ACCEPTED-FIXED at ADR-004 Consequences — added inline citation listing production rule keywords (BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1) + 2 fixture-rule examples (`keyword_only.md` + `multi_rules.md`) confirming bare-word vocabulary; also referenced the existing 18-test regression-guard as the automated check.

#### m3: design.md cites `tools/build_checks_audit.py:260-286` for `_rule_applies` location; brittle to future edits

- **Claim under review**: design.md: *"Defined in code at: `tools/build_checks_audit.py:260-286`"*.
- **Issue**: Line numbers break when the file is edited. Slice-005 itself edits this function.
- **Proposed fix**: Drop the line range; cite by symbol only (`tools/build_checks_audit.py::_rule_applies`).
- **Builder draft**: ACCEPTED-FIXED at design.md "Contracts > _rule_applies" — replaced `tools/build_checks_audit.py:260-286` with `tools/build_checks_audit.py::_rule_applies` (symbol reference).

#### m4: schema-pin test "skip when ~/.claude/build-checks.md not present" creates a CI gap not surfaced anywhere

- **Claim under review**: design.md: skip-marker disposition for global-file pin.
- **Issue**: pytest.skip is the right call; but CI never validates the global file. If the global file diverges silently, only local manual testing catches it.
- **Proposed fix**: Acknowledge the gap in design.md Builder notes; capture in validation.md evidence section at /validate-slice (run global-file pin manually, log pass/fail). The current design is acceptable as-is.
- **Builder draft**: ACCEPTED-PENDING at /validate-slice (capture global-file pin pass/fail in validation.md evidence section). ACCEPTED-FIXED at design.md Builder notes — CI gap explicitly documented with three mitigations: (1) /validate-slice T-final manual run + validation.md evidence; (2) build-log.md captures the global-file edit; (3) future slice could promote global pins to local-only suite. Current design acceptable; gap documented, not closed.

## Dimensions checked

- [x] **Unfounded assumptions** — B2 (AC #3 wording vs design empirical-table wording — different sentences, verified). m2 (claim "no existing keyword vocabulary intends substring-only match" is asserted not cited inline; benign).
- [x] **Missing edge cases** — Hyphenated keyword word-boundary verified (works correctly via `\b{re.escape("code-block")}\b` because hyphen is `\W` so boundaries land between `code`/`block` and surrounding `\W`). Morphological variants (`fenced`, `parses`, `subagents`) explicitly out-of-scope per design+ADR — acceptable trade-off; the actual concrete missing edge case is B2 (AC #3 itself uses a morphological variant). Empty `trigger_anchors` field handled. Anchor-without-keyword handled implicitly.
- [x] **Over-engineering** — None. Schema field is minimal; algorithm change is one function. ADR-004 explicitly rejected speculative options (ML, per-keyword-config, numeric thresholds).
- [x] **Under-engineering** — M1 (no test pins migrated anchor lists). M2 (input-validation must-not-defer item lacks TF-1 row). M3 (schema-pin pins one of two new contract surfaces). All three are story-to-design traceability gaps per Wiegers + Patton.
- [x] **Contract gaps** — M2 (new violation kind without guaranteed test). M3 (schema description prose has two surfaces but only one pinned). Per Newman.
- [x] **Security** — None. Offline methodology tooling. `re.escape(kw)` correctly prevents user-controlled keyword strings from being interpreted as regex. The build-checks.md files are author-controlled.
- [x] **Drift from vault** — B1 (must-not-defer #5 success criterion unverifiable as worded; per ISO/IEC/IEEE 42010). m1 (design.md error-model prose contradicts algorithm). m3 (line-number reference will be stale). No contradiction with ADR-001/002/003. ADR-002's lenient-API/strict-CLI posture correctly applied. Methodology v0.10.0 BC-1 v1 limitations explicitly contemplated this enhancement.
- [x] **Web-known issues** — Verified Python regex `\b` semantics for hyphenated keywords against [Python re docs](https://docs.python.org/3/library/re.html), [regular-expressions.info word boundary tutorial](https://www.regular-expressions.info/wordboundaries.html). The `rf"\b{re.escape(kw)}\b"` raw f-string + `re.escape` is the canonical idiom. Morphological-variant gap (`fenced` vs `fence`) is a known limitation the design acknowledges.

## Triage

**Triaged by**: user
**Date**: 2026-05-10
**Final verdict**: NEEDS-FIXES

User accepted all Builder draft dispositions as-is ("accept all"). Eight findings are ACCEPTED-FIXED (B1, B2, M1, M2, M3, m1, m2, m3) with edits applied inline to mission-brief.md, design.md, ADR-004 before triage. One finding (m4 — schema-pin global-file CI gap) is ACCEPTED-PENDING — addressed at /validate-slice via validation.md evidence section + design.md Builder-notes documentation of the gap. /build-slice may proceed; the m4 pending action is the single carry-through.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | mission-brief.md must-not-defer #5 + pre-finish gate item reformulated: rules {BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1} firing on slice-005's own files is **expected** meta-reference; a fourth rule appearing IS a regression. |
| B2 | Blocker  | ACCEPTED-FIXED | mission-brief.md AC #3 + design.md empirical-verification table aligned to canonical sentence "Parse the LLM agent's fenced output for nested triple-backtick code-block sections" — `llm` + `code-block` anchors match; `fence` doesn't (documented). |
| M1 | Major    | ACCEPTED-FIXED | mission-brief.md TF-1 plan + design.md test list — added `test_migrated_rules_have_expected_anchors` row pinning BC-PROJ-1 + BC-PROJ-2 anchor tuples; equivalent for BC-GLOBAL-1 with skip-if-not-present. |
| M2 | Major    | ACCEPTED-FIXED | mission-brief.md TF-1 plan + design.md "Components touched > test file" — promoted `test_anchor_not_in_keywords_yields_violation` to TF-1; removed OPTIONAL framing; closes input-validation must-not-defer loop. |
| M3 | Major    | ACCEPTED-FIXED | AC #5 + design.md schema-pin — pinned two substrings: (a) `Trigger anchors` for field name, (b) `word-boundary` for matching semantics. Two TF-1 rows replace the single original schema-doc-pin row. |
| m1 | Minor    | ACCEPTED-FIXED | design.md "Error model" prose clarified — "all anchors checked; invalid silently never match (since not in trigger_keywords); violation surfaces via parse-violation channel". No algorithm change. |
| m2 | Minor    | ACCEPTED-FIXED | ADR-004 Consequences — added inline citation listing production rule keywords (BC-PROJ-1/2/GLOBAL-1) + 2 fixture-rule examples confirming bare-word vocabulary; cited 18-test regression-guard as automated check. |
| m3 | Minor    | ACCEPTED-FIXED | design.md "Contracts > _rule_applies" — replaced line range `:260-286` with symbol reference `::_rule_applies`. |
| m4 | Minor    | ACCEPTED-PENDING | At /validate-slice T-final, capture global-file (`~/.claude/build-checks.md`) prose-pin manual run pass/fail in validation.md evidence section. design.md Builder notes documents the CI gap with three mitigations. |
