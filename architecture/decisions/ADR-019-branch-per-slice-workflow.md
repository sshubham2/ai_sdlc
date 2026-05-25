---
id: ADR-019
title: Branch-per-slice workflow at /build-slice Prerequisite check + /commit-slice --merge, enforced by BRANCH-1 audit
date: 2026-05-14
slice: slice-021-add-feature-branch-workflow-at-build-and-commit-slice
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-019: Branch-per-slice workflow (BRANCH-1)

**Note on rule-ID naming** (per `-D` suffix calibration-trail convention N=6 stable at slice-020; this rule does NOT carry `-D` suffix): BRANCH-1 is an **audit-enforced gate** at slice-runtime, NOT a /critique-time prose-heuristic discipline. The `-D` suffix convention (RSAD-1, EPGD-1, SCPD-1, RPCD-1, TPHD-1, BFRD-1) applies only to /critique-time skill-prose heuristics with no programmatic audit. BRANCH-1 sits in the audit-enforced-gate naming class alongside BC-1, CAD-1, PMI-1, INST-1, WIRE-1, NFR-1, CSP-1, VAL-1, RR-1, MCT-1, LAYER-EVID-1 — each backed by a `tools/<name>_audit.py` (or equivalent skill-runtime audit). BRANCH-1's programmatic gate is `tools/branch_workflow_audit.py`.

## Context

Today every slice's build, validate, reflect, and commit-slice commits all land directly on `master`. The repository has exactly two branches in the entire 20-slice history: `master` and `remotes/origin/master`. There has never been a feature branch, bug branch, or experimental branch. This creates three concrete pain points:

1. **No rollback boundary for a half-finished slice**: if /build-slice ships partial work and the user wants to abandon and start over, the discard requires identifying which commits-on-master belong to this slice vs. prior slices, then using `git reset --hard <ancestor>` or `git revert <range>` — error-prone and history-rewriting on the shared branch.

2. **No per-slice diff surface for review**: a future PR-based review workflow (whether human or AI reviewer like /ultrareview, or a CI gate at GH Actions) needs a coherent diff representing "the slice as a whole". Today the slice's diff is scattered across N intermediate commits on master interleaved with build-log + validation + reflection edits — no single integration point to attach a review against.

3. **Branch namespace pollution-by-omission**: `git branch -a` returns only `master`. There is no audit trail at the branch level for which slices exercised which surfaces. A merged slice branch produced via `git merge --no-ff` leaves a discoverable merge-commit attribution in `git log --graph --oneline` ("slice-018 merged here") that today's flat-master workflow cannot produce.

The empirical evidence base for codifying this:
- 20 slices shipped to date, ALL directly on master. The slice-020 reflection's "Strongest slice-021 candidates" list pre-queued `audit-tools-default-utf8-stdout` (N=4 cp1252 promotion) + 3 Dim 9 sub-class refinements + cleanup of stale R-1/R-2. None of those candidates touch the workflow-layer concern raised by the user explicitly at /slice-021 invocation.
- User direct request at /slice-021 invocation: *"any fix or features goes to main branch directly, can we created a feature or bug branch during build slice and commit-slice will auto commit to that branch and may be we can have a --merge command in commit-slice instead of --do-commit"*. Two concrete asks: (a) branch-create at /build-slice; (b) `--merge` replacing `--do-commit` at /commit-slice. Both delivered by Option 1 below.
- Brownfield CLAUDE.md "Refactors need a slice" rule already governs in-slice scope; branch-per-slice is the git-level expression of the same discipline (one slice = one merge unit).

The cost of codification is medium (~3–4 hours, ~21 files including forward-sync mirrors); the cost of waiting is one more cycle of direct-to-master commits per slice. The discipline is structurally analogous to MCT-1 (slice-010) — both introduce a skill-runtime gate enforcing a discipline the user could otherwise skip; MCT-1 enforces "Critic runs on cross-cutting tooling slices", BRANCH-1 enforces "slice work lives on its own branch".

