# Authoring named subagents

This guide explains how to create or modify a **named subagent** for the AI SDLC pipeline. Named subagents are a load-bearing pattern — they let a skill delegate work that needs *fresh context* (like adversarial review where the Critic must not see the Builder's reasoning trail) or *specialized prompts* (like the diagnose-narrator's storytelling discipline).

If you're not adding a new subagent, you don't need to read this. The agent files at `agents/<name>.md` are themselves the canonical examples.

## Three patterns for delegating work

The pipeline uses three distinct delegation patterns. Pick the right one before adding a subagent.

| Pattern | Context | Use when |
|---------|---------|----------|
| **Named subagent** (`subagent_type: "<name>"`) | Fresh — no parent thread context | The work *requires* isolation from the parent (adversarial review, objective pattern analysis) OR needs a stable prompt across invocations |
| **Fork** (`Agent` without `subagent_type`) | Inherits parent fully | The work needs full parent context (libraries, credentials, slice state) AND benefits from background execution |
| **General-purpose dispatch** (`subagent_type: "general-purpose"`) | Configurable per call | The work is one-off, doesn't need a stable role, just needs a fresh model run with an explicit prompt |

If unsure: named subagent if the role recurs across slices; general-purpose if the work is one-off; fork if context inheritance is the point.

## When a named subagent is the right answer

You should write a named subagent when ALL of these hold:

1. **The role recurs.** Multiple skill invocations should use the same prompt. If used once, dispatch general-purpose with an inline prompt.
2. **The role has a stable contract.** Inputs and outputs are defined enough that the prompt you write today still works in 20 invocations.
3. **Fresh context is load-bearing OR consistency is load-bearing.** Either the role MUST not see parent context (adversarial isolation) or you want every invocation to behave identically (no slice-history bias).
4. **The prompt is non-trivial.** If the prompt is two sentences, it's not worth the file overhead. A five-paragraph adversarial stance with calibration awareness is.

The four existing agents fit all four criteria. Don't add a fifth lightly.

## File location and naming

- Path: `agents/<kebab-name>.md` at the AI SDLC repo root
- The `<kebab-name>` MUST match the `name:` frontmatter field
- `INSTALL.md` Step 3f copies all `agents/*.md` to `~/.claude/agents/` automatically — no install changes needed when you add an agent

## Frontmatter spec

Every named subagent file starts with YAML frontmatter:

```yaml
---
name: <kebab-name>
description: <one paragraph>
tools: <comma-separated tool list>
model: <opus | sonnet | haiku | inherit>
---
```

### Required fields

**`name`** — kebab-case identifier. Must match the filename stem (without `.md`). Used as `subagent_type:` value when invoking via the Agent tool.

**`description`** — one paragraph. The first sentence is the agent's role; subsequent sentences cover stance ("adversarial," "honest"), inputs ("expects slice artifacts as input"), constraints ("read-only — never modifies code"), and the invoking skill ("Use ONLY when invoked by the /critique skill"). The harness shows this to the spawning agent so it can decide when to invoke. Keep it under ~250 words; it's read on every consideration.

**`tools`** — comma-separated list of tools the agent has access to. Match this to the actual work:
- Adversarial review / pattern analysis: `Read, Glob, Grep, Bash, WebSearch` (read-only + web)
- Web survey only: `Read, WebSearch`
- Narrative synthesis with output: `Read, Glob, Grep, Write`

The agent CANNOT use a tool not listed. If you grant `Edit` or `Write` to a read-only role (Critic, Meta-Critic), you've broken the contract.

**`model`** — one of:
- `opus` — synthesis, adversarial reasoning, narrative writing (current default for all 4 agents)
- `sonnet` — guided extraction, structured generation
- `haiku` — template filling, structured-data rendering
- `inherit` — match the spawning agent's model

Pick by **cognitive demand**, not by performance preference. If the agent does adversarial reasoning, it's `opus`. If it fills a template from JSON, it's `haiku`. The Phase 2 cost-optimization slices in the methodology roadmap revisit per-skill model selection systematically.

### Optional fields

None currently. Keep the frontmatter minimal.

## Tool-selection rules

**Read-only roles MUST NOT have write tools.** The Critic, Meta-Critic, and Field Recon agents do not have `Edit`, `Write`, or any other state-mutating tool. Their contract is to *return* recommendations, not apply them.

**Roles that produce a deliverable need `Write`.** The diagnose-narrator writes `sections/00-overview.md`. That's its job. Granting `Write` is correct — and the prompt explicitly limits *which* file it writes.

**`Bash` requires explicit justification.** The Critic has `Bash` for graphify queries (`$PY -m graphify query "..."`). It does not use it for anything else, and the prompt says so. If you grant `Bash`, document the bounded use in the prompt body.

**`WebSearch` is for live external data only.** The Critic uses it for Dimension 8 (web-known issues). The Field Recon agent uses it for the entire job. Don't grant it to roles that don't actually search the web.

## Prompt structure conventions

