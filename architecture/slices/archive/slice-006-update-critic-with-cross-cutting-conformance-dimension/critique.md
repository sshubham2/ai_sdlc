# Critique: Slice 006 update-critic-with-cross-cutting-conformance-dimension

**Critic reviewed**: mission-brief.md, design.md, ADR-005
**Date**: 2026-05-10
**Result**: NEEDS-FIXES (final, post-triage)

## Summary

The intent (a 9th umbrella dimension) is sound, the citation choice (Kiczales for vocabulary + honest-out for evidence) is well-defended in ADR-005, and the prose-parity sweep is thorough. However, the slice rests on a load-bearing factual claim that is **demonstrably false at design time**: the in-repo `agents/critique.md` does NOT contain the surgical Dim 1 / Dim 4 sub-bullets that the design says are at lines 57 and 89-92, and that Dim 9's three cross-references depend on. Those sub-bullets exist ONLY in the installed `~/.claude/agents/critique.md`. This invalidates the must-not-defer item "Cross-references explicit", contradicts the design's own "in-repo source is canonical" claim, and would either (a) build a Dim 9 with broken cross-references against the in-repo file, or (b) build it against the installed file as canonical, which the design explicitly says is not the source-of-truth. Until the cross-reference targets actually exist in the in-repo source, this slice cannot meet AC #2 sub-clauses 1-3 honestly.

**Builder verification of B1**: Empirically confirmed. In-repo `agents/critique.md` = 184 lines, sha256 `F3FD5F9098…`. Installed `~/.claude/agents/critique.md` = 189 lines, sha256 `B926CC6606…`. Substring `Methodology-audit conformance`: present 1× in installed, absent 0× in-repo. Dim 1 example bullets in in-repo end at line 56 (3 examples only); Dim 4 bullets end at line 87 (3 examples only). The /critic-calibrate ACCEPTED 2026-05-10 surgical edits were applied to the installed file (per `skills/critic-calibrate/SKILL.md:108-109` instructions to "edit ~/.claude/agents/critique.md") but never propagated back to the in-repo source. The Critic's lead finding is dispositive.

## Findings

### Blockers (must address before /build-slice)

#### B1: Cross-reference targets do not exist in the in-repo canonical source — Dim 9 sub-clauses 1, 2, 3 will point at empty lines

- **Claim under review**: From design.md "What's reused": *"the two surgical sub-bullets at line 57 (Dim 1 — tooling-doc-vs-implementation parity) and lines 89–92 (Dim 4 — methodology-audit conformance + algorithm-path-conformance with pre-existing branches), added per /critic-calibrate 2026-05-10 ACCEPTED proposals, remain as the cross-reference targets that Dim 9 sub-clauses 1–3 point at."* And from mission-brief AC #2 sub-clauses 1-3 (cross-references to Dim 1 / Dim 4).
- **Issue**: Empirically: in-repo `agents/critique.md` line 57 is blank; lines 89-92 are the start of Dimension 5 (Contract gaps), NOT Dimension 4 sub-bullets. `Methodology-audit conformance` substring absent from in-repo (0 occurrences); present in installed (1 occurrence). The two surgical edits exist only installed-side; never propagated back. The mission-brief and design state confidently that these targets exist — but the canonical edit surface for THIS slice is `agents/critique.md` (the in-repo file is the editable source per design.md "the in-repo source is canonical; the installed copy is the live working copy").
- **Evidence**:
  - In-repo `agents/critique.md`: 184 lines, sha256 `F3FD5F9098012A858267DB29245006825480219DD72B9946EEF32182DDD224A4`.
  - Installed `~/.claude/agents/critique.md`: 189 lines, sha256 `B926CC6606E3D40042BD0A630984D82765EA384B9254D1173DFC469111AD7EA7`.
  - Substring `Methodology-audit conformance`: in-repo 0× / installed 1×.
  - `tools/install_audit.py` checks file existence only (no `sha256` / `hashlib` / content-equality logic) — so in-repo↔installed content drift is not currently caught by any audit.
  - `skills/critic-calibrate/SKILL.md:108-109` explicitly instructs editing the installed file, never the in-repo file — this is the structural cause.
