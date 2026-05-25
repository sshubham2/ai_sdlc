# Validation: Slice 019 harden-diagnose-layering-evidence

**Date**: 2026-05-13
**Result**: PASS

## Per-criterion results

### AC1: /diagnose 03f-layering pass template (sole emitter of `category: layering-violation`) carries the textual-evidence prose at N=3 in-repo surfaces + N=3 installed surfaces with bidirectional sha256 byte-equality

- **Status**: PASS
- **Evidence**:
  - **pytest** (5 tests covering all 3 in-repo surfaces + bidirectional mini-CAD):
    ```
    tests/skills/diagnose/test_skill_md_pins.py::test_skill_md_step5_documents_textual_evidence_rule PASSED
    tests/skills/diagnose/test_skill_md_pins.py::test_layering_pass_template_emits_textual_evidence_rule PASSED
    tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces PASSED
    tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_skill_md_are_content_equal PASSED
    tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_03f_layering_md_are_content_equal PASSED
    ============================== 5 passed in 0.03s ==============================
    ```
  - **Canonical-phrase grep count across N=6 surfaces** (`textual import-evidence requirement`):
    - in-repo `skills/diagnose/passes/03f-layering.md`: 1 occurrence
    - in-repo `skills/diagnose/SKILL.md`: 1 occurrence
    - in-repo `methodology-changelog.md`: 3 occurrences (v0.33.0 entry header + Added body + Validation listing)
    - installed `~/.claude/skills/diagnose/passes/03f-layering.md`: 1 occurrence (matches in-repo)
    - installed `~/.claude/skills/diagnose/SKILL.md`: 1 occurrence (matches in-repo)
    - installed `~/.claude/methodology-changelog.md`: 3 occurrences (matches in-repo)
  - **Bidirectional sha256 ship hashes** (mini-CAD N=4 file list):
    - `skills/diagnose/SKILL.md`: `5da6debc9bddf76a...` (in-repo == installed)
    - `skills/diagnose/passes/03f-layering.md`: `e1af52c7640681eb...` (in-repo == installed)
    - `methodology-changelog.md`: `9d5e664a34fa5017...` (in-repo == installed; new ship hash, replaces slice-017 `06ce0c442874f0aa`)
    - `agents/critique.md`: `f34c967eaaa34413...` (in-repo == installed; preserved at slice-017 ship hash — no Critic-agent edit this slice; CAD-1 invariant holds)
- **Notes**: First introduction of mini-CAD for /diagnose. N-surface schema-pin shape per slice-016 RPCD-1 + slice-017 TPHD-1 precedent N=6 → N=7 stable. The N=3 in-repo "logical surfaces" decompose to N=6 byte-equal surfaces when counting installed copies.

### AC2: Regression integration test confirms zero HIGH layering findings on the F-LAYER-bca9c001 fixture shape; true-positive cross-tier import still fires HIGH

- **Status**: PASS
- **Evidence**:
  - **pytest** (2 tests against synthetic fixtures):
    ```
    tests/skills/diagnose/test_layering_pass_textual_evidence.py::test_synthetic_parallel_types_no_import_yields_zero_high_layering_findings PASSED
    tests/skills/diagnose/test_layering_pass_textual_evidence.py::test_synthetic_real_cross_tier_import_still_fires_high_layering_finding PASSED
    ============================== 2 passed in 0.02s ==============================
    ```
  - **Synthetic fixture inventory** (7 files across 2 trees):
    - `tests/skills/diagnose/fixtures/parallel_types_no_import/`:
      - `src/backend/types.ts` (595 bytes) — backend tier `enum NodeType { A, B, C }` + `TaskType` + `AssigneeType`
      - `frontend/lib/types.ts` (516 bytes) — **parallel** frontend definition of same-named enums
      - `frontend/components/Foo.tsx` (783 bytes) — imports ONLY from `@/lib/types` (frontend-local alias)
      - `frontend/tsconfig.json` (275 bytes) — `compilerOptions.paths.@/* → ["./*"]` rooted at frontend/, physically preventing cross-tier access
    - `tests/skills/diagnose/fixtures/parallel_types_real_import/`:
      - `src/backend/types.ts` (453 bytes) — same backend types
      - `frontend/components/Bar.tsx` (664 bytes) — **real** cross-tier import via `../../src/backend/types` (named + multi-line + side-effect + re-export variants all present)
      - `frontend/tsconfig.json` (275 bytes) — same alias map
  - The `_grep_textual_import` helper in `test_layering_pass_textual_evidence.py` covers ALL the rule's grep variants (5 TS import + 3 re-export + multi-line via `re.DOTALL` + alias-aware via tsconfig `paths` resolution + Python `from`/`import`); regex strings are byte-equal to those in `skills/diagnose/passes/03f-layering.md` Method step 4 per /critique M1 visual byte-equality mitigation.
