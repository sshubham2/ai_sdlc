# Design: Slice 074 codify-cp-r-in-branch-2-skill (expanded at /build-slice plan-mode: + switch-commit-switch-worktree codification)

**Date**: 2026-05-28
**Mode**: Standard
**Scope-expansion note**: original slice-074 scope (cp -r codification; AC#1-AC#4) was dual-Critic-cleared in the first /critique + /critique-review pass (CLEAN verdict; 10 dispositions all ACCEPTED-FIXED). The expansion to ALSO codify switch-commit-switch-worktree (AC#5-AC#6) was added at /build-slice plan-mode (user-approved at PCA-1 plan-mode gate). The expansion gets its OWN /critique + /critique-review pass before execution (TRI-1-EXT ratification) — the original AC#1-AC#4 clearance is NOT re-evaluated.

## What's new

**Cp -r codification (original scope; AC#1-AC#4)**:
- 3 new shell lines inside the existing bash codefence at `skills/build-slice/SKILL.md:56-61` (`## Prerequisite check ### Branch state` → numbered point 1 "If on default branch"), placed after `cd "$wt_base/slice-NNN-<slice-name>"`:
  - One `# Seed gitignored derived dirs from main tree (R-20): /diagnose + graphify outputs` comment line (anchors future readers to the codification's origin).
  - Two `if [ -d "$repo_root/<dir>" ]; then cp -r "$repo_root/<dir>" ./; fi` set-e-safe guarded lines, one for `diagnose-out`, one for `graphify-out` (graceful absence handling per AC#2; the `if/then/fi` form chosen over the `[ -d ... ] && cp -r` chained form per /critique m3 — the chained form leaks exit-status 1 on guard-skip and would fail loudly under future `set -e` hardening).
- One new test module `tests/methodology/test_build_slice_skill_cp_r_step.py` (3 structural-pin tests covering AC#1 + AC#2).
- One new test module `tests/methodology/test_r_20_retired.py` (1 audit-runtime test covering AC#4).
- One `architecture/risk-register.md` R-20 entry edit — `**Status**: mitigating` → `**Status**: retired`; append `**Retired**: slice-074-codify-cp-r-in-branch-2-skill (2026-05-28) — candidate fix (a) operationalized; SKILL.md `### Branch state` now contains the codified `cp -r` step.` paragraph after the existing `**Why not Critic-promotion**` paragraph.

**Switch-commit-switch-worktree codification (expansion scope; AC#5-AC#6)**:
- Numbered point 4 in `skills/build-slice/SKILL.md` `### Branch state` ("If working tree is dirty in the main tree") rewritten from the current "STOP, ask user to commit or stash on the main tree. NO auto-stash." STOP-class prose to the canonical 4-step resolution recipe (N=5 cumulative empirical pattern slice-070/071/072/073/074):
  ```bash
  # Canonical switch-commit-switch-worktree sequence for dirty pre-build state on default
  # (N=5 cumulative slice-070/071/072/073/074; canonical origin: slice-070 reflection L127; post-vault-in-git scaffolding-by-design class)
  git switch -c slice/NNN-<slice-name>          # carry dirty state to slice branch
  git add <scaffolding files>
  git commit -m "scaffold(slice-NNN): ..."        # scaffolding commit on slice branch
  git switch "$default"                           # back to clean default
  git worktree add "$wt_base/slice-NNN-<slice-name>" slice/NNN-<slice-name>   # no -b; branch exists
  cd "$wt_base/slice-NNN-<slice-name>"
  ```
- NEW prose paragraph at point 4 explicitly notes the sequence is **NOT idempotent by design** — re-running after a session death mid-scaffolding-commit fails LOUDLY at `git switch -c slice/NNN-<name>` (`fatal: A branch named 'slice/NNN-...' already exists`); recovery is via point 2 ("If the worktree already exists"), NOT silent state re-creation.
- NEW prose paragraph at point 4 explicitly distinguishes the worktree-create form from point 1's: **`-b` is OMITTED at point 4** because the branch already exists (created at point 4's step 1); including `-b` would cause `fatal: A branch named '...' already exists`.
- Per /critique pass-2 m1 ACCEPTED-FIXED: the codified codefence comment includes canonical origin citation — `# (N=5 cumulative slice-070/071/072/073/074; canonical origin: slice-070 reflection L127; post-vault-in-git scaffolding-by-design class)`.
- One new test module `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` (2 structural-pin tests covering AC#5 + AC#6).

## What's reused

- `skills/build-slice/SKILL.md` `### Branch state` sub-section — minted by [[slice-066-add-worktree-per-slice-discipline]] / [[ADR-063]]. This slice extends point 1's bash codefence; the surrounding BRANCH-2 contract (worktree-create + escape-hatch + audit) is unchanged.
- `$repo_root` shell variable assigned at `skills/build-slice/SKILL.md:57` via `git rev-parse --show-toplevel` — re-used as the cp-r SOURCE path (still points at the main tree after `cd` into the worktree, since shell variables are bound at assignment, not re-evaluated against cwd).
- [[architecture/risk-register#R-20]] — R-20 entry's 4-candidate enumeration is the architectural record of WHY candidate (a) was chosen over (b)/(c)/(d); selecting + retiring (a) needs no new ADR.
- `tools/risk_register_audit.py` — already supports `--filter-status retired --json` output; AC#4's test invokes it via subprocess.
- `tests/methodology/test_build_slice_skill_drift.py` — existing OSDG-1 drift guard; will FAIL after SKILL.md edit until installed `~/.claude/skills/build-slice/SKILL.md` is synced. AC#3 verification leverages this existing test, no new test needed.

## Components touched

### `skills/build-slice/SKILL.md` (modified)

- **Responsibility**: documents the /build-slice runtime contract; the `### Branch state` sub-section is the worktree-create prerequisite check that every BRANCH-2 slice executes.
- **Lives at**: `skills/build-slice/SKILL.md` (modified — 3 lines added inside the bash codefence at L56-L61).
- **Key interactions**: read by Claude at /build-slice invocation; mirrored to installed `~/.claude/skills/build-slice/SKILL.md` via INSTALL.md `cp` step (OSDG-1 forward-sync); content-equality verified by `tests/methodology/test_build_slice_skill_drift.py`; structural anchors pinned by `tests/methodology/test_build_slice_skill.py` (unchanged) + the new `test_build_slice_skill_cp_r_step.py`.

### `architecture/risk-register.md` (modified)

- **Responsibility**: tracks all risks across slices; R-20 entry tracks the cp-r tax class.
- **Lives at**: `architecture/risk-register.md` (modified — R-20 entry's Status line + new Retired paragraph).
- **Key interactions**: consumed by `tools/risk_register_audit.py`; the audit's `--filter-status retired` output is the AC#4 verification surface.

### `tests/methodology/test_build_slice_skill_cp_r_step.py` (NEW)

- **Responsibility**: pin the cp -r codification's structural shape against silent regression.
- **Lives at**: `tests/methodology/test_build_slice_skill_cp_r_step.py` (created by this slice).
- **Key interactions**: reads `skills/build-slice/SKILL.md` via `Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"`; 3 test functions (see Test contracts below). Runs in full pytest at /validate-slice + at every pre-commit hook.

### `tests/methodology/test_r_20_retired.py` (NEW)

- **Responsibility**: pin R-20's `retired` status against silent un-retirement.
- **Lives at**: `tests/methodology/test_r_20_retired.py` (created by this slice).
- **Key interactions**: invokes `tools.risk_register_audit` as a subprocess; parses JSON output; asserts `R-20` ∈ `{r.risk_id for r in retired}`. Runs in full pytest.

### `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` (NEW — expansion scope)

- **Responsibility**: pin the switch-commit-switch-worktree codification's structural shape against silent regression. Distinct from `test_build_slice_skill_cp_r_step.py` (separate concern; separate codification surface — point 4 not point 1).
- **Lives at**: `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` (created by this slice's expansion).
- **Key interactions**: reads `skills/build-slice/SKILL.md` via `Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"`; 2 test functions (see Test contracts below). Runs in full pytest at /validate-slice + at every pre-commit hook.

## Contracts added or changed

### SKILL.md `### Branch state` bash codefence (extended contract)

- **Endpoint/event**: not an endpoint — a Claude-runtime contract on the prose shape of `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` numbered point 1 bash codefence.
- **Defined in code at**: `skills/build-slice/SKILL.md:56-64` post-slice (was L56-L61 pre-slice; +3 lines).
- **Auth model**: N/A (Claude executes the prose at /build-slice invocation; no user-level auth at the SKILL surface; OSDG-1 drift guard enforces content-equality between in-repo + installed copies).
- **Error cases**:
  - `$repo_root/diagnose-out` absent on main tree (fresh project, never `/diagnose`'d) → `if [ -d ... ]; then ... fi` guard's then-branch is skipped; line exits 0 (the `if` statement returns 0 when the test is false and no body runs). No `cp` invocation, no error, set-e-safe.
  - `$repo_root/graphify-out` absent on main tree (graph never built) → same `if [ -d ... ]; then ... fi` skip semantics.
  - cp -r into existing worktree dir (resume after session death where the worktree's `diagnose-out/` already exists from a prior cp) → POSIX `cp -r` overwrites file-by-file (idempotent for derived artifacts; the timestamp drift across slices is acceptable since artifacts are regeneratable).
  - `cp -r` failure (disk full, permissions, etc.) — POSIX `cp -r` exits non-zero; bash codefence exits non-zero; /build-slice prereq check fails LOUDLY. No silent swallow.
  - Symlink loops in source — `cp -r` handles per POSIX default (follows symlinks; could trip on circular symlink graphs but neither `diagnose-out/` nor `graphify-out/` contains symlinks in practice — these are graphify + diagnose output dirs with plain JSON / HTML / Markdown files).

## Data model deltas

None. No new entities; no schema changes. The only data-model-shaped edit is R-20's `**Status**` field flip (`mitigating` → `retired`) — see `architecture/risk-register.md:344` post-slice.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0):

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_build_slice_skill_cp_r_step.py` | — | — | `consumer-test is the module itself (structural-pin test on a prose surface; no production code consumes it) — rationale: methodology pin tests are leaves of the test graph by design` |
| `tests/methodology/test_r_20_retired.py` | — | — | `consumer-test is the module itself (audit-status assertion test on a vault file; no production code consumes it) — rationale: methodology pin tests are leaves of the test graph by design` |
| `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` | — | — | `consumer-test is the module itself (structural-pin test on a prose surface; no production code consumes it) — rationale: methodology pin tests are leaves of the test graph by design` |

## Decisions made (ADRs)

**None.** Per MEPD-1 EXCLUDE stance below.

Rationale for not minting a new ADR: R-20's existing risk-register entry enumerates four candidate fix classes (a)/(b)/(c)/(d) with trade-offs explicit. Selecting and operationalizing candidate (a) is captured by the risk-register status flip (`mitigating` → `retired`) + the `**Retired**: slice-074 ... candidate fix (a) operationalized` paragraph + the slice-074 vault folder. An ADR would duplicate the risk-register's already-architectural narrative. The slice-068 / slice-070 / slice-071 EXCLUDE precedent applies (operationalize-existing-rule slices do not mint new ADRs).

If /critique disagrees and demands a new ADR (e.g., to formally close R-20 with full Options-considered context distinct from the risk-register), the cheapest ADR shape would be `ADR-069-codify-r-20-cp-r-fix-class-a.md` with `partial-supersedes: ADR-063` (extending BRANCH-2's prerequisite-check contract with the cp -r step). Builder will accept this in /critique if blocked.

## MEPD-1 stance: EXCLUDE

Per **MEPD-1** (Methodology Entry Predicate Decision; the design-time discipline that determines whether a slice gets a methodology-changelog entry + PMI-1 atomic bump):

**EXCLUDE** — this slice:
- Operationalizes existing R-20 candidate (a); does NOT mint a new methodology rule.
- Adds 3 shell lines to an existing bash codefence in a CAD-1/OSDG-1 guarded SKILL surface; the runtime contract shape (worktree-create → cd → seed-derived-dirs → ready-for-build) is a refinement of BRANCH-2, not a sibling rule.
- Matches slice-068 (VAULT_ROOT constant introduction — MEPD-1 EXCLUDE), slice-070 (PSQ-1 blast-radius dict-leak fix — MEPD-1 EXCLUDE), slice-071 (bundle-066-to-070 code-Critic cleanup — MEPD-1 EXCLUDE) precedent for "refactor / fix / operationalize that does NOT mint a new methodology rule." **Differentiating-axis note** (per /critique M4 ACCEPTED-FIXED): slice-066 amended this SAME SKILL.md `### Branch state` SURFACE and was MEPD-1 **INCLUDE** because it MINTED BRANCH-2 + ADR-063 (new methodology rule, v0.68.0 entry, ADR). slice-074 is EXCLUDE because it operationalizes an existing R-20 candidate without minting a new rule. **The differentiating axis is 'mints-a-new-rule' (slice-066 = yes; slice-074 = no), NOT 'amends-a-CAD-1-surface' (slice-066 = yes; slice-074 = yes; same surface).** Future readers comparing slice-074 to slice-066 precedent on the surface-class axis would get the wrong answer.
- Ships at methodology v0.72.0 unchanged.
- No `## v0.73.0` entry in `architecture/methodology-changelog.md`.
- No 5-part PMI-1 atomic bump (VERSION + plugin.yaml + pyproject.toml + changelog header + installed `~/.claude/ai-sdlc-VERSION` all remain at 0.72.0).
- No BC-PROJ-10 paired-pin obligation (no v0.73.0 entry to pin).
- No `architecture/shippability.md` row #74 addition (paired-pin discipline applies only when a methodology-changelog entry exists; slice-068 EXCLUDE precedent — no shippability row was added for `test_vault_paths_module_is_leaf` either).

The structural-pin tests on SKILL.md prose are protected via TF-1 plan in mission-brief + their presence in `tests/methodology/` (run by full pytest CI). The cp -r prose's content-equality is additionally guarded by OSDG-1 drift test `test_build_slice_skill_drift.py` against the installed copy.

## Bootstrap framing (slice-074 is the bootstrap instance)

Per /critique M1 ACCEPTED-FIXED, mirroring CRP-1 / ADR-024 slice-026 bootstrap exception precedent at `skills/build-slice/SKILL.md:37`:

**Slice-074 cannot self-apply its own codification at its own /build-slice Phase A prerequisite check.** Bootstrap order:

1. `/build-slice` reads the **INSTALLED** `~/.claude/skills/build-slice/SKILL.md` at slice-074 Phase A (prerequisite check). At this moment, the installed copy is still the pre-slice (v0.72.0) prose — the codified `if [ -d ... ]; then cp -r ...; fi` step does NOT yet exist in Claude's reading.
2. The cp -r that runs at slice-074 Phase A is the same MANUAL cp -r that has run at slices 067-073 (R-20 N=8 cumulative). It is NOT a self-application of the newly codified prose.
3. The OSDG-1 forward-sync (Phase B/C) propagates the in-repo SKILL.md edit to the installed copy AFTER Phase A has already completed. By then, prereq check has passed; the codification's runtime exercise window has closed for slice-074.

**Discharge of recursive-self-application for slice-074** (the three things slice-074 IS responsible for proving):

- (a) The in-repo `skills/build-slice/SKILL.md` carries the codified `if [ -d ... ]; then cp -r ...; fi` step in the correct position (3 structural-pin tests in `test_build_slice_skill_cp_r_step.py`).
- (b) The installed copy is byte-equal to the in-repo copy post-forward-sync (`test_build_slice_skill_md_in_repo_byte_equal_installed`).
- (c) R-20 is flipped `mitigating → retired` and the audit reflects it (`test_r_20_status_is_retired_in_risk_register`).

**Canonical first-governed-slice (N+1) demonstration is slice-075's /build-slice Phase A** — at slice-075, the installed SKILL.md carries the codified step (synced at slice-074 Phase B/C), so slice-075 Phase A actually reads + executes the codified `if/then/fi cp -r`. Slice-075's build-log Events line is where R-20's retirement gets its empirical proof point.

**Why this matters for /critique fail-modes**: a Critic comparing slice-074 to slice-040 (N+1 first-governed-slice doctrine — "every new structural rule's N+1 governed slice surfaces structurally-novel edges") might reasonably expect slice-074's Phase A to surface novel edges of the codified step. It cannot — by bootstrap order, slice-074 reads the OLD prose at Phase A. Slice-075 is the actual N+1 first-governed-slice for R-20 candidate (a). Builders maintaining this slice in retrospect should not flag the absent self-application as a defect.

**Phase A/B/C ↔ /build-slice Steps glossary** (per /critique-review m-add-2 ACCEPTED-FIXED): the "Phase A/B/C" terminology above is informal slice-vocabulary borrowed from mission-brief; it maps to canonical `skills/build-slice/SKILL.md` Steps 1-7 as follows:
- **Phase A** = `## Prerequisite check` (the worktree-create + Branch-state sub-section; runs BEFORE Step 1 plan-mode entry).
- **Phase B** = Step 4 task-by-task execution where the Builder edits in-repo `skills/build-slice/SKILL.md` AND cps it to installed `~/.claude/skills/build-slice/SKILL.md` (OSDG-1 forward-sync).
- **Phase C** = Step 6 pre-finish gate where `test_build_slice_skill_drift.py::test_build_slice_skill_md_in_repo_byte_equal_installed` verifies byte-equality between the two copies.

**Sequencing confirmation for slice-075 readiness**: slice-074 Phase B (Step 4 cp-to-installed) + Phase C (Step 6 drift test PASS) + /commit-slice merge ALL complete before slice-075's invocation. By the time slice-075's /build-slice fires Phase A prereq check, the installed `~/.claude/skills/build-slice/SKILL.md` carries slice-074's codified `if [ -d ...]; then cp -r ...; fi` step. Slice-075 is therefore the FIRST slice whose Phase A actually executes the codified prose — the canonical N+1 first-governed-slice demonstration for R-20 candidate (a).

## Test contracts (the structural-pin shape)

Pinned in `tests/methodology/test_build_slice_skill_cp_r_step.py`:

```python
from pathlib import Path
import re

SKILL_PATH = Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"

def _branch_state_section() -> str:
    """Extract '### Branch state' sub-section text up to the next markdown H2 heading.

    Per /critique M2 ACCEPTED-FIXED: the lookahead requires `## ` followed by a
    CAPITAL LETTER (markdown H2-headings convention; shell `## `-prefixed comments
    inside bash codefences are typically lowercase or arbitrary, so capital-letter
    anchor disambiguates section-end from in-fence comments). Do NOT relax to
    bare `(?=^## )` — that misfires on `## `-prefixed shell comments and silently
    truncates the section, masking real prose changes.
    """
    text = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^### Branch state\b.*?(?=^## [A-Z])", text, re.MULTILINE | re.DOTALL)
    assert m is not None, "### Branch state sub-section not found"
    return m.group(0)

def test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd():
    """AC#1: cp -r lines for both dirs present, positioned AFTER the cd line and BEFORE numbered point 2.

    Per /critique M3 ACCEPTED-FIXED: the regex requires the `if [ -d ... ]; then cp -r`
    guard prefix (NOT bare `cp -r [^\n]*<dir>`) to forestall comment-substring leaks
    (a comment mentioning `cp -r diagnose-out` would otherwise satisfy the assertion
    even if the actual functional line were deleted). This cross-pins AC#1 + AC#2 in
    a single regex shape.
    """
    section = _branch_state_section()
    cd_marker = 'cd "$wt_base/slice-NNN-<slice-name>"'
    point2_marker = "2. **If the worktree already exists**"
    cd_idx = section.find(cd_marker)
    point2_idx = section.find(point2_marker)
    assert cd_idx != -1, f"expected cd line {cd_marker!r} missing"
    assert point2_idx != -1, f"expected numbered point 2 marker {point2_marker!r} missing"
    diagnose_pattern = re.compile(r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*diagnose-out', re.MULTILINE)
    graphify_pattern = re.compile(r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*graphify-out', re.MULTILINE)
    diagnose_match = diagnose_pattern.search(section)
    graphify_match = graphify_pattern.search(section)
    assert diagnose_match is not None, "diagnose-out cp -r line missing (or not guarded by `if [ -d ...]; then cp -r` prefix per /critique M3)"
    assert graphify_match is not None, "graphify-out cp -r line missing (or not guarded by `if [ -d ...]; then cp -r` prefix per /critique M3)"
    assert cd_idx < diagnose_match.start() < point2_idx, "diagnose-out cp -r not positioned between cd and point 2"
    assert cd_idx < graphify_match.start() < point2_idx, "graphify-out cp -r not positioned between cd and point 2"

def test_cp_r_lines_reference_r_20_in_comment():
    """AC#1: a comment referencing R-20 is co-located with the cp -r lines (anchors codification origin)."""
    section = _branch_state_section()
    r20_match = re.search(r"#[^\n]*R-20", section)
    assert r20_match is not None, "no R-20 reference comment found in ### Branch state"

def test_cp_r_lines_use_if_then_guard_for_source_dir_absence():
    """AC#2: each cp -r line wrapped in `if [ -d ... ]; then ... fi` POSIX guard (set-e-safe).

    Per /critique m3 ACCEPTED-FIXED: switched from `[ -d ... ] && cp -r` chained form
    to `if [ -d ... ]; then cp -r ...; fi` because the chained form returns exit-status
    1 on guard-skip (would fail loudly under future `set -e` hardening of the codefence).
    The `if/then/fi` form returns 0 when the test is false (no body runs), which is the
    intended graceful-absence semantic.

    Per /critique-review m-add-1 ACCEPTED-FIXED: **single-line `if [ -d ... ]; then ... ; fi`
    form is intentionally pinned** (semicolons + same-line constraint via `[^\\n]*`).
    Multi-line POSIX equivalents — e.g., `if [ -d "$X" ]\\nthen\\n    cp -r "$X" ./\\nfi`
    (no `;` before `then`/`fi`, four lines) — are out-of-scope and will FAIL this test.
    This is by-design per RSAD-1 byte-exact-match discipline (slice-071 M6 prevention
    pattern): the structural-pin asserts the prose's wire-format shape, not its POSIX
    semantic equivalence class. Future Builders refactoring the codefence for
    "readability" MUST preserve the single-line form or update both the prose AND the
    test in the same fix block.
    """
    section = _branch_state_section()
    guard_pattern = re.compile(r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*;\s*fi', re.MULTILINE)
    matches = guard_pattern.findall(section)
    assert len(matches) >= 2, f"expected ≥2 `if [ -d ... ]; then cp -r ...; fi` guarded lines, found {len(matches)}"
```

Pinned in `tests/methodology/test_r_20_retired.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def test_r_20_status_is_retired_in_risk_register():
    """AC#4: risk-register R-20 entry has status: retired (was mitigating pre-slice-074)."""
    proc = subprocess.run(
        [sys.executable, "-m", "tools.risk_register_audit",
         str(REPO_ROOT / "architecture" / "risk-register.md"),
         "--json", "--filter-status", "retired"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=True,
    )
    data = json.loads(proc.stdout)
    risk_ids = [r["risk_id"] for r in data.get("risks", [])]
    assert "R-20" in risk_ids, f"R-20 not in retired risks; got {sorted(risk_ids)}"
```

Pinned in `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` (NEW expansion-scope module):

```python
from pathlib import Path
import re

SKILL_PATH = Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"

def _branch_state_section() -> str:
    """Extract '### Branch state' sub-section text up to the next markdown H2 heading.

    Identical extraction to test_build_slice_skill_cp_r_step.py (per /critique-review
    m-add-2 ACCEPTED-FIXED — single-line constraint pinned via (?=^## [A-Z])).
    """
    text = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^### Branch state\b.*?(?=^## [A-Z])", text, re.MULTILINE | re.DOTALL)
    assert m is not None, "### Branch state sub-section not found"
    return m.group(0)

def _point_4_codefence_body(section: str) -> str:
    """Extract the bash codefence BODY within numbered point 4 ('If working tree is dirty').

    Per /critique pass-2 M1 + M2 ACCEPTED-FIXED (shared mechanism): the upper boundary
    is the codefence close (```) rather than end-of-section. This (a) forecloses M2's
    "future point-5 / WORKTREE=skip paragraph pollutes AC#5 token search" failure mode
    AND (b) forecloses M1's "prose-only narrative without codefence passes AC#5" failure
    mode in a single regex change. The structural-pin asserts the codified contract
    EXISTS as an executable bash codefence (not as a prose paragraph that narrates the
    same tokens). Returns the codefence body (between the opening ```bash and closing
    ```), NOT including the fences themselves.
    """
    m = re.search(
        r"^4\. \*\*If working tree is dirty\b.*?```bash\b(.*?)```",
        section, re.MULTILINE | re.DOTALL
    )
    assert m is not None, (
        "point 4 'If working tree is dirty' does NOT contain a ```bash ...``` codefence — "
        "the switch-commit-switch codification requires the recipe to live in an executable "
        "bash codefence, not as prose narrative (per /critique pass-2 M1 ACCEPTED-FIXED)"
    )
    return m.group(1)

def test_point_4_contains_switch_commit_switch_worktree_sequence_in_order():
    """AC#5: point 4's bash codefence contains the canonical 4-step switch-commit-switch
    sequence in order, plus the scaffold-commit body shape.

    Per slice-074 design.md §'What's new' switch-commit-switch codification: the 5
    ordered tokens that MUST appear in point 4's bash codefence in the canonical order:
        1. `git switch -c slice/` (creates slice branch carrying dirty state)
        2. `git commit -m "scaffold(slice-NNN):` (scaffolding-commit body shape — added
           per /critique pass-2 M1 as the 5th anchor; discriminates "`git commit`
           mentioned in narrative" from "`git commit -m \"scaffold(...)\"` inside the
           codified recipe")
        3. `git switch "$default"` (back to clean default)
        4. `git worktree add` (creates worktree pointing at the already-existing branch)

    Per /critique pass-2 M1 + M2 ACCEPTED-FIXED (shared mechanism): the search scope is
    the bash CODEFENCE BODY (via `_point_4_codefence_body`), NOT the entire point-4
    block. A future Builder who reverts point 4 to STOP-prose while narrating the
    sequence as a paragraph would FAIL this test — the codefence-existence assertion
    fires in `_point_4_codefence_body` before token search runs.

    Per RSAD-1 byte-exact-match discipline (slice-071 M6 prevention pattern): asserts
    LITERAL token presence in ORDER, not POSIX-semantic equivalence. Multi-line equivalent
    forms (e.g., `git switch $default && git worktree add` chained) would FAIL.
    """
    codefence = _point_4_codefence_body(_branch_state_section())
    token_1 = codefence.find("git switch -c slice/")
    token_2 = codefence.find('git commit -m "scaffold(slice-NNN):', token_1 + 1) if token_1 != -1 else -1
    token_3 = codefence.find('git switch "$default"', token_2 + 1) if token_2 != -1 else -1
    token_4 = codefence.find("git worktree add", token_3 + 1) if token_3 != -1 else -1
    assert token_1 != -1, "token 1 (`git switch -c slice/`) missing from point-4 codefence"
    assert token_2 != -1, 'token 2 (`git commit -m "scaffold(slice-NNN):`) missing or out-of-order in point-4 codefence'
    assert token_3 != -1, 'token 3 (`git switch "$default"`) missing or out-of-order in point-4 codefence'
    assert token_4 != -1, "token 4 (`git worktree add`) missing or out-of-order in point-4 codefence"
    assert token_1 < token_2 < token_3 < token_4, (
        f"4 ordered tokens present but out of canonical order: "
        f"got positions [{token_1}, {token_2}, {token_3}, {token_4}]"
    )

def test_both_worktree_create_forms_documented_dash_b_and_no_dash_b():
    """AC#6: both worktree-create forms documented — -b form at point 1, no-b form at point 4.

    Per slice-074 design.md §'What's new' switch-commit-switch codification: a reader
    following the point-4 sequence MUST NOT include `-b` (which would cause `fatal:
    A branch named 'slice/NNN-...' already exists`). The two forms must coexist:
        - Point 1 (new-branch case): `git worktree add ... -b slice/NNN-<slice-name> "$default"`
        - Point 4 (existing-branch case): `git worktree add ... slice/NNN-<slice-name>` (no -b)

    Per /critique pass-2 B1 ACCEPTED-FIXED: the no-`-b` negative lookahead is scoped
    BEFORE the `#` comment delimiter (`[^#\\n]` not `[^\\n]`) so the canonical line's
    trailing explanatory comment `# no -b; branch exists` does NOT falsify the assertion
    via embedded `-b` literal. The `-b\\s` (flag + trailing whitespace) shape is required
    in the negative lookahead so the comment's `-b;` (no trailing space; semicolon
    follows) is unambiguously excluded.
    """
    section = _branch_state_section()
    # Point 1's -b form: explicit -b flag before slice/NNN-<slice-name> branch arg + $default
    point_1_dash_b_pattern = re.compile(
        r'git worktree add[^\n]+-b slice/NNN-<slice-name>[^\n]+\$default', re.MULTILINE
    )
    point_1_match = point_1_dash_b_pattern.search(section)
    assert point_1_match is not None, (
        "point 1's `-b` form `git worktree add ... -b slice/NNN-<slice-name> ... $default` "
        "missing from ### Branch state"
    )
    # Point 4's no-b form: extract from CODEFENCE BODY (per M2 fix) + comment-aware negative
    # lookahead scoped before `#` comment delimiter (per B1 fix) + `-b\s` flag shape required.
    codefence = _point_4_codefence_body(section)
    point_4_no_dash_b_pattern = re.compile(
        r'git worktree add\s+(?!(?:[^#\n]*?)-b\s)[^#\n]*slice/NNN-<slice-name>', re.MULTILINE
    )
    point_4_match = point_4_no_dash_b_pattern.search(codefence)
    assert point_4_match is not None, (
        "point 4's no-`-b` form `git worktree add <path> slice/NNN-<slice-name>` "
        "(without -b flag) missing from numbered point 4's codefence body"
    )

def test_point_4_codefence_does_not_contain_git_stash():
    """AC#5 sub-claim (per /critique pass-2 m2 ACCEPTED-FIXED): point 4's codefence body
    does NOT contain `git stash` — structurally pins the NO-auto-stash discipline that
    mission-brief.md L75 + this slice's out-of-scope section declare in prose.

    Per slice-022 codify-empirical-discipline axis: if a discipline is load-bearing
    enough to declare in out-of-scope, it should be load-bearing enough to pin
    structurally. AC#1's M3 ACCEPTED-FIXED guard-prefix anchor is the precedent
    (discipline-as-regex-anchor rather than prose-only declaration).

    A future Builder who "improves" the switch-commit-switch recipe by inserting
    `git stash` between `git switch -c` and `git commit` would FAIL this test —
    surfacing the silent discipline regression at /validate-slice mid-slice smoke gate.
    """
    codefence = _point_4_codefence_body(_branch_state_section())
    assert "git stash" not in codefence, (
        "point 4's codefence contains `git stash` — but mission-brief.md L75 declares "
        "NO-auto-stash as out-of-scope; the switch-commit-switch sequence MUST require "
        "explicit `git add` + `git commit` of scaffolding, never silent shelve via stash. "
        "Per /critique pass-2 m2 ACCEPTED-FIXED, this structural pin elevates the prose "
        "discipline declaration to a regex-anchor."
    )
```

Test count delta: **+7 NEW tests** (3 cp-r structural-pin + 1 R-20 retired-status + 3 switch-commit-switch structural-pin including the post-/critique-pass-2-m2 NO-auto-stash discipline pin); **8 TF-1 plan rows total** (row 4 = existing `test_build_slice_skill_drift.py::test_build_slice_skill_md_in_repo_byte_equal_installed` re-running against updated prose, no count delta). Expected post-slice pytest count: 995 → **1002** (slice-073 baseline + 7 new). Per /critique m1 ACCEPTED-FIXED + expansion update + pass-2 m2 ACCEPTED-FIXED — the +7-tests-vs-8-TF-1-rows discrepancy is explicit so future readers don't have to cross-grep.

## Authorization model for this slice

N/A. The SKILL.md prose surface has no end-user authorization model — Claude executes the prose as Claude itself at /build-slice invocation. The cp -r is a filesystem operation in the user's own home directory tree; no privileged escalation introduced (cp -r runs as the same user as the /build-slice process).

## Error model for this slice

- `if [ -d "$repo_root/diagnose-out" ]; then cp -r ...; fi` — source-dir-absent → then-branch skipped, line exits 0 (intentional graceful handling per AC#2; set-e-safe per /critique m3 ACCEPTED-FIXED).
- `cp -r` failure (disk full / permissions / read errors) — exits non-zero → bash codefence exits non-zero → /build-slice prereq check fails LOUDLY (no swallow). Recovery: user inspects the cp error, fixes filesystem issue, re-runs /build-slice (the worktree already exists, so the resume path point 2 takes over).
- Worktree's pre-existing `diagnose-out/` (resume scenario) — `cp -r` overwrites file-by-file; semantically acceptable for derived artifacts (timestamp drift across slices is by-design for cache-regen flows).
- Subsequent `/diagnose` runs INSIDE the worktree write to the worktree's `diagnose-out/` (not the main tree's). /commit-slice --merge teardown discards these worktree-local updates. This is consistent with "derived-artifacts-stay-gitignored" (ADR-066) — slices needing /diagnose updates persisted to main are out-of-scope.

## Worktree-vs-main-tree isolation contract (unchanged)

Slice-066 / ADR-063 established that the worktree filesystem is physically isolated from the main tree; uncommitted slice-A WIP on the main tree cannot contaminate slice-B's worktree. This slice's cp -r introduces COPIES (not symlinks / not shared mounts), so isolation is preserved. Each slice gets its own derived-artifact snapshot at /build-slice prereq time; subsequent modifications inside the worktree do not leak back to the main tree.

## Out-of-scope decisions (re-affirmed from mission-brief)

- Candidate (b) symlink discipline — Windows fragility carries through unchanged.
- Candidate (c) un-gitignore derived dirs — violates ADR-066 derived-artifacts principle.
- Candidate (d) auto-cp audit gate — codified prose is sufficient unless empirical refutation surfaces N≥3 additional "I forgot to read SKILL.md" failures.
- Symmetric cp -r in BRANCH-1 fallback path — BRANCH-1 single-tree-only path doesn't have a worktree-vs-main-tree gap.
- Extension beyond `diagnose-out/` + `graphify-out/` — slice-022 "codify exactly what reality has demanded" applies.
