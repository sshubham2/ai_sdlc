# Reflection: Slice 078 add-pcr-2a-vault-claim-resolver

**Date**: 2026-05-29
**Shipped**: YES

## Validated

- **7-step Resolution algorithm executes deterministically** — `resolve_vault_claim_conflict` per design.md §Resolution algorithm step-by-step; validated by 20 unit + integration tests in `test_pcr_2a_vault_claim_resolver.py`.
- **Strict-newer winner identification works regardless of stage origin (M4 critical invariant)** — validated by paired tests `test_timestamp_winner_when_newer_in_stage_3` + `test_timestamp_winner_when_newer_in_stage_2`. Without M4's `_overlay_claims_on_queue_text` discipline, a stage-2-winner would have been silently demoted by `_regen_slice_queue:614`'s `baseline_text = text_3 if text_3 else text_2` default.
- **Defensive post-overlay regex (M-add-1) catches silent-drop on malformed candidate blocks** — validated by `test_overlay_silently_dropped_returns_stop` exercising a synthetic stage-3 block lacking `**Risk-retired:**` pivot; resolver returns STOP with `overlay-silently-dropped` reason rather than ship a stale claim.
- **In-memory text input on `_pick_loser_replacement` (M-add-2) avoids disk-read race** — validated by `test_pick_loser_replacement_reads_resolved_text_not_disk`: disk holds conflict-marker'd file, in-memory holds resolved overlay, helper returns disk-ignored result. The signature change made the disk-read structurally impossible.
- **Both dispatch sites correctly route VAULT_CLAIM into the resolver; UNKNOWN-class fail-closed preserved** — validated by all 3 tests in `test_pcr_2a_regen_slice_queue_dispatch.py` (CLI-facing + defense-in-depth + UNKNOWN-still-fail-closed).
- **`_VaultClaimDispatch` sentinel raise + catch routing works as designed** — validated by `test_regen_slice_queue_vault_claim_defense_in_depth_gate_raises_sentinel` (Phase D Repair).
- **Uniform hyphen-space audit-row separator (M2) avoided em-dash/smart-dash fragility** — validated by `test_vault_claim_event_row_format` regex `^## Vault-claim resolution - \d{4}-\d{2}-\d{2}T`; section-type distinction works at the prefix word (`Vault-claim` vs `Soft-conflict`), not at the dash decoration.
- **APED-1 Pin #1 + Pin #2 regexes correctly bind to L185 + L192 prose** — validated by `test_substep_2_5_l185_pins_vault_claim_in_apply_block` + `test_substep_2_5_l192_drops_vault_claim_from_fall_closed_enumeration`. The first Pin #2 regex was over-broad and caught a corner-case fall-through prose; refined mid-build (see Discovered).
- **Mixed-section append-only audit log** — validated by `test_log_is_append_only_across_section_types` seeding a SOFT row then appending VAULT_CLAIM and asserting byte-equal preservation.
- **5-part PMI-1 atomic bump synchronized at 0.74.0 across all 5 surfaces** — validated by `test_version_files_synchronized_at_v_0_74_0` (post-rename) + MCFS-1 + AVFS-1 + TVFS-1 + PMI-1 audits all PASS.

## Corrected

(No design-substance corrections this slice — all dispositions ratified at TRI-1 and applied in fix block before /build-slice. Mid-build refinements below are Conformance-class deviations recorded in build-log §Design deviations.)

- **TF-1 plan row count drift**: design.md AC mapping said "AC#1, 4 tests"; mission-brief TF-1 plan declared 18 rows; reality is 20 test functions in `test_pcr_2a_vault_claim_resolver.py` (mid-build addition of 2 predicate-level tests). Build-log records the deviation as Conformance class. Vault not edited because:
  - Mission-brief is frozen at /critique-review time per TPHD-1 sub-mode (a)+(b) discipline.
  - Build-log captures the authoritative "what actually shipped" record.
  - code-Critic m4 explicitly classifies this as out-of-scope-for-code-review per slice-060 Dim 9 (design-meta TPHD-1 + PTFFD-1 surface).
