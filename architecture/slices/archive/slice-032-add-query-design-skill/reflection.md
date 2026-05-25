# Reflection: Slice 032 add-query-design-skill

**Date**: 2026-05-17
**Shipped**: YES-WITH-DEFERRALS (slice ACs all PASS; pre-existing unrelated diagnose drift user-approved-deferred)

## Validated
- `/query-design` read-only / grounding / delegation contract — validated by `test_query_design_skill.py` (6 passed: readonly-invariant-loophole-free, grounding, delegation, 3 error-model clauses, no-pipeline-position-block) + byte-equal drift test.
- 4-part PMI-1 atomic bump — validated: `VERSION`==`~/.claude/ai-sdlc-VERSION`==`plugin.yaml.version`==`0.46.0`; `test_v_0_46_0_qd_1` + `test_version_matches_most_recent_changelog_entry` pass; both changelog surfaces carry the entry.
- Out-of-loop design (no `## Pipeline position` block) — validated by `test_no_pipeline_position_block` + PCA-1 audit clean (8 chain skills; `query-design` correctly neither audited nor parametrized).
- **Critic B2 prediction empirically confirmed**: the new `Path.home()`-reading drift test classifies SCMD-1-clean (decoupling audit: 32 rows, incidental=0) — no `_ALLOWLIST_SYMBOLS` edit needed, exactly as the B2 fix required verifying rather than assuming.

## Corrected
- **DEVIATION-1** (caught at `/build-slice` plan-mode design-is-wrong gate): design.md's original m1 disposition cited a *non-existent* "slice-029 no-rule-lineage precedent" for omitting a bespoke `test_v_0_46_0` pin. Reality: 24/24 changelog versions are pinned, slice-029/v0.43.0 included. design.md corrected (m1 reversed; 4-part PMI-1 bump enumerated; rule-ID-bearing 4-assertion pin spec; 2-site `_QD1_PHRASE` pin). Append-only history preserved (v1 critique.md untouched; v2 in `critique-v2.md`/`critique-review-v2.md`; build-log Events record it).
- install_audit `_CANONICAL_SKILLS` placement: design hint "after drift-check" was alphabetically wrong (`h<q<r`); corrected to "after heavy-architect" at build (INST-1 sorts both sides → functionally inert; recorded in build-log, not re-critiqued).
- `test_no_pipeline_position_block` initial bare-substring check false-positived on SKILL.md's own descriptive prose; corrected to heading-at-line-start detection.

