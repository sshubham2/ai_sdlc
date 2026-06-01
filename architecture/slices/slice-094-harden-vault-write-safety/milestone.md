---
slice: slice-094-harden-vault-write-safety
stage: critique
updated: 2026-06-01
next-action: run /build-slice — TRI-1 verdict NEEDS-FIXES; ACCEPTED-PENDING items built in-slice; ACCEPTED-FIXED design-prose corrections applied
risk-tier: medium
critic-required: true
---

# Milestone: slice-094 harden-vault-write-safety

**Stage**: critique (v2 — NEEDS-FIXES)
**Next action**: run **`/build-slice`**. Full Critic stack ran on v2 — `/critique` NEEDS-FIXES (2B/2M/6m) + `/critique-review` EXTEND (+M-add-1/m-add-1/m-add-2). TRI-1 ratified 2026-06-01 (verdict NEEDS-FIXES); ACCEPTED-FIXED design-prose corrections applied to design.md/ADR-086/mission-brief; ACCEPTED-PENDING items built in-slice (B1 non-vacuous EPERM+>1024B proof, M1/M-add-1 5-part bump + R-33 master-merge + entry-pins at v0.80.0, m-add-1 large-payload byte test).
**Updated**: 2026-06-01
**Risk tier**: medium — Critic required: **yes** (mandatory trigger: in-house methodology surfaces `tools/**/*.py` + new audit; reinforced by vault data-integrity / concurrency sensitivity)

## Progress

- [x] /slice — 2026-05-31
- [x] /design-slice — 2026-05-31
- [x] /critique — 2026-06-01 — **BLOCKED** (3 blockers, 4 majors, 3 minors; all execution-verified). **TRI-1 ratified BLOCKED 2026-06-01** (all 10 dispositions accepted; B3 → flip-readiness re-scope, PCR out). `/critique-review` runs on v2.
- [x] /design-slice (REDESIGN — flip-readiness scope) — 2026-06-01
- [x] /critique (v2) — 2026-06-01 — NEEDS-FIXES (2B/2M/6m); TRI-1 ratified
- [x] /critique-review (v2) — 2026-06-01 — EXTEND (+M-add-1 Major, +m-add-1/m-add-2 Minor)
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

**v2 flip-readiness redesign + full Critic stack COMPLETE** (2026-06-01). `/critique` (NEEDS-FIXES, 2B/2M/6m) + `/critique-review` (EXTEND) both ran on v2 against the worktree; TRI-1 ratified → **NEEDS-FIXES**. ACCEPTED-FIXED design-prose corrections applied to design.md/ADR-086/mission-brief; ACCEPTED-PENDING items built in-slice. **Ready for `/build-slice`** (pending user approval of the build plan). Key v2 findings resolved: B1 (concurrency proof re-scoped to non-vacuous EPERM + >1024B append — both primitives were CRLF-buggy), B2 (routing does NOT close the RMW window — flip-residual), M2 (audit detection ≤1-hop+module-const depth), M-add-1 (v0.80.0 not 0.79.0 — slice-095 collision; R-33 master-merge first). The original v1 BLOCKED blockers, for the record (Builder AGREED, each reproduced against real code):

- **B1 — routing is NOT transparent (CRLF).** `tools/_vault_write.py` passes no `newline=` kwarg, so `safe_write_text`/`safe_append_text` emit **CRLF** on this repo's interpreter, while the existing writers use `newline=""` (**LF**). Routing as designed corrupts every vault file's newlines (EOL-DRIFT-1/ADR-033 class) → AC5 + must-not-defer violated. The mission-brief claim "`safe_write_text` keeps `newline=\"\n\"`" is false.
- **B2 — audit can't see the biggest writer + enumeration incomplete.** `parallel_conflict_resolver.py` has **7** raw vault-write ops (not 1) and imports **neither** `VAULT_ROOT` nor `_vault_paths`, so the design's primary (VAULT_ROOT-import) tripwire never fires on it. AC1/AC2 unmet as designed. ADR-086's "isolates EXACTLY the 3 real writers" is false.
- **B3 — contradicts slice-093's map + R-32 model.** R-32's register entry: concurrent-process lost-update "becomes live only at the slice-094 **flip**." All target files are **git-tracked today** (no flip), so concurrent writes surface as git conflicts PCR handles — routing through process-locks now adds no safety over the existing `.tmp`+`os.replace`, and slice-093 classified PCR as git-coupled "retires at the flip." Routing PCR now is premature/contradictory.

