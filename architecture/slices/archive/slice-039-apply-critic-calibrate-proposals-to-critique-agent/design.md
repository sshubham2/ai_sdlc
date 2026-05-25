# Design: Slice 039 apply-critic-calibrate-proposals-to-critique-agent

**Date**: 2026-05-18
**Mode**: Standard

## What's new

- `agents/critique.md` — TWO prose insertions (the two user-ACCEPTED 2026-05-17 calibration proposals), then forward-synced to `~/.claude/agents/critique.md` (CAD-1, EOL-agnostic per [[decisions/ADR-033]]):
  - **Proposal 2 → Dim 7 sub-bullet** "Methodology-surface RULE-ID + entry-pin obligation" inserted as a NEW bullet immediately after the existing Dim 7 "Does it write to vault folders…" bullet (`agents/critique.md:121`), before `### 8. Web-known issues` (`:123`). A checklist pass (explicitly SEPARATE from deep-dive): for any slice touching an in-house methodology surface, verify either **(a)** a RULE-ID + a `test_v_0_NN_0_<rule>_entry_present_in_repo_and_installed` entry-pin + an atomic PMI-1 version bump, **OR (b)** a documented "why none" that is verified against `tests/methodology/test_methodology_changelog.py` — NOT a Builder-asserted prior-slice precedent (the precedent must be confirmed against the enforcing artifact, not taken on assertion). Names rule-ID **MEPD-1**.
  - **Proposal 1 → Dim 9 sub-clause #12** "Audit-parse-rule empirical-execution discipline" inserted as a NEW `- **…**` sub-clause immediately after the "Phantom test-file citation discipline" sub-clause's SHOULD-list paragraph (ends `agents/critique.md:199`), before `### Bonus: weak graph edges` (`:201`). When a slice changes an audit's parse-rule (regex / parser / field-line matcher / token splitter), the Critic MUST **Bash-execute** the changed rule against an adversarial battery — own-brief field-lines, trailing-annotation, substring-collision, empty/absent, CRLF — file a **Blocker** on any silent-disable / default-off / false-FAIL / over-match, and state in the finding that the battery was *executed*, not reasoned. Names rule-ID **APED-1**. Carries the canonical N=3-MISS + N=1-CATCH evidence anchors (slices 030A / 031 / 033 MISS; slice-034 empirical-execution CATCH).
- `tests/methodology/test_critique_agent.py` — content-pin tests for both new clauses (mirrors the slice-037 M-add-1 anti-tautology pattern — content-pinning, NOT CAD-1-byte-equality-tautology):
  - **Supersede** `test_critique_dim_9_lists_eleven_sub_clauses` → `test_critique_dim_9_lists_twelve_sub_clauses` (PMI-1 structural-invariant supersession applied at the structural-invariant level; no two structural-invariant count tests coexist — slice-011/013/015/016/024/025 precedent chain, N=7 stable). The superseded test adds the new 12th title assertion `assert "Audit-parse-rule empirical-execution discipline" in CRITIQUE`.
  - `test_critique_dim_9_audit_parse_rule_empirical_execution_sub_clause_present` + `_location_pinned` (between `Phantom test-file citation discipline` and `### Bonus: weak graph edges`) + `_names_aped_1_rule_id` + `_cites_audit_parse_rule_evidence_anchors` (asserts the 030A/031/033 + 034 anchors) + **`_pins_behavioral_obligation`** (per Critic M1 — the slice-037 M-add-1 anti-tautology law applied symmetrically to APED-1: asserts the load-bearing behavioral verbs `"Bash-execute"`, `"Blocker"`, the `executed, not reasoned` phrase, AND ≥2 adversarial-battery member tokens `"substring-collision"` + `"CRLF"` are present in CRITIQUE — this pin FAILS if the obligation is silently weakened, e.g. `MUST Bash-execute` → `should reason about`, even while title/location/rule-ID/evidence-anchor pins stay green; without it the APED-1 pin set tautologically passes on a weakened clause).
  - `test_critique_dim_7_methodology_surface_entry_pin_sub_bullet_present` + `_location_pinned` (between `7. Drift from vault` and `### 8. Web-known issues`) + `_names_mepd_1_rule_id` + `_names_both_clauses` (the behavioral-content pin: asserts the (a) RULE-ID+entry-pin+PMI-1 and (b) verified-why-none / **not-Builder-asserted-precedent** halves — FAILS if either obligation half is dropped; this IS the symmetric anti-tautology pin M1 requires APED-1 to also carry).
