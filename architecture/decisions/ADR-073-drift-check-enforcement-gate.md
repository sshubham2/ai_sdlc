---
id: ADR-073
title: Enforce /drift-check-was-run as an audit-enforced gate at /build-slice Step 6 (DCE-1), procedural not semantic
date: 2026-05-29
slice: slice-081-fix-drift-check-enforcement-gap
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-073: Drift-Check Enforcement gate (DCE-1)

## Context

`/drift-check` is the only pipeline discipline that is *preached but not enforced*. CLAUDE.md's vault discipline says "Run `/drift-check` before commit"; the mission-brief template and `skills/build-slice/SKILL.md` Step 6 both list it. Yet — unlike every sibling discipline (BC-1 `tools/build_checks_audit`, PMI-1 `tools/plugin_manifest_audit`, CRP-1 `tools/critique_review_prerequisite_audit`, PCA-1 `tools/pipeline_chain_audit`, NAW-1 `tools/new_agent_warning_audit`, WIRE-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1) — `/drift-check` has:

- no `tools/drift_check_audit.py` (the only drift-named tool, `critique_agent_drift_audit.py`, is the unrelated CAD-1 Critic-agent content-equality check), and
- no installed pre-commit hook (the drift-check skill claims `/triage` installs one; `.git/hooks/` holds only `.sample` files).

So Step 6 carries only an honor-system `- [ ] /drift-check passes` checkbox. A slice can finish AND commit with the drift-check gate entirely unenforced — the R-7 / slice-022 "silent-disable" failure class that every other gate was structurally hardened against. The defect was user-reported and routed through `/repro` (BFRD-1): `tests/bugs/test_drift_check_enforcement_gap.py` (shippability row 86) fails until this gate exists.

A fundamental constraint shapes the fix: `/drift-check`'s core work is a **semantic** vault-vs-code comparison — reading ADR claims, design.md assertions, and must-not-defer items and judging them against code reality. That judgement cannot be replicated in a pure-Python audit. The mechanizable question is therefore not "is the vault correct?" but "**was the drift-check actually performed for this slice?**".

## Options considered

1. **Procedural "was-it-run" gate (CHOSEN)** — refuse `/build-slice` Step 6 unless the current slice left its drift-check marker in `architecture/drift-log.md`, with a documented escape-hatch and a MINIMAL-mode bypass. Mirrors CRP-1 exactly.
   - Pros: closes the *actual* gap (silent skip); zero false-positive surface (slice number is a unique freshness key); SMALL effort; reuses the existing `drift-log.md` marker convention and the proven CRP-1 template; honest about what can/can't be mechanized.
   - Cons: trusts Claude's semantic judgement of drift correctness (does not independently re-verify it). Accepted — that judgement is irreducibly Claude's, and the gap being closed is the skip, not the judgement.
2. **Mechanical-subset gate** — independently recompute the cheap mechanizable checks (ADR `status: accepted` library claims vs `pyproject.toml`; referenced source paths exist).
   - Pros: independent verification of a subset.
   - Cons: only the judgement-free subset; false-positive surface (renames); and — critically — it does NOT detect a silent skip, so it leaves the reported gap open. Rejected as not-closing-the-bug.
3. **Both (procedural + mechanical)** — A and B combined.
   - Pros: maximal coverage.
   - Cons: LARGE effort (risks >1 day / split); inherits B's false-positive surface; gold-plates a silent-skip fix. Rejected as over-engineered.

## Decision

Mint **DCE-1** (Drift-Check Enforcement): `tools/drift_check_audit.py`, an audit-enforced gate invoked at `skills/build-slice/SKILL.md` Step 6 AFTER `/drift-check` runs **in full mode** (only full mode writes the `drift-log.md` marker; `--fast` writes none).

**Scope honesty (per slice-081 /critique M2)**: DCE-1 is precisely a *was-it-**marked*** gate — it enforces that *a slice-referencing `drift-log.md` entry exists*, not that the semantic comparison was genuinely performed (a slice could in principle write the entry without doing the check). This residual gap is disclosed deliberately, mirroring NAW-1's known-false-positive disclosure; the structural hole it DOES close is the silent-skip (a slice finishing with no drift-check trace at all). The semantic correctness of drift detection remains Claude's irreducible judgement via the `/drift-check` skill.

**The git pre-commit hook remains out-of-scope** (per mission-brief; per slice-081 /critique m3): although the absent hook is cited in Context as part of the gap, DCE-1 enforces at `/build-slice` Step 6 only — it does NOT install a hook. The hook is a separate, deferrable decision.

It accepts (exit 0) when a `drift-log.md` entry references the current slice number, OR a canonical `drift-check-skip:` frontmatter key is present in the slice's `milestone.md` (value `^skip — rationale: .+`), OR the resolved mode is MINIMAL. It refuses (exit 1) with `drift-check-not-run` when mode ∈ {STANDARD, HEAVY} and no marker and no escape-hatch, or `escape-hatch-malformed` when the skip key is off-canonical. Bad invocation / unresolvable mode → exit 2 (fail-visible, never a false refuse). Mode resolves via `architecture/triage.md` frontmatter `mode:` → `CLAUDE.md` `**Mode**:` fallback. The gate is the bare `DCE-1` form (NON-`-D` per ADR-019 — it has a programmatic audit; naming-class peers BC-1 / CRP-1 / PCA-1 / NAW-1 / MCFS-1 / STP-1 / AVFS-1 / TVFS-1).

## Consequences

- `skills/build-slice/SKILL.md` Step 6 gains a DCE-1 audit sub-block; the bare `/drift-check` checkbox becomes an enforced HALT gate. Ordering is load-bearing: `/drift-check` (writes the marker) runs BEFORE `tools.drift_check_audit` (verifies it).
- `plugin.yaml` + `tools/install_audit.py` enumerate the new tool (PMI-1 / INST-1); 4-part version bump to v0.76.0 (MCFS-1 / AVFS-1 / TVFS-1).
- `milestone.md` frontmatter gains an optional `drift-check-skip:` key (additive, mirrors `critique-review-skip:`); `/build-slice` Step 7b must preserve it verbatim across continuous rewrites (same discipline as `critique-review-skip:` per ADR-024).
- `architecture/drift-log.md`'s existing `Trigger: slice-NNN …` line is now a load-bearing contract the gate parses; the `/drift-check` skill's full-mode output convention is unchanged but newly depended-upon.
- **Bootstrap (slice-081 only)**: the gate must discharge on its own build — `/drift-check` writes the `slice-081` marker before the audit runs at slice-081 Step 6 and exits 0. A non-zero before the drift-check run is the EXPECTED bootstrap signal, not a defect (CRP-1 slice-026 / PCA-1 slice-027 / NAW-1 slice-063 precedent). Every slice after 081 inherits a self-gating DCE-1.

## Reversibility

**cheap**. DCE-1 is a self-contained read-only audit + one Step 6 skill sub-block + manifest/registration entries. Reverting = delete `tools/drift_check_audit.py` + its tests, remove the Step 6 sub-block (restore the bare checkbox), drop the manifest/install/changelog entries, and supersede this ADR. No data model, no contract with external consumers, no irreversible state — a sub-1-hour reversal. The `drift-check-skip:` frontmatter key is additive and harmless if left behind.
