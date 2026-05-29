# Critique: Slice 079 bundle-074-075-077-078-code-critic-cleanup

**Critic reviewed**: mission-brief.md, design.md (slice-079 pre-fix), source code-review files for slices 074/075/077/078, slice-077 design.md (L181-191 contract source), `tools/pulse_worktree_resolver.py`, `tools/parallel_conflict_resolver.py`, `tools/slice_queue_writer.py`, `skills/build-slice/SKILL.md`, `tests/methodology/test_methodology_changelog.py:136`, aggregated lessons, critic-calibration-log 2026-05-29 (Proposal 1 APED-1 self-application clause-5)
**Date**: 2026-05-29
**Result**: NEEDS-FIXES (2B + 3M + 6m; pre-triage)

## Summary

Design is sound on structural scaffolding (DEFER-with-rationale entries are legitimate per archive-immutability + extraction-trigger precedent; MEPD-1(b) discharge verified; no new methodology axis opened). Two substantive Blockers caught empirically via the just-applied APED-1 clause-5 self-execution: (B1) Fix K cited 8 UNKNOWN reason-keys that did NOT match the canonical `_UNKNOWN_REASONS` tuple in the cited contract source; (B2) Fix S's premise (UTF-8 missing) was empirically false — all 9 sites already explicit. Three Majors on contract surface choice + ambiguity + test constructability. Six Minors on WIRE-1 categorization, AND-vs-OR logic, count parentheticals, AC count off-by-one, effort estimate, and shippability row enumeration.

**Slice-079 is the N+1 first-governed-slice of /critic-calibrate Proposal 1 (APED-1 self-application clause-5 applied 2026-05-29).** The Critic empirically ran APED-1 grep at /critique time on both B1 + B2 cited contracts — the canonical self-application path. Findings B1 + B2 are the empirical demonstration that clause-5 closes the discipline-on-itself loop at first-Critic time. **APED-1 clause-5 was effective on its very first governed slice.**

## Findings

### Blockers (must address before /build-slice)

#### B1: Fix K cites 8 UNKNOWN reason-key strings that do NOT match the canonical contract at `tools/pulse_worktree_resolver.py:77-86 _UNKNOWN_REASONS` or slice-077 design.md L181-191

