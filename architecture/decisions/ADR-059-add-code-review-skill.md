---
id: ADR-059
title: Add /code-review as in-loop walking-skeleton step between /build-slice and /validate-slice; mint RULE-ID CRSI-1; findings advisory only in v1 (TRI-1 gate + AI-bloat passes + verdict-driven block deferred to slices 061/062)
date: 2026-05-23
slice: slice-060-add-code-review-skill
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-059: Add `/code-review` as in-loop walking-skeleton step

## Context

The AI SDLC pipeline today exercises **five** distinct review surfaces, but the per-slice loop has no **adversarial code-level review of the just-written code**. The surfaces (grounded read at /query-design on 2026-05-23):

1. `/critique` + `/critique-review` (`skills/critique/SKILL.md`, `skills/critique-review/SKILL.md`) — review the **design** (mission-brief + design.md + new ADRs) BEFORE any code is written. Two-persona separation. Output blocks `/build-slice`.
2. `/build-slice` Step 6 pre-finish gates (`skills/build-slice/SKILL.md:136-156`) — **structural** properties only: branch state, encoding, version sync, manifest integrity, mock-budget, wiring matrix, test-first plan completion, etc. (16+ deterministic Python audits). NOT line-level code review.
3. `/validate-slice` VAL-1 layers (`skills/validate-slice/SKILL.md:116-149`) — **narrow** code-level safety: Layer A static-regex credential scan + Layer B Python AST dependency-hallucination check. Both deterministic, both narrow.
4. `/validate-slice` real-environment + shippability catalog — **behavior**: does the slice actually work on a real device/user/data; does it break any prior slice?
5. `/diagnose` — **whole-codebase** forensic review with 11 passes (dead code, duplicates, oversized functions, half-wired features, AI-bloat signatures). Heavyweight HTML deliverable. **Explicitly out-of-loop.**

The gap: there is no in-loop adversarial review of the **code diff** for a single slice — no line-level, file-by-file pass applying the same dimensions /critique applies to design. Two distinct AI-driven-coding failure classes go uncaught at slice-time today (per /critique m3 — more precise framing than the original draft):

1. **Dead-code that lands in a single slice and persists** because no per-slice code review ran. `diagnose-out/backlog.md` SC-022 (`_read_text` defined-never-called) and SC-025 (`severity_class` defined-never-called) are this class — each landed in ONE slice and stayed latent until `/diagnose` swept the whole repo. Per-slice review at lag 1 addresses this class directly.
2. **Multi-impl parallel-copy duplication that compounds across slices** — each slice adds a parallel implementation of the same capability, and the duplication is only visible by comparing across slices. SC-017 (parallel-copy duplication clusters) is this class. Slice-060's walking-skeleton doesn't address this directly (it reviews single-slice diff); slice-061's AI-bloat passes (the cross-slice rumination dimension) close this class.

The slice-060/061/062 split tracks these two classes plus the disposition gate: 060 catches the single-slice class; 061 catches the multi-slice class; 062 forces disposition discipline via TRI-1.

Closing this gap requires a new in-loop step. The structural choice is whether to (a) add it in-loop (changes canonical PCA-1 chain), (b) add it out-of-loop (peer to `/diagnose`, `/pulse`, `/query-design`), or (c) extend `/critique` to also review code (collapse the two persona separations).

## Options considered

### 1. In-loop step between `/build-slice` and `/validate-slice` (CHOSEN)

