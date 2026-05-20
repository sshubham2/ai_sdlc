"""Regression / golden test for /slice-candidates --obo (slice-052, ADR-054).

The conversational AskUserQuestion loop is Claude-driven and not unit-testable
(``Test-first: false`` for it); the deterministic ``build_backlog.py``
``--obo-extract`` / ``--obo-write`` / ``--obo-peek`` halves carry this
mandatory build-time gate. It pins the load-bearing parity contract
(must-not-defer #5 / AC4): silent byte-divergence is exactly the failure mode
``--obo-write`` exists to avoid, so a human eyeballing a browser is not an
acceptable verification — this is.

Critic lineage pinned here:
  * B1  — ``--obo-write`` MUST serialize ``ensure_ascii=False`` (Python's
          default emits ``\\uXXXX``; the browser emits raw UTF-8).
  * B2  — operational parity = ``backlog.md`` byte-equality + ``parse_html_state``
          annotation equality, NOT browser-output byte-equality.
  * M1  — unreviewed findings are ABSENT from the annotations map
          (``collect()`` ``if (conf||notes)`` gate), not empty entries.
  * M2/M-add-1 — resume predicate is ``id not in annotations``; Deferred is
          terminal for resume.
  * M-add-2 — step-5 insertion is match-span slicing, not ``re.sub`` (a
          ``re.sub`` impl corrupts ``\\`` / ``</`` in the JSON payload).
  * m1 (Major) — a duplicate ``diagnose-data`` block is refused, not silently
          first-bound.

NOTE (build-discovered): a subprocess capturing this child MUST pass
``encoding="utf-8"`` — the parent's cp1252 default mis-decodes the child's
correct UTF-8 emoji bytes. That is a harness concern, not a tool defect.
"""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT

BB = str((REPO_ROOT / "skills" / "slice-candidates" / "build_backlog.py").resolve())
FX = (REPO_ROOT / "tests" / "methodology" / "fixtures" / "obo_diagnose_out").resolve()
REPO = FX / "repo"
BS = chr(92)                       # a single backslash, escaping-safe
BSLASH_U_E = BS + "u00e9"          # the 6-char sequence é (escaped é)
BSLASH_U_D = BS + "ud83d"          # the 6-char sequence \ud83d (escaped emoji)
CLOSE = "</" + "script>"
GEN_RE = re.compile(r"_Generated from `.*?/diagnosis\.html` on .*?\._")


