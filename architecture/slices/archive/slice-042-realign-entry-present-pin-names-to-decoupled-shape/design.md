# Design: Slice 042 realign-entry-present-pin-names-to-decoupled-shape

**Date**: 2026-05-18 (rev-1 — post-/critique B1/B2/B3/M1/M2/M3/m1 ACCEPTED-FIXED)
**Mode**: Standard

## What's new

Pure identifier rename — no behavior change, no new modules.

**Single source of truth**: the build-step-1 **pre-edit inventory grep** (rename
map + carve-out snapshot). All counts below are *verified-as-of-2026-05-18* and
**illustrative**; if the build-time grep disagrees, the grep wins and the
narrative is reconciled to it (the slice-035 inventory-grep precedent —
predicates, not hand-typed lists). The slice-041-prose figures (`~33`,
`27-shippability`, `~17 ADRs`) are explicitly **superseded** by the verified
figures here.

### Rename anchor (ADR-044)

A function name is in the rename set iff it matches the regex
`^def (test_\w*_entry_(?:present|names_\w+)_in_repo_and_installed)\b` in an
**active** (non-frozen, see carve-out) `tests/methodology/*.py` file, OR is a
**live non-def** reference to such a name (comment/docstring/string/`::`-selector)
in a LIVE file. The anchor is the literal `_in_repo_and_installed` suffix on the
`_entry_present` / `_entry_names_` family. It MUST catch the no-`_sub_` variant
`test_v_0_36_0_entry_names_three_modes_in_repo_and_installed` and MUST NOT match
the unrelated, still-accurate `test_in_repo_and_installed_<x>_are_content_equal`
CAD-1/mini-CAD family.

### Verified inventory (2026-05-18, rev-2 — recomputed via the authoritative anchor after DR-1 B-add-1/2/3 + m-add-1)

**Canonical anchor (reproducible — NOT hand-transcribed)**:
`A='test_[A-Za-z0-9_]*_entry_(present|names_[A-Za-z0-9_]+)_in_repo_and_installed'`
then `grep -coE "^def ${A}\(" <file>` for defs / `grep -oE "$A" <file> | sort -u | wc -l`
for occ/unique. The figures below are that command's verified output on
2026-05-18; rev-1's hand-corrected figures (67/31, 43, 16-incl-ADR-016/018/031,
_index 4, calibration-log 1) were themselves recompute-don't-trust failures and
are **superseded**. If the build-step-1 grep disagrees, the grep wins.

