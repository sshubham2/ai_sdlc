# Critique Review: Slice 077 enhance-pulse-with-worktree-awareness

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-28
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 19-finding review is unusually high in count for the recent run (slice-076 pass-1 was 16; slice-075 was 4) but on inspection, the count reflects genuine slice density — slice-077 carries multiple cross-document drift issues that the slice-076 lessons already flagged. **All 19 first-Critic findings are VALID** with correct severities — no SUSPICIOUS, no SEVERITY-WRONG. Three missed findings surface: M-add-1 (Cross-spec parity table claims a `Path(".").resolve()` default that PCR-1 does not actually use at parse-time); M-add-2 (mission-brief L5 "Risk retired" uses RR-1-reserved vocabulary without a corresponding R-NN entry — same shape slice-076 handled by registering R-21 at /design); M-add-3 (m4 N=2 framing under-counts the existing Python-side parser duplication — actual is N=3 post-slice-077, which IS Fowler's extract trigger).

## Confirmed findings (per-finding assessments)

- **B1 (TF-1 `(manual)` row)** — VALID; severity Blocker correct. Verified slice-076 reflection L24 verbatim says "any meta-row for end-to-end checks should be PENDING-by-design or removed". PTFCD-1 grammar verified at `tools/test_first_audit.py:476`. Builder fix (remove L50 row) correct.
- **B2 (copy-paste argparse flags)** — VALID; severity Blocker correct. Verified `tools/parallel_conflict_resolver.py:946-948` flags. Post-fix at design.md L89 cites `--detect + --classify` correctly.
- **B3 (predicate underspecification)** — VALID; severity Blocker correct. Mission-brief AC#4 enumerates 3 files; pre-fix ADR-070 narrowed to 1; post-fix at design.md L141-156 + ADR-070 L107-127 pins 3-file set + all-match + content-equal-modulo-EOL per ADR-033/EOL-DRIFT-1. EOL carve-out correctly inherits from CAD-1/OSDG-1.
- **B4 (ADR-070 reasoning artifact)** — VALID; severity Blocker correct. Post-fix L99 has single coherent paragraph on stuck-state-vs-advisory-backlog framing.
- **M1 (MEPD-1 precedent claim)** — VALID; severity Major correct; Builder OVERRIDE-via-honest-precedent-rewrite is the right call. Direct slice-074/075 archive inspection confirms zero new helper modules in either. Slice-076's PCR-1 IS load-bearing cross-skill (consumed at `skills/commit-slice/SKILL.md:204`); slice-077's WorktreeState taxonomy is `/pulse`-internal. Post-fix ADR-070 §"Honest precedent inspection" at L42-50 names the precedent stretch honestly. **Not OVERRIDE-MISJUDGED — the Builder's framing is sound.**
- **M2 (5 vs 6 test modules)** — VALID; severity Major (FBCD-1 sub-mode (a) count-vs-enumeration drift, slice-068+ pattern). Post-fix design.md L14 reads "6 new test modules".
- **M3 (UNKNOWN silently dropped)** — VALID; severity Major correct. Post-fix design.md L162-192 enumerates 8 UNKNOWN sub-reasons + WARN texts.
- **M4 (precedence-table incomplete)** — VALID; severity Major correct. Post-fix design.md L125-134 has all 8 cells of WorktreeState × CAL-1 product. Step-2 vs Step-3 location anchor explicit at L115.
- **M5 (revert under no-ff merge)** — VALID; severity Major correct. ADR-070 L155 cites `git revert -m 1 <slice-077-merge-commit-sha>`.
- **M6 (branch-name edge cases)** — VALID; severity Major correct. Verified `tools/branch_workflow_audit.py:81` `_SLICE_BRANCH_RE`. Post-fix design.md L173-176 enumerates no-suffix, rename-drift, prunable-stale, non-slice branches with explicit behavior.
- **M7 (cross-spec parity)** — VALID; severity Major correct. The queued `parallel-slice-family-parity-audit` is real at `architecture/slice-queue.md:41`. Post-fix design.md L194-208 pins parity table — but see M-add-1 below for one defect in this very table.
- **M8 (APED-1 floor)** — VALID; severity Major correct. Post-fix raises floor to ≥13 with enumerated cases. 28-case slice-076 precedent justifies.
- **M9 (RSAD-1 design-time pre-empt)** — VALID; severity Major correct. `cadence-overdue` literal verified at `skills/pulse/SKILL.md:88`. Post-fix design.md L212-231 adds prose-pin discipline table.
- **m1 (LOC band)** — VALID; severity Minor correct. Post-fix design.md L9 has honest comparison.
- **m2 (_index.md staleness)** — VALID; severity Minor correct. Defer disposition with rationale at design.md L247-248 is honest.
- **m3 (MERGED cleanup-candidate)** — VALID; severity Minor correct. Surfacing format pinned + persistence vectors (--push/--sync-after-pr) acknowledged at ADR-070 L68-77.
- **m4 (worktree-list parser duplication)** — VALID; **severity needs refinement to Minor** because the N-count framing is wrong (see M-add-3). The deferral is viable but the count claim needs correction.
- **m5 (WorktreeStateClassification vs WorktreeState)** — VALID; severity Minor correct. Resolved to dataclass-with-`.state`-accessor.
- **m6 (Step-2 state-dict contract)** — VALID; severity Minor correct. TF-1 plan now has `test_step_2_state_dict_includes_worktrees_field_with_worktreeinfo_list`.

## Suspicious findings

None — every first-Critic finding survives close inspection.

## Missed findings

### M-add-1: Cross-spec parity table claims `default=Path(".").resolve()` for PCR-1; actual is `default=Path(".")` (unresolved at parse time)

- **Location**: design.md L201 — "`default=Path(".").resolve()`; `type=Path` (matches PCR-1)".
- **Evidence**: `tools/parallel_conflict_resolver.py:950` reads `parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repo root (default: cwd)")`; `.resolve()` is applied POST-parse at L953 (`repo_root = args.repo_root.resolve()`).
- **Why it matters (Fowler/Newman cross-spec parity)**: per ADR-070 + design.md, the parity table is the load-bearing claim the queued `parallel-slice-family-parity-audit` slice will check. If design.md claims a default that PCR-1 doesn't use, the parity audit will EITHER (a) flag PCR-1 as the diverger from slice-077's claim — inverting the load-bearing direction — or (b) miss the parity violation entirely.
- **Proposed fix**: change design.md L201 to `default=Path(".")` (parse-time default); add a follow-on row that resolution is done post-parse via `args.repo_root.resolve()`, preserving the convention without misrepresenting PCR-1.
- **Severity recommendation**: **Major** (FBCD-1 sub-mode (a) cross-file consistency drift — same class as B2 which was Blocker; this one is Major because it's misleading rather than logic-breaking, and the table doesn't affect slice-077's own runtime).
- **Builder draft**: **ACCEPTED-FIXED** — fix at design.md L201 with both parse-time default + post-parse resolve clarification. Applied in-band before TRI-1.

### M-add-2: Mission-brief L5 "Risk retired" claims a class of correctness gap closed but no R-NN entry exists — RR-1 vocabulary collision

- **Location**: `mission-brief.md:5` — `**Risk retired**: skill-correctness gap surfaced 2026-05-28 during the post-slice-076 /pulse run.`
- **Evidence**: `architecture/risk-register.md` walked: entries R-1 through R-21; none describe the /pulse worktree-awareness gap. Mission-brief.md L85 itself acknowledges: "Risk register: no entry currently tracks the witnessed gap; /design may register an R-NN entry OR fold the witnessing into the slice's reflection as a Discovered-class observation." But L5 still uses the RR-1-reserved keyword **Risk retired** — which per RR-1 semantics means a prior R-NN flips to `status: retired`. Without a prior entry, nothing is being retired.
- **Why it matters (Sommerville requirements-traceability)**: the "Risk retired" frontmatter field is the trace-link from /reflect's RR-1 audit to slice charter. Without an R-NN, downstream tooling (`tools/risk_register_audit.py --filter-status retired`) cannot find the corresponding retirement; slice lifecycle metadata is permanently misaligned. Slice-076 set the precedent by registering R-21 at /design time for the exact-same-shape "newly discovered, status: open" case.
- **Proposed fix**: option (1) open R-22 (next free) at /design time with `Status: open` + `Discovered: slice-077 charter 2026-05-28` (the witnessing happened during slice-076's merge but the formal registration happens at slice-077's design phase) + `Mitigation: slice-077 closes this`; update mission-brief L5 to cite R-22. Option (2) rename frontmatter field to "Gap closed" / "Witnessed gap". Recommend option (1) — matches slice-076 R-21 precedent + provides the RR-1-conformant retirement at /reflect.
- **Severity recommendation**: **Major** (slice-charter-level RR-1 vocabulary discipline; downstream tooling load-bearing).
- **Builder draft**: **ACCEPTED-FIXED via option (1)** — register R-22 in `architecture/risk-register.md` with status: open; update mission-brief L5 to "Risk retired: R-22 (witnessed during slice-076 merge sequence)". Applied in-band before TRI-1.

### M-add-3: m4 N=2 framing under-counts the existing Python-side worktree-list-porcelain parser duplication (actual N=3 post-slice-077)

- **Location**: design.md L21 + L249 (m4 disposition).
- **Evidence**: grep `"git worktree list --porcelain"` across `tools/` returns:
  - `tools/slice_queue_writer.py:265` — Python subprocess parser (N=1 pre-slice-077)
  - `tools/branch_workflow_audit.py:333+359` — Python subprocess parser (N=2 pre-slice-077)
  - slice-077 adds `tools/pulse_worktree_resolver.py` — Python subprocess parser (N=3 post-slice-077)
  
  Plus shell-side instances in `skills/commit-slice/SKILL.md:202+204+284` (slice-075 lineage), but those are an orthogonal axis (bash awk vs Python subprocess).
- **Why it matters (Fowler "Rule of Three" — extract at N=3)**: the Builder's m4 disposition claims N=2 with the rationale "At N=2 this is acceptable per voluntary-restraint default (Fowler 'rule of three' — extract at N=3)". But the Python-side parser count is ALREADY N=2 BEFORE slice-077 (slice_queue_writer + branch_workflow_audit); slice-077 makes it N=3, which IS the extract trigger per Fowler. The deferral is still viable but the count claim is wrong.
- **Proposed fix**: re-frame m4 disposition as "N=3 cumulative Python-side parser duplication post-slice-077, deliberately stretched-but-deferred-with-honest-rationale: the queued `parallel-slice-family-parity-audit` (slice-queue head) is the natural extraction-trigger slice — extracting in slice-077 would expand scope to N=3 sites + a new shared helper module + 3 sets of consumer-test updates (≥6 additional files). Voluntary-restraint defers extraction to the parity-audit slice which will already touch all 3 sites." Update count in disposition.
- **Severity recommendation**: **Minor** (defer-with-honest-rationale is still viable; issue is count claim, not deferral itself).
- **Builder draft**: **ACCEPTED-FIXED** — update m4 in critique.md + design.md L21/L249 to N=3 framing with honest rationale. Applied in-band before TRI-1.

## Severity adjustments

None. All 19 first-Critic findings carry correct severities. (The first Critic's 4B/9M/6m split, despite unusually high count, reflects genuine cross-document drift density — mission-brief AC#4 + design.md predicate + ADR-070 + 6 test modules + cross-spec parity claim all needed coherence at the same time. Calibration risk on this slice was UNDER-reaching, not over-reaching.)

## Notes

- The three missed findings landed in the **post-fix-rewrite surfaces** (Cross-spec parity table + Risk-retired claim + m4 count framing) — exactly the per-slice second-opinion zone, since these sections either didn't exist or hadn't been re-examined at pass-1 review time.
- The mission-brief "Risk retired" RR-1 vocabulary mismatch is a slice-charter-level semantic gap worth surfacing as a potential `/critic-calibrate` signal if it recurs (RR-1-vocabulary discipline at mission-brief frontmatter level — first-Critic should have caught it at Dim 9 sub-clause cross-cutting conformance).
- The first Critic's framework alignment was exemplary on B1 (slice-076 lesson-propagation directly cited), B3 (CAD-1/OSDG-1 EOL-agnostic discipline correctly invoked), M1 (Wiegers precedent-inspection rigor with empirical archive inspection), M6 (Hendrickson edge-case enumeration), M9 (RSAD-1 N=3 cumulative pattern).
- Builder's in-band fix pass (4B+9M+5m ACCEPTED-FIXED with m2/m4 honestly DEFERRED) is structurally sound — all 18 surviving findings have correct application at cited line locations. The 3 missed findings are now ACCEPTED-FIXED in-band before TRI-1.
