# Slice 032: add-query-design-skill

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: none directly (no open risk in `risk-register.md` tracks this) — capability/ergonomics addition; reduces the friction class where ad-hoc codebase questions either get answered without grounding or force a full `/diagnose` round-trip.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Add a new pipeline skill `/query-design`: a read-only, truthful, interactive conversation about the **existing** codebase. It answers the user's questions grounded in actual repo reads (Read / Grep / graphify) and changes nothing — no source edits, no vault writes. When a question surfaces a real requirement or defect, it does not author fixes; it offers (does not force) a clean handoff to `/slice` or `/slice-candidates`. This fills a niche no current skill covers — `/discover` is greenfield + vault-writing, `/diagnose` is a heavyweight non-conversational HTML deliverable, `/status` is a one-shot pulse, `/slice-candidates` needs the diagnose round-trip.

## Acceptance criteria

1. `skills/query-design/SKILL.md` exists in-repo AND the installed copy (`~/.claude/skills/query-design/SKILL.md`) is byte-equal — a drift test (mirroring the slice-skill drift test) passes.
2. The SKILL.md contract is explicitly read-only: it prohibits modifying source or vault files; the only permitted side effects are conversational output and an *optional* handoff to `/slice` or `/slice-candidates` (no direct authoring of code/vault/candidate files by `query-design` itself).
3. `plugin.yaml` enumerates `query-design` and `tools/install_audit.py` canonical lists include it — PMI-1 and INST-1 audits pass green.
4. `tests/methodology/test_query_design_skill.py` PASSES: it deterministically asserts the `skills/query-design/SKILL.md` prose contains the grounding contract (read repo before answering; cite specific files/symbols), the delegation contract (OFFER `/slice`; never auto-invoke; never author files), and the three error-model clauses (stale/missing graph; unanswerable-from-evidence; declined handoff → zero side effect). (Reworked per critique B3 — the prior "dry-run a conversational skill" had no deterministic pass/fail predicate, a slice-022 self-violation. The manual dry-run `/query-design "where is BRANCH-1 enforced?"` is retained as a NON-gating sanity note only.)
5. `methodology-changelog.md` records the new skill and its read-only invariant as a single versioned `## v0.46.0` entry carrying a minted rule reference (QD-1).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Skill exists + drift-clean | `ls skills/query-design/SKILL.md`; run the new drift test (pytest) — PASSES; manually diff in-repo vs installed = identical |
| 2 | Read-only contract | Grep SKILL.md for explicit "MUST NOT modify source/vault" + "handoff, not author" language; confirm no Write/Edit instruction targets code/vault |
| 3 | Manifest + install audit | `& $PY -m tools.plugin_manifest_audit` exits 0; `& $PY -m tools.install_audit` exits 0; both list `query-design` |
| 4 | Grounded answer + handoff (deterministic) | `& $PY -m pytest tests/methodology/test_query_design_skill.py -q` PASSES — prose-contract pin (grounding + delegation + 3 error-model clauses). Non-gating sanity: manual `/query-design "where is BRANCH-1 enforced?"` cites `tools/branch_workflow_audit.py` |
| 5 | Changelog entry + 4-part PMI-1 bump | `& $PY -m pytest tests/methodology/test_methodology_changelog.py -q` PASSES incl. the new `test_v_0_46_0_qd_1_entry_present_in_repo_and_installed`; `VERSION`==`~/.claude/ai-sdlc-VERSION`==`plugin.yaml.version`==`0.46.0`; in-repo & installed `methodology-changelog.md` both carry the `## v0.46.0` / `QD-1` entry |

## Must-not-defer

