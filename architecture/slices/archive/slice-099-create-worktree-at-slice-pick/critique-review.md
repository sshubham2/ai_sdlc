# Critique Review: Slice 099 create-worktree-at-slice-pick

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-02
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is strong: all four Blockers and three Majors are VALID with correct severities, and the Builder's 10 ACCEPTED-FIXED edits largely hold under code-grounded scrutiny — including the load-bearing B1 index-lock concurrency rewrite, which the meta-Critic empirically confirmed is technically sound (per-worktree index isolation means concurrent same-main-tree picks genuinely contend on one `.git/index.lock`). The review's gap is one missed Major: ADR-090's frontmatter says `supersedes: null` while the title, body, mission-brief AC4, design.md, and the verification plan all assert it partial-supersedes ADR-063 — a contradiction the Builder's fixes left standing and that breaks the established partial-supersession encoding pattern ADR-063 itself documents. Three Minor fix-delta precision gaps also surface.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity), with fix-delta verification:

- **B1** (PCR doesn't resolve a master-commit race) — confirmed; Blocker appropriate. The fix-delta's new claim ("queue commit serialized by git's index lock") is **technically sound**: each worktree has its own index (`.git/worktrees/<name>/index`) while the main tree's index is `.git/index`; since only one tree can hold `master` (worktree branch-checkout exclusivity), two concurrent `/slice` picks both contend on the *same* main-tree `index.lock`, and a contending `git add`/`commit` fails loudly — matching the design's "fails visibly and is retried." One precision nit (not severity-changing): `index.lock` serializes index-write + tree-build, while the `refs/heads/master` advance is serialized by a *different* lock (ref lock); the design slightly conflates these, but the net conclusion (serialized, fail-visible, retry) is correct.
- **B2** (`## Pick log` does not survive `format_queue_md`) — confirmed; Blocker appropriate; empirically re-confirmed (`## Pick log survives format_queue_md? False`). The read-tail/re-append fix is correct and does NOT collide with `parse_queue_text` (the pick-log line has no `### ` header, so it is not leaked as a candidate key).
- **B3** (version-bump fan-out unacknowledged) — confirmed; Blocker appropriate. `VERSION`=0.80.0, latest changelog `## v0.80.0` — the 0.80.0→0.81.0 BRANCH-3 fan-out is genuinely required.
- **B4** (WORKTREE=skip-at-pick has no recording surface) — confirmed; Blocker appropriate; the `build-log.md` Events stub fix is the right mechanism (see M-add-2 for a precision gap in the fix spec).
- **M1** (abandoned-pick is IN_PROGRESS informational, not stranded) — confirmed; Major appropriate. The Builder's downscope is **honest**: `classify_worktree_state` returns `IN_PROGRESS` for any `stage != "reflect"` (pulse_worktree_resolver.py:403-407) and `compute_status` lists IN_PROGRESS without setting `halt` (stranded_slice_audit.py:485-488).
- **M2** (cwd-mismatch now has live in-flight instances) — confirmed; Major appropriate; the "all audit invocations run from within the worktree" resolution is consistent with `_is_repo_root_a_worktree` (branch_workflow_audit.py:565-620).
- **M3** (two worktrees cannot both hold `master`; two-tree dance) — confirmed; Major appropriate. Verified against `git worktree list`: main tree holds `[master]`, worktrees hold `slice/098` / `slice/099`. The two-tree sequence with `git -C <main>` for the queue commit is correct.
- **m1** (seed partial-seed idempotency), **m2** (AC5 primary-path scope), **m3** (re-export back-compat overstated) — confirmed; Minor appropriate; all three fixes well-targeted.

## Suspicious findings

No suspicious findings. Every first-Critic finding is VALID against the code, and none over-reaches. (B1 in particular was a hard call — "route through PCR" was genuinely wrong, not a false positive; PCR's SOFT resolver is rebase-stage-only at commit-slice Step 5b.)

## Missed findings

- **M-add-1: ADR-090 frontmatter `supersedes: null` contradicts its own partial-supersession claim and the verification plan** — SUP-1 / traceability + the documented ADR-020/ADR-063 partial-supersession encoding pattern. ADR-090 frontmatter (line 8) reads `supersedes: null`, but the ADR title, body Consequences ("partial-supersedes ADR-063 timing"), mission-brief AC4, design.md §Decisions, and most concretely the **verification plan AC4** ("new ADR file exists with `supersedes: ADR-063`") all assert partial-supersession. ADR-063 itself (`supersedes: ADR-019` frontmatter + body scope enumeration) is the precedent. **Severity: Major** — no automated gate fails (`supersede_audit.py` keys on slice `**Supersedes**: slice-NNN`, not ADR frontmatter), but it breaks the documented encoding pattern AND will fail the slice's own verification-plan AC4 `supersedes: ADR-063` check at build — a self-contradiction. **Proposed fix**: set ADR-090 frontmatter `supersedes: ADR-063` (keep the append-only body scope enumeration).
- **M-add-2: B4 fix spec shows the WORKTREE=skip Events line WITHOUT the load-bearing `- ` bullet prefix the audit regex requires** — design.md line 56 + error model describe the stub line as `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>`, but `_WORKTREE_SKIP_LINE_RE` is anchored `^- \d{4}-…` (branch_workflow_audit.py:75-78) — the no-dash form does NOT match. **Severity: Minor** — the "test a pick-skipped slice passes the audit at build" must-not-defer would catch it. **Proposed fix**: write the stub line in its actual Events-bullet form with the leading `- `.
- **M-add-3: read-tail/re-append path unspecified for the first-pick case (no pre-existing `## Pick log`)** — the B2 fix doesn't state behavior when no `## Pick log` exists yet (first pick on a fresh/pre-BRANCH-3 queue): the tail read finds nothing and `record_pick` must *create* the section. **Severity: Minor** — benign but unspecified preconditions are where RMW code drops state. **Proposed fix**: one sentence in the `slice_queue_writer.py` Edge — "absent `## Pick log` → create after `## Candidates`; present → re-append" — and a first-pick test case.
- **M-add-4: PSQ-1 Step 6.5 `write_slice_queue(repo_root=Path('.'))` cwd-relativity not re-specified to the main tree under the two-tree sequence** — the two-tree sequence says the queue *commit* is `git -C <main>`, but the existing Step 6.5 invocation writes the queue with `repo_root=Path('.')` (slice SKILL.md:415); under BRANCH-3 the session may have `cd`'d toward the worktree, so `.` would write the worktree's queue, not the main tree's. **Severity: Minor**. **Proposed fix**: state in the Step 6.5 re-scope that `write_slice_queue` is called with `repo_root=<main-tree-root>` (the main tree's `git rev-parse --show-toplevel`), not `.`.

## Severity adjustments

No severity adjustments. All eleven first-Critic findings (B1-B4, M1-M3, m1-m3) are filed at the correct severity. M-add-1 is a *new* finding (not a re-grade).

## Notes

Confidence is high on the confirmed set and on M-add-1 (a concrete frontmatter/verification-plan contradiction cross-checked against four surfaces + the ADR-063 precedent). The first Critic correctly caught all four mechanism-level Blockers (the PCR mis-attribution and the empirically-falsified pick-log survival being the two genuinely hard catches) and calibrated severities well; its one blind spot was an artifact-consistency check on the new ADR's own metadata — a recurring class (a Builder rewriting prose under time pressure updates the body but not the frontmatter). The Builder's fix-delta is notably honest — the M1 downscope accurately reports that BRANCH-3 raises the abandon rate and defers a real discriminator rather than relabeling. One reservation worth a TRI-1 glance (not a filed finding): an orphan *worktree + branch* is a heavier abandon artifact to GC than the pre-BRANCH-3 branchless folder was, so the deferred `abandoned-pick-detection` follow-up should be treated as warranted-soon, not optional. The four Minor fix-delta gaps (M-add-2/3/4 + the B1 index.lock-vs-ref-lock nit) are build-time-catchable but cheaper to fold into the build plan now; M-add-2 in particular ships a regex-shape trap straight into `/build-slice` if left as-is.
