# Design: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Date**: 2026-05-31
**Mode**: Standard

## Problem restated

`/commit-slice`'s stale-slice-branch pre-flight guardrail fires in two places:

- **`--merge`** Step 5b sub-step 1 (`skills/commit-slice/SKILL.md:167`)
- **`--push`** Step 5c pre-flight #2 (`skills/commit-slice/SKILL.md:242`)

Both run `git for-each-ref --format='%(refname)' refs/heads/slice/` and STOP if **any non-current** `slice/*` branch is returned. That heuristic equates "another `slice/*` branch exists" with "stale conflict artifact." Under the PSQ-1 / PSQ-2 / BRANCH-2 parallel-slice model, a concurrent `slice/NNN` branch **with its own live worktree** is the normal state, so the guardrail false-positives and STOPs a legitimate merge/push — observed firsthand merging slice-088 while slice-087 was an active parallel slice (resolved only by manual override). Because the guardrail is *pre-flight*, it STOPs **before** the PSQ-3 rebase (sub-step 2.5) can run — making the existing rebase-and-resolve machinery unreachable while any peer slice is in flight.

## Core design decision

**Worktree-backing is the discriminator.** A local `slice/*` branch that has a live registered worktree is an active parallel slice (legitimate → allow); a `slice/*` branch with **no** worktree is a genuine orphan/straggler (stale → refuse).

**Worktree-backing is determined by parsing `git worktree list --porcelain` branch lines DIRECTLY** — reusing the raw `pulse_worktree_resolver._parse_worktree_porcelain` (slice-077 / ADR-070), NOT the higher-level `detect_active_worktrees()`. This is a deliberate correction (Critic B3): `detect_active_worktrees()` applies a slice-name-suffix filter (`_SLICE_BRANCH_RE = ^slice/(\d{3})-(.+)$`, pulse_worktree_resolver.py:320-322) and drops `prunable` / detached / path-gone worktrees — branches filtered for reasons unrelated to orphan-ness. Subtracting that filtered set would silently misclassify a worktree-backed `slice/077` (no `-name` suffix) as an orphan and false-STOP. Parsing the porcelain `branch refs/heads/slice/*` lines directly makes worktree-backing independent of the name-suffix regex.

