# Principles

Five principles this pipeline is built on. Every skill traces back to one or more.

## 1. Iterate per slice, not per phase

**Principle**: The unit of work is one thin vertical cut delivered end-to-end, not a horizontal step across the whole system.

**Why**: You learn what to build by building. Phase-driven pipelines lock design decisions before you have evidence. By the time validation runs, the wrong thing is built at scale.

**How**: `/slice` defines the next cut. `/design-slice` scopes the spec to that cut only. `/build-slice` ships it. `/reflect` captures what reality taught you before the next cut. Each cycle = working code + updated spec.

**Counter-principle**: For compliance-driven work where contracts must be defined upfront (think FDA, HIPAA, banking), Heavy mode relaxes this — contracts are frozen before any slice runs. But even then, slices remain the execution unit.

---

## 2. Risk-first ordering

**Principle**: Slice 1 is whatever retires the most uncertainty, not whatever's easiest.

**Why**: Projects die from unknown-unknowns discovered late. Build the scary thing first — novel auth, unproven API, new UX pattern, cross-device sync. If it works, everything else is execution. If it doesn't, you pivot cheaply before committing to a design built on the broken assumption.

**How**: `/triage` builds the risk register. `/slice` selects the next cut by risk, not dependency order. `/risk-spike` runs before design when the risk can be validated without full implementation (a 30-min spike beats an 8-sprint rebuild).

**Counter-principle**: When risks are comparable or already retired, slice by user value. Don't manufacture risk to justify ordering.

---

## 3. Two AI personas

**Principle**: Builder produces; Critic adversarially reviews. Same underlying model, different roles and prompts.

**Why**: Same AI on both sides of a quality gate is the bootstrapping problem. AI writes a spec → same AI validates the spec → same AI builds from the spec. Errors propagate silently because the validator shares the writer's blind spots.

**How**: `/critique` invokes a **named subagent** (`subagent_type: "critique"`) defined at `~/.claude/agents/critique.md`. The agent file carries the load-bearing adversarial prompt — stance, the 8 attack dimensions (each grounded in a named expert framework: Wiegers for requirements, Fowler for refactoring smells, Newman for service contracts, OWASP + McGraw for security, Hendrickson / Bach / Bolton for edge case heuristics, Patton, Cockburn, Beck, Sommerville, plus Dimension 8 — web-known issues — using live `WebSearch`), specificity rule, honesty rule, output format. Citation-based grounding shifts the model from blended training-data heuristics to specific vetted methodology. The skill orchestrates (gathers inputs, writes the result); the agent does the work. Same pattern for `/critic-calibrate`, the meta-skill that mines past misses to propose Critic prompt improvements (`~/.claude/agents/critic-calibrate.md`). Both agents run with **fresh context** — no carryover from the Builder's reasoning trail. That isolation is what makes adversarial review meaningful; a fork (which inherits parent context) would defeat it.

**Cost**: ~20% more tokens per slice. Cheaper than building the wrong thing.

**Failure mode to watch**: Critic becomes a rubber stamp if its prompt is too mild. The prompt must explicitly instruct adversarial stance and *rank* findings, so "no issues found" is a deliberate statement, not the default.

---

## 4. Reversibility-tagged decisions

**Principle**: Each decision gets a reversibility tag — `cheap`, `expensive`, or `irreversible`. Cheap-to-change → lock fast. Expensive-to-change → lock late, after evidence.

**Why**: Not all decisions are equal. Locking a UI color is free; locking a database schema or API contract is a migration. Treating all decisions the same forces early commitment on expensive things before evidence exists to support them.

**Examples**:

| Decision | Reversibility | When to lock |
|----------|---------------|--------------|
| UI design tokens (colors, spacing) | cheap | `/triage` or first frontend slice |
| Logging format | cheap | First slice that logs |
| Framework choice (React vs Vue) | expensive | After `/discover` confirms team fit |
| Database choice (Postgres vs Mongo) | expensive | After `/risk-spike` if any data model is novel |
| API contract (versioned public API) | expensive | After 2+ slices exercise the endpoints |
| User identity model | irreversible | Only after user research / `/risk-spike` |
| Tenant model (single / multi) | irreversible | Only with strong evidence |

