# Reflection: Slice 037 extend-ptfcd-1-to-test-function-level

**Date**: 2026-05-17
**Shipped**: YES

## Validated
- Function-level phantom-test-citation IS reachable and IS a real Critic-stack blind spot — design claim confirmed: the slice's OWN AC4 row carried a phantom test function (`test_critique_agent_in_repo_equals_installed`), proving the class is live, not theoretical (B1, exactly the N=3 evidence base slice-025/026/027).
- The strict-identifier discriminator (B2) holds against the real adversarial corpus — empirically validated: rejects slice-034's real `(full existing module — non-regression)` row + all harvested archived prose, accepts every real identifier incl. `test_x[param]`. Zero false-accept/false-reject (meta-Critic ran it live; corpus test passes).
- Tri-state skip-with-note (ADR-037) works: unparseable cited file → no violation + visible note; verified by `test_unparseable_file_emits_skip_note_in_human_output`.
- `tools/_pyfn.py` (leading-underscore, no `main()`) is structurally exempt from UTF8-STDOUT-1 / INST-1 / PMI-1 — validated: UTF8-STDOUT-1 still 22 tools, PMI-1 clean @ 0.50.0, no consumer-propagation sentinel update needed (first Critic + meta-Critic claim confirmed at build).
- Shippability catalog 37/37 PASS, 0 regressions — slice-037 broke no past slice.

## Corrected
- Spec said new tests live at `tests/tools/test_ptffd1_*.py`; reality: `tests/tools/` does not exist (repo convention is `tests/methodology/`). Corrected in mission-brief TF-1 plan + design.md WIRE-1 + row-37 in the same fix block (TPHD-1). build-log Events + Design deviations note the deviation. (This was a plan-mode catch — exactly the slice-027-B1 phantom-path-convention class.)
- Row 37's first Machine-cmd cited `test_slice034_prose_test_function_is_not_false_positive`, which reads the gitignored archive corpus → SCMD-1 incidental-coupling. Corrected in-gate: archive-coupled selector removed from row 37 (the test still exists/runs in the suite — SCMD-1 forbids only the *catalog-row citation*, the slice-029/R-4 lesson). No ADR/risk change — SCMD-1 is the existing correct invariant; this was the slice obeying it.

## Discovered
- **Second-order recursive self-application is real and the catalog layer is a distinct surface.** B1 was the TF-1-plan self-application; M-add-2 surfaced the catalog-layer recurrence (row 37's own selectors must resolve under the slice's own newly-live function-level audit); the SCMD-1 in-gate catch was a *third* layer (incidental-coupling). Impact: any future slice that adds a NEW audit AND a shippability row for it must verify the row under the new audit AND check the cited tests aren't environment-coupled — both, not either. Not a new risk-register entry (PTFFD-1 + SCMD-1 + the build-ordering constraint now cover it), but a strong lesson.
- **The `AuditResult` JSON-contract extension was a genuine first-Critic blind spot symmetric to its own m1** (meta-Critic m-add-1) — adding a dataclass field silently extends `--json`. Generalizes: any audit-tool slice adding a result field must declare the `to_dict()` additive delta. Already covered by the m1/m-add-1 pattern; worth a lesson, not a risk.

