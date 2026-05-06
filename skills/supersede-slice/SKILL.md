---
name: supersede-slice
description: "AI SDLC pipeline. Cleanly retire a shipped (archived) slice when reality has contradicted its design. Adds a `## Supersession` section to the archived slice's reflection.md and links it to the new slice that supersedes it. Per SUP-1 (`methodology-changelog.md` v0.19.0). Use when an archived slice's claims need to be marked obsolete — typically when a fix slice in active development would otherwise leave the old slice's claims standing as live assertions. Trigger phrases: '/supersede-slice', 'supersede slice NNN', 'mark slice obsolete', 'retire shipped slice', 'link supersession'."
user_invokable: true
argument-hint: <archived-slice-id>
---

# /supersede-slice — Mark a Shipped Slice Obsolete (SUP-1)

You are establishing a formal supersession link between a new (active) slice and an old (archived) slice whose design or claims have been contradicted by reality.

Per **SUP-1** (`methodology-changelog.md` v0.19.0).

## Where this fits

Optional maintenance skill. Most archived slices are historical artifacts and don't need supersession — `/reflect` already preserves their reflection.md as a frozen snapshot. Use `/supersede-slice` only when:

- A shipped slice's design.md / mission-brief.md continues to read as a live claim about current code (vault drift), AND
- A new slice in active development is fixing the issue, AND
- The link should be auditable (e.g., for compliance review or to feed `/critic-calibrate`)

For mid-iteration design corrections within an active slice (not yet archived), use the existing `/design-slice` deviation pattern instead — there's no archived slice to supersede.

## When NOT to use

- Adding a feature on top of a shipped slice: that's a normal new slice; no supersession needed.
- Fixing a typo in an archived reflection: edit the archived file directly; that's not supersession.
- Renaming or reorganizing archived slices: that's a different cleanup operation.

## Prerequisite check

- An archived slice must exist at `architecture/slices/archive/<archived-slice-id>/`
- That folder must contain a `reflection.md` (the shipped retrospective)
- An active slice (in `architecture/slices/<active-slice-id>/`) is typically the source of supersession; if no active slice yet, you can run `/supersede-slice` first and create the active slice next, but the bidirectional audit will fail until both ends are linked.

## Your task

### Step 1: Validate the target

Confirm the archived slice exists:

```bash
test -d architecture/slices/archive/<archived-slice-id>/
```

If not: STOP. Tell the user the archived slice id wasn't found and list available ones from `architecture/slices/archive/`.

Read the archived slice's `reflection.md` to see what's being superseded. Surface a one-line summary of its result + main lessons so the user has context before writing the supersession reason.

### Step 2: Gather the supersession reason

Ask the user:

> Why is `<archived-slice-id>` being superseded? (one paragraph: what reality contradicted, which active slice is replacing the work, when it was discovered)

Examples of good reasons:
- "Slice-008's claim that S3 sync upload is sufficient was retired by slice-014's load test which exceeded the 30s timeout. Async queue is now the path; slice-014 implements it."
- "Slice-005's auth middleware was inlined into routers in slice-019; the standalone middleware module no longer exists. Reflection still claims it does."

Examples of bad reasons:
- "It's old" — supersession is for design contradiction, not age
- "We refactored" — too generic; what specifically broke the original claim?
- "TBD" — surface specifics or don't supersede

### Step 3: Update the archived slice's reflection.md

Append a new section to `architecture/slices/archive/<archived-slice-id>/reflection.md`:

```markdown
## Supersession

**Superseded by**: <active-slice-id>
**Date**: <YYYY-MM-DD>
**Reason**: <user-provided reason from Step 2>
```

Do NOT modify any other content in the archived reflection.md — supersession is append-only history, like ADR supersession. The archived slice's other claims remain frozen; the section just marks them as no-longer-canonical.

### Step 4: Update the active slice's mission-brief.md

If an active slice exists (typical case), update its `mission-brief.md` frontmatter to add:

```markdown
**Supersedes**: <archived-slice-id>
```

This closes the bidirectional link the audit checks for.

If no active slice exists yet: tell the user to set this field when they next run `/slice` to define the replacement work.

### Step 5: Run the audit

Validate the bidirectional link is consistent:

```bash
$PY -m tools.supersede_audit --root .
```

Expected: 1 link validated (no violations). If the audit reports `one-way-link` or `missing-target`, the supersession is incomplete — fix the brief or reflection and re-run.

### Step 6: Update slices/_index.md

Update `architecture/slices/_index.md` to mark the archived slice as superseded in its row of the catalog table. Format:

```markdown
| <archived-slice-id> | <date> | <result> | superseded by [[<active-slice-id>]] |
```

This makes supersession discoverable from the index without needing to grep individual reflections.

### Step 7: Confirm and hand off

Tell the user:
- "Slice <archived-slice-id> superseded by <active-slice-id>."
- "reflection.md in archive updated; mission-brief.md frontmatter set; _index.md row updated; audit clean."
- "Run /critique on the active slice next, citing the supersession reason in design.md if it informs design choices."

## Critical rules

- DO NOT modify other content in the archived reflection.md. Supersession is append-only.
- DO NOT delete the archived slice. The folder remains in `slices/archive/` as historical record.
- VALIDATE the target id strictly (must match an existing folder under `slices/archive/`). A typo creates an orphan claim.
- BIDIRECTIONAL link is the rule, not just a convention. The audit refuses one-way links (active claims supersession but archive doesn't acknowledge, or vice versa).
- DO NOT use this skill for in-flight design corrections (slice not yet archived). Those are deviations recorded in build-log.md per `/build-slice` Step 7.

## Anti-patterns

- Superseding to "clean up" the archive: archived slices are reference, not clutter — they capture decisions made in their context. Don't treat them as garbage.
- Bulk supersession: each supersession should have a specific reason. If you want to supersede many slices at once, you probably want a different operation (a vault rewrite, perhaps).
- Superseding without a replacement: if no active slice fixes the issue, supersession is premature — capture the obsolescence in the risk register instead and supersede when the fix slice exists.

## How this differs from /reflect's auto-archive

`/reflect` Step 6 auto-archives a completed slice (moves the folder from `slices/` to `slices/archive/`). That's the normal happy-path closure for any slice — the slice shipped, retrospective is recorded, folder relocates.

`/supersede-slice` is the rare exceptional move when an ALREADY-archived slice's claims need explicit retirement because a NEW slice is reaching back to fix what the old one didn't get right.

## Next step

Continue working on the active slice that supersedes the old one. The supersession link is now in place; the audit will keep both ends consistent on subsequent runs.