| Bucket | Surface | Verified count (ADR-044 anchor, 2026-05-18) | Action |
|--------|---------|----------------|--------|
| LIVE — defs | `tests/methodology/test_methodology_changelog.py` `def`s | **37** = 33 `_entry_present` + **4** `_entry_names` (L802/1005/1512/1606) | rename (drop `_and_installed`) |
| LIVE — in-file comments | `test_methodology_changelog.py:1821`, `:2936` | 2 | realign |
| LIVE — sibling test files | `test_critique_agent.py:1426`, `test_methodology_changelog_forward_sync.py:16`, `test_query_design_skill.py:17`, `test_shippability_decoupling_audit.py:57` | 4 (1 each) | realign |
| LIVE — tool source | `tools/methodology_changelog_forward_sync.py:58` (module docstring naming the v0.53.0 pin) | 1 | realign (current source ⇒ must track rename — FBCD-1/RPCD-1) |
| LIVE — catalog | `architecture/shippability.md` | **69 occurrences = 32 unique names (28 `_entry_present` + 4 `_entry_names`) across 28 rows** `[7–27, 30, 32, 35, 37, 38, 39, 41]` | realign every occurrence |
| FROZEN — changelog | `methodology-changelog.md` `## v0.NN.0 **Validation**:` lines | **40 occurrences (32 unique)** | NOT renamed (append-only; forward-synced ⇒ untouched ⇒ no MCFS-1 interaction) |
| FROZEN — ADRs | `architecture/decisions/ADR-*.md` **except ADR-044/045** (predicate) | **13** prior ADR files contain the fn-name family (ADR-009..014, 026, 033, 034, 035, 038, 039, 040). ADR-016/018/031 do **NOT** match the fn-name family (rev-1's claim was false); a few ADRs reference only the bare conceptual substring in prose — all ADRs are FROZEN under the predicate regardless | NOT renamed (append-only) |
| FROZEN — corpus | `tests/methodology/fixtures/archive_backtest_corpus/**` | per pre-edit snapshot | NOT renamed |
| FROZEN — archive | `architecture/slices/archive/**` | per pre-edit snapshot | NOT renamed |
| FROZEN — historical vault prose | `architecture/slices/_index.md` (**3**), `architecture/lessons-learned.md` (**2**) | 5 | NOT renamed (record-of-what-happened, not executable binds) |

`architecture/critic-calibration-log.md` carries **0** fn-name-family references
(rev-1's "1" was false — DR-1 m-add-1); the bucket is dropped.

The 4 `_entry_names_*_in_repo_and_installed` defs (B1): `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_*` (L802), `test_v_0_32_0_tphd_1_entry_names_three_sub_modes_*` (L1005), `test_v_0_35_0_branch_1_entry_names_three_sub_modes_*` (L1512), `test_v_0_36_0_entry_names_three_modes_*` (L1606 — **no `_sub_`, no `_<rule>_` segment**).

## What's reused

- [[slice-041-reframe-installed-pin-forward-sync-invariant]] — the MCFS-1 decoupling (ADR-042/ADR-043) that made the bodies in-repo-only, creating the name↔body drift.
- [[slice-035-rename-status-skill-to-pulse]] — identifier-truth rename precedent: separate **executable-bind** vs **prose/frozen-history** buckets; **grep predicate + pre/post inventory snapshot, not hand-typed lists**; surviving executable bind = Bucket-A hard failure.
- `tests/methodology/test_methodology_changelog.py` — owns all 37 pin defs (bodies unchanged).
- `architecture/shippability.md` — live catalog; `Machine-cmd` `::`-selectors maintained-to-track-reality (precedent: row 7's slice-008 supersession note).

## Components touched

### `tests/methodology/test_methodology_changelog.py` (modified)
37 `def` renames (drop `_and_installed`) + 2 in-file comments (`:1821`, `:2936`). **Bodies NOT modified** — assertions/fixtures/logic unchanged.

### `architecture/shippability.md` (modified)
69 occurrences (32 unique names = 28 `_entry_present` + 4 `_entry_names`, across 28 rows) → new names. Mechanical 1:1 from the rename map; no row added/removed; no command semantics changed. Stale `::`-selector → pytest "no tests ran" → Step-5.5 false-FAIL (R-8 class) — the failure mode this realignment prevents.

### `tools/methodology_changelog_forward_sync.py` (modified — docstring only)
Line 58 module docstring names `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed` as the catalog-row-carrying pin. **Live source** describing the current pin — realigned so source prose matches the renamed fn (leaving it stale would re-introduce the exact name↔reality contradiction this slice removes; FBCD-1/RPCD-1 class). No executable logic in that file references the name (docstring only — verified).

### 4 sibling active test files (modified — descriptive refs only)
`test_critique_agent.py:1426`, `test_methodology_changelog_forward_sync.py:16`, `test_query_design_skill.py:17`, `test_shippability_decoupling_audit.py:57` — one comment/docstring/string each; `:57` is an f-string asserting a shippability `Machine-cmd` literal so it tracks the catalog realignment. Bodies/assertions otherwise unchanged.

## Frozen-history carve-out — stated as a PREDICATE (ADR-045, per B2)

NOT renamed (append-only shipped history / historical record-prose). Defined as a
**predicate + pre-edit snapshot**, not a hand-enumerated list (the list already
drifted — B2):

- `methodology-changelog.md` — all `## v0.NN.0 **Validation**:` family refs (**40** occurrences / 32 unique as of 2026-05-18; forward-synced to `~/.claude/`; untouched ⇒ no MCFS-1 interaction).
- `architecture/decisions/ADR-*.md` — **every file EXCEPT ADR-044 and ADR-045** (the predicate is leak-proof independent of count; **13** prior files contain the fn-name family as of 2026-05-18 — ADR-016/018/031 do NOT, contrary to rev-1). Append-only per CLAUDE.md.
- `tests/methodology/fixtures/archive_backtest_corpus/**` — frozen Critic-backtest corpus.
- `architecture/slices/archive/**` — shipped slice artifacts.
- Historical vault record-prose: `architecture/slices/_index.md` (**3**), `architecture/lessons-learned.md` (2) — these *record what happened*; not executable binds; renaming them would falsify the historical record. (`critic-calibration-log.md` carries 0 family refs — not a bucket.)

**Build-time invariant**: pre-edit, snapshot the FROZEN set's per-file family-ref
count + path list; post-edit, assert byte-identical (count + paths). Any drift in
the FROZEN set = hard STOP. (must-not-defer, mission brief.)

## Out-of-scope sibling family (must NOT be touched — name is accurate)

`test_in_repo_and_installed_<x>_are_content_equal` (CAD-1/mini-CAD drift tests, e.g. `test_query_design_skill_drift.py:12`, `test_slice_skill_drift.py:10`). These genuinely compare in-repo AND installed — `in_repo_and_installed` is *truthful*. The rename regex anchors on `_entry_(present|names_\w+)_in_repo_and_installed` and structurally cannot match `test_in_repo_and_installed_*_are_content_equal` (different lead token). Explicit negative invariant; prime Critic target.

## Wiring matrix

No new modules (pure rename + docstring/catalog realignment). Zero-row matrix — clean by audit.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Contracts added or changed

None. The only preserved invariant: shippability `::`-selectors + the `tools/` docstring stay name-coherent with the renamed defs.

## Data model deltas

None.

## Decisions made (ADRs)

- [[ADR-044]] — rename target + anchor (drop `_and_installed`; literal-suffix anchor incl. the no-`_sub_` `entry_names_three_modes` variant; must not match the CAD-1 family) — reversibility: cheap
- [[ADR-045]] — live-vs-frozen boundary stated as a **grep predicate** (not a hand list); shippability `::`-selectors + `tools/` docstring = LIVE; changelog/ADRs(≠044/045)/fixtures/archive/historical-vault-prose = FROZEN; ADR-044/045's own old-name citations intentionally retained as the rename's canonical record; corrects slice-041 Deferred-L22's "27-shippability frozen" framing — reversibility: cheap

## Methodology-surface obligation (RULE-ID / changelog / PMI-1)

**Verified at /critique against the actual enforcing audits** (not the precedent alone — MEPD-1(b) false-precedent guard satisfied):

- `test_each_changelog_entry_carries_rule_reference` (META-1) is per-`## v`-block and only checks for the literal `Rule reference` line; this slice adds **no** `## v` block → no obligation, and renaming fns while leaving frozen changelog `**Validation**:` lines stale creates **NO** audit failure (META-1 does not cross-check fn names).
- `test_plugin_yaml_version_matches_version_file_invariant` (PMI-1 v1.1) is version-agnostic; a no-VERSION-bump rename is unaffected.
- **Decision**: NO new RULE-ID, NO methodology-changelog `## v` entry, NO VERSION/PMI-1 bump. Identifier-truth conformance correction (slice-035/036/040 conformance-fix class). Recorded in `risk-register.md` + ADR-044/045 only — never a parentless changelog `###` entry.

## Authorization model for this slice

N/A — test/catalog/docstring rename; no runtime authz surface.

## Error model for this slice

No new error codes. Failure mode prevented: stale shippability `::`-selector after rename → pytest collects zero tests → Step-5.5 runner false-FAIL (R-8 class). Mitigated by realigning all 67 LIVE catalog occurrences + the `tools/` docstring in the same fix block + the mid-slice smoke gate.

## Build sequencing (drift-safe order)

1. **Pre-edit inventory grep = single source of truth**: build the exhaustive old→new rename map (regex-anchored, all 37 defs incl. the no-`_sub_` variant) AND snapshot the FROZEN set's per-file count + path list.
2. Rename the 37 defs + 2 in-file comments in `test_methodology_changelog.py`.
3. **Mid-slice smoke gate** (scope = the SOT file ONLY): run `pytest tests/methodology/test_methodology_changelog.py` + assert zero active `_and_installed` residual in it + FROZEN-set snapshot unchanged. STOP on any drift. **Explicitly EXCLUDED from this gate's green-bar claim**: `tools/shippability_path_audit.py` (`missing-test-function` layer, L199-213) and `tools/shippability_runner.py` (`subprocess.run` per row, L144) — between step 3 and step 4 the 69 shippability `::`-selectors still name the old defs while the defs are renamed, so those two consumers are *expected* to be red in this window and are validated only after step 4 (and at step 6 /validate-slice). Per DR-1 m-add-2, do NOT run the full Step-5.5 catalog / path-audit at the mid-slice gate.
4. Realign the remaining LIVE set from the same rename map, atomically before any catalog/path-audit run: `shippability.md` (69 occ / 32 unique / 28 rows) + `test_shippability_decoupling_audit.py:57` + the other 3 sibling files + `tools/methodology_changelog_forward_sync.py:58`.
5. Post-edit invariant (crisp): repo-wide active `_and_installed` family-literal count == **exactly 1** — ADR-044's single documenting example (ADR-045 = 0; all LIVE surfaces = 0; the v0.53.0 `:2936` docstring is rewritten to NOT retain the literal); zero old-name `::`-selector survives in `shippability.md`; FROZEN set byte-identical (per-file count + paths); no orphaned consumer in `tools/**` or other `tests/**` (incl. `shippability_path_audit` / `shippability_runner` now green). The DR-1 m-add / RSAD-1 lesson: a `/critique` fix-prose edit can itself re-introduce a literal (caught at T0 for ADR-045) — the post-edit grep is anchored repo-wide, not per-file.
6. Full methodology suite via `/validate-slice` (VAL-1 + WS-1 + ETC-1 + Step-5.5 catalog) green.
