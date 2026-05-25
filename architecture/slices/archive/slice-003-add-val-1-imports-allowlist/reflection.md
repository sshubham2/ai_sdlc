# Reflection: Slice 003 add-val-1-imports-allowlist

**Date**: 2026-05-09
**Shipped**: YES-WITH-DEFERRALS

## Validated

- **Setuptools-packages auto-read works for explicit-list form** — validated by `test_parse_declared_deps_reads_setuptools_packages` (unit) + real-CLI invocation against this repo's own `pyproject.toml` showing `"tools"` in `declared_deps` and `from tools.X import …` resolving with NO `--imports-allowlist` flag. AC #1 confirmed in production-shaped invocation.
- **Lenient-API / strict-CLI asymmetry per ADR-002 holds in practice** — validated by `test_imports_allowlist_flag_resolves_listed_name` (Python API silently merges; empty-after-normalize entries skip) + `test_cli_imports_allowlist_rejects_empty_string` (CLI emits canonical `parser.error` message with exit 2). The asymmetry is not just a documented preference — it's enforced by tests at both surfaces.
- **Cardinal AC #3 verification: slice-002 archive replay** — validated by both `test_slice_002_archive_replay_zero_findings_with_allowlist` AND a real-CLI subprocess invocation from project root. Returns "0 import finding(s)" exit 0 with `--imports-allowlist tests`. The slice's headline promise (the pain it set out to fix) is verifiably retired.
- **AC #4 prose-pin (per Critic M1) catches drift** — validated by `test_validate_slice_skill_documents_imports_allowlist_and_setuptools_packages` asserting both literal substrings `--imports-allowlist` AND `[tool.setuptools] packages` appear in `skills/validate-slice/SKILL.md`. The methodology-conformance gap M1 flagged is now closed: must-not-defer item promoted to AC #4 with its own test row that fails loudly on prose drift.
- **Voluntary Critic on a low-tier cross-cutting slice paid off — third confirmation.** Critic-required was `false` (low tier, no mandatory triggers). User invoked `/critique` anyway. Returned 7 findings (0 blockers + 2 majors + 5 minors); ALL 7 ratified ACCEPTED-FIXED before triage gate; ALL 7 confirmed VALIDATED at validate-time. ROI continues to justify default-on-cross-cutting for low-tier slices. **Pattern across slice-001 + slice-002 + slice-003: voluntary Critic on cross-cutting concerns is a no-brainer.**
- **TF-1 strict catches the methodology-conformance gap M1 was about** — validated by the audit returning clean (8/8 PASSING) at pre-finish, including the row #8 prose-pin that the M1 fix added. The discipline ratchets reliability up not just for code claims, but for documentation claims too.
- **Backwards-compat preserved** — validated by full `test_validate_slice_layers.py` suite running 32/32 (24 pre-existing + 8 new) without modification to existing tests. The `imports_allowlist=None` default IS byte-equivalent to today as the design promised.

## Corrected

- **Slice's mission-brief.md / design.md / ADR-002 already absorbed all 7 Critic ACCEPTED-FIXED edits during /critique** — those were corrections-during-design, not corrections-discovered-at-validate. Listed for completeness: M1 (prose-pin promoted to AC #4), M2 (Python API contract aligned with implementation sketch as lenient), m1 (PEP 503 mislabeling → "name-normalized"), m2 (Bash continuation → single-line PowerShell-friendly), m3 (dotted-only setuptools packages limitation documented), m4 (whitespace API path expanded), m5 (insertion-point ambiguity reworded).
- **Test-first row #5 venue clarified mid-build** — `test_imports_allowlist_rejects_empty_string` was renamed at /critique-time to `test_cli_imports_allowlist_rejects_empty_string`; type changed unit → integration to match its CLI-level scope.
- **One in-build deviation (test tightening, not behavior change)** — `test_cli_imports_allowlist_rejects_empty_string` initially asserted only `excinfo.value.code == 2`. This passed by accident before any implementation existed because argparse's "unrecognized arguments" path also exits with code 2. Tightened the assertion to ALSO require the canonical error-message substring `"--imports-allowlist requires a non-empty"` in stderr. After tightening: PENDING → WRITTEN-FAILING → PASSING transitions are genuine. **Lesson: TF-1 PENDING → WRITTEN-FAILING transition needs verification that the test would fail without the implementation, not just that the test fails right now.** No design change; design always specified the canonical error message — the deviation was a test-assertion tightening that now correctly enforces what the design said.
- **No ADRs superseded** — ADR-002 stands as accepted; ADR-001 is unrelated to this slice's scope.

