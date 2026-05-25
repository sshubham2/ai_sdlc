# Critique Review: Slice 045 fix-install-pypi-package-name-and-stale-prose

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-18
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: ACCEPT

## Summary

The first Critic's review is sound. M1 (MEPD-1 discharge + precedent-surface correction) is correctly Major and the boundary call is defensible; m1 and m2 are correctly Minor with correct fixes. The Builder's applied fixes landed, did not relocate the flaw, and are precedent-faithful (RR-1 audit clean, verified live). No suspicious findings, no missed findings, no severity adjustments.

## Confirmed findings

- **M1 (MEPD-1 not discharged by name; precedent mis-cited to reflection.md)** — confirmed; Major is appropriate. Over-reach check: MEPD-1's literal trigger enumeration in `agents/critique.md:122` lists `skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`, the in-house audits — INSTALL.md is *not* literally enumerated. But MEPD-1's binding clause is "changes behaviour on an in-house methodology surface," and INSTALL.md is the INST-1 install recipe Claude executes verbatim — a behaviour-bearing in-house methodology artifact. Genuine boundary case, but MEPD-1's own defect class (`critique.md:124` "silently carries *neither* branch is a Major") makes discharging the safe and correct call, not over-reach. The precedent-surface half is unambiguously correct: `slice-040 reflection.md:40` states verbatim that the precedent-faithful record is the `risk-register.md` `**Retired**:` line, never reflection.md — the original design's "recorded in reflection.md" was factually wrong. M1 is VALID.
- **m1 (install_audit.py still hardcodes v0.20.0 — :232 reword must not assert currency)** — confirmed; Minor appropriate. Verified `tools/install_audit.py:3-4,8,42-43` still hardcodes the v0.20.0 canonical inventory; rewording :232 to "current" would over-claim against frozen code (brownfield code-is-truth). The accepted fix ("The audit reports any drift from its canonical inventory." — no literal, no "current") is correct.
- **m2 (AC4 prose targets under-specified, invisible to repro test)** — confirmed; Minor appropriate. Verified `test_install_md_correctness.py:32-38` reads `INSTALL_MD` only; README:69 / HTML:1050 are outside the test contract, so an exact-phrase pin is the right control. Accepted fix pins `…if present, else the \`graphifyy\` PyPI package)` for both.

## Suspicious findings

No suspicious findings. The over-reach probe on M1 concludes it is a defensible boundary call, not a false positive. The first Critic did not over-reach treating an INST-1 recipe behaviour change as MEPD-1-governed.

## Missed findings

No missed findings — first Critic coverage is complete. Independent re-application of all 8 dimensions:

- **Born-retired R-11 over-correction check**: NOT a finding. R-11 discovered+retired = slice-045 (same slice), unlike R-4/R-5/R-7 (discovered earlier, retired later) and R-6 (discovered slice-031, retired slice-043 — different slices, direct open→retired). RR-1 schema imposes no different-slice constraint; live audit verified clean (total 11, retired 8, violation_count 0). The defect was latent/long-shipped, surfaced at /query-design, permanent guard (shippability #45) lands same-slice — no open-risk window to track, so born-retired is faithful representation, not manufactured. R-11 self-documents the deviation ("born retired … as R-6"). Precedent-faithful.
- **EDIT-2 false-negative sweep**: NOT a finding. Four `v0.20.0` literals (lines 18, 26, 168, 232) are the complete set; AC2 blunt regex catches all four. Line 168 reword ("predating the `pyproject.toml` packaging") is factually true — `git log -- pyproject.toml` confirms pyproject.toml was introduced by commit `01b2a42 feat: INST-1 — source-independent install`, i.e. the pyproject.toml packaging *is* the v0.20.0/INST-1 change, so the reworded anchor is semantically equivalent and stays correct. Line 26 INST-1 anchor reword breaks no cross-reference (rule ID is the stable anchor; other INST-1 refs at lines 150, 185, 209 carry no version literal). No 5th staleness class escapes; line 144 already uses the derive-from-source pattern.
- **Freshly-minted-obligation blind-spot lens (slice-040/R-10 pattern)**: NOT a finding. MEPD-1 (minted slice-039) is not freshly minted relative to slice-045 (6 slices prior, exercised at slice-040/R-10) and the first Critic *did* invoke it by name as M1 — the blind-spot pattern did not recur. STP-1 (slice-044) — no state-transition surface in this docs-only slice. ADR-046 split-slice naming (slice-043) — slice-045 is a numeric non-split slice, N/A. No freshly-minted obligation missed by both design and first Critic.
- **Dimensions 1–8 independent pass**: Unfounded assumptions — none (plugin.yaml = 25 confirmed via grep, VERSION = 0.54.0, INSTALL.md:93 sole bare occurrence confirmed). Edge cases — mid-slice smoke correctly placed. Over/under-engineering — EDIT-3 structural-guard correct for static markdown. Contract gaps — graphify module/CLI unchanged, verified against `test_install_md_correctness.py:48` `graphify(?!y)`. Security — package-name fix removes a typosquat vector. Drift — M1/m1 cover it. Web-known — `graphifyy` confirmed against live PyPI. No dimension surfaces an unflagged concern.

## Severity adjustments

No severity adjustments. m1 correctly Minor — code-vs-doc asymmetry has no production-impact path (install_audit.py runs correctly against its frozen inventory; only risk is doc over-claiming, neutralised by the accepted fix). m2 correctly Minor — a sloppy descriptive-sibling reword has no install-correctness or repro-contract impact (AC4 explicitly outside the FAIL→PASS test contract). Both stay Minor.

## Notes

High confidence. Every factual claim verified against live on-disk files (RR-1 audit executed clean; plugin.yaml tool count grepped = 25; slice-040 reflection precedent read verbatim at `reflection.md:40`; MEPD-1 trigger enumeration read from `agents/critique.md:122-124`; line-168 pyproject.toml anchor confirmed via `git log`). The first Critic's calibration is good — it did NOT fall into the slice-040/R-10 freshly-minted-rule blind spot (invoked MEPD-1 by name as M1) and empirically executed the repro regexes (Dim-1 / APED-1-adjacent discipline).

**`/critic-calibrate` reservation (N=1)**: MEPD-1's literal surface enumeration in `agents/critique.md:122` does not include INSTALL.md / the INST-1 recipe. This slice establishes (correctly) that "in-house methodology surface" is read broader than the parenthetical list. If this recurs (N≥2), the enumeration should be widened to make the boundary explicit rather than relying on Critic judgment each time. Carry to /reflect calibration.
