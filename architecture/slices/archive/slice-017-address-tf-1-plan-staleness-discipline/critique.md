# Critique: Slice 017 address-tf-1-plan-staleness-discipline

**Critic reviewed**: mission-brief.md, design.md, ADR-016-tphd-1-tf-plan-harmonization-discipline.md
**Date**: 2026-05-13
**Result**: CLEAN (all 7 dispositions ACCEPTED-FIXED at /critique fix-prose; user-ratified at TRI-1)

## Summary

The TPHD-1 codification is structurally well-pinned (3-surface schema, prose-pin duality, RPCD-1 sub-mode audits, EPGD-1 self-application all rigorous), and the mechanical insertion-point table verifies cleanly against actual line numbers in all three SKILL.md files. However, **the central lesson-framing in ADR-016 misrepresented what `tools/test_first_audit.py --strict-pre-finish` actually catches** (B1) — the audit checks `row.status != "PASSING"` only; it does not verify Test function names exist at the named Test path. This affected the value proposition of sub-modes (a)/(b) and the slice-016 root-cause narrative, now corrected. Three further majors covered cross-surface magnitude inconsistency (M1), structurally anomalous `### Step 0` placement vs natural `## Prerequisite check` fold (M2), and Audit 6 BC-1 reasoning naming wrong negative-anchor tokens (M3). Three minors completed the catch density at N=7 self-defects per recursive-self-application discipline (matching slice-013 N=7 / slice-015 N=6 / slice-016 N=4 codification-slice empirical band N=4-7).

All 7 findings VALIDATED at /critique-disposition via ACCEPTED-FIXED in same fix block — TPHD-1 sub-mode (a) self-application empirically demonstrated at slice-017's own /critique fix-prose phase: when M2 ACCEPTED-FIXED renamed test function names from `_phase_0_step_*` → `_prerequisite_check_bullet_*`, the mission-brief TF-1 plan rows 8-9 were harmonized in the SAME fix block per TPHD-1 sub-mode (a). Slice-017 IS the canonical reference instance #1 of TPHD-1 at /critique time.

## Findings

### Blockers (must address before /build-slice)

#### B1: ADR-016 Context misrepresents `tools/test_first_audit.py --strict-pre-finish` semantics

- **Claim under review**: ADR-016 L17: *"The `/build-slice` skill's Phase 6 strict-pre-finish gate runs `tools/test_first_audit.py --strict-pre-finish` (per TF-1, `methodology-changelog.md` v0.13.0) which refuses if any mission-brief TF-1 plan row has status outside `{PENDING, WRITTEN-FAILING, PASSING}` OR if any AC declared in the brief body has no test-first row OR if any row's Test function name doesn't exist at the named Test path."*
- **Issue**: The third clause ("OR if any row's Test function name doesn't exist at the named Test path") is false. `tools/test_first_audit.py:350-364`: `--strict-pre-finish` only emits `non-passing-pre-finish` violations when `row.status != "PASSING"`. There is no `name_exists` / `path_exists` / function-introspection check anywhere in the audit. This is a load-bearing factual error because it shapes the **lesson framing** of the entire slice. Under accurate TF-1 semantics, the slice-016 DEVIATION was caught because rows were PENDING (per ADR-016 L30 "All 10 TF-1 plan rows still in PENDING status at Phase 6 audit time"), not because function names were stale.
- **Evidence**: `tools/test_first_audit.py:65` (`_ALLOWED_STATUSES`), `tools/test_first_audit.py:320` (`status not in _ALLOWED_STATUSES` violation), `tools/test_first_audit.py:350-364` (`--strict-pre-finish` clause checks status only).
- **Proposed fix**: Correct ADR-016 Context paragraph to accurately describe what the audit checks (status only; no function-existence check). Reframe TPHD-1's value as prophylactic against an audit gap, not a redundant defense to an existing audit check.
- **Builder draft**: ACCEPTED-FIXED at `ADR-016 Context paragraph L17-L40` — rewrote to accurately describe TF-1 audit semantics (status-only check); distinguished two failure modes (status-staleness mode caught by TF-1 audit; function-name-staleness mode NOT caught — surfaces only at pytest collection); reframed TPHD-1's value proposition as prophylactic against function-name-staleness audit gap + defense-in-depth for status-staleness. Confirms the user-invoked proactive ratchet at N=1 is structurally well-justified (the discipline closes an audit gap, not a redundant check).

