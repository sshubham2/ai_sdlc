# Design: Slice 026 enforce-critique-review-prerequisite

**Date**: 2026-05-16
**Mode**: Standard

## What's new

- `tools/critique_review_prerequisite_audit.py` — new audit (rule-ID **CRP-1**), modeled structurally on `tools/branch_workflow_audit.py` (BRANCH-1): dataclass result, `--json`, exit codes 0/1/2, `_stdout.reconfigure_stdout_utf8()` per UTF8-STDOUT-1. Resolves pipeline mode + `critic-required` + `critique-review.md` presence + canonical `critique-review-skip` frontmatter key; refuses (exit 1) when a mandatory `/critique-review` is absent and unrationalised.
- `skills/build-slice/SKILL.md` `## Prerequisite check` — new CRP-1 sub-block placed **after the L22 `critique.md`-exists gate and after the L23 TPHD-1 paragraph, before `### Branch state`** (deterministic placement so the mini-CAD byte-equality drift test has a stable target). Dependency ordering rationale: there can be no `/critique-review` without a `/critique`, so the CRP-1 check must run after the existing `critique.md`-exists check (L22). It is NOT the first prerequisite step — L21/L22 critique.md gates and L23 TPHD-1 run before it. A defense-in-depth re-run is added at Step 6 pre-finish, mirroring BRANCH-1's Step 6 placement (catches `critique-review.md` deleted mid-build or `critic-required` flipped true during a `/design-slice` scope expansion that post-dated the prereq check). The escape-hatch key lives in `milestone.md` frontmatter precisely so it survives Step 7b's continuous milestone.md rewrite (see ADR-024 / B2).
- `~/.claude/templates/milestone.md` + the slice milestone.md shape — document the **optional** `critique-review-skip:` frontmatter key (absent by default) so the canonical escape-hatch has a defined, Step-7b-preserved home; add a `/build-slice` Step 7b instruction to preserve any present `critique-review-skip:` key verbatim across rewrites.
- `methodology-changelog.md` — new v0.40.0 entry codifying CRP-1 as an **audit-enforced gate, NON-`-D`** per ADR-019 (its programmatic gate is `tools/critique_review_prerequisite_audit.py`); naming-class peers are BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1, NOT the `-D` prose-heuristic family.
- `architecture/decisions/ADR-024-crp-1-critique-review-prerequisite-discipline.md` — locks the escape-hatch *location* (milestone.md frontmatter key, not build-log.md Events) and records the Step-7b-survival reasoning + the bootstrap-reference-instance consequence.
- `architecture/shippability.md` — new CRP-1 row + consumer-reference propagation (RPCD-1 / SCPD-1).
- `tests/methodology/test_critique_review_prerequisite_audit.py` — new test file (audit behavior over fixtures, incl. malformed-skip + narrative-prose non-false-positive).
- New consumer-propagation edits (the slice-025 L39 "under-enumerated new-tool propagation" site — this is N=4: slice-021/023/025/026):
  - `tools/install_audit.py` `_CANONICAL_TOOLS` tuple (18→19 entries) **AND** the stale prose comment at L66-71 (currently says "17 tool modules ... 15 audits + lint + install_audit"; bring to the post-slice-026 count/breakdown — this comment is itself the kind of under-enumerated drift site slice-025 L39 names).
  - `plugin.yaml` tools list (+1 `- path:` entry).
  - `tests/methodology/test_utf8_stdout_regression.py`: `_POSITIONAL_SLICE_TOOLS` (+1; verified the new tool's `<slice-folder>` CLI matches `_positional_slice_argv`'s `[PY, -m, tool, fixture_dir]` shape) AND the hard-coded roll-up sentinel `assert len(actual_audits) == 18` → 19, comment "post-slice-025"→"post-slice-026". **Note**: this sentinel counts the `tools/*.py` glob, which is an *independent counter* from `install_audit._CANONICAL_TOOLS`; both happen to move 18→19 this slice but for different reasons — do not treat them as one counter (a future divergence must not be masked).
  - **(N=5, per /critique-review M-add-1) milestone.md template forward-sync pair**: the B2 fix documents the `critique-review-skip:` key in the milestone.md template, which exists as TWO byte-equal copies — in-repo `templates/milestone.md` and installed `~/.claude/templates/milestone.md`. `tools/install_audit.py` `_check_templates` (L199-217) only asserts `template_path.exists()` — it does **NOT** byte-compare, and there is **no `test_*_drift.py` for the milestone template** (drift tests exist only for build-slice / commit-slice / slice SKILL.md + critique agent). This slice MUST edit BOTH copies in lockstep; this propagation is **manual and unguarded** and is enumerated here so the next template-touching slice does not inherit a silent forward-sync asymmetry (same FBCD-1 / slice-025-L39 under-enumerated-propagation class as the tool-inventory sites above — applied consistently to the surface B2 itself created). Scope decision: this slice does NOT add a milestone-template byte-equality drift test (that would be a separate discipline slice — out of scope here); it discharges the obligation by explicit enumeration + an ADR-024 Consequences note, not by a new audit.
  - `VERSION` + `plugin.yaml.version` → 0.40.0 (PMI-1 lockstep).

