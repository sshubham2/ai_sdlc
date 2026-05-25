# Design: Slice 033 fix-skill-drift-test-crlf-normalization

**Date**: 2026-05-17
**Mode**: Standard

## What's new

- `tests/skill_drift_equality.py` (NEW shared module) — single source of truth for the `.md` forward-sync drift assertion. Exposes `assert_md_forward_synced(in_repo: Path, installed: Path, *, label: str) -> None`, which compares the two files **content-equal modulo line endings** (CRLF→LF normalized before hashing) and raises `AssertionError` with a path-attributed, which-side-diverged message on genuine divergence. **Import resolution (M3 — empirically verified, not extrapolated)**: `from tests.skill_drift_equality import assert_md_forward_synced` resolves from BOTH `tests/skills/diagnose/` (which has a sys.path-mutating `conftest.py` and no `tests.` import today) AND `tests/methodology/`; verified by probe (644 tests still collect cleanly with the new top-level module present). The mid-slice smoke gate asserts the diagnose-subpackage import explicitly rather than trusting the `tests/methodology/` precedent.
- `tests/methodology/test_skill_drift_normalization.py` (NEW) — AC2(a)/AC3 regression module: (a) CRLF vs LF identical normalized content → helper passes; (b) genuinely divergent content (non-EOL) → helper still raises (real-drift detection preserved); (c) `test_guarded_md_files_have_no_crlf_in_working_tree` — every guarded in-repo `.md` contains zero `\r\n` bytes (working-tree-state check, NOT merely `git check-attr`).
- `.gitattributes` (NEW) — declares the guarded `.md` surface (`skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md`) `text eol=lf`. **M1 ACCEPTED-FIXED**: `.gitattributes` alone does NOT rewrite already-CRLF-checked-out files under `core.autocrlf=true` (confirmed via git-scm gitattributes docs); the slice therefore ALSO runs a **targeted `git add --renormalize -- <those globs>`** so the guarded working-tree files become LF. Bounded blast radius: the git blobs are already LF, so `--renormalize` produces an empty index diff — it only reconciles the working-tree representation. The shared comparator (AC1) remains the environment-independent correctness fix; `.gitattributes`+renormalize is the durability layer + keeps `git status` clean.
- CAD-1 (`tools/critique_agent_drift_audit.py::_sha256_of`, L87-91) — same one-line CRLF→LF normalization before `h.update(...)`. **M2 binding**: the EXISTING `tests/methodology/test_critique_agent_drift.py::test_drift_detection_fires_on_artificial_byte_flip` + `test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing` (genuinely-divergent `# v1`/`# v2` LF content → exit 1) are the AC2(b) CAD-1-side must-not-mask proof and must stay green post-change; a NEW `test_cad1_audit_treats_crlf_and_lf_identical_content_as_clean` is the EOL-only complement.
- **B1/B2 governing-surface consistency (AC5), RULE-ID `EOL-DRIFT-1` (m-add-1)** — this slice restates a behavior-defining methodology rule, so per PMI-1 discipline uniform across slices 007–032 it ALSO ships, in-slice (not deferred to `/reflect`):
  - `methodology-changelog.md` new `## v0.47.0` entry headed `**EOL-DRIFT-1 — .md forward-sync drift guards are EOL-agnostic**` (rule-ref + defect-class + validation-method), forward-synced in-repo↔installed, pinned by `test_methodology_changelog.py::test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed` (pin-name derives from the minted RULE-ID per the verified v0.46.0 `qd_1` precedent).
  - atomic version bump `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml` `version` 0.46.0 → 0.47.0.
  - `CLAUDE.md` L33 (CAD-1) + L36 (Mini-CAD) "MUST be byte-equal" → "MUST be content-equal modulo line endings (EOL-agnostic per ADR-033)", pinned by NEW `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py` (substring pin mirroring `test_root_claude_md_branch_per_slice_rule.py`).
- design.md "Out of scope" deferral handle (m2): the `;`-split Step-5.5 runner concern gets a concrete tracked handle — new risk-register entry `R-8` opened at `/reflect`, not a bare prose mention.

## What's reused

