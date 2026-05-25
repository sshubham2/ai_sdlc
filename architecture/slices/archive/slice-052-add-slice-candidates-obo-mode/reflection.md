# Reflection: Slice 052 add-slice-candidates-obo-mode

**Date**: 2026-05-20
**Shipped**: YES-WITH-DEFERRALS (the one logged deferral — OSDG-1 extension to `/slice-candidates` — is a deliberate own-slice deferral per slice-049/051 precedent, recorded as R-13 + a next-slice nomination, not a must-not-defer slip)

## Validated

- **AC1–5** all PASS with evidence (`validation.md`): severity ordering critical→high→medium→medium stable within band; default no-flag path unchanged (no traceback, classic "No Confirmed=yes" SystemExit); 5-option `AskUserQuestion` + live progress + scoped `--obo-peek` + ADR-054 carve-out + faithful `diagnosis.annotated.html` + resume predicate `id ∉ annotations` + Deferred-terminal-with-reopen-path.
- **B1 / B2 / M1 / M2 / M3 / M4 / M-add-1 / M-add-2 / m1 (now Major)** all VALIDATED — each is now pinned by a passing test in `tests/methodology/test_slice_candidates_obo.py` that would FAIL under the rejected alternative (e.g. `test_obo_write_ensure_ascii_false` fails without B1's fix; `test_obo_write_m_add_2_backslash_and_close_byte_exact` fails under a `re.sub`-based implementation). Operational parity backlog.md==golden held; Hard-rule-#3 SHA-256 invariance held; `--obo-peek` Path.resolve() containment refused every evasion class (5 parametrized cases: secret/sibling/`../`/absolute/`./`).
- **Critic-prompt APED-1 discipline** held (slice-050 lesson): the first Critic empirically executed both Python and JS serializations to ground B1/B2 — exactly what slice-050's "Builder false-precedent guard reconfirmed N+1" + the project's APED-1 culture asked for, and the meta-Critic kept that ground while extending it (M-add-2 traced the payload one hop further into the in-place substitution mechanic).
- **Branch-per-slice (BRANCH-1)** held: slice/052-add-slice-candidates-obo-mode created cleanly from master with the untracked `diagnose-out/` carrying through harmlessly; BRANCH-1 audit clean at pre-finish.

## Corrected

- **`design.md` / `mission-brief` "plugin-manifest / drift posture unaffected" claim** → reality is that ADR-054 + a new user-facing skill mode IS a methodology-surface behavior change per the changelog Inclusion heuristic + the slice-049/ADR-051 law. Corrected mid-build: applied the v0.60.0 4-part PMI-1 bump (changelog `## v0.60.0` + VERSION 0.59.0→0.60.0 + plugin.yaml + forward-synced installed `~/.claude/ai-sdlc-VERSION` + `~/.claude/methodology-changelog.md`) + the conventional `test_v_0_60_0_obo_{entry_present_in_repo,shippability_consumer_propagation}` pair. `design.md` "What's new" updated with the bump rationale + deviation note; `build-log.md` records the DEVIATION explicitly.
- **Pre-existing `build_backlog.py` `main()` stdout (and stderr) UTF-8 crash class** → discovered at T1 fixture-golden generation: the existing entrypoint didn't reconfigure stdout, so `--obo-extract`'s non-ASCII JSON would have inherited the same Windows `charmap` crash. Stderr also crashes — `SystemExit` refusal messages contain em-dashes. Fixed at the shared `_reconfigure_stdout()` entrypoint (reconfigures BOTH streams). Console-encoding-only fix; `backlog.md` bytes byte-identical (AC4 golden proves it). Logged DEVIATION in `build-log.md`; AC1 default-path-unchanged-output contract preserved.

## Discovered

- **N=2 recurrence of the "methodology-bump misclassified as PMI-1 artifact-enumeration unaffected" class** (slice-049 B2 + slice-052 missed-by-both-Critics): the slice-049 aggregated lesson stating "a drift-guard family member-addition whose slice has no other bump reason IS a methodology-surface behavior change → ## vN + 4-part PMI-1 bump path; NOT the rode-an-existing-bump non-precedent" was never converted into a Builder-side gate or Critic-prompt dimension, so it recurred at slice-052. **Promoted to BC-PROJ-10** this slice (BCI-1 fixture + live byte-equal; integrity audit PASS). Strong `/critic-calibrate` input for a Critic-prompt dimension extension (the BC-PROJ-10 Builder-side gate is the structural backstop; the Critic-prompt dimension closes the human-judgement axis).
- **Subprocess child UTF-8 capture discipline**: any test/harness invoking `build_backlog.py` from a parent Python on Windows MUST pass `encoding="utf-8"` to `subprocess.run` — the parent's cp1252 default mis-decodes the child's correct UTF-8 emoji bytes. NOT a tool defect; codified into the `tests/methodology/test_slice_candidates_obo.py` `run()` helper. Worth surfacing for future test authors — flagged here, not promoted (too narrow for BC-1).
- **Annotated-copy parity contract is fundamentally an *operational* invariant, not a byte-invariant** (B2 reframing): the browser `Save annotated HTML` does `'<!DOCTYPE html>\n' + document.documentElement.outerHTML` (`assemble.py` L1712) — a full DOM re-serialization the engine normalizes (attribute order, whitespace, entities). Reproducing that from Python is unreproducible *and* irrelevant: the only consumer (`parse_html_state` L42-63) reads only the embedded `diagnose-data` script block. Lesson: when reaching for "byte-faithful to the browser output", the right test is the consumer-end byte-equality (`backlog.md` == golden) + the `parse_html_state` annotation-set equality, not a whole-file diff. Worth carrying into any future browser↔Python parity contracts.

## Deferred

- **OSDG-1 drift-guard extension to `/slice-candidates`** — deliberate own-slice deferral per slice-049/051 precedent (drift-guard *addition* takes its own dedicated slice + own Critic pass; folding `test_slice_candidates_skill_drift.py` into a feature slice would be the "while I'm here" scope creep the brownfield rules forbid). Recorded as `risk-register.md` R-13 (status: open, next-slice candidate). The lock-step install sync WAS done this slice (`~/.claude/skills/slice-candidates/{SKILL.md,build_backlog.py}` content-equal mod EOL); only the *automated guard* is deferred. Strong next-slice candidate.

## Critic calibration

Per TRI-1: every finding's disposition reconciled against reality observed during build/validate. critique.md's `## Triage` table:

| ID | Disposition | Reality at build/validate | Score |
|----|-------------|---------------------------|-------|
| B1 (`json.dumps` `ensure_ascii=True` divergence) | ACCEPTED-FIXED | `test_obo_write_ensure_ascii_false` would FAIL under the rejected alternative; the annotated bytes carry raw `café`/`💡` (not `é`/`\ud83d`). | **VALIDATED** |
| B2 (parity target is whole-doc outerHTML, redefine operationally) | ACCEPTED-FIXED | Browser DOM re-serialization is unreproducible from Python (L1712); script-block-substitute strategy is the right impl; operational parity `backlog.md` == golden held end-to-end. | **VALIDATED** |
| M1 (`collect()` key-order + absent-not-empty) | ACCEPTED-FIXED | Untouched `F-med-2-aaaa1111` ABSENT from annotations (not `{confirmed:"",notes:""}`); `confirmed_findings` L91-108 re-sorts so key-order is non-contractual. | **VALIDATED** |
| M2 (resume predicate `id ∉ annotations`; Deferred not re-offered) | ACCEPTED-FIXED | Deferred entry IS in annotations (`confirmed:"defer"`), so resume skips it; never-reached entry IS absent, so it's first on resume. Tests confirm. | **VALIDATED** |
| M3 (`test-first:false` indefensible for deterministic helpers) | ACCEPTED-FIXED | The 16-test golden harness IS what would have caught a B1/B2/M-add-2 silent-divergence regression at build time. Without M3, the helpers would have shipped without that pin. | **VALIDATED** |
| M4 (mechanical scoped-peek via `--obo-peek`, not honour-system) | ACCEPTED-FIXED | 5 parametrized evasion-class tests PASS via `Path.resolve()` containment; honour-system prose alone would not have been auditable. | **VALIDATED** |
| M-add-1 (Defer-terminal-on-resume documented reopen path) | ACCEPTED-FIXED | Defer is by-design terminal for resume but is now documented in operator-facing SKILL.md prose (not a silent trap). | **VALIDATED** |
| M-add-2 (step-5 insertion is match-span slicing, NOT `re.sub`) | ACCEPTED-FIXED | `test_obo_write_m_add_2_backslash_and_close_byte_exact` PASSES under match-span slice insertion; a `re.sub` implementation would corrupt `\` + `</script>` in the JSON payload via Python's special replacement-string handling (`\g<…>`, `\1`, bare backslashes). | **VALIDATED** |
| m1 → Major (`parse_html_state` non-greedy first-bound; duplicate-block silently consumed) | ACCEPTED-FIXED, severity bumped Minor→Major (user-ratified) | `test_obo_extract_refuses_duplicate_data_block` PASSES via NEW `re.findall`-count detection; the severity bump correctly recorded the silent-correctness-corruption class (M-add-2-adjacent — a partial/aborted write would produce exactly this duplicate state). | **VALIDATED** |

**No FALSE-ALARM, no OVERRIDE-MISJUDGED, no NOT-YET.** 9 / 9 first-Critic + meta-Critic findings VALIDATED — the strongest dual-Critic outcome on this project's record (alongside slice-050 B/M VALIDATED rate). 

**Missed by Critic** (the calibration gold):
- **The v0.60.0 4-part PMI-1 bump was missed by BOTH Critic layers** (high-confidence; N=2 with slice-049 B2). Both first Critic and meta-Critic reviewed mission-brief's "plugin-manifest / drift posture unaffected" claim and design.md's "no new registered artifact" framing without flagging that ADR-054 + a new skill mode trips the changelog Inclusion heuristic. The slice-049 aggregated lesson naming this exact class existed but was never mined into a Critic-prompt dimension — so it recurred. **Promoted to BC-PROJ-10 this slice** (Builder-side gate); the residual Critic-prompt-dimension axis is strong `/critic-calibrate` input.
- **Pre-existing `build_backlog.py` stdout/stderr crash class on Windows** (low-confidence; not a recurring pattern): neither Critic noticed that `--obo-extract` emits non-ASCII finding text to stdout and would inherit the pre-existing `main()` crash, nor that `SystemExit` refusal messages with em-dashes crash on stderr. Discovered immediately at T1 + fixed in-band; not Critic-promptable (it required reading the existing `build_backlog.py main()` and reasoning about the shared entrypoint, which the dual-Critic stack did partially do — the design's mention of "default path unchanged" set up the misframe). Logged here, not promoted (too narrow).

**Pattern**: the first Critic's recurring strength is **APED-1 rigor on executed serializations** (B1/B2 empirically driven). The recurring blind spot remains **methodology-bump classification for a slice that mints an ADR + a new skill capability but no new RULE-ID / no new registered artifact** — N=2 (slice-049 B2 + slice-052 missed). BC-PROJ-10 is the Builder-side close; the slice-049/052 corpus is the `/critic-calibrate` input.

## Lessons for next slice

- **The slice-049/052 missed-by-Critic N=2 pattern is now backstopped by BC-PROJ-10** (Builder-side gate at /critique-time; promoted this slice; BCI-1 fixture+live byte-equal). Future slices that mint a new ADR or add a user-facing skill capability/mode MUST carry an explicit `Inclusion heuristic` / `bump-required` / `MEPD-1(b) why-none discharged` classification in mission-brief.md or design.md before /critique. Strong `/critic-calibrate` input remains for a Critic-prompt-dimension extension to close the human-judgement axis as well.
- **OSDG-1 extension to `/slice-candidates` is the strongest next-slice candidate** — R-13 (open) + the slice-049/051 verbatim member-addition shape (clone `assert_md_forward_synced` + 4-part PMI-1 bump + content-bearing v-entry-pin + CLAUDE.md enumeration + one shippability row). The lock-step sync this slice did is the *manual* control; the automated guard closes the loop.
- **Golden-test discipline for silent-divergence contracts** held strongly: any future parity/serialization/in-place-substitution contract should default to `**Test-first**: true` for the deterministic helpers OR (as here) carry a mandatory `tests/methodology/test_*_obo.py`-class golden harness. The 16-test harness caught what the dual-Critic stack also caught — but the test would have caught it if the Critic had missed.
- **Subprocess child UTF-8 capture is now a documented test convention** — codified in `test_slice_candidates_obo.py`'s `run()` helper. Future tests invoking UTF-8-reconfigured children from a Windows parent MUST pass `encoding="utf-8"` to `subprocess.run`.
- **Plan-mode self-application discipline reconfirmed N+1** (slice-044 BC-PROJ-8 lineage): the design-incompleteness halt mid-build caught the bump-classification miss before shipping. Halting + structured-options surfacing + user ratification was the right cost vs silently expanding scope OR silently shipping non-conformant.

## Vault updates made (thin vault)

- `architecture/decisions/ADR-054-scoped-source-peek-for-slice-candidates-obo-validate.md` — new, status: accepted, reversibility: cheap, supersedes: null (mechanical `--obo-peek` containment).
- `architecture/risk-register.md` — added R-12 (Hard-rule-#2 controlled relaxation, mitigating) + R-13 (OSDG-1 not yet extended, open next-slice candidate).
- `architecture/shippability.md` — row #52 (this slice's regression critical path).
- `architecture/build-checks.md` — promoted BC-PROJ-10 (per Step 5b; BCI-1 fixture + live byte-equal; integrity audit PASS).
- `tests/methodology/fixtures/build_checks/canonical_project_checks.md` — byte-copied from live (BCI-1 fixture-as-oracle).
- `architecture/drift-log.md` — appended the slice-052 drift-check audit (0 blockers / 0 majors).
- `methodology-changelog.md` (+`## v0.60.0`) + `~/.claude/methodology-changelog.md` (forward-sync).
- `VERSION` 0.59.0→0.60.0; `plugin.yaml` version 0.60.0; `~/.claude/ai-sdlc-VERSION` 0.60.0 (forward-sync).
- This slice's `design.md` corrected mid-build (the "drift posture unaffected" framing addendum + deviation note); `build-log.md` records both DEVIATIONS (shared-entrypoint stdout/stderr reconfigure + v0.60.0 bump scope correction).
