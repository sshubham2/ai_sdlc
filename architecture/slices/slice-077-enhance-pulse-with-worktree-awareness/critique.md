# Critique: Slice 077 enhance-pulse-with-worktree-awareness

**Critic reviewed**: mission-brief.md, design.md, ADR-070, slice-076 reflection, slice-074 reflection, slice-075 design.md, skills/pulse/SKILL.md, tools/parallel_conflict_resolver.py, tools/install_audit.py, tools/slice_queue_writer.py:248-280, tools/branch_workflow_audit.py::_resolve_default_branch + _SLICE_BRANCH_RE, architecture/slices/_index.md "Aggregated lessons" (L74-200)
**Date**: 2026-05-28
**Result**: NEEDS-FIXES (provisional; final after TRI-1)

## Summary

Critic returned 4 Blockers / 9 Majors / 6 Minors — higher than slice-076's 16-finding pass-1 because slice-077 carries multiple defects that immediately-preceding slices' published lessons should have prevented (B1 in particular: slice-076 reflection explicitly forbade `(manual)` TF-1 rows; slice-077 ships one anyway). The core design (worktree-state override + 4-state taxonomy + drift-flag suppression) is sound; the defects are textual / cross-file-consistency / under-engineered-edge-cases rather than design-level errors. Builder applies all 4 Blockers + 8 of 9 Majors + 5 of 6 Minors as ACCEPTED-FIXED in-band before /critique-review; 1 Major (M1) is ACCEPTED-FIXED via precedent-rationale rewrite (NOT promote-to-INCLUDE — see disposition); 1 Minor (m4) is DEFERRED to the queued `parallel-slice-family-parity-audit` slice (N=3 extraction trigger).

## Findings

### Blockers (must address before /build-slice)

#### B1: TF-1 plan row #5 cites `(manual)` as Test path — PTFCD-1 grammar will refuse the flip to PASSING

- **Claim under review**: mission-brief.md L50: `| 5 | end-to-end regression | (manual) | full pytest + shippability + 14+ Step-6 audits | PENDING |`
- **Issue**: slice-076 reflection L24 explicitly logged this exact defect class with the canonical fix ("any meta-row for end-to-end checks should be PENDING-by-design or removed; codified in build-log Summary table; TF-1 grammar enforces the discipline"). Slice-077 ships the same defect class three days later.
- **Evidence**: `architecture/slices/archive/slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen/reflection.md:24`; `tools/test_first_audit.py` PTFCD-1 grammar.
- **Proposed fix**: Remove row #5 from TF-1 plan; capture the end-to-end invariant in mission-brief's Pre-finish gate + Verification plan (already present). Match slice-076 in-band fix verbatim.
- **Builder draft**: **ACCEPTED-FIXED** — remove row #5 from mission-brief.md L50 TF-1 plan; end-to-end invariant already covered by mission-brief's "Pre-finish gate" section. Fix at mission-brief.md L50.

#### B2: design.md L89 error model lists wrong argparse flags — copy-pasted from PCR-1

- **Claim under review**: design.md L89: `**Exit 2** — malformed CLI args (argparse-driven; '--diagnose' + '--classify' + '--resolve-soft' mutually-exclusive group or unknown args).`
- **Issue**: `--diagnose / --classify / --resolve-soft` are `parallel_conflict_resolver.py`'s flags (verified at L946-948). Slice-077's actual CLI per design L9, L87, L143 + mission-brief L28 is `--detect / --classify`. RSAD-1 / FBCD-1 sub-mode (a) cross-file consistency drift.
- **Evidence**: design.md L89 vs L87, L143; `tools/parallel_conflict_resolver.py:946-948`.
- **Proposed fix**: Replace L89 with `--detect + --classify` flags. Grep `--diagnose\|--resolve-soft` returns zero matches in slice-077 vault files post-fix.
- **Builder draft**: **ACCEPTED-FIXED** — fix at design.md L89.

#### B3: `installed_content_matches_worktree` predicate underspecified — which file(s)? all/any? sha256 vs EOL-agnostic?

