# Critique Review: Slice 030B complete-shippability-decoupling

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-16
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively strong: B1, B2, B3, M1, M3, M4, M2, m2 are all VALID with correct severities, verified against the actual code. No over-reach (no suspicious findings) — the first Critic resisted the slice-030A D-3 trap and explicitly self-checked against the rubber-stamp signal. However, the first Critic's own B1-recommended fix (option (a): single tracked installed-mirror fixture + byte-equality guard) carries an unexamined relocation surface that would defeat the in-repo↔installed forward-sync invariant and re-home the coupling a fourth time — exactly the slice-030 failure pattern. One Major added (M-add-1); one observation on m1.

## Confirmed findings

- **B1** — CONFIRMED, Blocker correct. Rows 7–30 cite ~22 distinct `test_v_0_NN_0_*_entry_present_in_repo_and_installed` fns (v0.22.0 CAD-1 → v0.44.0 BCI-1), each reading `Path.home()/".claude"/"methodology-changelog.md"`. Scoping SCMD-1 to #5/#8/#12 leaves ~20 rows env-coupled; R-4→retired would be false. "Category moved into the hand-enumerated row triple = category enumeration" = the slice-030 v1/v2 relocation defect + the must-not-defer prohibition.
- **B2** — CONFIRMED, Blocker correct. `validate-slice/SKILL.md` Step 4 prose not in design's What's-new/Wiring; AC3 undelivered without it.
- **B3** — CONFIRMED, Blocker correct. `shippability.md` L7 header = 5 columns; `shippability_path_audit.py` L147 `if len(cells) < 5: continue`, L152 `command_cell = cells[3]`. ADR-031 says "6th" while design.md says "7th" — internal inconsistency. continue-skip silently disabling PTFCD-1 for a column-missing row is a real fail-open.
- **M1** — CONFIRMED, Major correct. Coupling already indirected: `_GLOBAL_BUILD_CHECKS` (test_build_checks_audit.py L380 module constant), `REPO_ROOT`/`read_file` cross-module (conftest L6/L15), inline `project_path = REPO_ROOT/"architecture"/"build-checks.md"; .read_text()` (L949-950) outside any `audit_slice`. Closed-world-allowlist counter-proposal is the right framing.
- **M3** — CONFIRMED, Major correct, sharpest finding in the set. slice-001 read by `test_slice_001_archive_still_fires_legitimate_rules` (L929/960, row #8) AND `test_slice_001_archive_still_fires_proj2` (L1314, row #12); ADR-030's list `slice-003/004/005/006/007/011` omits it — the enumeration defect literally recurring inside the ADR meant to cure it.
- **M4** — CONFIRMED, Major correct. 7 `if _GLOBAL_BUILD_CHECKS.exists():` guards (L426/465/507/842/880/919/974 — Critic listed 5, slight undercount, substance correct). Home-unavailable → assertions silently dropped → AC2 passes vacuously.
- **M2** — CONFIRMED, Major correct as far as it goes (M-add-1 deepens it).
- **m2** — CONFIRMED, Minor correct.

## Suspicious findings

None. Every first-Critic finding corroborated by the actual code. The first Critic did NOT over-reach.

## Missed findings

- **M-add-1 (Major): B1 option (a)'s tracked-mirror-fixture + byte-equality-guard relocates the coupling a 4th time and the guard escapes SCMD-1's derivation.** The in-repo↔installed entry-pin fns exist *specifically* to detect a forgotten forward-sync to untracked `~/.claude/methodology-changelog.md` (docstrings L212-213/L261-262: "forward-sync after in-repo edit was forgotten"). That read is the load-bearing assertion, **not incidental coupling** — unlike C1/C2 where the tracked fixture is byte-faithful via a separate always-on gate (BCI-1). **There is no BCI-1 analogue guaranteeing `~/.claude/methodology-changelog.md` ≡ in-repo**; that equivalence is precisely what these ~22 fns are the only enforcers of. Two unexamined consequences of B1(a)'s mechanism:
  1. If the ~22 fns assert against the **tracked mirror fixture**, they no longer witness a real forgotten `~/.claude/` forward-sync — the CAD-1-class invariant is **destroyed, not decoupled**. M2's naming-lie generalized from 2 fns to ~22 and escalated from naming to invariant-loss.
  2. The compensating "fixture↔real-installed byte-equality guard" is the *only remaining* reader of untracked `~/.claude/`. Either it is catalog-cited (then it IS the new coupled-cited-fn — relocation 4th time, SCMD-1's all-rows scan would FAIL it), or it is NOT catalog-cited (then SCMD-1's runtime re-derivation never scans it, the R-4-retirement-critical invariant is invisible to the durable audit, a future silent break uncaught — the slice-030 relocation pattern one indirection deeper).
  Not an argument against B1's scope-widen (correct). It is that the recommended *mechanism* for B1(a) is under-specified at exactly the relocation seam slice-030 keeps failing on. **Proposed fix**: TRI-1 must resolve, in ADR-031 or a new ADR, whether the installed-read is (i) eliminated (and what then witnesses forgotten forward-sync) or (ii) retained-and-allowlisted — SCMD-1's invariant becomes "every entry-pin fn's installed-read is *accounted for* (catalog-derived intentional-installed allowlist), the read is *registered* not *absent*" + how SCMD-1 derives+pins that allowlist from catalog text without the guard itself being an unscanned coupled fn. Without this, B1(a) ships the relocation. **Carry-forward**: applies regardless of B1 fork — if TRI-1 picks (b)/split, M-add-1 transfers to whatever slice owns entry-pin decoupling; not closed by the fork decision.

## Severity adjustments

None. All 8 first-Critic severities correctly calibrated. **Note on m1**: M-add-1 + M3 together make the corpus-fidelity argument load-bearing for R-4 retirement, so m1's "soften wording" fix is necessary-but-insufficient — the immutability claim needs the SCPD-1/SCMD-1 orphan-catch made concrete in AC2, not just softened prose.

## Notes

High confidence — every first-Critic citation independently verified against live files (row→fn map, line numbers, guard shapes), all corroborated (trivial undercounts only: M4 5-of-7 guards; B1 "~38" ≈ 22 entry-pin rows + ~16 PMI-1-gate rows same untracked path). Calibration: markedly healthier than slice-030 v1/v2 — per-finding accuracy matches the v3 standard; the Critic armed itself against the rubber-stamp smell. **Remaining D-3 risk is now Builder-side**: every Builder draft is again ACCEPTED-PENDING across a BLOCKED loop (the 030A D-3 signature); the B1 (a)-vs-(b) fork is genuine engagement, but M-add-1 shows the Builder accepted B1(a) without stress-testing the mechanism it endorsed — partial, not full engagement.
