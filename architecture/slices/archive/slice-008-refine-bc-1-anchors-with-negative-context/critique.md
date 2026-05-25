# Critique: Slice 008 refine-bc-1-anchors-with-negative-context

**Critic reviewed**: mission-brief.md, design.md, ADR-007
**Date**: 2026-05-10
**Result**: APPROVED-WITH-FIXES (0 blockers; 3 majors; 3 minors)

## Summary

Design is empirically grounded — backtest tables, negative-anchor curation rationale, and self-application all hold up under verification. Two minor scope/test-coverage concerns and a couple of contract-pinning gaps. **Zero blockers.** The design is the strongest in the slice-005..008 BC-1 refinement series. All 3 majors are concrete, actionable, and accepted by Builder for in-slice fix.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: BC-PROJ-2 migration is below the N=3 promotion threshold and the ACs do not gate it

- **Claim under review**: design.md states `BC-PROJ-1 + BC-PROJ-2 each get **Negative anchors**: ...` and ADR-007 says `Migrate BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1`. Mission-brief out-of-scope says: `BC-PROJ-2 modifications (deferred unless empirical surfaces firing).`
- **Issue**: Empirically, BC-PROJ-2 fires false-positively only on slice-005 (N=1) per Critic's own backtest run: `--changed-files tools/build_checks_audit.py architecture/build-checks.md` -> `applicable: ['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']`. Slice-006 + slice-007 both have BC-PROJ-2 in `skipped` (their changed files don't match `skills/**/*.py`/`tools/**/*.py`). Per slice-007 reflection's own promotion-threshold lesson ("Promotion candidate at N=3"), BC-PROJ-2 is at N=1 — not yet promotion-threshold-met. The mission-brief's conditional "deferred unless empirical surfaces firing" is technically satisfied (firing once != never), but the slice's own AC framework only gates BC-PROJ-1 and BC-GLOBAL-1 (ACs #1-#3). AC #4 explicitly accepts `BC-PROJ-1 AND (BC-PROJ-2 OR BC-GLOBAL-1)` — i.e., BC-PROJ-2 doesn't have to be migrated for any AC to pass.
- **Evidence**: `architecture/slices/archive/slice-007-add-critique-agent-content-equality-audit/reflection.md` (Discovered section) — the BC-1 false-positive class is described at N=3 across BC-PROJ-1 + BC-GLOBAL-1; BC-PROJ-2 is NOT in that count. Per Wiegers, an AC must trace to a design element AND vice versa — the design's BC-PROJ-2 migration has no driving AC.
- **Proposed fix**: Either (a) drop BC-PROJ-2 from this slice's migration scope and defer to a future slice if/when N=2 surfaces, OR (b) add an explicit AC #6 gating BC-PROJ-2 silencing on slice-005's archive. Option (a) is simpler and matches mission-brief OOS framing.
- **Builder draft**: ACCEPTED-FIXED — option (a) chosen. Updated `mission-brief.md` Out of scope clause to explicitly cite N=1 below promotion threshold; updated `design.md` What's new + Components touched + Empirical-verification table to drop BC-PROJ-2 migration; updated `ADR-007` Decision section + Consequences to migrate only BC-PROJ-1 + BC-GLOBAL-1, with BC-PROJ-2 deferred to N=2; updated `must-not-defer test 2` (`test_migrated_rules_have_expected_negative_anchors`) to assert only BC-PROJ-1 + BC-GLOBAL-1 tuples.

#### M2: Schema-pin TWO-surface discipline is under-pinned vs slice-005 precedent — only ONE prose substring per file

- **Claim under review**: AC #5 + design.md: `Both files contain the canonical literal substring chosen at /design-slice` (singular). The TF-1 plan row 5 lists one test: `test_negative_context_schema_substring_pinned_in_both_files`.
- **Issue**: Slice-005 added TWO prose-pin tests per surface (`test_build_checks_schema_documents_trigger_anchors_field_name` + `test_build_checks_schema_documents_word_boundary_semantics`) per Critic M3 — the rationale was that pinning ONLY the field name leaves the SEMANTICS phrase unprotected against doc refactor drift. Slice-008's `Negative anchors` field has its OWN distinguishable semantic phrase: "final filter" / "post-applicability filter". With only one pin per file, a future doc refactor could rename the prose summary from "Negative anchors are final filters" to "Negative anchors are exclusionary tokens" without breaking any test — and downstream rule authors would lose the universal-filter framing.
- **Evidence**: `tests/methodology/test_build_checks_audit.py:502-559` — the slice-005 precedent has TWO prose-pin tests covering field-name AND semantics. Per Sommerville's traceability principle, every contract-surface change should have a regression-guard test.
- **Proposed fix**: Add a SECOND TF-1 row: `test_negative_anchors_schema_documents_final_filter_semantics` pinning the literal phrase `final filter` in BOTH `architecture/build-checks.md` AND `~/.claude/build-checks.md`. Bumps TF-1 to 8 rows.
- **Builder draft**: ACCEPTED-FIXED — split AC #5 into 5a (field-name pin: `Negative anchors`) and 5b (semantics-phrase pin: `final filter`). TF-1 plan grew from 7 to 8 rows. Updated `mission-brief.md` AC #5 wording to mention BOTH substrings; updated TF-1 plan table; updated `design.md` "What's new" + "Components touched" sections (`build-checks.md` schema-prelude now TWO sentences); updated `design.md` Test-first plan refinement section to describe both AC #5a + AC #5b tests + the rationale.

