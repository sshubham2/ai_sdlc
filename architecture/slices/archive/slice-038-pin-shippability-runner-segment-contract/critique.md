# Critique: Slice 038 pin-shippability-runner-segment-contract

**Critic reviewed**: mission-brief.md, design.md, ADR-039
**Date**: 2026-05-17
**Result**: NEEDS-FIXES

## Summary

The core architectural decision is sound and the reuse claims verify cleanly against the real artifacts (`_segments()` L179-188, the `shippability_path_audit` import precedent L69-74, SKILL.md L213 prose, R-8 lineage). Two propagation blind spots the aggregated lessons warned about: (B1) the new `main()`-bearing tool breaks the UTF8-STDOUT-1 `discovered_set == covered_set` parity test — which IS shippability row #28, the slice's own dogfood row; (B2) the test-first plan omits the SCPD-1 consumer-propagation changelog test. Plus a tautological-pin Major (M1), a 3-part-vs-4-part PMI-1 Major (M2), and two Minors. Builder independently re-verified B1/B2/M2 against the artifacts (slice-032 "open the artifact" discipline) — B1/M2 fully confirmed; B2's prescription is sound though its evidence was over-generalized (see B2 Builder draft). All findings ACCEPTED-FIXED.

## Findings

### Blockers (must address before /build-slice)

#### B1: New `tools/shippability_runner.py` breaks UTF8-STDOUT-1 parity — and that test IS row #28, the slice's own dogfood row
- **Claim under review**: design.md §Recursion: "The runner is NOT an AST-citing audit … so the slice-037 three-layer recursive self-application hazard does not apply at full depth here." ADR-039 §Consequences lists propagation as PMI-1/INST-1/RPCD-1/SCPD-1 — UTF8-STDOUT-1 absent.
- **Issue**: `test_utf8_stdout_regression.py::_discovered_audit_tools()` (L278-289) auto-discovers every `tools/*.py` (non-`_`, non-`__init__`) with a top-level `main` AST node and asserts `discovered_set == covered_set` (L237/L387). The runner's `main()`/CLI surface (design.md, ADR-039) enters `discovered_set` automatically; it will NOT be in `covered_set` unless `_POSITIONAL_SLICE_TOOLS` (L81) gains the token AND a `_assert_no_encoding_error` call site is added (pattern L184-224). That parity test is segment 1 of shippability row #28 — the lone multi-segment row this slice exists to fix and dogfoods at its own Step 5.5. Slice-022 self-violation law / slice-031/033 BC-PROJ-4 pattern.
- **Evidence**: `test_utf8_stdout_regression.py` L81, L184-224, L278-289/L237/L387; `architecture/shippability.md:36` row #28 seg 1 = `test_utf8_stdout_regression.py`; design.md recursion note.
- **Proposed fix**: Add UTF8-STDOUT-1 propagation obligation to design.md + ADR-039; add `"tools.shippability_runner"` to `_POSITIONAL_SLICE_TOOLS` + a `test_shippability_runner_survives_cp1252_with_u2192` call site; add as a test-first row (AC4); rewrite the recursion note.
- **Builder draft**: ACCEPTED-FIXED — independently verified at `test_utf8_stdout_regression.py` L278-289 (`_discovered_audit_tools` globs all `tools/*.py` with top-level `main`) + L237 parity. Confirmed real slice-022 self-violation. Fixed: design.md §What's new (UTF8-STDOUT-1 propagation bullet) + §Recursion note rewritten; ADR-039 §Consequences; mission-brief TF-1 plan gains `test_utf8_stdout_regression.py::test_shippability_runner_survives_cp1252_with_u2192` (AC4). Runner takes a positional catalog path → `_POSITIONAL_SLICE_TOOLS`.