Successful named-subagent prompts follow a consistent shape:

1. **Role line** — "You are the [role]" — first line of the body, no preamble
2. **Stance** — one short paragraph naming the disposition ("adversarial," "pattern-finder, not advocate," "forensic, not flattering")
3. **Inputs you'll be given** — what the spawning skill hands the agent
4. **Method or dimensions** — for adversarial review, the dimensions table; for synthesis, the narrative shape; for survey, the query plan
5. **Hard rules / specificity rule / honesty rule** — the constraints that make the role load-bearing; pin canonical phrases here (these are what self-tests verify per **META-2**)
6. **Output format** — exact shape of what the agent returns
7. **What you DO NOT do** — explicit forbidden actions (mutation, paraphrasing, manufacturing findings)
8. **Common failure modes** — patterns the agent should avoid (rubber-stamping, generic findings, severity inflation)
9. **Calibration awareness** — how the agent's outputs feed back into improvement (if applicable)

The four existing agents conform to this shape. New agents should too.

## Calibration awareness pattern

If your agent's output is later validated (PASS / FAIL / FALSE ALARM / MISSED), the agent's prompt should reference the calibration loop. Pattern:

> Your findings are tracked in [downstream artifact] after [validation step]. Three outcomes per finding:
> - **VALIDATED**: reality confirmed your concern
> - **FALSE ALARM**: turned out to be a non-issue (you over-reached)
> - **MISSED**: something surfaced that you should have caught (you under-reached)
>
> Patterns across [N invocations] feed [calibration mechanism]. Be honest about uncertainty.

The Critic and Field Recon agents both use this pattern. It's what enables `/critic-calibrate` to mine misses systematically.

## Self-tests are required

Per **META-2** (`methodology-changelog.md` v0.2.0), every load-bearing rule in the agent's prompt must have a corresponding self-test that pins its canonical phrase. When you add a new agent:

1. Add a `tests/methodology/test_<name>_agent.py` with one test per load-bearing rule
2. Each test asserts the canonical phrase appears in the file
3. Each test docstring names the **defect class** and **rule reference**
4. Run `pytest tests/methodology/ -v` and confirm all tests pass

The four existing agents have ~14 tests collectively. Yours doesn't need that many — pin the *load-bearing* phrases (stance, hard rules, forbidden patterns), not every sentence.

Per **META-3**, the agent's frontmatter conformance is automatically tested by `tests/methodology/test_agent_frontmatter.py` (parametrized over all `agents/*.md` files except this one). You don't need to add frontmatter tests yourself; the parametrized test picks up new agents automatically.

## Adding to the install pipeline

Nothing to do. `INSTALL.md` Step 3f globs `agents/*.md` and copies all of them. Your new agent is included automatically.

## Adding a changelog entry

Per **META-1**, every behavior-changing addition gets a changelog entry. New named subagent = new behavior = new entry:

```markdown
## v<bumped-version> — <YYYY-MM-DD>

### Added

- **<RULE-ID> — Add <name> subagent**
  <One-paragraph description of what the agent does, when it's invoked, and what it returns>
  - **Rule reference**: <RULE-ID>
  - **Defect class**: <what bad behavior the agent prevents — e.g., "single-AI quality gate" or "blended training-data heuristics for survey">
  - **Validation**: `tests/methodology/test_<name>_agent.py` runs cleanly. `tests/methodology/test_agent_frontmatter.py` covers frontmatter conformance.
```

## Examples

The four existing agents cover the main patterns:

| Agent | Pattern | Why a named subagent |
|-------|---------|----------------------|
| `agents/critique.md` | Adversarial review (9 dimensions, expert frameworks) | Fresh context isolation — Critic must not see Builder's reasoning trail |
| `agents/critic-calibrate.md` | Meta-pattern analysis across reflections | Objective read; benefits from clean context |
| `agents/diagnose-narrator.md` | Narrative synthesis from structured findings | Specialized storytelling discipline; doesn't pollute /diagnose conversation |
| `agents/field-recon.md` | Live web survey with asymmetric drop rule | Web search noise stays out of main thread; recommendation is structured |

Read each before authoring a new one. The patterns repeat.

## Things to avoid

- **Don't replicate the parent skill's prompt.** If the agent's prompt is mostly the same as the spawning skill's, it shouldn't be a separate agent.
- **Don't grant write tools to review roles.** Read-only is what makes the review trustworthy.
- **Don't add agents for one-off work.** Use general-purpose dispatch with an inline prompt instead.
- **Don't omit calibration awareness if the agent's output gets validated.** Without it, the feedback loop is broken.
- **Don't bloat the description.** It's shown to the spawning agent on every consideration; keep it under ~250 words.
- **Don't pick the model by performance preference.** Pick by cognitive demand. An adversarial Critic on Haiku produces shallow reviews; a template-filler on Opus is wasteful.
- **Don't omit the changelog entry.** Per META-1, behavior-changing additions are tracked. New agents qualify.
