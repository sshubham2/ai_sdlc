# Reflection: Slice 102 vault-flip-readiness-tests

**Date**: 2026-06-02
**Shipped**: YES

## Validated
- The `tests/**/*.py` surface extension classifies correctly — validated by the live run (160 `test-update-at-flip` / 49 `test-collection-pathspec` / 0 `needs-human` over 247 files) + 27 tests + the 6 code-Critic probe batteries.
- **Capability-without-flip holds** — `_vault_paths` default `Path("architecture")` untouched; full methodology suite 1373 PASS; shippability 108/108; production `baseline_tuple() == _BASELINE` (4 sites, byte-identical, AC1/AC5).
- The `write_text`/`write_bytes` content-arg correctness fix leaves the production baseline byte-identical — verified by execution (the 4 `project_frame_synth.py` sites are `/`-BinOps, untouched by the rule), independently re-confirmed by the code-Critic.
- The fail-closed completeness invariant is non-vacuous — a seeded tests-surface dynamic-fragment produces `needs-human` (CLI exit 2), proven both by `test_tests_surface_needs_human_pin_non_vacuous` and the live `--repo-root <tmp>` demo.

## Corrected
- (none of SHIPPED behaviour) — no shipped design claim was refuted. The two design-level corrections (M1 collection-mirror split, M2 AC4 production-scoping) were applied at `/critique` Step 4 **before** build, so the built spec was already correct. ADR-091's ruleset, the slice-098 Class-B markers, and the `_vault_paths` seam all behaved as assumed.

