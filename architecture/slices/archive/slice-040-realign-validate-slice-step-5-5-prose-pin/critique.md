# Critique: Slice 040 realign-validate-slice-step-5-5-prose-pin

**Critic reviewed**: mission-brief.md, design.md, new ADRs (none — design explicitly mints no ADR)
**Date**: 2026-05-18
**Result**: NEEDS-FIXES (Critic) → all findings ACCEPTED-FIXED pre-triage (see Builder drafts + Triage)

## Summary

The Critic verified the core mechanical claims against real artifacts and found them sound:
both proposed anchors exist verbatim in `skills/validate-slice/SKILL.md` (L216, L213), both
are genuinely absent from the pre-SRSC-1 slice-031 state (git SHA `18f1215` — proven
non-tautological), the BFRD-1 failing-repro premise is live (`1 failed, 3 passed`), and the
catalog-absence claim is substantively correct. **No blockers.** Two majors + two minors, all
on the changelog-entry shape. Builder verification (per the project's "recompute the claim, not
reason about it" discipline) found the deeper root: the cited slice-036/R-9 conformance-fix
precedent added **no changelog entry at all** — the correct fix is to drop the changelog entry
entirely, which dissolves both majors.

## Findings

### Blockers (must address before /build-slice)

None. The design's load-bearing premises survive mechanical verification.

### Majors (address this slice)

#### M1: Proposed `### Fixed` changelog heading does not exist in the changelog's actual convention
- **Claim under review**: design.md "What's new" — "A `### Fixed` entry in methodology-changelog.md recording the realignment + R-10 retirement."
- **Issue**: Every `### ` heading in `methodology-changelog.md` is `### Added` (47×) or `### Changed` (6×); the template line L24 reads `### Added | Changed | Retired`. **No `### Fixed` precedent anywhere.** Introducing a novel heading vocabulary in a conformance-fix slice is unjustified divergence (Brownfield rule: respect existing conventions; deviations need an ADR — and this slice mints none).
- **Evidence**: `grep -oE "^### [A-Za-z]+" methodology-changelog.md | sort -u` → only `Added`/`Changed`; changelog template L24 says `Retired`, not `Fixed`.
- **Proposed fix (Critic)**: use `### Changed` or `### Retired`; do not introduce `### Fixed`.
- **Builder draft**: **ACCEPTED-FIXED** at design.md "What's new" + "Decisions made" + mission-brief AC5/verification-row-5/must-not-defer/out-of-scope. The fix is *deeper* than the Critic's proposal and I verified why: `grep "slice-036\|R-9\|ADR-036" methodology-changelog.md` → **0 real matches**. The cited conformance-fix precedent slice-036 (R-9, no VERSION bump) added **no changelog entry at all** — it recorded retirement in `risk-register.md` L170 `**Retired**:` line + ADR-036. The changelog's `### Added`/`### Changed` headings are nested under `## vN.N.N — date` version headings; a no-VERSION-bump fix has no `## v` parent, and META-1 (`test_each_changelog_entry_carries_rule_reference`) splits on `^## v\S+ — date` so a parentless `###` entry is invisible to META-1 or pollutes slice-039's `## v0.52.0` block. **Correct fix = drop the changelog entry entirely**, recording R-10 retirement in the `risk-register.md` `**Retired**:` line (mirroring R-9 L170) + the realigned test docstring. Strictly more precedent-faithful than re-heading. Applied to design.md + mission-brief (TPHD-1 harmonization done in the same fix block).

#### M2: New changelog entry's META-1 `Rule reference` obligation is unspecified
- **Claim under review**: design.md — the changelog entry with no `Rule reference` line specified.
- **Issue**: slice-029 lesson (in this slice's own context): "Each changelog entry must carry a `Rule reference` line — even rule-ID-less entries." The design specified none. Per the slice-022 self-violation law, pre-decide at design time.
- **Evidence**: `tests/methodology/test_methodology_changelog.py` META-1 splits on `## v`; design specified no `Rule reference` line.
- **Proposed fix (Critic)**: specify `Rule reference: SCMD-1` and/or `SRSC-1`; decide the entry's `## v` parent.
- **Builder draft**: **ACCEPTED-FIXED (subsumed by M1's fix)**. With no changelog entry, META-1 has nothing to parse and the slice-029 per-*entry* discipline is vacuously satisfied (no entry → no obligation). The SCMD-1→SRSC-1 lineage M2 wanted captured is instead carried in (a) the realigned test docstring (AC3) and (b) the R-10 `**Retired**:` line. Removing the entry is the correct way to satisfy M2's underlying concern, not bolting a `Rule reference` onto a divergent parentless entry. Recorded in design.md "What's new" + "Decisions made".

### Minors (log; address if cheap)

#### m1: Recursive-self-application — watch-list note must land at the canonical surface, not just design.md prose
- **Claim under review**: design.md "Decisions made" — "Recorded in the changelog `### Fixed` entry as a `/critic-calibrate` watch-list candidate."
- **Issue**: The scoping decision (decline the `-D` rule at N=1; backstop = slice-039 BC-PROJ-4) is sound and matches slice-017/slice-020 deferral precedent. But the watch-list note must materialize where `/critic-calibrate` actually mines it.
- **Builder draft**: **ACCEPTED-FIXED** at design.md "Decisions made". With the changelog entry removed (M1), the N=1 `/critic-calibrate` watch-list note now lands in the **R-10 `**Retired**:` line** + this slice's `reflection.md` "Critic calibration"/deferred section — the surfaces `/critic-calibrate` reads (it mines reflections + calibration log, not the changelog). Strictly better placement than the original.

#### m2: "grep count 0" method imprecise (conclusion correct; stated method false-positives)
- **Claim under review**: design.md — "No shippability-catalog reference exists (R-10: grep count 0)."
- **Issue**: bare `grep "test_validate_slice_skill" architecture/shippability.md` → count **1** (substring false-positive on `test_validate_slice_layers.py`'s `..._documents_imports_allowlist_...` row, a different file/function). The substantive conclusion is correct (exact file+function tokens → 0); the stated method is loose.
- **Builder draft**: **ACCEPTED-FIXED** at design.md "Realignment specifics — Function NOT renamed". Now cites the disambiguated grep: `grep -c "test_validate_slice_skill.py" architecture/shippability.md` → 0 AND `grep -c "test_step4_5_5_consumes_machine_stable_command" architecture/shippability.md` → 0. Behavior unchanged; precision only.

### Meta-Critic missed finding (from /critique-review — DR-1 EXTEND)

#### M-add-1: MEPD-1 — the directly-governing rule (minted slice-039, prior slice) not invoked by name
- **Claim under review**: design.md §"Decisions made" no-changelog-entry bullet — justified the no-entry decision via the slice-036/R-9 precedent + META-1 split mechanic, but never named MEPD-1.
- **Issue**: slice-039 minted **MEPD-1** (Methodology-surface Entry-Pin Discipline, Dim 7) one slice ago precisely for the "no changelog entry because…" decision class. Its (b) branch requires the why-none be *verified against the actual `test_methodology_changelog.py` enforcing assertion*, never resting on a Builder-asserted prior-slice precedent (the slice-032 false-precedent guard). The substance was already MEPD-1(b)-compliant (design.md independently verified the META-1 `^## v` split), but neither Critic layer nor the Builder cited MEPD-1 by name — a recursive-self-application gap on the *first* slice MEPD-1 governs. Severity: Major-class methodology-discipline gap (no correctness/false-gate consequence — 659/1 suite, META-1 green, VERSION lockstep at 0.52.0; only the discipline-trail was incomplete).
- **Evidence**: methodology-changelog.md L39 (MEPD-1 mint); MEPD-1 content-pin `tests/methodology/test_critique_agent.py:1433-1446`; META-1 split at `tests/methodology/test_methodology_changelog.py:136`.
- **Proposed fix (meta-Critic)**: add one sentence to design.md §"Decisions made" explicitly discharging MEPD-1 branch (b) by name.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §"Decisions made" no-changelog-entry bullet — now names MEPD-1(b), cites the META-1 `re.split` enforcing assertion at `test_methodology_changelog.py:136` as the load-bearing why-none, and demotes slice-036/R-9 to corroborating (not load-bearing), explicitly invoking the slice-032 false-precedent guard. Closes the self-hosting discipline-citation gap; substance unchanged (was already compliant).

## Dimensions checked
- [x] Unfounded assumptions — Critic mechanically verified both anchors + both kept assertions exist verbatim; non-tautology proven via git history. No unfounded assumption. (m2 = imprecise method, correct conclusion.)
- [x] Missing edge cases — none material; EOL edge correctly dismissed (anchors carry no newline; conftest.read_file raw utf-8). Non-tautology proof mandated by AC2.
- [x] Over-engineering — none; single-function modification, no new module/ADR/rule-ID/VERSION bump. (Builder fix further *reduces* scope: no changelog entry.)
- [x] Under-engineering — M1/M2 (changelog entry shape) — resolved by dropping the entry, the precedent-faithful path.
- [x] Contract gaps — none; only "contract" is the prose-pin assertion message, which the design updates to name the SRSC-1 anchor.
- [x] Security — none; no runtime surface, test + vault-doc edits only.
- [x] Drift from vault — none material; R-10 entry + SCMD-1/SRSC-1 changelog entries corroborate the lineage. M1's `### Fixed` divergence resolved by removing the entry.
- [x] Web-known issues — N/A; zero external technology surface.
- [x] Cross-cutting conformance — META-1 (changelog) → resolved by no-entry; TF-1 N/A (BFRD-1 disposition sound, repro pre-exists); PTFCD-1 catalog-citation verified (function uncatalogued, no propagation obligation); recursive-self-application watch-list note relocated to canonical surface (m1).

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

User ratified all five dispositions as Builder-drafted ("accept all", 2026-05-18). All
dispositions ACCEPTED-FIXED → zero ESCALATED, zero ACCEPTED-PENDING → mechanically CLEAN.

| ID | Severity | Disposition | Rationale |
|----|----------|------------------------------|-----------|
| M1 | Major    | ACCEPTED-FIXED | Verified slice-036/R-9 precedent adds NO changelog entry; dropped the entry entirely (design.md "What's new"/"Decisions made" + mission-brief AC5/verif-5/MND/OOS, TPHD-1-harmonized). Deeper + more precedent-faithful than the Critic's re-head proposal. |
| M2 | Major    | ACCEPTED-FIXED | Subsumed by M1: no entry → META-1 vacuously clean, slice-029 per-entry discipline N/A. SCMD-1→SRSC-1 lineage carried in test docstring + R-10 Retired line. |
| m1 | Minor    | ACCEPTED-FIXED | `/critic-calibrate` N=1 watch-list note relocated from the (now-removed) changelog entry to the R-10 `**Retired**:` line + reflection.md — the surfaces /critic-calibrate actually mines. |
| m2 | Minor    | ACCEPTED-FIXED | design.md now cites the disambiguated grep (`.py` file token + function token, both 0); bare-substring false-positive on `test_validate_slice_layers.py` noted. Conclusion unchanged. |
| M-add-1 | Major (meta-Critic missed) | ACCEPTED-FIXED | design.md §"Decisions made" now names MEPD-1(b), cites META-1 `re.split` enforcing assertion at `test_methodology_changelog.py:136` as load-bearing why-none, demotes slice-036/R-9 to corroborating (slice-032 false-precedent guard). Substance was already compliant; closes the self-hosting discipline-citation gap. |
