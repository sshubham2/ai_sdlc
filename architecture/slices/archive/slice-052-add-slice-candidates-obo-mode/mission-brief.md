# Slice 052: add-slice-candidates-obo-mode

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: New — annotation-friction risk: the manual `diagnosis.html` round-trip (open HTML, eyeball every finding, fill `Confirmed`/`Notes`, click Save, mail back) is high-friction for large diagnoses, so owners skip findings or abandon the round-trip, starving `/slice-candidates` of confirmed input. Adds a risk-register sub-entry for the controlled Hard-rule-#2 relaxation (scoped source peek).
**Test-first**: false  (conversational `AskUserQuestion` loop only — the deterministic `--obo-extract`/`--obo-write`/`--obo-peek` helpers carry a mandatory build-time golden regression test per M3 below)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Add an `--obo` ("on behalf of") interactive mode to `/slice-candidates`. Instead of forcing the owner to read the whole `diagnosis.html` and hand-annotate every finding, `--obo` walks findings one at a time — severity-ordered — and lets the owner decide each via structured options (Approve / Validate-then-approve / Defer / Reject-with-reason / Exit), showing live progress. On exit it bakes those decisions into a `diagnosis.annotated.html` copy whose embedded `diagnose-data` JSON carries the same annotations the in-browser "Save annotated HTML" would have, so the existing `build_backlog.py` consumes it and produces a byte-identical `backlog.md` (parity is operational — `backlog.md` + `parse_html_state` equality — NOT browser-output byte-equality; see AC4). Ships now because annotation friction is the single biggest leak between `/diagnose` and `/slice-candidates`.

## Acceptance criteria

