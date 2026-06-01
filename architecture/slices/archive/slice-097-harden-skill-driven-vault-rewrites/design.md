# Design: Slice 097 harden-skill-driven-vault-rewrites

**Date**: 2026-06-01
**Mode**: Standard

## Decision ratified at design (user, 2026-06-01)

The one open design fork — the RMW lost-update mechanism — was resolved by structured-options gate:

**Mechanism → Compare-and-swap (optimistic concurrency by base-comparison).** A new `vault_edit rewrite` subcommand re-reads the target *under the sidecar lock* and writes only if its bytes still equal the base the skill read; on mismatch it fails closed (a distinct exit code) and the skill prose re-reads + retries (bounded). Chosen over a **held vault-lease** (rejected — holds a lock across an unbounded LLM turn; a dead/aborted session strands the lease → a new failure mode needing expiry/steal/recovery) and over **structured per-op transforms** (rejected — 5+ bespoke transforms to build+test AND `/archive`'s full `_index.md` regeneration doesn't fit the prepend/set-field shape, so it would *still* need CAS → building both exceeds a 1-day slice). CAS is the single uniform mechanism that also covers `/archive`'s full-regen, holds no lock across an LLM turn, and is fail-VISIBLE (R-7). See [[ADR-088]].

This closes the **read-modify-write (RMW) residual** that [[slice-095-harden-skill-driven-vault-writes]] deliberately deferred ("the flip slice MUST close the RMW class BEFORE the flip goes live — it is not optional polish", slice-095 design.md §51). slice-097 is that pre-flip close.

## What's new

