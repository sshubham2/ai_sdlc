# Design: Slice 035 rename-status-skill-to-pulse

**Date**: 2026-05-17
**Mode**: Standard

> **Revision 2 (2026-05-17)** — incorporates Critic blockers B1–B5 + majors M1–M3 + minors m1–m2 (ACCEPTED-FIXED). The central correction: distinguish **executable filesystem-path binds** (`(REPO_ROOT/"skills"/"status"/...).read_text()`, path-list constants) from **prose `/status` references** — the former hard-fail the methodology suite on a directory rename and were under-inventoried in revision 1.

## What's new

This slice introduces **one new test function** (the methodology-changelog entry-pin, B4) and is otherwise a pure identifier rename + reference propagation:

- `skills/status/` → `skills/pulse/` (directory rename); `SKILL.md` frontmatter `name: status` → `name: pulse`
- All `/status` self-references inside the skill body rewritten to `/pulse`; colliding triggers `'/status'` and `'project status'` removed; `'pulse'`, `'macro state'`, `'where are we?'`, `'vault scan'` retained
- `plugin.yaml`: `- id: status` → `- id: pulse`; `version: 0.48.0` → `0.49.0`
- `tools/install_audit.py:49` canonical-list `"status"` → `"pulse"`; `:266` `/status` consumer comment → `/pulse`
- **Methodology rule SRCD-1 minted** (B4): `methodology-changelog.md` `## v0.49.0` entry + the **4-part PMI-1 atomic bump** `0.48.0`→`0.49.0` (B-add-1): `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml.version` + this changelog forward-synced to `~/.claude/methodology-changelog.md`
- **New entry-pin test** (B4): `tests/methodology/test_methodology_changelog.py::test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed` following the `test_v_0_48_0_tffl_1` template (`test_methodology_changelog.py:2689-2732`) — bidirectional in-repo + installed assertion of `## v0.49.0`, `SRCD-1`, canonical phrase, `ADR-035`
- **Shippability-catalog row for SRCD-1** (M-add-2): a new `architecture/shippability.md` row pinning `test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed` as SRCD-1's durable regression guard, mirroring the slice-033 EOL-DRIFT-1 (row #33) / slice-034 TFFL-1 (row #34) new-rule catalog-propagation precedent — per project CLAUDE.md RPCD-1/SCPD-1 ("every new audit rule MUST propagate its consumer references into the shippability catalog")
- `architecture/decisions/ADR-035-rename-status-skill-to-pulse.md` (new)

## What's reused

- PMI-1 / INST-1 / CSP-1 audit machinery + `test_methodology_changelog.py` invariants — [[shippability]] catalogs these; no audit logic changes
- [[ADR-030-archive-backtest-verbatim-tracked-corpus]] — governs the frozen fixture corpus this slice MUST NOT touch
- [[ADR-032-query-design-readonly-delegation-only]] — `/pulse` remains an out-of-loop peer (no `## Pipeline position` block), unchanged
- `test_methodology_changelog.py:2689` (`test_v_0_48_0_tffl_1`) — canonical entry-pin template the new SRCD-1 pin mirrors

## Reference taxonomy (the load-bearing distinction — B1/B2)

Every `status`-bearing site is classified into exactly one of three buckets. Builder MUST run the **pre-build inventory grep** below and enumerate every hit into bucket A or B before editing:

```
grep -rn -e 'skills/status' -e 'skills\\status' -e 'skills" / "status"' -e "skills', 'status'" \
        -e '/status\b' -e '"status"' -e 'name: status' -e 'id: status' -e 'test_status' \
   tests/ tools/ skills/ agents/ plugin.yaml *.md architecture/
```

### Bucket A — executable filesystem-path binds (rename or the methodology suite hard-fails)

