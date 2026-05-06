---
name: archive
description: "AI SDLC maintenance. Archive completed slices and maintain slices/_index.md — the single lookup point for any past slice. Convention: slices/ holds only ACTIVE slices (no reflection.md yet); slices/archive/ holds ALL completed slices. _index.md is how Claude finds past work — it holds the recent-10 catalog + aggregated lessons + pointers to archive/_index.md for the full catalog. /reflect auto-archives each completed slice; /archive is for rebuilding the index or batch operations on manually-moved folders. Trigger phrases: '/archive', 'archive completed slices', 'rebuild slice index', 'regenerate _index.md'."
user_invokable: true
argument-hint: [--index-only]
---

# /archive — Slice Archival + Index Maintenance

You archive completed slices to `slices/archive/` and maintain `slices/_index.md` (the single lookup point for all past slices). In normal flow, `/reflect` auto-archives each slice when it finishes. `/archive` exists for:

- Rebuilding a stale or missing `_index.md` (`--index-only`)
- Batch cleanup after manual moves or external edits
- Forcing archival of stuck "complete but not auto-archived" slices

## Convention

- `architecture/slices/` — ACTIVE slices only (no `reflection.md` yet)
- `architecture/slices/archive/` — ALL completed slices (with `reflection.md`)
- `architecture/slices/_index.md` — THE lookup: active list + recent-10 + aggregated lessons + pointer to archive catalog
- `architecture/slices/archive/_index.md` — full chronological catalog of archived slices

Claude finds past work via `_index.md` — no mixing of "recent-but-completed" with active.

## Argument modes

- `/archive` — sweep: move any slice with `reflection.md` from `slices/` to `slices/archive/`; regenerate `_index.md` + `archive/_index.md`
- `/archive --index-only` — rebuild indexes without moving anything (use when indexes are stale or missing)

No `--keep-last` flag: the convention is "no completed slices in `slices/`". If you want something visible in active, un-archive it with `mv` (acceptable for edge cases, not routine).

## Prerequisite check

- `architecture/slices/` must exist

## Your task

### Step 1: Enumerate current state

Scan (non-recursive):