- `tests/methodology/test_methodology_changelog.py` — NEW entry-pins (the AC4 dogfood of MEPD-1; content-pinning per slice-037 M-add-1):
  - `test_v_0_52_0_aped_1_entry_present_in_repo_and_installed`
  - `test_v_0_52_0_mepd_1_entry_present_in_repo_and_installed`
  - `test_v_0_52_0_critique_proposals_shippability_consumer_propagation` — **(reformulated per DR-1 meta-Critic M-add-1; supersedes the original Critic-m2 `not in catalog` formulation, which was a guaranteed false-FAIL — see Triage)**: asserts (i) **zero `::test_critique_dim_9_lists_eleven_sub_clauses` SELECTOR tokens remain** in any `Command` / `Machine-cmd` cell (the discriminator is the `::test_critique_dim_9_` selector prefix — NOT a blanket `_lists_eleven_sub_clauses not in catalog`, which would false-FAIL on the legitimately-preserved line-34 frozen narrative); (ii) `::test_critique_dim_9_lists_twelve_sub_clauses` present in **all 14 LIVE selector positions** (lines 14/19/21/23/24/32 = 2 each = 12; line 34 = 2); (iii) the line-34 frozen `` `_lists_ten_sub_clauses` -> `_lists_eleven_sub_clauses` `` PMI-1-supersession narrative is explicitly **allow-listed / asserted UNCHANGED**; (iv) the new v0.52.0 catalog row exists (SCPD-1 proactive-application pin).
