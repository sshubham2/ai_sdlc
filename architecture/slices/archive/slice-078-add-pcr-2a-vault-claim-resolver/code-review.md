# Code Review: Slice 078 add-pcr-2a-vault-claim-resolver

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-29
**Result**: FINDINGS (0B / 0M / 5m — advisory)

## Summary

PCR-2a's resolver code maps faithfully to design.md's 7-step Resolution algorithm; M1/M2/M-add-1/M-add-2 fixes from the design-Critic stack are visibly implemented (strict-newer-stage-agnostic winner, in-memory `_pick_loser_replacement`, post-overlay defensive regex, uniform hyphen-space audit separator). The dispatch wiring at both sites (`resolve_soft_conflict` L249, exception loop L279, `_regen_slice_queue` L712, `_append_audit_log` L1274) is structurally consistent — PCR-1's UNKNOWN fail-closed leg is preserved verbatim per AC#2. Tests exercise stage-2/stage-3 winners, tie/multi-collision/overlay-silent-drop/in-memory-disk-ignore, and lazy-create-across-section-types append-only. No blockers, no majors. Five minors are catalogued below for bundled cleanup — none block ship.

## Changed files (in-scope)

```
tools/parallel_conflict_resolver.py
skills/commit-slice/SKILL.md
methodology-changelog.md
tests/methodology/test_pcr_2a_vault_claim_resolver.py
tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py
tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py
tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py
tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py
tests/methodology/test_methodology_changelog.py
tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py
VERSION
plugin.yaml
pyproject.toml
architecture/slices/slice-078-add-pcr-2a-vault-claim-resolver/build-log.md
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

None.

### Minors

#### m1: `_format_vault_claim_audit_entry` re-derives winner/loser from `diag.claim_history` rather than receiving them from `resolve_vault_claim_conflict` directly

- **Claim under review**: `tools/parallel_conflict_resolver.py` `_format_vault_claim_audit_entry` — `collisions = _collect_same_candidate_different_identity(diag.claim_history)` followed by `winner_loser = _select_timestamp_winner(collisions)`. Same computation already performed at the resolver's Step 1+2.
- **Issue**: Per Fowler / Beck (DRY + simple design), this is **duplicated computation**: the resolver has the winner/loser in scope when it calls `_append_audit_log(repo_root, diag, result)`, but doesn't pass them. The audit formatter then re-runs the same selection. Functionally safe today because `ConflictDiagnostic` is `frozen=True, slots=True` and `claim_history` is a frozen tuple — same input deterministically yields same winner. Defensible coupling. But it creates a hidden contract: any future change to selection semantics (e.g., adding a clock-skew tiebreaker) would require updates in **two places** — the resolver and the audit formatter. The defensive `(unavailable)` fallback is also dead code in practice (resolve path never invokes audit on the STOP branches).
- **Evidence**: `tools/parallel_conflict_resolver.py::_format_vault_claim_audit_entry` (re-derives) vs SOFT path's audit-entry section in `_append_audit_log` (builds entirely from `diag.u_files` + `diag.concerned_slices` + `result.regenerated_files` — no re-derivation). The asymmetry is the VAULT_CLAIM path re-deriving winner.
- **Proposed fix**: Bundled-cleanup option (low priority): extend the `_append_audit_log` → `_format_vault_claim_audit_entry` signature to pass `winner: ClaimEntry | None` and `loser: ClaimEntry | None` explicitly (or extend `ResolutionResult` with a `winner`/`loser` field-pair). Alternatively, accept current shape as DRY-violation-tolerated-because-of-immutable-input and document the contract in the formatter docstring more explicitly than "deterministic — same input yields same winner."

#### m2: `_pick_loser_replacement`'s missing-Parallel-safety default of `"UNKNOWN-NO-GRAPH"` overloads a real PSQ-1 sentinel

- **Claim under review**: `tools/parallel_conflict_resolver.py::_parse_queue_candidates_for_replacement` `_flush()` writes `current_safety if current_safety is not None else "UNKNOWN-NO-GRAPH"`.
- **Issue**: Per Wiegers / explicit-assumptions discipline, the absent-Parallel-safety-line case is conflated with the real PSQ-1 valid value `UNKNOWN-NO-GRAPH` (meaning "graph not available, can't compute overlap"). A malformed candidate block missing the `**Parallel-safety:**` field-line silently becomes "UNKNOWN-NO-GRAPH" rather than a distinct "MISSING" sentinel. The downstream filter at `_pick_loser_replacement` (`if safety != "NON-OVERLAPPING": continue`) correctly rejects both, so this is **semantically safe by accident** — both rejected from replacement selection. But a future caller wanting to distinguish "no graph computation done yet" from "field absent entirely" cannot. Also: `test_loser_auto_re_pick_skips_non_parallel_safe_candidates` exercises `OVERLAPS-WITH-*` / `UNKNOWN-NO-GRAPH` / `UNKNOWN-NO-HINT-FILES` but does NOT exercise a candidate with NO `Parallel-safety:` line — the missing-field branch is unwitnessed by tests.
- **Evidence**: `tools/parallel_conflict_resolver.py::_parse_queue_candidates_for_replacement`; `tests/methodology/test_pcr_2a_vault_claim_resolver.py::test_loser_auto_re_pick_skips_non_parallel_safe_candidates`. PSQ-1 valid values per design.md `"UNKNOWN-NO-GRAPH"` + `"UNKNOWN-NO-HINT-FILES"`.
- **Proposed fix**: Bundled-cleanup option: change default to a distinct sentinel like `"MISSING-FIELD"` (not in PSQ-1 enumeration) and add a focused test exercising a candidate block with `### name` + body but no `**Parallel-safety:**` line.

