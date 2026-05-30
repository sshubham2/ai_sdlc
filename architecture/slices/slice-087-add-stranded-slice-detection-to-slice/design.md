# Design: Slice 087 add-stranded-slice-detection-to-slice

**Date**: 2026-05-30
**Mode**: Standard

> ## ⚠ PARKED — PARALLEL-SAFETY REFRAME REQUIRED BEFORE BUILD (2026-05-30)
>
> **Do NOT `/build-slice` this design as-is.** After `/critique` + `/critique-review` (NEEDS-FIXES, all reconciled), the USER caught a design flaw neither Critic layer reached: the detector as designed **flags ALL unmerged `slice/*` branches + worktrees as "stranded"**, but under the project's parallel-slice execution model (PSQ-1 / PSQ-2 / BRANCH-2) **many concurrent unmerged `slice/*` is the NORMAL state** — so it would cry-wolf on every in-flight parallel slice at every `/slice` open → R-7 silent-disable + undermines the parallel direction. (This motivated the `agents/critique.md` Dim-7 "strategic-direction-fit + architectural-concurrency" probe, committed `64f6ea3`.)
>
> **Required reframe — divergence-based, not existence-based (4-class model):** the detector must CLASSIFY, not flag-all. Stranded = git-unmerged **AND** vault-says-complete (the slice-086 divergence), NOT merely "an unmerged branch exists."
>
> | Class | Condition | `/slice` behavior |
> |-------|-----------|-------------------|
> | **STRANDED-COMPLETE** | git-unmerged AND vault says done (slice in `archive/`, or milestone stage terminal / next-action=commit) | **HALT** (the slice-086 bug) |
> | **ORPHANED** | git-unmerged AND no milestone/vault state at all | **HALT** |
> | **IN-PROGRESS** | vault milestone stage ∈ {slice…validate} (parallel-normal) | informational — **no halt** |
> | **CLAIMED-BY-OTHER** | PSQ-2 `Claimed-by` ≠ my git identity in `slice-queue.md` | informational ("owned by X") — **no halt** |
>
> Only STRANDED-COMPLETE / ORPHANED trip the gate. This means the tool must cross-reference **vault state** (per-slice `milestone.stage` + `archive/` presence) and **PSQ-2 claims** (`slice-queue.md`), not just git — a materially bigger tool than the pure-git design below. **Resume path**: revise design.md/ADR-079/mission-brief around this 4-class model, then re-run `/critique` (the now-direction-aware Critic re-reviews it — Part B's first live test). Everything below this banner is the PRE-reframe (git-only) design and must be reconciled with the 4-class model.

> **Post-critique reshape (B1/M3).** slice-077's `tools/pulse_worktree_resolver.py` ALREADY detects `slice/*` worktrees + runs the merge-base ancestry classification. This slice does NOT re-implement that — it **reuses** it, and its genuine-new value is the bare-unmerged-`slice/*`-branch-WITHOUT-a-worktree case + the `/slice`-open consult (the residual R-22's `/pulse`-only mitigation left open).

## What's new

