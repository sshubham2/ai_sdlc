# Critique: Slice 026 enforce-critique-review-prerequisite

**Critic reviewed**: mission-brief.md, design.md, ADR-024-crp-1-critique-review-prerequisite-discipline.md
**Date**: 2026-05-16
**Result**: BLOCKED (pre-triage) → CLEAN (post-fix, user-triaged)

## Summary

The core risk (structurally unenforced mandatory `/critique-review`) is real and correctly sourced from slice-025 L37; the BRANCH-1-modeled audit design is structurally sound. The Critic surfaced a blocking rule-ID naming contradiction (CRP**D**-1's `-D` suffix vs ADR-019's test-pinned non-`-D` audit-gate class), a blocking escape-hatch survival gap (milestone.md rewritten by Step 7b), and 4 majors + 2 minors. All 8 findings verified accurate against the cited evidence and ACCEPTED-FIXED at design time.

## Findings

### Blockers (must address before /build-slice)

#### B1: `-D` suffix on CRPD-1 contradicts ADR-019's test-pinned naming convention
- **Claim under review**: mission-brief AC3 / design.md / ADR-024: "rule-ID **CRPD-1**, `-D`-suffix per the RSAD-1 / EPGD-1 / SCPD-1 / TPHD-1 / FBCD-1 convention".
- **Issue**: ADR-019 L13 (accepted, active, not-superseded) reserves `-D` for `/critique`-time prose-heuristics with no programmatic audit, and places audit-enforced gates (BRANCH-1, BC-1, CAD-1, PMI-1, …) in a separate non-`-D` class. CRP-1 has `tools/critique_review_prerequisite_audit.py` — it is an audit-enforced gate. The `-D` suffix directly contradicts an active ADR without superseding it (Dim 7 / Dim 9 recursive-self-application class).
- **Evidence**: `architecture/decisions/ADR-019-branch-per-slice-workflow.md` L13 (verified verbatim); `methodology-changelog.md` L145 / L190 / L255.
- **Proposed fix**: Rename CRPD-1 → **CRP-1** across all surfaces; place in audit-enforced-gate class; conform to (not supersede) ADR-019.
- **Builder draft**: ACCEPTED-FIXED — verified ADR-019 L13 verbatim. Renamed CRPD-1→CRP-1 across mission-brief.md, design.md, ADR-024 (+ file slug, milestone.md, TF-1 test fn names). Naming-class corrected to audit-enforced/NON-`-D` per ADR-019 in all three artifacts; ADR-024 adds an explicit "conforms to ADR-019, does not supersede" note.

#### B2: milestone.md escape-hatch survival across build-slice Step 7b continuous rewrites unaddressed
- **Claim under review**: ADR-024: escape-hatch is a canonical line in `milestone.md`; design.md adds a Step 6 defense-in-depth re-run reading milestone.md again.
- **Issue**: `skills/build-slice/SKILL.md` Step 7b (L269-271) rewrites milestone.md continuously during execution. A free-form body line has no reserved home and can be clobbered between the prerequisite gate and the Step 6 re-run → false-refuse of a legitimately escape-hatched build (violates Must-not-defer "no false-refuse").
- **Evidence**: `skills/build-slice/SKILL.md` L269-271 (verified); ADR-024 (silent on Step 7b).
- **Proposed fix**: reserved location preserved by Step 7b, or scope the re-check to a Step-7b-stable source.
- **Builder draft**: ACCEPTED-FIXED — verified Step 7b L269-271. Escape-hatch moved from a free-form body line to the optional **`critique-review-skip:` frontmatter key** in milestone.md (structured home, Step-7b-preservable, frontmatter-keyed detection eliminates the m2 narrative false-positive too). ADR-024 Option 4 + Decision + Consequences rewritten; design.md adds the milestone.md-template + Step 7b "preserve the key" instruction; mission-brief AC2 + new Must-not-defer "Escape-hatch survives Step 7b".

### Majors (address this slice)

#### M1: "critique_review_audit refused at /validate-slice" premise not matching wiring
- **Issue**: `critique_review_audit` is invoked only from `skills/critique-review/SKILL.md` — zero refs in `/validate-slice`; it runs only *inside* `/critique-review` and cannot detect a *skip*. The mission-brief's causal claim is imprecise; the gap is wider than stated (no `/validate-slice` net).
- **Evidence**: `grep -rn critique_review_audit skills/` → sole hit `skills/critique-review/SKILL.md:92` (verified).
- **Builder draft**: ACCEPTED-FIXED — mission-brief Intent rewritten ("provides no skip-detection; there is no `/validate-slice`-side net; slice-025 caught only by AC4's hand-authored assertion failing"); design.md "What's reused" critique_review_audit note corrected. CRP-1 reframed as the *first* structural skip-detector.

#### M2: "First audit invoked at the prerequisite check" ordering claim is false
- **Issue**: `## Prerequisite check` L21-23 already has gating steps (critique.md BLOCKED/exists, TPHD-1) before any CRP-1 placement. "FIRST audit" is inaccurate and load-bearing for nothing; ordering vs the critique.md-exists check is a real dependency (no critique-review without critique).
- **Evidence**: `skills/build-slice/SKILL.md` L17-27 (verified).
- **Builder draft**: ACCEPTED-FIXED — design.md drops the "FIRST audit" claim; specifies deterministic placement: after L22 critique.md-exists gate and after L23 TPHD-1 paragraph, before `### Branch state`, with dependency-ordering rationale stated (stable mini-CAD target).

