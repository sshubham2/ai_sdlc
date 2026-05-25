# Critique: Slice 050 add-ai-sdlc-version-forward-sync-gate

**Critic reviewed**: mission-brief.md, design.md, ADR-052 (1 new ADR)
**Date**: 2026-05-19
**Result**: NEEDS-FIXES (pre-triage; final verdict set by user at TRI-1)

## Summary

The standalone-clone approach (ADR-052 Option 1) is sound and the MCFS-1 parallel is structurally faithful. However: the AC4 entry-pin is tautological/content-free for the AVFS-1 deliverable (recurring aggregated-lesson anti-pattern); the AC4 test-first mapping is incomplete (a planned `_shippability_consumer_propagation` pin is unmapped); the "trailing whitespace tolerant" comparator is unsafe and contradicts MCFS-1's actual CRLF-only semantics + the CSP-1 parity pin; the bootstrap self-application claim is materially weaker than asserted; the non-catalog-by-construction rationale was recomputed and **does not transfer** (the `essential` class keys on the changelog path only). All findings dispositioned ACCEPTED-FIXED.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC4 entry-pin is tautological/content-free for the AVFS-1 deliverable
- **Claim under review**: mission-brief AC4 / test-first row "a `test_v_0_58_0_avfs_1_entry_present_in_repo` entry-pin".
- **Issue**: Aggregated lesson: a content-bearing AC needs a CONTENT pin, not a presence/byte-equality pin (tautological green). Real precedents `test_v_0_53_0_mcfs_1_entry_present_in_repo` (test_methodology_changelog.py:2952-2977) + `test_v_0_54_0_stp_1_entry_present_in_repo` (:3041-3065) assert multiple slice-specific semantic literals. Neither mission-brief nor design.md specifies WHICH AVFS-1 literals the v0.58.0 pin must assert.
- **Evidence**: test_methodology_changelog.py:2952-2977, :3041-3065; aggregated lesson "A content-bearing AC needs a CONTENT pin".
- **Proposed fix**: Specify the required content assertions, mirroring STP-1/MCFS-1 depth: `"AVFS-1"`, `"ADR-052"`, `"supersedes nothing"`, plus a deliverable-distinguishing literal (the canonical attribution phrase and/or the "standalone clone, not folded into MCFS-1" decision). Add as explicit must-not-defer.
- **Builder draft**: ACCEPTED-FIXED — mission-brief AC4 + design.md "What's new" + must-not-defer now enumerate the required v0.58.0 entry-pin literals (AVFS-1 / ADR-052 / "supersedes nothing" / the canonical "NOT a slice regression" attribution phrase / the standalone-not-folded decision). FBCD-1-harmonized across both files.

#### B2: AC4 test-first mapping incomplete — `_shippability_consumer_propagation` pin unmapped
- **Claim under review**: design.md declares `test_v_0_58_0_avfs_1_shippability_consumer_propagation`; mission-brief test-first plan (8 rows) has no row for it.
- **Issue**: Every catalog-row-bearing slice ships BOTH `_entry_present_in_repo` AND `_shippability_consumer_propagation` pins (MCFS-1 2921/2980; STP-1 3024/3068). The propagation pin is an AC4 deliverable but absent from the plan → design.md/mission-brief FBCD-1 cross-file drift; an unmapped declared function surfaces at /build-slice pre-finish.
- **Evidence**: design.md "What's new" vs mission-brief test-first table; every catalog-bearing slice ships the propagation pin.
- **Proposed fix**: Add a test-first row AC4 → `test_methodology_changelog.py::test_v_0_58_0_avfs_1_shippability_consumer_propagation`; reconcile declared functions byte-identically across both files.
- **Builder draft**: ACCEPTED-FIXED — test-first plan row added; design.md + mission-brief reconciled (FBCD-1 sub-mode (a)).

