# Reflection: Slice 041 reframe-installed-pin-forward-sync-invariant

**Date**: 2026-05-18
**Shipped**: YES (split-lineage label "030C" — completes the slice-030 split 030A→030B→030C; retires R-4)

## Validated
- MCFS-1 whole-file EOL-agnostic forward-sync gate works — validated by `tools.methodology_changelog_forward_sync` on the real tree (PASS) + 8/8 regression suite (synced→0 / divergent→1 / installed-absent→WARN / CRLF-only→0 / empty-present→1 / CSP-1 parity / M-add-1 relocation-proof).
- Decouple converged exactly as the rev-3 DR-1 verified by execution — `shippability_decoupling_audit --json` exit 0, `essential_registered`={the single slice-019 cross-module pin}, `essential_unregistered`=[]. The rev-3 DR-1's cardinality-1 prediction held precisely against the real artifact.
- Closed-world non-empty registered allowlist (ADR-043) — validated: synthetic unregistered installed-reader ⇒ `essential-unregistered` exit 1; registered pin ⇒ accounted-for not flagged; V3 key resolves against real catalog.
- R-4 retired — `risk_register_audit --filter-status retired` lists R-4, `--filter-status mitigating` does not; full shippability catalog 41/41 PASS (no regression).
- m1 ungated wiring — build-slice Step 6 (verified-ungated checklist) + reflect NEW Step 5b-fs (NOT folded into rule-promotion-gated Step 5b); both forward-synced, 31 skill-drift tests + PCA-1 clean.

## Corrected
- No post-build design corrections. The design's own correction history (rev-1 empty-allowlist → rev-2 leg-drop falsified → rev-3 non-empty registered) was fully resolved *during* the 3-revision /critique loop before build; build executed rev-3 verbatim. The vault (ADR-042/ADR-043 rev-3, methodology-changelog v0.53.0, risk-register R-4 retired) already reflects reality — no further edits needed.

