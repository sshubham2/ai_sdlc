# AI SDLC — Hybrid Pipeline

Spec-driven SDLC for AI implementers. Hybrid of phase-driven rigor (for knowable domains) and slice-driven iteration (for unknowable ones).

## Five principles

1. **Iterate per slice, not per phase.** Unit of work = one thin vertical cut delivered end-to-end.
2. **Risk-first ordering.** Slice 1 retires the most uncertainty, not whatever's easiest.
3. **Two AI personas.** Builder produces; Critic adversarially reviews.
4. **Reversibility-tagged decisions.** Lock expensive decisions late; lock cheap ones fast.
5. **Vault as commit metadata.** Living artifact; pre-commit hook detects drift.

See [principles.md](principles.md) for rationale.

## Three modes

`/triage` opens every project and chooses the mode:

| Mode | For | Pipeline shape |
|------|-----|----------------|
| **Minimal** | Solo dev, MVP, exploration, one-off scripts | Skip critique/user-test/drift-check. Lightweight slices. |
| **Standard** | B2C, small teams, product work | All skills per slice. User-test before design. |
| **Heavy** | Compliance, enterprise, regulated | Closer to waterfall. Contracts upfront. Full audit trail. |

**Default: Standard.** Upgrade to Heavy only when a compliance constraint demands upfront contracts. Downgrade to Minimal only when the cost of the pipeline itself exceeds the project.

## Macro shape

```
/triage                              ← decide mode, scope pipeline
  ↓
/discover (loop)                     ← concept ↔ user ↔ risk-spike
  ↓
[Build loop per slice:]
  /slice                             ← define thinnest valuable cut
  /design-slice                      ← just-enough spec for THIS slice
  /critique                          ← adversarial review (Critic persona)
  /build-slice                       ← execute with verification gates
  /validate-slice                    ← real device / real user / real data
  /reflect                           ← update vault with learnings
  ↓ next slice

[Continuous:]
  /drift-check                       ← pre-commit, catches spec rot
  /reduce                            ← complexity budget, forces simplification
```

Each loop produces **working code + updated spec**. No comprehensive validation at the end.

## Skills

All 22 skills are drop-in Claude Code skills at `skills/<name>/SKILL.md` with proper frontmatter (some carry support files: `/diagnose` has `assemble.py` + 11 pass templates; `/slice-candidates` has `build_backlog.py`).

### Phase 0: Open the project

| Skill | When | Purpose |
|-------|------|---------|
| [/triage](skills/triage/SKILL.md) | Greenfield (no code yet) | Picks mode, scopes pipeline, builds risk register, generates CLAUDE.md |
| [/adopt](skills/adopt/SKILL.md) | Brownfield (existing codebase) | Analyzes code, reverse-engineers initial vault, generates brownfield-aware CLAUDE.md. Use INSTEAD of /triage |

### Phase 1: Discovery

| Skill | Modes | Purpose |
|-------|-------|---------|
| [/discover](skills/discover/SKILL.md) | all | Concept + user + constraint exploration (merges concept-brainstorm + act-as P1 + tech-brainstorm) |
| [/risk-spike](skills/risk-spike/SKILL.md) | all | Validate risky assumptions with throwaway code on real environments — runs BEFORE design |
| [/heavy-architect](skills/heavy-architect/SKILL.md) | **Heavy only** | Upfront comprehensive vault — components, contracts, schemas, threat model, cost estimation, requirements, NFRs |
| [/user-test](skills/user-test/SKILL.md) | Standard, Heavy | Real user validation — mockup, prototype, or working slice |

### Phase 2: Slice design

| Skill | Purpose |
|-------|---------|
| [/slice](skills/slice/SKILL.md) | Define the next thinnest valuable cut |
| [/design-slice](skills/design-slice/SKILL.md) | Just-enough vault entries for this slice |
| [/critique](skills/critique/SKILL.md) | Adversarial review by separate AI persona (Agent tool) |

### Phase 3: Build + validate

| Skill | Purpose |
|-------|---------|
| [/build-slice](skills/build-slice/SKILL.md) | Execute with plan mode + continuous verification |
| [/validate-slice](skills/validate-slice/SKILL.md) | Reality check against actual device/user/data |
| [/reflect](skills/reflect/SKILL.md) | Capture learnings, update vault |

### Phase 4: Maintenance