| Site | Current | Action |
|------|---------|--------|
| `tests/methodology/test_risk_register_audit.py:327` | `def test_status_skill_references_rr_1():` | rename fn → `test_pulse_skill_references_rr_1` |
| `tests/methodology/test_risk_register_audit.py:328,334` | docstring + `(REPO_ROOT/"skills"/"status"/"SKILL.md").read_text()` | repoint path → `"pulse"` (FileNotFoundError otherwise — **B1**) |
| `tests/methodology/test_skill_model_dispatch.py:25` | `"skills/status/SKILL.md",` (COST-1 inventory tuple, iterated + read) | path constant → `"skills/pulse/SKILL.md"` (**B2**) |
| `tests/methodology/test_skill_model_dispatch.py:3` | docstring `/commit-slice, /status, and /archive` | `/status` → `/pulse` |
| `tests/methodology/test_status_cadence_enforcement.py` (file) | filename | rename file → `test_pulse_cadence_enforcement.py` |
| `tests/methodology/test_status_cadence_enforcement.py:14,29,40,60,80,91` | `def test_status_*` (6 fns) | rename all → `test_pulse_*` (**m1** — function-name harmonization in-scope) |
| `tests/methodology/test_status_cadence_enforcement.py:11` | skill-path read | repoint → `skills/pulse/SKILL.md` |
| `tools/install_audit.py:49` | `"status"` canonical-list member | → `"pulse"` |
| `plugin.yaml:65` | `- id: status` | → `- id: pulse` |
| `skills/status/` (dir) | directory | → `skills/pulse/` |

Builder MUST re-run the grep **after** editing and confirm: (1) zero `skills/status` path binds, (2) zero `test_status_` function defs in renamed modules, and (3) **zero `test_status_cadence_enforcement` filename-token citations** anywhere — including `*.md` (m-add-1: `README.md:149` and `methodology-changelog.md:1365` cite the literal old filename; after the file rename they name a non-existent file). The existing predicate's `-e 'test_status'` over `*.md` already reaches these — the requirement is that the post-edit pass treats a surviving filename-token citation as a Bucket-A-class failure, not just `/status`-prose. slice-022 self-violation backstop: this slice's own scope is "complete the inventory," so the real-artifact post-edit grep is the primary catch, not Critic reasoning.

### Bucket B — prose `/status`-skill references (string rewrite `/status` → `/pulse`)

- `tools/install_audit.py:266` consumer comment
- `tools/risk_register_audit.py` L9/L14/L308 docstring consumer refs — **leave artifact `status` field logic L70/L219 untouched**
- `tests/methodology/test_methodology_changelog.py` L89/L111/L450/L517/L582/L827/L924/L1146 (`/status` named as changelog/version consumer in defect-class docstrings)
- `tests/methodology/test_risk_register_audit.py` L10/L12/L59/L72/L99/L212 (RR-1 downstream-consumer prose)
- **`methodology-changelog.md` self-references** (M-add-1 — this file is forward-synced to `~/.claude/`, so a dangling `/status` propagates to the installed copy):
  - `:11-15` `## How /status uses this file` heading + body (3 `/status` refs describing skill runtime behavior) → **REWRITE** — live structural description, same class as `concept.md:46`
  - `:1178` (`Updates skills/status/SKILL.md: surfaces top-3 …`) → **FREEZE-AS-HISTORY** — historical entry-body narrative; rewriting falsifies the record (ADR-035 frozen-as-history class)
  - `:1365` (`**Validation**: tests/methodology/test_status_cadence_enforcement.py …`) → **REWRITE** — live Validation cross-reference cell; the renamed filename makes it a broken pointer if frozen, so update the filename token only (not the surrounding historical prose)
