# Design: Slice 081 fix-drift-check-enforcement-gap

**Date**: 2026-05-29
**Mode**: Standard

## What's new

- **`tools/drift_check_audit.py`** — a new audit-enforced gate (rule **DCE-1**, "Drift-Check Enforcement"). A procedural gate in the shape of CRP-1: it refuses `/build-slice` Step 6 unless the current slice left its drift-check marker in `drift-log.md`, OR a documented escape-hatch is present, OR mode is MINIMAL. It does NOT re-implement Claude's semantic vault-vs-code drift reading (that stays the `/drift-check` skill's job). **Honest scope (per /critique M2)**: this is a *was-it-**marked*** gate, not a was-it-*run* gate — it proves a slice-referencing `drift-log.md` entry exists, which a slice could in principle satisfy by writing the entry without performing the semantic check. That residual gap is disclosed (mirroring NAW-1's known-false-positive disclosure at `tools/new_agent_warning_audit.py`); what it structurally closes is the **silent-skip** hole (the R-7 / slice-022 silent-disable failure class) — a slice can no longer finish with *no* drift-check trace at all.
- **`tests/methodology/test_drift_check_audit.py`** — the audit's own unit tests (clean fixture exits 0; violation fixture exits 1; escape-hatch accepted; malformed escape-hatch exits 1; MINIMAL accepted; mode-unresolvable exits 2; **M-add-1 negative fixture: a drift-log where the slice token appears only in a prior entry's Notes/Scope/heading with NO `**Trigger**:` line for the current slice → exits 1**). APED-1 empirical-execution discipline.
- **New rule DCE-1** in `methodology-changelog.md` (target **v0.76.0**) + **[[ADR-073]]**.
- **`skills/build-slice/SKILL.md` Step 6 wiring**: a new audit sub-block that (a) runs `/drift-check` **in full mode explicitly** (only full mode appends the slice-referencing entry to `architecture/drift-log.md`; `--fast` writes none — /critique M2) THEN (b) invokes `$PY -m tools.drift_check_audit architecture/slices/slice-NNN-<name>` — order load-bearing (the run must precede the verify, else the bootstrap can never discharge). Replaces the bare honor-system `- [ ] /drift-check passes` checkbox with an audit-enforced HALT gate.
- **`skills/build-slice/SKILL.md` Step 7b preservation (per /critique B2)**: add `drift-check-skip:` to the verbatim-preserved frontmatter keys at `skills/build-slice/SKILL.md` Step 7b (currently lists only `critique-review-skip:` at ~L494). Without this, the continuous milestone rewrite clobbers a legitimate skip key and the Step 6 DCE-1 re-run false-refuses — the exact bug ADR-024 L494 prevents for CRP-1. Also document `drift-check-skip: "skip — rationale: <text>"` in `~/.claude/templates/milestone.md` (currently shows only `critique-review-skip:`), and verify template-drift / INST-1 on it.
- **`skills/drift-check/SKILL.md` Trigger-template canonicalization (per /critique B1)**: change the full-mode `**Trigger**:` template at `skills/drift-check/SKILL.md:114` from `<pre-commit | manual | sliceNN pre-finish gate>` to the canonical dash-form `slice-NNN`, so the producer template matches the consumer audit; pin the canonical token with a test. (Defense-in-depth: the audit ALSO matches tolerantly — see Contracts.)
- **Registration**: `plugin.yaml` + `tools/install_audit.py` enumerate the new tool (PMI-1 / INST-1); 4-part version bump to v0.76.0 synced across `VERSION` / `plugin.yaml` / `pyproject.toml` / changelog (MCFS-1 / AVFS-1 / TVFS-1).
- **Shippability propagation**: row for the DCE-1 gate's own pinning tests (RPCD-1 / SCPD-1), alongside the existing repro row 86.

## What's reused

