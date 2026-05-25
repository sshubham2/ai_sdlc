---
id: ADR-062
title: Mirror NAW-1 union-of-three-sources read mechanism onto /code-review SKILL.md Step 1
date: 2026-05-23
slice: slice-064-fix-code-review-diff-resolution-falsifier
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-062: Mirror NAW-1 union-of-three-sources read mechanism onto /code-review SKILL.md Step 1

## Context

`/code-review`'s SKILL.md Step 1 (slice-060 / CRSI-1 / [[ADR-059]]) resolves the slice's filtered code diff with a single bash command:

```bash
git diff "$base"...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'
```

The `<base>...HEAD` syntax is **commit-vs-commit only** (per [git-scm.com/docs/git-diff](https://git-scm.com/docs/git-diff) — "`<commit>...<commit>` … starting at a common ancestor of both"). At `/build-slice` Step 6 — where `/code-review` auto-advances from per the canonical PCA-1 chain (`tools/pipeline_chain_audit.py:73-82`, slice-060) — **slice work is uncommitted in the working tree**. Commits land only at `/commit-slice`, the LAST step of the chain, user-invoked post-`/reflect` per the PCA-1 HARD-STOP terminal contract (`methodology-changelog.md` v0.41.0; slice-NN PCA-1 lineage).

Consequence: a clean-tree-from-Step-6 `/code-review` invocation runs `git diff "$base"...HEAD` on a branch whose tip equals `$base` (no commits yet), producing an empty file-set. Step 1's `no-code-changes` error case then writes `Result: NO-CODE-CHANGES — nothing to review` to `code-review.md`, marks the auto-advance clean, and proceeds to `/validate-slice`. The slice's actual code diff (uncommitted in WT) is never reviewed — a silent false-positive on every governed slice's in-loop code review.

slice-063 already discovered and retired this exact class — the **B1 falsifier class** — on its own audit-tool surface (NAW-1; [[ADR-061]] §Decision L60-67). NAW-1 reads the **union of three git-derived sources** covering all states a new file can occupy at `/build-slice` Step 6:

  1. `git diff --name-only --diff-filter=A {base} -- <pathspec>` — working-tree-vs-base.
  2. `git ls-files --others --exclude-standard -- <pathspec>` — untracked-new.
  3. `git diff --name-only --diff-filter=A {base}...HEAD -- <pathspec>` — commits-vs-base.

The slice-063 reflection L94 + L40 explicitly named the `/code-review` surface as the second known carrier of the B1 falsifier class (N=2 cumulative across NAW-1 + `/code-review`) and nominated mirroring NAW-1's union-of-three-sources fix onto `/code-review` as the ACTIVE slice-064 deferral.

## Options considered

1. **Route A — Mirror the union-of-three-sources read mechanism onto `/code-review` SKILL.md Step 1 (chosen)**:
   - **Pros**: Closes the B1 falsifier class on the second known carrier surface. Pattern is canonical and execution-proven on NAW-1 (slice-063 N=8 zero-false-alarm streak; verified at `tools/new_agent_warning_audit.py:182-228`). Surgical edit — only Step 1's bash block + Step 2's prompt-template `# Diff content` paragraph change; chain shape, agent-spawn semantics, error cases, `no-code-changes` branch, walking-skeleton advisory-only disposition all preserved verbatim. SOAD-1 + AskUserQuestion not required (no user-input gate added — the change is internal-to-SKILL.md prose).
   - **Cons**: Step 1 grows from one bash command to three (plus a small `union` aggregation step) — a ~15-line prose expansion. Step 2's prompt-template diff-content paragraph also rewrites to align (`git diff "$base" -- <file>` per file instead of `git diff "$base"...HEAD -- <files>`). Both are mechanical and within Step 1/Step 2's existing structural bounds.

2. **Route B — Drop the `...HEAD` and use plain `git diff "$base"` (single-command working-tree-vs-base only)**:
   - **Pros**: Simpler than the union — a one-character edit (drop `...HEAD`).
   - **Cons**: Misses untracked-new files (`/repro`-authored test files at /build-slice Step 6 pre-commit). Misses already-committed-in-branch files (a slice with a `/build-slice` Phase intermediate commit, or a worktree-add path). The pre-fix surface used `<base>...HEAD` because slice-060 conceptually wanted "committed slice work vs default branch"; degrading to "working-tree-vs-base only" would re-open a sibling class (committed-slice-work falsely absent from review). The union covers ALL three states in lock-step with NAW-1's already-proven discharge pattern. Rejected: gains simplicity at the cost of completeness; carries silent gaps the canonical union avoids.

3. **Route C — Replace bash with a Python helper (`tools/code_review_diff_resolver.py`)**:
   - **Pros**: Code-level fix; reusable across other diff-consuming surfaces. Could expose the same `default_branch_resolver` / `added_files_resolver` injection seams NAW-1 uses (`tools/new_agent_warning_audit.py:258-267`) for deterministic regression testing.
   - **Cons**: Introduces a new `tools/*.py` module, triggering BC-PROJ-9 5-inventory fan-out (`_CANONICAL_TOOLS` + `_ROOT_ONLY_TOOLS` + `plugin.yaml` tools-block + INSTALL.md tool-count literals + ai-sdlc-tools VERSION re-installation). Couples /code-review's SKILL.md tightly to a Python module (the SKILL.md would prose-pin a `$PY -m tools.code_review_diff_resolver` invocation, which then becomes a new CSP-1 / PMI-1 surface to maintain). Slice-064 is a focused-fix slice; introducing a new tool inflates scope. Rejected: the read mechanism is 3 bash one-liners — Python helper adds complexity without solving any contract that prose can't.

4. **Route D — voluntary-restraint: mint no new rule, mint no ADR, ship a silent SKILL.md prose edit**:
   - **Pros**: Cheapest of all (one SKILL.md prose edit + drift-guard re-sync).
   - **Cons**: Violates slice-062 reflection L77 voluntary-restraint discipline boundary — that posture is RESERVED for retirement-discharge / part-(b) closure / pure-conformance shapes (slice-040 R-10 / slice-043 R-6 / slice-045 R-11 / slice-056 R-15 part-(a) / slice-057 R-15 part-(b) — N=5 cumulative class precedent). This slice is a methodology-surface **scope-extension** (mirroring NAW-1's pattern onto a sibling SKILL.md surface), NOT a retirement-discharge. The slice-049 / slice-050 / slice-051 / slice-057 / slice-058 / slice-059 / slice-062 N=6 cumulative scope-extension precedent calls for changelog + ADR + PMI-1 bump + shippability row + entry-pin pair (Inclusion-heuristic firing). Rejected: misapplies voluntary-restraint to a non-conformance slice.

## Decision

Apply **Route A**: mirror NAW-1's union-of-three-sources read mechanism onto `/code-review` SKILL.md Step 1, with Step 2's prompt-template `# Diff content` block aligned to the same WT-aware diff (`git diff "$base" -- <file>` per file).

### Step 1 — new bash block

```bash
default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
base=$(git merge-base "$default" HEAD)

# Source (i): working-tree-vs-base (modified + staged-but-uncommitted adds)
git diff "$base" --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'

# Source (ii): untracked-new files
git ls-files --others --exclude-standard -- ':(exclude)architecture/**' ':(exclude)docs/**'

# Source (iii): commits-vs-base (already-committed-in-branch adds)
git diff "$base"...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'
```

Per /critique M1 fix: the path-exclude pathspecs are **inline literals on each leg** (the same shape as the slice-060 single-command Step 1 block), NOT a bash-array (`exclude=( … )` + `"${exclude[@]}"`) — POSIX `sh` does not support indexed arrays, and Claude Code's bash tool runs under bash on Unix and PowerShell on Windows; the inline form is portable across shells.

After the three commands, **Claude unions the three command outputs by path and deduplicates the resulting set** (per /critique M2 fix — Claude's runtime aggregation obligation is prose-binding, not ADR-only): the SKILL.md Step 1 post-bash prose carries the explicit instruction "Union the three outputs by path; deduplicate. The resulting file list is the in-scope diff scope handed to Step 2." That sentence is structurally pinned by AC#1's sibling test `test_skill_md_step_1_union_aggregation_prose_pinned`, asserting the union-instruction substring presence in the Step 1 section. Without the prose pin, a future Claude could plausibly run only Source (iii) for token budget, concatenate without deduplicating, intersect instead of union, or ignore Source (ii) — all silent failures the AC#1 filter-shape pin alone cannot reach.

`base` is resolved via the SAME BRANCH-1 chain slice-060 used (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → `default-branch-unresolvable` error case STOP).

### Step 2 — prompt-template `# Diff content` block aligned

For each in-scope file emitted by Step 1's union, the agent receives the WT-vs-base diff:

```
# Diff content
<for each file in the union: paste `git diff "$base" -- <file>` output, size-limited per Claude Code prompt budget>
```

The shape change: `git diff <base>...HEAD -- <files>` (commit-vs-commit aggregate) → `git diff "$base" -- <file>` (WT-vs-base, per file). The per-file form observes uncommitted edits AND is line-bounded enough that prompt-budget overflow on a many-file slice is gracefully handled file-by-file (the existing "if diff exceeds budget, list paths and let agent Read individual files" fallback at SKILL.md L85 still applies).

### Error cases preserved

- `default-branch-unresolvable` — SAME as pre-fix (STOP with BRANCH-1-shaped error).
- `no-code-changes` — fires ONLY when the union of sources (i + ii + iii) is empty. This is the structural improvement: the false-positive class is closed because a genuinely-empty union only occurs on a vault-only slice (e.g., `architecture/**`-only edits, which the in-scope path filter excludes anyway) or a slice that has reverted all WT changes before Step 6. The legitimate `no-code-changes` semantics (write minimal `code-review.md`, exit clean) are preserved verbatim.

Mints no new rule. Supersedes nothing. Sits adjacent to NAW-1 (slice-063 / ADR-061) on the **methodology-surface read-mechanism axis** — both surfaces share the canonical union-of-three-sources pattern for observing slice state at `/build-slice` Step 6.

## Consequences

- **Downstream gates** (no existing gate disturbed):
  - `/build-slice` Step 6 pre-finish runs `tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` (BFRD-1 repro test, slice-064 /repro Step 5) which transitions FAIL → PASS on Step 1's bash rewrite.
  - `tests/skills/code_review/test_code_review_skill_drift.py` (slice-060 OSDG-1 mini-CAD) continues to gate the in-repo↔installed forward-sync invariant on `skills/code-review/SKILL.md` — the slice MUST forward-sync to `~/.claude/skills/code-review/SKILL.md` in the same fix block as the SKILL.md edit (must-not-defer #3 at mission-brief).
  - PCA-1 `tools/pipeline_chain_audit.py` chain-shape block at SKILL.md's tail is UNTOUCHED — predecessor `/build-slice`, successor `/validate-slice`, auto-advance true preserved verbatim.
- **B1 falsifier class N=2 cumulative retirement on /code-review surface**: slice-063 retired it on NAW-1's audit-tool surface (`tools/new_agent_warning_audit.py:182-228`). slice-064 retires it on the `/code-review` SKILL.md surface. The conceptual pattern (union-of-three-sources read mechanism for observing slice state at /build-slice Step 6) is canonically established across both surfaces. Future SKILL.md / audit-tool surfaces that need to observe slice-Step-6 WT state inherit this discharge pattern by reference, NOT by code import (the two surfaces are independent implementations of the same conceptual contract — see design.md "R-X2" risk-decline note for the rationale against minting a cross-pin).
- **No new RULE-ID minted**: NAW-1's read mechanism is the canonical pattern; ADR-062 documents the application of that pattern to a sibling surface. Inclusion-heuristic firing on scope-extension precedent (N=8 cumulative inclusive of slice-064: slice-049/050/051/057/058/059/062 = 7 prior + this slice = 8).
- **5-part PMI-1 atomic bump** 0.66.0 → 0.67.0: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` (PVFS-1, slice-054) + `## v0.67.0 — 2026-05-23` methodology-changelog header + installed `~/.claude/ai-sdlc-VERSION` (AVFS-1 forward-sync, slice-050). BC-PROJ-9 5-inventory fan-out does NOT fire — this slice adds zero `tools/*.py` / `skills/*/SKILL.md` (new) / `agents/*.md` / install-recipe tool-count literals.
- **Methodology-changelog v0.67.0 entry** (next-free; head was `v0.66.0` slice-063 / NAW-1); META-1 + MCFS-1 cover its parity/shape. Entry shape per Inclusion-heuristic precedent (slice-062 v0.65.0 / ADR-060 / R-15-scope-extension shape — 8-anchor EPGD-1 pin list): header + Rule reference + NAW-1 (referenced not minted) + ADR-062 + extends-pattern + 5-part PMI-1 + /code-review surface + Inclusion-heuristic-class.
- **Shippability row #64** (added at /repro Step 5 as a stub) extended at /build-slice Phase E to cite the full BCR-1-traceability axis (cites BOTH ADR-062 AND NAW-1 / ADR-061 AND R-18-retired) + the entry-pin pair (`test_v_0_67_0_naw_extend_entry_present_in_repo` + `test_v_0_67_0_naw_extend_shippability_consumer_propagation`) in the Command cell.
- **No vault component added** (modified surface is an existing SKILL.md). **No `components/` file** (Standard mode thin-vault). **CLAUDE.md NOT edited** — ADR-062 is enforced at audit time + structurally pinned by the 3 prose-pin tests, not a per-edit discipline rule for users.
- **No SUP-1 supersession** — ADR-062 extends NAW-1's pattern; nothing is superseded. ADR-061 (NAW-1) + ADR-059 (CRSI-1) + slice-060 walking-skeleton v1 advisory-only disposition are all preserved verbatim.
- **`/code-review` v2 enhancements remain deferred** to slice-065+ — TRI-1 routing + verdict-driven block on `/validate-slice` + AI-bloat passes (originally nominated for slice-061/062/063; deferred again at slice-064 per CLAUDE.md "no while-I'm-here cleanups"). ADR-062 is a focused B1-falsifier-fix ADR; the broader v2 surface is its own slice with its own Critic pass.
- **Code-Critic m1 from slice-063 remains deferred** to slice-065+ — drop both `try/except FileNotFoundError` blocks from `tools/new_agent_warning_audit.py::_resolve_default_branch`. Different file (NAW-1 audit tool, not `/code-review` SKILL.md); declined the bundle to keep slice-064 focused on the B1 falsifier fix only.

## Reversibility

**Cheap.** Reverting means: (1) restore `skills/code-review/SKILL.md` Step 1 to the single-command form via `git revert` (slice-064 will land as one commit per BRANCH-1 / `/commit-slice --merge`); (2) restore Step 2 prompt-template to the original `git diff <base>...HEAD -- <files>` form (same commit); (3) drop the 3 prose-pin tests from `tests/skills/code_review/test_code_review_skill.py`; (4) drop the shippability row #64 + the v0.67.0 changelog entry + the entry-pin pair tests; (5) flip PMI-1 5-part bump back to 0.66.0 (VERSION + plugin.yaml + pyproject.toml + installed ai-sdlc-VERSION); (6) forward-sync the reverted installed `~/.claude/skills/code-review/SKILL.md`; (7) author a SUP-1 supersession ADR documenting the rationale. No downstream consumer is built on ADR-062's existence — NAW-1 / ADR-061 / R-18-retirement / CRSI-1 / ADR-059 are all independent. Est. ~30 minutes.

The B1 falsifier would re-manifest immediately on revert (verified by /repro's regression test surface). Any future revert must EITHER ship an alternative mitigation OR accept the falsifier class re-opening.
