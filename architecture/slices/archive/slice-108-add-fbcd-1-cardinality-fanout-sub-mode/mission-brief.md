# Slice 108: add-fbcd-1-cardinality-fanout-sub-mode

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: closes the count-literal / counted-set cardinality fan-out Critic blind spot (AP-10) — N≥3-distinct-slice first-Critic miss (slices 089/100/103/106, +096 prose sibling), self-flagged "overdue" in the slice-106 reflection. Applies the ACCEPTED Proposal 1 from the `/critic-calibrate` run 2026-06-03 (post-slice-107).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The dual design-Critic stack repeatedly misses sibling hard-count pins (`== N`, `len(...) == N`, INSTALL.md count lines) that live OUTSIDE the slice-authoring file-set when a slice changes a counted set's cardinality — they surface only at the full suite (slices 089/100/103/106). This slice applies the accepted `/critic-calibrate` Proposal 1 by extending the existing **FBCD-1** sub-clause (Dimension 9 of the Critic agent `agents/critique.md`) with a new **sub-mode (c)** that mandates a WHOLE-repo count-pin grep on any counted-set cardinality change, so the first Critic catches the fan-out at `/critique` time instead of the build's full suite catching it after the fact.

## Acceptance criteria

1. In-repo `agents/critique.md` Dimension 9 FBCD-1 sub-clause gains a **sub-mode (c) "Counted-set cardinality fan-out across repo-wide hard-count pins"** that (a) mandates grepping the WHOLE repo — not just `{mission-brief, design, ADR, milestone}` — for every `== N` / `len(...) == N` / `"N-element"` / `"set to N"` / INSTALL.md count literal referencing a set whose cardinality the slice changes; (b) directs a Major when a slice's plan enumerates only the membership pin; (c) cites the four concrete misses (089/100/103/106, AP-10); (d) states the explicit boundary that count-arithmetic-against-built-code (slice-091 decode-count) is OUT and stays APED-1/smoke-gate; plus a clause **(1b)** appended to FBCD-1's closing "When reviewing…" instruction extending the grep repo-wide on the cardinality-change trigger.
2. Installed `~/.claude/agents/critique.md` is forward-synced and **CAD-1 byte-equal** (EOL-agnostic per ADR-033): `python -m tools.critique_agent_drift_audit --repo-root .` exits 0.
3. **MEPD-1 discharged via the versioned-refinement branch (FBCD-1 v1.1)** — the locked decision (no new `-D` rule-ID; mirrors CCC-1 v1.1): mint a `## v0.83.0` methodology-changelog entry (with a `Rule reference: FBCD-1 (v1.1)` line) AND complete the full PMI-1 version-bump cascade in this slice — 5 version surfaces 0.82.0→0.83.0 + `pip install --upgrade .` (TVFS-1) + rename the rolling version-sync test `test_version_files_synchronized_at_v_0_82_0`→`_at_v_0_83_0` (sweep all 12 `0.82.0` literals across 4 asserts + docstring, update the `0.81.0→0.82.0` predecessor line, append `108` to the precedent chain) + repoint shippability row #75's version-sync citation (both cells) + add a `test_v_0_83_0_fbcd_1_v1_1_entry_present_in_repo` entry-pin; methodology-changelog + ai-sdlc-VERSION forward-synced (MCFS-1/AVFS-1).
4. A regression test pins sub-mode (c)'s presence in `agents/critique.md` (the failing repro guard PASSES at slice end) so the new Critic obligation can never silently regress; its run command is added to `architecture/shippability.md`.
5. Full suite + `/drift-check` green AND the slice's OWN artifacts (mission-brief, design, ADR if any, milestone) commit **no** count-literal fan-out — RSAD-1 self-application: the slice authoring the count-fan-out rule must survive that very rule.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_names_cardinality_fanout_sub_mode | PASSING |
| 4 | structural | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_names_cardinality_fanout_sub_mode | PASSING |
| 2 | audit (non-pytest) | — | CAD-1 `python -m tools.critique_agent_drift_audit` exit 0 | PASSING |
| 3 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_83_0_fbcd_1_v1_1_entry_present_in_repo | PASSING |
| 3 | structural | tests/methodology/test_methodology_changelog.py | test_version_files_synchronized_at_v_0_83_0 | PASSING |
| 5 | suite (non-pytest) | — | full suite + `/drift-check` + RSAD-1 self-application sweep | PASSING |

