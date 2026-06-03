# Design: Slice 108 add-fbcd-1-cardinality-fanout-sub-mode

**Date**: 2026-06-03
**Mode**: Standard (thin vault — reference code locations, no `components/`/`contracts/` files)

## Intent recap

Apply the ACCEPTED `/critic-calibrate` Proposal 1 (run 2026-06-03, post-slice-107): extend the existing **FBCD-1** sub-clause (Dimension 9 of `agents/critique.md`) with a **sub-mode (c)** that makes the design-Critic grep the WHOLE repo for sibling hard-count pins when a slice changes a counted set's cardinality — closing the AP-10 fan-out blind spot (slices 089/100/103/106). Per the locked MEPD-1 decision, this ships as a **versioned refinement (FBCD-1 v1.1)**, mirroring CCC-1 v1.1 / BC-1 v1.2 — i.e. WITH the full PMI-1 version-bump cascade, not a bare prose edit.

## What's new

- **`agents/critique.md` Dim-9 FBCD-1 sub-clause** — a new **sub-mode (c) "Counted-set cardinality fan-out across repo-wide hard-count pins"** inserted after sub-mode (b) (currently L196), plus a **clause (1b)** appended to FBCD-1's closing "When reviewing…" instruction (currently L198). Exact content in §"Sub-mode (c) content" below.
- **`methodology-changelog.md`** — a new top entry `## v0.83.0 — 2026-06-03` recording **FBCD-1 v1.1**, with a `**Rule reference**: FBCD-1 (v1.1) + META-2 + CCC-1` line (so `test_each_changelog_entry_carries_rule_reference` passes). NO new `-D` rule-ID is minted — lineage preserved, exactly like CCC-1 v1.1 (v0.24.0) / PTFFD-1's in-place refinement precedent.
- **`tests/methodology/test_methodology_changelog.py`** — a new entry-pin test `test_v_0_83_0_fbcd_1_v1_1_entry_present_in_repo` (mirrors `test_v_0_24_0_ccc_1_v_1_1_entry_present_in_repo`). **[M1] Per the slice-039 content-pin discipline (`test_critique_agent.py:1201-1206`) + the CCC-1 template's third substantive assert (`test_methodology_changelog.py:221`), this entry-pin MUST assert a SUBSTANTIVE content phrase, not presence-only** — it asserts the v0.83.0 entry contains ALL of: `## v0.83.0`, `FBCD-1 (v1.1)`, `Rule reference`, AND the substantive phrase **`Counted-set cardinality fan-out`** (so a presence-only pin that greens regardless of the entry's actual semantics is impossible). AND the rolling version-sync test renamed `test_version_files_synchronized_at_v_0_82_0` → `_at_v_0_83_0` (L5496): **[M2] sweep ALL `0.82.0`→`0.83.0` literals in the function body — grep-verified 12 occurrences across the 4 leg asserts + docstring, NOT just "4 legs"** — update the predecessor-bump docstring line `0.81.0 → 0.82.0 (slice-105)` → `0.82.0 → 0.83.0 (slice-108)`, and append `108` to the rename-precedent chain (`…/099/105` → `…/099/105/108`).
- **`tests/methodology/test_critique_agent.py`** — a new regression pin `test_critique_dim_9_fix_block_completeness_names_cardinality_fanout_sub_mode` (extends the existing FBCD-1 body-bound cluster) asserting both the sub-mode (c) heading anchor AND the slice-091 count-arithmetic boundary clause are present in the FBCD-1 body.
- **`architecture/shippability.md`** — one new catalog row **#114** for the sub-mode (c) regression test; AND row **#75**'s command repointed `..._at_v_0_82_0` → `..._at_v_0_83_0` (both the `<HOME>` Command cell and the `<interp>` Machine-cmd cell).

## What's reused

