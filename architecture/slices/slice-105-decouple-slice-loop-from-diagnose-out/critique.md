# Critique: Slice 105 decouple-slice-loop-from-diagnose-out

**Critic reviewed**: mission-brief.md, design.md, ADR-094, ADR-095, project-frame.md, action-points.md
**Date**: 2026-06-03
**Result**: CLEAN (post-TRI-1 — first Critic recommended BLOCKED; all 9 first-Critic + 4 meta-Critic findings ratified **ACCEPTED-FIXED**)
**Critic agent**: subagent `critique` (a991d001 — 39 tool uses, verified claims against implementation)

## Summary

The core decoupling is sound and well-evidenced: `test_bcr_1_round_trip_end_to_end.py` is genuinely the *sole* live `diagnose-out/backlog.md` reader (Critic verified every other apparent seed-consumer reads a fixture/tmp_path/mock), so deleting it really closes the seed need; `branch_workflow_audit.py` imports only path/branch helpers (verified) — removing `seed_derived_dirs` won't break it. But the SUP-1 partial-supersession plan contradicted a **test-pinned** ADR-family convention (B1), and the shippability "remove rows" plan would have deleted rows other tests require while leaving phantom test-file citations (B2/M1). Both were build-breakers. All findings have been fixed at the design level.

## Findings

### Blockers (must address before /build-slice)

#### B1: SUP-1 plan to add a `superseded-by:` pointer to ADR-055/ADR-090 violates the test-pinned append-only ADR convention
- **Claim under review**: design.md §"SUP-1 partial-supersession handling" — "each original ADR gets an **append-only** `superseded-by: ADR-NNN (partial — <half>)` pointer note." Mirrored in ADR-094 + ADR-095 Consequences/Decision.
- **Issue**: `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py::test_adr_019_unmodified_per_append_only_rule` codifies that supersession is encoded ONLY at the successor's `supersedes:` slot, NEVER reverse-linked from the superseded ADR. Live precedent confirms: ADR-019 (twice partial-superseded) carries no `superseded-by`; ADR-063 (partial-superseded by ADR-090) was left unmodified. The design cited "BRANCH-3 partial-supersedes ADR-063" as the pattern to mirror but proposed the *opposite* of what that precedent did. Adding a pointer note would itself violate append-only.
- **Evidence**: `test_adr_063_exists_and_supersedes_adr_019.py:89-119`; `ADR-019-*.md:1-9`; `ADR-063-*.md:1-9`; CLAUDE.md §Vault discipline.
- **Proposed fix**: Leave ADR-055 + ADR-090 byte-unmodified; encode supersession only at ADR-094/ADR-095 `supersedes:` + body scope-line.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §SUP-1 rewritten to "originals stay BYTE-UNMODIFIED; encoded only at successor `supersedes:` + body scope-line; per `test_adr_019_unmodified_per_append_only_rule`"; ADR-094 Consequences + ADR-095 Decision corrected to strike the pointer-note plan. The design's flagged "highest-judgement call" is resolved: do nothing to the originals.

#### B2: "Remove shippability rows L64/L66" deletes rows that other tests require to exist + leaves phantom citations (PTFCD-1)
- **Claim under review**: design.md "L64 + L66 (`test_bcr_1_round_trip_end_to_end` → remove)"; mission-brief AC4.
- **Issue**: shippability L64 = catalog **row #54** (slice-054/PVFS-1), L66 = **row #56** (slice-056/R-15). `test_methodology_changelog.py:3724` asserts row #54 present (+PVFS-1+SC-001); `:3768` asserts row #56 present (+R-15). Deleting the rows breaks both. Keeping the rows but leaving the deleted test's token in their `Command` cells fires `shippability_path_audit.py` (PTFCD-1) `missing-test-path-file` at /validate-slice Step 5.5. "→ remove" was ambiguous between row-delete and token-delete.
- **Evidence**: `shippability.md:64,66`; `test_methodology_changelog.py:3724-3765,3768-3806`; CLAUDE.md PTFCD-1.
- **Proposed fix**: Keep rows #54/#56; drop only the `test_bcr_1_round_trip_end_to_end.py::...` token from both command-cell copies; verify row #54 retains PVFS-1+SC-001, row #56 retains R-15; reword the round-trip narratives to past-tense.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"Vault / config surfaces" reworked with explicit "NEVER delete a row — edit command-cell token(s) only" + per-row plan for #54/#56, the verify-still-contains checks, and the narrative reword.