1. `/slice-candidates --obo [path]` enters an interactive loop: parses the embedded `diagnose-data` JSON, orders findings by severity (high → medium → low, stable within band), and presents exactly one finding at a time; non-`--obo` invocation behaviour is byte-for-byte unchanged.
2. Each prompt shows live progress (total findings, # reviewed, and per-disposition counts: approved / deferred / rejected) and offers structured options via `AskUserQuestion`: **Approve**, **Validate then approve**, **Defer**, **Reject** (captures a free-text "why"), and **Exit**.
3. **Validate then approve** performs a *scoped source peek* routed through a new `build_backlog.py --obo-peek --finding <id> --file <path>` helper subcommand that mechanically resolves the current finding's `evidence[].path` allow-set and refuses (non-zero, logged) any out-of-set path via a `Path.resolve()` containment check (per ADR-054 deviating Hard rule #2); Claude reads source only through that helper, presents a real/likely/not-real verdict with reasoning, then re-offers Approve/Defer/Reject for that finding.
4. On Exit or after the last finding, `--obo` writes `diagnose-out/diagnosis.annotated.html` (decisions baked into the embedded `diagnose-data` JSON, `confirmed` ∈ yes|no|defer|"" + `notes`, only findings with non-empty confirmed-or-notes present — `collect()` semantics); the original `diagnosis.html` is byte-unchanged (pre/post SHA-256 asserted). **Parity is defined operationally, NOT as browser-output byte-equality** (the browser save is a full `outerHTML` re-render, unreproducible and irrelevant): `parse_html_state(diagnosis.annotated.html)` yields an `annotations` map equal to the decisions under `collect()` semantics, AND `build_backlog.py --in` on the annotated copy produces a `backlog.md` **byte-identical** to a manual browser round-trip with the same decisions.
5. Mid-way Exit persists decisions made so far into the annotated copy; unreviewed findings are **absent** from the `annotations` map (NOT written as empty `{confirmed:"",notes:""}` entries — mirrors `collect()`'s `if (conf||notes)` gate). The exit report distinguishes never-reached vs Deferred counts. Re-running `--obo` on the annotated copy resumes at the first finding whose `id` is absent from `annotations`; Deferred findings (`confirmed:"defer"`, present in the map) are NOT re-offered on resume. Defer is terminal for resume by design — the documented reopen path (re-run `--obo` on the original `diagnosis.html`, or hand-edit the JSON) MUST be stated in SKILL.md operator guidance so it is not a silent one-way trap.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Interactive loop + severity order + default unchanged | Run `--obo` on a fixture `diagnose-out/` with mixed-severity findings; observe high→medium→low presentation order. Run `/slice-candidates` (no flag) on same fixture; diff `backlog.md` against pre-slice golden → identical. |
| 2 | Progress + structured options | Inspect each prompt: shows `Finding k of N · A approved · D deferred · R rejected`; the `AskUserQuestion` call carries all five options; Reject path captures and stores the typed reason. |
| 3 | Scoped source peek mechanically bounded | `tests/methodology/test_slice_candidates_obo.py` drives `build_backlog.py --obo-peek` for an in-set evidence path (returns content) and an out-of-set path incl. `../` traversal + absolute + `./`-prefixed variants (refused non-zero, logged). ADR-054 exists, append-only, references Hard rule #2. |
| 4 | Annotated copy operational parity + original untouched | Golden test: `Get-FileHash diagnosis.html` before/after `--obo-write` → equal. `parse_html_state(diagnosis.annotated.html)` annotations == expected decisions map. `build_backlog.py --in diagnose-out` on the copy → `backlog.md` **byte-identical** to a checked-in golden produced by a manual browser round-trip with the same decisions. Fixture finding text contains non-ASCII (emoji + accent) to pin the `ensure_ascii=False` requirement. |
| 5 | Mid-way Exit / resume predicate | Approve 1, Reject 1, Defer 1, Exit before the rest; assert annotated copy `annotations` has exactly those 3 keys (unreviewed absent, not empty entries); report distinguishes never-reached vs deferred. Re-run `--obo-extract` on the copy → first finding with `id ∉ annotations` is the resume point; the deferred finding is not re-offered. |

## Must-not-defer

- [ ] **Hard-rule-#3 invariant**: original `diagnosis.html` byte-identical pre/post (hash assertion in the helper, not just prose).
- [ ] **Input validation**: missing `diagnosis.html` / no `diagnose-data` script / malformed JSON / zero findings → explicit stop with the specific reason; never emit a partial or corrupt annotated copy.
- [ ] **Scoped-peek boundary enforcement — mechanical, not honour-system**: source reads for "Validate then approve" go through the `--obo-peek` helper which resolves the allow-set from the embedded JSON and refuses out-of-set paths via `Path.resolve()` containment (handles `../`, absolute, `./`-prefixed). SKILL.md MUST forbid Claude from `Read`-ing repo source directly in `--obo` — the helper is the only source-read channel.
- [ ] **ADR for the Hard-rule-#2 deviation**: append-only, new ADR ID (ADR-054), states scope (evidence-files-of-current-finding only), rationale, and the *mechanical* enforcement mechanism (`--obo-peek` containment check). No silent rule break.
- [ ] **Annotated-JSON serialization parity**: `--obo-write` MUST use `json.dumps(data, indent=2, ensure_ascii=False)` then `.replace("</", "<\\/")` so non-ASCII findings (emoji/accents — `/diagnose` emits these routinely, e.g. `assemble.py` L2130 `💡`) match the browser `JSON.stringify` control. Operational parity target is `backlog.md` byte-equality + `parse_html_state` annotation equality — NOT annotated-HTML byte-equality (browser save is a full `outerHTML` re-render, unreproducible from Python and not required by the only consumer).
- [ ] **OSDG-1 / mini-CAD decision + nomination actually written**: `slice-candidates/SKILL.md` is deliberately NOT added to the OSDG-1 guarded set this slice (slice-049/051 own-slice precedent). The "extend OSDG-1 to /slice-candidates" Discovered next-slice nomination MUST be physically written to the Discovered-nominations surface during build and verified at pre-finish — not merely asserted in design.md (slice-050 lesson: never treat "self-run sufficient" as written).
- [ ] Logging at the decision-capture and annotated-write critical paths.

## Out of scope

- Changing `build_backlog.py`'s DAG / priority / topo-sort algorithm — `--obo` only produces the annotated input it already consumes.
- Adding `--obo` to any skill other than `/slice-candidates`.
- Altering the non-interactive default path's behaviour or output.
- Auto-confirming, batch-approving, or inferring any disposition without explicit per-finding user input.
- Modifying `diagnosis.html` in place, or modifying `findings/*.yaml`.

## Dependencies

- Vault refs: [[skills/slice-candidates/SKILL.md]], [[skills/slice-candidates/build_backlog.py]]
- Embedded-JSON schema produced by [[skills/diagnose/SKILL.md]] ("Save annotated HTML" / `diagnose-data` script block) — source of truth for annotated-copy parity (AC4, must-not-defer #5)
- New ADR (next free ID, ~ADR-054) — append-only deviation of Hard rule #2 for the scoped source peek (AC3)
- Risk register: new sub-entry for the controlled Hard-rule-#2 relaxation
- Methodology surface change → `/critique` mandatory (In-house methodology surfaces trigger); plugin-manifest / drift posture unaffected (no new skill/agent/tool registered — `--obo` is a flag on an existing skill + its existing helper)

## Mid-slice smoke gate

At ~50% of build (interactive loop + annotated-HTML writer exist, scoped peek may be stubbed):
```
# against a small fixture diagnose-out/ with >=2 findings
/slice-candidates --obo diagnose-out      # Approve finding 1, Reject finding 2 (reason "not real"), Exit
Get-FileHash diagnose-out/diagnosis.html  # compare to pre-run hash
$PY skills/slice-candidates/build_backlog.py --in diagnose-out   # on the .annotated.html copy
```
Expected: original hash unchanged; `diagnosis.annotated.html` exists with finding-1 `confirmed=yes`, finding-2 `confirmed=no` + note; `backlog.md` contains only the approved candidate. If original hash changed or annotated schema mis-parses: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (incl. ADR written, scoped-peek bounded, OSDG-1 decision recorded)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Critic blockers addressed (Standard mode + methodology surface → Critic mandatory)
