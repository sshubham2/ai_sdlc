# Design: Slice 047 add-two-scope-install

**Date**: 2026-05-19
**Mode**: Standard

## What's new

- `INSTALL.md` gains a **Step 0b: Choose install scope** (after Step 0 "Locate the source", before Step 1 pre-flight mutation-free detection runs, and strictly before any Step 3 mutation): prompts **user-level `~/.claude` (default)** vs **project-level `<project>/.claude`**, binds `CLAUDE_DIR`, and prints an explicit user-facing statement of what stays global vs relocates (the must-not-defer "state the decision, never silently skip").
- `INSTALL.md` Step 3f and Step 4 **content** targets re-expressed relative to `$CLAUDE_DIR`. Step 4's INST-1 line passes `--claude-dir "$CLAUDE_DIR"`.
- New ADR-049 — records the scope-selection decision + the scope-local-vs-global artifact boundary (the answer to the slice's raison d'être latent-risk).
- `methodology-changelog.md` v0.56.0 entry — **INST-1 v1.1 (scope-parameterized)**; extends INST-1, mints no new rule-ID (precedent: slice-014 "PMI-1 v1.1", slice-008 "BC-1 v1.2" — a versioned refinement of an existing rule, not a new discipline). In-repo + installed copies forward-synced per MCFS-1.
- `architecture/shippability.md` — one new row pinning the scope-selection contract + the v0.56.0 entry (per the slice-038→R-10 lesson: the Step 5.3 catalog entry IS the added content pin).

## What's reused

- `tools/install_audit.py` — **reused, NOT modified**. Already fully `claude_dir`-parameterized (`--claude-dir`, default `$HOME/.claude`, path-generic via `pathlib.Path`; existing `no-claude-dir` violation kind at `tools/install_audit.py:301-308` covers a missing/unwritable project dir). Tool-module import check resolves from the global venv site-packages independent of `claude_dir`, and `_check_metadata` reads `claude_dir/methodology-changelog.md` + `claude_dir/ai-sdlc-VERSION` — both correct under project-scope because Step 3f copies metadata into `$CLAUDE_DIR`. **Zero audit code change required** — AC3 is a recipe-invocation change only.
- INST-1 canonical inventories in `tools/install_audit.py:_CANONICAL_*` ↔ `plugin.yaml` parity (`tests/methodology/test_install_audit.py`) — unchanged; this slice adds no skill/agent/template/tool.
- [[slice-045-fix-install-pypi-package-name-and-stale-prose]] — established `INSTALL.md` is an in-house methodology surface (MEPD-1 boundary broader than `agents/critique.md:122`'s literal list) → MEPD-1(b) discharged by name in this design (below).
- Claude Code's native project-level `.claude/` resolution — skills/agents/settings under `<project>/.claude/` are active when CC runs in that project; this is the platform mechanism project-scope rides on (not built by this slice).

## The scope boundary (core design — answers the latent risk)

`$CLAUDE_DIR` governs **AI-SDLC pipeline content only**. Environment-level artifacts stay **global** (`~/.claude`) under both scopes, because they bind to the global shared venv (which the mission brief keeps global) and the Claude-Code runtime, not to pipeline content. User-confirmed 2026-05-19.

| INSTALL.md step | Artifact | User scope | Project scope | Reason |
|---|---|---|---|---|
| 3a | `~/.claude/.venv` | global | global | shared venv (mission-brief out-of-scope to duplicate) |
| 3b | graphify in venv | global | global | rides the global venv |
| 3c | `~/.claude/skills/graphify/` | global | global | graphify's own integration, env-level (not AI-SDLC content) |
| 3d | `~/.claude/CLAUDE.md` PY-convention | global | **global** | binds to the global venv path; user decision 2026-05-19 |
| 3e | `~/.claude/settings.json` fork-var | global | **global** | Claude-Code runtime behavior toggle; user decision 2026-05-19 |
| 3f | skills / agents / templates / methodology-changelog / ai-sdlc-VERSION | `~/.claude/` | **`$CLAUDE_DIR` = `<project>/.claude/`** | the AI-SDLC pipeline *content* — the only thing scope relocates |
| 3g | `ai-sdlc-tools` pip package | global | global | inherently global (venv site-packages); mission-brief out-of-scope to duplicate |
| 4 | env checks (venv/graphify/tools-import) | global | global | verify the global env |
| 4 | content checks (skills/agents/templates/metadata) + INST-1 `--claude-dir` | `~/.claude` | **`$CLAUDE_DIR`** | verify the *chosen* scope (false-green guard) |

**Consequence stated in the recipe** (must-not-defer): the Step 0b statement tells the user verbatim that project-scope installs *content* under `<project>/.claude/` while the venv, the PY-convention, the fork-var, and the `ai-sdlc-tools` package remain global in `~/.claude/`; and that **project-scope requires the global env steps (3a–3e, 3g) to have run** — on a fresh machine the recipe still executes them globally, only 3f + the Step-4 content checks honor `$CLAUDE_DIR`. This is the explicit "decided, not silently skipped" requirement.

## Components touched

### `INSTALL.md` (modified — the INST-1 recipe; in-house methodology surface)
- **Responsibility**: the verbatim recipe a Claude instance executes to install the pipeline. This slice makes it scope-aware.
- **Lives at**: `INSTALL.md` (repo root; copied nowhere — it is project-source per its own Step 3f exclusion list).
- **Key interactions**: invokes `tools/install_audit.py` at Step 4; references the shared venv, `plugin.yaml` inventory indirectly via the audit.

### `tools/install_audit.py` (reused — NOT modified)
- **Responsibility**: INST-1 parity audit. Already scope-generic.
- **Lives at**: `tools/install_audit.py`.
- **Key interactions**: invoked from `INSTALL.md` Step 4 with `--claude-dir "$CLAUDE_DIR"`.

## Contracts added or changed

No code endpoint/event/API contract. The changed contract is the **recipe contract**: INSTALL.md now has a documented pre-mutation scope-selection input and a `$CLAUDE_DIR` indirection for content targets. Pinned in `architecture/shippability.md` (the regression surface) + the v0.56.0 changelog entry.

## Data model deltas

None.

## Wiring matrix

Per WIRE-1. This slice introduces **no new modules** (INSTALL.md = recipe prose, ADR-049 = doc, changelog entry = doc; `install_audit.py` unchanged). Zero-row matrix = clean by audit construction.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-049]] — Two-scope install: interactive user-vs-project scope selection; `$CLAUDE_DIR` governs AI-SDLC content only; env-level artifacts (venv, PY-convention, fork-var, tools pip package) stay global under both scopes — reversibility: **cheap** (recipe prose + a documented boundary; revertible by editing `INSTALL.md` back to a single hardcoded `~/.claude` with no data migration — no consumers bind to the scope mechanism).

