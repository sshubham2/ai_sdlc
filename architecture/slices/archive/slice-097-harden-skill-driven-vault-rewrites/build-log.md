# Build log: Slice 097 harden-skill-driven-vault-rewrites

**Date**: 2026-06-01
**Result**: SHIPPED

## Events (append-only — one line per significant action)

- 2026-06-01 BUILD: BRANCH-2 worktree created at ai_sdlc-wt/slice-097-... (branch slice/097-...; scaffolding commit bb8c05b); seeded graphify-out + diagnose-out
- 2026-06-01 BUILD: plan approved (6 tasks); milestone → stage:build; CRP-1 clean; _index.md confirmed CRLF (309KB) — B1 environment present
- 2026-06-01 BUILD: Task 1 start — safe_rewrite_text + _normalize_eol in tools/_vault_write.py
- 2026-06-01 TEST: Task 1 — safe_rewrite_text + _normalize_eol + _detect_eol + _atomic_replace_with_retry added; refactored safe_write_text to share the helper; 19/19 test_vault_safe_write.py PASS (incl. 8 new CAS tests: EOL-normalized compare, EOL-preserving write, M-add-1 trailing-newline-both-directions, create-when-absent, EPERM-retry, structural guard)
- 2026-06-01 BUILD: Task 2 start — vault_edit rewrite + read subcommands
- 2026-06-01 TEST: Task 2 — vault_edit.py rewritten (append + rewrite[CAS, exit-3] + read[raw-bytes base capture]; binary --base-file; docstring updated); 14/14 test_vault_edit_cli.py PASS (incl. 6 new: rewrite happy/conflict-exit-3/CRLF-EOL-preserving/missing-base, read raw-bytes/empty)
- 2026-06-01 BUILD: Task 3 — NEW test_skill_vault_rewrite_concurrency.py (spawn+barrier; CAS arm shells vault_edit rewrite via CLI subprocess per M1; naive mutation arm; CRLF fixture)
- 2026-06-01 SMOKE: MID-SLICE GATE PASS — CAS converges on CRLF fixture, 6/6 rewrites land (0 lost, EOL preserved); naive mutation loses writes (non-vacuous). B1 validated end-to-end via real CLI subprocess path; no false-conflict/livelock. 2 passed in 1.41s
- 2026-06-01 BUILD: Task 4 start — skill_vault_write_safety_audit.py op-class-aware (B2/B-add-1) + enum/allowlist 12→3
- 2026-06-01 TEST: Task 4 — op-class-aware verdict (retired bare tools.vault_edit token; APPEND/REWRITE token sets; _REWRITE_CLASS_VERBS={regenerate,rewrite}; rewrite-verb+append-route → channel-mismatch VIOLATION); deferred-rmw removed from _EXEMPT_REASONS; allowlist 12→3. Audit detects all 9 unrouted RMW sites (exit 1, expected pre-routing). 44/46 audit tests PASS; the 2 real-corpus-clean tests fail pending Task 5 routing. NEW: B2 channel-mismatch + B-add-1 bare-token-severance proofs PASS.
- 2026-06-01 BUILD: Task 5 start — route the 9 RMW sites in reflect/archive/supersede-slice SKILL.md
- 2026-06-01 BUILD: Task 5 — routed 9 sites: reflect :56(risk-status)/:321(_index regen)→rewrite, :322(archive/_index)→append (reworded verb Regenerate→Append per m-add-1 so op-class stays sound); archive :27/:58/:75/:131/:177→rewrite + B3 main-thread-owns-CAS protocol + m-add-3 --index-only recovery note; supersede :103→rewrite. SVW-1 audit CLEAN: 21 sites/18 routed/3 exempt(project-open)/0 violations
- 2026-06-01 TEST: Task 5 — forward-synced reflect+archive+supersede SKILL.md to ~/.claude/skills/; reinstalled ai-sdlc-tools-0.80.0 (content refresh, same VERSION — EXCLUDE). reflect OSDG-1 drift PASS; installed tools expose vault_edit rewrite + safe_rewrite_text. 81/81 across the 4 modified test files
- 2026-06-01 BUILD: Task 6 start — pre-finish gates (R-32 note deferred to /reflect dogfood per design; drift-check + all Step-6 audits + full suite)
- 2026-06-01 TEST: full methodology suite 1434 PASS (no regression from the safe_write_text refactor or audit op-class change; +24 new tests)
- 2026-06-01 TEST: Step-6 audits all CLEAN — BRANCH-2, WIRE-1, PCA-1, BCI-1, MCFS-1, AVFS-1, TVFS-1 (installed ai-sdlc-tools 0.80.0 matches VERSION), STP-1, NAW-1 (no new agents), UTF8-STDOUT-1 (39/39), CRP-1, SVW-1 (21 sites/18 routed/3 exempt/0 viol)
- 2026-06-01 BUILD: BC-1 attestations — BC-PROJ-3/BC-GLOBAL-2 (Critical): this slice performs NO destructive git checkout/restore/stash revert of uncommitted work; all test mutations use tmp_path fixtures + monkeypatch, never source-mutate-then-git-revert; the BRANCH-2 worktree flow COMMITS scaffolding (never stashes). BC-PROJ-4 (Important, addressed): the SVW-1 parse-rule change (op-class verdict + _REWRITE_VERB_RE + token sets) + the SKILL.md gate-prose edits carry an APED-1 both-direction battery (rewrite-routed CLEAN / RMW-via-append channel-mismatch / bare-token-severance / append-verb-clean) + a real-corpus-clean assertion, executed against the live tree. BC-PROJ-5 (Important, addressed): the surviving exemption set (3 project-open-single-shot rows) is pinned by test_exemption_allowlist_pinned; retired deferred-rmw proven-gone (test_deferred_rmw_marker_is_now_violation + audit 0 deferred-rmw). BC-PROJ-11 (Important, N/A): no INSTALL.md/README.md edit; no version literal (MEPD-1 EXCLUDE, VERSION unchanged 0.80.0).

