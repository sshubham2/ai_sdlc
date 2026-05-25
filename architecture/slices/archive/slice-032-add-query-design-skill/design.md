# Design: Slice 032 add-query-design-skill

**Date**: 2026-05-17
**Mode**: Standard (thin vault — design references code locations, no `components/`/`contracts/` files)

## Resolved design tension (was the mission brief's only open question)

The mission brief deferred *how* `query-design` hands off a discovered requirement: direct slice-candidate file authoring vs. pure delegation. **Resolved here → pure delegation, never direct authoring** (locked in [[ADR-032]], reversibility: cheap). Rationale: the skill's entire value proposition is "touches nothing." Writing a slice-candidate/backlog file is itself a mutation and would break the invariant the moment it fires. `/slice-candidates` also structurally requires an annotated `diagnosis.html` artifact `query-design` never produces. So: `query-design` produces conversation only; at session end, if a concrete requirement or defect surfaced, it presents a distilled summary and **offers to invoke** `/slice "<distilled intent>"` (single requirement) or recommends the `/diagnose` → `/slice-candidates` route (multiple/structural findings). The downstream skill performs its own writes under its own discipline; `query-design` itself never edits code, vault, or candidate files.

## What's new

- `skills/query-design/SKILL.md` (in-repo canonical) — the new skill's prose contract.
- `~/.claude/skills/query-design/SKILL.md` (installed copy, forward-synced byte-equal — runtime is what Claude reads).
- `tests/methodology/test_query_design_skill_drift.py` — per-file sha256 byte-equality test, mirroring `tests/methodology/test_slice_skill_drift.py` (MCT-1 / CAD-1 per-file pattern).
- One new changelog rule **QD-1** in `methodology-changelog.md` under a new `## v0.46.0 — 2026-05-17` entry.
- One new ADR: `architecture/decisions/ADR-032-query-design-readonly-delegation-only.md`.
- `tests/methodology/test_query_design_skill.py` — deterministic SKILL.md-prose structural pin (the AC4 verification element, per critique B3): asserts the SKILL.md body contains the grounding contract (read repo before answering; cite specific files/symbols), the delegation contract (OFFER `/slice`, never auto-invoke/never author), the three error-model clauses (stale graph, unanswerable, declined-handoff), **AND (re-critique-v2 M-add-v2-1) that the `_QD1_PHRASE` literal `"read-only, delegation-only codebase Q&A"` appears verbatim in `skills/query-design/SKILL.md`** — site (ii) of the 2-site canonical-phrase pin (the test imports/duplicates the same literal so a reword in either the changelog constant or SKILL.md fails a gate). Mirrors how MCT-1 / PCA-1 pin behavioral contracts as prose assertions rather than LLM-output dry-runs.
- `tests/methodology/test_methodology_changelog.py::test_v_0_46_0_qd_1_entry_present_in_repo_and_installed` + the `_V046`/`_QD1_PHRASE` module-constant pair — bespoke per-version entry-pin (DEVIATION-1). **Rule-ID-BEARING 4-assertion shape** (bci_1/scmd_1 class, NOT v0.43.0 rule-ID-less) — see the "Exact pin shape" spec under "Changelog entry note" for the full per-surface assertion list. This is the only test that verifies the v0.46.0 installed forward-sync.
- One new shippability catalog row (RPCD-1/SCPD-1) covering the new drift test — see **Shippability row grammar (SCMD-1)** below for the exact 6-cell shape.

## What's modified