### Majors (address this slice)

#### M1: Mission-brief AC #3 + design.md L124 magnitude claim contradicts ADR-016 magnitude claim

- **Claim under review**: mission-brief.md AC #3 L22: *"reversibility=cheap with magnitude justification **~3-5 sites** (3 skill files + methodology-changelog entry + canonical-phrase substring counts)"*. design.md L124: *"reversibility: **cheap** (~3-5 sites: 3 skill files + methodology-changelog + 3 test files; ~10-15 min revert per slice-016 ADR-015 magnitude class)"*. But ADR-016 L140, L162, L177: *"Magnitude estimate (~13-16 sites total)"*.
- **Issue**: Two distinct magnitude numbers across the slice's own artifacts. The 3-5 number is implausibly low when the slice modifies 3 SKILL.md files + 1 methodology-changelog entry + 1 ADR creation + 4 test files + 1 shippability row + 3 version files = ~12 distinct surfaces minimum (consistent with ADR-016's 13-16). Per slice-013 B1 rule-ID-drift catch class generalized to "internal-numeric-consistency", the slice should not ship with two different magnitude numbers for the same decision.
- **Evidence**: Cross-doc grep at mission-brief.md AC #3 vs design.md L124 vs ADR-016 L141-L154 enumeration (14 sites).
- **Proposed fix**: Harmonize mission-brief.md AC #3 + design.md L124 to read `~13-16 sites` matching ADR-016 (since the enumeration is explicit).
- **Builder draft**: ACCEPTED-FIXED at `mission-brief.md AC #3` + `design.md L124` — both updated to `~13-16 sites` with surface enumeration (3 skill files + methodology-changelog + 4 test files + shippability row + 3 version files + ADR file itself) matching ADR-016 Reversibility L141-L154 canonical enumeration. CCC-1 v1.1 sub-clause 2 doc-vs-canonical-inventory parity restored.

#### M2: Choice of `### Step 0` (new section) over folding TPHD-1 sub-mode (c) into existing `## Prerequisite check` is unjustified

- **Claim under review**: design.md "Mechanical insertion-point table" row 4 + ADR-016 Option 1 + ADR-016 L114: *"`skills/build-slice/SKILL.md` gains NEW `### Step 0: TPHD-1 — TF-1 plan harmonization pre-flight` between `## Your task` (L24) and `### Step 1: Load full slice context` (L26)."*
- **Issue**: `skills/build-slice/SKILL.md` already has a `## Prerequisite check` section at lines 17-22 that runs BEFORE `## Your task`. TPHD-1 sub-mode (c) is structurally a prerequisite verification ("scan the mission-brief TF-1 plan table; for each row, verify Test path exists or will be created at the right path AND Test function name will match what gets built"). The natural home is `## Prerequisite check` (bullet item). Inserting a NEW `### Step 0` introduces a numbering anomaly — the file's step numbering is 1,2,3,4,5,6,7,7b,7c,8; `Step 0` breaks the linear sequence. Neither ADR-016 Option 1 nor design.md addresses why the existing prerequisite section is rejected.
- **Evidence**: `skills/build-slice/SKILL.md:17-22` (existing Prerequisite check section); `grep -n "### Step" skills/build-slice/SKILL.md` shows step numbers 1,2,3,4,5,6,7,7b,7c,8 (no Step 0 anywhere).
- **Proposed fix**: (a) move TPHD-1 sub-mode (c) into `## Prerequisite check` as a new bullet "Run TPHD-1 pre-flight harmonization..." eliminating the `### Step 0` numbering anomaly; adapt prose-pin tests accordingly.
- **Builder draft**: ACCEPTED-FIXED at `mission-brief.md AC #2 + intent paragraph + must-not-defer + TPHD-1 self-application probe` + `design.md What's new + Components touched (skills/build-slice/SKILL.md + test_build_slice_skill.py) + Mechanical insertion-point table row 4 + Audit 3 + Audit 5` + `ADR-016 Option 1 + Option 2 + Decision + Consequences + Reversibility magnitude L147` — all references updated from "Step 0" placement to "NEW bullet INTO existing `## Prerequisite check` section (between L22 and `## Your task` L24)". TF-1 plan rows 8-9 renamed `_phase_0_step_*` → `_prerequisite_check_bullet_*` AND mission-brief AC #2 reflects placement decision rationale. **TPHD-1 sub-mode (a) self-application empirically demonstrated**: this fix block IS the canonical reference instance #1 of TPHD-1 sub-mode (a) — the rename of TF-1 plan function names triggered same-fix-block harmonization per the discipline TPHD-1 codifies.

