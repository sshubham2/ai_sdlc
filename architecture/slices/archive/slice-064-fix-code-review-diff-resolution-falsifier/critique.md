# Critique: Slice 064 fix-code-review-diff-resolution-falsifier

**Critic reviewed**: mission-brief.md, design.md, ADR-062
**Date**: 2026-05-23
**Result**: CLEAN

(Post-TRI-1 rename per /critique skill v0.11.0 — the original Critic verdict was BLOCKED; after user-ratified ACCEPTED-FIXED dispositions across all 14 findings, the final computed verdict is CLEAN.)

## Summary

Intent (mirror NAW-1's union-of-three-sources read mechanism onto `/code-review` SKILL.md Step 1) is correct and the BFRD-1 repro test is genuinely WRITTEN-FAILING. But the TF-1 plan in mission-brief.md ships a phantom test path + phantom test function at AC#4 — empirically rejected by `tools/test_first_audit --strict-pre-finish` with a `missing-test-path-file` (PTFCD-1) violation — AND design.md L17 unilaterally enumerates an entry-pin pair while mission-brief AC#5 plans only the entry-pin half (the shippability-consumer-propagation paired pin is missing — slice-060 M-add-2 / N≥17 BC-PROJ-10:173 recurrence). Both are Blockers because they will fail `/build-slice` Step 6 strict-pre-finish under PTFCD-1 + PTFFD-1 + TF-1 row-coverage axes.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC#4 cites a phantom test path AND a phantom test function — PTFCD-1 + PTFFD-1 double violation
- **Claim under review**: `mission-brief.md:33` — `| 4 | drift-guard | tests/skills/code_review/test_code_review_skill_drift.py | test_code_review_skill_md_forward_synced_modulo_eol | PASSING |`
- **Issue**: Empirically verified — both the cited test path and the cited test function name are phantom: `tests/skills/code_review/test_code_review_skill_drift.py` does NOT exist on disk; actual drift-guard is at `tests/methodology/test_code_review_skill_drift.py`. Function `test_code_review_skill_md_forward_synced_modulo_eol` does NOT exist; actual function (verified at `tests/methodology/test_code_review_skill_drift.py:26`) is `test_in_repo_and_installed_code_review_skill_md_are_content_equal`. PTFCD-1: a PASSING row may not cite a phantom test file. Same class as slice-023 B4 / slice-024.
- **Evidence**: `$PY -m tools.test_first_audit --strict-pre-finish architecture/slices/slice-064-fix-code-review-diff-resolution-falsifier` returns a `[Important] missing-test-path-file (AC#4)` violation. `Glob tests/skills/code_review/*.py` returns only `__init__.py` + `test_code_review_skill.py`. `Grep "def test_" tests/methodology/test_code_review_skill_drift.py` returns only `test_in_repo_and_installed_code_review_skill_md_are_content_equal`.
- **Proposed fix**: Edit mission-brief.md:33 AC#4 row to: `| 4 | drift-guard | tests/methodology/test_code_review_skill_drift.py | test_in_repo_and_installed_code_review_skill_md_are_content_equal | PASSING |`. Sweep all sites (design.md "What's reused" L23; mission-brief Verification plan row #4 cross-reference).
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md:33 AC#4 row + mission-brief.md:46 Verification plan row #4 + design.md L23. Per TPHD-1 sub-mode (a), all three sites harmonized in same fix block.

#### B2: design.md L17 entry-pin pair enumerated but mission-brief AC#5 plans only entry-pin half — consumer-propagation pin missing (slice-060 M-add-2 / N≥17 BC-PROJ-10:173 recurrence)
- **Claim under review**: `design.md:17` enumerates TWO tests (`test_v_0_67_0_naw_extend_entry_present_in_repo` + `test_v_0_67_0_naw_extend_shippability_consumer_propagation`) vs `mission-brief.md:34` which has ONE row with the disjunctive placeholder `test_v_0_67_0_or_no_bump_entry_present_in_repo_or_documented_skip`.
- **Issue**: Every Inclusion-heuristic-firing version-bump slice from slice-049 onward has shipped an entry-pin + a paired shippability-consumer-propagation pin (shippability rows #50/#51/#53/#54/#55/#57/#58/#59/#60/#62/#63 Command cells — all carry both `_entry_present_in_repo` and `_shippability_consumer_propagation`). slice-060 /critique-review M-add-2 explicitly named this paired-test class with "N≥17 instances". TF-1 row-coverage axis under FBCD-1 sub-mode (a) — design.md and mission-brief disagree on test count.
- **Evidence**: shippability row #63 (slice-063 NAW-1 entry-pin pair) Command cell shows BOTH `test_v_0_66_0_naw_1_entry_present_in_repo` AND `test_v_0_66_0_naw_1_shippability_consumer_propagation`. design.md L17 + L116 explicitly plan the pair; mission-brief AC#5 row only cites the first.
- **Proposed fix**: (a) Rename mission-brief.md:34 AC#5 function from disjunctive placeholder to design.md L17 locked name `test_v_0_67_0_naw_extend_entry_present_in_repo`. (b) Add second AC#5 row: `| 5 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_67_0_naw_extend_shippability_consumer_propagation | PENDING |`. (c) Update mission-brief.md:36 stale note ("AC 5's exact test name + entry-vs-skip shape is locked at /design-slice") to reflect post-design-locked state. Per slice-063 M-add-2 EPGD-1 fix-block precedent.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md:34 + new row + mission-brief.md:36 stale-note update. Per TPHD-1 sub-mode (a) cross-file harmonization. Also covers m2 (same fix).

### Majors (address this slice)

#### M1: ADR-062 §Decision Step 1 bash array syntax (`exclude=( … )` + `"${exclude[@]}"`) is bash-specific, not POSIX-portable
- **Claim under review**: `ADR-062:57-71` proposed Step 1 block uses bash-array.
- **Issue**: POSIX `sh` does not support indexed arrays. Claude Code's bash tool typically runs under bash on Unix and PowerShell on Windows. The existing SKILL.md Step 1 (L40-43) uses inline literal pathspecs (no array). NAW-1's own implementation uses Python `subprocess.run(…)` with literal args (`tools/new_agent_warning_audit.py:212-226`) — the "shape mirror" claim is on the conceptual three-source pattern, not literal shell form.
- **Evidence**: ADR-062:61 `exclude=( ':(exclude)architecture/**' ':(exclude)docs/**' )`; ADR-062:64/67/70 each use `-- "${exclude[@]}"`. The slice-021 BRANCH-1 pattern this skill mirrors is POSIX-sh-compatible.
- **Proposed fix**: Replace array form with inline literal pathspecs on each leg (matching existing Step 1 style).
- **Builder draft**: ACCEPTED-FIXED at ADR-062 §Decision Step 1 block (inline pathspecs on each leg).

#### M2: No runtime-aggregation prose-pin — AC#1 test only pins shape (three commands present), not the union-and-deduplicate runtime obligation
- **Claim under review**: ADR-062:73 documents the union obligation; SKILL.md Step 1 post-fix prose ends at the third bash command without an explicit "union the three outputs by path; deduplicate" instruction. Per CLAUDE.md "skill prose IS executable contract": Claude reads SKILL.md at runtime, not ADR-062.
- **Issue**: A future Claude could plausibly run only Source (iii) for token budget, concatenate without deduplicating producing duplicate review work, intersect instead of union, or ignore Source (ii). AC#1 test pins filter shape only — not aggregation behavior. The fix is silently relocatable to "first command wins" without violating any structural test.
- **Evidence**: ADR-062:73 has the union statement; SKILL.md Step 1 post-fix per ADR-062:57-71 ends at the third command. design.md L94-103 Phase A/B don't add a "union prose pin" test.
- **Proposed fix**: (a) Add explicit SKILL.md Step 1 post-bash-block prose: "Union the three outputs by path; deduplicate. The resulting file list is the in-scope diff scope handed to Step 2." (b) Add a fourth structural-anchor test `test_skill_md_step_1_union_aggregation_prose_pinned` asserting that union-instruction substring presence. Add to AC#1 TF-1 plan as a sibling row.
- **Builder draft**: ACCEPTED-FIXED at ADR-062 §Decision Step 1 block (add union prose instruction) + design.md "What's new" + new TF-1 plan row + AC#1 sibling test.

#### M3: Step 2 per-file diff form increases prompt-token surface for wide slices; existing fallback prose ("if diff exceeds budget, list paths and let agent Read individual files") is described as "still applies" but not load-bearing-tested
- **Claim under review**: ADR-062:75-84 changes Step 2 from aggregate (`git diff <base>...HEAD -- <files>`) to per-file (`git diff "$base" -- <file>`).
- **Issue**: Per-file form scales O(N) in git-invocations + per-file headers vs aggregate's single invocation. For a wide-refactor slice with 30+ files (slice-060 touched ~20; slice-063 NAW-1 touched 8) the per-file form adds 30+ git invocations + headers + command overhead, increasing prompt tokens. No test pins the fallback prose post-fix; no budget threshold pinned.
- **Evidence**: SKILL.md L85 (current) carries the fallback prose; ADR-062:84 claims it "still applies" but no test verifies. design.md L9 documents the per-file change without quantifying when fallback triggers.
- **Proposed fix**: Lighter-touch option (b) — document the wide-slice load-edge-case explicitly in design.md "Risks specific to this slice" as a recognized N=1 watch-list item.
- **Builder draft**: ACCEPTED-FIXED at design.md "Risks specific to this slice" (add R-X3 watch-list entry for wide-slice per-file Step 2 token cost; N=1 → /critic-calibrate candidate if N=2 emerges).

#### M4: design.md L84 BC-PROJ-9 5-inventory enumeration drifts from slice-063 shippability row #63 canonical 5-set
- **Claim under review**: design.md:84 lists `_CANONICAL_TOOLS` / `_ROOT_ONLY_TOOLS` / `plugin.yaml` tools-block / `INSTALL.md` tool-count literals / `_CANONICAL_AGENTS`.
- **Issue**: Per shippability row #63 (slice-063 NAW-1) the canonical 5-set is: `install_audit._CANONICAL_TOOLS` + `test_utf8_stdout._ROOT_ONLY_TOOLS` + `plugin.yaml tools block` + `INSTALL.md tool-count literal at L22 + L166` + the new shippability row. design.md L84 substitutes `_CANONICAL_AGENTS` for the new shippability row.
- **Evidence**: shippability row #63 Description cell verbatim. design.md L84 differs.
- **Proposed fix**: Rewrite design.md L84 to cite slice-063 row #63 canonical 5-set verbatim, noting that for slice-064 the first 4 inventories are UNCHANGED (no new tool) and the 5th (shippability row #64) IS new.
- **Builder draft**: ACCEPTED-FIXED at design.md L84 (canonical 5-set enumeration synced to slice-063 precedent).

### Minors (log; address if cheap)

#### m1: EPGD-1 8-anchor list missing "mints no new rule + supersedes nothing" lineage anchor
- **Claim under review**: design.md:17 — "EPGD-1 8-anchor list: header + Rule reference + NAW-1 + ADR-062 + 5-part PMI-1 + extend-pattern + /code-review-surface + Inclusion-heuristic literals".
- **Issue**: Per slice-063 v0.66.0 entry-pin precedent at `test_methodology_changelog.py:4184-4204`, the canonical Inclusion-heuristic-firing entry-pin includes a `mints a new rule` (or `mints no new rule`) + `supersedes nothing` lineage anchor. ADR-062 is "mints no new rule, supersedes nothing"; design.md L17 enumeration omits this. Slice-062 /critique-review M-add-2 pinned this exact class.
- **Proposed fix**: Add anchor (i) to design.md L17 enumeration: `+ "mints no new rule" + "supersedes nothing" lineage clauses`; update count 8 → 9.
- **Builder draft**: ACCEPTED-FIXED at design.md L17 (anchor count 8→9; lineage anchor added).

#### m2: mission-brief AC#5 disjunctive placeholder name will fail PTFFD-1 once design.md locks Inclusion-heuristic
- **Issue**: Covered by B2 fix above. Disjunctive placeholder name (`test_v_0_67_0_or_no_bump_entry_present_in_repo_or_documented_skip`) is stale post-design; the Inclusion-heuristic-FIRES decision at design.md L83 + ADR-062 §Decision locks the entry-bearing branch.
- **Builder draft**: ACCEPTED-FIXED — covered by B2 fix.

#### m3: mission-brief frontmatter `Test-first: true  <!-- … -->` trailing HTML comment — R-7 latent footgun shape
- **Issue**: Empirically verified the audit accepts the comment (TF-1 returned 5 row-level violations, not "Test-first: false → audit skipped"). Hygiene-only minor; not changing.
- **Builder draft**: OVERRIDDEN — empirically verified tolerated; the convention is acceptable per slice-061 mission-brief precedent. Rationale: changing prose for cosmetic-only reasons risks introducing drift without removing any audit-time risk.

#### m4: N=7 vs N=8 count drift between ADR-062 and design.md (FBCD-1 sub-mode (a))
- **Claim under review**: ADR-062:100 "N=7 cumulative: slice-049/050/051/057/058/059/062 + this" (7 prior + this = 8 total); design.md:83 "N=7 ... + slice-064 = N=7" (internally inconsistent — 7 + 1 = 8 not 7).
- **Proposed fix**: Standardize both surfaces to N=7 prior + slice-064 = N=8 cumulative inclusive.
- **Builder draft**: ACCEPTED-FIXED at ADR-062:100 + design.md:83 (both standardized to "N=8 cumulative inclusive of slice-064").

#### m5: design.md L130 "SOLE forward-sync" misleading — slice touches MCFS-1 + AVFS-1 + PVFS-1 + PMI-1 too
- **Claim under review**: design.md:130 "OSDG-1 mini-CAD member `skills/code-review/SKILL.md` is the SOLE forward-sync surface this slice touches".
- **Issue**: Next sentence acknowledges MCFS-1 + AVFS-1 forward-syncs. "SOLE" is misleading; per Sommerville requirements-design traceability the wording should be qualified.
- **Proposed fix**: Rewrite design.md L130 to: "OSDG-1 mini-CAD member `skills/code-review/SKILL.md` is the SOLE *new-surface* forward-sync this slice touches; the standard version-bump forward-syncs (MCFS-1 + AVFS-1 + PVFS-1 + PMI-1) are mechanical copies governed by their pre-existing gates."
- **Builder draft**: ACCEPTED-FIXED at design.md L130 (wording qualified).

## Dimensions checked

- [x] Unfounded assumptions — B1 (AC#4 phantom file + phantom function; empirically verified), m3 (Test-first comment annotation tolerance verified empirically not assumed)
- [x] Missing edge cases — M3 (per-file Step 2 form not load-tested for wide slices); m3 (R-7 footgun shape verified empirically)
- [x] Over-engineering — none (slice is surgical; ADR-062 explicitly rejected Route C on over-engineering grounds)
- [x] Under-engineering — B2 (consumer-propagation paired pin missing); M2 (no runtime-aggregation prose-pin)
- [x] Contract gaps — M2 (Claude's runtime union obligation not prose-pinned); M3 (per-file form lacks budget threshold pin)
- [x] Security — none
- [x] Drift from vault — M4 (BC-PROJ-9 5-inventory enumeration drift); m4 (N-count drift); m5 ("SOLE forward-sync" misleading)
- [x] Web-known issues — empirically verified `git ls-files --others --exclude-standard -- ':(exclude)…'` syntax + `git diff "$base"` working-tree-vs-base form per git-scm.com docs. M1 raises portability concern about bash-array.
- [x] Cross-cutting conformance — B1 (PTFCD-1+PTFFD-1); B2 (TF-1 row-coverage / FBCD-1 sub-mode (a)); M4 (BC-PROJ-9); m1 (EPGD-1 anchor completeness); m2 (TF-1 PTFFD-1); m4 (FBCD-1 sub-mode (a)); m5 (FBCD-1)

## Triage

**Triaged by**: user
**Date**: 2026-05-23
**Final verdict**: CLEAN

| ID | Severity | Disposition (Builder draft) | Rationale |
|----|----------|----------------------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | mission-brief.md:33 + Verification row #4 + design.md L23 sites harmonized (TPHD-1 sub-mode (a)) |
| B2 | Blocker | ACCEPTED-FIXED | mission-brief.md:34 renamed + new row added + L36 stale-note updated (TPHD-1) |
| M1 | Major | ACCEPTED-FIXED | ADR-062 §Decision Step 1 block: array syntax → inline literal pathspecs |
| M2 | Major | ACCEPTED-FIXED | ADR-062 + design.md + new test `test_skill_md_step_1_union_aggregation_prose_pinned` + AC#1 sibling row |
| M3 | Major | ACCEPTED-FIXED | design.md "Risks specific to this slice" — added R-X3 watch-list (lighter-touch option b) |
| M4 | Major | ACCEPTED-FIXED | design.md L84 enumeration synced to slice-063 row #63 canonical 5-set |
| m1 | Minor | ACCEPTED-FIXED | design.md L17 — anchor count 8→9; lineage anchor added |
| m2 | Minor | ACCEPTED-FIXED | covered by B2 |
| m3 | Minor | OVERRIDDEN | empirically verified the comment is tolerated by TF-1 audit; cosmetic-only |
| m4 | Minor | ACCEPTED-FIXED | ADR-062:100 + design.md:83 standardized to N=8 cumulative inclusive |
| m5 | Minor | ACCEPTED-FIXED | design.md L130 "SOLE forward-sync" wording qualified |
| M-add-1 | Major | ACCEPTED-FIXED | meta-Critic missed finding: TPHD-1 sub-mode (a) sweep INCOMPLETE — 3 residual stale-path sites (mission-brief.md L21 + L78 + design.md L109) corrected at /critique-review fix block |
| M-add-2 | Minor | ACCEPTED-FIXED | meta-Critic missed finding: anchor-count drift ADR-062 "8-anchor" vs design.md "9-anchor"; standardized to 8 (compound lineage clause per slice-063 precedent) |
| M-add-3 | Minor | ACCEPTED-FIXED | meta-Critic missed finding: design.md L18 EPGD-1 enumeration missing rule-name-expansion anchor; added "Extend NAW-1 union-of-three-sources to /code-review" anchor per slice-063 anchor (d) precedent |
