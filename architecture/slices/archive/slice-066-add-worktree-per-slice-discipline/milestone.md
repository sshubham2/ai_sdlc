---
slice: slice-066-add-worktree-per-slice-discipline
stage: complete
updated: 2026-05-24
next-action: none (slice complete) — /commit-slice is user-invoked per PCA-1
risk-tier: medium
critic-required: true
---

# Milestone: slice-066 add-worktree-per-slice-discipline

**Stage**: complete
**Next action**: none (slice complete) — user invokes `/commit-slice` manually per PCA-1 terminal-boundary contract.
**Updated**: 2026-05-24
**Risk tier**: medium — Critic required: yes (touches `skills/build-slice/SKILL.md` + `skills/commit-slice/SKILL.md` + `tools/branch_workflow_audit.py` + new ADR + methodology-changelog + CLAUDE.md → "In-house methodology surfaces" always-mandatory-Critic trigger fires regardless of tier)

## Progress

- [x] /slice — 2026-05-24
- [x] /design-slice — 2026-05-24
- [x] /critique — 2026-05-24 — NEEDS-FIXES (5B/5M/4m; 13 ACCEPTED-FIXED + m4 ACCEPTED-PENDING)
- [x] /critique-review — 2026-05-24 — EXTEND (0 suspicious / 6 missed / 0 severity-wrong; 5 missed ACCEPTED-FIXED + M-add-5 ACCEPTED-PENDING)
- [x] /build-slice — 2026-05-24 — SHIPPED (21/21 TF-1 PASSING + 14/14 Step 6 audits clean + shippability 66/66 PASS + full pytest 869/869 PASS; N=30 cumulative findings caught + closed = 14 dual-Critic + 6 meta-Critic + 10 Builder self-catches)
- [x] /code-review — 2026-05-24 — FINDINGS (0B/2M/4m; advisory per CRSI-1 v1; 6 findings deferred to slice-067+ bundled cleanup per slice-065 precedent)
- [x] /validate-slice — 2026-05-24 — PASS (5/5 ACs PASS with evidence; VAL-1 0 secrets + 0 imports; WS-1 5/5 EXERCISED; shippability 66/66; multi-instance N/A; Builder self-catch #11 — WS-1 R-7-class regex bug HTML-comment-fragility, workaround applied + /critic-calibrate candidate logged)
- [x] /reflect — 2026-05-24 — Slice complete. Reflection captured: 6 Validated, 5 Corrected, 5 Discovered, 8 Deferred. Critic calibration: 14 first-Critic VALIDATED + 6 meta-Critic VALIDATED + 6 code-Critic VALIDATED (advisory; bundled to slice-067+) + 10 Builder self-catches MISSED-by-Critic-stack (operational layer outside Critic reach). BC-1 promotion: skipped per user (lessons more apt as /critic-calibrate proposals). Auto-archiving next.
- [ ] /reflect
- [ ] /code-review
- [ ] /validate-slice
- [ ] /reflect

## Current focus

First-Critic returned 5B/5M/4m findings; all 14 ratified by Builder as ACCEPTED-FIXED in this round except m4 (graphify CLI node-name-convention — ACCEPTED-PENDING / reflection.md /critic-calibrate watch-list at N=1). **B1 was load-bearing**: BRANCH-1 was minted by **ADR-019**, not ADR-021 (which is utf8-stdout-1, unrelated). All three slice-authoring files (mission-brief / design / ADR-063) globally renamed ADR-021 → ADR-019; ADR-063 is now the N=2 application of slice-022's partial-supersession encoding pattern. Critical structural fix-block-completeness items applied per TPHD-1 sub-mode (a): TF-1 plan expanded from 16 to 20 rows (B3 audit call-shape coverage + B4 cross-spec parity row); design.md gained "Audit invocation call-shapes" enumeration (3 shapes) + "Path-comparison semantics" sub-paragraph (Windows symlink/junction/case via `Path.resolve(strict=False)` + `samefile()` + `normcase(realpath)` fallback) + 5-row "Mode-interaction matrix" (push-then-merge / push-then-STOP / etc.); ADR-063 §Scope of supersession extended with N=3 canonical-phrase pin / prospective application / v1 carveout dispositions; commit-slice Step 5b sub-step 5 + Step 5d sub-step 8 gained **idempotent worktree-remove guard** (closes slice-066 bootstrap symmetry + any future `WORKTREE=skip` slice).

## On resume

- **Last completed action**: /build-slice Phase A + Phase B-prefix harmonization (6 Builder self-catches: PMI-1 enum × 3 + TF-1 test_path × 2 + BC-PROJ-10 paired-pin × 1; all corrected in mission-brief + design + ADR-063). Branch `slice/066-add-worktree-per-slice-discipline` checked out, working tree clean (vault is gitignored). Nothing committed yet (no tracked file edits at this checkpoint).
- **Current work**: none — paused at user check-in BEFORE writing Phase B's 21 failing tests
- **Next immediate step** (resume in fresh session):
  1. `git status` + `git branch --show-current` → confirm on `slice/066-add-worktree-per-slice-discipline` with clean WT (the vault Phase A+B-prefix work persists in gitignored files)
  2. Run `/pulse` for full re-orient (reads this milestone.md as primary source of resume state)
  3. Run `/build-slice` — it will re-read mission-brief + design + critique + critique-review + milestone + build-log, then continue from Phase B (write 21 failing tests across 8 files: 2 NEW + 6 existing)
  4. Then Phase C (implementation: audit module + 2 SKILL.md edits + ADR finalize + methodology-changelog + CLAUDE.md L32 + R-17 retire + 5-part PMI-1 bump + shippability row #66 + forward-syncs + pip install upgrade for TVFS-1)
  5. Then Phase D (mid-slice smoke + Step 6 pre-finish gate audits)
- **Estimated remaining work**: ~2-2.5h focused build time
- **Watch-list for resume** (Builder discipline reminders, per slice-066 self-catches):
  - The plan-mode-approved plan (in this conversation's history) covered Phase A through D; user pre-approved the full sequence at TRI-1 plan-mode-approval gate
  - 6 self-catches in Phase A+B-prefix is a strong signal that mid-build sweep discipline is load-bearing; budget BC-PROJ-4 (run every gate on the real artifact at pre-finish + read output) attention at Phase D
  - 2 ACCEPTED-PENDING items from /critique: m4 (graphify CLI watch-list for reflection.md) + M-add-5 (APED-1 explicit bootstrap-variant TF-1 row — Builder discretion at Phase B based on whether row 11 fixture uses bootstrap canonical sample)

## Identity notes

- **Slice 066** is the first of a 4-slice family (066/067/068/069 nominated) implementing the user's parallel-slice-queue + worktree + claim + rebase vision (`/slice` arg-string 2026-05-24). slice-066 covers the **worktree-per-slice mechanics** only — the foundational layer that makes parallel work physically possible.
- **Sibling slices nominated** (NOT this slice's scope):
  - slice-067 `add-parallel-slice-queue-output` — `/slice` writes `architecture/slice-queue.md` with top-10 parallel-safe candidates (graphify blast-radius non-overlap).
  - slice-068 `add-slice-queue-claim-state-machine` — `slice-queue.md` claim semantics + session-id detection + force-claim escape.
  - slice-069 `add-rebase-and-conflict-discipline` — `/commit-slice` rebases default before merge + structured-options ASK on conflict.
- **R-17 retirement charter**: this slice closes R-17 via the candidate fix (b) verbatim at `risk-register.md:295`. R-17 transitions `mitigating` → `retired` at AC5.
- **Bootstrap exception**: slice-066 itself authors the worktree-create prose, so it cannot self-apply at its own `## Prerequisite check ### Branch state` — discharged via canonical `WORKTREE=skip-bootstrap` DEVIATION line per slice-021 / slice-026 precedent.
- **Graphify node-naming convention** (discovered 2026-05-24 at /design-slice, relevant to slice-067 design): the graph at `graphify-out/graph.json` indexes Python modules by **basename** (`branch_workflow_audit`), NOT file path (`tools/branch_workflow_audit.py`). Function/class nodes use parens (`audit()`, `_run_git()`) or bare names (`AuditResult`, `BranchViolation`). A query like `$PY -m graphify blast-radius --from "tools/branch_workflow_audit.py"` exits 1 with "node not found"; the correct form is `$PY -m graphify blast-radius --from "branch_workflow_audit"`. Slice-067's parallel-safe blast-radius non-overlap computation MUST honour this convention; the build-slice SKILL.md L77 example (`--from=<module>`) is closer to right than the docstring patterns elsewhere that use file paths. Watch-list `/critic-calibrate` candidate at N=1: "graphify CLI node-name-convention silently failing" — exit 1 + stderr message is loud, but a Claude redirecting stderr could miss it.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — pending
- [critique-review.md](critique-review.md) — pending
- [build-log.md](build-log.md) — pending
- [code-review.md](code-review.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
