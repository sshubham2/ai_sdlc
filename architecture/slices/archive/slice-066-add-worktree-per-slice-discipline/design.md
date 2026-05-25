# Design: Slice 066 add-worktree-per-slice-discipline

**Date**: 2026-05-24
**Mode**: Standard
**Risk tier**: medium — Critic required: yes (touches `skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `tools/branch_workflow_audit.py`, methodology-changelog, CLAUDE.md, new ADR → always-mandatory-Critic on in-house methodology surfaces)

## What's new

- **`skills/build-slice/SKILL.md`** — rewrite the `## Prerequisite check ### Branch state` sub-section (currently L39–L60) so the branch-create step uses `git worktree add ../<repo-parent>-wt/slice-NNN-<name> -b slice/NNN-<name> <default>` instead of `git checkout -b slice/NNN-<name>`. Tell Claude to `cd` into the worktree for the remainder of the slice. Resume case (`/build-slice` re-invoked on an existing slice): `cd <wt-path>` if the worktree exists, else recreate. Dirty-tree refusal preserved verbatim.
- **`skills/commit-slice/SKILL.md`** — extend Step 5b (`--merge`) and Step 5d (`--sync-after-pr`) cleanup flows with worktree-teardown. Step 5c (`--push`) is UNCHANGED (per user confirmation: worktree stays alive through `--push` until `--sync-after-pr`).
- **`tools/branch_workflow_audit.py`** — new helpers `_resolve_expected_worktree_path(slice_folder)`, `_is_repo_root_a_worktree(repo_root)`, `_worktree_registered(main_repo_root, wt_path)`. Updated `audit()` decision logic adds **four** new violation kinds: `worktree-not-registered`, `worktree-cwd-mismatch`, `worktree-path-shape-violation`, `worktree-skip-malformed` (per slice-066 /critique m1 ACCEPTED-FIXED — count harmonized across L11 / L84-88 / mission-brief AC3). New escape-hatch line `WORKTREE=skip` (separate regex from `BRANCH=skip`, same grammar shape).
- **`architecture/decisions/ADR-063-worktree-per-slice.md`** — mints **BRANCH-2** (worktree-per-slice + branch); supersedes **ADR-019** (BRANCH-1 — sub-mode (a) build-time branch-create only; sub-mode (b) was already partial-superseded by ADR-020 at slice-022 and remains so; sub-mode (c) audit-time pre-finish refusal is EXTENDED in place via the 4 new violation kinds, not superseded). ADR-020's three-mode `/commit-slice` design carries forward unchanged; this ADR EXTENDS the `--merge` + `--sync-after-pr` teardown but does not re-supersede ADR-020's mode definitions.
- **`methodology-changelog.md`** — new entry `## v0.68.0 — 2026-05-24` with `Rule reference: BRANCH-2` + `Defect class: cross-slice WT contamination + dirty-tree branch-create + single-branch-tree-checkout-conflict` + `Validation: tools.branch_workflow_audit (worktree-aware) + pytest test_branch_workflow_audit / test_adr_063_*` etc.
- **`CLAUDE.md`** — rewrite the "Branch-per-slice" bullet (currently L32 — verified by Read 2026-05-24; per slice-066 /critique M1 ACCEPTED-FIXED — was wrongly cited as L65 in the rev-1 design) to "Worktree-per-slice + branch", citing BRANCH-2 + ADR-063 + methodology v0.68.0; preserve the BRANCH-1 lineage citation as historical anchor.
- **`architecture/risk-register.md`** — transition R-17 entry from `**Status**: mitigating` → `**Status**: retired` with `**Retired**: slice-066-add-worktree-per-slice-discipline (2026-05-24; ADR-063 / BRANCH-2 / methodology v0.68.0)`. Append a retirement-paragraph naming the candidate-fix-(b) closure.
- **`tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py`** — NEW (file name corrected per slice-066 /critique B1 ACCEPTED-FIXED). Pins frontmatter `supersedes: ADR-019` + body's "Scope of supersession" section + asserts ADR-019 is git-clean (`append-only` invariant — even though ADR-020 also supersedes ADR-019, ADR-019 itself was never edited; the append-only rule holds across N=2 supersessions).
- **`tests/methodology/test_r17_retirement.py`** — NEW. Pins R-17 `**Status**: retired` line + asserts `$PY -m tools.risk_register_audit ... --filter-status open --json` does NOT include R-17 (post-slice-036 R-9 fix, this filter is now correct).
- **`tests/methodology/test_build_slice_skill.py`** — MODIFIED. New tests for AC1 (worktree-create invocation literal, sibling-path shape, absence of bare `git checkout -b slice/` in the prereq sub-section).
- **`tests/methodology/test_commit_slice_skill.py`** — MODIFIED. New tests for AC2 (Step 5b + 5d invoke `git worktree remove` + teardown order: worktree-remove BEFORE branch-delete).
- **`tests/methodology/test_branch_workflow_audit.py`** — MODIFIED. New tests for AC3 (worktree-mode accept/reject paths + WORKTREE=skip line shape).
- **`tests/methodology/test_methodology_changelog.py`** — MODIFIED. Mechanical add of `test_v_0_68_0_entry_present_in_repo` (no per-version installed-pin per slice-041 MCFS-1 decoupling — forward-sync re-homed on the whole-file gate; per-version installed-pins were retired in slice-041).
- **`tests/methodology/test_claude_md_pin.py`** — MODIFIED. New test asserting the "Worktree-per-slice + branch" rewrite + BRANCH-2 cite presence + BRANCH-1 lineage preservation.
- **`VERSION`** — bump 0.67.0 → 0.68.0.
- **`plugin.yaml`** — version bump 0.67.0 → 0.68.0 (PMI-1 part 2).
- **`architecture/shippability.md`** — new row #66 covering AC3's worktree-mode audit run.

## What's reused

- BRANCH-1's default-branch resolver (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → STOP) — unchanged; carries forward as the canonical helper across N=3 call sites (build-slice prereq, commit-slice 5b, commit-slice 5d) plus the new worktree-create invocation. See `tools/branch_workflow_audit.py:127` `_resolve_default_branch`. **Canonical-phrase N=3-surface pin** (per methodology-changelog v0.35.0 L677): the canonical phrase `git symbolic-ref refs/remotes/origin/HEAD` is pinned across N=3 surfaces; BRANCH-2 INHERITS this pin (the new worktree-create invocation in build-slice SKILL.md uses the same resolver). Per slice-066 /critique M4 ACCEPTED-FIXED — explicitly enumerated in ADR-063 §Scope of supersession "Carried forward unchanged".
- BRANCH-1 slice-branch naming convention (`slice/NNN-<slice-name>`, zero-padded 3-digit) — unchanged; the worktree's checked-out branch IS the same slice branch. See `_SLICE_BRANCH_RE` at `tools/branch_workflow_audit.py:59`.
- BRANCH-1 slice-folder naming convention (`slice-NNN-<name>`, numeric-only per ADR-046) — unchanged; the worktree's path uses the same folder slug as the suffix. See `_SLICE_FOLDER_RE` + `_SPLIT_SLICE_FOLDER_RE` at `tools/branch_workflow_audit.py:62-72`.
- BRANCH-1 escape-hatch grammar shape (`<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>`) — reused for the NEW `WORKTREE=skip` line (same regex shape, different keyword). See `_BRANCH_SKIP_LINE_RE` at `tools/branch_workflow_audit.py:53-56`.
- BRANCH-1 stale-slice-branch warning class — unchanged; the warning surface (`_check_stale_slice_branches` at `tools/branch_workflow_audit.py:205`) carries forward and now also flags stale worktrees by extension (out-of-scope for slice-066; documented as a future follow-up if N=2 stale-worktree incidents emerge).
- ADR-046 split-slice folder-naming convention (numeric-only accept; diagnostic letter-suffixed split-slice message) — unchanged. The worktree path inherits the numeric-only constraint.
- ADR-020 three-mode `/commit-slice` design (`--merge` / `--push` / `--sync-after-pr` mutual exclusion + the per-mode flows) — unchanged; ADR-063 ADDS worktree-teardown to `--merge` + `--sync-after-pr`, but does not supersede ADR-020. Note: ADR-020 itself partial-supersedes ADR-019 sub-mode (b) only (per methodology-changelog v0.36.0 L637-638), so ADR-019 is now once-partial-superseded by ADR-020 + about-to-be-twice-partial-superseded by ADR-063 (sub-mode (a)); sub-mode (c) audit-time refusal remains the only non-superseded surface and is EXTENDED in place via the 4 new violation kinds.
- ADR-019's `BRANCH=skip` escape-hatch — superseded only in the operational sense (worktree mode uses `WORKTREE=skip`); the `BRANCH=skip` line is preserved as a legacy escape-hatch when the audit detects a bare-main-tree slice run (matches the bootstrap-reference window for slice-066 itself).
- slice-022 ADR-020 partial-supersession encoding pattern: single `supersedes: <prior-ADR>` frontmatter slot + body-level "Scope of supersession" section. See [[ADR-020]] for the precedent; per slice-022 reflection D-2 + R-15 part-(b)-style retirement-discharge pattern.
- TF-1, WS-1, PMI-1, OSDG-1, EOL-DRIFT-1, CAD-1 audit family — all carry forward unchanged.
- MCFS-1 forward-sync gate (slice-041) — unchanged; the new v0.68.0 changelog entry is forward-sync-enforced by `tools/methodology_changelog_forward_sync.py`.
- SCMD-1 / SRSC-1 shippability catalog grammar + runner — unchanged; the new row #66 follows the established grammar.

## Components touched

### `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` (modified)
- **Responsibility**: at slice-start (Step 0 prereq), gate that the slice's work happens in its own filesystem-isolated worktree on its own `slice/NNN-<name>` branch.
- **Lives at**: `skills/build-slice/SKILL.md:39-60` (the existing Branch state sub-section).
- **Key interactions**: invokes `git worktree add` / `git worktree list --porcelain` / `git symbolic-ref` / `git config init.defaultBranch` (all native git plumbing); is dogfooded by every slice from slice-067 onward (slice-066 bootstrap-exempts via `WORKTREE=skip-bootstrap` Events line).
- **Behavior delta**: Pre-slice-066, the sub-section said "If on default branch: `git checkout -b slice/NNN-<slice-name>`". Post-slice-066, it says: "If on default branch: resolve `<wt-base>=$(realpath ../$(basename $(pwd))-wt)`, then `git worktree add <wt-base>/slice-NNN-<name> -b slice/NNN-<name> <default>`, then `cd <wt-base>/slice-NNN-<name>`. If the worktree already exists (resume after session death): `cd <wt-base>/slice-NNN-<name>` and verify `git branch --show-current` matches `slice/NNN-<name>`. If dirty tree on default branch: STOP (unchanged from BRANCH-1)." The `BRANCH=skip` escape-hatch carries forward as `WORKTREE=skip` (same grammar; new keyword) for the bootstrap window AND for legacy/edge-case slices.

### `skills/commit-slice/SKILL.md` Step 5b (`--merge`) + Step 5d (`--sync-after-pr`) (modified)
- **Responsibility**: at slice-end, tear down the per-slice worktree alongside the branch-delete that BRANCH-1 already does.
- **Lives at**: `skills/commit-slice/SKILL.md:162-186` (Step 5b) + `skills/commit-slice/SKILL.md:220-269` (Step 5d).
- **Key interactions**: invokes `git worktree remove <wt-path>` after the merge succeeds + before `git branch -d`. The order is load-bearing — a branch checked out in a worktree CANNOT be safely deleted (`git branch -d` refuses with "branch '<name>' checked out at '<wt-path>'"), so worktree-remove MUST precede branch-delete.
- **Behavior delta — Step 5b (`--merge`)**: pre-slice-066, the 5-step flow ended with `git branch -d slice/NNN-<name>`. Post-slice-066, the flow becomes:
  1. (inside worktree) commit on slice branch (existing).
  2. `cd <main-tree>` (NEW). The main-tree path is `$(git worktree list --porcelain | awk '/^worktree / {p=$2} /^bare$/ {next} /^branch refs\/heads\// && $2 != "refs/heads/slice/NNN-<name>" {print p; exit}')` — i.e., the first worktree record whose branch is NOT the slice branch (typically the main tree on `<default>`). On Windows, `awk` is provided via Git for Windows' bundled MSYS bash; on POSIX, native.
  3. `git checkout <default>` + `git merge --no-ff slice/NNN-<name>` (existing).
  4. Explicit confirm (existing /critique M5 ACCEPTED-PENDING — preserved verbatim).
  5. **Idempotent worktree-remove guard** (NEW; per slice-066 /critique B5 ACCEPTED-FIXED — covers slice-066's own bootstrap + any future `WORKTREE=skip` slice): pre-flight check `git worktree list --porcelain | grep -E "^branch refs/heads/slice/NNN-<name>$"` (POSIX shell; on Windows invoke via Git for Windows' bundled MSYS bash — same dependency as sub-step 2's `awk`, per slice-066 /critique-review M-add-3 ACCEPTED-FIXED parenthetical-acknowledgment option (i); slice-067+ may reshape the guard to use Python `subprocess.run(['git','worktree','list','--porcelain'])` + Python-side parsing for shell-agnostic execution if a recurrence emerges at N=2 across sibling /commit-slice cleanup surfaces). If empty (no worktree exists for this slice — bootstrap window OR documented WORKTREE=skip slice): LOG `slice/NNN-<name> worktree absent — skip worktree-remove (BRANCH-1 bootstrap or WORKTREE=skip slice)` to build-log Events + skip to step 6. Otherwise: `git worktree remove <wt-path>`. Refuses if the worktree has uncommitted state (post-step-1 commit, it shouldn't). On refuse: STOP loud — print git's stderr verbatim + actionable hint "If you have uncommitted work in the worktree, commit it before retry; if you intentionally abandoned changes, `git worktree remove --force <wt-path>` is the manual escape (this skill never auto-forces)".
  6. `git branch -d slice/NNN-<name>` (existing safe-delete). Order-load-bearing: worktree-remove (step 5) MUST precede branch-delete because a branch checked out in a worktree cannot be safely deleted — git refuses with "branch 'slice/NNN-<name>' checked out at '<wt-path>'" (verified via [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree); web-known-issue evidence in slice-066 /critique Dim 8).
  7. `git log -1` + `git log --graph` (existing).
- **Behavior delta — Step 5c (`--push`)**: UNCHANGED. Per user confirmation, the worktree stays alive through `--push` until `--sync-after-pr` (mirrors current branch lifecycle — `--push` doesn't delete the branch either).

- **Mode-interaction matrix** (per slice-066 /critique M3 ACCEPTED-FIXED — closes the "what happens on unhappy-path mode combinations" specification gap):

  | Sequence | Step 5b worktree-remove fires? | Step 5d worktree-remove fires? | Worktree state at end |
  |----------|-------------------------------|--------------------------------|----------------------|
  | `--push` only (PR pending review — no follow-up yet) | N/A (5b not invoked) | N/A (5d not invoked) | intact (expected; teardown deferred to eventual `--sync-after-pr` or `--merge`) — per slice-066 /critique-review M-add-4 ACCEPTED-FIXED |
  | `--merge` (no prior `--push`) | YES — Step 5b new sub-step 5 | N/A (5d not invoked) | removed |
  | `--push` then `--sync-after-pr` (PR merged, signals A+B both YES) | N/A | YES — Step 5d new sub-step 8 | removed |
  | `--push` then `--sync-after-pr` (signals A or B NO — STOP before any state change) | N/A | NO — STOPs pre-state-change | intact (unchanged) |
  | `--push` then `--merge` (abandoned PR, switched to local merge) | YES — Step 5b new sub-step 5 fires identically | N/A | removed |
  | `--push` then `--merge` after a force-push iteration | YES — Step 5b worktree-remove fires identically; `--merge` doesn't inspect remote ref state | N/A | removed; user must manually handle the orphaned remote `origin/slice/NNN-<name>` (existing ADR-020 behaviour — slice-066 doesn't change this) |

  The idempotent guard in Step 5b sub-step 5 (per /critique B5 ACCEPTED-FIXED) ensures the matrix's rightmost column "removed" actually means "removed if existed, otherwise no-op logged" — covering both the bootstrap window AND any future `WORKTREE=skip` slice.
- **Behavior delta — Step 5d (`--sync-after-pr`)**: pre-slice-066, cleanup was `git checkout <default>` + `git pull --ff-only` + `git branch -d`. Post-slice-066:
  1. Pre-flight checks (existing — unchanged).
  2. Sync remote refs (existing).
  3. Resolve default branch (existing).
  4. Two-signal merged-state detection (existing — preserves Signal A + Signal B two-pass logic + 3 guards verbatim per slice-022 /critique B2 + /critique-review M-add-5). If Signal A or B fails, STOP — worktree intact, no state change (per Mode-interaction matrix row 3).
  5. Confirm (existing).
  6. `cd <main-tree>` (NEW — same mechanism as Step 5b sub-step 2). The existing skill prose at `commit-slice/SKILL.md:258` already handles the `<default>` checked-out-elsewhere case with diagnostics; with worktree mode this becomes the expected case rather than the error case, so the diagnostic is rewritten to instruct the cd.
  7. `git checkout <default>` + `git pull --ff-only origin <default>` (existing — works from main tree where default is its own checkout).
  8. **Idempotent worktree-remove guard** (NEW; same shape as Step 5b sub-step 5 — closes the slice-066 bootstrap symmetry per /critique B5 ACCEPTED-FIXED): pre-flight `git worktree list --porcelain | grep -E "^branch refs/heads/slice/NNN-<name>$"`. If empty: LOG `slice/NNN-<name> worktree absent — skip worktree-remove`. Otherwise: `git worktree remove <wt-path>`.
  9. `git branch -d slice/NNN-<name>` (existing — order-load-bearing per Step 5b sub-step 6).
  10. `git log` (existing).

### `tools/branch_workflow_audit.py` (modified)
- **Responsibility**: programmatic gate at `/build-slice` Step 6 pre-finish + at slice integration points that the current state is a valid worktree-per-slice configuration.
- **Lives at**: `tools/branch_workflow_audit.py:1-445` (full module modified).
- **Key interactions**: invokes `git -C <repo_root> worktree list --porcelain`, `git -C <repo_root> branch --show-current`, `git -C <repo_root> symbolic-ref` (existing), and resolves `<wt-base>` via `Path(slice_folder).resolve().parents[N]`-walk to determine the canonical worktree path.
- **New helpers**:
  - `_resolve_expected_worktree_path(slice_folder: Path, main_repo_root: Path) -> Path`: returns `main_repo_root.parent / f"{main_repo_root.name}-wt" / slice_folder.name`. Used to compare against actual cwd and against `git worktree list --porcelain` entries.
  - `_is_repo_root_a_worktree(repo_root: Path) -> tuple[bool, Path | None]`: returns `(in_worktree, main_repo_root)`. Detection: a worktree's `.git` is a FILE (not directory) containing `gitdir: <main-repo>/.git/worktrees/<name>`. Parse the gitdir line + walk up to the main repo root.
  - `_worktree_registered(main_repo_root: Path, wt_path: Path) -> bool`: invokes `git -C <main_repo_root> worktree list --porcelain`, parses the `worktree <path>` records, returns True if `wt_path.resolve()` matches any record.
  - `_check_worktree_skip_line(slice_folder: Path) -> tuple[bool, str | None, BranchViolation | None]`: mirror of `_check_escape_hatch` but for the new `WORKTREE=skip` keyword. Returns `(skip_used, rationale, malformed_violation)`.
- **Path-comparison semantics** (per slice-066 /critique B2 ACCEPTED-FIXED — closes the Windows symlink/junction + case-insensitivity equivalence gap surfaced via WebSearch on [microsoft/vscode#101244](https://github.com/microsoft/vscode/issues/101244)): `_worktree_registered` and the `worktree-cwd-mismatch` check use `Path.resolve(strict=False)` on both sides + `samefile()` when both paths exist (the canonical clean case); fallback to `os.path.normcase(os.path.realpath(...))` string equality when one side doesn't exist (the worktree-not-registered detection path). Junctions / symlinks resolved transparently to their targets; case-insensitive comparison on Windows (via `normcase`). UNC paths (mission-brief Out-of-scope L88) are surfaced via a documented refusal kind rather than silent miscomparison.
- **Audit invocation call-shapes** (per slice-066 /critique B3 ACCEPTED-FIXED — closes the `worktree-cwd-mismatch` structurally-undefined-behaviour window). The audit handles three shapes, in priority order:
  1. **Cwd is inside the worktree, slice-folder path under the worktree's `architecture/`** (the canonical clean shape): `_is_repo_root_a_worktree(repo_root)` returns `(True, main_repo_root)`; `_worktree_registered(main_repo_root, repo_root)` returns True; `current_branch == expected_slice_branch`. CLEAN exit.
  2. **Cwd is the main tree, slice-folder path under the main tree's `architecture/`, BUT the slice branch is checked out in a worktree elsewhere** (the canonical "Claude forgot to `cd`" shape): `_is_repo_root_a_worktree(repo_root)` returns `(False, None)`; `git -C <main_repo_root> worktree list --porcelain` shows the slice branch checked out at `<expected_wt_path>`. Emit `worktree-cwd-mismatch` (Important). The audit treats `Path.cwd()` and the `slice_folder.parents`-derived `repo_root` as equivalent for this check — when they diverge, the worktree-list-vs-cwd disagreement IS the violation signal.
  3. **Composite: cwd is the main tree, slice-folder passed as `--root <main-tree>` + `<folder>`, worktree exists elsewhere** (the legacy bare-main-tree case OR a CI runner invocation): same as shape 2 — the `--root` flag does not exempt from the `worktree-cwd-mismatch` check, since being in the main tree while a worktree is checked out IS the misconfiguration the gate exists to catch. `WORKTREE=skip — rationale: <text>` in build-log.md Events is the documented escape.
- **New violation kinds added to `BranchViolation.kind` enum** (preserving the existing kinds — additive):
  - `worktree-not-registered`: cwd matches the expected worktree path but `git worktree list --porcelain` doesn't list it (corrupted state — `.git` file points to a worktree record that no longer exists).
  - `worktree-cwd-mismatch`: the slice branch is checked out in a worktree per `git worktree list --porcelain`, but `Path.cwd()` is the main tree (Claude forgot to `cd`). Severity Important; refuses at Step 6.
  - `worktree-path-shape-violation`: the slice's worktree is registered but at a path that doesn't match `_resolve_expected_worktree_path(slice_folder, main_repo_root)`. Severity Important.
  - `worktree-skip-malformed`: a `WORKTREE=skip` line is present in `build-log.md` Events but doesn't conform to the canonical grammar (mirrors `escape-hatch-malformed`).
- **Behavior delta**:
  - The existing `if current == default` branch (currently L357) is restructured: when in worktree mode (`_is_repo_root_a_worktree(repo_root)` → True), `current` is the slice branch (worktree's HEAD); the on-default-branch violation is bypassed since being in the worktree IS the legitimate state.
  - A new pre-check fires: if `Path.cwd()` resolves into the main tree but `git -C <main> worktree list --porcelain` shows the slice branch checked out in `<expected_wt>`, emit `worktree-cwd-mismatch` (severity Important) regardless of other state. This is the structural backstop for "Claude forgot to `cd` into the worktree".
  - The legacy bare-main-tree flow (no worktree exists yet — slice-066 bootstrap window) continues to honour the `BRANCH=skip` escape-hatch for backwards compatibility AND the new `WORKTREE=skip` escape-hatch for the slice-066 bootstrap exemption + future legacy/edge cases.

### `architecture/decisions/ADR-063-worktree-per-slice.md` (new)
- **Responsibility**: the canonical decision record minting BRANCH-2.
- **Lives at**: `architecture/decisions/ADR-063-worktree-per-slice.md` (new file).
- **Key interactions**: superseded ADR ([[ADR-019]]) reachable via the `supersedes:` frontmatter slot; downstream test `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py` pins the both-direction invariants.
- See the ADR file for full content (Step 5 below).

## Contracts added or changed

### `tools/branch_workflow_audit.py` CLI contract — extended (not breaking)
- **Endpoint**: `python -m tools.branch_workflow_audit [--json] [--root <repo-root>] <slice-folder>`
- **Defined in code at**: `tools/branch_workflow_audit.py:403-444` (`main()`).
- **Exit codes** (additive — existing codes preserved):
  - 0: clean (worktree mode validated OR legacy bare-main-tree-with-`BRANCH=skip` OR `WORKTREE=skip` escape-hatch present).
  - 1: violations (any Important kind including the 4 new worktree-* kinds).
  - 2: usage error (slice-folder missing, git unavailable, default-branch-unresolvable — UNCHANGED).
- **Error cases**:
  - `worktree-not-registered` (NEW): cwd looks like a worktree but `git worktree list` doesn't show it.
  - `worktree-cwd-mismatch` (NEW): main tree cwd + slice branch checked out in worktree → forgot to cd.
  - `worktree-path-shape-violation` (NEW): worktree registered but at non-canonical path.
  - `worktree-skip-malformed` (NEW): malformed `WORKTREE=skip` line.
  - Existing kinds (preserved): `on-default-branch`, `slice-branch-mismatch`, `escape-hatch-malformed`, `default-branch-unresolvable`, `stale-slice-branch`, `usage-error`.

### `WORKTREE=skip` Events-line grammar (new — mirrors BRANCH=skip)
- **Defined in code at**: `tools/branch_workflow_audit.py` (new regex `_WORKTREE_SKIP_LINE_RE`).
- **Grammar**: `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: WORKTREE=skip\b.+rationale: .+` (HH:MM required + `rationale:` token required — same shape as BRANCH=skip).
- **Pin surface**: `skills/build-slice/SKILL.md` Step 7c canonical-line-shape paragraph; cross-spec parity test (RPCD-1) asserts the same grammar literal appears in build-slice SKILL.md + commit-slice SKILL.md + branch_workflow_audit.py.

## Data model deltas

N/A — this slice has no data model. All state is git-internal (`.git/worktrees/<name>/`) or filesystem (worktree directory).

## Wiring matrix

Per **WIRE-1** ([[methodology-changelog.md#v0.9.0]]).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `architecture/decisions/ADR-063-worktree-per-slice.md` | Cited in `methodology-changelog.md` v0.68.0 + CLAUDE.md "Worktree-per-slice + branch" + `tools/branch_workflow_audit.py` module docstring | `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py` | — |
| `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py` | `architecture/shippability.md` row #66 invokes via shippability runner | `pytest tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py` (self-collecting; pytest collection IS the consumer test for a test module per slice-062 walk-proof precedent) | — |
| `tests/methodology/test_r17_retirement.py` | `architecture/shippability.md` row #66 invokes via shippability runner | `pytest tests/methodology/test_r17_retirement.py` (self-collecting per slice-062 walk-proof precedent) | — |

No exemptions. All new modules have explicit consumers + tests.

## Decisions made (ADRs)

- [[ADR-063]] — Worktree-per-slice + branch (BRANCH-2) supersedes BRANCH-1's branch-create mechanism; `--merge` and `--sync-after-pr` cleanups extended with `git worktree remove` — reversibility: **cheap** (1 ADR + 1 audit-module-modification revert; the `git worktree remove`/`git checkout -b` operational difference is git-builtin reversible).

## Authorization model for this slice

N/A — methodology tooling; no user-facing auth. The audit refuses or accepts based on git state; there is no actor/identity dimension.

## Error model for this slice

The 4 NEW error classes (all Important severity, all surface at `/build-slice` Step 6 pre-finish unless escape-hatch present):

| Code | Trigger | User message (verbatim shape) |
|------|---------|-------------------------------|
| `worktree-not-registered` | cwd resolves to expected worktree path BUT `git worktree list --porcelain` does not list it | "Worktree at `<wt-path>` is not registered via `git worktree list`. The worktree's `.git` file may be stale or the worktree may have been manually deleted. Recover with `git worktree repair` (if `<wt-path>` exists) or `git worktree add <wt-path> -b slice/NNN-<name> <default>` (if you deleted it)." |
| `worktree-cwd-mismatch` | `Path.cwd()` is the main tree AND `git worktree list --porcelain` shows the slice branch checked out elsewhere | "Slice branch `slice/NNN-<name>` is checked out in worktree `<wt-path>` but your cwd is the main tree `<main-path>`. Did you forget to `cd <wt-path>`? Run `cd <wt-path>` and retry; or, if you intend to skip the worktree discipline for this slice, document the canonical `WORKTREE=skip — rationale: <text>` line in build-log.md Events." |
| `worktree-path-shape-violation` | worktree is registered but at path != `<main-parent>/<main-name>-wt/slice-NNN-<name>` | "Worktree is registered at `<actual-path>` but the canonical convention is `<expected-path>` (`<main-parent>/<main-name>-wt/slice-NNN-<name>` per ADR-063 § \"Worktree path convention\"). Move the worktree (`git worktree move <actual-path> <expected-path>`) or document `WORKTREE=skip — rationale: <text>` in build-log.md Events." |
| `worktree-skip-malformed` | `WORKTREE=skip` line present in build-log.md Events but doesn't conform to canonical grammar | "build-log.md Events contains `WORKTREE=skip` but doesn't conform to canonical shape. Required: `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>` per skills/build-slice/SKILL.md Step 7c." |

The existing 7 BRANCH-1 error classes are preserved verbatim.

## Critical implementation order (for /build-slice)

The build phase MUST proceed in this order (per the TF-1 plan in mission-brief.md):

1. **Write the failing repro tests first** (TF-1) — all 20 TF-1 rows flip PENDING → WRITTEN-FAILING before any source edit (count updated per slice-066 /critique-review M-add-2 ACCEPTED-FIXED; was stale "16" from rev-1 pre-B3/B4-expansion). Confirms the tests would have caught the missing capability.
2. **Edit `tools/branch_workflow_audit.py`** to add the 4 helpers + 4 violation kinds + WORKTREE=skip handling. AC3 tests flip WRITTEN-FAILING → PASSING.
3. **Edit `skills/build-slice/SKILL.md`** Branch state sub-section. AC1 tests flip PASSING.
4. **Edit `skills/commit-slice/SKILL.md`** Step 5b + Step 5d. AC2 tests flip PASSING.
5. **Forward-sync** both edited skills to `~/.claude/skills/<name>/SKILL.md` (OSDG-1 + EOL-DRIFT-1 EOL-agnostic). Drift tests flip PASSING.
6. **Write ADR-063** + `tests/methodology/test_adr_063_*` (the test was already WRITTEN-FAILING in step 1; it flips PASSING when ADR-063 lands).
7. **Edit `methodology-changelog.md`** to add v0.68.0 entry. `test_v_0_68_0_entry_present_in_repo` flips PASSING.
8. **Forward-sync** methodology-changelog to `~/.claude/methodology-changelog.md` (MCFS-1).
9. **Edit `CLAUDE.md`** "Branch-per-slice" paragraph. `test_branch_per_slice_paragraph_rewritten_to_worktree_per_slice` flips PASSING.
10. **Edit `architecture/risk-register.md`** R-17 status to retired. AC5 tests flip PASSING.
11. **Edit `VERSION`** + **`plugin.yaml`** + add shippability row #66. PMI-1 5-part atomic bump complete (`tools.plugin_manifest_audit` exits 0).
12. **Run full /build-slice Step 6 pre-finish gate**: TF-1 strict-pre-finish (20/20 PASSING — per slice-066 /critique-review M-add-2 ACCEPTED-FIXED), WS-1 strict-pre-finish (5/5 EXERCISED), PMI-1, MCFS-1, CAD-1, OSDG-1, MCFS-1, branch_workflow_audit (with WORKTREE=skip-bootstrap line for slice-066 itself), shippability runner (66 rows including new #66).

**Bootstrap discipline**: per the slice-021 BRANCH-1 + slice-026 CRP-1 precedent, slice-066 itself runs WITHOUT worktree-mode at its own `/build-slice` (the SKILL.md prose authoring the worktree-create step doesn't yet exist at slice-066 start; cannot self-apply). The canonical `WORKTREE=skip-bootstrap — rationale: slice-066 authors the worktree-create prose; bootstrap-reference instance #1` line in build-log.md Events covers the gap. Every slice from slice-067 onward inherits a self-gating BRANCH-2 audit.

## Test coverage shape

Per the TF-1 plan in mission-brief.md (**20 rows** post-/critique fixes — was 16 in rev-1, +1 cross-spec parity (B4 ACCEPTED-FIXED), +3 audit call-shape rows (B3 ACCEPTED-FIXED)). High-level coverage:

- **AC1 (3 tests)**: `tests/methodology/test_build_slice_skill.py` — worktree-add invocation literal + sibling-path shape + absence-of-bare-checkout-b.
- **AC2 (3 tests)**: `tests/methodology/test_commit_slice_skill.py` — worktree-remove in Step 5b + Step 5d + teardown-order pin (worktree-remove BEFORE branch-delete).
- **AC3 (7 tests, was 4)**: `tests/methodology/test_branch_workflow_audit.py` — covers the three audit call-shapes enumerated above:
  - `test_accepts_cwd_in_worktree_sibling_path` (shape 1, canonical clean).
  - `test_accepts_worktree_registered_via_git_worktree_list_porcelain` (shape 1, registration check).
  - `test_accepts_invocation_from_inside_worktree_with_relative_slice_folder` (shape 1, cwd-relative path resolution).
  - `test_rejects_main_tree_cwd_when_worktree_registered_elsewhere` (shape 2 + 3 — "Claude forgot to `cd`" canonical case + `--root` variant; emits `worktree-cwd-mismatch`).
  - `test_emits_worktree_path_shape_violation_on_non_canonical_wt_path` (worktree registered but at non-canonical path; emits `worktree-path-shape-violation`).
  - `test_honours_canonical_worktree_skip_rationale_line` (escape-hatch accept).
  - `test_emits_worktree_skip_malformed_on_off_canonical_line` (escape-hatch malformed — the 4th violation kind per m1 ACCEPTED-FIXED).
- **AC3 cross-spec parity (1 test)**: `test_worktree_skip_grammar_pinned_across_three_surfaces` (per /critique B4 ACCEPTED-FIXED — added as a dedicated TF-1 row; closes the slice-013/014 SCPD-1 / FBCD-1 sub-mode (a) class).
- **AC4 (4 tests)**: ADR-063 frontmatter `supersedes: ADR-019` + body's "Scope of supersession" section + ADR-019-unmodified-append-only + methodology-changelog v0.68.0 entry + CLAUDE.md rewrite.
- **AC5 (2 tests)**: R-17 status retired + R-17 absent from risk_register_audit --filter-status open.

**Cross-spec parity test (RPCD-1)**: `test_worktree_skip_grammar_pinned_across_three_surfaces` asserts the `WORKTREE=skip` regex literal appears verbatim in (1) build-slice SKILL.md Step 7c, (2) commit-slice SKILL.md `--merge`/`--sync-after-pr` (canonical-shape reminder), (3) branch_workflow_audit.py `_WORKTREE_SKIP_LINE_RE`. Closes the cross-surface drift class (slice-019 LAYER-EVID-1 / slice-023 EPGD-1 precedent for cross-surface invariant pins). Now enumerated as a dedicated TF-1 row (no longer prose-only — was the slice-066 /critique B4 catch).

## Decisions deferred (NOT this slice)

- **Worktree pruning / garbage collection** — if N=2 stale-worktree incidents emerge (parallel to BRANCH-1's `_check_stale_slice_branches`), a follow-up slice adds `_check_stale_worktrees` to the audit. Currently not enough evidence to codify.
- **Rebase strategy in `/commit-slice --merge`** — slice D (`add-rebase-and-conflict-discipline`) handles rebase + conflict resolution. Slice-066 preserves the existing no-ff-merge contract verbatim.
- **`/slice` parallel-queue file** — slice A (`add-parallel-slice-queue-output`); needs slice-066 worktree mechanics + graphify blast-radius non-overlap computation.
- **Claim state machine** — slice B (`add-slice-queue-claim-state-machine`); depends on slice A.
- **WSL / Cygwin / network-drive worktree paths** — Windows + POSIX only in slice-066; cross-platform edge cases defer to a future slice if reports emerge.

## Pipeline position

- **predecessor**: `/slice`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: design.md + ADR-063 written → auto-invoke `/critique` via the Skill tool.
- **user-input gates**: none in this skill — clarifying questions answered upfront (worktree path convention + `--push` worktree handling).

Per PCA-1 ([[methodology-changelog.md#v0.41.0]]).
