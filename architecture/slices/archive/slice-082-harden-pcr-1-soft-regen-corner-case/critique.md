# Critique: Slice 082 harden-pcr-1-soft-regen-corner-case

**Critic reviewed**: mission-brief.md, design.md, ADR-074
**Date**: 2026-05-29
**Result**: NEEDS-FIXES

## Summary
The slice correctly targets R-21's two empirically-real silent-divergence vectors (the Critic verified against live source — the prelude-drop at `:1242` and the malformed-block claim-drop at `:830-841` both reproduce). But the 3-invariant equivalence class as originally specified was incomplete and partially mis-aimed: invariant #1 could not be evaluated from the named field-stripping helpers; invariant #3 was asymmetric and missed content-mutated non-numbered rows; and the atomicity/placement claim was sound only on an unstated fact. All addressable without redesign — four tightened in design.md now, two pending at build.

## Findings

### Blockers (must address before /build-slice)

#### B1: Invariant #1 re-parse cannot distinguish malformed-block drop from orphan drop using the named helpers
- **Claim under review**: design.md "calls back into `_parse_queue_candidates_for_replacement` / `parse_queue_text` / `_parse_shippability_rows` to re-read pending content"; invariant #1.
- **Issue**: To evaluate invariant #1 the guard needs `merged_claims`, the baseline `### <name>` headings, and the pending output's claim metadata. `_regen_slice_queue` returns only `(Path, str)` (`:666-727`) — `merged_claims`/`baseline_text` are computed inside and discarded. `_parse_queue_candidates_for_replacement` surfaces only `(name, parallel_safety, is_claimed)` (`:846-913`), no claim metadata. So the named helpers cannot supply invariant #1's inputs; the guard must re-derive them.
- **Evidence**: `tools/parallel_conflict_resolver.py:666-727`, `:846-913`; `tools/slice_queue_claim.py:201-303` (`parse_queue_text` returns claim metadata but strips PSQ-1 fields).
- **Proposed fix**: Re-derive `claims_2/claims_3/merged_claims` via `_extract_claim_diff` + `_merge_claim_dicts` on fresh stage reads; extract baseline `### ` headings via a direct regex; use `parse_queue_text` ONLY for pending claim-presence. Drop `_parse_queue_candidates_for_replacement` as an invariant-#1 helper.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"How the guard obtains its inputs (B1)" rewrites the re-parse plan exactly as proposed; `_parse_queue_candidates_for_replacement` removed from the invariant-#1 path.

### Majors (address this slice)

#### M1: Invariant #2 misses non-numbered (prelude) row content-mutation — a real R-21 divergence vector not caught
- **Claim under review**: invariant #2 (numbered-row set-equality) + invariant #3 (asymmetric discarded-stage check).
- **Issue**: The same-number HARD escalation (`:1232-1239`) and invariant #2 key on `^\|\s*(\d+)\s*\|` (`:1270`). A row whose first cell isn't a bare integer — `| 5,6 | … |`, `| 030C | … |` split-slice, annotated headers — lands in the *prelude*, never numbered. If such a row differs in content across stages, the same-number HARD escalation never fires and invariant #2 doesn't cover it. Invariant #3 covered it only against the *discarded* stage (asymmetric) — a content-mutated row that survived verbatim into the *kept* stage escaped all three invariants.
- **Evidence**: `tools/parallel_conflict_resolver.py:1270`; split-slice naming convention (CLAUDE.md / ADR-046) produces `030C`-style labels; empirical reproduction (`| 5,6 |` lands in prelude).
- **Proposed fix**: Make invariant #3 a symmetric set-equality over ALL non-blank prelude lines, OR document non-numbered cross-stage divergence as an out-of-scope residual.
- **Builder draft**: **ACCEPTED-FIXED** — design.md invariant #3 is now symmetric (`set(nonblank prelude_2) == set(nonblank prelude_3)`, and pending == that common set), catching content-mutation in EITHER stage incl. split/combined rows. The benign-difference→STOP tradeoff is documented and locked as correct fail-closed behavior.

