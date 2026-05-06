---
name: diagnose
description: Deep, owner-facing forensic analysis of a legacy or AI-assisted codebase. Reads code via graphify (entry points, reachability, communities, AST, semantic clusters) and produces a single self-contained interactive `diagnosis.html` covering inferred intent, current architecture with keep/modify/drop recommendations, code-level findings (dead code, duplicates, oversized functions, half-wired features, contradictory assumptions, layering violations, dead config, test gaps), and AI-bloat signatures specific to AI-assisted development (multiple impls of the same capability, modules added without integration, stale scaffolding, inconsistent patterns suggestive of session breaks). The HTML embeds findings as JSON and lets the repo owner fill `Confirmed` and `Notes` per finding in any browser; clicking "Save annotated HTML" downloads a copy with annotations baked in. The owner emails that file back; `/slice-candidates` extracts the embedded JSON to drive the backlog. NEVER modifies source files. Use when adopting / auditing / inheriting an existing repo and you want a comprehensive diagnostic deliverable for the repo owner. Trigger phrases — "/diagnose", "diagnose this codebase", "audit this repo", "deep analysis of legacy code", "forensic codebase review", "what's wrong with this codebase", "owner-facing audit".
argument-hint: [path-to-repo — omit to use current working directory]
---

# /diagnose — Deep Forensic Codebase Analysis

You produce **one self-contained interactive HTML diagnosis** of a target codebase, intended for the **repo owner** to read and annotate. The deliverable is `diagnosis.html` — a single file the owner opens in any browser, fills `Confirmed` + `Notes` per finding, then clicks "Save annotated HTML" to download a copy with annotations baked in. They email it back; `/slice-candidates` reads the embedded JSON.

This skill is a **diagnostic deliverable**, not a fix. It NEVER modifies source files in the target repo.

## Hard rules

1. **Never modify source files in the target repo.** All writes go to `diagnose-out/` only. Reading is fine; writing back is forbidden.
2. **No documentation reads from the target codebase.** Do not read any `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org`, or `docs/` directory in `TARGET`. Not READMEs, not CHANGELOGs, not design docs, not architecture notes the team has written. Everything must be derived from source code, config files (`.yaml`, `.toml`, `.json`, `.env`, `Dockerfile`, build manifests), schemas/migrations, and graphify queries. Inline docstrings and code comments may be read but never trusted as ground truth — they drift. This rule applies to every pass without exception.
3. **All output is pipeline-agnostic.** No references to any specific SDLC, slice loop, or downstream skill internals. The deliverable must be consumable by anyone with any toolchain.
4. **Stable content-derived finding IDs.** IDs are derived from content (category + evidence path + key signature), not generation order. A re-run produces the same ID for the same finding so owner annotations carry over.
5. **Never invent findings.** If a pass has no signal, it writes an empty findings file and a one-line summary. Do not pad with speculative issues.

## Step 1 — Determine target repo path

If `$1` was passed, use it. Otherwise use the current working directory.

Verify it's a non-empty directory with code in it. If empty, abort with a clear message.

```bash
TARGET="${1:-$PWD}"
OUT="$TARGET/diagnose-out"
```

## Step 2 — Set up output structure

```
$TARGET/diagnose-out/
  sections/         ← per-pass prose for the report (intermediate)
  findings/         ← per-pass structured findings (YAML, intermediate)
  summary/          ← per-pass one-paragraph self-summaries (intermediate)
  graphify-out/     ← code graph + GRAPH_REPORT
  diagnosis.html    ← final assembled deliverable (created by assemble.py)
  diagnosis.prev.html ← if a prior diagnosis.html existed (rotated by Step 8)
```

Create all subdirs. If `diagnose-out/diagnosis.html` already exists from a prior run, **do not delete it yet** — `assemble.py` reads its embedded JSON for state carryover (Confirmed/Notes annotations).

## Step 3 — Build the code graph

Always run graphify first. Every pass depends on it.

```bash
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) PY="$HOME/.claude/.venv/Scripts/python.exe" ;;
  *)                    PY="$HOME/.claude/.venv/bin/python" ;;
esac
$PY -m graphify code "$TARGET" --output "$OUT/graphify-out"
```

This writes `graphify-out/graph.json` and `graphify-out/CODE_REPORT.md`. The CODE_REPORT contains god nodes, communities, hotspots — useful seed for several passes.

**Fallback.** If graphify fails (unsupported language, broken AST), report the failure to the user and ask whether to proceed in **degraded mode** (passes that depend on graphify will produce reduced findings; clearly marked).

