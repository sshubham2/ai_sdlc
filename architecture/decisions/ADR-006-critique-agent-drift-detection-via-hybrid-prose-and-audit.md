---
id: ADR-006
title: Adopt option (d) hybrid — skill-prose update + standalone CAD-1 audit — for in-repo↔installed drift on agents/critique.md
date: 2026-05-10
slice: slice-007-add-critique-agent-content-equality-audit
reversibility: cheap
status: accepted
---

# ADR-006: Hybrid (c+a) for critique-agent in-repo↔installed drift detection

## Context

Slice-006 discovered (per `architecture/slices/archive/slice-006-update-critic-with-cross-cutting-conformance-dimension/reflection.md` Discovered section + Critic B1 finding) that the Meta-Critic skill `/critic-calibrate` instructs accepted-proposal application against the **installed** `~/.claude/agents/critique.md` only — see `skills/critic-calibrate/SKILL.md:107-114`. The in-repo `agents/critique.md` is the canonical source per project conventions, but no skill-prose nor audit enforces this; every `/critic-calibrate` ACCEPTED proposal that follows the current prose creates content drift between in-repo and installed copies.

Slice-006 itself was the first instance where this drift was observed (the surgical Dim 1 + Dim 4 sub-bullets accepted at the 2026-05-10 calibration run existed only in `~/.claude/agents/critique.md`, never propagated back to in-repo until slice-006 Phase 1 back-synced them). Slice-006's Critic B1 caught the drift incidentally — voluntary Critic happened to read implementation rather than docs. Methodology must not depend on incidental human-Critic discipline for a structural defect that is N=1 visible (slice-006) and N=∞ projected (every future calibration run).

A decision is needed because:

1. The slice-006 reflection explicitly named this as the **strongest slice-007 candidate by structural-fix-class importance**, with three named option families:
   - (a) standalone `tools/critique_agent_drift_audit.py` content-equality check
   - (b) INST-2 extension to `tools/install_audit.py` covering all installed files
   - (c) update `skills/critic-calibrate/SKILL.md:108-109` prose to instruct in-repo edits with manual forward-sync
   - (d) hybrid combinations
2. Without a recorded option choice, future maintainers seeing the slice-007 deliverables won't understand WHY one of (a/b/c/d) was picked — equivalent to slice-006's situation before ADR-005 landed.
3. The choice constrains follow-on slices: option (b) commits the project to extending INST-1's scope; option (a) creates a sibling audit family; option (c) alone defers detection.

## Options considered

1. **Option (a) standalone `tools/critique_agent_drift_audit.py` only** — narrow audit module covering only `agents/critique.md`; no skill-prose change.
   - Pros: minimal scope; clean module separation from INST-1; preserves INST-1's source-independence design contract; can be extended later if drift recurs on other files.
   - Cons: doesn't fix the SOURCE of recurrence — the `/critic-calibrate` skill prose continues telling users to edit only the installed copy. Audit catches drift but every `/critic-calibrate` run still creates new drift before audit runs. User must remember to invoke the audit; missed invocation = silent drift.
   - Verdict: **rejected** — leaves the recurrence pattern intact; treats symptom, not cause.

2. **Option (b) INST-2 extension of `tools/install_audit.py` with content-equality** — add a content-equality mode to install_audit covering all installed files vs in-repo equivalents.
   - Pros: most general; one tool for all in-repo↔installed drift; aligns with INST-1's existing `_CANONICAL_*` lists; future drift on `~/.claude/build-checks.md`, agents, skill SKILL.md files all caught by one audit.
   - Cons: violates INST-1's core design contract — INST-1 was scoped to allow the audit to run *after* the source folder is deleted (per `methodology-changelog.md` v0.20.0 INST-1 description: "the AI SDLC source folder can be deleted after install with no functional impact"). Content-equality requires both source-folder copy AND installed copy present at audit time. INST-2 must therefore be a SEPARATE audit class (separate module, separate `--repo-root` flag) — not a true extension. Effort ~60-90 min just for the refactor; over-scoped for slice-007's recurrence pattern (1 file, not N files).
   - Additional concern: INST-1's `_CANONICAL_*` lists track installed-file conventions (skill folder + SKILL.md, agent file, template file, metadata file). The mapping from `_CANONICAL_*` entry to in-repo path is implicit (e.g., `_CANONICAL_AGENTS` entry `critique` ↔ in-repo `agents/critique.md` ↔ installed `~/.claude/agents/critique.md`). This mapping has to be made explicit before content-equality works. That's a non-trivial refactor with cross-module ripple risk.
   - Verdict: **deferred** to a future slice if/when drift recurs on files other than `agents/critique.md` (N=2 promotion threshold for INST-2). Slice-007 narrowly closes the N=1 visible case.

