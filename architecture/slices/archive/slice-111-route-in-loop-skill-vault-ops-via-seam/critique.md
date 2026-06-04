# Critique: Slice 111 route-in-loop-skill-vault-ops-via-seam

**Critic reviewed**: mission-brief.md, design.md, ADR-103, ADR-104, project-frame.md, action-points.md
**Critic**: separate `critique` agent (read-only, adversarial), verified against the worktree
**Date**: 2026-06-04
**Result**: NEEDS-FIXES

## Summary

AC1 (routing) and AC2 (op-gate design) are largely sound, but the Critic found two blockers + three majors, all with file-line evidence: (B1) the dropped-AC3 `graphify vault` routing target does not exist — `/design-slice:62` is prose and no in-loop skill runs `graphify vault`; (B2) the `OP_DEFERRED_TO_FLIP` classifier mis-buckets the archive `mv` because source + dest literals coexist on one line and classification was line-anchored; (M1) AC1 routing drops ≥5 `architecture/` literals from the slice-107 baseline, tripping `_BASELINE_SHA256` / `_CLASS_COUNT_FLOOR[318]` / `EXPECTED_TOTAL=318` with no re-pin plan; (M2) the `vault_edit move` dest-exists guard was under-specified against `shutil.move` directory semantics; (M3) `OP_DEFERRED_TO_FLIP` lacked a contractually-required consumer. All ACCEPTED; design.md + ADR-103 + ADR-104 + mission-brief + risk-register edited this round.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC3's `graphify vault` routing target (`/design-slice:62`) is not an executable invocation
- **Claim under review**: mission-brief AC3 / design.md: "`/design-slice:62` `graphify vault architecture` → resolve via the seam."
- **Issue**: `/design-slice:62` is a sentence in the Keyword-archive-retrieval paragraph ("if the vault graph was built with `graphify vault architecture`…"), inside inline backticks — it documents a precondition, not a command `/design-slice` runs. The slice loop never runs `graphify vault`: `/reflect:298` rebuilds the *code* graph (`graphify code .`). The only `graphify vault architecture` executors are `/adopt`, `/discover`, `/heavy-architect`, `/sync` (+ `CLAUDE.md`) — exactly the `vault_flip_prose_inventory._RESIDUAL` set, already deferred. AC3 is therefore vacuous; `vault_edit root` would be an orphan subcommand.
- **Evidence**: `skills/design-slice/SKILL.md:62`; `skills/reflect/SKILL.md:298`; `tools/vault_flip_prose_inventory.py:299-305` (`_RESIDUAL` — no design-slice); grep of all `graphify vault` SKILL.md sites confirms none in-loop.
- **Proposed fix**: Drop AC3 + `vault_edit root`; fold graphify flip-awareness into the 318-prose-rewrite slice; remove `/design-slice` from the OSDG-1 re-sync set.
- **Builder draft**: **ACCEPTED-FIXED** — verified independently (`graphify vault` grep across all skills: zero in-loop executors). Dropped AC3 + `vault_edit root`; mission-brief AC3 removed + folded into OOS; ADR-103 retitled to `move`-only with a /critique-refinement note; design.md decisions-table row removed; OSDG-1 set reverted to `{/reflect, /commit-slice}`.

#### B2: `OP_DEFERRED_TO_FLIP` mis-classifies the archive `mv` — source + dest literals coexist on one line, gate was line-anchored
- **Claim under review**: ADR-104 rule 2: "target is a per-slice ACTIVE folder (`slices/slice-NNN…`, excluding `slices/archive/`)."
- **Issue**: The archive `mv` line carries BOTH `slices/slice-NNN` (active-folder → rule 2 DEFERRED) AND `slices/archive/` (must-route dest). Line-anchored classification (per `vault_flip_prose_inventory.py:22-25`) means a future un-routed `mv slices/slice-NNN <shared>/` would match rule 2 on its SOURCE literal and silently escape the gate — the precise AP-15 cheap-proxy failure ADR-104 claims to avoid. "Target" for a `mv` is the DESTINATION, but the matched active-folder literal is the SOURCE.
- **Evidence**: `skills/reflect/SKILL.md:320` + `skills/archive/SKILL.md:51` (two literals/line); `vault_flip_prose_inventory.py:22-25` (line-anchored, AP-1); AP-15.
- **Proposed fix**: Rule 2 keys on the op's DESTINATION/sink, not "any active-folder literal on the line." Add a dual-literal non-vacuity test: `mv slices/slice-NNN <shared>/` (no seam token) → `OP_UNROUTED`.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-104 rule 2 rewritten to key on destination/sink (mv/cp last-arg; Write/Edit/create/append target); dual-literal non-vacuity test added to ADR-104 + design.md test list.

