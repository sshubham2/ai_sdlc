# Slice 078: add-pcr-2a-vault-claim-resolver

**Mode**: Standard
**Estimated work**: ~0.5–1 day (SMALL-MEDIUM)
**Risk retired**: residual R-21 (PCR-1 corner-case) reduced + closes the parallel-conflict-resolution VAULT_CLAIM class structurally (PCR-1 left this class diagnosed-but-unresolved by design — see [[ADR-069]] § Forward references)
**Test-first**: true <!-- per TF-1 — feature/mechanism slice; failing repro for AC#5 written BEFORE the dispatch wire-in; APED-1 battery on minted predicates -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Mint **PCR-2a** (parallel-conflict-resolution v2a — vault-claim sub-mechanism), closing the VAULT_CLAIM class auto-resolution gap left open by PCR-1 (slice-076 / [[ADR-069]]). Today `classify_conflict()` returns `ConflictClass.VAULT_CLAIM` and `_regen_slice_queue()`'s defense-in-depth gate raises `_SoftResolutionError(VAULT_CLAIM)` — forcing user STOP for the simplest "two parallel sessions claimed the same candidate at different times" scenario. PCR-2a adds `resolve_vault_claim_conflict()` (timestamp-winner: newer `Claimed-at` wins; loser auto-re-picks the next-priority NON-OVERLAPPING unclaimed candidate from `architecture/slice-queue.md`), wires it into `/commit-slice --merge` sub-step 2.5 conflict-class dispatch, and appends a per-event row to `architecture/parallel-conflict-resolution-log.md`. HARD-conflict resolution + TRI-RESOLVE-1 user triage are explicitly **deferred to slice-079** (PCR-2b) per the split decision recorded in /slice (2026-05-28).

## Acceptance criteria

1. `tools.parallel_conflict_resolver.resolve_vault_claim_conflict(diag, repo_root=None)` returns a `ResolutionResult` whose preserved identity is the entry with the strictly-newer `Claimed-at` ISO-8601 timestamp — REGARDLESS of which stage (2=ours/slice-branch OR 3=rebase-target) holds the winner. The loser's name is auto-re-picked via `_pick_loser_replacement(queue_text=overlaid, exclude_names={winner.candidate_name})` from the **post-overlay in-memory queue text** produced by Resolution algorithm step 3 (per M-add-2 ACCEPTED-FIXED — NOT from `architecture/slice-queue.md` on disk, which during VAULT_CLAIM rebase-in-progress holds git conflict markers) — highest-priority unclaimed `Parallel-safety: NON-OVERLAPPING` candidate; returns `None` (audit sentinel `none-available`) when no candidate satisfies. Step 3 carries a defensive post-overlay `re.search` for the winner's claim in the overlaid text per M-add-1 ACCEPTED-FIXED — if the regex fails to match (silent-drop on malformed candidate block missing `Risk-retired:` pivot), returns `ResolutionResult(action="STOP", ...)` rather than ship a silently-stale claim.
2. **Both** the user-facing dispatch site `resolve_soft_conflict()` at `tools/parallel_conflict_resolver.py:242-253` AND the defense-in-depth backstop `_regen_slice_queue()` at L627-638 dispatch `ConflictClass.VAULT_CLAIM` into `resolve_vault_claim_conflict()` instead of returning STOP / raising `_SoftResolutionError(VAULT_CLAIM)`. PCR-1's UNKNOWN-class fail-closed branch at `_regen_slice_queue()` L605-609 remains intact (no scope-creep removing the safety net). The CLI `--resolve-soft` path (L986-1007) → SKILL.md L185 invocation therefore returns `action="APPLIED"` for VAULT_CLAIM.
3. `skills/commit-slice/SKILL.md` sub-step 2.5 prose pinned by APED-1-executed structural pins (in-repo + installed forward-synced; mini-CAD-style by `tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py`):
   - **Pin #1** (L185 dispatch paragraph): the line containing `VAULT_CLAIM` MUST co-occur with `auto-resolves` (or APPLIED-bound synonym) — asserts the dispatch logic mentions VAULT_CLAIM in APPLIED context.
   - **Pin #2** (L192 closing summary): the enumeration of classes "falling-closed-to-SOAD-1 STOP" MUST NOT contain bare `VAULT_CLAIM` — assert via `re.search(r"VAULT_CLAIM[^\n]+fall[- ]closed", L192)` returns None; VAULT_CLAIM instead appears in an "auto-resolved by PCR-2a" sentence.
   - APED-1 execution: each pin regex pre-tested against synthetic positive + negative on the actual L185-192 prose BEFORE the test commits (per slice-074 aggregated lesson).
