# Slice 006: update-critic-with-cross-cutting-conformance-dimension

**Mode**: Standard
**Estimated work**: 0.5 day (~3–4 hours after Critic-driven scope expansion: B1+B2+M2 added back-sync as first build action, M1 added empirical exercise at T-late)
**Risk retired**: none directly retire R-1 / R-2 (those are unrelated `/diagnose` runtime risks). This slice retires the **methodology-evidence-vs-Critic-structure tension** identified at slice-005 (`reflection.md` "Discovered" + lessons L23): cross-cutting-conformance miss class N=5 distinct slices / 10 sub-class hits — strongest evidence base in the project — currently scattered across Dim 1 (tooling-doc-vs-impl parity, surgical sub-bullet), Dim 4 (methodology-audit conformance + algorithm-path-conformance, surgical sub-bullets), and three N=1 lessons that have no home (runtime-environment, language-version, algorithm-path-conformance as standalone). A 9th umbrella dimension unifies the pattern at the cost of one of the Meta-Critic's three decline reasons (citation-anchor purity); the user is overriding. **Additionally** (per Critic B1, /critique 2026-05-10): the slice retires a structural in-repo↔installed drift gap — the two prior /critic-calibrate ACCEPTED surgical edits exist only in the installed copy `~/.claude/agents/critique.md` and were never back-propagated to in-repo; the slice's first build-time action back-syncs them, restoring canonical-source integrity. The follow-on structural fix (extending `tools/install_audit.py` for content-equality OR updating `/critic-calibrate` skill prose to instruct in-repo edits) is tracked as a Discovered slice-007+ candidate.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Add a **9th dimension — Cross-cutting conformance** — to `agents/critique.md` (in-repo canonical source; forward-synced to `~/.claude/agents/critique.md` at T-final), making explicit the unified pattern that slice-005's reflection identified (10 sub-class hits across slices 001–005). The two surgical proposals that `/critic-calibrate` ACCEPTED on 2026-05-10 (Dim 1 sub-bullet on tooling-doc-vs-impl parity; Dim 4 sub-bullet on methodology-audit conformance + algorithm-path-conformance) currently live **only in the installed copy** at `~/.claude/agents/critique.md` lines 57 and 89-92 — per Critic B1, the slice's **first build-time action back-syncs them into in-repo** so they exist in the canonical source as the cross-reference targets Dim 9 sub-clauses 1-3 point at. After back-sync, the slice is additive — a 9th umbrella that names the pattern, gathers the N=1 sub-clauses (runtime-environment, language-version) into a single home, and gives future Critics a single place to ask "is this slice's work conforming to upstream constraints / pre-existing systems / in-house audits?".

This slice **explicitly overrides** the `/critic-calibrate` Meta-Critic's 2026-05-10 decline of the 9th-dimension proposal (`architecture/critic-calibration-log.md:41-44`). The override rationale is recorded as part of AC #5: the Meta-Critic's three reasons (existing-dimension homes, N=1 sub-clauses being thin, citation-anchor purity) are acknowledged; the user prioritizes **pattern unification + a single-bucket home for cross-cutting findings** over framework-anchor purity, and accepts the citation-thin reality (Dim 8 already has the same shape — "the frame is the live web", no peer-level book citation).

## Acceptance criteria

1. `agents/critique.md` (in-repo canonical source; forward-synced to `~/.claude/agents/critique.md` at T-final) contains a `### 9. Cross-cutting conformance` body section inserted between the current Dimension 8 body (Web-known issues) and the existing `### Bonus: weak graph edges` heading. The "Review along these 8 dimensions" header is updated to "Review along these 9 dimensions" (or equivalent count update). The Reference frameworks table at the file's "Reference frameworks" section gains a Dimension 9 row. **Per Critic B1 (/critique 2026-05-10)**: the file ALSO contains the two prior /critic-calibrate 2026-05-10 ACCEPTED surgical sub-bullets at Dim 1 (tooling-doc-vs-impl parity) and Dim 4 (methodology-audit conformance + algorithm-path-conformance) — back-synced from the installed copy as the slice's first build action so the canonical source contains them.

