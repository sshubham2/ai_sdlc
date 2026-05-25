# Slice 038: pin-shippability-runner-segment-contract

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-8 (Shippability Step-5.5 catalog runner `;`-split / per-segment-backtick contract is unpinned)
**Test-first**: true  <!-- per TF-1 — the multi-segment naive-outer-strip repro fails before, passes after -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The `/validate-slice` Step-5.5 catalog runner contract (split `Machine-cmd` on ` ; `, then strip backticks **and** whitespace **per segment**) is defined only as SKILL.md prose + an `_segments()` helper *inside the SCMD-1 audit*. Nothing pins the **runner** that actually *executes* each catalog command — so every slice's Step-5.5 run re-derives it ad-hoc, and a naive outer-fence-only strip mangles segment 2 of the lone multi-segment row (#28) into `argv[0] = `` `<interp>… `` → `WinError 2`. This false-FAIL recurred N=2 (slice-032, slice-033). This slice pins the runner-segment contract in one canonical, consumed place so it can never be re-derived incorrectly, and catalogues the regression so the false-FAIL class is non-silently-recurrable.

## Acceptance criteria

1. The Step-5.5 multi-segment runner contract (per-`;`-segment backtick+whitespace strip; interpreter-anchored execution) is pinned in a single canonical place that `/validate-slice` Step 5.5 **consumes** (a shared runner tool OR an audit + explicit SKILL.md prose-pin — `/design-slice` chooses), so it is not re-derived ad-hoc per slice.
2. A catalogued regression test proves: the SCMD-1-correct per-segment parse runs **both** segments of the real row #28 cleanly (no leading backtick on segment 2), AND a naive outer-fence-only strip is demonstrably rejected/prevented by the pinned contract (negative fixture — proves the test is load-bearing, not a tautological green).
3. `skills/validate-slice/SKILL.md` Step 5.5 prose explicitly pins the runner-segment contract (cite the canonical mechanism), so an ad-hoc re-implementation is contract-bound, not folklore.
4. `methodology-changelog.md` (in-repo + installed, forward-synced) carries a new RULE-ID entry; an append-only ADR records the decision; PMI-1/INST-1/RPCD-1/SCPD-1 propagation is atomic (new tool/audit enumerated in `plugin.yaml` + `tools/install_audit.py` if one is added; a shippability catalog row added for the new test).
5. R-8 is marked `retired` in `risk-register.md` citing slice-038 + the new ADR; the new catalogued regression test makes the false-FAIL class environment-independently non-silently-recurrable.

## Test-first plan

Each AC maps to failing-first tests written BEFORE implementation. Paths below are the intended convention (`tests/methodology/`); `/design-slice` may refine. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_shippability_runner_segment_contract.py | test_multi_segment_row_splits_and_strips_per_segment | PASSING |
| 2 | unit | tests/methodology/test_shippability_runner_segment_contract.py | test_real_row_28_both_segments_interpreter_anchored | PASSING |
| 2 | unit | tests/methodology/test_shippability_runner_segment_contract.py | test_naive_outer_strip_runner_is_rejected | PASSING |
| 3 | unit | tests/methodology/test_shippability_runner_segment_contract.py | test_validate_slice_skill_pins_runner_invocation | PASSING |
| 4 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_51_0_srsc_1_entry_present_in_repo_and_installed | PASSING |
| 4 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_51_0_srsc_1_shippability_consumer_propagation | PASSING |
| 4 | methodology | tests/methodology/test_utf8_stdout_regression.py | test_shippability_runner_survives_cp1252_with_u2192 | PASSING |
| 5 | unit | tests/methodology/test_shippability_runner_segment_contract.py | test_real_row_28_both_segments_interpreter_anchored | PASSING |

