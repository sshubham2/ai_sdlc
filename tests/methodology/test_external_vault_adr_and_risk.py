"""Structural pins for slice-093 (ADR-085 / R-32) bookkeeping.

AC4: no NEW tool migration this slice (the VAULT_ROOT allowlist stays at the
     10 slice-068/071 consumers) + the tool-migration classification map is
     documented in design.md.
AC5: R-32 registered in risk-register.md + ADR-085 extends (does not supersede)
     ADR-065.
"""
from __future__ import annotations

import re
from pathlib import Path

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

REPO_ROOT = Path(__file__).resolve().parents[2]


def _vault_root_importers() -> set[str]:
    """tools/*.py modules that import VAULT_ROOT (the migration allowlist's
    actual membership — mirrors test_migration_site_allowlist_pinned)."""
    importers: set[str] = set()
    for py in sorted((REPO_ROOT / "tools").glob("*.py")):
        if py.name.startswith("_") or py.name == "__init__.py":
            continue
        if "from tools._vault_paths import VAULT_ROOT" in py.read_text(encoding="utf-8"):
            importers.add(f"tools/{py.name}")
    return importers


# ─── AC4: no new migration + classification map documented ──────────────


def test_no_new_tool_migration_and_classification_map_documented() -> None:
    """093 migrates NO additional tools (allowlist stays at 10), and design.md
    documents the FS-path / git-or-worktree-coupled / never-migrate map."""
    importers = _vault_root_importers()
    assert len(importers) == 10, (
        f"slice-093 must add NO new VAULT_ROOT importer (capability cut, no flip); "
        f"found {len(importers)}: {sorted(importers)}"
    )
    # _vault_write imports _CONFIG_REL (NOT VAULT_ROOT) → not an importer.
    assert "tools/_vault_write.py" not in importers

    design = (
        REPO_ROOT
        / "architecture/slices/slice-093-add-external-vault-support/design.md"
    ).read_text(encoding="utf-8")
    assert "Tool-migration classification map" in design
    assert "parallel_conflict_resolver.py" in design  # the git-coupled exemplar
    assert "pulse_worktree_resolver.py" in design  # the worktree-coupled exemplar
    assert "never-migrate" in design.lower() or "never migrate" in design.lower()


# ─── AC5: R-32 registered + ADR-085 extends ADR-065 ─────────────────────


def test_r32_registered_and_adr_extends_065() -> None:
    """R-32 is in the risk register and ADR-085 extends (not supersedes) ADR-065."""
    register = (REPO_ROOT / "architecture/risk-register.md").read_text(encoding="utf-8")
    assert re.search(r"\bR-32\b", register), "R-32 must be registered in risk-register.md"

    adr_path = (
        REPO_ROOT
        / "architecture/decisions/ADR-085-external-shared-vault-resolution-and-write-safety.md"
    )
    assert adr_path.exists(), "ADR-085 must exist"
    adr = adr_path.read_text(encoding="utf-8")
    # Extends, not supersedes: frontmatter supersedes is null, body references ADR-065.
    assert re.search(r"^supersedes:\s*null\s*$", adr, re.MULTILINE), (
        "ADR-085 must declare supersedes: null (it EXTENDS ADR-065, not supersedes)"
    )
    assert "ADR-065" in adr, "ADR-085 must reference the ADR-065 seam it extends"
