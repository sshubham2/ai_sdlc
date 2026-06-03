"""VWS-1 audit contract + APED-1 adversarial battery (slice-094 / [[ADR-086]]).

Executes the newly-minted per-write-target AST matcher against the REAL
``tools/`` corpus AND a planted adversarial battery in BOTH directions
(BC-PROJ-13 / AST-APED-1). The corpus assertions pin the FP/FN boundary the
build measured: clean on the routed tree, 6 CLEAN-SCOPED-OUT PCR ops, and the
matcher must NOT false-positive on a reader-with-a-non-vault-write or an
error-prose-only vault-literal mention (the M1 per-write-target guarantee), AND
must NOT false-negative the ``var = root/"architecture"/"x.md"; var.write_text()``
≤1-hop shape (the depth lock). Bounded-resolution residuals (2-hop alias,
container element) are pinned VISIBLE — never silently assumed closed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

from tools import vault_write_safety_audit as vws  # noqa: E402
from tools.vault_write_safety_audit import (  # noqa: E402
    _REGISTERED_SCOPED_OUT,
    audit_root,
    main,
    registered_scoped_out_counts,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _plant(tmp_path: Path, name: str, body: str) -> Path:
    """Write a one-module tree at tmp_path/tools/<name>.py; return the root."""
    tools = tmp_path / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    (tools / f"{name}.py").write_text(body, encoding="utf-8")
    return tmp_path


# ─── real-corpus contract: the routed tree is clean ─────────────────────


def test_real_corpus_is_clean() -> None:
    """The post-routing tools/ corpus passes — every vault write is routed,
    exempt, or on the scoped-out allowlist."""
    result = audit_root(_REPO_ROOT)
    assert result.status == "clean", (
        f"VWS-1 not clean on the real corpus: "
        f"{[(v.file, v.line, v.channel) for v in result.violations]}"
    )
    assert result.tools_scanned >= 40


def test_real_corpus_pcr_is_scoped_out_not_violation() -> None:
    """All 6 resolvable PCR vault writes classify CLEAN-SCOPED-OUT (git-coupled;
    retire at the flip) — never VIOLATION."""
    result = audit_root(_REPO_ROOT)
    pcr = [c for c in result.scoped_out if c.module_stem == "parallel_conflict_resolver"]
    assert len(pcr) == 6, f"expected 6 scoped-out PCR ops, got {[(c.line, c.channel) for c in pcr]}"
    assert all(v.file != "tools/parallel_conflict_resolver.py" for v in result.violations)


def test_real_corpus_seam_writers_routed() -> None:
    """The 2 seam writers + vault_edit + _vault_write's config-writer all route
    through the safe channel (>=4 routed call sites counted)."""
    result = audit_root(_REPO_ROOT)
    assert result.sites_routed >= 4


# ─── planted battery: flag the unsafe ───────────────────────────────────


def test_flags_planted_raw_vault_write(tmp_path: Path) -> None:
    """The canonical FN guard: a raw write_text to an architecture/ literal in a
    non-exempt, non-scoped-out module is a VIOLATION naming file:line."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    (root / 'architecture' / 'risk-register.md').write_text('x')\n",
    )
    result = audit_root(root)
    assert len(result.violations) == 1
    assert result.violations[0].channel == ".write_text"
    assert result.violations[0].line == 3


def test_depth_lock_one_hop_assignment_is_violation(tmp_path: Path) -> None:
    """The M2 depth lock: the ``var = root/"architecture"/"x.md";
    var.write_text()`` shape (all 4 real writers + 6 PCR ops use it) MUST resolve
    to a VIOLATION — a 0-hop-only matcher would silently miss it (fail-open)."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    out_path = root / 'architecture' / 'slice-queue.md'\n"
        "    out_path.write_text('x')\n",
    )
    result = audit_root(root)
    assert len(result.violations) == 1
    assert result.violations[0].line == 4


def test_module_const_target_is_violation(tmp_path: Path) -> None:
    """Module-level Path constant resolution (hop ii) — the PCR _AUDIT_LOG_PATH
    shape: a write to a module const that names an architecture/ path is caught."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "_LOG = Path('architecture/parallel-conflict-resolution-log.md')\n"
        "def f(root: Path) -> None:\n"
        "    log_path = root / _LOG\n"
        "    with log_path.open('a', encoding='utf-8') as fh:\n"
        "        fh.write('x')\n",
    )
    result = audit_root(root)
    assert len(result.violations) == 1
    assert result.violations[0].channel == ".open"