#### M3: No test exercises the `applies_to == ("always",)` + negative-anchor interaction

- **Claim under review**: Design.md algorithm-path conformance table claims the new mechanism applies UNIFORMLY across all three positive-applicability paths, including the `always: true` short-circuit. The design refactors `_rule_applies` so EVERY positive-return path is gated through `not _negative_anchor_match(...)`.
- **Issue**: The TF-1 plan tests glob path (slice-001 archive + slice-006/007 with `--changed-files`) and keyword path (slice-005 archive). No test exercises the `always: true` path with a negative anchor. The existing `test_always_true_rule_always_applies` uses an empty `negative_anchors`, which preserves the legacy semantic — but does not test the new "always-EXCEPT-when-negative-anchor-matches" semantic. Per slice-005's algorithm-path-conformance lesson (which slice-008 explicitly inherits), missing path coverage was the exact failure mode caught at /build-slice T5 last time. Per Hendrickson's edge-case heuristics, the `always: true` path is a distinct execution branch and should have explicit coverage when its semantic changes.
- **Evidence**: `tests/methodology/test_build_checks_audit.py:110-128` shows the existing `always` test predates the new semantic. The slice-007 reflection's "Validated" section calls out "TF-1 PENDING -> WRITTEN-FAILING transitions genuine" as N=4 stable — coverage must extend with semantic changes, not stay frozen.
- **Proposed fix**: Add a TF-1 row testing: synthetic build-checks fixture with one rule `Applies to: always: true` + `Negative anchors: foo`; slice text containing `foo`; assert rule appears in `skipped` not `applicable`. With M2 above, brings TF-1 to 9 rows.
- **Builder draft**: ACCEPTED-FIXED — added `test_always_true_rule_with_negative_anchor_match_is_skipped` as must-not-defer TF-1 row 9. Inline tmp_path fixture (matches `test_anchor_not_in_keywords_yields_violation` precedent — no separate fixture file needed). TF-1 plan now at 9 rows. Updated `mission-brief.md` TF-1 plan table; updated `design.md` Test-first plan refinement section with the test design + pre-fix fail signal + post-fix pass signal.

### Minors (log; address if cheap)

#### m1: `Critic-MISSED` token in negative-anchor list is highly methodology-specific to be in the GLOBAL build-checks file