- `tools/_vault_write.py` — **NEW function `safe_rewrite_text(path, text, *, expected_base: bytes)`** (underscore module → no PMI-1 fan-out). Under the existing `_file_lock` sidecar lock: read current target raw bytes → **compare EOL-normalized** (`_normalize_eol(current) == _normalize_eol(expected_base)`, CRLF≡LF) → if equal, write `text` **preserving the target's detected EOL** (detect-and-match: CRLF target ⟶ CRLF write) via the temp-write + atomic `os.replace` + bounded-EPERM-retry path → else raise a typed `StaleVaultBaseError`. **(critique B1/M2 — load-bearing):** the on-disk RMW targets `architecture/slices/_index.md` (309KB) and `architecture/risk-register.md` (137KB) are **CRLF** — `.gitattributes` does NOT normalize `architecture/**` (and explicitly scopes whole-vault renormalization OUT per slice-033/[[ADR-033]]). So a byte-EXACT compare would false-conflict on every attempt (base is LF-normalized, disk is CRLF) → livelock → fail-STOP, making the channel unusable on the very files R-32 exists for; AND an LF write would churn 309KB CRLF→LF (EOL corruption on an unguarded surface). The EOL-normalized compare makes representation immaterial (detects genuine content changes, ignores CRLF/LF); the EOL-preserving write avoids churn. The lock genuinely spans read→compare→write **in-process** — the LLM's read+edit happened OUTSIDE the lock, but the CAS re-validation under the lock converts a stale-base overwrite from SILENT to DETECTED. A pure EOL-flip between read and write is (correctly) NOT a conflict — it is not a content lost-update.
- `tools/vault_edit.py` — **NEW `rewrite` subcommand** (same existing tool — no new module, no PMI-1 count bump): `rewrite --file <vault-rel> --base-file <bytes-I-read> (--content-file <new> | --stdin)`. Resolves `--file` under `VAULT_ROOT` (reuses `_resolve_in_vault`). **(critique M2):** `--base-file` is read in **binary** (`open(...,"rb")` / `newline=""`), NOT `_read_content`'s universal-newlines `read_text` (which would LF-normalize the base and defeat the point). **Base-capture contract**: the skill obtains the base via a **tool-mediated raw read** — `vault_edit` gains a `read`/`snapshot` mode that emits the current file's content for the skill to edit — NOT the `Read` tool's `cat -n`/EOL-normalized output. Combined with B1's EOL-normalized compare, the skill may pass an LF base safely against a CRLF target. Reads base + new content, calls `safe_rewrite_text(target, new, expected_base=base_bytes)`. Exit **0** written / **2** usage (bad/escaping path, missing content/base) / **3** CAS conflict (fail-closed, the *retryable* signal — distinct from usage so prose can branch; the retry cap is `_REWRITE_RETRY_MAX` = a named constant, build picks ~5, fail-VISIBLE STOP on exhaustion). Edge cases: missing target ⟺ empty/absent base = create; missing target + non-empty base = conflict (exit 3, "deleted under you").
- `tools/skill_vault_write_safety_audit.py` — **enforce the RMW class, op-class-aware** (same existing tool): (1) add `"vault_edit rewrite"` to `_SAFE_ROUTE_TOKENS`; (2) **(critique B2 — op-class-aware enforcement):** a mutation site whose directive verb is **rewrite-class** (`regenerate`/`rewrite`/in-place-edit phrasing) that cites ONLY an `append`-class route token (`vault_edit append`, or a bare `tools.vault_edit ... append`) → **VIOLATION (channel-mismatch)**, NOT CLEAN. This closes the flat-OR hole where `_SAFE_ROUTE_TOKENS`'s pre-existing `"tools.vault_edit"` substring cleaned ANY subcommand incl. the lost-update-UNSAFE `append` — the "append masquerading as a rewrite" trap the must-not-defer forbids. **Honest residual (pinned, mirroring the M2/R-2 scope note):** enforcement is op-class-aware only to the lexically-determinable degree — an RMW operation phrased with an append-class verb, or an unclassifiable verb, can still mis-route; the lexical ceiling is documented in code + a test, not silently assumed closed. (3) **remove `"deferred-rmw"` from `_EXEMPT_REASONS`** → a lingering `deferred-rmw` marker becomes an `unknown-exemption-reason` VIOLATION (the deferral is *retired*, not re-markable); (4) drop the 3 `deferred-rmw` rows from `_REGISTERED_SKILL_EXEMPTIONS` (reflect/archive/supersede-slice) → the registered total falls **12 → 3** (only `project-open-single-shot` remains).
- Routed RMW prose in `skills/reflect/SKILL.md` (`:56` risk-status flip, `:321` `_index.md` recent-10/Active/lessons regen, `:322` `archive/_index.md`), `skills/archive/SKILL.md` (`:27`/`:58`/`:75`/`:131`/`:177` `_index.md` + `archive/_index.md` full regen), `skills/supersede-slice/SKILL.md` (`:103` superseded-row edit) — each now cites `vault_edit rewrite` (CAS) with the read→rewrite→retry-on-exit-3 protocol. A genuinely-append-shaped site among these (if any survives classification at build, e.g. a pure chronological `archive/_index.md` append) routes via the existing `vault_edit append` instead — the build executes the audit to confirm the post-routing tree is CLEAN with exemptions = 3.
- `tests/methodology/test_vault_safe_write.py` — extend with `safe_rewrite_text` CAS unit coverage (equal-base writes / stale-base raises `StaleVaultBaseError` / EPERM-retry inherited / byte-faithfulness).
- **NEW `tests/methodology/test_skill_vault_rewrite_concurrency.py`** (critique M1 — NOT the thread-based `test_skill_vault_write_safety_concurrency.py`, which is `ThreadPoolExecutor` + a `sleep`-widened GIL-masked window): the R-32 RMW concurrency proof as **`multiprocessing(spawn)`/subprocess `$PY -m tools.vault_edit rewrite` workers released by a shared barrier** (`mp.Barrier` via a manager, or a file-presence spin — the slice-094 "un-barriered spawn staggers ~100ms/worker, never overlaps" lesson). Each worker runs the read→rewrite→retry-on-3 loop from a shared base → final file contains **all N** updates, zero lost. **Run against a CRLF fixture** (not LF) to exercise B1. **Non-vacuity by mutation**: strip the CAS base-check (unconditional write) → N−1 updates lost → FAIL → revert (the slice-092/094/095 mutation discipline). The mid-slice smoke gate references THIS file.
- `tests/methodology/test_skill_vault_write_safety_audit.py` — update the APED-1 battery (critique m1 — FBCD-1 grep `deferred-rmw` across the file; ≥3 functions break on the enum removal): a `vault_edit rewrite`-routed RMW site → CLEAN; **an RMW site citing `append` → VIOLATION (channel-mismatch, B2 non-vacuity)**; a `deferred-rmw` marker → now VIOLATION (unknown reason); `test_exempt_reasons_are_closed` (`:313`) → assert enum == `{project-open-single-shot}`; `test_exempted_site_is_clean` (`:83`) → re-point to a `rewrite`-routed CLEAN site; `test_count_pin_trips_on_extra_marker_on_listed_file` (`:299`) → re-point to a `project-open-single-shot` (listed) file; `test_exemption_allowlist_pinned` total 12 → 3.