def _bb():
    spec = importlib.util.spec_from_file_location("_bb_obo", BB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(args, cwd=None):
    return subprocess.run(
        [sys.executable, BB, *args],
        capture_output=True, text=True, encoding="utf-8", cwd=cwd,
    )


def _decisions():
    note_hi = ("rejected: path C:" + BS + "temp" + BS + "x and " + CLOSE
               + " literal -- not real")
    return {
        "F-crit-1-bbbb2222": {"confirmed": "yes", "notes": "approved: café \U0001f4a1 real"},
        "F-high-1-cccc3333": {"confirmed": "no", "notes": note_hi},
        "F-med-1-dddd4444": {"confirmed": "defer", "notes": ""},
        "F-med-2-aaaa1111": {"confirmed": "", "notes": ""},  # untouched -> ABSENT
    }, note_hi


@pytest.fixture()
def staged(tmp_path):
    """A tmp diagnose-out with the fixture's pristine diagnosis.html."""
    shutil.copy(FX / "diagnosis.html", tmp_path / "diagnosis.html")
    return tmp_path


# --------------------------------------------------------------------------- #
# --obo-extract
# --------------------------------------------------------------------------- #


def test_obo_extract_severity_order_and_resume_flags(staged):
    r = run(["--in", str(staged), "--obo-extract"])
    assert r.returncode == 0, r.stderr
    ex = json.loads(r.stdout)
    assert [f["severity"] for f in ex["findings"]] == ["critical", "high", "medium", "medium"]
    assert ex["total"] == 4 and ex["reviewed"] == 0
    assert all(f["reviewed"] is False for f in ex["findings"])
    # evidence_paths allow-set surfaced for the --obo-peek step
    crit = next(f for f in ex["findings"] if f["id"] == "F-crit-1-bbbb2222")
    assert crit["evidence_paths"] == ["alpha.py"]


def test_obo_extract_emits_raw_utf8_not_escaped(staged):
    r = run(["--in", str(staged), "--obo-extract"])
    assert r.returncode == 0, r.stderr
    assert "café" in r.stdout and "\U0001f4a1" in r.stdout
    assert BSLASH_U_E not in r.stdout and BSLASH_U_D not in r.stdout


def test_obo_extract_refuses_duplicate_data_block(staged, tmp_path):
    html = (staged / "diagnosis.html").read_text(encoding="utf-8")
    block = re.search(
        r'<script\s+type="application/json"\s+id="diagnose-data">.*?</script>',
        html, re.DOTALL,
    ).group(0)
    (staged / "diagnosis.html").write_text(
        html.replace(block, block + "\n" + block, 1), encoding="utf-8"
    )
    r = run(["--in", str(staged), "--obo-extract"])
    assert r.returncode != 0
    assert "diagnose-data blocks (expected" in r.stderr


# --------------------------------------------------------------------------- #
# --obo-write
# --------------------------------------------------------------------------- #


def test_obo_write_hard_rule_3_and_collect_semantics(staged):
    orig_sha = hashlib.sha256((staged / "diagnosis.html").read_bytes()).hexdigest()
    decisions, _ = _decisions()
    dpath = staged / "decisions.json"
    dpath.write_text(json.dumps(decisions, ensure_ascii=False), encoding="utf-8")

    r = run(["--in", str(staged), "--obo-write", "--decisions", str(dpath)])
    assert r.returncode == 0, r.stderr

    # Hard rule #3: original byte-identical
    assert hashlib.sha256((staged / "diagnosis.html").read_bytes()).hexdigest() == orig_sha

    st = _bb().parse_html_state(staged / "diagnosis.annotated.html")
    got = st["annotations"]
    # M1: untouched finding ABSENT, not an empty entry
    assert set(got) == {"F-crit-1-bbbb2222", "F-high-1-cccc3333", "F-med-1-dddd4444"}
    assert "F-med-2-aaaa1111" not in got
    assert got["F-med-1-dddd4444"]["confirmed"] == "defer"


def test_obo_write_ensure_ascii_false(staged):
    decisions, _ = _decisions()
    dpath = staged / "d.json"
    dpath.write_text(json.dumps(decisions, ensure_ascii=False), encoding="utf-8")
    assert run(["--in", str(staged), "--obo-write", "--decisions", str(dpath)]).returncode == 0
    atext = (staged / "diagnosis.annotated.html").read_text(encoding="utf-8")
    # B1: raw UTF-8 baked in, NOT \uXXXX (json.loads would decode both, so the
    # only place this is observable is the annotated file bytes themselves).
    assert "café" in atext and "\U0001f4a1" in atext
    assert BSLASH_U_E not in atext and BSLASH_U_D not in atext


def test_obo_write_m_add_2_backslash_and_close_byte_exact(staged):
    decisions, note_hi = _decisions()
    dpath = staged / "d.json"
    dpath.write_text(json.dumps(decisions, ensure_ascii=False), encoding="utf-8")
    assert run(["--in", str(staged), "--obo-write", "--decisions", str(dpath)]).returncode == 0
    st = _bb().parse_html_state(staged / "diagnosis.annotated.html")
    # If step 5 used re.sub with the payload as replacement, \temp/\x and
    # </script> would be corrupted. Match-span slicing keeps it byte-exact.
    assert st["annotations"]["F-high-1-cccc3333"]["notes"] == note_hi
    assert st["annotations"]["F-high-1-cccc3333"]["notes"].count(BS) == 2
    assert CLOSE in st["annotations"]["F-high-1-cccc3333"]["notes"]


def test_obo_write_operational_parity_backlog_equals_golden(staged):
    decisions, _ = _decisions()
    dpath = staged / "d.json"
    dpath.write_text(json.dumps(decisions, ensure_ascii=False), encoding="utf-8")
    assert run(["--in", str(staged), "--obo-write", "--decisions", str(dpath)]).returncode == 0
    # Browser flow: replace the working diagnosis.html with the saved copy.
    shutil.copy(staged / "diagnosis.annotated.html", staged / "diagnosis.html")
    assert run(["--in", str(staged)]).returncode == 0
    produced = (staged / "backlog.md").read_text(encoding="utf-8")
    golden = (FX / "backlog.golden.md").read_text(encoding="utf-8")
    norm = lambda s: GEN_RE.sub("_Generated from `<DIR>/diagnosis.html` on <TS>._", s)
    assert norm(produced) == golden


def test_obo_write_refuses_unknown_finding(staged):
    dpath = staged / "d.json"
    dpath.write_text(json.dumps({"NO-SUCH": {"confirmed": "yes", "notes": ""}}), encoding="utf-8")
    r = run(["--in", str(staged), "--obo-write", "--decisions", str(dpath)])
    assert r.returncode != 0 and "unknown finding id" in r.stderr
    assert not (staged / "diagnosis.annotated.html").exists()


# --------------------------------------------------------------------------- #
# --obo-peek (ADR-054 mechanical allow-set)
# --------------------------------------------------------------------------- #


def test_obo_peek_in_set_served(staged):
    r = run(["--in", str(staged), "--obo-peek", "--finding", "F-crit-1-bbbb2222",
             "--file", "alpha.py"], cwd=str(REPO))
    assert r.returncode == 0 and "crit-evidence" in r.stdout


@pytest.mark.parametrize("bad", [
    "secret.py",                                  # exists, not in any evidence
    "beta.py",                                    # in ANOTHER finding's evidence
    str(Path("..") / "diagnosis.html"),           # parent traversal
    str(Path(".") / "secret.py"),                 # ./-prefixed
    str(Path(REPO_ROOT.anchor) / "etc" / "hosts"),  # absolute
])
def test_obo_peek_out_of_set_refused(staged, bad):
    r = run(["--in", str(staged), "--obo-peek", "--finding", "F-crit-1-bbbb2222",
             "--file", bad], cwd=str(REPO))
    assert r.returncode != 0 and "out-of-scope" in r.stderr


def test_obo_peek_unknown_finding_refused(staged):
    r = run(["--in", str(staged), "--obo-peek", "--finding", "NO-SUCH",
             "--file", "alpha.py"], cwd=str(REPO))
    assert r.returncode != 0 and "unknown finding id" in r.stderr


# --------------------------------------------------------------------------- #
# default path regression — the no-flag contract is byte-frozen (AC1)
# --------------------------------------------------------------------------- #


def test_default_path_unchanged_no_traceback(staged):
    """No-flag invocation: clean SystemExit on no-confirmed, never a traceback.

    Pins AC1 ('non---obo invocation behaviour unchanged') and the build-discovered
    pre-existing stdout-crash fix (the only default-path change is console
    encoding; backlog.md bytes are untouched, asserted via the golden test above).
    """
    r = run(["--in", str(staged)])
    assert "Traceback" not in r.stderr
    assert "No findings have Confirmed=yes" in r.stderr
