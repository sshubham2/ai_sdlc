# Critique: Slice 054 fix-pyproject-toml-version-drift

**Critic reviewed**: mission-brief.md, design.md, ADR-056
**Date**: 2026-05-21
**Result**: NEEDS-FIXES (0 blockers, 4 majors, 2 minors)

## Summary

Sound Route-B Inclusion-heuristic ride with verified precedent. Two Major gaps: (1) AC3 pin test has no concrete identity/anchor scheme in design.md (still "TBD" in the test-first plan after design lock), and (2) the design's "stale prose scrub" plan does not enumerate *all* `0.20.0` literals in pyproject.toml (line 3 `methodology-changelog.md v0.20.0` cite is unmentioned). M3 catches an FBCD-1 sub-mode (a) cross-file inconsistency between mission-brief.md smoke-gate expected literal (`0.61.0`) vs design.md Route-B target (`0.62.0`). M4 catches an AC4 verification-grep position-semantic gap — the first BCR-1 dogfood needs position-anchored verification, not content-only. One Minor on the SC-001 backlog block heading stale `VERSION = 0.59.0` text (correctly out-of-scope per BCR-1 append-only).

## Findings

### Blockers (must address before /build-slice)

(none — design is buildable; the Major findings below are addressable in this slice without redesign.)

### Majors (address this slice)

#### M1: AC3 pin test left "TBD at /design-slice" in the design

- **Claim under review**: mission-brief.md test-first-plan row 3: *"| 3 | TBD at /design-slice | TBD | test_pyproject_toml_no_stale_v0_20_0_literal (or similar) | PENDING |"*. design.md "What's new" enumerates the two methodology-changelog entry-pin tests in detail but says nothing about the AC3 pin test — neither test path, nor function name, nor assertion shape.
- **Issue**: Per **Wiegers** + **TF-1**: every AC needs a concrete test path + function name by /build-slice time, OR an explicit out-of-scope/deferred entry. /design-slice is where "TBD at /design-slice" gets resolved — it hasn't. If no pin test exists, AC3 collapses to a one-shot scrub with no regression guard — a future edit re-introducing `v0.20.0` in a comment or `13 audit modules` (the literal is genuinely stale today — 29 `.py` files in `tools/` per `ls` count, not 13) would go ungated. This slice's parent class is *"silently drifted forever because nothing pinned it"*; replicating that anti-pattern on AC3 is the failure mode the slice exists to retire.
- **Evidence**:
  - mission-brief.md test-first-plan row 3 still says `TBD` for both Test path and Test type after /design-slice ran.
  - design.md "What's new" enumerates the two new pin tests (v0.62.0 entry + shippability propagation) but no AC3 pin.
  - `tools/install_audit.py:25` already carries `"all 13 tool modules import"` — the same stale literal class lives across files (SC-024 is separately tracked).
- **Proposed fix**: Mint AC3 pin test in design.md "What's new" — extend the existing `tests/methodology/test_pyproject_version_matches_version_file.py` with a new function `test_pyproject_has_no_stale_v_0_20_0_or_count_literals` asserting `"0.20.0" not in pyproject_text` AND `"13 audit modules" not in pyproject_text` AND `"13 tool modules" not in pyproject_text`. The `[project].version` field reads `"0.20.0"` pre-fix and `"0.62.0"` post-fix, so the bare `"0.20.0"` substring test is safe — pre-fix FAILs on line 20 + lines 3+6+66; post-fix PASSes when ALL four sites are cleaned. Guarantees the WRITTEN-FAILING → PASS transition non-tautologically. Update mission-brief.md test-first row 3 with concrete Test path + function name + PENDING status.
- **Builder draft**: **ACCEPTED-FIXED** — design.md "What's new" mints the AC3 pin test `test_pyproject_has_no_stale_v_0_20_0_or_count_literals` co-located in the existing `test_pyproject_version_matches_version_file.py` module; mission-brief.md TF-1 row 3 updated with concrete path + function name + PENDING status (test authored at /build-slice WRITTEN-FAILING phase). Per TPHD-1 sub-mode (a), the harmonized mission-brief.md + design.md edit ships in this fix block. Fix applied at `design.md`§"What's new" + `mission-brief.md`§"Test-first plan" row 3.

#### M2: AC3 stale-literal enumeration is incomplete — design names two of three stale literal classes in pyproject.toml

