# Slice 083: add-pcr-2b-hard-class-conflict-resolution

**Mode**: Standard
**Estimated work**: ~1 day (LARGE — new rule + new ADR + new TRI-RESOLVE-1 gate + commit-slice SKILL.md HARD-branch + resolver helper + audit-log section + tests + 5-part PMI-1 bump; scoped tight via gate-on-hand-resolve)
**Risk retired**: Closes the last two open conflict-classes (**HARD** + **MIXED**) in the PCR-N taxonomy, which PCR-1 ([[ADR-069]]) and PCR-2a ([[ADR-071]]) both explicitly reserved for "PCR-2b". No risk-register ID is directly retired — but this ships the **deferred remediation venue** named as primary/secondary fix-candidate by both [[risk-register#R-24]] (truncated-baseline) and [[risk-register#R-23]] (clock-skew): the HARD Critic stack is the place those unexpected orderings can later be flagged. R-23/R-24 stay OPEN (per /slice scope decision 2026-05-29).
**Test-first**: true  <!-- per TF-1 — mechanism slice; failing repro for the HARD-dispatch + TRI-RESOLVE-1 fail-closed predicate written BEFORE the wire-in; APED-1 battery on the minted HARD dispatch -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Mint **PCR-2b** (parallel-conflict-resolution v2b — HARD + MIXED sub-mechanism), closing the auto-resolution-story gap PCR-1 and PCR-2a left open by design. Today `classify_conflict()` returns `ConflictClass.HARD` / `ConflictClass.MIXED` and the resolver returns a bare `action="STOP"` — `/commit-slice --merge` then falls straight through to PSQ-3's SOAD-1 3-option ask with no Critic adjudication on the contested resolution. PCR-2b replaces that bare STOP for HARD/MIXED conflicts with a **gate-on-hand-resolve** flow: the user resolves the conflict markers by hand, then the **`code-review` agent** (diff-calibrated, single pass — per TRI-1 M-add-2 decision; the named `/critique` agents fail-stop on a missing `design.md`) reviews the resolved working-tree diff, then a new **TRI-RESOLVE-1** user-triage gate (mirroring TRI-1) owns the final apply decision — only a non-blocking + user-ratified resolution reaches `git rebase --continue`; anything else fail-closes to STOP. Auto-proposing a HARD merge resolution is explicitly out of scope (the rejected ADR-069 Option 2).

## Acceptance criteria

1. **PCR-2b rule minted + taxonomy refined**: new `methodology-changelog.md` v0.77.0 entry naming `PCR-2b` as the rule reference + a new ADR (number assigned at `/design-slice`) authoring the HARD/MIXED resolution-mechanism decision and the gate-on-hand-resolve choice. [[ADR-069]]'s HARD + MIXED taxonomy rows flip from "deferred to slice-077 (PCR-2)" to "shipped (PCR-2b / slice-083)" via the new ADR's refinement (append-only; ADR-069 not edited in place). 5-part PMI-1 atomic bump 0.76.0 → 0.77.0.
2. **HARD-class gate-on-hand-resolve path**: for a HARD-class conflict at `/commit-slice --merge` Step 5b sub-step 2.5, after the user hand-resolves the conflict markers, the skill runs the `code-review` agent on the resolved working-tree diff and then the TRI-RESOLVE-1 gate BEFORE `git rebase --continue`. Only a non-blocking-and-ratified resolution continues; a blocking/unratified outcome fail-closes to STOP with no `--continue` called. The pre-PCR-2b bare SOAD-1 STOP is preserved verbatim as the fallback when the resolver helper is missing/fails to import (bootstrap defense per slice-067 / ADR-064 precedent).
3. **TRI-RESOLVE-1 user-triage gate minted**: a structured-options (SOAD-1, NOT free-text) ask that makes the user the final authority on whether the proposed HARD resolution is applied (continue) or rejected (STOP / `git rebase --abort` hint). Fail-closed — no silent auto-continue path exists; an unanswered/ambiguous triage outcome resolves to STOP.
4. **MIXED-class routed through the HARD path**: a MIXED conflict (≥1 SOFT U-file + ≥1 non-SOFT U-file) routes through the HARD gate-on-hand-resolve path with NO partial SOFT auto-resolve (atomicity per [[ADR-069]] MIXED row), confirmed by the classify → dispatch wiring and a regression test.
5. **HARD audit-log section + APED-1 battery**: `architecture/parallel-conflict-resolution-log.md` gains a sibling `## Hard-conflict resolution - <ISO-8601>` section (uniform hyphen-space separator per PCR-2a ADR-071 discipline) recording U-files, concerned slices, Critic verdict, and TRI-RESOLVE-1 disposition; an APED-1 empirical-execution battery drives the real resolver/dispatch against a real tmp-repo HARD conflict (HARD STOP-when-unratified + MIXED-routes-to-HARD + bare-STOP-fallback-on-missing-helper); full repo suite stays green.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_77_0_pcr_2b_tri_resolve_1_entry_present_in_repo | PENDING |
| 2 | integration | tests/methodology/test_pcr_2b_hard_conflict_dispatch.py | test_hard_conflict_fail_closes_to_stop_when_unratified | PENDING |
| 2 | integration | tests/methodology/test_pcr_2b_hard_conflict_dispatch.py | test_hard_path_preserves_bare_stop_when_helper_missing | PENDING |
| 2 | integration | tests/methodology/test_pcr_2b_hard_conflict_dispatch.py | test_soft_to_hard_shippability_escalation_enters_gate | PENDING |
| 2 | integration | tests/methodology/test_pcr_2b_verify_resolution.py | test_verify_resolution_clean_on_resolved_markdown_setext | PENDING |
| 3 | unit | tests/methodology/test_pcr_2b_tri_resolve_gate.py | test_tri_resolve_1_fail_closed_on_ambiguous_outcome | PENDING |
| 3 | structural | tests/methodology/test_commit_slice_skill_tri_resolve_gate.py | test_tri_resolve_1_soad1_structured_options_form_pinned | PENDING |
| 4 | integration | tests/methodology/test_pcr_2b_mixed_routes_to_hard.py | test_mixed_class_routes_through_hard_no_partial_soft | PENDING |
| 5 | integration | tests/methodology/test_pcr_2b_repro_hard_gate_closed.py | test_hard_gate_closed_returns_stop_resolution_result | PENDING |
| 5 | integration | tests/methodology/test_parallel_conflict_resolution_log_hard.py | test_hard_conflict_audit_section_appended | PENDING |
| 5 | integration | tests/methodology/test_parallel_conflict_resolution_log_hard.py | test_index_md_sole_hard_scenario_drives_gate | PENDING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | PCR-2b minted + taxonomy refined | `$PY -m pytest tests/methodology/test_methodology_changelog.py -k v_0_77_0_pcr_2b` PASSES; `$PY -m tools.plugin_manifest_audit` clean; new ADR present with `supersedes: null` + refinement note; ADR-069 HARD/MIXED rows annotated via the new ADR |
| 2 | HARD gate-on-hand-resolve | tmp-repo HARD rebase conflict → resolver/dispatch returns `action="STOP"` until a CLEAN+ratified outcome; no `git rebase --continue` invoked on BLOCKED/unratified (pinned test) |
| 3 | TRI-RESOLVE-1 fail-closed | unit test drives the gate with an ambiguous/empty triage outcome → resolves to STOP, never continue |
| 4 | MIXED routes to HARD | tmp-repo MIXED conflict (slice-queue.md + a tools/*.py file) → routes to HARD path, SOFT file NOT auto-regenerated (pinned test) |
| 5 | Audit-log + APED-1 | `## Hard-conflict resolution -` section appended on a real resolution event; full battery + full repo suite green |

## Must-not-defer

- [ ] **Fail-closed contract**: HARD / MIXED / UNKNOWN never silently auto-continue; BLOCKED or unratified TRI-RESOLVE-1 outcome → STOP with no `git rebase --continue`.
- [ ] **TRI-RESOLVE-1 is structured-options (SOAD-1)**, never a bare free-text prompt (free-text does not surface a user notification).
- [ ] **Bootstrap defense**: missing / failing resolver-helper import → unchanged PSQ-3 SOAD-1 STOP (try/except wrap per slice-067 / ADR-064).
- [ ] **Audit-log entry** written best-effort for every HARD resolution event (mirrors PCR-1 / PCR-2a; write failure → stderr, never blocks).
- [ ] **CAD-1 / OSDG-1 byte-equality** forward-sync for the edited `skills/commit-slice/SKILL.md`; **PMI-1 / INST-1** inventory updated if a new module/symbol ships.

## Out of scope

- **Auto-proposing a HARD resolution** (3-way merge driver / LLM-generated merge for the Critic to review) — the rejected ADR-069 Option 2; gate-on-hand-resolve ONLY (per /slice scope decision 2026-05-29).
- **Explicit R-23 (clock-skew) / R-24 (truncated-baseline) detection hooks** — emergent-only; both risks stay OPEN with their own SMALL queue candidates (`add-claim-sequence-number-for-clock-skew-detection`, `harden-pcr-2a-clock-skew-winner`).
- **`architecture/slices/_index.md` auto-resolve** — stays HARD per ADR-069 (Haiku-LLM-dispatched `/archive` regen is non-deterministic); user re-runs `/archive` post-merge.
- **PSQ-4 push-time rebase** — separate queued candidate.

## Dependencies

- Prior slices: [[slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen]] — `classify_conflict` already returns `HARD`/`MIXED`; `resolve_soft_conflict` STOP-dispatch is the branch point. [[slice-078-add-pcr-2a-vault-claim-resolver]] — the VAULT_CLAIM dispatch + audit-section pattern is the template for the HARD dispatch. [[slice-073-add-rebase-and-conflict-discipline]] — PSQ-3 sub-step 2.5 is the host site.
- Vault refs: [[decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen]] (taxonomy + HARD/MIXED rows + fail-closed contract), [[decisions/ADR-071-mint-pcr-2a-vault-claim-resolver]] (decoupled HARD/VAULT_CLAIM implementations), [[decisions/ADR-074-soft-regen-equivalence-guard]] (the guard-STOP that may later route into the HARD stack).
- Risk register: [[risk-register#R-23]], [[risk-register#R-24]] — remediation venue (NOT closed this slice).
- TRI-1 prior art: `skills/critique/SKILL.md` Step 4.5 (the user-triage gate this mirrors).

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m pytest tests/methodology/test_pcr_2b_hard_conflict_dispatch.py -q
```
Expected: the HARD-dispatch fail-closed test PASSES (resolver returns STOP until CLEAN+ratified; bare-STOP fallback preserved on missing helper). If fails: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
