---
name: commit-slice
description: "Generate an audit-grade commit message from a just-completed slice's vault artifacts. Pulls subject/body/refs from mission-brief.md, build-log.md, validation.md, and new ADRs. Produces conventional-commit-style output with slice folder reference, ADR IDs, AC count, Critic blockers addressed, and shippability entry — no hand-crafting required. Run right before committing code (after /reflect, which auto-archives the slice). Three mutually-exclusive mode flags (per ADR-020): with --merge (BRANCH-1 sub-mode (b) — local-merge into default + safe-delete; solo-dev / no-protected-branch path); with --push (push slice branch to origin + display PR-creation URL hint; PR-based workflow path); with --sync-after-pr (post-PR-merge local cleanup via two-signal merged-state detection + safe-delete; post-PR-merge cleanup path). No-flag invocation preserves slice-021 generate-only default. Trigger phrases: '/commit-slice', 'generate commit message', 'audit commit', 'slice commit message', '/commit-slice --merge', '/commit-slice --push', '/commit-slice --sync-after-pr'."
user_invokable: true
argument-hint: [--merge | --push | --sync-after-pr]
---

# /commit-slice — Audit-Grade Commit from Vault

You generate a commit message for the just-completed slice, pulling structured content from the slice's vault artifacts. No hand-crafting. No "wip" commits. Every slice gets a clean, consistent, audit-ready commit.

## Where this fits

Runs after `/reflect` (which auto-archives the slice). The slice folder is now at `<vault>/slices/archive/slice-NNN-<name>/`.

Also useful mid-slice: `/commit-slice` can generate intermediate commits using the partial state (build-log so far + ACs passed so far), but those are optional; most value is at slice completion.

Heavy mode benefits most — compliance trails want consistent commit format referencing slices + ADRs.

## Argument modes

- `/commit-slice` — generate the message, show it to user, user copies to `git commit -m` (no-flag default; slice-021 generate-only behavior preserved per ADR-020)
- `/commit-slice --merge` — generate + run `git add` + `git commit` on the current slice branch + no-ff merge into default branch + safe-delete the slice branch (per **BRANCH-1** sub-mode (b))
- `/commit-slice --push` — generate + run `git add` + `git commit` on the current slice branch + `git push -u origin slice/NNN-<name>` + display PR-creation URL hint (per **ADR-020**; PR-based workflow path; never merges locally, never deletes)
- `/commit-slice --sync-after-pr` — post-PR-merge local cleanup (no commit; skips Steps 1-4): two-signal merged-state detection then safe `git checkout <default> + git pull --ff-only + git branch -d slice/NNN-<name>` (per **ADR-020**; post-PR-merge cleanup workflow)

The 3 mode flags are **mutually exclusive** — passing two or more → STOP with "Mode flags `--merge`, `--push`, `--sync-after-pr` are mutually exclusive; pass exactly one (or none for the slice-021 generate-only default)."

Default: generate only. Mode flags require user confirmation at multiple checkpoints before executing git commands; see Step 5 for the per-mode flows.

## When to use which mode

Pick the mode that matches your repo's contribution workflow:

- **`--merge`** — **solo-dev / no-protected-branch path**. Use when you have direct push access to the default branch AND there's no required-PR / required-review / CI-gate policy. The fastest path: local merge + safe-delete the slice branch in one skill invocation. Don't use if your team has protected branches or required PR review — your local merge will fail at `git push` (or worse, succeed locally and diverge from origin's required-review-gated state).

- **`--push`** — **PR-based workflow path**. Use when the default branch is protected OR your team requires PR review OR CI must evaluate the slice branch in isolation. The skill pushes the slice branch to `origin/slice/NNN-<name>` and displays a `gh pr create` command + (for GitHub.com remotes) a raw compare URL. You open the PR (manually or via the displayed `gh` command), reviewers approve, the PR merges on GitHub, the origin branch is auto-deleted. Local cleanup happens later via `--sync-after-pr`.

- **`--sync-after-pr`** — **post-PR-merge local cleanup path**. Use AFTER your PR (opened post-`--push`) has been merged AND the origin slice branch has been auto-deleted. The skill detects the merged state via two independent signals (remote-branch absence via `git ls-remote` + commit-reachability on `origin/<default>` via `git cherry` Pass 1 + aggregate-tree-diff Pass 2 fallback for multi-commit GitHub squash-merge) and, on confirmation, runs `git checkout <default> + git pull --ff-only + git branch -d slice/NNN-<name>`. STOPs with diagnostic if either signal disagrees.

Per **ADR-020** the 3 modes are mutually exclusive; the no-flag default (generate only, no git operations) remains the slice-021 behavior unchanged.

## Prerequisite check

- Most recently archived slice folder exists (`<vault>/slices/archive/slice-NNN-*/`)
- That folder has `reflection.md` (slice completed)
- OR an active slice exists with `build-log.md` (for mid-slice commits)

If no slice artifacts found: stop. Tell user to run `/reflect` first (or if mid-slice: no data yet).

## Your task

### Step 1: Identify the target slice

Default: most recently archived slice (highest slice number in `slices/archive/`).

If `--merge` and multiple uncommitted slices exist: ask user which to commit (or commit them in order, one per commit).

### Step 2: Read vault artifacts

From the target slice folder, read:

- `mission-brief.md` → intent (first paragraph), acceptance criteria (count)
- `critique.md` (if exists) → blocker count + "addressed" status
- `build-log.md` → files changed, deferrals (if any)
- `validation.md` → per-AC PASS/FAIL, shippability regression status
- `reflection.md` → "Validated" items, any design corrections

Also read:
- New ADRs that reference this slice (`grep -l "slice: slice-NNN" <vault>/decisions/`)
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
- The agent returns the commit message string. Main thread either presents it (default) or runs the 5-step merge flow (Step 5 with `--merge`).

The main thread does not generate the message text — Haiku does. The main thread is responsible for input gathering (Step 2) and execution (Step 5).

**Why Haiku**: this is structured-data → template rendering. The cognitive demand is filling slots from the input dict, not synthesis or reasoning. Haiku is faster and cheaper for this; quality is unchanged because no judgment is required.

**Format** (the dispatched agent fills this):

```
<type>(<scope>): slice-NNN — <one-line intent from mission brief>

<body paragraph: what was built / changed, in 2-3 sentences>

Slice: [slice-NNN-<name>](<vault>/slices/archive/slice-NNN-<name>/)
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

Slice: <vault>/slices/archive/slice-023-add-receipt-upload/
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

The 3 mode flags are **mutually exclusive** (per ADR-020 + /critique B4 ACCEPTED-FIXED). If the user passes two or more, STOP with diagnostic: "Mode flags `--merge`, `--push`, `--sync-after-pr` are mutually exclusive; pass exactly one (or none for the slice-021 generate-only default)."

#### Step 5a: Default (no flag)

Show the message to user with instruction:

```
Copy this to your commit command:

git commit -m "$(cat <<'EOF'
<full message>
EOF
)"
```

Note: HEREDOC format to preserve newlines and special characters. The no-flag default preserves slice-021 generate-only behavior — no git operations are executed.

#### Step 5b: With `--merge` (per **BRANCH-1** sub-mode (b), `methodology-changelog.md` v0.35.0 — solo-dev / no-protected-branch path)

Per slice-022 AC #1 + ADR-020: the slice-021 `--merge` 5-step flow + 2 pre-flight guardrails are preserved verbatim. Behavior is unchanged; what's superseded is the implicit claim that `--merge` is the only post-/reflect cleanup path.

Pre-flight guardrails (run BEFORE any state change):
1. **Stale-slice-branch check** (parallel-aware per **ADR-081** / slice-089 — supersedes the slice-021 B5 flag-all heuristic: refuse ONLY on worktree-LESS orphan `slice/*` branches; a worktree-backed `slice/*` is a legitimate concurrent slice under PSQ-1 / PSQ-2 / BRANCH-2, NOT a stale artifact):
<!-- STALE-BRANCH-CHECK:BEGIN -->
   Run `python -m tools.stale_branch_classifier --repo-root . --json` at pre-flight — cwd is still the slice worktree, BEFORE any `cd` to the main tree (the ordering invariant: self-exclusion needs HEAD == the slice branch). Branch on the JSON `verdict`:
   - **`verdict: refuse`** (≥1 `orphan_branches` — worktree-less) → STOP. Print: "Stale slice branches detected (no live worktree): `<orphan_branches>`. For legitimate post-PR-merge stragglers, run `/commit-slice --sync-after-pr` on each. For other artefacts of prior unresolved conflicts, resolve manually (`git branch -d` each, after verifying merged) before retrying."
   - **`verdict: allow`** with non-empty `parallel_slices` → surface a one-line note "N parallel slice(s) in flight (worktree-backed, not stale): `<parallel_slices>`" (append the `noncanonical_backed` rename hint per ADR-063 when that list is non-empty) and PROCEED (no STOP).
   - **`verdict: allow`** with empty `parallel_slices` → proceed silently.
   - **Bootstrap / failure fallback** (`ModuleNotFoundError` / import failure / classifier exit ∈ {1, 2}): fall back to the legacy flag-all check — `git for-each-ref --format='%(refname:short)' refs/heads/slice/` minus the current branch (`git symbolic-ref --short HEAD`); STOP if any remain. Strictly no weaker than the pre-ADR-081 behavior. Surface the failure reason to the user (fail-visible, never a silent skip).
<!-- STALE-BRANCH-CHECK:END -->

(Per slice-075 closing P2.4: the pre-existing WT-clean preflight — which required an empty porcelain-status check BEFORE sub-step 2's commit — was lifted out of pre-flight to new sub-step 2.1. post-commit guardrail below. Pre-fix the WT-clean preflight contradicted sub-step 2's expectation that the slice work is uncommitted. The silent-WT-discard local-state-loss protection intent (per /critique M5 ACCEPTED-PENDING) is preserved at the new post-commit position.)

Then the 5-step merge flow:

1. Show the message + show which files will be staged (`git status` before commit) on the current slice branch.
2. Ask: "Confirm commit on `<current slice branch>`? (yes/no)" — on yes: `git add` the relevant files (source code touched in this slice — from build-log.md's "Files changed" section), then `git commit -m "..."` on the slice branch with the generated message.
2.1. **WT-clean check (post-commit guardrail)** (per slice-075 closing P2.4; lifted from pre-flight to here — pre-fix the WT-clean preflight required empty `git status --porcelain` BEFORE sub-step 2's commit could execute, contradicting sub-step 2's expectation that the slice work is uncommitted). `git status --porcelain` MUST return empty NOW (after sub-step 2's commit). If non-empty, STOP. Print: "WT non-empty after sub-step 2 commit. Unexpected un-committed files: `<list>`. Commit or discard before proceeding (preserves silent-WT-discard local-state-loss protection per /critique M5 ACCEPTED-PENDING — original intent: prevent silent local-state-loss when a downstream default-branch switch would silently carry stray un-committed files across branches)." **Vacuous on PSQ-3 re-entry** per [[ADR-068]] §Re-entry semantics: post-rebase-resolve re-invocation has sub-step 2 SKIP (nothing to commit, WT already clean post-conflict-resolve) → sub-step 2.1. passes trivially (WT was already clean before sub-step 2 SKIP) → sub-step 2.5 fast-forward no-ops → sub-step 3 proceeds.
2.5. **Rebase slice branch onto default** (per **PSQ-3**, `methodology-changelog.md` v0.72.0; [[ADR-068]] — mints rebase-and-conflict discipline on the parallel-slice family axis; sibling rule to PSQ-1 / PSQ-2 / BRANCH-2). Two parallel slice branches sequentially merged into the default branch produce silent merge conflicts at sub-step 3 (no-ff merge) without rebase-onto-default discipline — the second-to-merge slice discovers conflicts AT merge-time (all-at-once aggregate diff) rather than rebase-time (per-commit granular diff). PSQ-3 surfaces conflicts in the more diagnostic per-commit shape AND linearizes slice history before merge.

   Resolve default branch using the canonical 2-step pattern (identical to sub-step 3's pattern below — the rebase target MUST equal the merge target to avoid a footgun where they diverge): `default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')`; fallback `default=$(git config init.defaultBranch 2>/dev/null)`. STOP exit 2 if neither resolves (NAW-1 ADR-061 §Decision exit-2 contract verbiage: `default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved`).

   Then run `git rebase <default>` on the slice branch (the slice branch is the current worktree checkout per BRANCH-2). Per git-scm.com/docs/git-rebase: with no `<branch>` argument, `git rebase` does NOT switch branches — it replays the current branch's commits atop the target. Three outcome paths:
   - **Fast-forward no-op**: default has not advanced since the slice's branch-point (slice's branch-point IS default's tip); `git rebase` exits 0 without replay. Proceed to sub-step 3.
   - **Clean replay**: default has advanced past slice's branch-point but slice's commits replay cleanly atop the new default tip (the common second-to-merge case). Proceed to sub-step 3 (default checkout + no-ff merge).
   - **Conflict**: STOP. Do NOT proceed to sub-step 3 (default-checkout); do NOT delete worktree or branch. Print the conflicting file paths (extracted from `git status --porcelain` filtered to U-prefixed entries — `U` is the canonical git two-letter encoding for unmerged paths) + the `git rebase --abort` recovery hint.

     **PCR-1 + PCR-2a dispatch** (per **PCR-1**, `methodology-changelog.md` v0.73.0; [[ADR-069]] AND **PCR-2a**, `methodology-changelog.md` v0.74.0; [[ADR-071]] — mints parallel-conflict-resolution v1 + v2a vault-claim sub-mechanism on the family axis; sibling rules to PSQ-1 / PSQ-2 / PSQ-3 / BRANCH-2): invoke `python -m tools.parallel_conflict_resolver --resolve-soft --json` FIRST (before the structured-options ask block below) to attempt auto-resolution. The helper classifies the conflict per ADR-069's 5-class taxonomy (SOFT / VAULT_CLAIM / HARD / MIXED / UNKNOWN). For SOFT (all U-files in the 2-member SOFT file-set `{<vault>/slice-queue.md, <vault>/shippability.md}` AND no same-candidate-different-identity claim collision), the helper regenerates each file deterministically (slice-queue.md via textual claim-overlay on rebase-target stage `:3:` per /critique-review M-add-1 ACCEPTED-FIXED; shippability.md via row-union by slice number) + `git add` + `git rebase --continue`. **For VAULT_CLAIM** (sole U-file is slice-queue.md AND a single same-candidate-different-identity collision is present), per PCR-2a / ADR-071 the helper now auto-resolves via the strictly-newer `Claimed-at` timestamp-winner rule (loser's name suggested as a read-only audit-row replacement from the post-overlay in-memory queue text per M-add-2; defensive post-overlay verification per M-add-1 catches silent-drop) + `git add` + `git rebase --continue`. For HARD / MIXED, the helper returns a structured STOP diagnostic. Branch on the JSON output's `action` field + the resolver's exit code:

     - **`exit 0` + `action: APPLIED`** (SOFT auto-resolution succeeded OR `VAULT_CLAIM` auto-resolves via PCR-2a strict-newer Claimed-at + read-only loser-replacement — slice-queue.md merged deterministically + `git rebase --continue` already invoked by the resolver) → log a single-line breadcrumb to the slice's build-log.md Events section (`<YYYY-MM-DD HH:MM> PCR auto-resolved — see <vault>/parallel-conflict-resolution-log.md`) and proceed directly to sub-step 3 (SKIP the SOAD-1 STOP block below). The resolver has already staged the regenerated files + continued the rebase; no further skill action needed.
     - **`exit 0` + `action: STOP`** → first print the resolver's full-detail diagnostic from `python -m tools.parallel_conflict_resolver --diagnose --json` per U-file: (a) the concerned slices map (active slices whose `mission-brief.md` blast-radius includes the U-file path); (b) blast-radius for each concerned slice (the file paths the slice declares it touches); (c) claim history (PSQ-2 Claimed-by / Claimed-at lines parsed from BOTH branches' versions of slice-queue.md, surfacing same-candidate-different-identity collisions); (d) last-commit time per concerned slice via `git log -1 --format=%cI <slice-branch>` (the most recent commit on each concerned slice's branch, ISO-8601 UTC); (e) mission-brief link rendered as a markdown-relative path (`<vault>/slices/<slice-id>/mission-brief.md`) so the user can `Read` it directly. Then branch on the JSON `conflict_class`:
       - **`conflict_class` ∈ {`HARD`, `MIXED`}** (incl. a SOFT→HARD shippability escalation — keyed on the *returned class*, NOT on which internal path produced it, per [[ADR-075]] design §M2) → enter the **PCR-2b HARD/MIXED gate-on-hand-resolve flow** below (do NOT bare-fall-through to SOAD-1).
       - **`conflict_class` = `VAULT_CLAIM`** (corner cases — `claimed_at`-tie / multi-candidate collision / overlay silent-drop per ADR-071 Error model) → fall through to the existing SOAD-1 3-option block below for user-side disposition.
     - **`exit 1`** (UNKNOWN — resolver could not classify; rebase state unexpected — e.g., empty U-entries despite rebase-in-progress, both stages of a SOFT file missing, malformed parser input) → print the resolver's stderr diagnostic verbatim AND fall through to the SOAD-1 3-option block (APED-1 silent-disable / default-off-on-malformed criterion: NEVER silent-default to SOFT on UNKNOWN state).
     - **`exit 2`** (malformed inputs — invalid `--repo-root`, missing argparse args, etc.) → print resolver's stderr diagnostic verbatim AND fall through to SOAD-1.

     **PCR-2b HARD/MIXED gate-on-hand-resolve** (per **PCR-2b** + **TRI-RESOLVE-1**, `methodology-changelog.md` v0.77.0; [[ADR-075]] — mints two new rules; PCR-2b sibling to PCR-1 / PCR-2a on the parallel-conflict-resolution axis, TRI-RESOLVE-1 sibling to TRI-1): when `--resolve-soft --json` returns `action: STOP` with `conflict_class` ∈ {`HARD`, `MIXED`}, drive this gate instead of bare-falling-through to SOAD-1. Every leg is fail-closed — any failure STOPs with NO `git rebase --continue`:

       1. **Bootstrap guard**: if `python -m tools.parallel_conflict_resolver` is unavailable / fails to import (pre-PCR-2b install, broken module), SKIP the gate and fall through to the existing SOAD-1 3-option block below (the pre-PCR-2b bare STOP — strictly no weaker than today; per slice-067 / [[ADR-064]] bootstrap-defense precedent).
       2. **Diagnostic + `_index.md` hint**: the `--diagnose --json` output is already printed above. For an **`_index.md`-sole HARD conflict** (the high-frequency dominant HARD case per [[ADR-075]] §M4), additionally print the canonical hand-resolution hint: *"`<vault>/slices/_index.md` is regenerated by `/archive` (Haiku-dispatched, non-deterministic) — resolve by re-running `/archive` to regenerate the lessons-block, then `git add` it"* (ADR-069:72).
       3. **Hand-resolve**: the user — or Claude at the user's instruction — resolves the conflict markers in the working tree and `git add`s each resolved U-file.
       4. **Structural preflight**: run `python -m tools.parallel_conflict_resolver --verify-resolution --json`. Branch on the exit code FIRST, then `action` (per the slice-083 /code-review M1 fix — the `--verify-resolution` JSON emits `action: STOP` for BOTH a re-resolvable state AND an unreadable git state; only the exit code distinguishes them):
          - **`exit 1`** (`reason` starts `git-state-unreadable` — the rebase state itself is unreadable, not the resolution) → do NOT loop back to step 3; fall through to the SOAD-1 (a) abort/investigate block below (mirrors the `--resolve-soft` `exit 1` handling above — fail-closed on broken git state).
          - **`exit 0` + `action: STOP`** (`paths-still-unmerged` → not all U-files staged; `unresolved-markers-present` → a line-anchored `<<<<<<<`/`>>>>>>>` opener/closer or `|||||||` diff3 base-marker survives — keyed on the openers, NOT `=======`, so Markdown setext headings do NOT false-STOP per [[ADR-075]] §B2/M-add-1) → print the reason and return to step 3 (or offer Abort).
          - **`exit 0` + `action: CLEAN`** → proceed to step 5. Do NOT reach the Critic until verify is `CLEAN`.
       5. **`code-review` agent** (per [[ADR-075]] §M-add-2 — the `code-review` agent is diff-calibrated; the `/critique` + `/critique-review` agents are NOT and fail-stop on a missing slice `design.md`): spawn the Agent tool with `subagent_type: "code-review"`, handing it the resolved diff (`git diff --cached` of the U-file set), the `--diagnose --json` context, and both rebase stages (`git show :2:<path>` / `git show :3:<path>`). Prompt it to review the *merge resolution* for: lost-hunk / dropped-side, both-sides-intent preservation, semantic correctness, stray markers, and vault/ADR contradiction introduced by the resolution. Capture the verdict + findings INLINE — do NOT write a slice-folder `code-review.md`; do NOT run `triage_audit` / `critique_review_audit` (those are design-folder audits; TRI-RESOLVE-1 is the gate). Any **blocker** finding → verdict BLOCKED.
       6. **TRI-RESOLVE-1 user-triage gate** (per **TRI-RESOLVE-1** — structured-options via the `AskUserQuestion` tool, NEVER a free-text prompt; mirrors TRI-1): present the `code-review` verdict + findings + the resolved-diff summary, and offer exactly three options:
          - **Apply resolution (continue rebase)** — the ONLY continue path; offered ONLY when the `code-review` verdict carries no blocker (a blocking verdict greys/removes this option — the user may then only Re-resolve or Abort).
          - **Re-resolve (edit again)** — return to step 3.
          - **Abort rebase** — fall through to the SOAD-1 (a) `git rebase --abort` path below.
          **Fail-closed**: every non-`Apply` option AND any interrupt / no-selection / session-end maps to STOP-no-continue. The skill NEVER calls `git rebase --continue` except on an explicit `Apply` selection with a non-blocking verdict (two-condition apply — no default-accept). An abandoned gate leaves the rebase in-progress + WT untouched; re-invoking `/commit-slice --merge` re-enters cleanly at this sub-step per [[ADR-068]] §Re-entry semantics (the WT-clean guardrail at sub-step 2.1 + fast-forward no-op semantics).
       7. **On Apply**: run `python -m tools.parallel_conflict_resolver --record-hard-resolution --verdict "<code-review verdict>" --disposition apply --json` (best-effort audit append — a `## Hard-conflict resolution -` section; write failure logs to stderr but NEVER blocks), THEN `git rebase --continue`, log a build-log.md Events breadcrumb (`<YYYY-MM-DD HH:MM> PCR-2b HARD resolved + applied — see <vault>/parallel-conflict-resolution-log.md`), and proceed to sub-step 3. Order is load-bearing: `--record-hard-resolution` runs while still mid-rebase (U-files + concerned slices still visible to `--diagnose`), THEN `git rebase --continue`.

     PCR-1's SOFT-class auto-resolution is restricted to the 2-member SOFT file-set per ADR-069 § Decision: `<vault>/slices/_index.md` is **NOT** in SOFT because `/archive`'s regen is Haiku-LLM-dispatched per COST-1 (not deterministic — PCR-1 cannot reproduce Haiku's lessons-block synthesis); `methodology-changelog.md` is **NOT** in SOFT because PMI-1 5-leg atomic-bump risk on concurrent bumps means subtly inconsistent merged entries (different RULE-IDs, paired-pin test names, ADR refs). **PCR-2a (slice-078 / ADR-071) ships VAULT_CLAIM auto-resolution** via strict-newer `Claimed-at` timestamp-winner (the dominant case is now auto-resolved; the `claimed_at`-tie + multi-candidate-collision + overlay-silent-drop corner cases fall through to SOAD-1 STOP per ADR-071 Error model). **PCR-2b (slice-083 / [[ADR-075]]) ships HARD + MIXED resolution** via the gate-on-hand-resolve flow above (hand-resolve → `--verify-resolution` → `code-review` agent on the resolved diff → TRI-RESOLVE-1 user gate → `git rebase --continue`); HARD = any source / ADR / SKILL.md / _index.md / methodology-changelog.md U-file, MIXED = SOFT + non-SOFT coexist (atomicity — never partially auto-resolve). UNKNOWN (fail-closed) still routes through SOAD-1.

     Then surface a SOAD-1 structured-options ask (3-option decision tree — does NOT model as binary yes/no per [[ADR-050]] primary-form-of-ask scope; first SOAD-1 invocation in /commit-slice — the other 6 confirmation sites at L173/L175 + 4 other sites later in this file remain raw yes/no since they are binary confirmations):
     - **(a) Abort rebase + investigate** — print `Run \`git rebase --abort\` to restore the slice branch to its pre-rebase state, then investigate the conflict cause (e.g., recently-merged peer slice touched the same files). Re-invoke \`/commit-slice --merge\` after resolution.`
     - **(b) Resolve conflicts manually + run `git rebase --continue` outside the skill** — print `Resolve each U-entry file, \`git add\` the resolutions, run \`git rebase --continue\` outside this skill until rebase completes, then re-invoke \`/commit-slice --merge\` (WT-clean guardrail will pass; sub-step 2 detects no un-staged files and SKIPS the commit attempt; sub-step 2.5 fast-forward no-ops; flow proceeds normally per design.md §Re-entry semantics).`
     - **(c) Cancel slice merge entirely** — print `Run \`git rebase --abort\` to restore the slice branch. Skill exits cleanly leaving the worktree state unchanged. If you want to discard the slice branch entirely, run \`git branch -D slice/NNN-<name>\` manually OUTSIDE the skill — this skill NEVER force-deletes per Critical rules below.`

   **Non-conflict rebase failure** (e.g., detached HEAD, missing commits, broken HEAD reference): STOP exit non-zero with `git rebase --abort` hint + git's stderr printed verbatim. Exit without further state mutation.

   PSQ-3 NEVER auto-resolves rebase conflicts (no `-X theirs`, no `-X ours`, no merge driver) — preserves the existing /commit-slice "never auto-resolve, never bypass hooks, never force" Critical rules block.
3. **Switch to main tree, then resolve default and merge** (per slice-075 closing P1.2 BRANCH-2 worktree-vs-main-tree default-branch-checkout collision): under BRANCH-2 the worktree holds `slice/NNN-<name>` while the main tree holds the resolved default; a default-branch checkout from the worktree fails with `fatal: '<default>' is already checked out at '<main-tree-path>'`. First resolve the main tree path via `main_tree=$(git worktree list --porcelain | awk '/^worktree / {print $2; exit}')` (extracts first-listed worktree = main tree per the [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree) porcelain ordering invariant: "The main worktree is listed first, followed by each of the linked worktrees"; **SIBLING-BUT-DISTINCT idiom** from sub-step 5's specific-branch extraction `awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}'` — shared `/^worktree /` regex anchor with divergent AWK action because divergent semantics; per /critique m1 ACCEPTED-FIXED). If `main_tree` resolves empty (bare repo, worktree-list returns nothing, or worktree detached): STOP. Print: "main-tree-unresolvable: `git worktree list --porcelain` extraction returned empty — worktree may be detached or repo state corrupt. Resolve manually before retrying `/commit-slice --merge`." Otherwise `cd "$main_tree"` (cwd change harmless because subsequent sub-steps 5 worktree-remove + 6 branch-delete + 7 git-log all work correctly from main tree per [[ADR-063]] §Decision sub-step ordering — unchanged by slice-075). If `cd "$main_tree"` itself fails (path doesn't exist on disk — should be impossible if `git worktree list` returned it, but defensive): STOP with shell's stderr verbatim + actionable hint. Then resolve default branch (per **BRANCH-1** + /critique M1 ACCEPTED-PENDING — no hard-coded `master`/`main`): `default=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')`; fallback `default=$(git config init.defaultBranch)`. STOP if neither resolves. Then `git checkout $default` + `git merge --no-ff slice/NNN-<name> -m "Merge slice/NNN-<name>: <intent>"`. If conflict: STOP. Leave default-branch in conflicted state. Print: "Merge conflict at `<files>`. Resolve manually, then `git commit` to finalize the merge. Do NOT re-run `/commit-slice --merge` post-conflict — the slice branch will linger; cleanup is manual in v1 (recovery flow deferred to follow-on slice `add-merge-conflict-recovery-to-commit-slice-merge`)."
4. Ask explicit confirmation (per /critique M5 ACCEPTED-PENDING — closes unrecoverable-without-push local-state-loss path): "Confirm merge + delete? (yes/no)" — on no: ABORT skill cleanly, leave merged slice branch present for user inspection.
5. **Idempotent worktree-remove guard** (per **BRANCH-2** / [[ADR-063]] §Decision Step 5b sub-step 5 — covers slice-066 bootstrap + any future `WORKTREE=skip` slice): pre-flight check `git worktree list --porcelain | grep -E "^branch refs/heads/slice/NNN-<name>$"` (POSIX shell; on Windows invoke via Git for Windows' bundled MSYS bash — same dependency convention as elsewhere; slice-067+ may reshape to Python `subprocess.run(['git','worktree','list','--porcelain'])` parsing if recurrence emerges). If empty (no worktree exists for this slice — bootstrap window OR documented `WORKTREE=skip` slice): LOG `slice/NNN-<name> worktree absent — skip worktree-remove (BRANCH-1 bootstrap or WORKTREE=skip slice)` to build-log Events + skip to sub-step 6. Otherwise: resolve `wt_path=$(git worktree list --porcelain | awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}')` then `git worktree remove "$wt_path"`. Refuses if the worktree has uncommitted state (post-sub-step-2 commit it shouldn't). On refuse: STOP loud — print git's stderr verbatim + actionable hint "If you have uncommitted work in the worktree, commit it before retry; if you intentionally abandoned changes, `git worktree remove --force <wt-path>` is the manual escape (this skill never auto-forces)".
6. `git branch -d slice/NNN-<name>` (safe-delete, local only; NEVER `-D`; if `-d` refuses, STOP and print: "Safe-delete refused (branch has unmerged commits). Inspect with `git log <default>..slice/NNN-<name>`. Do NOT use `-D` without understanding what's being discarded."). **Order-load-bearing**: sub-step 5 worktree-remove MUST precede this sub-step — a branch checked out in a worktree CANNOT be safely deleted (git refuses with "branch 'slice/NNN-<name>' checked out at '<wt-path>'"); per [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree) + ADR-063 §Decision Step 5b sub-step 6 order pin.
7. Show `git log -1` + `git log --graph --oneline -5` to confirm merge commit + slice attribution preserved.

**Critical rules for `--merge`**:
- NEVER `git push`, NEVER `git push --force`, NEVER remote-delete (push is a separate user-driven action — use `--push` for PR-based workflows).
- NEVER `git branch -D` (force-delete) — safe-delete only.
- NEVER auto-resolve merge conflicts.
- NEVER `--no-verify` to bypass pre-commit hooks.

Do NOT push. Push is a separate action with its own confirmation flow (use `--push`).

#### Step 5c: With `--push` (per **ADR-020**, `methodology-changelog.md` v0.36.0 — PR-based workflow path)

`--push` commits on the current slice branch and pushes to `origin/slice/NNN-<name>` for downstream PR creation. Never merges locally, never deletes the slice branch, never touches the default branch.

Pre-flight guardrails (run BEFORE any state change):

1. **WT-clean check**: `git status --porcelain` MUST return empty. If non-empty, STOP. Print: "Uncommitted changes detected. Commit or stash before `--push`."
2. **Stale-slice-branch check** (parallel-aware per **ADR-081** / slice-089 — identical to the `--merge` Step 5b sub-step 1 check; refuse ONLY on worktree-LESS orphans, a worktree-backed `slice/*` is a legitimate concurrent slice):
<!-- STALE-BRANCH-CHECK:BEGIN -->
   Run `python -m tools.stale_branch_classifier --repo-root . --json` at pre-flight — cwd is still the slice worktree, BEFORE any `cd` to the main tree (the ordering invariant: self-exclusion needs HEAD == the slice branch). Branch on the JSON `verdict`:
   - **`verdict: refuse`** (≥1 `orphan_branches` — worktree-less) → STOP. Print: "Stale slice branches detected (no live worktree): `<orphan_branches>`. For legitimate post-PR-merge stragglers, run `/commit-slice --sync-after-pr` on each. For other artefacts of prior unresolved conflicts, resolve manually (`git branch -d` each, after verifying merged) before retrying."
   - **`verdict: allow`** with non-empty `parallel_slices` → surface a one-line note "N parallel slice(s) in flight (worktree-backed, not stale): `<parallel_slices>`" (append the `noncanonical_backed` rename hint per ADR-063 when that list is non-empty) and PROCEED (no STOP).
   - **`verdict: allow`** with empty `parallel_slices` → proceed silently.
   - **Bootstrap / failure fallback** (`ModuleNotFoundError` / import failure / classifier exit ∈ {1, 2}): fall back to the legacy flag-all check — `git for-each-ref --format='%(refname:short)' refs/heads/slice/` minus the current branch (`git symbolic-ref --short HEAD`); STOP if any remain. Strictly no weaker than the pre-ADR-081 behavior. Surface the failure reason to the user (fail-visible, never a silent skip).
<!-- STALE-BRANCH-CHECK:END -->
3. **Current-branch-is-slice-branch**: `git symbolic-ref --short HEAD` MUST start with `slice/`. Otherwise STOP. Print: "`--push` must be invoked from a `slice/*` branch; you are on `<current branch>`."
4. **Origin-remote presence**: `git remote get-url origin` MUST succeed. If it fails, STOP. Print: "No `origin` remote configured. `/commit-slice --push` requires an `origin` remote; configure it (`git remote add origin <url>`) before retrying. `--push` never falls back to alternate remotes silently."

Then the 5-step push flow:

1. Show the message + show which files will be staged (`git status` before commit) on the current slice branch.
2. Ask: "Confirm commit on `<current slice branch>`? (yes/no)" — on yes: `git add` the relevant files (source code touched in this slice — from build-log.md's "Files changed" section), then `git commit -m "..."` on the slice branch with the generated message.
3. Ask: "Confirm push to `origin/<current slice branch>`? (yes/no)" — on yes: `git push -u origin slice/NNN-<name>` (first-push semantics; sets upstream tracking). NEVER `--force`, NEVER `--force-with-lease`. Two error sub-paths (per /critique M4 ACCEPTED-FIXED):
   - **Non-ff push** (remote ref has diverged from local — typically rebase/amend after prior `--push`): STOP. Print: "Remote `origin/slice/NNN-<name>` has diverged from local. This typically means local history was rebased/amended after a prior push. Resolve manually (force-push intentionally via `git push --force-with-lease origin slice/NNN-<name>` if you confirm the rebase was correct, or `git pull --rebase` if remote has new commits). `/commit-slice --push` never force-pushes."
   - **Fast-forward re-push** (remote ref exists and local is ahead by N commits): ASK explicit confirmation: "Remote ref `origin/slice/NNN-<name>` already exists and local is ahead by N commits. Confirm fast-forward re-push? (yes/no)" — on no: ABORT cleanly.
4. On push success: display the PR-creation hint block.
   - **GitHub.com origin remote** (URL matches `git@github.com:OWNER/REPO`, `https://github.com/OWNER/REPO[.git]`, or `ssh://git@github.com/OWNER/REPO`): display BOTH:
     - `gh pr create --base <default> --head slice/NNN-<name> --web` (command form — works for any `gh`-supported host including GitHub Enterprise via `gh` config)
     - `https://github.com/OWNER/REPO/compare/<default>...slice/NNN-<name>` (raw browser-openable compare URL)
   - **Non-GitHub.com remotes** (GitLab, Bitbucket, GitHub Enterprise custom-host — Enterprise URL derivation deferred per ADR-020 to follow-on slice `add-github-enterprise-url-derivation`): display ONLY `gh pr create --base <default> --head slice/NNN-<name> --web` + a note "Or open the PR via your hosting UI (compare URL format varies per platform — slice's out-of-scope for multi-remote URL derivation in v1)."
5. Show `git log -1 origin/slice/NNN-<name>` to confirm remote received the commit.

**What `--push` does NOT do**: NOT `git checkout <default>`, NOT `git merge`, NOT `git branch -d`, NOT remote-delete. The slice branch stays present locally and remotely until the PR is merged and `/commit-slice --sync-after-pr` is invoked. `--push` is NOT merged locally and NOT deleted; default branch is NOT touched.

**Critical rules for `--push`**:
- NEVER `git push --force`, NEVER `git push --force-with-lease` (force-push remains user-driven manual action).
- NEVER auto-create the PR via `gh pr create` execution — display the command/URL only.
- NEVER push to a remote other than `origin`.
- NEVER `--no-verify` to bypass pre-commit hooks.

#### Step 5d: With `--sync-after-pr` (per **ADR-020**, `methodology-changelog.md` v0.36.0 — post-PR-merge local cleanup path)

`--sync-after-pr` is the resolution path for the PR-based workflow: dev ran `--push`, opened PR, reviewers approved, PR merged on GitHub, origin slice branch auto-deleted. `--sync-after-pr` detects the merged state and cleans up local default + slice branch.

`--sync-after-pr` SKIPS Steps 1-4 (no commit message is generated — the PR has already been merged externally; this mode is local-state cleanup only).

Pre-flight guardrails (run BEFORE any state change):

1. **WT-clean check**: `git status --porcelain` MUST return empty. If non-empty, STOP. Print: "Uncommitted changes detected. Commit or stash before `--sync-after-pr`."
2. **Current-branch-is-slice-branch**: `git symbolic-ref --short HEAD` MUST start with `slice/`. Otherwise STOP. Print: "`--sync-after-pr` must be invoked from the slice branch you intend to clean up; you are on `<current branch>`."
3. **Origin-remote presence**: `git remote get-url origin` MUST succeed (same as `--push`).
4. **Slice branch has upstream tracking**: `git rev-parse --abbrev-ref --symbolic-full-name @{u}` MUST succeed (i.e., `--push` was run for this branch previously). Otherwise STOP. Print: "Slice branch has no upstream — was `/commit-slice --push` ever run? Use `/commit-slice --merge` for solo workflows or `--push` to push first."

Then the cleanup flow:

1. **Sync remote refs**: `git fetch --prune origin <default> slice/NNN-<name>` (explicit refspec per /critique M1 ACCEPTED-FIXED — Signal B requires fresh local view of `origin/<default>`; the explicit form ensures it regardless of remote.fetch config).
2. **Resolve default branch** (per BRANCH-1 canonical helper — same N=3 surfaces as `--merge` + `--push`):
   ```
   default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
   # STOP if neither resolves
   ```
3. **Two-signal merged-state detection**:
   - **Signal A**: `git ls-remote --exit-code origin slice/NNN-<name>` returns non-zero (remote branch absent — pruned because PR merged and remote auto-deleted).
   - **Signal B (two-pass — per /critique B2 ACCEPTED-FIXED + /critique-review M-add-5 ACCEPTED-FIXED — handles GitHub squash-merge of N>1-commit slice branches)**:
     - **Pass 1 (per-commit cherry-pick equivalence)**: `git cherry origin/<default> slice/NNN-<name>` returns no lines starting with `+` → Signal B=YES (every commit individually represented; covers plain merge-commit + rebase-merge + cherry-pick-equivalence + single-commit-squash).
     - **Pass 2 (aggregate-tree-diff fallback, when Pass 1 reports `+` lines)**: compute `BASE=$(git merge-base origin/<default> slice/NNN-<name>)`; build the slice's full file-set `FILES=$(git diff --name-only BASE..slice/NNN-<name>)`. Three guards apply:
       - **Empty-FILES guard** (closes data-loss false-YES path): if `FILES` is empty (slice net-changes nothing — e.g., file added then removed, or intermediate-commit churn nets to zero) → Signal B Pass 2 = **NO**; STOP with diagnostic "Slice has empty net file-set — `--sync-after-pr` cannot verify merge via Pass 2. Manually verify PR-merged state and use `git branch -D` only if confirmed."
       - **Perf bound** (closes unbounded-scan path): Pass 2 scan is bounded to the most recent N=500 commits on `BASE..origin/<default>`. If `BASE..origin/<default>` exceeds 500 commits → STOP with diagnostic "Slice base is older than 500 commits behind `origin/<default>` (long-lived slice on busy default). Pass 2 scan exceeds perf bound. Manually verify PR-merged state via your PR UI and `git log origin/<default>` inspection, then use `git branch -D slice/NNN-<name>` after confirmation."
       - **Predicate** (after both guards pass): for each commit C on `BASE..origin/<default>` (within the 500-commit bound) check whether C's **touched-file set is a superset of `FILES`** (touched ⊇ FILES — allows GitHub conflict-resolution to touch additional files during the PR merge) AND C's **tree-state at the paths in `FILES`** (intersection only) equals `slice/NNN-<name>^{tree}` at those same paths. If ANY such C exists → Signal B Pass 2 = **YES** (squash-merge detected; the matching C is the squash commit). Else → Signal B Pass 2 = **NO**.
   - **Both signals MUST agree YES** → proceed to cleanup flow.
   - **Signal A=NO** (remote branch still exists at `origin/slice/NNN-<name>`): STOP. Print: "Remote slice branch still exists at `origin/slice/NNN-<name>`. PR may be open / unmerged / approved-but-not-merged. Resolve via your PR UI before retrying `--sync-after-pr`."
   - **Signal B=NO** (neither Pass 1 nor Pass 2 matched — commits NOT yet on `origin/<default>`): STOP. Print: "Slice branch's commits are NOT yet on `origin/<default>`. PR likely not merged yet. Re-run after PR is merged. (Detected via `git cherry` Pass 1 + aggregate-tree-diff Pass 2 — both failed.)"
   - **Signal A=YES + Signal B=NO has two common causes** (per /critique M5 ACCEPTED-FIXED): (1) PR commits don't represent the slice branch's full work — verify via `git log origin/<default>` vs `git log slice/...` AND aggregate-tree-diff at `FILES`; (2) abandoned/force-deleted PR where commits were never merged. STOP regardless and ask user to disambiguate via the printed `git diff` hints.
4. **Cleanup flow**: ask: "Slice branch's PR appears merged + remote-deleted. Confirm local cleanup (checkout `<default>` + pull --ff-only + safe-delete `slice/NNN-<name>`)? (yes/no)" — on no: ABORT cleanly.
5. On yes: `git checkout <default>` → `git pull --ff-only origin <default>` (explicit `--ff-only` per /critique B1 ACCEPTED-FIXED — `git pull`'s default is MERGE not ff-only; if pull is non-ff or conflicts, STOP and leave repo state intact per slice-021's NEVER-auto-resolve rule) → **idempotent worktree-remove guard** (per **BRANCH-2** / [[ADR-063]] §Decision Step 5d sub-step 8 — symmetric with Step 5b sub-step 5): `git worktree list --porcelain | grep -E "^branch refs/heads/slice/NNN-<name>$"` → if empty, LOG `slice/NNN-<name> worktree absent — skip worktree-remove`; otherwise resolve `wt_path` via the same awk-extraction shape as Step 5b sub-step 5 then `git worktree remove "$wt_path"` → `git branch -d slice/NNN-<name>` (safe-delete; if `-d` refuses, STOP and print "Safe-delete refused — branch has unmerged commits. Inspect with `git log <default>..slice/NNN-<name>`. Do NOT use `-D` without understanding what's being discarded."). **Order-load-bearing**: worktree-remove MUST precede branch-delete (same constraint as Step 5b — a branch checked out in a worktree cannot be safely deleted; per git-worktree docs + ADR-063 §Decision order pin).
6. Show `git log -1` + `git log --graph --oneline -5` to confirm local default branch advanced past the merged slice commits.

If `git checkout <default>` fails because `<default>` is already checked out in another worktree, STOP and print git's stderr + add: "Resolve via `git worktree remove <conflicting-path>` if intentional, or run `--sync-after-pr` from the worktree where `<default>` lives."

**What `--sync-after-pr` does NOT do**: NOT a new commit (skips Steps 1-4), NOT a push, NOT a force-pull. It is local-state-cleanup AFTER an external PR merge.

**Critical rules for `--sync-after-pr`**:
- NEVER `git branch -D` (force-delete) — safe-delete only; if `-d` refuses, STOP with diagnostic.
- NEVER auto-resolve merge/rebase conflicts during `git pull --ff-only` — STOP, leave repo in conflicted state.
- NEVER omit the explicit `--ff-only` flag from `git pull` — `git pull`'s default is MERGE, which would silently create a merge commit on the local default branch.
- NEVER omit the explicit fetch refspec — Signal B requires fresh local view of `origin/<default>`.
- NEVER skip the two-signal AND (Signal A AND Signal B both YES) — destructive `git branch -d` requires both signals confirming.
- NEVER `--no-verify` to bypass pre-commit hooks.

### Step 6: Handle edge cases

- **Slice has deferrals**: note them in commit body; they're part of the audit trail
- **Shippability regression caught**: if /validate-slice caught + fixed a regression during this slice, note it in the body ("Caught and fixed regression in slice-018's sync test")
- **No new ADRs**: state "ADRs: none" — don't omit the line (audit expects consistent format)
- **Critic CLEAN with no fixes**: "Critic blockers addressed: none (design passed review)"

## Critical rules

- NEVER fabricate content. Every field comes from an actual vault file.
- If a field is missing (e.g., no critique.md in Minimal mode): say "Critic: skipped (Minimal mode)" not omit.
- With `--merge`: always show the message + staged files BEFORE committing on the slice branch; show the merge plan BEFORE `git checkout <default>`; show the safe-delete plan BEFORE `git branch -d`. Wait for explicit "yes" at each checkpoint.
- NEVER `--no-verify`. Pre-commit hooks (like `/drift-check`) exist for a reason; don't bypass.
- NEVER push. Push requires user decision.
- CONSISTENT FORMAT. Every slice's commit looks the same shape. Audit tools scan for these patterns.

## For Minimal mode

Slices in Minimal often skip /critique. Commit message adapts:

```
feat(scan): slice-001 — folder scan with duplicate CSV report

Walks directory, computes perceptual hash via imagehash, groups by distance.
Emits CSV with cluster_id, file_path, hash.

Slice: <vault>/slices/archive/slice-001-scan-folder-emit-csv/
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

Slice: <vault>/slices/archive/slice-024-fix-heic-timeout/
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

- Message shown → user commits (or skill commits + merges + safe-deletes with `--merge`)
- After commit: next slice begins via `/slice` (or `/pulse` to re-orient)

## Pipeline position

- **predecessor**: `/reflect` (user-invoked hand-off — NOT an auto-advance edge)
- **successor**: `/slice`
- **auto-advance**: false
- **on-clean-completion**: out of the auto-advance loop entirely. `/commit-slice` is always user-invoked and is never an auto-advance target of any skill. After it completes, the next slice begins when the user invokes `/slice` (or `/pulse` to re-orient) — never auto-triggered.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Always user-invoked — no auto-advance into or out of this skill by contract.

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block records the terminal-boundary contract: `/commit-slice` is never auto-invoked. It is included in the PCA-1 coverage set so the successor graph is closed and auditable.
