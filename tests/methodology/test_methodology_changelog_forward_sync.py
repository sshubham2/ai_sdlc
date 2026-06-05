"""MCFS-1 regression suite — `tools/methodology_changelog_forward_sync.py`.

Per **MCFS-1** (`methodology-changelog.md` v0.53.0; slice-041; ADR-042 +
ADR-043). Proves the gate's must-not-mask AND must-not-false-FAIL properties,
the BCI-1/slice-030A meta-M3 installed-absent→WARN parity, the EOL-DRIFT-1
CRLF-agnostic property, the CSP-1 behaviour-parity with the canonical
`_normalized_sha256` comparator, and the M-add-1 relocation proof (the MCFS-1
module is provably non-catalog).

This module reads the installed copy in its synced/divergent cases and is
therefore **intentionally NOT shippability-catalog-cited** (m-add-2): a
catalog row for it would make it an unregistered `essential` cited fn ⇒
`essential-unregistered` exit 1 self-violation. The MCFS-1 tool's WIRE-1
consumer-test obligation is discharged by this suite existing and passing,
not by cataloging it; only the in-repo-only-body entry-pin
`test_v_0_53_0_mcfs_1_entry_present_in_repo` carries the row.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools import methodology_changelog_forward_sync as mcfs
from tools._vault_paths import VAULT_ROOT


def _write(p: Path, text: str, *, newline: str) -> None:
    p.write_bytes(text.replace("\n", newline).encode("utf-8"))


# --------------------------------------------------------------------------- #
# must-not-false-FAIL: synced + EOL-agnostic (EOL-DRIFT-1)                     #
# --------------------------------------------------------------------------- #
def test_synced_tree_exit_0(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "methodology-changelog.md", "## v0.53.0\nMCFS-1\n",
           newline="\n")
    installed = tmp_path / "installed.md"
    _write(installed, "## v0.53.0\nMCFS-1\n", newline="\n")

    r = mcfs.check(root, installed=installed)
    assert r.status == "synced" and r.exit_code == 0, r.to_dict()


def test_crlf_only_difference_is_not_a_fail(tmp_path: Path):
    """In-repo CRLF vs installed LF, identical content ⇒ exit 0 (the R-5
    Windows false-FAIL class, suppressed by design)."""
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "methodology-changelog.md", "## v0.53.0\nMCFS-1\n",
           newline="\r\n")
    installed = tmp_path / "installed.md"
    _write(installed, "## v0.53.0\nMCFS-1\n", newline="\n")

    r = mcfs.check(root, installed=installed)
    assert r.status == "synced" and r.exit_code == 0, r.to_dict()


# --------------------------------------------------------------------------- #
# must-not-mask: genuine divergence HALTs                                      #
# --------------------------------------------------------------------------- #
def test_genuine_divergence_halts_exit_1(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "methodology-changelog.md", "## v0.53.0\nMCFS-1 NEW\n",
           newline="\n")
    installed = tmp_path / "installed.md"
    _write(installed, "## v0.52.0\nMEPD-1 STALE\n", newline="\n")

    r = mcfs.check(root, installed=installed)
    assert r.status == "drift" and r.exit_code == 1, r.to_dict()
    assert "NOT a slice regression" in r.divergences[0]


def test_empty_present_installed_is_divergent_halt(tmp_path: Path):
    """empty != absent — an empty present installed file HALTs (R-4-class
    not silently reopened)."""
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "methodology-changelog.md", "## v0.53.0\nMCFS-1\n",
           newline="\n")
    installed = tmp_path / "installed.md"
    installed.write_bytes(b"")

    r = mcfs.check(root, installed=installed)
    assert r.status == "drift" and r.exit_code == 1, r.to_dict()


# --------------------------------------------------------------------------- #
# installed-absent → WARN exit 0 (BCI-1 / slice-030A meta-M3 parity)           #
# --------------------------------------------------------------------------- #
def test_installed_absent_is_warn_exit_0(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "methodology-changelog.md", "## v0.53.0\nMCFS-1\n",
           newline="\n")
    installed = tmp_path / "does-not-exist.md"  # absent

    r = mcfs.check(root, installed=installed)
    assert r.status == "warn" and r.exit_code == 0, r.to_dict()
    assert "PASS (with WARN)" in mcfs._format_human(r)


# --------------------------------------------------------------------------- #
# in-repo missing ⇒ usage exit 2 (repo malformed, not vault drift)            #
# --------------------------------------------------------------------------- #
def test_in_repo_missing_is_usage_exit_2(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()  # no methodology-changelog.md
    installed = tmp_path / "installed.md"
    _write(installed, "x\n", newline="\n")

    r = mcfs.check(root, installed=installed)
    assert r.status == "usage" and r.exit_code == 2, r.to_dict()


# --------------------------------------------------------------------------- #
# CSP-1 behaviour-parity: MCFS-1 norm ≡ skill_drift_equality._normalized_sha256
# --------------------------------------------------------------------------- #
def test_csp1_normalization_parity_with_skill_drift_equality(tmp_path: Path):
    """MCFS-1's local 1-line CRLF→LF normalization MUST be byte-equivalent to
    the canonical EOL-DRIFT-1 comparator. Pins "reuses the semantics, does not
    re-derive a different one" as a mechanical CSP-1 contract (slice-038
    object/behaviour-parity precedent), so a future drift in either is loud.
    """
    from tests.skill_drift_equality import _normalized_sha256

    for nl in ("\n", "\r\n"):
        p = tmp_path / f"f_{len(nl)}.md"
        _write(p, "## v0.53.0 — 2026-05-18\nMCFS-1 line\nsecond\n", newline=nl)
        mcfs_hash = hashlib.sha256(mcfs._normalized_bytes(p)).hexdigest()
        assert mcfs_hash == _normalized_sha256(p), (
            f"MCFS-1 normalization diverged from skill_drift_equality "
            f"._normalized_sha256 on newline={nl!r}"
        )


# --------------------------------------------------------------------------- #
# M-add-1 relocation proof: MCFS-1 is provably non-catalog                     #
# --------------------------------------------------------------------------- #
def test_mcfs1_module_is_non_catalog_relocation_proof():
    """The compensating forward-sync guard MUST NOT itself become the
    relocated essential coupling: the MCFS-1 module is never resolved by
    `tools.shippability_decoupling_audit`'s closed-world cited-fn derivation
    over the REAL catalog, and is cited in NO `Machine-cmd` cell. Mechanical
    M-add-1 discharge (not prose) — executed against the real artifact.
    """
    from tools import shippability_decoupling_audit as scda

    catalog = REPO_ROOT / VAULT_ROOT / "shippability.md"
    result = scda.audit(catalog)
    all_quals = (
        list(result.incidental)
        + list(result.essential)
        + list(result.clean)
    )
    assert all(
        "methodology_changelog_forward_sync" not in q for q in all_quals
    ), (
        "MCFS-1 module resolved as a catalog-cited fn — the compensating "
        "guard relocated the essential coupling (M-add-1 violation)"
    )
    # m-add-2: the MCFS-1 module must not be CITED (resolved by `_cited()`
    # from a Machine-cmd cell). Row #41's *Critical-path prose* legitimately
    # names `tools/methodology_changelog_forward_sync.py` (description of what
    # the row guards) — the invariant is about the executable **Machine-cmd
    # column (6th cell)**, NOT raw catalog text. Parse the Machine-cmd cell
    # per data row and assert the module is absent there.
    for line in catalog.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.split("|")]
        # | '' | # | Slice | Critical path | Command | Runtime | Machine-cmd | ''
        if len(cells) < 8 or not cells[1].isdigit():
            continue  # header / separator / non-data row
        machine_cmd = cells[6]
        assert "methodology_changelog_forward_sync" not in machine_cmd, (
            f"MCFS-1 module cited in a shippability Machine-cmd cell (row "
            f"{cells[1]}) — the regression suite reads installed → would be "
            f"essential-unregistered if cited (m-add-2 negative invariant); "
            f"only the in-repo-only entry-pin may carry the row"
        )
