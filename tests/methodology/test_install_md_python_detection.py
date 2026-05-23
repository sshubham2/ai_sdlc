"""Repro test for slice-NNN-fix-install-python-detection-and-prompt-fallback.

Bug: INSTALL.md hardcodes ``python3 -m venv ~/.claude/.venv`` in Step 3a
even though Step 1's pre-flight detects either ``command -v python3`` or
``command -v python``. On systems where the Python interpreter is invoked
as ``python`` and NOT aliased as ``python3`` (a common condition — Windows
installers do not register a ``python3.exe`` alias by default; some Linux
distros without ``python-is-python3``; macOS bare ``python`` symlinks),
Step 3a's literal execution fails with "python3: command not found" /
"'python3' is not recognized" even though Python IS installed.

The "No Python found" branch in Step 2 is also too brittle — it tells the
operator to ``Install Python 3.11+ and re-run`` instead of (a) asking the
user where Python actually lives (commonly: installed but not on PATH, or
installed in a non-standard location) and (b) doing so via the canonical
SOAD-1 structured-options ASK form.

Expected (post-fix):

  (1) Step 3a no longer carries a bare hardcoded ``python3 -m venv``
      literal; the venv-create command uses the interpreter Step 1
      detected (reuses a captured variable, or recomputes the
      ``command -v python3 || command -v python`` chain).

  (2) Step 2's "No Python found" branch directs Claude to ASK the user
      for the Python interpreter path (or to install Python) via
      structured options — explicit ``ask the user`` verb,
      ``AskUserQuestion`` reference, or ``structured options`` per the
      SOAD-1 Ask-discipline (CLAUDE.md ``## Ask discipline``).

  (3) Step 2's "Both system Python and conda available" default no longer
      hardcodes ``python3 -m venv`` — it references the detected
      interpreter, matching the Step 3a fix.

Actual (today): all three assertions FAIL.

The FAIL → PASS transition on these assertions is the reproduction
evidence for the fix slice. Pinned permanently in shippability.md so the
brittle-hardcoded-python3 defect cannot silently return.

Rule reference:
  - INST-1 (INSTALL.md is the INST-1 install recipe; integrity gated).
  - SOAD-1 (Ask-discipline — structured options for user-input gates,
    not bare free-text prompts; methodology-changelog v0.56.0).
"""
import re
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT

INSTALL_MD = REPO_ROOT / "INSTALL.md"


def _install_text() -> str:
    return INSTALL_MD.read_text(encoding="utf-8")


def _step_3a_section(text: str) -> str:
    """Return only the ``### 3a:`` Venv sub-section body."""
    m = re.search(
        r"###\s*3a:.*?(?=###\s*3b:)",
        text,
        flags=re.DOTALL,
    )
    assert m is not None, (
        "INSTALL.md no longer has a `### 3a:` Venv sub-section anchor"
    )
    return m.group(0)


def _step_1_section(text: str) -> str:
    """Return only the ``## Step 1:`` pre-flight detection section body."""
    m = re.search(
        r"##\s*Step\s*1:.*?(?=##\s*Step\s*2:)",
        text,
        flags=re.DOTALL,
    )
    assert m is not None, (
        "INSTALL.md no longer has a `## Step 1:` pre-flight section anchor"
    )
    return m.group(0)


def _step_2_section(text: str) -> str:
    """Return only the ``## Step 2:`` resolve-ambiguity section body."""
    m = re.search(
        r"##\s*Step\s*2:.*?(?=##\s*Step\s*3:)",
        text,
        flags=re.DOTALL,
    )
    assert m is not None, (
        "INSTALL.md no longer has a `## Step 2:` resolve-ambiguity section anchor"
    )
    return m.group(0)


def test_install_md_step_3a_does_not_hardcode_python3_venv():
    """Step 3a must NOT carry a bare hardcoded ``python3 -m venv`` literal.

    On systems where only ``python`` is invocable (not ``python3``), the
    literal fails. Step 3a should use the interpreter Step 1 detected —
    either reusing a captured shell variable, or recomputing the
    ``command -v python3 || command -v python`` fallback chain inline.
    """
    section = _step_3a_section(_install_text())
    bad = re.findall(r"\bpython3\s+-m\s+venv\b", section)
    assert not bad, (
        f"INSTALL.md Step 3a hardcodes `python3 -m venv` "
        f"({len(bad)} occurrence(s)); use the interpreter Step 1 detected "
        f"(reuse a captured variable, or recompute "
        f"`$(command -v python3 || command -v python)`). On systems with "
        f"only `python` on PATH, the bare `python3` literal fails."
    )


