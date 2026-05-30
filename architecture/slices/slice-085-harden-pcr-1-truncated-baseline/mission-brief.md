# Slice 085: harden-pcr-1-truncated-baseline

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-24 (PCR-1 SOFT equivalence guard cannot distinguish a genuinely-truncated/corrupt baseline from legitimate top-10 churn)
**Test-first**: true  (per TF-1 — the truncation/corruption failure mode is written as a failing test BEFORE the structural-distinction fix; see BFRD-1 disposition below)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

PCR-1's SOFT-class auto-merge (`tools/parallel_conflict_resolver.py::_resolve_soft`) decides "safe to auto-regenerate `slice-queue.md`" purely by comparing the regenerated entry-name *set* against the pre-merge baseline set. Slice-082 (ADR-074) added a count-floor WARN as a stop-gap, but it is fail-open (never STOPs) and only fires below 3 entries — so a baseline truncated mid-write to ≥3 entries, or a baseline that legitimately shrank vs. its committed state, can still spuriously compare set-equal and silently auto-merge. This slice adds a **structural integrity distinction** so the guard can tell a *truncated/corrupt* baseline that drops a claim (→ fail-closed STOP for human review) from a *legitimately-short healthy* one (→ unchanged auto-merge), **narrowing** R-24 (partial — clean-block-boundary truncation remains an undetectable residual; see [[decisions/ADR-077]]).

## Acceptance criteria

> **Scope refined at /design-slice + TRI-1-ratified ([[decisions/ADR-077]]).** Supersedes the original draft (which proposed STOPping on *any* truncation even with no claim-loss, plus a `git HEAD` entry-count comparison). The harm model — only **claims** are durable state in `slice-queue.md`; the candidate list self-heals on the next `/slice` — scopes the fix to **claim-loss-by-corruption**, and the mid-rebase `git HEAD` is not a stable baseline. **TRI-1 ratified (2026-05-30): Option 4 (orphan-gated) + (a) document M1 as residual** (NOT Hybrid, NOT (b) close-it).

1. The SOFT guard returns `action="STOP"` (fail-closed, no writes) when, in `_verify_soft_equivalence` Invariant #1's **orphan-claim branch**, a claimed candidate is dropped from the baseline AND the baseline is **tail-truncation-shaped** (the *last* `### <name>` block missing one or more of the 5 canonical on-disk PSQ-1 field labels `Source`/`Blast-radius`/`Parallel-safety`/`Effort`/`Risk-retired`, OR the file not ending at a clean block boundary) — escalating the current WARN-only `cross-stage-claim-drop`. A best-effort audit row names the claim-loss-by-corruption.
2. An orphan claim — a claimed candidate (from `merged_claims`) absent from a **well-formed** baseline — preserves the existing WARN-only behaviour and auto-merges (legitimate top-10 churn-drop, per ratified Option 4) — no false STOP / no auto-resolve regression. [happy-path guard]
3. A **well-formed** baseline that is legitimately short (passes the truncation precondition, clean ending, all blocks complete) auto-merges normally on a set-equal/churn regen — no false STOP on a healthy short queue. (The only "truncation auto-merges" case is the clean-block-boundary cut, which is undetectable and looks well-formed — documented residual, not a tested behaviour.)
4. No regression: (a) the pre-existing **overlay-silent-drop** STOP at `_verify_soft_equivalence:1775-1783` (a candidate claimed in `merged_claims` with a surviving heading whose claim is absent from the regenerated output → `_fail`; corrected per /critique M1 — this is NOT claim-line-truncation detection) stays a STOP — explicitly asserted; (b) the new STOP is end-to-end atomic — via real `resolve_soft_conflict` with slice-queue.md (truncation-shaped) AND shippability.md both pending, neither file mutated on disk; (c) PCR-1 SOFT set-equal (full-size healthy baseline) + PCR-2a clock-skew VAULT_CLAIM paths unchanged — every pre-slice-085 test in `tests/methodology/test_parallel_conflict_resolver*.py` still passes; (d) `_baseline_is_truncation_shaped` does NOT false-STOP an empty / `_(no candidates)_`-placeholder baseline and normalizes CRLF (per /critique m3 APED-1 battery).
5. R-24 is **narrowed** (not retired) in `architecture/risk-register.md` — a `**Narrowed:** slice-085 …` annotation records that claim-loss from a tail/mid-block-truncated baseline now STOPs, with clean-block-boundary truncation as the explicit undetectable residual (mirrors [[decisions/ADR-076]]/R-23); the 5 on-disk field labels are sourced from a single `_RENDERED_FIELD_LABELS` constant in `tools/slice_queue_writer.py` (not duplicated).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0) — each AC maps to one or more failing tests written BEFORE implementation. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_soft_stops_on_orphan_claim_drop_from_tail_truncated_baseline | PENDING |
| 1 | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_baseline_truncation_helper_is_tail_specific_not_whole_file_scan | PENDING |
| 2 | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_orphan_claim_drop_from_wellformed_baseline_warns_and_automerges | PENDING |
| 3 | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_wellformed_short_baseline_automerges_no_false_stop | PENDING |
| 4a | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_overlay_silent_drop_still_stops_1775_1783 | PENDING |
| 4b | integration | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_stop_is_atomic_via_resolve_soft_conflict_both_soft_files_pending | PENDING |
| 4d | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_empty_and_placeholder_baseline_not_truncation_shaped | PENDING |
| 4d | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_truncation_helper_normalizes_crlf_and_trailing_space_heading | PENDING |
| 5 | unit | tests/methodology/test_slice_queue_writer.py | test_format_entry_renders_from_rendered_field_labels_constant | PENDING |
| 5 | unit | tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py | test_baseline_truncation_helper_uses_writer_field_label_constant | PENDING |
| 5 | unit | tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py | test_existing_healthy_setequal_and_claim_preservation_unchanged | PENDING |

