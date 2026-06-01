# Critique: Slice 097 harden-skill-driven-vault-rewrites

**Critic reviewed**: mission-brief.md, design.md, ADR-088, project-frame.md; on-disk: `tools/_vault_write.py`, `tools/vault_edit.py`, `tools/skill_vault_write_safety_audit.py`, the three SKILL.md files, `test_skill_vault_write_safety_audit.py`, `test_skill_vault_write_safety_concurrency.py`, `test_vault_write_safety_concurrency.py`, `test_vault_safe_write.py`, `architecture/risk-register.md`, `.gitattributes`, the on-disk `_index.md`
**Date**: 2026-06-01
**Result**: BLOCKED (Critic's assessment — final verdict computed at Triage)

## Summary

The CAS mechanism is sound in the abstract and the 12→3 / 9-site arithmetic checks out exactly against the real allowlist and tree. But two executed checks surface correctness blockers the design hand-waves: (B1) the on-disk `_index.md` is **CRLF** while `safe_rewrite_text` inherits LF-only writes, so a byte-exact base-comparison will permanently false-conflict on the very file R-32 was opened for; and (B2) the audit cannot distinguish a `rewrite`-routed RMW site from one wrongly citing the lost-update-UNSAFE `append` channel — both read CLEAN — the exact false-confidence trap the must-not-defer forbids. (B3) the `/archive` Haiku-dispatch flow puts the read+transform in a subagent and the write in the main thread, so the read→rewrite→retry protocol has no coherent home.

**Builder note (independent verification)**: B1 confirmed (`_index.md` CRLF 309KB; `risk-register.md` CRLF 137KB; `.gitattributes` does NOT normalize `architecture/**` and explicitly scopes whole-vault renormalization OUT per slice-033 → fix-option (c) is wrong, must use EOL-normalized compare + EOL-preserving write). B2 confirmed (`_is_routed` flat-OR; `tools.vault_edit` substring already cleans any subcommand). B3 confirmed (`archive/SKILL.md:65` "agent returns ... Main thread writes them to disk"). m1 confirmed (`deferred-rmw` enum removal breaks `:83`, `:299`, `:313`). Zero false alarms.

## Findings

### Blockers

#### B1: CAS byte-exact base-comparison vs CRLF `_index.md` will permanently false-conflict
- **Claim under review**: design.md §What's new — "read current target bytes → if `current == expected_base` ... `newline=""` + `os.O_BINARY` byte-faithfulness inherited from `safe_write_text`." must-not-defer: "Byte-faithfulness: LF preserved, no CRLF corruption."
- **Issue**: `architecture/slices/_index.md` is **CRLF** on disk (309KB; verified), `risk-register.md` likewise (137KB). `.gitattributes` pins only `skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md` to `eol=lf` — `architecture/**` is unnormalized, so these vault aggregates legitimately live as CRLF. A byte-exact CAS compares `current_disk(CRLF) == expected_base`; the skill obtains its base via the `Read`/`Get-Content` path (LF-normalized) and `safe_rewrite_text` writes LF (`newline=""`). So (a) the base is LF, never byte-equal to CRLF on disk → `StaleVaultBaseError` on attempt 1, every time → bounded retry re-reads the same CRLF → cap exhausted → fail-VISIBLE STOP: the RMW channel is **unusable on the one file R-32 exists for**; and (b) if a write did land, it churns the file CRLF→LF (309KB EOL corruption on an unguarded surface — EOL-DRIFT-1).
- **Evidence**: `read_bytes` CRLF check (309783 / 137733 bytes); `.gitattributes` (no `architecture/` rule, "whole-vault renormalization explicitly out of slice-033 scope"); `_vault_write.py:108` (`newline=""`), `:147` (`O_BINARY`).
- **Proposed fix (Critic)**: decide+document the base-comparison normalization contract before build. Options (a) raw-bytes base [still churns], (b) EOL-normalize both sides for comparison AND preserve the target's existing EOL on write [no corruption], (c) renormalize `architecture/` to LF via `.gitattributes` [one-time churn]. APED-1-execute the chosen path against the *real* CRLF `_index.md`.
- **Builder draft**: **ACCEPTED-PENDING** — adopt option (b): `safe_rewrite_text` reads current raw bytes, compares EOL-normalized (CRLF≡LF) so representation never false-conflicts, and writes preserving the target's detected EOL (detect-and-match, no churn). Option (c) is rejected — `.gitattributes:` explicitly scopes whole-vault renormalization OUT of slice-033, and reversing that is out of THIS slice's scope. Design.md + ADR-088 updated this round to specify the contract; the implementation + APED-1 execution against the real CRLF `_index.md` AND `risk-register.md` lands at `/build-slice` (mid-slice smoke gate runs against the real CRLF file, not an LF fixture).

#### B2: SVW-1 cannot distinguish `rewrite`-routing from `append`-routing — an RMW site citing the UNSAFE `append` channel reads CLEAN
- **Claim under review**: AC3 "fail-closed-flags an un-routed RMW site"; must-not-defer #1 "NOT a per-call append masquerading as a rewrite"; design.md "add `vault_edit rewrite` to `_SAFE_ROUTE_TOKENS`".
- **Issue**: `_is_routed` (`:255-274`) is a flat OR over `_SAFE_ROUTE_TOKENS`, which already contains `"tools.vault_edit"` (a substring of every invocation) AND `"vault_edit append"`. A planted RMW site `Regenerate _index.md <!-- route: tools.vault_edit append -->` returns routed/CLEAN. So the audit cannot enforce that an RMW site uses `rewrite` — the "append masquerading as a rewrite" trap, promoted to the audit layer. AC3's non-vacuity test ("strip the route token → VIOLATION") proves only that *some* token is required, not the *correct* one. Adding `"vault_edit rewrite"` is partly cosmetic (the `tools.vault_edit` substring already cleans a `rewrite` citation).
- **Evidence**: `skill_vault_write_safety_audit.py:121-123, :255-274, :277-290`; executed battery (RMW-site-citing-append → routed=True).
- **Proposed fix (Critic)**: make the audit op-class-aware for RMW sites, OR explicitly downgrade AC3's claim + document the residual (mirror the R-2 honest-scope note). APED-1-execute an RMW-site-citing-append fixture.
- **Builder draft**: **ACCEPTED-PENDING** — make the audit op-class-aware to the lexically-determinable degree: a site whose directive verb is **rewrite-class** (`regenerate`/`rewrite`/in-place-edit phrasing) that cites only an `append`-class route token → VIOLATION (channel-mismatch). This catches the Critic's exact planted case. AND document the honest residual (an RMW operation phrased with an append-class verb, or an unclassifiable verb, can still mis-route — the lexical ceiling, mirroring SVW-1's existing M2 residual + R-2 note). AC3 + design.md corrected this round to claim op-class-aware-where-determinable + a pinned residual, NOT unconditional channel-correctness. Audit logic + the RMW-cites-append APED-1 fixture land at build.

