---
id: ADR-025
title: Pipeline-chain auto-advance via a normalized `## Pipeline position` directive + auto-invoke contract, enforced by the PCA-1 audit
date: 2026-05-16
slice: slice-027-add-pipeline-chain-auto-advance
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-025: Pipeline Chain Auto-advance (PCA-1)

**Note on rule-ID naming** (conforms to [[ADR-019]]'s test-pinned naming note; does NOT supersede it): PCA-1 is an **audit-enforced gate** at slice-runtime (`tools/pipeline_chain_audit.py` invoked at `/build-slice` Step 6), NOT a `/critique`-time prose-heuristic discipline. It therefore takes the **bare `PCA-1` form — NO `-D` suffix**, joining the audit-enforced-gate naming class alongside BC-1, CAD-1, PMI-1, INST-1, WIRE-1, BRANCH-1, UTF8-STDOUT-1, CRP-1. The `-D` suffix remains reserved for `/critique`-time prose heuristics with no programmatic audit (RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 / TPHD-1 / BFRD-1 / PTFCD-1's sub-clause).

## Context

The per-slice loop is `/slice → /design-slice → /critique → /critique-review → /build-slice → /validate-slice → /reflect`, then the user runs `/commit-slice`. Every one of those seven transitions today requires the operator to manually re-invoke the next skill. Each in-loop skill already ends with a human-readable `## Next step` prose section naming the successor — so the *knowledge* of "what's next" is present, but it is advisory narrative for a human, not a directive Claude acts on, and it is not uniform (some are single-line, some are conditional bullet lists, `adopt` even has both an H2 `## Next step` and a separate inline `Next step:` prose label).

User direct request at `/slice-027` invocation: *"read all skills again each skill should know which is the next appropriate skill in the pipeline. Also slice loop should auto trigger next skill unless user feedback or user input is required till just before commit-slice skill. User will always invoke commit-slice skill."* Two concrete asks: (a) every skill carries an explicit, machine-actionable successor; (b) the loop auto-advances unless a user-input gate is hit, hard-stopping before `/commit-slice` (always user-invoked).

This is a methodology-surface change (`skills/*/SKILL.md`) → mandatory-Critic trigger regardless of tier (CLAUDE.md "In-house methodology surfaces"); tier set `high` (novel cross-cutting behavioral change spanning the whole loop). The discipline is structurally analogous to BRANCH-1 (slice-021) and CRP-1 (slice-026): a skill-runtime mechanism enforcing a cross-skill invariant the operator could otherwise get wrong, backed by a `tools/<name>_audit.py` from day one.

The critical hazard is **auto-advancing past a state that needs the user** (e.g., past `/critique` TRI-1 user-owned triage, or past a `/validate-slice` FAIL). The design is fail-closed: any state not provably gate-free surfaces to the user; auto-advance is the privileged, narrowly-enumerated path.

## Options considered

### Option 1 — Normalized `## Pipeline position` H2 section in all 8 skills + auto-invoke prose + canonical gate enumeration + PCA-1 audit (CHOSEN)

