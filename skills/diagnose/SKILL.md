---
name: diagnose
description: Deep, owner-facing forensic analysis of a legacy or AI-assisted codebase. Reads code via graphify (entry points, reachability, communities, AST, semantic clusters) and produces a single self-contained interactive `diagnosis.html` covering inferred intent, current architecture with keep/modify/drop recommendations, code-level findings (dead code, duplicates, oversized functions, half-wired features, contradictory assumptions, layering violations, dead config, test gaps), and AI-bloat signatures specific to AI-assisted development (multiple impls of the same capability, modules added without integration, stale scaffolding, inconsistent patterns suggestive of session breaks). The HTML embeds findings as JSON and lets the repo owner fill `Confirmed` and `Notes` per finding in any browser; clicking "Save annotated HTML" downloads a copy with annotations baked in. The owner emails that file back; `/slice-candidates` extracts the embedded JSON to drive the backlog. NEVER modifies source files. Use when adopting / auditing / inheriting an existing repo and you want a comprehensive diagnostic deliverable for the repo owner. Trigger phrases — "/diagnose", "diagnose this codebase", "audit this repo", "deep analysis of legacy code", "forensic codebase review", "what's wrong with this codebase", "owner-facing audit".
argument-hint: [path-to-repo — omit to use current working directory] [--parallel — opt into the legacy single-message parallel batch dispatch (default is sequential; see Step 5)]
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

`/diagnose` accepts an optional `--parallel` flag (position-independent) in addition to the optional repo path. Parse args **flag-strip-before-TARGET** so a flag-shaped token never becomes the path:

```bash
PARALLEL=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --parallel)  PARALLEL=1 ;;
    --*)         echo "WARNING: unknown flag '$a' ignored (running sequential default)" >&2 ;;
    *)           ARGS+=("$a") ;;
  esac
done
TARGET="${ARGS[0]:-$PWD}"
OUT="$TARGET/diagnose-out"
```

`$PARALLEL` (0 = sequential default, 1 = `--parallel` opt-in) is read at Step 5. Fail-safe semantics: `--parallel` sets the flag and is consumed; any **other** `--`-prefixed token is an unknown flag → a one-line warning is emitted and the token is **ignored, never treated as the path** (so a flag typo like `--paralll` never becomes `TARGET` and never aborts — `TARGET` falls back to `$PWD`, sequential). Only a *non-flag-shaped* token is taken as the repo path; if that path doesn't exist the pre-existing `cd "$TARGET"`-fails abort (a few lines below) fires exactly as it does today for any bad path — that is unchanged path-validation behavior, **not** a flag-induced abort. This shell runs under Git-Bash/MINGW on Windows (see the `case "$(uname -s)"` block in Step 3); Git-Bash ships bash ≥4.x so the `ARGS=()` array + `"$@"` iteration are portable.

### If you're invoking with an explicit path, cd to it first

The cwd-must-match-TARGET pattern: `/diagnose` works most reliably when invoked from inside the target's directory (i.e., when `$TARGET` resolves to the same path as `$PWD`). Subagents *may* lose tool access otherwise — slice-001 surfaced this on 2026-05-09 when TARGET was outside `$PWD`; spawned `general-purpose` subagents lost Read / Grep / Bash / PowerShell access (only Glob remained), producing degraded analyses with mostly-empty findings.

