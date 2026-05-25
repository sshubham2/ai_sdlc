# Critique: Slice 030B complete-shippability-decoupling

**Critic reviewed**: mission-brief.md, design.md, ADR-030, ADR-031
**Date**: 2026-05-16
**Result**: BLOCKED
**Round**: v1 (first critique loop — preserve this file as the load-bearing audit artifact per slice-030A never-overwrite lesson; any re-critique copies this to `critique-history-v1.md` BEFORE rewriting)

## Summary

The slice's load-bearing anti-recurrence claim ("the audit re-derives from the catalog so it cannot miss a category") is undermined by its own row-scope: SCMD-1's decoupling invariant re-derives only from rows #5/#8/#12, while the identical `Path.home()/.claude/methodology-changelog.md` untracked-read coupling exists in ~38 cited functions across ~20 other rows (7–30). R-4 cannot truthfully escalate to `retired` while ~18 rows retain the exact coupling class this slice exists to eliminate. This is the slice-030 enumeration-completeness defect relocating a third time — now into the audit's hard-coded row filter. The high-risk-tier note mandated re-critique on exactly this surface; this finding is why.

**Builder self-check (slice-030A D-3 rubber-stamp signal, "self-check after BLOCKED #1")**: all 9 findings were independently verified against the actual code (`tools/shippability_path_audit.py`, `tests/methodology/test_*`, `architecture/shippability.md`, `skills/validate-slice/SKILL.md`). They are specific, not generic; several are architectural (M1 closed-world vs open-world). They share ONE root cause with ONE coherent fix → convergent, not relocating. Accepting them is the honest disposition, not a rubber stamp. B1 carries a genuine scope fork the user must own — surfaced at TRI-1 per the slice-030A "surface the split/scope-cut decision, don't unilaterally patch" lesson.

## Findings

### Blockers (must address before /build-slice)

#### B1: SCMD-1 decoupling invariant is scoped to rows #5/#8/#12 — the identical C3 coupling survives in ~18 other rows; R-4 `retired` would be false
- **Claim under review**: design.md L19 "re-derive from rows #5/#8/#12"; ADR-031 "slice-030 'missed a category' structurally impossible"; mission-brief Intent "R-4 escalates to `retired`".
- **Issue**: C3 coupling (`Path.home()/".claude"/"methodology-changelog.md"`) is in ~38 `test_v_0_NN_0_*_entry_present_in_repo_and_installed` functions across catalog rows 7–30 (v0.22.0→v0.44.0), not just v0.23.0/v0.27.0. SCMD-1 re-deriving only from #5/#8/#12 will not scan rows 7,9–27,30. Post-ship, a `~/.claude/` drift still produces a false PCA-1 HALT via those rows — the R-4 failure mode unretired. "Structurally impossible to miss a category" is false: the category moved into the hand-enumerated row triple (AC1 + design.md L19), which IS category enumeration — the must-not-defer prohibition.
- **Evidence**: shippability.md rows 7–30; test_methodology_changelog.py 28× `Path.home()/.claude/methodology-changelog.md` reads (L168…L2520); design.md L9+L19; mission-brief AC1; risk-register R-4; slice-029 aggregated lesson.
- **Proposed fix**: (a) widen SCMD-1's decoupling derivation to ALL catalog rows + decouple every entry-pin fn from the untracked read; OR (b) keep #5/#8/#12 scope but R-4 stays `mitigating` with a new sub-entry naming the ~18 rows + chartered 030C, and AC1/Intent/pre-finish gate rewritten to match. Silently escalating R-4 to `retired` with 18 rows still coupled is the D-3 "silently weakened" failure.
- **Builder draft**: ACCEPTED-PENDING — **REVISED recommendation: SPLIT (option (b)-aligned), NOT option (a) in-place** (changed after M-add-1; see below). Original draft recommended option (a) widen-in-place via an installed-mirror fixture; M-add-1 demonstrated that mechanism relocates the flaw a 4th time and destroys the forward-sync invariant. The scope defect B1 identifies is real and Blocker-correct (slice-030A design.md L9: 030B "owns the decoupling, scoped properly with a *mechanical* complete-set derivation (not category enumeration)" — "#5/#8/#12" was the slice-029 symptom-witnessed subset, not the complete set; hand-coding it IS the enumeration trap). But M-add-1 shows the complete set splits into **two categorically different problems**: *incidental* coupling (C1/C2, byte-faithfully repointable, R-4-retireable) vs *essential* coupling (C3 entry-pins, where the untracked read IS the invariant). Per slice-030A's lessons ("self-check after BLOCKED #1; prefer split over patch when the slice is actually two features; splitting removes the relocation surface") and the /slice ≤1-day scope rule, the honest recommendation is:
  - **030B (this slice, re-scoped minimal)**: incidental coupling only — archive-backtests → tracked canonical fixtures + verbatim tracked corpus (C1/C2, BCI-1 guarantees faithfulness), machine-stable command column (B2/B3 + AC3), meta-M1′ ADR-030 (corpus fidelity), closed-world AST allowlist for the *incidental* class (M1), AC2 non-vacuous (M4), corpus derived-not-enumerated (M3). R-4 stays **`mitigating`** with a new risk-register sub-entry naming the ~20 entry-pin rows + the M-add-1 relocation hazard. Shippable, bounded, ≤1 day, no false R-4 retirement.
  - **030C (chartered follow-up)**: essential-coupling reframe — re-home the in-repo↔installed forward-sync invariant to a properly-gated non-catalog control, define SCMD-1's invariant as *accounted-for* (catalog-derived intentional-installed allowlist) not *absent*, and only then escalate R-4 → `retired`. M-add-1 carries here.
  **This is a user-owned scope/split decision surfaced at TRI-1** — options: **(b-split)** [recommended] 030B-minimal + chartered 030C, R-4 stays mitigating; **(a-widen)** attempt all-rows + essential-coupling reframe in this one slice (larger, scope-risk, but R-4 retireable now); **(b-defer)** 030B-minimal, no 030C charter yet (R-4 mitigating, residual logged only).