## Discovered
- **A latent false-positive in slice-100's own audit**: a positional arg to `write_text`/`write_bytes` was treated as a path (`_PATH_METHODS` arg-match), so `(tmp/x).write_text("…architecture/…")` test-content was mis-flagged as path-construction (and an f-string content produced a spurious `dynamic-fragment`). Latent on the production surface (no production `write_text`-content vault literal in the 4-site baseline); surfaced only when the tests surface — full of `write_text("<vault content>")` — was scanned. Fixed in-slice (`_CONTENT_ARG_METHODS`); NOT a new risk (a scoped correctness fix, baseline-preserving).
- **The `test-collection-pathspec` bucket is structurally heterogeneous** (meta-Critic M-add-1): a genuine path-resolve that is a bare collection-display member is demoted to the review list, not the checklist, and is not fail-closed. **Zero-instance today** (all 49 collection members are real git-pathspec/Class-B mirrors). Captured as a documented residual (`test_collection_member_genuine_resolve_is_review_residual`) + the loud-breakage / flip-execute-consumes-both-lists contract — NOT a risk-register entry (a named static-analysis limit, like slice-100's fully-dynamic-path residual).
- No new risk-register entry: R-32 stays `mitigating` (this slice advances flip-readiness on the last auto-classifiable surface; R-32 retires AT the flip).

## Deferred
- **The contract-prose surface** (`skills/**/SKILL.md` / `agents/*.md` / `CLAUDE.md` / `INSTALL.md`) — bulk-rewritten atomically at flip-execute; not reliably auto-classifiable. Owned by flip-execute / a dedicated prose slice. (Unchanged from slice-100.)
- **The actual flip** (`execute-vault-flip`) — physical move + git-untrack + default-flip + prose rewrite + PCR-replacement. **The last auto-classifiable readiness surface (tests) is now covered**; flip-execute consumes BOTH the `test-update-at-flip` checklist AND the `test-collection-pathspec` review list + the production `must-rewrite` set. The next major cut.
- **M-add-1 fix (a)** (stronger: loop/comprehension-variable flow tracking, or a non-zero review-required gate) — declined at TRI-1 as gold-plating over a zero-instance case; revisit only if a real genuine-resolve-in-a-collection appears.

## Critic calibration

Per TRI-1, scored against the `critique.md` `## Triage` table + the meta-Critic + the code-Critic + reality:

- **M1** (collection-mirror mislabel): **VALIDATED** — ACCEPTED-FIXED; the live 49 collection members ARE git-pathspec/Class-B mirrors (meta-Critic inspected), so routing them into the checklist would have handed flip-execute ~49 false "update" entries. The split is correct.
- **M2** (AC4 "combined baseline" vs production-scoped `baseline_tuple()`): **VALIDATED** — ACCEPTED-FIXED; a genuine AC-vs-design contradiction; corrected.
- **M-add-1** (collection-bucket heterogeneity — **MISSED by the first Critic**, caught by the meta-Critic): **VALIDATED** — ACCEPTED-FIXED via (b). The demotion is real (pinned). This is the headline calibration signal (see Pattern).
- **m1** (aggregate floor misses sub-class collapse): **VALIDATED** — ACCEPTED-PENDING → per-class floors implemented + verified (160≥120, 49≥30).
- **m2** (backslash-rel surface mis-derivation): **VALIDATED** — ACCEPTED-PENDING → normalized; code-Critic verified `skills/foo/tests/` stays production.
- **m3** (`fixtures/**` silent residual): **VALIDATED** — ACCEPTED-PENDING → pinned residual test.
- **code-Critic m1** (reason-string coupling): **VALIDATED** — hardened in-slice (`_REASON_UNMARKED_COLLECTION` SSoT).
- **code-Critic m2** (multiline-f-string lineno): **LOG-ONLY** — benign CPython quirk; the audit reports the inner-Constant lineno (accurate) + is fail-closed regardless.
- **code-Critic m3** (`_format_human` cross-surface count mislabel): **VALIDATED** — hardened in-slice (surface-honest `[production]`/`[tests]`/`[both]`).

**Missed by Critic**: the FIRST design-Critic missed **M-add-1** — the second-order consequence of its OWN accepted M1 fix (M1's blanket remap moved a fail-closed sub-population off the gate). The meta-Critic caught it by executing the remapped ruleset against an ordinary loop-over-list. Separately, the `write_text`-content false-positive was surfaced by the **Builder's design-time probe** (running the existing audit over `tests/`), not by any Critic — and the code-Critic caught the execution-level m1/m3 the design+meta stack structurally can't reach.

**Pattern**: **"a Critic's own fix is a fresh claim" recursed one level up** — the meta-Critic's structural value this slice was reviewing the *delta the first Critic's fix introduced* (M1 remap → M-add-1 fail-closed waiver), exactly the slice-089/097 lesson, now on a classification-boundary axis. 3-Critic stack complementarity held, non-overlapping, zero false-alarms: design-Critic = contract/checklist-pollution + AC-contradiction; meta-Critic = second-order-consequence-of-the-fix; code-Critic = execution-level reason-coupling + output-label. Strong `/critic-calibrate` probe: **"when a fix achieves 'needs-human → ∅' / 'no more flagged', did it RESOLVE the ambiguity or RE-ROUTE a fail-closed sub-population OFF the gate?"**

## Lessons for next slice
- **A reclassification that moves a fail-closed sub-population (`needs-human`/exit-2) into a non-gating class is a fail-closed WAIVER even when it reads as a completeness win.** The meta-Critic's M-add-1 caught exactly this on the first Critic's M1 remap. When a fix makes a fail-closed bucket go empty, ask whether the ambiguity was resolved or merely re-routed off the gate. A `/critic-calibrate` Dim-probe candidate.
- **On a LOUD-breakage surface, a non-fail-closed review bucket is sound IFF the downstream consumer processes it — make the "consume BOTH lists" contract explicit** so "mostly stays" can't be read as a structural invariant. Honest-contract residual (slice-095) + a pinned test is the proportionate response to a zero-instance latent gap (over-engineering a flow-tracker for zero instances was correctly declined).
- **Execute a freshly-EXTENDED classifier against the real corpus at design-PROBE time, not just `/code-review`** — running slice-100's audit over `tests/` during design surfaced the `write_text`/`write_bytes` content-arg false-positive, turning a latent slice-100 bug into a scoped, baseline-preserving fix. APED-1 N+1 on the extension axis (extends slice-098 "execute the signal against real fixtures").
- **For `execute-vault-flip` (the next major cut)**: the readiness audit now covers production (`must-rewrite`, 4 sites) + tests (`test-update-at-flip` 160 checklist + `test-collection-pathspec` 49 review list); the contract-prose surface is the only remaining un-audited surface (owned by flip-execute). Run `vault_flip_readiness_audit --strict` as the production pre-flight gate; consume all three lists.

## Vault updates made (thin vault)
- [[lessons-learned.md]] — appended the slice-102 entry (via `vault_edit append`, SVW-1 channel).
- [[shippability.md]] — row #109 (added at build, RPCD-1/SCPD-1).
- [[drift-log.md]] — slice-102 CLEAN entry (added at build, DCE-1).
- [[risk-register.md]] — no change (R-32 stays `mitigating`; retires at the flip).
- No ADR superseded; [[decisions/ADR-092]] accepted as designed (+ the M-add-1 (b) / m1 / m3 hardening applied within its `reversibility: cheap` envelope).
- **BCR-1**: no-op — no `**Closes:** SC-` sentinel (slice-102 is sourced from slice-100's deferred follow-up, not a backlog SC candidate).
- **MCFS-1 / AVFS-1 / TVFS-1**: no-op — MEPD-1 EXCLUDE (no VERSION / methodology-changelog / PMI-1 bump), confirmed exit 0 in the Step-6 battery.
- **BC-1 promotion**: NOT applied (no new cross-slice CODE pattern — the lessons are audit-internal or `/critic-calibrate` process signals; logged in lessons-learned + the calibration section above).