- **Notes**: The negative-control test (`parallel_types_no_import`) reproduces the F-LAYER-bca9c001 shape and confirms the rule would correctly downgrade or skip. The positive control (`parallel_types_real_import`) confirms the rule does NOT over-suppress true-positives. Per /critique B2 ACCEPTED-PENDING applied at Phase 1: alias-aware grep handles the `@/*` pattern that produced the original witness.

### AC3: methodology-changelog v0.33.0 / LAYER-EVID-1 entry present in-repo + installed with canonical phrase pinned across N=3 surfaces; sibling-scoping discipline via `_extract_v033_body` helper

- **Status**: PASS
- **Evidence**:
  - **pytest** (4 entry-pin tests including slice-018 sibling-scoping discipline + PMI-1 v1.1 atomic-bump invariant):
    ```
    tests/methodology/test_methodology_changelog.py::test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed PASSED
    tests/methodology/test_methodology_changelog.py::test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase PASSED
    tests/methodology/test_methodology_changelog.py::test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body PASSED
    tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant PASSED
    ============================== 4 passed in 0.06s ==============================
    ```
  - **N=3 surface pin** (canonical phrase `textual import-evidence requirement`):
    - Surface 1: `skills/diagnose/passes/03f-layering.md` Method step 4 prose (the PRIMARY carrier, with literal regex strings byte-equal to test helper)
    - Surface 2: `skills/diagnose/SKILL.md` Step 5 cross-reference paragraph
    - Surface 3: `methodology-changelog.md` v0.33.0 entry (in-repo + installed)
  - **Sibling-scoping helper** (`_extract_v033_body(content) -> str`):
    - Lives at `tests/methodology/test_methodology_changelog.py` adjacent to slice-018's `_extract_v031_body` per slice-018 sibling-scoping discipline N=2 cumulative
    - Boundary: between `## v0.33.0` and `## v0.32.0` heading markers
    - Regression test asserts the helper retires the global-substring fallacy on synthetic content with v0.33.0 body stripped + v0.32.0 body carrying the canonical phrase as a foil — single-code-path discipline per slice-018 /critique M2 ACCEPTED-FIXED
  - **PMI-1 v1.1 atomic-bump invariant**: `plugin.yaml.version == VERSION == 0.33.0` (5th atomic bump post-slice-014 retirement of supersession pattern)
