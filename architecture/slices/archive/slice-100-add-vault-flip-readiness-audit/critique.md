# Critique: Slice 100 add-vault-flip-readiness-audit

**Critic reviewed**: mission-brief.md, design.md, ADR-091, project-frame.md, aggregated lessons + slice-098/093/095/097/088/085 reflections
**Date**: 2026-06-02
**Result**: BLOCKED (Critic's opinion; final verdict computed at TRI-1 from ratified dispositions)

## Summary
The slice's *intent* (a deterministic, regression-pinned flip-readiness inventory, capability-without-flip) is sound and well-aligned with the project trajectory. But the **classification heuristic at the heart of ADR-091 is unsound when executed against the real corpus** (APED-1 / Dim 9): its `must-rewrite-before-flip` definition — "executable `ast.Constant` str node, not docstring, not argparse help, not already-seam-routed" — cannot distinguish a path the code *resolves* from a vault path *mentioned in a human-facing error/warning string*, and it mis-classifies the slice-098 Class-B `_SOFT_FILE_SET` git-identity constants. Executed, it produces a baseline polluted with false `must-rewrite` entries and at least one false-class. That defeats AC1/AC2/AC3 and contradicts the slice-095/097 honest-contract lesson the design cites as precedent. Two blockers, three majors, two minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: The `must-rewrite-before-flip` definition mis-classifies error/warning-message strings as breakage (node-type, not usage-context classification)
- **Claim under review**: ADR-091 §Decision — "must-rewrite-before-flip: an executable string-literal (ast.Constant str node, NOT a docstring, NOT an argparse help=/description= kwarg value) containing the pattern, not already-seam-routed."
- **Issue**: Node-TYPE classification, not usage/context classification. A vault literal inside a human-facing message string (`message=(f"architecture/risk-register.md not found at {register} …")`) is an `ast.Constant` str, not a docstring, not an argparse kwarg → lands in `must-rewrite-before-flip`. But these strings do **not assume the vault location**; they are diagnostic prose, at worst slightly stale after the flip. Burying genuine seam sites among them defeats the "complete checklist" purpose (AC1).
- **Evidence**: Executed over `tools/**/*.py` + 3 skill helpers: of executable non-docstring non-Class-B vault-literal occurrences, ~6 path-shaped + ~24 prose/mention; even among path-shaped, several are error-message prose:
  - `tools/state_transition_pin_audit.py:381,395,407` — `message=(...)` diagnostic strings, **already carrying a hand-applied `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` comment** (a pre-existing in-tree convention the design's classifier does not recognize). **[Builder-verified at lines 378-410.]**
  - `tools/cross_spec_parity_audit.py:328-336`, `tools/drift_check_audit.py:309,361,365`, `tools/new_agent_warning_audit.py:116`, `tools/validate_slice_layers.py:241`, `skills/slice-candidates/build_backlog.py:668` — human-facing return/`message=`/warning strings; all `ast.Constant`, none docstrings/argparse → all would be `must-rewrite`. All false.
- **Proposed fix**: Re-scope `must-rewrite-before-flip` to require **path-construction context** (≤1-hop usage analysis, mirroring VWS-1 `_resolve_target`): literal is an arg to `Path(...)`/`PurePath(...)`, an operand of a `/` BinOp, the receiver/arg of `.open`/`.read_text`/`.write_text`/`.read_bytes`/`.glob`/`.iterdir`/`.exists`/`.joinpath`, OR assigned to a name flowing (≤1 hop) into one. A literal NOT in a path-construction context → `doc-example-safe` (reason `prose-mention`). Additionally **recognize the existing `error-message prose` marker** as a seam-acknowledged `doc-example-safe`, alongside the Class-B marker. Re-run APED-1 + re-derive the baseline before pinning AC3.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-091 §Decision rewritten to a context-aware ordered ruleset (marker recognition → seam/VAULT_ROOT → path-construction → fail-closed → prose default); design.md §Error model + match-rule updated. Verified B1 against real code (markers present at lines 381/395/407).

#### B2: `_SOFT_FILE_SET` (PCR:59-62) is Class-B git-identity but the design would classify it `must-rewrite` — contradicts slice-098/ADR-089
- **Claim under review**: design.md / ADR-091 — Class-B recognition is a per-line marker check (`line carries substring 'Class-B git identity (ADR-089)'`).
- **Issue**: slice-098 marked the 21 *usage* lines, not the *definition* constant. `tools/parallel_conflict_resolver.py:59-62` defines `_SOFT_FILE_SET = frozenset({"architecture/slice-queue.md","architecture/shippability.md"})` — two `ast.Constant` str literals on lines carrying **no** Class-B marker. These are git pathspecs fed to `git show :N:<pathspec>` (Class-B per ADR-089 — they RETIRE via `vault_is_external`, NOT filesystem reads needing a path rewrite). The classifier would emit them `must-rewrite`, contradicting slice-098/ADR-089 and putting a false entry in the flip checklist.
- **Evidence**: `tools/parallel_conflict_resolver.py:59-62` (definition, unmarked) vs `:217/:221/:298/:415/...` (21 marked usages). risk-register R-32 confirms PCR's `slice-queue.md`/`shippability.md` git-string reads are the Class-B retire-at-flip class. **[Builder-verified at lines 59-62: unmarked defn confirmed.]**
- **Proposed fix**: (c) explicitly add the Class-B marker to the `_SOFT_FILE_SET` definition lines as part of this slice (a one-line in-PCR edit closing the marker-coverage gap slice-098 left — cheapest, keeps the convention honest). Also: ADR-091 specifies an UNMARKED git-pathspec / ambiguous vault-literal (not a Path-construction, not marked) → `needs-human-classification` (fail-closed), so a future unmarked git-string is surfaced, not silently mis-classed.
- **Builder draft**: **ACCEPTED-FIXED** — adopt option (c): mark `_SOFT_FILE_SET` defn (PCR:60-61) with the Class-B marker (added to slice scope); ADR-091 §Decision documents git-pathspec recognition + unmarked-ambiguous → needs-human.

### Majors (address this slice)

#### M1: The literal-detection pattern is never specified — "containing the pattern" is undefined; over-match unaddressed
- **Claim under review**: ADR-091 — "for `architecture/` and `diagnose-out/` path literals … containing the pattern".
- **Issue**: The match rule (substring? `\barchitecture/`? value-prefix?) is unstated — exactly the APED-1/BC-PROJ-13 unspecified-content-matcher class. A naive substring scan over-matches on `tools/skill_vault_write_safety_audit.py:95` — SVW-1's own **detection regex string** `r"…|architecture/[\w./-]*…"`, not a vault path — and risks matching `_DERIVED_DIRS = ("diagnose-out", "graphify-out")` in `tools/_worktree_paths.py:65` (a config constant). Per slice-095, the match rule + residuals must be named in code + test.
- **Evidence**: `tools/skill_vault_write_safety_audit.py:95`; `tools/_worktree_paths.py:65`; static-analysis literature: distinguishing path-literal from mention requires context/parent-node analysis, not node-type ([Python ast docs](https://docs.python.org/3/library/ast.html), [DeepSource — build your own linter](https://deepsource.com/blog/python-asts-by-building-your-own-linter)).
- **Proposed fix**: Specify the match rule in ADR-091 + module docstring: a str **value** matching `(?:^|[\s'"(/=])(?:architecture|diagnose-out)/` evaluated against `ast.Constant.value` (a trailing `/` is required → excludes bare-`diagnose-out` config names). Exclude the audit's own regex-literal source lines and document residuals: (i) a vault path assembled fully dynamically with no constant fragment is invisible; (ii) a bare-dir-name reference (`"diagnose-out"`, no slash) is out of this surface — named, not silently assumed closed (slice-095 honest-contract).
- **Builder draft**: **ACCEPTED-FIXED** — match rule + the two documented residuals added to ADR-091 §Decision + design.md §Error model; audit-self-source + bare-name exclusions specified.

#### M2: AC3 baseline-pin identity key is fragile; mutation-non-vacuity proves presence, not correct-class
- **Claim under review**: AC2 byte-identical re-run; AC3 pin "by (relpath, stripped-snippet) — proven non-vacuous by mutation."
- **Issue**: (1) Implicit string concatenation — `ast.Constant` for a multi-line concatenated string reports a single start `lineno`/`col_offset`; real sites split the vault literal across physical lines (`cross_spec_parity_audit.py:328-336`), so a "stripped-snippet" key captures only the start-segment → unstable/colliding. (2) Mutation-by-addition proves the pin FAILS when a literal is *added*, not that it lands in the *right* class; given B1, an injected error-string would wrongly enter must-rewrite and the test would "pass non-vacuously" while validating a broken classifier.
- **Evidence**: `tools/cross_spec_parity_audit.py:328-336`; slice-092 lesson "prove non-vacuity by MUTATION" — but the mutation must exercise the *correct-class* property.
- **Proposed fix**: Key the pin on `(relpath, ast.Constant.value-normalized, klass)` (full constant value, not a line-snapshot). Add a second AC3 mutation case: inject an error-MESSAGE vault literal and assert it does NOT enter `must-rewrite` (proves B1's fix), alongside the inject-a-real-seam-literal case.
- **Builder draft**: **ACCEPTED-FIXED** — design.md baseline-key changed to `(relpath, normalized value, klass)`; mission-brief AC3 + TF-1 plan gains `test_error_message_literal_not_must_rewrite` (TPHD-1 harmonized).

#### M3: `diagnose-out/` is near-vacuous on the .py surface, and the genuine must-rewrite set is near-empty post-fix — AC1/smoke-gate over-claim
- **Claim under review**: AC1 "scans … every `architecture/`/`diagnose-out/` location-assuming literal"; smoke gate "non-empty must-rewrite set (>0)."
- **Issue**: Executed, there are **zero** `diagnose-out/`-prefixed path-construction literals in `tools/**/*.py` (only `_DERIVED_DIRS` config tuple + skill-helper docstrings/argparse). Once B1/B2 are fixed, the genuine production-`.py` `must-rewrite` set is near-empty — because **slice-098 already routed this surface**. The mid-slice "must-rewrite >0" gate may pass only *because of B1 false positives*. The real `architecture/` location-assumption density lives in `tests/**` + SKILL.md prose (both deferred).
- **Evidence**: full-corpus AST scan (Critic-executed): 0 `diagnose-out/` path-construction literals in tools/; risk-register R-32 names the residual as "physical move + git-untrack + prose rewrite".
- **Proposed fix**: Reframe honestly: the production-`.py` surface is *already largely seam-routed* (slice-098), so the audit's near-term value is the **completeness proof** (clean bill of health for the code surface) + the **regression guard**, not a large current must-rewrite checklist. Change the smoke gate from "must-rewrite >0 else broken" to "**total classified occurrences >0** AND zero un-triaged `needs-human` AND full suite green." Update AC1 to not imply a large must-rewrite set.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief smoke gate + AC1 reframed (value = completeness-proof + regression-guard; non-emptiness asserted on total classified, not must-rewrite); ADR-091 §Consequences already notes "near-term value is the regression guard."

### Minors (log; address if cheap)

#### m1: design.md cites a non-existent helper — `tools/_pyfn.py _find_repo_root`
- **Claim under review**: design.md What's reused — "tools/_pyfn.py _find_repo_root (.git-OR-VERSION resolver)."
- **Issue**: `tools/_pyfn.py` is the PTFFD-1 test-function-resolution helper (no `_find_repo_root`); the resolver lives in `tools/test_first_audit.py:269` / `tools/shippability_path_audit.py:90`, and the named template VWS-1 uses `Path(__file__).resolve().parent.parent` + `--repo-root`.
- **Evidence**: `tools/_pyfn.py`; `tools/test_first_audit.py:269`; `tools/vault_write_safety_audit.py`.
- **Proposed fix**: Cite VWS-1's `Path(__file__).resolve().parent.parent` default + `--repo-root` override (the structural template already named).
- **Builder draft**: **ACCEPTED-FIXED** — design.md "What's reused" corrected (drop `_pyfn._find_repo_root`; use VWS-1's `Path(__file__).parent.parent` + `--repo-root`).

#### m2: New-public-tool fan-out count not enumerated with site-grep
- **Claim under review**: must-not-defer "New-public-tool count fan-out — plugin.yaml + install_audit + INSTALL.md + shippability row."
- **Issue**: The aggregated lesson lists FIVE sites (incl. INSTALL.md L22+L166, the cp1252 parametrize list, per-tool inventory-pin tests); the design lists four and omits the cp1252 parametrize list + per-tool inventory-pin sites. Per FBCD-1, every count site should be grep-enumerated.
- **Evidence**: aggregated lessons "grep EVERY count literal (plugin.yaml, install_audit, INSTALL.md L22+L166, cp1252 parametrize list, per-tool inventory-pin tests)."
- **Proposed fix**: At build, grep every count literal per the five-site list and confirm each.
- **Builder draft**: **ACCEPTED-PENDING** — build-time grep of all five count-literal sites (a build step, not a design change).

## Dimensions checked
- [x] Unfounded assumptions — B1, B2, m1 (verified real). The "deterministic"/"complete checklist" claims don't hold as originally specified.
- [x] Missing edge cases — M2 (concatenation lineno; mutation correct-class), M3 (empty diagnose-out; near-vacuous must-rewrite). Concurrency/network N/A (read-only local CLI).
- [x] Over-engineering — none material; 4-class taxonomy justified; scope deferral well-reasoned.
- [x] Under-engineering — B1 (path-context detection AC1 needs is not designed), M1 (match rule unspecified).
- [x] Contract gaps — CLI exit codes / --json / --strict well-specified; `--strict` baseline needs the M2 key fix to be stable.
- [x] Security — none (read-only local CLI; no auth/network/writes/secrets).
- [x] Drift from vault — B2 (contradicts slice-098/ADR-089 Class-B). ADR-065/085/089 verified consistent; AC5 aligns with ADR-085 + R-32 retire-at-flip.
- [x] Web-known issues — confirmed: distinguishing path-literal from mention requires context/parent-node analysis, not node-type (corroborates B1/M1).
- [x] Cross-cutting conformance — APED-1 executed against the real corpus (not reasoned); honest-contract (slice-095/097) violated by B1/M1; cp1252/UTF8-STDOUT-1 correctly planned.

## Triage

**Triaged by**: user
**Date**: 2026-06-02
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes (first Critic B1/B2/M1/M2/M3/m1/m2 + meta-Critic missed-Blocker B-add-1). Meta-Critic verdict: EXTEND (all 7 first-Critic findings VALID + correct severity; +1 missed Blocker). User ratified all dispositions + apply B-add-1 + build.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Context-aware ordered ruleset replaces node-type-only (ADR-091 §Decision rules 1-5; design §Error model). |
| B2 | Blocker | ACCEPTED-FIXED | `_SOFT_FILE_SET` defn (PCR:60-61) gets the Class-B marker → rule 2 `already-seam-routed` (PCR edit at build). |
| M1 | Major | ACCEPTED-FIXED | Match rule specified + self/`_DERIVED_DIRS` exclusion; amended by B-add-1 (bare-or-slashed segment, context decides). |
| M2 | Major | ACCEPTED-FIXED | Pin keyed on `(relpath, ast.Constant.value, klass)`; 2nd mutation `test_error_message_literal_not_must_rewrite` guards B1. |
| M3 | Major | ACCEPTED-FIXED | Smoke gate reframed to total-classified >0 + zero needs-human; amended by B-add-1 (must-rewrite small-but-non-empty ≥4). |
| m1 | Minor | ACCEPTED-FIXED | Cite VWS-1 `Path(__file__).resolve().parent.parent` + `--repo-root`; not `_pyfn`. |
| m2 | Minor | ACCEPTED-PENDING | Five-site count-literal grep at `/build-slice` (plugin.yaml + install_audit + INSTALL.md L22+L166 + cp1252 parametrize + per-tool inventory pins). |
| B-add-1 | Blocker | ACCEPTED-FIXED | (meta-Critic missed finding) Match rule catches bare-segment path-construction; baseline includes the 4 `project_frame_synth.py` sites; M3/ADR "near-empty" over-claim retired. |
