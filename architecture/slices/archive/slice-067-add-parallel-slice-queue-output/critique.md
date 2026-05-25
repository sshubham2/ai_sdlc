# Critique: Slice 067 add-parallel-slice-queue-output

**Critic reviewed**: mission-brief.md, design.md, ADR-064-mint-psq-1-parallel-slice-queue.md
**Date**: 2026-05-25
**Result**: NEEDS-FIXES

## Summary

Strong design overall — BRANCH-2 worktree path is canonical, NAW-1 zero-warn claim verified, MEPD-1 Inclusion-heuristic posture correctly classified as new-mechanism (N=8 precedent), and the cross-slice contract pin with slice-068 is explicit. Two Blockers, however: **B1** BC-PROJ-10 paired-pin discipline gap at N≥18 cumulative — design.md L128 wiring-matrix cites a single entry-pin test that violates the canonical naming convention AND lacks the mandated `_shippability_consumer_propagation` sibling test, and mission-brief TF-1 plan ships ZERO entry-pin rows (textbook slice-064 B2 / slice-060 M-add-2 / N≥17 BC-PROJ-10:173 recurrence); **B2** `compute_parallel_safety()` enum drift — design.md L12 introduces `UNKNOWN-NO-HINT-FILES` as a 4th enum value that mission-brief AC2's `Parallel-safety` field-shape contract does not enumerate, AND the design has an unspecified collision rule when both "zero active slices" (AC4-(b) → NON-OVERLAPPING) and "candidate has empty hint_files" (UNKNOWN-NO-HINT-FILES) hold simultaneously. Three Majors and three minors below.

## Findings

### Blockers (must address before /build-slice)

#### B1: BC-PROJ-10 paired-pin discipline gap — wiring-matrix entry-pin test violates canonical naming + lacks shippability-consumer-propagation sibling + TF-1 plan ships zero entry-pin rows

- **Claim under review**: design.md L128 wiring-matrix row: ``| `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md` | … | `tests/methodology/test_methodology_changelog.py::test_v0_69_0_section_mints_psq_1` (collected by existing META-1 enforcing assertion at `:136`) | — |`` AND mission-brief.md L26-37 TF-1 plan has 10 rows, ZERO of which target `tests/methodology/test_methodology_changelog.py` for the v0.69.0 entry-pin pair.
- **Issue**: Three compounding problems on the BC-PROJ-10 paired-entry-pin axis:
  1. **Function-name convention violation**: canonical shape per `tests/methodology/test_methodology_changelog.py:4184/4248/4433/4513` is `test_v_0_NN_0_<rule>_entry_present_in_repo` + `test_v_0_NN_0_<rule>_shippability_consumer_propagation` (underscores around version digits; `v_0_69_0` NOT `v0_69_0`). Design.md cites `test_v0_69_0_section_mints_psq_1` — wrong underscore pattern AND wrong suffix (`_section_mints_psq_1` is not in the canonical lexicon).
  2. **Paired-pin schema missing**: every v-section entry-pin since v0.66.0 ships as a PAIR per BC-PROJ-10 paired-pin discipline (`_entry_present_in_repo` + `_shippability_consumer_propagation`). Design.md cites only ONE test. This is exactly the slice-064 B2 / slice-060 M-add-2 N≥17 BC-PROJ-10:173 recurrence.
  3. **TF-1 plan ships zero entry-pin rows for v0.69.0**: mission-brief TF-1 plan has rows mapped to AC1-AC5 — none for the v0.69.0 entry-pin pair. Per TF-1 strict-pre-finish discipline + BC-PROJ-10 paired-pin discipline, the v0.69.0 entry-pin PAIR needs TWO rows added to the TF-1 plan.
  4. **Misleading "collected by ... META-1 enforcing assertion at `:136`" framing**: META-1's assertion at `:136` is the `^## v` split that checks every entry carries a `Rule reference` line. It does NOT "collect" the entry-pin test functions. Entry-pin functions are SEPARATE pytest collections enumerated explicitly per version.