## Step 4 — Detect prior run state

Check for `$OUT/diagnosis.html` from a prior run.

If present, note it. `assemble.py` will:
- Parse its embedded JSON, carry forward `Confirmed` / `Notes` annotations on findings whose IDs match the new run.
- Mark previously-present findings that are now absent as `RESOLVED` in a separate section.
- Mark new findings as `NEW`.
- Mark recurring findings as `PERSISTING`.

You don't process this manually — `assemble.py` handles it. Just ensure prior `diagnosis.html` is left in place.

## Step 5 — Fan out the analysis passes (parallel)

Each pass is self-contained. Read its template from `~/.claude/skills/diagnose/passes/<name>.md` and pass it verbatim to a subagent.

**Parallel batch (run in a single message with multiple Agent tool calls).**

Per **COST-1.1** (`methodology-changelog.md` v0.5.0), each pass is dispatched on a model matched to its cognitive shape — Sonnet for extraction-shaped passes (reachability + grep + classification), Opus for reasoning-shaped passes (synthesis + judgment + cross-module analysis). HTML assembly remains pure Python (no model). Step 6.5 narrator stays Opus.

| Pass | Template file | Model | Rationale |
|------|---------------|-------|-----------|
| 01-intent | `passes/01-intent.md` | opus | Intent reconstruction = synthesis from entry points + handlers + models + integrations |
| 02-architecture | `passes/02-architecture.md` | opus | Architecture judgment = reasoning about fitness, layering, KEEP/MODIFY/DROP decisions |
| 03a-dead-code | `passes/03a-dead-code.md` | sonnet | Reachability analysis + verification (string grep, dynamic-import check) — extraction |
| 03b-duplicates | `passes/03b-duplicates.md` | opus | Semantic duplicate detection requires judging functional equivalence across modules |
| 03c-size-outliers | `passes/03c-size-outliers.md` | sonnet | Distribution computation + outlier flagging — extraction |
| 03d-half-wired | `passes/03d-half-wired.md` | opus | Half-wired feature detection requires reasoning about UI ↔ backend disconnects |
| 03e-contradictions | `passes/03e-contradictions.md` | opus | Cross-module assumption analysis = reasoning about how shared concepts diverge |
| 03f-layering | `passes/03f-layering.md` | sonnet | Dominant-pattern extraction + deviation flagging — classification |
| 03g-dead-config | `passes/03g-dead-config.md` | sonnet | Config registry vs consumer cross-reference — extraction |
| 03h-test-coverage | `passes/03h-test-coverage.md` | sonnet | Reachability + test-import cross-reference — extraction |

**Spawn each as `Agent` with `subagent_type: general-purpose`** AND the model from the table above (specified as `model: <opus|sonnet>` in the Agent invocation). **Do NOT use `Explore`** — Explore agents lack the `Write` tool and will silently fail to produce output files. Only `general-purpose` has the full tool set needed (Read, Grep, Glob, Bash, Write).

Each subagent receives the template content + `TARGET` and `OUT` paths. Each writes:

- `$OUT/sections/<pass-name>.md` — prose
- `$OUT/findings/<pass-name>.yaml` — structured findings (or empty list `[]`)
- `$OUT/summary/<pass-name>.md` — one paragraph self-summary

**Critical:** subagents must NOT read other passes' outputs and must NOT modify source files.

Wait for all 10 to finish before Step 6.

### Step 5.5 — Verify all expected output files exist

After the parallel batch completes, check that every pass produced its three files. Use Glob:

```bash
ls "$OUT/sections" "$OUT/findings" "$OUT/summary"
```

Expected: 10 entries in each (pass 04 will add an 11th in Step 6). For any missing file, report which pass(es) failed to write and re-spawn just those passes (still as `general-purpose`). Do not proceed to Step 6 with gaps — silent gaps become silent omissions in the final report.

## Step 6 — Cross-reference pass: 04-ai-bloat

This pass depends on `findings/03b-duplicates.yaml` and `findings/03d-half-wired.yaml`. Run it after Step 5.5 confirms those files exist.

Spawn one Agent with `subagent_type: general-purpose` (NOT `Explore`) and the template `passes/04-ai-bloat.md`. It reads only the structured YAMLs from prior passes (never their prose), composes AI-bloat signatures, writes its three files like the others.

After it returns, verify `$OUT/sections/04-ai-bloat.md`, `$OUT/findings/04-ai-bloat.yaml`, and `$OUT/summary/04-ai-bloat.md` all exist. Re-spawn if any are missing.

