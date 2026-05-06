---
name: slice-candidates
description: Reads an annotated `diagnosis.html` (produced by `/diagnose` and round-tripped through the repo owner), parses the embedded JSON to extract findings + annotations, picks every finding the owner marked `Confirmed: yes`, and produces a pipeline-agnostic `backlog.md` of slice candidates ordered as a dependency DAG. Each candidate carries id, title, source finding(s), description, rationale, suggested approach, evidence, dependencies, estimated effort, and risk. Uses graphify blast-radius and shared-evidence checks to detect when two candidates touch overlapping code (so they're sequenced correctly). NEVER modifies source files or the diagnosis. Output is a plain markdown backlog any toolchain can consume — no SDLC-specific format. Use after `/diagnose` has been run, the HTML report has been sent to the repo owner, the owner has annotated and saved it, and the saved file is back in `diagnose-out/`. Trigger phrases — "/slice-candidates", "generate slice candidates", "build the backlog from diagnosis", "turn confirmed findings into slices", "what should we fix first".
argument-hint: [path-to-diagnose-out — omit to use ./diagnose-out]
---

# /slice-candidates — Build a slice backlog from an annotated diagnosis

You read an annotated `diagnosis.html` and produce **`backlog.md`** — a prioritized, DAG-ordered list of slice candidates derived from findings the owner confirmed.

This skill is decoupled from any specific SDLC. The output is a plain markdown backlog with no toolchain assumptions.

## Hard rules

1. **Never modify source files** in the analyzed repo.
2. **Never read source or documentation files in the analyzed repo.** All inputs come from `diagnose-out/` (`diagnosis.html`, `findings/*.yaml` as fallback, `graphify-out/graph.json`). The codebase itself is not opened by this skill — that's already been done by `/diagnose`. Graphify queries operate on the prebuilt graph, not on raw code.
3. **Never modify `diagnosis.html`** or the `findings/*.yaml` files. They're inputs only.
4. **Only consume `Confirmed: yes` rows.** `no` and `defer` are filtered out. Empty values are treated as not confirmed.
5. **Output is pipeline-agnostic.** No mention of any specific workflow's terminology, file conventions, or process.
6. **One confirmed finding → one slice candidate.** Do not auto-consolidate; the dependency DAG makes consolidation opportunities visible without forcing them.

## Step 1 — Locate inputs

If `$1` was passed, treat it as the path to a `diagnose-out/` directory.
Otherwise, look for `./diagnose-out` in the current working directory.

Verify:
- `diagnose-out/diagnosis.html` exists (this is the file the owner saved and sent back)
- The HTML contains an embedded `<script type="application/json" id="diagnose-data">` block with at least one annotation where `confirmed=yes`

If any check fails, report the specific reason and stop. Do not generate a partial backlog. If `diagnosis.html` exists but has no `Confirmed: yes` annotations, tell the user to confirm that the file received from the owner is the **saved-and-downloaded** version (not the original sent), since the owner must click "Save annotated HTML" to bake in their annotations.

## Step 2 — Run the backlog builder

```bash
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) PY="$HOME/.claude/.venv/Scripts/python.exe" ;;
  *)                    PY="$HOME/.claude/.venv/bin/python" ;;
esac
$PY "$HOME/.claude/skills/slice-candidates/build_backlog.py" --in "$DIAGNOSE_OUT"
```

`build_backlog.py`:
1. Reads `diagnosis.html` and parses the embedded JSON state from `<script type="application/json" id="diagnose-data">`. The state contains both findings and annotations.
2. Falls back to `findings/*.yaml` only if the embedded JSON has no findings list (older runs).
3. Filters to confirmed=yes.
4. Builds dependency edges between candidates using two signals:
   - **Shared evidence files** — if candidates A and B both reference the same file in `evidence`, they overlap.
   - **Graphify blast-radius** — for each candidate's primary evidence file, if it appears in another candidate's blast-radius, the candidates are coupled. Calls `graphify blast-radius --from=<file>` once per unique node and caches.
5. Topo-sorts candidates by the dependency DAG. Within each topological layer, sorts by priority = `severity_rank * blast_radius_rank / effort_rank` (descending).
6. Detects cycles → reports them as "must do together" candidate clusters.
7. Writes `$DIAGNOSE_OUT/backlog.md`.

If graphify is unavailable, the builder degrades to shared-evidence-only and notes the degradation in the backlog header.

## Step 3 — Report to user

After `build_backlog.py` succeeds, report:

- Path to `backlog.md`
- Number of candidates
- Number of dependency edges detected
- Whether any cycles were found
- One-line top recommendation (first candidate by recommended order)

## Output format — `backlog.md`

The Python helper produces this shape; it's documented here so callers know what to expect.

```markdown
# Slice candidates backlog

_Generated from diagnose-out/diagnosis.html on <ISO timestamp>._

**N** confirmed findings → **M** slice candidates.
**K** dependency edges. **C** cycles (clusters that should be done together).

## Recommended order

Topo-sorted by dependency, prioritized within each layer by severity × blast / effort:

1. SC-001 — <title>
2. SC-002 — <title>
...

## Dependency map

```
SC-001 → SC-003
SC-002 → SC-003
SC-003 → SC-004
```

## Candidates

### SC-001 — <title>

- **Source findings:** F-XXX-abc12345
- **Owner notes:** <if any>
- **Severity:** high  •  **Blast:** medium  •  **Reversibility:** cheap  •  **Effort:** small
- **Risk profile:** <one-line synthesis>
- **Dependencies:** none
- **Blocks:** SC-003
- **Description:** <from finding description>
- **Rationale:** <why this is worth a slice>
- **Suggested approach:** <from finding suggested_action, lightly framed for an implementer>
- **Evidence:**
  - `path/to/file.py:42-67` — <note>
  - ...

### SC-002 — ...
```

## Anti-patterns to avoid

- **Don't infer confirmation.** If the owner left `Confirmed` blank, the finding is not in the backlog. Period.
- **Don't fold multiple findings into one candidate.** Even if two findings clearly belong together, keep them as separate candidates with a dependency edge. The implementer chooses to bundle.
- **Don't add candidates not derived from confirmed findings.** No "while you're here" suggestions.
- **Don't over-promise sequencing precision.** The DAG is a hint based on file overlap + blast radius. The owner / implementer can override.
- **Don't require any specific downstream tool.** The backlog is a markdown deliverable. What anyone does with it is up to them.

## What the skill does NOT do

- Does not modify any source file.
- Does not modify `diagnosis.html` or `findings/*.yaml`.
- Does not implement fixes.
- Does not depend on, reference, or assume any particular development process or toolchain.
