# Slice 041: reframe-installed-pin-forward-sync-invariant

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-4 (HIGH, score 6 — currently `mitigating`; this slice escalates it to `retired`). Discharges DR-1 **M-add-1** deferred at slice-030B TRI-1.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

> **Split-lineage label**: "030C" (chartered as `reframe-installed-pin-forward-sync-invariant` in the R-4 sub-entry, `architecture/risk-register.md` L90–92). Per R-6 convention the **folder is the numeric canonical `slice-041-`**; "030C" is a prose split-lineage label only (cross-refs: slice-030A=slice-030, slice-030B=slice-031). Decided at `/slice` to avoid the slice-031 mid-build rename churn (R-6).

## Intent

An audit-derived family of essential cited fns reads the **untracked** `~/.claude/methodology-changelog.md` (no BCI-1 analogue; SCMD-1 recognizes but does not flag this "essential" class, chartering the fix here). Two distinct populations: (1) the in-`test_methodology_changelog.py` per-version pins whose `.claude` token comes only from the installed read-leg → **decoupled** (leg-drop; forward-sync re-homed to the new whole-file MCFS-1 gate); (2) the cross-module slice-019 LAYER-EVID-1 pin whose installed-changelog read is intentional/protective → **registered** in a non-empty allowlist (charter-literal "registered not absent"). (rev-1 "32 fns/empty allowlist" + rev-2 "leg-drop the cross-module pin" were both empirically falsified by *executing* `classify_fn`; rev-3 is the DR-1-verified charter-faithful design after the slice-030A/031 non-convergence pivot.) This slice re-homes that forward-sync invariant onto a properly-gated **non-catalog** control (the BCI-1-analogue this class never had), reframes SCMD-1's essential-class handling from "silently not-flagged" to a positive catalog-derived **intentional-installed allowlist** (the read *registered*, not merely *absent*) — without the new compensating guard itself becoming an unscanned coupled cited-fn (the M-add-1 relocation hazard) — and escalates R-4 to `retired`. After this, the essential-class false-PCA-1-HALT window is closed and the slice-030 split (030A→030B→030C) is complete.

## Acceptance criteria