#### B3: "Trailing whitespace tolerant" comparator unsafe + contradicts the verbatim MCFS-1 template & CSP-1 pin
- **Claim under review**: mission-brief AC1/AC2/must-not-defer "content-equal modulo trailing whitespace/EOL" / "trailing newline tolerant".
- **Issue**: The cited verbatim template `methodology_changelog_forward_sync.py::_normalized_bytes` (:105) does exactly `read_bytes().replace(b"\r\n", b"\n")` — CRLF→LF ONLY, no whitespace/newline strip. "Trailing whitespace tolerant" is strictly wider, would mask a malformed installed file (e.g. `0.57.0 \n`), and breaks the AC's own claimed CSP-1 parity with `_normalized_sha256` (also CRLF-only). Verified: in-repo `VERSION` = `b'0.57.0'` (no trailing newline), installed copied byte-identically via `cp` (INSTALL.md:141).
- **Evidence**: methodology_changelog_forward_sync.py:95-105; tests/skill_drift_equality.py::_normalized_sha256; INSTALL.md:141 (`cp` → byte-identical, trailing-newline tolerance unnecessary).
- **Proposed fix**: Adopt the verbatim CRLF-only comparator; rewrite AC1/AC2/must-not-defer to "content-equal modulo line endings (CRLF↔LF) only", preserving the verbatim-clone thesis + CSP-1 pin.
- **Builder draft**: ACCEPTED-FIXED — Option (a) adopted. All three sites (AC1, AC2, must-not-defer) rewritten byte-identically to "modulo line endings (CRLF↔LF) only"; CSP-1 parity to `_normalized_sha256` preserved; trailing-whitespace tolerance explicitly rejected (a `cp` of a no-trailing-newline file is byte-identical — tolerance would only mask corruption).

### Majors (address this slice)

#### M1: Bootstrap self-application claim materially weaker than ADR-052/mission-brief assert
- **Claim under review**: ADR-052 "self-applies at own Step 6 (post-bump installed==in-repo 0.58.0 → exit 0)"; mid-slice smoke "installed 0.57.0 == in-repo 0.57.0".
- **Issue**: The installed `ai-sdlc-VERSION` is written by the manual LLM-executed PMI-1 forward-sync — exactly the N=2-drift-prone leg AVFS-1 exists to gate. At slice-050 Step 6, in-repo = `0.58.0`; AVFS-1 exits 0 ONLY if the dev manually synced installed → `0.58.0`. The slice authoring the gate is the single most likely place for it to FAIL its own Step 6. Mid-slice smoke (`0.57.0==0.57.0` at ~50%) tells you nothing about Step-6 self-application (post-bump `0.58.0`).
- **Evidence**: methodology-changelog.md:256 (MCFS-1 bootstrap works because changelog leg IS reliably forward-synced; the ai-sdlc-VERSION leg's N=2 history is the slice's premise).
- **Proposed fix**: ADR-052 Consequences + build-slice bootstrap note: a non-zero AVFS-1 at slice-050's own Step 6 is the EXPECTED signal to perform/repair the installed-VERSION forward-sync, not a slice defect — re-run until exit 0. Add a pre-finish line: manually verify `~/.claude/ai-sdlc-VERSION` == `0.58.0` as part of the 4-part bump. Fix mid-slice smoke to acknowledge it tests pre-bump state only.
- **Builder draft**: ACCEPTED-FIXED — ADR-052 Consequences reworded (un-shipped same-slice ADR edit, not SUP-1 — slice-047 precedent); mission-brief pre-finish gate gains the explicit manual-verify-0.58.0 line; mid-slice smoke reworded to state it validates the pre-bump 0.57.0==0.57.0 state and is NOT a Step-6 self-application proxy; the Step-6-non-zero=expected-repair-signal note added for the build plan.

#### M2: WIRE-1 exemption invents a third `_wiring.py` file MCFS-1 does not have
- **Claim under review**: design.md proposes `test_ai_sdlc_version_forward_sync_wiring.py` citing "MCFS-1 test_mcfs1_module_is_non_catalog_relocation_proof precedent".
- **Issue**: MCFS-1 has exactly TWO test artifacts: the entry-pin in `test_methodology_changelog.py` + the regression suite (`test_methodology_changelog_forward_sync.py`) which CONTAINS the relocation-proof (:142-183) and discharges WIRE-1 by "suite existing+passing" (:11-16). There is no `_wiring.py` and no SKILL.md-wiring assertion test in MCFS-1. Citing MCFS-1 precedent for a structure MCFS-1 lacks is a tooling-doc-vs-implementation parity defect.
- **Evidence**: test_methodology_changelog_forward_sync.py:11-16, :142-183; MCFS-1 has no `_wiring.py`.
- **Proposed fix**: Collapse to the MCFS-1 two-artifact shape: relocation/non-catalog proof + the (new, AVFS-1-specific) SKILL.md-wiring assertion live IN the regression suite; drop the third file; stop claiming MCFS-1 precedent for the SKILL.md-wiring pin (acknowledge it as an AVFS-1 addition). Reconcile the AC3/AC4 test-first rows.
- **Builder draft**: ACCEPTED-FIXED — design restructured to MCFS-1's exact two-artifact shape: (1) `test_methodology_changelog.py` entry-pin + propagation pin; (2) `test_ai_sdlc_version_forward_sync.py` regression suite holding synced/warn/drift/usage/empty/whitespace/CSP-1-parity/relocation-proof AND the AVFS-1 SKILL.md-wiring assertion (in-repo SKILL.md reads → `clean`). Third `_wiring.py` dropped; test-first plan rows AC3/AC4 repointed; the SKILL.md-wiring pin documented as an AVFS-1 addition, NOT MCFS-1 precedent.

