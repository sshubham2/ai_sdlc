# Code Review: Slice 094 harden-vault-write-safety

**code-Critic reviewed**: slice diff vs default branch (base `117a647`), filtered to in-scope code paths (the two new tests + audit, `_vault_write.py` byte-fix, the two routed seam writers, inventory/version fan-out)
**Date**: 2026-06-01
**Result**: FINDINGS (0 Blockers, 1 Major, 3 Minors — all advisory in v1; none should block `/validate-slice`)

## Summary

The code is sound and faithfully implements design v3. The primary attack targets held up: the VWS-1 matcher is fail-closed *within its declared channel set* (every documented channel flags, every FP shape stays clean, scope-cache/`id(func)` correct, `os.replace` dst-resolution right), the byte-fix is byte-transparent (verified equal to the prior inline pattern, no CRLF), and the concurrency proof is non-vacuous and non-flaky (mutation arm lost 11-16/20 across 20 reps — never near 0; the `mp.Barrier` B1 fix is genuine). The one real finding (M1) is a **silent fail-OPEN for write channels the matcher does not enumerate** — `os.rename`, `io.open`, `shutil.move/copy` — which contradicts the audit's stated "fail-closed structural guarantee." None are in the current corpus (no live regression), but `os.rename` is the direct untracked twin of the covered `os.replace`.

> **Builder disposition (2026-06-01)**: **M1 ACCEPTED-FIXED** — added `os.rename` + `io.open` + `shutil.move/copyfile/copy/copy2` to `_write_target`, with an executed APED-1 battery planting each → VIOLATION; design.md §Detection model channel list + the audit docstring + shippability #104 clause updated to match. **m1 ACCEPTED-FIXED** — `_WRITE_OPEN_FLAGS` tightened to require a true write flag (`O_WRONLY`/`O_RDWR`/`O_APPEND`), dropping bare `O_CREAT`. **m2 + m3 ACCEPTED-AS-DOCUMENTED** (both fail-safe; benign in this corpus) — logged for /reflect, no code change.

## Changed files (in-scope)

```
tools/vault_write_safety_audit.py            (NEW)
tests/methodology/test_vault_write_safety_audit.py        (NEW)
tests/methodology/test_vault_write_safety_concurrency.py  (NEW)
tools/_vault_write.py                        (byte-fix)
tools/slice_queue_writer.py                  (routed)
tools/slice_queue_claim.py                   (routed)
tools/install_audit.py                       (+tool)
plugin.yaml VERSION pyproject.toml INSTALL.md methodology-changelog.md  (version fan-out)
tests/methodology/test_vault_safe_write.py                (doc note + byte-identity test)
tests/methodology/test_methodology_changelog.py           (version-gate rename + 2 entry-pins)
tests/methodology/test_utf8_stdout_regression.py          (cp1252 list +tool)
tests/methodology/test_stranded_slice_audit_tool_inventory.py     (38→39)
tests/methodology/test_pulse_worktree_resolver_tool_inventory.py  (38→39)
architecture/slices/slice-094-harden-vault-write-safety/build-log.md  (artifact)
```

## Findings

### Blockers (advisory in v1)

None. The matcher covers every channel it claims to (within the enumerated set); the byte-fix and concurrency proof are sound; the version fan-out is consistent (PMI-1/INST-1/UTF8 exit 0 at 39 tools / v0.80.0; no 4th stale `38`/`0.79.0` count — surviving `0.79.0` strings are all the legitimate append-only `## v0.79.0` changelog entry + SKILL.md citations + the rename-test docstring).

### Majors

