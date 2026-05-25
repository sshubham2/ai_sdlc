# Slice 053: wire-backlog-md-into-slice-and-reflect

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: a methodology-surface deviation directly observed on this very `/slice` invocation (2026-05-20) — when `diagnose-out/backlog.md` exists, the `/slice` skill currently does NOT enumerate it among the "Gather candidates from ALL these sources" list (sources #1–6 cover risk-register / deferrals / discoveries / concept / lessons / user-stated intent only — NOT the `/diagnose → /slice-candidates` backlog). On this slice's own invocation, Claude ranked candidates from internal pipeline signals alone (R-13 OSDG-1 + audit-recovered risks) and missed the 26 owner-confirmed `/diagnose` backlog candidates (incl. **SC-001** — `pyproject.toml [project].version = 0.20.0` vs `VERSION = 0.60.0`, a critical live-defect: `pip install` produces a 40-minor-version-stale artifact). The user had to interrupt and re-route. The same round-trip is also missing from `/reflect` (Step 2 vault updates do not mention `backlog.md`), so closed backlog rows accumulate without status updates — the diagnose→slice→reflect loop is open. NOT a registered risk ID at brief-time; risk-register entry will be added by /design-slice / /reflect (the slice-049/052 precedent for an N=1 latent methodology-surface exposure surfaced mid-pipeline).
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Close the open half of the `/diagnose → /slice-candidates → /slice → /reflect` loop by adding `diagnose-out/backlog.md` as an authoritative candidate source in `/slice` (mandatory consultation when the file exists) and a round-trip annotation step in `/reflect` (mark addressed `SC-NNN` rows with the slice ID + date when their underlying finding(s) ship). Mint a new minimal rule-ID (call it `BCR-1` provisionally — *Backlog Consume-and-Round-trip discipline*; final name decided at /design-slice) governing the two-direction contract, and back it with a deterministic skill-prose anchor-presence audit (positive pins on both SKILL.md surfaces) so the wire cannot silently regress under future skill edits. Per the slice-049/052 Inclusion-heuristic + BC-PROJ-10 law, this IS a methodology-surface behavior change → carries the version-bump + ADR + entry-pin path (4-part PMI-1 atomic bump 0.60.0→0.61.0 + shippability row).

The slice's own existence is the proof of the gap: on its parent invocation, the `/slice` skill demonstrably failed to surface `backlog.md` candidates until the user interrupted. The fix is a load-bearing pipeline-continuity contract, not a cosmetic doc update.

## Acceptance criteria

1. `skills/slice/SKILL.md` "Gather candidates from ALL these sources" block names `diagnose-out/backlog.md` as a mandatory source (when the file exists), with explicit guidance on how to read it (the file's recommended-order list IS topo-sorted by dependency × severity / effort and is the primary input). Lock-step synced to `~/.claude/skills/slice/SKILL.md` (OSDG-1 guarded — `test_slice_skill_drift.py` already pins).
2. `skills/reflect/SKILL.md` Step 2 (vault updates) names `diagnose-out/backlog.md` as a target file: when the just-shipped slice closed one or more `SC-NNN` rows (because the slice was derived from a backlog candidate OR because its work happens to close a finding), `/reflect` MUST update those rows with `addressed-by: slice-NNN-<name>` + date. Lock-step synced to `~/.claude/skills/reflect/SKILL.md` (OSDG-1 guarded — `test_reflect_skill_drift.py` already pins).
3. A new deterministic anchor-presence audit asserts both contracts (positive pins on both SKILL.md surfaces; EOL-agnostic per ADR-033 / EOL-DRIFT-1 if cross-file comparison needed). The audit FAILs under per-surface genuine-contrast perturbation (remove the anchor → FAIL; restore → PASS) and PASSes on the fixed tree. Provisional name `BCR-1` (final name + RULE-ID conventions per `/design-slice`).
4. The methodology-surface behavior change is recorded: a new ADR extending the BC-PROJ-10 / Inclusion-heuristic lineage + a `methodology-changelog.md` `## v0.61.0` entry naming the new RULE-ID + the corresponding `test_methodology_changelog.py` entry-pin, with the 4-part PMI-1 atomic bump applied (`VERSION` 0.60.0→0.61.0 + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`). CLAUDE.md's brownfield rules section names the new contract.
5. Full methodology suite + all slice-finish audits (PMI-1, INST-1, CAD-1, RR-1, SUP-1, BC-1, drift-check, branch-workflow, pipeline-chain) pass green at pre-finish. One shippability row added for this slice's critical path. Risk-register entry minted for the now-mitigated drift (status: `mitigating` — the anchor-presence audit closes the structural deterministic axis; the human-judgement axis remains until a Critic-prompt dimension is added in a future slice).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | /slice SKILL.md backlog-md source named | `grep -n 'diagnose-out/backlog.md' skills/slice/SKILL.md` returns at least one hit in the "Gather candidates from ALL these sources" block; in-repo↔installed content-equal mod EOL via existing `test_slice_skill_drift.py` (PASS post-sync) |
| 2 | /reflect SKILL.md backlog-md round-trip named | `grep -n 'diagnose-out/backlog.md' skills/reflect/SKILL.md` returns at least one hit in Step 2 vault-updates block; in-repo↔installed content-equal mod EOL via existing `test_reflect_skill_drift.py` (PASS post-sync) |
| 3 | New audit exists + passes + genuine FAIL→PASS contrast | `$PY -m pytest tests/methodology/test_<bcr_1_audit>.py -q` → green on synced tree; perturb the anchor in each surface (one byte, NOT EOL, OUTSIDE any other anchor) → FAIL with surface-specific message; restore → PASS. Recorded in build-log.md. |
| 4 | Methodology-surface change recorded | new `decisions/ADR-0NN` extending BC-PROJ-10 / Inclusion-heuristic lineage; `methodology-changelog.md` has `## v0.61.0` entry naming BCR-1 (or final name); `test_methodology_changelog.py` entry-pin asserts it; `$PY -m tools.plugin_manifest_audit` clean (version parity 4-leg); `~/.claude/ai-sdlc-VERSION` == `VERSION` == `plugin.yaml.version`; CLAUDE.md self-hosting OR brownfield-rules section names BCR-1 |
| 5 | Suite + audits + shippability green | `/validate-slice` (VAL-1 + WS-1 + ETC-1 + shippability runner) + full `pytest tests/methodology` green; `$PY -m tools.critique_agent_drift_audit --repo-root .` clean; `$PY -m tools.shippability_runner architecture/shippability.md` 53/53 PASS (52 prior rows + this slice's row); `$PY -m tools.risk_register_audit` clean (new entry for the closed gap, status `mitigating`); BRANCH-1 audit clean (slice/053 branch); pipeline-chain audit clean |

## Must-not-defer

- [ ] **The contract must be bidirectional**: /slice consults backlog.md AND /reflect updates it. A one-way fix (read-only consumption without round-trip update) leaves the loop half-open and recreates a different staleness class (backlog rows that say "to do" but were silently shipped). Both anchors are pinned in the same audit.
- [ ] **EOL-agnostic skill-drift comparison**: existing `test_slice_skill_drift.py` + `test_reflect_skill_drift.py` already enforce this (CRLF↔LF is NOT drift per ADR-033 / EOL-DRIFT-1) — do NOT bypass them with a raw-byte audit
- [ ] **Per-surface genuine-contrast proof**: perturb the anchor in `skills/slice/SKILL.md` AND in `skills/reflect/SKILL.md` independently (no shared-mock proxy) — confirm each surface FAILs independently
- [ ] **Forward-sync installed SKILL.md copies BEFORE running OSDG-1 drift tests**: byte/EOL-verified sync to `~/.claude/skills/{slice,reflect}/SKILL.md` so the OSDG-1 family is green for the right reason (slice-051 precedent)
- [ ] **4-part PMI-1 bump applied atomically** (no partial leg — the slice-035 / slice-048→049 leg-drift class this discipline exists to prevent; AVFS-1 also gates the installed `~/.claude/ai-sdlc-VERSION` leg)
- [ ] **Entry-pin added to `test_methodology_changelog.py` for `## v0.61.0`** (not just the changelog text; the entry-pin shape is content-bearing per slice-049/051)
- [ ] **Shippability catalog row** added per RPCD-1 / SCPD-1 — an uncatalogued anchor-presence audit's breakage would be invisible to the catalog runner (slice-040 precedent)
- [ ] **Inclusion-heuristic classification stated explicitly** in design.md / mission-brief.md (this brief discharges it now): this slice mints a new RULE-ID + changes contract behavior on two OSDG-1-guarded SKILL.md surfaces → IS a methodology-surface behavior change → 4-part PMI-1 bump path; per BC-PROJ-10 (slice-052)
- [ ] **CLAUDE.md self-hosting / brownfield-rules update** naming BCR-1 alongside CAD-1 / OSDG-1 / PMI-1 / INST-1 / Mini-CAD (the canonical methodology-surface contracts list)

## Out of scope

- The 26 backlog candidates themselves (SC-001 through SC-026) — this slice WIRES the consumption channel; SC-001 (the critical pyproject.toml version drift, owner-flagged "major bug") is the immediate next-slice candidate after this lands, and the rest follow the backlog's topo-sort
- A Critic-prompt dimension closing the human-judgement axis (the brief's "Claude missed backlog.md" failure mode) — the anchor-presence audit closes the structural deterministic axis; the Critic-prompt addition is canonical `/critic-calibrate` territory, separate slice
- Generalizing to non-/diagnose backlog sources (e.g. a `TODO.md` at repo root, GitHub Issues) — the contract scope is *exactly* the `/diagnose` round-trip artifact `diagnose-out/backlog.md`
- A live programmatic test that parses backlog.md and asserts candidate-ID syntax (`SC-\d{3}`) — anchor-presence on SKILL.md prose is the v1 contract; structural backlog.md grammar pin is a future slice if drift emerges
- Backporting closure annotations to slices 1-52's already-closed work — backlog.md is a 2026-05-20 artifact; round-trip applies from slice-053 forward
- Any /diagnose, /slice-candidates, or assemble.py source change — they emit backlog.md unchanged; only /slice + /reflect SKILL.md prose + a new audit + ADR + methodology-changelog change

## Dependencies

- Prior slices: [[slice-052-add-slice-candidates-obo-mode]] — established the `/diagnose → /slice-candidates → backlog.md` half of the loop; this slice closes the `→ /slice → /reflect` half. [[slice-051-extend-osdg-1-to-reflect-skill]] — OSDG-1 already guards `reflect/SKILL.md` (the new anchor will be drift-protected for free). [[slice-049-add-triage-adopt-skill-drift-guards]] — the ADR-051 OSDG-1 lineage + Inclusion-heuristic precedent this slice inherits. [[slice-046-add-conditional-repro-auto-advance]] — precedent for `/slice` itself acquiring new behavior via SKILL.md prose pinned by anchor-presence tests (ADR-048).
- Vault refs: [[skills/slice/SKILL.md]] (Gather candidates from ALL these sources block — to edit), [[skills/reflect/SKILL.md]] (Step 2 vault updates block — to edit), [[skills/slice-candidates/SKILL.md]] (the producer of backlog.md — read-only context), [[diagnose-out/backlog.md]] (the artifact being wired in), CLAUDE.md "Self-hosting discipline" + "Brownfield rules", [[decisions/ADR-051]] (OSDG-1 lineage), [[decisions/ADR-053]] (slice-051 OSDG-1 reflect-extension)
- Risk register: no open risk ID at brief-time (N=1 latent exposure surfaced on this very `/slice` invocation, consistent with the slice-049/052 mid-pipeline-discovery handling); a new entry will be minted at /reflect Step 2

## Mid-slice smoke gate

At ~50% of build (both SKILL.md anchor edits written + installed copies synced + new audit drafted, before the methodology-changelog/PMI-1 bump), run:
```
$PY -m pytest tests/methodology/test_slice_skill_drift.py tests/methodology/test_reflect_skill_drift.py -q
```
Expected: PASS on the synced tree (both OSDG-1-guarded surfaces in-repo↔installed content-equal mod EOL).

Then run the new audit (whatever its module path resolves to at design-time):
```
$PY -m pytest tests/methodology/test_<bcr_1_audit>.py -q
```
Expected: PASS on the fixed tree.

Genuine-contrast check at this point: perturb the `diagnose-out/backlog.md` anchor in `skills/slice/SKILL.md` (one byte OUTSIDE any other anchor, NOT EOL) and re-run the new audit → expect FAIL with surface-specific message. Restore. Repeat for `skills/reflect/SKILL.md`. Run isolated tests only — do NOT run the full methodology suite during a perturbation window (`test_slice_skill_drift.py` and `test_reflect_skill_drift.py` would co-FAIL and pollute the contrast signal; slice-051 mid-slice smoke precedent). Record both genuine-contrast runs in build-log.md.

If the new audit passes under perturbation or fails on the synced tree: STOP, diagnose (likely a wrong helper import, an anchor regex that's too loose, or a raw-byte compare in place of the EOL-normalized helper), don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes (vault and code aligned; SKILL.md prose matches the round-trip the audit pins)
- [ ] Mid-slice smoke still passes (no regression after the v0.61.0 bump + ADR + changelog entry-pin)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 (4-leg version parity green) / INST-1 / CAD-1 / RR-1 / SUP-1 / BC-1 / BRANCH-1 / pipeline-chain / state-transition-pin / shippability-runner 53/53 / mock-budget-lint all green
- [ ] AVFS-1 forward-sync gate green (`~/.claude/ai-sdlc-VERSION` == `VERSION` == 0.61.0); MCFS-1 green (`~/.claude/methodology-changelog.md` content-equal mod EOL to in-repo)
- [ ] OSDG-1 family green: `test_{slice,reflect,build_slice,commit_slice,query_design,critique,diagnose,triage,adopt}_skill_drift.py` all PASS
- [ ] Full `pytest tests/methodology` green (no regressions in the ~764-test suite)
- [ ] Inclusion-heuristic classification statement present in this brief AND in design.md (BC-PROJ-10 dischargement)