- **Pin #2 regex specification refined mid-build**: original mission-brief AC#3 specified Pin #2 via prose `re.search(r"VAULT_CLAIM[^\n]+fall[- ]closed", L192)` returns None; APED-1 execution at build time showed this regex was over-broad (it matched legitimate post-PCR-2a corner-case prose `claimed_at-tie + ... fall through to SOAD-1`). Refined to `r"VAULT_CLAIM\s*\([^)]+\)\s*\+\s*HARD\s*\("` (matches only the pre-fix multi-class enumeration shape). Build-log records the refinement.

## Discovered

- **R-23 — Cross-machine clock-skew in PCR-2a strict-newer rule** (low/low/cheap/open) — registered in `architecture/risk-register.md` at Phase F per m9 ACCEPTED-PENDING + /critique-review M-add-2 ACCEPTED-FIXED precedent. Corrigibility hook = audit log records both Claimed-at timestamps for forensic skew detection. Remediation candidates: (a) queue candidate `add-claim-sequence-number-for-clock-skew-detection` (registered in `architecture/slice-queue.md`); (b) PCR-2b Critic-stack adjudication.
- **code-Critic surfaces 5 minors that the design-Critic stack structurally could not reach** — m1 DRY in audit-formatter re-derivation, m2 PSQ-1 sentinel-overload, m3 atomicity-discipline-asymmetry vs PCR-1, m4 design.md stale TF-1 count, m5 sentinel-inheritance documentation. **3-Critic stack N=13 cumulative complementarity stable** (extends slice-077 N=12). All 5 advisory; none block ship. Voluntary-restraint discipline N=18 cumulative (slices 037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/075/077/078) — code-Critic v1 findings consistently route to bundled cleanup.
- **PCR-2a scope was wider than initial "SMALL-MEDIUM" labeling implied** — the slice shipped 1 sentinel + 6 helpers + 7-step algorithm + 2 dispatch site rewires + audit-log class dispatch + 5 new test modules + 1 changelog entry + 1 ADR + 1 risk-register entry + 1 queue candidate + 1 shippability row + 2 stale-test repairs. The effort fit ~1 day as estimated, but the surface count exceeded the original mission-brief AC#1's "1 unit test module" assumption. Recorded as instructive sizing signal for future PCR-2b scoping.
- **Self-validating-slice property N=2 cumulative** (extends slice-077 N=1) — slice-078's own `/commit-slice --merge` invocation could theoretically exercise VAULT_CLAIM auto-resolution if a peer Claude session claims a candidate concurrently. Cooperative-acceptable corner case. Pattern: structural improvements to the parallel-slice family naturally dogfood themselves at the slice's own merge time.

## Deferred

- **bundle-074-075-077-078-code-critic-cleanup** — accumulated code-Critic findings across 4 slices (5 from slice-078; ~13 from slice-077; ~2 from slice-075; ~5 from slice-074). Voluntary-restraint N=18 cumulative. Strongest candidate when the bundle finally lands (slice-079+); per slice-queue.md still pending.
- **PCR-2b — HARD-conflict full Critic stack + TRI-RESOLVE-1** — slice-079 candidate per slice-076 + slice-077 + slice-078 forward-references. Promoted to top of slice-queue.md at slice-077 /slice Step 6.5. ADR-071 §Consequences explicitly nominates slice-079.
- **SP-1 — `/slice` no-arg auto-pick** — slice-080+ candidate per slice-076 + slice-077 deferrals.
- **R-23 corrigibility fix candidates** — monotonic claim sequence number OR PCR-2b Critic-stack adjudication. Queue candidate registered; remediation timing depends on N≥2 cross-machine skew occurrence trigger.
- **"MISSING-FIELD" Parallel-safety sentinel** (m2 code-Critic) — bundled cleanup.
- **AC test count harmonization** (m4 code-Critic) — design.md AC mapping update OR formal acceptance of build-log-as-truth-of-record; bundled cleanup.
- **`_VaultClaimDispatch` catch-clause-order clarity comment** (m5 code-Critic) — bundled cleanup.

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` `## Triage` table + reality observed during build/validate:

### First-Critic (design-Critic) findings — 16 dispositioned at TRI-1

- **B1** (parser mismatch — `parse_queue_md` non-existence + `parse_queue_text` strips `Parallel-safety`): **VALIDATED** — disposition ACCEPTED-FIXED; Option (b) inline helper `_parse_queue_candidates_for_replacement` ships; tests confirm regex-based file-order-preserving parser works.
- **B2** (single-direction repro structural incoherence): **VALIDATED** — disposition ACCEPTED-FIXED; single PASS-post-fix function + build-log Events FAIL→PASS contrast pattern works per slice-024 / slice-014 precedent.
- **B3** (AC#2 omits CLI-facing `resolve_soft_conflict` dispatch site): **VALIDATED** — disposition ACCEPTED-FIXED; `test_resolve_soft_conflict_dispatches_vault_claim_into_pcr_2a` confirms the L242 branch is load-bearing.
- **M1** (tie-rate honest framing under second-precision `_now_iso8601_utc`): **VALIDATED** — disposition ACCEPTED-FIXED; ADR-071 §Options Option 1 cons rewrite is accurate.
- **M2** (em-dash vs hyphen audit-row separator fragility): **VALIDATED** — disposition ACCEPTED-FIXED; uniform hyphen-space ships cleanly with zero downstream blast-radius (independent meta-Critic blast-radius grep verified).
- **M3** (APED-1 pin literal under-specification): **VALIDATED** — disposition ACCEPTED-FIXED; the over-broad initial regex shape WAS caught at APED-1-execution time at build, exactly as the Critic warned. **Pin #2 mid-build refinement is itself evidence the M3 concern was load-bearing.**
- **M4** (write semantics — winner-in-stage-2 demotion): **VALIDATED** — disposition ACCEPTED-FIXED; 7-step Resolution algorithm shipped; `test_timestamp_winner_when_newer_in_stage_2` demonstrates stage-agnostic correctness.
- **m1** (line-number drift across 4 sibling artifacts): **VALIDATED** — disposition ACCEPTED-FIXED; canonical "L627-638" propagated.
- **m2** (multi-candidate collision helper shape): **VALIDATED** — disposition ACCEPTED-FIXED; `_collect_same_candidate_different_identity` added.
- **m3** (HEAD-SHA field redundancy): **VALIDATED-OVERRIDE** — disposition OVERRIDDEN by user with rationale "section-type symmetry across SOFT/VAULT_CLAIM/HARD is load-bearing for forensic readers". Reality confirms the override: `test_vault_claim_event_row_format` exercises the field; symmetry preserved without ergonomic cost.
- **m4** (L192 cosmetic wording polish): **NOT-YET** — disposition DEFERRED to bundle-074-075-077-078-code-critic-cleanup; will re-score there.
- **m5** (3 distinct none-available branches): **VALIDATED** — disposition ACCEPTED-FIXED; 3 distinct test functions.
- **m6** (PMI-1 entry-pin name pre-spec): **VALIDATED** — disposition ACCEPTED-FIXED; `test_v_0_74_0_pcr_2a_entry_present_in_repo` shipped with canonical name.
- **m7** (audit log absent on disk): **VALIDATED** — disposition ACCEPTED-FIXED; `test_log_is_append_only_across_section_types` correctly seeds prior SOFT row.
- **m8** (wiring matrix omits `resolve_soft_conflict`): **VALIDATED** — disposition ACCEPTED-FIXED; folded into B3 wiring entry.
- **m9** (clock-skew accepted-residual lacks corrigibility detection signal): **VALIDATED** — disposition ACCEPTED-PENDING applied during /build-slice Phase F; R-23 + queue candidate registered.

### Meta-Critic (critique-review.md) findings — 2 M-add dispositioned at TRI-1

- **M-add-1** (Resolution algorithm step 3 silent-drop when winner block lacks `Risk-retired:` pivot): **VALIDATED** — disposition ACCEPTED-FIXED; defensive post-overlay regex + STOP fail-closed shipped; `test_overlay_silently_dropped_returns_stop` demonstrates the protection. The meta-Critic catch was load-bearing — without it the resolver would silently ship a stale loser identity on a malformed block.
- **M-add-2** (Step 4 disk-read race silently breaks loser-auto-re-pick): **VALIDATED** — disposition ACCEPTED-FIXED; `_pick_loser_replacement` signature change to in-memory text input AND `test_pick_loser_replacement_reads_resolved_text_not_disk` demonstrate the contract. The meta-Critic catch was load-bearing — without it AC#1's loser-auto-re-pick would silently return `none-available` for every real-world VAULT_CLAIM scenario (`architecture/slice-queue.md` IS the U-file during VAULT_CLAIM rebase-in-progress; disk reads encounter conflict markers).

### Code-Critic findings — 5 minors dispositioned at TRI

- **m1** (audit-formatter DRY re-derivation): **NOT-YET** — DEFERRED to bundled cleanup.
- **m2** (PSQ-1 sentinel-overload of `"UNKNOWN-NO-GRAPH"`): **NOT-YET** — DEFERRED.
- **m3** (atomicity discipline asymmetry vs PCR-1): **NOT-YET** — DEFERRED (documentation comment).
- **m4** (design.md stale TF-1 count): **NOT-YET** — DEFERRED.
- **m5** (sentinel-inheritance documentation): **NOT-YET** — DEFERRED.

### Missed by Critic

- **Pin #2 regex over-broad shape** — first-Critic M3 specified the structural pin in prose but did not pre-execute the regex against the actual L185-192 prose. The over-broad regex matched legitimate post-PCR-2a corner-case fall-through prose. Build-time APED-1 execution caught the issue. **Pattern**: design→code translation gap N=15 cumulative (extends slice-077's N=14). The first Critic's M3 finding itself flagged the APED-1-execution requirement — the Critic spec'd the discipline but didn't apply it to its own proposed pin literal. /critic-calibrate next-run candidate.
- **PCR-2a `_format_vault_claim_audit_entry` re-derivation pattern** (code-Critic m1) — design-Critic stack structurally cannot reach line-level audit-formatter implementation choices; only code-Critic could catch.
- **PSQ-1 sentinel-overload risk** (code-Critic m2) — design-Critic stack does not parse default-value semantics in line-level parser code.
- **Atomicity discipline asymmetry vs PCR-1** (code-Critic m3) — design-Critic stack does not cross-compare to the slice-076 SOFT-path's `pending_writes` batch pattern at line-level granularity.
- **design.md stale TF-1 count** (code-Critic m4) — TPHD-1 / PTFFD-1 surface; design-Critic only reviews the pre-build design.md content frozen at /critique time.
- **`_VaultClaimDispatch` sibling-not-inheritance ordering subtlety** (code-Critic m5) — pure code-clarity concern; design-Critic stack does not read code.

### Pattern

**3-Critic stack N=13 cumulative complementarity stable** (slice-063 → slice-078 inclusive). code-Critic m1-m5 are STRUCTURALLY UNREACHABLE by design-Critic + meta-Critic stack which read mission-brief/design at /critique time but don't run APED-1 / line-level parser-default-semantics / atomicity-cross-comparison against fresh code. Pattern stable. **Do NOT collapse the 3-Critic stack.**

**Design→code translation gap N=15 cumulative** (extends slice-077's N=14). The first Critic spec'd the APED-1 discipline at M3 then did not apply it to the proposed pin literal. /critic-calibrate next-run candidate.

**Voluntary-restraint discipline N=18 cumulative** (extends slice-077's N=17). Bundle-074-075-077-078-code-critic-cleanup awaits.

## Lessons for next slice

- **When a /critique finding spec'es an APED-1-execution discipline for ITSELF, run the APED-1 execution against the proposed structural pin literal AT /critique TIME, not at build time** — saves the mid-build refinement round. Pattern this slice: M3 spec'd Pin #2 in prose; build-time APED-1 caught over-broadness. Pin #2 could have been refined at TRI-1 if the regex shape had been executed at /critique time against the actual L185-192 prose. /critic-calibrate proposal target.
- **For mid-build TF-1 plan growth that adds predicate-level tests, accept the build-log-as-truth-of-record pattern rather than retroactively edit design.md AC mapping** — Conformance-class deviation per TPHD-1 sub-mode (a) discipline; design.md is frozen at /critique-review time. m4 code-Critic OPTIONAL-update (bundled cleanup) confirms this stance.
- **PCR-2a sized as "SMALL-MEDIUM" effort but shipped wider surface than the AC#1 "1 test module" assumption implied** — for PCR-2b sizing, allocate up-front for at least: 1 spawned Critic stack invocation per HARD-conflict + TRI-RESOLVE-1 user triage gate + 4-5 new helpers + 5+ test modules. Likely LARGE effort despite mission-brief's "MEDIUM" labeling at slice-076 reflection. Plan for splitting if Step 5 hard limits trigger.
- **Self-validating-slice property N=2 cumulative** — slice-077 + slice-078 both touched the parallel-slice family AND structurally dogfooded themselves at /commit-slice --merge. Watch for pattern continuation in slice-079 PCR-2b; if continues, codification candidate at /critic-calibrate.

## Vault updates made (thin vault — small list)

- [[risk-register.md]] — added R-23 "Cross-machine clock-skew in PCR-2a strict-newer rule" at Phase F per m9 ACCEPTED-PENDING discharge.
- [[slice-queue.md]] — added candidate `add-claim-sequence-number-for-clock-skew-detection` at Phase F (R-23 corrigibility hook).
- [[shippability.md]] — added row #78 (slice-078 catalogued regression `test_pcr_2a_repro_vault_claim_gate_closed.py::test_vault_claim_gate_closed_returns_resolution_result`) at Phase G.
- [[methodology-changelog.md]] — v0.74.0 entry minted (RULE-ID PCR-2a) at Phase E.
- [[decisions/ADR-071.md]] — minted at /design-slice; status: accepted (no edits at /reflect).
- [[VERSION]], [[plugin.yaml]], [[pyproject.toml]] — 5-part PMI-1 bump synchronized at 0.74.0.
- Installed `~/.claude/methodology-changelog.md` + `~/.claude/ai-sdlc-VERSION` + `~/.claude/skills/commit-slice/SKILL.md` — forward-synced.
- venv `ai-sdlc-tools` 0.73.0 → 0.74.0 via `pip install --upgrade .`.
- This slice's [[design.md]] — NOT edited at /reflect (build-log captures Conformance deviations; design.md frozen at /critique-review time per TPHD-1 sub-mode (a)).
- This slice's [[mission-brief.md]] — TF-1 statuses updated PENDING → PASSING (20/20) at Phase G; otherwise frozen.

## Critic calibration cadence note

Slice-078 marks 3 slices since 2026-05-28 /critic-calibrate run (post-slice-075). CAL-1 cadence: within window (3 of 20-slice budget; no flag). /critic-calibrate next-run trigger: at ~slice-086+ default OR earlier if /critic-calibrate-fit signal accumulates (e.g., design→code translation gap N=15 cumulative; voluntary-restraint N=18 with bundled-cleanup landing; APED-1-execution-at-/critique-not-build pattern as new candidate codification target).