## Step 6.5 — Narrative synthesis pass: diagnose-narrator

After all 11 forensic passes have written their YAMLs + summaries, spawn the **named narrator subagent** to write the engaging executive summary.

```
Agent tool, subagent_type: "diagnose-narrator"
```

The narrator agent at `~/.claude/agents/diagnose-narrator.md` carries the full prompt — tone, structure, length discipline, what to do, what NOT to do. You don't repeat that here. Your prompt body just hands it the path:

```
The /diagnose run for this codebase has completed all 11 analysis passes.
Output directory: $OUT

Read findings/*.yaml and summary/*.md from there. Synthesize a narrative
executive summary as described in your system prompt. Write it to
sections/00-overview.md.
```

Why a separate named subagent rather than a general-purpose pass:
- **Fresh context** — the narrator doesn't see the main /diagnose conversation, doesn't get polluted by prior pass details, focuses purely on synthesis.
- **Stable role** — its tone + structure rules live in the agent file, not inlined in this skill, so they can be tuned without touching the skill.
- **Read-only** — narrator has Read/Glob/Grep/Write only. No source modifications, no risk to the analyzed repo.

After it returns, verify `$OUT/sections/00-overview.md` exists. If absent, log the failure but continue to Step 7 — `assemble.py` falls back to per-pass summary stitching when the overview is missing (the report is degraded, not broken).

## Step 7 — Assemble

```bash
$PY "$HOME/.claude/skills/diagnose/assemble.py" --out "$OUT"
```

`assemble.py`:
1. Reads section/finding/summary files in manifest order.
2. Reads prior `diagnosis.html` (if exists) and extracts Confirmed/Notes from its embedded `<script type="application/json" id="diagnose-data">` block.
3. Applies carryover, marks NEW/PERSISTING/RESOLVED.
4. Renders one new self-contained `diagnosis.html` with: inline CSS+JS, executive summary, ordered prose sections (markdown converted to HTML), per-finding detail blocks, an interactive findings index table (each row has Confirmed dropdown + Notes textarea), a resolved-since-last-run table, and an embedded JSON state block carrying findings + annotations.
5. Rotates prior to `diagnosis.prev.html`.

If `assemble.py` fails, report the failure with the full error and stop. Do not partial-assemble manually.

## Step 8 — Report to user

Tell the user:

- Path to `diagnosis.html`
- Counts: total findings, by severity, NEW vs PERSISTING vs RESOLVED
- One sentence on the overall verdict (from executive summary)
- The intended workflow:
  1. Send `diagnosis.html` to the repo owner.
  2. Owner opens it in any browser. The findings table at the bottom has `Confirmed` (yes/no/defer) and `Notes` controls per finding.
  3. Owner clicks "Save annotated HTML" — JS regenerates the document with their annotations baked into the embedded JSON, and downloads a copy.
  4. Owner emails / sends the downloaded file back.
  5. Place that file at `$OUT/diagnosis.html` (replacing the original) and run `/slice-candidates` if you want to proceed to a slice backlog.
- Mention `/slice-candidates` only if the user asks "what now?" — do not push it. This skill is a deliverable, not a workflow step.

## Anti-patterns to avoid

- **Reading the master `diagnosis.html` mid-process.** Never. Each pass writes new files; assemble composes. The master is read only by `assemble.py`, only for prior-state extraction.
- **Cross-pass prose dependencies.** Pass N must never need to read pass M's `sections/*.md`. Use `findings/*.yaml` for cross-reads (only pass 04 does this).
- **Inventing findings to fill quota.** Each pass legitimately may produce zero findings. Accept that.
- **Over-summarizing.** "There are issues in the codebase" is not a finding. Every finding has a specific evidence (file:line) and concrete suggested action.
- **Touching the analyzed repo.** Even creating a `.gitignore` entry or a config file in the target repo is forbidden. All artifacts in `diagnose-out/` only.
- **Exposing internal pass mechanics in the report.** The owner sees one cohesive `diagnosis.html`, not 11 stitched fragments. The assembler glues invisibly.

## What the skill does NOT do

- Does not fix anything.
- Does not generate slice candidates (that's `/slice-candidates`).
- Does not enforce any project's process.
- Does not report progress over time as a dashboard — each run produces one snapshot with carryover from the previous.

## Output schema reference

Findings YAML schema is in `~/.claude/skills/diagnose/schema/finding.yaml`. All passes produce findings matching that schema. `assemble.py` validates.
