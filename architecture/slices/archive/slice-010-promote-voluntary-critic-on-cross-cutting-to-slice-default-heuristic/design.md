# Design: Slice 010 promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic

**Date**: 2026-05-12
**Mode**: Standard (per slice-009 archive — most recent active mode)
**Risk tier**: medium; **critic-required**: true with dual rationale:
- (a) **OLD heuristic (pre-promotion)**: voluntary Critic on cross-cutting tooling slices is N=9/9 paid off across slices 1-9 (every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; cumulative-post-build framing per Critic B1 honest reading); running 36/36 Critic-VALIDATED at /critique-disposition across slices 6-9 (strongest streak in the project).
- (b) **NEW heuristic (self-applying)**: slice-010 modifies `skills/slice/SKILL.md` — exactly the in-house methodology surface the new bullet covers. Under the heuristic this slice encodes, slice-010 itself qualifies for `critic-required: true`. Recursive-self-application class per slice-009 M2 phenomenon (slice-009 caught its own draft committing the design-doc-vs-canonical-inventory drift it was encoding — N=1; slice-010 ratchets to N=2 candidate post-completion). Critic at /critique stress-tested slice-010's own draft and surfaced 5 blockers + 3 majors + 3 minors — most addressing rule-class violations in the slice's own prose (B1 internal inconsistency in the load-bearing N=9/9 framing; B3 ADR-009 enumeration drift; M1 bullet-style asymmetry diverges from existing list convention; B5 rule-naming convention break — addressed via this design revision).

## What's new

- **MCT-1 — `/slice` Step 4a "In-house methodology surfaces" mandatory-Critic trigger** (new methodology rule; rename from working-draft "MCR-1 Mandatory Critic Rule" per Critic B5 — the -T- distinguishes /slice-time trigger semantics from audit-enforced gate semantics of siblings BC-1 / PMI-1 / CAD-1 / TF-1, none of which has the same prose-only enforcement shape). Per Critic M1 split, the slice introduces TWO additions to `skills/slice/SKILL.md` Step 4a — not a single multi-clause bullet:

  - **Addition 1: terse bullet** matching the existing 7 bullets' style, inserted **between the existing `Security-sensitive paths` bullet and the existing `Heavy mode (always)` bullet** (content-trigger bullets grouped before the mode-meta closer; line numbers cited as-of-2026-05-12 in ADR-009 once, symbolic references thereafter per Critic m1):
    ```
    - In-house methodology surfaces (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`)
    ```
    Canonical literals pinned (per AC #1 — bullet substrings): `In-house methodology surfaces` (capitalized-I bullet-title form — DEVIATION-1 mitigation: bold not used at bullet start; literal case preserved) + at least one of the file-class anchors `skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md` (canonical-inventory completeness — design selects all 4).
  - **Addition 2: evidence prose paragraph** placed AFTER the existing "When producing the mission brief..." paragraph (lines 173-174 of current SKILL.md state) — markdown blockquote keeps it visually distinct from the bullet list and from the regular prose:
    ```
    > **Evidence for the In-house methodology surfaces trigger**: voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 in this project's reflection record (e.g., slice-006 INST-1 inventory drift; slice-007 install-time rename; slice-008 negative-anchor uniformity; slice-009 recursive self-application). Every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; see `architecture/slices/_index.md` "Aggregated lessons" and `archive/slice-NNN/reflection.md` "Critic calibration" sections for per-slice disposition records.
    ```
    Canonical literals pinned (per AC #1 row 3 + AC #2 — evidence paragraph substrings): `N=9/9` (case-sensitive — slice-009 lesson framing) + `voluntary Critic` (lowercase-v body-prose form — DEVIATION-1 mitigation: phrase placed mid-sentence post-`N=9/9 voluntary Critic catch payoff` per literal case) + ≥2 of {`slice-006`, `slice-007`, `slice-008`, `slice-009`} cross-slice anchors. Per Critic M3 ACCEPTED-PENDING: at /build-slice also pin ≥2 of {`INST-1 inventory drift`, `install-time rename`, `negative-anchor uniformity`, `recursive self-application`} sub-class anchors (TF-1 plan row added).
    Honest framing per Critic B1 + B3: drops the previously-drafted "8 of 9 design-stage catches" sub-claim, which was internally inconsistent with the project's running counter across slice-007 (off-by-one) and slice-008 → slice-009 (counting-rule change). The cumulative-post-build framing "every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs" is the verifiable interpretation supported by every slice 1-9 reflection's `## Critic calibration` section.
