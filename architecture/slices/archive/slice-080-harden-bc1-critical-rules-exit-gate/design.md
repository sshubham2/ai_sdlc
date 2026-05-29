# Design: Slice 080 harden-bc1-critical-rules-exit-gate

**Date**: 2026-05-29
**Mode**: Standard

## What's new

- `tools/build_checks_audit.py` gains two opt-in CLI flags + matching `audit_slice` kwargs:
  - `--strict` — turns BC-1 from surface-only into an enforced gate: applicable Critical rules that are not acknowledged become **violations**, so the existing `return 1 if result.violations else 0` exit logic yields exit 1.
  - `--ack-critical <RULE-ID> [<RULE-ID> ...]` — the builder's explicit sign-off list; an applicable Critical rule whose `rule_id` is in this set is considered addressed and does NOT become a violation.
- A new `BuildCheckViolation` kind `unacknowledged-critical` (severity `Critical`), appended ONLY under `--strict`, one per applicable Critical rule absent from the ack set.
- `skills/build-slice/SKILL.md` Step 6 BC-1 invocation gains `--strict --ack-critical <addressed rule IDs>` + updated refusal-semantics prose stating the gate is now mechanical (forward-synced to the installed copy per OSDG-1).
- `methodology-changelog.md` `## v0.75.0` entry minting **BCSG-1** (BC-1 Strict Critical-Gate; refines BC-1 in place, supersedes nothing — TFFL-1/slice-034 precedent) + `VERSION` 0.74.0 → 0.75.0 + `plugin.yaml` version sync (PMI-1).

## What's reused

