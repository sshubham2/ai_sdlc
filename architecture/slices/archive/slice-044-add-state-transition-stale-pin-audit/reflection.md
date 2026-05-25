# Reflection: Slice 044 add-state-transition-stale-pin-audit

**Date**: 2026-05-18
**Shipped**: YES-WITH-DEFERRALS

## Validated
- STP-1 Sub-form A (SKILL.md-prose-repoint) + Sub-form B (risk-status-stale) both catch their target class — validated by 24 real fixture cases + the R-10 reconstruction + the real-repo self-application (exit 0) + SRSC-1 catalog 44/44.
- The git-diff-independent standing-invariant shape catches the slice-041 precedent (`test_r_4_stays_mitigating` vs live `R-4`=retired → exit 1) and correctly clears the slice-041-realigned name — validated by `test_subform_b_*` against real fixtures.
- ADR-037/PTFFD-1 skip-with-note for per-file `SyntaxError` is the correct discipline — validated: the live `tests/methodology/fixtures/syntax_error.py` is skip-noted, STP-1 exits 0 (would have self-HALTed under the pre-deviation exit-2 spec).
- Object-identity reuse of `risk_register_audit._parse_risks` (CSP-1) — validated by `test_object_identity_parse_risks_reuse` (`is` assertion) + clean parse of the live register.
- 4-part PMI-1 atomic bump + entry-pin + INST-1/PMI-1/META-1 — validated by the audits exit 0 + 4 version legs == 0.54.0 + 705-test suite.

## Corrected
- **design.md Sub-form B mechanism**: git-merge-base-baseline-diff → git-diff-independent standing invariant. Reality: `architecture/` is fully gitignored (`.gitignore:11`), so the merge-base mechanism could not self-apply. Corrected in [[design.md]] + [[ADR-047]] (Deviation section) + [[mission-brief.md]] AC1; build-log.md records the DEVIATION (2026-05-18 00:02).
- **design.md Sub-form A BoolOp handling**: "positive-only `BoolOp` per-operand" → "`And`-per-operand, `Or`-excluded". Reality: an `or`-disjunction (`assert "solo-dev" in c or "solo dev" in c`) legitimately has an absent alternative; per-operand flagging false-positived 8 live pins. Corrected in [[design.md]] (Positive-membership clause + Non-FP guarantee); build-log.md ERROR 2026-05-18 01:05.
- **changelog/entry-pin catalog index**: assumed #42 → actual #44 (recompute-don't-trust, slice-040 lesson). Corrected before the row was added.

