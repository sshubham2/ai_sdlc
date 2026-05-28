---
id: ADR-070
title: Worktree-awareness in /pulse via per-skill helper (not load-bearing methodology rule)
date: 2026-05-28
slice: slice-077-enhance-pulse-with-worktree-awareness
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-070: Worktree-awareness in /pulse via per-skill helper (not load-bearing methodology rule)

## Context

The post-slice-076 `/pulse` run (2026-05-28) witnessed a skill-correctness gap firsthand: with BRANCH-2 active, the slice lives in a sibling worktree (`<main-parent>/<main-name>-wt/slice-NNN-<name>` on branch `slice/NNN-<name>`) until `/commit-slice --merge`. `/pulse`'s Step 1 currently reads `architecture/slices/<active>/milestone.md` from the main tree only, so when slice-076 was fully built / validated / reflected / auto-archived in the worktree (HEAD = reflect commit; VERSION=0.73.0; 1039/1039 pytest; BC-PROJ-12 promoted) but master was still at the scaffold commit, `/pulse` mis-reported stage `slice` and recommended `/design-slice` while the real next action was `/commit-slice --merge`. `/pulse` also raised a false-positive "vault forward-population" drift flag for the same root cause (installed `~/.claude/methodology-changelog.md` was forward-synced by the worktree's `/reflect` step; master's changelog was stale until the merge landed).

Every future post-merge `/pulse` during a BRANCH-2 worktree window would repeat both errors without this slice. Slice-077 closes the gap.

The architectural question — and what this ADR captures — is the **scope class** of the fix:

- **Per-skill enhancement (chosen)**: bounded to `/pulse`'s SKILL.md + a new `tools/pulse_worktree_resolver.py` helper. MEPD-1 EXCLUDE; no methodology-changelog entry; no PMI-1 bump.
- **Load-bearing methodology rule (rejected)**: mint a "PWA-1" (Pulse Worktree-Awareness) rule on a new cross-cutting axis intended to propagate worktree-awareness to other skills (`/drift-check`, `/build-checks`, etc.). PMI-1 5-leg bump; methodology-changelog v0.74.0 entry; paired-pin tests; future-skill propagation discipline.

## Options considered

1. **Per-skill enhancement (chosen)** —
   - **Pros**: scope-honest; matches the witnessed gap's blast-radius (only `/pulse` was wrong); reuses existing OSDG-1 / CAD-1 / BC-PROJ-9 discipline without introducing a new rule axis; smaller surface = lower regression risk; cheap to revert.
   - **Cons**: if future skills (`/drift-check`, `/build-checks`) need similar worktree-awareness, each will re-implement the convention; no load-bearing rule audits enforce cross-skill consistency.

2. **Mint PWA-1 + ADR-070 promote to load-bearing** —
   - **Pros**: future-proof against the multi-skill-needs-worktree-awareness scenario; load-bearing rule makes the convention explicit + auditable; PMI-1 atomic bump documents the introduction.
   - **Cons**: premature codification — no current evidence that other skills need similar worktree-awareness (N=1 case witnessed: `/pulse`); rule-minting adds 5-leg PMI-1 bump scope (VERSION + plugin.yaml + pyproject.toml + changelog header + installed ai-sdlc-VERSION) + paired-pin tests + methodology-changelog v0.74.0 entry — substantial scope creep for SMALL-effort slice; conflicts with "thin vault, just-enough" pipeline philosophy; the convention can always be PROMOTED later if N=2+ cross-skill evidence accumulates.

3. **No code change, just document the gap as a known-issue** —
   - **Pros**: zero risk.
   - **Cons**: every future post-merge `/pulse` keeps mis-reporting; documentation-only fixes don't survive Claude session boundaries (the maintainer would have to remember the gap exists every time); fails the "deferring known correctness gaps compounds confusion" principle. Rejected.

## Decision

Option 1: **per-skill enhancement** scoped to `/pulse`. MEPD-1 EXCLUDE; no methodology-changelog entry; no PMI-1 bump; ships at v0.73.0 unchanged.

### Honest precedent inspection (per /critique M1 ACCEPTED-FIXED)

The earlier draft of this ADR claimed slice-074 / slice-075 as MEPD-1 EXCLUDE precedents. Direct inspection of those archives invalidates the claim: both shipped **pure `skills/*/SKILL.md` prose enhancements with ZERO new helper modules** — they're not structural twins of slice-077 (which ships a ~300-500 LOC helper + 5-inventory fan-out + 6 test modules). The only same-shape predecessor is **slice-076** (PCR-1) — which is MEPD-1 **INCLUDE**. So slice-074/075 are NOT the right precedent appeal.

