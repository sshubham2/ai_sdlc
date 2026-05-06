---
name: commit-slice
description: "Generate an audit-grade commit message from a just-completed slice's vault artifacts. Pulls subject/body/refs from mission-brief.md, build-log.md, validation.md, and new ADRs. Produces conventional-commit-style output with slice folder reference, ADR IDs, AC count, Critic blockers addressed, and shippability entry — no hand-crafting required. Run right before committing code (after /reflect, which auto-archives the slice). Trigger phrases: '/commit-slice', 'generate commit message', 'audit commit', 'slice commit message'."
user_invokable: true
argument-hint: [--do-commit]
---

# /commit-slice — Audit-Grade Commit from Vault

You generate a commit message for the just-completed slice, pulling structured content from the slice's vault artifacts. No hand-crafting. No "wip" commits. Every slice gets a clean, consistent, audit-ready commit.

## Where this fits

Runs after `/reflect` (which auto-archives the slice). The slice folder is now at `architecture/slices/archive/slice-NNN-<name>/`.

Also useful mid-slice: `/commit-slice` can generate intermediate commits using the partial state (build-log so far + ACs passed so far), but those are optional; most value is at slice completion.

Heavy mode benefits most — compliance trails want consistent commit format referencing slices + ADRs.

## Argument modes

- `/commit-slice` — generate the message, show it to user, user copies to `git commit -m`
- `/commit-slice --do-commit` — generate + run `git add` + `git commit` with the message

Default: generate only. `--do-commit` requires user confirmation before executing git commands.

## Prerequisite check

- Most recently archived slice folder exists (`architecture/slices/archive/slice-NNN-*/`)
- That folder has `reflection.md` (slice completed)
- OR an active slice exists with `build-log.md` (for mid-slice commits)

If no slice artifacts found: stop. Tell user to run `/reflect` first (or if mid-slice: no data yet).

## Your task

### Step 1: Identify the target slice

Default: most recently archived slice (highest slice number in `slices/archive/`).

If `--do-commit` and multiple uncommitted slices exist: ask user which to commit (or commit them in order, one per commit).

### Step 2: Read vault artifacts

From the target slice folder, read:

- `mission-brief.md` → intent (first paragraph), acceptance criteria (count)
- `critique.md` (if exists) → blocker count + "addressed" status
- `build-log.md` → files changed, deferrals (if any)
- `validation.md` → per-AC PASS/FAIL, shippability regression status
- `reflection.md` → "Validated" items, any design corrections

Also read:
- New ADRs that reference this slice (`grep -l "slice: slice-NNN" architecture/decisions/`)
- Relevant shippability.md entry (added by this slice)

### Step 3: Classify the slice type

Pick the conventional commit type from mission brief intent:

- "add X" → `feat`
- "fix X" → `fix`
- "refactor X" / "reduce X" → `refactor`
- "improve X" / performance → `perf`
- "update tests" / "add tests" → `test`
- "migrate X" → `chore` (or `feat` if user-facing)
- "update docs" → `docs`

If ambiguous: `feat` is the default.

Scope: derived from slice name area (e.g., `slice-023-add-receipt-ocr` → scope `receipt`).

### Step 4: Generate the commit message via Haiku dispatch

Per **COST-1** (cost-optimized model selection — `methodology-changelog.md` v0.4.0), this step is template-filling and dispatches to a Haiku subagent rather than running on the main thread's model.

**Dispatch:**
- Use the Agent tool with `subagent_type: "general-purpose"` and `model: haiku`.
- Hand the agent a structured input dict gathered in Step 2: `{type, scope, slice_id, slice_path, intent_one_line, body_2_3_sentences, ac_pass, ac_total, critic_blockers, adrs, shippability_entry_n, shippability_entry_text, deferrals, regressions, mode, do_commit_flag}`.
- Hand the agent the template + example below as the spec it fills.
- The agent returns the commit message string. Main thread either presents it (default) or runs `git add` + `git commit -m` (Step 5 with `--do-commit`).

The main thread does not generate the message text — Haiku does. The main thread is responsible for input gathering (Step 2) and execution (Step 5).

**Why Haiku**: this is structured-data → template rendering. The cognitive demand is filling slots from the input dict, not synthesis or reasoning. Haiku is faster and cheaper for this; quality is unchanged because no judgment is required.

**Format** (the dispatched agent fills this):

```
<type>(<scope>): slice-NNN — <one-line intent from mission brief>

<body paragraph: what was built / changed, in 2-3 sentences>

Slice: [slice-NNN-<name>](architecture/slices/archive/slice-NNN-<name>/)
Acceptance criteria: <X>/<Y> PASS (see validation.md)
Critic blockers addressed: <list or "none">
ADRs: <ADR-NNN, ADR-MMM> (or "none")
Shippability entry: #<N> — <one-line>
<if deferrals: "Deferred: <summary> (see reflection.md)">
<if regressions caught: "Regression caught: <summary>">
```

