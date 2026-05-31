"""Test the INSTALL.md base-vault-location config write (slice-093 / ADR-085).

AC3: the install flow writes ONLY the global base config
(`~/.claude/ai-sdlc-vault-base`) via `_vault_write.safe_write_text`, WITHOUT
moving any existing repo's `architecture/` (capability only; the per-project
`$GIT_COMMON_DIR/aisdlc/vault-root` write is slice-094). INSTALL.md is a
Claude-executed recipe; this exercises the underlying write primitive in the
install-shaped scenario + asserts the no-move property at the write level.
"""
from __future__ import annotations

from pathlib import Path

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

from tools._vault_write import safe_write_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_install_writes_global_base_config_without_moving_vault(tmp_path: Path) -> None:
    """Writing the global base config creates `<claude>/ai-sdlc-vault-base` with
    the chosen base, and leaves a pre-existing `architecture/` byte-identical."""
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    # A stand-in existing vault that MUST NOT be touched (no-flip safety contract).
    vault = tmp_path / "architecture"
    vault.mkdir()
    sentinel = vault / "risk-register.md"
    sentinel_bytes = b"# Risk register\nR-1 ...\n"
    sentinel.write_bytes(sentinel_bytes)

    base_value = "~/.aisdlc"
    base_config = claude_dir / "ai-sdlc-vault-base"
    safe_write_text(base_config, base_value + "\n")

    # Global base config written with exactly the chosen base.
    assert base_config.read_text(encoding="utf-8").strip() == base_value
    # The existing vault is untouched — capability only, no move/flip.
    assert sentinel.read_bytes() == sentinel_bytes
    assert sorted(p.name for p in vault.iterdir()) == ["risk-register.md"]


def test_install_step_documented_in_install_md() -> None:
    """INSTALL.md carries the base-vault-location prompt step + writes the
    global base config via _vault_write (the source-of-truth for the recipe)."""
    install = (REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    assert "ai-sdlc-vault-base" in install, "INSTALL.md must write the global base config"
    assert "_vault_write" in install, "INSTALL.md must write via the safe-write helper"
    assert "~/.aisdlc" in install, "INSTALL.md must name the default base location"
