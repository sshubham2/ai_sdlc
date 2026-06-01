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
    registered_exemption_counts,
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
    """A genuine route: the token inside a backtick code span (the corpus
    convention). M1-hardened: a BARE prose token no longer cleans (see
    test_m1_negated_route_bare_is_violation)."""
    root = _plant(
        tmp_path,
        "### Step 1: Append to `architecture/risk-register.md` via `tools.vault_edit append`\n",
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


# ─── slice-095 code-review hardening: M1 negation, M2 lexicon, m1 fences ─


def test_m1_negated_route_bare_is_violation(tmp_path: Path) -> None:
    """M1: a BARE prose mention of a route token does not clean a site (it must
    sit in a backtick code span or `<!-- route: -->` marker). The canonical
    false-CLEAN the code-Critic executed: '...raw (do NOT use tools.vault_edit
    append here)'."""
    root = _plant(
        tmp_path,
        "Append to `architecture/risk-register.md` raw (do NOT use tools.vault_edit append here)\n",
    )
    res = audit_root(root)
    assert len(res.violations) == 1
    assert res.violations[0].kind == "unrouted"


def test_m1_negated_route_not_via_is_violation(tmp_path: Path) -> None:
    """M1: 'NOT via safe_append_text' — a bare, negated route token — is a
    VIOLATION, not a silent CLEAN."""
    root = _plant(
        tmp_path,
        "Append to `architecture/risk-register.md` NOT via safe_append_text\n",
    )
    assert audit_root(root).status == "violation"


def test_m1_predates_route_token_is_violation(tmp_path: Path) -> None:
    """M1: a historical cross-reference ('predates _vault_write') is description,
    not a routing instruction."""
    root = _plant(
        tmp_path,
        "Append to `architecture/risk-register.md` directly (this predates _vault_write)\n",
    )
    assert audit_root(root).status == "violation"


def test_m1_backticked_but_negated_route_is_violation(tmp_path: Path) -> None:
    """M1: even a BACKTICKED route token is demoted when locally negated (a
    negation within the ~2 words before the code span)."""
    root = _plant(
        tmp_path,
        "Append to `architecture/risk-register.md` — do NOT use `tools.vault_edit append`\n",
    )
    assert audit_root(root).status == "violation"


def test_m1_trailing_safety_assertion_stays_clean(tmp_path: Path) -> None:
    """M1 must NOT over-fire: a genuine route whose downstream safety assertion
    governs the RAW write ('never a raw `Write`/`Edit`') stays CLEAN — the
    real-corpus shape (validate-slice:296 / user-test:115). The short look-back
    keeps '(don't wait)' and the trailing 'never a raw' from demoting it."""
    root = _plant(
        tmp_path,
        "Add to `architecture/risk-register.md` immediately (don't wait) via "
        "`tools.vault_edit append` (SVW-1; never a raw `Write`/`Edit`).\n",
    )
    assert audit_root(root).status == "clean"


def test_m1_route_marker_form_is_clean(tmp_path: Path) -> None:
    """M1: the `<!-- route: tools.vault_edit append -->` marker form (reflect/
    reduce) is a genuine route."""
    root = _plant(
        tmp_path,
        "### Step 5: Append to `architecture/lessons-learned.md` <!-- route: tools.vault_edit append -->\n",
    )
    assert audit_root(root).status == "clean"


@pytest.mark.parametrize("verb", ["Insert", "Replace", "Prepend", "Modify", "Amend", "Create"])
def test_m2_expanded_verb_raw_write_is_violation(tmp_path: Path, verb: str) -> None:
    """M2: the expanded directive verbs now flag a raw write the original 6-verb
    lexicon passed CLEAN (the fail-OPEN hole the 'fail-closed' claim overstated)."""
    root = _plant(tmp_path, f"{verb} a row in `architecture/risk-register.md` by hand\n")
    res = audit_root(root)
    assert len(res.violations) == 1, f"{verb!r} raw write not flagged"
    assert res.violations[0].kind == "unrouted"


@pytest.mark.parametrize("verb", ["Note", "Set", "Log", "Mark", "Put", "Record"])
def test_m2_lexicon_bound_residual_is_documented(tmp_path: Path, verb: str) -> None:
    """M2 HONEST residual: noun-prone verbs are DELIBERATELY excluded (adding
    them false-positives on descriptive prose like slice:34 'Note on…' /
    slice:221 'reflection record'). A raw write phrased SOLELY with such a verb
    is a documented, visible residual — this test pins the known gap so it is
    not silently assumed closed. If a future disambiguator lets us add one of
    these, this test flips and the lexicon comment must be updated."""
    root = _plant(tmp_path, f"{verb} a value in `architecture/risk-register.md` by hand\n")
    assert audit_root(root).status == "clean"


def test_m1_tilde_fence_content_skipped(tmp_path: Path) -> None:
    """m1: a `~~~` fence (valid CommonMark) is tracked — a raw-write directive
    inside it is template/example content, not a site."""
    root = _plant(
        tmp_path,
        "~~~markdown\nAppend to `architecture/risk-register.md` raw\n~~~\n",
    )
    assert audit_root(root).status == "clean"


def test_m1_mixed_fence_char_does_not_close(tmp_path: Path) -> None:
    """m1: a `~~~` line inside a ``` fence does NOT close it (different char) —
    the blind-toggle parity inversion the code-Critic flagged. The raw-write
    line stays fenced content."""
    root = _plant(
        tmp_path,
        "```markdown\n~~~\nAppend to `architecture/risk-register.md` raw\n```\n",
    )
    assert audit_root(root).status == "clean"


def test_m1_info_string_line_does_not_close_fence(tmp_path: Path) -> None:
    """m1 (CommonMark): a ```lang info-string line cannot CLOSE a fence (only
    open one) — so a nested ```markdown inside an open ``` block is content, and
    the real prose after the true closer is NOT swallowed (the triage-fence
    class that surfaced triage:179)."""
    root = _plant(
        tmp_path,
        "```markdown\n```markdown\n```\nAppend to `architecture/risk-register.md` raw\n",
    )
    # Opener at L1; the L2 ```markdown is content (info-string can't close);
    # L3 ``` closes; L4 is real prose OUTSIDE the fence → a flagged site.
    res = audit_root(root)
    assert res.status == "violation"
    assert res.violations[0].line == 4


# ─── M3: the exemption allowlist is pinned (off-allowlist → regression) ──


def test_exemption_allowlist_pinned() -> None:
    """The per-(skill, reason) exemption COUNTS actually present in the corpus
    MUST equal the pinned _REGISTERED_SKILL_EXEMPTIONS dict (M3, slice-095
    code-review hardening). Pinning the COUNT — not just the PAIR — means adding
    an N+1-th marker to an ALREADY-listed file trips this (the old pair-set pin
    could not). A new/removed exemption, or a count change, all trip — keeping
    'visible residual' enforced at site granularity, not self-asserted."""
    found = registered_exemption_counts(_REPO_ROOT)
    assert found == _REGISTERED_SKILL_EXEMPTIONS, (
        f"exemption allowlist drift (per-(file,reason) count) — "
        f"off-allowlist/changed: { {k: v for k, v in found.items() if _REGISTERED_SKILL_EXEMPTIONS.get(k) != v} }; "
        f"missing/changed: { {k: v for k, v in _REGISTERED_SKILL_EXEMPTIONS.items() if found.get(k) != v} }"
    )


def test_count_pin_trips_on_extra_marker_on_listed_file(tmp_path: Path) -> None:
    """M3 regression-of-the-regression: adding an N+1-th exemption marker to an
    ALREADY-listed (file, reason) changes the count — the granularity the old
    pair-set pin missed. Here a planted tree with TWO deferred-rmw markers on one
    file yields count 2 for that pair, which would NOT equal a pinned count of 1."""
    body = (
        "Update `architecture/risk-register.md` <!-- vault-write-safe: deferred-rmw -->\n"
        "Regenerate `architecture/slices/_index.md` <!-- vault-write-safe: deferred-rmw -->\n"
    )
    root = _plant(tmp_path, body)
    counts = registered_exemption_counts(root)
    assert counts == {("skills/fake/SKILL.md", "deferred-rmw"): 2}


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