- The existing **FBCD-1** sub-clause (minted slice-024, methodology-changelog v0.38.0, [[ADR-022]]) — this slice refines it in place; no new dimension, no new rule-ID.
- **CAD-1** content-equality audit `tools/critique_agent_drift_audit.py` — gates that in-repo `agents/critique.md` ≡ installed `~/.claude/agents/critique.md` (EOL-agnostic per [[ADR-033]]).
- The **PMI-1 version-bump cascade** machinery + the **slice-105 version-bump-obligations build-check** (`tests/methodology/fixtures/build_checks/canonical_project_checks.md` L257–262) — the authoritative checklist this slice executes (see §"Version-bump cascade").
- The **CCC-1 v1.1 / BC-1 v1.2** versioned-refinement precedent + their entry-pin tests as the template for the v0.83.0 entry-pin.
- The accepted **Proposal 1** text in `architecture/critic-calibration-log.md` (run 2026-06-03) as the canonical source of the sub-mode (c) wording.

## Components touched

### `agents/critique.md` (modified) — the design-Critic agent prompt
- **Responsibility**: the 9-dimension adversarial Critic prompt; Dim-9 carries the codified `-D` sub-clauses.
- **Change**: insert sub-mode (c) into the FBCD-1 sub-clause + clause (1b); no other dimension touched.
- **Forward-sync**: edit in-repo FIRST → copy to `~/.claude/agents/critique.md` SECOND → CAD-1 audit THIRD (must-not-defer ordering).

### `methodology-changelog.md` (modified) + `~/.claude/methodology-changelog.md` (forward-synced) — MCFS-1
- **Change**: prepend the `## v0.83.0` FBCD-1 v1.1 entry; mirror to the installed copy.

### Version surfaces (modified) — PMI-1 atomic 5-part bump 0.82.0 → 0.83.0
- `VERSION`, `plugin.yaml:15` `version:`, `pyproject.toml:20` `version =`, `~/.claude/ai-sdlc-VERSION` (AVFS-1), `methodology-changelog.md` header (above). Then `pip install --upgrade .` so the installed `ai-sdlc-tools` dist matches (TVFS-1).

### `tests/methodology/test_methodology_changelog.py` (modified)
- Add `test_v_0_83_0_fbcd_1_v1_1_entry_present_in_repo` (asserts the substantive phrase `Counted-set cardinality fan-out` + `FBCD-1 (v1.1)` + `Rule reference`, not presence-only); rename the rolling version-sync test + sweep all 12 `0.82.0` literals (4 asserts + docstring) + the `0.81.0→0.82.0` predecessor line + append `108` to the precedent chain.

### `tests/methodology/test_critique_agent.py` (modified)
- Add the sub-mode (c) regression pin; update the now-stale intra-file count-claims (see §"Self-application sweep").

### `architecture/shippability.md` (modified)
- New row #114; repoint row #75's version-sync citation.

## Contracts added or changed
None — no endpoints, events, or integrations. Pure methodology-surface + test change.

## Data model deltas
None.

## Wiring matrix

Per **WIRE-1**: this slice introduces **no new modules** (it edits existing `.md` prose, extends existing test files, and bumps version literals). Zero-row matrix → clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Sub-mode (c) content (the exact prose to add to FBCD-1)

Insert after FBCD-1 sub-mode (b). **[m1] Tighten the FBCD-1 intro so the count is unambiguous** — change `Two distinct sub-modes covering the temporal axis:` → `Three sub-modes — two on the temporal axis ((a)/(b)) plus one on the orthogonal SCOPE axis ((c)):` (no literal "two" count left sitting above three bullets). Then insert (c):