(The sub-mode (c) regression pin extends the canonical FBCD-1 body-bound cluster in `tests/methodology/test_critique_agent.py` — NOT a new file — and asserts BOTH the sub-mode (c) heading anchor AND the slice-091 count-arithmetic boundary clause, WRITTEN-FAILING against the pre-edit `critique.md` before the Dim-9 edit, PASSING after. The renamed rolling version-sync test `_at_v_0_83_0` goes RED on the 0.82.0→0.83.0 bump until its 4 leg literals are updated. AC2 (CAD-1) + AC5 (suite/drift) are verified by command execution, not a pytest file — the documented non-pytest TF-1 convention; included as rows so every AC carries a valid-status row per the slice-090 lesson.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | sub-mode (c) present in-repo | grep `agents/critique.md` for the sub-mode (c) heading + the four cited slice numbers + the slice-091 boundary clause |
| 2 | CAD-1 byte-equal | `python -m tools.critique_agent_drift_audit --repo-root .` → exit 0 |
| 3 | MEPD-1 discharged | open `tests/methodology/test_methodology_changelog.py`, confirm the EXCLUDE rationale matches what it actually asserts; full suite green |
| 4 | regression pin | the new test FAILS before the edit, PASSES after; shippability row runs green at `/validate-slice` Step 5.5 |
| 5 | self-application clean | `/drift-check` clean; manual RSAD-1 grep of this slice's own artifacts for unswept count literals; full suite green |

## Must-not-defer

- [ ] CAD-1 byte-equality between in-repo `agents/critique.md` and installed `~/.claude/agents/critique.md` (edit in-repo FIRST, forward-sync SECOND, audit THIRD)
- [ ] MEPD-1 discharged via the FBCD-1 v1.1 rule path (changelog `## v0.83.0` entry with a `Rule reference` line)
- [ ] **Full PMI-1 version-bump cascade completed in-slice** (the slice-105 build-check obligation set): 5 version surfaces 0.82.0→0.83.0 + `pip install --upgrade .` + rolling version-sync test rename `_at_v_0_82_0`→`_at_v_0_83_0` (sweep all 12 `0.82.0` literals across 4 asserts + docstring + `0.81.0→0.82.0` predecessor line + precedent-chain `108`) + shippability row #75 repoint (both cells) + entry-pin test
- [ ] New shippability catalog index computed as `max(existing)+1` = **#114** (catalog tail 111/112/113), NOT the slice number
- [ ] RSAD-1 self-application: sweep every FBCD-1 sub-mode-count claim — critique.md intro + BOTH stale `test_critique_agent.py` sites (the "two sub-modes" comment ≈L840 AND the `_names_both_sub_modes` docstring "not three" clause ≈L902, per meta-Critic m-add-1) — so the slice itself passes sub-mode (c); confirm no Dim-9 sub-CLAUSE-count pin is tripped
- [ ] Regression pin added to `architecture/shippability.md` (row #114) so the obligation can't silently regress
- [ ] `/drift-check` clean before finish

## Out of scope

- The **count-arithmetic-against-built-code** axis (slice-091 decode-count offset, where the correct value depends on a new helper's own runtime decode site). It stays APED-1 / mid-slice-smoke; sub-mode (c) explicitly excludes it. NOT added here.
- A standalone count-fan-out **build-check audit tool** — this slice is Critic-prompt-only. A deterministic repo-wide count-pin audit would be a separate slice (a future `build-check-candidate`).
- Any **new Dim-9 sub-clause** or new `-D` RULE-ID — this is a sub-MODE within the existing FBCD-1 rule, versioned as **FBCD-1 v1.1** (a methodology-changelog VERSION bump of the existing rule, NOT a new `-D` rule-ID and NOT a new dimension; anti-bloat: Dim-9 already carries 12 dense sub-clauses).
- The MEPD-1 **EXCLUDE** path (no VERSION bump) — considered and NOT chosen; the versioned FBCD-1 v1.1 path is locked (matches the CCC-1 v1.1 convention), so no deviation ADR is required.
- Re-litigating the routed-out categories from the calibration run (execution-only / meta-Critic-fix-delta classes).

## Dependencies

- Prior slices: [[slice-039-apply-critic-calibrate-proposals-to-critique-agent]] — lineage (same apply-a-calibration-proposal shape); [[slice-024-refine-dim-9-with-fix-block-completeness-sub-clause]] — FBCD-1 mint (the sub-clause being extended).
- Vault refs: `architecture/critic-calibration-log.md` run 2026-06-03 (post-slice-107) Proposal 1 (the accepted change text); `agents/critique.md` Dimension 9 FBCD-1 sub-clause.
- Self-hosting: CAD-1 (`tools/critique_agent_drift_audit.py`), MEPD-1 (`tests/methodology/test_methodology_changelog.py`).

## Mid-slice smoke gate

At ~50% (after the in-repo `agents/critique.md` edit + forward-sync to the installed copy):
```
python -m tools.critique_agent_drift_audit --repo-root .
```
Expected: exit 0 (CAD-1 clean) AND both copies contain the sub-mode (c) heading. If CAD-1 reports drift: STOP — the forward-sync is incomplete or the two copies diverged; do not continue building.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (CAD-1, MEPD-1, RSAD-1 self-application, shippability pin, drift-check)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (CAD-1 exit 0; sub-mode (c) in both copies)
- [ ] No new TODOs / FIXMEs / debug prints
