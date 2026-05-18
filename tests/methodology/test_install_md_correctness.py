"""Repro test for slice-045-fix-install-pypi-package-name-and-stale-prose.

Bug: INSTALL.md ships three factual defects.

  (1) PyPI package name wrong — INSTALL.md:93 has the install command
      ``$PY -m pip install graphify``, but the correct PyPI *distribution*
      is ``graphifyy`` (the module/CLI name ``graphify`` is correct and
      must stay; only the ``pip install`` target is wrong). Precedent:
      skills/discover/SKILL.md already uses ``pip install graphifyy[video]``.

  (2) Stale methodology-version literal — INSTALL.md says
      "methodology v0.20.0" (and "pre-v0.20.0" / "baked into v0.20.0")
      while VERSION is 0.54.0.

  (3) Stale tool-count claim — INSTALL.md says "13 executable methodology
      tools" while plugin.yaml enumerates 25.

Expected (post-fix): all three assertions PASS.
Actual (today):      all three assertions FAIL.

The FAIL -> PASS transition on these assertions is the reproduction
evidence for the fix slice. Pinned permanently in shippability.md so the
defects cannot silently return (and so the counts cannot re-drift).

Rule reference: INST-1 (INSTALL.md is the INST-1 install recipe).
"""
import re
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT

INSTALL_MD = REPO_ROOT / "INSTALL.md"
VERSION_FILE = REPO_ROOT / "VERSION"
PLUGIN_YAML = REPO_ROOT / "plugin.yaml"
README_MD = REPO_ROOT / "README.md"
TUTORIAL_HTML = REPO_ROOT / "tutorial-site" / "Hybrid AI SDLC Pipeline.html"


def _install_text() -> str:
    return INSTALL_MD.read_text(encoding="utf-8")


def test_install_md_graphify_pip_package_is_graphifyy():
    """The graphify pip-install target must be ``graphifyy``, never bare
    ``graphify`` (the importable module name stays ``graphify``)."""
    text = _install_text()
    # Bare ``pip install graphify`` NOT immediately followed by another
    # ``y`` is the defect. ``graphifyy`` / ``graphifyy[extra]`` is correct
    # and is excluded by the negative lookahead.
    bad = re.findall(r"pip install\s+graphify(?!y)", text)
    assert not bad, (
        f"INSTALL.md uses the wrong PyPI distribution name "
        f"({len(bad)} occurrence(s) of bare `pip install graphify`); "
        f"the correct PyPI package is `graphifyy`."
    )


def test_install_md_has_no_stale_v0_20_0_literal():
    """INSTALL.md must not carry the stale ``v0.20.0`` literal while
    VERSION says otherwise."""
    current = VERSION_FILE.read_text(encoding="utf-8").strip()
    text = _install_text()
    stale = re.findall(r"v0\.20\.0", text)
    assert not stale, (
        f"INSTALL.md contains {len(stale)} stale `v0.20.0` literal(s) "
        f"while VERSION is {current!r}; refresh the version prose "
        f"(prefer deriving it from VERSION so it cannot re-drift)."
    )


def test_install_md_tool_count_matches_plugin_yaml():
    """Every "N executable methodology tools" claim in INSTALL.md must
    equal the number of tools plugin.yaml enumerates."""
    plugin_tool_count = len(
        re.findall(r"^\s*- path: tools/", PLUGIN_YAML.read_text(encoding="utf-8"), re.M)
    )
    assert plugin_tool_count > 0, "plugin.yaml exposed no `- path: tools/` entries"

    text = _install_text()
    claims = [int(n) for n in re.findall(r"(\d+)\s+executable methodology tools", text)]
    assert claims, "INSTALL.md no longer states an 'N executable methodology tools' count"
    wrong = [n for n in claims if n != plugin_tool_count]
    assert not wrong, (
        f"INSTALL.md claims {wrong} executable methodology tools but "
        f"plugin.yaml enumerates {plugin_tool_count}; the count is stale."
    )


def test_readme_and_tutorial_name_graphifyy_package():
    """AC4 — the descriptive 'graphify install' sentences in README.md and
    the tutorial HTML must name the PyPI distribution `graphifyy` precisely
    (not the vague 'else PyPI'). Closes the Critic m2 gap: these prose
    siblings are outside the INSTALL.md repro contract, so without this
    pin a sloppy reword would be invisible to the catalog."""
    readme = README_MD.read_text(encoding="utf-8")
    html = TUTORIAL_HTML.read_text(encoding="utf-8")

    # The graphify-install line in README.md must name graphifyy and must
    # not retain the vague bare "else PyPI)".
    readme_line = next(
        (ln for ln in readme.splitlines()
         if "Installs `graphify`" in ln and "packages/graphify" in ln),
        None,
    )
    assert readme_line is not None, "README.md graphify-install bullet not found"
    assert "graphifyy" in readme_line, (
        f"README.md graphify-install bullet does not name the PyPI package "
        f"`graphifyy`: {readme_line.strip()!r}"
    )
    assert "else PyPI)" not in readme_line, (
        "README.md still uses the vague bare 'else PyPI)' — name `graphifyy`."
    )

    # The graphify-install <li> in the tutorial HTML must name graphifyy and
    # must not retain the vague bare "else PyPI).".
    html_line = next(
        (ln for ln in html.splitlines()
         if "Installs <code>graphify</code>" in ln and "packages/graphify" in ln),
        None,
    )
    assert html_line is not None, "tutorial HTML graphify-install <li> not found"
    assert "graphifyy" in html_line, (
        f"tutorial HTML graphify-install <li> does not name the PyPI package "
        f"`graphifyy`: {html_line.strip()!r}"
    )
    assert "else PyPI)." not in html_line, (
        "tutorial HTML still uses the vague bare 'else PyPI).' — name `graphifyy`."
    )
