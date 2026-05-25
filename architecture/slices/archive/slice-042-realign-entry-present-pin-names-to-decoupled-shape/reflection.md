# Reflection: Slice 042 realign-entry-present-pin-names-to-decoupled-shape

**Date**: 2026-05-18
**Shipped**: YES

## Validated
- ADR-044 anchor (`test_\w*_entry_(?:present|names_\w+)_in_repo_and_installed`, literal-suffix) catches all 37 active defs incl. the no-`_sub_`/no-`_<rule>_` edge variant `test_v_0_36_0_entry_names_three_modes_*` and structurally excludes the CAD-1 `test_in_repo_and_installed_*_are_content_equal` family — validated by T1 (37→0 residual) + 673-test suite green + 0 CAD-1-family matches.
- ADR-045 live-vs-frozen boundary is correct: renaming the 69 shippability `::`-selectors in lockstep with the 37 defs keeps the Step-5.5 catalog coherent — validated by `shippability_runner` 41/41 PASS + `shippability_path_audit` clean on the real catalog (the decisive runner-class artifact).
- "No RULE-ID/changelog/PMI-1 obligation" pre-decision — validated against the *actual* META-1 (`test_each_changelog_entry_carries_rule_reference` is per-`## v`-block, no fn-name cross-check) + PMI-1 v1.1 (version-agnostic); MCFS-1 PASS confirms the frozen changelog (untouched) stayed forward-synced. Conformance-fix class (slice-035/036/040; MEPD-1(b)).

## Corrected
- This slice's own design.md inventory counts (rev-0 carried slice-041 prose `~33`/`27-ship`/`~17 ADR`; rev-1 "fixes" were *also* wrong) → corrected to mechanically-verified `37 def / 69 ship-occ-32-uniq-28-rows / 40 changelog / 13 prior ADR / _index 3 / lessons 2` and design restructured to grep-predicate-as-single-source-of-truth (canonical anchor command embedded). Updated in this slice's [[design.md]], [[decisions/ADR-044]], [[decisions/ADR-045]], mission-brief (build-log notes the rev-1→rev-2 correction).
- ADR-045 prose "ADR-044/045 cite the old name" (DR-1 M3-sev: overstated — ADR-045=0) → then my own M3-sev fix re-introduced 1 literal into ADR-045; caught at build-T0, corrected so ADR-045=0 / ADR-044=1. Updated in [[decisions/ADR-045]].
- No ADR superseded, no risk-register state change (R-4 already retired by slice-041; this slice has no R-4 dependency).

## Discovered
- **Proving "frozen set untouched" by regex count is itself defect-prone**: `grep -c` counts lines not occurrences; a Python `(?:...)` non-capturing-group pattern silently mismatches under ERE `grep`. The robust invariant is a regex-independent **content hash (sha256) snapshot** of the frozen set. Impact: any future identifier/carve-out/rename slice should hash-snapshot the frozen set, never regex-count it. (Method-level analogue of the slice-022 self-violation law.)
- **A `/critique` ACCEPTED-FIXED fix-prose edit can itself re-introduce the exact defect it corrects** — the M3-sev fix put the old literal back into ADR-045 (slice-032 "a design correction is itself an unguarded adversarial surface", N+1), invisible to the Critic stack AND DR-1; caught only by the build-time T0 anchored grep. Impact: the build-T0 repo-wide anchored re-derivation is the structural backstop for identifier-truth slices, not the Critic stack.

## Deferred
- None. The slice's whole chartered scope (the slice-041 deferral) is discharged: identifier-truth restored, the only standing slice-041 follow-up is closed.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (all 13 ACCEPTED-FIXED) + build/validate reality:

- **B1** (def 40→37; AC "2"→4 _entry_names incl no-`_sub_`): VALIDATED — first Critic ran the grep, was empirically right; the design's count was false.
- **B2 / M1 / M2** (carve-out ADR list / shippability "~31 rows" / changelog count + sibling-enum): VALIDATED *as findings* — but the Builder's ACCEPTED-FIXED *corrections* (16-incl-016/018/031; 67/31; 43) were themselves wrong (trusted earlier non-anchored greps). The finding was right; the fix was a recompute-don't-trust miss.
- **B3** (4 undocumented active refs incl `tools/...:58`): VALIDATED — load-bearing; `tools/` source docstring would have shipped stale.
- **M3** (ADR self-ref RSAD-1): VALIDATED.
- **m1** (smoke-gate wording): VALIDATED.
- **B-add-1 / B-add-2 / B-add-3 / m-add-1 / m-add-2 / M3-sev** (DR-1 EXTEND): VALIDATED — DR-1 caught that the rev-1 ACCEPTED-FIXED corrections substituted new wrong numbers (69≠67, 32≠31, 40≠43, 13≠16, _index 3≠4, calib-log 0≠1; ADR-045 0≠"044/045"); every figure re-confirmed by Builder mechanical anchor-grep.

