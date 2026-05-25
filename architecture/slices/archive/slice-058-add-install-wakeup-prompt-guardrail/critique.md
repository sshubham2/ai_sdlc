# Critique: Slice 058 add-install-wakeup-prompt-guardrail

**Critic reviewed**: mission-brief.md, design.md, ADR-057
**Date**: 2026-05-22
**Result**: NEEDS-FIXES

## Summary

The slice is well-scoped and the INSTALL.md → global-CLAUDE.md placement decision (ADR-057) is sound. Two blockers: a cross-file test-function-name inconsistency (FBCD-1 sub-mode (a)), and a stale `v0.54.0` version literal at `INSTALL.md:18` that the slice will touch and leave knowingly false. Two majors sharpen AC3's test-row count and AC2's "genuine contrast" assertion design. The Inclusion-heuristic "no bump" classification was adjudicated by the Critic and **upheld**.

## Findings

### Blockers (must address before /build-slice)

#### B1: Test-function name inconsistent across three slice-authoring sites (FBCD-1 sub-mode (a) / TPHD-1)
- **Claim under review**: mission-brief.md test-first plan row 3 + verification plan #3 name `test_shippability_row_58_present_and_cites_install_wakeup_guardrail`; design.md "Wiring matrix" named `test_shippability_catalog_has_row_for_wakeup_guardrail`.
- **Issue**: per FBCD-1 sub-mode (a), a test function name asserted across multiple slice-authoring files MUST be byte-identical at every site. The same test was named two different things across mission-brief.md and design.md — a stale claim the Builder would otherwise reconcile mid-build.
- **Evidence**: mission-brief.md test-first plan vs design.md wiring-matrix `Consumer test` cell.
- **Proposed fix**: pick one canonical name byte-identical at all sites; recommend `test_shippability_row_58_present_and_cites_install_wakeup_guardrail` (matches the `test_shippability_row_56/57_present_and_cites_r15` convention).
- **Builder draft**: ACCEPTED-FIXED — design.md wiring-matrix `Consumer test` cell changed to `test_shippability_row_58_present_and_cites_install_wakeup_guardrail`; the new "## Test design notes" section pins the name as canonical and byte-identical across all three sites. Mission-brief already used the canonical name at both its sites — no mission-brief edit needed (TPHD-1 sub-mode (a) already satisfied there).

#### B2: Slice touches INSTALL.md but leaves the stale `v0.54.0` literal at INSTALL.md:18
- **Claim under review**: design.md "Components touched → INSTALL.md (modified) — This slice adds one step to it"; AC3 pins a regression test against INSTALL.md.
- **Issue**: `INSTALL.md:18` says "methodology v0.54.0 — see `VERSION`" but `VERSION` is `0.62.0`. slice-045 set line 18 to a hard literal that re-drifted across the 048–054 bumps. Shipping a slice that edits INSTALL.md while knowingly leaving a false version literal in the same file is a brownfield-rule violation ("Code is truth, docs are hypothesis").
- **Evidence**: `INSTALL.md:18` (`v0.54.0`) vs `VERSION` (`0.62.0`); slice-045 `test_install_md_correctness.py` only pins the specific `v0.20.0` literal, so the `v0.54.0` re-drift is unguarded.
- **Proposed fix**: (a) fix it in-scope (preferably drift-proof: drop the literal, reference `VERSION`); or (b) record an explicit out-of-scope line.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" item 6 + the INSTALL.md component-touched line now make the cleanup in-scope: build greps INSTALL.md for **every** stale current-version literal and rewords each **drift-proof** (drop the hard literal, reference `VERSION`). The new regression test is NOT generalized to pin version literals — declined as scope creep (the drift-proof reword needs no test by construction; the Critic explicitly left this to Builder's call).

### Majors (address this slice)

