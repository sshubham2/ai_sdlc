# Critique: Slice 057 retire-r15-via-slice-034-resolve-slice-dir-retrofit

**Critic reviewed**: mission-brief.md, design.md (no new ADRs — this slice mints zero)
**Date**: 2026-05-21
**Result**: NEEDS-FIXES (Builder draft pending user TRI-1; pending /critique-review)

## Summary

First-Critic returned **0 Blockers, 1 Major, 4 Minors** on slice-057. The Major (M1) is a real verification-path gap — mid-slice smoke gate omitted the new shippability row-#57 traceability-pin test that AC5 + design.md §5 introduce. Three minors flag mechanical drift between mission-brief / design.md / on-disk state (line numbers, line spans, terminology). m4 is a no-fix-required item recommending build-log explicit audit-enumeration. Zero-false-alarm streak now N=10 cumulative on codification-class slices (046/048/050/051/052/053/054/055/056/057 — the slice-037 audit-vs-real-artifact interaction-law trend continues).

## Findings

### Blockers (must address before /build-slice)

(none)

### Majors (address this slice)

#### M1: Mid-slice smoke gate omits the new shippability row #57 traceability-pin test, contradicting design.md §"Test plan additions" + AC5

- **Claim under review**: The mission-brief "Mid-slice smoke gate" runs only `test_slice034_prose_test_function_is_not_false_positive` + `test_no_new_archive_fragile_literals_in_methodology_corpus` "at ~50% of build (after the retrofit + whitelist shrink, before R-15 status flip)". design.md §"What's new" item 5 introduces a NEW test `test_shippability_row_57_present_and_cites_r15` (slice-056 row-#56 structural twin), and AC5 (verification row #5) requires the row to be present.
- **Issue**: Per Wiegers (every AC must have an observable success criterion delivered by the design) and per the slice-014/015 SCPD-1 lessons codified in Dim 9, a row-#57 test authored at design.md §5 must run somewhere in the pre-finish gate to actually verify the row exists. The mid-slice smoke gate as specified does not run it; the pre-finish gate prose says "All Step 6 audits clean" + "shippability.md row #57 present" but doesn't enumerate the new test by name. The slice-056 precedent (row #56) wired the row-#56 test into shippability row #56's own `Command` cell, which is the proactive SCPD-1 propagation mode. This slice's design.md §"What's new" item 4 says the row #57 `Command` cell "MUST run at least" the three named tests — but the mid-slice smoke gate only references two of them, creating an asymmetry between the mid-slice gate (2 tests) and the row-#57 pin (3 tests). A future maintainer reading mission-brief will see the mid-slice smoke as the "two tests that must pass after the retrofit" and may not realize the new traceability pin exists.
- **Evidence**: mission-brief.md "Mid-slice smoke gate" (pre-fix listed 2 tests); design.md §"What's new" item 4 (row #57 `Command` cell must run 3 tests); design.md §"What's new" item 5 (new test function); AC5 mentions "row #57 present" but not the pinning test by name; slice-056 row-#56 precedent at shippability.md:66 includes `test_shippability_row_56_present_and_cites_r15` in its `Command` cell.
- **Proposed fix**: Either (a) extend the mid-slice smoke gate to a 3-test list including `test_methodology_changelog.py::test_shippability_row_57_present_and_cites_r15` so the new traceability pin gets executed at the same 50% checkpoint it's authored at; OR (b) explicitly note in mission-brief that the row-#57 pin is authored AFTER the row is written (at ~90%, per slice-056 row-#56 author-after-row sequencing), and add an explicit Pre-finish-gate checkbox "`test_shippability_row_57_present_and_cites_r15` PASSes" so AC5's verification path is anchored. Either is acceptable; Critic recommends (a) since the row insert can land before the mid-slice gate (it's a one-line append), keeping the verification trail simple.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md "Mid-slice smoke gate" + "Pre-finish gate" — applied BOTH (a) AND (b) belt-and-suspenders: mid-slice smoke gate now lists all three tests (adding `test_shippability_row_57_present_and_cites_r15`), and the pre-finish gate gains an explicit checkbox `tests/methodology/test_methodology_changelog.py::test_shippability_row_57_present_and_cites_r15 PASSes`. The pre-finish checkbox carries the rationale "anchor for AC5's verification path; the new row-#57 BCR-1-traceability-axis pin must fire at pre-finish, not just be assumed-present". Mid-slice gate prose extended with the third FAIL-mode diagnostic ("row #57 insert hasn't landed yet OR doesn't cite R-15").

### Minors (log; address if cheap)

#### m1: Mission-brief AC1 + design.md cite line numbers 69-72 for the pre-edit literal; risk of propagating stale `:70-71` citations into the new slice-057 retirement paragraph

- **Claim under review**: mission-brief AC1 "The multi-line literal `REPO_ROOT / "architecture" / "slices" / "archive" / "slice-034-fix-tf1-audit-field-line-regex" / "mission-brief.md"` is replaced with `_resolve_slice_dir(34) / "mission-brief.md"`".
- **Issue**: Per Wiegers / Cockburn (make assumptions explicit) — verified on disk: lines 69-72 in `test_ptffd1_no_false_positive.py` are a 4-line parenthesized construction beginning at line 69 with `slice034 = (` and ending line 72 with `)`. The 1-line post-edit form means lines 73-79 (which read `assert slice034.is_file()`, etc.) will shift up by 3 lines. The corpus backstop's whitelist entry `("tests/methodology/test_ptffd1_no_false_positive.py", 70)` is being removed, so no line-number-tracking consumer breaks. But: the slice-056 risk-register paragraph (preserved verbatim per design.md §"Components touched"/risk-register.md edit shape) cites `test_ptffd1_no_false_positive.py:70-71` and `(line 70-71)` in TWO places (risk-register.md:259, also reproduced inline in design.md "Specific archived reflections"). These citations will become structurally stale (the literal is gone, line 70-71 no longer carries it). This is not a regression — historical record of slice-056's then-current state — but the new slice-057 retirement paragraph should NOT itself cite a stale `:70-71` line number.
- **Evidence**: Read of `test_ptffd1_no_false_positive.py` confirms 4-line construction L69-72; risk-register.md:259 cites `:70-71`; design.md §"Specific archived reflections" reproduces the same citation verbatim.
- **Proposed fix**: When authoring the new slice-057 retirement paragraph (design.md §"What's new" item 3), cite the pre-edit position as `test_ptffd1_no_false_positive.py:69-72` (matching the actual 4-line span at edit time) OR cite the line position abstractly ("the slice-034 archive-path literal previously at `test_ptffd1_no_false_positive.py:69-72`"). Do NOT propagate `:70-71` into the new paragraph. Existing slice-056 paragraph stays verbatim (historical record).
- **Builder draft**: ACCEPTED-FIXED at design.md §"What's new" item 3 — instruction now reads explicitly "the literal repoint at `test_ptffd1_no_false_positive.py:69-72` (the PRE-EDIT 4-line parenthesized construction span — per /critique m1 ACCEPTED-FIXED, cite `:69-72` not `:70-71`; the post-edit 1-line form shifts subsequent lines up by 3, so propagating the slice-056-era `:70-71` citation into the new paragraph would be structurally stale on landing — the slice-056 paragraph at risk-register.md:259 keeps `:70-71` as historical record of its then-current state)". This is a Builder-discipline instruction for the /build-slice author, not a content edit to slice-056's existing paragraph (which stays verbatim per the slice-040 R-10 retirement precedent).

#### m2: design.md "Edit shape" for `_R15_CORPUS_WHITELIST` says "6-line constant block"; verified the on-disk constant is L214-220 (7 lines), and mission-brief AC3 cites lines 214-218

- **Claim under review**: mission-brief AC3 "`_R15_CORPUS_WHITELIST` in `tests/methodology/test_resolve_slice_dir.py:214-218`"; design.md §"Components touched" "Lives at `tests/methodology/test_resolve_slice_dir.py:214-220`".
- **Issue**: Per Wiegers — internal consistency across slice artifacts. Verified on disk: the constant block runs from line 214 (`_R15_CORPUS_WHITELIST: set[tuple[str, int]] = {`) to line 220 (`}`). The AC3 line span cites `:214-218` while design.md cites `:214-220`. This is an FBCD-1 sub-mode (a) original-draft cross-file consistency drift — mission-brief and design.md should agree on the line span.
- **Evidence**: `test_resolve_slice_dir.py:214` opens with `_R15_CORPUS_WHITELIST: set[tuple[str, int]] = {` and `:220` closes with `}`. Mission-brief AC3 (pre-fix) said `:214-218`; design.md says `:214-220`.
- **Proposed fix**: Align both to `:214-220` (the correct closing-brace line).
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md AC3 — changed `:214-218` → `:214-220` to align with design.md and the on-disk truth.

#### m3: design.md §"R-15 retirement-discharge classification" item 1 lists "the M-add-2 corpus class-closure backstop mechanism are all already in the methodology surface as of slice-056" — but tests are not "methodology surface" in the META-1/MEPD-1 sense

- **Claim under review**: design.md §"R-15 retirement-discharge classification (MEPD-1(b) discharge mechanics)" item 1: "R-15 itself, the `_resolve_slice_dir(NNN)` helper contract, AND the M-add-2 corpus class-closure backstop mechanism are all already in the methodology surface as of slice-056".
- **Issue**: Per Wiegers / Sommerville — terminology precision. The "methodology surface" in MEPD-1's prose specifically refers to `skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`, and in-house audits (per the critique-skill prompt Dim 7 verbatim). `tests/methodology/*.py` and `tests/methodology/conftest.py` are TEST surfaces that PIN methodology, not methodology-surface tools. The slice's MEPD-1(b) discharge reasoning is correct in the META-1-assertion-vacuously-satisfied sense (item 3), but item 1's rhetorical scaffolding overstates the case. This is minor because the META-1 vacuous-satisfaction argument carries the discharge regardless.
- **Evidence**: design.md §"R-15 retirement-discharge classification" item 1; critique-skill prompt Dim 7 "When a slice changes behaviour on an in-house methodology surface (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`, the in-house audits)".
- **Proposed fix**: Tighten item 1 wording: "R-15 itself (as a risk-register entry), the `_resolve_slice_dir(NNN)` helper (in `tests/methodology/conftest.py`), AND the M-add-2 corpus class-closure backstop test are all already in the repo as of slice-056; no NEW methodology-surface rule is minted here". Don't conflate "methodology surface" with "test surface that pins methodology".
- **Builder draft**: ACCEPTED-FIXED at design.md §"R-15 retirement-discharge classification" item 1 — rewrote item 1 to draw the explicit test-surface-vs-methodology-surface distinction, cite the actual file paths (`architecture/risk-register.md:250-263`, `tests/methodology/conftest.py:20-108`, `tests/methodology/test_resolve_slice_dir.py:231-293`), and add a closing sentence noting that item 3 (META-1 vacuous-satisfaction) is the decisive argument carrying the discharge regardless of how "methodology surface" is parsed.

#### m4: design.md "Components touched" claims "no PMI-1 bump is required" — Critic notes this is correct; build-log should explicitly enumerate

- **Claim under review**: design.md §"Components touched" "no PMI-1 bump is required, no MCFS-1 / AVFS-1 forward-sync gate fires".
- **Issue**: Per Wiegers (every claim traces to evidence) — this is correct because no `plugin.yaml` / `VERSION` / `~/.claude/ai-sdlc-VERSION` edit is proposed. No fix needed; logging because PMI-1 / AVFS-1 / MCFS-1 / PVFS-1 / OSDG-1 audits will all run at Step 6 and should be clean. Recommend the build-log explicitly cites each as "no edit → no-op clean" so the verification trail is unambiguous.
- **Evidence**: design.md §"What's new" enumerates no installed-leg edits.
- **Proposed fix**: None required pre-build; build-log should enumerate the audits cleanly. No edit to design.md.
- **Builder draft**: ACCEPTED-PENDING — fold into /build-slice Phase F audit-execution build-log entries. No design.md or mission-brief edit. Phase F log will explicitly mark each of PMI-1 / AVFS-1 / MCFS-1 / PVFS-1 / OSDG-1 / INST-1 / CAD-1 as "no edit → no-op clean (per /critique m4 ACCEPTED-PENDING)" so the verification trail is unambiguous in the final reflection.

## Dimensions checked

- [x] Unfounded assumptions — verified on disk: `_resolve_slice_dir(34)` resolves to the archived directory, `mission-brief.md` exists at the resolved path, the `_R15_LITERAL_PATH_RE` regex matches the pre-edit form but not the post-edit form. Helper signature is single-arg `(slice_number: int)`. Two minors logged (m1 line-number citation, m2 line-span drift); no Blockers.
- [x] Missing edge cases — load N/A (single test file); empty N/A; network N/A (filesystem-only); concurrency N/A; permission denied N/A (read-only on archive); offline N/A; platform-specific verified at slice-056 (forward-slash diagnostic strings). The one edge case the design.md §"Error model" explicitly handles is "slice-034 archive directory missing/renamed" — verified present at design time. No findings.
- [x] Over-engineering — none. The slice is the minimum viable retirement-discharge (4 file edits + 1 new test function). The single new test function is a structural twin of slice-056's row-#56 pin and is required by the slice-054 BCR-1 traceability-axis pin discipline. No speculative-generality, no single-impl interfaces.
- [x] Under-engineering — M1 filed: the mid-slice smoke gate omitted the new shippability-row-#57 test, creating an AC5-verification-path gap. ACCEPTED-FIXED.
- [x] Contract gaps — N/A; no new endpoints, events, or APIs.
- [x] Security — N/A; no auth surface, no input validation surface, no secrets.
- [x] Drift from vault — none structurally. R-15 status flip is consistent with risk-register.md:254 current state. Slice-056 paragraph at risk-register.md:259-261 is preserved verbatim per design.md §"Components touched" (slice-040 R-10 retirement precedent at lines 180-195 also preserves history verbatim). No ADRs contradicted. Slice-034 archive directory present on disk. m1 logged (stale line-number citation risk in the new paragraph) — ACCEPTED-FIXED.
- [x] Web-known issues — N/A; no third-party APIs, no platform-version-sensitive dependencies, no recent-deprecation concerns. The slice is entirely internal to the in-repo methodology vault + test surface.
- [x] Cross-cutting conformance —
  - **Methodology-audit conformance (Dim 9 sub-clause 1)**: TF-1 opt-out per `Test-first: false`; no rows needed.
  - **Tooling-doc-vs-implementation parity (Dim 9 sub-clause 2)**: m2 logged (line-span drift) — ACCEPTED-FIXED.
  - **Algorithm-path-conformance with pre-existing branches**: regex matches pre-edit form and NOT post-edit form (verified empirically).
  - **Runtime/cwd boundaries**: helper uses module-globals `REPO_ROOT` binding (verified at slice-056); no new runtime surface.
  - **Language-version conformance**: no language-version-sensitive features added.
  - **Recursive self-application discipline (RSAD-1)**: the slice authors zero new methodology rules; the recursive self-application risk is the slice's OWN claims about line numbers / line spans (m1, m2 caught and FIXED).
  - **Entry-pin-vs-PMI-1-gate semantics (EPGD-1)**: no entry-pin or PMI-1-gate edits; N/A.
  - **Shippability-catalog consumer-reference propagation (SCPD-1)**: design.md §"What's new" item 4 + 5 proactively wire the row-#57 pin into the catalog row's own `Command` cell. M1 logged on the mid-slice smoke gate not executing the new pin — ACCEPTED-FIXED.
  - **Runtime-prerequisite completeness (RPCD-1)**: the new test function imports nothing new; slice-056 row-#56 precedent verified.
  - **Fix-block-completeness (FBCD-1)**: m2 logged (sub-mode (a) original-draft cross-file consistency drift on line span) — ACCEPTED-FIXED.
  - **Phantom test-file citation (PTFCD-1 / PTFFD-1)**: AC2 + AC3 test functions verified to exist; no phantom citations.
  - **Audit-parse-rule empirical-execution (APED-1)**: the slice modifies the `_R15_CORPUS_WHITELIST` data but does NOT modify `_R15_LITERAL_PATH_RE` (the parse rule). The regex was empirically executed at slice-056 against multi-line constructions. This slice's behavior change is purely the whitelist-shrinks-to-empty side; no APED-1 trigger.

## Triage

**Triaged by**: user
**Date**: 2026-05-21
**Final verdict**: NEEDS-FIXES

User accepted all 7 Builder-drafted dispositions as-is (per AskUserQuestion at /critique-review Step 5 hand-off). NEEDS-FIXES verdict computed mechanically: zero ESCALATED → not BLOCKED; one ACCEPTED-PENDING (m4 build-log enumeration) → NEEDS-FIXES not CLEAN. /build-slice proceeds; m4 work happens during /build-slice Phase F audit-execution log entries.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | mission-brief Mid-slice gate extended to 3 tests + Pre-finish gate gained explicit checkbox for `test_shippability_row_57_present_and_cites_r15` — belt-and-suspenders per the AC5-binding-test verification-traceability discipline |
| m1 | Minor | ACCEPTED-FIXED | design.md §"What's new" item 3 carries explicit Builder-discipline instruction to cite `test_ptffd1_no_false_positive.py:69-72` (pre-edit 4-line span) NOT `:70-71` (slice-056-era historical record) when authoring the new slice-057 retirement paragraph |
| m2 | Minor | ACCEPTED-FIXED | mission-brief AC3 line-span corrected `:214-218` → `:214-220` to align with design.md and the on-disk truth (7-line constant block L214-220) |
| m3 | Minor | ACCEPTED-FIXED | design.md §"R-15 retirement-discharge classification" item 1 rewritten with explicit test-surface-vs-methodology-surface distinction (citing exact file paths); META-1 vacuous-satisfaction identified as the decisive discharge argument regardless of terminology |
| m4 | Minor | ACCEPTED-PENDING | /build-slice Phase F audit-execution build-log MUST explicitly enumerate each of PMI-1 / AVFS-1 / MCFS-1 / PVFS-1 / OSDG-1 / INST-1 / CAD-1 as "no edit → no-op clean (per /critique m4 ACCEPTED-PENDING)" so the verification trail is unambiguous |
| m-add-1 | Minor | ACCEPTED-FIXED | mission-brief AC5 expanded to explicitly name `test_shippability_row_57_present_and_cites_r15` AND its assertion targets (`| 57 | slice-057-…` substring + `R-15` substring in catalog) AND the slice-056 L3768-3806 structural-twin template — kept AC count at 5 (no split); pre-finish-gate checkbox remains as redundant anchor (belt-and-suspenders parity with M1) |
| m-add-2 | Minor | ACCEPTED-FIXED | design.md §"What's new" item 2 gained explicit "Builder guard-rail (per /critique-review m-add-2 — slice-040 N+1 doctrine)" paragraph naming the regex match shape + self-skip scope + safe alternatives + prose-mention-is-safe-by-construction guarantee; prevents silent R-15 relapse via re-whitelisting if a careless comment-rewrite introduces a self-matching literal |