## What's reused

- `tools/_vault_write.py` — `_file_lock` (sidecar `.lock` + cross-platform `msvcrt`/`fcntl`; [[ADR-085]]) and `safe_write_text`'s temp+`os.replace`+EPERM-retry body. `safe_rewrite_text` is `safe_write_text` + a base-compare precondition INSIDE the same lock — it does not re-implement the lock or the replace.
- `tools/vault_edit.py` — `_resolve_in_vault` (the `VAULT_ROOT` containment guard, slice-095 m3), `_read_content`, the argparse/exit-code/`_stdout` scaffolding. The `rewrite` subparser is additive to the existing `append` subparser.
- `tools/_vault_paths.py` — `VAULT_ROOT` ([[ADR-065]]+[[ADR-085]]) so the CAS channel honors the future flip transparently.
- `tools/_stdout.py` — `reconfigure_stdout_utf8()` (UTF8-STDOUT-1) — already used by both tools (RSAD-1: a vault-infra tool must not ship its own cp1252 crash, N≥8).
- SVW-1's detection model, route-token + exemption-enum + per-(file,reason)-count allowlist machinery ([[ADR-087]], slice-095) — this slice tightens it (retires `deferred-rmw`), does not rebuild it.
- The "narrow, don't force-retire" pattern — slice-084/085/094/095. R-32 stays `mitigating`.

## The skill-driven RMW mutator set (code-grounded enumeration)

The 9 sites currently `<!-- vault-write-safe: deferred-rmw -->` exempt (pinned in `_REGISTERED_SKILL_EXEMPTIONS`, confirmed by `grep`):

| Skill | Site(s) | What it does | Op class | This slice |
|-------|---------|--------------|----------|------------|
| `/reflect` | `:56` | risk-register in-place status flip (mitigating→retired) | **RMW** | route → `vault_edit rewrite` (CAS) |
| `/reflect` | `:321` | `_index.md` — Active-remove + recent-10 prepend + Aggregated-lessons prepend | **RMW** | route → `vault_edit rewrite` (CAS) |
| `/reflect` | `:322` | `archive/_index.md` chronological catalog | append-or-regen | classify at build: append→`vault_edit append`, regen→`rewrite` |
| `/archive` | `:27`/`:58`/`:75`/`:131`/`:177` | full regen of `_index.md` (recent-10/Active/lessons) + `archive/_index.md` from all slice folders | **RMW (full regen)** | route → `vault_edit rewrite` (CAS) |
| `/supersede-slice` | `:103` | `_index.md` — mark one archived slice's row superseded | **RMW** | route → `vault_edit rewrite` (CAS) |

The `_index.md` recent-10 rewrite is the **exact scenario R-32 was opened for** (two concurrent slice completions both rewriting recent-10, one row silently lost) — slice-095 design.md §51 calls it the PRIMARY lost-update hazard. CAS closes it: writer A commits; writer B's lock-time base-compare fails → B re-reads (now sees A's row) → re-prepends → commits. Both rows land; nothing silently lost.