4. Every VAULT_CLAIM auto-resolution event appends a `## Vault-claim resolution - <ISO-8601 UTC>` section (hyphen-space separator — uniform with PCR-1 SOFT row per M2) to `architecture/parallel-conflict-resolution-log.md` capturing: Repo HEAD SHA pre-resolution, candidate name, winner `Claimed-by` + `Claimed-at`, loser `Claimed-by` + `Claimed-at`, loser auto-re-pick name (or `none-available`), resolution actions bullet list; format pinned by `tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py` (append-only, loss-free). Test 2 seeds a synthesized prior SOFT-section row before triggering the VAULT_CLAIM append (mixed-section append-only test — exercises lazy-create of second section-type given the file is absent on disk as of slice-078 build start).
5. Catalogued post-fix regression repro `tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py::test_vault_claim_gate_closed_returns_resolution_result` PASSes post-build (asserts `_regen_slice_queue()` returns a tuple `(Path, str)` after PCR-2a dispatch instead of raising `_SoftResolutionError(VAULT_CLAIM)` — exercises the actual gate-closure on the real implementation). The pre-fix → post-fix FAIL→PASS contrast is captured empirically in `build-log.md` Events at pre-build / post-build SHAs (NOT as a separate test function — per slice-024 / slice-014 precedent). Shippability row #N added per RPCD-1 / SCPD-1 pins the post-fix PASS as the never-silently-regress assertion.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_timestamp_winner_when_newer_in_stage_3 | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_timestamp_winner_when_newer_in_stage_2 | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_loser_auto_re_pick_skips_claimed_candidates | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_loser_auto_re_pick_skips_non_parallel_safe_candidates | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_no_available_when_queue_empty | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_no_available_when_all_overlapping | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_no_available_when_all_claimed | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_claimed_at_tie_returns_stop | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_multi_candidate_collision_returns_stop | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_overlay_silently_dropped_returns_stop | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_vault_claim_resolver.py | test_pick_loser_replacement_reads_resolved_text_not_disk | PASSING |
| 2 | integration | tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py | test_resolve_soft_conflict_dispatches_vault_claim_into_pcr_2a | PASSING |
| 2 | integration | tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py | test_regen_slice_queue_dispatches_into_vault_claim_resolver | PASSING |
| 2 | integration | tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py | test_unknown_class_still_fail_closed | PASSING |
| 3 | unit | tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py | test_substep_2_5_l185_pins_vault_claim_in_apply_block | PASSING |
| 3 | unit | tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py | test_substep_2_5_l192_drops_vault_claim_from_fall_closed_enumeration | PASSING |
| 3 | unit | tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py | test_in_repo_and_installed_forward_synced | PASSING |
| 4 | unit | tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py | test_vault_claim_event_row_format | PASSING |
| 4 | unit | tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py | test_log_is_append_only_across_section_types | PASSING |
| 5 | regression | tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py | test_vault_claim_gate_closed_returns_resolution_result | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `resolve_vault_claim_conflict()` correctness across stage-2/stage-3 winner + 3 none-available branches + tie + multi-collision + overlay-silently-dropped STOP + in-memory-text disk-ignore | `$PY -m pytest tests/methodology/test_pcr_2a_vault_claim_resolver.py -v` — all 11 unit tests PASS |
| 2 | `resolve_soft_conflict()` AND `_regen_slice_queue()` both dispatch into PCR-2a; UNKNOWN-class still fail-closed | `$PY -m pytest tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py -v` — all 3 PASS |
| 3 | SKILL.md sub-step 2.5 APED-1-pinned dispatch + forward-synced | `$PY -m pytest tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py -v` — all 3 PASS; OSDG-1 mini-CAD drift check exit 0 |
| 4 | Log row format + append-only across SOFT + VAULT_CLAIM section-types | `$PY -m pytest tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py -v` — both PASS |
| 5 | Post-fix regression repro PASSes + FAIL→PASS contrast captured in build-log + shippability row added | `$PY -m pytest tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py::test_vault_claim_gate_closed_returns_resolution_result` PASSes post-build; build-log.md Events records pre-build SHA where this test FAILed (raising) and post-build SHA where it PASSes (returning); new shippability row #N PASS in `$PY -m tools.shippability_runner architecture/shippability.md` |