| Skill | Modes | Purpose |
|-------|-------|---------|
| [/drift-check](skills/drift-check/SKILL.md) | all | Compare vault vs code, flag divergence (detect-only; pre-commit hook ready). Skips `slices/archive/` |
| [/sync](skills/sync/SKILL.md) | **Heavy only** | Bidirectional vault-code reconciliation — regenerates code-derived files (components, contracts, schemas) AND detects drift on the rest |
| [/reduce](skills/reduce/SKILL.md) | all (mandatory every 5 slices in Heavy) | Complexity budget — force simplification if exceeded |
| [/archive](skills/archive/SKILL.md) | all | Maintain `slices/_index.md` + `slices/archive/`. Auto-triggered by `/reflect` on slice completion; manual run (`--index-only`) to rebuild stale indexes. Convention: `slices/` = active only; all completed slices live in `slices/archive/`, found via `_index.md` lookup + `$PY -m graphify query` for deep semantic retrieval |
| [/critic-calibrate](skills/critic-calibrate/SKILL.md) | all | Meta-skill: every 10-20 slices, analyze "Missed by Critic" patterns across recent reflections and propose targeted updates to `critique/SKILL.md`. Human reviews; never auto-applies. Closes the Critic feedback loop systematically |
| [/status](skills/status/SKILL.md) | all | Orientation: compact macro-state summary (mode, active slice + stage, risk exposure, regression health, Critic calibration status, recommended next action). Use at session start, after time away, for handoff |
| [/repro](skills/repro/SKILL.md) | all | Bug-fix discipline: write failing test that reproduces the issue, confirm it fails, add to shippability.md BEFORE running `/slice` for the fix. Bug can't silently return once fixed |
| [/commit-slice](skills/commit-slice/SKILL.md) | all | Generate audit-grade commit message from slice artifacts (mission-brief + build-log + validation + ADRs). Conventional-commit format; Heavy mode adds sign-off + compliance lines. Optional `--merge` (per BRANCH-1) commits to current slice branch + no-ff merges back to default branch + safe-deletes slice branch |

## Vault structure (thin vault)

The vault holds **only what code can't carry**: decisions, rationale, risks, slice memory. Components, contracts, schemas, test plans, screens — those live in code (or auto-derived views like OpenAPI, type defs, AST queries via graphify).

