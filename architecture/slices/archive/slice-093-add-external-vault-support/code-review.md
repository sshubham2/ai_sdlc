# Code Review: Slice 093 add-external-vault-support

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths) at worktree, base `e738c09`
**Date**: 2026-05-31
**Result**: FINDINGS (advisory in v1 — does NOT block /validate-slice)

## Summary

Well-built: the locking primitive is genuinely load-bearing (empirically: pure `O_APPEND` loses 26/30 lines on Windows without the lock; concurrent `os.replace` to one target EPERMs — so the tests have real teeth), the no-flip invariant holds, leaf-purity is preserved, all 24 slice tests + RR-1/SUP-1/PMI-1 pass, the `_CONFIG_REL` SSoT is genuinely shared. No Blockers. The defects the design stack structurally could not reach are line-level, in the **observability print path** and the **git-subprocess decode path** — both the repo's own documented Windows-encoding footgun classes (cp1252 stderr; non-UTF-8 git output / R-30).

## Changed files (in-scope)
- tools/_vault_paths.py, tools/_vault_write.py
- tests/methodology/{test_vault_safe_write, test_install_vault_config, test_external_vault_adr_and_risk, test_vault_root_constant}.py
- INSTALL.md, build-log.md, spike docs (informational)

## Findings

### Blockers
None. No code path is broken-or-unsafe-as-shipped: no-flip default holds, `safe_write_text`/`safe_append_text` do not corrupt/lose data under contention (empirically verified), the lock is released on every path (timeout, EPERM-exhaustion), ADR-085 extends ADR-065 (`supersedes: null`). The findings below are robustness, not corruption.

### Majors

#### M1: observability `print(…, file=sys.stderr)` crashes the 10 consumers at import with `UnicodeEncodeError` on non-ASCII vault paths (cp1252 stderr)
- **Claim under review**: `tools/_vault_paths.py:117-127` (INFO prints) + `:90-101` (WARN prints). The must-not-defer "Observability: log which vault root was resolved and why" is delivered by these bare `print()` calls, run at module import (`_resolve_vault_root()` at module level).
- **Issue**: when the resolved/config path contains a non-ASCII character AND `sys.stderr` is a raw cp1252 stream (Windows default for redirected stderr / pipes / subprocess children that have NOT reconfigured), `print()` raises `UnicodeEncodeError` and the import fails. The 10 `_MIGRATION_SITE_ALLOWLIST` consumers import `_vault_paths` directly without reconfiguring stderr; only the test harness reconfigures, masking it. The repo's own CLAUDE.md documents this exact footgun. (RSAD-1: the slice does not survive its own repo's discipline.)
- **Evidence**: reproduced — cp1252-wrapped `sys.stderr` + `AI_SDLC_VAULT_ROOT=/tmp/vault-中文` → `importlib.reload(tools._vault_paths)` raised `UnicodeEncodeError`. Realistic trigger: a Windows user `C:\Users\Müller` choosing the default `~/.aisdlc` base. (Latent in 093 — the default path is silent; fires only when env/config is set, i.e. post-flip or env-set.)
- **Proposed fix**: leaf-safe encoding-defensive stderr write (`sys.stderr.buffer.write((msg+"\n").encode("utf-8","replace"))` guarded by `hasattr`, plain-`print` fallback) OR try/except `UnicodeEncodeError`. Add a regression test importing `_vault_paths` under cp1252-wrapped stderr + non-ASCII env.
- **Builder disposition**: ACCEPTED-FIXED (see code-review follow-up).

### Minors

#### m1: `_read_common_dir_config` git-subprocess decode (`encoding="utf-8"`) can `UnicodeDecodeError` in the reader thread on non-UTF-8 git output — not caught by `except (OSError, SubprocessError)` (the R-30/slice-091 class)
- **Evidence**: `tools/_vault_paths.py:70-78`; reproduced — a subprocess emitting `b"\xff\xfe…"` under `encoding="utf-8"` raised `UnicodeDecodeError` in the reader thread with `cp.stdout=None`, NOT caught (`issubclass(UnicodeDecodeError, OSError)` is False). The config-file read at `:89` *does* catch it — asymmetry confirms the gap. Outcome: ugly thread traceback + mis-classified as "no config" (defeats R-7 fail-visible).
- **Proposed fix**: bytes-capture (`text=False`) + explicit main-thread `.decode("utf-8")` inside the try with `UnicodeDecodeError` caught + WARN (the slice-091 R-30 hardening pattern). **Builder disposition**: ACCEPTED-FIXED.

