# Critique: Slice 108 add-fbcd-1-cardinality-fanout-sub-mode

**Critic reviewed**: mission-brief.md, design.md, project-frame.md (no new ADRs — versioned refinement of ADR-022 via the v0.83.0 changelog entry)
**Date**: 2026-06-03
**Result**: NEEDS-FIXES

## Summary

A genuinely well-prepared slice: the AP-10 fan-out it is built to catch is itself NOT under-enumerated (the Critic verified the rolling-test name lives only at the two row-#75 cells + the test definition), the version-cascade obligations 3-5 are exactly the slice-105 misses, no Dim-9 sub-clause-count pin moves when a sub-MODE is added, and the RSAD-1 self-application sweep is planned. Findings are two Majors (an unspecified entry-pin substantive-content phrase that risks a tautological-green pin; a docstring/literal sweep the design under-framed as "4 leg literals") plus two minors — all addressable in-slice, no blocker, no spike.

## Findings

### Blockers (must address before /build-slice)

None. Every load-bearing structural claim verified against the worktree holds: the rolling-test rename fan-out is fully enumerated (row #75 only), the `_lists_twelve_sub_clauses` pin counts sub-CLAUSES (unmoved by a sub-MODE add), the `_names_both_sub_modes` test asserts (a)/(b) presence via `in body` (so adding (c) inside the same anchor range does not break it), and the regression-test name is unused (the failing-repro genuinely fails first).

### Majors (address this slice)

#### M1: v0.83.0 entry-pin substantive-content phrase is unspecified — risks a tautological-green pin
- **Claim under review**: design.md — "a new entry-pin test `test_v_0_83_0_fbcd_1_v1_1_entry_present_in_repo` (mirrors `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo`)".
- **Issue**: The CCC-1 v1.1 template (`test_methodology_changelog.py:196-224`) asserts THREE things: `## v0.24.0` present, `CCC-1 v1.1` rule-ref present, AND a **substantive canonical phrase** (`design.md mechanical tables`) — the last is what makes it content-bearing. The slice-039 meta-Critic M-add-1 codified exactly this: a content-bearing deliverable needs a CONTENT pin, not a presence-only pin (a tautological green) — `test_critique_agent.py:1201-1206`. The design never named which substantive phrase the v0.83.0 entry-pin asserts; a presence-only pin (`## v0.83.0` + `FBCD-1 v1.1`) would pass whether or not the entry documents the cardinality-fan-out semantics.
- **Evidence**: `test_methodology_changelog.py:221` (CCC-1 template substantive assert) + `test_critique_agent.py:1201-1206` (slice-039 content-pin discipline) + `test_v_0_82_0_decouple_entry_present_in_repo` (L5708, asserts 7 substantive anchors).
- **Proposed fix**: Specify the substantive phrase the v0.83.0 entry-pin asserts (e.g. `Counted-set cardinality fan-out` AND `FBCD-1 (v1.1)` AND `Rule reference`), mirroring the CCC-1 template's third assert.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"What's new" (test_methodology_changelog bullet) + §"Components touched" bullet + §"Tests touched" table now require the entry-pin to assert ALL of `## v0.83.0` + `FBCD-1 (v1.1)` + `Rule reference` + the substantive phrase **`Counted-set cardinality fan-out`** (presence-only pin explicitly forbidden).

#### M2: "4 leg literals" under-frames the rolling-test rename — the function body has 12 `0.82.0` + 2 `0.81.0` literals
- **Claim under review**: design.md + mission-brief AC#3 — "rename … (4 leg literals + docstring)".
- **Issue**: The function body (`test_methodology_changelog.py:5496-5540`) has **12 occurrences of `0.82.0`** and **2 of `0.81.0`**. "4 legs" refers to the 4 ASSERT statements, but the rename requires sweeping ALL 12 `0.82.0`→`0.83.0` literals, PLUS updating the predecessor docstring line `0.81.0 → 0.82.0 (slice-105)` → `0.82.0 → 0.83.0 (slice-108)`, PLUS appending `108` to the rename-precedent chain. The "+ docstring" was a catch-all (so this is a Major, not a Blocker) — but the slice teaching the Critic to grep ALL count literals must not itself under-frame its own literal sweep.
- **Evidence**: `test_methodology_changelog.py:5496` function body — `0.82.0`×12, `0.81.0`×2; L5497 (predecessor line), L5513-5514 (precedent chain).
- **Proposed fix**: Reword to a grep-verified enumeration: "sweep all 12 `0.82.0`→`0.83.0` literals (4 asserts + docstring) + the `0.81.0→0.82.0` predecessor line + append `108` to the chain."
- **Builder draft**: **ACCEPTED-FIXED** — propagated to ALL SIX sites carrying the claim (FBCD-1 sub-mode (a) applied to the fix-delta): design.md §"What's new", §"Components touched" bullet, §"Version-bump cascade" obligation 3, §"Tests touched" table + mission-brief AC#3 + must-not-defer cascade bullet — each now states the grep-verified 12-literal + predecessor-line + precedent-chain sweep.

### Minors (log; address if cheap)

#### m1: Intro "Two distinct sub-modes" vs a body that now has three — internal prose tension (RSAD-1)
- **Issue**: The design kept the FBCD-1 intro "Two distinct sub-modes covering the temporal axis:" and added (c) as a third (scope-axis) sub-mode. No test breaks (`_names_both_sub_modes` asserts (a)/(b) presence only), and the framing is defensible — but a reader sees "Two … : (a) (b) (c)". Since this slice's point is catching count-literal drift, the dogfood value of an unambiguous lead-in is high.
- **Evidence**: `agents/critique.md:194` (intro) + `test_critique_agent.py:840` comment `# Two sub-modes (not three like RPCD-1)` the design already plans to update.
- **Proposed fix**: Tighten the lead-in to "Three sub-modes — two on the temporal axis ((a)/(b)) plus one on the orthogonal SCOPE axis ((c)):".
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"Sub-mode (c) content" lead-in + §"Self-application sweep" item 1 now specify the FBCD-1 intro is CHANGED to "Three sub-modes — two on the temporal axis ((a)/(b)) plus one on the orthogonal SCOPE axis ((c)):" (no literal "two" left above three bullets).

#### m2: design.md cites PTFFD-1 as the gate that would flag a missed row-#75 repoint — confirm the gate scope
- **Issue**: Correct belt-and-suspenders citation — after the rename, row #75 referencing `_at_v_0_82_0` would point to a now-absent function in a present file → `shippability_path_audit` (PTFFD-1) emits `missing-test-function` at /validate-slice Step 5.5. Claim verified; logged to confirm the Builder relies on the primary SCPD-1 same-block propagation, with PTFFD-1 as backstop (not the primary mechanism).
- **Evidence**: `agents/critique.md:202-205` (PTFFD-1 function-level layer); design.md obligation 4.
- **Builder draft**: **ACCEPTED-FIXED** — claim verified correct; no change required (the design already enumerates the row-#75 repoint as obligation 4 with PTFFD-1 noted as the backstop, not the primary mechanism). Logged for traceability.

#### m-add-1 (added by /critique-review meta-Critic, EXTEND): second stale "not three like RPCD-1" count-claim at `test_critique_agent.py:L902` not enumerated by the slice's RSAD-1 sweep
- **Issue**: Two stale "not three like RPCD-1" sites exist in `test_critique_agent.py` — the L840 comment (the design's sweep item 2 caught it) AND the `_names_both_sub_modes` docstring clause at L901-902 (missed). Once sub-mode (c) ships, FBCD-1 HAS three sub-modes, so "not three" at L902 is a false count-claim — the exact FBCD-1 sub-mode (c) fan-out class this slice ships to catch, left in its own diff.
- **Evidence**: `tests/methodology/test_critique_agent.py:840` (comment, enumerated) + L901-902 (docstring clause, missed); the design's own `grep "not three"` recipe would surface both; no test asserts the docstring text as a pinned string (grep-confirmed) → safe to edit.
- **Builder draft**: **ACCEPTED-FIXED** — design §"Self-application sweep" item 2 extended to update BOTH L840 + L902; mission-brief must-not-defer RSAD-1 bullet harmonized to name both sites.

## Dimensions checked
- [x] Unfounded assumptions — M2 (the "4 leg literals" framing undercounts the 12 `0.82.0` literals + omits the `0.81.0` predecessor line). The AP-10 rename fan-out was otherwise verified TRUE (not under-enumerated).
- [x] Missing edge cases — none. No load/network/concurrency/permission surface; only deterministic gate failures. R-28/AP-22 parallel-forward-sync checked: `git worktree list` shows only master + this slice's worktree — no sibling mid-bump slice.
- [x] Over-engineering — none. Versioned-refinement (FBCD-1 v1.1, no new `-D` rule-ID/dimension/ADR/build-check tool) is the minimal vehicle; matches CCC-1 v1.1.
- [x] Under-engineering — M1 (entry-pin substantive-content phrase unspecified). All 5 ACs otherwise have TF-1 rows; the two non-pytest ACs are correctly rowed per the slice-090 lesson; the regression-test name is genuinely unused (WRITTEN-FAILING-genuine).
- [x] Contract gaps — none. No endpoints/events/integrations; zero-row WIRE-1 matrix verified (no new modules).
- [x] Security — none. No auth/input/secret/injection/IDOR surface.
- [x] Drift from vault — none blocking. No ADR contradiction (versioned refinement of ADR-022, append-only respected). MEPD-1 rule-path verified: `test_each_changelog_entry_carries_rule_reference` (L127) needs only the `Rule reference` substring, satisfied by the planned line. Strategic-direction fit: this slice IS the calibration trajectory output (AP-21) and mitigates R-28's blast (AP-22) by bumping while no sibling slice is mid-bump.
- [x] Web-known issues — no applicable external technology (in-repo prose + tests + version literals). WebSearch not run (no external choice to validate).
- [x] Cross-cutting conformance — focus dimension, executed against the worktree: AP-10 rename fan-out enumerates exactly the real citations (shippability:84 row #75 ×2 + test def L5496) — NOT under-enumerated; `_lists_twelve_sub_clauses` counts sub-CLAUSES (12, unmoved by a sub-MODE; FBCD-1 is the 10th); body-bound tests scope FBCD-1 via start/end anchors and tolerate (c)'s insertion; sub-mode (c)'s `== N`/`len(...) == N` example literals are NOT BC-PROJ positive anchors (no self-application BC-1 trigger); SCPD-1 — the rename's only consumer is row #75, proactively repointed in-block; `_names_both_sub_modes` deliberately NOT renamed (avoids a fresh SCPD-1 obligation).

## Triage

**Triaged by**: user
**Date**: 2026-06-03
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | entry-pin now asserts substantive phrase `Counted-set cardinality fan-out` + `FBCD-1 (v1.1)` + `Rule reference` (design §What's new / §Components / §Tests touched); meta-Critic confirmed the phrase is unique repo-wide |
| M2 | Major | ACCEPTED-FIXED | grep-verified 12-literal + `0.81.0→0.82.0` predecessor-line + precedent-chain `108` sweep propagated to all 6 sites; meta-Critic re-verified "12" is the true `0.82.0` count |
| m1 | Minor | ACCEPTED-FIXED | FBCD-1 intro changed to "Three sub-modes — two temporal ((a)/(b)) + one scope ((c)):" across design §Sub-mode (c) content + §Self-application sweep |
| m2 | Minor | ACCEPTED-FIXED | PTFFD-1 backstop citation verified correct; no change required (logged) |
| m-add-1 | Minor | ACCEPTED-FIXED | self-application sweep extended to the L902 docstring "not three" claim + mission-brief must-not-defer harmonized |
