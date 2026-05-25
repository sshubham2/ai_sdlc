# Design: Slice 052 add-slice-candidates-obo-mode

**Date**: 2026-05-20
**Mode**: Standard

## What's new

- A `--obo` flag on `/slice-candidates`, documented as a new section in
  `skills/slice-candidates/SKILL.md`. It defines a **Claude-driven interactive
  review loop** (severity-ordered, one finding at a time, structured-options
  prompt per finding, scoped-peek validation, exit/resume).
- Three new deterministic entrypoints in the **existing** `build_backlog.py`
  (no new registered artifact — see "What's reused"):
  - `--obo-extract --in <dir>`: parse `diagnosis.html`'s embedded
    `diagnose-data` JSON, return findings as a JSON list **severity-sorted**
    (critical → high → medium → low; stable within band by original order),
    each annotated with its current `confirmed`/`notes` and its
    `evidence[].path` allow-set. Resume predicate: a finding is *unreviewed*
    iff its `id` is **absent from `state.annotations`**. **Defer is terminal
    for `--obo` resume** (a Deferred finding is present in `annotations` as
    `confirmed:"defer"`, so resume skips it permanently — by design, AC5);
    the documented reopen path is: re-run `--obo` against the **original**
    `diagnosis.html` (not the annotated copy), or hand-edit the JSON. SKILL.md
    operator guidance MUST state this so Defer is not a silent one-way trap
    (M-add-1). The helper also
    detects a *duplicate* `diagnose-data` block (NEW logic — `re.findall`
    count; the reused `parse_html_state()` is non-greedy and silently takes
    the first, so duplicate detection is NOT inherited — m1).
  - `--obo-write --in <dir> --decisions <decisions.json>`: given a decisions
    map `{finding_id: {confirmed, notes}}`, emit
    `diagnose-out/diagnosis.annotated.html` (operationally parity-correct, see
    "Annotated-copy parity" below — **NOT** browser-output byte-faithful), and
    assert the original `diagnosis.html` SHA-256 is unchanged across the call
    (raises non-zero on mismatch).
  - `--obo-peek --in <dir> --finding <id> --file <path>`: resolve the
    `evidence[].path` allow-set for `<id>` from the embedded JSON; if
    `Path(<path>).resolve()` is contained in the resolved allow-set, print the
    file's contents; else exit non-zero with a logged `out-of-scope` refusal.
    This is the **sole** source-read channel for "Validate then approve" —
    makes the ADR-054 boundary *mechanical*, not prompt-level (M4).
- `architecture/decisions/ADR-054-*` — the bounded Hard-rule-#2 deviation for
  "Validate then approve".
- A risk-register sub-entry recording the controlled Hard-rule-#2 relaxation.
- **methodology v0.60.0 4-part PMI-1 bump** (build-discovered design correction
  — see "Design deviation" note below): `methodology-changelog.md` `## v0.60.0`
  entry + `VERSION` + `plugin.yaml` version + forward-synced installed
  `~/.claude/ai-sdlc-VERSION` & `~/.claude/methodology-changelog.md`, plus the
  conventional `test_v_0_60_0_obo_*` entry-pin + shippability-consumer-prop
  tests (v0.56–0.59 shape). The mission-brief/earlier-design claim "plugin-
  manifest / drift posture unaffected" was correct only for PMI-1 *artifact
  enumeration* (no new registered skill/agent/tool); it wrongly implied no
  version bump. ADR-054 + a new skill mode is a methodology-surface behavior
  change → the changelog Inclusion heuristic + the slice-049/ADR-051 law
  require the `## vN` + 4-part bump. Both Critic layers missed this (recorded
  for the reflection "Missed by Critic" calibration).

## What's reused

- `skills/slice-candidates/build_backlog.py` — its `parse_html_state()` is the
  canonical embedded-JSON reader; the new `--obo-write` reuses the **exact**
  serialization the browser uses (see "Annotated-copy parity" below). Its
  DAG / priority / topo-sort code is **untouched** (mission brief out-of-scope).
- `skills/diagnose/assemble.py` `save-btn` handler (L1705-1727) and `collect()`
  (L1635-1646) — the source of truth for what a saved annotated file is. The
  `--obo-write` parity contract is derived from these, not invented.
- `AskUserQuestion` tool — the per-finding structured-options prompt (Ask
  discipline / SOAD-1: never a bare free-text prompt).
- `/diagnose` embedded-state schema: `state.findings[]` (each has `id`,
  `title`, `severity`, `description`, `suggested_action`, `evidence[]{path,
  lines,note}`, …) and `state.annotations{ id: {confirmed, notes} }`.