- **Claim under review**: design.md (pre-fix) Fix K: "add module-level constant `_UNKNOWN_REASON_WARN_TEMPLATES: dict[str, str]` mapping each of the 8 UNKNOWN sub-reasons enumerated at slice-077 design.md L181-191 (`milestone-malformed-yaml-frontmatter` / `milestone-stage-key-absent` / `milestone-stage-value-out-of-enum` / `worktree-not-registered` / `worktree-cwd-mismatch` / `worktree-path-shape-violation` / `default-branch-unresolvable` / `git-not-installed`)"
- **Issue**: The 8 keys named in Fix K are NOT the contract. APED-1 self-application clause-5 execution at /critique time grep'd `_UNKNOWN_REASONS` in `tools/pulse_worktree_resolver.py:77-86` — found the canonical 8 are completely different (the cited keys exist in `tools/branch_workflow_audit.py`, a different tool, NOT in `pulse_worktree_resolver.py`). Canonical set: `fresh-worktree-no-milestone` / `milestone-missing-in-active-and-archive` / `milestone-frontmatter-malformed` / `detached-head` / `dirty-worktree` / `merge-base-error` / `head-unresolvable` / `slice-folder-name-drift`.
- **Evidence**: `tools/pulse_worktree_resolver.py:77-86` `_UNKNOWN_REASONS` tuple (the canonical 8); slice-077 design.md:183-190 Drift & flags table column matches; cross-check `grep -rnE "milestone-malformed-yaml-frontmatter|worktree-not-registered" tools/ skills/ tests/` → only `branch_workflow_audit.py` references (unrelated tool); zero hits in `pulse_worktree_resolver.py`.
- **Proposed fix**: Replace Fix K's 8 reason-keys with the canonical 8 from `_UNKNOWN_REASONS`. Update Fix K paragraph + test plan row K.
- **Builder draft**: **ACCEPTED-FIXED** — design.md Fix K paragraph replaced with canonical 8 keys cited byte-equal from `tools/pulse_worktree_resolver.py:77-86 _UNKNOWN_REASONS`. Test plan row K reframed to parameterize over the canonical tuple + add `test_constant_keys_are_byte_equal_to_unknown_reasons_tuple` byte-equal invariant. Empirical APED-1 grep at /critique time (the Critic's own clause-5 self-execution) was the catch surface — clause-5 effective on its first governed slice.

#### B2: Fix S's premise that `tools/slice_queue_writer.py` calls lack `encoding="utf-8"` is empirically false — the helper is already UTF-8 explicit at all 9 sites

- **Claim under review**: design.md (pre-fix) Fix S: "audit every `Path.write_text(...)`, `Path.read_text(...)`, `open(...)` call in the helper and force explicit `encoding='utf-8'`"; mission-brief Must-not-defer (pre-fix): "explicit `encoding='utf-8'` on every `Path.write_text` / `open()` call in the helper"; design.md test plan row S: "pre-fix: file contains `Â§` / `â€"` / `Ã©` mojibake. post-fix: contains `§` / `—` / `é` directly."
- **Issue**: APED-1 self-application clause-5 execution at /critique time grep'd `tools/slice_queue_writer.py` — all 9 encoded-I/O sites (L134, 183, 214, 266, 351, 450, 703, 790, 847) ALREADY use `encoding="utf-8"` explicitly. The proposed regression test (write `§` then re-read; assert literal `§` round-trips) will PASS pre-fix AND post-fix → NO FAIL→PASS contrast → AC#5 obligation cannot be honestly met. The mojibake observed at slice-074 Step 6.5 was real but the root cause is NOT here — likely upstream (`tools/slice_pick.py` subprocess invocations / `PYTHONIOENCODING` env defaults / `/slice` skill's own subprocess invocation).
- **Evidence**: `tools/slice_queue_writer.py:134, 183, 214, 266, 351, 450, 703, 790, 847` all 9 already explicit. `wc -l` 889 lines; `grep -c encoding` 9 matches. APED-1 grep at /critique time empirically demonstrated.
- **Proposed fix**: Either (a) ESCALATE — locate the real mojibake source before Fix S lands; OR (b) REFRAME — promote Fix S to a regression PIN ONLY (pin existing `encoding="utf-8"` via structural-pin) and demote root-cause investigation to source-pending as P3.10' for a future slice.
- **Builder draft**: **ACCEPTED-FIXED** — option (b) per Critic's proposed fix: design.md Fix S reframed to structural-pin AST-walker test (asserts no encoded-I/O site lacks `encoding=` kwarg; FAIL→PASS contrast via fixture-mutation rather than codebase mutation since codebase is already correct). Mission-brief AC#5 + verification-plan #5 + Must-not-defer L34 all rewritten to match. P3.10's root-cause investigation routed to source-pending as new P3.10' `find-real-mojibake-source` candidate. The structural-pin honors AC#5's "regression tests pin both" obligation honestly (P3.10 is now a regression-guard not a fix; encoding=utf-8 pattern is structurally enforced going forward).

### Majors (address this slice)

#### M1: Fix K's `format_unknown_warn` signature + `_run_classify` invocation invent a new contract (the WARN-text strings + `augment_pulse_state_dict["unknown_warn"]` key) that goes beyond "conformance to existing slice-077 contract"

- **Claim under review**: design.md (pre-fix) L11 "Two NEW production-surface contract additions inside existing modules: `tools/pulse_worktree_resolver._UNKNOWN_REASON_WARN_TEMPLATES` mapping + `format_unknown_warn()` helper"; mission-brief Must-not-defer: "no new RULE-IDs minted; no new methodology-changelog entries; this is a no-VERSION-bump conformance / cleanup-discharge class per MEPD-1(b)".
- **Issue**: Slice-077 m5 explicitly enumerated two options: (a) Haiku-side prose interpretation via SKILL.md mapping table; OR (b) code-side helper `format_unknown_warn` + `_UNKNOWN_REASON_WARN_TEMPLATES`. Fix K (pre-fix) silently picked option (b) WITHOUT ADR'ing the choice. Adding a new public helper + new JSON state-dict field `"unknown_warn"` is a contract surface widening — the MEPD-1(b) EXCLUDE posture asserts "no new methodology axis" but does not argue.
- **Evidence**: slice-077 code-review m5 L85 enumerates options; ADR-070 (slice-077) JSON-output contract `{state, reason}`; adding `"unknown_warn"` widens it.
- **Proposed fix**: Either (a) mint ADR-072 naming the option-(a) vs option-(b) choice + reversibility argument (~40-line ADR); OR (b) demote Fix K to MAP-ONLY (only `_UNKNOWN_REASON_WARN_TEMPLATES` constant; no public helper; no state-dict field; SKILL.md consumes via Read+lookup).
- **Builder draft**: **ACCEPTED-FIXED** — option (b) demote Fix K to MAP-ONLY. Preserves JSON state-dict shape + CLI text-mode shape (no widening). The constant is exposed at module scope; `skills/pulse/SKILL.md` Drift & flags prose consumer reads `tools/pulse_worktree_resolver.py` + performs `_UNKNOWN_REASON_WARN_TEMPLATES.get(reason, fallback)` lookup at Haiku-side prose-interpretation time (slice-077 m5 option (a) canonical consumer). MEPD-1 EXCLUDE preserved; no ADR needed; contract-narrowing rationale documented at design.md § Contracts. Closer to "conformance to existing slice-077 contract" than the helper-dispatch path was.

#### M2: Fix O's signature extension leaves the `(unavailable)` defensive-fallback choice ambiguous ("deleted or kept with `# pragma: no cover`")

- **Claim under review**: design.md (pre-fix): "The `(unavailable)` defensive fallback becomes truly dead and is removed (or kept with a `# pragma: no cover` marker + a docstring line naming the rationale)."
- **Issue**: The "(or)" leaves Builder choice unspecified. Deletion is permanent contract narrowing; `pragma: no cover` preserves defensive shape. Per slice-079 calibration-log lesson "design→code translation gap N=15 cumulative": ambiguous Builder choice in design.md is the canonical entry point for translation-gap drift.
- **Evidence**: design.md L87 + L106-111 (also ambiguous).
- **Proposed fix**: Pick `# pragma: no cover` + docstring rationale (preserves defensive branch; ~3 lines; documents helper IS robust to None inputs).
- **Builder draft**: **ACCEPTED-FIXED** — design.md Fix O updated to unambiguously specify "kept with `# pragma: no cover` marker + docstring rationale" + test plan row O extended with `::test_unavailable_branch_rendered_when_winner_loser_none` (exercises pragma:no-cover branch when both args are None). Both branches exercised; defensive shape documented.

#### M3: Fix S's regression test design unconstructable as written (FAIL→PASS contrast cannot be demonstrated because the helper is already correct)

- **Claim under review**: AC#5 (pre-fix) + design.md test plan row S (pre-fix): "pre-fix: file contains `Â§` / `â€"` / `Ã©` mojibake. post-fix: contains `§` / `—` / `é` directly."
- **Issue**: Same root cause as B2 — helper already correct; roundtrip test PASSES on unmodified codebase → no FAIL→PASS contrast → AC#5 obligation structurally unmet. Bundled-cleanup discipline "FAIL→PASS contrast catalogued in `architecture/shippability.md`" would be silently violated.
- **Evidence**: B2 evidence; AC#5 obligation at mission-brief L20.
- **Proposed fix**: Couple with B2 fix.
- **Builder draft**: **ACCEPTED-FIXED** — covered by B2 reframe. Design.md test plan row S now uses fixture-mutation pattern for FAIL→PASS contrast (test stashes module, deletes `encoding="utf-8"` from one site via test fixture, re-imports → assertion fails; restore → passes). Empirical contrast preserved without requiring codebase mutation.

### Minors (log; address if cheap)

#### m1: WIRE-1 row for `tests/methodology/_skill_parse_helpers.py` not modeling the corpus-grep test

- **Claim under review**: design.md (pre-fix) WIRE-1 matrix; test plan row E `test_helper_defined_only_once_in_test_corpus` (corpus-grep test).
- **Issue**: Corpus-grep test is a global structural invariant on the test corpus, not a consumer-test of `_skill_parse_helpers.py`. WIRE-1 audit may flag as un-wired.
- **Proposed fix**: Either (a) note in WIRE-1 Exemption column; OR (b) add second WIRE-1 row pointing at test corpus.
- **Builder draft**: **ACCEPTED-FIXED** — option (a) per Critic's recommendation. WIRE-1 Exemption column now carries a rationale-prefixed note distinguishing the corpus-grep test as a global structural invariant exempt from per-module-consumer modeling.

#### m2: Fix L's OR-vs-AND logic for bare-repo detection

- **Claim under review**: design.md (pre-fix) Fix L: "(no `worktree <path>` key OR `"bare"` field present)".
- **Issue**: OR widens trigger to an impossible-state branch; slice-077 m6 original prescription was just `"bare" in block[0]` (AND check).
- **Proposed fix**: Tighten to AND.
- **Builder draft**: **ACCEPTED-FIXED** — design.md Fix L tightened to AND-only (`"bare"` field present in first-block) per slice-077 m6 original prescription. Removed the impossible-state OR branch.

#### m3: precedent-class count parenthetical "(cumulative N=6)" stale by 1 vs in-line text "N=7"

- **Claim under review**: design.md (pre-fix) §Decisions made (ADRs) MEPD-1(b) discharge text.
- **Issue**: Cosmetic; FBCD-1 sub-mode (a) cross-file-claim consistency.
- **Proposed fix**: Update parenthetical to "(cumulative N=7 including slice-079)".
- **Builder draft**: **ACCEPTED-FIXED** — design.md updated to "Precedent class (cumulative N=7 including slice-079): ... = N=6 prior + slice-079 = N=7". Internal consistency restored.

#### m4: AC#3 says "13 findings" but only 12 are actionable (m11 is positive observation per slice-077 code-review L117)

- **Claim under review**: mission-brief (pre-fix) AC#3 "Slice-077 13 code-Critic findings"; design.md AC mapping table.
- **Issue**: m11 is explicitly a positive observation, not a finding. AC#3 prose is technically false.
- **Proposed fix**: Reword to "12 actionable findings (m11 is positive observation)".
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief AC#3 reworded to "Slice-077 12 actionable code-Critic findings (m11 is positive observation per slice-077 code-review.md L117, NOT counted; per /critique m4 ACCEPTED-FIXED)". Design.md AC mapping table updated to match.

#### m5: Effort estimate "1 day" feels light for 19 fixes + 16 new tests + OSDG-1 lock-step + UTF8-STDOUT-1 + parameterized 8-reason tests + synthetic git fixtures

- **Claim under review**: mission-brief (pre-fix) "Estimated work: 1 day"; design.md test plan ~16 new/extended tests.
- **Issue**: Realistic effort ~8-12 hours; closer to MEDIUM-LARGE than MEDIUM. Slice-071's 31-finding precedent says 19 fixes is mid-range viable but only with realistic estimate.
- **Proposed fix**: Bump to "1.5 days" or "MEDIUM-LARGE".
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief frontmatter updated to "Estimated work: 1.5 days (MEDIUM-LARGE; bumped from '1 day' per /critique m5 ACCEPTED-FIXED — ...)". Slice scope unchanged; effort framing honest.

#### m6: Shippability catalog row enumeration deferred to /build-slice Phase A — design.md describes cluster shapes but doesn't enumerate concrete row text

- **Claim under review**: design.md §Shippability catalog impact (pre-fix) "Exact row count + Machine-cmd content locked at /build-slice Phase A".
- **Issue**: Deferral creates SCPD-1 propagation hazard at /build-slice Phase 4/5 Edit time.
- **Proposed fix**: Enumerate 6-8 rows in design.md with concrete Row title + Machine-cmd + Verifies cells before /build-slice (~30 min design work).
- **Builder draft**: **ACCEPTED-PENDING** — concrete row text enumeration deferred to /build-slice Phase A as currently scoped at design.md L231; the catalog grammar is structurally enforced by SCMD-1 + SRSC-1, so Phase A is the canonical authoring time. Phase A will enumerate concrete row text + verify SCPD-1 propagation (consumer-reference propagation into shippability catalog) in the SAME Phase block — per slice-079's own discipline of paired in-fix-block verification. Critic concern noted; Phase A explicitly handles the propagation surface.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (Fix K reason-keys do NOT exist in cited contract source; APED-1 self-application clause-5 grep executed); B2 (Fix S premise empirically false; APED-1 grep executed).
- [x] **Missing edge cases** — none additional. Slice does not introduce new edge case surfaces; defense-by-conformance pattern.
- [x] **Over-engineering** — none material after M1 ACCEPTED-FIXED (option-b MAP-ONLY narrows the contract surface back to slice-077 contract conformance).
- [x] **Under-engineering** — m4 (AC#3 count off-by-one — ACCEPTED-FIXED); m6 (shippability row enumeration — ACCEPTED-PENDING with Phase A handoff); B2/M3 (Fix S structurally unmet without reframe — ACCEPTED-FIXED).
- [x] **Contract gaps** — M1 (Fix K new public surface — ACCEPTED-FIXED via demote to MAP-ONLY); M2 (Fix O ambiguity — ACCEPTED-FIXED via pragma:no-cover pick).
- [x] **Security** — none. All edits are pure refactors / prose tightenings / contract conformance. No new auth/authz/credential surfaces.
- [x] **Drift from vault** — none structural. MEPD-1(b) discharge verified empirically; precedent class N=7 (m3 ACCEPTED-FIXED).
- [x] **Web-known issues** — Skipped (stdlib + in-house only).
- [x] **Cross-cutting conformance** —
  - **Tooling-doc-vs-implementation parity**: B1 is the canonical instance (Fix K cited contract source != actual). APED-1 self-application clause-5 executed at /critique time per the just-applied clause.
  - **Recursive self-application discipline**: **slice-079 IS the N+1 first-governed-slice of APED-1 clause-5** (per calibration-log 2026-05-29). The Critic executed APED-1 grep at /critique time for Fix K (B1) AND Fix S (B2) — both empirical demonstrations that clause-5 closes the discipline-on-itself loop at first-Critic time. **APED-1 clause-5 effective on its very first governed slice (N=1 catch, not miss).**
  - **Fix-block-completeness discipline (FBCD-1 sub-mode a)**: m3 (precedent-count parenthetical — ACCEPTED-FIXED); m4 (AC#3 vs mapping table count — ACCEPTED-FIXED).
  - **Phantom test-file/function citation discipline (PTFCD-1 / PTFFD-1)**: NEW test files cited are slice-created → not phantoms.
  - **Audit-parse-rule empirical-execution discipline (APED-1)**: original-scope not engaged; clause-5 self-application scope engaged on B1 + B2.

## Triage

**Triaged by**: user
**Date**: 2026-05-29
**Final verdict**: NEEDS-FIXES

Per /critique Step 4.5 TRI-1 (PCA-1 HALT gate) — user ratified all 12 Builder draft dispositions via "Accept all" 2026-05-29 after reviewing the reconciled findings from first Critic + meta-Critic. 11 ACCEPTED-FIXED + 1 ACCEPTED-PENDING → mechanically computes to NEEDS-FIXES.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md Fix K reason-keys + test plan row K corrected to canonical `_UNKNOWN_REASONS` (`fresh-worktree-no-milestone` / `milestone-missing-in-active-and-archive` / `milestone-frontmatter-malformed` / `detached-head` / `dirty-worktree` / `merge-base-error` / `head-unresolvable` / `slice-folder-name-drift`); APED-1 clause-5 grep at /critique time was empirical catch |
| B2 | Blocker | ACCEPTED-FIXED | design.md Fix S reframed to structural-pin AST-walker; mission-brief AC#5 + verification-plan #5 + Must-not-defer rewritten; P3.10 root-cause investigation routed to new P3.10' source-pending entry |
| M1 | Major | ACCEPTED-FIXED | Fix K demoted to MAP-ONLY (constant only; no helper; no state-dict field); MEPD-1 EXCLUDE preserved; slice-077 m5 option (a) Haiku-side prose-interpretation consumer canonical |
| M2 | Major | ACCEPTED-FIXED | Fix O pragma:no-cover pick + docstring rationale + paired test for None-branch |
| M3 | Major | ACCEPTED-FIXED | covered by B2 reframe (fixture-mutation FAIL→PASS contrast) |
| m1 | Minor | ACCEPTED-FIXED | WIRE-1 Exemption note distinguishing corpus-grep test as global structural invariant |
| m2 | Minor | ACCEPTED-FIXED | Fix L tightened to AND-only per slice-077 m6 original prescription |
| m3 | Minor | ACCEPTED-FIXED | precedent-class parenthetical updated to (cumulative N=7 including slice-079) |
| m4 | Minor | ACCEPTED-FIXED | AC#3 reworded to "12 actionable findings (m11 is positive observation)"; design.md mapping table matches |
| m5 | Minor | ACCEPTED-FIXED | effort estimate bumped to "1.5 days (MEDIUM-LARGE)" |
| m6 | Minor | ACCEPTED-PENDING | concrete shippability row enumeration deferred to /build-slice Phase A; SCPD-1 propagation verified in same Phase block per slice's own paired-verification discipline |
| M-add-1 | Minor | ACCEPTED-FIXED | meta-Critic-surfaced finding (per critique-review.md): design.md §Contracts mis-cited `_format_vault_claim_audit_entry` pre-fix signature as 2-arg; corrected to actual 4-arg `(diag, result, timestamp, head_sha)` post-fix 6-arg `(..., winner, loser)`; `_append_audit_log` public surface UNCHANGED — computation lives in existing scope at L1270-1277 before dispatch at L1277 |
