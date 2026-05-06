"""Verify COST-1.1 — per-pass model assignment in /diagnose Step 5.

Per COST-1.1 (methodology-changelog.md v0.5.0), each of the 11 /diagnose
passes has an explicit model assignment in skills/diagnose/SKILL.md Step 5:
Sonnet for extraction-shaped passes (reachability + grep + classification),
Opus for reasoning-shaped passes (synthesis + judgment + cross-module analysis).

Rule reference: COST-1.1.
"""
import re

from tests.methodology.conftest import read_file

DIAGNOSE = read_file("skills/diagnose/SKILL.md")

# Cognitive-shape analysis from the changelog. Sonnet for extraction work,
# Opus for reasoning work. The 04-ai-bloat pass is dispatched in Step 6
# separately, so it is not in this table.
EXPECTED_MODELS = {
    "01-intent": "opus",
    "02-architecture": "opus",
    "03a-dead-code": "sonnet",
    "03b-duplicates": "opus",
    "03c-size-outliers": "sonnet",
    "03d-half-wired": "opus",
    "03e-contradictions": "opus",
    "03f-layering": "sonnet",
    "03g-dead-config": "sonnet",
    "03h-test-coverage": "sonnet",
}


def test_diagnose_step_5_has_model_column():
    """Step 5 dispatch table must include a Model column.

    Defect class: Without an explicit Model column, executors run all 11
    passes on the main-thread default (typically Opus), wasting budget on
    extraction-shaped work that Sonnet handles equivalently.
    Rule reference: COST-1.1.
    """
    assert "| Model |" in DIAGNOSE, (
        "skills/diagnose/SKILL.md Step 5 has no `| Model |` column header"
    )


def test_diagnose_references_cost_1_1_rule():
    """Step 5 prose must cross-reference the COST-1.1 rule.

    Defect class: Rule changes that aren't traceable to the changelog can't
    be evaluated for impact. A `COST-1.1` reference lets readers trace
    rationale.
    Rule reference: COST-1.1.
    """
    assert "COST-1.1" in DIAGNOSE, "no COST-1.1 reference found in /diagnose SKILL.md"


def test_each_pass_has_explicit_model_assignment():
    """Every pass row must name its assigned model.

    Defect class: Missing model on a row means that pass falls back to the
    main-thread default. Per-pass dispatch breaks down silently for any
    pass without an explicit model.
    Rule reference: COST-1.1.
    """
    for pass_name, expected_model in EXPECTED_MODELS.items():
        # Match a row like: | <pass-name> | <template-cell> | <model> | <rationale> |
        # The middle cell may contain backticks; [^\|]* matches non-pipe chars.
        pattern = rf"\|\s*{re.escape(pass_name)}\s*\|[^\|]*\|\s*{expected_model}\s*\|"
        assert re.search(pattern, DIAGNOSE), (
            f"Pass {pass_name} missing or wrong model assignment "
            f"(expected `{expected_model}` in Step 5 dispatch table)"
        )


def test_extraction_passes_run_on_sonnet():
    """Sanity check: at least the 5 extraction-shaped passes are on Sonnet.

    Defect class: Drift toward "everything on Opus to be safe" undoes the
    optimization. Pinning the extraction-passes-on-Sonnet count prevents
    silent regressions.
    Rule reference: COST-1.1.
    """
    sonnet_passes = [name for name, model in EXPECTED_MODELS.items() if model == "sonnet"]
    assert len(sonnet_passes) >= 5, (
        f"Expected ≥5 extraction-shaped passes on Sonnet; got {len(sonnet_passes)}: "
        f"{sonnet_passes}"
    )


def test_reasoning_passes_run_on_opus():
    """Sanity check: reasoning-shaped passes stay on Opus.

    Defect class: Drift toward "everything on Sonnet to save more" trades
    quality on the synthesis-heavy passes (intent, architecture, semantic
    duplicates, half-wired, contradictions) for cost — wrong direction.
    Pinning the reasoning-passes-on-Opus count prevents that drift.
    Rule reference: COST-1.1.
    """
    opus_passes = [name for name, model in EXPECTED_MODELS.items() if model == "opus"]
    assert len(opus_passes) >= 5, (
        f"Expected ≥5 reasoning-shaped passes on Opus; got {len(opus_passes)}: "
        f"{opus_passes}"
    )
