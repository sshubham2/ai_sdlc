# Critique Review: Slice 030B complete-shippability-decoupling (v2 meta-review, DR-1)

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-17
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The v2 Critic's six findings (B1, B2, M1, M2, m1, m2) are all VALID with correct severities — every evidence claim independently verified against actual files (catalog header 5 cols; rows #8/#12 genuinely co-cite an essential entry-pin fn; `test_skill_md_pins.py` absent / `test_validate_slice_skill.py` present; row #28 two `;`-joined invocations w/ bare `python` + leading `Commands:` prose; allowlist constants at L380/391/392; `shippability_path_audit.py` L147/L152 = `cells[3]`/`len<5`). The split **genuinely converged** — not a 5th relocation; Builder D-3 PASS, substantive not cosmetic (spot-checked B1/B2/M2). One Major missed: **M-add-A** — the M1 fix asserts a per-segment prose-discrimination mechanism that is specified nowhere, while the only concrete shared artifact (`_TEST_PATH_RE`) provably cannot perform that discrimination. Verdict EXTEND.

## Confirmed findings

- **B1** — confirmed, Blocker. Verified rows #8/#12 co-cite incidental `test_slice_001_archive_still_fires_*` AND essential `test_v_0_23_0_*`/`test_v_0_27_0_*`; runner executes the row whole. Fix substantive (Intent/AC2 re-scoped per-fn + explicit #8/#12 non-goal + mid-slice HALT-still-fires eyeball). Stress-test #2 resolved: AC2 pass/fail is per-fn, #8/#12 row-fragility an explicit non-goal — verifiable, not ambiguous.
- **B2** — confirmed, Blocker. `ls`-verified: `tests/methodology/test_skill_md_pins.py` absent; `tests/methodology/test_validate_slice_skill.py` present (docstring pins validate-slice SKILL.md prose). Fix repoints correctly + TPHD-1 harmonized.
- **M1** — confirmed, Major. Row #28 = two `;`-joined invocations; single-token mandate would cross-contaminate `-k v_0_42_0` / drop the UTF8 surface. Grammar revision is a genuine improvement. Stress-test #1: relaxation does not reopen D-2 *in principle* — but see M-add-A for the unspecified enforcement locus.
- **M2** — confirmed, Major (fail-closed → Major not Blocker, sound). Allowlist constants verified at named lines; design's membership table faithful. Stress-test #3 resolved: `test_allowlist_membership_is_exactly` pins a fixed closed set by identity (trips loudly on rename) — does NOT re-curate; v1-M3 hand-list defect does not recur a level down.
- **m1** — confirmed, Minor. Absolute vs bare-`python` interpreter inconsistency real; canonical `<interp>` normalization correct.
- **m2** — confirmed, Minor. Reverse orphan sub-check = SCPD-1 orphan-catch made concrete; substantive.

## Suspicious findings

None. Every v2 Critic finding survived independent file verification; no over-reach.

## Missed findings

- **M-add-A (Major): SCMD-1's per-segment grammar-discrimination mechanism is asserted but unspecified — the M1 fix recurs the "claimed-more-than-delivered" pattern it was meant to close.** ADR-031 + design.md state `Machine-cmd` is "one or more `;`-separated grammar-conformant pytest invocations, prose-free … a leading `Commands:` … is a violation" and that "the grammar is net-new". But the net-new discriminator (split on `;`; per trimmed segment require an **anchored** full-match `^<interp> -m pytest tests/…` shape; reject leading barewords) is **specified nowhere** — design.md only prose-describes the grammar. The verified shared predicate `_TEST_PATH_RE = r"tests/\S+?\.py"` (shippability_path_audit.py L50), applied *after the first `pytest` keyword* (`_extract_test_tokens` L112-129), provably does NOT reject prose: `Commands: \`python -m pytest tests/x.py\`` passes the extractor unchanged. So the mechanism that makes the M1 relaxation safe is the *unwritten* net-new check; the only concrete commitment is a predicate that explicitly cannot do the discrimination. Same class as v2-B1 (claimed-more-than-delivered) relocated into the M1 fix's grammar claim. **Severity: Major** — spec-precision, in-slice-addressable (not redesign; grammar concept sound, enforcement locus unpinned). **Proposed fix**: design.md Data-model-deltas + ADR-031 Decision (a) specify the segment validator concretely — (1) split `Machine-cmd` on `;`; (2) each non-empty trimmed segment full-matches an anchored `^<interp> -m pytest (tests/\S+\.py(::\S+)?| tests/\S+ )…$` (final form at build); anchoring is what rejects a leading `Commands:`; (3) add a **TF-1 negative fixture** to the AC3 plan: a `Commands: \`…\`` leading-bareword cell MUST be a SCMD-1 violation AND a two-clean-`;`-separated cell MUST pass — proving the discriminator, not asserting it. (Current AC3 TF-1 rows pin neither the prose-rejection nor the `;`-clean-accept.)

## Severity adjustments

None. All six v2 Critic findings at correct severity; M2 Blocker-vs-Major reasoning sound.

## Notes

High confidence — all load-bearing claims verified against actual files (catalog rows, module presence/absence, allowlist constants at L380/391/392, path-audit indices L147/L152, `_TEST_PATH_RE` L50, RR-1 audit exit 0 / R-4 `mitigating`). Builder D-3 PASS independently confirmed (spot-checked B1/B2/M2 — all materially substantive). Stress-tests #2/#3/#4/#5 resolved in the fixes' favor: R-4 honestly `mitigating`, 030C charter concrete (3-step DoD), M-add-1 explicitly DEFERRED-not-closed. M-add-A is NOT a convergence failure or 5th relocation — the all-rows-derivation + read-shape predicate genuinely closes the slice-030 root — it is a precision gap *inside the M1 fix* (the safe-relaxation discriminator asserted, not pinned), in-slice-addressable, consistent with the v2 NEEDS-FIXES (not BLOCKED) calibration. Reservation: if left to build time it invites over-strict (breaks a future row) or under-strict (re-admits prose) — pinning the discriminator + negative fixture pre-`/build-slice` is cheap insurance the rest of the slice already models.
