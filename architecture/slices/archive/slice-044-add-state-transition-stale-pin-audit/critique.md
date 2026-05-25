# Critique: Slice 044 add-state-transition-stale-pin-audit

**Critic reviewed**: mission-brief.md, design.md, ADR-047
**Date**: 2026-05-18
**Result**: BLOCKED (pre-triage Critic verdict; Builder drafts all ACCEPTED-FIXED — final verdict set at TRI-1)

## Summary

Intent is sound (R-10 class is real, recurring, Critic-unreachable). But Sub-form A's detection mechanism as originally specified did not match the actual prose-pin corpus: it would (B1) false-positive on deliberately-absent `not in` pins, (B2) under-detect the dominant function-local + sliced-segment binding shape, and (B3) mis-extract implicitly-concatenated multi-line literals. Sub-form B's merge-base/changed-file semantics were unspecified at the only invocation point (M1). All three Blockers + three Majors were empirically reproduced against the real codebase by the Critic and **independently re-verified by the Builder** (grep confirmed 2 live `not in` pins + 38 function-local/sliced-segment occurrences across 8 files). The design + ADR-047 + mission-brief have been revised in this round.

## Findings

### Blockers (must address before /build-slice)

#### B1: Sub-form A false-positives on `not in` negative prose-pins — violates must-not-defer #3
- **Claim under review**: design.md Sub-form A: "asserting a constant string literal via `in` membership … An absent literal ⇒ violation".
- **Issue**: `test_commit_slice_skill_merge_flag.py:38` (`"--do-commit" not in content`) and `:57` (`"git branch -D" not in content or "NEVER" in content`) assert literals *correctly absent by design*. A naive absent-literal scan fires on every `not in` pin on the clean tree — reintroducing the false-PCA-1-HALT class the slice exists to remove; would FAIL the slice's own mid-slice smoke / Step 6.
- **Evidence**: Builder re-verified — `grep 'not in '` over `tests/methodology/test_*skill*.py` → exactly those 2 live pins; both literals absent from `skills/commit-slice/SKILL.md` by design.
- **Proposed fix**: AST detector restricted to `ast.Compare` with single `ast.In` op; `ast.NotIn` + any `BoolOp`-nested membership excluded; explicit negative verification + mid-slice-smoke fixture.
- **Builder draft**: **ACCEPTED-FIXED** — design.md What's new Sub-form A "Positive-membership only" clause + Non-false-positive guarantee bullet 1 + ADR-047 residual #1 + mission-brief verification rows 2 & mid-slice-smoke `not in` fixture (→ exit 0).

#### B2: `read_file(...)`-bound-name recognition misses the dominant function-local + sliced-segment shape
- **Claim under review**: design.md What's reused: "recognises `read_file("skills/<x>/SKILL.md")` / `conftest.read_file(...)` bindings"; What's new: "every `tests/**/test_*skill*.py` prose-pin".
- **Issue**: Corpus is dominated by function-local `content = read_file(...)` then assertions against a *sliced sub-segment* (`prereq_block = content.split("## …")[1]…`). Module-level-only recognition scans a small minority; AC2's "R-10's exact class" coverage claim is materially false for the general mechanism (R-10's own pin is module-level, so AC4 could pass while the mechanism misses the majority).
- **Evidence**: Builder re-verified — 38 `content = read_file`/`prereq_block`/`scoped` occurrences across 8 files; `test_build_slice_skill_branch_create.py:21-31` is the canonical counter-example.
- **Proposed fix**: binding-tracer resolving local + module-level names transitively through `str.split(...)[i]`/slice chains; **presence checked against the full SKILL.md, not the sub-segment** (slicing narrows location, not presence).
- **Builder draft**: **ACCEPTED-FIXED** (option (a), full fix) — design.md Sub-form A "Binding tracer" + "Presence check is against the FULL SKILL.md" clauses; Non-false-positive guarantee bullet 4; mission-brief verification row 2 exercises both module-level + function-local sliced-segment.

