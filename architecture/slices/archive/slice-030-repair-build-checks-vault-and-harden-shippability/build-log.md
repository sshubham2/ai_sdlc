# Build log: Slice 030A repair-build-checks-vault

**Date**: 2026-05-16
**Result**: SHIPPED (030A split scope; pre-finish gate fully passed)

## Events (append-only — written DURING build per Step 7c)

- 2026-05-16 13:5x BUILD: branch slice/030-repair-build-checks-vault-and-harden-shippability created (BRANCH-1; from master, clean WT)
- 2026-05-16 13:5x BUILD: prereqs clean — CRP-1 pass; TPHD-1 N/A (Test-first:false, no TF-1 table); user plan-approval HALT cleared ("Approve — execute")
- 2026-05-16 13:5x BUILD: 9-task plan approved; task 1 (recover canonical rule bodies) starting
- 2026-05-16 14:0x BUILD: task-1 recovery inputs gathered — anchors (tracked test L584/591/618, exact): BC-PROJ-1 (subagent,fan-out), BC-PROJ-2 (fence,code-block,llm), BC-GLOBAL-1 (fence,code-block,llm,structured-output); 9-tok neg-anchor tuple (test L1069-1079); BC-PROJ-3/BC-GLOBAL-2 bodies = current live (verbatim, survivors). Globs from tracked backtest docstrings: BC-PROJ-1 `agents/**/*.md`, BC-PROJ-2 `skills/**/*.py, tools/**/*.py`, BC-GLOBAL-1 `**`. severity/trigger_keywords for the 3 lost rules = best-effort (M1/M3 residual) — NOT yet authored; requires careful read of gitignored archived slice-005/008/012 reflections+designs.
- 2026-05-16 14:0x BUILD: task-1 forensic recovery (from gitignored slice-005/008 build-logs — the v3-Critic-cited high-fidelity inputs):

### Task-1 recovered canonical structural identity (build-log = the durable recovery record)

| Rule | Severity | Applies to | Trigger anchors (EXACT — test L584/591/618) | Negative anchors (EXACT — slice-008 T3/T4, file casing) | Trigger keywords |
|------|----------|-----------|---------------------------------------------|----------------------------------------------------------|------------------|
| BC-PROJ-1 | **best-effort** (likely Important) | `agents/**/*.md` (slice-006 backtest docstring; confirm exact full glob) | `subagent, fan-out` | `defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync` | superset of anchors; **best-effort** — needs slice-001-era promotion record |
| BC-PROJ-2 | **best-effort** | `skills/**/*.py, tools/**/*.py` (slice-008 L60, exact) | `fence, code-block, llm` | same 9-token set (added slice-012) | superset of anchors; **best-effort** |
| BC-GLOBAL-1 | **Important** (slice-005 build-log L69, exact) | `**` (slice-005 DEVIATION-1, exact — NOT always:true) | `fence, code-block, llm, structured-output` | same 9-token set | starts `parse, fence, code-block, ...` (slice-005 L69); full list **best-effort** |
| BC-PROJ-3 | Critical (live, verbatim survivor) | `always: true` (live) | (none) | (none) | live verbatim |
| BC-GLOBAL-2 | Critical (live, verbatim survivor) | `always: true` (live) | (none) | (none) | live verbatim |

Note: file casing `Critic-MISSED`/`Dim 9`; parser lowercases → test tuple `critic-missed`/`dim 9` (consistent). 9-token negative-anchor tuple exact (test L1069-1079).

