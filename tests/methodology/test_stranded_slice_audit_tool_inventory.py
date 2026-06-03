"""BC-PROJ-9 5-inventory pin for tools/stranded_slice_audit.py (slice-087 / ADR-079).

A new `tools/*.py` must be registered across all 5 canonical surfaces in lockstep
(witnessed at slice-077's pulse_worktree_resolver row); any drift is a refusal:

1. plugin.yaml tools block
2. tools/install_audit.py::_CANONICAL_TOOLS
3. INSTALL.md tool-count literal at L22 AND L166 (bumped 33→35→36; two-site pin)
4. architecture/shippability.md row (referencing slice-087 — row# != slice# here)
5. tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS (root-only
   bucket — the tool takes --repo-root/--root, no positional slice arg)
"""
from __future__ import annotations

import re

from tests.methodology.conftest import REPO_ROOT

_TOOL_PATH = REPO_ROOT / "tools" / "stranded_slice_audit.py"
_PLUGIN_YAML = REPO_ROOT / "plugin.yaml"
_INSTALL_AUDIT = REPO_ROOT / "tools" / "install_audit.py"
_INSTALL_MD = REPO_ROOT / "INSTALL.md"
_SHIPPABILITY = REPO_ROOT / "architecture" / "shippability.md"
_UTF8_TEST = REPO_ROOT / "tests" / "methodology" / "test_utf8_stdout_regression.py"


def test_stranded_slice_audit_in_canonical_inventory():
    """BC-PROJ-9 5-inventory: stranded_slice_audit registered at all 5 sites."""
    assert _TOOL_PATH.is_file(), "tools/stranded_slice_audit.py must exist"

    # 1. _CANONICAL_TOOLS
    install_audit_src = _INSTALL_AUDIT.read_text(encoding="utf-8")
    assert '"tools.stranded_slice_audit"' in install_audit_src, (
        "tools.stranded_slice_audit missing from tools/install_audit.py::_CANONICAL_TOOLS"
    )

    # 2. plugin.yaml tools block
    plugin_yaml = _PLUGIN_YAML.read_text(encoding="utf-8")
    assert "tools/stranded_slice_audit.py" in plugin_yaml, (
        "tools/stranded_slice_audit.py missing from plugin.yaml tools block"
    )

    # 3. INSTALL.md tool-count literal `35` at L22 AND L166 (bumped 33→35→36 (slice-087→slice-089))
    install_md_lines = _INSTALL_MD.read_text(encoding="utf-8").splitlines()
    assert len(install_md_lines) >= 166, (
        f"INSTALL.md has only {len(install_md_lines)} lines; expected >=166 for the L166 pin"
    )
    assert "42" in install_md_lines[21], (
        f"INSTALL.md L22 missing post-bump tool-count `42` (…→40→41→42; slice-107 +1 vault_flip_prose_inventory); actual: {install_md_lines[21]!r}"
    )
    assert "42" in install_md_lines[165], (
        f"INSTALL.md L166 missing post-bump tool-count `42`; actual: {install_md_lines[165]!r}"
    )

    # 4. shippability.md row referencing slice-087 (row number != slice number here)
    shippability = _SHIPPABILITY.read_text(encoding="utf-8")
    assert re.search(
        r"^\|\s*\d+\s*\|\s*slice-087-add-stranded-slice-detection-to-slice\s*\|",
        shippability,
        flags=re.MULTILINE,
    ), "shippability.md missing a table row for slice-087-add-stranded-slice-detection-to-slice"

    # 5. _ROOT_ONLY_TOOLS
    utf8_test_src = _UTF8_TEST.read_text(encoding="utf-8")
    root_only_match = re.search(r"_ROOT_ONLY_TOOLS\s*=\s*\[(.*?)\]", utf8_test_src, flags=re.DOTALL)
    assert root_only_match, "_ROOT_ONLY_TOOLS list not found in test_utf8_stdout_regression.py"
    assert '"tools.stranded_slice_audit"' in root_only_match.group(1), (
        "tools.stranded_slice_audit missing from test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS"
    )