**Missed by Critic**: (1) Neither the first Critic nor DR-1 re-verified that the *Builder's own M3-sev fix* would re-introduce a literal into ADR-045 — caught only at build-T0 by the anchored grep. (2) Neither flagged that the FROZEN-integrity proof method itself (regex count) was measurement-fragile — caught only at build-T2 when the archive baseline diverged 22 vs 121.

**Pattern**:
1. **Execute-don't-reason / recompute-don't-trust is now N≥4 for the Builder's own /critique fix specifically** (slice-032/034/041/042): a Critic finding "count X is wrong" is correctly ACCEPTED-FIXED, but the *replacement* count is transcribed from an earlier non-authoritative grep rather than recomputed via the authoritative anchor. DR-1 B-add-1/2/3 is the structural backstop; the durable cure (applied this slice) is **embed the canonical anchor command in design.md + declare the build-step-1 grep the single source of truth** so narrative counts are reconciled-to-grep, never hand-typed. Strong `/critic-calibrate` input.
2. **slice-032 "a design correction is itself an unguarded surface" recurs at ADR-prose level (N+1)** — the M3-sev fix committed the exact defect (a literal old-name) it was resolving. Backstop = build-T0 repo-wide anchored re-derivation, NOT the Critic/DR-1 stack. Candidate Builder-plan-mode checklist item: "after applying any identifier ACCEPTED-FIXED edit, re-run the authoritative anchor repo-wide before T1."
3. **Measurement-method fragility is a first-class blind spot** — the dual-Critic stack reviews the *claim*, never the *measurement tool's own correctness*. "Prove frozen-set integrity by content hash, not regex count" generalizes to all carve-out/rename slices.

## Lessons for next slice
- **For any identifier/rename/carve-out slice: prove "frozen set untouched" with a regex-independent sha256 tree-hash snapshot (pre/post), never a regex/grep count.** `grep -c`=lines≠occ; Python `(?:)` ≠ ERE. (slice-042 — generalizable; strongest standing process lesson.)
- **For inventory-accuracy slices: embed the authoritative anchor command in design.md and declare the build-step-1 grep the single source of truth; never hand-transcribe counts** (the rev-0→rev-1→rev-2 drift took two Critic layers + build-T0 to converge — the structural cure is to stop transcribing). Candidate `/critic-calibrate` watch-list + Builder-plan-mode checklist item.
- **After applying any identifier-class ACCEPTED-FIXED /critique edit, re-run the authoritative anchor repo-wide at build-T0 before any other edit** — the fix-prose can re-introduce the literal (slice-032 N+1); the Critic/DR-1 stack does not catch this.
- No new RULE-ID / changelog / risk-register state change (conformance-fix; slice-035/036/040 precedent verified against META-1/PMI-1, MEPD-1(b)).

## Vault updates made (thin vault — small list)
- This slice's [[design.md]] — rev-1/rev-2 inventory corrections + grep-predicate-as-SOT restructure (build-log notes the rev chain)
- [[decisions/ADR-044]] — anchor clarified (literal-suffix incl. no-`_sub_` variant; 37 verified)
- [[decisions/ADR-045]] — predicate carve-out; M3-sev narrowing; build-T0 self-contradiction note
- [[shippability.md]] — 69 `::`-selectors realigned in-lockstep (LIVE, local vault) + row #42 added (Step 5.3)
- [[lessons-learned.md]] — slice-042 entry appended
- No ADR superseded; no `risk-register.md` change (R-4 retired by slice-041, no dependency); no `methodology-changelog.md` edit (no version bump — conformance class) — MCFS-1 PASS confirms forward-sync intact
- No `components/`/`contracts/` (thin vault, code is truth)
- **BC-1 promotion: YES (user-approved at Step 5b)** — authored **BC-PROJ-5** ("Identifier/rename/carve-out slices must prove the frozen set untouched by content-hash snapshot, not regex count; drive every count from one authoritative anchor command") into live [[build-checks.md]] + the git-tracked canonical fixture `tests/methodology/fixtures/build_checks/canonical_project_checks.md` + a literal-constant structural pin `test_bc_proj_5_has_expected_structural_identity` in `tests/methodology/test_build_checks_audit.py` (BCI-1 fail-loud discipline; ADR-028 fixture=subject/literal=oracle). BCI-1 PASS exit 0; recursive self-application discharged — BC-PROJ-5 self-fires on slice-042 (Important) and is satisfied (this slice proved frozen by sha256, embedded the anchor command, re-derived at build-T0). No BC-GLOBAL promotion (project-specific to the self-hosting recompute-don't-trust + carve-out class).
