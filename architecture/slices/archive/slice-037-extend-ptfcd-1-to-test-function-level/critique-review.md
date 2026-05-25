# Critique Review: Slice 037 extend-ptfcd-1-to-test-function-level

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-17
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's eight findings (B1/B2/B3, M1/M2/M3, m1/m2) are all VALID with correct severities, and the Builder's in-round ACCEPTED-FIXED dispositions genuinely resolve them without flaw-relocation — empirically verified (regex tested against the live adversarial corpus; rule-ID convention confirmed against `methodology-changelog.md`). However, the first Critic missed two real Majors plus two Minors: (1) the slice's own AC4 TF-1 row was a **tautological green** — it cited the pure CAD-1 byte-equality test, which passes even if the Dim 9 function-level refinement is entirely absent; (2) design under-specified row 37's Machine-cmd and created an un-flagged **second-order recursive self-application** (the slice's own new audit vs its own new catalog row); (m-add-1) the M2 fix silently extends `AuditResult.to_dict()`'s JSON contract with no contract note; (m-add-2) M3 left the both-columns-disagree case unstated.

## Confirmed findings

- **B1** (own AC4 phantom test-function): VALID, **Blocker** appropriate. `test_critique_agent_drift.py:62` proves only `test_in_repo_and_installed_critique_agent_are_content_equal` exists; the original citation was a phantom. Post-fix row cites the real name — fix VALID, no relocation.
- **B2** (prose `test_function` false-positive): VALID, **Blocker** appropriate. Post-fix regex empirically REJECTS slice-034's `(full existing module — non-regression)` + all prose, ACCEPTS all real identifiers incl. `test_x[param]`. Zero false-accept/reject on the live corpus. Not hand-waved.
- **B3** (rule-ID `-D` vs `vN.N`): VALID, **Blocker** appropriate. `methodology-changelog.md` independently confirms the partition; TFFL-1 v0.48.0 says "new minted rule-ID refines TF-1 in place, supersedes nothing". `PTFFD-1` well-formed; ADR-038 matches the TFFL-1↔TF-1 precedent. Fix VALID.
- **M1** (SCPD-1 catalog propagation): VALID, **Major** appropriate. (Under-delivery at design stage → M-add-2.)
- **M2** (ADR-037 observability undelivered): VALID, **Major** appropriate. (Residual dataclass contract → m-add-1.)
- **M3** (`_resolve_test_path` `::`-strip escape): VALID, **Major** appropriate. (Residual both-columns case → m-add-2.)
- **m1** (`PhantomCitation.kind` legacy default unpinned): VALID, **Minor** appropriate.
- **m2** (async/nested thinly tested): VALID, **Minor** appropriate.

## Suspicious findings

None. All eight first-Critic findings are VALID with correctly-filed severities; every Builder fix was empirically verified to resolve the finding without relocating the defect class one layer deeper (the slice-030A/031/032 flaw-relocation pattern was actively probed for B1/B2/B3 and not found).

## Missed findings

- **M-add-1: AC4 was a tautological green** (severity: **Major**). The cited `test_in_repo_and_installed_critique_agent_are_content_equal` (`test_critique_agent_drift.py:62-81`) is a pure CAD-1 byte-equality subprocess check — it passes whether or not the Dim 9 function-level refinement exists, as long as in-repo == installed. AC4's stated deliverable had no verifying test. The slice-025 content-pin precedent (`test_critique_dim_9_phantom_test_file_citation_*`, `test_critique_agent.py:1012+`) is the established pattern AC4 should use. **Builder draft**: ACCEPTED-FIXED — AC4 reworded; TF-1 plan gains content-pinning rows `test_critique_dim_9_phantom_citation_function_level_layer_present` + `test_critique_dim_9_phantom_citation_names_ptffd_1_rule_id` in `test_critique_agent.py`; CAD-1 byte-equality kept as a separate (necessary-but-insufficient) AC4 row.
- **M-add-2: row 37 under-specified + un-flagged second-order self-application** (severity: **Major**). design.md said only "add row 37"; SCPD-1 + slice-025 precedent demand the Machine-cmd selectors be named at design stage. Further, the slice's own newly-live function-level `shippability_path_audit` runs against `shippability.md` at `/validate-slice` Step 5.5 — row 37's own selectors must resolve at the function level or the slice trips its own new audit (B1's class one order up). **Builder draft**: ACCEPTED-FIXED — design.md enumerates row 37's exact Machine-cmd; mission-brief verification plan #6 + a build-ordering constraint in the smoke gate require row 37 + entry-pins added LAST, after the cited test files/functions exist.
- **m-add-1: M2 fix silently extends `AuditResult.to_dict()` JSON contract** (severity: **Minor**). `AuditResult` (non-frozen, `test_first_audit.py:122`) gains `skip_notes`; `to_dict()` (asdict, L130) extends the `--json` shape — same additive-contract concern as the first Critic's own m1 for `PhantomCitation`, missed for the symmetric `AuditResult` case. **Builder draft**: ACCEPTED-FIXED — design.md Contracts notes the additive `skip_notes` key (no removed key) + key-superset assertion on the skip-note test row.
- **m-add-2: M3 both-columns-disagree case unstated** (severity: **Minor**). When `test_path::test_a` and `test_function=test_b` both checkable but differ, function-column wins implicitly. Safe choice but unstated. **Builder draft**: ACCEPTED-FIXED — design.md error model + ADR-037 now state: function column wins, path-column selector not separately validated (authoritative-field, conservative).

## Severity adjustments

None. B1/B2/B3 correctly Blockers, M1/M2/M3 correctly Majors, m1/m2 correctly Minors. The first Critic's BLOCKED verdict was warranted at review time (pre-fix B1/B2 are genuine blockers). Post-TRI-1, if all twelve dispositions (8 first-Critic + 4 meta) hold as ACCEPTED-FIXED, the verdict mechanically becomes CLEAN — all are design-stage-fixable and were fixed in-round. No inflation.

## Notes

Confidence high — Blocker fixes were empirically executed, not reasoned about (B2 regex run against the live archived corpus; B3 convention cross-checked against `methodology-changelog.md`). The first Critic's two standing blind spots (audit-self-violation; RULE-ID/entry-pin) were both caught this round (B1/B3). The two new Majors are one layer deeper: M-add-1 is verification-vacuity (the AC's verifier cannot fail when the AC is unmet — distinct from B1's phantom-citation class), M-add-2 is the second-order catalog-self-application (B1 at the TF-1-plan layer recurs at the catalog layer the first Critic's M1 touched but did not trace). Both align with the project's strongest standing lesson (`_index.md:54-55`): the dual-Critic stack under-reaches the audit-vs-its-own-artifact interaction.
