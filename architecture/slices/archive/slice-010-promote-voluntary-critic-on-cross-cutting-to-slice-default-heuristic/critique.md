# Critique: Slice 010 promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic

**Critic reviewed**: mission-brief.md, design.md, ADR-009 (plus skills/slice/SKILL.md, methodology-changelog.md v0.24.0, build-checks.md, BC-1 audit, prior slice reflections + critique.md files for slices 1-9, install_audit.py, shippability.md)
**Date**: 2026-05-12
**Result**: NEEDS-FIXES (pre-triage); will move to CLEAN once user ratifies dispositions

## Summary

The Option-1 promotion decision is structurally sound, the recursive-self-application discipline is honestly acknowledged, anchor uniqueness + canonical-literal absence were empirically pre-verified at design time, and the ~5-line surface area + PMI-1 supersession framing are correct. **However, the load-bearing N=9/9 + "8 of 9 design-stage catches" claim — pinned into BOTH the SKILL.md bullet body (forever) AND the v0.25.0 changelog entry (append-only) — does not survive contact with the project's own reflection record.** Slice-008's reflection said "8 of 8 catching design-stage failures" (slices 1-8); slice-009's reflection said "8 of 9 design-stage catches" — implying slice-009 contributed ZERO net design-stage catches (which is false — slice-009 caught 3 at /critique). The accounting is internally inconsistent across slices 1-9 and slice-010 was about to canonize the mess into permanent prose. Plus: AC #3's TF-1 PENDING → WRITTEN-FAILING transition is non-genuine at Phase 1b (test PASSES at first write because both files start byte-equal); the BC-1 self-application prediction is structurally trivial (positive anchors don't fire at all, negative anchors don't get a chance to silence); MCR-1 the rule name conflates "audit-enforced gate" semantics (BC-1/PMI-1/CAD-1) with "/slice-time heuristic" semantics (no audit enforces this). Five blockers, three majors, three minors.

**Recursive-self-application observation (slice-009 M2 phenomenon, N=2 candidate)**: as predicted, the Critic at /critique surfaced rule-class violations in slice-010's own draft prose. The slice authoring "voluntary Critic on cross-cutting tooling pays off" was Critic'd and found to have an unverified load-bearing claim (N=9/9 = B1), a stylistic asymmetry the design hand-waved (M1), and a rule-naming convention break (B5). Strongest evidence yet for the recursive-self-application discipline.

## Findings

### Blockers (must address before /build-slice)

#### B1: The "8 of 9 design-stage catches" claim is mathematically inconsistent with the project's own reflection history — pinning it as canonical prose forever canonizes the inconsistency

- **Claim under review**: mission-brief.md / design.md / ADR-009 / proposed SKILL.md bullet body — all assert verbatim "N=9/9 voluntary Critic catch payoff … 8 of 9 design-stage catches".
- **Issue**: The arithmetic does not survive cross-reflection audit. Three different counting rules co-exist in the project's record:
  1. **"Catch contributions"** (counts B/M findings dispositioned at /critique): slice-003 = 1, …, slice-009 = 3 → cumulative ≈ 12+ across slices 3-9, NOT 8
  2. **"Slices that contributed ≥1 design-stage catch"**: slices 3, 4, 5, 6, 7, 8 = 6 of 8 (slices 1+2 = 0); slice-009 = 1 → 7 of 9
  3. **"Slices whose 100%-design-stage catch rate held (no build-time miss)"**: slices 1-4 = 4 (debatable), slice-008 = 1, slice-009 = 0 → ??

  Slice-007 reflection L86 enumeration is off-by-one (claims "5 of 7" but listed 6 catches); slice-008 reflection L88 jumps from "5 of 7" to "8 of 8" without explaining where slices 1+2 went; slice-009 reflection L95 reframes "8 of 8" to "8 of 9" with a counting-rule change. Slice-010 about to canonize "8 of 9 design-stage catches" into SKILL.md prose forever.
