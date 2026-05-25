# Reflection: Slice 002 fix-diagnose-contract-and-cwd-mismatch

**Date**: 2026-05-09
**Shipped**: YES-WITH-DEFERRALS

## Validated

- **Canonical contract wording locked across 13 sites byte-equal** — validated by `test_pass_templates_match_skill_md_step5_contract` + Python-counted occurrences (1 SKILL.md + 11 templates + 1 extra in 01-intent.md Hard rules = 13). The byte-equality discipline preserves slice-001's lesson "the contract was authoritative in SKILL.md and copied verbatim into templates" — drift would now fail loudly instead of silently.
- **Cwd-mismatch warning bash check fires correctly under TARGET ≠ $PWD** — validated by manual smoke (deferred from old AC #5): with `TARGET="<HOME>"` outside `$PWD`, the warning emits with full prose; with `TARGET="$(pwd)"`, no warning (silent — correct happy-path).
- **RR-1 audit picks up R-1 + R-2 cleanly post-conversion** — validated by `tools.risk_register_audit` returning both risks with score+band derived correctly (R-1: medium×high=6 high; R-2: medium×low=2 low), zero violations.
- **Slice-001 foundation untouched by slice-002 prose edits** — shippability catalog 30/30 PASS. Full repo test suite 333/333 (was 326 + 7 new). Pure-prose-edit slice doesn't regress code.
- **Voluntary Critic on a low-tier slice paid off — second confirmation.** Slice-001 (large surface) returned 12 findings with 2 real blockers; slice-002 (narrow surface) returned 8 findings with 1 hypothesis-correction win (M1) + 7 design-tightening wins. Pattern across two slices: voluntary Critic on any slice touching cross-cutting concerns (orchestration, contract-wording, vault-format, runtime-environment) reliably surfaces real issues. **Recommendation for future low-tier slices**: invoke voluntary Critic if the slice touches anything cross-cutting; skip only on truly localized changes.

## Corrected

- **Slice's own design wrong about AC count** — design.md had 5 ACs; AC #4 was a meta-AC ("prose-pin tests regression-guard the corrections") and AC #5 was deferred-explicitly manual smoke. Both blocked TF-1 strict at pre-finish (AC#4 + AC#5 had no test-first rows). Collapsed to 3 ACs during /build-slice Phase 6; manual smoke moved to verification plan as a deferred check; meta-AC dropped (TF-1 enforces what AC #4 asserted inherently). Mission-brief.md and design.md updated in place during build; build-log.md captures the deviation. **Lesson**: don't write ACs that are circular meta-claims about other ACs — TF-1's enforcement of test-mapping per AC makes those redundant. Don't write ACs that are explicitly-deferred manual-only checks — put them in the verification plan as deferred entries instead. ACs should be testable, observable, and *productive* (not derivable from other ACs).
- **No ADRs superseded** — slice-002 corrects how slice-001's ADR-001 was *expressed*, not the contract itself; ADR-001 remains accepted.

## Discovered

- **VAL-1 Layer B internal-imports finding pattern is recurring** — slice-001 had 6 findings of `assemble`/`tests`; slice-002 has 3 findings of `tests`/`tools`. Same defer-with-rationale pattern. Graduates from "one-off finding" (slice-001) to "real methodology gap" (slice-002 confirmation). The `tools` case is especially weird because `tools` IS a real pip-installed package per `pyproject.toml`'s `[tool.setuptools] packages = ["tools"]`, but Layer B reads only `[project.dependencies]` (external deps), not the project's own declared package list. **Impact for next slice**: this is now a clear slice-003 candidate — add `--imports-allowlist` (or read project's own declared packages) to `tools.validate_slice_layers`. Logged in lessons-learned.md.
- **RR-1 audit docstring vs regex mismatch** — `tools/risk_register_audit.py:17-26` docstring shows `## R-NN -- <title>` (double-dash) as a valid heading, but the regex `_RISK_HEADING_RE` at line 56 only accepts single em-dash or single hyphen (one character). My initial format conversion in /build-slice Phase 4 used `--` per the docstring; audit returned 0 risks silently; switched to em-dash to fix. **Tooling-cleanup candidate** (small slice or risk-spike): either fix the regex to accept `--`, or update the docstring to drop the misleading example. Logged in lessons-learned.md.
- **Critic miss-pattern accumulating: methodology-conformance / tooling-conformance** — slice-002 missed by Critic: (a) the 5-AC structure being TF-1-incompatible (AC#4 meta + AC#5 deferred had no rows); (b) the RR-1 docstring-vs-regex mismatch when reviewing the format conversion plan. These complement slice-001's missed-by-Critic pattern (environmental / runtime / cwd / permissions). **Both miss-classes are cross-cutting concerns that map weakly to the existing 8 Critic dimensions.** N=2 toward the `/critic-calibrate` ≥3-distinct-slices threshold. One more slice with this pattern → calibration-prompt update candidate.

## Deferred

- **Slice-003 candidate: `add-val-1-imports-allowlist`** — addresses the now-confirmed recurring VAL-1 Layer B noise. Small slice (~1-2 hours). Could read project's own pyproject.toml `[tool.setuptools] packages` AND/OR accept an explicit `--imports-allowlist <path>` flag. Eliminates the defer-with-rationale ritual on every slice that touches `tests/`.
- **Tooling cleanup: `fix-rr1-audit-docstring-or-regex`** — surfaced this slice. Cheap (one-line regex update OR one-line docstring update). Could be a quick warm-up slice or a build-check pattern ("use em-dash heading in risk-register" → BC-PROJ rule).
- **R-2 (no programmatic test of cwd-warning runtime emission)** — open in risk-register.md. Defer until evidence of regression.
- **R-1 deeper fixes (option C orchestrator pre-cd; option E parent-thread pre-compute)** — open until option A's documented constraint proves insufficient in practice. No action this slice.

## Critic calibration

Per TRI-1, scoring each finding from `critique.md` `## Triage` against build + validate reality:

- **M1** (cwd-mismatch hypothesis softening): **VALIDATED** — Critic uncovered GitHub issue #57037 + applied causal-uncertainty correction; the slice-002 fix prose now references both the cwd-mismatch hypothesis AND the parallel-spawn cascade-failure alternative. Without M1, the warning prose would have over-promised certainty. Critic was right.
- **M2** (canonical contract wording lock + byte-equality test): **VALIDATED** — wording locked uniformly across 13 sites; `test_pass_templates_match_skill_md_step5_contract` enforces drift detection. Critic was right.
- **M3** (AC #5 demote to deferred-explicitly + R-2 entry): **VALIDATED** — manual smoke is appropriately deferred; R-2 logged in risk-register; programmatic verification deferred only if regression surfaces. Critic was right.
- **M4** (preserve "Do NOT call Write" substring for existing test compatibility): **VALIDATED** — canonical contract wording preserves the substring; existing `test_skill_md_subagents_instructed_no_write` continues to pass without modification. Critic was right.
- **m1** (11-file enumeration): **VALIDATED** — design.md reads cleanly with explicit list; no future reviewer will mistake the range as 4 files.
- **m2** (`_FIELD_RE` single-line caveat): **VALIDATED** — sub-bullets after field block confirmed working; the audit's parser ignored prose without violation; no truncation.
- **m3** (explicit before/after diff table): **VALIDATED** — table was exactly the build-time recipe; zero misreads during conversion.
- **m4** (drop band/score over-specification): **VALIDATED** — integration test asserts only `≥1 risk + zero violations`; band-agnostic; resilient to future re-rankings.

**Missed by Critic**:
- **5-AC structure was TF-1-incompatible.** AC#4 (meta-AC) and AC#5 (deferred manual smoke) had no test-first rows. The Critic reviewed the test-first plan and didn't flag that ACs without rows would fail TF-1 strict at pre-finish. Same calibration class as slice-001's "Critic missed environmental/runtime concerns": both are about **methodology-conformance** rather than internal technical consistency of the design. Discovered at /build-slice Phase 6 pre-finish gate.
- **RR-1 audit docstring-vs-regex mismatch.** The Critic reviewed design.md's "Format conversion (R1 only)" subsection citing the audit's expected format, and didn't dig into the audit's actual regex to verify the docstring example was consistent. Same calibration class — **tooling-conformance**: the Critic took the docstring at face value rather than verifying the implementation matched.

**Pattern (cumulative across slice-001 + slice-002)**: Critic is strong on internal technical consistency within the slice's scope but consistently misses **cross-cutting conformance** issues:
- slice-001: environmental / runtime / cwd / permissions (cwd-mismatch); contract self-inconsistency in legacy templates the slice didn't touch
- slice-002: methodology-conformance (TF-1-incompatible AC structure); tooling-conformance (docstring-vs-regex mismatch)

N=2 toward `/critic-calibrate` ≥3-distinct-slices threshold. **One more slice with a similar miss → graduates to a real Critic-prompt update candidate** (e.g., add a "Cross-cutting conformance" 9th dimension: "Does the slice's work conform to existing methodology audits, tooling docs vs implementation, and runtime environment assumptions?"). Logging here so `/critic-calibrate` (when archive ≥ 5 slices) sees the pattern explicitly.

## Lessons for next slice

- **Don't write meta-ACs.** ACs that assert "tests for above ACs exist" are circular under TF-1. Keep ACs to direct, observable, testable claims.
- **Don't write deferred-explicitly ACs.** Move deferred manual smokes to the verification plan as deferred entries; ACs should map to test-first rows that progress PENDING → PASSING.
- **For RR-1 risk-register entries: use em-dash heading separator (`## R-N — title`), not double-dash (`--`).** The audit's docstring is misleading; the actual regex is single-character. Slice-003 candidate: fix audit docstring or regex.
- **VAL-1 Layer B internal-imports recurrence is now confirmed across 2 slices.** Treat as a methodology gap, not a one-off. `add-val-1-imports-allowlist` is now a clear slice candidate with concrete user-facing benefit (no more defer-with-rationale on every test-touching slice).
- **Voluntary Critic on cross-cutting concerns continues to pay off.** Slice-001 + slice-002 both invoked voluntary Critic on low-tier slices and both runs caught real issues. For slice-003 (whatever it is), default to running voluntary Critic if it touches subagent / orchestration / contract-wording / vault-format / runtime-environment.

## Vault updates made (thin vault)

- [`risk-register.md`](../../risk-register.md) — converted to RR-1 schema during build; R-1 retained with claude-code #57037 cross-reference; R-2 added (no programmatic test of cwd-warning runtime emission)
- [`lessons-learned.md`](../../lessons-learned.md) — slice-002 entry appended (see Step 5 below)
- [`shippability.md`](../../shippability.md) — slice-002 critical-path test entry appended (see Step 5.3 below)
- This slice's [`design.md`](design.md) — updated during /build-slice Phase 0 to reflect 8 triage corrections; updated during /build-slice Phase 6 to collapse 5 ACs → 3 ACs (build-log captures the deviation)
- This slice's [`mission-brief.md`](mission-brief.md) — same — collapsed 5 ACs to 3; deferred manual smoke moved to verification plan
- This slice's [`build-log.md`](build-log.md) — appended deviation + finding events
- No ADRs created or superseded — slice-002 corrects how ADR-001 was *expressed* in skill prose, not the contract itself. ADR-001 remains accepted.
