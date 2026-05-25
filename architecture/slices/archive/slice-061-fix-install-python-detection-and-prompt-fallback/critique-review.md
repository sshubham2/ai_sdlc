# Critique Review: Slice 061 fix-install-python-detection-and-prompt-fallback

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-23
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

(12 first-Critic findings: 1 Blocker B1 + 8 Majors M1–M8 + 3 Minors m1–m3; all ACCEPTED-FIXED in Builder draft. Meta-Critic adds M-add-1 + m-add-1.)

## Summary

The first Critic's 12 findings are substantively correct and the draft fixes already applied to design.md + mission-brief.md are well-shaped. However, a second-pass independent re-application of the 8 dimensions surfaces **one Major the first Critic missed** (the in-loop `/code-review` skill's in-scope-paths list does not enumerate `INSTALL.md`, so slice-061's primary artifact will silently fall outside slice-060's code-review surface unless wired) **and one Minor** (the M5 validation block's `"$user_path"` is bound by Claude's conversational-state substitution, but the prose contract never names that mechanism — the same prose-templating question the B1 fix faced, left unsaid for M5). One severity adjustment considered (M7) and discharged — Major is appropriate. No findings I'd demote.

## Confirmed findings (VALID, severity-correct)

All 12 first-Critic findings: VALIDATED, severity correct, ACCEPTED-FIXED disposition appropriate.

- **B1** (`$BOOT_PYTHON` cross-bash) — VALID Blocker; INSTALL.md fenced bash blocks at L46/L115/L135/L152/L164/L196/L252 are each separate `bash -c` invocations. Inline-recompute fix is robust.
- **M1** (unbounded "I'll wait") — VALID Major; option-removal-on-retry IS the enforcement mechanism.
- **M2** (abort-path wording) — VALID Major; original wording was qualified-true for current invocation but misleading on re-runs (L227 contemplates partial-config carry-over from prior Steps 3d/3e/3h).
- **M3** (AC4 section-scoping) — VALID Major; parallels existing `_step_3a_section`/`_step_2_section` helpers; slice-058-class false-green prevented.
- **M4** (PowerShell routing) — VALID Major; user's global CLAUDE.md PowerShell-preference makes the routing ambiguity material; bash-fence + Bash-tool routing is load-bearing.
- **M5** (`>= 3.10` hardcoded) — VALID Major; slice-058 / BC-PROJ-11 lesson re-applied; combined dynamic-grep + L71 sibling-drop is FBCD-1 sibling-coverage correct.
- **M6** (R-17 canonical surface) — VALID Major; aggregated-lessons L131 generalizes to all risk-register surfaces.
- **M7** (R-16 broader class) — VALID Major; original prose scope (Windows/macOS/Linux) was narrower than the fix's coverage (conda-only / NixOS / Termux / Docker). Notes paragraph correctly anchors second-platform reports as NEW R-NN, not re-opens. slice-057/R-15 Notes-pattern precedent.
- **M8** (MEPD-1(b) discharge-by-assertion) — VALID Major; slice-040/045/053 lineage applied correctly.
- **m1** (WIRE-1 honor-system) — VALID Minor; `wiring_matrix_audit.py:275-284` parses only for `rationale:` substring.
- **m2** (ADR criteria mechanical) — VALID Minor; strengthened SOAD-1 + BFRD-1 framing is correct.
- **m3** (installer-suggestion minor literals) — VALID Minor; same class as M5; version-agnostic rewording correct.

## Suspicious findings (over-reach challenged)

**None.** Specifically challenged:

- **M7 was NOT over-reach.** Without the Notes paragraph, a future Termux/NixOS/Docker user-report would be ambiguous (re-open R-16 or file new?). The Notes paragraph resolves declaratively. slice-057/R-15 lineage applied correctly.
- **M2 wording WAS genuinely misleading.** "Steps 0/1/2 are read-only" conflated "this invocation" with "all possible invocations". INSTALL.md L227-L231 explicitly documents partial-state re-runs. Reworded contract is materially less misleading and adds the load-bearing "abort path must NOT clean up pre-existing state" constraint.

## Missed findings (added by meta-Critic via independent dimension re-application)

### M-add-1 (Major): INSTALL.md is NOT in `/code-review`'s in-scope-paths list — slice-061's primary artifact silently falls outside slice-060's code-review surface

