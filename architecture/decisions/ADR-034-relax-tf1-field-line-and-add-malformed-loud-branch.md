---
id: ADR-034
title: Fix R-7 by relaxing the TF-1 field-line value match AND adding a loud malformed-field branch (no silent default-off on present-but-broken)
date: 2026-05-17
slice: slice-034-fix-tf1-audit-field-line-regex
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-034: Relax TF-1 field-line value match + add loud malformed-field branch

## Context

R-7 (risk-register, open, medium/medium, score 4; recurred N+1 at slice-033): `tools/test_first_audit.py:54` `_TEST_FIRST_FIELD_RE` is `$`-anchored (`^\*\*Test[-\s]?first\*\*\s*:\s*(true|false)\s*$`). The idiomatic `/slice` mission-brief template form `**Test-first**: true  (per TF-1 — …)` fails the `\s*$` anchor, so `_detect_test_first_flag` returns False, `run_audit` takes the L289 silent default-off path, and `main` exits 0 reporting "not enabled" on a genuinely test-first slice — the entire TF-1 gate is silently bypassed. The defect has only ever been caught manually by the BC-PROJ-4 real-artifact gate run; both first-Critic and DR-1 meta-Critic missed it at slice-033. The risk-register names two candidate fixes: (a) a loud `malformed-test-first-field` violation distinguishing "field absent" from "field present-but-unparseable"; (b) relax the regex to accept a trailing annotation after `true|false`.

## Options considered

1. **Relax-regex only (option b)** — accept `(true|false)\b.*$`. Pros: minimal; closes the witnessed annotated-true case (R-7's exact trigger). Cons: leaves the *other* silent-bypass class open — a present-but-malformed value (`**Test-first**: maybe`, empty value) still falls through to silent default-off. The latent footgun is only half-closed.
2. **Loud-violation only (option a)** — keep strict value match; treat any present-but-non-`true|false` field as `malformed-test-first-field`. Pros: kills all silent bypass. Cons: an annotated `**Test-first**: true  (per TF-1 …)` would be classed *malformed* and HALT every test-first slice using the idiomatic template — turns a silent bug into a loud false-positive that breaks the documented `/slice` template. Unacceptable without also relaxing the value match.
3. **Both (chosen)** — relax the value match so an annotated `true|false` is correctly detected (option b), AND add a separate value-agnostic "field present?" detector that raises a loud `malformed-test-first-field` violation when the field is present but no line yields a valid boolean (option a). Pros: closes the witnessed case AND the broader present-but-broken silent-bypass class; preserves the idiomatic annotated template; `_detect_test_first_flag` keeps its `bool` contract (repro pins `is True`). Cons: two coordinated changes instead of one; a new violation kind to test.

## Decision

Option 3. Widen the value match so the captured boolean must be a **standalone token** — followed by whitespace, an opening `(`, or end-of-line: `^\*\*Test[-\s]?first\*\*\s*:\s*(true|false)(?=[\s(]|$)` (still `^`-anchored on the `**Test-first**:` bold field prefix, so mid-sentence prose cannot match). The earlier candidate `(true|false)\b.*$` was **rejected at /critique M1**: `\b` matches between `false` and `-`, so `false-positive`→`false` / `true.`→`true` / `false; note`→`false` would be silently accepted — re-introducing a narrower form of the R-7 silent-bypass through the fix's own regex (self-violation law). The standalone-token lookahead sends those malformed-suffix forms to the malformed branch instead. Independently, add a value-agnostic field-present matcher; in `run_audit`, before the silent default-off return, if the field prefix is present on some line but no line satisfies the value match, append a `TestFirstViolation(kind="malformed-test-first-field", severity="Important")` with an attributed, actionable message and skip the silent path. Genuinely-absent field → unchanged legitimate default-off. The malformed branch MUST consult the same `(true|false)` matcher (capturing BOTH booleans) so `**Test-first**: false` stays a legitimate default-off, NOT a malformed violation (per /critique M2 — load-bearing invariant). `_detect_test_first_flag` retains its `bool` signature (only the regex it consults changes).

## Consequences

- Behaviour change → `methodology-changelog.md` v0.48.0 entry + 4-part atomic PMI-1 bump (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`). No tool added/removed → INST-1 lockstep only.
- **RULE-ID disposition (per /critique-review M-add-1 — slice-032 DEVIATION-1 class avoidance):** the entry bears a newly-minted RULE-ID **`TFFL-1`** ("TF-1 Field-Line robustness") that *refines TF-1 (slice-002) in place* — rule-ID lineage preserved, **supersedes nothing** — mirroring the EOL-DRIFT-1↔CAD-1 / PMI-1 v1.0→v1.1 in-place-refinement precedent. Every versioned changelog entry v0.22.0→v0.47.0 carries a rule-ID + a bound `test_v_0_NN_0_<rule>_entry_present_in_repo_and_installed`; slice-034 MUST add `tests/methodology/test_methodology_changelog.py::test_v_0_48_0_tffl_1_entry_present_in_repo_and_installed` asserting the `TFFL-1` token + canonical phrase + ADR-034 lineage in BOTH changelog surfaces, and pin the canonical phrase `**Test-first** field-line value must be a standalone boolean token` in the entry body. Omitting the rule-ID/entry-pin would re-commit the slice-032 DEVIATION-1 "no-rule-lineage precedent" self-violation class.
- A brief that was silently-passed yesterday (annotated field-line) now correctly engages the gate; a malformed field that was silently-passed now HALTs loudly at `/build-slice` Step 6. This is the intended refusal-boundary shift.
- New violation kind `malformed-test-first-field` (severity Important) in the audit's vocabulary; rendered by the existing generic `_format_human` + `to_dict()` paths (no special-casing).
- R-7 escalated to `retired`; the catalogued repro (`tests/methodology/test_tf1_field_line_annotation_regression.py`, shippability #34) becomes the durable regression guard so the class cannot silently return.
- No `agents/*.md` / guarded `SKILL.md` touched → CAD-1 / mini-CAD unaffected.

## Reversibility

**Cheap.** The change is localized to one regex and one branch in `tools/test_first_audit.py` plus tests; reverting is a ~1-hour edit. No data model, no contract consumers beyond the audit's own callers, no migration. The methodology-changelog entry would be retired/superseded per the changelog's own append-only discipline if ever rolled back.