#### B3: `/archive` regenerates `_index.md` via a Haiku SUBAGENT — the read+CAS+retry loop has no home in the main thread
- **Claim under review**: design.md routes `archive/SKILL.md :27/:58/:75/:131/:177` "→ `vault_edit rewrite` (CAS) with the read→rewrite→retry-on-exit-3 protocol".
- **Issue**: `archive/SKILL.md:58-67`: index regeneration is dispatched to a Haiku subagent; "The agent returns both `_index.md` files' content. Main thread writes them to disk." The transform (full regen from slice folders) is in the subagent's context; the main thread only writes. On an exit-3 CAS conflict the main thread cannot simply retry — it must re-dispatch Haiku. The "read→rewrite→retry" protocol assumes reader/transformer/writer are the same agent in one turn; the archive flow violates that.
- **Evidence**: `skills/archive/SKILL.md:58-67`; design.md §What's new (routes all 5 archive sites uniformly with no mention of the subagent boundary).
- **Proposed fix (Critic)**: specify the archive CAS protocol across the subagent boundary (main reads base → dispatches Haiku → Haiku returns content → main `vault_edit rewrite --base-file <base>` → on exit-3, main re-reads base AND re-dispatches Haiku, bounded), OR argue concurrent `/archive` doesn't realistically co-occur.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §`/archive` subagent protocol — the MAIN THREAD owns the base-capture + the `vault_edit rewrite` call + the bounded retry loop; the Haiku subagent is purely the content generator. On exit-3 the main thread re-captures the base AND re-dispatches the Haiku regeneration (so the re-gen sees the concurrent writer's row). Also note: a concurrent `/archive` + auto-`/reflect`-archive is the only realistic race, but the protocol holds regardless.

