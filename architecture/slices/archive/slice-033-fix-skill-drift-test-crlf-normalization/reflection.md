# Reflection: Slice 033 fix-skill-drift-test-crlf-normalization

**Date**: 2026-05-17
**Shipped**: YES

## Validated
- The shared EOL-agnostic comparator retires R-5 environment-independently — validated: 5 skill-drift modules + CAD-1 = 13 passed under `core.autocrlf=true`; the pre-existing failing repro (`971e2326…` vs `aaab3190…`) now PASSES; synthetic CRLF-vs-LF `_normalized_sha256` equal = True.
- ADR-033's load-bearing claim "git blobs already LF → `git add --renormalize` index diff is empty" — validated empirically: `git ls-files --eol` showed `i/lf w/crlf`, renormalize produced an empty `git diff --cached`, `git diff HEAD -- skills/ agents/` EMPTY.
- M2 must-not-mask binding held: existing CAD-1 `test_drift_detection_fires_on_artificial_byte_flip` + CLI exit-code matrix stayed green (still exit 1 on `# v1`/`# v2`) after `_sha256_of` normalization — the safety property survives the relaxation.
- Shippability 32/32 PASS — no past slice regressed (incl. R-5 rows #1: 41 passed, #19: 12 passed).

## Corrected
- None at build time. The design's mid-flight corrections (4→5 ACs, CAD-1 in scope, `.gitattributes`+renormalize, RULE-ID `EOL-DRIFT-1`) all landed during the /critique→/critique-review→TRI-1 loop and were already in design.md/ADR-033/mission-brief before /build-slice. The design held through build with zero deviation.

## Discovered
- **M1's concern materialized exactly as flagged**: `.gitattributes eol=lf` + `git add --renormalize` updated the index but did NOT rewrite the already-CRLF working tree — a scoped `rm + git checkout --` was required to materialize LF. The `test_guarded_md_files_have_no_crlf_in_working_tree` working-tree-STATE check (M1 ACCEPTED-FIXED) caught the gap that a `git check-attr` declaration check would have missed. Reality confirmed the Critic.
- **R-7 silent-bypass reproduced LIVE at /build-slice pre-finish (N+1 since slice-031)** — the mission-brief `**Test-first**: true  (per TF-1 — …)` trailing parenthetical broke `test_first_audit.py`'s `\s*$`-anchored regex → TF-1 silently default-off-bypassed. Caught ONLY by the BC-PROJ-4 discipline (run every affected gate on the real artifact at pre-finish + read its output: "not enabled" on a test-first slice = silent-bypass alarm). Fixed in-slice (bare field-line + HTML-comment annotation, the slice-031 remedy). Impact: R-7 gets fresh N+1 recurrence evidence; the cure (BC-PROJ-4) worked exactly as designed.
- **Ad-hoc `;`-split runner footgun reproduced LIVE (slice-032 secondary discovery / R-5)** — a naive catalog runner stripping only OUTER backticks (not per-`;`-segment) false-FAILs row #28 (segment 2's leading `` ` `` → argv[0] → WinError 2). Row #28 PASSES under SCMD-1-correct per-segment parsing (26 + 2 passed). NOT a slice-033 regression. → opened as **R-8**.

## Deferred
- **R-8 — shippability Step-5.5 runner `;`-split contract unpinned** — reason: distinct SCMD-1-adjacent runner-parsing concern, out of slice-033 scope per mission-brief (m2 ACCEPTED-FIXED handle). Lands in: a future runner-hardening slice. Opened in risk-register this /reflect.
- The `;`-split runner contract itself (no audit pins that the Step-5.5 runner does per-segment backtick-strip) — tracked by R-8.

## Critic calibration

Scored from `critique.md` `## Triage` + DR-1 `critique-review.md` + reality during build/validate:

- **B1** (no changelog/version bump): **VALIDATED** — ACCEPTED-FIXED; PMI-1 audit genuinely required 0.47.0 + the changelog pin at build (`test_v_0_47_0_…` would not exist otherwise). Critic right.
- **B2** (CLAUDE.md "MUST be byte-equal" actively false): **VALIDATED** — ACCEPTED-FIXED; the L33/L36 statements were factually false post-fix; corrected + pinned. Critic right.
- **M1** (.gitattributes doesn't normalize already-CRLF tree; test only checks declaration): **VALIDATED** — ACCEPTED-FIXED; materialized EXACTLY as flagged (renormalize index-only; working tree stayed CRLF until re-checkout). Highest-value finding.
- **M2** (CAD-1 existing drift tests not bound): **VALIDATED** — ACCEPTED-FIXED; binding held, must-not-mask preserved.
- **M3** (wrong-subpackage import precedent): **VALIDATED-as-Minor** — ACCEPTED-FIXED; DR-1 recalibrated Major→Minor (technical risk empirically disproven); the import did resolve from both subpackages (41 tests collect) as predicted. DR-1's severity call was correct.
- **M4** (top-level module vs conftest convention): **VALIDATED** — ACCEPTED-FIXED; pytest did not collect it, import resolved from both subpackages; ADR rationale sound.
- **m1** (AC4 procedural→property): **VALIDATED** — ACCEPTED-FIXED; AC4-as-property held (rows #1/#19 green cp-state-independent).
- **m2** (`;`-split deferral handle): **VALIDATED** — ACCEPTED-FIXED; the `;`-split footgun recurred LIVE this slice, vindicating the need for a tracked handle → R-8 opened.
- **m-add-1** (DR-1 missed-finding: RULE-ID/pin-name parity): **VALIDATED** — ACCEPTED-FIXED; minted `EOL-DRIFT-1`; `test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed` passed, 007–032 naming parity restored.

**Missed by Critic**: the R-7 field-line-annotation silent-bypass. Neither the first Critic nor the DR-1 meta-Critic flagged that the mission-brief's own `**Test-first**: true  (per TF-1 — …)` annotation would break the TF-1 audit regex — despite R-7 being an OPEN risk-register entry and the meta-Critic being explicitly asked framing-question (d) about the TF-1 status vocabulary (it verified `PASSING` was valid but did not notice the field-LINE annotation itself). This is the documented BC-PROJ-4 / aggregated-lessons class ("the audit's OWN parse rules are a design-stage blind spot"; "Critics review intent, not the audit-vs-artifact interaction"). Strong `/critic-calibrate` input.

**Pattern**: the slice-022 self-violation law fires again (~N≈10) — a methodology-tooling slice nearly committed the exact footgun (R-7) documented in its own risk register. The dual-Critic stack structurally cannot reach the audit-vs-artifact interaction; the BC-PROJ-4 pre-finish discipline (run the real gate, read its output) is the load-bearing backstop and worked precisely as designed. Confirms: for audit-touching slices, budget the BC-PROJ-4 real-artifact gate run as the primary R-6/R-7-class catch, not the Critic stack.

## Lessons for next slice
- The slice-022 self-violation law now holds at ~N≈10 — any methodology/audit-tooling slice should pre-budget its OWN risk-register footguns (R-6/R-7) at the /build-slice pre-finish BC-PROJ-4 gate, not expect the Critic stack to catch them.
- M1-class (declaration-check vs state-check) is a recurring high-value Critic catch on infra/config slices: when a fix's verification asserts a *declaration* (`git check-attr`, a config key) rather than the *resulting state*, demand the state assertion.
- BC-1 promotion candidate (not promoted this slice — opt-in, no user confirmation in autonomous run): "any NEW in-repo↔installed `.md` drift guard MUST delegate to `tests/skill_drift_equality.assert_md_forward_synced` (EOL-normalized), never re-inline raw `read_bytes()` sha256" — guards EOL-DRIFT-1 against a future drift-guard reverting the R-5 class. Recorded here + lessons-learned for a future `/reflect` to promote.

## Vault updates made (thin vault)
- [[risk-register.md]] — R-5 → `retired` (core CRLF false-FAIL class closed environment-independently; `;`-split residual split to R-8); R-7 → N+1 recurrence sub-entry (slice-033 live reproduction + BC-PROJ-4 catch); NEW **R-8** (shippability Step-5.5 runner `;`-split contract unpinned).
- [[decisions/ADR-033-md-drift-guards-eol-agnostic.md]] — authored this slice (status: accepted; reversibility: cheap); RULE-ID `EOL-DRIFT-1` minted.
- [[methodology-changelog.md]] — v0.47.0 EOL-DRIFT-1 entry (in-repo + installed forward-synced).
- This slice's [[design.md]] / [[mission-brief.md]] — corrected through the /critique loop (pre-build); no post-build design deviation.