- ADR-054 (this slice) — governs the scoped source peek.

## Components touched

### `/slice-candidates` skill — `--obo` interactive mode (SKILL.md)

- **Responsibility**: when invoked with `--obo`, walk confirmed-or-not findings
  one at a time in severity order and let the owner dispose each
  (Approve / Validate-then-approve / Defer / Reject-with-reason / Exit) with
  live progress, then bake the decisions into a faithful annotated HTML copy —
  removing the read-the-whole-HTML annotation friction without changing the
  downstream backlog contract.
- **Lives at**: `skills/slice-candidates/SKILL.md` (modified — new "`--obo`
  interactive review" section; Hard rule #2 amended to reference ADR-054).
- **Key interactions**: drives `build_backlog.py --obo-extract`,
  `--obo-write`, and (for "Validate then approve") `--obo-peek`; calls
  `AskUserQuestion` per finding; MUST NOT `Read` repo source directly under
  `--obo` (the ADR-054 scoped peek is mechanically gated by `--obo-peek`);
  after exit/last-finding optionally continues to the normal Step 2
  `build_backlog.py` run on the annotated copy.

### `build_backlog.py` — `--obo-extract` / `--obo-write` / `--obo-peek`

- **Responsibility**: the deterministic, non-conversational halves of `--obo` —
  severity-sorted extraction, operationally-parity-correct annotated-copy
  emission with an original-file-immutability assertion, and the mechanically
  bounded source-peek gate. Conversation (the loop, the prompts, the verdict)
  stays in the skill/Claude layer because Python cannot call `AskUserQuestion`.
- **Lives at**: `skills/slice-candidates/build_backlog.py` (modified — add an
  `argparse` subcommand/flag layer; existing default `--in` behaviour and the
  DAG/priority/render code are unchanged and covered by a regression check).
- **Key interactions**: reads `diagnose-out/diagnosis.html`; writes
  `diagnose-out/diagnosis.annotated.html`. `--obo-peek` DOES read repo source
  — but **only** a path it has verified is inside the current finding's
  resolved evidence allow-set (this is the mechanical realization of ADR-054;
  it is the only place in this skill that reads repo source, gated by a
  `Path.resolve()` containment check). `--obo-extract`/`--obo-write` never read
  repo source.

## Contracts added or changed

No network/event/endpoint contracts. Two internal CLI contracts on
`build_backlog.py` (consumed only by the `/slice-candidates` skill prose):

- `--obo-extract --in <dir>` → stdout JSON:
  `{"findings": [{"id","title","severity","description","suggested_action",
  "evidence":[{path,lines,note}], "current": {confirmed,notes},
  "evidence_paths": [<allow-set>]}], "total": N, "reviewed": M}`. Severity order
  is fixed (`critical,high,medium,low`); stable within band.
- `--obo-write --in <dir> --decisions <path>`: `decisions.json` is
  `{finding_id: {"confirmed": "yes|no|defer|", "notes": "<str>"}}`. Entries
  with both `confirmed` and `notes` empty are dropped (matches `collect()`
  L1643). Writes `diagnosis.annotated.html`; exits non-zero if the original
  `diagnosis.html` content hash changed or if inputs are missing/malformed.
- `--obo-peek --in <dir> --finding <id> --file <path>`: stdout = file contents
  iff `Path(path).resolve()` ∈ `{Path(p).resolve() for p in evidence_paths(id)}`
  (resolved relative to the analyzed-repo root, which is the CWD `--obo` is run
  from — `/diagnose` records repo-relative paths, `build_backlog.py` L117);
  else exit non-zero, stderr `out-of-scope: <path> not in finding <id> evidence
  allow-set`, and append a one-line refusal to a run log. Unknown `<id>` →
  non-zero. The containment check normalizes `../`, absolute, and `./`-prefixed
  inputs via `resolve()` before the membership test.
- **Auth model**: N/A (local CLI helper). The only access-scoping primitive is
  the `--obo-peek` allow-set (M4 / ADR-054) — mechanical, not honour-system.
- **Error cases**: missing `diagnosis.html`, absent/**duplicate**
  `diagnose-data` script block (duplicate = NEW `re.findall`-count check, not
  inherited from `parse_html_state()` — m1), malformed embedded JSON, zero
  findings, unknown finding id (in decisions or `--obo-peek`), out-of-scope
  peek path, original-hash mismatch → each exits non-zero with the specific
  reason and writes **no** partial annotated file.

### Annotated-copy parity (must-not-defer #5 — the load-bearing contract)

**Parity is defined operationally, not as browser-output byte-equality.** The
browser "Save annotated HTML" does `'<!DOCTYPE html>\n' +
document.documentElement.outerHTML` (`assemble.py` L1712) — a full DOM
re-serialization the engine normalizes (attribute quoting/order, whitespace,
entity reencoding). That is **unreproducible from Python and irrelevant**: the
only consumer, `parse_html_state()` (`build_backlog.py` L42-63), reads *only*
the `diagnose-data` script block. So the testable invariant is:

> `parse_html_state(diagnosis.annotated.html)["annotations"]` equals the
> decisions map under `collect()` semantics, AND `build_backlog.py --in` on the
> annotated copy yields a `backlog.md` **byte-identical** to a manual browser
> round-trip with the same decisions.

`--obo-write` implementation (the "substitute only the script block" strategy
is correct — it is the prior *spec wording* "byte-faithful to browser" that was
wrong, B2):

1. Read original `diagnosis.html` text; capture SHA-256.
2. Extract the `<script type="application/json" id="diagnose-data">…</script>`
   block via the same regex `parse_html_state()` uses; parse to `data`.
3. Set `data["annotations"] = collected`, where `collected` keeps only finding
   ids whose decision has non-empty `confirmed` **or** `notes` (mirrors
   `collect()` L1643). Unreviewed findings are **absent** from the map (NOT
   written as `{confirmed:"",notes:""}`) — AC5 resume semantics + M1.
   `annotations` **key order is NOT part of the parity contract**:
   `confirmed_findings()` iterates `annotations.items()` and `build_backlog.py`
   re-sorts (L91-108, L240-311), so the Builder must NOT waste effort matching
   the browser's DOM (severity-grouped) key order — only the key *set* and each
   `{confirmed,notes}` *value* matter.
4. Serialize: `json.dumps(data, indent=2, ensure_ascii=False)` then
   `.replace("</", "<\\/")`. **`ensure_ascii=False` is mandatory** (B1):
   Python's default `ensure_ascii=True` emits `\uXXXX`, but the browser
   `JSON.stringify` (L1709) emits raw UTF-8, and `/diagnose` output routinely
   carries non-ASCII (`assemble.py` L2130 embeds `💡`; descriptions carry smart
   quotes / accented identifiers). The `.replace` mirrors L1709's
   `.replace(/<\//g, '<\\/')` — it maps the two characters `<` `/` to `<` `\`
   `/` (single backslash); the Builder MUST NOT emit a double backslash.
5. Substitute **only** that script block's inner text back into the otherwise
   unchanged original HTML string **by match-span string slicing**, NOT
   `re.sub` (M-add-2): with `m` the `re.search` match used in step 2, write
   `text[:m.start(1)] + new_inner + text[m.end(1):]`. `re.sub`/`re.Match.expand`
   with the JSON payload as the *replacement* would corrupt it — Python treats
   `\g<…>`, `\1`, and bare backslashes in a replacement string specially, and
   the payload legitimately contains `<\/` plus arbitrary `\uXXXX`/backslash
   sequences from finding text. Slice insertion is byte-exact and escape-free.
   Write to `diagnosis.annotated.html`.
6. Re-hash the original `diagnosis.html`; assert equal to step-1 hash; abort
   non-zero on mismatch (Hard-rule-#3 invariant, mechanical not prose).

`json.loads` decodes `\uXXXX` and raw UTF-8 identically, so a wrong
`ensure_ascii` would still parse — the divergence is *silent* (exactly the
must-not-defer #5 failure). The golden regression test (see "Test plan") pins
it with a non-ASCII fixture; `backlog.md` byte-equality is the assertion, not
annotated-HTML byte-equality.

## Test plan (M3 — deterministic helper regression; conversational loop stays manual)

`**Test-first**: false` is retained for the `AskUserQuestion` loop only
(Python cannot drive it). The deterministic helpers carry a mandatory
build-time golden test `tests/methodology/test_slice_candidates_obo.py`:

- **Fixture**: a checked-in `diagnose-out/` whose findings span ≥2 severities
  and include non-ASCII text (emoji + accented char) in a description + a note.
- **`--obo-write`**: given a known decisions map (Approve / Reject+notes /
  Defer / one untouched) → assert (a) original `diagnosis.html` SHA-256
  unchanged, (b) `parse_html_state(annotated)["annotations"]` == expected
  (untouched finding absent), (c) `build_backlog.py --in` output byte-equal to
  a checked-in `backlog.golden.md` produced from a manual browser round-trip.
  **At least one decision's `notes` MUST contain a literal backslash AND a
  `</` sequence** (M-add-2) — pins that step-5 insertion is match-span slicing,
  not `re.sub` (a `re.sub` impl corrupts `\`/`</` and fails this case).
- **`--obo-peek`**: in-set path → contents; `../`-traversal, absolute, and
  `./`-prefixed out-of-set paths → non-zero + logged refusal; unknown finding
  → non-zero.
- **`--obo-extract`**: severity order critical→high→medium→low stable; resume
  predicate = `id ∉ annotations`; duplicate `diagnose-data` block → non-zero.
- **Default path regression**: `build_backlog.py --in` (no `--obo*`) on the
  fixture → output unchanged vs a pre-slice golden (proves the argparse
  refactor didn't disturb the DAG/render path).

## Data model deltas

None persistent. `decisions.json` is an ephemeral hand-off between the Claude
loop and `--obo-write`, created via `tempfile.mkstemp()` (unique name — no
fixed-name collision between concurrent `--obo` runs on different
`diagnose-out/` dirs, m2) and deleted in a `finally` regardless of
success/failure. Never written into `diagnose-out/`.

## Wiring matrix

Per WIRE-1. The only **new file** is the build-time regression test (M3); the
`--obo-*` entrypoints live inside the already-consumed `build_backlog.py` and
the loop is prose in the already-consumed `SKILL.md`. A test file is its own
consumer (collected by the methodology pytest suite); no registered-artifact
change (PMI-1 / INST-1 enumerate skills/agents/tools, not `tests/methodology/`
files — unaffected).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_slice_candidates_obo.py` | — | (is itself the test) | `rationale: regression/golden test for the --obo helpers; collected by the methodology pytest suite — it IS the consumer test, no further consumer demanded` |

## OSDG-1 / mini-CAD decision (must-not-defer #6)

`skills/slice-candidates/SKILL.md` is **NOT** added to the OSDG-1 / mini-CAD
in-repo↔installed content-equality guarded set in this slice. Rationale:
project precedent (slice-049) treats drift-guard *addition* as its own
dedicated slice with its own Critic pass — folding a new
`test_slice_candidates_skill_drift.py` into a feature slice would be a
"while I'm here" scope creep the brownfield rules forbid. The exposure (in-repo
SKILL.md edited here but installed copy not yet guarded) is real but identical
in class to every pre-OSDG-1 skill.

**The nomination must be physically written, not asserted** (m3 / slice-050
lesson — never treat "self-run sufficient" as written). `/build-slice` adds a
`risk-register.md` sub-entry "extend OSDG-1 drift guard to `/slice-candidates`"
(status: open, next-slice candidate) AND records it in this slice's
`reflection.md` "Discovered" section; pre-finish greps risk-register.md to
verify the line exists. This is a deliberate, logged exclusion — not an
oversight. (Note: this slice DOES still update the installed
`~/.claude/skills/slice-candidates/SKILL.md` + `build_backlog.py` in lock-step
during build per the brownfield self-hosting discipline; only the *automated
guard* is deferred, not the sync itself.)

## Decisions made (ADRs)

- [[ADR-054]] — `/slice-candidates --obo` "Validate then approve" may read ONLY
  the current finding's `evidence[].path` files; bounded deviation of
  slice-candidates Hard rule #2 — reversibility: **cheap**

## Authorization model for this slice

N/A — local single-user CLI/skill. The only access-scoping concept introduced
is the ADR-054 read allow-set (per-finding evidence paths). It is enforced
**mechanically inside `--obo-peek`** (a `Path.resolve()` containment check that
refuses + logs out-of-set paths), NOT by a SKILL.md instruction asking Claude
to self-restrict. SKILL.md additionally forbids Claude from `Read`-ing repo
source directly under `--obo` — `--obo-peek` is the only source-read channel,
so the boundary cannot be bypassed by the conversational layer (M4).

## Error model for this slice

No new error *codes* (CLI helper, non-zero exit + stderr reason). Failure
classes, all fail-closed (no partial/corrupt annotated file):

- Input absent/malformed (`diagnosis.html` missing, no/duplicate
  `diagnose-data` block, bad JSON, zero findings) → stop, specific reason.
- Decisions reference an unknown finding id → stop, name the id.
- Original-hash mismatch after write → stop (Hard-rule-#3 breach signal).
- Scoped-peek boundary violation (`--obo-peek` given a path that fails the
  `Path.resolve()` containment check, incl. `../`/absolute/`./` variants) →
  helper exits non-zero + logs; the loop continues (the finding can still be
  Approved/Deferred/Rejected without the peek).
- User picks **Exit** mid-stream → not an error: persist decisions-so-far,
  report remaining-unreviewed count, resume-on-rerun.
