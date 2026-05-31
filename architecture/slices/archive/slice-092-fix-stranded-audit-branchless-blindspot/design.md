# Design: Slice 092 fix-stranded-audit-branchless-blindspot

**Date**: 2026-05-31
**Mode**: Standard

## Project-frame consult (PFS-1, Step 0.5)

Ran `$PY -m tools.project_frame_synth --slice-dir …slice-092…`. Trajectory =
the parallel-slice family (PSQ / BRANCH) plus PCR/PFS/DCE/BCSG. **ATTACK-LENS
verdict: aligned, no tension.** This slice *strengthens* the parallel-slice
direction — it makes branchless in-flight parallel work *discoverable* (the same
goal as the slice-087 stranded detector and PSQ-1's queue), and it does so with
the family's binding constraint intact: **informational, never a halt** (the
slice-087 reframe's whole point). The one place a careless design could fight the
direction is by halting on the branchless signal — explicitly rejected here and
in [[ADR-084]] Option 2.

## What's new

- **`tools/stranded_slice_audit.py`** — extend the classifier with a third
  enumeration pass and a 5th divergence class:
  - New `DivergenceClass.BRANCHLESS_IN_FLIGHT = "branchless-in-flight"` — **NOT**
    added to `_HALT_CLASSES` (informational, `halt=False`).
  - New private helper `_branchless_in_flight_slices(repo_root, all_slice_refs)`
    — enumerate `architecture/slices/slice-NNN-<name>/` folders in the invoking
    tree (exclude `archive/`), dedup against existing `slice/*` refs, skip
    terminal/absent/malformed milestones, emit one `BRANCHLESS_IN_FLIGHT` entry
    per surviving folder.
  - `classify_branches` calls the new pass after the worktree + bare-branch
    passes, passing the **full** `slice/*` ref set (so dedup covers BOTH
    worktree'd and bare branches, not just the bare ones).
- **`tests/methodology/test_stranded_slice_audit.py`** — new cases (4j–4n, see
  Test plan) folded into the existing module (no new test file).
- **`skills/pulse/SKILL.md`** (+ `skills/slice/SKILL.md`) — klass-enumeration
  prose additions (real M1; see §Components touched), forward-synced to installed
  copies.
- **`architecture/risk-register.md`** — R-31 → `mitigating` once shipped.
- **`architecture/shippability.md`** — row #99 already added by `/repro`.

## What's reused

- `tools/stranded_slice_audit.py` internals — `_frontmatter_field` (milestone
  stage/next-action extraction), `_is_terminal` (terminal discrimination —
  reuse verbatim so a `stage: complete` folder is skipped), `_entry`
  (StrandedEntry constructor with `halt = klass in _HALT_CLASSES`),
  `_SLICE_BRANCH_RE` (the `slice/(\d{3})-(.+)` shape, mirrored for the folder
  form `slice-(\d{3})-(.+)`), `_run_git` (the `encoding="utf-8"` git wrapper —
  for the ref-set query).
- The existing `git for-each-ref refs/heads/slice/` query (already run inside
  `_bare_slice_branches`) supplies the ref set for dedup — but see the dedup
  note below: `classify_branches` must surface the **union** of worktree'd +
  bare ref keys, so the dedup set is assembled in `classify_branches`, not
  re-derived inside the new helper.
- [[ADR-079]] — the 4-class divergence model + the advisory-never-blocking
  contract this extends.
- The existing `/slice` prerequisite consult + `/pulse` signal prose handle
  `status: clean` with informational entries (consult surfaces a one-line note
  and proceeds on `status`; `/pulse` renders entry `klass`). **Revised per M4:**
  the `/slice` SKILL.md prose enumerates a CLOSED informational klass set
  (`klass ∈ {in-progress, claimed-by-other}`). Shipping a 5th klass without
  updating it is latent 4-vs-5 contract drift, so this slice **does** add
  `branchless-in-flight` to that prose enumeration (and checks `/pulse`),
  forward-syncing the installed copy so OSDG-1 content-equality holds. This is a
  scope addition vs the original "no skill edit" claim — see §Components touched
  and the M4 disposition in critique.md.

## Components touched

### `tools/stranded_slice_audit.py` (modified)
- **Responsibility**: classify unmerged `slice/*` branches AND now branchless
  in-flight slice folders into the divergence model, so `/slice` and `/pulse`
  see in-flight parallel work whether or not it has been branched yet.
- **Lives at**: `tools/stranded_slice_audit.py`.
- **Key interactions**: adds a read of the invoking tree's
  `architecture/slices/` directory listing + per-folder `milestone.md` read
  (via existing `_frontmatter_field`); reuses the `git for-each-ref` ref set for
  dedup. No new git subprocess kinds; no writes.

### `skills/pulse/SKILL.md` (modified — load-bearing, real M1)
- **Responsibility**: the `/pulse` macro-state surface; its stranded-signal prose
  enumerates which klasses to render. Extended to recognize `branchless-in-flight`
  as a parallel-normal informational class (surfaced as a situational-awareness
  note, NOT a `⚠` warning) so branchless in-flight work is visible — closing the
  must-not-defer #5 `/pulse` half.
- **Lives at**: `skills/pulse/SKILL.md` (stranded-signal section, the
  informational/parallel-normal klass enumeration ~L39).
- **OSDG-1**: edit is content-synced to `~/.claude/skills/pulse/SKILL.md` at
  end-of-build; the existing `test_pulse_skill_drift.py` content-equality test
  stays green after sync, and `test_pulse_skill_stranded_signal.py` gains an
  assertion that the new klass name is present.

### `skills/slice/SKILL.md` (modified — documentation-only, real M1)
- **Responsibility**: the `/slice` opener's stranded-consult prose; gains
  `branchless-in-flight` in its informational-klass enumeration so the documented
  contract matches the tool's 5-klass JSON. NOT load-bearing (the consult branches
  on `status`, not the specific klass), but kept in sync to avoid 4-vs-5 doc drift.
- **Lives at**: `skills/slice/SKILL.md` (stranded-slice consult, `status: clean`
  informational branch).
- **OSDG-1**: content-synced; `test_slice_skill_drift.py` stays green after sync.

## Contracts added or changed

- **JSON `klass` enum** gains a 5th value `"branchless-in-flight"`
  (backward-additive — no existing value changes). The new entry carries
  `halt=false`, `worktree_path=null`, `ahead=null`, and `branch` = the
  **folder-form id** `slice-NNN-name` (hyphen, to distinguish from a
  `slice/NNN-name` branch ref). `vault_state` = `"folder:<stage>"`; `reason`
  names the slice + stage.
- **`compute_status` contract unchanged**: BRANCHLESS_IN_FLIGHT ∉ `_HALT_CLASSES`
  ⇒ does not make a run `divergent`. A repo with only branchless in-flight
  slices stays `clean`.
- **Behavioral contract** (pinned by tests): a non-terminal branchless folder is
  surfaced exactly once; a folder that also has a `slice/*` branch is reported
  once (via the branch path, not double); a terminal folder is not surfaced as
  in-flight; a repo with no slices stays empty/clean.

## Data model deltas

None. The detector reads existing vault/git state; it persists nothing.

## Dedup design (the load-bearing detail — must-not-defer #1)

The new pass must not double-report a slice that has BOTH a folder AND a matching
`slice/*` branch. **Folder location is NOT assumed (real M-add-1).** Where a
branched slice's `architecture/slices/slice-NNN-*/` folder physically lives
relative to a given invoking tree is context-dependent under BRANCH-2: for a
branchless pre-build slice the folder is in the main tree (the R-31 target, where
slice-091/092 sit today); for a built-in-worktree slice the folder lives in the
worktree (and never on `master` — verified: `git ls-tree -d master
architecture/slices/` returns ONLY `archive`; merged slices move to `archive/`,
so zero non-archive folders ever live on `master`). The dedup is therefore
written to be correct **regardless of which tree the folder lives in** — it
suppresses any folder whose `NNN-name` key matches a `slice/*` ref, in whatever
tree `classify_branches` scans. Mechanism:

1. In `classify_branches`, after the worktree + bare passes, assemble
   `seen_keys: set[str]` from BOTH ref sources with the EXACT construction (B2):
   ```python
   seen_keys = (
       {b[len("slice/"):] for b in worktree_branches}              # full slice/NNN-name refs
       | {f"{num}-{name}" for (_branch, num, name) in bare_tuples}  # bare (branch,num,name)
   )
   ```
   `worktree_branches` holds full `slice/NNN-name` refs (slicing the `"slice/"`
   prefix yields `NNN-name`); the bare set yields `(branch, num, name)` tuples
   (build `f"{num}-{name}"`). Do NOT derive the worktree key from `wt.slice_name`
   alone — that is the **bare name without the `NNN-` prefix**
   (`pulse_worktree_resolver.WorktreeInfo.slice_name = m.group(2)`), which would
   mis-key and double-report. Key derivation is regex-CAPTURE, never a
   `slice/`/`slice-` prefix-strip (the prefixes coincide at 6 chars only by
   accident). (Refactor `_bare_slice_branches` so its `(branch, num, name)` tuples
   are available here rather than re-querying git.)
2. `_branchless_in_flight_slices` receives `seen_keys` and skips any folder whose
   `f"{num}-{name}"` key (from the folder-form regex `^slice-(\d{3})-(.+)$`
   capture) is in it.

**Precedence subordination.** Branch-derived entries are AUTHORITATIVE; the folder
pass is **strictly subordinate** — it emits ONLY for keys absent from the full ref
set, so it can never downgrade or mask a halt-worthy branch classification
(preserving ADR-079's load-bearing precedence).

**Test rigor for the dedup (real M-add-1).** The worktree-branch dedup is
load-bearing ONLY when a folder AND its matching `slice/*` ref are both visible to
a single `classify_branches` invocation. The dedup test MUST construct that
coexistence explicitly and **invoke from the tree where the folder actually lives**
— NOT rely on the `classify_branches(repo)`-from-main-root idiom, which would pass
vacuously (zero BRANCHLESS because the folder was never scanned, not because dedup
fired). Test 4n places the folder in the invoking tree, creates the matching
`slice/NNN` branch/worktree, invokes `classify_branches` against THAT tree, and
asserts exactly one IN-PROGRESS entry AND zero BRANCHLESS_IN_FLIGHT — so the dedup
is genuinely exercised, not trivially satisfied.

## Self-surfacing disambiguation (real B1)

The pass enumerates branchless folders in the **invoking tree**, so it could in
principle report the operator's OWN in-flight slice. Three runtime contexts, three
correct behaviors — stated explicitly so the detector never cry-wolfs the
operator's own work (the Dim-7(b) class the slice-087 reframe exists to prevent):

1. **`/slice` prereq consult (the R-31 target) — timing-safe.** The consult runs
   BEFORE Step 1 candidate-gathering; the current slice's folder is not written
   until Step 6. So at consult time the tool **cannot** see its own
   not-yet-created folder, and DOES correctly see *sibling* branchless slices
   (slice-091 when defining slice-092 — exactly R-31). No self-surface here.
2. **`/build-slice` in a worktree — dedup-safe.** The worktree's own slice has a
   `slice/NNN` branch, so the dedup above (keyed correctly per B2) suppresses its
   own folder. Pinned non-vacuously by test 4n (per the M-add-1 rigor above).
3. **`/pulse` / manual runs after the folder exists but before branching —
   intended.** Surfacing the operator's own branchless in-flight slice is *correct
   situational awareness*, NOT cry-wolf — it is informational, never a halt.

The detector deliberately does NOT learn "which slice is current" (a fragile,
larger contract); contexts 1–2 are handled structurally (consult-ordering +
dedup) and context 3 is correct-by-design. A future reader must NOT add a blanket
"exclude folder == invoking slice" filter — it would suppress the legitimate
context-3 signal.

## Wiring matrix

This slice introduces **no new module** (it extends an existing tool) and **no
new test file** (cases fold into the existing
`tests/methodology/test_stranded_slice_audit.py`). Zero-row matrix — clean per
WIRE-1.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Test plan (folded into `tests/methodology/test_stranded_slice_audit.py`)

The AC1 behavioral repro already lives at
`tests/bugs/test_stranded_audit_branchless_slice_blindspot.py` (WRITTEN-FAILING).
Additional cases pin the contract edges:

All AC2–AC4 cases are authored **WRITTEN-FAILING before** the implementation edit
(TF-1 genuineness, real M2) and carry `assert len(...) == 1` where they pin
exactly-one (so a double-report fails loudly, not silently):

- **4j — branchless surfaced**: an untracked `slice-NNN-name/` folder, non-terminal
  milestone, no `slice/NNN-name` branch → **exactly one** entry,
  `klass=BRANCHLESS_IN_FLIGHT`, `halt=False`, `compute_status=="clean"`, AND
  `vault_state.startswith("folder:")` naming the stage (m1 pin).
- **4k — dedup vs branch (BOTH variants, real B2)**: a slice with BOTH a folder
  AND a `slice/*` branch — run once with a **worktree'd** branch and once with a
  **bare** branch → reported exactly once (via the branch path), zero
  BRANCHLESS_IN_FLIGHT entry for it. The worktree'd variant is the one B2's
  key-mismatch would break.
- **4l — terminal folder skipped**: a branchless folder whose milestone uses the
  PRODUCTION terminal vocabulary (`stage: complete` / `next-action: none (slice
  complete)` — the exact pair from `test_complete_stage_bare_branch_is_stranded_complete`,
  not a synthetic stage) → NOT surfaced as in-flight (zero BRANCHLESS_IN_FLIGHT).
- **4m — absent/malformed milestone fails open**: a branchless folder with no
  `milestone.md` (or unparseable frontmatter) → skipped, no entry, no raise. Also
  pin that a stray non-conforming dir/file (`slice-bad`, `_index.md`) is skipped.
- **4n — invoking-slice self-folder not double-surfaced (real B1 + M-add-1)**: a
  worktree's own foldered+branched slice, with the folder placed in the invoking
  tree AND `classify_branches` invoked against THAT tree (NOT the main-root
  idiom — see §Dedup design test-rigor) → exactly one IN-PROGRESS entry, zero
  BRANCHLESS_IN_FLIGHT. This exercises the dedup non-vacuously (the context-2
  guarantee).
- **4o — stage-less-but-parseable milestone (real m-add-2)**: a folder whose
  `milestone.md` has well-formed frontmatter but NO `stage:` field
  (`_frontmatter_field → None`) → MUST NOT emit a `vault_state="folder:None"`
  entry. Per §Error model it is skipped (treated as incomplete/unparseable); the
  test asserts no entry naming that slice carries `folder:None`.
- **regression**: `test_clean_when_no_slice_branches` (no folders, no branches →
  empty/clean) and `test_in_progress_parallel_slice_does_not_halt` (the binding
  parallel-safety pin) stay green.

## Decisions made (ADRs)

- [[ADR-084]] — Surface branchless in-flight slices as a 5th INFORMATIONAL
  divergence class (`branchless-in-flight`, never-halt); MEPD-1 EXCLUDE — extends
  [[ADR-079]]. reversibility: **cheap**. (Updated post-critique: states the
  folder pass is strictly subordinate to branch classification; records the B1
  self-surfacing disambiguation rule; names the archived-but-never-branched-folder
  residual.)

## OSDG-1 note (post-critique, real M1)

This slice edits TWO skill surfaces: `skills/pulse/SKILL.md` (load-bearing — adds
the `branchless-in-flight` render path, real M1) and `skills/slice/SKILL.md`
(documentation-only klass-enumeration sync). Both edits are additive and
content-synced to the installed copies at end-of-build, so the existing
`test_pulse_skill_drift.py` + `test_slice_skill_drift.py` content-equality guards
stay green. `test_pulse_skill_stranded_signal.py` gains a presence assertion for
the new klass. No NEW drift test module is minted (existing guards cover it).

## Authorization model for this slice

N/A — read-only git/vault inspection, inherits ADR-079's cooperative trust model
(any local write to the slice folder / milestone can spoof state; not defended
against a hostile local actor — same boundary as the rest of the tool).

## Error model for this slice

- The new pass is fail-open on a per-folder basis: a folder with an absent or
  unparseable `milestone.md` is skipped (NOT an INDETERMINATE halt — minting a
  halt for a missing milestone would re-introduce the cry-wolf the slice-087
  reframe killed; out of scope per [[ADR-084]] Option 4).
- **Stage-less-but-parseable milestone (real m-add-2)**: a `milestone.md` with
  well-formed frontmatter but no `stage:` field yields `_frontmatter_field → None`
  and `_is_terminal(None, …) → False`, so it would otherwise emit an entry with
  `vault_state="folder:None"` — naming no stage, violating must-not-defer #5's
  observability requirement. **Decision**: treat stage-`None` as the
  incomplete/unparseable case and **skip it** (same fail-open path as an absent
  milestone) — a folder we cannot describe by stage is not surfaced. (Build may
  instead emit a defined sentinel like `folder:unknown` if a visible-but-vague
  signal is judged more useful than silence; either is acceptable — the literal
  `None` is not. Pinned by test 4o.)
- No new exit codes; no new whole-run failure modes. The directory read is
  wrapped so a missing `architecture/slices/` directory yields zero folders (not
  a raise), preserving the advisory-never-blocking contract.
- `compute_status` semantics unchanged: only the three existing halt classes
  drive `divergent`.

## MEPD-1 / rule-footprint note

MEPD-1 **EXCLUDE** — no new RULE-ID, no `methodology-changelog.md` entry, no
VERSION bump. Directly mirrors [[ADR-079]] (slice-087), the same tool's own
EXCLUDE posture, and the aggregated-lessons "MEPD-1 EXCLUDE for a risk-narrowing
fix-slice with an ADR + no new RULE-ID" pattern (077/079/082/084/085/086/087,
now N≥7). No BC-PROJ-9 inventory fan-out (no new `tools/*.py` module; the tool
already exists in every inventory surface).

## Self-reference note

This slice DOES edit `skills/slice/SKILL.md` (the running skill) and
`skills/pulse/SKILL.md` — both additive klass-enumeration syncs (see §Components
touched, real M1). The `/slice` edit is documentation-only (the consult branches
on `status`, not the specific klass), so it is monotonically safe and the
installed-copy sync is atomic at end-of-build; no in-loop re-run sees a
half-migrated skill. Edited code: `tools/stranded_slice_audit.py` + its test
module + the two SKILL.md surfaces. (Dogfooding, now a designed property not just
irony: this very `/slice`→`/design` run produced the branchless slice-092 folder
the fix surfaces — and per §Self-surfacing disambiguation the `/slice` consult's
BEFORE-Step-1 timing means it correctly sees the *sibling* slice-091, not itself.)
