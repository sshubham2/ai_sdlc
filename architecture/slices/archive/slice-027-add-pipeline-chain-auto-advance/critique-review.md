# Critique Review: Slice 027 add-pipeline-chain-auto-advance

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-16
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is fact-solid: every B/M/m claim verifies against disk, the in-round fixes are consistent and introduce no new defect (the slice-026 M-add-1 "fix-block creates a new unguarded surface" lesson does not recur — the new drift test is itself a guard following the `tests/methodology/test_<name>.py` convention). But the Contract-gaps dimension was under-applied: the design enumerates *named user-input gates* thoroughly while leaving two clean-path edge cases in the auto-advance runtime contract unaddressed — `/validate-slice` PARTIAL and the `/critique` `auto-advance: true` vs. its conditional `## Next step` semantics.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (`tests/tools/` → `tests/methodology/`) — confirmed; `ls tests/` yields only `methodology/ skills/ README.md`; all `_CANONICAL_TOOLS` peers live at `tests/methodology/`. Blocker appropriate (PTFCD-1 class, drives a WIRE-1 row). Fix consistent on disk.
- **B2** (`architecture/ai-sdlc-VERSION` nonexistent) — confirmed; canonical PMI-1 triad = in-repo `VERSION` + installed `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`. Blocker appropriate. Fix consistent (AC#5/row5/MND#4).
- **M1** (7-pair forward-sync mitigation asserted-not-demonstrated) — confirmed; `install_audit` existence-only on installed skill dirs. Major appropriate. Fix (`test_pipeline_position_block_drift.py`, 8-pair parametrized, section-scoped) is the correct minimal element, no convention break.
- **M2** (AC#5 Wiegers traceability over 8 files, element for 1) — confirmed; discharged 1:1 by the M1 element. Major appropriate.
- **M3** (gate-enumeration completeness, must-not-defer #1) — confirmed; the per-skill table is accurate against real prose (`slice` SKILL.md:131-132, `design-slice`:255, `critique-review`:15/104, `reflect`:344-346). No skill's Critical-rules prose contradicted. Major appropriate.
- **m1** (ADR-025 L17 "two Next step blocks") — confirmed reworded; non-blocking.
- **m2** (new-tool propagation sentinel N=5) — confirmed; `install_audit.py:66` "19 tool modules post-slice-026" comment exists exactly as cited; design.md propagation checklist complete. Minor appropriate.

## Suspicious findings

None. Every first-Critic finding survived independent fact-checking against disk; none is over-reach or already-addressed.

## Missed findings

- **M-add-1 (Major): `/validate-slice` PARTIAL is an unenumerated clean-path state in the auto-advance contract.** `skills/validate-slice/SKILL.md` defines a 3-valued per-criterion outcome PASS|PARTIAL|FAIL and an aggregate `Result: PARTIAL`. The gate table / canonical enumeration enumerated only "any per-criterion FAIL → HALT". PARTIAL is neither a provable clean PASS nor an enumerated FAIL. The fail-closed catch-all *technically* covers it, but M3's own ratified principle ("explicit, not catch-all-reliant") makes the silent omission the exact same defect class as M3, one row down. The first Critic fixed M3 for `/critique-review`//`/slice`//`/design-slice` but did not re-scan the table it was ratifying for the `validate-slice` PARTIAL hole. **Fix applied**: `validate-slice` PARTIAL → HALT row added to design.md§authorization table + ADR-025 canonical gate enumeration (same disposition as FAIL).

- **m-add-1 (Minor): `/critique` `auto-advance: true` under-specifies the conditional/self-loop successor.** `skills/critique/SKILL.md:293-294` `## Next step` is conditional (`CLEAN/NEEDS-FIXES → /build-slice`; `BLOCKED → re-run /critique`). The flat `**successor**: <skill>` schema field models only the primary edge. No safety hole (TRI-1 HALT dominates — auto-advance never fires from `/critique` without a user pass-through), hence Minor; but a latent audit false-positive risk at `/build-slice` Step 6 if the Builder hard-codes a single-successor expectation. **Fix applied**: design.md§contracts now states verdict-dependent successors express the conditional in the `on-clean-completion` field and the audit must tolerate the documented `/critique` BLOCKED self-edge.

## Severity adjustments

None. B1/B2 (Blocker), M1/M2/M3 (Major), m1/m2 (Minor), m3 (Minor, ACCEPTED-PENDING) all correctly filed. m3 correctly NOT a slice-027 blocker — deferred slice-028 function-level-PTFCD-1 candidate; routing to `/reflect` as corroborating evidence is the right disposition.

## Notes

High confidence — every first-Critic claim independently disk-verified and held; fixes consistent and non-regressing (slice-026 M-add-1 fix-block-creates-new-surface risk specifically checked, does not recur). Calibration observation: first Critic's factual accuracy excellent (8/8 verified true), but a narrow blind-spot pattern — having opened the M3 "enumeration must be explicitly complete" thread it did not re-scan the *full* gate table for sibling omissions, missing the `validate-slice` PARTIAL row one line below the FAIL row it discussed. Same dimension (missing-edge-cases / contract-gaps) the first Critic marked "none beyond M3"; M-add-1 sits squarely inside M3's own ratified principle → rated Major not informational.
