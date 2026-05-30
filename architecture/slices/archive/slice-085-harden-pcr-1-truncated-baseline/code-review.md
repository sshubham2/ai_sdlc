# Code Review: Slice 085 harden-pcr-1-truncated-baseline

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-30
**Result**: FINDINGS
**Reviewer**: `code-review` agent (separate code-Critic persona; read the live worktree source + executed an APED-1 probe battery against `_baseline_is_truncation_shaped`)

## Summary
A tightly-scoped, well-engineered risk-narrowing slice. The truncation-shape discriminator fires exactly where AC-1 demands and abstains where AC-2/AC-3 forbid; the SSoT wiring genuinely closes M3 (verified empirically — writer renders from the constant at `:667`, resolver reads the same object at `:1729`); the battery passes and exercises the real resolver against real tmp-repo rebase conflicts (not mock-faked). Findings: **0 blockers, 2 majors, 4 minors** — the majors are a confirmed false-negative class in the label-presence regex (M1) and a stale design.md/ADR-077 MEPD-1 contradiction (M2).

## Changed files (in-scope)
```
tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py
tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py
tests/methodology/test_slice_queue_writer.py
tools/parallel_conflict_resolver.py
tools/slice_queue_writer.py
```
(build-log.md is post-build vault prose; not reviewed as code.)

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None. The harm-gate fires correctly on every AC-1 fixture, abstains on every AC-2/AC-3/AC-4d fixture, and the atomicity test (AC-4b) confirms no writes precede the STOP. No broken contract, no injection vector, no ADR contradiction in the code itself.

### Majors

