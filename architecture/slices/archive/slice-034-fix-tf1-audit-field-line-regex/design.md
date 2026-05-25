# Design: Slice 034 fix-tf1-audit-field-line-regex

**Date**: 2026-05-17
**Mode**: Standard

## What's new

- A relaxed field-line value match in `tools/test_first_audit.py` so an annotated `**Test-first**: true  (per TF-1 — …)` line is detected as test-first (closes R-7 silent default-off).
- A new **field-present-but-malformed** detection + a loud `malformed-test-first-field` violation, so a present-but-unparseable field can never silently take the default-off path (the R-7 fix recommendation's "distinguish absent from present-but-broken" half).
- New tests for the absent-stays-clean and malformed-is-loud cases (AC2/AC3) plus an R-7-retired vault assertion (AC5) added to `tests/methodology/test_test_first_audit.py` / the repro module.
- `methodology-changelog.md` v0.48.0 entry under **RULE-ID `TFFL-1`** ("TF-1 Field-Line robustness") + 4-part atomic PMI-1 version bump (behavior change: a brief silently-passed yesterday now engages the gate; a malformed field now HALTs loudly). **RULE-ID disposition (per /critique-review M-add-1)**: `TFFL-1` is minted as a NEW rule-ID that *refines TF-1 (slice-002) in place* — rule-ID lineage preserved, **supersedes nothing** — following the documented EOL-DRIFT-1↔CAD-1 / PMI-1 v1.0→v1.1 in-place-refinement precedent (methodology-changelog.md:45). The entry body carries the canonical invariant phrase `**Test-first** field-line value must be a standalone boolean token` (N-surface schema-pin precedent). A bound entry-pin test `tests/methodology/test_methodology_changelog.py::test_v_0_48_0_tffl_1_entry_present_in_repo_and_installed` asserts the rule token + canonical phrase + ADR-034 lineage in BOTH the in-repo and installed changelog surfaces (the 28-function v0.22.0→v0.47.0 precedent).
- `architecture/risk-register.md` R-7 escalated to `retired`.
- ADR-034 (fix strategy).

## What's reused

- `tools/test_first_audit.py` — `_TEST_FIRST_FIELD_RE` (`tools/test_first_audit.py:54`), `_detect_test_first_flag` (L138–144), `run_audit` default-off path (L289), `_format_human` (L443–444), the existing `TestFirstViolation` dataclass + `severity="Important"` convention (cf. `missing-section` at L294–299).
- Repro: `tests/methodology/test_tf1_field_line_annotation_regression.py` (BFRD-1 prerequisite; [[shippability]] row #34).
- [[risk-register#R-7]] — retired by this slice.
- Prior context: [[slice-031-complete-shippability-decoupling]], [[slice-033-fix-skill-drift-test-crlf-normalization]] (R-7 discovery + N+1; bare-field-line remedy; BC-PROJ-4 backstop).
- Self-hosting discipline: CAD-1 / PMI-1 / INST-1 (no tool-list change → INST-1 lockstep only; no `agents/*.md` or guarded `SKILL.md` touched → CAD-1/mini-CAD unaffected).

## Components touched

### `tools/test_first_audit.py` (modified)
- **Responsibility**: TF-1 audit — detect the opt-in `**Test-first**` field and, when enabled, enforce the test-first plan table. WHY: the gate that refuses non-PASSING test-first rows at `/build-slice` Step 6.
- **Lives at**: `tools/test_first_audit.py`
- **Key interactions**: consumed by `/build-slice` Step 6 (`--strict-pre-finish`), `/slice` + `/build-slice` skill prose pins, `tests/methodology/test_test_first_audit.py`, the repro module, shippability rows. No new module — pure in-file change.

**Change shape (HOW):**

1. **Value-match relaxation (fixes AC1/AC2; tightened per /critique M1).** The detector must accept an optional trailing annotation after the boolean, but the boolean MUST be a **standalone token** — NOT an arbitrary `\b`. `(true|false)\b.*$` was rejected: `\b` matches between `false` and `-`, so `**Test-first**: false-positive` → captured `false`, `**Test-first**: true.` → `true`, `**Test-first**: false; note` → `false` — these malformed *suffix* values would be silently accepted as valid booleans, re-introducing the exact R-7 silent-bypass class this slice exists to close (a self-violation-law instance). Instead, require the captured boolean to be immediately followed by whitespace, an opening `(` (the idiomatic annotation), or end-of-line: `^\*\*Test[-\s]?first\*\*\s*:\s*(true|false)(?=[\s(]|$)` (`re.IGNORECASE`; `re.match` semantics — the annotation remainder need not be consumed). Still `^`-anchored on the `**Test-first**:` bold field token at line start, so mid-sentence prose and the HTML-comment annotation lines (mission-brief.md:7-13) do NOT match. `false-positive` / `true.` / `trueish` / `false-ish` / `false; note` fail the standalone-token lookahead and fall through to the §2 malformed branch (NOT silently accepted). `_detect_test_first_flag` keeps its `bool` return contract (the repro asserts `_detect_test_first_flag(...) is True`) — only the regex it consults is tightened-and-widened. Verified empirically: this slice's own bare `**Test-first**: true` (mission-brief.md:6) and the repro's annotated `true  (per TF-1 …)` (two spaces then `(`) both still match; `false-positive` / `true.` now do not.

2. **Field-present-but-malformed branch (fixes AC3).** Add a second, value-agnostic "is the field syntactically present?" matcher (the field prefix `^\*\*Test[-\s]?first\*\*\s*:` regardless of value). In `run_audit`, BEFORE the L289 `return result  # default-off`: if the field prefix is present on some line AND no line satisfies the value matcher → append a `TestFirstViolation(kind="malformed-test-first-field", severity="Important", …)` with an attributed, actionable message (which brief, which line, the offending value, the accepted forms) and do NOT take the silent default-off path. Absent field (no prefix on any line) → unchanged legitimate default-off.

   **Load-bearing invariant (per /critique M2 — do NOT narrow):** the "value matcher" this branch consults is the SAME `(true|false)(?=[\s(]|$)` matcher `_detect_test_first_flag` uses — it captures BOTH booleans. Therefore a legitimately-disabled `**Test-first**: false`-only brief SATISFIES the value matcher and correctly takes the silent default-off path (AC2 non-regression), NOT the malformed branch. The malformed branch fires ONLY when the field prefix is present but NO line yields a valid `true|false` standalone token (empty value, `maybe`, `false-positive`, `true.`, …). An implementation that narrowed this branch's value check to `true`-only would spuriously emit `malformed-test-first-field` on every `**Test-first**: false` brief — explicitly prohibited; pinned by an AC2 test.

3. **Human formatter.** `_format_human` already renders violations generically (L458–465); the new violation kind needs no special-casing. The "not enabled" silent message (L444) is now only reached on genuine absence.

## Contracts added or changed

No HTTP/event contracts. The audit's behavioural contract changes:

- **Before**: annotated field-line → silent default-off, exit 0. Present-but-malformed value → silent default-off, exit 0.
- **After**: annotated `true|false` → engages the gate. Present-but-malformed value → `malformed-test-first-field` violation (non-silent; non-zero on the violation path / surfaced in JSON + human output). Genuinely absent field → unchanged legitimate default-off.

CLI surface (`main`, exit codes, `--json`, `--strict-pre-finish`, `--no-carry-over`) is unchanged — only the equivalence relation for "is this brief test-first" and the malformed handling change.

## Data model deltas

None.

## Wiring matrix

_Zero new modules — this slice is a pure in-file behavior change to existing `tools/test_first_audit.py` (regex + one branch + one formatter guard); consumers (`/build-slice` Step 6, `tests/methodology/test_test_first_audit.py`, repro module, shippability #34) are pre-existing. Per WIRE-1, a zero-row matrix (header + separator only) is clean._

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-034]] — fix R-7 by relaxing the field-line value match (accept trailing annotation) AND adding a loud `malformed-test-first-field` branch so a present-but-broken field cannot silently default-off — reversibility: cheap.

## Authorization model for this slice

N/A — local audit tool; no auth surface.

## Error model for this slice

- New violation kind `malformed-test-first-field` (severity **Important**, consistent with the existing `missing-section` precedent at L294–299). Message MUST be attributed and actionable: brief path, line number, the offending raw value, and the accepted forms (`**Test-first**: true | false`, optionally annotated). It MUST surface through both `--json` (`result.to_dict()`) and `_format_human`, and MUST NOT be reachable via the silent default-off return.
- No new exceptions/stack traces — malformed input is a structured violation, not a crash (must-not-defer "loud, attributed, not a bare trace").
