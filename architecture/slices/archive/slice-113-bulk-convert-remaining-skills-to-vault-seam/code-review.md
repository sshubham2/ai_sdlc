# Code Review: Slice 113 bulk-convert-remaining-skills-to-vault-seam

**code-Critic reviewed**: slice diff vs default branch (worktree `slice-113-bulk-convert-remaining-skills-to-vault-seam`, base `8a3896b`), filtered to in-scope paths
**Date**: 2026-06-04
**Result**: FINDINGS

## Summary

The headline tool change (op-gate seam-awareness, ADR-106) is correct and well-tested: the matcher/extractor lockstep is real, non-vacuous (2 of the 3 new tests genuinely go red when the extractor is reverted to `_PATH_TOKEN_RE`, proven by execution), the `_OP_SINK_RE`/`_MATCH_RE` separation holds, all re-pins (`EXPECTED_TOTAL=129`, floor `127`, `_BASELINE_SHA256`, op-floors `{6,11,23,0}`) recompute exactly, and the 43 `_CONVERTED_CARVEOUTS` hashes are all live with zero stale/missing entries. The full methodology suite is green. **One real defect**: three git-pathspec literals in `skills/code-review/SKILL.md` were wrongly converted to `<vault>/`, violating the slice's own must-not-defer ("git-pathspecs stay concrete, class-1") and its own catalogued regression clause (shippability row 119).

