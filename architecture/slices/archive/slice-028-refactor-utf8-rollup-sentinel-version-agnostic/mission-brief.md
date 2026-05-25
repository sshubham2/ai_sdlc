# Slice 028: refactor-utf8-rollup-sentinel-version-agnostic

**Mode**: Standard
**Estimated work**: 0.5 day (SMALL, ~2 hr)
**Risk retired**: No risk-register ID. Retires the recurring **N=5 sentinel-count-bump maintenance-tax class** flagged in slice-027 aggregated lessons (`architecture/slices/_index.md` line 40) — the UTF-8 rollup sentinel's hardcoded `== N` literal + version-anchored ledger comment was manually bumped at slices 023→025→026→027 and would bump again here.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The UTF-8 rollup sentinel `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` (`tests/methodology/test_utf8_stdout_regression.py:203`) asserts a hardcoded absolute count (`assert len(actual_audits) == 20`) with a `post-slice-027` version anchor and a hand-maintained "17 + 1 + 1 + 1" tool ledger comment. Every slice that adds a `tools/*.py` audit tool must manually bump this literal or the suite goes red — a recurring, mechanical maintenance tax (N=5 and counting). This slice refactors the sentinel to assert the invariant it actually protects (every discovered audit tool is exercised under cp1252 somewhere in this module) **derived from repo state**, not a magic number — exactly the version-agnostic-refactor pattern slice-014/[[ADR-013]] applied to the PMI-1 cleanliness gate (PMI-1 v1.0 → v1.1).

## Acceptance criteria

1. The rollup sentinel contains no hardcoded absolute tool-count literal and no `post-slice-NNN` version anchor; its assertion is derived from current repo state.
2. Protective invariant is preserved, not weakened: adding a hypothetical new `tools/<x>.py` audit tool **with** cp1252 regression coverage keeps the methodology suite green with **zero sentinel edits**; adding one **without** coverage makes the suite **red**.
3. Removing or renaming an audit tool leaves no stale count assertion behind (suite stays green when coverage is consistently in sync; no manual ledger edit required).
4. Full `tests/methodology/` suite passes; `tools.utf8_stdout_audit` still reports clean; no regression in the existing per-tool cp1252 parametrized/custom-argv tests.
5. `methodology-changelog.md` records the refactor with rule-ID lineage preserved (UTF8-STDOUT-1 evolution — not a new rule ID), and `architecture/shippability.md` UTF-8 rollup row is updated to reference the version-agnostic shape (RPCD-1 / SCPD-1 consumer-ref propagation).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | No count literal / version anchor | `grep -nE '== [0-9]+|post-slice-[0-9]+' tests/methodology/test_utf8_stdout_regression.py` returns nothing in the rollup sentinel body; read the function to confirm derivation from repo state |
| 2 | Invariant preserved both directions | Temporarily add a stub `tools/_tmp_fake_audit.py` exposing `main()` WITHOUT cp1252 coverage → run `tests/methodology/` → suite RED with a clear "uncovered tool" message; add a matching coverage entry → suite GREEN with no sentinel edit; revert stub |
| 3 | No stale count on removal | Temporarily move an existing audit tool aside → suite stays GREEN (no `== N` mismatch crash) when coverage is correspondingly absent; revert |
| 4 | No regression | `& $PY -m pytest tests/methodology/ -q` all pass; `& $PY -m tools.utf8_stdout_audit` exit 0 |
| 5 | Vault propagation | `methodology-changelog.md` has a new versioned entry citing UTF8-STDOUT-1 lineage; `architecture/shippability.md` UTF-8 rollup row references version-agnostic shape; `/drift-check` clean |

## Must-not-defer

- [ ] Protective invariant NOT weakened — version-agnostic ≠ assertion-removed. A new audit tool lacking cp1252 coverage MUST still fail the suite (the whole point of the sentinel).
- [ ] Rule-ID lineage preserved — this is UTF8-STDOUT-1 evolution (analogous to PMI-1 v1.0→v1.1 / slice-014); do NOT mint a new rule ID for an existing discipline.
- [ ] RPCD-1 / SCPD-1 propagation — changelog entry + `architecture/shippability.md` UTF-8 rollup row updated to the new shape (every audit-rule change propagates consumer refs into the catalog).
- [ ] PMI-1 version atomicity — if `VERSION` bumps, `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` move together in the same slice.
- [ ] Self-hosting drift check — confirm during design whether `tests/methodology/test_utf8_stdout_regression.py` is mirrored/installed anywhere; if so, byte-equality is maintained (mini-CAD class).
- [ ] Clear failure message — when the sentinel fails on an uncovered tool, the message must name the offending tool(s), not just a count delta.

## Out of scope

- The function-level-PTFCD-1 candidate (`_index.md` line 41, N=3) — a separate deferred concern, NOT this slice.
- The already-shipped PMI-1 cleanliness-gate version-agnostic refactor (slice-014/[[ADR-013]]) — referenced as precedent only, not re-touched.
- Any change to the per-tool cp1252 invocation tests' behavior, the `_stdout.reconfigure_stdout_utf8()` helper, or `tools/utf8_stdout_audit.py` (the AST audit tool) — this slice is the regression-sentinel test only.
- Generalizing the pattern to other count-asserting tests beyond the UTF-8 rollup sentinel.

## Dependencies

- Prior slices: [[slice-023-retire-cp1252-stdout-encoding-class]] (origin of UTF8-STDOUT-1 + the rollup sentinel), [[slice-027-add-pipeline-chain-auto-advance]] (last count bump → 20; flagged the refactor as the strongest standing deferred candidate, `_index.md` lines 40-41)
- Precedent: [[slice-014]] / [[ADR-013]] — "version-agnostic PMI-1 cleanliness gate" (PMI-1 v1.0→v1.1); the canonical refactor shape to model.
- Vault refs: [[methodology-changelog]] (UTF8-STDOUT-1 v0.37.0), [[shippability]] (UTF-8 rollup row), [[tools/utf8_stdout_audit.py]], [[tools/_stdout.py]]
- Risk register: none (process-debt class, not a tracked R-ID)

## Mid-slice smoke gate

At ~50% of build (sentinel refactored, before changelog/shippability propagation), run:
```
& $PY -m pytest tests/methodology/test_utf8_stdout_regression.py -q
grep -nE '== [0-9]+|post-slice-[0-9]+' tests/methodology/test_utf8_stdout_regression.py
```
Expected: regression module passes; grep finds no count literal / version anchor in the rollup sentinel body. Then add a throwaway uncovered `tools/_smoke_fake.py` with `main()` and re-run the suite — expected RED with a tool-naming message. Revert the stub. If the suite stays GREEN with an uncovered tool present: STOP — the invariant was weakened; diagnose before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
