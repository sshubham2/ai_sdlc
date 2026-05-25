# Slice 047: add-two-scope-install

**Mode**: Standard
**Estimated work**: 1 day (design-slice MUST run a scope-check; split candidate noted under "Out of scope")
**Risk retired**: none open-high (register is exhausted of open-high); retires the standing **structural deferral** carried slice-045 Deferred #2 → slice-046 Deferred #1, and removes the compounding latent risk that INST-1/CAD-1/PMI-1 self-hosting contracts silently assume a single global scope
**Test-first**: false  (design-slice may opt in per TF-1 — flagged as an open design question below)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Today `INSTALL.md` (the INST-1 recipe Claude executes verbatim) hardcodes every install target to the global `~/.claude/`. This slice makes the recipe ask the user, before any mutation, whether to install **user-level** (`~/.claude`, the default — current behavior, unchanged) or **project-level** (`<project>/.claude`), and parameterizes all install targets to the resolved scope. User-scope output must remain byte-identical to today (regression-safe); project-scope becomes newly available with an explicitly *decided* boundary for which self-hosting artifacts are scope-local vs inherently global. Why now: it's the queued next slice, it's the first user-facing capability in ~25 conformance micro-slices, and deferring again keeps the scope-blindness latent in INST-1/CAD-1/PMI-1.

## Acceptance criteria

1. `INSTALL.md` prompts the user to choose install scope — **user-level `~/.claude` (default)** vs **project-level `<project>/.claude`** — at a defined step that executes BEFORE any filesystem mutation; choosing default reproduces today's behavior with no extra prompts.
2. Every install/verify target path in `INSTALL.md` Steps 3–4 is expressed relative to a single resolved `$CLAUDE_DIR` (`~/.claude` for user scope, `<project>/.claude` for project scope) instead of a hardcoded `~/.claude`; user-scope rendering is byte-equivalent to the pre-slice recipe behavior.
3. `INSTALL.md` Step 4 verification passes the resolved `$CLAUDE_DIR` to `tools/install_audit.py` via its existing `--claude-dir` parameter, so install-parity is checked against the actually-chosen scope (no audit code change required for the user-scope path; if a project-scope gap is found in install_audit.py it is fixed minimally).
4. A new ADR records (a) the scope-selection decision, and (b) the self-hosting-contract scope boundary — explicitly which artifacts are scope-local (skills/agents/templates/methodology-changelog/VERSION) vs inherently global (the pip-installed `ai-sdlc-tools` package + the shared venv), with the rationale that project-scope does NOT duplicate the venv/tools package in this slice.
5. `$PY -m tools.install_audit`, CSP-1 cross-spec parity, INST-1, PMI-1, and `/drift-check` all pass post-slice; the canonical skill/agent/template/tool inventories in `tools/install_audit.py` still match `plugin.yaml`.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Scope prompt exists, pre-mutation, default = user | Read `INSTALL.md`; confirm the scope question appears before Step 3 (Execute install) and that "user-level / default" is the documented no-further-prompt path. Dry-run narration: simulate the recipe choosing default and confirm no behavioral delta vs current. |
| 2 | Paths parameterized to `$CLAUDE_DIR`, user-scope byte-stable | `grep -n "~/.claude\|\$HOME/.claude" INSTALL.md` — every remaining literal is either inside the `$CLAUDE_DIR` *definition* for user scope or an explicitly-justified non-target reference (e.g. the shared-venv global note). Diff the user-scope-resolved recipe against pre-slice INSTALL.md semantics: no target-path change. |
| 3 | Audit invoked with resolved scope | `INSTALL.md` Step 4 line shows `tools.install_audit --claude-dir "$CLAUDE_DIR"`. Run `$PY -m tools.install_audit --claude-dir ~/.claude` (user scope) → OK. If project-scope path touched in `install_audit.py`, run its test module. |
| 4 | ADR present and decides the boundary | New `architecture/decisions/ADR-NNN.md` exists, `status: accepted`, names the scope-local vs global artifact split + the venv/tools-package-stays-global rationale; referenced from `methodology-changelog.md` if a rule-ID is minted (design decides ID-vs-no-ID per the conformance-class precedent). |
| 5 | All self-hosting audits green | `$PY -m tools.install_audit`, `$PY -m tools.plugin_manifest_audit`, `$PY -m tools.cross_spec_parity_audit`, `/drift-check`, `$PY -m tools.critique_agent_drift_audit --repo-root .` (if Critic agent untouched, still run for CAD-1) all exit clean; `pytest tests/methodology` green. |

