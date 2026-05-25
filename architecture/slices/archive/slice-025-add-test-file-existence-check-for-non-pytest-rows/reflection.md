# Reflection: Slice 025 add-test-file-existence-check-for-non-pytest-rows

**Date**: 2026-05-16
**Shipped**: YES

## Validated

- **PTFCD-1 codified across 3 surfaces** — validated: `agents/critique.md` Dim 9 11th sub-clause present + location-pinned + names-both-sub-modes + cites-slice-023/024 (5 prose-pin tests PASS); `tools/test_first_audit.py` strict-only `missing-test-path-file` loop; new `tools/shippability_path_audit.py`. CAD-1 byte-equal (sha256 `51041c07`).
- **PASSING-gate prevents the M1 double-flag** — validated by `test_pending_row_missing_file_emits_exactly_one_violation`: a still-PENDING missing-file row under `--strict-pre-finish` emits exactly one violation (`non-passing-pre-finish`), never doubled.
- **M2 token predicate excludes non-test tokens** — validated against the REAL catalog: `shippability_path_audit` scanned 25 rows / 192 `tests/<…>.py` tokens with zero interpreter-path / `-m` / `-q` false-positives.
- **Recursive-self-application closure at 4 layers** — (1) /critique B1 = predicted FBCD-1 sub-mode (a) `PTFC-1`↔`PTFCD-1` rule-ID drift; (2) /build-slice TPHD-1 sub-mode (c) pre-flight caught a phantom test-FUNCTION citation in the slice's own TF-1 plan; (3) PTFCD-1 sub-mode (a) ran on slice-025's own brief at strict-pre-finish and passed (16/16 PASSING rows' Test paths exist); (4) `shippability_path_audit` ran on the catalog including the slice's own row 25 and passed. AC5 confirmed.
- **AC1–AC5 + shippability** — full methodology suite 522 PASS / 0 FAIL; catalog 25/25 PASS (0 regression); VAL-1 clean.

## Corrected

- **mission-brief.md rule ID `PTFC-1` → `PTFCD-1`** (B1, /critique time) — replace_all across all 4 slice files; zero non-D residue. No ADR supersession (ADR-023 correct as authored).
- **mission-brief.md TF-1 plan AC3 phantom test-FUNCTION citation** → `test_critique_agent_byte_equal_in_repo_vs_installed` does not exist; corrected to the real `test_in_repo_and_installed_critique_agent_are_content_equal`; AC3 expanded to the 5-fn sibling convention + `_lists_eleven` supersession row. Caught at /build-slice TPHD-1 sub-mode (c) pre-flight (build-log DEVIATION event), NOT by /critique.
- **design.md** — PASSING-gate predicate pinned (M1), token predicate pinned (M2), +3 component entries (B2/M3), `_EMPTY_SENTINELS` reference (m1), `::`-split scoping (m2). All at /critique TRI-1; this slice's design.md is the source of truth for what shipped.
- **`critique-review.md` First-Critic-verdict field** → must be the bare token `CLEAN` (no parenthetical) per `critique_review_audit`'s parser; corrected during AC4-DR-1 remediation.

## Discovered

- **Mandatory `/critique-review` was silently skippable and only caught at /validate-slice** — the pipeline ran `/critique → /build-slice → /validate-slice`, skipping `/critique-review` (mandatory in Standard mode for in-house-methodology surfaces per CLAUDE.md, slice-010). It was caught ONLY because this slice's AC4 happened to bake "DR-1 audits clean" as an acceptance criterion; `critique_review_audit` refused on the absent `critique-review.md`. Without AC4 naming DR-1, the skip would have shipped unnoticed. Impact: this is a pipeline-orchestration gap, not a project risk — NOT added to `risk-register.md` (consistent with how slice-024 classified PTFCD-1's own origin as developer-process calibration). Strong slice-026 candidate: enforce the dual-review prerequisite structurally rather than relying on per-slice AC authorship.
- **Function-level phantom-test citation is now N=1** — PTFCD-1 (this slice) explicitly scoped function-level (`::fn`) resolution OUT (N=0 at design time). The slice's OWN TF-1 plan then committed exactly a function-level phantom citation (AC3), caught only by TPHD-1 pre-flight luck. N=0 → **N=1 witnessed, with the slice's Out-of-scope section having foreshadowed the recurrence site** — per the project's "promote at N=2 when foreshadowed" convention this is promotion-eligible at the next recurrence.
- **`critique_review_audit` First-Critic-verdict parser is strict-token** — no parenthetical detail allowed in the `**First-Critic verdict**:` field. Minor authoring constraint; cost one re-run.

## Deferred

- **Function-level (`::fn`) test-function existence resolution** — explicitly out of scope (PTFCD-1 is file-level; N=0 at design, now N=1). Lands in: backlog / a future PTFCD-1-or-TPHD-1 extension slice at N=2.
- **`/critic-calibrate` retrospective ratification of PTFCD-1** — the v0.39.0 changelog entry notes a future `/critic-calibrate` run should ratify PTFCD-1 effectiveness against slices 25–35 first-Critic-MISS counts. Lands in: scheduled `/critic-calibrate` window run.
- **v2 `tools/ptfcd_1_audit.py`** — N/A: unlike FBCD-1 (prose-only, audit deferred), PTFCD-1 is already audit-gated by two `tools/*_audit.py` surfaces. No deferred audit.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (all 7 ACCEPTED-FIXED) + reality observed at build/validate + the meta-Critic (ACCEPT):