## Methodology-obligation discharge (MEPD-1(b))

`INSTALL.md` is an in-house methodology surface (slice-045 lesson: the INST-1 recipe a user executes verbatim, broader than `agents/critique.md:122`'s literal enumeration). This slice changes its behavior → **methodology-changelog.md v0.56.0 entry is mandatory** (NOT a no-VERSION-bump conformance class — this is a genuine behavioral capability addition, unlike slice-045's prose-correctness fix). Framed as **INST-1 v1.1 (scope-parameterized)**: no new rule-ID (versioned refinement of an existing rule — slice-014 PMI-1 v1.1 / slice-008 BC-1 v1.2 precedent class), VERSION bump 0.55.0 → 0.56.0, PMI-1 `version`-match invariant holds. Entry header MUST match META-1 (`## v0.56.0 — <U+2014 em-dash> 2026-05-NN` + carry the `INST-1` rule reference). In-repo ↔ installed forward-synced per MCFS-1 (non-catalog whole-file EOL-agnostic gate, slice-041).

## Authorization model for this slice

N/A — install recipe; no runtime principal, no protected action. Stated explicitly to satisfy the design template (not an omission).

## Error model for this slice

No new error codes. Failure modes are covered by existing mechanisms:
- Project-scope chosen but `<project>/.claude` is not a sane project dir / not writable → the Step 0b prompt is pre-mutation; the recipe asks/aborts before any write (same discipline as Step 0's source-locate ask). No partial-write state.
- INST-1 run with `--claude-dir <project>/.claude` against a missing/empty dir → existing `no-claude-dir` violation kind (`tools/install_audit.py:301-308`) — already actionable, names the dir, points at `--claude-dir`.
- Project-scope chosen with no prior global env → Step 0b statement instructs (and the recipe still executes) the global env steps 3a–3e/3g; not a silent skip.

## Open design questions — resolved

- **(a) Test-first?** → **false**. The ACs are recipe-prose + audit-invocation; verification is INST-1 (`--claude-dir` run) + CSP-1 cross-spec parity + grep-on-recipe + the shippability content-pin. A TF-1 plan over a markdown recipe would be tautological pin-writing with no genuine FAIL→PASS contrast (distinct from slice-046's prose-pin, which guarded a `SKILL.md` *executable* contract). Regression guard = the shippability row + v0.56.0 entry-pin, enforced by the existing methodology-changelog/CSP-1 suite. (slice-045 TF-1-plan-completeness lesson is satisfied: `Test-first: false`, so no per-AC TF-1 mapping is owed.)
- **(b) Project-scope env-artifact location?** → **stay global** (user-confirmed 2026-05-19). Encoded in the scope-boundary table above + ADR-049.
- **(c) Rule-ID vs no-ID?** → **no new rule-ID; INST-1 v1.1 versioned refinement** + mandatory v0.56.0 changelog entry (rationale in the MEPD-1(b) section above).

## Scope-check (mission-brief 1-day boundary)

Effort re-estimated post-context-gathering: **MEDIUM, ~0.5 day, no split.** Drivers: `install_audit.py` needs **zero code change** (already `--claude-dir`-parameterized); deliverables are (1) INSTALL.md Step 0b + ~6 content-target path edits, (2) ADR-049, (3) one v0.56.0 changelog entry (in-repo + installed), (4) one shippability row. The mission-brief 047/048 split fallback is **not triggered** — the LARGE estimate assumed possible `install_audit.py` project-scope work that the code inspection ruled out.
