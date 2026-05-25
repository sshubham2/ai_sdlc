# Design: Slice 013 refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class

**Date**: 2026-05-13
**Mode**: Standard

## What's new

- A new **7th sub-clause** appended to `agents/critique.md` Dimension 9 ("Cross-cutting conformance") with canonical literal title `Entry-pin-vs-PMI-1-gate semantics conflation`, placed BETWEEN the existing 6th sub-clause `Recursive self-application discipline` (L168-L172) and the existing `### Bonus: weak graph edges` H3 (L174). Body documents BOTH sub-modes: **build-time slip mode** (slice-011 N=1) + **design-time-pre-empted success mode** (slice-012 N=2). Cross-slice anchors formalized per slice-011 `_cites_at_least_two_cross_slice_anchors` precedent (post-M2 ACCEPTED-FIXED at /critique):
  - **Cross-slice anchors (strict-both)**: `["slice-011", "slice-012"]` — both MUST be present in the 7th sub-clause body
  - **Substantive-discipline anchors (≥2 of 4)**: `["Phase 1b INSERT", "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]` — at least 2 of these 4 MUST be present in the 7th sub-clause body
- A new `~/.claude/agents/critique.md` mirror (Phase 2 forward-sync target; CAD-1 byte-equality invariant from slice-007).
- A new `methodology-changelog.md` v0.28.0 entry naming **EPGD-1** as the new methodology rule reference (in-repo + installed). Rule-ID convention: **EPGD** = Entry-Pin-Gate-Discipline; -D suffix per slice-011 B5 calibration-trail discipline N=2 stable (signals prose-heuristic applied at /critique-time + /build-slice-time, distinct from audit-enforced-gate sibling rules BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1, each of which has a corresponding `tools/*_audit.py`).
- 3 new test functions in `tests/methodology/test_critique_agent.py`: `test_critique_dim_9_entry_pin_vs_pmi_1_gate_sub_clause_present` + `test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned` + `test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012`.
- 1 superseded structural-invariant test: `test_critique_dim_9_lists_seven_sub_clauses` replaces `test_critique_dim_9_lists_six_sub_clauses` (PMI-1 structural-invariant supersession discipline per slice-011 N=1 precedent; no two structural-invariant tests coexist).
- 1 mini-CAD-1 row 3 regression-guard: `test_critique_dim_9_recursive_self_application_sub_clause_present` (slice-011's 6th-sub-clause-substring-pin) — already exists, follows PASSING → WRITTEN-FAILING → PASSING transition per slice-007/009/010/011/012 N=5 stable pattern.
- 1 new test in `tests/methodology/test_methodology_changelog.py`: `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` (3-pin shape: `## v0.28.0` heading + `EPGD-1` rule-ID + substantive canonical phrase `Entry-pin-vs-PMI-1-gate semantics conflation`).
- 1 superseded PMI-1 versioned-gate: `test_plugin_yaml_version_matches_version_file_at_0_28_0` replaces `_at_0_27_0` (slice-012's gate). PMI-1 supersession N=6 events stable post-slice-013.
- Atomic version bump: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all `0.27.0` → `0.28.0`.
- `architecture/shippability.md` row 13 added; row 12 header updated to note slice-013 supersession of slice-012's `_at_0_27_0` PMI-1 gate.
- ADR-012 — Promote entry-pin-vs-PMI-1-gate-discipline to agents/critique.md Dim 9 7th sub-clause via append-new (EPGD-1).

## What's reused

- [[agents/critique.md]] — the canonical Critic-prompt body; slice-013 appends ONLY at L172-L173 boundary; existing 6 sub-clauses + Dim 1-8 + Bonus section untouched.
- [[architecture/decisions/ADR-005-add-cross-cutting-conformance-9th-critic-dimension]] — CCC-1 v1 introduced Dim 9 with 5 sub-clauses. EPGD-1 extends Dim 9's enumeration to 7 sub-clauses (slice-011 grew 5 → 6; slice-013 grows 6 → 7) — additive sibling, not superseding ADR-005.
- [[architecture/decisions/ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class]] — CCC-1 v1.1; inline-refinement-of-existing-sub-clause-body precedent (slice-009). EPGD-1 follows ADR-010 append-new precedent instead (slice-011), not ADR-008 inline-refinement, because EPGD-1 is a distinct Edit-discipline (not extending an existing sub-clause body).
- [[architecture/decisions/ADR-010-promote-recursive-self-application-discipline-to-critique-dim-9-sub-clause]] — RSAD-1 (slice-011); the canonical structural-shape reference for slice-013 (append-new sub-clause + PMI-1 structural-invariant supersession + -D-suffix rule-ID convention + 5-prose-pin-tests scaffolding).
- `tests/methodology/test_critique_agent.py` — existing 25+ tests from slice-006..011 + slice-012's growth (the structural-invariant `_lists_six_sub_clauses` + location-pin + canonical-substring + cross-slice anchors). Slice-013 supersedes `_lists_six_sub_clauses` → `_lists_seven_sub_clauses`; adds 3 new tests; deletes 0 (existing tests preserved per backward-compat covenant per slice-011 + slice-012 Critic findings B1 class).
- `tests/methodology/test_methodology_changelog.py` — existing entry-pin functions for v0.22.0..v0.27.0 (6 functions total post-slice-012 build). Slice-013 supersedes only the PMI-1 versioned-gate function `_at_0_27_0` → `_at_0_28_0`; ALL 6 entry-pin functions persist untouched per the very EPGD-1 discipline this slice authors (RSAD-1 self-application — slice's own ship is the canonical reference instance).
- `tools/plugin_manifest_audit.py` — PMI-1 audit; reused unchanged. Verifies `VERSION` + `ai-sdlc-VERSION` + `plugin.yaml.version` atomicity post-bump.
- `tools/critique_agent_drift_audit.py` — CAD-1 audit; reused unchanged. Verifies in-repo↔installed `agents/critique.md` byte-equality.
- `tools/build_checks_audit.py` — BC-1 audit; reused unchanged. Negative-anchor mechanism (BC-1 v1.3 / slice-012) silences slice-013's own mission-brief + design.md methodology-vocabulary firing.
- `tools/test_first_audit.py` — TF-1 audit; reused unchanged. Verifies 8-row TF-1 plan at pre-finish.
- [[methodology-changelog.md]] — v0.21.0 (CCC-1 v1) + v0.24.0 (CCC-1 v1.1) + v0.26.0 (RSAD-1) lineage; v0.28.0 (EPGD-1) is the next entry. slice-007's PMI-1 escape-closure invariant atomically bumps all 3 surfaces at slice end.
- `architecture/shippability.md` — 12-row catalog from slice-012; row 12 references slice-012's critical path; slice-013 appends row 13 + updates row 12 header per the slice-008/009/010/011/012 convention.

## Components touched

### `agents/critique.md` — Dim 9 sub-clause enumeration

- **Responsibility**: canonical Critic-prompt body read by every `/critique` invocation. Dim 9 enumerates cross-cutting-conformance sub-classes; slice-013 adds the 7th.
- **Lives at**: `agents/critique.md` (modified — single append between L172 and L174)
- **Key interactions**: read by `agents/critique.md`'s consumer (the `Agent({subagent_type: "critique"})` invocation in `~/.claude/skills/critique/SKILL.md`); byte-equal mirror at `~/.claude/agents/critique.md` (forward-sync target).

### `~/.claude/agents/critique.md` — installed mirror

- **Responsibility**: byte-equal mirror of in-repo `agents/critique.md`; the file actually read by the Critic agent at runtime.
- **Lives at**: `~/.claude/agents/critique.md` (modified — full replacement to match in-repo post-edit)
- **Key interactions**: read by Claude Code's Agent dispatcher at /critique invocation; sha256 byte-equality enforced by CAD-1 audit (`tools/critique_agent_drift_audit.py`).

### `methodology-changelog.md` — v0.28.0 entry

- **Responsibility**: append-only changelog of behavior-changing rules in the AI SDLC pipeline. v0.28.0 entry codifies EPGD-1.
- **Lives at**: `methodology-changelog.md` (in-repo) + `~/.claude/methodology-changelog.md` (installed mirror)
- **Key interactions**: read by `/status` for surfacing methodology metadata; pinned bidirectionally by `tests/methodology/test_methodology_changelog.py` entry-pin functions; PMI-1 atomic version bump invariant per slice-007 escape-closure.

### `tests/methodology/test_critique_agent.py` — 3 new test functions + 1 superseded structural-invariant

- **Responsibility**: prose-pin tests on `agents/critique.md` body. Asserts canonical literal substrings + structural invariants + location pins.
- **Lives at**: `tests/methodology/test_critique_agent.py` (modified — 3 added + 1 replaced)
- **Key interactions**: loaded by pytest; reads in-repo `agents/critique.md` content via module-level `CRITIQUE = (Path(__file__).parents[2] / "agents" / "critique.md").read_text(encoding="utf-8")`.

### `tests/methodology/test_methodology_changelog.py` — 1 new entry-pin + 1 superseded PMI-1 gate

- **Responsibility**: bidirectional changelog-entry pins (per shipped version) + PMI-1 versioned-gate function (one at a time).
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (modified — 1 added + 1 replaced — Edit narrow-scoped per EPGD-1 self-application)
- **Key interactions**: loaded by pytest; reads in-repo + installed `methodology-changelog.md` for entry-pin asserts; reads `plugin.yaml` + `VERSION` + `~/.claude/ai-sdlc-VERSION` for PMI-1 gate.

## Contracts added or changed

None. Slice introduces no API endpoints, events, or external integrations. Pure prompt-prose addition + changelog entry + version bump.

## Data model deltas

None. No DB schema, no migration, no data-model field changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Slice introduces NO new `.py` modules. Empty matrix is treated as clean by `tools/wiring_audit.py`.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-012]] — Promote entry-pin-vs-PMI-1-gate-discipline to agents/critique.md Dim 9 7th sub-clause via append-new (EPGD-1) — reversibility: cheap

## Authorization model for this slice

Not applicable. Slice modifies prose content in canonical methodology files; no runtime authorization decisions are introduced. Edits to `agents/critique.md` + `methodology-changelog.md` + `VERSION` are governed by repository write access (existing — slice-013 is authored by the project owner per the existing developer flow).

## Error model for this slice

Slice introduces no runtime error codes. Build-time error surfaces are existing audit failures:

- **CAD-1 byte-equality failure** (`tools/critique_agent_drift_audit.py` exit 1 with `content-drift`) — fires at /build-slice Phase 2 mid-slice smoke if in-repo `agents/critique.md` edited but installed mirror not yet forward-synced. Expected at mid-slice gate; must be exit 0 at pre-finish gate.
- **PMI-1 atomicity failure** (`tools/plugin_manifest_audit.py` exit 1 with version mismatch) — fires if `VERSION` / `ai-sdlc-VERSION` / `plugin.yaml.version` get out of sync at Phase 1d. Mitigation: atomic 3-file edit in single commit per slice-007 escape-closure pattern.
- **TF-1 strict-pre-finish failure** (`tools/test_first_audit.py --strict-pre-finish` exit 1) — fires if any TF-1 row is non-PASSING at Phase 6 pre-finish. Mitigation: 8-row TF-1 plan locked at mission-brief; transitions tracked per slice-011/012 PENDING → WRITTEN-FAILING → PASSING discipline.
- **BC-1 self-application firing** (`tools/build_checks_audit.py --slice architecture/slices/slice-013-...` reports `applicable=[BC-PROJ-1]` Important or similar) — slice's own mission-brief + design.md carry methodology-vocabulary anchors. Mitigation: BC-1 v1.3 negative-anchor mechanism (slice-008 + slice-012 — uniform 9-token set on BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1) silences ALL three project-relevant rules. Expected post-build result: `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` (10-of-9 or 9-of-9 over-determination per slice-012 self-application pattern N=10 → N=11 ratchet).
- **EPGD-1 self-application failure** (post-Phase 1c Edit, any of v_0_22_0..v_0_27_0 entry-pin tests FAIL) — fires if the slice's own PMI-1 supersession Edit accidentally spans entry-pin function definitions. Mitigation: Phase 1b INSERT under new `# --- Slice-013 / EPGD-1 entry pinning ---` SECTION header BEFORE Phase 1c Edit; Phase 1c Edit `old_string` scoped to the existing `# --- PMI-1 cleanliness gate at v0.27.0 ---` SECTION header + the gate function body ONLY. Pre-Edit empirical structural-separation audit (per slice-012 Audit 6 pattern) verifies the two SECTION headers don't share prose. **This is the slice's own canonical reference-instance verification of the EPGD-1 discipline it authors** (RSAD-1 self-application N=5 cumulative).

## Sub-clause canonical body (the exact prose appended to critique.md Dim 9)

For Critic reviewability, the canonical body of the new 7th sub-clause is reproduced here. The actual append insertion point is `agents/critique.md` L172↔L174 boundary (between L172 RSAD-1 close and L174 `### Bonus: weak graph edges` H3).

```markdown
- **Entry-pin-vs-PMI-1-gate semantics conflation** — N=2 sub-clause (slice-011 N=1 build-time slip surfaced at /validate-slice Step 5.5 + slice-012 N=2 design-time-pre-empted success at /design-slice + /critique); peer cross-reference: none — operates at the methodology Edit-discipline level, distinct from the meta-level recursive-self-application discipline above. The methodology distinguishes TWO function classes in `tests/methodology/test_methodology_changelog.py`: **entry-pin functions** (one per shipped versioned changelog entry; ALL persist across slices — the v0.22.0 entry-pin coexists with v0.23.0, v0.24.0, ..., v0.N entry-pins; never deleted) AND **PMI-1 versioned-gate functions** (exactly one at a time; superseded each version bump per slice-007 introduction → slice-008..012 supersession; N=5 supersession events stable post-slice-012). When superseding a PMI-1 versioned-gate test via the Edit tool's `old_string` / `new_string` parameters, scoping the Edit block to span a SECTION header (`# --- Slice-NNN / <rule> entry pinning ---`) + an entry-pin function + the PMI-1 gate function — and replacing the whole block with the new version's section — silently deletes the prior version's entry-pin function. Two distinct sub-modes:
  - **Build-time slip mode** — at /build-slice Phase 1c, an Edit `old_string` spans both an entry-pin function AND the PMI-1 versioned-gate function via a shared SECTION header (because the developer drafts the Edit block visually from the file's then-current contiguous block layout); replacement silently deletes the entry-pin function. Concrete miss: slice-011 N=1 (Critic-MISSED at /critique; an Edit-tool-scoping discipline is not a design semantic the pre-RSAD-1 Critic prompt covered) — caught at /validate-slice Step 5.5 by shippability catalog row regression check (the row's pytest command referenced the deleted test); fixed in-line at validate-time by re-adding the entry-pin function between the adjacent versions' entry-pins.
  - **Design-time-pre-empted success mode** — at /design-slice / /critique, the slice authoring a methodology refinement explicitly plans Phase 1b INSERT for the new version's entry-pin function under a NEW dedicated SECTION header — placed separately from the PMI-1 gate's dedicated SECTION header — followed by Phase 1c narrow-scope Edit on the PMI-1 gate function body + its dedicated SECTION header ONLY. A pre-Edit empirical structural-separation audit at /design-slice verifies the two SECTION headers don't share intervening prose. Post-build empirical confirmation: all prior versions' entry-pin functions PASS unchanged; only the PMI-1 gate function body changes. Concrete catch: slice-012 N=2 (Critic M1 ACCEPTED-FIXED at /critique; slice-011's NEW Dim 9 sub-class candidate at N=1 ratcheted to N=2 promotion threshold MET).

  When reviewing a slice that supersedes a PMI-1 versioned-gate, the Critic SHOULD: (1) verify the /design-slice phase plan separates the new version's entry-pin INSERT (Phase 1b) from the PMI-1 gate supersession Edit (Phase 1c) into structurally distinct artifacts in `tests/methodology/test_methodology_changelog.py` (each under its own dedicated SECTION header); (2) verify the Phase 1c Edit's `old_string` scope is narrow — gate function body + its dedicated SECTION header only — and does NOT span entry-pin function definitions for ANY version (current or prior); (3) require a pre-Edit empirical structural-separation audit at /design-slice (mirrors slice-012 Audit 6) confirming entry-pin SECTION headers and PMI-1 gate SECTION header don't share intervening prose. Slices that fail to plan structural separation at /design-slice carry build-time entry-pin-deletion risk equivalent to slice-011 N=1 build-time slip.
```

## Phase plan (informs /build-slice)

Detailed for the Critic + Builder. Annotated with where EPGD-1 self-application applies.

- **Phase 0** — sha256 forensic capture (baseline). Capture in-repo + installed sha256 for: `agents/critique.md`, `methodology-changelog.md`, `ai-sdlc-VERSION`. Captured in `build-log.md`.
- **Phase 1a** — Edit `agents/critique.md` between L172↔L174 inserting the 7th sub-clause canonical body. Verify location-pin anchors unique at this stage.
- **Phase 1b** — INSERT new entry-pin function `test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` in `tests/methodology/test_methodology_changelog.py` under a NEW dedicated SECTION header `# --- Slice-013 / EPGD-1 entry pinning ---` PLACED BEFORE the existing `# --- PMI-1 cleanliness gate at v0.27.0 ---` SECTION header. The two SECTION headers are structurally separated (no shared intervening prose other than blank lines).
- **Phase 1c** — Edit narrow-scoped on the PMI-1 versioned-gate function ONLY. `old_string` MUST span ONLY: the line `# --- PMI-1 cleanliness gate at v0.27.0 ---` + the function `test_plugin_yaml_version_matches_version_file_at_0_27_0` body. `new_string` MUST replace with: `# --- PMI-1 cleanliness gate at v0.28.0 ---` + the renamed function `test_plugin_yaml_version_matches_version_file_at_0_28_0`. **EPGD-1 self-application check**: pre-Edit structural-separation audit verifies the Phase 1b INSERT placed the new entry-pin function ABOVE the PMI-1 gate SECTION header — no entry-pin function appears within the `old_string` scope. Post-Edit pytest sanity check: all 6 prior entry-pin functions (v_0_22_0..v_0_27_0) still PASS.
- **Phase 1d** — Atomic version bump: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all `0.27.0` → `0.28.0` in single commit. PMI-1 audit clean post-edit (`python -m tools.plugin_manifest_audit --root .` exits 0).
- **Phase 1e** — Edit `agents/critique.md` line 4 if needed to update `description` (deferred to slice-end if no change needed — Dim count is already 9 from slice-006). Append v0.28.0 entry to `methodology-changelog.md` (in-repo).
- **Phase 1f** — Add 3 new test functions to `tests/methodology/test_critique_agent.py` (canonical-substring + location-pin + cross-slice anchors). Supersede `_lists_six_sub_clauses` → `_lists_seven_sub_clauses` per PMI-1 structural-invariant supersession discipline (delete old, add new — slice-011 N=1 precedent). The mini-CAD-1 row 3 regression-guard test `_recursive_self_application_sub_clause_present` PASSING throughout.
- **Phase 2** — Forward-sync `agents/critique.md` + `methodology-changelog.md` to `~/.claude/`. CAD-1 audit clean post-sync.
- **Phase 3** — Sub-build sanity: `pytest tests/methodology/test_critique_agent.py tests/methodology/test_methodology_changelog.py -q` PASS.
- **Phase 4** — Full methodology suite: `pytest tests/methodology/ -q` PASS. BC-1 self-application audit on slice-013's own mission-brief + design.md: expected `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` per slice-012 BC-PROJ-2 negative-anchor migration (BC-1 v1.3). Bidirectional sha256 forensic capture (post-edit).
- **Phase 5** — Shippability catalog row 13 added; row 12 header updated.
- **Phase 6** — Pre-finish gates: TF-1 strict-pre-finish + PMI-1 clean + CAD-1 clean + drift-check clean + EPGD-1 self-application empirical confirmation.

## Out-of-repo files touched

| File | Operation | Verification |
|------|-----------|--------------|
| `~/.claude/agents/critique.md` | Forward-sync from in-repo `agents/critique.md` post-edit | sha256 byte-equality via `tools/critique_agent_drift_audit.py` exit 0 |
| `~/.claude/methodology-changelog.md` | Forward-sync from in-repo `methodology-changelog.md` post-edit | sha256 byte-equality (Phase 4 forensic capture) |
| `~/.claude/ai-sdlc-VERSION` | Atomic bump from `0.27.0` to `0.28.0` (install-time rename of in-repo `VERSION`) | `python -m tools.plugin_manifest_audit --root .` exit 0 (PMI-1 invariant) |

Note (per slice-007 Critic B1 lesson + slice-009 CCC-1 v1.1 design-md-mechanical-tables canonical inventories sub-clause): in-repo file is `VERSION`; the install-time rename to `ai-sdlc-VERSION` happens via `INSTALL.md` Step 3f-equivalent. The "Out-of-repo files touched" table above names the INSTALLED filename `ai-sdlc-VERSION` per Dim 9 sub-clause 2's install-time-rename surface convention. `plugin.yaml` is NOT installed (on `INSTALL.md` Step 3f do-not-copy list per slice-006 DEVIATION-1 lesson); its `version` field is in-repo only.

## Pre-AC-lock empirical audits (per slice-009/010/011/012 discipline N=11 stable)

These were run BEFORE the mission-brief ACs were locked. Documented for /critique to reference.

**Audit 1 — Location-pin anchor uniqueness** (slice-009 DEVIATION-2 + slice-010 anchor-uniqueness pre-emption pattern):

- Substring `Recursive self-application discipline` in `agents/critique.md` → exactly 1 occurrence (L168). ✅ Unique anchor.
- Substring `### Bonus: weak graph edges` in `agents/critique.md` → exactly 1 occurrence (L174). ✅ Unique anchor.
- The location-pin test (AC #1 row 2) uses `text.find()` with verified-unique anchors; no first-occurrence-wins collision risk per slice-009 DEVIATION-2 lesson.

**Audit 2 — Canonical literal substring absence** (slice-010 absence-discipline pattern):

- Substring `Entry-pin-vs-PMI-1-gate semantics conflation` in `agents/critique.md` → 0 occurrences (clean slate). ✅ Pre-fix, all 3 canonical-substring-pin tests (AC #1 row 1 + AC #2 row 1) genuinely FAIL with `AssertionError: '<phrase>' not in CRITIQUE` per TF-1 PENDING → WRITTEN-FAILING genuine-failure discipline N=9 stable.

**Audit 3 — BC-1 self-application prediction** (slice-010 + slice-011 + slice-012 pattern N=8 stable; RSAD-1 build-time sub-mode):

- Slice-013's mission-brief + design.md + ADR-012 mention BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 positive anchors AS HISTORICAL CONTEXT for the EPGD-1 discipline. Per BC-1 v1.3's negative-anchor mechanism (slice-008 + slice-012): all 3 project-relevant rules carry the uniform 9-token methodology-vocabulary negative-anchor set (`defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`). At /build-slice Phase 4 BC-1 self-application, expected: `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` (all 3 silenced by 9-of-9 over-determination). The expectation pre-empts the slice-010 DEVIATION-3 build-time recursive-self-application sub-mode RSAD-1 codifies; slice-013 itself uses abstract anchor descriptions in the canonical critique.md body (per slice-011 Critic M1 stylistic / readability rationale + slice-010 DEVIATION-3 lesson) so the canonical `agents/critique.md` artifact is BC-1-clean at post-slice audits.

**Audit 4 — EPGD-1 self-application pre-Edit structural-separation prediction** (mirrors slice-012 Audit 6):

- Current `tests/methodology/test_methodology_changelog.py` (post-slice-012 build) carries 6 entry-pin functions (v_0_22_0..v_0_27_0) + 1 PMI-1 gate function (`_at_0_27_0`). At /build-slice Phase 1b, slice-013 INSERTs the v_0_28_0 entry-pin function under a NEW `# --- Slice-013 / EPGD-1 entry pinning ---` SECTION header placed structurally BEFORE the existing `# --- PMI-1 cleanliness gate at v0.27.0 ---` SECTION header. Post-Phase-1b structural-separation: the new entry-pin SECTION header (NEW slice-013) sits ABOVE the PMI-1 gate SECTION header; no shared prose between them other than blank lines. Phase 1c Edit `old_string` scope is the PMI-1 gate SECTION header + its function body ONLY — does NOT include the new entry-pin SECTION header or function. Audit confirms structural separation pre-Edit; predicts ALL 6 prior entry-pin functions PASS unchanged post-Edit + the new v_0_28_0 entry-pin function PASSES post-Phase-1b.

**Audit 5 — Recursive self-application discipline self-check** (per RSAD-1 / slice-011):

The slice authoring EPGD-1 IS itself an instance of the discipline it encodes: at /build-slice Phase 1c, slice-013 supersedes a PMI-1 versioned-gate (slice-012's `_at_0_27_0` → slice-013's `_at_0_28_0`) — the EXACT operation EPGD-1 governs. Slice-013's own ship is the canonical reference instance of EPGD-1 (mirrors slice-011's RSAD-1 self-application + slice-012's BC-PROJ-2-migration self-application). Audit 4 above empirically pre-verifies that slice-013's own Phase 1b + Phase 1c respect EPGD-1's structural-separation discipline. **Slice fails its own discipline at build time → EPGD-1's design-time pre-emption claim is empirically falsified at the very slice that codified it**. Critic SHOULD verify Audit 4's plan is concrete (not aspirational) — the /design-slice phase plan above specifies the exact `old_string` scope and the exact SECTION-header structural separation.

**Audit 6 — RSAD-1 build-time-via-/critique-fix-prose sub-mode prediction**:

Per slice-010 DEVIATION-3 / slice-011 + slice-012 RSAD-1 design-time pre-emption pattern: if at /critique fix prose adds empirical-rebuttal anchor descriptions (e.g., literal BC-PROJ-1/2/GLOBAL-1 positive-anchor substrings or PMI-1 versioned-gate function names with specific version numbers different from current 0.28.0), those substrings might trigger BC-1 audit or other audits at Phase 4 self-application. Mitigation per Audit 3: BC-1 v1.3 negative-anchor mechanism silences BC-PROJ-1/2/GLOBAL-1 on methodology-vocabulary slices; PMI-1 gate version-number substrings (`_at_0_22_0`..`_at_0_28_0`) are not BC-1 positive anchors. No expected build-time recursive-self-application fire.

## Recursive self-application N=5 cumulative

This slice (slice-013) is the **5th cumulative recursive-self-application instance** post-RSAD-1 codification:

- N=1 slice-009 M2 (design-time, pre-RSAD-1)
- N=2 slice-010 design-time stress-test B1+M1+B5 + build-time DEVIATION-3 (pre-RSAD-1)
- N=3 slice-011 (4 of 7 findings on own draft, post-RSAD-1)
- N=4 slice-012 (B1 on own draft: naive substring verification approach couldn't enforce its own data, post-RSAD-1)
- **N=5 slice-013 (this slice — the EPGD-1 discipline applies to slice-013's own Phase 1c PMI-1 supersession Edit; slice's own ship is the canonical reference instance; post-RSAD-1)**

The Critic at /critique SHOULD stress-test slice-013's design.md prose against EPGD-1 itself: does the phase plan above respect EPGD-1's structural-separation discipline at Phase 1b + Phase 1c? See Audit 4 + Audit 5 for the empirical pre-verification.
