# Critique: Slice 076 add-pcr-1-conflict-diagnostic-and-soft-regen

**Critic reviewed**: mission-brief.md, design.md, ADR-069 (new)
**Date**: 2026-05-28
**Result**: NEEDS-FIXES

## Summary

The graduated 3-class taxonomy is the right shape, the strictly-additive SKILL.md edit pattern is correct, and the fail-closed UNKNOWN/MIXED policy is well-grounded. But the slice carries (a) a wrong library-API citation (`parse_queue_text` does NOT live at `slice_queue_writer`), (b) a major mission-brief vs design+ADR drift on the SOFT file-set count (4 files vs 3), (c) a hand-waved "inline equivalent of `/archive` skill's algorithm" claim where the algorithm is actually a Haiku LLM dispatch, (d) an under-specified VAULT_CLAIM detection predicate that risks PSQ-2's same-candidate-claim race being silently auto-resolved by `write_slice_queue`'s union semantics — which is exactly what PCR-1's "STOP for VAULT_CLAIM" was meant to prevent, (e) an APED-1-executed Windows path-typing gap where `_SOFT_FILE_SET` membership checks against `str(Path)` produce backslashes that miss the forward-slash frozenset, and (f) several missing edge cases (git-show stage 2/3 on add-only-one-side, concurrent invocation, audit-log race). The 3-Critic stack should NOT be collapsed; each finding below is reachable only by inspecting the cited source.

## Findings

### Blockers (must address before /build-slice)

#### B1: `parse_queue_text` cited at wrong module — design.md misidentifies the library API location
- **Claim under review**: design.md "What's reused": "**`tools/slice_queue_writer.parse_queue_text()`** at `tools/slice_queue_writer.py`". ADR-069 § Resolution algorithm: "Candidates extracted via `parse_queue_text(git_show(":2:..."))` + `parse_queue_text(git_show(":3:..."))`".
- **Issue**: Executed `from tools.slice_queue_writer import parse_queue_text` returns `ImportError: cannot import name 'parse_queue_text' from 'tools.slice_queue_writer'`. The function is defined at `tools/slice_queue_claim.py:201` with signature `parse_queue_text(text: str) -> dict[str, dict[str, object]]`. Per the docstring (L230-234), `parse_queue_text` returns ONLY claim metadata — Source/Blast-radius/Parallel-safety/Effort/Risk-retired are NOT preserved. Therefore PCR-1 cannot rebuild the full candidates list from `git show :2:/:3:` via `parse_queue_text` alone (CCC-1 tooling-doc-vs-implementation parity).
- **Evidence**: `tools/slice_queue_claim.py:201`; `tools/slice_queue_writer.py:702` (internal import from slice_queue_claim); `tools/slice_queue_writer.py:622` (`_format_entry` consumes name/source/blast_radius/parallel_safety/effort/risk_retired keys); executed `from tools.slice_queue_writer import parse_queue_text` → `ImportError`.
- **Proposed fix**: (a) Correct citation: cite `tools.slice_queue_claim.parse_queue_text`. (b) Re-design the slice-queue.md SOFT-regen: take rebase-target's queue text (`git show :3:...`) verbatim as candidate baseline; use `parse_queue_text` against BOTH branches' versions for CLAIM-history merge only; dispatch via `write_slice_queue` which already merges claims via PSQ-2 newest-wins semantics. Candidates unique to the rebased branch are dropped — documented as next-/slice-regen-recoverable behavior, not a bug.
- **Builder draft**: ACCEPTED-FIXED — citation corrected at design.md "What's reused" § + ADR-069 § Resolution algorithm; algorithm redesigned per option (b). Both fix sites use rebase-target verbatim + claim-history merge.

