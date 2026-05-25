# Slice 046: add-conditional-repro-auto-advance

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: No formal risk-register entry. Retires a documented methodology friction — the BFRD-1 Step 3c STOP-route currently *punts* bug-fix slices back to the user ("run `/repro <issue>` yourself, then re-invoke `/slice`"), directly contradicting the PCA-1 (v0.41.0) auto-advance philosophy and the explicit user directive of 2026-05-19 (memory `repro-confirm-then-auto-invoke`).
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Bug-fix slices currently dead-end at `/slice` Step 3c: when BFRD-1 fires and no failing repro test exists, `/slice` HARD-STOPS and tells the user to go run `/repro` themselves. This slice reclassifies that STOP-route into a **conditional confirm-then-auto-invoke edge**: `/slice` distills the bug description, presents it for confirm/modify via structured options, then auto-invokes `/repro` itself with the confirmed string — removing the mechanical hand-off while preserving the only legitimate reason the gate existed (an auto-generated test reproducing the *wrong* failure signature, now mitigated by the lightweight confirm checkpoint). Codifies the standing user directive into the shared pipeline so the repo becomes canonical.

## Acceptance criteria

1. `skills/slice/SKILL.md` Step 3c "STOP-and-route behavior" is reclassified: when BFRD-1 fires and no failing repro test exists, `/slice` (a) distills the bug description, (b) presents it for confirm/modify via structured options (`AskUserQuestion`, per the `ask-via-structured-options` discipline), (c) auto-invokes `/repro` via the Skill tool with the confirmed/modified description, then continues — it NO LONGER emits the unconditional "run `/repro` yourself, then re-invoke `/slice`" hard-stop.
2. The pre-existing BFRD-1 verbal-claim-with-path fallback (user pastes an already-existing failing-test path) is preserved unchanged, and the fail-closed escape is preserved: if the user cannot confirm a bug description (e.g. "this is not a bug"), `/slice` does NOT silently auto-invoke `/repro` with an unconfirmed signature.
3. `skills/slice/SKILL.md`'s `## Pipeline position` block is updated so the Step 3c entry is the conditional confirm-gate (the confirm/modify prompt is the only remaining user-input gate for the bug-fix path; on confirm, auto-invoke proceeds) rather than an unconditional HALT-and-route; `tools/pipeline_chain_audit.py` still passes.
4. A new ADR (**ADR-048**) records the decision to reclassify the BFRD-1 STOP-route from an unconditional gate to a conditional confirm-then-auto-invoke edge; `methodology-changelog.md` gains a `v0.55.0` entry carrying a Rule reference; `VERSION`, `~/.claude/ai-sdlc-VERSION`, and `plugin.yaml` `version` are bumped to `0.55.0` in lockstep (PMI-1 atomic 4-part bump).
5. Self-hosting contracts hold: the installed `~/.claude/skills/slice/SKILL.md` is content-equal modulo line endings to the in-repo copy (mini-CAD for `slice` skill — `tests/methodology/test_slice_skill_drift.py` PASSES), and `tools.plugin_manifest_audit` (PMI-1) + `tools.install_audit` (INST-1) are clean.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Step 3c reclassified | Read `skills/slice/SKILL.md` Step 3c — assert the verbatim unconditional STOP block is replaced by the confirm-then-auto-invoke sequence; a content-pin test (slice-025 `test_critique_dim_*` pattern, NOT a byte-equality/CAD pin) greps for the new conditional behavior tokens and the absence of the old "re-invoke `/slice`" hard-stop string |
| 2 | Fallback + fail-closed preserved | Read Step 3c — assert the verbal-claim-with-path fallback paragraph still present; assert an explicit fail-closed clause covering "user cannot confirm a bug description" |
| 3 | Pipeline-position block coherent | `& $PY -m tools.pipeline_chain_audit` exits 0; manual read confirms the Step 3c user-input-gate entry now describes the confirm/modify gate, not HALT-and-route |
| 4 | ADR + changelog + version bump | `architecture/decisions/ADR-048-*.md` exists; `methodology-changelog.md` has a `## v0.55.0` section with a `Rule reference:` line; `VERSION` == `~/.claude/ai-sdlc-VERSION` == `plugin.yaml:version` == `0.55.0` |
| 5 | Self-hosting contracts | `& $PY -m pytest tests/methodology/test_slice_skill_drift.py` PASSES; `& $PY -m tools.plugin_manifest_audit` clean; `& $PY -m tools.install_audit` clean |