<!-- AC5 TF-1-row correction (plan-mode finding, user-ratified 2026-05-17): the
original `test_risk_register_audit.py::test_repro_r8_retired_with_slice_and_adr`
row was dropped — R-8 is a runner-contract risk (not an audit-behavior bug like
R-9/slice-036), so a risk-register-read test would assert gitignored-vault
bookkeeping, environment-fragile and not a regression guard. AC5's failing-first
guarantee IS the AC2 catalogued runner-contract test (fails pre-fix, passes
post-fix — exactly AC5's prose). R-8 status-flip = vault bookkeeping + changelog/
ADR cite, mirroring slices 033/034 R-5/R-7 retirement. -->

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Contract pinned + consumed | Inspect the canonical pin (tool or audit+prose); confirm `skills/validate-slice/SKILL.md` Step 5.5 references it (grep). Run the pinned mechanism against real `architecture/shippability.md` row #28 → segment 2 has NO leading backtick. |
| 2 | Regression + negative fixture | `<interp> -m pytest tests/methodology/test_shippability_runner_segment_contract.py -q` → PASS post-fix; the naive-outer-strip negative case is asserted-rejected; both row-#28 segments resolve to interpreter-anchored invocations. |
| 3 | SKILL.md prose-pin | Grep `skills/validate-slice/SKILL.md` Step 5.5 for the per-segment-strip contract clause naming the canonical mechanism. |
| 4 | Propagation atomic | `<interp> -m tools.plugin_manifest_audit` exit 0; `<interp> -m tools.install_audit` exit 0; changelog entry present in-repo AND installed (forward-sync); new shippability row present. |
| 5 | R-8 retired | `<interp> -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` → R-8 absent; R-8 entry shows `Status: retired` + slice-038 + ADR cite. |

## Must-not-defer

- [ ] The pinned contract MUST be **consumed** by `/validate-slice` Step 5.5 (tool invocation or prose-pin citing the canonical mechanism) — a defined-but-unconsumed contract reproduces the exact R-8 folklore failure.
- [ ] The regression test MUST be added as a `architecture/shippability.md` catalogued row (RPCD-1/SCPD-1) so the false-FAIL class can never silently regress.
- [ ] If a new tool/audit is added: enumerate it atomically in `plugin.yaml` + `tools/install_audit.py` (PMI-1/INST-1) in the same slice.
- [ ] Negative-fixture proof: a naive outer-fence-only strip MUST be demonstrably rejected (the test must FAIL before the fix on the multi-segment row) — no tautological green.
- [ ] If `methodology-changelog.md` / installed copies are touched: forward-sync in-repo↔installed (EOL-agnostic per EOL-DRIFT-1) and bump PMI-1 version atomically.

## Out of scope

- R-6 (BRANCH-1 numeric-`NNN` folder regex) and R-2 (`/diagnose` cwd-mismatch runtime test) — separate risks, separate slices.
- Re-homing the **essential**-class coupling (`~/.claude/methodology-changelog.md` forward-sync rows) — that is the chartered slice-030C domain; this slice touches only the runner-segment contract.
- Changing the SCMD-1 `Machine-cmd` grammar or the existing `_segments()` audit logic itself — it is already correct; this slice pins the *runner consumer*, not the audit grammar.
- The EOL-DRIFT-1 `.md` skill-drift comparator concern (R-5, retired) — distinct from the runner-segment concern.

## Dependencies

- Prior slices: [[slice-031-complete-shippability-decoupling]] — SCMD-1 / ADR-031 / `_segments()` per-segment strip already exists; this slice pins the **runner** that consumes the catalog, not the grammar.
- Prior slices: [[slice-033-fix-skill-drift-test-crlf-normalization]] — R-8 split out + formally opened here (m2 ACCEPTED-FIXED handle; reproduced LIVE at slice-033 /validate).
- Vault refs: [[decisions/ADR-031]], [[risk-register#R-8]], `skills/validate-slice/SKILL.md` Step 4 / Step 5.5, `tools/shippability_decoupling_audit.py` `_segments()` (L179–188).
- Test-first failing repro: `tests/methodology/test_shippability_runner_segment_contract.py` (path final at `/design-slice`).

## Mid-slice smoke gate

At ~50% of build, run:
```
<interp> -m pytest tests/methodology/test_shippability_runner_segment_contract.py -q
```
Expected: the per-segment-strip cases PASS and the naive-outer-strip negative case asserts-rejected; against real `architecture/shippability.md`, row #28's two segments BOTH resolve to interpreter-anchored invocations (segment 2 has no leading backtick). If the naive-strip negative case does NOT fail without the pinned contract: STOP — the test is tautological, not load-bearing (slice-037 lesson).

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] TF-1 audit `--strict-pre-finish` clean (all Test-first rows PASSING)
- [ ] PMI-1 / INST-1 / SCMD-1 / RR-1 audits exit 0
