# Critique Review: Slice 033 fix-skill-drift-test-crlf-normalization

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-17
**First-Critic verdict**: NEEDS-FIXES
**First-Critic finding profile**: 2 Blockers, 4 Majors, 2 Minors; all 8 dispositioned ACCEPTED-FIXED; provisional CLEAN pending TRI-1
**Dual-review verdict**: ADJUST

## Summary

The first Critic's review is substantively sound — B1, B2, M1, M2, M4, m1, m2 are all VALID with correct severities and the Builder's applied fixes are coherent and independently verified against live repo state. One severity miscalibration (M3 should be Minor, not Major) and one residual cross-document drift introduced by the B1/B2 fix (the AC5 changelog pin lacks an explicit minted RULE-ID, breaking naming-parity with the v0.46.0 `qd_1` precedent) require adjustment. No new Blocker/Major. The slice is **not** a slice-022 self-violation — shipping the changelog/version/CLAUDE.md propagation in-slice is the *opposite* of that defect.

## Confirmed findings (VALID, severity correct)

- **B1** (no methodology-changelog/version bump despite PMI-1 uniformity 007–032) — VALID, Blocker correct. Verified: VERSION=0.46.0, plugin.yaml `version: 0.46.0`, installed `ai-sdlc-VERSION`=0.46.0; v0.46.0 (QD-1) entry documents the required 4-part atomic bump. Builder's ADR-033 fix correctly retracts the misleading PMI-1-analogy (precedent = changelog+version BOTH shipped).
- **B2** (CLAUDE.md "MUST be byte-equal" left actively false) — VALID, Blocker correct. CLAUDE.md L33/L36 verified. Deferring an actively-false governing invariant to /reflect is the slice-022 defect class. In-slice propagation is right.
- **M1** (.gitattributes doesn't normalize already-CRLF tree; test only checks declaration) — VALID, Major correct. Builder decomposition (targeted `git add --renormalize` + AC1 comparator as the env-independent fix + working-tree-state test) is correct.
- **M2** (CAD-1 existing drift tests not bound as AC2 evidence) — VALID, Major correct. Both bound as AC2(b) PASSING + EOL-only complement added.
- **M4** (top-level shared module vs conftest convention needs ADR rationale) — VALID, Major correct. ADR-033 supplies sound rationale (2-sibling-subpackage consumer set; conftest is fixture-scoped; `pytest.ini python_files=test_*.py` won't collect it).
- **m1** (AC4 cp-masking procedural→property) — VALID, Minor correct.
- **m2** (;-split deferral handle) — VALID, Minor correct. Already tracked in risk-register R-5 "Secondary discovery"; R-8-at-/reflect commitment is a sufficient handle.

## Suspicious findings

None. Every first-Critic finding corroborated by independent verification (`git ls-files --eol` → `i/lf` blob / `w/crlf` tree; TF-1 audit vocabulary; v0.46.0 precedent). No over-reach.

## Missed findings

- **m-add-1 — RULE-ID / pin-test-name parity drift introduced by the B1 fix** — **Minor.** AC5's pin is `test_v_0_47_0_md_drift_eol_agnostic_entry_present_in_repo_and_installed`, but the verified v0.46.0 precedent is `test_v_0_46_0_qd_1_entry_present_in_repo_and_installed` (minted RULE-ID `qd_1` infix). The slice assigns NO explicit RULE-ID; `methodology-changelog.md` entry-format requires `**<RULE-ID> — <Rule name>**`. Per Wiegers (every requirement uniquely + consistently identified), the v0.47.0 entry needs an explicit RULE-ID and the pin name must derive from it for 007–032 cross-reference parity. Genuine residual drift the B1 fix itself introduced (framing-question (a)). Low severity (mechanical; caught by /drift-check + changelog-format inspection) but worth closing now, not at /reflect — RULE-ID gaps left unpinned recur (cf. R-5's own N+2 history).
  - **Proposed fix**: mint RULE-ID `EOL-DRIFT-1`; add it to ADR-033 + the v0.47.0 changelog entry header; rename the pin test `test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed`.
  - **Builder draft**: ACCEPTED-FIXED — RULE-ID `EOL-DRIFT-1` minted in ADR-033 + AC5 + design.md; pin test renamed; TF-1 plan + Verification plan harmonized in the same fix block (TPHD-1 sub-mode b).

- **m-add-2 — TF-1 "PASSING" status for the two bound CAD-1 regression tests** — **informational, NO action.** Verified against `tools/test_first_audit.py`: `_ALLOWED_STATUSES = {PENDING, WRITTEN-FAILING, PASSING}` (no BOUND/REGRESSION status); `--strict-pre-finish` requires all rows PASSING; PTFCD-1 requires each PASSING row's test file to exist (both already exist). PASSING is the only valid status; Builder's choice correct. Logged so TRI-1 does not re-litigate it.

## Severity adjustments

- **M3** (namespace-import proof cites wrong subpackage precedent) — **SEVERITY-WRONG: Major → Minor.** The first Critic's own text concedes the technical risk is "verified true empirically so NOT a blocker"; the fix is a documentation/citation correction with no production-impact path or design-soundness consequence. Per Hendrickson (severity tracks consequence, not embarrassment), this is a Minor. Disposition unchanged (still ACCEPTED-FIXED). Recorded so /critic-calibrate does not learn "cite-the-wrong-precedent = Major".

## 8-dimension independent re-application

1. **Requirements/AC (Wiegers)** — 5 ACs (≤5 ✓); AC1/2/3/5 bound to named tests; AC4 correctly a *property* of AC1. Residual: m-add-1 (RULE-ID unpinned).
2. **Architecture (Fowler)** — shared module collapsing 6 `_sha256` dups is sound; ADR-033 justifies location. Clean.
3. **Contracts (Newman)** — CAD-1 exit-code 0/1/2 explicitly UNCHANGED; only equivalence relation EOL-insensitive. `assert_md_forward_synced` well-specified. No regression.
4. **Security/integrity (McGraw)** — N/A runtime; self-hosting integrity covered by AC2 must-not-mask. `git ls-files --eol` confirms normalization narrows the equivalence class to exactly the spurious-CRLF case, not a general weakening. Sound.
5. **Error model** — path-attributed AssertionError + both normalized hashes; INSTALL.md hint; no raise on EOL-only. Diagnosable. Clean.
6. **Testability/TF-1 (Hendrickson)** — 2 AC1 WRITTEN-FAILING (live repro verified), new rows PENDING, 2 CAD-1 PASSING (vocabulary verified, m-add-2). Well-formed.
7. **Operability/blast radius (Newman)** — whole-vault renorm excluded; targeted renorm verified bounded (`i/lf` blobs → empty index diff). Framing-question (c) resolves clean: git-blobs-already-LF is empirically TRUE. ADR-033 reversibility=cheap accurate.
8. **Cross-document consistency (CAD-1/PMI-1/SUP-1)** — B1/B2 propagate to changelog v0.47.0 + 3-file atomic bump + CLAUDE.md + mirror pin. One residual: m-add-1. No SUP-1 violation (`supersedes: null` correct — introduces, not supersedes). No CAD-1 self-violation.

## Notes

Confidence **high** — every load-bearing claim independently verified: `git ls-files --eol` (`i/lf`/`w/crlf`, no current .gitattributes), `test_first_audit.py` status vocab + strict-pre-finish/PTFCD-1, the cited mirror `test_root_claude_md_branch_per_slice_rule.py` exists, v0.46.0 QD-1 atomic-bump precedent, VERSION/plugin.yaml/ai-sdlc-VERSION all 0.46.0, R-5 N+2 provenance. First-Critic calibration in this slice is healthy. Only genuine miscalibration: M3 (Major→Minor). m-add-1 is real Minor; close in-slice.
