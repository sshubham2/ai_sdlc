# Reflection: Slice 096 add-slice-candidates-drift-guard

**Date**: 2026-06-01
**Shipped**: YES-WITH-DEFERRALS

## Validated
- **OSDG-1 per-skill drift guard, cloned from the established idiom, works** — `tests/methodology/test_slice_candidates_skill_drift.py` collects, passes against the synced tree, and is non-vacuous (proven by mutation: temp-copy swap → FAIL on genuine divergence, restore → PASS, content-hash pre==post). The slice-032/033 `assert_md_forward_synced` reuse-as-is pattern held — a new guarded member is a pure new caller, no helper edit.
- **MEPD-1 = EXCLUDE was the correct disposition AND held end-to-end** — `git diff` confirms `VERSION` / `methodology-changelog.md` / `plugin.yaml` / `tools/install_audit.py` UNCHANGED at validation. Both Critic layers independently verified no methodology enforcer (changelog entry-pin, count-pin, version-gate `test_version_files_synchronized_at_v_0_78_0`) trips on an EXCLUDE slice-096.
- **Independence from the two in-flight parallel slices was real** — slice-096's code files (the new test) collide with nothing in 094 (`slice_queue_writer`/`claim`/`parallel_conflict_resolver`/VWS-1 audit) or 095 (skill-vault-write audit + vault-writing SKILL.md surfaces). `/slice-candidates` writes only `diagnose-out/`, so it sits outside 095's vault-path audit scope. The only shared surface was the additive `shippability.md` row (PCR-resolvable).

## Corrected
- **"17 existing per-skill drift tests" → 13** (reality). The "17" counted files matching `assert_md_forward_synced` — which includes the helper, the normalization test, and the agent-drift tests — not the 13 actual per-skill SKILL.md guards. Caught by the **code-Critic** (not the design stack). Corrected in `design.md:8,49`, `mission-brief.md:12,16,20`.
- **"final / lone previously-unguarded member" overstated set-completeness** → narrowed to "last named-but-unguarded member of THIS OSDG-1 family" with an explicit "NOT a total-coverage claim" (12 skills — `discover`, `risk-spike`, `validate-slice`, … — remain unguarded by design). Caught by the code-Critic against the real `skills/` tree. Corrected in `CLAUDE.md:42` (executable contract), `mission-brief.md:5`, `shippability.md` row 102.

## Discovered
- **D1 — stale active-path test pin from slice-093's archival** (pre-existing master breakage). `tests/methodology/test_external_vault_adr_and_risk.py:49` hard-codes `architecture/slices/slice-093-add-external-vault-support/design.md` (active path); slice-093 is archived → `FileNotFoundError` on clean master. NOT a slice-096 regression; out of scope (external-vault initiative / 094-095 domain). Impact: master's methodology suite has had a latent red since slice-093's merge; route the archive-aware fix to slice-094/095 or a maintenance slice. Added to risk register awareness via lessons.
- **D2 — R-20 worktree-seed gap recurred** (the slice-093 lesson). This worktree was created at `/slice` time with a plain `git worktree add`, which skipped `/build-slice`'s codified `cp -r diagnose-out/ graphify-out/` seed → `diagnose-out/backlog.md` absent → `test_bcr_1_*` false-failed until manually seeded mid-build. The systemic fix (seed at /slice-time worktree creation, or a shared worktree-create helper invoked by BOTH /slice and /build-slice) remains open from slice-093.
- **R-28 materialized — and in TWO distinct faces during this one slice** (now N=3 witnessed):
  1. **Shippability false-drift**: in-flight slice-095 forward-synced its unmerged `skills/reflect/SKILL.md` into the shared `~/.claude/` install (sha256 `F435D0…`, == slice-095's worktree, ≠ master/096/094's `CEF4B3…`), so slice-096's shippability `test_reflect_skill_drift` row reported drift on a skill slice-096 never touched. Fails on clean master too. User-approved deferral.
  2. **Running-skill-prose contamination** (new face): the `/reflect` skill the Skill tool loaded was slice-095's **installed** version, carrying slice-095's unmerged SVW-1 / ADR-087 prose that instructs `$PY -m tools.vault_edit append …` — but `tools/vault_edit.py` is NOT installed (slice-095 unmerged), so blindly following the installed prose would have CRASHED. The shared-install contention doesn't just break content-equality audits — it silently swaps the executable methodology a parallel slice runs.

