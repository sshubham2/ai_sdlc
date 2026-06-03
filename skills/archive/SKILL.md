---
name: archive
description: "AI SDLC maintenance. Archive completed slices and maintain slices/_index.md — the single lookup point for any past slice. Convention: slices/ holds only ACTIVE slices (no reflection.md yet); slices/archive/ holds ALL completed slices. _index.md is how Claude finds past work — it holds the recent-10 catalog (thin one-liners) + a pointer to the curated action-points.md register + pointers to archive/_index.md for the full catalog. /reflect auto-archives each completed slice; /archive is for rebuilding the index or batch operations on manually-moved folders. Trigger phrases: '/archive', 'archive completed slices', 'rebuild slice index', 'regenerate _index.md'."
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
- `architecture/slices/_index.md` — THE lookup: active list + recent-10 (thin one-liners) + pointer to `action-points.md` + pointer to archive catalog
- `architecture/slices/archive/_index.md` — full chronological catalog of archived slices

Claude finds past work via `_index.md` — no mixing of "recent-but-completed" with active.

## Argument modes

- `/archive` — sweep: move any slice with `reflection.md` from `slices/` to `slices/archive/`; regenerate `_index.md` + `archive/_index.md` via `vault_edit rewrite` (R-32 CAS — see Step 3)
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

### Step 3: Regenerate `slices/_index.md` via Haiku dispatch + `vault_edit rewrite` (R-32 CAS — [[ADR-088]])

Per **COST-1** (cost-optimized model selection — `methodology-changelog.md` v0.4.0), index regeneration is dispatched to a Haiku subagent. This step and Step 4 (the archive catalog) both go to Haiku.

