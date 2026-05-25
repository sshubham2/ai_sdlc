---
slice: slice-007-add-critique-agent-content-equality-audit
stage: complete
updated: 2026-05-10
next-action: none (slice complete)
risk-tier: low
critic-required: true
---

# Milestone: slice-007 add-critique-agent-content-equality-audit

**Stage**: complete
**Next action**: none (slice complete; auto-archived)
**Updated**: 2026-05-10
**Risk tier**: low — Critic required: yes (cross-cutting tooling slice; per slice-006 reflection lesson #2). critic-required: true even though tier is low.

## Progress

- [x] /slice — 2026-05-10
- [x] /design-slice — 2026-05-10
- [x] /critique — 2026-05-10 — CLEAN (8 findings: 2 blockers + 3 majors + 3 minors; ALL ratified ACCEPTED-FIXED inline → mechanical verdict CLEAN per triage_audit)
- [x] /build-slice — 2026-05-10 — SHIPPED-WITH-DEFERRALS (all 5 ACs PASS, 7/7 TF-1 PASSING, 366/366 full suite, BC-1 N=3 false-positive deferred-with-rationale)
- [x] /validate-slice — 2026-05-10 — PASS (5/5 ACs PASS via real CLI invocations; VAL-1 Layer A 0 secrets + Layer B 0 hallucinated imports; shippability catalog 62/62 in 3.0s; 3 reality surprises captured for /reflect)
- [x] /reflect — 2026-05-10 — Slice shipped. Lessons captured. Auto-archiving next.

## Current focus

Critique complete. **CLEAN verdict** — all 8 findings ratified ACCEPTED-FIXED inline at /critique time; no ACCEPTED-PENDING/ESCALATED rows so the triage_audit's mechanical verdict-pattern check resolves to CLEAN. Mission-brief grew 4 → 5 ACs (at /slice's hard limit per AC #5 added by Critic B2 to gate the slice-006 PMI-1 escape).

**Critic findings summary (N=8, all ACCEPTED-FIXED):**
- **B1**: VERSION naming — in-repo file is `VERSION`, not `ai-sdlc-VERSION` (the `ai-sdlc-` prefix is added at install per `INSTALL.md:141`). Recurrence of slice-006 DEVIATION-1+2 cross-cutting class at **N=2** — meets aggregated lessons' "promote to Dim 9 sub-clause when N=2" threshold. Fix applied across design.md (Out-of-repo table + What's new + Components touched + Empirical verification #4) + mission-brief AC #4 + ADR-006.
- **B2**: AC set didn't gate the slice-006 PMI-1 escape that ADR-006 claimed to fix. Empirically verified pre-slice: `python -m tools.plugin_manifest_audit --root .` exits 1 with `version-mismatch ('0.20.0' vs '0.21.0')`. Fix: added AC #5 (PMI-1 clean post-build), verification-plan row 5, must-not-defer entry, TF-1 row.
- **M1**: `--repo-root` is an extension beyond `install_audit.py`, not a mirror (verified `install_audit.py:339-352` has only `--claude-dir`, `--strict`, `--no-strict`, `--json`). Fix: design.md Components touched section pins `--repo-root` as new extension; fixture contract pinned (tmp_path/repo + tmp_path/claude with synthetic `plugin.yaml` + `INSTALL.md` for sanity check).
- **M2**: Line-range pin `107-114` is too brittle. Fix: replaced with substring-only assertion + negative substring per slice-006 prose-pin precedent.
- **M3**: Stale `build/lib/` shadow risk (verified `git status: ?? build/`). Fix: added `usage-error` (exit 2) sanity-check refusal when `--repo-root` lacks `plugin.yaml` + `INSTALL.md`. New TF-1 row 3c.
- **m1**: `_CANONICAL_TOOLS` shorthand vs literals. Fix: design.md Empirical verification #3 uses `tools.X` literals.
- **m2**: ADR-006 reversibility section thin vs ADR-005 standard. Fix: expanded to enumerate 5 irreversibles (methodology-changelog, build-log forensics, future-slice citations, git history non-monotonicity, `_CANONICAL_TOOLS` count).
- **m3**: AC #1 verification command Bash-tool-wrapper incompat. Fix: parenthetical added + agent-runnable equivalent.

**Calibration signal**: Cross-cutting conformance Dim 9 paid off — Critic B1 + M1 + m1 are all Dim 9 sub-class hits surfaced because the dimension prompted the check. Slice-006's user-override-of-Meta-Critic effectiveness target (≤2 cross-cutting misses across slices 6-15) is on track at slice-007: 0 NEW misses (all caught), 1 promotion-eligible recurrence (B1 design.md-table-vs-canonical-inventory at N=2). To be recorded in slice-007 reflection's calibration log effectiveness section.

**TF-1 plan grew 5 → 7 rows** post-critique (added rows for AC #3c sanity-check refusal + AC #5 PMI-1 cleanliness):
1. AC #1: test_in_repo_and_installed_critique_agent_are_content_equal
2. AC #2: test_drift_detection_fires_on_artificial_byte_flip
3. AC #3a (prose): test_critic_calibrate_skill_prose_instructs_in_repo_canonical_with_forward_sync
4. AC #3b (CLI): test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing
5. AC #3c (sanity): test_repo_root_without_plugin_yaml_or_install_md_exits_usage_error
6. AC #4: test_v_0_22_0_cad_1_entry_present_in_repo_and_installed
7. AC #5: test_plugin_yaml_version_matches_version_file_at_0_22_0

## On resume

- **Last completed action**: /critique (NEEDS-FIXES verdict; all 8 findings ratified ACCEPTED-FIXED inline; design.md + ADR-006 + mission-brief.md updated; TF-1 plan grew 5 → 7 rows)
- **Current work**: none
- **Next immediate step**: run `/build-slice`. Mission-brief now has 5 ACs and 7 TF-1 rows. /build-slice Phase 0 should run sha256 checkpoints on `~/.claude/agents/critique.md`, `~/.claude/skills/critic-calibrate/SKILL.md`, `~/.claude/ai-sdlc-VERSION`, `~/.claude/methodology-changelog.md` BEFORE any edits per slice-005+006 forensic-capture discipline.

## Phase artifacts

- [mission-brief.md](mission-brief.md) — 5 ACs; TF-1 plan 7 rows; verification plan 5 rows; must-not-defer 7 entries
- [design.md](design.md) — option (d) locked; mechanical tables corrected per Critic B1 + m1; error model has 4 cases per Critic M3; CLI flags pinned per Critic M1
- [critique.md](critique.md) — 8 findings (2B + 3M + 3m); NEEDS-FIXES with all ACCEPTED-FIXED inline
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending

## ADRs

- [[ADR-006]] (`architecture/decisions/ADR-006-critique-agent-drift-detection-via-hybrid-prose-and-audit.md`) — Adopt option (d) hybrid (c+a); reject INST-2 as over-scoped; reversibility: cheap with 5 enumerated irreversibles
