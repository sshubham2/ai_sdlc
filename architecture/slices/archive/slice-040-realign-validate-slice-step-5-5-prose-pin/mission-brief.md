# Slice 040: realign-validate-slice-step-5-5-prose-pin

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-10 (top open risk, score 3, medium band) — slice-038 (SRSC-1) left a stale slice-031 SCMD-1 mini-CAD prose-pin
**Test-first**: false  (the failing repro test pre-exists — see Dependencies / BFRD-1 disposition below)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-038 (SRSC-1; [[ADR-039]]; methodology v0.51.0) rewrote `/validate-slice` Step 5.5
to **invoke** `tools.shippability_runner` (`skills/validate-slice/SKILL.md` L216),
replacing the exact slice-031 prose `"Run each entry's **Machine-cmd** column"`. The
mini-CAD prose-pin `test_step4_5_5_consumes_machine_stable_command` still asserts that
dead phrase, so it has been FAILing slice-innocently on master since slice-038 shipped
(rigorously slice-039-innocent — `git diff --quiet master --` clean for validate-slice
surface). This slice realigns the orphaned prose-pin to the SRSC-1 runner-invocation
wording that actually ships, retiring R-10 and returning `tests/methodology/` to green.

## Acceptance criteria

1. `tests/methodology/test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command` PASSES — its assertions pin the SRSC-1 runner-invocation prose actually present in `skills/validate-slice/SKILL.md` (not the dead slice-031 phrase).
2. The realigned test still enforces the load-bearing invariant non-tautologically: it FAILS if Step 5.5 prose regresses to the pre-SRSC-1 wording (prose `Command` column / hand-rolled execution loop). Proven by a deliberate temporary revert during validation.
3. The realigned test's docstring documents the slice-031 SCMD-1 B2-v1 → SRSC-1 supersession lineage, so a future reader does not re-mistake the new pin as the old dead one (the SCPD-1 / mini-CAD-propagation class applied to `test_*_skill.py` prose-pins).
4. The full `tests/methodology/` suite is green on the slice branch with no remaining slice-038-rooted false-FAIL.
5. R-10 marked `retired` in `architecture/risk-register.md` via a `**Retired**:` line mirroring the R-9 L170 conformance-fix form (with verification evidence + the N=1 `/critic-calibrate` watch-list note). Per the verified slice-036/R-9 precedent this is a no-VERSION-bump conformance fix that adds **no** `methodology-changelog.md` entry and **no** ADR. RR-1 + PMI-1 + META-1 + CAD-1 audits clean.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Realigned pin passes | `$PY -m pytest tests/methodology/test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command -q` → 1 passed |
| 2 | Non-tautological | Temporarily revert Step 5.5 prose to a pre-SRSC-1 phrase in a scratch copy / monkeypatched `VALIDATE`, re-run the test, observe it FAILS; restore. Document the revert proof in `validation.md`. |
| 3 | Lineage documented | Read the test docstring — names slice-031 SCMD-1 B2-v1 as superseded-by SRSC-1 ([[ADR-039]]) with the reason the pinned phrase changed |
| 4 | Suite green | `$PY -m pytest tests/methodology/ -q` → 0 failed |
| 5 | Audits + vault | `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` shows R-10 absent from open set; `$PY -m tools.plugin_manifest_audit` clean; `$PY -m pytest tests/methodology/test_methodology_changelog.py -q` (META-1) clean — confirms NO changelog entry was needed; `$PY -m tools.critique_agent_drift_audit --repo-root .` clean; `/drift-check` clean |

## Must-not-defer