- **`~/.claude/skills/slice/SKILL.md`** (out-of-repo) — Phase 2 forward-sync target. Same bullet insertion applied; per-file mini-CAD-1 byte-equality test verifies at slice end (AC #3).
- **`tests/methodology/test_slice_skill.py`** (NEW file) — 4 prose-pin tests for AC #1 + AC #2 (Critic M3 ACCEPTED-PENDING adds a 5th sub-class-anchor row at /build-slice — TF-1 plan grows 7 → 8 rows):
  - `test_slice_step4a_mandatory_critic_section_contains_in_house_methodology_surfaces_bullet` (AC #1 row 1) — asserts canonical literal `In-house methodology surfaces` present in `skills/slice/SKILL.md` (case-sensitive substring) within the Step 4a section bounds (start anchor `Always mandatory Critic`, end anchor `### Step 5:`).
  - `test_slice_step4a_in_house_methodology_bullet_location_between_security_paths_and_heavy_mode` (AC #1 row 2; M1 location-pin per slice-009 lesson) — asserts the new bullet's canonical phrase appears BETWEEN the existing `Security-sensitive paths` bullet and the existing `Heavy mode (always)` bullet (so the bullet's position within the bullet list is precisely pinned). Test impl uses scoped `text.find()` chained off the section start anchor — empirically verified at design time all three anchors (`Security-sensitive paths`, `Heavy mode (always)`, `Always mandatory Critic`) appear exactly once in `skills/slice/SKILL.md` (pre-empts slice-009 DEVIATION-2 `.find()`-collision class).
  - `test_slice_step4a_evidence_paragraph_cites_n_9_and_voluntary_critic` (AC #1 row 3) — asserts canonical literals `N=9/9` AND `voluntary Critic` (case-sensitive lowercase-v) both present within the Step 4a section bounds (widened end anchor `### Step 5:` so the evidence prose paragraph below the bullet list also falls within scope per Critic M1 split).
  - `test_slice_step4a_evidence_paragraph_cites_at_least_two_cross_cutting_tooling_slices` (AC #2) — asserts count ≥2 of canonical substrings `slice-006`, `slice-007`, `slice-008`, `slice-009` present in the evidence paragraph scoped to the Step 4a section bounds.
  - `test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors` (AC #2 sub-row; ACCEPTED-PENDING from Critic M3; added at /build-slice) — asserts count ≥2 of canonical substrings `INST-1 inventory drift`, `install-time rename`, `negative-anchor uniformity`, `recursive self-application` present in the evidence paragraph scoped to the Step 4a section bounds. Pins the sub-class evidence so a future cleanup deleting them surfaces as a test failure.
- **`tests/methodology/test_slice_skill_drift.py`** (NEW file) — 1 byte-equality test for AC #3:
  - `test_in_repo_and_installed_slice_skill_md_are_content_equal` — mini-CAD-1 shape (mirrors slice-007's `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal`). Computes sha256 of in-repo `skills/slice/SKILL.md` + installed `~/.claude/skills/slice/SKILL.md`; raises `AssertionError` with both sha256 values on mismatch. Per-file scope-narrow assertion — does NOT generalize INST-2 (which remains deferred per slice-009 reflection at N=1 actual-drift evidence; slice-010 adds a per-file test mirroring CAD-1's pattern but does NOT build a generalized audit tool).
- **`methodology-changelog.md`** (in-repo + `~/.claude/`) — new H2 entry `## v0.25.0 — 2026-05-12` under `### Added` (new methodology rule MCT-1 vs `### Changed` for refinements). Title: "MCT-1 — `/slice` Step 4a 'In-house methodology surfaces' mandatory-Critic trigger (promotes voluntary-Critic-on-cross-cutting-tooling to default at N=9/9)". Body includes:
  - One-paragraph summary (mirrors v0.21.0 / v0.22.0 / v0.23.0 / v0.24.0 prose pattern).
  - Empirical-evidence-base citation: "voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 (every voluntary Critic invocation produced VALIDATED findings post-build with zero FALSE-ALARMs; cumulative-post-build framing per slice-N reflection records). Example sub-class anchors: slice-006 INST-1 inventory drift + slice-007 install-time rename + slice-008 negative-anchor uniformity + slice-009 recursive self-application. Running 36/36 Critic-VALIDATED at /critique-disposition across slices 6-9."
  - Substantive canonical phrase pinned bidirectionally per slice-008 M2 + slice-009 M3 N-surface schema-pin discipline: `In-house methodology surfaces` appears in BOTH in-repo + installed methodology-changelog.md AND in `skills/slice/SKILL.md` = 3 surfaces total.
  - Rule reference: MCT-1.
  - Defect class: "Cross-cutting tooling slices (modifying skill prose, agent prompts, in-house audit tooling, or methodology rules) routinely surface cross-cutting drift sub-classes (Dim 9 catch rate trajectory: 0% pre-CCC-1 → 25% / 60% / 100% / 60% across slices 6-9; range-bound 60-100% on N=4 evidence, NOT monotonic per slice-009 reflection) that user-facing-feature triggers (auth, API contracts, data model, sync, external integrations, security) do not enumerate. Without the new trigger, every cross-cutting tooling slice relies on per-slice voluntary opt-in to set `critic-required: true` — codification eliminates the voluntary-call friction at /slice time."
  - **Limitations** (per Critic B5; mirrors v0.24.0 prose pattern): "MCT-1 is /slice-time heuristic prose only, NOT an audit-enforced gate. The siblings BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 each have a corresponding `tools/*_audit.py` module that enforces the rule programmatically; MCT-1 has no such audit — the rule lives only in `skills/slice/SKILL.md` Step 4a prose, depending on the Claude main thread reading the bullet at /slice invocation and setting `critic-required: true` for matching slices. A future slice modifying in-house methodology surfaces but setting `critic-required: false` would NOT be caught by any audit. v2 candidate at slice-N+ if drift surfaces: build `tools/mct_1_audit.py` walking `architecture/slices/*/milestone.md` + `mission-brief.md` and asserting `critic-required: true` when slice scope references in-house methodology files. Adds scope (~0.5 day); deferred at slice-010 to keep this slice within the ~0.5-day budget."
  - Validation: names the 5 new prose-pin tests (4 at slice-010 + 1 ACCEPTED-PENDING M3 sub-class anchor row at /build-slice) + 1 mini-CAD-1 byte-equality test + 1 bidirectional changelog-pin test + 1 PMI-1 versioned-gate test.
- **`tests/methodology/test_methodology_changelog.py`** — add `test_v_0_25_0_mct_1_entry_present_in_repo_and_installed` (bidirectional pin per slice-007/008/009 precedent — asserts `## v0.25.0 —`, `MCT-1`, AND substantive canonical phrase `In-house methodology surfaces` in BOTH in-repo + installed changelog copies). REPLACE `test_plugin_yaml_version_matches_version_file_at_0_24_0` with `test_plugin_yaml_version_matches_version_file_at_0_25_0` (PMI-1 versioned-gate supersession per slice-007/008/009 N=2-stable pattern — no two version-gates coexist; slice-010 ratchets to N=3 supersession events on completion per Critic M5 framing at slice-009).
- **`VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`**: atomic bump 0.24.0 → 0.25.0 (PMI-1 invariant per slice-007 escape-closure pattern).
- **`architecture/shippability.md`** — add row 10 naming slice-010's critical path: Step 4a `In-house methodology surfaces` bullet + per-file mini-CAD-1 byte-equality on `skills/slice/SKILL.md` + v0.25.0 entry bidirectional pin + PMI-1 0.25.0 supersession. Update row 9 (slice-009) to note slice-010 supersedes the `_at_0_24_0` PMI-1 versioned-gate with `_at_0_25_0` (mirrors slice-008's row 7 update for slice-007's v0.22.0 gate + slice-009's row 8 update for slice-008's v0.23.0 gate).
- New ADR: [[ADR-009-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] — reversibility: **cheap** with magnitude justification per Critic m3 corrected count (~11-13 sites total: SKILL.md bullet + evidence-paragraph insert + ~/.claude mirror + methodology-changelog v0.25.0 entry + ~/.claude mirror + VERSION + ~/.claude/ai-sdlc-VERSION + plugin.yaml.version + 2 new test files + test_methodology_changelog.py edits + ADR-009 itself + shippability row 10 add + row 9 supersession update — closer in magnitude to ADR-007's ~10-15 sites than to ADR-008's ~5 sites). Minor irreversible portion: append-only changelog + cumulative slice-010-N Critic invocations gated by MCT-1 going forward.

## What's reused

- **`skills/slice/SKILL.md` Step 4a ground** — the 7 existing "Always mandatory Critic" bullets (Auth / API contracts / Data model / Multi-device sync / External integrations / Security-sensitive paths / Heavy mode (always)) are preserved unchanged. Slice-010 is additive: appends 1 bullet between L171 and L172.
- **CCC-1 v1 + v1.1 (slice-006 + slice-009)** — Dim 9 sub-clause 2 "Tooling-doc-vs-implementation parity" (now including the v1.1 design-doc-level surface) is the Critic-side rule MCR-1 governs at /critique time. Slice-010 doesn't modify CCC-1; it codifies WHEN the Critic-with-9-dim should run (the /slice-side heuristic).
- **CAD-1 audit pattern (slice-007)** — `tools/critique_agent_drift_audit.py` is the canonical example of a per-file byte-equality audit. Slice-010 mirrors the test shape (`test_in_repo_and_installed_<file>_are_content_equal`) for `skills/slice/SKILL.md` but does NOT build a generalized INST-2 audit tool. INST-2 remains deferred per slice-009 reflection at N=1 actual-drift evidence.
- **BC-1 v1.2 negative-anchor mechanism (slice-008)** — silences BC-PROJ-1 + BC-GLOBAL-1 on this slice's mission-brief + design (contains methodology-vocabulary anchors `aggregated lessons`, `back-sync`, `forward-sync`, `voluntary Critic`, `cross-cutting tooling`, `recursive self-application`). Empirically verified at design-time (see "Empirical verification" section).
- **PMI-1 atomic version bump pattern (slice-007/008/009 N=2 stable; N=3 supersession events post-slice-010)** — atomic across `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`. Slice-010 supersedes slice-009's `_at_0_24_0` gate with `_at_0_25_0`. The supersession act is justified by slice-009 reflection's explicit choice (no two version-gates coexist) + the in-repo VERSION file's monotonicity invariant, NOT by N=3 stability of supersession-events (slice-010 itself creates that N=3 on completion). Refactor candidate (`refactor-pmi-1-gate-to-version-agnostic-shape`) deferred 4 times post-slice-010 — approaching but not yet at the N≥4 friction threshold per slice-008 reflection.
- **TWO-surface schema-pin discipline generalized to N-surface (slice-007 + slice-008 lesson)** — slice-010 pins ONE substantive canonical phrase (`In-house methodology surfaces`) across N=3 surfaces (skills/slice/SKILL.md + in-repo methodology-changelog.md + installed methodology-changelog.md). Per slice-008 M2: N-substring discipline within AC #1 (4 distinct canonical literals: `In-house methodology surfaces` + file-class anchor + `N=9/9` + `voluntary Critic`).
- **Bidirectional sha256 forensic capture pattern (slice-005..009 N=5 stable)** — slice-010 captures sha256 for `skills/slice/SKILL.md` (in-repo + installed) + `methodology-changelog.md` (in-repo + installed) + `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) BEFORE Phase 2 forward-sync (Phase 0) and AFTER (Phase 4). Slice's git diff alone is insufficient evidence for out-of-repo edits — N=5 stable methodology now N=6 on slice-010 completion.
- **"Validate using your own ship" pattern (N=7 stable across slice-003..009)** — slice-010 self-applies the BC-1 v1.2 negative-anchor mechanism (closes the noise loop on its own ship; empirically verified pre-design). N=8 on completion.
- **Empirical-verification-at-design-time discipline (N=8 stable across slice-003..009)** — slice-010 runs the canonical-literal-absence audit + location-pin anchor-uniqueness audit against THIS slice's target file BEFORE locking ACs (see "Empirical verification" section). N=9 on completion.
- **Recursive-self-application observation (slice-009 M2; N=1)** — slice-010 IS a recursive-self-application instance: the slice authoring the heuristic that promotes voluntary-Critic-on-cross-cutting-tooling to mandatory ALSO modifies the very in-house methodology surface (`skills/slice/SKILL.md`) the heuristic targets. The Critic at /critique SHOULD be expected to find rule-class violations in slice-010's own draft. N=2 candidate post-completion; promote `recursive-self-application-discipline` to actionable /critique-skill-prose at N=3 if a third instance surfaces.

## Components touched

### `skills/slice/SKILL.md` (modified — in-repo canonical)

- **Responsibility**: User-invokable skill that defines the next slice via mission brief. Step 4a "Pick the risk tier" enumerates the mandatory-Critic trigger list (regardless of tier).
- **Lives at**: `skills/slice/SKILL.md` Step 4a section. Line numbers as-of-2026-05-12: section spans L155-174 (the "Always mandatory Critic" list is L165-172; the "When producing the mission brief..." paragraph is L173-174). All slice-010 references are symbolic post-2026-05-12 (per Critic m1): the new bullet goes between the `Security-sensitive paths` bullet and the `Heavy mode (always)` bullet; the evidence paragraph goes between the existing `When producing the mission brief...` paragraph and the start of `### Step 5:`.
- **Key interactions**: read by Claude main thread at /slice invocation; pinned (after slice-010) by `tests/methodology/test_slice_skill.py` (5 prose-pin tests including the ACCEPTED-PENDING sub-class anchor row); installed at `~/.claude/skills/slice/SKILL.md` via INST-1 (file enumerated in `tools/install_audit.py:_CANONICAL_SKILLS`); byte-equality verified by mini-CAD-1 test `tests/methodology/test_slice_skill_drift.py::test_in_repo_and_installed_slice_skill_md_are_content_equal`.
- **What changes** (per Critic M1 split — two additive insertions, not a single multi-clause bullet):
  - **Bullet list grows 7 → 8 bullets**: terse bullet inserted between the `Security-sensitive paths` bullet and the `Heavy mode (always)` bullet:
    ```
    - In-house methodology surfaces (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`)
    ```
    Bullet stays stylistically uniform with the existing 7 bullets (single-line, single-clause, no embedded justification prose — matches "External integrations (OAuth, payment gateways, third-party APIs)" shape).
  - **Evidence prose paragraph appended** after the existing "When producing the mission brief..." paragraph (which itself follows the bullet list — L173-174 as-of-2026-05-12). Markdown blockquote `>` keeps the new prose visually distinct:
    ```
    > **Evidence for the In-house methodology surfaces trigger**: voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 in this project's reflection record (e.g., slice-006 INST-1 inventory drift; slice-007 install-time rename; slice-008 negative-anchor uniformity; slice-009 recursive self-application). Every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; see `architecture/slices/_index.md` "Aggregated lessons" and `archive/slice-NNN/reflection.md` "Critic calibration" sections for per-slice disposition records.
    ```
  - Canonical-literal scaffolding (per AC #1 + AC #2 + ACCEPTED-PENDING M3 row):
    - `In-house methodology surfaces` — bullet text, capitalized-I bullet-title form (DEVIATION-1 mitigation: bullet start gets natural capitalization without forcing case).
    - `skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md` — file-class anchors in bullet body (AC #1 row 1 asserts at least one present; design selects all 4 for canonical-inventory completeness).
    - `N=9/9` — empirical evidence anchor in evidence paragraph (AC #1 row 3).
    - `voluntary Critic` — pattern-name canonical literal in evidence paragraph, lowercase-v (DEVIATION-1 mitigation: phrase placed mid-sentence post-`N=9/9 voluntary Critic catch`, not at sentence start — preserves literal case).
    - `slice-006`, `slice-007`, `slice-008`, `slice-009` — 4 cross-slice example anchors in evidence paragraph (AC #2 asserts ≥2; design includes all 4 for completeness).
    - `INST-1 inventory drift`, `install-time rename`, `negative-anchor uniformity`, `recursive self-application` — 4 sub-class anchors in evidence paragraph. Per Critic M3 ACCEPTED-PENDING: at /build-slice add `test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors` asserting ≥2 of these 4 (TF-1 plan grows 7 → 8 rows). Pinning the sub-class anchors closes the drift vector slice-009 N-substring discipline would otherwise warn against.
  - **No changes to**: Step 4 intro text, Step 4a intro paragraph, the 7 existing bullets (Auth / API contracts / Data model / Multi-device sync / External integrations / Security-sensitive paths / Heavy mode (always) — preserved bit-for-bit), Step 4a "When producing the mission brief..." paragraph (preserved bit-for-bit; evidence paragraph appended BELOW it as additive), Step 5 (Scope check), Step 6 (Write the mission brief + create milestone.md), Initial milestone.md template, Mission brief template, Critical rules, Anti-patterns for slice 1, Good slice 1 examples, Next step.

### `~/.claude/skills/slice/SKILL.md` (modified — out-of-repo Phase 2 forward-sync target)

- **Responsibility**: installed runtime copy of `skills/slice/SKILL.md`. Read by Claude Code at `/slice` invocation from any project. Enumerated in `tools/install_audit.py:_CANONICAL_SKILLS` (INST-1 positive-inclusion canonical inventory).
- **Lives at**: `~/.claude/skills/slice/SKILL.md` (installed via INST-1).
- **Key interactions**: byte-equality with in-repo verified by mini-CAD-1 test `tests/methodology/test_slice_skill_drift.py::test_in_repo_and_installed_slice_skill_md_are_content_equal`; sha256 forensic capture in build-log Phase 0 + Phase 4 per N=5 stable bidirectional pattern.
- **What changes**: same bullet insertion as in-repo `skills/slice/SKILL.md`. Phase 2 forward-sync (`Copy-Item` from in-repo) after in-repo edits are validated via mid-slice smoke gate.

### `methodology-changelog.md` (in-repo + `~/.claude/`) — append-only entry

- **Responsibility**: methodology rule changelog; pinned by PMI-1 + bidirectional changelog-entry-pin tests. INST-1 negative-exclusion: installed via Step 3f explicit copy (not via `_CANONICAL_*` tuples) — per slice-009 CCC-1 v1.1 framing.
- **What changes**: new H2 entry `## v0.25.0 — 2026-05-12` under `### Added` (new mechanism MCR-1 vs `### Changed` for refinements like CCC-1 v1.1) — title: "MCR-1 — `/slice` Step 4a 'Always mandatory Critic' bullet for in-house methodology surfaces". Body includes:
  - One-paragraph summary (mirrors v0.21.0 / v0.22.0 / v0.23.0 / v0.24.0 prose patterns).
  - The substantive canonical phrase `In-house methodology surfaces` (AC #4 bidirectional pin per Critic M3 N-surface discipline).
  - Empirical-evidence-base citation pinning slice-006 / slice-007 / slice-008 / slice-009 sub-class anchors.
  - Rule reference: **MCR-1**.
  - Defect class: cross-cutting tooling slices routinely surface Dim 9 sub-class hits that user-facing trigger bullets don't enumerate.
  - Validation: names the 4 prose-pin tests + 1 mini-CAD-1 byte-equality test + 1 bidirectional changelog-pin test + 1 PMI-1 `_at_0_25_0` gate.

### `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed)

- **Responsibility**: PMI-1 atomic version-bump invariant. INST-1 install-time rename: in-repo `VERSION` → installed `ai-sdlc-VERSION` (per slice-007 Critic B1 lesson + slice-009 CCC-1 v1.1 install-time-rename canonical-inventory surface). Both files MUST be bumped atomically with `plugin.yaml.version`.
- **What changes**: 0.24.0 → 0.25.0 (both files; same content per install-time rename).

### `plugin.yaml` (in-repo only; INST-1 negative-exclusion — on Step 3f do-not-copy list)

- **Responsibility**: plugin manifest. PMI-1 audit (`tools/plugin_manifest_audit.py`) enforces `version:` field matches `VERSION` file content.
- **What changes**: `version: 0.24.0` → `version: 0.25.0`. Single field edit at file line 15.

### `tests/methodology/test_methodology_changelog.py` (modified)

- **Responsibility**: bidirectional changelog-entry pins (per slice-007/008/009 precedent) + PMI-1 versioned-gate test (per slice-007 introduction; slice-008/009/010 supersession pattern).
- **What changes**:
  - ADD `test_v_0_25_0_mcr_1_entry_present_in_repo_and_installed` — asserts both `## v0.25.0 —` + `MCR-1` + canonical phrase `In-house methodology surfaces` present in BOTH in-repo `methodology-changelog.md` AND `~/.claude/methodology-changelog.md`.
  - REPLACE `test_plugin_yaml_version_matches_version_file_at_0_24_0` with `test_plugin_yaml_version_matches_version_file_at_0_25_0` (PMI-1 versioned-gate supersession — no two version-gates coexist).

### `tests/methodology/test_slice_skill.py` (NEW file)

- **Responsibility**: prose-pin tests for `skills/slice/SKILL.md` Step 4a `In-house methodology surfaces` bullet (AC #1 + AC #2).
- **What's in it**: 4 test functions (enumerated under "What's new" above). Reads in-repo `skills/slice/SKILL.md` from project root; scoped section search within "Always mandatory Critic" bounds.

### `tests/methodology/test_slice_skill_drift.py` (NEW file)

- **Responsibility**: mini-CAD-1 byte-equality test between in-repo `skills/slice/SKILL.md` and installed `~/.claude/skills/slice/SKILL.md` (AC #3). Mirrors slice-007's `test_critique_agent_drift.py` shape but scope-narrow to /slice SKILL.md; does NOT generalize INST-2.
- **What's in it**: 1 test function — computes sha256 of both files; asserts equality with detailed mismatch message including both sha256 values.

### `architecture/shippability.md` (modified)

- **Responsibility**: shippability catalog rows enumerating each slice's critical-path tests for cross-slice regression-guard at /validate-slice.
- **What changes**:
  - ADD row 10 naming slice-010's critical path tests (the 4 prose-pin + 1 mini-CAD-1 + 1 bidirectional changelog pin + 1 PMI-1 `_at_0_25_0` gate).
  - UPDATE row 9 (slice-009) header to note slice-010 supersedes the `_at_0_24_0` PMI-1 versioned-gate with `_at_0_25_0`.

## Contracts added or changed

N/A — slice modifies methodology-prose files (`skills/slice/SKILL.md`, `methodology-changelog.md`) + test pins + version files + plugin.yaml manifest field. No new HTTP endpoints, no new events, no new external integrations, no contract shapes.

## Data model deltas

N/A — slice doesn't add or modify any data model. No DB schema changes, no Pydantic models, no in-memory state.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces no new runtime modules — all source-code changes are extensions of existing files (`skills/slice/SKILL.md`, `methodology-changelog.md`, `tests/methodology/test_methodology_changelog.py`, `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml`, `architecture/shippability.md`) + two new pytest test modules (`tests/methodology/test_slice_skill.py`, `tests/methodology/test_slice_skill_drift.py` — auto-discovered by pytest; not runtime modules consumed by other code) + a new ADR file (`architecture/decisions/ADR-009-*.md` — vault document, not a runtime module). Empty-matrix posture (header + separator only — accepted by audit per slice-005 / slice-008 / slice-009 fixture pattern).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-009-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] at `architecture/decisions/ADR-009-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic.md` — adopt **Option 1 (refined per Critic M1)** from the 3-options analysis: append a terse new bullet + adjacent evidence prose paragraph to the existing `skills/slice/SKILL.md` Step 4a "Always mandatory Critic" section. Bullet inserted between the last content-trigger bullet (`Security-sensitive paths`) and the mode-meta closer (`Heavy mode (always)`); evidence prose appended below the existing "When producing the mission brief..." paragraph. Preserves the existing 7 bullets bit-for-bit + the existing "When producing..." paragraph bit-for-bit; doesn't restructure the section into sub-lists. Codifies as new methodology rule **MCT-1** (Mandatory Critic Trigger; -T- distinguishes /slice-time trigger semantics from audit-enforced gate semantics of siblings BC-1/PMI-1/CAD-1/TF-1 per Critic B5). Reversibility: **cheap** with magnitude justification per Critic m3 corrected count (~11-13 sites; same magnitude class as ADR-007 ~10-15 sites; larger than ADR-008 ~5 sites). Minor irreversible portion: append-only methodology-changelog entry + cumulative slice-010-N Critic invocations gated by MCT-1 going forward.

## Authorization model for this slice

N/A — slice modifies a methodology-prose file (`/slice` SKILL.md) + test pins + changelog entries + version files. No auth/authz surface. The `/slice` skill runs locally on the developer's machine via Claude Code main-thread invocation; no network calls; no user-data flow; no authentication. The new MCR-1 heuristic GATES Critic invocation (sets `critic-required: true` more often), but doesn't itself perform authorization.

## Error model for this slice

N/A — slice introduces no new runtime error cases. The mini-CAD-1 byte-equality test raises `AssertionError` on sha256 mismatch (test infrastructure failure mode — same shape as slice-007 CAD-1's `test_in_repo_and_installed_critique_agent_are_content_equal`). The 4 prose-pin tests raise `AssertionError` on canonical-literal absence (test infrastructure failure mode — same shape as slice-009's `test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables`). All new failure modes are pytest-test failures, NOT production runtime errors.

## Empirical verification at design time

Per slice-009 N=8 stable empirical-verification-at-design-time discipline. Slice-010 ratchets pattern to N=9 stable. Two pre-AC-lock audits executed:

### Audit 1: Canonical-literal absence (genuineness of TF-1 PENDING → WRITTEN-FAILING)

Pre-design grep on `skills/slice/SKILL.md` for the proposed canonical literals confirmed ZERO pre-existing matches:
- `In-house methodology surfaces` — 0 matches
- `in-house methodology surfaces` — 0 matches
- `N=9/9` — 0 matches
- `voluntary Critic` (case-sensitive) — 0 matches
- `cross-cutting tooling` — 0 matches

Implication: PENDING → WRITTEN-FAILING transitions for AC #1 + AC #2 will be authentic (no coincidental pre-existing matches). TF-1 audit at /build-slice Step 6 (strict-pre-finish) will receive genuine failure signals.

### Audit 2: Location-pin anchor uniqueness (DEVIATION-2 `.find()`-collision pre-emption)

Pre-design grep on `skills/slice/SKILL.md` for the proposed location-pin anchors confirmed each appears exactly ONCE in the file:
- `Always mandatory Critic` — 1 match at line 165 (start-of-section anchor)
- `Security-sensitive paths` — 1 match at line 171 (preceding-bullet anchor; useful as a sub-section position pin)
- `Heavy mode (always)` — 1 match at line 172 (end-of-section anchor)

Implication: the location-pin test (AC #1 row 2) uses scoped `text.find("Heavy mode (always)", text.find("Always mandatory Critic"))` — both anchors are unique, so first-occurrence-wins resolution returns the intended position; no slice-009 DEVIATION-2 `.find()`-collision risk.

### Audit 3: BC-1 self-application clean (validate using your own ship — N=7 stable, slice-003..009)

Per Critic B4: the audit's expected `applicable: []` result comes from TWO distinct mechanisms acting on different rules — NOT uniform negative-anchor silencing. Empirical word-boundary counts at design time (`\bsubagent\b`, `\bfan-out\b`, `\bfence\b`, `\bcode-block\b`, `\bllm\b` via the venv Python interpreter):

- **BC-PROJ-1** (positive trigger anchors: `subagent`, `fan-out`) — empirical count in slice-010 mission-brief.md = 0; in design.md = 0. Rule does NOT positively-fire; negative-anchor filter is never reached on this rule's keyword path. NOT a silencing event.
- **BC-PROJ-2** (positive trigger anchors: `fence`, `code-block`, `llm`) — empirical count in slice-010 mission-brief.md = 0; in design.md = 0. Same as BC-PROJ-1: rule does NOT positively-fire; negative-anchor filter not reached.
- **BC-GLOBAL-1** (`Applies to: **` always-fires under `--changed-files`) — DOES positively-fire on slice-010's mission-brief + design. BC-1 v1.2's negative-anchor mechanism (slice-008) genuinely silences it: slice-010's prose contains `aggregated lessons` (2 mission + 2 design), `forward-sync` (9 each), `back-sync` (1 + 2), `Dim 9` (3 each), `vocabulary` (2 each), `meta-discussion` (1 design), `defer-with-rationale` (1 mission) — at least one negative anchor per file, so the negative-anchor filter silences. This IS a genuine silencing event (closes the noise loop on the slice's own ship per slice-008 + slice-009 N=7 stable pattern).

Expected `applicable: []` result = no-positive-firing (BC-PROJ-1 + BC-PROJ-2) + negative-anchor-silencing (BC-GLOBAL-1). Empirical verification deferred to /build-slice Phase 0 (run `tools/build_checks_audit.py` against the slice's own mission-brief.md + design.md and confirm `applicable: []` per BC-1 v1.2 semantics); design-time prediction is that BC-1 v1.2's negative-anchor set is sufficient FOR BC-GLOBAL-1 specifically.

## Phase plan (build-slice will follow this order)

Per slice-007/008/009 N=3 stable Phase 0..4 pattern:

- **Phase 0**: Pre-edit sha256 forensic capture for in-repo + installed copies of `skills/slice/SKILL.md`, `methodology-changelog.md`, `VERSION`/`ai-sdlc-VERSION`, `plugin.yaml`. Confirm in-repo↔installed byte-equality at start (slice-009 ended with both pairs byte-equal — confirm pre-slice-010 state). Record in `build-log.md` Phase 0 table.
- **Phase 1**: TF-1 PENDING → WRITTEN-FAILING transitions for 6 of 7 TF-1 rows; row 3 (mini-CAD-1) starts PASSING per slice-009 mission-brief row 3 precedent (file pair byte-equal at slice start per Phase 0 capture). Pin specific failure signals (canonical literal absent, scoped `.find()` returns -1, sha256 mismatch arrives only AFTER Phase 2 in-repo edit, version mismatch).
  - Phase 1a: write the 4 prose-pin tests in `test_slice_skill.py` (FAIL pre-edit — canonical literals absent per Audit 1).
  - Phase 1b: write the 1 mini-CAD-1 test in `test_slice_skill_drift.py` (PASSING pre-edit — both files byte-equal at slice start per Phase 0 capture; transitions to WRITTEN-FAILING only at Phase 2 when in-repo is edited and installed not yet synced — observed at Phase 2b mid-slice smoke gate).
  - Phase 1c: write the 1 bidirectional changelog-pin test for v0.25.0 / MCT-1 (FAIL pre-edit — entry doesn't exist).
  - Phase 1d: REPLACE the `_at_0_24_0` PMI-1 versioned-gate with `_at_0_25_0` (FAIL pre-edit — VERSION still 0.24.0).
- **Phase 2**: In-repo edits. Edit `skills/slice/SKILL.md` Step 4a (insert new bullet between L171 and L172). Append v0.25.0 entry to in-repo `methodology-changelog.md`. Bump in-repo `VERSION` 0.24.0 → 0.25.0 + `plugin.yaml.version` 0.24.0 → 0.25.0.
- **Phase 2b — mid-slice smoke gate**: run `pytest tests/methodology/test_slice_skill.py tests/methodology/test_slice_skill_drift.py tests/methodology/test_methodology_changelog.py -q`. Expected: 4 prose-pin tests PASS (in-repo edited); 1 mini-CAD-1 test FAIL with sha256 mismatch (installed not yet forward-synced); 1 v0.25.0 bidirectional pin FAIL (installed changelog not synced); 1 PMI-1 `_at_0_25_0` PASS (in-repo VERSION = 0.25.0; plugin.yaml.version = 0.25.0). If 4 prose-pin tests FAIL: STOP, diagnose per mid-slice smoke gate guidance.
- **Phase 2c — Phase 2 forward-sync**: `Copy-Item` from in-repo to installed for `skills/slice/SKILL.md`, `methodology-changelog.md`, `VERSION` → `ai-sdlc-VERSION` (per INST-1 install-time-rename surface — explicit rename at copy time, NOT a separate file).
- **Phase 3**: Re-run mid-slice smoke gate post-forward-sync. Expected: all 7 TF-1 rows PASS. PMI-1 audit (`python -m tools.plugin_manifest_audit --root .`) clean (exit 0). CAD-1 audit (slice-007 — `python -m tools.critique_agent_drift_audit`) clean (exit 0 — unchanged by slice-010; agents/critique.md not modified). Methodology suite clean (`pytest tests/methodology/ -q` exit 0; no broader regression).
- **Phase 4**: Post-forward-sync sha256 forensic capture for all 4 file pairs. Record in `build-log.md` Phase 4 table. Confirm byte-equality post-edits. Self-application BC-1 audit (run against slice-010's own mission-brief.md + design.md) — expected `applicable: []` per Audit 3 prediction.
- **Phase 5**: Add shippability.md row 10 + update row 9 header (slice-009 PMI-1 versioned-gate superseded notation).
- **Phase 6** (pre-finish gate): TF-1 strict-pre-finish audit clean; drift-check clean; methodology suite clean; mini-CAD-1 + CAD-1 + PMI-1 audits clean.