- [[skills/drift-check/SKILL.md]] — full-mode already documents appending a `## Audit <date>` block to `architecture/drift-log.md` with a `**Trigger**: slice-NNN pre-finish gate (...)` line. The audit matches against that existing convention; no change to the drift-check algorithm.
- `architecture/drift-log.md` — the existing append-only artifact (entries already use `Trigger: slice-NNN pre-finish gate`). This IS the marker the gate verifies.
- `tools/critique_review_prerequisite_audit.py` — the procedural-gate template (mode resolution; milestone.md frontmatter escape-hatch key keyed on the *key* not a body scan; exit-code contract). DCE-1 mirrors it structurally. **Per /critique M1, the build copies these literals BYTE-FAITHFULLY (not paraphrased) from this exact path** (slice-073 sibling-byte-faithfulness lesson): the escape-hatch regex `_SKIP_VALUE_RE = re.compile(r"^skip — rationale: .+")` (em-dash `—`, NOT a hyphen); the `_frontmatter_block` / `_frontmatter_value` helpers; the `_resolve_mode` ladder (`architecture/triage.md` frontmatter `mode:` regex `^\*\*Mode\*\*\s*:\s*([A-Za-z]+)` → `CLAUDE.md` `**Mode**:` fallback → `None`/exit 2) with `tools/_vault_paths.VAULT_ROOT` routing (slice-068); the exit-code mapping (usage-kinds → 2, other violations → 1). The build plan includes a `grep -n` sibling byte-faithfulness check across these literals. (NB: the slice-081 /critique M1 premise that design names a nonexistent `tools/crp_audit.py` is inaccurate — this line has always cited the real path; the adopted residue is the verbatim-literal enumeration above.)
- `tools/_stdout.py` `reconfigure_stdout_utf8()` — UTF8-STDOUT-1 conformance.
- The BFRD-1 repro `tests/bugs/test_drift_check_enforcement_gap.py` (shippability row 86) — AC #3 asserts it passes.
- Mode-resolution precedent: `architecture/triage.md` frontmatter `mode:` → `CLAUDE.md` `**Mode**:` fallback.

## Components touched

### `tools/drift_check_audit.py` (new)
- **Responsibility**: enforce that a `/drift-check` was actually run for the active slice before the build can finish — closing the silent-skip gap. Procedural, not semantic.
- **Lives at**: `tools/drift_check_audit.py` (created by this slice).
- **Key interactions**: reads `architecture/drift-log.md` (marker source), the slice folder's `milestone.md` (escape-hatch frontmatter key), `architecture/triage.md` + `CLAUDE.md` (mode resolution). Invoked from `skills/build-slice/SKILL.md` Step 6. No writes (read-only audit).

### `skills/build-slice/SKILL.md` (modified)
- **Responsibility**: the pre-finish gate now invokes the DCE-1 audit after running `/drift-check`.
- **Lives at**: `skills/build-slice/SKILL.md` Step 6 (in-repo); installed copy kept content-equal (mini-CAD / build-slice skill-drift guard — reinstall at build).
- **Key interactions**: calls `tools.drift_check_audit`; ordering — `/drift-check` run BEFORE the audit.

## Contracts added or changed

### CLI: `tools/drift_check_audit.py`
- **Invocation**: `$PY -m tools.drift_check_audit architecture/slices/slice-NNN-<name>` (positional slice-folder argument, mirroring CRP-1).
- **Defined in code at**: `tools/drift_check_audit.py` (to be created); `main()` entry point.
- **Exit-code contract** (mirrors CRP-1):
  - **0** — accept: a `drift-log.md` entry references the current slice number, OR canonical `drift-check-skip:` key present in milestone.md, OR resolved mode == MINIMAL.
  - **1** — refuse: `drift-check-not-run` (mode ∈ {STANDARD, HEAVY} AND no slice-referencing drift-log entry AND no canonical escape-hatch key); OR `escape-hatch-malformed` (`drift-check-skip:` key present but value ≠ `^skip — rationale: .+`).
  - **2** — `usage-error` / `mode-unresolvable`.