- **`tools/stranded_slice_audit.py`** — a new read-only git-state detector that **reuses** `pulse_worktree_resolver.detect_active_worktrees` (worktree-stranded side) + `pulse_worktree_resolver._resolve_default_branch` (or `branch_workflow_audit`'s — pick the already-imported one), and ADDS only:
  - **Bare unmerged `slice/*` branches without a worktree** (the genuinely-new case): `git for-each-ref refs/heads/slice/` minus the branches already reported via worktrees → for each remaining, `git merge-base --is-ancestor <branch> <default>` (ancestor ⇒ merged, skip; non-ancestor ⇒ stranded) + ahead-count `git rev-list --count <default>..<branch>`. A per-branch merge-base **error** → that entry is marked `indeterminate` (mirror `pulse_worktree_resolver`'s `merge-base-error` UNKNOWN), NOT a whole-run failure (m2).
  - Output unions worktree-stranded (reused helper) + bare-branch-stranded entries: `{branch, worktree_path|null, ahead, dirty, indeterminate}`. Exit 0 + `status: "clean"` when none; exit 0 + `status: "stranded"` + list when found (advisory — NOT a refuse; **no exit 1**). Exit 2 only on usage failure (git unavailable, default-branch unresolvable, bad root). `--json` + human; accepts `--repo-root` AND a `--root` alias with default-mode = detection so the `_ROOT_ONLY_TOOLS` cp1252 regression genuinely reaches stdout (M2); UTF8-STDOUT-1 compliant (`_stdout.reconfigure_stdout_utf8()` first statement of `main()`).
- **`skills/slice/SKILL.md` Prerequisite-check augmentation** — a strictly-additive sub-section that runs the detector BEFORE Step 1 candidate-gathering and, on `status: stranded`, HALTs with an `AskUserQuestion` structured-options gate (Resume via `/commit-slice` / continue that slice's `/build-slice` / proceed defining a new slice anyway). Proceed-anyway is always offered (advisory, never blocking). On exit 2 (usage), surface the stderr and continue (fail-visible, not fail-silent skip).
- **`skills/pulse/SKILL.md` augmentation** — surface the **bare-branch-without-worktree** stranded signal (the case slice-077's existing worktree block does NOT cover) as a one-line addition, placed so it does NOT perturb `test_pulse_skill_worktree_awareness.py`'s offset/window pins (re-run them after the edit). The `/pulse` OSDG-1 guard is the EXISTING `test_pulse_skill_drift.py` (M4 — NOT the `/slice` drift test).
- **New tests**: `tests/methodology/test_stranded_slice_audit.py` (behavioral, 4 cases) + `tests/methodology/test_slice_skill_stranded_prereq.py` + `tests/methodology/test_pulse_skill_stranded_signal.py` (structural-pin) + `/pulse` OSDG-1 drift test (and reuse the existing `/slice` drift test).
- **`architecture/risk-register.md`**: new **R-26** (mitigating once the detector ships). **`architecture/shippability.md`**: new row.

## What's reused

- **`tools/pulse_worktree_resolver.py` (slice-077) — the primary reuse (B1)**: `detect_active_worktrees(repo_root)` (L275-345, the `git worktree list --porcelain` parse filtered to `_SLICE_BRANCH_RE`) for the worktree-stranded side; `classify_worktree_state` / its `merge-base --is-ancestor` ancestry test (L348-431) as the ancestry reference; its `merge-base-error` UNKNOWN sub-reason (L83/L118) as the per-entry-indeterminate precedent (m2); `_resolve_default_branch`. The new tool ADDS only the bare-branch case + the `/slice`-open consult.
- `tools/branch_workflow_audit.py` — `_SLICE_BRANCH_RE = re.compile(r"^slice/(\d{3})-(.+)$")` (the slice-branch pattern, already shared with pulse_worktree_resolver) and the `stale-slice-branch` warning concept this detector generalizes to open-time.
- `tools/new_agent_warning_audit.py` — the git-subprocess audit shape (argparse `--json`/`--repo-root`, `subprocess.run` error→exit-2, `_stdout.reconfigure_stdout_utf8()`) as a structural model.
- `tools/_stdout.py` — UTF8-STDOUT-1 helper.
- The EXISTING `tests/methodology/test_slice_skill_drift.py` (guards `skills/slice/SKILL.md`) AND `tests/methodology/test_pulse_skill_drift.py` (guards `skills/pulse/SKILL.md`) — reuse both, do not duplicate (M4).
- `tests/methodology/test_pulse_worktree_resolver_tool_inventory.py` — the model for AC#5's inventory-pin test (M1).

## Components touched

### `tools/stranded_slice_audit.py` (created)
- **Responsibility**: read-only detection of stranded prior slice work (unmerged `slice/*` branches + `slice/*` worktrees) so the pipeline can surface git-vs-vault divergence at `/slice` open and `/pulse`.
- **Lives at**: `tools/stranded_slice_audit.py` (new).
- **Key interactions**: `git` subprocess (`for-each-ref`, `merge-base --is-ancestor`, `rev-list --count`, `worktree list --porcelain`, `status --porcelain`); invoked as `$PY -m tools.stranded_slice_audit` from `slice` + `pulse` skill prose. No writes.

### `skills/slice/SKILL.md` (modified)
- **Responsibility**: the `/slice` opener; gains a prerequisite git-state consult.
- **Lives at**: `skills/slice/SKILL.md` — additive sub-section under `## Prerequisite check`, before Step 1.
- **Key interactions**: runs the detector; on stranded → `AskUserQuestion` gate.

### `skills/pulse/SKILL.md` (modified)
- **Responsibility**: macro-state summary; gains a stranded-work line.
- **Lives at**: `skills/pulse/SKILL.md`.
- **Key interactions**: runs the detector; renders its `status` in the summary.

### Installed copies (synced)
- `~/.claude/skills/{slice,pulse}/SKILL.md` — forward-synced after edits so OSDG-1 content-equality holds.

## Contracts added or changed

No code endpoints. The contracts are: (a) the detector's CLI/JSON contract (`status ∈ {clean, stranded}` + per-entry `{branch, worktree_path, ahead, dirty}`, exit 0 advisory / exit 2 usage), and (b) the prose behavioral contract in the two SKILL.md files (consult-at-open + advisory-halt), enforced by structural-pin + OSDG-1 drift tests — the standard SKILL.md enforcement model.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/stranded_slice_audit.py` | `skills/slice/SKILL.md` Prerequisite check + `skills/pulse/SKILL.md` (invoke `$PY -m tools.stranded_slice_audit`) | `tests/methodology/test_stranded_slice_audit.py::test_flags_unmerged_slice_branch` | — |
| `tests/methodology/test_stranded_slice_audit.py` | — | — | `test module — consumer is pytest collection — rationale: behavioral test of the detector, no product consumer demanded` |
| `tests/methodology/test_slice_skill_stranded_prereq.py` | — | — | `test module — consumer is pytest collection — rationale: structural-pin of SKILL.md prereq prose` |
| `tests/methodology/test_pulse_skill_stranded_signal.py` | — | — | `test module — consumer is pytest collection — rationale: structural-pin of pulse signal prose` |

## Decisions made (ADRs)

- [[ADR-079]] — Stranded-slice detection at `/slice` open (+ `/pulse` signal): a read-only git-state detector surfaces unmerged `slice/*` branches + `slice/*` worktrees, advisory-not-blocking; shipped MEPD-1 EXCLUDE (no new RULE-ID, no version bump) — reversibility: **cheap**.

## Authorization model for this slice

N/A — no auth surface. Read-only git inspection.

## Error model for this slice

- Detector: exit 0 (`status: clean|stranded`); exit 2 on usage failure (git binary unavailable, default-branch unresolvable, root not a git repo) with a stderr message (NAW-1 fail-visible precedent). There is **no exit 1** — stranded work is informational, never a hard failure. A single branch's `git merge-base --is-ancestor` **error** (non-zero-non-1) marks that entry `indeterminate` and the run still succeeds (m2; mirrors `pulse_worktree_resolver`'s `merge-base-error` UNKNOWN) — it does NOT escalate to a whole-run exit 2.
- `/slice`: on detector exit 2, surface the stderr and continue (do not silently skip — R-7 silent-disable class); on `status: stranded`, HALT with the structured-options gate.
- **Self-reference / in-flight classification (m-add-1)**: the active slice's OWN `slice/NNN` branch becomes a bare-unmerged-branch-without-worktree after `/commit-slice --push` (awaiting PR) or a `--merge` worktree-remove failure (both live states per risk-register R-22 lineage). The detector flags it stranded — this is **EXPECTED, not a false positive**: the `/slice` gate's Resume / Continue-build options already frame it as resumable. AC4 case (e) pins this. Only `recovery/*`, merged `slice/*`, and the main worktree are true false-positives to exclude.
- **`recovery/*` exclusion mechanism (m-add-2)**: enforced **structurally by the `git for-each-ref refs/heads/slice/` ref-glob** (`recovery/*` lives at `refs/heads/recovery/...`, outside the glob) — NOT a post-filter. The glob is **load-bearing**: widening it to `refs/heads/` would silently reintroduce `recovery/*` false-positives.
- **Orphan ahead-count (m-add-2)**: `git rev-list --count <default>..<branch>` is undefined-symmetric for a branch sharing no merge-base with default; treat a no-common-ancestor branch as stranded with `ahead: null` (distinct from `indeterminate`, which is a merge-base *error*).

## MEPD-1 / rule-footprint note

This slice ships **MEPD-1 EXCLUDE** — no new RULE-ID, no `methodology-changelog.md` entry, no VERSION bump. The on-point structural precedent is **[[decisions/ADR-070]] (slice-077)** — itself a tool-shipping `/pulse` enhancement (`pulse_worktree_resolver.py`) shipped MEPD-1 EXCLUDE — plus the aggregated-lessons "MEPD-1 EXCLUDE for a risk-closing fix-slice with an ADR but no new RULE-ID" (slices 082/077/079, N≥4) (m1). Footprint: the new tool + two SKILL.md edits + tests + ADR-079 + R-26 + the **BC-PROJ-9 5-surface inventory** (below) — which a no-VERSION-bump slice still touches because adding a `tools/*.py` is inventory-independent of a methodology bump.

## Inventory fan-out (BC-PROJ-9 5-surface, M1)

Adding `tools/stranded_slice_audit.py` propagates across all five canonical surfaces (witnessed at slice-077's `pulse_worktree_resolver` row):
1. `plugin.yaml` tools block (PMI-1).
2. `tools/install_audit.py::_CANONICAL_TOOLS` (INST-1).
3. `INSTALL.md` count literal "**33 executable methodology tools**" → 34, at **both** L22 and L166.
4. `tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS` — added, sound because the tool gains a `--root` alias with default-mode = detection so the `[-m tool, --root, REPO]` invocation reaches stdout (M2; avoids the `slice_queue_claim` `--root`-bucketing incidental-pass at L143).
5. `architecture/shippability.md` — new row.

## Self-reference note

This slice edits `skills/slice/SKILL.md` — the very skill currently running to define it. The change is additive (a new prerequisite consult) and monotonically safe; installed-copy sync is atomic at end-of-build so no in-loop re-run sees a half-migrated skill.