- **Proposed fix**: **Option A (recommended)** — Add a pre-Dim-9 build step "Sync the two prior /critic-calibrate ACCEPTED edits back into in-repo `agents/critique.md`". Insert the Dim 1 sub-bullet at the right position (after "Async queue is sufficient" example) and the Dim 4 sub-bullet (after "Must-not-defer says ... design has no authz on /X" example). Add new tests `test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet` and `test_critique_dim_4_has_methodology_audit_conformance_sub_bullet` so this drift is caught next time. THEN add Dim 9 with cross-references to the now-existing targets.
- **Builder draft**: **ACCEPTED-FIXED** — apply Option A. Update mission-brief and design.md to add the back-sync step as the first build-time action; add the two new prose-pin tests for the surgical sub-bullets to the test plan; Dim 9 cross-references then resolve to real in-repo prose. The slice is now bigger but still under 1 day (~3-4 hours total). This is also itself the *first concrete demonstration* of the cross-cutting-conformance class the slice exists to address — the slice was about to ship the very defect class it intends to mitigate.

#### B2: Verification plan #1 doesn't exercise cross-reference target resolution — Dim 9 body could ship with stale dangling pointers and still PASS

- **Claim under review**: Mission-brief verification plan row 1 (regex count of `### \d+\.` headings) + must-not-defer item 3 (cross-references explicit).
- **Issue**: The verification regex only counts heading shape; it cannot detect that "see Dimension 4 sub-bullet" points at non-existent prose. Smoke gate tests structure not semantic-target validity. So if B1 is fixed via Option C (drop cross-references) but a stale "see Dim 4 sub-bullet" pointer is left behind, AC #1 still PASSES. The slice would ship the very tooling-doc-vs-implementation parity defect class it exists to mitigate.
- **Evidence**: Mission-brief verification plan row 1 + Dim 9 body shape's literal "see Dimension 4 sub-bullet" text.
- **Proposed fix**: Add test `test_critique_dim_9_cross_references_resolve` that asserts each "see Dimension 4 sub-bullet" / "see Dimension 1 sub-bullet" pointer in Dim 9 body is paired with the actual existence of the referenced sub-bullet text within the same file (e.g., `assert "see Dimension 4 sub-bullet" in CRITIQUE` AND `assert "Methodology-audit conformance" in CRITIQUE` both required to PASS together). Update mission-brief verification plan row 1 to add this assertion.
- **Builder draft**: **ACCEPTED-FIXED** — fix lands with B1: once back-sync is in scope, the cross-references resolve to real prose. Add the cross-reference resolution test as Critic specified. Standalone value (catches independent-side drift in the future).

### Majors (address this slice)

#### M1: "Won't double-fire" claim is asserted via mental simulation — same shape as the slice-005 lesson the slice cites as prior art

- **Claim under review**: design.md "Empirical verification at design-time" item 3: *"Verified by mental simulation against slice-005's design.md: the BC-GLOBAL-1 always-true miss would be filed under either Dim 4 (algorithm-path-conformance) or Dim 9 (cross-cutting view of the same), not both."*
- **Issue**: "Verified by mental simulation" is exactly the discipline the slice-005 aggregated lesson "Empirical verification at design-time should exercise ALGORITHM PATHS, not just isolated metric counts" was added to defend against. The claim "won't double-fire" lacks an observable success criterion at design-time. Per Wiegers (Dim 1 frame), this trace-to-evidence gap is a Major.
- **Evidence**: Aggregated lessons L1 (slice-005) + L6 (N=4 stable empirical-verification discipline). Design.md's exact phrase "verified by mental simulation".
- **Proposed fix**: Either (a) replace mental simulation with an exercised check: pick 3 archived slices (001, 003, 005), write out per-slice the Dim 9 vs Dim 1/Dim 4 finding-text the Critic would produce for the same underlying miss; show dispositions wouldn't conflict at TRI-1 — OR (b) add Major verification step: in the next 2-3 slices' /critique runs, instrument for double-firing and surface the signal at /critic-calibrate.
- **Builder draft**: **ACCEPTED-PENDING** — apply at /build-slice T-late (after Dim 9 added + B1 back-sync done). Spawn 1 Critic re-critique of slice-005's archived design.md against the new 9-dim Critic; capture in build-log.md the finding count + per-finding dimension framing. If the same underlying miss produces ONE finding (Dim 4 OR Dim 9 framing) → empirical confirmation of the no-double-fire claim. If it produces TWO findings → revisit Dim 9 cross-reference structure (could escalate to BLOCKED at validate-time). Add a calibration-log signal note for tracking double-firing across slices 6-8 to the next /critic-calibrate.

