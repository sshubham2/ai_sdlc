# Build log: Slice 093 add-external-vault-support

**Date**: 2026-05-31
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-31 build: plan approved (PCA-1 gate). Pre-build hygiene done: rev-2 critique committed (0a71942), master e738c09 (slice-092 merge) merged into slice/093 (d5cb1b6, conflict-free; R-33 sync).
- 2026-05-31 build: prerequisites green — branch slice/093, CRP-1 clean, TF-1 harmonized. Stage→build.
- 2026-05-31 BUILD: tools/_vault_paths.py (3-tier resolution) + tools/_vault_write.py (C2 safe_write/append + sidecar lock + EPERM retry) written. Phase-1 tests: 22 PASS / 2 expected-fail (INSTALL.md + R-32 pending T7/T8). C2 primitive green: concurrent writers/appenders + mocked-EPERM + reader-parity.
- 2026-05-31 BUILD: T7 INSTALL.md Step 3i (base-location prompt + ai-sdlc-vault-base write via _vault_write) + T8 risk-register R-32 (mitigating). Slice-093 tests 24/24 PASS.
- 2026-05-31 SMOKE: mid-slice + pre-finish full suite 1314 PASS / 0 FAIL (no-flip backward-compat proven; only existing-test change = count-pin 12→15). R-20 seed: diagnose-out/ cp -r'd into worktree (worktree-at-/slice skips the /build-slice seed — slice-088 gap, surfaced by dogfooding).
- 2026-05-31 BUILD: 12 deterministic audits PASS (TF-1 strict 12/12, WIRE-1, BRANCH, UTF8, CRP, PCA, BCI, MCFS, STP, AVFS, TVFS, NAW). DCE-1 clean. mock-budget clean.
- 2026-05-31 BUILD: BC-PROJ-3/BC-GLOBAL-2 (Critical) ADDRESSED — this slice performs NO destructive `git checkout`/`restore`/`stash` revert of uncommitted work (the `git merge master` R-33 sync was on a clean tree, not a revert; tests use tmp_path/monkeypatch only). BC-PROJ-4 (no audit parse-rule/classifier change; all gates run on the REAL slice at prereq+pre-finish, not fixtures). BC-PROJ-5 (no identifier rename / frozen carve-out; VAULT_ROOT allowlist verified unchanged at 10 via dynamic actual-importer computation, not a hand-count). BC-PROJ-11 (INSTALL.md Step 3i adds NO methodology-version literal — verified by grep).

## Summary

### Plan executed
- **T1** `test_vault_safe_write.py` (5) — DONE/PASS · **T2** `test_install_vault_config.py` (2) — DONE/PASS · **T3** `test_external_vault_adr_and_risk.py` (2) — DONE/PASS · **T4** `test_vault_root_constant.py` +3 resolution tests + count-pin 12→15 — DONE/PASS
- **T5** `tools/_vault_paths.py` 3-tier resolution (env → git-common-dir config → `architecture/` default; stdlib leaf; defensive R-7; observability INFO/WARN) — DONE
- **T6** `tools/_vault_write.py` (`safe_write_text` sidecar-lock+atomic+EPERM-retry; `safe_append_text` O_APPEND; `write/read_vault_root_config`; shared `_CONFIG_REL` SSoT) — DONE
- **T7** `INSTALL.md` Step 3i (base-location prompt + `ai-sdlc-vault-base` write via `_vault_write`) — DONE · **T8** `risk-register.md` R-32 (mitigating) — DONE

### Mid-slice smoke gate
**Result**: PASS — full suite **1314 passed** (no-flip backward-compat: resolved default unchanged at `architecture/`; only existing-test change = count-pin 12→15). `diagnose-out/` seeded (R-20 worktree-at-/slice gap).