- **Claim under review**: design.md "What's new" — *"pyproject.toml stale prose scrub (AC3): line 6 comment `(the 13 audit modules under tools/)` and line 66 comment `# The tools package itself has no non-Python data files in v0.20.0.` cleaned"*. mission-brief.md AC3 — *"no stale `v0.20.0` literal and no `13 audit modules` / `13 tool modules` literal"*.
- **Issue**: Per **CCC-1 / Tooling-doc-vs-implementation parity** (Dim 9): the design.md mechanical inventory of stale literals must be cell-verifiable against the actual file. Three `0.20.0`-class literals exist in pyproject.toml: **line 3** (`Per INST-1 (methodology-changelog.md v0.20.0).`), **line 6** (the `13 audit modules` count), **line 66** (the `v0.20.0` data-files comment). The design names lines 6+66; **line 3 is unmentioned**. Either the scrub misses line 3 (AC3 verification FAILs at build time) OR the scrub hits line 3 incidentally without a design plan for the replacement (uncontrolled edit).
- **Evidence**:
  - `grep -nE "v0\.20\.0|0\.20\.0" pyproject.toml` returns lines 3, 20, 66 — three sites, not two. Line 6 also has `13 audit modules` (separate stale literal class).
  - Line 3: `# Per INST-1 (methodology-changelog.md v0.20.0). The pipeline ships skills,` — methodology version reference, drifted across 41 minor versions.
  - design.md "What's new" enumerates only lines 6 + 66.