3. **Option (c) skill-prose update only** — change `skills/critic-calibrate/SKILL.md:107-114` prose to instruct in-repo edits with manual forward-sync; no audit added.
   - Pros: cheapest (~10-15 min); fixes the source of recurrence without adding code; structural prevention.
   - Cons: doesn't catch existing drift — the slice-006-back-synced copy could re-drift on the next `/critic-calibrate` run if a future user edits the installed copy directly (e.g., from a different machine, or because they forgot the prose). Doesn't have a test gate; relies on humans/agents reading prose correctly; impossible to run as a CI check.
   - Verdict: **rejected as standalone** — necessary but not sufficient.

4. **Option (d) hybrid (c+a) — skill-prose update PLUS standalone CAD-1 audit** — combine (c) and (a).
   - Pros: prose addresses the recurrence at its source (preventive); audit catches anything the prose doesn't prevent (detective); both validated via tests; both generalize cleanly when extended to other files later. Effort ~45-60 min total. The two halves are independently valuable: prose correction stands alone if the audit is later folded into INST-2; audit stands alone if the prose drifts.
   - Cons: two surfaces to maintain instead of one. Mitigated by `tests/methodology/test_critique_agent_drift.py` pinning the prose contract.
   - Verdict: **accepted**.

5. **Option (d) hybrid (c+b) — skill-prose update PLUS INST-2 extension** — most general; covers all in-repo↔installed pairs.
   - Pros: addresses both the slice-006 recurrence AND any future drift class with one slice.
   - Cons: same INST-2 design-contract violation as Option (b); effort ~75-105 min total; over-scoped for the N=1 evidence base.
   - Verdict: **rejected** — wait for N=2 evidence before extending INST-1's design contract.

## Decision

Adopt **Option (d) hybrid: (c) skill-prose update + (a) standalone `tools/critique_agent_drift_audit.py` audit (rule reference CAD-1)**. The skill-prose update at `skills/critic-calibrate/SKILL.md:107-114` instructs in-repo `agents/critique.md` as canonical with manual forward-sync to installed; the audit verifies sha256 byte-equality between the two copies. Both pinned by `tests/methodology/test_critique_agent_drift.py`. New methodology-changelog entry `v0.22.0 — CAD-1` documents the rule + validation method. Plugin manifest (`plugin.yaml`) and INST-1 canonical inventory (`tools/install_audit.py:_CANONICAL_TOOLS`) updated atomically (14 → 15 tool entries) to register the new audit as a canonical tool module.

## Consequences

