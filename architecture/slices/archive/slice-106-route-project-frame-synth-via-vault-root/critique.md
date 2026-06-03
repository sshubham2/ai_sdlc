# Critique: Slice 106 route-project-frame-synth-via-vault-root

**Critic reviewed**: mission-brief.md, design.md, new ADRs (none — design deliberately mints none)
**Date**: 2026-06-03
**Result**: NEEDS-FIXES

## Summary
The core routing transform is empirically sound — `repo_root / VAULT_ROOT / "X"` is a verified pure no-op under the default relative `VAULT_ROOT` and flip-correct under an absolute override (pathlib RHS-reset). The allowlist-count, L44-orphan-literal, and L48/L304-non-match claims all check out against the real code. But the design's enumeration of touched tests is **incomplete in a build-breaking way**: it missed `test_emits_classified_inventory_with_evidence`, which asserts `MUST_REWRITE in classes` on the real-repo audit and will FAIL the moment production must-rewrite drops to 0 — directly defeating AC2 and AC5. There is also a real AC4/AC5/design scope tension over whether a "new regression test" + "new catalog row" exist or whether existing machinery is being reused.

## Findings

### Blockers (must address before /build-slice)

#### B1: Routing to 0 production must-rewrite breaks `test_emits_classified_inventory_with_evidence` (AC2/AC5 violated)
- **Claim under review**: design.md §"What's reused" / AC5 "Full methodology suite green"; design.md §3 lists only `_BASELINE` and §4 "test_must_rewrite_baseline_pinned … stays correct" as the `vault_flip_readiness_audit` test surface touched.
- **Issue**: `tests/methodology/test_vault_flip_readiness_audit.py:47` (`test_emits_classified_inventory_with_evidence`) runs `audit_root(REPO_ROOT)` and asserts `assert MUST_REWRITE in classes`. Critic executed the audit: the **only** 4 `MUST_REWRITE` occurrences in the entire repo are exactly the 4 `project_frame_synth.py` sites this slice routes (L121/122/185/194), and the tests surface **never** yields `MUST_REWRITE` (it remaps to `TEST_UPDATE_AT_FLIP`). After routing, `MUST_REWRITE in classes` is `False` → the test **fails**. APED-1 / Dim-9-algorithm-path miss: the design reasoned about `_BASELINE` (which goes `()` cleanly) but never traced the *other* real-repo assertion in the same module. Because shippability rows L117 (slice-100) and L118 (slice-102) both run the full `test_vault_flip_readiness_audit.py`, the break also reds the shippability catalog at /validate-slice.
- **Evidence**: `tests/methodology/test_vault_flip_readiness_audit.py:38-49`; executed `audit_root` shows 4 MUST_REWRITE occurrences, all `tools/project_frame_synth.py`, all `surface=production`; tests-surface MUST_REWRITE set empty (remap to TEST_UPDATE_AT_FLIP).
- **Proposed fix**: In the same slice, update `test_emits_classified_inventory_with_evidence` so it no longer asserts a real-repo `MUST_REWRITE` presence that this slice deliberately drives to 0. Replace the `assert MUST_REWRITE in classes` real-repo positive-presence assertion with a synthetic-fixture assertion (mirroring `test_new_unrouted_literal_fails_gate`'s tmp-file pattern), OR assert `TEST_UPDATE_AT_FLIP in classes`. Keep `ALREADY_SEAM_ROUTED in classes` + `DOC_EXAMPLE_SAFE in classes`. Enumerate as an explicit edit in design.md §"What's new", not discovered at build time.
- **Builder draft**: **ACCEPTED-PENDING** — design.md §"What's new" item 4 + §"Consequence chain" #3 now enumerate the synthetic-injected-literal rework of `test_emits_classified_inventory_with_evidence` (keep `ALREADY_SEAM_ROUTED`/`DOC_EXAMPLE_SAFE` real-repo asserts; move `MUST_REWRITE` proof to a tmp-file fixture mirroring `test_new_unrouted_literal_fails_gate`). The code/test edit applies during `/build-slice`, verified red-before / green-after. Excellent catch — verified build-breaker the design missed.

### Majors (address this slice)

#### M1: AC4 "regression test" vs AC5 "new catalog row" vs design "reuse existing machinery" — unresolved scope tension
- **Claim under review**: AC4 "A regression test pins that `project_frame_synth` resolves its vault files via `VAULT_ROOT` … proven non-vacuous by mutation (AP-5)"; AC5 "the AC4 regression test propagated into the catalog per RPCD-1/SCPD-1"; design.md §"Build-time checks": "add a new row only if a genuinely new test is introduced" and "Existing test_project_frame_synth.py fixtures are the standing guard."
- **Issue**: AC4 + AC5 read as promising a **new, named, mutation-proven regression test** plus a **new shippability row**. The design instead reuses existing machinery: `test_migration_site_allowlist_pinned` + `test_no_orphan_architecture_literal_in_migrated_tools`, both in `test_vault_root_constant.py`, which fire once `project_frame_synth.py` joins the allowlist. Critic confirmed no `project_frame_synth`-specific VAULT_ROOT regression test exists today. Per Wiegers, an AC must be unambiguously testable; the Builder cannot tell whether a new test+row is in-scope. The AP-5 mutation-proof obligation is real either way.
- **Evidence**: AC4/AC5 (mission-brief); design.md §"Build-time checks"; grep confirms no existing pfs-VAULT_ROOT test; `test_vault_root_constant.py:125-159` (orphan guard), `:290-312` (allowlist pin).
- **Proposed fix**: Reconcile in design.md: state AC4 is satisfied by the **existing** allowlist-pin + orphan-literal guards (begin guarding `project_frame_synth.py` once it joins the allowlist), **no new test file**, therefore **no new shippability row** (existing slice-068 row covers it). Reword AC4/AC5 to match, OR name a genuinely new test + its row. State the concrete mutation that proves non-vacuity and which guard reds.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief AC4/AC5 reworded this round + design.md §"AC4 / AC5 satisfaction" added: the existing slice-068 allowlist-pin + orphan-literal guards cover `project_frame_synth` once it joins `_MIGRATION_SITE_ALLOWLIST`; **no new test file, no new catalog row** (existing slice-068 row running `test_vault_root_constant.py` covers it). Mutation non-vacuity: revert one routed site → orphan-literal test reds AND baseline-pin reds. Harmonized mission-brief↔design in one block (TPHD-1/AP-17).

#### M2: Stale narrative in slice-100/slice-102 shippability rows + `test_production_baseline_unchanged_vs_slice100` (AP-13 consumer-reference propagation)
- **Claim under review**: design.md §"Build-time checks": "Count-literal fan-out (AP-10): grep test_vault_flip_readiness_audit.py (and any shippability row / narrative) for a 4 / 'project_frame_synth' literal … and repoint to 0 / empty."
- **Issue**: The design names the fan-out obligation but does not enumerate the specific sites, and two are load-bearing prose, not just counts. (a) Shippability row L117 (slice-100) prose "the 4 bare-`"architecture"` `/`-BinOp path-construction sites in `project_frame_synth.py` classify `must-rewrite-before-flip`" — stale post-routing. (b) Row L118 (slice-102) prose "verified to leave the production `_BASELINE` (4 `/`-BinOp sites) BYTE-IDENTICAL" — `_BASELINE` is now `()`. (c) `test_production_baseline_unchanged_vs_slice100` (L220) — name/comment assert "unchanged"; still passes (both empty) but misleading. (d) `_BASELINE` in-module comment `vault_flip_readiness_audit.py:163-170` narrates "The 4 bare-'architecture' … sites in project_frame_synth.py" — must reword.
- **Evidence**: shippability.md L117, L118; `test_vault_flip_readiness_audit.py:220-229`; `vault_flip_readiness_audit.py:162-171`.
- **Proposed fix**: Enumerate all four sites in design.md and repoint each; confirm the project's convention for editing archived/historical shippability rows in place vs appending. Run the AP-10 grep against `architecture/shippability.md`, `vault_flip_readiness_audit.py`, and `test_vault_flip_readiness_audit.py` for both `"4"`-as-must-rewrite-count and `project_frame_synth`.
- **Builder draft**: **ACCEPTED-PENDING** — design.md §"Build-time checks" now enumerates all four stale-narrative sites explicitly + flags the in-place-vs-append shippability-row convention check (resolve at build, don't guess). Repointed during `/build-slice`. Correct AP-13 consumer-reference catch.

### Minors (log; address if cheap)

#### m1: Stale "14-element" prose + the two-numbers-in-one-file trap
- **Claim under review**: design.md §2: "the comment (L41) + the `test_migration_site_allowlist_pinned` docstring (L291) say '14-element', but the live set is already 15 … slice-106 makes it 16."
- **Issue**: Correct (live count is 15 via AST), but the stale-count surface is wider: `test_full_pytest_baseline_preserved` (`test_vault_root_constant.py:184-203`) hard-pins `test_count == 15`. This slice adds **no new test function** to that module (only edits the allowlist set + comments + an existing docstring), so the `== 15` count-pin stays correct and must **not** be bumped. Two different numbers in one file (allowlist membership 16 vs test-function count 15) — FBCD-1 cross-number confusion risk.
- **Evidence**: `test_vault_root_constant.py:41` (comment), `:199-203` (`assert test_count == 15`), `:291` (docstring "14-element").
- **Proposed fix**: In design.md distinguish the two numbers: allowlist membership 15→16 (edit L41 comment + L291 docstring), test-function count stays 15 (do NOT touch L199).
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"Build-time checks" m1 bullet now explicitly distinguishes allowlist-membership 15→16 (edit L41/L291) from the test-function-count pin `== 15` (do-not-touch; this slice adds no new test function to that module).

#### m2: "no ADR" is defensible but should be stated against the supersession/decision test
- **Claim under review**: design.md §"Decisions made (ADRs): None."
- **Issue**: Emptying `_BASELINE` to `()` is the *completion* of the ADR-091 readiness program, not a new decision; routing the last file applies the ADR-065 seam; no convention broken. "no ADR" is correct, but per Dim-7 + the codebase's "deviations need an ADR" rule, worth a one-line justification pointing at the MEPD-1 EXCLUDE / mechanical-refactor posture (slice-068, slice-098 precedent).
- **Evidence**: design.md §"Decisions made"; CLAUDE.md "Deviations need an ADR"; slice-068 "MEPD-1 EXCLUDE posture."
- **Proposed fix**: Add one sentence: "MEPD-1 EXCLUDE posture — pure application of the existing ADR-065 seam + ADR-091 baseline; mints no rule, no audit surface, no behavior change; no new ADR (slice-068 / slice-098 precedent)."
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"Decisions made" now carries the MEPD-1 EXCLUDE one-line justification with the slice-068/098 precedent.

## Dimensions checked
- [x] Unfounded assumptions — **B1** (the "suite green" claim rested on an unverified test-enumeration; the missed real-repo `MUST_REWRITE in classes` assertion falsifies it). The "15 not 14" allowlist count and "L44-only orphan" claims were verified TRUE by execution.
- [x] Missing edge cases — none beyond findings: the flip case (absolute VAULT_ROOT) is correctly handled by pathlib RHS-reset (verified); default no-op is byte-identical (verified); missing source files already degrade via `_read` → None → WARN (unchanged).
- [x] Over-engineering — none: minimal 4-site routing reusing the existing seam; no new module, no speculative generality. Zero-row wiring matrix appropriate.
- [x] Under-engineering — **B1** (an AC's "suite green" element is undelivered because a breaking test was not accounted for); **M1** (AC4/AC5 design elements ambiguous).
- [x] Contract gaps — none: internal tooling, no endpoint/event/versioning surface. Exit-code contract (0/2, never 1) unchanged.
- [x] Security — none: no auth, no input-boundary, no secret/PII path introduced or altered; `_read` keeps `except OSError → None`. No silent fallback to a hardcoded `"architecture"` (VAULT_ROOT is the only source) — satisfies the must-not-defer.
- [x] Drift from vault — **M2** (slice-100 + slice-102 shippability row narratives and the `_BASELINE` comment carry stale "4 sites"; AP-13). Dim-7 strategic-direction fit: the slice is squarely ON the project's deliberate trajectory (project-frame names R-32 / external-vault flip as the active direction; this slice takes production must-rewrite 4→0, the M1 prerequisite). It does NOT retire R-32 (correctly scoped). No direction conflict.
- [x] Web-known issues — none novel. Verified pathlib's absolute-RHS-reset join semantics are documented + intentional (`p / abs` discards the left operand), confirming `repo_root / VAULT_ROOT / "X"` is flip-correct when VAULT_ROOT is overridden absolute, and a pure no-op when it stays the default relative `Path("architecture")`. Sources: docs.python.org/3/library/pathlib ; lukas-prokop.at filepath-join-behavior.
- [x] Cross-cutting conformance — **B1** headline (APED-1 / algorithm-path-conformance: design reasoned about `_BASELINE` but did not trace the sibling real-repo assertion; Critic executed `audit_root` to confirm). **m1** FBCD-1 cross-number-confusion (allowlist-size 16 vs test-function-count 15). **M2** AP-13/SCPD-1 consumer-reference propagation. Mutation-proof obligation (AP-5) real and now specified (M1 fix).

**Empirical commands the Critic ran** (re-runnable by the Builder): `python -m tools.vault_flip_readiness_audit` (4 production must-rewrite, all project_frame_synth L121/122/185/194); char-built replica of the orphan regex `["\']architecture[/"\\]` vs project_frame_synth.py (matched L44/121/122/185/194; L44 NOT skipped — line starts `frame =`; L48/L304 NOT matched — space-prefixed); AST count of `_MIGRATION_SITE_ALLOWLIST` = 15; `audit_root(REPO_ROOT)` confirming MUST_REWRITE comes ONLY from the 4 production sites; tests surface never yields MUST_REWRITE.

## Triage

**Triaged by**: user
**Date**: 2026-06-03
**Final verdict**: NEEDS-FIXES

Dual-review (DR-1): meta-Critic verdict **ACCEPT** — all 5 findings VALID, severities correct, no suspicious / no missed findings (see critique-review.md). User ratified all 5 Builder draft dispositions as-is.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Synthetic-fixture rework of `test_emits_classified_inventory_with_evidence` enumerated in design.md §What's-new #4 + §Consequence-chain #3; code edit at /build-slice (red-before/green-after). Meta-Critic confirmed true build-breaker + Blocker severity. |
| M1 | Major | ACCEPTED-FIXED | mission-brief AC4/AC5 reworded + design §"AC4/AC5 satisfaction": existing allowlist+orphan guards cover it, no new test/row (TPHD-1 harmonized). Meta-Critic confirmed no-new-row is correct per RPCD-1/SCPD-1. |
| M2 | Major | ACCEPTED-PENDING | 4 stale-narrative sites enumerated in design §Build-time-checks + convention-check flagged; repoint at /build-slice. |
| m1 | Minor | ACCEPTED-FIXED | design §Build-time-checks distinguishes allowlist-membership 16 vs test-function-count pin ==15 (do-not-touch). |
| m2 | Minor | ACCEPTED-FIXED | design §Decisions-made adds MEPD-1 EXCLUDE justification (slice-068/098 precedent). |