#### m2: `safe_append_text` has no EPERM-retry — asymmetric with `safe_write_text` and with R-32's own framing (append-log class named as EPERM-vulnerable)
- **Evidence**: `tools/_vault_write.py:122-135` (`os.open` no retry) vs `:106-119` (`os.replace` 6-attempt backoff). On Windows `os.open` against a held file (aggressive AV/OneDrive mid-scan, no `FILE_SHARE_WRITE`) can raise `PermissionError` → propagates immediately. Robustness gap, not corruption.
- **Proposed fix**: wrap the `os.open` in the same bounded EPERM-retry (or factor a shared `_retry_eperm`). Add a mocked-EPERM-on-`os.open` test. **Builder disposition**: ACCEPTED-FIXED.

#### m3 (forward-looking, latent in 093): persistent `.lock` sidecars accumulate beside vault files at the 094 flip; audit broad-glob vault consumers before then
- **Evidence**: `tools/_vault_write.py:50` — sidecar `.lock` never unlinked (correct, to avoid delete-race). In 093 purely latent (`safe_write_text` only test-exercised in `tmp_path`; INSTALL writes to `~/.claude/`; verified `git ls-files architecture/**/*.lock` empty). At 094, real vault writers gain permanent siblings (`_index.md.lock`, …). `supersede_audit` filters `is_dir()` (safe); others (`parallel_conflict_resolver:894`, `slice_queue_writer`, `stranded_slice_audit`) should be checked at 094.
- **Proposed fix**: NO change in 093 (out of scope). slice-094 design: lock sidecars in a dedicated `.aisdlc-locks/` dir OR confirm every vault-scanning glob filters `*.md`/`is_dir()` + pin. **Builder disposition**: DEFERRED to slice-094.

## Dimensions checked
- [x] Unfounded assumptions — m1 (docstring claims defensive git-failure coverage; misses `UnicodeDecodeError`). No phantom imports; `_CONFIG_REL` SSoT genuinely shared.
- [x] Missing edge cases — M1 (non-ASCII path at import), m1 (non-UTF-8 git output), m2 (EPERM on append). Concurrency genuinely covered (lock verified load-bearing).
- [x] Over-engineering — none. `write/read_vault_root_config` test-exercised + 094 caller declared in wiring matrix; no dead code/params/imports.
- [x] Under-engineering — none. Each AC → passing test (24); no-flip + observability must-not-defers delivered (M1 makes observability fragile — a defect in delivered code, not absence).
- [x] Contract gaps — none blocking. All `_vault_write` publics annotated+docstringed; typed `PermissionError` names path+remediation. m2 notes writer/appender resilience asymmetry. Lock mutual-exclusion verified across handles.
- [x] Security — none. No authn/authz/network/secrets/injection (`subprocess.run` fixed argv, no `shell=True`). Paths user-owned; config in repo's `.git/`.
- [x] Drift from vault — none. Code matches design.md rev-2 + ADR-085 (3-tier resolution, sidecar-lock-never-target, O_APPEND append, INSTALL base-only, allowlist 10, `supersedes: null`). MEPD-1 EXCLUDE matches no-VERSION-bump impl.
- [x] Web-known issues — none contradicting. `os.replace` Windows-EPERM-on-held-handle + retry-with-sleep is the documented workaround (bugs.python.org #46003, beeware/briefcase #1780, conan #6560) — exactly `safe_write_text`'s impl. `msvcrt.locking`/`LK_NBLCK` current, non-deprecated.
- [x] Cross-cutting conformance — RSAD-1: M1 is a self-application failure (own cp1252-stderr discipline violated); m1 is the R-30/slice-091 class. APED-1: no audit parse-rule modified → no battery obligation. New precedence composes correctly with ADR-065 consumer-freeze cascade (`test_consumer_constants_are_frozen_at_first_import` green).