def test_vault_basename_without_architecture_segment_is_violation(tmp_path: Path) -> None:
    """Secondary signal: a known vault basename catches a write even when the
    literal omits the 'architecture' segment."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(d: Path) -> None:\n"
        "    (d / 'risk-register.md').write_text('x')\n",
    )
    assert audit_root(root).status == "violation"


def test_vault_root_derived_target_is_violation(tmp_path: Path) -> None:
    """Tertiary (post-flip) signal: a target derived from the VAULT_ROOT seam is
    a vault write even with no literal 'architecture' segment."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "from tools._vault_paths import VAULT_ROOT\n"
        "def f() -> None:\n"
        "    (VAULT_ROOT / 'whatever.md').write_text('x')\n",
    )
    assert audit_root(root).status == "violation"


@pytest.mark.parametrize(
    "channel_body,channel",
    [
        ("    import os\n    os.replace('tmp', root / 'architecture' / 'x.md')\n", "os.replace"),
        ("    open(root / 'architecture' / 'x.md', 'w').close()\n", "open"),
        (
            "    import os\n"
            "    fd = os.open(root / 'architecture' / 'x.md', os.O_WRONLY | os.O_CREAT)\n"
            "    os.close(fd)\n",
            "os.open",
        ),
        ("    (root / 'architecture' / 'x.md').open('a').close()\n", ".open"),
        # /code-review M1 — channels added to close the fail-OPEN gap:
        ("    import os\n    os.rename('tmp', root / 'architecture' / 'x.md')\n", "os.rename"),
        ("    import io\n    io.open(root / 'architecture' / 'x.md', 'w').close()\n", "io.open"),
        ("    import shutil\n    shutil.move('tmp', root / 'architecture' / 'x.md')\n", "shutil.move"),
        ("    import shutil\n    shutil.copyfile('tmp', root / 'architecture' / 'x.md')\n", "shutil.copyfile"),
    ],
)
def test_all_write_channels_flagged(tmp_path: Path, channel_body: str, channel: str) -> None:
    """Every recognised raw write channel flags a vault target: write_text (above),
    os.replace/os.rename dst, builtin open(w)/io.open(w), os.open(write-flags),
    Path.open(a), shutil.move/copyfile dst (the M1 channel-set — /code-review)."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n" + channel_body,
    )
    result = audit_root(root)
    assert any(v.channel == channel for v in result.violations), (
        f"channel {channel!r} not flagged: {[v.channel for v in result.violations]}"
    )


# ─── planted battery: the FP shapes the matcher must NOT flag ────────────


def test_os_open_readonly_create_not_flagged(tmp_path: Path) -> None:
    """m1 (/code-review): `os.open(target, O_RDONLY|O_CREAT)` is a create-for-READ,
    NOT a write — bare O_CREAT no longer triggers (a write needs O_WRONLY/O_RDWR/O_APPEND)."""
    root = _plant(
        tmp_path, "reader",
        "import os\n"
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    fd = os.open(root / 'architecture' / 'x.md', os.O_RDONLY | os.O_CREAT)\n"
        "    os.close(fd)\n",
    )
    assert audit_root(root).status == "clean"


def test_reader_with_non_vault_write_not_flagged(tmp_path: Path) -> None:
    """The M1 false-positive guard: a module that WRITES a non-vault file
    (graphify-out/) is CLEAN — vault-target-only by construction."""
    root = _plant(
        tmp_path, "reader",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    out = root / 'graphify-out' / 'graph.json'\n"
        "    out.write_text('{}')\n",
    )
    assert audit_root(root).status == "clean"


def test_error_prose_only_vault_literal_not_flagged(tmp_path: Path) -> None:
    """The canonical M1 FP: a module that only MENTIONS a vault literal in an
    error string / a `git show` subprocess arg (no write op) is CLEAN. This is
    the per-write-target win over the v1 module-mention tripwire."""
    root = _plant(
        tmp_path, "reader",
        "import subprocess\n"
        "def f(repo_root) -> str:\n"
        "    msg = 'see architecture/risk-register.md for the register'\n"
        "    subprocess.run(['git', 'show', 'architecture/risk-register.md'])\n"
        "    return msg\n",
    )
    assert audit_root(root).status == "clean"


def test_read_text_of_vault_literal_not_flagged(tmp_path: Path) -> None:
    """A READ of a vault file is not a write op (read_text)."""
    root = _plant(
        tmp_path, "reader",
        "from pathlib import Path\n"
        "def f(root: Path) -> str:\n"
        "    return (root / 'architecture' / 'risk-register.md').read_text()\n",
    )
    assert audit_root(root).status == "clean"


def test_routed_call_not_flagged_and_counted(tmp_path: Path) -> None:
    """A safe_write_text call is the routed safe channel — CLEAN, counted as a
    routed site (never a raw write op)."""
    root = _plant(
        tmp_path, "good",
        "from tools._vault_write import safe_write_text\n"
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    safe_write_text(root / 'architecture' / 'risk-register.md', 'x')\n",
    )
    result = audit_root(root)
    assert result.status == "clean"
    assert result.sites_routed == 1


def test_safe_rewrite_text_recognized_as_routed(tmp_path: Path) -> None:
    """slice-109 / ADR-098 (AC3): a safe_rewrite_text call WITH a non-constant
    expected_base= is the routed CAS channel — CLEAN, counted as a routed site."""
    root = _plant(
        tmp_path, "good_cas",
        "from tools._vault_write import safe_rewrite_text\n"
        "from pathlib import Path\n"
        "def f(root: Path, base: bytes) -> None:\n"
        "    safe_rewrite_text(root / 'architecture' / 'slice-queue.md', 'x', expected_base=base)\n",
    )
    result = audit_root(root)
    assert result.status == "clean"
    assert result.sites_routed == 1


def test_safe_rewrite_text_degenerate_base_flagged(tmp_path: Path) -> None:
    """slice-109 / ADR-098 (Critic m1): a safe_rewrite_text call with a CONSTANT
    expected_base (e.g. b"") is CAS-defeating — NOT auto-cleaned; it surfaces as an
    un-routed vault write VIOLATION rather than a silent skip."""
    root = _plant(
        tmp_path, "evil_cas",
        "from tools._vault_write import safe_rewrite_text\n"
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    safe_rewrite_text(root / 'architecture' / 'slice-queue.md', 'x', expected_base=b'')\n",
    )
    result = audit_root(root)
    assert len(result.violations) == 1, (
        f"degenerate constant-base safe_rewrite_text not flagged: {result.violations}"
    )
    assert result.violations[0].channel == "safe_rewrite_text"
    assert result.sites_routed == 0


def test_safe_rewrite_text_name_bound_constant_base_flagged(tmp_path: Path) -> None:
    """slice-109 / code-review M1: the name-indirection CAS-defeat — `expected_base`
    bound to a MODULE-LEVEL constant (`_EMPTY = b''`) — resolves to a constant and
    is FLAGGED, not just the literal form. A genuinely dynamic/local base stays
    routed (covered by test_safe_rewrite_text_recognized_as_routed)."""
    root = _plant(
        tmp_path, "name_bound_cas",
        "from tools._vault_write import safe_rewrite_text\n"
        "from pathlib import Path\n"
        "_EMPTY = b''\n"
        "def f(root: Path) -> None:\n"
        "    safe_rewrite_text(root / 'architecture' / 'slice-queue.md', 'x', expected_base=_EMPTY)\n",
    )
    result = audit_root(root)
    assert len(result.violations) == 1, (
        f"name-bound constant-base CAS-defeat not flagged: {result.violations}"
    )
    assert result.violations[0].channel == "safe_rewrite_text"
    assert result.sites_routed == 0


def test_routed_funcs_pinned() -> None:
    """slice-109 / ADR-098 (AC3): the routed-channel set is pinned CLOSED — a 4th
    channel needs an explicit, reviewed change (no silent widening of the hole)."""
    assert vws._ROUTED_FUNCS == frozenset(
        {"safe_write_text", "safe_append_text", "safe_rewrite_text"}
    )


def test_tmp_target_not_flagged(tmp_path: Path) -> None:
    """A write to a .tmp sibling (the atomic-replace staging file) is not a vault
    write — its name does not resolve to a vault literal."""
    root = _plant(
        tmp_path, "writer",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    tmp = root / 'scratch.tmp'\n"
        "    tmp.write_text('x')\n",
    )
    assert audit_root(root).status == "clean"


# ─── classification: exempt + scoped-out ─────────────────────────────────


def test_vault_write_module_is_exempt(tmp_path: Path) -> None:
    """A raw vault write inside a module named _vault_write is EXEMPT (the
    sanctioned primitive impl) — never a violation."""
    root = _plant(
        tmp_path, "_vault_write",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    (root / 'architecture' / 'x.md').write_text('x')\n",
    )
    result = audit_root(root)
    assert result.status == "clean"
    assert len(result.exempt) == 1 and result.exempt[0].verdict == "exempt"


def test_scoped_out_module_is_clean(tmp_path: Path) -> None:
    """A raw vault write inside the scoped-out allowlist module
    (parallel_conflict_resolver) classifies CLEAN-SCOPED-OUT, not VIOLATION."""
    root = _plant(
        tmp_path, "parallel_conflict_resolver",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    (root / 'architecture' / 'slice-queue.md').write_text('x')\n",
    )
    result = audit_root(root)
    assert result.status == "clean"
    assert len(result.scoped_out) == 1 and result.scoped_out[0].verdict == "scoped-out"


# ─── bounded-resolution residuals: pinned VISIBLE (documented, not silent) ─


def test_two_hop_alias_is_documented_residual(tmp_path: Path) -> None:
    """The depth bound is ≤1 hop: a 2-hop alias (b = a; b.write_text()) does NOT
    resolve → NOT flagged. This is the deliberate decidability tradeoff vs the
    rejected undecidable interprocedural dataflow — pinned VISIBLE so the bound
    is not silently assumed tighter than it is. If a future hop-2 resolver lands,
    this test flips and the docstring/`hops_left` comment must be updated."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    a = root / 'architecture' / 'x.md'\n"
        "    b = a\n"
        "    b.write_text('x')\n",
    )
    assert audit_root(root).status == "clean"  # residual: NOT flagged (documented)