def test_install_md_step_2_no_python_branch_asks_user_for_interpreter():
    """Step 2's ``**No Python found**`` branch must direct Claude to ASK the
    user for the Python interpreter path (or to install Python), not
    hard-fail with ``Install Python 3.11+ and re-run``.

    Python is a hard dependency; the install must surface the missing
    interpreter interactively (the user may have Python installed but not
    on PATH, or in a non-standard location). The ask must use the
    SOAD-1 structured-options form, not a bare free-text prompt.
    """
    section = _step_2_section(_install_text())
    # Match the `**No Python found**` row body up to the next bullet.
    no_python_block = re.search(
        r"\*\*No Python found\*\*.*?(?=\n\s*-\s*\*\*|\n##\s|\Z)",
        section,
        flags=re.DOTALL,
    )
    assert no_python_block is not None, (
        "INSTALL.md Step 2 no longer has a `**No Python found**` "
        "ambiguity-resolution row"
    )
    body = no_python_block.group(0)
    asks_user = bool(
        re.search(r"\bask the user\b", body, re.IGNORECASE)
        or "AskUserQuestion" in body
        or "structured options" in body
    )
    assert asks_user, (
        f"INSTALL.md Step 2 `**No Python found**` branch must direct Claude "
        f"to ASK the user for the Python interpreter path (or to install "
        f"Python) via SOAD-1 structured options — not hard-fail with "
        f"`Install Python 3.11+ and re-run`. Branch body: {body.strip()!r}"
    )


def test_install_md_step_1_preserves_python3_or_python_detection_chain():
    """AC4 regression-guard: Step 1's pre-flight detection chain
    ``command -v python3 || command -v python`` MUST remain present
    **inside the `## Step 1:` section** verbatim — the slice-061 fix
    propagates the detected interpreter downstream (into Step 3a and
    Step 2's conda-default + No-Python branch), it must NEVER narrow
    detection to python3-only or python-only.

    Section-scoped (M3 fix from /critique-review): a bare ``in
    install_md_text`` substring check would silently false-green if a
    future edit moved the chain out of Step 1 and into a misleading
    comment elsewhere (slice-058 FBCD-1 / canonical-phrase-placement
    discipline applied here). Scoping to the Step 1 section pins the
    chain to its actual contract surface.
    """
    section = _step_1_section(_install_text())
    assert "command -v python3 || command -v python" in section, (
        "INSTALL.md Step 1 no longer preserves the "
        "`command -v python3 || command -v python` detection-chain "
        "fallback. The slice-061 fix must keep this chain verbatim in "
        "Step 1's pre-flight bash block; downstream sites (Step 3a, "
        "Step 2 conda-default) propagate the detected interpreter from "
        "here. Narrowing to python3-only or python-only re-introduces "
        "the original brittleness this slice exists to fix."
    )


def test_install_md_step_2_conda_default_does_not_hardcode_python3_venv():
    """Step 2's ``**Both system Python and conda available**`` row must not
    hardcode ``python3 -m venv`` as the default — it should reference the
    detected interpreter, matching the Step 3a fix.

    Without this assertion, a fix that patches Step 3a but leaves the
    Step 2 prose default ``python3 -m venv`` would re-introduce the bug
    the next time Claude reads INSTALL.md and parrots the default.
    """
    section = _step_2_section(_install_text())
    conda_block = re.search(
        r"\*\*Both system Python and conda available.*?(?=\n\s*-\s*\*\*|\n##\s|\Z)",
        section,
        flags=re.DOTALL,
    )
    assert conda_block is not None, (
        "INSTALL.md Step 2 no longer has a `**Both system Python and conda "
        "available**` ambiguity-resolution row"
    )
    body = conda_block.group(0)
    bad = re.findall(r"`python3\s+-m\s+venv`", body)
    assert not bad, (
        f"INSTALL.md Step 2 conda-ambiguity row hardcodes `python3 -m venv` "
        f"({len(bad)} occurrence(s)); reference the detected interpreter "
        f"instead so the default tracks the Step 3a execution prose."
    )