#### M3: Audit 6 (BC-1 self-application) lists wrong negative-anchor token set for BC-PROJ-2

- **Claim under review**: design.md Audit 6 L226-L233: *"Mission-brief + design.md substring count of methodology-vocabulary tokens (`fence` / `code-block` / `LLM` / `prompt` / `agent`)"* and *"9-token set includes `methodology`, `Critic`, `slice`, `dim`, `Dimension`, etc."*
- **Issue**: BC-PROJ-2's actual `Trigger keywords` field is: `parse, fence, code-block, backtick, llm, agent, prompt, output, response`. Trigger anchors are `fence, code-block, llm`. Negative anchors per slice-012 migration: `defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`. The 9-token set named in design.md Audit 6 (`methodology`, `Critic`, `slice`, `dim`, `Dimension`) is NOT in BC-PROJ-2's rule body. The audit reasoning is not load-bearing — it can't reliably predict whether BC-PROJ-2 will fire or not.
- **Evidence**: `architecture/build-checks.md` L33-L35 (BC-PROJ-2 rule body trigger keywords + trigger anchors + negative anchors).
- **Proposed fix**: Rewrite Audit 6 with actual BC-PROJ-2 9 trigger keywords + 3 trigger anchors + 9 negative anchors; compute accurate substring counts; state empirical fire-or-silence prediction based on trigger-anchor / negative-anchor interaction.
- **Builder draft**: ACCEPTED-FIXED at `design.md Audit 6` — fully rewritten with empirically correct BC-PROJ-2 trigger keywords (9-token) + trigger anchors (3) + negative anchors (9) from `architecture/build-checks.md:33-35`; computed accurate substring counts; verified Applies-to glob (0 `skills/**/*.py` matches), positive trigger keyword matches (`agent`/`prompt`/`output`/`response` fire), trigger anchors final-filter (0/3 anchors match → rule does NOT fire), negative anchors final-filter (`forward-sync`/`Critic-MISSED`/`aggregated lessons` would silence it even if anchors had matched). Conclusion: BC-PROJ-2 silenced on slice-017 via trigger-anchors final-filter (primary) + negative-anchors final-filter (secondary backup); 0 BC-PROJ-2 fires expected at /build-slice Phase 5.

### Minors (log; address if cheap)

#### m1: Rule-ID drift negative-example anchors create RSAD-1 sub-mode (b) re-introduction