## Changed files (in-scope)
```
tools/vault_flip_prose_inventory.py
tests/methodology/test_vault_flip_op_gate.py
tests/methodology/test_vault_flip_prose_inventory.py
tests/methodology/test_validate_slice_skill.py
skills/adopt/SKILL.md ... skills/validate-slice/SKILL.md (23 converted skill SKILL.md)
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

#### B1: Three git-pathspec exclusion literals wrongly converted to `<vault>/` in `skills/code-review/SKILL.md` (must-not-defer + ADR-105 class-1 violation)

- **Claim under review**: `skills/code-review/SKILL.md:102/104/105` — the "Out-of-scope paths" bullet list (line 100 explicitly states it is "pruned via inline `:(exclude)` pathspecs on each of the three union legs"):
  ```
  102: - `<vault>/decisions/**` — ADRs are reviewed by `/critique` ...
  104: - `<vault>/slices/_index.md` — slice index, maintained by `/reflect`
  105: - `<vault>/slices/archive/**` — archived slice content, frozen historical record
  ```
- **Issue**: These three bullets are the prose mirror of class-1 **git-pathspec** literals. The mission-brief must-not-defer is explicit: *"Git-pathspecs stay concrete (class-1, M-add-2) — `:(exclude)architecture/…` are git-consumed (silent-wrong on non-substitution), NOT converted."* Their siblings (line 103 `:(glob)architecture/*.md`, lines 106-107 `architecture/slices/*/{milestone,code-review}.md`) correctly stayed concrete — a within-list inconsistency confirming this was an error, not an intentional carve-out.
- **Evidence**: The **executable** commands (lines 46-85, the fenced `git diff ... :(exclude)architecture/decisions/**` legs) were correctly left concrete — so `/code-review` still runs today; the prose block now contradicts the command it documents. The slice's own consumer test pins the command concrete: `tests/skills/code_review/test_code_review_skill.py:241-244` asserts `':(exclude)architecture/decisions/**'` etc. — green only because it asserts the command, not the prose, so the conversion slipped past it. Shippability row 119 names this as a regression: *"OR git-pathspecs get converted (silent-wrong git exclusion set, M-add-2)."* Confirmed by execution: these three lines dropped out of the inventory (0 occurrences post-conversion).
- **Scope note**: prose-description mirror, not the executable command — does not break `/code-review` at runtime today. Filed Blocker because (a) it is an explicit must-not-defer item the pre-finish gate requires "fully addressed," and (b) a future "sync prose to command" edit would propagate `<vault>/decisions/**` into the executable `:(exclude)` pathspec → git matches nothing → ADRs/index/archive silently re-enter code-review scope (the class-1 silent-wrong failure).
- **Proposed fix**: Revert lines 102/104/105 to concrete (`architecture/decisions/**`, `architecture/slices/_index.md`, `architecture/slices/archive/**`), matching siblings 103/106/107 + the executable command. They are class-1 flip-residual. Re-run `--strict`; confirm they re-enter the inventory as `git-pathspec`. NOTE: the many *other* `<vault>/slices/_index.md` conversions (adopt/archive/slice/pulse) are CORRECT — plain read/lookup references to a shared-aggregate index that relocates with the vault; only the three inside code-review's `:(exclude)` block are wrong.

### Majors
None. (B2 lockstep, all re-pins, carve-out hashes, code-review-un-ratcheted soundness, and conversion completeness all verified clean by execution.)

### Minors

#### m1: One of the three new op-gate tests does not detect the extractor-revert mutation it claims to guard against
- **Claim under review**: `tests/methodology/test_vault_flip_op_gate.py:245-249` docstring — *"each of these FAILs if the value EXTRACTOR is not upgraded ... bare prefix and every sink sub-regex misses."* ADR-106:43 *"Non-vacuity is pinned by three new `<vault>/`-sink op-gate tests."*
- **Issue**: Reverting `_OP_SINK_TOKEN_RE`→`_PATH_TOKEN_RE`: the active-folder + slice-queue tests go RED (non-vacuous ✓), but `test_seam_aware_vault_unrouted_aggregate_still_bites` (expects `OP_UNROUTED`) STAYS GREEN — `<vault>/risk-register.md` lands OP_UNROUTED both ways (correctly via full value; incorrectly via bare-`<vault>/` fall-through). It proves the matcher widening, not the extractor lockstep.
- **Proposed fix**: strengthen the assertion to also assert `"risk-register.md" in ops[0].value` (red on the bare-`<vault>/` collapse → genuinely extractor-sensitive), OR soften the docstring/ADR wording to "two of the three." The lockstep is adequately pinned by the other two regardless.

## Dimensions checked
- [x] Unfounded assumptions — m1 (the "each of three" non-vacuity claim overstates; the other in-code claims — baseline, EXPECTED_TOTAL, floors, {6,11,23,0}, slice:264 — all recompute exactly).
- [x] Missing edge cases — none. Regex probed: empty/no-slash, non-boundary `<`, terminators, worktree-composed mid-string, CRLF (universal-newlines read), ReDoS (linear, 0.4ms/100k).
- [x] Over-engineering — none. The `_OP_SINK_RE`/`_MATCH_RE` duplication is justified + documented.
- [x] Under-engineering — none. All 5 ACs have delivering code; the 3 un-converted-but-guarded skills (query-design/critique-review/slice-candidates) verified to have 0 convertible literals.
- [x] Contract gaps — none. Op-gate JSON shape + exit codes unchanged; M3 mutation test verified non-vacuous.
- [x] Security — none. Static prose audit; no shell=True/eval/exec/input boundary.
- [x] Drift from vault — B1 (code-review.md:102/104/105 contradicts the must-not-defer + shippability row 119). No other drift.
- [x] Web-known issues — Skipped (no external API/SDK; Python `re`/`hashlib`/`json` stdlib; semantics stable 3.11–3.13).
- [x] Cross-cutting conformance — APED-1 satisfied (the changed parse rule executed against an adversarial battery); RSAD-1 (the slice's own converted code survives its own ratchet + op-gate); the AP-10 docstring fan-out done correctly. The parity misses are B1 + m1.

---
**Disposition (post-review, applied this round)**: B1 ACCEPTED-FIXED — reverted the 3 git-pathspec prose literals + re-pinned the inventory cascade. m1 ACCEPTED-FIXED — strengthened the third op-gate test assertion to be extractor-sensitive. See build-log Events.