- Existing audit pipeline: `audit_slice()`, `BuildCheckRule`, `BuildCheckViolation`, `AuditResult`, `_format_human()`, `main()` exit logic at `tools/build_checks_audit.py:619`.
- `AuditResult.to_dict()` already computes `summary.critical_applicable` (`tools/build_checks_audit.py:154`) — the strict gate iterates `result.applicable` filtered by `severity.lower() == "critical"`, the same predicate.
- The `--strict` → append-to-`result.violations` → `return 1 if result.violations else 0` idiom from `tools/test_first_audit.py:460-479,629` and `tools/walking_skeleton_audit.py:343,433` (BC-1's flag is named `--strict` not `--strict-pre-finish` because BC-1 has a single gate point, not a status-progression lifecycle).
- BFRD-1 repro: `tests/bugs/test_bc1_critical_rule_exit_gate.py` (established this session; shippability row #85).
- Test fixtures `tests/methodology/fixtures/build_checks/one_always_applies.md` (1 Critical always-rule) + `clean_project_checks.md` (0 rules).
- [[ADR-034]] / TFFL-1 — the "refine an existing audit in place, mint a refinement RULE-ID, supersede nothing" precedent.

## Components touched

### `tools/build_checks_audit.py` (modified)
- **Responsibility**: surface + (now, under `--strict`) enforce evergreen BC-1 build-checks rules at `/build-slice` pre-finish.
- **Lives at**: `tools/build_checks_audit.py`.
- **Key interactions**: invoked by `skills/build-slice/SKILL.md` Step 6 (sole runtime consumer); reads `architecture/build-checks.md` + `~/.claude/build-checks.md`.
- **Change shape**:
  - `audit_slice(...)` gains `strict: bool = False` and `ack_critical: tuple[str, ...] = ()` kwargs (default-off preserves every existing caller). After applicability resolution, when `strict` is true, for each rule in `result.applicable` with `severity.lower() == "critical"` whose `rule_id not in set(ack_critical)`, append `BuildCheckViolation(path="<build-checks source>", line=rule.line, rule_id=rule.rule_id, kind="unacknowledged-critical", severity="Critical", message="applicable Critical rule not acknowledged via --ack-critical; address it and pass its rule ID")`.
  - `main()` adds `--strict` (`store_true`) + `--ack-critical` (`nargs="*", default=[]`); threads both into `audit_slice`. Exit logic at L619 is **unchanged** (`return 1 if result.violations else 0`) — the strict gate works purely by populating `violations`.
  - `_format_human()` gains a line under `--strict` summarizing acknowledged vs unacknowledged Critical rules (output is informational; never suppresses the surfaced-rules report).
  - `BuildCheckViolation` docstring comment "severity: always Important" updated to note the `unacknowledged-critical` Critical-severity exception.

### `skills/build-slice/SKILL.md` (modified)
- **Responsibility**: drives the pre-finish gate sequence; Step 6 invokes BC-1.
- **Lives at**: `skills/build-slice/SKILL.md` (Step 6 "Build-checks audit (BC-1)" block, ~L391-415) + installed `~/.claude/skills/build-slice/SKILL.md` (OSDG-1 lock-step).
- **Change shape**: the invocation codefence gains `--strict --ack-critical <addressed Critical rule IDs>`; refusal-semantics prose updated — "Critical rules are not deferrable" is now mechanically enforced: under `--strict` an unacknowledged applicable Critical rule fails the audit (exit 1); the builder addresses each Critical rule, documents in build-log.md, and passes its rule ID to `--ack-critical`. The v1/v2 caveat at L415 is rewritten to reflect that exit-code enforcement now exists (acknowledgment-based), while executable per-rule auto-verification (running the `Validation hint`) remains the deferred v2.

## Contracts added or changed

### `build_checks_audit` CLI contract (changed — additive, backward-compatible)
- **Defined in code at**: `tools/build_checks_audit.py` `main()` argparse + `audit_slice()` signature.
- **New flags**: `--strict` (opt-in; default off → identical legacy behavior), `--ack-critical <RULE-ID...>` (only meaningful under `--strict`; ignored otherwise).
- **Exit codes** (unchanged shape): `0` = clean (no parse violations; under `--strict`, all applicable Critical rules acknowledged or none applicable); `1` = parse violations OR (under `--strict`) ≥1 unacknowledged applicable Critical rule; `2` = usage error (slice folder not found).
- **JSON**: `--json` output unchanged in shape; the new `unacknowledged-critical` violations appear in the existing `violations` array; `summary.critical_applicable` already present.
- **Auth model**: n/a (local CLI audit tool).
- **Error/edge cases**:
  - `--ack-critical` of a rule ID that is not an applicable Critical rule → **ignored** (lenient ack; only applicable Critical rules are checked against the set). Deliberate v1 choice — a stale/extraneous ack is harmless and avoids coupling the ack list to exact applicability; flagged for Critic. Out of scope: warning on over-acknowledgment / stale-ack drift detection.
  - `--ack-critical` without `--strict` → ignored (no gate active).
  - NFR-1 carry-over slice → zero applicable rules → exit 0 under `--strict` (unchanged).
  - Important rules → never gate, regardless of `--strict` (defer-with-rationale unchanged).

## Data model deltas

None. No new entity/field; `BuildCheckViolation` reuses its existing shape with a new `kind` value and (for this kind only) `severity="Critical"`.

## Wiring matrix

Per **WIRE-1**. This slice introduces no new module (it modifies existing `tools/build_checks_audit.py` + `skills/build-slice/SKILL.md`). Zero-row matrix → clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-072]] — BC-1 gains an opt-in `--strict` + `--ack-critical` acknowledgment gate (RULE-ID **BCSG-1**, refines BC-1 in place, supersedes nothing); acknowledgment is by explicit rule-ID sign-off rather than a persistent status surface; ack is lenient (extraneous IDs ignored) — reversibility: **cheap**.
- **MEPD-1 INCLUDE**: this changes a mandatory gate's enforcement behavior (a Critical-touching slice could previously pass `/build-slice` Step 6 with exit 0; post-slice it must acknowledge) — the Inclusion heuristic fires (extending an existing gate to refuse a previously-acceptable class; slice-049/051/057/058/059/062 precedent). Therefore the **5-part PMI-1 atomic version bump** (canonical 5 legs per `test_methodology_changelog.py` anchor): (1) `VERSION` 0.74.0→0.75.0, (2) `plugin.yaml` version, (3) `pyproject.toml [project].version` (PVFS-1, currently `0.74.0` at `pyproject.toml:20`), (4) `## v0.75.0` changelog header, (5) installed `~/.claude/ai-sdlc-VERSION` (AVFS-1). The installed `~/.claude/methodology-changelog.md` (MCFS-1) is a **separate** post-bump forward-sync obligation, NOT a PMI-1 atomic leg. PLUS: the `## v0.75.0` entry minting BCSG-1; the BC-PROJ-10 paired entry-pin pair (`test_v_0_75_0_bcsg_1_entry_present_in_repo` + `test_v_0_75_0_bcsg_1_shippability_consumer_propagation`); shippability row #85 (rewritten per M1). No new tool/skill/agent module → no BC-PROJ-9 inventory bump.