**Dispatch + CAS write (the MAIN THREAD owns the compare-and-swap — [[ADR-088]] / critique B3):** the read→regenerate→write loop spans a subagent boundary (the Haiku agent regenerates the content; the main thread writes), so the CAS lives in the MAIN THREAD, never the subagent:
- Main thread captures a byte-exact base for EACH target into a DISTINCT file (use `--out-file`, NOT shell `>` — PowerShell `>` corrupts bytes to UTF-16LE+BOM → CAS livelock): `$PY -m tools.vault_edit read --file slices/_index.md --out-file idx_base.bin` AND `$PY -m tools.vault_edit read --file slices/archive/_index.md --out-file archive_base.bin`. (One base file per target — reusing one base across the two distinct files would always conflict.)
- Use the Agent tool with `subagent_type: "general-purpose"` and `model: haiku`. Hand the agent the active and archived slice paths (lists), the templates from Step 3 + Step 4 below, and instruction to read each slice's `mission-brief.md` (for one-line intent) and recent reflections' "Lessons" sections. The agent is a pure content generator — it has NO lock/CAS responsibility.
- The agent returns both `_index.md` files' content. The MAIN THREAD writes `slices/_index.md` via `$PY -m tools.vault_edit rewrite --file slices/_index.md --base-file idx_base.bin --content-file <regen>` (and `slices/archive/_index.md` with `--base-file archive_base.bin` per Step 4).
- **On exit 3** (CAS conflict — a parallel slice completion wrote `_index.md` between the base-capture and the write): the main thread RE-captures the base AND RE-dispatches the Haiku regeneration (so the regen picks up the concurrent slice's row), bounded to ~5 attempts. If still conflicting after the bound: STOP loudly. **Recovery (m-add-3):** the Step-2 `mv` has already moved the folder, so the fail-STOP leaves a recoverable state — re-run `/archive --index-only` to redo only the index regeneration without re-moving.

**Why Haiku**: index regeneration is reading folder contents (mission-brief intent, reflection lessons, dates) and assembling tables. No synthesis. The agent reads ~10-N files in its fresh context, which keeps the main thread's context lean for the rest of the session.

This is THE lookup file. Claude reads it to find past work instead of scanning individual slice folders.

Read (the dispatched agent does this; listed here so the spec is clear):
- Each active slice folder in `slices/` (for the Active table)
- Last 10 archived slices in `slices/archive/` (for the Recent-10 table one-liners, pulled from each slice's mission-brief Intent). The action-points register is NOT regenerated — it lives in the curated `slices/action-points.md`.

Write `architecture/slices/_index.md` (via `vault_edit rewrite` per the Step-3 CAS protocol above):

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

**THIN-ROUTER CONTRACT (ADR-093 / slice-103, enforced by `tools/index_router_thinness_audit.py`):** EXACTLY the 10 most recent rows; each row is ONE physical line; the one-line summary is pulled from the slice's `mission-brief.md` "Intent" (first sentence, trimmed) and MUST be ≤ 500 chars. Do NOT paste the reflection's full summary paragraph — this table is a router, not a store. The audit fails the slice-finish gate (shippability) on a >500-char row or >10 rows.

### Cross-slice action points (pointer — NOT regenerated here)

The synthesized, bounded action-points register lives in its OWN file **`architecture/slices/action-points.md`** (relocated out of `_index.md` at ADR-093 so the regen path physically cannot re-bloat it). It is a **curated** artifact — `/archive` and `/reflect` do NOT regenerate it; they leave it untouched. Emit only a pointer in `_index.md`:

```
## Cross-slice action points

The bounded action-points register (pattern-recognition input for `/slice` + `/critique`) lives in [`action-points.md`](action-points.md). Full per-slice lesson history: [`../lessons-learned.md`](../lessons-learned.md).
```

Do NOT pull an all-history lesson dump into `_index.md` (the slice-103 root cause: the old "Aggregated lessons" section had grown to 631 lines / 542 bullets — every lesson already lives durably in `lessons-learned.md`).

## How Claude uses this index

- **Looking up "did we build X?"** → scan "Most recent 10" and "Full catalog" (archive/_index.md); if match, read `archive/slice-NNN/` for details.
- **Pattern recognition before /design-slice or /critique** → read the curated [`action-points.md`](action-points.md) register. For specific patterns, follow to the relevant archived slice or `lessons-learned.md`.
- **Finding a related past decision** → search ADRs (`decisions/`), then cross-reference slice that locked the ADR (`slice:` frontmatter field in ADR).
- **Full-text search across archived slices** → grep `architecture/slices/archive/` (still works — archive is just a directory).
```

### Step 4: Regenerate `slices/archive/_index.md` (via `vault_edit rewrite` per the Step-3 CAS protocol)

Full chronological catalog of archived slices (the main thread writes the Haiku-regenerated content via `$PY -m tools.vault_edit rewrite --file slices/archive/_index.md --base-file archive_base.bin --content-file <regen>`, same exit-3 re-dispatch loop as Step 3):

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
- slices/_index.md regenerated (thin recent-10 + action-points pointer; the curated action-points.md left untouched)
- slices/archive/_index.md regenerated (full catalog)

To find a past slice, check slices/_index.md first.
```

## Critical rules

- NEVER delete slice folders. Archive is `mv`, never `rm`. Slice history is audit trail.
- NEVER touch file contents during archive. Just move + regenerate indexes.
- NEVER leave completed slices in `slices/` (with `reflection.md`). That breaks the convention.
- DO regenerate both `_index.md` files on every run, writing each via `vault_edit rewrite` (R-32 CAS — Step 3 protocol).
- The `_index.md` content stays a THIN router — recent-10 one-liners (≤500 chars, from each slice's mission-brief Intent, not the reflection's full summary) plus a pointer to the curated `slices/action-points.md` register; never an all-history lesson dump (the slice-103 / ADR-093 thin-router contract). `/archive` leaves `slices/action-points.md` untouched (it is curated, not regenerated here).
- HEAVY MODE: same flow. Audit trail is preserved; archived slices remain accessible at `archive/slice-NNN/`.

## How other skills use `_index.md`

- **`/reflect`**: auto-archives the slice after writing reflection.md (moves to `slices/archive/`), then calls `/archive --index-only` to refresh the index
- **`/slice`**: reads `slices/_index.md` (active work, recent-10) + the curated `slices/action-points.md` register for pattern recognition — that's all; doesn't scan individual archived slice folders
- **`/critique`**: reads `slices/action-points.md` + "Most recent 10" from `slices/_index.md` for pattern recognition; follows specific links only if a pattern is relevant to the current slice
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
