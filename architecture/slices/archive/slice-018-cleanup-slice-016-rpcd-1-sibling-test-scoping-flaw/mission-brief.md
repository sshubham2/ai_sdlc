# Slice 018: cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw

**Mode**: Standard
**Estimated work**: SMALL (~30 min Edit + verify) — narrow targeted scoping fix to one existing test + one NEW regression test, no methodology version bump, no SKILL.md changes, no ADR
**Risk retired**: NEW first-Critic-MISS class at N=1 from slice-017 reflection — "test-scoping-flaw-inherited-across-codification-slice-siblings" — retires latent regression risk on slice-016 RPCD-1 pin where `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` at `tests/methodology/test_methodology_changelog.py:910-951` uses global-substring scoping that would false-positive PASS if a future slice strips Sub-mode (a)/(b)/(c) markers from the v0.31.0 entry body, because v0.32.0+ entries still carry the markers
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Fix the global-substring scoping flaw at `tests/methodology/test_methodology_changelog.py:910-951` (slice-016 RPCD-1 sibling `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed`) so it scopes assertions to the v0.31.0 entry body — between `## v0.31.0` and `## v0.30.0` boundaries — mirroring the slice-017 TPHD-1 sibling pattern at L1086-1094 of the same file. Add a regression test that proves the scoping discipline by stripping Sub-mode markers from a synthetic v0.31.0 body and asserting the slice-016 sibling now correctly FAILS (whereas with the old global-substring scoping it would have spuriously PASSED).

This slice is a pure cleanup — no methodology version bump, no SKILL.md prose, no agents/critique.md change, no ADR. Per slice-017 reflection, this is the strongest slice-018 candidate (a) at latent-regression severity HIGH (silent test false-positive on a methodology pin is a methodology-correctness regression, not just a code regression).

## Acceptance criteria

1. `tests/methodology/test_methodology_changelog.py::test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` is refactored to scope content to `v031_body = content[v031_start:v030_start]` (mirroring slice-017 TPHD-1 sibling at L1086-1094); the function's 5 sub-mode + discipline-anchor assertions reference `v031_body` rather than raw `content`. Boundary-not-found edge case handled (`v030_start == -1` → use rest of file from `v031_start`).

2. NEW regression test `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body` proves the scoping discipline by constructing synthetic methodology-changelog content where only the v0.31.0 body has Sub-mode markers stripped (v0.32.0+ retains them) — asserts `"Sub-mode (a)" not in v031_body` on the synthetic content. Demonstrates the failure mode that the global-substring scoping flaw masked.

3. Test docstring at L911-924 updated to document the scoping fix with explicit reference to slice-017 DEVIATION-1 evidence anchor and slice-017 TPHD-1 sibling canonical pattern. Slice-017 NEW first-Critic-MISS class `test-scoping-flaw-inherited-across-codification-slice-siblings` retired inline at N=1 (no Dim 9 sub-clause needed; cleanup-only).

4. Full methodology test suite passes 405/405 (slice-017 baseline 404 + 1 NEW regression test); no regression on rows 1-17 of shippability catalog at `architecture/shippability.md`; `tools/test_first_audit.py --strict-pre-finish` clean on the slice's mission-brief TF-1 plan.

5. NO methodology-changelog version bump (this is a pure test-quality cleanup; PMI-1 v1.1 invariant gate stays at 0.32.0); NO SKILL.md prose changes; NO new ADR; NO agents/critique.md edits (CAD-1 byte-equality preserved through slice).

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed | PASSING |
| 2 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body | PASSING |
| 3 | grep-verification | tests/methodology/test_methodology_changelog.py | docstring at L911-? cites "slice-017 DEVIATION-1" (3 hits empirically verified at /build-slice Phase 6: L955 + L1018 + L1031) | PASSING |
| 4 | catalog-verification | architecture/shippability.md | full catalog 17/17 PASS no regression on rows 1-17 (infrastructure in place at /build-slice; full run at /validate-slice Step 5.5 per slice-017 row 5 precedent) | PASSING |
| 4 | mini-CAD-1 | tests/methodology/test_critique_agent_drift.py | test_critique_agent_md_byte_equal_in_repo_and_installed | PASSING |
| 5 | git-diff-verification | git diff master -- methodology-changelog.md VERSION plugin.yaml ~/.claude/ai-sdlc-VERSION agents/critique.md skills/critique/SKILL.md skills/critique-review/SKILL.md skills/build-slice/SKILL.md | returns empty diff (empirically verified at /build-slice Phase 6: git status --short returns no output across all 7 surfaces) | PASSING |

