"""STP-1 — state-transition stale-pin audit (slice-044; ADR-047).

Covers mission-brief verification rows 1/1b/1c/2/2b/2c/3b + fail-closed +
live-repo self-application. No mocks — real tmp_path fixture trees, real
`ast`, real `risk_register_audit._parse_risks`.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
from tools import risk_register_audit, state_transition_pin_audit
from tools.state_transition_pin_audit import _RISK_STATUS_FN_RE, audit, main
from tests.methodology.conftest import REPO_ROOT


@pytest.fixture(autouse=True)
def _pin_vault_location_agnostic(request):
    """slice-110 / [[ADR-101]]: pin VAULT_ROOT to the in-tree relative default so
    ``root / VAULT_ROOT / 'risk-register.md'`` resolves to each test's own tmp
    fixture — green under the default suite AND under an external
    ``AI_SDLC_VAULT_ROOT`` override (the flip simulation).

    Post-flip ([[ADR-107]]) the live self-application test reads the GENUINE
    external vault: ``audit(root=REPO_ROOT)`` resolves ``REPO_ROOT / VAULT_ROOT /
    risk-register.md`` → the external store. Pinning "architecture" would point it
    at the in-tree (now gitignored orphan) copy, so it is excluded from the pin."""
    if request.node.name == "test_live_repo_self_application_clean":
        yield
        return
    with vi.pin_vault_root(Path("architecture"), state_transition_pin_audit):
        yield

_REGISTER_TMPL = """\
# Risk Register

## R-4 — test risk four

**Likelihood**: medium
**Impact**: medium
**Status**: {r4_status}

## R-5 — test risk five