## What's reused

- `tools/branch_workflow_audit.py` — structural template (escape-hatch scan, canonical regex, malformed-attempt → Important violation, exit-code scheme, JSON shape) AND the non-`-D` audit-enforced-gate naming-class precedent. [[slice-021-add-feature-branch-workflow-at-build-and-commit-slice]].
- `tools/critique_review_audit.py` — **unchanged**; it validates `critique-review.md` *structure* (4 sections) and runs only from `skills/critique-review/SKILL.md` (sole invocation site — it is NOT a skip-detector and is NOT wired into `/validate-slice`). CRP-1 is the *first* structural skip-detector — orthogonal concern, separate tool (mirrors BRANCH-1 being its own tool).
- `tools/_stdout.py` `reconfigure_stdout_utf8()` — UTF8-STDOUT-1 compliance for the new tool. [[slice-023-audit-tools-default-utf8-stdout]].
- `architecture/triage.md` frontmatter `mode: STANDARD` — primary mode source; fallback `CLAUDE.md` `**Mode**:`.
- `milestone.md` frontmatter `critic-required:` — the mandatory-Critic trigger signal authored by `/slice` Step 4a. [[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]].
- DR-1 (`methodology-changelog.md` v0.17.0) — the dual-review discipline whose mandatory-in-Standard status this slice operationalizes. [[CLAUDE.md]] "Builder ↔ Critic separation".
- ADR-019 — the active, test-pinned authority defining the `-D`-vs-audit-enforced-gate naming classes; CRP-1 *conforms to* (does not supersede) ADR-019 by joining the audit-enforced-gate class. [[slice-017-address-tf-1-plan-staleness-discipline]] (TPHD-1 sub-mode (c) `## Prerequisite check` placement precedent).

## Components touched

### `tools/critique_review_prerequisite_audit.py` (created)
- **Responsibility**: Refuse `/build-slice` when a mandatory `/critique-review` was skipped without a documented rationale — closing the slice-025 silent-skip gap. First structural skip-detector for DR-1.
- **Lives at**: `tools/critique_review_prerequisite_audit.py` (created by this slice).
- **Key interactions**: reads `architecture/triage.md` (mode; fallback `CLAUDE.md`), the slice folder's `milestone.md` (`critic-required` + `critique-review-skip` frontmatter key) and `critique-review.md` (presence). No git calls (unlike BRANCH-1). Invoked by `skills/build-slice/SKILL.md` prose at `## Prerequisite check` (primary) and Step 6 (defense-in-depth).

### `skills/build-slice/SKILL.md` (modified)
- **Responsibility**: gains the CRP-1 prerequisite sub-block (deterministic placement, post-L22/L23) + Step 6 defense-in-depth re-run + a Step 7b instruction to preserve any `critique-review-skip:` frontmatter key.
- **Lives at**: `skills/build-slice/SKILL.md` `## Prerequisite check` + Step 6 + Step 7b.
- **Key interactions**: byte-equality drift-gated by `tests/methodology/test_build_slice_skill_drift.py` (mini-CAD) — the in-repo copy MUST equal the installed copy; the slice's `/commit-slice` / install step keeps them in lockstep.

