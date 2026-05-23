"""Pins the agents/code-review.md agent prompt (CRSI-1; slice-060).

Asserts:
- All 9 dimensions reframed for CODE are present (with the canonical names
  + the design→code substitution evidence per design.md L277-293 table).
- Read-only tools pinned (positive + negative substring per slice-007 M2 /
  slice-053 M-add-4 pattern).
- Specificity rule `path/to/file.py:line` present (inherited from
  agents/critique.md specificity discipline).

Rule reference: CRSI-1 (methodology-changelog.md v0.64.0; slice-060; ADR-059).
"""
from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AGENT_MD = _REPO_ROOT / "agents" / "code-review.md"


def _read() -> str:
    assert _AGENT_MD.exists(), f"missing {_AGENT_MD}"
    return _AGENT_MD.read_text(encoding="utf-8")


def test_agent_md_contains_nine_dimensions_against_code():
    """agents/code-review.md must enumerate all 9 dimensions reframed for
    CODE (per design.md L277-293 "9 dimensions reframed for code" table).

    Per /critique M1 + slice-051 / slice-037 M-add-1 content-bearing-pin
    discipline: assert specific substrings from the reframed prose, not
    just dimension names (a dimension-name-only check is tautologically
    green if the agent's body becomes empty).
    """
    body = _read()
    # All 9 dimension names present as headings
    dims = [
        "### 1. Unfounded assumptions",
        "### 2. Missing edge cases",
        "### 3. Over-engineering",
        "### 4. Under-engineering",
        "### 5. Contract gaps",
        "### 6. Security",
        "### 7. Drift from vault",
        "### 8. Web-known issues",
        "### 9. Cross-cutting conformance",
    ]
    for h in dims:
        assert h in body, f"agents/code-review.md missing dimension heading {h!r}"

    # Code-reframe evidence: specific substrings showing the design→code
    # substitution actually landed (NOT just heading-presence).
    code_reframe_anchors = [
        # Dim 1: code-level docstring drift + phantom-import
        "phantom-import",
        # Dim 2: code-paths-in-diff
        "code paths in the diff",
        # Dim 3: methods/types defined but never called (SC-022/SC-025 class)
        "defined but never called",
        # Dim 4: mission-brief AC ↔ code traceability
        "code has no error path",
        # Dim 5: type hints + docstrings on function signatures
        "Type hints",
        # Dim 6: OWASP applied to code with concrete patterns
        "subprocess.run",
        # Dim 7: code-vs-design drift
        "code contradict",
        # Dim 8: known-bad patterns in code
        "asyncio.get_event_loop",
        # Dim 9: in-scope sub-clauses for code-as-artifact
        "RSAD-1",
        "APED-1",
        "EOL-DRIFT-1",
    ]
    for anchor in code_reframe_anchors:
        assert anchor in body, (
            f"agents/code-review.md missing code-reframe anchor {anchor!r} — "
            f"design.md L277-293 reframe table not realized in agent prose; "
            f"test_agent_md_contains_nine_dimensions_against_code would be "
            f"tautologically-green without this content-bearing check (per "
            f"slice-037 M-add-1 discipline)"
        )


def test_agent_md_read_only_tools_pinned():
    """agents/code-review.md `tools:` frontmatter MUST list the 5 read-only
    tools verbatim (matches agents/critique.md:4 for CSP-1 parity) AND must
    NOT list any write tool.

    Positive + negative substring assertion per slice-007 M2 / slice-053
    M-add-4 / /critique B4 fix block pattern: positive on the literal
    5-tool list catches deletion; negative on each forbidden tool catches
    a future `Read, Glob, Grep, Bash, WebSearch, Edit` regression.
    """
    body = _read()
    # Positive: the literal 5-tool list (frontmatter line)
    assert "tools: Read, Glob, Grep, Bash, WebSearch" in body, (
        "agents/code-review.md must declare `tools: Read, Glob, Grep, Bash, "
        "WebSearch` verbatim for CSP-1 parity with agents/critique.md:4"
    )
    # Negative: forbidden write tools must NOT appear on the tools line.
    # Extract the tools line for precise check.
    tools_line = ""
    for line in body.splitlines():
        if line.startswith("tools:"):
            tools_line = line
            break
    assert tools_line, "agents/code-review.md missing `tools:` frontmatter line"
    for forbidden in ("Write", "Edit", "NotebookEdit"):
        assert forbidden not in tools_line, (
            f"agents/code-review.md `tools:` line includes forbidden write "
            f"tool {forbidden!r} — read-only stance violated (ADR-059 "
            f"load-bearing safety invariant)"
        )


def test_agent_md_specificity_rule_path_line_present():
    """agents/code-review.md must carry the `path/to/file.py:line`
    specificity discipline (inherited verbatim from agents/critique.md;
    the rule that distinguishes a sharp code-review finding from a
    docstring-read; per slice-060 mission-brief AC #2).
    """
    body = _read()
    assert "## Specificity rule" in body, (
        "agents/code-review.md missing `## Specificity rule` section — "
        "the rule that distinguishes sharp findings from useless ones"
    )
    assert "path/to/file.py:line" in body, (
        "agents/code-review.md `## Specificity rule` missing the verbatim "
        "`path/to/file.py:line` phrase per CSP-1 parity with critique.md"
    )
