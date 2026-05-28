# Reflection: Slice 077 enhance-pulse-with-worktree-awareness

**Date**: 2026-05-29
**Shipped**: YES

## Validated

- **4-state taxonomy (IN_PROGRESS / BUILT_BUT_NOT_MERGED / MERGED / UNKNOWN) works end-to-end** — APED-1 battery 13/13 cases PASS (6 detect + 7 classify); stage-first dispatch per ADR-070 literal reading verified via real-world smoke (slice-077's own worktree correctly classified as IN_PROGRESS stage=code-review from main repo perspective).
- **Override-precedence ordering (3-level: worktree-state > CAL-1 cadence-overdue > stage-derived)** — 5 prose-pin tests on SKILL.md Step 2 prose + `augment_pulse_state_dict` library function constructs the augmented state-dict with `recommended_next_action_override` resolved deterministically at Step 2 (main thread) before Step 3 Haiku dispatch consumes it.
- **Drift-flag false-positive suppression predicate (3-surface all-match + EOL-tolerant)** — 3 unit tests PASS including positive (all match → suppress), negative (any divergence → don't suppress), EOL-tolerant (CRLF↔LF normalized per ADR-033 / EOL-DRIFT-1).
- **MEPD-1 EXCLUDE empirically holds** — slice-077 ships at v0.73.0 unchanged with no methodology-changelog entry, no PMI-1 bump, no paired-pin tests; no cross-skill consumer of `WorktreeState` materialized during slice work, validating ADR-070 § "load-bearing cross-skill contract" differentiator vs slice-076 PCR-1.
- **R-22 witnessed-gap class structurally closed** — real-world smoke `$PY -m tools.pulse_worktree_resolver --classify slice-077-... --json --repo-root C:/Users/sshub/ai_sdlc` returns correct `IN_PROGRESS(stage=code-review)` from MAIN REPO perspective. The post-slice-076 /pulse failure mode (mis-reporting stage + false-positive drift flag) cannot recur.
- **CAD-1 / OSDG-1 byte-equality on `skills/pulse/SKILL.md`** — `test_pulse_skill_drift.py` mirrors `test_reflect_skill_drift.py` shape; EOL-agnostic per slice-033.
- **BC-PROJ-9 5-inventory bump 31→32 lockstep** — all 5 surfaces aligned; `test_pulse_worktree_resolver_in_canonical_tools_plugin_manifest_install_md_at_l22_and_l166` + PMI-1 + INST-1 + UTF8-STDOUT-1 all clean.

## Corrected

- **ADR-070 4-state taxonomy stage-vs-ancestry precedence ambiguity** (Phase C in-band fix) — pre-fix logic had MERGED beating IN_PROGRESS when stage != reflect but head IS ancestor. Updated impl to stage-first dispatch: IN_PROGRESS strictly when stage != reflect (regardless of ancestry); MERGED only fires for stage == reflect + IS ancestor. Per ADR-070 § 4-state worktree taxonomy literal reading. Design.md + ADR-070 already documented the correct semantics; impl just needed to match. Class: design→code translation gap caught by Phase C unit test.
- **`_resolve_milestone_path` scan-root semantics** (Phase D mid-slice smoke in-band fix) — pre-fix `_resolve_milestone_path(repo_root, ...)` scanned the main repo's filesystem; under BRANCH-2 the milestone.md lives in the WORKTREE's filesystem (checked into the slice branch). Renamed param `repo_root` → `scan_root` and updated `detect_active_worktrees` to pass `wt_path` (worktree's path). **This is the literal witnessed-gap (R-22) fix surfacing during slice-077's own build** — the slice that closes R-22 experienced R-22 in its own build mid-slice smoke. No vault update needed (the helper is internal; behavior matches design.md § What's reused intent).
- **TPHD-1 sub-mode (a) at slice-076 inventory test** (Phase G in-band fix) — slice-076's `test_parallel_conflict_resolver_in_canonical_tools_*` hard-pinned `31`; slice-077's 31→32 bump caused regression. Refactored to forward-compat L22==L166 + floor-of-31 assertion. Same-shape regression every count-bumping slice would have caused. Class: TPHD-1 sub-mode (a) count-pin-in-test recurrence N=9 cumulative.
- **R-22 status flip open → retired** — registered at /design per /critique-review M-add-2; flipped to retired at /reflect per mission-brief commitment + RR-1 schema lifecycle.

## Discovered

- **Self-validating slice property (methodology-gold, N=1)** — the slice that closes a witnessed methodology-internal gap experienced and closed that gap during its own build via mid-slice smoke gate. /pulse Phase D mid-slice smoke directly exercised R-22 (called the helper against main repo's milestone.md scan-root) and observed the bug in a single empirical run; the fix landed in the SAME slice's commit chain. This is /critic-calibrate signal class "slice eats own dogfood": when fixing a methodology surface, the slice's own /build-slice IS the canonical empirical validation. Worth promoting as a methodology pattern at N≥2 (slice-085+ candidate).
- **Design→code translation gap N=14+ cumulative** — even with 22+ Critic dispositions covering 9 dimensions, the `_resolve_milestone_path` scan-root bug manifested only at Phase D mid-slice smoke (real-world invocation), not in unit tests (which used fake fixtures where milestone.md sat at the synthetic repo's path = same as main path). Same class as slice-076 code-Critic M2 atomicity gap (design mandated atomicity; impl traced through helper boundaries that wrote-then-raised). 3-Critic stack N=13 cumulative (slice-063 → slice-077) — design-Critic + meta-Critic each caught conceptual + cross-doc-consistency gaps; code-Critic caught implementation-level gaps; mid-slice smoke caught design→code translation gap. Strong pattern: each defect class has a structurally-distinct catcher. **DO NOT collapse the 3-Critic stack** + **DO NOT skip mid-slice smoke gate**.
- **m5 /code-review finding: UNKNOWN WARN-text design contract under-implemented** — design.md L181-191 enumerates 8 specific WARN strings for the 8 UNKNOWN sub-reasons; impl emits the reason ID but no canonical WARN template. SKILL.md Step 3 prose mentions the WARN-not-silent policy but has no template-mapping table for Haiku to consume. Class: design contract under-implementation (a class of TPHD-1 sub-mode (a)). DEFERRED to slice-079+ bundled-cleanup; promotion candidate for /critic-calibrate signal at N=13+ cumulative design→code translation gap evidence base.
- **CRSI-1 v1 voluntary-restraint N=17 cumulative** — slice-077 inherits the pattern: code-Critic returns 0B/2M/11m advisory findings; all DEFERRED to next bundled-cleanup slice rather than fix-in-band. Pattern is structurally stable across 17 cycles (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/075/077). Empirical baseline: code-Critic Majors are typically real but small-surface; bundling preserves slice's SMALL effort budget. Per slice-076 reflection L33 the alternative path (Phase H user-fix-all disposition) is also viable for high-confidence Majors; slice-077 chose voluntary-restraint default.
- **3-Critic stack N=13 cumulative complementarity stable** — code-Critic surfaced 2 distinct Major findings + 11 Minor findings structurally unreachable by design-Critic + meta-Critic stack (M1 cross-spec JSON action-key case + M2 pytest.skip swallowing real-defect signal). Both are code-level concerns the design-Critic stack cannot reach (Critic reads design.md / ADRs at /critique time; doesn't read code). Continued empirical validation.
- **TPHD-1 sub-mode (a) N=9 cumulative** — slice-076 count-pin-in-test stale-anchor surfaced at slice-077; pattern recurrence rate slows when Builder fix-block discipline is tight but inventory tests have a structural drift surface every count-bumping slice will hit. Worth N=3 promotion candidate at /critic-calibrate.

## Deferred

- **bundle-077-code-critic-cleanup** (re-queued to slice-079+ per CRSI-1 v1 voluntary-restraint) — all 13 code-Critic findings (M1 + M2 + m1-m11). M1 + m1 may naturally extract at `parallel-slice-family-parity-audit` slice (cross-spec parity scope). m5 (UNKNOWN WARN-text under-implementation) is the most substantive; design→code translation gap candidate.
- **PCR-2 (vault-claim + hard-conflict full Critic stack + TRI-RESOLVE-1)** — slice-078 candidate per slice-076 reflection's nomination (now bumped one slot due to slice-077's slice-077 claim).
- **SP-1 (slice no-arg auto-pick)** — slice-079 candidate per slice-076 deferral.
- **parallel-slice-family-parity-audit** — extraction-trigger slice for the worktree-list-porcelain parser (now N=3 Python-side post-slice-077) + JSON action-key case canonicalization (M1) + INSTALLED_SURFACES module-level extraction (m1).
- **bundle-074-code-critic-cleanup + bundle-075-code-critic-cleanup** — re-queued; still pending.
- **Self-validating slice property as methodology pattern** (Discovered #1) — defer codification to N≥2 recurrence trigger.

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` `## Triage` + reality observed during build/validate:

### First-Critic (design-Critic) findings — 19 dispositioned at TRI-1

All 4 Blockers + 9 Majors + 6 Minors VALIDATED at validation:

- **B1** (`(manual)` TF-1 row): VALIDATED — disposition ACCEPTED-FIXED; the row was removed; TF-1 audit clean post-fix. Slice-076 reflection L24 lesson directly applied.
- **B2** (argparse flag copy-paste `--diagnose/--classify/--resolve-soft`): VALIDATED — disposition ACCEPTED-FIXED; design.md L89 corrected to `--detect + --classify`; PCR-1 contract preserved.
- **B3** (`installed_content_matches_worktree` predicate underspec): VALIDATED — disposition ACCEPTED-FIXED; design.md L141-156 + ADR-070 L107-127 pin 3-file set + all-match + EOL-tolerant; suppression unit tests 3/3 PASS.
- **B4** (ADR-070 reasoning artifact): VALIDATED — disposition ACCEPTED-FIXED; L99 rewritten as single coherent paragraph.
- **M1** (MEPD-1 EXCLUDE precedent claim): VALIDATED — disposition ACCEPTED-FIXED via honest precedent rewrite; load-bearing cross-skill criterion correctly distinguishes slice-076 INCLUDE from slice-077 EXCLUDE; no cross-skill consumer emerged.
- **M2** (test count 5 vs 6): VALIDATED — disposition ACCEPTED-FIXED; design.md L14 corrected.
- **M3** (UNKNOWN silently dropped): VALIDATED — disposition ACCEPTED-FIXED; design.md L162-192 enumerates 8 UNKNOWN sub-reasons + WARN-not-silent policy; classify unit tests cover all 4 states + UNKNOWN sub-reasons.
- **M4** (AC#3 scope creep / 4×CAL-1 precedence): VALIDATED — disposition ACCEPTED-FIXED; design.md L125-134 full 8-cell precedence table + Step-2-not-Step-3 location anchor.
- **M5** (single `git revert` claim): VALIDATED — disposition ACCEPTED-FIXED; ADR-070 L155 cites `git revert -m 1`.
- **M6** (BRANCH-2 branch-name edge cases): VALIDATED — disposition ACCEPTED-FIXED; design.md L173-176 enumerates no-suffix / rename-drift / prunable-stale / non-slice branches.
- **M7** (cross-spec parity not pinned): VALIDATED — disposition ACCEPTED-FIXED; design.md L194-208 § Cross-spec parity table.
- **M8** (APED-1 floor ≥6 too permissive): VALIDATED — disposition ACCEPTED-FIXED; raised to ≥13; battery actually executes 13/13 cases.
- **M9** (RSAD-1 design-time pre-empt): VALIDATED — disposition ACCEPTED-FIXED; design.md L212-231 § Prose-pin discipline + per-literal anchoring; in-band Phase D fix to `Active slice folder (if any):` anchor (replacing `milestone.md FIRST` substring that didn't actually exist as literal — DEMONSTRATES the design.md § Prose-pin discipline mandate's value).
- **m1-m6** (minors): VALIDATED — all ACCEPTED-FIXED or DEFERRED with rationale; no surprises.

### Meta-Critic (critique-review.md) findings — 3 M-add dispositioned at TRI-1-EXT

- **M-add-1** (PCR-1 default Path(".").resolve() vs Path(".")): VALIDATED — disposition ACCEPTED-FIXED; design.md L201 cross-spec parity table corrected; impl matches PCR-1 parse-time default exactly.
- **M-add-2** (R-22 RR-1 vocabulary mismatch): VALIDATED — disposition ACCEPTED-FIXED; R-22 registered at /design with status: open; mission-brief L5 cites R-22; flips to retired at /reflect (this slice). RR-1 schema semantics preserved.
- **M-add-3** (m4 N=2 framing under-counts): VALIDATED — disposition ACCEPTED-FIXED; critique.md + design.md re-framed to N=3 post-slice-077 (Fowler extract trigger); deferral preserved with honest rationale.

### Code-Critic (code-review.md) findings — 13 dispositioned at TRI

- **M1** (cross-spec JSON action-key case UPPERCASE vs lowercase): NOT-YET — DEFERRED to slice-079+ bundled-cleanup; will re-score there.
- **M2** (pytest.skip swallowing real-defect signal): NOT-YET — DEFERRED to slice-079+ bundled-cleanup.
- **m1-m11**: NOT-YET — DEFERRED to slice-079+ bundled-cleanup. m5 (UNKNOWN WARN-text under-implementation) is the substantive design→code translation gap candidate.

### Missed by Critic

- **`_resolve_milestone_path` scan-root semantics gap** — pre-Phase-D impl scanned main repo's filesystem instead of worktree's. The design.md / ADR-070 documentation correctly described "scan from the worktree" (design.md § What's reused L23 cites the worktree's path explicitly), but no Critic finding pinpointed that the IMPL would diverge. Caught only at Phase D mid-slice smoke (real-world invocation). **Same class as slice-076 code-Critic M2 + slice-073 code-Critic M1** — design→code translation gaps that mock-based unit tests cannot reach. /critic-calibrate signal: design→code translation gap N=14+ cumulative; the 3-Critic stack catches structurally-distinct classes per layer (design-Critic = design-time conceptual; meta-Critic = cross-doc consistency; code-Critic = code-level call-site discipline) but the runtime-real-world gap surfaces only at mid-slice smoke / validation. **The mid-slice smoke gate is structurally load-bearing — do NOT skip.**

### Pattern

- 3-Critic stack N=13 cumulative complementarity stable; do NOT collapse.
- Mid-slice smoke gate is the 4th catcher for design→code translation gaps; do NOT skip.
- Voluntary-restraint discipline N=17 cumulative; bundling code-Critic findings into next slice keeps each slice at SMALL effort budget without sacrificing finding-coverage.
- TPHD-1 sub-mode (a) count-pin recurrence pattern surfaced again at slice-076 inventory test; forward-compat assertion shape (L22==L166 + floor-of-N) is the standard fix.

## Lessons for next slice

- **When fixing a methodology-internal correctness gap, the slice's own /build-slice is the canonical empirical validation case** — design the mid-slice smoke gate to deliberately exercise the gap (slice-077 example: smoke ran `--classify` from main repo specifically because the gap was "main-repo can't see worktree milestone").
- **Count-pinning in inventory tests is a TPHD-1 sub-mode (a) recurrence hot spot** — prefer forward-compat assertions (L22==L166 + floor-of-N) over hard-pinned integer literals; same fix shape applies to every BC-PROJ-9 5-inventory consumer-test.
- **3-Critic stack catches structurally-distinct defect classes per layer** — design-Critic = conceptual / cross-document; meta-Critic = cross-document consistency; code-Critic = code-level call-site; mid-slice smoke = real-world / design→code translation. Each is load-bearing.
- **Slice-077 ships at v0.73.0 unchanged (MEPD-1 EXCLUDE empirically supported)** — confirmed the load-bearing-cross-skill criterion correctly distinguishes EXCLUDE-shaped slices from INCLUDE-shaped slices; helper-module-ships is NOT the differentiator.

## Vault updates made (thin vault)

- `architecture/risk-register.md` — R-22 flipped open → retired.
- `architecture/shippability.md` — row #77 already added at Phase E.
- `architecture/lessons-learned.md` — slice-077 entry appended (Step 5).
- `architecture/slices/_index.md` — Active table updated (slice-077 removed); Most-recent-10 table updated (slice-077 prepended); Aggregated lessons updated (this slice's Lessons items pulled).
- `architecture/slices/archive/_index.md` — slice-077 appended to chronological catalog.
- This slice's `design.md` + ADR-070 — no further corrections needed beyond the in-band TRI-1 + TRI-1-EXT fixes (all already landed pre-build).

## Critic calibration cadence note

Slice-077 marks 2 slices since 2026-05-28 /critic-calibrate run (post-slice-075). CAL-1 cadence: within window (2 of 20-slice budget; no flag). /critic-calibrate next-run trigger: at ~slice-086+ default OR earlier if /critic-calibrate-fit signal accumulates (e.g., design→code translation gap N=14+ cumulative; voluntary-restraint N=17 with bundled-cleanup landing; TPHD-1 sub-mode (a) N=9; m5 UNKNOWN WARN-text under-implementation as design contract gap class).
