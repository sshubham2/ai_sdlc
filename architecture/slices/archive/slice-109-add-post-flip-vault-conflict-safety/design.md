# Design: Slice 109 add-post-flip-vault-conflict-safety

**Date**: 2026-06-03
**Mode**: Standard

## What's new

- A **bounded, fail-visible CAS retry loop** wrapping the read-compose-write cycle of the three queue/claim read-modify-write writers, so each rewrites via `_vault_write.safe_rewrite_text` (compare-and-swap) instead of the non-CAS whole-file `safe_write_text`. The whole read→compose→CAS attempt repeats on `StaleVaultBaseError`; exhaustion of the bound RAISES (never silent last-writer-wins).
- `tools/vault_write_safety_audit.py` (VWS-1) learns `safe_rewrite_text` as a third **routed safe channel** (`_ROUTED_FUNCS`), with its membership pin test extended — so the newly CAS-routed sites read as routed and a future un-routed vault write still fails the audit.
- `.gitattributes` gains `architecture/slice-queue.md eol=lf` — enforces the LF precondition the AC4 byte-identity claim depends on (Critic B1).
- New tests: `tests/methodology/test_post_flip_queue_cas.py` (routing + retry + LF byte-identity + CRLF-on-disk behavior) and `tests/methodology/test_post_flip_queue_cas_concurrency.py` (barrier-synchronized N≥4 lost-update proof exercising `record_pick`/claim/regen + a concurrent-mutation-triggers-one-retry-both-land test + non-vacuous mutation control).
- Vault: R-32 register entry + `architecture/shippability.md` updated to record the residual closed.

## What's reused

- `_vault_write.safe_rewrite_text` + `StaleVaultBaseError` — the CAS channel shipped by [[slice-097-harden-skill-driven-vault-rewrites]] / [[decisions/ADR-088]]. EOL-NORMALIZED base compare + EOL-PRESERVING write; under the sidecar `<path>.lock`. See `tools/_vault_write.py:206`.
- The existing read/compose logic in the writers — `record_pick` (`tools/slice_queue_writer.py:742`, idempotent pick-log-block scan + rebuild), `write_slice_queue` (`tools/slice_queue_writer.py:810`, claim-preserving top-10 regen), and `slice_queue_claim`'s entry-rewrite + `_atomic_write_text` (`tools/slice_queue_claim.py:528`). Only the WRITE call (and a base-capture + retry wrapper) changes; the compose logic is unchanged.
- VWS-1's routed-channel detection machinery (`_ROUTED_FUNCS` at `tools/vault_write_safety_audit.py:114`) — [[slice-094-enforce-python-vault-write-safety]] / [[decisions/ADR-086]].
- The barrier-synchronized multiprocessing-spawn concurrency-proof pattern from `tests/methodology/test_vault_write_safety_concurrency.py` / `test_skill_vault_rewrite_concurrency.py` (AP-5 non-vacuity + AP-6 barrier).

## Components touched

### `tools/slice_queue_writer.py` (modified)
- **Responsibility**: writes `slice-queue.md` — the `## Candidates` regen (`write_slice_queue`) and the `## Pick log` append (`record_pick`). Both are read-modify-write: read existing → compose new full text → write.
- **Change**: wrap read→compose→write in a bounded retry over `safe_rewrite_text(out_path, new_text, expected_base=base_bytes)`. **Single-read invariant (Critic M1)**: each retry attempt does ONE `read_bytes()` → `base = those bytes` → `existing_text = base.decode("utf-8")` (NOT a separate `read_text()` that could straddle a concurrent write); the full compose (`record_pick`'s idempotency prefix-scan, `write_slice_queue`'s `parse_queue_text` claim-preservation + `_extract_pick_log_block`) re-runs on that single fresh base inside the loop, so a concurrent writer's pick/claim is seen on re-read. **Graphify hoist (Critic M1)**: `derive_active_slice_blast_radius` (`tools/slice_queue_writer.py:868`, spawns ~30s graphify subprocesses) is computed ONCE before the retry loop — it does not depend on the queue file's bytes — so retries never re-spawn graphify (no livelock cost). **record_pick concurrency (Critic M2)**: two distinct slices' picks produce distinct `- <slice> —` prefixes; both survive because the prefix-scan re-runs on the retry's fresh base (pinned by `test_concurrent_record_pick_distinct_slices_both_survive`).
- **Key interactions**: `_vault_write.safe_rewrite_text`; `slice_queue_claim.parse_queue_text` (claim preservation); callers `/slice` Step 6.5 + the CLI.

### `tools/slice_queue_claim.py` (modified)
- **Responsibility**: claim / release / force-claim a queue candidate — reads queue, rewrites the target `### entry` block, writes whole file (`_atomic_write_text` → `safe_write_text`, `tools/slice_queue_claim.py:528`).
- **Change**: same single-read base-capture + bounded CAS-retry wrapper around the claim/release read-rewrite-write cycle, via `safe_rewrite_text`. **Critic M1**: `apply_claim`/`apply_release` (and the unconditional `force_claim` write path, `tools/slice_queue_claim.py:609`) re-run on the re-read text INSIDE each retry — a concurrent claim is re-applied, not clobbered.
- **Key interactions**: `_vault_write.safe_rewrite_text`; the `python -m tools.slice_queue_claim` CLI (PSQ-2).

