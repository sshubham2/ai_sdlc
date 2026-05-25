# Critique Review: Slice 047 add-two-scope-install

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-19
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's BLOCKED verdict is sound — B1 is a real, Builder-confirmed platform-precedence blocker that defeats the slice's central premise. But B1 is built on a uniform "skills/agents" precedence claim that is provably false for agents: project-level subagents OVERRIDE user-level, the opposite of skills. This asymmetry changes B1's redesign option set materially and is itself a missed finding (M-add-1). M1/M2/M3/m1/m2 are all VALID with correct severities. One additional Minor missed (m-add-2).

> **Builder note (recompute-don't-trust, per the recurring DR-1 "execute don't reason" lesson)**: the meta-Critic flagged its own reservation that M-add-1's subagent-precedence direction rested on web search, not WebFetch. The Builder independently re-confirmed it via WebFetch against [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents) on 2026-05-19. The official precedence table reads: `.claude/agents/` (project) = **Priority 3**; `~/.claude/agents/` (user) = **Priority 4**; "the higher-priority location wins" → **project overrides user for subagents**. This is the exact inverse of the skills rule ("personal overrides project") that B1's skill-half was confirmed against. M-add-1 is therefore Builder-VALIDATED, not merely meta-Critic-asserted.

## Confirmed findings

- **B1** (project-scope silently defeated by personal>project precedence for skills) — confirmed; severity Blocker appropriate. Skills-precedence half verified against official Claude Code skills docs ("personal overrides project"). The design's load-bearing platform assumption is false for the skill artifacts the pipeline ships. ESCALATED → BLOCKED is correct: the Builder cannot unilaterally decide redesign-vs-abandon.
- **M1** (v0.56.0 entry-pin not committed as a named per-version test) — confirmed; Major appropriate. Per-version pin convention is real and consistently named (`test_methodology_changelog.py:3097`; shippability rows 37-46 all cite `test_v_0_NN_0_*` by exact name). design.md Scope-check enumerates 4 deliverables, none an entry-pin test. An uncited shippability row self-violates SCPD-1; phantom-fn citation fails PTFFD-1 at /validate Step 5.5.
- **M2** (Test-first:false unrebutted vs slice-045/046 same-surface precedent) — confirmed; Major appropriate. slice-045 (row 55) + slice-046 (row 56) both shipped genuine-contrast prose pins on the INSTALL.md/SKILL.md surface family; design.md asserts "tautological pin-writing" without rebutting the aggregated precedent. Calibration regression.
- **M3** (Step 0b before Step 1 leaves Step 1's hardcoded ~/.claude unreconciled) — confirmed; Major appropriate. Verified `INSTALL.md:46-65`: Step 1 hardcodes `$HOME/.claude` content detection (:61 skills 0/6, :62 agents 0/5, :63 templates 0/4). design.md parameterizes only Step 3f + Step 4. Under project-scope with Step 0b binding `CLAUDE_DIR` first, Step 1 reports a false-negative content state.
- **m1** (install_audit remediation messages scope-unaware) — confirmed; Minor appropriate. `install_audit.py:301-308` `no-claude-dir` message hardcodes remediation prose; design.md overstates "Zero audit code change required" without noting prose stays scope-agnostic. Cosmetic, no behavior impact.
- **m2** (ADR-049 reversibility "no code consumer binds" imprecise) — confirmed; Minor appropriate. The slice's own SCPD-1 obligation creates the shippability row + entry-pin regression consumer; ADR-049 Reversibility omits dropping them on revert.

## Suspicious findings

No suspicious findings. Every first-Critic finding survives second-pass scrutiny against design.md, INSTALL.md, install_audit.py, and official platform docs. The 4th-option disconfirmation attempt for B1 (plugin `plugin-name:skill-name` namespace, which "cannot conflict with other levels") does not moot it: the pipeline installs via INSTALL.md `cp` into `~/.claude/skills/`, not as a namespaced plugin, so the namespace escape is unavailable without re-architecting the install model (which ADR-049 does not propose). B1 stands.

## Missed findings

- **M-add-1 (Blocker-class, strengthens B1): B1's premise over-generalizes — agent precedence is the INVERSE of skill precedence; the real failure mode is a split-resolution state, not a uniform no-op.** B1 says "personal overrides project for same-named skills/agents." Verified-true for **skills** ("personal overrides project") but verified-**false for subagents**: official Claude Code subagents docs precedence table — `.claude/agents/` (project) Priority 3 **>** `~/.claude/agents/` (user) Priority 4; "the higher-priority location wins" → **project overrides user**. The pipeline ships BOTH 25 skills AND 5 subagents (`agents/critique.md`, `critic-calibrate.md`, `critique-review.md`, `diagnose-narrator.md`, `field-recon.md` — verified on disk). Under project-scope on an existing user-scope machine: the 25 skills are shadowed by user copies (do NOT load from project) while the 5 agents' project copies DO override the user copies (project agents load). This **split-resolution** state is *more dangerous* than B1's stated clean no-op: INST-1 `--claude-dir <project>/.claude` verifies all artifacts present on disk while CC loads a mixed skill(user)/agent(project) set at runtime — the must-not-defer false-green guard is specifically defeated for the skill half. Proposed fix for TRI-1: any B1 redesign / ADR-049 must (a) state the skill-vs-agent precedence asymmetry explicitly (Builder-confirmed via WebFetch, see Builder note above), and (b) decide the split-resolution case as a first-class hazard. This strengthens, not weakens, BLOCKED.

- **m-add-2 (Minor): the v0.56.0 installed-copy write is named only parenthetically, not as a discrete tracked deliverable.** design.md asserts "In-repo ↔ installed forward-synced per MCFS-1"; Scope-check deliverable (3) says "one v0.56.0 changelog entry (in-repo + installed)" — the installed-copy propagation is the Builder's intent but is parenthetical. Per slice-041 MCFS-1, `tools/methodology_changelog_forward_sync.py` whole-file-compares at /build-slice Step 6, so an in-repo-only v0.56.0 entry is a Step-6 FAIL. The first Critic's M1 covers only the missing per-version *test*, not the explicit installed-copy *write*. Recommend folding into M1's post-B1 redesign as an explicit discrete sub-deliverable, not left implicit. Minor (completeness of deliverable spec).

## Severity adjustments

No severity adjustments. B1=Blocker, M1/M2/M3=Major, m1/m2=Minor are all correctly calibrated. M-add-1 is filed Blocker-class (it reinforces B1's existing Blocker; it does not introduce a separately-dispositioned blocker but materially expands B1's scope and redesign option set).

## Notes

High confidence. The first Critic's pass is strong: it caught the central viability blocker, Builder-verified it against official docs rather than asserting it, and correctly ESCALATED rather than over-reaching into a unilateral abandon recommendation — zero false positives across 7 findings. The single substantive gap (M-add-1) is a precedence-asymmetry blind spot: the first Critic verified the *skill* precedence direction but generalized it to "skills/agents" without separately verifying agents, which resolve in the inverse direction. That asymmetry does not rescue the slice (skills still shadowed; the split-resolution state is arguably worse than a clean no-op), so EXTEND reinforces BLOCKED. The Builder has discharged the meta-Critic's stated reservation by independently WebFetch-confirming the subagent project>user direction before TRI-1.
