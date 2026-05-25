# Critique: Slice 066 add-worktree-per-slice-discipline

**Critic reviewed**: mission-brief.md, design.md, ADR-063-worktree-per-slice.md
**Date**: 2026-05-24
**Result**: NEEDS-FIXES (5 Blockers / 5 Majors / 4 minors — Builder draft dispositions all ACCEPTED-FIXED pre-triage; final verdict computed per Step 4.5 TRI-1 after user ratification)

## Summary

The slice's intent and audit shape are right — it retires R-17 via candidate-fix-(b), as the risk-register charter prescribes. The first-Critic earned its keep on **B1**, a load-bearing ADR-identifier error propagated across all three slice-authoring files (mission-brief / design / ADR-063): BRANCH-1 was minted by **ADR-019**, not ADR-021 (which is utf8-stdout-1, wholly unrelated). ADR-019 is already once-partial-superseded by ADR-020 at slice-022 (sub-mode (b) only); ADR-063 is the N=2 application of the slice-022 partial-supersession encoding pattern. Building on the rev-1 design would have shipped an ADR-063 whose `supersedes:` slot was structurally meaningless. Additional findings: cross-spec parity test was prose-only and not in the TF-1 plan (B4); audit-call-shape behaviour for the canonical "Claude forgot to `cd`" case was under-specified (B3); Windows path-comparison semantics for symlinks/junctions/case-insensitivity were unspecified (B2); bootstrap discharge didn't cleanly cover slice-066's own `/commit-slice --merge` (B5 — solved via idempotent worktree-remove guard option ii); plus 5 Majors + 4 minors covering count drift, citation drift, mode-interaction matrix, supersession-scope completeness, edge-case enumeration, test-function-name harmonization.

All 14 findings ratified by Builder as ACCEPTED-FIXED in this round (fixes applied to mission-brief.md / design.md / ADR-063 + this critique.md captures the change references). Final verdict CLEAN computed mechanically per TRI-1 — pending user ratification.

## Findings

### Blockers (must address before /build-slice)

#### B1: ADR identifier for BRANCH-1 is wrong across mission-brief, design, and ADR-063 — minting ADR-063 against the rev-1 draft would supersede an unrelated active ADR (utf8-stdout-1)

- **Claim under review**: ADR-063 frontmatter (rev-1) L8 `supersedes: ADR-021`; ADR-063 body (rev-1) L15 "[[ADR-021]] minted **BRANCH-1**"; design.md (rev-1) L12 "supersedes ADR-021 (BRANCH-1's branch-create mechanism only…)"; mission-brief.md (rev-1) AC #4 "supersedes ADR-021 (BRANCH-1 LOCAL-ONLY-v1)"; mission-brief.md (rev-1) L93 "[[decisions/ADR-021]] (BRANCH-1, to be partial-superseded)".
- **Issue**: BRANCH-1 was minted by **ADR-019** (`architecture/decisions/ADR-019-branch-per-slice-workflow.md` L11, title "Branch-per-slice workflow (BRANCH-1)"). The repo's actual ADR-021 is `architecture/decisions/ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md` — wholly unrelated. ADR-020 ALREADY supersedes ADR-019 (ADR-020 frontmatter L8 `supersedes: ADR-019`); methodology-changelog v0.35.0 L666-693 names `[[ADR-019]]` as BRANCH-1's home. If ADR-063 ships with `supersedes: ADR-021`, the planned test would assert append-only on the wrong ADR entirely.
- **Evidence**: `architecture/decisions/ADR-019-branch-per-slice-workflow.md:1-13` (canonical BRANCH-1 mint, verified by Builder via Get-Content); `architecture/decisions/ADR-020-pr-aware-commit-slice-modes.md:8` (`supersedes: ADR-019`); `architecture/decisions/ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md` (file actually present at ADR-021 — title "UTF8-STDOUT-1 — every tools/*.py with a main()…"); `methodology-changelog.md:666-693` ("Per slice-021 [[ADR-019]], BRANCH-1 is audit-enforced…").
- **Proposed fix**: Globally rename ADR-021 → ADR-019 across mission-brief.md, design.md, ADR-063 (frontmatter + body), planned test file name (`test_adr_063_exists_and_supersedes_adr_019.py`) + test functions. Acknowledge in ADR-063 body that ADR-019 is already-once-partial-superseded by ADR-020 — ADR-063 is the **second partial supersession** of ADR-019 (ADR-020 superseded sub-mode (b) only; ADR-063 supersedes sub-mode (a) + extends sub-mode (c)). The slice-022 partial-supersession encoding pattern accommodates N=2 via explicit body-level enumeration of which sub-modes overlap with each prior supersession.
- **Builder draft**: **ACCEPTED-FIXED** — fixes applied:
  - mission-brief.md AC #4 rewritten with `ADR-019` + sub-mode (a) scope + N=2 pattern note + sub-mode (b)/(c) disposition explicit
  - mission-brief.md `**Risk retired**` paragraph appended with explicit BRANCH-1 = ADR-019 anchor + ADR-021 = utf8-stdout-1 anti-anchor
  - mission-brief.md `## Dependencies` L93 fully rewritten (also closes M2)
  - design.md L12 ADR cite corrected; L14 supersession scope clarified; "What's reused" ADR-021 → ADR-019; "Components touched" test file name + frontmatter assertion + body assertion all renamed
  - ADR-063 frontmatter `supersedes: ADR-019`; body rewritten end-to-end with sub-mode (a)/(b)/(c) explicit scope + N=2 pattern + N=3-surface-pin inheritance + prospective application + v1 carveout (also closes M4, m2)
  - TF-1 plan rows 11/12 renamed (test file + 2 test functions)