**How**: Every ADR has a `reversibility:` frontmatter field. `/design-slice` only locks expensive decisions when the slice *needs* them; cheap ones lock early to unblock work.

---

## 5. Thin vault — AI memory, not system documentation

**Principle**: The vault contains only what code can't carry: decisions and rationale (ADRs), risks and reversibility tags, slice intent + critiques + validation + reflection, project mode + concept. Everything else — components, contracts, schemas, test plans, screen catalogs — lives in code where it can't drift.

**Why**: The biggest failure mode of spec-driven SDLC is spec rot. The deeper cause: trying to document what code already shows. Component descriptions, contract schemas, test plans, screen catalogs drift not because discipline is weak, but because the same fact lives in two places (code + vault) that want to diverge. The cure is fewer places, not more discipline.

**Reframe**: think of the vault as the **AI's project memory across sessions**, not the project's documentation for new readers. Different design constraints follow:

- AI memory needs to capture: decisions made (so it doesn't relitigate), risks (so it doesn't re-discover), slice history (so it knows what's done), reflections (so it learns)
- AI memory does NOT need to capture: every component, every endpoint, every test — those are derivable from code

**The split**:

- **Code is the source of truth for "what"** — components, contracts, data shapes, test coverage, frontend structure
- **Vault is the source of truth for "why"** — decisions, rationale, risks, intent, learnings

**How**:

- Vault contains: `triage.md`, `concept.md`, `risk-register.md`, `decisions/ADR-*.md`, `slices/slice-NNN-*/...`, `spikes/`, `lessons-learned.md`
- Vault deliberately does NOT contain by default: `components/`, `contracts/`, `schemas/`, `test-plan/`, `frontend/` — these are derived from code on demand (OpenAPI, type defs, AST queries via graphify, AI synthesis)
- `/drift-check` still runs but on the thin surface — checks that ADR-claimed libraries are still in dependencies, contract claims in slice designs match endpoints, etc.
- `/reflect` updates decisions and risks; rarely needs to update component-style docs (they don't exist)

**Heavy mode behavior** (refined): compliance / regulated domains need comprehensive audit artifacts. But maintaining 30+ hand-tended markdown files in sync with living code is fool's errand — they'll drift.

The honest Heavy mode: `/heavy-architect` produces only human-authored files (threat model, cost estimation, requirements, NFRs, diagrams, actor narratives). Code-derived artifacts (components, contracts, schemas) are **generated on-demand by `/sync`** right before audits — from current code. Between audits they don't exist as vault files. This keeps the Thin Vault principle intact even in Heavy mode: code is the source of truth for "what"; views over code are regenerated, not maintained.

**Failure mode to watch**: even thin vault rots if `/reflect` is skipped. Drift-check on the thin surface is faster (smaller surface = sub-second pre-commit hook), so there's less excuse to bypass.

**Graph as structural index**: `/triage` and `/adopt` install graphify — a multi-modal knowledge graph over code + vault + external references (papers, docs, videos). Skills query the graph instead of scanning files when reachability/blast-radius/keyword queries are needed. The graph doesn't replace vault or code; it's a queryable index over both. Rationale comments in code (`# WHY:`, `# NOTE:`) become graph edges alongside vault ADRs — so the "why" lives in both places and is queryable in one. See [graphify-integration.md](graphify-integration.md).

---

## What these principles reject

- **Waterfall-as-default**: encoding "specs come first, exhaustively" as the only mode misapplies it to projects where the spec itself is unknown. We treat that as one mode (Heavy), not the default.
- **Single-AI quality gates**: one AI writing and another part of the same AI validating is theater, not review.
- **Artifact completeness as a goal**: a vault with 200 files and stale claims is worse than one with 20 files that match reality.
- **Phase gates as milestones**: the only milestone is working software that a real user/device has touched.

## What these principles are honest about

- **Slice-driven has its own failure modes**: losing sight of the whole, building inconsistently across slices, accumulating tech debt. `/reduce` and `/drift-check` are the counterweights, but discipline is still required.
- **Two-persona costs tokens**: and the Critic isn't perfect. Calibration happens over time by tracking `/reflect`'s "critic calibration" section.
- **Heavy mode exists because these principles don't always fit**: compliance domains genuinely need upfront contracts. Don't force slice-driven where it's wrong.