## Must-not-defer

- [ ] **Self-hosting-contract scope-dependency must be DECIDED, not silently ignored** — the ADR explicitly states what project-scope reuses (global venv + global `ai-sdlc-tools` pip package) vs duplicates (nothing, this slice). A silent assumption here is the exact latent risk this slice exists to retire.
- [ ] Default (user-scope) path remains byte-stable — no regression to the existing single-scope install (every current INSTALL.md user is on this path).
- [ ] Project-scope must not corrupt or write outside `<project>/.claude/` — recipe must not mutate `~/.claude/CLAUDE.md` / `~/.claude/settings.json` when project-scope is chosen unless the ADR explicitly decides those stay global (and then it must NOT silently skip them either — the recipe states the decision to the user).
- [ ] INST-1 install audit must verify the *chosen* scope, not blindly `~/.claude` — a project-scope install that passes a user-scope audit is a false green.
- [ ] No new TODO/FIXME/placeholder in `INSTALL.md` or `tools/install_audit.py`.

## Out of scope

- **Per-project venv / per-project `ai-sdlc-tools` package duplication** — this slice's ADR decides these stay global; actually building project-isolated Python environments is a separate future slice (only if ever demonstrated necessary).
- **Project-scope `settings.json` fork-var / project-scope global-CLAUDE.md PY-convention rewrite** — design.md + ADR decide the reuse-global policy; implementing project-local copies of those is out of scope here.
- **Migration tooling** (move an existing user-scope install to project-scope or vice-versa) — not this slice.
- **Split candidate**: if design-slice's scope-check finds the recipe parameterization + ADR + any install_audit.py project-scope fix exceeds 1 day, split into 047 (interactive scope selection + path parameterization, user-scope-byte-stable) and 048 (project-scope install_audit.py support + verification hardening). The split must leave 047 shippable (user-scope unchanged + project-scope at least documented even if audit-verification of project-scope lands in 048).

## Dependencies

- Prior slices: [[slice-045-fix-install-pypi-package-name-and-stale-prose]] — established that `INSTALL.md` is an in-house methodology surface (MEPD-1 boundary, broader than `agents/critique.md:122`'s literal list) and that `tools/install_audit.py` canonical inventories must match `plugin.yaml`; [[slice-046-add-conditional-repro-auto-advance]] — the reflection that promoted this to the queued next slice
- Vault refs: [[INSTALL.md]], [[tools/install_audit.py]], [[decisions/ADR-NNN]] (new, this slice)
- Risk register: no open risk retired; standing deferral (slice-045/046) discharged — design.md records on the canonical surface per the slice-045 MEPD-1(b) discipline (NOT reflection.md)

## Mid-slice smoke gate

At ~50% of build, run:
```
grep -n "~/.claude\|\$HOME/.claude\|CLAUDE_DIR" INSTALL.md
$PY -m tools.install_audit --claude-dir ~/.claude --json
```
Expected: scope-resolution block + `$CLAUDE_DIR` parameterization present in INSTALL.md; install_audit still green against `~/.claude` (user-scope path unbroken). If install_audit FAILs or any user-scope target path silently changed: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. the scope-dependency DECISION in the ADR)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (user-scope install_audit still green; no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] CSP-1 + INST-1 + PMI-1 + CAD-1 audits green
