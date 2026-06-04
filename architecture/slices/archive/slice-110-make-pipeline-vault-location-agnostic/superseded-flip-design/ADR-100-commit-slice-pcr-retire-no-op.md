---
id: ADR-100
title: /commit-slice --merge recognizes the resolver's external-vault RETIRE result as a distinct clean no-op (executes ADR-089's flip-slice assignment)
date: 2026-06-04
slice: slice-110-flip-vault-to-external-store
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-100: /commit-slice consumes the PCR external-RETIRE as a clean no-op

## Context

[[ADR-089]] made `parallel_conflict_resolver` flip-ready: `_retire_if_vault_external(repo_root)` (`tools/parallel_conflict_resolver.py:307`, wired at resolve-entry `:367` and `:1455`) returns a RETIRE `ResolutionResult` when `vault_is_external` is True — vault files are untracked, cannot produce a git rebase-stage conflict, and routing `out_path` externally would corrupt in-tree git state. [[ADR-089]] §Consequences explicitly assigned the *consumer* side to the flip slice: "Wiring that replacement into PCR is the **flip slice's** job." slice-109 deferred its AC3 to here for the same reason ("lets it test the REAL external path"). With slice-110 performing the flip, the real external `VAULT_ROOT` now exists to exercise it.

`/commit-slice --merge` rebases the slice branch and, on conflict, dispatches to PCR's SOFT/HARD/MIXED/VAULT_CLAIM/UNKNOWN branches (`skills/commit-slice/SKILL.md` PCR-2b gate, ~`:196`–`:227`). Post-flip, a vault-file conflict cannot arise, but a *genuine non-vault* (code/test) rebase conflict still can — and the resolver's RETIRE result must be handled as a distinct outcome, never crash the flow or be misread as SOFT/HARD.

## Options considered

1. **Do nothing in `/commit-slice`** — rely on the resolver's RETIRE result falling through an existing branch. Con: the RETIRE `ResolutionResult` would land in whichever branch its class/exit maps to (risking a misleading SOFT/HARD message or an opaque UNKNOWN STOP); the operator gets no clear "vault is external; PCR retired" signal. **Rejected** (silent/confusing — the R-32 fail-visible spirit).
2. **Remove the PCR dispatch from `/commit-slice` entirely** — Con: over-broad; a genuine non-vault rebase conflict still needs the manual SOAD-1 path, and a pre-flip repo still needs PCR. **Rejected.**
3. **Recognize the external-RETIRE result explicitly as a distinct clean no-op** (chosen): when the resolver signals external-RETIRE, `/commit-slice` prints the RETIRE breadcrumb (vault is an external untracked store; vault conflicts cannot exist; the write-race is owned by `_vault_write` CAS per [[ADR-098]]) and routes any genuine non-vault conflict to the existing manual SOAD-1 block. Bounded prose + test.

## Decision

Adopt option 3. In `skills/commit-slice/SKILL.md`'s `--merge` rebase-conflict flow, branch on the resolver's external-RETIRE outcome **before** the SOFT/HARD/VAULT_CLAIM dispatch: treat it as a distinct, clean no-op carrying the actionable RETIRE breadcrumb; fall through to manual SOAD-1 only for genuine non-vault conflicts. Re-sync the OSDG-1-guarded installed copy. Add a test exercising the path against a real external `VAULT_ROOT` (a tmp repo with the git-common-dir config set to a tmp external dir) asserting the distinct no-op (not a crash, not a SOFT/HARD misclassification).

## Consequences

- Post-flip `/commit-slice --merge` is coherent: vault conflicts are impossible-by-construction and reported as such; non-vault conflicts still route to manual resolution; the bootstrap guard (resolver unavailable → fall through) is preserved.
- The PCR-for-vault-files retirement promised across [[ADR-085]]/[[ADR-089]] is now *complete on the consumer side*; the lost-update race is fully owned by `_vault_write` CAS (slice-109).
- No change to the resolver (slice-098 already RETIREs); this ADR is purely the `/commit-slice` consumer + its test.

## Reversibility

**Cheap.** A SKILL.md prose gate + one test + an OSDG-1 re-sync; `git revert` of the slice removes it. No data model, schema, contract, or identity lock.