- `tools/install_audit.py` — add `"query-design"` to `_CANONICAL_SKILLS` (alphabetical: after `"drift-check"`, before `"heavy-architect"`).
- `plugin.yaml` — add `- id: query-design` + one-line description (alphabetical position), AND bump `version: 0.46.0`.
- **PMI-1 atomic version bump — 4-part lockstep (CORRECTED at plan-mode; DEVIATION-1)**. The original design listed only `VERSION` + `plugin.yaml`. Shippability rows 28-31 + the slice-006/007 archived precedent establish the bump is a 4-part atomic set; all four MUST move together to 0.46.0:
  1. `VERSION` (in-repo, repo root) — `0.45.0` → `0.46.0`
  2. `~/.claude/ai-sdlc-VERSION` (installed; INST-1 install-time-renamed copy of `VERSION`, per `INSTALL.md:141`) — forward-sync to `0.46.0`
  3. `plugin.yaml` `version:` field — `0.45.0` → `0.46.0` (PMI-1 invariant: `plugin_manifest_audit` emits `version-mismatch` if `plugin.yaml.version != VERSION`)
  4. `~/.claude/methodology-changelog.md` — forward-sync of the new `## v0.46.0` entry (the in-repo↔installed parity asserted by the new `test_v_0_46_0_qd_1_entry_present_in_repo_and_installed`)
  INST-1 test asserts `sorted(plugin skill ids) == sorted(_CANONICAL_SKILLS)`; `plugin.yaml` is NOT itself forward-synced to `~/.claude/` (INST-1 do-not-copy list, methodology v0.20.0).
- `INSTALL.md` — hard-codes the skill count at **THREE** sites (verified, critique-review M-add-1): **L19** (`- **24 drop-in skills** — copied to ~/.claude/skills/`), **L185** (`(24 skills, 5 agents, 4 templates, methodology files, 13 tool modules importable)`), **L218** (`- ~/.claude/skills/ — markdown skill files (24)`). Adding `query-design` makes the true count 25 at all three; no audit pins any of this prose (verified: `test_install_audit.py` L249-262 asserts only substrings, no count) so it drifts silently. Per the count-agnostic lesson (slice-027), **rewrite ALL THREE to count-agnostic phrasing** (e.g. L19 "drop-in skills", L185 "the full canonical inventory of skills, agents, templates, methodology files, and importable tool modules", L218 "markdown skill files") rather than bumping 24→25 — L185's rewrite also incidentally retires the pre-existing stale "13 tool modules" figure (`_CANONICAL_TOOLS` is 22; not re-counted, the count-agnostic phrasing retires it). Single-site fixing (only L185) would ship L19+L218 stale — the exact silent-prose-drift defect M1 names, surviving at 2 of 3 instances. This is prose-only and **ungated** — explicit must-not-defer item + a pre-finish grep guard.

## Shippability row grammar (SCMD-1) — exact contract for the new row (critique B1)

The real `architecture/shippability.md` is a **6-column** table (verified L7): `| # | Slice | Critical path | Command | Runtime | Machine-cmd |`. `test_shippability_command_column.py::test_every_row_has_machine_stable_command_or_violation` runs the audit against the real catalog and asserts ZERO `missing-machine-cmd` / `prose-segment` violations on **every** data row; `test_shippability_decoupling_audit.py::test_real_catalog_scmd1_clean` + `test_cited_fn_set_derived_from_all_rows_not_enumerated` derive the cited-fn set from **every row's `Machine-cmd` cell**. Therefore the new row MUST be a full 6-cell row whose `Machine-cmd` cell is a **prose-free** interpreter-anchored invocation matching `_SEGMENT_RE` — no leading bareword (e.g. NOT `` Drift: `…` ``). Concretely the `Machine-cmd` cell is:

`` `<PY> -m pytest tests/methodology/test_query_design_skill_drift.py tests/methodology/test_query_design_skill.py -q` ``

(both new test files in one `pytest` invocation; `;`-separation only if two distinct interpreter anchors are needed). **Mid-slice smoke-gate addition**: after the row is added, `& $PY -m tools.shippability_decoupling_audit` and the SCMD-1 command-column audit MUST exit 0 — added to the mission-brief mid-slice gate.

## SCMD-1 decoupling classification of the new drift test (critique B2 — verify BEFORE writing the test)

