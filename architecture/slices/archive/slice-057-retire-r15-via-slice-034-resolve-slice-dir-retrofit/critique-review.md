# Critique Review: Slice 057 retire-r15-via-slice-034-resolve-slice-dir-retrofit

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-21
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

_First-Critic counts: 0 Blockers / 1 Major / 4 Minors. Meta-Critic: +2 missed (m-add-1, m-add-2) + 0 suspicious + 0 severity adjustments._

## Summary

The first Critic's M1/m1/m2/m3/m4 findings are all VALID with correct severities, and the Builder's four ACCEPTED-FIXED edits + one TPHD-1(b) self-caught harmonization land cleanly against the post-edit on-disk state. Independent re-review surfaces one missed minor concern (m-add-1) and one missed forward-looking concern (m-add-2) that are particularly relevant given slice-040's lesson that "discipline rule minted in slice N is a first-Critic blind spot on slice N+1" — slice-057 is the first slice governed by slice-056's freshly minted corpus class-closure backstop, and the meta-Critic is the structural backstop per that doctrine.

Zero-false-alarm streak now N=10 cumulative on codification-class slices; the slice-040 N+1 lineage doctrine paid off N+1 (cumulative tally now N=11 across slice-026/029/038/039/046/049/050/051/054/055/056/057 where DR-1 caught what the first Critic missed on codification slices).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **M1** (mid-slice smoke gate omits row #57 pin test) — VALID; severity Major is appropriate. design.md §"What's new" item 5 + AC5 add `test_shippability_row_57_present_and_cites_r15` but the PRE-FIX mid-slice gate ran only 2 tests; without M1's fix the row-#57 pin test could fail at pre-finish with no mid-slice catch. Verified the parallel slice-056 row-#56 test exists at `test_methodology_changelog.py:3768-3806` confirming the template. Builder draft applied BOTH (a) extend mid-slice to 3 tests AND (b) explicit pre-finish checkbox — belt-and-suspenders is appropriate for the AC5-binding test (per Wiegers verification-traceability discipline).
- **m1** (`:69-72` vs `:70-71` line-number citation drift) — VALID; severity Minor is appropriate. Verified on disk `tests/methodology/test_ptffd1_no_false_positive.py:69-72` is the 4-line pre-edit literal span (binding starts line 69, closing `)` line 72). Builder's design.md §"What's new" item 3 explicitly cites `:69-72` post-fix. Fixed correctly.
- **m2** (`:214-218` vs `:214-220` line span for `_R15_CORPUS_WHITELIST`) — VALID; severity Minor is appropriate. Verified `test_resolve_slice_dir.py:214-220` is the 7-line constant block (declaration L214, comment L215-218, entry L219, closing `}` L220). Builder's mission-brief AC3 corrected to `:214-220`. Fixed correctly.
- **m3** (methodology-surface vs test-pinning-surface conflation) — VALID; severity Minor is appropriate. Per MEPD-1 / ADR-041 the enumerated methodology surfaces are `skills/*/SKILL.md` + `agents/*.md` + `tools/**/*.py` + `methodology-changelog.md` + in-house audits; `tests/methodology/*.py` is a test surface that PINS methodology, NOT a methodology surface. The original design conflated these, and the Builder's POST-fix design.md §"R-15 retirement-discharge classification" item 1 makes the distinction crisp and explicitly identifies item 3 (META-1 vacuous satisfaction) as decisive. Fixed correctly.
- **m4** (build-log should enumerate PMI-1 / OSDG-1 non-applicability) — VALID; severity Minor is appropriate. ACCEPTED-PENDING to /build-slice Phase F. Acceptable.

## Suspicious findings

No suspicious findings. Every first-Critic finding holds up against the on-disk state.

## Missed findings

Two concerns the first Critic didn't flag that surface from independent re-review:

### m-add-1: AC5 maps to two artifacts (row insert + new pinning test) but mission-brief names only the row by inference — every AC should bind to a named verification artifact

- **Severity**: Minor (Dim 1 — Unfounded assumptions / Dim 5 — Contract gaps)
- **Claim under review**: design.md §"Plus one new test" lists test #5 but mission-brief lists only 5 acceptance criteria for 4 file edits — AC5 maps to BOTH the shippability.md row insert AND the new test function. The TPHD-1(a) mapping discipline (mission-brief TF-1-plan row ↔ test-function 1-to-1) is implicit, not explicit.
- **Issue**: design.md §"What's new" enumerates `5. tests/methodology/test_methodology_changelog.py (new function at end)` as a separate edit, but mission-brief AC5 (pre-m-add-1-fix) said only "row #57 capturing the corpus-class-closure backstop's whitelist-empty invariant... SCMD-1, PTFCD-1, and the shippability runner all stay clean." The mission-brief AC5 didn't name `test_shippability_row_57_present_and_cites_r15` explicitly. Per Wiegers (Software Requirements 3e, §10 verification traceability) every acceptance criterion should bind to a named verification artifact; the binding here was by inference.
- **Evidence**: mission-brief AC5 (pre-fix) vs design.md §"What's new" items 4+5 (the row and the test are separate edits but only the row was named in AC5).
- **Proposed fix**: Either (a) split AC5 into AC5a (row insert) + AC5b (new pinning test), OR (b) the existing pre-finish-gate checkbox "`test_shippability_row_57_present_and_cites_r15` PASSes (per /critique M1 ACCEPTED-FIXED — explicit anchor for AC5)" should be promoted into the AC5 prose itself.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md AC5 — chose option (b)-style: expanded AC5 prose to explicitly name `test_shippability_row_57_present_and_cites_r15` AND its assertion targets (the `| 57 | slice-057-…` substring + `R-15` substring in catalog) AND the slice-056 L3768-3806 structural-twin template. Kept AC count at 5 (no split) — the bifurcation pattern (slice-054 AC4 input-axis-at-/validate + output-axis-at-/reflect) doesn't fit here cleanly because both halves of AC5 verify at /validate-slice, not across skill boundaries. The pre-finish-gate checkbox stays as a redundant anchor (belt-and-suspenders, matching the M1 belt-and-suspenders posture).

### m-add-2: Comment-rewrite at design §"What's new" item 2 could theoretically introduce a new self-matching literal-path RHS that would relapse R-15 — slice-040 N+1 doctrine guard-rail missing

- **Severity**: Minor (Dim 2 — Missing edge cases / Dim 9 — Cross-cutting conformance)
- **Claim under review**: design.md §"What's new" item 2 says "Rewrite the surrounding comment block from 'deferral surface' framing to 'retirement-discharge witness' framing" without explicit guidance about avoiding literal-path-RHS constructions inside the rewritten comment.
- **Issue**: When `_R15_CORPUS_WHITELIST` shrinks to `set()`, the slice-034 literal references inside `test_resolve_slice_dir.py` itself (the docstring at line 266 and any pre-edit whitelist tuple) are still on disk as comment text — but `_R15_LITERAL_PATH_RE` requires `REPO_ROOT / "architecture" / "slices" / ...` literal Python code, not prose, so prose references don't match. However, the post-edit comment block (per design §"What's new" item 2) MUST be carefully written so any inline example REPO_ROOT-literal that the rewrite might include is either avoided or guarded. The first Critic didn't dimension-check that the comment-rewrite step (a free-form prose edit) can't accidentally introduce a self-matching pattern. This is the canonical slice-040 N+1 blind-spot: slice-056 just minted the M-add-2 corpus class-closure backstop AND its self-skip clause; slice-057 is the first governed slice.
- **Evidence**: design.md §"What's new" item 2 (pre-m-add-2-fix had no guard-rail prose); `test_resolve_slice_dir.py:222-228` shows the regex requires literal Python code (REPO_ROOT identifier + quoted-string-segment sequence); `test_resolve_slice_dir.py:259-260` shows the self-skip clause shields ONLY `test_resolve_slice_dir.py` itself, not other test modules that might copy-paste a problematic comment.
- **Proposed fix**: Builder should add a one-line precaution to design.md §"What's new" item 2: "The comment-rewrite MUST NOT include any `REPO_ROOT / 'architecture' / 'slices' / ...` Python-literal-form example (only English prose references to the literal); if an example is needed, use markdown code-fence or non-matching syntax to avoid creating a new corpus-backstop match that would force re-whitelisting." Verified at `test_resolve_slice_dir.py:222-228` the regex is whitespace-tolerant but still requires the literal `REPO_ROOT` identifier + quoted-string-segment sequence, so prose-text mentions are safe by construction — but the design.md should call this out so the Builder doesn't introduce a regression at the comment-rewrite step. Severity Minor (a regression here would FAIL the mid-slice smoke gate immediately so latency is zero, but explicit guard-rail is the slice-040 lesson).
- **Builder draft**: ACCEPTED-FIXED at design.md §"What's new" item 2 — added explicit "Builder guard-rail (per /critique-review m-add-2 ACCEPTED-FIXED — slice-040 N+1 doctrine)" paragraph naming: (a) the regex shape that triggers a match (`REPO_ROOT` identifier + `"architecture"/"slices"/(?:"archive"/)?"slice-\d{3}-` quoted-string sequence); (b) the self-skip clause's exact scope (this file only — line 259-260); (c) safe alternatives if an in-comment example is needed (markdown code-fence in docstring OR backtick-fenced inline placeholder with internal slashes replaced); (d) the prose-mention-is-safe-by-construction guarantee. The guard-rail is upstream of the comment-rewrite step; the failure mode (silent R-15 relapse via re-whitelisting) is the durable consequence the design.md guard prevents.

## Severity adjustments

No severity adjustments. M1 as Major, m1/m2/m3/m4 as Minor — all calibrated correctly. M1's verification-path gap is impact-bounded (would surface at pre-finish, not silently regress production behavior — but blocks slice finish, hence Major not Minor). The minors are all citation/terminology hygiene, not execution-path. m-add-1 and m-add-2 are Minor (document-shape clarity and forward-looking guard-rail respectively; no execution-path latency on either since the existing gates catch any concrete regression at mid-slice smoke).

## Notes

Confidence is high on the M1/m1/m2/m3/m4 dispositions (all verified against on-disk state including `test_ptffd1_no_false_positive.py:69-72`, `test_resolve_slice_dir.py:214-220`, `risk-register.md:250-263`, and the slice-056 row-#56 template at `test_methodology_changelog.py:3768-3806`). The Builder's POST-fix harmonization (design.md "Validation strategy" stale "two affected tests" → "three") is correctly applied — verified at design.md §"Validation strategy (POST-self-caught-harmonization)" — and is the kind of TPHD-1 sub-mode (b) move that prevents downstream drift.

The first Critic's coverage of Dimensions 1, 5, 6, 7, 9 was thorough. The two missed findings cluster in Dimensions 1, 2, and 9, both around the slice-040 "rule minted in N is blind-spot in N+1" doctrine — slice-056 just minted both the corpus class-closure backstop test AND the self-skip clause, and slice-057 is the first slice asked to live within that machinery (whitelist=∅ becomes the structural witness). Calibration observation: the meta-Critic catching exactly the N+1 lineage class is consistent with the slice-040 doctrine ("DR-1 meta-Critic is the structural backstop for newly-minted discipline").

Both missed findings are Minor — Builder absorbed at /critique-review Step 3 with prose-only edits to design.md and mission-brief AC5. No blocking concerns; no severity adjustments needed.

**Files referenced**:
- `tests/methodology/test_ptffd1_no_false_positive.py` (lines 69-72 pre-edit, lines 16 + 69-72 post-edit)
- `tests/methodology/test_resolve_slice_dir.py` (lines 214-220 constant, 222-228 regex, 231-293 backstop, 259-260 self-skip, 266 docstring)
- `tests/methodology/test_methodology_changelog.py` (lines 125-145 META-1 assertion, 3768-3806 row-#56 template)
- `tests/methodology/conftest.py` (lines 20-108 `_resolve_slice_dir`, lines 38-46 R-15 docstring)
- `architecture/risk-register.md` (lines 250-263 R-15 entry)
- `architecture/shippability.md` (rows 27-56, row #57 add target)
- `methodology-changelog.md` (most-recent v0.62.0 / v0.61.0 entries for vacuous-satisfaction context)