> - **Sub-mode (c) Counted-set cardinality fan-out across repo-wide hard-count pins** (a third sub-mode, on the SCOPE axis rather than the temporal axis of (a)/(b)) — first-Critic catch at /critique time, scope EXPLICITLY BROADER than (a)/(b)'s `{mission-brief, design, ADR, milestone}` slice-authoring file-set. When a slice's design declares a change to the **cardinality of a counted set** (adds/removes the Nth member of a tool inventory, migration-allowlist, importer set, cp1252-coverage list, AC count, sub-clause/sub-mode count, or any enumerated collection), the obvious membership-set-equality pin the slice directly edits is NOT the only hard-count pin: independent `== N` / `len(...) == N` / `"N-element"` / `"set to N"` / INSTALL.md count literals for the SAME set routinely live in sibling test files (`tests/**/test_*_inventory.py`, `tests/methodology/test_*.py`) and non-test surfaces (`INSTALL.md` count lines, design prose count-narratives). The Critic MUST grep the WHOLE repo (not just the slice-authoring file-set) for every hard-count literal referencing the changed set, enumerate every site, and verify each is updated in lockstep — OR flag a slice plan that enumerates only the membership pin as a Major. Concrete misses (all caught only by the full suite, never by any Critic layer): slice-089 (INSTALL.md L22/L166 + two `*_tool_inventory.py` `35` literals + cp1252 parametrize list); slice-100 (2 per-tool inventory-pin tests); slice-103 (6 inventory-pin tests tripped by one new tool); slice-106 (the 2nd VAULT_ROOT-importer `== N` pin in `test_external_vault_adr_and_risk.py` while the allowlist membership pin WAS enumerated — AP-10). **Boundary**: a count whose correct post-change value depends on **new runtime behavior not yet a static literal** (e.g. slice-091's decode-count offset, where a new helper's own `git rev-parse` is itself a decode site) is OUT of this static sub-mode — that is APED-1 "execute the count-pin against the built code," routed to the mid-slice-smoke / BC-PROJ-4 backstop, not a static grep.

And append to the closing "When reviewing…" instruction, clause (1):

> …; **(1b) when the slice declares a counted-set cardinality change (sub-mode c), extend the grep beyond the slice-authoring file-set to the WHOLE repo — every `== N`, `len(...) == N`, "N-element", "set to N", and INSTALL.md count literal referencing that set — and enumerate every site**; …