#### M1: `^` + `re.escape(label)` label-presence search has a confirmed false-negative — a value line beginning with a label literal masks a real tail-truncation
- **Claim under review**: `tools/parallel_conflict_resolver.py:1730-1733` — `missing = [label for label in labels if not _re.search("^" + _re.escape(label), last_block, _re.MULTILINE)]`.
- **Issue**: The helper decides a label is "present" iff *any* line in the last block starts with that label literal — it does not distinguish a genuine field line from a continuation/value line that happens to start with the same literal. Adversarial last block (executed against the worktree): real `Source/Blast-radius/Parallel-safety/Effort` present, real `Risk-retired` field truncated away, but a value spilled onto a new line beginning `- **Risk-retired:** spillover` → probe `FN2` returned `(False, None)`. The genuinely tail-truncated baseline is judged WELL-FORMED → the claim-loss STOP does NOT fire → AC-1's harm gate is bypassed for this shape.
- **Evidence**: The canonical PSQ-1 writer never emits a value containing a leading-`- **`-prefixed continuation line (values are scalars / single-line backtick-joined cells), so this cannot arise from the writer — only from a hand-edited or genuinely-corrupt baseline, which is precisely the R-24/ADR-077 threat population. The false-negative lives *inside* the population the gate exists to catch.
- **Severity rationale**: Major not Blocker — the precondition (corruption injecting a line starting with the *exact* missing label literal) is doubly-rare and lands SAFE-by-luck only on that coincidence; any other corruption shape still STOPs (AC-1 test + probe "heading-only tail" → True). Real, in-population, and not in the design's residual list.
- **Proposed fix**: (a) tighten to a field-line *shape* check `^- \*\*\w[\w -]*:\*\*` rather than per-label literal search (durable); OR (b) document as a 4th R-24 residual in `risk-register.md` + ADR-077 §Consequences (proportionate at low/low under the cooperative model).
- **Disposition (Builder)**: **(b) APPLIED this slice** — added residual (iv) to R-24 `**Narrowed:**` + ADR-077 §Consequences. (a) the durable field-shape tightening is logged as a follow-up candidate (a cheap, well-bounded hardening, but a code+test change beyond this slice's ratified Option-4 scope). Consistent with the slice's established narrowing-with-honest-residuals thesis.

#### M2: Internal contradiction — design.md:46 asserts "methodology-changelog entry + ADR (per MEPD-1)" while ADR-077 + mission-brief assert MEPD-1 EXCLUDE
- **Claim under review**: `design.md:46`: *"…this is a **behavior change** → methodology-changelog entry + ADR (per MEPD-1)."* vs `ADR-077` §Consequences: *"MEPD-1 EXCLUDE … no methodology-changelog entry, no VERSION bump, no PMI-1 bump."*
- **Issue**: Two in-slice vault artifacts make opposed claims about whether a changelog entry is owed. The design.md sentence is a stale draft remnant predating the /critique-review m-add-2 EXCLUDE determination. The CODE matches EXCLUDE (changed-files set contains no `methodology-changelog.md`/`VERSION`/`plugin.yaml`), so the drift is design.md→reality, but per the brownfield "don't carry forward stale design claims" rule it is a logged discrepancy that would otherwise archive as a live contradiction.
- **Proposed fix**: Align design.md:46 to the ratified EXCLUDE.
- **Disposition (Builder)**: **APPLIED this slice** — design.md:46 rewritten to the EXCLUDE statement citing ADR-077 §Consequences.

### Minors
- **m1**: `slice_queue_claim._RISK_RETIRED_PREFIX` (:109) is a documented-but-untested drift twin of `_RENDERED_FIELD_LABELS[4]`; `parse_queue_text`/overlay key on the independent literal. Proposed: a one-line cross-module pin `assert slice_queue_claim._RISK_RETIRED_PREFIX == slice_queue_writer._RENDERED_FIELD_LABELS[4]`. **Disposition**: logged for /reflect (cheap test-only hardening; converts the prose "by intent" NOTE into an enforced invariant).
- **m2**: the `except Exception` fail-closed branch (`:1856`) is correct posture but currently unreachable (the helper body has no raising op on `str|None`), so it is unexercised defensive code. Proposed: a monkeypatch test making the helper raise + assert STOP, or `# pragma: no cover`. **Disposition**: logged for /reflect.
- **m3**: `test_format_entry_renders_from_rendered_field_labels_constant` field-prefix filter silently depends on `_ITEM` being claim-less; would break confusingly if claim keys are added. Proposed: slice to `[:5]` or add a comment. **Disposition**: logged for /reflect (cosmetic).
- **m4**: AC-4d trailing-space-heading is asserted only on the helper, not end-to-end through `_verify_soft_equivalence` (where the `:1805` `.strip()` prevents the slice-082-class orphan-branch bypass). Proposed: a resolver-level trailing-space-claimed-heading fixture. **Disposition**: logged for /reflect (closes a known historical bypass class at the integration level).

## Dimensions checked
- [x] Unfounded assumptions — m2 (unreachable fail-closed branch). Docstring claims verified empirically (probes A–F + AC-4d battery); no phantom imports (`_baseline_is_truncation_shaped` @:1690, `_RENDERED_FIELD_LABELS` @ writer:129 both import; 20 tests pass).
- [x] Missing edge cases — **M1** (label-as-value-line false-negative, confirmed by execution). Empty/placeholder/CRLF/trailing-space/heading-only all probed. EOL-DRIFT-1: helper CRLF-normalizes before any compare (`:1719`).
- [x] Over-engineering — none. One helper + one constant + one branch; the constant extraction removes a duplicated literal.
- [x] Under-engineering — none material. Every AC has a delivering code element AND a passing test (AC-1..AC-5 enumerated).
- [x] Contract gaps — none. Helper fully type-hinted with a thorough contract docstring; `_fail` correctly `NoReturn`.
- [x] Security — none. ADR-067 cooperative-not-adversarial; no auth/input boundary; `re` built from a module-internal constant via `re.escape` (no user-controlled regex); `subprocess.run` list-args.
- [x] Drift from vault — **M2** (design.md:46 vs ADR-077 EXCLUDE). Otherwise code matches design.md components, the zero-row wiring matrix, and ADR-077's wiring; EXCLUDE correctly reflected in the diff.
- [x] Web-known issues — none applicable. Skipped targeted WebSearch: no external SDK/API; only stdlib `re` (stable multiline anchors) + `git` subprocess list-args; `str | None` floor-3.10-safe.
- [x] Cross-cutting conformance — m1 (`_RISK_RETIRED_PREFIX` twin), m4 (trailing-space end-to-end pin). APED-1: the new parse rule WAS executed against an adversarial battery — M1 is the one member that slipped the slice's own tests. RSAD-1: the slice's own canonical block is judged not-truncation-shaped (probe F → False). The new orphan-branch STOP composes correctly with the pre-existing `:1828` claimed-WITH-heading STOP (mutually exclusive sets; AC-4a pins it unchanged).
