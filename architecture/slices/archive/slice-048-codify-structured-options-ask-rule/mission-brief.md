# Slice 048: codify-structured-options-ask-rule

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none directly — generalizes an established N≥1 practice (memory `ask-via-structured-options.md` + ADR-048 slice-046 gate-specific precedent) into a first-class pipeline-wide discipline, closing a real Claude Code platform-UX gap (free-text asks emit no user notification, so a skill silently blocks without alerting the user).
**Test-first**: false  <!-- /design-slice picks the test strategy; the project's genuine-contrast prose-pin technique (aggregated-lessons L59/L69) is the expected approach but is a HOW decision -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Every pipeline skill that pauses for user input must ask via the `AskUserQuestion` tool as **structured options with a clearly-marked recommended choice** — never a bare free-text question — because Claude Code only surfaces a user-facing notification when an options prompt is presented; a plain free-text question executes silently and the user is never told the skill is blocked waiting on them. ADR-048 (slice-046) already mandates this for the single BFRD-1 confirm gate; this slice promotes it to a pipeline-wide discipline written into the project-root `CLAUDE.md` that `/triage` (Step 5b) and `/adopt` (Step 10) emit into every adopted/triaged project, and dogfoods it into this repo's own `CLAUDE.md`.

## Acceptance criteria

1. A named discipline rule (proposed RULE-ID **SOAD-1** — Structured-Options-Ask Discipline; final ID/classification confirmed at `/design-slice`) is added to `methodology-changelog.md` as a new version entry with a META-1-conformant header (em-dash U+2014 + ISO date); `VERSION` and `plugin.yaml` `version` bumped in lockstep (PMI-1 clean).
2. The `/triage` Step 5b **fresh** and **append** CLAUDE.md templates AND the `/adopt` Step 10 **fresh** and **append** CLAUDE.md templates (4 template blocks total) each carry the SOAD-1 rule, stating both the mechanic (structured options + a recommended choice; free-text via the tool's built-in fallback) and the rationale (Claude Code notifies only on options prompts).
3. This repository's own project-root `CLAUDE.md` carries the identical SOAD-1 rule (self-hosting dogfood, per the self-hosting discipline).
4. An ADR is appended recording the decision — generalizing ADR-048's gate-specific "structured options, not free-text" to a pipeline-wide skill-ask discipline; append-only, supersedes nothing.
5. A genuine-contrast regression test pins the SOAD-1 rule's presence in all 4 opener-skill template blocks + this repo's `CLAUDE.md` (FAILs pre-edit on the pinned phrase's absence, PASSES post-edit).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | RULE-ID + version bump | `$PY -m tools.plugin_manifest_audit` exit 0; `pytest tests/methodology/test_methodology_changelog.py` (META-1 header-split) green; `VERSION` == `plugin.yaml:version` |
| 2 | 4 opener template blocks carry the rule | `grep` the pinned SOAD-1 phrase in `skills/triage/SKILL.md` Step 5b fresh+append blocks and `skills/adopt/SKILL.md` Step 10 fresh+append blocks → 4 hits; CAD/mini-CAD drift guards for those SKILL.md files still green (installed copies forward-synced) |
| 3 | This repo's CLAUDE.md carries the rule | `grep` the pinned phrase in `./CLAUDE.md` → 1 hit |
| 4 | ADR recorded | New `architecture/decisions/ADR-NNN-*.md` exists, references ADR-048 as the gate-specific precedent, `supersedes:` empty |
| 5 | Genuine-contrast regression test | Run the new test against the pre-edit tree (or simulated absence) → FAIL; against post-edit tree → PASS; included in `/validate-slice` Step 5.5 shippability catalog |

## Must-not-defer

- [ ] The rule text MUST state the **rationale** (notification only on options prompts), not just the mechanic — otherwise a future maintainer strips it as redundant boilerplate.
- [ ] BOTH `fresh` AND `append` template blocks in BOTH opener skills (4 blocks) — not fresh-only; the append path governs every project that already has a CLAUDE.md.
- [ ] CAD-1 / mini-CAD in-repo↔installed parity for `skills/triage/SKILL.md` + `skills/adopt/SKILL.md` (forward-sync installed copies; EOL-agnostic per ADR-033).
- [ ] The rule MUST preserve the legitimate free-text escape hatch (ADR-048's verbal-claim-with-path fallback where `AskUserQuestion` genuinely cannot model the input) — SOAD-1 mandates structured options as the *primary/default* ask form, not an absolute ban.
- [ ] methodology-changelog META-1 header shape (em-dash + ISO date) + shippability-catalog propagation (RPCD-1/SCPD-1) for the new regression test.

## Out of scope

- Retrofitting the existing 24 skills' "ask the user" prose to the `AskUserQuestion` form (user-decided deferral — the CLAUDE.md contract governs skill behavior; a per-skill prose sweep is a separate, larger slice).
- An executable lint/audit that scans skill prose for free-text-ask anti-patterns (future slice; this slice ships the CLAUDE.md contract + opener-wiring + regression pin only).
- The user's personal `~/.claude/CLAUDE.md` (user chose the pipeline-generated project-CLAUDE.md surface; the openers do not manage the personal global file).

## Dependencies

- Prior slices: [[slice-046-add-conditional-repro-auto-advance]] — ADR-048 is the gate-specific "structured options, not free-text" precedent this generalizes.
- Vault refs: [[decisions/ADR-048]]; new ADR appended this slice.
- Skill surfaces: `skills/triage/SKILL.md` Step 5b (fresh + append), `skills/adopt/SKILL.md` Step 10 (fresh + append).
- Methodology: `methodology-changelog.md`, `VERSION`, `plugin.yaml` (PMI-1), `tools/install_audit.py` (INST-1 — only if the new test is a tool; otherwise untouched).
- Originating feedback: user memory `ask-via-structured-options.md` (informational — the user-stated rationale driving this slice).

## Mid-slice smoke gate

At ~50% of build (after the 4 template blocks + this repo's CLAUDE.md are edited, before the changelog/VERSION bump is finalized):
```
grep -l "<pinned SOAD-1 phrase>" skills/triage/SKILL.md skills/adopt/SKILL.md ./CLAUDE.md
$PY -m tools.plugin_manifest_audit
```
Expected: the pinned phrase present in all targeted surfaces (4 template blocks + repo CLAUDE.md); PMI-1 exit 0 once VERSION/plugin.yaml are bumped. If a surface is missing or PMI-1 fails: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