## Discovered
- **The m-add-1 two-syntactic-form hazard was load-bearing, not theoretical.** The AST transformer v1 clobbered `for` headers (the loop-iterable `List` node's `lineno` == the `for` line, so whole-line replacement destroyed `for … in` + `:`). Caught immediately by the post-transform `ast.parse` + backup-restore. Confirms the rev-3 DR-1 m-add-1 finding was correct to surface; the "regenerate-from-`--json`, edit by BOTH forms, treat post-decouple `--json`-empty as confirmation-not-discovery" discipline is what made the recovery clean.
- **A state-transition slice (risk X: mitigating→retired) silently breaks pre-existing tests that pin the OLD state.** `test_r_4_subentry_charters_030c_and_stays_mitigating` asserted "R-4 stays mitigating until 030C ships" — slice-041 IS 030C, so retiring R-4 (the slice's deliverable) FAILed that pin. Neither the design nor the 3-revision Critic stack enumerated it; surfaced only at the pre-finish full-suite run (BC-PROJ-4 class). Realigned in the same fix block (slice-039 discipline) — fn renamed `test_r_4_retired_by_slice_041_030c_completes_the_split`, body flipped, 0 live `::`-consumers so no propagation. **Generalizable Critic-miss class** (calibration input below).
- **Self-inflicted Phase-A over-tightening**: the M-add-1 relocation-proof test asserted `"…" not in catalog_text` (whole catalog) — but row #41's *Critical-path prose* legitimately names the tool. The real invariant is "not in the executable Machine-cmd column (6th cell)". Caught at pre-finish; corrected to parse the column. Lesson: a negative-invariant pin must target the *executable* surface, not raw text that legitimately contains the name in prose.

## Deferred
- **The `_entry_present_in_repo_and_installed`→`_entry_present` rename** — TRI-1 scope-cut at /critique rev-2 to a SEPARATE identifier-truth slice. Reason: DR-1-verified orthogonal to R-4 (no test-fn-name dependency; breaks no structural enforcer) AND carries a 41-changelog-line + 27-shippability + ~17-ADR/lessons/index **frozen-history-vs-rewrite** blast radius into append-only shipped history. The ~33 decoupled `_entry_present_*` fns + the new v0.53.0 pin now temporarily over-claim (name says `_and_installed` but body reads in-repo only) — consciously accepted (slice-035 decided-not-discovered), recorded in design.md/changelog/risk-register. **Lands in: the next slice (strongest standing candidate).**

## Critic calibration

Per TRI-1, scored against `critique.md` (rev-3) `## Triage` + the rev-1/rev-2 lineage + build/validate reality:

- **rev-1 B1** (essential ≠ the 32): VALIDATED — the first Critic *ran the audit* and was empirically right; the design's central premise was false.
- **rev-1 B2 / M1–M4 / m1–m2 / M-add-1 / M-add-2**: VALIDATED — all confirmed; drove the rev-2 redesign.
- **rev-2 B1** (flaw relocated — leg-drop cannot reclassify the cross-module pin; `classify_fn` unordered subset): VALIDATED — the single most load-bearing catch of the whole slice. The rev-1 first-Critic AND the rev-1 DR-1 BOTH false-confirmed the re-home premise by *reasoning about `_ESSENTIAL_SHAPES`* instead of *executing `classify_fn`*.
- **rev-2 M1** (frozen-history carve-out incomplete): VALIDATED — resolved via the TRI-1 scope-cut.
- **rev-3 first-Critic CLEAN**: accurate — DR-1 independently re-executed and confirmed genuine slice-031/030A convergence (not a post-fatigue rubber-stamp).
- **rev-3 DR-1 m-add-1** (two-syntactic-form leg): VALIDATED — materialized as a real transformer bug during build (Discovered above).
- **rev-3 DR-1 m-add-2** (MCFS-1 regression suite must not be catalog-cited): VALIDATED — design.md negative invariant + the consumer-propagation test's m-add-2 assertion prevented a self-violating catalog row.

**Missed by Critic**: the state-transition-breaks-old-state-pin class (`test_r_4_..._stays_mitigating`). Neither the design nor any of the 3 Critic revisions / 3 DR-1 passes enumerated that the slice's own R-4 retirement would FAIL a pre-existing test asserting R-4 mitigating. Only the pre-finish full-suite run (BC-PROJ-4) caught it. (The relocation-proof over-tightening was a Builder implementation imprecision, not a Critic-reachable design defect — self-caught at pre-finish.)

**Pattern**:
1. **The "execute, don't reason" law is now N≥3 for the DR-1 layer specifically** (slice-032 Builder/Critic; slice-034 first-Critic; slice-041 rev-1 DR-1). A DR-1 "independently verified mechanically sound" on an AST-classification / audit-parse claim is *worthless* unless the meta-Critic instantiated the classifier against the real (and edit-simulated) artifact. Reading the shape constant + the changed line is necessary-but-insufficient. **Strong `/critic-calibrate` input** — candidate critique-review-agent sub-clause: "for any AST-classification/audit-parse soundness claim, the meta-Critic MUST execute the classifier, not reason about the shape constant; a reasoned 'mechanically sound' is a false-confirm class (slice-041 rev-1 DR-1, N≥3 with slice-032/034)".
2. **State-transition slices need a Critic checklist item**: "does this slice change a vault state (risk status, ADR status, gate verdict) that a pre-existing test pins to the OLD value? Enumerate + realign in the same fix block (slice-039 generalized)." The 3-revision stack missed it on every pass.
3. **Split→one-pass convergence confirmed a 3rd time** (slice-030A, slice-031, now slice-041): 2 BLOCKED loops with flaw-relocation → structural pivot (not a rev-N patch) → CLEAN-core in one pass. The discipline's prescription ("stop patching, surface a structural decision; don't wait for the meta-Critic to force it") paid off decisively.

## Lessons for next slice
- **The rename is the strongest standing next-slice candidate** — `realign-entry-present-pin-names-to-decoupled-shape` (or similar): rename the ~33 `_entry_present_in_repo_and_installed` + the v0.53.0 pin + the 2 `_entry_names_*_in_repo_and_installed` → drop `_and_installed`, with the frozen-history carve-out (`fixtures/archive_backtest_corpus/**`, `archive/**`, the 41 shipped-changelog `**Validation**:` lines, ~17 ADRs) consciously enumerated as NOT-renamed. Identifier-truth (slice-035); no R-4 dependency.
- **For any slice that flips a vault state value** (risk mitigating→retired, ADR accepted→superseded, a verdict): pre-grep for tests pinning the OLD value and realign them in the same fix block. Add this to the Builder plan-mode checklist.
- **A negative-invariant pin must target the executable surface, not raw text** — `"X not in catalog_text"` is wrong when X legitimately appears in prose; assert against the parsed Machine-cmd column / the resolved-fn set.
- **DR-1 calibration**: feed pattern #1 to the next `/critic-calibrate` — the rev-1 DR-1 reasoned-not-executed false-confirm is the highest-signal meta-Critic miss recorded to date (it let a BLOCKED slice's flaw relocate undetected for a full revision).

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-4 `mitigating`→`retired` (**Retired**: slice-041; 030A/030B/030C lineage) — done in build Phase F
- [[methodology-changelog.md]] — v0.53.0 MCFS-1 entry + forward-synced to `~/.claude/` — done in build Phase D
- [[decisions/ADR-042]] + [[decisions/ADR-043]] — authored (rev-3 scope), both `reversibility: cheap`, `supersedes: null`
- This slice's [[design.md]] — rev-3 (pivot + m-add-1/m-add-2 notes); no post-build deviation
- [[shippability.md]] — row #41 added (build Phase F) — the slice's catalog critical path
- No `components/`/`contracts/` updates (thin vault, Standard mode — code is truth)
- **No BC-1 build-check promotion**: this slice's lessons are methodology/Critic-calibration class (DR-1 execute-don't-reason; state-transition pin realignment) — they flow via lessons-learned + `/critic-calibrate` (Critic-prompt tuning), NOT evergreen per-slice build-checks. No recurring *code* pattern to promote.
