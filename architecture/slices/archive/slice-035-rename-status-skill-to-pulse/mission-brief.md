# Slice 035: rename-status-skill-to-pulse

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none (no risk-register entry) — resolves a UX/invocation collision: the AI SDLC `/status` skill name shadows Claude Code's built-in `/status` command, making the skill ambiguously invocable.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The AI SDLC pipeline ships a skill named `status` whose trigger `/status` collides with Claude Code's built-in `/status` command, so users cannot reliably invoke the project-pulse skill. This slice renames the skill to `pulse` (already its conceptual name — `skills/status/SKILL.md:8` titles it "Project Pulse / Macro State" and `pulse` is an existing declared trigger) and propagates the rename across the plugin manifest, audit-list canon, tests, and all cross-doc references so the rename lands atomically with every drift/parity audit staying green.

## Acceptance criteria

1. `skills/pulse/SKILL.md` exists with frontmatter `name: pulse`, all `/status` self-references rewritten to `/pulse`, the colliding triggers (`/status`, `project status`) removed while `pulse` / `macro state` / `where are we?` triggers are retained; no `skills/status/` directory remains.
2. `plugin.yaml` declares `- id: pulse` (no `id: status`) and PMI-1 (`$PY -m tools.plugin_manifest_audit`) passes.
3. `tools/install_audit.py` canonical skill list contains `"pulse"` (not `"status"`) and its `/status` consumer comment is updated; INST-1 (`$PY -m tools.install_audit`) passes.
4. The three test modules referencing the skill are renamed and updated (`test_status_cadence_enforcement.py` → `test_pulse_cadence_enforcement.py`, plus `test_skill_model_dispatch.py` and `test_install_audit.py` body updates) and the full methodology test suite passes with zero stale `/status` skill references.
5. All Bucket-B prose `/status`-skill references are rewritten to `/pulse` per the design.md reference taxonomy — `pipeline.md`, `tutorial.md`, `README.md`, `INSTALL.md`, `templates/milestone.md`, `tools/install_audit.py:266`, `tools/risk_register_audit.py` L9/L14/L308, the changelog/RR-1 consumer prose in `test_methodology_changelog.py` + `test_risk_register_audit.py`, sibling SKILL.md next-step refs (`triage`, `slice`, `reflect`, `build-slice`, `commit-slice`, `query-design`), `tutorial-site/*.html`, `README.md:149` filename-token citation (m-add-1), the `methodology-changelog.md` self-references `:11-15` (`## How /status uses this file`, REWRITE) + `:1365` (Validation cross-ref, REWRITE filename) + `:1178` (FREEZE-AS-HISTORY) per M-add-1, and the vault docs `architecture/concept.md:46` + `architecture/risk-register.md:170,172` (rewritten; `architecture/lessons-learned.md:414` frozen-as-history per ADR-035). **`agents/critique.md` is NOT touched** (no `/status` skill ref exists there — B3; CAD-1 N/A). Rule `SRCD-1` is minted with a `methodology-changelog.md` `## v0.49.0` entry, the atomic `VERSION`/`plugin.yaml version`/changelog-header triple at `0.49.0`, forward-synced to the installed copy and pinned by a new `test_methodology_changelog.py::test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed`. CSP-1 + the full `tests/methodology/` suite stay green and a post-edit inventory grep shows Bucket A empty.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Skill renamed | `skills/pulse/SKILL.md` exists, frontmatter `name: pulse`; `Glob skills/status/**` returns nothing; `Grep "/status"` in `skills/pulse/SKILL.md` returns zero skill self-refs |
| 2 | Manifest parity | `$PY -m tools.plugin_manifest_audit` exits 0; `plugin.yaml` has `id: pulse`, no `id: status` |
| 3 | Install canon | `$PY -m tools.install_audit` exits 0; `"pulse"` present in canonical list, `"status"` absent |
| 4 | Tests green | `$PY -m pytest tests/methodology/ -q` passes; renamed test files present; `Grep` for `/status` skill refs across `tests/` returns only unrelated artifact-Status matches |
| 5 | Cross-doc + audits | `$PY -m tools.cross_spec_parity_audit` exits 0; repo-wide `Grep "/status"` yields only the excluded unrelated artifact-`Status` field vocabulary; changelog entry + VERSION bump present |