- [ ] SKILL.md read-only invariant stated unambiguously (no "may edit if…" loophole) — the entire value proposition is non-mutation
- [ ] PMI-1 / INST-1 / CSP-1 cross-spec parity wired (in-repo skill ↔ installed ↔ plugin.yaml ↔ install_audit) — partial wiring is a hard violation per CLAUDE.md self-hosting discipline
- [ ] **4-part PMI-1 atomic bump complete (DEVIATION-1)**: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + `~/.claude/methodology-changelog.md` forward-sync all at 0.46.0; bespoke `test_v_0_46_0_qd_1_entry_present_in_repo_and_installed` added in the **rule-ID-BEARING 4-assertion shape** (header + `QD-1` + `_QD1_PHRASE` + `ADR-032`, body-scoped, both surfaces — re-critique-v2 M1/M2) — 24/24 universal convention, NOT optional
- [ ] **v0.46.0 changelog entry is format-conformant** (re-critique-v2 m1): `### Added` heading + `Rule reference:` + `Defect class:` + `Validation:` lines per `methodology-changelog.md` L17-31 — only `Rule reference` is generically gated; `Defect class`/`Validation` absence ships silently if skipped
- [ ] **`_QD1_PHRASE` pinned at BOTH canonical sites (re-critique-v2 M-add-v2-1)**: `"read-only, delegation-only codebase Q&A"` appears verbatim in (i) v0.46.0 changelog `### Added` block (pinned by `test_v_0_46_0_qd_1`) AND (ii) `skills/query-design/SKILL.md` (pinned by a new explicit assertion in `test_query_design_skill.py`) — leaving (ii) unpinned recreates the silent-prose-drift class this slice exists to prevent (N=2 recurrence of v1 M-add-1)
- [ ] Drift test added so the skill can never silently diverge from installed copy (shippability catalog row per RPCD-1/SCPD-1) — row MUST be the 6-cell SCMD-1 shape (see design.md "Shippability row grammar"); `& $PY -m tools.shippability_decoupling_audit` exits 0 with the new row clean
- [ ] **ALL THREE INSTALL.md hard-count sites updated — L19, L185, L218** (count-agnostic phrasing per critique M1 + critique-review M-add-1) — ungated prose, will drift silently if skipped; single-site fixing ships 2/3 stale
- [ ] Handoff path is explicit and declinable — `query-design` must never silently auto-create a slice or candidate file
- [ ] Logging/trace: answers must be attributable to concrete repo evidence, not ungrounded recall — enforced by `test_query_design_skill.py` grounding-clause assertion (critique B3)
- [ ] Builder MUST NOT add a `## Pipeline position` block (out-of-loop; critique M3)

## Out of scope

- The exact mechanism of the handoff (direct slice-candidate file authoring vs. pure delegation to `/slice` / `/slice-candidates`) — that is a `/design-slice` decision; the brief pins only the *invariant* (read-only; offer-not-author).
- Modifying `/discover`, `/diagnose`, `/slice`, or `/slice-candidates` — `query-design` is additive and one-way-coupled (it may invoke them; they do not change).
- Any agent (`agents/*.md`) — this is a skill, not a Critic-style subagent.
- Auto-advance / `## Pipeline position` loop membership — `query-design` is an out-of-loop, user-invoked exploratory entrypoint, not an in-loop pipeline stage.

## Dependencies

- Prior slices: [[slice-007-install-time-rename]] — INST-1 install-audit parity precedent; [[slice-009-recursive-self-application]] — methodology-surface self-hosting precedent
- Vault refs: `plugin.yaml`, `tools/install_audit.py`, `tools/plugin_manifest_audit.py`, `architecture/methodology-changelog.md`, `architecture/shippability.md`
- Risk register: none (no open risk maps to this capability)
- Skill refs: [[skills/slice-candidates/SKILL.md]], [[skills/discover/SKILL.md]] (delineation references — what `query-design` is NOT)

## Mid-slice smoke gate

At ~50% of build (SKILL.md drafted + plugin.yaml/install_audit/VERSION edited, drift-test + new shippability row added, before changelog finalize):
```
& $PY -m tools.plugin_manifest_audit ; & $PY -m tools.install_audit ; & $PY -m tools.shippability_decoupling_audit
```
Expected: all three exit 0 with `query-design` listed and the new shippability row classified clean (critique B1/B2 — the SCMD-1 decoupling classification of the new `Path.home()`-reading drift test MUST be verified clean here, NOT assumed by pattern-copy; if `incidental`/coupled, STOP and redesign the row/test — an `_ALLOWLIST_SYMBOLS` edit is out of scope). If any fails: STOP, fix before continuing.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (manifest + install audits green)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] CSP-1 / PMI-1 / INST-1 / changelog-rule-reference audits all green at Step 6
- [ ] `grep -nE '\b2[45]\b.*skill' INSTALL.md` shows NO stale literal skill count (M-add-1 pre-finish guard — all three sites count-agnostic)