- **Evidence**:
  - `tests/methodology/test_methodology_changelog.py:4433` `def test_v_0_68_0_branch_2_entry_present_in_repo():`
  - `tests/methodology/test_methodology_changelog.py:4513` `def test_v_0_68_0_branch_2_shippability_consumer_propagation():`
  - methodology-changelog.md v0.67.0 entry text references the recurring class
  - design.md L176 itself names "BC-PROJ-10 paired-pin discipline" — but L128 wiring-matrix only cites one test
  - Aggregated lessons line 67 (slice-066): "BC-PROJ-10 paired-entry-pin verification at design-time"
- **Proposed fix**:
  1. Rename the design.md L128 wiring-matrix test cite to the canonical PAIR: `tests/methodology/test_methodology_changelog.py::test_v_0_69_0_psq_1_entry_present_in_repo` + `tests/methodology/test_methodology_changelog.py::test_v_0_69_0_psq_1_shippability_consumer_propagation`.
  2. Strike the "collected by existing META-1 enforcing assertion at `:136`" parenthetical; replace with "(BC-PROJ-10 paired-pin schema per slice-066 v0.68.0 entry precedent at `:4433` + `:4513`)".
  3. Add two TF-1 plan rows to mission-brief.md targeting the entry-pin pair under a new meta-AC (AC6 covering v0.69.0 changelog-entry pin + RPCD-1 / SCPD-1 shippability propagation).
  4. Update design.md L20 (shippability row #67) to explicitly name the paired-pin test naming convention.
- **Builder draft**: ACCEPTED-FIXED — all 4 sub-fixes applied in this fix block (mission-brief.md AC6 + 2 new TF-1 rows; design.md L128 wiring-matrix corrected + L20 shippability cite extended; ADR-064 unchanged since it didn't carry the misframing).

#### B2: `compute_parallel_safety()` enum drift between design.md and mission-brief AC2 + unspecified collision when zero-active-slices AND empty-hint-files both hold

- **Claim under review**:
  - mission-brief.md AC2 (L17): "`**Parallel-safety:**` (`NON-OVERLAPPING` OR `OVERLAPS-WITH-slice-NNN`...)"
  - design.md L12: `compute_parallel_safety()` returns `("UNKNOWN-NO-HINT-FILES", [])` if `candidate_files` is empty; classification overridden to `UNKNOWN-NO-GRAPH` if graphify graph missing
  - mission-brief AC4 sub-(c) (L19): missing graph → `**Parallel-safety:** UNKNOWN-NO-GRAPH`
  - mission-brief AC4 sub-(b) (L19): zero active slices → all candidates `NON-OVERLAPPING`
  - design.md L80: "Active-slice `_index.md` `## Active` table absent or empty → `derive_active_slice_blast_radius()` returns `{}`; downstream `compute_parallel_safety()` correctly flags all candidates `NON-OVERLAPPING` (AC4-(b))"
- **Issue**: Two compounding gaps:
  1. **Field-shape enum drift**: AC2 enumerates 2 values; AC4(c) adds 1; design.md L12 introduces a 4th (`UNKNOWN-NO-HINT-FILES`) the AC2 + AC4 contract never enumerates. Format-pin tests cannot pin honestly because the contract itself is incomplete.
  2. **Unspecified collision rule when zero-active-slices AND empty-hint-files both hold**: per design.md L12, empty `candidate_files` returns `UNKNOWN-NO-HINT-FILES` regardless. Per AC4-(b), zero active slices → all `NON-OVERLAPPING`. When both conditions hold, what wins? `test_zero_active_slices_all_non_overlapping` would FAIL on any candidate with legitimately empty hint files.
- **Evidence**:
  - mission-brief.md L17 (AC2 — 2-value enum)
  - mission-brief.md L19 (AC4 — adds 3rd value)
  - design.md L12 (4th value introduced unilaterally)
  - ADR-064 L58 (also enumerates 4-value — sibling cross-file drift, see m1)
  - Builder's own Special-attention dimension #5 names this as a falsifier class
- **Proposed fix**:
  1. Promote `UNKNOWN-NO-HINT-FILES` to first-class enum member in mission-brief AC2: "`NON-OVERLAPPING` | `OVERLAPS-WITH-slice-NNN[, slice-MMM]` | `UNKNOWN-NO-HINT-FILES` | `UNKNOWN-NO-GRAPH`".
  2. Add new AC4 sub-(d): "candidate with empty `hint_files` set → entry classified `UNKNOWN-NO-HINT-FILES`".
  3. Specify precedence rule in design.md L80 + AC4-(b) qualifier: `UNKNOWN-NO-GRAPH` > `UNKNOWN-NO-HINT-FILES` > `OVERLAPS-WITH-*` > `NON-OVERLAPPING`. Add qualifier to AC4-(b): "for candidates with non-empty hint_files; empty-hint candidates still flag `UNKNOWN-NO-HINT-FILES`".
  4. Add TF-1 row `test_empty_hint_files_overrides_zero_active_slices_to_unknown_no_hint_files`.
  5. Update Verification plan rows #3 + #4 to enumerate the four-way classification.
- **Builder draft**: ACCEPTED-FIXED — all 5 sub-fixes applied in this fix block; m1 (ADR-064 L58 sibling drift) auto-closes via this fix.

### Majors (address this slice)

#### M1: BCR-1 round-trip non-trigger declaration is correct but defensive language masks the missing structural test

- **Claim under review**: mission-brief.md L57 must-not-defer prose + L74 Dependencies prose declare "NOT a BCR-1 round-trip" but lack a structural verification anchor.
- **Issue**: Prose-only declarations without a structural verification benefit from a positive test; Wiegers requirements-design traceability principle.
- **Evidence**: mission-brief.md L57 + L74; `tests/methodology/test_bcr_1_backlog_round_trip.py`; slice-053 first-dogfood "trigger correctly no-ops" pattern.
- **Proposed fix**: (a) Add a verification-plan row pinning BCR-1 test PASSes on slice-067; OR (b) drop the "MUST explicitly note" weight to "should note" since no enforcement gate exists.
- **Builder draft**: OVERRIDDEN — the BCR-1 audit test (`tests/methodology/test_bcr_1_backlog_round_trip.py`) runs in the full pytest suite at `/validate-slice` Step 5 and would catch a regression in BCR-1's no-op-on-no-sentinel behavior structurally. A per-slice "BCR-1 sentinel-grep returns empty" test is over-engineering at N=15 cumulative codification slices' worth of evidence the existing structural test holds. The prose at mission-brief L57 + L74 is /reflect-time discipline marker (slice-053 + slice-064 + slice-065 + slice-066 all carry the explicit "NOT a BCR-1 round-trip" cite), not an enforcement gate — the current discipline is sound. **Rationale**: existing structural test in full pytest suite is the backstop; prose marker is operational discipline for /reflect; cost-benefit on a per-slice empirical test is poor.

#### M2: Mid-slice smoke gate command bootstrap-impossible — `tools.slice_queue_writer` doesn't exist when /slice runs, but the dogfood-seed claim in Pipeline position implies it ran

- **Claim under review**: mission-brief.md L107 Pipeline position hedges "/slice as dogfood seed OR deferred to /build-slice — `/design-slice` locks"; design.md L21 says "written first at this slice's /build-slice mid-slice smoke"; mid-slice smoke command at mission-brief L83 imports `from tools.slice_queue_writer import write_slice_queue` which only exists post-Phase-A of /build-slice. The Pipeline position hedge never resolves.
- **Issue**: Bootstrap-discharge ambiguity mirrors slice-066 `WORKTREE=skip-bootstrap` shape — needs an explicit canonical bootstrap-discharge line.
- **Evidence**: mission-brief.md L107; mission-brief.md L83-87; design.md L21; slice-066 reflection.md bootstrap-discharge precedent.
- **Proposed fix**: Two options: (1) lock bootstrap-discharge prose in mission-brief L107 explicitly; OR (2) add idempotent ImportError guard in Step 6.5 skill prose.
- **Builder draft**: ACCEPTED-FIXED — both options applied (defense-in-depth):
  - Mission-brief L107 rewritten to drop the dogfood-seed branch and explicitly cite bootstrap-discharge: "slice-067's own `/slice` invocation did NOT write `architecture/slice-queue.md` — the helper doesn't exist at /slice time; bootstrap-reference instance #1 per slice-066 WORKTREE=skip-bootstrap precedent; first write at /build-slice mid-slice smoke."
  - Design.md gains a new sub-section "Step 6.5 ImportError guard" specifying that the SKILL.md prose wraps the helper invocation in a try/ImportError block so any future `/slice` run before the helper is available silently no-ops (defensive for PSQ-1-revert scenario + slice-bootstrap window).

#### M3: Step 6.5 SKILL.md insertion position relative to the existing template's pre-finish-gate prose is unspecified — risk of breaking the multi-line markdown template block

- **Claim under review**: design.md L16 cites "between current Step 6 and `## Critical rules`" which is a 165-line span (SKILL.md:215-380); that span includes the mission-brief template literal at SKILL.md:276-378 — inserting Step 6.5 anywhere inside that span risks corrupting the template's fenced-markdown block.
- **Issue**: Insertion-point ambiguity could trip the OSDG-1 content-equality guard if landed inside the mission-brief template literal.
- **Evidence**: SKILL.md:214 (Step 6 header); SKILL.md:276 (mission-brief template fence open); SKILL.md:378 (template fence close); SKILL.md:380 (## Critical rules).
- **Proposed fix**: Pin insertion to SKILL.md:378 (after template-fence close) before SKILL.md:380 (## Critical rules); also pin the `## Pipeline position` update.
- **Builder draft**: ACCEPTED-FIXED — design.md L16 + new sub-section pin the insertion point to SKILL.md:378-379 (after the template close-fence ``` at L378 and before `## Critical rules` at L380); also pin the `## Pipeline position` block extension to note the queue-write side-effect (add to existing `on-clean-completion` clause: "Step 6.5 fires here; queue-write failure is non-fatal — wrapped in try/except per ADR-064 Consequences §").

### Minors (log; address if cheap)

#### m1: ADR-064 cross-slice contract section names `Parallel-safety` enum members that mission-brief AC2 doesn't enumerate — same B2 drift class

- **Claim under review**: ADR-064 L58: "The `Parallel-safety` enum is `NON-OVERLAPPING | OVERLAPS-WITH-slice-NNN[, slice-MMM] | UNKNOWN-NO-HINT-FILES | UNKNOWN-NO-GRAPH`."
- **Issue**: ADR-064 enumerates 4-value enum honestly; mission-brief AC2 only enumerates 2. Sibling FBCD-1 cross-file harmonization site.
- **Evidence**: ADR-064 L58 vs mission-brief.md L17 + L19.
- **Proposed fix**: Auto-closes via B2 fix in mission-brief.md AC2.
- **Builder draft**: ACCEPTED-FIXED (bundled with B2 fix — mission-brief AC2 now enumerates all 4 values matching ADR-064 L58).

#### m2: Atomic-write must-not-defer mentions `os.replace()` but not `os.fsync()` — sufficient for the use case but worth noting in design

- **Claim under review**: mission-brief.md L51 + design.md L116 atomic claim without fsync.
- **Issue**: Per canonical atomic-write recipe, full crash-durability needs fsync; for slice-queue use case it's over-engineering but ambiguous.
- **Evidence**: cited bswen.com/blog/2026-04-04 atomic-write recipe.
- **Proposed fix**: Add scope-explicit note in design.md L116.
- **Builder draft**: ACCEPTED-FIXED — design.md L116 gains note: "`.tmp` + `os.replace()` provides atomicity vs concurrent reader; crash-durability via `os.fsync()` is explicitly OUT OF SCOPE — queue is regenerable on every `/slice` invocation, so a post-crash zero-byte queue is not load-bearing."

#### m3: R-19 entry is hedged as "Optional — to be decided at /critique time" but design.md already wrote it

- **Claim under review**: design.md L194: "(Optional — to be decided at /critique time whether R-19 warrants entry now or defers to /reflect Discovered.)"
- **Issue**: This is /critique time — the hedge can be resolved now.
- **Evidence**: design.md L192-194.
- **Proposed fix**: Drop the hedge; commit to R-19 being added at /build-slice Phase A.
- **Builder draft**: ACCEPTED-FIXED — design.md L194 hedge dropped; commits to R-19 entry at /build-slice Phase A with the L192 prose; risk-tier low-band per the design.md L192 score reasoning.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (paired-pin test naming + "collected by META-1" misframing); `build_backlog.py:120-155` cite verified; BRANCH-2 canonical-worktree-path literal verified against `tools/branch_workflow_audit.py:_resolve_expected_worktree_path`.
- [x] **Missing edge cases** — B2 (enum drift + zero-active-AND-empty-hint collision); concurrent /slice across sessions handled via atomic-write must-not-defer (acceptable, see m2).
- [x] **Over-engineering** — none. 4-function helper API is appropriately decomposed for testability axes per slice-059 / slice-063 injection-seam precedent. ADR-064 Option 3 (SQLite) correctly rejected.
- [x] **Under-engineering** — B1 (TF-1 plan zero entry-pin rows); M3 (SKILL.md insertion point unspecified); M1 (BCR-1 no-trigger declaration prose-only — Builder OVERRIDDEN with rationale).
- [x] **Contract gaps** — B2 (Parallel-safety enum drift); B1 (BC-PROJ-10 paired-pin contract not declared).
- [x] **Security** — none. Methodology-internal helper; no external surface; no auth boundaries; fixed-argv subprocess invocation (no shell injection).
- [x] **Drift from vault** — Standard mode confirmed; MEPD-1 Inclusion-heuristic posture verified (N=8 new-mechanism precedent); BC-PROJ-9 5-inventory fan-out all sites verified at cited shape today (`plugin.yaml:94-150`, `install_audit.py:_CANONICAL_TOOLS:90-119`, `test_utf8_stdout_regression.py:_ROOT_ONLY_TOOLS:95-105`, `INSTALL.md:22 + :166`); PSQ-1 + paired entry-pin obligation flagged in B1; 5-part PMI-1 leg enumeration consistent.
- [x] **Web-known issues** — `os.replace()` atomicity verified via WebSearch (Python 3.3+ docs); m2 fsync gap acceptable for use case.
- [x] **Cross-cutting conformance** — B1 covers BC-PROJ-10 paired-pin (slice-014 SCPD-1 sibling-class on test-name supersession); FBCD-1 sub-mode (a) cross-file harmonization fires on m1 (auto-closes via B2); APED-1 not fired (no audit parse rule change); RPCD-1 covered (5-inventory fan-out); PTFCD-1 + PTFFD-1 covered (TF-1 plan paths verified); NAW-1 zero-warn confirmed; WS-1 / ETC-1 R-7 silent-default-off not fired (frontmatter values are bare `false` without HTML comments); RSAD-1 design-discoverability sound modulo m3 hedge.

## Sources (Critic-supplied)

- [Python os.replace function — atomic cross-platform overwrite](https://zetcode.com/python/os-replace/)
- [How to Implement Atomic File Writing in Python (No Partial Writes) | BSWEN (2026-04-04)](https://docs.bswen.com/blog/2026-04-04-atomic-file-writing-python/)

## Triage

**Triaged by**: user
**Date**: 2026-05-25
**Final verdict**: CLEAN

Reconciliation incorporates BOTH passes per DR-1: first-Critic findings (B1, B2, M1, M2, M3, m1, m2, m3) + meta-Critic missed findings (M-add-1, M-add-2, M-add-3, M-add-4). All 4 meta-Critic missed findings were Builder-fix-block-introduced regressions caught by the meta-Critic's empirical re-review of post-fix artifacts (slice-062 + slice-064 M-add-1 precedent extending to N=3 cumulative on BRANCH-2 first-governed-slice N+1). M1 disposition stays OVERRIDDEN but rationale corrected per meta-Critic SEVERITY-WRONG-ON-RATIONALE.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | BC-PROJ-10 paired-pin discipline gap; 4 sub-fixes applied — design.md L128 wiring-matrix now cites canonical PAIR `test_v_0_69_0_psq_1_entry_present_in_repo` + `test_v_0_69_0_psq_1_shippability_consumer_propagation` (mirroring slice-066 v0.68.0 BRANCH-2 at `test_methodology_changelog.py:4433` + `:4513`); META-1 misframing struck; mission-brief AC6 + 2 TF-1 rows added; design.md L20 shippability cite extended. |
| B2 | Blocker | ACCEPTED-FIXED | `compute_parallel_safety()` enum drift + zero-active-AND-empty-hint collision rule unspecified; 5 sub-fixes applied — AC2 enumerates 4 values; AC4 sub-(d) added; design.md L80 precedence rule specified (`UNKNOWN-NO-GRAPH > UNKNOWN-NO-HINT-FILES > OVERLAPS-WITH-* > NON-OVERLAPPING`); TF-1 row `test_empty_hint_files_overrides_zero_active_slices_to_unknown_no_hint_files` added; Verification plan extended to 4-way classification. |
| M1 | Major | OVERRIDDEN | BCR-1's trigger discipline is enforced by /reflect's own runtime logic — a spurious trigger on absent sentinel would fail visibly at /reflect time when it attempted to round-trip a non-existent SC-NNN entry; per-slice empirical pre-pin is cost-benefit-negative at N=15 cumulative codification slices' worth of evidence. (Rationale corrected per /critique-review meta-Critic SEVERITY-WRONG-ON-RATIONALE: the original Builder draft cited `tests/methodology/test_bcr_1_backlog_round_trip.py` as a structural backstop, but the 8 tests in that file pin prose-presence anchors inside scoped SKILL.md sections, NOT runtime no-trigger behavior. The OVERRIDE outcome stands; the rationale was strengthened.) |
| M2 | Major | ACCEPTED-FIXED | Mid-slice smoke bootstrap-impossible; defense-in-depth dual-option applied — mission-brief L107-112 cites bootstrap-discharge instance #1 per slice-066 WORKTREE=skip-bootstrap precedent; design.md L213-234 added `Step 6.5 ImportError guard` subsection with idempotent try/except shape covering both bootstrap window AND future PSQ-1-revert in ONE mechanism. |
| M3 | Major | ACCEPTED-FIXED | SKILL.md insertion position pinned at design.md L16 to SKILL.md:378-379 (after template-fence close at L378, before `## Critical rules` at L380); template literal L276-378 MUST NOT be modified; `## Pipeline position` block extension spec added. |
| m1 | Minor | ACCEPTED-FIXED | ADR-064 L58 enum drift auto-closed by B2 fix — mission-brief AC2 now matches ADR-064 L58 4-value enum. |
| m2 | Minor | ACCEPTED-FIXED | Atomic-write fsync gap explicit OUT-OF-SCOPE note added at design.md L116 with regenerable-artifact rationale. |
| m3 | Minor | ACCEPTED-FIXED | R-19 hedge dropped at design.md L194; commits R-19 entry to risk-register.md at /build-slice Phase A with full prose + Status: `mitigating`. |
| M-add-1 | Major | ACCEPTED-FIXED | AC6 introduction violates SKILL.md L174/L208/L295 ≤5-AC rule; rationale note added at mission-brief.md after AC6 documenting per-slice deviation (new-mechanism-mint with BC-PROJ-10 paired-pin obligation cannot fold cleanly into AC1-AC5); flagged for /critic-calibrate aggregation if pattern recurs on slice-068+. |
| M-add-2 | Major | ACCEPTED-FIXED | Pre-finish gate L96 "All 5 acceptance criteria" updated to "All 6 acceptance criteria" with cross-ref to AC6 + AC-count deviation rationale; TPHD-1 sub-mode (a) Builder-fix-block-introduced internal-drift defect closed. |
| M-add-3 | Major | ACCEPTED-FIXED | design.md L21 "(dogfood seed)" residual phrase replaced with "(bootstrap-discharge instance #1 per slice-066 WORKTREE=skip-bootstrap precedent — the helper does not exist at /slice time so the slice's own /slice cannot self-apply)" — semantic drift between mission-brief L112 + design.md L21 closed. |
| M-add-4 | Major | ACCEPTED-FIXED | ADR-064 L50 5-part PMI-1 leg enumeration corrected to canonical 5 legs (VERSION / plugin.yaml.version / pyproject.toml [project].version / methodology-changelog.md ## v0.69.0 header / installed ~/.claude/ai-sdlc-VERSION) per slice-066 v0.68.0 entry-pin at `tests/methodology/test_methodology_changelog.py:4483-4491`; TVFS-1 + MCFS-1 noted separately as BC-PROJ-9 consumer-propagation surfaces (NOT PMI-1 parts). |