Plus M1 (literal-path tripwire FP surface — 37 tools name vault files, mostly readers), M2 (PMI-1 "5-part" asserted abstractly — enumerate vs real inventory), M3 (concurrency test must use `multiprocessing`/spawn + bounded timeout, not threads), M4 (ADR-086 "signatures unchanged" vs B1 fix; `.gitignore` `*.<pid>.tmp` glob matches nothing — use `*.tmp`), m1 (all design line numbers stale: real writes are `slice_queue_writer.py:818-820`, `slice_queue_claim.py:527-536`, PCR `:430/:1546/:713/:764/:1779/:2133/:2234`), m2 (primitives have zero production callers — first use), m3 (shippability is at 101 rows; cited test path not yet authored).

## Redesign scope (flip-readiness) — RATIFIED at TRI-1 (2026-06-01)

The Builder's recommended re-scope, **ratified by the user at TRI-1** (chosen via `/slice "priorities blockers for external vault flip"` → "Resume & redesign 094" → "Ratify + redesign, full stack on v2"):

1. **Fix the primitive first**: add `newline=""` to `safe_write_text`; pin `safe_append_text` LF-faithfulness; **nt-guarded byte-identity regression test** vs the pre-routing pattern (B1, M4). Update ADR-086 (signatures DO change) or supersede.
2. **Route ONLY the 2 seam whole-file writers** (`slice_queue_writer`, `slice_queue_claim`) → `safe_write_text`. **Scope PCR OUT** per slice-093's map (git-coupled, retires at the flip) — or, if kept, add the lock-held-across-`git rebase --continue` analysis B3 demands (B2, B3).
3. **Audit detection model** that does NOT depend on the VAULT_ROOT import (resolve write targets under `architecture/`), with a precise per-write-target AST match + an **executed** APED-1 battery incl. reader-with-non-vault-write=CLEAN (B2, M1).
4. **Concurrency proof** via `multiprocessing` (spawn) + bounded timeout, non-vacuity by mutation (M3).
5. **Reframe R-32**: this slice = **flip-readiness** (byte-faithful primitive + enforcement audit + 2 seam writers + concurrency proof). R-32's runtime hazard **retires at the flip**, not now (B3). Reconcile mission-brief AC1 ("every call site routes through") to a code-grounded executed enumeration.

Alternatives the user may pick instead: (b) run `/critique-review` first (meta-Critic) before redesign; (c) keep PCR in scope (larger; needs the rebase-lock analysis).

## Handoff (cross-session, 2026-06-01)

- **Worktree**: `C:\Users\sshub\ai_sdlc-wt\slice-094-harden-vault-write-safety` on branch `slice/094-harden-vault-write-safety`. **master is clean** (5f13582); this slice's scaffolding + critique are committed on the slice branch.
- **Another session created `slice-095-harden-skill-driven-vault-writes/` + a `slice-queue.md` change on master's working tree** — that is NOT this slice's work; leave it for that session.
- **To continue**: run TRI-1 (ratify the Builder drafts in `critique.md` — B3 is drafted ESCALATED ⇒ verdict BLOCKED), then `/design-slice` to redesign per the scope above (or run `/critique-review` first if the rigorous path is preferred).
- **Build note (for after redesign)**: this worktree IS the BRANCH-2 worktree (NOT WORKTREE=skip) — per the slice-090/093 directive.

## Phase artifacts

- [mission-brief.md](mission-brief.md) — v1 (over-claims AC1/AC5; to be narrowed in redesign)
- [design.md](design.md) — v1 (BLOCKED; redesign required)
- [ADR-086](../../decisions/ADR-086-vault-write-safety-enforcement.md) — vault-write-safety enforcement (VWS-1) — to be revised (signatures + PCR-detection)
- [critique.md](critique.md) — **BLOCKED** (3B/4M/3m; Builder drafts written, TRI-1 pending)
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
