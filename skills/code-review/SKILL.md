---
name: code-review
description: "AI SDLC pipeline. In-loop adversarial review of the just-written code (slice diff) by a separate code-Critic AI persona. Spawns a separate Agent with adversarial prompt, attacks the slice's code diff along the 9 fixed dimensions (assumptions, edge cases, over/under-engineering, contract gaps, security, drift, web-known issues, cross-cutting), produces blockers/majors/minors with `path/to/file.py:line` specificity. Use AFTER /build-slice, BEFORE /validate-slice. Walking-skeleton v1 — findings advisory only; AI-bloat passes deferred to slice-061 and TRI-1 triage gate + verdict-driven block deferred to slice-062. Trigger phrases: '/code-review', 'review the slice code', 'review the just-built code', 'adversarial code review', 'code review on the diff'. Mandatory in the canonical PCA-1 chain post-slice-060."
user_invokable: true
---

# /code-review — Adversarial Review of the Slice Diff by Code-Critic Persona

You are running the code-Critic-persona review of the current slice's CODE — the just-written diff vs the default branch. The code-Critic is a SEPARATE Agent (spawned via the Agent tool) with an adversarial prompt — its job is to attack the code, not approve it.

Per **CRSI-1** (`methodology-changelog.md` v0.64.0; slice-060; ADR-059).

## Where this fits

