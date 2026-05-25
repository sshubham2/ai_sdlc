# Slice 029: make-diagnose-dispatch-sequential

**Mode**: Standard
**Estimated work**: 0.5 day (~3–4h)
**Risk mitigated (not retired)**: R-1 (Cwd-mismatch / parallel-spawn permission cascade-failure tool denial for spawned subagents in `/diagnose` — medium×HIGH, highest-scored open risk). Sequential-by-default dispatch is fix-candidate #3's "one Agent call at a time defeats the parallel-spawn cascade-failure mode" ([claude-code #57037](https://github.com/anthropics/claude-code/issues/57037)). **Mitigating, not retired** (per /critique M1): sequential default defeats only the parallel-spawn hypothesis; R-1's independent cwd-mismatch hypothesis stays open and the `--parallel` opt-in path retains full exposure by explicit caller choice.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`/diagnose` Step 5 currently fans out all 10 analysis passes as multiple `Agent` tool calls in a single message (parallel batch). The user reports this triggers the parallel-spawn permission cascade-failure (R-1 / claude-code #57037): subagents lose Read/Grep/Bash access, producing a degraded `diagnosis.html`. This slice makes **sequential dispatch the default** (one `Agent` call per message, processed one at a time) and adds an opt-in **`--parallel`** argument that restores the prior single-message multi-Agent-call batch for environments that tolerate it. The post-subagent pipeline (`write_pass.py`, 3-attempt cap, Step 5.5 verification) is unchanged — only the dispatch sequencing changes.

## Acceptance criteria

