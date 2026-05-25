# Slice 044: add-state-transition-stale-pin-audit

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: recurring methodology-discipline class (N≥3) — "a slice performs a state transition but a pre-existing test still pins the OLD value, caught only at pre-finish BC-PROJ-4, never by the dual-Critic stack, sometimes latent N slices" (R-10 instance: slice-038→040, ~5-slice latency; slice-041 R-4 retirement FAILed `test_r_4_..._stays_mitigating`; slice-042 ADR-prose recurrence N+1). Explicitly nominated "Candidate Builder-plan-mode checklist item" by slice-041 AND slice-042.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

A new executable pre-finish gate `tools/state_transition_pin_audit.py` that detects when this slice flips a risk's `**Status**:` line OR repoints a `SKILL.md` prose anchor while a pre-existing test still asserts the OLD value and was not realigned in the same change set. Per this repo's own demonstrated law (slice-038 SRSC-1: *"prose binds nothing executable; the invoked single-sourced runner does"*; the dual-Critic stack structurally cannot reach the audit-vs-artifact interaction — only a pre-finish real-artifact gate can), this converts a class currently caught by luck/discipline into a loud, attributed HALT. Scoped to the two mechanically-detectable, highest-recurrence sub-forms; the fuzzy ADR-accepted→superseded sub-form is explicitly deferred (Out of scope).

## Acceptance criteria