- **Evidence**: slice-001 reflection L44-55 (all 12 findings ACCEPTED-PENDING — fixes post-build, not design-stage); slice-002 reflection L36-43; slice-003 reflection L75; slice-004 reflection L66; slice-005 reflection L91; slice-007 reflection L86; slice-008 reflection L88; slice-009 reflection L95.
- **Proposed fix**: Pick **Option A (cleanest)** — drop the design-stage-catch sub-claim entirely. Pin only "N=9/9 voluntary Critic catch payoff across slices 1-9" with honest cumulative-post-build framing: every voluntary Critic invocation produced VALIDATED findings post-build with zero FALSE-ALARMs. This is verifiable per slice-N reflections.
- **Builder draft**: **ACCEPTED-FIXED** — applied Option A. Dropped "8 of 9 design-stage catches" sub-claim from mission-brief Intent + risk-retired framing + design.md What's-new + design.md risk-tier rationale + ADR-009 Context section + proposed SKILL.md bullet body / evidence paragraph. Replaced with "N=9/9 voluntary Critic catch payoff" + cumulative-post-build framing ("every voluntary Critic invocation produced VALIDATED findings post-build with zero FALSE-ALARMs"). Fix references: mission-brief Risk-retired prose; design.md Risk-tier (b); ADR-009 Context's "Honest aggregate framing" subsection (rewritten).

#### B2: AC #3 mini-CAD-1 test TF-1 status PENDING is mis-classified — the test PASSES at first write (Phase 1b), not WRITTEN-FAILING

- **Claim under review**: mission-brief.md TF-1 row 3 (`PENDING`) + Notes L49 ("AC #3 fails pre-fix with sha256 mismatch") + design.md Phase plan L184 ("PASSING pre-edit") — contradictory.
- **Issue**: Per slice-009 mission-brief L33 precedent (`test_in_repo_and_installed_critique_agent_are_content_equal | PASSING |`), the correct TF-1 status for a byte-equality test against already-byte-equal files at slice start is **PASSING**, not PENDING. The "WRITTEN-FAILING" moment for AC #3 is Phase 2 (in-repo edited; installed not yet synced) observed at Phase 2b mid-slice smoke gate, NOT Phase 1b (test creation).
- **Evidence**: mission-brief.md TF-1 row 3 + design.md Phase plan L184 contradiction. slice-009 mission-brief L33 precedent.
- **Proposed fix**: Option A — change AC #3 TF-1 row status from `PENDING` to `PASSING`; update mission-brief Notes L49 to say "AC #3 transitions PASSING → WRITTEN-FAILING (Phase 2 in-repo edit, observed at Phase 2b mid-slice smoke) → PASSING (Phase 2c post-forward-sync)". Mirrors slice-009 row 3 precedent.
- **Builder draft**: **ACCEPTED-FIXED** — applied Option A. mission-brief.md TF-1 row 3 status changed `PENDING` → `PASSING`; Notes section AC #3 entry rewritten to describe the PASSING → WRITTEN-FAILING (Phase 2b) → PASSING transition; design.md Phase 1 description updated to note 6 of 7 rows transition PENDING → WRITTEN-FAILING (row 3 is the PASSING outlier). AC #3 verification-plan row also updated to reflect transition. Mirrors slice-009 CAD-1 row 3 precedent.

#### B3: ADR-009 enumeration of "voluntary Critic on slices 1-9" misrepresents slice-001 and slice-002 — they had Critic findings but NO design-stage catches; describing them as "Critic surfaced design improvements at /critique" hand-waves the actual disposition

