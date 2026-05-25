# Reflection: Slice 035 rename-status-skill-to-pulse

**Date**: 2026-05-17
**Shipped**: YES

## Validated
- The `/status`→`/pulse` rename resolves the Claude Code built-in collision — validated by the live skill registry reload mid-build: `/pulse` now surfaces with the collision-free trigger set and `query-design` self-updated to "Distinct from … /pulse".
- The Bucket A/B/C reference taxonomy was sufficient — post-edit inventory grep returned Bucket A empty; the full methodology suite (616) passed including the renamed path-binds, confirming no executable bind was missed.
- 4-part PMI-1 atomic bump correct — `VERSION` = `~/.claude/ai-sdlc-VERSION` = `plugin.yaml.version` = changelog header = `0.49.0`; `test_plugin_yaml_version_matches_version_file_invariant` + the new entry-pin both green in-repo AND installed.
- No regression — 35/35 shippability catalog PASS (after correcting the ad-hoc-runner false-FAIL on #28).

## Corrected
- None. design.md rev-2 (post-dual-review) matched code reality; the only build deviation was a *sequencing* choice (pull installed-skill rename before the mid-slice INST-1 smoke gate, since INST-1 audits the installed tree) — already in scope (B5), logged in build-log Events, no design.md edit needed.

## Discovered
- Nothing new to the project. Re-confirmed (already R-8, open): the ad-hoc Step-5.5 shippability runner's outer-backtick-only strip false-FAILs the lone multi-segment row #28 — the SCMD-1 pre-gate (which passed) proves the *catalog row* is well-formed; the *runner contract* remains unpinned. No new risk entry; R-8 already tracks it.

## Deferred
- None. The slice closed its full scope (all 14 findings ACCEPTED-FIXED and built).

## Critic calibration

Per TRI-1, scored from `critique.md` `## Triage` + `critique-review.md` + reality during build/validate:

**First Critic (10 findings, all disposition ACCEPTED-FIXED):**
- B1 (test_risk_register_audit.py hard path bind): **VALIDATED** — without the repoint, `(REPO_ROOT/"skills"/"status"/...).read_text()` would FileNotFoundError; the renamed test passed only because the bind was repointed.
- B2 (test_skill_model_dispatch.py:25 COST-1 path tuple): **VALIDATED** — the parametrized COST-1 test reads the path; `skills/pulse/SKILL.md` resolves, would have failed on the old constant.
- B3 (false `agents/critique.md:194` citation → CAD-1 N/A): **VALIDATED** — independently re-confirmed at build: the `/status` match is the substring in "NEW symbol/status/anchor"; critique.md untouched, CAD-1 correctly not triggered.
- B4 (changelog RULE-ID + entry-pin under-spec): **VALIDATED** — SRCD-1 + `test_v_0_49_0_srcd_1_*` were genuinely required for suite-green.
- B5 (installed-copy boundary incoherent): **VALIDATED** — installed reconciliation was load-bearing for INST-1 + the entry-pin's installed assertion.
- M1 (vault docs missing): **VALIDATED** — concept.md:46 / risk-register.md:170,172 were real live `/status` refs.
- M2 (tutorial-site asserted not evidenced): **VALIDATED** — evidence-log discipline applied; classification held.
- M3 (build/lib/ unaddressed): **VALIDATED** — excluded correctly; no audit globs build/.
- m1 (test_status_* fn names): **VALIDATED** — 6 fns renamed; no dangling.
- m2 (installed/in-repo split): **VALIDATED** — split was accurate.

**Meta-Critic (EXTEND, +4 missed findings):**
- B-add-1 (4-part bump, not "triple" — `~/.claude/ai-sdlc-VERSION` dropped): **VALIDATED** — load-bearing. The mission-brief must-not-defer literally said "atomic triple"; the first Critic missed it. This is the slice-006 DEVIATION-2 / slice-007-B1 installed-side recurrence class — confirmed real.
- M-add-1 (`methodology-changelog.md:11-15` live `## How /status uses this file`, forward-synced): **VALIDATED** — was a live un-dispositioned skill ref; rewritten + :1377 Validation-cell repointed.
- M-add-2 (SRCD-1 no shippability row): **VALIDATED** — row #35 added; the RPCD-1/SCPD-1 project rule + #33/#34 precedent governed.
- m-add-1 (README.md:149 filename citation): **VALIDATED** — real dangling-filename-after-rename.

**Missed by Critic**: Neither layer pre-flagged that the mid-slice INST-1 smoke gate would fail until the *installed* skill dir was renamed (INST-1 audits the installed tree, but the plan sequenced installed reconciliation as Task 9). Not a defect — the smoke gate caught it exactly as designed and the fix was an in-scope re-ordering — but a sharper plan-review could have ordered installed-reconciliation before any INST-1 gate. Low-severity, process-level.

**Pattern**: The dual-Critic stack performed at its best here. First Critic: 10/10 VALIDATED, zero false-alarms, plus a disciplined anti-over-reach retraction (B3). Meta-Critic earned its cost decisively — B-add-1 was load-bearing and ONLY the meta-Critic caught it, confirming the documented first-Critic blind spot on the **installed-side configuration set** (`~/.claude/ai-sdlc-VERSION`, forward-synced changelog self-references) — the exact slice-006/007 recurrence axis. Strongest evidence-to-date that DR-1 dual-review pays for itself on methodology-surface slices; strong `/critic-calibrate` input (candidate: a first-Critic Dim-7/Dim-9 sub-bullet — "for any version-bumping methodology slice, enumerate ALL FOUR PMI-1 atomic-bump legs incl. the installed `~/.claude/ai-sdlc-VERSION`; the in-repo-only mental model is the recurring miss").

## Lessons for next slice
- **A skill (or any identifier) rename is NOT a prose string-replace.** The load-bearing distinction is executable filesystem-path binds (`(ROOT/"skills"/"<name>"/…).read_text()`, iterated path-list constants, test-module filenames + `test_<name>_*` fn defs) vs prose `/<name>` references. The former hard-fails the suite on a directory rename; enumerate them separately, run a pre-edit AND post-edit inventory grep, and treat a surviving bind as a Bucket-A-class failure. Now codified as SRCD-1.
- **The installed-side configuration set is the first Critic's structural blind spot.** PMI-1 atomic bump is 4-part (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced changelog) — every prior changelog entry documents this, yet the first Critic + the design both said "triple". For any version-bumping methodology slice, the four legs must be enumerated explicitly; the in-repo-only mental model recurs (slice-006/007/035).
- **Sequence installed-copy reconciliation before any INST-1 gate.** INST-1 audits the installed `~/.claude` tree; if a slice renames an installed artifact, do the installed rename before the mid-slice smoke gate, not as a late task.
- **Frozen-as-history is a first-class disposition.** ADR-030 corpus, `lessons-learned.md:414`, and historical changelog entry *narratives* legitimately retain old identifiers (rewriting falsifies the record); only *live* sections (`## How /pulse uses this file`) and *pointer* cells (Validation cross-refs to renamed test files) get rewritten. Distinguish narrative-vs-pointer per-line.

## Vault updates made (thin vault)
- [[decisions/ADR-035-rename-status-skill-to-pulse]] — created (rename + no-alias + SRCD-1 + 4-part-bump + frozen-as-history exclusions; reversibility cheap)
- [[risk-register.md]] — no change (no risk retired/added; R-8 already tracks the runner footgun)
- [[shippability.md]] — row #35 added during build (M-add-2; SRCD-1 durable guard)
- [[concept.md]] — :46 `/status`→`/pulse` (live architecture description)
- This slice's [[design.md]] — rev-2 is the as-built spec (all 14 findings); no post-build correction needed
- `methodology-changelog.md` — v0.49.0 SRCD-1 entry (the methodology rule this slice mints)
