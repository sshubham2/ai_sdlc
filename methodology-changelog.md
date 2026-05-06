# AI SDLC Methodology Changelog

This file tracks behavior-changing rules in the AI SDLC pipeline. Each entry carries a **rule reference**, **defect class**, and **validation method**.

## Inclusion heuristic

> If a slice acceptable yesterday would be refused today (or vice versa), it's a changelog entry.

Typo and formatting edits don't qualify; behavior changes do. New skills, new gates, modified pre-finish checks, changed prompt structures for named subagents — these qualify. Doc clarifications that don't change behavior do not.

## How `/status` uses this file

This file is also installed at `~/.claude/methodology-changelog.md` so `/status` can surface the most recent dated entry as a Methodology section, regardless of which project the user is in.

When the file is missing (e.g., older install before this feature shipped), `/status` gracefully skips the Methodology section and optionally hints that re-running the install would surface methodology metadata.

## Format per entry

```markdown
## v<semver> — <YYYY-MM-DD>

<One-paragraph summary>

### Added | Changed | Retired

- **<RULE-ID> — <Rule name>**
  <Description of what this rule enforces and where>
  - **Rule reference**: <RULE-ID>
  - **Defect class**: <what bad behavior this prevents>
  - **Validation**: <how we verify the rule holds — pytest, structural grep, runtime gate, etc.>
```

Rules are identified by short IDs (e.g., `META-1`, `LINT-MOCK-1`, `WIRE-1`) for cross-reference from SKILL.md prose and from later changelog entries that supersede or refine.

---

## v0.19.0 — 2026-05-06

Adds two final pipeline rules. **SUP-1** introduces `/supersede-slice` for cleanly retiring a shipped (archived) slice when reality has contradicted its design. **PMI-1** adds a `plugin.yaml` manifest at the repo root with a parity audit against the actual filesystem, laying groundwork for plugin marketplace distribution.

### Added

- **SUP-1 — Slice supersession**
  Adds `tools/supersede_audit.py` and `skills/supersede-slice/SKILL.md`.

  When a shipped slice's design.md / mission-brief.md continues to read as a live claim about current code (vault drift), AND a new slice in active development is fixing it, `/supersede-slice <archived-id>` formalizes the link:
  - Appends a `## Supersession` section to the archived slice's `reflection.md` with `**Superseded by**: <active-id>`, `**Date**:`, `**Reason**:` fields
  - The active slice's `mission-brief.md` gains a `**Supersedes**: <archived-id>` field
  - The audit walks both directions and validates bidirectional consistency

  Refusal semantics:
  - `missing-target`: Supersedes / Superseded-by points to a slice id that doesn't exist in active or archive
  - `one-way-link`: only one end declares the link (active claims supersedes but archive doesn't acknowledge, or vice versa)

  Append-only history: `/supersede-slice` does NOT modify other content in the archived reflection.md or delete the archived folder. Like ADR supersession, the original slice remains as historical record; the supersession section just marks its claims as no-longer-canonical.

  CLI: `python -m tools.supersede_audit [--root <path>] [--json]`. Exit codes: 0 clean, 1 violations, 2 usage error.

  - **Rule reference**: SUP-1
  - **Defect class**: Without explicit supersession, fix slices accumulate as "another slice in the catalog" while the original archived slice's claims (in its reflection.md and design.md) continue reading as live assertions. /drift-check skips the archive (correctly — those slices already shipped) so the stale claims aren't surfaced. Vault rot accumulates silently across releases. SUP-1 makes supersession an explicit, auditable, bidirectional link, mirroring the ADR `supersedes:` / `superseded-by:` pattern at slice scope.
  - **Validation**: `tests/methodology/test_supersede_audit.py` — 7 tests over tmp_path-built fixtures: no-supersession-clean, bidirectional-clean, missing-target, one-way-active-to-archived, one-way-archived-to-active, missing-slices-dir-graceful, plus skill prose pin (SUP-1 + supersede_audit reference + Supersedes/Superseded-by field formats).

  Limitations (v1, documented in code): no automatic /reflect integration; single-slice supersession only (no chains); no slice-folder name format enforcement; no /critique cross-reference for superseded slices.

- **PMI-1 — Plugin marketplace manifest**
  Adds `plugin.yaml` at repo root + `tools/plugin_manifest_audit.py`.

  The manifest enumerates every skill (24 entries), agent (5 entries), and tool (13 entries — auto-updates as new tools ship) the AI SDLC plugin distributes. The audit cross-validates the manifest against the actual filesystem layout: required top-level fields present (name, version, description, skills, agents, tools); version field matches the top-level `VERSION` file (lock-step semver); every manifest-listed skill has `skills/<id>/SKILL.md`; every manifest-listed agent has `agents/<id>.md`; every manifest-listed tool exists at the declared path; reverse: no orphan skills/agents/tools (real files not listed).

  Format note: this is a starting-point YAML manifest. As the Claude Code plugin marketplace specification stabilizes, the file may be reformatted (e.g., to `.claude-plugin/plugin.json`) and the audit's parser updated. The structural invariants the audit checks (declared = actual; version sync) are the load-bearing piece.

  CLI: `python -m tools.plugin_manifest_audit [--root <path>] [--json]`. Exit codes: 0 clean, 1 violations, 2 usage error. The audit found 2 real violations on its first run (orphan-tool — itself not yet in the manifest; version-mismatch during the in-progress release) — the rule's intended behavior caught its own bootstrap state.

  - **Rule reference**: PMI-1
  - **Defect class**: Distributing AI SDLC as a Claude Code plugin requires a manifest. Without an audit, the manifest drifts the moment a new skill / agent / tool is added without a corresponding manifest update. Installers see "ai-sdlc 0.19.0 with 24 skills" but the package contains 25 — the new one ships but isn't enumerated, so any consumer that walks the manifest (e.g., to render the plugin's contents in marketplace UI) misses it. PMI-1 keeps both in sync at audit time.
  - **Validation**: `tests/methodology/test_plugin_manifest_audit.py` — 9 tests: clean tmp-project, missing-manifest, version-mismatch, missing-required-field, missing-skill, orphan-skill / orphan-agent / orphan-tool, plus a real-repo smoke test that the actual `plugin.yaml` is in sync with the AI SDLC repo (excluding version-mismatch during release-in-progress). Total methodology suite: 272 -> 288.

  Limitations (v1, documented in code): YAML format is provisional (eventual marketplace spec may differ); no content-level validation of SKILL.md frontmatter (covered by other audits); no transitive dependency declaration (yaml, tomllib, tree_sitter); no version-compatibility range; no install-script integration with INSTALL.md.

---

## v0.18.0 — 2026-05-06

Adds **CSP-1** — cross-spec parity audit for Heavy mode. Walks `architecture/threat-model.md`, `architecture/requirements.md`, and `architecture/nfrs.md` and validates that every H2 item (`TM-NN` / `REQ-NN` / `NFR-NN`) has structured fields AND its `Implementation:` (TM/REQ) or `Verification:` (NFR) cross-reference points to a file that actually exists. Catches the canonical Heavy-mode failure mode: a threat / requirement / NFR claims a mitigation or verification that no longer exists in code (or never did).

### Added