#### M2: The orphan-claim "documented expected drop" exemption can hide a real R-21 divergence
- **Claim under review**: invariant #1 orphan exemption ("absent from baseline headings → expected drop").
- **Issue**: A candidate present in stage-2 with a claim, absent from stage-3 baseline, looks identical whether stage-3 legitimately dropped it (top-10 churn) OR stage-3 is truncated/corrupt (the R-21 silent-wrong class). The exemption assumes baseline is authoritative/complete; `baseline_text = text_3 if text_3 else text_2` (`:693`) has no completeness check beyond the both-missing raise (`:684-689`).
- **Evidence**: design.md invariant #1 + L137; `tools/parallel_conflict_resolver.py:693`, `:684-689`.
- **Proposed fix (Critic)**: An orphan claim is "expected" only if absent from BOTH stages' headings; a candidate with a heading in the discarded stage but absent from baseline → STOP.
- **Builder draft**: **ACCEPTED-PENDING (concern accepted; Critic's literal fix modified)** — implemented at build + `/reflect`. The Critic's specific remedy (STOP on cross-stage drop) is **rejected with rationale**: legitimate top-10 churn IS a cross-stage candidate drop and is the *common* case in parallel work — STOP-ing on it would fire constantly and defeat the entire SOFT auto-resolve mechanism. The happy-path-preserving remedy (now in design.md invariant #1 §"orphan-claim exemption + its bound"): do NOT STOP on cross-stage drops, but emit a **loud audit-log warning** (`cross-stage-claim-drop: <name> present in stage-N, absent from baseline`) so the truncated-baseline case is observable; register the genuinely-corrupt-baseline residual as a narrow named R-21 sub-residual scoped to PCR-2b's HARD path at `/reflect`. *(User: ratify whether loud-audit-not-STOP is the right line, or whether you want the stricter STOP despite the false-STOP cost on benign churn.)*

#### M3: Atomicity claim relies on an unstated fact about guard placement / `_VaultClaimDispatch` ordering
- **Claim under review**: "Unprovable → STOP, no writes (atomicity preserved since commit phase hasn't run)".
- **Issue**: The design's prose ("between the SOFT helpers producing pending_writes and the commit phase") was ambiguous about whether the guard sits before/after the `if not pending_writes` empty-check (`:302`), and didn't state the guard is read-only or that the dispatch/error handlers `return` before reaching it (loop order is git-status order, `:275`, not deterministic).
- **Evidence**: `tools/parallel_conflict_resolver.py:273-320`.
- **Proposed fix**: Pin the call-site (after `:308` empty-check, before `:316` write loop); state read-only; runs only on all-helpers-succeeded path; APED-1 case proving the guard does NOT run/mutate when dispatch/error fired.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"Guard call-site (M3)" pins the call-site exactly, states read-only + all-helpers-succeeded-only, and explains why loop-order is irrelevant. The APED-1 no-run-on-dispatch case is added to the build battery (mission-brief TF-1 / charter).

### Minors (log; address if cheap)

#### m1: ADR-074 / design.md disagree on the verdict-signal class
- **Issue**: design.md left "`_SoftEquivalenceError` (or reuse `_SoftResolutionError`)" open; a new sibling class would need its own `except` clause (catch-order invariant at `:371-381`) and risks silent fall-through if forgotten.
- **Proposed fix**: Reuse `_SoftResolutionError(message, ConflictClass.UNKNOWN)` — routes through the existing `except` with zero ladder change.
- **Builder draft**: **ACCEPTED-FIXED** — design.md "What's new" now commits to reusing `_SoftResolutionError`; the new-class option is explicitly rejected with rationale.

#### m2: Audit-log section variant `(equivalence-guard STOP)` is a new prose shape + STOP-path append is new behavior
- **Issue**: Log currently emits exactly two section types (`:1351`, `:1011`); a third could break a closed-set assertion. SOFT STOP path today does NOT log (`:356` runs only on APPLIED); a STOP-path append is new, and writes to the log file — confirm it's excluded from the "STOP unmutated" claim.
- **Proposed fix**: (a) grep `tests/` for a closed-set heading assertion before adding the variant; (b) clarify the must-not-defer excludes the best-effort audit append.
- **Builder draft**: **ACCEPTED-PENDING** — design.md Error model §"Scope of repo state unmutated" now clarifies (b): the audit-log append is best-effort and excluded from the tracked-conflict-state "unmutated" guarantee (consistent with the APPLIED-path precedent). The grep check (a) is performed at build before adding the third variant.

## Dimensions checked
- [x] Unfounded assumptions — B1 (re-parse helpers can't supply invariant #1 inputs — verified against source), m1 (verdict-class ambiguity). The two empirical divergence-vector claims (`:830-841`, `:1242`) were reproduced and are CORRECT.
- [x] Missing edge cases — M1 (non-numbered row content-mutation), M2 (truncated-stage masquerading as orphan drop), m2 (audit-log STOP-path append is new). Empty/both-missing already handled (`:684-689`, `:1218-1223`); O_APPEND audit concurrency contract unchanged.
- [x] Over-engineering — none. Single private predicate + one call-site; zero-row wiring matrix appropriate.
- [x] Under-engineering — M1/M2 (invariant set left named vectors uncovered, now closed/bounded). AC coverage traces: AC1→repro, AC2→guard, AC3→STOP+audit, AC4→happy-path battery, AC5→shippability pin. TF-1: confirm AC4 (happy-path-preserved, GREEN-throughout regression guard — not RED-first) and AC5 (shippability-pin) each have a genuine row.
- [x] Contract gaps — none. No public-signature change; `ResolutionResult` (`:129-136`) accommodates the new STOP without field change.
- [x] Security — none. Cooperative threat model (ADR-067); audit log append-only prose, no injection surface.
- [x] Drift from vault — none. ADR-074 supersedes nothing (correct — SELECTS R-21 fix-class (b), which R-21's register entry `:372` enumerates verbatim). APED-1/SOAD-1/ADR-069 citations check out.
- [x] Web-known issues — n/a (in-house git-rebase/markdown tooling; no external API surface).
- [x] Cross-cutting conformance — APED-1: Builder MUST empirically execute the guard's re-derivation path (B1), the non-numbered-row vector (M1), and the no-run-on-dispatch case (M3) against crafted fixtures — reasoning insufficient per the N=3 miss record. PTFCD-1: test path `test_pcr_1_soft_regen_equivalence_guard.py` doesn't exist yet (slice creates it). RSAD-1: self-validating-slice — the guard will be exercisable on this slice's own `/commit-slice --merge`. **MEPD-1 (resolve at build)**: ADR-074 refines PCR-1's SOFT path in-place without minting a new RULE-ID; confirm against the actual `test_methodology_changelog.py` assertion whether a changelog entry / version bump is required (slice-078 PCR-2a refined the same axis and DID bump v0.74.0 — but it minted a named sub-rule; this slice does not, so the documented-why-none path is plausible). Do NOT assume; check the test.

## Triage

**Triaged by**: user
**Date**: 2026-05-29
**Final verdict**: NEEDS-FIXES

Reconciles both passes (first Critic critique.md + meta-Critic critique-review.md). User ratified all Builder draft dispositions as drafted (2026-05-29).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §"How the guard obtains its inputs" — re-derive merged_claims via _extract_claim_diff/_merge_claim_dicts + regex headings + parse_queue_text for pending presence |
| M1 | Major | ACCEPTED-FIXED | design.md invariant #3 made symmetric (set(nonblank prelude_2)==set(nonblank prelude_3)); catches non-numbered row content-mutation incl. split/combined rows |
| M2 | Major | ACCEPTED-PENDING | Concern accepted; Critic's literal STOP-on-cross-stage-drop OVERRIDDEN — legit top-10 churn IS a cross-stage drop (common case), STOP would defeat SOFT. Remedy: loud audit-warn + named R-21 residual to PCR-2b; implemented at /build-slice + registered at /reflect. Meta-Critic confirmed this call correct. |
| M3 | Major | ACCEPTED-FIXED | design.md §"Guard call-site" pins after empty-check (:308) before write loop (:316), read-only, all-helpers-succeeded-only |
| m1 | Minor | ACCEPTED-FIXED | design.md "What's new" commits to reusing _SoftResolutionError(UNKNOWN); new-class option rejected |
| m2 | Minor | ACCEPTED-PENDING | Error-model unmutated-scope clarified (audit-log append excluded); grep tests/ for closed-set heading assertion performed at /build-slice |
| M-add-1 | Major (meta) | ACCEPTED-FIXED | design.md invariant #1 domain restricted to claimed_names={name: d.claimed_by}; excludes unclaimed candidates that would false-STOP happy path / break AC-4. APED-1 mixed-fixture pinned for build. |