This is deliberate. See [principles.md#5](principles.md) for the rationale; the short version: the same fact in two places drifts; fewer places = less drift.

### Standard / Minimal mode (the default)

```
architecture/
  CLAUDE.md                  # Auto-generated by /triage; pipeline enforcement
  triage.md                  # Mode + rationale + initial risks
  concept.md                 # What + who + constraints (one file; no separate actors/)
  risk-register.md           # Risks + spike status + reversibility tags
  decisions/                 # ADRs — the WHY of expensive decisions
    ADR-001-*.md             #   each tagged: reversibility: cheap | expensive | irreversible
  spikes/                    # From /risk-spike
    spike-*.md
  slices/                    # THE CORE
    _index.md                # THE lookup: active list + recent-10 + aggregated lessons + pointer to archive catalog
    slice-NNN-<name>/        # ACTIVE slices only (no reflection.md yet)
      milestone.md           # Rolling state file (updated by every skill); /status reads this first
      mission-brief.md       # Per-slice intent + ACs + risk-tier + critic-required + gates
      design.md              # Just-enough — references code locations, doesn't duplicate them
      critique.md            # Critic's review + Builder's responses (may be "skipped" for low-risk slices)
      build-log.md           # What was built, verification results
      validation.md          # Reality-check per AC + shippability catalog results
      (reflection.md appears → /reflect auto-archives the slice)
    archive/                 # ALL completed slices (auto-moved by /reflect)
      _index.md              # Full chronological catalog
      slice-001-<name>/      # Frozen history (milestone.md frozen as "complete")
      slice-002-<name>/
      ...
  user-tests/                # From /user-test (B2C only)
    <test-name>.md
  shippability.md            # Regression catalog — one critical-path test per slice, run by /validate-slice
  drift-log.md               # Drift events over time
  lessons-learned.md         # Accumulated insights, chronological
  critic-calibration-log.md  # Audit trail of /critic-calibrate runs
  changelog.md               # Pipeline-bypass log, if any

graphify-out/                # Query cache — multi-modal knowledge graph
  graph.json                 # AST + semantic + INFERRED edges over code, docs, papers, videos
  GRAPH_REPORT.md            # One-page digest: god nodes, communities, surprising connections
  vault-graph.json           # Separate vault graph (optional; for Heavy mode only)
```

## Graphify: the structural index layer

`/triage` and `/adopt` install graphify's Claude Code integration. After that:

- **PreToolUse hook** — nudges Claude to read `GRAPH_REPORT.md` before Glob/Grep (structure-aware navigation; the hook is a hint, not an interceptor)
- **Git hooks** — post-commit + post-checkout auto-rebuild the graph (stays fresh without manual work)
- **Multi-modal** — code + docs + papers (`from graphify.ingest import ingest` for URLs; the slash form `/graphify add <arxiv-url>` works inside Claude Code chat) + images + video/audio (transcribed locally with whisper, requires `[video]` extra)
- **Query modes**: `$PY -m graphify query "<keyword>"` (substring match, not semantic), `reachable --from=`, `blast-radius --from=`, plus inline `networkx.shortest_path` for path A→B since the CLI lacks `path` and `explain`
- **Sub-second structural queries** against a pre-built graph instead of re-scanning files

Every skill in this pipeline queries the graph instead of scanning files where possible. Full reference: [graphify-integration.md](graphify-integration.md).

**Deliberately NOT in the vault** (derived from code on demand):

- `components/` → read the code; or `$PY -m graphify code` for a graph view
- `contracts/` → auto-generated from OpenAPI / Pydantic / type defs
- `schemas/` → from data models / migrations
- `test-plan/` → tests are the plan
- `frontend/` → code structure shows screens; mission briefs reference them by path
- `actors/` → inline section in `concept.md` (one paragraph per actor); no separate files

If you find yourself wanting one of these, ask: would code (or a code-derived view) capture this better? Usually yes.

### Heavy mode (compliance / regulated / audit) — updated

Heavy mode keeps the thin vault as its persistent state. `/heavy-architect` produces only the **human-authored** files. Code-derived views (components, contracts, schemas) are **generated on-demand by `/sync`** before audits / releases — they don't persist between runs.

This is a deliberate change from prior design: maintaining 30+ hand-tended markdown files in sync with a living codebase is fool's errand. The honest approach — code is the truth; views over code are regenerated as needed.

Heavy vault adds these **human-authored** files to the thin vault:

```
architecture/
  (everything from thin vault, plus:)
  actors/
    <actor>.md               # one per actor with full role-play walkthroughs (human narratives)
  threat-model.md            # STRIDE per component (human risk rationale)
  cost-estimation.md         # per-component infra costs at 1K/10K/100K (human estimates)
  requirements.md            # functional requirements by actor (human intent)
  non-functional.md          # NFRs + compliance constraints (HIPAA/PCI/SOC2/GDPR — human mapping)
  diagrams.md                # Mermaid: system overview + sequence (human design intent)
  sync-log.md                # /sync execution history (audit trail)
```

**Transient — generated by `/sync` on-demand** (not in vault between runs):

```
  components/<component>.md  # generated from code AST/imports
  contracts/<integration>.md # generated from OpenAPI / route handlers / event annotations
  schemas/<entity>.md        # generated from data models / migrations
```

Before audit: run `/sync` → generates these views from current code. After audit: can delete or leave; next `/sync` regenerates. They're views, not source-of-truth artifacts.

Heavy mode pipeline:

```
/triage (Heavy) → /discover (full) → /risk-spike all → /heavy-architect → /user-test (if B2C)
  → [per slice with audit trails:]
    /slice → /design-slice (updates comprehensive vault inline) → /critique (mandatory + human sign-off)
    → /build-slice (compliance trail: test coverage report, sign-off, audit-grade commits)
    → /validate-slice (reproducible commands, timestamped evidence, QA sign-off)
    → /reflect (full vault updates including components/contracts/schemas)
  → [every 5 slices:] /reduce (mandatory in Heavy)
  → [every 5-10 slices:] /sync (regenerates components/contracts/schemas from code; detects drift on the rest)
```

## How the two-persona model works

Every slice uses two Agent personas, same underlying model, different roles:

- **Builder** (main thread): runs `/slice`, `/design-slice`, `/build-slice`, `/validate-slice`, `/reflect`
- **Critic** (spawned per `/critique` via Agent tool with `subagent_type: "critique"`): reads Builder's design + mission brief, attacks it adversarially, produces findings

Cost: ~20% more tokens per slice vs single-persona. Cheaper than building the wrong thing.

See [agents/critique.md](agents/critique.md) for the Critic system prompt and [skills/critique/SKILL.md](skills/critique/SKILL.md) for how the skill orchestrates the invocation.

## Architecture: skills, named subagents, and forks

Skills live at `skills/<name>/SKILL.md` and orchestrate the work. Some skills delegate to **named subagents** at `agents/<name>.md`; others can be **forked** to run in the background with full project context. Three categories:

| Skill | Pattern | Where the prompt lives | Why |
|-------|---------|------------------------|-----|
| `/critique` | Named subagent (fresh context) | `agents/critique.md` | Adversarial isolation — the Critic must NOT see the Builder's reasoning trail; that's what makes the review meaningful |
| `/critic-calibrate` | Named subagent (fresh context) | `agents/critic-calibrate.md` | Objective pattern analysis across past reflections; benefits from a clean read |
| `/diagnose` Step 6.5 | Named subagent (fresh context) | `agents/diagnose-narrator.md` | Synthesizes engaging executive summary for the diagnosis HTML; fresh context so it doesn't pollute the main /diagnose conversation |
| `/risk-spike` Step 2.5 | Named subagent (fresh context) | `agents/field-recon.md` | Web search noise stays out of main thread; agent returns findings + structured early-drop recommendation, main thread decides whether to skip the empirical test |
| `/risk-spike` (overall) | Fork (inherits context, runs in background) | Skill body | Steps 1–4, 6, 7 need project context (libraries, credentials, env); parallel risk validation is the killer use case |
| `/reduce` | Fork (inherits context, runs in background) | Skill body | Long-running complexity audit; user keeps moving while it runs |
| `/sync` | Fork (inherits context, runs in background) | Skill body | Heavy mode only; 1–3 min reconciliation is best done off the main thread |
| All other skills | Main thread | Skill body | Iterative user dialogue (slicing, design, build, validate, reflect) — these need conversation continuity |

**Forks require** `CLAUDE_CODE_FORK_SUBAGENT=1` in your environment (Claude Code v2.1.117+). Without the env var, the three fork-friendly skills run in the main thread instead — same outputs, just blocking. Without forks set up, you can still parallelize risk validation by running spike → spike → spike serially; you just lose the background-execution benefit.

**Named subagents** work without any env var configuration. The fresh-context isolation they provide is independent of the fork mechanism.

When `/critic-calibrate` proposes prompt improvements, the user edits `agents/critique.md` (NOT a skill file). The agent file is the load-bearing artifact for adversarial review — treat it like compiled code, not a comment.

## The mission brief vs sprint file

Instead of a 500-line sprint file per sprint, this pipeline produces a **1-page mission brief** per slice (embedded in [slice/SKILL.md](skills/slice/SKILL.md)) and relies on Claude Code's plan mode for execution details.

| Mission brief (persistent) | Plan mode (session) |
|----------------------------|---------------------|
| Acceptance criteria | Exact files to touch |
| Must-not-defer list | Task sequence |
| Verification commands | Current-code-aware details |
| Vault/contract refs | Plan visible to user for approval |

**Why**: the brief carries the discipline (gates, don't-defer, acceptance). Plan mode carries the groundedness (adapts to actual code seen at build time). Avoids the "500-line sprint file written against stale assumptions" failure mode.

See [templates/mission-brief.md](templates/mission-brief.md) (also embedded inline in [skills/slice/SKILL.md](skills/slice/SKILL.md)).

## How to iterate

- **Next feature** → `/slice` defines it, loop executes
- **Scope change mid-slice** → abandon slice folder, re-run `/slice`
- **Design wrong** → `/reflect` captures, next `/design-slice` incorporates
- **Drift detected** → `/drift-check` flags, resolve before next `/build-slice`
- **Complexity creeping** → `/reduce` forces a simplification slice

## Handoff between modes

Projects can change mode mid-life:

- **Minimal → Standard**: triggered when a user-facing UI emerges, or when a second dev joins
- **Standard → Heavy**: triggered when compliance / regulatory requirement surfaces
- **Heavy → Standard**: unusual but valid when a compliance burden is lifted

`/triage` can be re-run at any time; it preserves existing vault content and updates mode config.

## Getting started

```bash
cd your-project/
/triage "family expense tracker that syncs between two phones"
```

`/triage` asks ~5 questions, picks a mode, creates `architecture/triage.md` + initial risk register, and tells you what to run next.

## When NOT to use this pipeline

- **Pure research / data exploration**: notebooks don't need slicing
- **One-off scripts**: `/triage` → Minimal → tiny single slice → done
- **Codebases with established patterns**: the existing conventions are your spec; don't rewrite them into a vault

For everything in between (most product and internal-tool work), this pipeline's Standard mode is the default. For compliance-heavy work that demands comprehensive upfront contracts, use Heavy mode.
