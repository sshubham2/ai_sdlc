# Critique: Slice 078 add-pcr-2a-vault-claim-resolver

**Critic reviewed**: mission-brief.md, design.md, ADR-071; cross-referenced against `tools/parallel_conflict_resolver.py`, `tools/slice_queue_claim.py`, `tools/slice_queue_writer.py`, `skills/commit-slice/SKILL.md` L160-220, slice-076 archive, VERSION (0.73.0).
**Date**: 2026-05-29
**Result**: NEEDS-FIXES

## Summary

The design's core decision (strict-newer `Claimed-at` timestamp-winner with read-only loser-replacement suggestion, behaviorally-additive on PCR-1's atomicity infra) is sound and well-justified against the cooperative threat model. However, three concrete defects need addressing before /build-slice can proceed without rework: (B1) `_pick_loser_replacement` cannot read `Parallel-safety` via the parsers the design names — `parse_queue_text` strips it (slice_queue_claim.py:230) and `parse_queue_md` **does not exist** in `slice_queue_writer.py` (verified — function list at slice_queue_writer.py:124-830 contains zero parser); (B2) the AC#5 "FAIL pre-fix → PASS post-fix in one test module" pattern is structurally incoherent — pre-fix and post-fix are the same git working tree; (B3) AC#2 omits `resolve_soft_conflict()` L242-253, the actual CLI-facing dispatch site. The `claimed_at-tie` rule is more reachable than the ADR claims because `_now_iso8601_utc()` writes second-precision (slice_queue_claim.py:630). 4 majors + 9 minors below.

## Findings

### Blockers (must address before /build-slice)

#### B1: `_pick_loser_replacement` cannot filter by `Parallel-safety` via the parsers named in design.md

- **Claim under review**: design.md "Private helpers" → `_pick_loser_replacement(repo_root, exclude_names) — reads architecture/slice-queue.md via tools.slice_queue_writer parser; returns highest-priority candidate name whose Parallel-safety: NON-OVERLAPPING AND Claimed-by: field-line is absent`; "What's reused" → `tools/slice_queue_writer.py: parse_queue_md() candidate iterator + Parallel-safety field reader`.
- **Issue**: Two compounding defects empirically verified:
  1. `parse_queue_md` does not exist in `tools/slice_queue_writer.py`. The module exposes `write_slice_queue`, `format_queue_md`, `_format_entry`, `derive_active_slice_blast_radius`, `compute_parallel_safety` — no queue-text parser returning per-candidate dicts.
  2. `tools.slice_queue_claim.parse_queue_text` DOES exist but per `slice_queue_claim.py:229-234` docstring explicitly **strips all PSQ-1 known fields including Parallel-safety**: *"Known PSQ-1 fields (Source / Blast-radius / Parallel-safety / Effort / Risk-retired) are NOT returned"*. So even falling back, the helper has no way to read `Parallel-safety`.
- **Evidence**: `tools/slice_queue_writer.py` function list (no `parse_queue_md`); `tools/slice_queue_claim.py:229-234` docstring; mission-brief.md AC#1 test 3 requires the filter.
- **Proposed fix**: Option (b) — inline private helper `_parse_queue_candidates_for_replacement(text) → list[tuple[name, parallel_safety, is_claimed]]` inside `tools/parallel_conflict_resolver.py`. Doesn't widen `slice_queue_writer`'s public API; bounded blast-radius. Update design.md "What's reused" + "Private helpers" + wiring matrix in the same fix block (FBCD-1 sub-mode (a) original-draft cross-file consistency).
- **Builder draft**: ACCEPTED-FIXED — apply Option (b) edits to design.md "Private helpers" + "What's reused" + wiring matrix in this round; add `_parse_queue_candidates_for_replacement` as new file-local helper.

#### B2: AC#5 "FAIL pre-fix → PASS post-fix in one test module" is structurally incoherent

