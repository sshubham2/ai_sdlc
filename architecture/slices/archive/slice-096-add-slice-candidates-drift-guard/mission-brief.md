# Slice 096: add-slice-candidates-drift-guard

**Mode**: Standard
**Estimated work**: 0.5 day (SMALL; could stretch if the in-repo / installed SKILL.md copies have drifted and need a forward-sync reconcile)
**Risk retired**: R-13 (low band, score 2, status `open`, reversibility cheap) — "OSDG-1 drift guard not yet extended to `/slice-candidates`". Closing this retires the last named-but-unguarded member of the OSDG-1 / mini-CAD skill-drift family (other skills carry no drift test by design — not a total-coverage claim; see Out of scope).
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The OSDG-1 / mini-CAD self-hosting discipline pins every methodology skill's in-repo `SKILL.md` to be content-equal (modulo EOL) to its installed `~/.claude/...` copy, so Claude never reads stale prose at skill runtime. 13 per-skill drift tests guard that family today (`triage`, `adopt`, `slice`, `design-slice`, `critique`, `critique-review`, `reflect`, `query-design`, `build-slice`, `commit-slice`, `code-review`, `pulse`, `diagnose`) — but `/slice-candidates` is the one named gap (R-13, open since slice-052; slice-095's own out-of-scope list defers to it as "R-13 OSDG-1-for-slice-candidates — separate queued candidate"). Its installed copy can silently drift from the in-repo canonical with no test catching it, which would let `/slice-candidates` run on stale prose — including a possibly-weakened "never read source files" read-only invariant ([[skills/slice-candidates/SKILL.md]] L16, the ADR-054 bounded carve-out). This slice closes the gap: it adds the per-skill drift guard for `slice-candidates`, wires it into the slice-finish gate roster + shippability catalog, and reconciles the two copies if they have drifted — completing the OSDG-1 guarded set.

## Acceptance criteria