#### M1: VWS-1 fails OPEN — silently — for write channels outside its 5-name enumeration (`os.rename`, `io.open`, `shutil.move/copy*`)
- **Claim under review**: `tools/vault_write_safety_audit.py:7-9` docstring — "the 'fail-closed' guarantee is real (a write op the matcher cannot classify … is a VIOLATION, never a silent pass)." Shippability #104 restates it.
- **Issue**: The guarantee held only for the 5 enumerated channels in `_write_target`. Any other channel → `None` → silently skipped → never a violation = fail-OPEN. Code-Critic executed the gap (planted temp modules): `os.rename`/`io.open`/`shutil.move` to a vault target all → status=clean. No corpus instance today (latent, not live → Major not Blocker), but `os.rename` is the direct twin of `os.replace` and the most likely future R-32 re-opening vector.
- **Proposed fix**: add `os.rename` alongside `os.replace` (target=arg1); optionally `io.open` + `shutil.move/copyfile/copy/copy2`; add planted-VIOLATION APED-1 tests; or narrow the "fail-closed" claim to "for the enumerated channels."
- **Builder disposition**: **ACCEPTED-FIXED** (broadened the channel set + APED-1 tests + doc/shippability alignment — the cheapest+best disposition; closes the os.rename twin gap).

### Minors

#### m1: `_WRITE_OPEN_FLAGS` includes bare `O_CREAT`, over-triggering vs design's "O_CREAT-with-write"
- `os.open(target, O_RDONLY|O_CREAT)` would flag as a write (FP-safe / fail-CLOSED direction; no corpus instance). **Builder disposition: ACCEPTED-FIXED** — tightened to require a real write flag.

#### m2: `_func_scope` walks into nested functions, over-collecting names
- `ast.walk(func)` descends into nested defs; `_enclosing_func` correctly attributes each write op to its innermost function, so over-collection is benign (a write referencing an inner-only name would be a runtime NameError anyway). Verified by execution. **Builder disposition: ACCEPTED-AS-DOCUMENTED** (benign; no fix).

#### m3: aliased `safe_write_text` import not counted as routed (benign)
- `import safe_write_text as sw; sw(...)` not detected as routed → under-reports `sites_routed`; fail-SAFE (an aliased routed call is a Name-call, never flagged/mis-counted as a violation). No alias today. **Builder disposition: ACCEPTED-AS-DOCUMENTED** (fail-safe brittleness note; no fix).

## Dimensions checked
- [x] Unfounded assumptions — none in impl; the audit docstring "fail-closed … never a silent pass" was the one over-statement → M1 (true only within the enumerated channel set; now broadened + claim aligned).
- [x] Missing edge cases — covered (empty/non-vault/tmp/reads/module-level/nested/f-string/with_name/module-const all execute correctly); the one uncovered edge was the un-enumerated write channel (M1, fixed).
- [x] Over-engineering — none. Bounded `_resolve_target` deliberately rejects undecidable dataflow with documented residuals.
- [x] Under-engineering — AC2/AC3/AC4 complete; passes PMI-1/INST-1/UTF8/MCFS-1/AVFS-1/TVFS-1/RSAD-1/APED-1. M1 was the one incomplete-delivery of "every channel flagged" (fixed).
- [x] Contract gaps — none structural (type hints + docstrings + tested exit codes; no phantom imports).
- [x] Security — none. Data-integrity control not a security boundary (ADR-067); ast.parse (no eval/exec/shell); ctypes holder is test-only + checks INVALID_HANDLE sentinel.
- [x] Drift from vault — one drift folded into M1 (docstring/shippability "fail-closed" claim vs enumerated-channel behavior; resolved by broadening + aligning). Everything else matches design v3 + R-33-reconciled fan-out (#104, no stale 38/0.79.0).
- [x] Web-known issues — confirmed (not contradicted) the platform claims: bugs.python.org#42606 (Windows O_APPEND NOT atomic across processes — validates Proof 2); msvcrt docs (LK_NBLCK OSError-on-contention + mandatory byte-range locks — validates sidecar-lock-not-target design + unlock-before-close).
- [x] Cross-cutting conformance — RSAD-1 (uses `_stdout`, passes UTF8-STDOUT-1); APED-1 (battery executed both directions; the M1 channel-gap was precisely the residual the battery didn't yet plant — now planted); EOL-DRIFT-1 (byte-fix correct, seam byte-equality preserved); `id(func)` scope-cache correct; POSIX `_nt_only` mutation arms vacuous-but-harmless, the cross-platform canary honestly documented.

**Net**: 0 Blockers / 1 Major (fixed) / 3 Minors (1 fixed, 2 accepted-documented). Nothing blocked `/validate-slice`.