- **Claim under review**: ADR-009 Context bullet list claims slice-001 + slice-002 contributed; running counter in slice-008 reflection starts at slice-003.
- **Issue**: slice-001 dispositions all ACCEPTED-PENDING (post-build fixes); slice-002 mix of ACCEPTED-FIXED + ACCEPTED-PENDING. The "8 of 9 design-stage catches" framing was implying slice-001 + slice-002 contributed which the project's reflection record does NOT support.
- **Evidence**: slice-001 reflection L44-55 (all 12 findings ACCEPTED-PENDING); slice-002 reflection L36-43; slice-008 reflection L88 (running counter starts at slice-003 m1).
- **Proposed fix**: Reframe ADR-009 Context section per-slice enumeration to honestly note slice-001 + slice-002 had VALIDATED findings but ACCEPTED-PENDING dispositions (fixed at build, not design-stage). Drop "8 of 9" framing.
- **Builder draft**: **ACCEPTED-FIXED** — applied. ADR-009 Context section per-slice enumeration rewritten with honest disposition state: slice-001 12 findings ACCEPTED-PENDING + validated post-build; slice-002 mix of ACCEPTED-FIXED + ACCEPTED-PENDING; slices 003-007 named the specific finding ID + disposition state; slice-008 + slice-009 named all triaged finding outcomes. New "Honest aggregate framing" subsection replaces the prior "Aggregated metrics" subsection — pins "N=9/9 voluntary Critic invocations produced VALIDATED findings post-build (no FALSE-ALARMs)" as the verifiable cumulative-post-build framing. Dovetails with B1 fix.

#### B4: BC-1 self-application prediction (design.md "Audit 3") is structurally trivial — BC-PROJ-1 + BC-PROJ-2 don't have positive applicability against slice-010 at all; the "negative-anchor mechanism silences cleanly" framing is misleading

- **Claim under review**: design.md Audit 3 + mission-brief.md Must-not-defer self-application bullet — both claim BC-1 v1.2's negative-anchor mechanism silences BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1.
- **Issue**: Empirical word-boundary count via venv Python on slice-010's actual mission-brief.md + design.md: NONE of BC-PROJ-1's positive trigger anchors (`subagent`, `fan-out`) appear; NONE of BC-PROJ-2's positive anchors (`fence`, `code-block`, `llm`) appear. So neither rule has positive applicability to suppress — negative anchors don't get reached. Only BC-GLOBAL-1 fires via `Applies to: **` glob path; only that rule is genuinely silenced.
- **Evidence**: `tools/build_checks_audit.py` L412-418 `_rule_applies` semantics — positive applicability gated through `not _negative_anchor_match()`; negative filter is final filter on positive decisions. If no positive decision is made, negative filter is never invoked.
- **Proposed fix**: Update Audit 3 prose (design.md + mission-brief.md Must-not-defer) to precisely distinguish BC-GLOBAL-1 (genuinely silenced) from BC-PROJ-1 + BC-PROJ-2 (no positive applicability — never reaches negative filter).
- **Builder draft**: **ACCEPTED-FIXED** — applied. design.md Audit 3 section rewritten with empirical word-boundary counts AND distinction between no-positive-firing (BC-PROJ-1/2) vs negative-anchor-silencing (BC-GLOBAL-1). mission-brief.md Must-not-defer self-application bullet updated with same precise framing. Expected `applicable: []` result framed honestly: no-positive-firing + negative-silencing.

#### B5: MCR-1 rule-class semantics conflate "audit-enforced gate" with "/slice-time prose heuristic" — the convention (BC-1/PMI-1/CAD-1/TF-1) needs a sub-distinction or different ID

