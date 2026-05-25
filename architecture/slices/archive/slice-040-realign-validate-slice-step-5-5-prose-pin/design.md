# Design: Slice 040 realign-validate-slice-step-5-5-prose-pin

**Date**: 2026-05-18
**Mode**: Standard

## What's new

- A **realigned assertion + docstring** in the existing test function
  `tests/methodology/test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command`.
  The dead slice-031 prose anchor `"Run each entry's **Machine-cmd** column"` is replaced
  with two SRSC-1-exclusive anchors that pin the runner-invocation wording slice-038 actually
  shipped. The function name and the two still-valid sibling assertions are kept (see below).
- `architecture/risk-register.md` R-10 status flipped `open → retired`, recorded as a
  `**Retired**:` line mirroring the R-9 L170 conformance-fix form, carrying the verification
  evidence + the `/critic-calibrate` N=1 watch-list note.

**No `methodology-changelog.md` entry** (corrected post-/critique M1+M2). The cited
conformance-fix precedent slice-036 (R-9, no VERSION bump) added **no changelog entry at
all** — it recorded retirement in `risk-register.md` (L170 `**Retired**:` line) + ADR-036,
verified by `grep "slice-036\|R-9\|ADR-036" methodology-changelog.md` → 0 real matches.
The methodology-changelog's only `### ` headings are `### Added` (47×) / `### Changed` (6×),
both nested **under `## vN.N.N — date` version headings**; `### Fixed` exists nowhere. A
no-VERSION-bump fix has no `## v` parent to nest under, and `test_each_changelog_entry_carries_rule_reference`
(META-1) splits the file on `^## v\S+ — date` — a parentless `###` entry is either invisible
to META-1 or pollutes slice-039's `## v0.52.0` APED-1/MEPD-1 block. So the M1 fix is to
**drop the changelog entry entirely**, not re-head it; M2's `Rule reference` obligation is
thereby moot (no entry → nothing META-1 parses). The SCMD-1→SRSC-1 lineage M2 wanted captured
lives in the realigned test docstring (AC3) + the R-10 `**Retired**:` line.

No new modules, no new contracts, no data-model delta, no skill/agent/tool/changelog prose
change, no new rule-ID, no ADR, no VERSION bump (conformance-fix class — slice-036 / R-9
precedent: a stale test realigned to already-shipped prose changes no rule and warrants no
changelog touch, so PMI-1 + META-1 stay clean at 0.52.0).

## What's reused

- `skills/validate-slice/SKILL.md` Step 5.5 (L213–219) — the SRSC-1 runner-invocation prose
  shipped by [[slice-038-pin-shippability-runner-segment-contract]] ([[ADR-039]]). **Read, not
  modified** — it is already SRSC-1-correct; the bug is the test pinned the *old* phrase.
- `tests/methodology/conftest.py::read_file` — raw `utf-8` read (no CRLF normalization). The
  assertions are plain substring checks; anchors are chosen to be EOL-insensitive (no embedded
  newline in any pinned substring), so EOL-DRIFT-1 ([[slice-033...]]) is a non-issue here.
- SCMD-1 (`_segments()`) and `tools/shippability_runner.py` — referenced by the pinned prose;
  untouched by this slice (slice-038 already pins them, 39/39 PASS on the real catalog).

## Components touched

### `tests/methodology/test_validate_slice_skill.py` (modified)
- **Responsibility**: pins load-bearing prose in `skills/validate-slice/SKILL.md` so a silent
  prose regression is caught by the methodology suite (mini-CAD discipline for skill prose).
- **Lives at**: `tests/methodology/test_validate_slice_skill.py` (modify ONE function only:
  `test_step4_5_5_consumes_machine_stable_command`, L40–58; the other 3 tests are untouched and
  currently pass).
- **Key interactions**: reads `skills/validate-slice/SKILL.md` via `conftest.read_file`; run by
  the full `tests/methodology/` suite at every `/validate-slice` Step 5 and the BC-PROJ-4
  pre-finish full-suite run (the backstop that surfaced R-10).

### Realignment specifics (the HOW, pinned so /critique can attack it)

Current assertions (L51–58):
1. `assert "Run each entry's **Machine-cmd** column" in VALIDATE` ← **DEAD** (slice-038 removed
   this exact slice-031 phrase). **This is the realignment target.**
2. `assert "tools.shippability_decoupling_audit" in VALIDATE` ← still valid (SCMD-1 pre-catalog
   gate, SKILL.md L205). **Keep verbatim.**
3. `assert "every row's **Machine-cmd** cell resolves" in VALIDATE` ← still valid (PTFCD-1 gate,
   SKILL.md L212). **Keep verbatim.**

