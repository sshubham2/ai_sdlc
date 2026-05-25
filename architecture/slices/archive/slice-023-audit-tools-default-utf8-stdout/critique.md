# Critique: Slice 023 audit-tools-default-utf8-stdout

**Critic reviewed**: mission-brief.md, design.md, ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md
**Date**: 2026-05-15
**Result**: BLOCKED (pre-triage) — 5 Blockers + 8 Majors + 4 Minors = 17 findings

## Summary

The Critic returned a substantial review (5 Blockers + 8 Majors + 4 Minors). The slice premise is sound and the helper + audit pattern is structurally clean, but the design committed multiple Dim 9 sub-clause 2 (design.md vs canonical inventory) instances: claimed paths that don't exist in this repo (`architecture/methodology-changelog.md`, `tests/decisions/`, `tests/methodology/test_row_*.py`), conventions that have no precedent (leading-underscore PMI-1 filter, plugin.yaml `- id:` field), and internally-contradictory counts (audit JSON output `tools_scanned: 17, tools_with_main: 16` is logically impossible). Builder's pre-/critique prediction of ≤5 first-Critic findings was falsified at 2.6× (actual 13). All findings are verified against the codebase by Builder before drafting dispositions.

## Findings

### Blockers (must address before /build-slice)

#### B1: `methodology-changelog.md` path wrong in 6 sites — file is at repo root, not under `architecture/`

- **Claim under review**: design.md L39 + L53 + L58 + L265 + L329 + ADR-021 L84 all reference `architecture/methodology-changelog.md`.
- **Issue**: The in-repo file lives at `<repo>/methodology-changelog.md`. `architecture/methodology-changelog.md` does not exist. Per Wiegers + Dim 9 sub-clause 2 (design.md vs canonical inventory), every design path claim must be evidence-backed.
- **Evidence**: `Glob "methodology-changelog.md"` returns `methodology-changelog.md` (root); `Glob "**/methodology-changelog.md"` same — no `architecture/` prefix anywhere.
- **Proposed fix**: Strike `architecture/` prefix from all 6 mentions across design.md + ADR-021.
- **Builder response**: **ACCEPTED-FIXED** at design.md (global `replace_all`) + ADR-021 (global `replace_all`). Verified via `Grep "architecture/methodology-changelog" architecture/slices/slice-023-*/ architecture/decisions/ADR-021-*` returns zero matches post-fix.

#### B2: PMI-1 will fire `orphan-tool` on `tools/_stdout.py` — design's "leading-underscore exclusion convention" does not exist in the audit

- **Claim under review**: design.md L51 + L295 "EXCLUDE `_stdout` (leading underscore = private convention; mirrors `tools/__init__.py` exclusion). `/build-slice` Step 1 verifies the `_CANONICAL_TOOLS` set's existing leading-underscore exclusion (or PMI-1 audit's filtering rule) to confirm this matches precedent."
- **Issue**: `tools/plugin_manifest_audit.py:_list_actual_tools` L133-140 only excludes `__init__.py` — no leading-underscore filter. Once `tools/_stdout.py` ships, PMI-1's `actual_tools - declared_tools` set diff will produce an `orphan-tool` violation, failing the gate at every subsequent `/build-slice` Step 6 forever. Design's hand-wave to "Step 1 will resolve" is under-engineering: AC #5 + Must-not-defer "PMI-1 PASS" cannot be met without a code change.
- **Evidence**: `tools/plugin_manifest_audit.py` L137-140 (verified by Read). `tools/install_audit.py` `_CANONICAL_TOOLS` is an explicit tuple — also no leading-underscore filter, but it doesn't scan the filesystem so `_stdout` exclusion is achieved trivially via tuple non-membership.
- **Proposed fix**: Extend `_list_actual_tools` to also exclude `p.name.startswith("_")`. Add a unit test covering both `__init__.py` and a fixture `tools/_helper.py`. Treat as +1 source-file edit + 1 test-file edit in design.md "Files changed".
- **Builder response**: **ACCEPTED-PENDING** (Path A chosen). Will apply at /build-slice: (a) one-line edit to `tools/plugin_manifest_audit.py` `_list_actual_tools` to add `and not p.name.startswith("_")` to the comprehension filter; (b) new unit test `test_list_actual_tools_filters_leading_underscore_helpers` in `tests/methodology/test_plugin_manifest_audit.py` covering both `__init__.py` and synthetic `_helper.py` exclusion; (c) design.md "Files changed" enumeration extended at row 32 + row 31 (already updated inline this round to reflect the +1 source-file + +1 test). PMI-1 v1.1 retirement-proof invariant preserved (gate body unchanged; only the discovery filter narrows).

