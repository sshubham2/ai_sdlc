# Reflection: Slice 101 add-gate-audit-cli-exit-code-tests

**Date**: 2026-06-02
**Shipped**: YES

## Validated
- **In-process `main(argv)` exercises the real regression** — all 8 audit `main()` return the code (`sys.exit(main())` is the only exit site); validated by 18/18 + the 8-row mutation harness (each block test FAILS when `main()→return 0`).
- **Paired int+kind cause-assert delivers AC3** — every block test pins the SOLE target violation kind on its fixture; the code-Critic independently verified no co-firing kinds.
- **Parallel-safety with slice-100 held end-to-end** — diff = only `tests/methodology/test_gate_audit_cli_exit_codes.py`; `tools/`/`skills/`/`plugin.yaml`/`INSTALL.md`/`shippability.md`/`VERSION` all unchanged; no `VERSION` bump → zero R-28 forward-sync contention. Full suite 1345 + shippability 106/106.
- **Reusing existing on-disk fixtures was the right call** — `broken_impl_threat.md`'s em-dash heading sidesteps the M-add-1 double-dash trap *by construction* (the regex `[—\-]` accepts em-dash); hand-authoring a fixture would have risked the double-dash false-exit-0.

## Corrected
- None. No design claim was refuted by reality; no ADR superseded; no risk-register status flip. The design (CLEAN through the dual-Critic stack) matched what shipped exactly.

## Discovered
- **A mutation harness with a byte-length-IDENTICAL edit (`return 1`→`return 0`) poisons the `.pyc` cache.** After `git checkout` reverts the source, Python's default `.pyc` staleness check is `(mtime, size)` — a same-size edit + coarse-resolution mtime collision makes Python serve the STALE MUTATED bytecode. Surfaced as a phantom `test_lintmock` failure in the full suite (passed alone pre-harness). Impact: any future source-edit mutation harness must either (a) use a byte-length-CHANGING mutation, (b) clear `__pycache__` after revert, or (c) avoid source edits entirely via `monkeypatch.setattr(module, "main", lambda argv: 0)`. NOT a slice defect (`git diff tools/` empty throughout) — a harness-technique lesson.
- **The `--no-carry-over` flag is defensive-not-load-bearing for mission-brief-less tmp fixtures** (meta-Critic m2): `_slice_is_carry_over` returns False when no sibling `mission-brief.md` exists, so a bare tmp-dir fixture never triggers carry-over regardless. Kept the flag as future-proofing.

## Deferred
- **m2 (code-review)**: strengthen the LINT-MOCK/DR-1/WIRE-1 block-test int-asserts to `assert kinds == {"<target>"}` (lock the single-kind invariant so future fixture-drift fails loudly) — lands in: bundled code-Critic cleanup.
- **n1 (code-review)**: reproducible-AC2 idea — a committed `pytest.mark.skip`-gated `monkeypatch.setattr(module, "main", lambda argv: 0)` mutation test (sidesteps the `.pyc`-staleness class entirely) — lands in: bundled cleanup or a future test-quality slice.
- **Dedicated shippability row** for the new module — deliberately NOT added (AC4 parallel-safety forbids touching `shippability.md` while slice-100 holds edits to it). The new tests are covered by the existing methodology-suite regression surface; a dedicated row can be added in a post-slice-100-merge follow-up if desired (Step 5.3 carve-out, see Vault updates).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality observed at build/validate:

- **M1** (int can't discriminate STOP cause for PMI-1/TRI-1/DR-1): **VALIDATED** — ACCEPTED-FIXED; the multi-kind exit-1 ambiguity was real (reproduced by both Critics); the paired kind-assert fix is exercised by 18/18.
- **M2** (branch_workflow machine-fragility): **VALIDATED** — ACCEPTED-FIXED; the deterministic `branch -M trunk` recipe resolves host-independently (code-Critic traced all 3 branches).
- **M3** (mock_budget + shippability fixtures under-specified): **VALIDATED** — ACCEPTED-FIXED; naive shapes genuinely false-green to exit 0 (reproduced); the known-good-fixture reuse fixed it.
- **m1/m2/m3** (mutation-vs-cause; carry-over redundancy; BRANCH-1 label): **VALIDATED** — ACCEPTED-FIXED; all documentation/defensive, confirmed accurate.
- **M-add-1** (meta-Critic MISSED-by-first-Critic: CSP-1 row-6 same false-exit-0 trap, one row over): **VALIDATED** — ACCEPTED-FIXED; the first Critic's M3 was incomplete by exactly one row; the fixture-reuse fix sidesteps it.

**Missed by Critic**: the stale-`.pyc` mutation-harness footgun was surfaced by the full-suite run (BC-PROJ-4 backstop), NOT by any of the 3 Critics — none reads bytecode-cache semantics. (It's a harness-technique issue, not a deliverable defect, so arguably out of all three Critics' scope; noting for completeness.) The meta-Critic note (1) — a non-existent kind literal (`parity-mismatch`) in the Builder's OWN M1-fix table — is the canonical "a Critic's own fix is a fresh claim" catch, here applied to the *Builder's* fix delta.

**Pattern**: 3-Critic stack complementarity held again (design-Critic = multi-kind ambiguity + fixture under-spec + machine-fragility; meta-Critic = the missed-by-one-row CSP-1 trap + the Builder's own non-existent-kind-literal; code-Critic = runtime env-dependence m1 + non-vacuity re-confirmation by independent probe). Three personas, three non-overlapping defect classes. Do NOT collapse the stack. **MEPD-1 EXCLUDE** correctly applied — a test-only slice with no new RULE-ID / no `tools/*.py` / no VERSION bump → MCFS-1/AVFS-1/TVFS-1 forward-sync gates no-op.

## Lessons for next slice
- A source-edit mutation/non-vacuity harness MUST clear `__pycache__` after `git checkout` revert, OR use a byte-length-changing mutation, OR prefer `monkeypatch.setattr` over source edits — Python's `(mtime,size)` `.pyc` check silently serves stale same-size bytecode (the slice-101 stale-`.pyc` incident).
- Reusing a proven on-disk fixture beats hand-authoring one — it inherits the fixture's already-correct edge handling (here, the em-dash heading that sidesteps the CSP-1 double-dash trap by construction).
- For a deliberately-parallel-safe slice, an explicit AC forbidding edits to shared-aggregate files (`shippability.md`) is worth the carve-out from the "every slice adds a shippability row" rule — coverage via the existing suite-regression surface, dedicated row deferred to post-merge.

## Vault updates made (thin vault — small list)
- This slice's [[design.md]] — fix-updated through /critique (M1/M2/M3/m1/m2/m3) + /code-review (m1); matches what shipped.
- [[lessons-learned.md]] — appended the slice-101 entry (stale-`.pyc` + fixture-reuse + parallel-safe-carve-out patterns) via `vault_edit append`.
- [[diagnose-out/backlog.md]] — BCR-1 round-trip: `**Addressed:** slice-101-… on 2026-06-02` appended to SC-004/011/013/014/015/016/020/021.
- **No** `risk-register.md` change — no new open risk (the stale-`.pyc` is a harness-technique lesson, not a project risk).
- **No** `shippability.md` row — deliberate AC4 parallel-safety carve-out (Step 5.3 skipped with rationale; post-slice-100-merge follow-up option).
- **No** `methodology-changelog.md` / `VERSION` bump — MEPD-1 EXCLUDE (test-only, no new RULE-ID) → MCFS-1/AVFS-1/TVFS-1 no-op.
- **No** build-check promotion — the stale-`.pyc` lesson is N=1 (one-off harness technique); lands in lessons-learned, promote if it recurs.