1. A **non-catalog** forward-sync control ships that asserts in-repo `methodology-changelog.md` is content-equal **modulo line endings** (EOL-DRIFT-1 / ADR-033) to installed `~/.claude/methodology-changelog.md`, wired as a **non-opt-out** gate (BCI-1-analogue: `/build-slice` pre-finish and/or `/reflect` post-write, fail-loud with an attributed message), and regression-tested.
2. The new forward-sync control is provably **NOT** a shippability-catalog-cited fn: `tools/shippability_decoupling_audit.py`'s own closed-world cited-fn derivation does not resolve the new guard, and no `Machine-cmd` cell cites it (M-add-1 relocation guard — the compensating guard must not re-introduce the essential coupling).
3. The audit-derived in-`tests/methodology/test_methodology_changelog.py` essential fns (28 `_entry_present_*` incl. essential-but-uncited `v_0_42_0` + 5 `_entry_names_*`/`_supersession`) ∪ the 4 defined-but-uncited `_entry_present_*` no longer read untracked `~/.claude/methodology-changelog.md` (drop only that read-leg; retain every in-repo content/canonical-phrase assertion). Worklist regenerated from `shippability_decoupling_audit --json` `essential`, never hand-copied (rev-1 failure mode). DR-1-verified: 0/37 in-module fns remain essential post-leg-drop. **No rename** (scope-cut — separate identifier-truth slice).
4. SCMD-1's essential-class handling is reframed to a closed-world **non-empty catalog-registered intentional-installed allowlist**: `_REGISTERED_INSTALLED_READERS = frozenset({"tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces"})` (registers exactly the slice-019 LAYER-EVID-1 cross-module pin with rationale — charter-literal "registered not absent"; that pin is untouched). A cited fn classified `essential` ∉ the set ⇒ `essential-unregistered` exit 1; ∈ ⇒ accounted-for. Post-slice essential set = exactly the registered member ⇒ exit 0 (DR-1-verified cardinality=1). `--json` reports `essential_registered` + `essential_unregistered`.
5. R-4 escalated to `Status: retired` in `architecture/risk-register.md` with a `**Retired**: slice-041 …` line; `risk_register_audit --filter-status retired` lists R-4 and `--filter-status mitigating` no longer does. Full shippability catalog runs with no regression and no essential-class environment-fragile FAIL.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Non-catalog forward-sync control | New test module asserts in-repo↔installed `methodology-changelog.md` content-equality (CRLF-normalized); intentionally divergent fixture proves it FAILs loudly; the wired gate (build-slice pre-finish / reflect post-write) refuses on divergence. `pytest <new module>` green on a synced tree. |
| 2 | Guard not catalog-cited | `$PY -m tools.shippability_decoupling_audit architecture/shippability.md --json` — new guard fn not in the derived cited-fn set; `grep` of `architecture/shippability.md` Machine-cmd column shows no reference to the new guard module/fn. |
| 3 | Decouple complete (executed) | Worklist regenerated from `--json` `essential`; post-decouple `shippability_decoupling_audit --json` `essential` = exactly `{tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces}`; that qualname ∈ `_REGISTERED_INSTALLED_READERS` ⇒ `essential_unregistered` empty ⇒ exit 0. |
| 4 | Non-empty registered allowlist + closed-world | `--json` shows the cross-module pin in `essential_registered`; a deliberately-unregistered essential fixture ⇒ `essential-unregistered` exit 1 (closed-world proof); the registered-key regression test asserts the qualname resolves against the real catalog (DR-1 key-form flag). |
| 5 | R-4 retired + catalog green | `risk_register_audit --json --filter-status retired` lists R-4; `--filter-status mitigating` does not; full `/validate-slice` Step-5.5 catalog run = no regression, no essential-class env-fragile FAIL. |
| 6 | M3 self-classification (pre-finish) | After authoring the v0.53.0 pin + its shippability row LAST: `shippability_decoupling_audit --json` asserts `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed ∈ clean` (in-repo-only body). |
| 7 | m1 ungated wiring | `/build-slice` Step 6 MCFS-1 sub-section is non-opt-out + NOT rule-promotion-gated; the new `/reflect` step is NOT inside Step 5b (read both anchors, confirm). |

## Must-not-defer