2. The Dimension 9 body **enumerates at least 5 sub-clauses** with concrete examples drawn from slices 001–005, AND the cross-references in sub-clauses 1-3 **resolve** to actual prose existing in-file (per Critic B2, anti-dangling-pointer):
   - **Methodology-audit conformance** — cross-references the Dim 4 sub-bullet rather than duplicating; one-line pointer "see Dimension 4 sub-bullet — listed here as a cross-cutting view". Cross-reference resolves: Dim 4 body MUST contain "Methodology-audit conformance" substring (back-synced per AC #1).
   - **Tooling-doc-vs-implementation parity** — cross-references the Dim 1 sub-bullet, same shape. Cross-reference resolves: Dim 1 body MUST contain "Verify by reading the implementation" substring (back-synced per AC #1).
   - **Algorithm-path-conformance with pre-existing branches** — cross-references the Dim 4 sub-bullet sub-sub-bullet, same shape. Cross-reference resolves: Dim 4 body MUST contain "Algorithm-path-conformance with pre-existing branches" substring (back-synced per AC #1).
   - **Runtime-environment / cwd / tool-permission boundaries** — N=1 sub-clause (slice-001 cwd-mismatch tool denial). New home; no cross-reference target. Concrete example required.
   - **Language-version conformance** — N=1 sub-clause (slice-004 Python 3.12+ docstring escape-sequence SyntaxWarning). New home; no cross-reference target. Concrete example required.

3. The Dimension 9 body either (a) cites a peer-level expert framework anchor — candidates: Cleland-Huang & Gotel (*Software and Systems Traceability*) for cross-cutting traceability, OR Kiczales et al. (1997 *Aspect-Oriented Programming*) for cross-cutting concerns terminology — OR (b) explicitly mirrors the existing Dim 8 honest-out: "no specific framework — operational/empirical (cross-slice evidence accumulation across slices 001–005, 10 sub-class hits)". This must be a deliberate choice with one-line rationale, not an oversight.

4. The output-format `## Dimensions checked` checklist (currently 8 items) is expanded to 9 items, with `Cross-cutting conformance` added as the 9th line in the same `- [x] <name> — <findings or "none because ...">` shape. The "Walk every dimension, in order" prose remains accurate (still walks every dimension — now 9 of them).

5. `architecture/critic-calibration-log.md` gains a **new dated entry** (header `## User override — 2026-05-10`, or whatever today's date resolves to at build-time) recording the slice-006 user-override of the prior Meta-Critic decline. Entry MUST include: (a) link/reference to the 2026-05-10 calibration run that declined; (b) the user's rationale — pattern-unification preference + acceptance of citation-anchor thinness; (c) which of the Meta-Critic's three reasons is being overridden vs. acknowledged; (d) success criterion the user expects the dimension to deliver (consolidated cross-cutting findings; reduced Critic miss-rate in the cross-cutting bucket measured at the next /critic-calibrate run).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Dim 9 body inserted; count update; framework-table row; Dim 1 + Dim 4 surgical sub-bullets back-synced | `Get-Content -Raw agents/critique.md` (in-repo) → assert `### 9. Cross-cutting conformance` substring present; assert exactly 9 `### \d+\. ` headings (regex count); assert the Reference frameworks table contains a row beginning `\| 9.`; **per Critic B1**: assert `Verify by reading the implementation` substring present (Dim 1 sub-bullet back-synced); assert `Methodology-audit conformance` substring present (Dim 4 sub-bullet back-synced); assert `Algorithm-path-conformance with pre-existing branches` substring present (Dim 4 sub-sub-bullet back-synced). |
| 2 | Five sub-clauses enumerated AND cross-references resolve | `Get-Content -Raw agents/critique.md` → assert all 5 sub-clause titles substring-present in Dim 9's body section: `Methodology-audit conformance`, `Tooling-doc-vs-implementation parity`, `Algorithm-path-conformance`, `Runtime-environment`, `Language-version conformance`. **Per Critic B2**: assert each "see Dimension N sub-bullet" pointer in Dim 9 body resolves — `assert "see Dimension 4 sub-bullet" in CRITIQUE` AND `assert "Methodology-audit conformance" in CRITIQUE`; `assert "see Dimension 1 sub-bullet" in CRITIQUE` AND `assert "Verify by reading the implementation" in CRITIQUE`. Both halves of each pair MUST hold (anti-dangling-pointer). |
| 3 | Citation choice deliberate | Manual read of Dim 9's framework-table cell + body opening: either contains a peer-level citation (Kiczales OR equivalent) OR explicitly says "no specific framework — operational/empirical" with one-line rationale. NOT silent. **Per Critic M3**: Kiczales claim must NOT overstate ("the dimension's name is literally his framework's term" was overstated) — preferred wording: "the AOP body of work originating with Kiczales et al. (1997 ECOOP), where 'cross-cutting concerns' became a frozen term-of-art within ~2-3 years". |
| 4 | Output format checklist has 9 items | `Get-Content -Raw agents/critique.md` → in the `## Output format` section's example, assert exactly 9 `- [x]` lines under `## Dimensions checked`; assert `Cross-cutting conformance` is the 9th. |
| 5 | Calibration-log override entry | `Get-Content -Raw architecture/critic-calibration-log.md` → assert new dated entry header substring (e.g., `User override — 2026-05-10`) + assert all four required parts present: prior-decline reference, user rationale, Meta-Critic-reason disposition, success criterion for next /critic-calibrate run. |

**Out-of-repo file caveat (per slice-005 lesson)**: `~/.claude/agents/critique.md` lives outside the project repo. Slice's git diff alone is insufficient evidence — `build-log.md` MUST capture before/after forensic snapshots of the file at T-final (line counts, sha256, full Dim 9 body block, Reference-frameworks table delta). Local prose-pin tests (T-final) and manual re-reads (validate) substitute for CI in the same way slice-005 handled `~/.claude/build-checks.md`.

## Must-not-defer

- [ ] **Pre-Dim-9 back-sync** (per Critic B1+B2+M2) — installed→in-repo back-sync of Dim 1 + Dim 4 surgical sub-bullets is the FIRST build-time action; build-log.md captures pre + post sha256 + line counts; tests `test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet` + `test_critique_dim_4_has_methodology_audit_conformance_sub_bullet` PASS post-back-sync
- [ ] **Cross-references resolve** (per Critic B2) — `test_critique_dim_9_cross_references_resolve` PASSES; each Dim 9 "see Dimension N" pointer paired with the actual Dim N sub-bullet text existing in-file
- [ ] **Citation choice deliberate** (peer-level OR honest-no-framework with rationale — NOT silent); Kiczales claim NOT overstated per Critic M3
- [ ] **Sub-clauses populated** with concrete cross-slice example for each (no `TODO: fill in`; no bare bullet without example)
- [ ] **Cross-references explicit** — Dim 9's three cross-reference sub-clauses (methodology-audit, tooling-doc-vs-impl, algorithm-path) point at Dim 1 / Dim 4 sub-bullets so the Critic doesn't double-count via two paths
- [ ] **Backward compat** — existing 8 dimensions remain unchanged in body and intent (additive only; no removals; no rewording of Dim 1 / Dim 4 EXAMPLE bullets — only the back-sync ADDS the surgical sub-bullets per AC #1)
- [ ] **Out-of-repo file forensic capture** in `build-log.md` per slice-005 precedent — **bidirectional sync** (per Critic M2): for `agents/critique.md`, sha256 + line counts at FOUR points (T-pre-back-sync, T-post-back-sync, T-post-Dim-9-edit, T-post-final-resync); for the other 6 affected files, sha256 + line counts before+after Phase 2 forward-sync
- [ ] **Calibration-log override entry** — written contemporaneously, not as a post-hoc summary; record per TRI-1 vocabulary (user-override of meta-critique, distinct from Critic-MISSED or FALSE-ALARM)
- [ ] **Methodology-changelog entry** — v0.21.0 with rule ID `CCC-1` (Cross-Cutting Conformance dimension v1) including: behavior change ("future /critique runs will produce findings under a 9th dimension"), defect class (cross-cutting findings previously had no consistent home, scattered across Dim 1 + Dim 4 + lessons-learned), validation method (prose-pin tests on `agents/critique.md` matching AC verification plan)
- [ ] **VERSION + changelog atomicity** (per Critic M4) — VERSION 0.20.0 → 0.21.0 + methodology-changelog v0.21.0 entry land in same commit; mid-slice smoke includes `pytest test_version_matches_most_recent_changelog_entry` to catch format drift early
- [ ] **M1 empirical exercise** (ACCEPTED-PENDING per Critic M1, applied at /build-slice T-late) — spawn 1 Critic re-critique of slice-005's archived design.md against the new 9-dim Critic; capture finding count + per-finding dimension framing in build-log.md. ONE finding (Dim 4 OR Dim 9) → empirical confirmation of no-double-fire claim. TWO findings → escalate as validate-time blocker.

## Out of scope

- **Removing the surgical sub-bullets** from Dim 1 and Dim 4 of `agents/critique.md` post-back-sync — they remain as the cross-reference targets for Dim 9. A future cleanup slice could de-duplicate, but additive-only is the safe first cut.
- **Re-running /critique on archived slices 001–005** to retroactively generate Dim 9 findings — useful as effectiveness-check input for the next /critic-calibrate, but separate slice (low priority; the calibration loop will catch real misses going forward).
- **Adding a `tools/cross_cutting_audit.py`** or any tooling — the dimension is a Critic agent prompt addition, not a separate audit tool. The Critic applies the dimension during /critique invocations.
- **Updating the Critic's "Reference frameworks" prose elsewhere** beyond the table row + Dim 9 body — the file's other prose ("These citations are retrieval keys", etc.) does not need updates.
- **Changing /critic-calibrate skill or `tools/critique_review_audit.py`** — orthogonal; the /critic-calibrate skill should still work unchanged after Dim 9 is added (it analyzes "Missed by Critic" entries regardless of dimension count).
- **Refactoring `architecture/critic-calibration-log.md`'s structure** — single new dated entry only.
- **Structural fix for the in-repo↔installed drift class** (per Critic M2 + m3 — extending `tools/install_audit.py` for content-equality OR new `tools/critique_agent_drift_audit.py` OR updating `skills/critic-calibrate/SKILL.md:108-109` to instruct in-repo edits) — tracked in /reflect Discovered as slice-007+ candidate. Slice-006's back-sync addresses the SYMPTOM; the structural fix addresses the CLASS.

## Dependencies

- Prior slices: [[slice-005-add-bc-1-keyword-precision]] — provides the "out-of-repo edits require forensic capture in build-log.md" pattern + the `~/.claude/build-checks.md` precedent for testing files outside the repo. Also provides the algorithm-path-conformance sub-clause that lands as one of Dim 9's cross-references.
- Prior slices: [[slice-001 through slice-004]] — provide the 10 sub-class hits enumerated in slice-005's reflection that Dim 9 organizes.
- Vault refs: [[critic-calibration-log.md]] (the prior decline being overridden), [[methodology-changelog.md]] (v0.21.0 entry needed), [[~/.claude/agents/critique.md]] (the file being modified)
- Risk register: none directly retired
- Methodology refs: existing surgical sub-bullets at `~/.claude/agents/critique.md:57` (Dim 1) and `:89-92` (Dim 4) remain as cross-reference targets

## Mid-slice smoke gate

At ~50% of build (after Dim 9 body is drafted but before tests are written), run:

```powershell
$cm = "C:\Users\sshub\ai_sdlc\agents\critique.md"  # in-repo canonical source
$content = Get-Content -Raw $cm
$dimCount = ([regex]::Matches($content, '(?m)^### \d+\. ')).Count
Write-Output "Dimension headings: $dimCount (expected 9)"
$has9 = $content.Contains('### 9. Cross-cutting conformance')
Write-Output "Has Dim 9 heading: $has9 (expected True)"
$tableHas9 = $content -match '(?m)^\| 9\. '
Write-Output "Reference table has row 9: $tableHas9 (expected True)"
# Per Critic B1 — back-sync targets present in-repo:
$hasDim1Surgical = $content.Contains('Verify by reading the implementation')
Write-Output "Has Dim 1 surgical sub-bullet (back-synced): $hasDim1Surgical (expected True)"
$hasDim4Surgical = $content.Contains('Methodology-audit conformance')
Write-Output "Has Dim 4 surgical sub-bullet (back-synced): $hasDim4Surgical (expected True)"
# Per Critic m4 — prose-parity sweep:
$paritySweep = (Get-ChildItem -Recurse -Path agents,skills,plugin.yaml,tutorial-site -Include *.md,*.yaml,*.html -ErrorAction SilentlyContinue | Select-String -Pattern "8 dimensions" -SimpleMatch | Measure-Object).Count
Write-Output "Stale '8 dimensions' references: $paritySweep (expected 0)"
# Per Critic M4 — VERSION/changelog atomicity:
$PY = "C:\Users\sshub\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_methodology_changelog.py::test_version_matches_most_recent_changelog_entry --tb=short 2>&1 | Select-Object -Last 3
```

Expected: `Dimension headings: 9` AND `Has Dim 9 heading: True` AND `Reference table has row 9: True` AND `Has Dim 1 surgical sub-bullet: True` AND `Has Dim 4 surgical sub-bullet: True` AND `Stale '8 dimensions' references: 0` AND pytest line ends with `1 passed`. If any fail: STOP, the additive structure or back-sync or prose-parity or version-atomicity broke; diagnose the specific delta before continuing.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md` (note: ACs #1 and #2 expanded per Critic B1+B2)
- [ ] Must-not-defer list fully addressed (10 items above; expanded per Critic B1+B2+M4+M1+M2)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (all 7 expected outputs hold)
- [ ] No new TODOs / FIXMEs / debug prints in `agents/critique.md` (in-repo or installed) or `architecture/critic-calibration-log.md`
- [ ] `methodology-changelog.md` v0.21.0 / CCC-1 entry present
- [ ] `build-log.md` carries **bidirectional** sync sha256 + line counts (per Critic M2): for `agents/critique.md` = 4 capture points (T-pre-back-sync, T-post-back-sync, T-post-Dim-9-edit, T-post-final-resync); for the other 6 forward-sync files = before+after; plus full Dim 9 body block + Reference-frameworks table-row delta
- [ ] M1 empirical exercise complete (per Critic M1): build-log.md contains the 1 Critic re-critique against slice-005's archived design.md + finding count + dimension framing classification; finding count == 1 OR explicit escalation rationale captured if == 2
- [ ] VAL-1 self-application clean (`--imports-allowlist tests`, per slices 003/004/005 N=3 stable pattern)
