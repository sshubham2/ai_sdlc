# Slice 043: codify-split-slice-folder-naming-convention

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-6 (open, low-band, recurring) — `tools/branch_workflow_audit.py` `_SLICE_BRANCH_RE`/`_SLICE_FOLDER_RE` (lines 59/62) hard-require `\d{3}`; the project's split-slice convention (030A/030B/030C → folders 030/031/041) collided with this implicit, undocumented convention and cost slice-031 a mid-build folder+branch+id rename.
**Test-first**: false  (opt-in; /design-slice may elevate if it picks a regex-behavior-change option — pinning the decided BRANCH-1 behavior with a failing test first is the project-idiomatic path for an audit-behavior change)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The split-slice follow-up naming convention ("numeric `slice-NNN-` folder; the `NNNx` letter is a prose lineage label only") is real, witnessed, and load-bearing — but it lives nowhere as an explicit, enforced statement, so `tools/branch_workflow_audit.py` ambushes the next split slice with a `usage-error` mid-build (slice-031 paid this cost). This slice makes the convention unambiguous and deterministic so the next split slice (the 030-lineage proves split slices are routine here) cannot re-discover R-6.

## Acceptance criteria

1. The split-slice folder/branch naming convention is stated once, canonically, in a discoverable durable location (CLAUDE.md and/or a methodology note) — no implicit "numeric-folder, letter-label-in-prose-only" trap remains.
2. `tools/branch_workflow_audit.py`'s behavior on a split-slice follow-up is deterministic and intentional: it either accepts the canonical split-slice form, or rejects it with an actionable message that names the convention and the fix (decision locked at /design-slice, recorded in an ADR).
3. A regression test pins the decided BRANCH-1 behavior (the canonical-form input + the rejected-form input, whichever the ADR decides) so the next split slice cannot silently regress or re-trip R-6.
4. R-6 transitions **open → retired** in `architecture/risk-register.md` — the `**Status**: open` field line is flipped to `**Status**: retired` AND a `**Retired**: slice-043 (2026-05-18; ADR-046)` line is added (R-7 two-part shape; RR-1 parses status from the `**Status**:` field, not the `**Retired**:` prose). Verified via `tools.risk_register_audit` reporting `R-6.status == "retired"` and R-6 absent from `--filter-status open`.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Convention documented canonically | grep the durable location for the canonical convention statement; confirm exactly one authoritative statement, no contradicting/implicit phrasing remains |
| 2 | BRANCH-1 behavior deterministic + intentional | Run `$PY -m tools.branch_workflow_audit` against a synthetic split-slice folder fixture; observe the ADR-decided outcome (accept, or reject with the actionable message) |
| 3 | Regression pin exists and is non-tautological | Run the new regression test; confirm it FAILs against the pre-slice audit behavior (or a simulated revert) and PASSes against the shipped behavior |
| 4 | R-6 retired | `$PY -m tools.risk_register_audit architecture/risk-register.md --json` — R-6's parsed `status == "retired"`; `--filter-status open` does NOT contain R-6 (it DOES pre-slice — genuine contrast). R-6 goes `open → retired` directly (no `mitigating` intermediate, unlike R-4/R-5) |

## Must-not-defer

- [ ] Methodology-surface obligation question pre-decided at /design-slice and verified against the *actual* enforcing META-1 / PMI-1 assertions (NOT a precedent alone — MEPD-1(b) / slice-032 false-precedent guard): does this need a methodology-changelog RULE-ID + `test_v_0_NN_0_*` entry-pin + PMI-1 4-part version bump, or is it a conformance/convention-codification class recorded via ADR + risk-retirement only? Decide BEFORE build, never auto-bless "no entry", never adjudicate late at /reflect.
- [ ] State-transition pre-grep (slice-039/041 recurring lesson, N≥2): before flipping R-6 open→retired, grep the test suite for any test pinning R-6's OLD `open`/`Status: open` state (or asserting "R-6 stays open") and realign it in the SAME fix block — the BC-PROJ-4 full-suite pre-finish run is the structural backstop, not the Critic stack.
- [ ] CAD-1 / mini-CAD: if CLAUDE.md or any installed-mirrored surface is touched, verify in-repo↔installed forward-sync (EOL-agnostic per ADR-033 / EOL-DRIFT-1).
- [ ] The new regression test is a genuine contrast (FAILs on pre-slice behavior), not a tautological green.

## Out of scope

- Widening the regex AND simultaneously codifying a no-letter-folder convention as a hedge — pick ONE coherent behavior at /design-slice; shipping both is a contradictory contract.
- Any change to the split-slice *lineage-label* convention itself (the `NNNx` prose label semantics) — only the folder/branch *naming + audit acceptance* is in scope.
- Retroactively renaming any archived split-slice folder (030/031/041 stay as shipped).
- Running `/critic-calibrate` on the slices-038–042 input backlog (separate, flagged at /slice — not this slice).

## Dependencies

- Prior slices: [[slice-031-complete-shippability-decoupling]] — the witnessed R-6 instance (mid-build rename); [[slice-041-reframe-installed-pin-forward-sync-invariant]] — the "030C" split-lineage label precedent + state-transition pre-grep lesson.
- Vault refs: [[risk-register#R-6]], `tools/branch_workflow_audit.py` (`_SLICE_BRANCH_RE`:59, `_SLICE_FOLDER_RE`:62, usage-error at :277), `CLAUDE.md` (Brownfield rules → Branch-per-slice / BRANCH-1).
- Risk register: [[risk-register#R-6]] (open → retire).

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m tools.branch_workflow_audit <synthetic split-slice folder fixture path>
```
Expected: the ADR-decided deterministic outcome (clean accept, OR exit-2 usage-error with the new actionable convention-naming message — whichever /design-slice locked). If the outcome is the OLD undifferentiated `slice folder name does not match slice-NNN-<name> pattern` with no convention guidance: STOP, the fix is not wired.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] BC-PROJ-4: every affected audit/gate run on the REAL artifact at pre-finish, output read (state-transition pre-grep backstop)
- [ ] Full `tests/methodology/` suite green (R-10-class master-non-green guard)