#### M2: Slice-005 forensic-capture precedent inherits the same in-repo↔installed gap — naive in-repo→installed re-sync would OVERWRITE the only correct copy of the surgical sub-bullets

- **Claim under review**: design.md out-of-repo files touched table (7 files needing in-repo→installed re-sync at T-final) + slice-005 precedent claim.
- **Issue**: Slice-005's precedent assumed in-repo was the source-of-truth. In THIS slice's case, in-repo `agents/critique.md` is missing content the installed copy has. Naive in-repo→installed sync would overwrite the surgical sub-bullets in the installed file, silently degrading the only correct copy. Recurring class, not a slice-005 corner case.
- **Evidence**: This slice = first instance where installed contains content in-repo doesn't. `skills/critic-calibrate/SKILL.md:108-109` instructs installed-file edits, never in-repo — every future /critic-calibrate ACCEPTED proposal creates this drift class.
- **Proposed fix**: Two-part: **(in this slice)** before any in-repo→installed re-sync at T-final, the build sequence must do installed→in-repo back-sync of the two surgical sub-bullets first. Build-log.md captures BOTH directions of sha256 (pre-back-sync, post-back-sync, post-Dim-9-edit, post-final-resync). **(precedent for future slices)** Update `skills/critic-calibrate/SKILL.md:108-109` to instruct editing in-repo source-of-truth. OR add `tools/critique_agent_drift_audit.py` content-equality check.
- **Builder draft**: **ACCEPTED-FIXED** — apply the in-this-slice fix as part of B1's resolution (back-sync direction comes first; build-log.md captures bidirectional sha256 trace). Defer the precedent-fix-for-future-slices (skill prose update + content-equality audit) to a separate slice. Track as a discovered risk in /reflect's Discovered section: "/critic-calibrate workflow has structural in-repo↔installed drift gap — slice-007+ candidate for `update-critic-calibrate-to-edit-in-repo-source` OR `add-critique-agent-content-equality-audit`."

#### M3: Kiczales citation "literally his framework's term" overstated — "cross-cutting concerns" crystallized in subsequent AOP literature, not in the original 1997 paper as a coined phrase

- **Claim under review**: design.md "Empirical verification at design-time" item 1 + ADR-005 Decision section: *"Kiczales is the canonical citation for 'cross-cutting concerns' terminology — the dimension's name is literally his framework's term."*
- **Issue**: Per the agent prompt's own Reference-frameworks paragraph: citation as evidence-trace. Web-search verification: the original 1997 ECOOP paper introduced AOP and the verb "cross-cut", but the noun phrase "cross-cutting concerns" as frozen term-of-art crystallized over the next 2-3 years in subsequent AOP literature. The current claim is slightly overstated.
- **Evidence**: Wikipedia "Aspect-oriented programming" + "Cross-cutting concern" articles confirm the terminology trajectory. The honest-out portion (no peer-level evidence-framework cited) is unimpeachable; the Kiczales vocabulary-anchor portion is sound but overstated.
- **Proposed fix**: Update Dim 9 body's first paragraph and ADR-005 Decision section's parallel claim to: "Vocabulary follows the **Aspect-Oriented Programming** body of work originating with Kiczales et al. (1997, ECOOP), where 'cross-cutting concerns' became a frozen term-of-art within ~2-3 years of the original paper." Precision tightening, not citation change.
- **Builder draft**: **ACCEPTED-FIXED** — apply Critic's exact suggested wording. Cosmetic precision; reads more honestly. Update both Dim 9 body and ADR-005 Decision section.

#### M4: VERSION ↔ changelog atomicity warning is correct but verification plan doesn't exercise the changelog format pin

