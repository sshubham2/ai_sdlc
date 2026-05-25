# Design: Slice 054 fix-pyproject-toml-version-drift

**Date**: 2026-05-21
**Mode**: Standard
**Inclusion-heuristic classification**: **Route B (chosen at design)** — new RULE-ID `PVFS-1` (Pyproject Version Forward Sync) + ADR-056 + methodology-changelog v0.62.0 entry + 4-part PMI-1 atomic bump (VERSION + plugin.yaml + changelog header + installed `~/.claude/ai-sdlc-VERSION` leg via AVFS-1). **NO standalone audit tool** (SOAD-1/BCR-1 rule-without-tool precedent — the pytest assertion IS the gate). Discharges MEPD-1 (`agents/critique.md` Dim 7) by **rule-path** (option (a)), not (b) why-none.

**Precedent cited (verified-against-artifact, not asserted)**:
- PMI-1 docstring `tools/plugin_manifest_audit.py:18-22` already frames "a plugin manifest that drifts from the actual distribution is worse than no manifest"; pyproject was a carve-out (PMI-1 reads plugin.yaml only at L207), not a deliberate exemption — closing the carve-out is a new rule scope.
- Slice-049/050 precedent: cheap-substance new-rule slices are legitimate when the gate scope is genuinely new (OSDG-1 / AVFS-1 both shipped on N=1 latent-exposure evidence).
- Slice-050 AVFS-1 minted a standalone tool because `~/.claude/ai-sdlc-VERSION` lives OUT of repo (runtime read required); pyproject.toml is in-repo so the pytest assertion is structurally sufficient — Route C (full-tool) would be over-engineering per `/reduce`.

## What's new

- **PVFS-1** rule-ID minted (Pyproject Version Forward Sync). Asserts: `pyproject.toml [project].version` MUST equal the trimmed contents of `VERSION`. Closes the SC-001 stale-pip-artifact class structurally (was: an ungated PMI-1 sibling).
- **ADR-056** `architecture/decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md` (cheap reversibility — a pytest assertion can be removed; the bump can be reverted).
- **methodology-changelog v0.62.0** entry recording PVFS-1 / ADR-056 / new-rule-supersedes-nothing / 4-part PMI-1 atomic bump lineage.
- **VERSION 0.61.0 → 0.62.0** (4-part PMI-1 atomic bump leg 1).
- **plugin.yaml `version: 0.61.0 → 0.62.0`** (leg 2, PMI-1 gates this).
- **methodology-changelog `## v0.62.0` header** (leg 3, META-1 gates this).
- **`~/.claude/ai-sdlc-VERSION` → 0.62.0`** (leg 4, AVFS-1 gates this — installed forward-sync).
- **pyproject.toml `[project].version = "0.20.0"` → `"0.62.0"`** (the SC-001 fix substance; matches the new VERSION).
- **pyproject.toml stale prose scrub** (AC3) — *3 sites enumerated per /critique M2*: **line 3** comment `# Per INST-1 (methodology-changelog.md v0.20.0). The pipeline ships skills,` → refactor to non-version-bearing form per slice-045 INSTALL.md precedent (e.g., `# Per INST-1. The pipeline ships skills,` — drops the version literal so it isn't a per-VERSION-bump scrub obligation); **line 6** comment `(the 13 audit modules under tools/)` → refactor to count-free wording (e.g., `(the audit modules under tools/ — see plugin.yaml for the canonical inventory)`); **line 66** comment `# The tools package itself has no non-Python data files in v0.20.0.` → refactor to version-free wording (e.g., `# The tools package itself has no non-Python data files.`).
- **AC3 pin test** (per /critique M1, mints in this slice as the structural backstop for AC3): extend the existing `tests/methodology/test_pyproject_version_matches_version_file.py` (already authored at `/repro` for AC1) with a new function `test_pyproject_has_no_stale_0_20_0_or_count_literals` asserting `"0.20.0" not in pyproject_text` AND `"13 audit modules" not in pyproject_text` AND `"13 tool modules" not in pyproject_text`. The `[project].version` field reads `"0.20.0"` pre-fix (line 20) and `"0.62.0"` post-fix, so the bare `"0.20.0"` substring test catches all four sites (lines 3 + 6 + 20 + 66) pre-fix and PASSes when ALL are cleaned post-fix — guarantees a non-tautological WRITTEN-FAILING → PASS transition AND catches any forgotten site even if the design author overlooks one. Same test module as AC1 (one file per concern: pyproject↔VERSION + pyproject-no-stale-literals).
- **Two entry-pin tests** in `tests/methodology/test_methodology_changelog.py` (content-bearing per slice-051 precedent — NOT thin presence checks):
  - `test_v_0_62_0_pvfs_1_entry_present_in_repo` — asserts the v0.62.0 entry body carries `PVFS-1`, `ADR-056`, `Pyproject Version Forward Sync`, `mints a new rule`, `supersedes nothing`, `Rule reference`, AND the 4-part-bump anchor (`4-part PMI-1 atomic bump` or equivalent).
  - `test_v_0_62_0_pvfs_1_shippability_consumer_propagation` — asserts `architecture/shippability.md` row #54 mentions **BOTH `PVFS-1` AND `SC-001`** (per /critique-review M-add-1: row #54 is the slice's *only* trace anchor for the BCR-1 `/diagnose → /slice → /reflect` round-trip — pinning only `PVFS-1` would silently pass a future row rewrite that drops the `SC-001` cite, severing the traceability axis slice-053 BCR-1 just shipped to enforce; slice-054 is the first BCR-1 end-to-end dogfood so the SC-NNN trace must be regression-pinned on the slice that mints it). RPCD-1/SCPD-1 consumer-propagation per slice-040 lesson — uncatalogued pin's breakage is invisible to the runner.