- **Forward**: Every future `/critic-calibrate` ACCEPTED proposal now follows the corrected prose (in-repo edit + forward-sync) AND is detectable by `tools.critique_agent_drift_audit` if the prose is ignored. Recurrence pattern closed at the source.
- **Sibling generalization**: If drift on a SECOND file (e.g., `agents/critique-review.md`, `agents/critic-calibrate.md`, `~/.claude/build-checks.md`) is observed, slice-007's audit module is the template — clone with different paths, OR consolidate via INST-2 at N=2.
- **Plugin manifest co-evolution**: The slice's `_CANONICAL_TOOLS` 14 → 15 update means future re-runs of `tools/plugin_manifest_audit.py` (PMI-1) and `tools/install_audit.py` (INST-1) will treat the new audit as canonical — surfaces missing if not pip-installed.
- **Explicit fix to slice-006 escape (gated by AC #5 per Critic B2)**: `plugin.yaml.version` was lagging at `0.20.0` while in-repo `VERSION` (renamed to `ai-sdlc-VERSION` at install per `INSTALL.md:141`) was `0.21.0` — a PMI-1 violation slice-006 left behind. **Verified empirically post-Critic**: pre-slice-007 `python -m tools.plugin_manifest_audit --root .` exits 1 with `version-mismatch`. Slice-007's version bump to `0.22.0` corrects both atomically AND adds AC #5 + must-not-defer entry + TF-1 row that gates the fix at /build-slice pre-finish. Without the gate (which Critic B2 surfaced), the slice would have left another slice-006-style escape behind. Captured in slice-007 reflection's "Discovered" as a slice-006 Critic-MISSED with sub-class promotion candidate (design.md mechanical tables vs canonical references at N=2 per Critic B1).
- **Backward**: existing test suite expanded by ~4 tests in `test_critique_agent_drift.py`; existing tests unaffected. Shippability catalog grows by 1 critical-path entry.

## Reversibility

**Cheap.** Reverting the slice requires:
1. `git revert` of the slice's commit (unstages all changes including audit module + skill-prose + changelog + version bumps).
2. Re-run `pip install --upgrade $AI_SDLC_DIR` to remove `tools.critique_agent_drift_audit` from the installed package.
3. Manual revert of `~/.claude/skills/critic-calibrate/SKILL.md`, `~/.claude/methodology-changelog.md`, `~/.claude/ai-sdlc-VERSION` (forward-sync rollback) — sha256-equal to pre-slice state stored in `build-log.md` as recovery anchor.

Total: ~15 min mechanical work. No downstream consumers of `CAD-1` exist outside this slice; no other slices have shipped depending on the audit's existence. Compare to ADR-005 (slice-006) which was tagged **expensive** because the cumulative slice-006-N critique outputs filed under Dim 9 are irreversible — slice-007 has no such cumulative effect because the audit is internal tooling, not a pattern-recognition surface filed against in archived critiques.

### Items that cannot be cleanly reverted (per Critic m2 — matching ADR-005 enumeration standard)

1. **Methodology-changelog audit-trail entries** are append-only by convention; revert leaves a gap row but the dated `## v0.22.0 — 2026-05-10 — CAD-1` entry remains in git history. This is acceptable per existing methodology-changelog conventions.
2. **`build-log.md` sha256 forensic captures** for `~/.claude/agents/critique.md`, `~/.claude/skills/critic-calibrate/SKILL.md`, `~/.claude/methodology-changelog.md`, and `~/.claude/ai-sdlc-VERSION` are append-only per slice-005 + slice-006 forensic-capture discipline; revert leaves the captured hashes in build-log history.
3. **Reflections in slices ≥008 that cite CAD-1** are textually persistent — once a future slice's `reflection.md` mentions `CAD-1` rule reference (e.g., as a precedent for an INST-2 generalization), revert leaves dangling references. Mitigated only by an explicit `/supersede-slice` of the citing slice.
4. **Git history of the `plugin.yaml.version` jump from 0.20.0 → 0.22.0** (skipping 0.21.0 in plugin.yaml) — the slice-006 escape correction means future maintainers reading `git log -- plugin.yaml` see a non-monotonic version history. This is the empirical artifact of the slice-006 escape; revert does not undo the historical anomaly.
5. **The 14 → 15 `_CANONICAL_TOOLS` entry count** is reversible mechanically (re-delete the entry from both `tools/install_audit.py` and `plugin.yaml`), but `tests/methodology/test_install_audit.py::test_canonical_tools_match_plugin_yaml` will then verify a 14-tool inventory — meaning every downstream pip-install will re-resolve `tools.critique_agent_drift_audit` as missing (post-revert), surfacing as INST-1 violation. Reverting cleanly requires also reverting the `~/.claude/` installed copy via `pip install --upgrade ai-sdlc-tools` after the revert commit.