- **Claim under review**: mission-brief / design / ADR-009 introduce **MCR-1 Mandatory Critic Rule** alongside audit-enforced siblings BC-1 (`tools/build_checks_audit.py`), PMI-1 (`tools/plugin_manifest_audit.py`), CAD-1 (`tools/critique_agent_drift_audit.py`), TF-1 (`tools/test_first_audit.py`), RR-1 (`tools/risk_register_audit.py`), INST-1 (`tools/install_audit.py`), VAL-1 (Layer B audit), WIRE-1 (wiring audit).
- **Issue**: MCR-1 is enforced by ZERO audit — the heuristic lives only in SKILL.md prose. Naming it under the same rule-ID convention sets a precedent future readers will assume audit-enforcement is universal; calibration-trail damage of the same shape as slice-009 Critic M4 (reversibility-tag inconsistency).
- **Evidence**: `tools/install_audit.py` L44-67 `_CANONICAL_*` tuples (zero MCR-related entries); `methodology-changelog.md` v0.10.0 (BC-1) / v0.13.0 (TF-1) / v0.22.0 (CAD-1) all carry `**Validation**:` field naming the audit module — MCR-1 would not.
- **Proposed fix**: Three options offered (A: rename to MCT-1 / SCT-1 / TRG-1 signaling trigger semantics; B: build the audit; C: keep MCR-1 + add Limitations note). Builder picks **Option A (rename to MCT-1 Mandatory Critic Trigger)** because:
  - -T- signals /slice-time trigger semantics distinct from audit gate
  - Rename is cheapest NOW (slice-010 hasn't committed; changelog entry not yet append-only)
  - Preserves rule-ID convention's clarity for future readers
- **Builder draft**: **ACCEPTED-FIXED** — applied. Global rename MCR-1 → MCT-1 + "Mandatory Critic Rule" → "Mandatory Critic Trigger" across mission-brief.md (AC #4 test name + tooling references + intent prose), design.md (What's-new MCT-1 rule section + methodology-changelog entry plan + test names + decisions section), ADR-009 (title + body + frontmatter title field + Consequences + Reversibility + Cumulative-Critic-influence). Test name: `test_v_0_25_0_mct_1_entry_present_in_repo_and_installed`. ADR-009 prepended with explicit naming-rationale note explaining the -T- distinction. Also applied **Option C complement**: methodology-changelog v0.25.0 entry plan includes explicit Limitations note acknowledging "MCT-1 is /slice-time heuristic prose only, NOT an audit-enforced gate" with v2 candidate framing.

### Majors (address this slice)

#### M1: ADR-009 "Cons" of Option 1 hand-waves the bullet-style asymmetry — the proposed bullet body is qualitatively different from the existing 7 bullets

- **Claim under review**: ADR-009 Cons list "slight stylistic asymmetry"; the proposed bullet body is ~3x length + ~5x syntactic complexity of any existing Step 4a bullet.
- **Issue**: Existing 7 bullets are one-line single-clause; the proposed bullet was 2+ sentences with embedded "Evidence:" prefix, semicolon-separated sub-clauses, inline metrics. "Slight stylistic asymmetry" understated this — the asymmetry carries a semantic signal that other 7 bullets are "self-evident" while this one needs evidence to defend itself.
- **Evidence**: `skills/slice/SKILL.md` L166-172 (existing 7 bullets each ≤1 short line); proposed bullet body was ~5 lines.
- **Proposed fix**: Split bullet into terse form matching existing style + adjacent evidence prose paragraph below the list (after the existing "When producing the mission brief..." paragraph). Canonical-literal pins target both surfaces (bullet substrings + evidence paragraph substrings).
- **Builder draft**: **ACCEPTED-FIXED** — applied. design.md What's-new section restructured to describe TWO additions (terse bullet + evidence prose paragraph appended below "When producing..." paragraph). Proposed bullet body now: `- In-house methodology surfaces (skills/*/SKILL.md, agents/*.md, tools/**/*.py, methodology-changelog.md)` (single-line, single-clause, matches "External integrations (OAuth, payment gateways, third-party APIs)" shape). Evidence paragraph as markdown blockquote: `> **Evidence for the In-house methodology surfaces trigger**: voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 …`. mission-brief AC #1 + AC #2 + Notes section + Verification-plan + Must-not-defer all updated to reflect the bullet/evidence split. Location-pin scope widened from `Heavy mode (always)` to `### Step 5:` end anchor to include evidence paragraph. AC #1 row 2 sub-asserts the bullet position between `Security-sensitive paths` and `Heavy mode (always)` specifically. ADR-009 Option 1 description rewritten to show both surfaces.

#### M2: AC #2's "≥2 of {slice-006, slice-007, slice-008, slice-009}" anchor count drops slice-001..005 — but the bullet body claims "N=9/9 across slices 1-9", semantic mismatch

- **Claim under review**: AC #2 verifies bullet body cites slices 6-9 examples; bullet body says "across slices 1-9".
- **Issue**: A future drift could rewrite the bullet to say "N=4/4 across slices 6-9" and AC #2 would still pass — the test doesn't enforce the headline N count matches the cited slice range.
- **Evidence**: mission-brief.md AC #1 pins `N=9/9` AND AC #2 pins ≥2 of slices 6-9, but no test pins co-occurrence.
- **Proposed fix**: Dovetails with B1 — once "8 of 9 design-stage catches" is dropped and the cumulative-post-build framing is honest, the slice-N example anchors are illustrative-of-the-evidence-base; the headline N comes from cumulative-validation-post-build (verifiable per slice-N reflections). AC #2 stays.
- **Builder draft**: **ACCEPTED-FIXED** — dovetailed with B1 fix. Once "8 of 9 design-stage catches" was dropped and the cumulative-post-build framing replaced it, "across slices 1-9" became honest cumulative framing (every slice 1-9 had voluntary Critic with VALIDATED findings post-build, verifiable per slice-N reflection's Critic-calibration section), and the slice-6-9 example anchors became illustrative-sub-class-anchors rather than evidence-of-N-count. AC #2 stands.

#### M3: "Optional sub-class anchors" (4 anchors) descriptive only, not test-pinned — creates a drift-vector

- **Claim under review**: design.md What's-new — 4 sub-class anchors (`INST-1 inventory drift`, `install-time rename`, `negative-anchor uniformity`, `recursive self-application`) marked descriptive-only.
- **Issue**: Slice-009 N-substring schema-pin discipline (referenced repeatedly in mission-brief) says substantive prose anchors should be pinned. Leaving 4 anchors unpinned creates drift vector.
- **Evidence**: design.md What's-new sub-class anchor enumeration; AC #2 pattern shows ≥2-of-4 anchor pin is the precedent.
- **Proposed fix**: Add a 5th TF-1 row (AC #2 sub-row) pinning ≥2 of 4 sub-class anchors. TF-1 plan grows 7 → 8 rows. Cost: ~10 min at /build-slice.
- **Builder draft**: **ACCEPTED-PENDING** — fix applied at /build-slice (not at /critique). At Phase 1a of /build-slice, write `test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors` alongside the other 4 prose-pin tests; TF-1 plan grows 7 → 8 rows; design.md test enumeration already updated to list this test as the 5th function with explicit ACCEPTED-PENDING marker. mission-brief AC #2 verification + Tooling section also updated to note the M3 sub-class anchor row added at /build-slice.

### Minors (log; address if cheap)

#### m1: design.md L11 + ADR-009 L57 + L113 "between line 171 and line 172" creates a slice-010-internal drift-vector

- **Claim under review**: Line-number references in design.md + ADR-009 for SKILL.md insertion point.
- **Issue**: After slice-010 ships, the bullet list reorders; future references to L171 mislocate.
- **Proposed fix**: Replace line numbers with symbolic references ("between `Security-sensitive paths` bullet and `Heavy mode (always)` bullet").
- **Builder draft**: **ACCEPTED-FIXED** — applied. design.md "Lives at" subsection in Components touched now says "Line numbers as-of-2026-05-12: section spans L155-174 … All slice-010 references are symbolic post-2026-05-12 (per Critic m1)". ADR-009 Option 1 description updated to use symbolic references with a single "line numbers cited as-of-2026-05-12 in design.md L155-174 once" anchor.

#### m2: Anchor uniqueness is point-in-time; ADR-009 Option 2 example body itself contains "Heavy mode (always)" prose

- **Claim under review**: mission-brief Notes "anchors on the UNIQUE substring `Heavy mode (always)` (line 172) as end-of-section anchor" — uniqueness verified empirically pre-AC-lock.
- **Issue**: Point-in-time uniqueness. ADR-009 Option 2 example body contains "Heavy mode (always)" prose that could leak into SKILL.md if a future slice author copies it.
- **Proposed fix**: Use more rare/idiosyncratic location-pin anchor at slice-011+ if recurrence surfaces.
- **Builder draft**: **DEFERRED** to slice-011+ — verbosity-cost of switching anchors NOW > marginal robustness gain. ADR-009 Option 2 example body is in vault prose (not in SKILL.md target file); the location-pin test's anchor uniqueness on SKILL.md itself remains stable through slice-010. If a future slice modifies Step 4a in a way that introduces "Heavy mode (always)" prose elsewhere in SKILL.md, the location-pin test would surface the collision as an immediate AssertionError, providing a fail-fast detection rather than silent drift. Defer monitoring to slice-011+.

#### m3: ADR-009 surface area "5-7 sites" is undercount; closer to 11-13

- **Claim under review**: ADR-009 Reversibility "surface area ~5-7 sites".
- **Issue**: Counting actual sites: 11-13 (SKILL.md bullet + evidence paragraph + installed mirror + methodology-changelog v0.25.0 + installed mirror + VERSION + ai-sdlc-VERSION + plugin.yaml.version + 2 new test files + test_methodology_changelog.py edits + ADR file + 2 shippability sub-edits). Closer in magnitude to ADR-007 (BC-1 v1.2 ~10-15 sites) than to ADR-008 (CCC-1 v1.1 ~5 sites).
- **Proposed fix**: Recount + update ADR-009 Reversibility magnitude estimate + comparison.
- **Builder draft**: **ACCEPTED-FIXED** — applied. ADR-009 Reversibility section's Magnitude estimate rewritten with explicit enumeration of all 11-13 sites. Comparison sentence updated: "closer in magnitude to ADR-007 (~10-15 sites) than to ADR-008's ~5 sites". Cheap-vs-expensive verdict unchanged (still cheap; revert path remains git-diff-revert + superseding entry).

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (N=9/9 + "8 of 9" claim doesn't survive cross-reflection audit); B3 (ADR-009 slice-001/002 enumeration hand-waves disposition state); B4 (BC-1 self-application prediction's "negative-anchor silences" framing structurally inapplicable for BC-PROJ-1/2). All three ACCEPTED-FIXED in this round.
- [x] **Missing edge cases** — m2 (anchor uniqueness point-in-time; ADR Option 2 prose could leak). Single minor; DEFERRED.
- [x] **Over-engineering** — M1 (bullet body asymmetry — too long for bullet position; evidence belongs in adjacent prose). ACCEPTED-FIXED.
- [x] **Under-engineering** — M3 (sub-class anchors unpinned creates drift vector); B2 (TF-1 PENDING → WRITTEN-FAILING genuineness contradiction). M3 ACCEPTED-PENDING for /build-slice; B2 ACCEPTED-FIXED.
- [x] **Contract gaps** — None. Slice introduces no HTTP endpoints, events, or external integrations (design.md L122 + L124 explicit).
- [x] **Security** — None. Slice modifies methodology-prose + version files + plugin manifest. No auth, no user data, no network.
- [x] **Drift from vault** — None significant. Correctly references CCC-1 v1.1 / CAD-1 / BC-1 v1.2 / PMI-1 supersession.
- [x] **Web-known issues** — Skipped. Pure methodology-prose internal to this project's pipeline.
- [x] **Cross-cutting conformance** — B1 + B2 + B3 + B4 + B5 + M1 + M2 + M3 collectively span cross-cutting concerns. The recursive self-application stress test found 3+ rule-class violations in slice-010's own draft (B1 internal inconsistency, M1 stylistic asymmetry, B5 rule-naming convention break) — recursive-self-application phenomenon ratchets from slice-009 M2 (N=1) to slice-010 (N=2 candidate post-completion). Discipline DOES self-apply.

---

## Triage

**Triaged by**: user
**Date**: 2026-05-12
**Final verdict**: NEEDS-FIXES

User ratification: `accept all` (all Builder drafts ratified as-is at TRI-1 Step 4.5). One finding (M3) is ACCEPTED-PENDING — the 5th prose-pin test (`test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors`) is added at /build-slice Phase 1a; TF-1 plan grows 7 → 8 rows. All other findings are ACCEPTED-FIXED (10 edits applied in the /critique round across mission-brief.md + design.md + ADR-009) or DEFERRED (m2 only). Verdict computed mechanically per /critique Step 4.5 rules: 0 ESCALATED → not BLOCKED; M3 ACCEPTED-PENDING → NEEDS-FIXES (the gate to /build-slice is OPEN; ACCEPTED-PENDING fixes apply during /build-slice).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Dropped "8 of 9 design-stage catches" framing across mission-brief + design + ADR-009 + proposed SKILL.md bullet/evidence paragraph; replaced with honest cumulative-post-build framing per Option A |
| B2 | Blocker  | ACCEPTED-FIXED | AC #3 TF-1 row status `PENDING` → `PASSING`; Notes + Phase plan updated to describe PASSING → WRITTEN-FAILING (Phase 2b) → PASSING transition per slice-009 row 3 precedent |
| B3 | Blocker  | ACCEPTED-FIXED | ADR-009 Context per-slice enumeration rewritten with honest disposition state for slice-001..009; new "Honest aggregate framing" subsection replaces prior "Aggregated metrics" |
| B4 | Blocker  | ACCEPTED-FIXED | Audit 3 prose (design.md + mission-brief.md) distinguishes no-positive-firing (BC-PROJ-1/2) from negative-anchor-silencing (BC-GLOBAL-1) with empirical word-boundary counts |
| B5 | Blocker  | ACCEPTED-FIXED | Global rename MCR-1 → MCT-1 (Mandatory Critic Trigger; -T- signals /slice-time trigger vs audit-enforced gate); ADR-009 prepended with naming-rationale note; v0.25.0 changelog entry plan includes Limitations note |
| M1 | Major    | ACCEPTED-FIXED | Bullet split into terse form + adjacent evidence prose paragraph (markdown blockquote); design.md + ADR-009 + mission-brief restructured; location-pin scope widened to `### Step 5:` end anchor |
| M2 | Major    | ACCEPTED-FIXED | Dovetailed with B1 fix — cumulative-post-build framing makes "across slices 1-9" honest; slice-6-9 anchors become illustrative-sub-class-anchors not evidence-of-N-count |
| M3 | Major    | ACCEPTED-PENDING | At /build-slice add `test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors` (5th prose-pin test); TF-1 plan grows 7 → 8 rows; design.md test enumeration + AC #2 verification already updated to reflect the planned addition |
| m1 | Minor    | ACCEPTED-FIXED | Line-number references replaced with symbolic ones in design.md + ADR-009 (single as-of-2026-05-12 anchor preserved once) |
| m2 | Minor    | DEFERRED | To slice-011+ — verbosity-cost of anchor change now > marginal robustness gain; ADR-009 Option 2 example body is in vault prose only (not in SKILL.md target file); fail-fast location-pin test surfaces any future collision as immediate AssertionError |
| m3 | Minor    | ACCEPTED-FIXED | ADR-009 Reversibility surface-area estimate corrected to ~11-13 sites; comparison sentence updated to "closer in magnitude to ADR-007 than to ADR-008"; cheap verdict unchanged |