- `slices/` → active candidates (no reflection.md) + violators (completed slices that shouldn't still be here)
- `slices/archive/` → archived slices (should all have reflection.md)

If `--index-only`: skip to Step 3.

### Step 2: Sweep

For each slice in `slices/` that has `reflection.md`:

- `mv architecture/slices/slice-NNN-* architecture/slices/archive/`
- Preserve folder contents exactly

Tell user: "Archived N slices to `slices/archive/`."

Edge case: if `slices/archive/<same-name>/` already exists (rare, only from manual edits): stop and ask user to resolve manually. Don't overwrite.

### Step 3: Regenerate `slices/_index.md` via Haiku dispatch

Per **COST-1** (cost-optimized model selection — `methodology-changelog.md` v0.4.0), index regeneration is dispatched to a Haiku subagent. This step and Step 4 (the archive catalog) both go to Haiku.

**Dispatch:**
- Use the Agent tool with `subagent_type: "general-purpose"` and `model: haiku`.
- Hand the agent the active and archived slice paths (lists), the templates from Step 3 + Step 4 below, and instruction to read each slice's `mission-brief.md` (for one-line intent) and recent reflections' "Lessons" sections.
- The agent returns both `_index.md` files' content. Main thread writes them to disk.

**Why Haiku**: index regeneration is reading folder contents (mission-brief intent, reflection lessons, dates) and assembling tables. No synthesis. The agent reads ~10-N files in its fresh context, which keeps the main thread's context lean for the rest of the session.

This is THE lookup file. Claude reads it to find past work instead of scanning individual slice folders.

Read (the dispatched agent does this; listed here so the spec is clear):
- Each active slice folder in `slices/` (for the Active table)
- Last 10 archived slices in `slices/archive/` (for Recent table + Aggregated lessons)

Write `architecture/slices/_index.md`:

```markdown
# Slice Index

**Project**: <from concept.md>
**Mode**: <from triage.md>
**Totals**: <total> slices (<A> active, <C> archived)
**Last updated**: <YYYY-MM-DD>

## Active

| # | Name | Stage | Started |
|---|------|-------|---------|
| 046 | [email-digest](slice-046-email-digest/) | build | 2026-04-18 |
| 047 | [notification-prefs](slice-047-notification-prefs/) | design | 2026-04-20 |

Stage is derived from which files exist:
- no `design.md` → "slice"
- no `critique.md` → "design"
- no `build-log.md` → "critique"
- no `validation.md` → "build"
- no `reflection.md` → "validate"

## Past slices (all archived)

Full catalog: [archive/_index.md](archive/_index.md)

### Most recent 10

| # | Name | Completed | One-line summary |
|---|------|-----------|------------------|
| 045 | [add-csv-export](archive/slice-045-add-csv-export/) | 2026-04-19 | CSV export from expenses page |
| 044 | [onboarding-flow](archive/slice-044-onboarding-flow/) | 2026-04-17 | first-run UX + empty states |
| 043 | [settings-page](archive/slice-043-settings-page/) | 2026-04-14 | user prefs + password change |
| ... |

One-line summary: pulled from the "Intent" section of `mission-brief.md`, trimmed to one line.

### Aggregated lessons (from recent reflections)

- <lesson from slice-045's "Lessons for next slice">
- <lesson from slice-044's "Lessons for next slice">
- <lesson from slice-043's "Lessons for next slice">
- <etc. — up to ~10 from the most recent reflections>

These are the patterns future slices should respect. Source: `archive/slice-NNN/reflection.md` (Lessons section).

## How Claude uses this index

- **Looking up "did we build X?"** → scan "Most recent 10" and "Full catalog" (archive/_index.md); if match, read `archive/slice-NNN/` for details.
- **Pattern recognition before /design-slice or /critique** → read "Aggregated lessons" section. For specific patterns, follow to the relevant archived slice.
- **Finding a related past decision** → search ADRs (`decisions/`), then cross-reference slice that locked the ADR (`slice:` frontmatter field in ADR).
- **Full-text search across archived slices** → grep `architecture/slices/archive/` (still works — archive is just a directory).
```

### Step 4: Regenerate `slices/archive/_index.md`

Full chronological catalog of archived slices:

```markdown
# Archived Slices — Full Catalog

Total: <N>
Last updated: <YYYY-MM-DD>

## By number (chronological)

| # | Name | Completed | Summary |
|---|------|-----------|---------|
| 001 | [setup-database](slice-001-setup-database/) | 2026-01-05 | initial schema + migrations |
| 002 | [user-auth](slice-002-user-auth/) | 2026-01-08 | email/password + magic link |
| ... |
| <N> | [<name>](slice-NNN-<name>/) | <date> | <one-liner> |

## How to find a specific past slice

- Know the number? → `slice-NNN-<name>/` in this directory
- Know a keyword from the name? → grep this file
- Know an ADR that was locked? → check ADR's `slice:` frontmatter
- Need full-text? → `grep -r "<keyword>" architecture/slices/archive/`
```

### Step 5: Summary

Close with:

```
Archive sweep complete.
- Active slices: <A> (in slices/)
- Archived: <C> (in slices/archive/)
- slices/_index.md regenerated (recent-10 + aggregated lessons)
- slices/archive/_index.md regenerated (full catalog)

To find a past slice, check slices/_index.md first.
```

## Critical rules

- NEVER delete slice folders. Archive is `mv`, never `rm`. Slice history is audit trail.
- NEVER touch file contents during archive. Just move + regenerate indexes.
- NEVER leave completed slices in `slices/` (with `reflection.md`). That breaks the convention.
- DO regenerate both `_index.md` files on every run.
- DO pull the "Aggregated lessons" from actual reflection.md files — don't fabricate patterns.
- HEAVY MODE: same flow. Audit trail is preserved; archived slices remain accessible at `archive/slice-NNN/`.

## How other skills use `_index.md`

- **`/reflect`**: auto-archives the slice after writing reflection.md (moves to `slices/archive/`), then calls `/archive --index-only` to refresh the index
- **`/slice`**: reads `slices/_index.md` to see active work, recent completions, aggregated lessons — that's all; doesn't scan individual archived slice folders
- **`/critique`**: reads "Aggregated lessons" + "Most recent 10" from `slices/_index.md` for pattern recognition; follows specific links only if a pattern is relevant to the current slice
- **`/design-slice`**: same — reads index; archived slice files only as needed
- **`/drift-check`**: scans `slices/` (active only now — no completed slices mixed in); ignores `slices/archive/` entirely
- **`graphify`**: builds graph including `archive/` (archived slices remain queryable)

## When to run /archive manually

- Indexes look stale (haven't been regenerated in a while)
- After cloning the repo — `/archive --index-only` to rebuild
- After manual moves (you `mv`'d a slice folder; index doesn't reflect it)
- A `/reflect` was interrupted before auto-archival completed

## Index-only mode

`/archive --index-only`:

- Does NOT move any files
- Regenerates both index files from current directory state
- Useful when: index got stale, files were moved manually, after fresh clone

## Performance

With the new convention (active slices only in `slices/`):

- `/drift-check` scans maybe 2-5 active slice folders — sub-second regardless of project age
- `/critique` reads `_index.md` (one file) + current slice — fast
- `/slice` reads `_index.md` — fast
- `$PY -m graphify vault` traverses archive but it's a one-time query; build it once, query many times

The convention scales to 500+ total slices with no scan-time degradation for the common operations.

## Next step

- Normal: resume current slice work or run `/slice` for next cut
- If something feels off (wrong number of active, missing archived): verify with `ls architecture/slices/` and `ls architecture/slices/archive/`, then `/archive --index-only` to refresh indexes