1. A new per-skill drift test `tests/methodology/test_slice_candidates_skill_drift.py` asserts in-repo `skills/slice-candidates/SKILL.md` is content-equal **modulo line endings** (EOL-DRIFT-1 / [[ADR-033]]) to installed `~/.claude/skills/slice-candidates/SKILL.md`, via the shared `tests.skill_drift_equality.assert_md_forward_synced` helper (mirrors the 13 existing per-skill drift tests' exact shape — additive, no edit to the generic helper).
2. The OSDG-1 guarded-set enumeration in `CLAUDE.md` (Self-hosting discipline → "Mini-CAD / OSDG-1" bullet) is updated to name `slice-candidates` + its new drift test, closing the R-13-specific gap. (Scope note per /critique m1: this is a **courtesy-parity** edit — there is NO test pinning the enumeration to the drift-test-file set, and full enumeration↔drift-test parity for ALL skills is out of scope: `pulse` + `code-review` already have drift tests yet are absent from the prose list, and stay so.)
3. The new drift test PASSES against the current installed copy — reconciling via forward-sync (copy the in-repo canonical over the installed copy) if they currently diverge on non-EOL content — AND is non-vacuous: a planted non-EOL mutation (in a fixture or a temporary in-repo edit) makes it FAIL with the EOL-normalized-divergence message, then is reverted (slice-092/094 mutation-proof discipline).
4. The guard is wired into the methodology slice-finish gate path (collected by the `tests/methodology/` suite that `/validate-slice` runs) AND `architecture/shippability.md` records a row for it per RPCD-1 / SCPD-1 — a future silent drift of `slice-candidates/SKILL.md` can never merge unnoticed.
5. No regression: the full test suite stays green; the 13 existing drift guards behave identically; the MEPD-1 disposition (INCLUDE vs EXCLUDE — extending an existing guarded set vs minting a new rule) is decided in `/design-slice` and recorded, with no unintended RULE-ID / VERSION churn beyond what that disposition requires.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Drift guard added | `$PY -m pytest tests/methodology/test_slice_candidates_skill_drift.py` collects + PASSES; the test imports `assert_md_forward_synced` and targets `skills/slice-candidates/SKILL.md` vs `~/.claude/skills/slice-candidates/SKILL.md` |
| 2 | Enumeration in sync | `CLAUDE.md` OSDG-1 bullet names `slice-candidates` + `test_slice_candidates_skill_drift.py`; grep confirms the skill is no longer absent from the guarded-set list |
| 3 | Non-vacuous + reconciled | Mutation run: inject a non-EOL change into the in-repo (or a fixture) copy → test FAILs naming both normalized hashes; revert → PASSES. If the live copies diverged, the forward-sync reconcile is shown in build-log |
| 4 | Gate-wired + cataloged | The test runs under the `tests/methodology/` suite invoked by `/validate-slice`; `architecture/shippability.md` has a new row whose Command targets the new drift test; `$PY -m tools.shippability_*` (catalog audits) stay green |
| 5 | No regression | Full suite green (`$PY -m pytest`); `git diff` shows the change is additive (new test + CLAUDE.md prose + shippability row + any forward-sync); MEPD-1 disposition recorded in design.md / ADR if INCLUDE |

## Must-not-defer

- [ ] The new shippability row is added per RPCD-1 / SCPD-1 — skill-drift enforcement for `slice-candidates` must never silently regress (the new-audit-rule propagation discipline).
- [ ] The drift test fails CLOSED on a genuine (non-EOL) divergence — it must not be a vacuous always-pass (proven by mutation), and it must not mask real drift behind EOL normalization (the EOL-DRIFT-1 must-not-mask safety property, already exercised by `test_skill_drift_normalization.py`).
- [ ] OSDG-1 forward-sync of THIS slice's own edits: if `skills/slice-candidates/SKILL.md` is touched at all, it stays content-equal (modulo EOL) to its installed copy and its own new drift test passes (no self-inflicted drift).
- [ ] MEPD-1 disposition is explicit (INCLUDE → methodology-changelog + VERSION + PMI-1 atomic bump + shippability; EXCLUDE → guarded-set extension only) — decided, not defaulted; recorded in design.md.
- [ ] If the disposition is INCLUDE, the new-tool/new-pin count fan-out is complete (any per-test inventory pin enumerating the drift-test set is updated to include the new test).

## Out of scope

- Extending OSDG-1 to any OTHER currently-unguarded skill (`risk-spike`, `user-test`, `reduce`, `sync`, `archive`, `drift-check`, `heavy-architect`, `discover`, `supersede-slice`, …) — each is its own candidate; this slice closes only the R-13-named `slice-candidates` gap. (If design finds a near-free generalization, that's an ADR-worthy widening decision — not assumed here.)
- The R-2 diagnose-cwd runtime test, R-30 cp1252 decode audit, and the external-vault flip — separate queued candidates / blocked work.
- Any change to `/slice-candidates`'s behavior, contracts, or the `build_backlog.py` engine — this slice only adds a drift guard around its SKILL.md prose; it does not modify what the skill does.
- The shared `tests/skill_drift_equality.py` comparator — it is generic and reused as-is; this slice does NOT edit it.

## Dependencies

- Prior slices: [[slice-032-add-query-design-skill]] / [[slice-033-make-skill-drift-eol-agnostic]] — the per-skill drift-test pattern + the EOL-agnostic `assert_md_forward_synced` helper this slice reuses. [[slice-052-add-slice-candidates-obo-mode]] — where R-13 was registered (the slice that shipped `/slice-candidates` without bringing it under OSDG-1).
- Vault refs: [[decisions/ADR-033]] (EOL-DRIFT-1), [[decisions/ADR-032]] (per-file content-equality pattern). A new ADR is required ONLY if the MEPD-1 disposition is INCLUDE (minting/extending a rule); EXCLUDE needs no ADR.
- Risk register: [[risk-register#R-13]] (the risk this retires).
- **Parallel-safety**: independent of the two in-flight slices. slice-094 (`harden-vault-write-safety`) touches `tools/slice_queue_writer.py` / `slice_queue_claim.py` / `parallel_conflict_resolver.py` + a new VWS-1 audit — none shared. slice-095 (`harden-skill-driven-vault-writes`) touches vault-WRITING `skills/*/SKILL.md` surfaces + a new skill-vault-write audit; `/slice-candidates` writes only to `diagnose-out/` (never `architecture/`), so it is outside slice-095's vault-path-targeted audit scope. The only possible coordination overlap is the additive append to `architecture/shippability.md` (PCR-resolvable, the normal parallel-safe state — NOT a code collision) and, if slice-095 happens to edit the same `CLAUDE.md` OSDG-1 paragraph, a trivial markdown-list-append merge.

## Mid-slice smoke gate

At ~50% of build (drift test written + installed copy reconciled), run:
```
$PY -m pytest tests/methodology/test_slice_candidates_skill_drift.py
# then mutate the in-repo SKILL.md by one non-EOL char and re-run -> expect FAIL naming both hashes
# revert the mutation and re-run -> expect PASS
```
Expected: PASS on the synced tree, FAIL on the mutation (non-vacuity proven). If it passes on a planted non-EOL divergence (fails open) or the installed copy is missing (INSTALL.md not run): STOP, fix before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Ran in this dedicated BRANCH-2 worktree (NOT WORKTREE=skip) — isolated from the parallel slice-094 + slice-095 work.
