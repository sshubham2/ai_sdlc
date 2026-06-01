"""BC-PROJ-9 5-inventory pin for tools/pulse_worktree_resolver.py.

Per slice-077 mission-brief AC#5 + design.md L194-208. The new helper must be
registered across 5 canonical surfaces:

1. plugin.yaml tools block
2. tools/install_audit.py::_CANONICAL_TOOLS
3. INSTALL.md tool-count literal at L22 AND L166 (now `36`; per slice-076 M6
   two-site pin precedent — bumped 33→35→36 (slice-087→slice-089)/ADR-079)
4. architecture/shippability.md row #77
5. tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS (root-only
   bucket — uses --repo-root with no positional slice arg per slice-067 /
   parallel_conflict_resolver precedent)

ALL 5 sites must be in lockstep — any drift is a refusal per the BC-PROJ-9
5-inventory discipline.

Includes cross-spec parity smoke per design.md § Cross-spec parity (M7
ACCEPTED-FIXED): verifies the helper imports `_stdout` and `_resolve_default_branch`
from the canonical sources, matching parallel_conflict_resolver.py.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT


_TOOL_PATH = REPO_ROOT / "tools" / "pulse_worktree_resolver.py"
_PLUGIN_YAML = REPO_ROOT / "plugin.yaml"
_INSTALL_AUDIT = REPO_ROOT / "tools" / "install_audit.py"
_INSTALL_MD = REPO_ROOT / "INSTALL.md"
_SHIPPABILITY = REPO_ROOT / "architecture" / "shippability.md"
_UTF8_TEST = REPO_ROOT / "tests" / "methodology" / "test_utf8_stdout_regression.py"


def test_pulse_worktree_resolver_in_canonical_tools_plugin_manifest_install_md_at_l22_and_l166():
    """BC-PROJ-9 5-inventory: assert pulse_worktree_resolver registered at all
    5 sites in lockstep.

    1. _CANONICAL_TOOLS contains `tools.pulse_worktree_resolver`
    2. plugin.yaml tools block contains `- path: tools/pulse_worktree_resolver.py`
    3. INSTALL.md L22 + L166 both contain literal `35` (post-bump tool count)
    4. shippability.md contains a row `| 77 |` referencing slice-077
    5. _ROOT_ONLY_TOOLS contains `tools.pulse_worktree_resolver`
    """
    # 1. _CANONICAL_TOOLS in tools/install_audit.py
    install_audit_src = _INSTALL_AUDIT.read_text(encoding="utf-8")
    assert '"tools.pulse_worktree_resolver"' in install_audit_src, (
        "tools.pulse_worktree_resolver missing from tools/install_audit.py::_CANONICAL_TOOLS"
    )

    # 2. plugin.yaml tools block
    plugin_yaml = _PLUGIN_YAML.read_text(encoding="utf-8")
    assert "tools/pulse_worktree_resolver.py" in plugin_yaml, (
        "tools/pulse_worktree_resolver.py missing from plugin.yaml tools block"
    )

    # 3. INSTALL.md tool-count literal `35` at L22 AND L166
    install_md_lines = _INSTALL_MD.read_text(encoding="utf-8").splitlines()
    assert len(install_md_lines) >= 166, (
        f"INSTALL.md has only {len(install_md_lines)} lines; expected ≥166 for the L166 pin"
    )
    l22 = install_md_lines[21]  # 1-indexed line 22 → 0-indexed [21]
    l166 = install_md_lines[165]  # 1-indexed line 166 → 0-indexed [165]
    assert "38" in l22, (
        f"INSTALL.md L22 missing post-bump tool-count `38` (33→35→36→38, two-site; slice-095 +2 SVW-1 tools); "
        f"actual line content: {l22!r}"
    )
    assert "38" in l166, (
        f"INSTALL.md L166 missing post-bump tool-count `38`; actual line content: {l166!r}"
    )

    # 4. shippability.md row #77
    shippability = _SHIPPABILITY.read_text(encoding="utf-8")
    assert re.search(r"^\|\s*77\s*\|", shippability, flags=re.MULTILINE), (
        "shippability.md missing row #77 for slice-077"
    )

    # 5. _ROOT_ONLY_TOOLS in test_utf8_stdout_regression.py
    utf8_test_src = _UTF8_TEST.read_text(encoding="utf-8")
    # Find the _ROOT_ONLY_TOOLS block and check membership
    root_only_match = re.search(
        r"_ROOT_ONLY_TOOLS\s*=\s*\[(.*?)\]",
        utf8_test_src,
        flags=re.DOTALL,
    )
    assert root_only_match, "_ROOT_ONLY_TOOLS list not found in test_utf8_stdout_regression.py"
    root_only_block = root_only_match.group(1)
    assert '"tools.pulse_worktree_resolver"' in root_only_block, (
        "tools.pulse_worktree_resolver missing from test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS "
        "(should be in root-only bucket — uses --repo-root with no positional slice arg per slice-067 precedent)"
    )


def test_cross_spec_parity_with_parallel_conflict_resolver():
    """Per design.md § Cross-spec parity (M7 + M-add-1 ACCEPTED-FIXED): the
    pulse_worktree_resolver helper must follow the same conventions as PCR-1
    sibling helper (parallel_conflict_resolver.py).

    Asserts source-level parity on the load-bearing convention points the
    queued parallel-slice-family-parity-audit slice will check.
    """
    src = _TOOL_PATH.read_text(encoding="utf-8")

    # UTF8-STDOUT-1 shim import + first-line-of-main() call (matches PCR-1 + design.md § Cross-spec parity)
    assert "from tools import _stdout" in src, (
        "pulse_worktree_resolver must `from tools import _stdout` per UTF8-STDOUT-1 + design.md § Cross-spec parity"
    )
    assert "_stdout.reconfigure_stdout_utf8()" in src, (
        "pulse_worktree_resolver main() must call `_stdout.reconfigure_stdout_utf8()`"
    )

    # Canonical default-branch helper reuse (single-sourced per design.md § What's reused)
    assert "from tools.branch_workflow_audit import _resolve_default_branch" in src, (
        "pulse_worktree_resolver must reuse `_resolve_default_branch` from tools.branch_workflow_audit "
        "(single-sourced — NAW-1 ADR-061 exit-2 contract preserved)"
    )

    # argparse mutually-exclusive group required (matches PCR-1's contract)
    assert "add_mutually_exclusive_group(required=True)" in src, (
        "pulse_worktree_resolver must use `add_mutually_exclusive_group(required=True)` "
        "per cross-spec parity with parallel_conflict_resolver.py"
    )

    # Parse-time --repo-root default = Path(".") per M-add-1 ACCEPTED-FIXED
    # (NOT Path(".").resolve() — that happens post-parse at main() body)
    assert 'default=Path(".")' in src, (
        "pulse_worktree_resolver --repo-root parse-time default must be `Path(\".\")`; "
        "post-parse `.resolve()` happens at top of main() body. Per M-add-1 ACCEPTED-FIXED."
    )
    assert "args.repo_root.resolve()" in src, (
        "pulse_worktree_resolver main() must call `args.repo_root.resolve()` post-parse"
    )