## Must-not-defer

- [ ] INST-1 / PMI-1 parity updated in the SAME slice as the rename (canonical list, plugin.yaml, install_audit.py); **4-part PMI-1 atomic bump** `0.48.0`→`0.49.0` (B-add-1): `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml version` + latest changelog header — all `0.49.0` in lockstep (`test_plugin_yaml_version_matches_version_file_invariant` + the prior-entry 4-part precedent at `methodology-changelog.md:89,105,…`)
- [ ] SRCD-1 minted: `methodology-changelog.md` `## v0.49.0` entry in mandated format (RULE-ID + Rule-reference + Defect-class + Validation), forward-synced to `~/.claude/methodology-changelog.md`, pinned by new `test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed`, AND a new `architecture/shippability.md` row pinning that test as SRCD-1's durable guard per RPCD-1/SCPD-1 (M-add-2; mirrors rows #33/#34) — OR a written ADR-035 exemption rationale if SRCD-1 is judged catalog-exempt
- [ ] Bucket-A executable filesystem-path binds (`test_risk_register_audit.py:334`, `test_skill_model_dispatch.py:25`, `test_status_cadence_enforcement.py:11`, fn renames) repointed — these FileNotFoundError on a directory-only rename
- [ ] CAD-1: **N/A this slice** — `agents/critique.md` has no `/status` skill ref (B3); rationale recorded in design.md Bucket C + ADR-035. (If build discovers a real critique.md edit is needed, CAD-1 reactivates.)
- [ ] Mini-CAD for `slice` skill stays green when `skills/slice/SKILL.md` next-step ref is updated
- [ ] Installed-copy reconciliation in-slice: `~/.claude/methodology-changelog.md` + `~/.claude/skills/status/`→`~/.claude/skills/pulse/` + sibling installed SKILL.md refs
- [ ] Post-edit inventory grep shows Bucket A empty; no dangling `/status` skill ref outside Bucket C (artifact-`Status` vocab, ADR-030 corpus, `lessons-learned.md:414`, `build/lib/`)

## Out of scope

- The unrelated artifact-`Status` field vocabulary in `tools/cross_spec_parity_audit.py`, `tools/build_checks_integrity.py`, `tools/utf8_stdout_audit.py` (dataclass fields / status enums — NOT the skill; must be left untouched)
- Any behavioral change to the skill's logic, output format, Haiku dispatch (COST-1), or cadence-enforcement semantics — this is a pure rename, not a redesign
- Renaming any other skill or adding a `/status` alias/shim (no backwards-compat alias — clean rename per brownfield no-shim discipline)
- Installed-copy reconciliation on the user's machine beyond what INSTALL.md documents

## Dependencies

- Prior slices: [[slice-032-add-query-design-skill]] — established the out-of-loop peer-skill set that references `/status`; [[slice-027-add-pipeline-chain-auto-advance]] — PCA-1 chain wiring that `/status` is deliberately excluded from (must remain excluded post-rename)
- Vault refs: [[methodology-changelog]] (RR-1 / COST-1 / CAL-1 rule refs to `/status`), [[shippability]] (INST-1 / PMI-1 / CSP-1 consumer references)
- Audits gating: INST-1, PMI-1, CSP-1, CAD-1, plus full `tests/methodology/` suite

## Mid-slice smoke gate

At ~50% of build (skill folder renamed + plugin.yaml + install_audit.py updated, before cross-doc sweep), run:
```
$PY -m tools.plugin_manifest_audit && $PY -m tools.install_audit
```
Expected: both exit 0 (PMI-1 + INST-1 green) with `pulse` present and `status` absent. If either fails: STOP, the canonical-list/manifest triad is out of sync — fix before propagating cross-doc refs.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (INST-1/PMI-1/CAD-1/changelog+VERSION)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Repo-wide `/status` grep returns only the explicitly excluded artifact-`Status` vocabulary
