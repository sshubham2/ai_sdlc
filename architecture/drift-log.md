# Drift Log

Append-only audit trail of `/drift-check` runs. Each entry records vault-vs-code divergence findings + resolutions.

## Audit 2026-05-15 14:40

**Trigger**: slice-024 pre-finish gate (/build-slice Phase 6)
**Scope**: full (thin-vault surface — ADRs + risk-register + active slice design/mission-brief)
**Findings**: 0 blockers, 0 majors

### Blockers

(none)

### Majors

(none)

### Notes

slice-024 is a pure methodology-codification slice. All vault claims verified against code reality by the Phase 6 audit gauntlet:
- ADR-022 (status: accepted, reversibility: cheap, supersedes: null) — matches design.md + mission-brief claims.
- `agents/critique.md` carries the FBCD-1 `Fix-block-completeness discipline` Dim 9 10th sub-clause (CAD-1 byte-equal in-repo ↔ installed; sha256 f0bd6653cf5a97a0...).
- `methodology-changelog.md` v0.38.0 entry present in-repo + installed (bidirectional sha256 byte-equal 3928548a2bddfe68...).
- `architecture/risk-register.md` untouched (0 changed files) — matches "no new risks introduced" claim (R-1/R-2/R-3 unchanged).
- TF-1 plan 13/13 PASSING; PMI-1 clean (version 0.38.0); SCPD-1 propagation clean (5 pytest-cmd rows propagated, 2 historical preserved).

No DRIFT / UNSPECIFIED-CODE / STALE-CLAIM. Vault and code aligned.

## Audit 2026-05-16

**Trigger**: slice-026 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — active slice-026 ADR-024 + design.md + mission-brief.md; risk-register; ADRs status:accepted)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Notes
- ADR-024 claims verified vs code: `tools/critique_review_prerequisite_audit.py` exists and reads the `critique-review-skip` milestone.md frontmatter key (10 refs) with regex `^skip — rationale: .+`; escape-hatch location matches ADR-024 decision.
- ADR-019 conformance verified: zero `CRPD-1`/`-D` rule-ID residue in source (tools/, build-slice SKILL.md, plugin.yaml). The single `CRPD-1` token in methodology-changelog.md v0.40.0 is legitimate historical narrative documenting the /critique B1 catch, not a live naming-class assertion.
- All slice-026 design.md "What's new" file claims exist on disk.
- No risk-register drift (slice-026 retires no registered R-N; it closes a methodology-process gap from slice-025 reflection L37).
- Self-hosting drift gates all clean this slice: CAD-1 (agents/critique.md byte-equal), PMI-1 (v0.40.0, 19 tools), INST-1 (19/19), mini-CAD (build-slice SKILL.md in-repo↔installed byte-equal), milestone.md template in-repo↔installed byte-equal (M-add-1).

### Resolutions
- No findings; no resolutions required.

## Audit 2026-05-16 (slice-028 pre-finish gate)