#### B2: `/validate-slice` Step 4 still consumes the prose `Command` column — the Machine-cmd footgun is not actually closed at the runner
- **Claim under review**: design.md "runner + audits authoritatively consume `Machine-cmd`"; AC3 "the catalog runner ... never shell-execs a narrative/Runtime cell".
- **Issue**: The runner is `skills/validate-slice/SKILL.md` Step 4 (L207: "Run each entry's **Command** column"). Design edits tools/shippability.md/tests/ADRs but NOT SKILL.md Step 4 → the actual LLM runner still reads the prose `Command` column; rows #28/#29 multi-`;` narrative cells stay executed-as-prose. AC3's literal wording is undelivered (under-engineering: AC3 has no design element for the runner-side half).
- **Evidence**: skills/validate-slice/SKILL.md L207; design.md What's-new/Wiring (no SKILL.md row); shippability.md L36–L37.
- **Proposed fix**: Add SKILL.md Step 4 (+ Step 5.5) to What's-new/Components/Wiring; repoint runner prose to `Machine-cmd`; add a SKILL.md prose-pin (mini-CAD class).
- **Builder draft**: ACCEPTED-PENDING — correct; the runner is the LLM executing SKILL.md prose, and I repointed the tools but not the prose. Will add `skills/validate-slice/SKILL.md` Step 4 + Step 5.5 to Components touched/Wiring matrix with a `Machine-cmd` repoint + a prose-pin test. Contingent on B1 scope (same redesign round).

#### B3: "7th column" but the catalog has 5 columns; `shippability_path_audit` hard-codes `cells[3]` + `len(cells)<5` guard; column-index/guard change unspecified; missing-column silent skip disables PTFCD-1
- **Claim under review**: design.md "a **7th column** `Machine-cmd`"; "predicate already matches — no parser fork".
- **Issue**: Header is 5 cols (`# | Slice | Critical path | Command | Runtime`); new col is the 6th. `shippability_path_audit.audit_catalog_file` uses `command_cell = cells[3]` + `if len(cells) < 5: continue`. Repointing to Machine-cmd requires a new index + guard change; a row missing the new column must be a SCMD-1 violation, not a silent `continue`-skip (which silently disables PTFCD-1 for that row). "predicate already matches" conflates token-regex (matches) with column-selection (must change, unspecified).
- **Evidence**: shippability.md L7; tools/shippability_path_audit.py L146–L152; design.md Data-model-deltas.
- **Proposed fix**: Correct 5→6; specify exact `audit_catalog_file` change (new index, guard rejects-not-skips rows missing Machine-cmd as a SCMD-1 violation); add a test that a missing-column row FAILS SCMD-1 + is not silently PTFCD-1-skipped.
- **Builder draft**: ACCEPTED-PENDING — factually correct; "7th" was an error and the `cells[3]`/`len<5` index dependency was hand-waved. Will correct the count, specify the parser index+guard change (missing Machine-cmd ⇒ SCMD-1 violation, never a silent skip), add the missing-column regression test. Same redesign round.

