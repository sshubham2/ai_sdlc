# Validation: Slice 097 harden-skill-driven-vault-rewrites

**Date**: 2026-06-01
**Result**: PASS

Methodology tooling slice — "real environment" = exercising the actual CLI tools + audits on real files (real CRLF vault files, real multi-process concurrency, real shell invocation), not mocks.

## Per-criterion results

### AC1: concurrency-safe CAS rewrite channel — EOL-normalized compare + EOL-preserving write; concurrent rewrites lose zero updates silently
- **Status**: PASS
- **Evidence**: Real-CLI end-to-end demo (self-contained subprocess, AI_SDLC_VAULT_ROOT→tmp vault, CRLF + UTF-8 em-dash payload):
  - `vault_edit read --file idx.md --out-file base.bin` → rc 0; base **byte-exact** to source (CRLF + em-dash preserved).
  - `vault_edit rewrite --base-file base.bin --content-file new.md` (LF-authored new content, matched base) → rc 0; result **all-CRLF** (`count(\n)==count(\r\n)`, no CRLF→LF churn), new row landed, em-dash intact → EOL-preserving write proven (B1).
  - stale-base `rewrite` (file changed since base) → rc **3** + CONFLICT message; file **untouched** (no silent overwrite).
  - Concurrency proof `test_skill_vault_rewrite_concurrency.py::test_cas_rewrite_loses_zero_updates`: 6 barrier-synchronized spawn workers running the documented `read --out-file`→`rewrite`→retry-on-3 loop on a CRLF fixture → all 6 markers land, 0 lost, CRLF preserved.
- **Notes**: "lose zero updates silently" holds — every concurrent rewrite either commits or fails-closed exit-3 (loud) → re-applied via retry; never a silent overwrite.

### AC2: all `deferred-rmw`-class sites routed; the `deferred-rmw` standing exemption removed
- **Status**: PASS
- **Evidence**: `skill_vault_write_safety_audit --json` → status **clean**, 23 sites found / 20 routed / 3 exempt (all `project-open-single-shot`). `grep -rl 'vault-write-safe: deferred-rmw'` on reflect/archive/supersede SKILL.md → **0** markers. `_EXEMPT_REASONS == {project-open-single-shot}` (test_exempt_reasons_are_closed); `_REGISTERED_SKILL_EXEMPTIONS` 12→3.
- **Notes**: the 9 ex-deferred-rmw sites route via `vault_edit rewrite` (reflect:56/:321, archive×5, supersede:103) or `vault_edit append` (reflect:322 — append-shaped catalog row).

### AC3: SVW-1 fail-closed + op-class-aware; project-open-single-shot stays exempt
- **Status**: PASS
- **Evidence**: op-class battery (7 tests pass): `test_rmw_site_routed_via_append_is_channel_mismatch` (B2 — rewrite-verb + append-route → VIOLATION), `test_bare_tools_vault_edit_append_on_rewrite_verb_is_violation` (B-add-1 bare-token-severance — the real `$PY -m tools.vault_edit append` corpus form on a regenerate verb → VIOLATION), `test_bare_tools_vault_edit_no_subcommand_does_not_clean_rewrite`, `test_append_verb_with_append_route_is_clean`/`_with_rewrite_route`, `test_deferred_rmw_marker_is_now_violation`, `test_reflect_risk_status_flip_is_detected_and_rewrite_routed` (M2 regression). The 3 project-open-single-shot sites remain exempt (audit JSON above).
- **Notes**: honest lexical-ceiling residual documented (RMW phrased with ambiguous verbs `update`/`write` routed via append is not caught — only `regenerate`/`rewrite` are rewrite-class).

### AC4: non-vacuous concurrency proof (mutation)
- **Status**: PASS
- **Evidence**: `test_naive_rewrite_mutation_loses_writes` — 6 barrier-synchronized spawn workers doing unconditional `safe_write_text` (no CAS) → survivors < 6 (writes LOST). Paired with the CAS arm (0 lost) this is the non-vacuity proof (slice-092/094/095 mutation discipline). Cross-platform (the RMW lost-update is app-level, not OS-atomicity-dependent).

### AC5: R-32 narrowed in the register; full suite + Step-6 gates green; OSDG-1 drift green
- **Status**: PASS
- **Evidence**: full methodology suite **1437 PASS**; all Step-6 gates clean (SVW-1, BC-1 strict, BRANCH-2, PCA-1, BCI-1, MCFS-1, AVFS-1, TVFS-1, STP-1, DCE-1, NAW-1, UTF8-STDOUT-1, WIRE-1, LINT-MOCK, CRP-1); `test_reflect_skill_drift.py` PASS (OSDG-1, in-repo ≡ installed); shippability catalog **103/103 PASS** (no regression).
- **Notes (register-narrowing)**: per design.md §R-32 disposition ("recorded fully at /reflect"), the R-32 register-note narrowing (skill-driven RMW sub-class CLOSED; residual = 3 git-coupled tools + flip mechanics) is the immediately-following `/reflect` deliverable — it dogfoods `vault_edit rewrite` on the real CRLF `risk-register.md`/`_index.md` (the critique-review m-add-2 live-fire). The slice's CODE that closes the RMW sub-class is done + validated here; R-32 status stays `mitigating` (STP-1 clean — not flipped). This is a designed sequencing (doc-step at /reflect), NOT a validation gap.

## Multi-instance validation
**Required?**: yes — this is a concurrency control (multiple parallel slice-worktree skills writing the same vault file).
**Result**: PASS
**Evidence**: validated with N=6 concurrent `multiprocessing(spawn)` processes released by a shared `mp.Barrier` (true simultaneous contention, not staggered), each shelling the real `vault_edit` CLI — the multi-process analogue the R-32 hazard requires. CAS arm: all land; naive arm: writes lost.

## Reality surprises
- None at validation. (The two significant surprises — the PowerShell `>`/Out-File byte-corruption of the base-capture, and the `reflect:56` reword dropping the site out of audit detection — were caught at `/code-review`, not here, and fixed in-slice: `read --out-file` + adding `rewrite` to `_DIRECTIVE_VERBS`.)

## Shippability catalog regression check
- SCMD-1 clean (103 rows, 1133 cited fns), PTFCD-1 clean (452 test-path tokens all resolve), SVW-1 clean.
- Runner: **103 rows, 103 PASS, 0 FAIL**. No past slice regressed.

## VAL-1 layered safety
- Layer A (credential scan): 0 secrets.
- Layer B (dependency hallucination): 0 import findings (changed `.py` imports all resolve; `--imports-allowlist tests`).
