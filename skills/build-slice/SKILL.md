---
name: build-slice
description: "AI SDLC pipeline. Execute the current slice with plan-mode + verification gates. Reads mission brief, enters plan mode to explore actual code, ships with mid-slice smoke gate, do-not-defer enforcement, and pre-finish gate. Use after /critique blockers are addressed. Trigger phrases: '/build-slice', 'build this slice', 'implement the slice', 'ship the slice'. Works from a 1-page mission brief plus plan mode, not a long sprint file."
user_invokable: true
---

# /build-slice — Execute With Plan Mode + Verification

You are executing the current slice. Approach: plan mode (Builder explores actual code) + mission-brief discipline (gates, do-not-defer, acceptance criteria).

The mission brief is the **intent**. The design is the **shape**. The Critic findings are the **constraints**. Plan mode is the **route through actual code**.

## Where this fits

Runs after `/critique` blockers + majors are addressed. Output: working code + tests + build-log. Hands off to `/validate-slice`.

## Prerequisite check

- Find active slice folder
- Read `mission-brief.md`, `design.md`, `critique.md`, new ADRs from this slice
- If `critique.md` shows BLOCKED: stop, tell user to address blockers first
- If `critique.md` doesn't exist (Standard or Heavy mode): stop, run `/critique` first
- **Run TPHD-1 pre-flight harmonization** (per `methodology-changelog.md` v0.32.0 sub-mode (c)): scan the mission-brief TF-1 plan table; for each row, verify (a) the Test path exists or will be created at the right path, (b) the Test function name will match what gets built. The /critique + /critique-review fix-prose may have changed test function names or AC row references without harmonizing the TF-1 plan in the same fix block (sub-modes (a) + (b) defend at fix-prose time; sub-mode (c) is the prerequisite-check defense-in-depth layer). Flag any drift to user for fix BEFORE Step 1 plan-mode entry. This closes the function-name-staleness audit gap that `tools/test_first_audit.py --strict-pre-finish` does not detect (status-only check per slice-017 /critique B1 ACCEPTED-FIXED).
- **Run CRP-1 critique-review-prerequisite check** (per `methodology-changelog.md` v0.40.0): runs AFTER the `critique.md`-exists check above (there can be no `/critique-review` without a `/critique`). Invoke:

  ```bash
  $PY -m tools.critique_review_prerequisite_audit architecture/slices/slice-NNN-<name>
  ```

  Refusal semantics (exit 1 → STOP):
  - `mandatory-critique-review-absent`: mode ∈ {STANDARD, HEAVY} AND `milestone.md` `critic-required: true` AND `critique-review.md` absent AND no canonical `critique-review-skip` frontmatter key.
  - `escape-hatch-malformed`: `critique-review-skip` key present but value off-canonical (not `^skip — rationale: .+`).
  - `usage-error` / `mode-unresolvable` (exit 2): slice folder / milestone.md missing, or mode unresolvable from `<vault>/triage.md` frontmatter `mode:` → fallback `CLAUDE.md` `**Mode**:`.

  On `mandatory-critique-review-absent`, STOP and tell the user verbatim: **"STOP: this slice has a mandatory `/critique-review` (DR-1) that has not been run. Run `/critique-review` for this slice before `/build-slice`. If the skip is deliberate, document it by adding `critique-review-skip: \"skip — rationale: <text>\"` to milestone.md frontmatter (per ADR-024)."** Do not enter Step 1 plan mode until the audit exits 0.

  **Bootstrap exception (slice-026 only)**: per ADR-024, slice-026 is CRP-1 bootstrap-reference instance #1 — it authors this very sub-block, so this sub-block does not exist at slice-026's own prerequisite check and cannot self-gate that build. slice-026's self-application is discharged by `/critique-review` run on slice-026 + the audit run against slice-026's own folder at Step 6. Every slice after 026 inherits a self-gating CRP-1.

### Branch state

Per **BRANCH-2** (`methodology-changelog.md` v0.68.0; [[ADR-063]]; partial-supersedes ADR-019 / BRANCH-1 sub-mode (a) build-time branch-create + extends sub-mode (c) audit-time refusal): worktree-per-slice + branch workflow runs at /build-slice as a structural prerequisite (NOT a new Step — slice-021 follows slice-017 TPHD-1 sub-mode (c) precedent of placing prerequisite-class disciplines under `## Prerequisite check` rather than creating a numbered Step 0). The slice's own commits live in a **filesystem-isolated worktree** at the canonical sibling-dir path `<main-parent>/<main-name>-wt/slice-NNN-<slice-name>` on a dedicated `slice/NNN-<slice-name>` branch; `/commit-slice --merge` integrates back + tears the worktree down at slice end (BRANCH-1's `git checkout -b` on the main tree is superseded — closes R-17 / uncommitted-slice-A-WIP-contaminates-slice-B class structurally).

Per **BRANCH-3** ([[ADR-090]]; `methodology-changelog.md` v0.81.0; partial-supersedes ADR-063's *timing*, NOT its path convention): the worktree is now created at `/slice` **pick-time** (`skills/slice/SKILL.md` Step 5.5), not here — so by `/build-slice` it almost always **already exists** (its scaffold + design + critique were written into it on the default branch's behalf, leaving the default tree clean). The numbered points below are therefore reordered so **detect-an-existing-worktree (point 1) is the primary path**; `/build-slice` creates a worktree only when none exists (legacy pre-BRANCH-3 slice, or a pick-time `WORKTREE=skip`). The canonical path + branch are computed from the shared `tools/_worktree_paths.py` helper — the SAME source `/slice` Step 5.5 and `branch_workflow_audit.py` use (slice-099 AC5, single source of truth on the primary create path).

Resolve the repo's default branch at runtime (unchanged from BRANCH-1 per /critique M1 ACCEPTED-PENDING — canonical N=3-surface pin inherited by BRANCH-2; replaces hard-coded `master`/`main` for cross-project portability):

```bash
# Primary resolution
default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
# Fallback if no origin remote
[ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
# STOP if neither resolves
```

Then apply the worktree logic (BRANCH-2 timing superseded by BRANCH-3 — see the reordered points). First compute the shared paths **once**, in this pre-amble above the numbered list — `$wt_base` locates an existing worktree (point 1, primary) and anchors the legacy dirty-tree dance (point 4); both reference `$repo_root` / `$wt_base` without ever executing the create path's (point 2) body, so these assignments MUST live here, NOT inside any single numbered point's codefence (slice-074 M1 / P1.1):

```bash
repo_root="$(git rev-parse --show-toplevel)"
wt_base="$(dirname "$repo_root")/$(basename "$repo_root")-wt"
```

1. **If the worktree already exists** at `<wt_base>/slice-NNN-<slice-name>` — the **BRANCH-3 normal case** (created at `/slice` pick-time per [[ADR-090]]; also the resume-after-session-death path): `cd` into it and verify the branch matches the slice:
   ```bash
   cd "$wt_base/slice-NNN-<slice-name>"
   git branch --show-current   # must match slice/NNN-<slice-name>
   ```
   (No derived-dir seed exists post-slice-105 / [[ADR-094]] — `diagnose-out/`/`graphify-out/` are no longer copied into worktrees on any path; a skill that needs the code graph regenerates it with `$PY -m graphify code .`.) The worktree's filesystem is physically isolated from the main tree; uncommitted slice-A WIP on the main tree cannot contaminate slice-B's worktree.
