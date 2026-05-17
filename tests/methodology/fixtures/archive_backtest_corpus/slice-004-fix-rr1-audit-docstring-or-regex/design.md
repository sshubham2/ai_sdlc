# Design: Slice 004 fix-rr1-audit-docstring-or-regex

**Date**: 2026-05-09
**Mode**: Standard

## What's new

- `tools/risk_register_audit.py`:
  - **Module docstring "Format" section** (currently L17–L27): change the canonical heading example `## R-NN -- <title>` → `## R-1 — <title>` (digit-bearing ID + em-dash separator). *(Critic B1: `R-NN` is letters; the regex requires `R-?\d+`; `## R-NN — title` returns NO-MATCH. Empirically verified.)* Add a one-line note clarifying that single hyphen `## R-1 - <title>` is also accepted as a permitted alternate form (matches the regex's character class `[—\-]`), but em-dash is canonical per the methodology's lessons-learned (slice-002).
  - **Inline comment immediately above `_RISK_HEADING_RE`** (currently L55): rewrite from the misleading current form `# H2 risk heading: "## R-NN -- title" or "## R-NN — title" (em dash)` to accurately describe what the regex matches, using digit-bearing examples: `# H2 risk heading: "## R-1 — title" (em-dash separator, canonical) or "## R-1 - title" (single hyphen, accepted alternate). Double-hyphen "--" is NOT accepted — that's two characters; the regex is single-character via [—\-].`
  - **Regex itself (`_RISK_HEADING_RE` at L56)**: **UNCHANGED**. Stays as `r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$"`. No behavior change.
- `architecture/risk-register.md`:
  - **L3 opening description prose** (per Critic M2): change `H2 heading \`## R-N -- <title>\`` → `H2 heading \`## R-1 — <title>\`` (digit-bearing example, em-dash separator). The R-1 / R-2 entries below L3 are unchanged (they already use the canonical form). *(Critic M2: third documentation surface; in-scope this slice.)*
- `tests/methodology/test_risk_register_audit.py`: 3 new test functions appended after the existing skill-prose-pin block (currently around L296–L320):
  - `test_docstring_format_examples_match_actual_regex` (AC #1) — extracts H2-shaped headings from the module docstring; runs each through `_RISK_HEADING_RE.match(...)`; asserts each matches.
  - `test_inline_regex_comment_examples_match_actual_regex` (AC #2) — reads the `tools/risk_register_audit.py` source, locates the inline comment immediately above `_RISK_HEADING_RE = re.compile(...)`, extracts every `"..."`-quoted (Python string) AND `` `...` ``-quoted (markdown code-span) heading shape; runs each through `_RISK_HEADING_RE.match(...)`; asserts each matches. *(Critic M3: extraction widened beyond `"..."`-only.)*
  - `test_risk_register_md_schema_description_examples_match_actual_regex` (AC #3) — reads `architecture/risk-register.md`, scans the prelude prose (lines BEFORE the first `## R-` heading) for `` ` ``-quoted heading shapes, runs each through `_RISK_HEADING_RE.match(...)`, asserts each matches. *(Critic M2: regression guard for the third surface.)*
- `tests/methodology/test_risk_register_audit_real_file.py`: 1 new **regression-guard** test function appended (NOT a TF-1 row per Critic M1 — invariant assertion, not behavior-delivery):
  - `test_slice_004_no_regression_in_existing_risk_register` — runs the real-file audit on `architecture/risk-register.md`, asserts R-1 returns `score=6 band=high` and R-2 returns `score=2 band=low` (current observed values; locked as the regression-guard snapshot). Lives outside the test-first plan tracker; mission-brief verification-plan calls it out separately.
- `architecture/decisions/ADR-003-rr1-fix-docs-not-regex.md`: records the choice of "fix docs, keep regex strict" over the 3 alternatives (widen regex; tighten regex to em-dash only; hybrid widen + deprecation hint).

## What's reused

- [[ADR-002]] — sets the precedent for "additive enhancement, no breaking change" decisions; slice-004 follows the same shape (no breaking behavior change; documentation accuracy)
- `tools/risk_register_audit.py:56` (`_RISK_HEADING_RE`) — kept unchanged; this is the source of truth the docstring/comment now align with
- `tools/risk_register_audit.py` legacy-format hint pattern (`--warn-legacy`, L29–L31) — reused conceptually only, NOT extended to the `--`-vs-em-dash case in this slice (out of scope per mission brief; would be the option-C "hybrid" path deferred)
- Existing `_RISK_HEADING_RE` semantics: accepts em-dash `—` OR single hyphen `-` between the ID and the title
- Existing test fixtures in `tests/methodology/fixtures/risk_register/` (`clean_register.md`, `all_retired.md`, etc.) — all use em-dash; unchanged
- Existing 31+ tests in `tests/methodology/test_risk_register_audit.py` and 7+ tests in `tests/methodology/test_risk_register_audit_real_file.py` — unchanged; must remain green
- Existing `architecture/risk-register.md` R-1 + R-2 entries — both use em-dash; unchanged

## Components touched

### `tools/risk_register_audit.py` (modified — documentation only)
- **Responsibility**: Validates and ranks the project's risk-register entries per RR-1 schema. Used by `/slice` (top-N candidates) and `/status` (top-N concerns).
- **Lives at**: `tools/risk_register_audit.py`
- **Key interactions**:
  - Reads `architecture/risk-register.md` (or any path passed as argv[1])
  - Called by `skills/slice/SKILL.md` Step 1 invocation `$PY -m tools.risk_register_audit ... --json --filter-status open --sort score --top 5`
  - Called by `skills/status/SKILL.md` for top-N risk surfacing
  - Tested by `tests/methodology/test_risk_register_audit.py` + `tests/methodology/test_risk_register_audit_real_file.py`
- **Slice-004 change**: no behavior change. Two documentation surfaces — the module docstring's "Format" section AND the inline comment immediately above `_RISK_HEADING_RE` — are corrected to accurately describe the regex's actual accepted formats. Regex is untouched.

### `tests/methodology/test_risk_register_audit.py` (modified)
- **Responsibility**: Unit + integration tests for `tools/risk_register_audit.py` (~31 existing tests).
- **Lives at**: `tests/methodology/test_risk_register_audit.py`
- **Key interactions**: Imports `from tools.risk_register_audit import ...`. Uses fixtures from `tests/methodology/fixtures/risk_register/`.
- **Slice-004 change**: 2 new test functions appended for AC #1 + AC #2.

### `tests/methodology/test_risk_register_audit_real_file.py` (modified)
- **Responsibility**: Real-file integration test against `architecture/risk-register.md`. Locked as slice-002's shippability entry.
- **Lives at**: `tests/methodology/test_risk_register_audit_real_file.py`
- **Slice-004 change**: 1 new regression-guard test function appended (NOT a TF-1 row per Critic M1).

### `architecture/risk-register.md` (modified — L3 prose only) *(Critic M2 in-scope extension)*
- **Responsibility**: User-facing risk register; the artifact users actually edit when adding new risks. Its opening prose at L3 includes the canonical heading-shape example.
- **Lives at**: `architecture/risk-register.md`
- **Key interactions**: Read by users; parsed by `tools/risk_register_audit.py` (only the H2 entries below the prelude; the prelude prose itself is ignored by the audit but read by humans).
- **Slice-004 change**: L3 only. Replace `## R-N -- <title>` (double-dash, single-letter ID) with `## R-1 — <title>` (em-dash, digit-bearing ID) and a parenthetical clarifying the accepted-vs-rejected separator forms. R-1 + R-2 H2 entries below are unchanged.

## Contracts added or changed

None. Slice-004 makes no public-API or CLI changes. The audit's CLI surface (`--json`, `--filter-status`, `--sort`, `--top`, `--warn-legacy`) is unchanged. The Python API (`audit_register`, `Risk` dataclass, etc.) is unchanged. Output shape is identical pre/post slice (verified by AC #3).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Zero new modules — only modifications to three existing files (`tools/risk_register_audit.py`, `tests/methodology/test_risk_register_audit.py`, `tests/methodology/test_risk_register_audit_real_file.py`). Empty matrix per WIRE-1 zero-row clean convention.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-003-rr1-fix-docs-not-regex]] — choose to fix the docstring + inline comment to match `_RISK_HEADING_RE`'s actual behavior (rather than widen the regex to accept `--` OR tighten to em-dash only OR add a deprecation hint hybrid) — reversibility: **cheap**

## Authorization model for this slice

N/A — `tools/risk_register_audit.py` is a methodology audit with no auth surface. Runs as the invoking user; reads + validates a single markdown file; no multi-tenant / multi-user concerns.

## Error model for this slice

No new error paths introduced. The existing audit error paths (malformed field block → violation; duplicate risk ID → violation; invalid status/level value → violation; legacy table format with `--warn-legacy` → deprecation violation) are unchanged.

The slice does NOT add an error path for `--`-shaped headings — that's the option-C "hybrid" approach explicitly NOT chosen here per ADR-003. Today's silent-zero-risks behavior on `--`-shaped headings persists; the fix is documenting clearly that em-dash (or single hyphen) is required, NOT making `--` produce an explicit error. Future slice can revisit if the UX pain recurs.

## Implementation sketch

The fix is small. Three localized edits:

### 1. `tools/risk_register_audit.py` docstring (currently L17–L27)

Before:
```python
Format (H2-structured, matching BC-1 / TRI-1 conventions):

    ## R-NN -- <title>

    **Likelihood**: low | medium | high
    ...
```

After (digit-bearing example per Critic B1 — `R-NN` doesn't match `R-?\d+`):
```python
Format (H2-structured, matching BC-1 / TRI-1 conventions):

    ## R-1 — <title>

    **Likelihood**: low | medium | high
    ...

The separator between the risk ID and the title is em-dash `—` (canonical
per slice-002 lessons-learned) OR single hyphen `-` (accepted alternate
form). Double-hyphen `## R-1 -- <title>` is NOT accepted — the regex
character class is single-character.
```

The negative-counterexample sentence (`Double-hyphen \`## R-1 -- <title>\` is NOT accepted`) is in continuous paragraph prose, NOT on its own line. AC #1's extraction `line.strip().startswith("## R-")` reads stripped lines from the docstring; this sentence's stripped form starts with `Double-hyphen` (not `## R-`), so it isn't picked up. *(Critic B1's option-c hardening: keep negative counterexamples inside backtick spans within continuous prose, never as a line's leading non-whitespace token.)*

### 2. `tools/risk_register_audit.py` inline comment (currently L55)

Before:
```python
# H2 risk heading: "## R-NN -- title" or "## R-NN — title" (em dash)
_RISK_HEADING_RE = re.compile(r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$")
```

After (digit-bearing examples per Critic B1):
```python
# H2 risk heading: "## R-1 — title" (em-dash separator, canonical) or
# "## R-1 - title" (single hyphen, accepted alternate). Double-hyphen
# "--" is NOT accepted — the regex character class [—\-] is single-character.
_RISK_HEADING_RE = re.compile(r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$")
```

### 3. `architecture/risk-register.md` L3 opening description (per Critic M2)

Before:
```markdown
Active risks discovered during slice work. Each entry follows the **RR-1** schema (`tools/risk_register_audit.py`): H2 heading `## R-N -- <title>`, with required fields ...
```

After (digit-bearing example, em-dash separator):
```markdown
Active risks discovered during slice work. Each entry follows the **RR-1** schema (`tools/risk_register_audit.py`): H2 heading `## R-1 — <title>` (em-dash separator, canonical; single hyphen `-` also accepted; double-hyphen `--` is NOT accepted — the regex is single-character), with required fields ...
```

### 3. New tests in `tests/methodology/test_risk_register_audit.py`

```python
def test_docstring_format_examples_match_actual_regex():
    """Module docstring's 'Format' section heading example matches _RISK_HEADING_RE.

    Defect class: slice-002 hit silent 0-risks because the docstring
    showed `## R-NN -- <title>` (double-dash; ALSO `R-NN` letters not
    digits) but the regex required `R-?\\d+` AND single-character
    separator. This test guards against future drift in either
    direction.
    Slice-004 AC #1.
    Rule reference: RR-1.
    """
    import inspect
    from tools.risk_register_audit import _RISK_HEADING_RE
    import tools.risk_register_audit as audit_module

    docstring = inspect.getdoc(audit_module) or ""
    # Find every line in the docstring that looks like an H2 risk heading example.
    # `inspect.getdoc()` dedents per PEP 257; the indented "Format" example
    # block becomes flush after stripping. The negative counterexample
    # (`## R-1 -- <title>`) appears INSIDE backticks within continuous
    # paragraph prose — never as a line's leading non-whitespace token —
    # so it's not picked up by `startswith("## R-")` after `.strip()`.
    candidates = [
        line.strip()
        for line in docstring.splitlines()
        if line.strip().startswith("## R-")
    ]
    assert candidates, "no `## R-...` heading example found in docstring"
    for heading in candidates:
        assert _RISK_HEADING_RE.match(heading), (
            f"docstring example heading {heading!r} does NOT match "
            f"_RISK_HEADING_RE — docstring/regex contradiction (the "
            f"slice-002 silent-zero-risks bug). Common causes: letter "
            f"placeholder like `R-NN` (regex requires R-?\\d+); "
            f"double-hyphen `--` (regex character class is single-char)."
        )


def test_inline_regex_comment_examples_match_actual_regex():
    """Inline comment above _RISK_HEADING_RE shows only formats the regex actually accepts.

    Coverage: extracts BOTH "..."-quoted (Python string literal
    convention) AND `...`-quoted (markdown code-span convention)
    heading shapes from the immediately-adjacent `#`-prefixed comment
    block above the regex.

    Known coverage gap (Critic M3): unquoted prose examples like
    `# Also accepts ## R-1 — title` (no quotes) silently bypass this
    test. If a future maintainer adds an unquoted example, the test
    won't catch a `--`-vs-em-dash mismatch in that example. Acceptable
    trade-off: tightening to also catch unquoted shapes risks false
    positives on comment lines that happen to mention `## R-` in
    non-example contexts. Address in a follow-on slice if drift recurs.

    Slice-004 AC #2.
    Rule reference: RR-1.
    """
    import re as re_module
    from pathlib import Path
    from tools.risk_register_audit import _RISK_HEADING_RE

    src = Path(
        REPO_ROOT / "tools" / "risk_register_audit.py"
    ).read_text(encoding="utf-8")

    # Find the line containing `_RISK_HEADING_RE = re.compile(`.
    lines = src.splitlines()
    target_idx = None
    for i, line in enumerate(lines):
        if "_RISK_HEADING_RE = re.compile(" in line:
            target_idx = i
            break
    assert target_idx is not None, "_RISK_HEADING_RE assignment line not found"

    # Walk backwards over consecutive `#` comment lines to gather the inline doc block.
    # NOTE: stops at the first non-`#`-prefixed line. Multi-block comments
    # separated by a blank line would have only the immediate block scanned.
    # That's intentional scoping — the test inspects what's adjacent to the
    # regex, not arbitrary upstream documentation.
    comment_lines = []
    j = target_idx - 1
    while j >= 0 and lines[j].lstrip().startswith("#"):
        comment_lines.insert(0, lines[j])
        j -= 1
    assert comment_lines, "no inline comment found above _RISK_HEADING_RE"

    comment_blob = "\n".join(comment_lines)
    # Extract every `## R-...`-shaped example, whether double-quoted or
    # backtick-quoted. Per Critic M3: backtick-quoted is markdown
    # convention; covering both shapes catches more realistic drift.
    quoted_examples = re_module.findall(r'[`"](## R-[^`"]+)[`"]', comment_blob)
    assert quoted_examples, (
        f"no `## R-...` quoted example found in inline comment block:\n"
        f"{comment_blob!r}"
    )
    for heading in quoted_examples:
        assert _RISK_HEADING_RE.match(heading), (
            f"inline-comment example heading {heading!r} does NOT match "
            f"_RISK_HEADING_RE — inline-comment/regex contradiction."
        )


def test_risk_register_md_schema_description_examples_match_actual_regex():
    """architecture/risk-register.md prelude prose's heading shape examples match _RISK_HEADING_RE.

    Defect class (Critic M2): the user-facing risk-register.md file's
    OPENING DESCRIPTION PROSE — the prelude before the first `## R-`
    heading — is the third documentation surface (after the audit's
    docstring + inline comment). Today it shows `## R-N -- <title>`
    (double-dash; ALSO `R-N` is a single letter, not `\\d+`). A user
    reading this file follows the example, types the same shape into
    a new entry, runs the audit, gets silent 0-risks. This test
    enforces the prelude prose stays consistent with the audit's
    behavior.

    Coverage: scans LINES BEFORE the first `## R-` heading (the
    prelude); extracts backtick-quoted `## R-...` shapes; runs each
    through _RISK_HEADING_RE.match; asserts each matches.

    Slice-004 AC #3.
    Rule reference: RR-1.
    """
    import re as re_module
    from tools.risk_register_audit import _RISK_HEADING_RE

    register_path = REPO_ROOT / "architecture" / "risk-register.md"
    text = register_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # The prelude is everything before the first H2 risk heading.
    prelude_end = None
    for i, line in enumerate(lines):
        if line.startswith("## R-") or line.startswith("## R"):
            prelude_end = i
            break
    assert prelude_end is not None, "no `## R-...` heading found in risk-register.md"
    prelude = "\n".join(lines[:prelude_end])

    # Extract every backtick-quoted `## R-...` shape.
    quoted_examples = re_module.findall(r'`(## R-[^`]+)`', prelude)
    assert quoted_examples, (
        f"no backtick-quoted `## R-...` example found in risk-register.md "
        f"prelude:\n{prelude!r}"
    )
    for heading in quoted_examples:
        assert _RISK_HEADING_RE.match(heading), (
            f"risk-register.md prelude example {heading!r} does NOT match "
            f"_RISK_HEADING_RE — user-facing schema documentation "
            f"contradicts the audit's actual behavior."
        )
```

### 4. Regression-guard test in `tests/methodology/test_risk_register_audit_real_file.py`

Per Critic M1: this is a regression-guard, NOT a TF-1 row. It asserts an invariant (R-1/R-2 parsing unchanged) that can't legitimately reach WRITTEN-FAILING because the slice deliberately makes no behavior change. Lives outside the test-first plan tracker; mission-brief verification-plan calls it out separately.

```python
def test_slice_004_no_regression_in_existing_risk_register():
    """slice-004's docstring/comment/risk-register.md changes don't change R-1 / R-2 parsing.

    Regression-guard invariant (NOT a TF-1 AC row): existing em-dash
    entries return identical scores+bands pre/post slice-004. If a
    future slice changes regex behavior in a way that affects scoring,
    this test fails loudly rather than silently shifting risk rankings.
    Slice-004 must-not-defer item.
    Rule reference: RR-1.
    """
    from tools.risk_register_audit import audit_register

    result = audit_register(REPO_ROOT / "architecture" / "risk-register.md")
    by_id = {r.risk_id: r for r in result.risks}
    assert "R-1" in by_id, "R-1 missing from risk-register parse"
    assert "R-2" in by_id, "R-2 missing from risk-register parse"
    assert by_id["R-1"].score == 6 and by_id["R-1"].band == "high", (
        f"R-1 expected score=6 band=high; got "
        f"score={by_id['R-1'].score} band={by_id['R-1'].band}"
    )
    assert by_id["R-2"].score == 2 and by_id["R-2"].band == "low", (
        f"R-2 expected score=2 band=low; got "
        f"score={by_id['R-2'].score} band={by_id['R-2'].band}"
    )
```

(Test file imports / `audit_register` symbol name to be confirmed at build-time when the test is actually appended; if `audit_register` is not the public function, swap to whichever is — existing real-file test is the reference.)

## Testing strategy

**3 TF-1 rows** mapped 1-to-1 from the test-first plan in mission-brief.md, plus **1 regression-guard test** outside the TF-1 tracker (per Critic M1):

- **AC #1** — 1 unit test (`test_docstring_format_examples_match_actual_regex`). Failing pre-fix because today's docstring contains `## R-NN -- <title>` which doesn't match `_RISK_HEADING_RE` (both `R-NN` letters fail `R-?\d+` AND `--` two-character fails the single-character class). Post-fix, docstring contains `## R-1 — <title>` which matches.
- **AC #2** — 1 unit test (`test_inline_regex_comment_examples_match_actual_regex`). Failing pre-fix because today's inline comment contains the quoted example `"## R-NN -- title"` which doesn't match `_RISK_HEADING_RE`. Post-fix, the comment contains `"## R-1 — title"` and `"## R-1 - title"`, both of which match. **Critic M3 hardening**: extraction widened to catch BOTH `"..."`-quoted (Python convention) AND `` `...` ``-quoted (markdown convention) shapes.
- **AC #3** — 1 unit test (`test_risk_register_md_schema_description_examples_match_actual_regex`). Failing pre-fix because today's `architecture/risk-register.md:3` contains `` `## R-N -- <title>` `` which doesn't match `_RISK_HEADING_RE` (both `R-N` single letter AND `--` two-character fail). Post-fix, L3 contains `` `## R-1 — <title>` `` which matches. **Critic M2**: third surface — the user-facing one — now covered.

All 3 TF-1 rows progress PENDING → WRITTEN-FAILING (immediately after the new tests are committed; before any docstring/comment/risk-register edits) → PASSING (after the three documentation surfaces are corrected). `tools/test_first_audit.py --strict-pre-finish` enforces all 3 PASSING at pre-finish.

**Regression-guard test outside TF-1** (`test_slice_004_no_regression_in_existing_risk_register` in `tests/methodology/test_risk_register_audit_real_file.py`): asserts R-1.score=6/band=high + R-2.score=2/band=low. Per Critic M1, this is an invariant assertion not a behavior delivery — it cannot legitimately reach WRITTEN-FAILING because the slice deliberately makes no regex change. Lives in the verification-plan + must-not-defer sections of mission-brief.md, NOT in the TF-1 test-first table. Test passes from creation (regex unchanged + R-1/R-2 entries unchanged); continues to pass post-slice. Functions as a regression detector if a future slice inadvertently changes parsing behavior.

## Reflection-corrected notes

(none — this is the initial design pre-build; if `/build-slice` discovers something this design got wrong, the deviation goes in `build-log.md` and a "Reflection-corrected" note appended here.)
