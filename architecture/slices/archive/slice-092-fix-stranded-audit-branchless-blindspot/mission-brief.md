# Slice 092: fix-stranded-audit-branchless-blindspot

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-31 — `stranded_slice_audit` cannot see branchless (uncommitted-working-tree) in-flight slices; the branch-only enumeration reports `status: clean` while a `/slice`+`/design`'d-but-not-branched scaffold sits in the main tree (the slice-089/090/091 false-all-clear class).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`stranded_slice_audit.classify_branches` enumerates only worktree'd branches (`detect_active_worktrees`) and bare `slice/NNN-*` branches (`for-each-ref refs/heads/slice/`). A slice that has been `/slice`+`/design`'d but **not yet branched** — the normal pre-`/build-slice` state, where the scaffold (`mission-brief.md` + `milestone.md`, stage pre-`build`) lives untracked in the main working tree with NO `slice/NNN` ref — is structurally invisible. The consult returns a false `clean`, so a new slice can be defined "on top of" an in-flight branchless slice without the operator being told. This slice teaches the detector to ALSO enumerate branchless in-flight slice folders and surface them as **informational** entries (NOT a halt — same cooperative parallel-safety posture as ADR-079).

## Acceptance criteria

1. The failing repro test `tests/bugs/test_stranded_audit_branchless_slice_blindspot.py` PASSES at slice end (BFRD-1 mandatory).
2. `classify_branches` surfaces a branchless in-flight slice — an `architecture/slices/slice-NNN-<name>/` folder present in the invoking tree whose `milestone.md` exists and is NON-terminal AND which has **no** matching `slice/NNN-*` branch (neither worktree'd nor bare) — as exactly one entry, deduplicated against the branch-derived entries (a slice that already has a `slice/*` branch is NOT double-reported).
3. The new entry is **informational only** (`halt=False`); it does NOT change `compute_status` away from `clean`, preserving the ADR-079 cooperative model (a branchless in-flight slice is healthy parallel-safe state, never a `/slice` halt).
4. No regression: the existing `tests/methodology/test_stranded_slice_audit.py` suite (4a–4i, incl. the binding `test_in_progress_parallel_slice_does_not_halt` parallel-safety pin and `test_clean_when_no_slice_branches`) and the `/slice`+`/pulse` prereq drift tests stay green; a branchless folder whose milestone is **terminal** (`stage: complete` / `next-action` ~ commit) is NOT mis-surfaced as in-flight.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0) — the AC1 repro is already WRITTEN-FAILING (established by `/repro` before this slice).

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | bug-repro | tests/bugs/test_stranded_audit_branchless_slice_blindspot.py | test_branchless_in_flight_slice_is_surfaced_informationally | PASSING |
| 2 | unit | tests/methodology/test_stranded_slice_audit.py | test_branchless_in_flight_slice_is_informational_status_clean | PASSING |
| 2 | unit | tests/methodology/test_stranded_slice_audit.py | test_branchless_slice_not_double_reported_when_bare_branch_exists | PASSING |
| 2 | unit | tests/methodology/test_stranded_slice_audit.py | test_branchless_dedup_against_worktree_branch_is_non_vacuous | PASSING |
| 3 | unit | tests/methodology/test_stranded_slice_audit.py | test_branchless_in_flight_slice_is_informational_status_clean | PASSING |
| 4 | regression | tests/methodology/test_stranded_slice_audit.py | test_branchless_terminal_folder_not_surfaced_as_in_flight | PASSING |
| 4 | regression | tests/methodology/test_stranded_slice_audit.py | test_branchless_absent_or_malformed_milestone_and_stray_dirs_fail_open | PASSING |
| 4 | regression | tests/methodology/test_stranded_slice_audit.py | test_branchless_stageless_milestone_emits_no_folder_none | PASSING |