### Majors (address this slice)

#### M1: AC1 routing drops ≥5 `architecture/` literals from the slice-107 baseline, tripping three pins with no re-pin plan
- **Claim under review**: design.md "Data model deltas: None"; AC #4 "default suite green at every commit."
- **Issue**: Routing replaces `architecture/...` with vault-relative `slices/...` in `vault_edit` commands → `_MATCH_RE` no longer matches them → `REWRITE_AT_FLIP` < 318, failing `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]=318`, `_BASELINE_SHA256`, `EXPECTED_TOTAL=318` simultaneously. Default suite goes RED at the AC1 commit.
- **Evidence**: `vault_flip_prose_inventory.py:90,288,291-296,312`; `tests/methodology/test_vault_flip_prose_inventory.py`; shippability #113.
- **Proposed fix**: After AC1 edits, re-run `--json`, re-pin all three to `318−K`, FBCD-1 fan-out the `318` literal repo-wide (docstring, tests, shippability narrative).
- **Builder draft**: **ACCEPTED-FIXED (plan) + ACCEPTED-PENDING (exec)** — re-pin step added to design Phase A + What's new + mission-brief Must-not-defer + Data-model-deltas; the live `318−K` measurement + re-pin execute at build (APED-1).

#### M2: `vault_edit move` dest-exists guard under-specified vs `shutil.move` directory semantics
- **Claim under review**: ADR-103: "refuses if the destination already exists."
- **Issue**: `move --to slices/archive/` — `slices/archive/` always exists. `shutil.move` moves src INSIDE an existing dst dir; the in-dir landing path must not pre-exist. A naive `if Path(--to).exists(): exit 2` refuses EVERY archive.
- **Evidence**: `shutil.move` docs (verified); `skills/archive/SKILL.md:56` (the existing semantic).
- **Proposed fix**: Guard checks the final landing path `<--to>/basename(<--from>)`, not `--to`. Add the test case.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-103 + design.md contracts + test list specify the final-landing-path guard (`--to` existing is NOT a refusal).

#### M3: `OP_DEFERRED_TO_FLIP` is an off-gate waiver unless a contractually-required consumer drains it (AP-12)
- **Claim under review**: ADR-104: "the flip slice greps that class and drives it to ∅."
- **Issue**: No audit/test FAILS if the flip slice ships without draining the bucket (the count-floor only catches a silent shrink, not a never-drained residual). Separately, the cross-store `mv` coherence hazard is parked in ADR-103 prose with no gate-visible owner (the routed `mv` leaves the bucket as `OP_ROUTED`).
- **Evidence**: AP-12; `_CLASS_COUNT_FLOOR` guards only shrink (`vault_flip_prose_inventory.py:331-334`); ADR-103 cross-store note.
- **Proposed fix**: Add a contractual consumer (R-32 sub-entry naming the flip-slice drain obligation) + record the cross-store hazard as an R-32 sub-entry.
- **Builder draft**: **ACCEPTED-FIXED** — risk-register R-32.a (drain `OP_DEFERRED_TO_FLIP` to ∅ = flip-slice pre-finish obligation) + R-32.b (cross-store archive-`mv` coherence) added; ADR-104 Consequences + mission-brief Must-not-defer reference them.

### Minors (log; address if cheap)

#### m1: AP-16 — verify `_WRITE_OP_VERBS` detection ⊇ classification set; `add` vs `git add` bigram
- **Issue**: existing `_OP_VERBS` has bare `add` (fires on "add a row"); the op-gate must detect every `git add architecture/...` form (`-A`, `--all`, multi-flag) while not flagging plain-prose "add" without a vault literal.
- **Builder draft**: **ACCEPTED-PENDING** — build-time APED-1: detection set documented as a superset of the classification set; assert both directions against the real corpus + code-Critic pass.

#### m2: MEPD-1 EXCLUDE precedent must be verified against the enforcing artifact
- **Issue**: a new fail-closed gate wired into `/build-slice`/`/validate-slice` with no RULE-ID is discoverable only via shippability; verify 106/109/110 each carried zero changelog entry while editing a build-gate before relying on EXCLUDE.
- **Builder draft**: **ACCEPTED-PENDING** — verify the precedent at build; ensure the op-gate shippability row lands (RPCD-1/SCPD-1); if precedent is wrong, mint a RULE-ID + v0.83.0 entry + PMI-1 4-part bump.

#### m3: `vault_edit root` trailing-newline + cross-shell interpolation
- **Issue**: `root`'s exact stdout bytes (newline?) + graphify absolute-path acceptance were asserted, not specified.
- **Builder draft**: **RESOLVED-BY-B1** — `vault_edit root` is dropped with AC3 (no consumer); moot.