- 2026-06-01 BUILD: /code-review (code-Critic on diff) — 2B/2M/2m, ALL VALIDATED (zero false alarms), ALL ACCEPTED-FIXED in-slice
- 2026-06-01 FINDING: B1 — documented `vault_edit read ... > base.bin` corrupts the CAS base under PowerShell (`>`=Out-File→UTF-16LE+BOM) → livelock; the concurrency test captured base in-process so the shell protocol was never exercised (test gap)
- 2026-06-01 FIX: B1+M1 — added `read --out-file` (Python writes raw bytes, no shell `>`); all 4 SKILL.md read commands use `--out-file`; archive uses DISTINCT per-target base files (idx_base.bin/archive_base.bin); concurrency worker rewired to capture via `read --out-file` subprocess (+2 CLI tests); FIX M2 — reflect:56 "Rewrite … in place" + added "rewrite" to `_DIRECTIVE_VERBS` (now detected+rewrite-class) + regression test; FIX m1 reflect:143 de-staled; FIX m2 docstring
- 2026-06-01 TEST: post-fix — SVW-1 23/20/3/0 CLEAN (reflect:56 now detected+rewrite-routed; no false positives from +rewrite verb); reflect OSDG-1 drift PASS; UTF8-STDOUT-1 clean; ai-sdlc-tools reinstalled; full suite **1437 PASS**

## Summary

