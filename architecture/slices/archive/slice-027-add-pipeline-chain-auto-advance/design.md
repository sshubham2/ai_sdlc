# Design: Slice 027 add-pipeline-chain-auto-advance

**Date**: 2026-05-16
**Mode**: Standard

## What's new

- A normalized, machine-actionable `## Pipeline position` H2 section appended to **8** pipeline skills: the 7 in-loop skills (`slice`, `design-slice`, `critique`, `critique-review`, `build-slice`, `validate-slice`, `reflect`) **plus** `commit-slice` (declared as the user-invoked terminus so the chain graph is closed and auditable).
- An auto-advance behavioral contract codified as **PCA-1** (Pipeline Chain Auto-advance): on successful completion with **no pending user-input gate**, an in-loop skill auto-invokes its declared successor via the Skill tool, without waiting for the user.
- A canonical user-input-gate enumeration; an explicit gate-halt directive placed at each gate site in the gate-bearing skills (`critique`, `build-slice`, `validate-slice`).
- A new audit `tools/pipeline_chain_audit.py` (PCA-1) — BRANCH-1/CRP-1-modeled — that verifies every covered skill carries a well-formed `## Pipeline position` block, the successor edges match the canonical chain, and the terminal boundary (`reflect → commit-slice`, `commit-slice`) is marked non-auto / user-invoked.
- Methodology codification: `methodology-changelog.md` v0.41.0 entry (in-repo + installed), `architecture/decisions/ADR-025-*`, `architecture/shippability.md` new row, `CLAUDE.md` Brownfield-rules bullet, methodology test additions, atomic version bump.

## What's reused

- `## Next step` sections already in every skill (`skills/*/SKILL.md`) — left **unmodified**; they remain the human-narrative companion to the new machine-actionable block. Lower drift risk than rewriting them.
- BRANCH-1 / CRP-1 codification shape — [[decisions/ADR-019]], [[decisions/ADR-024]]. `tools/branch_workflow_audit.py` and `tools/critique_review_prerequisite_audit.py` are the structural templates for the new audit (dataclass result, exit 0/1/2, UTF8-STDOUT-1 stdout).
- `tools/install_audit.py` `_CANONICAL_TOOLS`, `plugin.yaml` `tools:` list, `VERSION` / `~/.claude/ai-sdlc-VERSION` / `plugin.yaml.version` PMI-1 atomic-bump invariant.
- `tests/methodology/test_slice_skill_drift.py` (mini-CAD for `skills/slice/SKILL.md`) — stays green after forward-sync of the new section.
- Gate sites already in code: `skills/critique/SKILL.md` Step 4.5 (TRI-1 user-owned triage) + BLOCKED path; `skills/build-slice/SKILL.md` plan-mode (ExitPlanMode) + mid-slice smoke gate; `skills/validate-slice/SKILL.md` per-criterion FAIL.

## Components touched

### `## Pipeline position` section — 8 skill files (`skills/<name>/SKILL.md`)
- **Responsibility**: declare, in a fixed machine-actionable shape, each skill's successor and whether completion auto-advances; carry the imperative auto-advance instruction Claude executes.
- **Lives at**: `skills/{slice,design-slice,critique,critique-review,build-slice,validate-slice,reflect,commit-slice}/SKILL.md` (modified — new H2 section appended after `## Next step`); each forward-synced to `~/.claude/skills/<name>/SKILL.md` (INST-1).
- **Key interactions**: read by Claude at skill-completion time; greped by `tools/pipeline_chain_audit.py`.

### `tools/pipeline_chain_audit.py` (new)
- **Responsibility**: structural gate — fail the build if the pipeline-chain directive graph is malformed or incomplete.
- **Lives at**: `tools/pipeline_chain_audit.py` (created); registered in `tools/install_audit.py` `_CANONICAL_TOOLS` + `plugin.yaml` `tools:`.
- **Key interactions**: invoked at `skills/build-slice/SKILL.md` Step 6 pre-finish (defense-in-depth, alongside BRANCH-1/CRP-1/PMI-1/BC-1); reads the 8 SKILL.md files.

### Gate-halt directive — `critique`, `build-slice`, `validate-slice`
- **Responsibility**: at each enumerated user-input gate, instruct Claude to NOT auto-advance, surface to the user, and STOP until explicit user action.
- **Lives at**: inline at the existing gate sites (critique Step 4.5 + BLOCKED; build-slice plan-mode + mid-slice smoke; validate-slice per-criterion FAIL).

## Contracts added or changed

No HTTP/event contracts. The "contract" is the **`## Pipeline position` block schema** (prose contract, parsed by the audit):