- **Claim under review**: mission-brief AC#5 + TF-1 rows 36-37 (`test_pre_fix_raises_soft_resolution_error` + `test_post_fix_returns_resolution_result` both PENDING in same module).
- **Issue**: A single test module cannot contain both a pre-fix-FAIL test AND a post-fix-PASS test exercising mutually-exclusive behavior on the same git state. Post-build either raises or returns — not both. Either the suite is RED forever or the pre-fix test is monkeypatched away (no longer a regression test of the actual gate).
- **Evidence**: mission-brief.md AC#5; TF-1 rows 36-37; design.md AC mapping row #5.
- **Proposed fix**: Option (a) — single-direction repro `test_vault_claim_gate_closed_returns_resolution_result` asserting the post-fix behavior. FAIL→PASS contrast captured empirically in build-log.md Events at pre-build / post-build SHAs. Shippability row #N pins the post-fix PASS. Matches slice-024 / slice-014 precedent.
- **Builder draft**: ACCEPTED-FIXED — rewrite AC#5 + collapse TF-1 rows 36-37 to one row in mission-brief; update design.md AC mapping.

#### B3: AC#2 omits the actual user-facing dispatch site `resolve_soft_conflict()` L242-253

- **Claim under review**: mission-brief AC#2 pins only `_regen_slice_queue` lines 627-637. Design.md L35 acknowledges `resolve_soft_conflict()` lines 242-253 needs extension but no AC / test-first row / wiring-matrix row covers it.
- **Issue**: The CLI path through `--resolve-soft` calls `resolve_soft_conflict`, NOT `_regen_slice_queue`. `resolve_soft_conflict:243` short-circuits on `if cls is not ConflictClass.SOFT:` → STOP. Even after `_regen_slice_queue`'s raise leg is swapped, this guard fires first. AC#3's "exit 0 + action: APPLIED" claim is unreachable from CLI without rewiring `resolve_soft_conflict`.
- **Evidence**: `tools/parallel_conflict_resolver.py:242-253` (guard); L267 (`_regen_slice_queue` call site); L986-1007 (CLI `--resolve-soft`); SKILL.md L185 (CLI invocation); design.md L35.
- **Proposed fix**: Rewrite AC#2 to cover BOTH sites. Add wiring-matrix row for `resolve_soft_conflict::VAULT_CLAIM dispatch`. Add a test-first row pinning the user-facing dispatch.
- **Builder draft**: ACCEPTED-FIXED — rewrite AC#2 in mission-brief; add resolve_soft_conflict dispatch test row + wiring matrix row in design.

### Majors (address this slice)

#### M1: Strict-newer `claimed_at` tie probability under second-precision timestamps is materially higher than ADR claims

- **Claim under review**: ADR-071 §Decision Option 1 cons "ties are rarer"; design.md "cooperative-not-adversarial threat model makes this corner-case rare".
- **Issue**: `tools/slice_queue_claim.py:630` `_now_iso8601_utc()` writes `%Y-%m-%dT%H:%M:%S` — second precision. Two cooperating sessions racing to claim the same hot candidate within a single wall-clock second produce byte-identical `Claimed-at` values. Tie window is ~1s wide, not microseconds. Doesn't break the design (ties fall to STOP) but invalidates the ADR's risk-acceptance reasoning. Honest defense: ties defer to PCR-2b because strict-newer covers the dominant case, NOT because ties are rare.
- **Evidence**: `tools/slice_queue_claim.py:630`; design.md L10; ADR-071 §Options.
- **Proposed fix**: Update ADR-071 §Options Option 1 cons + design.md L10 to honest framing.
- **Builder draft**: ACCEPTED-FIXED — update ADR-071 + design.md framing in this round.

#### M2: Audit-row section-heading distinction (em-dash vs hyphen) is a 1-character sentinel — collision risk

- **Claim under review**: design.md L12, L78: `## Vault-claim resolution — <ISO>` (em-dash) vs `## Soft-conflict resolution - <ISO>` (hyphen).
- **Issue**: Section-type distinction collapses to U+2014 vs U+002D at same column. Windows editor smart-dash autocorrect can flip silently. Three section-types compounds the fragility. Real distinction lives at the prefix word (`Soft-conflict` / `Vault-claim` / `Hard-conflict`), not the trailing separator.
- **Evidence**: design.md L12, L78; `tools/parallel_conflict_resolver.py:891` existing hyphen literal.
- **Proposed fix**: Use uniform `- ` separator: `## Vault-claim resolution - <ISO>` (hyphen). Pin literal `## Vault-claim resolution - ` is pollution-resistant per slice-075 lesson.
- **Builder draft**: ACCEPTED-FIXED — update design.md L12 + L78 + ADR-071 §Consequences.

