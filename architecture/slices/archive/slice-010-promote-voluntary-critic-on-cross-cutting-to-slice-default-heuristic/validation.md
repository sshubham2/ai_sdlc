# Validation: Slice 010 promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic

**Date**: 2026-05-12
**Result**: PASS (5 of 5 ACs PASS; 0 shippability regressions; 1 build-time DEVIATION-3 from /build-slice carried over with defer-with-rationale; VAL-1 Layer A 0 secrets, Layer B 3 known false-positives dispositioned)

## Per-criterion results

### AC #1: `skills/slice/SKILL.md` Step 4a contains terse `In-house methodology surfaces` bullet + adjacent evidence prose paragraph with 4 canonical literals; bullet position-pinned between `Security-sensitive paths` and `Heavy mode (always)`

- **Status**: PASS
- **Evidence (3 pytest functions; all PASS in 0.03s)**:
  ```
  pytest tests/methodology/test_slice_skill.py::test_slice_step4a_mandatory_critic_section_contains_in_house_methodology_surfaces_bullet \
         tests/methodology/test_slice_skill.py::test_slice_step4a_in_house_methodology_bullet_location_between_security_paths_and_heavy_mode \
         tests/methodology/test_slice_skill.py::test_slice_step4a_evidence_paragraph_cites_n_9_and_voluntary_critic -v
  → 3 passed in 0.03s
  ```
