"""AC#3 — SKILL.md sub-step 2.5 dispatch prose pins (slice-078 / M3 APED-1).

Three pins per the APED-1 + RSAD-1 + slice-074/075 aggregated lesson on
UNIQUE-TO-THE-INVOCATION literal specification:

- Pin #1 (L185 dispatch paragraph): a line containing `VAULT_CLAIM` MUST
  co-occur with `auto-resolves` (APPLIED-bound context).
- Pin #2 (L192 closing summary): the enumeration of classes "falling-closed
  to SOAD-1" MUST NOT contain bare `VAULT_CLAIM`.
- Pin #3 (OSDG-1): in-repo + installed SKILL.md content-equal modulo EOL.

The APED-1 execution discipline: both regex pins are pre-tested against
the actual prose AS IT EXISTS post-edit; this test exercises the regex
shape on the current SKILL.md.
"""
from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    """Walk up to the repo root via VERSION sentinel (avoids matching
    `tests/skills/` which exists as a sibling and confuses a plain
    `skills/` search).
    """
    p = Path(__file__).resolve()
    while p != p.parent and not (p / "VERSION").is_file():
        p = p.parent
    return p


def _installed_root() -> Path:
    return Path.home() / ".claude"


def test_substep_2_5_l185_pins_vault_claim_in_apply_block() -> None:
    """Pin #1: at least one line in sub-step 2.5 dispatch prose mentions
    `VAULT_CLAIM` co-occurring with an APPLIED-bound phrase (`auto-resolves`,
    `APPLIED`, `dispatched to PCR-2a`, etc.).

    APED-1-executed: this regex must MATCH the post-edit prose AND not match
    PCR-1's L192 fall-closed closing summary by itself.
    """
    skill_md = (_repo_root() / "skills" / "commit-slice" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    # Co-occurrence regex: same line carries VAULT_CLAIM + an apply-bound token.
    # Lines are long in this SKILL.md, so we use multiline-aware split-on-newline.
    apply_pattern = re.compile(
        r"VAULT_CLAIM[^\n]*(?:auto-resolves|APPLIED|auto-resolved by PCR-2a|dispatched to PCR-2a)",
        re.IGNORECASE,
    )
    matches = apply_pattern.findall(skill_md)
    assert matches, (
        "Pin #1 (L185 dispatch paragraph) absent: no line co-occurs "
        "`VAULT_CLAIM` with an APPLIED-bound phrase. The dispatch logic "
        "prose must explicitly route VAULT_CLAIM through PCR-2a APPLIED, "
        "not leave it as a fall-through to SOAD-1 STOP."
    )


def test_substep_2_5_l192_drops_vault_claim_from_fall_closed_enumeration() -> None:
    """Pin #2: the L192 closing summary enumeration of fall-closed classes
    MUST NOT include bare `VAULT_CLAIM` (PCR-2a now auto-resolves it).

    APED-1-executed: this regex MUST match the pre-edit prose (witnessing
    the stale enumeration) and MUST NOT match the post-edit prose.

    Anchor: search for `VAULT_CLAIM` immediately followed by descriptive
    parenthetical AND occurring in a sentence containing `fall-closed` /
    `falling-closed` / `fall through to SOAD`. The PCR-1 closing prose's
    canonical shape was:
        `VAULT_CLAIM (...) + HARD (...) + MIXED (...) + UNKNOWN (...)
        classes ALL fall-closed`.
    """
    skill_md = (_repo_root() / "skills" / "commit-slice" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    # Pre-fix shape: `VAULT_CLAIM (<descriptive paren>) + HARD (<descriptive paren>)`
    # — the multi-class fall-closed enumeration. PCR-2a removes VAULT_CLAIM from
    # this enumeration. Note: VAULT_CLAIM may still appear in a corner-case
    # context (`claimed_at-tie + ... fall through`), which is correct.
    enumeration_pattern = re.compile(
        r"VAULT_CLAIM\s*\([^)]+\)\s*\+\s*HARD\s*\(",
        re.IGNORECASE,
    )
    matches = enumeration_pattern.findall(skill_md)
    assert not matches, (
        f"Pin #2 (L192 closing summary) still contains the pre-fix "
        f"`VAULT_CLAIM (...) + HARD (...)` multi-class fall-closed "
        f"enumeration; PCR-2a auto-resolves VAULT_CLAIM, so the closing "
        f"prose must drop VAULT_CLAIM from this enumeration position. "
        f"Found {len(matches)} stale occurrence(s)."
    )


def test_in_repo_and_installed_forward_synced() -> None:
    """Pin #3 (OSDG-1): in-repo + installed SKILL.md content-equal modulo EOL.

    Per ADR-033 EOL-DRIFT-1 — CRLF / LF differences excluded from drift
    semantics.
    """
    in_repo = (_repo_root() / "skills" / "commit-slice" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    installed_path = _installed_root() / "skills" / "commit-slice" / "SKILL.md"
    if not installed_path.exists():
        # Plugin not installed on this machine — WARN-class per OSDG-1 parity
        # with AVFS-1/MCFS-1; do NOT fail. Test passes vacuously.
        return
    installed = installed_path.read_text(encoding="utf-8")
    assert in_repo.replace("\r\n", "\n") == installed.replace("\r\n", "\n"), (
        "OSDG-1 forward-sync drift: in-repo skills/commit-slice/SKILL.md "
        "differs from installed ~/.claude/skills/commit-slice/SKILL.md "
        "(after CRLF→LF normalization per ADR-033). Re-run the OSDG-1 sync."
    )
