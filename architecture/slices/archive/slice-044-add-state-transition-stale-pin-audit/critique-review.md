# Critique Review: Slice 044 add-state-transition-stale-pin-audit

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-18
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's eight findings are individually sound and all VALID at correct severity — the corpus-survey methodology (empirically reproduced, Builder re-verified) was disciplined. But the Builder's ACCEPTED-FIXED revisions **relocated the flaw twice** (slice-041 pattern, now at the meta-Critic layer): the B1 fix's "exclude *all* `BoolOp`-nested membership" clause blinded Sub-form A to ~45 of ~140 positive prose-pins (32% coverage hole, including genuine R-10-class pins), and the Sub-form B fn-token regex transcribed into design.md as the B/M1 fix **did not match its own cited `test_r_4_..._stays_mitigating` precedent** when executed (`\b` is never a boundary adjacent to `_`). Both were caught only by executing against the real artifact. Both have been re-fixed by the Builder in this round (design.md§Sub-form-A per-operand BoolOp clause + `_`-delimited regex; ADR-047 residual #1; mission-brief verification rows 1b, 2c, AC4 signature-specificity).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (NotIn false-positive) — confirmed; Blocker appropriate. Exactly 2 live `not in` pins (`test_commit_slice_skill_merge_flag.py:38,57`). Fix *direction* right; *over-breadth* is B-add-1 below.
- **B2** (function-local + sliced-segment binding) — confirmed; Blocker appropriate. 21 local + 7 module-level `read_file` assigns / 19 files; `test_build_slice_skill_branch_create.py:27,40` is the cited `content.split("## …",1)[1]…` shape. Presence-vs-full-SKILL.md fix sound.
- **B3** (folded-constant extraction) — confirmed; Blocker appropriate. `ast.parse` on `test_build_slice_skill.py:162-166` executed: CPython folds the 3-line implicit-concat into one `ast.Constant`; `node.left` is directly `ast.Constant` (not `BinOp`/`JoinedStr`). `ast.Constant.value` fix mechanically verified.
- **M1** (merge-base/changed-file semantics) — confirmed; Major appropriate.
- **M2** (default-branch object-identity reuse) — confirmed; Major appropriate. `_resolve_default_branch`/`_run_git` exist as importable objects; reuse-by-identity achievable.
- **M3** (qualified `conftest.read_file` YAGNI + `assert_md_forward_synced` boundary) — confirmed; Major appropriate. Zero qualified-call instances; the single inline `read_bytes` RHS (`test_skill_drift_normalization.py:91`) is correctly inside the M3-excluded EOL-DRIFT-1 family.
- **m1** (shippability 6-col / SCMD-1 / PTFFD-1 / row-LAST) — confirmed; Minor appropriate.
- **m2** (ADR-047 introduced residuals) — confirmed; Minor appropriate; ADR-047 §"Introduced residuals" records both.

## Suspicious findings

None. Every first-Critic finding survives closer reading of design.md and empirical re-execution.

## Missed findings

- **B-add-1: The B1 fix relocated the flaw — excluding *all* `BoolOp`-nested membership blinded Sub-form A to ~45 positive `in` pins** (Hendrickson missing-edge-case; slice-041 flaw-relocation pattern). Corpus-executed: 140 positive `in` pins, **45 nested in a `BoolOp`** that the original B1-fix clause excluded entirely — not negative pins but conjoined positive assertions of load-bearing literals: `test_build_slice_skill.py:187-190` (`"audit-enforced gate" in BUILD and "NON-`-D` per ADR-019" in BUILD` — a textbook R-10-class pin), `test_build_slice_skill_branch_create.py:43` (`"slice/" in prereq_block and "NNN" in prereq_block`). AC2's "R-10's exact class" coverage was materially weakened a second time (same defect-shape as B2). **Builder draft**: ACCEPTED-FIXED — design.md§Sub-form-A "Positive-membership only — per-operand, NOT whole-BoolOp" clause (exclude only own-`NotIn` or `BoolOp`-with-`NotIn`/non-constant-sibling; positive-only chains evaluated per-operand; build-time machine-classification of the full BoolOp-pin set) + Non-false-positive guarantee bullet 1 + ADR-047 residual #1 + mission-brief verification row 2c. Empirically re-verified: positive-only `BoolOp` pins exist with zero `NotIn` siblings.

