# Critique: Slice 047 add-two-scope-install

**Critic reviewed**: mission-brief.md, design.md, ADR-049
**Date**: 2026-05-19
**Result**: BLOCKED

## Summary

The slice is structurally clean on the methodology-surface obligations (MEPD-1(b) discharged by name, PMI-1 gate version-agnostic, INSTALL.md correctly identified as in-house surface). However the design's central premise — that project-scope installs become "newly available" by riding Claude Code's native project-level `.claude/` resolution — is contradicted by the official Claude Code precedence rule: **personal `~/.claude/` skills/agents override project `.claude/` ones**. For every existing user (all of whom have a user-scope install, per the mission brief's own framing), a project-scope install would be silently shadowed and have no effect. The Builder independently verified this against the official docs (see B1 evidence). Additional findings: the v0.56.0 entry-pin test is not committed in the phase plan (M1), the Test-first:false rationale does not rebut the same-surface slice-045/046 precedents (M2), and Step 1 pre-flight is left hardcoded under project scope (M3).

## Findings

### Blockers (must address before /build-slice)

#### B1: Project-scope is silently defeated by Claude Code's personal-over-project precedence for every existing user

- **Claim under review**: ADR-049 Options §2 pro "rides Claude Code's native project-level `.claude/` resolution"; design.md "What's reused": "skills/agents/settings under `<project>/.claude/` are active when CC runs in that project"; mission-brief Intent "project-scope becomes newly available".
- **Issue**: When a skill/agent name collides across levels, **personal (`~/.claude/`) overrides project (`.claude/`)**. The pipeline ships fixed-named skills (`slice`, `critique`, `build-slice`, …) and agents. Every existing user already has these user-scope (mission brief stresses "every current INSTALL.md user is on this path"). After a project-scope install, the user's `~/.claude/skills/slice/` shadows `<project>/.claude/skills/slice/` — the project copy never loads. Project-scope is a no-op in the dominant case and only works on a machine with no user-scope install. The "first user-facing capability" does not function for its primary audience.
- **Evidence**: [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) (Builder-verified independently via WebFetch 2026-05-19, quoting the "Where skills live" section verbatim): *"When skills share the same name across levels, enterprise overrides personal, and personal overrides project."* design.md has no precedence-collision handling; ADR-049 Consequences omits it.
- **Proposed fix**: Re-run /design-slice or /risk-spike. ADR must explicitly decide one of: (a) project-scope meaningful only on machines with no user-scope install (Step 0b says so verbatim — re-check it still clears the "first user-facing capability" bar); (b) project-scope additionally instructs user to remove/override user-scope copies (migration-adjacent — currently out of scope); (c) descope to documented-but-precedence-caveated. ADR-049's "rides native project-level resolution" pro is false as written and must be corrected — native resolution *defeats* the feature for existing users.
- **Builder draft**: **ESCALATED** — the platform fact is now CONFIRMED by the Builder against the official docs (not merely Critic-asserted), so this is not a "spike to learn the fact" escalation; it is a slice-viability decision the Builder cannot make unilaterally. The slice's entire value proposition collapses for the primary audience under options (a)/(c), and option (b) pulls in mission-brief-out-of-scope migration work. This must go back to the user (TRI-1) as a redesign-or-abandon decision: rescope the slice (e.g. project-scope-with-skillOverrides-guidance, or a different user-facing slice entirely), or accept a materially narrowed capability. Per the gate mechanics ESCALATED → BLOCKED → no /build-slice; revise design or pick a different slice.

### Majors (address this slice)

#### M1: Design plans a v0.56.0 changelog entry but does not commit to the per-version entry-pin test the shippability row must cite

- **Claim under review**: design.md "(a)": "Regression guard = the shippability row + v0.56.0 entry-pin, enforced by the existing methodology-changelog/CSP-1 suite."
- **Issue**: The generic tests (`test_version_matches_most_recent_changelog_entry`, `test_each_changelog_entry_carries_rule_reference`) only check *some* most-recent dated entry exists with *a* rule reference — they do not pin v0.56.0 content. The actual per-version pin is a hand-authored `test_v_0_NN_0_*_entry_present_in_repo()` (slice-046 row 46 cites `test_v_0_55_0_bfrd_1_reclassification_entry_present_in_repo` by name). design.md's deliverable list never enumerates authoring `test_v_0_56_0_*`. A shippability row citing an unwritten `test_v_0_56_0_*` is a PTFFD-1 phantom-function citation that fails /validate-slice Step 5.5; citing nothing executable fails SCPD-1.
- **Evidence**: `tests/methodology/test_methodology_changelog.py:3097` (slice-046 entry-pin), `architecture/shippability.md:56` (row 46 Command cell), design.md "Scope-check" deliverable list (4 items, no entry-pin test).
- **Proposed fix**: Add an explicit deliverable: author `tests/methodology/test_methodology_changelog.py::test_v_0_56_0_inst_1_v1_1_entry_present_in_repo()` (in-repo-only body per slice-041 MCFS-1 decoupling), asserting `## v0.56.0` header + `INST-1` ref + canonical discriminating phrase + `ADR-049` lineage + `Rule reference` line; shippability row cites it by exact name.
- **Builder draft**: **ACCEPTED-PENDING** — Critic is correct; this is a real PTFFD-1/SCPD-1 gap. Disposition is ACCEPTED-PENDING rather than ACCEPTED-FIXED-now because B1 forces a redesign that will rewrite design.md's deliverable list wholesale — applying this edit pre-redesign is churn. The entry-pin-function deliverable + corrected regression-guard wording fold into the post-B1 redesign and are mandatory there if any v0.56.0 entry survives the rescope.

#### M2: "Test-first: false" rationale does not rebut the same-surface slice-045/046 genuine-contrast precedents

- **Claim under review**: design.md "(a)": "A TF-1 plan over a markdown recipe would be tautological pin-writing with no genuine FAIL→PASS contrast (distinct from slice-046's prose-pin)."
- **Issue**: slice-045 lesson ("Test-first purity is cheap and worth it even for descriptive-prose ACs") and slice-046 lesson ("Genuine-contrast test-first works cleanly for a prose-reclassification AC … pin a positive grep-verified ABSENT + a negative grep-verified PRESENT") directly contradict the "tautological" claim on this exact surface. INSTALL.md is *more* executable-contract-like than slice-046's SKILL.md prose; AC #2's hard byte-stability claim is currently guarded only by manual grep+diff. The design dismisses the precedent without engaging it — an unrebutted aggregated lesson is a calibration regression.
- **Evidence**: Aggregated lessons (slice-045, slice-046); slice-046 shippability row 46 demonstrates the positive-absent/negative-present pattern on prose; mission-brief AC #2 guarded only by narration.
- **Proposed fix**: Either (a) adopt the slice-045/046 genuine-contrast pin (positive: `$CLAUDE_DIR`/Step 0b canonical phrase ABSENT pre-edit; negative: a current hardcoded `~/.claude` target literal PRESENT pre-edit) wired into the methodology test suite; or (b) keep Test-first:false but explicitly rebut why this surface differs from slice-045/046.
- **Builder draft**: **ACCEPTED-PENDING** — Critic is correct that the dismissal is unrebutted and the precedent applies. Fold into the post-B1 redesign: if a rescoped slice still touches INSTALL.md prose, adopt fix (a) (the genuine-contrast positive+negative INSTALL.md pin); the "tautological" rationale is withdrawn.

#### M3: Step 0b ordering vs Step 1 pre-flight leaves Step 1's hardcoded `~/.claude` detection unreconciled with project scope

- **Claim under review**: design.md "What's new": Step 0b "after Step 0 … before Step 1 pre-flight".
- **Issue**: INSTALL.md Step 1 (`:46-65`) hardcodes `$HOME/.claude` for content-detection lines (`:61` AI SDLC skills, `:62` agents, `:63` templates). Step 0b binding `$CLAUDE_DIR` to a project path *before* Step 1 makes Step 1 report "0/6 canary skills" against `~/.claude` even when project scope is populated (or "6" reading global when project is empty). design.md parameterizes only Step 3f + Step 4, omitting Step 1 — exactly the false-green/false-red surface AC #1 ("no behavioral delta") and the must-not-defer ("INST-1 verify the chosen scope") care about.
- **Evidence**: `INSTALL.md:46-65` (Step 1 hardcoded `$HOME/.claude` lines 54,59,60,61,62,63); design.md "What's new" omits Step 1 from the parameterized list.
- **Proposed fix**: design.md must decide: (a) Step 1 *content* lines also resolve against `$CLAUDE_DIR` while *env* lines stay `$HOME/.claude`; or (b) Step 0b runs *after* Step 1 (Step 1 stays global-env pre-flight) and the scope-boundary table notes Step 1 is global-only by design.
- **Builder draft**: **ACCEPTED-PENDING** — Critic is correct; the Step 1 omission is a genuine edge the scope-boundary table must resolve explicitly. Fold into the post-B1 redesign (it is the same recipe-surface rework B1 forces). Likely resolution: option (a) — Step 1 content lines honor `$CLAUDE_DIR`, env lines stay global, added as an explicit scope-boundary-table row.

### Minors (log; address if cheap)

#### m1: INSTALL.md install_audit remediation messages are scope-unaware

- **Issue**: `install_audit.py` is correctly `--claude-dir`-generic for path resolution, but violation messages hardcode "Re-run INSTALL.md Step 3f/3g" (`:184,206,228,256`) — under a project-scope failure this is correct only if the user re-selects project scope. The design's "zero audit code change, fully generic" slightly oversells: paths are generic, remediation prose is scope-unaware.
- **Proposed fix**: One sentence in ADR-049 Consequences: INST-1 violation prose is scope-agnostic; a project-scope user re-runs INSTALL.md and re-selects project scope — acceptable, no code change, explicitly decided.
- **Builder draft**: **ACCEPTED-PENDING** — valid; fold the one-sentence ADR-049 acknowledgement into the post-B1 redesign.

#### m2: ADR-049 reversibility "no consumer binds to the scope mechanism" is imprecise

- **Issue**: The slice deliberately creates one regression consumer (the shippability row + v0.56.0 entry-pin) per its own SCPD-1 obligation. "No consumer binds" is imprecise — revert must also drop the row + entry-pin test.
- **Proposed fix**: Reword ADR-049 Reversibility: "revert = edit INSTALL.md back to hardcoded `~/.claude`, drop the v0.56.0 entry + its entry-pin test + the shippability row; no data/schema migration, no *runtime* code consumer."
- **Builder draft**: **ACCEPTED-PENDING** — valid precision fix; fold into the post-B1 redesign's ADR rewrite.

## Dimensions checked

- [x] Unfounded assumptions — B1 (the "rides native project resolution" assumption is FALSE per official docs, Builder-verified); `install_audit.py` IS `--claude-dir`-generic (`:363`) so that reuse claim holds; PMI-1 gate is version-agnostic so "PMI-1 version-match invariant holds" is correct.
- [x] Missing edge cases — M3 (project-scope on a machine with populated user-scope install → misleading Step 1 pre-flight); B1 (collision-precedence platform edge).
- [x] Over-engineering — none; slice is minimal (recipe prose + ADR + one changelog entry + one shippability row).
- [x] Under-engineering — M1 (AC #5 / SCPD-1 needs an entry-pin test not committed); B1 (AC #1 project-level option has no design element making the project copy take effect).
- [x] Contract gaps — recipe contract only; M1 covers the missing regression-pin function.
- [x] Security — none; no runtime principal/protected action; must-not-defer "no write outside `<project>/.claude/`" structurally satisfied (Step 0b pre-mutation).
- [x] Drift from vault — ADR-049 number free; VERSION=plugin.yaml=0.55.0 so 0.55.0→0.56.0 bump correct; slice-014/008 versioned-refinement precedent genuine; MEPD-1(b) discharged by name; entry-pin obligation owed = exactly the M1 gap.
- [x] Web-known issues — B1 filed and Builder-confirmed from official Claude Code skills docs (2026-05-19): personal overrides project — directly contradicts ADR-049's core enabling assumption.
- [x] Cross-cutting conformance — M1 (PTFFD-1 phantom-function risk; SCPD-1 owed, M1 fix discharges it); EPGD-1 benign (version-agnostic gate, no supersession); RSAD-1 — the slice's own ADR-049 "rides native resolution" prose is itself the rule-class defect (unfounded platform assumption in a slice whose point is to *decide* the scope boundary) — folded into B1.

## Triage

**Triaged by**: user
**Date**: 2026-05-19
**Final verdict**: BLOCKED

User TRI-1 decision (2026-05-19): the `add-two-scope-install` *feature* is abandoned as platform-infeasible — B1 (skills: personal `~/.claude/` overrides project `.claude/`) and M-add-1 (agents: project `.claude/agents/` overrides user `~/.claude/agents/` — the inverse, yielding a split-resolution state), both independently Builder-confirmed via WebFetch against the official Claude Code skills + sub-agents docs. The salvaged value (retire the standing slice-045/046 structural deferral) is preserved by rewriting ADR-049 from a feature-design ADR into a **decision record**: project-scope-via-`cp` is not viable; install scope is decided **global-only**; revisit only via a Claude Code **plugin** re-architecture (namespaced `plugin-name:skill-name` cannot collide). `/build-slice` is NOT run. Slice-047 is closed out as a decision-only / withdrawn-feature slice; the next candidate is selected via a fresh `/slice`.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ESCALATED | User-directed 2026-05-19: feature platform-infeasible (skills personal>project, Builder-doc-confirmed). Abandon the feature build; redesign ADR-049 to a global-only decision record retiring the deferral. /build-slice NOT run. |
| M-add-1 | Blocker-class | ESCALATED | Reinforces B1 (agents project>user — inverse — split-resolution worse than no-op; Builder-doc-confirmed). Subordinate to B1's resolution; same user decision. |
| M1 | Major | DEFERRED | Moot under the decision-only redesign — no v0.56.0 behavioral changelog entry (no-behavior-change/conformance class per slice-043/045 precedent); the entry-pin deliverable folds away with the abandoned feature. Backlog target: none (obsolete with the feature). |
| M2 | Major | DEFERRED | Moot — no INSTALL.md prose change in the decision-only redesign; the slice-045/046 genuine-contrast pin is N/A with no recipe edit. Backlog target: none. |
| M3 | Major | DEFERRED | Moot — no Step 0b / Step 1 reconciliation in the decision-only redesign. Backlog target: none. |
| m1 | Minor | DEFERRED | Moot — `install_audit.py` untouched in the decision-only redesign. Backlog target: none. |
| m2 | Minor | ACCEPTED-PENDING | Still applies: the ADR-049 rewrite states precise reversibility — as a pure decision record, revert = delete the ADR; no consumer/shippability binding is created (the imprecision the finding flagged is removed by the rewrite). |
| m-add-2 | Minor | DEFERRED | Moot — no v0.56.0 installed-copy write in the decision-only redesign. Backlog target: none. |