Runs after `/build-slice` (the slice's code + tests + build-log are written; pre-finish gate has passed). Output: `code-review.md` written into the active slice folder with findings; **advisory only in v1** — does NOT block `/validate-slice`. AI-bloat passes (multi-impls, half-wired modules, stale scaffolding, session-break inconsistency) are deferred to slice-061; TRI-1-style user triage gate + verdict-driven HALT-on-BLOCKED is deferred to slice-062.

The three-persona model (extended from `/critique` + `/critique-review`): design-Critic (`/critique`) reviews mission-brief + design.md + new ADRs BEFORE code is written; code-Critic (this skill) reviews the slice DIFF AFTER code is written. Same underlying model, different inputs, different output format. Cost: ~20% more tokens than a single Critic pass (per `/critique` figure). Catches code-level defects that the structural pre-finish audits (BC-1, PCA-1, BCI-1, MCFS-1, LINT-MOCK, WIRE-1, etc.) cannot reach — line-level idiom, accidental complexity, contract gaps inside `.py` functions, security issues in code paths, drift between the just-written code and the slice's own design.md.

## When to run

`/code-review` runs **automatically in-loop** as part of the canonical PCA-1 chain (post-slice-060): `/build-slice` → **`/code-review`** → `/validate-slice`. There is no risk-tier-based skip in v1 — every slice runs `/code-review` (vault-only slices auto-exit clean via empty-diff handling). Skip-via-flag is a slice-061+ extension if N≥3 vault-only slices accumulate.

`/code-review` is also manually user-invokable for ad-hoc review of a slice's code (e.g., re-running after addressing a finding).

## Prerequisite check

- Find the active slice folder (check `<vault>/slices/_index.md` "Currently active slice", else stat `<vault>/slices/slice-*/` for one stage-active `milestone.md`).
- Read `mission-brief.md`, `design.md`, and any new `ADR-NNN-*.md` files in this slice.
- Read `build-log.md` — if its frontmatter shows `Result: NOT-SHIPPED`: STOP with explicit message ("`/code-review` cannot review a slice that isn't built yet — run `/build-slice` first"). Do not auto-advance.
- If `mission-brief.md` is missing: STOP, tell user to run `/slice` first.
- If `design.md` is missing: STOP, tell user to run `/design-slice` first.

## Your task

### Step 1: Resolve the slice's code diff

Compute the slice's filtered code diff vs the default branch using the **union-of-three-sources** read mechanism (per [[ADR-062]], mirroring the slice-063 NAW-1 / [[ADR-061]] §Decision L60-67 pattern). The single-command `git diff "$base"...HEAD` is commit-vs-commit only (per [git-scm.com/docs/git-diff](https://git-scm.com/docs/git-diff) "`<commit>...<commit>` … starting at a common ancestor of both") and returns EMPTY at `/build-slice` Step 6 where slice work is uncommitted in the working tree — commits land only at `/commit-slice` per the PCA-1 HARD-STOP terminal contract. The union covers all three states slice code can occupy at Step 6:

```bash
default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
[ -z "$default" ] && { echo "default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved" >&2; exit 2; }
base=$(git merge-base "$default" HEAD)

# Source (i): working-tree-vs-base (modified + staged-but-uncommitted adds)
git diff "$base" --name-only --diff-filter=ACMR -- \
  ':(exclude)docs/**' \
  ':(exclude)architecture/decisions/**' \
  ':(glob,exclude)architecture/*.md' \
  ':(exclude)architecture/slices/_index.md' \
  ':(exclude)architecture/slices/archive/**' \
  ':(exclude)architecture/slices/*/milestone.md' \
  ':(exclude)architecture/slices/*/mission-brief.md' \
  ':(exclude)architecture/slices/*/design.md' \
  ':(exclude)architecture/slices/*/critique.md' \
  ':(exclude)architecture/slices/*/critique-review.md' \
  ':(exclude)architecture/slices/*/code-review.md'

# Source (ii): untracked-new files
git ls-files --others --exclude-standard -- \
  ':(exclude)docs/**' \
  ':(exclude)architecture/decisions/**' \
  ':(glob,exclude)architecture/*.md' \
  ':(exclude)architecture/slices/_index.md' \
  ':(exclude)architecture/slices/archive/**' \
  ':(exclude)architecture/slices/*/milestone.md' \
  ':(exclude)architecture/slices/*/mission-brief.md' \
  ':(exclude)architecture/slices/*/design.md' \
  ':(exclude)architecture/slices/*/critique.md' \
  ':(exclude)architecture/slices/*/critique-review.md' \
  ':(exclude)architecture/slices/*/code-review.md'

# Source (iii): commits-vs-base (already-committed-in-branch adds)
git diff "$base"...HEAD --name-only --diff-filter=ACMR -- \
  ':(exclude)docs/**' \
  ':(exclude)architecture/decisions/**' \
  ':(glob,exclude)architecture/*.md' \
  ':(exclude)architecture/slices/_index.md' \
  ':(exclude)architecture/slices/archive/**' \
  ':(exclude)architecture/slices/*/milestone.md' \
  ':(exclude)architecture/slices/*/mission-brief.md' \
  ':(exclude)architecture/slices/*/design.md' \
  ':(exclude)architecture/slices/*/critique.md' \
  ':(exclude)architecture/slices/*/critique-review.md' \
  ':(exclude)architecture/slices/*/code-review.md'
```

**Union the three outputs by path; deduplicate. The resulting file list is the in-scope diff scope handed to Step 2.** Without this aggregation step Claude could plausibly run only Source (iii) for token budget, concatenate without deduplicating producing duplicate review work, intersect instead of union, or ignore Source (ii) — all silent failures.

Default-branch resolution mirrors the BRANCH-1 pattern (slice-021). `--diff-filter=ACMR` includes Added/Copied/Modified/Renamed; deletions excluded. The path-exclude pathspecs are inline literals on each leg (POSIX-portable; no bash arrays). Per slice-069 / [[ADR-066]] M5 INCLUDE direction, the pre-slice-069 catch-all `':(exclude)architecture/**'` is replaced by 10 surgical exclusions per leg — admitting `architecture/slices/*/{build-log,validation,reflection}.md` (post-build artifacts) into /code-review scope while continuing to exclude ADRs (reviewed by /critique), top-level vault docs (reviewed by /reflect / /risk-spike / /slice on own surfaces), the slice index + archive, and the slice's own non-post-build files (mission-brief / design / critique / critique-review / milestone / code-review.md self-referential).

**In-scope paths** (per design.md M3 — METHODOLOGY-PROSE-AS-EXECUTABLE-CONTRACT is in scope; CLAUDE.md self-hosting-discipline: "skill prose IS executable contract"):
- `skills/**/SKILL.md` — methodology orchestrator prose (executable contract)
- `agents/*.md` — agent prompts (executable contract)
- `tools/**/*.py` — audit + lint Python modules
- `tests/**/*.py` — test modules
- Root-level config files — `plugin.yaml`, `pyproject.toml`, `VERSION`, `methodology-changelog.md`
- `<vault>/slices/*/build-log.md` + `validation.md` + `reflection.md` (post-slice-069 / [[ADR-066]] M5 INCLUDE direction — these post-build artifacts are tracked production content landing in every PR diff; entering /code-review scope rather than relying on the dual-Critic stack which structurally only reads design.md / ADRs at /critique time)

**Out-of-scope paths** — pruned via inline `:(exclude)` pathspecs on each of the three union legs (per [[ADR-066]] / slice-069 M5 INCLUDE direction; rationale per excluded class):
- `docs/**` — pure documentation if any
- `<vault>/decisions/**` — ADRs are reviewed by `/critique` (design-Critic) at /critique time
- `:(glob)architecture/*.md` — top-level vault docs (risk-register, lessons-learned, build-checks, shippability, slice-queue, concept, triage, principles, pipeline, tutorial) — reviewed by `/reflect` / `/risk-spike` / `/slice` on their own surfaces. **MUST use `:(glob)` pathspec magic** — without it, git's default fnmatch (no `FNM_PATHNAME` flag) makes `*` match across `/` segments and `architecture/*.md` would recursively re-exclude all `.md` files under `architecture/` (including the post-build artifacts M5 INCLUDE admits to scope). Slice-069 build-time discovery: the bare `architecture/*.md` pathspec silently re-excluded `architecture/slices/slice-069-track-vault-in-git/build-log.md` from the /code-review diff scope.
- `<vault>/slices/_index.md` — slice index, maintained by `/reflect`
- `<vault>/slices/archive/**` — archived slice content, frozen historical record
- `<vault>/slices/*/milestone.md` + `mission-brief.md` + `design.md` + `critique.md` + `critique-review.md` — slice non-post-build files (milestone is auto-generated; mission-brief / design / critique / critique-review reviewed by the design-Critic stack at /critique time)
- `<vault>/slices/*/code-review.md` — /code-review's own output, self-referentially excluded

**Error cases**:
- `default-branch-unresolvable` (neither `git symbolic-ref` nor `git config init.defaultBranch` resolves): STOP with the BRANCH-1-shaped error and instruct user to re-run after default branch resolves.
- `no-code-changes` (filtered diff is empty): write a minimal `code-review.md` with `Result: NO-CODE-CHANGES — nothing to review` and exit clean (auto-advance to `/validate-slice` proceeds). This is the operational footgun gate per must-not-defer #3 — a vault-only slice (e.g., a methodology-changelog-only entry) must not crash the in-loop review.

### Step 2: Spawn the code-Critic agent

Use the Agent tool with **`subagent_type: "code-review"`**. This is a named subagent at `~/.claude/agents/code-review.md` that carries the full adversarial code-Critic system prompt — stance, 9 dimensions reframed for CODE, specificity/honesty rules, output format. You don't repeat that here.

Your job in this step is just to **hand the agent the inputs**. The prompt body should contain:

```
Slice: slice-NNN-<name>
Mode: <Minimal | Standard | Heavy from triage.md>
Risk tier: <low | medium | high from milestone.md>

# mission-brief.md
<paste full contents>

# design.md
<paste full contents>

# New ADRs
<paste contents of each ADR-NNN-*.md created by this slice>

# Changed files (code diff scope)
<the unioned + deduplicated file list emitted by Step 1 — one path per line; vault paths excluded per Step 1 in-scope list>

# Diff content
<for each file in Step 1's union, paste `git diff "$base" -- <file>` output (WT-vs-base per-file — observes uncommitted edits consistently with Step 1's union); size-limited per Claude Code prompt budget — if diff exceeds budget, list paths and let agent Read individual files (the slice-064 wide-slice load-edge-case watch-list per design.md R-X3)>
```

Return the agent's complete `code-review.md` content. Do not re-prompt for dimensions — the agent already knows them.

**If the agent returns "no blockers, no majors"**: that's a valid result. Do not push back. Trust the calibration loop in `/reflect` to surface false negatives over time. Compare with the design-Critic at `/critique` whose own "no findings" result is similarly a valid signal.

**If the agent's findings look generic** ("consider error handling" without a `path/to/file.py:line` ref): the code-Critic prompt has degraded. Request a re-run with: "Findings must reference specific `path/to/file.py:line` — re-attack with specificity."

**Error cases**:
- `agent-unspawnable` (Agent tool raises on `subagent_type: "code-review"`): exit 1 with explicit error; do NOT auto-advance.
- `agent-empty-output` (agent returns zero-length output): write `code-review.md` with `Result: AGENT-EMPTY — re-run with verbosity`; exit 1; do NOT auto-advance. This catches the rubber-stamp footgun from `/critique`'s failure-mode-to-watch list.
- `agent-malformed-output` (agent returns text but required sections — Blockers/Majors/Minors/Dimensions checked — are missing): write the raw output verbatim into `code-review.md`; surface a warning to the user; auto-advance proceeds (advisory mode; slice-061 hardens this).

**Await the real agent — never fabricate its output.**

- The `Agent` tool may return an **asynchronous acknowledgment** ("Async agent launched…"), NOT the finished review.
- That acknowledgment is **NOT** the deliverable.
- STOP and wait for the `task-notification`; write `code-review.md` ONLY from the agent's **actual returned content**.
- NEVER self-author a placeholder, and never write the file from your own main-thread reasoning, while the agent runs — doing so silently defeats the Builder↔code-Critic separation this skill exists to provide (the R-25 failure mode observed live in slice-085).

### Step 3: Receive code-Critic findings and write `code-review.md`

Take the agent's output and write it to `<vault>/slices/slice-NNN-<name>/code-review.md` using the template below. v1 has NO `## Triage` section (slice-062 owns the TRI-1 extension); findings are advisory.

### Step 4: Update milestone.md

Update `<vault>/slices/slice-NNN-<name>/milestone.md`:

- Frontmatter: `stage: code-review`, `updated: <today>`, `next-action: run /validate-slice`
- Check progress box: `- [x] /code-review — <date> — <FINDINGS-COUNT findings | NO-CODE-CHANGES | AGENT-EMPTY | AGENT-MALFORMED>`
- Update phase artifact status: `code-review.md — <result>`
- "Current focus" section: code-review result summary (blocker count, major count, minor count, OR no-code-changes / agent-empty / agent-malformed status)
- "On resume": next step = /validate-slice

### Step 5: Write `code-review.md`

```markdown
# Code Review: Slice NNN <name>

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: <YYYY-MM-DD>
**Result**: NO-CODE-CHANGES | FINDINGS | AGENT-EMPTY | AGENT-MALFORMED

## Summary
<1-2 sentences; or "no code changes in scope — nothing to review" on empty diff>

## Changed files (in-scope)
<one path per line>

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

#### B1: <short title>
- **Claim under review**: <quote from code; cite path/to/file.py:line>
- **Issue**: <what's wrong>
- **Evidence**: <code excerpt + reference to design.md / mission-brief / ADRs if drift>
- **Proposed fix**: <concrete code change>

#### B2: ...

### Majors

(same structure)

### Minors

(same structure)

## Dimensions checked
- [x] Unfounded assumptions — <findings or "none">
- [x] Missing edge cases — <findings or "none">
- [x] Over-engineering — <findings or "none">
- [x] Under-engineering — <findings or "none">
- [x] Contract gaps — <findings or "none">
- [x] Security — <findings or "none">
- [x] Drift from vault — <findings or "none">
- [x] Web-known issues — <findings or "none" or "Skipped — WebSearch unavailable">
- [x] Cross-cutting conformance — <findings or "none">
```

## Critical rules

- USE THE Agent TOOL with `subagent_type: "code-review"` for the code-Critic. Don't fake it by self-reviewing in the main thread — that defeats the two-persona separation.
- DON'T re-state the adversarial stance or 9 dimensions in the prompt body — those live in the agent file (`~/.claude/agents/code-review.md`). Skill prompt is just inputs.
- DO NOT soften code-Critic findings. If the code-Critic is wrong, dispute with rationale; don't water down severity.
- DO NOT block `/validate-slice` in v1 — findings are advisory only (TRI-1 + verdict-driven block deferred to slice-062). Always auto-advance unless an error class (agent-unspawnable / agent-empty-output) fires.
- TRACK code-Critic accuracy in `/reflect` (the calibration section). Once N≥10 slices of operation accumulate, `/critic-calibrate` v2 extends to track code-review accuracy patterns.

## Failure mode to watch

code-Critic becomes a rubber stamp if its prompt is too mild or the diff is too small. Warning signs:
- "No issues found" on 3+ slices in a row (statistically unlikely on real code diffs)
- Findings always tagged "minor"
- Findings generic ("consider error handling") rather than specific (`path/to/file.py:NN`)

If you spot this: rerun with a more pointed prompt, or escalate to user about code-Critic effectiveness.

## The agent vs the skill — separation of concerns

- **Agent** (`~/.claude/agents/code-review.md`): carries the adversarial code-Critic prompt — role, stance, 9 dimensions reframed for CODE with examples, specificity/honesty rules, output format. Read-only tools (`Read, Glob, Grep, Bash, WebSearch`). The prompt itself is load-bearing; treat it like compiled code, not a comment.
- **Skill** (this file): orchestrates — resolves the slice diff, gathers inputs, invokes the agent, writes the result to `code-review.md`, updates `milestone.md`, auto-advances to `/validate-slice`. The skill is glue; the agent is the work.

If the agent prompt needs tuning, edit the agent file, not this skill. The skill should rarely need changes once stable (same META-3 discipline as `/critique` + `/critique-review` + `/critic-calibrate`).

## Next step

`/validate-slice` — real-environment validation of the slice's acceptance criteria + shippability catalog regression check.

## Pipeline position

- **predecessor**: `/build-slice`
- **successor**: `/validate-slice`
- **auto-advance**: true
- **on-clean-completion**: once `code-review.md` is written (including the `NO-CODE-CHANGES` / `AGENT-MALFORMED` advisory paths), invoke `/validate-slice` via the Skill tool without waiting for the user.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - None in v1 — findings are advisory only. slice-062 will add a TRI-1 verdict-driven HALT-on-BLOCKED gate. The `agent-unspawnable` and `agent-empty-output` error classes are exit-1 conditions (HALT for user) but NOT user-input-gates in the PCA-1 sense — they are infrastructure failures the user must repair before re-invoking, not deliberate methodology halts.

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. Manual invocation remains supported.