## Discovered
- **R-5 N+2** (added to [[risk-register#R-5]]): the shippability catalog's in-repo↔installed drift tests (#1/#19 diagnose) FAIL on machine-local install staleness *independent of the slice under test* — concretely witnessed a 3rd time (slice-030A, -031, -032). Strongest standing non-feature deferred candidate: `fix-skill-drift-test-crlf-normalization`.
- **Naive catalog runner false-FAIL**: a Step-5.5 runner that does NOT implement SCMD-1's deterministic `;`-split mis-reports multi-segment Machine-cmd rows (row #28 false-FAILed under my ad-hoc runner; both segments PASS under correct `;`-split). Logged under R-5 — the CRLF-fix slice should also pin the runner's `;`-split contract.
- **Corrections are unguarded design surfaces**: the re-critique loop caught the DEVIATION-1 *correction* committing the very slice-022 self-violation it cited (v2 M1: "mirrors scmd_1" specified 2 of scmd_1's 4 assertions), and dual-review-v2 caught the fix re-introducing the single-site-coverage silent-drift class at N=2 (M-add-v2-1: `_QD1_PHRASE` obligated 3 sites, pinned 1). A design correction must go through the full adversarial loop — it is not a trusted edit.

## Deferred
- Pre-existing `skills/diagnose/SKILL.md` in-repo↔installed drift (catalog #1/#19) — reason: not a slice-032 regression (zero diagnose files touched), out of slice scope to fix — user-approved deferral 2026-05-17 — lands in: `fix-skill-drift-test-crlf-normalization` (R-5).
- R-5 environment-fragility hardening (drift tests skip/warn on environment-only staleness vs real code drift; pin Step-5.5 runner `;`-split) — lands in: chartered `fix-skill-drift-test-crlf-normalization` slice.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (v1) + `critique.md` `### Triage — v2 delta` + reality at build/validate:

**v1 findings**:
- B1 (SCMD-1 6-col grammar): VALIDATED — ACCEPTED-FIXED; the 6-cell row + prose-free Machine-cmd was required exactly as flagged (decoupling audit confirmed).
- B2 (Path.home decoupling classification): VALIDATED — ACCEPTED-FIXED; the "verify, don't assume" demand was right — empirical check at build confirmed clean (the assumption *could* have been wrong).
- B3 (AC4 slice-022 self-violation): VALIDATED — ACCEPTED-FIXED; the prose-pin is the deterministic gate that actually validated AC4. Non-deterministic dry-run would have been unverifiable at pre-finish exactly as predicted.
- M1 (INSTALL.md hard-count): VALIDATED — ACCEPTED-FIXED.
- M2 (allowed-tools): VALIDATED — ACCEPTED-FIXED (documented-decision); 0 skills use `allowed-tools`, decision held.
- M3 (PCA-1 by-analogy): VALIDATED — ACCEPTED-FIXED; PCA-1 clean, no-block confirmed by test.
- m1 (QD-1 prose-only, "no bespoke pin"): **OVERRIDE-MISJUDGED** — Builder ACCEPTED-FIXED with rationale "slice-029 no-rule-lineage precedent → no bespoke pin"; first Critic filed it Minor and the meta-Critic *explicitly confirmed* "declining a bespoke pin correctly avoids over-build". Reality (build-plan-mode): the cited precedent was **factually false** — 24/24 versions pinned, slice-029 included. The entire v1 Critic stack accepted a non-existent precedent without verifying it against `test_methodology_changelog.py`. Calibration signal for the **Critic** (verify precedent claims against the artifact) more than the user.
- m2 (ADR `supersedes: null`): FALSE-ALARM — user/Builder OVERRODE; reality confirmed ADR-031 uses the identical sentinel. Critic over-reached (correctly Minor).
- M-add-1 (INSTALL.md 3 sites not 1): VALIDATED — meta-Critic caught it; 3 sites confirmed and fixed.

**v2 (DEVIATION-1 re-critique) findings**: M1-v2, M2-v2, m1-v2, M-add-v2-1 — all VALIDATED (all real, all ACCEPTED-FIXED, all shipped clean; the loop's findings were each confirmed by the final passing tests).

**Missed by Critic**: the v1 first Critic **and** the v1 meta-Critic both missed that m1's "slice-029 no-rule-lineage precedent" was factually false (24/24 versions pinned). Caught only at `/build-slice` plan-mode by reading the actual enforcing test file. Two adversarial passes + dual-review confirmed a Builder rationale built on a non-existent precedent because neither Critic verified the precedent claim against the artifact.

**Pattern**: (1) `/build-slice` plan-mode is a load-bearing backstop for **false-precedent claims** the dual-Critic stack rubber-stamped — the "design is wrong" gate caught what 2 Critic passes + dual-review missed. (2) The slice-029 "pre-read the enforcing audit's actual assertion" lesson **recurred at the Critic layer** (not just Builder). (3) The single-site-coverage blind spot fired **N=2 within one slice** (v1 M-add-1 INSTALL 1-of-3 → v2 M-add-v2-1 phrase 1-of-3) — a strong `/critic-calibrate` candidate. (4) A design *correction* is itself an adversarial surface; routing DEVIATION-1 through full re-critique paid off twice.

## Lessons for next slice
- When a Builder disposition cites a prior-slice "precedent" (slice-NNN did/didn't do X), the Critic MUST verify the precedent against the actual enforcing artifact before confirming — accepting the claim is a dual-Critic-stack blind spot witnessed here at N=1 (strong `/critic-calibrate` input; pairs with the slice-029 "pre-read the enforcing audit" lesson now generalized to the Critic).
- A design correction discovered at build-plan-mode is a NEW design surface — route it through the full `/critique`+`/critique-review` loop. This slice did; v2 found the correction self-violated slice-022 and dual-review-v2 found the fix re-introduced silent-drift at N=2. Corrections are not trusted edits.
- The single-site-coverage silent-drift blind spot is now N=2-in-one-slice — when a fix introduces an N-site verbatim obligation, immediately ask "is every site test-pinned, or only the one I just touched?"
- `fix-skill-drift-test-crlf-normalization` (R-5) is overdue at N+2 and should also pin the Step-5.5 runner's SCMD-1 `;`-split contract.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-5 recurrence sub-entry (N+2, slice-032) + the catalog-runner `;`-split discovery.
- This slice's [[design.md]] — DEVIATION-1 corrections (m1 reversed; 4-part PMI-1 bump; 4-assertion pin spec; 2-site `_QD1_PHRASE`); build-log Events + Summary record the deviation.
- [[shippability.md]] — row #32 (added during /build-slice task 10 per the slice's own RPCD-1/SCPD-1 requirement; Step 5.3 satisfied, NOT duplicated here).
- No ADR superseded (ADR-032 stands as accepted; DEVIATION-1 refined its consequences, not its decision).
