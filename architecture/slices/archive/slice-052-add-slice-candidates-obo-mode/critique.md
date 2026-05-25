# Critique: Slice 052 add-slice-candidates-obo-mode

**Critic reviewed**: mission-brief.md, design.md, new ADRs (ADR-054)
**Date**: 2026-05-20
**Result**: NEEDS-FIXES (first Critic) → CLEAN (post-TRI-1: all ACCEPTED-FIXED)

## Summary

Well-scoped slice; ADR-054 deviation properly bounded. But the load-bearing
"annotated-copy parity" contract (must-not-defer #5, AC4) was specified two
ways that silently produce a byte-different file on any non-ASCII finding
(which `/diagnose` routinely emits), and the parity *target* was mis-stated as
browser-output byte-equality (the browser does a full `outerHTML` re-render,
unreproducible from Python and irrelevant to the only consumer). All 9 findings
are execution-backed and VALIDATED; the Builder applied the cheap design fixes
this round.

## Findings

### Blockers (must address before /build-slice)

#### B1: `json.dumps` default `ensure_ascii=True` breaks byte-parity with browser `JSON.stringify` on any non-ASCII finding
- **Claim under review**: design.md parity step 4 `json.dumps(data, indent=2)`; AC4 "byte-equivalent"; must-not-defer #5 "mis-parses silently".
- **Issue**: Critic executed both serializations — Python default `ensure_ascii=True` emits `é`; browser `JSON.stringify` (assemble.py L1709) emits raw UTF-8. `/diagnose` routinely emits non-ASCII (`assemble.py` L2130 `💡`, smart quotes, accented identifiers). The annotated copy would diverge from the manual-round-trip control silently (`json.loads` decodes both forms identically, so `parse_html_state` still parses → no error).
- **Evidence**: `assemble.py` L1709, L2117, L2130; `build_backlog.py` L60-62; empirical run in the Critic transcript.
- **Proposed fix**: `json.dumps(data, indent=2, ensure_ascii=False)`; golden test with non-ASCII fixture asserting `backlog.md` byte-equality.
- **Builder draft**: ACCEPTED-FIXED — design.md parity step 4 now mandates `ensure_ascii=False` with the rationale + the `<\/` single-backslash clarification; mission-brief must-not-defer #5 + verification row 4 updated; golden test (M3) pins it with an emoji+accent fixture. Note: once B2 redefines the contract to `backlog.md`-equality, B1's *practical* impact narrows (loads decode identically) — but `ensure_ascii=False` is the correct faithful-to-browser choice and costs nothing, so fixed regardless.

#### B2: Parity target is the whole-document `outerHTML` re-render, not "substitute only the script block into the byte-identical original"
- **Claim under review**: design.md step 5 + "byte-faithful to the browser Save output"; AC4.
- **Issue**: Browser save = `'<!DOCTYPE html>\n' + document.documentElement.outerHTML` (assemble.py L1712) — a full DOM re-serialization the engine normalizes (attribute quoting/order, whitespace, entities). "Byte-faithful to browser output" is unachievable from Python AND unnecessary: the only consumer, `parse_html_state()`, reads only the `diagnose-data` script block. The script-substitution implementation is *correct*; the *spec wording* was wrong/untestable.
- **Evidence**: `assemble.py` L1707-1721; design.md step 5 (pre-fix).
- **Proposed fix**: redefine parity operationally — `parse_html_state` annotations equal the decisions under `collect()` semantics AND `backlog.md` byte-identical to the manual round-trip; drop "byte-faithful to browser outerHTML".
- **Builder draft**: ACCEPTED-FIXED — design.md "Annotated-copy parity" rewritten with the operational invariant; AC4, must-not-defer #5, verification row 4 updated to assert `backlog.md` byte-equality, not annotated-HTML byte-equality. Implementation strategy unchanged (it was right).

### Majors (address this slice)

#### M1: `collect()` parity — DOM key order + empty-entry handling under-specified
- **Issue**: `collect()` iterates DOM (severity-grouped) order, not `state.findings[]` order; key order is irrelevant to `build_backlog.py` (re-sorts) but the design claimed byte-parity without saying so. AC5 "leaves unreviewed findings with empty annotations" reads as if it writes `{confirmed:""}` entries; `collect()`'s `if(conf||notes)` gate *omits* them.
- **Evidence**: `assemble.py` L1635-1646, L2094-2097; `build_backlog.py` L95-108; AC5 vs design step 3.
- **Proposed fix**: state key-order irrelevance; reword AC5 to "unreviewed = absent from map".
- **Builder draft**: ACCEPTED-FIXED — design step 3 now states key-order is not part of the contract (with the `confirmed_findings`/re-sort cite); AC5 reworded to "absent, NOT empty entries".

#### M2: Resume predicate (deferred vs never-reached) unstated
- **Issue**: `--obo-extract` `current` derives from `annotations`, which omits unreviewed findings. "First unreviewed" = first `id ∉ annotations`. A Deferred finding writes `confirmed:"defer"` and IS in the map → skipped on resume; design never stated this or that the report must distinguish never-reached vs deferred.
- **Evidence**: `build_backlog.py` L95, `collect()` L1643; design `--obo-extract` contract; AC5.
- **Proposed fix**: state resume predicate = `id ∉ annotations`; Deferred not re-offered; report distinguishes the two counts.
- **Builder draft**: ACCEPTED-FIXED — AC5 + design `--obo-extract` contract now state the predicate explicitly and the report-distinction requirement.

#### M3: TF-1 posture — `test-first:false` indefensible for the deterministic helpers
- **Issue**: AC4 / must-not-defer #5 are silent-divergence contracts; B1/B2 are exactly the class an automated golden test catches at build time. `test-first:false` is fine for the conversational `AskUserQuestion` loop (Python can't drive it), not for `--obo-extract`/`--obo-write`/`--obo-peek`.
- **Evidence**: mission-brief verification rows 4-5 (manual); `build_backlog.py` is pure-function-testable.
- **Proposed fix**: add a deterministic golden regression test for the helpers; keep test-first:false for the loop only.
- **Builder draft**: ACCEPTED-FIXED — design.md "Test plan" section added (`tests/methodology/test_slice_candidates_obo.py`: non-ASCII fixture, original-hash invariance, `parse_html_state` equality, `backlog.golden.md` byte-equality, `--obo-peek` traversal cases, `--obo-extract` order/resume/duplicate, default-path regression); verification rows 3-5 now cite the concrete test path; `**Test-first**: false` annotated to scope it to the conversational loop only.

#### M4: must-not-defer #3 "mechanically bounded" not delivered — enforcement was prompt-level
- **Issue**: design put the scoped-peek enforcement in Claude prose ("the skill MAY read … restricted to …"). A SKILL.md instruction telling Claude to self-restrict IS honour-system; must-not-defer #3 explicitly demands "mechanically bounded, not honour-system". No mechanical gate is possible if the reader is Claude.
- **Evidence**: ADR-054 Decision/Consequences (pre-fix); design "scoped peek performed by Claude"; must-not-defer #3.
- **Proposed fix**: route source reads through an `--obo-peek` helper subcommand resolving the allow-set + `Path.resolve()` containment refusal (Critic recommended this over downgrading the wording).
- **Builder draft**: ACCEPTED-FIXED — adopted the stronger option: new `--obo-peek --finding <id> --file <path>` subcommand with `Path.resolve()` containment is now the SOLE source-read channel; SKILL.md forbids direct `Read` of repo source under `--obo`; ADR-054 Decision/Consequences, design "build_backlog.py" component, Authorization model, Error model, mission-brief AC3 + must-not-defer #3 all updated to the mechanical form; `--obo-peek` traversal cases in the M3 golden test.

### Minors (log; address if cheap)

#### m1: `parse_html_state()` doesn't detect duplicate `diagnose-data` blocks
- **Issue**: reused `parse_html_state()` (L47-51) is non-greedy, silently takes the first; design promised "absent/duplicate … exits non-zero" — duplicate detection is NOT inherited.
- **Builder draft**: ACCEPTED-FIXED — design `--obo-extract` + error-cases now state duplicate detection is NEW `re.findall`-count logic, not inherited.

#### m2: `decisions.json` temp-file cleanup + concurrent collision unspecified
- **Builder draft**: ACCEPTED-FIXED — design "Data model deltas" now specifies `tempfile.mkstemp()` (unique name) + `finally` cleanup.

#### m3: OSDG-1 "Discovered nomination" asserted, not yet recorded
- **Issue**: slice-050 lesson — never treat "self-run sufficient" as written; ensure the nomination is physically written during build.
- **Builder draft**: ACCEPTED-FIXED — design OSDG-1 section + mission-brief must-not-defer #6 now require a `risk-register.md` sub-entry + `reflection.md` Discovered entry, pre-finish grep-verified.

## Dimensions checked
- [x] Unfounded assumptions — B1, B2, m1 (Critic executed serializations, not just read prose)
- [x] Missing edge cases — M2 (resume), m2 (concurrent temp); non-ASCII folded into B1
- [x] Over-engineering — none (entrypoints reuse existing helper; ADR minimally scoped)
- [x] Under-engineering — M3 (no automatable design element for silent-divergence ACs), M4 (mechanical bound not delivered)
- [x] Contract gaps — M1 (collect() order/empty semantics), m1 (duplicate detection)
- [x] Security — none beyond M4 (read-only, local single-user, no network/secrets)
- [x] Drift from vault — none (ADR-054 append-only, next free ID, supersedes null, amends Hard rule #2 by reference per SUP-1; all cited code lines verified)
- [x] Web-known issues — none novel (browser outerHTML normalization captured first-principles in B2)
- [x] Cross-cutting conformance — APED-1 satisfied (serializations executed); no PMI-1/INST-1 surface; TPHD-1/SCPD-1 N/A

## Triage

**Triaged by**: user
**Date**: 2026-05-20
**Final verdict**: CLEAN

Dual-review reconciled (critique-review.md verdict: EXTEND — 0 suspicious, 2
missed Majors added, 1 severity bump). User ratified all dispositions as
ACCEPTED-FIXED; m1 severity bumped Minor→Major per meta-Critic recommendation
(calibration: first-Critic severity-underweight on a silent-correctness path).
All fixes applied to mission-brief.md / design.md / ADR-054 this round.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md§annotated-copy-parity step 4 — `ensure_ascii=False` + non-ASCII golden fixture |
| B2 | Blocker | ACCEPTED-FIXED | design.md§annotated-copy-parity — parity redefined operationally (`backlog.md` + `parse_html_state` equality); AC4/MND#5/verif row 4 |
| M1 | Major | ACCEPTED-FIXED | design.md step 3 key-order-irrelevant note; AC5 reworded "absent not empty" |
| M2 | Major | ACCEPTED-FIXED | AC5 + design `--obo-extract` contract — resume predicate `id ∉ annotations`, Deferred not re-offered |
| M3 | Major | ACCEPTED-FIXED | design.md§Test-plan — mandatory `tests/methodology/test_slice_candidates_obo.py`; test-first:false scoped to loop |
| M4 | Major | ACCEPTED-FIXED | new `--obo-peek` `Path.resolve()` containment; ADR-054 + Authz + MND#3 + AC3 updated to mechanical form |
| M-add-1 | Major | ACCEPTED-FIXED | design `--obo-extract` + AC5 — documented Defer reopen path (re-run on original / hand-edit); SKILL.md operator guidance |
| M-add-2 | Major | ACCEPTED-FIXED | design.md step 5 — match-span string slicing mandated, NOT `re.sub`; golden test gets backslash+`</` notes case |
| m1 | Major | ACCEPTED-FIXED | severity bumped Minor→Major (user-ratified); NEW `re.findall` duplicate-block detection, not inherited from `parse_html_state()` |
| m2 | Minor | ACCEPTED-FIXED | design.md§Data-model — `tempfile.mkstemp()` + `finally` cleanup |
| m3 | Minor | ACCEPTED-FIXED | design.md§OSDG-1 + MND#6 — risk-register sub-entry + reflection Discovered, pre-finish grep-verified |
