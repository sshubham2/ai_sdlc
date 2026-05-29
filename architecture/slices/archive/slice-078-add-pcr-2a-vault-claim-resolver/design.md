# Design: Slice 078 add-pcr-2a-vault-claim-resolver

**Date**: 2026-05-29
**Mode**: Standard

## What's new

- Public library API `tools.parallel_conflict_resolver.resolve_vault_claim_conflict(diag, repo_root=None)` — returns a `ResolutionResult` (existing dataclass) for `ConflictClass.VAULT_CLAIM` input: timestamp-winner identity preserved on `architecture/slice-queue.md`; loser's candidate name auto-re-picked from queue's highest-priority unclaimed NON-OVERLAPPING entry; appends audit-trail row via existing `_append_audit_log` helper (header-and-section-shape unchanged).
- Private helpers (file-local; no consumer beyond `resolve_vault_claim_conflict` + tests):
  - `_collect_same_candidate_different_identity(claim_history) → list[tuple[str, ClaimEntry, ClaimEntry]]` — enumerates EVERY same-candidate-different-identity collision in `claim_history` (returns list, not just bool). `_has_same_candidate_different_identity` becomes a thin `bool(_collect_...)` wrapper preserving the existing `classify_conflict` consumer's API.
  - `_select_timestamp_winner(collisions)` — input is the list from `_collect_...`; on len > 1 returns `("multi-candidate", ...)` sentinel for the resolver to translate into STOP (Error model below); on len == 1 returns `(winner_entry, loser_entry)` keyed by strictly-newer `Claimed-at`. **Strict-newer rule** — equal timestamps fall-closed to `ResolutionResult(action="STOP", conflict_class=VAULT_CLAIM, reason="claimed_at-tie deferred to PCR-2b")` per M1 honest framing (the strict-newer rule auto-resolves the dominant non-tie case; ties defer because `_now_iso8601_utc()` writes second-precision timestamps at `tools/slice_queue_claim.py:630` — a ~1-second tie window is plausible for racing claims). Predicate exercised by APED-1 battery.
  - `_pick_loser_replacement(queue_text: str, exclude_names: set[str])` — applies the filter against the supplied `queue_text` string (NOT disk-read per M-add-2 ACCEPTED-FIXED): highest-priority candidate whose `Parallel-safety: NON-OVERLAPPING` AND `Claimed-by:` field-line is absent AND name not in `exclude_names`. Returns `None` (audit-row sentinel `none-available`) when no candidate satisfies. **Signature rationale**: the caller (Resolution algorithm step 4) passes the post-overlay in-memory `overlaid` string from step 3, NOT the on-disk `architecture/slice-queue.md` which contains git's `<<<<<<<` conflict markers during VAULT_CLAIM rebase-in-progress. **Parser**: uses a NEW file-local helper `_parse_queue_candidates_for_replacement(text) → list[tuple[name, parallel_safety, is_claimed]]` defined in `tools/parallel_conflict_resolver.py` (per B1 ACCEPTED-FIXED — neither `tools/slice_queue_writer.py` exposes a queue-text parser nor `tools.slice_queue_claim.parse_queue_text` returns `Parallel-safety`). The new helper is regex-based + file-order-preserving; tested independently of resolver via in-memory text fixtures.