- [ ] The realigned assertion MUST stay non-tautological — it must still FAIL on a pre-SRSC-1 Step 5.5 regression (prove via deliberate revert, AC2). A pin weakened to always-true defeats R-10's whole point.
- [ ] Supersession lineage (slice-031 SCMD-1 B2-v1 → SRSC-1 / [[ADR-039]]) documented in the test docstring so the realignment is auditable, not silent.
- [ ] `architecture/risk-register.md` R-10 → `retired` lands in the same fix block as the test realignment — do NOT leave R-10 open after the fix (this is itself the SCPD-1 / mini-CAD-propagation discipline this slice exists to honour). **No** `methodology-changelog.md` edit (verified slice-036/R-9 conformance-fix precedent adds none; a parentless `###` entry would break META-1's `## v`-block split — see design.md "What's new").
- [ ] CAD-1 / mini-CAD drift stays clean: do NOT edit `skills/validate-slice/SKILL.md` (it is already SRSC-1-correct per slice-038; touching it risks a forward-sync drift FAIL and is unnecessary).

## Out of scope

- Minting a NEW `-D` discipline rule / audit for the "SKILL.md-repointing slice must supersede its mini-CAD prose-pin in the same fix block" class. N=1 (only slice-038); below this project's N≥2/N≥3 promotion threshold, and the backstop already exists (slice-039 BC-PROJ-4 "run the full suite on the real artifact at pre-finish" caught R-10). The N=1 gap is noted as a `/critic-calibrate` watch-list candidate in the R-10 `**Retired**:` line + this slice's `reflection.md` (the surfaces `/critic-calibrate` mines); no new rule/version-class is codified here.
- Editing `skills/validate-slice/SKILL.md` Step 5.5 prose — already SRSC-1-correct (slice-038); changing it is not this slice's job.
- Any change to `tools/shippability_runner.py` or SCMD-1 `_segments()` — slice-038 already pinned these (39/39 PASS on the real catalog); untouched here.
- The R-9-adjacent `--filter-status open` returns-retired-risks footgun — separate concern (candidate #2, its own slice per CLAUDE.md "refactors need a slice").

## Dependencies

- Prior slices: [[slice-038-pin-shippability-runner-segment-contract]] — SRSC-1, the repointing that orphaned the prose-pin; [[slice-031-complete-shippability-decoupling]] — SCMD-1, origin of the B2-v1 prose-pin being superseded
- Failing repro test (BFRD-1 prerequisite — **pre-exists, no `/repro` needed**): `tests/methodology/test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command` — currently FAILS on master with `AssertionError: Step 5.5 runner must consume the Machine-cmd column (B2-v1)` (confirmed live at /slice: `1 failed, 3 passed`). One AC (AC1) asserts this test PASSES at slice end.
- Vault refs: [[risk-register#R-10]], [[decisions/ADR-039]] (SRSC-1), [[decisions/ADR-031]] (SCMD-1)

### BFRD-1 disposition (Step 3c)

Candidate-source signal sub-mode (b) fires: sourced from risk-register bug-class entry R-10.
`architecture/shippability.md` has no `tests/bugs/*` row for this defect (grep count 0, per
R-10) — but the project's convention for this defect class is the pre-existing methodology
mini-CAD test, which **already fails on master with the expected signature** (verified live
at /slice). The BFRD-1 "verbal-claim-with-path / project's convention for bug-fix tests"
fallback (skills/repro/SKILL.md L87 caveat) is satisfied: the reproduction already exists
and IS the artifact this slice realigns. No STOP-route to `/repro` — mirrors the
slice-034 (R-7/TFFL-1) and slice-036 (R-9) risk-register-sourced conformance-bug precedent.

## Mid-slice smoke gate

At ~50% of build (after realigning the test assertion + docstring), run:
```
$PY -m pytest tests/methodology/test_validate_slice_skill.py -q
```
Expected: `4 passed`, 0 failed. Then prove non-tautology (AC2): temporarily substitute a
pre-SRSC-1 phrase for `VALIDATE` (monkeypatch or scratch string), re-run
`test_step4_5_5_consumes_machine_stable_command`, observe it FAILS, restore.
If the realigned test passes a pre-SRSC-1 regression: STOP, the pin is tautological — fix before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. non-tautology proof + R-10 retired atomically)
- [ ] /drift-check passes (CAD-1 / mini-CAD clean — SKILL.md untouched)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
