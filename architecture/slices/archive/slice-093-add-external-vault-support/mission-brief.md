# Slice 093: add-external-vault-support

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (new — concurrent-write lost-update / atomic-rename-EPERM corruption on a shared mutable vault); de-risks the external-shared-vault initiative by activating the capability without flipping. Extends ADR-065 / `VAULT_ROOT` seam.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Make the AI-SDLC vault relocatable to a single shared external location (default `~/.aisdlc/<project>/`) so that, in a later slice, all concurrent slice worktrees can share ONE live vault view instead of each holding a copy that merge-conflicts. This slice ships the **activation machinery only** — the resolution-precedence chain, per-project keying, a concurrent-write-safe vault-write helper, install-time configuration, and completion of the partially-adopted `VAULT_ROOT` seam — while the **default stays `architecture/`** so this repo and every existing tool/test/skill behave identically (no flip). The live flip (SKILL-prose rewrite + physical move + history decision) is deferred to slice-094. Grounded in `architecture/spikes/spike-external-shared-vault.md` (verdict: CONDITIONAL — GO with constraints C1–C5).

## Acceptance criteria

1. `tools/_vault_paths.py` resolves the vault root via a documented precedence — env `AI_SDLC_VAULT_ROOT` → repo-local pointer/config deriving `~/.aisdlc/<project>/` from `git rev-parse --path-format=absolute --git-common-dir` (canonicalized; bounded-hash subdir, per C1) → default `architecture/` — and the unset/no-config default is UNCHANGED (`Path("architecture")`), so all existing tools/tests behave identically (backward-compatible; no flip).
2. A concurrent-write/append-safe vault helper exists (`tools/_vault_write.py`: `safe_write_text` = sidecar-lock + atomic `os.replace` + bounded EPERM-retry; `safe_append_text` = `O_APPEND`/`FILE_APPEND_DATA` + lock for append-only files like ADRs/risk-register/logs) and tests demonstrate it prevents lost-update / partial-write under concurrent whole-file writers AND concurrent appenders AND a (mocked) EPERM condition — the R-32 mitigation.
3. `INSTALL.md` (+ the install flow) prompts for the base vault location (default `~/.aisdlc`) and writes ONLY the GLOBAL base config `~/.claude/ai-sdlc-vault-base` (via `_vault_write.safe_write_text`) — the per-project `$GIT_COMMON_DIR/aisdlc/vault-root` write is slice-094 — WITHOUT moving any existing repo's `architecture/` (capability only).
4. The remaining `architecture/`-path-referencing `tools/*.py` are **classified** into a migration map (FS-path → migrate-at-flip / git-or-worktree-model-coupled → rethink-at-flip / pattern-data+prose → never-migrate), documented in `design.md` §Tool-migration classification map + [[ADR-085]]. **093 migrates NONE** (default stays `architecture/`, so unmigrated tools stay correct); `_MIGRATION_SITE_ALLOWLIST` is UNCHANGED (the 10 slice-068/071 consumers). A structural test asserts no-new-migration + the classification map's presence. (Reduced from "migrate ~6 tools" at /design-slice: the scan showed `parallel_conflict_resolver`/`stranded_slice_audit`/`pulse_worktree_resolver` are git/worktree-model-coupled — naive migration is wrong; they're rethought at the 094 flip.)
5. R-32 + constraints C1–C5 are registered in `risk-register.md` (append-only, in this slice's worktree), an ADR extends/refines ADR-065 for the external-vault resolution precedence + write-safety contract, and the full audit suite + `/validate-slice` are green.

## Test-first plan

(per **TF-1**) Each AC maps to failing tests written before implementation. `tools/test_first_audit.py --strict-pre-finish` must show all PASSING at finish.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_vault_root_constant.py | test_resolution_precedence_env_over_pointer_over_default | PASSING |
| 1 | subprocess | tests/methodology/test_vault_root_constant.py | test_git_common_dir_key_stable_across_main_and_worktree | PASSING |
| 1 | unit | tests/methodology/test_vault_root_constant.py | test_default_unchanged_when_no_env_no_pointer | PASSING |
| 2 | integration | tests/methodology/test_vault_safe_write.py | test_concurrent_writers_no_lost_update | PASSING |
| 2 | integration | tests/methodology/test_vault_safe_write.py | test_concurrent_appenders_no_lost_update | PASSING |
| 2 | integration | tests/methodology/test_vault_safe_write.py | test_write_retries_on_mocked_eperm | PASSING |
| 2 | integration | tests/methodology/test_vault_safe_write.py | test_write_raises_after_eperm_budget_exhausted | PASSING |
| 2 | unit | tests/methodology/test_vault_safe_write.py | test_inline_and_helper_config_readers_agree | PASSING |
| 3 | integration | tests/methodology/test_install_vault_config.py | test_install_writes_global_base_config_without_moving_vault | PASSING |
| 3 | structural | tests/methodology/test_install_vault_config.py | test_install_step_documented_in_install_md | PASSING |
| 4 | structural | tests/methodology/test_external_vault_adr_and_risk.py | test_no_new_tool_migration_and_classification_map_documented | PASSING |
| 5 | structural | tests/methodology/test_external_vault_adr_and_risk.py | test_r32_registered_and_adr_extends_065 | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Resolution precedence + unchanged default | `AI_SDLC_VAULT_ROOT` unset & no pointer → `VAULT_ROOT == Path("architecture")` (existing tests still green); env set → external; pointer present → `~/.aisdlc/<hash>` derived; `--path-format=absolute --git-common-dir` identical in a main+worktree fixture |
| 2 | Concurrent-write safety (R-32) | Spawn N writers on one target via the helper + simulate a held handle forcing rename-EPERM → assert no lost update / no truncation; lock serializes |
| 3 | Install capability, no flip | Run the install config function → per-project pointer/config written; assert `architecture/` bytes untouched |
| 4 | Seam completeness | Extended `test_vault_root_constant.py` green; no orphan `architecture/` filesystem literals outside the two-marker exclusions |
| 5 | Bookkeeping + green | `risk_register_audit` shows R-32; ADR file exists with `supersedes`/extends ADR-065; `/validate-slice` VAL-1 + all gate audits green |

## Must-not-defer

- [ ] **Backward-compat invariant**: default MUST stay `architecture/`; every existing tool/test/skill behaves identically (no silent flip). This is the slice's safety contract.
- [ ] **C2 concurrent-write safety implemented + tested** (not deferred) — R-32 is the scariest spike finding; do not ship the resolution chain without the safe-write helper.
- [ ] **Fail-visible resolution** (R-7 class): malformed pointer / unresolvable git-common-dir / missing external dir → clear signal + fall back to `architecture/`, never silently mis-resolve.
- [ ] **Preserve (or ADR-document) the consumer-freeze / read-at-import semantic** from ADR-065.
- [ ] **Observability**: log which vault root was resolved and why (env / pointer / default).

## Out of scope

- Flipping THIS repo to the external vault (default stays `architecture/`) — slice-094.
- Rewriting `skills/*/SKILL.md` prose to resolve the vault root — slice-094 (the coherence constraint: tools + prose must flip atomically).
- Physically moving `architecture/` + `diagnose-out/` + `graphify-out/` to `~/.aisdlc/<project>/` — slice-094.
- The C5 history/auditability decision (own-repo vs sync-back vs no-history) — resolved at slice-094 `/design-slice`.
- The broad "every tracked-file-writing skill uses a worktree" rule + worktree-creation-at-`/slice` — later slices in this initiative (the original `/slice` argument).

## Dependencies

- Prior slices: [[slice-068-add-vault-root-constant]] ([[ADR-065]], `_vault_paths.py` seam — this slice extends it); slice-071 (seam-adoption fixes / two-marker convention).
- Vault refs: [[decisions/ADR-065]]; `architecture/spikes/spike-external-shared-vault.md`; `architecture/spikes/spike-external-shared-vault/field-recon.md` — **REQUIRED READING for `/critique`** per the spike's authoritative-contradiction gate (concurrent-write hazard is sourced from official-repo issues).
- Risk register: R-32 (new, registered this slice) + constraints C1–C5.
- Parallel: slice-092 (`fix-stranded-audit-branchless-blindspot`) in flight at build stage — **CODE-LEVEL OVERLAP, not a clean disjoint radius**: it edits `tools/stranded_slice_audit.py` (+ `skills/pulse/SKILL.md`, `skills/slice/SKILL.md`), and THIS slice's `VAULT_ROOT` migration set also includes `tools/stranded_slice_audit.py` and `tools/pulse_worktree_resolver.py`. Mitigation: either EXCLUDE `stranded_slice_audit.py` (and `pulse_worktree_resolver.py`) from this slice's migration until slice-092 merges, OR sequence this slice's `/build-slice` AFTER slice-092's `--merge` (092 is near-done). Re-run the stranded-slice consult at build setup to check 092's merge state; do NOT assume a conflict-free merge on that file.
- `diagnose-out/backlog.md`: not present / not the candidate source (candidate is user-intent + spike-derived) → BCR-1 no-op.

## Mid-slice smoke gate

At ~50% (resolution chain + safe-write/append helper in, default unchanged):
```
& $PY -m pytest tests/methodology/test_vault_root_constant.py tests/methodology/test_vault_safe_write.py -q
& $PY -m pytest -q   # full suite — backward-compat proof
```
Expected: the RESOLUTION path is unchanged (default still `architecture/`) + new concurrency/append tests green. NOTE: `test_full_pytest_baseline_preserved`'s count-pin legitimately moves 12→15 (AC1 adds 3 functions) — that is the ONE sanctioned existing-test change, NOT a resolution-behavior change. Any OTHER existing test changing behavior → STOP, diagnose.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Built in a real BRANCH-2 worktree (NOT `WORKTREE=skip`)
