# Slice 081: fix-drift-check-enforcement-gap

**Mode**: Standard
**Estimated work**: 0.5–1 day
**Risk retired**: closes the drift-check enforcement gap — `/drift-check` is the only pipeline discipline preached (CLAUDE.md "Run /drift-check before commit") and listed in `/build-slice` Step 6 yet enforced by nothing (the R-7 / slice-022 silent-disable failure class). Introduces a new audit-enforced gate (new rule + ADR minted at design time).
**Test-first**: false  (the BFRD-1 repro test is the test-first artifact; the new audit tool's own unit tests are a build deliverable, not a TF-1 plan table)
**Walking-skeleton**: false
**Exploratory-charter**: false

**Closes:** (no SC-NNN — user-reported defect, not a `/diagnose` backlog finding)

## Intent

`/drift-check` is the conspicuous exception among pipeline disciplines: every sibling (BC-1, PMI-1, CRP-1, PCA-1, NAW-1, MCFS-1, STP-1, AVFS-1, TVFS-1, WIRE-1, BCI-1) ships a `tools/*_audit.py` whose `main()` returns non-zero on violation AND is invoked at `/build-slice` Step 6 so the build HALTs. `/drift-check` has neither a `tools/drift_check_audit.py` nor an installed pre-commit hook (`.git/hooks/` holds only `.sample` files) — only an honor-system `- [ ] /drift-check passes` checkbox. A slice can therefore finish and commit with the drift-check gate entirely unenforced. This slice makes drift-check an audit-enforced gate like its siblings, closing the silent-disable hole.

## Acceptance criteria

> **AC count = 6 (>5)** — justified per the slice-067 / slice-072 precedent: a new-mechanism mint that carries a paired-pin meta-AC (entry-pin) + a multi-leg version-bump meta-AC genuinely needs the extra rows. Critic findings B1/B2/M2/M3 (slice-081 /critique) are folded in as acceptance criteria.

1. A `tools/drift_check_audit.py` module exists, exposes a `main()` entry point, conforms to UTF8-STDOUT-1, and performs a real (non-stub) enforcement check returning exit 0 (clean) / 1 (`drift-check-not-run` or `escape-hatch-malformed`) / 2 (usage-error / mode-unresolvable) — the CRP-1 exit-code contract, with the mode-resolution and escape-hatch literals copied verbatim from `tools/critique_review_prerequisite_audit.py` (M1).
2. `skills/build-slice/SKILL.md` Step 6 invokes the audit programmatically (`$PY -m tools.drift_check_audit architecture/slices/slice-NNN-<name>`) as a documented HALT gate, **after** a `/drift-check` **full-mode** run (only full mode writes the `drift-log.md` marker; `--fast` writes none — M2), replacing the bare honor-system checkbox; in-repo↔installed build-slice copies stay content-equal (skill-drift guard).
3. Marker contract is consistent AND false-ACCEPT-safe (B1 + critique-review M-add-1): `skills/drift-check/SKILL.md` full-mode `**Trigger**:` template emits the canonical `slice-NNN` form (not `sliceNN`); the audit matches **only on `**Trigger**:`-prefixed lines** (line-anchored, NOT a whole-file scan) AND anchored on the slice number (`slice[- ]?0*<N>\b`) so canonical/habit/sloppy forms resolve while cross-mentions of the slice number in other entries' Notes/Scope/headings do NOT false-ACCEPT. Pinned by tests including the M-add-1 negative fixture (slice token only in a prior entry's non-Trigger line → exit 1). The BFRD-1 repro `tests/bugs/test_drift_check_enforcement_gap.py` PASSES (both functions).
4. Escape-hatch lifecycle is complete (B2): `drift-check-skip:` is added to the verbatim-preserved frontmatter keys at `skills/build-slice/SKILL.md` Step 7b (alongside `critique-review-skip:`) AND documented in `~/.claude/templates/milestone.md`; a canonical `drift-check-skip: "skip — rationale: <text>"` is accepted (exit 0) and a malformed value is refused (exit 1).
5. Version + registration meta-AC (M3): a 4-part atomic bump 0.75.0→0.76.0 across `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + installed `~/.claude/ai-sdlc-VERSION`; a `## v0.76.0` DCE-1 changelog entry forward-synced (MCFS-1) with a `test_v_0_76_0_dce_1_*` entry-pin; PMI-1 + INST-1 enumerate `tools/drift_check_audit.py` and stay green.
6. Self-application / bootstrap: DCE-1 runs against this very repo at slice finish and exits 0 — which requires slice-081's own Step 6 to run `/drift-check` (writing the `slice-081` marker) before the audit, proving the gate does not false-fire on a conformant tree.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Audit tool exists + real check + exit contract | `$PY -c "import tools.drift_check_audit as m; assert hasattr(m,'main')"`; run on clean fixture (exit 0), violation fixture (exit 1), malformed-skip fixture (exit 1), mode-unresolvable fixture (exit 2); confirm `_SKIP_VALUE_RE` / `_resolve_mode` literals byte-match `tools/critique_review_prerequisite_audit.py` |
| 2 | Wired into Step 6 (full-mode + HALT) | `grep "tools.drift_check_audit" skills/build-slice/SKILL.md` + confirm the sub-block specifies `/drift-check` full mode before the audit; build-slice skill-drift test green (in-repo↔installed) |
| 3 | Marker contract consistent + false-ACCEPT-safe | `grep "slice-NNN pre-finish gate" skills/drift-check/SKILL.md` (canonical form); APED-1: run the line-anchored matcher against (i) `**Trigger**: slice-081 …`→accept, (ii) `slice81`/`sliceNN` Trigger forms, (iii) `slice-0810`→reject, (iv) slice token only in a prior entry's Notes/heading, no Trigger line→**exit 1** (M-add-1); quote output; repro `$PY -m pytest tests/bugs/test_drift_check_enforcement_gap.py -v` → 2 passed |
| 4 | Escape-hatch lifecycle | `grep "drift-check-skip" skills/build-slice/SKILL.md` (Step 7b preserved-keys) + `~/.claude/templates/milestone.md`; audit on canonical skip → exit 0, malformed skip → exit 1 |
| 5 | Version + registration | `$PY -m tools.plugin_manifest_audit`; `$PY -m tools.install_audit`; `$PY -m tools.ai_sdlc_version_forward_sync`; `$PY -m tools.ai_sdlc_tools_version_forward_sync`; `$PY -m tools.methodology_changelog_forward_sync`; confirm `## v0.76.0` entry + `test_v_0_76_0_dce_1_*` entry-pin pass |
| 6 | Self-application clean | `$PY -m tools.drift_check_audit architecture/slices/slice-081-fix-drift-check-enforcement-gap` on this repo at finish → exit 0 (after the slice-081 `/drift-check` marker is written) |