```
## Pipeline position

- **predecessor**: <skill or "(loop entry)">
- **successor**: <skill>
- **auto-advance**: true | false
- **on-clean-completion**: <imperative — e.g. "invoke `/design-slice` via the Skill tool without waiting for the user">
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - <gate 1> | (none)
```

- **`auto-advance: false`** is mandatory for `reflect` (successor `/commit-slice`) and `commit-slice` (terminus). All 7 in-loop non-terminal transitions are `auto-advance: true`.
- **Verdict-dependent / self-loop successors** (fixes /critique-review m-add-1): `/critique` has a conditional successor — `/build-slice` on CLEAN/NEEDS-FIXES (post-TRI-1) but a `/critique`→`/critique` **self-loop** on BLOCKED (re-run after redesign). The flat `**successor**: <skill>` field models only the primary edge; the conditional/self-loop is expressed in the `on-clean-completion` free-text imperative field (e.g. "on CLEAN/NEEDS-FIXES post-TRI-1 invoke `/build-slice`; on BLOCKED do NOT auto-advance — redesign then re-run `/critique`"). The audit's "successor edges == canonical chain" check (line 11) MUST treat the primary `successor` field as authoritative for chain-shape and MUST tolerate (not flag as malformed) the documented `/critique` BLOCKED self-edge. No safety impact (TRI-1 HALT dominates — auto-advance never fires from `/critique` without a user pass-through); this note exists to prevent a latent audit false-positive at `/build-slice` Step 6 if the Builder hard-codes a single-successor expectation.
- Exact field names/order are pinned by `ADR-025` and the audit; canonical schema reference lives in the changelog entry — not duplicated elsewhere (RPCD-1).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/pipeline_chain_audit.py` | `skills/build-slice/SKILL.md` Step 6 pre-finish gate (+ `tools/install_audit.py` `_CANONICAL_TOOLS`) | `tests/methodology/test_pipeline_chain_audit.py::test_clean_chain_exits_zero` + `::test_missing_block_exits_one` | — |

> Audit-test location convention (verified): every `_CANONICAL_TOOLS` peer's unit tests live at `tests/methodology/test_<name>.py` (e.g. `tests/methodology/test_branch_workflow_audit.py`, `tests/methodology/test_critique_review_prerequisite_audit.py`). There is no `tests/tools/` directory. (Fixes /critique B1.)

## AC #5 byte-equality verification element (fixes /critique M1 + M2)

AC #5 asserts "all touched in-repo skill copies remain byte-equal to their installed copies (mini-CAD / CAD-1 class)" over **8** skills, but only `skills/slice/SKILL.md` (`test_slice_skill_drift.py`) and `skills/build-slice/SKILL.md` (`test_build_slice_skill_drift.py`) have full-file drift tests, and `install_audit` only *existence*-checks installed skill dirs (no content compare). Without a delivering element AC #5 is unverifiable for 6 of 8 skills (Wiegers traceability gap) AND the installed chain could go silently stale (slice-026 M-add-1 watch-list, now load-bearing for runtime behavior).

**Element**: this slice ships `tests/methodology/test_pipeline_position_block_drift.py` — a **parametrized** test over all 8 skill pairs (`slice`, `design-slice`, `critique`, `critique-review`, `build-slice`, `validate-slice`, `reflect`, `commit-slice`) asserting the extracted `## Pipeline position` section is **byte-equal** between `skills/<name>/SKILL.md` and `~/.claude/skills/<name>/SKILL.md`. Section-scoped (not full-file) — cheaper than 6 new full mini-CADs, and precisely targets the runtime-behavioral surface this slice introduces. This gives AC #5 a 1:1 traceable verification element for every touched skill. The full-file mini-CAD generalization for the 6 un-mini-CAD'd skills remains the deferred `add-skill-drift-audit` N≥2 follow-on (out of scope; recorded in ADR-025 future-slice candidates).

**Propagation checklist for `tools/pipeline_chain_audit.py`** (fixes /critique m2 — new-tool consumer-propagation roll-up sentinel, N=5): (a) add to `tools/install_audit.py` `_CANONICAL_TOOLS`; (b) add to `plugin.yaml` `tools:`; (c) first statement conforms to UTF8-STDOUT-1 (`_stdout` UTF-8 reconfigure, mirroring `branch_workflow_audit`/`critique_review_prerequisite_audit`); (d) update the hard-coded module-count narrative — `tools/install_audit.py:66` comment "19 tool modules post-slice-026" → 20, and any UTF8-STDOUT-1 `tools_scanned` narrative in `skills/build-slice/SKILL.md` — and any test asserting the count; (e) `/build-slice` Step 6 pre-finish gains a `- [ ] PCA-1 audit passes` bullet + invocation.

## Decisions made (ADRs)