## Dimensions checked
- [x] Unfounded assumptions — B1 (routing target does not exist), M2 (guard contradicts shutil.move), m3 (root behavior asserted).
- [x] Missing edge cases — M2 (`slices/archive/` always exists → naive guard refuses all); cross-filesystem move copy-window noted (low-prob, one-shot).
- [x] Over-engineering — none (op-gate reuses slice-107 tool, CSP-1-compliant; `move` minimal). **B1's fix further reduces surface** (drops `root`).
- [x] Under-engineering — B1 (AC3 no real target), M1 (re-pin step missing), M3 (no drain consumer).
- [x] Contract gaps — M2 (guard semantics), m3 (root output); op-gate exit contract well-specified.
- [x] Security — none (local tool/prose/audit; `move` reuses `_resolve_in_vault` outside-root guard for both `--from`/`--to`).
- [x] Drift from vault — B1 (`_RESIDUAL` contradicts the AC3 target), M1 (FBCD-1 `318` fan-out), m2 (MEPD-1 precedent); OSDG-1 set verified (reflect/commit_slice/design_slice guarded; archive/drift_check unguarded — B1 removes design_slice from the edited set).
- [x] Web-known issues — `shutil.move` directory semantics (M2); `$()` cross-shell newline-stripping (m3, now moot via B1).
- [x] Cross-cutting conformance — B2 (AP-15 cheap-proxy), m1 (AP-16 detection⊇classification — APED-1 at build), M1 (FBCD-1/AP-10 counted-set fan-out), M3 (AP-12 emptied-bucket). APED-1: op-gate not yet built → parse battery MUST execute against the real corpus at build (AP-3/AP-4).

## Triage

**Triaged by**: user
**Date**: 2026-06-04
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes — the first Critic (B1–m3) + the meta-Critic / `/critique-review` EXTEND (M-add-1–m-add-5). User-ratified at TRI-1 (3 structured decisions: M-add-1 → in-loop-set + `OP_OUT_OF_SCOPE` class; m-add-5 → hand-sync + document residual; re-review depth → proceed to build, APED-1 + code-Critic gate). No ESCALATED → not BLOCKED; ACCEPTED-PENDING present → NEEDS-FIXES.

| ID | Severity | Disposition | Rationale / fix ref |
|----|----------|-------------|---------------------|
| B1 | Blocker | ACCEPTED-FIXED | dropped AC3 + `vault_edit root` (no in-loop `graphify vault` executor); mission-brief/design/ADR-103 updated; OSDG set corrected |
| B2 | Blocker | ACCEPTED-FIXED | op-gate rule keys on op destination, not line literal (ADR-104) + dual-literal test |
| M1 | Major | ACCEPTED-PENDING | re-pin `_BASELINE_SHA256`/`_CLASS_COUNT_FLOOR[318]`/`EXPECTED_TOTAL` to `318−K` + FBCD-1 fan-out at build (plan in design Phase A; K deterministic post-M-add-2) |
| M2 | Major | ACCEPTED-FIXED | `vault_edit move` dest-guard = final landing path `<--to>/basename(<--from>)` (ADR-103) |
| M3 | Major | ACCEPTED-FIXED | risk-register R-32.a (drain `OP_DEFERRED_TO_FLIP`) + R-32.b (cross-store `mv`) |
| m1 | Minor | ACCEPTED-PENDING | build APED-1: detection ⊇ classification + `git add -A`/multi-path |
| m2 | Minor | ACCEPTED-PENDING | verify MEPD-1 EXCLUDE precedent at build; ensure shippability row lands |
| m3 | Minor | ACCEPTED-FIXED | moot — `vault_edit root` dropped by B1 |
| M-add-1 | Blocker | ACCEPTED-FIXED | 4th class `OP_OUT_OF_SCOPE` + pinned `_IN_LOOP_SKILLS`; `OP_UNROUTED` in-loop only (ADR-104); build APED-1 finalizes the allowlist (gate must go green) |
| M-add-2 | Major | ACCEPTED-FIXED | AC1 narrowed — `/commit-slice` archived reads deferred to the prose-rewrite slice; makes M1 `K` deterministic |
| m-add-3 | Minor | ACCEPTED-PENDING | add `query-design:59` (+ confirm `archive:216`) to `_RESIDUAL` at build |
| m-add-4 | Minor | ACCEPTED-FIXED | ADR-104 rewritten — stale `/design-slice` OSDG line removed |
| m-add-5 | Major | ACCEPTED-FIXED | "no installed copy" rationale corrected to "no `*_skill_drift.py`"; hand-sync `/archive`+`/drift-check`+`/validate-slice` installed copies (build must-not-defer) + documented residual |
