# Critique Review: Slice 056 fix-bcr1-round-trip-test-archive-paths

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-21
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 7 substantive findings (M1, M2, m1-m5) are all VALID with substantially correct severities, and the in-band fix-block dispositions land structurally sound on each. However, an independent re-read surfaces one load-bearing finding the first Critic missed (TF-1 strict-pre-finish gate WILL refuse this brief's plan rows because AC `"4a"/"4b"/"4c"` do not satisfy the `"4"` AC enumerated in the body) plus two lighter-touch additions (a class-level structural backstop for the deferred N=2 R-15 instance; mission-brief vs design Pipeline-position predecessor inconsistency). Verdict EXTEND. The TF-1 finding is build-time-reachable — Builder hits it at /build-slice Step 6.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- M1 (N=1 corpus claim wrong; N=2): confirmed via live grep against `tests/methodology/` — 3 code-surface hits (`test_bcr_1_round_trip_end_to_end.py:43`, `test_ptffd1_no_false_positive.py:46` is `slices_root` non-slice-specific so legitimately excluded, `test_ptffd1_no_false_positive.py:70` is the N=2 instance). Severity Major appropriate; the voluntary-restraint posture rested on N=1 and the design-time corpus enumeration was wrong. Fix-block disposition (acknowledge + defer with rationale + nominate slice-034 retrofit) is structurally correct.
- M2 (1-arg vs 2-arg signature contract surface): confirmed; design.md L145 pre-fix had a "Builder picks at Phase A" alternative that opened a public-API arity surface AC2 didn't encompass. Severity Major appropriate per Newman / Fielding contract-stability framing. Fix-block pin (single-arg + call-time `REPO_ROOT` binding + 2-arg explicit-reject) is the correct choice.
- m1 (AC3 prose-vs-evidence asymmetry on `SLICE_054_DIR` removal): confirmed; the literal-path-RHS-vs-symbol-name distinction was genuinely under-specified. Severity Minor appropriate. Fix harmonized across 3 sites (AC3 + verification-plan row 3 + design AC3 test design).
- m2 (R-15 retirement criteria two-part gate): confirmed against risk-register.md:259; part-(b) is by-definition unsatisfiable by slice-056 itself. Severity Minor appropriate (it's a status-transition framing error, not a build-time-reachable defect). Fix-block disposition (R-15 stays `mitigating`; part-(a) DONE; part-(b) pending future slice) is the safer dogfood of the R-15 entry's own contract.
- m3 (row #54 PASS-flip uncited in AC5): confirmed; design noted it in narrative but AC5 + verification-plan row 5 only enumerated row #56. Severity Minor appropriate (the row #54 PASS-flip was already happening; the issue was traceability not behavior). Fix adds AC5 claim + verification-plan row 5b.
- m4 (Windows path-separator hazard in diagnostic message): confirmed via design.md L88 pre-fix wording reasoning about format without executing. **Severity question raised below.** Fix-block pin (forward-slash f-string template + AC4c substring assertion on FORWARD-SLASH literals + dry-run check) is structurally correct.
- m5 (pathlib glob Windows case sensitivity): confirmed; BRANCH-1 lowercase enforcement does mitigate, but the prior design didn't document. Severity Minor appropriate (documentation gap, not a behavior defect). 2-line note added is the right minimum.
- m6 (META-1 grounding): confirmed informational; live read of test_methodology_changelog.py:127-145 matches the design.md L114 citation.

## Suspicious findings

No suspicious findings. Each finding holds up under independent re-read against design.md and the referenced corpus. Particular checks I performed and rejected as SUSPICIOUS:

- M2's signature pinning is NOT over-rigid for a private test utility — AC2 explicitly names the signature, and `monkeypatch.setattr` semantics genuinely differ between the 1-arg and 2-arg shapes. The first Critic was right to refuse "Builder picks at Phase A" on a contract surface.
- m4's Windows path-separator hazard is NOT a non-issue — the AC4c forward-slash substring assertion would have FAILed at /build-slice Step 6 on a Windows (this repo's) host had the helper used `str(Path(...))`. The pre-fix design.md L88 prose used `f"{active_glob}"` interpolation that did not pin the no-Path-round-trip rule.
- m5's cross-platform note is NOT redundant — even Windows-only repos benefit from documenting platform deltas latent in dependencies (`pathlib.Path.glob`); future CI matrices or contributors on POSIX surface the delta if folder casing ever drifts. The 2-line note is minimum-viable documentation, not over-engineering.

## Missed findings

### M-add-1: TF-1 strict-pre-finish gate WILL fail — AC-row labels `"4a"/"4b"/"4c"` do not satisfy AC body label `"4"`

- **Issue**: mission-brief.md Acceptance criteria enumerates 5 numbered ACs (`1.`, `2.`, `3.`, `4.`, `5.` per the L18/19/20/21/22 list items). TF-1's `_find_acs()` parses these via `_AC_ITEM_RE = r"^\s*(\d+)\.\s+\S"` → `acs_in_brief = ["1","2","3","4","5"]`. The Test-first plan table at mission-brief L28-36 declares AC cells `"4a"`, `"4b"`, `"4c"` (rows for AC4 sub-cases). `_normalize_ac_label()` does `s.replace("ac","").replace("#","").replace(" ","")` — applied to `"4a"` gives `"4a"`, NOT `"4"`. So `rows_by_ac` has keys `{"1","2","3","4a","4b","4c","5"}`. The check `if ac not in rows_by_ac` for `ac="4"` from `acs_in_brief` → **FAIL** (kind=`ac-without-row`).
- **Framework**: Sommerville (verification-traceability) + Hendrickson (TF-1 gate semantics). TF-1's purpose is bidirectional AC ↔ test traceability; the gate is built around `_normalize_ac_label` accepting exactly the body-list numbering.
- **Design.md ref**: mission-brief.md§Test-first plan rows 4-6 (`| 4a | ...`, `| 4b | ...`, `| 4c | ...`) versus mission-brief.md§Acceptance criteria item `4.` (the bare integer).
- **Why missed**: the first Critic checked AC content (m1, m3) but did not exercise `tools/test_first_audit.py` against the rendered TF-1 plan table. TF-1 strict-pre-finish runs at /build-slice Step 6 — this WILL refuse the slice.
- **Why this slice is structurally reachable**: this is a build-time-reachable defect, not a methodology-prose claim. Failure mode: `python -m tools.test_first_audit architecture/slices/slice-056-... --strict-pre-finish` exits 1 with `ac-without-row` for AC#4 because the body has `4.` but rows only carry `4a/4b/4c`.
- **Proposed fix** (meta-Critic option (a) — was inaccurate; the actual fix path is): change plan-row AC cells from `4a/4b/4c` to plain `4` (multi-row-per-AC is the canonical TF-1 shape — `rows_by_ac["4"]` accumulates as a list of rows). The (a)/(b)/(c) sub-branch lettering survives in the prose + the test-function names which disambiguate. Verified live post-fix: TF-1 audit reports CLEAN (8 rows, no `ac-without-row`).
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-review-disposition (this round). Applied:
  - mission-brief.md TF-1 plan table: AC cells `4a/4b/4c` rewritten to plain `4` (3 rows → now 4 rows after M-add-2 adds a 4th); test-function names retain disambiguation.
  - mission-brief.md test-first-plan notes-block: NEW paragraph documenting the `_AC_ITEM_RE = r"^\s*(\d+)\.\s+\S"` integer-only constraint + canonical multi-row-per-AC shape (per /critique-review M-add-1 ACCEPTED-FIXED).
  - design.md "Components touched"/"Test design" sections: AC4 sub-case references updated from `(AC4a)`/`(AC4b)`/`(AC4c)` to `(AC4 row 1)`/`(AC4 row 2)`/`(AC4 row 3)` for consistency with the new shape.
  - Verified post-fix: `$PY -m tools.test_first_audit architecture/slices/slice-056-...` reports CLEAN (8 rows total — 7 helper + 1 BFRD-1 pre-existing).
  - (Meta-Critic's M-add-1 option (a) recommendation to split AC body `4.` into `4a./4b./4c.` would NOT have worked — `_AC_ITEM_RE` requires `\d+\.` not `\d+[a-z]\.` so `4a.` is rejected at the regex layer. Builder verified empirically + chose the canonical multi-row-per-AC fix path that actually passes TF-1 strict-pre-finish.)

### M-add-2: No structural backstop test pins the absence of NEW R-15-class literals in `tests/methodology/*.py`

- **Issue**: the slice fixes the N=2 first instance (slice-054 literal) and explicitly defers the N=2 second instance (slice-034 literal) with rationale. Both are point fixes — neither prevents a fourth instance landing in a future test module. A cheap structural test would assert "no `tests/methodology/*.py` file carries a literal `REPO_ROOT / "architecture" / "slices" / "(archive/)?slice-\d{3}-` substring except the known whitelisted N=2 (with the slice-034 retrofit pending)". This is the analog of slice-053's M2 SC-grammar literal pin (R-13-hedge backstop), applied to the R-15 class.
- **Framework**: Newman, *Building Microservices* (consumer-side contract test); the helper is the runtime contract, the corpus test is the audit that callers consume the contract instead of recurring the anti-pattern.
- **Design.md ref**: design.md§Defensive / out-of-scope branches L191 acknowledges the corpus surface and the N=2 deferral but does NOT pin a regression backstop for the class. design.md§Test design (test #5 `test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir`) pins ONE module's regression but not the class.
- **Why this matters**: R-15's `**Status**: mitigating` part-(b) waits for a future slice to demonstrably use the helper. Between now and that future slice, ANY new test module that hardcodes a slice-NNN literal silently re-violates the class without surfacing — the same R-15 latency the entry warns about. A corpus-level regression test closes the class loop independent of part-(b).
- **Proposed fix**: add one test in `tests/methodology/test_resolve_slice_dir.py` (or a sibling) that greps `tests/methodology/*.py` for `REPO_ROOT\s*/\s*"architecture"\s*/\s*"slices"\s*/\s*("archive"\s*/\s*)?"slice-\d{3}-` and asserts the match-set is a subset of the known whitelist (currently just slice-034 line 70 until that retrofit lands). Cost: ~15 lines + maintenance burden on the whitelist (whitelist shrinks when slice-034 retrofit lands → asserts zero matches → R-15 part-(b) is structurally satisfied). Severity Major (class-closure backstop; without it, R-15 mitigation is point-fix only).
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-review-disposition. Applied:
  - mission-brief.md AC4: expanded prose from "Three regression tests" → "Four regression tests for `_resolve_slice_dir(NNN)` + the R-15 class"; new sub-(d) prose adds the corpus class-closure backstop with whitelist-shrinkage as the structural mechanism for R-15 part-(b) retirement.
  - mission-brief.md TF-1 plan table: NEW 4th row under AC `4` for `test_no_new_archive_fragile_literals_in_methodology_corpus` (PENDING).
  - mission-brief.md verification-plan row 4: rewritten to expect 6 passing tests (was 5) + added explicit TF-1 strict-pre-finish dry-run claim.
  - design.md "What's new" test-module enumeration: bumped from 5 tests to 6 tests; new test described with explicit whitelist + structural-mechanism prose.
  - design.md "Helper-test fixture choices": NEW dedicated section for the corpus backstop test (grep regex + whitelist + pass criterion + design-time verification that `conftest.py` is excluded by the regex anchor).
  - Severity sustained at Major (per meta-Critic).

### M-add-3: mission-brief.md§Pipeline position `predecessor: /reflect` vs design.md§Pipeline position `predecessor: /slice` — internal inconsistency

- **Issue**: mission-brief.md L106 declares `predecessor: /reflect` (the brief views itself as authored by `/slice`, whose immediate per-slice-loop predecessor in the canonical chain is `commit-slice → /slice` per `tools/pipeline_chain_audit.py:73-82`, NOT `/reflect`). design.md L210 declares `predecessor: /slice` (correct — `/design-slice`'s predecessor in the canonical chain IS `/slice`). The mission-brief predecessor value is wrong per the canonical chain; it conflates "the prior slice ended at `/reflect`" with "this artifact's per-skill predecessor".
- **Framework**: PCA-1 chain-shape semantics (`_CANONICAL_CHAIN` in pipeline_chain_audit.py).
- **Design.md ref**: mission-brief.md L106 vs design.md L210; canonical chain `("slice", "/design-slice", True)` with `slice`'s predecessor being `commit-slice` (the loop closure).
- **Why missed**: the first Critic's m6 was about META-1 grounding, not PCA-1. PCA-1's audit (`pipeline_chain_audit.py`) only scans `skills/*/SKILL.md`, not slice-local mission-brief.md/design.md Pipeline-position blocks — so this is NOT structurally gated. It's an artifact-internal inconsistency.
- **Why it matters even though ungated**: PCA-1 prose contract relies on Pipeline-position blocks being readable and consistent; future `/critic-calibrate` runs across slice artifacts may surface confusion. Cheap fix.
- **Proposed fix**: mission-brief.md L106 → `predecessor: /commit-slice` (per the canonical chain) OR `predecessor: /slice (this artifact's authoring skill)` (clearer prose). Severity Minor (cosmetic; no gate fires; just internal doc fidelity).
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-review-disposition. Applied:
  - mission-brief.md Pipeline-position predecessor: `/reflect (slice-055 just shipped)` → `/commit-slice (canonical chain per PCA-1 tools/pipeline_chain_audit.py:80-81 — reflect → /commit-slice (auto-advance false), commit-slice → /slice (auto-advance false). Per /critique-review M-add-3 ACCEPTED-FIXED — prior wording modeled the loop-entry from user perspective but contradicted the canonical chain; this artifact's authoring skill is /slice whose canonical chain predecessor is /commit-slice)`.

## Severity adjustments

### m4 SEVERITY-WRONG candidate (soft — leave as Minor)

- **Finding**: m4 (Windows path-separator hazard) was filed Minor. The hazard is genuinely build-time-reachable: had the Builder coded `str(Path(...))` formatting, AC4c's forward-slash substring assertion would have FAILED at /build-slice Step 6 on a Windows host, blocking the slice. By the "build-time-reachable on the slice's own host" criterion, this is Major-class.
- **Counter**: the design.md L88 pre-fix code snippet already used `f"{active_pattern}"` interpolation on a `Path` object (which Windows-stringifies to backslash, but the OPERATOR was clearly heading toward an f-string template, not a `str(Path(...))` round-trip). The hazard was that the design TRIPS the Builder, not that it definitively WOULD have. Calling it Minor is defensible because the fix is structurally cheap (no signature change, no algorithm change) and the design.md disposition was already heading the right direction.
- **Recommendation**: LEAVE as Minor. The fix-block pin (forward-slash literal + dry-run check) closes the gap; severity escalation would be over-reading. The first Critic's calibration on this is defensible.
- **Builder draft**: **ACCEPTED-NO-CHANGE** — meta-Critic's own recommendation is to leave m4 as Minor; severity-wrong call NOT adopted.

No other severity adjustments.

## Notes

Confidence: high on M-add-1 (TF-1 AC numbering — verified by reading `tools/test_first_audit.py` `_normalize_ac_label` + `_find_acs` + `acs_in_brief`-vs-`rows_by_ac` cross-check; this WILL fire at strict-pre-finish — empirically confirmed: `python -m tools.test_first_audit architecture/slices/slice-056-... --strict-pre-finish` pre-fix exited 1 with `ac-without-row AC#4`; post-fix non-strict exits 0 CLEAN). Confidence: medium on M-add-2 (corpus structural backstop — cheap and aligned with the slice-053 M2 R-13 hedge pattern; voluntary-restraint reasonably argues for OR against, Builder chose to accept since it folds into AC4 without exceeding the ≤5 AC limit). Confidence: low on M-add-3 (internal inconsistency, ungated, easy fix; flagged primarily for clean-room artifact hygiene).

Calibration observation on the first Critic in this slice: structurally precise on prose-claim accuracy (M1's N=1→N=2 corpus rescan caught a genuinely wrong empirical claim — the strongest move in the review) and on contract-surface ambiguity (M2 arity), but did not exercise the `tools/test_first_audit.py` AC-row label normalization against the rendered plan table. The N=8 dual-Critic zero-false-alarm streak holds modulo the M-add-1 build-time-reachable miss, which is recoverable in TRI-1 triage. No pressure to manufacture findings — M-add-1 is mechanically verifiable, M-add-2 is a cheap class-closure backstop the slice's voluntary-restraint posture can rationally accept or defer, M-add-3 is cosmetic. The first Critic's 7 substantive findings + ACCEPTED-FIXED dispositions remain sound.
