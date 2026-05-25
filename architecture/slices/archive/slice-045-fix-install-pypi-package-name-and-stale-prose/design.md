# Design: Slice 045 fix-install-pypi-package-name-and-stale-prose

**Date**: 2026-05-18
**Mode**: Standard

## What's new

- No new code modules. This is a documentation-correctness slice over `INSTALL.md` (+ two descriptive refs) with the regression guard already in place (`tests/methodology/test_install_md_correctness.py`, shippability #45, written by the `/repro` prelude).
- Edits only: `INSTALL.md`, `README.md`, `tutorial-site/Hybrid AI SDLC Pipeline.html`.

## What's reused

- [[shippability]] entry #45 — the FAIL→PASS contract for this slice (3 tests in `tests/methodology/test_install_md_correctness.py`).
- INST-1 — `INSTALL.md` is the INST-1 install recipe; `tools/install_audit.py` and the canonical inventory are unchanged by this slice.
- Canonical correct form to mirror: `skills/discover/SKILL.md:105` (`pip install graphifyy[video]`).
- Source-of-truth files the corrected prose must agree with: `VERSION` (0.54.0), `plugin.yaml` (25 `- path: tools/` entries).

## Components touched

None. No `src/` or `tools/` module is created or modified. The only behavioral artifact (the repro test) was authored by `/repro` and is consumed by the shippability runner.

## Contracts added or changed

None. No endpoint, event, schema, or CLI surface changes. The `graphify` **module/CLI** name is explicitly **unchanged** (`$PY -m graphify`, `import graphify`, `$PY -m graphify install`, `$PY -m graphify --help`) — only the PyPI **distribution** token in `pip install` lines changes.

## Data model deltas

None.

## The precise edit set

### EDIT-1 — PyPI distribution name (AC1)
- `INSTALL.md:93`: `$PY -m pip install graphify` → `$PY -m pip install graphifyy`.
- Verified scope: this is the **only** bare `pip install graphify` occurrence in `INSTALL.md` (Step 3b fallback). No other `pip install graphify` exists in the repo except `skills/discover/SKILL.md:105`, which is already correct (`graphifyy[video]`) and is NOT touched.
- Module/CLI `graphify` references (lines 58, 95, 99, 144, 174, 179–180, 229, etc.) are **left verbatim** — must-not-defer regression guard.

### EDIT-2 — methodology version prose (AC2)
The repro test forbids the literal `v0.20.0` **anywhere** in `INSTALL.md`. The four occurrences split into two semantic classes:

| Line | Text | Class | Resolution |
|------|------|-------|------------|
| 18 | "The AI SDLC pipeline (methodology v0.20.0):" | **current-version claim (stale)** | → `(methodology v0.54.0 — see \`VERSION\`)` — matches `VERSION` AND labels the source-of-truth per AC2 ("labelled against `VERSION`"). **Build deviation (user-approved at plan-mode gate, 2026-05-18):** realized with the `— see \`VERSION\`` label rather than the bare `(methodology v0.54.0)` originally drafted here; AC-faithful strengthening of the same edit-site/intent, not a scope change. |
| 232 | "drift from the canonical inventory baked into v0.20.0" | **stale version literal** | reword to drop the literal **without asserting currency** (per Critic m1 — `tools/install_audit.py:4,8,42` still hardcodes the v0.20.0 inventory, so the doc must not claim "current"): → "The audit reports any drift from its canonical inventory." (no version literal, no "current") |
| 26 | "Per **INST-1** (`methodology-changelog.md` v0.20.0)" | **historical anchor (factually correct)** | reword to drop the brittle literal: "Per **INST-1**" (the rule ID is the stable reference; the install recipe does not need to cite which historical changelog version introduced it) |
| 168 | "older source folder pre-v0.20.0 won't have it" | **historical anchor (factually correct)** | reword without the literal: "an older source folder predating the `pyproject.toml` packaging won't have it" |

**Design decision (no ADR — cheap, prose-only, reversible):** rather than *loosen the catalogued repro guard* to tolerate historical `v0.20.0` strings, we *eliminate the literal entirely* by rewording the two historical anchors to reference the stable rule ID / the packaging artifact instead of a changelog version number. Rationale: (a) keeps shippability #45 a strong blunt guard (no "allow-list of OK v0.20.0 strings" fragility); (b) genuinely improves the recipe — an install recipe should not carry changelog-archaeology version pins; (c) advances the "don't state brittle version literals in the recipe" intent. The one load-bearing current-version statement (line 18) is set to `v0.54.0`; note line 144 already uses the derive-from-source pattern `methodology v<cat ~/.claude/ai-sdlc-VERSION>` and is left as the model.

### EDIT-3 — tool count (AC3)
- `INSTALL.md:22` and `:150`: "13 executable methodology tools" → "25 executable methodology tools".
- **Derive-from-source mechanism:** `INSTALL.md` is static markdown executed by a human/Claude — it cannot compute the count at read-time. The re-drift guard is therefore *structural, not templated*: `test_install_md_tool_count_matches_plugin_yaml` (shippability #45) asserts every "N executable methodology tools" claim equals `plugin.yaml`'s enumerated `- path: tools/` count on every `/validate-slice`. The test *requires the phrase to exist* (`assert claims`), so removing the number is not an option — the correct value (25) plus the standing test IS the derivation contract.

### EDIT-4 — descriptive package-name precision (AC4)
Exact resulting phrase pinned (per Critic m2 — Builder must not improvise; both targets are prose, not `pip install` commands):
- `README.md:69`: `Installs \`graphify\` (editable from \`~/.claude/packages/graphify\` if present, else PyPI)` → `Installs \`graphify\` (editable from \`~/.claude/packages/graphify\` if present, else the \`graphifyy\` PyPI package)`.
- `tutorial-site/Hybrid AI SDLC Pipeline.html:1050`: same substitution — `else PyPI` → `else the \`graphifyy\` PyPI package` (HTML uses `<code>` for the inline literals; preserve the existing markup style on that line, only the trailing "else PyPI" phrase changes). The module/CLI noun `graphify` earlier in the sentence is unchanged.
- Not covered by the repro test (it reads only `INSTALL.md`, confirmed `test_install_md_correctness.py:32-38`); verified by grep + `/drift-check` + human review per the mission brief.

## Wiring matrix

Per **WIRE-1**. This slice introduces no new production module. The one new file (`tests/methodology/test_install_md_correctness.py`) was authored by the `/repro` prelude and is a test consumed by the shippability runner.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_install_md_correctness.py` | — | — | `test module authored by /repro prelude, consumed by the shippability #45 runner — no production consumer demanded — rationale: it IS the regression test` |

## Decisions made (ADRs)

None. No decision rises to ADR: all edits are prose-correctness; the one judgment call (reword historical version anchors vs. weaken the repro guard) is cheap, reversible, and documented inline under EDIT-2.

### MEPD-1(b) discharge (in-house methodology surface — INSTALL.md is the INST-1 install recipe)

This slice changes the behaviour of an in-house methodology surface (the recipe a user executes verbatim), so the MEPD-1 Dim-7 obligation must be discharged by name with exactly one branch. **Branch (b) — documented why-none, verified against the actual META-1 enforcing assertion (not the precedent alone — slice-032 false-precedent guard):**

- **No VERSION bump, no methodology-changelog entry.** This is a no-VERSION-bump conformance/prose-correctness fix: it locks no code-behaviour decision and mints no RULE-ID. A parentless `###` entry would orphan-split under META-1's enforcing regex `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` at `tests/methodology/test_methodology_changelog.py:136` (verified — Critic executed it; matches the slice-040/R-10 + slice-036/R-9 precedent class, corroborating not sole-basis).
- **No PMI-1 bump.** No skill/agent/tool added or removed; `plugin.yaml` inventory unchanged (the new repro test is a test file, not a manifested tool).
- **Risk-retirement is recorded on the canonical surface: `risk-register.md` R-11 `**Retired**:` line** — NOT `reflection.md` (the original design's mis-citation, corrected per Critic M1; the slice-040/R-10 + slice-036/R-9 precedent surface for a no-VERSION-bump conformance-fix retirement is the risk-register, never reflection.md). R-11 is born this slice (discovered + retired by slice-045) documenting the latent install-recipe defect; the permanent regression guard is shippability #45.

## Authorization model for this slice

N/A — no runtime surface, no auth-bearing path.

## Error model for this slice

N/A — documentation edits. The only failure mode is "edit does not satisfy the repro assertion", caught deterministically by the mid-slice smoke gate (run the 3 repro tests after the INSTALL.md edits) before AC4 work begins.