2. **If no worktree exists** (legacy pre-BRANCH-3 slice, a pick-time `WORKTREE=skip`, or HEAD == resolved default with a clean tree): create it now — the BRANCH-2 create path. Compute the path + branch from the shared `_worktree_paths` helper — the SAME source `/slice` Step 5.5 + `branch_workflow_audit` use, so the three surfaces cannot drift (AC5, primary create path):
   ```bash
   # path + branch from the ONE shared source (no duplicated convention):
   $PY -m tools._worktree_paths --slice-folder slice-NNN-<slice-name> --repo-root "$repo_root"
   # → line 1 = <wt_path>;  line 2 = slice/NNN-<slice-name>
   git worktree add <wt_path> -b slice/NNN-<slice-name> "$default"
   cd <wt_path>
   ```
   (POSIX shell; on Windows invoke via Git for Windows' bundled MSYS bash — same dependency convention as commit-slice Step 5b/5d.)

   Slice-071 M2 + m4 FIXes (per slice-066 code-Critic M2/m4): the canonical path is derived from `git rev-parse --show-toplevel` (the `.git`-ancestor walk) rather than `$(pwd)` (cwd-derived) — `_worktree_paths.canonical_worktree_path` and the audit at `tools/branch_workflow_audit.py:_resolve_expected_worktree_path` agree on the same canonical path via the same mechanism, so running `/build-slice` from a subdirectory (e.g., `cwd=<vault>/slices/`) no longer surfaces a `worktree-path-shape-violation`.

   The worktree's filesystem is physically isolated from the main tree; uncommitted slice-A WIP on the main tree cannot contaminate slice-B's worktree.
3. **If on any other branch** (including stale `slice/<other-number>-*` from prior conflict OR a worktree for a different slice): STOP, ask user to switch context or document `WORKTREE=skip` escape-hatch in `build-log.md` Events per Step 7c canonical shape.
4. **If working tree is dirty** in the main tree (`git status --porcelain` non-empty before `worktree add`) — **legacy-only**: under BRANCH-3 this never fires for a picked slice (whose default tree is clean — `/slice` wrote the scaffold into the worktree and committed only `slice-queue.md`). It remains for legacy pre-BRANCH-3 dirty-default scaffolding (mission-brief.md + design.md + critique.md + critique-review.md + milestone.md + regenerated slice-queue.md written on the default branch). Apply the canonical switch-commit-switch-worktree sequence below; NO auto-stash (the codified sequence requires explicit `git add` + `git commit` of the scaffolding, never silent shelve via `git stash`):
   ```bash
   # Canonical switch-commit-switch-worktree sequence for dirty pre-build state on default
   # (N=5 cumulative slice-070/071/072/073/074; canonical origin: slice-070 reflection L127;
   # legacy post-vault-in-git scaffolding-by-design class — superseded by BRANCH-3 pick-time create)
   git switch -c slice/NNN-<slice-name>          # carry dirty state to slice branch
   git add architecture/slices/slice-NNN-<slice-name>/ architecture/slice-queue.md   # explicit staging — no auto-stash (concrete scaffolding pathspec, slice-074 m1)
   git commit -m "scaffold(slice-NNN): mission-brief + design + critique + ..."  # scaffolding commit on slice branch
   git switch "$default"                           # back to clean default
   git worktree add "$wt_base/slice-NNN-<slice-name>" slice/NNN-<slice-name>   # no -b; branch exists
   cd "$wt_base/slice-NNN-<slice-name>"
   ```
   This sequence is **NOT idempotent by design** — re-running after a session death mid-scaffolding-commit fails LOUDLY at `git switch -c slice/NNN-<slice-name>` (`fatal: A branch named 'slice/NNN-<slice-name>' already exists`); recovery is via point 1 ("If the worktree already exists"), NOT silent state re-creation. **`-b` is OMITTED at `git worktree add`** because the branch was created at step 1 of this sequence; including `-b` would cause `fatal: A branch named '...' already exists`. Contrast with point 2's new-branch-at-worktree-create form `git worktree add <wt_path> -b slice/NNN-<slice-name> "$default"`. If you cannot or do not wish to apply this sequence (e.g., the dirty state is unrelated to slice scaffolding and you want to STOP for manual resolution), document `WORKTREE=skip` escape-hatch in `build-log.md` Events per Step 7c canonical shape.

The canonical `WORKTREE=skip` escape-hatch line shape (Step 7c-pinned per BRANCH-2; mirrors `BRANCH=skip`'s shape from BRANCH-1): `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>`. The `tools/branch_workflow_audit.py` (BRANCH-2 audit) at Step 6 pre-finish refuses anything else. **`BRANCH=skip` is preserved as a parallel legacy escape-hatch** (per ADR-063 §Scope of supersession "Carried forward unchanged" 4th-surface inheritance) — both grammars coexist; `BRANCH=skip` for legacy single-tree-only escapes, `WORKTREE=skip` for the worktree-discipline-skip case + slice-066 bootstrap.

## Your task

### Step 1: Load full slice context

State briefly to the user:
- "Slice NNN: <name>"
- "Acceptance criteria: <count>"
- "Must-not-defer items: <count>"
- "Critic blockers addressed: yes / pending"

### Step 2: Enter plan mode

Use ExitPlanMode tooling appropriately. In plan mode:

- **Graphify first** for structural understanding:
  - `$PY -m graphify reachable --from=<module>` — what this module touches transitively
  - `$PY -m graphify blast-radius --from=<module>` — what touches it (reverse reachability)
  - Inline shortest-path (CLI lacks `path`):
    ```bash
    $PY -c "
    import json, networkx as nx
    G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
    try: print(' -> '.join(nx.shortest_path(G, '<target>', '<adjacent>')))
    except Exception as e: print(f'no path: {e}')
    "
    ```
    If path is short, you're near a god node and must design carefully.
  - The PreToolUse hook (installed by `/triage` / `/adopt`) injects a static hint pointing Claude at `GRAPH_REPORT.md` before Glob/Grep — it doesn't redirect those tools, just nudges.
- Then Read specific code files for detail (much less scanning needed after graph queries)
- Build dependency understanding for this slice's surface area
- Identify integration points with existing code
- Draft a concrete task sequence: files to create, files to modify, in what order

The plan should be:
- Grounded in the code you've actually read (not what design.md assumes)
- Specific (file paths, function names)
- Ordered so the mid-slice smoke gate is reachable at ~50% of work
- Sized so each task is independently verifiable

### Step 3: User approval

Present the plan to the user. Wait for approval or revisions.

> **PCA-1 gate-halt (v0.41.0)**: plan-mode approval is an enumerated user-input gate. DO NOT auto-advance into Step 4 execution — present the plan and HALT for explicit user sign-off, even when the pipeline is otherwise auto-advancing.

If user requests changes: revise the plan, re-present.

If the plan reveals the design is wrong: STOP. Tell the user: "Design says X. Code reality requires Y. Stop and revise design, or proceed with a deviation?"

### Step 4: Execute task-by-task with per-task verification

For each task in the plan:

1. Implement the task
2. Run the relevant acceptance criterion check (or smoke test if AC isn't testable yet)
3. If passes: mark complete, move on
4. If fails: fix, then verify again
5. If still fails after reasonable attempts: stop, ask for help (don't accumulate broken state)

### Step 5: Mid-slice smoke gate (at ~50%)

When ~50% of plan is done, run the mid-slice smoke gate from mission brief on a real environment:

- Backend: hit the endpoint with curl or test client; check DB
- Frontend: open the page in a real browser
- Mobile: install on a real device
- ML: run inference on a real sample

If smoke fails: STOP. Diagnose. Don't continue building on a broken base. Often the right move is to revise the plan.

> **PCA-1 gate-halt (v0.41.0)**: a mid-slice smoke-gate failure is an enumerated user-input gate. DO NOT auto-advance — STOP, surface the failure + diagnosis to the user, and HALT. Auto-advance on a broken base is forbidden.

### Step 6: Pre-finish gate

Before declaring slice done, ALL of these must be true:

- [ ] All acceptance criteria PASS with evidence
- [ ] All must-not-defer items addressed (no TODO, no stub, no silent except)
- [ ] `/drift-check` passes (vault and code aligned) — run in **full mode**, which appends the slice's `**Trigger**:` entry to `<vault>/drift-log.md` (the marker the DCE-1 gate verifies)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints / console.logs
- [ ] **Mock-budget lint passes (LINT-MOCK-1)** — see "Mock-budget lint" below
- [ ] **Wiring matrix audit passes (WIRE-1)** — see "Wiring matrix audit" below
- [ ] **Build-checks audit passes (BC-1)** — see "Build-checks audit" below
- [ ] **Test-first audit passes (TF-1)** — see "Test-first audit" below (only when `**Test-first**: true`)
- [ ] **Branch workflow audit passes (BRANCH-1)** — see "Branch workflow audit" below
- [ ] **UTF-8 stdout audit passes (UTF8-STDOUT-1)** — see "UTF-8 stdout audit" below
- [ ] **Critique-review prerequisite audit passes (CRP-1)** — see "Critique-review prerequisite audit" below
- [ ] **Pipeline-chain audit passes (PCA-1)** — see "Pipeline-chain audit" below
- [ ] **Build-checks integrity audit passes (BCI-1)** — see "Build-checks integrity audit" below
- [ ] **Methodology-changelog forward-sync audit passes (MCFS-1)** — see "Methodology-changelog forward-sync audit" below
- [ ] **State-transition stale-pin audit passes (STP-1)** — see "State-transition stale-pin audit" below
- [ ] **ai-sdlc-VERSION forward-sync audit passes (AVFS-1)** — see "ai-sdlc-VERSION forward-sync audit" below
- [ ] **ai-sdlc-tools version forward-sync audit passes (TVFS-1)** — see "ai-sdlc-tools version forward-sync audit" below
- [ ] **New-agent session-restart warning (NAW-1)** — see "New-agent warning audit" below
- [ ] **Drift-check enforcement audit passes (DCE-1)** — see "Drift-check enforcement audit" below
- [ ] **Skill-vault-write-safety audit passes (SVW-1)** — see "Skill-vault-write-safety audit" below

If any gate fails: don't declare done. Fix or escalate.

#### Skill-vault-write-safety audit (SVW-1)

Per **SVW-1** (`methodology-changelog.md` v0.79.0; slice-095; [[ADR-087]]; mints a new rule; supersedes nothing): the skill-driven counterpart of slice-094's VWS-1 (which AST-audits `tools/*.py` Python vault-writers). Every `skills/*/SKILL.md` directive that mutates a **shared-aggregate** vault file (`risk-register.md` / `lessons-learned.md` / `_index.md` / `methodology-changelog.md` / `shippability.md` / `build-checks.md`) MUST route through the `vault_edit append` safe channel (R-32 lock + `O_APPEND`) OR carry a sanctioned `<!-- vault-write-safe: <reason> -->` exemption (reason ∈ `{deferred-rmw, project-open-single-shot}`). Run:

```bash
$PY -m tools.skill_vault_write_safety_audit
```

Refusal semantics: exit **1** (≥1 unrouted-and-unexempted mutation site, OR an unknown exemption reason — names `skills/<x>/SKILL.md:line`) / **2** (usage — `skills/` missing/unreadable). **Honest scope (B1 / [[ADR-029]])**: SVW-1 guarantees the PROSE prescribes the safe channel — it is NOT a completeness guarantee over runtime writes (no content-oracle exists for LLM-authored appends, so a BCI-1-style downstream gate is unconstructible; the R-2 runtime-obedience axis is structurally unreachable by a static audit). The exempt-site allowlist `_REGISTERED_SKILL_EXEMPTIONS` is pinned by `tests/methodology/test_skill_vault_write_safety_audit.py::test_exemption_allowlist_pinned` (a NEW off-allowlist exemption trips a regression — closes the per-line `# noqa` silent-bypass class M3). SVW-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / AVFS-1 / TVFS-1 / NAW-1 / DCE-1) — its programmatic gate is `tools/skill_vault_write_safety_audit.py`.

Bootstrap (slice-095 only): slice-095 authors SVW-1; at slice-095's own Step 6 the audit runs against the routed worktree and MUST exit 0 (self-application discharge — the 10 append sites routed through `vault_edit append` + 12 RMW/project-open sites exempt-marked). Every slice after 095 inherits a self-gating SVW-1.

#### Drift-check enforcement audit (DCE-1)

Per **DCE-1** (`methodology-changelog.md` v0.76.0; slice-081; [[ADR-073]]; mints a new rule; supersedes nothing): `/drift-check` was the only pipeline discipline preached (CLAUDE.md "Run /drift-check before commit") and listed in this checklist yet enforced by nothing — no `tools/drift_check_audit.py`, no installed pre-commit hook, only the honor-system checkbox above (the R-7 / slice-022 silent-disable failure class). DCE-1 converts the drift-check checkbox into an audit-enforced gate.

**Order is load-bearing**: run `/drift-check` **in full mode** FIRST (only full mode appends the `**Trigger**: slice-NNN pre-finish gate` entry to `<vault>/drift-log.md`; `--fast` writes stdout only and leaves NO marker), THEN run the audit:

```bash
$PY -m tools.drift_check_audit architecture/slices/slice-NNN-<name>
```

The audit is a procedural *was-it-marked* gate (ADR-073 § Scope honesty): it verifies a slice-referencing drift-log marker exists — NOT that the semantic comparison was performed (that stays Claude's irreducible judgement via the `/drift-check` skill). The match is **line-anchored** to lines beginning `**Trigger**:` AND slice-number-anchored (`slice[- ]?0*<N>\b`) — a cross-mention of the slice number in another entry's `**Scope**` / Notes / heading does NOT satisfy the gate (per /critique-review M-add-1, mirroring CRP-1's keyed-not-substring discipline per ADR-024).

Refusal semantics:
- `drift-check-not-run` (Important, exit 1): mode ∈ {STANDARD, HEAVY} AND no `**Trigger**:` line in `drift-log.md` references the slice number AND no canonical `drift-check-skip` milestone.md frontmatter key. A missing/empty `drift-log.md` is "no marker" → refuse (NOT usage-error).
- `escape-hatch-malformed` (Important, exit 1): `drift-check-skip:` key present but value ≠ `^skip — rationale: .+`.
- `usage-error` / `mode-unresolvable` (exit 2): slice folder / milestone.md missing, slice-folder name off-shape, or mode unresolvable from `<vault>/triage.md` frontmatter `mode:` → `CLAUDE.md` `**Mode**:` fallback. Fail-visible, never a false refuse.

Accept (exit 0): a slice-referencing `**Trigger**:` line present, OR canonical `drift-check-skip` value present, OR resolved mode == MINIMAL (drift-check is skipped-by-default in Minimal).

Escape-hatch: to deliberately skip drift-check for a slice, add `drift-check-skip: "skip — rationale: <text>"` to milestone.md frontmatter (Step 7b preserves it verbatim — see Step 7b). DCE-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / AVFS-1 / TVFS-1 / NAW-1) — its programmatic gate is `tools/drift_check_audit.py`.

Bootstrap (slice-081 only): slice-081 authors DCE-1. At slice-081's own Step 6 the build runs `/drift-check` full mode (writing a `**Trigger**: slice-081 pre-finish gate` line to `<vault>/drift-log.md`) BEFORE the audit, which must then exit 0 (self-application discharge). A non-zero before that drift-check run is the EXPECTED signal to run `/drift-check` first — NOT a slice defect; re-run until exit 0. Every slice after 081 inherits a self-gating DCE-1. (Same bootstrap shape as CRP-1 slice-026 / PCA-1 slice-027 / NAW-1 slice-063.)

#### Branch workflow audit (BRANCH-1)

Per **BRANCH-1** (`methodology-changelog.md` v0.35.0 sub-mode (c)): the slice's commits MUST live on a `slice/NNN-<slice-name>` branch matching the active slice (created at the `## Prerequisite check ### Branch state` sub-section above). Run:

```bash
$PY -m tools.branch_workflow_audit architecture/slices/slice-NNN-<name>
```

Refusal semantics:
- `on-default-branch`: current branch is the resolved default branch AND no canonical `BRANCH=skip` escape-hatch line in `build-log.md` Events.
- `slice-branch-mismatch`: current branch is `slice/<wrong-number>-<wrong-name>` (doesn't match active slice).
- `escape-hatch-malformed`: a `BRANCH=skip` line is present but doesn't conform to the canonical regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+` (HH:MM + `rationale:` token required per Step 7c canonical shape).
- `default-branch-unresolvable`: neither `git symbolic-ref refs/remotes/origin/HEAD` nor `git config init.defaultBranch` resolves (exit 2 usage error).
- `stale-slice-branch`: lingering `slice/*` branches detected from prior `--merge` conflict-recovery (warning class — surfaces but doesn't refuse).

Default-branch resolution mirrors the `## Prerequisite check ### Branch state` sub-section logic.

#### UTF-8 stdout audit (UTF8-STDOUT-1)

Per **UTF8-STDOUT-1** (`methodology-changelog.md` v0.37.0): every `tools/*.py` module exposing `def main(argv: list[str] | None = None) -> int:` MUST call `_stdout.reconfigure_stdout_utf8()` (from the canonical helper at `tools/_stdout.py`) as the first executable statement of `main()`. This retires the recurring Windows cp1252 console encoding class (N=6 cumulative recurrence across slices 007 / 016 / 018 / 020 / 021 / 022).

Run:

```bash
$PY -m tools.utf8_stdout_audit
```

Refusal semantics:
- Any audit tool's `main()` whose first executable statement is not `_stdout.reconfigure_stdout_utf8()` → exit 1 + violation.
- Any audit tool missing the canonical import `from tools import _stdout` → exit 1 + violation.
- `tools/` directory missing at resolved root → exit 2 + stderr.
- SyntaxError parsing any `tools/*.py` → exit 2 + stderr.

Exclusion list: `__init__.py` + leading-underscore helpers (e.g., `tools/_stdout.py`) — neither has `main()`; both are out of scope by structural convention. The PMI-1 audit's `_list_actual_tools` filter mirrors this exclusion to prevent `orphan-tool` false positives.

Self-application: `tools/utf8_stdout_audit.py` itself conforms; the audit run on the post-slice-027 codebase returns `tools_scanned: 20, tools_with_main: 20, tools_clean: 20` (slice-027 added `tools/pipeline_chain_audit.py`, which conforms — `_stdout.reconfigure_stdout_utf8()` is the first statement of its `main()`).

#### Critique-review prerequisite audit (CRP-1)

Per **CRP-1** (`methodology-changelog.md` v0.40.0): the same audit invoked at the `## Prerequisite check` (above) is re-run at Step 6 pre-finish as a defense-in-depth layer — it catches `critique-review.md` deleted mid-build, or `critic-required` flipped `true` during a `/design-slice` scope expansion that post-dated the prerequisite check. It is idempotent and reads the Step-7b-preserved `critique-review-skip:` milestone.md frontmatter key (per ADR-024 the escape-hatch is a frontmatter key precisely so it survives Step 7b's continuous milestone.md rewrite). Run:

```bash
$PY -m tools.critique_review_prerequisite_audit architecture/slices/slice-NNN-<name>
```

Refusal semantics: `mandatory-critique-review-absent` (Important, exit 1) — mode ∈ {STANDARD, HEAVY} AND `critic-required: true` AND `critique-review.md` absent AND no canonical `critique-review-skip` key; `escape-hatch-malformed` (Important, exit 1) — key present, value off-canonical; `usage-error` / `mode-unresolvable` (exit 2). CRP-1 is an **audit-enforced gate** (NON-`-D` per ADR-019; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1) — its programmatic gate is `tools/critique_review_prerequisite_audit.py`.

Bootstrap (slice-026 only, per ADR-024): slice-026 authors CRP-1; at slice-026's Step 6 the audit IS run against slice-026's own folder and MUST exit 0 (self-application discharge — `/critique-review` having been run on slice-026).

#### Pipeline-chain audit (PCA-1)

Per **PCA-1** (`methodology-changelog.md` v0.41.0): every covered pipeline skill MUST carry a well-formed `## Pipeline position` block whose declared successor edge matches the canonical per-slice loop, and the terminal boundary (`reflect` + `commit-slice`) MUST be `auto-advance: false` so `/commit-slice` is never auto-invoked. Run:

```bash
$PY -m tools.pipeline_chain_audit
```

Refusal semantics:
- `malformed-block` (Important, exit 1): a covered skill's `## Pipeline position` section is absent or a required field (`predecessor`/`successor`/`auto-advance`/`on-clean-completion`/`user-input gates`) is missing/unparseable.
- `successor-mismatch` (Important, exit 1): a declared `successor:` ≠ the canonical chain successor.
- `auto-advance-mismatch` (Important, exit 1): a declared `auto-advance:` ≠ canonical — including the terminal guarantee that `reflect` and `commit-slice` are `false`.
- `usage-error` (exit 2): repo root unresolvable, `skills/` dir or a covered SKILL.md missing.

PCA-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1) — its programmatic gate is `tools/pipeline_chain_audit.py`. The audit reads the flat `successor:` field for chain-shape only; the documented `/critique` post-TRI-1 → `/build-slice` hop and `/critique`→`/critique` BLOCKED self-loop live in `on-clean-completion` prose and are NOT flagged (per slice-027 /critique-review m-add-1).

Bootstrap (slice-027 only, per [[ADR-025]]): slice-027 authors PCA-1; the `## Pipeline position` directive does not exist on disk during slice-027's own loop (the chain ran manually per the user's at-invocation directive). At slice-027's Step 6 the audit IS run against the repo and MUST exit 0 (self-application discharge — `/critique-review` having been run on slice-027). Every slice after 027 inherits a self-gating PCA-1.

#### Build-checks integrity audit (BCI-1)

Per **BCI-1** (`methodology-changelog.md` v0.44.0; slice-030A; [[ADR-028]] + [[ADR-029]]): `/reflect` Step 5b promotion is LLM-executed prose with no deterministic source (R-4 witnessed both `<vault>/build-checks.md` + `~/.claude/build-checks.md` silently truncated to the last-promoted rule). The only sound control for a non-deterministic step is a deterministic downstream gate. BCI-1 asserts the live build-checks files match the **git-tracked** canonical fixtures (`tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md`) on **full per-rule structural identity** — `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check` — NOT rule-ID-set-only (slice-030A meta-M-add-2: an ID-only check passes a coverage-degraded file, re-opening R-4). Run:

```bash
$PY -m tools.build_checks_integrity
```

Refusal semantics:
- `drift` (exit 1, HALT): a present live file diverges from the canonical fixture — missing/extra rules, **empty present file**, or any structural-field mismatch — OR the project `<vault>/build-checks.md` is absent. Message is attributed: *"LOCAL VAULT DRIFT — reconstruct from <fixture>; this is NOT a slice regression"* (retires the R-4 anti-pattern where a truncation read as a confusing slice regression).
- `warn` (exit 0): `~/.claude/build-checks.md` **absent** (file does not exist) — the global file is untracked/environment-dependent; a machine that hasn't installed it must not HALT (slice-030A meta-M3). An *empty present* global file is `drift`/HALT, not WARN (empty != absent — R-4-global not silently reopened).
- `usage` (exit 2): a canonical fixture (the tracked oracle) is missing/unreadable, emits its own parse violations, or repo root is unresolvable.

BCI-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1) — its programmatic gate is `tools/build_checks_integrity.py`, wired non-opt-out here AND as a `/reflect` Step 5b fail-loud post-write instruction. (The shippability-catalog-row wiring is deferred to slice-030B per the user-approved split; 030A's two wiring points fully retire R-4's substance.)

Bootstrap (slice-030A only): slice-030A authors BCI-1; at slice-030A's Step 6 the audit IS run against the repo and MUST exit 0 (self-application discharge — the live files were just reconstructed from the canonical fixtures). Every slice after 030A inherits a self-gating BCI-1.

#### Methodology-changelog forward-sync audit (MCFS-1)

Per **MCFS-1** (`methodology-changelog.md` v0.53.0; slice-041, split-lineage label "030C"; [[ADR-042]] + [[ADR-043]]): the PMI-1 4-part forward-sync that produces `~/.claude/methodology-changelog.md` is LLM-executed prose with no deterministic source — slice-041 re-homed the ~33 per-version `test_v_0_NN_0_*` essential reads that half-asserted it onto ONE deterministic whole-file gate (the slice-030A/BCI-1 sound-control-for-a-non-deterministic-step rationale). MCFS-1 asserts in-repo `methodology-changelog.md` is content-equal **modulo line endings** (EOL-DRIFT-1 / [[ADR-033]]) to the installed copy. Run:

```bash
$PY -m tools.methodology_changelog_forward_sync
```

Refusal semantics:
- `drift` (exit 1, HALT): installed file present but content-divergent after CRLF→LF (incl. empty-present — empty ≠ absent). Message is attributed: *"METHODOLOGY-CHANGELOG FORWARD-SYNC DRIFT — re-run the PMI-1 forward-sync (in-repo → ~/.claude/); this is NOT a slice regression"*.
- `warn` (exit 0): installed `~/.claude/methodology-changelog.md` **absent** — untracked/environment-dependent; a machine that hasn't installed the plugin must not HALT (slice-030A meta-M3 parity).
- `usage` (exit 2): in-repo `methodology-changelog.md` missing/unreadable, or repo root unresolvable.

MCFS-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1) — its programmatic gate is `tools/methodology_changelog_forward_sync.py`. It is **non-opt-out and UNGATED** here: this Step 6 checklist item runs **every slice regardless of whether a build-checks rule was promoted** (distinct from `/reflect`'s rule-promotion-gated Step 5b — folding MCFS-1 into a rule-promotion gate would silently disable it on a version-bumping-but-no-rule-promoted slice, the R-7/slice-022 silent-disable class; m1 / DR-1). The complementary `/reflect` wiring is its OWN dedicated Step 5b-fs (also ungated), NOT part of Step 5b.

Bootstrap (slice-041 only): slice-041 authors MCFS-1; at slice-041's Step 6 the audit IS run against the repo and MUST exit 0 (self-application discharge — the v0.53.0 entry was just forward-synced). Every slice after 041 inherits a self-gating MCFS-1.

#### State-transition stale-pin audit (STP-1)

Per **STP-1** (`methodology-changelog.md` v0.54.0; slice-044; [[ADR-047]]): a slice that performs a *state transition* but leaves a pre-existing test pinning the OLD value is caught historically only at the pre-finish full-suite (BC-PROJ-4) run, sometimes latent for several slices (R-10 slice-038→040 ~5-slice latency; slice-041 R-4 stale `test_r_4_..._stays_mitigating`; slice-042 ADR-prose recurrence). STP-1 converts this from caught-by-luck to a loud, attributed gate. Run:

```bash
$PY -m tools.state_transition_pin_audit
```

Two mechanically-detectable sub-forms (the fuzzy ADR `accepted`→`superseded` sub-form is out of scope per ADR-047):
- **Sub-form A — SKILL.md-prose-repoint stale pin** (git-diff-independent standing invariant): a `tests/**/test_*skill*.py` positive-membership prose-pin whose folded-constant literal is absent from the *full* target `SKILL.md`. `not in` pins, `ast.Or`-disjunction operands, and mixed `ast.And`-with-`NotIn`/non-constant-sibling are excluded; a positive-only `ast.And` chain is checked per-operand.
- **Sub-form B — risk-status-stale pin** (git-diff-independent standing invariant): a test `FunctionDef` name matching `(?:^|_)r[_-]?(\d+).*?_(stays|remains|is)_(open|mitigating|retired|accepted)(?:_|$)` whose claimed status differs from the live `<vault>/risk-register.md` `**Status**:` (parsed via the object-identity-reused `risk_register_audit._parse_risks`).

Refusal semantics:
- `stale-skill-prose-pin` (Important, exit 1): Sub-form A — names `tests/<file>::<fn>` + the missing folded literal + target SKILL.md + remediation.
- `stale-risk-status-pin` (Important, exit 1): Sub-form B — names the risk ID + `claimed → live` + the stale `tests/<file>::<fn>` + remediation.
- Per-scanned-file AST `SyntaxError` → **skip-with-visible-note, NO violation, NOT exit 2** (ADR-037/PTFFD-1 discipline, inherited from the `shippability_path_audit.py`/`_pyfn` precedent — a false-FAIL on a parse failure is the strictly-worse audit failure mode; e.g. the permanent `tests/methodology/fixtures/syntax_error.py`).
- `usage-error` (Important, exit 2): hard-input failure ONLY — `<vault>/risk-register.md` missing/unreadable/unparseable, `tests/`/`skills/` dir missing, or repo-root unresolvable. Fail-closed, never silent exit 0.

STP-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1) — its programmatic gate is `tools/state_transition_pin_audit.py`. It is **git-independent** (Sub-form B revised from a git-merge-base mechanism by the slice-044 plan-mode deviation — `<vault>/` is gitignored).

Bootstrap (slice-044 only): slice-044 authors STP-1; at slice-044's Step 6 the audit IS run against the repo and MUST exit 0 (self-application discharge — no live test contradicts the register, no removed-anchor prose-pin, the lone unparseable fixture is skip-noted). Every slice after 044 inherits a self-gating STP-1.

#### ai-sdlc-VERSION forward-sync audit (AVFS-1)

Per **AVFS-1** (`methodology-changelog.md` v0.58.0; slice-050; [[ADR-052]]; extends the slice-041/MCFS-1 forward-sync-via-deterministic-downstream-gate lineage): the PMI-1 4-part atomic version bump has a 4th leg — installed `~/.claude/ai-sdlc-VERSION` — that PMI-1 never reads (it audits in-repo `VERSION`==`plugin.yaml` only) and MCFS-1 does not cover (it guards the changelog leg). That leg drifted silently N=2 (slice-035 DEVIATION-2; slice-048→049). AVFS-1 is a standalone verbatim MCFS-1 clone asserting in-repo `VERSION` is content-equal **modulo line endings** (CRLF→LF only — EOL-DRIFT-1 / [[ADR-033]]) to installed `~/.claude/ai-sdlc-VERSION`. Run:

```bash
$PY -m tools.ai_sdlc_version_forward_sync
```

Refusal semantics:
- `drift` (exit 1, HALT): installed file present but content-divergent after CRLF→LF (incl. empty-present AND whitespace-only-present — empty ≠ absent). Message is attributed: *"AI-SDLC-VERSION FORWARD-SYNC DRIFT — re-run the PMI-1 4-part forward-sync (in-repo VERSION → ~/.claude/ai-sdlc-VERSION); this is NOT a slice regression"*.
- `warn` (exit 0): installed `~/.claude/ai-sdlc-VERSION` **absent** — untracked/environment-dependent; a machine that hasn't installed the plugin must not HALT (slice-030A meta-M3 parity).
- `usage` (exit 2): in-repo `VERSION` missing/unreadable, or repo root unresolvable.

AVFS-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1) — its programmatic gate is `tools/ai_sdlc_version_forward_sync.py`. It is **non-opt-out and UNGATED** here: this Step 6 checklist item runs **every slice regardless of whether a build-checks rule was promoted** (distinct from `/reflect`'s rule-promotion-gated Step 5b — folding AVFS-1 into a rule-promotion gate would silently disable it on a version-bumping-but-no-rule-promoted slice, the R-7/slice-022 silent-disable class). The complementary `/reflect` wiring is its OWN dedicated Step 5b-avfs (also ungated), NOT part of Step 5b.

Bootstrap (slice-050 only): slice-050 authors AVFS-1. The bootstrap is **conditional and weaker than MCFS-1's** (M1): at slice-050's own Step 6 in-repo `VERSION` is `0.58.0`, so AVFS-1 exits 0 ONLY IF this slice's own 4-part PMI-1 bump correctly forward-synced installed `~/.claude/ai-sdlc-VERSION` → `0.58.0` — and that leg is precisely the N=2-drift-prone manual step AVFS-1 exists to gate. A **non-zero AVFS-1 at slice-050's own Step 6 is the EXPECTED signal to perform/repair the installed-VERSION forward-sync — NOT a slice defect**; re-run until exit 0. Every slice after 050 inherits a self-gating AVFS-1 (which from slice-051 behaves exactly like MCFS-1's bootstrap, the bump leg then a routine part of any version-bumping slice).

#### ai-sdlc-tools version forward-sync audit (TVFS-1)

Per **TVFS-1** (`methodology-changelog.md` v0.63.0; slice-059; [[ADR-058]]; extends the slice-050/AVFS-1 + slice-041/MCFS-1 forward-sync-via-deterministic-downstream-gate lineage): the PMI-1 version bump's installed **`ai-sdlc-tools` pip-distribution** leg has no gate — PVFS-1 keeps `pyproject.toml` correct so the *next* `pip install` builds a correct wheel, but nothing forces the *re-install* (the venv package drifted silently to `0.20.0` while the source advanced to `0.62.0`). TVFS-1 asserts the version of the `ai-sdlc-tools` distribution installed in the running interpreter's venv site-packages equals trimmed in-repo `VERSION`. The read is scoped to `sysconfig.get_path("purelib")` — the naive `importlib.metadata.version()` is shadowed by the in-repo `ai_sdlc_tools.egg-info/` build artifact (B1). Run:

```bash
$PY -m tools.ai_sdlc_tools_version_forward_sync
```

Refusal semantics:
- `drift` (exit 1, HALT): installed `ai-sdlc-tools` version ≠ in-repo `VERSION`. Message is attributed: *"AI-SDLC-TOOLS VERSION DRIFT — re-run INSTALL.md Step 3g (`$PY -m pip install --upgrade <source>`); this is NOT a slice regression"*.
- `warn` (exit 0): `ai-sdlc-tools` not installed in the running interpreter's venv site-packages — untracked/environment-dependent; a machine that hasn't installed the plugin must not HALT. The WARN message names `sys.executable` + `purelib` (M3 — TVFS-1's WARN is weaker than AVFS-1's: "not in this interpreter's site-packages" can co-exist with a stale install reachable another way).
- `usage` (exit 2): in-repo `VERSION` missing/unreadable, repo root unresolvable, OR >1 `ai-sdlc-tools` distribution in site-packages (a stale duplicate `.dist-info` from an interrupted upgrade — distinct duplicate-distribution remediation message, M-add-2).

TVFS-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / AVFS-1) — its programmatic gate is `tools/ai_sdlc_tools_version_forward_sync.py`. It is **non-opt-out and UNGATED** here: this Step 6 checklist item runs **every slice regardless of whether a build-checks rule was promoted** (folding TVFS-1 into a rule-promotion gate would silently disable it on a version-bumping-but-no-rule-promoted slice, the R-7/slice-022 silent-disable class). The complementary `/reflect` wiring is its OWN dedicated Step 5b-tvfs (also ungated), NOT part of Step 5b.

Bootstrap (slice-059 only): slice-059 authors TVFS-1. The bootstrap is **conditional** (AVFS-1 precedent): slice-059's build sequence runs `$PY -m pip install --upgrade .` after the 4-part PMI-1 bump to refresh the installed `ai-sdlc-tools` → `0.63.0`. A **non-zero TVFS-1 at slice-059's own Step 6 before that re-install is the EXPECTED signal to perform the re-install — NOT a slice defect**; re-run until exit 0. Every slice after 059 inherits a self-gating TVFS-1 — any version-bumping slice must `$PY -m pip install --upgrade <source>` before Step 6 or TVFS-1 HALTs.

#### New-agent warning audit (NAW-1)

Per **NAW-1** (`methodology-changelog.md` v0.66.0; slice-063; [[ADR-061]]; mints a new rule; supersedes nothing): the first audit-enforced gate on the **discovery-gate** axis, adjacent to (but NOT extending) the forward-sync family (PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1). R-18 (slice-061-discovered; N=2 cumulative recurrence at slice-061 + slice-062): the Claude Code agent registry is loaded at session start; mid-session writes to `~/.claude/agents/*.md` are invisible to `Agent(subagent_type=…)` calls until the user restarts Claude Code. NAW-1 surfaces this failure mode methodology-discoverably at this Step 6 BEFORE the next slice's chain runs. Run:

```bash
$PY -m tools.new_agent_warning_audit
```

Refusal semantics (binary exit contract by construction — there is NO "drift" branch for a discovery gate, and NO exit 1):
- `clean` (exit 0, quiet stdout): no added `agents/*.md` files in the slice's diff (working-tree-vs-base + untracked-new + commits-vs-base union per [[ADR-061]] §Decision read mechanism). Quiet stdout in `--check` mode; structured `status: "clean"` in `--json`.
- `warn` (exit 0, stdout): ≥1 added `agents/*.md` files. WARN line(s) on stdout naming each new agent path + session-restart-before-next-slice instruction + R-18 cross-reference. A new-agent slice is NOT a slice regression; the WARN is informational, NEVER a HALT.
- `usage` (exit 2): repo root unresolvable, `git` binary unavailable on PATH, default-branch resolution returned `None` (no `main` literal fallback in BRANCH-1's `_resolve_default_branch` per the M3 critique fix), or any of the three `git` subprocess calls non-zero. Stderr-only error message per AVFS-1/TVFS-1 precedent.

NAW-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / AVFS-1 / TVFS-1) — its programmatic gate is `tools/new_agent_warning_audit.py`. It is **non-opt-out and UNGATED** here: this Step 6 checklist item runs **every slice regardless of whether a build-checks rule was promoted**. There is intentionally **NO `/reflect` Step 5b-naw counterpart** — NAW-1 is a discovery gate, NOT a forward-sync gate; it has no installed-side mutation to verify (distinct from AVFS-1/MCFS-1/TVFS-1's `/reflect` Step 5b-X parity).

**Overbroad-pathspec known false-positive class** (m2 critique fix): the `agents/*.md` pathspec matches ANY `.md` file added under `agents/` — not just files registered in `tools/install_audit.py` `_CANONICAL_AGENTS`. A future slice that adds a prose-doc under `agents/` (e.g., `agents/CONVENTIONS.md`) will trigger a NAW-1 WARN even though no registry cache-miss can result. Accepted as a known-false-positive class with minimal cost — an extra WARN never HALTs.

Bootstrap (slice-063 only): slice-063 authors NAW-1. The bootstrap is **conditional-clean** — the audit runs at slice-063's own Step 6 against slice-063's own working-tree + ls-files state; slice-063 adds zero `agents/*.md` (the slice ships a new `tools/*.py` audit + `skills/build-slice/SKILL.md` edit + `<vault>/risk-register.md` flip; zero `agents/*.md` deltas), so all three sources return `[]` → audit exits 0 quietly. Vacuous-pass IS the structural self-application discharge. Every slice after 063 inherits a self-gating NAW-1.

#### Test-first audit (TF-1)

Per **TF-1** (`methodology-changelog.md` v0.13.0), when this slice's `mission-brief.md` declares `**Test-first**: true`, every Acceptance criterion must map to one or more tests with a status field whose value at pre-finish is `PASSING`. Run:

```bash
$PY -m tools.test_first_audit architecture/slices/slice-NNN-<name> --strict-pre-finish
```

Refusal semantics:
- `missing-section`: brief declares test-first true but has no `## Test-first plan` section
- `format` / `missing-cells`: table is malformed (need 5 columns: AC | Test type | Test path | Test function | Status)
- `invalid-status`: status outside `{PENDING, WRITTEN-FAILING, PASSING}`
- `ac-without-row`: an AC declared in the brief body has no test-first row
- `non-passing-pre-finish`: any row's status is `PENDING` or `WRITTEN-FAILING` (only emitted with `--strict-pre-finish`)

Default-off semantics: when the brief lacks the `**Test-first**:` field or sets it to `false`, the audit returns clean and the gate passes silently. TF-1 is opt-in per slice; old briefs without the field continue to work.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates 2026-05-06 are exempt automatically.

#### Build-checks audit (BC-1)

Per **BC-1** (`methodology-changelog.md` v0.10.0), every slice's pre-finish runs the build-checks audit to surface evergreen rules promoted from past lessons-learned. The audit reads `<vault>/build-checks.md` (project-specific) and `~/.claude/build-checks.md` (global, cross-project), filters rules by applicability, and surfaces matches.

Per **BCSG-1** (`methodology-changelog.md` v0.75.0; slice-080; [[ADR-072]]; refines BC-1 in place, supersedes nothing), this gate is **mechanically enforced under `--strict`**: an applicable Critical rule that is NOT acknowledged via `--ack-critical` becomes an `unacknowledged-critical` violation → gate-failure exit 1. The enumerate-then-ack pattern (run EVERY slice — BC-PROJ-3 + BC-GLOBAL-2 are `always:true` Critical rules that apply to every slice):

1. Enumerate applicable Critical rules:
   ```bash
   $PY -m tools.build_checks_audit \
     --slice architecture/slices/slice-NNN-<name> \
     --changed-files <list of files changed by this slice> --json \
     | $PY -c "import sys,json; d=json.load(sys.stdin); print([r['rule_id'] for r in d['applicable'] if r['severity'].lower()=='critical'])"
   ```
2. Address each applicable Critical rule and attest it in `build-log.md` (e.g. "BC-PROJ-3/BC-GLOBAL-2: this slice performs no destructive `git checkout`/`restore`/`stash` revert of uncommitted work").
3. Re-run with `--strict` and the acknowledged rule IDs (place `--ack-critical` LAST — `nargs="*"` is greedy):
   ```bash
   $PY -m tools.build_checks_audit \
     --slice architecture/slices/slice-NNN-<name> \
     --changed-files <list of files changed by this slice> \
     --strict --ack-critical <addressed Critical rule IDs>
   ```
   Exit 0 = all applicable Critical rules acknowledged (or none apply). Exit 1 = ≥1 unacknowledged applicable Critical rule (the human-readable output names which, plus any `--ack-critical` ID that matched no applicable rule — a typo/stale-ack diagnostic).

Applicability is the OR of three signals:
- `Applies to: always: true` — always fires
- `Applies to: <globs>` — fires when any glob matches a changed file (e.g., `src/api/uploads/**`)
- `Trigger keywords: <words>` — fires when any keyword appears in mission-brief.md or design.md

Refusal semantics:
- **Critical rule applies**: this slice MUST address the rule before declaring done, then acknowledge it via `--ack-critical <rule-id>`. Under `--strict` an unacknowledged applicable Critical rule is a gate-failure (exit 1) — Critical rules are not deferrable, and the gate is now mechanical (BCSG-1), not honor-system. To escalate (rule is wrong / needs scope adjustment) rather than fix: document the escalation in build-log.md AND acknowledge the rule ID so the gate clears; the build-log attestation is the audit trail.
- **Important rule applies**: surface to user; defer-with-rationale is allowed and logged in build-log.md (matching the LINT-MOCK Important pattern). `--strict` never gates on Important rules.
- **Parse violations** (malformed `build-checks.md` rule, missing required field, invalid severity): fail the audit with exit code 1; fix the rule's format before continuing.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates BC-1's release date (2026-05-06) are exempt automatically. The audit returns `carry_over_exempt: true` and zero applicable rules for those.

If neither `<vault>/build-checks.md` nor `~/.claude/build-checks.md` exists, the audit returns zero applicable rules. Both files are populated manually at `/reflect` Step 5b when a recurring pattern emerges across slices.

BCSG-1 (slice-080) added exit-code enforcement: under `--strict` the exit code is a gate signal (acknowledgment-based), so an automated/CI consumer no longer gets a false-green on an applicable Critical rule. The acknowledgment is an attestation (the builder asserts the rule was addressed, recorded in build-log.md) — NOT machine proof the rule's required check actually ran. That executable per-rule auto-verification (parse + run each rule's `Validation hint`) remains the deferred BC-1 v2.

#### Wiring matrix audit (WIRE-1)

Per **WIRE-1** (`methodology-changelog.md` v0.9.0), this slice's `design.md` must include a wiring matrix declaring a consumer entry point + consumer test for every new module, or an exemption with explicit rationale. Run:

```bash
$PY -m tools.wiring_matrix_audit architecture/slices/slice-NNN-<name>
```

Refusal on Important findings:
- `no-matrix`: design.md is missing the `## Wiring matrix` heading entirely
- `missing-cells`: a row has neither (consumer entry point + consumer test) nor an exemption
- `missing-rationale`: exemption present but no `rationale:` substring
- `format`: malformed table (wrong column count, missing separator, etc.)

v1 enforces format validation only. A v2 will add existence/import audits — verify entry-point files exist and grep for module imports.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates WIRE-1's release date (2026-05-06) are exempt automatically. The audit returns zero findings for those.

If the slice introduces no new modules: keep the matrix header + separator only — the audit accepts zero-row matrices as clean.

#### Mock-budget lint (LINT-MOCK-1, LINT-MOCK-2, LINT-MOCK-3)

Per **LINT-MOCK-1** (Python; v0.6.0), **LINT-MOCK-2** (TypeScript / JavaScript; v0.7.0), and **LINT-MOCK-3** (Go; v0.8.0), Python, TS/JS, and Go test files changed in this slice must pass `tools/mock_budget_lint.py`. The linter dispatches by file extension automatically:

```bash
$PY -m tools.mock_budget_lint <changed-test-files>
# Add --seam-allowlist <vault>/.cross-chunk-seams (if file exists)
# Add --strict in Heavy mode (Important also blocks)
```

Supported extensions: `.py` (LINT-MOCK-1), `.ts` `.tsx` `.js` `.jsx` `.mts` `.cts` (LINT-MOCK-2), `.go` (LINT-MOCK-3).

Severity rules:
- **Critical** (target is in `<vault>/.cross-chunk-seams`): blocks pre-finish; cannot be deferred. *(Critical applies to LINT-MOCK-1 and LINT-MOCK-2 only; LINT-MOCK-3 v1 enforces mock-budget without internal-mock classification — no Critical findings emitted.)*
- **Important** in Standard / Minimal mode: surface to user; allow defer with rationale recorded in `build-log.md`
- **Important** in Heavy mode: blocks pre-finish (`--strict` is mandatory)

The `<vault>/.cross-chunk-seams` allowlist (if present) names targets where mocking is escalated to Critical. One target per line; lines starting with `#` are comments. The same allowlist applies to Python and TS files; format matches each language's import-target string (e.g., `src.api.receipts.upload_receipt` for Python, `./api/receipts` for TS). Go v1 doesn't yet honor the allowlist; a later slice adds import-aware boundary classification for Go.

If the slice didn't touch any Python, TS/JS, or Go test files: skip this gate (not applicable).

### Step 7: Do-not-defer enforcement

The mission brief's must-not-defer list is checked at pre-finish. Items there CANNOT be:

- Marked "TODO" and shipped
- Stubbed with placeholder values (`return None`, `// implement later`)
- Wrapped in silent try/except that hides failures
- Skipped via "we'll add this in the next slice"
- Committed with debug prints / console.logs

If you want to defer anything on the list: STOP and ask the user explicitly. Approved deferrals get logged in `build-log.md` with rationale.

### Step 7b: Update milestone.md continuously

Unlike other skills which update milestone.md at completion, `/build-slice` updates it **during execution** because build is the longest phase and most likely to be interrupted by session death.

Updates during build:

- At plan approval: `stage: build`, `next-action: task 1 (<specific>)`, "Current focus" = first task
- After EACH task completes: update "Progress" counter (`- [ ] /build-slice — in progress: N/M tasks complete`), update "Current work" and "Files being edited", update "Next immediate step"
- At mid-slice smoke gate: record pass/fail in "Current focus"
- At pre-finish gate: check the build-slice box, set `next-action: run /validate-slice`

**Preserve the CRP-1 + DCE-1 escape-hatch keys (per ADR-024 + ADR-073).** If `milestone.md` frontmatter carries a `critique-review-skip:` key (CRP-1) and/or a `drift-check-skip:` key (DCE-1), the continuous rewrite MUST preserve each verbatim. They are deliberate per-slice skip records the Step 6 defense-in-depth re-runs read (CRP-1 reads `critique-review-skip:`; DCE-1 reads `drift-check-skip:`); dropping either would false-refuse a legitimately escape-hatched build. Treat `critique-review-skip:` and `drift-check-skip:` like `critic-required:` / `risk-tier:` — frontmatter fields that survive every rewrite, never regenerated-from-template fields.

**Critical for session resume**: if session dies mid-build, `milestone.md` tells Claude (or the user) EXACTLY where to pick up: task number, files being edited, specific next step. Don't skimp on these fields.

### Step 7c: Append events to build-log.md (flight recorder)

`milestone.md` is the phase checkpoint ("where am I"). `build-log.md`'s `## Events` section is the append-only flight recorder ("what just happened"). They're complementary: milestone records phase transitions; events capture the finer-grained activity between transitions where tool failures and session deaths usually strike.

**Write a one-line event BEFORE any tool call that could fail and erase in-memory context.** Tool failures (corrupted binaries, parser errors, network drops) can wipe the conversation, but committed files persist.

**When to append**:
- **Before** any tool call that returns binary or large parseable output (screenshots, image reads, web fetches that may include images, large file reads). Record the *intent* and any *pending finding* first.
- **After** significant build/test commands complete (PASS / FAIL with brief evidence).
- **When you discover a finding** mid-build (UI bug, surprising behavior, edge case). Record the finding **before** doing anything else with it — including taking a screenshot.
- **On errors** you intend to investigate (preserves the cause if the investigation tool itself fails).

**Format**: `<YYYY-MM-DD HH:MM> <CATEGORY>: <one-line description>` where CATEGORY ∈ `BUILD`, `TEST`, `SMOKE`, `FINDING`, `ERROR`, `DEFERRAL`, `DEVIATION`.

**Examples**:

- `2026-05-03 14:25 BUILD: :app:assembleDebug PASS`
- `2026-05-03 14:30 SMOKE: mid-slice run on Pixel 7`
- `2026-05-03 14:32 FINDING: version footer half-hidden by nav bar — screenshot pending`
- `2026-05-03 14:33 ERROR: screenshot read failed (binary corruption); finding still valid via manual inspection`

**Canonical `BRANCH=skip` sub-shape** (per **BRANCH-1**, `methodology-changelog.md` v0.35.0 sub-mode (a) — narrows the empirically-permissive parent DEVIATION convention for audit-quality): when documenting a deliberate skip of BRANCH-1's branch-create discipline, the DEVIATION line MUST conform to this exact shape: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` (HH:MM required; `rationale:` token required; text is non-empty). `tools/branch_workflow_audit.py` escape-hatch grep accepts only this shape via the regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+`. Example: `2026-05-14 20:14 DEVIATION: BRANCH=skip — rationale: trivial 1-line typo fix per CLAUDE.md hard-rule exception`. **`BRANCH=skip` is preserved post-BRANCH-2 as a legacy parallel escape-hatch** (per ADR-063 §Scope of supersession "Carried forward unchanged" 4th-surface inheritance).

**Canonical `WORKTREE=skip` sub-shape** (per **BRANCH-2**, `methodology-changelog.md` v0.68.0; [[ADR-063]] §Decision; mirrors `BRANCH=skip`'s shape with a new keyword for the worktree-discipline-skip case): when documenting a deliberate skip of BRANCH-2's worktree-create discipline (slice-066 bootstrap; legacy single-tree edge cases; etc.), the DEVIATION line MUST conform to this exact shape: `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>` (HH:MM required; `rationale:` token required; text is non-empty). `tools/branch_workflow_audit.py` `_WORKTREE_SKIP_LINE_RE` grep accepts only this shape via the regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: WORKTREE=skip\b.+rationale: .+`. Example (slice-066 bootstrap): `2026-05-24 17:00 DEVIATION: WORKTREE=skip-bootstrap — rationale: slice-066 authors the worktree-create prose; bootstrap-reference instance #1`. Cross-spec parity (RPCD-1): the literal `WORKTREE=skip` is pinned across N=3 surfaces — (1) this canonical-line-shape paragraph, (2) `skills/commit-slice/SKILL.md` `--merge`/`--sync-after-pr` cleanup reminder, (3) `tools/branch_workflow_audit.py` `_WORKTREE_SKIP_LINE_RE` regex. Both grammars coexist post-BRANCH-2.

Keep entries to one line each. Detailed evidence (full command output, stack traces, screenshot paths) goes in the Summary section at slice end. The events section is the trace; the summary is the report.

`/pulse` reads the tail of this section on resume to reconstruct recent activity — durable next-action signal that survives `milestone.md` staleness.

### Step 8: Write `architecture/slices/slice-NNN-<name>/build-log.md`

```markdown
# Build log: Slice NNN <name>

**Date**: <YYYY-MM-DD>
**Result**: SHIPPED | SHIPPED-WITH-DEFERRALS | NOT-SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-03 14:25 BUILD: :app:assembleDebug PASS
- 2026-05-03 14:30 SMOKE: mid-slice run on Pixel 7
- 2026-05-03 14:32 FINDING: version footer half-hidden by nav bar
- 2026-05-03 14:33 ERROR: screenshot read failed (binary corruption); finding still valid via manual inspection

## Summary (filled at slice end)

### Plan executed
<the approved plan, with status per task>

### Mid-slice smoke gate
**Result**: PASS | FAIL
**Evidence**: <command + output>
<if FAIL: what was diagnosed and how it was fixed>

### Pre-finish gate
- [x] All ACs pass with evidence — see validation.md
- [x] Must-not-defer addressed
- [x] Drift-check pass
- [x] Smoke regression check pass
- [x] No debug code

### Deferrals (if any)
- <item> — reason: <why> — user-approved: <yes/no> — followup: <next slice / backlog>

### Design deviations (if any)
- <where design.md said X, code does Y because Z>
- <updated in design.md? yes/no>

### Files changed
- <list of source files modified>
```

## Critical rules

- ENTER PLAN MODE FIRST. Don't start editing without a user-approved plan.
- USE the Read / Glob / Grep tools to understand actual code BEFORE planning.
- DO NOT skip the mid-slice smoke gate. Catches "builds but doesn't work" early.
- DO NOT bypass the pre-finish gate. If something can't pass, the slice isn't done.
- DO NOT silently defer must-not-defer items. Ask explicitly.
- APPEND TO build-log.md events BEFORE risky tool calls (screenshots, image reads, large/binary outputs). Tool failures erase in-memory context; committed files persist. See Step 7c.
- IF design is wrong: STOP and surface, don't silently "make it work."

## When the design is wrong mid-build

This happens. Procedure:

1. STOP execution immediately
2. Write what you discovered (in conversation, not as a file yet)
3. Ask: "Design says X. Code says Y. Revise design, or proceed with documented deviation?"
4. If revise: stop the slice, run `/design-slice` updates, re-run `/critique` for the changed parts, then resume
5. If deviate: log the deviation in build-log.md and continue

## Heavy mode adjustment

In Heavy mode:
- Test coverage report at pre-finish (compliance trail)
- Sign-off field in build-log.md (human reviewer)
- Audit-grade commit messages: reference slice + ADRs

## The brief vs plan mode split

Persistent (mission brief, lives across sessions):
- Acceptance criteria
- Must-not-defer list
- Verification commands
- Vault/contract refs

Session (plan mode, mutable):
- Exact files to touch
- Task sequence
- Code-aware specifics

Brief carries discipline. Plan mode carries groundedness. This avoids the "500-line sprint file written against stale assumptions" failure mode.

## Next step

`/validate-slice` — reality check against real device / user / data.

## Pipeline position

- **predecessor**: `/critique` (post-TRI-1, on CLEAN/NEEDS-FIXES)
- **successor**: `/code-review`
- **auto-advance**: true
- **on-clean-completion**: once the pre-finish gate fully passes (all ACs, must-not-defer, drift-check, all Step 6 audits incl. PCA-1) and build-log.md is written, invoke `/code-review` via the Skill tool without waiting for the user. Per slice-060 / CRSI-1: `/code-review` is the in-loop adversarial code-Critic between `/build-slice` and `/validate-slice`; `/code-review` itself auto-advances to `/validate-slice` on clean completion (v1 walking-skeleton — advisory only; TRI-1 + verdict-driven block deferred to slice-062).
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Plan-mode approval (Step 3 / ExitPlanMode) — HALT for explicit user plan sign-off before any code edits.
  - Mid-slice smoke-gate failure (Step 5) — HALT, STOP, diagnose; do NOT auto-advance on a broken base.
  - Design-is-wrong mid-build — HALT and surface ("design says X, code says Y; revise or deviate?").

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. Manual invocation remains supported.