#### B3: `tests/decisions/test_adr_021.py` references a directory that does not exist; ADR-pin convention is `tests/methodology/test_methodology_changelog.py::test_adr_NNN_*`

- **Claim under review**: mission-brief.md TF-1 plan row 16; design.md L50 + L335 + L286.
- **Issue**: `tests/decisions/` does not exist (`Glob "tests/decisions/*.py"` returns no files). ADR-pin convention is `test_methodology_changelog.py::test_adr_NNN_*` (verified via `Grep "^def test_adr_" test_methodology_changelog.py` returning rows for ADR-013 through ADR-020).
- **Evidence**: `Glob "tests/decisions/*.py"` empty. Grep on `test_methodology_changelog.py` shows `test_adr_020_exists_and_supersedes_adr_019` + `test_adr_020_documents_three_mode_taxonomy` at L1863 / L1903.
- **Proposed fix**: Replace all `tests/decisions/test_adr_021.py` references with `tests/methodology/test_methodology_changelog.py::test_adr_021_present_and_reversibility_cheap`. Update TF-1 plan row 16, design.md L50 + L335 + shippability row 23 command cell.
- **Builder response**: **ACCEPTED-FIXED** at mission-brief.md TF-1 row 16 (updated path) + design.md L50 ("EXTENDS test files" block now lists ADR-pin under `test_methodology_changelog.py`) + design.md L335 (Files-changed row 29 updated) + design.md L286 (shippability row 23 command cell updated to include `test_methodology_changelog.py::test_adr_021_present_and_reversibility_cheap`).

#### B4: `test_row_023_utf8_stdout.py` references a convention that does not exist; row tests in shippability are inline `Command` cells, not separate files

- **Claim under review**: mission-brief.md TF-1 row 15 + design.md L49 + L334 + L287.
- **Issue**: No `tests/methodology/test_row_*.py` or `tests/methodology/test_shippability*.py` files exist (verified by Glob). Shippability rows are not tested by separate per-row files; the `Command` cell in shippability.md IS the test, invoked by `/validate-slice` at pre-finish.
- **Evidence**: `Glob "tests/**/test_row_*.py"` empty. `Glob "tests/**/test_shippability*.py"` empty.
- **Proposed fix**: Drop the `test_row_023_utf8_stdout.py` file entirely. Re-enumerate shippability row 23's `Command` cell to invoke the actual tests this slice ships. Remove TF-1 plan row 15. Decrement file count.
- **Builder response**: **ACCEPTED-FIXED** at mission-brief.md TF-1 plan (row 15 replaced with structural tests pointing at `test_plugin_manifest_audit.py` and `test_install_audit.py` named functions) + design.md L49 + L334 (dropped `test_row_023_utf8_stdout.py` entirely; reduced from row 28 → no row; replaced with `test_utf8_stdout_regression.py` from M5 split) + design.md L286 (shippability row 23 command cell re-enumerated to 9 invocation targets across 5 test files, all of which actually exist or are NEW within this slice).

#### B5: Audit output contract miscounts — `tools_scanned: 17, tools_with_main: 16` is wrong; canonical numbers post-slice are `scanned: 17, with_main: 17, clean: 17`