## Authorization model for this slice

n/a — `build_checks_audit` is a local CLI audit tool with no auth surface.

## Error model for this slice

- Exit 1 introduced for a NEW trigger: under `--strict`, ≥1 unacknowledged applicable Critical rule (via the `unacknowledged-critical` violation). Existing exit-1 trigger (parse violations) and exit-2 (usage) unchanged.
- Combined case: under `--strict`, parse violations AND unacknowledged Critical rules coexist → both populate `violations` → exit 1 (neither signal masks the other).

## Build plan — Critic-ratified additions (slice-080 /critique, TRI-1 pending)

These are named `/build-slice` steps surfaced by the Critic; recorded here so the plan does not ship stale.

- **(B2) Version-sync test supersession + propagation** — in the SAME build block, BEFORE the /validate-slice catalog run: (a) supersede `tests/methodology/test_methodology_changelog.py::test_version_files_synchronized_at_v_0_74_0` → `_at_v_0_75_0`, updating its four `0.74.0` literal asserts (VERSION / plugin.yaml / pyproject / `## v0.NN.0` changelog header — NOT installed ai-sdlc-VERSION, which is leg 5 and explicitly NOT asserted by this test per its own docstring) to `0.75.0`; (b) propagate the rename into `architecture/shippability.md` (the catalog row whose pytest command cites `test_version_files_synchronized_at_v_0_74_0`); (c) add the BC-PROJ-10 paired entry-pin pair `test_v_0_75_0_bcsg_1_entry_present_in_repo` + `test_v_0_75_0_bcsg_1_shippability_consumer_propagation`.
- **(B3) Self-application ack** — BC-PROJ-3 + BC-GLOBAL-2 are `Critical` + `always:true` (empirically `critical_applicable: 2` on this slice). slice-080's own Step 6 strict run MUST pass `--ack-critical BC-PROJ-3 BC-GLOBAL-2`, after attesting in build-log.md that this slice performs no destructive revert of uncommitted work (both are git-revert-discipline rules — genuinely satisfiable: this slice does no `git checkout`/`restore`/`stash` reverts). The SKILL.md Step 6 example + prose must instruct every future slice to first enumerate applicable Critical rules (`build_checks_audit ... --json`), address+attest each in build-log.md, then pass their IDs to `--ack-critical`.
- **(M3) Append placement pin** — the strict-append loop runs ONCE over the fully-assembled `result.applicable` (after BOTH the project and global source loops, immediately before `return result` in `audit_slice`), guarded by `if strict:`, and only when not carry-over-exempt (the NFR-1 early-return short-circuits before it — verified exit 0). Add a unit test asserting a **global-source** Critical rule is captured by the strict gate (the repro only exercises a project-source always-rule; BC-GLOBAL-2 is global-source).
- **(M2) Lenient-ack diagnostic** — `_format_human` under `--strict` must list (a) which applicable Critical rules are unacknowledged-and-firing (by ID) and (b) which `--ack-critical` IDs matched NO applicable Critical rule (so a typo'd/stale ack surfaces as e.g. "ack 'BC-PROJ3' matched no applicable Critical rule"). Exit semantics unchanged; this only converts the fail-CLOSED silent-no-op into a visible diagnostic.
- **(m1) nargs greediness** — in the SKILL.md Step 6 example, place `--ack-critical <ids>` last (or immediately before another flag) so `nargs="*"` does not swallow a following bareword. No code change.
- **(m2) Docstring kinds** — update `BuildCheckViolation` L128 `kind` comment (currently "missing-field | invalid-severity | parse-error", omits the existing `anchor-not-in-keywords` / `negative-anchor-overlaps-positive` AND the new `unacknowledged-critical`) and the L129 `severity` "always Important" comment to reflect the new Critical-severity kind.