**The honest framing**: the differentiator between INCLUDE and EXCLUDE is NOT "ships a helper module" but **"introduces a load-bearing cross-skill methodology contract"**.

- **Slice-076 / PCR-1 IS load-bearing cross-skill**: the SOFT file-set + `classify_conflict` 5-class taxonomy + `resolve_soft_conflict` ABI are **called from `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5** (cross-skill consumer wired into a different skill's runtime). The SOFT taxonomy is referenced in /commit-slice prose. PCR-N is now a methodology family with sibling-rule visibility benefit. Future skills look up "PCR-1" by RULE-ID. The methodology-changelog v0.73.0 entry is load-bearing because future RULE-ID lookups depend on it.
- **Slice-077 / hypothetical PWA-1 would NOT be cross-skill**: the 4-state taxonomy + override-precedence + drift-flag suppression predicate are **consumed only by `/pulse` itself**. No cross-skill ABI. The structural shape (helper module + dataclasses + CLI + tests) coincides with PCR-1's, but the rule-axis content does not. No future skill will look up "PWA-1" by RULE-ID; the `WorktreeState` taxonomy is a /pulse implementation detail.
- **Slice-058 IS the rule-axis precedent**: ADR-057 (install-wakeup-prompt guardrail; methodology v0.62.0 → v0.62.0 unchanged) minted an ADR without minting a methodology rule because the guardrail's surface was the INSTALL.md prose + a global CLAUDE.md append — load-bearing for installation but not a cross-skill contract. Same pattern here: ADR-070 captures the design decision without minting a cross-skill rule.

**ADR-070 minted (this file) to capture the design choice itself + 4-state worktree taxonomy + override-precedence ordering + fail-closed UNKNOWN semantics + drift-flag suppression predicate** — none of which are encoded as a rule, but all of which future maintainers benefit from seeing recorded. ADRs and methodology-changelog entries are independent axes (slice-058 precedent).

### Promotion trigger explicitly noted

If **N=2 cross-skill consumers** of the `WorktreeState` classification emerge (e.g., `/drift-check` also needs `WorktreeState`-aware behavior to suppress false positives during `BUILT_BUT_NOT_MERGED` windows; `/build-checks` skips audits unsuitable for worktree-state windows), the convention promotes to PWA-1 (Pulse-Like Worktree-Awareness) on its own methodology axis. Promotion mechanics: PMI-1 5-leg bump + methodology-changelog entry + paired-pin tests + supersede ADR-070 via new ADR per SUP-1.

### 4-state worktree taxonomy

```
WorktreeState:
  IN_PROGRESS            — worktree milestone.md stage ≠ "reflect"; slice still being built.
                           Triggers next-action recommendation: cd <worktree> && <stage-derived>.
  BUILT_BUT_NOT_MERGED   — worktree milestone.md stage = "reflect" AND worktree HEAD is NOT an
                           ancestor of <default>'s tip (per `git merge-base --is-ancestor`);
                           slice is complete but merge hasn't happened yet. Triggers next-action
                           recommendation: cd <worktree> && /commit-slice --merge.
  MERGED                 — worktree HEAD IS an ancestor of <default>'s tip. Persists legitimately
                           after multiple workflows: (a) /commit-slice --merge worktree-remove
                           failed (slice-066 bootstrap precedent); (b) /commit-slice --push +
                           PR-merged-on-remote + /commit-slice --sync-after-pr where the
                           --sync-after-pr worktree-remove also failed; (c) user manually
                           merged + forgot to remove worktree. Surfaced as a CLEANUP-CANDIDATE
                           one-line WARN in Drift & flags: `⚠️ Worktree <path> on branch
                           <branch> is MERGED but not torn down — run `git worktree remove
                           <path>` to clean up`. Does NOT override next-action; CAL-1
                           cadence-overdue / stage-derived still applies per precedence #2/#3.
  UNKNOWN                — fail-closed default: returned on ANY parse failure (fresh worktree
                           with no milestone.md yet, milestone.md frontmatter malformed,
                           detached HEAD, dirty worktree blocks classification, git command
                           error, HEAD unresolvable, slice-folder-name drift). Each UNKNOWN
                           instance surfaces as a one-line WARN in Drift & flags with the
                           specific reason. NEVER silently dropped (per /critique M3
                           ACCEPTED-FIXED). Does NOT override next-action; existing CAL-1 /
                           stage-derived precedence still applies per precedence #2/#3.
                           Never silent-defaults to MERGED or BUILT_BUT_NOT_MERGED.