### `tools/vault_write_safety_audit.py` (modified)
- **Responsibility**: VWS-1 — fail-closed AST audit that every `tools/*.py` vault write goes through a routed safe channel.
- **Change**: add `"safe_rewrite_text"` to `_ROUTED_FUNCS` (`tools/vault_write_safety_audit.py:114`); update the diagnostic message that enumerates the safe channels; extend the membership pin test so the recognized set stays a closed, pinned `{safe_write_text, safe_append_text, safe_rewrite_text}` (no silent widening). **Critic m1 + code-review M1 (CAS-defeat defense)**: `safe_rewrite_text` is recognized as routed ONLY when `expected_base=` is present AND does not RESOLVE to a constant — a literal `b""` **OR a module-level name bound to a constant** (`expected_base=_EMPTY` where `_EMPTY = b""`) is a CAS-defeat → NOT auto-cleaned, and `_write_target` flags it as an un-routed vault write; a genuinely dynamic/local base (the real writers' read-bytes result, not a module constant) stays routed. `_is_routed_call(call, module_consts)` resolves the name-indirection variant (code-review M1 closed the literal-only gap; the audit already owns this name→const machinery via `_collect_consts`). Pinned by `test_safe_rewrite_text_degenerate_base_flagged` + `test_safe_rewrite_text_name_bound_constant_base_flagged` (both EXECUTED — APED-1).
- **Key interactions**: `/build-slice` Step 6 + `/validate-slice` invoke it; `test_vault_write_safety_audit.py` pins it.

### `tools/_vault_write.py` (modified — optional helper)
- **Responsibility**: the R-32-safe vault writer.
- **Change (if a shared wrapper is chosen)**: a thin bounded-retry helper (e.g. `rewrite_with_retry(path, compose, *, retries)`) that performs read-bytes → `compose(base)` → `safe_rewrite_text(..., expected_base=base)` → retry-on-`StaleVaultBaseError`, raising on exhaustion. It MUST live in `_vault_write` so the actual `safe_rewrite_text` write site VWS-1 inspects stays inside the writer module. If instead the retry loop is inlined at each of the 3 call sites (calling `safe_rewrite_text` directly), no `_vault_write` change is needed — both satisfy AC1; the Builder picks one at plan time. Either way the 3 writers reach the recognized CAS channel.

## Contracts added or changed

None. No endpoints, events, or schemas. All changes are internal function-call routing + an audit's recognized-channel set. The `safe_rewrite_text(path, text, *, expected_base: bytes)` signature is unchanged (reused as-is).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new production module** — it modifies existing `tools/*.py` and adds test files (consumer tests, not modules demanding consumers). Zero-row matrix is clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[decisions/ADR-098]] — Close the post-flip vault-queue read-modify-write lost-update class by routing the queue/claim RMW writers through the `_vault_write` CAS channel under a bounded fail-visible retry, and teach VWS-1 to recognize the CAS channel — reversibility: **cheap**.

## Authorization model for this slice

N/A — no auth/authz surface. The writers are local-process vault writers; cross-process safety is enforced by the OS sidecar file lock + CAS, not an authorization check.

## Error model for this slice

- `StaleVaultBaseError` (from `safe_rewrite_text`) is the **retryable** signal: the writer re-reads the current bytes, re-applies its compose, and retries, bounded at ≈5 attempts (ADR-088 `vault_edit rewrite` precedent).
- **Retry exhaustion** raises (propagates a typed error) — fail-visible, never a silent fall-back to a lost-update-prone `safe_write_text`. R-32's hazard is silent corruption; the degrade path must be loud. **Fail-visibility asymmetry at the production caller (Critic M-add-1)**: at `skills/slice/SKILL.md` Step 6.5, `record_pick` is un-wrapped → its raise propagates loudly (provenance is non-regenerable, must stay loud); `write_slice_queue` is inside the ADR-064 `try/except Exception` non-fatal wrapper → its exhaustion-raise is caught and downgraded to a WARN. This is correct, not a silent lost-update: the `## Candidates` top-10 is a regenerable advisory list (regenerated next `/slice`), so swallowing its regen is the ADR-064-designed behavior; only the non-regenerable pick-log demands loudness. The "loud" must-not-defer is therefore scoped to `record_pick`.
- The first-write / create race is covered by CAS: `expected_base=b""` against a now-non-empty file mismatches → retry → re-read sees the created file → re-compose → write.

## Scope / methodology notes

- **MEPD-1 EXCLUDE** (mirrors slices 097/098): no new module, no new RULE-ID, no `methodology-changelog.md` entry, no VERSION bump. Routing existing writers through an existing channel + extending VWS-1's recognized-channel set is the rule operating within its documented scope, not a new rule.
- **No `/commit-slice` edit** — the post-flip `/commit-slice --merge` RETIRE no-op + the distinct PCR RETIRE signal are scope-narrowed OUT to the flip slice per ADR-089 (back-propagated to mission-brief Out-of-scope, AP-17). So this slice touches **no guarded SKILL.md** (no OSDG-1 forward-sync) — only `tools/*.py` + tests + vault.
- **No-flip byte-identity (AC4), enforced not assumed (Critic B1)**: `safe_rewrite_text` is EOL-PRESERVING while `safe_write_text` is LF-faithful — so byte-identity holds only while the queue is LF on disk, which `.gitattributes` does NOT guarantee for `architecture/**` (executed: a CRLF on-disk queue → `safe_rewrite_text` preserves CRLF, `safe_write_text` writes LF → NOT identical). This slice adds `architecture/slice-queue.md eol=lf` to `.gitattributes` (the queue is a tool-owned regenerable artifact, legitimately LF-canonical — unlike the hand-edited CRLF aggregates `safe_rewrite_text` was built to preserve), enforcing the LF precondition; byte-identity to `safe_write_text` then holds and the PSQ-1/PSQ-2 byte-equal round-trip assertions hold. The CRLF-on-disk edge is pinned by an executed behavior test (APED-1), not reasoned away.