### Pre-finish gate
- [x] All 5 ACs PASS — TF-1 strict 12/12 PASSING (`/validate-slice` records per-AC evidence)
- [x] Must-not-defer addressed — backward-compat (default `architecture/`); C2 implemented+tested; fail-visible resolution (WARN on malformed config); consumer-freeze preserved (test green); observability (INFO on env/config override + WARN on malformed)
- [x] Drift-check pass (DCE-1 clean; drift-log full-mode `**Trigger**: slice-093` entry)
- [x] Smoke regression check pass (full suite 1314)
- [x] No debug code (TODO/FIXME/pdb scan clean)
- [x] 16 Step-6 audits PASS: TF-1, WIRE-1, BRANCH, UTF8, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, DCE-1, BC-1 (strict/BCSG-1 acked), mock-budget
- [x] Built in a real BRANCH-2 worktree (NOT `WORKTREE=skip`) — created early at `/slice` (dogfooded the worktree-at-/slice initiative)

### Deferrals (recorded at TRI-1 / out-of-scope)
- **m-add-1** (DEFERRED): pre-existing stale `8-element` comments at `test_vault_root_constant.py:41,281` (frozenset is 10; test passes dynamically) — re-sync at slice-094.
- **M4 residual**: stale `_ERROR_MESSAGE_STRING_EXCLUSIONS` tuples (5 pinned vs 7 real marker sites) — out-of-scope (093 migrates nothing; orphan test matches by substring) — re-sync at slice-094.

### Design deviations
- `diagnose-out/` post-hoc `cp -r` seed (R-20): the worktree was created at `/slice` (dogfooding the worktree-at-/slice initiative), which skips `/build-slice`'s seed step. A worktree-setup artifact, NOT a code change. **Evidence for the broader initiative**: worktree-at-/slice must own the R-20 seed (carry to slice-094+).
- No `design.md` deviations — code matches design rev-2.

### Files changed
- `tools/_vault_paths.py` (resolution extension) · `tools/_vault_write.py` (NEW) · `INSTALL.md` (Step 3i) · `architecture/risk-register.md` (R-32)
- `tests/methodology/test_vault_root_constant.py` (+3, count-pin) · `test_vault_safe_write.py` (NEW) · `test_install_vault_config.py` (NEW) · `test_external_vault_adr_and_risk.py` (NEW)
- slice artifacts: mission-brief/design/ADR-085/critique/critique-review/milestone/build-log/drift-log

### Code-review follow-up (CRSI-1 — advisory v1)
- code-Critic **FINDINGS 0B/1M/3m**. Empirically VERIFIED the lock is load-bearing (pure O_APPEND loses 26/30 lines without it; concurrent os.replace EPERMs).
- **M1** (Major, my observability edit): `print(…, file=sys.stderr)` crashes the 10 consumers at import with `UnicodeEncodeError` on a non-ASCII vault path under cp1252 stderr — the repo's own documented footgun. **ACCEPTED-FIXED**: leaf-safe `_stderr` helper (UTF-8 bytes to `sys.stderr.buffer`, `errors="replace"`; ascii-fold fallback) replaces all 4 print sites.
- **m1** (Minor): `_read_common_dir_config`'s `subprocess.run(encoding="utf-8")` → uncaught `UnicodeDecodeError` in the reader thread on non-UTF-8 git output (the R-30 / slice-091 class). **ACCEPTED-FIXED**: bytes-capture + explicit main-thread decode with `UnicodeDecodeError` caught + WARN.
- **m2** (Minor): `safe_append_text` lacked the EPERM-retry `safe_write_text` has. **ACCEPTED-FIXED**: bounded EPERM-retry on `os.open`.
- **m3** (Minor, forward-looking): `.lock` sidecars accumulate in the vault at the 094 flip — out-of-scope for 093 (verified none land now). **DEFERRED to slice-094**.
- +2 regression tests (`test_vault_paths_import_survives_cp1252_stderr_with_non_ascii_path`, `test_append_retries_on_mocked_eperm`). Full suite **1316 PASS**; leaf/utf8/TF-1 green. code-review.md written.