- **Claim under review**: design.md L116-142 JSON contract; mission-brief.md L50 verification cell N=16; design.md L225 "17 tools"; design.md L344 "currently 16, will be 17 post-slice".
- **Issue**: Internally contradictory. Post-slice tools/ has 19 .py files (`__init__.py` + `_stdout.py` + 16 modified audits + 1 new audit). Exclusion list per L105 is `_stdout.py` + `__init__.py`. After exclusion: 17 scanned, all with main(). The design claimed `tools_scanned: 17, tools_with_main: 16` — logically impossible. AC #2 verification cell N=16 also drifted vs L225's "17 tools".
- **Evidence**: design.md L105 (exclusion list); L116-142 (output contract); L225; L344; mission-brief.md L50.
- **Proposed fix**: Pick canonical (17/17/17 on clean) and propagate across mission-brief AC #2 cell + design.md L116-142 + L225 + L344 + audit unit-test assertions. Add a regression-guard prose-pin test asserting `tools_scanned == tools_with_main + (helper_count)` and `tools_clean == tools_with_main` on clean.
- **Builder response**: **ACCEPTED-FIXED** at design.md L116-142 (JSON contract now shows `17/17/17` clean + `17/17/16+violations` on violation; output-contract-invariant block added with 3 regression-guard prose-pinned assertions) + design.md L225 (Self-application section rewritten to assert `tools_scanned: 17, tools_with_main: 17, tools_clean: 17`) + design.md L344 (Wiegers-coverage-symmetry watch-list ratcheted to N=13+ cumulative) + mission-brief.md L50 (verification cell now references the canonical 17/17/17). Sibling-site sweep verified across 6 surfaces per Wiegers regression-guard coverage-symmetry discipline.

### Majors (address this slice)

#### M1: AC #4 behavioural regression test argv strategy under-specified — most audit tools require positional slice-folder argument

- **Claim under review**: AC #4 / mission-brief.md L19 + design.md L43 + L223.
- **Issue**: Each audit tool has a different argv contract. Without per-tool argv strategy, the regression test may pass vacuously (no audit reaches the encoding-touching path) or fail spuriously (argparse exits 2 before reconfigure fires — the accidental-PASS pitfall TF-1 PENDING→WRITTEN-FAILING genuineness sub-clause flags). Also: parent-side `subprocess.run` must pin `encoding="utf-8"` or it crashes decoding the child's UTF-8 output.
- **Evidence**: tools/branch_workflow_audit.py L375 (positional `slice_folder`); tools/test_first_audit.py L405-414 (same); slice-021 `test_critique_agent_drift_audit_clean_at_slice_021_ship` uses `subprocess.run(..., text=True)` WITHOUT `encoding="utf-8"`.
- **Proposed fix**: Per-tool argv enumeration table; pin subprocess.run kwargs; pin assertion on `UnicodeEncodeError`/`UnicodeDecodeError` not in stderr.
- **Builder response**: **ACCEPTED-FIXED** at design.md "Error model" surface 3. Per-tool argv strategy enumerated by group: (a) positional-slice-folder tools (9 audits) take a synthetic `tests/methodology/fixtures/utf8_stdout/slice-fixture/` with U+2192-bearing mission-brief.md; (b) `--root`-only tools take `--root tmp_path`; (c) no-argv tools (`mock_budget_lint`, `validate_slice_layers`) invoke bare; (d) `risk_register_audit` takes positional file path; (e) `critique_agent_drift_audit` + `critique_review_audit` take `--repo-root`. subprocess.run pinned to `text=True, encoding="utf-8", errors="replace", env={"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0", ...}`. Failure assertion targets stderr-contains-UnicodeEncodeError/DecodeError, NOT exit-code-0. Fixture file `tests/methodology/fixtures/utf8_stdout/slice-fixture/mission-brief.md` added as row 36 in Files-changed.

#### M2: design.md L67 + L176 claim 7 audits are "already in Step 6 audit list" — only 5 are

- **Claim under review**: design.md L67 + L176.
- **Issue**: `skills/build-slice/SKILL.md` Step 6 (L120-129) enumerates ONLY 5 audits: LINT-MOCK-1, WIRE-1, BC-1, TF-1, BRANCH-1. WS-1 / ETC-1 / RR-1 / PMI-1 run at /validate-slice, not /build-slice Step 6.
- **Evidence**: Read of `skills/build-slice/SKILL.md` L115-129 confirms 5-bullet list.
- **Proposed fix**: Reword L67 + L176 to enumerate the actual 5 audits.
- **Builder response**: **ACCEPTED-FIXED** at design.md L67 (rewritten to name the 5 actual audits + describe the 6th-bullet + new sub-section insertion) + L176 ("Build-slice Step 6 pre-finish gate (extended)" rewritten to assert "verified prose-enumerated at L120-129 per M2 ACCEPTED-FIXED" + 5-audit enumeration).