### Majors

#### M1: concurrency proof must be multiprocessing-spawn/subprocess + barrier, not the thread-based GIL-masked sibling
- **Claim under review**: AC4 / verification-plan #1: "`test_skill_vault_write_safety_concurrency.py` (or a new sibling)"; mid-slice smoke runs that file.
- **Issue**: the named `test_skill_vault_write_safety_concurrency.py` uses `ThreadPoolExecutor` (`:54`) + a `time.sleep(0.002)` window-widener (`:79`) — the GIL-masked regime. The authoritative R-32 discipline is `multiprocessing(spawn)` + `mp.Barrier` (`test_vault_write_safety_concurrency.py:35-40`; slice-094 lesson) because an un-barriered pool staggers ~100ms/worker and never overlaps.
- **Evidence**: `test_skill_vault_write_safety_concurrency.py:54,79`; `test_vault_write_safety_concurrency.py:35-40`; slice-094 aggregated lesson.
- **Proposed fix (Critic)**: commit to subprocess (`vault_edit rewrite`) workers released by a shared barrier, CAS retry loop per worker, mutation arm = CAS-check stripped → ≥1 lost. Name the concrete file.
- **Builder draft**: **ACCEPTED-FIXED** at design.md — a NEW `tests/methodology/test_skill_vault_rewrite_concurrency.py` (not the thread sibling): N concurrent `$PY -m tools.vault_edit rewrite` **subprocesses** released by a shared barrier (`mp.Barrier` via a manager, or a file-presence spin), each running the read→rewrite→retry-on-3 loop; non-vacuity by mutation (strip the CAS base-check → ≥1 lost → FAIL → revert). The mid-slice smoke gate references THIS file, not `test_skill_vault_write_safety_concurrency.py`.

#### M2: the "exact bytes I read" base-capture is unspecified
- **Claim under review**: design.md CLI `rewrite ... --base-file <bytes-I-read>`; ADR-088 "its bytes still equal the base the skill read."
- **Issue**: the upstream cause of B1. Claude reads via the `Read` tool (`cat -n`-formatted, EOL-normalized) — not raw bytes. `vault_edit.py:69-72` `_read_content` uses `read_text(encoding="utf-8")` (universal-newlines → LF). There is no described path for the skill to capture+pass byte-exact base.
- **Evidence**: design.md §vault_edit CLI; `vault_edit.py:69-72`.
- **Proposed fix (Critic)**: specify the capture mechanism (a tool-mediated snapshot returning a token/hash, OR a documented raw-byte dump + binary `--base-file` read).
- **Builder draft**: **ACCEPTED-FIXED** at design.md (jointly with B1) — the base is captured tool-mediated: `vault_edit` emits the current file's content for the skill to edit (a `read`/`snapshot` mode), and `--base-file` is read in **binary** (`newline=""`/`rb`), NOT universal-newlines. Combined with B1's EOL-normalized comparison, the skill may pass LF base safely. Exact sub-command ergonomics are a build-plan detail; the contract (tool-mediated raw capture + EOL-normalized compare) is locked.

