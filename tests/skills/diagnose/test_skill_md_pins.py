"""Prose pins for skills/diagnose/SKILL.md (slice-001 + slice-002).

These tests assert specific phrases appear (or don't) in SKILL.md and
the 11 pass templates so that future edits don't silently regress the
behaviors encoded by ACs and dispositions.

Rule references:
- slice-001: ACs #1, #5, dispositions M3, m3
- slice-002: ACs #1, #2, #4, dispositions M1, M2, M4 (cwd-mismatch
  documentation, Step 5 contract relaxation, byte-equality of contract
  string across SKILL.md + 11 pass templates, negative regression guard)
"""
from pathlib import Path

from tests.skills.diagnose.conftest import REPO_ROOT, SKILL_DIR

SKILL_MD = SKILL_DIR / "SKILL.md"
PASSES_DIR = SKILL_DIR / "passes"

# Canonical contract string locked by slice-002 / triage M2.
# This MUST appear byte-for-byte at the listed sites (SKILL.md Step 5
# contract bullet + each of the 11 pass templates' Output format
# section). The byte-equality test is the regression guard.
SLICE_002_CANONICAL_CONTRACT = (
    "**Do NOT call Write to produce output files (the orchestrator "
    "handles that). You MAY use Bash/python for graphify queries within "
    "$OUT/graphify-out/, and Read/Grep/Glob for source files within "
    "$TARGET.**"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- AC #5: graphify flag ---


def test_skill_md_uses_out_not_output():
    """SKILL.md graphify command uses --out, not --output.

    Defect class: 2026-05-09 issue 4 — `--output` is wrong; the actual
    graphify CLI flag is `--out`.
    Disposition ref: AC #5.
    """
    text = _read(SKILL_MD)
    # The graphify code invocation must use --out
    assert "graphify code" in text, "SKILL.md must invoke graphify code"
    # No --output anywhere in SKILL.md (it's not a valid graphify flag)
    assert "--output" not in text, (
        "SKILL.md uses --output (invalid graphify flag); should be --out"
    )


def test_no_pass_template_uses_output_flag():
    """No pass template under passes/ uses --output (regression guard).

    Defect class: per AC #5 + M5, pass templates currently use --graph
    rather than --output, so this trivially holds today. Test exists as a
    regression guard so a future edit doesn't introduce the wrong flag.
    Disposition ref: AC #5.
    """
    for path in sorted(PASSES_DIR.glob("*.md")):
        text = _read(path)
        assert "--output" not in text, (
            f"{path.name} uses --output flag; should be --out (or --graph)"
        )


# --- AC #1: write_pass invocation + no-Write contract ---


def test_skill_md_invokes_write_pass():
    """SKILL.md Step 5 invokes write_pass.py per pass.

    Defect class: AC #1 says the orchestrator is the writer; SKILL.md must
    direct main thread to call write_pass.py after each subagent returns.
    Disposition ref: AC #1.
    """
    text = _read(SKILL_MD)
    assert "write_pass.py" in text, (
        "SKILL.md must invoke skills/diagnose/write_pass.py to write pass output"
    )
    assert "--raw-file" in text, (
        "SKILL.md must invoke write_pass.py with --raw-file (stdin not supported)"
    )


def test_skill_md_subagents_instructed_no_write():
    """SKILL.md tells subagents NOT to use Write tool (per critique m3).

    Defect class: per critique m3, the original prose said 'each subagent
    writes 3 files' which is exactly the regression we're fixing. Negative
    assertion: that string must NOT appear; positive assertion: a phrase
    saying subagents must not Write must appear.
    Disposition ref: m3.
    """
    text = _read(SKILL_MD)
    # Negative: the old prose pattern
    assert "writes 3 files" not in text, (
        "SKILL.md still contains the old prose 'writes 3 files'; "
        "subagent contract has not been updated"
    )
    # Positive: an explicit instruction not to use Write
    lower = text.lower()
    assert "do not call write" in lower or "do not use write" in lower or \
           "no write tool" in lower or "must not call write" in lower or \
           "do not write" in lower, (
        "SKILL.md must explicitly tell subagents not to use the Write tool"
    )


# --- M3: bounded retry cap on re-spawn ---


def test_skill_md_caps_respawn_attempts():
    """SKILL.md Step 5 caps re-spawn attempts (per critique M3).

    Defect class: per M3, an unbounded re-spawn loop on a deterministically
    malformed subagent output would loop forever. The skill prose must name
    a numeric cap (3 attempts) and say what happens after.
    Disposition ref: M3.
    """
    text = _read(SKILL_MD)
    lower = text.lower()
    # Some phrasing of "at most 3" or "3 attempts" or "3 total"
    assert ("3 total" in lower or "3 attempts" in lower or
            "at most twice" in lower or "at most 3" in lower or
            "three attempts" in lower or "thrice" in lower), (
        "SKILL.md must name a re-spawn cap (3 attempts / at most twice / etc.)"
    )
    # And: name the failed-raw artifact destination
    assert ".failed.raw" in text or "failed.raw" in text, (
        "SKILL.md must specify where terminally-failed subagent output is "
        "saved (.failed.raw under .tmp/)"
    )


# --- slice-002 / AC #1: Step 1 cwd-must-match documentation + warning ---


def test_skill_md_step1_documents_cwd_constraint():
    """SKILL.md Step 1 documents the cwd-must-match-TARGET pattern.

    Defect class: per slice-001 AC #6 + R1, when TARGET is outside the
    parent thread's cwd, spawned subagents may lose tool access. Slice-002
    documents this in Step 1 prose so users know to `cd $TARGET` first.
    Rule reference: slice-002 AC #1, disposition M1.
    """
    text = _read(SKILL_MD)
    # Locate Step 1 region (between "## Step 1" and "## Step 2")
    step1_start = text.find("## Step 1")
    step2_start = text.find("## Step 2")
    assert step1_start != -1, "SKILL.md must have a `## Step 1` heading"
    assert step2_start != -1 and step2_start > step1_start
    step1 = text[step1_start:step2_start].lower()
    # Some phrasing telling user to cd to TARGET first
    assert ("cd to target" in step1 or "cd $target" in step1 or
            "cd \"$target\"" in step1 or "cwd must match" in step1 or
            "match-target" in step1), (
        "SKILL.md Step 1 must document the cwd-must-match-TARGET pattern "
        "(per slice-002 AC #1)"
    )


def test_skill_md_step1_emits_cwd_mismatch_warning():
    """SKILL.md Step 1 instructs the orchestrator to emit a warning on TARGET ≠ $PWD.

    Defect class: prose-pin protects the warning instruction; without it
    the orchestrator (Claude main thread) has no SKILL-level direction to
    detect the mismatch and warn.
    Rule reference: slice-002 AC #1.
    """
    text = _read(SKILL_MD)
    step1_start = text.find("## Step 1")
    step2_start = text.find("## Step 2")
    assert step1_start != -1 and step2_start != -1
    step1 = text[step1_start:step2_start]
    step1_lower = step1.lower()
    # Both: a warning instruction AND a reference to cwd / PWD / TARGET context
    assert "warning" in step1_lower, (
        "Step 1 must instruct the orchestrator to emit a warning on cwd-mismatch"
    )
    assert ("$pwd" in step1_lower or "pwd" in step1_lower or
            "$target" in step1_lower or "cwd" in step1_lower), (
        "Step 1's warning prose must reference TARGET / $PWD / cwd context"
    )


# --- slice-002 / AC #2: relaxed contract wording ---


def test_skill_md_step5_allows_bash_for_graphify():
    """SKILL.md Step 5 contains the canonical contract string (allows Bash for graphify).

    Defect class: per slice-001 reflection, the legacy "Do NOT call Write,
    Bash, or python" contract was self-contradicting (pass templates'
    Method sections require Bash for graphify queries). Slice-002 relaxes
    this with a single canonical string locked across 12 sites.
    Rule reference: slice-002 AC #2, disposition M2.
    """
    text = _read(SKILL_MD)
    assert SLICE_002_CANONICAL_CONTRACT in text, (
        "SKILL.md Step 5 must contain the byte-equal canonical contract "
        "string (slice-002 M2). Got SKILL.md without the canonical string."
    )


def test_pass_templates_allow_bash_for_graphify():
    """All 11 pass templates' Output format sections contain the canonical contract string.

    Defect class: drift between SKILL.md Step 5 and pass templates is
    exactly the bug slice-001 shipped (legacy phrase in 11 templates'
    Output format sections contradicting their own Method sections).
    Slice-002 locks one canonical string across all 12 sites.
    Rule reference: slice-002 AC #2, disposition M2.
    """
    failures = []
    for path in sorted(PASSES_DIR.glob("*.md")):
        text = _read(path)
        if SLICE_002_CANONICAL_CONTRACT not in text:
            failures.append(path.name)
    assert not failures, (
        f"Pass templates missing the canonical contract string: {failures}"
    )


def test_no_legacy_no_bash_no_python_phrase():
    """Negative pin: the legacy phrase must NOT appear anywhere in skills/diagnose/.

    Defect class: regression guard for slice-002. The legacy contract
    string "Do NOT call Write, Bash, or python" was the source of the
    self-contradiction with pass templates' Method sections; if it
    re-appears anywhere in SKILL.md or pass templates, this test fires.
    Rule reference: slice-002 AC #2.
    """
    LEGACY = "Do NOT call Write, Bash, or python"
    failures = []
    skill_text = _read(SKILL_MD)
    if LEGACY in skill_text:
        failures.append("SKILL.md")
    for path in sorted(PASSES_DIR.glob("*.md")):
        if LEGACY in _read(path):
            failures.append(path.name)
    assert not failures, (
        f"Legacy phrase 'Do NOT call Write, Bash, or python' still present in: "
        f"{failures}. Slice-002 relaxed this contract; the phrase must not recur."
    )


# --- Slice-019 / LAYER-EVID-1 prose pins (AC #1) ---

# Canonical phrase locked by slice-019 / LAYER-EVID-1 across N=3 surfaces.
# Per /critique M1 mitigation: this string is also embedded verbatim in
# Method step 4 prose of 03f-layering.md (visual byte-equality is the
# prose-pin equivalent of CAD-1 byte-equality at the rule-content level).
SLICE_019_CANONICAL_PHRASE = "textual import-evidence requirement"

LAYERING_PASS_TEMPLATE = PASSES_DIR / "03f-layering.md"


def test_skill_md_step5_documents_textual_evidence_rule():
    """SKILL.md Step 5 contains the LAYER-EVID-1 cross-reference paragraph.

    Per slice-019 AC #1 + design.md Surface 2: SKILL.md Step 5 gains a
    NEW paragraph between the "Subagent contract (canonical line)"
    subsection and the "After each subagent returns" subsection,
    cross-referencing the LAYER-EVID-1 rule body (which lives in
    passes/03f-layering.md, not here).

    Defect class: forgetting the cross-reference at SKILL.md means
    the orchestrator may dispatch the 03f-layering subagent without
    surfacing that LAYER-EVID-1 applies; subagent reads pass template
    in isolation; misses the rule body if a future SKILL.md edit
    obscures Step 5's structure.

    Rule reference: LAYER-EVID-1 (slice-019 AC #1, Surface 2 of N=3).
    """
    text = _read(SKILL_MD)
    assert "LAYER-EVID-1" in text, (
        "SKILL.md missing 'LAYER-EVID-1' rule-ID reference — Step 5 "
        "cross-reference paragraph not present"
    )
    assert SLICE_019_CANONICAL_PHRASE in text, (
        f"SKILL.md missing canonical phrase {SLICE_019_CANONICAL_PHRASE!r} — "
        f"Step 5 cross-reference paragraph not present at Surface 2 of N=3"
    )


def test_layering_pass_template_emits_textual_evidence_rule():
    """skills/diagnose/passes/03f-layering.md carries the LAYER-EVID-1
    rule body (Method step 4 + Severity rubric downgrade rule + Anti-patterns
    negative-pin).

    Per slice-019 AC #1 + design.md Surface 1: 03f-layering.md is the
    PRIMARY carrier of the rule body. SKILL.md only cross-references; the
    actual prose lives here.

    Defect class: forgetting to update 03f-layering.md after promising
    LAYER-EVID-1 at SKILL.md + methodology-changelog leaves the subagent
    reading an old pass template that doesn't apply the rule.

    Rule reference: LAYER-EVID-1 (slice-019 AC #1, Surface 1 of N=3 —
    the PRIMARY carrier).
    """
    text = _read(LAYERING_PASS_TEMPLATE)
    assert "LAYER-EVID-1" in text, (
        "passes/03f-layering.md missing 'LAYER-EVID-1' rule-ID reference"
    )
    assert SLICE_019_CANONICAL_PHRASE in text, (
        f"passes/03f-layering.md missing canonical phrase "
        f"{SLICE_019_CANONICAL_PHRASE!r}"
    )
    # Method step 4 marker — proves the rule body lives inside Method
    assert "Grep-verify the import statement" in text, (
        "passes/03f-layering.md Method section missing 'Grep-verify the "
        "import statement' marker — Method step 4 body not present"
    )
    # Anti-patterns negative-pin marker
    assert "graphify edges for HIGH-severity boundary findings without textual" in text, (
        "passes/03f-layering.md Anti-patterns section missing the "
        "LAYER-EVID-1 negative-pin bullet"
    )


def test_textual_evidence_rule_byte_equal_across_n_3_surfaces():
    """The canonical phrase `textual import-evidence requirement` MUST appear
    byte-equal across all N=3 in-repo surfaces AND all N=3 installed
    surfaces (bidirectional N=6 total).

    Per slice-019 AC #1: N=3 surfaces are
    (Surface 1) skills/diagnose/passes/03f-layering.md,
    (Surface 2) skills/diagnose/SKILL.md (Step 5 cross-reference),
    (Surface 3) methodology-changelog.md v0.33.0 entry.
    Each surface has a bidirectional in-repo ↔ installed pair (mini-CAD
    + methodology-changelog forward-sync per slice-018 N=14 -> N=15
    forensic capture).

    Defect class: partial forward-sync (e.g., updates in-repo but forgets
    one of the installed copies) silently breaks the N-surface pin and
    leaves /diagnose runtime reading stale prose.

    Rule reference: LAYER-EVID-1 (slice-019 AC #1, byte-equality across
    N=6 surfaces).
    """
    from pathlib import Path

    installed_diagnose = Path.home() / ".claude" / "skills" / "diagnose"
    installed_changelog = Path.home() / ".claude" / "methodology-changelog.md"

    surfaces = {
        "in-repo 03f-layering.md":     LAYERING_PASS_TEMPLATE,
        "in-repo SKILL.md":            SKILL_MD,
        "in-repo methodology-changelog.md": REPO_ROOT / "methodology-changelog.md",
        "installed 03f-layering.md":   installed_diagnose / "passes" / "03f-layering.md",
        "installed SKILL.md":          installed_diagnose / "SKILL.md",
        "installed methodology-changelog.md": installed_changelog,
    }

    missing = []
    for name, path in surfaces.items():
        if not path.exists():
            missing.append(f"{name} (file not found at {path})")
            continue
        text = path.read_text(encoding="utf-8")
        if SLICE_019_CANONICAL_PHRASE not in text:
            missing.append(name)

    assert not missing, (
        f"Canonical phrase {SLICE_019_CANONICAL_PHRASE!r} missing from "
        f"N-surface schema-pin at: {missing}. All 6 surfaces (3 in-repo + "
        f"3 installed) must carry the byte-equal phrase. Likely cause: "
        f"forgotten forward-sync after in-repo edit."
    )


def test_pass_templates_match_skill_md_step5_contract():
    """Byte-equality: canonical contract string MUST appear identically in 12 sites.

    Defect class: per slice-002 critique M2, the slice-001 lesson "the
    contract was authoritative in SKILL.md and copied verbatim into
    templates" must be preserved. Drift = test fails. The byte-equality
    constraint catches partial-edits (someone edits SKILL.md's contract
    but forgets one or more pass templates).
    Rule reference: slice-002 disposition M2.
    """
    skill_text = _read(SKILL_MD)
    assert skill_text.count(SLICE_002_CANONICAL_CONTRACT) >= 1, (
        "SKILL.md must contain the canonical contract string at least once "
        "(in Step 5's contract bullet)"
    )
    template_misses = []
    for path in sorted(PASSES_DIR.glob("*.md")):
        if SLICE_002_CANONICAL_CONTRACT not in _read(path):
            template_misses.append(path.name)
    assert not template_misses, (
        f"Byte-equality fails: pass templates with NO match for canonical "
        f"string: {template_misses}. Edit them to match SKILL.md verbatim."
    )


# --- Slice-029 / sequential-dispatch-default prose pins (ADR-027) ---
#
# These pin the four behaviors slice-029 introduces. They are NEW pins;
# the slice-001/002/019 pins above (incl. CSP-1 byte-equality + the
# LAYER-EVID-1 N=6 pin) are deliberately left unmodified — they are the
# regression guard for the Step-5 rewrite. Rule reference: ADR-027
# (no rule-ID minted — TRI-1 M2 option B / slice-002 prose-pin precedent).


def test_skill_md_step5_dispatch_is_sequential_by_default():
    """SKILL.md Step 5 makes one-Agent-call-per-message sequential the default.

    Defect class: ADR-027 / slice-029 AC1 — the prior single-message
    multi-Agent parallel batch triggered the R-1 / claude-code #57037
    cascade. The default path MUST now be sequential; a future edit that
    silently restores the parallel default re-exposes every default run.
    """
    text = _read(SKILL_MD)
    assert "Step 5 — Dispatch the analysis passes (sequential by default" in text, (
        "Step 5 heading must declare sequential-by-default dispatch"
    )
    lower = text.lower()
    assert "one `agent` call per message, one at a time" in lower, (
        "Step 5 must describe the sequential one-Agent-call-per-message loop"
    )
    assert "`$parallel` = 0" in lower or "$parallel = 0" in lower, (
        "Step 5 must gate the default sequential path on $PARALLEL = 0"
    )
    # The R-1 / #57037 rationale must be present so the 'why' can't be lost.
    assert "#57037" in text and "R-1" in text, (
        "Step 5 must cite R-1 / claude-code #57037 as the sequential-default rationale"
    )


def test_skill_md_documents_parallel_optin():
    """`--parallel` opt-in is documented in argument-hint AND Step 5.

    Defect class: slice-029 AC2 — the fast path must remain reachable via
    an explicit, discoverable opt-in. If argument-hint or the Step-5
    opt-in branch is dropped, users lose the documented escape hatch.
    """
    text = _read(SKILL_MD)
    # Frontmatter argument-hint region (between the two leading '---').
    fm_end = text.find("---", 3)
    frontmatter = text[:fm_end] if fm_end != -1 else text
    assert "--parallel" in frontmatter and "argument-hint" in frontmatter, (
        "frontmatter argument-hint must document the --parallel flag"
    )
    lower = text.lower()
    assert "opt-in — parallel batch" in lower, (
        "Step 5 must carry the explicit `--parallel` opt-in branch"
    )
    assert "/diagnose --parallel" in text, (
        "Step 5/Step 1 must show the `/diagnose --parallel` invocation"
    )


def test_skill_md_step1_flag_strip_fail_safe():
    """Step 1 strips flags before TARGET resolution and fail-safes unknown flags.

    Defect class: slice-029 B3 + /critique-review M-add-1 — the prior
    `TARGET="${1:-$PWD}"` made `/diagnose --parallel` resolve TARGET to
    `--parallel` and abort. The 3-arm case must: consume `--parallel`,
    WARN+IGNORE any other `--`-flag (never treat it as the path, so a
    flag typo never aborts), and only take a non-flag token as the path.
    """
    text = _read(SKILL_MD)
    step1 = text[text.find("## Step 1"):text.find("## Step 2")]
    assert "--parallel)  PARALLEL=1" in step1, (
        "Step 1 must consume --parallel via the case arm"
    )
    assert '--*)' in step1 and "unknown flag" in step1.lower(), (
        "Step 1 must WARN+IGNORE unknown --flags (the --* case arm)"
    )
    assert 'TARGET="${ARGS[0]:-$PWD}"' in step1, (
        "Step 1 must resolve TARGET from the flag-stripped ARGS residue"
    )
    assert "never treated as the path" in step1.lower(), (
        "Step 1 must state an unknown flag is never treated as the path "
        "(fail-safe — a flag typo never aborts)"
    )


def test_skill_md_step55_dispatch_aware_with_early_exit():
    """Step 5.5 is dispatch-mode-aware and carries the sequential early-exit guard.

    Defect class: slice-029 B1 + /critique-review confirm — the prior
    'After the parallel batch completes' opening was false on the
    sequential default; and an interrupted sequential loop leaves
    un-spawned (not failed) passes. Step 5.5 must handle both: not assume
    a parallel batch, and never silently skip to Step 6 with <10 passes.
    """
    text = _read(SKILL_MD)
    s55 = text[text.find("### Step 5.5"):text.find("## Step 6")]
    assert "sequentially by default" in s55.lower(), (
        "Step 5.5 opening must be dispatch-mode-aware (not 'after the "
        "parallel batch completes')"
    )
    assert "sequential early-exit" in s55.lower(), (
        "Step 5.5 must carry the sequential early-exit silent-gap guard"
    )
    assert "never silently skip to step 6" in s55.lower(), (
        "Step 5.5 early-exit guard must forbid skipping to Step 6 with "
        "fewer than 10 passes attempted"
    )
