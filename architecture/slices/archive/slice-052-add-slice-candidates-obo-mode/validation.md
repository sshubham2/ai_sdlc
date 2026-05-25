# Validation: Slice 052 add-slice-candidates-obo-mode

**Date**: 2026-05-20
**Result**: PASS

## Per-criterion results

### AC1 — `/slice-candidates --obo [path]` enters an interactive loop: parses embedded `diagnose-data` JSON, severity-orders findings (high→medium→low stable within band), presents one finding at a time; non---obo invocation is byte-for-byte unchanged

- **Status**: PASS
- **Evidence**:
  - `tests/methodology/test_slice_candidates_obo.py::test_obo_extract_severity_order_and_resume_flags` PASS — observed order `['critical','high','medium','medium']` (4 findings, stable within band); `total=4`, `reviewed=0`; each finding carries `evidence_paths` allow-set.
  - `tests/methodology/test_slice_candidates_obo.py::test_default_path_unchanged_no_traceback` PASS — no-flag invocation on the fixture exits with the existing `"No findings have Confirmed=yes …"` SystemExit message, no traceback. Backlog-byte parity for default path is additionally pinned by the AC4 operational-parity test (which runs `build_backlog.py --in` on the annotated copy and asserts byte-equality vs the pre-slice manual-round-trip golden).
- **Notes**: argparse refactor is dispatch-guarded — the default `--in` code path is unchanged after the early `if args.obo_*` short-circuits. The only default-path change is the shared-entrypoint stdout+stderr UTF-8 reconfigure (logged DEVIATION in build-log), a console-encoding-only fix; the `backlog.md` file output bytes are unaffected (proven by AC4 golden equality).

### AC2 — Each prompt shows live progress (total/reviewed + per-disposition counts) and offers structured `AskUserQuestion` options Approve / Validate-then-approve / Defer / Reject-with-reason / Exit

- **Status**: PASS
- **Evidence**: `skills/slice-candidates/SKILL.md` structural commitments (Claude-driven loop is not Python-unit-testable; verified by static prose pins on the file Claude reads at runtime):
  - `## --obo interactive review mode` section present
  - `AskUserQuestion` tool invoked per finding with all 5 options literally named (Approve / Validate then approve / Defer / Reject / Exit)
  - live-progress format `Finding k of N · A approved · D deferred · R rejected` present
  - Reject path captures free-text "why" (literal "free-text" + "why" wording present)
  - `--obo-extract` JSON output carries the data the loop renders (`total`, `reviewed`, per-finding `current`/`reviewed`) — verified by AC1 evidence
- **Notes**: SOAD-1 honored (structured options, never a bare free-text prompt). The deterministic data substrate (`--obo-extract`) is golden-tested; the conversational rendering is documented prose Claude executes.

### AC3 — `Validate then approve` performs a scoped source peek routed through `build_backlog.py --obo-peek` (mechanical `Path.resolve()` allow-set per ADR-054 deviating Hard rule #2); Claude reads source only through that helper

- **Status**: PASS
- **Evidence**:
  - `tests/methodology/test_slice_candidates_obo.py::test_obo_peek_in_set_served` PASS — `--obo-peek --finding F-crit-1-bbbb2222 --file alpha.py` (cwd = fixture/repo) prints `def alpha(): return 'crit-evidence'`.
  - `test_obo_peek_out_of_set_refused[secret.py]` / `[beta.py]` / `[..\diagnosis.html]` / `[./secret.py]` / `[C:\etc\hosts]` ALL PASS — every evasion (sibling-evidence-of-another-finding, parent-traversal, `./`-prefixed, absolute) is refused non-zero with `out-of-scope: <path> not in finding <id> evidence allow-set` on stderr and a logged refusal in `obo-run.log`.
  - `test_obo_peek_unknown_finding_refused` PASS — `NO-SUCH` finding id → non-zero, `unknown finding id` on stderr.
  - `architecture/decisions/ADR-054-scoped-source-peek-for-slice-candidates-obo-validate.md` exists, `status: accepted`, `supersedes: null`, append-only (no in-place edits to prior ADRs).
  - `skills/slice-candidates/SKILL.md` carries the Hard-rule-#2 ADR-054 carve-out + "`--obo-peek` is the only permitted source-read channel" constraint.
