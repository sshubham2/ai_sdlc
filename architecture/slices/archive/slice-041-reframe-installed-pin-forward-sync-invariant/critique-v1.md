# Critique: Slice 041 reframe-installed-pin-forward-sync-invariant

**Critic reviewed**: mission-brief.md, design.md, new ADRs (ADR-042, ADR-043)
**Date**: 2026-05-18
**Result**: BLOCKED (Critic's advisory result; final verdict computed at TRI-1)

## Summary

The re-homing strategy (non-catalog BCI-1-analogue gate + closed-world registered allowlist) is structurally sound and the M-add-1 relocation reasoning is verified-correct. But the design's central scope premise — "the essential class IS the 32 `_entry_present_in_repo_and_installed` fns" — is **empirically false against the real artifact**: the decoupling audit classifies **37 essential cited fns**, including 8 non-`_entry_present` fns (`_entry_names_*`, `_supersession_pattern_retired`) and a cross-module LAYER-EVID-1 pin in `tests/skills/diagnose/test_skill_md_pins.py` the design never touches. Under ADR-043's empty allowlist these 8 cause `essential-unregistered ⇒ exit 1`, failing AC3/AC4/AC5. Requires re-scope before build.

## Findings

### Blockers (must address before /build-slice)

#### B1: Essential class is NOT the 32 `_entry_present_*` fns — "split 32" leaves ~8 essential cited fns unaddressed → AC4 empty allowlist exits 1
- **Claim under review**: design.md/ADR-042 "32 fns ... split 32, keep in-repo half"; AC3 "zero remaining essential-class cited fns"; AC4 "allowlist empty post-041".
- **Issue**: Critic ran `tools.shippability_decoupling_audit architecture/shippability.md --json` on the real catalog: `essential count 37`; 28 unique `_entry_present_*`, **8 NOT**: `test_v_0_29_0_entry_names_supersession_pattern_retired`, `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed`, `test_v_0_32_0_tphd_1_entry_names_slice_016_cross_slice_anchor`, `test_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo_and_installed`, `test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase`, and `tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` (LAYER-EVID-1 N=6-surface pin reading `Path.home()/".claude"/"methodology-changelog.md"` at L349). The "split the 32 `_entry_present_*`" plan does nothing to these 8; post-ADR-043 they are essential ∧ unregistered → exit 1. AC3/AC4/AC5 + pre-finish gate FAIL.
- **Evidence**: `shippability_decoupling_audit.py` `classify_fn` L393–415 + `_ESSENTIAL_SHAPES` L95–97 (matches ANY fn reaching `(".claude","methodology-changelog.md")`); live audit JSON (rows_scanned 40, essential 37); `test_skill_md_pins.py:326–349`.
- **Proposed fix**: Re-scope at /design-slice. (a) extend keep-in-repo/drop-installed treatment to ALL essential `test_methodology_changelog.py` fns incl. `_entry_names_*` + `_supersession_pattern_retired`, AND decide explicitly how cross-module `test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` is handled (decouple its installed read OR register it — non-empty allowlist, contradicting ADR-043); OR (b) non-empty allowlist enumerating every legitimately-essential fn with per-entry rationale. Correct AC3/AC4 + ADR-042/043 "32"/"empty post-041" framing to the real population; verification plan #3/#4 must assert the actual essential set.
- **Builder draft**: ACCEPTED-FIXED (redesign applied post-TRI-1, direction user-ratified) — Critic is empirically correct; I verified the failure mechanism. **Recommended resolution**: extend the keep-in-repo-half/drop-installed-half treatment to ALL essential-classified `test_methodology_changelog.py` fns (the `_entry_present_*` 28 + `_entry_names_*`/`_supersession_pattern_retired` set); for the cross-module `test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` LAYER-EVID-1 pin, **re-home its installed-changelog leg onto MCFS-1** (its in-repo N=6-surface byte-equality assertions are retained; only the `Path.home()/.claude/methodology-changelog.md` leg is dropped — MCFS-1's whole-file equality subsumes that single per-surface installed read). This keeps `_REGISTERED_INSTALLED_READERS` **empty**, preserving ADR-043's locked decision. The genuine user-facing branch (re-home vs non-empty registered allowlist) is surfaced for TRI-1 ratification before redesign is applied.

#### B2: AC4 + ADR-043 "empty allowlist post-041" contradicts the existence of a legitimate cross-module essential pin
- **Claim under review**: ADR-043 "`_REGISTERED_INSTALLED_READERS = frozenset()` ... essential set empty ⊆ empty allowlist ⇒ exit 0"; AC4.
- **Issue**: ADR-043 asserts post-041 essential set is empty *because* ADR-042 splits the 32. B1 shows it is not the 32. `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` legitimately asserts in-repo↔installed forward-sync of the v0.33.0 entry as part of a LAYER-EVID-1 N=6 pin — its installed read is intentional/protective (the exact "essential" semantics). Sound treatment is either re-home onto MCFS-1 or *register* it; registering ⇒ allowlist NOT empty ⇒ contradicts ADR-043 + AC4. "Register the read" and "empty allowlist" are mutually exclusive once the real essential population is accounted for — the design did not recognise this.
- **Evidence**: `test_skill_md_pins.py:326–356` (LAYER-EVID-1 N=6 bidirectional pin, slice-019 AC #1); ADR-043 Decision/Consequences.
- **Proposed fix**: At /design-slice decide and document: (i) re-home the LAYER-EVID-1 / `_entry_names_*` essential pins' installed leg onto MCFS-1 whole-file equality (re-justify ADR-042's "whole-file ≡ stronger" for these), OR (ii) non-empty `_REGISTERED_INSTALLED_READERS`. Update ADR-043, AC4, "empty post-041" prose. Redesign-level decision.
- **Builder draft**: ACCEPTED-FIXED (redesign applied post-TRI-1, direction user-ratified) — coupled to B1. **Recommended**: option (i) — re-home the cross-module LAYER-EVID-1 pin's installed-changelog leg onto MCFS-1, keeping the allowlist empty so ADR-043's closed-world default holds unchanged. ADR-042's "whole-file ≡ stronger than per-surface installed substring read" is re-justified: MCFS-1 whole-file in-repo≡installed equality strictly subsumes any single per-entry installed substring check (if whole files are equal, the v0.33.0 substring is equal); the pin's *in-repo* N=6 byte-equality assertions (the LAYER-EVID-1 content protection) are fully retained. **The user chooses (i) vs (ii) at TRI-1.**

### Majors (address this slice)

#### M1: "rows 7–30 / ~20 / 32→~24 selectors" is wrong — actual: rows 7–39 with gaps, 27 unique cited, 37 essential
- **Issue**: Verified: `_entry_present_*` cited by rows 7–27,30,32,35,37,38,39 (range 7–39, gaps 28/29/31/33/34/36; row 18 duplicates row 16's `test_v_0_31_0_rpcd_1`; row 39 cites both `aped_1`+`mepd_1`). 32 defined, **27 unique cited**, **5 defined-but-uncited** (`v_0_42_0_utf8_stdout_1_v1_1`, `v_0_43_0_diagnose_sequential_dispatch`, `v_0_45_0_scmd_1`, `v_0_47_0_eol_drift_1`, `v_0_48_0_tffl_1`). Every quantitative claim driving the rename/propagation plan is inaccurate → under-specifies the PTFFD-1 lockstep surface.
- **Evidence**: grep over `architecture/shippability.md` vs `test_methodology_changelog.py`; row 16/18 duplicate.
- **Proposed fix**: Replace "~20/7–30/32→~24" with verified figures; enumerate exact rows; note 5 uncited fns (rename still needed for in-file consistency, no selector); note row 16/18 duplicate; add the 8 B1 fns.
- **Builder draft**: ACCEPTED-FIXED — folded into the B1 redesign; design.md will carry the exact enumerated row list + the 32-defined / 27-cited / 5-uncited / +8-non-`_entry_present` breakdown.

#### M2: Sibling-scoping regression tests (`_extract_v031_body`/`_extract_v033_body`) not in the rename/reshape scope analysis
- **Issue**: `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body` (L1054), `test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body` (L1431) exercise `_extract_v031_body`/`_extract_v033_body` scoped between adjacent entry-pin fns. The slice changes entry-pin *shape* (drop installed half) + names; if any sibling-scoping helper anchors on old names or the installed-half body structure, the scope windows silently shift. "PTFFD-1 enforces lockstep" only covers cited-fn existence, not intra-file structural anchors.
- **Evidence**: `test_methodology_changelog.py:1054`, `:1431`; design Self-application note covers only the v0.53.0 pin shape.
- **Proposed fix**: Audit `_extract_v031_body`/`_extract_v033_body` (+ any sibling-scoping helper) for dependence on old names + installed-half-as-delimiter; add design.md component entry + regression assertion they still bound correctly post-reshape; add to wiring/verification plan.
- **Builder draft**: ACCEPTED-FIXED — design.md gains a Components-touched entry for the sibling-scoping helpers + a verification-plan row asserting `_extract_v031_body`/`_extract_v033_body` boundary correctness post-reshape. (Note: `_extract_version_body` scopes by `## v{version}` text anchors, not fn names — verified at read; the reshape drops body lines but not the `## v` anchors, so risk is low, but the explicit regression assertion is cheap and correct to add.)

#### M3: AC3 self-application — no mechanical pre-finish check that the as-built v0.53.0 pin classifies `clean`, only prose
- **Issue**: The v0.53.0 entry-pin gets its own shippability row (wiring matrix "new row LAST") so `_cited()` WILL resolve it. AC3-safe only if it reaches NO `(".claude","methodology-changelog.md")` segment — in-repo `read_file("methodology-changelog.md")` only, no transitive `Path.home()` helper. Design asserts the shape but gives no mechanical pre-finish classification check (slice-037 "layers 2&3 reachable only by pre-finish real-artifact runs").
- **Evidence**: `_reachable_path_segments` L369–390 (follows same-module callees + module consts); design Self-application note (no post-build classification check).
- **Proposed fix**: Add verification-plan step: after authoring the v0.53.0 pin + its row, run `tools.shippability_decoupling_audit --json` and assert `test_v_0_53_0_mcfs_1_entry_present ∈ clean` (not essential/incidental); part of the pre-finish gate, sequenced LAST.
- **Builder draft**: ACCEPTED-FIXED — added to design.md verification plan + pre-finish gate as an explicit BC-PROJ-4-class real-artifact assertion.

#### M4: Methodology-surface obligation branch asserted, not verified against the actual META-1 enforcing test
- **Issue**: Full-obligation path is plausibly the right MEPD-1(a) branch (SCMD-1 exit-code contract changes), but two sub-claims unverified: (1) is there a META-1 structural test asserting every `## vX.Y.Z` has an `_entry_present_in_repo_and_installed`-*named* test (a suffix-convention enforcer the rename would break)? Critic's grep found none but design doesn't cite having checked. (2) slice-040/MEPD-1(b): the obligation decision must be verified against the actual `test_methodology_changelog.py` enforcing assertion, not precedent — design asserts the branch without quoting the enforcing test.
- **Evidence**: 32 fns all named `_entry_present_in_repo_and_installed`; design Methodology-surface section cites no specific META-1 assertion; slice-040 lesson; v0.53.0 confirmed correct (VERSION 0.52.0, latest entry v0.52.0).
- **Proposed fix**: Cite the specific `test_methodology_changelog.py` enforcing fn(s); confirm none asserts the `_entry_present_in_repo_and_installed` suffix as a convention (else rename breaks it → same-fix-block update, slice-039 generalized).
- **Builder draft**: ACCEPTED-FIXED — design.md Methodology-surface section will quote the specific META-1 enforcing assertion verified against, and explicitly record the suffix-convention-enforcer check result (with the exact grep/read evidence) per MEPD-1(b).

### Minors (log; address if cheap)

#### m1: Wiring matrix names `/reflect` post-write generically — name the exact step
- **Issue**: BCI-1's reflect wiring is "Step 5b fail-loud post-write" tied to rule-promotion; MCFS-1's concern is the PMI-1 changelog forward-sync at a different `/reflect` point. Generic "post-write" risks mis-placed wiring.
- **Proposed fix**: Name the exact `skills/reflect/SKILL.md` step, mirroring BCI-1's "Step 5b" precision.
- **Builder draft**: ACCEPTED-FIXED — read `skills/reflect/SKILL.md` at redesign, name the exact PMI-1-forward-sync step anchor in the wiring matrix.

#### m2: ADR-042 "whole-file ≡ stronger" holds for `_entry_present_*` but conflate-risk for `_entry_names_*` content pins
- **Issue**: MCFS-1 whole-file equality confirms in-repo==installed but not that a canonical phrase is *present in either* (META-1's job, retained in-repo half). Must not let "MCFS-1 covers it" drop a content assertion (slice-037 meta-Critic: content-bearing AC needs a CONTENT pin).
- **Proposed fix**: State explicitly the in-repo content/canonical-phrase half of every essential `_entry_names_*`/`_entry_present_*` pin is RETAINED; MCFS-1 (forward-sync) + retained in-repo META-1 (content) jointly preserve protective value.
- **Builder draft**: ACCEPTED-FIXED — explicit in the B1 redesign: only the installed-read leg is dropped/re-homed; every in-repo content + canonical-phrase + N=6 byte-equality assertion is retained.

## Dimensions checked
- [x] Unfounded assumptions — B1 (essential ≠ the 32, audit executed), M1 (counts all wrong), M4 (obligation branch asserted)
- [x] Missing edge cases — M2 (sibling-scoping helpers), M3 (slice's own pin self-classification); BCI-1 installed-absent→WARN transferability confirmed faithful for the non-determinism threat model
- [x] Over-engineering — none (minimal sound control; empty frozenset right closed-world default modulo B2)
- [x] Under-engineering — B1, B2, M3 (ACs lack design elements for the real population / contradiction / mechanical self-check)
- [x] Contract gaps — none beyond B1/B2 population scoping (MCFS-1 + SCMD-1 contracts well-specified, BCI-1-faithful)
- [x] Security — none (read-only audits; M-add-1 relocation guard verified structurally sound — `_cited()` cannot reach a non-Machine-cmd `tools/*` module)
- [x] Drift from vault — R-4 escalation consistent with risk-register L70/L92; ADRs append-only/supersede-nothing (SUP-1 OK; ADR-033 home untouched); split-lineage label consistent with R-6
- [x] Web-known issues — none (in-house Python AST tooling; no external surface)
- [x] Cross-cutting conformance — B1/M1 (audit-vs-artifact, audit executed not reasoned), M2 (algorithm-path), M3 (recursive self-application, slice-037), M4 (MEPD-1); precedent claims verified against `shippability_decoupling_audit.py` directly (slice-032 law)

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

> Reconciled across BOTH passes (first Critic + DR-1 meta-Critic EXTEND). Meta-Critic severity adjustments ratified: M2 Major→Minor, m1 Minor→Major. Two meta-Critic missed findings (M-add-1 Major, M-add-2 Minor) added as triage rows. User branch decisions: (1) **re-home** the cross-module LAYER-EVID-1 pin's installed-changelog leg + all essential `_entry_names_*`/`_entry_present_*`/`_supersession` installed legs onto MCFS-1 — `_REGISTERED_INSTALLED_READERS` stays `frozenset()`, ADR-043/AC4 unchanged; (2) **update `agents/critique.md` prose** to the new `_entry_present` suffix in the same fix block (CAD-1 content-equality + 4-part forward-sync). Verdict CLEAN is mechanically correct (no ESCALATED / no ACCEPTED-PENDING) — but the slice is **high-tier** and the redesign is material, so per the high-tier rule a mandatory **re-`/critique`** of the revised design follows; **no auto-advance to `/build-slice`**.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Empirically confirmed by DR-1; redesign re-scopes to the real essential population (37 raw / 34 unique / 28 `_entry_present` / 6 non-`_entry_present`), driven off `shippability_decoupling_audit --json` essential. Branch (1): re-home, allowlist stays empty. |
| B2 | Blocker | ACCEPTED-FIXED | Branch (1) ratified: re-home cross-module pin's changelog leg onto MCFS-1; ADR-043 "empty post-041" + AC4 stand unchanged (DR-1 verified mechanically sound). |
| M1 | Major | ACCEPTED-FIXED | Counts corrected to verified figures (rows 7–39 w/ gaps, row 16=18 dup, row 39 dual-fn, 5 defined-but-uncited incl. essential-but-uncited `v_0_42_0` per M-add-2). |
| M2 | Minor | ACCEPTED-FIXED | Severity Major→Minor (DR-1: `_extract_version_body` anchors on `## v` text not fn names → low risk). Cheap sibling-scoping regression assertion still added. |
| M3 | Major | ACCEPTED-FIXED | Explicit pre-finish BC-PROJ-4-class assertion added: as-built `test_v_0_53_0_mcfs_1_entry_present` ∈ `clean`, sequenced LAST. |
| M4 | Major | ACCEPTED-FIXED | design.md will quote the specific META-1 enforcing assertion + record the suffix-convention-enforcer check (DR-1 confirmed none exists; v0.53.0 correct). |
| m1 | Major | ACCEPTED-FIXED | Severity Minor→Major (DR-1: latent silent-disable — MCFS-1 must NOT be wired into rule-promotion-gated /reflect Step 5b; must fire on the version-bump path). Exact reflect step named at redesign. |
| m2 | Minor | ACCEPTED-FIXED | In-repo content/canonical-phrase/N=6 byte-equality halves retained for ALL essential pins; only the installed-changelog leg re-homed. |
| M-add-1 | Major | ACCEPTED-FIXED | Cross-file old-suffix literals enumerated (`test_critique_agent.py:1426` + `test_query_design_skill.py:17` + `test_shippability_decoupling_audit.py:56,128`); branch (2) ratified — `agents/critique.md` prose updated same fix block under CAD-1 + forward-sync; grep-verification row added. |
| M-add-2 | Minor | ACCEPTED-FIXED | Decouple worklist driven off `--json` essential (34 unique), not selector-cited (27); `v_0_42_0_utf8_stdout_1_v1_1` noted essential-but-uncited (transitive resolution). |
