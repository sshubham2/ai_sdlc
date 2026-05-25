# Reflection: Slice 005 add-bc-1-keyword-precision

**Date**: 2026-05-10
**Shipped**: YES-WITH-DEFERRALS

## Validated

- **Word-boundary regex (`\bkw\b`) + per-rule `Trigger anchors:` mechanism silences the N=2 confirmed false-positive class** — validated empirically by AC #1 (slice-003 archive backtest: applicable=[], all 3 rules in skipped) AND AC #2 (slice-004 archive backtest: same shape) AND positive-case AC #3 (synthetic LLM-fence brief fires `{BC-PROJ-2, BC-GLOBAL-1}` via `\bllm\b` + `\bcode-block\b` anchor matches). The aggregated-lessons "BC-1 trigger-keyword precision is overdue" claim from slice-003+004 is now closed; the noise-floor on BC-1 surfacing is reset.
- **Schema-pin TWO-surface discipline (per Critic M3) — both files (`architecture/build-checks.md` + `~/.claude/build-checks.md`) contain BOTH literal substrings (`Trigger anchors` + `word-boundary`)** — validated by 2 prose-pin tests passing AND PowerShell `Get-Content -Raw | .Contains(...)` checks. Future doc-refactor drift on either surface in either file fails loudly.
- **`anchor-not-in-keywords` parse-violation kind** — validated by `test_anchor_not_in_keywords_yields_violation` (constructs inline tmp_path fixture with bad anchor; assertions on violation kind + rule_id + offending anchor's name in message). Input-validation must-not-defer loop closed (per Critic M2).
- **`test_migrated_rules_have_expected_anchors` catches migration typos** — validated by reading the actual `architecture/build-checks.md` via `_parse_rules` and asserting BC-PROJ-1.trigger_anchors == ('subagent', 'fan-out') AND BC-PROJ-2.trigger_anchors == ('fence', 'code-block', 'llm'). Without this test (per Critic M1), a `Trigger anchors: fenced, code-block, llm` typo would silently ship — backtest tests pass either way for slice-003+004 (those briefs have neither variant).
- **TF-1 PENDING → WRITTEN-FAILING genuineness — per slice-003 lesson, each transition was unambiguous**. Pre-T3: 6 of 7 new tests fail with distinct failure modes (`AttributeError` on missing `trigger_anchors` attribute; `AssertionError` on BC-PROJ-2 in applicable; missing schema substring; missing violation kind). Test #3 (positive case) passes pre-fix as a regression-guard shape (expected). The "fix not applied" vs "fix doesn't exist" distinction is locked.
- **Voluntary Critic on a low-tier cross-cutting slice paid off — fifth consecutive confirmation, with B1 + B2 both fatal catches at design time AND M1/M2/M3 forcing TF-1 plan growth from 4 → 7 rows**. Tier=low, critic-required=false. User invoked /critique anyway. Returned 9 findings (2 blockers + 3 majors + 4 minors); ALL 9 ratified ACCEPTED-FIXED or ACCEPTED-PENDING; ALL 9 confirmed VALIDATED at validate-time. Pattern hardening: voluntary Critic on cross-cutting low-tier slices is N=5/5 paid off; **3 of 5 (slice-003 m1 false-PASS warning + slice-004 B1 fatal catch + slice-005 B2 wording-mismatch catch) caught design-stage failures that would have failed at build time**.
- **"Validate using your own ship" pattern reused — third confirmation (slice-003 + slice-004 + slice-005)**. Slice-005 ran VAL-1 self-application with `--imports-allowlist tests` and got "Clean — both layers passed." The pattern is now N=3 stable.
- **Empirical-verification-at-design-time discipline ratchets to N=4 distinct slices** (slice-001 cwd-mismatch hypothesis + slice-003 argparse exit-code-2 collision + slice-004 R-NN literal-match catch + slice-005 word-boundary-alone-insufficient empirical realization). The cost (~30 seconds) saves entire slice cycles every time. Treating this as standard discipline.

## Corrected

- **DEVIATION-1 (mid-build, T5)**: BC-GLOBAL-1's `Applies to: always: true` → `Applies to: **`. The `_rule_applies` algorithm short-circuits before the anchor filter when `applies_to == ("always",)`, so anchor-based silencing was unreachable for BC-GLOBAL-1. Three options surfaced to user (hardcoded language list rejected as brittle; algorithm change rejected as semantic break; `**` glob accepted as language-agnostic). `~/.claude/build-checks.md` updated with the deviation rationale + design.md "What's new" / "Components touched > ~/.claude/build-checks.md" sections updated. Real-world `/build-slice` invocations always pass `--changed-files`, so BC-GLOBAL-1 fires identically on every real slice (same effective behavior). Backtests on archive folders without `--changed-files` correctly fall through to anchor-filtered keyword path. ADR-004 NOT superseded — the decision-level intent (word-boundary + Trigger anchors) is unchanged; only the migration tactic for BC-GLOBAL-1's `Applies to:` needed adjustment.

- **DEVIATION-2 (mid-build, T7)**: AC #4 (regression-guard "no regression in existing 18 BC-1 tests") DEMOTED from numbered-AC list to verification-plan + must-not-defer track. Original AC #5 (schema-pin) renumbered to AC #4. mission-brief.md ACs are now 1-4 (was 1-5). Reason: TF-1 strict-pre-finish refused with `ac-without-row` because regression-guard ACs cannot have a meaningful TF-1 row — a test asserting "all other tests pass" is circular meta-AC per slice-002+slice-004 lessons. Same calibration class as slice-002's "Don't write meta-ACs" lesson and slice-004's "AC #3 invariant-assertion is also a meta-AC variant — move to verification-plan + must-not-defer track" lesson. **N=3 confirmation now**.

- **Slice's mission-brief.md / design.md / critique.md / ADR-004 absorbed all 9 Critic ACCEPTED-FIXED + 1 ACCEPTED-PENDING edits** during /critique triage and at /build-slice T5/T7 deviation-handling. Listed for completeness: B1 (must-not-defer #5 reformulation + pre-finish gate item), B2 (AC #3 wording aligned with design empirical-table), M1 (TF-1 row added for migrated anchor tuples), M2 (anchor-not-in-keywords promoted to TF-1), M3 (schema-pin split into two surfaces, two TF-1 rows), m1 (error-model prose clarification), m2 (ADR-004 inline citations), m3 (line-range → symbol reference), m4 (CI-gap acknowledgment in design.md Builder notes; resolved at validate via local pin runs).

- **No ADRs superseded** — ADR-004 stands as accepted; ADR-001/002/003 unrelated to this slice's scope.

## Discovered

- **Pre-existing bug: `audit_slice` default heuristic broken for archived slice paths** (slice-005 mid-build T4 discovery). The heuristic `slice_folder.parent.parent / "build-checks.md"` resolves to `architecture/slices/build-checks.md` for archived slice paths because `archive/` violates the depth assumption. Workaround: pass `--project-checks architecture/build-checks.md` explicitly. Pre-existing in `tools/build_checks_audit.py:332-334` (BC-1 v0.10.0); NOT slice-005's scope. **Slice-006+ candidate (`fix-bc-1-archived-slice-heuristic`, ~30 min effort)** — fix the heuristic to recognize the `archive/` segment OR add explicit support for archived slices.

- **`_rule_applies` algorithm-vs-AC interaction surface that empirical-verification-at-design-time DID NOT cover** (slice-005 mid-build T5 surface). The design's empirical-verification table counted anchor matches but not algorithm-path interaction (`always: true` short-circuits before anchors). Caught only at /build-slice T5 when post-anchor-migration backtests still showed BC-GLOBAL-1 firing. **Generic methodology-discipline lesson**: empirical verification at design-time should exercise algorithm paths (always-true → glob → keyword), not just isolated metric counts. **Possible BC-1 promotion candidate** if the pattern recurs in slice-006+ — for now, log in lessons-learned and aggregated-lessons.

- **BC-1 v1 morphological-variant limitation surfaces concretely** in AC #3's example (`fenced` vs `fence` mismatch caught by Critic B2). Acknowledged in design as deferrable; surfaced again here as the AC #3 wording case. Future slices that mention only morphological forms (e.g., "fenced output" without bare "fence") will defer-with-rationale; that's acceptable. Promote to BC-1 keyword-list expansion only if it becomes a real recurring noise source.

- **Cross-cutting-conformance Critic-miss class hardens to N=5 distinct slices**. Pattern: slice-001 (environmental/runtime + tooling-conformance), slice-002 (methodology-conformance + tooling-conformance), slice-003 (testing-discipline-conformance + tooling-conformance), slice-004 (testing-discipline-conformance + language-version-conformance), slice-005 (testing-discipline-conformance via Critic-caught B2 wording mismatch + **algorithm-path-conformance** via Critic-MISSED BC-GLOBAL-1 always-true interaction). The 9th Critic dimension proposal (cross-cutting conformance) now has the strongest evidence base in the project — N=5 distinct slices with 10 sub-class hits. **`/critic-calibrate` ≥5-archived-slices threshold is now MET (slice-005 archives next).**

## Deferred

- **`fix-bc-1-archived-slice-heuristic`** — NEW (slice-005 discovery). Pre-existing bug in `audit_slice`'s `parent.parent` heuristic; one-off fix; ~30 min. Workaround (`--project-checks` explicit) acceptable until then.
- **`/critic-calibrate` meta-skill run** — NOW UNBLOCKED. ≥5 archived slices threshold reached after this slice archives. Slice-006 strongest candidate; the 9th Critic dimension proposal has 10 sub-class hits across 5 slices.
- **`add-csp-1-docstring-or-regex`** — slice-004 carryover; sibling tooling slice with identical bug pattern in `tools/cross_spec_parity_audit.py`. Independent of slice-005; ~30-60 min slice; carries forward to slice-006+ candidate list.
- **BC-1 morphological-variant keyword expansion** (e.g., adding `fenced, parses, parsed, parsing` to BC-PROJ-2's `Trigger keywords`) — design out-of-scope; deferred until a future slice's brief mentions only the morphological variant without the bare anchor word AND the case becomes a real noise-source.
- **`~/.claude/build-checks.md` CI gap closure** — m4 ACCEPTED-PENDING resolved at /validate-slice via local pin manual runs; the structural CI gap (`pytest.skip` when global file absent) remains documented in design.md Builder notes for future maintenance. Future slice could promote global-file pins to a separate local-only test-suite. Low priority.
- **Setuptools `[tool.setuptools.packages.find]` auto-discovery** + multi-backend support (Hatch, PDM, Flit) + dotted-only setuptools-packages top-component fallback — carried from slice-003's deferred list.
- **R-1 deeper fixes** (orchestrator pre-cd; parent-thread pre-compute) — open in risk-register; documented-constraint workaround still acceptable per slice-002.
- **R-2 programmatic test of cwd-warning runtime emission** — open in risk-register; deferred until evidence of regression.
- **BC-1 promotion of empirical-verification-algorithm-paths lesson** — N=1 occurrence (slice-005 only); logging in lessons-learned for now; promote if recurs in slice-006+.

## Critic calibration

Per **TRI-1**, scoring each finding from `critique.md` `## Triage` table against build + validate reality:

- **B1** (must-not-defer #5 self-application contradiction): **VALIDATED** — disposition ACCEPTED-FIXED; reformulation worked exactly. Slice-005 self-application yielded {BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1} — exactly 3 rules, no fourth, "expected meta-reference fire" rationale held. The Critic's framing was the correct disposition.
- **B2** (AC #3 example wording `fenced` vs `fence`): **VALIDATED** — disposition ACCEPTED-FIXED; the synthetic positive case post-fix matches `llm` + `code-block` anchors as designed. If AC had stayed `fenced`-only, the test would have passed only via `llm` alone; the asymmetry would have been opaque. **Critic was right and prevented a misleading test.** Fatal catch.
- **M1** (TF-1 plan no row for migrated rule parsing): **VALIDATED** — disposition ACCEPTED-FIXED; `test_migrated_rules_have_expected_anchors` passed after migration. Without it, anchor-list typos would silently ship. Critic was right.
- **M2** (anchor-not-in-keywords OPTIONAL contradicts must-not-defer): **VALIDATED** — disposition ACCEPTED-FIXED; promoted to TF-1; closes input-validation must-not-defer loop. Critic was right.
- **M3** (schema-pin TWO surfaces): **VALIDATED** — disposition ACCEPTED-FIXED; both `Trigger anchors` AND `word-boundary` substrings pinned in both files. Critic was right; preventive against future doc-refactor drift.
- **m1** (error-model prose contradiction): **VALIDATED** — disposition ACCEPTED-FIXED; cosmetic prose-vs-code alignment. Critic was right; preventive.
- **m2** (backward-compat claim asserted not measured): **VALIDATED** — disposition ACCEPTED-FIXED; ADR-004 has inline production-rule + 2-fixture citations. Critic was right; traceability improvement.
- **m3** (line-range reference brittle): **VALIDATED** — disposition ACCEPTED-FIXED; symbol reference `::_rule_applies` used. Critic was right; resilient against future edits.
- **m4** (schema-pin global-file CI gap): **VALIDATED** — disposition ACCEPTED-PENDING; resolved at validate via local pin manual runs (both prose-pin tests passed against `~/.claude/build-checks.md`). CI gap structurally remains; documented for future maintenance. Critic was right; correct disposition.

**Missed by Critic**:

- **BC-GLOBAL-1's `Applies to: always: true` short-circuits before the anchor filter**, making AC #1+#2 unachievable as locked. The Critic reviewed the algorithm pseudocode in design.md (the snippet showing `if rule.trigger_anchors: return any(...)`) and the migration list (BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 all getting anchors) but didn't trace through the ALREADY-EXISTING `if rule.applies_to == ("always",): return True` short-circuit at the top of `_rule_applies` to ask "do all 3 migration targets have a non-always-true `Applies to`?". They don't — BC-GLOBAL-1 was always-true. Surfaced empirically at /build-slice T5 when post-anchor-migration backtests still showed BC-GLOBAL-1 firing. **Calibration class: algorithm-path-conformance** — does the slice's proposed algorithm interact correctly with the existing audit's pre-existing branches (`always: true` short-circuit, glob path, keyword path)? **The Critic should ask: "When this slice adds a new branch to existing logic, does each pre-existing branch correctly compose with the new branch in all the cases the design needs?"**

**Pattern (cumulative across slice-001 + slice-002 + slice-003 + slice-004 + slice-005)**: cross-cutting-conformance miss-class hardens to N=5 with 10 sub-class hits. The Critic is strong on internal technical consistency within the slice's scope but consistently misses **conformance to upstream constraints / pre-existing systems**:

- **slice-001**: environmental/runtime conformance (cwd-mismatch tool denial); tooling-conformance (legacy templates contradicting new contract)
- **slice-002**: methodology-conformance (5-AC TF-1-incompatible); tooling-conformance (RR-1 docstring-vs-regex)
- **slice-003**: testing-discipline-conformance (TF-1 false-PASS via argparse exit-code-2); tooling-conformance (BC-1 trigger-keyword precision — fixed THIS slice)
- **slice-004**: testing-discipline-conformance (R-NN vs `\d+` empirical-verification gap, caught by Critic); language-version-conformance (Python 3.12+ docstring escape-sequence, missed by Critic)
- **slice-005**: testing-discipline-conformance (B2 fenced/fence wording, caught by Critic); **algorithm-path-conformance** (BC-GLOBAL-1 always-true short-circuit, missed by Critic)

**N=5 distinct slices, 10 sub-class hits**. The 9th Critic dimension proposal (cross-cutting conformance) now has the strongest evidence base in the project. Sub-clauses:
- methodology-audit conformance (TF-1, RR-1, WIRE-1, BC-1, NFR-1, VAL-1)
- tooling-doc-vs-implementation parity
- BC-1 trigger-keyword false-positive anticipation
- TF-1 PENDING→WRITTEN-FAILING genuineness
- runtime-environment assumptions
- language-version conformance (added at slice-004)
- **algorithm-path-conformance** (added at slice-005 — when adding a new branch to existing logic, trace through ALL pre-existing branches)

**`/critic-calibrate` ≥5-archived-slices threshold MET after slice-005 archives.** Slice-006 strongest candidate.

## Lessons for next slice

- **Empirical verification at design-time should exercise ALGORITHM PATHS, not just isolated metric counts.** Slice-005's empirical-verification table counted anchor matches but missed the `always: true` short-circuit ahead of anchors. When the design adds a new branch to existing logic, trace through ALL pre-existing branches (always-true → glob → keyword) to ensure the new branch is reachable in the cases the design needs it for. **Generic methodology-discipline lesson — N=1 occurrence; promote to BC-1 if recurs in slice-006+.**
- **Regression-guard ACs MUST be authored into verification-plan + must-not-defer, NOT into the numbered-AC list.** N=3 confirmation (slice-002 5-AC + slice-004 AC #3 invariant + slice-005 AC #4 regression-guard). All three were caught by TF-1 strict-pre-finish; all three required mid-slice demotion. **Aggregated-lesson candidate** — `/slice` and `/design-slice` should pre-flight regression-guard ACs out of the numbered list.
- **`/critic-calibrate` is NOW RUNNABLE.** ≥5 archived slices threshold met after slice-005 archives. The 9th Critic dimension proposal has 10 sub-class hits across 5 slices — strongest evidence base in the project. Slice-006 strongest candidate; running it before slice-007 would feed Critic prompt updates AND user-judgement awareness signals (TRI-1 calibration vocabulary now distinguishes Critic accuracy from user-override accuracy).
- **Voluntary Critic on cross-cutting low-tier slices is now N=5/5 paid off, with 3 of 5 catching design-stage failures that would have failed at build time** (slice-003 m1 false-PASS warning + slice-004 B1 fatal catch + slice-005 B2 wording-mismatch catch). Default heuristic continues to apply.
- **"Validate using your own ship" pattern is N=3 stable.** Future audit-shipping slices reuse `--imports-allowlist tests`.
- **Empirical-verification-at-design-time discipline is N=4 across slices.** Treating it as standard practice. Now also includes algorithm-path coverage (per the slice-005 lesson above).
- **Out-of-repo edits (`~/.claude/...`) require explicit forensic capture in build-log.md.** Slice-005 captured the BC-GLOBAL-1 before/after diff. Future slices touching `~/.claude/...` should follow the pattern; the slice's git diff alone is insufficient evidence.

## Vault updates made (thin vault)

- `architecture/lessons-learned.md` — slice-005 entry appended (see Step 5)
- `architecture/shippability.md` — slice-005 critical-path test entry appended (see Step 5.3)
- `architecture/slices/slice-005-add-bc-1-keyword-precision/` — to be auto-archived in Step 6
- `architecture/slices/_index.md` and `architecture/slices/archive/_index.md` — to be regenerated in Step 6
- This slice's [`design.md`](design.md), [`mission-brief.md`](mission-brief.md), [`ADR-004`](../../decisions/ADR-004-bc-1-keyword-precision-via-word-boundary-and-anchors.md) — already updated during /critique with 9 ACCEPTED-FIXED + 1 ACCEPTED-PENDING fixes; updated again at /build-slice T5 (DEVIATION-1) + T7 (DEVIATION-2)
- This slice's [`build-log.md`](build-log.md) — already captures 8/8 task progression + 2 deviations + 1 discovery + 1 deferral
- This slice's [`validation.md`](validation.md) — captures 4/4 ACs PASS + regression-guard + VAL-1 clean + shippability 41/41 + m4 resolved
- `architecture/risk-register.md` — no new risks added (the 2 deviations + 1 mid-build discovery are tooling-conformance issues, not project risks)
- No ADRs superseded — ADR-004 stands as accepted; ADR-001/002/003 unrelated
