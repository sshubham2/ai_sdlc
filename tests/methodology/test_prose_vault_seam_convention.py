"""Tests for the `<vault>` prose-seam convention (slice-112 / ADR-105).

Pins the convention + the pilot conversion:
  * AC1 — CLAUDE.md states the resolution rule exactly once; ADR-105 present + lists
          the 7 carve-out classes; the `<diagnose-out>` token is NOT minted (B5).
  * AC3 — the pilot files (CLAUDE.md + agents/critique.md) carry zero UN-EXEMPTED
          `rewrite-at-flip` literal after conversion; agents/critique.md embeds a
          self-sufficient `<vault>` note (M-add-1 — a subagent lacks CLAUDE.md).
  * AC4 — the convention's documented default resolves to the same `architecture/`
          the code seam (`tools/_vault_paths.VAULT_ROOT`) resolves to (no pre-flip
          behaviour change).

The converted-file one-way ratchet itself (AC2) is pinned in
`test_vault_flip_prose_inventory.py` (extends the slice-107 tool tests).
"""
from __future__ import annotations

from pathlib import Path

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py

from tools import _vault_paths
from tools.vault_flip_prose_inventory import (
    audit_root,
    converted_file_regressions,
    REWRITE_AT_FLIP,
    _CONVERTED_FILES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
AGENT_MD = REPO_ROOT / "agents" / "critique.md"
ADR_105 = REPO_ROOT / "architecture" / "decisions" / "ADR-105-prose-vault-seam-placeholder.md"

# The distinctive resolution-rule sentinel authored into CLAUDE.md + the agent note.
_RULE_SENTINEL = "denotes the vault root"
# The 7 carve-out class anchors ADR-105 must enumerate (taxonomy classes 1-7).
_SEVEN_CARVE_OUT_ANCHORS = (
    "INSTALL.md",            # 1 user-facing root docs
    "Definitional literals", # 2
    "Historical anchors",    # 3
    "Worktree-composed",     # 4
    "ACTIVE-folder",         # 5 per-slice active folder
    "slice-queue.md",        # 6 undecided ledger
    "diagnose-out",          # 7 no seam yet
)


# ── AC1 ──────────────────────────────────────────────────────────────────────
def test_claude_md_states_resolution_rule_exactly_once():
    """CLAUDE.md states the `<vault>` resolution rule EXACTLY once (the single
    authoritative resolver the main agent carries in context)."""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    assert text.count(_RULE_SENTINEL) == 1, (
        f"CLAUDE.md must state the resolution rule exactly once "
        f"(found {text.count(_RULE_SENTINEL)} of '{_RULE_SENTINEL}')"
    )
    # the rule names the `<vault>/` token and the plain-prose default `architecture/`
    assert "`<vault>/`" in text
    assert "AI_SDLC_VAULT_ROOT" in text


def test_adr_105_present_and_lists_seven_carve_out_classes():
    """ADR-105 exists and enumerates the 7-class carve-out taxonomy."""
    assert ADR_105.exists(), "ADR-105 must be present"
    adr = ADR_105.read_text(encoding="utf-8")
    for anchor in _SEVEN_CARVE_OUT_ANCHORS:
        assert anchor in adr, f"ADR-105 carve-out taxonomy missing class anchor: {anchor!r}"


def test_diagnose_out_token_not_minted():
    """`<diagnose-out>` is NOT minted as a PATH placeholder (no seam in
    _vault_paths.py — B5); the convention mints only `<vault>`. The prose may
    MENTION `<diagnose-out>` to say it is not minted, but it is never USED as a
    path (`<diagnose-out>/…`); diagnose-out/ stays concrete."""
    for p in (CLAUDE_MD, AGENT_MD):
        assert "<diagnose-out>/" not in p.read_text(encoding="utf-8"), (
            f"{p.name} must NOT use `<diagnose-out>/` as a path placeholder (B5)"
        )
    # diagnose-out is still referenced concretely in CLAUDE.md (carved out, not converted)
    assert "diagnose-out/backlog.md" in CLAUDE_MD.read_text(encoding="utf-8")


# ── AC3 ──────────────────────────────────────────────────────────────────────
def test_pilot_files_zero_rewrite_at_flip_after_conversion():
    """The converted pilot files carry zero UN-EXEMPTED `rewrite-at-flip` literal
    (the operational refs are now `<vault>/`; only the sanctioned hash-keyed
    carve-outs remain) — i.e. the one-way ratchet is satisfied on the real repo."""
    regressions = converted_file_regressions(audit_root(REPO_ROOT))
    assert regressions == [], (
        "converted pilot files must have no un-exempted rewrite-at-flip literal; got: "
        + ", ".join(f"{o.path}:{o.line}:{o.col} {o.value!r}" for o in regressions)
    )


def test_agent_critique_embeds_self_sufficient_vault_note():
    """agents/critique.md embeds a self-contained `<vault>` resolution note near
    the top — a Critic SUBAGENT does NOT inherit the project CLAUDE.md (M-add-1),
    so the agent must carry its own resolver."""
    lines = AGENT_MD.read_text(encoding="utf-8").splitlines()
    head = "\n".join(lines[:80])
    assert _RULE_SENTINEL in head, (
        "agents/critique.md must embed the `<vault>` resolution note near the top "
        "(the subagent has no CLAUDE.md to resolve from — M-add-1)"
    )
    assert "`<vault>/`" in head


# ── AC4 ──────────────────────────────────────────────────────────────────────
def test_seam_token_resolves_to_architecture_default():
    """The convention's documented default (`architecture/`) matches what the code
    seam resolves to with no env / no git-common-dir config — prose and code resolve
    identically. slice-115 ([[ADR-107]] — THE flip): this repo is now genuinely flipped
    (a live config makes the ambient VAULT_ROOT external), so the default-resolution
    MECHANISM is verified via the isolation helper (env + config stubbed), not the live
    VAULT_ROOT."""
    with vi.default_vault_root() as vr:
        assert vr == Path("architecture"), (
            "the code seam's default must resolve to architecture/ — the convention's "
            "stated default must mirror it"
        )
    # the CLAUDE.md rule states architecture/ as the plain-prose default
    assert "architecture/" in CLAUDE_MD.read_text(encoding="utf-8")


# ── AC5 ──────────────────────────────────────────────────────────────────────
def test_followon_remainder_worklist_complete():
    """AC5: the not-yet-converted operational prose literals (the skill-conversion
    follow-on's worklist) are a complete, classified enumeration — every remaining
    `rewrite-at-flip` literal OUTSIDE the converted pilot files is fully tagged
    (path/line/value), so the follow-on has no orphaned/unclassified site."""
    res = audit_root(REPO_ROOT)
    remainder = [o for o in res.occurrences
                 if o.klass == REWRITE_AT_FLIP and o.path not in _CONVERTED_FILES]
    assert remainder, "the follow-on worklist (un-converted rewrite-at-flip) must be non-empty"
    for o in remainder:
        assert o.path and o.line >= 1 and o.value, "every worklist entry must be fully tagged"