- **Claim under review**: design.md "Components touched" → VERSION + Builder notes atomicity.
- **Issue**: Mid-slice smoke gate tests Dim 9 structure only, not changelog format pin. If the bumped-version commit lands and `test_version_matches_most_recent_changelog_entry` fails due to format drift (date separator, version shape), the failure surfaces only at pre-finish.
- **Evidence**: Mid-slice smoke gate definition + `tests/methodology/test_methodology_changelog.py` not inspected during design.
- **Proposed fix**: Add to mid-slice smoke gate: *"Verify `pytest tests/methodology/test_methodology_changelog.py::test_version_matches_most_recent_changelog_entry` passes locally."* Cheap; catches format-drift early.
- **Builder draft**: **ACCEPTED-FIXED** — add the pytest invocation to the mid-slice smoke gate PowerShell block. Cheap. Update mission-brief mid-slice smoke gate.

#### M5: ADR-005 reversibility "expensive" estimate excludes the irreversible portion (cumulative prompt-cache + in-context-conditioning effects + Dim-9-classified findings in archived slices)

- **Claim under review**: ADR-005 Reversibility section.
- **Issue**: Missing from cost estimate: post-revert, what happens to slice-006-N critique.md files filed under Dim 9? (They stay filed under Dim 9 — historical record.) Cumulative slice-006-N critique outputs influence pattern-recognition at future calibration runs irrespective of revert. Per ISO/IEC/IEEE 42010 (Dim 7), architecture description consistency requires the consequences section to acknowledge the irreversible portions. ADR-005 *does* note this in Consequences but not in Reversibility.
- **Evidence**: ADR-005 Reversibility lists 7 mechanical edit steps; Consequences item 1 has the in-context-conditioning paragraph but in the wrong section.
- **Proposed fix**: Either (a) move/duplicate the in-context-conditioning paragraph from Consequences into Reversibility for prominence, AND add sub-section "Items that cannot be reverted" — OR (b) downgrade ADR-005 reversibility from "expensive" to "irreversible-after-N-slices" with N=5.
- **Builder draft**: **ACCEPTED-FIXED** — apply Critic's Option (a). Move in-context-conditioning paragraph into Reversibility for prominence; add "Items that cannot be reverted" sub-section enumerating: archived critique.md files filed under Dim 9 stay filed under Dim 9 (historical record); calibration-log entries are append-only; cumulative slice-006-N critique outputs influence future pattern-recognition. Keep "expensive" tag (the additive structural-revert IS expensive but not strictly irreversible across all surfaces — only the historical-record portion is irreversible).

### Minors (log; address if cheap)

#### m1: Design.md says "Six in-repo prose-parity updates" but enumerates seven sites — typo

- **Claim under review**: design.md "What's new" item 6.
- **Issue**: Count word ("Six") doesn't match bullet count (7).
- **Evidence**: design.md "What's new" item 6 enumeration.
- **Proposed fix**: Change "Six" to "Seven".
- **Builder draft**: **ACCEPTED-FIXED** — one-character fix at /build-slice T-1.

#### m2: Test rename misses docstring update — "must walk all eight" prose contradicts new function name

- **Claim under review**: design.md test additions: rename `test_critique_lists_eight_dimensions` → `test_critique_lists_nine_dimensions`.
- **Issue**: Existing test at `tests/methodology/test_critique_agent.py:41-55` has docstring using literal "all eight review dimensions" / "the eight named dimensions". Rename without docstring update leaves contradiction.
- **Evidence**: `tests/methodology/test_critique_agent.py:42-46` docstring text.
- **Proposed fix**: Rename function AND update docstring to "must walk all nine review dimensions" / "the nine named dimensions".
- **Builder draft**: **ACCEPTED-FIXED** — update docstring alongside function rename. One-line fix.

#### m3: INST-1 install path note doesn't acknowledge content-drift gap — design.md should mention it explicitly even if defer fix to future slice

- **Claim under review**: design.md "What's reused" final bullet on INST-1 install path.
- **Issue**: INST-1 catches inventory drift but not content drift; the slice itself was caught by this gap (B1). Documenting the gap surfaces it for a future slice.
- **Evidence**: `tools/install_audit.py` inspection — no content-equality code; `skills/critic-calibrate/SKILL.md:108-109` instructs installed-file edits.
- **Proposed fix**: Add note to design.md (or future-work section) that INST-1 catches inventory drift but not content drift; consider INST-2 / `tools/critique_agent_drift_audit.py` for content-equality.
- **Builder draft**: **ACCEPTED-FIXED** — add a one-line acknowledgment to design.md's "What's reused" INST-1 bullet AND a Discovered entry at /reflect time tracking the structural-drift class for slice-007+. Out-of-scope for slice-006's actual implementation.

