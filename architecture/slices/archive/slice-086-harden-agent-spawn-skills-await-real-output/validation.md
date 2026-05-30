# Validation: Slice 086 harden-agent-spawn-skills-await-real-output

**Date**: 2026-05-30
**Result**: PASS

The "real environment" for this methodology-prose slice is the live repo + the installed `~/.claude/skills/` mirrors + the pytest suite. Each AC is validated by executing the actual check against those surfaces (not the test suite as a proxy).

## Per-criterion results

### AC1: All three spawn-skills carry the await-the-real-agent guard at the spawn→write (Step 2 → Step 3) seam
- **Status**: PASS
- **Evidence**: heading literal `**Await the real agent — never fabricate its output.**` (U+2014) present exactly once in each worktree skill:
  ```
  skills/critique/SKILL.md         : heading_count=1
  skills/critique-review/SKILL.md  : heading_count=1
  skills/code-review/SKILL.md      : heading_count=1
  ```
  APED-1 (build-time): heading file_count=1 AND seam_count=1 per skill (present once, and within the Step 2→Step 3 region); body literal `NEVER self-author a placeholder` seam_count=1 per skill.
- **Notes**: guard sits immediately before each `### Step 3` heading (verified by code-Critic offsets). The `code-review` SKILL.md guard is visible in the running pipeline — this very `/code-review` + `/validate-slice` invocation read it.

### AC2: New structural-pin test asserts the guard present in all three; WRITTEN-FAILING before edits, PASSING after
- **Status**: PASS
- **Evidence**: `tests/methodology/test_r25_await_real_agent_guard.py` — pre-edit run was 6 seam cases FAILED + relocate-fixture PASS (genuine WRITTEN-FAILING); post-edit `pytest` → **9 passed** (6 parametrized seam presence + relocate-rejection + line-anchor regression + Step-20-prefix-rejection). The test is SEAM-SCOPED (M-add-1): the code-Critic's mutation battery confirmed it FAILS on delete / relocate-out-of-seam / gut-body / em-dash→hyphen, PASSES unmutated.
- **Notes**: m1 (code-review) fixed in-slice — region extractor is line-anchored (`(?m)^### Step N\b`), not bare substring.

### AC3: Installed copies updated; existing OSDG-1 drift test stays green
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_code_review_skill_drift.py` → **1 passed** (in-repo worktree == installed, content-equal modulo EOL). Installed copies carry the guard:
  ```
  ~/.claude/skills/critique/SKILL.md         : heading_count=1
  ~/.claude/skills/critique-review/SKILL.md  : heading_count=1
  ~/.claude/skills/code-review/SKILL.md      : heading_count=1
  ```
- **Notes**: `critique` + `critique-review` have NO content-equality drift test (B1/B2, verified against disk) — the AC-2 pin test is their sole guard-literal enforcement; `code-review` is the only one of the three with a drift test, and it stays green.

### AC4: Global CLAUDE.md `# Spawned-agent output` stopgap removed as the CLOSING step
- **Status**: PASS
- **Evidence**: `Spawned-agent output` occurrences in `~/.claude/CLAUDE.md` = **0**. Removed only after AC-1/2/3 verified (ordering invariant per ADR-078 §Consequences; build-log event 00:08 confirms sequence).
- **Notes**: migration recorded in build-log.md + drift-log.md; full reflection-record at /reflect.

### AC5: Shippability row pinning the new structural-pin test
- **Status**: PASS
- **Evidence**: row 92 references `tests/methodology/test_r25_await_real_agent_guard.py` (count=1, no changelog node per MEPD-1 EXCLUDE / m1). `shippability_path_audit` → CLEAN (test path + cited fns exist).

## Layered safety checks (VAL-1)
- **Layer A (credential scan)**: 0 secrets.
- **Layer B (dependency hallucination)**: 0 import findings (`re`, `pytest`, `tests.methodology.conftest` all resolve; `--imports-allowlist tests`).
- **Result**: clean — both layers passed.

## Opt-in audits
- **WS-1 (walking-skeleton)**: N/A — `Walking-skeleton: false`.
- **ETC-1 (exploratory-charter)**: N/A — `Exploratory-charter: false`.
- **TF-1 (test-first)**: N/A — `Test-first: false`.

## Multi-instance validation
**Required?**: no
**Result**: not-applicable
**Evidence**: this slice changes methodology prose + a content-presence test; no multi-user / multi-device / multi-account runtime surface.

## Shippability catalog (regression check)
- **Pre-gates**: SCMD-1 clean (91 rows; incidental=0); PTFCD-1(b) clean (432 test-path tokens, all exist).
- **Runner**: `shippability_runner architecture/shippability.md` → **91 row(s), 91 PASS, 0 FAIL**. No past slice's critical path regressed; row 92's own test (the R-25 guard) passes within the catalog.

## Reality surprises
- None. The slice behaved exactly as designed. The one code-review Minor (m1, region-extractor substring fragility) was a latent future-robustness gap, fixed in-slice — not a reality surprise.

## Discovered (carry to /reflect)
- Follow-up `reconcile-osdg-1-inventory-claude-md-L42` (B2): CLAUDE.md:42 names `critique`/`diagnose` with `*_skill_drift.py` that don't exist on disk, and omits `code-review`/`pulse` that do. Pre-existing bidirectional OSDG-1 inventory drift; out of scope here.
- R-25 register flip to **retired** is a /reflect action (consistent with slice-077/082/084/085 pattern).
