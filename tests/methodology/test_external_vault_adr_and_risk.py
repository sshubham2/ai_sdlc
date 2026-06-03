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
    """093 migrated NO additional tools (the 10 slice-068/072/081 consumers);
    slice-095 added `tools/vault_edit.py` (11); slice-098 / ADR-089 then migrated
    the 3 git-coupled tools 093 AC4 deferred ("migrate-NONE") —
    parallel_conflict_resolver + pulse_worktree_resolver + stranded_slice_audit
    (Class-A ROUTE via VAULT_ROOT + Class-B RETIRE-when-external via vault_is_external)
    — bringing the live importer set to 14; slice-103 then added
    tools/index_router_thinness_audit.py (15) and slice-106 added
    tools/project_frame_synth.py (16). slice-093's archived design.md still
    documents the original FS-path / git-or-worktree-coupled / never-migrate map
    (immutable history); slice-098 is the slice that acted on the deferral."""
    importers = _vault_root_importers()
    assert len(importers) == 16, (
        f"expected the 10 slice-068/072/081 consumers + slice-095's "
        f"tools/vault_edit.py + slice-098's 3 git-coupled tools + slice-103's "
        f"tools/index_router_thinness_audit.py + slice-106's "
        f"tools/project_frame_synth.py = 16 VAULT_ROOT "
        f"importer(s); found {len(importers)}: {sorted(importers)}"
    )
    assert "tools/index_router_thinness_audit.py" in importers, (
        "slice-103's index_router_thinness_audit.py must consume VAULT_ROOT "
        "(resolves slices/_index.md + archive/_index.md + action-points.md under it; ADR-093 / M5)"
    )
    assert "tools/vault_edit.py" in importers, (
        "slice-095's vault_edit.py must consume VAULT_ROOT (resolves --file under it)"
    )
    assert "tools/project_frame_synth.py" in importers, (
        "slice-106's project_frame_synth.py must consume VAULT_ROOT (routes the 4 "
        "concept/triage/slice-queue/risk-register reads under it; production must-rewrite 4→0; ADR-091)"
    )
    # slice-098 / ADR-089: the 3 once-deferred git-coupled tools are now migrated.
    for migrated in (
        "tools/parallel_conflict_resolver.py",
        "tools/pulse_worktree_resolver.py",
        "tools/stranded_slice_audit.py",
    ):
        assert migrated in importers, f"slice-098 must migrate {migrated} to VAULT_ROOT"
    # _vault_write imports _CONFIG_REL (NOT VAULT_ROOT) → not an importer.
    assert "tools/_vault_write.py" not in importers

    # Archive-aware (R-15 class — slice-093 is archived once shipped; the glob
    # resolves its design.md in slices/ OR slices/archive/. Exposed at slice-095
    # when the importer-count fix let this assertion run past the count gate.)
    design = next(
        REPO_ROOT.glob(
            "architecture/slices/**/slice-093-add-external-vault-support/design.md"
        )
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
