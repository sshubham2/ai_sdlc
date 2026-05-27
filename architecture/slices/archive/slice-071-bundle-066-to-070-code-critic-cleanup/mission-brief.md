# Slice 071: bundle-066-to-070-code-critic-cleanup

**Mode**: Standard
**Estimated work**: 1-2 days (LARGE+; 31-finding bundled cleanup at 10× slice-065 reference-precedent scale — slice-065's 3-finding cleanup was 30-45 min, linear extrapolation puts this at 5-7.5 hours raw FIX work + phase overhead + 8-9 new regression-pin-test functions + ~5 modifications of existing tests + 2 forward syncs + 14 audits + slice's own /code-review. User-ratified full-bundle scope at `/slice` 2026-05-26 over the recommended split-options A/B/C; **mid-slice smoke gate is the structural pressure-valve** — if first-half (slice-066/067/068 + 12 findings) slips materially, fall back to in-build scope-split per /critique M4 ACCEPTED-FIXED. Slice-070 reflection L108 split-slice nomination preserved as fallback)
**Risk retired**: NONE (technical-debt cleanup; not risk-driven)
**Test-first**: false (mixed-disposition cleanup slice; ACs map to disposition-discharge, not to single-test-per-AC shape)
**Walking-skeleton**: false
**Exploratory-charter**: false

**Closes:** SC-028

## Intent

Burn down the ~30-finding code-Critic advisory backlog accumulated under **CRSI-1 v1 walking-skeleton** across slices 066-070. Voluntary-restraint discipline (N=11 cumulative) deferred each slice's code-Critic findings to a future bundled slice; slice-070 reflection L108 explicitly declared the backlog has crossed the explicit-scope-decision threshold ("30 advisory findings across 5 slices is past the slice-069-projected explicit /slice scope decision threshold"). This slice discharges every finding via explicit per-finding disposition (FIXED / DEFERRED-AGAIN with rationale / OBSOLETE), closes SC-028 (slice-068 test_vault_root_constant.py hardening bundle), and resets the post-CRSI-1 backlog to ~0. Voluntary-restraint discipline extends to **N=12 cumulative** on this slice's MEPD-1 EXCLUDE posture (no methodology-changelog entry, no PMI-1 bump, no new ADR — ships at v0.70.0 unchanged per slice-065 / slice-067 / slice-070 cleanup-slice precedent).

## Acceptance criteria