- **Claim under review**: mission-brief.md Must-not-defer item #1 L61 + design.md L245 enumerate `TPH-1`, `TPHD1`, `tphd-1` as anti-patterns. A naive substring grep for these anti-forms against the slice's artifacts will return those very design.md / mission-brief lines (RSAD-1 sub-mode (b) re-introduction class; N=2 pattern slice-010 DEVIATION-3 + slice-011 RSAD-1 codification body).
- **Issue**: Severity Minor because (a) any rule-ID-drift check should grep for canonical-form usage as the assertion, not anti-form absence; (b) the must-not-defer item is rhetoric, not an automated check.
- **Evidence**: `mission-brief.md:61` and `design.md:245` both contain the anti-form strings.
- **Proposed fix**: Drop anti-form enumeration; replace with positive-form assertion ("TPHD-1 canonical-form used uniformly across all surfaces").
- **Builder draft**: ACCEPTED-FIXED at `mission-brief.md Must-not-defer item #1` + `design.md "Rule-ID drift" bullet under Recursive-self-application section` — both updated to use positive-form assertion `grep -c "TPHD-1" <file>` returns ≥1 hit per surface, removing anti-form enumeration. RSAD-1 sub-mode (b) re-introduction risk eliminated.

#### m2: Mid-slice smoke gate references non-existent Phase 1f

- **Claim under review**: mission-brief.md "Mid-slice smoke gate" L94 specifies running after "Phase 1a-1f INSERT/Edit" — but design.md L138-L146 phase plan only enumerates Phases 1a-1e + 2 + 3 + 4 + 5 (no 1f).
- **Issue**: Mission-brief's "Phase 1a-1f" is a range that includes a non-existent Phase 1f. Minor textual drift; no functional impact (the smoke gate command itself is correct).
- **Evidence**: design.md L138-L146 phase plan enumerates Phases 1a-1e (no 1f); mission-brief L94 references "Phase 1a-1f".
- **Proposed fix**: Mission-brief change "Phase 1a-1f" → "Phase 1a-1e".
- **Builder draft**: ACCEPTED-FIXED at `mission-brief.md mid-slice smoke gate L94` — corrected to "Phase 1a-1e" matching design.md phase plan enumeration.

#### m3: AC #5 "row 17 cites SCPD-1 proactive-application N=2 → N=3 stable" is a self-pinning claim with weak verification