- [ ] **M-add-1 relocation proof** — mechanically-asserted evidence that MCFS-1 is NOT reachable by `tools.shippability_decoupling_audit._cited()` over the real catalog (non-catalog AND not a callee of any cited fn). DR-1-verified sound; the regression test is the proof, not prose. The closed-world rule additionally HALTs any *future* unregistered essential. Non-negotiable.
- [ ] **Forward-sync invariant preserved, not weakened** — MCFS-1 must HALT on a genuine divergent installed-changelog fixture AND exit 0 on a CRLF-only difference (both must-not-mask AND must-not-false-FAIL proven). A guard that passes regardless of divergence is a silent-disable (R-7/slice-022 class).
- [ ] **m1 ungated wiring (Major, DR-1-upgraded)** — MCFS-1's primary gate is `/build-slice` Step 6 (non-opt-out, NOT gated on rule promotion); any `/reflect` wiring is a NEW dedicated step, NOT folded into rule-promotion-gated Step 5b.
- [ ] **Registered-key form** — `_REGISTERED_INSTALLED_READERS` member = the exact audit-emitted file-path-qualified `::`-selector; a regression test asserts it resolves against the real catalog (a typo'd key silently fails-open — DR-1 flag).
- [ ] **Cross-module pin untouched** — `tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` is *registered*, not modified; its N surfaces (incl. the L349 installed-changelog read) stay (slice-019 LAYER-EVID-1 protection preserved).
- [ ] EOL-agnostic comparison (EOL-DRIFT-1 / ADR-033) — local 1-line CRLF→LF normalization, CSP-1 behaviour-parity-pinned to `_normalized_sha256` (not raw-byte; not a tools→tests import).
- [ ] R-4 risk-register escalation written with a `**Retired**: slice-041` line; 030A/030B/030C lineage cross-refs intact.
- [ ] Methodology-surface obligation = **MEPD-1 (a) rule-path**, verified against the actual enforcing assertion `test_methodology_changelog.py::test_each_changelog_entry_carries_rule_reference` (L127–144 — a `Rule reference` line per `## v` block, NOT a test-name suffix convention; DR-1-confirmed): mint MCFS-1 + v0.53.0 entry + 4-part PMI-1 bump + in-repo-only-body entry-pin (existing naming convention, LAST). `agents/critique.md` NOT edited (scope-cut).

## Out of scope

- R-6 (BRANCH-1 numeric-NNN regex) — separate slice; this slice merely *complies* with the numeric-folder convention.
- R-1 / R-2 / R-3 — unrelated risks; not touched.
- The *incidental* decoupling class — already shipped at slice-030B (=slice-031, SCMD-1/ADR-031). This slice handles only the *essential* class.
- Reworking BCI-1's build-checks integrity gate — the new control is an *analogue* for a different artifact, not a change to BCI-1.
- **The `_entry_present_*`→`_entry_present` rename (TRI-1 scope-cut, rev-2)** — DR-1-verified orthogonal to R-4 (no test-fn-name dependency; breaks no structural enforcer); its 41-changelog/27-shippability/~17-ADR frozen-history blast radius into append-only shipped history is a SEPARATE identifier-truth slice. Decoupled fn names temporarily over-claim — consciously accepted (slice-035: decided, not discovered).
- **Modifying `tests/skills/diagnose/test_skill_md_pins.py` or `classify_fn`/`_ESSENTIAL_SHAPES`** — the cross-module pin is *registered*, not modified; the audit's subset semantics are correct as-is (rev-2 B1 was a design misread, not an audit bug).

## Dependencies

- Prior slices: [[slice-031-complete-shippability-decoupling]] (=030B, SCMD-1 / ADR-030 + ADR-031 — recognizes the essential class and charters this fix); [[slice-030-repair-build-checks-vault-and-harden-shippability]] (=030A, BCI-1 / ADR-028 + ADR-029 + ADR-030 — the BCI-1 pattern this control is an analogue of); [[slice-033-fix-skill-drift-test-crlf-normalization]] (EOL-DRIFT-1 / ADR-033 — the EOL-agnostic comparator to reuse).
- Vault refs: [[risk-register#R-4]] (charter — `**slice-030B re-scope sub-entry**`, L87–92); `tools/shippability_decoupling_audit.py` (SCMD-1 essential-class branch, L27–30); `tools/build_checks_integrity.py` (BCI-1 analogue pattern).
- Risk register: [[risk-register#R-4]] — escalate `mitigating` → `retired`.
- **Not a BFRD-1 bug-fix route**: R-4's *substance* was mitigated at slice-030A; the repro `tests/methodology/test_build_checks_audit.py` exists and is green. This slice is the chartered *decoupling / invariant-re-homing refactor* residual, not a defect reproduction — no `/repro` prerequisite. (Recorded transparently at `/slice` since the candidate is risk-register-sourced.)

## Mid-slice smoke gate

At ~50% of build (non-catalog control written + wired, before reframing the SCMD-1 essential branch), run:
```
$PY -m pytest <new forward-sync control module> -q
$PY -m tools.shippability_decoupling_audit architecture/shippability.md --json
```
Expected: the new control passes on the synced tree AND FAILs on a deliberately-divergent fixture; the decoupling audit still classifies the not-yet-reframed essential set as recognized (no incidental violations introduced). If the new control passes regardless of divergence, or the audit reports an incidental violation: STOP, diagnose, don't continue (relocation / silent-disable signal).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. M-add-1 relocation proof + forward-sync-not-weakened)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] Full shippability catalog: no regression, no essential-class environment-fragile FAIL
- [ ] No new TODOs / FIXMEs / debug prints