- **CSP-1 — Cross-spec parity audit (Heavy mode only)**
  Adds `tools/cross_spec_parity_audit.py` — H2-structured parser + cross-reference validator for Heavy artifacts. Each item is `## TM-NN — <title>` / `## REQ-NN — <title>` / `## NFR-NN — <title>` followed by structured fields. Required fields: `Status`, plus `Implementation` (TM/REQ) or `Verification` (NFR) when status implies real implementation.

  Status vocabulary by artifact type:
  - **Threats**: `mitigated` | `accepted` | `open`
  - **Requirements**: `implemented` | `pending` | `deferred`
  - **NFRs**: `met` | `unmet` | `unverified`

  Statuses requiring a non-empty path: `mitigated`, `implemented`, `met`. Statuses where empty / `n/a` is acceptable: `accepted`, `open`, `pending`, `deferred`, `unmet`, `unverified`.

  Path resolution: the cell value is parsed as `<file>:<func>` (or just `<file>`); the file part is resolved relative to `--root` (default cwd). File existence is verified. Function names within files are NOT verified in v1 (see limitations).

  Heavy-mode-only: the audit auto-detects `**Mode**: Heavy` in `architecture/triage.md` and returns a clean no-op for Minimal / Standard projects. CLI flag `--skip-heavy-check` overrides for archive scans / CI.

  Updates `skills/sync/SKILL.md` Step 3b (between vault drift detection and the diff presentation): runs the audit; surfaces violations in the diff view; broken refs do NOT propagate into regenerated artifacts. Updates `skills/drift-check/SKILL.md` to document CSP-1 as the per-artifact-deep complement to drift-check's fast pre-commit pattern.

  CLI: `python -m tools.cross_spec_parity_audit [--root <path>] [--threats <path>] [--requirements <path>] [--nfrs <path>] [--skip-heavy-check] [--json]`. Exit codes: 0 clean (or non-Heavy / artifacts absent), 1 violations, 2 usage error.

  - **Rule reference**: CSP-1
  - **Defect class**: Heavy artifacts (threat-model.md, requirements.md, nfrs.md) drift from code asymmetrically. Code refactors rename or delete files; a threat row claiming "mitigated by `src/middleware/rate_limit.py`" continues to read like a real claim even after that file moved or was inlined into a router. Without a parity check, audit reviewers (security, compliance, architecture) consume the documents at face value and the gap surfaces only in production. CSP-1 makes the cross-reference auditable: every `mitigated` / `implemented` / `met` status MUST point to a real file that exists right now, and the rule explicitly accepts `accepted` / `open` / `pending` / `unmet` / `unverified` patterns where empty Implementation is the honest state. The audit is structurally identical to other CSV-1-style validators (BC-1, RR-1, TF-1, WS-1, ETC-1, DR-1) — H2 parser + structured fields + status-driven validation rules.
  - **Validation**: `tests/methodology/test_cross_spec_parity_audit.py` — 14 tests over 7 fixtures (`tests/methodology/fixtures/cross_spec_parity/`): Heavy-mode detection (recognizes `**Mode**: Heavy`, returns false for Standard, handles missing triage), ID normalization variants (TM-01, TM01, tm-1 -> TM-1), Heavy-mode gating (Standard returns clean no-op), `--skip-heavy-check` override, clean parsing across all 3 artifact types (TM=3, REQ=2, NFR=2 items), accepted-with-empty-impl passes, broken-ref detection (Implementation points to nonexistent file), missing-status flagging, invalid-status-for-artifact flagging, mitigated-with-empty-impl flagging, plus skill prose pins for `/sync` SKILL and `/drift-check` SKILL. Total methodology suite: 258 -> 272.

  Limitations (v1, documented in code):
  - **No function-level resolution**. `Implementation: src/middleware/auth.py:require_auth` validates the file exists but does NOT verify `require_auth` is defined in it. v2 candidate: ast-parse the file (Python only) to check function definitions.
  - **No bidirectional parity (orphan code)**. The audit catches orphan artifacts (claim with no file) but not orphan code (real authentication middleware that no threat claims as mitigation). Reverse-direction parity needs domain-specific signals (e.g., scan src/middleware/* and ask: is there a threat covering each?). v2 candidate.
  - **Hardcoded artifact paths**. Defaults are `architecture/threat-model.md` / `requirements.md` / `nfrs.md`. Projects with non-standard layouts must pass `--threats`, `--requirements`, `--nfrs` explicitly. A v2 could autodetect.
  - **No NFR target validation**. The audit checks that NFR `Verification:` references exist but doesn't validate the `Target:` value (numeric ranges, units, etc.). NFR target sanity is project-specific.
  - **No multi-file Implementation**. A single threat / requirement may legitimately span multiple files; the audit currently checks only the literal value (single path). Comma-separated paths or YAML lists are deferred.
  - **No status transition validation**. The audit doesn't track historical changes to a Status (e.g., "was mitigated in v1, now open" — should that flag?). Out of scope.

---

## v0.17.0 — 2026-05-06

Adds **DR-1** — dual review for `/critique`. A new meta-Critic agent (`critique-review`) reviews the first Critic's `critique.md` for false positives (over-reach), false negatives (missed concerns), and severity miscalibrations. Per-slice second opinion that complements `/critic-calibrate`'s cross-slice pattern mining: DR-1 catches blind spots faster (one slice) where calibration only surfaces them after N slices accumulate.

### Added

- **DR-1 — Dual review for /critique**
  Adds three components:

  1. **`agents/critique-review.md`** — adversarial-meta Critic prompt. Inputs: mission-brief.md + design.md + critique.md + new ADRs. Stance: assume the first Critic was either too lenient or too aggressive until specifics prove otherwise. For each finding in critique.md, scores VALID / SUSPICIOUS / SEVERITY-WRONG. Independently re-applies the 8 review dimensions (same as agents/critique.md) to design.md to surface missed findings. Output: structured `critique-review.md` with 4 sections (Confirmed findings / Suspicious findings / Missed findings / Severity adjustments) + a top-level Dual-review verdict in `{ACCEPT, ADJUST, EXTEND}`. Frontmatter conforms to META-3 (name=critique-review, model=opus, read-only tools: Read+Glob+Grep+Bash+WebSearch).

  2. **`skills/critique-review/SKILL.md`** — orchestration skill. Reads mission-brief.md + design.md + critique.md, spawns the agent via `Agent(subagent_type="critique-review", ...)`, writes the agent's output to `architecture/slices/slice-NNN-<name>/critique-review.md`, runs the audit, hands off to `/critique` Step 4.5 (TRI-1) for user reconciliation. Manual invocation in v1; auto-trigger via a `**Dual-review**: true` mission-brief field deferred to v2.

  3. **`tools/critique_review_audit.py`** — structural validator. Checks the resulting critique-review.md has all 4 required sections (Confirmed findings, Suspicious findings, Missed findings, Severity adjustments), all 4 required header fields (Reviewed by, Date, First-Critic verdict, Dual-review verdict), and that verdict values are in their allowed sets (`{CLEAN, NEEDS-FIXES, BLOCKED}` for First-Critic mirroring TRI-1, `{ACCEPT, ADJUST, EXTEND}` for Dual-review).

  TRI-1 reconciliation pattern: when the user runs `/critique` Step 4.5, they consult both critique.md (first Critic findings) and critique-review.md (meta-Critic adjustments) when assigning dispositions per finding. SUSPICIOUS findings carry reduced friction toward OVERRIDDEN; missed findings get added as new triage rows with their own dispositions; SEVERITY-WRONG entries adjust the severity in the triage table.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_DR_1_RELEASE_DATE` (2026-05-06) are exempt automatically.

  CLI: `python -m tools.critique_review_audit <slice-folder> [--json] [--no-carry-over]`. Exit codes: 0 clean (or carry-over exempt), 1 violations, 2 usage error.

  - **Rule reference**: DR-1
  - **Defect class**: Single-Critic-pass review has two failure modes that `/critic-calibrate` doesn't catch in real time: (1) per-slice over-reach (Critic flags concerns already addressed in design.md, training the user to ignore findings) and (2) per-slice blind spots (Critic misses a real concern because of dimension-bias or framework gap; the calibration log will eventually surface this after N slices but only after it has happened N times). DR-1 adds a per-slice second opinion: a separate Agent with full meta-Critic context independently scores each finding and re-applies the 8 dimensions to design.md, catching both over-reach and under-reach immediately. The agent + skill + audit triple is structurally identical to the META-3 pattern (named subagent + orchestration skill + read-only artifact validator) used by /critique, /critic-calibrate, /diagnose's narrator, and /risk-spike's field-recon.
  - **Validation**: `tests/methodology/test_critique_review_audit.py` — 11 tests over 4 fixtures (`tests/methodology/fixtures/critique_review/`): clean review with all 4 sections + valid verdicts, missing-section (2 sections absent), invalid-verdict (both verdicts use disallowed values), missing-verdict (header fields absent), missing critique-review.md graceful, carry-over mtime + override, plus skill prose pins (DR-1 reference + subagent_type dispatch), agent prose pins (Meta-Critic stance + scoring vocab VALID/SUSPICIOUS/SEVERITY-WRONG + verdict vocab ACCEPT/ADJUST/EXTEND + Specificity rule). The new `critique-review` agent also auto-conforms to META-3 via the existing `test_agent_frontmatter.py` parametrized test suite (frontmatter shape, name=filename, model in allowed set, tools non-empty, description substantive). Total methodology suite: 243 -> 258.

  Limitations (v1, documented in code):
  - **Manual invocation only**. The `/critique` skill does NOT auto-invoke `/critique-review`; the user must run it explicitly. v2 candidate: a `**Dual-review**: true` mission-brief field that auto-triggers /critique-review at end of /critique Step 3.
  - **No outcome-tracking integration with /reflect**. The agent prompt mentions calibration outcomes (VALIDATED-ON-RECONSIDERATION / OVERRIDDEN-AT-TRIAGE / OVERRIDDEN-MISJUDGED) but `/reflect` Step 3 doesn't yet have a section for scoring meta-Critic findings. v2 will add this so /critic-calibrate can mine DR-1 patterns alongside CAL-1 patterns.
  - **No automatic finding cross-reference**. The audit checks structure but doesn't verify that finding IDs in critique-review.md (e.g., "B1 — confirmed") actually match IDs in critique.md. v2 candidate: cross-file ID validation.
  - **No Heavy-mode reviewer signature**. Heavy mode should record a human reviewer's sign-off on the dual review; the audit doesn't yet validate a Reviewed-by-human field. v2 candidate.
  - **Agent dispatch only**. The skill spawns one meta-Critic agent. A v2 could spawn N parallel meta-Critics with different specializations (security-focused, contract-focused, framework-citation-focused) and aggregate.

---

## v0.16.0 — 2026-05-06

Adds **ETC-1** — charter-based exploratory testing. Mission briefs gain an opt-in `**Exploratory-charter**: true` field; when set, the brief must include a `## Exploratory test charter` section with timeboxed mission statements that the tester runs freely and records findings against. `/validate-slice` Step 5d refuses PENDING / IN-PROGRESS rows at strict-pre-finish; COMPLETED and DEFERRED are both accepted (DEFERRED is the escape hatch with rationale). COMPLETED and DEFERRED rows MUST have non-empty Findings — the discipline IS capturing what surfaces.

### Added

- **ETC-1 — Charter-based exploratory testing**
  Adds `tools/exploratory_charter_audit.py` — a parser + validator for charter-based exploratory test sessions. Detects the opt-in `**Exploratory-charter**: true | false` field. When true: validates the `## Exploratory test charter` section exists with a 5-column markdown table (# | Mission | Timebox | Status | Findings); validates the table has at least one charter row; validates each row's Mission cell is non-empty (a charter without a mission is undirected exploration); validates each row's Status is in `{PENDING, IN-PROGRESS, COMPLETED, DEFERRED}`; validates non-empty Findings when status is COMPLETED or DEFERRED. With `--strict-pre-finish`, PENDING and IN-PROGRESS rows are violations; COMPLETED and DEFERRED are both accepted as "settled."

  Default-off semantics: a brief without the field (or with `Exploratory-charter: false`) is unaffected — the audit returns clean and `/validate-slice` skips the gate.

  Updates `skills/slice/SKILL.md` mission brief template + `templates/mission-brief.md`: documents the `**Exploratory-charter**:` field and the `## Exploratory test charter` 5-column table format. Updates `skills/validate-slice/SKILL.md` Step 5d (between Step 5c WS-1 walking-skeleton and Step 5.5 shippability catalog): runs the audit with `--strict-pre-finish` when the field is true; refuses on any of `missing-section`, `empty-table`, `format`, `missing-cells`, `missing-mission`, `invalid-status`, `missing-findings`, `non-final-pre-finish`.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_ETC_1_RELEASE_DATE` (2026-05-06) are exempt automatically.

  CLI: `python -m tools.exploratory_charter_audit <slice-folder> [--strict-pre-finish] [--json] [--no-carry-over]`. Exit codes: 0 clean (or default-off / carry-over exempt), 1 violations, 2 usage error.

  - **Rule reference**: ETC-1
  - **Defect class**: `/validate-slice` already executes the verification plan from the mission brief (each AC's PASS/FAIL with evidence) but is structurally focused on confirming what's spec'd. It doesn't surface what's NOT spec'd — unstated assumptions, edge cases the design didn't predict, UX issues real users would hit but the AC writer didn't think of, race conditions surfaced by concurrent use. Charter-based exploratory testing (Bach / Kaner / Hendrickson) is the discipline for filling that gap: timeboxed sessions with a stated mission ("Explore X using Y to find Z") where the tester runs freely and captures findings. Without an explicit gate at validate-time, exploratory testing decays into "we'll poke at it" — knowledge that surfaces in chat and never lands in any persistent artifact. ETC-1 makes the charters explicit (must be enumerated with mission + timebox), forces findings to be recorded (COMPLETED/DEFERRED both require non-empty Findings), and gates `/validate-slice` so charters can't be silently left undone.
  - **Validation**: `tests/methodology/test_exploratory_charter_audit.py` — 15 tests over 8 fixtures (`tests/methodology/fixtures/exploratory_charter/`): clean brief with COMPLETED + DEFERRED rows, default-off when field absent, missing-section when true, empty-table, missing-mission, completed/deferred without findings (both flagged), invalid-status, strict-pre-finish accepts COMPLETED + DEFERRED but refuses PENDING + IN-PROGRESS, strict-pre-finish disabled allows all, missing brief silent, carry-over mtime exemption + override, plus skill prose pins for `/slice` SKILL, `/validate-slice` SKILL, and `templates/mission-brief.md`. Total methodology suite: 228 -> 243.

  Limitations (v1, documented in code):
  - **No timebox enforcement**. The Timebox cell is captured as a string ("60min") but the audit doesn't parse it or check that the actual session duration matched. v2 candidate: parse Timebox as duration, cross-reference against build-log.md timestamps for the charter session.
  - **No Findings detail validation**. A non-empty Findings cell passes; the audit doesn't verify the prose actually describes what was explored or what surfaced. Heuristic content checks (minimum word count, presence of bug/risk vocabulary) are deferred to v2.
  - **No follow-up tracking**. Findings that surface in a charter ideally feed `/reflect`'s "Discovered" section AND become candidates for risk-register entries; the audit doesn't enforce that linkage. Manual today.
  - **No charter library**. Each project writes charters fresh; there's no template library of common charters (e.g., "explore upload size limits", "explore concurrent reads"). v2 candidate: a `tools/charter_library.py` with starter charters by domain.

---

## v0.15.0 — 2026-05-06

Adds **WS-1** — walking-skeleton slice variant. Mission briefs gain an opt-in `**Walking-skeleton**: true` field; when set, the brief must include a `## Architectural layers exercised` section listing every architectural layer the slice touches end-to-end with statuses tracked PENDING -> EXERCISED. `/validate-slice` Step 5c refuses non-EXERCISED rows at strict-pre-finish.

This rounds out the slice-variant trio alongside TF-1 (test-first): standard slice (default), test-first slice (TDD discipline), walking-skeleton slice (architecture-first).

### Added

- **WS-1 — Walking-skeleton slice variant**
  Adds `tools/walking_skeleton_audit.py` — a parser + validator for the walking-skeleton variant. Detects the opt-in `**Walking-skeleton**: true | false` field. When true: validates the `## Architectural layers exercised` section exists with a 5-column markdown table (# | Layer | Component | Verification | Status); validates the table has at least one data row (a skeleton with no layers is a contradiction); validates each row's Verification cell is non-empty; validates each row's Status is in `{PENDING, EXERCISED}`. With `--strict-pre-finish`, any non-EXERCISED row is a `non-exercised-pre-finish` violation — used at `/validate-slice` Step 5c to refuse declaring slice validated while a layer hasn't been exercised at runtime.

  Default-off semantics: a brief without the field (or with `Walking-skeleton: false`) is unaffected — the audit returns clean and `/validate-slice` skips the gate. WS-1 is opt-in per slice; existing briefs continue to work without modification.

  Updates `skills/slice/SKILL.md` mission brief template + `templates/mission-brief.md`: documents the `**Walking-skeleton**:` field and the `## Architectural layers exercised` 5-column table format. Updates `skills/validate-slice/SKILL.md` Step 5c (between Step 5b VAL-1 layers and Step 5.5 shippability catalog): runs the audit with `--strict-pre-finish` when the field is true; refuses on any of `missing-section`, `empty-table`, `format`, `missing-cells`, `missing-verification`, `invalid-status`, `non-exercised-pre-finish`.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_WS_1_RELEASE_DATE` (2026-05-06) are exempt automatically.

  CLI: `python -m tools.walking_skeleton_audit <slice-folder> [--strict-pre-finish] [--json] [--no-carry-over]`. Exit codes: 0 clean (or default-off / carry-over exempt), 1 violations, 2 usage error.

  - **Rule reference**: WS-1
  - **Defect class**: Greenfield slices that build vertical features without first proving the architecture works end-to-end repeatedly hit late-discovery integration failures: each layer was unit-tested but the request never actually reached the persistence layer in production, or the external API call wasn't wired correctly, or the frontend's call shape didn't match the API gateway's. The walking-skeleton discipline (Cockburn / Pragmatic Programmers) inverts the order: ship the thinnest vertical that exercises every layer first, then layer real features onto the proven foundation. Without an explicit gate at validate-time, "walking skeleton" decays into a label the team mentions but doesn't enforce — every layer remains an unverified claim until the first feature happens to flush it. WS-1 makes the layers explicit (must be enumerated), the verification explicit (must be runtime, not unit), and the status explicit (must transition PENDING -> EXERCISED before the slice is shippable).
  - **Validation**: `tests/methodology/test_walking_skeleton_audit.py` — 14 tests over 7 fixtures (`tests/methodology/fixtures/walking_skeleton/`): clean brief with all EXERCISED layers, default-off when field absent, missing-section when walking-skeleton true, empty-table (header + separator only), missing-verification, invalid-status, strict-pre-finish refuses PENDING, strict-pre-finish disabled allows PENDING, missing brief silent, carry-over mtime exemption + override, plus skill prose pins for `/slice` SKILL, `/validate-slice` SKILL, and `templates/mission-brief.md`. Total methodology suite: 214 -> 228.

  Limitations (v1, documented in code):
  - **No automatic verification execution**. The audit trusts the declared status — it doesn't run the Verification cell's check to confirm EXERCISED actually exercises. v2 candidate: parse Verification as a runnable command (curl, pytest -k, bash) and execute it.
  - **No layer-completeness check**. The audit doesn't verify that the layers enumerated COVER every architectural layer in the project — projects could declare "Frontend → API" and skip Persistence. A v2 could cross-reference an `architecture/layers.yaml` declaration of expected layers.
  - **No conflict detection with other slice variants**. A brief could set both `Test-first: true` AND `Walking-skeleton: true`; both audits run independently. In practice these compose well (you can do test-first walking-skeleton), but no rule enforces that.
  - **Status vocabulary minimal**. Only PENDING and EXERCISED — no intermediate states for partial exercise across layers. Sufficient for v1.

---

## v0.14.0 — 2026-05-06

Adds **VAL-1** — layered `/validate-slice` safety checks. Two defensive layers run against the slice's changed files before the shippability catalog: Layer A (credential scan, Critical, blocks `/reflect`) and Layer B (dependency hallucination check, Important, surfaces to user). Closes a class of defects that real-environment validation tends to miss: committed credentials and AI-hallucinated package imports.

### Added

- **VAL-1 — Layered /validate-slice safety checks**
  Adds `tools/validate_slice_layers.py` — two-layer defensive check for the per-slice validation flow.

  **Layer A (credential scan):** static regex patterns for AWS access keys (`AKIA...`), GitHub PATs (classic `ghp_`, fine-grained `github_pat_`, OAuth/user/app/refresh `gho_/ghu_/ghs_/ghr_`), Slack tokens (`xox[baprs]-`), JWTs (`eyJ.*\\..*\\..*`), PEM private keys (`-----BEGIN ... PRIVATE KEY-----`), Anthropic API keys (`sk-ant-`), OpenAI API keys (`sk-..T3BlbkFJ..`), and generic `api_key = "..."` literals. Each detected secret is a `Critical` finding that **cannot be deferred** — committed credentials are immediately exploitable. False positives (test fixtures, public-docs examples) are suppressed via `architecture/.secrets-allowlist` (one regex per line; `#` comments).

  **Layer B (dependency hallucination check, Python only in v1):** ast-parses every changed `.py` file and resolves each top-level import against three sources: stdlib (via `sys.stdlib_module_names`), declared deps (`pyproject.toml` `[project.dependencies]` + `[project.optional-dependencies]` + `[tool.poetry.dependencies]`, OR `requirements.txt`), and a small known-aliases table (`yaml`->`pyyaml`, `bs4`->`beautifulsoup4`, `PIL`->`pillow`, `cv2`->`opencv-python`, `sklearn`->`scikit-learn`, etc.). Relative imports (`from . import X`) are skipped. Anything else is an `Important` `hallucinated-import` finding — possible AI hallucination, or a real package the project forgot to declare. Surfaces to user; defer-with-rationale allowed.

  Updates `skills/validate-slice/SKILL.md` Step 5b (between Step 5 validation.md and Step 5.5 shippability catalog): runs both layers; refusal-on-Critical (Layer A); surface-with-defer (Layer B). Skip flags `--skip-secrets` and `--skip-deps` allow projects that run their own scanners/linters to disable each layer independently.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_VAL_1_RELEASE_DATE` (2026-05-06) are exempt automatically. CLI flag `--no-carry-over` disables for archive scans.

  CLI: `python -m tools.validate_slice_layers --slice <slice-folder> --changed-files <files...> [--secrets-allowlist <path>] [--pyproject <path>] [--requirements <path>] [--skip-secrets] [--skip-deps] [--json] [--no-carry-over]`. Exit codes: 0 clean (or carry-over exempt), 1 findings (Critical or Important), 2 usage error.

  - **Rule reference**: VAL-1
  - **Defect class**: Real-environment validation (curl the endpoint, render the page, install on a real device) catches behavioral failures but is structurally blind to two AI-assisted-development defect classes. (1) **Committed credentials**: an AI implementation may inline an API key for testing convenience and forget to revert; the slice's runtime checks pass because the key works, and the secret leaks. (2) **Hallucinated dependencies**: an AI implementation may write `from acme_helpers import compute` against a package that doesn't exist or wasn't declared in pyproject.toml; the import only fails at runtime in a code path the slice didn't exercise. Both classes typically reach `/reflect` and `/commit-slice` undetected because they don't break the validation runs themselves. VAL-1 closes the gap with two static checks at the validation step.
  - **Validation**: `tests/methodology/test_validate_slice_layers.py` — 24 tests over 15 fixtures (`tests/methodology/fixtures/validate_layers/`): parser unit tests (`_extract_pkg_name` handles version specifiers + extras + comments + URL specs; `_normalize_pkg` PEP 503; `_check_import_resolves` for stdlib + declared + alias), `parse_declared_deps` from pyproject.toml + requirements.txt, Layer A pattern detection (AWS, GitHub classic + fine + bot, JWT, private key, Anthropic, generic), allowlist suppression, `--skip-secrets` flag, Layer B detection (clean + hallucinated + aliased + relative), `--skip-deps` flag, run_layers integration aggregating both layers, NFR-1 carry-over + override, plus `/validate-slice` skill prose pin (VAL-1 + tool name + "credential scan" + "hallucinat..." substrings). Total methodology suite: 190 -> 214.

  Limitations (v1, documented in code):
  - **Python-only Layer B**. TS/JS dependency-hallucination check deferred to v2 (would need package.json parsing, scoped-package handling, peer-deps logic). The audit accepts non-Python files but doesn't lint their imports.
  - **Pattern set is starting point, not exhaustive**. Layer A covers the most common secret formats but misses vendor-specific ones (Stripe live/test keys, Twilio SIDs, etc.). Projects can extend by maintaining a project-local copy or by contributing patterns upstream.
  - **No fix-suggest action**. Layer B reports the missing import but doesn't propose adding the package to `pyproject.toml`. v2 candidate.
  - **Allowlist is global**. The `.secrets-allowlist` applies to all patterns equally; a v2 could scope by pattern name or file glob.
  - **No transitive-import resolution**. If a Python file imports `package_a`, and `package_a.foo` is what's imported, Layer B only checks `package_a` — it doesn't verify that `foo` is a real submodule. Out of scope for v1.

---

## v0.13.0 — 2026-05-06

Adds **TF-1** — test-first slice variant. Mission briefs gain an opt-in `**Test-first**: true` field; when set, the brief must include a `## Test-first plan` section mapping each AC to one or more tests with statuses tracked through the lifecycle (PENDING -> WRITTEN-FAILING -> PASSING). `/build-slice` Step 6 refuses non-PASSING rows at pre-finish.

### Added

- **TF-1 — Test-first slice variant**
  Adds `tools/test_first_audit.py` — a parser + validator for the test-first variant. Detects the opt-in `**Test-first**: true | false` field (case-insensitive, with or without hyphen normalization). When true: validates the `## Test-first plan` section exists with a 5-column markdown table (AC | Test type | Test path | Test function | Status); validates every AC referenced in the brief's `## Acceptance criteria` section (numbered list 1, 2, 3, ...) has at least one test-first row; validates each row's status is in `{PENDING, WRITTEN-FAILING, PASSING}`. With `--strict-pre-finish`, any non-PASSING row is a `non-passing-pre-finish` violation — used at `/build-slice` Step 6 to refuse declaring slice done while tests are still failing.

  Default-off semantics: a brief without the field (or with `Test-first: false`) is unaffected — the audit returns clean and `/build-slice` skips the gate. TF-1 is opt-in per slice; existing briefs continue to work without modification.

  Updates `skills/slice/SKILL.md` mission brief template + `templates/mission-brief.md`: documents the `**Test-first**:` field and the `## Test-first plan` 5-column table format. Updates `skills/build-slice/SKILL.md` Step 6 (pre-finish gate): runs the audit with `--strict-pre-finish` when the field is true; refuses on any of `missing-section`, `format`, `missing-cells`, `invalid-status`, `ac-without-row`, `non-passing-pre-finish`.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_TF_1_RELEASE_DATE` (2026-05-06) are exempt automatically. CLI flag `--no-carry-over` disables the exemption for archive scans.

  CLI: `python -m tools.test_first_audit <slice-folder> [--strict-pre-finish] [--json] [--no-carry-over]`. Exit codes: 0 clean (or default-off / carry-over exempt), 1 violations, 2 usage error.

  - **Rule reference**: TF-1
  - **Defect class**: AI-implemented slices have a chronic problem with test-after-the-fact patterns: tests are written to confirm the implementation already works, not to specify the behavior before it exists. Test-after tests are weaker because they're shaped by the code rather than the requirement, often miss negative paths the implementation already passes, and don't catch regressions because they were never red. Test-first discipline (red-green-refactor) flips the order: each AC produces a failing test BEFORE the implementation, then the implementation drives the test green. Without an explicit gate at pre-finish, a slice declaring test-first can quietly skip the discipline (write the implementation first, then add tests at the end). TF-1 makes the gate explicit and refusable, with statuses tracked per-test through the slice lifecycle.
  - **Validation**: `tests/methodology/test_test_first_audit.py` — 14 tests over 6 fixtures (`tests/methodology/fixtures/test_first/`): AC-label normalization (AC#1, ac 1, 1 -> 1), clean brief with all PASSING, default-off when field absent, missing-section when test-first true, invalid-status, ac-without-row (orphan AC), strict-pre-finish refuses non-PASSING, strict-pre-finish disabled allows PENDING/WRITTEN-FAILING, missing brief silent, carry-over mtime exemption + override, plus skill prose pins for `/slice` SKILL, `/build-slice` SKILL, and `templates/mission-brief.md`. Total methodology suite: 176 -> 190.

  Limitations (v1, documented in code):
  - **No filesystem existence check**. The audit doesn't verify that the test path + function actually exist on disk. v2 candidate: walk each row's `Test path`, parse it (Python ast / TS / Go), and verify the named test function exists.
  - **No actual test execution**. The audit trusts the declared status — it doesn't run the test runner to confirm PASSING actually passes or WRITTEN-FAILING actually fails. v2 candidate: integrate a runner adapter (pytest -k, vitest filter, go test -run).
  - **No build-log enforcement**. The audit doesn't verify that build-log.md events show test-first sequencing (test fails first, then implementation, then test passes). v2 candidate: parse `build-log.md` `## Events` section and check for `TEST: ... FAIL` entries followed by `TEST: ... PASS`.
  - **AC reference normalization is heuristic**. `AC#1`, `ac 1`, `1` all normalize to `1`; if a project uses different conventions (e.g., `[AC-005]`), normalization may miss the match. v2 could surface a parse-mode warning.

---

## v0.12.0 — 2026-05-06

Adds **RR-1** — risk register scoring. The `architecture/risk-register.md` migrates from a freeform 4-column table to an H2-structured format with explicit Likelihood and Impact fields; the audit tool computes Score and Band so `/slice` and `/status` can sort by score instead of grepping for "HIGH" or "active".

### Added

- **RR-1 — Risk register scoring**
  Adds `tools/risk_register_audit.py` — H2-structured parser for the risk register. Each risk is `## R-NN — <title>` followed by required fields (`Likelihood`, `Impact`, `Status`) and optional fields (`Reversibility`, `Mitigation`, `Discovered`, `Notes`). Score is computed as `Likelihood * Impact` with `low=1, medium=2, high=3` -> `1..9`. Band is derived: 1-2 = low, 3-4 = medium, 6-9 = high. The CLI supports `--filter-status`, `--filter-band`, `--sort=score|band|id`, `--top N`, `--json`, and `--warn-legacy` (opt-in deprecation hint for old table-format files).

  Updates `skills/triage/SKILL.md` Step 5: replaces the legacy `| ID | Risk | Reversibility | Spike? |` table with the H2 format and references the audit. Updates `skills/slice/SKILL.md` Step 1: candidate gathering now consumes scored risks via the audit (`--filter-status open --sort score --top 5`) instead of grepping for "HIGH"/"active". Updates `skills/status/SKILL.md`: surfaces top-3 open by score in the Risk exposure section.

  Opt-in migration: legacy table-format registers yield zero risks with no violation by default — projects migrate when ready. With `--warn-legacy`, a `legacy-format` violation surfaces so audits can flag the un-migrated state explicitly.

  CLI: `python -m tools.risk_register_audit <register.md> [--json] [--warn-legacy] [--filter-status STATUS] [--filter-band BAND] [--sort {score,band,id}] [--top N]`. Exit codes: 0 clean, 1 violations, 2 usage error.

  - **Rule reference**: RR-1
  - **Defect class**: Pre-RR-1, the risk register was a freeform 4-column table with no structured Likelihood/Impact fields. `/slice` and `/status` could only describe risks with text grep ("Active HIGH: 2 — R7, R11") and the human had to mentally re-classify entries each session. There was no audit-time check that a risk had complete information, no consistent vocabulary for status, and no way to mechanically pull "the top 3 unmitigated concerns." When the register grew past ~10 risks, it became a wall of text that nobody re-read. RR-1 makes the register structured + scored + sortable so risk-first ordering is mechanical and `/status` can surface signal without manual triage.
  - **Validation**: `tests/methodology/test_risk_register_audit.py` — 21 tests over 7 fixtures (`tests/methodology/fixtures/risk_register/`): score computation per band threshold, full-register parsing, optional-field capture, missing-required-field violation, invalid-status violation, duplicate-id violation, empty-register graceful handling, missing-file graceful handling, legacy-format silent-by-default + flagged-with-`--warn-legacy`, filter by status, filter by band, sort by score (desc with id-tiebreak), top-N limit, summary aggregates by band/status, `open_high_count` zero when all retired, plus skill prose pins (RR-1 reference + audit module reference + Likelihood/Impact field documentation in `/triage`, `/slice`, `/status`). Total methodology suite: 155 -> 176.

  Limitations (v1, documented in code):
  - **Likelihood × Impact only**. No exposure, time-to-detect, or weighted scoring (FAIR / FMEA-style). Sufficient for product-build risk; v2 candidate for compliance Heavy mode.
  - **Status vocabulary fixed**. {open, mitigating, retired, accepted} doesn't include "deferred" or "transferred"; sufficient for current pipeline use.
  - **No mitigation parsing**. The Mitigation field is captured as free text; v2 could parse spike refs and validate the spike file exists.
  - **No automatic migration**. Legacy table format is not auto-converted; projects migrate manually when adopting RR-1.

---

## v0.11.0 — 2026-05-06

Adds **TRI-1** — three-verdict + user-owned triage. Renames the critique verdicts (APPROVED -> CLEAN, APPROVED-WITH-FIXES -> NEEDS-FIXES; BLOCKED unchanged), inserts an explicit user-ratification step at `/critique` Step 4.5, and adds an audit tool that validates the resulting `## Triage` section in critique.md. Calibration vocabulary in `/reflect` Step 3 expands to include OVERRIDE-MISJUDGED so user-side override accuracy is tracked alongside Critic accuracy.

### Added

- **TRI-1 — Three-verdict + user-owned triage**
  Adds `tools/triage_audit.py` — parser + validator for the `## Triage` section in critique.md. The section captures: `Triaged by`, `Date`, `Final verdict`, plus a 4-column dispositions table (ID | Severity | Disposition | Rationale). Audit checks: section exists, required header fields present, final verdict is one of {CLEAN, NEEDS-FIXES, BLOCKED}, every body finding (`#### B1`, `#### M1`, `#### m1`) has a disposition row, dispositions are in the allowed vocabulary {ACCEPTED-FIXED, ACCEPTED-PENDING, OVERRIDDEN, DEFERRED, ESCALATED}, OVERRIDDEN/DEFERRED/ESCALATED rows have non-empty rationale, and declared final verdict matches the disposition pattern (any ESCALATED -> BLOCKED; else any ACCEPTED-PENDING -> NEEDS-FIXES; else CLEAN).

  Updates `agents/critique.md`: result-field rules now use CLEAN / NEEDS-FIXES / BLOCKED; verdicts are described as **provisional** (Critic emits) until user triage finalizes them.

  Updates `skills/critique/SKILL.md`: Step 4 now generates a Builder **draft** disposition (not a final response). New Step 4.5 (User-owned triage) explicitly prompts the user to ratify each finding's disposition; computes the final verdict mechanically from the disposition pattern; runs `triage_audit` and refuses on violations. The embedded critique.md template now includes the `## Triage` section.

  Updates `skills/reflect/SKILL.md` Step 3 calibration vocabulary: VALIDATED, FALSE-ALARM, **OVERRIDE-MISJUDGED** (new — user OVERRODE but reality showed Critic was right; calibration signal for both Critic AND user), NOT-YET, MISSED. The pre-TRI-1 `FALSE ALARM` (with a space) is replaced by `FALSE-ALARM` (hyphenated) for consistency with the new vocabulary tokens.

  Renames carried through `templates/critique-report.md`, `templates/milestone.md`, and `skills/commit-slice/SKILL.md`. All references to APPROVED / APPROVED-WITH-FIXES in load-bearing prose are removed; backward references in archive carry-overs are handled by the audit's mtime-based exemption.

  CLI: `python -m tools.triage_audit <slice-folder> [--json] [--no-carry-over]`. Exit codes: 0 clean (or carry-over exempt), 1 violations, 2 usage error.

  NFR-1 carry-over: critiques in slices whose `mission-brief.md` mtime predates `_TRI_1_RELEASE_DATE` (2026-05-06) are exempt automatically; archived critiques continue using their original verdict vocabulary without retroactive refusal.

  - **Rule reference**: TRI-1
  - **Defect class**: Builder dispositions were unaudited — the user had no formal authority over the gate. Pre-TRI-1, the Builder's "Builder response: disputed: ..." line could flip a critique from BLOCKED to APPROVED with no user ratification, and `disputed` was a single-bit decision that lost calibration signal (was the user right? was the Critic right? both? we couldn't tell). TRI-1 makes triage user-owned and explicit, with a richer disposition vocabulary (5 tokens replace 3) so calibration data sharpens both Critic prompt tuning AND user-judgement tracking. The OVERRIDE-MISJUDGED state is the load-bearing addition: if the user repeatedly overrides correct Critic findings, that's a user-side awareness signal that is invisible without the explicit category.
  - **Validation**: `tests/methodology/test_triage_audit.py` — 20 tests over 8 fixtures (`tests/methodology/fixtures/triage/`): verdict-computation unit tests (no findings -> CLEAN, ESCALATED dominates -> BLOCKED, PENDING -> NEEDS-FIXES, all-settled -> CLEAN), file-level audit tests (clean critique, needs-fixes critique, blocked critique, missing triage section, missing disposition row, missing rationale, invalid disposition, verdict-mismatch), carry-over (mtime exemption + --no-carry-over override), graceful missing-file handling, plus skill prose pins (TRI-1 reference + triage_audit module reference + Step 4.5 heading + disposition vocabulary + new verdicts + agent verdict alignment + reflect calibration vocabulary). Total methodology suite: 135 -> 155.

  Limitations (v1, documented in code):
  - **No automatic Builder draft -> final disposition link**. Builder draft text in `Builder draft:` lines is informational; the audit only enforces the table. v2 candidate: cross-link them (warn if Builder draft is OVERRIDDEN but the user's final disposition is ACCEPTED-PENDING).
  - **No Heavy-mode reviewer signature**. Heavy mode requires human sign-off but the audit doesn't yet validate a `Reviewed by:` field. v2 candidate.
  - **No retroactive verdict translation**. Archived critiques with old verdicts are exempt via carry-over but not auto-renamed; if needed, a one-shot migration script could rewrite them. Out of scope for TRI-1.
  - **No Critic-emitted-verdict vs user-final-verdict gap analysis**. Both are stored (Critic in body header `**Result**:`, user in `## Triage` -> `Final verdict`) but we don't yet compute or surface the delta. /critic-calibrate v2 candidate.

---

## v0.10.0 — 2026-05-06

Closes the lessons-learned -> builder feedback loop. Adds **BC-1** — a build-checks gate that surfaces curated, evergreen rules at `/build-slice` pre-finish based on the slice's changed files and mission-brief / design text. Promotion from per-project `lessons-learned.md` to per-project `architecture/build-checks.md` (or global `~/.claude/build-checks.md`) is manual at `/reflect` Step 5b.

### Added

- **BC-1 — Build-checks gate (lessons-learned -> builder feedback loop)**
  Adds `tools/build_checks_audit.py` — a markdown parser + applicability resolver for build-checks files. Each rule is an H2 heading prefixed `BC-` with structured fields: `Severity` (Critical | Important), `Applies to` (file globs OR `always: true`), `Trigger keywords` (comma-separated), `Check`, `Rationale`, `Validation hint`, `Promoted from`. Applicability is the OR of three signals: `always: true`, any glob matching any of `--changed-files`, or any keyword appearing as a case-insensitive substring of `mission-brief.md` + `design.md`. Reads both project (`architecture/build-checks.md`) and global (`~/.claude/build-checks.md`) and merges results. Updates `skills/build-slice/SKILL.md` Step 6 (pre-finish gate) to run the audit and surface applicable rules with refusal-on-Critical semantics. Updates `skills/reflect/SKILL.md` to add Step 5b: explicit user prompt asking whether a recurring pattern surfaced this slice should become a build-check, with the structured-field schema documented inline.

  Refusal semantics in `/build-slice`:
  - Critical applies: must be addressed before declaring slice done; not deferrable
  - Important applies: surfaced; defer-with-rationale allowed (matches the LINT-MOCK Important pattern)
  - Parse violation in build-checks.md (missing required field, invalid severity): exit code 1, fix format first

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_BC_1_RELEASE_DATE` (2026-05-06) are exempt automatically. CLI flag `--no-carry-over` disables the exemption for archive scans / CI.

  CLI: `python -m tools.build_checks_audit --slice <slice-folder> [--changed-files <files...>] [--project-checks <path>] [--global-checks <path>] [--json] [--no-carry-over]`. Exit codes: 0 success (rules surfaced or none apply), 1 parse violation in build-checks.md, 2 usage error.

  - **Rule reference**: BC-1
  - **Defect class**: Recurring patterns silently re-surface across slices. The lessons-learned journal records them ("EXIF orientation issue with HEIC uploads — slice 7", "rotation broken on Pixel uploads — slice 12", "PDF metadata orientation — slice 18") but `/build-slice` never reads it, so the same class of defect ships repeatedly until a human notices the pattern at retrospective. Without an evergreen-rules layer that the builder consults at every slice's pre-finish, lessons-learned is journalism, not engineering. BC-1 closes the loop: recurring patterns get curated into build-checks, build-checks get surfaced at every slice, surface-relevant ones force builder attention.
  - **Validation**: `tests/methodology/test_build_checks_audit.py` — 18 tests covering: glob matcher (single-segment `*`, multi-segment `**`, substring within filename, Windows separator normalization), parsing (clean file, always-true, glob-match, glob-no-match, keyword-only via mission-brief, missing-severity violation, invalid-severity violation, multi-rules with mixed applicability), source merge (project + global), carry-over exemption, `--no-carry-over` override, missing-file graceful handling, `/build-slice` BC-1 + tool-name reference pin, `/reflect` BC-1 + "recurring pattern" prose pin. Total methodology suite: 117 -> 135.

  Limitations (v1, documented in code):
  - **Surfaces, doesn't auto-verify**. The `Validation hint` field is human-readable; v2 will parse and execute it (e.g., run a grep / pytest -k command, refuse on non-zero exit).
  - **Manual promotion**. `/reflect` Step 5b prompts the user; recurring-pattern auto-detection across N reflections is deferred to a future `/critic-calibrate` extension.
  - **No rule-supersession mechanism**. Promoted rules accumulate; retiring or merging duplicates is manual.
  - **Glob limited to `*` and `**`**. No `{a,b}` brace expansion, no `?` single-char, no negation. Sufficient for v1 file targeting.

---

## v0.9.0 — 2026-05-06

Adds the wiring matrix discipline (WIRE-1). Every new module introduced by a slice must declare its consumer (entry point + test) or carry an exemption with rationale. Audited at `/build-slice` pre-finish; format validation enforced in v1.

### Added

- **WIRE-1 — Wiring matrix discipline**
  Adds `tools/wiring_matrix_audit.py` — a markdown table parser + format validator for the wiring matrix in each slice's `design.md`. Updates `skills/design-slice/SKILL.md` to require a `## Wiring matrix` section in the design.md template (4 columns: New module | Consumer entry point | Consumer test | Exemption). Updates `skills/build-slice/SKILL.md` Step 6 (pre-finish gate) to run the audit and refuse on Important findings.

  The matrix's purpose is structural: every new module/file declares a consumer demand (entry point + test) — preventing dead-modules-with-green-tests where unit tests pass but no entry point ever imports the module. Per Freeman & Pryce (*Growing Object-Oriented Software*) — "consumer demand precedes producer build".

  Exemption mechanism: a row with `internal helper, no consumer demanded — rationale: <reason>` in the Exemption column declares an internal helper without a direct consumer. The audit requires the literal `rationale:` substring; bare exemptions without rationale are flagged as `missing-rationale`. Empty matrices (header + separator + zero data rows) are accepted — the slice introduced no new modules.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_WIRE_1_RELEASE_DATE` (2026-05-06) are exempt automatically. The rule applies to slices authored on or after the rule's release. CLI flag `--no-carry-over` disables the exemption for testing / CI archive scans.

  CLI: `python -m tools.wiring_matrix_audit <slice-folder>` (auto-finds design.md inside) OR `python -m tools.wiring_matrix_audit <design.md>`. Options: `--json`, `--no-carry-over`. Exit codes: 0 clean (or carry-over exempt), 1 violations, 2 usage error.

  - **Rule reference**: WIRE-1
  - **Defect class**: Dead modules with green tests. A slice introduces a module (passes its own unit tests in isolation) but no entry point imports it — the module never runs in production. Without consumer-demand discipline, this drift is invisible at PR review and surfaces only when someone notices the module was never wired in. WIRE-1 catches it at design time by requiring the consumer to be declared upfront.
  - **Validation**: `tests/methodology/test_wiring_matrix_audit.py` — 11 tests covering: clean design (cells filled or rationalized exemption), missing-cells violation, missing-rationale violation, no-matrix violation, empty-matrix acceptance, missing design.md graceful handling, carry-over exemption with mtime, `--no-carry-over` flag override, missing-mission-brief means no carry-over claim, and skill-prose references in both `/design-slice` and `/build-slice`. Total methodology suite: 106 -> 117.

  Limitations (v1, documented in code):
  - **Format validation only**. A v2 will add existence/import audits: verify each Consumer entry point file exists in the repo, grep its contents for the named module's import + call site. The grep audit is the bigger structural value — without it, the matrix is a documentation discipline, not a refusal-on-dead-code mechanism.
  - **No multi-language module-name normalization**. Module names are treated as opaque strings; the audit doesn't validate Python dotted vs filesystem path conventions, TS module specifiers, or Go import paths.
  - **No test function existence check**. Consumer test cells like `tests/test_x.py::test_foo` are not split into file + function; only the surrounding format is validated. A v2 grep would also verify the function exists in the file.

---

## v0.8.0 — 2026-05-06

Adds Go support to the mock-budget linter (LINT-MOCK-3). Phase 3's mock-budget linter trio now covers Python, TypeScript/JavaScript, and Go.

### Added

- **LINT-MOCK-3 — Mock-budget linter (Go) — mock-budget rule v1**
  Extends `tools/mock_budget_lint.py` with Go support via the `tree_sitter` + `tree_sitter_go` packages (already in the shared venv). Detection covers any `call_expression` whose function name matches `^New(Mock|Fake|Stub|Spy)` — covering gomock-generated mocks (`mocks.NewMockUserService(ctrl)`), manual mocks (`NewMockHTTPClient()`), fakes (`fakes.NewFakeRepository()`), stubs, and spies. Test scopes are top-level `func TestXxx(t *testing.T)` declarations (with the `Test` + uppercase-letter convention to filter helpers like `Testing`) plus `t.Run("name", func ...)` subtest blocks. Mocks are attributed to the innermost containing scope. The dispatcher recognizes `.go` and routes to `_lint_go`. Updates `skills/build-slice/SKILL.md` to broaden the gate to "Python, TS/JS, and Go test files" with the LINT-MOCK-3 reference.

  Function declarations like `func NewMockUserService()` are correctly NOT counted — only `call_expression` nodes match, not `function_declaration` nodes (verified by a dedicated test).

  - **Rule reference**: LINT-MOCK-3
  - **Defect class**: Go test files were unlinted — gomock-generated mock proliferation in Go codebases (multiple `NewMockXxx(ctrl)` calls per `TestXxx` function) had no enforcement. Idiomatic Go testing with gomock makes it easy to bypass multiple internal interfaces in one test, which structurally bypasses the very integration seams the test pretends to verify. The Go extension closes that gap with the mock-budget rule (>1 mock per test = Important). Internal-mock classification is deferred to v2 — Go mocks are type-based without string targets, so accurate boundary classification requires import-aware analysis.
  - **Validation**: `tests/methodology/test_mock_budget_lint.py` adds 5 new tests covering Go clean file, too-many mocks (`TestUserAndOrder` with 2 NewMock* calls), syntax error graceful handling, declaration-vs-call disambiguation rot guard (`func NewMockX()` definitions must NOT count), and `/build-slice` LINT-MOCK-3 reference. Total methodology suite: 101 -> 106.

  Limitations (v1, documented in code):
  - `var x MockUserService` declarations not yet counted (constructor pattern is dominant in Go test code)
  - `testify/mock.Mock` embedding not yet detected (would require type-graph walk; v2 candidate)
  - `gomock.NewController(t)` itself not counted (it's infra; the `NewMockXxx` calls that follow are the actual mocks)
  - `seam_allowlist` parameter accepted but ignored for `.go` files in v1; reserved for v2 internal-mock support

---

## v0.7.0 — 2026-05-06

Adds TypeScript / JavaScript support to the mock-budget linter (LINT-MOCK-2). Same lint contract as the Python implementation — single tool, multi-language dispatch by file extension.

### Added

- **LINT-MOCK-2 — Mock-budget linter (TypeScript / JavaScript)**
  Extends `tools/mock_budget_lint.py` with TypeScript and JavaScript support via the `tree_sitter` + `tree_sitter_typescript` packages (already in the shared venv per `~/.claude/CLAUDE.md`). Detection covers `vi.mock`, `vi.spyOn`, `vi.doMock` (vitest); `jest.mock`, `jest.spyOn`, `jest.doMock` (jest); `td.replace` (testdouble); and `sinon.stub`, `sinon.replace`, `sinon.spy`, `sinon.mock` (sinon). Test scopes are `it()` / `test()` calls (and their `.only` / `.skip` / `.concurrent` / `.each` / `.todo` / `.fails` variants); mocks are attributed to the innermost containing scope. The TS boundary defaults (`_TS_BOUNDARY_DEFAULTS`) cover HTTP (axios, node-fetch, got, ky, undici), Node built-ins (`node:fs`, `fs`, `node:http`, `node:https`, `node:child_process`, etc.), databases (pg, mysql2, mongodb, mongoose, redis, prisma, knex, typeorm), cloud SDKs (`@aws-sdk`, `@google-cloud`, stripe, `@anthropic-ai/sdk`, openai, `@azure`), and email/messaging (nodemailer, kafkajs). Scoped npm packages (e.g., `@aws-sdk/client-s3`) match at the scope level. Relative imports (`./...`, `../...`, `/...`) are never boundaries.

  Refactor: the previous `lint_file` (Python-only) is renamed to `_lint_python`; a new `lint_file` dispatcher routes by file extension (`.py` -> `_lint_python`; `.ts` / `.tsx` / `.js` / `.jsx` / `.mts` / `.cts` -> `_lint_typescript`). Unsupported extensions return a `parse-error` finding rather than crashing — runners can pass any file path safely.

  Updates `skills/build-slice/SKILL.md` to broaden the LINT-MOCK gate to "Python and TS/JS test files" and adds the LINT-MOCK-2 rule reference.

  - **Rule reference**: LINT-MOCK-2
  - **Defect class**: TS test files were unlinted — internal-mock proliferation in TS codebases (`vi.mock('./services/user-service')`, `jest.mock('./api/receipts')`) had no enforcement. AI-generated TS tests gravitate toward mocking everything internal because mocks are syntactically easier than fixtures; without lint, this drift is invisible at PR review and surfaces only when production fails on the unmocked code path. The TS extension closes that gap with the same contract as the Python linter (mock budget + boundary check + seam-allowlist escalation).
  - **Validation**: `tests/methodology/test_mock_budget_lint.py` adds 9 new tests covering TS clean file, too-many mocks, internal-target, seam-with-allowlist, seam-without-allowlist, syntax error, boundary defaults coverage sanity, unsupported-extension graceful handling, and `/build-slice` LINT-MOCK-2 reference. Total methodology suite: 92 -> 101.

  Limitations (v1, documented in code): module-level `vi.mock` / `jest.mock` calls (hoisted; apply to all tests in the file) are not attributed to any specific test's count; only mocks inside the `it()` / `test()` body count. `beforeEach` / `afterEach` mocks are similarly not attributed. These are known gaps; a v2 may track module-level mocks as an implicit per-test contribution.

---

## v0.6.0 — 2026-05-06

Adds the Python mock-budget linter (LINT-MOCK-1) — the first AI SDLC rule that ships executable code rather than markdown-only discipline. Implements TDD-2 enforcement (≤1 mock per test, only at external boundaries) and integrates as a `/build-slice` pre-finish gate.

### Added

- **LINT-MOCK-1 — Mock-budget linter (Python)**
  Adds `tools/mock_budget_lint.py` — an AST-based linter for Python test files. Detects (1) test functions with >1 mock invocation (`mock-budget` violation, severity Important) and (2) tests that mock targets outside the external-boundary allowlist (`internal-mock` violation, severity Important; escalated to Critical if target is in `architecture/.cross-chunk-seams`). The boundary allowlist (`_BOUNDARY_DEFAULTS`) covers HTTP/networking, OS/process, filesystem, databases, cloud SDKs (boto3/google/stripe/anthropic/openai/azure), email/messaging, SSH, and time. Detection covers `@patch`, `@patch.object`, `@mock.patch` decorators and `patch(...)`, `mocker.patch(...)`, `mocker.spy(...)`, `mocker.patch.object(...)` inline calls. Integrated into `skills/build-slice/SKILL.md` Step 6 (pre-finish gate): Critical findings block; Important surface to user (Standard/Minimal) or block (Heavy with `--strict`). CLI: `python -m tools.mock_budget_lint <files...> [--seam-allowlist <path>] [--strict] [--json]`. Exit codes: 0 clean, 1 Critical present, 2 usage error.
  - **Rule reference**: LINT-MOCK-1
  - **Defect class**: Internal-mock proliferation hides integration seams. A test that mocks `UserService` and asserts behavior against the mock is verifying nothing real — the seam the mock pretends to verify is the seam the test silently bypasses (Freeman & Pryce GOOS — protocol drift). Mock-budget violations (>1 per test) compound this: each additional mock disconnects the test further from any single behavior the system actually exhibits. Without lint enforcement, this drift is invisible at PR review and only surfaces in production when the unmocked code path fails.
  - **Validation**: `tests/methodology/test_mock_budget_lint.py` — 12 tests over 5 fixtures (`tests/methodology/fixtures/mock_budget_*.py`): clean file, too-many-mocks, internal-class, seam-with-allowlist, seam-without-allowlist, syntax error, missing file, multi-file aggregation, allowlist file format (comments + blanks + trailing whitespace), missing allowlist file, boundary-defaults coverage sanity, `/build-slice` integration prose pin. Total methodology suite: 80 → 92.

### Changed

- **`pytest.ini`** — added `pythonpath = .` so the test suite can import `tools.mock_budget_lint` from anywhere under `tests/`. No effect on existing tests.

---

## v0.5.0 — 2026-05-06

Adds two improvements: per-pass model assignment for `/diagnose` (COST-1 extension), and explicit critic-calibrate cadence enforcement in `/status` (CAL-1).

### Added

- **COST-1.1 — Per-pass model assignment for /diagnose**
  Adds a Model column to the Step 5 dispatch table in `skills/diagnose/SKILL.md` specifying per-pass model based on cognitive shape: Sonnet for the 5 extraction-shaped passes (03a dead-code, 03c size-outliers, 03f layering, 03g dead-config, 03h test-coverage — reachability + grep + classification work), Opus for the 5 reasoning-shaped passes (01 intent, 02 architecture, 03b duplicates, 03d half-wired, 03e contradictions — synthesis + judgment + cross-module analysis). HTML assembly remains pure Python (no model). Step 6.5 narrator stays Opus. Pass 04-ai-bloat is dispatched in Step 6 separately and remains on the main-thread default.
  - **Rule reference**: COST-1.1 (extension of COST-1 to /diagnose passes)
  - **Defect class**: All 11 /diagnose passes running on the same model wastes Opus budget on extraction-shaped work. The cognitive shape varies — graphify reachable + grep cross-reference is Sonnet's job; semantic equivalence judging across modules is Opus's. A flat model assignment burns 5-10x cost on the extraction passes for no quality difference.
  - **Validation**: `tests/methodology/test_diagnose_pass_models.py` parametrizes over the 10 passes (excluding 04-ai-bloat) and verifies each row in Step 5 names the assigned model. Plus sanity checks: ≥5 extraction passes on Sonnet (rot guard against "everything on Opus"), ≥5 reasoning passes on Opus (rot guard against "everything on Sonnet to save more"), and a `COST-1.1` rule reference for traceability.

- **CAL-1 — Critic-calibrate cadence enforcement in /status**
  Adds explicit four-state cadence categorization to `skills/status/SKILL.md` Step 2: **within window** (0-9 slices), **approaching** (10-14), ⚠️ **recommended** (15-20), ⚠️⚠️ **overdue** (>20). When state is overdue, the calibration flag surfaces as the top line of "Recommended next action" in Step 3 output, overriding other suggestions until calibration runs. The check honors the deferred-first-run rule: empty calibration log + <10 archived slices = no warning, just "first calibration deferred until 10 slices accumulate".
  - **Rule reference**: CAL-1
  - **Defect class**: The "every 10-20 slices" cadence in `/critic-calibrate` was advisory; the previous `/status` had a single `If >15 slices: ⚠️ suggest running` line buried in metrics. Without explicit cadence enforcement, projects let calibration slip past 25, 30, 50 slices — at which point Critic calibration drift has accumulated and missed-pattern data is too noisy to mine effectively. The single-emoji warning was easy to miss; the double-emoji overdue escalation + override of next-action recommendations makes it actionable.
  - **Validation**: `tests/methodology/test_status_cadence_enforcement.py` verifies the SKILL.md prose contains the four cadence categories (within / approaching / recommended / overdue), the literal threshold numbers (10-20), the deferred-first-run language, override semantics for the overdue state, the double-emoji escalation pattern (⚠️⚠️), and a `CAL-1` rule reference.

---

## v0.4.0 — 2026-05-06

Adds cost-optimized model selection (COST-1). Three skills now explicitly dispatch their template-filling and rendering work to a Haiku subagent rather than running entirely on the main thread's model.

### Added

- **COST-1 — Cost-optimized model selection (Haiku-dispatched skills)**
  Adds explicit Haiku dispatch directives to `skills/commit-slice/SKILL.md` (Step 4 — commit message generation), `skills/status/SKILL.md` (Step 3 — summary rendering for default and brief modes), and `skills/archive/SKILL.md` (Step 3 — `slices/_index.md` regeneration; covers Step 4 archive catalog regeneration as well). The pattern: main thread gathers structured inputs (file reads + metric computation), then dispatches the formatting/rendering work to a `general-purpose` subagent with `model: haiku`. Quality is unchanged because the dispatched work is template-filling, not reasoning or synthesis — the cognitive demand is filling slots from a structured input dict, which Haiku does in a fraction of Opus's time and cost.
  - **Rule reference**: COST-1
  - **Defect class**: Skills running on the user's globally-set model (typically Opus) for work that has no reasoning component. `/commit-slice` fills a conventional-commit template from a structured dict — that's Haiku's shape, not Opus's. Running it on Opus burns ~5-10x cost for no quality difference. Same logic applies to `/status` (rendering metrics into a summary) and `/archive --index-only` (assembling tables from folder reads). Without explicit dispatch directives in each SKILL.md, the optimization sits unused — the executor doesn't know to delegate.
  - **Validation**: `tests/methodology/test_skill_model_dispatch.py` parametrizes over the three skills and verifies each SKILL.md contains (1) an explicit `model: haiku` directive, (2) a `subagent_type: "general-purpose"` reference, (3) a "Why Haiku" rationale section so future maintainers understand the cognitive-shape analysis, and (4) a `COST-1` rule reference for cross-link to the changelog. Skills missing any marker fail the test, which is the rot guard against future "to be safe, use Opus" reverts.

---

## v0.3.0 — 2026-05-06

Adds the named-subagent authoring guide and frontmatter conformance tests. New named subagents must conform to the documented frontmatter shape, tool-selection rules, and prompt structure conventions. Existing agents are pinned by static checks.

### Added

- **META-3 — Named-subagent authoring guide and frontmatter conformance**
  Adds `agents/AUTHORING.md` documenting when to use named subagents (vs forks vs general-purpose dispatch), the required frontmatter shape (`name`, `description`, `tools`, `model`), tool-selection rules (read-only roles MUST NOT have write tools), prompt structure conventions, calibration-awareness pattern, and self-test expectations. Adds `tests/methodology/test_agent_frontmatter.py` enforcing frontmatter conformance for every `agents/*.md` file (except `AUTHORING.md` itself), parametrized so new agents are checked automatically. Updates `README.md` to reference the new files.
  - **Rule reference**: META-3
  - **Defect class**: Future named subagents drift from established conventions (missing fields, mismatched name/filename, write tools granted to review roles, models picked by performance preference rather than cognitive demand) without an authoring guide. Drift compounds and erodes the load-bearing isolation property of named subagents — the Critic that becomes a rubber stamp because someone added `Write` to its tools and a "do helpful suggestions" instruction.
  - **Validation**: `tests/methodology/test_agent_frontmatter.py` runs as part of the methodology test suite. Tests verify (1) at-least-one named agent exists, (2) required-fields presence per agent, (3) name-matches-filename per agent, (4) model in allowed set per agent, (5) tools-non-empty per agent, (6) description substantive (>50 chars) per agent. Plus `test_authoring_guide_exists_and_pins_canonical_sections` pins canonical section headers in `AUTHORING.md` itself so the guide can't be paraphrased away.

---

## v0.2.0 — 2026-05-06

Adds the methodology self-test harness. From this version on, every behavior-changing rule introduced in a slice MUST have a corresponding pytest test that pins its prose, so silent paraphrase rot is prevented.

### Added

- **META-2 — Methodology self-test harness**
  Adds `tests/methodology/` directory with pytest harness and ~20 baseline tests covering load-bearing prose across `agents/critique.md`, `agents/critic-calibrate.md`, `agents/diagnose-narrator.md`, `agents/field-recon.md`, `skills/slice/SKILL.md`, `skills/build-slice/SKILL.md`, `skills/validate-slice/SKILL.md`, `skills/reflect/SKILL.md`, `skills/diagnose/SKILL.md`, plus self-tests for `methodology-changelog.md` (version sync, dated entries, rule-reference presence). Adds `pytest.ini` at repo root configuring `testpaths = tests`. Adds `tests/README.md` documenting setup, run, and how to add tests for new rules. CI hook documented (opt-in; no `.github/workflows/` shipped).
  - **Rule reference**: META-2
  - **Defect class**: Silent prose drift in load-bearing SKILL.md and agent files. A Critic prompt that reads "be thoughtful" produces different behavior than one that reads "assume the design is wrong until proven right" — and without enforcement, paraphrase rot is invisible until the Critic has degraded into a rubber stamp.
  - **Validation**: `pytest tests/methodology/ -v` runs cleanly and reports every test passing. `tests/methodology/test_methodology_changelog.py` validates VERSION ↔ changelog version sync and rule-reference presence per entry. Each subsequent slice that introduces a load-bearing rule MUST add a self-test for it; failure to do so is a violation of META-2 surfaced in `/critique`.

---

## v0.1.0 — 2026-05-06

Initial release of methodology versioning and changelog tracking.

### Added

- **META-1 — Methodology versioning + changelog**
  Adds `VERSION` file at the AI SDLC repo root tracking methodology semver. Adds `methodology-changelog.md` recording each behavior-changing rule with rule reference + defect class + validation method. `INSTALL.md` copies both to `~/.claude/` so they're discoverable from any project. `/status` reads `~/.claude/methodology-changelog.md` (if present) and surfaces the most recent dated entry as a Methodology section in default and full modes; the brief mode shows version on the header line.
  - **Rule reference**: META-1
  - **Defect class**: Methodology evolution had no audit trail. Users couldn't tell what changed between AI SDLC updates, why a new rule existed, or whether the methodology had drifted since they last looked. Without an audit trail, refinements get lost and speculative additions accumulate without scrutiny.
  - **Validation**: `VERSION` file exists at repo root with a semver string. `methodology-changelog.md` exists at repo root and has at least one dated entry. The most-recent entry's version matches `VERSION`. `INSTALL.md` Step 4 verifies both are copied to `~/.claude/`. `/status` reads the file gracefully (no error if missing) and surfaces version + most-recent rule.