- Cross-docs (in-repo + installed-runtime annotated per **m2**):
  - **Installed-runtime** (forward-sync `~/.claude/` copy too): `methodology-changelog.md`, `templates/milestone.md`, sibling `skills/{triage,slice,reflect,build-slice,commit-slice,query-design}/SKILL.md` next-step refs
  - **In-repo-only** (no installed copy — per `INSTALL.md:146`): `pipeline.md`, `tutorial.md` (L79/L738/L741), `README.md`, `INSTALL.md`
  - **`README.md:149`** (m-add-1): cites the literal filename `test_status_cadence_enforcement.py` in the directory-tree block → rewrite to `test_pulse_cadence_enforcement.py` (filename-token citation, distinct from `/status`-prose; the post-edit grep predicate below is extended to catch it)
- `tutorial-site/Hybrid AI SDLC Pipeline.html` (7 `/status` hits) — see M2 evidence below
- **Vault docs** (M1 — per-file disposition, NOT silently omitted):
  - `architecture/concept.md:46` (`CAL-1 cadence enforcement in /status`) → **REWRITE** — live ISO-42010 architecture description; a dangling `/status` is Dim-7 vault drift
  - `architecture/risk-register.md:170,172` (`/status and /slice read the per-risk status field`; `a future /slice or /status change`) → **REWRITE** — live risk narrative, not ADR-030 corpus
  - `architecture/lessons-learned.md:414` → **FREEZE-AS-HISTORY** — historical reflection text recording what slice-N actually did when `/status` was the name; rewriting falsifies the historical record (same reasoning class as the ADR-030 exclusion). Rationale recorded in ADR-035.

### Bucket C — NOT references to this skill (MUST NOT touch)

- `agents/critique.md` — **NO `/status` skill reference exists** (**B3**). Grep `/status` returns only L194, whose `status` is the FBCD-1/PTFCD-1 *TF-1-row-status* term-of-art ("name-harmonization (TPHD-1), status, and cross-file consistency"), not the skill. `agents/critique.md` is NOT edited by this slice → **CAD-1 is N/A** (no Critic-agent content change → no drift possible). Revision-1's `agents/critique.md:194` citation was false (unverified grep-line propagation) and is removed from scope.
- `tools/cross_spec_parity_audit.py`, `tools/build_checks_integrity.py`, `tools/utf8_stdout_audit.py`, `tools/risk_register_audit.py:70,219` — `status` = dataclass/enum field vocabulary, unrelated to the skill
- `tests/methodology/fixtures/archive_backtest_corpus/slice-004…/design.md`, `…/slice-007…/design.md` — frozen verbatim per [[ADR-030-archive-backtest-verbatim-tracked-corpus]]; historical records of slices that genuinely ran `/status`; rewriting corrupts the backtest baseline
- `build/lib/tools/install_audit.py`, `build/lib/tools/risk_register_audit.py` (**M3**) — pip build artifacts, not source; excluded. Builder MUST verify no audit/drift-check globs `build/` (grep audit tools for `build/lib`); if any does, regenerate `build/` post-rename rather than hand-edit. State the verification in build-log.

## Components touched

### `skills/pulse/SKILL.md` (renamed from `skills/status/SKILL.md`)
- **Responsibility**: project-pulse / macro-state read-only summary — behavior unchanged, identity renamed
- **Lives at**: `skills/pulse/SKILL.md`

### `plugin.yaml` (modified)
- `:65` `- id: status`→`- id: pulse`; `version:` `0.48.0`→`0.49.0` (PMI-1 + `test_plugin_yaml_version_matches_version_file_invariant`)

### `tools/install_audit.py` (modified)
- `:49` canonical-list `"status"`→`"pulse"`; `:266` `/status`→`/pulse` comment

### Test modules — Bucket A renames + Bucket B prose (see taxonomy)
- `test_risk_register_audit.py` (fn rename + path repoint + prose)
- `test_skill_model_dispatch.py` (path constant + docstring)
- `test_status_cadence_enforcement.py` → `test_pulse_cadence_enforcement.py` (file + 6 fn renames + path)
- `test_install_audit.py` (asserts canonical list — `"status"`→`"pulse"`)
- `test_methodology_changelog.py` (Bucket B prose + **new SRCD-1 entry-pin fn**, B4)