#### B2: Test-first plan omits the SCPD-1 `_shippability_consumer_propagation` changelog test
- **Claim under review**: mission-brief AC4 row: single test `test_new_runner_contract_ruleid_entry_present`. AC4 prose invokes SCPD-1 + "a shippability catalog row added".
- **Issue**: The slice-037 PTFFD-1 precedent pairs `test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed` (L2864) with `test_v_0_50_0_ptffd_1_shippability_consumer_propagation` (L2915-2941, asserts the rule token + consumer test filename present in `architecture/shippability.md`). AC4 invokes SCPD-1 but no test-first row enforces propagation; strict TF-1 would flag AC4's unenforced sub-claim.
- **Evidence**: `test_methodology_changelog.py` L2864-2941 (PTFFD-1 paired instance); mission-brief TF-1 plan (one AC4 row).
- **Proposed fix**: Add `test_v_0_51_0_srsc_1_shippability_consumer_propagation`; rename the first row to `test_v_0_51_0_srsc_1_entry_present_in_repo_and_installed`.
- **Builder draft**: ACCEPTED-FIXED — prescription adopted. **Evidence correction (Builder, slice-032 verify-the-artifact discipline)**: the Critic's "every prior RULE-ID slice has two changelog tests" is over-generalized — grep shows QD-1 (v0.46), EOL-DRIFT-1 (v0.47), TFFL-1 (v0.48), SRCD-1 (v0.49) have ONLY `_entry_present_in_repo_and_installed`; ONLY PTFFD-1 (v0.50/slice-037) has the pair. But the obligation still holds for SRSC-1 specifically: it has a shippability consumer (the runner consumed by Step 5.5) + adds a catalog row, and slice-037 is the most-recent governing precedent + AC4 explicitly invokes SCPD-1. Severity stays Blocker (unenforced AC4 propagation = the slice-034/036 under-raised RULE-ID/PMI-1 obligation class). Fixed: mission-brief TF-1 plan (paired SRSC-1 rows); design.md + ADR-039.

### Majors (address this slice)

#### M1: AC2/AC4 "entry present" pin risks tautological green — needs a content/anti-silent-weakening phrase pin
- **Claim under review**: AC4 test name `test_new_runner_contract_ruleid_entry_present`; AC4 prose "a new RULE-ID entry".
- **Issue**: slice-037 meta-Critic M-add-1: a content-bearing AC needs a CONTENT pin, not presence. Canonical precedent `test_v_0_50_0_ptffd_1_entry_present` (L2900-2904) asserts a specific anti-silent-weakening string. `"SRSC-1" in body` passes even if the entry's substance (reuse-of-`_segments()`, "do NOT hand-roll", per-segment-strip) is gutted.
- **Evidence**: `test_methodology_changelog.py` L2900-2912; mission-brief AC4 name; slice-037 aggregated lesson.
- **Proposed fix**: SRSC-1 `entry_present` test asserts a canonical anti-silent-weakening phrase in BOTH in-repo + installed bodies + ADR-039 lineage + "supersedes nothing"; AC3 SKILL.md test asserts the canonical-mechanism string present at Step 5.5, not merely that it changed.
- **Builder draft**: ACCEPTED-FIXED — directly aligned with the slice-037 meta-Critic lesson. Fixed: design.md §What's new specifies the `entry_present` test asserts literal phrases `do NOT hand-roll the execution loop` + `reuses SCMD-1 _segments()` + ADR-039 lineage + "supersedes nothing" (mirrors PTFFD-1 L2900-2912) in-repo AND installed; AC3 SKILL.md prose-pin is a content pin.