def test_container_element_is_documented_residual(tmp_path: Path) -> None:
    """The PCR :430 shape: a for-loop tuple-unpack write target (container
    element) does NOT resolve → NOT flagged. The documented accepted residual —
    pinned VISIBLE (the real PCR :430 is excluded from the scoped-out count of 6
    for exactly this reason)."""
    root = _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(pending) -> None:\n"
        "    for out_path, content in pending:\n"
        "        out_path.write_text(content)\n",
    )
    assert audit_root(root).status == "clean"  # residual: NOT flagged (documented)


# ─── M3: the scoped-out allowlist is COUNT-pinned ────────────────────────


def test_scoped_out_allowlist_pinned() -> None:
    """The per-module CLEAN-SCOPED-OUT COUNT actually present in the corpus MUST
    equal the pinned _REGISTERED_SCOPED_OUT dict. Adding a scoped-out vault op to
    PCR (or a whole new scoped-out module) changes this count and trips the pin —
    fail-closed against silent scope creep (slice-095 _REGISTERED_* shape)."""
    found = registered_scoped_out_counts(_REPO_ROOT)
    assert found == _REGISTERED_SCOPED_OUT, (
        f"scoped-out allowlist drift — live counts {found} != pinned {_REGISTERED_SCOPED_OUT}"
    )


