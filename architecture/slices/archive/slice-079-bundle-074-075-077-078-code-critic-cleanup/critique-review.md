# Critique Review: Slice 079 bundle-074-075-077-078-code-critic-cleanup

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-29
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively sound. All 11 findings (B1, B2, M1, M2, M3, m1-m6) are VALID at the correct severity, and the empirical APED-1 clause-5 self-execution on B1 + B2 was rigorous and verifiable (meta-Critic re-ran the same grep paths — `_UNKNOWN_REASONS` at `tools/pulse_worktree_resolver.py:77-86` matches the canonical 8 keys cited in the ACCEPTED-FIXED design.md; all 9 encoded-I/O sites in `tools/slice_queue_writer.py` carry `encoding="utf-8"` at the cited line numbers). The ACCEPTED-FIXED edits landed in mission-brief.md (effort, AC#3, AC#5, verification-plan #5, Must-not-defer) and design.md (in-scope shape, Fix K, Fix L AND-logic, Fix O pragma, Fix S reframe, WIRE-1 Exemption, N=7 parenthetical, AC mapping 12-not-13, Contracts narrowed) as claimed. **One MISSED finding (M-add-1, Minor)** surfaces from independent re-review: design.md §"Contracts added or changed" mis-cited the pre-fix signature of `_format_vault_claim_audit_entry` as 2-arg (`diag, result`) when codebase reality at `tools/parallel_conflict_resolver.py:923-928` shows the actual pre-fix signature is 4-arg (`diag, result, timestamp, head_sha`).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1 (Fix K reason-keys mis-cited)** — confirmed; severity Blocker appropriate; APED-1 clause-5 grep at `tools/pulse_worktree_resolver.py:77-86` shows canonical 8 keys (`fresh-worktree-no-milestone` / `milestone-missing-in-active-and-archive` / `milestone-frontmatter-malformed` / `detached-head` / `dirty-worktree` / `merge-base-error` / `head-unresolvable` / `slice-folder-name-drift`) byte-equal to the ACCEPTED-FIXED design.md. Pre-fix list was indeed from a different tool (`branch_workflow_audit.py`). **Blocker severity correct** because Fix K without the actual contract keys would have produced a constant whose keys never match any caller's `reason` field — consumer SKILL.md lookup would silently fall through to fallback on every call, defeating the entire fix.

- **B2 (Fix S premise empirically false)** — confirmed; severity Blocker appropriate; all 9 encoded-I/O sites verified explicit at cited line numbers. Reframe to structural-pin AST-walker with fixture-mutation FAIL→PASS contrast is the right discharge. **Blocker severity correct** because original Fix S would have either (a) silently passed pre-and-post failing AC#5's "FAIL→PASS contrast" obligation, or (b) been a no-op fix shipping no actual byte-level change — either way structurally unmet against `shippability.md` discipline.

- **M1 (Fix K contract surface widening)** — confirmed; severity Major appropriate; demoting to MAP-ONLY per option-(a) preserves slice-077's contract surface without minting ADR-072. **Major (not Blocker)** because original helper+state-dict path was a viable design — just one requiring an ADR — and the Builder's ACCEPTED-FIXED choice resolves it via contract narrowing rather than escalation. Per Newman §contract-evolution, the narrowing path is the lower-risk discharge.

- **M2 (Fix O `(unavailable)` ambiguity)** — confirmed; severity Major appropriate; the "(or)" leaves Builder choice unspecified, which is the canonical design→code translation gap entry surface. The pragma:no-cover pick is the documented-defensive option.

- **M3 (Fix S regression-test unconstructable)** — confirmed; severity Major appropriate; coupled with B2's reframe.

- **m1 (WIRE-1 Exemption note)** — confirmed; Minor severity appropriate; resolved via Exemption column note. WIRE-1 audit will not flag the corpus-grep test once categorization is documented.

- **m2 (Fix L AND-vs-OR)** — confirmed; Minor severity appropriate; tightened to AND-only per slice-077 m6 original prescription. Verified: `_parse_worktree_porcelain` at `tools/pulse_worktree_resolver.py:128` treats `bare` as a single-token sentinel flag in its first block — the AND-check on `"bare" in block[0]` is correct porcelain semantics.

- **m3 (precedent-class N=6 vs N=7)** — confirmed; Minor severity appropriate; updated to "N=7 including slice-079" with arithmetic `N=6 prior + slice-079 = N=7` shown.

- **m4 (AC#3 13-vs-12)** — confirmed; Minor severity appropriate; corrected at mission-brief.md and design.md AC mapping table.

- **m5 (effort estimate 1d→1.5d)** — confirmed; Minor severity appropriate; mission-brief.md bumped with rationale.

- **m6 (shippability row enumeration deferred)** — confirmed; Minor severity appropriate; ACCEPTED-PENDING with Phase A handoff is a legitimate disposition (SCMD-1 + SRSC-1 structurally enforce catalog grammar; Phase A is canonical authoring time per slice-071 precedent).

## Suspicious findings

**None.** Every finding the first Critic filed was substantive and survived independent re-verification.

## Missed findings

One missed concern surfaces from independent re-review of design.md against the cited code.

### M-add-1: design.md §Contracts mis-cites the pre-fix `_format_vault_claim_audit_entry` signature (Minor — Wiegers §Specification Accuracy)

- **Issue**: design.md (pre-meta-fix) §"Contracts added or changed" stated: `old _format_vault_claim_audit_entry(diag: ConflictDiagnostic, result: ResolutionResult) -> str`. Actual code at `tools/parallel_conflict_resolver.py:923-928` shows the existing signature is `(diag: ConflictDiagnostic, result: ResolutionResult, timestamp: str, head_sha: str) -> str` — already 4-arg, not 2-arg. Proposed extension stated new shape `(..., winner: ClaimEntry | None, loser: ClaimEntry | None)` — making post-fix shape 6-arg (not 4-arg as L110's prose implied).
- **Why it matters**: at /build-slice Phase A, the Builder reading design.md verbatim would draft a 4-arg target signature, then discover at edit-time that the codebase already has `timestamp` + `head_sha`. Two possible bad outcomes: (a) silent deletion of `timestamp` / `head_sha` (regressing PCR-2a audit-format — `head_sha` is load-bearing per the audit row `## Vault-claim resolution - <ISO-8601 UTC>` section body); or (b) confused mid-build improvisation under design→code translation pressure (the canonical N=15 cumulative class the first Critic itself flagged in M2 reasoning).
- **Severity**: **Minor** (not Major). The actual code is correct, the proposed direction of the fix is correct, and the test plan row O is consistent with the right post-fix shape. The defect is purely in the design-meta prose about the pre-fix signature. Phase A's structural-pin tests will likely catch the gap empirically. But surfacing it now saves Phase A a translation-gap incident.
- **Proposed fix**: at design.md §Contracts, correct the old-signature citation to 4-arg `(diag, result, timestamp, head_sha) -> str` and the new-signature citation to 6-arg `(diag, result, timestamp, head_sha, winner, loser) -> str`. Update call-site shape to `_append_audit_log(repo_root, diag, result)` UNCHANGED (timestamp+head_sha+winner+loser are computed inside `_append_audit_log` near L1270-1277 before the dispatch at L1277).
- **Framework**: Wiegers (Software Requirements §Accuracy of References) + the slice's own MEPD-1 EXCLUDE posture which requires precise contract-surface citation.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"Contracts added or changed" updated to cite the actual pre-fix 4-arg signature at `tools/parallel_conflict_resolver.py:923-928` empirically verified by meta-Critic and re-verified by Builder. Post-fix shape is 6-arg. Call-site discharge: `_append_audit_log(repo_root, diag, result)` PUBLIC SURFACE UNCHANGED; winner/loser computed inside `_append_audit_log`'s existing scope (where `timestamp` + `head_sha` are already computed before the dispatch) — single-source-of-computation preserved, DRY goal of Fix O satisfied without widening `_append_audit_log`'s public boundary. §Components touched Fix O paragraph updated in lock-step with the signature citation.

## Severity adjustments

**None.** All 11 first-Critic findings are filed at the correct severity. The Blocker/Major/Minor partition matches the impact-path analysis (B1+B2 would have produced broken artifacts; M1-M3 would have produced ambiguous Builder choices; m1-m6 are documentation/observability/effort-estimate concerns).

## Notes

High confidence in this review. The first Critic's APED-1 clause-5 self-execution was the load-bearing catch — verifying empirical grep claims against the actual codebase reproduces the cited contracts byte-equal, which means the Critic's evidence chain holds end-to-end. The single MISSED finding (M-add-1) is a different concern class than the empirical-grep-validation that drove B1+B2 — it's a design-meta signature-citation drift that wasn't in the first Critic's APED-1 grep scope (the Critic grep'd constant names + encoding sites, not the formatter signature). That's a calibration observation worth recording for the per-slice reflection: **APED-1 clause-5 catches contract-source falsification when the proposed-fix prose cites a specific module/line, but doesn't sweep all design.md contract-surface prose for signature-shape accuracy against the live code.** A future calibration candidate (not for slice-079, just a watch-list note for `/critic-calibrate` after N=3 slices show the same pattern) might extend APED-1 clause-5 to "any contract-surface prose in design.md §Contracts that names a function signature MUST be APED-1-grep'd against the live source-of-truth signature before /critique exits." For slice-079 itself, this single Minor MISSED finding (M-add-1) is the only material delta from the first Critic's coverage; the verdict **EXTEND** reflects that surfacing rather than any substantive disagreement with the first Critic's pattern.