- **Notes**: Helper-extraction asymmetry mitigation per slice-018 /critique-review m-add-2 + slice-019 DR-1 class (b) catch: `_extract_v031_body` (slice-018) + `_extract_v033_body` (slice-019) coexist as N=2 sibling instances. Generalization to `_extract_version_body(content, version)` deferred until N≥3 (next codification slice's entry-pin tests).

### AC4: ADR-017 exists at `architecture/decisions/ADR-017-textual-evidence-requirement-for-diagnose-boundary-findings.md` with canonical phrase

- **Status**: PASS
- **Evidence**:
  - **pytest**:
    ```
    tests/methodology/test_methodology_changelog.py::test_adr_017_exists_and_names_layer_evid_1_canonical_phrase PASSED
    ============================== 1 passed in 0.04s ==============================
    ```
  - **ADR-017 structural check**:
    - File present at `architecture/decisions/ADR-017-textual-evidence-requirement-for-diagnose-boundary-findings.md`
    - Frontmatter: `id: ADR-017`, `slice: slice-019-harden-diagnose-layering-evidence`, `reversibility: cheap`, `status: accepted`
    - Sections: Context (witness narrative), Options considered (A vs B vs C), Decision (Option B with 4-point rationale), Consequences (downstream changes within + outside slice + no-changes-to + future flexibility), Reversibility, **Recursive self-application (RSAD-1)** section per /critique M2 ACCEPTED-FIXED + /critique-review M-add-2 wording refinement (slice-019 IS the codification slice AND canonical reference instance #1 at codification time, mirroring slice-015 SCPD-1 + slice-017 TPHD-1 precedent; "post-codification N=1" framing retired per M-add-2)
    - Canonical phrase `textual import-evidence requirement` present in the ADR body
  - **ADR-pin convention**: N=4 stable → **N=5 stable** with ADR-017 added (ADR-013 + ADR-014 + ADR-015 + ADR-016 + ADR-017)
- **Notes**: ADR-017 documents the Option-A-vs-B trade-off (graphify-level fix vs pass-template-level fix) with reversibility=cheap. The R-3 escalation criteria document when Option A would become warranted (N≥2 distinct slices reporting symbol-conflation false-positives in other passes/consumers).

### AC5: R-3 added to risk-register.md per RR-1 schema documenting the broader-class concern (graphify symbol-resolution may conflate same-name cross-file symbols into phantom edges); status=mitigating; reversibility=cheap

- **Status**: PASS
- **Evidence**:
  - **pytest**:
    ```
    tests/methodology/test_risk_register_audit_real_file.py::test_r_3_added_post_slice_019_with_graphify_symbol_conflation_class PASSED
    ============================== 1 passed in 0.03s ==============================
    ```
  - **risk-register.md inventory** (`grep '^## R-'`):
    ```
    7:## R-1 — Cwd-mismatch tool denial for spawned subagents in /diagnose
    28:## R-3 — Graphify symbol-resolution may conflate same-name cross-file symbols into phantom edges
    46:## R-2 — No programmatic test ensures /diagnose emits cwd-mismatch warning at runtime
    ```
  - **RR-1 audit** (full register parse): `Total risks: 3`, `violation_count: 0` — all 3 risks parse cleanly under RR-1 schema; no format violations
  - **R-3 fields verified by test**:
    - `status == "mitigating"` (NOT `retired` because graphify-level root cause is untouched)
    - `reversibility == "cheap"` (LAYER-EVID-1 prose can be retired in <1 day if graphify is later fixed upstream)
    - `title` contains broader-class signal: "Graphify symbol-resolution may conflate same-name cross-file symbols into phantom edges" — matches the four required keyword signals (`symbol`, `conflate`, `phantom`, `graphify`)
- **Notes**: R-3's escalation criteria spell out the promotion path: if `/critic-calibrate` flags symbol-conflation false-positives in other /diagnose passes (`02-architecture`, `03d-half-wired`, `03e-contradictions`) OR in other graphify consumers (`/architect`, `/validate`, `/sprint-runner`, etc.) at N≥2 distinct slices, promote a follow-on slice to either extend LAYER-EVID-1 to those passes or fix graphify symbol-resolution upstream. R-3 is the explicit tracker for the broader-class concern beyond the witness pass.

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: This slice modifies methodology prose + adds test infrastructure. No runtime user data, no multi-user/multi-device flow, no synchronization, no sharing. The slice's effects manifest entirely on the local machine through file content + test outcomes. Single-instance validation is sufficient.

## VAL-1 layered safety checks (Step 5b)

```
$PY -m tools.validate_slice_layers --slice architecture/slices/slice-019-harden-diagnose-layering-evidence \
  --changed-files <16 in-repo files> --imports-allowlist tests

VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).
Clean — both layers passed.
```

**Layer A (Credential scan)**: 0 findings. No AWS keys, GitHub PATs, Slack tokens, JWTs, PEM private keys, Anthropic/OpenAI API keys, or generic `api_key = "..."` literals in any of the 16 in-repo files changed by this slice.

**Layer B (Dependency hallucination check)**: 0 findings. All Python imports in the changed test files resolve cleanly against declared deps (`pyproject.toml` + `requirements.txt`) plus the `tests` allowlist (project-internal namespace package, slice-003 VAL-1 Layer B `--imports-allowlist tests` precedent N=17 cumulative).

## WS-1 walking-skeleton audit (Step 5c)

**Not applicable.** Mission-brief carries `**Walking-skeleton**: false` — this is a methodology codification slice, not a walking-skeleton vertical. WS-1 audit returns clean per default-off semantics.

## ETC-1 exploratory-charter audit (Step 5d)

**Not applicable.** Mission-brief carries `**Exploratory-charter**: false` — methodology codification slice with N=1 witnessed failure mode + targeted regression coverage; charter-based exploratory testing doesn't fit the scope. ETC-1 audit returns clean per default-off semantics.

## Shippability catalog regression check (Step 5.5)

**Result**: PASS (no regressions)

Full project test suite (superset of shippability catalog) ran:

```
$PY -m pytest tests/ --no-header -q
[447 passed in 3.41s]
```

All 447 tests PASS. The shippability catalog has 19 entries; the full test run is a strict superset (every shippability entry's pytest command is a subset of the 447 collected). No prior slice's critical path was broken by this slice.

**Per-row coverage** (sampled — full superset run is the canonical signal):
- Row 18 (slice-018 RPCD-1 sibling-scoping): `_extract_v031_body` helper still present and functional (sibling of new `_extract_v033_body`); slice-018 regression test passes against unchanged v0.31.0 entry body
- Row 17 (slice-017 TPHD-1): mission-brief + design.md self-application discipline preserved (slice-019 IS canonical reference instance #3 of TPHD-1 at all 3 sub-modes, empirically verified by edit pattern + Phase 2/3 transitions)
- Row 16 (slice-016 RPCD-1 Dim 9): agents/critique.md byte-equal at slice-017 ship hash `f34c967eaaa34413` preserved (CAD-1 invariant); 9 sub-clause Dim 9 structure unchanged
- Rows 1-15: full superset run confirms all pass

**Slices since last full catalog run**: 1 (this slice — first run since slice-018 ship). Within the >3-slice ⚠️ threshold from /status documentation. No flag.

## Reality surprises

None. The /critique + /critique-review cycle surfaced the unknowns BEFORE /build-slice (B2 ES-module variants, B3 mini-CAD TF-1 row split, M4 sibling-scoping inheritance, M-add-1 schema-enum mismatch, M-add-2 RSAD-1 wording incoherence) — all addressed at Phase 1 with TPHD-1 sub-mode (a) harmonization. The slice shipped with **ZERO classical build-time DEVIATIONs**, regaining the streak after slice-018's N=1 break.

## Audit gate summary at /validate-slice ship

| Gate | Result | Evidence |
|------|--------|----------|
| TF-1 `--strict-pre-finish` | clean | 12/12 PASSING |
| WIRE-1 | clean | zero-row matrix accepted |
| BC-1 | clean | no rules apply (BC-PROJ-2 negative-anchor empirical-clean N=6 cumulative) |
| RR-1 | clean | 3 risks (R-1, R-2, R-3); violation_count=0 |
| PMI-1 v1.1 | clean | 24 skills + 5 agents + 15 tools at version 0.33.0 (5th atomic bump under retirement-proof N=5) |
| CAD-1 | clean | agents/critique.md byte-equal at slice-017 ship hash `f34c967eaaa34413` |
| Mini-CAD for /diagnose (NEW) | clean | 2 single-file tests PASSING (SKILL.md + 03f-layering.md byte-equal in-repo↔installed) |
| Triage audit | clean | NEEDS-FIXES verdict per TRI-1; 10 findings + 2 meta-Critic |
| Critique-review audit | clean | EXTEND verdict; M-add-1 + M-add-2 added |
| VAL-1 Layer A (credential scan) | clean | 0 secret findings |
| VAL-1 Layer B (dependency hallucination) | clean | 0 import findings |
| WS-1 walking-skeleton | n/a | brief carries Walking-skeleton: false |
| ETC-1 exploratory-charter | n/a | brief carries Exploratory-charter: false |
| Shippability catalog (19 rows) | clean | 447/447 superset run passes |

## Slice next-action recommendation

All 5 ACs PASS with evidence. VAL-1 + shippability catalog clean. No reality surprises. **Proceed to `/reflect`** to capture learnings (Validated / Corrected / Discovered / Deferred categories per Reflect template).
