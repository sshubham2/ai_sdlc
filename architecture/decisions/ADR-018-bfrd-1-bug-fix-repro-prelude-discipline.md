---
id: ADR-018
title: Codify BFRD-1 bug-fix repro prelude discipline as 1-surface skill-prose discipline at /slice Step 3c
date: 2026-05-14
slice: slice-020-codify-bug-fix-repro-prelude-at-slice
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-018: Codify bug-fix repro prelude discipline (BFRD-1)

**Note on rule-ID naming** (per -D suffix calibration-trail convention N=5 → N=6 stable post-RSAD-1 v0.26.0 + EPGD-1 v0.28.0 + SCPD-1 v0.30.0 + RPCD-1 v0.31.0 + TPHD-1 v0.32.0): the rule is **BFRD-1 "Bug-Fix-Repro-Discipline"** with **-D suffix** at end of abbreviation, signaling skill-prose-heuristic semantics applied at /slice-time, distinct from audit-enforced gate semantics of sibling rules (BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1, each with a corresponding `tools/*_audit.py` enforcing the rule programmatically). BFRD-1 lives in `skills/slice/SKILL.md` Step 3c body prose only. v2 candidate `tools/bfrd_1_audit.py` (programmatic detection: scan mission-brief for `fix-*` name + presence of failing-test reference under Dependencies) deferred until N≥3 BFRD-1 violations recur post-codification at slice-021+.

## Context

CLAUDE.md (project root, brownfield rules) carries a "Tests-first for bug fixes" rule explicitly: *"Reproduce with a failing test before fixing (run `/repro`)."* The `/repro` skill exists as a standalone discipline that establishes a failing test before the bug-fix slice begins, preserving test-first ordering on bug fixes.

However, `/slice` (the canonical entry point for defining the next vertical cut) does NOT enforce this prerequisite. The current flow assumes the user remembers to invoke `/repro` first when the next slice is a bug fix; `/slice` itself happily produces a mission brief for `fix-*`-named slices without checking that a failing repro test exists. This creates an exercise-on-the-honor-system gap:

- **Failure mode 1 — Forgot `/repro` entirely**: user invokes `/slice "fix-thumbnail-orientation"` directly, `/slice` produces a mission brief, `/build-slice` proceeds, fix is implemented, no failing test ever existed, no regression guard installed → bug can silently regress at any future slice.
- **Failure mode 2 — Mock-test-on-buggy-code mirage**: user writes a test as part of the fix slice rather than before it. Test passes on buggy code because it asserts what the buggy code does, not what correct code should do. Bug appears "fixed and tested" but neither claim is grounded.
- **Failure mode 3 — Test-first inversion**: user invokes `/slice` first, then `/repro` after, with the mission brief already written and AC list locked. The failing test exists but the slice's ACs were defined without referencing it. The repro test isn't promoted to AC, the regression guard discipline is half-applied.

The empirical evidence base for codifying this:
- CLAUDE.md states the rule but provides no enforcement mechanism. Skill prose at `skills/slice/SKILL.md` carries no bug-fix-detection prelude. The rule lives only in the project-root CLAUDE.md, which the user reads (Claude reads it too) but doesn't get checked at `/slice` runtime against the actual slice candidate.
- Slice-016 reflection's "Strongest slice-017 candidates" + slice-017 / slice-018 / slice-019 reflections' "Strongest slice-NN+1 candidates" all carry the note: *"cleanup of stale R-1 + R-2 if user pursues — both untouched for N slices, require `/repro` first"*. The note acknowledges the existing skip-`/repro` risk for two specific risks (R-1 cwd-mismatch /diagnose; R-2 no programmatic /diagnose warning test); the broader pattern (any bug fix needs `/repro`) is implicit but uncodified.
- User-invoked /slice at slice-020 with explicit `codify-bug-fix-repro-prelude-at-slice` argument ratchets codification ahead of N=2 promotion threshold. Justification: structurally clear lesson + small codification cost + the rule is already half-stated in CLAUDE.md ("Tests-first for bug fixes"); BFRD-1 just operationalizes the existing implicit discipline at the skill-runtime surface where it's actually enforceable.

