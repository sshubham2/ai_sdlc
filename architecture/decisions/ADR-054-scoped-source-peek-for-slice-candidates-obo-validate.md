---
id: ADR-054
title: /slice-candidates --obo "Validate then approve" may read ONLY the current finding's cited evidence files — a bounded deviation of slice-candidates Hard rule #2
date: 2026-05-20
slice: slice-052-add-slice-candidates-obo-mode
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-054: Scoped source peek for `/slice-candidates --obo` "Validate then approve"

## Context

`/slice-candidates` Hard rule #2 forbids the skill from reading any source or
documentation file in the analyzed repo — all inputs come from `diagnose-out/`
(`diagnosis.html`, `findings/*.yaml`, `graphify-out/graph.json`). The rule
exists because `/diagnose` already did the code reading; re-reading source from
`/slice-candidates` risks the skill drifting into a second, uncontrolled
analysis pass and breaks its pipeline-agnostic contract.

Slice-052 adds an interactive `--obo` mode whose "Validate then approve" option
must let the owner ask, per finding, "is this finding actually real?" before
confirming it. A meaningful validation verdict cannot be produced from the
finding's prose alone — it needs to confront the finding against the actual
lines of code it cites. The user explicitly chose the thorough option (scoped
source peek) over a graph-only or re-present-only validation when this slice
was scoped.

This is a genuine deviation of Hard rule #2 and therefore requires a written,
append-only decision rather than a judgement call (brownfield rule:
"Deviations need an ADR").

## Options considered

1. **Graph + embedded-evidence only** — validate using `graphify-out/graph.json`
   plus the line-refs already embedded in the finding. Pros: zero Hard-rule-#2
   deviation, no ADR. Cons: the graph is structural, not semantic; it cannot
   confirm whether the *claim* a finding makes about a span of code is true —
   the owner asked for real validation, this would be theatre.
2. **Re-present full finding detail** — render description + rationale + all
   evidence for human eyeballing, no Claude judgement. Pros: no deviation.
   Cons: identical to just reading the HTML — does not reduce the annotation
   friction this slice exists to remove.
3. **Unrestricted source peek** — let "Validate" read anything in the repo.
   Pros: maximally informed. Cons: reintroduces exactly the uncontrolled
   second-analysis-pass risk Hard rule #2 was written to prevent; unbounded
   blast radius.
4. **Scoped source peek (chosen)** — "Validate then approve" may open ONLY the
   files enumerated in the *current finding's* `evidence[].path` set, read the
   cited spans, and produce a real/likely-real/not-real verdict with reasoning,
   then re-offer Approve/Defer/Reject. Pros: enough signal for a genuine
   verdict; blast radius mechanically bounded to files `/diagnose` already
   surfaced for this one finding; opt-in (only the "Validate" choice, only the
   `--obo` flag). Cons: a real, if narrow, Hard-rule-#2 deviation.

## Decision

Adopt option 4. Under `/slice-candidates --obo`, and ONLY when the owner picks
"Validate then approve" for a finding, the source files whose paths appear in
that finding's `evidence` list MAY be read, restricted to confirming or
refuting that finding.

Enforcement is **mechanical, not honour-system**: the read is routed through a
new `build_backlog.py --obo-peek --finding <id> --file <path>` helper
subcommand that (a) resolves the allow-set = `{Path(p).resolve() for p in the
finding's evidence[].path}` from the embedded `diagnose-data` JSON, (b) admits
`<path>` only if `Path(<path>).resolve()` is in that set (so `../`-traversal,
absolute, and `./`-prefixed evasions all normalize and are rejected), and
(c) otherwise exits non-zero and logs the refusal. SKILL.md forbids Claude from
`Read`-ing repo source directly under `--obo`; `--obo-peek` is the only
source-read channel, so the boundary cannot be widened by the conversational
layer. The deviation does NOT apply to the non-`--obo` path, to other findings,
or to writing (Hard rules #1 and #3 — never modify source, never modify
`diagnosis.html` — are untouched).

## Consequences

- `skills/slice-candidates/SKILL.md` gains a documented, bounded carve-out from
  Hard rule #2, scoped to the `--obo` "Validate then approve" branch and to the
  current finding's cited evidence files only. Hard rule #2's general statement
  is amended to reference this ADR rather than being silently contradicted.
- The boundary is enforced mechanically by the `--obo-peek` `Path.resolve()`
  containment gate (not by prose honour-system) — pinned as a must-not-defer
  item and covered by `tests/methodology/test_slice_candidates_obo.py`
  (in-set / `../` / absolute / `./` / unknown-finding cases).
- No new registered artifact: the `--obo` machinery is a flag on the existing
  `/slice-candidates` skill plus new entrypoints in the existing, already-
  registered `build_backlog.py`; PMI-1 / INST-1 surfaces are unaffected.
- `/critique` is mandatory for this slice regardless of risk tier (In-house
  methodology surface + a Hard-rule deviation).

## Reversibility

Tagged **cheap**. The carve-out is gated behind a single opt-in flag and a
single menu choice; the readable-path allow-set is one derived data structure.
Removing the deviation later means deleting the "Validate then approve" branch
(or downgrading it to option 1/2) — a localized change in one skill + one
helper, no data migration, no contract consumers. Nothing downstream of
`build_backlog.py` depends on validation having occurred; it only ever consumed
`confirmed`/`notes`, which are unchanged in shape.