- **Notes**: enforcement is mechanical (helper-side `{Path(p).resolve() for p in evidence_files(...)}` containment), not honour-system prose. The boundary cannot be widened by the conversational layer because SKILL.md forbids direct `Read` of repo source under `--obo`.

### AC4 — `--obo-write` bakes decisions into `diagnosis.annotated.html` (collect() semantics, confirmed ∈ yes|no|defer|""); original `diagnosis.html` byte-unchanged (pre/post SHA-256 asserted); operational parity defined as `parse_html_state` annotation equality + `backlog.md` byte-identity to the manual browser round-trip (NOT browser-output byte-equality)

- **Status**: PASS
- **Evidence**:
  - `test_obo_write_hard_rule_3_and_collect_semantics` PASS — pre/post SHA-256 of the original equal (`296bf8ea09558d80…`); annotated `annotations` keys == `{F-crit-1, F-high-1, F-med-1}` (untouched `F-med-2` ABSENT, not an empty entry — M1 collect() semantics); deferred entry carries `confirmed:"defer"`.
  - `test_obo_write_ensure_ascii_false` PASS — annotated bytes contain raw `café` + `💡` and do NOT contain `é` / `\ud83d` (B1: Python default `ensure_ascii=True` would emit `\uXXXX`; the browser `JSON.stringify` emits raw UTF-8, so this pins parity).
  - `test_obo_write_m_add_2_backslash_and_close_byte_exact` PASS — a Reject note containing a literal backslash + `</script>` round-trips byte-exact through `parse_html_state`; a `re.sub` implementation would corrupt it (M-add-2).
  - `test_obo_write_operational_parity_backlog_equals_golden` PASS — copying the annotated file over a working `diagnosis.html` and running `build_backlog.py --in` produces a `backlog.md` byte-identical (mod the non-deterministic `_Generated from …_` header line) to the checked-in `tests/methodology/fixtures/obo_diagnose_out/backlog.golden.md` (the browser-saved manual round-trip control).
  - `test_obo_write_refuses_unknown_finding` PASS — a decisions map referencing `NO-SUCH` fails closed (non-zero, `unknown finding id`); no partial `diagnosis.annotated.html` written.
- **Notes**: insertion mechanism is **match-span string slicing** `orig_text[:m.start(1)] + new_inner + orig_text[m.end(1):]` — NOT `re.sub` (which would treat `\1` / `\g<…>` / bare backslashes specially and corrupt the payload, M-add-2).

### AC5 — Mid-way Exit persists decisions so far; unreviewed findings ABSENT from annotations (not empty entries); exit report distinguishes never-reached vs Deferred; re-run on annotated copy resumes at first `id ∉ annotations`; Deferred (`confirmed:"defer"`, present in map) NOT re-offered on resume

- **Status**: PASS
- **Evidence**:
  - Combined with AC4 evidence: `F-med-2` (untouched) is ABSENT from `annotations`; `F-med-1` (Defer) IS present in `annotations` with `confirmed:"defer"`. Resume predicate (`id ∉ annotations`) places `F-med-2` first on resume, and `F-med-1` is skipped permanently.
  - SKILL.md operator guidance documents Defer as terminal for resume and names the reopen path ("re-run `--obo` against the **original** `diagnosis.html` … or hand-edit the JSON") — pin verified by AC2 SKILL.md check #6.
  - `--obo-extract`'s per-finding `reviewed` flag (= `fid in annotations`) is the resume predicate's machine-readable form (pinned by AC1 evidence).
- **Notes**: M2/M-add-1 — Deferred is by-design terminal-on-resume but no longer a silent one-way trap; the reopen path is in operator-facing SKILL.md prose.

## Multi-instance validation