- **Evidence (manual visual confirmation on installed `~/.claude/skills/slice/SKILL.md` Step 4a section)**:
  ```
  **Always mandatory Critic** (regardless of tier — this field is "critic-required: true" in milestone.md):
  - Auth / authz / permissions / login / tokens
  - New API contracts or endpoint shapes
  - Data model changes / migrations / schema
  - Multi-device / multi-user / sync / sharing
  - External integrations (OAuth, payment gateways, third-party APIs)
  - Security-sensitive paths
  - In-house methodology surfaces (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`)
  - Heavy mode (always)

  When producing the mission brief and milestone.md: scan the slice's scope for these triggers. If any match, set `critic-required: true` even if tier is `low`. Tell the user explicitly: "Tier is low, but slice touches auth — Critic will run anyway."

  > **Evidence for the In-house methodology surfaces trigger**: voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 in this project's reflection record (e.g., slice-006 INST-1 inventory drift; slice-007 install-time rename; slice-008 negative-anchor uniformity; slice-009 recursive self-application). Every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; ...
  ```
- **Notes**: Bullet stays stylistically uniform with the existing 7 bullets (single-line, single-clause matching `External integrations (OAuth, payment gateways, third-party APIs)` shape) per slice-010 Critic M1 split. Evidence prose carries longer justification clause as markdown blockquote. Location-pin uses scoped `text.find()` chained off `Security-sensitive paths` start anchor and `Heavy mode (always)` end anchor — both empirically verified unique pre-AC-lock + post-edit. DEVIATION-1 case-sensitivity trap pre-empted (`In-house methodology surfaces` capitalized-I bullet-title form; `voluntary Critic` placed mid-sentence post-`N=9/9 voluntary Critic catch` per literal lowercase-v case).

### AC #2: Evidence prose paragraph cites ≥2 of 4 cross-slice anchors AND ≥2 of 4 sub-class anchors (M3 ACCEPTED-PENDING added at /build-slice Phase 1a)

- **Status**: PASS
- **Evidence (2 pytest functions; all PASS in 0.03s)**:
  ```
  pytest tests/methodology/test_slice_skill.py::test_slice_step4a_evidence_paragraph_cites_at_least_two_cross_cutting_tooling_slices \
         tests/methodology/test_slice_skill.py::test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors -v
  → 2 passed in 0.03s
  ```
- **Evidence (substring count)**: all 4 cross-slice anchors present (`slice-006`, `slice-007`, `slice-008`, `slice-009`) AND all 4 sub-class anchors present (`INST-1 inventory drift`, `install-time rename`, `negative-anchor uniformity`, `recursive self-application`) — exceeds the ≥2 floor for both rows.
- **Notes**: M3 sub-class anchor pin was Critic-flagged at /critique as ACCEPTED-PENDING (descriptive-only anchors create drift vector per slice-009 N-substring discipline); added at /build-slice Phase 1a as 5th prose-pin test; closes the drift vector.

### AC #3: `~/.claude/skills/slice/SKILL.md` byte-equal to in-repo `skills/slice/SKILL.md` post-forward-sync

- **Status**: PASS
- **Evidence (pytest)**:
  ```
  pytest tests/methodology/test_slice_skill_drift.py::test_in_repo_and_installed_slice_skill_md_are_content_equal -v
  → 1 passed in 0.03s
  ```
- **Evidence (sha256 forensic confirmation post-forward-sync)**:
  ```
  ac6fc1e82464d1d6151c8f2d3c378268bc8c686ff7629957939b371ec3d0520f *skills/slice/SKILL.md
  ac6fc1e82464d1d6151c8f2d3c378268bc8c686ff7629957939b371ec3d0520f */c/Users/sshub/.claude/skills/slice/SKILL.md
  ```
- **Notes**: Per slice-009 row 3 + Critic B2 honest framing: test started at TF-1 status PASSING (both files byte-equal at slice start per Phase 0 capture); transitioned PASSING → WRITTEN-FAILING at Phase 2 (in-repo edited, installed not yet synced — observed at Phase 2b mid-slice smoke gate as `RuntimeError: sha256 mismatch`) → PASSING at Phase 2c post-forward-sync. Mini-CAD-1 pattern scope-narrow to /slice SKILL.md; does NOT generalize INST-2 (still deferred at N=1 actual-drift evidence per slice-009 reflection).

### AC #4: `methodology-changelog.md` (both in-repo and installed) contains v0.25.0/MCT-1 entry with substantive canonical phrase `In-house methodology surfaces` pinned bidirectionally; Limitations note per Critic B5

- **Status**: PASS
- **Evidence (pytest)**:
  ```
  pytest tests/methodology/test_methodology_changelog.py::test_v_0_25_0_mct_1_entry_present_in_repo_and_installed -v
  → 1 passed in 0.04s
  ```
- **Evidence (sha256 forensic on methodology-changelog.md)**:
  ```
  1dcfcb97edc7c8fa055d45c1a4a8b75613919d5d52f8a10af61588d1fbe56979 *methodology-changelog.md
  1dcfcb97edc7c8fa055d45c1a4a8b75613919d5d52f8a10af61588d1fbe56979 */c/Users/sshub/.claude/methodology-changelog.md
  ```
- **Evidence (manual visual head-of-entry from installed)**:
  ```
  ## v0.25.0 — 2026-05-12

  Adds **MCT-1** — Mandatory Critic Trigger for **In-house methodology surfaces**. Promotes voluntary-Critic-on-cross-cutting-tooling-slices to the `/slice` Step 4a default mandatory-Critic trigger list, codifying the strongest aggregated-lesson promotion candidate in the project's reflection record (voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 — every voluntary Critic invocation produced VALIDATED findings post-build with zero FALSE-ALARMs; cumulative-post-build framing per slice-N reflection records). ...
  ```
- **Notes**: N-surface schema-pin discipline applied across 3 surfaces: `skills/slice/SKILL.md` bullet + in-repo `methodology-changelog.md` + installed `methodology-changelog.md` — ONE canonical phrase `In-house methodology surfaces` pinned across all 3. Limitations note explicitly acknowledges MCT-1 is /slice-time prose-heuristic only, NOT audit-enforced gate (per Critic B5).

### AC #5: PMI-1 atomic at 0.25.0; `_at_0_25_0` test PASSING; `_at_0_24_0` superseded

- **Status**: PASS
- **Evidence (pytest)**:
  ```
  pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_at_0_25_0 -v
  → 1 passed in 0.04s
  ```
- **Evidence (PMI-1 audit)**:
  ```
  python -m tools.plugin_manifest_audit --root .
  → PMI-1 plugin manifest audit: clean. 24 skill(s), 5 agent(s), 15 tool(s); version 0.25.0.
  ```
- **Evidence (manual 3-file atomicity)**:
  ```
  in-repo VERSION:            0.25.0
  installed ai-sdlc-VERSION:  0.25.0
  plugin.yaml.version:        version: 0.25.0
  ```
- **Evidence (PMI-1 versioned-gate supersession N=3 confirmed)**:
  ```
  grep -c "test_plugin_yaml_version_matches_version_file_at_" tests/methodology/test_methodology_changelog.py
  → 1
  ```
  Exactly one versioned-gate test exists (`_at_0_25_0`); no `_at_0_24_0` coexists (slice-010 ratchets the supersession pattern to N=3 events post-completion per slice-009 Critic M5 framing).
- **Notes**: PMI-1 atomic version bump 0.24.0 → 0.25.0 across all 3 files. Install-time rename surface (in-repo `VERSION` → installed `ai-sdlc-VERSION`) preserved per INST-1.

## VAL-1 layered safety checks

### Layer A — Credential scan (Critical, blocks)

- **Status**: CLEAN — 0 secrets found across all slice-010 changed files.
- **Evidence**:
  ```
  python -m tools.validate_slice_layers --slice <slice-010 path> --changed-files <list of 9 files>
  → VAL-1 layered safety checks: 0 secret(s), 3 import finding(s), 0 suppressed (allowlisted).
  ```

### Layer B — Dependency hallucination check (Important)

- **Status**: 3 Important findings, ALL dispositioned **defer-with-rationale** (known false-positive class)
- **Findings**:
  ```
  [Important] tests/methodology/test_slice_skill.py:2 (hallucinated-import) `tests`
  [Important] tests/methodology/test_slice_skill_drift.py:27 (hallucinated-import) `tests`
  [Important] tests/methodology/test_methodology_changelog.py:7 (hallucinated-import) `tests`
  ```
- **Rationale (defer-with-rationale)**: All 3 findings reference `from tests.methodology.conftest import ...` — the `tests` "package" is the project's own intra-repo test directory, NOT an external pip package. Verified:
  ```
  <HOME>/ai_sdlc/tests/methodology/__init__.py → exists (intra-repo namespace package)
  pyproject.toml [tool.setuptools].packages = ["tools"] → only `tools` declared (correct — `tests` is intentionally not a published package)
  ```
  The import resolves at pytest collection time via the project's `pytest.ini rootdir` + `tests/methodology/` having `__init__.py`. Same false-positive class slices 003-009 must have hit (every methodology test adds a `from tests.methodology.conftest import read_file` line). Per VAL-1 Important semantics: "surface to user; defer-with-rationale allowed in validation.md". Followup: not a slice candidate — VAL-1 Layer B's intra-repo-package handling could be enhanced in a v2 to recognize `[tool.pytest.ini_options]` testpaths and auto-allow them; out-of-scope for slice-010.

## Multi-instance validation

- **Required?**: No
- **Result**: N/A
- **Evidence**: slice-010 modifies methodology-prose files (SKILL.md, methodology-changelog.md) + version files + plugin.yaml manifest + 3 test files + 1 ADR. No multi-user / multi-device / sync / external integration surface. Single-instance prose-edit slice; verification via pytest replay + audit replay against actual edited files + sha256 forensic capture covers the full surface.

## Reality surprises

### Build-time DEVIATION-3 (recursive-self-application N=3 candidate) — discovered at /build-slice Phase 4 BC-1 self-application

- **What surfaced**: BC-PROJ-2 fired against slice-010's own mission-brief.md L81 + design.md L193 at Phase 4 BC-1 self-application audit. Audit 3 design-time prediction said BC-PROJ-2 would NOT fire (empirical word-boundary count = 0 at design time).
- **Root cause**: At /critique B4 fix I added empirical prose **describing** BC-PROJ-2's anchors (the substrings `fence`, `code-block`, `llm`) to mission-brief L81 + design.md L193 to explain why BC-PROJ-2 wouldn't fire. The description itself contains those substrings → BC-PROJ-2's anchor path positively fires on slice-010's own prose. This is the **classic recursive-self-application phenomenon at build-time** — slice-009 M2 was at /critique design-time prose; slice-010 brings the same phenomenon to /build-slice build-time audits. Distinct sub-class candidate at N=2 across phases (slice-009 design-time + slice-010 build-time).
- **Disposition (carried from /build-slice)**: defer-with-rationale per BC-1 Important semantics (non-blocking; rule's true scope is `Applies to: skills/**/*.py, tools/**/*.py` — LLM-output parsing in code — which slice-010 changes zero of). Same false-positive class slice-005..008 had with BC-PROJ-1 + BC-GLOBAL-1 before BC-1 v1.2 closed it via negative-anchor mechanism. BC-PROJ-2 hasn't been migrated yet; **slice-010 = N=2 evidence** (slice-005 + slice-010 methodology-vocabulary slices) at BC-PROJ-2 negative-anchor migration promotion threshold.
- **Impact on next slice**: `bc-proj-2-negative-anchor-migration` is now a slice-011+ candidate at N=2 evidence meeting BC-1 v1.2 promotion threshold per slice-008 reflection convention. Adds 9-token methodology-vocabulary negative-anchor set to BC-PROJ-2 mirroring slice-008 BC-PROJ-1 + BC-GLOBAL-1 v1.2 migration.
- **Reflection note (recursive self-application strongest evidence to date)**: recursive-self-application phenomenon ratchets N=1 (slice-009 M2 design-time) → N=2 (slice-010 /critique design-time stress-test catches 3 violations: B1 N=9/9 inconsistency + M1 bullet-style asymmetry + B5 rule-naming convention break) → N=3 (slice-010 build-time DEVIATION-3 BC-PROJ-2 anchor-prose self-trigger). **At N=3 the candidate `recursive-self-application-discipline` meets promotion threshold per slice-009 reflection language**: "Promote to /critique skill prose at N=3 if a third instance surfaces at slice-011+". Slice-011+ candidate: codify recursive-self-application expectation into the Critic agent prompt (when a slice authors a methodology refinement, stress-test the draft against the very discipline the slice is encoding; expect the discipline to self-apply to the rule's own prose).

### Validate-using-your-own-ship — MCT-1 self-application (N=7 → N=8 stable)

- **What checked**: Under the NEW MCT-1 heuristic that slice-010 encodes, would slice-010 itself have qualified for `critic-required: true`?
- **Result**: YES — slice-010 modifies `skills/slice/SKILL.md` (matches MCT-1 trigger glob `skills/*/SKILL.md`); `milestone.md` frontmatter `critic-required: true` ✓; rule self-applies correctly. N=7 → N=8 stable validate-using-your-own-ship pattern across slices 003-010.
- **Notes**: Slice-009 ended with N=7 stable; slice-010 brings to N=8. The MCT-1 trigger glob list (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`) is self-consistent — every slice that adds an MCT-1 trigger entry would itself qualify.

## Shippability catalog regression check (rows 1-10)

**Result**: PASS — 80 tests / 80 PASS in 2.67s (target <2 min; well under).

**Evidence**:
```
pytest <full row 1-10 critical-path test list> --no-header -q
→ 80 passed in 2.67s
```

**Per-row status**:
- Row 1 (slice-001 diagnose orchestration): PASS
- Row 2 (slice-002 RR-1 schema + diagnose contract): PASS
- Row 3 (slice-003 VAL-1 Layer B): PASS
- Row 4 (slice-004 RR-1 docstring/regex): PASS
- Row 5 (slice-005 BC-1 keyword precision): PASS
- Row 6 (slice-006 Critic 9-dim CCC-1): PASS
- Row 7 (slice-007 CAD-1 hybrid): PASS
- Row 8 (slice-008 BC-1 v1.2 negative-anchors): PASS
- Row 9 (slice-009 CCC-1 v1.1 design-doc-level): PASS
- Row 10 (slice-010 MCT-1; this slice): PASS (8 tests in <0.1s)

Zero regressions introduced by slice-010 to past slices' critical paths. Methodology suite full run (357 tests) earlier at /build-slice Phase 3b also clean.

## Next action

All 5 ACs PASS + 0 shippability regressions + VAL-1 Layer A clean + VAL-1 Layer B Important findings dispositioned defer-with-rationale (known false-positive class). 1 reality surprise (DEVIATION-3 recursive-self-application N=3 candidate) recorded for /reflect Step 5 capture.

**Run `/reflect`** — capture what reality taught at slice-010:
- Recursive-self-application phenomenon ratcheted to N=3 evidence; promotion candidate for /critique skill prose
- BC-PROJ-2 negative-anchor migration promotion threshold met at N=2 evidence; slice-011+ candidate
- "Validate using your own ship" pattern N=8 stable
- MCT-1 added to methodology; effective from slice-011+ onward (prospective application)
- Empirical-verification-at-design-time discipline N=9 stable (slice-003..010); pre-AC-lock grep + anchor-uniqueness verification continues to pre-empt DEVIATION-1/DEVIATION-2 class (zero recurrence at slice-010 of slice-009's two DEVIATIONs)
- Bidirectional sha256 forensic capture N=6 stable
- PMI-1 versioned-gate supersession pattern N=3 supersession events stable post-slice-010
