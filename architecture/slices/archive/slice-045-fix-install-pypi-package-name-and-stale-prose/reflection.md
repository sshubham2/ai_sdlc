# Reflection: Slice 045 fix-install-pypi-package-name-and-stale-prose

**Date**: 2026-05-19
**Shipped**: YES

## Validated
- EDIT-1 — `INSTALL.md:93` `graphify`→`graphifyy` (PyPI distribution) with module/CLI `graphify` untouched — validated by `test_install_md_graphify_pip_package_is_graphifyy` (PASS) + grep (`graphifyy` ×1 at L93; 5 `-m graphify`/`graphify install` refs intact at L58/91/95/99/174). Web-verified by first-Critic against live pypi.org/project/graphifyy/.
- EDIT-2 — all four `v0.20.0` literals removed; `INSTALL.md:18` = `(methodology v0.54.0 — see \`VERSION\`)` — validated by `test_install_md_has_no_stale_v0_20_0_literal` (PASS, count 0) + visual read.
- EDIT-3 — tool-count `13`→`25` at L22/L150 = `plugin.yaml` `- path: tools/` count — validated by `test_install_md_tool_count_matches_plugin_yaml` (PASS, 25==25).
- EDIT-4 — README.md:69 + tutorial HTML:1050 name `graphifyy` — validated by the build-added `test_readme_and_tutorial_name_graphifyy_package` (PASS).
- AC5 — repro suite FAIL→PASS: FAIL captured at `/repro` (3 FAILED) and again at AC4 test-first (1 FAILED on reverted README/HTML); PASS now (4/4). Shippability catalog 45/45 PASS, 0 FAIL — no past slice regressed.
- Born-retired R-11 is a legitimate RR-1 pattern — meta-Critic (DR-1) independently confirmed RR-1-clean (total 11, retired 8, 0 violations) and precedent-faithful (not an over-correction) for a latent long-shipped defect surfaced at `/query-design` whose fix + permanent guard (shippability #45) land in the same slice (no open-risk window to track; self-documents the deviation "as R-6").

## Corrected
- design.md EDIT-2 `:18` row originally drafted bare `(methodology v0.54.0)` → built as `(methodology v0.54.0 — see \`VERSION\`)` to honor mission-brief AC2's "labelled against VERSION" wording. Updated in [[design.md]] (EDIT-2 :18 row records the build deviation); user-approved at the plan-mode gate. Strengthening, same edit-site/intent — not a scope change.
- The original design's "risk-retirement recorded in reflection.md not changelog" was factually wrong (first-Critic M1) → corrected to the canonical surface: `risk-register.md` R-11 `**Retired**:` line. Updated in [[design.md]] (MEPD-1(b) discharge sub-section) + [[risk-register.md]] (R-11 born-retired) + [[mission-brief.md]] (Risk-retired → `[[risk-register#R-11]]`, TPHD-1 harmonized).

## Discovered
- **TF-1 `ac-without-row` plan-completeness gap**: a `Test-first: true` brief authored by `/slice` with 5 ACs but only 3 mapped to TF-1 rows (AC4 was grep-only by design, AC5 was a meta-restatement) FAILs `tools.test_first_audit --strict-pre-finish` at `/build-slice` pre-finish — TF-1's per-AC rule is mechanical and does not read the brief's prose note exempting AC4/AC5. Cost an in-build remediation. Impact for next slices: a `Test-first: true` brief must map EVERY numbered AC to ≥1 TF-1 row at `/slice` authoring time (or restructure so non-test ACs aren't separately numbered). Not added to risk-register (process-discipline lesson, not a code/risk surface) — captured as a Lesson + lessons-learned pattern; promote to a build-check only if it recurs (N≥2).
- **MEPD-1 trigger-enumeration boundary** (`/critic-calibrate` watch-list, N=1): `agents/critique.md:122`'s literal MEPD-1 Dim-7 surface list (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`) does NOT name `INSTALL.md` / the INST-1 recipe. This slice establishes — correctly, and confirmed sound by the meta-Critic — that "in-house methodology surface" is read broader than the parenthetical list (INSTALL.md is the behaviour-bearing INST-1 recipe a user executes verbatim). N=1; if it recurs (N≥2) the enumeration should be widened so the boundary is explicit rather than relying on per-slice Critic judgment.

## Deferred
- slice-046 `add-conditional-repro-auto-advance` — codifies the user's feedback that `/slice` should present the exact `/repro` bug description for confirm/modify then auto-invoke `/repro`, never punt "go run it yourself" (see memory `repro-confirm-then-auto-invoke`). Reason: methodology-surface change needing its own design + `/critique` + likely an ADR. Lands in: next slice (queued).
- slice-047 `add-two-scope-install` — user-level (`~/.claude`) vs project-level (`<proj>/.claude`) install chosen interactively. Reason: structural, high-care (INST-1/CAD-1/PMI-1 self-hosting contracts become scope-dependent), needs design.md + `/critique` + ADR. Lands in: backlog after 046.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` + reality observed during build/validate:

- **M1** (MEPD-1 not discharged by name; precedent mis-cited to reflection.md): **VALIDATED** — disposition ACCEPTED-FIXED; the concern was real (the slice would otherwise have recorded the retirement on no canonical surface). Fix (MEPD-1(b) discharge + R-11) verified RR-1-clean and precedent-faithful by the meta-Critic and by the live audit at build.
- **m1** (INSTALL.md:232 reword must not assert currency): **VALIDATED** — disposition ACCEPTED-FIXED; `install_audit.py:4,8,42` confirmed still-frozen at v0.20.0, so the "current" phrasing would genuinely have over-claimed against code (brownfield code-is-truth). Final wording "drift from its canonical inventory" is correct.
- **m2** (AC4 prose targets under-specified, invisible to repro test): **VALIDATED** — disposition ACCEPTED-FIXED; reality confirmed the gap exactly (TF-1 then forced an AC4 mapping, and the README/HTML were genuinely outside the repro contract). Resolved beyond the ratified phrase-pin by adding a real AC4 regression test.

**Missed by Critic**: the TF-1 `ac-without-row` plan-completeness gap (AC4/AC5 unmapped in a `Test-first: true` brief) was not flagged by either the first Critic or the meta-Critic — both reviewed the mission-brief with its 5 ACs + 3-row TF-1 plan and the prose note, and neither predicted the mechanical audit would reject the unmapped ACs at pre-finish. Class: methodology-plan-completeness (the brief's own TF-1 table vs the brief's AC list), structurally adjacent to the slice-040/R-10 "stale-pin caught only at the pre-finish full-suite run" family — the dual-Critic stack reviews design soundness, not whether the brief's TF-1 table is mechanically complete against `test_first_audit`'s per-AC rule.

**Pattern**: first-Critic calibration was good — it correctly invoked MEPD-1 by name (did NOT recur the slice-040/R-10 "freshly-minted rule is a slice N+1 first-Critic blind spot" failure; MEPD-1 is 6 slices old and now internalised) and empirically executed the repro regexes rather than reasoning about them. The single Critic miss is a NEW class (brief-internal TF-1 plan completeness) that no dimension currently targets — distinct from design-soundness; candidate `/critic-calibrate` input alongside the MEPD-1-enumeration-boundary watch-list item.

## Lessons for next slice
- A `**Test-first**: true` mission-brief MUST map EVERY numbered AC to ≥1 TF-1 plan row at `/slice` authoring time. `tools.test_first_audit --strict-pre-finish` enforces per-AC presence mechanically and does not honor a prose "AC-N is grep-only / meta" exemption note — an unmapped AC fails at `/build-slice` pre-finish, costing an in-build remediation. For a genuinely non-test AC, either fold it into a tested AC, give it a real regression test (often a strict improvement, as AC4 here closed the Critic-m2 gap permanently), or do not number it as a separate AC.
- For a no-VERSION-bump conformance/prose-correctness slice that touches an in-house methodology surface: discharge **MEPD-1(b) by name** in design.md, verify why-none against the ACTUAL META-1 enforcing assertion (`test_methodology_changelog.py:136` `^## v…` split), and record any risk-retirement on the canonical `risk-register.md` `**Retired**:` surface — NEVER reflection.md (slice-040/R-10 + slice-036/R-9 precedent class). A born-retired entry (discovered+retired same slice) is RR-1-legitimate for a latent defect surfaced + fixed + guarded in one slice.
- "In-house methodology surface" (MEPD-1 / mandatory-Critic) is broader than `agents/critique.md:122`'s literal enumeration — `INSTALL.md` (the INST-1 recipe) counts. Fail-closed (discharge MEPD-1) when a slice changes any behaviour-bearing methodology artifact even if not literally listed. (`/critic-calibrate` watch-list, N=1.)
- Test-first purity is cheap and worth it even for descriptive-prose ACs: reverting the 2 README/HTML edits to get a genuine FAIL→PASS on the new AC4 test cost ~4 trivial ops and produced a real regression guard + non-tautological contrast (the BC-PROJ-5/genuine-contrast discipline applied to a prose AC).

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — added **R-11** (INSTALL.md install-recipe factual drift), born-retired by slice-045, RR-1-clean (total 11, retired 8, 0 violations); MEPD-1(b) discharge cross-referenced.
- This slice's [[design.md]] — EDIT-2 :18 row records the `— see VERSION` build deviation; EDIT-2 :232 + EDIT-4 reworded per Critic m1/m2; "Decisions made (ADRs)" gained the MEPD-1(b) discharge sub-section.
- This slice's [[mission-brief.md]] — Risk-retired line → `[[risk-register#R-11]]` (TPHD-1 harmonized); TF-1 plan expanded to 7 rows (AC1-5 mapped).
- [[shippability.md]] — entry **#45** (added by `/repro`; extended this slice to also cover README/HTML `graphifyy` naming). This IS slice-045's Step-5.3 catalog contribution (no duplicate row added).
- [[drift-log.md]] — 2026-05-19 00:30 audit entry, 0 blockers / 0 majors.
- No ADR (prose-only, no-VERSION-bump). No `methodology-changelog.md` edit → MCFS-1 Step 5b-fs forward-sync not triggered (and ran clean at build Step 6 regardless).