#### B3: Implicitly-concatenated multi-line literal pins mis-extracted
- **Claim under review**: design.md non-false-positive guarantee "ignores non-constant … operands"; error model "missing literal (≤80 chars)".
- **Issue**: `test_build_slice_skill.py:162-166` asserts a 3-line implicitly-concatenated literal. CPython folds it to one `ast.Constant`, so it is NOT skipped by the "non-constant" guarantee — but a regex/first-token extractor would search for a non-existent prefix and false-positive / mis-report.
- **Evidence**: Critic-cited `test_build_slice_skill.py:161-166` (CRP-1 verbatim STOP routing message pin); CPython adjacent-literal fold is standard parser behavior.
- **Proposed fix**: extract `ast.Constant.value` (post-fold) / `ast.literal_eval`, never source-text scraping; verification case for present + absent folded value.
- **Builder draft**: **ACCEPTED-FIXED** — design.md Sub-form A "Folded-constant literal extraction" clause + Non-false-positive guarantee bullet 3 + mission-brief verification row 2b.

### Majors (address this slice)

#### M1: Sub-form B merge-base/changed-file semantics unspecified at the Step-6-on-slice-branch invocation point
- **Claim under review**: design.md Sub-form B "differs between the git merge-base baseline and the working tree … NOT in the slice's git changed-file set"; CLI "base = `git merge-base HEAD <default>`".
- **Issue**: Audit wired ONLY at Step 6 (runs on `slice/044` per BRANCH-1). The `git diff --name-only <base>` invocation + committed-vs-uncommitted semantics were unstated — the only behavior that makes Sub-form B sound; AC1 fixture ("test file unchanged") never exercised the real slice-branch path.
- **Evidence**: `git merge-base HEAD master` → master tip; `git diff --name-only master` empty on master (fixture would pass while real path untested).
- **Proposed fix**: specify `git diff --name-only <merge-base>` (working tree, committed+uncommitted, vs base) + a slice-044-own-Step-6 dogfood (exit 0; slice flips no risk status).
- **Builder draft**: **ACCEPTED-FIXED** — design.md Sub-form B parenthetical (exact invocation + semantics) + Non-false-positive guarantee bullets 5–6 + mission-brief verification row 3c (RSAD-1 self-dogfood) + mid-slice-smoke live-tree exit-0 case.

#### M2: Default-branch resolution fragile here; reuse by object identity + document the universal-HALT residual
- **Claim under review**: design.md What's reused "`_resolve_default_branch` pattern"; must-not-defer "git-base resolution failure must HALT".
- **Issue**: On this repo `git symbolic-ref refs/remotes/origin/HEAD` already `fatal`s; resolution survives only via `init.defaultBranch`. A misconfigured clone → fail-closed HALT of *every* Step 6 on a clean repo — a new false-HALT class under-acknowledged in ADR-047.
- **Evidence**: Empirical: primary leg `fatal` on this repo; `git config init.defaultBranch` → `master`.
- **Proposed fix**: reuse `_resolve_default_branch` by object-identity import (assert `is`, per the slice-038 CSP-1 lesson the design already applies to `_parse_risks`); document the residual + actionable message in ADR-047; both-legs-fail verification case.
- **Builder draft**: **ACCEPTED-FIXED** — design.md What's reused (object-identity `_run_git` + `_resolve_default_branch`, assert `is`) + ADR-047 residual #2 + mission-brief verification row 3b.

#### M3: `conftest.read_file(...)` qualified-call shape has zero corpus instances (YAGNI); `assert_md_forward_synced` boundary unstated
- **Claim under review**: design.md What's reused "recognises … `conftest.read_file(...)` bindings".
- **Issue**: Every corpus file uses bare imported `read_file`; the qualified shape is speculative generality and implies untested coverage. The `assert_md_forward_synced(Path,…)` forward-sync drift family (the other mini-CAD surface) is silently omitted rather than named out-of-scope.
- **Evidence**: `grep conftest … read_file` → only import lines, zero qualified calls; `tests/skill_drift_equality.py:49`.
- **Proposed fix**: drop the qualified shape (YAGNI); explicitly name the `assert_md_forward_synced` family out-of-scope (guarded by EOL-DRIFT-1, not Sub-form A).
- **Builder draft**: **ACCEPTED-FIXED** — design.md What's reused (bare-`read_file`-only, qualified shape unsupported) + new "Out-of-scope coverage boundaries (critique M3)" section + ADR-047 already records the ADR-supersession deferral.

### Minors (log; address if cheap)