- **Dimension**: Cross-cutting conformance + Drift from vault.
- **Claim under review**: design.md "Components touched" §L37-L44 names `INSTALL.md` as the primary artifact-of-change. The slice auto-advances from `/build-slice` → `/code-review` per slice-060's PCA-1 canonical-chain extension (8→9 entries).
- **Issue**: Per `skills/code-review/SKILL.md:48-55`, the in-scope paths enumerate `skills/**/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `tests/**/*.py`, and root-level config files `plugin.yaml | pyproject.toml | VERSION | methodology-changelog.md` — **`INSTALL.md` is NOT in either the in-scope OR the explicit out-of-scope list**. The auto-advance to `/code-review` will compute the filtered diff via `git diff $base...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'` — INSTALL.md WILL appear in the diff (not excluded), but the code-Critic agent's prompt focuses on the listed paths; INSTALL.md prose-contract review will be ambiguous-coverage at best, silently-omitted at worst. The slice-060 design's M3 rationale ("skill prose IS executable contract") applies AT LEAST AS STRONGLY to INSTALL.md (the INST-1 install recipe Claude executes literally) as to plugin.yaml or methodology-changelog.md.
- **Evidence**: `skills/code-review/SKILL.md:48-55` in-scope path list; design.md L37-L44 names INSTALL.md as principal artifact-of-change; PCA-1 canonical chain at `tools/pipeline_chain_audit.py:73-82` includes `/code-review` between `/build-slice` and `/validate-slice`. Per Newman (Building Microservices, contract surfaces) + Sommerville (drift from stated contract).
- **Why first Critic missed**: the first Critic checked the slice's internal design but did not check the slice's downstream interaction with the just-shipped slice-060 `/code-review` chain edge. This is the canonical RSAD-1 / slice-046 "first Critic blind to novel control-flow edges" pattern applied to a cross-slice adjacency (slice-060 + slice-061).
- **Proposed fix — TWO OPTIONS for user TRI-1 decision**:
  - **Option (a)**: document explicitly in slice-061 design.md that INSTALL.md falls under the "Root-level config files" in-scope category by analogy (since plugin.yaml + pyproject.toml + VERSION + methodology-changelog.md are listed and INSTALL.md is the same kind of root-level methodology artifact). Surface this as a slice-062 nomination to formally extend `/code-review`'s in-scope list.
  - **Option (b)**: note explicitly that INSTALL.md prose review is out-of-scope for `/code-review` v1 (advisory only) and rely on the AC1–3 prose-pin tests + slice-045's `test_install_md_correctness.py` + INST-1 audit (via `tools/install_audit.py`) as the structural review surfaces. Add a one-line note to design.md naming this as the deliberate scope-narrowing decision.
- **Disposition**: pending — user decides at TRI-1.

### m-add-1 (Minor): M5 validation block's `"$user_path"` + `"$AI_SDLC_DIR"` binding mechanism unnamed in prose contract

- **Dimension**: Unfounded assumptions.
- **Claim under review**: design.md "What's new" Step 2 path-validation entry specifies `test -x "$user_path"` + `"$user_path" -c "..."` + `MIN_PY=$(grep -E '^requires-python' "$AI_SDLC_DIR/pyproject.toml" ...)`.
- **Issue**: `$user_path` is bound by Claude substituting the user's structured-options response into the bash command before invocation, NOT by a shell variable assigned in the same bash process. Same applies to `$AI_SDLC_DIR/pyproject.toml` — works in practice because INSTALL.md L137-L141 / L153 already use the `$AI_SDLC_DIR`-as-conversational-state pattern. This is the SAME prose-templating-vs-shell-variable distinction the B1 fix encountered for `$BOOT_PYTHON`. The first Critic's B1 fix chose inline-recompute to bypass the cross-invocation persistence question entirely; M5's `$user_path` is bypassing the SAME question by an unstated "Claude substitutes the user's path" mechanism. Internally consistent with existing INSTALL.md patterns (`$AI_SDLC_DIR` works on L137-L141 / L153) — not broken, just unnamed.
- **Evidence**: INSTALL.md L137 `mkdir -p ~/.claude/skills ~/.claude/agents ~/.claude/templates && cp -r "$AI_SDLC_DIR/skills/"* ~/.claude/skills/` already uses `$AI_SDLC_DIR` in a bash invocation distinct from Step 0's binding — the working precedent. design.md L13-L16 validation block uses the same pattern without naming the mechanism.
- **Why first Critic missed**: applied the B1 scrutiny to `$BOOT_PYTHON` but did not check the M5 fix's own use of `$AI_SDLC_DIR` + `$user_path` against the same B1 dimension. Same dimension, sibling surface, missed by sibling-coverage gap.
- **Proposed fix**: add one sentence to design.md Error model recovery path 1: "`$user_path` is bound by Claude substituting the user's structured-options response into the bash command before invocation (same prose-templating pattern as the existing `$AI_SDLC_DIR` references at INSTALL.md L137-L141 / L153); not a cross-bash-invocation shell-variable channel." Makes the mechanism explicit; forecloses future B1-class scrutiny against M5.
- **Disposition**: ACCEPTED-FIXED (draft) — one-sentence prose addition; mechanically clear; no user-decision required at TRI-1. Will be applied to design.md after TRI-1 ratifies the meta-Critic's findings.

