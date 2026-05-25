---
id: ADR-009
title: Promote voluntary-Critic-on-cross-cutting-tooling to /slice Step 4a default mandatory-Critic trigger via In-house methodology surfaces bullet + evidence prose paragraph (MCT-1)
date: 2026-05-12
slice: slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-009: Promote voluntary-Critic-on-cross-cutting-tooling to /slice Step 4a default mandatory-Critic trigger (MCT-1)

**Note on rule-ID naming** (per Critic B5): the rule was originally drafted as "MCR-1 Mandatory Critic Rule" but renamed to **MCT-1 Mandatory Critic Trigger** during /critique to signal /slice-time prose-heuristic semantics distinct from the audit-enforced gate semantics of sibling rules (BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 each have a corresponding `tools/*_audit.py`; MCT-1 does not — the rule lives in `skills/slice/SKILL.md` Step 4a prose only). v2 candidate at slice-N+ if drift surfaces: build `tools/mct_1_audit.py` walking `architecture/slices/*/milestone.md` + `mission-brief.md` and asserting `critic-required: true` when slice scope references in-house methodology files. Deferred at slice-010 to stay within the ~0.5-day budget.

## Context

The `/slice` skill's Step 4a "Pick the risk tier" section enumerates a list of "Always mandatory Critic" triggers — slice characteristics that force `critic-required: true` regardless of the picked risk tier:

```
- Auth / authz / permissions / login / tokens
- New API contracts or endpoint shapes
- Data model changes / migrations / schema
- Multi-device / multi-user / sync / sharing
- External integrations (OAuth, payment gateways, third-party APIs)
- Security-sensitive paths
- Heavy mode (always)
```

All seven existing triggers cover **user-facing concerns** (auth, contracts, data, sync, integrations, security) plus a mode-meta closer. None cover **in-house methodology surfaces** — slices that modify the pipeline's own machinery: skill prose under `skills/*/SKILL.md`, agent prompts under `agents/*.md`, custom build / lint / audit tooling under `tools/**/*.py`, or methodology rules in `methodology-changelog.md`. These slices are *cross-cutting tooling slices* — they don't ship user-visible features, but they ship the discipline that governs every future slice.

Across slices 1-9, a strong empirical pattern accumulated in the reflection record:

**Voluntary-Critic-on-cross-cutting-tooling-slices is N=9/9 paid off** (cumulative-post-build framing per Critic B1 honest reading — every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; this is the verifiable interpretation supported by every slice 1-9 reflection's `## Critic calibration` section):

- slice-001 (diagnose orchestration fix) — 12 voluntary Critic findings ALL dispositioned ACCEPTED-PENDING and validated post-build (fixes applied at /build-slice, not at /critique-disposition). Critic effective for post-build catch; did NOT directly modify mission-brief/design.md at /critique time.
- slice-002 (diagnose contract relaxation + RR-1 migration) — Critic M1+M2+M3+M4 + m1-m4 dispositioned at /critique (mix of ACCEPTED-FIXED + ACCEPTED-PENDING). Surfaced cwd-mismatch causal-attribution caveat + prose-pin fragility (R-2 created) + 12-site canonical-contract drift target list. Post-build validated.
- slice-003 (VAL-1 imports allowlist) — Critic m1 ACCEPTED-FIXED at /critique-disposition (canonical-prose pin gap at SKILL.md Step 5b). First slice contributing a /critique-disposition catch to the project's running counter.
- slice-004 (RR-1 docstring-or-regex) — Critic B1 ACCEPTED-FIXED at /critique-disposition (3-surface alignment requirement).
- slice-005 (BC-1 keyword precision) — Critic B2 ACCEPTED-FIXED at /critique-disposition (algorithm-path-conformance lesson: BC-GLOBAL-1 always-true short-circuit interaction); 2 additional build-time DEVIATIONs surfaced and were fixed at mid-slice smoke.
- slice-006 (9th Critic dimension CCC-1) — Critic B1 ACCEPTED-FIXED at /critique-disposition (in-repo prose-parity drift fatal save); 11/11 findings VALIDATED post-build; 2 additional build-time DEVIATIONs (INST-1 inventory drift sub-class).
- slice-007 (CAD-1 hybrid) — Critic B1 + B2 ACCEPTED-FIXED at /critique-disposition (in-repo VERSION install-time rename + PMI-1 gate closure — two fatal saves); 8/8 VALIDATED.
- slice-008 (BC-1 v1.2 negative-anchors) — Critic M1+M2+M3 ACCEPTED-FIXED at /critique-disposition (pre-empted what would have been DEVIATIONs); ZERO build-time DEVIATIONs (first in series); 6/6 VALIDATED.
- slice-009 (CCC-1 v1.1 design-doc-level surface) — Critic B1+B2 + M1-M5 + m1-m4 dispositioned at /critique (mix of ACCEPTED-FIXED + ACCEPTED-PENDING); 11/11 VALIDATED; 2 additional build-time DEVIATIONs caught at mid-slice smoke (DEVIATION-1 lowercase-at-sentence-start case-sensitivity + DEVIATION-2 `.find()`-collision in location-pin test); recursive-self-application phenomenon (M2: slice-009 caught its own draft committing the design-doc-vs-canonical-inventory drift it was encoding).

**Honest aggregate framing** (per Critic B1 + B3 corrections):
- **N=9/9 voluntary Critic invocations produced VALIDATED findings post-build** (no FALSE-ALARMs across slices 1-9). This is the verifiable cumulative-post-build framing.
- Per-slice "design-stage catch" counter (slices that had ≥1 ACCEPTED-FIXED Critic finding at /critique-disposition modifying mission-brief or design.md before build): slices 003-009 = 7 slices contributed; slices 001-002 had Critic findings but were primarily ACCEPTED-PENDING dispositions or non-design-modifying. The earlier-drafted "8 of 9 design-stage catches" framing was internally inconsistent with the project's running counter across slice-007 (off-by-one re-cast) and slice-008→slice-009 (counting-rule change); dropped from the canonical bullet body per Critic B1.
- 36/36 Critic findings VALIDATED at /critique-disposition across slices 6-9 (every triaged finding ratified by user; zero FALSE-ALARMs at /critique-disposition; strongest streak in the project).
- Dim 9 (CCC-1) catch rate trajectory: 0% (slices 1-5, pre-CCC-1) → 25% (slice-006) → 60% (slice-007) → 100% (slice-008) → 60% (slice-009); range-bound 60-100% on N=4 evidence; NOT monotonic (slice-008's strict-improvement claim falsified at slice-009).

Slice-008 + slice-009 reflections explicitly recommend promoting this pattern at slice-010+:
- slice-008 reflection: "/slice's default heuristic SHOULD be updated at slice-N+ to set `critic-required: true` when scope includes 'modifies in-house audit / agent prompt / methodology rule' — empirical case strongest in the project at N=8/8."
- slice-009 reflection: "Voluntary Critic on cross-cutting tooling slices is N=9/9 paid off — should promote to /slice default heuristic at slice-010+ (~30 min skill-prose update). Strongest evidence base in the project."

Without the promotion, every future cross-cutting tooling slice (modifying skill prose / agent prompts / in-house tooling / methodology rules) relies on per-slice voluntary opt-in to set `critic-required: true`. The N=9/9 evidence base makes that voluntary call effectively a discipline already, but it lacks the codification needed to make it automatic at /slice-invocation time. Codifying it eliminates the per-slice judgment call.

## Options considered

### Option 1 — Append a terse bullet + adjacent evidence prose paragraph (CHOSEN, refined per Critic M1)

Insert a terse new bullet between the `Security-sensitive paths` bullet and the `Heavy mode (always)` bullet (content-trigger bullets grouped before the mode-meta closer; line numbers cited as-of-2026-05-12 in design.md L155-174 once, symbolic references thereafter per Critic m1):

```
- In-house methodology surfaces (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`)
```

Bullet matches the existing 7 bullets' style (single-line, single-clause; no embedded justification clause; mirrors `External integrations (OAuth, payment gateways, third-party APIs)` shape).

Append an evidence prose paragraph AFTER the existing "When producing the mission brief..." paragraph (preserved bit-for-bit) at the end of the Step 4a section. Markdown blockquote keeps it visually distinct from the bullet list and the regular prose:

```
> **Evidence for the In-house methodology surfaces trigger**: voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 in this project's reflection record (e.g., slice-006 INST-1 inventory drift; slice-007 install-time rename; slice-008 negative-anchor uniformity; slice-009 recursive self-application). Every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; see `architecture/slices/_index.md` "Aggregated lessons" and `archive/slice-NNN/reflection.md` "Critic calibration" sections for per-slice disposition records.
```

**Pros**:
- Bullet stays stylistically uniform with the existing 7 bullets (resolves Critic M1's "stylistic asymmetry" concern — the original draft had a 5-line multi-clause bullet that diverged ~3x in length and ~5x in syntactic complexity from existing list members).
- Evidence prose can refine without bullet drift; future re-readings of the bullet list see consistent terse style.
- Preserves the existing 7 bullets + "When producing..." paragraph bit-for-bit. Pure additive change.
- Codifies the heuristic in the same physical location every /slice invocation already consults at Step 4a — zero discoverability cost. The blockquote `>` styling signals "supporting context" without competing with the action-imperative bullet list.
- Reversibility: cheap. Revert path is a single git diff revert + a superseding methodology-changelog entry retracting MCT-1.
- Test scaffolding fits slice-007 + slice-009 prose-pin convention (substring tests + location-pin per Critic M1 + bidirectional changelog-pin per Critic M3 + per Critic M3 ACCEPTED-PENDING sub-class anchor pin at /build-slice).
- Canonical-literal pins target both surfaces: bullet substrings (`In-house methodology surfaces`, file-class anchor) AND evidence-paragraph substrings (`N=9/9`, `voluntary Critic`, ≥2 cross-slice anchors, ≥2 sub-class anchors per /build-slice).

**Cons**:
- Step 4a section gains BOTH a new bullet AND a new evidence paragraph (vs single bullet) — two insertion sites; slightly more surface area. Mitigated: the additions are spatially adjacent (bullet → existing paragraph → evidence paragraph) so future readers consume them as one block.
- Future cross-cutting trigger candidates (e.g., "modifies pre-commit hooks", "modifies shippability catalog convention") would each require their own bullet additions plus matching evidence paragraphs, potentially making the section grow. Mitigated by promotion-threshold discipline (N≥3 each before promotion); section bounded by actual count of distinct empirical trigger classes, not speculative ones.

### Option 2 — Restructure Step 4a into two sub-lists (user-facing concerns vs in-house tooling concerns)

Reorganize the existing 7 bullets + the new bullet into two H4 sub-headings:

```
**Always mandatory Critic** — user-facing concerns:
- Auth / authz / ...
- New API contracts ...
- Data model changes ...
- Multi-device sync ...
- External integrations ...
- Security-sensitive paths

**Always mandatory Critic** — in-house methodology concerns:
- In-house methodology surfaces (skill prose, agent prompts, tooling, methodology rules)

(Plus: Heavy mode (always) — regardless of category.)
```

**Pros**: signposts the two distinct semantic groups; future cross-cutting trigger bullets get a natural home.

**Cons**: restructure tax — modifies the existing bullets' position (changes line numbers, invalidates any external references to line numbers of existing bullets), adds two H4 sub-headings + a "regardless of category" qualifier. ~15-20 lines of churn vs Option 1's ~5 lines. The single new trigger doesn't justify the restructure; restructure makes sense at N≥2 in-house trigger bullets. **Rejected**: revisit at N≥2 in-house trigger candidates.

### Option 3 — Add a separate Step 4b "Always mandatory Critic for in-house methodology surfaces"

Introduce a parallel Step 4b paragraph distinct from Step 4a:

```
### Step 4b: In-house methodology surfaces force mandatory Critic

(Mirrors Step 4a but specifically for cross-cutting tooling slices...)
```

**Pros**: visually separates the new heuristic from the existing list; emphasizes the new rule's empirical evidence base.

**Cons**: duplicates the section heading "Always mandatory Critic"; same content as Option 1 with more friction; Claude main thread at /slice invocation already reads Step 4a — adding a parallel Step 4b doubles the prose surface. **Rejected**: same effect as Option 1 with more surface area.

## Decision

**Adopt Option 1 (refined per Critic M1)** — append a terse new bullet to the existing `skills/slice/SKILL.md` Step 4a "Always mandatory Critic" list between the existing `Security-sensitive paths` bullet and the existing `Heavy mode (always)` bullet, AND append an evidence prose paragraph AFTER the existing "When producing the mission brief..." paragraph at the end of the Step 4a section. Both additions are pure-additive (preserve existing prose bit-for-bit). Canonical body documented under "What's new" in [[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic/design.md]]. Codify as new methodology rule **MCT-1** in `methodology-changelog.md` v0.25.0 under `### Added` with explicit Limitations note per Critic B5 (acknowledging /slice-time prose-heuristic semantics; no audit-enforced gate; v2 candidate if drift surfaces). PMI-1 atomic version bump 0.24.0 → 0.25.0 with versioned-gate supersession (slice-009's `_at_0_24_0` → slice-010's `_at_0_25_0`; N=3 supersession event post-completion).

The bullet + evidence paragraph pin canonical literals via the same N-substring + N-surface schema-pin discipline established at slice-008 + slice-009 (with the M1-split refinement):
- AC #1 canonical literals split across bullet + evidence paragraph: `In-house methodology surfaces` + file-class anchor (`skills/*/SKILL.md` etc.) — both in the bullet body; `N=9/9` + `voluntary Critic` (case-sensitive lowercase-v) — both in the evidence paragraph.
- AC #2 cross-slice example anchors: at least two of `slice-006`, `slice-007`, `slice-008`, `slice-009` in the evidence paragraph.
- Per Critic M3 ACCEPTED-PENDING (TF-1 row added at /build-slice): at least two of sub-class anchors {`INST-1 inventory drift`, `install-time rename`, `negative-anchor uniformity`, `recursive self-application`} in the evidence paragraph — closes the drift vector that would otherwise let the descriptive sub-class text drift unpinned.
- 1 substantive canonical phrase pinned across N=3 surfaces: `In-house methodology surfaces` appears in skills/slice/SKILL.md (bullet) + in-repo methodology-changelog.md (v0.25.0 entry body) + installed methodology-changelog.md (forward-sync mirror).
- 1 location-pin (slice-009 Critic M1 lesson; widened scope per M1 split): scoped `text.find("### Step 5:", text.find("Always mandatory Critic"))` to capture both the bullet list AND the evidence paragraph below it (widened end anchor from `Heavy mode (always)` to `### Step 5:` per Critic M1 split). The bullet position-pin uses the tighter sub-anchors `Security-sensitive paths` / `Heavy mode (always)` to ensure the new bullet falls precisely between them. Anchor uniqueness empirically verified pre-AC-lock: all three substrings (`Always mandatory Critic`, `Security-sensitive paths`, `Heavy mode (always)`) appear exactly once in `skills/slice/SKILL.md`; `### Step 5:` is a markdown H3 header (also unique) — pre-emption of slice-009 DEVIATION-2 `.find()`-collision class.

Recursive-self-application: slice-010 IS a cross-cutting tooling slice modifying `skills/slice/SKILL.md` — exactly the in-house methodology surface MCT-1 covers. Under both the OLD heuristic (voluntary Critic on cross-cutting tooling at N=9/9) AND the NEW heuristic this slice encodes, slice-010 qualifies for `critic-required: true`. The Critic at /critique SHOULD be expected to find rule-class violations in slice-010's own draft prose (recursive-self-application phenomenon per slice-009 M2; N=1 at slice-009, slice-010 ratchets to N=2 candidate post-completion). **EMPIRICALLY OBSERVED at slice-010's /critique step**: the Critic surfaced 5 blockers + 3 majors + 3 minors — most addressing rule-class violations in slice-010's own draft (B1 internal inconsistency in N=9/9 framing; B3 ADR enumeration drift; M1 bullet-style asymmetry; B5 rule-naming-convention break — all addressed via this ADR revision). The recursive self-application discipline ratchets to N=2 with strong evidence — promote `recursive-self-application-discipline` to actionable /critique-skill prose at N=3 if a third instance surfaces at slice-011+.

## Consequences

**Immediate** (slice-010 ship):
- `skills/slice/SKILL.md` Step 4a list grows 7 → 8 bullets + adjacent evidence prose paragraph appended after the existing "When producing the mission brief..." paragraph (per Critic M1 split).
- `~/.claude/skills/slice/SKILL.md` byte-equal post-forward-sync.
- `methodology-changelog.md` v0.25.0 entry appended (in-repo + installed) with MCT-1 rule reference + explicit Limitations note per Critic B5.
- `tests/methodology/test_slice_skill.py` NEW with 4 prose-pin tests + 1 sub-class anchor pin per Critic M3 ACCEPTED-PENDING (5 total).
- `tests/methodology/test_slice_skill_drift.py` NEW with 1 mini-CAD-1 byte-equality test.
- `tests/methodology/test_methodology_changelog.py` gains 1 bidirectional changelog-pin test (`test_v_0_25_0_mct_1_entry_present_in_repo_and_installed`) + 1 PMI-1 versioned-gate test (`_at_0_25_0` supersedes slice-009's `_at_0_24_0`).
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.25.0.
- `architecture/shippability.md` row 10 added; row 9 header updated.

**Downstream** (slice-011 and beyond):
- Every /slice invocation that touches in-house methodology surfaces (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`) automatically gets `critic-required: true` set at mission-brief / milestone.md creation time **via the Claude main thread reading Step 4a's bullet at /slice invocation** (NOT via automated audit — per Critic B5 the rule has no `tools/mct_1_audit.py` enforcing it; v2 candidate at slice-N+ if drift surfaces). The voluntary-call friction at /slice is eliminated for human/Claude judgment, but drift detection relies on slice-N+ reflection-record auditing rather than a programmatic gate.
- /critique runs for these slices regardless of risk-tier picked. Cross-cutting Critic catch trajectory (60-100% range-bound at slice-006..009) projected to remain ≥60% going forward, with potential improvement as the Critic prompt itself accumulates more refinements (e.g., slice-009 carryover candidates `case-sensitivity-canonical-literal-pin-discipline` at N=2 promotion + `substring-search-location-pin-anchor-uniqueness-discipline` at N=2 promotion — both pre-empted at slice-010 design time but not yet codified into the Critic agent prompt).
- The N=9/9 evidence base is no longer "aggregated-lesson recommendation"; it's codified into the pipeline's default behavior. Per slice-009 reflection's effectiveness-target framing (≤2 cross-cutting misses across slices 6-15; currently at 8 misses through slice-009), MCT-1 is one of two candidate responses (the other is `/critic-calibrate` recalibrating the quantitative target). /critic-calibrate at slice-012-015 boundary will assess whether MCT-1 alone has moved the catch rate sufficiently, or whether further Critic-prompt refinements are needed.

**Cumulative-Critic-influence note**: MCT-1 is applied prospectively — slice-011 onward. Past slices (slice-001..009) retain their original `critic-required` settings (voluntary, where set). The methodology-changelog entry documents this as the new default at slice-010+; no retroactive re-evaluation of past slices.

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 Critic M4 + ADR-008 precedent; corrected per slice-010 Critic m3):

**Magnitude estimate** (~11-13 sites total):
1. `skills/slice/SKILL.md` — bullet insert (1 site)
2. `skills/slice/SKILL.md` — evidence prose paragraph insert (1 site; M1 split)
3. `~/.claude/skills/slice/SKILL.md` — forward-sync mirror (1 site)
4. `methodology-changelog.md` — v0.25.0 entry (1 site, ~30 lines)
5. `~/.claude/methodology-changelog.md` — forward-sync mirror (1 site)
6. `VERSION` — bump 0.24.0 → 0.25.0 (1 site)
7. `~/.claude/ai-sdlc-VERSION` — forward-sync mirror (1 site)
8. `plugin.yaml.version` — bump 0.24.0 → 0.25.0 (1 site)
9. `tests/methodology/test_slice_skill.py` — NEW file (5 functions per ACCEPTED-PENDING M3 + 4 ACs)
10. `tests/methodology/test_slice_skill_drift.py` — NEW file (1 mini-CAD-1 function)
11. `tests/methodology/test_methodology_changelog.py` — add `_v_0_25_0_mct_1_entry` + replace `_at_0_24_0` with `_at_0_25_0` (2 sub-edits in 1 file)
12. `architecture/shippability.md` — add row 10 + update row 9 header (2 sub-edits in 1 file)
13. `architecture/decisions/ADR-009-*.md` — this file itself

**Comparison to prior ADRs**:
- ADR-005 (CCC-1 v1, slice-006) — **expensive** with irreversible portion. Added entire 9th Critic dimension + 7 prose-parity sites + Kiczales citation; surface area ~30+ sites.
- ADR-006 (CAD-1, slice-007) — **cheap** with 5 enumerated irreversibles. Added per-file byte-equality audit + 2 SKILL.md prose updates; surface area ~5-10 sites.
- ADR-007 (BC-1 v1.2, slice-008) — **cheap**. Added negative-anchor mechanism + 9-token migration; surface area ~10-15 sites.
- ADR-008 (CCC-1 v1.1, slice-009) — **cheap** with magnitude justification. ~5-sentence refinement of one Dim 9 sub-clause body; surface area ~5 sites.
- **ADR-009 (this) — cheap with magnitude justification**. ~11-13 sites; closer in magnitude to **ADR-007 (~10-15 sites)** than to ADR-008's ~5 sites. The bullet+evidence-paragraph split (Critic M1) + 2 new test files + shippability+changelog updates put slice-010 in the BC-1 v1.2 magnitude class, not the inline-refinement class. Still cheap on reversibility because each site is small and the revert path is git-diff-revert + superseding changelog entry.

**Revert path**:
1. Git diff revert of slice-010's commits (single-slice revert is clean since no in-flight cross-slice dependencies exist).
2. Append a superseding methodology-changelog entry retracting MCT-1 (e.g., `## v0.26.0 — <date>` with `### Retired` section naming MCT-1 + rationale for retirement). Per PMI-1 + changelog inclusion heuristic: "If a slice acceptable yesterday would be refused today (or vice versa), it's a changelog entry."
3. Remove the 5 new test functions + delete the 2 new test files. Reinstate `_at_0_24_0` PMI-1 versioned-gate (or supersede to whatever VERSION ends up at).
4. Forward-sync the reverted `skills/slice/SKILL.md` + `methodology-changelog.md` to `~/.claude/`. Confirm byte-equality.

**Irreversible portion** (minor, append-only):
- The `methodology-changelog.md` v0.25.0 entry itself, once committed, becomes part of the append-only changelog history. A retraction is a SUPERSEDING entry (per PMI-1 + slice-007/008/009 precedent), NOT a deletion of the v0.25.0 entry. Reading the file historically will always show "MCT-1 was added at slice-010 and retired at slice-N".
- Cumulative slice-010-N Critic invocations that ran (and the artifacts they produced) under MCT-1's mandatory-Critic gate are part of the project's empirical record. Future /critic-calibrate runs may reference them. The Critic invocations themselves can't be un-invoked.

Both irreversible portions are documentation-record-class (not functional-behavior-class). Neither prevents revert; they only mean the project's history would record MCT-1 as having existed.

**Conclusion**: Reversibility is **cheap**. Magnitude is ~11-13 sites (same class as ADR-007; larger than ADR-008's inline-refinement). Revert path is well-trodden (single-slice git diff revert + superseding changelog entry). Adopt Option 1 (refined per Critic M1 split).
