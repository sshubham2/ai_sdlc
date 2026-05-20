---
name: slice-candidates
description: Reads an annotated `diagnosis.html` (produced by `/diagnose` and round-tripped through the repo owner), parses the embedded JSON to extract findings + annotations, picks every finding the owner marked `Confirmed: yes`, and produces a pipeline-agnostic `backlog.md` of slice candidates ordered as a dependency DAG. Each candidate carries id, title, source finding(s), description, rationale, suggested approach, evidence, dependencies, estimated effort, and risk. Uses graphify blast-radius and shared-evidence checks to detect when two candidates touch overlapping code (so they're sequenced correctly). NEVER modifies source files or the diagnosis. Output is a plain markdown backlog any toolchain can consume — no SDLC-specific format. Use after `/diagnose` has been run, the HTML report has been sent to the repo owner, the owner has annotated and saved it, and the saved file is back in `diagnose-out/`. Trigger phrases — "/slice-candidates", "generate slice candidates", "build the backlog from diagnosis", "turn confirmed findings into slices", "what should we fix first".
argument-hint: [path-to-diagnose-out — omit to use ./diagnose-out] [--obo for guided one-finding-at-a-time review]
---

# /slice-candidates — Build a slice backlog from an annotated diagnosis

You read an annotated `diagnosis.html` and produce **`backlog.md`** — a prioritized, DAG-ordered list of slice candidates derived from findings the owner confirmed.

This skill is decoupled from any specific SDLC. The output is a plain markdown backlog with no toolchain assumptions.

## Hard rules

1. **Never modify source files** in the analyzed repo.
2. **Never read source or documentation files in the analyzed repo.** All inputs come from `diagnose-out/` (`diagnosis.html`, `findings/*.yaml` as fallback, `graphify-out/graph.json`). The codebase itself is not opened by this skill — that's already been done by `/diagnose`. Graphify queries operate on the prebuilt graph, not on raw code. **Bounded carve-out (ADR-054):** the `--obo` "Validate then approve" branch may read a finding's cited evidence files — and ONLY those — exclusively through `build_backlog.py --obo-peek` (mechanically allow-set-gated). This is the sole exception; it does not widen for the default path, other findings, or direct reads. See "`--obo` interactive review mode" below.
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

## `--obo` interactive review mode (ADR-054)

When invoked as `/slice-candidates --obo [path]` (the `--obo` token anywhere in the invocation), DO NOT run Step 2 first. The owner often cannot face reading the whole `diagnosis.html` and hand-annotating every finding; `--obo` ("on behalf of") walks findings one at a time, severity-ordered, and bakes the owner's per-finding decisions into a faithful `diagnosis.annotated.html` copy that Step 2 then consumes unchanged.

The conversational loop is Claude-driven; the deterministic halves are `build_backlog.py` subcommands. **Under `--obo`, you MUST NOT `Read` any analyzed-repo source file directly — `--obo-peek` is the only permitted source-read channel** (ADR-054 / Hard rule #2 carve-out is mechanically bounded, not honour-system).

1. **Extract.** Run:
   ```bash
   $PY "$HOME/.claude/skills/slice-candidates/build_backlog.py" --in "$DIAGNOSE_OUT" --obo-extract
   ```
   This emits JSON `{total, reviewed, findings:[…]}` already severity-sorted (critical → high → medium → low, stable within band). Each finding carries `reviewed` (true iff its id is already in `annotations`), `current` (existing `{confirmed,notes}`), and `evidence_paths` (the `--obo-peek` allow-set). On resume, skip every finding whose `reviewed` is true (resume = first finding with `reviewed:false`).

2. **Per-finding prompt.** For each unreviewed finding in order, present it (title, severity, description, suggested action, evidence) and ask via the **`AskUserQuestion` tool** (structured options — never a bare free-text prompt; per SOAD-1) with a header showing live progress: `Finding k of N · A approved · D deferred · R rejected`. Options:
   - **Approve** → record `{confirmed:"yes", notes:""}` (or the owner's note).
   - **Validate then approve** → run `build_backlog.py --in "$DIAGNOSE_OUT" --obo-peek --finding <id> --file <path>` for the finding's cited evidence path(s) ONLY (it refuses out-of-set paths with a non-zero exit + logged refusal). Read the returned content, give a real / likely-real / not-real verdict with reasoning, then re-offer Approve / Defer / Reject for this finding.
   - **Defer** → record `{confirmed:"defer", notes:""}`.
   - **Reject** → capture a free-text "why" and record `{confirmed:"no", notes:"<why>"}`.
   - **Exit** → stop the loop now; proceed to step 3 with decisions gathered so far.

3. **Write the annotated copy.** Collect decisions into a JSON map `{finding_id: {confirmed, notes}}` (omit findings the owner never reached — do NOT write empty entries), write it to a temp file, and run:
   ```bash
   $PY "$HOME/.claude/skills/slice-candidates/build_backlog.py" --in "$DIAGNOSE_OUT" --obo-write --decisions <tmp>
   ```
   This bakes the decisions into `diagnose-out/diagnosis.annotated.html`, asserts the original `diagnosis.html` is byte-unchanged, and fails closed on any malformed input. Report the remaining-unreviewed count, distinguishing **never-reached** from **Deferred**.

4. **Continue (optional).** If at least one finding was Approved, you MAY run Step 2 on the annotated copy (`build_backlog.py --in <dir>` after copying `diagnosis.annotated.html` over a working `diagnosis.html`, or point the owner at it) to produce `backlog.md` immediately. Otherwise stop and tell the owner where the annotated copy is.

**Operator guidance — Defer is terminal for `--obo` resume.** A Deferred finding is written to the annotated copy as `confirmed:"defer"` and is therefore present in `annotations`; on any later `--obo` run against that annotated copy it is treated as reviewed and is NOT re-offered. To revisit a Deferred finding the owner re-runs `--obo` against the **original** `diagnosis.html` (not the annotated copy), or hand-edits the JSON. State this to the owner when they choose Defer so it is not a silent one-way trap.

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

- Does not modify any source file. (`--obo` "Validate then approve" *reads* a finding's cited evidence via the allow-set-gated `--obo-peek` only — never writes source.)
- Does not modify `diagnosis.html` or `findings/*.yaml`. (`--obo` writes a *new* `diagnosis.annotated.html`; the original `diagnosis.html` is asserted byte-unchanged.)
- Does not implement fixes.
- Does not depend on, reference, or assume any particular development process or toolchain.