```

The fail-closed UNKNOWN behavior mirrors PCR-1's UNKNOWN class semantics from ADR-069 — never auto-assume a state when classification is ambiguous; surface the failure to the user.

### Override-precedence ordering

`/pulse`'s "Recommended next action" derivation follows this precedence (HIGHEST first):

1. **Worktree-state override** (new in slice-077) — if `any(wt.state in {BUILT_BUT_NOT_MERGED, IN_PROGRESS})` across active worktrees, recommended next action becomes `cd <worktree-path> && <action>` where `<action>` is `/commit-slice --merge` for BUILT_BUT_NOT_MERGED and the stage-derived next-action from the worktree's milestone.md for IN_PROGRESS. Supersedes #2 + #3.
2. **CAL-1 cadence-overdue override** (existing, slice-031 / SRCD-1 lineage) — if /critic-calibrate cadence is `overdue` (>20 slices since last run), recommended next action becomes `/critic-calibrate`. Fires only when #1 doesn't.
3. **Stage-derived next-action** (existing) — read from active-slice `milestone.md` `next-action:` field (main-tree fallback when no worktree exists).

**Rationale for #1 > #2** (per /critique B4 ACCEPTED-FIXED — earlier draft contained an unredacted reasoning self-correction): a worktree with milestone-readable state is a **stuck-state pipeline pointer** — the user is mid-slice and the next pipeline advance requires acting on the worktree (either continuing the build for IN_PROGRESS or merging for BUILT_BUT_NOT_MERGED). CAL-1 cadence-overdue is an **advisory backlog** — calibration is due-soon but the user can still pick + run the next slice if no slice is currently in-flight. Stuck-state pipeline pointers rank above advisory backlogs because the user actioning the stuck-state recommendation also clears the surface that would normally block the advisory's primary use case (picking the next slice). Once the worktree is resolved (merge lands or build continues to completion), CAL-1 cadence-overdue still fires for the next /pulse invocation if applicable.

`MERGED` (cleanup-candidate) and `UNKNOWN` worktree states do NOT trigger rule #1 — they fall through to rule #2 / rule #3 and contribute only a sidebar WARN in Drift & flags. See § 4-state worktree taxonomy for state-by-state next-action mapping and the design.md § Override-precedence ordering table for the full 4×CAL-1 enumeration.

### Drift-flag false-positive suppression predicate

Per /critique B3 ACCEPTED-FIXED — predicate pinned explicitly (file-set, all-match, EOL-agnostic):

```python
def should_suppress_vault_forward_population_flag(detected_worktrees, repo_root):
    # Condition #1: at least one worktree is BUILT_BUT_NOT_MERGED
    if not any(wt.state == BUILT_BUT_NOT_MERGED for wt in detected_worktrees):
        return False
    # Condition #2: ALL 3 installed surfaces match the worktree's content
    INSTALLED_SURFACES = [
        ("~/.claude/methodology-changelog.md",  "<worktree>/methodology-changelog.md"),
        ("~/.claude/ai-sdlc-VERSION",           "<worktree>/VERSION"),
        ("~/.claude/skills/pulse/SKILL.md",     "<worktree>/skills/pulse/SKILL.md"),
    ]
    for installed_path, worktree_relpath in INSTALLED_SURFACES:
        if not content_equal_modulo_eol(installed_path, worktree_relpath):
            return False  # ANY divergence → don't suppress
    return True