- The 5 existing drift tests, refactored to delegate to the shared helper (no behavior loss, uniformity enforced):
  - `tests/skills/diagnose/test_diagnose_skill_drift.py` (2 functions: `SKILL.md` + `passes/03f-layering.md`)
  - `tests/methodology/test_slice_skill_drift.py` ([[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] MCT-1)
  - `tests/methodology/test_build_slice_skill_drift.py` ([[slice-021-add-feature-branch-workflow-at-build-and-commit-slice]])
  - `tests/methodology/test_commit_slice_skill_drift.py` (slice-021)
  - `tests/methodology/test_query_design_skill_drift.py` ([[slice-032-add-query-design-skill]] QD-1)
- `tools/critique_agent_drift_audit.py` `_sha256_of()` (line 87–91) — CAD-1's hash helper; same one-line CRLF→LF normalization applied. CLAUDE.md "Self-hosting discipline" CAD-1 / mini-CAD; [[slice-007-add-critique-agent-content-equality-audit]].
- `tests/methodology/conftest.py::REPO_ROOT`; `tests/skills/diagnose/conftest.py`.

## Components touched

### `tests/skill_drift_equality.py` (new shared helper)
- **Responsibility**: the one place that defines "in-repo `.md` is forward-synced to installed copy" as **content-equality modulo line endings**, with a meaningful failure message. Eliminates the 6 duplicated `_sha256(read_bytes())` definitions and gives AC2's regression test a single target.
- **Lives at**: `tests/skill_drift_equality.py` (created by this slice).
- **Key interactions**: imported by the 5 skill-drift test modules; no production-code dependency.

### 5 skill-drift test modules (modified)
- **Responsibility**: unchanged intent — assert each guarded `SKILL.md` / `03f-layering.md` is forward-synced. Each test function now computes `in_repo` / `installed` paths and calls `assert_md_forward_synced(...)` instead of inlining `_sha256`.
- **Lives at**: paths listed under "What's reused".
- **Key interactions**: `tests/skill_drift_equality`; filesystem (`~/.claude/skills/...`).

### `tools/critique_agent_drift_audit.py` (modified — CAD-1)
- **Responsibility**: unchanged — CAD-1 in-repo↔installed `agents/critique.md` equality gate. `_sha256_of()` normalizes CRLF→LF before `h.update(...)` so the gate is EOL-agnostic, matching the skill-drift fix. Exit-code contract (0 clean / 1 drift / 2 missing) UNCHANGED — only the equivalence relation feeding clean-vs-drift becomes EOL-insensitive. AC2(b) binds the existing genuine-divergence tests as the must-not-mask proof.
- **Lives at**: `tools/critique_agent_drift_audit.py:87-91`.
- **Key interactions**: `agents/critique.md`, `~/.claude/agents/critique.md`; consumed by `/critique`, `/critic-calibrate`, CLAUDE.md CAD-1 pre-commit gate.

### Governing-surface edits (B1/B2/AC5 — modified)
- **`methodology-changelog.md`**: new `## v0.47.0` entry (in-repo + installed forward-synced). **`VERSION`/`~/.claude/ai-sdlc-VERSION`/`plugin.yaml`**: atomic 0.46.0 → 0.47.0. **`CLAUDE.md` L33/L36**: "MUST be byte-equal" → EOL-agnostic precise wording.
- **Responsibility**: keep every governing surface consistent with the restated CAD-1/mini-CAD invariant in the SAME slice that restates it (slice-022 self-violation law avoidance; PMI-1 uniformity 007–032).

## Contracts added or changed

No runtime endpoints/events. One internal test-API contract added: `assert_md_forward_synced(in_repo, installed, *, label)` — raises `AssertionError` (path + diverging-side message) on genuine content divergence; returns `None` on EOL-only or exact match. Pre-existing-file assertions (`in_repo.exists()` / `installed.exists()` with the "has the plugin been installed" hint) are preserved inside the helper.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/skill_drift_equality.py` | `tests/skills/diagnose/test_diagnose_skill_drift.py` + `tests/methodology/test_{slice,build_slice,commit_slice,query_design}_skill_drift.py` | `tests/methodology/test_skill_drift_normalization.py::test_normalized_compare_treats_crlf_and_lf_identical_content_as_equal` | — |
| `tests/methodology/test_skill_drift_normalization.py` | — | — | `rationale: test module IS the consumer/verifier; no further consumer demanded for a regression-test file` |
| `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py` | — | — | `rationale: governing-doc substring pin (B2); test module IS the verifier — mirrors existing test_root_claude_md_branch_per_slice_rule.py exemption shape` |
| `.gitattributes` | git checkout/renormalize (working-tree EOL policy) + targeted `git add --renormalize` of the guarded globs | `tests/methodology/test_skill_drift_normalization.py::test_guarded_md_files_have_no_crlf_in_working_tree` | — |

## Decisions made (ADRs)

- [[ADR-033]] — `.md` forward-sync drift guards (5 skill-drift tests + CAD-1) compare content **modulo line endings**, not raw bytes; `.gitattributes` + targeted `git add --renormalize` of the guarded globs only (whole-vault renorm out of scope); the restated invariant is propagated in-slice to `methodology-changelog.md` (v0.47.0) + atomic VERSION bump + `CLAUDE.md` L33/L36 (NOT deferred to `/reflect`); shared helper lives at top-level `tests/skill_drift_equality.py` (location rationale in ADR) — reversibility: **cheap**.

## Authorization model for this slice

N/A — test/tooling change only; no runtime authorization surface. The self-hosting authorization concern (CAD-1/mini-CAD must keep catching real forward-sync misses) is enforced by AC2's must-not-mask-real-drift regression test.

## Error model for this slice

- `assert_md_forward_synced` raises `AssertionError` on: (a) in-repo file missing, (b) installed file missing (with the existing INSTALL.md hint), (c) genuine content divergence after EOL normalization (message names both paths + both normalized hashes). It does **not** raise on EOL-only differences (the R-5 false-FAIL class — now suppressed by design).
- CAD-1 audit exit-code contract unchanged: 0 clean / 1 content-drift / 2 path-missing|usage-error. Only the equivalence relation feeding "clean vs drift" changes (EOL-insensitive); genuine `# v1` vs `# v2`-class divergence still yields exit 1.