- **Marker match (line-anchored + slice-anchored, per /critique B1 + /critique-review M-add-1)**: the audit scans `architecture/drift-log.md` **only on lines beginning `**Trigger**:`** (a line-anchored match — NOT a whole-file substring scan), and on such a line matches the current slice **anchored on the slice number** via `slice[- ]?0*<N>\b` (e.g. `slice[- ]?0*81\b`) — resolving canonical `slice-081`, sloppy `slice81`/`slice 81`, while `\b` + `0*` reject `slice-0810` / `slice-081x`. **The `**Trigger**:`-line anchor is load-bearing (M-add-1)**: drift-log.md is append-only and routinely cross-mentions OTHER slice numbers in `**Scope**` / Notes / Resolutions / `## Audit (slice-NNN …)` heading lines (29 such non-Trigger lines exist today); a bare whole-file scan would **false-ACCEPT** a slice merely *mentioned* by a prior entry (e.g. "deferred to slice-NNN"), silently defeating the gate — the opposite, worse failure direction from M2. This mirrors CRP-1's keyed-not-substring discipline (ADR-024, which keys on the frontmatter *key* precisely to kill the BRANCH-1 narrative-prose false-positive class). Slice numbers are globally unique → the slice number IS the freshness key; no timestamp logic. APED-1 (build): execute the matcher against (i) a `**Trigger**: slice-081 pre-finish gate` line → accept; (ii) `slice81`/`sliceNN` Trigger forms; (iii) `slice-0810` → reject; **(iv) a drift-log where `slice-081` appears ONLY in a prior entry's Notes/Scope/heading with NO `**Trigger**: slice-081` line → MUST exit 1 (the M-add-1 negative fixture)**; quote observed output. (The producer template is ALSO canonicalized to `slice-NNN` — see the B1 bullet in "What's new" — so producer and consumer agree.)
- **Auth model**: n/a (local CLI audit).
- **Error cases**: missing slice folder / unparseable `milestone.md` → exit 2 usage-error (NOT a false refuse — fail-visible, per the **ADR-037 / STP-1 / BCI-1 "skip-with-note / fail-visible over false-FAIL"** lineage; corrected from the slice-081 /critique m2 mis-citation of PTFFD-1, which is the unrelated phantom-test-function-citation rule).

## Data model deltas

None. The escape-hatch is a `drift-check-skip:` key in the existing `milestone.md` frontmatter (additive, mirrors `critique-review-skip:`). No new files beyond the tool + its tests.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/drift_check_audit.py` | `skills/build-slice/SKILL.md` Step 6 (`$PY -m tools.drift_check_audit …`) | `tests/methodology/test_drift_check_audit.py::test_refuses_when_drift_check_not_run` + `tests/bugs/test_drift_check_enforcement_gap.py::test_drift_check_audit_wired_into_build_slice_step6` | — |
| `tests/methodology/test_drift_check_audit.py` | — | — | `test module — exercised directly by pytest, no runtime consumer demanded — rationale: audit unit tests` |

## Decisions made (ADRs)
- [[ADR-073]] — mint DCE-1: enforce `/drift-check`-was-run as an audit gate at `/build-slice` Step 6, procedural (CRP-1 pattern), not semantic — reversibility: **cheap**.

## Authorization model for this slice
n/a — local CLI audit tool; no auth surface.

## Error model for this slice
- `drift-check-not-run` (exit 1) — the gate's purpose; emitted when the slice has no drift-log marker and no escape-hatch.
- `escape-hatch-malformed` (exit 1) — `drift-check-skip:` present but off-canonical (prevents a sloppy skip from silently passing).
- `usage-error` / `mode-unresolvable` (exit 2) — bad invocation or unresolvable mode; fail-visible, never a false refuse.

## Bootstrap (slice-081 only)

slice-081 authors DCE-1, so the gate must discharge on its own build. At slice-081's Step 6 the build sequence runs `/drift-check` (writing an entry to `architecture/drift-log.md` that **MUST carry a `**Trigger**: slice-081 pre-finish gate …` line** — per /critique-review m-add-1, the slice token in the `## Audit (slice-081 …)` heading alone is NOT sufficient under the M-add-1 line-anchored matcher) BEFORE invoking `tools.drift_check_audit architecture/slices/slice-081-fix-drift-check-enforcement-gap`, which must then exit 0 (self-application discharge). An explicit APED-1 assertion at build confirms slice-081's actually-written entry exits 0 under the line-anchored matcher. A **non-zero DCE-1 at slice-081's own Step 6 before the drift-check run is the EXPECTED signal to run `/drift-check` first — NOT a slice defect**; re-run until exit 0. Every slice after 081 inherits a self-gating DCE-1. (Same bootstrap shape as CRP-1 slice-026 / PCA-1 slice-027 / NAW-1 slice-063.)
