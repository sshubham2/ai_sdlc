---
name: reflect
description: "AI SDLC pipeline. Capture what this slice taught you and update the vault with reality. Categories: validated / corrected / discovered / deferred. Tracks Critic accuracy. Use after /validate-slice, before next /slice. Trigger phrases: '/reflect', 'reflect on slice', 'capture learnings', 'update vault with reality', 'slice retrospective'. The cure for spec rot — automatic vault updates at slice boundaries."
user_invokable: true
---

# /reflect — Capture Reality, Update Vault

You are reflecting on the just-completed slice and updating the vault with what reality taught you. This is THE step that prevents spec rot.

## Where this fits

Runs after `/validate-slice`. Output feeds the next `/slice` (the discoveries and deferrals inform what to build next).

## Why this matters

Spec rot is the biggest failure mode of spec-driven SDLC: spec written, code evolves, spec goes stale, discipline collapses. The cure: make vault updates automatic at slice boundaries, not optional at project end. Every slice produces deltas to the vault — `/reflect` is where they land.

## Prerequisite check

- Find active slice folder
- Read all of: `mission-brief.md`, `design.md`, `critique.md`, `build-log.md`, `validation.md`
- If `validation.md` is missing: stop, run `/validate-slice` first

## Your task

### Step 1: Synthesize learnings into four categories

Read all slice files. Categorize observations:

#### Validated
Design claims that reality confirmed. Examples:
- "Endpoint accepts JPEG/PNG/HEIC up to 10MB — validated by curl tests on each format"
- "Authorization rejects non-owners — manual check with second account"

#### Corrected
Design claims that reality refuted. Vault must be updated.
- "Design said thumbnails generate async; reality is sync (async queue is a separate slice)"
- "ADR-008 chose sendgrid; reality is we used resend"

#### Discovered
Things you didn't know to spec. New risks, edge cases, constraints.
- "iPhone HEIC files have EXIF orientation; thumbnails appeared sideways without handling"
- "S3 PUT timeout default (30s) is too aggressive for >5MB files"

#### Deferred
Things not done this slice. Will be addressed in next slice or backlog.
- "Multiple receipts per transaction — out of scope per mission brief"
- "Receipt deletion — separate slice"

### Step 2: Update affected vault files (thin vault)

The thin vault has fewer files to update. For each Corrected item, update the relevant file:

- Decision wrong → supersede the ADR (procedure below)
- Risk claim wrong → **Rewrite** `<vault>/risk-register.md` in place (a `**Status**:` flip is a whole-file read-modify-write) via `vault_edit rewrite` (R-32 CAS — [[ADR-088]]): capture the byte-exact base with `$PY -m tools.vault_edit read --file risk-register.md --out-file base.bin` (use `--out-file`, NOT shell `>` — PowerShell's `>` re-encodes stdout to UTF-16LE+BOM and corrupts the base → guaranteed CAS livelock), edit a copy, then `$PY -m tools.vault_edit rewrite --file risk-register.md --base-file base.bin --content-file <edited>`; on exit 3 (a parallel slice wrote it first) re-read + re-apply + retry (bounded ~5, then STOP loudly). A NEW risk *entry* is an append → `vault_edit append` (unchanged).
- Concept assumption wrong → update `<vault>/concept.md` (the relevant section)
- Slice's own design wrong → update the slice's `design.md` (note the change in build-log too)
- `diagnose-out/backlog.md` round-trip — **RETIRED at slice-105 / [[ADR-095]]** (BCR-1 is now *consume-only*): `/reflect` no longer writes an `**Addressed:** slice-NNN` line back into `diagnose-out/backlog.md`. Under BRANCH-3 `/reflect` runs in the worktree, where `diagnose-out/` is gitignored, so that write landed in a copy discarded at merge — a dead write. `/slice` still *consults* `backlog.md` as a candidate source when present (the consume side is unchanged); the `**Closes:** SC-NNN` sentinel is now inert documentation, not a round-trip trigger.

For each Discovered item:
- Add to `<vault>/risk-register.md` with reversibility tag <!-- route: tools.vault_edit append -->
- If it affects current slice scope: note in this slice's `reflection.md`
- If it spawns a future slice: leave a candidate note for next `/slice`

For superseded decisions:
- Mark original ADR `status: superseded`
- Add `superseded-by: ADR-NNN` field to the original
- Create new ADR with updated decision + `supersedes: ADR-NNN` field
- DO NOT edit the original ADR's content. Decisions are append-only history.

**What you do NOT update** (because they don't exist in thin vault, Standard / Minimal mode):
- `components/<name>.md` — read the code instead
- `contracts/<name>.md` — code IS the contract (FastAPI / OpenAPI / Pydantic)
- `schemas/<name>.md` — data models are in code
- `test-plan/` — tests are the plan

If you find yourself wanting to update one of these: either you're in Heavy mode (where they exist) or you're trying to document what code already shows (don't).

### Step 3: Critic calibration

Per **TRI-1** (`methodology-changelog.md` v0.11.0), the calibration vocabulary now distinguishes between Critic accuracy AND user-override accuracy. For each Critic finding in this slice's `critique.md`, score:

- **VALIDATED**: reality confirmed the Critic's concern (Critic was right; disposition was ACCEPTED-FIXED or ACCEPTED-PENDING and the underlying problem materialized)
- **FALSE-ALARM**: user OVERRODE the Critic and reality confirmed the user — the Critic over-reached on this finding
- **OVERRIDE-MISJUDGED**: user OVERRODE the Critic but reality showed the Critic was right after all. This is calibration learning for **both** the Critic AND the user — track recurrent patterns; if a user override pattern is consistently wrong, the user's mental model needs adjustment as much as the Critic's prompt does
- **NOT-YET**: DEFERRED or ESCALATED; can't score yet — re-score in the future slice that addresses it
- **MISSED by Critic**: surfaced during build/validate, was NOT in the Critic's findings at all. The Critic's prompt may need a new dimension or sharpened heuristic

**Why this matters**: every 10-20 slices, `/critic-calibrate` reads these calibration entries across recent reflections. Patterns of MISSED feed Critic prompt updates. Patterns of OVERRIDE-MISJUDGED feed both Critic prompt updates AND a user-side awareness signal — the same person who was wrong twice on a similar override should see the pattern surface in `/pulse` or `/critic-calibrate` output. Specific entries produce specific improvements: "Critic didn't flag EXIF orientation on iPhone HEIC uploads" beats "Critic missed something."

This data accumulates over time and informs Critic prompt tuning + user-judgement awareness across projects.

### Step 4: Write `architecture/slices/slice-NNN-<name>/reflection.md`

```markdown
# Reflection: Slice NNN <name>

**Date**: <YYYY-MM-DD>
**Shipped**: YES | YES-WITH-DEFERRALS | NO

## Validated
- <design claim> — validated by <test/observation>
- <design claim> — validated by <test/observation>

## Corrected
- <design claim> → reality is <actual> — updated in [[file]]
- <decision> → superseded by [[ADR-NNN]]

## Discovered
- <discovery> — impact: <what changes for next slices>
- <discovery> — added to risk register as [[R-NN]]

## Deferred
- <item> — reason: <why> — lands in: <next slice | backlog>

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` -> `## Triage` table + reality observed during build/validate:

- B1 (<title>): VALIDATED — disposition ACCEPTED-FIXED; bug appeared exactly as flagged during validation
- B2 (<title>): VALIDATED — disposition ACCEPTED-PENDING; reality confirmed concern when fix landed
- M1 (<title>): FALSE-ALARM — disposition OVERRIDDEN by user with reasoning X; reality confirmed override was correct (Critic over-reached)
- M2 (<title>): OVERRIDE-MISJUDGED — disposition OVERRIDDEN by user reasoning X; reality showed Critic was right after all (calibration signal for both Critic AND user)
- m1 (<title>): NOT-YET — disposition DEFERRED to slice-NNN; will re-score there

**Missed by Critic**: <things that surfaced during build/validate that Critic didn't flag>

**Pattern**: <observation about Critic accuracy for future tuning>

## Lessons for next slice
- <actionable insight>
- <actionable insight>

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — added R7 (...)
- [[decisions/ADR-NNN.md]] — finalized with library choice
- This slice's [[design.md]] — corrected async claim to sync (build-log notes the deviation)
```

(In Standard / Minimal mode, this list is short. No `components/X.md` updates because those files don't exist — code is the source of truth. If your reflection has lots of file updates, you might be in Heavy mode, OR you're documenting what code already shows.)

> **Vault-write safety (SVW-1 / [[ADR-087]]; RMW class closed at slice-097 / [[ADR-088]])** — mutations of shared-aggregate vault files (`risk-register.md`, `lessons-learned.md`, `build-checks.md`, `shippability.md`, `_index.md`) go through the R-32 safe channel by OP-CLASS: **appends** via `$PY -m tools.vault_edit append --file <name> --content-file <tmp>` (write the block to a temp file first); **read-modify-writes** (the `_index.md` recent-10 regen + in-place risk-status flips) via `$PY -m tools.vault_edit rewrite` (compare-and-swap — capture the base with `read --out-file`, then `rewrite --base-file`; exit 3 → re-read + retry). NEVER a raw `Write`/`Edit` on these files (it bypasses the `_vault_write` lock — the silent lost-update/torn-write class once the vault goes shared). The RMW class is now ENFORCED, not deferred — a rewrite-class directive routed through the unsafe `append` channel is a channel-mismatch violation. Enforced by `tools/skill_vault_write_safety_audit.py`.

### Step 5: Append to `<vault>/lessons-learned.md` <!-- route: tools.vault_edit append -->

Append a chronological entry:

```markdown
## Slice NNN (<name>) — <YYYY-MM-DD>

### Worked
- <what about the design / process / approach worked>

### Didn't work
- <what didn't>

### Pattern
- <generalizable insight for future slices>
```

### Step 5b: Promotion to build-checks (BC-1)

Per **BC-1** (`methodology-changelog.md` v0.10.0), `/reflect` is where lessons-learned graduates to evergreen build-checks. Lessons-learned is a chronological journal — most entries don't matter to future slices. Build-checks is the curated, applies-at-every-slice layer that `/build-slice` reads at pre-finish.

Ask the user explicitly:

> Did this slice surface a **recurring pattern** that should become a build-check? (y/N)
>
> Examples of patterns worth promoting:
> - "Image uploads need EXIF orientation normalization" — third time this slice hit it
> - "JWT verification must check signature, not just decode claims" — root cause of two prior bugs
> - "Migrations must include a down() reverse" — caught only in pre-prod
>
> Examples NOT worth promoting (one-off fixes):
> - A typo in this slice's design
> - A library version bump
> - A specific endpoint's specific bug

If the user answers yes, gather:

1. **Title** (one line, imperative). Example: "All file uploads normalize EXIF orientation before storage"
2. **Severity** — `Critical` (must address; not deferrable) or `Important` (surface; defer-with-rationale allowed)
3. **Applies to** — file globs (e.g., `src/api/uploads/**, src/services/*upload*.py`) OR `always: true`
4. **Trigger keywords** — comma-separated, lowercased words to match in mission-brief.md / design.md (e.g., `upload, image, jpeg, heic`)
5. **Check** — actionable verification step (one paragraph)
6. **Rationale** — why this is permanent, not a one-time fix (one paragraph; reference prior slices where the pattern recurred)
7. **Validation hint** — how to verify (grep, pytest -k, curl, etc.)

Append the rule to `<vault>/build-checks.md` under the `## Rules` heading, using the next available `BC-PROJ-NNN` ID. Format (parsed by `tools/build_checks_audit.py`): <!-- route: tools.vault_edit append -->

```markdown
## BC-PROJ-NNN — <title>

**Severity**: Critical | Important
**Applies to**: <globs> OR always: true
**Promoted from**: slice-NNN-<name> (<YYYY-MM-DD>) — <recurrence note if any>
**Trigger keywords**: <comma-separated>

**Check**: <verification step>

**Rationale**: <why permanent>

**Validation hint**: <how to verify>
```

If `<vault>/build-checks.md` doesn't exist yet, create it with the canonical header (see `tests/methodology/fixtures/build_checks/clean_project_checks.md` for the template).

**Optional global promotion**: if the rule is generic enough to apply to **all projects** (not just this one), also offer to append it to `~/.claude/build-checks.md` with a `BC-GLOBAL-NNN` ID. Examples of globally generic rules: secrets in code, JWT signature verification, SQL injection prevention, file-upload size limits. Project-specific rules (e.g., "the `receipts` table requires `merchant_id`") stay project-only.

> **BCI-1 fail-loud post-write step (mandatory when a rule was promoted)** — per **BCI-1** (`methodology-changelog.md` v0.44.0; slice-030A; [[ADR-028]] + [[ADR-029]]). This Step 5b is LLM-executed prose with no deterministic promotion function; R-4 witnessed a whole-file truncation where every prior rule + the schema preamble was silently lost. To make any such truncation/divergence loud immediately rather than ship silently:
>
> 1. After authoring the new rule, **also add the same rule to the git-tracked canonical fixture** — `tests/methodology/fixtures/build_checks/canonical_project_checks.md` (or `canonical_global_checks.md` for a `BC-GLOBAL-NNN`) — AND a literal-constant full-structural-identity pin in `tests/methodology/test_build_checks_audit.py` (the fixture is the subject; the literal constant is the tracked oracle — see ADR-028). The fixture, not the gitignored live file, is the source of truth.
> 2. Reconstruct the live file from the fixture (byte-copy), then run:
>
>    ```bash
>    $PY -m tools.build_checks_integrity
>    ```
>
> 3. If it exits non-zero (`drift`/HALT): **STOP and report** — a prior rule, the schema preamble, or a structural field was lost/diverged. Do NOT proceed; reconstruct from the fixture. Exit 0 (incl. the global-absent WARN) is required before Step 5b is considered done. This is the deterministic downstream gate that retires R-4's silent-degradation class (the prose itself cannot be made defect-proof — ADR-029).

If the user answers no, skip — promotion is opt-in and never auto-applied. Recurring patterns missed at this step still surface in lessons-learned.md and can be promoted in a later slice.

### Step 5b-fs: Methodology-changelog forward-sync gate (MCFS-1)

Per **MCFS-1** (`methodology-changelog.md` v0.53.0; slice-041, split-lineage label "030C"; [[ADR-042]] + [[ADR-043]]): a deterministic downstream gate asserting in-repo `methodology-changelog.md` is content-equal **modulo line endings** to the installed `~/.claude/methodology-changelog.md`. slice-041 re-homed the ~33 per-version `test_v_0_NN_0_*` essential reads that half-asserted this invariant onto this single whole-file gate.

> **This is a SEPARATE, UNGATED step — explicitly NOT folded into Step 5b** (m1 / DR-1). Step 5b (build-checks promotion) is rule-promotion-gated ("promotion is opt-in"); the methodology-changelog forward-sync must fire on **any slice that bumped the methodology-changelog version**, independent of whether a build-checks rule was promoted. Folding it into the rule-promotion-gated Step 5b would silently disable the gate on a version-bumping-but-no-rule-promoted slice (the R-7/slice-022 silent-disable class). Run it whenever this slice edited `methodology-changelog.md` (PMI-1 4-part bump):
>
> ```bash
> $PY -m tools.methodology_changelog_forward_sync
> ```
>
> If it exits non-zero (`drift`/HALT): **STOP and report** — the in-repo → `~/.claude/` forward-sync was forgotten or diverged. Re-run the PMI-1 forward-sync (byte-copy in-repo → installed) and re-run until exit 0 (incl. the installed-absent WARN, also exit 0). This is the deterministic downstream control that retires R-4's essential-class residual (the per-version installed reads are decoupled; ADR-042). MCFS-1 is also wired non-opt-out at `/build-slice` Step 6 (likewise ungated) — the two ungated points are complementary, neither gated on rule promotion.

### Step 5b-avfs: ai-sdlc-VERSION forward-sync gate (AVFS-1)

Per **AVFS-1** (`methodology-changelog.md` v0.58.0; slice-050; [[ADR-052]]; extends the slice-041/MCFS-1 forward-sync-via-deterministic-downstream-gate lineage): a deterministic downstream gate asserting in-repo `VERSION` is content-equal **modulo line endings** (CRLF→LF only) to the installed `~/.claude/ai-sdlc-VERSION` — the 4th PMI-1 leg PMI-1 never reads and MCFS-1 does not cover (it drifted silently N=2: slice-035 DEVIATION-2, slice-048→049).

> **This is a SEPARATE, UNGATED step — explicitly NOT folded into Step 5b** (MCFS-1 Step 5b-fs parity). Step 5b (build-checks promotion) is rule-promotion-gated; the ai-sdlc-VERSION forward-sync must fire on **any slice that bumped the PMI-1 version**, independent of whether a build-checks rule was promoted. Folding it into the rule-promotion-gated Step 5b would silently disable the gate on a version-bumping-but-no-rule-promoted slice (the R-7/slice-022 silent-disable class). Run it whenever this slice performed a PMI-1 4-part bump:
>
> ```bash
> $PY -m tools.ai_sdlc_version_forward_sync
> ```
>
> If it exits non-zero (`drift`/HALT): **STOP and report** — the in-repo `VERSION` → `~/.claude/ai-sdlc-VERSION` forward-sync was forgotten or diverged. Re-run the PMI-1 4-part forward-sync (byte-copy in-repo `VERSION` → installed `~/.claude/ai-sdlc-VERSION`) and re-run until exit 0 (incl. the installed-absent WARN, also exit 0). This is the deterministic downstream control retiring the slice-035/048/049 N=2 silent-drift class. AVFS-1 is also wired non-opt-out at `/build-slice` Step 6 (likewise ungated) — the two ungated points are complementary, neither gated on rule promotion.

### Step 5b-tvfs: ai-sdlc-tools version forward-sync gate (TVFS-1)

Per **TVFS-1** (`methodology-changelog.md` v0.63.0; slice-059; [[ADR-058]]; extends the slice-050/AVFS-1 + slice-041/MCFS-1 forward-sync-via-deterministic-downstream-gate lineage): a deterministic downstream gate asserting the `ai-sdlc-tools` pip distribution installed in the running interpreter's venv site-packages equals trimmed in-repo `VERSION` — the installed-pip-artifact leg PVFS-1 (source `pyproject.toml`) cannot cover, since PVFS-1 makes the *next* `pip install` correct but never forces the *re-install* (the venv package drifted silently to `0.20.0`).

> **This is a SEPARATE, UNGATED step — explicitly NOT folded into Step 5b** (AVFS-1 Step 5b-avfs parity). Step 5b (build-checks promotion) is rule-promotion-gated; the ai-sdlc-tools version forward-sync must fire on **any slice that bumped the PMI-1 version**, independent of whether a build-checks rule was promoted (folding it into the rule-promotion-gated Step 5b would silently disable the gate on a version-bumping-but-no-rule-promoted slice — the R-7/slice-022 silent-disable class). Run it whenever this slice performed a PMI-1 version bump:
>
> ```bash
> $PY -m tools.ai_sdlc_tools_version_forward_sync
> ```
>
> If it exits non-zero (`drift`/HALT): **STOP and report** — the installed `ai-sdlc-tools` pip package was not re-installed after this slice's version bump. Run `$PY -m pip install --upgrade <ai-sdlc-source>` (INSTALL.md Step 3g) and re-run until exit 0 (incl. the not-installed WARN, also exit 0). This is the deterministic downstream control retiring the installed-pip-artifact silent-drift class. TVFS-1 is also wired non-opt-out at `/build-slice` Step 6 (likewise ungated) — the two ungated points are complementary, neither gated on rule promotion.

### Step 5.3: Add one entry to `<vault>/shippability.md` <!-- route: tools.vault_edit append -->

Every completed slice contributes ONE critical-path test to the shippability catalog. Future `/validate-slice` runs execute the full catalog to catch regressions.

Ask yourself: **"If this slice silently broke later, what's THE one test that would catch it first?"** That's the critical path for this slice.

Append to `<vault>/shippability.md`: <!-- route: tools.vault_edit append -->

```markdown
| <next-#> | slice-NNN-<name> | <one-line critical path> | `<runnable command>` | <expected runtime> |
```

Rules for the critical-path entry:

- **One line** describing the path (e.g., "POST /receipts accepts HEIC with EXIF orientation preserved")
- **Runnable command** (curl, pytest -k, bash script, cypress spec). Must work as-is from project root.
- **Expected runtime** — keep to <10 seconds per entry. Shippability runs add up; if a slice's critical path takes minutes, split it into a faster smoke + a thorough CI-only version.
- Must be TEST, not manual step. `/validate-slice` runs the catalog programmatically.

If `<vault>/shippability.md` doesn't exist yet, create it with header:

```markdown
# Shippability Catalog

Critical-path tests from every slice. `/validate-slice` runs these at pre-finish to catch regressions introduced by the current slice breaking past slices' critical paths.

| # | Slice | Critical path | Command | Runtime |
|---|-------|--------------|---------|---------|
```

### Step 5.5: Refresh the knowledge graph

Code shipped this slice. Refresh graphify so the graph reflects current state:

```bash
# If /triage or /adopt installed the post-commit git hook: already done at commit time — skip.
# If --watch is running in another terminal: already done — skip.
# Otherwise:
$PY -m graphify code .   # rebuild is fast; CLI has no incremental --update flag
```

This keeps GRAPH_REPORT.md current. The next slice's `/design-slice` and `/critique` will query a fresh graph.

### Step 5.8: Update milestone.md to complete

Final update to `architecture/slices/slice-NNN-<name>/milestone.md`:

- Frontmatter: `stage: complete`, `updated: <today>`, `next-action: none (slice complete)`
- Check progress box: `- [x] /reflect — <date>`
- "Current focus": brief one-line ("Slice shipped. Lessons captured. Auto-archiving next.")
- All phase artifact statuses should now show complete/PASS/etc.

After this update, the immediate next step (Step 6) auto-moves the whole slice folder (including milestone.md) to `slices/archive/`. The archived milestone.md is a frozen snapshot — the "complete" state becomes permanent history.

### Step 6: Auto-archive this slice

The convention: `slices/` holds ACTIVE slices only; completed slices live in `slices/archive/` with lookup via `slices/_index.md`.

After writing `reflection.md`, this slice is complete. Archive it immediately:

1. `$PY -m tools.vault_edit move --from slices/slice-NNN-<name> --to slices/archive/` (R-32 seam-routed archive move — [[ADR-103]]; resolves BOTH endpoints under `VAULT_ROOT` so the move follows the vault to the external store at flip instead of a hardcoded in-tree path; refuses if `slices/archive/slice-NNN-<name>` already exists, preserving the no-overwrite semantic)
2. Regenerate `<vault>/slices/_index.md` — update the "Active" table (remove this slice), update the "Most recent 10" table (add this slice at the top as a THIN one-liner from this slice's mission-brief Intent, ≤500 chars, and drop the now-oldest row so the table stays EXACTLY 10 — the thin-router contract enforced by `tools/index_router_thinness_audit.py` per slice-103 / ADR-093). Do NOT touch the curated `slices/action-points.md` register and do NOT add an all-history "Aggregated lessons" dump (it was relocated out at ADR-093; `_index.md` carries only a `## Cross-slice action points` pointer); the slice's full "Lessons for next slice" items go to `lessons-learned.md` at Step 5 as usual. This is a read-modify-write, so apply it via `vault_edit rewrite` (R-32 CAS — [[ADR-088]]): `$PY -m tools.vault_edit read --file slices/_index.md --out-file base.bin` (use `--out-file`, NOT shell `>` — PowerShell's `>` corrupts the base to UTF-16LE+BOM → CAS livelock), regenerate into a copy, then `$PY -m tools.vault_edit rewrite --file slices/_index.md --base-file base.bin --content-file <regen>`; on exit 3 (a parallel slice completed first) re-read + re-regenerate + retry (bounded ~5, then STOP loudly). Verify byte-integrity afterward (no CRLF→LF churn).
3. Prepend this slice's THIN one-liner row (4-col `| # | Slice | Shipped | one-liner ≤500 |`, the one-liner from this slice's mission-brief Intent — per the ADR-093 thin-router contract) to the TOP of `<vault>/slices/archive/_index.md` (the catalog is newest-at-top — see its header), right after the table separator. This is a read-modify-write (insert at the top of an existing file), so apply it via `vault_edit rewrite` (R-32 CAS — [[ADR-088]]): `$PY -m tools.vault_edit read --file slices/archive/_index.md --out-file base.bin` (use `--out-file`, NOT shell `>`), insert the row after the separator in a copy, then `$PY -m tools.vault_edit rewrite --file slices/archive/_index.md --base-file base.bin --content-file <edited>`; on exit 3 re-read + re-apply + retry (bounded ~5). NOT `vault_edit append` — appending at EOF puts the row at the OLDEST position in a newest-first catalog (slice-097 /reflect live-fire discovery D1).

This is the same work as `/archive --index-only` but triggered automatically by slice completion. If you'd rather skip auto-archive and batch it later, explicitly tell the user: "Leaving slice in `slices/` — run `/archive` to sweep later." Only do this if the user requests it.

### Step 7: Preview next-slice candidates

Don't just say "run /slice next" — preview top candidates so the user sees what's on deck. This maintains continuity from reflection into next-slice planning.

Gather candidates from:
- This slice's **Discovered** items → candidates for addressing new risks
- This slice's **Deferred** items → candidates for completing deferred scope
- Recent `risk-register.md` active HIGH risks
- `concept.md` scope not yet built

Do a quick ranking (lightweight — `/slice` will do the full scoring):

```
Next-slice candidates (preview — run `/slice` for full scoring):

🏆 #1: <verb-object name>
   Reason: <one line — what risk it retires OR what deferred item it completes>

#2: <verb-object name>
   Reason: <one line>

#3: <verb-object name>
   Reason: <one line>
```

Keep it short — this is a preview, not the full ranked list. `/slice` does the deep work.

### Step 8: Close

State:
- "Reflection complete. Vault updates: <list files>."
- "Slice archived to `slices/archive/slice-NNN-<name>/`. Index refreshed."
- "Discoveries: <count> (added to risk register)."
- "Deferrals: <count> (surfaced above as slice candidates)."
- "Run `/slice` to formally select + define the next cut. I've previewed candidates above."

Archived slices are easy to find via `<vault>/slices/_index.md`. Full catalog in `archive/_index.md`. Direct file access via `slices/archive/slice-NNN-<name>/` still works.

## Critical rules

- HONESTY DISCIPLINE: this is not a victory lap. Capture what didn't work, where you got lucky, where you're still guessing.
- UPDATE THE VAULT for every Corrected item. The vault must reflect reality, not the original design.
- DO NOT edit superseded ADRs. Decisions are append-only history.
- TRACK Critic accuracy every slice. This data compounds.
- IF discoveries section is empty across multiple slices: either you're not learning or not capturing. Push harder.

## Honesty discipline examples

GOOD reflection (honest):
> "Discovered: HEIC EXIF orientation issue. We got lucky that one user complained early; without that, sideways thumbnails would've been in production for weeks. Pattern: image-handling slices need EXIF awareness in mission brief."

BAD reflection (sales pitch):
> "All acceptance criteria passed. The team did a great job implementing the design as planned. No major issues."

The bad version teaches nothing for the next slice. The good version arms you for the future.

## Vault update examples

In Standard / Minimal mode (thin vault), most "behavior corrections" don't need vault edits — code IS the truth. But there are still cases:

**Decision wrong**: ADR-008 said "use SQS for async uploads"; you implemented sync. Don't edit ADR-008. Mark it `status: superseded`, create ADR-014 with `supersedes: ADR-008` documenting why sync now and when async planned.

**Risk claim wrong**: risk-register.md said "R3 retired by spike-002" but reality is R3 only retired for the simple case; complex case still risky. Update risk-register.md to reflect that nuance.

**Slice design wrong (vs what shipped)**: this slice's design.md said "async via SQS"; you shipped sync. Update this slice's design.md (the slice is the source of truth for what was decided/built). Also note in build-log.md: "Deviated from design — sync instead of async; rationale in reflection.md."

In Heavy mode (where `components/storage-service.md` exists): also update that file. But Heavy mode is the exception, not the default.

## Next step

`/slice` — define the next cut, informed by this slice's discoveries and deferrals.

## Pipeline position

- **predecessor**: `/validate-slice`
- **successor**: `/commit-slice`
- **auto-advance**: false
- **on-clean-completion**: TERMINAL-BEFORE-COMMIT. Once reflection.md is written and the slice is auto-archived, do NOT auto-invoke `/commit-slice` — the user always invokes it manually. Present a concise hand-off ("slice complete; run `/commit-slice` to generate the audit-grade commit"). The `/reflect`→`/slice` next-slice kickoff is out of scope (a deliberate user decision).
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Terminal stop — the chain ALWAYS halts here. `/commit-slice` is user-invoked by contract.

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. This is the auto-advance terminus: `/commit-slice` is never auto-invoked under any path.
