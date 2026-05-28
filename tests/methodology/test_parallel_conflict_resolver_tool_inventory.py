"""BC-PROJ-9 5-inventory pin for `tools/parallel_conflict_resolver.py` (PCR-1 / slice-076).

Per BC-PROJ-9: every new `tools/*.py` module MUST be registered in all 5 inventory
surfaces so the install audit + manifest audit + UTF-8 regression coverage stay in
sync. PCR-1 ships the new module ``tools/parallel_conflict_resolver.py``; this test
guards the 5 registration sites:

  1. ``plugin.yaml`` tools block (PMI-1 manifest)
  2. ``tools/install_audit.py::_CANONICAL_TOOLS`` (INST-1)
  3. ``INSTALL.md`` tool-count literal at L22 ("**N executable methodology tools**")
  4. ``INSTALL.md`` tool-count literal at L166 ("The N executable methodology tools")
  5. ``tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS``
     (UTF8-STDOUT-1 coverage — parallel_conflict_resolver uses --repo-root, no
     positional slice arg → root-only bucket per slice-067 PSQ-1 / slice_queue_writer
     precedent)

The shippability row #76 (the 5th BC-PROJ-9 surface, sometimes counted separately) is
covered by ``test_v_0_73_0_pcr_1_shippability_consumer_propagation`` in
``test_methodology_changelog.py`` (BC-PROJ-10 paired-pin layer). Per /critique M6
ACCEPTED-FIXED + design.md L20: INSTALL.md has the tool-count literal at BOTH L22 and
L166; both must bump 30→31 in lockstep.
"""
from __future__ import annotations

import re

from tests.methodology.conftest import read_file


def test_parallel_conflict_resolver_in_canonical_tools_plugin_manifest_install_md_at_l22_and_l166() -> None:
    """5-inventory presence pin for parallel_conflict_resolver post-PCR-1.

    Asserts all 5 registration surfaces carry the new module:
      (1) plugin.yaml tools block has ``  - path: tools/parallel_conflict_resolver.py``
      (2) install_audit.py _CANONICAL_TOOLS tuple contains
          ``"tools.parallel_conflict_resolver"``
      (3) INSTALL.md L22 reads ``**31 executable methodology tools**`` (bumped 30→31)
      (4) INSTALL.md L166 reads ``The 31 executable methodology tools`` (bumped 30→31)
      (5) tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS list
          contains ``"tools.parallel_conflict_resolver"`` — PCR-1 helper uses
          --repo-root (no positional slice arg), root-only bucket per
          slice_queue_writer precedent
    """
    # (1) plugin.yaml tools block
    plugin_yaml = read_file("plugin.yaml")
    assert "tools/parallel_conflict_resolver.py" in plugin_yaml, (
        "plugin.yaml tools block missing `- path: tools/parallel_conflict_resolver.py` "
        "— PCR-1 BC-PROJ-9 5-inventory surface 1 (PMI-1 manifest registration)"
    )

    # (2) install_audit.py _CANONICAL_TOOLS tuple
    install_audit = read_file("tools/install_audit.py")
    assert '"tools.parallel_conflict_resolver"' in install_audit, (
        "tools/install_audit.py _CANONICAL_TOOLS tuple missing "
        '"tools.parallel_conflict_resolver" — PCR-1 BC-PROJ-9 5-inventory '
        "surface 2 (INST-1 install audit)"
    )

    # (3) + (4) INSTALL.md tool-count literal at L22 + L166 both at 31
    install_md = read_file("INSTALL.md")
    # Both forms must read 31, not 30, post-PCR-1 (30→31 bump).
    assert "**31 executable methodology tools**" in install_md, (
        "INSTALL.md must contain '**31 executable methodology tools**' literal "
        "(L22 anchor; bumped from **30** at PCR-1 BC-PROJ-9 5-inventory surface 3)"
    )
    assert "31 executable methodology tools (audit modules" in install_md, (
        "INSTALL.md must contain 'The 31 executable methodology tools (audit modules' "
        "literal (L166 anchor; bumped from '30' at PCR-1 BC-PROJ-9 5-inventory "
        "surface 4 — TWO-SITE pin per /critique M6 ACCEPTED-FIXED; desync between "
        "L22 and L166 fails INST-1 audit)"
    )
    # Defense-in-depth: there must be NO remaining literal '30 executable methodology
    # tools' anywhere in INSTALL.md (catches a half-bumped state where one site bumped
    # but the other didn't).
    assert "30 executable methodology tools" not in install_md, (
        "INSTALL.md still contains stale '30 executable methodology tools' literal "
        "— a half-bumped state at PCR-1; BOTH L22 + L166 sites must bump 30→31 in "
        "lockstep per /critique M6 ACCEPTED-FIXED two-site pin"
    )

    # (5) test_utf8_stdout_regression.py _ROOT_ONLY_TOOLS
    utf8_regression = read_file("tests/methodology/test_utf8_stdout_regression.py")
    assert '"tools.parallel_conflict_resolver"' in utf8_regression, (
        "tests/methodology/test_utf8_stdout_regression.py _ROOT_ONLY_TOOLS list "
        'missing "tools.parallel_conflict_resolver" — PCR-1 BC-PROJ-9 5-inventory '
        "surface 5 (UTF8-STDOUT-1 cp1252 coverage; PCR-1 helper uses --repo-root "
        "with no positional slice arg → root-only bucket per slice-067 / slice_queue_writer "
        "precedent)"
    )