(All AC2–AC4 cases (4j–4o) were folded into the existing `tests/methodology/test_stranded_slice_audit.py` — no new test file; function names finalized at `/build-slice` per TPHD-1. 4n is the non-vacuous worktree-key dedup pin — verified by temporarily mutating the `seen_keys` worktree-key derivation to the bare-name mis-key, confirming 4n FAILED `2 == 1`, then reverting.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Repro passes | `$PY -m pytest tests/bugs/test_stranded_audit_branchless_slice_blindspot.py -q` → 1 passed |
| 2 | Branchless surfaced + dedup | Unit: an untracked `slice-NNN-*` folder with no `slice/*` branch yields exactly one informational entry; a folder that DOES have a `slice/*` branch is reported once (via the branch path), not twice |
| 3 | Informational, status clean | Unit: the branchless entry has `halt=False` and `compute_status` stays `clean` |
| 4 | No regression | `$PY -m pytest tests/methodology/test_stranded_slice_audit.py tests/methodology/test_slice_skill_stranded_prereq.py tests/methodology/test_pulse_skill_stranded_signal.py -q` green; terminal branchless folder not mis-surfaced |

## Must-not-defer

- [ ] **Dedup against the branch-derived entries** — a slice with both a folder AND a `slice/*` branch (the post-`/build-slice` state) must be reported once, not twice. Conflating the two is the trap to avoid.
- [ ] **Informational, never a halt** — the new class/flag must NOT be in `_HALT_CLASSES`; a branchless in-flight slice keeps `compute_status` == `clean` (ADR-079 cooperative model, NOT a security boundary).
- [ ] **Terminal-folder discrimination** — reuse `_is_terminal` / `_frontmatter_field` so a leftover terminal (`stage: complete`) folder is not mis-surfaced as in-flight (it is either already merged or a genuine strand the branch path owns).
- [ ] **Encoding discipline** — any new git/file read passes `encoding="utf-8"` (BC-PROJ-15 / cp1252 class); reuse existing `_run_git` / `_frontmatter_field` rather than re-implementing.
- [ ] Observability: the new entry's `reason`/`vault_state` must name the branchless slice + its stage so the `/slice` consult and `/pulse` signal can render it.

## Out of scope

- Promoting the branchless signal to a **halt** — it stays informational by design (ADR-079 cooperative model). A future slice could revisit if a halt is ever wanted.
- Detecting branchless slices whose `milestone.md` is **absent/malformed** beyond the existing `_frontmatter_field` None-handling — fail-open (skip), consistent with the tool's advisory-never-blocking posture; no new INDETERMINATE class for the folder path.
- Changing the `/slice` prereq-consult or `/pulse` rendering PROSE beyond what's needed to surface the new informational entry (the consult already handles `status: clean` informational entries per the slice-087 contract) — unless `/design-slice` finds a real gap.
- R-31's sibling concerns in other tools (none currently open) — this is `stranded_slice_audit.py`-scoped.

## Dependencies

- Prior slices: [[slice-087-add-stranded-slice-detection-to-slice]] — this extends its `classify_branches` enumeration with the branchless-folder path; reuses `_frontmatter_field` / `_is_terminal` / `_bare_slice_branches` / `_entry`.
- Failing repro (BFRD-1): `tests/bugs/test_stranded_audit_branchless_slice_blindspot.py::test_branchless_in_flight_slice_is_surfaced_informationally`
- Vault refs: [[risk-register#R-31]], [[decisions/ADR-079]]
- Code: `tools/stranded_slice_audit.py` (`classify_branches` L336, `_bare_slice_branches` L224, `DivergenceClass` L84, `_HALT_CLASSES` L92, `_is_terminal` L177)
- Parallel sibling: slice-091 (`harden-pcr-decode-non-silent`) — DISJOINT blast radius (`tools/parallel_conflict_resolver.py`); NON-OVERLAPPING, safe to build concurrently.

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m pytest tests/bugs/test_stranded_audit_branchless_slice_blindspot.py tests/methodology/test_stranded_slice_audit.py -q
```
Expected: the repro now PASSES and ALL pre-existing 4a–4i cases (especially `test_in_progress_parallel_slice_does_not_halt` and `test_clean_when_no_slice_branches`) still PASS. If `test_clean_when_no_slice_branches` breaks: STOP — the branchless path is over-firing (a repo with no slices must still be clean/empty).

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints

## Branch / worktree note

Per BRANCH-2 + memory `next-slice-use-worktree-not-skip`: this slice MUST run in a real BRANCH-2 worktree at `/build-slice` (`git worktree add ... -b slice/092-fix-stranded-audit-branchless-blindspot <default>`) — **no `WORKTREE=skip`**. It is a deliberate parallel sibling of slice-091; both build in isolated worktrees on disjoint blast radii. NOTE for `/build-slice`: the AC2 dedup logic must enumerate folders in the worktree's own tree, and the repro fixture builds a synthetic repo (tmp_path) so it is worktree-agnostic.