## Contracts added or changed

### CLI: `python -m tools.critique_review_prerequisite_audit <slice-folder> [--json] [--root <repo-root>]`
- **Defined in code at**: `tools/critique_review_prerequisite_audit.py` (to be created).
- **Auth model**: n/a (local CLI audit).
- **Refuse condition (exit 1, `mandatory-critique-review-absent`)**: `mode ∈ {STANDARD, HEAVY}` AND `milestone.md critic-required: true` AND `critique-review.md` absent in slice folder AND no canonical `critique-review-skip` frontmatter key. Message names which of the four conditions held.
- **Accept (exit 0)**: `critique-review.md` present, OR canonical `critique-review-skip` value present, OR mode == MINIMAL, OR `critic-required: false`.
- **Malformed-skip (exit 1, Important, `escape-hatch-malformed`)**: `critique-review-skip` frontmatter key present but value does NOT match `^skip — rationale: .+`. Detection is keyed on the *frontmatter key* (not a substring scan of free-form body prose) — this eliminates the BRANCH-1-style narrative-prose false-positive risk.
- **Usage error (exit 2, `usage-error` / `mode-unresolvable`)**: slice folder missing, `milestone.md` missing, mode unresolvable from triage.md + CLAUDE.md.

## Data model deltas

One optional `milestone.md` frontmatter key: `critique-review-skip:` (string, value `^skip — rationale: .+`). Absent by default; documented in the milestone.md template. Parsed via the same frontmatter reader the audit uses for `critic-required`.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/critique_review_prerequisite_audit.py` | `skills/build-slice/SKILL.md` `## Prerequisite check` (prose invocation) + Step 6 pre-finish | `tests/methodology/test_critique_review_prerequisite_audit.py::test_refuses_when_standard_mandatory_and_absent` | — |

## Decisions made (ADRs)
- [[ADR-024]] — CRP-1 documented-skip escape-hatch lives in the `milestone.md` `critique-review-skip` *frontmatter key*, NOT `build-log.md` Events (BRANCH-1) NOR a free-form body line, because the CRP-1 gate fires at the `## Prerequisite check` *before* `build-log.md` exists AND the key must survive Step 7b's continuous milestone.md rewrite — reversibility: cheap. CRP-1 conforms to ADR-019's naming convention (audit-enforced-gate class, NON-`-D`); it does not supersede ADR-019.

## Authorization model for this slice

n/a — local CLI audit + skill prose. No runtime auth surface.

## Error model for this slice

The audit emits structured violations (kind/severity/message) mirroring BRANCH-1's `BranchViolation` shape:
- `mandatory-critique-review-absent` (Important, exit 1) — the core refuse; message names which of the four conditions held so the user can act (per mission-brief must-not-defer "refuse-path observability").
- `escape-hatch-malformed` (Important, exit 1) — `critique-review-skip` key present but value off-canonical.
- `usage-error` / `mode-unresolvable` (Important, exit 2).
No Warning class (BRANCH-1's stale-branch warning has no CRP-1 analogue).

## Recursive self-application — bootstrap-reference instance #1

Per the BRANCH-1 precedent (`methodology-changelog.md` L205: slice-021 is the BRANCH-1 bootstrap-reference instance — the slice authoring the prerequisite sub-section cannot itself use it at its own `/build-slice` time), **slice-026 is CRP-1 bootstrap-reference instance #1**. At slice-026's own `/build-slice` Prerequisite check, the CRP-1 sub-block does not yet exist in `skills/build-slice/SKILL.md` (this build authors it), so CRP-1 cannot structurally self-gate this build. Self-application is therefore satisfied by: (a) `/critique-review` run manually on slice-026 (mandatory — in-house methodology surface), and (b) `python -m tools.critique_review_prerequisite_audit architecture/slices/slice-026-enforce-critique-review-prerequisite` run against slice-026's own folder once `critique-review.md` exists, asserted exit 0 in Verification-plan row 5. This bootstrap distinction is also recorded in ADR-024 Consequences.
