# Design: Slice 053 wire-backlog-md-into-slice-and-reflect

**Date**: 2026-05-20
**Mode**: Standard (per `architecture/triage.md`)

## What's new

- New rule-ID **BCR-1** (*Backlog Consume-and-Round-trip discipline*) minted: when `diagnose-out/backlog.md` exists in the repo, `/slice` MUST consult it as a primary candidate source, and `/reflect` MUST round-trip the file with an `**Addressed:** slice-NNN-<name> on YYYY-MM-DD` line under each `SC-NNN` candidate block the slice closed.
- New ADR: **`architecture/decisions/ADR-055-mint-bcr-1-backlog-consume-and-round-trip-discipline.md`** — extends the BC-PROJ-10 / Inclusion-heuristic lineage (slice-052); reversibility: cheap; supersedes: nothing.
- New test module: **`tests/methodology/test_bcr_1_backlog_round_trip.py`** — anchor-presence pins on both SKILL.md surfaces (SOAD-1 multi-surface precedent + BFRD-1 position-pin precedent). 6 tests: 2 prose-presence + 2 position-pin + 2 mandatory-consumption-canonical-phrase. EOL-agnostic via `read_file` (no raw-byte compare).
- New methodology-changelog entry: **`## v0.61.0`** in `methodology-changelog.md`, naming BCR-1 + the ADR-055 / BC-PROJ-10-extension lineage.
- New entry-pin tests in `tests/methodology/test_methodology_changelog.py`: `test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo` + `test_v_0_61_0_bcr_1_shippability_consumer_propagation` (content-bearing, slice-049/051 lesson).
- One new shippability catalog row (`architecture/shippability.md` row #53) — runs the new audit module + the two entry-pins + the OSDG-1 family (`test_slice_skill_drift.py` + `test_reflect_skill_drift.py`) + `test_root_claude_md_cad1_eol_agnostic.py`.
- New risk-register entry minted at `/reflect` Step 2 (status `mitigating`; reversibility cheap) tracking the now-deterministically-pinned but-still-Critic-blind-spot human-judgement axis.

## What's reused

- `skills/slice/SKILL.md` "Gather candidates from ALL these sources" block (line 40) — added: a new source #7 "**`diagnose-out/backlog.md`** (when present)" + canonical guidance prose. The block's existing structure preserved.
- `skills/reflect/SKILL.md` "### Step 2: Update affected vault files" block (line 51) — added: a new bullet for `diagnose-out/backlog.md` round-trip update, sibling to the existing "Decision wrong → supersede the ADR" / "Risk claim wrong → update risk-register" bullets.
- `agents/critique.md` — NOT touched (no `/slice` or `/reflect` skill-runtime reference inside it; CAD-1 N/A).
- `tests/skill_drift_equality.assert_md_forward_synced` — reused verbatim by the existing OSDG-1 drift tests for both surfaces (no change required; the new BCR-1 anchor falls within their content-equality scope automatically).
- `tests/methodology/conftest.read_file` — reused for in-repo SKILL.md reads in the new audit module (slice-046/048 precedent).
- BFRD-1 section-scoped helper pattern from `tests/methodology/test_slice_skill.py::_step3c_section` — cloned shape for the two new `_<section>` helpers.
- SOAD-1 multi-surface pattern from `tests/methodology/test_soad1_structured_options_ask_rule.py::_fenced_block_after` — cloned shape for handling two SKILL.md surfaces in one audit module.
- `tools/methodology_changelog_forward_sync.py` (MCFS-1; slice-041) — picks up the new `## v0.61.0` entry forward-sync automatically; no tool change.
- `tools/ai_sdlc_version_forward_sync.py` (AVFS-1; slice-050) — picks up the new `VERSION` 0.61.0 forward-sync automatically; no tool change.
- `tools/plugin_manifest_audit.py` (PMI-1) — picks up `plugin.yaml.version` 0.61.0 ↔ `VERSION` 0.61.0 parity automatically; no tool change.
- `[[skills/slice-candidates/SKILL.md]]` — read-only reference (the producer of `backlog.md`; slice-053 does not modify it).

## Components touched

### `skills/slice/SKILL.md` (modified)

- **Responsibility**: the user-invocable `/slice` skill prose Claude reads at runtime to pick the next slice candidate. This slice adds `diagnose-out/backlog.md` as a mandatory consultation source.
- **Lives at**: `skills/slice/SKILL.md` (in-repo canonical) + `~/.claude/skills/slice/SKILL.md` (installed; forward-synced; OSDG-1-guarded).
- **Edit location**: inside the "Gather candidates from ALL these sources" block. Add a new numbered source #7 immediately after source #6 ("User-stated intent"), before the "Use graphify queries" anchor. The source-#7 prose names `diagnose-out/backlog.md` literally and asserts mandatory consultation when the file exists.
- **Key interactions**: read at every `/slice` invocation; the new prose adds one read of `diagnose-out/backlog.md` to Claude's "Gather candidates" loop. No code-side hook — this is a prose contract Claude executes.

### `skills/reflect/SKILL.md` (modified)

- **Responsibility**: the user-invocable `/reflect` skill prose Claude reads at slice-completion to update the vault with reality. This slice adds a round-trip update step for `diagnose-out/backlog.md`.
- **Lives at**: `skills/reflect/SKILL.md` (in-repo canonical) + `~/.claude/skills/reflect/SKILL.md` (installed; forward-synced; OSDG-1-guarded since slice-051).
- **Edit location**: inside the "### Step 2: Update affected vault files (thin vault)" block. Add a new bullet immediately after the existing 4-bullet "For each Corrected item" list (anchor: `Slice's own design wrong`), before the "For each Discovered item:" anchor. The bullet names `diagnose-out/backlog.md` literally, defines the `**Closes:** SC-\d{3}` sentinel-anchored citation trigger (in mission-brief.md OR reflection.md — see Trigger grammar refinement, M4), and specifies the in-place additive edit shape (`**Addressed:** slice-NNN-<name> on YYYY-MM-DD` line at end of each closed candidate block, after the `**Evidence:**` sub-list).
- **Key interactions**: read at every `/reflect` invocation; the new prose adds one optional write of `diagnose-out/backlog.md` to Claude's vault-update loop, conditional on `**Closes:** SC-NNN` sentinel-citation. No code-side hook.

### `tests/methodology/test_bcr_1_backlog_round_trip.py` (new)

- **Responsibility**: deterministic anchor-presence audit pinning the BCR-1 contract on both SKILL.md surfaces. Survives /build-slice Phase 1 prose drafting via literal-string pins (slice-046 BFRD-1 precedent).
- **Lives at**: `tests/methodology/test_bcr_1_backlog_round_trip.py` (created by this slice).
- **Key interactions**: imports `read_file` from `tests.methodology.conftest`. Reads `skills/slice/SKILL.md` + `skills/reflect/SKILL.md` (in-repo only — slice-041 M3 discipline; the installed↔in-repo forward-sync is covered by the OSDG-1 family). The `read_file` helper resolves paths against `REPO_ROOT` (the local checkout, NOT git-show / git-blob) — the same read-path semantic used by slice-052's `test_v_0_60_0_obo_shippability_consumer_propagation` for the gitignored `architecture/shippability.md` (m3 precedent). Runs under the methodology suite + via the new shippability catalog row #53 + invoked indirectly by `/build-slice` Step 6 pre-finish (full pytest methodology run).
- **Public surface**: 8 test functions (see "Test inventory" below — bumped from 6 → 7 at /critique M4 closes-sentinel grammar pin → 8 at /critique-review M-add-2 split of Test #6 canonical-phrase + SC-grammar into separate tests).

### `architecture/decisions/ADR-055-mint-bcr-1-backlog-consume-and-round-trip-discipline.md` (new)

- **Responsibility**: records the BCR-1 minting decision + extends-BC-PROJ-10 lineage + Inclusion-heuristic classification + cheap reversibility tag.
- **Lives at**: `architecture/decisions/ADR-055-mint-bcr-1-backlog-consume-and-round-trip-discipline.md` (created by this slice).
- **Key interactions**: cited in `methodology-changelog.md` `## v0.61.0` entry; cited in CLAUDE.md brownfield-rules section; cited in mission-brief.md + design.md + (post-build) reflection.md.

### `methodology-changelog.md` + `~/.claude/methodology-changelog.md` (modified)

- **Responsibility**: append-only ledger of behavior-changing rules. This slice adds `## v0.61.0`.
- **Lives at**: `methodology-changelog.md` (in-repo canonical) + `~/.claude/methodology-changelog.md` (installed; MCFS-1 forward-sync gated; slice-041).
- **Edit location**: append below the existing `## v0.60.0` entry (most recent). Entry follows the META-1 `^## v` split-shape + the slice-051 / v0.59.0 content schema (rule reference + extends-lineage + supersedes-clause + content-bearing body).

### `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml` (modified — 4-part PMI-1 atomic bump)

- **Edit**: 0.60.0 → 0.61.0 across all four legs (in-repo VERSION, installed `~/.claude/ai-sdlc-VERSION` per AVFS-1, `plugin.yaml.version`, and `~/.claude/methodology-changelog.md` via MCFS-1's forward-sync). Per the slice-035 DEVIATION-2 + slice-048→049 leg-drift class this 4-part discipline exists to prevent.

### `CLAUDE.md` (modified)

- **Edit location**: "Self-hosting discipline (specific to this repo)" section. Add a new bullet naming BCR-1 alongside the existing CAD-1 / PMI-1 / INST-1 / Mini-CAD / OSDG-1 enumeration (around line 50-55 of the current self-hosting block).

### `architecture/shippability.md` (modified)

- **Edit location**: append row #53 to the end of the table. Row identifies slice-053 + the regression critical path (the new audit + entry-pins + OSDG-1 family + CAD-1 + the in-place backlog.md round-trip mechanic — i.e., what would have to break for BCR-1 to silently regress).

### `architecture/risk-register.md` (modified at /reflect)

- **Edit location**: append a new risk entry (next free ID, likely **R-14**) tracking "BCR-1 deterministic axis closed; Critic-prompt-dimension axis remains open" with status `mitigating`, reversibility `cheap`. Adding at /reflect Step 2 per the slice-049/052 mid-pipeline-discovery handling precedent — not at design time.

## Contracts added or changed

### BCR-1 prose contract on `/slice` SKILL.md

- **Surface**: the "Gather candidates from ALL these sources" numbered list.
- **Defined in (after edit)**: `skills/slice/SKILL.md` source-list section (new source #7 inserted before the "Use graphify queries" anchor).
- **Canonical phrase pinned (M1-locked at design time)**: literal sentence `MUST consult diagnose-out/backlog.md as a mandatory candidate source when it exists` — this exact wording MUST appear verbatim in the SKILL.md source-#7 prose at /build-slice (no defer-to-build-time fuzzy literal). Pinned by the new audit's Test #3.
- **Auth model**: prose contract Claude reads at runtime. No code authorization — Claude's adherence is enforced indirectly via the BCR-1 anchor-presence audit (regression = silent prose drift caught by the audit at pre-finish).
- **Error cases**: file absent → no-op clean (consultation guidance carries an explicit "when the file exists" qualifier; the slice produces no error if backlog.md is missing). File present but malformed → fall back to the other 6 candidate sources (the prose handles graceful degradation; no audit checks malformed backlog.md grammar — that's a future-slice candidate per Out of scope).

### BCR-1 prose contract on `/reflect` SKILL.md

- **Surface**: the "### Step 2: Update affected vault files (thin vault)" block.
- **Defined in (after edit)**: `skills/reflect/SKILL.md` Step 2 bullet list (new bullet inserted after the existing 4-bullet "For each Corrected item" list, before the "For each Discovered item:" anchor).
- **Canonical phrase pinned (M1-locked at design time)**: literal sentence `append **Addressed:** slice-NNN-<name> on YYYY-MM-DD under each closed candidate block` — this exact wording MUST appear verbatim in the SKILL.md Step 2 bullet at /build-slice (no defer-to-build-time fuzzy literal). The literal `diagnose-out/backlog.md` (substring) ALSO appears in the same bullet.
- **Auth model**: prose contract Claude reads at slice-completion. Trigger is grep-able (`\*\*Closes:\*\* SC-\d{3}` sentinel-anchored regex over mission-brief.md OR reflection.md per **M4 refinement**) — deterministic, not Claude-judgement. **Sentinel anchoring rationale (M4)**: the bare `SC-\d{3}` regex over the whole mission-brief / reflection corpus is too loose — any prose mention of an `SC-NNN` candidate (e.g. design.md prose explaining "we are NOT addressing SC-001 here") would false-trigger the round-trip. The `**Closes:**` sentinel mirrors GitHub closes-issue convention and is unambiguous. Slice authors add a literal `**Closes:** SC-NNN[, SC-MMM, …]` line to mission-brief.md (or to reflection.md if the closure was discovered mid-build) ONLY when the slice actually closes the listed candidates; mere mention does not trigger the round-trip.
- **Error cases**: file absent → no-op clean (this slice didn't produce a backlog.md; nothing to round-trip). No `**Closes:** SC-NNN` sentinel found → no-op clean (per M4 refinement — bare `SC-NNN` mentions do NOT trigger). `**Closes:** SC-NNN` sentinel present but the candidate block isn't in backlog.md → emit a warning (handled by the in-place-edit prose; not a hard error). Multiple `SC-NNN` listed under one `**Closes:**` sentinel → annotate each block. SC-NNN block already carries one or more `**Addressed:**` lines (prior-slice double-shipment per **m5**) → APPEND a new `**Addressed:**` line below the existing one(s); never replace. Multiple `**Addressed:**` lines are valid — the candidate's history shows every slice that touched it.

### Methodology-changelog `## v0.61.0` entry

- **Defined in code at**: `methodology-changelog.md` (in-repo) + `~/.claude/methodology-changelog.md` (installed; forward-synced via MCFS-1 / slice-041).
- **Schema**: META-1-compliant — `## v` prefix + ISO date + em-dash header + rule reference line + extends-lineage line + supersedes-clause + content-bearing body naming BCR-1, the two SKILL.md surfaces, the ADR-055-extends-BC-PROJ-10/Inclusion-heuristic lineage, the audit file path, and the shippability row #53.
- **Error cases**: missing entry → `test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo` FAILs; entry present but missing key content tokens → same test FAILs (content-bearing, slice-051 lesson — no tautological-green presence check).

### `diagnose-out/backlog.md` in-place additive write contract

- **Defined in code at**: prose only — there is no code-side helper this slice. The contract is "/reflect Claude reads the SKILL.md prose and performs the additive edit using its standard Edit tool". This avoids minting a `tools/backlog_round_trip.py` helper for a v1 contract where prose is sufficient (out-of-scope for this slice; future-slice candidate if drift emerges).
- **Edit shape (B1-revised insert location)**: for each closed `SC-NNN` candidate block (e.g. `### SC-001 — pyproject.toml…`), append one new line `- **Addressed:** slice-NNN-<name> on YYYY-MM-DD` immediately AFTER the closing `- **Evidence:**` sub-bullet list of that candidate (between the last `Evidence:` sub-bullet and the next `### SC-NNN` header, or end-of-file). This places the `Addressed:` line at a structurally stable seam — at the END of the candidate block, separate from the existing top-of-block metadata bullets (`Source finding:`, `Severity:`, `Risk profile:`, `Dependencies:`, `Blocks:`, `Description:`, `Rationale:`, `Suggested approach:`, `Evidence:`). The previous proposal (insert directly under `**Risk profile:**`) was REJECTED at /critique B1 — it would have shoved `Addressed:` BETWEEN `Risk profile:` and `Dependencies:`, mid-metadata-block, displacing all fixed-position metadata bullets after `Risk profile:`. Append-at-end-of-block preserves the metadata-bullet contract by construction. Multi-line example after edit:
  ```
    - `tests/methodology/test_install_audit.py:292-302` — test_pyproject_toml_declares_tools_package checks name+packages, not version

  - **Addressed:** slice-054-fix-pyproject-toml-version-drift on 2026-05-21

  ### SC-002 — tomllib used in validate_slice_layers.py but not declared
  ```
- **Error cases**: backlog.md absent → /reflect emits "no backlog.md to round-trip, skipping" log and proceeds; no audit failure. SC-NNN block missing in backlog.md → /reflect logs the discrepancy; no audit failure (the diagnose→slice-candidates→backlog.md pipeline owns the SC inventory). **m5 double-shipment**: SC-NNN block already carries one or more `- **Addressed:**` lines (because a previous slice closed it, and the current slice closes it again via a different angle or because slice-053's own slice-054 follow-up later iterates the same finding) → APPEND a new `**Addressed:**` line BELOW the existing one(s); NEVER replace. Multiple `Addressed:` lines are valid — the candidate's history shows every slice that touched it; the most recent is at the bottom. **M-add-1 empty-Evidence-list shape**: SC-NNN block has NO `**Evidence:**` sub-bullet list (possible for a manually-authored backlog candidate, or under a future build_backlog.py emit-shape change that drops the Evidence: section) → insert the `**Addressed:**` line after the last top-level metadata bullet of the candidate block (i.e., after `**Suggested approach:** …`, or if that is also absent, after `**Description:**`'s body content), before the next `### SC-NNN` header or end-of-file. This preserves the "append-at-end-of-candidate-block" structural seam while gracefully degrading on incomplete candidate-block shapes — Sommerville graceful-degradation discipline. The diagnose→slice-candidates→backlog.md pipeline currently always emits Evidence sub-lists (verified for all 26 of 26 candidates in `diagnose-out/backlog.md` at slice-053 design time), so practical impact today is zero; the explicit error-case prose hardens the contract against future producer-shape variation. The audit verifies the SKILL.md prose contract is present; it does NOT verify backlog.md byte-for-byte (the file is gitignored — there's no canonical pre-edit shape to pin).

## Data model deltas

None. This slice adds prose contracts + a test module + a changelog entry + an ADR. No new entities, no new fields, no schema changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_bcr_1_backlog_round_trip.py` | shippability catalog row #53 (`architecture/shippability.md`) + `/build-slice` Step 6 full-`pytest tests/methodology` invocation | The test module IS the consumer test; self-consuming per the slice-038/044 audit-module convention | — |
| `architecture/decisions/ADR-055-mint-bcr-1-backlog-consume-and-round-trip-discipline.md` | `methodology-changelog.md` `## v0.61.0` entry (cites ADR-055) + design.md + mission-brief.md + CLAUDE.md brownfield-rules | `tests/methodology/test_methodology_changelog.py::test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo` (asserts the `## v0.61.0` entry names ADR-055) | — |

The two skill-prose edits (`skills/slice/SKILL.md` + `skills/reflect/SKILL.md`), the changelog entry, the CLAUDE.md update, the VERSION bumps, and the shippability row #53 are MODIFICATIONS to existing files, not new modules — WIRE-1 doesn't list them (per the slice-046/048 precedent — modifications never need wiring-matrix rows).

## Decisions made (ADRs)

- [[ADR-055]] — mint BCR-1 (Backlog Consume-and-Round-trip discipline): when `diagnose-out/backlog.md` exists, `/slice` MUST consult it as a primary candidate source and `/reflect` MUST round-trip closed `SC-\d{3}` findings with an in-place additive `**Addressed:**` line — reversibility: **cheap** (the rule is one prose anchor per SKILL.md surface + one audit module + one changelog entry; removal = delete those; no migration, no contract consumers outside this repo).

No other ADRs minted by this slice.

## Authorization model for this slice

No new authorization. Both SKILL.md surfaces are user-invocable (`/slice` and `/reflect`); the new prose extends behavior Claude executes on the user's behalf during a slice loop. The BCR-1 audit is a passive test run by /build-slice Step 6 + shippability runner — no privilege escalation, no new write paths beyond what /reflect already had (which already writes to risk-register.md, ADRs, the slice's own design.md, etc.).

## Error model for this slice

- **Audit FAIL — anchor missing in `/slice` SKILL.md**: `test_slice_skill_md_bcr_1_backlog_md_consume_anchor_present` (m4-renamed) emits `skills/slice/SKILL.md candidate-sources section is missing literal 'diagnose-out/backlog.md' — BCR-1 prose contract not honored on the /slice consumption side`. Recovery: re-insert the source-#7 prose at the documented anchor location.
- **Audit FAIL — anchor missing in `/reflect` SKILL.md**: `test_reflect_skill_md_bcr_1_backlog_md_round_trip_anchor_present` (m4-renamed) emits `skills/reflect/SKILL.md Step 2 vault-updates section is missing literal 'diagnose-out/backlog.md' — BCR-1 prose contract not honored on the /reflect round-trip side`. Recovery: re-insert the Step 2 bullet at the documented anchor location.
- **Audit FAIL — position-pin violated**: emits surface-specific location error per BFRD-1 precedent (anchor exists but outside the bounded section).
- **Audit FAIL — closes-sentinel grammar missing in `/reflect` SKILL.md (M4-new)**: `test_reflect_skill_md_bcr_1_closes_sentinel_grammar_pinned` emits `skills/reflect/SKILL.md Step 2 bullet is missing the literal '**Closes:** SC-' sentinel-anchor grammar — BCR-1 trigger semantic regressed to bare-SC-NNN-grep (false-positive class)`. Recovery: re-insert the sentinel-grammar prose.
- **Audit FAIL — SC-\d{3} regex grammar missing in `/reflect` SKILL.md (M2-extension; M-add-2 split into Test #7)**: `test_reflect_skill_md_bcr_1_sc_grammar_pinned` emits `skills/reflect/SKILL.md Step 2 bullet is missing the literal 'SC-\d{3}' regex token — BCR-1↔R-13 producer-side cross-skill grammar pin lost (the producer-side rename of SC-NNN identifier syntax would silently no-op the consumer)`. Recovery: re-insert the grammar token in the SKILL.md prose.
- **Audit FAIL — methodology-changelog entry missing or content-incomplete**: `test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo` emits missing-content-token messages (BCR-1, ADR-055, "extends", etc.).
- **OSDG-1 family FAIL (skill-drift)**: existing `test_slice_skill_drift.py` / `test_reflect_skill_drift.py` emit `<surface>` byte-divergence error (CRLF↔LF excluded per EOL-DRIFT-1). Recovery: re-sync installed copy.
- **MCFS-1 FAIL**: existing `tools/methodology_changelog_forward_sync.py` HALTs on divergent installed copy. Recovery: re-sync.
- **AVFS-1 FAIL**: existing `tools/ai_sdlc_version_forward_sync.py` HALTs on divergent `~/.claude/ai-sdlc-VERSION`. Recovery: re-sync.
- **PMI-1 version-parity FAIL**: `tools/plugin_manifest_audit.py` emits version-mismatch across the 4-leg parity. Recovery: align all 4 legs to 0.61.0.
- **Runtime `/reflect` warning — SC-NNN cited but absent from backlog.md**: prose contract emits a log warning, not an audit failure. By design — the audit gates the SKILL.md prose contract, not backlog.md content (the diagnose→slice-candidates→backlog.md pipeline owns SC inventory).
- **Runtime `/slice` warning — backlog.md absent**: prose contract handles via "when the file exists" qualifier; consultation is skipped silently. No-op clean.

## Inclusion-heuristic classification (per BC-PROJ-10, slice-052)

This slice **IS a methodology-surface behavior change**:
- Mints a NEW rule-ID (BCR-1) governing two OSDG-1-guarded SKILL.md surfaces.
- Adds a new ADR (ADR-055) extending the BC-PROJ-10 / Inclusion-heuristic lineage.
- Adds new behavior contracts on `/slice` (consume) + `/reflect` (round-trip).

Therefore: **4-part PMI-1 atomic bump path** (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`), 0.60.0 → 0.61.0, with the new `## v0.61.0` changelog entry + content-bearing entry-pin.

**META-1 enforcing-assertion citation (m2-discharged)**: the canonical META-1 assertion is `test_methodology_changelog.py::test_methodology_changelog_has_versioned_entries` (the `^## v` split semantic; `tests/methodology/test_methodology_changelog.py:136` per slice-045 / slice-052 lesson). A behavior-changing methodology slice that minted a new rule-ID without a `## vN.N.N` entry would FAIL this assertion — verified by literal grep of the assertion's regex, NOT by precedent slice analogy alone. Slice-053's `## v0.61.0` entry naming BCR-1 + ADR-055 satisfies the assertion at construction time; the entry-pin `test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo` keeps it satisfied at every future suite run.

Precedent class: slice-048 (SOAD-1 minted), slice-044 (STP-1 minted), slice-050 (AVFS-1 minted), slice-038 (SRSC-1 minted). NOT the conformance-fix/born-retired class (slice-040, slice-043, slice-045).

## Test inventory (new audit module)

`tests/methodology/test_bcr_1_backlog_round_trip.py` — **8 tests** (bumped from 6 → 7 at /critique M4 closes-sentinel grammar pin → 8 at /critique-review M-add-2 split of Test #6 canonical-phrase + SC-grammar into separate tests, restoring BFRD-1 single-assertion-per-test discipline):

| # | Test name | Surface | Pin shape |
|---|-----------|---------|-----------|
| 1 | `test_slice_skill_md_bcr_1_backlog_md_consume_anchor_present` | `skills/slice/SKILL.md` | Literal `diagnose-out/backlog.md` substring inside the scoped "Gather candidates" → "Use graphify queries" section. **(m4-renamed: was `_backlog_md_named_in_candidate_sources`; now mirrors BFRD-1 `_prelude_present` precedent — `_consume_anchor_present`.)** |
| 2 | `test_slice_skill_md_bcr_1_source_position_pinned` | `skills/slice/SKILL.md` | Position-pin (slice-046 BFRD-1 shape): the new source #7 anchor sits AFTER existing source #6 anchor (`User-stated intent`) and BEFORE the `Use graphify queries` anchor |
| 3 | `test_slice_skill_md_bcr_1_mandatory_consumption_phrase_present` | `skills/slice/SKILL.md` | **(M1-locked at design time)** Literal full-sentence pin: `MUST consult diagnose-out/backlog.md as a mandatory candidate source when it exists` — exact verbatim substring assertion against the scoped section. NOT a two-token shaving; full-canonical per BFRD-1 / SOAD-1 precedent. |
| 4 | `test_reflect_skill_md_bcr_1_backlog_md_round_trip_anchor_present` | `skills/reflect/SKILL.md` | Literal `diagnose-out/backlog.md` substring inside the scoped "### Step 2:" → "### Step 3:" section. **(m4-renamed: was `_backlog_md_named_in_step2`; now mirrors BFRD-1 precedent.)** |
| 5 | `test_reflect_skill_md_bcr_1_round_trip_position_pinned` | `skills/reflect/SKILL.md` | Position-pin: the new bullet sits AFTER the existing "For each Corrected item" 4-bullet list (anchor: `Slice's own design wrong`) and BEFORE the `For each Discovered item:` anchor |
| 6 | `test_reflect_skill_md_bcr_1_round_trip_canonical_phrase_present` | `skills/reflect/SKILL.md` | **(M1-locked at design time; M-add-2 split: canonical-phrase ONLY)** Literal full-sentence pin: `append **Addressed:** slice-NNN-<name> on YYYY-MM-DD under each closed candidate block` — exact verbatim substring assertion against the scoped section. Single-assertion-per-test discipline (BFRD-1 / SOAD-1 / Hendrickson). |
| 7 | `test_reflect_skill_md_bcr_1_sc_grammar_pinned` | `skills/reflect/SKILL.md` | **(M-add-2-new: M2-extended grammar pin SPLIT OUT of Test #6)** Literal `SC-\d{3}` regex-token substring pin against the scoped Step 2 section. Asserts the SKILL.md prose names the literal trigger-regex grammar `SC-\d{3}` so a future producer-side rename of `SC-NNN` syntax (R-13 deferred OSDG-1 extension to `/slice-candidates`) forces a same-time consumer-side update — the BCR-1↔R-13 cross-skill brittleness pin (Newman contract-test framework). Single-assertion-per-test. |
| 8 | `test_reflect_skill_md_bcr_1_closes_sentinel_grammar_pinned` | `skills/reflect/SKILL.md` | **(M4-new; renumbered #7→#8 at M-add-2 split)** Literal closes-sentinel grammar pin: asserts the SKILL.md Step 2 bullet prose names the literal `**Closes:** SC-` sentinel anchor (NOT bare `SC-\d{3}`), so the round-trip trigger semantic is mentioned-vs-closes-disambiguated in the skill prose itself (mirrors GitHub closes-issue convention). Closes the M4 self-bootstrap defect — bare-grep over the whole mission-brief / reflection corpus is too loose; the sentinel anchor is the disambiguator. |

Plus 2 entry-pin tests added to `tests/methodology/test_methodology_changelog.py`:
| # | Test name | Purpose |
|---|-----------|---------|
| 9 | `test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo` | Content-bearing v0.61.0 entry-pin (BCR-1 / ADR-055 / "extends" / "BC-PROJ-10" / two-surface mention). Slice-051 precedent. |
| 10 | `test_v_0_61_0_bcr_1_shippability_consumer_propagation` | Asserts row #53 of architecture/shippability.md cites the new audit module + the two entry-pins. Slice-051 precedent. |

**Genuine-contrast proof method** (per the mid-slice smoke gate in mission-brief.md, applying the slice-051 BC-PROJ-3 / BC-GLOBAL-2 hazard-avoidance discipline per **M3 fix**):

**Save-bytes-then-restore-via-hash-assertion recipe** (per **M3** + slice-051 aggregated lesson — replaces git-checkout/restore/stash, which would trip Critical BC-PROJ-3 / BC-GLOBAL-2 even when provably harmless; under BRANCH-1 a git-level revert of a slice-touched path destroys uncommitted slice work):

1. **Read + hash + save**: `bytes0 = Path(target).read_bytes()`; `sha0 = hashlib.sha256(bytes0).hexdigest()`; save `bytes0` to an in-memory variable (NOT to a temp file — keeping it in-memory avoids any filesystem-level state).
2. **Perturb**: via the Edit tool (preferred) or direct `Path(target).write_bytes(perturbed)` — flip one non-EOL byte OUTSIDE any other anchor in the file (the new BCR-1 anchor is the perturbation target; for other anchor-presence tests, pick a non-overlapping anchor byte).
3. **Run isolated test only**: `$PY -m pytest tests/methodology/test_bcr_1_backlog_round_trip.py::<single_test_name> -q` — NOT the full methodology suite (the OSDG-1 family `test_slice_skill_drift.py` + `test_reflect_skill_drift.py` would co-FAIL during the perturbation window and pollute the contrast signal; slice-051 mid-slice smoke precedent). Assert FAIL with surface-specific error message.
4. **Restore**: `Path(target).write_bytes(bytes0)` — write back the saved in-memory bytes.
5. **Re-hash + assert equal**: `sha1 = hashlib.sha256(Path(target).read_bytes()).hexdigest(); assert sha1 == sha0` — content-hash equality check confirms the restore landed byte-exact.
6. **NEVER**: use `git checkout -- <path>`, `git restore <path>`, or `git stash` to restore. The 6-step recipe is the only authorized restore mechanic for git-tracked perturbation targets.

Both `skills/slice/SKILL.md` and `skills/reflect/SKILL.md` are git-tracked → the slice-051 hazard applies directly to this slice's perturbation targets. Echo the recipe + the 6 pre/post hashes in build-log.md per the mid-slice smoke gate prose.

**Per-test contrast plan** (post-/critique-review numbering, 8 audit tests + 2 entry-pins = 10 contrasts):
- Tests 1, 3 → perturb the named substring in `skills/slice/SKILL.md` (one non-EOL byte) → FAIL. Restore (6-step recipe above). PASS.
- Test 2 → swap source #7's position with source #6 (whole-line swap via Edit) → test 2 FAILs while tests 1, 3 still PASS (orthogonal contrast). Restore (recipe above).
- Tests 4, 6, 7, 8 → perturb the corresponding named substring in `skills/reflect/SKILL.md` (one non-EOL byte each, run isolated). FAIL. Restore. PASS.
- Test 5 → swap bullet position in `skills/reflect/SKILL.md`. Same orthogonal contrast.
- Tests 9, 10 → perturb `methodology-changelog.md` v0.61.0 entry tokens. FAIL. Restore. PASS. (methodology-changelog.md is also git-tracked — apply the same 6-step recipe.) **M-add-3 isolation discipline**: do NOT run `$PY -m tools.methodology_changelog_forward_sync` (MCFS-1) during the v0.61.0-entry perturbation window — MCFS-1 will HALT on the divergent installed copy and pollute the contrast signal, mirroring the OSDG-1 family co-FAIL hazard on SKILL.md perturbations. Run isolated `pytest tests/methodology/test_methodology_changelog.py::test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo -q` only.

All 10 contrasts recorded in build-log.md per slice-049/051 lesson + slice-044/BC-PROJ-7.

## Open ambiguities (declared, not blocking)

These were considered design-time and resolved with defensible defaults; the user / Critic may override. **Critic at /critique surfaced 4 of these as findings (B1, M2, M4, m5); all four are now ACCEPTED-FIXED above. The ambiguity entries below carry the post-fix-block resolution.**

1. **`diagnose-out/backlog.md` path scope**: strict (this canonical path only) vs configurable (env var / config). **Decision: strict.** The path matches the `/diagnose` skill's documented output location; configurability expands the contract surface for no current need.
2. **"Addressed" trigger — REFINED PER M4 + M2**: previously proposed as bare `SC-\d{3}` regex match in mission-brief.md OR reflection.md. **REFINED: `\*\*Closes:\*\* SC-\d{3}` sentinel-anchored regex** — only an explicit `**Closes:** SC-NNN[, SC-MMM, …]` literal sentinel header triggers the round-trip, not a mere mention of an SC-NNN candidate elsewhere in the prose. Mirrors GitHub closes-issue convention; the sentinel is the disambiguator. **M2-secondary refinement**: the literal trigger-regex grammar `SC-\d{3}` is ALSO pinned in the SKILL.md prose (via Test #6's grammar pin), so a future producer-side rename of the SC-NNN identifier syntax (R-13 deferred producer-side OSDG-1 extension) forces a same-time consumer-side update. The "trigger objective (grep-able, not Claude-judgement)" claim now holds: the closes-sentinel is unambiguous, and the regex grammar is pinned on both sides of the trigger contract.
3. **Update mechanic — REFINED PER B1**: previously proposed as in-place additive bullet directly under `**Risk profile:** …` row. **REFINED: in-place additive `- **Addressed:** slice-NNN-<name> on YYYY-MM-DD` line at the END of each closed candidate block — AFTER the `**Evidence:**` sub-bullet list, BEFORE the next `### SC-NNN` header.** Structurally stable seam, preserves the existing fixed-position metadata-bullet contract by construction (the previous Risk-profile-sibling insert would have shoved `Addressed:` BETWEEN `Risk profile:` and `Dependencies:`, mid-metadata-block — B1 rejection). Single source of truth; matches the user's stated intent ("update backlog.md to show which one got fixed"); file is gitignored (no commit churn). Multiple `Addressed:` lines are valid (m5 double-shipment append-never-replace).
4. **Self-bootstrap — RECOMPUTED PER M4**: should slice-053 itself round-trip backlog.md? **Decision: no — and now correctly self-consistent under the refined trigger.** Under the NEW `**Closes:**` sentinel trigger (M4 refinement), slice-053's mission-brief.md has NO `**Closes:** SC-NNN` sentinel header (verified by literal grep — only `**SC-001**` bold-emphasis mentions appear, none anchored by the closes-sentinel syntax) → the BCR-1 round-trip trigger correctly no-ops. Under the PREVIOUS bare-`SC-\d{3}` trigger (now-rejected), slice-053 would have false-triggered (M4 defect). The /critique correctly caught the empirical contradiction; the sentinel refinement resolves it. The first slice that triggers the round-trip will be slice-054 (= SC-001 fix-pyproject-toml-version-drift), whose mission-brief.md will carry a literal `**Closes:** SC-001` sentinel.