**Out of the RMW set (unchanged):** the `project-open-single-shot` sites (`/discover:113`, `/risk-spike:148`, `/triage:179`) — single-shot project-lifecycle writes, never run twice in parallel; stay exempt. The append-class sites slice-095 already routed (`/reflect` lessons/shippability/methodology-changelog/risk-register-new-entry, `/reduce`, `/repro`, `/validate-slice`, `/user-test`) — already `vault_edit append`, untouched. `/triage:163` stays fence-hidden (the separate, still-deferred triage-markdown bug; NOT this slice).

## Components touched

### `tools/_vault_write.py` — `safe_rewrite_text` (NEW function)
- **Responsibility**: a lost-update-safe whole-file write — write the new content only if the target still matches the base the caller read, under the sidecar lock; else raise so the caller can re-read and retry.
- **Lives at**: `tools/_vault_write.py` (modified — additive function).
- **Key interactions**: `_file_lock`, `os.replace`/`os.O_BINARY` (reused), a new `StaleVaultBaseError` (subclass of `OSError` or a dedicated exception — build picks; must be catchable distinctly so `vault_edit` maps it to exit 3, not 2).

### `tools/vault_edit.py` — `rewrite` subcommand (NEW)
- **Responsibility**: give Claude a CAS channel to safely apply an LLM-authored whole-file rewrite of a shared-aggregate vault file.
- **Lives at**: `tools/vault_edit.py` (modified — additive subparser).
- **CLI contract**: `rewrite --file <vault-rel> --base-file <path> (--content-file <path> | --stdin)`. Exit 0/2/3 (see §Error model). `append` is unchanged.
- **Key interactions**: `safe_rewrite_text`, `_resolve_in_vault`, `_stdout`. Invoked by `/reflect`, `/archive`, `/supersede-slice` prose.

### `tools/skill_vault_write_safety_audit.py` — RMW enforcement (MODIFIED)
- **Responsibility**: make an un-routed skill-driven RMW site un-mergeable (was: deferrable via `deferred-rmw`).
- **Change**: route token `+vault_edit rewrite`; `_EXEMPT_REASONS −deferred-rmw`; allowlist −3 rows (total 12→3). Detection model, fence tracking, negation look-back, fail-closed-for-recognized-sites scope (M2 residual) — all unchanged. The honest-scope ceiling (static prose audit cannot observe runtime obedience — the R-2 class, [[ADR-029]]) is unchanged and re-stated.

## Contracts added or changed

None in the HTTP/event/schema sense. One CLI contract added: `vault_edit rewrite` (exit 0/2/3 — the new exit-3 CAS-conflict code is the only novel surface; `append` 0/2 unchanged). `safe_append_text`/`safe_write_text` signatures unchanged; `safe_rewrite_text` is a new function.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| — (no NEW module; this slice adds a function to `_vault_write.py` + a subcommand to `vault_edit.py` + edits the SVW-1 audit, all existing files) | — | — | zero-row matrix — rationale: no new module introduced; new behavior on existing modules is covered by `test_vault_safe_write.py` (safe_rewrite_text), `test_skill_vault_write_safety_concurrency.py` (CAS proof), and `test_skill_vault_write_safety_audit.py` (enforcement) |

(WIRE-1 treats a header-only/zero-row matrix as clean. The new code lives in already-wired modules; its consumers are the existing skills + the existing test suite.)

## Decisions made (ADRs)