- **Claim under review**: design.md L118; ADR-070 L73-82.
- **Issue**: Mission-brief AC#4 enumerates 3 installed files (`~/.claude/methodology-changelog.md` + `~/.claude/ai-sdlc-VERSION` + installed SKILL.md). ADR-070 narrows to 1 (`methodology-changelog.md`). Design.md is silent on (a) file-set, (b) all-match vs any-match, (c) sha256 vs EOL-agnostic. The CAD-1 / OSDG-1 byte-equality the surrounding discipline mandates is EOL-agnostic per ADR-033 / EOL-DRIFT-1 — but the new predicate doesn't inherit the carve-out. Suppression logic is load-bearing for AC#4 negative test.
- **Evidence**: mission-brief.md L26 vs design.md L118 vs ADR-070 L73-82; project CLAUDE.md OSDG-1 EOL-agnostic clause.
- **Proposed fix**: Pin explicitly: file-set = {methodology-changelog.md, ai-sdlc-VERSION, installed pulse/SKILL.md mirror}; all-match required (any divergence → don't suppress); content-equal modulo line endings per ADR-033.
- **Builder draft**: **ACCEPTED-FIXED** — pin predicate in design.md + ADR-070 + add EOL-tolerant test row to TF-1 plan. Fix at design.md L116-119 and ADR-070 L74-82.

#### B4: ADR-070 § Override-precedence contains unredacted reasoning artifact ("Wait — that ordering is wrong... The real argument is...")

- **Claim under review**: ADR-070 L70.
- **Issue**: Published vault-permanent decision document with a mid-paragraph self-correction. Two incompatible rationales printed; first is wrong (merge-is-blocking-so-calibration-runs-first is repudiated 2 sentences later). Signals incomplete reasoning at /design time.
- **Evidence**: ADR-070 L70.
- **Proposed fix**: Rewrite as a single coherent paragraph using only the corrected (stuck-state vs advisory-backlog) framing.
- **Builder draft**: **ACCEPTED-FIXED** — rewrite L70 cleanly. Fix at ADR-070 L70.

### Majors (address this slice)

#### M1: MEPD-1 EXCLUDE precedent claim doesn't survive precedent-inspection

- **Claim under review**: design.md L100-103; ADR-070 L42 (slice-058 precedent), L88-92 (slice-074/075 precedent claim).
- **Issue**: Slice-074 / slice-075 shipped **zero new helper modules** (pure SKILL.md prose); slice-076 (the only same-shape predecessor with a new helper module + 5-inventory) is MEPD-1 **INCLUDE**, not EXCLUDE. The precedent claim is structurally inverted.
- **Evidence**: `archive/slice-074-codify-cp-r-in-branch-2-skill/reflection.md` (no new tools); `archive/slice-075-close-merge-substep-3-worktree-collision/design.md:88` ("in-band methodology-prose-fix to existing contracts"); `archive/slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen/design.md` (MEPD-1 INCLUDE, ships new helper).
- **Proposed fix**: (a) promote to INCLUDE / mint PWA-1, OR (b) keep EXCLUDE but rewrite the precedent rationale honestly.
- **Builder draft**: **ACCEPTED-FIXED via (b)** — keep EXCLUDE but rewrite ADR-070 precedent rationale honestly. **Why not (a)**: PCR-1's INCLUDE was justified by introducing a **cross-cutting load-bearing contract** (the SOFT file-set + classify_conflict taxonomy + resolve_soft_conflict ABI are callable from `/commit-slice` SKILL.md and the SOFT taxonomy is referenced from /commit-slice prose). PWA-1 would codify only `/pulse`-internal mechanism (4-state taxonomy + override-precedence + drift-flag predicate) with **no cross-skill consumers**. Methodology-changelog tracks cross-cutting contracts, not skill-internal mechanisms. The differentiator is "load-bearing for ≥2 skills" not "ships a new helper module"; slice-076 satisfies the former, slice-077 doesn't. ADR-070 rewrite must (i) acknowledge the precedent stretch honestly; (ii) state the load-bearing-for-≥2-skills criterion explicitly; (iii) cite slice-058 (ADR-only mint, no rule) as the closer precedent on the rule-axis; (iv) cite slice-076 as the structural-twin-with-different-rule-axis-shape (helper module yes, cross-skill contract yes vs no). Fix at ADR-070 § Options-considered + § Decision + design.md L100-104.

#### M2: design.md L14 says "5 new test modules" but enumerates 6 — FBCD-1 sub-mode (a) count-vs-enumeration drift

- **Claim under review**: design.md L14.
- **Issue**: Stated count 5, enumerated list 6.
- **Evidence**: design.md L14; mission-brief.md L34-49 TF-1 plan.
- **Proposed fix**: Change to "6 new test modules".
- **Builder draft**: **ACCEPTED-FIXED** — fix at design.md L14.

#### M3: 4-state taxonomy incomplete — fresh worktree on slice/NNN branch with no milestone.md collapses to UNKNOWN and is silently dropped

- **Claim under review**: design.md L9, L46-58, L127, L133.
- **Issue**: Under BRANCH-2's `git worktree add ... -b slice/NNN-<name>` + `cd` sequence, a freshly-created worktree may exist without milestone.md (if branch-create runs before scaffold). Design's `UNKNOWN → silently ignored for override` rule means /pulse won't surface the worktree during the IN_PROGRESS-but-pre-milestone window — exactly the kind of bug this slice exists to fix. Also: detached HEAD, dirty WT, stale-prunable not enumerated.
- **Evidence**: design.md L9, L46-58, L127, L133; project CLAUDE.md BRANCH-2 section.
- **Proposed fix**: Either add 5th state `PRE_BUILD` OR explicitly surface UNKNOWN-fresh-worktree as a WARN in Drift & flags (not silently dropped). Add DIRTY / DETACHED considerations.
- **Builder draft**: **ACCEPTED-FIXED via WARN-not-silent** — keep 4-state taxonomy but change "UNKNOWN ignored for override" → "UNKNOWN surfaced as `⚠️ Worktree <path> on <branch> — state unknown (<reason>)` in Drift & flags". Explicitly enumerate fresh-worktree-no-milestone + detached-HEAD + dirty-WT + stale-prunable as UNKNOWN-reasons in design.md § Fail-closed paths. Fix at design.md L52-58, L127, L133 + add to § Fail-closed paths summary.

#### M4: AC#3 scope creep — design.md adds CAL-1 cadence-overdue as 2nd-level precedence; AC#3 only contracts for #1 > #3

- **Claim under review**: mission-brief.md L24; design.md L110-116; ADR-070 L62-69.
- **Issue**: AC#3 says "supersedes the next-action derivation from milestone.md stage" + parenthetical "precedence over the cadence-overdue critic-calibrate override". Design.md elevates to a 3-level deterministic ordering. Also: (i) IN_PROGRESS+CAL-1, MERGED+CAL-1, UNKNOWN+CAL-1 cells empty in precedence table; (ii) Step-2 vs Step-3 location of the override application is ambiguous (Step-3 is Haiku-dispatched per existing SKILL.md L94-101).
- **Evidence**: mission-brief.md L24, L58; design.md L37, L108-118; ADR-070 L62-69; skills/pulse/SKILL.md L94-101.
- **Proposed fix**: Extend precedence table to cover all 4 WorktreeState × CAL-1 cells. Add explicit "override applied at Step 2 deterministic metric computation; Haiku Step 3 receives the resolved recommendation".
- **Builder draft**: **ACCEPTED-FIXED** — extend precedence table in design.md L110-116 + add Step-2-not-Step-3 anchor + clarify mission-brief AC#3 contract scope (CAL-1 precedence IS in-contract per the parenthetical). Fix at design.md L108-118 + ADR-070 L62-69 + mission-brief.md L24 (minor wording clarification).

#### M5: ADR-070 reversibility "single git revert" claim technically inaccurate under no-ff merge

- **Claim under review**: ADR-070 L107.
- **Issue**: BRANCH-2's `--merge` workflow lands as no-ff merge commit. `git revert` of a no-ff merge requires `-m 1` to pick mainline parent; bare `git revert` fails with "fatal: ... is a merge but no -m option was given".
- **Evidence**: project CLAUDE.md BRANCH-2 section; ADR-070 L107.
- **Proposed fix**: Replace with `git revert -m 1 <slice-077-merge-commit-sha>` + note about orphaned child commits.
- **Builder draft**: **ACCEPTED-FIXED** — fix at ADR-070 L107.

#### M6: BRANCH-2 path predicate doesn't handle edge cases (no-suffix branch, drift-after-rename, prunable-stale registrations)

- **Claim under review**: design.md L23, L126-127.
- **Issue**: `slice/077` (no suffix), `slice/077-foo` while folder is `slice-077-bar` (rename drift), `prunable` worktrees aren't explicitly handled in design's Fail-closed paths.
- **Evidence**: `tools/branch_workflow_audit.py:81` `_SLICE_BRANCH_RE`; project CLAUDE.md split-slice convention; design.md L23, L126-127.
- **Proposed fix**: Add to § Fail-closed paths summary: branch-name-doesn't-match-shape → filter out; branch-matches-but-folder-doesn't → UNKNOWN; prunable-stale → filter out + WARN; no-suffix-branch → filter out + WARN.
- **Builder draft**: **ACCEPTED-FIXED** — extend § Fail-closed paths summary in design.md. Fix at design.md L120-128.

#### M7: Cross-spec parity with parallel_conflict_resolver not pinned — future parity audit will flag divergences

- **Claim under review**: design.md L20-22, L86-89.
- **Issue**: `parallel_slice_family_parity_audit` is queued (slice-queue head L39). When it ships, it will discover `pulse_worktree_resolver` shares conventions (argparse mutually-exclusive-group, --repo-root, JSON output, Exit 0/1/2, UTF8-STDOUT-1) with PCR-1 but isn't currently in the parity-family. Design should pin these conventions explicitly so the future audit doesn't flag slice-077 as divergent.
- **Evidence**: `architecture/slice-queue.md:39-42`; design.md L20-22, L86-89; `tools/parallel_conflict_resolver.py:941-953`.
- **Proposed fix**: Add design.md § Cross-spec parity enumerating (i) argparse mutually-exclusive-group required; (ii) --repo-root default Path(".").resolve(); (iii) JSON keys {action, error}; (iv) Exit 0/1/2 semantics; (v) _stdout.reconfigure_stdout_utf8() at top of main().
- **Builder draft**: **ACCEPTED-FIXED** — add § Cross-spec parity section to design.md.

#### M8: APED-1 battery floor `≥6 cases` under-engineered for the surface count

- **Claim under review**: mission-brief.md must-not-defer #3; design.md L145.
- **Issue**: Slice-076's battery had 28 cases. Slice-077's actual surface enumeration: detect (8 cases) + classify (12+ cases) = 20+ minimum. ≥6 floor admits ships that miss key edges (no-milestone, stale-prunable).
- **Evidence**: mission-brief.md L70; design.md L145; archive/slice-076 reflection L8 (28-case battery).
- **Proposed fix**: Raise floor to ≥12 with explicit enumeration: detect {empty, one, multiple, non-slice-branch-filtered, mixed, stale-prunable} = 6 + classify {IN_PROGRESS, BUILT_BUT_NOT_MERGED, MERGED, UNKNOWN-no-milestone, UNKNOWN-malformed-frontmatter, UNKNOWN-git-error, UNKNOWN-head-unresolvable} = 7 → ≥13.
- **Builder draft**: **ACCEPTED-FIXED** — raise to ≥13 with enumerated cases. Fix at mission-brief.md must-not-defer #3 + design.md L145.

#### M9: No RSAD-1 design-time discipline — new SKILL.md prose introduces literal tokens that structural-pin tests will assert; aggregated lessons L77 says this is the strongest /critic-calibrate target

- **Claim under review**: aggregated lessons _index.md L77, L79, L81; design.md L139.
- **Issue**: Slice-077 adds ~30-50 lines to skills/pulse/SKILL.md with new literal tokens (`git worktree list --porcelain`, `BUILT_BUT_NOT_MERGED`, `cadence-overdue`, etc.). `cadence-overdue` already exists at L88 of the current SKILL.md → naïve substring-presence test would pass pre-edit. Per slice-075 N=3 RSAD-1 lesson, structural-pin tests MUST use line-start / wrapping-context / invocation-form anchoring.
- **Evidence**: aggregated lessons L77; existing skills/pulse/SKILL.md L88 (existing `cadence-overdue` mention).
- **Proposed fix**: Add design.md § Prose-pin test discipline mandating (anchor-strategy + APED-1-pre-AND-post-fix-prose) per literal.
- **Builder draft**: **ACCEPTED-FIXED** — add § Prose-pin test discipline to design.md with anchor-strategy table for each new literal. Fix at design.md (append new section).

### Minors (log; address if cheap)

#### m1: LOC band "~350-450 LOC" hand-waved

- **Claim under review**: design.md L9.
- **Issue**: PCR-1 helper is 1014 LOC. Slice-077's estimate is ~3× smaller; if the empirical helper turns out larger, the MEPD-1 EXCLUDE "bounded scope" rationale weakens.
- **Proposed fix**: Tighten estimate with honest comparison OR remove the LOC band.
- **Builder draft**: **ACCEPTED-FIXED** — tighten estimate to ~300-500 LOC with honest comparison to PCR-1 (slice-077 has no claim-overlay or 5-class taxonomy or audit log — just 2 main functions + dataclasses + CLI; expected ~30-50% of PCR-1's size). Fix at design.md L9.

#### m2: Active _index.md staleness during BUILT_BUT_NOT_MERGED window not addressed

- **Claim under review**: skills/pulse/SKILL.md L41.
- **Issue**: Master's _index.md "Active" table is stale during BUILT_BUT_NOT_MERGED window. /pulse's slice-count totals may be off-by-one.
- **Proposed fix**: Note in design.md § Out-of-scope OR optionally consult worktree's _index.md.
- **Builder draft**: **DEFERRED** — note in design.md § Out-of-scope. Surfaced as a known limitation; slice-count off-by-one is cosmetic (the next-action override is the load-bearing path). Defer to a future slice if user-reported pain emerges.

#### m3: MERGED cleanup-candidate surfacing semantics underspecified

- **Claim under review**: design.md L52-54; ADR-070 L51-54.
- **Issue**: How is "CLEANUP-CANDIDATE" surfaced (Drift & flags? Active slice section? formatting?). Also: MERGED can persist legitimately after --push + /sync-after-pr workflows, not just --merge failures.
- **Proposed fix**: Pin surfacing format; acknowledge MERGED persistence vectors.
- **Builder draft**: **ACCEPTED-FIXED** — pin as one-line in Drift & flags: `⚠️ Worktree <path> on branch <branch> is MERGED but not torn down — run \`git worktree remove <path>\` to clean up`. Acknowledge --push + /sync-after-pr persistence vectors in ADR-070. Fix at design.md L52-54 + ADR-070 L51-54.

#### m4: worktree-list parser duplication (actual count: N=3 post-slice-077 per /critique-review M-add-3)

- **Claim under review**: design.md L21.
- **Issue**: Python-side parser count is N=2 BEFORE slice-077 (`tools/slice_queue_writer.py:265` + `tools/branch_workflow_audit.py:333+359`); slice-077 makes N=3, which IS Fowler's "rule of three" extract trigger. Earlier draft m4 disposition under-counted at N=2 (per /critique-review M-add-3 ACCEPTED-FIXED).
- **Proposed fix**: (a) extract shared helper IN slice-077 (scope expansion to MEDIUM); (b) defer-with-honest-N=3-rationale to the queued `parallel-slice-family-parity-audit` slice.
- **Builder draft**: **DEFERRED with honest N=3 rationale** — the queued `parallel-slice-family-parity-audit` (slice-queue head) is the natural extraction-trigger slice; extracting in slice-077 would expand scope to N=3 sites + a new shared helper module + 3 sets of consumer-test updates (≥6 additional files). Voluntary-restraint defers extraction to the parity-audit slice which will already touch all 3 sites. Count corrected from N=2 to N=3 in design.md L21 + L249 + ADR-070 (per /critique-review M-add-3 ACCEPTED-FIXED).

#### m5: WorktreeStateClassification vs WorktreeState return-type drift

- **Claim under review**: design.md L9, L59 vs mission-brief.md L22.
- **Issue**: design.md says `classify_worktree_state` returns `WorktreeStateClassification` (dataclass); mission-brief AC#2 says it returns `WorktreeState` (enum). FBCD-1 sub-mode (a).
- **Proposed fix**: Pick one; propagate to test names.
- **Builder draft**: **ACCEPTED-FIXED** — go with `WorktreeStateClassification` (richer; carries reason/evidence for debugging) with `.state: WorktreeState` accessor. Update mission-brief AC#2 + AC#5 + design.md L9, L59 + test row names in mission-brief TF-1 plan. Fix at mission-brief.md L22, L46 + design.md L9, L59.

#### m6: Step-3 Haiku augmented state-dict shape not pinned as contract

- **Claim under review**: design.md L37.
- **Issue**: Haiku silently renders whatever dict shape it receives; no test pins the new keys/types.
- **Proposed fix**: Add test row to TF-1 plan asserting state-dict shape.
- **Builder draft**: **ACCEPTED-FIXED** — add TF-1 row `test_step_2_state_dict_includes_worktrees_field_with_worktreeinfo_list` to AC#3 (the override is the load-bearing surface that requires the new dict field). Fix at mission-brief.md TF-1 plan.

## Dimensions checked

- [x] **Unfounded assumptions** — B3 (predicate file-set/all-or-any/sha256-vs-EOL), B4 (precedence rationale incomplete), M5 (single-revert claim), m1 (LOC band).
- [x] **Missing edge cases** — M3 (PRE_BUILD / DIRTY / DETACHED / stale-prunable), M6 (branch-name shape edge cases), m2 (_index.md staleness), m3 (MERGED persistence after --push / --sync-after-pr).
- [x] **Over-engineering** — None significant.
- [x] **Under-engineering** — M3, M4, M8, M9.
- [x] **Contract gaps** — B2, B3, M5, M7, m5, m6.
- [x] **Security** — None. /pulse is read-only; no auth/secrets/external-input crossing trust boundaries.
- [x] **Drift from vault** — M1 (precedent claim inverted), B1 (slice-076 reflection lesson ignored), M9 (aggregated-lessons RSAD-1 N=3 strongest /critic-calibrate target not pre-empted).
- [x] **Web-known issues** — Skipped (no external technology / API; all surfaces in-house-vetted).
- [x] **Cross-cutting conformance** — RSAD-1 (M9), FBCD-1 sub-mode (a) (B2, M2, m5), PTFCD-1/PTFFD-1 (B1), MEPD-1 (M1), TPHD-1 sub-mode (a) (will apply during ACCEPTED-FIXED edits — harmonize mission-brief + design + ADR-070 in same fix block), APED-1 scope (M8), CAD-1/OSDG-1/EOL-DRIFT-1 (B3).

## Triage

**Triaged by**: user
**Date**: 2026-05-28
**Final verdict**: CLEAN

22 findings dispositioned (19 first-Critic + 3 meta-Critic missed); 20 ACCEPTED-FIXED applied in-band; 2 DEFERRED with honest rationale. User ratified en bloc at TRI-1 — all Builder draft dispositions accepted unchanged. Mechanical verdict computes to CLEAN per /critique SKILL.md Step 4.5 formula (zero ACCEPTED-PENDING, zero ESCALATED, zero OVERRIDDEN).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | mission-brief.md L50 `(manual)` TF-1 row removed; slice-076 reflection L24 lesson now applied |
| B2 | Blocker | ACCEPTED-FIXED | design.md L89 corrected to `--detect + --classify` (PCR-1 copy-paste pollution removed) |
| B3 | Blocker | ACCEPTED-FIXED | design.md L141-156 + ADR-070 L107-127 — predicate pinned: 3-file set, all-match, content-equal-modulo-EOL per ADR-033/EOL-DRIFT-1 |
| B4 | Blocker | ACCEPTED-FIXED | ADR-070 L99 — Override-precedence rationale rewritten as single coherent paragraph (stuck-state-vs-advisory-backlog framing); reasoning artifact removed |
| M1 | Major | ACCEPTED-FIXED | ADR-070 § Honest precedent inspection + § Decision rewritten; EXCLUDE kept with "load-bearing cross-skill" criterion replacing the slice-074/075 precedent stretch; slice-058 cited as the closer ADR-only precedent; promotion trigger N=2 cross-skill consumers explicitly stated |
| M2 | Major | ACCEPTED-FIXED | design.md L14 corrected: "6 new test modules" (FBCD-1 sub-mode (a) count drift fixed) |
| M3 | Major | ACCEPTED-FIXED | design.md L162-192 — UNKNOWN WARN-not-silent + 8 sub-reasons enumerated (fresh-worktree-no-milestone, detached-HEAD, dirty-WT, etc.); closes the witnessed-gap class |
| M4 | Major | ACCEPTED-FIXED | design.md L125-134 — full 4×CAL-1 precedence table (8 cells); Step-2 deterministic vs Step-3 Haiku-render location anchor explicit |
| M5 | Major | ACCEPTED-FIXED | ADR-070 L155 — `git revert -m 1 <slice-077-merge-commit-sha>` (no-ff merge parent-selection correction) |
| M6 | Major | ACCEPTED-FIXED | design.md L173-176 — branch-name edge cases enumerated (no-suffix, rename-drift, prunable-stale, non-slice) with filter+WARN behavior |
| M7 | Major | ACCEPTED-FIXED | design.md L194-208 — § Cross-spec parity table pins 8 conventions vs PCR-1 (forestalls future parity-audit divergence flag) |
| M8 | Major | ACCEPTED-FIXED | mission-brief.md L67 + design.md L243 — APED-1 floor raised from ≥6 to ≥13 with enumerated cases (slice-076's 28-case precedent justifies) |
| M9 | Major | ACCEPTED-FIXED | design.md L212-231 — § Prose-pin test discipline + per-literal anchoring-strategy table; RSAD-1 N=3 cumulative pattern pre-empted at design time |
| m1 | Minor | ACCEPTED-FIXED | design.md L9 — LOC band tightened to ~300-500 with honest PCR-1 (1014 LOC) comparison rationale |
| m2 | Minor | DEFERRED | design.md L247-248 — Active _index.md staleness during BUILT_BUT_NOT_MERGED window noted as known limitation; off-by-one slice-count cosmetic; next-action override is the load-bearing path; defer to future slice if user-reported pain emerges |
| m3 | Minor | ACCEPTED-FIXED | design.md MERGED-cell precedence + ADR-070 L68-77 — surfacing format pinned (one-line in Drift & flags); persistence vectors (--push/--sync-after-pr/--merge-failure) acknowledged |
| m4 | Minor | DEFERRED | design.md L21/L249 (N=3 framing corrected per M-add-3); extraction deferred to queued `parallel-slice-family-parity-audit` slice — that slice will already audit all 3 sites for parity and helper extraction folds into its scope |
| m5 | Minor | ACCEPTED-FIXED | mission-brief.md AC#2 + AC#5 + design.md L9/L59 — `classify_worktree_state` returns `WorktreeStateClassification` dataclass with `.state: WorktreeState` + `.reason: str` accessor; consistent across all three files |
| m6 | Minor | ACCEPTED-FIXED | mission-brief.md TF-1 plan — added `test_step_2_state_dict_includes_worktrees_field_with_worktreeinfo_list` row to AC#3 (pins Step-2 augmented state-dict shape passed to Haiku) |
| M-add-1 | Major | ACCEPTED-FIXED | design.md L201 — PCR-1 parse-time default corrected from `Path(".").resolve()` to `Path(".")`; post-parse `args.repo_root.resolve()` clarification added |
| M-add-2 | Major | ACCEPTED-FIXED | R-22 registered in architecture/risk-register.md (status: open, witnessed during slice-076 merge sequence, will retire at slice-077 /reflect); mission-brief.md L5 now cites R-22 (RR-1 semantic conformance); mirrors slice-076 R-21 precedent |
| M-add-3 | Minor | ACCEPTED-FIXED | critique.md m4 + design.md L21/L249 — N=2 framing corrected to N=3 post-slice-077 (Fowler extract trigger; Python-side parser exists at slice_queue_writer.py:265 + branch_workflow_audit.py:333+359 + slice-077 adds pulse_worktree_resolver.py); deferral preserved with honest rationale |