### Plan executed
1. **`tools/_vault_write.py`** — `safe_rewrite_text` (CAS) + `_normalize_eol` (CRLF→LF only) + `_detect_eol` + `StaleVaultBaseError` + shared `_atomic_replace_with_retry` (refactored `safe_write_text` to share it). ✅ (B1, M-add-1)
2. **`tools/vault_edit.py`** — `rewrite` (CAS, exit 0/2/3) + `read` (raw-bytes base) subcommands; binary `--base-file`; docstring updated. ✅ (B1, M2)
3. **NEW `tests/methodology/test_skill_vault_rewrite_concurrency.py`** — spawn+barrier; CAS arm shells `vault_edit rewrite` (CLI subprocess, M1); naive mutation arm; CRLF fixture. ✅ (M1)
4. **`tools/skill_vault_write_safety_audit.py`** — op-class-aware (retired bare token; APPEND/REWRITE token sets; `_REWRITE_CLASS_VERBS`; channel-mismatch verdict); `deferred-rmw` removed from enum; allowlist 12→3. ✅ (B2, B-add-1, m1)
5. Routed 9 SKILL.md sites (reflect/archive/supersede) + B3 main-thread-owns-CAS protocol + m-add-3 recovery; forward-synced installs + reinstalled `ai-sdlc-tools`. ✅ (B3, m-add-1/2/3)
6. Pre-finish: drift-check + all Step-6 audits + full suite. ✅ (m2 R-32 note → /reflect)

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `test_skill_vault_rewrite_concurrency.py` — CAS arm 6/6 rewrites land on a **CRLF** fixture (0 lost, EOL preserved, no false-conflict/livelock); naive mutation arm loses writes (non-vacuous). B1 validated end-to-end via the real CLI subprocess path. `2 passed in 1.41s`.

### Pre-finish gate
- [x] All ACs pass with evidence (→ validation.md): AC1 CAS channel (concurrency + CLI + units), AC2 9 sites routed + deferred-rmw removed (SVW-1 CLEAN 21/18/3/0), AC3 op-class fail-closed + project-open exempt (battery), AC4 non-vacuous proof (mutation), AC5 suite green + OSDG-1 drift green (R-32 note at /reflect)
- [x] Must-not-defer addressed: lock spans read→compare→write (CAS, not append-masquerade) / byte-faithful EOL-preserving (proven on CRLF) / fail-VISIBLE exit 2/3 (R-7) / SVW-1 fail-closed for RMW / cp1252-safe (UTF8-STDOUT-1 39/39; `read` uses stdout.buffer)
- [x] Drift-check full mode PASS (DCE-1 clean — marker written)
- [x] Mid-slice smoke still passes (in full suite)
- [x] No new TODOs/FIXMEs/debug prints
- [x] All Step-6 audits clean: BC-1(strict, BC-PROJ-3+BC-GLOBAL-2 acked), WIRE-1, LINT-MOCK, BRANCH-2, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, DCE-1, SVW-1; full suite **1434 PASS**

### Deferrals
- R-32 register-note narrowing + `_index.md`/risk-register regeneration → **/reflect** (per design.md §R-32 disposition: "recorded fully at /reflect"; dogfoods `vault_edit rewrite` on the real CRLF files — the m-add-2 live-fire). NOT a build defect; the design assigns it to /reflect.

### Design deviations
- `_REWRITE_RETRY_MAX` is NOT a `vault_edit` constant (design hinted it could be): `vault_edit rewrite` is single-attempt (exit 3 on conflict) because it cannot re-apply an LLM edit internally; the bounded retry lives in SKILL prose (read→rewrite→retry-on-3, ~5 attempts). Recorded; consistent with ADR-088's "the skill re-reads + re-applies + retries". design.md updated to reflect this is fine as-is (the skill owns the loop).
- Concurrency proof CAS arm shells the CLI subprocess (M1) while the mutation arm calls `safe_write_text` directly (clean no-CAS mutation — there is no unconditional-rewrite CLI by design). Asymmetric by necessity; each arm proves its half.

### Files changed
- `tools/_vault_write.py`, `tools/vault_edit.py`, `tools/skill_vault_write_safety_audit.py`
- `tests/methodology/test_vault_safe_write.py`, `test_vault_edit_cli.py`, `test_skill_vault_write_safety_audit.py`, NEW `test_skill_vault_rewrite_concurrency.py`
- `skills/reflect/SKILL.md`, `skills/archive/SKILL.md`, `skills/supersede-slice/SKILL.md` (+ forward-synced to `~/.claude/skills/`)
- `architecture/drift-log.md` (slice-097 audit entry)
- (installed) `ai-sdlc-tools` reinstalled 0.80.0