- **Claim under review**: Design.md applies the same 9-token list to BC-GLOBAL-1 in `~/.claude/build-checks.md`. The token `Critic-MISSED` is internal vocabulary specific to the AI SDLC methodology's reflection.md schema (slice-006 introduction, per aggregated lessons).
- **Issue**: The global build-checks file is meant to apply across ALL projects (per its file header). Tokens like `Critic-MISSED`, `back-sync`, `forward-sync`, `Dim 9`, `meta-discussion` are AI-SDLC-methodology-internal vocabulary; a future user adopting this build-checks scaffolding in an unrelated project (e.g., a frontend app with no Critic agent) might have no `Critic-MISSED` references but ALSO might legitimately use `back-sync` (a generic git-versioning concept) in a brief that DOES need the LLM-fence rule to fire. The N=0 evidence of cross-project misuse is reassuring, but the curation rationale's "removing tokens present in slice-001" gives no guarantee about tokens NOT in slice-001 that legitimately appear in non-methodology slices.
- **Evidence**: `~/.claude/build-checks.md:1-3` — file header: "applies across all projects". Compare to project-scoped tokens which are project-specific.
- **Proposed fix**: Either (a) document in the schema-prelude that the `~/.claude/build-checks.md` negative-anchor set is curated for AI-SDLC-methodology-vocabulary slices and may need re-curation in other adopting projects (one prose sentence), OR (b) shrink the global-file negative-anchor set to ONLY the most universal methodology-meta tokens. Option (a) is cheaper and preserves the silencing behavior on this project's slices.
- **Builder draft**: ACCEPTED-FIXED — option (a) chosen. Added a sentence to `~/.claude/build-checks.md` schema-prelude (also reflected in `design.md` "Components touched > `~/.claude/build-checks.md`" and "Negative-anchor curation rationale > Cross-project applicability" subsection). Option (b) rejected because shrinking would break silencing on slice-007 (its negative-anchor coverage relies on `back-sync, forward-sync, Dim 9, Critic-MISSED` — all AI-SDLC-internal tokens; without them, slice-007 has no negative-anchor match in the global file and BC-GLOBAL-1 still false-positive fires, defeating AC #3).

#### m2: ADR-007 "Reversibility: cheap" estimate may understate the test-deletion cost

- **Claim under review**: ADR-007 lists revert steps as "~15 minutes."
- **Issue**: The 9 new tests will all need deletion or rollback in a revert. The 15-minute estimate ignores the test-suite cleanup. Not a blocker — reversibility remains "cheap" semantically.
- **Proposed fix**: Update ADR-007 revert-cost estimate to "~30 minutes (includes 7-9 test cleanup)."
- **Builder draft**: ACCEPTED-FIXED — updated ADR-007 Reversibility section to "~30 minutes" with explicit "9 tests total per the post-Critic TF-1 plan" rationale + a new step #6 enumerating which tests to delete. Reversibility tag remains `cheap`.

#### m3: Token `false positive` (with space) — anchor parser dedup-after-lowercase, but still fragile to author typos

- **Claim under review**: Design's negative-anchor parsing reuses the slice-005 `Trigger anchors` parser shape (comma-split + strip + lowercase + dedupe).
- **Issue**: The token `false positive` works correctly (verified empirically — word-boundary regex matches it cleanly), but a typo like `false-positive` (with hyphen) in the rule text would silently NOT match because the slice texts in slice-005..007 use the space-form. The schema requires no validation that negative anchors actually appear with the expected spelling. Same risk class as slice-005's `anchor-not-in-keywords` (mitigated by parse violation) — but for negative anchors, there's no analogous "anchor-not-in-any-known-slice" sanity check. Not slice-008's job to fix; just flagging.
- **Proposed fix**: Optional — extend `test_migrated_rules_have_expected_negative_anchors` to assert each rule's `negative_anchors` tuple matches the canonical 9-token list literal (mirrors existing `test_migrated_rules_have_expected_anchors`). The design's TF-1 plan already includes this row, so this is pre-mitigated; just note the spelling-fragility concern.
- **Builder draft**: ACCEPTED-FIXED — pre-mitigated. The `test_migrated_rules_have_expected_negative_anchors` TF-1 row already pins exact tuple equality (`("defer-with-rationale", "aggregated lessons", "false positive", "meta-discussion", "vocabulary", "critic-missed", "back-sync", "dim 9", "forward-sync")` lowered). A typo at write-time would fail this test. No additional action needed beyond confirming the test asserts the canonical 9-token tuple as written in the design's "Test-first plan refinement" section.

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (BC-PROJ-2 migration not gated by AC; promotion threshold not met). Per Wiegers, design elements without driving ACs and without empirical evidence are speculative. Other claims (zero overlap, slice-001 zero-hit, slice-005..007 silencing, slice-008 self-application) all empirically validated.
- [x] **Missing edge cases** — M3 (always: true + negative-anchor interaction not in TF-1 plan). Per Hendrickson, distinct execution branches need distinct test cases when their semantics change.
- [x] **Over-engineering** — none. Design is minimum-viable: one new schema field, one new violation kind, two migrated rules, no plugin/factory machinery. ADR-007 explicitly rejects per-keyword-vocabulary auto-promotion as v1 over-engineering. The 9-token curation set is conservative (avoids generic `methodology`, `audit`, `lessons-learned`) — calibrated, not speculative.
- [x] **Under-engineering** — none beyond M1 (BC-PROJ-2 in design without driving AC) which is the inverse problem. Each numbered AC has a TF-1 row + verification-plan entry. Must-not-defer items (input validation on new field, atomic version-bump, two-surface schema-pin, sha256 forensic capture) are all addressed.
- [x] **Contract gaps** — M2 (TWO-pin discipline under-applied vs slice-005 precedent). Per Newman, contract surfaces should be regression-guarded at every distinguishable layer.
- [x] **Security** — none. Slice introduces no new authentication, authorization, network exposure, or data-flow paths. The negative-anchor mechanism is a local-file parser refinement.
- [x] **Drift from vault** — none. Design correctly references slice-005 / ADR-004 ground, preserves bidirectional sha256 forensic-capture pattern, atomic version-bump invariant, TWO-surface schema-pin discipline.
- [x] **Web-known issues** — m1-adjacent. Negative-keyword/exclusion-rule design pattern is well-documented (Karooya 2025; Search Engine Land 2026; OneUptime DLP guide 2026; rexegg "Best Regex Trick"). Empirical-curation discipline is the standard mitigation. The 9-token list is small and validated against a 7-slice corpus.
- [x] **Cross-cutting conformance (Dim 9)** — implicitly covered by M2 (TWO-surface schema-pin discipline = cross-cutting tooling-doc-vs-impl parity sub-clause) + M3 (algorithm-path-conformance sub-clause). Both surfaced at /critique time, validating the 9-dim Critic's empirical effectiveness on cross-cutting findings (slice-007 was 60% catch rate; slice-008 currently sees 2 of 6 cross-cutting hits caught at design vs. 4 carried forward per the slice-007 effectiveness target).

Sources cited:
- [Karooya — Keywords & Negative Keywords in Google Ads 2025](https://www.karooya.com/blog/keywords-negative-keywords-in-google-ads-2025/)
- [Search Engine Land — Negative Keywords Strategy 2026](https://searchengineland.com/negative-keywords-strategy-476563)
- [OneUptime — Exclusion Rules to Reduce False Positives in Cloud DLP](https://oneuptime.com/blog/post/2026-02-17-how-to-create-exclusion-rules-to-reduce-false-positives-in-cloud-dlp/view)
- [rexegg — The Best Regex Trick](https://www.rexegg.com/regex-best-trick.php)
- [regular-expressions.info — Lookahead and Lookbehind](https://www.regular-expressions.info/lookaround.html)

Files reviewed:
- `tools/build_checks_audit.py`
- `architecture/build-checks.md`
- `~/.claude/build-checks.md`
- `tests/methodology/test_build_checks_audit.py`
- All 7 archived slice folders (slice-001 through slice-007)
- `architecture/slices/slice-008-refine-bc-1-anchors-with-negative-context/` (mission-brief.md + design.md + ADR-007)
- `methodology-changelog.md` (in-repo + `~/.claude/`)
- `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml`

## Triage

**Triaged by**: user
**Date**: 2026-05-10
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major  | ACCEPTED-FIXED | mission-brief OOS clause clarified; design.md What's new + Components touched + Empirical table updated; ADR-007 Decision + Consequences updated; BC-PROJ-2 dropped from migration; `test_migrated_rules_have_expected_negative_anchors` only asserts BC-PROJ-1 + BC-GLOBAL-1 |
| M2 | Major  | ACCEPTED-FIXED | AC #5 split into 5a (field-name pin) + 5b (`final filter` semantics pin); TF-1 plan grew 7 -> 8 rows; mission-brief AC #5 + TF-1 table + design.md What's new + Components touched + Test-first plan refinement all updated |
| M3 | Major  | ACCEPTED-FIXED | Added `test_always_true_rule_with_negative_anchor_match_is_skipped` as must-not-defer TF-1 row 9; inline tmp_path fixture (no new fixture file); TF-1 plan grew 8 -> 9 rows; mission-brief TF-1 table + design.md Test-first plan refinement updated |
| m1 | Minor  | ACCEPTED-FIXED | Added cross-project-applicability sentence to `~/.claude/build-checks.md` schema-prelude; design.md "Components touched > `~/.claude/build-checks.md`" + "Negative-anchor curation rationale > Cross-project applicability" subsection updated. Option (b) rejected (would break slice-007 silencing) |
| m2 | Minor  | ACCEPTED-FIXED | ADR-007 Reversibility section updated: "~30 minutes" estimate + new step #6 enumerating 9 tests to delete. Tag remains `cheap` |
| m3 | Minor  | ACCEPTED-FIXED | Pre-mitigated by existing `test_migrated_rules_have_expected_negative_anchors` TF-1 row; no additional action needed |

**Triage summary**:
- 0 blockers
- 3 majors: all ACCEPTED-FIXED in design + mission-brief + ADR-007
- 3 minors: 2 ACCEPTED-FIXED (m1 prose addition, m2 cost estimate update); 1 pre-mitigated (m3)
- 0 OVERRIDDEN, 0 DEFERRED, 0 ESCALATED

**Final verdict per audit semantics**: CLEAN (all 6 dispositions are ACCEPTED-FIXED; none ESCALATED, none ACCEPTED-PENDING). User ratified all 6 dispositions per TRI-1.
