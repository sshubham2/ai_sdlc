# Slice 030: repair-build-checks-vault-and-harden-shippability

**Mode**: Standard
**Estimated work**: ~0.5–1 day (030A split scope: reconstruct + tracked literal-constant oracle + BCI-1 + propagation; NO shippability-row repoint / archive fixturization — those are 030B)
**Risk retired**: [[risk-register#R-4]] — Local AI-SDLC-vault build-checks.md corruption (BC-1 coverage silently degraded), open, score 4 (top-ranked open risk)
**Test-first**: false  (BFRD-1 prelude already supplies the failing repro `tests/methodology/test_build_checks_audit.py`; `/design-slice` may opt the AC-4 regression test into a TF-1 plan)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

R-4: both `architecture/build-checks.md` (project) and `~/.claude/build-checks.md` (global) were found truncated to ONLY the slice-028-promoted rule (`BC-PROJ-3` / `BC-GLOBAL-2`), silently losing `BC-PROJ-1`, `BC-PROJ-2`, and `BC-GLOBAL-1`. BC-1's evergreen pre-finish coverage is therefore degraded on this machine. **030A scope**: restore the lost rules from new git-tracked canonical fixtures backed by an all-5-rule literal-constant tracked oracle, and make any future silent degradation impossible by adding a deterministic non-opt-out full-structural-identity gate (BCI-1) at `/build-slice` pre-finish + `/reflect` Step5b post-write. `/reflect` Step 5b has no deterministic source (it is LLM-executed prose — B2/ADR-029); the durable control is the downstream BCI-1 invariant gate, regression-tested. **Decoupling the shippability catalog rows #5/#8/#12 from gitignored content (the original "harden shippability" goal) is DEFERRED to 030B** — see "Deferred to slice 030B"; 030A retires R-4's *substance* (silent degradation), 030B removes the residual catalog brittleness.

> **v3 / SPLIT to 030A scope (2026-05-16).** After two BLOCKED dual-Critic loops, the v2 meta-Critic surfaced a non-convergence (flaw-relocation) signal. User decision (AskUserQuestion, 2026-05-16): **split**. This slice is now the **minimal emergency 030A**: reconstruct + full-structural-identity tracked-fixture oracle + non-opt-out BCI-1 gate. The shippability-catalog decoupling (v2-B1, meta M-add-1) and archive-backtest synthetic-vs-real-corpus fidelity (meta M1′) are **DEFERRED to follow-up slice 030B** (see "Deferred to 030B" + design.md). v1/v2 ACs superseded by the 030A ACs below. Audit trail: `critique-history-v1.md`, `critique.md` (v2 re-critique), `critique-review.md` (v2 dual-review EXTEND).

## Acceptance criteria (030A)

1. Both `architecture/build-checks.md` and `~/.claude/build-checks.md` are reconstructed from new git-tracked canonical fixtures (`tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md`) and parse (via `tools/build_checks_audit.py._parse_rules`) to exactly `{BC-PROJ-1, BC-PROJ-2, BC-PROJ-3}` and `{BC-GLOBAL-1, BC-GLOBAL-2}`. The failing repro `tests/methodology/test_build_checks_audit.py` PASSES (17 failed → 0 failed) — BFRD-1 closure; the 4 schema-substring pins satisfied by a fixture schema preamble recovered from the **git-tracked** `tools/build_checks_audit.py` module docstring (v1-B3, verified).
2. The tracked test file `tests/methodology/test_build_checks_audit.py` carries **literal-constant** full-structural-identity pins covering `(severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` for **all five** rules — BC-PROJ-1/2 + BC-GLOBAL-1 (existing anchor/neg-anchor tuple pins **extended to also pin `applies_to` + `trigger_keywords`** — B2: these had no literal pins, leaving the oracle circular for the fields rows #8/#12 depend on) AND **BC-PROJ-3 + BC-GLOBAL-2** (NEW pins). The fixtures are asserted *against these literal constants* (fixture = subject; **the test-file literal constant is the git-tracked oracle** — `tests/` is git-tracked). **Recovery-input note (B2 source correction)**: the `architecture/slices/archive/` build-logs/designs are *gitignored* (`git ls-files architecture/` → 0) — they are best-effort *recovery input* for authoring the literal constants, NOT themselves tracked oracles. Authoritative source priority: surviving uncorrupted live body (for BC-PROJ-3/BC-GLOBAL-2, lossless-vs-truncation) > archive build-log verbatim body (e.g. slice-005 BC-GLOBAL-1 `Applies to: **` DEVIATION-1; slice-008 BC-PROJ-1 glob) > archive prose. Residual (no pre-R-4 byte-tracked oracle for the 3 lost rules' applies_to/keywords) named honestly per M1/M3; accepted because BCI-1 makes any *future* drift loud. Closes v2-B3 / meta-M-add-3 for all five rules.
3. A deterministic `tools/build_checks_integrity.py` (rule **BCI-1**) asserts, per rule, **full canonical structural identity** — `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check` — of the live files vs the tracked fixtures (NOT rule-ID-set-only; meta-M-add-2). Divergence ⇒ exit 1 + attributed *"LOCAL VAULT DRIFT — reconstruct from <fixture>; NOT a slice regression"*. **Absent** `~/.claude/build-checks.md` (file does not exist) ⇒ distinct WARN (exit 0 + message), `/build-slice` treats as WARN-not-HALT; **present-and-non-conformant including empty** ⇒ HALT (meta-M3, refined). Wired non-opt-out at `/build-slice` pre-finish + a fail-loud `skills/reflect/SKILL.md` Step 5b post-write instruction (B2/ADR-029: the only testable lever for an LLM-executed step is a deterministic downstream gate).
4. A regression test exercises `tools/build_checks_integrity.py`: PASSES on the full canonical set; FAILS loud (exit 1 + attributed message) on a synthetic file truncated to one rule; emits the WARN path (not HALT) on a synthetic absent-global; HALTs on a synthetic empty-global. Tests the deterministic tool (B2-correct).
5. New-tool propagation is correct and complete (meta-M2 — checklist file-locations corrected): `tools/install_audit.py` `_CANONICAL_TOOLS` (only; no count comment exists); `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` += `tools.build_checks_integrity` (mandatory — sentinel auto-discovers via AST `main` but fails-closed on coverage); `plugin.yaml` (PMI-1, rule BCI-1, atomic `VERSION`+`plugin.yaml.version` bump); `methodology-changelog.md` BCI-1 entry; INST-1 install_audit↔plugin.yaml parity; pre-suite "run BCI-1 against its own repo" self-violation gate. The tool has a top-level `main` + `_stdout.reconfigure_stdout_utf8()`.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Reconstruct from fixtures; BFRD-1 closure | Both live files byte-reconstructed from the tracked fixtures; `$PY -m pytest tests/methodology/test_build_checks_audit.py --no-header -q` → `0 failed` (was `17 failed, 21 passed`); 4 schema-substring pins green; `_parse_rules` on both live files yields `{BC-PROJ-1,2,3}`/`{BC-GLOBAL-1,2}` |
| 2 | All-5-rule literal-constant tracked oracle | Repointed `test_migrated_rules_*` retain literal tuple constants **and add `applies_to`+`trigger_keywords` literal pins**; NEW structural pins for BC-PROJ-3 + BC-GLOBAL-2; fixtures asserted *against* the literals (not derive-from-fixture). **Specifically assert reconstructed `BC-GLOBAL-1.applies_to == ("**",)`** (slice-005 DEVIATION-1 value — guards the coincidental-pass path where `always:true` would still land slice-005 in `skipped`). `$PY -m pytest <those tests> -q` green |
| 3 | BCI-1 full structural identity + semantics | `$PY -m tools.build_checks_integrity --check-live` exit 0 on conformant; exit 1 + attributed message on per-rule field divergence (anchors OR severity OR applies_to OR trigger_keywords OR empty check); WARN (exit 0+msg) on absent global; HALT on empty global. Wired in `/build-slice` pre-finish + Step5b post-write prose |
| 4 | Regression test exercises the tool | New test: PASS on full canonical set; FAIL-loud on 1-rule truncation; FAIL on a single corrupted `Applies to:`/`Severity` field (proves full-identity not ID-only); WARN-path on absent-global; HALT on empty-global; `$PY -m pytest <new test> -q` green |
| 5 | New-tool propagation correct + self-clean | `$PY -m tools.install_audit` clean; `$PY -m pytest tests/methodology/test_utf8_stdout_regression.py -q` green (tool in `_ROOT_ONLY_TOOLS`); `plugin.yaml.version == VERSION`; methodology-changelog BCI-1 entry test green; `$PY -m tools.build_checks_integrity` run against this repo BEFORE the suite (self-violation gate) exits 0 |

## Must-not-defer

- [ ] B2 finding written: `/reflect` Step 5b is LLM-executed prose with NO deterministic promotion function — documented explicitly; the lever is the deterministic BCI-1 downstream gate (NOT a non-existent "source defect" fix).
- [ ] BOTH `build-checks.md` files reconstructed (project + global) from the tracked canonical fixtures — not just one. BC-PROJ-3/BC-GLOBAL-2 fixture bodies are pinned to NEW tracked literal-constant assertions (authoritative source = the surviving uncorrupted live bodies, corroborated against the slice-028 promotion record) — NOT sourced only from the suspect live file (meta-M-add-3). Honest best-effort framing recorded for BC-PROJ-1/2/BC-GLOBAL-1 prose (M3 per-rule table).
- [ ] BCI-1 asserts FULL per-rule structural identity `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check` — NOT rule-ID-set-only (meta-M-add-2). **Internal-consistency VERIFICATION TASK (B1 — not a self-attestation)**: at `/build-slice` Step 6, `grep -rn "rule-ID set\|rule-ID-set\|set-identity" mission-brief.md design.md ADR-028 ADR-029` must return zero "BCI-1 asserts …" hits, AND ADR-029's "wiring points" count must read "two (030A)". ADR-029 stale "rule-ID set"/"(c) shippability catalog row"/"three wiring points" text was corrected 2026-05-16 per B1 — re-grep to confirm, do not assume.
- [ ] BCI-1 absent-vs-non-conformant semantics explicit (meta-M3): absent global file ⇒ WARN-not-HALT; present-and-non-conformant **including empty** ⇒ HALT (empty global routes to HALT — R-4-global not silently reopened).
- [ ] BCI-1 is **non-opt-out** at `/build-slice` pre-finish + a fail-loud Step 5b post-write instruction. Truncation is fail-loud at every consuming gate — never the silent zero-rule degradation of the bare BC-1 path (M2).
- [ ] New-tool propagation file-locations CORRECT (meta-M2): `install_audit._CANONICAL_TOOLS` (only — no count comment exists, do NOT add one); `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` += `tools.build_checks_integrity` (mandatory coverage edit — auto-discovery via AST `main` is automatic, coverage is NOT); `plugin.yaml`/PMI-1/atomic VERSION; `methodology-changelog.md` BCI-1 entry; INST-1 parity. Pre-suite "run BCI-1 against its own repo" before the full suite (slice-027 self-violation gate).

## Deferred to slice 030B (follow-up — user-approved split, 2026-05-16)

NOT in 030A scope; recorded here as the explicit deferral so `/reflect` carries it forward as the next slice candidate:

- **Shippability-catalog decoupling (v2-B1 + meta-M-add-1)**: rows #5/#8/#12's cited test functions (incl. `test_legitimate_llm_fence_brief_still_triggers_bc_proj_2_and_global_1` AND `test_methodology_changelog.py::test_v_0_23_0_*`/`test_v_0_27_0_*` which hard-read untracked `~/.claude/`) still transitively read gitignored/untracked content. 030B must mechanically derive the COMPLETE cited-fn token set from `shippability.md` L13/L16/L20 (no category enumeration) and decouple every one.
- **Archive-backtest fidelity (meta-M1′)**: synthetic `_make_slice` briefs vs verbatim-tracked real archived corpus — a deliberate detection-fidelity decision deferred for proper TRI-1, not silently weakened.
- **Risk note**: 030A retires R-4's *substance* (silent BC-1 degradation cannot recur — BCI-1 catches drift loud at a non-opt-out gate + Step5b). 030A does NOT yet decouple the shippability *catalog rows* from gitignored drift; the residual false-PCA-1-HALT window is narrowed (drift caught loudly at next `/build-slice`/`/reflect` with a reconstruction runbook) but not eliminated until 030B. This is the accepted 030A/030B seam.

## Out of scope (030A)

- Changing `tools/build_checks_audit.py` `_parse_rules` / anchor / applicability **semantics**. BCI-1 is a *separate* tool calling `_parse_rules` read-only — an integrity check, not a semantics change.
- The shippability-row repoint + archive-backtest fidelity → **030B** (see Deferred).
- Fixing R-1 / R-2 / R-3.
- Un-gitignoring `build-checks.md` / `architecture/` (`.gitignore:11` stands; durability = tracked fixtures + tracked literal-constant oracle + BCI-1).
- "Fixing the `/reflect` Step 5b source defect" — no deterministic source exists (B2/ADR-029).

## Dependencies

- Failing repro (BFRD-1, pre-satisfied): `tests/methodology/test_build_checks_audit.py` — pre-existing, currently `17 failed, 21 passed` with signature `AssertionError: BC-PROJ-2 not parsed from architecture/build-checks.md` (only `BC-PROJ-3` parsed). Per R-4 + slice-029 aggregated lesson: "Failing repro `tests/methodology/test_build_checks_audit.py` already exists → BFRD-1 prelude pre-satisfied."
- Risk register: [[risk-register#R-4]]
- Prior slices: [[slice-005-add-bc-1-keyword-precision]], [[slice-008-refine-bc-1-anchors-with-negative-context]], [[slice-012-bc-proj-2-negative-anchor-migration]], [[slice-028-refactor-utf8-rollup-sentinel-version-agnostic]] (BC-PROJ-3/BC-GLOBAL-2 promotion), [[slice-029-make-diagnose-dispatch-sequential]] (R-4 discovery + deferral approval)
- Vault refs: `architecture/build-checks.md`, `~/.claude/build-checks.md`, `skills/reflect/SKILL.md` Step 5b (L159–L208), `architecture/shippability.md` rows #5/#8/#12, `tests/methodology/test_build_checks_audit.py`

## Mid-slice smoke gate

After authoring the canonical fixtures + the all-5-rule literal-constant pins + reconstructing both `build-checks.md` files, and BEFORE building the BCI-1 tool, run:
```
$PY -m pytest tests/methodology/test_build_checks_audit.py --no-header -q
```
Expected: `0 failed` (baseline `17 failed, 21 passed`). If any test still fails: STOP — the fixture/literal-constant authoring is incomplete; diagnose before building BCI-1.

**M2 anti-circularity cross-check** (a `0 failed` here is satisfiable by a structurally-wrong reconstruction if fixture + literal pin were authored from the same wrong source — `_rule_applies` L413-431 makes `always:true`/glob both land slice-005 in `skipped`, a coincidental pass). So ALSO assert, against a *different* recovery artifact than the one the fixture body was authored from: reconstructed `BC-GLOBAL-1.applies_to == ("**",)` cross-checked vs the slice-005 archive `build-log.md` verbatim before/after body (recovery input; the tracked oracle is the new test-file literal constant). If it does not equal `("**",)`: STOP — `applies_to` mis-reconstructed despite green tests.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] BFRD-1: repro test `tests/methodology/test_build_checks_audit.py` PASSES (AC-2)