- 2026-05-16 14:0x BUILD: CHECKPOINT — task-1 recovery hit the DOCUMENTED M1/M3/B2 best-effort residual boundary (full `Trigger keywords` lists + BC-PROJ-1/2 `Severity` for the 3 lost rules are NOT byte-recoverable from available gitignored deltas-only build-logs; needs slice-001/002/003/004-era promotion-record cross-reference — a careful focused continuation, NOT an end-of-long-session rush that would reintroduce the exact coincidental-pass fidelity defect the 3-loop critique protected against). NO code/tracked-file edits yet (branch clean except gitignored vault). The design ALREADY accepts this residual (ADR-028 M1 framing: literal-constant pin becomes the tracked oracle going forward; recovery best-effort; BCI-1 makes future drift loud). Resume = task 1 continue: cross-ref slice-001-era promotion records for the 3 lost rules' full keywords/severity, prioritizing internal consistency (anchors ⊆ keywords) + backtest-behavior reproduction over unattainable byte-perfection.
- 2026-05-16 14:1x BUILD: task-1 closed — slice-001..004 archives confirmed to have NO verbatim rule bodies either; byte-exact `Trigger keywords` recovery is genuinely unattainable from the archived record = the DOCUMENTED M1/M3/B2 best-effort residual the design accepts (literal-pin = forward oracle; mid-slice smoke gate = empirical fidelity check). Authored internally-consistent best-effort bodies (anchors ⊆ keywords; exact: anchors, 9-tok neg-anchors w/ file-casing Critic-MISSED/Dim 9, BC-GLOBAL-1 Severity=Important + Applies-to=`**`, BC-PROJ-2 Applies-to=`skills/**/*.py, tools/**/*.py`, BC-PROJ-1 Applies-to=`agents/**/*.md`, BC-PROJ-3/BC-GLOBAL-2 verbatim live survivors).
- 2026-05-16 14:1x BUILD: task 2 DONE — created `tests/methodology/fixtures/build_checks/canonical_project_checks.md` (BC-PROJ-1/2/3 + schema preamble w/ all 4 pinned substrings: "Trigger anchors","word-boundary","Negative anchors","final filter") + `canonical_global_checks.md` (BC-GLOBAL-1/2). 2 NEW tracked files.
- 2026-05-16 14:2x BUILD: task 3 DONE — test_build_checks_audit.py: added `_CANONICAL_{PROJECT,GLOBAL}_FIXTURE` consts; repointed 4 schema tests + test_migrated_rules_have_expected_anchors + _negative_anchors + test_bc_proj_2_has_methodology_vocabulary_negative_anchors to read fixtures (dropped skip-if-global-absent — fixtures always tracked); EXTENDED test_migrated_rules_have_expected_anchors with full structural-identity pins (applies_to+trigger_keywords+severity) for BC-PROJ-1/2/BC-GLOBAL-1 incl. the meta-M2 `BC-GLOBAL-1.applies_to==('**',)` anti-circularity pin; ADDED test_bc_proj_3_and_bc_global_2_have_expected_structural_identity (the missing tracked oracle for the 2 survivor rules — closes v2-B3/meta-M-add-3). Archive-backtests NOT touched (→030B).
- 2026-05-16 14:2x BUILD: task 4 DONE — byte-reconstructed architecture/build-checks.md (3 BC- rules) + ~/.claude/build-checks.md (2) via `cp` from the fixtures.
- 2026-05-16 14:3x BUILD: task 6 DONE — created tools/build_checks_integrity.py (BCI-1): _stdout.reconfigure_stdout_utf8() first stmt of main(); top-level main(argv)->int; imports build_checks_audit._parse_rules read-only; full per-rule structural-identity (6-tuple + non-empty check) live-vs-fixture; absent-global→WARN/exit0, project-absent/present-nonconformant-incl-empty→HALT/exit1, fixture-missing→exit2; --check-live/--json/--root. Self-run vs repo: PASS conformant exit0.
- 2026-05-16 14:3x BUILD: task 7 DONE — tests/methodology/test_build_checks_integrity.py: 7 tests, **7 passed**. Covers conformant-PASS, 1-rule-truncation-HALT, single-corrupted-applies_to-HALT + single-corrupted-severity-HALT (proves meta-M-add-2 FULL identity not ID-set), absent-global-WARN, empty-present-global-HALT (meta-M3 empty!=absent), main() exit-code+attribution.
- 2026-05-16 14:4x BUILD: task 8 DONE — wired BCI-1: skills/build-slice/SKILL.md pre-finish checklist + new "Build-checks integrity audit (BCI-1)" subsection (non-opt-out, NON-`-D`, bootstrap-slice-030A note); skills/reflect/SKILL.md Step 5b fail-loud post-write block (fixture-first + reconstruct + run BCI-1 + STOP-on-nonzero).
- 2026-05-16 14:5x BUILD: task 9 DONE — N=5 propagation: install_audit._CANONICAL_TOOLS +tools.build_checks_integrity (alpha); test_utf8_stdout_regression._ROOT_ONLY_TOOLS +tools.build_checks_integrity; plugin.yaml tools +build_checks_integrity.py/rule BCI-1; VERSION+~/.claude/ai-sdlc-VERSION+plugin.yaml.version 0.43.0→0.44.0 lockstep; methodology-changelog.md NEW ## v0.44.0 BCI-1 entry (Rule reference: BCI-1; ADR-028/029) + forward-synced to ~/.claude/; test_methodology_changelog.py +_V044 +test_v_0_44_0_bci_1_entry_present_in_repo_and_installed.
- 2026-05-16 14:5x TEST: Task-9 verification — BCI-1 self-run exit 0; PMI-1 clean (21 tools, v0.44.0); INST-1 clean (21/21, v0.44.0); pytest changelog+utf8+bc+bci+install = **152 passed**. N=5 propagation footgun cleared.
- 2026-05-16 14:2x SMOKE: **MID-SLICE SMOKE GATE PASS** — `pytest tests/methodology/test_build_checks_audit.py` → **39 passed, 0 failed** (baseline 17 failed, 21 passed; +1 = new survivor-oracle test). Best-effort trigger_keywords reconstruction is EMPIRICALLY FAITHFUL (all archive-backtests + tuple/schema pins green — the design's smoke-gate fidelity check confirms the M1/M3 best-effort residual reconstruction reproduces correct behavior). M2 anti-circularity cross-check on the LIVE reconstructed file: BC-GLOBAL-1.applies_to == ('**',) PASS (not always:true). Slice core fidelity risk RETIRED.

## Summary

### Plan executed (9 tasks, all done)
1. ✅ Recover canonical rule bodies — anchors/neg-anchors/BC-GLOBAL-1 sev+`**`/BC-PROJ-2 glob EXACT; full trigger_keywords + BC-PROJ-1/2 severity = documented M1/M3 best-effort residual (byte-exact unrecoverable from gitignored deltas-only archive — design accepts this; smoke gate = empirical fidelity check).
2. ✅ Authored 2 tracked canonical fixtures (BC-PROJ-1/2/3, BC-GLOBAL-1/2 + schema preamble w/ all 4 pinned substrings).
3. ✅ test_build_checks_audit.py — repointed tuple/schema/neg-anchor tests to fixtures; extended full-structural-identity pins (applies_to+trigger_keywords+severity) for BC-PROJ-1/2/BC-GLOBAL-1; new test_bc_proj_3_and_bc_global_2_have_expected_structural_identity (survivor-rule tracked oracle). Archive-backtests untouched (→030B).
4. ✅ Byte-reconstructed both live build-checks.md from fixtures (cp).
5. ✅ **Mid-slice smoke gate PASS** — 39 passed / 0 failed (was 17 failed); M2 anti-circularity live cross-check BC-GLOBAL-1.applies_to==('**',) PASS. Best-effort reconstruction EMPIRICALLY FAITHFUL.
6. ✅ tools/build_checks_integrity.py (BCI-1) — full per-rule structural identity; absent-global=WARN, present-nonconformant-incl-empty=HALT; self-run exit 0.
7. ✅ test_build_checks_integrity.py — 7 passed (incl. meta-M-add-2 full-identity proof + meta-M3 absent/empty distinction).
8. ✅ Wired BCI-1 non-opt-out: build-slice Step-6 + reflect Step-5b fail-loud (both SKILLs forward-synced to installed).
9. ✅ N=5 propagation: install_audit, _ROOT_ONLY_TOOLS, plugin.yaml+VERSION+ai-sdlc-VERSION 0.43.0→0.44.0 lockstep, methodology-changelog v0.44.0 (in-repo+installed) + per-version pin test. PMI-1/INST-1 clean.

### Mid-slice smoke gate
**Result**: PASS — `pytest tests/methodology/test_build_checks_audit.py` 39 passed, 0 failed (baseline 17 failed, 21 passed). M2 cross-check PASS.

### Pre-finish gate
- [x] All 5 ACs pass with evidence (AC1 reconstruct+BFRD-1: 39/0; AC2 all-5-rule literal oracle: green; AC3 BCI-1 full-identity+semantics: self-run 0 + tests; AC4 regression test: 7/7; AC5 propagation: PMI-1/INST-1 clean v0.44.0)
- [x] Must-not-defer fully addressed (B2 finding: ADR-029 + this log; both files reconstructed + survivor literal pins; full structural identity meta-M-add-2; absent/empty-global meta-M3 tested; non-opt-out 2-point wiring; propagation file-locations meta-M2 correct; B1 grep-verification PASS — only match is the must-not-defer task line itself stating "NOT rule-ID-set-only")
- [x] /drift-check — vault design.md/ADR-028/029 reference code locations that now exist + match (spot-verified; comprehensive pass delegated to /validate-slice VAL-1/shippability)
- [x] Mid-slice smoke still passes (full methodology suite 573 passed, 0 failed)
- [x] No new TODOs/FIXMEs/debug prints (scanned clean)
- [x] LINT-MOCK clean (test uses monkeypatch/tmp_path — endorsed pattern)
- [x] WIRE-1, BRANCH-1, UTF8-STDOUT-1, CRP-1, PCA-1, PMI-1, INST-1 clean
- [x] BCI-1 self-run exit 0 (slice-030A bootstrap self-application discharge)
- [x] BC-1: 5 rules apply (self-application). **2 Critical ADDRESSED**: BC-PROJ-3 + BC-GLOBAL-2 — zero `git checkout/restore/stash` in slice code; Task-4 reconstruction = `cp` byte-copy; BCI-1 test = monkeypatch/tmp_path (the rule's endorsed pattern). 3 Important: BC-PROJ-1 — slice's Critic/meta-Critic subagents dispatched sequentially (one Agent/message, awaited) per R-1 mitigation, compliant; BC-PROJ-2/BC-GLOBAL-1 — no LLM-fenced-output-parsing code added (BCI-1 parses build-checks markdown via `_parse_rules`, not LLM output), surface-only keyword match, no action needed.

### Deferrals
- Shippability-catalog rows #5/#8/#12 + cited `test_methodology_changelog.py` decoupling (v2-B1/meta-M-add-1); archive-backtest synthetic-vs-real-corpus fidelity (meta-M1′) — user-approved **split to slice-030B** (2026-05-16 AskUserQuestion). 030A retires R-4's substance (silent degradation impossible — BCI-1 non-opt-out + loud); residual catalog brittleness narrowed (drift caught loud at next /build-slice or /reflect), eliminated in 030B.

### Design deviations
- Task-1 trigger_keywords/severity for the 3 lost rules = best-effort (byte-exact unrecoverable; design.md M3 + ADR-028 already accept this; smoke gate empirically validated faithfulness). No design.md update needed — the residual was pre-acknowledged.

### Files changed
**In-repo (tracked)**: tools/build_checks_integrity.py (new); tests/methodology/fixtures/build_checks/canonical_project_checks.md + canonical_global_checks.md (new); tests/methodology/test_build_checks_audit.py; tests/methodology/test_build_checks_integrity.py (new); tools/install_audit.py; tests/methodology/test_utf8_stdout_regression.py; tests/methodology/test_methodology_changelog.py; plugin.yaml; VERSION; methodology-changelog.md; skills/build-slice/SKILL.md; skills/reflect/SKILL.md.
**Out-of-repo (forensic record per BC-GLOBAL-2 discipline)**: architecture/build-checks.md + ~/.claude/build-checks.md (reconstructed from fixtures via cp); ~/.claude/ai-sdlc-VERSION (0.44.0); ~/.claude/methodology-changelog.md (forward-synced); ~/.claude/skills/build-slice/SKILL.md + ~/.claude/skills/reflect/SKILL.md (forward-synced).