(The FBCD-1 closing note's `-D`-rule-ID enumeration — "N=7 stable (RSAD-1 + EPGD-1 + …)" — is a count of RULE-IDs, NOT sub-modes; adding sub-mode (c) mints NO new rule-ID, so that enumeration is unchanged.)

## Self-application sweep (RSAD-1 + dogfood of sub-mode (c) itself)

This slice changes FBCD-1's sub-mode cardinality 2 → 3, so it MUST itself pass the very rule it adds. Enumerated count-claim sites for FBCD-1's sub-mode count (grep `"sub-mode"` / `"Two sub-modes"` / `"not three"` scoped to the edit surface):

1. `agents/critique.md` — the FBCD-1 intro is UPDATED (m1) `Two distinct sub-modes covering the temporal axis:` → `Three sub-modes — two on the temporal axis ((a)/(b)) plus one on the orthogonal SCOPE axis ((c)):`, so no literal "two" count sits above three bullets; (c) is the third bullet.
2. `tests/methodology/test_critique_agent.py` — **TWO** factually-stale "not three like RPCD-1" count-claim sites (both surfaced by this section's own `grep "not three"` recipe), both updated **[meta-Critic m-add-1]**: (i) the section comment `# … Two sub-modes (not three like RPCD-1) given FBCD-1's …` (≈L840–841); AND (ii) the `_names_both_sub_modes` test **docstring** clause at ≈L901–902 (`two sub-modes given FBCD-1's … evidence base, not three like RPCD-1`). Both become FALSE once (c) ships (FBCD-1 then HAS three sub-modes) → reword each to a three-sub-mode-accurate phrasing. The `_names_both_sub_modes` function NAME is left UN-renamed deliberately (a rename would trip SCPD-1 consumer-propagation into shippability) and its ASSERTS are unchanged (they check (a)+(b) presence via `in body`, confirmed L916–923, so leaving them is correct); the new `_names_cardinality_fanout_sub_mode` test pins (c). No test asserts either prose site as a pinned string (grep-confirmed), so both edits are safe.
3. **Confirm NOT tripped**: any Dim-9 *sub-clause*-COUNT pin (historical `_lists_N_sub_clauses` shape). Adding a sub-MODE does NOT add a sub-CLAUSE, so the sub-clause count is unchanged — verify by grep at build (this is the boundary that keeps the change bounded). If a sub-clause-count pin exists and is unaffected, record that in build-log.

This sweep is the slice demonstrating sub-mode (c) on its own diff — the strongest possible validation of the rule.

## Version-bump cascade (the slice-105 build-check obligation set, executed in full)

Locked by the MEPD-1 decision (FBCD-1 v1.1 = versioned). Per `canonical_project_checks.md` L257–262, ALL of the following land in THIS slice, in one block, before `/validate-slice`:

1. **5 version surfaces** 0.82.0 → 0.83.0: `VERSION`, `plugin.yaml:15`, `pyproject.toml:20`, `~/.claude/ai-sdlc-VERSION`, `methodology-changelog.md` `## v0.83.0` header (+ `~/.claude/methodology-changelog.md` mirror).
2. **`pip install --upgrade .`** so installed `ai-sdlc-tools` matches (TVFS-1).
3. **Rename the rolling version-sync test** `test_version_files_synchronized_at_v_0_82_0` → `_at_v_0_83_0` (`test_methodology_changelog.py:5496`) + **[M2] sweep ALL `0.82.0`→`0.83.0` literals in the function body (grep-verified 12 occurrences across the 4 leg asserts — VERSION / plugin.yaml / pyproject / `## v` header — + the docstring)** + update the predecessor-bump docstring line `0.81.0 → 0.82.0 (slice-105)` → `0.82.0 → 0.83.0 (slice-108)` + append `108` to the rename-precedent chain.
4. **Repoint shippability row #75** — its command runs the version-sync test at TWO cells (`<HOME>` Command + `<interp>` Machine-cmd); update both `_at_v_0_82_0` → `_at_v_0_83_0`, else `tools.shippability_path_audit` (PTFFD-1) flags a phantom function-citation at `/validate-slice` Step 5.5.
5. **New catalog row index** for the sub-mode (c) regression test = `max(existing)+1` = **#114** (catalog tail = 111/112/113; NOT the slice number).
6. **`## v0.83.0` changelog entry** with a `Rule reference` line (FBCD-1 v1.1) — forward-synced to the installed mirror (MCFS-1).

Obligations 3–5 are the exact surfaces slice-105 missed — they are enumerated here explicitly so the design-Critic + Builder do not re-miss them.

## Decisions made (ADRs)

**No new ADR.** This is a versioned refinement of the existing FBCD-1 rule ([[ADR-022]]), not a new decision — recorded via the `## v0.83.0` methodology-changelog entry + the accepted Proposal 1 in `architecture/critic-calibration-log.md`. Matches the CCC-1 v1.1 precedent (slice-009 versioned CCC-1 without a fresh ADR for the v1.1 bump). Reversibility of the underlying choice: **cheap** (Critic-prompt prose; revertible by deleting sub-mode (c) + a version bump). If the Critic argues a deviation/decision ADR is warranted, that is a triage call at /critique.

## Authorization model for this slice
N/A — no auth surface.

## Error model for this slice
N/A — no runtime error paths. The only "failure modes" are gate failures (CAD-1 drift, PMI-1 version mismatch, PTFFD-1 phantom citation, the rolling version-sync test) — all caught deterministically at `/build-slice` pre-finish and `/validate-slice`.

## Tests touched (anti-slice-105 explicit enumeration)

| File | Change |
|------|--------|
| `tests/methodology/test_critique_agent.py` | ADD `test_critique_dim_9_fix_block_completeness_names_cardinality_fanout_sub_mode`; UPDATE stale "two sub-modes" comment |
| `tests/methodology/test_methodology_changelog.py` | ADD `test_v_0_83_0_fbcd_1_v1_1_entry_present_in_repo` (asserts substantive phrase `Counted-set cardinality fan-out` + `FBCD-1 (v1.1)` + `Rule reference`, NOT presence-only); RENAME `_at_v_0_82_0` → `_at_v_0_83_0` + sweep all 12 `0.82.0` literals + `0.81.0→0.82.0` predecessor line + precedent-chain `108` |
| `architecture/shippability.md` | ADD row #114; REPOINT row #75 version-sync citation (2 cells) |