#### M3: plugin.yaml entry shape wrong — uses `- id:` but canonical shape is `- path: ... rule: ...`

- **Claim under review**: design.md L295.
- **Issue**: Existing 16 tool entries use `- path: tools/<name>.py / rule: <RULE-ID>` shape; no `id:` field on any. `test_plugin_yaml_lists_branch_workflow_audit` pins the `path:` shape.
- **Evidence**: `Grep "tools/" plugin.yaml` shows `- path: tools/branch_workflow_audit.py` + 15 more in same shape; no `- id:` matches.
- **Proposed fix**: Replace with canonical shape `- path: tools/utf8_stdout_audit.py / rule: UTF8-STDOUT-1`.
- **Builder response**: **ACCEPTED-FIXED** at design.md L295 ("PLUGIN MANIFEST update" line) — entry shape now `- path: tools/utf8_stdout_audit.py / rule: UTF8-STDOUT-1`. Sibling-site sweep verified: design.md "What's new" plugin-yaml mention also pins the canonical shape.

#### M4: design.md L36 "from tools import _stdout (or `from . import _stdout` — picks the existing import convention per tool)" — no existing convention exists; both forms are NEW

- **Claim under review**: design.md L36 + L149.
- **Issue**: `tools/__init__.py` is empty; no current tool imports another tool sibling. The "picks the existing convention" framing is a hedge against a phantom variability. 16 sites and zero precedents → risk of inconsistency.
- **Evidence**: `tools/__init__.py` empty (verified); no current intra-`tools/` sibling import via `from tools import` or `from . import`.
- **Proposed fix**: Pin `from tools import _stdout` as the canonical form for all 17 modules. Add a prose-pin test.
- **Builder response**: **ACCEPTED-FIXED** at design.md L36 (canonical form pinned + rationale + prose-pin test reference) + L149 ("What changes per tool" block updated). Prose-pin test added to TF-1 plan / audit unit tests: `test_every_tool_uses_canonical_from_tools_import_stdout` in `test_utf8_stdout_audit.py`.

#### M5: AC #4 says "Test lives at `tests/methodology/test_utf8_stdout_audit.py`" but TF-1 plan rows 7-12 already use that file for AC #2 + #3 unit tests — single file holding audit unit tests + audit behavioural regression conflates two test purposes

