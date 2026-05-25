# Critique: Slice 018 cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw

**Critic reviewed**: mission-brief.md, design.md, no new ADRs (cleanup slice)
**Date**: 2026-05-13
**Result**: NEEDS-FIXES (pre-triage); see ## Triage for final verdict

## Summary

The intent is sound and the regression-test approach is technically correct — but the slice ITSELF commits the exact discipline-class violation (TPHD-1 sub-mode (a/b) TF-1-plan staleness vs. design-decision drift) the recently-codified rule was meant to catch. design.md decides "preserve function name" while mission-brief.md TF-1 plan rows 1 and 3 carry NEW function names. This is a recursive-self-application failure at design-time — exactly what Dim 9 sub-clause 6 (RSAD-1) flags as load-bearing for codification-adjacent slices. Additionally, the regression test as designed is partially tautological, the proposed docstring "test" (AC #3, TF-1 row 3) is meta-prose-testing with no behavioral value, and the boundary-overlap edge case is hand-waved in Audit 1.

## Findings

### Blockers (must address before /build-slice)

#### B1: TPHD-1 self-application failure — design.md "preserve name" decision contradicts mission-brief.md TF-1 plan rows 1 + 3

- **Claim under review**: design.md L96-103 Decision section: "preserve name. Rationale: ... EPGD-1 self-application stays vacuous at the function-name level (0 of 15 touched)". AND mission-brief.md L18 AC #1: "test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed is refactored to scope content..."
- **Issue**: design.md decides to PRESERVE the function name. AC #1 references this preserved name. BUT mission-brief.md TF-1 plan (L34) row 1 lists the test as `_scopes_to_v031_body` — a DIFFERENT name. TF-1 row 3 (L36) introduces `_sibling_docstring_documents_slice_017_scoping_fix` which design.md regression-test sketch L120-165 never plans (sketch only mentions `_rejects_stripped_v031_body`). Per TPHD-1 sub-mode (a) (methodology-changelog.md L44), this is the discipline class — "test function names or AC #N row references in mission-brief.md or design.md" must be harmonized in the same fix block. The slice retiring `test-scoping-flaw-inherited-across-codification-slice-siblings` ships with TF-1-plan-vs-design-decision staleness on its OWN draft. RSAD-1 design-time-mode violation per slice-011/013 precedent: codification-adjacent slice commits the rule's own violation class on own draft.
- **Evidence**: design.md L85/L96/L98 + mission-brief.md L34/L36/L84/L87 + methodology-changelog.md L44 (TPHD-1 sub-mode (a) canonical anchor) + archive/slice-017/validation.md L97.
- **Proposed fix**: Path A (recommended): keep design.md "preserve name"; mission-brief.md TF-1 row 1 Test function = `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` (preserved). Verification row 1 already correctly greps for `v031_body` substring inside the preserved function. Delete TF-1 row 3 (see M1). OR Path B: rename + flip design.md to Option 2; shippability row 16 propagation needed.
- **Builder draft**: **ACCEPTED-FIXED** — Path A chosen. Apply to mission-brief.md: TF-1 row 1 function name = `_entry_names_three_sub_modes_in_repo_and_installed` (preserved); TF-1 row 3 deleted per M1; row total = 4 (down from 5). design.md Decision L96 stays Option 1; consistency now holds across design.md + AC #1 + TF-1 plan + mid-slice smoke gate (L87) + verification plan.

#### B2: AC #1 internal contradiction — preserves function name BUT TF-1 row 1 names a different function

- **Claim under review**: mission-brief.md L18 AC #1 (preserved name) vs L34 TF-1 row 1 (NEW name `_scopes_to_v031_body`).
- **Issue**: AC #1 says the function NAMED `_in_repo_and_installed` is refactored. TF-1 row 1 says a NEW function NAMED `_scopes_to_v031_body` is built. Mutually exclusive deliverables. Status PENDING + `tools/test_first_audit.py` status-only check (methodology-changelog.md L39, L70) cannot detect the inconsistency — function-name-staleness mode NOT caught by TF-1 audit per slice-017 reflection.
- **Evidence**: mission-brief.md L18 + L34 + L57 (must-not-defer assumes preservation); methodology-changelog.md L39/L46/L70.
- **Proposed fix**: Resolved as consequence of B1 Path A — TF-1 row 1 function name = `_entry_names_three_sub_modes_in_repo_and_installed`.
- **Builder draft**: **ACCEPTED-FIXED** — consequence of B1 fix.

### Majors (address this slice)

#### M1: TF-1 plan row 3 (docstring-documents-fix test) is over-engineering — testing prose comments

- **Claim under review**: mission-brief.md L36 TF-1 row 3 `_sibling_docstring_documents_slice_017_scoping_fix` + L48 verification grep.
- **Issue**: Per Fowler (speculative generality) + Beck (YAGNI), this is meta-test on prose with no behavioral value. The docstring is not load-bearing methodology surface (unlike `agents/critique.md` Dim 9 sub-clause titles which ARE pins). Pinned-prose tests are reserved for methodology-vocabulary surfaces (`agents/critique.md`, `skills/*/SKILL.md`, `methodology-changelog.md`). A docstring on a test function is a code-comment, NOT a methodology surface. Verification plan row 3 accomplishes the same check via a single grep at /validate-slice — no dedicated pytest needed. Adding a test inflates count (405 → 406) for prose future devs WILL legitimately edit (a docstring rewrite via /critic-calibrate or /reflect would silently break the test).
- **Evidence**: mission-brief.md L36 + L48; design.md L120-165 (doesn't plan this test); design.md L88-89.
- **Proposed fix**: Delete TF-1 row 3; reduce total to 4 rows; AC #3 partially preserved as "docstring update at L911-924 with explicit citation of slice-017 DEVIATION-1 + slice-017 TPHD-1 sibling canonical pattern at L1086-1094" — verified at /validate-slice via grep, NOT pytest.
- **Builder draft**: **ACCEPTED-FIXED** — TF-1 row 3 deleted; AC #3 retained as documentation requirement; verification grep stays.

#### M2: Regression test is partially tautological — proves only that the test author wrote synthetic content correctly, not that the discipline catches real-world drift

- **Claim under review**: design.md L120-165 regression-test sketch.
- **Issue**: Per Hendrickson — a regression test that constructs synthetic content AND then asserts properties OF that synthetic content tests the fixture-construction author's hand, not the underlying discipline. The sibling test (L910-951 refactored) reads the REAL `methodology-changelog.md` via `read_file()` (L925), not synthetic. The proposed regression test exercises boundary-slicing in isolation but doesn't actually prove the sibling test's CALL to that logic would fail on stripped content. Link is established only by code-reading, not execution.
- **Evidence**: design.md L120-165; tests/methodology/test_methodology_changelog.py:925-927.
- **Proposed fix**: Extract `_extract_v031_body(content: str) -> str` helper at module level; BOTH refactored sibling test AND regression test call it. Regression test then proves: `assert "Sub-mode (a)" not in _extract_v031_body(synthetic)` — exercises the same code path the sibling uses. (Slice-014 DEVIATION-1 monkeypatch alternative also viable but more complex.)
- **Builder draft**: **ACCEPTED-FIXED** — helper extraction adopted. design.md regression-test design section updated to plan module-level `_extract_v031_body(content: str) -> str` helper; refactored sibling test calls helper for its real-file scoping; regression test calls helper for synthetic-content scoping. Single code path under test.

#### M3: Audit 1 "ONLY slice-016 RPCD-1 sibling has the flaw" is empirically incomplete — boundary-overlap edge case not checked

- **Claim under review**: design.md L169-176 Audit 1.
- **Issue**: `v031_start = content.find("## v0.31.0")` matches FIRST occurrence. If a later-version body contains `"## v0.31.0"` as quoted narrative or inside a code block, `find()` returns the wrong boundary. Today's `methodology-changelog.md` has no such drift, but the design has zero defense. Critic offers (a) tighten to `content.find("\n## v0.31.0")` for newline-anchored matching OR (b) defer to /reflect watch-list as N=1 candidate.
- **Evidence**: design.md L169-176; methodology-changelog.md L82-L142 (retrospective cross-references prove the codebase routinely mentions prior versions inside later-version prose, though not as exact heading literals today); `find` semantics first-occurrence-wins.
- **Proposed fix**: ONE of: (a) Tighten + add 2nd regression assertion; (b) Defer to /reflect watch-list.
- **Builder draft**: **ACCEPTED-FIXED** — chose Critic option (b): defer to /reflect watch-list. Rationale: today's methodology-changelog.md has no inline-prose collision (empirically verified — `## v0.31.0` and `## v0.30.0` are unique heading-only occurrences); tightening would break symmetry with slice-017 TPHD-1 sibling canonical pattern at L1086 (design.md Audit 3 "Pattern reproduces verbatim" assertion would become false); cleanup slice scope should not retrofit slice-017. Added to mission-brief.md out-of-scope as new bullet + design.md as Audit 6 acknowledging the limitation.

#### M4: Hidden coupling — design.md SCPD-1-proactive-application claim that "shippability row 16 unchanged" assumes Path A function-name preservation but doesn't enumerate the row 16 pytest command

- **Claim under review**: design.md L67-71 SCPD-1 lesson application + mission-brief.md L63 must-not-defer.
- **Issue**: Per CCC-1 v1.1 sub-clause 2 — design.md asserts row 16 unchanged but must-not-defer L63 says verification of row 16 propagation occurs at /design-slice (which IS this slice). Did design author EMPIRICALLY check row 16 pytest command? Row 16 enumerates ~12 pytest commands; SCPD-1 sub-mode (b) proactive-application requires enumerating the consumer-references explicitly.
- **Evidence**: design.md L67-71 + mission-brief.md L63; shippability.md L24 row 16; methodology-changelog.md L116-143 SCPD-1 canonical body.
- **Proposed fix**: At /design-slice, explicitly enumerate row 16 dependency on preserved name.
- **Builder draft**: **ACCEPTED-FIXED** — Empirically verified at /critique fix-prose: shippability.md row 16 (line 24) is the slice-016 RPCD-1 row; it contains `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` as exactly 1 of ~12 pytest commands. Per Path A (preserve name), row 16 stays unchanged this slice. SCPD-1 proactive-application vacuously satisfied. Recorded in design.md as Audit 4.

### Minors (log; address if cheap)

#### m1: Audit 3 boundary-slice pattern reproduction "verbatim" understates the v030_start fallback risk

- **Claim under review**: design.md L194 "Pattern reproduces verbatim..."
- **Issue**: Mechanical "verbatim replace" is correct, but fallback branch (`v030_start == -1`) has different semantics: for v0.31.0 ↔ v0.30.0, fallback triggers only if v0.30.0 is DELETED (extraordinary). Could legitimately use `assert v030_start != -1`. Minor design choice.
- **Proposed fix**: (a) keep fallback for symmetry with slice-017 canonical (lower churn); (b) assert + remove fallback branch. Document the choice.
- **Builder draft**: **ACCEPTED-FIXED** — chose (a) keep fallback for symmetry with slice-017 canonical pattern at L1091-1094. Documenting the choice in the refactored function docstring (added paragraph: "Fallback branch retained for symmetry with slice-017 TPHD-1 sibling canonical pattern at L1091-1094, though triggers only if v0.30.0 entry is deleted — an extraordinary regression beyond this slice's threat model").

#### m2: "Possible shippability.md row 16 update" in design.md L13-14 is conditionally hedged but never resolved

- **Claim under review**: design.md L13-14 conditional hedge.
- **Issue**: Decision section commits to Option 1 (preserve name) so the conditional resolves to "no row 16 propagation needed". The hedge remains in text as if undecided.
- **Proposed fix**: Rewrite L13-14 unconditionally per Decision.
- **Builder draft**: **ACCEPTED-FIXED** — design.md L13-14 rewritten to: "Per Decision L96 (preserve name) + Audit 4 (shippability row 16 empirical verification), shippability.md row 16 is unchanged this slice. SCPD-1 proactive-application: vacuous."

#### m3: Out-of-scope claim L67 / mission-brief.md "BC-1 self-application should be silenced by BC-PROJ-2" is asserted, not verified

- **Claim under review**: mission-brief.md L59 must-not-defer assertion.
- **Issue**: Per Wiegers — every claim traces to evidence. The mission-brief says "should be silenced" but no design-time empirical run is documented.
- **Proposed fix**: Run BC-1 audit at /design-slice and record output.
- **Builder draft**: **ACCEPTED-FIXED** — ran at /critique fix-prose: `$PY -m tools.build_checks_audit --slice <slice-folder> --changed-files mission-brief.md design.md` returned literal output: `"No build-checks rules apply to this slice."` — BC-PROJ-2 negative-anchor migration from slice-012 silences this slice's methodology vocabulary as predicted. Recorded in design.md as Audit 5.

## Dimensions checked

- [x] **Unfounded assumptions (Wiegers / Cockburn)** — B1 + B2 + M3 + m3. "preserve name" decision contradicted by TF-1 plan + AC text. Audit 1 doesn't probe boundary-overlap. BC-1 silencing asserted not empirically verified.
- [x] **Missing edge cases (Hendrickson / Bach)** — M3 + m1. Inline-prose collision not covered; v0.30.0 fallback dead code.
- [x] **Over-engineering (Fowler / Beck)** — M1. TF-1 row 3 docstring meta-test has no behavioral value.
- [x] **Under-engineering (Wiegers / Patton)** — B1 + B2. AC #1 + TF-1 row 1 structurally ambiguous; status-only TF-1 audit cannot detect.
- [x] **Contract gaps (Newman / Fielding)** — none. No API/endpoint/event/integration; pure test-file refactor.
- [x] **Security (OWASP / McGraw)** — none. No auth/authz/input/data-exposure paths.
- [x] **Drift from vault (Sommerville / 42010)** — B1 + M4. Design decision inconsistent with mission-brief TF-1 plan; SCPD-1 row-16 propagation claim hedged conditionally without empirical enumeration.
- [x] **Web-known issues** — skipped (no third-party APIs, platforms, library versions).
- [x] **Cross-cutting conformance (Kiczales)** — B1 (RSAD-1 design-time-mode + TPHD-1 sub-mode (a) on own draft) + M3 + M4 (Methodology-audit conformance — TF-1 row coverage + boundary-anchor under Algorithm-path-conformance) + m3 (Tooling-doc-vs-implementation parity — BC-1 silencing assertion not empirically verified).

## Triage

**Triaged by**: user (auto-ratified per session-level "work without stopping" instruction; all dispositions are ACCEPTED-FIXED with explicit rationales captured above; reconciles BOTH first-Critic + meta-Critic findings per /critique-review DR-1 dual-review v0.17.0)
**Date**: 2026-05-13
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Path A (preserve name); TF-1 row 1 = preserved name; TF-1 row 3 deleted per M1; design.md Option 1 stays consistent across all surfaces |
| B2 | Blocker  | ACCEPTED-FIXED | Consequence of B1 fix — TF-1 row 1 harmonized to preserved name |
| M1 | Major    | ACCEPTED-FIXED | TF-1 row 3 deleted; AC #3 retained as documentation grep at /validate-slice, not pytest function |
| M2 | Major    | ACCEPTED-FIXED | Extract `_extract_v031_body(content)` helper at module level; both refactored sibling + regression test call it; single code path under test |
| M3 | Major    | ACCEPTED-FIXED | Chose Critic option (b) — defer to /reflect watch-list as N=1 candidate; preserve symmetry with slice-017 canonical pattern; today's file has no inline-prose collision |
| M4 | Major    | ACCEPTED-FIXED | Empirically verified row 16 contains preserved name as 1 of ~12 pytest commands; per Path A row 16 unchanged; SCPD-1 vacuous; recorded as Audit 4 |
| m1 | Minor    | ACCEPTED-FIXED | Keep fallback for symmetry with slice-017 canonical at L1091-1094; document choice in refactored function docstring |
| m2 | Minor    | ACCEPTED-FIXED | design.md L13-14 hedge cleaned up per Path A decision |
| m3 | Minor    | ACCEPTED-FIXED | BC-1 audit run empirically: "No build-checks rules apply to this slice"; recorded as Audit 5 |
| m-add-1 | Minor | ACCEPTED-FIXED | Meta-Critic catch: helper-internal assert loses surface_name diagnostic context vs slice-017 canonical pattern at L1088-1090. Chose option (a) — move `assert v031_start != -1` back to call site INSIDE the `for surface_name, content in [...]` loop with `f"{surface_name} ..."` error message; helper assumes pre-validated input. Preserves slice-017 symmetry + Hendrickson "self-explaining failures" discipline. design.md helper + sibling-test sketches updated at /critique-review fix-prose. |
| m-add-2 | Minor | ACCEPTED-FIXED | Meta-Critic catch: helper-extraction asymmetry vs slice-017 inline boundary-slicing; Audit 3 "Pattern reproduces verbatim" claim was stale post-M2 fix. Updated Audit 3 to acknowledge symmetry is at boundary-slicing-pattern level (find + assert + fallback), NOT literal-code level. Added Audit 7 explicitly declining generic `_extract_version_body(content, start_marker, end_marker)` foreshadowing at N=1 (YAGNI; promote at N≥2 if future slice introduces a second `_extract_vNN_body` need). |
| m-add-3 | Minor | ACCEPTED-FIXED | Meta-Critic catch: design.md L371 "Pre-smoke verification: Confirm `## v0.30.0` exists in `methodology-changelog.md` (both in-repo + installed)" was committed but Audit 6 only verified in-repo. Empirically verified at /critique-review fix-prose: `grep -c "^## v0.30.0" <installed-path>` = 1; `grep -c "^## v0.30.0" <in-repo-path>` = 1. Audit 6 updated with bidirectional empirical evidence. |