Upstream root cause is uncertain: it may be **cwd-mismatch** specifically, or a **known parallel-spawn permission cascade-failure** ([claude-code #57037](https://github.com/anthropics/claude-code/issues/57037)) which fires when multiple `Agent` tool calls dispatch in one message — exactly what Step 5 does. So `cd $TARGET` is the cheapest mitigation but not guaranteed to fix every instance. (Tracked in this project's `architecture/risk-register.md` as **R-1**.)

Run a cwd-mismatch check before fanning out subagents:

```bash
TARGET_REAL=$(cd "$TARGET" 2>/dev/null && pwd) || { echo "TARGET does not exist: $TARGET"; exit 1; }
PWD_REAL=$(pwd)
if [ "$TARGET_REAL" != "$PWD_REAL" ]; then
  cat <<EOF
WARNING: TARGET resolves to a path outside the current directory.

  TARGET: $TARGET_REAL
  PWD:    $PWD_REAL

  Slice-001 surfaced this scenario at validation: spawned subagents may
  lose Read/Grep/Bash access in this configuration, producing a degraded
  diagnosis with mostly empty findings. Upstream root cause may be
  cwd-mismatch and/or claude-code #57037 (parallel-spawn cascade).

  Recommendation: cd to TARGET first, then re-invoke /diagnose:
      cd "$TARGET"
      # (re-invoke /diagnose from your client)

  You may proceed anyway — the run will not fail outright, but findings
  quality will be lower than ideal.
EOF
fi
```

If the warning fires: surface it to the user verbatim and proceed (do not abort). The user can choose to interrupt and re-invoke after `cd`'ing.

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

## Step 3 — Build the code graph + load pass templates into memory

Always run graphify first. Every pass depends on it.

```bash
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) PY="$HOME/.claude/.venv/Scripts/python.exe" ;;
  *)                    PY="$HOME/.claude/.venv/bin/python" ;;
esac
$PY -m graphify code "$TARGET" --out "$OUT/graphify-out"
```

This writes `graphify-out/graph.json` and `graphify-out/CODE_REPORT.md`. The CODE_REPORT contains god nodes, communities, hotspots — useful seed for several passes.

**Fallback.** If graphify fails (unsupported language, broken AST), report the failure to the user and ask whether to proceed in **degraded mode** (passes that depend on graphify will produce reduced findings; clearly marked).

**Read pass templates and the finding-schema crib sheet into memory now.** They will be embedded into subagent prompts in Step 5 — analysis subagents do NOT read out-of-cwd files themselves (per ADR-001 / slice-001-diagnose-orchestration-fix). Use the Read tool on:

- `~/.claude/skills/diagnose/passes/*.md` — 11 pass templates (one per pass listed in Step 5's table)
- `~/.claude/skills/diagnose/schema/finding.yaml` — read the file but for subagent prompts, use only the 5-line crib sheet that already lives in each pass template (avoids ~30KB redundant embedding per /diagnose run, per slice-001 critique m2)

## Step 4 — Detect prior run state

Check for `$OUT/diagnosis.html` from a prior run.

If present, note it. `assemble.py` will:
- Parse its embedded JSON, carry forward `Confirmed` / `Notes` annotations on findings whose IDs match the new run.
- Mark previously-present findings that are now absent as `RESOLVED` in a separate section.
- Mark new findings as `NEW`.
- Mark recurring findings as `PERSISTING`.

You don't process this manually — `assemble.py` handles it. Just ensure prior `diagnosis.html` is left in place.

## Step 5 — Dispatch the analysis passes (sequential by default; --parallel opt-in)

Per ADR-001 (slice-001-diagnose-orchestration-fix), each analysis subagent **does analysis only** — it returns three 4-backtick fenced blocks (`section`, `findings`, `summary`) in its result message. The subagent does NOT call Write, Bash, or python; it does NOT read out-of-cwd files. The main thread does all I/O via the `write_pass.py` helper after each subagent returns.

This pattern is robust to subagent permission configurations (`general-purpose` subagents may have narrower allowlists than the parent thread) and eliminates the schema-mismatch + YAML-quoting failure modes that arose under the prior "subagent writes its own files" contract.

**Dispatch mode is controlled by `$PARALLEL` (set in Step 1).**

- **Default — sequential (`$PARALLEL` = 0).** Dispatch the 10 analysis passes **one `Agent` call per message, one at a time**: spawn pass N's Agent, wait for its result, run the "After each subagent returns" `write_pass.py` flow + 3-attempt cap for pass N, **then** spawn pass N+1. This is the default because dispatching multiple `Agent` tool calls in a single message triggers the parallel-spawn permission cascade-failure ([claude-code #57037](https://github.com/anthropics/claude-code/issues/57037)) tracked as `architecture/risk-register.md` R-1 — spawned subagents lose Read/Grep/Bash access and produce a degraded `diagnosis.html`. Sequential dispatch (one Agent call per message) defeats that cascade mode. Per ADR-027 (slice-029).
- **Opt-in — parallel batch (`$PARALLEL` = 1, via `/diagnose --parallel`).** Run the 10 passes as a **single message with multiple `Agent` tool calls** (the legacy fan-out). Faster wall-clock, but re-exposes R-1 — the caller has chosen this explicitly. The per-pass contract, model routing, and the entire "After each subagent returns" writer flow are **identical** to the sequential default; only the dispatch shape (one message, N Agent calls) differs.

Both modes use the same model-routing table, the same single subagent-contract subsection, and the same per-pass writer flow below — only *when* each `Agent` is spawned changes.

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

**Spawn each as `Agent` with `subagent_type: general-purpose`** AND the model from the table above (specified as `model: <opus|sonnet>` in the Agent invocation).

### What goes into each subagent's prompt

Embed (in the prompt body):

1. The pass template content (loaded in Step 3)
2. `TARGET` and `OUT` paths
3. The explicit subagent contract — see canonical contract below.

The pass templates already include a 5-line schema crib sheet describing required-field shape. No need to embed the full `schema/finding.yaml`.

### Subagent contract (preamble — human-readable breakdown)

The subagent's tool envelope is a four-line permission breakdown:

1. **Write**: forbidden — the orchestrator writes the three pass output files via `write_pass.py`.
2. **Read / Grep / Glob**: allowed within `$TARGET` (including `$TARGET/diagnose-out/graphify-out/`); allowed for files in the subagent's cwd; not needed (and may not work) for paths outside cwd, hence templates + schema are embedded in the prompt.
3. **Bash / python**: allowed for graphify queries against `$OUT/graphify-out/graph.json` (per each pass template's Method section).
4. **Output**: return three 4-backtick fenced blocks (`section`, `findings`, `summary`) in your final message; the orchestrator parses + writes.

### Subagent contract (canonical line — embed verbatim in subagent prompts)

The line below is the **single canonical contract string** locked across SKILL.md Step 5 + 11 pass templates' Output format sections (slice-002 / triage M2). Edit it here and the byte-equality test forces consistent edits across all 12 sites:

> **Do NOT call Write to produce output files (the orchestrator handles that). You MAY use Bash/python for graphify queries within $OUT/graphify-out/, and Read/Grep/Glob for source files within $TARGET.**

### Pass-specific evidence requirement (LAYER-EVID-1)

Per `methodology-changelog.md` v0.33.0 (slice-019), the `03f-layering` pass subagent MUST apply the **textual import-evidence requirement** before emitting any HIGH-severity layering-violation finding. The rule body lives in `passes/03f-layering.md` Method step 4 + Severity rubric downgrade rule + Anti-patterns negative-pin (the regex variants for TypeScript/JavaScript, Python, Rust, Go, Java + the alias-aware grep semantics for tsconfig.json `paths`/`baseUrl`). The subagent's Grep/Read/Glob tool envelope (per the canonical contract above) is sufficient — no new tools required. Witnessed failure mode: F-LAYER-bca9c001 false-positive (parallel type files defining identically-named enums; graphify symbol-resolution synthesized a phantom edge where zero textual imports existed).

### After each subagent returns

For each completed subagent (in the sequential default, this runs immediately after that one pass's Agent returns and **before** the next pass is spawned; in `--parallel` mode, process them as they finish — order doesn't matter):

1. Save the subagent's raw response text to `$OUT/.tmp/<pass-name>.raw` (create `.tmp/` if missing)
2. Invoke the writer helper:

   ```bash
   $PY $HOME/.claude/skills/diagnose/write_pass.py \
       --pass <pass-name> \
       --out $OUT \
       --raw-file $OUT/.tmp/<pass-name>.raw
   ```

3. The helper extracts the three fenced blocks, normalizes the findings (per-pass signature extractor recomputes malformed IDs deterministically), validates against `REQUIRED_FIELDS` from `assemble.py`, and writes the three pass files via `yaml.safe_dump`. Exit codes: 0 clean / 1 validation failure / 2 parse failure.
4. **Re-spawn cap (per slice-001 critique M3): at most 3 total attempts per pass.** If `write_pass.py` exits non-zero on the third attempt, save the raw response to `$OUT/.tmp/<pass-name>.failed.raw` and proceed with the pass marked degraded (`assemble.py` will surface this in the final report). Do not loop forever.

**Critical:** subagents must NOT read other passes' outputs and must NOT modify source files. The "do not call Write" rule is enforced by the contract above; the prose-pin tests (`tests/skills/diagnose/test_skill_md_pins.py`) protect against regression.

Whether dispatched sequentially (default — each pass awaited and written before the next is spawned) or as a `--parallel` batch, all 10 passes MUST have returned AND had `write_pass.py` run on each before Step 6.

### Step 5.5 — Verify all expected output files exist

After all 10 passes have been dispatched and written (sequentially by default — each awaited+written before the next; or after the `--parallel` batch completes), check that every pass produced its three files. Use Glob:

```bash
ls "$OUT/sections" "$OUT/findings" "$OUT/summary"
```

Expected: 10 entries in each (pass 04 will add an 11th in Step 6). Also check `$OUT/.tmp/` for any `*.failed.raw` files — those are passes that exhausted the 3-attempt cap (Step 5) and shipped degraded. Note them for the user. For any missing file (i.e., the helper never wrote it because the cap wasn't reached but a prior validation/parse failure went unnoticed), report which pass(es) and re-spawn the affected pass once before proceeding. Do not proceed to Step 6 with gaps — silent gaps become silent omissions in the final report.

**Sequential early-exit (default-mode silent-gap guard).** In the sequential default a pass is only spawned after the previous one was written, so if the dispatch loop did **not** reach all 10 (orchestrator interrupted, session death, manual stop), the un-reached passes are *missing* (never spawned) — distinct from *failed* (spawned, exhausted the 3-attempt cap, has a `.failed.raw`). The gap check above applies identically to both: any pass with no `sections/findings/summary` triple AND no `.failed.raw` is an un-spawned pass — re-spawn it (sequentially) before Step 6. **Never treat an interrupted-loop gap as "degraded and acceptable"; never silently skip to Step 6 with fewer than 10 passes attempted.**

## Step 6 — Cross-reference pass: 04-ai-bloat

This pass depends on `findings/03b-duplicates.yaml` and `findings/03d-half-wired.yaml`. Run it after Step 5.5 confirms those files exist.

Spawn one Agent with `subagent_type: general-purpose` and `model: opus`. The 04-ai-bloat subagent IS allowed to read the two prior YAML files from `$OUT/findings/` (those live inside the target's `diagnose-out/`, which the parent's working directory typically grants). Embed `passes/04-ai-bloat.md` content + paths + the same "do NOT call Write / return three 4-backtick fenced blocks" contract from Step 5 in the subagent's prompt.

After it returns, run the same writer-helper flow as Step 5 (save raw text → invoke `write_pass.py --pass 04-ai-bloat --raw-file $OUT/.tmp/04-ai-bloat.raw`). Apply the same 3-attempt cap. Verify `$OUT/sections/04-ai-bloat.md`, `$OUT/findings/04-ai-bloat.yaml`, and `$OUT/summary/04-ai-bloat.md` all exist before continuing.

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

Per slice-001 / ADR-001: the narrator agent's pattern is **deliberately preserved**. It's a named subagent with an explicit Write tool grant, writes only `sections/00-overview.md`, and worked correctly under the same machine configuration that exposed the analysis-subagent failure mode. The fenced-block + write_pass.py pattern in Steps 5/6 is for **anonymous `general-purpose` subagents** whose tool allowlist may be narrower than the parent's; named subagents with explicit tool declarations operate normally.

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