1. All **6 slice-066 code-Critic findings** discharged (M1 `_is_repo_root_a_worktree` shallow-gitdir walk-off + M2 `wt_base` `$(pwd)`-vs-`.git`-ancestor divergence + m1 asymmetric `AuditResult` surface + m2 `test_honours_canonical_worktree_skip_rationale_line` not-load-bearing + m3 inline `import os` per call + m4 SKILL.md PowerShell-portability parenthetical) with explicit FIXED / DEFERRED-AGAIN / OBSOLETE disposition in `build-log.md` Events § per-finding.
2. All **6 slice-067 + slice-068 code-Critic findings** discharged: slice-067 m1 `main()` DRY duplication + slice-068 SC-028 bundle (M1 missing `test_vault_paths_module_is_leaf` + m1 idempotency regex under-coverage + m2 freeze-pin assertion gap + m3 two-marker convention regex coverage gap) + slice-068 m4 PEP-8 blank line cosmetic.
3. All **8 slice-069 code-Critic findings** discharged (M1 `_SECRET_PATTERNS` count `9` vs actual `10` across methodology-changelog v0.70.0 + ADR-066 + mission-brief AC4 + m1-m6: vault file-count drift 631/633/634 + PII-redaction count divergence 93/113/141 + methodology-changelog v0.70.0 600-word blob + `.gitignore` comment seam + build-log `--detach HEAD` uncodified + M5 INCLUDE BC-1 false-positive surface).
4. All **11 slice-070 code-Critic findings on `tools/slice_queue_writer.py`** discharged (M1 worktree-absolute-path silent-corruption + M2 `_is_path_shaped`-vs-AC#3-regex contract drift + M3 PRIMARY id-lookup unfiltered + M4 `lru_cache` shared-mutable foot-gun + M5 `` `unknown` `` cell breaks AC#3 + M6 `subprocess.run` patch scope + m1 `cache_clear` never called + m2 `--from` fallback untested + m3 build-log honesty (already FIXED at slice-070 /reflect — re-confirm OBSOLETE here) + m4 eager id-map build + m5 forward-compat tuple as magic constant).
5. Full pytest **≥ 950 PASS** (slice-070 baseline) + shippability runner **≥ 70/70 PASS** + 14 Step-6 audits all clean + slice's own `/code-review` surfaces **0 new structural Majors** (cosmetic minor advisories permitted under continuing CRSI-1 v1 walking-skeleton posture).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | slice-066 6 findings discharged | `grep -cE "^\\| slice-066 (M1\|M2\|m1\|m2\|m3\|m4) " architecture/slices/slice-071-bundle-066-to-070-code-critic-cleanup/build-log.md` = 6 |
| 2 | slice-067 1 + slice-068 5 findings discharged | `grep -cE "^\\| slice-067 m1 \|^\\| slice-068 (M1\|m1\|m2\|m3\|m4) " build-log.md` = 6 |
| 3 | slice-069 8 findings discharged | `grep -cE "^\\| slice-069 (M1\|M2\|m1\|m2\|m3\|m4\|m5\|m6) " build-log.md` = 8 |
| 4 | slice-070 11 findings discharged | `grep -cE "^\\| slice-070 (M1\|M2\|M3\|M4\|M5\|M6\|m1\|m2\|m3\|m4\|m5) " build-log.md` = 11 |
| 5 | Full test/audit/shippability + /code-review structural-clean | `$PY -m pytest tests/ -q` → exit 0; `$PY -m tools.shippability_runner architecture/shippability.md` → exit 0 + ≥70 PASS; 14 Step-6 audits all exit 0; `/code-review` invocation surfaces 0 new structural M / B findings |

Note for AC#3: slice-069 inventory per `architecture/slices/archive/slice-069-track-vault-in-git/code-review.md` is M1 + **M2** + m1-m6 = **8 distinct findings**. M2 is a Major covering BOTH the missing paired-pin tests AND the missing `architecture/shippability.md` row #69. Slice-069 /reflect Step 5.3 partial-discharged ONLY the shippability row; the paired-pin tests are STILL outstanding (this slice's design.md §Components touched → `tests/methodology/test_methodology_changelog.py` adds them as `test_v_0_70_0_adr_066_*`). AC#3's "8 findings" + "= 8" verification regex + design.md disposition table (8 rows) are now all consistent (per /critique M1 ACCEPTED-FIXED).

## Must-not-defer

- [ ] **Every one of the ~31 findings** gets an explicit per-finding disposition row in `build-log.md` Events (no silent skips; no aggregated "all minors deferred" lines) — precise hand-count yields 31; mission-brief Intent's "~30" is the early estimate, design.md disposition table has the exact 31 rows (per /critique-review m-add-2 ACCEPTED-FIXED)
- [ ] **FIXED findings** ship with a regression-pin test where structurally possible (not test-first per slice posture, but coverage-after is mandatory for any structural finding)
- [ ] **DEFERRED-AGAIN findings** ship with (a) written rationale, (b) explicit "lands-in-slice-NNN+" nomination, and (c) note in reflection.md §Deferred (no quiet re-deferral)
- [ ] **No new code-Critic structural findings** introduced by this slice's own edits (slice's own `/code-review` must show 0 new M/B; cosmetic minors permitted)
- [ ] **MEPD-1 EXCLUDE posture verified**: NO new `## v0.71.0` `methodology-changelog.md` entry minted; NO `plugin.yaml`/`VERSION`/`pyproject.toml` bump; NO new ADR (cleanup-only voluntary-restraint discipline N=12 cumulative). **Permitted under this posture**: retroactive in-place TEXT corrections to the existing `## v0.70.0` entry per the SUP-1 §Append-only-of-DECISIONS-not-of-FACTS interpretation (slice-069 M1/m1/m2/m3 dispositions in design.md ride this carve-out — the underlying decisions in v0.70.0 are unchanged; only count-facts and prose density are corrected); paired MCFS-1 forward-sync to `~/.claude/methodology-changelog.md` is required and counts as in-band for this slice (per /critique B2 ACCEPTED-FIXED)
- [ ] **Authorization-touching skill surfaces** (`skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md` from slice-066 m4 + slice-068 m3 surfaces) → OSDG-1 forward-sync to `~/.claude/skills/<name>/SKILL.md` MUST be paired with each in-repo edit per CAD-1 / OSDG-1 lineage discipline

## Out of scope

