# Slice 039: apply-critic-calibrate-proposals-to-critique-agent

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none from `risk-register.md` directly; closes the `/critic-calibrate` feedback loop by applying the two user-ACCEPTED proposals from the 2026-05-17 (post-slice-034) calibration run. Leaving accepted proposals unapplied keeps two demonstrated first-Critic blind spots live: audit-parse-rule-vs-artifact (N=3 MISS — slices 030A/031/033; the R-5/R-6/R-7 class) and RULE-ID/entry-pin omission (N=2 — slices 032/034).
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The 2026-05-17 `/critic-calibrate` run generated two proposals, both **ACCEPTED by the user (2026-05-17) — "user to apply manually"** (`critic-calibration-log.md` L457–458). They have not been applied through slices 035–038. This slice applies both verbatim-to-intent into `agents/critique.md`, syncs the installed copy (CAD-1), mints the codifying methodology rule(s) + ADR(s) with their own entry-pin (dogfooding Proposal 2), and marks the calibration-log proposal table as applied. After this slice the Critic prompt enforces empirical audit-parse-rule execution and the methodology-surface RULE-ID/entry-pin checklist.

## Acceptance criteria

1. **Proposal 1 applied**: a new Dim 9 sub-clause "Audit-parse-rule empirical-execution discipline" is present in `agents/critique.md`, inserted after the PTFCD-1/PTFFD-1 phantom-citation sub-clause and before `### Bonus: weak graph edges`. It requires the Critic to Bash-execute a changed audit parse-rule against an adversarial battery (own-brief field-lines / trailing-annotation / substring-collision / empty-absent / CRLF), raise a **Blocker** on any silent-disable / default-off / false-FAIL / over-match, and state the battery was executed (not reasoned).
2. **Proposal 2 applied**: a new Dim 7 sub-bullet "Methodology-surface RULE-ID + entry-pin obligation" is present, inserted after the Dim 7 "write to vault folders" bullet. It is a checklist pass (separate from deep-dive) verifying either (a) RULE-ID + `test_v_0_NN_0_<rule>_entry_present_in_repo_and_installed` + atomic PMI-1 version bump, OR (b) a documented "why none" verified against `tests/methodology/test_methodology_changelog.py` — explicitly NOT a Builder-asserted prior-slice precedent (confirm vs artifact).
3. **CAD-1 holds**: `$PY -m tools.critique_agent_drift_audit --repo-root .` exits 0 — in-repo `agents/critique.md` content-equal modulo line endings (EOL-DRIFT-1) to installed `~/.claude/agents/critique.md`.
4. **Self-applied entry-pin (dogfood of Proposal 2)**: the codifying RULE-ID(s) + `methodology-changelog.md` entry (next version `v0.52.0`) + ADR(s) are minted, `tests/methodology/test_methodology_changelog.py` carries a `test_v_0_52_0_*_entry_present_in_repo_and_installed`, and PMI-1 (`$PY -m tools.plugin_manifest_audit`) passes with the version field bumped atomically.
5. **Calibration log reconciled**: the `### Proposals` table in `critic-calibration-log.md` (2026-05-17 run, L455–458) "User action" cells are updated from "ACCEPTED (2026-05-17) — user to apply manually" to applied, citing `slice-039`.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Proposal 1 clause present, correctly positioned | `grep -n "Audit-parse-rule empirical-execution" agents/critique.md`; confirm line ordering: after PTFCD-1/PTFFD-1 sub-clause, before `### Bonus: weak graph edges` |
| 2 | Proposal 2 sub-bullet present, correctly positioned | `grep -n "RULE-ID + entry-pin\|entry-pin obligation" agents/critique.md`; confirm it follows the Dim 7 "write to vault folders" bullet |
| 3 | CAD-1 content-equality | `$PY -m tools.critique_agent_drift_audit --repo-root .` exits 0 |
| 4 | Entry-pin + PMI-1 + changelog | `$PY -m pytest tests/methodology/test_methodology_changelog.py -k v_0_52_0` green; `$PY -m tools.plugin_manifest_audit` exits 0; new ADR file(s) exist under `architecture/decisions/` |
| 5 | Calibration log reconciled | `grep -n "slice-039" architecture/critic-calibration-log.md` shows the proposal-table cells updated |

## Must-not-defer

- [ ] CAD-1 installed-copy sync — in-repo and `~/.claude/agents/critique.md` must be content-equal modulo line endings after edit (EOL-DRIFT-1)
- [ ] PMI-1 plugin-manifest audit passes with atomic `VERSION` / `plugin.yaml` bump
- [ ] The entry-pin discipline this slice codifies (Proposal 2) is self-applied to this slice's own rule(s) — the codifying slice must satisfy its own rule
- [ ] Changelog entry is atomic with the rule mint (no rule without changelog row; no changelog row without in-repo + installed sync)
- [ ] Proposal text applied to-intent, not paraphrased into a weaker discipline (Critic clauses are executable contract — wording is load-bearing)

## Out of scope

- The three "Non-Critic-prompt actions for the user" (calibration log L460–464): function-level-PTFCD-1/TPHD-1 extension (already shipped as slice-037/PTFFD-1), auto-mode-classifier Builder note, autonomous-loop rubber-stamp skill-prose note — none are Critic-prompt edits.
- Watching-list items not yet at threshold (false-precedent Dim 1 sub-bullet — promote only if it recurs on a non-entry-pin surface per L476/L477).
- Any change to `/critic-calibrate` skill itself (this slice consumes its output, does not modify the skill).
- Re-running `/critic-calibrate` or re-deriving proposals (the proposals are fixed and accepted; this slice only applies them).

## Dependencies

- Prior slices: [[slice-037-extend-ptfcd-1-to-test-function-level]] — the PTFCD-1/PTFFD-1 Dim 9 sub-clause whose end is Proposal 1's insertion anchor; [[slice-034-fix-tf1-audit-field-line-regex]] — the R-7 N+1 miss that motivated Proposal 1.
- Vault refs: [[critic-calibration-log]] (2026-05-17 run, `### Proposals` L453–458), [[methodology-changelog]], [[decisions/ADR-038]] / [[decisions/ADR-039]] (most recent ADR numbering — next is ADR-040).
- Source: `agents/critique.md` (Dim 7 ~L121 "write to vault folders"; Dim 9 PTFCD-1/PTFFD-1 sub-clause L197–199; `### Bonus: weak graph edges` L201).
- Self-hosting: CAD-1 (`tools/critique_agent_drift_audit.py`), PMI-1 (`tools/plugin_manifest_audit.py`), INST-1 (`tools/install_audit.py`).

## Mid-slice smoke gate

At ~50% of build (after Proposal 1 inserted, before Proposal 2):
```
$PY -m tools.critique_agent_drift_audit --repo-root .
grep -n "Audit-parse-rule empirical-execution\|### Bonus: weak graph edges" agents/critique.md
```
Expected: drift audit exits 0 (in-repo synced to installed after the first edit); grep shows the new sub-clause appearing immediately before `### Bonus: weak graph edges`. If drift audit non-zero or ordering wrong: STOP, fix the sync/placement before continuing to Proposal 2.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] CAD-1, PMI-1, INST-1, BC-1 all green at Step-6 pre-finish
