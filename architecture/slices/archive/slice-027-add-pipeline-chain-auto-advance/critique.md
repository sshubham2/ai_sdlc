# Critique: Slice 027 add-pipeline-chain-auto-advance

**Critic reviewed**: mission-brief.md, design.md, ADR-025
**Date**: 2026-05-16
**Result**: NEEDS-FIXES

## Summary

Core mechanism (skill-prose-driven auto-invoke + audit-from-day-one, modeled on BRANCH-1/CRP-1) is sound; fail-closed gate model well-reasoned. The slice-022 self-violation law fired as pre-budgeted: this PCA-1-codifying slice's own artifacts carried a phantom test-path convention break (B1 — the exact PTFCD-1 class) and a wrong version-file path (B2). All findings verified against repo reality and fixed in-round.

## Findings

### Blockers (must address before /build-slice)

#### B1: design.md cited `tests/tools/` — that dir does not exist; convention is `tests/methodology/`
- **Claim under review**: WIRE-1 row + ADR-025 cited `tests/tools/test_pipeline_chain_audit.py::test_clean_chain_exits_zero` / `::test_missing_block_exits_one`.
- **Issue**: No `tests/tools/` dir; every `_CANONICAL_TOOLS` peer's tests live at `tests/methodology/test_<name>.py`. Verified `tests/methodology/test_branch_workflow_audit.py` + `test_critique_review_prerequisite_audit.py`. PTFCD-1 class (Missed-by-Critic N=2) + slice-022 self-violation law.
- **Evidence**: `ls tests/` → only `methodology/`, `skills/`, `README.md`; no `tests/tools/`.
- **Proposed fix**: rewrite all citations to `tests/methodology/test_pipeline_chain_audit.py`.
- **Builder draft**: **ACCEPTED-FIXED** — design.md WIRE-1 row + new convention note; ADR-025 line 89 + revert-path line corrected to `tests/methodology/`.

#### B2: mission-brief AC #5 named `architecture/ai-sdlc-VERSION` — file does not exist
- **Claim under review**: AC #5 "atomic bump across VERSION + plugin.yaml + architecture/ai-sdlc-VERSION".
- **Issue**: No `architecture/ai-sdlc-VERSION`. Canonical PMI-1 triad = in-repo `VERSION` + installed `~/.claude/ai-sdlc-VERSION` (install-time-rename, slice-007-B1 surface) + `plugin.yaml.version`. ADR-025 had it right; mission-brief contradicted this slice's own ADR.
- **Evidence**: `ls architecture/ai-sdlc-VERSION` → absent; `tools/install_audit.py:62 _CANONICAL_METADATA = (..., "ai-sdlc-VERSION")` (installed-side name).
- **Proposed fix**: rewrite AC #5 + verification row + must-not-defer #4 to the correct triad.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief AC #5, verification-plan row 5, must-not-defer #4 all corrected.

### Majors (address this slice)

#### M1: 7-unguarded-skill-pair forward-sync mitigation asserted, not demonstrated
- **Issue**: `install_audit` only existence-checks installed skill dirs (no content compare); only `slice`/`build-slice` have full drift tests. 6 skills' `## Pipeline position` block could go silently stale installed-side — slice-026 M-add-1 watch-list, now load-bearing for runtime behavior. ADR-025's stated mitigation didn't actually cover the class; option (b) would contradict AC #5.
- **Proposed fix**: option (a) — ship a section-scoped parametrized byte-equality test over all 8 skill pairs.
- **Builder draft**: **ACCEPTED-FIXED** — design.md new "AC #5 byte-equality verification element": `tests/methodology/test_pipeline_position_block_drift.py`, parametrized over all 8 pairs, section-scoped. Implementation lands at `/build-slice`.

#### M2: AC #5 byte-equality claim over 8 files, verification element for only 1 (Wiegers traceability)
- **Issue**: same root cause as M1 — AC #5 unverifiable for 6 of 8 skills as originally designed.
- **Proposed fix**: M1's parametrized test enumerating all 8 pairs gives AC #5 a 1:1 traceable element.
- **Builder draft**: **ACCEPTED-FIXED** — discharged by the M1 element (explicitly enumerates all 8 skill pairs).

#### M3: gate enumeration completeness — `/critique-review` / `/slice` / `/design-slice` halts unstated; must-not-defer #1 demands explicit completeness
- **Issue**: 5-gate list covered only `/critique`/`/build-slice`/`/validate-slice`. `/critique-review` is a DR-1 adjudication step inside the auto-advancing chain with no explicit pause; must-not-defer #1 elevates completeness to critical — silence (reliance on the catch-all alone) not acceptable.
- **Proposed fix**: add explicit halt conditions OR an explicit no-gap statement for every skill.
- **Builder draft**: **ACCEPTED-FIXED** — design.md new per-skill "Canonical gate enumeration — explicitly COMPLETE per 8-skill coverage" table (incl. `/critique-review` no-gap reasoning: its non-clean output is reconciled *at* `/critique` TRI-1, the enumerated HALT); ADR-025 reference paragraph added (RPCD-1 canonical-once).

