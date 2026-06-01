# Design: Slice 096 add-slice-candidates-drift-guard

**Date**: 2026-06-01
**Mode**: Standard

## What's new

- `tests/methodology/test_slice_candidates_skill_drift.py` (NEW) — the OSDG-1 per-skill drift guard for `/slice-candidates`: asserts in-repo `skills/slice-candidates/SKILL.md` is content-equal **modulo line endings** to installed `~/.claude/skills/slice-candidates/SKILL.md`. A byte-for-byte clone of the 13 existing per-skill drift tests (the `test_query_design_skill_drift.py` shape), differing only in the skill name + label string. (Count corrected per /code-review m3 — 13 pre-existing per-skill SKILL.md drift guards; the earlier "17" had counted non-per-skill `assert_md_forward_synced` matches — the helper, the normalization test, agent-drift tests.) Closes R-13.
- `CLAUDE.md` (MODIFIED) — the Self-hosting-discipline "Mini-CAD / OSDG-1" bullet's `Guarded skills:` enumeration gains `slice-candidates` + `tests/methodology/test_slice_candidates_skill_drift.py`, so the prose claim and the test reality stay in parity (AC2).
- `architecture/shippability.md` (MODIFIED) — one new catalog row (next free id **102** — row 101 is taken by slice-093 on master; re-confirm `max(existing #-id)+1` at build) registering the guard as a "must never silently regress" claim per RPCD-1 / SCPD-1 (AC4).

## What's reused

- `tests/skill_drift_equality.py::assert_md_forward_synced` — the generic EOL-agnostic forward-sync comparator (EOL-DRIFT-1 / [[ADR-033]]). **Reused as-is, NOT edited** — it takes `(in_repo, installed, label=...)` and is content-agnostic, so a new guarded member is purely a new caller, never a change to the helper.
- `tests/methodology/conftest.py::REPO_ROOT` — the repo-root anchor every per-skill drift test imports.
- The `.gitattributes` `skills/**/SKILL.md text eol=lf` surface (line 8) + `tests/methodology/test_skill_drift_normalization.py::_GUARDED_GLOBS` (`"skills/**/SKILL.md"`) — both already match `skills/slice-candidates/SKILL.md` via the blanket glob, so the CRLF-working-tree guarantee (EOL-DRIFT-1 AC3) already covers this skill. **No change to `.gitattributes` or `test_skill_drift_normalization.py`.**
- OSDG-1 / mini-CAD lineage — [[decisions/ADR-051]] (OSDG-1, slice-049), [[decisions/ADR-033]] (EOL-DRIFT-1), slice-010 MCT-1, slice-007 CAD-1. The CLAUDE.md OSDG-1 note already declares the guarded set **open-ended** ("OSDG-1's 'Opener-Skill' name is now a historical label, NOT a scope boundary"), so adding `slice-candidates` is the rule operating within its documented scope — an extension, not a rule change.
- `skills/slice-candidates/SKILL.md` — the guarded surface. **Not edited**: in-repo and installed copies are already content-equal (EOL-normalized — verified at design time), so no forward-sync reconcile is required and the guard passes against the current tree on day one. This slice only *pins* the current state; it does not change `/slice-candidates`' behavior or the `build_backlog.py` engine.

## Components touched