### Methodology-changelog 4-part atomic bump (B4 + B-add-1) + shippability row (M-add-2) + ADR-035

## Contracts added or changed

None. `/status`→`/pulse` is a CLI-surface identifier, not a code contract. The **only** added contract-shaped element is the SRCD-1 changelog-entry format obligation (`methodology-changelog.md:24-33`): minted RULE-ID `SRCD-1`, target `v0.49.0`, canonical anti-silent-weakening phrase `user-invocable skill names MUST NOT collide with Claude Code built-in command names`, ADR-035 lineage — pinned by the new `test_v_0_49_0_srcd_1_*` test.

## Data model deltas

None.

## Wiring matrix

Per WIRE-1. The one new test function (`test_v_0_49_0_srcd_1_*`) is itself a consumer test of the changelog entry; it is its own consumer. No new src/ module. Zero-row src matrix = clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-035-rename-status-skill-to-pulse]] — rename `/status`→`/pulse`; no backward-compat alias; SRCD-1 minted; ADR-030 corpus + `architecture/lessons-learned.md:414` frozen-as-history excluded — reversibility: **cheap**

## Authorization model for this slice

N/A — `/pulse` inherits the `/status` read-only invariant verbatim; no authorization surface changed.

## Error model for this slice

No new runtime error codes. The regression guard for a partial/wrong rename is the **post-edit inventory grep (Bucket A must be empty)** + PMI-1 + INST-1 + CSP-1 + the full `tests/methodology/` suite (which now hard-fails on a `skills/status/` path bind via B1/B2 and on a missing SRCD-1 entry-pin via B4). slice-022 self-violation law: the real-artifact grep + suite run, not Critic reasoning, is the structural backstop for this inventory-completeness slice.

## Installed-copy reconciliation (B5 — boundary made coherent)

In-scope, in-slice (required for green pre-finish):
- `~/.claude/methodology-changelog.md` — forward-synced (the SRCD-1 entry-pin test reads `Path.home()/".claude"/"methodology-changelog.md"`; not syncing = AC#4/#5 false)
- **`~/.claude/ai-sdlc-VERSION`** — bumped to `0.49.0` (B-add-1): this is the **installed** leg of the **4-part PMI-1 atomic bump** (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`). Every prior changelog entry documents all four moving in lockstep (`methodology-changelog.md:89,105,121,139,155,179`); omitting the installed `ai-sdlc-VERSION` is the slice-006 DEVIATION-2 / slice-007-B1 recurrence class. Revision-2's "atomic triple" wording was wrong and is corrected to "4-part atomic bump" everywhere.
- `~/.claude/skills/status/` → `~/.claude/skills/pulse/` — renamed for INSTALL.md cp-list parity + to actually resolve the collision in the user's live skill set (cheap; verified `~/.claude/skills/` currently has `status`, no `pulse`). Sibling installed SKILL.md next-step refs forward-synced.

Out-of-scope (genuinely): reconciliation on **other** machines / end-user installs beyond what `INSTALL.md` documents as the install procedure.

## Evidence log (M2 — verification recorded, not asserted)

- **tutorial-site classification**: `ls tutorial-site/` → only `Hybrid AI SDLC Pipeline.html` (no generator, no source `.md`); grep for the filename across `tools/`, `skills/`, repo `*.py` → no generator script. Conclusion: hand-maintained; edit `/status`→`/pulse` (7 hits) in place. (If a generator is later found outside searched roots, regenerate instead.)
- **ADR-030 corpus**: both `tests/methodology/fixtures/archive_backtest_corpus/slice-004…/design.md` and `…/slice-007…/design.md` exist and contain historical `/status` — frozen per ADR-030.
- **CAD-1 N/A**: `grep -n "/status" agents/critique.md` → only L194 (FBCD-1 term-of-art, not skill). No critique.md edit ⇒ no drift.