Append a fixed-schema `## Pipeline position` H2 section (after the existing `## Next step`, which is left untouched) to the 7 in-loop skills **plus `commit-slice`** (declared as the user-invoked terminus, so the successor graph is closed and the audit's terminal check is well-formed). The section carries structured fields (`predecessor`, `successor`, `auto-advance`, `on-clean-completion`, `user-input gates`) AND the imperative instruction Claude executes on clean completion. `reflect` and `commit-slice` carry `auto-advance: false`. Gate-bearing skills (`critique`, `build-slice`, `validate-slice`) get an explicit gate-halt directive inline at each enumerated gate. Add `tools/pipeline_chain_audit.py` (PCA-1), invoked at `/build-slice` Step 6 pre-finish, validating: all 8 blocks present + well-formed; successor edges == canonical chain; `reflect`/`commit-slice` non-auto/terminal. Codify in `methodology-changelog.md` v0.41.0; pin canonical phrase `Pipeline position` across N=3 surfaces (skill section + in-repo changelog + installed changelog). Mirror BRANCH-1/CRP-1 audit shape (dataclass, exit 0/1/2, UTF8-STDOUT-1 stdout). Atomic PMI-1 bump 0.40.0 → 0.41.0.

**Pros**:
- Defense-in-depth: prose directive drives the runtime behavior; the audit refuses any build where the chain graph drifted (8-file cross-consistency is exactly the drift class audits exist for).
- Existing `## Next step` prose is untouched → zero regression risk to the human-narrative the section already serves; the new block is purely additive.
- `commit-slice` in the coverage set closes the graph: the audit can assert the terminal boundary positively rather than by absence.
- Fail-closed gate model: auto-advance is the enumerated privilege; everything else surfaces to the user.
- Reversibility cheap; revert = git diff + superseding changelog entry. Magnitude ≈ BRANCH-1/CRP-1 (well-trodden).

**Cons**:
- ~30 touches (8 skill edits ×2 for forward-sync + audit + install_audit + plugin.yaml + 3 version files + changelog ×2 + ADR + shippability + CLAUDE.md + tests). Larger than `-D` prose-only codifications; same magnitude band as BRANCH-1 (MEDIUM, ~1 day).
- Two forward-sync surfaces (7 in-loop skills) lack a per-file byte-equality gate beyond `slice`'s mini-CAD — the slice-026 M-add-1 watch-list class. Mitigated: PCA-1's own audit greps the *in-repo* copies; `install_audit` existence-checks the installed copies; a general `tools/skill_drift_audit.py` remains the deferred N≥2 follow-on (not in scope here — see Limitations).

### Option 2 — Prose-only directive, no audit

Add the `## Pipeline position` prose to the skills but ship no `tools/pipeline_chain_audit.py`; rely on Claude reading the prose.

**Rejected** — same cost-asymmetry argument as [[ADR-019]] Option 2: the successor-graph-across-8-files invariant is *mechanically checkable* (grep + edge compare). Deferring an audit when the check is mechanically trivial is YAGNI-in-reverse: the audit is cheaper than the prose-pin test mass needed to defend 8 files against drift, and it belongs in the `/build-slice` Step 6 audit family (BRANCH-1/CRP-1/PMI-1/BC-1) at the same surface level. Audit-from-day-one is the right enforcement level.

### Option 3 — Encode the directive in SKILL.md frontmatter instead of a body section

Put `successor:` / `auto-advance:` keys in each SKILL.md YAML frontmatter.

**Rejected** — frontmatter is currently `name`/`description`(/`argument-hint`) only; loading behavioral control into frontmatter is a non-obvious convention break, and the auto-advance behavior still needs imperative *body* prose for Claude to act on (frontmatter is metadata, not instruction). A single body section co-locating the structured contract with the imperative instruction is simpler and matches the existing `## Prerequisite check` / `## Next step` H2-section idiom. (CRP-1's `critique-review-skip:` frontmatter key is the right tool for a *single optional escape-hatch flag*, not for a multi-field behavioral contract.)

### Option 4 — Also auto-advance `/reflect → /slice` (continuous multi-slice autonomy)

Extend the chain past `/commit-slice` so the next slice auto-starts.

**Rejected at slice-027** — the user explicitly bounded the loop "till just before commit-slice"; starting the next slice is a deliberate human decision (candidate selection, scope). Out of scope per mission brief; listed as a future-slice candidate (`add-cross-slice-auto-kickoff`) only if the user later asks.

## Decision

**Adopt Option 1.** Codified as **PCA-1** in `methodology-changelog.md` v0.41.0. Canonical phrase `Pipeline position` pinned across N=3 surfaces. The `## Pipeline position` schema (fields, order, `auto-advance` boolean semantics) is canonically defined once in the v0.41.0 changelog entry and referenced (not duplicated) from skill prose and the audit, per RPCD-1.

Coverage set = 8 skills: `slice`, `design-slice`, `critique`, `critique-review`, `build-slice`, `validate-slice`, `reflect` (in-loop, `auto-advance: true`), + `commit-slice` (terminus, `auto-advance: false`, user-invoked).

Canonical user-input-gate enumeration (auto-advance HALTS, surface to user, resume only on explicit user action):
- `/critique` Step 4.5 — TRI-1 user-owned triage (dispositions)
- `/critique` verdict BLOCKED — design revision required
- `/build-slice` plan-mode — ExitPlanMode user approval
- `/build-slice` mid-slice smoke gate — failure
- `/validate-slice` — any per-criterion FAIL
- `/validate-slice` — any PARTIAL (per-criterion or aggregate `Result: PARTIAL`; the skill's outcome is 3-valued PASS|PARTIAL|FAIL) — user-decides-remediation, same disposition as FAIL; explicit per must-not-defer #1 / the M3 principle, not catch-all-covered (fixes /critique-review M-add-1)

These 5 are the load-bearing *named* gates. Per /critique M3 (must-not-defer #1 demands the enumeration be *explicitly* complete, not reliant on the catch-all alone): `design.md` §"Canonical gate enumeration — explicitly COMPLETE per 8-skill coverage" carries the canonical per-skill table stating, for every one of the 8 skills, its halt conditions OR an explicit no-gap statement of why it has no clean-path user gate (notably `/critique-review` — its non-clean / Builder-Critic-disagreement output is reconciled *at* `/critique` Step 4.5 TRI-1, the already-enumerated HALT, not auto-advanced past it; `/slice` candidate-selection and `/design-slice` clarifying-questions halts are bounded by those skills' existing Critical-rules prose, no new gate prose needed). That table is the RPCD-1 canonical reference, mirrored into the v0.41.0 changelog schema.

Fail-closed rule: any state not provably matching a clean-completion transition surfaces to the user; auto-advance is never the default for an ambiguous state. `/commit-slice` is never auto-invoked under any path.

PMI-1 atomic version bump 0.40.0 → 0.41.0 (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`), version-agnostic gate preserved (no test-body modification).

**PCA-1 bootstrap-self-application at slice-027**: slice-027 is PCA-1 bootstrap-reference instance #1 (mirrors slice-021/BRANCH-1, slice-026/CRP-1). The `## Pipeline position` directive does not exist on disk during this slice's own loop, so this slice's chaining is driven manually by the main thread per the user's at-invocation directive (the pre-codification equivalent of PCA-1). Recursive self-application is discharged by `tools/pipeline_chain_audit.py` run against the repo at Step 6 (expect exit 0) + `/critique-review` on slice-027. First non-bootstrap reference instance = the next slice after 027.

## Consequences

**Immediate (slice-027 ship)**:
- 8 `skills/<name>/SKILL.md` gain a `## Pipeline position` section (in-repo) + 8 installed forward-sync mirrors.
- Gate-halt directive inserted at 5 gate sites across `critique`/`build-slice`/`validate-slice` SKILL.md.
- `tools/pipeline_chain_audit.py` created; `tools/install_audit.py` `_CANONICAL_TOOLS` + `plugin.yaml` `tools:` gain `pipeline_chain_audit`.
- `skills/build-slice/SKILL.md` Step 6 pre-finish gains a `- [ ] PCA-1 audit passes` checklist bullet + invocation.
- `methodology-changelog.md` v0.41.0 entry (in-repo + installed) with PCA-1 + schema + canonical gate list + Limitations.
- `architecture/decisions/ADR-025-*` (this file); `architecture/shippability.md` new row enumerating PCA-1 critical-path checks; `CLAUDE.md` Brownfield-rules gains a `Pipeline auto-advance` bullet.
- `VERSION`/`ai-sdlc-VERSION`/`plugin.yaml.version` 0.40.0 → 0.41.0.
- Tests: `test_methodology_changelog.py` v0.41.0 entry-pin + ADR-025 pin; per-skill prose-pin asserts for the 8 `## Pipeline position` blocks; `tests/methodology/test_slice_skill_drift.py` stays green post forward-sync; `tests/methodology/test_pipeline_position_block_drift.py` (parametrized byte-equality over all 8 skill pairs — AC #5 verification element, fixes /critique M1+M2); `tests/methodology/test_pipeline_chain_audit.py` (≥2 unit tests). Audit-test location is `tests/methodology/` — there is no `tests/tools/` dir (fixes /critique B1).

**Downstream (slice-028+)**:
- Every in-loop skill, on clean completion with no pending gate, auto-invokes its successor; the operator interacts only at the enumerated gates and at `/commit-slice`.
- PCA-1 audit at Step 6 refuses any future slice that drifts the chain graph (e.g., a renamed skill not reflected in a `successor:` edge).
- Manual single-skill invocation remains fully supported (the directive is "auto-invoke on clean completion", not "forbid manual runs").
- Future-slice candidates: `add-cross-slice-auto-kickoff` (Option 4, only on explicit user ask); `add-skill-drift-audit` (general 8-skill byte-equality gate; the slice-026 M-add-1 watch-list, promote at N≥2).

## Reversibility

**Reversibility: cheap** with magnitude justification (per the slice-009→slice-026 cheap-with-magnitude-justification convention). **Magnitude ≈ 30 touches** — same band as BRANCH-1 (ADR-019, ~30) / CRP-1 (ADR-024); MEDIUM effort (~1 day), well within the codification-slice budget and revert path well-trodden by 10 prior codification slices.

**Revert path**: (1) `git revert` the slice-027 merge commit (or `git reset --hard <pre-027>` if pre-merge); (2) append a superseding `methodology-changelog.md` entry retiring PCA-1; (3) delete `tools/pipeline_chain_audit.py` + `tests/methodology/test_pipeline_chain_audit.py` + `tests/methodology/test_pipeline_position_block_drift.py` + the new prose-pin/entry-pin/ADR-pin tests; (4) drop `pipeline_chain_audit` from `install_audit` + `plugin.yaml`; (5) forward-sync reverted SKILL.md ×8 + changelog + `ai-sdlc-VERSION` to `~/.claude/`, confirm byte-equality; (6) atomic post-retirement version bump.

**Irreversible portion** (minor, append-only, documentation-record-class): the v0.41.0 changelog entry and any slice-028+ slices that ran under PCA-1 become part of the append-only record; retraction is a superseding entry, not a deletion. Does not prevent revert.

**Conclusion**: Reversibility is **cheap**; magnitude **≈30 touches** (BRANCH-1/CRP-1 band, MEDIUM, ~1 day). Adopt Option 1.