```

**Semantics pinned**:
- **File-set**: exactly 3 surfaces (methodology-changelog.md + ai-sdlc-VERSION + installed pulse/SKILL.md mirror). The pulse SKILL.md mirror is included because slice-077 itself edits skills/pulse/SKILL.md + OSDG-1 forward-syncs it; checking the mirror's match-to-worktree is the additional surface beyond PCR-1's typical changelog+VERSION pair.
- **All-match required**: ANY surface that doesn't match the worktree's content disqualifies suppression (fail-closed against partial-sync). Justification: if methodology-changelog matches worktree but VERSION doesn't (or vice versa), something is wrong with the forward-sync — emitting the drift flag is correct.
- **Content-equal modulo line endings per ADR-033 / EOL-DRIFT-1**: NOT sha256 byte-equal. The surrounding CAD-1 / OSDG-1 byte-equality discipline is explicitly EOL-agnostic per CLAUDE.md ("CRLF↔LF is not drift; genuine content divergence still is"); the suppression predicate inherits the carve-out so CRLF↔LF differences on Windows don't trigger spurious flag emission.

**Rationale**: master-vs-installed divergence on these 3 surfaces IS the expected state during a `BUILT_BUT_NOT_MERGED` window (the worktree's `/reflect` step forward-synced the installed copies via MCFS-1 + AVFS-1 + OSDG-1; master is behind by design until the merge lands). Flagging it as drift creates a false positive.

**Negative test (load-bearing)**: if any installed surface diverges from BOTH worktree AND main, suppression does NOT fire — that's genuine three-way drift, a real defect.

When suppression fires, /pulse emits a positive surface in lieu of the suppressed flag: `ℹ️ Master-vs-installed divergence on changelog/VERSION/SKILL.md is the EXPECTED state during the BUILT_BUT_NOT_MERGED window — run /commit-slice --merge to reconcile.`

## Consequences

- `/pulse` runs during a BRANCH-2 worktree window correctly classify worktree-state + override recommended-next-action + suppress the drift false-positive.
- New helper `tools/pulse_worktree_resolver.py` joins the canonical tools inventory (BC-PROJ-9 5-inventory pin + INSTALL.md tool-count `31 → 32`).
- `skills/pulse/SKILL.md` is now ~30-50 lines longer (Step 1 + Step 2 + Step 3 prose additions); CAD-1 / OSDG-1 byte-equality discipline guards the in-repo↔installed pair.
- ADR-070 stands as the load-bearing decision record. Future ADRs that revisit worktree-awareness across skills (if the multi-skill scenario emerges) can cite ADR-070 as predecessor + supersede it as a load-bearing methodology rule.
- No PMI-1 bump; no methodology-changelog entry; no paired-pin tests; no version-files changes. Ships at v0.73.0 unchanged.

### Forward-reference: when to promote to a rule

If 2+ future slices need similar worktree-awareness in DIFFERENT skills (e.g., `/drift-check` needs to consult worktree state to avoid false-positives; `/build-checks` needs to skip audits that don't make sense during a worktree window), promote the convention to a load-bearing rule "PWA-1 (Pulse-Like Worktree-Awareness)" or similar. The promotion trigger is N=3 cross-skill evidence (standard /critic-calibrate codification threshold).

Promotion mechanics: mint PWA-1 in methodology-changelog v0.NN.0 with the 4-state taxonomy + override-precedence as canonical contract; PMI-1 5-leg bump; paired-pin tests; ADR-NNN supersedes ADR-070 with rationale "N=3 cross-skill evidence accumulated, promoting to load-bearing rule".

### Forward-reference: when to deprecate the helper

If `/pulse` is itself superseded or refactored to consume a different macro-state-aggregation source, `tools/pulse_worktree_resolver.py` can be deprecated. The taxonomy + override-precedence concepts encoded in this ADR survive the helper's removal — they document a class of correctness concern that any successor skill would need to handle.

## Reversibility

**Cheap**. Per /critique M5 ACCEPTED-FIXED — revert is technically `git revert -m 1 <slice-077-merge-commit-sha>` under BRANCH-2's `--merge` workflow (no-ff merge requires `-m 1` to pick the mainline parent; bare `git revert` of a no-ff merge commit fails with `fatal: ... is a merge but no -m option was given`). The revert:

- Reverts the effective tree change introduced by the slice-077 merge commit (this is the load-bearing revert action).
- Orphaned child commits (Phase B/C/E/F/G/fix/validate/reflect on the deleted `slice/077-...` branch) become unreachable after the slice branch is deleted and are GC'd by `git gc` (no manual cleanup needed).
- The reverted tree state restores `skills/pulse/SKILL.md` to pre-slice-077 content (CAD-1 / OSDG-1 byte-equality is re-asserted by the existing `test_pulse_skill_drift.py` post-revert).
- The reverted tree state removes `tools/pulse_worktree_resolver.py` + companion test modules; reverts `tools/install_audit.py::_CANONICAL_TOOLS` + `plugin.yaml` tools-block + INSTALL.md tool-count + `test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS` + `architecture/shippability.md` row #77.

No external API consumers, no schema changes, no contract dependencies that downstream tooling would break.

If a future slice wishes to instead promote to a load-bearing rule, revert is NOT needed — superseding ADR (per SUP-1 append-only discipline) is the canonical path.