- **M-add-1: The Sub-form B fn-token regex did not match its own cited precedent when executed** (Wiegers verifiable-requirement; slice-039 oracle-applied-at-TRI-1-without-mechanical-recompute + slice-042 transcribed-from-non-authoritative-source N≥4). design.md line 14 specified `r[_-]?<num>.*\b(stays|remains|is)_<oldstatus>\b`. Executed against `test_r_4_stays_mitigating` (ADR-047 line 18; the precedent this slice exists to catch) → **NO match**: `_` is `\w`, so `\b` is never a boundary adjacent to `_`; `\b(stays…)` cannot match after the snake_case `_` delimiter (this repo's universal convention). The corrected `r[_-]?\d+.*_(stays|remains|is)_(\w+)` was executed and matches `test_r_4_stays_mitigating` while rejecting the realigned `test_r_4_retired_by_slice_041_…`. As originally written, Sub-form B's fn-token leg was dead — zero real stale risk-status pins caught. **Builder draft**: ACCEPTED-FIXED — design.md line 14 regex replaced with the `_`-delimited form + rationale; mission-brief verification row 1b (mechanical contrast: regex vs literal `test_r_4_stays_mitigating` → match; vs realigned name → no-match). Empirically re-verified (`re.search` on both forms).

## Severity adjustments

- **AC4 vs `Test-first: false` (m-add — SEVERITY: Minor, advisory).** AC4 requires the R-10 regression "written FIRST, FAILs vs the unmodified tool, PASSES post-impl" while header sets `Test-first: false`. Internally coherent (slice-037 catalogued-repro precedent: a single targeted failing repro ≠ full TF-1). But the genuine-contrast is only real if the repro asserts an exit-1 *signature* (kind + named literal), not merely exit≠0 — else B-add-1's coverage hole could let the tool exit 1 for the wrong reason and the repro still "pass." **Builder draft**: ACCEPTED-FIXED — mission-brief AC4 + verification row 4 now require asserting `kind == "stale-skill-prose-pin"` + the named folded literal, not `exit != 0`.

## Notes

Confidence high on both missed findings — each established by executing `ast.parse` / `re.search` against the real artifacts, not reasoning (slice-032/034/041 execute-don't-reason law, N≥4 at the DR-1 layer). The first Critic's detection work was excellent (8/8 VALID, correct severity); the failure was downstream — the Builder's ACCEPTED-FIXED edits exhibited the exact slice-041 "flaw relocates each revision" + slice-042 "fix transcribed from a non-authoritative source without recompute" patterns this slice was nominated to close, recurring inside the fix for this very slice. Calibration signal: when a Builder ratifies *all* findings ACCEPTED-FIXED in one round and self-revises three artifacts pre-triage, the meta-Critic's primary value is mechanical re-execution of the *fixed* spec, not re-litigation of the originals — that is where both real defects were found. One open reservation carried to /build-slice: B-add-1's per-operand `BoolOp` fix must be confirmed against the full 45-pin set by build-time machine classification (sampled ~15, all positive conjunctions), not assumed.

---

# Critique Review — ROUND 2 (Sub-form B git-independence deviation delta)

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-18
**First-Critic verdict**: BLOCKED (Round-2 targeted re-critique; all 6 ACCEPTED-FIXED → CLEAN)
**Dual-review verdict**: EXTEND

## Summary (Round 2)

The Round-2 targeted re-critique (B4/B5/M4/M5/m3/m4) is empirically sound — every fix re-derived against the live repo, none relocated the flaw. One missed finding: the Round-2 m3 fix corrected exactly one stale git-mechanism site in ADR-047 (Reversibility L64) but an equally-current one survived at ADR-047 L27 — the **Chosen** option still asserting Sub-form B is "git-diff-dependent."

## Confirmed findings (Round 2)

- **B4** VALID/Blocker — `ast.parse` sweep over `tests/**/*.py` (87 files): exactly one `SyntaxError` = `tests/methodology/fixtures/syntax_error.py`. Pre-fix exit-2 ⇒ STP-1 self-HALT at its own Step 6. Post-fix skip-with-visible-note ⇒ exit 0 on live tree. Verified.
- **B5** VALID/Blocker — fix applied to BOTH sub-forms (design.md L26/L51/L94/L101); the fixture doesn't even match the Sub-form A `test_*skill*.py` glob (21 Sub-form-A files all parse). No relocation; explicitly does not contradict/supersede ADR-037.
- **M4** VALID/Major — executed anchored regex: `test_addr_5_is_open`→None, `test_parser_4_is_retired`→None (old form bound `(5,is,open)`/`(4,is,retired)`; live R-5=retired → old form would have false-HALTed an innocent slice).
- **M5** VALID/Major — `test_r_4_stays_mitigating_until_spike_done`→`(4,stays,mitigating)` (fires); precedent `test_r_4_stays_mitigating`→`(4,stays,mitigating)`; realigned `…_retired_by_slice_041_…`→None. False-negative closed.
- **m3** VALID/Minor as filed (L64 fixed) — but scope too narrow (see Missed).
- **m4** VALID/Minor — design.md L56 now "no git state".
- Round-1 mooting confirmed: `_parse_risks` on live register → 10 risks, 0 violations, no exception (R-4=retired, R-5=retired, R-1=mitigating, R-2=open). M1 mooted, M2 residual dissolved, register-clean cannot trip exit-2.

## Suspicious findings (Round 2)

None. No fix relocated the flaw; slice-041 "flaw relocates" + slice-042 "Builder's own ACCEPTED-FIXED transcription error" patterns specifically checked and did NOT recur — post-fix regex literal is **character-identical** across design.md L14, ADR-047 L35, mission-brief L16 (zero transcription drift).

## Missed findings (Round 2)

- **m-add-R2-1** (Minor): ADR-047 Options-considered #3 (the **Chosen** option, L27) still asserted Sub-form B is "git-diff-dependent (compare register at merge-base vs working tree)" — m3 fixed only L64; L27 is the load-bearing rationale a reader reaches before the L35 Decision / L43 Deviation that correct it. FBCD-1 deviation-consistency sub-mode (a): m3's fix was incomplete (patched one occurrence, left an equally-current one in the same file). **Disposition**: ACCEPTED-FIXED — ADR-047 L27 struck-through + cross-referenced to the Deviation sub-section (mirrors L35 self-annotation). No executable impact (design.md L14 / ADR Decision L35 / mission-brief L16 unambiguous + git-independent) — ADR-internal documentation-consistency only.

## Severity adjustments (Round 2)

None. B4/B5 correctly Blockers (live-repo self-HALT / cited-precedent contradiction), M4/M5 correctly Majors (latent footgun / AC1 false-negative, neither blocks the clean live tree today), m3/m4/m-add-R2-1 correctly Minors (doc-consistency, no executable impact).

## Notes (Round 2)

High confidence — N≥6 empirical executions at the DR-1 layer (regex over 87 test files + 14 adversarial literals; full `ast.parse` sweep; `_parse_risks` on live register; character-compare of the regex across 3 sites; FBCD-1 git-prose grep over 4 files; Sub-form A glob/parse check). Calibration observation (NOT filed — speculative, never-witnessed, within declared scope per design.md Out-of-scope): `.search` binds only the first match, so a hypothetical compound `test_r_4_is_retired_and_r_5_is_open` would evaluate only R-4 — zero such names exist; the slice-041 precedent is single-claim; design.md explicitly bounds Sub-form B to the witnessed fn-name-token leg. Verdict EXTEND solely on m-add-R2-1 (a doc-consistency Minor); Round-2 fixes are substantively sound.