#### M3: confirm `risk-register.md` EOL + record the whole-file-rewrite trade-off for the single-field `reflect:56` status flip
- **Claim under review**: design.md §RMW-mutator-set: "`/reflect` `:56` risk-register in-place status flip — RMW — route → `vault_edit rewrite`".
- **Issue**: `reflect:56` is a single-field status flip; a whole-file CAS rewrite of `risk-register.md` (CRLF, large) is heavier than a structured set-field (the Option-2 path ADR-088 rejected wholesale, but which fits THIS one site). The trade-off should be on record, and risk-register.md's EOL confirmed (it's under B1).
- **Evidence**: `skills/reflect/SKILL.md:56`; ADR-088 §Options.
- **Proposed fix (Critic)**: confirm risk-register.md EOL; note the uniform-CAS accepts a heavier-than-necessary whole-file rewrite for the single-field case so the trade-off is explicit.
- **Builder draft**: **ACCEPTED-FIXED** at design.md — risk-register.md confirmed CRLF (137KB), so it is under B1's EOL contract. Recorded explicitly: uniform-CAS deliberately accepts a heavier whole-file rewrite for the single-field `:56` flip (rather than build a bespoke set-field) — the simplicity/uniformity trade-off ADR-088 chose, now on the record rather than silent.

### Minors

#### m1: test-update plan omits the enum-closure + deferred-rmw-planting tests that the removal will break
- **Claim under review**: design.md test-update list (mentions only the allowlist pin 12→3).
- **Issue**: removing `deferred-rmw` from `_EXEMPT_REASONS` breaks `test_exempt_reasons_are_closed` (`:313`, hard-asserts the enum), `test_exempted_site_is_clean` (`:83`, plants a deferred-rmw marker), `test_count_pin_trips_on_extra_marker_on_listed_file` (`:299`, plants two). The design's list omits all three.
- **Evidence**: `test_skill_vault_write_safety_audit.py:83, :299-310, :313-315`.
- **Proposed fix (Critic)**: enumerate EVERY `deferred-rmw` test site; grep `deferred-rmw` across the test file (FBCD-1).
- **Builder draft**: **ACCEPTED-FIXED** at design.md — test-update list expanded to name `test_exempt_reasons_are_closed`, `test_exempted_site_is_clean`, `test_count_pin_trips_on_extra_marker_on_listed_file`; build greps `deferred-rmw` across the test file (FBCD-1) so no stale plant survives. These re-point to a `rewrite`-routed CLEAN case + the new op-class-mismatch VIOLATION (B2).

#### m2: R-32 residual-list update must preserve the 3 git-coupled tools, not collapse to "flip mechanics only"
- **Claim under review**: design.md §R-32 disposition: "update the residual list to 'flip mechanics only'".
- **Issue**: the live R-32 residual list (slice-094 entry) has 5 items incl. the 3 git-coupled tools (`parallel_conflict_resolver`/`stranded_slice_audit`/`pulse_worktree_resolver`). "Flip mechanics only" silently drops them.
- **Evidence**: risk-register.md R-32 entry; mission-brief Out-of-scope.
- **Proposed fix (Critic)**: at /reflect re-state residual as "3 git-coupled tools + physical move + git-untrack + prose rewrite".
- **Builder draft**: **ACCEPTED-FIXED** at design.md §R-32 disposition — residual re-stated as "the 3 git-coupled tools (route/retire) + physical move + git-untrack + prose rewrite," not collapsed.