## Discovered
- **The gitignored-vault blind spot**: an audit that reasons about `architecture/**` via git cannot self-apply in this repo (the entire vault is local-only). Any future vault-targeting tool must use live on-disk reads, not git. Impact: a general constraint for methodology-tooling slices — added as a lesson; not a risk-register entry (it's a now-known design constraint, not an open risk).
- **`Or`-disjunction is a distinct prose-pin class** from `not in` and mixed-`BoolOp` — the B1/B-add-1 findings did not enumerate it. Impact: codified in design.md; the detector now distinguishes `ast.And` (per-operand) from `ast.Or` (excluded).
- **Markdown-table pipe hazard**: embedding a regex with `|` alternation in a shippability *Critical path* prose cell silently shifts columns and breaks SCMD-1 segmentation. Impact: catalog-row authoring must be pipe-free or `\|`-escaped — strong build-checks promotion candidate.
- **cp1252 coverage-parity is a hard self-application gate**: a new `tools/*.py` with `main()` must be added to `test_utf8_stdout_regression.py`'s argv-classified list. Impact: known recurring obligation for every new audit tool (slice-022/035 class).

## Deferred
- **Sub-form B literal-detection leg** (a status string-literal co-located with a risk-id token) — reason: false-positive-prone (must AST-distinguish real asserts from docstring/f-string prose), no witnessed non-fn-name instance; the fn-name-token leg alone catches the slice-041 precedent. Lands in: backlog `/reflect` Discovered — add only if a non-fn-name risk-status pin is ever witnessed.
- **ADR `accepted`→`superseded` stale-pin sub-form** — reason: no canonical machine-readable test↔superseded-claim signal (ADR-047 Decision). Lands in: backlog — a future slice if a mechanizable signal emerges.
- **Plan-mode-stage STP-1 invocation** — reason: this slice wires Step-6 pre-finish only. Lands in: backlog — a separate decision (would catch stale pins earlier, before build).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (verdict CLEAN both rounds, all ACCEPTED-FIXED) + reality observed during build/validate:

**Round 1 — first Critic (BLOCKED → all ACCEPTED-FIXED):**
- B1 (`not in` false-positive): **VALIDATED** — real; build confirmed (and the `Or` extension of the same class surfaced — see Missed).
- B2 (function-local/sliced-segment binding): **VALIDATED** — the dominant corpus shape; the binding-tracer was required and works (38-occurrence reality matched).
- B3 (folded multi-line literal): **VALIDATED** — CPython `ast.Constant` fold confirmed empirically in build.
- M1 (merge-base semantics): **VALIDATED-then-MOOTED** — the concern was real, but the plan-mode gitignore discovery removed the entire git mechanism (resolved by re-architecture, not the original fix).
- M2 (default-branch object-identity reuse): **VALIDATED** — real; dissolved by the deviation (no git remains); CSP-1 reuse preserved on `_parse_risks`.
- M3 (`conftest.read_file` YAGNI + `assert_md_forward_synced` boundary): **VALIDATED** — zero qualified-call corpus instances confirmed.
- m1 (shippability 6-col/SCMD-1/PTFFD-1/row-LAST): **VALIDATED** — row #44 followed exactly this; the pipe-hazard sub-issue was NOT in the finding (see Missed).
- m2 (ADR-047 introduced residuals): **VALIDATED**.

**Round 1 — DR-1 meta-Critic (EXTEND):**
- B-add-1 (BoolOp over-exclusion blinding ~45/140 positive pins): **VALIDATED** — empirically real; the fix preserved positive-only `And` per-operand (and the `Or` refinement extended it).
- M-add-1 (dead `\b`-anchored regex vs snake_case): **VALIDATED** — empirically dead (`re.search` returned None on the precedent); the `_`-delimited form fixed it.
- m-add (AC4 signature-specificity): **VALIDATED** — the repro asserts kind+folded-literal, not exit≠0.

**Round 2 — targeted re-critique (deviation; BLOCKED → all ACCEPTED-FIXED) + DR-1 EXTEND:**
- B4/B5/M4/M5/m3/m4 + m-add-R2-1: **all VALIDATED** — each empirically reproduced against the real repo before fixing; B4 (syntax_error.py self-HALT) and M4 (embedded-`r` false-bind) and M5 (greedy-`\w+` false-negative) were exact, mechanically-confirmed.

**Missed by Critic** (the load-bearing calibration signal — the dual-Critic+DR-1 stack, BOTH rounds, BOTH layers, missed these; all caught only by build-time real-artifact execution):
1. **`architecture/` is gitignored** → Sub-form B's entire git-merge-base mechanism inapplicable. The meta-Critic even *observed* `git diff --name-only master` was empty and mis-attributed it to "on master, merge-base=HEAD" rather than the gitignore root cause. Caught at /build-slice plan-mode.
2. **`Or`-disjunction false-positive** (8 live pins). B1/B-add-1 enumerated `not in`/`NotIn`/mixed-`BoolOp` but not positive-only `or`. Caught at Task-1 self-verify on the live repo.
3. **Recursive double-count** (module-walk descending into functions). Caught at Task-2 test run.
4. **Markdown-table `|`-in-regex column shift** breaking SCMD-1. Caught at Task-7.
5. **cp1252 coverage-parity** (new tool absent from UTF8-STDOUT-1 list). Caught at SRSC-1 runner.

**Pattern**: across 2 rounds × 2 Critic layers, ~20 filed findings were ~100% VALIDATED with ~0 FALSE-ALARM — the stack is *precise on what it reviews*. But it structurally **cannot reach the audit-vs-real-artifact interaction** — the exact law STP-1 itself codifies — and that blind spot fired **N≥5 inside slice-044's own construction**. The load-bearing backstop is build-time real-artifact execution + plan-mode code-reality reads (slice-032/036/037 N+1…N+5). This is the strongest possible `/critic-calibrate` input: the slice that systematizes "the dual-Critic stack cannot reach audit-vs-artifact" had that exact blind spot fire five times on itself.

## Lessons for next slice
- **For any methodology-tooling slice that targets `architecture/**`: the vault is fully gitignored (`.gitignore:11`) — design for live on-disk reads, never git diff/show of vault paths. Verify self-application at plan-mode, not after building.** (Candidate Builder-plan-mode checklist item — the N≥1 gitignored-vault datapoint.)
- **A new `tools/*.py` audit with `main()` carries TWO non-negotiable self-application obligations beyond its own logic: (a) add it to `test_utf8_stdout_regression.py`'s argv-classified cp1252 list (`_ROOT_ONLY_TOOLS` vs `_POSITIONAL_SLICE_TOOLS` — verify the argv contract, slice-038), (b) its shippability row's prose must be pipe-free/`\|`-escaped (a `|` in any cell shifts the 6-col schema and breaks SCMD-1).** Sequence the cp1252-list edit + the row LAST, run SRSC-1, read its output (slice-037 / BC-PROJ).
- **`/critic-calibrate` watch-list (high priority)**: the dual-Critic+DR-1 stack is precise-but-structurally-blind to audit-vs-real-artifact interactions; N≥5 on slice-044 alone. Candidate Critic dimension: when the slice ships an *audit/tool that scans the repo*, explicitly task the Critic to "name the exact real-repo conditions (gitignore, permanent fixtures, snake_case conventions, markdown-table escaping) the tool will encounter on its own first run" — though the durable cure remains build-time execution, not a new Critic dimension (slice-037 law).
- **`Or` vs `And` prose-pin semantics**: a disjunction pins no operand individually; a conjunction pins each. Any future prose-pin-analysis tooling must distinguish them.

## Vault updates made (thin vault — small list)
- This slice's [[design.md]] — Sub-form B git-independence rewrite (deviation) + Sub-form A `Or`-exclusion correction (build-log records both)
- [[decisions/ADR-047]] — Deviation section + Introduced-residuals (#2 dissolved) + L27 Chosen-option strikethrough (m-add-R2-1); pre-commit edits sanctioned by /critique Step 4 ACCEPTED-FIXED
- This slice's [[mission-brief.md]] — AC1/AC2 + verification rows realigned to the git-independent + ADR-037-skip-with-note + anchored-regex spec
- [[shippability.md]] — row #44 added (Step 5.3 satisfied during /build-slice Task 7)
- No risk-register entry: the discoveries are now-known design constraints (gitignored vault) or codified rules (Or-disjunction), not open risks. R-1/R-2/R-3 unchanged; STP-1 introduces no new open risk.