### `tests/methodology/test_slice_candidates_skill_drift.py` (NEW)
- **Responsibility**: prove the in-repo `/slice-candidates` SKILL.md is forward-synced to its installed copy, so Claude never runs `/slice-candidates` on stale prose — including a silently-weakened "never read source files" read-only invariant (the ADR-054 bounded `--obo-peek` carve-out, the skill's load-bearing safety property). One test function, calling `assert_md_forward_synced` with the slice-candidates paths + `label="skills/slice-candidates/SKILL.md"`.
- **Lives at**: `tests/methodology/test_slice_candidates_skill_drift.py` (created by this slice).
- **Key interactions**: imports `REPO_ROOT` (conftest) + `assert_md_forward_synced` (`tests/skill_drift_equality.py`); reads in-repo `skills/slice-candidates/SKILL.md` + `Path.home()/.claude/skills/slice-candidates/SKILL.md`. Pytest-collected; runs under the `tests/methodology/` suite that `/validate-slice` invokes.

### `CLAUDE.md` (MODIFIED — OSDG-1 enumeration)
- **Responsibility (unchanged)**: project instructions. This slice only extends the OSDG-1 `Guarded skills:` list to name the new member + its test (parity with reality).
- **Lives at**: `CLAUDE.md` Self-hosting-discipline section, the "Mini-CAD / OSDG-1" bullet (~line 42).
- **Key interactions**: human-/Claude-read instruction surface; not installed to `~/.claude` (that is the separate global CLAUDE.md), so no forward-sync obligation on this edit.

### `architecture/shippability.md` (MODIFIED — new row 102)
- **Responsibility (unchanged)**: the single source of truth for "must never silently regress" claims. Gains one row whose Command runs the new drift test.
- **Lives at**: `architecture/shippability.md` (append after current tail row 101 = slice-093; next free `#`-id = **102** as of this review — re-confirm `max(existing #-id)+1` at build, since a 094/095 merge would shift it).
- **Key interactions**: consumed by the shippability runner / catalog audits (`/validate-slice`). The row's Command must be a valid, green pytest invocation (it is — the guard passes against the synced tree). PTFCD-1: the row's cited test path resolves because this slice creates that file in the same build. **SCMD-1 (ADR-031; per /critique-review m-add-1)**: the new row MUST clone row 101's full **6-column** shape — `| # | Slice | Critical path | Command | Runtime | Machine-cmd |` — including BOTH the `Command` cell AND the machine-stable `Machine-cmd` cell (`<interp> -m pytest tests/methodology/test_slice_candidates_skill_drift.py --no-header -q`). `tests/methodology/test_shippability_command_column.py` is a HARD validate-gate that FAILs (`missing-machine-cmd` / `prose-segment`) on a missing or malformed `Machine-cmd` cell.

## Contracts added or changed

None. No endpoints, events, or schemas. The drift guard's only interface is its pytest pass/fail + the `assert_md_forward_synced` AssertionError message (unchanged, inherited from the shared helper).

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_slice_candidates_skill_drift.py` | — | — | internal — rationale: pytest-collected OSDG-1 drift guard; a test module is self-consuming, no downstream module consumer demanded (mirrors all 13 existing per-skill drift tests, e.g. `test_query_design_skill_drift.py`) |

## Decisions made (ADRs)

**None.** No ADR is minted — see the MEPD-1 sub-decision below.

### Sub-decisions (recorded here, not ADR-worthy — anti-pattern to ADR trivial choices)

- **MEPD-1 disposition = EXCLUDE** (no new RULE-ID, no methodology-changelog entry, no VERSION bump, no PMI-1 atomic bump, no INST-1 change, no new ADR). Rationale, three legs:
  1. **No installed artifact.** This slice ships a *test* only — no skill, agent, or `tools/*.py` audit. By slice-094's own MEPD-1 framing (INCLUDE = "a non-underscore PMI-1-enumerated audit tool wired into gates"; EXCLUDE = everything thinner), a test-only change is the EXCLUDE shape. A test is not enumerated in `plugin.yaml` and is not installed to `~/.claude`, so PMI-1 / INST-1 / TVFS-1 have nothing to bump.
  2. **No co-occurring rule event to record** (corrected per /critique M1 — the earlier "member-adds never get a changelog entry" claim was factually false). Prior OSDG-1 member-adds WERE changelog-recorded: slice-051 (reflect) shipped a v0.59.0 entry + ADR-053 + shippability row #51; slice-088 (design-review trio) recorded an "OSDG-1 guarded-set extended" discharge inside its v0.78.0 PFS-1 entry. But in *every* case that entry rode a **co-occurring** rule event — 049 minted OSDG-1; 051 carried ADR-053's "Opener-Skill name → historical label, NOT a scope boundary" semantic re-scope; 088 minted PFS-1. slice-096 carries **no** such co-occurring decision: ADR-053 already decoupled the guarded set from the "Opener-Skill" label, so adding `slice-candidates` exercises *already-settled* scope with no new semantic claim. EXCLUDE is correct because **there is nothing new to record**, not because member-adds are never recorded. Verified against the enforcer: no assertion in `tests/methodology/test_methodology_changelog.py` fires on a missing slice-096 entry, no count-pin exists on the guarded-skill set, and `test_version_files_synchronized_at_v_0_78_0` stays green at 0.78.0 under EXCLUDE (an INCLUDE bump would instead have to supersede that gate).
  3. **Independence is the slice's design constraint** (user-directed "pick next *independent* slice"). A VERSION bump + methodology-changelog entry are exactly the high-contention single-line files that the in-flight slice-094 (INCLUDE, bumps both) and slice-095 also touch; EXCLUDE keeps slice-096 off those collision surfaces. The residual touches (`CLAUDE.md` OSDG-1 paragraph, `shippability.md` append) are the documented additive / PCR-resolvable parallel-safe overlaps, not hard code collisions.
- **shippability row `#`-id at merge — a cheap MANUAL renumber, NOT a silent auto-merge** (corrected per /critique M3). This slice writes the next free `#`-id (**102** as of review) against its base. If slice-094/095/096 each append a *different-content* row at the *same* `#`-id, `_merge_shippability` (`tools/parallel_conflict_resolver.py:1814-1822`) raises `_SoftResolutionError(..., HARD)` and **STOPs** the 2nd/3rd `/commit-slice --merge` — it does NOT silently union (the union keys on the `#`-id integer per `_parse_shippability_rows`, whose docstring mislabels it "slice number" — /critique m2). The *outcome* the design wants (later slices renumber) is right, but the *mechanism* is a one-line manual renumber at merge, not an automatic PCR resolution. Accepted as cheap + expected under the active parallel-slice trajectory (N concurrent slices appending rows is the NORMAL state); build should take `max(existing #-id)+1` at merge time to minimize — not eliminate — the clash window.
- **No `skills/slice-candidates/SKILL.md` edit**: copies are already content-equal, so the slice neither edits the skill nor needs a self-forward-sync. This is what makes the slice touch **zero** files in slice-094's or slice-095's edit sets.

## Authorization model for this slice

Not applicable — test-only methodology tooling, no auth/authz surface. Consistent with the cooperative-not-adversarial model ([[ADR-067]]): a drift guard is a data-integrity / stale-prose control, not a security boundary.

## Error model for this slice

No new error codes. The guard's failure mode is a single `AssertionError` raised by `assert_md_forward_synced`, whose message already names both file paths + both EOL-normalized sha256 hashes + the `label` + the forward-sync fix hint (see `tests/skill_drift_equality.py:72`). The two pre-existing failure branches (in-repo missing / installed missing-with-INSTALL.md-hint) are inherited unchanged.

## Parallel-safety (independence ledger)

| File touched by slice-096 | In slice-094 set? | In slice-095 set? | Overlap class |
|---|---|---|---|
| `tests/methodology/test_slice_candidates_skill_drift.py` (NEW) | no | no | none (brand-new file) |
| `CLAUDE.md` (OSDG-1 enumeration ¶) | no | **no — confirmed via /critique: slice-095's design references no `CLAUDE.md` / OSDG-1 / `slice-candidates`** | none on this ¶ |
| `architecture/shippability.md` (append row, `#`-id 102) | yes (094 appends its VWS-1 row) | yes (095 appends its row) | **cheap manual-renumber merge collision** on the `#`-id surface — `_merge_shippability` HARD-STOPs (`parallel_conflict_resolver.py:1816`) if two in-flight branches append different-content rows at the same `#`-id; resolved by a one-line renumber at the 2nd/3rd merge (see M3 sub-decision). Not a silent union — but cheap + expected under the parallel-slice trajectory |

`/slice-candidates` writes only to `diagnose-out/` (never `architecture/`), so it is categorically outside slice-095's vault-path-targeted skill-write audit — confirming this slice does not pre-empt or duplicate 095's scope.
