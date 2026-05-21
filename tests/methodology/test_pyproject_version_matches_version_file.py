"""SC-001 reproduction: pyproject.toml [project].version must equal VERSION.

Bug (diagnose-out/backlog.md SC-001, severity=critical):
  pyproject.toml declares ``version = "0.20.0"`` under ``[project]``.
  The canonical version source is ``VERSION`` (0.61.0) and ``plugin.yaml``
  (0.61.0). PMI-1 (``tools/plugin_manifest_audit.py``) gates
  plugin.yaml<->VERSION only — it does not read pyproject.toml. No other
  test/audit compares pyproject [project].version against VERSION.

  Observed at slice-054 reproduction: ``pip install <repo>`` produces
  ``ai-sdlc-tools 0.20.0``, 41 minor versions behind. External pip-install
  consumers see the wrong version label, an ungated stale pip artifact.

Expected (post-fix): ``[project].version`` in ``pyproject.toml`` is
character-equal to the trimmed contents of ``VERSION`` (mirroring the
PMI-1 plugin.yaml<->VERSION gate at ``tools/plugin_manifest_audit.py:207``).

Per BFRD-1 (``methodology-changelog.md`` v0.45.0): this is the failing
reproduction test established BEFORE the fix slice (slice-054) begins.
Convention: bug-fix tests live under ``tests/methodology/`` in this repo
(slice-036 ``test_repro_r9_*`` / slice-045 ``test_install_md_correctness``
precedent — the documented "or project's convention for bug-fix tests"
caveat at ``skills/repro/SKILL.md:87``).
"""

from __future__ import annotations

import re

from tests.methodology.conftest import REPO_ROOT


def _read_pyproject_project_version() -> str:
    """Parse ``[project].version`` from ``pyproject.toml`` via plain regex.

    Deliberately avoids ``tomllib`` (Python 3.11+ stdlib, absent on 3.10 —
    SC-002 in the same backlog). Mirrors the text-parse pattern at
    ``tests/methodology/test_install_audit.py:299-302`` for
    ``pyproject.toml`` parsing in this repo.
    """
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    # Locate the [project] table, then the first `version = "..."` inside it.
    # Stop at the next `[...]` table header to avoid bleeding into
    # `[project.optional-dependencies]` etc.
    project_block_match = re.search(
        r"^\[project\]\s*$(.*?)(?=^\[|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert project_block_match, (
        "pyproject.toml has no `[project]` table — package metadata "
        "must be PEP 621 compliant."
    )
    version_match = re.search(
        r'^version\s*=\s*"([^"]+)"\s*$',
        project_block_match.group(1),
        flags=re.MULTILINE,
    )
    assert version_match, (
        "pyproject.toml `[project]` table has no `version` field — "
        "PEP 621 requires it for non-dynamic versioning."
    )
    return version_match.group(1)


def _read_version_file() -> str:
    """Read the canonical ``VERSION`` file (single source of truth)."""
    return (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_pyproject_has_no_stale_0_20_0_or_count_literals():
    """AC3 pin test (slice-054; minted at /design-slice per /critique M1; name
    harmonized from `v_0_20_0` to bare `0_20_0` per /critique-review m-add-1
    to match the bare ``"0.20.0"`` assertion literal).

    Asserts pyproject.toml carries no stale `0.20.0`-class literal AND no
    `13 audit modules` / `13 tool modules` count literal. The bare ``"0.20.0"``
    substring catches all four pre-fix sites:

      - line 3:  ``# Per INST-1 (methodology-changelog.md v0.20.0).`` (version cite)
      - line 6:  ``(the 13 audit modules under tools/)`` (count literal — separate class)
      - line 20: ``version = "0.20.0"`` (SC-001 fix substance — bumped to current VERSION)
      - line 66: ``# The tools package itself has no non-Python data files in v0.20.0.``

    All four are scrubbed by the slice-054 Phase A bump (line 20) + Phase D
    scrub (lines 3 + 6 + 66). The bare ``"0.20.0"`` literal AND the two count
    literals are universal — catches any forgotten site even if the design
    author overlooks one (the slice-045 INSTALL.md / slice-053 multi-site-
    literal-contrast lesson generalized).

    Defect class: a future pyproject.toml edit re-introduces a stale `0.20.0`
    literal in a comment OR a `13 audit modules` / `13 tool modules` count
    literal (the slice-054 parent class: silently drifted forever because
    nothing pinned it; replicating that anti-pattern on AC3 would be exactly
    the failure mode this slice exists to retire).

    Rule reference: PVFS-1 (slice-054; ADR-056; AC3 stale-prose scrub
    structural backstop; CCC-1 mechanical-inventory class — verifies the
    inventory matches the file).
    """
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "0.20.0" not in pyproject_text, (
        "pyproject.toml carries a stale `0.20.0` literal — slice-054 AC3 "
        "scrub MUST remove all four pre-fix sites (lines 3, 6, 20, 66). "
        "A re-leaked `0.20.0` literal is the SC-001 ungated-stale-pip-"
        "artifact class re-opening. Run `grep -nE '0\\.20\\.0' "
        "pyproject.toml` to find the site, then refactor to non-version-"
        "bearing wording per slice-045 INSTALL.md precedent."
    )
    assert "13 audit modules" not in pyproject_text, (
        "pyproject.toml carries a stale `13 audit modules` count literal "
        "— slice-054 AC3 scrub MUST remove it from line 6 (real count is "
        "now decoupled; refactor to `(the audit modules under tools/ — "
        "see plugin.yaml for the canonical inventory)` per slice-045 "
        "count-decoupling precedent so this is not a per-tool-addition "
        "scrub obligation)."
    )
    assert "13 tool modules" not in pyproject_text, (
        "pyproject.toml carries a stale `13 tool modules` count literal "
        "— same class as `13 audit modules`; refactor to count-free "
        "wording (SC-024 tracks the parallel install_audit.py "
        "occurrence; this pin keeps the pyproject.toml leg clean)."
    )


def test_repro_sc001_pyproject_project_version_matches_version_file():
    """SC-001 / slice-054 BFRD-1 reproduction.

    FAILS pre-fix: pyproject.toml ``[project].version = "0.20.0"`` while
    ``VERSION = "0.61.0"`` (41 minor versions behind).
    PASSES post-fix: pyproject.toml ``[project].version`` equals VERSION.

    Mirrors the PMI-1 plugin.yaml<->VERSION gate at
    ``tools/plugin_manifest_audit.py:207-217`` — the canonical pattern
    for "manifest version tracks VERSION in lock-step".
    """
    pyproject_version = _read_pyproject_project_version()
    version_file = _read_version_file()
    assert pyproject_version == version_file, (
        f"pyproject.toml `[project].version` is {pyproject_version!r} but "
        f"VERSION is {version_file!r}. They MUST track in lock-step "
        f"(SC-001; mirrors the PMI-1 plugin.yaml<->VERSION gate at "
        f"tools/plugin_manifest_audit.py:207). External `pip install <repo>` "
        f"produces `ai-sdlc-tools {pyproject_version}` while the methodology "
        f"semver is {version_file} — an ungated stale pip artifact label."
    )