## Deferred
- R-8 (shippability Step-5.5 runner per-`;`-segment-backtick contract unpinned) — explicitly out of scope; remains the strongest open standing candidate (slice candidate #2 from /slice). Lands in: next slice or backlog.
- R-6 (BRANCH-1 numeric-NNN regex rejects letter-suffixed split folders) — open, low band, untouched. Lands in: backlog until a split slice needs it.
- R-2 (no programmatic test for /diagnose cwd-mismatch warning) — open, low band, untouched.
- AC3 archive-corpus tests (`test_slice034_prose_*`, `test_archived_corpus_prose_*`) remain in the suite for B2 corpus coverage but are deliberately NOT catalog-cited (SCMD-1). Not deferred work — a permanent design property.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (all 12 ACCEPTED-FIXED, user-ratified) + reality at build/validate:

- B1 (own AC4 phantom test-fn): **VALIDATED** — ACCEPTED-FIXED; the phantom was real (`test_critique_agent_drift.py:62` proved the correct name); had it shipped, the slice's own Step-6 TF-1 strict-pre-finish would have refused. The recursive self-violation the project's slice-022 law predicts (N≈11).
- B2 (prose `test_function` false-positive): **VALIDATED** — ACCEPTED-FIXED; reality (live corpus run) confirmed slice-034's prose row would have false-positived without the discriminator.
- B3 (`-D` vs `vN.N` rule-ID convention): **VALIDATED** — ACCEPTED-FIXED; the changelog/ADR-023/TFFL-1 precedent independently confirmed PTFFD-1 (not `PTFCD-1 v1.1`) is correct.
- M1 (SCPD-1 catalog propagation): **VALIDATED** — ACCEPTED-FIXED; row 37 + propagation entry-pin are real obligations (CLAUDE.md vault discipline).
- M2 (ADR-037 observability undelivered): **VALIDATED** — ACCEPTED-FIXED; the skip-note now renders + is tested.
- M3 (`_resolve_test_path` `::`-strip escape): **VALIDATED** — ACCEPTED-FIXED; `test_path_column_selector_used_when_function_column_empty` proves the escape was real and the fallback closes it.
- m1 (`PhantomCitation.kind` legacy default unpinned): **VALIDATED** — ACCEPTED-FIXED; legacy-direction pin passes.
- m2 (async/nested thinly tested): **VALIDATED** — ACCEPTED-FIXED; async+nested test passes.
- M-add-1 (AC4 tautological green) [meta-Critic]: **VALIDATED** — ACCEPTED-FIXED; verified the cited CAD-1 test is pure byte-equality (`test_critique_agent_drift.py:62-81`); content-pin tests now make AC4 actually verify the Dim 9 refinement.
- M-add-2 (row 37 under-spec + second-order self-application) [meta-Critic]: **VALIDATED** — ACCEPTED-FIXED; the build-ordering constraint was load-bearing — building row 37 last let its selectors resolve under the live function-level audit (37 rows / 238 tokens clean).
- m-add-1 (`AuditResult.to_dict()` undeclared extension) [meta-Critic]: **VALIDATED** — ACCEPTED-FIXED.
- m-add-2 (both-columns-disagree unstated) [meta-Critic]: **VALIDATED** — ACCEPTED-FIXED.

**Missed by Critic**: TWO, both caught by non-Critic backstops exactly as the project's strongest standing lesson (`_index.md:54-55`) predicts:
1. The `tests/tools/` → `tests/methodology/` phantom-path-convention error (slice-027-B1 class) — missed by BOTH Critic layers AND the meta-Critic (which read the spec but did not stat the directory); caught only at `/build-slice` plan-mode (the slice-032 "plan-mode is a load-bearing backstop for what the dual-Critic stack rubber-stamps" pattern, now confirmed again).
2. The row-37 SCMD-1 incidental-coupling (archive-corpus-reading test cited in a catalog Machine-cmd) — missed by both Critic layers AND not surfaced by M-add-2's row-37 analysis (which focused on function-level resolution, not gitignored-state coupling); caught only by the pre-finish SCMD-1 decoupling gate (BC-PROJ-4-class real-artifact backstop).

**Pattern**: The dual-Critic stack achieved 12/12 VALIDATED with zero FALSE-ALARM (high precision again on a methodology-codification slice), but its TWO standing structural blind spots both fired and were both caught by the non-Critic backstops the project already relies on: plan-mode artifact-reading (phantom-path) and the SCMD-1/BC-PROJ-4 pre-finish real-artifact run (incidental-coupling). The slice-022 self-violation law held at maximal depth — a slice codifying *phantom-citation* detection committed a phantom path-convention citation AND nearly shipped a catalog row coupled to gitignored state. Confirms: for audit-codification slices, budget plan-mode + the pre-finish real-artifact gates as first-class verification layers, NOT the Critic stack, for the audit-vs-its-own-artifact interaction.

## Lessons for next slice
- **Audit-codification slices recursively self-apply at THREE layers, not two: the TF-1-plan layer (B1), the shippability-catalog-row layer (M-add-2), and the catalog-row-incidental-coupling layer (SCMD-1).** Pre-budget all three; the third (gitignored-state coupling in the new audit's own catalog row) is the deepest and is reachable ONLY by the pre-finish SCMD-1/BC-PROJ-4 real-artifact run, never the Critic stack. (slice-037)
- **Plan-mode directory-existence check is a load-bearing backstop the dual-Critic stack (incl. meta-Critic) does not reach.** Both Critic layers read the spec's `tests/tools/` citations and neither stat'd the directory; plan-mode caught it in one read. For any slice citing new test paths, the FIRST plan-mode action should be `ls`/stat of the cited directories. (slice-037, confirming slice-032/027-B1)
- **A `-D`-rule refinement mints a NEW `-D` ID (PTFFD-1←PTFCD-1), never a `vN.N` label** — the `vN.N` label is exclusively the NON-`-D` audit-gate naming class. TFFL-1↔TF-1 is the governing precedent; ADR-038 now records it for the `-D` family. Next `-D` refinement: mint, don't version. (slice-037)
- **An AC verified only by a byte-equality / drift audit is a tautological green** — the meta-Critic's sharpest catch (M-add-1). Any AC whose deliverable is *content* (prose, a sub-clause, a rule) needs a CONTENT pin, not just a CAD-1/forward-sync equality test. (slice-037)
- **The dual-Critic stack hit 12/12 VALIDATED / 0 FALSE-ALARM again on a codification slice** — its precision is not the problem; its two standing blind spots (audit-self-violation reachable only by real-artifact runs; phantom-path reachable only by plan-mode stat) are structural and the existing backstops cover them. Do not add Critic dimensions for these — the backstops are the right layer. (slice-037)

## Vault updates made (thin vault — small list)
- [[decisions/ADR-037]] — authored (unparseable→skip-with-note) + amended in-round (M2 observability delivered, M3 precedence, m-add-2 both-columns-disagree)
- [[decisions/ADR-038]] — authored (PTFFD-1 new `-D` ID refines PTFCD-1 in place, supersedes nothing)
- [[methodology-changelog.md]] — v0.50.0 PTFFD-1 entry (+ forward-synced installed copy; 4-part PMI-1 atomic bump 0.49.0→0.50.0)
- [[architecture/shippability.md]] — row 37 added at build (M-add-2 ordering required pre-finish); archive-coupled selector removed in-gate (SCMD-1)
- [[agents/critique.md]] — Dim 9 phantom-citation sub-clause refined N=2→N=3 + function-level layer + PTFFD-1 (+ forward-synced, CAD-1 clean)
- No risk-register change — R-8/R-6/R-2 remain open + untouched (deferred); no new risk (PTFFD-1 + SCMD-1 + build-ordering constraint codify everything discovered)
- Code is truth for the rest (`tools/_pyfn.py`, the two extended audits, the test files) — no component/contract vault files in Standard mode