#### m3: Step 5 atomic write inverts the SOFT path's helper-returns-pair / commit-batch-after-loop discipline

- **Claim under review**: `tools/parallel_conflict_resolver.py::resolve_vault_claim_conflict` Step 5 — writes `out_path` THEN calls `subprocess.run(["git", "add", ...])` THEN `git rebase --continue` directly inline.
- **Issue**: PCR-1's SOFT path explicitly inverted this pattern after slice-076 critique M2 fix: helpers RETURN `(Path, str)` pairs without writing; only after the `try/except` loop completes successfully does the SOFT path batch-write + stage + continue. The PCR-2a path writes-then-stages BEFORE checking whether the rebase --continue itself will succeed. This is a partial regression of the slice-076 atomicity discipline — if `git add` fails (e.g., index locked by a concurrent process), the queue file on disk is already overwritten with the winner-overlaid content but no commit has captured it. Rebase abort would then encounter an unexpected working-tree modification.
- **Evidence**: `tools/parallel_conflict_resolver.py::resolve_vault_claim_conflict` Step 5 (PCR-2a inline write+stage+continue) vs `tools/parallel_conflict_resolver.py::resolve_soft_conflict` SOFT branch (PCR-1 batch-write-after-success). Same docstring at the resolver claims "Step 5: Atomic write + git add + git rebase --continue" but does not name "atomic" with respect to which failure modes.
- **Proposed fix**: Bundled-cleanup option: PCR-2a is single-file in scope so the SOFT-style "pending_writes list, batch-commit-after-loop" pattern would be overkill. But the discrepancy is worth a comment at Step 5 acknowledging the difference and naming the (smaller) blast-radius: "Single-file scope → inline write acceptable; PCR-1's pending_writes batching addressed multi-file partial-resolution windows that don't apply here." Alternatively, swap to: `git add` → `git rebase --continue` → write-on-success — but the current order is required because `git add` needs the file on disk. The minor finding is really documentation: pin the atomicity-by-single-file argument in the docstring.

#### m4: design.md `AC#1, 4 tests` claim is stale vs actual 20 test functions (build-log already records this as Conformance deviation)

- **Claim under review**: `architecture/slices/slice-078-add-pcr-2a-vault-claim-resolver/design.md` AC mapping table for AC#1 still says `(9 tests covering stage-2/stage-3 winners, ...)` while the actual `tests/methodology/test_pcr_2a_vault_claim_resolver.py` ships 20 test functions. The build-log Phase A notes "29 tests across new modules" — mission-brief TF-1 plan grew to 20 mid-build.
- **Issue**: Per TPHD-1 (Test-Plan-Harmonization-Discipline) / Wiegers traceability, the TF-1 plan in mission-brief is the load-bearing pre-commit anchor; drift between the plan and the realized test count is a documented mid-build addition. The build-log calls this out as "TF-1 plan rows grew from 18 (mission-brief) to 20 (mid-build addition of 2 predicate tests). Conformance class." So the design deviation is RECORDED, not silent — documentation-discipline working as designed, not a real defect. But design.md was NOT re-synced with the build-log addition.
- **Evidence**: `architecture/slices/slice-078-add-pcr-2a-vault-claim-resolver/design.md` AC mapping; `architecture/slices/slice-078-add-pcr-2a-vault-claim-resolver/mission-brief.md` TF-1 plan; `tests/methodology/test_pcr_2a_vault_claim_resolver.py` (20 `test_*` functions); `build-log.md` Design deviations section.
- **Proposed fix**: design.md drift is **out-of-scope for /code-review per slice-060 Dim 9** (design-meta TPHD-1 + PTFFD-1). Logging it as a minor here for the meta-Critic's reference at the next slice's `/critique-review` — Builder may optionally update design.md to match the realized 20-test count, or leave it as-is since build-log already captured the deviation.