User question at slice-021 origination: *"may be we can have a --merge command in commit-slice instead of --do-commit"*. The chosen approach (Option 1 below) replaces `--do-commit` with `--merge` as a clean break — no deprecation alias, no two-flag mode (separate `--commit` and `--merge`) — because the codebase has zero non-repo consumers; 3 in-repo doc surfaces (`pipeline.md` L97, `tutorial.md` L750, `tutorial-site/Hybrid AI SDLC Pipeline.html` L583) are atomically updated this slice (per /critique B2 ACCEPTED-PENDING), and a single integrated flow is simpler than two separate flags whose composition users would have to learn.

## Options considered

### Option 1 — 3-sub-mode discipline at `/build-slice` `## Prerequisite check ### Branch state` sub-section + `/commit-slice --merge` flag + BRANCH-1 audit (CHOSEN; v1 carves out upstream-pipeline scope per /critique M-add-4 ACCEPTED option (a))

Insert a NEW `### Branch state` sub-section WITHIN the existing `## Prerequisite check` H2 in `skills/build-slice/SKILL.md` (per slice-017 TPHD-1 sub-mode (c) precedent at methodology-changelog v0.32.0 L102: "step numbering is 1,2,3,4,5,6,7,7b,7c,8 with no Step 0; the discipline IS structurally a prerequisite verification"). Replace `--do-commit` with `--merge` in `skills/commit-slice/SKILL.md` (frontmatter `argument-hint` + Step 5 prose, with 2 pre-flight guardrails per /critique B5 + M5 ACCEPTED). Add a new audit `tools/branch_workflow_audit.py` (BRANCH-1) invoked at /build-slice Step 6 pre-finish (NOT "Phase 6" — that vocabulary retired at slice-017 ADR-016).