- **Pros**: Findings reach the user at the moment they're introduced (lowest fix cost); auto-advance via PCA-1 means no user friction; per-slice cadence matches the "AI-bloat compounds silently" failure mode; structurally analogous to `/critique` + `/critique-review` (review BEFORE code) — symmetric coverage with `/code-review` (review AFTER code).
- **Cons**: Requires canonical PCA-1 chain change (`_CANONICAL_CHAIN` tuple-of-tuples 2-line edit); adds one agent invocation per slice (~20% token cost per `/critique`'s figure); structural change requires the bootstrap-discharge mechanism (slice-026/slice-027 precedent).

### 2. Out-of-loop user-invokable skill (peer to `/diagnose`, `/pulse`, `/query-design`)

- **Pros**: No PCA-1 chain change; lower-risk introduction; user opts in per slice.
- **Cons**: Defeats the value proposition — if `/code-review` is opt-in, it gets forgotten, and AI-bloat continues to compound silently exactly as today. The /query-design conversation surfaced the gap PRECISELY because the user noticed the in-loop absence; opt-in would not close it. Also: opt-in means the BCR-1-style cross-slice loop (slice-053) does not gain a structural axis.

### 3. Extend `/critique` to also review code (collapse two persona separations)

- **Pros**: No new skill, no new agent, no chain change.
- **Cons**: Violates the two-persona separation by responsibility — design Critic at `/critique` runs BEFORE code exists; code Critic must run AFTER code exists. They cannot be the same agent invocation; they have different inputs (design.md vs slice diff), different output formats (design findings vs code findings), and different gate semantics (BLOCKED → redesign vs BLOCKED → fix-code-or-defer). Collapsing would either require running `/critique` TWICE (once pre-code, once post-code — same effective cost as a new skill) OR weakening the design-Critic discipline by mixing concerns. Neither is cheaper than option 1.

### 4. Status-quo + periodic /diagnose

- **Pros**: No methodology change.
- **Cons**: The /query-design conversation already established this is insufficient. /diagnose at cadence N catches AI-bloat at lag N, not at lag 1; the failures compound. SC-017/022/025 in the current backlog are evidence: each ONE slice introduced the AI-bloat that /diagnose caught later. Per-slice review at lag 1 is structurally cheaper than catching N slices of compound.

## Decision

**Adopt option 1: `/code-review` is a new in-loop walking-skeleton step between `/build-slice` and `/validate-slice`.**

The walking-skeleton scope (chosen by the user at /slice Step 5 via structured options) ships the structural foundation end-to-end — skill + agent + PCA-1 chain edge + self-hosting drift guards (CAD-1 family member-add for the agent via the slice-049/051 OSDG-1 pattern + OSDG-1 family member-add for the skill) + shippability catalog row + methodology surface — but **findings are advisory only** in v1. No AI-bloat passes (deferred to slice-061), no TRI-1 user triage gate (deferred to slice-062), no verdict-driven block on `/validate-slice` (deferred to slice-062). The walking-skeleton self-dogfoods on slice-060 itself: invoking `/code-review` against slice-060 produces `architecture/slices/slice-060-add-code-review-skill/code-review.md` with non-empty findings before the slice declares done.

A new RULE-ID **CRSI-1** (Code-Review Skill Insertion) is minted to record the methodology-surface insertion in `methodology-changelog.md` v0.64.0.

The agent (`agents/code-review.md`) inherits the structural template from `agents/critique.md`: same 9 dimensions (reframed for code, not design — explicit reframing table in design.md "## 9 dimensions reframed for code"), same framework citations, same specificity rule, same output format, same tool set (`Read, Glob, Grep, Bash, WebSearch`), same model (`opus`). The skill (`skills/code-review/SKILL.md`) inherits the orchestration template from `skills/critique/SKILL.md`: Agent-tool spawn with `subagent_type: "code-review"`, hand-the-agent-the-inputs discipline, write-findings-to-`code-review.md`, `## Pipeline position` block.

**Read-only stance** (load-bearing safety invariant — per /critique m4 platform-evidence citation): the agent's tool set omits `Write`, `Edit`, `NotebookEdit`. Enforcement relies on Claude Code's **subagent**-frontmatter `tools:` field being a hard runtime constraint (per [Claude Code docs — Create custom subagents](https://code.claude.com/docs/en/sub-agents); confirmed via [Tembo's 2026 subagent guide](https://www.tembo.io/blog/claude-code-subagents) — "hard constraint, not a naming convention or a prompt instruction"). The **skill**-frontmatter `allowed-tools` field has known enforcement issues per GitHub [anthropics/claude-code#18837](https://github.com/anthropics/claude-code/issues/18837) — but this slice uses **subagent** frontmatter (not skill frontmatter) for the access-control surface, so the bug does not affect us.

## Consequences

### What this slice ships

1. `skills/code-review/SKILL.md` + installed copy at `~/.claude/skills/code-review/`.
2. `agents/code-review.md` + installed copy at `~/.claude/agents/code-review.md`.
3. `tools/pipeline_chain_audit.py` `_CANONICAL_CHAIN` extended with the new edge (2-line tuple change).
4. `skills/build-slice/SKILL.md` Pipeline-position successor flipped to `/code-review`.
5. `skills/validate-slice/SKILL.md` Pipeline-position predecessor flipped to `/code-review`.
6. `tools/install_audit.py` `_CANONICAL_SKILLS` + `_CANONICAL_AGENTS` extended (one entry each).
7. `plugin.yaml` enumerated with the new skill + agent; `version:` bumped 0.63.0 → 0.64.0.
8. `methodology-changelog.md` `## v0.64.0` entry referencing CRSI-1 + ADR-059.
9. `architecture/shippability.md` new row for the walking-skeleton self-dogfood regression guard.
10. `VERSION` 0.63.0 → 0.64.0; **5-part** PMI-1 atomic bump (VERSION + plugin.yaml.version + **pyproject.toml `[project].version`** + installed `~/.claude/ai-sdlc-VERSION` + installed `~/.claude/methodology-changelog.md`) — per /critique B2; pyproject.toml leg restored to enumeration; PVFS-1 (slice-054 / ADR-056) gate exits 0 at Step 6.
11. Test suite: 16 new failing-tests-first rows mapped to the 5 ACs (per the mission brief TF-1 plan).

### What CRSI-1 enables (downstream slices)

- **slice-061**: ports `/diagnose`'s AI-bloat pass templates (multi-impls / half-wired modules / stale scaffolding / session-break inconsistency) into `/code-review`, scoped to the slice diff. Builds on CRSI-1's skill+agent without changing the chain.
- **slice-062**: adds the TRI-1-style user triage gate (Builder draft dispositions → user ratification → final verdict mechanic) + verdict-driven block on `/validate-slice` predecessor entry. Changes `/code-review`'s Pipeline-position user-input-gates list (currently empty → BLOCKED-HALT).

### What CRSI-1 does NOT do

- **No changes to `/critique` or `/critique-review`** — those review DESIGN; `/code-review` reviews CODE. Separate concerns, separate agents.
- **No changes to `/validate-slice` Step 5b VAL-1 layers** — credential scan and dependency-hallucination check stay deterministic and narrow; `/code-review` does NOT subsume them.
- **No `--force` / `--skip` flag** in v1 — every slice runs `/code-review`. If a slice has no code changes (vault-only), the empty-diff handling writes a minimal `code-review.md` with `Result: NO-CODE-CHANGES` and auto-advances cleanly. Skip-via-flag is a slice-061+ extension if N≥3 vault-only slices accumulate.
- **No `/critic-calibrate` extension** for code-review accuracy tracking in v1 — defer until N≥10 slices of operation per the slice-037 precedent ("don't add Critic dimensions for build-time-reachable classes; the gates work — accumulate evidence first"). A future `/critic-calibrate`-route proposal can extend the calibration loop once a track record exists.
- **No retroactive migration** of archived slices — slice-060 onward only.

### PCA-1 bootstrap-discharge

Slice-060 itself authors the new chain shape. At slice-060's own `/build-slice` Step 6 pre-finish, the PCA-1 audit MUST exit 0 against the post-slice-060 9-entry `_CANONICAL_CHAIN`. The bootstrap-discharge is the self-application proof — identical mechanic to CRP-1 slice-026 and PCA-1 slice-027. Every slice after 060 inherits a self-gating PCA-1 against the new chain.

### Risks

- **Cost**: one additional agent invocation per slice (~20% token cost per the `/critique` figure). For a 30-slice quarter at current rates, this is meaningful but not blocking. The user accepted this trade-off at `/query-design` and again at `/slice` Step 5.
- **False positives on advisory-only findings**: in v1 with no TRI-1 gate, every finding is visible but none blocks. The risk is finding fatigue ("the code-review agent always flags X") leading to ignored output. Mitigation: slice-061's AI-bloat passes raise the signal-to-noise ratio; slice-062's TRI-1 gate forces explicit disposition per finding (same calibration discipline as /critique).
- **Build-time-unreachable classes** (slice-037 law): some code-review concerns require runtime behavior (concurrency, race conditions, platform-specific edge cases) that the agent cannot directly observe. Slice-037 / slice-038 / slice-044 / slice-050 / slice-051 / slice-052 / slice-053 / slice-054 / slice-055 confirmed N≥9 that adding dimensions for build-time-unreachable classes does NOT improve coverage — `/validate-slice`'s real-environment check is the durable backstop. ADR-059 inherits this discipline: the 9 dimensions stay design-derived; the agent does NOT speculate about runtime behavior.

## Reversibility

**Cheap.** The chain edge is one `_CANONICAL_CHAIN` 2-line tuple change to undo. The skill + agent files are deletable. The drift-guard tests are removable. `tools/install_audit.py` canonical tuples revert with one-entry edits each. `plugin.yaml` reverts with one-section edits. `methodology-changelog.md` is append-only (a future SUP-1 supersession entry would record the reversal, not edit v0.64.0 in place). No external API consumers exist. No data model changes. No production-facing surface.

If `/code-review` proves cost-prohibitive or low-value after N slices of operation, a future slice can retire CRSI-1 via supersession-by-new-ADR + the SUP-1 mechanic. The retirement slice's diff is a near-exact inverse of slice-060's diff plus the new ADR — total cost ≤ 1 day, no migration burden.