- Audit-row formatter `_format_vault_claim_audit_entry(diag, winner, loser, replacement)` extends `_append_audit_log`'s shape with a NEW section heading `## Vault-claim resolution - <ISO-8601 UTC>` (hyphen-space separator — UNIFORM with PCR-1 SOFT row per M2 ACCEPTED-FIXED; the section-type distinction lives in the prefix word `Vault-claim` vs `Soft-conflict`, NOT the trailing dash decoration — pollution-resistant per slice-075 RSAD-1 lesson). Reuses the `_append_audit_log` single-open `O_APPEND` pattern (fix m6 / code-review from slice-076 — no rewrite, no TOCTOU regression).
- Test modules:
  - `tests/methodology/test_pcr_2a_vault_claim_resolver.py` (AC#1, 4 tests — timestamp-winner, loser-skip-claimed, loser-skip-non-parallel-safe, none-available)
  - `tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py` (AC#2, 2 tests — dispatch hits resolver, UNKNOWN still fail-closed)
  - `tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py` (AC#3, 2 tests — sub-step 2.5 prose-pin + forward-sync)
  - `tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py` (AC#4, 2 tests — row format + append-only)
  - `tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py` (AC#5, 2 tests — pre-fix raise + post-fix ResolutionResult)
- ADR-071 (this slice) — mint **PCR-2a** vault-claim auto-resolution sub-mechanism.
- methodology-changelog v0.74.0 entry — RULE-ID **PCR-2a** (refines PCR-1's class taxonomy; supersedes nothing); both-bidirectional PMI-1 pins per RPCD-1.
- Shippability row #N (next free) — wires the AC#5 regression test as a never-silently-regress assertion.

## What's reused

- `tools/parallel_conflict_resolver.py` ([[slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen]]):
  - `ConflictDiagnostic`, `ClaimEntry`, `ResolutionResult` dataclasses (added at slice-076; no schema change required)
  - `ConflictClass.VAULT_CLAIM` enum value
  - `classify_conflict()` — VAULT_CLAIM gate at lines 200-213 already correctly returns VAULT_CLAIM (no change)
  - `_regen_slice_queue()` — defense-in-depth gate at lines 627-638; PCR-2a replaces its `raise _SoftResolutionError(VAULT_CLAIM)` leg with a dispatch into `resolve_vault_claim_conflict(diag, repo_root)` (4-line change; UNKNOWN-class raise leg at L605-609 untouched)
  - `resolve_soft_conflict()` — wrapper at lines 242-253; PCR-2a adds a NEW VAULT_CLAIM dispatch branch ABOVE the existing `if cls is not ConflictClass.SOFT:` guard at L243 (per B3 ACCEPTED-FIXED — the CLI path through `--resolve-soft` calls this function FIRST; without the branch, L243 short-circuits VAULT_CLAIM to STOP before `_regen_slice_queue` is reached). New branch shape: `if cls is ConflictClass.VAULT_CLAIM: return resolve_vault_claim_conflict(diag, repo_root)`.
  - `_append_audit_log()` at lines 842-917 (single-open `O_APPEND` pattern reused verbatim; dispatched based on `result.conflict_class` to either the existing SOFT row formatter or the new `_format_vault_claim_audit_entry`)
- `tools/slice_queue_claim.py` ([[slice-072-add-psq-2-claim-machinery]]):
  - `parse_queue_text()` — Claimed-by/Claimed-at field-line parser (no change; explicitly NOT used for `Parallel-safety` reading — slice_queue_claim.py:229-234 strips PSQ-1 known fields including Parallel-safety per B1)
- `tools/slice_queue_writer.py` ([[slice-067-add-parallel-slice-queue-output]]):
  - `write_slice_queue` + `format_queue_md` + `compute_parallel_safety` (read-only references; PCR-2a does NOT widen `slice_queue_writer`'s public API per B1 ACCEPTED-FIXED — the parser used by `_pick_loser_replacement` is a NEW file-local helper inside `parallel_conflict_resolver.py`, not a new public function on `slice_queue_writer`)
- `skills/commit-slice/SKILL.md` sub-step 2.5 PCR-1 dispatch block at lines 185-192 ([[slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen]]) — prose-edit per M3 ACCEPTED-FIXED structural-pin specification: L185 dispatch paragraph gains a sentence pinning `VAULT_CLAIM` in APPLIED context (co-occurs with `auto-resolves`); L192 closing summary DROPS `VAULT_CLAIM` from the fall-closed-to-SOAD-1 enumeration. The resolver wrapper code change above is the load-bearing infrastructure delivering `action="APPLIED"` to the CLI consumer.
- [[ADR-069]] — PCR-1 design § Forward references explicitly nominates PCR-2 for vault-claim resolution; PCR-2a is the first leg.

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: Add VAULT_CLAIM-class auto-resolution path. Today the module classifies + resolves SOFT only; PCR-2a extends the resolution coverage to VAULT_CLAIM via timestamp-winner.
- **Lives at**: `tools/parallel_conflict_resolver.py` (modified — adds `resolve_vault_claim_conflict()` + 4 private helpers + audit-row formatter; modifies `resolve_soft_conflict()` dispatch + `_regen_slice_queue()` raise leg)
- **Key interactions**: reads `architecture/slice-queue.md` via the new file-local `_parse_queue_candidates_for_replacement` helper + `tools.slice_queue_claim.parse_queue_text` (claim-block parse for unclaimed-detection only); writes `architecture/parallel-conflict-resolution-log.md` (audit trail); invokes `git rebase --continue` via `subprocess.run` (existing pattern at line 312-318).

### `skills/commit-slice/SKILL.md` (modified)
- **Responsibility**: Sub-step 2.5 dispatch prose update — VAULT_CLAIM no longer falls through to SOAD-1 STOP; the existing `exit 0 + action: APPLIED` branch now covers VAULT_CLAIM as well as SOFT.
- **Lives at**: `skills/commit-slice/SKILL.md` lines 185-192 (PCR-1 dispatch block) — surgical edit moving "VAULT_CLAIM" mention from the STOP enumeration to the APPLIED enumeration; lines 192's "PCR-2 (slice-077)" forward-reference rewritten to "PCR-2a (slice-078 / VAULT_CLAIM auto-resolution) shipped; PCR-2b (slice-079) will ship HARD + TRI-RESOLVE-1".
- **Key interactions**: forward-sync to `~/.claude/skills/commit-slice/SKILL.md` via existing OSDG-1 mini-CAD pattern (ADR-033 EOL-agnostic content equality).

### `architecture/parallel-conflict-resolution-log.md` (extended — schema additive)
- **Responsibility**: Audit trail of every PCR resolution event. PCR-1 introduced `## Soft-conflict resolution - <ISO>` sections; PCR-2a adds a sibling `## Vault-claim resolution - <ISO>` section type (UNIFORM hyphen-space separator per M2 ACCEPTED-FIXED — the section-type distinction lives at the prefix word `Vault-claim` vs `Soft-conflict`; uniform separator avoids Windows smart-dash autocorrect collision).
- **Lives at**: `architecture/parallel-conflict-resolution-log.md` — file is **absent on disk as of slice-078 build start** (PCR-1's `_append_audit_log` lazy-creates on first append; no soft-conflict has been resolved in production yet). Lazy-create logic at L913 carries over for the first append of EITHER section type.
- **Key interactions**: append-only contract enforced by `_append_audit_log`'s `open("a")` pattern; AC#4 test 2 seeds a synthesized SOFT-section row before triggering the VAULT_CLAIM append (mixed-section append-only test — exercises lazy-create-on-first-of-each-section behavior).

## Contracts added or changed

### `resolve_vault_claim_conflict(diag, repo_root=None) → ResolutionResult` (new public API)
- **Defined in code at**: `tools/parallel_conflict_resolver.py` (function signature + docstring + APED-1-tested predicates `_select_timestamp_winner` and `_pick_loser_replacement` referenced via wiring matrix below)
- **Inputs**: `ConflictDiagnostic` (existing dataclass; `claim_history: tuple[ClaimEntry, ...]` field is the load-bearing input — both branches' claims captured at PCR-1 `diagnose_conflict` time); optional `repo_root: Path` defaulting to `Path.cwd()` (test injection)
- **Outputs**: `ResolutionResult` (existing dataclass) with `action="APPLIED"`, `conflict_class=ConflictClass.VAULT_CLAIM`, `regenerated_files=("architecture/slice-queue.md",)`, `reason=None` on success; `action="STOP"` paths enumerated under Error model below
- **Auth model**: identity-as-claim per [[ADR-067]] PSQ-2 cooperative-not-adversarial threat model — no auth mediation, no impersonation check; loser is the staler `Claimed-at` regardless of identity (winner could be anyone; PCR-2a does not promote or demote identity).
- **Error cases**: enumerated in Error model section below.

### Sub-step 2.5 SKILL.md dispatch contract (extended)
- **Endpoint**: prose at `skills/commit-slice/SKILL.md:185-192` — `python -m tools.parallel_conflict_resolver --resolve-soft --json` is the load-bearing CLI invocation
- **Pre-PCR-2a behavior**: VAULT_CLAIM → `action="STOP", conflict_class=VAULT_CLAIM` → falls into SOAD-1 3-option block (b-option manual resolution)
- **Post-PCR-2a behavior**: VAULT_CLAIM → `action="APPLIED", conflict_class=VAULT_CLAIM, regenerated_files=("architecture/slice-queue.md",)` → breadcrumb to build-log + skip SOAD-1 (same code path as SOFT today)
- **No CLI flag change**: `--resolve-soft` is preserved as the existing flag name; resolver internally dispatches on `classify_conflict()` result. *(Renaming to `--resolve-auto` is deferred to bundled cleanup — bikeshed.)*

## Data model deltas

### `architecture/slice-queue.md` (no schema change; existing PSQ-2 format preserved)
- **Format**: `## Candidates` → `### <candidate-name>` blocks; field-lines `**Source:**`, `**Blast-radius:**`, `**Parallel-safety:**`, `**Effort:**`, `**Risk-retired:**`, optional `**Claimed-by:**`, `**Claimed-at:**`
- **Reader**: `tools.slice_queue_writer.parse_queue_md` (existing) + `tools.slice_queue_claim.parse_queue_text` (existing)
- **Write**: PCR-2a's `_pick_loser_replacement` is **read-only** on the queue — it does NOT modify `Claimed-by` for the replacement. Claim assignment for the replacement happens via the existing `tools.slice_queue_claim --claim <name>` CLI invoked by the loser's user OUT-OF-BAND after they see the audit log. *(Auto-claim of replacement deferred to PCR-2b / slice-079 to keep PCR-2a's blast-radius bounded; failing-fast on out-of-band claim is cooperative-acceptable per ADR-067.)*

### `architecture/parallel-conflict-resolution-log.md` (additive — new section type)
- **New section**: `## Vault-claim resolution - <ISO-8601 UTC>` (UNIFORM hyphen-space separator per M2 ACCEPTED-FIXED; lazy-created on first vault-claim event)
- **Body fields** (markdown bold field-lines, mirroring `## Soft-conflict resolution`):
  - `**Repo HEAD SHA pre-resolution**:` `<git rev-parse HEAD>` or `(unavailable)`
  - `**Candidate name**:` `<name>` (the same-candidate-different-identity name)
  - `**Winner Claimed-by**:` `<git-name> <git-email>`
  - `**Winner Claimed-at**:` `<ISO-8601 UTC>`
  - `**Loser Claimed-by**:` `<git-name> <git-email>`
  - `**Loser Claimed-at**:` `<ISO-8601 UTC>`
  - `**Loser auto-re-pick**:` `<candidate-name>` OR `none-available` (sentinel — queue has no NON-OVERLAPPING unclaimed candidate)
  - `**Resolution actions**:` bulleted — `` - `architecture/slice-queue.md` — claim assignment preserved for winner ``

## Wiring matrix

Per WIRE-1.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `resolve_vault_claim_conflict` (new public function in `tools/parallel_conflict_resolver.py`) | `tools/parallel_conflict_resolver.py::resolve_soft_conflict` VAULT_CLAIM dispatch branch (new, above L243 guard) AND `tools/parallel_conflict_resolver.py::_regen_slice_queue` defense-in-depth dispatch (replaces existing raise leg at L633-638) AND `skills/commit-slice/SKILL.md` sub-step 2.5 (user-facing CLI invocation) | `tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py::test_resolve_soft_conflict_dispatches_vault_claim_into_pcr_2a` + `test_regen_slice_queue_dispatches_into_vault_claim_resolver` | — |
| `_collect_same_candidate_different_identity` (file-local helper) | `_select_timestamp_winner` (same file) + `_has_same_candidate_different_identity` (existing predicate becomes a thin `bool(...)` wrapper) | `tests/methodology/test_pcr_2a_vault_claim_resolver.py::test_multi_candidate_collision_returns_stop` | — |
| `_select_timestamp_winner` (file-local helper) | `resolve_vault_claim_conflict` (same file) | `tests/methodology/test_pcr_2a_vault_claim_resolver.py::test_timestamp_winner_when_newer_in_stage_3` + `test_timestamp_winner_when_newer_in_stage_2` + `test_claimed_at_tie_returns_stop` (APED-1-style direct predicate exercise) | — |
| `_parse_queue_candidates_for_replacement(text)` (file-local helper; in-memory text input) | `_pick_loser_replacement` (same file) | `tests/methodology/test_pcr_2a_vault_claim_resolver.py::test_no_available_when_queue_empty` + `test_no_available_when_all_overlapping` + `test_no_available_when_all_claimed` (predicate parses queue text and surfaces per-candidate `name` + `parallel_safety` + `is_claimed`; APED-1-executed against the actual `architecture/slice-queue.md` shape) | — |
| `_pick_loser_replacement(queue_text, exclude_names)` (file-local helper; in-memory text per M-add-2) | `resolve_vault_claim_conflict` (same file; called with `queue_text=overlaid` from Resolution algorithm step 3) | `tests/methodology/test_pcr_2a_vault_claim_resolver.py::test_loser_auto_re_pick_skips_claimed_candidates` + `test_loser_auto_re_pick_skips_non_parallel_safe_candidates` + `test_pick_loser_replacement_reads_resolved_text_not_disk` (fixture: disk holds conflict-marker'd text + in-memory holds resolved overlay; assert helper returns disk-ignored result) | — |
| `_format_vault_claim_audit_entry` (file-local helper) | `_append_audit_log` (same file; vault-claim branch) | `tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py::test_vault_claim_event_row_format` + `test_log_is_append_only_across_section_types` | — |

## Decisions made (ADRs)

- [[ADR-071]] — Mint PCR-2a vault-claim auto-resolution via timestamp-winner + read-only loser-replacement-suggestion — reversibility: **cheap** (single audit-row format addition; resolver-leg dispatch swap; SKILL.md prose edit; behaviorally additive — pre-PCR-2a fallthrough to SOAD-1 is restorable by reverting 3 small commits)

## Resolution algorithm for VAULT_CLAIM (per M4 ACCEPTED-FIXED)

`resolve_vault_claim_conflict(diag, repo_root=None)` executes the following steps. **Critical invariant**: the strictly-newer winner's identity is written onto the resolved queue regardless of which stage held the newer claim — without this step the `_regen_slice_queue` baseline-from-stage-3 default at `parallel_conflict_resolver.py:614` would silently DEMOTE a winner whose newer claim resides in stage 2 (the slice's own branch).

1. **Collect collisions**: `collisions = _collect_same_candidate_different_identity(diag.claim_history)`. If `len(collisions) > 1`, return `ResolutionResult(action="STOP", conflict_class=VAULT_CLAIM, reason="multi-candidate VAULT_CLAIM collision — sequential auto-resolution deferred to PCR-2b")`. If `len(collisions) == 0`, return `ResolutionResult(action="STOP", conflict_class=UNKNOWN, reason="VAULT_CLAIM dispatch without same-candidate-different-identity claim collision — diag/class disagree, fail-closed")`.
2. **Select winner**: `winner, loser = _select_timestamp_winner(collisions[0])`. If `winner.claimed_at == loser.claimed_at` (strict-newer tie), return `ResolutionResult(action="STOP", conflict_class=VAULT_CLAIM, reason="claimed_at-tie deferred to PCR-2b — strict-newer rule yields no winner")`.
3. **Read baseline + overlay winner**: `text_3 = _git_show_stage(repo_root, 3, "architecture/slice-queue.md")`; `text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")`; `baseline_text = text_3 or text_2` (mirrors `_regen_slice_queue:614`). Apply `overlaid = _overlay_claims_on_queue_text(baseline_text, {winner.candidate_name: {"claimed_by": winner.claimed_by, "claimed_at": winner.claimed_at}})` — re-uses PCR-1's existing overlay helper. **Post-overlay defensive verification (M-add-1 ACCEPTED-FIXED)**: per PCR-1's `_overlay_claims_on_queue_text:687` silent-drop semantics (candidate's queue-text block lacking `- **Risk-retired:**` post-emit pivot → claim silently dropped with stderr-loud-but-APPLIED), defensively verify the winner's claim made it into the overlaid text via `re.search(rf'### {re.escape(winner.candidate_name)}.*?Claimed-by:\*\* {re.escape(winner.claimed_by)}', overlaid, re.S)`. If the regex fails to match, return `ResolutionResult(action="STOP", conflict_class=VAULT_CLAIM, reason="overlay-silently-dropped — candidate block missing Risk-retired pivot; manual intervention required")` — converts the loud-stderr-but-still-APPLIED case into fail-closed STOP, preserving M4's strict-newer-wins contract integrity.
4. **Pick loser-replacement (read-only, in-memory)**: `replacement = _pick_loser_replacement(queue_text=overlaid, exclude_names={winner.candidate_name})` per M-add-2 ACCEPTED-FIXED. **Reads from step 3's in-memory `overlaid` string** — NOT from `architecture/slice-queue.md` on disk, which during VAULT_CLAIM rebase-in-progress contains git's `<<<<<<<` / `=======` / `>>>>>>>` conflict markers around `slice-queue.md` (the U-file). Disk-read would silently parse only the non-conflicted portion of the queue and return `none-available` for almost every real-world scenario, silently degrading AC#1's resolution quality. May return `None` (sentinel for audit-row `none-available`). No write to queue's `Claimed-by`/`Claimed-at` for the replacement — defers to PCR-2b per ADR-071 §Decision.
5. **Atomic write + stage + continue**: write resolved queue text via the stage-then-commit pattern from PCR-1 SOFT (`pending_writes` list, atomic `write_text(content, encoding="utf-8", newline="")` then `git add architecture/slice-queue.md` then `git rebase --continue`). On stage / rebase-continue failure, return `ResolutionResult(action="STOP", conflict_class=VAULT_CLAIM, reason="git rebase --continue failed post vault-claim resolution: <stderr>")` per Error model below.
6. **Audit-log append (best-effort)**: invoke `_append_audit_log` with the `ResolutionResult` carrying `conflict_class=VAULT_CLAIM`; `_append_audit_log` dispatches on the class to the new `_format_vault_claim_audit_entry` formatter. OSError is caught + stderr-printed without changing the APPLIED result (matches PCR-1 SOFT contract).
7. **Return**: `ResolutionResult(action="APPLIED", conflict_class=VAULT_CLAIM, regenerated_files=("architecture/slice-queue.md",), reason=None)`.

The defense-in-depth `_regen_slice_queue()` raise leg at L633-638 is reshaped to dispatch into step (3)+ of this algorithm directly (already inside the helper's overlay context). The CLI-facing `resolve_soft_conflict()` L242 entry calls `resolve_vault_claim_conflict()` BEFORE the existing SOFT branch — these are two independent entry points; both lead to step 1 of the algorithm above.

## Authorization model for this slice

- VAULT_CLAIM resolution is **identity-agnostic**: the winner is whichever `Claimed-at` is strictly newer (cooperative threat model per [[ADR-067]] § Threat model — no adversarial claim-backdating mitigation in v1).
- The loser's auto-re-pick is a **suggestion**, not a write — `_pick_loser_replacement` reads the queue but does NOT claim the replacement on behalf of the loser; the loser observes the audit log and claims out-of-band via the existing `tools.slice_queue_claim --claim <name>` CLI. *(Rationale: claim-on-behalf would require the loser's `git user.email` to be derivable from the queue text alone — which it IS via the `Claimed-by:` field — but the auto-claim then introduces a race window with the loser's actual session, where the loser may have ALREADY claimed a different candidate concurrently. Deferring to PCR-2b keeps PCR-2a's blast-radius bounded.)*
- No auth mediation, no audit-log redaction.

## Error model for this slice

`resolve_vault_claim_conflict` returns `ResolutionResult(action="STOP", ...)` (NOT raises) for the enumerated failure cases below, to preserve atomicity discipline established by PCR-1's SOFT path:

| Condition | conflict_class | reason field |
|-----------|----------------|--------------|
| Equal `Claimed-at` timestamps on the collision pair (tie) | VAULT_CLAIM | `claimed_at-tie deferred to PCR-2b — strict-newer rule yields no winner` |
| `diag.claim_history` has no same-candidate-different-identity pair (caller misuse — class is VAULT_CLAIM but diag content disagrees) | UNKNOWN | `VAULT_CLAIM dispatch without same-candidate-different-identity claim collision — diag/class disagree, fail-closed` |
| Multiple same-candidate-different-identity collisions in one `diag` (>1 candidate name in conflict) | VAULT_CLAIM | `multi-candidate VAULT_CLAIM collision — sequential auto-resolution deferred to PCR-2b` |
| Post-overlay defensive regex (Resolution algorithm step 3) fails to find winner's claim in `overlaid` (silent-drop per M-add-1) | VAULT_CLAIM | `overlay-silently-dropped — candidate block missing Risk-retired pivot; manual intervention required` |
| `git rebase --continue` fails after stage + audit-log append | VAULT_CLAIM | `git rebase --continue failed post vault-claim resolution: <subprocess stderr>` (mirrors SOFT path lines 319-328) |
| Audit-log append OSError | VAULT_CLAIM | best-effort per `_append_audit_log` contract; resolver still returns `action="APPLIED"` with stderr-printed warning (no STOP — audit is non-blocking by design.md §Error model from slice-076) |

The defense-in-depth `_regen_slice_queue` UNKNOWN-class raise leg at lines 605-609 is **NOT modified** — only the VAULT_CLAIM raise leg at lines 632-638 is swapped to a dispatch call. UNKNOWN remains fail-closed.

## Acceptance criteria mapping (cross-ref to mission-brief)

| AC | Code location | Test |
|----|--------------|------|
| 1 | `tools/parallel_conflict_resolver.py::resolve_vault_claim_conflict` + `_collect_same_candidate_different_identity` + `_select_timestamp_winner` + `_pick_loser_replacement` + `_parse_queue_candidates_for_replacement` | `tests/methodology/test_pcr_2a_vault_claim_resolver.py` (9 tests covering stage-2/stage-3 winners, 3 none-available branches, tie, multi-collision, 2 skip-filter cases) |
| 2 | `tools/parallel_conflict_resolver.py::resolve_soft_conflict` L242-253 (new VAULT_CLAIM dispatch branch above L243 guard) + `_regen_slice_queue` L627-638 (raise → dispatch swap) | `tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py` (3 tests: both dispatch sites + UNKNOWN-still-fail-closed) |
| 3 | `skills/commit-slice/SKILL.md` L185-192 (APED-1-executed prose pins on both L185 dispatch paragraph + L192 closing summary) | `tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py` (3 tests: L185 in-APPLY pin + L192 NOT-in-fall-closed pin + OSDG-1 forward-sync) |
| 4 | `tools/parallel_conflict_resolver.py::_format_vault_claim_audit_entry` + `_append_audit_log` class-dispatch extension; section heading `## Vault-claim resolution - <ISO>` (hyphen-space uniform with SOFT per M2) | `tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py` (2 tests: row format + mixed-section append-only seeded with synthesized prior SOFT row) |
| 5 | Catalogued post-fix regression repro asserting `_regen_slice_queue` returns `(Path, str)` instead of raising `_SoftResolutionError(VAULT_CLAIM)`; FAIL→PASS contrast captured empirically in build-log.md Events at pre-build/post-build SHAs | `tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py::test_vault_claim_gate_closed_returns_resolution_result` (single PASS-post-fix function per slice-024 / slice-014 precedent) — added as shippability row #N |