- New methodology rules or ADR mints (cleanup-only; no rule axis additions)
- VERSION bump (MEPD-1 EXCLUDE posture; ships at v0.70.0 unchanged)
- Wide refactors beyond the enumerated 31 findings (no opportunistic cleanup; if a new finding surfaces during build, defer to slice-072+ unless it strictly blocks an in-scope fix; count corrected from "30" to "31" per /critique-review m-add-2 ACCEPTED-FIXED — exact hand-count is 31)
- WS-1 / ETC-1 TFFL-1 R-7-class extension (standing `/critic-calibrate` proposal target from slice-066 reflection L97-L98; carried-forward; lands in a dedicated future slice)
- PSQ-2 (claim state machine) / PSQ-3 (rebase + conflict discipline) — slice-072+ nominees
- `rename-architecture-to-sdlc` — slice-072+ user-intent nominee
- SC-006 / SC-007 / SC-008 documented-but-unenforced-gate cluster (HIGH severity backlog items; slice-072+ nominee `implement-or-downgrade-drift-check`)
- Architecture changes (no new audit, no new skill, no new tool, no new contract)
- AC count ≤ 5 rule: this slice has exactly 5 ACs (AC#1-AC#5); per-slice deviation rationale is N/A

## Dependencies

- Prior slices (the 5 source slices whose code-Critic findings this slice discharges):
  - [[slice-066-add-worktree-per-slice-discipline]] — 6 findings on `tools/branch_workflow_audit.py` + `skills/build-slice/SKILL.md` + `skills/commit-slice/SKILL.md`
  - [[slice-067-add-parallel-slice-queue-output]] — 1 finding on `tools/slice_queue_writer.py` `main()`
  - [[slice-068-add-vault-root-constant]] — 5 findings (4 in SC-028 bundle on `tests/methodology/test_vault_root_constant.py` + 1 cosmetic on `tools/supersede_audit.py`)
  - [[slice-069-track-vault-in-git]] — 8 findings on `methodology-changelog.md` + `ADR-066` + `mission-brief` + `.gitignore` + build-log narrative seams
  - [[slice-070-fix-psq-1-blast-radius-dict-leak]] — 11 findings on `tools/slice_queue_writer.py` (single-file concentration; most structurally important)
- Vault refs:
  - [[diagnose-out/backlog.md#SC-028]] — slice-068 test_vault_root_constant.py hardening bundle (the one BCR-1 closure via `**Closes:** SC-028` sentinel above)
  - [[architecture/methodology-changelog.md]] — voluntary-restraint precedent lineage (N=11 → N=12 cumulative on this slice)
  - [[architecture/principles.md]] — CRSI-1 v1 walking-skeleton advisory-only posture
  - [[architecture/decisions/ADR-066-track-vault-in-git.md]] — slice-069 M1 count-drift target (`_SECRET_PATTERNS` 9-vs-10)
- Risk register: none retired (cleanup is not risk-band gating)
- Backlog round-trip: closes SC-028 only; SC-027 already closed at slice-070; other SC items remain open and out of scope

## Mid-slice smoke gate

At ~50% of build (after slice-066 + slice-067 + slice-068 disposition rows land in `build-log.md` AND any FIXED fixes for those 12 findings are applied to source; BEFORE tackling slice-069 + slice-070 inventory):

```bash
$PY=$USERPROFILE/.claude/.venv/Scripts/python.exe
$PY -m pytest tests/ -q && $PY -m tools.shippability_runner architecture/shippability.md
```

Expected: full pytest baseline **≥ 950 PASS** (slice-070 baseline was 950); shippability runner **≥ 70/70 PASS**; both exit 0. If fails: **STOP** — a first-half fix likely introduced a regression. Diagnose root cause before continuing into second half (slice-069 + slice-070 inventory). Do NOT mask a regression by deferring the offending finding silently — surface the regression class in build-log.md Events § and reflection.md §Discovered, then re-defer the originating finding with `regression-induced-rollback` rationale.

## Pre-finish gate

- [ ] All **5 acceptance criteria** PASS with evidence cited in `validation.md`
- [ ] **Must-not-defer list** fully addressed (each box checked with build-log.md citation)
- [ ] `/drift-check` passes (vault claims still match code reality after the bulk edits)
- [ ] **Mid-slice smoke still passes** in the second half (no regression introduced by slice-069/070 dispositions)
- [ ] **No new TODOs / FIXMEs / debug prints** introduced (VAL-1 catches at /validate-slice but pre-check here)
- [ ] **All 14 Step-6 audits clean** — CAD-1, PMI-1, INST-1, BC-1, RR-1, DR-1, TF-1, WS-1, WIRE-1, ETC-1, CSP-1, SUP-1, LINT-MOCK-1/2/3
- [ ] **Slice's own `/code-review`** surfaces **0 new structural M/B findings** (cosmetic minors are permitted per CRSI-1 v1 walking-skeleton posture; if any structural item emerges, treat as in-band fix obligation under "no new code-Critic findings introduced" must-not-defer)
- [ ] **BCR-1 round-trip**: `**Closes:** SC-028` sentinel in this mission-brief.md triggers `- **Addressed:** slice-071-bundle-066-to-070-code-critic-cleanup on YYYY-MM-DD` line append to `diagnose-out/backlog.md` SC-028 block (between Evidence sub-list and next SC header) at `/reflect` Step 5
- [ ] **MEPD-1 EXCLUDE posture verified**: zero edits to `plugin.yaml`, `VERSION`, `pyproject.toml`, `~/.claude/ai-sdlc-VERSION`; zero new ADRs under `architecture/decisions/`; zero NEW `## v0.71.0` entries added to `methodology-changelog.md` (retroactive in-place TEXT corrections to existing `## v0.70.0` entry are permitted per the must-not-defer #5 carve-out + design.md slice-069 M1/m1/m2/m3 dispositions; MCFS-1 forward-sync to `~/.claude/methodology-changelog.md` mirrors those in-place edits)
