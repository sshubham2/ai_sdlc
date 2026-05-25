# Validation: Slice 037 extend-ptfcd-1-to-test-function-level

**Date**: 2026-05-17
**Result**: PASS (pre-finish; /validate-slice will reality-check per-AC)

Per-AC verification with evidence. All five acceptance criteria PASS.

| AC | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 1 | `test_first_audit.py --strict-pre-finish` emits `missing-test-function` (file exists, fn absent); function-column-first → `::`-tail fallback (M3); prose/non-identifier degrades to FILE-level-only (B2) | PASS | `test_ptffd1_test_first_audit.py` 8/8 pass: phantom→violation, present→clean, sentinel/prose→degrade, path-column-selector fallback (M3), unparseable→no-violation, skip-note renders (M2), async/nested resolve True (m2). Smoke: crafted fixture → exit 1 + `missing-test-function`. |
| 2 | `shippability_path_audit.py` emits `missing-test-function` for `::`-selector phantom; legacy file-phantom keeps `kind="missing-test-file"` + `to_dict()` key-superset (m1) | PASS | `test_ptffd1_shippability_path_audit.py` 4/4 pass incl. class::method terminal resolution + legacy-kind/key-superset pin. |
| 3 | Zero false positives on the live catalog + the real prose corpus (incl. slice-034's `(full existing module — non-regression)`) | PASS | `test_ptffd1_no_false_positive.py` 3/3 pass; live `shippability_path_audit architecture/shippability.md` clean: 37 rows / 238 tokens, all files AND functions exist; corpus-validated discriminator rejects all real prose. |
| 4 | `agents/critique.md` Dim 9 refined N=2→N=3 + function-level layer (content-pinned, not byte-equality alone — M-add-1); CAD-1 clean | PASS | `test_critique_dim_9_phantom_citation_function_level_layer_present` + `_names_ptffd_1_rule_id` pass; CAD-1 audit clean (in-repo ≡ installed, EOL-agnostic). |
| 5 | `methodology-changelog.md` v0.50.0 + PTFFD-1 + entry-pin + shippability row 37 (SCPD-1) + 4-part PMI-1 atomic bump; PMI-1/INST-1 clean | PASS | `test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed` + `_shippability_consumer_propagation` pass; PMI-1 clean @ 0.50.0; INST-1 16/16; VERSION=plugin.yaml=ai-sdlc-VERSION=0.50.0; changelog forward-sync byte-equal. |

## Audit battery (pre-finish gate)

TF-1 (19/19 PASSING) · BRANCH-1 · UTF8-STDOUT-1 (22 tools) · CRP-1 · PCA-1 (8 skills) · BCI-1 · PMI-1 (0.50.0) · BC-1 · WIRE-1 · LINT-MOCK-1 · INST-1 · critique_review · triage (CLEAN) · SCMD-1 decoupling — **all clean**. Full suite: **682 passed, 0 failed**.

## Recursive self-application (slice-022 law) — closed at three layers

1. **B1 / TF-1-plan layer**: own AC4 phantom test-fn — caught at /critique, fixed; own brief now TF-1 19/19 PASSING under its own live function-level audit.
2. **M-add-2 / catalog layer**: own shippability row 37 — function-level audit clean on its own catalog (37 rows / 238 tokens).
3. **SCMD-1 / incidental-coupling layer**: row 37 nearly cited an archive-corpus-coupled test — caught by the pre-finish SCMD-1 decoupling gate (NOT the Critic stack), fixed in-gate. The BC-PROJ-4 / SCMD-1 real-artifact backstop did its job exactly per the project's strongest standing lesson.

## /validate-slice run (real-environment evidence)

**Date**: 2026-05-17 · **Aggregate result**: PASS

- **Per-AC (AC1–AC5)**: 19/19 PTFFD-1 tests PASS (fresh re-run) — real command execution against real repo artifacts (the operative environment for an in-house tooling slice; no device/UI surface).
- **VAL-1 layered safety**: clean — 0 secrets, 0 hallucinated imports, 0 suppressed (`--imports-allowlist tests`).
- **WS-1 / ETC-1**: not enabled (brief sets Walking-skeleton / Exploratory-charter false) — audits correctly default-off.
- **Step 5.5 pre-catalog gates**: SCMD-1 decoupling clean (37 rows, 390 cited fns, incidental=0); PTFCD-1/PTFFD-1 path audit clean (37 rows, 238 tokens, all files AND functions exist).
- **Step 5.5 shippability catalog regression**: **37 rows, 37 PASS, 0 FAIL** (35s, under the 2-min target). No past slice broken by slice-037; row 37 (this slice's own new row) passes under its own newly-live function-level audit (second-order self-application clean at the catalog-execution layer too).

## Multi-instance validation
**Required?**: no (in-house audit tooling — no multi-user/device/account surface)
**Result**: not-applicable

## Reality surprises
- None unpredicted. The one in-gate failure (SCMD-1 incidental-coupling on row 37) was a *predicted* class — the slice-029/R-4 lesson + slice-022 self-violation law named it in advance; the pre-finish SCMD-1 backstop caught it exactly as designed.

## Failure classification

One failure surfaced + resolved during the pre-finish gate (SCMD-1 incidental-coupling on row 37). Classification: **implementation bug** (catalog-row citation depended on gitignored state) — not a spec gap (SCMD-1 is an existing, correct invariant) and not a reality surprise (the slice-029/R-4 lesson predicted exactly this class). Fixed in-round; no deferral. No open FAIL/PARTIAL — aggregate Result: PASS.