### Majors (address this slice)

#### M1: AST literal-shape scan is structurally incomplete under constant/cross-module indirection — anti-recurrence guard can pass while coupling remains
- **Claim under review**: design.md L19 "AST-scan ... for literal gitignored/untracked read shapes"; "cannot 'miss a category'".
- **Issue**: Coupling is ALREADY indirected: `_GLOBAL_BUILD_CHECKS` (module constant, test_build_checks_audit.py L380), `REPO_ROOT`/`read_file` (cross-module from conftest.py L6/L15). An open-world literal-AST hunt that doesn't transitively follow cross-module imports is false-clean (misses the coupling — the slice-030 failure mode) or explodes scope. Completeness asserted for a technique with intrinsic incompleteness under indirection.
- **Evidence**: test_build_checks_audit.py L380/L408–L412/L823–L827; conftest.py L6/L15; design.md L19.
- **Proposed fix**: Specify resolver closure; OR (stronger) closed-world allowlist — decoupled fns may reach paths ONLY via an allowlisted set of tracked-fixture-producing symbols; any other Path-producing name/call → violation. Add a deliberately-indirected negative-test fixture.
- **Builder draft**: ACCEPTED-PENDING — strong finding; the code's *current* shape already defeats a naive literal scan. Will redesign SCMD-1's decoupling check as a **closed-world allowlist** (complete-by-construction, no indirection escape) + add an indirected-Path.home() negative-test fixture asserting SCMD-1 catches it. This strengthens the guarantee and matches the design's own fail-closed philosophy. Same round.