## Must-not-defer

- [ ] Defense-in-depth UNKNOWN-class fail-closed at `_regen_slice_queue()` MUST be preserved verbatim — PCR-2a removes ONLY the VAULT_CLAIM raise leg; the `_SoftResolutionError(UNKNOWN)` raise leg stays exactly as-is (regression-pinned in AC#2 second test).
- [ ] Loser-auto-re-pick MUST NOT silently return a candidate that is (a) already claimed by anyone, or (b) `Parallel-safety` != `NON-OVERLAPPING`. Both branches exercised by AC#1 tests 2 + 3.
- [ ] `architecture/parallel-conflict-resolution-log.md` MUST be append-only — no row mutation, no rewrite (AC#4 test 2 asserts byte-equality of prior rows after a new event appends).
- [ ] Audit-trail row MUST be loss-free even when re-pick returns `none-available` — the sentinel is captured, not swallowed.
- [ ] Methodology-changelog v0.74.0 entry minted with RULE-ID **PCR-2a** + entry-pin test function `tests/methodology/test_methodology_changelog.py::test_v_0_74_0_pcr_2a_entry_present_in_repo_and_installed` AND PMI-1 4-part atomic bump: (a) `VERSION` 0.73.0 → 0.74.0; (b) `~/.claude/ai-sdlc-VERSION` matching; (c) `plugin.yaml` `version:` matching; (d) forward-synced `~/.claude/methodology-changelog.md` content-equal modulo EOL. RPCD-1 bidirectional pins.
- [ ] R-22 risk-register entry added — "Cross-machine clock-skew in PCR-2a strict-newer rule producing wrong-winner-by-staleness" (low likelihood / low impact; reversibility: cheap; status: open) — corrigibility-detection hook per m9 ACCEPTED-PENDING.
- [ ] Queue candidate `add-claim-sequence-number-for-clock-skew-detection` appended to slice-queue.md (read-only registration; SP-1 candidate slot).
- [ ] ADR-071 minted (anchor reserved by next-free check 2026-05-28): "Mint PCR-2a vault-claim auto-resolution" — references [[ADR-069]] as parent.
- [ ] OSDG-1 forward-sync for `skills/commit-slice/SKILL.md` (in-repo ↔ installed content-equal modulo EOL per [[ADR-033]]).

## Out of scope

- HARD-conflict resolution (slice-079 PCR-2b) — `ResolutionResult` for `ConflictClass.HARD` still RETURNS `_SoftResolutionError(HARD)` unchanged from PCR-1.
- TRI-RESOLVE-1 user triage gate mirroring TRI-1 for resolution dispositions (slice-079 PCR-2b).
- MIXED partial-resolution (slice-079+ per [[ADR-069]] § Forward references).
- Cross-machine claim-race hardening when both worktrees push concurrently — last-write-wins on `architecture/slice-queue.md` is still an R-21 corner case; deferred to `cross-worktree-race-hardening` slice candidate (queue entry).
- Spawning the design-Critic / meta-Critic agents on a proposed resolution — that infra arrives in PCR-2b. PCR-2a's vault-claim resolution is mechanical (no LLM Critic invocation), keeping the slice SMALL.
- Refactoring `tools/parallel_conflict_resolver.py` for code-Critic cleanup of m5 (UNKNOWN WARN-text under-implementation, deferred per slice-077 reflection) — that lands in `bundle-077-code-critic-cleanup`.

## Dependencies

- Prior slices:
  - [[slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen]] — `ConflictClass.VAULT_CLAIM` enum, `classify_conflict()`, `_regen_slice_queue()` defense-in-depth gate, `_SoftResolutionError` carrier, `architecture/parallel-conflict-resolution-log.md` schema
  - [[slice-072-add-psq-2-claim-machinery]] — `Claimed-by` / `Claimed-at` field-line grammar in `architecture/slice-queue.md`; `tools/slice_queue_claim.py` claim/release helpers
  - [[slice-067-add-parallel-slice-queue-output]] — `architecture/slice-queue.md` format + `tools/slice_queue_writer.py`
- Vault refs: [[ADR-069]] (PCR-1 design + § Forward references → PCR-2 nomination), [[ADR-067]] (PSQ-2 claim ownership), [[components/parallel-conflict-resolver]]
- Risk register: [[risk-register#R-21]] — PCR-2a closes the VAULT_CLAIM corner-case window; HARD-class window remains for slice-079

## Mid-slice smoke gate

At ~50% of build (after `resolve_vault_claim_conflict()` core lands + AC#1 unit tests PASS, BEFORE the `_regen_slice_queue()` dispatch wire-in):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_pcr_2a_vault_claim_resolver.py -v
```

Expected: 4 PASSING (AC#1 fully green); AC#2-#5 tests still PENDING / WRITTEN-FAILING. If AC#1 false-passes (e.g., older-timestamp wins, or already-claimed candidate gets re-picked) OR if any pre-existing PCR-1 test (`tests/methodology/test_parallel_conflict_resolver_*`) regresses: STOP, diagnose, do NOT proceed to the dispatch wire-in. The dispatch wire-in compounds with the resolver — wire-in on a broken resolver silently ships a broken VAULT_CLAIM path.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` clean
- [ ] BC-PROJ-4 full methodology suite green (`$PY -m pytest tests/methodology/ -v` exit 0)
- [ ] TF-1 audit PASS (all 12 test-first rows PASSING; `$PY -m tools.test_first_audit --strict-pre-finish`)
- [ ] SCMD-1 + SRSC-1 shippability runner full sweep PASS (`$PY -m tools.shippability_runner architecture/shippability.md` exit 0; new row #N PASS)
- [ ] Mid-slice smoke still PASSes (no regression on AC#1 from later wire-in)
- [ ] No new TODOs / FIXMEs / debug prints (`$PY -m tools.todo_audit` exit 0)
- [ ] META-1 + PMI-1 + CAD-1 + OSDG-1 + RR-1 + INST-1 + BCI-1 all green
- [ ] methodology-changelog v0.74.0 entry minted with PCR-2a both-bidirectional pins
- [ ] VERSION 0.73.0 → 0.74.0 + plugin.yaml version-sync
- [ ] ADR-071 minted at `architecture/decisions/ADR-071-mint-pcr-2a-vault-claim-resolver.md`
- [ ] PSQ-1 `architecture/slice-queue.md` regenerated (top-10 candidates; slice-078 candidate removed; slice-079 PCR-2b promoted)
- [ ] Worktree-mode (BRANCH-2) audit clean per `$PY -m tools.branch_workflow_audit` Step 6

## Pipeline position

- **predecessor**: `/slice` (this skill; auto-advances from `/reflect` post-slice-077)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission-brief.md + milestone.md written; candidate settled via user pick (PCR-2 recommended → split-vote PCR-2a); auto-invoke `/design-slice`.
