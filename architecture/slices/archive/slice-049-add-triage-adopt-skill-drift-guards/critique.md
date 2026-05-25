# Critique: Slice 049 add-triage-adopt-skill-drift-guards

**Critic reviewed**: mission-brief.md, design.md, new ADRs (none at review time — rev-0 design.md explicitly locked no new ADR)
**Date**: 2026-05-19
**Result**: NEEDS-FIXES

## Summary

The core mechanism (extend the established mini-CAD per-file pattern to triage/adopt) is sound and the `.gitattributes` glob already covers both new surfaces with zero gap. But the load-bearing MEPD-1(b) "no changelog/VERSION bump" pre-decision rested on a **factually false precedent** (B2 — slice-035 did NOT add the build/commit skill-drift tests; slice-021 did, while already bumping for BRANCH-1), the TF-1 plan cited a **phantom test file** (B1 — `test_shippability_catalog.py` does not exist; PTFCD-1), AC3/AC4 were prose-only rows that fail `--strict-pre-finish` per the slice-045 law (M1), and the "forward-sync first" sequencing can mask a real pre-existing drift (M2). All Critic findings independently re-verified by the Builder against the real artifacts before disposition.

## Findings

### Blockers (must address before /build-slice)

#### B1: TF-1 plan cites a phantom test file — `tests/methodology/test_shippability_catalog.py` does not exist (PTFCD-1)
- **Claim under review**: rev-0 TF-1 plan AC4 `Test path` = `tests/methodology/test_shippability_catalog.py`; verification #4 "the catalog runner executes both rows green".
- **Issue**: No such file on disk. Real files: `test_ptffd1_shippability_path_audit.py`, `test_shippability_command_column.py`, `test_shippability_decoupling_audit.py`, `test_shippability_path_existence.py`, `test_shippability_runner_segment_contract.py`. The runner is `tools/shippability_runner.py`. `tools/test_first_audit.py --strict-pre-finish` emits `missing-test-path-file` and FAILs at /build-slice Step 6 on a phantom path (PTFCD-1 class).
- **Evidence**: Builder re-verified — `ls tests/methodology/ | grep shippab` → no `test_shippability_catalog.py`; `ls tools/shippability_runner.py` → exists.
- **Proposed fix**: Cite the real artifacts.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md AC4 + TF-1 plan rows + verification #4 now cite `tools/shippability_runner.py` + `tests/methodology/test_shippability_runner_segment_contract.py` + `tests/methodology/test_shippability_path_existence.py` (all verified on-disk). Phantom removed.

#### B2: MEPD-1(b) pre-decision rested on a false precedent — slice-035 did NOT add the build/commit skill-drift tests
- **Claim under review**: rev-0 design.md Rationale #2: *"slice-035 added two new skill-drift byte-equality tests (build_slice+commit_slice) … with NO independent rule-ID or version bump (validation infra under BRANCH-1)."*
- **Issue**: False on both counts, and load-bearing. The `mini-CAD-1 N=11 → N=13` phrase is at `methodology-changelog.md:474` — the **v0.35.0 BRANCH-1** entry. `git log --diff-filter=A` shows those drift tests were first added by **slice-021** (commit `8823c53`), riding slice-021/BRANCH-1's *existing* 4-part PMI-1 v0.35.0 bump — the opposite of a "no-bump member-addition" precedent. This is a recursive-self-application miss: the slice's own pre-decision committed the exact false-precedent error MEPD-1(b) exists to catch. Under the changelog's own Inclusion heuristic ("acceptable yesterday → refused today ⇒ changelog entry"), a triage/adopt forward-sync miss acceptable-yesterday is HALTed-today — a behavior change by the project's published criterion.
- **Evidence**: Builder re-verified — `methodology-changelog.md:474` is the v0.35.0 BRANCH-1 Validation line (co-located with `test_v_0_35_0_branch_1_entry_*`); `git log --oneline --diff-filter=A -- tests/methodology/test_build_slice_skill_drift.py` → `8823c53 … slice-021 — BRANCH-1`.
- **Proposed fix**: Withdraw the no-bump pre-decision; take the design's own named remediation (v0.57.0 + 4-part PMI-1 + entry-pin + ADR).
- **Builder draft**: **ACCEPTED-FIXED** (design.md pre-decision withdrawn, corrected analysis written, ADR-051 created, OSDG-1 minted) **+ ACCEPTED-PENDING** (the consequent `## v0.57.0` changelog entry, 4-part VERSION bump, `test_v_0_57_0_osdg_1_*` pins, and shippability rows are build-time artifacts applied during `/build-slice`). Net disposition for triage: **ACCEPTED-PENDING** (build-time work remains).