#### M3: install_audit.py stale comment + roll-up sentinel double-meaning not enumerated
- **Issue**: `install_audit.py` L66-71 comment already stale ("17"); the UTF8 sentinel `assert len(actual_audits)==18` counts the `tools/*.py` glob, an *independent* counter from `_CANONICAL_TOOLS` (coincidentally both 18). design.md propagation list omitted the stale comment and conflated the counters.
- **Evidence**: `tools/install_audit.py` L66-71 vs L72-91; `tests/methodology/test_utf8_stdout_regression.py` L213-219 (verified).
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" propagation bullet now explicitly lists the L66-71 stale comment as a propagation site and notes the two counters are independent (both move 18→19 this slice for different reasons; future divergence must not be masked).

#### M4: Self-application (RSAD-1) recursive ordering hazard — CRP-1 cannot self-gate its own build
- **Issue**: BRANCH-1 bootstrap precedent (changelog L205): the slice authoring the prerequisite sub-block cannot use it at its own `/build-slice`. mission-brief/design asserted self-application without the bootstrap distinction.
- **Evidence**: `methodology-changelog.md` L205 (verified).
- **Builder draft**: ACCEPTED-FIXED — mission-brief AC5 + Must-not-defer rewritten "bootstrap-aware"; design.md adds a "Recursive self-application — bootstrap-reference instance #1" section; ADR-024 Consequences adds the bootstrap consequence; Verification-plan row 5 now states the explicit `python -m tools.critique_review_prerequisite_audit <slice-026-folder>` exit-0 invocation.

### Minors (log; address if cheap)

#### m1: ADR-024 number/title — confirm sequence + rename on B1
- **Builder draft**: ACCEPTED-FIXED — ADR sequence verified gap-free (highest prior ADR-023); ADR id stays 024; file slug + title + body renamed CRPD-1→CRP-1; title expanded to cover naming-class placement.

#### m2: Malformed-skip substring could false-positive on narrative prose
- **Builder draft**: ACCEPTED-FIXED — resolved by B2's redesign: detection is now keyed on the `critique-review-skip:` *frontmatter key*, not a body-substring scan, so narrative prose mentioning the token cannot false-positive. A non-false-positive fixture is added to the TF-1 test file scope (design.md "What's new").

## Dimensions checked
- [x] Unfounded assumptions — M1, M2, M4 (all ACCEPTED-FIXED)
- [x] Missing edge cases — B2 (Step 7b state-mutation), m2 (narrative false-positive) — both ACCEPTED-FIXED
- [x] Over-engineering — none (audit appropriately scoped, reuses BRANCH-1)
- [x] Under-engineering — B1 naming-class conformance (ACCEPTED-FIXED); TF-1 row coverage adequate
- [x] Contract gaps — CLI contract fully specified; B2 addressed input-stability gap
- [x] Security — none (local CLI audit, no auth/network/secrets/injection surface)
- [x] Drift from vault — B1 (ADR-019 contradiction, the central blocker — ACCEPTED-FIXED); all cited paths verified to exist
- [x] Web-known issues — n/a (self-hosting in-house methodology slice; zero external technology)
- [x] Cross-cutting conformance — B1 (naming-class), M3 (mechanical-table-vs-inventory), M4 (bootstrap discipline) — all ACCEPTED-FIXED; BRANCH-1 template parity verified accurate

## Triage

**Triaged by**: user
**Date**: 2026-05-16
**Final verdict**: CLEAN
**Dual-review reconciliation**: /critique-review verdict EXTEND — 8 first-Critic findings confirmed VALID at correct severity, 0 suspicious, 1 missed Major (M-add-1, milestone-template forward-sync) added below as ACCEPTED-FIXED.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | ADR-019 L13 verified verbatim; CRPD-1→CRP-1 renamed across all surfaces; placed in audit-enforced-gate class, conforms to (not supersedes) ADR-019 |
| B2 | Blocker | ACCEPTED-FIXED | Step 7b L269-271 verified; escape-hatch moved to Step-7b-preservable `critique-review-skip:` milestone.md frontmatter key; ADR-024 + design.md + mission-brief updated |
| M1 | Major | ACCEPTED-FIXED | Wiring verified (sole invocation skills/critique-review/SKILL.md:92); mission-brief Intent + design.md corrected; CRP-1 reframed as first structural skip-detector |
| M2 | Major | ACCEPTED-FIXED | Prereq-check L17-27 verified; "FIRST audit" claim dropped; deterministic post-L22/L23 placement specified with dependency rationale |
| M3 | Major | ACCEPTED-FIXED | install_audit L66-71 stale comment + independent-counter nature verified; both added to design.md propagation enumeration |
| M4 | Major | ACCEPTED-FIXED | BRANCH-1 bootstrap precedent (changelog L205) verified; bootstrap-reference-instance section added to design.md + ADR-024 + mission-brief; audit-against-self in Verification row 5 |
| m1 | Minor | ACCEPTED-FIXED | ADR sequence gap-free verified; id 024 kept, slug/title/body renamed |
| m2 | Minor | ACCEPTED-FIXED | Subsumed by B2 frontmatter-key redesign; non-false-positive fixture added to test scope |
| M-add-1 | Major | ACCEPTED-FIXED | /critique-review (DR-1) missed finding. Verified: templates/milestone.md + ~/.claude/templates/milestone.md byte-equal; install_audit `_check_templates` L208 existence-only; no milestone template drift test. B2 fix created an unguarded in-repo↔installed template forward-sync surface (FBCD-1 / slice-025-L39 under-enumerated-propagation class). Fixed: design.md §What's-new N=5 propagation bullet (manual+lockstep, template byte-equality discipline scoped OUT) + ADR-024 Consequences enumeration-discharge note |