- **Proposed fix**: Update design.md "What's new" to enumerate all three stale-version literal sites: **line 3** (methodology version cite → refactor to non-version-bearing form per slice-045 INSTALL.md precedent, so it doesn't become a per-VERSION-bump scrub obligation), line 6 (`13 audit modules` → count-free wording), line 66 (`v0.20.0` data-files comment → version-free wording). M1's AC3 pin test will catch line 3 even if the design author forgets it (since `"0.20.0" not in pyproject_text` is universal).
- **Builder draft**: **ACCEPTED-FIXED** — design.md "What's new" enumerates all 3 stale-literal sites in pyproject.toml (line 3 + line 6 + line 66) with per-site refactor target wording (non-version-bearing per slice-045 precedent). M1's pin test (`"0.20.0" not in pyproject_text`) is the structural backstop catching any forgotten site. Fix applied at `design.md`§"What's new".

#### M3: Mid-slice smoke gate expected-PASS literal in mission-brief contradicts design.md's Route-B atomic bump

- **Claim under review**: mission-brief.md "Mid-slice smoke gate" — *"Expected: PASS (`assert '0.61.0' == '0.61.0'`)."* vs design.md "Mid-slice smoke gate (operational expansion)" — *"the bump literal must be '0.62.0' (NOT '0.61.0')"*.
- **Issue**: Per **Wiegers** (traceability) + **slice-053 multi-site-literal-contrast** + **FBCD-1** sub-mode (a) Dim 9: a load-bearing literal at >1 site must be byte-identical or the Builder follows whichever site is read at edit time. A Builder reading mission-brief alone, bumping pyproject to `0.61.0` (the pre-Route-B VERSION value), running the smoke gate, seeing PASS, and proceeding — would have skipped Route B's VERSION→0.62.0 leg entirely.
- **Evidence**:
  - mission-brief.md "Mid-slice smoke gate" block: `Expected: PASS (\`assert '0.61.0' == '0.61.0'\`).` (authored at /slice before /design-slice chose Route B).
  - design.md "Mid-slice smoke gate (operational expansion)": Route B literal is `0.62.0`, recommends atomic bump.
  - Inconsistent — slice-022/023 FBCD-1 sub-mode (a) original-draft cross-file class.
- **Proposed fix**: Update mission-brief.md "Mid-slice smoke gate" block to: `Expected: PASS (\`assert '0.62.0' == '0.62.0'\`) post-Route-B atomic 4-part bump (VERSION + plugin.yaml + ai-sdlc-VERSION + pyproject.toml all on 0.62.0 before the smoke runs).` Cross-link to design.md smoke-gate operational-expansion.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md "Mid-slice smoke gate" block updated to `0.62.0` expected literal + cross-link to design.md operational-expansion section. Per slice-053 multi-site-literal-contrast law: grep verified no other `0.61.0` smoke-gate-literal sites in mission-brief.md / design.md / ADR-056 (Intent paragraph `0.61.0` ref is correctly historical /repro-time state, not a smoke-gate literal). Fix applied at `mission-brief.md`§"Mid-slice smoke gate".

#### M4: BCR-1 round-trip insertion target ambiguity — SC-001 block has BOTH `**Suggested approach:**` and `**Evidence:**` bullets; AC4 verification grep is anchored on `### SC-001 —` but does not verify *position* relative to `**Evidence:**`

- **Claim under review**: mission-brief.md AC4 verification-plan row — *"`grep -A 30 \"^### SC-001 —\" diagnose-out/backlog.md | grep \"Addressed:.*slice-054-fix-pyproject-toml-version-drift\"` returns the line"*.
- **Issue**: Per **BCR-1** (slice-053) the **Addressed** line must go *AFTER `**Evidence:**` AND BEFORE the next `### SC-NNN` header*. AC4's current grep only verifies presence somewhere in the next 30 lines — would PASS even if `/reflect` mis-inserted between `**Source finding:**` and `**Severity:**` (BCR-1-violating placement). Per slice-053 M-add-1 graceful-degradation, BCR-1's insertion semantic is *position-anchored*; AC4's verification is *content-anchored only*. This is the first BCR-1 dogfood — AC4 should pin the position semantic.
- **Evidence**:
  - SC-001 block: L87–L106; `**Evidence:**` at L100, sub-list L101–L105; SC-002 header at L107.
  - `skills/reflect/SKILL.md:59`: *"at the END of the candidate block, AFTER its **Evidence:** sub-bullet list … BEFORE the next ### SC-NNN header"*.
  - AC4 grep is `grep -A 30 "^### SC-001 —" | grep "Addressed:..."` — passes for ANY position in next 30 lines.
- **Proposed fix**: Tighten AC4 verification-plan to position-pinned check via line-number comparison (awk + `grep -n`) OR add an explicit test function `tests/methodology/test_bcr_1_backlog_round_trip_end_to_end.py::test_sc001_addressed_position_after_evidence_before_sc002` invoked at /validate-slice. Default to the position-pinned grep in the verification plan (cheaper, no new test file) AND optionally add the dedicated test function at /build-slice if cheap.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md AC4 verification-plan row tightened to a position-pinned check using awk-extract + `grep -n` line-number comparison (`addressed_line > evidence_last_line` AND `addressed_line < next_sc_header_line`). Pin lives in the verification-plan; no new test file added at /design-slice (Test-first plan AC4 row remains "manual + grep" with the tightened grep). If the position-pinned awk pattern proves too brittle at /build-slice, will mint a dedicated pytest at that time. Fix applied at `mission-brief.md`§"Verification plan" row 4.

### Minors (log; address if cheap)

#### m1: SC-001 backlog block heading carries stale `VERSION = 0.59.0` text

- **Claim under review**: `diagnose-out/backlog.md:13` and `:87` — `### SC-001 — pyproject.toml [project].version = 0.20.0 while VERSION = 0.59.0 — ungated stale pip artifact label`.
- **Issue**: Heading says `VERSION = 0.59.0` (the /diagnose-time value, ~5 versions ago); current is `0.61.0`, post-fix `0.62.0`. AC4's grep is heading-text-prefix-insensitive so the grep works — but a human reading the closed candidate post-fix sees a stale literal. BCR-1 is append-only; doesn't rewrite the heading. This is a `/diagnose` output staleness, not a slice-054 defect.
- **Proposed fix**: No design change. Log as `/critic-calibrate` candidate (should BCR-1 soft-warn on stale closed-candidate headings?).
- **Builder draft**: **DEFERRED** to `/critic-calibrate` discussion — BCR-1 round-trip is correctly append-only per slice-053 ADR-055; rewriting the heading would violate the append-only discipline. Whether `/reflect` should emit a soft-warn for stale literals in closed-candidate headings is a separate methodology refinement question worth surfacing at the next `/critic-calibrate` pass. Logged in milestone.md "Discovered" pending-list for /reflect Step 5.

#### m2: design.md is missing the `Components touched` enumeration that "(See full design.md — …)" parenthetical promises

- **Claim under review**: design.md `## Components touched` section reads *"(See full design.md — components touched: pyproject.toml, VERSION, plugin.yaml, …)"*.
- **Issue**: The "(See full design.md — …)" wording reads as if a more detailed table lives elsewhere; the parenthetical IS the enumeration. Misleading at /critique read-time.
- **Proposed fix**: Drop "(See full design.md — …)" framing; render as a clean bullet list. Cosmetic.
- **Builder draft**: **ACCEPTED-FIXED** — design.md "Components touched" section rewritten as a clean bullet list (the original draft used a parenthetical shortcut since the components were already detailed in "What's new"; the rewrite makes the section self-contained without duplicating "What's new"). Fix applied at `design.md`§"Components touched".

## Dimensions checked

- [x] Unfounded assumptions — M2 (design.md stale-literal enumeration claim does not match actual file's three sites)
- [x] Missing edge cases — none beyond M3 (smoke-gate consistency under Route-B atomic bump)
- [x] Over-engineering — none. Route B + no standalone tool is right scope; ADR-056 correctly rejects Route C
- [x] Under-engineering — M1 (AC3 no design element delivering it), M4 (AC4 position-semantic gap)
- [x] Contract gaps — none. PVFS-1 is methodology invariant, not code API
- [x] Security — none. Static-file invariant, no auth/data exposure
- [x] Drift from vault — none. ADR-056 reversibility honest. MEPD-1 discharge by rule-path (a) cited and verified against actual `tests/methodology/test_methodology_changelog.py` entry-pin pattern. Route B 4-part PMI-1 atomic bump correctly enumerated. AVFS-1 + PMI-1 verified clean pre-bump. SUP-1 N/A. Slice-049/050 precedent verified by reading entry-pin functions at L3219/L3295.
- [x] Web-known issues — skipped (in-repo methodology-invariant slice with no external-platform dependency; PEP 621 [project].version semantics stable; explicitly: no novel issues expected for this slice class)
- [x] Cross-cutting conformance — M2 (CCC-1 mechanical-table-vs-canonical-inventory), M3 (FBCD-1 sub-mode (a) cross-file consistency). SCPD-1 row #54 PVFS-1 enrichment correctly required. PTFCD-1/PTFFD-1: cited test file + function exist on disk (verified). EPGD-1 not at risk (PMI-1 invariant untouched). APED-1 N/A.

## Triage

**Triaged by**: user
**Date**: 2026-05-21
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major  | ACCEPTED-FIXED | design.md "What's new" mints AC3 pin test (co-located in existing test_pyproject_version_matches_version_file.py); mission-brief.md TF-1 row 3 updated with concrete path + function name + PENDING status (TPHD-1 sub-mode (a) harmonized) |
| M2 | Major  | ACCEPTED-FIXED | design.md "What's new" enumerates all 3 stale-literal sites (lines 3 + 6 + 66) with per-site refactor target; M1's universal pin test is the structural backstop |
| M3 | Major  | ACCEPTED-FIXED | mission-brief.md smoke-gate block updated to `'0.62.0' == '0.62.0'` expected literal + cross-link to design.md operational-expansion; multi-site-literal-contrast verified no other smoke-gate-class sites |
| M4 | Major  | ACCEPTED-FIXED | mission-brief.md AC4 verification-plan tightened to position-pinned awk + line-number check (addressed_line > evidence_last AND < next_sc_header); dedicated pytest deferred to /build-slice if needed |
| m1 | Minor  | DEFERRED | /critic-calibrate candidate — BCR-1 append-only is correct per slice-053 ADR-055; stale heading literal soft-warn is a separate methodology refinement |
| m2 | Minor  | ACCEPTED-FIXED | design.md Components-touched section rewritten as clean bullet list |
| M-add-1 | Major | ACCEPTED-FIXED | /critique-review meta-Critic missed finding — design.md entry-pin contract for `test_v_0_62_0_pvfs_1_shippability_consumer_propagation` expanded to assert BOTH `PVFS-1` AND `SC-001` in shippability row #54 (BCR-1 traceability-axis pin on the first end-to-end BCR-1 dogfood slice) |
| m-add-1 | Minor | ACCEPTED-FIXED | /critique-review meta-Critic missed finding — function renamed `test_pyproject_has_no_stale_v_0_20_0_or_count_literals` → `test_pyproject_has_no_stale_0_20_0_or_count_literals` (drop `v_` prefix to match the bare `"0.20.0"` assertion literal); design.md + mission-brief.md TF-1 row 3 TPHD-1 sub-mode (b) harmonized |