#### M3: non-catalog-by-construction rationale recomputed — does NOT transfer (essential keys on changelog path only)
- **Claim under review**: design.md/wiring-matrix: regression suite "NOT shippability-cited (m-add-2 parity) — a catalog row for an installed-reading fn self-violates essential-unregistered".
- **Issue**: Recomputed against the real audit: `_ESSENTIAL_SHAPES = ((".claude", "methodology-changelog.md"),)` (shippability_decoupling_audit.py:95-97) and `classify_fn` explicitly classifies OTHER `~/.claude/...` reads (incl. `ai-sdlc-VERSION`) as `clean`, NOT `essential` (:421-432, prose :27-34). So an `ai-sdlc-VERSION`-reading test would NOT trip `essential-unregistered`. The MCFS-1 m-add-2 mechanism does NOT transfer to this path — the stated rationale is factually wrong.
- **Evidence**: tools/shippability_decoupling_audit.py:95-97 (`_ESSENTIAL_SHAPES`), :421-432 + :27-34 (other home reads → `clean`), :514-525 (essential-unregistered fires only on the changelog shape).
- **Proposed fix**: Correct the rationale to the actually-correct reason: the regression suite reads the untracked, environment-mutable `~/.claude/ai-sdlc-VERSION` → it must NOT be a shippability Machine-cmd (slice-029/030A "rows must not depend on environment-mutable/untracked state" discipline), independent of essential-unregistered (which provably does not apply to this path). The negative-invariant test asserts row-absence for the environment-state reason.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's reused" + wiring matrix rationale rewritten: non-catalog because the suite reads untracked environment-mutable installed state (slice-029/030A discipline; aggregated lessons "rows must not depend on gitignored/environment-mutable state"), with an explicit note that `essential-unregistered` does NOT apply here (`_ESSENTIAL_SHAPES` is changelog-only — verified at shippability_decoupling_audit.py:95-97,421-432). The regression-suite negative invariant asserts the module is absent from every Machine-cmd cell on the environment-state ground.

#### M4: Empty-present semantics under-specify the whitespace-only-present edge
- **Claim under review**: must-not-defer "Empty-present ≠ absent → HALT".
- **Issue**: A whitespace-only present installed file (`b'\n'`, `b' '`, `b'\r\n'`) is the dangerous edge: under the (incorrect) trailing-whitespace-tolerant wording, `0.57.0 \n` vs `0.57.0` would false-sync. Under the verbatim CRLF-only comparator (B3) it correctly HALTs. The edge should be explicitly enumerated + tested.
- **Evidence**: methodology_changelog_forward_sync.py:152-161 (empty handled by byte inequality, no special branch); B3 dependency.
- **Proposed fix**: Add must-not-defer "whitespace-only-present → HALT (same class as empty-present)"; add a test-first row; note B3's verbatim comparator resolves it.
- **Builder draft**: ACCEPTED-FIXED — must-not-defer enumerates whitespace-only-present alongside empty-present; test-first plan gains `test_whitespace_only_present_installed_halts`; explicitly noted that B3's verbatim CRLF-only comparator makes this correct by construction (no special branch).

### Minors (log; address if cheap)

#### m1: ADR-052 reversibility "delete+revert+supersede" wording contradicts SUP-1
- **Issue**: ADRs are append-only (SUP-1); "delete" of an ADR is invalid. Reversal = delete-module + revert-SKILL.md/changelog/row + supersede-ADR-052-via-new-ADR.
- **Builder draft**: ACCEPTED-FIXED — ADR-052 Reversibility reworded to the SUP-1-correct path (supersede via new ADR; never delete an ADR).

#### m2: must-not-defer "trailing whitespace tolerant" self-contradictory (FBCD-1)
- **Issue**: Subsumed by B3; flagged separately because it sits in the hard must-not-defer contract. All three sites (AC1, AC2, must-not-defer) must be harmonized byte-identically.
- **Builder draft**: ACCEPTED-FIXED — folded into the B3 fix; all three sites rewritten byte-identically.

#### m3: row "#50" asserted without next-free recompute
- **Issue**: Convention is one-row-per-slice; #50 plausible but asserted without recompute.
- **Builder draft**: ACCEPTED-FIXED — recomputed: max existing shippability row = #49 (slice-049), next-free = #50 (verified mechanically). #50 is consistent across mission-brief/design/ADR-052; no change needed beyond recording the verified basis.