Three distinct sub-modes (per slice-020 BFRD-1 + slice-017 TPHD-1 + slice-016 RPCD-1 N-sub-mode N=6 → N=7 stable):
- **Sub-mode (a) build-time branch-create**: at /build-slice `## Prerequisite check ### Branch state` sub-section, resolve repo default branch via `git symbolic-ref refs/remotes/origin/HEAD` with `git config init.defaultBranch` fallback (per /critique M1 ACCEPTED — replaces hard-coded `master`/`main`); detect current branch + create `slice/NNN-<slice-name>` from default-branch HEAD if HEAD is on default-branch; switch to it if branch exists; STOP otherwise; STOP on dirty WT.
- **Sub-mode (b) commit-time `--merge` flow**: at /commit-slice with `--merge` flag, pre-flight guardrails (no stale `slice/*` branches per B5; `git status --porcelain` empty per M5) + commit on slice branch + `git checkout <default-branch>` + `git merge --no-ff slice/NNN-<name>` + explicit `Confirm merge + delete? (yes/no)` user-confirmation + `git branch -d slice/NNN-<name>` (safe-delete only; never `-D`).
- **Sub-mode (c) audit-time pre-finish refusal**: at /build-slice Step 6 pre-finish, `tools/branch_workflow_audit.py <slice-folder>` refuses if current branch is the resolved default-branch or `slice/NNN-<wrong-name>`, unless `BRANCH=skip` escape-hatch is documented in `build-log.md` Events conforming to the canonical regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+` (canonical shape pinned in build-slice SKILL.md Step 7c per /critique B1 ACCEPTED).

**v1 carveout** (per /critique M-add-4 ESCALATED → option (a) chosen): the 3 sub-modes fire only at /build-slice + /commit-slice. The 4 upstream slice-pipeline skills (`/slice`, `/design-slice`, `/critique`, `/critique-review`) have NO branch guard in v1 — they author files into the slice-N folder regardless of current branch. Cross-slice-branch leakage (where slice-N artifacts land on `slice/(N-1)` because previous slice wasn't `--merge`d) is surfaced AT /build-slice when BRANCH-1 sub-mode (a) STOPs; recovery requires `git stash` / `git cherry-pick`. Pipeline-wide enforcement is queued as follow-on slice `add-pipeline-wide-branch-discipline-to-upstream-slice-skills`. Rationale: pipeline-wide scope inflates magnitude to ~35+ sites (8 SKILL.md surfaces × in-repo + installed = 16 + their prose-pin tests + their mini-CAD drift + the cross-skill state-machine analysis), which likely splits into 2 slices anyway per project's slice-size convention; original user ask anchored on `/build-slice`.

Codify in `methodology-changelog.md` v0.35.0 entry naming BRANCH-1 + 3 sub-modes + Limitations note acknowledging local-only scope (no push, no PR, no squash, no per-classification-prefix) + v1 upstream-pipeline carveout.

Mirror BFRD-1 (slice-020 ADR-018) structural shape: terse skill-prose insertions at named insertion points + N-surface schema-pin + prose-pin tests + Limitations note + atomic version bump.

**Pros**:
- Defense-in-depth: build-time creates the branch (Sub-mode (a)), commit-time integrates it back (Sub-mode (b)), audit-time refuses if either step was skipped (Sub-mode (c)).
- Programmatic-gate-from-day-one: BRANCH-1 has a `tools/branch_workflow_audit.py` audit at codification, not deferred to v2. Distinguishes from /critique-time `-D` family which routinely defer the audit (BFRD-1, RPCD-1, TPHD-1, etc.). The branch-state is mechanically checkable, so programmatic gate is the right level of enforcement.
- Reversibility: cheap. Revert path is git diff + superseding changelog entry. ~3–4 hours per slice-020 BFRD-1 + slice-019 LAYER-EVID-1 magnitude.
- Clean break: replacing `--do-commit` with `--merge` (no alias, no two-flag mode) is simpler to teach and to maintain. Zero external consumers per [[architecture/triage.md]] — no migration burden.
- Slice-attribution preserved in git history: `git merge --no-ff` ensures a merge commit per slice, discoverable via `git log --graph --oneline`. Today's flat-master workflow has no equivalent.

**Cons**:
- Bootstrap-ordering caveat at slice-021 itself: the slice that introduces the `## Prerequisite check ### Branch state` sub-section cannot use that sub-section at /build-slice time because the sub-section doesn't exist yet on disk when /build-slice starts. Mitigated by Claude main thread manually firing the equivalent branch-create at Step 1 plan-mode entry (recorded as canonical BRANCH=skip-bootstrap DEVIATION line in build-log.md Events) — documented per design.md "Self-application of BRANCH-1" caveat 1. Non-bootstrap canonical reference instance #1 starts at the next non-/repro slice after this one.
- Audit-enforced gate means a user who manually runs `git checkout master` mid-slice + builds on master would have to address the BRANCH-1 finding at /build-slice Step 6 pre-finish gate before declaring done — friction surface. Mitigated by the canonical `BRANCH=skip — rationale: <text>` escape-hatch documented in build-log.md Events (e.g., "trivial 1-line typo fix per CLAUDE.md hard-rule exception").
- v1 single-merge-strategy (`--no-ff`) and local-only scope (no push) cover the user's stated ask but leave PR-based review, squash, rebase, remote-branch lifecycle, and per-classification-prefix as future-slice concerns. Limitations list in v0.35.0 entry explicitly enumerates these.

### Option 2 — Skill-prose-only discipline at /build-slice + /commit-slice (no audit)

Insert the `## Prerequisite check ### Branch state` sub-section and `--merge` prose in the two skill files but DO NOT add a programmatic audit. Rely on Claude main thread (and the user) reading the prose at /build-slice and /commit-slice time.

**Pros**: 2-surface change vs 3-surface (drops the audit); ~30 min less work; mirrors BFRD-1 v1 codification pattern (prose-only, audit deferred to v2 at N≥3 violations).

