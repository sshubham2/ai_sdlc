# Critique Review: Slice 080 harden-bc1-critical-rules-exit-gate

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-29
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively sound: all 8 findings are VALID with correct severities, the empirical mechanism verification (unchanged `return 1 if result.violations else 0` exit via appended violations) holds, and the Builder's B1/M1 fixes (canonical 5-leg PMI-1 enumeration in design.md + ADR-072; shippability row #85 rewritten to the acknowledgment contract) are correct on independent re-read. A second pass surfaces one MISSED finding of the *same class* the first Critic caught in M1 (rejected-design documentation persisting in a second surface — the repro test docstrings), plus one sub-threshold inaccuracy the B1 fix transferred into the B2 build-plan step (the version-sync test's four literal asserts mis-enumerated). Verdict EXTEND.

## Confirmed findings (VALID + correct severity)

- **B1** — confirmed Blocker. Canonical 5 legs verified against `tests/methodology/test_methodology_changelog.py:5239-5257` (VERSION, plugin.yaml, pyproject, `## vX` header) + AVFS-1 leg-5 separation (docstring 5230-5233); `pyproject.toml` would fail the renamed sync test if unbumped. Builder post-fix enumeration (design.md §Decisions + ADR-072 Consequences) is sound, MCFS-1 correctly called out as separate.
- **B2** — confirmed Blocker. Time-locked-deletion convention for the sync test (`test_methodology_changelog.py:5064-5069`) + cumulative entry-pins (4695-5178) verified; the rename-sync-test + add-new-entry-pin-pair split in the Build plan is correct.
- **B3** — confirmed Blocker. Standing-ack consequence correctly recorded in ADR-072; the slice cannot finish its own Step 6 without the ack + build-log attestation (hard build-time gate, not advisory).
- **M1** — confirmed Major. Rewritten row #85 (`architecture/shippability.md`) describes the acknowledgment contract precisely. Fix sound.
- **M2** — confirmed Major. `_format_human` diagnostic plan correctly converts the typo'd-ack silent-no-op into a visible line.
- **M3** — confirmed Major. `audit_slice` accumulates `result.applicable` across project loop (`build_checks_audit.py:483-494`) then global loop (496-511) before `return result` (513); carry-over early-return (471-473) short-circuits first. The global-source unit test the plan adds is genuinely required (repro only exercises project-source BC-PROJ-1).
- **m1** — confirmed Minor. Non-triggering in code; SKILL.md example-ordering concern.
- **m2** — confirmed Minor. Stale comments at `build_checks_audit.py:128-129` verified.

## Suspicious findings

None. Every first-Critic finding survives a closer reading. No over-reach on any of the 8.

## Missed findings

- **m-add-1 (Minor): the repro test docstrings document the REJECTED option-1 blunt-count design — the same class as M1, in a second surface.** `tests/bugs/test_bc1_critical_rule_exit_gate.py` module docstring + per-test docstrings described the contract as "returns nonzero … when `critical_applicable > 0`" (ADR-072 option 1, rejected). The first Critic caught this class in the shippability catalog (M1) but did not sweep the repro's own docstrings (also authored during /repro before the design fork). Tests still PASS under option 2 (no `--ack-critical` → BC-PROJ-1 unacknowledged → exit 1; zero applicable → exit 0), so documentation-only → Minor. **Proposed fix**: rewrite the repro docstrings to the acknowledgment contract in the SAME block as the M1 catalog rewrite; consider an `--ack-critical`-clears-it assertion.

## Severity adjustments

None. B1/B2/B3 each block a clean /build-slice or /validate-slice. M2's fail-CLOSED framing is right (diagnosability, not a wrong gate signal → Major not Blocker). B3-as-Blocker is not over-filed (hard build-time gate on the slice itself).

## Notes

High confidence. Empirically re-verified the exit mechanism, carry-over early-return placement (M3), canonical 5-leg vs 4-assert distinction (B1/B2), cumulative-vs-time-locked test convention (B2), and the live stale comments (m2). Calibration observation: the first Critic identified the rejected-design-documentation class (M1) but swept only one of two surfaces (catalog), missing the repro docstrings (m-add-1) — "found the class, under-swept the surfaces," sibling of the slice-074/075 RSAD-1 assertion-strength under-sweep (shippability row #74). Sub-threshold note (not filed): design.md L84 (B2 plan) mis-described the version-sync test's four literal asserts as "VERSION / plugin.yaml / pyproject / installed ai-sdlc-VERSION" — the actual 4th assert is the `## v0.NN.0` changelog header (leg 5 / installed ai-sdlc-VERSION is explicitly NOT asserted by that test). Self-correcting on first read of the test body; worth a one-word design.md fix.

**Builder post-review actions** (applied before TRI-1): m-add-1 repro docstrings rewritten to the acknowledgment contract; design.md L84 four-assert enumeration corrected to `## v0.NN.0` changelog header.
