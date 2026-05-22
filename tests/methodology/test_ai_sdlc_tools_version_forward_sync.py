"""TVFS-1 regression suite — `tools/ai_sdlc_tools_version_forward_sync.py`.

Per **TVFS-1** (`methodology-changelog.md` v0.63.0; slice-059; ADR-058;
extends the slice-050/AVFS-1 + slice-041/MCFS-1
forward-sync-via-deterministic-downstream-gate lineage; mints a new rule;
supersedes nothing). Structural sibling of `test_ai_sdlc_version_forward_sync.py`
(AVFS-1 suite), retargeted from `VERSION` ↔ `~/.claude/ai-sdlc-VERSION`
file comparison to `VERSION` ↔ installed `ai-sdlc-tools` pip-distribution
version.

Two coverage layers:
  1. **Seam-injected** — all four states (synced / drift-HALT /
     not-installed-WARN / usage) + the >1 duplicate-distribution case,
     driven through the `installed_version_resolver` injection seam (B2)
     so the drift case genuinely exercises the mismatch branch with no
     tautology.
  2. **Real-resolver egg-info isolation** — proves the real
     `_resolve_installed_version()` (purelib-scoped) does NOT pick up an
     `ai_sdlc_tools.egg-info/` on `sys.path` — the B1 CWD-shadowing class.

Plus the 2-point wiring assertion (WIRE-1 consumer test) and the
non-catalog relocation proof (the module reads environment-mutable
installed state — slice-029/030A discipline).
"""
from __future__ import annotations

import sys
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools import ai_sdlc_tools_version_forward_sync as tvfs


# --------------------------------------------------------------------------- #
# seam-injected: synced (must-not-false-FAIL)                                  #
# --------------------------------------------------------------------------- #
def test_synced_when_installed_equals_version(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "VERSION").write_text("0.63.0\n", encoding="utf-8")

    r = tvfs.check(root, installed_version_resolver=lambda: "0.63.0")
    assert r.status == "synced" and r.exit_code == 0, r.to_dict()


# --------------------------------------------------------------------------- #
# seam-injected: drift HALTs (must-not-mask) — genuine non-tautological case   #
# --------------------------------------------------------------------------- #
def test_drift_halts_exit1_with_attribution(tmp_path: Path):
    """The installed-version side is injected (`9.9.9`) independently of the
    in-repo `VERSION` — so this drift case genuinely exercises the mismatch
    branch (B2: editing `VERSION` alone cannot, since the real resolver and
    the in-repo egg-info both derive from `VERSION`)."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "VERSION").write_text("0.63.0\n", encoding="utf-8")

    r = tvfs.check(root, installed_version_resolver=lambda: "9.9.9")
    assert r.status == "drift" and r.exit_code == 1, r.to_dict()
    assert "NOT a slice regression" in r.divergences[0], r.divergences
    assert "INSTALL.md Step 3g" in r.divergences[0], r.divergences


# --------------------------------------------------------------------------- #
# seam-injected: not-installed → WARN exit 0 (AVFS-1 installed-absent parity)   #
# --------------------------------------------------------------------------- #
def test_not_installed_is_warn_exit0(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "VERSION").write_text("0.63.0\n", encoding="utf-8")

    r = tvfs.check(root, installed_version_resolver=lambda: None)
    assert r.status == "warn" and r.exit_code == 0, r.to_dict()
    # M3: the WARN message MUST name the interpreter actually checked, so a
    # $PY misconfiguration is visible rather than a silent false-clean.
    assert sys.executable in r.warnings[0], r.warnings
    assert "PASS (with WARN)" in tvfs._format_human(r)


# --------------------------------------------------------------------------- #
# seam-injected: in-repo VERSION missing ⇒ usage exit 2 (repo malformed)       #
# --------------------------------------------------------------------------- #
def test_in_repo_version_missing_is_usage_exit2(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()  # no VERSION

    r = tvfs.check(root, installed_version_resolver=lambda: "0.63.0")
    assert r.status == "usage" and r.exit_code == 2, r.to_dict()


# --------------------------------------------------------------------------- #
# seam-injected: >1 distribution ⇒ usage exit 2, distinct message (M-add-2)    #
# --------------------------------------------------------------------------- #
def test_duplicate_dist_is_usage_exit2_distinct_message(tmp_path: Path):
    """A stale duplicate `.dist-info` (interrupted upgrade) is an ENVIRONMENT
    fault with its own remediation — NOT a malformed repo. Exit 2, distinct
    message naming the `pip uninstall` fix (M-add-2)."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "VERSION").write_text("0.63.0\n", encoding="utf-8")

    def _dup() -> str | None:
        raise tvfs.DuplicateDistributionError(
            ["0.62.0", "0.63.0"], "/fake/site-packages"
        )

    r = tvfs.check(root, installed_version_resolver=_dup)
    assert r.status == "usage" and r.exit_code == 2, r.to_dict()
    assert "DUPLICATE DISTRIBUTION" in r.divergences[0], r.divergences
    assert "pip uninstall ai-sdlc-tools" in r.divergences[0], r.divergences