**Required?**: no — local single-user CLI/skill; no multi-user / multi-device / multi-account / sync surface.
**Result**: not-applicable

## Reality surprises

1. **Pre-existing Windows `charmap` crash in `build_backlog.py` `main()`** (discovered at T1 fixture-golden generation): the existing entrypoint didn't reconfigure stdout to UTF-8, so its non-ASCII top-candidate print crashed rc=2 on Windows. `--obo-extract` emits JSON containing finding text to stdout and would have inherited the identical crash. Logged as build-log FINDING + DEVIATION; fixed in-band by reconfiguring **both** stdout and stderr at the shared `main()` entrypoint (stderr was also needed — `SystemExit` refusal messages contain em-dashes). No behaviour-of-output change; `backlog.md` bytes are byte-identical (AC4 golden proves it).
2. **Test harness UTF-8 capture requirement**: a `subprocess.run(text=True)` call against `build_backlog.py` mis-decodes the child's correct UTF-8 emoji bytes via the parent's cp1252 default. NOT a tool defect; codified into `tests/methodology/test_slice_candidates_obo.py` (`encoding="utf-8"` on every `subprocess.run`). Captured here so future test authors don't repeat it.
3. **Mid-build methodology-bump scope correction**: design.md / mission-brief's "plugin-manifest / drift posture unaffected" claim conflated PMI-1 artifact enumeration (true: no new registered skill/agent/tool) with "no version bump" (false: ADR-054 + a new skill mode is a methodology-surface behavior change per the changelog Inclusion heuristic + slice-049/ADR-051 law). User-ratified via structured options at the design-is-wrong-mid-build halt → applied the v0.60.0 4-part PMI-1 bump + conventional entry-pin + shippability-consumer-propagation tests. Logged DEVIATION. **Both Critic layers missed this** — captured for the `/reflect` "Missed by Critic" calibration record (a recurring class: behavior-change classification when the slice has no other bump reason; slice-049 B2 generalized to slice-052 by N+1).

## Shippability catalog regression check (Step 5.5)

**Pre-gates**:
- SCMD-1 (`tools.shippability_decoupling_audit`): clean — 52 rows; 497 cited fns; `incidental=0 essential_registered=2 essential_unregistered=0 clean=495` (the new row #52's `pytest tests/methodology/test_slice_candidates_obo.py` is module-level pytest discovery, not a named-function citation — classifies `clean`).
- PTFCD-1 (`tools.shippability_path_audit`): clean — 52 rows, 293 test-path tokens, all files and cited functions exist on disk.

**Runner** (`tools.shippability_runner`): **52 row(s), 52 PASS, 0 FAIL**. No past slice's critical path silently regressed. Row #52 (this slice — operational parity + `--obo-peek` mechanical scoped-peek boundary + Hard-rule-#3 SHA invariance + duplicate-block refusal) PASS.

## VAL-1 layered safety checks (Step 5b)

- **Layer A (credential scan)**: **0** secrets across 24 changed files (skills/, tests/, fixtures, methodology-changelog.md, VERSION, plugin.yaml, ADR-054, slice vault files, drift-log.md, risk-register.md, shippability.md). No allowlist suppressions consumed.
- **Layer B (dependency hallucination)**: **0** import findings. `build_backlog.py` adds `hashlib` (stdlib); `test_slice_candidates_obo.py` resolves cleanly with `--imports-allowlist tests` (pytest namespace conftest); fixture `.py` files contain no imports. No hallucinated or undeclared third-party packages.

## WS-1 / ETC-1

Both opt-in disciplines are **not enabled** for this slice (`**Walking-skeleton**: false`, `**Exploratory-charter**: false` in mission-brief). The audits return clean for non-enabled slices; correct.

## Aggregate result

**PASS** — every AC has PASS evidence, multi-instance N/A, no reality surprise blocks progression, VAL-1 clean, WS-1/ETC-1 not enabled (correct), shippability catalog 52/52, pre-gates clean. Auto-advance permitted.