#### M1: AC3 row-count ambiguity — one test or two?
- **Claim under review**: mission-brief test-first plan has one AC3 row; design.md wiring matrix described a separately-named self-pinning function.
- **Issue**: ambiguous whether AC3 needs one test or two; TF-1 row-coverage needs every AC to have unambiguous test-row coverage.
- **Evidence**: mission-brief test-first plan vs design.md wiring matrix.
- **Proposed fix**: state explicitly that AC3 is delivered by exactly one function doing both (row-present) and (cites-slice) assertions; identical name in the wiring matrix.
- **Builder draft**: ACCEPTED-FIXED — design.md "## Test design notes → AC3" now states AC3 is delivered by exactly ONE function (`test_shippability_row_58_present_and_cites_install_wakeup_guardrail`) making both assertions; collapses into B1's single harmonization.

#### M2: "Genuine contrast" must-not-defer under-specified — AC2 needs discrete per-fact assertions
- **Claim under review**: must-not-defer "no tautological pin"; AC2 test `test_wakeup_block_states_load_bearing_facts` collapses three facts + a carve-out into one function.
- **Issue**: AC2 assertions could be written so loose (e.g. heading-only) they pass tautologically; each load-bearing fact + carve-out needs a discrete content-specific assertion. The prose-pin is also R-2-class (guards prose existence, not runtime behavior) and that limitation should be a recorded decision.
- **Evidence**: AC2 enumerates three facts + a carve-out; the test-first plan collapses them into one function; R-2 limitation.
- **Proposed fix**: design.md specifies AC2's test asserts four discrete substrings (one per fact + carve-out), each FAILing individually pre-edit; state explicitly it is an R-2-class prose-existence pin.
- **Builder draft**: ACCEPTED-FIXED — design.md "## Test design notes → AC2" now specifies four discrete assertions (literal-replay / never-as-no-op / `/loop`-carve-out / harness-notifies context), each FAILing individually at the mid-slice smoke gate; the section preamble explicitly records the R-2-class prose-existence-pin limitation as an accepted decision (behavioral test infeasible — step runs only at install time).

### Minors (log; address if cheap)

#### m1: ADR-057 numbering — verified clean
- **Claim under review**: design.md "[[ADR-057]]".
- **Issue**: none — ADR-056 is the prior max; ADR-057 is correct and already on disk with slice-058 attribution. Logged to ensure the Builder does not double-create/renumber it.
- **Evidence**: `architecture/decisions/` — ADR-056 prior max, ADR-057 present.
- **Proposed fix**: none needed; Builder treats ADR-057 as already authored.
- **Builder draft**: ACCEPTED-FIXED — no change required; confirmed ADR-057 is correctly numbered and already authored. design.md "What's new" item 5 updated to explicitly note build must NOT recreate or renumber it.

#### m2: design.md `## v0.63.0` next-version reference — confirmed correct
- **Claim under review**: design.md Inclusion-heuristic section references `## v0.63.0` as the hypothetical bump target.
- **Issue**: none — `VERSION` is `0.62.0`, latest changelog entry `## v0.62.0`, so `v0.63.0` is the correct next version. Logged to confirm no miscompute.
- **Evidence**: `VERSION` = `0.62.0`; `methodology-changelog.md` latest = `## v0.62.0`.
- **Proposed fix**: none — correct as written.
- **Builder draft**: ACCEPTED-FIXED — no change required; confirmed correct.

## Inclusion-heuristic adjudication

The Critic explicitly adjudicated (not rubber-stamped) the flagged "no `methodology-changelog.md` entry / no `VERSION` bump / no new RULE-ID" classification and **UPHELD** it: slice-058 adds no pipeline capability (distinguishable from slice-052 `--obo`), mints/extends no RULE-ID (distinguishable from slice-049 OSDG-1), and is structurally the slice-045 INSTALL.md-prose conformance class. The slice-045 precedent was confirmed against the enforcing artifact (`test_install_md_correctness.py` carries `Rule reference: INST-1`, no `v0.45.0`-class entry), not the claim. Caveat carried forward: `/build-slice` must discharge MEPD-1(b) **by name** against the real META-1 assertion at `tests/methodology/test_methodology_changelog.py:136` at the build-log no-changelog decision point — design.md rationale point 5 already commits to this.