- **shippability row #54 PVFS-1 enrichment**: the row added at `/repro` cites `SC-001` but does NOT yet cite `PVFS-1`. Edit the row to add `PVFS-1` rule-ID anchor in the Critical-path column (consumer-propagation requirement above forces this).
- **mission-brief.md `**Closes:** SC-001`** sentinel header (already written — BCR-1 trigger).
- **reflection.md (at `/reflect`)**: BCR-1 round-trip will inject `- **Addressed:** slice-054-fix-pyproject-toml-version-drift on YYYY-MM-DD` line into `diagnose-out/backlog.md` SC-001 block (AC4 first end-to-end dogfood).

## What's reused

- PMI-1 plugin.yaml↔VERSION gate **pattern** at `tools/plugin_manifest_audit.py:207-217` — mirrored, NOT extended. PMI-1 itself stays unchanged (no edit to `plugin_manifest_audit.py`). PVFS-1 is a sibling gate, not a PMI-1 sub-rule.
- AVFS-1 (`tools/ai_sdlc_version_forward_sync.py`, slice-050) — gates leg 4 of the atomic bump (`~/.claude/ai-sdlc-VERSION`). Already wired into `/build-slice` Step 6 + `/reflect` Step 5b-avfs.
- MCFS-1 (`tools/methodology_changelog_forward_sync.py`, slice-041) — gates installed↔in-repo forward-sync of methodology-changelog (covers the v0.62.0 entry's in-repo↔installed parity via whole-file gate; NO per-version installed read needed).
- BCR-1 round-trip mechanism (slice-053 wire) for AC4.
- `tests/methodology/conftest.REPO_ROOT` + `read_file` helpers for the new entry-pin tests.
- `_extract_version_body(in_repo, "0.62.0")` helper at `tests/methodology/test_methodology_changelog.py` for the entry-body slice (already exists, used by every prior `test_v_0_NN_0_*` pin).
- pyproject.toml plain-text regex parse pattern at `tests/methodology/test_pyproject_version_matches_version_file.py:_read_pyproject_project_version` (already authored at `/repro`; deliberately avoids `tomllib` per SC-002).

## Components touched

*(Per /critique m2: rewritten as a self-contained section after the per-component sub-sections were ambiguously framed as "see full design.md" in the rev-0 draft. The bullet list immediately below mirrors the per-component sub-sections that follow it.)*

**Quick inventory** (the per-component sub-sections below detail each):

- `pyproject.toml` (modified) — `[project].version` 0.20.0 → 0.62.0; 3 stale-literal scrub sites (lines 3 + 6 + 66 per M2)
- `VERSION` (modified) — 0.61.0 → 0.62.0 (atomic bump leg 1)
- `plugin.yaml` (modified) — `version: 0.61.0 → 0.62.0` (leg 2)
- `methodology-changelog.md` (modified) — new `## v0.62.0` section (leg 3)
- `~/.claude/ai-sdlc-VERSION` (modified) — 0.61.0 → 0.62.0 (leg 4, AVFS-1)
- `architecture/decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md` (created)
- `tests/methodology/test_methodology_changelog.py` (modified — +2 entry-pin functions)
- `tests/methodology/test_pyproject_version_matches_version_file.py` (modified — +1 AC3 stale-literal pin function, per M1)
- `architecture/shippability.md` (modified) — row #54 enriched with `PVFS-1` rule-ID anchor
- `diagnose-out/backlog.md` (modified at /reflect only) — BCR-1 round-trip injects `**Addressed:**` line into SC-001 block

### `pyproject.toml` (modified)
- **Responsibility**: PEP 621 package metadata for `ai-sdlc-tools` pip distribution; declares `[project].version` consumed by `pip install <repo>`.
- **Lives at**: `pyproject.toml` (project root)
- **Key interactions**: `pip install <repo>` reads it; the new PVFS-1 test at `tests/methodology/test_pyproject_version_matches_version_file.py` asserts `[project].version` equals trimmed `VERSION`; PMI-1 does NOT read it (deliberate carve-out; PVFS-1 is the sibling gate).
- **Edit scope**: line 20 `version = "0.20.0"` → `version = "0.62.0"`; line 6 comment cleanup (drop `13 audit modules` literal); line 66 comment cleanup (drop `v0.20.0` literal).

### `VERSION` (modified — atomic bump leg 1)
- **Responsibility**: canonical methodology semver, single source of truth read by every forward-sync gate.
- **Lives at**: `VERSION` (project root)
- **Key interactions**: read by PMI-1, AVFS-1, MCFS-1; will be read by PVFS-1.
- **Edit scope**: `0.61.0` → `0.62.0` (single trimmed line).

### `plugin.yaml` (modified — atomic bump leg 2)
- **Responsibility**: AI SDLC plugin manifest enumerating skills/agents/tools + version.
- **Lives at**: `plugin.yaml` (project root)
- **Key interactions**: PMI-1 gates `plugin.yaml.version == VERSION`.
- **Edit scope**: `version: 0.61.0` → `version: 0.62.0`. No skill/agent/tool inventory change in this slice.

### `methodology-changelog.md` (modified — atomic bump leg 3)
- **Responsibility**: append-only ledger of methodology-surface behavior changes.
- **Lives at**: `methodology-changelog.md` (project root)
- **Key interactions**: META-1 gates `## v` split shape; MCFS-1 gates installed↔in-repo parity; new `test_v_0_62_0_pvfs_1_entry_present_in_repo` gates entry body content.
- **Edit scope**: prepend a new `## v0.62.0 — 2026-05-21` section above `## v0.61.0` carrying PVFS-1 entry (Rule reference / Defect class / Validation method per META-1 entry-pin obligation).

### `~/.claude/ai-sdlc-VERSION` (modified — atomic bump leg 4)
- **Responsibility**: installed VERSION leg PMI-1 doesn't reach; AVFS-1's exclusive domain.
- **Lives at**: `~/.claude/ai-sdlc-VERSION` (installed; OUT of repo)
- **Key interactions**: AVFS-1 gates parity with in-repo `VERSION`.
- **Edit scope**: `0.61.0` → `0.62.0` (single trimmed line). Operator-applied at INSTALL.md install step OR maintained by `/build-slice` Step 6 / `/reflect` Step 5b-avfs guidance.

### `architecture/decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md` (created)
- **Responsibility**: append-only ADR recording the PVFS-1 minting decision + alternatives + reversibility.
- **Lives at**: `architecture/decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md`
- **Key interactions**: cited in the v0.62.0 methodology-changelog entry (`Rule reference` block); CSP-1 cross-spec parity covers ADR↔changelog naming.

### `tests/methodology/test_methodology_changelog.py` (modified — add 2 entry-pin tests)
- **Responsibility**: pin every methodology-changelog version body's content-bearing anchors (slice-051 pattern).
- **Lives at**: `tests/methodology/test_methodology_changelog.py`
- **Key interactions**: invoked by full pytest run; consumed by SCMD-1 / SCPD-1 / RPCD-1; shippability runner row #54 cites them.
- **Edit scope**: append two new `def test_v_0_62_0_pvfs_1_*` functions immediately AFTER the existing `test_v_0_61_0_bcr_1_shippability_consumer_propagation` block (preserve append-only ordering — newest version-pin at file bottom).

### `tests/methodology/test_pyproject_version_matches_version_file.py` (existing — possibly extended for AC3)
- **Responsibility**: PVFS-1 gate (already authored at `/repro`).
- **Edit scope**: add ONE additional test function `test_pyproject_toml_no_stale_v_0_20_0_or_13_audit_modules_literal` (AC3 stale-prose pin) — small, single-file regex check. Keep both functions in the same module.

### `architecture/shippability.md` (modified — enrich row #54)
- **Responsibility**: catalog of critical-path tests (every slice's regression-protection lives here).
- **Edit scope**: row #54 Critical-path column gets a `PVFS-1` rule-ID anchor (currently only `SC-001` referenced). Required for the new `test_v_0_62_0_pvfs_1_shippability_consumer_propagation` test to PASS.

### `diagnose-out/backlog.md` (modified at `/reflect` — BCR-1 round-trip)
- **Responsibility**: `/diagnose → /slice → /reflect` round-trip backlog.
- **Edit scope**: NOT touched at `/build-slice`. At `/reflect`, BCR-1 round-trip injects `- **Addressed:** slice-054-fix-pyproject-toml-version-drift on YYYY-MM-DD` line into SC-001 block AFTER `**Evidence:**` (M4 sentinel-anchored, triggered by mission-brief.md `**Closes:** SC-001`).

## Contracts added or changed

**PVFS-1** (the new methodology-class invariant — not a code-level API contract):

- **Rule shape**: `pyproject.toml [project].version` ≡ trimmed contents of `VERSION`.
- **Gate**: `tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file` (already exists from `/repro`).
- **Runtime invocation**: pytest catalog runner at `/validate-slice` Step 5.5 (via shippability row #54).
- **Failure mode**: pytest exit 1; catalog runner reports row #54 FAIL; build refuses to declare slice done.
- **Defect class**: a future VERSION bump that forgets to update pyproject.toml (or a pyproject edit that hard-codes a stale literal).

No new code-level API endpoints, events, or schemas. PVFS-1 is a methodology-discipline rule, not a runtime contract.

## Data model deltas

None. No DB schema change; no migration.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces no `src/`-style production modules — only test/doc/manifest edits. The new test file at `tests/methodology/test_pyproject_version_matches_version_file.py` was created at `/repro`; its consumer is the shippability catalog runner (already wired via row #54).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero-row matrix — audit treats this as clean per /design-slice Step 4 WIRE-1 paragraph: "If this slice introduces no new modules: keep the header + separator only.")

## Decisions made (ADRs)

- [[ADR-056]] — Mint PVFS-1 (Pyproject Version Forward Sync); pyproject.toml `[project].version` MUST equal trimmed `VERSION`; gate is a pytest assertion mirroring PMI-1's plugin.yaml↔VERSION pattern; no standalone tool (SOAD-1/BCR-1 rule-without-tool precedent). — reversibility: **cheap**

## Authorization model for this slice

N/A. PVFS-1 is an audit-time methodology invariant; no user-facing actions, no roles, no protected resources.

## Error model for this slice

- **Gate failure**: `test_repro_sc001_pyproject_project_version_matches_version_file` raises `AssertionError` with a message naming the actual pyproject value, the actual VERSION value, and citing the PMI-1 sibling pattern (already authored at `/repro`).
- **Runner integration**: shippability runner `tools/shippability_runner.py` reports row #54 as FAIL; `/validate-slice` Step 5.5 surfaces the row in the per-row report; `/build-slice` Step 6 pre-finish refuses.
- **Entry-pin failure**: `test_v_0_62_0_pvfs_1_entry_present_in_repo` raises AssertionError with the specific anchor missing (`PVFS-1` / `ADR-056` / `mints a new rule` / `supersedes nothing` / etc.) per the slice-051 content-bearing pin pattern.
- **Consumer-propagation failure**: `test_v_0_62_0_pvfs_1_shippability_consumer_propagation` raises AssertionError if shippability row #54 lacks the `PVFS-1` rule-ID anchor (post-row-enrichment).
- **AVFS-1 failure on installed leg**: AVFS-1's existing HALT semantics fire if `~/.claude/ai-sdlc-VERSION` is not bumped to 0.62.0 (build-time, not runtime, surface).

## Mid-slice smoke gate (operational expansion)

The mission-brief mid-slice smoke gate applies after the pyproject.toml `[project].version` bump. With Route B chosen, the bump literal must be `"0.62.0"` (NOT `"0.61.0"`) because VERSION will also be bumped to 0.62.0 as part of the atomic 4-part PMI-1 bump. The repro test asserts equality with whatever VERSION currently reads — so if VERSION bump happens BEFORE pyproject bump, the test will FAIL at `'0.20.0' == '0.62.0'`; if pyproject bumps first, the test will FAIL at `'0.62.0' == '0.61.0'`. **Recommended build order**: bump VERSION + plugin.yaml + ai-sdlc-VERSION + pyproject.toml together (atomic), THEN run the smoke gate. Out-of-order bumps that pass the smoke gate falsely-green are the slice-054 self-violation hazard.

## Pre-finish gate (design-time expansion of the mission-brief checklist)

In addition to the mission-brief Pre-finish gate items:

- [ ] Atomic 4-part PMI-1 bump VERIFIED (no leg lags the others): `VERSION` + `plugin.yaml.version` + `methodology-changelog ## v0.62.0` header + `~/.claude/ai-sdlc-VERSION` all read `0.62.0` (the AVFS-1 and PMI-1 audits at Step 6 catch any lag).
- [ ] ADR-056 file exists at `architecture/decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md` (lowercase-kebab-case per ADR-naming convention; INST-1 / CSP-1 cover the naming axis).
- [ ] methodology-changelog v0.62.0 entry carries all 7 entry-pin anchors (`PVFS-1`, `ADR-056`, `Pyproject Version Forward Sync`, `mints a new rule`, `supersedes nothing`, `Rule reference`, `4-part PMI-1 atomic bump`).
- [ ] shippability row #54 enriched with `PVFS-1` rule-ID anchor (in addition to the existing `SC-001` anchor).
- [ ] Both new entry-pin tests pass under genuine FAIL-then-PASS contrast (slice-053 M2 multi-site-literal-contrast law — verify the pin FAILS pre-edit / PASSES post-edit; pin must be non-tautological).
- [ ] No `BC-1` Critical applicable post-edit; SCMD-1 / PTFCD-1 / PTFFD-1 / STP-1 all clean on the new test files (slice-037 PTFFD-1 phantom-fn class; slice-044 STP-1 stale-pin class).
- [ ] BCR-1 mission-brief.md `**Closes:** SC-001` sentinel present at top of mission-brief.md (already verified; AC4 trigger).