## Discovered

- **TF-1 false-PASS pitfall: argparse exit-code-2 collisions.** When writing test-first tests for an argparse `parser.error(...)` flow, asserting only on `excinfo.value.code == 2` can produce a TF-1-invalid PENDING → WRITTEN-FAILING transition: argparse's "unrecognized arguments" branch ALSO exits with code 2 when the flag isn't yet implemented, so the test "passes" before the production code exists. **Generic Python test-first pattern**, not project-specific. The fix: pin a flag-specific signal (the canonical error-message substring in stderr, or the flag name appearing in the parser's `usage` output, or similar). Surfaced at slice-003 /build-slice T5; deviated and fixed mid-build. Worth lessons-learned (and watch list for BC-1 promotion if it recurs in slice-004+).
- **VAL-1 self-application meta-irony.** When a slice ships a fixture file containing a fake import (intentionally fake — used as test data by the audit being shipped), running /validate-slice's Step 5b VAL-1 audit on this slice's own changed files surfaces 1 Important finding on that fixture's import statement. The fixture's package isn't declared in THIS repo's pyproject (because it's intentionally fake). **Resolution path: use the slice's own new `--imports-allowlist <fake_pkg>` flag at validate-time** — pleasing self-referential symmetry. Future slices that ship fixtures with fake imports should add the fake package name to the validate-time allowlist. Not a project risk; not a design defect; just a wrinkle in the meta-bootstrap path that's worth documenting.
- **AC #3 baseline shifted from 5 → 3 (positive surprise).** Mission brief's "vs 5 today" baseline was pre-fix. Post-fix without flag: 3 findings (only `tests` remaining, because AC #1's setuptools-packages auto-read eliminates the 2 `tools` findings automatically). With flag: 0. The implementation does MORE than AC #3 strictly required — AC #1 is a stronger fix than the AC's framing credited. Net effect is positive; shifts the slice's value upward.
- **BC-1 trigger-keyword false-positive precision issue.** BC-PROJ-2 (LLM fence parsing) and BC-GLOBAL-1 (same) both fired on this slice because the mission brief contains the word "parse" (in `tomllib`-parses and `ast`-parses contexts — neither related to LLM output fence collisions). The current BC-1 trigger-keyword matcher is substring-only with no word-boundary or domain-context awareness. **Tooling-precision issue**, not a project risk; could be addressed by a future small slice (`add-bc-1-keyword-precision`) that adds word-boundary or context-disambiguation to `tools.build_checks_audit`. Defer-with-rationale was the right disposition this slice; logged for future improvement.
- **Critic miss-class "cross-cutting conformance" reaches N=3 distinct slices.** Pattern hardening: slice-001 (environmental/runtime + tooling-conformance), slice-002 (methodology-conformance + tooling-conformance), slice-003 (testing-discipline-conformance + tooling-conformance). The existing 8 Critic dimensions don't cover this miss-class cleanly. **`/critic-calibrate` ≥3-distinct-slices threshold is now reached.** Specific recommendation: add a 9th Critic dimension covering "does the slice's work conform to existing methodology audits (TF-1, RR-1, WIRE-1, BC-1, NFR-1, VAL-1), tooling docs vs implementation, runtime environment assumptions, and testing-discipline conventions (e.g., TF-1 PENDING → WRITTEN-FAILING genuineness)?"

## Deferred

- **`fix-rr1-audit-docstring-or-regex`** — surfaced in slice-002 deferrals; still pending. Cheap (~30-60 min); could be a fast warm-up slice.
- **`add-bc-1-keyword-precision`** — surfaced this slice; would address the BC-1 trigger-keyword false-positive precision issue (word-boundary or context-aware matching).
- **`/critic-calibrate` meta-skill run** — N=3 threshold reached; recommend after this slice archives. Proposes 9th Critic dimension targeting cross-cutting conformance.
- **Setuptools `[tool.setuptools.packages.find]` auto-discovery** — out-of-scope per mission brief; ADR-002 documents it as a follow-on.
- **Multi-backend build-system reading** (Hatch `[tool.hatch.build.targets.wheel] packages`, PDM `[tool.pdm]`, Flit `[tool.flit]`) — out-of-scope; deferred until a project hits the gap.
- **Dotted-only setuptools packages top-component fallback** — documented as a known limitation in ADR-002 Consequences; workaround `--imports-allowlist <top>` exists.
- **R-1 deeper fixes (orchestrator pre-cd; parent-thread pre-compute)** — open in risk-register; documented-constraint workaround still acceptable per slice-002.
- **R-2 programmatic test of cwd-warning runtime emission** — open; deferred until evidence of regression.

## Critic calibration

Per **TRI-1**, scoring each finding from `critique.md` `## Triage` table against build + validate reality:

- **M1** (must-not-defer SKILL.md prose update without test row): **VALIDATED** — disposition ACCEPTED-FIXED; promoted to AC #4 with prose-pin test row #8; test passes; SKILL.md prose contains both literal substrings; methodology-conformance gap closed. Critic was right.
- **M2** (Python API empty-entry handling self-contradiction): **VALIDATED** — disposition ACCEPTED-FIXED; lenient/strict asymmetry per ADR-002 implemented and tested at both API and CLI surfaces. Critic was right.
- **m1** (PEP 503 mislabeled): **VALIDATED** — disposition ACCEPTED-FIXED; design.md + ADR-002 now say "name-normalized" with explanatory note. Critic's web-known-issues catch was technically correct; documentation accuracy improved.
- **m2** (Bash continuation on Windows / PowerShell): **VALIDATED** — disposition ACCEPTED-FIXED; mid-slice smoke command collapsed to single line; verified in PowerShell during validation (cross-shell-compatible). Critic's runtime-environment catch was right.
- **m3** (dotted-only setuptools packages): **VALIDATED** — disposition ACCEPTED-FIXED; documented as known limitation in ADR-002 Consequences. The case didn't surface in this repo (no dotted-only declarations), but the documentation prevents future confusion. Critic was right; preventive.
- **m4** (whitespace API path under-described): **VALIDATED** — disposition ACCEPTED-FIXED; error model row 3 expanded; behavior matches (CLI strips before validating; API normalizes via `_normalize_pkg`'s internal `.strip()`). Critic was right.
- **m5** (parse_declared_deps insertion-point ambiguous): **VALIDATED** — disposition ACCEPTED-FIXED; implementation sketch reworded; build implementation went into the right scope (inside the `if pyproject_path` branch); no `NameError`. Critic's drift-from-implementation catch was right.

**Missed by Critic**:

- **TF-1 false-PASS pitfall (argparse exit-code-2 collision).** The Critic reviewed the test-first plan (8 rows, 4 ACs) and didn't flag that `test_imports_allowlist_rejects_empty_string` (now `test_cli_imports_allowlist_rejects_empty_string`) would pass accidentally before any implementation existed because argparse's "unrecognized arguments" path also exits with code 2. Same calibration class as slice-001's "Critic missed environmental/runtime concerns" and slice-002's "Critic missed methodology-conformance" — this slice's miss is **testing-discipline-conformance**: the Critic should ask "would this test fail BEFORE the implementation in a way that distinguishes 'flag rejected' from 'flag doesn't exist'?" Discovered at /build-slice T5 first run.

- **BC-1 trigger-keyword false-positive precision.** The Critic reviewed `mission-brief.md` and `design.md` and didn't flag that the words "parse" (in `tomllib`-parses / `ast`-parses contexts) would trigger BC-PROJ-2 / BC-GLOBAL-1 (LLM fence parsing rules) at /build-slice's BC-1 audit. Same calibration class as slice-001's contract self-inconsistency miss and slice-002's RR-1 docstring-vs-regex miss — **tooling-conformance** issue: the Critic should ask "do this slice's natural-language artifacts contain trigger keywords for existing BC rules in unrelated semantic contexts that will produce false-positive findings at /build-slice?"

**Pattern (cumulative across slice-001 + slice-002 + slice-003)**: Critic is strong on internal technical consistency within the slice's scope but consistently misses **cross-cutting conformance** issues:

- **slice-001**: environmental / runtime (cwd-mismatch tool denial); contract self-inconsistency in legacy templates the slice didn't touch (tooling-conformance)
- **slice-002**: methodology-conformance (5-AC structure TF-1-incompatible); tooling-conformance (RR-1 audit docstring-vs-regex mismatch)
- **slice-003**: testing-discipline-conformance (TF-1 PENDING → WRITTEN-FAILING genuineness for argparse exit codes); tooling-conformance (BC-1 trigger-keyword false-positive precision)

**N=3 distinct slices reached** (slice-001 + slice-002 + slice-003). The `/critic-calibrate` ≥3-slices threshold is met. **Concrete proposal** for the 9th Critic dimension: "**Cross-cutting conformance**: Does the slice's work conform to existing methodology audits (TF-1, RR-1, WIRE-1, BC-1, NFR-1, VAL-1, TRI-1)? Does any documentation claim differ from the actual implementation it cites? Do natural-language artifacts contain trigger keywords for existing BC rules that will produce false-positive findings? Will TF-1 PENDING → WRITTEN-FAILING transitions be genuine, or could the test pass coincidentally before implementation? Will the slice's runtime environment (cross-shell, cross-platform, cross-CWD) match the design's assumptions?"

Recommend running `/critic-calibrate` after this slice archives — it can ratify or refine this proposal with cross-slice pattern analysis.

## Lessons for next slice

- **TF-1 PENDING → WRITTEN-FAILING transition needs genuine failure, not coincidental.** Tests asserting only on argparse exit codes can pass accidentally before implementation (argparse "unrecognized arguments" exits with code 2, same as `parser.error`). Pin flag-specific signals: canonical error message substring in stderr, OR the flag name appearing in the parser's `usage` output. Generic Python test-first pattern.
- **VAL-1 fixture-meta-irony resolution: use the slice's own ship.** When a slice introduces a fixture file with a fake import, run /validate-slice's Step 5b with `--imports-allowlist <fake_pkg>` to silence the meta-finding. Defer-with-rationale is also valid; both routes work.
- **BC-1 trigger keywords match substrings without word-boundary or context awareness — anticipate false positives.** Defer-with-rationale is the right disposition when the keyword match is semantically unrelated to the rule's domain. A future `add-bc-1-keyword-precision` slice can address this if recurring noise becomes a problem.
- **Voluntary Critic on cross-cutting low-tier slices is now N=3 / 3 paid off.** Default heuristic continues to apply: invoke voluntary Critic if the slice touches subagent / orchestration / contract-wording / vault-format / runtime-environment / methodology-tooling, even on low-tier scope.
- **`/critic-calibrate` should run next** — N=3 threshold reached for cross-cutting conformance miss-class. The recommendation is concrete: add a 9th dimension. Don't let this finding decay in the lessons-learned stream when the calibration loop is the explicit cure for spec-rot of the Critic prompt itself.

## Vault updates made (thin vault)

- `architecture/lessons-learned.md` — slice-003 entry appended (see Step 5 below)
- `architecture/shippability.md` — slice-003 critical-path test entry appended (see Step 5.3 below)
- `architecture/slices/slice-003-add-val-1-imports-allowlist/` — to be auto-archived in Step 6 below
- `architecture/slices/_index.md` and `architecture/slices/archive/_index.md` — to be regenerated in Step 6 below
- This slice's [`design.md`](design.md), [`mission-brief.md`](mission-brief.md), [`ADR-002`](../../decisions/ADR-002-val-1-imports-allowlist-explicit-flag.md) — already updated during /critique with the 7 ACCEPTED-FIXED fixes (M1, M2, m1, m2, m3, m4, m5); no further updates needed at /reflect time
- `architecture/risk-register.md` — no new risks added (the discoveries are tooling-precision and meta-bootstrap observations, not project risks)
- No ADRs superseded — ADR-002 stands as accepted; ADR-001 is unrelated