#### m1: AC4 shippability row 6-column schema + SCMD-1/PTFFD-1/slice-037-ordering unstated
- **Issue**: `shippability.md` is the 6-column schema; PTFFD-1 function-verifies the `::`-selector; slice-037 says sequence the new audit's own row LAST. design.md did not state these → risk of a self-application FAIL at this slice's own Step 6.
- **Evidence**: `shippability.md:7` schema; `shippability_path_audit.py` reads `cells[5]`; slice-037 aggregated lesson.
- **Proposed fix**: state the 6-column + backtick-`Machine-cmd` (SCMD-1) + final PTFFD-1-clean selector + row-added-LAST discipline.
- **Builder draft**: **ACCEPTED-FIXED** — design.md "AC4 shippability catalog row (critique m1)" section + mission-brief verification row 4.

#### m2: ADR-047 Consequences omit the new false-HALT residuals introduced by B1/M2
- **Issue**: ADR records the closed class + deferred sub-form but not the two new failure surfaces the gate creates (NotIn false-positive; misconfigured-clone HALT).
- **Evidence**: ADR-047 Consequences; B1 + M2.
- **Proposed fix**: append both residuals + mitigations to ADR-047 Consequences.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-047 "Introduced residuals (critique m2)" sub-section appended (pre-triage, pre-commit; sanctioned by /critique Step 4 ACCEPTED-FIXED "edit design.md / ADR before triage").

### Targeted re-critique — Round 2 (Sub-form B git-independence deviation)

After TRI-1 CLEAN, /build-slice plan-mode discovered Sub-form B's git-merge-base mechanism was inapplicable (`architecture/` gitignored). User approved "deviate now + targeted re-critique" (build-log.md 2026-05-18 00:02). A scoped Critic pass on the revised git-independent Sub-form B returned **BLOCKED**; all 6 findings empirically re-verified by the Builder and ACCEPTED-FIXED in the same round. IDs continue the round-1 sequence (audit-parseable; all before `## Triage`).

#### B4: Sub-form B `tests/**/*.py` scan hits the permanent intentional `tests/methodology/fixtures/syntax_error.py` → live-repo exit 2, not 0 (self-application false-HALT; RSAD-1 / must-not-defer #3)
- **Issue**: design's "AST SyntaxError on a scanned file ⇒ exit 2 fail-closed" → STP-1 exits 2 on the live repo (one unparseable file: the deliberate mock-budget fixture) → slice-044's own mid-slice-smoke + Step-6 self-application cannot pass; the exact false-PCA-1-HALT class STP-1 exists to remove, reproduced in STP-1.
- **Evidence**: Builder re-verified — `ast.parse` sweep over `tests/**/*.py` → exactly `tests/methodology/fixtures/syntax_error.py` raises `SyntaxError`.
- **Builder draft**: **ACCEPTED-FIXED** — design.md Sub-form B + What's-reused + Error-model + Non-FP guarantee + ADR-047 Decision/Deviation + mission-brief AC1/row 1c/must-not-defer: per-scanned-file `SyntaxError` ⇒ skip-with-visible-note, NO violation, NOT exit 2; exit-2 reserved for hard-input failure (register/dir/repo-root).

#### B5: exit-2-on-SyntaxError contradicted the ADR-037/PTFFD-1 skip-with-note discipline of the precedent design.md cites as reused (`shippability_path_audit.py`)
- **Issue**: design.md "What's reused" claimed the `shippability_path_audit.py`/`_pyfn` AST-scan technique but inverted its single load-bearing parse-failure decision (skip-with-note → exit-2-HALT) — an unfounded "follows precedent X" the precedent's source refutes; also a vault-drift vs the accepted repo-wide ADR-037 adjudication of this exact question.
- **Evidence**: `shippability_path_audit.py` skip-notes + ADR-037 M2 "a false-FAIL on a parse failure would halt the pipeline gate, the strictly worse audit failure mode".
- **Builder draft**: **ACCEPTED-FIXED** — STP-1 (both sub-forms) now explicitly inherits the ADR-037/PTFFD-1 skip-with-note discipline; design.md "What's reused" + ADR-047 state the alignment explicitly (no contradiction/supersession of ADR-037). Resolves jointly with B4.