Total: 6 TF-1 rows at /build-slice Phase 6 (2 PENDING → WRITTEN-FAILING → PASSING for AC #1+#2 + 1 grep-verification for AC #3 + 1 catalog-verification for AC #4 + 1 mini-CAD-1 for AC #4 (stayed PASSING; no transition per /build-slice Phase 5 DEVIATION — slice-018 doesn't modify agents/critique.md) + 1 git-diff-verification for AC #5). Lower density than recent codification slices (slice-014: 8 rows; slice-015: 13; slice-016: 15; slice-017: 12) — reflects narrow cleanup scope.

**Original-draft framing** (per /critique M1 ACCEPTED-FIXED): AC #3 docstring was originally going to be verified at /validate-slice via single grep (NOT promoted to a TF-1 pytest row — docstring is code-comment, NOT methodology pin surface; meta-test on prose has no behavioral value per Fowler speculative-generality + Beck YAGNI). At /build-slice Phase 6, TF-1 audit `ac-without-row` violation surfaced because every AC needs at least one row regardless of test_type. Resolution: row added with `test_type = grep-verification` (NOT pytest) capturing the empirical Phase 6 grep result (3 hits at L955 + L1018 + L1031) — preserves M1's intent (no pytest meta-test on prose) while satisfying TF-1's coverage discipline.

Per /critique B1 + B2 + M1 ACCEPTED-FIXED Path A: TF-1 row 1 function name preserved as `_entry_names_three_sub_modes_in_repo_and_installed` (matches AC #1, design.md Decision L96, mid-slice smoke gate L87, verification plan row 1). TPHD-1 sub-mode (a) self-application: TF-1 plan harmonized in same /critique fix block as design.md decision (zero TF-1-plan-vs-design-decision drift).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Test scoped to v031_body | `grep -n "v031_body = content\[v031_start:v030_start\]" tests/methodology/test_methodology_changelog.py` returns 1 hit inside slice-016 RPCD-1 sibling function; manual Read confirms all 5 assertions reference `v031_body` |
| 2 | Regression test proves scoping | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body -q` returns 0 |
| 3 | Docstring documents fix | `grep -n "slice-017 DEVIATION-1" tests/methodology/test_methodology_changelog.py` returns 1 hit inside slice-016 RPCD-1 sibling docstring |
| 4 | Full suite + shippability catalog clean | `pytest tests/methodology -q` returns 0 with 405 PASS; manual shippability.md extraction at /validate-slice Step 5.5 → 17/17 PASS in <2 min |
| 5 | No methodology version bump | `git diff master -- methodology-changelog.md VERSION plugin.yaml ~/.claude/ai-sdlc-VERSION` returns empty diff (slice changes ONLY `tests/methodology/test_methodology_changelog.py` + shippability row 17 entry if catalog reorder needed + slice vault folder) |

## Must-not-defer

- [ ] Input validation: boundary-not-found edge case — when `## v0.30.0` is absent from the file (e.g., truncated test fixture), the scoping logic falls back to `v031_body = content[v031_start:]` per slice-017 TPHD-1 sibling L1091-1094 precedent. Verification: synthetic content with no `## v0.30.0` boundary makes the test logic resolve correctly (regression test covers this branch).
- [ ] Assertion preservation: all 5 existing Sub-mode + discipline-anchor assertions (`"Sub-mode (a)"`, `"Sub-mode (b)"`, `"Sub-mode (c)"`, `"_ALLOWED_STATUSES"`, `"sibling"`) preserved verbatim; only the haystack changes from `content` to `v031_body`. Verification: assertion error messages reference `v0.31.0 body` not `v0.31.0` generic.
- [ ] CAD-1 byte-equality on `agents/critique.md` preserved through slice (slice does NOT touch agents/critique.md; bidirectional sha256 forensic capture confirms byte-equal in-repo↔installed at slice end at same hash as slice-017 ship `f34c967eaaa34413...`).
- [ ] EPGD-1 self-application: 0 of 15 prior entry-pin functions (v0.22.0..v0.32.0; 12 from slice-017 + 3 NEW v0.32.0 TPHD-1 functions per slice-017 EPGD-1 self-application count) touched by slice-018's edit. The edit is INTERNAL to `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` (one of the 12 prior v0.31.0 entry-pin functions) — refactoring its BODY does not violate EPGD-1's structural-separation discipline, which guards against accidental SUPERSESSION of prior entry-pin functions via PMI-1 gate Edit. Verification: `grep -c "^def test_v_0_" tests/methodology/test_methodology_changelog.py` returns 15 both pre-edit and post-edit.
- [ ] PMI-1 v1.1 invariant: NO version bump this slice (cleanup-only). `plugin.yaml.version` stays 0.32.0, `VERSION` stays 0.32.0, `~/.claude/ai-sdlc-VERSION` stays 0.32.0. PMI-1 v1.1 gate `test_plugin_yaml_version_matches_version_file_invariant` continues to PASS unchanged.
- [ ] BC-1 self-application: methodology-vocabulary slices recur with negative-anchor false-positive class (N=5+ cumulative); slice-018 should be silenced by BC-PROJ-2 negative-anchor migration from slice-012. **Verified empirically at /critique fix-prose**: `$PY -m tools.build_checks_audit --slice <slice-folder> --changed-files mission-brief.md design.md` returned literal output `"No build-checks rules apply to this slice."` Recorded in design.md as Audit 5 per /critique m3 ACCEPTED-FIXED.
- [ ] No new TODOs / FIXMEs / debug prints in any test file edit.
- [ ] Test docstring quality: cite slice-017 DEVIATION-1 evidence anchor explicitly + cite slice-017 TPHD-1 sibling canonical pattern at L1086-1094 of same file; future readers should be able to trace the fix back to its lesson source.
- [ ] Regression test demonstrates real failure mode: synthetic content MUST construct a v0.31.0 body that loses Sub-mode markers WHILE v0.32.0+ retains them — proves the scoping fix catches what the global-substring scoping missed.
- [ ] SCPD-1 proactive-application: slice-018 has NO Dim 9 sub-clause supersession; `_lists_nine_sub_clauses` stays valid; no shippability row count change unless test count changes meaningfully (1 NEW test + 1 EDIT of existing test → row 16 pytest command may need a `_scopes_to_v031_body` or `_rejects_stripped_v031_body` reference if propagation is warranted; verify at /design-slice).

## Out of scope

- Methodology version bump — this is a cleanup slice; PMI-1 v1.1 stays at 0.32.0. No methodology-changelog.md entry.
- SKILL.md prose changes — TPHD-1 codification at slice-017 already covers `/critique` + `/critique-review` + `/build-slice` discipline; this slice retires a test-quality gap, not a methodology gap.
- `agents/critique.md` Dim 9 10th sub-clause for `test-scoping-flaw-inherited-across-codification-slice-siblings` — N=1 only; defer until N=2 if recurs at slice-019+. Slice-017 reflection explicitly defers Dim 9 promotion to N=2.
- `tools/test_scoping_audit.py` standalone audit tooling — v2 candidate; defer until N=3 recurrence post-cleanup.
- Updating any OTHER `_names_N_sub_modes` test in the codebase — empirical grep at /design-slice will confirm only slice-016 RPCD-1 sibling has the flaw (slice-017 TPHD-1 sibling at L1055-1121 already has correct scoping per L1086-1094).
- ADR creation — cleanup slice, not an architecture change; ADR-pin convention N=4 stable doesn't extend to test-quality fixes.
- Open R-1 (cwd-mismatch `/diagnose`) + R-2 (no programmatic `/diagnose` warning test) — stale risks since slice-001/002; untouched for 16 slices; require `/repro` first.
- Windows cp1252 console encoding workaround — **N=3 cumulative at slice-018** (slice-007 + slice-016 + slice-018; the `tools/critique_review_audit.py` console output at /critique-review fix-prose hit it with U+2192 right-arrow `→`; workaround `PYTHONIOENCODING=utf-8` applied inline). **N=3 promotion threshold MET** per project convention. Out-of-scope for slice-018 (cleanup focuses on RPCD-1 sibling scoping flaw) but separate candidate `audit-tools-default-utf8-stdout` is now promotable at slice-019+. Flag for /reflect.
- **Boundary-find inline-prose collision tightening** (NEW watch-list at N=1 from /critique M3 ACCEPTED-FIXED option (b)) — `content.find("## v0.31.0")` matches first occurrence; could collide with future inline-prose reference to `"## v0.31.0"` in a later-version body's narrative. Chose deferral over tightening to `\n## v0.31.0` because: (1) today's methodology-changelog.md has no inline-prose collision (empirically verified — `## v0.31.0` and `## v0.30.0` are unique heading-only occurrences); (2) tightening would break symmetry with slice-017 TPHD-1 sibling canonical pattern at L1086 (design.md Audit 3 "Pattern reproduces verbatim" assertion); (3) cleanup-slice scope should not retrofit slice-017. Promote to a future cleanup slice if inline-prose collision actually surfaces (N=2 promotion threshold per project convention).

## Dependencies

- Prior slices: [[slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class]] — sibling test source at L910-951 (the target of this cleanup); [[slice-017-address-tf-1-plan-staleness-discipline]] — DEVIATION-1 evidence anchor + canonical scoping pattern at L1086-1094 of same file (the template to mirror)
- Vault refs: [[tests/methodology/test_methodology_changelog.py]] (sibling test target at L910-951; canonical pattern at L1086-1094), [[architecture/shippability.md]] (row 16 RPCD-1 reference may need pytest command update if propagation needed)
- Risk register: no entries — test-scoping-flaw is a methodology-internal lesson at N=1, not a registered risk; no risk-register changes expected this slice

## Mid-slice smoke gate

At ~50% of build (after refactoring `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` to scoped form, BEFORE writing regression test):

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant tests/methodology/test_critique_agent_drift.py -q
```

Expected: 3 PASS (refactored sibling test + PMI-1 v1.1 invariant + CAD-1 byte-equality on agents/critique.md). If fails: STOP, diagnose. Sibling test fail would mean scoping boundary slicing has a bug (e.g., `v031_start` returns -1, or `v030_start` lookup not anchored to `v031_start` offset). PMI-1 fail would mean version files accidentally touched (this slice should NOT bump versions). CAD-1 fail would mean agents/critique.md was accidentally edited (this slice should NOT touch agents/critique.md).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (10 items)
- [ ] `tools/test_first_audit.py --strict-pre-finish` clean on slice's mission-brief TF-1 plan
- [ ] /drift-check passes (no vault drift introduced)
- [ ] Mid-slice smoke still passes (no regression on PMI-1 + CAD-1 + refactored sibling test)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full methodology test suite 405/405 PASS at /validate-slice Step 5.5
- [ ] Shippability catalog 17/17 rows PASS no regression on rows 1-17
- [ ] No git diff on `methodology-changelog.md` / `VERSION` / `plugin.yaml` / `~/.claude/ai-sdlc-VERSION` (cleanup-only; no version bump)
- [ ] No git diff on `agents/critique.md` / `skills/critique/SKILL.md` / `skills/critique-review/SKILL.md` / `skills/build-slice/SKILL.md` (CAD-1 + SKILL preservation)