### Majors (address this slice)

#### M1: slice-079 row #79 runs `test_build_slice_skill_cp_r_step.py`, which this slice deletes (PTFCD-1)
- **Issue**: shippability L87 = row #79 (slice-079), command runs `test_build_slice_skill_cp_r_step.py` alongside 4 other tests; the row must survive. Same row-vs-token ambiguity as B2.
- **Evidence**: `shippability.md:87`.
- **Proposed fix**: Keep row #79; drop only the cp_r-test token; keep its 4 other tokens.
- **Builder draft**: **ACCEPTED-FIXED** — design.md per-row plan adds row #79 to the "drop token, keep row + 4 survivors" list.

#### M2: removing the point-4 cp-r (L96-97) breaks `test_build_slice_skill_cp_r_step.py` sibling assertions before it's deleted + stale row #107 narrative
- **Issue**: (1) `test_build_slice_skill_cp_r_step.py:52,113` assert `seed_derived_dirs in section` + `len(cp_r)==2`; editing the SKILL.md prose before deleting the test fails the suite — needs atomic batch. (2) shippability row #107 (slice-099, L116) narrative claims "primary create path seeds via `seed_derived_dirs`" + "guarded cp -r count is 2" + matching regression clauses — false after this slice (`test_v_0_81_0_branch_3_shippability_consumer_propagation` won't fail, but the narrative is stale-by-construction → /drift-check).
- **Evidence**: `test_build_slice_skill_cp_r_step.py:52,113`; `build-slice/SKILL.md:67,76,96-97`; `shippability.md:116`.
- **Proposed fix**: Atomic delete+edit batch note; rewrite row #107 narrative dropping seed/cp-r-count claims + regression clauses, keep BRANCH-3/ADR-090/R-31/pick/AC5/Pick log.
- **Builder draft**: **ACCEPTED-FIXED** — design.md adds the build-sequencing atomic-batch note + the row #107 narrative-correction scope.

#### M3: AC1 delete-vs-fixture refinement not back-propagated to mission-brief — TPHD-1 sub-mode (a) / AP-17
- **Issue**: design.md decides to *delete* the test; mission-brief AC1 + verification-plan row 1 still said *fixture* → AC1 unsatisfiable as worded; milestone.md already said "deleted" (propagation was partial).
- **Evidence**: mission-brief.md:18,28 (was "fixture"); design.md:10-12; milestone.md:28.
- **Proposed fix**: Rewrite mission-brief AC1 + verification row 1 to "deleted / verify absent + seedless suite green."
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief AC1, verification row 1, and the smoke-gate wording harmonized to "deleted."

#### M4: missing v0.82.0 changelog entry-pin test + shippability row for the slice's own version bump (RPCD-1 / paired-entry-pin)
- **Issue**: design adds a v0.82.0 changelog entry + version cascade but planned no `test_v_0_82_0_*` entry-pin, no propagation test, no new slice-105 catalog row — breaking the slice-099 `test_v_0_81_0_branch_3_*` paired-pin precedent; the slice's own critical path goes uncatalogued.
- **Evidence**: `test_methodology_changelog.py:5603,5672`; CLAUDE.md RPCD-1/SCPD-1; META-1 `:130`.
- **Proposed fix**: Add `test_v_0_82_0_decouple_entry_present_in_repo` + paired propagation test + a new Row #105 citing ADR-094/ADR-095/R-20.
- **Builder draft**: **ACCEPTED-FIXED** — design.md "Tests touched" adds the entry-pin + propagation tests; "Vault / config surfaces" adds NEW Row #105.

#### M5: `/slice` Step-renumber cross-references not enumerated (FBCD-1 within-file)
- **Issue**: renumbering Step 5.5 (remove seed Step 3; Write→3, queue→4) leaves the downstream "Step-5 (queue-commit) failure" orphan-worktree narrative (`slice/SKILL.md:~257`) pointing at the old number.
- **Evidence**: `slice/SKILL.md:249-257`.
- **Proposed fix**: Grep the section for Step 3/4/5 refs after renumber; update "Step-5" → "Step-4"; mirror to installed copy.
- **Builder draft**: **ACCEPTED-FIXED** — design.md /slice bullet adds the within-file cross-ref-propagation + OSDG-1-mirror instruction.

