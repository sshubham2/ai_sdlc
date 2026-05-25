# Critique: Slice 036 fix-rr1-audit-status-filter

**Critic reviewed**: mission-brief.md, design.md, ADR-036
**Date**: 2026-05-17
**Result**: NEEDS-FIXES
**Critic**: spawned `critique` agent (Standard mode, medium tier, critic-required:true — in-house methodology surface `tools/risk_register_audit.py`). Agent performed empirical file verification (read `risk_register_audit.py`, `risk-register.md` R-9, `cross_spec_parity_audit.py`, both consumer SKILL.md, fixtures, prior-slice precedents).

## Summary

Core fix sound, minimal, well-targeted; `view`-removal safety independently re-verified by grep (only producer L420, no consumer). But the mission-brief Intent overstated the defect's impact in contradiction to the authoritative R-9 register entry (B1), and CSP-1 was mis-cited as the consumer-parity mechanism though it is a Heavy-mode-only no-op here (B2). Both are vault-drift / unfounded-claim blockers. Two majors on test-oracle coverage; two cheap minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: Mission-brief Intent contradicts the authoritative R-9 register entry on current-impact
- **Claim under review**: Intent — *"This corrupts risk-driven slice selection — the pipeline's own steering signal."*
- **Issue**: `architecture/risk-register.md` L170/L172 (authoritative) states the opposite: *"Current consumers are unaffected … correct today"*, *"Impact in practice: low — no current correctness impact"*. Verified consumers (`skills/pulse/SKILL.md` L40, `skills/slice/SKILL.md` L45-49) read the per-risk `status` field, not filter membership. The bug is a **latent footgun**, not live corruption. Risks reflection.md asserting a false "fixed live corruption" R-9-retirement claim.
- **Evidence**: `risk-register.md` L162-174; `skills/pulse/SKILL.md` L40; `skills/slice/SKILL.md` L42-49.
- **Proposed fix**: Rewrite Intent / design Context / ADR-036 Context to R-9's "latent footgun, no current correctness impact, proactive retirement" framing. Technical fix unchanged.
- **Builder draft**: ACCEPTED-FIXED — verified B1 against `risk-register.md` L170/L172 directly (Critic correct). Rewrote mission-brief Intent + `Risk retired` line, added design.md impact-framing blockquote, rewrote ADR-036 Context. No technical change.

#### B2: CSP-1 mis-cited as the consumer-parity mechanism (CSP-1 is Heavy-mode-only, unrelated)
- **Claim under review**: AC #4 / Must-not-defer / design.md note / ADR-036 Consequences all attribute consumer parity to "(CSP-1)".
- **Issue**: `tools/cross_spec_parity_audit.py` L1-12 — CSP-1 walks Heavy-mode `threat-model.md`/`requirements.md`/`nfrs.md` and is a no-op in Standard mode (this project: `triage.md` L4 `mode: STANDARD`). It cannot catch skill-prose↔JSON parity; it passes vacuously. The slice leaned on an audit structurally unable to reach the regression class AC #4 names.
- **Evidence**: `tools/cross_spec_parity_audit.py` L1-46; `architecture/triage.md` L4/L13.
- **Proposed fix**: Strike every "(CSP-1)"; replace with the real mechanism — prose-pin tests `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1`, the AC #4 contract-pin tests, and an explicit manual `/build-slice` + `/validate-slice` SKILL.md re-read.
- **Builder draft**: ACCEPTED-FIXED — verified B2 against `cross_spec_parity_audit.py` L1-12 (Heavy-only, confirmed). Struck all CSP-1 attributions from mission-brief AC #4 / Must-not-defer / Dependencies / Pre-finish, design.md Consumer-parity note, ADR-036 Consequences; named the actual enforcement mechanism in each.

### Majors (address this slice)

