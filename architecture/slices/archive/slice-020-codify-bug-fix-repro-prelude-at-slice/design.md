# Design: Slice 020 codify-bug-fix-repro-prelude-at-slice

**Date**: 2026-05-14
**Mode**: Standard

## What's new

- `skills/slice/SKILL.md`: NEW `### Step 3c: Bug-fix prelude (BFRD-1)` section inserted between existing `### Step 3b: If user has their own idea` (close at L140) and `### Step 4: Define the slice` (header at L142). Section names both detection modes ((a) `fix-` name-prefix + (b) explicit bug-fix signal from candidate source), STOP-and-route-to-`/repro` behavior on missing failing test, and mission-brief consequences (failing-test path under `Dependencies`, one AC asserting "repro test PASSES at slice end"). Section is location-pinned between Step 3b end-anchor and Step 4 header-anchor.
- `methodology-changelog.md`: NEW v0.34.0 entry codifying BFRD-1 (Bug-Fix Repro Discipline-1, -D suffix N=5 → N=6 stable). Entry names both detection modes + STOP-and-route behavior + ADR-018 pin + Limitations note (prose-heuristic; no audit-enforced gate; v2 `tools/bfrd_1_audit.py` deferred until N≥3 violations recur).
- `architecture/decisions/ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md`: NEW ADR; reversibility=cheap with magnitude justification ~11 sites (per /critique B3 ACCEPTED-FIXED recount); supersedes=null; extends ADR-016 (TPHD-1) at the cross-cutting-tooling skill-prose-discipline layer.
- `tests/methodology/test_slice_skill.py`: appends NEW SECTION `# --- Slice-020 / BFRD-1 bug-fix repro prelude pinning ---` with 2 prose-pin tests (`test_slice_skill_md_bfrd_1_prelude_present` + `test_slice_skill_md_bfrd_1_prelude_location_pinned`) following slice-010 MCT-1 + slice-017 TPHD-1 `_present` + `_location_pinned` duality precedent N=6 stable.
- `tests/methodology/test_methodology_changelog.py`: appends NEW SECTION `# --- Slice-020 / BFRD-1 entry pinning ---` with 4 tests (`test_v_0_34_0_bfrd_1_entry_present_in_repo_and_installed` + `test_v_0_34_0_bfrd_1_entry_names_both_detection_modes` + `test_v_0_34_0_bfrd_1_entry_names_stop_and_route_behavior` + `test_adr_018_exists_and_names_bfrd_1_canonical_phrase`).
- `architecture/shippability.md`: appends row 20 enumerating BFRD-1 critical-path tests.
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`: atomic bump 0.33.0 → 0.34.0 per PMI-1 v1.1 retirement-proof N=5 → N=6 stable.

## What's reused

- [[skills/slice/SKILL.md]] — existing skill, single-surface edit (Step 3c insertion between L140 and L142)
- [[skills/repro/SKILL.md]] — referenced by Step 3c prose, NOT modified
- [[architecture/decisions/ADR-016]] — TPHD-1 precedent for skill-prose-discipline reversibility analysis
- [[methodology-changelog.md]] — existing format; v0.34.0 follows v0.33.0 (LAYER-EVID-1) entry pattern
- [[tests/methodology/test_slice_skill.py]] — existing prose-pin tests at slice-010 MCT-1; new tests follow same pattern (substring + location-pin duality)
- [[tests/methodology/test_slice_skill_drift.py]] — existing mini-CAD-1 byte-equality test on `skills/slice/SKILL.md`; transitions PASSING → WRITTEN-FAILING → PASSING at Phase 2 per slice-010 precedent N=10 stable
- [[tests/methodology/test_methodology_changelog.py]] — existing pattern of entry-pin tests + `_extract_v0NN_0_body` sibling-scoping helpers per slice-018 + slice-019 N=2 cumulative (per /critique M5 ACCEPTED-FIXED + Audit 4 Option C: slice-020 generalizes to `_extract_version_body(content, version)` at rule-of-three trigger; existing `_extract_v031_body` + `_extract_v033_body` become thin wrappers for backward compatibility)
- CAD-1 byte-equality on `agents/critique.md` — slice does NOT touch it; preserved at slice-019 ship hash `f34c967eaaa34413...`

## Components touched

### `skills/slice/SKILL.md`

- **Responsibility**: define the next vertical slice; produce mission brief; route bug fixes through `/repro` prerequisite (NEW per BFRD-1)
- **Lives at**: `skills/slice/SKILL.md` (modified — single-surface Step 3c insertion)
- **Key interactions**: read by Claude main thread at `/slice` invocation; read by `tests/methodology/test_slice_skill.py` for prose-pin assertions; byte-equal mirror at `~/.claude/skills/slice/SKILL.md` per mini-CAD-1

The Step 3c insertion sits structurally between candidate selection (Step 3 / 3b) and slice definition (Step 4). This is the natural inflection point — the candidate is chosen but the slice isn't yet defined, so STOPping to route bug-fix candidates through `/repro` preserves `/repro`'s ordering invariant (failing test exists BEFORE slice exists) without merging `/repro`'s body into `/slice`.

### `methodology-changelog.md`

- **Responsibility**: rolling record of behavior-changing methodology rules with rule-ID + defect class + validation per entry
- **Lives at**: `methodology-changelog.md` (in-repo canonical) + `~/.claude/methodology-changelog.md` (installed mirror, bidirectional sha256 byte-equal per CAD-1)
- **Key interactions**: `/status` reads most recent entry; `tests/methodology/test_methodology_changelog.py` pins entry presence + content + sibling-scoping; `test_critique_agent_drift.py` does NOT cover this file (different mini-CAD)

### `architecture/decisions/ADR-018`

- **Responsibility**: written justification for the BFRD-1 codification decision with reversibility tag + magnitude estimate + revert path
- **Lives at**: `architecture/decisions/ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md` (NEW)
- **Key interactions**: pinned by `test_adr_018_exists_and_names_bfrd_1_canonical_phrase`; cross-referenced from methodology-changelog v0.34.0 entry

## Contracts added or changed

None. This slice is pure prose-discipline codification at one skill surface plus methodology-changelog metadata. No endpoints, events, schemas, or data-model changes.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `architecture/decisions/ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md` | `methodology-changelog.md` v0.34.0 entry (cross-reference) | `tests/methodology/test_methodology_changelog.py::test_adr_018_exists_and_names_bfrd_1_canonical_phrase` | — |

No new Python modules / no new test files introduced (extends existing `test_slice_skill.py` + `test_methodology_changelog.py`). ADR-018 is documentation, not a runtime module — consumer entry point is the cross-reference from the methodology-changelog entry; consumer test is the ADR-pin assertion.

## Decisions made (ADRs)

- [[ADR-018]] — Codify BFRD-1 (Bug-Fix Repro Prelude Discipline) as 1-surface skill-prose discipline at `skills/slice/SKILL.md` Step 3c — reversibility: **cheap**

## Authorization model for this slice

N/A — pure prose-discipline codification; no runtime auth surface touched.

## Error model for this slice

N/A — pure prose codification. The Step 3c prose itself defines a behavioral routing rule (STOP-and-instruct-user when bug-fix slice lacks failing test), but this is read by Claude main thread at `/slice` time; no error codes / exceptions are raised in code.

## Step 3c content structure (canonical-form prose plan)

The new Step 3c section structurally mirrors `/build-slice` SKILL.md's Prerequisite-check bullet style (per slice-017 TPHD-1 sub-mode (c) ACCEPTED-FIXED placement). Section structure:

1. Header: `### Step 3c: Bug-fix prelude (BFRD-1)`
2. Opening sentence stating purpose (route bug-fix slices through `/repro` prerequisite).
3. Detection-mode list:
   - **Sub-mode (a) name-shape fast-path**: candidate name matches one of `fix-*` (prefix), `*-fix` (suffix — witnessed in-project at `slice-001-diagnose-orchestration-fix` per /critique B1), `bugfix-*`, `hotfix-*`, `defect-*`, `repair-*`, `patch-*`, `harden-*-bug` (regex set covering canonical bug-fix naming variants). **Name-shape detection is necessary-but-not-sufficient** — it's a fast-path fallback only; the primary signal is mode (b).
   - **Sub-mode (b) candidate-source signal (PRIMARY)**: candidate sourced from risk-register bug-class entry, prior reflection's "bug observed" note, user description explicitly identifying a defect, or `/repro` invocation context. When mode (a) misses (e.g., a security-hardening slice that fixes a latent defect), mode (b) catches.
