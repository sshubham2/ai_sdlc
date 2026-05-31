---
id: ADR-084
title: stranded_slice_audit surfaces a branchless in-flight slice (untracked slice-NNN folder, no slice/* branch, non-terminal milestone) as a 5th INFORMATIONAL divergence class — never a halt
date: 2026-05-31
slice: slice-092-fix-stranded-audit-branchless-blindspot
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-084: Surface branchless in-flight slices (informational, never-halt)

## Context

`tools/stranded_slice_audit.py` ([[ADR-079]], slice-087) classifies every
**unmerged `slice/*` branch** into a divergence model. Its enumeration has
exactly two sources: (a) branches with a live worktree
(`detect_active_worktrees`) and (b) bare `slice/NNN-<name>` branches
(`git for-each-ref refs/heads/slice/`).

A slice that has been `/slice`+`/design`'d but **not yet branched** — the normal
pre-`/build-slice` state, where the scaffold (`mission-brief.md` +
`milestone.md`, stage pre-`build`) lives untracked in the **main working tree**
with **no** `slice/NNN` ref yet — is therefore structurally invisible.
`classify_branches` returns no entry for it and `compute_status` reports
`clean` (R-31).

This is not hypothetical: it was the slice-090 incident (an in-flight slice-089
sat uncommitted while the consult reported `clean`) and was re-confirmed live at
slice-091/092 definition (both slices sat as untracked folders; the consult
returned `{"status": "clean", "entries": []}`). The consult's `clean` is a
false-reassurance for the branchless case — a new slice can be defined "on top
of" branchless in-flight work without the operator being told.

Crucially, a branchless in-flight slice is **healthy parallel-safe state**, not
a strand. Under PSQ/BRANCH-2 multiple concurrent in-flight slices are normal
(the slice-087 reframe's whole point). So the right fix surfaces the slice
**informationally**, exactly as IN-PROGRESS does — it must never halt `/slice`.

## Options considered

1. **Filesystem-scan the invoking tree for branchless folders, surface as a new
   informational class (CHOSEN)** — after the worktree + bare-branch passes,
   enumerate `architecture/slices/slice-NNN-<name>/` folders in the invoking
   tree, skip any whose `slice/NNN-<name>` ref already produced (or could
   produce) an entry, skip terminal-milestone folders, and emit a non-halting
   `BRANCHLESS_IN_FLIGHT` entry for the rest. *Pros*: closes R-31 with the
   smallest possible surface; reuses `_frontmatter_field` / `_is_terminal`;
   stays within the established advisory-never-blocking contract; no skill-prose
   change (the existing `/slice` consult already proceeds on `status: clean`
   with informational entries). *Cons*: reads the invoking-tree filesystem (not
   git) — but that is exactly where a branchless folder lives, and the tool
   already reads the invoking tree as a secondary fallback in
   `_classify_bare_branch`.
2. **Promote the signal to a halt** — *Rejected*: a branchless in-flight slice
   is healthy parallel work; halting `/slice` over it is the cry-wolf failure
   the slice-087 reframe exists to kill (the rejected Option 4 there). It would
   actively undermine the parallel-slice direction.
3. **Commit the scaffold so it becomes a bare branch the existing path sees** —
   *Rejected*: that changes the methodology's workflow (scaffolds are
   intentionally branchless until `/build-slice` creates the worktree+branch per
   BRANCH-2) to suit the detector. The detector should observe reality, not
   mandate a new commit discipline.
4. **Add an INDETERMINATE folder path for absent/malformed milestones** —
   *Rejected (out of scope)*: a folder with no parseable milestone fails open
   (skipped), consistent with the tool's advisory posture; minting a halt-worthy
   class for a missing milestone would re-introduce cry-wolf.

## Decision

`classify_branches` gains a **third enumeration pass** (after worktree'd and
bare branches) and a **5th divergence class**:

- New `DivergenceClass.BRANCHLESS_IN_FLIGHT = "branchless-in-flight"`, **NOT** in
  `_HALT_CLASSES` (informational, `halt=False`).
- A helper enumerates direct child folders of `architecture/slices/` matching
  `^slice-(\d{3})-(.+)$` (excluding `archive/`). For each folder:
  - **Dedup**: compute the folder key `NNN-name` from the folder regex's CAPTURE
    GROUPS (`f"{num}-{name}"`), NOT a prefix-strip (B2); skip if a `slice/NNN-name`
    ref exists — checked against the full ref set of **both** worktree'd AND bare
    branches (B1: in BRANCH-2 a slice's main-tree folder co-exists with its live
    worktree for the whole in-flight period, so the ref set must include
    worktree'd branches, not only bare ones), so a slice that has BOTH a folder
    AND a branch is reported once, via the branch path.
  - **Precedence subordination (M2)**: branch-derived entries are AUTHORITATIVE;
    the folder pass is strictly subordinate — it emits ONLY for keys absent from
    the full ref set, so it can never downgrade or mask a halt-worthy branch
    classification (preserving ADR-079's load-bearing precedence).
  - Read `milestone.md`. **Absent/unparseable → skip** (fail-open, out of
    scope).
  - **Terminal milestone** (`_is_terminal(stage, next_action)`) → **skip** (it
    is either already merged or a genuine strand the branch path owns; never
    mis-surfaced as in-flight).
  - **Non-terminal → emit** one `BRANCHLESS_IN_FLIGHT` entry. Because no
    `slice/NNN` ref exists, the entry's `branch` field carries the **folder-form
    id** (`slice-NNN-name`, with a hyphen, NOT `slice/NNN-name`) to signal "this
    is a folder, not a branch"; `worktree_path=None`; `vault_state` and `reason`
    name the slice + its stage so `/slice` and `/pulse` can render it.

`compute_status` is unchanged: BRANCHLESS_IN_FLIGHT is not halt-worthy, so a
branchless in-flight slice keeps the run `clean` (parallel-safe). The existing
`/slice` prerequisite consult already proceeds on `status: clean` with
informational entries (surfacing a one-line note), so **no skill-prose change is
required** — the new entry flows through the existing informational path.

This narrows R-31 (it does not mint a new RULE-ID). Ships **MEPD-1 EXCLUDE** (no
`methodology-changelog.md` entry, no VERSION bump) — directly mirroring
[[ADR-079]]'s own EXCLUDE posture for the same tool.

## Consequences

- `tools/stranded_slice_audit.py`: +1 enum member, +1 enumeration pass, +1
  private helper. `classify_branches`'s existing two passes are untouched.
- `DivergenceClass` gains a 5th member; any exhaustive consumer of the enum (the
  JSON `klass` contract) sees a new value — additive, no existing value changes.
- A branchless in-flight folder now appears in `--json` entries with
  `halt=false` and `klass="branchless-in-flight"`; consumers that key on `halt`
  (the `/slice` gate) are unaffected (it never halts).
- **Skill-prose change (real M1)**: `skills/pulse/SKILL.md` enumerates a CLOSED
  klass set — it surfaces `halt: true` klasses as `⚠ stranded` and names
  `in-progress` / `claimed-by-other` as parallel-normal; `branchless-in-flight`
  is in NEITHER, so it would be invisible in `/pulse`. This slice adds a `/pulse`
  render path (parallel-normal situational-awareness note, not a warning) — the
  load-bearing skill edit — plus a documentation-only `branchless-in-flight`
  addition to the `/slice` consult enumeration. Both forward-synced so OSDG-1
  (`test_pulse_skill_drift.py` / `test_slice_skill_drift.py`) stays green. (The
  earlier "no skill-prose change" framing was wrong — `/pulse` documented a
  closed set and could not render the new klass.)
- **Self-surfacing disambiguation (real B1)**: the pass enumerates folders in the
  invoking tree, so it could in principle report the operator's OWN in-flight
  slice. The detector deliberately does NOT learn "which slice is current" (a
  fragile, larger contract). Instead the three runtime contexts are each correct:
  (1) the `/slice` prereq consult runs BEFORE the current slice's folder is
  written (Step 6), so it never self-surfaces and DOES see *sibling* branchless
  slices — the R-31 target; (2) `/build-slice` in a worktree has a `slice/NNN`
  branch, so dedup suppresses its own folder; (3) `/pulse`/manual runs surfacing
  the operator's own branchless slice is *intended* situational awareness, never a
  halt. A future reader must NOT add a blanket "exclude folder == invoking slice"
  filter — it would suppress the legitimate context-3 signal. Pinned by test 4n.
- BC-PROJ-9 inventory fan-out does **not** apply (no new `tools/*.py` module).
- R-31's "branchless blindspot" is closed for the invoking tree. **Residuals:**
  (a) a branchless slice whose folder lives in a *different* worktree than the
  invoking one is not cross-scanned — the same single-tree scope every other
  invoking-tree fallback in the tool already has, out of scope; (b) an
  archived-but-never-branched folder (`archive/slice-NNN-name/` with no `slice/*`
  ref) is surfaced by neither pass (the folder pass scans non-archive only) —
  out of scope; the cooperative model assumes archival follows merge.

## Reversibility

cheap — the change is one enum member, one enumeration pass, and one helper, all
localized to `tools/stranded_slice_audit.py`. Reverting is a mechanical deletion
(re-opening R-31). No external contract, persisted format, or skill prose
changes; the JSON `klass` addition is backward-additive.