#### m5: `_VaultClaimDispatch` sentinel exception inherits from `Exception` (not from `_SoftResolutionError`); ordering of `except` clauses is order-load-bearing-by-accident, not by inheritance

- **Claim under review**: `tools/parallel_conflict_resolver.py` defines `class _VaultClaimDispatch(Exception)`. The exception loop in `resolve_soft_conflict` has `except _VaultClaimDispatch:` BEFORE `except _SoftResolutionError as exc:`.
- **Issue**: Per Fowler (clear-intent code) and Python language idiom, the catch order matters for sibling exception types when one inherits from the other. Here `_VaultClaimDispatch` and `_SoftResolutionError` BOTH inherit directly from `Exception` — they are independent siblings, so catch-clause ordering is **semantically irrelevant**. A reader who flips the two `except` blocks would not change behavior. This is fine, but the comment block doesn't name the ordering invariant. A future maintainer might mistakenly believe ordering matters (because pattern is "more-specific exception caught first") and resist reordering. Also: `_VaultClaimDispatch` carries no payload by design — but the docstring claim "the dispatch target re-collects collisions from diag.claim_history directly (already populated by diagnose_conflict)" is only true when the resolver was invoked through `resolve_soft_conflict` with a `diag` that came from `diagnose_conflict`. If a future caller constructs `diag` manually with empty `claim_history` and triggers `_regen_slice_queue` to raise the sentinel, the dispatch target's Step 1 will return `STOP(conflict_class=UNKNOWN, reason="diag/class disagree, fail-closed")` — which is correct fail-closed behavior, but the sentinel's design assumes the diag is well-formed.
- **Evidence**: `tools/parallel_conflict_resolver.py` (`_SoftResolutionError` and `_VaultClaimDispatch` both `Exception` subclasses, no inheritance between them); exception-loop in `resolve_soft_conflict`; `tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py::test_unknown_class_still_fail_closed` exercises the disagree fail-closed path.
- **Proposed fix**: Add one-line comment after the `_VaultClaimDispatch` docstring: "Sibling to `_SoftResolutionError`; both inherit directly from `Exception` — catch-order in `resolve_soft_conflict`'s exception loop is **independent** (not load-bearing by inheritance)." This is purely a clarity-for-future-readers minor.

## Dimensions checked