4. **Verification mechanism (per /critique B2 + /critique-review M-add-2 ACCEPTED-FIXED Option (a))**: when either detection mode fires, Claude greps `architecture/shippability.md` for a row whose `Command` cell targets `tests/bugs/*` (the documented `/repro` skill convention at `skills/repro/SKILL.md` L87/L94/L114). If no `tests/bugs/*`-targeting row exists → ask the user to paste the failing-test path and confirm it was just-added by `/repro` (verbal-claim-with-path is the documented fallback covering `/repro`'s "or project's convention for bug-fix tests" caveat at L87 — bug-fix tests outside `tests/bugs/`). If the user can't produce a path → STOP-and-route. The prior `bug:` provenance branch was DROPPED at /critique-review per M-add-2 RPCD-1 sub-mode (b) class catch: shippability rows 1-19 contain zero `bug:` provenance comments AND no /repro skill prose update in this slice mandates `bug:` going forward — branch was aspirational. Canonical phrase to pin: `shippability.md grep verification`.
5. STOP-and-route behavior with verbatim instruction the user receives: *"This slice is a bug fix. Before defining the mission brief, run `/repro <issue>` to establish a failing test that reproduces the bug. The test must FAIL with the expected signature. Then re-invoke `/slice` and cite the failing-test path under `Dependencies`."*
6. Mission-brief consequences when proceeding past Step 3c (failing-test path cited under Dependencies; one AC asserting "repro test PASSES at slice end").
7. Cross-reference to [[skills/repro/SKILL.md]] (one-way dependency; `/repro` is not modified).

Canonical phrase pinned in skill prose: `BFRD-1` rule ID (in section header) + `bug-fix repro prelude discipline` (in section opener) + `shippability.md grep verification` (in verification-mechanism bullet). Cross-surface phrase pinning in methodology-changelog v0.34.0 entry (in-repo + installed) preserves N=3 surface convention per N=6 stable precedent.

**Prose-pin test assertion locks (per /critique-review M2 SUSPICIOUS ACCEPTED-FIXED clarification)**: the `_prelude_present` test MUST assert the literal canonical phrase `bug-fix repro prelude discipline` (substring search in Step 3c section bounds), NOT merely the `BFRD-1` rule ID. This transitively requires Step 3c body to contain the literal phrase, locking the design.md commitment via test enforcement (closes the first-Critic M2 OVERRIDDEN rationale's "phrase appears naturally in section opener" claim into a concrete test-assertion contract that survives /build-slice Phase 1 prose drafting). The `_verification_mechanism_present` test asserts the literal canonical phrase `shippability.md grep verification` in Step 3c section bounds. Both literals are substring-checked, NOT regex-matched, per slice-009 DEVIATION-1 case-sensitivity discipline.

## Audits

**Audit 1 — Step 3c anchor uniqueness in `skills/slice/SKILL.md`**

Empirically verified at design time: the existing string `### Step 3b: If user has their own idea` appears exactly once in `skills/slice/SKILL.md` (substring search returns 1 hit at L134); `### Step 4: Define the slice` appears exactly once (substring search at L142). Step 3c insertion between these two anchors is unambiguously locatable. The `_location_pinned` scoped-find test uses these as start/end anchors per slice-009 DEVIATION-2 + slice-010 anchor-uniqueness algorithm-path-conformance discipline N=10 stable.

**Audit 2 — `bfrd_1` literal absence (sanity check)**

Empirically verified at design time: `grep -c "BFRD-1" skills/slice/SKILL.md methodology-changelog.md architecture/decisions/*.md tests/methodology/test_slice_skill.py tests/methodology/test_methodology_changelog.py` returns 0 across all surfaces pre-slice — no pre-existing references to BFRD-1 mean the slice introduces the literal cleanly. (Verified by reading the files; no prior commits reference BFRD-1.) Per RSAD-1 sub-mode (b) re-introduction discipline N=11 stable: positive-form assertions only; no negative anti-form enumeration.

**Audit 3 — Entry-pin function structural separation (EPGD-1 self-application)**

Per slice-019 reflection N=6 → N=7 stable: 0 of 15 prior `test_v_0_NN_0_*` entry-pin functions in `tests/methodology/test_methodology_changelog.py` may be touched. Slice-020 adds NEW SECTION header `# --- Slice-020 / BFRD-1 entry pinning ---` + 4 new functions (3 entry-pin + 1 ADR-pin). Function-name-level grep confirms 15 prior + 4 new = 19 total post-slice (3 new entry-pin functions for v0.34.0 — note v0.34.0 single, not doublet, since BFRD-1 has only one canonical sub-clause; per slice-014 (a)↔(b) duality convention only multi-sub-mode rules get doubled entry-pin functions; BFRD-1 has detection modes but a single behavioral rule).

**Audit 4 — Sibling-scoping discipline (RPCD-1 sub-mode (c) self-application) — Decision revised per /critique M5**

Per slice-018 + slice-019 N=2 cumulative: when a future slice strips canonical markers from the v0.34.0 entry body, the v0.34.0 entry-pin tests MUST surface the strip rather than silently pass via global substring match across other entries. Three options considered:
- (Option A — inline) Direct `## v0.34.0` boundary string slicing inline in each test function. **Rejected per /critique M5**: 3 new entry-pin tests × inline boundary slicing = 3 fresh sites of the pattern; slice-020 IS the next codification slice and the aggregated lesson at `slices/_index.md` explicitly says "Promote to `_extract_version_body(content, version) -> str` at N=3 (next codification slice)". Inline would violate the aggregated-lessons promotion threshold and re-introduce the helper-asymmetry-foreshadowing-decline class that slice-018 m-add-2 codified.
- (Option B — version-local helper) Extract `_extract_v034_body(content)` module-level helper parallel to slice-018 `_extract_v031_body` + slice-019 `_extract_v033_body`. **Rejected**: adds N=3 instance of identical pattern — textbook Fowler rule-of-three violation; cleaner to generalize.
- (Option C — generalized helper, CHOSEN per /critique M5 ACCEPTED-FIXED): Introduce `_extract_version_body(content: str, version: str) -> str` module-level helper accepting version string `"0.31.0"`/`"0.33.0"`/`"0.34.0"`. Keep existing `_extract_v031_body` + `_extract_v033_body` as thin wrappers calling `_extract_version_body(content, "0.31.0")` + `_extract_version_body(content, "0.33.0")` for backward compatibility — slice-018 + slice-019 existing tests continue passing unchanged. Slice-020's 3 new entry-pin tests + 1 sibling-scoping regression test call `_extract_version_body(content, "0.34.0")` directly.

**Decision**: Option C — generalize at N=3 per aggregated-lessons promotion threshold. The refactor adds ~20 min to slice-020's build budget (well within 60-90 min envelope per slice-019 N=11 cumulative recursive-self-application precedent). Rule-of-three counter advances N=2 → N=3 stable post-slice-020; future v0.35.0+ entry-pin tests use `_extract_version_body` directly without introducing new wrappers.

**Audit 5 — Mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition (slice-010 precedent)**

Per slice-007 CAD-1 + slice-010 mini-CAD-1 N=10 stable: `tests/methodology/test_slice_skill_drift.py::test_in_repo_and_installed_slice_skill_md_are_content_equal` starts at PASSING (file pair byte-equal at slice start), transitions to WRITTEN-FAILING at Phase 2 (in-repo Step 3c edit; installed copy not yet synced), back to PASSING at Phase 2c post-`Copy-Item` forward-sync. TF-1 plan row 6 reflects this 3-state transition.

**Audit 6 — TPHD-1 self-application probe at all 3 sub-modes (slice-017 precedent N=3 → N=4 stable post-codification)**

If `/critique` fix-prose changes any test function name or AC #N row reference in this design.md or the mission-brief, the mission-brief TF-1 plan MUST be harmonized in the SAME fix block (sub-mode (a)). Same for `/critique-review` fix-prose (sub-mode (b)). `/build-slice` Phase 0 Prerequisite-check MUST verify TF-1 plan rows match design.md function names BEFORE Phase 1 plan-mode entry (sub-mode (c)). Slice-020 IS canonical reference instance #4 of TPHD-1.

**Audit 7 — BFRD-1 self-application N/A documented (revised per /critique M1)**

Slice-020 is a NEW-feature codification slice (codifies BFRD-1), not a bug-fix slice. The STOP-route does NOT trigger on slice-020 itself. The discipline is exercised PROSPECTIVELY at slice-021+ on the first slice whose candidate name matches a mode-(a) bug-fix naming variant OR whose source signal identifies a defect. Documented under must-not-defer per /slice convention; the BFRD-1 N=1 canonical-reference-instance count starts at the first prospective application, not at codification time.

This is a **contingent N/A**, not an architectural impossibility (per /critique M1 ACCEPTED-FIXED): slice-020 happens to be a NEW-feature codification slice that does not fix a runtime bug, so BFRD-1's STOP-route is vacuously satisfied at codification time. A hypothetical future codification-AND-bug-fix slice (codifying a new methodology rule while ALSO fixing a runtime defect) would self-apply BFRD-1 trivially via mode (a) or mode (b) detection. This differs from slice-015 SCPD-1 / slice-017 TPHD-1 / slice-019 LAYER-EVID-1 (which had self-application at codification time because the rule applied to the codification slice's own artifacts); BFRD-1 only applies to slices whose mission brief describes a bug fix.

**Audit 8 — Surface count parity with prior 1-surface codifications (clarified per /critique m3)**

Slice-010 (MCT-1, 1 skill file) vs slice-017 (TPHD-1, 3 skill files) vs slice-020 (BFRD-1, 1 skill file). Slice-020 is the 1-surface variant. Test count parity: slice-010 had 5 prose-pin tests; slice-020 has 3 prose-pin tests (BFRD-1 prelude_present + prelude_location_pinned + verification_mechanism_present per /critique B2 ACCEPTED-FIXED) + 4 entry-pin/ADR-pin tests = 7 total methodology-test additions (similar density). TF-1 row count: slice-010 had 7 rows; slice-020 has 11 rows post-B2 ACCEPTED-FIXED (was 9 pre-fix; +2 verification-mechanism rows added per /critique B2). Within precedent envelope.

**Clarification (per /critique m3 ACCEPTED-FIXED)**: slice-020 has fewer skill-prose tests than slice-010's 5 because BFRD-1's discipline is structurally simpler than MCT-1's — BFRD-1 pins a STOP-route plus verification mechanism (3 phrases); MCT-1 pins a bullet plus evidence-paragraph with sub-class anchors (5 anchors). The 3-vs-5 count is structural, not a regression on prose-pin density.

## Test-first plan (mirrors mission-brief)

The 10-row TF-1 plan in `mission-brief.md` is the canonical plan (was 9; +1 row added at /critique B2 ACCEPTED-FIXED for verification-mechanism prose-pin). Test paths and function names locked at design time (harmonized to mission-brief in same /critique fix block per TPHD-1 sub-mode (a) self-application N=3 → N=4 stable):

- `tests/methodology/test_methodology_changelog.py::test_v_0_34_0_bfrd_1_entry_present_in_repo_and_installed`
- `tests/methodology/test_methodology_changelog.py::test_v_0_34_0_bfrd_1_entry_names_both_detection_modes`
- `tests/methodology/test_methodology_changelog.py::test_v_0_34_0_bfrd_1_entry_names_stop_and_route_behavior`
- `tests/methodology/test_methodology_changelog.py::test_v_0_34_0_bfrd_1_entry_names_verification_mechanism` (NEW per /critique B2 ACCEPTED-FIXED — pins `shippability.md grep verification` canonical phrase in changelog body)
- `tests/methodology/test_methodology_changelog.py::test_adr_018_exists_and_names_bfrd_1_canonical_phrase`
- `tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant` (existing PMI-1 v1.1 invariant; passes unchanged through atomic version bump)
- `tests/methodology/test_slice_skill.py::test_slice_skill_md_bfrd_1_prelude_present`
- `tests/methodology/test_slice_skill.py::test_slice_skill_md_bfrd_1_prelude_location_pinned`
- `tests/methodology/test_slice_skill.py::test_slice_skill_md_bfrd_1_verification_mechanism_present` (NEW per /critique B2 ACCEPTED-FIXED — pins `shippability.md grep verification` canonical phrase in Step 3c skill prose)
- `tests/methodology/test_slice_skill_drift.py::test_in_repo_and_installed_slice_skill_md_are_content_equal` (existing mini-CAD-1; PASSING → WRITTEN-FAILING → PASSING transition per Audit 5)

**Helper-generalization scope** (per /critique M5 ACCEPTED-FIXED → Audit 4 Option C): introduce `_extract_version_body(content: str, version: str) -> str` module-level helper at `tests/methodology/test_methodology_changelog.py` at /build-slice Phase 1a; keep existing `_extract_v031_body` + `_extract_v033_body` as thin wrappers calling the generalized form; new v0.34.0 entry-pin tests call `_extract_version_body(content, "0.34.0")` directly. Slice-018 + slice-019 existing tests unchanged at call-site.

Per slice-017 TPHD-1 sub-mode (c) self-application: at `/build-slice` Phase 0, verify TF-1 plan rows match these function names BEFORE Phase 1 plan-mode entry. Any /critique or /critique-review fix-prose that renames any of these functions MUST harmonize the TF-1 plan + design.md test-name list in the same fix block.