**Cons**:
- Branch state is **mechanically checkable** — `git branch --show-current` is a one-line subprocess call. Deferring an audit when the underlying check is mechanically trivial is YAGNI in reverse: the audit is cheaper than the prose-pin test mass needed to defend the prose against drift.
- Without an audit-enforced gate, the rule reduces to advisory-only at /critique time. Per slice-020 BFRD-1 /critique B2 ACCEPTED-FIXED lesson ("Verification mechanism `shippability.md grep verification` for `tests/bugs/*` Command-cell match"), audit-less prose-disciplines need an explicit verification mechanism; BRANCH-1's natural verification mechanism IS the audit, so deferring it costs more than building it.
- The /build-slice Step 6 pre-finish gate enumerates audits as a checklist (TF-1, WIRE-1, BC-1, LINT-MOCK, etc.); BRANCH-1 belongs in that list at the same surface level. Skill-prose-only would force BRANCH-1 to live OUTSIDE the standard Step 6 audit family, which is structural drift.
- **Rejected**: cost asymmetry doesn't favor deferral. Audit-from-day-one is the right level of enforcement.

### Option 3 — Per-classification branch prefix (`feat/`, `fix/`, `bugfix/`, `hotfix/`, etc.) at branch-create

Use BFRD-1's slice-name detection (mode (a) name-shape: `fix-*` / `*-fix` / `bugfix-*` / `hotfix-*` / `defect-*` / `repair-*` / `patch-*` / `harden-*-bug`) to choose a branch prefix at /build-slice Prerequisite check `### Branch state`: bug-fix slices → `bugfix/NNN-<name>`, methodology slices → `chore/NNN-<name>`, feature slices → `feat/NNN-<name>`, etc.

**Pros**: `git branch -a` becomes more semantically rich; conventional-commits-style classification at branch level + at merge-commit message; matches Conventional-Commits + GitFlow precedent.