## Must-not-defer

- [ ] Fail-closed semantics: user declines/cannot-confirm a bug description ⇒ `/slice` must NOT auto-invoke `/repro` with an unconfirmed signature (this is the sole legitimate reason the original gate existed — preserve the protection, change only the delivery).
- [ ] BFRD-1 verbal-claim-with-path fallback remains available (do not delete the existing escape while reclassifying the primary path).
- [ ] One-way coupling preserved: `skills/repro/SKILL.md` is NOT modified by this slice (BFRD-1's documented one-way coupling).
- [ ] Methodology-behavior-change obligation discharged affirmatively: a `v0.55.0` changelog entry WITH a Rule reference + a new ADR + the PMI-1 4-part version bump — never an unjustified "no entry" (slice-029/034/040 precedent class).
- [ ] mini-CAD content-equality: install the edited `skills/slice/SKILL.md` to `~/.claude/skills/slice/SKILL.md` so `test_slice_skill_drift.py` stays green (EOL-agnostic per ADR-033).

## Out of scope

- slice-047 `add-two-scope-install` (user/project install scope) — separate, sequenced after this.
- Generalizing confirm-then-auto-invoke to OTHER pipeline STOP gates (TRI-1 triage, BLOCKED critique, plan-mode approval, mid-slice smoke, validate FAIL/PARTIAL) — this slice touches ONLY the BFRD-1 Step 3c bug-fix path.
- Modifying `/repro` itself or the BFRD-1 detection logic (sub-mode (a)/(b)) — only the post-detection STOP-route delivery changes.
- Building any new `AskUserQuestion` mechanism — the structured-options tool already exists; this slice only directs `/slice` to use it at Step 3c.

## Dependencies

- Prior slices: [[slice-045-fix-install-pypi-package-name-and-stale-prose]] — its Deferred section queued this as the next slice.
- User directive: memory `repro-confirm-then-auto-invoke` (2026-05-19) — the codification mandate; memory `ask-via-structured-options` — the confirm prompt must use structured options (free-text questions don't notify the user).
- Vault refs: [[methodology-changelog]] BFRD-1 (the discipline being reclassified), PCA-1 (v0.41.0 auto-advance philosophy this aligns with), [[decisions/ADR-033]] (EOL-agnostic content-equality for the mini-CAD pin).
- Skill refs: [[skills/repro/SKILL.md]] (one-way coupling consumer — read-only here), `skills/slice/SKILL.md` Step 3c + `## Pipeline position` (the edited surface).
- Risk register: none (no open risk retired; methodology-friction codification per standing user directive).

## Mid-slice smoke gate

At ~50% of build (Step 3c prose reclassified + Pipeline-position block edited, before ADR/changelog/version bump), run:
```
& $PY -m tools.pipeline_chain_audit
& $PY -m pytest tests/methodology/test_slice_skill_drift.py -q
```
Expected: `pipeline_chain_audit` exits 0 (block still well-formed); the drift test FAILS (in-repo edited, installed copy not yet synced — confirms the edit landed and the mini-CAD pin is live). If `pipeline_chain_audit` fails: STOP, the `## Pipeline position` block is malformed — diagnose before continuing. If the drift test PASSES at this point: STOP, the in-repo edit did not actually land.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (fail-closed, fallback, one-way coupling, changelog/ADR/version, mini-CAD install)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (pipeline_chain_audit 0; drift test PASSES after install)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 / INST-1 / CAD-1 / mini-CAD-slice / pipeline_chain_audit all green at Step 6