1. `tools/state_transition_pin_audit.py` exists and detects the **risk-status-stale pin** sub-form as a **git-diff-independent standing invariant** (2026-05-18 plan-mode deviation — `architecture/` is gitignored so the original git-merge-base mechanism was inapplicable): a test whose `FunctionDef` name matches the anchored detector `(?:^|_)r[_-]?(\d+).*?_(stays|remains|is)_(open|mitigating|retired|accepted)(?:_|$)` claims `R-<num>`=`<status>`; if the **live** `architecture/risk-register.md` `**Status**:` for that risk ≠ the claimed status → actionable, attributed `stale-risk-status-pin` Important violation naming the risk ID, `claimed → live`, and the stale `tests/<file>::<fn>`; **exit code 1**. Live register parsed via the reused `risk_register_audit._parse_risks` (object-identity). No git invocation. Per-scanned-file AST `SyntaxError` ⇒ skip-with-visible-note, no violation, NOT exit 2 (ADR-037/PTFFD-1 — both sub-forms). Exit 2 `usage-error` reserved for hard-input failure only: register unparseable/missing, `tests/`/`skills/` dir missing, repo-root unresolvable. (Literal-detection leg out of v1 — false-positive-prone, no witnessed instance.)
2. The same tool detects the **SKILL.md-prose-repoint stale pin** sub-form (R-10's exact class): a positive-membership (`ast.In`, never `ast.NotIn`/`BoolOp`-nested) prose-pin whose folded-constant literal is ABSENT from the **full** target `SKILL.md` → `stale-skill-prose-pin` Important violation (exit 1) naming the stale pin's path + missing folded literal + SKILL.md. Covers both module-level and function-local `read_file(...)`→sliced-segment bindings. Git-diff-INDEPENDENT standing invariant. Non-constant operands are skipped (cannot prove absence).
3. `skills/build-slice/SKILL.md` Step 6 (pre-finish) invokes the audit non-opt-out and HALTs on any violation; the SKILL.md edit is forward-synced in-repo + installed (CAD-1 / skill-drift clean, EOL-agnostic per EOL-DRIFT-1).
4. A catalogued failing-repro regression test reconstructs R-10's exact scenario (a `test_*_skill.py` prose-pin asserting a since-repointed SKILL.md anchor): written FIRST, run against the unmodified tool to capture the FAIL, then PASSES post-implementation (slice-043 genuine-contrast discipline). The repro asserts the **exit-1 signature** — `kind == "stale-skill-prose-pin"` AND the named folded literal — NOT merely `exit != 0` (m-add: a coverage hole could otherwise let the tool exit 1 for the wrong reason and the repro still "pass"). Added to `architecture/shippability.md` with a runner-pinned `Machine-cmd`.
5. RULE-ID minted per the `-D`-vs-`vN.N` convention; 4-part PMI-1 atomic version bump (VERSION + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + `~/.claude/methodology-changelog.md`) + a rule-ID-bearing changelog entry-pin test; INST-1 / PMI-1 / CSP-1 / META-1 all clean.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Risk-status-stale detection (Sub-form B, standing invariant) | Fixture: temp tree, `architecture/risk-register.md` `## R-4 …` `**Status**: retired` + `tests/x.py` `def test_r_4_stays_mitigating(): ...` → exit 1 `stale-risk-status-pin` naming `R-4`, `mitigating → retired`, `tests/x.py::test_r_4_stays_mitigating`. Negatives (→ exit 0): fn renamed `test_r_4_retired_by_slice_041_…` (no verb-token); `test_r_4_stays_mitigating` while register `**Status**: mitigating` (claimed==live). NO git anywhere. |
| 1b | Sub-form B regex mechanical contrast (M-add-1 + targeted-M1 + targeted-M2) | Execute the implemented anchored regex against literals: `test_r_4_stays_mitigating` → MUST match `(4,stays,mitigating)`; `test_r_4_stays_mitigating_until_spike_done` → MUST match `(4,stays,mitigating)` (targeted-M2 suffixed-name false-negative closed); `test_addr_5_is_open` / `test_parser_4_is_retired` → MUST NOT match (targeted-M1 embedded-`r` collision suppressed — the old unanchored form DID match these); `test_r_4_retired_by_slice_041_030c_completes_the_split` → MUST NOT match (realigned, no verb-token); `test_r_10_is_retired` → MUST match `(10,is,retired)`. |
| 1c | Per-file SyntaxError skip-with-note (targeted-B1/B2) | Fixture tree containing an unparseable `tests/…/syntax_error.py` (mirrors the real `tests/methodology/fixtures/syntax_error.py`) AND no real stale pin → audit exits **0** with a rendered skip-note for that file (ADR-037/PTFFD-1), NOT exit 2. Asserts STP-1's exit-2 path is reserved for hard-input failure only. |
| 2 | SKILL.md-prose-repoint detection (Sub-form A) | Fixture: a module-level-bound AND a function-local `content = read_file(...)`→`prereq_block = content.split(...)[1]` sliced-segment pin asserting `"OLD ANCHOR"` absent from the full target SKILL.md → exit 1 `stale-skill-prose-pin` naming pin path + missing folded literal + SKILL.md. Negatives (all → exit 0): pin literal present in the full SKILL.md (even if not in the sliced segment); a `not in`/`BoolOp`-nested `not in` pin whose literal is deliberately absent (B1); an f-string/`+`-built/non-constant operand (skipped). |
| 2b | Folded multi-line literal (B3) | Fixture: a 3-line implicitly-concatenated literal pin — folded value present → exit 0; folded value absent → exit 1 with the **full folded** literal in the message (never a mis-extracted prefix). |
| 2c | Positive `BoolOp` conjunction NOT dropped (B-add-1) | Fixture mirroring `test_build_slice_skill.py:187-190` (`"A" in BUILD and "B" in BUILD`, both positive `ast.In`): one literal absent → exit 1 (the absent operand flagged). Negative: mixed `"x" not in c or "NEVER" in c` with `"x"` deliberately absent → exit 0. Plus: at build, machine-classify the full corpus `BoolOp`-pin set (positive-only vs mixed) and record the count in build-log. |
| 3 | Pre-finish wiring | `grep` `skills/build-slice/SKILL.md` Step 6 for the non-opt-out invocation; run `tools/critique_agent_drift_audit.py` + skill-drift suite → clean; confirm installed copy forward-synced (`assert_md_forward_synced`). |
| 3b | Object-identity reuse (CSP-1; M2) | Assert `state_transition_pin_audit._parse_risks is risk_register_audit._parse_risks` (the surviving CSP-1 reuse — `_resolve_default_branch` reuse dropped: no git in the revised design). Register-unparseable fixture → exit 2 attributed `usage-error`, never silent exit 0 (fail-closed). |
| 3c | Self-application dogfood (RSAD-1) | Run `$PY -m tools.state_transition_pin_audit` against the live repo (git-independent — works despite the gitignored vault) at this slice's own mid-slice smoke + Step 6 → exit 0: no live test fn-name matches the verb-token detector contradicting the live register (verified — only `test_r_4_retired_by_slice_041_…` exists, no `_(stays|remains|is)_` token), and slice-044 introduces no removed-anchor prose-pin. |
| 4 | Catalogued failing repro | `git stash` the tool change, run the new repro test → assert it FAILs with the expected signature; restore → assert PASSES. AC4 row populates the full 6-column `shippability.md` schema, backtick-wrapped `Machine-cmd` (SCMD-1), final PTFFD-1-clean `::`-selector, added LAST (slice-037); `tools/shippability_runner.py architecture/shippability.md` passes it. |
| 5 | Version/rule-ID integrity | `tools/plugin_manifest_audit.py` (PMI-1) clean; the 4 version legs equal; the rule-ID-bearing entry-pin test passes; `tools/install_audit.py` (INST-1) clean; META-1 changelog-split test clean (recompute the why-none/entry-pin obligation against the actual `test_methodology_changelog.py` assertion, not the slice-037/040 precedent — slice-040/043 lesson). |

## Must-not-defer

- [ ] **Fail-closed on hard-input failure, never silent-default-off** (R-7 / TFFL-1 precedent): an unparseable/missing `architecture/risk-register.md`, missing `tests/`/`skills/` dir, or unresolvable repo-root must HALT loudly with an attributed `usage-error` (exit 2) — NEVER pass silently. A **per-scanned-file AST `SyntaxError` is NOT this case** — it is skip-with-visible-note (ADR-037/PTFFD-1; targeted-critique B1/B2), so the lone permanent `tests/methodology/fixtures/syntax_error.py` does not false-HALT the gate. (No git failure mode exists post-deviation.)
- [ ] **Actionable, attributed messages** (R-6 / ADR-046 BRANCH-1 precedent): every violation names the slice's transition (risk ID + old→new, or SKILL.md + missing anchor) AND the stale test path, with a one-line remediation hint.
- [ ] **No false-positive on the live clean tree**: running the audit on the current repo (no in-flight stale pins) must exit 0 — the gate must not block innocent slices (the false-PCA-1-HALT class it is designed to remove).
- [ ] Observability: violation output is greppable and self-attributing (kind + exit code stable, consistent with sibling `tools/*_audit.py`).

## Out of scope

- The **ADR accepted→superseded stale-pin sub-form** — fuzziest mechanizability (no canonical machine-readable "this test pinned the superseded ADR's prior claim" signal); note as a possible follow-up slice in /reflect Discovered.
- Fixing any *existing* stale pin — there are none in-flight (R-10 retired by slice-040; slice-041's was caught in-slice). This slice adds the gate; it does not remediate history.
- The broader prose plan-mode checklist (candidate #2) beyond what this executable audit mechanizes.
- Plan-mode-stage invocation — this slice wires the audit at `/build-slice` Step 6 pre-finish only; a plan-mode-stage variant is a separate decision.

## Dependencies

- Prior slices: [[slice-040-realign-validate-slice-step-5-5-prose-pin]] (R-10 retirement — the exact class this generalizes), [[slice-038-pin-shippability-runner-segment-contract]] (SRSC-1 SKILL.md repoint that rooted R-10), [[slice-041-reframe-installed-pin-forward-sync-invariant]] (R-4 stale `test_r_4_..._stays_mitigating` instance), [[slice-037-extend-ptfcd-1-to-test-function-level]] (PTFFD-1 — sibling audit-codification pattern to follow), [[slice-034-fix-tf1-audit-field-line-regex]] (TFFL-1 — fail-closed-not-silent-default-off precedent), [[slice-043-codify-split-slice-folder-naming-convention]] (ADR-046 — actionable attributed `usage-error` message precedent).
- Vault refs: [[methodology-changelog]], [[shippability]], CLAUDE.md "Vault discipline" + "Self-hosting discipline", ADR `-D`-vs-`vN.N` convention ([[ADR-038]]).
- Risk register: [[risk-register#R-10]] (retired instance of this class), [[risk-register#R-4]] (sub-entry stale-pin instance).

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m tools.state_transition_pin_audit                        # live repo (git-independent; RSAD-1 self-dogfood)
$PY -m tools.state_transition_pin_audit --root <r10-fixture>   # Sub-form A: R-10 reconstruction (sliced-segment + module-level)
$PY -m tools.state_transition_pin_audit --root <notin-fixture> # Sub-form A: deliberately-absent `not in` pin (B1)
$PY -m tools.state_transition_pin_audit --root <rstatus-fixture> # Sub-form B: register R-4 retired + test_r_4_stays_mitigating
```
Expected: live repo → **exit 0** (no false-positive — no live test contradicts the register; no removed-anchor prose-pin). R-10 fixture → **exit 1** `stale-skill-prose-pin`, message names the stale pin path + missing folded literal + target SKILL.md. `not in` fixture → **exit 0** (B1: negative pin never flagged). `rstatus` fixture → **exit 1** `stale-risk-status-pin` naming `R-4`, `mitigating → retired`, the stale test. If any diverges: STOP, diagnose, do not continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (fail-closed, attributed, no live false-positive, observable)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] BC-1 / RR-1 / CAD-1 / PMI-1 / INST-1 / DR-1 / SUP-1 / SCMD-1 / SRSC-1 + the new gate all green on the real artifact (BC-PROJ-4 discipline)
