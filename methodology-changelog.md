# AI SDLC Methodology Changelog

This file tracks behavior-changing rules in the AI SDLC pipeline. Each entry carries a **rule reference**, **defect class**, and **validation method**.

## Inclusion heuristic

> If a slice acceptable yesterday would be refused today (or vice versa), it's a changelog entry.

Typo and formatting edits don't qualify; behavior changes do. New skills, new gates, modified pre-finish checks, changed prompt structures for named subagents — these qualify. Doc clarifications that don't change behavior do not.

## How `/status` uses this file

This file is also installed at `~/.claude/methodology-changelog.md` so `/status` can surface the most recent dated entry as a Methodology section, regardless of which project the user is in.

When the file is missing (e.g., older install before this feature shipped), `/status` gracefully skips the Methodology section and optionally hints that re-running the install would surface methodology metadata.

## Format per entry

```markdown
## v<semver> — <YYYY-MM-DD>

<One-paragraph summary>

### Added | Changed | Retired

- **<RULE-ID> — <Rule name>**
  <Description of what this rule enforces and where>
  - **Rule reference**: <RULE-ID>
  - **Defect class**: <what bad behavior this prevents>
  - **Validation**: <how we verify the rule holds — pytest, structural grep, runtime gate, etc.>
```

Rules are identified by short IDs (e.g., `META-1`, `LINT-MOCK-1`, `WIRE-1`) for cross-reference from SKILL.md prose and from later changelog entries that supersede or refine.

---

## v0.4.0 — 2026-05-06

Adds cost-optimized model selection (COST-1). Three skills now explicitly dispatch their template-filling and rendering work to a Haiku subagent rather than running entirely on the main thread's model.

### Added

- **COST-1 — Cost-optimized model selection (Haiku-dispatched skills)**
  Adds explicit Haiku dispatch directives to `skills/commit-slice/SKILL.md` (Step 4 — commit message generation), `skills/status/SKILL.md` (Step 3 — summary rendering for default and brief modes), and `skills/archive/SKILL.md` (Step 3 — `slices/_index.md` regeneration; covers Step 4 archive catalog regeneration as well). The pattern: main thread gathers structured inputs (file reads + metric computation), then dispatches the formatting/rendering work to a `general-purpose` subagent with `model: haiku`. Quality is unchanged because the dispatched work is template-filling, not reasoning or synthesis — the cognitive demand is filling slots from a structured input dict, which Haiku does in a fraction of Opus's time and cost.
  - **Rule reference**: COST-1
  - **Defect class**: Skills running on the user's globally-set model (typically Opus) for work that has no reasoning component. `/commit-slice` fills a conventional-commit template from a structured dict — that's Haiku's shape, not Opus's. Running it on Opus burns ~5-10x cost for no quality difference. Same logic applies to `/status` (rendering metrics into a summary) and `/archive --index-only` (assembling tables from folder reads). Without explicit dispatch directives in each SKILL.md, the optimization sits unused — the executor doesn't know to delegate.
  - **Validation**: `tests/methodology/test_skill_model_dispatch.py` parametrizes over the three skills and verifies each SKILL.md contains (1) an explicit `model: haiku` directive, (2) a `subagent_type: "general-purpose"` reference, (3) a "Why Haiku" rationale section so future maintainers understand the cognitive-shape analysis, and (4) a `COST-1` rule reference for cross-link to the changelog. Skills missing any marker fail the test, which is the rot guard against future "to be safe, use Opus" reverts.

---

## v0.3.0 — 2026-05-06

Adds the named-subagent authoring guide and frontmatter conformance tests. New named subagents must conform to the documented frontmatter shape, tool-selection rules, and prompt structure conventions. Existing agents are pinned by static checks.

### Added

