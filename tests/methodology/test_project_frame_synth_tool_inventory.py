"""BC-PROJ-9 inventory-pin for `tools/project_frame_synth.py` (slice-088 / PFS-1).

A new `tools/*.py` module must be registered across every inventory surface in
lockstep (BC-PROJ-9). This pins the two machine-readable surfaces — the
`install_audit._CANONICAL_TOOLS` canonical tuple (INST-1) and the `plugin.yaml`
tools block (PMI-1) — plus on-disk existence. The cp1252-coverage surface is
the bespoke `test_project_frame_synth_survives_cp1252_with_u2192` (NOT
`_ROOT_ONLY_TOOLS`, per slice-088 B2); the INSTALL.md count + shippability row
are prose surfaces guarded by PMI-1 / RPCD-1.

Rule reference: PFS-1 (slice-088; ADR-080); BC-PROJ-9.
"""
from pathlib import Path

import yaml

from tests.methodology.conftest import REPO_ROOT


def test_project_frame_synth_in_canonical_inventory():
    """`tools.project_frame_synth` is in install_audit._CANONICAL_TOOLS,
    `tools/project_frame_synth.py` is a plugin.yaml tools entry, and the module
    exists on disk."""
    from tools.install_audit import _CANONICAL_TOOLS

    assert "tools.project_frame_synth" in _CANONICAL_TOOLS

    manifest = yaml.safe_load((REPO_ROOT / "plugin.yaml").read_text(encoding="utf-8"))
    tool_paths = {entry["path"] for entry in manifest.get("tools", [])}
    assert "tools/project_frame_synth.py" in tool_paths

    assert (REPO_ROOT / "tools" / "project_frame_synth.py").is_file()
