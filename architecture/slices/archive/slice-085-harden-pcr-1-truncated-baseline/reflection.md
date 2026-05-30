# Reflection: Slice 085 harden-pcr-1-truncated-baseline

**Date**: 2026-05-30
**Shipped**: YES

## Validated
- The tail-truncation-shape signal discriminates claim-loss-by-corruption from legitimate top-10 churn — validated by the real-resolver battery (AC-1 STOP on a tail-truncated baseline; AC-2 WARN+APPLIED on a well-formed orphan-drop; AC-3 APPLIED on a healthy short queue). The orphan-branch gate fires exactly where AC-1 demands and abstains everywhere AC-2/AC-3 forbid.
- `_RENDERED_FIELD_LABELS` is a **genuine** single source of truth (not SSoT-in-name) — validated by `test_format_entry_renders_from_rendered_field_labels_constant` (writer renders FROM the constant via zip) + `test_baseline_truncation_helper_uses_writer_field_label_constant` (monkeypatch proves the resolver reads the SAME object at call time). The code-Critic independently re-verified this empirically.
- The new STOP is atomic and composes with the pre-existing `:1775-1783` overlay-silent-drop STOP — validated by AC-4a (overlay STOP unchanged) + AC-4b (both-files-pending atomicity: no writes precede the STOP). The two branches are mutually exclusive (`claimed_names & baseline_headings` vs `claimed_names - baseline_headings`).
- Empty/`_(no candidates)_`/CRLF/trailing-space baselines do NOT false-STOP — validated by the AC-4d unit tests + a 9-input APED-1 executed battery.

## Corrected
- `design.md` §Contracts (`:46`) claimed this behavior change owes a "methodology-changelog entry + ADR (per MEPD-1)" — a stale draft remnant contradicting the ratified MEPD-1 **EXCLUDE** (ADR-077 §Consequences). **Corrected** in `design.md` (per /code-review M2) to the EXCLUDE statement. Code already matched EXCLUDE (no changelog/VERSION/plugin.yaml touched); the drift was doc→reality.
- No design *decision* was refuted — Option 4 (orphan-gated) shipped exactly as ratified. No ADR superseded.

## Discovered
- **Label-presence false-negative (code-Critic M1)**: `_baseline_is_truncation_shaped`'s per-line `^<label>` `re.search` treats a label as present if ANY line starts with that literal — so a corrupt baseline whose injected/spilled text begins with the *exact* missing field-label literal (e.g. `- **Risk-retired:** spillover` when the real field was truncated) masks the tail-truncation → no STOP. Unreachable from the canonical writer (values are scalars, never `- **`-prefixed continuation lines); only from a hand-edited/corrupt baseline — in-population but doubly-rare at low/low. **Recorded as R-24 residual (iv)** in risk-register + ADR-077. The durable fix (assert field-line SHAPE `^- \*\*\w[\w -]*:\*\*` rather than per-label literal presence) is a logged follow-up candidate.
- **VAULT_CLAIM sibling exposure (meta-Critic m-add-1)**: `resolve_vault_claim_conflict` carries the same baseline-truncation claim-loss exposure and never runs `_verify_soft_equivalence` — out of scope here, recorded as R-24 residual (iii), deferred to a future PCR-2a hardening.
- **Test-fixture footgun (self-caught at smoke)**: the AC-4b atomicity fixture initially used same-number shippability rows, which trigger a `_merge_shippability` HARD escalation STOP *independent* of the truncation gate — the test would have passed for the wrong reason (green without exercising the wiring). Caught at the mid-slice smoke gate by noticing AC-4b passed pre-wiring; fixed to distinct row numbers (SOFT-benign) so the only STOP cause is the truncation gate.

## Deferred
- **M1 invisible-claim case** (a claim that existed ONLY on the truncated baseline branch, claim lines cut → invisible to `merged_claims`) — TRI-1-ratified disposition (a): documented R-24 residual (ii), NOT closed. Doubly-rare; the meta-Critic's proposed per-claim (b) mechanism was itself flawed (would false-STOP the insert-new overlay path).
- **M1(a) durable fix** (field-line-shape check) — logged follow-up; lands in: backlog / a future PCR-1 hardening.
- **code-review minors m1–m4**: m1 cross-module `_RISK_RETIRED_PREFIX == _RENDERED_FIELD_LABELS[4]` pin test; m2 fail-closed-branch coverage (monkeypatch-raise test or `# pragma: no cover`); m3 test-filter `[:5]` shape-hardening; m4 end-to-end trailing-space-claimed-heading resolver-level pin. Lands in: backlog (cheap test-only hardenings).

## Critic calibration

Per TRI-1, scored against `critique.md` §Triage dispositions + reality observed at build/code-review/validate:

- **M1** (orphan branch leaves a claim-loss path uncovered): **VALIDATED** — disposition DEFERRED (document-as-residual). Reality confirmed the gap is real AND the code-Critic found an *additional* concrete instance (label-as-value-line, M1-code). The design-Critic's concern was correct; the slice's choice to document-not-close was a ratified scope decision, not a Critic miss.
- **M2** (nil-harm model omits the git commit): **VALIDATED** — disposition ACCEPTED-FIXED; the corrected "transiently-corrupt committed queue, eventually-consistent self-heal" harm model held up.
- **M3** (`_RENDERED_FIELD_LABELS` SSoT-in-name unless wired): **VALIDATED** — disposition ACCEPTED-PENDING; the code-Critic empirically confirmed the wiring genuinely closes SSoT (writer renders from it, resolver reads same object).
- **m1** (ratify Option 4 at TRI-1): **VALIDATED** — ACCEPTED-FIXED; Option 4 shipped with no false-STOP regression.
- **m2** (O(blocks×labels) bound): **VALIDATED** — ACCEPTED-FIXED; bound note present, helper is tail-block-only.
- **m3** (APED-1 executed battery): **VALIDATED-but-incomplete** — ACCEPTED-PENDING; the battery WAS written + executed, but it did NOT include the value-line-starting-with-label-literal false-negative input that the code-Critic's deeper probe (M1-code) surfaced. Calibration signal below.
- **m-add-1** (VAULT_CLAIM sibling residual): **NOT-YET** — deferred residual (iii); re-score if a future PCR-2a hardening addresses it.
- **m-add-2** (MEPD-1 discharge tracking): **VALIDATED** — ACCEPTED-FIXED; EXCLUDE determination recorded + gated.

**Missed by Critic**: the **design-Critic + the slice's own APED-1 battery both missed the label-as-value-line false-negative (M1-code)** — it was caught only by the **code-Critic** running its own adversarial probe battery against the live helper. This is textbook 3-persona complementarity: the design-Critic structurally cannot run the regex; the build-time battery was written by the same author who wrote the regex (shared blind spot); the independent code-Critic executing an independent corpus is the catch. Strongest calibration signal: **an APED-1 battery for a label/field *presence* check (per-line `^<literal>`) MUST include a false-negative input where a non-field/value/continuation line begins with the exact field literal** — presence ≠ field-line-shape.

**Pattern**: the BC-PROJ-13 family ("a newly-minted regex/parser needs an APED-1 adversarial-corpus battery, BOTH directions") fired again — but the *author-written* battery had a blind spot the *independent code-Critic* battery did not. The discipline isn't just "write a battery"; it's "an independent persona must author/run an adversarial battery against the literal," because the regex author and the battery author sharing a mental model produces a correlated blind spot.

## Lessons for next slice
- **A label/field *presence* regex (`^<literal>` per-line search) is not a field-line *shape* check** — a value/continuation line beginning with the literal masks a genuinely-missing field. When the gate's whole purpose is to detect a *missing* structural element, assert the element's SHAPE (`^- \*\*\w[\w -]*:\*\*`), not the presence of a specific literal string. (slice-085 / code-Critic M1)
- **The APED-1 battery author and the regex author sharing a mental model = a correlated blind spot** — the strongest false-negative (M1-code) slipped the build-time battery and was caught only by the independent code-Critic's own corpus. Treat the code-Critic's adversarial battery as a required second, independently-authored APED-1 pass for any newly-minted content-scanning regex — not a duplicate of the build-time one.
- **A two-file atomicity test can pass for the wrong reason** — when asserting "STOP leaves both files unmutated," ensure the *non-target* file's conflict is benign (SOFT-resolvable), or a spurious HARD escalation on it masks whether the *target* gate fired. Pin the STOP *cause*, not just the STOP. (slice-085 AC-4b smoke self-catch)
- **Self-validating-slice property N=6 on the parallel-slice family** (slice-077/078/082/083/084/085) — well past N=3; the "parallel-family slices dogfood their own `/commit-slice --merge`" codification candidate is now very ripe for `/critic-calibrate`.
- **MEPD-1 EXCLUDE for a risk-narrowing fix-slice with an ADR but no new RULE-ID is now N≥4** (slice-077/079/082/084 → slice-085) — the in-place-edit-to-already-manifested-tool class is a stable precedent; the EXCLUDE determination should perhaps itself be a build-check or a /critic-calibrate codification.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-24 `**Narrowed:** slice-085` annotation (residuals i–iv); Status stays open-downgraded. (R-25 was added earlier this slice during /critique — the main-thread-fabrication risk.)
- [[decisions/ADR-077-scope-pcr-1-baseline-integrity-to-claim-loss.md]] — §Consequences residual (iv) added per /code-review M1.
- This slice's [[design.md]] — §Contracts MEPD-1 clause corrected to EXCLUDE (per /code-review M2).
- [[drift-log.md]] — slice-085 CLEAN audit entry.
- [[shippability.md]] — new row pinning the claim-loss-by-truncation STOP (Step 5.3).
- [[lessons-learned.md]] — slice-085 entry.
- code-review.md minors m1–m4 + M1(a) durable fix logged as backlog candidates.