- **B1** (rule-ID drift `PTFC-1`/`PTFCD-1`): **VALIDATED** — ACCEPTED-FIXED; the drift was real and was the *predicted* FBCD-1 sub-mode (a) recursive-self-application catch. Meta-Critic confirmed zero non-D residue in shipped code.
- **B2** (PMI-1/INST-1 edits unenumerated): **VALIDATED** — ACCEPTED-FIXED; pre-finish PMI-1/INST-1 passed only because the registration was added; AC4 would have failed otherwise.
- **M1** (existence-loop predicate unpinned): **VALIDATED** — ACCEPTED-FIXED; the PASSING-gate is load-bearing; the regression test proves the double-flag the Critic predicted.
- **M2** (`\S+\.py` over-broad): **VALIDATED** — ACCEPTED-FIXED; real-catalog run (192 tokens, 0 false-positive) confirms the scoped predicate was necessary.
- **M3** (Step 5.5 wiring + row 25 unenumerated): **VALIDATED** — ACCEPTED-FIXED; unwired tool would have been a slice-018-class dead module.
- **m1** (`_EMPTY_SENTINELS` restated): **VALIDATED** — ACCEPTED-FIXED.
- **m2** (`::`-split over-specifies TF-1): **VALIDATED** — ACCEPTED-FIXED.

**Missed by Critic**: (1) The first Critic did NOT flag the **phantom test-FUNCTION citation in the slice's own TF-1 plan** (AC3, `test_critique_agent_byte_equal_in_repo_vs_installed`) — ironically the exact phantom-citation class this slice codifies, in the slice's own brief, at function granularity. It checked TF-1 *paths* (path-lock table) but not *function names* against the actual test files. Caught by TPHD-1 sub-mode (c) pre-flight at /build-slice, not /critique. (2) Neither first-Critic nor meta-Critic could catch the **/critique-review-was-skipped** process gap — structurally outside design-review scope; only /validate-slice's DR-1 audit reaches it. Both are execution-reachable, not static-design-reachable — consistent with the project's standing lesson that the static Critic stack cannot reach execution-reachable classes (the very thesis PTFCD-1 codifies).

**Pattern**: a slice codifying a *-citation discipline committed both a rule-ID drift AND a function-level phantom citation in its own artifacts — recursive-self-application at maximal depth for an audit-gated (not prose-only) -D discipline (4 layers, incl. /build-slice pre-flight + /validate-slice self-application). The Critic-stack's blind spots cluster at exactly the execution-reachable boundary PTFCD-1 targets — the first Critic is strong on static cross-file consistency (predicted its own B1) but cannot stat function names or detect skipped pipeline steps. Meta-Critic ACCEPT was well-calibrated: 0 suspicious / 0 missed / 0 severity, and it independently re-verified the ≥7-site SCPD-1 sweep + 4 FBCD-1 end_anchor tightenings left no stale sibling (FBCD-1 sub-mode (b) on the Builder's own fix-block — clean). Meta-Critic's lone sub-Minor (changelog line citing "rows 14/19/21/23/24/32") was assessed and is NOT a defect: those six ARE the propagation sites; row 25 was authored fresh with `_lists_eleven`, not propagated.

## Lessons for next slice

- **In Standard mode, `/critique-review` is mandatory for methodology-surface slices and must run between `/critique` and `/build-slice` — enforce it structurally, don't rely on per-slice AC authorship.** It was caught here only by coincidence (AC4 named DR-1). Strong slice-026 candidate: a `/build-slice` or `/validate-slice` prerequisite-check that refuses when Standard-mode + mandatory-Critic + `critique-review.md` absent + no documented skip rationale.
- **Codification slices that codify a citation/consistency discipline should stat their OWN TF-1 plan test-FUNCTION names (not just file paths) at /design-slice.** PTFCD-1 is file-level; the function-level sibling slipped here (N=1, foreshadowed in this slice's Out-of-scope). Promote a function-level extension at N=2.
- **Recursive-self-application closure for an audit-GATED -D discipline reaches deeper than prose-only ones** (4 layers incl. /build-slice TPHD-1 pre-flight + /validate-slice self-application). Budget validation + pre-flight attention accordingly.
- **`critique_review_audit` requires a bare-token `First-Critic verdict`** — put detail in a separate parenthetical line.

## Vault updates made (thin vault — small list)

- This slice's [[design.md]] — corrected at /critique (M1 PASSING-gate, M2 predicate, B2/M3 component entries, m1/m2); build-log records the /build-slice TPHD-1 DEVIATION.
- This slice's [[mission-brief.md]] — B1 rule-ID rename + AC3 TF-1 phantom-fn correction + status flips.
- [[architecture/shippability.md]] — row 25 added at /build-slice Phase 9 (per the slice's own RPCD-1/SCPD-1 must-not-defer — codification slices bundle the catalog row at build time so AC5 self-application can run; /reflect Step 5.3 therefore already satisfied, no duplicate added) + SCPD-1 propagation of 6 `_lists_ten`→`_lists_eleven` consumer tokens.
- [[methodology-changelog.md]] — v0.39.0 entry (+ installed byte-equal); [[architecture/decisions/ADR-023-ptfcd-1-phantom-test-file-citation-discipline]] authored.
- `risk-register.md` — **no change** (the /critique-review-skip discovery is developer-process calibration, not a project risk, consistent with slice-024's classification of PTFCD-1's own origin).
