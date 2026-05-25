---
id: ADR-056
title: Mint PVFS-1 (Pyproject Version Forward Sync) — pyproject.toml [project].version MUST equal trimmed VERSION; gate is a pytest assertion mirroring PMI-1's plugin.yaml↔VERSION pattern; no standalone tool.
date: 2026-05-21
slice: slice-054-fix-pyproject-toml-version-drift
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-056: Mint PVFS-1 (Pyproject Version Forward Sync)

## Context

`pyproject.toml [project].version` and `VERSION` had drifted to `"0.20.0"` vs `0.61.0` — 41 minor versions apart — at the start of slice-054 (SC-001, surfaced in `diagnose-out/backlog.md` as CRITICAL severity from the slice-053 `/diagnose` round-trip). `pip install <repo>` produced `ai-sdlc-tools 0.20.0` as a stale pip artifact label for every external consumer.

PMI-1 (`tools/plugin_manifest_audit.py:207-217`, slice-021 / methodology v0.19.0) gates `plugin.yaml.version` against `VERSION`. The PMI-1 docstring at L18-22 frames the rule purpose:

> a plugin manifest that drifts from the actual distribution is worse than no manifest — installers see "anthropic-ai-sdlc 0.19.0" with N skills but the package contains N+M because someone added a skill without updating the manifest. PMI-1 keeps both in sync at audit time.

Same defect class applies to `pyproject.toml` — but PMI-1's scope is plugin.yaml only. Pyproject was an ungated PMI-1 sibling — not a deliberate exemption, just an uncovered surface. The drift went unnoticed for ~41 methodology-changelog versions and surfaced only at the `/diagnose` audit.

The AVFS-1 (slice-050) / MCFS-1 (slice-041) lineage established the **forward-sync gate family** pattern: each canonical-VERSION leg gets its own gate keyed off the in-repo `VERSION` source of truth. PMI-1 covers `plugin.yaml`; MCFS-1 covers in-repo↔installed methodology-changelog parity; AVFS-1 covers the installed `~/.claude/ai-sdlc-VERSION` leg. PVFS-1 closes the pyproject.toml leg.

The Inclusion-heuristic decision (per `agents/critique.md` Dim 7 MEPD-1) was settled at `/design-slice` Step 2 by the user: **Route B — new RULE-ID, lightweight (no standalone tool)**. The user-rejected alternatives are recorded below.

## Options considered

1. **Route A — born-retired conformance class (no RULE-ID / no methodology-changelog entry / no VERSION bump)**:
   - **Pros**: Cheapest path. Slice-045 precedent (R-11 born-retired for INSTALL.md graphifyy package-name fix + stale `v0.20.0` literal scrub). MEPD-1(b) why-none discharge possible: pyproject.toml is not in the strict in-house methodology surface enumeration (skills/, agents/, tools/, methodology-changelog.md).
   - **Cons**: The pyproject↔VERSION lock-step gate is structurally new — no prior rule pinned it. Slice-045's R-11 scope was strictly stale-literal scrub + regression-pin (no new structural invariant); slice-054 introduces a new structural invariant. The gate exists only as shippability row #54 → methodology-discoverability gap (a future reader of `methodology-changelog.md` or `agents/critique.md` MEPD-1 has no rule-ID anchor to find PVFS-1).
   - **Rejected because**: PMI-1 docstring L18-22 explicitly frames the parent class ("manifest version drift is worse than no manifest") — closing the pyproject carve-out is a new rule scope deserving methodology-discoverability, not a hidden shippability-only pin.