- [[ADR-088]] — Close the skill-driven RMW lost-update class via compare-and-swap (`vault_edit rewrite` over a new `safe_rewrite_text`), fail-closed on stale base; retire the SVW-1 `deferred-rmw` exemption and enforce the RMW class — reversibility: **cheap**. (Extends [[ADR-087]]'s deferred half; supersedes nothing.)

### Sub-decisions (recorded here, not ADR-worthy)

- **MEPD-1 → EXCLUDE.** No new tool MODULE (extends `vault_edit.py` + `skill_vault_write_safety_audit.py` + underscore `_vault_write.py`) → no PMI-1 inventory fan-out; no new RULE-ID (completes the existing SVW-1 rule's documented-as-deferred RMW half); no VERSION/methodology-changelog mint. Mirrors the N≥8 risk-narrowing tool-EXTENSION EXCLUDE lineage (077/079/082/084/085/086/087/092/093/096) AND is the parallel-safety-optimal shape (no MCFS-1/AVFS-1/TVFS-1 forward-sync fan-out → no R-28 contention). The SVW-1 scope-completion (deferred-rmw retired) is recorded in ADR-088 + the risk-register R-32 update, not a changelog RULE entry.
- **CAS retry is bounded.** The skill's read→rewrite→retry loop has a bounded cap (fail-VISIBLE STOP after the cap, R-7) so pathological livelock under sustained contention surfaces loudly rather than spinning. Concurrent reflect-completions in the same window are rare; the common path is one attempt.
- **`deferred-rmw` removed from the enum, not zeroed in the allowlist.** Removing the reason makes a future `deferred-rmw` marker a hard `unknown-exemption-reason` VIOLATION (stronger than an empty allowlist entry, which would silently accept the reason). The deferral is structurally un-re-claimable.
- **Install forward-sync of the 3 edited SKILLs.** `reflect` is OSDG-1-guarded (in-repo ≡ installed drift test) → its install MUST sync (and BEFORE this slice's own `/reflect` runs, so the routed prose is what executes — the slice-096 R-28 face-(b) lesson). `archive` + `supersede-slice` are NOT drift-guarded but their installs sync too for runtime correctness. No active parallel slice now (stranded audit clean) → no R-28 contention this time.

## /critique round — fixes applied (B3, M3, docstring)

### B3 — `/archive` CAS protocol across the Haiku-subagent boundary
`skills/archive/SKILL.md:58-67` dispatches `_index.md` + `archive/_index.md` regeneration to a Haiku subagent (`subagent_type: general-purpose`, `model: haiku`) that *returns* the content while "the main thread writes them to disk". The read→transform→write→retry loop assumes one agent, so the protocol is specified explicitly: **the MAIN THREAD owns the CAS** — it (1) captures the base (tool-mediated raw read of each target), (2) dispatches Haiku with the base + templates, (3) receives the regenerated content, (4) calls `vault_edit rewrite --base-file <base> --content-file <regen>`, (5) on exit-3 **re-captures the base AND re-dispatches Haiku** (so the regeneration picks up the concurrent writer's row), bounded by `_REWRITE_RETRY_MAX`. The Haiku subagent is a pure content generator with no lock/CAS responsibility. (The only realistic race is a manual `/archive` co-occurring with `/reflect`'s auto-archive; the protocol holds regardless.)

### M3 — `reflect:56` single-field status flip: trade-off on record
`risk-register.md` is confirmed CRLF (137KB) → under B1's EOL contract. The `:56` "status flip" is a single-field in-place edit, yet routed through a whole-file CAS rewrite. This deliberately accepts a **heavier-than-necessary whole-file rewrite** for the single-field case rather than build a bespoke structured set-field (the Option-2 path ADR-088 rejected wholesale). Recorded here so the simplicity/uniformity trade-off is explicit, not silent — a future slice MAY add a structured `set-risk-status` if the whole-file churn proves costly.

### Docstring parity (Critic Dim-1)
`tools/vault_edit.py:9-13` docstring states "`rewrite` is deliberately NOT exposed". The build MUST update that docstring to describe the now-exposed CAS `rewrite` subcommand (else a stale-doc / OSDG-1-adjacent finding at `/code-review`).

## /critique-review round — fixes applied (B-add-1, M-add-1, m-add-1/2/3)

### B-add-1 (Blocker) — the op-class discriminator MUST sever the bare-`tools.vault_edit` flat-OR path
The meta-Critic caught that "op-class-aware" (B2) is not closed by merely adding `"vault_edit rewrite"` to `_SAFE_ROUTE_TOKENS`: `_is_routed` (`skill_vault_write_safety_audit.py:267-273`) returns True on the FIRST un-negated token hit, and the bare `"tools.vault_edit"` token (`:121-123`) substring-matches ANY subcommand — so a rewrite-class site citing `` `tools.vault_edit append` `` (or `$PY -m tools.vault_edit append`) is cleaned by the bare token BEFORE any op-class logic runs. **Buildable discriminator (the mechanism, locked here):**
1. **Retire the bare `tools.vault_edit` as a standalone clean signal.** A route reference must NAME a subcommand to be op-class-classifiable. Replace the bare token with subcommand-bearing recognition: APPEND-class tokens `{vault_edit append, safe_append_text}`; REWRITE-class tokens `{vault_edit rewrite, safe_rewrite_text}` (each matched with or without a `tools.`/`$PY -m ` prefix, inside a code span or `<!-- route: -->` marker, per the existing `_ROUTE_IN_CODESPAN_RE`/`_ROUTE_MARKER_RE` machinery + the negation look-back).
2. **Classify the cited route's op-class** (APPEND vs REWRITE vs none-named).
3. **Verdict (asymmetric — only the UNSAFE direction is a violation):** a **rewrite-class directive verb** (`regenerate`/`rewrite`/in-place-edit) is CLEAN only with a REWRITE-class route; an APPEND-class route (or a route that names no subcommand) on it → **channel-mismatch VIOLATION** (fail-closed). An **append-class verb** is CLEAN with EITHER route (a rewrite channel is lost-update-safe for an append too — heavier, not unsafe). 
4. **APED-1 proof the bare-token path is severed:** the adversarial positive uses the REAL corpus citation form — a `Regenerate _index.md` line citing `` `$PY -m tools.vault_edit append` `` MUST be VIOLATION (not merely a `<!-- route: ... append -->` marker), proving the bare-`tools.vault_edit` substring no longer rides through. Honest residual unchanged: an RMW op phrased with an append-class verb, or an unclassifiable verb, can still mis-route — the documented lexical ceiling. **Disposition: ACCEPTED-PENDING** (mechanism specified now; audit code + the bare-token-severance adversarial proof execute at build — it is the load-bearing must-not-defer item, not "done" until proven).

### M-add-1 (Major) — `_normalize_eol` contract pinned: CRLF→LF ONLY, all other bytes preserved
`_normalize_eol` maps `\r\n → \n` and touches **nothing else** — trailing newlines, final-line-without-newline, and interior content bytes are preserved verbatim. So base="…row\n" vs current="…row" (a genuine concurrent truncation) compares **UNEQUAL** → CAS conflict → fail-closed (NOT a silent overwrite — the dangerous direction M-add-1 flags). And a pure CRLF↔LF representation flip compares EQUAL → no false-conflict (the B1 direction). The `test_skill_vault_rewrite_concurrency.py` + `test_vault_safe_write.py` unit coverage MUST assert BOTH directions: (a) CRLF-base ≡ LF-base (no false conflict), (b) trailing-newline-delta ⇒ conflict (no silent lost-update). **Disposition: ACCEPTED-PENDING** (contract pinned now; both-direction tests execute at build).

### m-add-1 (Minor) — reflect:322 classified NOW: `archive/_index.md` chronological catalog = APPEND
Decided at design (not punted to build): reflect:322 appends one chronological row to `archive/_index.md` → route via the existing `vault_edit append` (APPEND-class). Under B-add-1's asymmetric verdict an append-verb + append-route is CLEAN. The build's first classification check CONFIRMS the prose is append-shaped (not a full regen); if it is a full regen, it routes via `vault_edit rewrite` instead — but the default decision is append. **Disposition: ACCEPTED-FIXED.**

### m-add-2 (Minor) — this slice's own `/reflect` is a deliberate live-fire test of the new CAS channel
Because `reflect/SKILL.md` is OSDG-1-guarded and its install forward-syncs before this slice's own `/reflect` runs, slice-097's reflection step is the FIRST production exercise of `vault_edit rewrite` CAS against the real 309KB CRLF `_index.md` (a bootstrap/self-host edge, slice-088/PFS-1 class). The build treats it as a live-fire test: after this slice's `/reflect`, verify `_index.md` byte-integrity — specifically **no CRLF→LF churn** (re-run the CRLF byte-check) — rather than assume it. The mid-slice smoke gate (subprocess + CRLF fixture) is the earlier backstop. **Disposition: ACCEPTED-FIXED.**

### m-add-3 (Minor) — `/archive` retry-exhaustion leaves a recoverable state
On `_REWRITE_RETRY_MAX` exhaustion mid-`/archive`, the Step-2 `mv` has ALREADY moved the slice folder to `slices/archive/` (before the Step-3 regen). The fail-STOP is recoverable: `/archive --index-only` re-runs the index regeneration without re-moving. The build documents this in the `/archive` retry prose (the fail-VISIBLE STOP message names `--index-only` as the recovery path). Re-dispatching Haiku ~5× re-reads ~10-N folders each — a cost multiplier under genuine contention, accepted (contention is rare; correctness > latency). **Disposition: ACCEPTED-FIXED.**

## Authorization model for this slice

Not applicable — local build/skill tooling, no auth/authz surface. Per the cooperative model ([[ADR-067]]): vault-write-safety is a **data-integrity control, not a security boundary**. CAS defends two cooperating parallel slices on one machine from silent lost-update, not a malicious actor.

## Error model for this slice

- `safe_rewrite_text`: returns on success; raises `StaleVaultBaseError` on base-mismatch (the retryable signal); inherits `safe_write_text`'s `PermissionError` (EPERM-exhausted) / `TimeoutError` (lock-acquire) runtime model.
- `vault_edit rewrite`: exit **0** (written) / **2** (usage — bad/escaping `--file`, missing content/base; fail-VISIBLE) / **3** (CAS conflict — base changed; re-read + retry). Exit-3 is distinct from 2 so prose branches retry-vs-abort.
- `skill_vault_write_safety_audit`: exit **0** clean / **1** ≥1 unrouted/unexempted/unknown-reason site / **2** usage. Fail-closed unchanged; a `deferred-rmw` marker now lands in the exit-1 set.

## R-32 disposition (planned here; recorded fully at /reflect)

This slice closes the **skill-driven RMW** sub-class — the third and final write-safety sub-class of R-32 (Python-writer = slice-094/VWS-1; skill-append = slice-095/SVW-1; skill-RMW = this slice). With all three closed, the **entire write/append/rewrite axis** of R-32 is enforced on both the Python and skill paths.

**R-32 NARROWS, it does not RETIRE.** Per the R-32 register entry, R-32 "retires only when BOTH the Python-writer AND skill-driven-append sub-classes have merged AND the RMW residual is closed *at the flip*." The silent-corruption hazard is a property of the SHARED MUTABLE store, which does not exist until the flip's physical move + git-untrack. So after this slice **no write-safety sub-class remains open**. At `/reflect`: keep R-32 `mitigating`, record the RMW sub-class closed-with-evidence, and **(critique m2)** re-state the remaining residual EXPLICITLY as **"route/retire the 3 git-coupled tools (`parallel_conflict_resolver` + `stranded_slice_audit` + `pulse_worktree_resolver`) + physical move of `architecture/` + git-untrack decision + prose rewrite"** — NOT collapsed to a bare "flip mechanics" that silently drops the 3 git-coupled tools (which are out-of-scope here, folded into the flip's design per the mission-brief). Pre-flip (Critic m1, slice-095): every shared-aggregate vault file is still git-tracked ([[ADR-066]]) so `/commit-slice` PCR resolves conflicts loudly — this slice's CAS is the structural replacement readied for when the flip removes that backstop.

**Honest residual (unchanged by this slice):** SVW-1 is a static prose audit — it proves the SKILL.md prose *prescribes* the CAS channel; it cannot observe Claude invoking raw `Write`/`Edit` at runtime in violation of correct prose (the R-2 class, [[ADR-029]]). Runtime obedience rests on the cooperative model + the wrapper actually being used, not on this audit. Documented, not a deliverable.
