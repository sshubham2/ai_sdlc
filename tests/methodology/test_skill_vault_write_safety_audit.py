"""SVW-1 audit contract + APED-1 adversarial battery (slice-095 / [[ADR-087]]).

Executes the newly-minted matcher against the REAL 26-skill corpus AND a
planted adversarial battery in BOTH directions (BC-PROJ-13 / regex-APED-1).
The corpus assertions pin the FP/FN boundary the build measured: the matcher
must stay clean on the routed tree, flag a planted raw write, and NOT flag the
known false-positive shapes (build-slice:394 noun-`flip`, ~/.claude global,
`post-write` compound, bare un-backticked filename).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

from tools import skill_vault_write_safety_audit as svw  # noqa: E402
from tools.skill_vault_write_safety_audit import (  # noqa: E402
    _REGISTERED_SKILL_EXEMPTIONS,
    audit_root,
    main,
    registered_exemption_pairs,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _plant(tmp_path: Path, body: str) -> Path:
    """Write a one-skill tree at tmp_path/skills/fake/SKILL.md; return root."""
    sk = tmp_path / "skills" / "fake"
    sk.mkdir(parents=True, exist_ok=True)
    (sk / "SKILL.md").write_text(body, encoding="utf-8")
    return tmp_path


# ─── real-corpus contract: the routed tree is clean ─────────────────────


def test_real_corpus_is_clean() -> None:
    """The post-routing 26-skill corpus passes — every shared-vault mutation
    site is routed or validly exempted."""
    result = audit_root(_REPO_ROOT)
    assert result.status == "clean", (
        f"SVW-1 not clean on the real corpus: "
        f"{[(v.file, v.line) for v in result.violations]}"
    )
    assert result.skills_scanned >= 26


def test_build_slice_394_false_positive_excluded() -> None:
    """The NAW-1 bootstrap prose at build-slice (backticked
    `architecture/risk-register.md` governed only by the NOUN `flip`/`edit`)
    must NOT be flagged — the canonical APED-1 false-positive the Critic found."""
    result = audit_root(_REPO_ROOT)
    bs = [v for v in result.violations if "build-slice" in v.file]
    assert bs == [], f"build-slice false-positive regressed: {bs}"


# ─── planted battery: flag the unsafe, pass the safe ────────────────────


def test_flags_planted_raw_skill_append(tmp_path: Path) -> None:
    root = _plant(tmp_path, "### Step 1: Append to `architecture/risk-register.md` directly\n")
    result = audit_root(root)
    assert len(result.violations) == 1
    assert result.violations[0].kind == "unrouted"


def test_routed_site_is_clean(tmp_path: Path) -> None:
    root = _plant(
        tmp_path,
        "### Step 1: Append to `architecture/risk-register.md` via tools.vault_edit append\n",
    )
    assert audit_root(root).status == "clean"


def test_exempted_site_is_clean(tmp_path: Path) -> None:
    root = _plant(
        tmp_path,
        "Regenerate `architecture/slices/_index.md` <!-- vault-write-safe: deferred-rmw -->\n",
    )
    res = audit_root(root)
    assert res.status == "clean"
    assert len(res.exemptions) == 1 and res.exemptions[0].reason == "deferred-rmw"


def test_unknown_exemption_reason_is_violation(tmp_path: Path) -> None:
    """A marker whose reason is not in the closed enum is a VIOLATION (M3 — a
    free-text reason cannot silently green the gate)."""
    root = _plant(
        tmp_path,
        "Append to `architecture/risk-register.md` <!-- vault-write-safe: whatever -->\n",
    )
    res = audit_root(root)
    assert len(res.violations) == 1
    assert res.violations[0].kind == "unknown-exemption-reason"


# ─── planted battery: the FP shapes the matcher must NOT flag ────────────


def test_bare_mention_not_flagged(tmp_path: Path) -> None:
    """A directive verb + an UN-backticked filename is descriptive prose, not a
    site (reflect:386 'Update risk-register.md said ...')."""
    root = _plant(tmp_path, "Note: risk-register.md said R3 was retired; update risk-register.md later.\n")
    assert audit_root(root).status == "clean"


def test_global_claude_file_not_flagged(tmp_path: Path) -> None:
    """A ~/.claude/ GLOBAL file is not the architecture/ vault (reflect:207)."""
    root = _plant(tmp_path, "Also offer to append it to `~/.claude/build-checks.md` with a BC-GLOBAL-NNN ID.\n")
    assert audit_root(root).status == "clean"


def test_hyphen_compound_verb_not_flagged(tmp_path: Path) -> None:
    """'post-write' is a compound noun, not a directive verb (reflect:209)."""
    root = _plant(tmp_path, "BCI-1 fail-loud post-write step — per BCI-1 (`methodology-changelog.md` v0.44.0).\n")
    assert audit_root(root).status == "clean"


def test_noun_after_codespan_not_flagged(tmp_path: Path) -> None:
    """A verb used as a noun right after a code span ( `X.md` edit ) is excluded."""
    root = _plant(
        tmp_path,
        "The slice ships a `tools/x.py` audit + `skills/build-slice/SKILL.md` edit + `architecture/risk-register.md` flip.\n",
    )
    assert audit_root(root).status == "clean"


def test_per_slice_file_not_in_shared_set(tmp_path: Path) -> None:
    """A directive on a per-slice-folder file (mission-brief.md) is out of the
    shared-aggregate set — isolated by construction, never flagged."""
    root = _plant(tmp_path, "Write `architecture/slices/slice-NNN/mission-brief.md` with the brief.\n")
    assert audit_root(root).status == "clean"


def test_fenced_code_block_skipped(tmp_path: Path) -> None:
    """A directive inside a ``` fence is example/template content, not a site."""
    root = _plant(
        tmp_path,
        "```markdown\nAppend to `architecture/risk-register.md` raw\n```\n",
    )
    assert audit_root(root).status == "clean"


# ─── M3: the exemption allowlist is pinned (off-allowlist → regression) ──


def test_exemption_allowlist_pinned() -> None:
    """The (skill, reason) exemption set actually present in the corpus MUST
    equal the pinned _REGISTERED_SKILL_EXEMPTIONS. A NEW exemption added by a
    future skill edit (or a removed one) trips this — keeping 'visible residual'
    enforced, not self-asserted (closes the per-line `# noqa` bypass M3)."""
    found = registered_exemption_pairs(_REPO_ROOT)
    assert found == set(_REGISTERED_SKILL_EXEMPTIONS), (
        f"exemption allowlist drift — off-allowlist: {found - set(_REGISTERED_SKILL_EXEMPTIONS)}; "
        f"missing: {set(_REGISTERED_SKILL_EXEMPTIONS) - found}"
    )


def test_exempt_reasons_are_closed() -> None:
    """The reason enum is closed (M3) — exactly the two sanctioned reasons."""
    assert svw._EXEMPT_REASONS == frozenset({"deferred-rmw", "project-open-single-shot"})


# ─── CLI exit-code contract ─────────────────────────────────────────────


def test_main_exit_zero_on_clean_corpus(capsys: pytest.CaptureFixture) -> None:
    rc = main(["--root", str(_REPO_ROOT)])
    assert rc == 0


def test_main_exit_one_on_violation(tmp_path: Path) -> None:
    _plant(tmp_path, "Append to `architecture/risk-register.md` raw\n")
    rc = main(["--root", str(tmp_path)])
    assert rc == 1


def test_main_exit_two_on_missing_skills(tmp_path: Path) -> None:
    rc = main(["--root", str(tmp_path / "nonexistent")])
    assert rc == 2