def test_scoped_out_allowlist_membership() -> None:
    """Exactly one module is scoped out (PCR), and it carries a rationale."""
    assert set(_REGISTERED_SCOPED_OUT) == {"parallel_conflict_resolver"}
    assert "git-coupled" in vws._SCOPED_OUT_RATIONALE


# ─── CLI exit-code contract ──────────────────────────────────────────────


def test_main_exit_zero_on_clean_corpus(capsys: pytest.CaptureFixture) -> None:
    rc = main(["--repo-root", str(_REPO_ROOT)])
    assert rc == 0


def test_main_exit_one_on_violation(tmp_path: Path) -> None:
    _plant(
        tmp_path, "evil",
        "from pathlib import Path\n"
        "def f(root: Path) -> None:\n"
        "    (root / 'architecture' / 'risk-register.md').write_text('x')\n",
    )
    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 1


def test_main_exit_two_on_missing_tools(tmp_path: Path) -> None:
    rc = main(["--repo-root", str(tmp_path / "nonexistent")])
    assert rc == 2


def test_unparseable_tool_is_usage_error(tmp_path: Path) -> None:
    """An unparseable tools/*.py is a fail-VISIBLE usage error (exit 2), NOT a
    silent skip (the R-7 silent-disable class)."""
    _plant(tmp_path, "broken", "def f(:\n")  # SyntaxError
    rc = main(["--repo-root", str(tmp_path)])
    assert rc == 2