> **TRI-1 ratified (2026-05-30)**: Option 4 (m1, orphan-gated) + (a) document M1 as residual (NOT (b) close-it). AC-1 is the orphan-branch claim-loss STOP (claimed candidate dropped from a tail-truncation-shaped baseline); AC-2 is the orphan-on-well-formed WARN; AC-3 is the no-false-STOP guard for a legitimately-short well-formed baseline. The M1 invisible-claim case (claim only on the truncated branch) is a documented R-24 residual, not a tested STOP.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Tail-truncation precondition STOP | Synthetic baseline whose last block is missing a field label (and a variant cut mid-claim-line) → assert `resolve_soft_conflict` returns `action=="STOP"` regardless of whether a claim-loss is provable (incl. the M1 invisible-claim case); assert an audit row names the truncation |
| 2 | Orphan-on-well-formed WARN (no false STOP) | Claimed candidate (from merged_claims) absent from a fully well-formed baseline → assert auto-merge (`action=="APPLIED"`) + `cross-stage-claim-drop` WARN on stderr |
| 3 | Well-formed short baseline auto-merges | A legitimately-short but well-formed baseline (clean ending, all blocks complete) on a set-equal regen → assert `action=="APPLIED"`, no STOP (no false-STOP on a healthy short queue) |
| 4 | Single source of truth | Assert `_baseline_is_truncation_shaped` reads the labels from `slice_queue_writer._RENDERED_FIELD_LABELS` (monkeypatch/identity check) — writer + reader share one constant |
| 5 | No regression + R-24 narrowed | `& $PY -m pytest tests/methodology/test_parallel_conflict_resolver*.py tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py` → all green; `/validate-slice` VAL-1/WS-1/ETC-1 clean; R-24 carries a `**Narrowed:** slice-085` annotation |

## Must-not-defer

- [ ] **Fail-closed on uncertainty**: when the structural signal is *ambiguous* (e.g. git HEAD unavailable / file not yet committed), choose the safe verb — do NOT silently auto-merge a baseline that cannot be integrity-checked; degrade to STOP (or preserve the slice-082 WARN only where a STOP would be a strict false-positive, documented in design).
- [ ] **No new silent auto-resolve**: the slice must not widen the auto-merge surface — every new branch either STOPs or preserves existing AUTO_MERGE semantics (per `/commit-slice` "NEVER auto-resolve" contract).
- [ ] **Backward-compatible field-line contract**: the well-formedness check must read the *exact* 5 PSQ-1 field-line names from the stable on-disk contract (`slice_queue_writer`), not a hard-coded drift-prone copy — cite the source.
- [ ] **Audit/logging**: a STOP caused by the new structural distinction must emit a `detail`/`warnings` message naming the integrity failure (claim-loss from a truncation-shaped baseline) so the human reviewer knows WHY.
- [ ] R-24 register entry updated (narrowed, not retired) — not left stale.

## Out of scope

