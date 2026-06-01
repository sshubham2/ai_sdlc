# Code Review: Slice 097 harden-skill-driven-vault-rewrites

**code-Critic reviewed**: slice diff vs default branch `f50d8ec` (working-tree uncommitted, filtered to in-scope paths)
**Date**: 2026-06-01
**Result**: FINDINGS (2 Blockers, 2 Majors, 2 Minors — all VALIDATED; Builder fixing in-slice)

## Summary

The core mechanism — `safe_rewrite_text` CAS, EOL-normalized compare + EOL-preserving write, the op-class-aware audit with bare-token severance, and the non-vacuous spawn-barrier concurrency proof — is correct and well-tested (full suite 1434 PASS; audit clean 12→3). But the **end-to-end skill protocol as written is broken on the project's default shell (PowerShell)**: the documented `vault_edit read --file X > base.bin` capture corrupts bytes under PowerShell (`>` = `Out-File` → UTF-16LE+BOM), and the concurrency test captured the base in-process so the shell-redirection path was never exercised. Two secondary defects: the `reflect:56` reword dropped the site out of audit detection (hyphen-compound verb), and `/archive` reuses one `base.bin` for two distinct targets. All findings empirically verified by the code-Critic.

## Changed files (in-scope)
- `tools/_vault_write.py`, `tools/vault_edit.py`, `tools/skill_vault_write_safety_audit.py`
- `tests/methodology/test_vault_safe_write.py`, `test_vault_edit_cli.py`, `test_skill_vault_write_safety_audit.py`, `test_skill_vault_rewrite_concurrency.py` (new)
- `skills/reflect/SKILL.md`, `skills/archive/SKILL.md`, `skills/supersede-slice/SKILL.md`
- `architecture/slices/.../build-log.md`

## Findings

### Blockers (advisory in v1)