2. **Route B — new RULE-ID PVFS-1, lightweight (no standalone tool)** *(chosen)*:
   - **Pros**: Methodology-discoverable (named rule + ADR + changelog entry + entry-pin test pair). 4-part PMI-1 atomic bump aligns with the AVFS-1 / MCFS-1 family pattern. SOAD-1 (slice-048) and BCR-1 (slice-053) precedent: rule-without-tool is legitimate when the gate is enforceable via pytest assertion alone. The fix substance stays small (one literal bump + one already-failing test + one stale-prose scrub + 2 entry-pin tests + ADR + changelog entry).
   - **Cons**: 4-part PMI-1 atomic bump must stay atomic (AVFS-1 / PMI-1 / MCFS-1 gates catch lag at /build-slice Step 6 + /reflect Step 5b — proven backstop; not a blocker). Slightly more surface than Route A (one ADR + one changelog entry + 2 entry-pin tests + row #54 enrichment).
   - **Chosen because**: Methodology-discoverability matters more than the marginal cost; the gate joins the existing forward-sync family deliberately, not by accident.

3. **Route C — new RULE-ID PVFS-1 + standalone tool `tools/pyproject_version_forward_sync.py`**:
   - **Pros**: Full AVFS-1 analogue. Most discoverable; matches the forward-sync family shape (PMI-1 / AVFS-1 / MCFS-1 are all `tools/*.py`).
   - **Cons**: Over-engineering. AVFS-1 minted a standalone tool because `~/.claude/ai-sdlc-VERSION` lives OUT of repo (runtime read required for installed leg). pyproject.toml is in-repo — pytest assertion is structurally sufficient. A tool would just wrap the pytest assertion in CLI scaffolding with no operational benefit. /reduce complexity-budget concern.
   - **Rejected because**: The forward-sync family's tool-bearing members (PMI-1, AVFS-1, MCFS-1) each address a structural need a pytest assertion couldn't meet (PMI-1 reads filesystem layout; AVFS-1 reads OUT-of-repo installed file; MCFS-1 reads OUT-of-repo installed file). PVFS-1 has no such structural need.

## Decision

Mint **PVFS-1 (Pyproject Version Forward Sync)** as a new methodology-class rule-ID via Route B. PVFS-1 asserts: `pyproject.toml [project].version` MUST equal the trimmed contents of `VERSION`. The gate is the pytest assertion `tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file` (already authored at slice-054 BFRD-1 `/repro`). The gate is invoked at `/validate-slice` Step 5.5 via the shippability runner (catalog row #54). No standalone audit tool is minted; `tools/plugin_manifest_audit.py` (PMI-1) is NOT edited (PVFS-1 is a sibling gate, not a PMI-1 sub-rule).

Atomic 4-part PMI-1 bump 0.61.0 → 0.62.0 applies (VERSION + plugin.yaml.version + methodology-changelog `## v0.62.0` header + installed `~/.claude/ai-sdlc-VERSION`).

Mints a new rule. Supersedes nothing. Extends the PMI-1 / AVFS-1 / MCFS-1 forward-sync family on the pyproject.toml leg.

## Consequences

- **Downstream gates** (additive, no existing gate disturbed):
  - `/validate-slice` Step 5.5 catalog runner runs the PVFS-1 pytest assertion via row #54.
  - `/build-slice` Step 6 pre-finish: the standard `pytest tests/methodology/` sweep covers PVFS-1.
  - `/reflect` Step 5b-avfs: AVFS-1 already gates the installed leg of the 4-part bump.
- **Methodology-changelog v0.62.0** entry is added; META-1 + MCFS-1 cover its parity / shape.
- **shippability row #54** is enriched with `PVFS-1` rule-ID anchor (was: `SC-001` only).
- **Two entry-pin tests** are added: `test_v_0_62_0_pvfs_1_entry_present_in_repo` + `test_v_0_62_0_pvfs_1_shippability_consumer_propagation` (content-bearing per slice-051 precedent; NOT thin presence checks).
- **No new code-level API contract** (PVFS-1 is a methodology-discipline rule, not a runtime contract).
- **No vault component added** (Standard mode thin vault; pyproject.toml is a config file, not a component).
- **CLAUDE.md NOT edited in this slice**: PVFS-1 is a packaging/manifest rule enforced at audit time, not a per-edit discipline a contributor needs to think about. Adding a `## Packaging discipline` section to CLAUDE.md is a separate slice candidate if it ever becomes warranted.
- **BCR-1 round-trip dogfood**: slice-054 is the first end-to-end exercise of slice-053's `**Closes:** SC-NNN` → `/reflect`-injects-`**Addressed:**` wire (AC4).

## Reversibility

**Cheap.** PVFS-1 is enforced by a single pytest assertion in a single test file. Reverting means:
1. Delete the test function (or relax the assertion).
2. Drop shippability row #54 (or remove the `PVFS-1` anchor from it).
3. Add a SUP-1 supersession ADR explaining the reversal rationale.
4. The pyproject.toml `[project].version` literal can stay or drift — neither blocks any other gate.

No downstream consumer is built on top of PVFS-1's existence. PMI-1 / AVFS-1 / MCFS-1 stay unaffected. The reversal cost is ~30 minutes of focused work (one test removal + one shippability edit + one ADR).

The atomic 4-part PMI-1 bump itself is also cheap-reversible: VERSION can be rolled back if the v0.62.0 entry needs to be retracted, but this would require a methodology-changelog SUP-1 entry per the changelog's append-only discipline.
