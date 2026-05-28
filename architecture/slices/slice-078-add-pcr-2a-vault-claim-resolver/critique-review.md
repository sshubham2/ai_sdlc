# Critique Review: Slice 078 add-pcr-2a-vault-claim-resolver

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-29
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 3B/4M/9m findings are all VALID with appropriate severities. B1's parser-mismatch claim was rigorously verified (`parse_queue_md` genuinely absent from `slice_queue_writer.py`; `parse_queue_text` strips `Parallel-safety` per docstring at `slice_queue_claim.py:230-234`). B3's CLI dispatch site at L242-253 is genuinely load-bearing (without it `--resolve-soft` short-circuits VAULT_CLAIM to STOP before reaching `_regen_slice_queue`). B2's structural-incoherence diagnosis matches slice-024/014 precedent. Two missed concerns surface from independent re-review of the post-fix `design.md` Resolution algorithm — one a silent-drop edge case in step 3, one a step-3/step-4 disk-read sequencing race that silently breaks AC#1's loser-auto-re-pick contract in practice.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (parser mismatch): VALID; severity **Blocker** appropriate. Empirically verified — `tools/slice_queue_writer.py` function list (L124-830) shows zero parser; `parse_queue_text` at `slice_queue_claim.py:230-234` docstring strips PSQ-1 known fields including Parallel-safety. Builder's Option (b) inline file-local helper is the right fix; Option (a) (widening `slice_queue_writer.py` public API) would carry CSP-1 cross-spec parity propagation cost across 6+ downstream consumers — Option (b)'s single-file blast-radius is the right call.
- **B2** (single-direction repro): VALID; severity **Blocker** appropriate. "FAIL pre-fix → PASS post-fix in same module" IS structurally incoherent on a single post-build git state. Option (a) fix (post-fix-PASS test + build-log Events FAIL→PASS contrast + shippability row #N) is correct and matches slice-024/014 precedent. The shift from "tested" to "captured-in-prose-event-log" is RPCD-1/SCPD-1-compliant — shippability row pins the post-fix PASS as the never-silently-regress assertion; the pre-fix FAIL is a single point-in-time evidentiary record, not a continued contract.
- **B3** (CLI dispatch site): VALID; severity **Blocker** appropriate. `tools/parallel_conflict_resolver.py:243` guard `if cls is not ConflictClass.SOFT:` fires FIRST for VAULT_CLAIM; `_regen_slice_queue` only fires inside L264-269 SOFT branch via `pending_writes.append`. Without rewiring `resolve_soft_conflict`, the CLI `--resolve-soft` path (L986-1007) cannot reach the defense-in-depth backstop. Builder's ACCEPTED-FIXED scope (both L242-253 + L627-638) is complete.
- **M1** (tie-rate honest framing): VALID; severity **Major** appropriate. `tools/slice_queue_claim.py:629-633` confirmed second-precision (`%Y-%m-%dT%H:%M:%S` + offset; no `%f`). ADR-071 §Options Option 1 cons rewrite to honest framing is the right fix at the right scope. Upgrading `_now_iso8601_utc` to microsecond precision is correctly out-of-scope — it's a PSQ-2 sub-mechanism change requiring its own slice (ADR-067 format contract change + methodology-changelog entry + forward-compat with already-written second-precision claims).
- **M2** (em-dash vs hyphen): VALID; severity **Major** appropriate. Blast-radius audit independently confirmed: grep of `Soft-conflict resolution` literal across `tools/ tests/ skills/` returns exactly one consumer — the writer at `tools/parallel_conflict_resolver.py:891`. Zero downstream readers. Uniform-hyphen-space decision propagates cleanly with zero downstream blast-radius beyond to-be-written tests.
- **M3** (APED-1 pin literals): VALID; severity **Major** appropriate. SKILL.md L185-192 verified — L185 is a ~600-char paragraph; L192 mentions `VAULT_CLAIM` as fall-through. Naive `"VAULT_CLAIM" in skill_text` would falsely pass. Pin #1 + Pin #2 specification matches RSAD-1 + slice-074/075 aggregated lesson.
- **M4** (write semantics — winner-in-stage-2 demotion): VALID; severity **Major** appropriate. `_regen_slice_queue:614` `baseline_text = text_3 if text_3 else text_2` would silently demote a stage-2 winner without overlay. Resolution algorithm step 3 fix addresses the demotion — see M-add-1 below for an executability concern downstream of the fix.
- **m1, m2, m5, m6, m7, m8**: all VALID; severities **Minor** appropriate; Builder dispositions sound.
- **m3** (HEAD-SHA field forensic value): VALID OVERRIDDEN with sound rationale — section-type symmetry is load-bearing for forensic readers.
- **m4** (L192 cosmetic wording): VALID DEFERRED to bundled cleanup; legitimate voluntary-restraint pattern.
- **m9** (clock-skew detection signal): VALID ACCEPTED-PENDING; R-22 + queue-candidate is the right corrigibility hook.

## Suspicious findings

None. The first Critic's 3B + 4M + 9m set is empirically grounded, correctly scoped, and free of over-reach. Builder draft dispositions (14 ACCEPTED-FIXED + 1 OVERRIDDEN + 1 DEFERRED + 1 ACCEPTED-PENDING) match the meta-Critic's independent reading on every disposition.

## Missed findings

Two concerns surface from independent re-review of the post-fix `design.md` Resolution algorithm. Both downstream of the M4-prompted algorithm spec — fresh design surface that hadn't been reviewed yet.

### M-add-1: Resolution algorithm step 3 silent-drop when winner candidate block lacks `Risk-retired:` pivot

- **Issue**: design.md §"Resolution algorithm" step 3 invokes `_overlay_claims_on_queue_text(baseline_text, {winner.candidate_name: {"claimed_by": ..., "claimed_at": ...}})`. The interface shape IS compatible with the existing PCR-1 helper at `tools/parallel_conflict_resolver.py:670-688` (verified at L734-736: helper reads `claim.get("claimed_by")` / `claim.get("claimed_at")`). **However**, per PCR-1's slice-076 m6 / code-review fix: `_overlay_claims_on_queue_text:687` carries a silent-drop semantics — if the candidate's queue-text block lacks the canonical `- **Risk-retired:**` line (the post-emit insertion pivot), the new claim is silently dropped. Builder added loud APED-1 stderr at L751-759 for this case but does NOT escalate to STOP — the resolver would return `action="APPLIED"` with a silently-stale claim shipped. For PCR-2a's strict-newer-wins contract this is a load-bearing edge case: a malformed candidate block could silently carry over the stage-3 baseline's stale loser identity, defeating the M4 fix.
- **Severity**: **Minor** — the loud stderr makes the failure observable in build-log AND `- **Risk-retired:**` is canonically required by PSQ-1's 5-field writer (every well-formed candidate block has it; only a hand-edited malformed block exhibits the drop). Plausibly empty in practice today but not contractually guaranteed.
- **Framework**: Hendrickson edge-cases (malformed-input invariant) + APED-1 silent-default-on-malformed criterion.
- **Reference**: design.md §"Resolution algorithm" step 3; `tools/parallel_conflict_resolver.py:670-688`, L751-759.
- **Proposed fix**: design.md step 3 wording extended with a sub-clause: "After `_overlay_claims_on_queue_text` returns, defensively verify via `re.search(rf'### {re.escape(winner.candidate_name)}.*?Claimed-by:\\*\\* {re.escape(winner.claimed_by)}', overlaid, re.S)` that the winner's claim made it into the overlaid baseline. If the regex fails to match, return `ResolutionResult(action='STOP', conflict_class=VAULT_CLAIM, reason='overlay-silently-dropped — candidate block missing Risk-retired pivot; manual intervention required')` — converts the loud-stderr-but-still-APPLIED case into fail-closed STOP, preserving M4's contract integrity. Add a TF-1 row `test_overlay_silently_dropped_returns_stop` exercising a synthetic malformed candidate-block fixture (block lacks `Risk-retired:` line).

### M-add-2: Resolution algorithm step 3 + step 4 sequencing — disk-read race silently breaks loser-auto-re-pick in practice

- **Issue**: design.md §"Resolution algorithm" steps 3 + 4 + 5 sequence as: (3) build overlaid baseline text in memory; (4) `_pick_loser_replacement(repo_root, exclude_names)` reads `architecture/slice-queue.md` from disk; (5) atomic write of overlaid text + `git add` + `git rebase --continue`. **The disk-read in step 4 happens BEFORE the disk-write in step 5** — so step 4 reads the PRE-resolution queue file, which during a rebase-in-progress state contains git's `<<<<<<<` `=======` `>>>>>>>` conflict markers AROUND the conflicted section of `slice-queue.md` (the U-file by definition during VAULT_CLAIM rebase). `_pick_loser_replacement`'s candidate-iteration will encounter conflict-marker noise and silently fail to parse most candidates — the audit log will record `Loser auto-re-pick: none-available` even when the queue has plenty of valid candidates, silently degrading AC#1's resolution-quality contract.
- **Severity**: **Major** — affects core AC#1 correctness ("loser auto-re-picks the next-priority NON-OVERLAPPING unclaimed candidate"). The `_pick_loser_replacement(repo_root, exclude_names)` signature in design.md L11 + L12 + L101 + L115 all assume disk-read; this propagates through 4 sibling artifact citations (FBCD-1 sub-mode (a) consistency concern). In real-world VAULT_CLAIM scenarios `architecture/slice-queue.md` IS the U-file — the conflict-marker'd disk state is the dominant case, not the corner case.
- **Framework**: Hendrickson concurrency / TOCTOU (read-then-write race on a file actively being rebase-mediated); Newman atomicity (resolved-state must precede consumer-read).
- **Reference**: design.md §"Resolution algorithm" steps 3/4/5; `tools/parallel_conflict_resolver.py:602-614` (stage-read pattern); mission-brief.md AC#1.
- **Proposed fix**: design.md step 4 wording made explicit: "`_pick_loser_replacement(queue_text, exclude_names)` reads from the post-overlay in-memory `overlaid` string produced by step 3 — NOT from `architecture/slice-queue.md` on disk (which contains git's `<<<<<<<` conflict markers during the rebase-in-progress state)." Helper signature changes from `_pick_loser_replacement(repo_root, exclude_names)` → `_pick_loser_replacement(queue_text: str, exclude_names: set[str])` (drops `repo_root` — no disk I/O needed). Propagate the signature change to design.md L11 + L12 + L101 + L115 + Wiring matrix row + Resolution algorithm step 4 + Error model. Add TF-1 row `test_pick_loser_replacement_reads_resolved_text_not_disk` with fixture where disk holds conflict-marker'd text + in-memory holds resolved overlay; assert helper returns the correct disk-ignored result. This is the **load-bearing fix** — without it AC#1's loser-auto-re-pick is silently broken in practice.

## Severity adjustments

None. All 16 first-Critic findings have appropriate severities. M2's Major grade is correct (contract-gap fragility, not cosmetic — Windows smart-dash autocorrect is a real on-platform fail-mode per Bach). M1's framing-only fix at correct scope (microsecond-precision upgrade explicitly out-of-scope per PSQ-2 sub-mechanism change discipline).

## Notes

Meta-Critic confidence:
- **High** on confirmed findings (B1's empirical claims verified line-by-line; B3's CLI short-circuit verified at L243; M1's second-precision verified at slice_queue_claim.py:629-633; M2's blast-radius verified via cross-tree grep).
- **Medium-high** on M-add-2 (the disk-read-before-overlay-write race is a structural concern from reading the algorithm sequencing; possible the Builder's mental model assumed in-memory text and the design.md wording is imprecise rather than implementation defective — TRI-1 should confirm with Builder which path was intended).
- **Medium** on M-add-1 (silent-drop is real PCR-1 inheritance; loud-stderr makes it observable; escalating to STOP may be over-defensive — existing SOFT path tolerates the silent-drop without STOP).

Calibration observation: this is a **strong first-Critic review**. The first Critic correctly verified empirical claims (B1), identified structural-incoherence (B2), identified CLI-dispatch under-engineering (B3 — Builder's original draft pinned only the helper not the CLI-facing wrapper), and identified write-semantics contract gap (M4 — winner-in-stage-2 demotion). The two missed concerns are both downstream of M4's algorithm-spec fix — the meta-pass's job to interrogate the freshly-introduced spec found them. **Pattern signal for /critic-calibrate**: when a major-severity Critic finding triggers a Builder-added algorithm spec in the post-fix design, the meta-pass should re-interrogate THAT new spec specifically — the Builder's fix surface is fresh code that hasn't been reviewed yet.

Files referenced for grounding:
- `architecture/slices/slice-078-add-pcr-2a-vault-claim-resolver/{mission-brief,design,critique}.md`
- `architecture/decisions/ADR-071-mint-pcr-2a-vault-claim-resolver.md`
- `tools/parallel_conflict_resolver.py` (L80-203, L221-346, L367-384, L532-584, L587-645, L670-761, L842-917, L920-1014)
- `tools/slice_queue_claim.py` (L200-260, L610-635)
- `tools/slice_queue_writer.py` (function list)
- `skills/commit-slice/SKILL.md` (L170-209)
