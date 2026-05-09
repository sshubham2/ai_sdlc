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
