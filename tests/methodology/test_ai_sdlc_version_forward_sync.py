"""AVFS-1 regression suite — `tools/ai_sdlc_version_forward_sync.py`.

Per **AVFS-1** (`methodology-changelog.md` v0.58.0; slice-050; ADR-052;
extends the slice-041/MCFS-1 forward-sync-via-deterministic-downstream-gate
lineage; mints a new rule; supersedes nothing). Structural twin of
`test_methodology_changelog_forward_sync.py` (MCFS-1 suite), retargeted from
`methodology-changelog.md` ↔ `~/.claude/methodology-changelog.md` to
`VERSION` ↔ `~/.claude/ai-sdlc-VERSION`.

Proves the gate's must-not-mask AND must-not-false-FAIL properties, the
slice-030A meta-M3 installed-absent→WARN parity, the EOL-DRIFT-1 CRLF-agnostic
property, the CSP-1 behaviour-parity with the canonical `_normalized_sha256`
comparator, the 2-point SKILL.md wiring (build-slice Step 6 + reflect
post-write step), and the M-add-1/M3 relocation proof (the AVFS-1 module is
provably non-catalog — it reads the untracked, environment-mutable installed
copy; a Machine-cmd row depending on environment-mutable state is the
slice-029/030A discipline this asserts, NOT essential-unregistered which keys
on the changelog path only).

This module reads the installed copy in its synced/divergent cases and is
therefore **intentionally NOT shippability-catalog-cited**: only the two
in-repo-only entry-pins
`test_methodology_changelog.py::test_v_0_58_0_avfs_1_entry_present_in_repo`
+ `::test_v_0_58_0_avfs_1_shippability_consumer_propagation` carry row #50.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools import ai_sdlc_version_forward_sync as avfs
from tools._vault_paths import VAULT_ROOT


def _write(p: Path, text: str, *, newline: str) -> None:
    p.write_bytes(text.replace("\n", newline).encode("utf-8"))


# --------------------------------------------------------------------------- #
# must-not-false-FAIL: synced + EOL-agnostic (EOL-DRIFT-1)                     #
# --------------------------------------------------------------------------- #
def test_synced_when_in_repo_equals_installed(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "VERSION", "0.58.0\n", newline="\n")
    installed = tmp_path / "ai-sdlc-VERSION"
    _write(installed, "0.58.0\n", newline="\n")

    r = avfs.check(root, installed=installed)
    assert r.status == "synced" and r.exit_code == 0, r.to_dict()


def test_crlf_only_difference_is_not_a_fail(tmp_path: Path):
    """In-repo CRLF vs installed LF, identical content ⇒ exit 0 (the R-5
    Windows false-FAIL class, suppressed by the verbatim CRLF→LF
    normalization — B3)."""
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "VERSION", "0.58.0\n", newline="\r\n")
    installed = tmp_path / "ai-sdlc-VERSION"
    _write(installed, "0.58.0\n", newline="\n")

    r = avfs.check(root, installed=installed)
    assert r.status == "synced" and r.exit_code == 0, r.to_dict()


# --------------------------------------------------------------------------- #
# must-not-mask: genuine divergence HALTs                                      #
# --------------------------------------------------------------------------- #
def test_divergent_halts_exit1_with_attribution(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "VERSION", "0.58.0\n", newline="\n")
    installed = tmp_path / "ai-sdlc-VERSION"
    _write(installed, "0.57.0\n", newline="\n")

    r = avfs.check(root, installed=installed)
    assert r.status == "drift" and r.exit_code == 1, r.to_dict()
    assert "NOT a slice regression" in r.divergences[0], r.divergences


def test_empty_present_installed_halts(tmp_path: Path):
    """empty != absent — an empty present installed file HALTs (R-4-class
    not silently reopened)."""
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "VERSION", "0.58.0\n", newline="\n")
    installed = tmp_path / "ai-sdlc-VERSION"
    installed.write_bytes(b"")

    r = avfs.check(root, installed=installed)
    assert r.status == "drift" and r.exit_code == 1, r.to_dict()


def test_whitespace_only_present_installed_halts(tmp_path: Path):
    """A whitespace-only present installed file (`\\n`, ` `, `\\r\\n`) is the
    same class as empty-present → HALT (M4). Resolved by construction under
    the verbatim CRLF→LF-only comparator (no trailing-whitespace strip): a
    trailing-whitespace-tolerant comparator would false-sync `0.58.0 \\n` vs
    `0.58.0` — explicitly rejected (B3)."""
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "VERSION", "0.58.0\n", newline="\n")
    for i, blob in enumerate((b"\n", b" ", b"\r\n", b"0.58.0 \n")):
        installed = tmp_path / f"ws-{i}.txt"
        installed.write_bytes(blob)
        r = avfs.check(root, installed=installed)
        assert r.status == "drift" and r.exit_code == 1, (blob, r.to_dict())


# --------------------------------------------------------------------------- #
# installed-absent → WARN exit 0 (BCI-1 / slice-030A meta-M3 parity)           #
# --------------------------------------------------------------------------- #
def test_installed_absent_is_warn_exit0(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "VERSION", "0.58.0\n", newline="\n")
    installed = tmp_path / "does-not-exist"  # absent

    r = avfs.check(root, installed=installed)
    assert r.status == "warn" and r.exit_code == 0, r.to_dict()
    assert "PASS (with WARN)" in avfs._format_human(r)


# --------------------------------------------------------------------------- #
# in-repo missing ⇒ usage exit 2 (repo malformed, not vault drift)            #
# --------------------------------------------------------------------------- #
def test_in_repo_missing_is_usage_exit2(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()  # no VERSION
    installed = tmp_path / "ai-sdlc-VERSION"
    _write(installed, "0.58.0\n", newline="\n")

    r = avfs.check(root, installed=installed)
    assert r.status == "usage" and r.exit_code == 2, r.to_dict()


# --------------------------------------------------------------------------- #
# CSP-1 behaviour-parity: AVFS-1 norm ≡ skill_drift_equality._normalized_sha256
# --------------------------------------------------------------------------- #
def test_csp1_normalization_parity_with_skill_drift_equality(tmp_path: Path):
    """AVFS-1's local 1-line CRLF→LF normalization MUST be byte-equivalent to
    the canonical EOL-DRIFT-1 comparator (the same CSP-1 contract MCFS-1
    pins). A future divergence in either is loud. This is the structural
    reason the comparator MUST stay CRLF→LF-only (B3): any trailing-whitespace
    tolerance would break parity with `_normalized_sha256`."""
    from tests.skill_drift_equality import _normalized_sha256

    for nl in ("\n", "\r\n"):
        p = tmp_path / f"f_{len(nl)}.txt"
        _write(p, "0.58.0\n", newline=nl)
        avfs_hash = hashlib.sha256(avfs._normalized_bytes(p)).hexdigest()
        assert avfs_hash == _normalized_sha256(p), (
            f"AVFS-1 normalization diverged from skill_drift_equality."
            f"_normalized_sha256 on newline={nl!r}"
        )


# --------------------------------------------------------------------------- #
# 2-point wiring: build-slice Step 6 + reflect dedicated post-write step       #
# (reads in-repo SKILL.md only → classifies `clean`)                           #
# --------------------------------------------------------------------------- #
def test_wired_in_build_slice_step6_and_reflect_post_write():
    """AVFS-1 MUST be wired at the same two enforcement points MCFS-1 uses:
    `/build-slice` Step 6 pre-finish + a dedicated `/reflect` post-write step
    (NOT folded into the rule-promotion-gated Step 5b). Both SKILL.md reads
    are in-repo (git-tracked) → no `Path.home()` → classifies `clean`. This
    is an AVFS-1 addition (MCFS-1 has no wiring-assertion test — it discharges
    WIRE-1 by the suite existing+passing); not an MCFS-1 precedent."""
    bs = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(
        encoding="utf-8")
    rf = (REPO_ROOT / "skills" / "reflect" / "SKILL.md").read_text(
        encoding="utf-8")

    assert "tools.ai_sdlc_version_forward_sync" in bs, (
        "build-slice/SKILL.md missing the AVFS-1 invocation — Step 6 "
        "pre-finish wiring absent (the gate would never run at /build-slice)"
    )
    assert "AVFS-1" in bs, (
        "build-slice/SKILL.md missing the 'AVFS-1' rule reference in its "
        "Step 6 audit block"
    )
    assert "tools.ai_sdlc_version_forward_sync" in rf, (
        "reflect/SKILL.md missing the AVFS-1 invocation — the dedicated "
        "post-write step is absent (R-7/slice-022 silent-disable class on a "
        "version-bumping-but-no-rule-promoted slice)"
    )
    assert "AVFS-1" in rf, (
        "reflect/SKILL.md missing the 'AVFS-1' rule reference in its "
        "dedicated post-write step"
    )
    assert "Step 5b-avfs" in rf, (
        "reflect/SKILL.md AVFS-1 step is not a DEDICATED step — it must NOT "
        "be folded into the rule-promotion-gated Step 5b (m1/DR-1 / MCFS-1 "
        "Step 5b-fs parity)"
    )


# --------------------------------------------------------------------------- #
# M-add-1 / M3 relocation proof: AVFS-1 module is provably non-catalog         #
# --------------------------------------------------------------------------- #
def test_avfs1_module_is_non_catalog_relocation_proof():
    """The compensating forward-sync guard MUST NOT itself become a
    catalog-cited fn: the AVFS-1 module is never resolved by
    `tools.shippability_decoupling_audit`'s closed-world cited-fn derivation
    over the REAL catalog, and is cited in NO `Machine-cmd` cell. The
    non-catalog ground is the slice-029/030A environment-mutable-state
    discipline (the regression suite reads the untracked
    `~/.claude/ai-sdlc-VERSION`), NOT essential-unregistered — `_ESSENTIAL_
    SHAPES` keys on the changelog path only (M3). Mechanical discharge
    against the real artifact, not prose."""
    from tools import shippability_decoupling_audit as scda

    catalog = REPO_ROOT / VAULT_ROOT / "shippability.md"
    result = scda.audit(catalog)
    all_quals = (
        list(result.incidental)
        + list(result.essential)
        + list(result.clean)
    )
    assert all(
        "ai_sdlc_version_forward_sync" not in q for q in all_quals
    ), (
        "AVFS-1 module resolved as a catalog-cited fn — the compensating "
        "guard relocated into the catalog (relocation violation)"
    )
    # The AVFS-1 module must not be cited in any executable Machine-cmd cell
    # (6th column). Row #50's Critical-path prose may legitimately name the
    # module (description of what the row guards); the invariant is about the
    # Machine-cmd column, NOT raw catalog text.
    for line in catalog.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 8 or not cells[1].isdigit():
            continue  # header / separator / non-data row
        machine_cmd = cells[6]
        assert "ai_sdlc_version_forward_sync" not in machine_cmd, (
            f"AVFS-1 module cited in a shippability Machine-cmd cell (row "
            f"{cells[1]}) — the regression suite reads the untracked "
            f"environment-mutable ~/.claude/ai-sdlc-VERSION; a Machine-cmd "
            f"must not depend on environment-mutable state (slice-029/030A). "
            f"Only the two in-repo-only test_methodology_changelog.py pins "
            f"may carry row #50."
        )