- R-23 (clock-skew) — separate risk, separate slice; PCR-2a path only touched for regression-proofing.
- Any change to the SOFT *set-equivalence* algorithm itself (slice-081 contract) — this slice adds a *pre-check*, it does not rewrite the equivalence comparison.
- A checksum/declared-count header in `slice-queue.md` (a heavier self-describing-integrity option) — noted in ADR-077 as a deferred alternative; the intrinsic tail-truncation signal suffices for the claim-loss scope.
- HARD/MIXED/VAULT_CLAIM resolution paths (PCR-2b / PCR-2a) — untouched except for the AC-4 no-regression assertion.
- **`Claimed-by` value-corruption** (heading + `Claimed-by` line present but the value is garbled) — a different corruption class from truncation/loss (per /critique B2 (b-ii)). NOTE: the case where the `Claimed-by` *line itself* is truncated away (b-i) is NOT out of scope — it already STOPs at `:1775-1783` and AC-4 pins it.

## Dependencies

- Prior slices: [[slice-082-harden-pcr-1-soft-regen-corner-case]] (the count-floor WARN this slice supersedes-by-strengthening), [[slice-081-add-pcr-1-soft-class-conflict-resolution]] (the SOFT equivalence guard), [[slice-067-add-psq-1...]] (the 5-field-line `slice-queue.md` contract via `slice_queue_writer`)
- Code: `tools/parallel_conflict_resolver.py::_verify_soft_equivalence` (Invariant #1 orphan-claim branch, ~`:1785-1799`) + new `_baseline_is_truncation_shaped` helper; `resolve_soft_conflict` (caller); `tools/slice_queue_writer.py` (field-label contract source, inline f-strings `:634-638` → new `_RENDERED_FIELD_LABELS` constant)
- Vault refs: [[decisions/ADR-074]] (slice-082 fail-open-with-audit decision being strengthened), [[decisions/ADR-072]] (PCR-1 equivalence guard), [[decisions/ADR-069]] (PCR taxonomy)
- Risk register: [[risk-register#R-24]]
- Tests: `tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py`, `..._soft_equivalence.py`, `..._clock_skew.py`, `..._pcr2a.py`

## BFRD-1 disposition (Step 3c)

Detection: name-shape sub-mode (a) does **not** fire (`harden-pcr-1-truncated-baseline` ≠ `harden-*-bug`). Candidate-source sub-mode (b): sourced from risk-register R-24, but R-24 is a **known-accepted limitation** whose current behaviour (fail-open WARN) was *deliberately chosen* at slice-082 / ADR-074 — not a latent defect producing wrong output in normal operation (it requires an abnormal truncated/corrupt baseline precondition). Consistent with sibling hardening slices 082 (`harden-pcr-1-soft-regen-corner-case`) and 084 (`harden-pcr-2a-clock-skew`), **neither routed through `/repro`** — this is a robustness hardening, not a bug-fix. Routed through **TF-1 test-first** instead (failure-mode test written before fix) to preserve reproduce-before-fix rigor without the `/repro` ceremony calibrated for defects. No `tests/bugs/*` row required.

## Critic disposition (Step 4a)

**critic-required: true** — slice touches `tools/parallel_conflict_resolver.py`, an in-house methodology surface (`tools/**/*.py`), a mandatory Critic trigger regardless of tier. It is also a correctness/safety guard on the parallel-merge auto-resolve path. Tier = medium.

## Mid-slice smoke gate

At ~50% of build (failing tests written + structural-distinction helper drafted), run:
```
& $PY -m pytest tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py -x
```
Expected: the new AC-1 claim-loss-STOP test FAILS (red, pre-fix the guard still WARNs-and-auto-merges) while the AC-2/AC-3 happy-path tests and ALL pre-existing resolver tests PASS — confirms the new test targets the right gap and no regression was introduced before the fix lands. If a pre-existing test breaks: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Test-first audit clean (`tools/test_first_audit.py --strict-pre-finish` — all rows PASSING)
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression in PCR-1/PCR-2a paths)
- [ ] R-24 narrowed (not retired) in risk-register.md
- [ ] **MEPD-1 determination recorded** (per /critique-review m-add-2): EXCLUDE per the slice-082/084 risk-narrowing-fix-with-ADR-no-new-RULE-ID precedent — confirm no new RULE-ID minted and no PMI-1 inventory change (in-place edit to already-manifested `parallel_conflict_resolver.py`); ADR-077 + R-24 `**Narrowed:**` + reflection are the audit trail. (If TRI-1 ruled INCLUDE: changelog entry + atomic version/PMI-1 bump instead.)
- [ ] No new TODOs / FIXMEs / debug prints