**Trigger**: slice-028 /build-slice pre-finish gate
**Scope**: active slice-028 (vault ADR-026 + design.md + mission-brief vs code)
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Resolutions
- CLEAN — 8 vault claims verified aligned: helpers exist; sentinel name preserved (shippability row 23 target); 3 guard tests exist; no int-count Compare in sentinel body (AC#1); PMI-1 atomic 0.42.0 across VERSION+plugin.yaml+installed; ADR-026 accepted/reversibility:cheap; risk-register unmodified (no R-ID retired); no unspecified changed files (design.md Components-touched complete).

## Audit 2026-05-17 02:40

**Trigger**: slice-031 (split-label 030B) /build-slice pre-finish gate
**Scope**: full (thin vault — ADRs + risk-register + active slice-031 design/mission-brief)
**Findings**: 0 blockers, 0 majors

### Verified aligned
- ADR-030 / ADR-031: status=accepted, reversibility=cheap (slice-031's own decisions).
- design.md "What's new" — all files exist (tools/shippability_decoupling_audit.py, tests/methodology/test_shippability_{decoupling_audit,command_column}.py, fixtures/archive_backtest_corpus/, validate-slice/SKILL.md).
- ADR-031 "6th machine-stable column" ⇔ shippability.md header = 6 columns; "shippability_path_audit reads Machine-cmd" ⇔ `cells[5] if len(cells) > 5 else cells[3]` present.
- risk-register R-4 = `mitigating` (NOT retired — honest incidental-only split); sub-entry charters slice-030C; M-add-1 carried (DEFERRED).
- SCMD-1 self-run clean (incidental=0, essential=31 recognized-not-flagged); TF-1 18/18 PASSING.

### Resolutions
- None required — thin vault authored concurrently with code; zero drift accrued.

### Out-of-scope note (not slice-031 drift)
- `tests/skills/diagnose/test_diagnose_skill_drift.py` fails on R-5/D-1 CRLF-LF fragility (in-repo CRLF vs installed LF, content byte-identical normalized; diagnose SKILL.md git-untouched this slice). Pre-existing, explicitly out-of-scope per slice-031 mission-brief; slice-030A precedent (user-approved-deferral against R-5). Tracked by risk-register R-5.

## Audit 2026-05-17 01:20

**Trigger**: slice-035 pre-finish gate
**Scope**: full (active slice slice-035-rename-status-skill-to-pulse)
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Resolutions
- ADR-035 rename claims verified against code: skills/pulse/ exists, no skills/status/, plugin.yaml id:pulse, install_audit canonical "pulse", VERSION/changelog v0.49.0 SRCD-1 — all aligned.
- design.md Bucket A/B/C taxonomy verified: post-edit inventory grep shows Bucket A empty (0 executable path binds, 0 test_status_ fns). Frozen-as-history (ADR-030 corpus, lessons-learned.md:414, historical changelog entry narratives) intentionally retained per ADR-035.
- shippability #35 Command-cell test paths all resolve on disk.
- risk-register.md: no risks claimed retired by this slice (R-1/R-2 untouched).

## Audit 2026-05-17 02:30

**Trigger**: slice-036-fix-rr1-audit-status-filter pre-finish gate
**Scope**: full (active slice slice-036; Standard thin vault)
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Resolutions
- ADR-036 / design.md claim "out['risks'] = filtered view, no out['view']" verified vs `tools/risk_register_audit.py:424` (out["risks"] = [r.to_dict() for r in view]; zero `out["view"]` occurrences).
- design.md "What's reused" (filter_and_sort:319, _format_human:348, to_dict:119 unchanged) verified — anchors present, slice touched only the `if args.json:` block.
- R-9 `architecture/risk-register.md` still `Status: open` (L166) — NOT drift: slice retires R-9 proactively; register entry is updated at /reflect, design.md claims proactive retirement only.
- shippability #36 command target `test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks` exists and PASSES.

## Audit 2026-05-17 — slice-038 pre-finish gate

**Trigger**: slice-038 /build-slice pre-finish gate
**Scope**: full (thin vault — active slice slice-038 + ADR-039 + R-8)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Verified clean
- ADR-039 (accepted): `tools/shippability_runner.py` exists and REUSES SCMD-1 `_segments`/`_catalog_rows`/`_machine_cmd_cell` by object identity (not re-derived) — verified.
- design.md code refs (`tools/shippability_runner.py`, `tests/methodology/test_shippability_runner_segment_contract.py`) exist.
- AC1/AC3 claim: `skills/validate-slice/SKILL.md` Step 5.5 invokes `tools.shippability_runner` + carries the canonical no-hand-roll/reuse pins — present in BOTH in-repo and installed copies.
- methodology-changelog.md v0.51.0 SRSC-1 entry forward-synced in-repo↔installed (EOL-agnostic per EOL-DRIFT-1).
- risk-register R-8 `Status: retired` consistent with shipped SRSC-1 (runner + SKILL.md invocation + catalogued regression #38).
- No UNSPECIFIED CODE / STALE CLAIM: SRSC-1 is additive; no removed feature, no orphan code.

## Audit 2026-05-19 00:30

**Trigger**: slice-045 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin-vault Standard) — focus on slice-045 surface
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Verification performed
- design.md EDIT-1..EDIT-4 claims vs code reality: INSTALL.md:93 = `pip install graphifyy` (✓); `v0.20.0` literal absent from INSTALL.md (✓ repro test 2); INSTALL.md tool-count claims = 25 = plugin.yaml `- path: tools/` count (✓ repro test 3); README.md:69 + tutorial HTML:1050 name `graphifyy` (✓ AC4 test).
- mission-brief must-not-defer "no collateral rename of graphify module/CLI": grep confirms `graphifyy` appears exactly once in INSTALL.md (line 93, pip target only); all 5 `$PY -m graphify` / `graphify --help` / `graphify install` module/CLI refs (lines 58/91/95/99/174) unchanged; no stray `-m graphifyy` / `import graphifyy` (✓).
- risk-register R-11 born-retired: `**Status**: retired` field line present; RR-1 audit clean (total 11, retired 8, 0 violations); R-11's factual claims (wrong PyPI name fixed, stale prose fixed, shippability #45 guard exists) all match code reality (✓).
- shippability #45 consumer reference: catalogued command targets the extant `tests/methodology/test_install_md_correctness.py` (4 tests, all PASSING); SCPD-1/PTFCD-1 consistent.
- No UNSPECIFIED CODE / STALE CLAIM: slice is prose-correctness + a regression test; no removed feature, no orphan vault claim. graphify module/CLI is NOT renamed (only the PyPI distribution token), so no ADR/component drift.

### Resolutions
- none required — vault and code aligned for the slice-045 surface.

## Audit 2026-05-19 15:05

**Trigger**: slice-049 /build-slice pre-finish gate
**Scope**: full (Standard / thin vault; active slice = slice-049 only)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Notes
Vault claims verified against code reality: ADR-051 (status: accepted, reversibility: cheap, supersedes: null) ↔ `tests/methodology/test_{triage,adopt}_skill_drift.py` exist + reuse `assert_md_forward_synced` verbatim (2 refs each, zero new comparator); `methodology-changelog.md` `## v0.57.0` OSDG-1 entry present + forward-synced (MCFS-1 PASS); exactly ONE `| 49 | slice-049-…` shippability row (SRSC-1 runner: 49 rows / 49 PASS); `VERSION`=`plugin.yaml.version`=`~/.claude/ai-sdlc-VERSION`=0.57.0 (PMI-1/INST-1 clean). Full methodology suite 730 passed; CAD-1 + all skill-drift + OSDG-1 + entry-pin guards green. No DRIFT / UNSPECIFIED-CODE / STALE-CLAIM. (Pre-existing `~/.claude/ai-sdlc-VERSION`=0.55.0 slice-048 leg-drift was reconciled to 0.57.0 by this slice's 4-part bump — recorded in slice-049 build-log FINDING for /reflect.)

## Audit 2026-05-19 18:33

**Trigger**: slice-051 pre-finish gate
**Scope**: full (thin vault — ADRs accepted, risk-register, active slice-051 design/brief)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Resolutions
- Clean. ADR-053 claims verified: tests/methodology/test_reflect_skill_drift.py exists; CLAUDE.md OSDG-1 bullet names reflect; methodology-changelog.md v0.59.0 entry present; 4-part PMI-1 bump 0.58.0->0.59.0 (PMI-1/AVFS-1/MCFS-1 PASS); shippability row #51 (SCMD-1 clean 51 rows). risk-register: no retired-claim this slice (STP-1 clean). slice-051 design/brief references all resolve to existing artifacts (746-pass methodology suite).

## Audit 2026-05-20 — slice-052 pre-finish gate

**Trigger**: slice-052-add-slice-candidates-obo-mode pre-finish gate (/build-slice Step 6)
**Scope**: full (thin-vault surface: ADR-054, risk-register R-12/R-13, active slice design.md + mission-brief, methodology-changelog v0.60.0)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Notes
ADR-054 `status: accepted` and its code claim holds — `build_backlog.py` exposes `obo_extract`/`obo_write`/`obo_peek`, and `obo_peek` enforces the allow-set mechanically via `{Path(p).resolve() for p in evidence_files(...)}` containment (not honour-system). `skills/slice-candidates/SKILL.md` carries the `--obo interactive review mode` section + the Hard-rule-#2 ADR-054 carve-out + the `--obo-peek` only-source-read-channel constraint. R-13 ("OSDG-1 not yet extended to /slice-candidates", status `open`) is consistent with reality — `tests/methodology/test_slice_candidates_skill_drift.py` is correctly ABSENT (deliberate own-slice deferral). R-12 ("Hard-rule-#2 controlled relaxation", `mitigating`) matches the mechanical `--obo-peek` gate + shippability row #52. methodology-changelog `## v0.60.0` references real code (`build_backlog.py --obo-peek`); design.md / mission-brief references all resolve to existing artifacts (`test_slice_candidates_obo.py` + fixture + `backlog.golden.md`). 4-part PMI-1 bump 0.59.0→0.60.0 (PMI-1/AVFS-1/MCFS-1 PASS); 764-pass methodology suite; design.md "drift posture unaffected" claim corrected in-slice (logged deviation). No DRIFT / UNSPECIFIED-CODE / STALE-CLAIM.

## Audit 2026-05-22 — slice-058 pre-finish gate

**Trigger**: slice-058-add-install-wakeup-prompt-guardrail /build-slice Step 6 pre-finish gate
**Scope**: full (thin-vault Standard — ADRs accepted, risk-register, active slice-058 design.md + mission-brief.md)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Verified aligned
- ADR-057 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (seed the guardrail via an INSTALL.md → global `~/.claude/CLAUDE.md` append) matches code: `INSTALL.md` carries `### 3h: Global CLAUDE.md — wakeup-prompt discipline`; `/triage` + `/adopt` SKILL.md are untouched (the option-2 per-project route was not taken).
- design.md "What's new" — all claims verified on disk: INSTALL.md Step 3h present; the `# Wakeup-prompt discipline` block embeds the four load-bearing facts; `tests/methodology/test_install_md_wakeup_guardrail.py` created (3/3 PASS); `architecture/shippability.md` row #58 present (SRSC-1 runner 58/58 PASS); ADR-057 on disk.
- B2 cleanup verified: `INSTALL.md` carries **zero** version-number literals after the line-18 reword (re-grep `v?0\.\d+\.\d+` → no matches) — the `v0.54.0` staleness is drift-proof, not band-aided.
- Inclusion-heuristic "no bump" claim holds against reality: `VERSION` unchanged at `0.62.0`; `methodology-changelog.md` unchanged (MCFS-1 + AVFS-1 PASS); `plugin.yaml` untouched.
- risk-register.md: slice-058 retires no registered risk (it is preventive; no `**Status**:` flip) — STP-1 clean, consistent.
- git tracked changes = exactly `M INSTALL.md` + new `tests/methodology/test_install_md_wakeup_guardrail.py` — matches design.md "Components touched" precisely; no UNSPECIFIED CODE.
- No STALE CLAIM: the slice is additive install-recipe prose + a regression test; no removed feature, no orphan vault claim.

### Resolutions
- None required — vault and code aligned for the slice-058 surface.

## Audit 2026-05-23 01:15

**Trigger**: slice-059 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADRs + risk-register + active slice-059 design.md/mission-brief)
**Findings**: 0 blockers, 0 majors

### Blockers
(none)

### Majors
(none)

### Verified aligned
- ADR-058 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (mint TVFS-1 as a standalone tool `tools/ai_sdlc_tools_version_forward_sync.py`, purelib-scoped read) matches code: the tool exists on disk; the read mechanism is `importlib.metadata.distributions(path=[sysconfig.get_path("purelib")])` exactly as the ADR specifies.
- design.md "What's new" / "What's modified" — every claim verified on disk: the tool + `tests/methodology/test_ai_sdlc_tools_version_forward_sync.py` (8 tests) created; `tools/install_audit.py` `_CANONICAL_TOOLS` carries the entry + the two count-literal scrubs + the M-add-1 cross-ref; `plugin.yaml` carries the `- path:` entry; `skills/build-slice/SKILL.md` Step 6 + `skills/reflect/SKILL.md` Step 5b-tvfs wired; `methodology-changelog.md` v0.63.0 entry; `architecture/shippability.md` row #59; the two `test_v_0_63_0_tvfs_1_*` entry-pins added.
- mission-brief must-not-defer — all addressed in code: graceful not-installed handling (the `None`→WARN branch, no traceback); actionable mismatch message (`_ATTRIB_DRIFT` names `pip install --upgrade` + INSTALL.md Step 3g); CWD-shadowing confirmed closed (purelib-scoped resolver; `test_real_resolver_excludes_in_repo_egg_info` PASS); shippability propagation (row #59 + consumer-propagation entry-pin); UTF8-STDOUT-1 (`_stdout.reconfigure_stdout_utf8()` first line of `main()`).
- 4-part PMI-1 bump consistent: `VERSION` = `plugin.yaml.version` = `pyproject.toml [project].version` = `0.63.0`; methodology-changelog head `## v0.63.0`; installed `~/.claude/ai-sdlc-VERSION` = `0.63.0` (AVFS-1 PASS); TVFS-1's own gate confirms the installed `ai-sdlc-tools` pip distribution = `0.63.0` (bootstrap re-install done).
- risk-register.md: slice-059 retires no registered risk (the gap it closes was a newly-discovered un-numbered gap; a risk entry may be minted at /reflect per design.md) — STP-1 clean, consistent.
- No UNSPECIFIED CODE / no STALE CLAIM: the slice is additive (a new tool + the new rule TVFS-1); no removed feature, no orphan vault claim. Full methodology suite 807/807 PASS; 14 Step 6 audits exit 0.

### Resolutions
- None required — vault and code aligned for the slice-059 surface.
