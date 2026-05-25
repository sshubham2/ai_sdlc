# Critique: Slice 063 add-build-slice-new-agent-warning

**Critic reviewed**: mission-brief.md, design.md, ADR-061
**Date**: 2026-05-23
**Result**: BLOCKED (pre-fix-block; post-Builder-fix-block expected verdict at TRI-1: NEEDS-FIXES or CLEAN)

## Summary

One Blocker on the audit's core read mechanism (a real falsifier — `git diff <default>...HEAD` cannot see the uncommitted slice work that would carry the new agent file at Step 6, defeating the audit's purpose); one Major on a phantom test-file citation (PTFCD-1) in the TF-1 plan; one Major on a contract drift between mission-brief and design.md (FBCD-1 sub-mode (a)) introducing a `--strict-pre-finish` flag that the design doesn't declare; one Major on a misattributed BRANCH-1 default-branch fallback chain (the implementation has NO `main` fallback — `None` → exit 2); one Major on AC#2 test housed in the wrong file (Mini-CAD-1 drift test vs structural-anchor test); plus a small set of Minors on misattributed precedent slice, overbroad pathspec, bootstrap-brittle self-application test, CAD-1/OSDG-1 family-confusion phrasing, and missing entry-pin anchor list. The slice mints NAW-1 cleanly and the multi-surface fan-out enumeration is correct on shape, but the audit will be tautologically green for real new-agent slices as currently specified — requires redesign of the read mechanism (Dimension 8 web-confirmed: `git diff A...B` is commit-vs-commit only).

## Findings

### Blockers (must address before /build-slice)

#### B1: Audit's `git diff <default>...HEAD` cannot observe uncommitted slice work — will be tautologically green at Step 6 for every real new-agent slice