# --------------------------------------------------------------------------- #
# real-resolver: egg-info on sys.path is excluded (B1 fix pin)                 #
# --------------------------------------------------------------------------- #
def test_real_resolver_excludes_in_repo_egg_info(tmp_path: Path):
    """B1 fix pin — the test that would have caught the original defect. An
    `ai_sdlc_tools.egg-info/` placed on `sys.path` (the in-repo build-artifact
    shadowing class) must NOT be picked up: the real `_resolve_installed_
    version()` scopes to `sysconfig.get_path("purelib")` and never consults
    `sys.path`. A reversion to the naive `importlib.metadata.version()` would
    resolve the `9.9.9` egg-info and FAIL this test."""
    egg = tmp_path / "ai_sdlc_tools.egg-info"
    egg.mkdir()
    (egg / "PKG-INFO").write_text(
        "Metadata-Version: 2.1\nName: ai-sdlc-tools\nVersion: 9.9.9\n",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))
    try:
        resolved = tvfs._resolve_installed_version()
    finally:
        sys.path.remove(str(tmp_path))

    assert resolved != "9.9.9", (
        "real _resolve_installed_version picked up the ai_sdlc_tools.egg-info "
        "on sys.path — the B1 CWD-shadowing class is NOT closed (the resolver "
        "must scope to sysconfig purelib, not sys.path)"
    )
    assert resolved is not None, (
        "real _resolve_installed_version returned None — ai-sdlc-tools should "
        "be installed in the test venv (the audit always runs under $PY)"
    )


# --------------------------------------------------------------------------- #
# 2-point wiring: build-slice Step 6 + reflect Step 5b-tvfs (WIRE-1)           #
# --------------------------------------------------------------------------- #
def test_wired_in_build_slice_step6_and_reflect_step5b_tvfs():
    """TVFS-1 MUST be wired at the two AVFS-1/MCFS-1 enforcement points:
    `/build-slice` Step 6 pre-finish + a dedicated `/reflect` Step 5b-tvfs
    (NOT folded into the rule-promotion-gated Step 5b)."""
    bs = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    rf = (REPO_ROOT / "skills" / "reflect" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "tools.ai_sdlc_tools_version_forward_sync" in bs, (
        "build-slice/SKILL.md missing the TVFS-1 invocation — Step 6 "
        "pre-finish wiring absent (the gate would never run at /build-slice)"
    )
    assert "TVFS-1" in bs, (
        "build-slice/SKILL.md missing the 'TVFS-1' rule reference in its "
        "Step 6 audit block"
    )
    assert "tools.ai_sdlc_tools_version_forward_sync" in rf, (
        "reflect/SKILL.md missing the TVFS-1 invocation — the dedicated "
        "post-write step is absent (R-7/slice-022 silent-disable class)"
    )
    assert "TVFS-1" in rf, (
        "reflect/SKILL.md missing the 'TVFS-1' rule reference"
    )
    assert "Step 5b-tvfs" in rf, (
        "reflect/SKILL.md TVFS-1 step is not a DEDICATED step — it must NOT "
        "be folded into the rule-promotion-gated Step 5b (Step 5b-avfs parity)"
    )


# --------------------------------------------------------------------------- #
# non-catalog relocation proof: TVFS-1 module reads environment-mutable state  #
# --------------------------------------------------------------------------- #
def test_tvfs1_module_is_non_catalog():
    """The TVFS-1 module reads the environment-mutable installed distribution
    metadata; a shippability `Machine-cmd` must not depend on such state
    (slice-029/030A). The module must NOT be cited in any `Machine-cmd` cell
    — only the two in-repo-only entry-pins carry row #59."""
    catalog = (REPO_ROOT / "architecture" / "shippability.md").read_text(
        encoding="utf-8"
    )
    for line in catalog.splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 8 or not cells[1].isdigit():
            continue  # header / separator / non-data row
        machine_cmd = cells[6]
        assert "ai_sdlc_tools_version_forward_sync" not in machine_cmd, (
            f"TVFS-1 module cited in a shippability Machine-cmd cell (row "
            f"{cells[1]}) — the audit reads the environment-mutable installed "
            f"distribution; a Machine-cmd must not depend on environment-"
            f"mutable state (slice-029/030A). Only the two in-repo-only "
            f"entry-pin tests may carry row #59."
        )