**Algorithm** (all branch names are normalized to **short form** `slice/NNN-name` before any set operation — Critic B-add-1):
1. `current_path = git -C <repo> rev-parse --show-toplevel` (normalize `\`→`/`); `current_branch = git -C <repo> symbolic-ref --short HEAD`.
2. `backed = { strip_refs_heads(block["branch"]) for every worktree block in git worktree list --porcelain whose branch matches refs/heads/slice/ AND whose worktree path ≠ current_path }`. **The classifier itself strips the `refs/heads/` prefix** — the reused `_parse_worktree_porcelain` returns the `branch` field as the RAW refname `refs/heads/slice/NNN-name` (the strip lives in `detect_active_worktrees:319`, which we are NOT calling), so the classifier must do `branch[len("refs/heads/"):]` to land in the same short-form space as step 3. Keyed by worktree PATH, so the **current slice's own worktree is excluded by path-equality** (Critic B1), with current-branch exclusion as defense-in-depth.
3. `all_slice_refs = { git -C <repo> for-each-ref --format='%(refname:short)' refs/heads/slice/ } − {current_branch}` (Critic m2: `%(refname:short)` yields short `slice/NNN-name`).
4. `parallel_slices = all_slice_refs ∩ backed` (worktree-backed → allow); `orphan_branches = all_slice_refs − backed` (worktree-less → stale). **Both operands are short-form** — a raw-vs-short key mismatch would make `∩` always empty / `−` always all-refs → universal false-refuse (Critic B-add-1). The test `test_worktree_backed_slice_branch_is_allowed` MUST assert short-form membership against a REAL porcelain fixture (not a stub that pre-strips), so this contract is exercised end-to-end.
5. `verdict = "refuse" iff orphan_branches non-empty, else "allow"`.

**Ordering invariant** (Critic B1): the classifier MUST run at pre-flight (Step 5b sub-step 1 / Step 5c pre-flight #2) while cwd is still the slice's own worktree — BEFORE Step 5b sub-step 3's `cd` to the main tree. At pre-flight HEAD is the slice branch and `--show-toplevel` is the slice worktree, so self-exclusion is correct; running it post-`cd` would resolve HEAD to the default branch and exclude nothing.

**Self-exclusion is correct IFF path-equality OR current-branch-exclusion fires** (Critic M-add-1): on Windows `git rev-parse --show-toplevel` and the porcelain `worktree` line can differ in drive-letter case / 8.3 short-name / trailing separator, so path-equality alone is not load-bearing. The current branch is therefore ALSO removed from `all_slice_refs` in step 3 (the belt to the path suspenders) — the current worktree is double-protected. A test variant feeds a case/separator-mismatched `current_path` to prove the branch-exclusion belt covers a path-equality miss.

**Boundary cases** (Critic m-add-1) — all resolve correctly under the algorithm; named here so the suite covers them: (a) zero `slice/*` refs → `all_slice_refs` empty → `orphan_branches` empty → verdict `allow`, silent; (b) a worktree on the **default branch** (or the main worktree block) → branch is not `refs/heads/slice/*`, so it enters neither `backed` nor `all_slice_refs` → correctly ignored; (c) the current slice with NO peers → `all_slice_refs` empty after self-exclusion → verdict `allow`.

The discriminator is deliberately conservative on the dangerous side: a genuinely-**stranded** branch (committed-but-unmerged whose worktree was removed — slice-087 STRANDED-COMPLETE) is worktree-*less*, so it correctly lands in **refuse**. We never reclassify stranded work as safe-to-ignore (R-26 alignment). We do NOT add merge-ancestry logic to further sub-classify worktree-less branches — that is the stranded detector's job, not this guardrail's; worktree-less → refuse (with the existing actionable message that already points post-PR-merge stragglers at `--sync-after-pr`). A worktree-backed branch with a **non-canonical name** (e.g. `slice/077`, no `-name`) is still recognized as backed (allow); the informational note flags it ("`slice/077` has a worktree but a non-canonical name — rename per ADR-063").

## What's new

- `tools/stale_branch_classifier.py` — a small read-only library + CLI that classifies the repo's local `slice/*` branches into `parallel_slices` (worktree-backed, non-current → allowed) vs `orphan_branches` (worktree-less, non-current → stale), and returns a `verdict` of `allow` | `refuse` (`refuse` iff ≥1 orphan).
- `tests/methodology/test_stale_branch_parallel_aware.py` — unit tests exercising both classification directions + the merge/push symmetry + bootstrap fallback.

## What's reused

- `tools/pulse_worktree_resolver.py` — the **raw** `_parse_worktree_porcelain(output)` block parser (reused directly per Critic B3; NOT `detect_active_worktrees`, whose name-suffix filter would misclassify). Reusing a module-level private helper is consistent with codebase convention (pulse_worktree_resolver itself reuses the private `branch_workflow_audit._resolve_default_branch`). (slice-077 / [[ADR-070]])
- `tools/_stdout.reconfigure_stdout_utf8` — Windows cp1252 console safety (UTF8-STDOUT-1).
- `skills/commit-slice/SKILL.md` — the two guardrail surfaces being made parallel-aware.
- CSP-1 cross-spec parity conventions from `pulse_worktree_resolver` / `parallel_conflict_resolver`: argparse `--repo-root` (parse-time `default=Path(".")`, post-parse `.resolve()`), `--json`, JSON `{"action": ...}` stdout / `{"action":..., "error":...}` stderr, and the **exit-code contract 0 success / 1 runtime error / 2 malformed CLI args** (Critic M1 — matches `pulse_worktree_resolver.py:26`; the earlier 0/2 draft was a parity break).
- Default-branch resolution is **NOT needed** by this guardrail (worktree-backing is independent of the default branch) — so this helper does NOT call `_resolve_default_branch`, and there is no default-unresolvable exit path here.

## Components touched

### `tools/stale_branch_classifier.py` (new)
- **Responsibility**: classify local `slice/*` branches by worktree-backing so the `/commit-slice` stale-branch guardrail can distinguish a legitimate concurrent slice from a genuine orphan.
- **Lives at**: `tools/stale_branch_classifier.py` (created by this slice)
- **Key interactions** (read-only — never mutates git state): `git -C <repo> for-each-ref --format='%(refname:short)' refs/heads/slice/` (enumerate local slice branches; Critic m2 — `%(refname:short)` normalizes to `slice/NNN-name`); `git -C <repo> rev-parse --show-toplevel` (current worktree path, for path-equality self-exclusion); `git -C <repo> symbolic-ref --short HEAD` (current branch, defense-in-depth exclusion); `git -C <repo> worktree list --porcelain` parsed via the reused `pulse_worktree_resolver._parse_worktree_porcelain` (worktree-backed branch set, independent of `_SLICE_BRANCH_RE`).
- **Public surface**:
  - `classify_stale_branches(repo_root: Path) -> StaleBranchVerdict` — library API returning a frozen dataclass `{verdict: "allow"|"refuse", current_branch: str|None, parallel_slices: list[str], orphan_branches: list[str], noncanonical_backed: list[str]}` (`noncanonical_backed` = worktree-backed branches whose name fails `_SLICE_BRANCH_RE` — allowed but flagged in the note).
  - `main(argv) -> int` — CLI; `--json` emits the verdict dict; **exit 0** on successful classification (verdict in payload, allow OR refuse), **exit 1** on runtime error (git unavailable / not-a-repo / git command failure), **exit 2** on malformed CLI args (argparse default). (Critic M1 — sibling parity 0/1/2.)

### `skills/commit-slice/SKILL.md` (modified)
- **Responsibility**: replace the inline flag-all `git for-each-ref` heuristic at the two guardrail surfaces with an invocation of the classifier, branching on its `verdict`.
- **Lives at**: `skills/commit-slice/SKILL.md` — Step 5b sub-step 1 (`:167`) + Step 5c pre-flight #2 (`:242`)
- **New prose contract** — the two surfaces embed a **byte-identical** invocation+branching block (Critic M2.1: stated identical so a future edit to one site that misses the other is caught; an FBCD-1 prose-parity test asserts the two stale-check blocks match modulo surrounding context):
  1. Run `python -m tools.stale_branch_classifier --repo-root . --json`. (Runs at pre-flight per the Ordering invariant above — cwd is still the slice worktree.)
  2. **`verdict: refuse`** (≥1 `orphan_branches`) → STOP with the existing actionable message, now listing only the orphan branches: *"Stale slice branches detected (no live worktree): `<orphan list>`. For legitimate post-PR-merge stragglers, run `/commit-slice --sync-after-pr` on each. For other artefacts of prior unresolved conflicts, resolve manually (`git branch -d` each, after verifying merged) before retrying."*
  3. **`verdict: allow`** with non-empty `parallel_slices` → surface a one-line informational note *"N parallel slice(s) in flight (worktree-backed, not stale): `<list>`"* (appending the `noncanonical_backed` rename hint when present) and PROCEED (no STOP).
  4. **`verdict: allow`** with empty `parallel_slices` → proceed silently (today's clean path).
  5. **Bootstrap / failure fallback** (helper unavailable — `ModuleNotFoundError` / import failure / **exit ∈ {1, 2}**): fall back to the **legacy flag-all check** — `git for-each-ref --format='%(refname:short)' refs/heads/slice/` minus the current branch (`git symbolic-ref --short HEAD`); STOP if any remain. Strictly no weaker than today; Critic M1 widens the trigger from "exit 2" to "exit ∈ {1,2}" so a runtime git error still falls back. Per [[ADR-064]] bootstrap-defense + PCR-2b bootstrap-guard precedent. Surface the failure reason to the user (fail-visible, not silent).

- **Symmetry & the `--push`→`--sync-after-pr` window** (Critic M2.2): self-exclusion (above) removes the *current* slice branch from both sets, so a `--push` immediately followed by these checks never flags its own pushed branch. A *prior*-pushed peer slice that still holds its worktree (between its `--push` and its `--sync-after-pr`) is correctly worktree-backed → surfaces as a benign `parallel_slices` note, not an orphan. The two surfaces are behaviourally identical because the classifier is position-independent (it reads git state, not skill-step context).
- **Self-exclusion correctness** (Critic M3): BOTH the classifier path and the bootstrap-fallback exclude the current branch before evaluating remaining `slice/*` refs. This makes explicit the "non-current" qualifier that the legacy SKILL.md:167 prose asserted but never mechanized — resolving an inherited ambiguity rather than silently carrying it forward.

## Contracts added or changed

No HTTP/event contracts. The CLI contract for `tools/stale_branch_classifier.py` (above) is the new surface. JSON output shape:

```json
{"action": "classify-stale-branches", "verdict": "allow",
 "current_branch": "slice/089-make-commit-slice-stale-branch-check-parallel-slice-aware",
 "parallel_slices": ["slice/090-add-rebase-and-conflict-resolve-to-commit-slice-push"],
 "orphan_branches": [],
 "noncanonical_backed": []}
```

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/stale_branch_classifier.py` | `skills/commit-slice/SKILL.md` (Step 5b sub-step 1 + Step 5c pre-flight #2 invoke `python -m tools.stale_branch_classifier --json`) | `tests/methodology/test_stale_branch_parallel_aware.py::test_worktree_backed_slice_branch_is_allowed` | — |

## Decisions made (ADRs)
- [[ADR-081]] — worktree-backing is the stale-vs-active-parallel discriminator for the `/commit-slice` stale-branch guardrail (refuse only on worktree-less `slice/*` branches) — reversibility: **cheap** (heuristic refinement localized to two SKILL.md blocks + one helper+test; revert = restore the legacy `for-each-ref` check and delete the helper; bootstrap-fallback already IS the legacy behavior — Critic m1).

## Authorization model for this slice

No external authz surface. The guardrail itself is a safety check authorizing the destructive merge/push action; this slice **narrows** the refusal set (worktree-less only) while **preserving** the protection for genuine orphans/stranded work — it never widens what is allowed beyond worktree-backed peers, and the bootstrap-fallback can only be MORE conservative (flag-all).

## Error model for this slice

- Classifier runtime error (git unavailable / not-a-repo / `git` command non-zero) → **exit 1** + `{"action":..., "error":...}` on stderr (sibling parity per Critic M1). Malformed CLI args → **exit 2** (argparse default).
- The skill treats **exit ∈ {1, 2}** (Critic M1 — widened from exit-2-only) OR a `ModuleNotFoundError` as "cannot classify" → bootstrap-fallback to legacy flag-all-minus-current (fail-visible; surface stderr).
- Helper import failure (pre-install) → same legacy fallback.
- No UNKNOWN classification state: worktree-backing is a deterministic binary from `git worktree list --porcelain` — no fail-closed sub-taxonomy needed (unlike the worktree-*state* classifier in `pulse_worktree_resolver`, which must judge HEAD-vs-default ancestry). The one near-miss — a worktree-backed branch with a non-canonical name — is handled explicitly (allowed + flagged via `noncanonical_backed`), not collapsed silently.

## MEPD-1 disposition

**EXCLUDE.** This is a behaviour-refining fix-slice carrying an ADR ([[ADR-081]]) and **no new RULE-ID** — it refines the existing BRANCH-2 / PSQ-family stale-branch guardrail rather than minting a new methodology rule. No `methodology-changelog.md` entry and no `VERSION` bump are required, so the AVFS-1 / MCFS-1 / TVFS-1 forward-sync gates no-op. This matches the documented EXCLUDE precedent for risk-mitigating fix-slices with an ADR + no new RULE-ID — N≥6 (slices 077 / 079 / 082 / 084 / 085 / 086 / 087). The discharge of the methodology obligation is this explicit documented-why-none rationale (Critic MEPD-1).

Unlike the precedent slices (which ship mechanism/tools), this slice **changes a shipped guardrail's decision boundary** (narrows the refusal set from all-non-current to worktree-less-only). That behaviour-boundary change is durably captured by [[ADR-081]] (supersedes null) + the `skills/commit-slice/SKILL.md` prose delta — so EXCLUDE here means "no new RULE-ID," NOT "no behaviour change" (meta-Critic MEPD-1 reservation). The audit trail stays honest: a future reader sees the boundary moved and why, via ADR-081.

## Re-entry / interaction notes

- This change is upstream of PSQ-3 (sub-step 2.5 rebase) and PCR-1/2a/2b — it does not touch them. Its only effect is letting `--merge`/`--push` pre-flight PASS when peers are worktree-backed, so the existing rebase path becomes reachable. The queued slice-090 (`add-rebase-and-conflict-resolve-to-commit-slice-push`) then extends rebase to `--push`.
- OSDG-1: editing SKILL.md requires re-syncing the installed `~/.claude/skills/commit-slice/SKILL.md` at build time; `test_commit_slice_skill_drift.py` + the structural anchor tests (`*_merge_flag.py`, `*_push_flag.py`, etc.) must stay green — the rewrite preserves the existing message literals those anchors pin where possible, adjusting only the parallel-aware branches.