Replace assertion #1 with two SRSC-1-exclusive anchors (both absent from the pre-SRSC-1 Step 5.5,
so the pin stays non-tautological per mission-brief AC2 / Must-not-defer):

- `assert "$PY -m tools.shippability_runner architecture/shippability.md" in VALIDATE` — the
  literal invoked-runner command (SKILL.md L216). A regression to the pre-SRSC-1 hand-rolled
  loop removes this exact line → the pin FAILs, as required.
- `assert "canonical pinned runner" in VALIDATE` — the SRSC-1 contract noun-phrase (SKILL.md
  L213), tying the pin to [[ADR-039]] and guarding the "do NOT hand-roll" invariant, not merely
  "some command is present".

Docstring rewrite: state the slice-031 SCMD-1 B2-v1 pin was **superseded by SRSC-1**
([[ADR-039]]; slice-038) — Step 5.5 no longer says "Run each entry's Machine-cmd column"; it
INVOKES `tools.shippability_runner`, which itself reuses SCMD-1 `_segments()`. The pin still
guards the same invariant (Step 5.5 must not hand-roll the catalog execution loop) at the new
prose. Reference R-10 + ADR-039 in the docstring so the realignment is auditable, not silent.

**Function NOT renamed**: `test_step4_5_5_consumes_machine_stable_command` stays accurate —
under SRSC-1 the runner still consumes each row's Machine-cmd cell. Renaming would be gratuitous
churn and risks a shippability-catalog reference break. No such reference exists, cited by the
**disambiguated** grep (m2 fix — the bare substring `test_validate_slice_skill` false-positives
count 1 on `test_validate_slice_layers.py`'s `..._documents_imports_allowlist_...` row, a
different file/function):
`grep -c "test_validate_slice_skill.py" architecture/shippability.md` → **0** AND
`grep -c "test_step4_5_5_consumes_machine_stable_command" architecture/shippability.md` → **0**.
So no SCPD-1 catalog-propagation obligation arises and the no-rename keeps that guaranteed-safe.

## Contracts added or changed

None. No endpoint, event, or interface changes.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new modules** (it modifies one existing test
function and appends to two existing vault files). Zero-row matrix → clean by audit.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

**No new ADR.** Three scoping decisions, all applications of existing project convention
(none a novel decision warranting an ADR):

- **No new `-D` discipline rule** for the "a SKILL.md-repointing slice must supersede its
  mini-CAD prose-pin in the same fix block" class. Evidence is N=1 (slice-038 only); the
  project's N≥2/N≥3 promotion-threshold convention is not met, and the backstop already exists
  (slice-039 BC-PROJ-4 full-suite-on-real-artifact pre-finish run surfaced R-10). The N=1
  `/critic-calibrate` watch-list note is recorded in the **R-10 `**Retired**:` line**
  (`risk-register.md`) and carried into this slice's `reflection.md` "Critic calibration" /
  deferred section — the surfaces `/critic-calibrate` actually mines — **not** a changelog
  entry (m1 fix; there is no changelog entry — see "What's new"). Reversibility: cheap (a
  future slice can codify if N≥2).
- **No methodology-changelog entry** — conformance-fix class. **MEPD-1(b)** (slice-039;
  the directly-governing discipline for this changelog why-none decision class) is discharged
  along branch (b): the why-none is verified against the **actual META-1 enforcing assertion**
  — `test_each_changelog_entry_carries_rule_reference` splits on
  `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` at `tests/methodology/test_methodology_changelog.py:136`,
  so a parentless `###` entry is invisible to / pollutes the v0.52.0 block — **not** on the
  slice-036 precedent alone (the slice-032 false-precedent guard MEPD-1(b) exists to enforce;
  slice-036/R-9 is corroborating, independently verified `grep → 0`, not load-bearing). This
  is the first slice MEPD-1 governs; citing it by name closes the M-add-1 self-hosting gap.
  Reversibility: cheap.
- **No ADR / no VERSION bump / no new rule-ID** — a stale test realigned to already-shipped
  prose changes no rule and locks no code-behavior decision. (slice-036 *did* mint ADR-036,
  but ADR-036 documented a `main()` *logic* change; slice-040 has no logic change — only a
  test-assertion realignment to existing prose — so unlike slice-036 it warrants no ADR.)
  PMI-1 + META-1 stay clean at 0.52.0. Reversibility: cheap.

## Authorization model for this slice

N/A — no runtime surface, no auth-bearing code. Test + vault-doc edits only.

## Error model for this slice

N/A — no new error codes. The realigned assertion's failure message is updated to name the
SRSC-1 anchor it now pins (so a future regression yields a self-explaining failure rather than
the now-misleading "must consume the Machine-cmd column (B2-v1)" message).