## Severity adjustments

**None.** All 12 first-Critic findings carry the right severity (B1 Blocker; M1–M8 Majors; m1–m3 Minors). The two missed findings sit at Major (M-add-1: cross-slice surface-coverage gap) and Minor (m-add-1: documentation gap on internally-consistent pattern).

## Candidate misses discharged

The other candidate-misses I attacked and discharged (per user's adversarial prompt):

- **R-16 + R-17 born-in-same-slice scope**: discharged. Different lifecycles (R-16 born-retired; R-17 born-open-mitigating). Slice-045 R-11 precedent + standard discovered-risk-record on canonical surface = appropriately-scoped.
- **Shippability row #61 wired pre-build vs AC4 PENDING**: discharged. Row cites file-level path (not function-level); AC4 will be authored mid-slice and the row passes at `/validate-slice`.
- **SOAD-1 self-application of 3-option ASK**: discharged. The 3-option form IS structured options; AC2 pins SOAD-1 conformance.
- **Slice's heavy bash idioms vs user CLAUDE.md PowerShell-prefer**: partially discharged. M4 fix handles validation block; INSTALL.md's existing bash idioms at L47-L51 already establish the Git-Bash-on-Windows pattern. User's CLAUDE.md preference is for ad-hoc shell work, not for executing a recipe whose authored idioms are bash.
- **`$AI_SDLC_DIR` in M5 fix is a fresh B1 instance**: partially discharged → folded into m-add-1. The mechanism is internally consistent with INSTALL.md L137-L141 / L153 working precedent, but the prose contract never names it.

## Notes

Meta-Critic confidence:
- **High** on the 12 confirmed first-Critic findings (mechanism-traced, file-line-cited, lineage-correct).
- **Medium-high** on M-add-1 (mechanically verifiable that `skills/code-review/SKILL.md:48-55` does not list INSTALL.md; practical impact depends on slice-061-as-first-/code-review-governed-INSTALL.md-slice — a slice-060-coverage-edge first-fire).
- **Medium** on m-add-1 (internally consistent with `$AI_SDLC_DIR` precedent; lower-stakes documentation gap rather than load-bearing contract gap).

**Calibration observation**: the first Critic ran a comprehensive 12-finding pass with strong mechanism-tracing (B1 / M5 / M6 / M8 all assertion-grep / file-line-cited) and slice-058 / slice-057 / slice-045 lineage correctly applied. The blind spot is the **slice-060 + slice-061 adjacency**: slice-060 SHIPPED `/code-review` whose in-scope-paths list was authored before INSTALL.md was the slice-061 surface; slice-061 is the first slice where the omission matters in practice. This is exactly the "novel control-flow edge" RSAD-1 / slice-046 lineage warned to attack — the first Critic checked the slice's internal design but did not check downstream interaction with the just-shipped chain edge. The missed finding is **surgical** (single-line scope list omission) not bulk, consistent with the slice-053 / slice-057 zero-false-alarm-precision pattern for codification-class neighborhoods.

No reservations on the ACCEPTED-FIXED disposition for all 12 first-Critic findings. The two missed findings should route through TRI-1 — M-add-1 carries TWO valid resolution options (a/b) requiring user judgment; m-add-1 carries a clear one-sentence-add ACCEPTED-FIXED draft.