## Dimensions checked
- [x] Unfounded assumptions — folded into B2 (INSTALL.md:18 stale literal); Step 3d structural-twin claim + INSTALL.md:198 citation + tool-count (26) all verified accurate.
- [x] Missing edge cases — none; error model covers heading-present / file-absent / user-declines.
- [x] Over-engineering — none; minimal surface (one step, one test, one ADR, one row).
- [x] Under-engineering — M1 (AC3 row-count), M2 (genuine-contrast under-specification).
- [x] Contract gaps — none; no endpoints/events/schemas.
- [x] Security — none; confirmation-gated + diff-shown global-CLAUDE.md write, static advisory prose.
- [x] Drift from vault — folded into B2; ADR-057 numbering clean (m1); ADR-057 does not contradict ADR-049.
- [x] Web-known issues — skipped (no external technology/API/platform-version dependency; ScheduleWakeup is a harness tool documented from lived experience).
- [x] Cross-cutting conformance — B1 (FBCD-1 sub-mode (a)), M1 (TF-1 row-coverage); SCPD-1 row #58 correct; MEPD-1(b) documented-why-none branch validly available.

## Meta-Critic missed findings (DR-1 EXTEND)

`/critique-review` returned **EXTEND** — all 6 first-Critic findings confirmed VALID with correct severity, no suspicious findings, plus 2 missed findings:

#### M-add-1: AC2's four-discrete-assertion design pins a block still labelled "Draft" — test/text coupling risk
- **Issue**: design.md "What's new" item 2 labelled the block "Draft:" while the AC2 test pins discrete substrings against it; test and text could drift apart at build.
- **Proposed fix**: freeze the block as canonical (drop "Draft:"); AC2 test anchors on verbatim substrings from the frozen block.
- **Builder draft**: ACCEPTED-FIXED — design.md item 2 now declares the block FROZEN canonical wording (verbatim append); "Test design notes → AC2" names the four verbatim anchor phrases (`literally, as fresh user input` / `no-op label, heartbeat, or fallback wakeup` / `/loop` + `are unaffected` / `notifies you on completion`) with whitespace-collapse so line-wrapping is irrelevant.

#### M-add-2: the new install step had no specified placement/identifier in INSTALL.md's Step 3a-3g sequence
- **Issue**: design.md said "a new step modelled on Step 3d" but never said where it slots.
- **Proposed fix**: name the exact insertion point + identifier.
- **Builder draft**: ACCEPTED-FIXED — design.md item 1 now specifies the step as `### 3h: Global CLAUDE.md — wakeup-prompt discipline`, appended after `3g`, no renumber (rationale: INSTALL.md's "Source independence" section cross-references Step 3f/3g by letter — a renumber is a wide-edit drift risk; the step is order-independent). "Test design notes → AC1" anchors the test on the heading text, not the `3h` letter.

**B2 fix-wording precision note** (meta-Critic informational, not a separate finding): the meta-Critic verified `INSTALL.md:18` is the SOLE stale current-version literal. design.md item 6 was tightened to name that single line (with a re-grep confirmation) rather than the over-broad "every literal" wording.

## Triage

**Triaged by**: user
**Date**: 2026-05-22
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | canonical test-fn name `test_shippability_row_58_present_and_cites_install_wakeup_guardrail` pinned across all 3 sites — design.md wiring matrix + Test design notes |
| B2 | Blocker | ACCEPTED-FIXED | INSTALL.md:18 stale-literal drift-proof reword added in-scope — design.md What's-new item 6 |
| M1 | Major | ACCEPTED-FIXED | AC3 = exactly one function making two assertions — design.md Test design notes → AC3 |
| M2 | Major | ACCEPTED-FIXED | four discrete asserts, each FAIL-able pre-edit — design.md Test design notes → AC2 |
| m1 | Minor | ACCEPTED-FIXED | ADR-057 numbering verified clean; build instructed not to recreate — design.md item 5 |
| m2 | Minor | ACCEPTED-FIXED | v0.63.0 next-version reference verified correct; no change required |
| M-add-1 | Major | ACCEPTED-FIXED | block frozen canonical + 4 verbatim anchor phrases — design.md item 2 + Test design notes → AC2 |
| M-add-2 | Major | ACCEPTED-FIXED | step placement specified as `### 3h`, no renumber — design.md item 1 + Test design notes → AC1 |
