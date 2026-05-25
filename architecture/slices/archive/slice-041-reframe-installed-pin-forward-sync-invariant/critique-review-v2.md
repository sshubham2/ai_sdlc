# Critique Review: Slice 041 reframe-installed-pin-forward-sync-invariant (REV-2 DR-1)

**Reviewed by**: critique-review agent (DR-1, rev-2 — independent re-execution after the rev-1 DR-1 false-confirm)
**Date**: 2026-05-18
**First-Critic verdict**: BLOCKED
**First-Critic context**: 2nd consecutive BLOCKED, flaw-relocating (rev-1 B1 → rev-2 B1)
**Dual-review verdict**: ACCEPT

## Summary

The rev-2 first-Critic is empirically correct on every load-bearing claim, confirmed by **executing `classify_fn`/`_reachable_path_segments` against the real artifacts** (not reasoning about `_ESSENTIAL_SHAPES` — the exact error the rev-1 first-Critic and rev-1 DR-1 both made). B1 is VALID; the structural-pivot recommendation is mechanically exact and charter-faithful. M1 and its scope-cut are VALID. The rev-1 DR-1's "re-home ⇒ clean, no hidden contradiction, mechanically sound" is a confirmed calibration-critical **false-negative**. No new missed finding, no severity miscalibration; the pivot does not relocate the flaw. **ACCEPT.**

## Empirical verification performed (the rev-1 DR-1's omission, corrected)

1. **B1** — EXECUTED. Indexed real `test_skill_md_pins.py`, classified `test_textual_evidence_rule_byte_equal_across_n_3_surfaces`, surgically removed L349 + L357, re-classified: `segs=['.claude','diagnose','methodology-changelog.md','skills']` UNCHANGED; `classify=essential` before AND after. `.claude` survives via retained L348 `Path.home()/".claude"/"skills"/"diagnose"`; `methodology-changelog.md` via retained in-repo L354. **Rev-2 B1 correct; rev-1 first-Critic + rev-1 DR-1 empirically false.**
2. **Pivot half 2** — EXECUTED. Swept all 37 currently-essential `test_methodology_changelog.py` fns, simulated dropping only the `.claude/methodology-changelog.md` read-leg: **0 of 37 remain essential** (each → `segs=['methodology-changelog.md']` → `clean`; `.claude` came exclusively from the dropped leg). Confirms the defect is isolated to the cross-module pin.
3. **Registered set cardinality** — EXECUTED both modules. Post-leg-drop essential set = **exactly `{tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces}`** (1 fn). Registering that one qualname ⇒ `essential ⊆ allowlist` ⇒ exit 0 ⇒ R-4 retireable. No other fn needs registration.
4. **Charter fidelity** — VERIFIED `risk-register.md` L90: R-4 charters *"a catalog-derived intentional-installed allowlist, the read **registered** not **absent**"*. Rev-1's `frozenset()` ("re-home, not register") was a charter *deviation*; the rev-2 non-empty-registered pivot returns to the literal charter. Both rev-1 reviewers blessed the charter-divergent branch.
5. **M1 figures** — RE-GREPPED repo-wide: `methodology-changelog.md`=41, `architecture/shippability.md`=27, plus ~17 active-ADR/risk-register/lessons/index/calibration-log sites outside the design's `tests/ agents/ skills/` grep scope. First-Critic figures corroborated.
6. **Rename orthogonality** — VERIFIED. R-4 retirement (charter L90-92) depends on the read-leg disposition, not test-fn names; `test_critique_agent.py:1424` is prefix-only (rename-safe); no structural enforcer asserts the `_in_repo_and_installed` suffix. The rename is pure slice-035 identifier-truth, independently slice-able. **M1 scope-cut sound.**

## Confirmed findings

- **B1** (re-home claim empirically false; cross-module pin stays `essential` after leg-drop; flaw relocated from rev-1 B1) — **VALID**, Blocker appropriate. Builder's structural pivot (non-empty registered allowlist registering exactly the cross-module pin + decouple-only the in-`test_methodology_changelog.py` essentials + rewrite ADR-043) is charter-faithful and mechanically exact (registered set cardinality verified = 1).
- **M1** (frozen-history carve-out misses 41 changelog + 27 shippability + ~17 ADR/lessons/index sites) — **VALID**, Major appropriate. ACCEPTED scope-cut correct — rename orthogonal to R-4, breaks no structural enforcer.
- **m1** (design.md L1426 pointer imprecise; moot under scope-cut) — **VALID**, Minor appropriate.
- **Non-convergence discipline invocation** (slice-030A/031: 2 BLOCKED loops, flaw relocating ⇒ structural pivot + scope-cut, not rev-3 patch) — **VALID and correctly applied**. A rev-3 leg-drop patch provably cannot reclassify the cross-module pin `clean` while retaining its in-repo changelog surface (AC3/m2-required). The register-the-pin pivot is the only convergence move simultaneously mechanically sound AND charter-faithful. Builder missed no cleaner move.

## Suspicious findings

None. Every rev-2 finding verified by execution against real artifacts and holds.

## Missed findings

None (the rev-2 first-Critic's coverage is complete for the design as it must now proceed). Two **TRI-1-record observations** (not EXTEND material — already implied by the BLOCKED + pivot disposition):

- The on-disk design.md / mission-brief.md (AC4) / ADR-042 (L35) / ADR-043 (L15/L24/L28) / verification plan **still encode the empirically-falsified rev-1 empty-allowlist branch**. This is **correct and expected** under the non-convergence discipline — the Builder must NOT pre-apply the pivot before TRI-1 re-ratifies the redesign direction (rev-1 branch-(1) rested on the now-falsified "re-home ⇒ clean" premise). Flagged so the user's TRI-1 explicitly re-ratifies the *non-empty registered* direction and the design/ADR-043 rewrite is tracked as a triage obligation, not assumed done.
- When the pivot's design.md is authored post-TRI-1, `_REGISTERED_INSTALLED_READERS` membership must key on the exact audit-emitted qualified form: `tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` (file-path-qualified `::`-selector, verified from `--json`). Forward design-detail for the not-yet-written pivot design.md; noted so it is not lost between TRI-1 and redesign.

## Severity adjustments

None. B1=Blocker, M1=Major, m1=Minor all correctly calibrated. (The rev-1 DR-1's own M2 Major→Minor / m1 Minor→Major adjustments were ratified at rev-1 TRI-1 and are not re-litigated; not part of the rev-2 finding set.)

## Notes

Confidence **high**, grounded in execution. The rev-1 DR-1's failure is a confirmed reproducible false-negative: it reasoned about `_ESSENTIAL_SHAPES` in isolation (true) but not about `classify_fn`'s subset test over the **union of all retained segments** (L348's unrelated `.claude/skills/diagnose` + L354's retained in-repo `methodology-changelog.md` jointly re-satisfy the two-token shape). Calibration signal for the DR-1 log: a DR-1 "independently verified mechanically sound" on an AST-classification claim is worthless unless the meta-Critic instantiates the classifier against the real (post-edit-simulated) module — reading the shape constant + the dropped line is necessary but not sufficient. The rev-2 first-Critic is the inverse of the rev-1 looseness: empirically rigorous, charter-literal, correctly disciplined (proactive structural pivot, not a doomed rev-3 patch). The pivot introduces no new hidden flaw — swept both modules, registered set is exactly the single cross-module pin, registering it makes R-4 retireable. **ACCEPT.**