#### M1: No-flag `--json` ordering change asserted but not regression-pinned
- **Issue**: Post-fix unfiltered `out["risks"]` becomes `filter_and_sort` score-desc order vs pre-fix register order. Design/ADR acknowledge it but no Test-first row pins it; a future maintainer could "restore register order" with no failing test.
- **Evidence**: `risk_register_audit.py` L419 (register order) vs L410-416 (score default); Test-first plan had no no-flag-ordering row.
- **Proposed fix**: Add an AC #4 Test-first row pinning no-flag consumed-`risks` = score-desc-then-id.
- **Builder draft**: ACCEPTED-FIXED — added Test-first row `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id` (AC #4, PENDING) + design.md Contracts "Error cases" pin note + ADR-036 Consequences pin reference. TPHD-1 harmonized (mission-brief TF-1 plan + design.md same fix block).

#### M2: Band/top leak under-covered by a stable oracle; real-register test fragile
- **Issue**: Repro covers only `--filter-status open` on `clean_register.md`; the defect class also spans `--filter-band`/`--top`. AC #2's only band/top guard was split into a real-register test bound to mutable vault state (fragile — every risk add/retire shifts counts; violates slice-004 real-file-scoping discipline).
- **Evidence**: repro L248-252 (status-only fixture); `clean_register.md` (4 risks span bands/statuses); `test_risk_register_audit_real_file.py` slice-004 precedent (pins only stable invariants).
- **Proposed fix**: Band/top test runs against the fixture with a stable oracle (`--filter-band high`→{R1,R3}; `--top 2 --sort score`→exactly 2 score-desc); real-register test asserts only the invariant (zero non-`open` under `--filter-status open`), no count/ordering.
- **Builder draft**: ACCEPTED-FIXED — split AC #2 into `test_json_filter_band_and_top_applied_to_consumed_risks_fixture` (stable fixture oracle) + `test_json_filter_status_open_excludes_non_open_real_register_invariant` (invariant-only, slice-004-scoped); added explicit "Test oracle scoping" subsection to mission-brief. TPHD-1 harmonized.

### Minors (log; address if cheap)

#### m1: design.md / ADR-036 stale-line-number robustness
- **Issue**: "L418–421" is currently accurate but a literal line number in a design doc drifts on any edit above it.
- **Builder draft**: ACCEPTED-FIXED — re-anchored design.md + ADR-036 references to the symbol `main()` `if args.json:` branch (thin-vault convention).

#### m2: AC #3 no-regression gate command not named
- **Issue**: TF-1 carve-out for AC #3 is correct (slice-004 precedent) but the gate command was unnamed.
- **Builder draft**: ACCEPTED-FIXED — named `python -m pytest tests/methodology/test_risk_register_audit.py -q` in AC #3, Mid-slice smoke gate, and Pre-finish gate.

## Dimensions checked
- [x] Unfounded assumptions — **B1** (Intent vs authoritative R-9). Critic read `risk_register_audit.py` directly; confirmed L419-420 exact defect, ~2-line fix.
- [x] Missing edge cases — **M1** (no-flag ordering unguarded), **M2** (band/top under-covered, real-register fragility). Empty/legacy/missing-file paths verified unchanged.
- [x] Over-engineering — none. Fix genuinely minimal; dropping redundant dual-list is anti-speculative.
- [x] Under-engineering — **M1/M2**. Repro genuineness verified (asserts consumed key; FAIL pre-fix / PASS post-fix; `rc==0` asserted separately so import/parse error can't masquerade).
- [x] Contract gaps — JSON shape change explicit; exit-code/violations verified unchanged (L425); `summary` register-wide invariant verified (`to_dict()` L119-137 over `self.risks`, untouched).
- [x] Security — none (local CLI, no auth/input boundary beyond argparse path).
- [x] Drift from vault — **B1**, **B2**. ADR-036 contradicts no prior ADR. `view`-removal VALIDATED by grep.
- [x] Web-known issues — none (self-contained internal CLI; no external API/SDK/platform surface).
- [x] Cross-cutting conformance — **B2** headline (methodology-audit-ID mis-attribution). slice-022 self-violation law observed: the slice's own mission-brief committed a vault-conformance defect (B1) while fixing a contract-conformance defect. Algorithm-path-conformance traced (filter_and_sort branches compose correctly); tooling-doc-vs-impl parity verified (docstring L38-44 vs argparse L383-405 consistent).

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

(User ratified all 7 findings — 6 first-Critic + M-add-1 meta-Critic, DR-1 EXTEND — as the Builder drafts: all ACCEPTED-FIXED. Mechanical verdict: only ACCEPTED-FIXED dispositions → CLEAN.)

| ID | Severity | Disposition (Builder draft) | Rationale |
|----|----------|------------------------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Verified vs `risk-register.md` L170/L172; Intent/design/ADR reframed to "latent footgun, no current correctness impact" |
| B2 | Blocker  | ACCEPTED-FIXED | Verified vs `cross_spec_parity_audit.py` L1-12 (Heavy-only no-op); CSP-1 struck everywhere, real mechanism named |
| M1 | Major    | ACCEPTED-FIXED | No-flag ordering pin test added (AC #4); TPHD-1 harmonized |
| M2 | Major    | ACCEPTED-FIXED | Band/top → fixture stable oracle; real-register → invariant-only (slice-004 scoping); TPHD-1 harmonized |
| m1 | Minor    | ACCEPTED-FIXED | Re-anchored to symbol `main()` `if args.json:` branch |
| m2 | Minor    | ACCEPTED-FIXED | No-regression gate command named in AC #3 + gates |
| M-add-1 | Major (meta-Critic, DR-1 EXTEND) | ACCEPTED-FIXED | Verified vs `test_risk_register_audit.py` L356-381 — `*_references_rr_1` tests pin only bare RR-1/module substring, NOT flag/prose. Added durable `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` (AC #4, option a); corrected over-claim in mission-brief/design/ADR; TPHD-1 harmonized |