#### m4: Mid-slice smoke gate could include prose-parity sweep — partial-edit state would only surface at pre-finish today

- **Claim under review**: mission-brief mid-slice smoke gate (3 checks: heading count, Dim 9 heading, table row 9).
- **Issue**: A partial build that updates `~/.claude/agents/critique.md` but forgets one of the 7 prose-parity sites would PASS smoke and only surface at pre-finish via `test_no_in_repo_drift_on_eight_dimensions_phrase`.
- **Evidence**: Mid-slice smoke gate definition.
- **Proposed fix**: Add to smoke gate: count `8 dimensions` occurrences across `agents/`, `skills/`, `plugin.yaml`, `tutorial-site/`; assert == 0.
- **Builder draft**: **ACCEPTED-FIXED** — add the one-liner. Update mission-brief mid-slice smoke gate PowerShell block.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (cross-reference targets don't exist in canonical source); M1 (mental-simulation claim); M3 (Kiczales citation overstated). Per Wiegers, the cross-reference targets and "won't double-fire" claim do not trace to evidence at design time.
- [x] **Missing edge cases** — B2 (verification plan doesn't cover cross-reference target resolution); m4 (mid-slice smoke gate doesn't cover prose-parity drift).
- [x] **Over-engineering** — none. Slice is purely additive and disciplined: 5 sub-clauses with concrete examples, no speculative configurability, no plugin-system-with-one-plugin smell, no premature factory.
- [x] **Under-engineering** — B1 (AC #2 sub-clauses 1-3 cannot be honestly delivered as currently designed); m2 (test rename misses docstring update). Per Wiegers/Patton story-to-design traceability, AC #2's three cross-reference sub-clauses lack a deliverable design element in the in-repo file.
- [x] **Contract gaps** — none. No new endpoints / events / APIs. Critic-prompt-as-internal-contract gains 1 row in output checklist + 1 dimension body; design's parser-robustness note (`/critic-calibrate` skill scans `### \d+\.` headings rather than hardcoding 8) is correct.
- [x] **Security** — none because slice introduces no new authentication, authorization, network surface, or data exposure paths. Methodology-tooling slice with markdown / YAML / HTML / Python-test edits only.
- [x] **Drift from vault** — B1 (in-repo↔installed drift directly contradicts design's "in-repo is canonical" claim); M2 (slice-005 forensic-capture precedent inherits the gap); M5 (ADR-005 reversibility under-counts irreversible portion). Per Sommerville requirements-design traceability + ISO/IEC/IEEE 42010 architecture description consistency, slice has internal contradictions between "in-repo source is canonical" and "Empirical verification" item 3 citing installed-only line numbers as canonical content.
- [x] **Web-known issues** — M3 (Kiczales 1997 vocabulary-anchor claim verified against Wikipedia / Springer / ResearchGate — paper exists, ECOOP 1997 confirmed, but "cross-cutting concerns" as frozen noun-phrase is the AOP body of work crystallized over years, not the 1997 paper as a single coined phrase). Cleland-Huang & Gotel's *Software and Systems Traceability* (2012) confirmed to exist but does NOT contain a dedicated cross-cutting-concerns framework — supports ADR-005 Option 2 dismissal. No deprecations / quotas affect this slice (markdown prose pinning, not runtime tech). 5 web queries used (within budget).

Sources cited by Critic:
- [Aspect-oriented programming - Wikipedia](https://en.wikipedia.org/wiki/Aspect-oriented_programming)
- [Cross-cutting concern - Wikipedia](https://en.wikipedia.org/wiki/Cross-cutting_concern)
- [Aspect-oriented programming | Springer Nature Link (ECOOP 1997 chapter)](https://link.springer.com/chapter/10.1007/BFb0053381)
- [Software and Systems Traceability | Springer Nature Link (Cleland-Huang & Gotel 2012)](https://link.springer.com/book/10.1007/978-1-4471-2239-5)
- [Software and Systems Traceability | Semantic Scholar](https://www.semanticscholar.org/paper/Software-and-Systems-Traceability-Cleland-Huang-Gotel/eddc33ca1a3669b92699fd98e3aed705a6d7ccb5)

## Triage

**Triaged by**: user
**Date**: 2026-05-10
**Final verdict**: NEEDS-FIXES

Mechanically computed: 1 ACCEPTED-PENDING (M1) + 0 ESCALATED + 10 ACCEPTED-FIXED → NEEDS-FIXES (per TRI-1: any ACCEPTED-PENDING && no ESCALATED → NEEDS-FIXES).

User accepted all Builder draft dispositions in a single "accept all" ratification at 2026-05-10. ACCEPTED-FIXED items have been applied to mission-brief.md, design.md, and ADR-005 in this slice's folder; M1's ACCEPTED-PENDING fix executes at /build-slice T-late.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Option A back-sync (installed→in-repo for the Dim 1 + Dim 4 surgical sub-bullets) is now the slice's first build-time action ("What's new" item 0 in design.md); 2 new prose-pin tests `test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet` + `test_critique_dim_4_has_methodology_audit_conformance_sub_bullet` added to design.md test plan; AC #1 extended in mission-brief.md to require these sub-bullets present in-repo. |
| B2 | Blocker | ACCEPTED-FIXED | New test `test_critique_dim_9_cross_references_resolve` added to design.md test plan (asserts each "see Dim N" pointer paired with actual sub-bullet text); AC #2 extended in mission-brief.md to require resolution; verification plan row 2 carries the explicit substring-pairing assertions. |
| M1 | Major | ACCEPTED-PENDING | Design.md "Empirical verification at design-time" item 3 rewritten — replaces "verified by mental simulation" with the build-time exercise plan: spawn 1 Critic re-critique of slice-005's archived design.md against the new 9-dim Critic at /build-slice T-late; capture finding count + framing in build-log.md. Mission-brief must-not-defer carries the same. ONE finding → empirical confirm; TWO findings → escalate at validate-time. |
| M2 | Major | ACCEPTED-FIXED | Design.md "Out-of-repo files touched" section restructured into Phase 1 (installed→in-repo back-sync, T-early) + Phase 2 (in-repo→installed forward-sync, T-final); mission-brief must-not-defer captures bidirectional sha256 trace requirements. Discovered class (structural in-repo↔installed gap) added to design.md INST-1 bullet + Out-of-scope; tracked for slice-007+ candidate. |
| M3 | Major | ACCEPTED-FIXED | Design.md Dim 9 body shape "What's new" + ADR-005 Decision section + ADR-005 Options Considered Option 3 — all updated to: "the AOP body of work originating with Kiczales et al. (1997 ECOOP), where 'cross-cutting concerns' became a frozen term-of-art within ~2-3 years of the original paper". |
| M4 | Major | ACCEPTED-FIXED | Mission-brief mid-slice smoke gate PowerShell block extended with `pytest tests/methodology/test_methodology_changelog.py::test_version_matches_most_recent_changelog_entry`; must-not-defer carries VERSION-changelog atomicity. |
| M5 | Major | ACCEPTED-FIXED | ADR-005 Reversibility section restructured: split into "What can be reverted (mechanical)" + "Items that cannot be reverted (irreversible portion)" + "Cost summary". In-context-conditioning paragraph moved from Consequences to Reversibility for prominence. "Expensive" tag retained (the additive structural-revert is expensive but not strictly irreversible across all surfaces — only the historical-record portion is irreversible). Cost summary closes with "refinement, not revert" guidance. |
| m1 | Minor | ACCEPTED-FIXED | Design.md "What's new" item 6: "Six" → "Seven". |
| m2 | Minor | ACCEPTED-FIXED | Design.md test additions section + ADR-005 Consequences both updated to require docstring update ("all eight review dimensions" → "all nine review dimensions") in lock-step with the test rename. |
| m3 | Minor | ACCEPTED-FIXED | Design.md "What's reused" INST-1 bullet extended with "Known gap (per Critic m3, /critique 2026-05-10): tools/install_audit.py checks file existence only, not content equality..." note + future-slice candidate references; mission-brief Out-of-scope carries the deferred structural fix. /reflect Discovered entry at slice-006 close. |
| m4 | Minor | ACCEPTED-FIXED | Mission-brief mid-slice smoke gate PowerShell block extended with the prose-parity sweep one-liner counting `8 dimensions` occurrences across `agents/`, `skills/`, `plugin.yaml`, `tutorial-site/`. |