`test_slice_skill_drift.py` reads `Path.home() / ".claude" / "skills" / "slice" / "SKILL.md"` directly and is **not** SCMD-1-flagged today, but the design must not copy the pattern on faith (the "audit's own parse rules are a design-stage blind spot" lesson, N+3). **Build-time prerequisite, gated at mid-slice smoke**: before authoring `test_query_design_skill_drift.py`, run `& $PY -m tools.shippability_decoupling_audit` and inspect the cited-fn classification to establish the *verified predicate* by which existing per-file drift tests are clean (candidate: per-file drift tests are not in the catalog-cited module-derivation set, OR `Path.home()` reads without an archive-corpus reference are not "incidental" by the audit's actual predicate). The new test (and its new shippability row, which DOES enter the cited-fn derivation per B1) MUST inherit that same verified exemption — if it would be classified `incidental`/coupled, STOP and redesign the row/test rather than ship a coupled catalog row. The allowlist is pinned by `test_allowlist_membership_is_exactly` (`_ALLOWLIST_SYMBOLS`, `_RESOLVE_THROUGH ⊇ {REPO_ROOT, read_file}`) — the new test must resolve clean WITHOUT requiring an allowlist edit (an allowlist change would be an unscoped SCMD-1 surface change, out of scope).

## What's reused

- `skills/slice-candidates/SKILL.md`, `skills/discover/SKILL.md`, `skills/status/SKILL.md` — delineation references (what `query-design` is NOT) and structural precedent for an out-of-loop, user-invoked skill.
- `skills/slice/SKILL.md` — the handoff target `query-design` may invoke (one-way coupling; `/slice` is unmodified).
- [[ADR-006]]-class CAD-1 forward-sync precedent; [[slice-007-install-time-rename]] INST-1 parity precedent; [[slice-009-recursive-self-application]] methodology-surface self-hosting precedent.

## Components touched

### query-design skill (new)
- **Responsibility**: A read-only, interactive, truthful Q&A about the *existing* codebase. Answers grounded strictly in actual repo reads (Read / Grep / graphify); changes nothing. On a surfaced requirement/defect, offers a declinable handoff to `/slice` — never authors files.
- **Lives at**: `skills/query-design/SKILL.md` (canonical) + `~/.claude/skills/query-design/SKILL.md` (runtime). Created by this slice.
- **Key interactions**: read-only graphify queries (`graphify-out/graph.json`), Read/Grep over repo; *invokes* `/slice` via the Skill tool only on explicit user acceptance.
- **Out-of-loop — verified mechanism (critique M3, not analogy)**: `pipeline_chain_audit.audit()` iterates `_CANONICAL_CHAIN` only (verified `tools/pipeline_chain_audit.py` L200); `test_pipeline_position_block_drift.py::_SKILLS` is derived `[skill for skill,_,_ in _CANONICAL_CHAIN]` (verified L31). A skill absent from `_CANONICAL_CHAIN` is therefore **neither audited nor parametrized** for a `## Pipeline position` block — so `query-design` carries none. The Builder **MUST NOT add a `## Pipeline position` block** to this skill (adding one is harmless to PCA-1 but misrepresents the out-of-loop class and misleads future readers). The named out-of-loop peers (`/status`, `/diagnose`, `/reduce`, `/drift-check`) are illustrative, not the mechanism.
- **Read-only enforcement mechanism (critique M2 — documented decision)**: the official Claude Code skills spec supports an `allowed-tools` SKILL.md frontmatter field as platform-native tool restriction. **Verified**: zero skills in this repo use `allowed-tools` (`grep -rl allowed-tools skills/` → 0), including read-only peers `/status`, `/diagnose`, `/drift-check`; the project convention is `name:` + `description:` frontmatter only, and these skills run **inline in the main thread** via the Skill tool (not as packaged-plugin restricted subagents — where `allowed-tools` semantics apply). Introducing `allowed-tools` solely for `query-design` would be an unprecedented divergent mechanism of unverified efficacy in the inline-skill execution path. **Decision**: `query-design` follows project convention — read-only is enforced by (a) unambiguous SKILL.md prose, (b) the QD-1 changelog rule, (c) the drift test pinning that prose against silent divergence. This is recorded in ADR-032 Consequences as an examined, deliberate choice, not an oversight.

### install_audit / plugin.yaml / VERSION (modified)
- **Responsibility**: canonical skill enumeration + version parity.
- **Lives at**: `tools/install_audit.py`, `plugin.yaml`, `VERSION`.
- **Key interactions**: `test_install_audit.py` L201-202 asserts plugin-skill-ids set == `_CANONICAL_SKILLS`; `test_methodology_changelog.py` asserts `VERSION` == newest changelog version AND `VERSION` == `plugin.yaml.version` (PMI-1). All three MUST move in lockstep.

## Contracts added or changed

None. No endpoints, events, schemas, or data model. The "contract" here is the SKILL.md prose contract (the read-only / delegation-only invariant), enforced by ADR-032 + QD-1 + the drift test, not a code interface.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. This slice introduces no new importable code module — the new artifacts are a markdown skill (`SKILL.md`) and a pytest test file (itself a consumer, not a consumed module). `plugin.yaml`/`install_audit.py`/`VERSION` are modifications to existing files. Zero new-module rows → audit treats as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `skills/query-design/SKILL.md` | Claude runtime (Skill tool dispatch) + `plugin.yaml` enumeration + `tools/install_audit.py:_CANONICAL_SKILLS` | `tests/methodology/test_query_design_skill_drift.py::test_in_repo_and_installed_query_design_skill_md_are_content_equal` (drift) AND `tests/methodology/test_query_design_skill.py` (prose-contract pin, AC4) | — |

## Decisions made (ADRs)

- [[ADR-032]] — `query-design` is an out-of-loop, read-only, delegation-only exploratory skill: it never writes code/vault/candidate files, never auto-advances, and carries no `## Pipeline position` block; requirement handoff is by offering to invoke `/slice`, declinable — reversibility: **cheap**. (Updated post-critique M2: ADR-032 Consequences now records the examined decision to enforce read-only via project-convention prose + QD-1 + drift test rather than the unprecedented `allowed-tools` frontmatter.)

## Changelog entry note (critique m1 — CORRECTED at /build-slice plan-mode; DEVIATION-1)

**The original m1 disposition was built on a factually false precedent and is hereby reversed.** Plan-mode read `tests/methodology/test_methodology_changelog.py` and found that **every** changelog version v0.22.0 → v0.45.0 carries a `test_v_0_NN_0_*_entry_present_in_repo_and_installed` test — **24/24, no exceptions**. The cited "slice-029 no-rule-lineage precedent" is false: slice-029 (v0.43.0) **has** `test_v_0_43_0_diagnose_sequential_dispatch_entry_present_in_repo_and_installed` (line 2590) despite minting no new rule-ID. The convention is universal and rule-lineage-independent.

**Corrected decision**: this slice **DOES add** `tests/methodology/test_methodology_changelog.py::test_v_0_46_0_qd_1_entry_present_in_repo_and_installed`. Rationale: (a) the generic `test_each_changelog_entry_carries_rule_reference` + `test_version_matches_most_recent_changelog_entry` gates read the **in-repo file only** — without the bespoke per-version test the v0.46.0 installed forward-sync would be the ONLY unverified one in 25 versions; (b) omitting it is a 25th-version inconsistency vs a 24/24 universal convention (slice-022 self-violation). This is convergence to an existing convention, not over-build.

**Exact pin shape — RULE-ID-BEARING 4-assertion (re-critique-v2 M1+M2; pre-read against the actual test source `test_methodology_changelog.py:2502-2581`)**. QD-1 is a **minted audited rule** (design L15/L97), so the pin MUST take the **rule-ID-BEARING** shape of `test_v_0_44_0_bci_1` (L2508) / `test_v_0_45_0_scmd_1` (L2546) — the more precise precedent is `bci_1`, whose docstring encodes the "minted rule, NOT rule-ID-set-only, anti-silent-weakening" intent that applies identically to QD-1 (a behavioral-contract rule pinned against prose erosion). It **MUST NOT** take the rule-ID-LESS `test_v_0_43_0` (L2590) shape, which asserts `"no rule-ID" in body` and would be actively wrong for a minted rule. The new test asserts, **in BOTH the in-repo `methodology-changelog.md` AND the installed `~/.claude/methodology-changelog.md` surfaces** (the scmd_1 dual-surface loop, NOT whole-file — `_extract_version_body`-scoped to prevent sibling-version bleed, per the slice-018 sibling-scoping discipline scmd_1 inherits):
  1. `## v0.46.0` header present in `content`
  2. `body = _extract_version_body(content, "0.46.0")`; `"QD-1" in body` (rule-reference layer)
  3. `_QD1_PHRASE in body` — define a module constant pair mirroring `_V045`/`_SCMD1_PHRASE` (L2504-2505): `_V046 = "0.46.0"` and **`_QD1_PHRASE = "read-only, delegation-only codebase Q&A"`** (the QD-1 canonical invariant phrase — the anti-weakening guard so a future edit cannot silently erode QD-1 to a non-read-only rule). **Canonical-phrase propagation — 2 TEST-PINNED sites (re-critique-v2 M-add-v2-1; corrects the original N≥2-vs-3-sites inconsistency)**: the phrase originates in the changelog and MUST appear verbatim in exactly two **independently test-pinned** locations: (i) the v0.46.0 changelog entry body — pinned here by `test_v_0_46_0_qd_1` (the `### Added` rule block, so the literal sits inside the `_extract_version_body`-scoped region; the "QD-1 rule text" occurrence is this same site, not a third); (ii) `skills/query-design/SKILL.md` — pinned by an explicit new assertion in `test_query_design_skill.py` (see What's-new bullet). The precedent (`_SCMD1_PHRASE`/`_BCI1_PHRASE`) pins only site (i) (N=1); QD-1 deliberately pins N=2 — strictly stronger, applying bci_1's anti-silent-weakening rationale to the *runtime* artifact (SKILL.md), not only the changelog. Leaving the SKILL.md occurrence unpinned would recreate the exact silent-prose-drift defect class this slice exists to prevent (v1 M-add-1 INSTALL.md-1-of-3 analogue, now N=2).
  4. `"ADR-032" in body` (decision lineage — single ADR; bci_1/scmd_1 assert two each, QD-1 has only ADR-032)

The build MUST author the v0.46.0 entry so all four tokens (`## v0.46.0`, `QD-1`, the `_QD1_PHRASE` literal, `ADR-032`) appear in the `_extract_version_body`-scoped entry body, in BOTH surfaces (the 4-part PMI-1 forward-sync guarantees the installed surface).

## ADR sentinel note (critique m2 — OVERRIDDEN)

ADR-032's `supersedes: null` was flagged for convention-check. **Verified**: the most recent ADR (`ADR-031`, header L8) uses exactly `supersedes: null`. ADR-032 already conforms — no change. `tools/supersede_audit.py` (SUP-1) parses this sentinel; `null` is the in-repo convention. No action.

## Authorization model for this slice

N/A — no auth surface. The relevant access-control concern is *capability scoping*: the SKILL.md MUST explicitly forbid Write/Edit/NotebookEdit against source/vault/candidate files and forbid any non-declined auto-invocation. This is the load-bearing safety property; it is enforced by ADR-032 + QD-1 changelog rule + the drift test pinning the contract prose against silent divergence.

## Error model for this slice

No new error codes. Failure modes to address in SKILL.md prose (must-not-defer): (1) graphify graph stale/missing → instruct rebuild (`$PY -m graphify code .`) rather than answering ungrounded; (2) question unanswerable from repo evidence → state that explicitly, do not speculate (grounding invariant); (3) user accepts handoff → invoke `/slice` with distilled intent; user declines → end cleanly with no side effect.