### Minors (log; address if cheap)

#### m1: version-cascade enumeration omits `plugin.yaml.version` explicitly
- **Proposed fix**: enumerate all five surfaces (VERSION + plugin.yaml + pyproject + ai-sdlc-VERSION + methodology-changelog header) with their gates.
- **Builder draft**: **ACCEPTED-FIXED** — design.md version-cascade line now names all five surfaces + their gates (PMI-1/PVFS-1/AVFS-1/MCFS-1) + the AP-10 old-literal grep.

#### m2: mid-slice smoke gate renames graphify-out aside — a concurrent graph need could surface a false failure
- **Note**: Critic says "largely covered by the existing STOP-find-it instruction; log only."
- **Builder draft**: **ACCEPTED-FIXED** — smoke-gate "Expected" line annotated that a non-slice failure indicates a different latent live-derived-dir reader (m2).

## Dimensions checked
- [x] Unfounded assumptions — none; the design's empirical claims (sole live reader; audit import surface; vault_flip_readiness non-scan of `_worktree_paths`) all verified against implementation.
- [x] Missing edge cases — graceful-degrade correctly moot post-removal; build-sequencing edge → M2.
- [x] Over-engineering — none (slice removes mechanism; delete-vs-fixture is the simpler choice).
- [x] Under-engineering — M4 (missing entry-pin/row), M3 (AC1 had no deliverable as worded).
- [x] Contract gaps — methodology contract (BCR-1 → consume-only) recorded in ADR-095 + changelog + CLAUDE.md; consume-side retained + pinned by tests #1-#3.
- [x] Security — none (methodology slice; removing the worktree copy reduces derived-data sprawl).
- [x] Drift from vault — B1 (SUP-1 vs append-only convention) + M2 (stale row #107 narrative).
- [x] Web-known issues — N/A (pure in-house methodology slice; WebSearch not applicable, by reasoned exclusion).
- [x] Cross-cutting conformance — PTFCD-1 (B2/M1), SCPD-1/RPCD-1/AP-13 (B2/M1/M2/M4), FBCD-1 (M3/M5), MEPD-1/META-1 (M4). Sibling tests `test_build_slice_skill_branch_state_preamble.py` + `_dirty_tree_resolution.py` verified to survive the `### Branch state` edits.

## Triage

**Triaged by**: user
**Date**: 2026-06-03
**Final verdict**: CLEAN

Reconciles BOTH passes (first Critic `critique.md` + meta-Critic `critique-review.md`). Meta-Critic added B-add-1 / M-add-1 / M-add-2 + the label defect (all VALID); no SUSPICIOUS findings, no severity adjustments. All dispositions ACCEPTED-FIXED → verdict CLEAN.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §SUP-1 + ADR-094/ADR-095: originals byte-unmodified; supersession only at successor `supersedes:` |
| B2 | Blocker | ACCEPTED-FIXED | design.md §shippability: edit command-cell token, never delete row #54/#56 |
| B-add-1 | Blocker | ACCEPTED-FIXED | design.md test-row + mission-brief must-not-defer: delete/invert `test_resolve_slice_dir.py:77` is_file guard in same batch |
| M1 | Major | ACCEPTED-FIXED | design.md: row #79 drop token, keep row + 4 survivors |
| M2 | Major | ACCEPTED-FIXED | design.md: atomic-batch note + row #107 narrative rewrite |
| M-add-1 | Major | ACCEPTED-FIXED | design.md: build-sequencing extended to 3 atomic prose↔test pairs (incl. reflect) |
| M-add-2 | Major | ACCEPTED-FIXED | design.md: `test_worktree_paths.py:17` import removal made explicit |
| M3 | Major | ACCEPTED-FIXED | mission-brief AC1 + verification row 1 + smoke-gate harmonized to "delete" |
| M4 | Major | ACCEPTED-FIXED | design.md: v0.82.0 entry-pin + propagation test + Row #105 added |
| M5 | Major | ACCEPTED-FIXED | design.md: /slice step-renumber cross-ref propagation note |
| m1 | Minor | ACCEPTED-FIXED | design.md: 5 version surfaces enumerated |
| m2 | Minor | ACCEPTED-FIXED | mission-brief smoke-gate note |
| label | Note | ACCEPTED-FIXED | design.md: "Row #63" → "catalog row #53 (L63)"; row #107 narrative-only clarified |