#### M2: PMI-1 atomic-bump scope stated as 3-part; the established precedent is 4-part
- **Claim under review**: ADR-039 / design.md: "`VERSION` + PMI-1 version bumped atomically".
- **Issue**: slice-035 B-add-1 (N≥3): PMI-1 atomic bump is 4-part — `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced installed changelog. The 3-part shorthand drops the installed `~/.claude/ai-sdlc-VERSION` leg.
- **Evidence**: slice-037 changelog v0.50.0 entry (canonical 4-part wording); `VERSION`=0.50.0, `~/.claude/ai-sdlc-VERSION`=0.50.0, `plugin.yaml:15`=0.50.0; slice-035 lesson.
- **Proposed fix**: State the 4-part bump explicitly (all 0.50.0→0.51.0); sequence installed-copy reconciliation before INST-1.
- **Builder draft**: ACCEPTED-FIXED — independently verified: `VERSION`=0.50.0, `~/.claude/ai-sdlc-VERSION`=0.50.0, `plugin.yaml:15`=0.50.0 (4-part confirmed). Fixed: design.md §What's new (explicit 4-part bullet) + ADR-039 §Consequences.

### Minors (log; address if cheap)

#### m1: Two non-identical enumeration surfaces for the new tool
- **Claim under review**: design.md "`plugin.yaml` + `tools/install_audit.py` enumerate the new tool atomically".
- **Issue**: `tools/install_audit.py` `_CANONICAL_TOOLS` (L77+, no `utf8_stdout_audit`) and `plugin.yaml` tools list (L91-127, includes `utf8_stdout_audit.py`) differ in membership; a `main()`-bearing tool goes in BOTH (not a `_`-helper). slice-006 inclusion-surface trap.
- **Evidence**: `tools/install_audit.py:77-95`; `plugin.yaml:91-127`.
- **Proposed fix**: Explicitly add to both surfaces; run both audits to exit 0.
- **Builder draft**: ACCEPTED-FIXED — design.md §What's new now names both surfaces explicitly + the not-a-`_`-helper note.

#### m2: Negative fixture (AC2) must be a contrast, not a call to the already-correct `_segments()`
- **Claim under review**: test-first row `test_naive_outer_strip_runner_is_rejected`; design.md "a naive outer-only-strip is demonstrably wrong".
- **Issue**: The runner reuses correct `_segments()` — no naive path inside it to assert-reject. The test must contrast an inline `_naive_outer_strip(cell)` (leaves leading backtick on seg 2 of real row #28) vs `_segments()` (does not). Calling `_segments()` and asserting correctness is tautological.
- **Evidence**: `shippability_decoupling_audit.py` L179-188; `risk-register.md:156` (R-8 mechanism); Must-not-defer "no tautological green".
- **Proposed fix**: Build an explicit local naive-strip fn; assert the contrast against real row #28 in one test.
- **Builder draft**: ACCEPTED-FIXED — design.md §What's new now specifies `test_naive_outer_strip_runner_is_rejected` as the explicit `_naive_outer_strip(cell)[1].startswith("\`")` is True vs `_segments(cell)[1].startswith("\`")` is False contrast.

## Dimensions checked
- [x] Unfounded assumptions — none; `_segments()` reuse, import precedent, SKILL.md L213 all verified against artifacts.
- [x] Missing edge cases — B1 (UTF8-STDOUT-1 auto-discovery), m2 (negative-fixture construction); empty-catalog/non-zero-segment covered.
- [x] Over-engineering — none; runner is minimal, reuses not re-derives, mirrors sibling conventions.
- [x] Under-engineering — B2 (SCPD-1 propagation test), M1 (presence vs content pin).
- [x] Contract gaps — exit-code contract fully specified; m1 (dual enumeration surface).
- [x] Security — none; local CLI, no auth/network/data-model/multi-user surface.
- [x] Drift from vault — none; ADR-039 correctly does NOT supersede SCMD-1/ADR-031; SRSC-1 correctly minted non-`-D` `vN.N`; M2 flags 3-vs-4-part PMI-1 scope drift.
- [x] Web-known issues — N/A; no external tech/API/platform surface.
- [x] Cross-cutting conformance — B1 (recursive self-application / slice-022 law), B2 (paired-changelog-test convention), M2 (4-part PMI-1 inventory).

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

Dual-review verdict: **ADJUST** (see critique-review.md). Meta-Critic confirmed B1/M1/M2/m1/m2 VALID at correct severity; reclassified B2 Blocker→**M3 (Major)** (obligation real + fix correct, but rests on N=1 precedent not an N≥3 invariant); added missed Minor **m-add-1** (stale "18 entries" count, actual 22 — FBCD-1 doc-drift, fixed). User ratified all Builder drafts 2026-05-17; B2 accepted as reclassified Major. All dispositions ACCEPTED-FIXED → mechanical verdict CLEAN.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Verified slice-022 self-violation (UTF8-STDOUT-1 parity = row #28 dogfood); design.md §What's new/§Recursion + ADR-039 + TF-1-plan fixed. Meta-Critic CONFIRMED Blocker. User-ratified. |
| B2 | Major (reclassified from Blocker per DR-1) | ACCEPTED-FIXED | Paired SCPD-1 changelog test added (mission-brief TF-1 + design.md + ADR-039). Meta-Critic SEVERITY-WRONG Blocker→Major (evidence-correction confirmed N=1 precedent, not "every prior"); disposition unchanged. User-ratified as Major. |
| M1 | Major    | ACCEPTED-FIXED | Content/anti-silent-weakening pin per slice-037 meta-Critic lesson. Meta-Critic CONFIRMED Major. User-ratified. |
| M2 | Major    | ACCEPTED-FIXED | 4-part PMI-1 verified (VERSION + ai-sdlc-VERSION + plugin.yaml:15 all 0.50.0). Meta-Critic CONFIRMED Major. User-ratified. |
| m1 | Minor    | ACCEPTED-FIXED | Both enumeration surfaces named. Meta-Critic CONFIRMED Minor. User-ratified. |
| m2 | Minor    | ACCEPTED-FIXED | Explicit naive-strip-vs-`_segments()` contrast + smoke-gate enforcement. Meta-Critic CONFIRMED Minor. User-ratified. |
| m-add-1 | Minor | ACCEPTED-FIXED | Meta-Critic MISSED-FINDING: design.md `_CANONICAL_TOOLS` "18 entries" stale (actual 22). design.md corrected to "22 → 23 after this slice" + grep-verify-at-build note. User-ratified. |