- **Claim under review**: mission-brief.md AC #5 L26: *"row 17 cites SCPD-1 proactive-application N=2 → N=3 stable per /build-slice Phase 5 in-line propagation discipline"*.
- **Issue**: SCPD-1 proactive-application requires an active propagation event. Slice-017 has no `_lists_N_sub_clauses` supersession (per AC #5 itself); SCPD-1 proactive-application is **vacuously satisfied** — there is nothing to propagate. The "N=2 → N=3 stable" counter increment is not earned by this slice; SCPD-1 N=2 (slice-016) stays N=2 stable.
- **Evidence**: AC #5 itself acknowledges "no Dim 9 sub-clause supersession; `_lists_nine_sub_clauses` stays valid".
- **Proposed fix**: Drop the "N=2 → N=3 stable" counter claim from AC #5. SCPD-1 stays at N=2 stable; slice-017 is a no-op for SCPD-1.
- **Builder draft**: ACCEPTED-FIXED at `mission-brief.md AC #5` — dropped "N=2 → N=3 stable" counter claim; restated as "SCPD-1 stays at N=2 stable (per /critique m3 ACCEPTED-FIXED: slice-017 has NO Dim 9 sub-clause supersession event, so SCPD-1 proactive-application is vacuously satisfied — no active propagation event occurs; row 17 is added as a NEW row with no prior-row touch needed)". SCPD-1 counter integrity preserved.

## Dimensions checked

- [x] Unfounded assumptions — B1 (load-bearing TF-1 audit-semantics misrepresentation); m3 (SCPD-1 counter increment unfounded for this slice). Both ACCEPTED-FIXED.
- [x] Missing edge cases — No findings. Pure methodology-prose codification; no load/empty/network/concurrency surfaces. Mid-slice smoke gate covers PMI-1 invariant + CAD-1 byte-equality.
- [x] Over-engineering — No findings. 3-surface skill-prose codification justified by 3 distinct Critic-stack fix-prose moments. Wiegers `_present` + `_location_pinned` duality justified by N=4 stable precedent.
- [x] Under-engineering — M2 (Step 0 vs Prerequisite-check placement; folded into existing section). ACCEPTED-FIXED. TF-1 row coverage clean post-fix.
- [x] Contract gaps — No findings. No new endpoint, event, or integration.
- [x] Security — No findings. Pure methodology prose.
- [x] Drift from vault — M1 (magnitude inconsistency). ACCEPTED-FIXED. ADR-016 references vault-grounded.
- [x] Web-known issues — Skipped — no external platform/API/SDK choices in scope.
- [x] Cross-cutting conformance — M3 (Audit 6 BC-1 self-application reasoning structurally invalid, wrong negative-anchor token set named). ACCEPTED-FIXED. m1 (RSAD-1 sub-mode (b) re-introduction in negative-example enumeration). ACCEPTED-FIXED. EPGD-1 self-application (Audit 4) confirms 0/12 prior entry-pin functions touched (count corrected from initial 0/11 per /critique-review m-add-1 ACCEPTED-FIXED — v0.31.0 doubled per slice-016 RPCD-1 (a)↔(b) duality at test_methodology_changelog.py:844 + :910 was missed in initial design.md Audit 4). Recursive-self-application discipline (RSAD-1) catches at design.md L240-L245 enumerated 5 expected self-defect categories; this critique surfaced 1 blocker + 3 majors + 3 minors = 7 findings on the slice's own draft, **EMPIRICALLY MATCHING slice-013 N=7 codification-slice density** (and within the N=4-7 band per slice-011/013/015/016 precedent). Recursive-self-application N=8 → **N=9 cumulative** post-RSAD-1 codification CONFIRMED at slice-017 /critique.

## Triage

**Triaged by**: user
**Date**: 2026-05-13
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | ADR-016 Context paragraph L17-L40 rewrote to accurately describe TF-1 audit semantics (status-only check); reframed TPHD-1 value as prophylactic against function-name-staleness audit gap + defense-in-depth for status-staleness |
| M1 | Major    | ACCEPTED-FIXED | mission-brief.md AC #3 + design.md L124 updated to ~13-16 sites matching ADR-016 Reversibility enumeration L141-L154 |
| M2 | Major    | ACCEPTED-FIXED | All "Step 0" references in mission-brief.md + design.md + ADR-016 updated to "NEW bullet INTO existing `## Prerequisite check` section"; TF-1 plan rows 8-9 renamed `_phase_0_step_*` → `_prerequisite_check_bullet_*`; TPHD-1 sub-mode (a) self-application empirically demonstrated at this fix block |
| M3 | Major    | ACCEPTED-FIXED | design.md Audit 6 rewritten with empirically correct BC-PROJ-2 trigger keywords (9-token) + trigger anchors (3) + negative anchors (9) from architecture/build-checks.md:33-35 |
| m1 | Minor    | ACCEPTED-FIXED | mission-brief.md must-not-defer #1 + design.md "Rule-ID drift" bullet updated to positive-form assertion; anti-form enumeration removed |
| m2 | Minor    | ACCEPTED-FIXED | mission-brief.md mid-slice smoke gate Phase 1a-1f → Phase 1a-1e matching design.md phase plan |
| m3 | Minor    | ACCEPTED-FIXED | mission-brief.md AC #5 SCPD-1 N=2 → N=3 stable counter claim dropped; restated as "SCPD-1 stays at N=2 stable" (vacuously satisfied) |
| m-add-1 | Minor (meta-Critic) | ACCEPTED-FIXED | design.md Audit 4 entry-pin count drift (11 → 12) corrected across 6 sites: mission-brief.md L66 + design.md L32 + L92 + L138 + L206 + L208 + critique.md L87. v0.31.0 doubling per slice-016 RPCD-1 (a)↔(b) duality acknowledged. EPGD-1 guarantee 0/N preserved at corrected N=12. Wiegers regression-guard coverage-symmetry watch-list class N=1 → **N=2 cumulative** post-slice-016 codification (ratchets toward N=3 promotion threshold) — see [critique-review.md](critique-review.md) m-add-1 |