#### M3: AC#3 SKILL.md structural-pin literal not specified — APED-1 pollution risk on L185-192

- **Claim under review**: design.md L46-48 + mission-brief AC#3 names the prose change but not the pin literal. L185 is a ~600-char single paragraph with co-occurring substrings; L192 closing summary mentions VAULT_CLAIM as fall-through.
- **Issue**: Per RSAD-1 + slice-074/075 aggregated lesson — UNIQUE-TO-THE-INVOCATION literal required. Naive `"VAULT_CLAIM" in skill_text` is satisfied by L192's closing summary even if L185 dispatch still routes VAULT_CLAIM to STOP. APED-1 demands execution against the actual prose.
- **Evidence**: `skills/commit-slice/SKILL.md:185-192`; slice-074/075 aggregated lessons.
- **Proposed fix**: Specify two pin literals in AC#3:
  - **Pin #1**: L192 closing summary must DROP `VAULT_CLAIM` from the "fall-closed-to-SOAD-1" enumeration AND ADD it to a "auto-resolved by PCR-2a" sentence.
  - **Pin #2**: L185 dispatch paragraph must contain `VAULT_CLAIM` co-occurring with `auto-resolves` (or analogous APPLIED-bound phrase) in the same line.
  - APED-1 execution: regex pre-tested against synthetic positive + negative on the actual L185-192 prose before /critique disposition.
- **Builder draft**: ACCEPTED-FIXED — specify pin literals in mission-brief AC#3 + design.md AC mapping in this round; APED-1 execution at build time.

#### M4: Write semantics resolution algorithm undefined — winner-in-stage-2 silently loses to baseline=stage-3

- **Claim under review**: AC#1 says "preserved identity is the entry with strictly-newer `Claimed-at`" but no design line specifies HOW the winner's identity is written when the winner is in stage 2 (slice branch) while baseline is stage 3 (rebase-target).
- **Issue**: PCR-1's `_regen_slice_queue:614` `baseline_text = text_3 if text_3 else text_2`. If winner is in stage 2, the design as written would have `git rebase --continue` ship stage-3's stale claim, silently DEMOTING the strictly-newer winner. The "strict-newer-wins" contract is then violated transparently.
- **Evidence**: `tools/parallel_conflict_resolver.py:614`; design.md L43, L60, L75, L121; no Resolution algorithm specified.
- **Proposed fix**: Add explicit Resolution algorithm to design.md:
  1. Parse `claim_history` → find strict-newer winner.
  2. Read stage-3 queue text as baseline (existing pattern).
  3. Apply `_overlay_claims_on_queue_text` with `{winner_candidate: winner_claim_data}` — overlays winner's identity onto baseline regardless of which stage held the newer claim.
  4. Atomic write + `git add` + `git rebase --continue` (existing stage-then-commit pattern).
  5. Audit-log append (best-effort).

  Parametrize AC#1 test 1 over both directions (winner-in-stage-2 + winner-in-stage-3).
- **Builder draft**: ACCEPTED-FIXED — add Resolution algorithm section to design.md; parametrize test row in mission-brief TF-1 plan.

### Minors (log; address if cheap)

#### m1: Line-number drift between mission-brief / design / ADR (627-637 vs 632-638)

