# Design: Slice 021 add-feature-branch-workflow-at-build-and-commit-slice

**Date**: 2026-05-14
**Mode**: Standard

## What's new

(All "Step 0.5 / Phase 0.5 / Phase 6" framing retired per /critique B3 ACCEPTED-PENDING — replaced with `## Prerequisite check ### Branch state` sub-section + `Step 6 pre-finish gate` per slice-017 ADR-016 TPHD-1 vocabulary precedent at methodology-changelog v0.32.0 L102.)

- NEW `### Branch state` sub-section under existing `## Prerequisite check` H2 in `skills/build-slice/SKILL.md`. Resolves repo's default branch via `git symbolic-ref refs/remotes/origin/HEAD` with `git config init.defaultBranch` fallback (per /critique M1 ACCEPTED-PENDING — replaces hard-coded `master`/`main`); if HEAD is on the resolved default branch, creates `slice/NNN-<name>` from HEAD; switches to it if branch exists; STOPs and asks the user if on any other branch.
- NEW canonical-shape sentence in `skills/build-slice/SKILL.md` Step 7c flight-recorder discipline (per /critique B1 ACCEPTED-PENDING): canonical `BRANCH=skip` line shape `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` pinned with HH:MM required + `rationale:` token required (narrows the empirical-but-permissive parent DEVIATION convention for audit-quality).
- REPLACED flag `--do-commit` → `--merge` in `skills/commit-slice/SKILL.md` argument-hint frontmatter + Step 5 prose. New `--merge` semantics: pre-flight guardrails (no stale `slice/*` branches; `git status --porcelain` empty); `git add` + `git commit` on current slice branch with generated message; `git checkout <default-branch>`; `git merge --no-ff slice/NNN-<name>` with a merge-commit message referencing the slice; explicit `Confirm merge + delete? (yes/no)` user confirmation; `git branch -d slice/NNN-<name>` (safe-delete, local only).
- NEW audit `tools/branch_workflow_audit.py` (BRANCH-1) — invocable as `$PY -m tools.branch_workflow_audit <slice-folder>`; validates current git branch matches the active slice's `slice/NNN-<name>` pattern; resolves default branch via symbolic-ref + init.defaultBranch fallback; documented `BRANCH=skip` escape-hatch via build-log.md Events conforming to the canonical regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+`.
- NEW Step 6 pre-finish gate entry in `skills/build-slice/SKILL.md` invoking BRANCH-1.
- UPDATED 3 stale-doc surfaces (per /critique B2 ACCEPTED-PENDING — retracts prior "zero external consumers" claim): `pipeline.md` L97, `tutorial.md` L750, `tutorial-site/Hybrid AI SDLC Pipeline.html` L583 each get `--do-commit` → `--merge` replacement reflecting the new semantics.
- NEW `architecture/decisions/ADR-019-branch-per-slice-workflow.md` documenting the decision (reversibility: cheap; supersedes: null).
- NEW `architecture/methodology-changelog.md` v0.35.0 entry naming BRANCH-1, its 3 sub-modes (build-time branch-create + commit-time `--merge` + audit-time pre-finish refusal), Limitations note acknowledging local-only scope, atomic version bump 0.34.0 → 0.35.0.
- NEW `architecture/shippability.md` row 21 enumerating BRANCH-1 critical-path tests (audit-clean run on a synthetic slice branch fixture).
- NEW bullet in root `CLAUDE.md` "Brownfield rules" section: `Branch-per-slice`. Pointer to `/build-slice` `## Prerequisite check ### Branch state` sub-section + `/commit-slice --merge`.
- NEW test directory `tests/tools/` with `__init__.py` and 1 test file `test_branch_workflow_audit.py` (BRANCH-1 unit tests against synthetic git repos).
- NEW prose-pin test files:
  - `tests/methodology/test_build_slice_skill_branch_create.py` — 4 prose-pin asserts on the `## Prerequisite check ### Branch state` sub-section.
  - `tests/methodology/test_commit_slice_skill_merge_flag.py` — 3 prose-pin asserts on `--merge` semantics + `--do-commit` removal.
  - `tests/methodology/test_root_claude_md_branch_per_slice_rule.py` — 1 prose-pin assert on the new CLAUDE.md bullet.
- NEW mini-CAD drift tests for the 2 newly-modified skill SKILL.md files:
  - `tests/methodology/test_build_slice_skill_drift.py` — sha256 byte-equality in-repo ↔ installed.
  - `tests/methodology/test_commit_slice_skill_drift.py` — sha256 byte-equality in-repo ↔ installed.
- NEW shippability-catalog row test `tests/shippability/test_row_021_branch_workflow.py` (mirrors slice-020 row-20 pattern at `tests/shippability/test_row_020_*.py` if that convention is followed; otherwise a new sub-directory under `tests/methodology/` matching project precedent — `/build-slice` will pick the right path).
- NEW entry-pin tests in `tests/methodology/test_methodology_changelog.py` for the v0.35.0 BRANCH-1 entry (3 sub-mode names + STOP-and-route-equivalent merge-conflict-error-handling clause + Limitations local-only-scope clause).
- NEW ADR-pin test in `tests/decisions/` (or wherever ADR-pins live per project convention) verifying `ADR-019-*.md` exists, frontmatter parses, and body names BRANCH-1.
- PLUGIN MANIFEST update: `plugin.yaml.version` 0.34.0 → 0.35.0; `tools:` list gains `branch_workflow_audit`. `tools/install_audit.py` canonical list mirrors the addition.
- VERSION bumps: in-repo `VERSION` 0.34.0 → 0.35.0; forward-sync to `~/.claude/ai-sdlc-VERSION`.

## What's reused

