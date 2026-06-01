# Validation: Slice 095 harden-skill-driven-vault-writes

**Date**: 2026-06-01
**Result**: PASS

> Validated AFTER the code-review hardening round (M1/M2/M3 + m1/m3). All 5 ACs
> re-verified against the hardened+committed worktree (`b1ab6a3`). WS-1 / ETC-1 /
> TF-1 are all `false` in the mission brief → those audits no-op.

## Per-criterion results

### AC1: Skill-driven vault mutations route through the safe mechanism
- **Status**: PASS
- **Evidence**: `$PY -m tools.skill_vault_write_safety_audit` → `clean. 26 skill(s) scanned; 22 mutation site(s) (10 routed, 12 exempted)`, **exit 0**. The 10 append-class sites route through `` `vault_edit append` `` (codespan) or `<!-- route: … -->` markers; 12 RMW/project-open sites carry sanctioned `<!-- vault-write-safe: … -->` exemptions. No site bypasses `_vault_write`'s lock + atomic-replace.
- **Notes**: M1 hardening tightened "routed" to require the token inside a backtick code span or route marker (bare/negated mentions no longer false-CLEAN) — all 10 real routed sites still classify correctly.

### AC2: Fail-closed audit detects unsafe skill-driven vault writes
- **Status**: PASS
- **Evidence**: injected a raw write (`Append to \`architecture/risk-register.md\` raw`) into a temp `skills/fake/SKILL.md` → audit **exit 1**, naming `skills/fake/SKILL.md:1 [unrouted]`; removed it → real tree **exit 0**. An unclassifiable/negated route is a VIOLATION, never a silent pass (M1/M2 hardening: bare-token, negated-route, and unlisted-verb raw writes all now flag). Audit is wired into `/build-slice` Step-6 + `/validate-slice` Step 5.5c gate rosters + `architecture/shippability.md` (#102).
- **Notes**: APED-1 battery extended this round (+M1 negation/marker, +M2 expanded-verb, +m1 tilde/mixed/info-string fences, +M3 count-pin) — all in the green full suite.

### AC3: Concurrency proof — N concurrent skill-path writers lose zero data
- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_skill_vault_write_safety_concurrency.py` → **2 passed**. Non-vacuity established at build by mutation (the naive read-modify-write mutation control reliably loses 23/24 updates across 20 trials; revert → pass) — the lock is empirically load-bearing.
- **Notes**: untouched by this hardening round (the wrapper's `safe_append_text` lock path was not modified).

### AC4: R-32 skill-driven sub-class recorded closed-with-evidence
- **Status**: PASS
- **Evidence**: `$PY -m tools.risk_register_audit architecture/risk-register.md --json` → `R-32: mitigating | score 4 | band medium | rev cheap` (valid register, exit 0). `risk-register.md` records the skill-driven **append** sub-class CLOSED-with-evidence + the retire-on-BOTH-merged trigger (slice-094 Python-writer sub-class is parked at critique, NOT merged → R-32 correctly stays `mitigating`, NOT `retired`). The RMW residual + the new 12th exemption (triage:179) are documented.
- **Notes**: count reconciled 11→12 exempt this round (the m1 fence fix surfaced + exempted triage:179).

### AC5: No-flip safety contract preserved
- **Status**: PASS
- **Evidence**: `_resolve_vault_root()` with no env/config → `WindowsPath('architecture')`; `VAULT_ROOT == Path('architecture')` (`default-is-architecture: True`). Full suite **1367 pass / 0 fail** (was 1335 pre-hardening; +~30 new APED-1 tests). The hardening touched only slice-095's own deliverables (its 2 new tools, the SVW-routed SKILL.md prose, a triage exemption comment, count prose) — zero behavioral change to pre-095 skills/tools.

## VAL-1 layered safety checks (Step 5b)
- **Layer A (credentials)**: 0 secrets across 40 changed files.
- **Layer B (dep hallucination)**: 0 import findings (`--imports-allowlist tests`).
- **Result**: clean (exit 0).

## Walking-skeleton (WS-1) / Exploratory-charter (ETC-1)
- **Not applicable** — both `false` in mission-brief; audits no-op.

## Shippability catalog regression (Step 5.5)
- **Pre-gates**: SCMD-1 clean (101 rows / 1064 cited fns) · PTFCD-1 clean (101 rows / 448 path tokens) · SVW-1 exit 0.
- **Runner**: `$PY -m tools.shippability_runner architecture/shippability.md` → **101 row(s), 101 PASS, 0 FAIL** (exit 0). No past slice regressed.

## Multi-instance validation
- **Required?**: no — SVW-1 is a static prose audit + a single-process CLI; the concurrency dimension is covered by AC3's cross-subprocess proof, not a multi-device runtime.
- **Result**: not-applicable.

## Reality surprises
- The m1 CommonMark fence fix surfaced **triage:179** — a real project-open risk-register write the old naive ```` ``` ```` toggle was hiding behind triage's malformed nested fence. Resolved in-slice (exempt `project-open-single-shot`, allowlist-pinned), reversing a build-time reliance on the fence bug. **triage:163 remains fence-hidden** — the separate, still-deferred triage-markdown bug (a DISCOVERED finding for its own fix slice; not an SVW-1 gap).