- [x] **Unfounded assumptions** — m5 (the `_VaultClaimDispatch` docstring assumes `diag.claim_history` is well-formed when raised; tested fail-closed path exists, but the doc could be sharper).
- [x] **Missing edge cases** — none. The 9 categories (load, empty, network failure, concurrency, permission, offline, platform, CRLF) are mostly N/A for this resolver. Concurrency is explicitly accepted-residual per ADR-071's cooperative threat model + R-23. CRLF-EOL-DRIFT-1 is preserved via `newline=""` (same pattern as PCR-1 SOFT). m2 catches the one untested edge (missing Parallel-safety field).
- [x] **Over-engineering** — m1 (re-derivation of winner in audit formatter when resolver already has it in scope). No other speculative-generality patterns; no single-implementation interfaces; no dead parameters that I could find. `(unavailable)` fallback is dead in practice but defensible defensive coding.
- [x] **Under-engineering** — none. All 5 ACs have code elements; both dispatch sites wired; UNKNOWN-class fail-closed preserved verbatim (regression-pinned by `test_unknown_class_still_fail_closed`); APED-1 Pin #1 + Pin #2 regexes exercised at `test_substep_2_5_*`; pre-fix → post-fix repro at `test_pcr_2a_repro_vault_claim_gate_closed.py` (catalogued shippability row #78 per AC#5).
- [x] **Contract gaps** — none. Public `resolve_vault_claim_conflict` has docstring with 7-step algorithm + Error model enumerated. New helpers have docstrings explaining purpose + signature rationale (M-add-1 / M-add-2 / B1 fix references). Type hints on all public signatures. `_VaultClaimDispatch`'s "no-payload" contract is documented with the assumption noted in m5.
- [x] **Security** — none. No new user-input boundary; identity-as-claim per ADR-067 cooperative threat model is unchanged from PCR-1. No `shell=True`; no `eval`/`exec`; no hardcoded credentials. Subprocess invocations use list-form arguments (no shell injection vector). `GIT_EDITOR=true` env override is the standard Unix idiom and works on Windows where git invokes `cmd /c true` (the SOFT path uses the same pattern; no new attack surface).
- [x] **Drift from vault** — m4 (mission-brief / design.md TF-1 plan claims 4-row AC#1 while actual file ships 15+ test functions — build-log records this as Conformance-class deviation). No code-vs-design.md drift in the actual resolver behavior — the 7-step algorithm in code matches design.md §Resolution algorithm step-by-step. MEPD-1 INCLUDE posture honored: methodology-changelog v0.74.0 entry minted (all 7 required anchors present per `test_v_0_74_0_pcr_2a_entry_present_in_repo`); PMI-1 5-part bump synchronized at 0.74.0 across `VERSION` + `plugin.yaml` + `pyproject.toml` + `## v0.74.0` header.
- [x] **Web-known issues** — Skipped — code uses only stdlib (`subprocess`, `re`, `pathlib`, `os`, `dataclasses`, `enum`) + in-house modules. No third-party API / SDK calls in the diff that would require post-cutoff web verification. ISO-8601 lexicographic comparison of UTC `+00:00`-suffixed strings is a standard idiom with no known platform-specific bugs.
- [x] **Cross-cutting conformance** — none worth blocking. **APED-1 discipline**: Pin #1 + Pin #2 regexes were APED-1-executed during build (build-log records the Pin #2 regex refinement after initial over-broad match). **Algorithm-path-conformance**: Step 3's `baseline_text = text_3 if text_3 else text_2` mirrors `_regen_slice_queue` exactly (same default semantics); the test `test_timestamp_winner_when_newer_in_stage_2` explicitly guards the M4 critical-invariant case. **Language-version conformance**: `tuple[ClaimEntry, ...] | list[ClaimEntry]` is PEP 604 union syntax (Python 3.10+), which the repo targets. **Runtime-environment**: subprocess tests run in tmp_path-isolated repos (no `~/.gitconfig` pollution; `git config user.email/user.name` are local per `cwd=tmp_path`). **EOL-DRIFT-1 / ADR-033**: queue-file write uses `newline=""` (LF-only byte-deterministic); audit-log writes use `_append_audit_log`'s existing single-open `O_APPEND` pattern (no new byte-equality compare on `.md` content introduced). **Phantom-import check**: all `import` statements in the diff resolve — `_VaultClaimDispatch`, `_collect_same_candidate_different_identity`, `_select_timestamp_winner`, `_parse_queue_candidates_for_replacement`, `_pick_loser_replacement`, `resolve_vault_claim_conflict` are all defined in `tools/parallel_conflict_resolver.py` and imported correctly by all 5 new test modules. **Methodology-audit conformance**: the slice's own code pre-satisfies BC-1, TF-1 (20/20 PASSING per build-log), WIRE-1 (6 matrix entries with consumer-test pairs), PMI-1 (5-part bump), CAD-1 (no Critic-agent drift), OSDG-1 (commit-slice SKILL.md forward-synced), MCFS-1 (changelog forward-synced), AVFS-1 (installed VERSION matches), PVFS-1 (pyproject version matches), TVFS-1 (venv reinstalled at 0.74.0). RSAD-1 recursive-self-application: PCR-2a's own /commit-slice --merge invocation could hit VAULT_CLAIM auto-resolution if a peer claims concurrently — self-validating-slice property N=2 per build-log.

## Builder voluntary-restraint disposition (N=17 cumulative)

Per CRSI-1 v1 advisory-only mode + the voluntary-restraint discipline established at slices 037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/075/077, all 5 minors route to **bundled cleanup `bundle-074-075-077-078-code-critic-cleanup`** (extends the existing pending slice-079+ candidate). None block ship. None require code changes in this slice; carrying as deferred is the canonical pattern.

Sources:
- Fowler, *Refactoring* (2nd ed.) — DRY / speculative generality smell (referenced by m1)
- Wiegers, *Software Requirements* — explicit-assumptions discipline (referenced by m2, m5)
- ADR-069 (PCR-1 design § Forward references) — VAULT_CLAIM gate inheritance frame
- ADR-071 (this slice) — § Decision Option 1 frame + § Error model contract
- Mission-brief slice-078 AC#1-#5 — traceability frame for under/over-engineering check