#### B2: SOFT file-set drift — mission-brief AC3 + milestone L46 listed 4 files; design.md + ADR-069 list 3
- **Claim under review**: mission-brief AC3 enumerated 4 files (including methodology-changelog.md) + prescribed "methodology-changelog merge for changelog"; milestone L46 enumerated 4; design.md `_SOFT_FILE_SET` defined 3; ADR-069 § Decision explicitly excluded changelog with reasoning.
- **Issue**: FBCD-1 sub-mode (a) original-draft cross-file inconsistency on the most load-bearing axis of the slice. ADR-069 L73's reasoning (PMI-1 5-leg atomic-bump risk on concurrent bumps) is sound; mission-brief + milestone drifted from the /design-slice clarifying answer that locked changelog HARD.
- **Evidence**: mission-brief.md AC3 (original); milestone.md L46 (original); design.md L49 + ADR-069 L62-73 (original 3-file).
- **Proposed fix**: Sweep all 3 sites; mission-brief AC3 + milestone L46 now match design.md + ADR-069 with 3 files. Combined with B3 below, final state is 2 files.
- **Builder draft**: ACCEPTED-FIXED — sweep applied at mission-brief AC3 + milestone L46 (now both reflect the 2-file SOFT set after B3 reduction).

#### B3: Inline `_index.md` regen claimed "deterministic" but `/archive` is Haiku-LLM-dispatched
- **Claim under review**: design.md "What's reused": "**Existing `/archive` skill regen logic** for `architecture/slices/_index.md` — PCR-1 dispatches to a callable form. … PCR-1 implements an inline equivalent: scan + emit the index, mirroring the skill's algorithm." ADR-069 § Resolution algorithm: "Inline archive-scan: walk … (refactor to shared library out of scope) … idempotent and deterministic; inline equivalent avoids subprocess-to-Claude-skill round-trip."
- **Issue**: `skills/archive/SKILL.md:58` Step 3 is titled "Regenerate `slices/_index.md` via Haiku dispatch" per COST-1. The "Aggregated lessons" prose block is Haiku-synthesized from N archived reflections — non-deterministic, NOT a deterministic scan. PCR-1's claimed inline equivalent cannot reproduce Haiku's output; two parallel branches may have differently-synthesized lessons blocks with no "union of branches" answer.
- **Evidence**: `skills/archive/SKILL.md:58-67`; the Aggregated lessons block at `architecture/slices/_index.md:74+` is the very input THIS critique skill reads.
- **Proposed fix**: Option (b) — **REMOVE `_index.md` from `_SOFT_FILE_SET`**. SOFT reduces to 2 files (slice-queue.md + shippability.md). `_index.md` conflicts fall to HARD-class until PCR-2 (or user re-runs `/archive` post-merge to regenerate the Haiku-synthesized block). Document explicitly in ADR-069 § Decision.
- **Builder draft**: ACCEPTED-FIXED — option (b) applied. `_SOFT_FILE_SET` now `{slice-queue.md, shippability.md}` — 2 files. Test row for `_index.md` removed from TF-1 plan; `_regen_index` private helper removed from design's Public/Private functions list; resolution algorithm row removed; ADR-069's "deliberately NOT in SOFT-set" explanation extended to cover both `_index.md` (Haiku) and `methodology-changelog.md` (PMI-1 atomic).

