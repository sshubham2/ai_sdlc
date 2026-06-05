# Validation: Slice 114 convert-agent-prose-to-vault-seam

**Date**: 2026-06-05
**Result**: PASS

This is a methodology prose-conversion + audit-constant re-pin slice (no runtime app / device / user surface). "Real environment" = executing the real classifier/audits against the live converted corpus + running the real drift tests against the actual installed `~/.claude/agents/` copies — done below, not mocked.

## Per-criterion results

### AC1: the 2 convertible-bearing agents carry a self-sufficient ADR-105 resolver note; the 2 no-op files stay untouched
- **Status**: PASS
- **Evidence**: `grep -l 'ADR-105'` → `agents/code-review.md` + `agents/critic-calibrate.md` both carry the verbatim 3-line pilot seam note (`<vault>/` default + "subagent does NOT inherit CLAUDE.md" resolver line); confirmed via direct read (`has <vault>/ note: True | ADR-105: True` for both). `git status --porcelain` shows `critique-review.md` + `diagnose-narrator.md` NOT in the changed-file set (untouched).
- **Notes**: critique.md also untouched (CAD-1) — not in changed files.

### AC2: the 3 convertible reads → `<vault>/…`; surviving literals are deliberate carve-outs per design
- **Status**: PASS
- **Evidence**: `git diff` shows `code-review.md:44` critic-calibration-log + `:119` .secrets-allowlist + `critic-calibrate.md:22` critic-calibration-log all rewritten `architecture/…` → `<vault>/…`. Live `vault_flip_prose_inventory --json` post-edit: the 3 converted refs no longer appear; remaining agent occurrences = `code-review.md:29` (`architecture/**`, carve-out) + `:237` (active-folder, carve-out) + the doc-example notes + `critique-review.md:78` + `diagnose-narrator.md:19` (untouched class 5/7) + `critique.md` ×3 (pilot). 0 `<vault>/slices/slice-NNN` mis-buckets. (Code-Critic m1 also converted the `critic-calibrate.md:80` operational "read it" reference for self-sufficiency consistency — zero inventory impact.)

### AC3: `--strict` passes; rewrite-at-flip 127 / doc-example 4 / total 131
- **Status**: PASS
- **Evidence**: `$PY -m tools.vault_flip_prose_inventory --strict` → exit 0, "36 file(s), 131 literal(s) — 127 rewrite-at-flip, 0 historical-anchor, 4 doc-example, 0 needs-human." Re-run after the m1 fix: identical (131; 127/0/4/0), confirming the m1 `<vault>/` ref had zero count impact. `_BASELINE_SHA256` re-pinned to the live `44b2287682…` (computed via `audit_root` + `baseline_sha`, APED-1-derived). Converted-file ratchet: zero regressions (`code-review.md`'s 2 carve-outs hash-keyed in `_CONVERTED_CARVEOUTS`).

### AC4: both edited agents forward-synced + drift-guarded; `critique.md` untouched
- **Status**: PASS
- **Evidence**: `pytest test_code_review_agent_drift.py test_critic_calibrate_agent_drift.py` → 2 passed AFTER forward-sync (both RED before — FAIL→PASS non-vacuity proven, AP-5). The NEW `test_critic_calibrate_agent_drift.py` brings `critic-calibrate.md` under the CRSI-1/CAD-1 family (closing the M1 unguarded gap). `$PY -m tools.critique_agent_drift_audit --repo-root .` → clean (CAD-1, `critique.md` content-equal — untouched). CRLF check on both edited agents: 0 CRLF pairs (clean LF).

### AC5: R-32 records the agent-prose residual drained; physical move = sole pre-move residual
- **Status**: PASS
- **Evidence**: `risk_register_audit --json` → R-32 status `mitigating`, 0 violations. The appended slice-114 R-32 paragraph states "with the ENTIRE prose-rewrite leg now drained (CLAUDE.md slice-112 + 25 skills slice-113 + the 2 convertible agents slice-114), the SOLE residual to retirement is the physical move ONLY". CRLF preserved (630/0).

## Layered safety checks
- **VAL-1**: Layer A (credential scan) + Layer B (dep hallucination, `--imports-allowlist tests`) → exit 0 (no secrets, no hallucinated imports — the new test imports `tests.methodology.conftest` + `tests.skill_drift_equality`, both real).
- **WS-1 / ETC-1**: not applicable (no `Walking-skeleton` / `Exploratory-charter` field in mission-brief).

## Shippability catalog (regression check)
- **Pre-catalog gates**: SCMD-1 + PTFCD-1 + SVW-1 → all exit 0.
- **Catalog run**: `shippability_runner` → **119 rows, 119 PASS, 0 FAIL**. No past slice broken; the new slice-114 row 120 (inventory + 2 agent drift tests) runs green.

## Multi-instance validation
**Required?**: no (no multi-user / multi-device / multi-account surface — methodology prose + audit constants).
**Result**: not-applicable

## Reality surprises
- None. The build matched design exactly; the code-Critic's 2 minors were the only post-build deltas (m1 a self-sufficiency consistency fix, m2 a docstring confirm — both resolved/verified). The 127/4/131 arithmetic + carve-out hashes + baseline all reproduced as designed.