- **Issue**: FBCD-1 sub-mode (a) — same code range cited as 627-637 (mission-brief AC#2 + design L29) vs 632-638 (design L122 + ADR-071 §Decision). Actual: defense-in-depth block runs L618-638.
- **Proposed fix**: Canonical range "L627-638" (predicate loop start + raise block); propagate to all 4 sites.
- **Builder draft**: ACCEPTED-FIXED — normalize to "L627-638" in this round.

#### m2: Multi-candidate collision detection helper shape not designed

- **Issue**: `_has_same_candidate_different_identity` returns `bool`, not a list. Multi-collision detection (Error model row) needs a list/count.
- **Proposed fix**: Add `_collect_same_candidate_different_identity(claim_history) → list[tuple[name, ClaimEntry, ClaimEntry]]` to wiring matrix; `_has_same_candidate_different_identity` becomes a thin `bool(_collect_...)` wrapper preserving the existing `classify_conflict` consumer.
- **Builder draft**: ACCEPTED-FIXED — add helper to wiring matrix + Private helpers list in design.

#### m3: Audit-row `Repo HEAD SHA pre-resolution` field — symmetry vs redundancy

- **Issue**: PCR-1's SOFT audit captures HEAD SHA because SOFT mutates files; VAULT_CLAIM mutation is smaller. Low-confidence Critic finding; flagged for symmetry-vs-redundancy consideration.
- **Proposed fix**: No action; preserve for SOFT/VAULT_CLAIM/HARD section-type symmetry.
- **Builder draft**: OVERRIDDEN — keep HEAD SHA field. Rationale: symmetry across the 3 PCR section-types is load-bearing for downstream log-readers + forensic value (the HEAD SHA pinpoints the rebase state independently of the timestamp); 1 field is not over-engineering.

#### m4: SKILL.md L192 forward-reference rewording — cosmetic

- **Issue**: Current L192 references stale "PCR-2 (slice-077)"; design.md proposes rewrite but past-tense "shipped" reads awkwardly.
- **Proposed fix**: Wording polish at build time.
- **Builder draft**: DEFERRED to `bundle-074-075-077-code-critic-cleanup` candidate. Rationale: cosmetic prose; not load-bearing on AC#3 dispatch contract; routes to the existing accumulated SKILL.md-prose-polish bundle per voluntary-restraint pattern (N=17 cumulative).

#### m5: AC#1 test 4 "none-available sentinel" — 3 distinct branches not pinned

- **Issue**: `_pick_loser_replacement` returns `None` on (a) queue empty, (b) all candidates non-parallel-safe, (c) all candidates claimed. Single test name covers one of three.
- **Proposed fix**: Split into 3 TF-1 rows: `test_no_available_when_queue_empty` + `test_no_available_when_all_overlapping` + `test_no_available_when_all_claimed`.
- **Builder draft**: ACCEPTED-FIXED — split TF-1 row 29 into 3 rows in mission-brief.

#### m6: methodology-changelog v0.74.0 entry-pin function name not pre-specified

- **Issue**: must-not-defer #5 commits to v0.74.0 entry + PMI-1 bump but doesn't pre-spec entry-pin function name shape `test_v_0_74_0_pcr_2a_entry_present_in_repo_and_installed` nor the 4-part atomic bump.
- **Proposed fix**: Expand must-not-defer #5 with entry-pin function name + 4-part bump enumeration.
- **Builder draft**: ACCEPTED-FIXED — expand must-not-defer #5 in mission-brief.

#### m7: `architecture/parallel-conflict-resolution-log.md` does not yet exist on disk — AC#4 byte-equality precondition

- **Issue**: PCR-1 lazy-creates; no soft-conflict resolved yet in production. AC#4 test 2 "byte-equality of prior rows" needs synthesized fixture.
- **Proposed fix**: Update design.md L52 to make absent-on-disk explicit; specify AC#4 test 2 fixture seeds a SOFT-row before the VAULT_CLAIM append (mixed-section append-only test).
- **Builder draft**: ACCEPTED-FIXED — update design.md L52 + clarify TF-1 row in mission-brief.

#### m8: Wiring matrix omits `resolve_soft_conflict` dispatch site

- **Issue**: Follows from B3 — `resolve_soft_conflict`'s VAULT_CLAIM dispatch branch is the user-facing path but no wiring row pins consumer-test pair.
- **Proposed fix**: Add wiring row: `resolve_soft_conflict::VAULT_CLAIM dispatch | tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py::test_resolve_soft_conflict_dispatches_vault_claim`.
- **Builder draft**: ACCEPTED-FIXED — add wiring matrix row in design.

#### m9: Clock-skew accepted-residual lacks corrigibility detection signal

- **Issue**: ADR-071 §Reversibility carves out clock-skew as accepted residual but no observable signal for recurrence detection.
- **Proposed fix**: Add risk-register R-22 entry "Cross-machine clock-skew in PCR-2a strict-newer rule" + queue candidate `add-claim-sequence-number-for-clock-skew-detection`.
- **Builder draft**: ACCEPTED-PENDING — R-22 entry + queue candidate added during /build-slice Phase G housekeeping; ADR-071 §Reversibility unchanged.

## Dimensions checked

- [x] Unfounded assumptions — B1 (`parse_queue_md` doesn't exist; `parse_queue_text` strips field — both empirically false), M1 (ties-are-rarer falsified by `_now_iso8601_utc` second precision), m1 (line-number drift across 4 sibling artifacts), m9 (clock-skew detection signal)
- [x] Missing edge cases — M4 (winner-in-stage-2 write semantics — Hendrickson concurrency), m2 (multi-candidate collision helper), m5 (3 distinct none-available branches), m7 (audit log absent on disk — Hendrickson empty), M2 (Windows smart-dash autocorrect — Bach platform)
- [x] Over-engineering — m3 (HEAD-SHA field redundancy — low-confidence, advisory); none other found
- [x] Under-engineering — B3 (AC#2 omits CLI-facing dispatch site), m8 (wiring-matrix row missing), m6 (PMI-1 entry-pin name not pre-specified)
- [x] Contract gaps — M4 (write-semantics resolution algorithm undefined), M2 (em-dash/hyphen sentinel fragility), m7 (lazy-create-of-second-section-type unpinned)
- [x] Security — none (cooperative threat model from ADR-067 inherited; no auth mediation; no claim-on-behalf writes; identity-as-claim + read-only loser-replacement correctly scoped)
- [x] Drift from vault — m6 (PMI-1 entry-pin atomic bump per MEPD-1 RULE-path); ADR-071 supersedes nothing; ADR-067 + ADR-069 inheritance correct per SUP-1
- [x] Web-known issues — N/A (in-house tooling on tested-stable surfaces — git CLI, subprocess, pathlib; ISO-8601 lexicographic ordering per RFC 3339 well-understood; no recent platform deprecation)
- [x] Cross-cutting conformance — APED-1/MCT-1 (M3 pin literal); FBCD-1 sub-mode (a) (m1 line-number drift); TPHD-1 (AC mapping clean); PTFFD-1 (12 TF-1 functions verified at /build-slice phase); SCPD-1 (additive only, zero propagation risk); MEPD-1 (rule-path + entry-pin per m6); RSAD-1 (M3 + B3 caught — slice authoring methodology refinement cannot ship via path that doesn't reach user-facing CLI); EOL-DRIFT-1/OSDG-1 (forward-sync committed in must-not-defer); self-validating-slice property acknowledged but dogfooding case explicitly out-of-scope (single-user developing PCR-2a unlikely to also have peer Claude session claiming concurrently)

## Builder fix block (TPHD-1 sub-mode (a) — applied in this round)

Edits made to mission-brief.md / design.md / ADR-071 in the same fix block as the Builder draft dispositions, per TPHD-1 sub-mode (a) original-draft cross-file consistency:

- **B1** (parser mismatch): design.md "Private helpers" + "What's reused" + Wiring matrix updated — `_pick_loser_replacement` reads via new file-local helper `_parse_queue_candidates_for_replacement` inside `tools/parallel_conflict_resolver.py`; false citations of `parse_queue_md` / `parse_queue_text` Parallel-safety access removed.
- **B2** (single-direction repro): mission-brief AC#5 rewritten to single PASS-post-fix function; TF-1 row 36-37 collapsed to one row; design.md AC#5 mapping updated.
- **B3** (CLI dispatch site): mission-brief AC#2 expanded to cover BOTH `resolve_soft_conflict()` L242-253 AND `_regen_slice_queue()` L627-638; design.md Components-touched expanded with `resolve_soft_conflict` modification; wiring matrix row updated to enumerate all three dispatch sites; TF-1 row added (`test_resolve_soft_conflict_dispatches_vault_claim_into_pcr_2a`).
- **M1** (tie-rate honest framing): ADR-071 §Options Option 1 cons rewritten with explicit citation of `tools/slice_queue_claim.py:630` second-precision strftime + honest "ties defer because strict-newer covers dominant case" framing.
- **M2** (uniform hyphen separator): design.md L12 + L78 + ADR-071 §Decision + §Consequences updated to `## Vault-claim resolution - <ISO>` (hyphen-space matching PCR-1 SOFT row).
- **M3** (APED-1 pin literals): mission-brief AC#3 expanded with explicit Pin #1 (L185 in-APPLY co-occurrence) + Pin #2 (L192 NOT-in-fall-closed regex); TF-1 rows split into 2 function-name pins; design.md AC mapping updated.
- **M4** (Resolution algorithm): design.md gains new "Resolution algorithm for VAULT_CLAIM" section (7-step contract); critical invariant of winner-identity-written-regardless-of-stage explicit; TF-1 row `test_timestamp_winner_when_newer_in_stage_2` added.
- **m1** (line-number drift): all 4 sibling citations normalized to "L627-638".
- **m2** (multi-candidate helper): `_collect_same_candidate_different_identity` added to design.md Private helpers + Wiring matrix; `test_multi_candidate_collision_returns_stop` added to TF-1.
- **m5** (none-available 3 branches): TF-1 row 29 split into 3 rows (`test_no_available_when_queue_empty` / `..._when_all_overlapping` / `..._when_all_claimed`).
- **m6** (PMI-1 entry-pin pre-spec): mission-brief must-not-defer #5 expanded with entry-pin function name + 4-part atomic bump enumeration.
- **m7** (audit log absent on disk): design.md L52 rewritten to "absent on disk as of slice-078 build start"; AC#4 test 2 TF-1 row name updated (`test_log_is_append_only_across_section_types`).
- **m8** (wiring matrix `resolve_soft_conflict` row): added (folded into B3 dispatch row).

Deferred / overridden:
- **m3** OVERRIDDEN — HEAD-SHA field kept for SOFT/VAULT_CLAIM/HARD section-type symmetry.
- **m4** DEFERRED — L192 forward-reference cosmetic wording bundled to `bundle-074-075-077-code-critic-cleanup`.
- **m9** ACCEPTED-PENDING — R-22 risk-register entry + queue candidate added during /build-slice Phase G (commit at must-not-defer items).

## Builder draft summary (pre-TRI-1)

| ID | Severity | Builder draft | Rationale |
|----|----------|---------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md "Private helpers" / "What's reused" / Wiring matrix updated; new file-local `_parse_queue_candidates_for_replacement` helper |
| B2 | Blocker | ACCEPTED-FIXED | AC#5 rewritten to single PASS-post-fix function; TF-1 collapsed |
| B3 | Blocker | ACCEPTED-FIXED | AC#2 covers both `resolve_soft_conflict` + `_regen_slice_queue`; wiring + TF-1 updated |
| M1 | Major | ACCEPTED-FIXED | ADR-071 §Options + design.md tie-framing honest about `_now_iso8601_utc:630` second-precision |
| M2 | Major | ACCEPTED-FIXED | Uniform hyphen-space separator across SOFT + VAULT_CLAIM + future HARD section-types |
| M3 | Major | ACCEPTED-FIXED | AC#3 specifies Pin #1 + Pin #2 with APED-1 execution at build time |
| M4 | Major | ACCEPTED-FIXED | Resolution algorithm section added; stage-2 winner test row added |
| m1 | Minor | ACCEPTED-FIXED | Canonical "L627-638" propagated |
| m2 | Minor | ACCEPTED-FIXED | `_collect_same_candidate_different_identity` added |
| m3 | Minor | OVERRIDDEN | HEAD-SHA field kept for section-type symmetry / forensic value |
| m4 | Minor | DEFERRED | L192 wording polish → bundle-074-075-077-code-critic-cleanup |
| m5 | Minor | ACCEPTED-FIXED | 3 distinct none-available test functions |
| m6 | Minor | ACCEPTED-FIXED | must-not-defer #5 enumerates entry-pin name + 4-part bump |
| m7 | Minor | ACCEPTED-FIXED | design.md L52 absent-on-disk explicit; mixed-section test |
| m8 | Minor | ACCEPTED-FIXED | wiring row folded into B3 dispatch row |
| m9 | Minor | ACCEPTED-PENDING | R-22 + queue candidate added during /build-slice Phase G |

## Triage

**Triaged by**: user
**Date**: 2026-05-29
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md "Private helpers" / "What's reused" / Wiring matrix updated; new file-local `_parse_queue_candidates_for_replacement` helper |
| B2 | Blocker | ACCEPTED-FIXED | AC#5 rewritten to single PASS-post-fix function; TF-1 collapsed; FAIL→PASS contrast captured empirically in build-log Events |
| B3 | Blocker | ACCEPTED-FIXED | AC#2 covers both `resolve_soft_conflict` L242-253 + `_regen_slice_queue` L627-638; wiring matrix + TF-1 expanded |
| M1 | Major | ACCEPTED-FIXED | ADR-071 §Options + design.md tie-framing honest about `_now_iso8601_utc:630` second-precision; microsecond upgrade correctly out-of-scope |
| M2 | Major | ACCEPTED-FIXED | Uniform hyphen-space separator across SOFT + VAULT_CLAIM + future HARD section-types; section-type distinguished at prefix word |
| M3 | Major | ACCEPTED-FIXED | AC#3 specifies Pin #1 (L185 in-APPLY co-occurrence) + Pin #2 (L192 NOT-in-fall-closed regex) with APED-1 execution at build time |
| M4 | Major | ACCEPTED-FIXED | 7-step Resolution algorithm added to design.md; `_overlay_claims_on_queue_text` ensures winner-identity writes regardless of stage origin |
| m1 | Minor | ACCEPTED-FIXED | Canonical "L627-638" propagated across mission-brief / design / ADR-071 |
| m2 | Minor | ACCEPTED-FIXED | `_collect_same_candidate_different_identity` added; `_has_same_candidate_different_identity` becomes thin wrapper |
| m3 | Minor | OVERRIDDEN | Section-type symmetry across SOFT/VAULT_CLAIM/HARD is load-bearing for forensic readers; 1 field is not over-engineering |
| m4 | Minor | DEFERRED | bundle-074-075-077-code-critic-cleanup — cosmetic L192 wording polish; voluntary-restraint N=17 pattern |
| m5 | Minor | ACCEPTED-FIXED | TF-1 row 29 split into 3 distinct test functions (queue-empty / all-overlapping / all-claimed) |
| m6 | Minor | ACCEPTED-FIXED | must-not-defer #5 enumerates entry-pin function name + PMI-1 4-part atomic bump |
| m7 | Minor | ACCEPTED-FIXED | design.md L52 absent-on-disk explicit; mixed-section append-only test seeded with synthesized SOFT row |
| m8 | Minor | ACCEPTED-FIXED | wiring row for `resolve_soft_conflict` dispatch folded into B3 wiring entry |
| m9 | Minor | ACCEPTED-PENDING | R-22 risk-register entry + queue candidate `add-claim-sequence-number-for-clock-skew-detection` added during /build-slice Phase G |
| M-add-1 | Minor | ACCEPTED-FIXED | Resolution algorithm step 3 defensive post-overlay `re.search` + STOP on silent-drop; test `test_overlay_silently_dropped_returns_stop` added |
| M-add-2 | Major | ACCEPTED-FIXED | `_pick_loser_replacement(queue_text, exclude_names)` signature change — in-memory text input avoids disk-read race during VAULT_CLAIM rebase-in-progress; test `test_pick_loser_replacement_reads_resolved_text_not_disk` added |
