# Critique: Slice 080 harden-bc1-critical-rules-exit-gate

**Critic reviewed**: mission-brief.md, design.md, ADR-072, repro `tests/bugs/test_bc1_critical_rule_exit_gate.py`, fixtures, shippability row #85, live `architecture/build-checks.md` + `~/.claude/build-checks.md`
**Date**: 2026-05-29
**Result**: NEEDS-FIXES

## Summary

The core mechanism is sound and the Critic verified it empirically (APED-1): `--strict` appends a `BuildCheckViolation` per unacknowledged applicable Critical rule, and the unchanged `return 1 if result.violations else 0` then yields exit 1; both repro tests pass under the design, no existing BC-1 test regresses. The findings are not in the audit logic — they are methodology-surface obligations the design under-specified (PMI-1 leg enumeration wrong + self-contradictory; version-sync test supersession + shippability propagation unplanned; shippability row #85 documented the rejected design; the slice's own Step 6 strict run fires on itself).

## Findings

### Blockers (must address before /build-slice)

#### B1: PMI-1 atomic-bump leg enumeration wrong in BOTH design.md and ADR-072, and self-contradictory
- **Issue**: design.md said "5-part (VERSION + plugin.yaml + paired entry-pin tests)"; ADR-072 implied a different set. Canonical 5 legs (verified at `tests/methodology/test_methodology_changelog.py` + changelog body) are: VERSION, plugin.yaml, **pyproject.toml [project].version (PVFS-1)**, `## v0.75.0` header, installed `~/.claude/ai-sdlc-VERSION (AVFS-1)`. Installed `~/.claude/methodology-changelog.md` (MCFS-1) is a SEPARATE obligation, not a leg. Entry-pin tests are a BC-PROJ-10 surface, not a PMI-1 leg. `pyproject.toml:20` is `0.74.0` and would fail the renamed sync test if unbumped.
- **Evidence**: `test_methodology_changelog.py` 5-leg anchors; `methodology-changelog.md` body; `pyproject.toml:20`; "stale N-part PMI-1 count drift" aggregated lesson.
- **Builder draft**: **ACCEPTED-FIXED** — design.md MEPD-1 bullet + ADR-072 Consequences corrected to the canonical 5 legs with MCFS-1 called out as separate; pyproject 0.74.0→0.75.0 + AVFS-1 sync added to the build plan.

#### B2: Version-sync test supersession (`_v_0_74_0` → `_v_0_75_0`) + shippability propagation + BC-PROJ-10 entry-pin pair entirely unplanned (SCPD-1 class)
- **Issue**: a v0.75.0 bump requires renaming `test_version_files_synchronized_at_v_0_74_0` → `_at_v_0_75_0` (four literal asserts updated) AND propagating that rename into the shippability row that cites the test name (else stale ref FAILs at /validate-slice Step 5.5). The BC-PROJ-10 paired entry-pin pair for v0.75.0 was also unplanned. None were named build steps.
- **Evidence**: `test_methodology_changelog.py:5221,5235`; `architecture/shippability.md` row citing the sync test; SCPD-1 / Dim-9 consumer-propagation sub-clause.
- **Builder draft**: **ACCEPTED-PENDING** — three named steps added to design.md "Build plan" (B2); executed in the SAME /build-slice block before the catalog run.

#### B3: slice-080's own Step 6 strict run exits 1 unless it acks BC-PROJ-3 + BC-GLOBAL-2 (RSAD-1 self-application)
- **Issue**: empirical audit on the slice-080 folder → `critical_applicable: 2`, applicable Critical = BC-PROJ-3 + BC-GLOBAL-2 (both `always:true` git-revert-discipline rules). Under the chosen design, the slice's own Step 6 strict run fails unless it passes `--ack-critical BC-PROJ-3 BC-GLOBAL-2`. Broader consequence: because these are always-on Critical rules, EVERY future slice must ack them — design + Step 6 prose must make the enumerate-then-ack pattern explicit.
- **Evidence**: empirical run (`critical_applicable: 2`); `architecture/build-checks.md:67-69` (BC-PROJ-3 Critical); `~/.claude/build-checks.md:46-48` (BC-GLOBAL-2 Critical); ADR-072 attestation flow.
- **Builder draft**: **ACCEPTED-FIXED** — design.md Build plan (B3) + ADR-072 "Standing acknowledgment consequence" record the concrete ack list + the per-slice enumerate-then-ack pattern; the build-log.md attestation itself is performed at /build-slice (the design surface is fixed now).

### Majors (address this slice)

#### M1: shippability row #85 documented the REJECTED blunt-count design (option 1), not the chosen acknowledgment design
- **Issue**: row #85 (written during /repro, before the design fork) described "exit 1 whenever critical_applicable > 0" — ADR-072 option 1, explicitly rejected. Its regression clause would falsely flag the correct acknowledged-clears-it behavior.
- **Evidence**: `architecture/shippability.md` row #85; ADR-072 (option 1 rejected, option 2 chosen).
- **Builder draft**: **ACCEPTED-FIXED** — row #85 rewritten to the acknowledgment contract (exit 1 on un-acked applicable Critical; exit 0 when all acked or none apply; default path byte-unchanged).

#### M2: lenient-ack is a silent-no-op surface (fail-CLOSED) — needs a diagnostic
- **Issue**: a typo'd/stale `--ack-critical` ID silently fails to match → rule stays unacknowledged → exit 1, with no signal distinguishing "forgot to ack" from "ack ID wrong." Fails CLOSED (red, fail-safe — lower severity than the R-7 fail-OPEN class), but must be diagnosable.
- **Evidence**: design lenient-ack note; R-7 silent-disable aggregated lesson (fail-OPEN sibling).
- **Builder draft**: **ACCEPTED-PENDING** — `_format_human` diagnostic pinned in design.md Build plan (M2): list unacknowledged-firing rule IDs + ack IDs that matched no applicable Critical rule. Implemented at /build-slice.

#### M3: append placement must be AFTER both project+global source loops, guarded by `if strict:`; repro only exercises a project-source rule
- **Issue**: `audit_slice` accumulates `result.applicable` across project AND global loops; the strict-append must run once over the full list before `return result`, else a global-source Critical (BC-GLOBAL-2) is missed (under-engineering vs AC#1). Default path must stay byte-identical.
- **Evidence**: `tools/build_checks_audit.py` `audit_slice` project+global loops; empirical BC-GLOBAL-2 (global-source Critical) applicable.
- **Builder draft**: **ACCEPTED-PENDING** — placement pinned in design.md Build plan (M3); a global-source-Critical unit test added at /build-slice.

### Minors (log; address if cheap)

#### m1: `--ack-critical nargs="*"` greediness in Step 6 wiring
- **Builder draft**: **ACCEPTED-PENDING** — SKILL.md Step 6 example places `--ack-critical <ids>` last; no code change (design.md Build plan m1).

#### m2: `BuildCheckViolation` L128 `kind` comment + L129 `severity` comment go stale
- **Builder draft**: **ACCEPTED-PENDING** — both comments updated when touching the class (design.md Build plan m2).

## Dimensions checked
- [x] Unfounded assumptions — B1 (PMI-1 legs), M3 (append placement). "exit 1 via unchanged L619" verified empirically.
- [x] Missing edge cases — M3 (global-source Critical not in repro); carry-over early-return verified exit 0; clean case verified exit 0.
- [x] Over-engineering — none. Acknowledgment-flag is the minimal completable option; reuses the sibling violations→exit-1 idiom; no new module.
- [x] Under-engineering — B1, B2, B3, M2.
- [x] Contract gaps — M1 (catalog documents rejected design); m1 (nargs greediness). Default-off path verified byte-equal-preserving.
- [x] Security — none (local methodology-audit CLI; ack IDs matched against a closed parsed-rule set; no eval/injection).
- [x] Drift from vault — M1, B1 (ADR-072 enumeration stale vs canonical anchor). BCSG-1 not previously minted; ADR-072 `supersedes: null` correct (refines BC-1 per TFFL-1/ADR-034).
- [x] Web-known issues — argparse `nargs="*"` greediness (Python docs + cpython#101990): real but non-triggering (no positionals); logged m1.
- [x] Cross-cutting conformance — APED-1 (Critic executed the mechanism vs the real artifact + adversarial battery: no-ack→1, ack→0, clean→0, global-source Critical, carry-over→0); MEPD-1 (INCLUDE posture correct, legs corrected B1); SCPD-1 (B2); RSAD-1 (B3); FBCD-1 ("5-part" count drift B1).

## Triage

**Triaged by**: user
**Date**: 2026-05-29
**Final verdict**: NEEDS-FIXES

Dual review: first-Critic NEEDS-FIXES (3B/3M/2m, all VALID per meta-Critic) + meta-Critic EXTEND (0 suspicious, 1 missed Minor m-add-1, 0 severity-wrong). User ratified all dispositions as drafted 2026-05-29.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §Decisions + ADR-072 Consequences corrected to canonical 5 PMI-1 legs; MCFS-1 marked separate; pyproject bump added to plan |
| B2 | Blocker | ACCEPTED-PENDING | design.md Build plan (B2): rename version-sync test → _v_0_75_0, propagate shippability ref, add BC-PROJ-10 entry-pin pair — executed at /build-slice |
| B3 | Blocker | ACCEPTED-PENDING | design.md Build plan (B3) + ADR-072 standing-ack consequence record ack list (BC-PROJ-3 BC-GLOBAL-2) + Step-6 enumerate-then-ack pattern; ack-invoke + build-log attestation at /build-slice |
| M1 | Major | ACCEPTED-FIXED | shippability row #85 rewritten to the acknowledgment contract |
| M2 | Major | ACCEPTED-PENDING | design.md Build plan (M2): `_format_human` lists unacknowledged-firing IDs + ack IDs matching no applicable Critical rule — at /build-slice |
| M3 | Major | ACCEPTED-PENDING | design.md Build plan (M3): append after both project+global loops, `if strict:` guarded; add global-source Critical unit test — at /build-slice |
| m1 | Minor | ACCEPTED-PENDING | design.md Build plan (m1): SKILL.md Step 6 example places `--ack-critical` last — at /build-slice |
| m2 | Minor | ACCEPTED-PENDING | design.md Build plan (m2): update BuildCheckViolation L128/L129 comments — at /build-slice |
| m-add-1 | Minor | ACCEPTED-FIXED | repro test docstrings rewritten to the acknowledgment contract (2nd surface of M1) |