### Minors (log; address if cheap)

#### m1: ADR-025 line 17 "`adopt` has two `Next step` blocks" — imprecise
- **Issue**: `adopt` has one H2 `## Next step` (L456) + one inline `Next step:` label (L425), not "two blocks".
- **Builder draft**: **ACCEPTED-FIXED** — reworded to "both an H2 `## Next step` and a separate inline `Next step:` prose label".

#### m2: new-tool consumer-propagation roll-up sentinel (N=5) — confirm all sites
- **Issue**: confirm `_CANONICAL_TOOLS` + `plugin.yaml` + UTF8-STDOUT-1 conformance + hard-coded "19 tool modules" narrative (`install_audit.py:66`) all propagated.
- **Builder draft**: **ACCEPTED-FIXED** — design.md propagation checklist added, explicitly incl. the `:66` "19 → 20" comment bump + UTF8-STDOUT-1 + Step 6 bullet.

#### m3: pre-named function-level-PTFCD-1 slice-027 candidate was deferred; B1 corroborates the live gap
- **Issue**: not a slice-027 design defect (user's scoping is legitimate); B1 is empirical evidence the deferred candidate remains live.
- **Builder draft**: **ACCEPTED-PENDING** — no slice-027 change; `/reflect` will note B1 as corroborating evidence and strengthen the function-level-PTFCD-1 candidate priority for slice-028.

## Dimensions checked
- [x] Unfounded assumptions — M3, M1
- [x] Missing edge cases — M3 (human-decision step inside auto-advancing chain)
- [x] Over-engineering — none (audit justified by ADR-019 cost-asymmetry; `commit-slice` in coverage closes the graph)
- [x] Under-engineering — B2, M2 (AC #5 traceability)
- [x] Contract gaps — none beyond M3 (`## Pipeline position` schema well-formed; RPCD-1 canonical-once correct; audit exit 0/1/2 mirrors BRANCH-1/CRP-1)
- [x] Security — none (fail-closed posture correct; central hazard handled fail-closed)
- [x] Drift from vault — B1, B2 (ADR-025 conforms to ADR-019 NON-`-D`; v0.41.0 correctly not-yet-existing; shippability 26→27 consistent)
- [x] Web-known issues — none blocking (SKILL.md-prose auto-invoke is a supported documented pattern; Claude-mediated orchestration caveat noted, consistent with design)
- [x] Cross-cutting conformance — B1 (test-location convention), B2 (install-time-rename surface), M1 (M-add-1 watch-list), m2 (sentinel N=5); slice-022 self-violation law fired as pre-budgeted (B1); bootstrap self-application correctly discharged

## Triage

**Triaged by**: user
**Date**: 2026-05-16
**Final verdict**: NEEDS-FIXES

Reconciled across both passes (`/critique` first Critic + `/critique-review` meta-Critic EXTEND). User ratified all Builder drafts ("accept all"). m3 ACCEPTED-PENDING (a `/reflect` note, not a `/build-slice` blocker) → mechanical verdict NEEDS-FIXES; no ESCALATED so not BLOCKED.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md/ADR-025 `tests/tools/`→`tests/methodology/`; verified no `tests/tools/` dir |
| B2 | Blocker | ACCEPTED-FIXED | mission-brief AC#5/row5/MND#4 → in-repo `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`; verified no `architecture/ai-sdlc-VERSION` |
| M1 | Major | ACCEPTED-FIXED | design.md ships parametrized 8-pair `tests/methodology/test_pipeline_position_block_drift.py` (section-scoped) |
| M2 | Major | ACCEPTED-FIXED | same element as M1 → AC#5 1:1 traceable for all 8 skill pairs |
| M3 | Major | ACCEPTED-FIXED | design.md per-skill completeness table + ADR-025 ref; explicit `/critique-review` no-gap reasoning |
| m1 | Minor | ACCEPTED-FIXED | ADR-025 L17 reworded ("both an H2 + an inline label") |
| m2 | Minor | ACCEPTED-FIXED | design.md propagation checklist incl. `install_audit.py:66` "19→20" narrative |
| m3 | Minor | ACCEPTED-PENDING | `/reflect` notes B1 as corroborating evidence for slice-028 function-level-PTFCD-1 candidate; no slice-027 artifact change |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic) `/validate-slice` PARTIAL → HALT row added to design.md gate table + ADR-025 canonical enumeration |
| m-add-1 | Minor | ACCEPTED-FIXED | (meta-Critic) design.md§contracts: verdict-dependent successor in `on-clean-completion`; audit tolerates `/critique` BLOCKED self-edge |