#### B1: documented base-capture `vault_edit read ... > base.bin` corrupts bytes under PowerShell → guaranteed CAS livelock
- **Claim under review**: `skills/reflect/SKILL.md:56`,`:321`, `skills/supersede-slice/SKILL.md:103`, `skills/archive/SKILL.md:63` instruct `$PY -m tools.vault_edit read --file <X> > base.bin` then `rewrite --base-file base.bin`. The point of `read` + binary `--base-file` (M2) is a **byte-exact** CAS base.
- **Issue**: PowerShell (the project's default shell per both CLAUDE.md) aliases `>` to `Out-File`, which re-encodes stdout as **UTF-16LE + BOM** — not raw bytes. So `base.bin` never EOL-normalized-matches the UTF-8/CRLF on-disk target → `StaleVaultBaseError` every attempt → bounded retry exhausts → fail-STOP on every `/reflect`/`/archive`/`/supersede-slice`. Unusable on the very files R-32 exists for.
- **Evidence**: Empirical — `read --file idx.md > base.bin` in `powershell -NoProfile`: 27-byte CRLF+UTF-8 source → 60-byte capture, byte-match False, first bytes `255,254,...` (UTF-16LE BOM). The `read` code (`_cmd_read`, `sys.stdout.buffer.write`) is byte-correct via raw subprocess; the corruption is injected by the shell `>`. MS Learn `about_Character_Encoding`; FiloSottile/age#290.
- **Test gap**: `test_skill_vault_rewrite_concurrency.py:68-73` captures base via in-process `target.read_bytes()` — never invokes `vault_edit read`, never uses shell redirection. The CAS *mechanism* is proven; the *skill protocol* is not.
- **Proposed fix**: add `--out-file <path>` to the `read` subcommand (Python writes raw bytes, no shell redirection); change all SKILL.md to `read --file X --out-file base.bin`; extend the concurrency test to capture the base via the real `read --out-file` subcommand.
- **Builder disposition**: **ACCEPTED-FIXED** — `read --out-file` added; all 4 SKILL.md read commands use it; concurrency worker rewired to capture base via `vault_edit read --out-file` subprocess (closes the test gap).

### Majors

#### M1: `/archive` reuses one `base.bin` for two distinct target files
- **Issue**: `skills/archive/SKILL.md:63`/`:65` (slices/_index.md) and `:74` (slices/archive/_index.md) both use `--base-file base.bin`, but base.bin is captured from `slices/_index.md` only → archive/_index.md's rewrite validates against the wrong base → always conflict → STOP.
- **Proposed fix**: distinct base files per target (`idx_base.bin` / `archive_base.bin`), each via `--out-file`.
- **Builder disposition**: **ACCEPTED-FIXED** — distinct `--out-file` base files per target (folds into B1's `--out-file` fix).

#### M2: the `reflect:56` reword removed the directive verb → site no longer DETECTED (enforcement regressed to invisible)
- **Issue**: the reword's only directive verbs (`modify`/`write`) sit inside the hyphen-compound "read-modify-write", which `_is_mutation_site` rejects → the line is SKIPPED (`skill_vault_write_safety_audit.py:409 if not _is_mutation_site(line): continue`) → not counted/routed/enforced. AC-3 fail-closed no longer covers `reflect:56`; a future deletion of its `vault_edit rewrite` ref would NOT be flagged.
- **Evidence**: base line `_is_mutation_site=True`; reworded `=False` (even with route token stripped). Detected verbs all inside "read-modify-write".
- **Proposed fix**: lead with an un-hyphenated directive verb governing the ref ("**Rewrite** `architecture/risk-register.md` in place … via `vault_edit rewrite`") so `_is_mutation_site` re-detects + `_site_verb_is_rewrite_class` requires the rewrite route; add a regression test pinning `reflect:56` as detected + rewrite-routed.
- **Builder disposition**: **ACCEPTED-FIXED** — reworded to lead with "Rewrite … in place"; regression test added pinning the site detected + rewrite-class.

### Minors

#### m1: `reflect:143` still describes the retired `deferred-rmw` policy as live (stale/contradictory + AC-2 grep hit)
- **Issue**: `:143` (unedited this slice) says the RMW class is "deferred … marked `<!-- vault-write-safe: deferred-rmw -->`" — contradicts ADR-088 + the routed `:56`/`:321`, and literally contains the marker string AC-2's grep forbids. Escapes the audit only because the same line cites `vault_edit append` (route short-circuits the exemption check).
- **Builder disposition**: **ACCEPTED-FIXED** — `:143` updated to the enforced state (RMW routes via `vault_edit rewrite`, CAS, ADR-088); literal `deferred-rmw` marker string removed.

#### m2: `safe_rewrite_text` docstring's `\r\r\n` rationale imprecise (cosmetic; code correct)
- **Issue**: the comment names "stray CRLF" as the `\r\r\n` risk, but the code correctly preserves lone-`\r`-before-LF; behavior verified correct across 5 EOL payloads. Doc-only.
- **Builder disposition**: **ACCEPTED-FIXED** — comment reworded to name the real lone-CR/CRLF-preservation behavior.

## Dimensions checked
- [x] Unfounded assumptions — B1 (PowerShell `>` byte-exactness), m1 (stale :143).
- [x] Missing edge cases — none beyond findings; create/deleted-under-you/CRLF/LF/mixed/lone-CR/trailing-newline-both-directions/EPERM all verified correct.
- [x] Over-engineering — none (`_atomic_replace_with_retry` is genuine dedup).
- [x] Under-engineering — B1 + M1 (channel doesn't execute end-to-end as documented), M2 (fail-closed doesn't cover reflect:56).
- [x] Contract gaps — none in signatures; `StaleVaultBaseError` correctly NOT an OSError subclass (exit-3 distinct); `read` correctly uses `stdout.buffer` (reconfigure is in-place, `.buffer` stays raw).
- [x] Security — none (data-integrity control per ADR-067; no `shell=True`; `_resolve_in_vault` containment reused).
- [x] Drift from vault — m1 (:143 contradicts ADR-088); ADR-088 itself matches the code.
- [x] Web-known issues — B1 corroborated (MS Learn about_Character_Encoding; FiloSottile/age#290 — PowerShell redirection UTF-16LE+BOM corruption).
- [x] Cross-cutting conformance — RSAD-1/APED-1/EOL-DRIFT-1 all clean on the mechanism; the miss is B1/M2 (shell-boundary + hyphen-compound-verb composition).

## Builder fix summary (applied in-slice)
B1+M1 → `read --out-file` + distinct per-target base files + concurrency worker uses the real subcommand capture. M2 → `reflect:56` leads with "Rewrite … in place" + regression test. m1 → `reflect:143` de-staled. m2 → docstring reworded. Re-run: full suite + SVW-1 audit + the concurrency proof (now exercising the documented `read --out-file` protocol).