- [[skills/build-slice/SKILL.md]] — 3 insertion points: (1) NEW sub-section within existing `## Prerequisite check` H2 at L17-23 (NOT a new Step 0.5 — slice-017 TPHD-1 vocabulary precedent); (2) NEW canonical-shape sentence in existing Step 7c flight-recorder block at L222-243; (3) NEW pre-finish gate checklist bullet in existing Step 6 at L93-107.
- [[skills/commit-slice/SKILL.md]] — Step 5 prose replacement at L142-149 boundary (replace `--do-commit` flag handling with `--merge` flow + 5-step + 2 pre-flight guardrails).
- [[skills/slice/SKILL.md]] — NOT TOUCHED (Step 3c BFRD-1 reference at slice-020 stays as-is; BRANCH-1 doesn't require slice-skill changes).
- [[agents/critique.md]] — NOT TOUCHED (CAD-1 byte-equality preserved at slice-017 ship hash `f34c967eaaa34413`); BRANCH-1 is an audit-enforced gate, not a /critique-time prose discipline (-D suffix not applicable).
- [[architecture/decisions/ADR-018-bfrd-1-bug-fix-repro-prelude-discipline]] — most recent ADR, used as structural shape template for ADR-019.
- [[architecture/methodology-changelog.md]] — v0.34.0 entry (BFRD-1) is the immediate predecessor; v0.35.0 entry follows that shape.
- [[architecture/shippability.md]] — row 20 (BFRD-1) is the immediate predecessor; row 21 follows that single-line-per-row format.
- [[tests/methodology/conftest.py]] — `repo_root` fixture + `read_file()` helper reused by new prose-pin tests.
- `tools/critique_agent_drift_audit.py` — pattern reference for the new `tools/branch_workflow_audit.py` (CLI shape: `--json`, exit codes 0/1/2, structured findings).
- `tools/plugin_manifest_audit.py` — reused at pre-finish to verify the new audit is enumerated.
- `tools/install_audit.py` — reused at pre-finish to verify INST-1 canonical list matches `plugin.yaml`.

## Components touched

### `skills/build-slice/SKILL.md` (modified)

- **Responsibility**: defines the canonical build-execution flow for a slice. Adds branch-create as a structural prerequisite (NOT a new step) per slice-017 TPHD-1 precedent.
- **Lives at**: `skills/build-slice/SKILL.md`
- **Key interactions**: read by Claude main thread at `/build-slice` invocation; cross-referenced from `/critique` (Step 6 pre-finish gates), `/validate-slice`, `/reflect`. Forward-synced to `~/.claude/skills/build-slice/SKILL.md` (mini-CAD-1 byte-equality invariant enforced by new `test_build_slice_skill_drift.py`).
- **What changes**:
  1. Insert NEW `### Branch state` sub-section as a 3rd bullet OR sub-heading WITHIN existing `## Prerequisite check` H2 (currently L17-23). Body specifies: (a) detect `git branch --show-current`; (b) resolve repo default branch via `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'` with `git config init.defaultBranch` fallback; STOP if neither resolves; (c) if HEAD is on the resolved default branch: create `slice/NNN-<slice-name>` from HEAD via `git checkout -b slice/NNN-<slice-name>`; (d) if `slice/NNN-<slice-name>` already exists (resume after session death): `git checkout slice/NNN-<slice-name>`; (e) if any other branch: STOP, ask the user to switch to default branch or document `BRANCH=skip` escape-hatch in build-log.md Events using the canonical shape pinned in Step 7c; (f) if working tree is dirty (`git status --porcelain` non-empty): STOP, ask user to commit or stash first — no auto-stash.
  2. Add 1 sentence to existing Step 7c flight-recorder discipline canonicalizing the `BRANCH=skip` line shape: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` (canonical-shape with HH:MM REQUIRED and `rationale:` token REQUIRED; narrows the empirically-permissive parent convention).
  3. Existing Step 6 pre-finish gate checklist (L93-107) gains a NEW bullet: `- [ ] **BRANCH-1 audit passes** — see "Branch state pre-finish audit" below`. New sub-section after Step 6 enumerates the invocation: `$PY -m tools.branch_workflow_audit architecture/slices/slice-NNN-<name>`.

### `skills/commit-slice/SKILL.md` (modified)

- **Responsibility**: generates audit-grade commit message AND (optionally) integrates the slice branch back to default-branch.
- **Lives at**: `skills/commit-slice/SKILL.md`
- **Key interactions**: read by Claude main thread at `/commit-slice` invocation; runs after `/reflect` (slice already archived). Forward-synced to `~/.claude/skills/commit-slice/SKILL.md` (mini-CAD-1 byte-equality invariant enforced by new `test_commit_slice_skill_drift.py`).
- **What changes**:
  1. Frontmatter `argument-hint: [--do-commit]` → `argument-hint: [--merge]`. "Argument modes" section: replace bullet `--do-commit` with `--merge`.
  2. Step 5 "Present or execute": replace `**With --do-commit**:` block with `**With --merge**:` block enumerating the 5-step flow:
     - Pre-flight 1: refuse if `git for-each-ref --format='%(refname)' refs/heads/slice/` returns any non-current `slice/*` branches (B5 stale-branch guardrail).
     - Pre-flight 2: refuse if `git status --porcelain` returns non-empty (M5 WT-loss guardrail) — STOP with "uncommitted changes detected; resolve before --merge".
     - Step 1: `git add` slice-folder changes; `git commit -m "$(cat <<'EOF' ... EOF)"` on current slice branch.
     - Step 2: Resolve default branch (`git symbolic-ref refs/remotes/origin/HEAD` etc.); `git checkout <default-branch>` (only after Pre-flight 2 confirms WT clean); `git merge --no-ff slice/NNN-<name> -m "Merge slice/NNN-<name>: <intent>"`. If conflict: STOP, leave default-branch in conflicted state, print recovery instructions per design.md "Error model".
     - Step 3: Explicit `Confirm merge + delete? (yes/no)` prompt (M5 unrecoverable-without-push guardrail); abort skill if user says no.
     - Step 4: `git branch -d slice/NNN-<name>` (safe-delete; STOP if refused; never `-D`).
  3. Add "Critical rules" entries: NEVER push, NEVER `--force`, NEVER `-D`, NEVER auto-resolve conflicts.

### `tools/branch_workflow_audit.py` (created)

- **Responsibility**: validates that the current git branch matches the active slice's `slice/NNN-<name>` pattern, with documented escape-hatch.
- **Lives at**: `tools/branch_workflow_audit.py` (created by this slice).
- **Key interactions**: invoked by `/build-slice` Step 6 pre-finish gate; unit-tested by `tests/tools/test_branch_workflow_audit.py`; enumerated in `plugin.yaml.tools` (PMI-1 gate); listed in `tools/install_audit.py` canonical list (INST-1 gate).
- **CLI shape** (mirrors `critique_agent_drift_audit.py` pattern):
  - `python -m tools.branch_workflow_audit <slice-folder>` — basic invocation; reads slice number + name from folder; calls `git branch --show-current` via subprocess; matches against expected pattern.
  - `python -m tools.branch_workflow_audit --json <slice-folder>` — JSON output for /build-slice machine-readable parse.
  - `python -m tools.branch_workflow_audit --root <repo-root> <slice-folder>` — explicit repo root override (mirrors `plugin_manifest_audit`).
  - Exit codes: 0 clean (branch matches OR documented escape-hatch in build-log.md Events) ; 1 violation (branch doesn't match AND no escape-hatch) ; 2 usage error (slice folder doesn't exist, build-log.md unreadable for escape-hatch check, git not available).
- **Escape-hatch mechanism**: scan `<slice-folder>/build-log.md` Events section for a line matching `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+` (canonical phrase per slice-018+ flight-recorder discipline). Presence = audit returns clean with `escape_hatch_used: true` in JSON output; absence + branch mismatch = violation.

## Contracts added or changed

### `python -m tools.branch_workflow_audit` CLI (new)

- **Endpoint**: command-line entry point at `tools/branch_workflow_audit.py:__main__`.
- **Auth model**: none (local development tool; no network calls; reads git via subprocess + reads slice-folder files via Pathlib).
- **Input contract** (positional + flags): `<slice-folder>` required; `--json` / `--root` / `--help` optional.
- **Output contract** (JSON when `--json`):
  ```json
  {
    "slice_folder": "architecture/slices/slice-021-...",
    "expected_branch": "slice/021-add-feature-branch-workflow-at-build-and-commit-slice",
    "actual_branch": "<current branch>",
    "status": "clean" | "violation" | "escape-hatch-used",
    "escape_hatch_used": false,
    "escape_hatch_rationale": null,
    "violations": []
  }
  ```
- **Error cases**: slice folder missing → exit 2 + stderr "slice folder not found: …" ; git not available → exit 2 + stderr "git not on PATH" ; build-log.md unreadable when escape-hatch line lookup needed → exit 2 with explicit cause.

### NEW `/build-slice` Prerequisite check `### Branch state` sub-section contract (skill-prose discipline)

- **Responsibility**: build-slice's runtime branch-create discipline.
- **Defined in code at**: `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section.
- **Contract surface**: prose-heuristic — Claude main thread reads + executes the prose. No machine-readable contract.

### NEW `/commit-slice --merge` flag contract

- **Responsibility**: replaces `--do-commit` semantics with integrated commit-and-merge flow.
- **Defined in code at**: `skills/commit-slice/SKILL.md` frontmatter + Step 5.
- **Backward compatibility**: NONE. `--do-commit` is REMOVED, not aliased. Users on the old workflow re-learn. Rationale: clean break is cheaper than carrying a deprecation alias on a methodology-research codebase with zero non-repo consumers per [[architecture/triage.md]] adoption-record (per /critique B2 ACCEPTED-PENDING: 3 in-repo doc surfaces — `pipeline.md` L97, `tutorial.md` L750, `tutorial-site/Hybrid AI SDLC Pipeline.html` L583 — atomically updated this slice).

## Data model deltas

None. Pure workflow + tooling slice; no schemas, no entities, no migrations.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/branch_workflow_audit.py` | `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section + Step 6 pre-finish gate | `tests/tools/test_branch_workflow_audit.py::test_branch_workflow_audit_*` | — |
| `tests/tools/__init__.py` | — | — | rationale: pytest discovery init; no consumer demanded (sibling of existing `tests/methodology/__init__.py` empty-file pattern) |

The 4 new test files (`test_build_slice_skill_branch_create.py`, `test_commit_slice_skill_merge_flag.py`, `test_root_claude_md_branch_per_slice_rule.py`, `test_branch_workflow_audit.py`) + 2 new mini-CAD drift tests + 1 new shippability-catalog test + 1 new ADR-pin test are CONSUMERS, not new modules requiring further consumers — they don't appear in the matrix per slice-018+ precedent.

## Decisions made (ADRs)

- [[ADR-019]] — branch-per-slice workflow codified as BRANCH-1 (3 sub-modes: build-time branch-create at `/build-slice` `## Prerequisite check ### Branch state` sub-section + commit-time `--merge` flag at `/commit-slice` Step 5 + audit-time pre-finish refusal at BRANCH-1 audit invoked from `/build-slice` Step 6) — reversibility: **cheap**

## Authorization model for this slice

Local-only git authority (no `git push`, no remote-delete). BUT `--merge` introduces 2 NEW local-state-loss paths not present in today's `--do-commit` flow (per /critique M5 ACCEPTED-PENDING). Defense-in-depth applies to destructive local operations even though no authn/authz surface is introduced:

1. **`git checkout <default-branch>` silent-WT-discard path**: `git checkout` can silently discard uncommitted WT changes in files NOT modified between the slice branch and default-branch (git's checkout proceeds without complaint). Concrete loss: user edits a file mid-/commit-slice (e.g., a Test-WT change to verify post-merge behavior), `--merge` proceeds, the user's WT change is lost on `git branch -d`. **Mitigation (must-not-defer)**: hard `git status --porcelain` empty-check BEFORE `git checkout <default-branch>` — STOP on any non-empty output with explicit "uncommitted changes detected; resolve before --merge" message.

2. **`git branch -d slice/NNN-<name>` unrecoverable-without-push path**: safe-delete (refuses unmerged branches) is safe in the merge sense, but the slice branch was never pushed to remote (local-only v1) so once `-d` succeeds the user's record of that branch's individual commits is gone (the merge-commit preserves content but loses the per-commit history if those individual commits weren't pushed elsewhere). **Mitigation (must-not-defer)**: explicit `Confirm merge + delete? (yes/no)` user-confirmation prompt BEFORE `git branch -d` — abort skill if user says no, leaving the merged slice branch present for user inspection.

## Error model for this slice

Four failure surfaces, each with explicit STOP-rather-than-silent-continue handling:

1. **`/build-slice` `## Prerequisite check ### Branch state` — wrong starting branch / default-branch resolution failure**:
   - Currently on a non-default / non-`slice/*` branch → STOP. Print: "Refuse to auto-create slice branch on top of `<current>`. Either switch to the default branch first, or document `BRANCH=skip` escape-hatch in build-log.md Events with rationale (using the canonical shape from Step 7c)."
   - Dirty working tree → STOP. Print: "Working tree is dirty. Commit or stash before slice branch creation. The skill does not auto-stash."
   - `git checkout -b` fails (branch already exists with different content) → STOP. Print: "Branch `slice/NNN-<name>` already exists with diverging history. Manual resolution required."
   - `git symbolic-ref refs/remotes/origin/HEAD` AND `git config init.defaultBranch` BOTH fail to resolve → STOP. Print: "Cannot resolve repo default branch. Set `git config init.defaultBranch <name>` or add `origin` remote with HEAD reference, then retry."

2. **`/commit-slice --merge` — pre-flight + git operations fail**:
   - Pre-flight 1 (stale `slice/*` branches present) → STOP. Print: "Stale slice branches detected: `<list>`. These are artefacts of prior unresolved conflicts. Resolve manually (`git branch -d` each, after verifying merged) before retrying `--merge`."
   - Pre-flight 2 (dirty WT) → STOP. Print: "Uncommitted changes detected. Commit or stash before `--merge` (closes M5 silent-WT-discard path)."
   - `git checkout <default-branch>` fails despite clean Pre-flight 2 → STOP. Print: "Cannot switch to `<default-branch>` (likely detached HEAD). Resolve manually."
   - `git merge --no-ff slice/NNN-<name>` produces conflicts → STOP. Print: "Merge conflict at `<files>`. Resolve manually, then `git commit` to finalize the merge. Do NOT re-run `/commit-slice --merge` post-conflict — the slice branch will linger; cleanup is manual in v1 (recovery flow deferred to follow-on slice `add-merge-conflict-recovery-to-commit-slice-merge`)." Default-branch left in conflicted state.
   - User declines `Confirm merge + delete? (yes/no)` prompt → ABORT skill cleanly (NOT a STOP — leaves merged slice branch present for user inspection; user can manually `git branch -d` later).
   - `git branch -d slice/NNN-<name>` fails (unmerged) → STOP. Print: "Safe-delete refused (branch has unmerged commits). Inspect with `git log <default>..slice/NNN-<name>`. Do NOT use `-D` without understanding what's being discarded." Skill exits without deleting.

3. **BRANCH-1 audit — pre-finish refusal**:
   - Current branch is the resolved default branch AND no `BRANCH=skip` escape-hatch in build-log.md Events conforming to canonical regex → exit 1 with finding "active-slice work occurred on default branch".
   - Current branch is `slice/NNN-<wrong-name>` (mismatch) → exit 1 with finding "active-slice branch name does not match active slice".
   - Escape-hatch line present BUT doesn't conform to canonical regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+` → exit 1 with finding "BRANCH=skip line present but malformed; expected `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` (canonical Step 7c shape)".
   - Slice folder missing OR build-log.md missing when escape-hatch check needed → exit 2 (usage error).
   - git not on PATH → exit 2 with explicit cause.
   - Default-branch resolution fails (symbolic-ref + init.defaultBranch both fail) → exit 2 with "cannot resolve default branch; cannot determine if current branch is protected".

4. **Cross-slice-branch leakage at upstream skills (M-add-4 ESCALATED resolution)**: BRANCH-1 v1 does NOT enforce at `/slice` + `/design-slice` + `/critique` + `/critique-review` — those upstream skills may run on any branch. If the user just shipped slice-(N-1) without `--merge` and stayed on `slice/(N-1)`, then /slice for slice-N authors slice-N artifacts on the wrong branch; BRANCH-1's STOP at `## Prerequisite check ### Branch state` will surface this AT /build-slice but recovery requires `git cherry-pick` or `git checkout master && git stash pop` mid-state. v1 carves out this scope explicitly in Limitations item 8 below; future slice `add-pipeline-wide-branch-discipline-to-upstream-slice-skills` covers it.

## Self-application of BRANCH-1 at this slice

Per RSAD-1 (recursive-self-application discipline, slice-011): this slice IS the canonical reference instance #1 of BRANCH-1. The expectation is that slice-021's own /build-slice run will fire the new `## Prerequisite check ### Branch state` sub-section, create `slice/021-add-feature-branch-workflow-at-build-and-commit-slice`, and /commit-slice --merge will be the canonical first invocation of the new flag. Build-log.md Events will record the 4 branch-state transitions for forensic capture.

Two caveats:
1. **Bootstrap ordering**: the skill prose that defines the new `## Prerequisite check` sub-section (post /critique B3 ACCEPTED-PENDING — replaces original "Step 0.5" framing) is itself written in this slice. There is a brief moment between `/design-slice` ship and `/build-slice` start where the skill on disk doesn't yet contain the branch-create sub-section — the sub-section is being added in /build-slice's own task plan. Workaround: at /build-slice Step 1 plan-mode time, Claude manually fires the equivalent (creates the slice branch by hand before plan-mode entry) and records this in build-log.md Events as a canonical BRANCH=skip-bootstrap DEVIATION line (per /critique B1 ACCEPTED-PENDING shape + B4 ACCEPTED-PENDING literal text). RSAD-1 self-application at slice-021 is therefore a **bootstrap reference instance**, not a runtime-of-fully-codified-rule instance. The first non-bootstrap reference instance is **the next non-/repro slice after this one** (per /critique m2 ACCEPTED-FIXED — softened from prior "slice-022" speculation; if slice-022 is a /repro, then slice-023+).
2. **`/commit-slice --merge` bootstrap**: by /commit-slice time, the new `--merge` flag prose exists in the local in-repo SKILL.md but NOT in `~/.claude/skills/commit-slice/SKILL.md` (mini-CAD forward-sync happens at /build-slice end, which is right before /commit-slice). Claude main thread reads the in-repo SKILL.md when running /commit-slice in this repo — so `--merge` works locally. Forward-sync after /commit-slice is acceptable if mini-CAD drift test runs at the END of the slice's /validate-slice gate.

3. **Cross-slice-branch leakage prevention at slice-021 ship**: per Limitations item 8 + Error model surface 4, BRANCH-1 v1 doesn't enforce at `/slice` + `/design-slice` + `/critique` + `/critique-review`. Before shipping slice-021, /build-slice MUST verify (a) the current branch is `slice/021-add-feature-branch-workflow-at-build-and-commit-slice` (set up at bootstrap before plan-mode entry per caveat 1); (b) no stale `slice/*` branches present (BRANCH-1 audit *warns on* this — per /critique-rerun m3 ACCEPTED-FIXED; for slice-021 bootstrap vacuously satisfied since no `slice/*` branches exist pre-ship); (c) build-log.md Events records the canonical bootstrap DEVIATION line. The pipeline-wide cross-slice-branch leakage prevention is queued as follow-on slice `add-pipeline-wide-branch-discipline-to-upstream-slice-skills`.

## Cumulative-Critic-influence note

(Post /critique + /critique-review + TRI-1 redesign rerun — empirical update.)

Per slice-019/020 lesson "codification slices that codify a discipline almost always commit instances of that discipline on their own draft": slice-021 **empirically validated this hypothesis at high density**. First /critique returned 14 findings (5 Blockers + 5 Majors + 4 Minors); /critique-review surfaced 4 more (1 Blocker + 3 Majors) = **18 findings, new project HWM**. Of these, **5 distinct recursive-self-application defects** on disciplines slice-021's own predecessors codified against:
- B3: slice-017 TPHD-1 vocabulary (Step-0/Phase-0 retired at v0.32.0 L102)
- M4: slice-020 B3 Wiegers regression-guard coverage-symmetry count-drift
- M-add-1: meta-Critic-caught count-drift WITHIN slice-021's own M3 fix block (exact slice-020 M-add-1 recurrence)
- M-add-2: TPHD-1 sub-mode (a) violation WITHIN slice-021's own M3 + m3 fix blocks
- M-add-3: B3 vocabulary survival in Must-not-defer block missed by first Critic

Recursive-self-application N=17 → **N=28 cumulative HWM** at slice-021 codification (was N=12 at slice-019; N=17 at slice-020; +5 first-Critic + 6 /critique-rerun + 4 /critique-review-rerun = 15 distinct instances within slice-021 lifecycle alone = empirical project HWM per /critique-review-rerun M-add-3-rerun ACCEPTED-FIXED N-ratchet propagation; harmonized with ADR-019 L158 canonical count).

BRANCH-1 itself is **bootstrap-reference-instance N=1** at codification time; non-bootstrap N=1 starts at the next non-/repro slice after this one.

EPGD-1 self-application N=6 → N=7 stable preserved: slice-021 ADDS-only against the prior entry-pin function list at `tests/methodology/test_methodology_changelog.py` — no body-edit of prior `_v_0_NN_0_*` entry-pin functions; only adds NEW `_v_0_35_0_branch_1_*` entry-pin functions per design.md L213-217 enumeration.

SCPD-1 self-application N=3 → N=4 stable: shippability row 21 propagates BRANCH-1 consumer references in-line BEFORE /validate-slice catalog run; Command cell enumerates exactly 14 invocation targets per M-add-1 canonical recount.

TPHD-1 self-application N=4 → N=5 partial: /critique + /design-slice-rerun + /critique-rerun fix-prose harmonized 3 named surfaces (mission-brief.md + design.md Files-changed + ADR-019) but milestone.md L43/L46 + design.md L197/L209/L211 carried residual stale counts caught at /critique-review-rerun M-add-1-rerun + M-add-2-rerun + M-add-3-rerun (now swept inline at TRI-1). Honest status: N=5 reached via 4 passes of fix + meta-review (initial /critique + /critique-review + /critique-rerun + /critique-review-rerun), not via a single Builder-self-check. The /critic-calibrate slice-022 sub-clause promotion is the structural closure for the class — per /critique-rerun M1-residual + /critique-review-rerun's empirical demonstration that fix-block-completeness recursion is provably outside any single Builder-self-check's reach.

BFRD-1 contingent N/A: slice-021 is a feature/methodology slice (not bug-fix; name has no `fix-*`/`*-fix`/etc. shape; source signal is workflow enhancement). STOP-route vacuously satisfied per slice-020 contingent-inapplicability precedent.

Wiegers regression-guard coverage-symmetry watch-list **N=5 → N=9 cumulative** with 4 NEW instances within slice-021 itself (first-Critic M4 + meta-Critic M-add-1 + /critique-rerun B3-new violations 1+2 + /critique-review-rerun M-add-1-rerun + M-add-3-rerun) — **promotion to Dim 9 sub-clause ELEVATED to /critic-calibrate slice-022** (from slice-024+) per /critique-rerun M1-residual ACCEPTED-FIXED + /critique-review-rerun M-add-3-rerun ACCEPTED-FIXED. The slice-021 own-draft contribution alone meets the N≥3 promotion threshold with margin; the class is empirically the dominant recurrence class for codification slices and is structurally outside any single Builder-self-check's reach (per /critique-rerun M1-residual empirical falsification + /critique-review-rerun's 4 missed findings within the rerun's own fix-block).

DR-1 catch-class diversification N=8 → **N=10 cumulative stable** with 2 NEW class candidates at N=1 from slice-021: (a) /critique-review M-add-4 *Cross-slice-branch leakage at upstream skill pipeline* (promote at N≥3); (b) /critique-review-rerun M-add-2-rerun *Milestone-summary surface as load-bearing claims-propagation target* (the rerun /critique's grep scope excluded milestone.md, producing 2 missed propagations at L43/L46 — distinct from prior Wiegers count-drift class; promote at N≥3 if recurs at slice-022+).

## Limitations / explicit non-coverage

1. **Local-only `--merge` is STRUCTURALLY WRONG for non-solo projects (DEVIATION-5 + slice-022 candidate)**: `--merge`'s local merge to default branch + `git push origin <default>` either (a) fails on protected branches (GitHub branch protection, GitLab merge rules), (b) bypasses required PR review, or (c) skips CI evaluation on the slice branch in isolation. Slice-021 ships local-only as a documented v1 limitation because this codebase is solo + no protected branches + no CI on master; for any other project the `--merge` sub-command is wrong by default. **Slice-022 candidate `redesign-commit-slice-for-pr-aware-flow`**: DROP `--merge` sub-command entirely; replace with `--push` flag that pushes the slice branch to origin (user creates PR + merges manually via UI). BRANCH-1 sub-mode (a) build-time branch-create + sub-mode (c) audit-time pre-finish refusal stay unchanged in slice-022; only sub-mode (b) is redesigned. ADR-020 (slice-022) will supersede ADR-019 Option 1's sub-mode (b) decision.
2. **Single-merge-strategy**: `--no-ff` only. Squash and rebase are deferred (`add-squash-merge-toggle-to-commit-slice`).
3. **Branch-prefix uniformity**: `slice/NNN-<name>` for all slices, regardless of BFRD-1 classification. Per-classification prefixes (`feat/`, `fix/`, `bugfix/`) deferred (`add-classified-branch-prefix-to-build-slice`).
4. **No auto-stash**: dirty WT at `## Prerequisite check ### Branch state` STOPs; user must explicitly handle. Auto-stash deferred (`add-auto-stash-at-build-slice-prerequisite-check-branch-state`).
5. **No `git branch -D`**: safe-delete only. Force-delete escape-hatch deferred (`add-force-delete-escape-hatch-to-commit-slice-merge`).
6. **No history rewrite on slice branch**: amend / rebase / squash-merge forbidden in v1. Deferred per (2).
7. **Detection mode = current-branch-name only**: BRANCH-1 doesn't validate that the slice branch was actually created from default-branch HEAD (vs. branched from another slice branch by mistake). Origin-validation deferred (`add-branch-origin-validation-to-branch-1`).
8. **`/build-slice`-only enforcement (per /critique M-add-4 ESCALATED resolution — option (a) chosen)**: BRANCH-1 sub-modes (a/b/c) only fire at `/build-slice` + `/commit-slice` + `/build-slice` Step 6 audit. The 4 upstream skills `/slice` + `/design-slice` + `/critique` + `/critique-review` author files into the slice-N folder before /build-slice runs; they currently have NO branch guard. If the user shipped slice-(N-1) without `--merge` and stayed on `slice/(N-1)` branch, then /slice for slice-N authors slice-N artifacts on the wrong branch; BRANCH-1's `## Prerequisite check ### Branch state` STOP at /build-slice surfaces this AFTER the fact, requiring `git stash pop` / `git cherry-pick` recovery. **v1 punts pipeline-wide enforcement to follow-on slice** `add-pipeline-wide-branch-discipline-to-upstream-slice-skills`. User is responsible for ensuring previous slice was `--merge`d before starting `/slice` for new slice. (Rationale: pipeline-wide scope inflates this slice's magnitude to ~35+ sites — would split into 2 slices anyway; original user ask was `/build-slice` anchor.)
9. **No bootstrap-slice handling in `## Prerequisite check ### Branch state` prose** (per /critique B4 ACCEPTED-PENDING resolution): the slice-021 bootstrap (where the new sub-section prose is being written by the very build that uses it) is handled manually per "Self-application of BRANCH-1" caveat 1 below. Build-log.md Events MUST contain the canonical bootstrap DEVIATION line: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip-bootstrap — rationale: ## Prerequisite check ### Branch state sub-section prose authored this slice; manual branch-create fired before sub-section exists on disk. RSAD-1 canonical bootstrap-reference instance #1.` Future bootstrap slices follow the same pattern with their own canonical-reference-instance qualifier.
10. **Merge-conflict-recovery flow not implemented (per /critique B5 ACCEPTED-PENDING option (c) chosen)**: v1 `--merge` STOPs at merge conflict with explicit instructions; user resolves manually. The slice branch lingers post-resolution; the merge commit message is hand-written (violates "CONSISTENT FORMAT" invariant). Pre-flight 1 guardrail surfaces the lingering branch at NEXT slice's `--merge`. Full recovery flow deferred to `add-merge-conflict-recovery-to-commit-slice-merge`.
11. **Design-time fix-block-completeness recursion** (per /critique M-add-1 + M-add-2 + M-add-3 ACCEPTED-PENDING + /critique-rerun M1-residual ACCEPTED-FIXED option (a) — empirical falsification: the /design-slice rerun authored a "Design-time fix-block-completeness self-check" Pre-finish-gate item AND immediately committed 5 fresh count-drift instances on its own rerun fix-block. The aspirational guard was retired at /critique-rerun M1-residual; no slice-local mitigation in v1. Wiegers regression-guard coverage-symmetry watch-list **N=9 cumulative** (N=5 prior + 2 within slice-021 first /critique + 5 within /critique rerun + 5 within /design-slice rerun ratchets the empirical evidence well past N=3 promotion threshold). Promotion to Dim 9 sub-clause at /critic-calibrate **ELEVATED to slice-022** (from slice-024+) — the class is empirically the dominant recurrence class for codification slices. The honest closure is `/critic-calibrate` codifies a sub-clause that the Critic checks adversarially, NOT a slice-local self-check that the same Builder authors then immediately falsifies.

## Insertion points (concrete file edits)

For `/build-slice` Step 1 plan-mode entry, here are the line ranges + canonical phrases to pin (post /critique B3 + M-add-2 + M-add-3 ACCEPTED-PENDING vocabulary harmonization across all surfaces):

1. **`skills/build-slice/SKILL.md` insertions** (2 sites):
   - **Site 1a: NEW sub-section in `## Prerequisite check` H2** (currently L17-23 — H2 stays; the new sub-section is a 3rd item WITHIN it, NOT a new top-level Step). Pick H3 `### Branch state` OR a 3rd numbered bullet — /build-slice plan-mode picks the structure-cleaner option per slice-017 TPHD-1 sub-mode (c) precedent (which used a numbered list inside the same `## Prerequisite check`). Canonical phrases pinned by prose-pin tests:
     - `"BRANCH-1"` (1+ occurrence in sub-section body)
     - `"slice/NNN-<slice-name>"` (canonical branch-name format)
     - `"BRANCH=skip"` (canonical escape-hatch token)
     - `"git symbolic-ref refs/remotes/origin/HEAD"` (default-branch resolution per /critique M1)
     - `"init.defaultBranch"` (default-branch fallback)
     - `"safe-delete"` or `"git branch -d"` (NOT `-D`)
   - **Site 1b: NEW canonical-shape sentence in existing Step 7c flight-recorder discipline** (currently L222-243 build-slice SKILL.md). Add 1 sentence canonicalizing `BRANCH=skip` line shape: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` (HH:MM required; rationale token required). Canonical phrases pinned:
     - `"BRANCH=skip — rationale:"` (literal canonical-shape exemplar)
     - `"HH:MM"` (timestamp requirement language)
   - **Site 1c: Existing Step 6 pre-finish gate checklist** (L93-107) gains 1 NEW bullet `- [ ] **BRANCH-1 audit passes**` + NEW sub-section after Step 6 documenting the invocation.
2. **`skills/commit-slice/SKILL.md` edits** — frontmatter L5 `argument-hint: [--do-commit]` → `argument-hint: [--merge]`; Step 5 L142-149 `**With --do-commit**:` block → `**With --merge**:` block enumerating the 5-step flow with pre-flight guardrails. Canonical phrases pinned:
   - `"--merge"` (NEW; ≥3 occurrences in Step 5)
   - `"--do-commit"` (REMOVED; 0 occurrences after edit)
   - `"git merge --no-ff"` (canonical merge command)
   - `"git branch -d"` (NOT `-D`)
   - `"Confirm merge + delete? (yes/no)"` (canonical M5 user-confirmation prompt)
   - `"git status --porcelain"` (canonical M5 WT-loss guardrail)
   - `"git for-each-ref --format='%(refname)' refs/heads/slice/"` (canonical B5 stale-branch guardrail)
   - `"NEVER push"` / `"never remote-delete"` / `"NEVER -D"` (canonical rules)
3. **`architecture/methodology-changelog.md` v0.35.0 entry** — prepended at file top after existing v0.34.0 entry. Canonical phrases pinned by entry-pin tests:
   - `"v0.35.0"` (version header)
   - `"BRANCH-1"` (rule ID; ≥3 occurrences)
   - `"Sub-mode (a)"` / `"Sub-mode (b)"` / `"Sub-mode (c)"` (3 sub-mode enumeration)
   - `"build-time branch-create"` / `"commit-time `--merge` flow"` / `"audit-time pre-finish refusal"` (canonical sub-mode names)
   - `"branch-per-slice workflow"` (canonical-phrase pinned across N=3 surfaces)
   - References to `Prerequisite check ### Branch state` (NOT "Step 0.5" / "Phase 0.5")
4. **`architecture/decisions/ADR-019-branch-per-slice-workflow.md`** — new file. Frontmatter mirrors ADR-018 shape; body sections: Context, Options considered (4 options), Decision (Option 1 chosen with M-add-4 option (a) v1 carveout), Consequences, Reversibility.
5. **`architecture/shippability.md` row 21** — single-line table row appended at L29 (after current L28 row 20). Format mirrors row 20. Command cell enumerates the canonical **14 invocation targets** (per /critique M-add-1 ACCEPTED-PENDING canonical recount: 8 whole-file targets + 6 `::test_*` named targets) using the canonical test function names from mission-brief.md TF-1 plan (per /critique M-add-2 ACCEPTED-PENDING harmonization):

   ```
   $PY -m pytest \
     tests/tools/test_branch_workflow_audit.py \
     tests/methodology/test_build_slice_skill_branch_create.py \
     tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py \
     tests/methodology/test_commit_slice_skill_merge_flag.py \
     tests/methodology/test_root_claude_md_branch_per_slice_rule.py \
     tests/methodology/test_build_slice_skill_drift.py \
     tests/methodology/test_commit_slice_skill_drift.py \
     tests/methodology/test_slice_skill_drift.py \
     tests/methodology/test_critique_agent_drift.py::test_critique_agent_drift_audit_clean_at_slice_021_ship \
     tests/methodology/test_install_audit.py::test_install_audit_enumerates_branch_workflow_audit \
     tests/methodology/test_plugin_manifest_audit.py::test_plugin_yaml_lists_branch_workflow_audit \
     tests/methodology/test_methodology_changelog.py::test_v_0_35_0_branch_1_entry_present_in_repo_and_installed \
     tests/methodology/test_methodology_changelog.py::test_v_0_35_0_branch_1_entry_names_three_sub_modes_in_repo_and_installed \
     tests/methodology/test_methodology_changelog.py::test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1 \
     -v
   ```

   That's **14 enumerated invocation targets across 11 test files** (8 whole-file pytest paths + 6 `::test_*` named-function pytest paths). RPCD-1 sub-mode (b) self-application N=2 → N=3 stable.

   Note: the ADR-pin test function name was harmonized to `test_adr_019_branch_per_slice_workflow_exists_and_links_to_branch_1` (TF-1 plan original) per /critique M-add-2 ACCEPTED-PENDING — replaces the earlier inconsistent `test_adr_019_exists_and_names_branch_1_canonical_phrase` from the first /critique M3 fix block.

6. **`CLAUDE.md` Brownfield rules section** — insert NEW bullet between existing `Graphify before wide changes.` and the closing of the brownfield-rules list. Canonical phrase: `"Branch-per-slice"` (bullet header).
7. **`plugin.yaml` tools list** — append `- id: branch_workflow_audit, path: tools/branch_workflow_audit.py`. Version line 0.34.0 → 0.35.0.
8. **`VERSION` file** → 0.35.0. `~/.claude/ai-sdlc-VERSION` forward-sync → 0.35.0.
9. **`tools/install_audit.py` canonical list** — add `branch_workflow_audit` to the tool inventory tuple.
10. **3 stale-doc surfaces** (per /critique B2 ACCEPTED-PENDING):
    - `pipeline.md` L97: `--do-commit` → `--merge` (update semantics description to match new 5-step flow).
    - `tutorial.md` L750: `--do-commit` → `--merge` (update tutorial text to match new flow).
    - `tutorial-site/Hybrid AI SDLC Pipeline.html` L583: `--do-commit` → `--merge` (update HTML text accordingly).
    Verification: `grep -F "--do-commit" pipeline.md tutorial.md tutorial-site/Hybrid\ AI\ SDLC\ Pipeline.html` returns 0 matches post-fix.

## Files changed (estimated count)

**~25 files total** (per /critique M4 ACCEPTED-FIXED + B2 ACCEPTED-PENDING canonical recount; harmonized with ADR-019 L152/L186/L203 + mission-brief.md). Files touched in this slice:

1. `skills/build-slice/SKILL.md` — NEW `## Prerequisite check ### Branch state` sub-section + Step 7c canonical BRANCH=skip shape sentence + Step 6 pre-finish gate addition
2. `skills/commit-slice/SKILL.md` — `--do-commit` → `--merge` swap + 5-step flow + 2 guardrails
3. `tools/branch_workflow_audit.py` (NEW) — BRANCH-1 audit + default-branch resolution helpers
4. `tools/install_audit.py` — append `branch_workflow_audit` to canonical list
5. `plugin.yaml` — version 0.34.0 → 0.35.0 + tools list addition
6. `VERSION` — 0.34.0 → 0.35.0
7. `~/.claude/ai-sdlc-VERSION` (forward-sync)
8. `~/.claude/skills/build-slice/SKILL.md` (forward-sync)
9. `~/.claude/skills/commit-slice/SKILL.md` (forward-sync)
10. `~/.claude/methodology-changelog.md` (forward-sync)
11. `architecture/methodology-changelog.md` — v0.35.0 entry naming BRANCH-1 + 3 sub-modes
12. `architecture/decisions/ADR-019-branch-per-slice-workflow.md` (NEW)
13. `architecture/shippability.md` — row 21 with 14-target Command cell
14. `CLAUDE.md` (root project) — NEW Brownfield-rules bullet `Branch-per-slice`
15. `pipeline.md` — L97 `--do-commit` → `--merge` (per /critique B2 ACCEPTED-PENDING)
16. `tutorial.md` — L750 `--do-commit` → `--merge` (per /critique B2 ACCEPTED-PENDING)
17. `tutorial-site/Hybrid AI SDLC Pipeline.html` — L583 `--do-commit` → `--merge` (per /critique B2 ACCEPTED-PENDING)
18. `tests/tools/__init__.py` (NEW — empty pytest discovery init)
19. `tests/tools/test_branch_workflow_audit.py` (NEW — 8 unit tests per AC #4)
20. `tests/methodology/test_build_slice_skill_branch_create.py` (NEW — 4 prose-pin tests per AC #1)
21. `tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py` (NEW — 1 prose-pin test per AC #2)
22. `tests/methodology/test_commit_slice_skill_merge_flag.py` (NEW — 4 prose-pin tests per AC #3)
23. `tests/methodology/test_root_claude_md_branch_per_slice_rule.py` (NEW — 1 prose-pin test)
24. `tests/methodology/test_build_slice_skill_drift.py` (NEW — mini-CAD)
25. `tests/methodology/test_commit_slice_skill_drift.py` (NEW — mini-CAD)
26. `tests/methodology/test_methodology_changelog.py` (extends — 3 entry-pin + 1 ADR-pin test)
27. `tests/shippability/test_row_021_branch_workflow.py` (NEW — shippability self-test)
28. `tests/methodology/test_install_audit.py` (extends — INST-1 enumeration test per /critique M2 ACCEPTED-FIXED)
29. `tests/methodology/test_critique_agent_drift.py` (extends — CAD-1 vacuously-clean test per /critique M2 ACCEPTED-FIXED)
30. `tests/methodology/test_plugin_manifest_audit.py` (extends — `branch_workflow_audit` enumeration test)

That's **~25 source files + 5 test-file extends = 30 total touches at slice-021 ship** (forward-sync mirrors counted with source files; PMI-1 atomic-bump invariant test is a 0-line extends since it's already PMI-1 v1.1 version-agnostic per slice-014 codification). Within slice-021's effort budget at MEDIUM (~3–4 hours). **Wiegers regression-guard coverage-symmetry watch-list ratchets to N=9 cumulative** (slices 016/017/019/020/021 — slice-021 contributes 4 instances: first-Critic M4 4-count drift + meta-Critic M-add-1 14-vs-11 drift within M3 fix block + /critique-rerun B3-new "7+7 vs 8+6" + /critique-review-rerun M-add-1-rerun + M-add-3-rerun — well past N=3 promotion threshold; **promotion to Dim 9 sub-clause ELEVATED to /critic-calibrate slice-022** per /critique-rerun M1-residual ACCEPTED-FIXED (from slice-024+). The /design-slice rerun's "Design-time fix-block-completeness self-check" Pre-finish item 11 was RETIRED at /critique-rerun M1-residual as aspirational + empirically falsified; structural closure is the adversarial Critic check at slice-022, NOT a Builder-self-check.