#### B4: VAULT_CLAIM detection predicate under-specified — risks PSQ-2's `write_slice_queue` silently auto-resolving same-candidate-claim races
- **Claim under review**: ADR-069 § 3-class taxonomy: "VAULT_CLAIM | Sole U-file is `architecture/slice-queue.md` AND the only differences between branches' versions are `Claimed-by:` / `Claimed-at:` field lines on the same candidate"; design.md private helper `_extract_claim_diff` listed without predicate boundary. ADR-069 § Resolution algorithm: candidates "union by candidate name; claim-history preserved via PSQ-2 merge semantics (newest `Claimed-at:` wins on duplicates)".
- **Issue**: PSQ-2's `write_slice_queue` already merges same-candidate claims (newest-wins) at `slice_queue_writer.py:692-708`. If `classify_conflict` doesn't explicitly detect same-candidate-different-identity BEFORE dispatching `write_slice_queue`, the SOFT path silently resolves what PCR-2 reserved for timestamp-winner + light-Critic — exactly the slice-005 BC-GLOBAL-1 "pre-existing branch dominates" pattern (Dim 9 #1 algorithm-path-conformance).
- **Evidence**: ADR-069 § taxonomy + § Resolution algorithm (original); `tools/slice_queue_writer.py:692-708`.
- **Proposed fix**: (a) Tighten classify_conflict spec: detect same-candidate-different-identity (any candidate name in BOTH parsed claim dicts with DIFFERENT `Claimed-by:`) → return `VAULT_CLAIM` not `SOFT`. (b) Add explicit TF-1 row: `test_classify_conflict_returns_vault_claim_when_same_candidate_claimed_by_different_identities_across_branches`. (c) Defensive post-merge guard in `_regen_slice_queue`: re-parse resolved queue's claim dict; abort with `action: STOP, conflict_class: VAULT_CLAIM` if same-candidate-different-identity remains post-merge.
- **Builder draft**: ACCEPTED-FIXED — VAULT_CLAIM gate now explicit in ADR-069 § Resolution algorithm (gate step 3 of 5); design.md Resolution-algorithm § specifies the predicate; TF-1 row added; defensive post-merge guard documented in ADR-069 + design.md.

### Majors (address this slice)

#### M1: APED-1-executed: Windows Path() str-cast produces backslashes that miss forward-slash `_SOFT_FILE_SET`
- **Claim under review**: design.md `_SOFT_FILE_SET: frozenset[str]` (forward-slash strings); `ConflictDiagnostic.u_files: list[Path]`; `_extract_u_files` parses `git status --porcelain`.
- **Issue**: APED-1 battery executed locally — `python -c "from pathlib import Path; print(str(Path('architecture/slice-queue.md')))"` → `'architecture\\slice-queue.md'` (Windows backslash); `str(p) in _SOFT_FILE_SET` → `False`. Silent fail-CLOSED (no soft-regen attempted) — but the 5-session parallel-slice value proposition is DOA on Windows. APED-1 silent-disable / default-off-on-malformed criterion applies.
- **Evidence**: Executed APED-1 battery (Critic's own); CLAUDE.md "Platform: win32".
- **Proposed fix**: Type `_SOFT_FILE_SET` and `ConflictDiagnostic.u_files` as `list[str]` (raw porcelain forward-slash-keyed); OR keep `list[Path]` with `.as_posix()` normalization. Pin in regression test. JSON output: raw forward-slash strings throughout.
- **Builder draft**: ACCEPTED-FIXED — `_SOFT_FILE_SET` documented as forward-slash-keyed module constant; `ConflictDiagnostic.u_files` typed `list[str]` (NOT `list[Path]`); path-normalization convention added at design.md "Module-level constants" + "Path normalization convention" sections + ADR-069 § Path normalization convention. Regression test row `test_soft_file_set_membership_uses_forward_slash_keys_on_windows_paths` added to TF-1.

#### M2: Missing edge case — `git show :2:<file>` / `git show :3:<file>` when file added on one branch only
- **Claim under review**: design.md "Reads `git show :2:<file>` / `git show :3:<file>`"; AC3 test rows only enumerate "both branches have file with conflicting content".
- **Issue**: For a U-file added on ONE branch only (e.g., shippability.md row), `git show :2:` succeeds but `:3:` exits non-zero (or vice versa). Per Dim 2 + Dim 9 algorithm-path-conformance: stage-missing on one side is the load-bearing SOFT-class scenario, not edge-case.
- **Evidence**: design.md L43; mission-brief TF-1 rows L38-43 original; `tools/slice_queue_claim.py:236-237` (`if not text: return {}`).
- **Proposed fix**: (a) Catch `subprocess.CalledProcessError` from `git show :2:/:3:`; treat empty result as empty-content (equivalent to `parse_queue_text("")`'s `{}` return for queue, `[]` rows for shippability). (b) Add TF-1 rows for the add-on-one-side case for both SOFT files. (c) Stage-missing-on-both-simultaneously → UNKNOWN class (defense-in-depth).
- **Builder draft**: ACCEPTED-PENDING — design.md + ADR-069 § Resolution algorithm tables now have explicit "Edge cases" column documenting the stage-missing handling per the proposed fix. TF-1 row `test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_shippability` added. Implementation of the `subprocess.CalledProcessError` catch + the both-stages-missing → UNKNOWN check ships at /build-slice (code-level).

#### M3: Missing AC for `_index.md` regen — coupled with B3 resolution
- **Claim under review**: AC3 lists `_index.md` in SOFT (original); TF-1 row `test_resolve_soft_conflict_dispatches_to_index_regen_for_index_conflict` (original); design.md `_regen_index` private helper (original).
- **Issue**: Per B3 the underlying algorithm is conceptually broken (Haiku LLM dispatch). The current TF-1 row would pin a broken behavior. Coupled with B3 resolution.
- **Evidence**: mission-brief.md TF-1 plan original; design.md L52 (`_regen_index` original); ADR-069 L92 (original).
- **Proposed fix**: Per B3 option (b): delete the `_index.md` TF-1 row + `_regen_index` private helper + ADR-069 Resolution-algorithm row for `_index.md`. SOFT-set reduces to 2 files.
- **Builder draft**: ACCEPTED-FIXED — coupled with B3 fix. `_index.md` row removed from TF-1; `_regen_index` removed from design.md private helpers; ADR-069 resolution-algorithm `_index.md` row removed; ADR-069 explicit "NOT in SOFT" explanation added.

#### M4: Missing AC for UNKNOWN/MIXED class fail-closed behavior
- **Claim under review**: mission-brief Must-not-defer "Conflict-class fail-closed"; AC4 TF-1 rows cover SOFT/HARD/VAULT_CLAIM/MIXED only — no UNKNOWN; MIXED row covers SOFT+HARD only — no SOFT+VAULT_CLAIM.
- **Issue**: APED-1 silent-disable / default-off-on-malformed criterion applies, but the slice doesn't pin its own must-not-defer with a TF-1 row.
- **Evidence**: mission-brief.md L73 + L44-50 (original).
- **Proposed fix**: Add `test_classify_conflict_returns_unknown_when_rebase_state_empty` + `test_resolve_soft_conflict_returns_stop_on_unknown_class` + `test_classify_conflict_returns_mixed_when_soft_and_vault_claim_coexist`.
- **Builder draft**: ACCEPTED-FIXED — all 3 TF-1 rows added; ADR-069 § taxonomy table now includes the UNKNOWN row + explicitly pins these tests in the "Shipped in" column.

#### M5: Pre-finish gate count claim — self-withdrawn by Critic
- **Claim under review**: pre-finish gate "Must-not-defer list (8 items above)".
- **Issue**: Critic recounted and found the 8-count IS correct. Withdrew M5 as Major; substantive concern about the APED-1 calibration citation moved to m1.
- **Evidence**: Critic's own re-count in M5 body.
- **Proposed fix**: None as Major; see m1 for the substantive concern.
- **Builder draft**: OVERRIDDEN — Critic explicitly self-withdrew this finding as Major. Substantive concern (calibration citation) handled at m1.

#### M6: BC-PROJ-9 5-inventory — INSTALL.md tool-count is at TWO sites (L22 + L166), not one
- **Claim under review**: design.md "INSTALL.md tool-count literal NN → NN+1" (singular).
- **Issue**: INSTALL.md L22 + L166 both literally state "30 executable methodology tools"; updating only one fails INST-1 audit. CCC-1 v1.1 mechanical-table-vs-canonical-inventory failure mode.
- **Evidence**: `INSTALL.md:22` + `INSTALL.md:166`.
- **Proposed fix**: design.md explicit two-site enumeration: "INSTALL.md tool-count literal at L22 AND L166 (both `30 → 31`)"; TF-1 row asserting both sites synchronized.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" BC-PROJ-9 enumeration + design.md "What's reused" tools/install_audit + TF-1 row name (`test_install_md_tool_count_literal_is_at_31_at_both_sites_post_pcr_1`) all updated to explicit two-site form.

#### M7: SOFT-regen audit-log race + lazy-create non-atomic concerns
- **Claim under review**: design.md "Created lazily on first append" + ADR-069 § Audit log.
- **Issue**: Per Dim 6 concurrency: two parallel `/commit-slice --merge` sessions could race lazy-create or interleave appends. The cooperative-not-adversarial threat model (ADR-067) covers this, but the design.md "best-effort" prose doesn't explicitly call out the race-acceptance.
- **Evidence**: design.md L64-80 (audit log) + ADR-069 L97-101.
- **Proposed fix**: Document race-acceptance explicitly in ADR-069 § Audit log + § Adversarial model (audit log MAY interleave under concurrent --resolve-soft; acceptable per cooperative model; revisit at PCR-2 if empirically observable). Specify the atomic semantics (single `open(a, "a")` per append; deterministic check for header-write).
- **Builder draft**: ACCEPTED-FIXED — ADR-069 § Audit log expanded with explicit "Concurrency / race-acceptance" paragraph + atomic-semantics specification per cooperative-not-adversarial threat model.

### Minors (log; address if cheap)

#### m1: APED-1 "freshly-extended scope" citation in mission-brief.md L70 — verified via 2026-05-28 calibration commit `58fe17e`
- **Claim under review**: mission-brief.md L70 "Per the freshly-extended APED-1 scope from the 2026-05-28 calibration run".
- **Issue**: Critic couldn't find the calibration extension in this session's view. However, commit `58fe17e` (this conversation) DID apply the APED-1 scope extension to `agents/critique.md` Dim 9 #12. The citation is grep-verifiable post-commit, just not in the Critic's snapshot. Mission-brief was authored mid-conversation between calibration-log append and APED-1 patch apply.
- **Evidence**: Commit `58fe17e` "chore(critique): apply APED-1 scope-extension from 2026-05-28 calibration run"; `architecture/critic-calibration-log.md` "Calibration run — 2026-05-28 (post-slice-075)" appended at `7e34024`.
- **Proposed fix**: Replace citation with self-grounded justification per Critic's proposed text (Dim 9 #12 reference + executable battery enumeration). Keeps the methodology citation but avoids the "freshly-extended" timestamp ambiguity.
- **Builder draft**: ACCEPTED-FIXED — mission-brief.md Must-not-defer APED-1 entry now self-grounded with "Per Dim 9 sub-clause #12 (APED-1) §When reviewing a slice that mints any parse-time-evaluated pattern" + explicit battery enumeration.

#### m2: `ConflictDiagnostic.concerned_slices` Path-keyed dict — same root cause as M1
- **Claim under review**: design.md `concerned_slices: dict[Path, list[ConcernedSlice]]`.
- **Issue**: Coupled with M1 — `Path` keys serialize as backslash-paths via `str(Path)` on Windows in JSON output, drifting cross-platform.
- **Evidence**: design.md L14 (original); M1 finding.
- **Proposed fix**: Coupled with M1 — use `dict[str, ...]` with forward-slash keys; serialize raw.
- **Builder draft**: ACCEPTED-FIXED — coupled with M1; `concerned_slices` typed as `dict[str, list[ConcernedSlice]]` (forward-slash keys) in design.md "Frozen dataclasses" section.

#### m3: BC-PROJ-10 paired-pin substring enumeration not in design
- **Claim under review**: design.md "BC-PROJ-10 paired-pin tests" mentions test names but not the v0.73.0 entry-pin load-bearing substrings.
- **Issue**: Risk of entry-pin test pin-string drift from actual changelog entry text at /build-slice.
- **Evidence**: design.md L21 (original); v0.72.0 PSQ-3 entry-pin precedent.
- **Proposed fix**: Enumerate the 5 load-bearing substring anchors in design.md: `## v0.73.0` header / `PCR-1` / `ADR-069` / `parallel-conflict-resolution` / `mints a new rule on a new family axis`.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" BC-PROJ-10 paragraph extended with the 5-anchor enumeration per the proposed fix.

#### m4: design.md "PCA-1 unchanged" claim should reference the regression-guard audit
- **Claim under review**: ADR-069 "PCA-1 pipeline position unchanged".
- **Issue**: `tools/pipeline_chain_audit.py` is the regression guard at /build-slice Step 6 pre-finish; design.md doesn't reference it, risking future silent edits flipping `auto-advance: true`.
- **Evidence**: ADR-069 L116 (original); CLAUDE.md "PCA-1" reference.
- **Proposed fix**: Add a line to design.md "What's reused": "PCA-1 regression guard at `tools/pipeline_chain_audit.py` runs at Step 6 pre-finish".
- **Builder draft**: ACCEPTED-FIXED — design.md "What's reused" section now references `tools/pipeline_chain_audit.py` PCA-1 regression guard.

#### m5: R-21 risk-register entry for SOFT auto-regen failure-mode class
- **Claim under review**: ADR-069 § Reversibility anticipates "unforeseen failure mode of the SOFT auto-regen" but doesn't register it.
- **Issue**: Per RR-1 discipline: a known-anticipated failure class is a risk-register candidate.
- **Evidence**: ADR-069 L165 (original); `architecture/risk-register.md` (no R-21 currently).
- **Proposed fix**: Add R-21: "SOFT auto-regen produces semantically-different content from manual-resolve baseline at a corner case"; likelihood medium / impact medium / status active / candidate-fix "tighten classify_conflict OR extend SOFT-set audit OR fail-closed broader".
- **Builder draft**: ACCEPTED-PENDING — R-21 to be added to `architecture/risk-register.md` at /build-slice Phase A scaffolding step; mission-brief Dependencies sub-bullet to include R-21 reference post-add.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (parse_queue_text wrong module), B3 (`/archive` algorithm is Haiku not deterministic), B4 (VAULT_CLAIM predicate under-spec), m1 (calibration citation).
- [x] **Missing edge cases** — M2 (stage-missing on add-one-side), M4 (UNKNOWN/MIXED fail-closed not in TF-1), M7 (audit-log race), m5 (auto-regen-failure-mode unregistered risk).
- [x] **Over-engineering** — no findings: the dataclass surface is justified by the diagnostic AC2; CLI injection seams are standard per slice-067/068/072/073 precedent.
- [x] **Under-engineering** — M3 (`_index.md` regen no explicit AC), M4 (UNKNOWN/MIXED not in TF-1), M6 (INSTALL.md two-site pin), m3 (BC-PROJ-10 paired-pin substring enumeration).
- [x] **Contract gaps** — exit-code semantics well-specified vs NAW-1; JSON `--json` schema not formally documented (m2 / partial — addressed via design.md "Frozen dataclasses" forward-slash-string commitment).
- [x] **Security** — M7 (audit-log race); subprocess args are constant strings — no injection; U-file paths from porcelain trusted per cooperative-not-adversarial.
- [x] **Drift from vault** — B1 (CCC-1 tooling-doc-vs-implementation), B2 (FBCD-1 cross-file SOFT file-set), M6 (CCC-1 v1.1 INSTALL.md two-site). ADR-069 SUP-1 frontmatter correct; MEPD-1 (a) rule path correctly declared; PMI-1 5-part canonical shape correctly enumerated.
- [x] **Web-known issues** — Sources confirm `git show :2:/:3:` exits non-zero on stage-missing (motivates M2); `git rebase --continue` requires explicit `git add` of staged files (design correctly specifies). No novel issue.
- [x] **Cross-cutting conformance** — B1 (CCC-1), B2 (FBCD-1 sub-mode a), B4 (algorithm-path-conformance), M1 (APED-1 Windows path), M6 (CCC-1 v1.1). RSAD-1 annotation-pollution risk LOW for the slice's structural-pin literals; STP-1 clean (no risk-register status-bit flip); PTFCD-1+PTFFD-1 clean (concrete test names); MEPD-1 (a) 5-leg correctly enumerated.

## Graph notes

Graphify is available (`graphify-out/graph.json` exists). Did not run blast-radius queries because the new module `tools/parallel_conflict_resolver.py` does not yet exist on disk — graphify can only report on its declared consumers (none of which exist yet). The design's WIRE-1 matrix names two consumers; the consumer test path columns are concrete and verifiable post-build.

## Triage

**Triaged by**: user
**Date**: 2026-05-28
**Final verdict**: NEEDS-FIXES

Reconciled across both Critic passes (first-Critic critique.md + meta-Critic critique-review.md per DR-1; meta-Critic missed findings M-add-1 through M-add-5 added per /critique-review Step 5 hand-off).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | parse_queue_text citation corrected at design.md + ADR-069; slice-queue regen redesigned per textual claim-overlay (M-add-1 follow-on) |
| B2 | Blocker | ACCEPTED-FIXED | mission-brief AC3 + milestone L46 swept to match design+ADR (final state 2 files post B3) |
| B3 | Blocker | ACCEPTED-FIXED | _index.md dropped from _SOFT_FILE_SET (Haiku-LLM-dispatched); SOFT now 2 files; coupled fixes applied |
| B4 | Blocker | ACCEPTED-FIXED | VAULT_CLAIM gate explicit; defensive post-overlay guard documented |
| M1 | Major | ACCEPTED-FIXED | _SOFT_FILE_SET forward-slash-keyed; u_files: list[str]; path-normalization convention documented |
| M2 | Major | ACCEPTED-PENDING | Edge-cases column documents stage-missing; subprocess.CalledProcessError catch implements at /build-slice |
| M3 | Major | ACCEPTED-FIXED | Coupled with B3 — _regen_index helper removed |
| M4 | Major | ACCEPTED-FIXED | 3 TF-1 rows added (UNKNOWN class + STOP on UNKNOWN + MIXED SOFT+VAULT_CLAIM disambiguation) |
| M5 | Major | OVERRIDDEN | Critic explicitly self-withdrew this finding; vocabulary-gap methodology-refinement candidate queued at slice-079+ |
| M6 | Major | ACCEPTED-FIXED | INSTALL.md two-site (L22+L166) enumeration explicit; TF-1 row name reflects both-sites pin |
| M7 | Major | ACCEPTED-FIXED | ADR-069 § Audit log expanded with race-acceptance + atomic-semantics per cooperative-not-adversarial threat model |
| m1 | Minor | ACCEPTED-FIXED | mission-brief APED-1 citation self-grounded via Dim 9 sub-clause #12 reference |
| m2 | Minor | ACCEPTED-FIXED | Coupled with M1 — concerned_slices: dict[str, ...] forward-slash keys |
| m3 | Minor | ACCEPTED-FIXED | BC-PROJ-10 5-anchor enumeration (anchor (e) precedent-aligned per M-add-3) |
| m4 | Minor | ACCEPTED-FIXED | design.md "What's reused" references tools/pipeline_chain_audit.py PCA-1 regression guard |
| m5 | Minor | ACCEPTED-PENDING | R-21 risk-register entry to be added at /build-slice Phase A scaffolding step |
| M-add-1 | Blocker | ACCEPTED-FIXED | Phantom function `parse_target_queue_for_candidate_metadata` replaced with textual claim-overlay algorithm (new helper `_overlay_claims_on_queue_text`); no `write_slice_queue` round-trip for SOFT-resolve; TF-1 rows added; defensive post-overlay guard documented |
| M-add-2 | Minor | ACCEPTED-FIXED | Symmetric slice-queue stage-missing TF-1 row added |
| M-add-3 | Minor | ACCEPTED-FIXED | BC-PROJ-10 anchor (e) reverted to `mints a new rule` (3-word literal) per v0.68.0/v0.69.0/v0.72.0 precedent |
| M-add-4 | Major | ACCEPTED-FIXED | ADR-069 § Reversibility `3 named files` → `2 named files` (FBCD-1 sub-mode (b) sweep miss closed) |
| M-add-5 | Minor | ACCEPTED-FIXED | APED-1 enumeration extended to `_extract_claim_diff` + `_merge_shippability` predicates |