Example output:

```
feat(receipt): slice-023 — HEIC/PNG/JPEG receipt upload with thumbnail

Adds POST /transactions/:id/receipt accepting images up to 10MB
with authorization restricted to transaction owner. Generates
200x200 WebP thumbnails via Pillow + pyheif (for HEIC).

Slice: architecture/slices/archive/slice-023-add-receipt-upload/
Acceptance criteria: 5/5 PASS (see validation.md)
Critic blockers addressed: B1 (authz check), B2 (MIME validation strategy)
ADRs: ADR-008 (object-storage-thumbnails)
Shippability entry: #15 — POST /receipts HEIC with correct EXIF preserved
Deferred: re-invitation cancellation flow (→ slice-024 candidate)
```

For Heavy mode: add extra lines for compliance:

```
Reviewer sign-offs: <from critique.md + validation.md>
Compliance: <applicable frameworks from non-functional.md>
```

### Step 5: Present or execute

**Default (no `--do-commit`)**: Show the message to user with instruction:

```
Copy this to your commit command:

git commit -m "$(cat <<'EOF'
<full message>
EOF
)"
```

Note: HEREDOC format to preserve newlines and special characters.

**With `--do-commit`**: 
1. Show the message
2. Show which files will be staged (git status before commit)
3. Ask: "Confirm commit? (yes/no)"
4. On yes: `git add` the relevant files (source code touched in this slice — from build-log.md's "Files changed" section), then `git commit` with the message
5. Show `git log -1` to confirm

Do NOT push. Push is a separate action with its own confirmation flow.

### Step 6: Handle edge cases

- **Slice has deferrals**: note them in commit body; they're part of the audit trail
- **Shippability regression caught**: if /validate-slice caught + fixed a regression during this slice, note it in the body ("Caught and fixed regression in slice-018's sync test")
- **No new ADRs**: state "ADRs: none" — don't omit the line (audit expects consistent format)
- **Critic APPROVED with no fixes**: "Critic blockers addressed: none (design passed review)"

## Critical rules

- NEVER fabricate content. Every field comes from an actual vault file.
- If a field is missing (e.g., no critique.md in Minimal mode): say "Critic: skipped (Minimal mode)" not omit.
- With `--do-commit`: always show the message + staged files BEFORE committing. Wait for explicit "yes."
- NEVER `--no-verify`. Pre-commit hooks (like `/drift-check`) exist for a reason; don't bypass.
- NEVER push. Push requires user decision.
- CONSISTENT FORMAT. Every slice's commit looks the same shape. Audit tools scan for these patterns.

## For Minimal mode

Slices in Minimal often skip /critique. Commit message adapts:

```
feat(scan): slice-001 — folder scan with duplicate CSV report

Walks directory, computes perceptual hash via imagehash, groups by distance.
Emits CSV with cluster_id, file_path, hash.

Slice: architecture/slices/archive/slice-001-scan-folder-emit-csv/
Acceptance criteria: 5/5 PASS
Critic: skipped (Minimal mode)
ADRs: ADR-001 (phash-library)
Shippability entry: #1 — scan-folder produces expected CSV for 50-file test set
```

## For brownfield / bug-fix slices

When the slice was preceded by `/repro`: note the reproduction in the body.

```
fix(receipt): slice-024 — HEIC >5MB upload no longer times out

Reproduction established in /repro (failing test in tests/bugs/). Fix:
switch from sync S3 PUT to multipart upload for files >5MB; bump timeout
to 60s. Reproduction test now passes.

Slice: architecture/slices/archive/slice-024-fix-heic-timeout/
Acceptance criteria: 3/3 PASS
Critic blockers addressed: B1 (progress feedback to client during multipart)
ADRs: ADR-014 (multipart-upload-threshold)
Shippability entry: #23 — POST /receipts HEIC >5MB returns 201 within 10s
Reproduction test added: tests/bugs/test_receipt_upload_heic_timeout.py
```

## Anti-patterns

- **Hand-editing the generated message**: if something feels off, fix the underlying vault file (mission-brief, reflection) — the message is a view; inconsistency means the vault is inconsistent.
- **Amending past commits with updated messages**: don't. The commit is a snapshot of what was true at commit time.
- **Multiple slices per commit**: one slice per commit. If two are ready: two commits.

## Next step

- Message shown → user commits (or skill commits with `--do-commit`)
- After commit: next slice begins via `/slice` (or `/status` to re-orient)
