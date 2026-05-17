# Slice 002: fix-diagnose-contract-and-cwd-mismatch

**Mode**: Standard
**Risk tier**: low
**Critic required**: false (no mandatory triggers — no auth/contracts/data-model/multi-device/external-integration/security)
**Estimated work**: 0.5 day (~2-3 hours)
**Risk retired**: R1 (cwd-mismatch tool denial) via the cheapest fix path — documented constraint + at-spawn warning. Closes the design correction noted in archived slice-001's design.md (contract over-reach in SKILL.md + 11 pass templates).
**Test-first**: true
<!-- prose-pin tests are a clean test-first path for SKILL.md / pass-template edits -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Resolve the two carryover items from slice-001: (1) the contract over-reach in `SKILL.md` Step 5 + 11 pass-template "Output format" sections (currently forbids Bash/python despite each template's Method section requiring Bash for graphify queries); (2) R1 cwd-mismatch tool denial via the cheapest fix path — explicit cwd-must-match documentation in SKILL.md Step 1 plus a runtime warning when explicit-path TARGET differs from the parent's cwd. Bonus cleanup: convert `architecture/risk-register.md` to the RR-1 audit's expected schema so `tools.risk_register_audit` picks up R1 correctly.

## Acceptance criteria

1. `skills/diagnose/SKILL.md` Step 1 documents the cwd-must-match-TARGET pattern with explicit user-facing prose ("if invoking with an explicit path that differs from `$PWD`, `cd` to TARGET first — subagents *may* lose tool access otherwise; slice-001 surfaced this when TARGET was outside `$PWD`, and the upstream root cause may be cwd-mismatch and/or a known parallel-spawn permission cascade-failure (claude-code #57037), so `cd $TARGET` is the cheapest mitigation but not guaranteed to fix every instance") AND the orchestrator emits a clear warning at Step 1 if TARGET resolves to a path outside `$PWD`, recommending the user re-invoke after `cd`'ing.
2. `skills/diagnose/SKILL.md` Step 5 + all 11 pass-template "Output format" sections (`skills/diagnose/passes/*.md`) AND `skills/diagnose/passes/01-intent.md` Hard rules contain the **byte-equal canonical contract string** (per triage M2 — pre-selected to lock wording across 12 sites): `**Do NOT call Write to produce output files (the orchestrator handles that). You MAY use Bash/python for graphify queries within $OUT/graphify-out/, and Read/Grep/Glob for source files within $TARGET.**` — present uniformly. The legacy string "Do NOT call Write, Bash, or python" must not appear anywhere in `skills/diagnose/`. The chosen wording must preserve the substring "Do NOT call Write" (case-insensitive) so existing test `test_skill_md_subagents_instructed_no_write` continues to pass (per triage M4).
3. `architecture/risk-register.md` conforms to the RR-1 audit's expected schema: `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` returns R1 in the output with zero parse violations. R1's content (description, fix candidates) is preserved across the format conversion.
<!--
  Note: prior drafts had AC #4 (prose-pin regression-guard meta-claim) and AC #5 (manual smoke deferred-explicitly). Collapsed during /build-slice Phase 6 because (a) AC #4 was circular — it asserted the test-first plan exists, which is what TF-1 enforces inherently for ACs 1-3; (b) AC #5 was deferred to /validate-slice with no programmatic test (logged as R-2 in risk-register.md). The deferred manual smoke moves to "Verification plan" below as an explicit deferred check rather than an AC. Per slice-002 critique M3.
-->


## Test-first plan

Per **TF-1**. Prose-pin tests + a small risk-register integration test are amenable; manual smoke (formerly AC #5, now a deferred verification check) is not unit-testable.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_step1_documents_cwd_constraint | PASSING |
| 1 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_step1_emits_cwd_mismatch_warning | PASSING |
| 2 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_step5_allows_bash_for_graphify | PASSING |
| 2 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_pass_templates_allow_bash_for_graphify | PASSING |
| 2 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_no_legacy_no_bash_no_python_phrase | PASSING |
| 2 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_pass_templates_match_skill_md_step5_contract | PASSING |
| 3 | integration | tests/methodology/test_risk_register_audit_real_file.py | test_project_risk_register_audit_clean | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|---|---|
| 1 | Step 1 cwd doc + warning | Read `SKILL.md` Step 1 prose to confirm the constraint is documented; the prose-pin tests assert specific phrases. AC #5 covers the runtime smoke. |
| 2 | Relaxed contract wording in Step 5 + 11 templates | Run prose-pin tests; manually grep `skills/diagnose/` for "Do NOT call Write, Bash, or python" → zero matches. |
| 3 | risk-register.md audit-clean | `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --top 5` returns ≥1 risk, zero violations. |
| (deferred) | /diagnose cwd-mismatch warning emits at runtime (formerly AC #5) | (deferred-explicitly to `/validate-slice`; **per triage M3, runtime emission is acknowledged-fragile**) — invoke `/diagnose <some-path-outside-PWD>` from this repo's cwd; observe warning in initial output; cancel before fanning out subagents. Logged as **R-2** in risk-register.md. |
| 1-3 + meta | Full test suite pass | `pytest tests/skills/diagnose/test_skill_md_pins.py tests/methodology/test_risk_register_audit_real_file.py -v` all pass; full `tests/` suite still 326+ tests passing. |

## Must-not-defer

- [ ] No "Do NOT call Write, Bash, or python" string remains anywhere under `skills/diagnose/` (verified by grep + the new negative prose-pin)
- [ ] R1's full content (description, three fix candidates, status) is preserved across the risk-register.md format conversion — not silently truncated by format mismatch
- [ ] Existing tests still 24/24 PASSING in `tests/skills/diagnose/` — no regression to slice-001's foundation
- [ ] `/drift-check` passes
- [ ] INSTALL.md re-run + `tools.install_audit --strict` clean — write_pass.py / SKILL.md changes propagate to `~/.claude/skills/diagnose/`

## Out of scope

- **Orchestrator pre-cd before spawning subagents** (option C from R1) — needs a `/risk-spike` to test whether subagent permissions inherit a `cd` from the parent. Defer.
- **Parent-thread pre-compute of all graphify queries** (option E from R1) — LARGE effort; would be its own slice if option-A documented-constraint proves insufficient in practice.
- **Full risk-register schema overhaul** beyond what the RR-1 audit needs — only convert what the audit demands.
- **Adding "environmental / runtime / cwd / permissions" dimension to the Critic prompt** — separate calibration concern; surface via `/critic-calibrate` instead.
- **Editing archived slice-001 design.md** — archived slices are append-only history; this slice's reflection.md will close the loop instead.

## Dependencies

- Prior slices: [[slice-001-diagnose-orchestration-fix]] — the orchestration foundation this slice tunes
- Risk register: [[risk-register#R1]]
- ADR refs: [[../decisions/ADR-001-diagnose-subagent-io-contract]] (unchanged; this slice doesn't supersede it)
- Build-checks: [[build-checks#BC-PROJ-1]] (subagents need embedded read-content) — this slice's changes preserve compliance

## Mid-slice smoke gate

After SKILL.md Step 5 + pass templates updated, before tackling risk-register format conversion:

```powershell
$py = "C:/Users/sshub/.claude/.venv/Scripts/python.exe"
# Prose pins should be green
& $py -m pytest tests/skills/diagnose/test_skill_md_pins.py -v
# Negative pin: legacy phrase should be absent
$txt = (Get-Content -Raw skills/diagnose/SKILL.md, skills/diagnose/passes/*.md) -join ""
if ($txt -match "Do NOT call Write, Bash, or python") { Write-Error "legacy phrase still present" } else { "negative pin OK" }
```

Expected: all prose pins pass; negative pin reports OK. If fails: STOP, the relaxation has gaps.

## Pre-finish gate

- [ ] All 4 testable ACs PASS with evidence in validation.md (AC #5 is /validate-slice manual)
- [ ] Test-first audit passes: `$PY -m tools.test_first_audit ... --strict-pre-finish`
- [ ] Must-not-defer list fully addressed
- [ ] No "Do NOT call Write, Bash, or python" anywhere in `skills/diagnose/`
- [ ] /drift-check passes
- [ ] INSTALL.md re-run; `tools.install_audit --strict` clean
- [ ] shippability.md entry #1 still passes (full diagnose test suite 24+ tests)
- [ ] Mid-slice smoke gate still passes (no regression)
