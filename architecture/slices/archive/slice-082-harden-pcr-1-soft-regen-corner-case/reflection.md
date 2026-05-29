# Reflection: Slice 082 harden-pcr-1-soft-regen-corner-case

**Date**: 2026-05-29
**Shipped**: YES

## Validated
- The SOFT auto-regen DID have silent-divergence vectors exactly as R-21 anticipated — validated empirically: the malformed-block claim drop (`_overlay_claims_on_queue_text`) and the discarded-prelude drop (`_merge_shippability`) both reproduced as RED tests against the real resolver before the guard.
- Fix-class (b) "Extend SOFT-set audit" was the right choice — the guard is a single read-only predicate + one call-site, preserves the happy path byte-for-byte (full PCR suite 161 PASS, full repo suite 1173 PASS), and converts the divergence vectors to loud STOPs. ADR-074 reversibility=cheap held.
- Atomicity claim validated: `test_stop_leaves_repo_state_unmutated` confirms a guard-STOP leaves the U-file's conflict markers + the rebase-in-progress untouched (`regenerated_files == ()`).

## Corrected
- **Design re-parse plan (B1)** → the named helpers (`_parse_queue_candidates_for_replacement`) cannot supply invariant #1's inputs (they strip claim metadata); corrected in design.md to re-derive `merged_claims` via `_git_show_stage`+`_extract_claim_diff`+`_merge_claim_dicts` + a local heading regex. Applied at /critique.
- **Invariant #1 domain (M-add-1)** → design originally checked all `merged_claims` keys; reality is `merged_claims` includes UNCLAIMED candidates (from `parse_queue_text`), so the unrestricted check would false-STOP the happy path / break AC-4. Corrected to the claimed subset only. Caught by the meta-Critic, applied before build.
- **Guard call-site routing (m1 design-deviation)** → design said the guard-STOP "routes through the existing `except` with zero ladder change"; reality is the pinned post-empty-check call-site is OUTSIDE the original loop-try, so a LOCAL `try/except _SoftResolutionError` was required (still no new exception type). Logged in build-log.md; design wording updated at /critique.
- **Heading regex normalization (code-Critic M1)** → the guard's `^### (.+)$` did not `.strip()` while the canonical `parse_queue_text` rstrips; a trailing-whitespace baseline heading silently bypassed invariant #1. Corrected in-loop (all 3 heading captures now `.strip()`) + adversarial test added.
- [[risk-register#R-21]] → flipped to **retired** (the regen-logic divergence class is structurally closed by the guard).

## Discovered
- **Rebase-stage inversion**: `git rebase master` (on branchA) assigns stage 2 = master, stage 3 = branchA (the `_regen_slice_queue` baseline), and `_merge_claim_dicts` keeps the stage-2 entry when stage-3's `claimed_at` is absent. Inverts the naive ours/theirs intuition — captured in the test helper docstring for future PCR test authors. Impact: any future PCR test must set fixture content by branch, not by stage number.
- **Truncated/corrupt-baseline residual** → added as [[risk-register#R-24]] (low/low, deferred to PCR-2b). The guard cannot distinguish a corrupt baseline from legitimate top-10 churn at the name level; warn-not-STOP is the deliberate happy-path-preserving choice (M2).
- **ETC-1 vs TF-1 field-parser inconsistency**: ETC-1's enable-flag regex is `$`-anchored (`(true|false)\s*$`) and rejects a trailing parenthetical that TF-1's looser parser tolerates. Cost one validate-time round-trip. Impact: a cross-skill cleanup / `/critic-calibrate` candidate (harmonize the two field parsers); non-blocking.

## Deferred
- **PCR-2b HARD-class conflict resolution** — the largest remaining parallel-slice-family gap; R-24's truncated-baseline residual + R-23's clock-skew Critic-adjudication both land there. Lands in: a future slice (next-slice candidate).
- **R-24 truncated-baseline guard** — warn-only this slice; STOP-via-Critic-adjudication deferred to PCR-2b. Lands in: PCR-2b.

## Critic calibration

Per TRI-1, scored from `critique.md` `## Triage` + `critique-review.md` + reality during build/validate:

- **B1** (invariant #1 re-parse can't use field-stripping helpers): **VALIDATED** — ACCEPTED-FIXED; the named helpers genuinely couldn't supply the inputs; re-derivation worked exactly as prescribed.
- **M1** (non-numbered row content-mutation): **VALIDATED** — ACCEPTED-FIXED; symmetric invariant #3 catches `| 5,6 |`/`| 030C |` prelude rows; pinned by `test_equivalence_guard_stops_on_unprovable_equivalence`.
- **M2** (orphan-exemption truncated-baseline): **VALIDATED (concern)** — ACCEPTED-PENDING with the Critic's literal fix OVERRIDDEN (loud-audit-not-STOP); the meta-Critic + reality both confirmed the override was correct (STOP-on-cross-stage-drop would false-STOP legitimate churn). Residual → R-24.
- **M3** (atomicity/placement unstated fact): **VALIDATED** — ACCEPTED-FIXED; call-site pinned read-only; atomicity confirmed by test.
- **m1** (verdict-class ambiguity): **VALIDATED** — ACCEPTED-FIXED; reused `_SoftResolutionError`.
- **m2** (audit variant + unmutated scope): **VALIDATED** — ACCEPTED-PENDING; grep confirmed no closed-set heading assertion; scope clarified.
- **M-add-1** (meta-Critic; unclaimed-subset false-STOP): **VALIDATED** — ACCEPTED-FIXED; a genuine AC-4-breaking defect the FIRST design-Critic missed (B1 fixed the re-parse mechanics but not that `merged_claims` over-includes). Meta-Critic earned its keep.

**Missed by Critic**:
- **code-Critic M1 (trailing-whitespace heading bypass)** — MISSED by BOTH the design-Critic AND the meta-Critic AND the Builder through design+build. Caught only by the code-Critic reading the LITERAL regex against the canonical rstrip parser. This is the textbook 3-Critic-stack complementarity: the design stack reasons about behavior; the code-Critic reads the literal code. A parse-rule (regex) shipped without an adversarial-variant execution — the exact slice-081 "assert BOTH boundaries / anchored-claim needs adversarial execution" class, recurring N+1.

**Pattern**: 3-Critic stack complementarity holds and compounds — design-Critic (B1/M1/M2/M3 conceptual + contract) + meta-Critic (M-add-1, the domain-over-inclusion the first Critic's own fix introduced) + code-Critic (M1, the literal-regex normalization gap none of the prose-readers could reach). Do NOT collapse the stack. **New recurring class at N≥2**: "a slice introducing a new parser/regex MUST execute it against the canonical parser's normalization (rstrip/strip/anchor) as an adversarial-variant test" (slice-081 anchored-matcher + slice-082 heading-regex). Candidate for a /critique dimension or a build-check at N=3.

## Lessons for next slice
- **When a slice adds a new regex/parser that must agree with an existing canonical parser, write the parity test FIRST** (feed the canonical parser's normalization edge — trailing space, CRLF, leading whitespace, annotation suffix). The code-Critic caught M1 only because it read the literal regex; bake that into the design-time test plan so the design stack doesn't have to.
- **Rebase stage assignment is inverted vs intuition** (stage 2 = rebase-target/master, stage 3 = replayed-branch/baseline) and `_merge_claim_dicts` is asymmetric on absent `claimed_at`. Any PCR test author: set fixtures by branch, verify the stage mapping empirically before asserting.
- **Self-validating-slice property N=3 on the PCR family** (slice-077 worktree-awareness, slice-078 PCR-2a, slice-082 equivalence guard) — each touched the parallel-slice family AND is exercisable on its own `/commit-slice --merge`. The lessons flagged N=3 as a codification trigger; PCR-2b is the natural place to codify "parallel-slice-family slices dogfood their own merge."
- **MEPD-1 EXCLUDE for a risk-closing fix-slice with an ADR but no new RULE-ID** is the right call (slice-077/079 precedent) — avoids the heavy PMI-1/AVFS-1/MCFS-1/TVFS-1 forward-sync machinery when no rule is minted.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-21 flipped to **retired** (closed by the equivalence guard); **R-24** added (truncated-baseline residual, deferred to PCR-2b).
- [[decisions/ADR-074-soft-regen-equivalence-guard.md]] — accepted (written at /design-slice).
- `architecture/shippability.md` — row 88 (equivalence-guard pin) added at build.
- `architecture/drift-log.md` — slice-082 audit entry + DCE-1 trigger.
- This slice's `design.md` — B1/M1/M2/M3/m1/m2/M-add-1 fixes (at /critique); the code-Critic M1 strip refinement is captured in code comments + build-log + code-review.md (design line citations are approximate post-insertion per the drift-log minor).
- No methodology-changelog / VERSION edit — MEPD-1 EXCLUDE (no new RULE-ID).