User question at slice-020 origination: *"I want slice to handle new features as well as bug. Can slice use repro skill for bug and it's usual for new features? What's your opinion?"* The chosen approach (this ADR's Option 1 below) preserves `/repro`'s ordering invariant while making `/slice` the single entry point — `/slice` detects bug-fix candidates and STOPs to route through `/repro` when no failing test exists yet, rather than merging `/repro`'s body into `/slice`.

The cost of codification is small (1-surface skill-prose insertion + methodology-changelog entry + ADR + 2 prose-pin tests + 4 methodology-entry tests + 1 shippability row); the cost of waiting for N=2 recurrence is one more avoidable bug-fix slice shipped without a regression guard. The discipline is structurally analogous to TPHD-1 (slice-017) — both are skill-prose preludes inserted at named locations in skill SKILL.md files to enforce a multi-step discipline at the right inflection point.

## Options considered

### Option 1 — 1-surface skill-prose discipline at `/slice` Step 3c (CHOSEN)

Insert a NEW `### Step 3c: Bug-fix prelude (BFRD-1)` section in `skills/slice/SKILL.md` between existing `### Step 3b: If user has their own idea` (L134) and `### Step 4: Define the slice` (L142). Section names:

1. **Detection mode (a)** — name-prefix check: candidate's verb-object name starts with `fix-` (e.g., `fix-thumbnail-orientation`, `fix-receipt-upload-edge-cases`). Auto-detected from the chosen name.
2. **Detection mode (b)** — candidate-source signal: candidate was sourced from the risk register's bug-class entry, from a `/repro` invocation, from user description explicitly identifying a defect, or from a prior slice's reflection naming this as a known-buggy area.
3. **STOP-and-route behavior** — when either detection mode fires AND no failing repro test is pinned: `/slice` STOPS and instructs the user verbatim: *"This slice is a bug fix. Before defining the mission brief, run `/repro <issue>` to establish a failing test that reproduces the bug. The test must FAIL with the expected signature. Then re-invoke `/slice` and cite the failing-test path under `Dependencies`."*
4. **Proceed-with-repro consequences** — if the user confirms a failing repro test already exists (or returns post-`/repro` completion): `/slice` continues to Step 4 with two new requirements: (i) the failing-test path is cited under `Dependencies` (e.g., `tests/fixtures/test_thumbnail_orientation_regression.py::test_iphone_exif_rotation`); (ii) one AC asserts "the failing repro test PASSES at slice end".

Codify in `methodology-changelog.md` v0.34.0 entry naming BFRD-1 + 2 detection modes + STOP-and-route behavior + cross-reference to CLAUDE.md "Tests-first for bug fixes" rule + Limitations note acknowledging prose-heuristic semantics (no audit-enforced gate; v2 candidate deferred).

Mirror MCT-1 (slice-010 ADR-009) + TPHD-1 (slice-017 ADR-016) structural shape: terse skill-prose section at named insertion point + N-surface schema-pin + prose-pin tests + Limitations note.

**Pros**:
- 1-surface coverage matches the canonical entry point for the discipline (`/slice` is THE skill that decides whether a bug-fix slice is well-formed; no other skill needs to enforce the prelude).
- Skill-prose-only — no audit-enforced gate at codification time. Prose-heuristic discipline is reversible per slice-011 RSAD-1 + slice-016 RPCD-1 + slice-017 TPHD-1 retirement-proof precedent N=3 stable. v2 `tools/bfrd_1_audit.py` candidate deferred per N=5 prose-first-audit-later convention.
- Prose-pin test scaffolding mirrors slice-010 MCT-1 `test_slice_skill.py` precedent + slice-014/015/016/017 entry-pin + `_location_pinned` duality N=5 stable.
- Reversibility: cheap. Revert path is git diff + superseding changelog entry. ~10-15 min per slice-016 RPCD-1 + slice-017 TPHD-1 magnitude.
- One-way coupling — `/slice` references `/repro`, but `/repro` itself stays unchanged. No risk of two-way coupling drift.

**Cons**:
- Single-skill enforcement means a user who manually bypasses `/slice` (writes a mission brief by hand and proceeds to `/design-slice` directly) escapes the prelude. Mitigated by the cultural convention of always invoking `/slice` to start a slice + by the future v2 audit (which would scan ANY new mission brief for bug-fix signals).
- Detection mode (b) "candidate-source signal" is inherently a soft check (Claude main thread interprets candidate sources). False negatives possible if a bug fix arrives with a non-`fix-` name and no explicit source signal (e.g., `harden-receipt-upload` describing a security bug). Mitigated by user prompt at Step 3c — the section asks the user to confirm "Is this a bug fix?" if name doesn't match `fix-*` but candidate source is ambiguous.

### Option 2 — 2-surface discipline at `/slice` + `/design-slice` Step 0 cross-check

Insert BFRD-1 prose at `/slice` Step 3c (same as Option 1) AND add a defensive cross-check at `/design-slice` Step 0 verifying that bug-fix slices have a failing-test reference in mission-brief Dependencies before producing design.md.

**Pros**: defense-in-depth — catches bug-fix slices that skipped `/slice`'s Step 3c (e.g., user hand-wrote a `fix-*` mission brief and went straight to `/design-slice`).

**Cons**:
- 2-surface insertion (vs 1-surface for Option 1) adds more code-surface for prose drift. Mitigated by prose-pin tests with duality (substring-pin + location-pin per surface = 4 tests across 2 skill files), but doubles the maintenance burden.
- `/design-slice` Step 0 cross-check overlaps with `/build-slice` Phase 0 Prerequisite-check (slice-017 TPHD-1 sub-mode (c)) — three-layer coverage for what is fundamentally a one-time gate at slice-definition time. Risk of redundancy without proportional value.
- **Rejected at slice-020 codification time**: defer until N≥2 instances of "user hand-wrote a bug-fix mission brief bypassing /slice" recur post-codification. The 1-surface variant is sufficient if `/slice` is the canonical entry point (which it is per project convention).

### Option 3 — Promote to `agents/critique.md` Dim 9 10th sub-clause

Codify BFRD-1 as a NEW Dim 9 sub-clause in the adversarial Critic prompt, similar to RPCD-1 / SCPD-1 / TPHD-1 sibling rules. The Critic would flag bug-fix slices at `/critique` time that lack failing-test references under Dependencies.

**Pros**: first-Critic catches bug-fix slices missing repro citation at /critique time, before fix-prose finalizes the mission brief.

**Cons**:
- BFRD-1 is a **timing/sequencing** discipline ("STOP and route to /repro BEFORE writing mission brief"), not an **adversarial-prompt content** discipline (which is what Dim 9 sub-clauses are — fixed dimensions the Critic attacks design along).
- By `/critique` time the mission brief is already written; the Critic flagging "missing failing-test reference" comes AFTER `/slice` should have stopped to invoke `/repro`. Adding Dim 9 sub-clause defends the LATER layer, not the canonical inflection point.
- Per slice-017 ADR-016 reasoning: timing/sequencing disciplines belong in the skill that owns the inflection point, NOT in the adversarial Critic prompt. TPHD-1 lives at `/critique` + `/critique-review` + `/build-slice` skill-prose, not in agents/critique.md Dim 9; BFRD-1 follows the same precedent.
- **Rejected**: misclassifies the discipline. A Dim 9 sub-clause could provide a /critique-time safety net for slices that escape /slice-time detection, but the round-trip cost (slice already designed before discovery) makes /slice-time prevention strictly cheaper per /critique m4 ACCEPTED-FIXED. /critique-time safety net deferred as v2 candidate if BFRD-1 prose escapes detection in real slices at N≥3 first-Critic-MISS instances of "bug-fix slice without failing-test reference reached /critique" post-BFRD-1-codification.

## Decision

**Adopt Option 1** — 1-surface skill-prose discipline at `skills/slice/SKILL.md` Step 3c. Codified as BFRD-1 in `methodology-changelog.md` v0.34.0 with -D suffix calibration-trail convention N=5 → N=6 stable. Canonical phrase `bug-fix repro prelude discipline` pinned across N=3 surfaces per slice-013 EPGD-1 + slice-014 PMI-1 v1.1 + slice-015 SCPD-1 + slice-016 RPCD-1 + slice-017 TPHD-1 N-surface schema-pin precedent N=6 → N=7 instances stable: (1) `skills/slice/SKILL.md` Step 3c prose, (2) in-repo `methodology-changelog.md` v0.34.0 entry, (3) installed `~/.claude/methodology-changelog.md` v0.34.0 entry.

Detection-mode list distinctly named:
- **Detection mode (a) name-prefix check**: `fix-*` slice-name prefix triggers auto-detection.
- **Detection mode (b) candidate-source signal**: explicit bug identification from risk-register entry, prior reflection note, user description, or `/repro` invocation context.

STOP-and-route behavior verbatim:
- When either detection mode fires AND no failing repro test exists: STOP, instruct user to run `/repro <issue>`, await re-invocation of `/slice` post-`/repro` completion.
- When proceeding past Step 3c with confirmed failing repro test: cite failing-test path under `Dependencies`; one AC asserts "the failing repro test PASSES at slice end".

PMI-1 atomic version bump 0.33.0 → 0.34.0 with versioned-gate retirement-proof (PMI-1 v1.1 version-agnostic gate N=5 → N=6 stable; zero test code modification on gate body per slice-014 + slice-015 + slice-016 + slice-017 + slice-019 precedent).

**BFRD-1 contingent N/A at codification time (revised per /critique M1 ACCEPTED-FIXED)**: slice-020 happens to be a NEW-feature codification slice (its name does not match any mode-(a) bug-fix naming variant; its source signal is methodology-codification, not bug-fix). The discipline does NOT trigger STOP-and-route on slice-020 itself, so BFRD-1's check is vacuously satisfied at codification time. The N=1 canonical-reference-instance count starts at the first PROSPECTIVE bug-fix slice at slice-021+. This is a **contingent inapplicability**, not an architectural impossibility — a hypothetical future codification-AND-bug-fix slice (codifying a new methodology rule while ALSO fixing a runtime defect) would self-apply BFRD-1 trivially via mode (a) or mode (b) detection.

Comparison to prior codifications:
- Slice-015 SCPD-1 / slice-017 TPHD-1 / slice-019 LAYER-EVID-1 all self-applied at codification time (the rule applied to the codification slice's own artifacts).
- BFRD-1 only applies to slices whose mission brief describes a bug fix; slice-020 doesn't qualify because its mission brief describes a methodology codification.

This contingent inapplicability is documented in the mission-brief Must-not-defer + design.md Audit 7 explicitly, mirroring the slice-019 ADR-017 R-3 broader-class-concern + escalation-criteria pattern (acknowledge limitation; specify when the limitation might matter).

Recursive-self-application: slice-020 IS a cross-cutting tooling slice modifying `skills/slice/SKILL.md` + `methodology-changelog.md` — exactly the in-house methodology surfaces MCT-1 (slice-010 ADR-009) covers. `critic-required: true` set at /slice time per MCT-1 default trigger N=9 → N=10 stable. Under the TPHD-1 heuristic this slice's predecessor codified, slice-020's own design + mission-brief + ADR-018 are expected to exhibit recursive-self-application defects at /critique. Per slice-019 lesson "codification slices that codify a discipline almost always commit instances of that discipline on their own draft. Strong prior. Recursive-self-application N=10 → N=11 cumulative post-RSAD-1 codification." Slice-020 first-Critic ratchet: N=11 → N=12 (3 Blockers + 5 Majors + 6 Minors = 14 first-Critic findings at /critique, all VALIDATED post-disposition — see critique.md). The recursive-self-application discipline at slice-020 applies to RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 / TPHD-1 / LAYER-EVID-1 sibling rules on slice-020 artifacts; BFRD-1 itself is contingently N/A per the inapplicability above, not architecturally exempt.

## Consequences

**Immediate** (slice-020 ship):

- `skills/slice/SKILL.md` gains NEW `### Step 3c: Bug-fix prelude (BFRD-1)` section between L140 (Step 3b close) and L142 (Step 4 header).
- `methodology-changelog.md` v0.34.0 entry appended (in-repo + installed) with BFRD-1 rule reference + 2-detection-mode naming + STOP-and-route behavior + Limitations note + TPHD-1-self-application probe + EPGD-1-self-application N=6 → N=7 confirmation.
- `tests/methodology/test_slice_skill.py` gains 2 prose-pin tests appended in NEW SECTION `# --- Slice-020 / BFRD-1 bug-fix repro prelude pinning ---` (`test_slice_skill_md_bfrd_1_prelude_present` + `test_slice_skill_md_bfrd_1_prelude_location_pinned`).
- `tests/methodology/test_methodology_changelog.py` gains 1 NEW SECTION header `# --- Slice-020 / BFRD-1 entry pinning ---` + 3 entry-pin tests (`_v_0_34_0_bfrd_1_entry_present_in_repo_and_installed` + `_v_0_34_0_bfrd_1_entry_names_both_detection_modes` + `_v_0_34_0_bfrd_1_entry_names_stop_and_route_behavior`) + 1 ADR-pin test (`_adr_018_exists_and_names_bfrd_1_canonical_phrase`).
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.33.0 → 0.34.0 atomically.
- `architecture/shippability.md` row 20 added enumerating BFRD-1 critical-path tests; rows 1-19 NOT touched (no Dim 9 sub-clause supersession this slice; SCPD-1 stays at N=3 stable; `_lists_nine_sub_clauses` if such a test exists on Dim 9 enumeration stays valid).
- `agents/critique.md` NOT touched (CAD-1 byte-equality preserved at slice-019 ship hash `f34c967eaaa34413...`; bidirectional sha256 forensic capture N=15 → N=16 stable expected).

**Downstream** (slice-021 and beyond):

- Every `/slice` invocation with a `fix-*`-named candidate OR an explicit bug-fix-source signal automatically triggers Step 3c STOP-and-route per BFRD-1 prose (read by Claude main thread at /slice time).
- The first prospective bug-fix slice at slice-021+ becomes the canonical reference instance #1 of BFRD-1 self-application. Reflection.md SHOULD record the BFRD-1 trigger as a load-bearing prelude (analogous to slice-018's "TPHD-1 self-application empirically demonstrated at /critique fix-prose").
- The "Tests-first for bug fixes" rule in CLAUDE.md becomes structurally enforced at `/slice` runtime (was: cultural rule with no runtime check; now: skill-prose discipline with prose-pin tests).
- Drift detection at v1: prose-pin tests (substring + location-pin = 2 tests on `test_slice_skill.py` + 4 entry-pin/ADR-pin on `test_methodology_changelog.py`) catch SKILL.md drift; v2 candidate `tools/bfrd_1_audit.py` (programmatic mission-brief scan for bug-fix name + failing-test reference) deferred at codification time; promote at N≥3 violations post-codification.

**Cumulative-Critic-influence note**: BFRD-1 is applied prospectively — slice-021 onward (the FIRST slice candidate to exercise the rule). Slice-020 is the codification reference but does not self-apply (per architectural impossibility above). The Critic-stack discipline at slice-020 is the TPHD-1 + RSAD-1 + EPGD-1 + SCPD-1 + RPCD-1 + LAYER-EVID-1 sibling-rule cluster applied to slice-020's own draft — N=6 sibling rules each running their own self-application probe on slice-020 artifacts at /critique time.

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 ADR-008 + slice-010 ADR-009 + slice-013 ADR-012 + slice-014 ADR-013 + slice-015 ADR-014 + slice-016 ADR-015 + slice-017 ADR-016 + slice-019 ADR-017 cheap-with-magnitude-justification convention N=8 → N=9 stable).

**Magnitude estimate** (~11 sites total per /critique B3 ACCEPTED-FIXED recount — prior "~8-10" claim was internally inconsistent with the 11-item enumeration that followed; corrected here to match the empirical count; ratchets the Wiegers regression-guard coverage-symmetry watch-list class to N=4 cumulative across slices 016/017/019/020 — promotion-eligible for Dim 9 sub-clause refinement at next codification slice if recurs at slice-021+):
1. `skills/slice/SKILL.md` — Step 3c section insert (1 site, ~25-30 lines)
2. `~/.claude/skills/slice/SKILL.md` — forward-sync mirror (1 site)
3. `methodology-changelog.md` — v0.34.0 entry insert at file top (1 site, ~50-70 lines)
4. `~/.claude/methodology-changelog.md` — forward-sync mirror (1 site)
5. `VERSION` — bump 0.33.0 → 0.34.0 (1 site)
6. `~/.claude/ai-sdlc-VERSION` — forward-sync mirror (1 site)
7. `plugin.yaml.version` — bump 0.33.0 → 0.34.0 (1 site)
8. `tests/methodology/test_slice_skill.py` — append 2 prose-pin tests + NEW SECTION header (1 site, ~30-40 lines)
9. `tests/methodology/test_methodology_changelog.py` — append NEW SECTION header + 3 entry-pin tests + 1 ADR-pin test (1 site, ~30-40 lines)
10. `architecture/shippability.md` — append row 20 (1 site, multi-line pytest command)
11. `architecture/decisions/ADR-018-*.md` — this file itself (1 site, ~250-300 lines)

**Comparison to prior ADRs**:
- ADR-009 (MCT-1, slice-010) — **cheap** with magnitude justification. ~11-13 sites. Skill-prose-discipline at 1 surface (skills/slice/SKILL.md Step 4a). BFRD-1 closest sibling in pattern (also 1-surface skill-prose at /slice).
- ADR-010 (RSAD-1, slice-011) — **cheap** with magnitude justification. ~12 sites. Skill-prose-discipline at 1 surface (agents/critique.md Dim 9 sub-clause).
- ADR-012 (EPGD-1, slice-013) — **cheap** with magnitude justification. ~12 sites.
- ADR-014 (SCPD-1, slice-015) — **cheap** with magnitude justification. ~13-15 sites.
- ADR-015 (RPCD-1, slice-016) — **cheap** with magnitude justification. ~13-15 sites.
- ADR-016 (TPHD-1, slice-017) — **cheap** with magnitude justification. ~13-16 sites at 3-surface skill-prose insertion.
- ADR-017 (LAYER-EVID-1, slice-019) — **cheap** with magnitude justification. ~12-14 sites at /diagnose runtime discipline with mini-CAD for /diagnose.
- **ADR-018 (this) — cheap with magnitude justification**. ~11 sites (per /critique B3 ACCEPTED-FIXED recount); slimmer than prior /critique-time and /diagnose-time codifications because BFRD-1 is 1-surface skill-prose with no new test files (extends existing `test_slice_skill.py` + `test_methodology_changelog.py`) and no `agents/critique.md` edit.

**Revert path**:
1. Git diff revert of slice-020's commits (single-slice revert clean).
2. Append a superseding methodology-changelog entry retracting BFRD-1 (e.g., `## v0.35.0 — <date>` with `### Retired` section naming BFRD-1 + retirement rationale).
3. Remove the 6 new test functions (2 prose-pin + 3 entry-pin + 1 ADR-pin) from `test_slice_skill.py` + `test_methodology_changelog.py`.
4. Forward-sync the reverted `methodology-changelog.md` to `~/.claude/`. Confirm byte-equality.
5. Forward-sync the reverted `skills/slice/SKILL.md` to `~/.claude/`. Confirm byte-equality.
6. Atomic version bump (post-retirement bump 0.34.0 → 0.35.0 or whatever VERSION ends up at).

**Irreversible portion** (minor, append-only):
- The `methodology-changelog.md` v0.34.0 entry itself becomes part of the append-only changelog history. Retraction is a SUPERSEDING entry per slice-007/008/009/010/011/012/013/014/015/016/017/019 PMI-1 + changelog inclusion heuristic precedent, NOT a deletion.
- Cumulative slice-021-N bug-fix slices that took the BFRD-1 STOP-route are part of the project's empirical record.

Both irreversible portions are documentation-record-class (not functional-behavior-class). Neither prevents revert.

**Conclusion**: Reversibility is **cheap**. Magnitude is ~11 sites per /critique B3 ACCEPTED-FIXED recount + /critique-review M-add-1 ACCEPTED-FIXED propagation (slimmer count than ADR-014/015/016 codification slices at ~13-15 sites + ADR-017 at ~12-14 sites because BFRD-1 spans 1 skill file vs 3 for TPHD-1 / pass-template-prose for LAYER-EVID-1; per /critique-review M-add-3 ACCEPTED-FIXED — "slimmer count" not "slimmer class"). Revert path is well-trodden. Adopt Option 1 (1-surface skill-prose discipline at `/slice` Step 3c).