## Deferred
- **D1 (external_vault stale pin)** — reason: out of slice-096 scope (094/095 external-vault domain; fixing here breaks independence). Lands in: slice-094/095 or a maintenance slice.
- **R-28 reflect shippability drift** — reason: not slice-096's regression; self-resolves when slice-095 merges. User-approved deferral (validation.md Step 5.5). Lands in: slice-095 merge / R-28 structural fix.
- **m2 (critique docstring mislabel in `parallel_conflict_resolver.py`)** — reason: pre-existing, slice-094's file, "refactors need a slice". Lands in: a future PCR-touching slice.

## Critic calibration

Per TRI-1, scored against `critique.md` → `## Triage` + reality:

- **M1 (false-precedent in EXCLUDE leg 2)**: VALIDATED — ACCEPTED-FIXED; the design DID rest on a vault-contradicting precedent claim; correcting it was right (the EXCLUDE verdict survived, confirming the meta-Critic's "safe disposition, wrong reason" read).
- **M2 (stale shippability id 101)**: VALIDATED — ACCEPTED-FIXED; reality (max id = 101 = slice-093) confirmed 101 was taken; build used 102.
- **M3 (shippability-merge HARD-STOP mischaracterization)**: NOT-YET — ACCEPTED-FIXED prose; the actual 3-way merge HARD-STOP only fires at `/commit-slice --merge` (re-score then). The meta-Critic independently confirmed the HARD-STOP is reachable (094+095 both append rows).
- **m1 (AC2 parity over-claim)**: VALIDATED — ACCEPTED-FIXED.
- **m2 (docstring)**: NOT-YET — DEFERRED.
- **m-add-1 (meta-Critic missed-finding: SCMD-1 6-column)**: VALIDATED — the new row genuinely needed the `Machine-cmd` column; SCMD-1 audit confirmed it post-build. The meta-Critic (EXTEND) earned its keep.

**Missed by design-Critic AND meta-Critic** (caught only by the **code-Critic**): the "17→13" count miscount and the "final/lone" completeness overstatement — both lived in the `design.md`/`mission-brief.md` prose the design stack reviewed, but neither layer verified the number against disk or scrutinized the completeness adjective. This is the **slice-037 audit-vs-real-artifact law** again: the design+meta stack structurally reasons about prose; the code-Critic verifies prose against the real tree. **Do NOT collapse the 3-Critic stack.**

**Pattern / `/critic-calibrate` candidate**: add a design-Critic heuristic — (a) verify any numeric count in design prose ("N existing X") against the actual artifact; (b) flag set-completeness adjectives (`final` / `lone` / `last` / `all` / `every` / `complete`) for unstated scope. Promote only if this miss recurs (N≥2).

## Lessons for next slice
- **R-28 is no longer theoretical — it bit a third slice, in two faces** (shippability false-drift + running-skill-prose swap). The shared single `~/.claude/` install under N parallel slices is a genuine hazard: it corrupts content-equality audits AND silently changes the methodology a slice executes. Strong candidate for a structural fix — per-worktree install isolation, or content-equality keyed to the slice's own base rather than the mutable shared global. Until fixed, expect shippability `test_*_skill_drift` false-drifts whenever a parallel slice forward-syncs a guarded SKILL.md.
- **Creating the worktree at `/slice` time silently drops the R-20 seed** (D2, recurrence of the slice-093 lesson). The next worktree-lifecycle slice should move the `cp -r diagnose-out/ graphify-out/` seed to `/slice`-time worktree creation (or a shared helper). Workaround this slice: manual seed at build.
- **The code-Critic catches a class the design+meta stack cannot** — prose-accuracy / count / completeness errors verified against the real tree. Confirms CRSI-1's value; the 3-Critic stack is load-bearing, not redundant.
- **MEPD-1 = EXCLUDE for a test-only guarded-set extension is clean and parallel-safe** — no VERSION/changelog churn keeps a slice off the high-contention coordination files, which is exactly what made slice-096 independent of 094/095. Extends the EXCLUDE precedent (N≥9) to the "pure member-add within already-settled rule scope" case.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — **R-13 flipped `open` → `retired`** (slice-096 shipped the OSDG-1 guard for `/slice-candidates`); **R-28** gains a witnessed-occurrence note (N=3, two faces).
- [[lessons-learned.md]] — slice-096 chronological entry appended.
- This slice's [[design.md]] / [[mission-brief.md]] — "17→13" count + "final/lone" overstatement corrected (build-log + code-review.md record the deltas).
- `architecture/shippability.md` row #102 — added at build (the slice's AC4 deliverable); Step 5.3 satisfied (no duplicate).
- **NOT used**: `tools.vault_edit` SVW-1 channel — `tools/vault_edit.py` is not installed (slice-095 unmerged); the vault is still in-git + per-worktree-isolated (no flip), so direct edit is safe and is master-methodology behavior.