- [[ADR-025]] — PCA-1 pipeline-chain auto-advance: normalized `## Pipeline position` directive + auto-invoke contract + canonical gate enumeration + audit-enforced gate; rule-ID is NON-`-D` (audit-enforced-gate class, conforms to [[ADR-019]]) — reversibility: **cheap**

## Authorization model for this slice

N/A — methodology-surface change; no runtime authz. The only "authority" boundary is the user-input-gate enumeration: auto-advance is **denied** past any enumerated gate (fail-closed — an unenumerated ambiguous state defaults to surfacing to the user, never to silent auto-advance). This is the slice's critical safety property (mission-brief Must-not-defer #1).

### Canonical gate enumeration — explicitly COMPLETE per 8-skill coverage (fixes /critique M3)

Must-not-defer #1 demands the enumeration be *explicitly* complete, not reliant only on the fail-closed catch-all. Per-skill clean-path halt conditions:

| Skill | Auto-advance | User-input HALT conditions on the path through this skill |
|-------|--------------|------------------------------------------------------------|
| `slice` | true | Candidate selection — HALT unless the user supplied explicit intent OR said "you pick"/autonomous (per `/slice` Critical rules + Step 3b). Bug-fix BFRD-1 STOP-route → HALT. |
| `design-slice` | true | Real design ambiguity → `/design-slice` Step 2 clarifying questions (≤4) → HALT. No clean-path plan-mode (plan mode is `/build-slice`, not here). |
| `critique` | true | (i) Step 4.5 TRI-1 user-owned triage → **HALT (always, by methodology — Builder cannot self-ratify)**; (ii) verdict BLOCKED (any ESCALATED) → HALT (redesign / `/risk-spike`). |
| `critique-review` | true | Clean path has NO user gate — its output feeds `/critique` Step 4.5 TRI-1, which is itself the enumerated HALT. A non-clean / Builder-Critic-disagreement verdict does NOT auto-advance past TRI-1; it is reconciled *at* TRI-1. (Explicit no-gap statement, not silence.) |
| `build-slice` | true | (i) plan-mode ExitPlanMode user approval → HALT; (ii) mid-slice smoke-gate failure → HALT (STOP, diagnose). |
| `validate-slice` | true | Any per-criterion **FAIL** → HALT (user decides remediation / failure classification). Any **PARTIAL** (per-criterion or aggregate `Result: PARTIAL`, `skills/validate-slice/SKILL.md` 3-valued PASS\|PARTIAL\|FAIL) → HALT — PARTIAL is a user-decides-remediation state, identical disposition to FAIL; it is neither a provable clean PASS nor an enumerated FAIL, so it must be an *explicit* gate (not catch-all-covered) per must-not-defer #1 / the M3 principle. (Fixes /critique-review M-add-1.) |
| `reflect` | **false** | Terminal-before-commit. Successor `/commit-slice` is user-invoked; `reflect`→`/slice` next-slice kickoff is out of scope (Option 4 rejected). |
| `commit-slice` | **false** | Out of loop entirely — always user-invoked; never an auto-advance target. |

The canonical 5 *named* gates (TRI-1, BLOCKED-critique, plan-mode, smoke-gate, validate FAIL) are the load-bearing halts; the `slice`/`design-slice` entries above are bounded by their own skills' existing Critical-rules prose (no NEW gate prose needed there — they already pause for real ambiguity) and are documented here to make the completeness argument explicit rather than implicit. ADR-025 and the v0.41.0 changelog schema carry this same table as the canonical reference (RPCD-1: defined once, referenced not duplicated).

## Error model for this slice

`tools/pipeline_chain_audit.py` exit codes (mirrors BRANCH-1/CRP-1): `0` = chain well-formed; `1` = malformed/missing/incorrect-successor/terminal-violation (build refused at Step 6); `2` = usage/IO error. No new runtime error codes.

## Self-application of PCA-1 (bootstrap caveat)

slice-027 is **PCA-1 bootstrap-reference instance #1** (mirrors slice-021/BRANCH-1, slice-026/CRP-1): the `## Pipeline position` directive is authored *by* this slice, so it does not exist on disk when this slice's own `/slice → /design-slice → …` chain runs. This slice's chaining is being driven manually by the main thread per the user's explicit at-invocation directive (the pre-codification equivalent of PCA-1). Recursive self-application is discharged by running `tools/pipeline_chain_audit.py` against the repo at `/build-slice` Step 6 (expect exit 0) + `/critique-review` on this slice. The first non-bootstrap reference instance is the next slice after 027.

Per the slice-022 self-violation law (N≈6 stable, slices 020-026): expect this slice's own draft to commit exactly the defect PCA-1 catches — e.g., a successor-edge typo or a missing `auto-advance: false` on `reflect`/`commit-slice`. The audit is designed to catch its own authoring slice's violation; `/critique` should pre-budget for it.