**Likelihood**: medium
**Impact**: medium
**Status**: {r5_status}
"""


def _make_tree(
    tmp_path: Path,
    *,
    skill_md: str = "# Foo Skill\n\n## H\n\ncanonical anchor present.\n",
    test_files: dict[str, str] | None = None,
    r4_status: str = "retired",
    r5_status: str = "retired",
) -> Path:
    """Build a minimal fixture repo (skills/ + tests/ + architecture/)."""
    (tmp_path / "skills" / "foo").mkdir(parents=True)
    (tmp_path / "skills" / "foo" / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (tmp_path / "architecture").mkdir()
    (tmp_path / "architecture" / "risk-register.md").write_text(
        _REGISTER_TMPL.format(r4_status=r4_status, r5_status=r5_status),
        encoding="utf-8",
    )
    tdir = tmp_path / "tests" / "methodology"
    tdir.mkdir(parents=True)
    for rel, content in (test_files or {}).items():
        p = tmp_path / "tests" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content), encoding="utf-8")
    return tmp_path


def _kinds(root: Path) -> list[str]:
    return [v.kind for v in audit(root=root).violations if v.severity == "Important"]


# --------------------------------------------------------------------------
# Sub-form A — SKILL.md-prose-repoint stale pin
# --------------------------------------------------------------------------

def test_subform_a_module_level_stale_pin_flagged(tmp_path: Path) -> None:
    """Row 2: module-level `X = read_file(...)` + absent literal → exit 1."""
    root = _make_tree(tmp_path, test_files={
        "methodology/test_foo_skill.py": '''
            from tests.methodology.conftest import read_file
            X = read_file("skills/foo/SKILL.md")
            def test_pin():
                assert "GONE ANCHOR" in X
        ''',
    })
    res = audit(root=root)
    kinds = [v.kind for v in res.violations]
    assert kinds == ["stale-skill-prose-pin"], kinds
    msg = res.violations[0].message
    assert "test_foo_skill.py::test_pin" in msg
    assert "GONE ANCHOR" in msg and "skills/foo/SKILL.md" in msg
    assert main(["--root", str(root)]) == 1


def test_subform_a_function_local_sliced_segment_presence_is_full_file(tmp_path: Path) -> None:
    """Row 2 (B2): function-local `content=read_file` → sliced segment;
    presence is checked against the FULL SKILL.md, not the slice."""
    skill = "# Foo\n\n## A\n\nalpha-only.\n\n## B\n\nBETA-ANCHOR here.\n"
    # Pin asserts BETA-ANCHOR against the segment BEFORE '## B' — but it IS
    # present in the full file, so it must NOT be flagged (slicing narrows
    # location, not presence).
    root = _make_tree(tmp_path, skill_md=skill, test_files={
        "methodology/test_foo_skill.py": '''
            from tests.methodology.conftest import read_file
            def test_pin():
                content = read_file("skills/foo/SKILL.md")
                seg = content.split("## B", 1)[0]
                assert "BETA-ANCHOR" in seg
        ''',
    })
    assert _kinds(root) == []
    # And a genuinely-absent literal in the same sliced shape IS flagged.
    root2 = _make_tree(tmp_path / "t2", skill_md=skill, test_files={
        "methodology/test_foo_skill.py": '''
            from tests.methodology.conftest import read_file
            def test_pin():
                content = read_file("skills/foo/SKILL.md")
                seg = content.split("## B", 1)[1]
                assert "VANISHED" in seg
        ''',
    })
    assert _kinds(root2) == ["stale-skill-prose-pin"]


def test_subform_a_not_in_pin_not_flagged(tmp_path: Path) -> None:
    """B1: a `not in` pin asserts a deliberately-absent literal → exit 0."""
    root = _make_tree(tmp_path, test_files={
        "methodology/test_foo_skill.py": '''
            from tests.methodology.conftest import read_file
            C = read_file("skills/foo/SKILL.md")
            def test_pin():
                assert "DELIBERATELY ABSENT" not in C
        ''',
    })
    assert _kinds(root) == []
    assert main(["--root", str(root)]) == 0


def test_subform_a_or_disjunction_not_flagged(tmp_path: Path) -> None:
    """Task-1 self-verify refinement: `A in c or B in c` is a disjunction —
    an absent alternative is intentional, must NOT be flagged."""
    root = _make_tree(
        tmp_path,
        skill_md="# Foo\n\nhyphen-form is canonical.\n",
        test_files={
            "methodology/test_foo_skill.py": '''
                from tests.methodology.conftest import read_file
                C = read_file("skills/foo/SKILL.md")
                def test_pin():
                    assert "hyphen-form" in C or "space form" in C
            ''',
        },
    )
    assert _kinds(root) == []
    assert main(["--root", str(root)]) == 0


def test_subform_a_and_conjunction_one_absent_flagged(tmp_path: Path) -> None:
    """B-add-1: positive-only `and` conjunction — each conjunct is pinned;
    an absent one IS a stale pin (must be checked per-operand)."""
    root = _make_tree(
        tmp_path,
        skill_md="# Foo\n\nPRESENT anchor only.\n",
        test_files={
            "methodology/test_foo_skill.py": '''
                from tests.methodology.conftest import read_file
                C = read_file("skills/foo/SKILL.md")
                def test_pin():
                    assert "PRESENT" in C and "MISSING-CONJUNCT" in C
            ''',
        },
    )
    res = audit(root=root)
    msgs = [v.message for v in res.violations]
    assert len(msgs) == 1 and "MISSING-CONJUNCT" in msgs[0], msgs


def test_subform_a_mixed_and_with_notin_sibling_not_flagged(tmp_path: Path) -> None:
    """B1/B-add-1: an `and` whose sibling is `not in` is the mixed idiom →
    all its operands excluded."""
    root = _make_tree(
        tmp_path,
        skill_md="# Foo\n\nonly-this.\n",
        test_files={
            "methodology/test_foo_skill.py": '''
                from tests.methodology.conftest import read_file
                C = read_file("skills/foo/SKILL.md")
                def test_pin():
                    assert "FORBIDDEN" not in C and "ALSO-ABSENT" in C
            ''',
        },
    )
    assert _kinds(root) == []


def test_subform_a_folded_multiline_literal(tmp_path: Path) -> None:
    """B3: implicitly-concatenated 3-line literal — folded value present →
    exit 0; absent → exit 1 with the FULL folded literal in the message."""
    folded = "STOP: this is a long multi line anchor that exists verbatim."
    root_ok = _make_tree(
        tmp_path / "ok",
        skill_md=f"# Foo\n\n{folded}\n",
        test_files={
            "methodology/test_foo_skill.py": '''
                from tests.methodology.conftest import read_file
                C = read_file("skills/foo/SKILL.md")
                def test_pin():
                    assert (
                        "STOP: this is a long multi line "
                        "anchor that exists verbatim."
                    ) in C
            ''',
        },
    )
    assert _kinds(root_ok) == []
    root_bad = _make_tree(
        tmp_path / "bad",
        skill_md="# Foo\n\nunrelated.\n",
        test_files={
            "methodology/test_foo_skill.py": '''
                from tests.methodology.conftest import read_file
                C = read_file("skills/foo/SKILL.md")
                def test_pin():
                    assert (
                        "STOP: this is a long multi line "
                        "anchor that exists verbatim."
                    ) in C
            ''',
        },
    )
    res = audit(root=root_bad)
    assert [v.kind for v in res.violations] == ["stale-skill-prose-pin"]
    # Full folded literal (not a mis-extracted prefix) is in the message.
    assert "STOP: this is a long multi line anchor that exists verbatim." in res.violations[0].message


def test_subform_a_fstring_operand_skipped(tmp_path: Path) -> None:
    """Non-constant (f-string) operand cannot prove absence → skipped."""
    root = _make_tree(tmp_path, test_files={
        "methodology/test_foo_skill.py": '''
            from tests.methodology.conftest import read_file
            C = read_file("skills/foo/SKILL.md")
            def test_pin():
                name = "x"
                assert f"dynamic {name} anchor" in C
        ''',
    })
    assert _kinds(root) == []


def test_subform_a_syntaxerror_file_skip_with_note(tmp_path: Path) -> None:
    """Row 1c (B1/B2): an unparseable scanned file → skip-with-visible-note,
    NO violation, NOT exit 2 (ADR-037/PTFFD-1)."""
    root = _make_tree(tmp_path, test_files={
        "methodology/test_broken_skill.py": "def test_x(\n    pass\n",
    })
    res = audit(root=root)
    assert [v for v in res.violations if v.severity == "Important"] == []
    assert any("test_broken_skill.py" in s and "skip-with-note" in s for s in res.skipped)
    assert main(["--root", str(root)]) == 0


# --------------------------------------------------------------------------
# Sub-form B — risk-status-stale pin (git-diff-independent standing invariant)
# --------------------------------------------------------------------------

def test_subform_b_stale_status_pin_flagged(tmp_path: Path) -> None:
    """Row 1: register R-4=retired + `test_r_4_stays_mitigating` → exit 1."""
    root = _make_tree(tmp_path, r4_status="retired", test_files={
        "methodology/test_riskpins.py": '''
            def test_r_4_stays_mitigating():
                assert True
        ''',
    })
    res = audit(root=root)
    assert [v.kind for v in res.violations] == ["stale-risk-status-pin"]
    msg = res.violations[0].message
    assert "R-4" in msg and "mitigating" in msg and "retired" in msg
    assert "test_riskpins.py::test_r_4_stays_mitigating" in msg
    assert main(["--root", str(root)]) == 1


def test_subform_b_realigned_name_not_flagged(tmp_path: Path) -> None:
    """Row 1 negative: the slice-041-realigned name has no verb-token."""
    root = _make_tree(tmp_path, r4_status="retired", test_files={
        "methodology/test_riskpins.py": '''
            def test_r_4_retired_by_slice_041_030c_completes_the_split():
                assert True
        ''',
    })
    assert _kinds(root) == []


def test_subform_b_claimed_equals_live_not_flagged(tmp_path: Path) -> None:
    """Row 1 negative: claimed == live → clean."""
    root = _make_tree(tmp_path, r4_status="mitigating", test_files={
        "methodology/test_riskpins.py": '''
            def test_r_4_stays_mitigating():
                assert True
        ''',
    })
    assert _kinds(root) == []


def test_subform_b_suffixed_name_still_flagged(tmp_path: Path) -> None:
    """targeted-M5: a descriptive suffix after the status word is still
    caught (explicit alternation, not greedy \\w+)."""
    root = _make_tree(tmp_path, r4_status="retired", test_files={
        "methodology/test_riskpins.py": '''
            def test_r_4_stays_mitigating_until_spike_done():
                assert True
        ''',
    })
    assert _kinds(root) == ["stale-risk-status-pin"]


def test_subform_b_embedded_r_not_flagged(tmp_path: Path) -> None:
    """targeted-M4: an embedded `r` (addr/parser) must NOT false-bind a
    risk-number even though the claimed status is valid."""
    root = _make_tree(tmp_path, r4_status="retired", r5_status="retired", test_files={
        "methodology/test_riskpins.py": '''
            def test_addr_5_is_open():
                assert True
            def test_parser_4_is_retired():
                assert True
        ''',
    })
    assert _kinds(root) == []


def test_subform_b_risk_not_in_register_not_flagged(tmp_path: Path) -> None:
    """A risk id absent from the register is not a contradiction."""
    root = _make_tree(tmp_path, test_files={
        "methodology/test_riskpins.py": '''
            def test_r_99_stays_open():
                assert True
        ''',
    })
    assert _kinds(root) == []


def test_subform_b_regex_mechanical_contrast() -> None:
    """Row 1b: execute the implemented regex against literal names
    (M-add-1 + targeted-M1 + targeted-M2)."""
    def g(name: str):
        m = _RISK_STATUS_FN_RE.search(name)
        return m.groups() if m else None

    assert g("test_r_4_stays_mitigating") == ("4", "stays", "mitigating")
    assert g("test_r_4_stays_mitigating_until_spike_done") == ("4", "stays", "mitigating")
    assert g("test_r_10_is_retired") == ("10", "is", "retired")
    assert g("test_r_4_retired_by_slice_041_030c_completes_the_split") is None
    assert g("test_addr_5_is_open") is None
    assert g("test_parser_4_is_retired") is None


# --------------------------------------------------------------------------
# Fail-closed + structural + object-identity reuse
# --------------------------------------------------------------------------

def test_fail_closed_register_missing_exit_2(tmp_path: Path) -> None:
    """Row 3b: missing register → usage-error exit 2 (fail-closed)."""
    root = _make_tree(tmp_path, test_files={"methodology/test_x.py": "def test_z(): pass\n"})
    (root / "architecture" / "risk-register.md").unlink()
    res = audit(root=root)
    assert any(v.kind == "usage-error" for v in res.violations)
    assert main(["--root", str(root)]) == 2


def test_fail_closed_tests_dir_missing_exit_2(tmp_path: Path) -> None:
    """Missing tests/ → usage-error exit 2."""
    (tmp_path / "skills" / "foo").mkdir(parents=True)
    (tmp_path / "skills" / "foo" / "SKILL.md").write_text("# x\n", encoding="utf-8")
    (tmp_path / "architecture").mkdir()
    (tmp_path / "architecture" / "risk-register.md").write_text(
        _REGISTER_TMPL.format(r4_status="open", r5_status="open"), encoding="utf-8")
    assert main(["--root", str(tmp_path)]) == 2


def test_object_identity_parse_risks_reuse() -> None:
    """Row 3b (CSP-1): Sub-form B reuses RR-1's parser by object identity,
    NOT re-derived (slice-038 lesson)."""
    assert state_transition_pin_audit._parse_risks is risk_register_audit._parse_risks


# --------------------------------------------------------------------------
# Row 3c — live-repo self-application (RSAD-1 dogfood)
# --------------------------------------------------------------------------

def test_live_repo_self_application_clean() -> None:
    """STP-1 run against the real repo MUST be clean (exit 0): no live test
    contradicts the register, no removed-anchor prose-pin, the lone
    `tests/methodology/fixtures/syntax_error.py` is skip-noted not HALT-ed."""
    res = audit(root=REPO_ROOT)
    important = [v for v in res.violations if v.severity == "Important"]
    assert important == [], [f"{v.kind}: {v.message}" for v in important]
    assert any("syntax_error.py" in s for s in res.skipped)