## Must-not-defer

- [ ] The audit performs a genuine enforcement check — NOT a no-op/`return 0` stub (a theater gate is worse than none; this is the R-7 silent-disable class the slice exists to close).
- [ ] Fail-closed + false-positive safety: clean repo → exit 0; the violation condition is precisely defined so the gate cannot be trivially satisfied. Document the exit-code contract (0 clean / 1 violation / 2 usage-error) mirroring sibling audits.
- [ ] UTF8-STDOUT-1 conformance (`_stdout.reconfigure_stdout_utf8()` first statement of `main()`).
- [ ] The audit ships with its own unit tests using a clean fixture AND a violation fixture (APED-1 empirical-execution discipline) — not only the structural repro test.
- [ ] New rule + ADR minted (append-only); shippability propagation (RPCD-1/SCPD-1) for the new audit's own consumer references; version bump synced across PMI-1/MCFS-1/AVFS-1/TVFS-1 surfaces.

## Out of scope

- Re-implementing Claude's full semantic vault-vs-code drift comparison in Python. The audit enforces a well-defined structural/procedural subset (decided in `/design-slice` — e.g. "a drift-check was run for this slice" and/or the cheap mechanical checks: ADR library claims vs `pyproject.toml`, referenced source paths exist). The semantic, judgment-heavy drift reading stays Claude's job via the `/drift-check` skill.
- Installing a git pre-commit hook (the skill claims `/triage` does this; whether to actually install one is a separate decision — this slice closes the Step-6 *gate* enforcement, not the commit-hook delivery).
- Changing the `/drift-check` skill's own algorithm or output format beyond what's needed to wire the gate.

## Dependencies

- Failing repro test (BFRD-1 prerequisite): `tests/bugs/test_drift_check_enforcement_gap.py::test_drift_check_audit_tool_exists` and `::test_drift_check_audit_wired_into_build_slice_step6` — established 2026-05-29, currently FAILING; AC #3 asserts they PASS at slice end. Pinned in `architecture/shippability.md` row 86.
- Vault refs: [[skills/build-slice/SKILL.md]] Step 6, [[skills/drift-check/SKILL.md]], CLAUDE.md vault discipline, `architecture/shippability.md`.
- Sibling-gate precedents to mirror: [[slice-063-add-build-slice-new-agent-warning]] (NAW-1), [[slice-059-add-tools-package-version-gate]] (TVFS-1), [[slice-027-add-pipeline-chain-auto-advance]] (PCA-1), [[slice-080-harden-bc1-critical-rules-exit-gate]] (BCSG-1).
- Risk register: not currently tracked (fresh user-identified defect); a new risk sub-entry may be registered at `/reflect` if a residual failure mode is anticipated.

## Mid-slice smoke gate

At ~50% of build (after `tools/drift_check_audit.py` exists but before full Step 6 wiring), run:
```
$PY -m tools.drift_check_audit <args>   # on a clean fixture → exit 0
$PY -m pytest tests/bugs/test_drift_check_enforcement_gap.py::test_drift_check_audit_tool_exists -q
```
Expected: clean fixture exits 0; the tool-exists repro function PASSES. If fails: STOP, diagnose, don't continue to wiring.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes (and the NEW `tools/drift_check_audit` gate exits 0 on this repo — self-application)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