- **Claim under review**: mission-brief.md L19 + TF-1 rows 7-12 + design.md L42-43.
- **Issue**: Combining AST unit tests (fast) with subprocess-based regression (slow; 17×subprocess ≈ 5–17s) in one file means the audit unit tests can't be run quickly in isolation. Failure-mode lineage less crisp.
- **Evidence**: Mental arithmetic: 17 subprocess.run invocations × 0.3–1.0s = 5–17s.
- **Proposed fix**: Split into `test_utf8_stdout_audit.py` (unit tests) + `test_utf8_stdout_regression.py` (subprocess behavioural). Update TF-1 plan.
- **Builder response**: **ACCEPTED-FIXED** at mission-brief.md L19 (test path updated to `test_utf8_stdout_regression.py`) + mission-brief.md TF-1 plan row 12 (AC #4 row's path updated) + design.md L42-43 (split documented) + design.md L223 (regression test home now `test_utf8_stdout_regression.py`) + design.md Files-changed list row 28 (new file added) + shippability row 23 command cell (added `test_utf8_stdout_regression.py` as 3rd whole-file pytest target).

#### M6: AC #1 "Idempotent under repeat invocation" + helper body — idempotency-via-encoding-check is fragile under pytest reconfigure

- **Claim under review**: design.md L86-95 helper body — idempotency relies on `if getattr(stream, "encoding", "").lower() == "utf-8": continue`.
- **Issue**: If a downstream caller has reconfigured with `errors="strict"`, the encoding check passes but the errors mode is still strict; a subsequent U+2192 crashes. The slice's whole point is `errors="replace"`.
- **Evidence**: design.md L92-94 (encoding-only short-circuit); AC #1 (c) idempotency; Must-not-defer item 3 errors=replace.
- **Proposed fix**: Drop the encoding-only short-circuit; rely on stdlib's idempotent reconfigure. Add unit test `test_reconfigure_overrides_prior_errors_strict_to_errors_replace`.
- **Builder response**: **ACCEPTED-FIXED** at design.md L86-95 (helper body simplified; encoding-only short-circuit removed; docstring updated to explain why unconditional reconfigure is correct). Idempotency now relies on stdlib `TextIOWrapper.reconfigure` being safe to call with same kwargs (true since Python 3.7). Will add `test_reconfigure_overrides_prior_errors_strict_to_errors_replace` to TF-1 plan AC #1 at /build-slice — 5th row added to test_stdout_helper.py (currently 4 rows).

#### M7: ADR-021 L82 N=6 cumulative recurrence claim should be accompanied by the slice-022 archived reflection citation

- **Claim under review**: ADR-021 + mission-brief.md L5 N=6 across slices 007, 016, 018, 020, 021, 022.
- **Issue**: Count provenance not inline-cited. shippability rows 20/21/22 establish the increments but ADR-021 doesn't link them.
- **Evidence**: shippability row 22 cites N=5 → N=6; row 21 N=4 → N=5; row 20 N=3 → N=4.
- **Proposed fix**: Strengthen with shippability-row citation. Replace `?` date placeholders.
- **Builder response**: **ACCEPTED-FIXED** at ADR-021 — slice-022 entry now cites `architecture/slices/archive/slice-022-redesign-commit-slice-for-pr-aware-flow/milestone.md` L44 + `validation.md` L113 + shippability rows 20/21/22 cumulative-count provenance trail.

#### M8: design.md "Cumulative-Critic-influence note" prediction (≤5 first-Critic + N=8 stable) is a falsifiable claim worth scoring — current critique already exceeds the prediction at 13 first-Critic

- **Claim under review**: design.md L232 prediction.
- **Issue**: This critique surfaces 13 first-Critic findings (5B + 8M + 4m). The prediction's prose-pin under-counted the artifact-vs-codebase-convention class (Dim 9 sub-clause 2).
- **Evidence**: This critique's finding count + breakdown.
- **Proposed fix**: Update Cumulative-Critic-influence note with actual count + class breakdown post-/critique for /critic-calibrate scoring.
- **Builder response**: **ACCEPTED-FIXED** at design.md "Cumulative-Critic-influence note" — full rewrite to: (a) record predicted vs actual; (b) enumerate catch-class breakdown (Dim 9 sub-clause 2 dominant at 6 findings; Dim 4 under-engineering at 3; Dim 5 contract gaps at 3; cross-cutting at 1+ informational); (c) Wiegers ratchet N=12 → N=13+ at slice-023; (d) Cross-mission-brief-vs-design-consistency-checking N=1 → N=3 cumulative at slice-023 — **promotion to Dim 9 sub-clause at /critic-calibrate slice-024 ELIGIBLE at N=3 threshold**.

### Minors (log; address if cheap)

#### m1: ADR-021 L19-24 has `(2026-?, ...)` date placeholders for slices 007 and 016

- **Claim under review**: ADR-021 L19-20.
- **Builder response**: **ACCEPTED-FIXED** — looked up archive/_index.md ship dates (slice-007: 2026-05-10, slice-016: 2026-05-13); updated ADR-021 L19-20 inline this round.

#### m2: ADR-021 N-surface schema-pin language conflates cross-slice ordinal (N=9 → N=10) with within-slice surface count (N=3 surfaces)

- **Claim under review**: ADR-021 L85.
- **Builder response**: **ACCEPTED-FIXED** at ADR-021 L85 — two counters disambiguated explicitly.

#### m3: design.md L45 "rule-of-three at N=3 entries" then enumerates 5 entries → label inconsistent

- **Claim under review**: design.md L45.
- **Builder response**: **ACCEPTED-FIXED** at design.md L45 (now part of the rewritten EXTENDS-test-files block) — rephrased to "rule-of-three originally confirmed at N=3 entries v0.33.0/v0.34.0/v0.35.0; now N=5 stable with v0.36.0 + v0.37.0 added".

#### m4: Mid-slice smoke gate's `Remove-Item env:PYTHONIOENCODING` may fail if env var was never set

- **Claim under review**: mission-brief.md L100.
- **Builder response**: **ACCEPTED-FIXED** at mission-brief.md L100 — wrapped in `if ($env:PYTHONIOENCODING) { ... }`.

## Dimensions checked

- [x] Unfounded assumptions — B1 (methodology-changelog path), B3 (tests/decisions/ convention), B4 (test_row_*.py convention), M4 (intra-tools import convention), M7 (N=6 citation chain). All Dim 1 / Dim 9 sub-clause 2 (design.md mechanical tables vs canonical inventory) wins.
- [x] Missing edge cases — M1 (subprocess argv variance per audit tool), M6 (idempotency under errors-mode drift), m4 (PowerShell Remove-Item on absent env var).
- [x] Over-engineering — none. Helper ~25 LOC, audit ~120 LOC, 16 mechanical one-line additions. No speculative generality.
- [x] Under-engineering — B2 (PMI-1 fires on `_stdout.py` orphan; design hand-waves to /build-slice Step 1), B5 (audit output contract numbers internally contradictory), M1 (AC #4 lacks per-tool argv strategy).
- [x] Contract gaps — M3 (plugin.yaml entry shape wrong), M5 (single test file conflates unit + regression), B5 (audit JSON output miscount), M6 (helper idempotency edge).
- [x] Security — none. No new authn/authz/secrets/IDOR/injection surfaces.
- [x] Drift from vault — M2 (design.md L67+L176 claims 7 audits in Step 6 list; only 5 are), B1, B3, B4 (shadow conventions not in vault).
- [x] Web-known issues — Skipped (local-only Python stdlib `sys.stdout.reconfigure()` since Python 3.7; shared interpreter is 3.13; no post-cutoff platform-deprecation risk).
- [x] Cross-cutting conformance — Dim 9 sub-clause 6 (recursive-self-application): 4 of 5 Blockers (B1, B3, B4, M2) are exactly Dim 9 sub-clause 2 class on the slice's own draft. **Cross-mission-brief-vs-design-consistency-checking** (slice-022 NEW Critic-MISS class at N=1+) fired N=3 in this slice (B5 count drift + B3 ADR-pin path drift + M5 test-file path drift across mission-brief + design + ADR-021) — promotes that class toward N=3+ cumulative, ELIGIBLE for /critic-calibrate slice-024 promotion to Dim 9 sub-clause. **Fix-block-completeness on count-drift Blockers** (slice-020 M-add-1 watch-list at N=1+): applied at B5 fix sweep across 6 sibling surfaces (mission-brief AC #2 cell + design.md L120/121/130/131 + L225 + L344) — confirmed swept in single fix block this round.

## Triage

**Triaged by**: user
**Date**: 2026-05-15
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md + ADR-021 global replace_all `architecture/methodology-changelog.md` → `methodology-changelog.md` (verified zero post-fix matches via Grep) |
| B2 | Blocker | ACCEPTED-PENDING | At /build-slice: extend `tools/plugin_manifest_audit.py:_list_actual_tools` to filter `p.name.startswith("_")` + 2-assertion test in `test_plugin_manifest_audit.py::test_list_actual_tools_filters_leading_underscore_helpers` (per M-add B2 sub-recommendation: real `_stdout.py` filtered AND synthetic `_helper.py` filtered) |
| B3 | Blocker | ACCEPTED-FIXED | mission-brief.md TF-1 row 16 + design.md L50 + L286 + L335 updated to `tests/methodology/test_methodology_changelog.py::test_adr_021_present_and_reversibility_cheap` (verified ADR-pin convention via Grep `^def test_adr_` returning rows 013-020 all in test_methodology_changelog.py) |
| B4 | Blocker | ACCEPTED-FIXED | Dropped `test_row_023_utf8_stdout.py` file from all surfaces; shippability row 23 command cell re-enumerated to 9 invocation targets across 5 actual test files |
| B5 | Blocker | ACCEPTED-FIXED | Audit output canonical counts pinned 17/17/17 on clean; 6 sibling sites swept (mission-brief AC #2 + design.md L120-121 + L130-131 + L225 + L344); output-contract-invariant block added with 3 regression-guard prose-pinned assertions |
| M1 | Major | ACCEPTED-FIXED | design.md "Error model" surface 3 enumerates per-tool argv strategy; subprocess.run kwargs pinned (text=True, encoding=utf-8, errors=replace + PYTHONIOENCODING=cp1252, PYTHONUTF8=0); failure assertion targets UnicodeEncodeError/DecodeError in stderr (not exit code 0) |
| M2 | Major | ACCEPTED-FIXED | design.md L67 + L176 + L307 rewritten to enumerate actual 5-audit Step 6 list (LINT-MOCK-1, WIRE-1, BC-1, TF-1, BRANCH-1) per verified build-slice/SKILL.md L120-129 |
| M3 | Major | ACCEPTED-FIXED | design.md L295 entry shape switched to `- path: tools/utf8_stdout_audit.py / rule: UTF8-STDOUT-1` |
| M4 | Major | ACCEPTED-FIXED | design.md L36 + L149 + L289 pinned canonical `from tools import _stdout`; prose-pin test `test_every_tool_uses_canonical_from_tools_import_stdout` added to audit unit tests |
| M5 | Major | ACCEPTED-FIXED | Test split into `test_utf8_stdout_audit.py` (unit, AC #2 + #3) + `test_utf8_stdout_regression.py` (subprocess, AC #4); design.md L42-43 + Files-changed + TF-1 row 12 updated |
| M6 | Major | ACCEPTED-FIXED | design.md L86-95 helper body simplified — encoding short-circuit removed; docstring explains why unconditional reconfigure is correct (M-add-3 propagated same fix to ADR-021) |
| M7 | Major | ACCEPTED-FIXED | ADR-021 N=6 trail now cites shippability rows 20/21/22 cumulative-count provenance + slice-022 milestone.md L44 D-5 + validation.md L113 |
| M8 | Major | ACCEPTED-FIXED | Cumulative-Critic-influence note fully rewritten with predicted vs actual (≤5 predicted, 17 actual = 3.4× over per M-add-5 corrected math); catch-class breakdown enumerated; promotion-eligibility flagged for /critic-calibrate slice-024 |
| m1 | Minor | ACCEPTED-FIXED | ADR-021 L19-20 placeholders replaced: slice-007 2026-05-10, slice-016 2026-05-13 (looked up via archive/_index.md) |
| m2 | Minor | ACCEPTED-FIXED | ADR-021 L85 N=9-vs-N=3 conflation disambiguated: cross-slice ordinal vs within-slice surface count |
| m3 | Minor | ACCEPTED-FIXED | design.md L45 rule-of-three rephrased: "originally confirmed at N=3 entries v0.33.0/v0.34.0/v0.35.0; now N=5 stable with v0.36.0 + v0.37.0" |
| m4 | Minor | ACCEPTED-FIXED | mission-brief.md L100 wrapped: `if ($env:PYTHONIOENCODING) { Remove-Item env:PYTHONIOENCODING }` |
| M-add-1 | Major | ACCEPTED-FIXED | mission-brief.md L114 pre-finish gate "16 TF-1 rows" → "18 TF-1 rows" with inline breakdown (4×AC1 + 2×AC2 + 5×AC3 + 1×AC4 + 6×AC5) |
| M-add-2 | Major | ACCEPTED-FIXED | design.md per-tool argv strategy re-grouped per verified argparse contracts: install_audit→--claude-dir; mock_budget_lint→positional files; validate_slice_layers→--slice required; "no argv" group dissolved |
| M-add-3 | Major | ACCEPTED-FIXED | ADR-021 L57-69 helper body simplified (M6 fix propagated); docstring explains M6 + M-add-3 rationale inline |
| M-add-4 | Major | ACCEPTED-FIXED | 3 sibling sites updated to `test_utf8_stdout_regression.py`: design.md L194 (wiring matrix), mission-brief.md L54 (verification), ADR-021 L73 (behavioural regression reference) |
| M-add-5 | Minor | ACCEPTED-FIXED | design.md L251 + L260 + downstream Cumulative-Critic-influence prose updated: 13 → 17 first-Critic findings; new paragraph documents 6 meta-Critic missed = 23 cumulative |
| M-add-6 | Minor | ACCEPTED-FIXED | `supersedes: null` retained as correct per SUP-1 scope (no prior ADR-codified discipline to supersede; shell-side workaround was DEVIATION pattern, already documented in ADR-021 Context L17-24). No code change; verification recorded. |