- **Claim under review**:
  - design.md "Components touched / `tools/new_agent_warning_audit.py`": *"Scan the slice's `git diff --name-status <default-branch>...HEAD --diff-filter=A -- 'agents/*.md'`"*
  - design.md "What's new" item 1: *"Read mechanism specialized: `subprocess.run(["git", "diff", "--name-status", f"{base}...HEAD", "--diff-filter=A", "--", "agents/*.md"], …)`"*
  - ADR-061 §Decision: identical mechanism.
- **Issue**: At `/build-slice` Step 6 (pre-finish gate), slice work lives in the **uncommitted working tree** — commits don't land until `/commit-slice` (the LAST step, user-invoked, post Step 7c + post `/code-review` + post `/validate-slice` + post `/reflect`; verified via `skills/build-slice/SKILL.md` Step 7c + `skills/commit-slice/SKILL.md` L23/L173 / pipeline-position L548-550 + 5 recent git log entries showing one `feat()` commit per slice attached only at `/commit-slice` time). `git diff <base>...HEAD` is a **commit-vs-merge-base** comparison (git-scm.com/docs/git-diff "the symmetric difference … `A...B` is equivalent to `$(git merge-base A B) B`"); it does NOT include working-tree or index changes. For a freshly-created `slice/063-…` branch at Step 6, `master...HEAD` yields an EMPTY diff because the slice's `agents/<new>.md` addition is still untracked or staged-but-uncommitted. The audit will therefore exit `clean / quiet` on every real new-agent slice — the EXACT class the slice exists to mitigate (R-18 N=2 recurrence). The self-application test at AC#4 (`test_self_application_slice_063_diff_is_clean`) is a vacuous-pass for the wrong reason: slice-063's diff IS literally empty at Step 6 (no new agents AND no commits yet), so the audit passes whether the implementation is correct or broken.
- **Evidence**:
  - `skills/build-slice/SKILL.md:121-156` (Step 5 mid-slice smoke → Step 6 pre-finish ordering; commits not invoked).
  - `skills/build-slice/SKILL.md:548-550` (Pipeline position: Step 6 completes → `/code-review` → `/validate-slice` → `/reflect`; `/commit-slice` HARD-STOP per PCA-1, user-invoked).
  - `skills/commit-slice/SKILL.md:22-24, 173` (`/commit-slice` is where `git add` + `git commit` runs).
  - `git log --oneline | head` confirms one `feat()` + one merge per slice — no incremental commits during build.
  - design.md and ADR-061 both specify `f"{base}...HEAD"` — verified-by-execution: a `git diff master...HEAD` from the current `slice/062-…` branch (working-tree-only changes present) yields empty output.
- **Proposed fix**: Replace `f"{base}...HEAD"` with a **union of three sources** covering all states a new agent file can occupy at Step 6:
  1. `git diff --name-only --diff-filter=A {base} -- 'agents/*.md'` — modified+staged-but-uncommitted additions vs base (working-tree-aware; `..HEAD` syntax omitted intentionally → working-tree comparison).
  2. `git ls-files --others --exclude-standard -- 'agents/*.md'` — untracked-new agent files.
  3. `git diff --name-only --diff-filter=A {base}...HEAD -- 'agents/*.md'` — already-committed-in-branch agents (covers the case where a prior `/build-slice` Step 4 task did commit, e.g., a worktree-add path).

  Union the three sets; deduplicate by path. Document the mechanism choice in ADR-061 §Decision with a worked example: a Step 6 dry-run where the user adds `agents/foo.md` (untracked) reproduces a WARN. Self-application discipline (slice-037 audit-vs-real-artifact law / APED-1): the Builder MUST empirically run the audit at Phase B against a `tmp_repo` whose ONLY change is an uncommitted-untracked `agents/foo.md` file AND a `tmp_repo` whose only change is a staged-uncommitted `agents/foo.md` AND assert a WARN in both cases. Replace the AC#4 self-application test (see m3 redesign below) with a seam-driven version that does not depend on slice-063's own live branch state.
- **Builder draft**: ACCEPTED-FIXED — design.md "Components touched / `tools/new_agent_warning_audit.py`" Responsibility + design.md "What's new" item 1 + ADR-061 §Decision + ADR-061 §Consequences worked-example rewritten in this fix block. AC#4 test plan harmonized via m3 (function name updated; injection-seam usage required).

### Majors (address this slice)

#### M1: Phantom test-file citation `tests/methodology/test_risk_register.py` — no such file exists (PTFCD-1)

- **Claim under review**: mission-brief Test-first plan AC#5 row: *"`tests/methodology/test_risk_register.py (extended)` | `test_r_18_retired_post_slice_063`"*; mission-brief Verification plan AC#5; design.md "Other modified files" L20 makes no edit-target file appear at this path.
- **Issue**: `tests/methodology/test_risk_register.py` does NOT exist on disk (`Glob tests/methodology/test_risk_register*.py` returns `test_risk_register_audit.py` + `test_risk_register_audit_real_file.py` only). The risk-status-staleness pin convention (per slice-040 R-10 `test_r_4_retired_by_slice_041_030c_completes_the_split` precedent) is housed in `tests/methodology/test_risk_register_audit_real_file.py:120` — not the cited path. This is a PTFCD-1 phantom-citation Blocker-class per Dim 9. At `/build-slice` Phase 1 the audit `tools/test_first_audit.py --strict-pre-finish` will emit a `missing-test-path-file` violation on this row, blocking pre-finish.
- **Evidence**: `Glob` against `tests/methodology/test_risk_register*.py` returns 2 files, neither matching `test_risk_register.py`. Slice-040 R-10 retirement precedent's actual home: `tests/methodology/test_risk_register_audit_real_file.py:120 def test_r_4_retired_by_slice_041_030c_completes_the_split`.
- **Proposed fix**: Repoint AC#5 TF-1 row's `Test path` cell to `tests/methodology/test_risk_register_audit_real_file.py (extended)` (matching the slice-041 R-4 retirement precedent that lives there). Update mission-brief Verification plan AC#5 accordingly. Confirm the new function `test_r_18_retired_post_slice_063` will be added to that file (not a new file). Re-grep all slice-063 artifacts for "`test_risk_register`" to harmonize (FBCD-1 sub-mode (a) cross-file consistency).
- **Builder draft**: ACCEPTED-FIXED — mission-brief TF-1 plan AC#5 row + Verification plan AC#5 cell updated in this fix block.

#### M2: `--strict-pre-finish` flag in mission-brief contradicts design.md / ADR-061 CLI surface (FBCD-1 sub-mode (a))

- **Claim under review**:
  - mission-brief Must-not-defer item: *"Non-blocking-by-construction: audit exits 0 on BOTH branches; explicit pytest assertion that `subprocess.run([…, '--strict-pre-finish'])` returns `returncode == 0` even on positive-warning branch"*
  - design.md "Contracts added or changed": CLI surface = `$PY -m tools.new_agent_warning_audit [--check] [--json] [--root <repo-root>]` — **no** `--strict-pre-finish` flag.
  - ADR-061 §Decision: same minimal CLI.
- **Issue**: The mission-brief asserts the audit accepts a `--strict-pre-finish` flag, but neither design.md nor ADR-061 declares that flag on the audit's contract. `--strict-pre-finish` is a flag class belonging to slice-folder audits (TF-1 `tools/test_first_audit.py`, ETC-1 `tools/exploratory_charter_audit.py`) that distinguishes mid-slice from pre-finish stricter modes. NAW-1 is a binary discovery audit with no PENDING-vs-PASSING state machine and no slice-folder arg — the flag is conceptually misapplied. This is FBCD-1 sub-mode (a) cross-file consistency drift; the inconsistency will land as a real pytest assertion in `test_audit_exits_0_on_new_agent_diff_with_warn_line` if not reconciled, and that test will FAIL because the audit CLI rejects the unknown flag (argparse exit 2).
- **Evidence**: design.md "Contracts added or changed / CLI surface" line; ADR-061 §Decision text; `Grep "strict-pre-finish" tools/` shows it lives only in `tools/exploratory_charter_audit.py` + `tools/test_first_audit.py` (folder-scoped audits).
- **Proposed fix**: Remove `--strict-pre-finish` from the mission-brief Must-not-defer assertion. Replace with: *"explicit pytest assertion that `subprocess.run(['$PY', '-m', 'tools.new_agent_warning_audit', '--root', tmp_repo])` returns `returncode == 0` AND a WARN line on stdout when an `agents/foo.md` addition is present"*. Re-grep mission-brief + design.md for any other `--strict-pre-finish` references and harmonize.
- **Builder draft**: ACCEPTED-FIXED — mission-brief Must-not-defer bullet rewritten in this fix block.

#### M3: ADR-061 / design.md mis-describes BRANCH-1's default-branch fallback chain — `tools/branch_workflow_audit.py` has NO "fallback `main`" leg

- **Claim under review**:
  - design.md "What's reused": *"`tools/branch_workflow_audit.py` (BRANCH-1, slice-027) — default-branch resolution logic (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → fallback `main`)"*
  - ADR-061 §Consequences/Decision implicit reuse of the same chain.
- **Issue**: `tools/branch_workflow_audit.py:127-146` `_resolve_default_branch` returns `None` after `init.defaultBranch` fails — there is **no** `main` fallback. Callers that get `None` trip the `default-branch-unresolvable` violation at exit 2 (L329-341). The design.md claim that the resolver "→ fallback `main`" is factually incorrect against the implementation. This is Dim 1 unfounded-assumption (Wiegers: claim doesn't trace to evidence) AND Dim 9 Tooling-doc-vs-implementation-parity. NAW-1 will inherit BRANCH-1's `None`-return → exit 2 (usage error) on a fresh-clone-without-remote, which contradicts ADR-061's softer "fallback `main`" framing.
- **Evidence**: `tools/branch_workflow_audit.py:127-146` (function body); `tools/branch_workflow_audit.py:329-341` (None → `default-branch-unresolvable` violation, exit 2). No `return "main"`, no `return "master"`, no string-literal fallback below the `init.defaultBranch` block.
- **Proposed fix**: Update design.md "What's reused" line on BRANCH-1 to read: *"`tools/branch_workflow_audit.py` (BRANCH-1, slice-027) — default-branch resolution logic (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → `None` ⇒ usage error exit 2 per BRANCH-1's `default-branch-unresolvable` semantics)"*. Update ADR-061 §Decision parallel prose. Then the audit's exit-2 usage class for default-branch-unresolvable is consistent across documents.
- **Builder draft**: ACCEPTED-FIXED — design.md What's reused + ADR-061 §Decision prose updated in this fix block.

#### M4: AC#2 test housed in wrong file — `test_build_slice_skill_drift.py` is a content-equality drift test, not a structural-prose-anchor test

- **Claim under review**: mission-brief TF-1 plan AC#2 row: *"`tests/methodology/test_build_slice_skill_drift.py (extended)` | `test_build_slice_step_6_invokes_new_agent_warning_audit`"*; same in mission-brief Verification plan AC#2.
- **Issue**: `tests/methodology/test_build_slice_skill_drift.py` contains exactly ONE test (`test_build_slice_skill_md_in_repo_byte_equal_installed`) and its sole purpose per its docstring + the slice-021 / slice-007 CAD-1 hybrid lineage is **content-equality between in-repo and installed SKILL.md** (Mini-CAD-1 / OSDG-1). Adding a structural-prose-anchor test that grep-asserts a substring like "New-agent warning audit (NAW-1)" inside that file violates the file's documented scope and the OSDG-1-family convention. The correct home for SKILL.md anchor pins is `tests/methodology/test_build_slice_skill.py` (28 existing tests pin load-bearing prose anchors via `BUILD = read_file(...)` + substring asserts; slice-017 TPHD-1 sub-mode (c) lineage).
- **Evidence**: `tests/methodology/test_build_slice_skill_drift.py:1-32` (single-test content-equality file, docstring "Mini-CAD-1: content-equality between in-repo `skills/build-slice/SKILL.md` and installed `~/.claude/skills/build-slice/SKILL.md`"); `tests/methodology/test_build_slice_skill.py:1-46` (the structural-anchor pin file with `BUILD = read_file(...)` pattern).
- **Proposed fix**: Update mission-brief TF-1 plan AC#2 + Verification plan AC#2 row's `Test path` cell from `tests/methodology/test_build_slice_skill_drift.py (extended)` to `tests/methodology/test_build_slice_skill.py (extended)`. The function name `test_build_slice_step_6_invokes_new_agent_warning_audit` stays. The OSDG-1 drift test (`test_build_slice_skill_drift.py`) PASSES automatically post-edit by virtue of forward-syncing installed `~/.claude/skills/build-slice/SKILL.md` — no extension needed.
- **Builder draft**: ACCEPTED-FIXED — mission-brief TF-1 plan AC#2 + Verification plan AC#2 path cells updated in this fix block; design.md "Components touched" updated to reflect the structural-anchor test housing.

### Minors (log; address if cheap)

#### m1: Design.md "BC-PROJ-9 multi-surface fan-out (slice-050 precedent)" mis-attributes the precedent slice

- **Claim under review**: design.md "What's new" item 5: *"BC-PROJ-9 multi-surface fan-out (slice-050 precedent) for the new `tools/*.py` module"*
- **Issue**: BC-PROJ-9's 5-inventory completeness was first articulated at **slice-059 reflection** ("Adding a `tools/` module touches five inventories, not three (BC-PROJ-9, slice-059)") — slice-050 added AVFS-1's tool but didn't enumerate the 5-inventory rule then. Mis-attribution doesn't change the slice's scope but a future reader following the citation back to slice-050 won't find the rule's first articulation.
- **Evidence**: aggregated lessons under "slice-059" stanza.
- **Proposed fix**: Change "BC-PROJ-9 multi-surface fan-out (slice-050 precedent)" → "BC-PROJ-9 multi-surface fan-out (slice-059 precedent on the 5-inventory completeness; slice-050 AVFS-1 tool-addition precedent on the 4-inventory subset)".
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" item 5 attribution updated in this fix block.

#### m2: `agents/*.md` pathspec is overbroad — matches `agents/AUTHORING.md` (a prose-doc, not a registered agent)

- **Claim under review**: design.md / ADR-061 pathspec `agents/*.md`.
- **Issue**: The current `agents/` directory contains `AUTHORING.md` (a documentation file, NOT in `_CANONICAL_AGENTS` at `tools/install_audit.py:61-64`; not installed by INSTALL.md Step 3f to the Claude Code registry). A future slice that adds a similar prose-doc under `agents/` would trigger a NAW-1 WARN with no actual registry-cache miss — false positive. The cost is small (a spurious WARN, not a HALT), but the WARN's recommendation ("restart Claude Code") is misleading when the new file isn't an agent.
- **Evidence**: `agents/AUTHORING.md` present on disk; not in `_CANONICAL_AGENTS` tuple at `tools/install_audit.py:61-64`.
- **Proposed fix**: Accept the overbroad match as a known false-positive class and document it in ADR-061 §Consequences ("WARN is over-broad: triggers on any `agents/*.md` addition, not just registered subagents; minimal cost — extra WARN never HALTs"). Option (b) cross-referencing `_CANONICAL_AGENTS` was considered but rejected for the fragile coupling to `install_audit.py`'s import path; the simpler binary-discovery framing is correct and the false-positive cost is acceptable.
- **Builder draft**: ACCEPTED-FIXED — ADR-061 §Consequences gains explicit "overbroad-pathspec known false-positive class" sub-bullet in this fix block.

#### m3: Self-application test `test_self_application_slice_063_diff_is_clean` is bootstrap-brittle and non-regressing

- **Claim under review**: mission-brief AC#4 row + design.md test-functions list entry naming `test_self_application_slice_063_diff_is_clean`.
- **Issue**: This test is a one-off, branch-scoped, working-tree-state-dependent assertion. Once slice-063 is merged to master and `slice/063-…` deleted, the test's "from inside the slice-063 branch" precondition is gone — every subsequent slice's run would run from a DIFFERENT branch and the diff content would be whatever THAT slice's diff is. The test either silently asserts a moving target or is permanently dead code. Compare to slice-059's TVFS-1 self-application: TVFS-1 tests use `installed_version_resolver` injection seams (B2) to drive the assertion mechanically rather than depending on environmental git state.
- **Evidence**: `tools/ai_sdlc_tools_version_forward_sync.py:34-40` (injection-seam design pattern used at slice-059 for similar non-deterministic SCM-state reads).
- **Proposed fix**: Replace `test_self_application_slice_063_diff_is_clean` with a generic `test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents` that uses the `added_files_resolver` injection seam (already declared at design.md "Components touched / Public surface") with a controlled fixture set rather than a live `git diff`. Document the seam-driven approach in ADR-061 §Consequences as the regression-stable variant of slice-063's bootstrap discharge.
- **Builder draft**: ACCEPTED-FIXED — mission-brief TF-1 plan AC#4 function-name row + design.md test-functions list entry + ADR-061 §Consequences seam-driven self-application sub-bullet all updated in this fix block (TPHD-1 sub-mode (a) harmonization on function-name change).

#### m4: Pre-finish gate item phrasing "CAD-1 / OSDG-1 (build_slice variant) skill-drift tests" conflates CAD-1 (agents) with OSDG-1 (skills)

- **Claim under review**: mission-brief Pre-finish gate: *"CAD-1 / OSDG-1 (build_slice variant) skill-drift tests PASS post-SKILL.md edit"*
- **Issue**: CAD-1 (slice-007 / ADR-019) guards `agents/critique.md` content-equality; it is NOT relevant to `skills/build-slice/SKILL.md`. OSDG-1 (slice-049 / ADR-051) guards the opener-skill + reflect set. The build-slice variant is Mini-CAD-1 family member `test_build_slice_skill_drift.py`. A regression-test runner reading this gate item would not know which subset to run.
- **Evidence**: CLAUDE.md "Self-hosting discipline" section distinguishes CAD-1 (`agents/critique.md`) from Mini-CAD / OSDG-1 (skills + `reflect`); `tests/methodology/test_build_slice_skill_drift.py:1-9` docstring "slice-021 AC #5 + slice-007 CAD-1 hybrid (option d)".
- **Proposed fix**: Replace pre-finish gate line with: *"`test_build_slice_skill_drift.py` (Mini-CAD-1 / OSDG-1 build_slice variant) PASSES post-SKILL.md edit + forward-sync to `~/.claude/skills/build-slice/SKILL.md`"*.
- **Builder draft**: ACCEPTED-FIXED — mission-brief Pre-finish gate bullet rewritten in this fix block.

#### m5: Methodology-changelog v0.66.0 entry's PMI-1 anchor literal not explicitly pinned at entry-pin design

- **Claim under review**: design.md item 8 entry-pin schema.
- **Issue**: The slice-059 / slice-062 entry-pin precedent asserts SPECIFIC anchor substrings inside the v-entry body: rule-ID, ADR ID, rule-name-expansion, `"mints a new rule"`, `"supersedes nothing"`, AND the `"N-part PMI-1 atomic bump"` literal. Design.md doesn't enumerate which anchors will be pinned for v0.66.0; without a list, the entry-pin tests at /build-slice will be written ad-hoc and may diverge from the slice-062 precedent (e.g., asserting "4-part PMI-1 atomic bump" instead of "5-part PMI-1 atomic bump").
- **Evidence**: `tests/methodology/test_methodology_changelog.py:3901-3905` (TVFS-1 entry pin's "4-part PMI-1 atomic bump" anchor — slice-059 had 4-part because no new tool; slice-063 has 5-part with new tool — anchor MUST differ).
- **Proposed fix**: Add to design.md item 8 an explicit anchor list mirroring the slice-059 TVFS-1 anchor set: `"NAW-1"`, `"ADR-061"`, `"New-Agent Warning"`, `"mints a new rule"`, `"supersedes nothing"`, `"5-part PMI-1 atomic bump"`. Document at design-time per EPGD-1.
- **Builder draft**: ACCEPTED-FIXED — design.md item 8 anchor list inserted in this fix block.

## Dimensions checked

- [x] **Unfounded assumptions** — M3 (BRANCH-1 "fallback `main`" doesn't exist in the implementation); B1 (the audit's read mechanism rests on an unverified assumption that `master...HEAD` covers Step-6 working-tree state — falsified by execution + `skills/build-slice/SKILL.md` sequencing).
- [x] **Missing edge cases** — Empty diff is the EXACT edge case B1 highlights and the design fails to address. Permission-denied class: `git` binary unavailable IS covered (exit 2 usage). Detached HEAD: not addressed but BRANCH-1 already gates pre-finish on `slice/NNN-…` branch — not filed.
- [x] **Over-engineering** — design.md exposes TWO injection seams; net acceptable given m3's redesign requires the second seam.
- [x] **Under-engineering** — TF-1 row coverage: 5 ACs / 8 rows; all PENDING — expected to WRITTEN-FAILING. See M1 (phantom path), M4 (wrong-file housing), M2 (`--strict-pre-finish` flag).
- [x] **Contract gaps** — CLI surface explicit, errors enumerated. M2 is the contract-drift finding within this dimension.
- [x] **Security** — no new authentication, authorization, data exposure paths; subprocess `git` calls use list-form (no shell injection). No findings.
- [x] **Drift from vault** — M1 (phantom test-file path is also vault-drift class). MEPD-1 RULE-ID + entry-pin: NAW-1 + ADR-061 + paired v0.66.0 entry-pin tests + 5-part PMI-1 atomic bump + TVFS-1 forward-sync. All branches present and design-explicit.
- [x] **Web-known issues** — `git diff <base>...HEAD` working-tree exclusion confirmed via git-scm.com/docs/git-diff: "`<commit>...<commit>` … shows the changes on the branch containing and up to the second `<commit>`, starting at a common ancestor of both" — commit-to-commit only, working tree excluded. `git ls-files --others --exclude-standard` is the canonical untracked-file enumerator. No deprecations.
- [x] **Cross-cutting conformance** — Methodology-audit conformance: TF-1 row coverage 5 ACs / 8 rows / single-AC labels (no slice-062 M-add-1 multi-AC class). RR-1 / BC-PROJ-9 / BC-PROJ-7 acknowledged. Tooling-doc-vs-implementation parity: M3. Algorithm-path-conformance: B1. PTFCD-1: M1. FBCD-1 sub-mode (a): M2; m5. APED-1: confirmed B1 by `git diff master...HEAD` execution against current branch (empty output).

Sources:
- https://git-scm.com/docs/git-diff
- https://www.mankier.com/1/git-diff
- https://manpages.ubuntu.com/manpages/noble/man1/git-diff.1.html
- https://git-scm.com/docs/git-ls-files
- https://git-scm.com/docs/git-status

## Triage

**Triaged by**: user
**Date**: 2026-05-23
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Read mechanism rewritten as union of three git sources at design.md L12 + ADR-061 §Decision L60-67; worked example added; empirically verified by meta-Critic against synthetic tmp_repo (untracked + staged + committed-in-branch states). |
| M1 | Major | ACCEPTED-FIXED | mission-brief.md L38 TF-1 row + L48 Verification plan repointed from phantom `test_risk_register.py` to `test_risk_register_audit_real_file.py` (slice-041 R-4 retirement-precedent housing). |
| M2 | Major | ACCEPTED-FIXED | mission-brief.md L57 Must-not-defer rewritten without `--strict-pre-finish` flag; replaced with `subprocess.run(['$PY', '-m', 'tools.new_agent_warning_audit', '--root', tmp_repo])` shape. |
| M3 | Major | ACCEPTED-FIXED | design.md L25 + ADR-061 L65 prose updated to BRANCH-1's actual `None → usage exit 2` semantics (no `main` fallback in the implementation per `tools/branch_workflow_audit.py:127-146`). |
| M4 | Major | ACCEPTED-FIXED | mission-brief.md L32 + L45 TF-1 row + Verification plan repointed from `test_build_slice_skill_drift.py` (Mini-CAD-1) to `test_build_slice_skill.py` (structural-anchor pin per slice-017 TPHD-1 sub-mode (c) lineage). |
| m1 | Minor | ACCEPTED-FIXED | design.md L16 BC-PROJ-9 attribution corrected to slice-059 (5-inventory completeness) + slice-050 (4-inventory subset precedent). |
| m2 | Minor | ACCEPTED-FIXED | ADR-061 L106 §Consequences gained explicit overbroad-pathspec known-false-positive class documentation (option (a) accepted; option (b) `_CANONICAL_AGENTS`-scoped pathspec rejected for fragile coupling). |
| m3 | Minor | ACCEPTED-FIXED | `test_self_application_slice_063_diff_is_clean` renamed to `test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents` (seam-driven via `added_files_resolver` injection); TPHD-1 sub-mode (a) harmonized across mission-brief L37 + design.md L61 + ADR-061 L107. |
| m4 | Minor | ACCEPTED-FIXED | mission-brief.md L105 Pre-finish gate phrasing clarified — Mini-CAD-1 / OSDG-1 build_slice variant (CAD-1 explicitly distinguished as `agents/critique.md`-only). |
| m5 | Minor | ACCEPTED-FIXED | design.md item 8 anchor list enumerated explicitly at design-time per EPGD-1 — initial 6-anchor list at /critique fix block, extended to 8 anchors at /critique-review fix block per M-add-2. |
| M-add-1 | Major | ACCEPTED-FIXED | design.md L17 rewritten to align with ADR-061 L85's authoritative 5-leg PMI-1 enumeration; MCFS-1 + TVFS-1 dropped from atomic-bump legs, documented separately as BC-PROJ-9 fan-out / post-bump forward-sync obligations (mission-brief L56 was already correct). Same defect class as slice-060 B2 / slice-062 B1 — cross-doc enumeration drift caught at /critique-review. |
| M-add-2 | Minor | ACCEPTED-FIXED | design.md item 8 anchor list extended from 6 → 8 anchors; added `"## v0.66.0"` header anchor + `"Rule reference"` literal (META-1 mandatory enforcing-assertion at `test_methodology_changelog.py:136`). |
| M-add-3 | Minor | ACCEPTED-FIXED | design.md L218 Validation strategy step 2 rewritten to enumerate the actual 13 Step 6 audits + new NAW-1 = 14 audits; `plugin_manifest` dropped (PMI-1 is enforced via paired tests + `_CANONICAL_TOOLS`/`plugin.yaml` lock-step, NOT a Step 6 checklist line). |