**Cons**:
- Classification logic at branch-create couples BRANCH-1 to BFRD-1 (and to future classification rules like SECURITY-1 if added). The coupling is one-way (BRANCH-1 reads BFRD-1's name-shape regex), but it adds complexity at slice-021 codification without empirical N≥2 evidence that the classification matters at branch level.
- Uniform `slice/NNN-<name>` (Option 1) is simpler, easier to grep, easier to audit (one regex per pattern), and easier to extend later if classification turns out to matter. Per slice-018+ helper-extraction precedent (Fowler rule-of-three at N=3), `slice/NNN-<name>` first, classified-prefix second-at-N≥2-recurrence.
- **Rejected**: defer until N≥2 instances of "branch-name semantic richness would have prevented friction" emerge post-slice-021. Listed as future-slice candidate in design.md Limitations item 3.

### Option 4 — Remote-aware flow at slice-021 (push slice branch + open PR + auto-merge after CI)

Extend `--merge` to push the slice branch to `origin`, open a PR via `gh pr create`, wait for CI green, then merge via `gh pr merge --squash` or equivalent.

**Pros**: full end-to-end CI-gated review workflow; matches industry practice for production codebases.

**Cons**:
- This repo has zero non-repo consumers (per [[architecture/triage.md]] adoption-record; 3 in-repo doc surfaces handled atomically per /critique B2 ACCEPTED-PENDING). CI is not currently set up (no `.github/workflows/` directory). Building remote-aware flow at slice-021 requires CI infrastructure that doesn't exist yet — premature.
- The user's stated ask is local-only ("commit-slice will auto commit to that branch and may be we can have a --merge command"). Remote scope is beyond what was asked.
- Per slice-019 ADR-017 R-3 escalation-criteria precedent: build the local-only v1; promote to remote-aware v2 when (a) CI infrastructure exists or (b) the user requests PR-based flow explicitly.
- **Rejected at slice-021 codification**: defer to a follow-on slice (`add-remote-pr-flow-to-commit-slice-merge`) once CI infra exists. Listed as future-slice candidate in design.md Limitations item 1.

## Decision

**Adopt Option 1** — 3-sub-mode discipline at /build-slice `## Prerequisite check ### Branch state` sub-section + /commit-slice `--merge` + BRANCH-1 audit at /build-slice Step 6. Codified as BRANCH-1 in `methodology-changelog.md` v0.35.0. Canonical phrase `branch-per-slice workflow` pinned across N=3 surfaces per N-surface schema-pin precedent N=7 → N=8 stable: (1) `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section prose, (2) `skills/commit-slice/SKILL.md` Step 5 `--merge` block prose, (3) in-repo + installed `methodology-changelog.md` v0.35.0 entry.

Three sub-modes distinctly named:
- **Sub-mode (a) build-time branch-create**: /build-slice `## Prerequisite check ### Branch state` sub-section — resolve default branch (symbolic-ref + init.defaultBranch fallback); `git checkout -b slice/NNN-<slice-name>` from default-branch HEAD when on default-branch; switch when slice branch exists; STOP on dirty WT or wrong starting branch.
- **Sub-mode (b) commit-time `--merge` flow**: /commit-slice Step 5 — 2 pre-flight guardrails (stale-branch + WT-clean) + `git add` + `git commit` on slice branch + `git checkout <default-branch>` + `git merge --no-ff slice/NNN-<name>` + explicit confirmation prompt + `git branch -d slice/NNN-<name>`.
- **Sub-mode (c) audit-time pre-finish refusal**: /build-slice Step 6 — `$PY -m tools.branch_workflow_audit <slice-folder>` exits 1 on mismatch + no canonical `BRANCH=skip` escape-hatch line; 0 on clean or canonical escape-hatch documented.

`--do-commit` flag REMOVED (no alias, no two-flag mode). Backward-incompatible with prior /commit-slice invocations; zero non-repo consumers per adoption record + 3 in-repo doc surfaces atomically updated this slice (per /critique B2 ACCEPTED-PENDING) makes this safe.

PMI-1 atomic version bump 0.34.0 → 0.35.0 with versioned-gate retirement-proof (PMI-1 v1.1 version-agnostic gate N=6 → N=7 stable; zero test code modification on gate body).

**BRANCH-1 bootstrap-self-application at slice-021**: per design.md "Self-application of BRANCH-1" caveat 1, slice-021 IS the canonical bootstrap-reference instance #1 of BRANCH-1. The slice's own /build-slice will fire the bootstrap-equivalent manually (Claude main thread creates the slice branch by hand before plan-mode entry; documented via the canonical BRANCH=skip-bootstrap DEVIATION line per /critique B1 ACCEPTED-PENDING + B4 ACCEPTED-PENDING). The first non-bootstrap canonical reference instance is **the next non-/repro slice after this one** (per /critique m2 ACCEPTED-FIXED — softened from prior "slice-022" speculation because design.md Limitations item 4 carves out /repro slices from BRANCH-1 scope; if slice-022 is a /repro, then slice-023+).

**BFRD-1 contingent N/A at slice-021**: per slice-020 BFRD-1 contingent-inapplicability precedent — slice-021 is NEW-feature methodology-codification, not bug-fix; name has no `fix-*`/`*-fix`/etc. shape; source signal is workflow enhancement. STOP-route vacuously satisfied.

## Consequences

**Immediate** (slice-021 ship):

- `skills/build-slice/SKILL.md` gains 3 insertions: (1) NEW `### Branch state` sub-section within existing `## Prerequisite check` H2 (current L17-23 stays; sub-section appended within); (2) NEW canonical-shape sentence in existing Step 7c flight-recorder block (current L222-243) pinning `BRANCH=skip — rationale: <text>` line shape; (3) NEW pre-finish gate checklist bullet `- [ ] BRANCH-1 audit passes` in existing Step 6 (current L93-107).
- `skills/commit-slice/SKILL.md` frontmatter L5 `argument-hint: [--do-commit]` → `[--merge]`; Step 5 L142-149 `--do-commit` block → `--merge` block.
- `methodology-changelog.md` v0.35.0 entry appended (in-repo + installed) with BRANCH-1 rule reference + 3-sub-mode naming + Limitations note (local-only scope; single-merge-strategy; uniform branch-prefix; no auto-stash; safe-delete only; no history rewrite; no origin-validation).
- `architecture/decisions/ADR-019-branch-per-slice-workflow.md` created (this file).
- `architecture/shippability.md` row 21 added enumerating BRANCH-1 critical-path tests (BRANCH-1 audit clean run on synthetic slice branch fixture + prose-pin tests + mini-CAD-drift tests).
- `tools/branch_workflow_audit.py` created with CLI shape mirroring `critique_agent_drift_audit.py` + `plugin_manifest_audit.py` patterns.
- `tools/install_audit.py` canonical list gains `branch_workflow_audit`.
- `plugin.yaml.version` 0.34.0 → 0.35.0; `tools:` list gains `branch_workflow_audit`.
- `VERSION` 0.34.0 → 0.35.0; `~/.claude/ai-sdlc-VERSION` forward-sync.
- `CLAUDE.md` Brownfield rules section gains NEW bullet `Branch-per-slice`.
- `tests/methodology/test_methodology_changelog.py` gains NEW SECTION header `# --- Slice-021 / BRANCH-1 branch-per-slice workflow ---` + entry-pin tests for v0.35.0 + ADR-pin test for ADR-019.
- `tests/methodology/test_build_slice_skill_branch_create.py` (NEW) — 3 prose-pin asserts.
- `tests/methodology/test_commit_slice_skill_merge_flag.py` (NEW) — 3 prose-pin asserts.
- `tests/methodology/test_root_claude_md_branch_per_slice_rule.py` (NEW) — 1 prose-pin assert.
- `tests/methodology/test_build_slice_skill_drift.py` (NEW) — mini-CAD-1 byte-equality.
- `tests/methodology/test_commit_slice_skill_drift.py` (NEW) — mini-CAD-1 byte-equality.
- `tests/tools/__init__.py` + `tests/tools/test_branch_workflow_audit.py` (NEW) — 4 unit tests on the new audit.
- `agents/critique.md` NOT touched (CAD-1 byte-equality preserved at slice-017 ship hash `f34c967eaaa34413...`; bidirectional sha256 forensic capture N=16 → N=17 stable expected).
- `skills/slice/SKILL.md` NOT touched (mini-CAD-1 byte-equality preserved at slice-020 ship hash `cc18b5a05c2220dd...`; row 3 PASSING → PASSING stable).

**Downstream** (slice-022 and beyond):

- Every `/build-slice` invocation runs the `## Prerequisite check ### Branch state` sub-section — creates `slice/NNN-<name>` automatically if on default branch; switches to it if exists; STOPs if on a non-default / non-`slice/*` branch (with documented canonical `BRANCH=skip — rationale: <text>` escape-hatch).
- Every `/commit-slice --merge` invocation runs the 3-step commit-and-merge flow; no-ff merge commit preserves slice attribution in `git log --graph --oneline`.
- BRANCH-1 audit at Step 6 pre-finish gate catches any slice that bypassed the `## Prerequisite check ### Branch state` sub-section OR ran on the wrong branch.
- The first non-bootstrap canonical reference instance of BRANCH-1 is **the next non-/repro slice after this one** (per /critique m2 ACCEPTED-FIXED). Reflection.md SHOULD record BRANCH-1 self-application as a load-bearing discipline (analogous to BFRD-1 first prospective bug-fix slice at slice-021+).
- Future-slice candidates queued: `add-remote-pr-flow-to-commit-slice-merge` (when CI infra exists), `add-squash-merge-toggle-to-commit-slice` (when slice-branch noise compression matters), `add-classified-branch-prefix-to-build-slice` (when classification-by-prefix matters), `add-auto-stash-at-build-slice-step-0-5` (when dirty-WT STOPs cost more than auto-stash), `add-force-delete-escape-hatch-to-commit-slice-merge` (when safe-delete-refuses cost more), `add-branch-origin-validation-to-branch-1` (when wrong-origin branches recur).
- Drift detection at v1: BRANCH-1 audit (mechanically checks branch state at /build-slice Step 6) + prose-pin tests (defend SKILL.md prose) + mini-CAD-drift tests (defend forward-sync). v2 candidate `tools/branch_workflow_audit.py` extension to validate branch was created from default-branch HEAD (not from another slice branch) deferred per design.md Limitations item 7.

**Cumulative-Critic-influence note**: BRANCH-1 is applied prospectively starting from slice-021 itself (bootstrap reference instance #1) and from slice-022+ (non-bootstrap reference instances). Per slice-019/020 lesson "codification slices that codify a discipline almost always commit instances of that discipline on their own draft": slice-021 expects RSAD-1 / EPGD-1 / SCPD-1 / TPHD-1 sibling-rule first-Critic catches on its own draft (e.g., recursive-self-application defects in this ADR-019; TPHD-1 3-surface harmonization gaps if /critique fix-prose edits AC text). Recursive-self-application N=17 → N=18+ ratchet expected.

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 ADR-008 + slice-010 ADR-009 + slice-013 ADR-012 + slice-014 ADR-013 + slice-015 ADR-014 + slice-016 ADR-015 + slice-017 ADR-016 + slice-019 ADR-017 + slice-020 ADR-018 cheap-with-magnitude-justification convention N=9 → N=10 stable).

**Magnitude estimate**: **~25 source files + 5 test-file extends = 30 total touches** at slice-021 ship. Per /critique-rerun M4-new ACCEPTED-FIXED option (b) — the prior dual-enumeration drift class (ADR-019 listing items 1-22 + design.md listing items 1-30) is retired in favor of a single canonical enumeration in `design.md §Files changed (estimated count)` cited authoritatively from here. See [[design.md#Files changed (estimated count)]] for the full 30-item enumeration.

Summary: ~25 source files (2 SKILL.md edits + 1 new audit + plugin.yaml/VERSION/install_audit/CLAUDE.md/shippability/methodology-changelog/ADR-019 + 4 forward-sync mirrors + 3 stale-doc surfaces + 2 new mini-CAD test files + 4 NEW prose-pin/audit test files) + 5 test-file extends (test_methodology_changelog.py + test_install_audit.py + test_critique_agent_drift.py + test_plugin_manifest_audit.py + test_shippability/test_row_021_branch_workflow.py).

Wiegers regression-guard coverage-symmetry watch-list ratchets to **N=9 cumulative** across slices 016/017/019/020 + 2 within slice-021 first /critique + 2 within /critique rerun + 5 within /design-slice rerun (per /critique-rerun B3-new + M3-new + M4-new ACCEPTED-FIXED). **Promotion ELEVATED to slice-022** (was slice-024+) per /critique-rerun observation — class is empirically the dominant recurrence class for codification slices. Recursive-self-application N=17 → **N=28 cumulative HWM** ratchets accordingly.

**Comparison to prior ADRs**:
- ADR-009 (MCT-1, slice-010) — **cheap** with magnitude justification. ~11-13 sites. Skill-prose-discipline at 1 surface.
- ADR-010 (RSAD-1, slice-011) — **cheap**. ~12 sites. Skill-prose at 1 surface.
- ADR-012 (EPGD-1, slice-013) — **cheap**. ~12 sites.
- ADR-014 (SCPD-1, slice-015) — **cheap**. ~13-15 sites.
- ADR-015 (RPCD-1, slice-016) — **cheap**. ~13-15 sites.
- ADR-016 (TPHD-1, slice-017) — **cheap**. ~13-16 sites at 3-surface skill-prose insertion.
- ADR-017 (LAYER-EVID-1, slice-019) — **cheap**. ~12-14 sites at /diagnose runtime discipline.
- ADR-018 (BFRD-1, slice-020) — **cheap**. ~11 sites at 1-surface skill-prose.
- **ADR-019 (this) — cheap with magnitude justification**. **~25 source files + 5 test-file extends = 30 total touches** (per /critique-rerun M4-new ACCEPTED-FIXED option (b) — single canonical enumeration in design.md §Files changed cited authoritatively from here; eliminates the dual-enumeration drift class permanently). Larger than prior /critique-time codifications because BRANCH-1 ships a new programmatic audit + 2 SKILL.md edits + 4 new test files + 3 stale-doc surface updates (B2 fix); smaller than would-be Heavy-mode comprehensive-architecture slices (which run 40+ sites). Effort budget within MEDIUM (~3–4 hours) per slice-019 LAYER-EVID-1 magnitude.

**Revert path**:
1. Git diff revert of slice-021's commits (`git revert <slice-021-merge-commit>` if using the new --merge flow, OR `git reset --hard <pre-slice-021>` on master if reverting before --merge ships).
2. Append a superseding methodology-changelog entry retracting BRANCH-1 (e.g., `## v0.36.0 — <date>` with `### Retired` section naming BRANCH-1 + retirement rationale).
3. Remove the new test files (`test_build_slice_skill_branch_create.py`, `test_commit_slice_skill_merge_flag.py`, `test_root_claude_md_branch_per_slice_rule.py`, `test_build_slice_skill_drift.py`, `test_commit_slice_skill_drift.py`, `test_branch_workflow_audit.py`) and the new audit (`tools/branch_workflow_audit.py`).
4. Remove the new entry-pin + ADR-pin tests from `test_methodology_changelog.py`.
5. Forward-sync the reverted `methodology-changelog.md` + `skills/build-slice/SKILL.md` + `skills/commit-slice/SKILL.md` + `ai-sdlc-VERSION` to `~/.claude/`. Confirm byte-equality.
6. Atomic version bump (post-retirement bump 0.35.0 → 0.36.0 or whatever VERSION ends up at).
7. Restore `--do-commit` flag on `skills/commit-slice/SKILL.md` if retraction is total (vs. partial retraction keeping `--merge` but reverting branch-create).

**Irreversible portion** (minor, append-only):
- The `methodology-changelog.md` v0.35.0 entry itself becomes part of the append-only changelog history. Retraction is a SUPERSEDING entry, NOT a deletion.
- Cumulative slice-022-N slices that ran under BRANCH-1 (with merge commits in git history) are part of the project's empirical record. Branch-merge commits CAN be reverted in fresh future commits but the merge-commit nodes themselves stay in `git log --graph`.

Both irreversible portions are documentation-record-class (not functional-behavior-class). Neither prevents revert.

**Conclusion**: Reversibility is **cheap**. Magnitude is **~25 source files + 5 test-file extends = 30 total touches** (per /critique-rerun M4-new ACCEPTED-FIXED option (b) canonical single-enumeration in design.md §Files changed) — larger than prior /critique-time-only codifications but well within MEDIUM effort budget. Revert path is well-trodden by 9 prior codification slices. Adopt Option 1 (3-sub-mode discipline at `## Prerequisite check ### Branch state` sub-section in `/build-slice` + `/commit-slice` `--merge` + BRANCH-1 audit at /build-slice Step 6; note: original draft "Step 0.5 / Phase 6" vocabulary retired per /critique B3 ACCEPTED-PENDING + /critique-rerun B1-residual ACCEPTED-FIXED 22-site sweep in favor of `## Prerequisite check ### Branch state` sub-section per slice-017 TPHD-1 precedent).