#### M4: unanchored `re.search` let an embedded `r` false-bind a risk-number (`test_addr_5_is_open`, `test_parser_4_is_retired`) — status-validity guard not sufficient
- **Issue**: latent false-positive footgun: a future innocuous `def test_addr_5_is_open()` would bind `R-5`/`open`, and since live `R-5`=`retired` STP-1 would false-fire `stale-risk-status-pin` and HALT an innocent slice (must-not-defer #3).
- **Evidence**: Builder re-verified — `re.search(OLD, "test_addr_5_is_open")` → `('5','is','open')`; `("test_parser_4_is_retired")` → `('4','is','retired')`; anchored form → `None` for both.
- **Builder draft**: **ACCEPTED-FIXED** — regex `(?:^|_)`-anchored on the `r`-token (design.md L14 / ADR-047 / mission-brief AC1 + verification row 1b adversarial cases).

#### M5: greedy `(\w+)` status group suppressed suffixed real stale pins (`test_r_4_stays_mitigating_until_done`) → false-negative (AC1 under-delivery)
- **Issue**: a realistic suffixed pin genuinely claiming `R-4`=mitigating bound group3=`mitigating_until_done` → not a valid status → suppressed → STP-1 misses a real stale pin (inverse of the gate's purpose).
- **Evidence**: Builder re-verified — old form suppresses `test_r_4_stays_mitigating_until_spike_done`; explicit-alternation form → `(4,stays,mitigating)` (caught).
- **Builder draft**: **ACCEPTED-FIXED** — status is an explicit `(open|mitigating|retired|accepted)(?:_|$)` alternation (no validity-guard reliance); verification row 1b suffixed-name case.

#### m3: ADR-047 Reversibility (L64) carried a stale "git merge-base register diff" reference describing the CURRENT design
- **Builder draft**: **ACCEPTED-FIXED** — ADR-047 Reversibility → "(AST literal/binding scan, live-register parse via the reused `_parse_risks`)".

#### m4: design.md "Data model deltas" still said "pure read-only function over **git state** + …"
- **Builder draft**: **ACCEPTED-FIXED** — design.md → "over the test/skill/register file corpus (no git state — git-independent post-deviation)".

**DR-1 Round-2 meta-review** (critique-review.md ROUND 2) → **EXTEND**: 6/6 Round-2 findings VALID at correct severity, no relocation, regex character-identical across all 3 sites. One missed finding **m-add-R2-1** (Minor): m3 fixed ADR-047 L64 but the same stale "git-diff-dependent" phrase survived at ADR-047 **L27 (the Chosen option)** — the load-bearing rationale a reader hits before the Decision/Deviation that correct it (FBCD-1 deviation-consistency: m3's fix was incomplete). Disposition **ACCEPTED-FIXED** — ADR-047 L27 struck-through + cross-referenced to the Deviation sub-section (mirrors L35 self-annotation); no executable impact. Added as a triage row below.

## Dimensions checked
- [x] Unfounded assumptions — B2, M3 (recognition assumption vs real corpus; verified by grep)
- [x] Missing edge cases — B1 (`not in`), B3 (concatenated literal), M1 (slice-branch merge-base degeneracy)
- [x] Over-engineering — M3 (qualified-call resolver, no corpus instance); two-sub-form scoping otherwise appropriately YAGNI
- [x] Under-engineering — B1, B2 (ACs without a delivering design element — now fixed)
- [x] Contract gaps — M1 (`git diff` invocation/semantics), m1 (shippability 6-col/Machine-cmd)
- [x] Security — none (read-only local audit; fixed-argv `subprocess`, no `shell=True`; no auth/network/secrets)
- [x] Drift from vault — none (ADR-047 supersedes nothing; STP-1 NON-`-D` `vN.N` consistent with the audit-gate naming-class; cited reuse targets all exist and were read)
- [x] Web-known issues — n/a (pure-stdlib in-house audit; no external platform surface)
- [x] Cross-cutting conformance — RSAD-1 (self-application: slice-044's own Step 6 must exit 0 — addressed via the M1 dogfood case), APED-1 (Critic empirically executed corpus survey; Builder independently re-verified B1/B2), PTFCD-1/PTFFD-1 (m1 — AC4 `::`-selector must be extant; row LAST per slice-037), MEPD-1 (STP-1 minted, 4-part PMI-1 bump + entry-pin in AC5; Builder must recompute the why-none against the actual `test_methodology_changelog.py` assertion, not precedent)

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

Reconciles all passes: first Critic + DR-1 critique-review.md EXTEND + the **Round-2 targeted re-critique** of the Sub-form B git-independence deviation (B4/B5/M4/M5/m3/m4). DR-1 missed findings B-add-1 / M-add-1 / m-add and the Round-2 findings added as rows. Round-1 M1/M2 were rendered moot/dissolved by the deviation (annotated below) — their ACCEPTED-FIXED disposition stands as "addressed via the deviation that removed the git mechanism entirely." All dispositions ACCEPTED-FIXED → mechanical verdict CLEAN (zero ACCEPTED-PENDING, zero ESCALATED).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md§Sub-form-A positive-membership clause; not-in/BoolOp-mixed excluded; mission-brief verif row 2 |
| B2 | Blocker | ACCEPTED-FIXED | design.md§Sub-form-A binding-tracer + presence-vs-full-SKILL.md; What's-reused; verif row 2 |
| B3 | Blocker | ACCEPTED-FIXED | design.md§Sub-form-A folded-`ast.Constant.value` extraction; verif row 2b |
| M1 | Major | ACCEPTED-FIXED | MOOTED by the 2026-05-18 deviation — Sub-form B no longer uses git-diff at all (standing invariant); no git-diff semantics remain to be wrong |
| M2 | Major | ACCEPTED-FIXED | DISSOLVED by the deviation — no git ⇒ no default-branch resolution ⇒ no misconfigured-clone HALT; CSP-1 object-identity reuse preserved on `_parse_risks` |
| M3 | Major | ACCEPTED-FIXED | design.md drop qualified `conftest.read_file`; "Out-of-scope coverage boundaries" section |
| m1 | Minor | ACCEPTED-FIXED | design.md "AC4 shippability catalog row" section (6-col/SCMD-1/PTFFD-1/row-LAST) |
| m2 | Minor | ACCEPTED-FIXED | ADR-047 "Introduced residuals (critique m2)" sub-section |
| B-add-1 | Blocker | ACCEPTED-FIXED | DR-1 missed; design.md§Sub-form-A per-operand BoolOp + build-time machine-classification; Non-FP guarantee bullet 1; ADR-047 residual #1; verif row 2c |
| M-add-1 | Major | ACCEPTED-FIXED | DR-1 missed; design.md line 14 `_`-delimited regex (empirically verified vs `test_r_4_stays_mitigating`); mission-brief verif row 1b |
| m-add | Minor | ACCEPTED-FIXED | DR-1 sev-add; mission-brief AC4 + verif row 4 assert exit-1 signature (kind + folded literal), not exit≠0 |
| B4 | Blocker | ACCEPTED-FIXED | Round-2; per-file SyntaxError ⇒ skip-with-note not exit-2 (ADR-037); design.md Error-model/Non-FP + ADR-047 + mission-brief AC1/row 1c/must-not-defer |
| B5 | Blocker | ACCEPTED-FIXED | Round-2; STP-1 explicitly inherits ADR-037/PTFFD-1 skip-with-note (no contradiction/supersession); design.md What's-reused + ADR-047 |
| M4 | Major | ACCEPTED-FIXED | Round-2; regex `(?:^|_)`-anchored r-token (no embedded-`r` false-bind); empirically verified; verif row 1b |
| M5 | Major | ACCEPTED-FIXED | Round-2; explicit status alternation `(open|mitigating|retired|accepted)(?:_|$)` (closes suffixed-name false-negative); verif row 1b |
| m3 | Minor | ACCEPTED-FIXED | Round-2; ADR-047 Reversibility L64 stale "git merge-base register diff" → live-register parse |
| m4 | Minor | ACCEPTED-FIXED | Round-2; design.md "Data model deltas" stale "git state" → "no git state" |
| m-add-R2-1 | Minor | ACCEPTED-FIXED | DR-1 Round-2 missed; ADR-047 L27 (Chosen option) stale "git-diff-dependent" struck + cross-ref'd to the Deviation sub-section (m3 fixed only L64); ADR-internal doc-consistency, no executable impact |