- **META-3 — Named-subagent authoring guide and frontmatter conformance**
  Adds `agents/AUTHORING.md` documenting when to use named subagents (vs forks vs general-purpose dispatch), the required frontmatter shape (`name`, `description`, `tools`, `model`), tool-selection rules (read-only roles MUST NOT have write tools), prompt structure conventions, calibration-awareness pattern, and self-test expectations. Adds `tests/methodology/test_agent_frontmatter.py` enforcing frontmatter conformance for every `agents/*.md` file (except `AUTHORING.md` itself), parametrized so new agents are checked automatically. Updates `README.md` to reference the new files.
  - **Rule reference**: META-3
  - **Defect class**: Future named subagents drift from established conventions (missing fields, mismatched name/filename, write tools granted to review roles, models picked by performance preference rather than cognitive demand) without an authoring guide. Drift compounds and erodes the load-bearing isolation property of named subagents — the Critic that becomes a rubber stamp because someone added `Write` to its tools and a "do helpful suggestions" instruction.
  - **Validation**: `tests/methodology/test_agent_frontmatter.py` runs as part of the methodology test suite. Tests verify (1) at-least-one named agent exists, (2) required-fields presence per agent, (3) name-matches-filename per agent, (4) model in allowed set per agent, (5) tools-non-empty per agent, (6) description substantive (>50 chars) per agent. Plus `test_authoring_guide_exists_and_pins_canonical_sections` pins canonical section headers in `AUTHORING.md` itself so the guide can't be paraphrased away.

---

## v0.2.0 — 2026-05-06

Adds the methodology self-test harness. From this version on, every behavior-changing rule introduced in a slice MUST have a corresponding pytest test that pins its prose, so silent paraphrase rot is prevented.

### Added

- **META-2 — Methodology self-test harness**
  Adds `tests/methodology/` directory with pytest harness and ~20 baseline tests covering load-bearing prose across `agents/critique.md`, `agents/critic-calibrate.md`, `agents/diagnose-narrator.md`, `agents/field-recon.md`, `skills/slice/SKILL.md`, `skills/build-slice/SKILL.md`, `skills/validate-slice/SKILL.md`, `skills/reflect/SKILL.md`, `skills/diagnose/SKILL.md`, plus self-tests for `methodology-changelog.md` (version sync, dated entries, rule-reference presence). Adds `pytest.ini` at repo root configuring `testpaths = tests`. Adds `tests/README.md` documenting setup, run, and how to add tests for new rules. CI hook documented (opt-in; no `.github/workflows/` shipped).
  - **Rule reference**: META-2
  - **Defect class**: Silent prose drift in load-bearing SKILL.md and agent files. A Critic prompt that reads "be thoughtful" produces different behavior than one that reads "assume the design is wrong until proven right" — and without enforcement, paraphrase rot is invisible until the Critic has degraded into a rubber stamp.
  - **Validation**: `pytest tests/methodology/ -v` runs cleanly and reports every test passing. `tests/methodology/test_methodology_changelog.py` validates VERSION ↔ changelog version sync and rule-reference presence per entry. Each subsequent slice that introduces a load-bearing rule MUST add a self-test for it; failure to do so is a violation of META-2 surfaced in `/critique`.

---

## v0.1.0 — 2026-05-06

Initial release of methodology versioning and changelog tracking.

### Added

- **META-1 — Methodology versioning + changelog**
  Adds `VERSION` file at the AI SDLC repo root tracking methodology semver. Adds `methodology-changelog.md` recording each behavior-changing rule with rule reference + defect class + validation method. `INSTALL.md` copies both to `~/.claude/` so they're discoverable from any project. `/status` reads `~/.claude/methodology-changelog.md` (if present) and surfaces the most recent dated entry as a Methodology section in default and full modes; the brief mode shows version on the header line.
  - **Rule reference**: META-1
  - **Defect class**: Methodology evolution had no audit trail. Users couldn't tell what changed between AI SDLC updates, why a new rule existed, or whether the methodology had drifted since they last looked. Without an audit trail, refinements get lost and speculative additions accumulate without scrutiny.
  - **Validation**: `VERSION` file exists at repo root with a semver string. `methodology-changelog.md` exists at repo root and has at least one dated entry. The most-recent entry's version matches `VERSION`. `INSTALL.md` Step 4 verifies both are copied to `~/.claude/`. `/status` reads the file gracefully (no error if missing) and surfaces version + most-recent rule.