#### M2: Splitting `test_v_0_23_0_*`/`test_v_0_27_0_*` creates a naming-vs-behavior lie + asymmetric coverage + uncited installed-half fn's gate unspecified
- **Issue**: `_and_installed`-named fns whose body no longer checks installed = parity lie (Dim 1/9 — the class the methodology audits exist to catch); only 2 of ~38 split while ~36 stay coupled (asymmetry, see B1); the uncited installed-half fn's running gate unspecified (CLAUDE.md: raw pytest misses gated guarantees).
- **Evidence**: test_methodology_changelog.py L184/L377; CLAUDE.md "raw pytest runs miss these".
- **Proposed fix**: Rename to match reduced body; OR keep fns whole and point installed-half at a git-tracked installed-mirror fixture (ADR-030's pattern applied to the changelog).
- **Builder draft**: ACCEPTED-PENDING — resolved together with B1 option (a): the installed-mirror-fixture approach keeps every `_and_installed` fn WHOLE (no rename, no split, no asymmetry) AND decoupled, with one catalog-cited fixture↔real-installed byte-equality guard re-homing the forward-sync invariant. Eliminates the lie, the asymmetry, and the uncited-gate problem in one move. Folded into B1's redesign.

#### M3: ADR-030 hand-enumerates slice-003/004/005/006/007/011 — slice-001 (read by row #8/#12 fns) is missing; enumeration defect recurring inside the ADR's own fixture list
- **Evidence**: test_build_checks_audit.py L929 `test_slice_001_archive_still_fires_legitimate_rules` (row #8), L1314 `test_slice_001_archive_still_fires_proj2` (row #12) — read slice-001 archive; design.md/ADR-030 list omits slice-001.
- **Proposed fix**: Remove the hand list; corpus populated by the same runtime derivation (audit emits exact archive paths the derived set reads; build copies precisely those); AC2 sub-check: every derived archive folder has a tracked corpus fixture (no missing folder → no silent skip).
- **Builder draft**: ACCEPTED-PENDING — correct; the hand list IS the enumeration trap recurring (omitted slice-001, verified). Will remove the enumerated list from design.md/ADR-030; the corpus derivation spans the same all-rows mechanical set as B1(a); add the AC2 corpus-completeness sub-check. Same round.

#### M4: AC2 "made unavailable" can false-green via `if _GLOBAL_BUILD_CHECKS.exists():` skip guards; Windows `Path.home()` import-time resolution unspecified
- **Evidence**: test_build_checks_audit.py L426/L465/L842/L880/L919 `if _GLOBAL_BUILD_CHECKS.exists():`; mission-brief AC2/Verification#2.
- **Proposed fix**: AC2 must assert non-vacuous execution; post-decouple remove `.exists()` guard (input is an always-present tracked fixture, hard-assert); meta-check that decoupled fns contain no `if <untracked>.exists():` skip; specify env-patch mechanism (monkeypatch `Path.home` + re-derive, or subprocess with patched `USERPROFILE`).
- **Builder draft**: ACCEPTED-PENDING — correct; pointing HOME at empty temp dir + existing `.exists()` guards = vacuous pass, exactly the false-green the slice prevents. Will rewrite AC2 to require non-vacuous assertion, add the no-skip-guard meta-check, and specify the env-patch mechanism. Same round.

### Minors (log; address if cheap)

#### m1: ADR-030 "archived slices immutable so drift-cost ~0" asserted, not evidenced
- **Builder draft**: ACCEPTED-PENDING — fair. Will soften ADR-030 to "archived folders are gitignored and convention-frozen; the tracked corpus is authoritative and intentionally decoupled — divergence from the gitignored original is acceptable and expected." Cheap wording fix in the redesign.

#### m2: "single shared parser / CSP-1-class" overstated — token extraction reused but grammar enforcement is net-new
- **Builder draft**: ACCEPTED-PENDING — fair. Will reword ADR-031 to "shared token-extraction predicate; SCMD-1 adds grammar enforcement on top of it". Cheap wording fix, same round.

### Meta-Critic added findings (DR-1 / critique-review EXTEND)

#### M-add-1 (Major): B1 option (a)'s tracked-mirror-fixture mechanism relocates the coupling a 4th time and destroys the in-repo↔installed forward-sync invariant
- **Claim under review**: critique.md B1 Builder draft — "bounded via single git-tracked installed-mirror fixture of ~/.claude/methodology-changelog.md + one-helper sweep + CAD-1-class fixture↔real-installed byte-equality guard".
- **Issue**: The ~22 entry-pin fns read untracked `~/.claude/methodology-changelog.md` *as the load-bearing assertion itself* (purpose: detect a forgotten forward-sync; docstrings L212-213/L261-262). This is **essential coupling**, categorically unlike C1/C2 **incidental coupling** where slice-030A's BCI-1 gate guarantees the tracked fixture is byte-faithful to the live file. There is NO BCI-1 analogue for the changelog — these ~22 fns are the *only* enforcers of in-repo≡installed. If they assert against a tracked mirror, the invariant is **destroyed, not decoupled**. The compensating byte-equality guard is then the sole remaining untracked-`~/.claude/` reader: cited → it's the new coupled-cited-fn (relocation, SCMD-1 all-rows scan FAILs it); uncited → invisible to SCMD-1's durable audit (the R-4-critical invariant unguarded — slice-030 relocation one indirection deeper).
- **Evidence**: `test_methodology_changelog.py` L168/L212-213/L261-262 (installed read = the assertion's purpose); absence of any BCI-1-class always-on changelog-equivalence gate; verified by critique-review agent.
- **Carry-forward**: applies regardless of B1 fork — if TRI-1 splits to 030C, M-add-1 transfers there; NOT closed by the fork decision.
- **Builder draft**: ACCEPTED-FIXED (analysis-level) — **this is a correct catch and it changes my B1 recommendation.** M-add-1 reveals 030B-as-scoped conflated **two semantically distinct problems**: (i) *incidental* coupling (C1/C2 — repointable to byte-faithful tracked fixtures, R-4 retireable for those rows) and (ii) *essential* coupling (C3 entry-pin installed-reads — the read IS the invariant, not decoupleable without re-homing the forward-sync check off-catalog + a SCMD-1-derived intentional-installed allowlist so the read is *accounted for*, not *absent*). Per the slice-030A lesson ("self-check after BLOCKED #1; surface a split/scope-cut decision, don't patch; splitting removes the relocation surface") and the /slice scope rule (a slice that is actually two features → split), I am **revising my B1 recommendation from option (a) in-place to a SPLIT** (B1 option (b)-aligned, scoped correctly): see revised B1 Builder draft below. This is the genuine-engagement response the meta-Critic's Builder-side D-3 note demanded — I changed my recommendation because the mechanism I endorsed was shown to be a relocation trap.

## Dimensions checked
- [x] Unfounded assumptions — B3, M1, m1, m2
- [x] Missing edge cases — M3, M4, B3 (missing-column PTFCD-1 silent skip)
- [x] Over-engineering — none (single-tool/single-rule SCMD-1 merge appropriately scoped; thin-vault conformant)
- [x] Under-engineering — B1, B2, M2
- [x] Contract gaps — B3 (schema-delta column-index/guard + missing-column behavior)
- [x] Security — none (no runtime authz/input/secrets; non-opt-out gate wiring specified, mirrors BCI-1)
- [x] Drift from vault — B1 (R-4 `retired` would be a false risk-register state), M2 (fn-name-vs-behavior drift)
- [x] Web-known issues — deliberate low-yield skip (no external SDK/API/platform; only Python `ast`, intrinsic incompleteness assessed under M1)
- [x] Cross-cutting conformance — B1 (slice-030 enumeration defect relocated a 3rd time into the audit row-filter), M3 (same class in ADR-030 corpus list), B2 (actual runner not repointed), M2 (recursive self-application: a catalog-coupling-hardening slice introduced a name-vs-behavior parity violation of the very class the methodology audits catch)

## Triage

**Triaged by**: user
**Date**: 2026-05-16
**Final verdict**: NEEDS-FIXES

Dual-pass reconciled (first Critic BLOCKED + meta-Critic EXTEND). User ratified **B1 → (b-split)**: 030B re-scoped to incidental coupling only; chartered 030C for the essential-coupling reframe; R-4 stays `mitigating` with a new sub-entry. All other findings accepted as drafted. Verdict computed mechanically: no ESCALATED; ACCEPTED-PENDING present (B2/B3/M1/M2/M3/M4/m1/m2) → NEEDS-FIXES. High-tier rule mandates re-critique after the material scope rewrite → v2 loop (this critique.md preserved as `critique-history-v1.md` before the v2 rewrite, per slice-030A never-overwrite lesson).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | User-ratified (b-split): 030B re-scoped incidental-only + 030C chartered + R-4 sub-entry; applied to mission-brief/design/ADRs/risk-register this round |
| B2 | Blocker | ACCEPTED-PENDING | validate-slice/SKILL.md Step4+5.5 runner repoint to Machine-cmd + prose-pin; design-scoped this round, code in /build-slice |
| B3 | Blocker | ACCEPTED-PENDING | Correct 5→6 col; specify shippability_path_audit index+guard (missing-col ⇒ SCMD-1 violation, not silent skip); missing-col regression test |
| M1 | Major | ACCEPTED-PENDING | Closed-world allowlist AST scoped to the incidental (C1/C2) class + deliberately-indirected negative-test fixture |
| M2 | Major | ACCEPTED-PENDING | Resolved by the M-add-1 reframe: entry-pins are essential → 030C; 030B does NOT split/rename them (no naming lie introduced) |
| M3 | Major | ACCEPTED-PENDING | Remove hand-listed corpus from ADR-030/design; corpus derived from the cited set (incl. slice-001); AC2 corpus-completeness sub-check |
| M4 | Major | ACCEPTED-PENDING | AC2 rewritten non-vacuous (decoupled fns drop `.exists()` guard, hard-assert) + no-skip-guard meta-check + env-patch mechanism specified |
| M-add-1 | Major (meta-Critic, DR-1) | DEFERRED | Essential-coupling reframe is 030C's chartered scope (user-ratified split); carried forward to slice-030C — NOT closed by the fork |
| m1 | Minor | ACCEPTED-PENDING | Soften ADR-030 immutability prose + make the SCPD-1/SCMD-1 orphan-catch concrete in AC2 (per meta-Critic note: necessary-but-insufficient if only softened) |
| m2 | Minor | ACCEPTED-PENDING | Reword ADR-031: "shared token-extraction predicate; SCMD-1 adds grammar enforcement on top" (not "no second parser / CSP-1-class") |