1. By default, `/diagnose` SKILL.md Step 5 instructs the orchestrator to dispatch the 10 analysis passes **one `Agent` call per message, sequentially** (each pass returns + is written via `write_pass.py` before the next is spawned); the prior all-in-one-message parallel batch is no longer the default path.
2. Invoking `/diagnose --parallel` restores the prior single-message multi-`Agent`-call batch behavior; the flag is documented in `argument-hint` (frontmatter) + parsed in Step 1 + branched on in Step 5. Unknown/garbled args fail safe to the sequential default (no mid-run error-out).
3. Sequential mode preserves every existing post-subagent invariant: per-pass `write_pass.py` flow, ≤3-attempt re-spawn cap, `.failed.raw` degraded-pass handling, Step 6 (04-ai-bloat) + Step 6.5 (narrator) ordering. The Step-5/5.5 dispatch-coupled sentences are rewritten **dispatch-mode-aware** (an enumerated, auditable edit set per design.md "What's new" — not "byte-unchanged"); the Step 5.5 silent-gap invariant holds for BOTH sub-cases: a pass *failing* the 3-attempt cap → `.failed.raw` + loop continues; the loop *not reaching* all 10 (interrupted) → unspawned passes are *missing* and re-spawned before Step 6, never silently skipped.
4. Prose-pin coverage updated (`tests/skills/diagnose/test_skill_md_pins.py`): asserts (a) default-sequential prose present, (b) `--parallel` opt-in prose present + documented in `argument-hint`, (c) flag-strip-before-TARGET fail-safe prose present, (d) Step-5.5 dispatch-mode-aware + early-exit clause present. Existing CSP-1 byte-equality + slice-019 LAYER-EVID-1 N=6 + `test_diagnose_skill_drift.py` mini-CAD tests are NOT modified and MUST keep passing unchanged (they are the rewrite's regression guard).
5. `architecture/risk-register.md` R-1 status updated **→ `mitigating`** (not `retired` — per /critique M1) with a structured RR-1 `Mitigation:` field citing this slice + ADR-027 and stating residual exposure; `architecture/shippability.md` gains a propagation row whose Command cell is the real runnable file-selector `... -m pytest tests/skills/diagnose/test_skill_md_pins.py --no-header -q` (per /critique m1 + /critique-review M-add-4, no `-k`); **`methodology-changelog.md` gains a `### Changed` v0.43.0 entry (NO rule-ID) citing ADR-027 + slice-029, with the atomic PMI-1 lockstep `VERSION`/`~/.claude/ai-sdlc-VERSION`/`plugin.yaml.version` 0.42.0→0.43.0 + `test_methodology_changelog.py` v0.43.0 entry-pin** (TRI-1-ratified M2 option B).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Sequential default | Read SKILL.md Step 5: default path describes one-Agent-call-per-message loop; `pytest tests/skills/diagnose/test_skill_md_pins.py` green for the new sequential-default pin |
| 2 | `--parallel` opt-in | `argument-hint` lists `--parallel`; Step 1 strips it before TARGET resolution via the 3-arm `case` (`--parallel`→flag / `--*`→warn+ignore / else→path); B3 snippet dry-run under Git-Bash recorded in build-log.md (per /critique-review M-add-1). **`/diagnose --parallel` (no path)** → TARGET=`$PWD`, runs the `--parallel` batch, NEVER the `:41` abort. **`/diagnose --paralll` (typo, no path)** → unknown-flag warned+ignored, TARGET=`$PWD`, sequential, **no abort** (TRI-1-ratified option B). Only a *non-flag-shaped* genuinely-bad path arg reaches the pre-existing **`:41` `cd`-fails abort** unchanged (corrected from the prior `:25` mislabel per /critique-review M-add-1). |
| 3 | Dispatch-coupled rewrite is auditable | The Step-5/5.5 edits match the enumerated dispatch-coupled-prose inventory in design.md "What's new" (heading, batch-paragraph split, `:170` order clause, `:187` barrier, Step 5.5 opening + early-exit) — no un-enumerated post-subagent-flow edits; `pytest tests/skills/diagnose/` fully green |
| 4 | Prose-pin + CSP-1 + LAYER-EVID-1 N=6 | `pytest tests/skills/diagnose/test_skill_md_pins.py tests/skills/diagnose/test_diagnose_skill_drift.py` green incl. `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` + `test_pass_templates_match_skill_md_step5_contract`; canonical contract line grep-identical across SKILL.md + `skills/diagnose/passes/*.md`; `textual import-evidence requirement` phrase present in-repo + installed SKILL.md |
| 5 | R-1 + shippability | `$PY -m tools.risk_register_audit architecture/risk-register.md --json` shows R-1 status changed with rationale; `grep` shippability.md for the new dispatch-default row |

## Must-not-defer

- [ ] Canonical subagent-contract byte-equality (CSP-1) preserved — the contract string MUST NOT drift in either the sequential or `--parallel` branch
- [ ] Step 5.5 silent-gap detection still functions in sequential mode (no pass silently omitted because the loop exited early)
- [ ] `--parallel` flag parsing fails safe — unrecognized/garbled argument → sequential default, never a mid-run abort
- [ ] R-1 status change is explicitly justified in the register (no silent retire); shippability propagation added per RPCD-1/SCPD-1
- [ ] Installed-copy sync: `~/.claude/skills/diagnose/SKILL.md` updated to stay byte-equal to in-repo copy (mini-CAD / `test_diagnose_skill_drift.py`)
- [ ] PMI-1 atomic lockstep: methodology-changelog v0.43.0 entry (no rule-ID) + `VERSION`/`~/.claude/ai-sdlc-VERSION`/`plugin.yaml.version` 0.42.0→0.43.0 + `test_methodology_changelog.py` entry-pin all land together; `tools.plugin_manifest_audit` + `test_methodology_changelog.py` accept a rule-ID-less `### Changed` entry (if not, surface as DEVIATION at smoke gate — do NOT mint an audited rule-ID)

## Out of scope

- Modifying the subagent contract itself or `write_pass.py` parse/normalize/validate logic
- Fixing upstream claude-code #57037 (external platform issue)
- R-2 runtime-warning instrumentation (separate deferred risk — not touched)
- Per-pass model routing (COST-1.1) — model assignment unchanged, only dispatch sequencing
- Step 6 / Step 6.5 dispatch (already single-agent; only renumbered references if any)

## Dependencies

- Prior slices: [[slice-001-diagnose-orchestration-fix]] (ADR-001 subagent contract — sequential reuses it unchanged), [[slice-002-fix-diagnose-contract-and-cwd-mismatch]] (precedent: R-1/R-2 surface handled as prose-pin-guarded orchestration slice, not `/repro`-routed)
- Vault refs: [[decisions/ADR-001]], [[risk-register#R-1]], [[shippability]]
- Risk register: [[risk-register#R-1]] (primary, **mitigated** — not retired — by this slice), [[risk-register#R-2]] (adjacent, untouched)
- slice-019 LAYER-EVID-1 N=6 pin: the `textual import-evidence requirement` cross-reference paragraph (SKILL.md:164–166) sits **inside Step 5** (the rewrite blast radius) — preserved verbatim + correctly positioned; `test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` is the regression guard (per /critique B2)
- BFRD-1 disposition: bug-class change but no deterministic in-repo failing test possible (upstream parallel-spawn platform behavior; same untestability R-2 documents). `/repro` not applicable — slice-002 precedent governs the `/repro`-route + rule-ID questions. NOTE (TRI-1 M2 ratification): the slice-002 *changelog-omission* is NOT followed — per the unconditional inclusion heuristic this slice DOES add a v0.43.0 changelog entry (rule-ID still omitted). Prose-pin tests are the established guard for `/diagnose` SKILL.md behavioral claims.

## Mid-slice smoke gate

At ~50% (after SKILL.md Step 1 flag-strip + Step 5 sequential default edited, before R-1/shippability propagation):
```
$PY -m pytest tests/skills/diagnose/test_skill_md_pins.py tests/skills/diagnose/test_diagnose_skill_drift.py -q
```
Expected: new sequential-default + `--parallel` + flag-strip + Step-5.5-dispatch-aware pins assert present; AND **all pre-existing pins still GREEN**, specifically `test_pass_templates_match_skill_md_step5_contract` (CSP-1 byte-equality), `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` (slice-019 LAYER-EVID-1 N=6 — the highest-risk casualty of a Step-5 restructure, per /critique B2), and `test_in_repo_and_installed_diagnose_skill_md_are_content_equal` (mini-CAD). If ANY of those three named guards fails: STOP — the Step-5 rewrite drifted a protected contract; do not continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