### Majors (address this slice)

#### M1: AC3 and AC4 were prose-only TF-1 rows — replays the slice-045 unmapped-AC pre-finish failure
- **Claim under review**: rev-0 TF-1 plan AC3 `Test function` = "(build-log captures perturb→FAIL→restore→PASS)"; AC4 = "(existing catalog-runner asserts …)".
- **Issue**: `tools/test_first_audit.py --strict-pre-finish` requires every row's Status to reach PASSING; a prose "build-log captures…" row has no executable test that can be marked PASSING (slice-045 law: fold into a tested AC, give it a real test, or don't number it).
- **Evidence**: slice-045 aggregated lesson; `tools/test_first_audit.py:461-474`.
- **Proposed fix**: Fold AC3 into AC1/AC2 (the genuine-contrast IS those tests' non-tautology proof); re-cite AC4 to a real test.
- **Builder draft**: **ACCEPTED-FIXED** — AC3 folded into AC1/AC2 (build-log captures the FAIL→PASS as AC1/AC2 evidence); AC4 re-cited to real on-disk audits; every TF-1 row now maps to an existing file. TF-1 plan harmonized in the same fix block (TPHD-1 sub-mode (a)).

#### M2: "Forward-sync installed copies first" can erase evidence of a real pre-existing drift
- **Claim under review**: rev-0 must-not-defer #1 / build-sequencing #1: "Forward-sync first … copy in-repo → installed BEFORE writing/running tests."
- **Issue**: If installed copies are *already* divergent at slice start (the exact latent bug this slice guards), blindly copying in-repo→installed destroys the evidence the bug occurred and the slice "passes" having silently overwritten a real drift (slice-030A "coincidental cp masks the failure" class). Currently in-sync (Critic verified), so cheap to add the guard now.
- **Evidence**: must-not-defer #1; Critic's EOL-normalized diff: currently "IN SYNC" for both.
- **Proposed fix**: Pre-sync EOL-normalized diff, recorded in build-log; STOP + record if a non-EOL divergence is found, before reconciling.
- **Builder draft**: **ACCEPTED-FIXED** — new must-not-defer item #1 added: pre-sync EOL-normalized diff of both openers recorded verbatim in build-log; a non-EOL divergence STOPs and is recorded in slice vault + risk-register before any `cp`.

### Minors (log; address if cheap)

#### m1: design.md "slice-019/021 added /diagnose mini-CAD members as infra" is an uncorroborated supporting claim
- **Claim under review**: rev-0 Rationale #2 sub-claim.
- **Issue**: Same false-precedent class as B2 (slice-021 demonstrably bumped for BRANCH-1); asserted without grepping the enforcing artifact.
- **Evidence**: B2 evidence.
- **Builder draft**: **ACCEPTED-FIXED** — sentence deleted as part of the B2 corrected analysis (no longer present in design.md rev-1).

#### m2: WIRE-1 exemption cells — format acceptable, recorded for completeness
- **Claim under review**: design.md Wiring matrix exemption cells.
- **Issue**: None — both cells contain the required `rationale:` substring; logged per the honesty rule since the spawn prompt asked it be checked.
- **Builder draft**: **ACCEPTED-FIXED** — no-op; format verified correct, no change required (acknowledged).

## Dimensions checked

- [x] Unfounded assumptions — B2 (false slice-035 precedent, load-bearing), m1 (uncorroborated slice-019/021 sub-claim). Both Builder-re-verified against the real changelog + git history.
- [x] Missing edge cases — M2 (pre-existing-drift-masked-by-blind-forward-sync; the "the bug already happened" edge).
- [x] Over-engineering — none (minimal 2-file structural twin of an established pattern; zero new comparison logic).
- [x] Under-engineering — M1 (prose-only AC3/AC4 fail `--strict-pre-finish`).
- [x] Contract gaps — none (no endpoint/event/integration; `assert_md_forward_synced` reused verbatim).
- [x] Security — none (test-only; reads two SKILL.md files, hashes them).
- [x] Drift from vault — `.gitattributes` glob `skills/**/SKILL.md` ALREADY covers both new surfaces (no gap); REPO_ROOT `parents[2]` resolves correctly for `tests/methodology/`. No-ADR was wrong (B2) → ADR-051 + v0.57.0 + 4-part PMI-1 now required and added.
- [x] Web-known issues — skipped (no external technology/API/platform dependency; pure in-repo Python).
- [x] Cross-cutting conformance — B1 (PTFCD-1 phantom test-file), B2 (RSAD-1 recursive-self-application: slice's own MEPD-1(b) pre-decision committed the false-precedent error MEPD-1(b) catches), M1 (TF-1 slice-045 class). Sibling skill-drift tests do carry shippability rows — AC4's catalog requirement is pattern-consistent once B1 is fixed.

## Triage

**Triaged by**: user
**Date**: 2026-05-19
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes (first Critic `critique.md` + meta-Critic `critique-review.md` EXTEND). User ratified all 8 Builder draft dispositions verbatim at the TRI-1 gate (no overrides, no severity changes). Verdict computed mechanically: no ESCALATED; B2 carries ACCEPTED-PENDING → NEEDS-FIXES.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | mission-brief AC4/TF-1/verification re-cited to real `tools/shippability_runner.py` + `test_shippability_runner_segment_contract.py` + `test_shippability_path_existence.py`; phantom `test_shippability_catalog.py` removed |
| B2 | Blocker | ACCEPTED-PENDING | design pre-decision withdrawn + ADR-051/OSDG-1 minted now; the `## v0.57.0` changelog entry + 4-part PMI-1 atomic bump 0.56.0→0.57.0 + `test_v_0_57_0_osdg_1_entry_present_in_repo`/`_shippability_consumer_propagation` pins are build-time artifacts applied during /build-slice |
| M1 | Major | ACCEPTED-FIXED | AC3 folded into AC1/AC2 (genuine-contrast IS those tests' non-tautology proof, captured in build-log); AC4 re-cited; every TF-1 row maps to an on-disk file (TPHD-1 (a) harmonized) |
| M2 | Major | ACCEPTED-FIXED | new must-not-defer #1: pre-sync EOL-normalized diff recorded in build-log; non-EOL divergence STOPs + opens a risk-register entry before any `cp` |
| m1 | Minor | ACCEPTED-FIXED | uncorroborated slice-019/021 sentence deleted in the B2 corrected analysis (no longer in design.md rev-1) |
| m2 | Minor | ACCEPTED-FIXED | no-op; WIRE-1 exemption cells verified to contain the required `rationale:` substring |
| B-add-1 | Blocker | ACCEPTED-FIXED | (meta-Critic, DR-1 EXTEND) AC4 + design §"What's new" + build-sequencing now specify exactly ONE row `\| 49 \| slice-049-… \| OSDG-1 …` covering both guards (one-row-per-slice, slice-048 #48 precedent); resolves the AC3-pin / AC4 self-contradiction |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic, DR-1 EXTEND) new AC5 + verification row #5 + TF-1 row + must-not-defer: re-run `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py` immediately after the CLAUDE.md Mini-CAD edit (slice-039 realign-the-pin-you-touch law) |