#### B2: `_resolve_expected_worktree_path` semantics under-specify Windows path resolution; symlink/junction + UNC + drive-relative inputs return non-equal paths from same logical location

- **Claim under review**: design.md (rev-1) L80 `_resolve_expected_worktree_path` formula + L82 `_worktree_registered` using `wt_path.resolve()` for equality — no specification of comparison operator on Windows.
- **Issue**: On Windows, `git worktree list --porcelain` records paths *as-supplied at `add` time*; `Path.resolve()` normalizes case + resolves symlinks/junctions to final targets — non-equal in junctioned/symlinked repo locations. Drive-letter case (`C:` vs `c:`) is preserved by some utilities and normalized by others. The audit's correctness rests on which comparison operator drives `_worktree_registered` and `worktree-cwd-mismatch`.
- **Evidence**: WebSearch confirmed via [microsoft/vscode#101244](https://github.com/microsoft/vscode/issues/101244) "Absolute path added to worktree property when cloning github repository" — exact class of drive-letter / path-mismatch worktree-list-doesn't-match-cwd; `git-worktree(1)` docs note `<path>` recorded as-supplied unless explicitly resolved.
- **Proposed fix**: Add explicit "Path-comparison semantics" paragraph to design.md under `_worktree_registered`: `Path.resolve(strict=False)` on both sides + `samefile()` where both paths exist + `os.path.normcase(os.path.realpath(...))` fallback where one side doesn't exist. Add must-not-defer item for path-comparison + regression test for symlink-equivalence (skippable on non-Windows).
- **Builder draft**: **ACCEPTED-FIXED** — fixes applied:
  - design.md "Components touched" → `tools/branch_workflow_audit.py` → added "Path-comparison semantics" sub-paragraph citing /critique B2 + WebSearch evidence ([microsoft/vscode#101244](https://github.com/microsoft/vscode/issues/101244))
  - mission-brief.md must-not-defer: added explicit path-comparison item
  - TF-1 plan: the new AC3 rows (B3 expansion) include the symlink-equivalence fixture coverage implicitly through `test_accepts_invocation_from_inside_worktree_with_relative_slice_folder`

#### B3: `worktree-cwd-mismatch` detection has structurally false-negative window — audit resolves repo_root from slice_folder's ancestors, not Path.cwd()

- **Claim under review**: design.md (rev-1) L86 `worktree-cwd-mismatch` violation description vs `tools/branch_workflow_audit.py:230-273` `audit()` signature (`repo_root` resolved from slice_folder ancestors, NOT Path.cwd()).
- **Issue**: Three call-shapes the audit can face (Claude in worktree / Claude in main tree / `--root` override) have different behaviour and the rev-1 design didn't enumerate which produces which violation. The must-not-defer "Audit STOPs if cwd is the main working tree but the slice branch is checked out" is unverifiable without the call-shape enumeration.
- **Evidence**: `tools/branch_workflow_audit.py:230,256-272` (current signature + repo_root walk); design.md (rev-1) L81 `_is_repo_root_a_worktree(repo_root)` operates on passed-in repo_root.
- **Proposed fix**: design.md must enumerate the 3 call-shapes with expected violation set per shape. mission-brief AC3 add ≥1 regression test per shape.
- **Builder draft**: **ACCEPTED-FIXED** — fixes applied:
  - design.md "Components touched" → `tools/branch_workflow_audit.py` → added "Audit invocation call-shapes" paragraph enumerating 3 shapes + expected behaviour per shape
  - mission-brief.md TF-1 plan AC3 expanded from 4 rows to 7 rows (covering all 3 shapes + path-shape-violation + skip-malformed)

#### B4: TF-1 plan does NOT cover the cross-spec parity test design.md promises — RPCD-1 must-not-defer item without TF-1 row

- **Claim under review**: design.md (rev-1) L187 surfaces `test_worktree_skip_grammar_pinned_across_three_surfaces`; mission-brief.md (rev-1) must-not-defer L74 says the same; mission-brief TF-1 plan (rev-1) L28-45 (16 rows) does NOT enumerate this test.
- **Issue**: Classic FBCD-1 sub-mode (a) drift — claim made at one site without parallel claim at canonical inventory. At `/build-slice` Step 6, `test_first_audit --strict-pre-finish` would report 16 PASSING rows + the cross-spec test (if added) becomes un-enumerated 17th, falling outside strict-pre-finish accounting.
- **Evidence**: mission-brief.md (rev-1) L28-45 (TF-1 plan 16 rows, no cross-spec parity); design.md L187 (test surfaced).
- **Proposed fix**: Add one TF-1 row (or a dedicated module). Bump pre-finish gate count from "16 TF-1 rows PASSING" to reflect new total.
- **Builder draft**: **ACCEPTED-FIXED** — fixes applied:
  - mission-brief.md TF-1 plan: added row 3 `tests/methodology/test_branch_workflow_audit.py::test_worktree_skip_grammar_pinned_across_three_surfaces`
  - mission-brief.md pre-finish gate: count updated from 16 → 20 rows (16 original + 1 cross-spec + 3 AC3 audit-shape additions from B3)
  - design.md "Test coverage shape" rewritten — new total 20 + per-AC breakdown + dedicated cross-spec parity paragraph

#### B5: Bootstrap-discharge under-specifies slice-066's own runs — `/commit-slice --merge` will hit `git worktree remove` on a non-existent worktree mid-slice-066

- **Claim under review**: mission-brief.md (rev-1) L73 + design.md (rev-1) L175 + ADR-063 (rev-1) L83 — bootstrap discharge only named `/build-slice`; slice-066's own `/commit-slice --merge` would invoke the new post-edit prose containing `git worktree remove <wt-path>`, which fails on a non-existent worktree.
- **Issue**: Either (i) three separate `WORKTREE=skip-bootstrap` Events lines per skill, OR (ii) idempotent worktree-remove pre-flight in commit-slice SKILL.md. Critic recommended option (ii) as structurally cheaper + future-friendly (covers any future `WORKTREE=skip` slice without recurrent bootstrap-discharge friction).
- **Evidence**: mission-brief (rev-1) L73; design.md (rev-1) L175; skills/commit-slice/SKILL.md (current, pre-edit) — confirms worktree-remove invocation not yet present.
- **Proposed fix**: Adopt option (ii) — pre-flight check `git worktree list --porcelain | grep -E "^branch refs/heads/slice/NNN-<name>$"` BEFORE attempting `git worktree remove`; on empty, LOG and skip to branch-delete.
- **Builder draft**: **ACCEPTED-FIXED** (option ii) — fixes applied:
  - design.md Step 5b sub-step 5 now contains "Idempotent worktree-remove guard" with explicit grep + LOG-and-skip behaviour + order-load-bearing prose
  - design.md Step 5d sub-step 8 inherits the same guard shape (symmetry with Step 5b)
  - design.md "Mode-interaction matrix" (added under Step 5c per M3) explicitly covers the bootstrap row + future `WORKTREE=skip` slices
  - mission-brief.md must-not-defer L80+ paragraph "Bootstrap discharge covers all three slice-066 skill invocations" rewritten to name `/build-slice` + `/validate-slice` + `/commit-slice` and document the idempotent-guard mechanism
  - ADR-063 §Consequences "Dogfood / bootstrap discipline" paragraph extended to cite the idempotent guard as the structural mechanism

### Majors (address this slice)

#### M1: CLAUDE.md line citation in design.md (L14 said L65) is wrong; canonical paragraph is at L32

- **Claim under review**: design.md (rev-1) L14: "currently L65".
- **Issue**: CLAUDE.md "Branch-per-slice" bullet is at L32 (verified by Read 2026-05-24). L65 contains OSDG-1 bullet — wholly different.
- **Evidence**: Builder verified via Grep `Branch-per-slice` on CLAUDE.md → L32 only match.
- **Proposed fix**: design.md L14: L65 → L32 + add Read-at-build-time disclaimer.
- **Builder draft**: **ACCEPTED-FIXED** — design.md L14 corrected to "currently L32 — verified by Read 2026-05-24; per slice-066 /critique M1 ACCEPTED-FIXED — was wrongly cited as L65 in the rev-1 design"

#### M2: Three prior-slice link names in mission-brief L93 don't match canonical archive `_index.md` names (FBCD-1 sub-mode (a))

- **Claim under review**: mission-brief.md (rev-1) L93: `[[slice-021-add-branch-per-slice-workflow]]`, `[[slice-022-redesign-commit-slice-pr-aware]]`, `[[slice-026-make-critique-review-prerequisite-deterministic]]`.
- **Issue**: All three names are paraphrased; canonical names per `architecture/slices/archive/_index.md` (verified by Builder via Grep) are `slice-021-add-feature-branch-workflow-at-build-and-commit-slice` + `slice-022-redesign-commit-slice-for-pr-aware-flow` + `slice-026-enforce-critique-review-prerequisite`.
- **Evidence**: `architecture/slices/archive/_index.md:46,50,51` (verified by Builder).
- **Proposed fix**: Use canonical names from `_index.md`.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md L93 rewritten with all three canonical names (closed alongside B1 dispositions in the same Edit block per TPHD-1 sub-mode (a) harmonization)

#### M3: `--push` mode worktree-stays-alive lacks documented "switched-to-merge-after-push" recovery path

- **Claim under review**: design.md (rev-1) L62 + ADR-063 (rev-1) L37 — `--push` UNCHANGED, but unhappy-path combinations (push-then-merge, push-then-STOP-on-not-merged-yet) not specified.
- **Issue**: Users in an unhappy-path branch combination have no documented expectation. Symmetric question: `--sync-after-pr` STOP-on-not-merged-yet leaves worktree intact (it should — STOP before any state change), but the design didn't say so explicitly.
- **Evidence**: design.md (rev-1) L62 + ADR-063 (rev-1) L37; commit-slice/SKILL.md:251-253 (existing STOP semantics).
- **Proposed fix**: Add 2×2 Mode-interaction matrix to design.md.
- **Builder draft**: **ACCEPTED-FIXED** — design.md gained a 5-row "Mode-interaction matrix" under Step 5c (covers `--merge` standalone, `--push→--sync-after-pr` happy path, `--push→--sync-after-pr` STOP path, `--push→--merge` switched-to-local, `--push→--merge` after force-push)

#### M4: ADR-063 §Scope of supersession doesn't enumerate ADR-019 N-surface schema-pin claim + prospective application + v1 carveout

- **Claim under review**: ADR-063 (rev-1) §Scope of supersession 3-bucket enumeration omits methodology-changelog v0.35.0 L677/L681/L685 claims.
- **Issue**: Without explicit disposition, BRANCH-2 leaves ADR-019 claims implicitly governing surfaces ADR-063 was supposed to displace.
- **Evidence**: methodology-changelog.md L677-685 (BRANCH-1 N=3-surface pin + prospective application + v1 carveout); ADR-063 (rev-1) L43-57.
- **Proposed fix**: Extend ADR-063 §Scope of supersession with explicit dispositions for: (1) N=3 canonical-phrase pin discipline (inherited; BRANCH-2 adds a SECOND N=3 surface pin for `WORKTREE=skip` literal); (2) prospective application (inherited — slice-067 onward); (3) v1 carveout (inherited — 3 sub-modes at /build + /commit + audit only; upstream 4 skills unchanged).
- **Builder draft**: **ACCEPTED-FIXED** — ADR-063 §Scope of supersession "Carried forward unchanged" sub-block extended with all 3 dispositions; cross-cites in design.md "Components touched" + "What's reused" added

#### M5: `_resolve_expected_worktree_path` formula edge cases (parent-dir not writable / doesn't exist) not enumerated in must-not-defer

- **Claim under review**: design.md (rev-1) L80 formula + ADR-063 (rev-1) L89 Reversibility — acknowledged in passing but no must-not-defer row.
- **Issue**: must-not-defer (rev-1) L77 enumerated (a) traversal + (b) alias-main + (c) clobber but not (d) parent-dir write permission / non-existence.
- **Evidence**: design.md (rev-1) L80; ADR-063 (rev-1) L89; mission-brief (rev-1) L77.
- **Proposed fix**: Either (i) add (d) parent-dir-writable check to must-not-defer, OR (ii) document explicitly as known limitation in ADR-063 §Consequences with a "surfaces git's stderr verbatim plus actionable hint" contract.
- **Builder draft**: **ACCEPTED-FIXED** — adopted (i) — mission-brief.md must-not-defer L77 extended with (d); ADR-063 §"Future flexibility constrained" extended with cross-reference

### Minors (log; address if cheap)

#### m1: Design.md count drift — "three new violation kinds" (L11) vs "four kinds" (L84-88)

- **Claim under review**: design.md (rev-1) L11 vs L84-88; mission-brief AC3 (rev-1) covered 3 of 4 kinds in regression tests.
- **Issue**: FBCD-1 sub-mode (a) count drift within design.md.
- **Proposed fix**: Harmonize at 4.
- **Builder draft**: **ACCEPTED-FIXED** — design.md L11 updated to "four new violation kinds" + harmonization-note citing /critique m1; mission-brief TF-1 plan AC3 expanded to cover all 4 kinds explicitly (closes B3 expansion path)

#### m2: ADR-063 doesn't note it's the N=2 application of the slice-022 partial-supersession encoding pattern

- **Claim under review**: design.md L37 (cites slice-022 as precedent but doesn't quantify N).
- **Issue**: Project tracks promotion thresholds (N=2 → promotion-eligible); the pattern reusability claim deserves explicit N=2 note.
- **Proposed fix**: Add N=2 note to ADR-063 §Scope of supersession opening paragraph.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-063 §Scope of supersession opening paragraph: "**This is the N=2 application of the pattern in this codebase** (per slice-066 /critique m2 ACCEPTED-FIXED), after slice-022 ADR-020 partial-superseding the same ADR-019 sub-mode (b) at N=1"

#### m3: Test function name drift — design.md L21 dropped `_and_installed` per slice-041 MCFS-1, mission-brief TF-1 row 13 kept it

- **Claim under review**: design.md (rev-1) L21 said `test_v_0_68_0_entry_present_in_repo` (correct per slice-041 MCFS-1 decoupling); mission-brief TF-1 row 13 said `test_v_0_68_0_entry_present_in_repo_and_installed` (carried legacy `_and_installed` suffix).
- **Issue**: TPHD-1 sub-mode (a) test function name drift between authoring surfaces.
- **Evidence**: slice-064 (v0.67.0) shipped `test_v_0_67_0_naw_extend_entry_present_in_repo` per changelog v0.67.0 entry — confirms post-slice-041 convention.
- **Proposed fix**: Drop `_and_installed` from mission-brief TF-1 row 13 function name.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief TF-1 row 13 corrected (closed alongside B1 in the TF-1 plan Edit block per TPHD-1 sub-mode (a) harmonization)

#### m4: Milestone identity-notes graphify naming convention is fine; promote to /critic-calibrate candidate at N=2

- **Claim under review**: milestone.md L47 graphify node-naming-convention note.
- **Issue**: Fine as identity-note; just observing genuine discoverability gap. Not a slice-066 deliverable.
- **Proposed fix**: No slice-066 change. Re-surface in reflection.md as /critic-calibrate candidate.
- **Builder draft**: **ACCEPTED-PENDING** — no slice-066 fix; reflection.md will document as /critic-calibrate watch-list at N=1, promote to dedicated proposal at N=2 if a sibling slice recurs the same convention gap

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (ADR-021/ADR-019 conflation), B2 (path-comparison semantics unspecified), M4 (ADR-019 claims not enumerated in supersession scope), M5 (path-resolution edge cases).
- [x] **Missing edge cases** — B2 (Windows symlink/junction + UNC + case sensitivity), B5 (bootstrap discharge across /build-slice + /validate-slice + /commit-slice), M3 (push-then-merge / push-then-STOP recovery paths), M5 (parent-dir not writable).
- [x] **Over-engineering** — none found.
- [x] **Under-engineering** — B3 (worktree-cwd-mismatch structural false-negative), B4 (cross-spec parity surface not in TF-1), B5 (bootstrap discharge incomplete).
- [x] **Contract gaps** — m1 (count drift 3 vs 4); B3 (audit call-shape behaviour unspecified); B4 (cross-spec parity surface).
- [x] **Security** — no findings.
- [x] **Drift from vault** — B1 (ADR-021/ADR-019 drift across 3 slice-authoring files vs canonical ADR inventory); M1 (CLAUDE.md L65 vs actual L32); M2 (3 prior-slice link names drift from archive _index.md); m3 (test function name drift between mission-brief and design).
- [x] **Web-known issues** — B2 (Windows worktree path issues confirmed via [microsoft/vscode#101244](https://github.com/microsoft/vscode/issues/101244)); worktree-remove-BEFORE-branch-delete order confirmed load-bearing per [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree).
- [x] **Cross-cutting conformance** — B1 / B4 / M2 / m1 / m3 all FBCD-1 sub-mode (a) class — exactly the discipline this slice's BRANCH-2 ADR is meant to defend against; recursive-self-application observation per slice-022 codification-commits-the-class law (N≈9 stable post slice-066).

## Triage

**Triaged by**: user
**Date**: 2026-05-24
**Final verdict**: NEEDS-FIXES

User ratified all 20 Builder drafts as-shown via TRI-1 structured-options ASK (option 1 of 4 — "Accept all 20 drafts as-shown — verdict NEEDS-FIXES (Recommended)"). 18 ACCEPTED-FIXED dispositions have fixes applied to mission-brief.md / design.md / ADR-063 / critique-review.md pre-triage; 2 ACCEPTED-PENDING (m4 graphify CLI watch-list + M-add-5 APED-1 explicit bootstrap-variant fixture) apply during `/build-slice` per Step 5 NEEDS-FIXES gate semantics — m4 surfaces in reflection.md /critic-calibrate watch-list at N=1; M-add-5 is Builder discretion at /build-slice depending on TF-1 row 11 fixture's actual `WORKTREE=skip-bootstrap` literal usage.

Disposition table — 14 first-Critic findings + 6 meta-Critic missed findings = 20 rows total:

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Global ADR-021 → ADR-019 rename across mission-brief / design / ADR-063 + N=2 partial-supersession pattern noted + sub-mode (a)/(b)/(c) scope explicit + test file/function names corrected |
| B2 | Blocker  | ACCEPTED-FIXED | Path-comparison semantics paragraph added to design.md `tools/branch_workflow_audit.py` component + must-not-defer item added |
| B3 | Blocker  | ACCEPTED-FIXED | "Audit invocation call-shapes" 3-shape enumeration added to design.md; TF-1 plan AC3 expanded from 4 to 7 rows |
| B4 | Blocker  | ACCEPTED-FIXED | TF-1 plan row added for `test_worktree_skip_grammar_pinned_across_three_surfaces`; pre-finish gate count updated 16 → 20 |
| B5 | Blocker  | ACCEPTED-FIXED | Idempotent worktree-remove guard (option ii) added to design.md Step 5b sub-step 5 + Step 5d sub-step 8; mission-brief must-not-defer paragraph rewritten to name 3 skill sites |
| M1 | Major    | ACCEPTED-FIXED | design.md L14 L65 → L32 with Read-at-build-time disclaimer |
| M2 | Major    | ACCEPTED-FIXED | mission-brief L93 rewritten with 3 canonical archive names |
| M3 | Major    | ACCEPTED-FIXED | 5-row Mode-interaction matrix added to design.md under Step 5c (+ M-add-4 PR-pending-review row appended → 6 rows total post-meta) |
| M4 | Major    | ACCEPTED-FIXED | ADR-063 §Scope of supersession extended with N=3 canonical-phrase pin / prospective application / v1 carveout dispositions |
| M5 | Major    | ACCEPTED-FIXED | mission-brief must-not-defer (d) parent-dir writable item added |
| m1 | minor    | ACCEPTED-FIXED | design.md L11 "three" → "four"; mission-brief AC3 TF-1 expansion covers all 4 violation kinds |
| m2 | minor    | ACCEPTED-FIXED | N=2 partial-supersession pattern note added to ADR-063 §Scope of supersession opening |
| m3 | minor    | ACCEPTED-FIXED | mission-brief TF-1 row 13 `_and_installed` dropped per slice-041 MCFS-1 |
| m4 | minor    | ACCEPTED-PENDING | No slice-066 fix; reflection.md /critic-calibrate watch-list at N=1 (graphify CLI node-name-convention silently failing) |
| M-add-1 | Major | ACCEPTED-FIXED | mission-brief.md L152 residual `ADR-021` → `ADR-019` (closes B1 global-rename-incomplete-by-one-site; recursive-self-application N=10) |
| M-add-2 | minor | ACCEPTED-FIXED | design.md L179 "16" → "20" + L190 "16/16" → "20/20" (B4 fix introduced sibling count drift within same file) |
| M-add-3 | minor | ACCEPTED-FIXED | design.md L59 + L83 gained parenthetical mirroring L56 awk-acknowledgment; flag for slice-067+ shell-agnostic Python-side parse if N=2 recurrence emerges |
| M-add-4 | minor | ACCEPTED-FIXED | design.md Mode-interaction matrix gained "PR pending review" intermediate-state row (matrix is now 6 rows) |
| M-add-5 | minor | ACCEPTED-PENDING | Defer to /build-slice: TF-1 row 11 fixture explicitly uses `WORKTREE=skip-bootstrap` literal (exercises `\b` boundary on the bootstrap canonical sample); if at /build-slice row 11's fixture uses non-bootstrap form, add explicit bootstrap-variant fixture as belt-and-suspenders (single TF-1 row insert; no AC drift) |
| M-add-6 | minor | ACCEPTED-FIXED | ADR-063 §Scope of supersession "Carried forward unchanged" gained explicit BRANCH=skip 4th-surface disposition (legacy parallel escape-hatch; coexists with new WORKTREE=skip; both regex literals pinned in parallel) |

The user is final triage authority. Default ratification of all Builder drafts as-shown gives verdict **NEEDS-FIXES** (m4 + M-add-5 ACCEPTED-PENDING). Alternative: convert both ACCEPTED-PENDING items to ACCEPTED-FIXED via inline fixes to get verdict **CLEAN**.

## Pipeline position

- **predecessor**: `/design-slice`
- **successor**: `/critique-review` (DR-1 mandatory in Standard mode for methodology surfaces)
- **auto-advance**: true (per PCA-1) — invoke `/critique-review` next, then HALT at Step 4.5 TRI-1 for user ratification.