## Dimensions checked
- [x] Unfounded assumptions — B1, M1, M3, m3 (entry-pin adequacy / bootstrap / non-catalog mechanism / row# all asserted without recompute; M3's recompute overturned the stated mechanism)
- [x] Missing edge cases — M4 (whitespace-only-present); B3 (trailing-newline for a one-line semver file)
- [x] Over-engineering — none (standalone-clone is minimal blast radius; M2's third file was the only over-build, now removed)
- [x] Under-engineering — B2 (propagation pin unmapped), B1 (content-pin under-specified)
- [x] Contract gaps — B3 (comparator contract internally contradictory vs the verbatim template + CSP-1 pin)
- [x] Security — none (local read-only audit; no auth/network/secret/injection surface)
- [x] Drift from vault — m1 (SUP-1 append-only); ADR-051 4-part-bump path correctly applied; no active-ADR contradiction
- [x] Web-known issues — skipped (purely internal tooling; stdlib only; no external platform surface)
- [x] Cross-cutting conformance — B1 (recursive self-application: a forward-sync-gate slice must not pin its own deliverable tautologically), B2/m2/m3 (FBCD-1 cross-file byte-identity), M1 (the slice's own Step-6 is the highest-risk self-application site), M2/M3 (recompute against the real artifact, not the prose precedent — M3's recompute changed the design)

## Triage

**Triaged by**: user
**Date**: 2026-05-19
**Final verdict**: CLEAN

Reconciled across both passes: first Critic (`critique.md`, NEEDS-FIXES) + meta-Critic (`critique-review.md`, EXTEND — 0 suspicious, 0 severity adjustments, 2 missed findings added below as M-add-1 / M-add-2). User ratified all 12 Builder drafts as ACCEPTED-FIXED; M-add-1 mitigation = scoped option (a).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | mission-brief AC4 + must-not-defer + design.md§What's-new enumerate the required v0.58.0 entry-pin literals (AVFS-1 / ADR-052 / supersedes-nothing / attribution phrase / standalone-not-folded) — STP-1/MCFS-1 depth |
| B2 | Blocker | ACCEPTED-FIXED | test-first plan row added for `test_v_0_58_0_avfs_1_shippability_consumer_propagation`; design.md/mission-brief fn names reconciled byte-identical (FBCD-1) |
| B3 | Blocker | ACCEPTED-FIXED | verbatim CRLF→LF-only comparator adopted; AC1/AC2/must-not-defer/design.md/ADR-052 all rewritten byte-identical; CSP-1 parity to `_normalized_sha256` preserved |
| M1 | Major | ACCEPTED-FIXED | ADR-052 Consequences + mid-slice smoke + new pre-finish line: Step-6 non-zero = expected forward-sync-repair signal, not a slice defect; mid-slice tests pre-bump state only |
| M2 | Major | ACCEPTED-FIXED | collapsed to MCFS-1's two-test-artifact shape; third `_wiring.py` dropped; SKILL.md-wiring assertion documented as an AVFS-1 addition not MCFS-1 precedent |
| M3 | Major | ACCEPTED-FIXED | rationale corrected to environment-mutable-state (slice-029/030A); `essential-unregistered` shown inapplicable (`_ESSENTIAL_SHAPES` changelog-path-only, shippability_decoupling_audit.py:95-97) |
| M4 | Major | ACCEPTED-FIXED | whitespace-only-present enumerated in must-not-defer + test-first row; resolved by construction under the B3 comparator |
| m1 | Minor | ACCEPTED-FIXED | ADR-052 Reversibility reworded to SUP-1-correct (supersede via new ADR, never delete) |
| m2 | Minor | ACCEPTED-FIXED | folded into B3 — all comparator sites byte-identical |
| m3 | Minor | ACCEPTED-FIXED | recomputed: max shippability row = #49, next-free = #50 (verified) |
| M-add-1 | Major | ACCEPTED-FIXED | meta-Critic missed-finding (DR-1 EXTEND). design.md de-claims "sufficient"; scoped option (a): must-not-defer hand-verify installed reflect/SKILL.md + `/reflect` Discovered-gap nomination for future OSDG-1 extension (fold-into-OSDG-1 = out of scope this slice) |
| M-add-2 | Major | ACCEPTED-FIXED | meta-Critic missed-finding (DR-1 EXTEND). Added must-not-defer + pre-finish line for the `/build-slice` skill-drift forward-sync (OSDG-1 guarded-leg hard finish-gate) |
