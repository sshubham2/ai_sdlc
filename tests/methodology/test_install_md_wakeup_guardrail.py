"""Regression pins for slice-058-add-install-wakeup-prompt-guardrail.

slice-058 adds Step 3h to INSTALL.md (the INST-1 install recipe): an
idempotent, confirmation-gated step that appends a ``# Wakeup-prompt
discipline`` block to the installing user's global ~/.claude/CLAUDE.md, so
the ScheduleWakeup-misuse guardrail travels to every machine that installs
the pipeline.

All three pins are prose-existence pins (the slice-045
``test_install_md_correctness.py`` class) -- R-2-class: they guard prose
existence in INSTALL.md / shippability.md, NOT runtime behavior. The
install step runs only at install time on a real machine, so a behavioral
test is infeasible -- an accepted, recorded limitation (design.md "Test
design notes").

Rule reference: INST-1 (INSTALL.md is the INST-1 install recipe).
"""
import re

from tests.methodology.conftest import REPO_ROOT

INSTALL_MD = REPO_ROOT / "INSTALL.md"
SHIPPABILITY_MD = REPO_ROOT / "architecture" / "shippability.md"


def _install_text() -> str:
    return INSTALL_MD.read_text(encoding="utf-8")


def _collapse_ws(text: str) -> str:
    """Collapse every whitespace run to a single space so the block's
    line-wrapping is irrelevant to substring matching."""
    return re.sub(r"\s+", " ", text)


def test_install_md_has_idempotent_wakeup_discipline_step():
    """AC1 -- INSTALL.md carries the new idempotent, confirmation-gated
    wakeup-prompt-discipline install step. Anchors on the step's heading
    TEXT, not the ``3h`` letter (the letter is positional -- a future
    slice adding a Step 3i could shift it)."""
    raw = _install_text()
    collapsed = _collapse_ws(raw)

    # (a) the step exists -- anchor on the stable heading text, not "3h"
    assert "Global CLAUDE.md — wakeup-prompt discipline" in raw, (
        "INSTALL.md is missing the wakeup-prompt-discipline install step "
        "(expected a heading 'Global CLAUDE.md — wakeup-prompt discipline')"
    )
    # (b) the step appends to the installing user's global CLAUDE.md
    assert "~/.claude/CLAUDE.md" in collapsed, (
        "the wakeup-prompt-discipline step does not reference ~/.claude/CLAUDE.md"
    )
    # (c) idempotent -- embeds the block heading AND skips when it is present
    assert "# Wakeup-prompt discipline" in raw, (
        "the wakeup-prompt-discipline step does not embed the "
        "'# Wakeup-prompt discipline' block heading"
    )
    assert "already present" in collapsed and "skip" in collapsed, (
        "the wakeup-prompt-discipline step lacks an idempotency skip guard "
        "(expected 'already present' + 'skip')"
    )
    # (d) confirmation-gated -- show the diff, get confirmation
    assert "confirmation" in collapsed, (
        "the wakeup-prompt-discipline step is not confirmation-gated "
        "(expected a 'confirmation' instruction)"
    )


def test_wakeup_block_states_load_bearing_facts():
    """AC2 -- the appended ``# Wakeup-prompt discipline`` block states the
    four load-bearing facts. Four discrete asserts, each a phrase lifted
    verbatim from the frozen block (design.md "What's new" item 2); the
    text is whitespace-collapsed so the block's line-wrapping is
    irrelevant. The four anchor phrases are ASCII-only -- encoding-robust."""
    collapsed = _collapse_ws(_install_text())

    # (a) literal-replay fact
    assert "literally, as fresh user input" in collapsed, (
        "wakeup block missing the literal-replay fact "
        "('literally, as fresh user input')"
    )
    # (b) never-as-no-op / heartbeat / fallback fact
    assert "no-op label, heartbeat, or fallback wakeup" in collapsed, (
        "wakeup block missing the never-pass-as-no-op fact "
        "('no-op label, heartbeat, or fallback wakeup')"
    )
    # (c) /loop-and-intentional-wakeups carve-out
    assert "/loop" in collapsed and "are unaffected" in collapsed, (
        "wakeup block missing the /loop intentional-wakeup carve-out "
        "('/loop' ... 'are unaffected')"
    )
    # (d) harness-notifies-on-completion context
    assert "notifies you on completion" in collapsed, (
        "wakeup block missing the harness-notifies-on-completion context "
        "('notifies you on completion')"
    )


def test_shippability_row_58_present_and_cites_install_wakeup_guardrail():
    """AC3 -- architecture/shippability.md carries a row #58 for this
    slice that runs this very test module (one function, two assertions:
    row present + cites the slice and the test module)."""
    text = SHIPPABILITY_MD.read_text(encoding="utf-8")
    row = next(
        (ln for ln in text.splitlines() if ln.lstrip().startswith("| 58 |")),
        None,
    )
    assert row is not None, (
        "architecture/shippability.md has no row numbered 58"
    )
    assert "slice-058-add-install-wakeup-prompt-guardrail" in row, (
        "shippability row 58 does not cite "
        "slice-058-add-install-wakeup-prompt-guardrail"
    )
    assert "tests/methodology/test_install_md_wakeup_guardrail.py" in row, (
        "shippability row 58 does not run "
        "tests/methodology/test_install_md_wakeup_guardrail.py"
    )