## Dimensions checked
- [x] Unfounded assumptions — B1 (byte-faithfulness "inherited" fails vs real CRLF), M2 (base-capture asserted, undefined). Also: `vault_edit.py:9-13` docstring still says "rewrite is deliberately NOT exposed" — build MUST update it (stale-doc).
- [x] Missing edge cases — B3 (Haiku-subagent boundary breaks read-transform-write-retry).
- [x] Over-engineering — none (uniform-CAS justified; reflect:56 set-field trade-off noted in M3, not over-build).
- [x] Under-engineering — B2 (AC3 claims enforcement the audit can't deliver), m1 (test-update plan incomplete).
- [x] Contract gaps — `--base-file` byte-exactness unspecified (M2); exit-3 retry cap "bounded" but unnumbered — name it.
- [x] Security — none (data-integrity control, not a boundary; ADR-067; path containment reused).
- [x] Drift from vault — m2 (R-32 residual accuracy). MEPD-1 EXCLUDE verified correct; ADR-088 supersedes nothing, correctly extends ADR-087. Strategic-direction fit: squarely on the VWS/SVW trajectory.
- [x] Web-known issues — skipped (no novel external surface; in-house file-locking + CAS).
- [x] Cross-cutting conformance — APED-1 executed (route-token battery + B2 false-CLEAN reproduced); docstring-vs-impl parity flagged (vault_edit.py:9-13); count-pin verified by execution (12 exemptions), not arithmetic.

## Triage

**Triaged by**: user
**Date**: 2026-06-01
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes — the first Critic (B1–m2) and the meta-Critic (B-add-1, M-add-1, m-add-1/2/3, in critique-review.md). Dual-review verdict: EXTEND (zero suspicious / 5 missed / 0 severity adjustments). User ratified all dispositions as drafted.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | EOL-normalized compare + EOL-preserving write (option b; option c rejected — slice-033 scopes whole-vault renorm OUT). Contract in design.md §What's-new + ADR-088; built + APED-1-proven vs the real CRLF `_index.md` AND `risk-register.md` at /build-slice |
| B2 | Blocker | ACCEPTED-PENDING | Op-class-aware audit; subsumed + completed by B-add-1's buildable discriminator |
| B3 | Blocker | ACCEPTED-FIXED | design.md §B3 — main thread owns CAS capture/dispatch/write/retry; re-dispatches Haiku on exit-3; Haiku is a pure content generator |
| B-add-1 | Blocker | ACCEPTED-PENDING | design.md §B-add-1 — retire the bare `tools.vault_edit` standalone-clean token; classify the cited subcommand; asymmetric verdict (rewrite-verb + append-route → VIOLATION); adversarial bare-token-severance proof at build (load-bearing must-not-defer item) |
| M1 | Major | ACCEPTED-FIXED | NEW `test_skill_vault_rewrite_concurrency.py` (subprocess + barrier, CRLF fixture, mutation arm); mid-slice gate references it, not the thread sibling |
| M2 | Major | ACCEPTED-FIXED | Tool-mediated raw base capture + binary `--base-file`; joint with B1 (design.md §What's-new) |
| M3 | Major | ACCEPTED-FIXED | risk-register.md CRLF confirmed (under B1 contract); whole-file-rewrite-for-single-field trade-off on record (design.md §M3) |
| M-add-1 | Major | ACCEPTED-PENDING | `_normalize_eol` = CRLF→LF ONLY, trailing/other bytes preserved → trailing-newline truncation is a genuine conflict, never a silent overwrite; both-direction tests at build (design.md §M-add-1 + ADR-088) |
| m1 | Minor | ACCEPTED-FIXED | Test-update list enumerates `test_exempt_reasons_are_closed`/`test_exempted_site_is_clean`/`test_count_pin_trips...`; FBCD-1 grep `deferred-rmw` (design.md §What's-new) |
| m2 | Minor | ACCEPTED-FIXED | R-32 residual re-stated explicitly with the 3 git-coupled tools (design.md §R-32 disposition) |
| m-add-1 | Minor | ACCEPTED-FIXED | reflect:322 decided = APPEND (`vault_edit append`); build confirms append-shape as first classification check (design.md §m-add-1) |
| m-add-2 | Minor | ACCEPTED-FIXED | This slice's own `/reflect` is a deliberate live-fire test; post-reflect `_index.md` byte-integrity check (no CRLF→LF churn) (design.md §m-add-2) |
| m-add-3 | Minor | ACCEPTED-FIXED | `/archive` retry-exhaustion recoverable via `--index-only` (Step-2 `mv` already done); documented in the retry prose (design.md §m-add-3) |
