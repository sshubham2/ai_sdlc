# Design: Slice 077 enhance-pulse-with-worktree-awareness

**Date**: 2026-05-28
**Mode**: Standard
**MEPD-1 path**: **EXCLUDE** (no methodology-changelog entry; no PMI-1 bump; ADR-070 minted to capture the design choice; rationale below)

## What's new

- `tools/pulse_worktree_resolver.py` — new helper module (estimated ~300-500 LOC; comparison: PCR-1's `parallel_conflict_resolver.py` is 1014 LOC because it ships claim-overlay + 5-class taxonomy + audit log + soft-resolution + classify + diagnose; slice-077's helper ships just 2 main functions + dataclasses + CLI → expected ~30-50% of PCR-1's size; per /critique m1 ACCEPTED-FIXED tightening). Frozen dataclasses `WorktreeInfo` + `WorktreeStateClassification` (carries `.state: WorktreeState` + `.reason: str` for debugging); enum `WorktreeState` with 4 values (`IN_PROGRESS` / `BUILT_BUT_NOT_MERGED` / `MERGED` / `UNKNOWN`). Library API surfaces: `detect_active_worktrees(repo_root)` and `classify_worktree_state(worktree, default_branch, repo_root) -> WorktreeStateClassification`. CLI: `python -m tools.pulse_worktree_resolver [--detect | --classify <slice-NNN>] [--json] [--repo-root <path>]`.
- `skills/pulse/SKILL.md` Step 1 prose enhancement — INSERT a new bullet BEFORE the existing "Active slice folder (if any): milestone.md FIRST..." bullet (L42) that documents `git worktree list --porcelain` parsing (via the new helper) as a mandatory pre-read step; the existing milestone.md read is preserved AND extended to also consult the worktree's milestone.md when a non-main slice/NNN worktree exists.
- `skills/pulse/SKILL.md` Step 2 prose enhancement — INSERT a new paragraph in "Active slice stage + next action" documenting the worktree-state classification + override-precedence ordering for all 4 WorktreeState × CAL-1 cells (see § Override-precedence ordering below). The override is applied at Step 2 deterministic metric computation (main-thread); the Step 3 Haiku-dispatched rendering consumes the resolved recommendation from the augmented structured-state dict — Haiku itself does not run the override logic.
- `skills/pulse/SKILL.md` Step 3 prose enhancement — INSERT a new paragraph in "Drift & flags" guidance documenting the false-positive suppression rule (master-vs-installed divergence is the EXPECTED state during a `BUILT_BUT_NOT_MERGED` window when installed-content matches worktree) + the UNKNOWN-state WARN-not-silent-drop policy.
- `architecture/decisions/ADR-070-worktree-awareness-in-pulse.md` — captures the design choice (per-skill helper, not load-bearing methodology rule; 4-state taxonomy; override precedence; fail-closed UNKNOWN).
- **6 new test modules** (per mission-brief test-first plan): `tests/methodology/test_pulse_skill_worktree_awareness.py`, `tests/methodology/test_pulse_worktree_resolver_tool_inventory.py`, `tests/skills/pulse/test_classify_worktree_state.py`, `tests/skills/pulse/test_drift_flag_suppression.py`, `tests/skills/pulse/test_detect_active_worktrees.py`, `tests/skills/pulse/test_cli.py`. Per critique M2 ACCEPTED-FIXED correction from earlier "5 new" miscount.
- `architecture/slices/slice-077-enhance-pulse-with-worktree-awareness/aped_1_battery.py` — APED-1 empirical-execution battery (must-not-defer per mission-brief; ≥13 enumerated cases per /critique M8 ACCEPTED-FIXED).
- `architecture/shippability.md` row #77.

## What's reused

- `tools/branch_workflow_audit.py::_resolve_default_branch(repo_root)` — IMPORTED for default-branch resolution (canonical 2-step `git symbolic-ref refs/remotes/origin/HEAD` + `git config init.defaultBranch` fallback). Re-using this preserves NAW-1 ADR-061 exit-2 contract semantics on default-branch-unresolvable AND keeps the default-branch-resolution discipline single-sourced.
- `tools/slice_queue_writer.py:252-280` worktree-list parsing pattern — REPLICATED (not imported). Note: this makes the Python-side parser count N=3 across the codebase (`slice_queue_writer.py:265` + `branch_workflow_audit.py:333+359` + this new helper) — Fowler's extract trigger. Slice-077 nevertheless replicates with deliberate scope-discipline rationale; the queued `parallel-slice-family-parity-audit` slice is the canonical extraction-trigger slice (see § Known limitations m4 disposition for rationale). Pattern: `subprocess.run(["git", "-C", str(repo_root), "worktree", "list", "--porcelain"], ...)` + line-by-line walk parsing `worktree ` + `branch refs/heads/...` + blank-line separators. Verified ordering invariant per git-scm.com/docs/git-worktree: "The main worktree is listed first, followed by each of the linked worktrees."
- UTF8-STDOUT-1 shim (`tools._stdout.reconfigure_stdout_utf8()` per slice-059 TVFS-1 / slice-023 UTF8-STDOUT-1) — REUSED at top of `main()` for Windows console encoding safety.
- BRANCH-2 worktree-path convention from [[ADR-063]] — `<main-parent>/<main-name>-wt/slice-NNN-<name>` on branch `slice/NNN-<name>` — used as the validation predicate for "is this a BRANCH-2 slice worktree?" (path + branch name shape match).
- milestone.md frontmatter `stage:` parsing — implemented as inline simple-regex (no pyyaml dependency); same shape as `/pulse`'s existing Step 2 milestone.md frontmatter read at L56-60 of SKILL.md.
- CAD-1 / OSDG-1 byte-equality discipline for `skills/pulse/SKILL.md` repo↔installed — already in place; existing `test_pulse_skill_drift.py` will catch drift post-edit.

## Components touched

### `tools/pulse_worktree_resolver.py` (NEW)
- **Responsibility**: detects BRANCH-2 slice worktrees registered with the repo and classifies each worktree's HEAD-vs-default state, surfacing the data `/pulse` needs to produce a worktree-aware macro-state summary. Read-only — does NOT modify worktree state, does NOT invoke git mutations.
- **Lives at**: `tools/pulse_worktree_resolver.py` (created by this slice).
- **Key interactions**: subprocess `git worktree list --porcelain` (worktree enumeration); subprocess `git merge-base --is-ancestor <worktree-HEAD> <default-tip>` (state classification); reads worktree's `architecture/slices/<active>/milestone.md` (active OR `archive/slice-NNN-<name>/milestone.md` if auto-archived) for stage field; imports `tools.branch_workflow_audit._resolve_default_branch`.

### `skills/pulse/SKILL.md` (MODIFIED)
- **Responsibility**: macro-state observability skill. After this slice ships, also surfaces BRANCH-2 worktree state (active worktrees + their HEAD-vs-default classification) and overrides recommended-next-action + suppresses drift false-positives accordingly.
- **Lives at**: `skills/pulse/SKILL.md` (existing — modified Step 1 + Step 2 + Step 3 prose blocks).
- **Key interactions**: invokes `python -m tools.pulse_worktree_resolver --detect --json` at Step 1 (before milestone.md read); Haiku dispatch in Step 3 receives augmented structured-state dict with `worktrees: list[WorktreeInfo]` + per-worktree `state: WorktreeState` fields.

### `tools/install_audit.py::_CANONICAL_TOOLS` (MODIFIED)
- **Responsibility**: canonical tools list for INST-1 inventory audit.
- **Modification**: add `"pulse_worktree_resolver"` entry.

### `plugin.yaml` (MODIFIED)
- **Responsibility**: plugin manifest for PMI-1 audit.
- **Modification**: add `- path: tools/pulse_worktree_resolver.py` to tools block.

### `INSTALL.md` (MODIFIED)
- **Responsibility**: install recipe — tool-count literals at L22 + L166.
- **Modification**: `31 → 32` at both sites (per slice-076 M6 precedent — two-site bump).

### `tests/methodology/test_utf8_stdout_regression.py` (MODIFIED)
- **Modification**: add `"pulse_worktree_resolver"` to `_ROOT_ONLY_TOOLS` (helper uses `--repo-root` with no positional slice arg → root-only bucket per slice-067 / parallel_conflict_resolver precedent).

## Contracts added or changed

NONE — no new endpoints, events, or external interfaces. The library API surface is internal:

- `detect_active_worktrees(repo_root: Path) -> list[WorktreeInfo]` — returns each non-main worktree on a `slice/NNN-<name>` branch (per BRANCH-2 path+branch shape predicate). Returns empty list when only the main worktree exists. Worktrees that fail the path+branch predicate are filtered out (non-slice branches, no-suffix `slice/077` malformed, prunable-stale registrations — each filtered with optional WARN per § Fail-closed paths summary).
- `classify_worktree_state(worktree: WorktreeInfo, default_branch: str, repo_root: Path) -> WorktreeStateClassification` — returns a frozen dataclass with `.state: WorktreeState` (one of the 4 enum values) + `.reason: str` (human-readable rationale; load-bearing for debugging + Drift & flags WARN surfacing).

Detailed signatures + dataclass fields live in code (`tools/pulse_worktree_resolver.py`); not duplicated here per thin-vault.

## Data model deltas

NONE.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0):

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/pulse_worktree_resolver.py` | `skills/pulse/SKILL.md` Step 1 (CLI invocation via `python -m tools.pulse_worktree_resolver --detect --json`) | `tests/methodology/test_pulse_skill_worktree_awareness.py::test_step_1_documents_pulse_worktree_resolver_dispatch` | — |

## Decisions made (ADRs)

- [[ADR-070]] — Worktree-awareness in /pulse via per-skill helper (not load-bearing methodology rule) — reversibility: **cheap**.

## Authorization model for this slice

N/A — `/pulse` is read-only observability. No mutations, no auth model.

## Error model for this slice

`tools/pulse_worktree_resolver.py`:

- **Exit 0** — success. `--detect` emits JSON list of detected worktrees (empty list when no non-main worktrees). `--classify` emits JSON `WorktreeStateClassification` for the named slice.
- **Exit 1** — runtime error: git command failed (e.g., not in a git repo, worktree-list parse error), milestone.md unparseable, fail-closed UNKNOWN returned from `classify_worktree_state` when invoked via `--classify`. Diagnostic written to stderr in `{"action": "<verb>", "error": "<message>"}` JSON shape (matches parallel_conflict_resolver convention).
- **Exit 2** — malformed CLI args (argparse-driven; `--detect` + `--classify` mutually-exclusive group required, OR unknown args). Per /critique B2 ACCEPTED-FIXED — earlier draft incorrectly listed PCR-1's flags (`--diagnose / --classify / --resolve-soft`) via copy-paste.

Fail-closed contract:
- `classify_worktree_state` returns `WorktreeState.UNKNOWN` on ANY parse failure (git command failure, milestone.md missing, milestone.md frontmatter malformed, HEAD-sha unresolvable). NEVER silent-defaults to `MERGED` or `BUILT_BUT_NOT_MERGED`. Mirrors PCR-1 UNKNOWN fail-closed pattern.
- `/pulse` SKILL.md prose says: on UNKNOWN, FALL BACK to main-tree-only behavior (current `/pulse` behavior preserved) AND surface a one-line WARN in "Drift & flags" section noting the detection failure.

## MEPD-1 path declaration + rationale

**EXCLUDE** — ships at v0.73.0 unchanged.

**Honest precedent inspection (per /critique M1 ACCEPTED-FIXED)**: slice-077 is structurally between two prior MEPD-1 precedents — slice-058 (ADR-only mint, no rule, no helper module of this scale) and slice-076 (ADR + new ~1014 LOC helper + INCLUDE — minted PCR-1). The earlier draft of this rationale cited slice-074/075 as EXCLUDE precedents, but BOTH were pure SKILL.md prose enhancements with ZERO new helper modules — the precedent shape doesn't survive direct inspection. The ONLY same-shape predecessor (helper module + 5-inventory fan-out + multiple test modules) is slice-076, which is MEPD-1 INCLUDE.

**Why EXCLUDE is still correct despite the precedent stretch — the differentiator is NOT "ships a helper module" but "introduces a load-bearing cross-skill methodology contract"**:

- **Slice-076 / PCR-1 IS load-bearing cross-skill**: the SOFT file-set + classify_conflict 5-class taxonomy + resolve_soft_conflict ABI are **called from `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5** (cross-skill consumer). The SOFT taxonomy is referenced in /commit-slice prose. PCR-N is now a named methodology family with sibling-rule visibility benefit (PSQ-N family relationships). Future skills (slice-077's PWA, PCR-2, parallel-slice-family-parity-audit) reference PCR-1 by RULE-ID. The methodology-changelog v0.73.0 entry is load-bearing because future RULE-ID lookups depend on it.
- **Slice-077 / hypothetical PWA-1 would be skill-internal**: the 4-state taxonomy + override-precedence + drift-flag suppression predicate are **consumed only by `/pulse` itself**. No cross-skill ABI. The structural shape (helper module + dataclasses + CLI + tests) coincides with PCR-1's, but the rule-axis content does not. No future skill will look up "PWA-1" by RULE-ID; the `WorktreeState` taxonomy is a /pulse implementation detail.
- **Slice-058 is the closer rule-axis precedent**: ADR-057 (install-wakeup-prompt guardrail) minted an ADR without minting a methodology rule because the guardrail's surface was the INSTALL.md prose + a global CLAUDE.md append — load-bearing for installation but not a cross-skill contract. Same pattern here: ADR-070 captures the design decision without minting a cross-skill rule.

**Concrete EXCLUDE consequences**: no methodology-changelog entry; no PMI-1 bump (5 legs: VERSION + plugin.yaml + pyproject.toml + changelog header + installed ai-sdlc-VERSION all stay at 0.73.0); no paired-pin tests (`test_v_0_NN_0_*_entry_present_in_repo`); no installed-changelog forward-sync (MCFS-1); no installed-VERSION forward-sync (AVFS-1); no installed-tools forward-sync (TVFS-1). Shippability row #77 IS added (BC-PROJ-10 paired-entry-pin discipline is universal per slice-068 + slice-075 MEPD-1-EXCLUDE-vs-shippability-row N=2 — independent axis from methodology-changelog).

**Promotion trigger explicitly noted**: if N=2 cross-skill consumers of the worktree-state classification emerge (e.g., `/drift-check` also needs `WorktreeState`-aware behavior to suppress false positives during `BUILT_BUT_NOT_MERGED` windows; `/build-checks` skips audits unsuitable for worktree-state windows), the convention promotes to PWA-1 (Pulse-Like Worktree-Awareness) on its own methodology axis. Promotion mechanics: PMI-1 5-leg bump + methodology-changelog entry + paired-pin + supersede ADR-070 via new ADR per SUP-1.

**ADR-070 minted regardless of EXCLUDE**: per slice-058 precedent (ADR-057 minted; no rule minted; methodology-changelog unchanged), ADRs and methodology-changelog entries are independent axes. ADR-070 captures the design choice (4-state taxonomy, override precedence, fail-closed UNKNOWN, EXCLUDE rationale with honest precedent inspection) for future maintainers.

## Override-precedence ordering (Step 2 deterministic — applied BEFORE Step 3 Haiku dispatch)

**Location anchor (per /critique M4 ACCEPTED-FIXED)**: the override is computed in `/pulse` Step 2 deterministic metric computation on the main thread; the resolved `recommended_next_action` field is part of the structured-state dict passed to Step 3 Haiku dispatch. Haiku itself does NOT run the override logic — it renders the already-resolved recommendation. Unit tests exercise the Step-2 resolver against synthetic state dicts; no Haiku invocation in tests.

**3-level precedence ordering** (HIGHEST first; the precedence resolver returns the first matching rule):

1. **Worktree-state override** (new in slice-077) — if `any(wt.state == BUILT_BUT_NOT_MERGED for wt in detected_worktrees)`, recommended next action becomes `cd <worktree-path> && /commit-slice --merge`. Supersedes #2 + #3.
2. **CAL-1 cadence-overdue override** (existing per /pulse SKILL.md L86-88) — if /critic-calibrate cadence is `overdue` (>20 slices since last run), recommended next action becomes `/critic-calibrate`. Fires only when #1 doesn't.
3. **Stage-derived next-action** (existing) — read from active-slice `milestone.md` `next-action:` field.

**4 WorktreeState × CAL-1 combinations explicitly enumerated** (per /critique M4 ACCEPTED-FIXED — earlier draft only covered BUILT_BUT_NOT_MERGED + CAL-1):

| WorktreeState observed | CAL-1 cadence-overdue? | Resolved next-action |
|---|---|---|
| `BUILT_BUT_NOT_MERGED` | any | `cd <worktree-path> && /commit-slice --merge` (rule #1 fires) |
| `IN_PROGRESS` | any | `cd <worktree-path> && <stage-derived-next-action from worktree milestone>` (worktree-internal stage advance — rule #1 variant; worktree milestone.md is authoritative) |
| `MERGED` (CLEANUP-CANDIDATE) | overdue | `/critic-calibrate` (rule #2 fires) + sidebar WARN about cleanup-candidate (Drift & flags) |
| `MERGED` (CLEANUP-CANDIDATE) | not overdue | stage-derived (rule #3 fires) + sidebar WARN about cleanup-candidate |
| `UNKNOWN` | overdue | `/critic-calibrate` (rule #2 fires) + WARN about UNKNOWN-state-reason |
| `UNKNOWN` | not overdue | stage-derived (rule #3 fires; main-tree fallback) + WARN about UNKNOWN-state-reason |
| no worktrees detected | overdue | `/critic-calibrate` (rule #2 fires; current behavior preserved) |
| no worktrees detected | not overdue | stage-derived (rule #3 fires; current behavior preserved) |

Rationale: ANY active worktree with milestone-readable stage (`IN_PROGRESS` or `BUILT_BUT_NOT_MERGED`) is a "stuck" state for the next-slice axis — the user is mid-slice and the worktree's stage is authoritative. The override rules #1 + #1-variant collectively mean "if there's a live worktree, recommend continuing IT". `MERGED` is a sidebar concern (cleanup) — doesn't override #2/#3 but adds a sidebar WARN. `UNKNOWN` falls through to existing CAL-1 / stage-derived logic with a WARN about the detection failure.

**Drift-flag suppression predicate** (per /critique B3 ACCEPTED-FIXED — pinned explicitly):

```
def should_suppress_vault_forward_population_flag(detected_worktrees, repo_root) -> bool:
    # Predicate condition #1: at least one BUILT_BUT_NOT_MERGED worktree exists
    if not any(wt.state == BUILT_BUT_NOT_MERGED for wt in detected_worktrees):
        return False
    # Predicate condition #2: ALL of these installed surfaces match the worktree's content
    #                         (content-equal-modulo-EOL per ADR-033 / EOL-DRIFT-1)
    INSTALLED_SURFACES = [
        ("~/.claude/methodology-changelog.md", "<worktree>/methodology-changelog.md"),
        ("~/.claude/ai-sdlc-VERSION",          "<worktree>/VERSION"),
        ("~/.claude/skills/pulse/SKILL.md",    "<worktree>/skills/pulse/SKILL.md"),
    ]
    for installed_path, worktree_relpath in INSTALLED_SURFACES:
        if not content_equal_modulo_eol(installed_path, worktree_relpath):
            return False  # ANY divergence → don't suppress (genuine three-way drift)
    return True
```

Predicate semantics: ALL 3 installed surfaces must match the worktree's content (any-divergence-disqualifies, NOT any-match-suffices — fail-closed against partial-sync). Comparison is **content-equal modulo line endings per ADR-033 / EOL-DRIFT-1** (CRLF↔LF is not drift; matches the surrounding CAD-1 / OSDG-1 byte-equality discipline). Test rows pin both the positive (all 3 match → suppress) and the EOL-tolerance (CRLF↔LF still matches).

When suppression fires, the "vault forward-population" flag is omitted from `/pulse`'s Drift & flags section AND a positive surface is emitted: `ℹ️ Master-vs-installed divergence on changelog/VERSION/SKILL.md is the EXPECTED state during the BUILT_BUT_NOT_MERGED window — run /commit-slice --merge to reconcile.`

## Fail-closed paths summary

Extended per /critique M3 + M6 ACCEPTED-FIXED — earlier draft silently dropped UNKNOWN-state worktrees (problematic during fresh-worktree pre-milestone window which is exactly the slice's witnessed gap); now UNKNOWN surfaces as a one-line WARN in Drift & flags with the specific UNKNOWN-reason, never silently dropped. Branch-name edge cases (no-suffix, drift-after-rename, prunable-stale) explicitly enumerated.

### Detection-side (detect_active_worktrees)

| Failure surface | Fail-closed behavior |
|-----------------|----------------------|
| `git worktree list --porcelain` subprocess failure | `detect_active_worktrees` returns empty list + logs WARN to stderr; `/pulse` falls back to main-tree-only behavior. Drift & flags: `⚠️ Worktree detection failed — git worktree list returned <exit>: <stderr>`. |
| Worktree-list parsing returns unexpected schema | Same as above (warning text: `... parse error: <details>`). |
| Worktree path doesn't exist on disk (stale registration / pruned) | Worktree filtered out + Drift & flags: `⚠️ Worktree <branch> registered but path missing — run \`git worktree prune\` to clean up`. |
| Worktree on `slice/<NNN>` (no `-<name>` suffix; doesn't match `_SLICE_BRANCH_RE` `slice/(\d{3})-(.+)$`) | Filtered out + Drift & flags: `⚠️ Branch \`slice/<NNN>\` lacks canonical \`-<name>\` suffix — BRANCH-2 convention violated`. |
| Worktree on non-`slice/*` branch | Silently filtered out (not in scope; e.g., user's dev/exp branches). |
| Worktree on `slice/NNN-foo` branch but slice folder is `slice-NNN-bar` (rename drift) | Detected; `classify_worktree_state` returns UNKNOWN with reason `slice-folder-name-drift`. |
| `prunable` flag in worktree-list-porcelain output | Filtered out + Drift & flags: `⚠️ <N> prunable worktree(s) detected — run \`git worktree prune\``. |
| Multiple `slice/NNN-<name>` worktrees with same NNN (race / corruption) | All surfaced independently in detect output; `/pulse` lists each with its own classification. |

### Classification-side (classify_worktree_state — all return WorktreeStateClassification with state=UNKNOWN + reason)

| Failure surface | UNKNOWN reason | WARN text in Drift & flags |
|-----------------|----------------|----------------------------|
| Fresh worktree on `slice/NNN-<name>` branch but `architecture/slices/slice-NNN-<name>/milestone.md` doesn't exist yet (worktree created pre-scaffold per BRANCH-2 `git worktree add ... -b <branch> <default>` sequence) | `fresh-worktree-no-milestone` | `⚠️ Worktree <path> on <branch> — no milestone.md yet (slice not yet scaffolded in worktree)` |
| milestone.md missing in both active + archive paths (deleted/renamed) | `milestone-missing-in-active-and-archive` | `⚠️ Worktree <path> on <branch> — milestone.md not found in active or archive` |
| milestone.md frontmatter malformed (no `stage:` field, YAML unparseable) | `milestone-frontmatter-malformed` | `⚠️ Worktree <path> on <branch> — milestone.md frontmatter unparseable` |
| Worktree HEAD detached | `detached-head` | `⚠️ Worktree <path> on <branch> — detached HEAD (mid-rebase or manual checkout?)` |
| Worktree has uncommitted changes (`git status --porcelain` non-empty) | `dirty-worktree` | `⚠️ Worktree <path> on <branch> — uncommitted changes (state classification skipped)`. Note: dirty WT is INFORMATIONAL — does NOT prevent override; the merge command itself will fail until clean. |
| `git merge-base --is-ancestor <worktree-HEAD> <default>` returns unexpected exit code (not 0 or 1) | `merge-base-error` | `⚠️ Worktree <path> on <branch> — git merge-base failed: <stderr>` |
| HEAD-sha unresolvable (rev-parse fails) | `head-unresolvable` | `⚠️ Worktree <path> on <branch> — HEAD sha unresolvable` |
| Slice-folder-name drift (branch `slice/NNN-foo`, folder `slice-NNN-bar`) | `slice-folder-name-drift` | `⚠️ Worktree <path> on <branch> — branch suffix doesn't match slice folder name` |

**UNKNOWN state's override behavior** (per /critique M3 ACCEPTED-FIXED): `UNKNOWN` worktrees do NOT fire override rule #1 (since the classification didn't establish BUILT_BUT_NOT_MERGED or IN_PROGRESS state) — but each is surfaced as a one-line WARN in Drift & flags with the specific reason, NEVER silently dropped. This closes the witnessed-gap class where a fresh worktree pre-milestone would be invisible to /pulse.

## Cross-spec parity with `tools/parallel_conflict_resolver.py` (PCR-1 sibling helper)

Per /critique M7 ACCEPTED-FIXED — explicit so the queued `parallel-slice-family-parity-audit` (slice-queue head) doesn't flag slice-077 as divergent:

| Convention | Value pinned for `pulse_worktree_resolver` |
|------------|--------------------------------------------|
| argparse mode-flag group | `argparse.add_mutually_exclusive_group(required=True)` containing `--detect` + `--classify` (matches PCR-1's `add_mutually_exclusive_group(required=True)` for `--diagnose / --classify / --resolve-soft`) |
| `--repo-root` argument | parse-time: `default=Path(".")`; `type=Path` (matches PCR-1 `parallel_conflict_resolver.py:950`). Post-parse: `args.repo_root.resolve()` at top of `main()` body (matches PCR-1 `L953`). Per /critique-review M-add-1 ACCEPTED-FIXED — earlier draft incorrectly claimed parse-time `Path(".").resolve()`. |
| `--json` argument | `action="store_true"` (matches PCR-1) |
| stdout JSON shape (success) | `{"action": "<detect\|classify>", ...data...}` to stdout (matches PCR-1's `{"action": "<diagnose\|classify\|resolve-soft>", ...}`) |
| stderr JSON shape (error) | `{"action": "<verb>", "error": "<message>"}` to stderr (matches PCR-1) |
| Exit codes | 0 success, 1 runtime error (UNKNOWN classification when explicitly invoked / git failure / parse error), 2 malformed CLI args (matches PCR-1's contract) |
| UTF-8 stdout reconfigure | `tools._stdout.reconfigure_stdout_utf8()` first line of `main()` (matches PCR-1 + UTF8-STDOUT-1 / slice-023 + slice-059 TVFS-1) |
| Module shape | top-level frozen dataclasses + enum + library functions + `def main(argv=None)` + `if __name__ == "__main__": main()` (matches PCR-1) |
| Import discipline | reuses `tools.branch_workflow_audit._resolve_default_branch` for default-branch resolution (single-sourced; PCR-1 has its own equivalent) |

A separate test row (`tests/methodology/test_pulse_worktree_resolver_tool_inventory.py::test_cross_spec_parity_with_parallel_conflict_resolver`) asserts the convention rows above via AST inspection or grep where structurally pinnable.

## Prose-pin test discipline (per /critique M9 ACCEPTED-FIXED — RSAD-1 design-time pre-empt)

Aggregated lessons L77 (slice-075): "For ANY structural-pin test that asserts a literal in prose-as-executable-contract surfaces, the pinned literal MUST be UNIQUE-TO-THE-INVOCATION (not a noun-phrase that appears in informative narration). Tighten to invocation-form (`git checkout $default`), line-start anchor (`^2.1.\s`), or wrapping context (`\nLITERAL\n`). APED-1 against pre-fix AND post-fix prose at design time would catch the build-time + post-finish RSAD-1 sub-class."

Slice-077 anticipates this risk for the new SKILL.md prose tokens. Each prose-pin test must use the specified anchoring strategy:

| Literal | Anchoring strategy | Test rationale |
|---------|-------------------|----------------|
| `git worktree list --porcelain` | invocation-form (the bare verb-flag combination is unambiguous) + line-start `^\s*\|\s*\\\`` (code-fence-bracket boundary) | matches the actual invocation in Step 1 prose, not a discussion reference |
| `BUILT_BUT_NOT_MERGED` | wrapping context: pattern `(?:^\|[^A-Z_])BUILT_BUT_NOT_MERGED(?:$\|[^A-Z_])` OR backtick-wrap `\`BUILT_BUT_NOT_MERGED\`` | distinguishes the canonical state-name from incidental ALL-CAPS prose |
| `pulse_worktree_resolver` (module name) | invocation-form `python -m tools\\.pulse_worktree_resolver` OR import-form `from tools\\.pulse_worktree_resolver import` | matches actual code-equivalents, not module-name discussions |
| `cadence-overdue` | scope to **Step 2 NEW paragraph only** (substring-after-anchor pattern: find Step 2 new-paragraph anchor literal first, then assert `cadence-overdue` within the matched block) — NOT bare substring-presence (would match existing /pulse SKILL.md L88 mention) | distinguishes the new precedence-table mention from the existing CAL-1 override mention |
| `cd <worktree-path> && /commit-slice --merge` | wrapping-context backtick OR code-fence-anchor (literal exists ONLY in the new override-recommendation paragraph) | post-fix-unique by construction |
| `WorktreeState`, `WorktreeStateClassification`, `WorktreeInfo` | invocation-form (typed-signature context) OR import-form | matches actual code-equivalents |

**APED-1-against-pre-AND-post-fix-prose at /design time** (mandatory per slice-074 gold-standard rigor): before /build-slice runs, Builder MUST draft the exact SKILL.md prose insertions AND verify that each pinned anchor-regex above:
1. Returns no match (or expected-existing-only matches) against the **pre-edit** `skills/pulse/SKILL.md` content (verifies TF-1 WRITTEN-FAILING semantics — the test would fail on the unmodified file).
2. Returns the expected post-edit match against the **proposed-but-not-yet-applied** Step 1/2/3 prose (verifies the post-fix anchor is hit).

This APED-1 discipline is captured at the `aped_1_battery.py` artifact + executed at /build-slice Phase B (TF-1 WRITTEN-FAILING verification) AND Phase G (post-fix re-verification).

## Test plan summary

The 7-row test-first plan from mission-brief expands as follows:

- **Prose-pin tests** (`test_pulse_skill_worktree_awareness.py`): assert SKILL.md Step 1 contains `git worktree list --porcelain` literal AND the worktree-milestone read clause precedes (substring-offset) the main-tree milestone read clause; assert Step 2 documents the 3-level override precedence with specific anchor literals (`BUILT_BUT_NOT_MERGED`, `cadence-overdue`); assert Step 3 documents the drift-flag suppression predicate.
- **State-classification unit tests** (`test_classify_worktree_state.py`): each of the 4 `WorktreeState` values has a positive-evidence test (synthetic git fixture; mock `subprocess.run` for `git merge-base --is-ancestor`); UNKNOWN test exercises all enumerated parse-failure paths.
- **Detection unit tests** (`test_detect_active_worktrees.py`): empty list when only main worktree; correct WorktreeInfo when one slice/NNN worktree; multiple slice/NNN worktrees all returned; non-slice/* branch worktrees correctly filtered out.
- **Drift-flag suppression unit tests** (`test_drift_flag_suppression.py`): positive (BUILT_BUT_NOT_MERGED + installed matches worktree → suppress); negative #1 (BUILT_BUT_NOT_MERGED + installed diverges from BOTH worktree AND main → emit flag); negative #2 (IN_PROGRESS state → emit flag if drift exists by other criteria).
- **CLI tests** (`test_cli.py`): `--detect --json` parses; `--classify <slice-NNN> --json` returns expected shape; `--detect` and `--classify` mutually-exclusive; unknown-arg exit 2.
- **Tool-inventory pin** (`test_pulse_worktree_resolver_tool_inventory.py`): assert `pulse_worktree_resolver` is in `_CANONICAL_TOOLS`; `plugin.yaml` tools block; INSTALL.md tool-count `32` at L22 AND L166; `_ROOT_ONLY_TOOLS` set; shippability row #77.
- **APED-1 battery** (`aped_1_battery.py`): **≥13 enumerated cases** across `detect_active_worktrees` + `classify_worktree_state` per /critique M8 ACCEPTED-FIXED — detect {empty / one-slice-worktree / multiple-slice-worktrees / non-slice-branch-filtered / mixed-slice-and-non-slice / stale-prunable} = 6 + classify {IN_PROGRESS / BUILT_BUT_NOT_MERGED / MERGED / UNKNOWN-no-milestone / UNKNOWN-malformed-frontmatter / UNKNOWN-git-merge-base-error / UNKNOWN-head-unresolvable} = 7. Observed-behavior on real synthetic fixtures must match the unit-test expectations (APED-1 catches design→code translation gaps that mock-based unit tests can miss; slice-076 precedent: 28-case battery).
- **CAD-1 / OSDG-1 byte-equality** (`test_pulse_skill_drift.py` — existing): re-verifies post-edit byte-equality of in-repo↔installed `skills/pulse/SKILL.md`.

## Known limitations / out-of-scope (per /critique m2 + m4 dispositions)

- **Active `_index.md` staleness during BUILT_BUT_NOT_MERGED window** (m2 DEFERRED): master's `architecture/slices/_index.md` "Active" table is also stale during the worktree's BUILT_BUT_NOT_MERGED window — the slice has been auto-archived in the worktree's `_index.md` but master still lists it as Active until merge. /pulse's "Total slices" / "Recently shipped" counts may be off-by-one until merge. Surfaced as a known limitation: the **next-action override is the load-bearing path** (correctly recommends `/commit-slice --merge`), and the slice-count cosmetic is informational only. Defer to a future slice if user-reported pain emerges (candidate fix: consult worktree's `_index.md` when BUILT_BUT_NOT_MERGED detected; merge the two Active+Archive tables for display).
- **Worktree-list parser duplication N=3 post-slice-077** (m4 DEFERRED; count corrected per /critique-review M-add-3 ACCEPTED-FIXED): the Python-side `git worktree list --porcelain` parser exists at `tools/slice_queue_writer.py:265` (N=1) + `tools/branch_workflow_audit.py:333+359` (N=2) pre-slice-077; `tools/pulse_worktree_resolver.py` makes N=3 — Fowler's extract trigger. Slice-077 nevertheless DEFERS extraction with honest rationale: extracting in this slice would expand scope to a new shared `tools/_git_worktree_porcelain_parser.py` helper + ≥6 consumer-test updates across all 3 sites, breaching the slice's SMALL effort budget. The queued `parallel-slice-family-parity-audit` (slice-queue head — Phase 1 candidate) is the natural extraction-trigger slice: when it ships, it will already audit all 3 sites for cross-spec parity and the helper extraction folds naturally into that scope. Voluntary-restraint precedent (N=16 cumulative through slice-075) supports defer-with-honest-rationale. Note in ADR-070 § Forward references.