- `methodology-changelog.md` — NEW `## v0.52.0 — 2026-05-18` entry carrying **both** rule-references (APED-1 + MEPD-1) under one `### Added` section; 4-part PMI-1 atomic bump 0.51.0→0.52.0 (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + this file forward-synced to `~/.claude/methodology-changelog.md`).
- `architecture/shippability.md` — (i) **SCPD-1 propagation (corrected per DR-1 M-add-1)**: rename **only the `::test_critique_dim_9_lists_eleven_sub_clauses` SELECTOR tokens** → `::test_critique_dim_9_lists_twelve_sub_clauses` across rows **6, 11, 13, 15, 16, 24, 25** = shippability.md lines 14/19/21/23/24/32/34. **Mechanically verified occurrence map: 15 total `_lists_eleven_sub_clauses` occurrences = 14 LIVE selector tokens to rename (lines 14/19/21/23/24/32 carry 2 live selector tokens each — the bare-`Command`-cell + the backticked-`Machine-cmd`-cell duplicate = 12; line 34 carries 2 live selector tokens) + 1 FROZEN historical-narrative occurrence at line 34** (the slice-025 row "Why" prose `` `_lists_ten_sub_clauses` -> `_lists_eleven_sub_clauses` `` PMI-1-structural-invariant-supersession record — slice-025 superseded ten→eleven; a blanket substring rename here would corrupt it to a false "ten→twelve" claim). The frozen occurrence is **deliberately PRESERVED** (slice-025's own "2 historical-narrative occurrences preserved" precedent; same frozen-history class as changelog:266). Executed in the same `/build-slice` block BEFORE the `/validate-slice` Step 5.5 catalog run (proactive-application mode, slice-014 precedent — NOT reactive/fixed-when-fails). (ii) NEW catalog row binding the v0.52.0 entry-pins + the new content-pin tests (SCPD-1 consumer-propagation for the two new rules discharged HERE at `/design-slice`, per `_index.md:48` — NOT auto-blessed "no row", NOT deferred to `/reflect`). **Scope boundary (per Critic m1 + DR-1 M-add-1 — FBCD-1 sub-mode (a) full-repo enumeration, applied symmetrically to BOTH frozen-history twins)**: a full-repo grep of `_lists_eleven_sub_clauses` matches two frozen-history sites that are **deliberately NOT renamed** — (1) `methodology-changelog.md:266` (frozen v0.39.0 PTFCD-1 entry `Validation:` line; not an executed consumer — no audit runs changelog `Validation:` lines) and (2) `architecture/shippability.md` line 34 (slice-025 row "Why"-prose PMI-1-supersession narrative, distinguished from live tokens by the ABSENCE of the `::test_critique_dim_9_` selector prefix). SCPD-1 propagation is scoped to the 14 live selector tokens + `tests/methodology/test_critique_agent.py` self-references; both frozen-history occurrences are enumerated-and-excluded sites, not missed ones.
- `architecture/critic-calibration-log.md` — the 2026-05-17 run `### Proposals` table (L455–458) "User action" cells updated `ACCEPTED (2026-05-17) — user to apply manually` → `APPLIED slice-039 (2026-05-18)`; Run-summary row optional note.

## What's reused

- [[slice-037-extend-ptfcd-1-to-test-function-level]] — the canonical precedent for "apply a calibration-derived Critic-prompt discipline": its design.md is the structural template (CAD-1 forward-sync, content-pin not tautology, SCPD-1 row, atomic changelog). [[decisions/ADR-038]] is the rule-ID-minting precedent (new `-D` ID, refine/supersede-nothing, NOT a `vN.N` label).
- [[slice-034-fix-tf1-audit-field-line-regex]] — the R-7 N+1 LIVE miss that empirically motivates APED-1 (the audit-vs-its-own-artifact interaction the dual-Critic stack structurally cannot reach; only the BC-PROJ-4 real-artifact run caught it).
- `agents/critique.md:115-152` Dim 7 + Dim 9 structure; the existing 11 sub-clause titles enumerated by `tests/methodology/test_critique_agent.py:115`.
- `tools/critique_agent_drift_audit.py` — CAD-1 EOL-agnostic content-equality gate (the must-not-defer installed sync).
- `tools/plugin_manifest_audit.py` (PMI-1) + `tools/install_audit.py` (INST-1) — version-bump consistency backstop (no skill/agent/tool added or removed this slice → manifest unchanged except `version`).
- `architecture/critic-calibration-log.md:453-458` — the fixed, accepted proposal text (this slice consumes it verbatim-to-intent; it does NOT re-derive or re-run `/critic-calibrate`).

## Components touched

### `agents/critique.md` (modified — prose codification, in place)
- **Responsibility**: the adversarial Critic prompt. Gains one Dim 7 checklist sub-bullet (MEPD-1) and one Dim 9 cross-cutting sub-clause (APED-1).
- **Lives at**: `agents/critique.md` (Dim 7 insert after `:121`; Dim 9 insert after `:199`, before `:201`); forward-sync to `~/.claude/agents/critique.md`.
- **Key interactions**: CAD-1 (`tools.critique_agent_drift_audit`); the `/critique` + `/critique-review` agents that read it at runtime; `tests/methodology/test_critique_agent.py` content-pins.

### `tests/methodology/test_critique_agent.py` (modified)
- **Responsibility**: content-pins the load-bearing Critic prose; structural-invariant sub-clause count.
- **Lives at**: supersede `_lists_eleven_sub_clauses`→`_lists_twelve_sub_clauses` (`:115`); add 8 new content-pin functions (4 per proposal).
- **Key interactions**: consumed by shippability rows 6/11/13/15/16/24/25 (the SCPD-1 surface) + the new v0.52.0 row.

### `tests/methodology/test_methodology_changelog.py` (modified)
- **Responsibility**: entry-pin the v0.52.0 changelog entry in-repo↔installed (the MEPD-1 dogfood) + the SCPD-1 propagation assertion.
- **Lives at**: add `test_v_0_52_0_aped_1_*`, `test_v_0_52_0_mepd_1_*`, `test_v_0_52_0_critique_proposals_shippability_consumer_propagation` under a NEW dedicated `# --- Slice-039 / APED-1 + MEPD-1 entry pinning ---` section header (EPGD-1: separate section header from any PMI-1 gate; no shared intervening prose — no PMI-1 versioned-gate is superseded this slice, so the EPGD-1 build-time-slip mode does not apply, but the dedicated-section-header discipline is followed regardless).

## Contracts added or changed

No HTTP/event/CLI contracts. The "contracts" changed are **prompt contracts** (Critic behavioral obligations) and **test-name contracts**:
- `test_critique_dim_9_lists_eleven_sub_clauses` is renamed (superseded) → `test_critique_dim_9_lists_twelve_sub_clauses`. This is a structural-invariant supersession; the consumer surface is `architecture/shippability.md` rows 6/11/13/15/16/24/25 (enumerated above) + any docstring/prose self-reference. Propagation is proactive (slice-014 mode), in the build block before `/validate-slice`.
- No audit exit-code / JSON-shape contract changes (this slice changes prose + test functions only; it does NOT modify any audit's regex/parser — therefore APED-1's own trigger condition does not fire on slice-039's build, see Self-application below).

## Data model deltas

None (no persistence).

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new modules** (prose edits to an existing agent file + new test functions in existing test modules + a new changelog entry). Zero-row matrix → clean per the audit.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[decisions/ADR-040]] — Rule-ID minting for both proposals: Proposal 1 → NEW minted `-D`-suffix **APED-1** ("Audit-Parse-rule Empirical-execution Discipline"), a Dim 9 cross-cutting sub-clause #12; Proposal 2 → NEW minted `-D`-suffix **MEPD-1** ("Methodology-surface Entry-Pin Discipline"), a Dim 7 checklist sub-bullet. Both refine nothing / supersede nothing. The `-D` suffix denotes the behavioral class "/critique-time prose-heuristic discipline" (NOT "Dim 9 membership" — Dim-9 membership is incidental to most prior `-D` rules, not definitional); MEPD-1 is the first `-D` rule deliberately homed outside Dim 9, and ADR-040 pins that the class boundary is behavioral. -D calibration trail N=9 → N=11. Follows the [[decisions/ADR-038]] / TFFL-1↔TF-1 mint-not-version precedent. — reversibility: **cheap**
- [[decisions/ADR-041]] — Both proposals ship under ONE changelog version (`v0.52.0`) with two `Rule reference`s + two entry-pins, rather than two sequential single-rule versions. They were generated by one calibration run, accepted in one user action, and applied in one atomic Critic-prompt edit cycle; splitting into v0.52.0 + v0.53.0 would imply an ordering/dependency that does not exist and double the PMI-1 bump churn. — reversibility: **cheap**

## Authorization model for this slice

N/A — local prompt + test + vault edits, no actors/permissions. Critic is mandatory here on the in-house-methodology-surface trigger (`agents/critique.md`, `methodology-changelog.md`, `tools/**` consumers, `tests/methodology/**`) — `critic-required: true` already set in milestone.md.

## Error model for this slice

No runtime error paths (no executable behavior added). Failure modes are gate failures, all loud:
- CAD-1 non-zero → in-repo/installed `agents/critique.md` diverge (must-not-defer; mid-slice smoke gate catches after Proposal 1).
- `_lists_twelve_sub_clauses` superseded but a shippability row still cites `_eleven_` → `/validate-slice` Step 5.5 FAIL (prevented by the proactive SCPD-1 propagation phase + the `test_v_0_52_0_critique_proposals_shippability_consumer_propagation` pin).
- Entry-pin present in-repo but not installed (forward-sync miss) → `test_v_0_52_0_*_entry_present_in_repo_and_installed` FAIL.
- **Anti-tautology guard**: each new content-pin must FAIL if its proposal prose were absent (slice-037 M-add-1 law) — the entry-pin tests assert the *clause anchor strings*, not CAD-1 byte-equality; verified by the mid-slice gate transiently removing/restoring an anchor (build-log evidence).

## Self-application (RSAD-1 / slice-022 self-violation law — stated explicitly)

This slice authors two Critic disciplines; per RSAD-1 the Critic at `/critique` will (and should) stress-test slice-039's own `mission-brief.md` / `design.md` / `ADR-040` / `ADR-041` against APED-1 and MEPD-1:
- **MEPD-1 self-check**: slice-039 IS a methodology-surface slice → it must itself satisfy MEPD-1 clause (a): RULE-IDs (APED-1, MEPD-1) + entry-pins (`test_v_0_52_0_aped_1_*`, `test_v_0_52_0_mepd_1_*`) + atomic PMI-1 bump. AC4 is exactly this dogfood; the design satisfies it by construction.
- **APED-1 self-check**: APED-1's trigger is "a slice changes an audit's parse-rule". Slice-039 changes prose + adds test functions; it does **not** modify any audit's regex/parser/field-matcher → APED-1's empirical-execution battery is **not** required for slice-039's own build (stated so the Critic sees this was reasoned, not missed — mirrors slice-037 design's explicit self-violation-law note).
- **Phantom-citation (PTFCD-1/PTFFD-1) self-check**: every test path/function this design cites (`tests/methodology/test_critique_agent.py::test_critique_dim_9_lists_twelve_sub_clauses`, the 8 new functions, the 3 new changelog-test functions) is created BY this slice — the build plan creates each before the catalog row referencing it (mission-brief smoke-gate ordering), so no phantom citation. Conventions are not cited; only concrete function names.
