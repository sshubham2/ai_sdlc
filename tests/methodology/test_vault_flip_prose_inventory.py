"""Tests for the vault-flip PROSE inventory (slice-107 / ADR-096 + ADR-097).

The prose-surface analog of `test_vault_flip_readiness_audit.py` (the Python
production/tests surfaces). Pins:
  * AC1 — boundary-free, all-matches-per-line enumeration of the full prose corpus
  * AC2 — fail-closed `needs-human` default for inline-code (NOT doc-example); B2
  * AC3 — the pinned baseline + `--strict` drift gate
  * AC4 — non-vacuous-by-mutation classifier; cross-line (M2) + intra-line (M-add-1)
          disposition-key collision-freedom
  * AC5 — disjointness: the new tool adds NO production must-rewrite literal

Dual-review corrections baked in: boundary-free matcher (real anchored=69 vs
boundary-free=318), `re.finditer` all-matches-per-line, 5-tuple disposition key
with column-offset, per-class count floor.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.vault_flip_prose_inventory import (
    audit_file,
    audit_root,
    classify_line_occurrences,
    REWRITE_AT_FLIP,
    HISTORICAL_ANCHOR,
    DOC_EXAMPLE,
    _ALL_CLASSES,
    _BASELINE_SHA256,
    baseline_sha,
    _CLASS_COUNT_FLOOR,
    _PROSE_GLOBS,
    _RESIDUAL,
    EXPECTED_TOTAL,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
TOOL = "tools.vault_flip_prose_inventory"


def _write(tmp_path: Path, rel: str, content: str) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ── AC1: boundary-free, all-matches-per-line enumeration ─────────────────────
def test_enumerates_full_corpus_318_all_matches_per_line():
    """The boundary-free matcher enumerates the full prose corpus (== grep
    -rohE count, EXPECTED_TOTAL) using re.finditer so intra-line multi-matches
    are NOT collapsed (M-add-1 / B3 residue: a per-line single re.search would
    undercount)."""
    result = audit_root(REPO_ROOT)
    assert result.files_scanned > 0
    assert len(result.occurrences) == EXPECTED_TOTAL, (
        f"expected {EXPECTED_TOTAL} occurrences (boundary-free, all matches/line); "
        f"got {len(result.occurrences)}"
    )
    for o in result.occurrences:
        assert o.path and o.line >= 1 and o.col >= 0
        assert o.klass in _ALL_CLASSES
        assert o.reason
    # code-review.md:103 carries 5 matches on ONE line (intra-line multiplicity)
    cr = [o for o in result.occurrences
          if o.path.endswith("code-review/SKILL.md") and o.line == 103]
    assert len(cr) == 5, f"expected 5 intra-line matches at code-review.md:103, got {len(cr)}"
    assert len({o.col for o in cr}) == 5, "the 5 intra-line matches must have distinct columns"


def test_finditer_all_matches_per_line(tmp_path):
    """A single line with two vault literals yields TWO occurrences with
    distinct columns — proving all-matches-per-line, not one re.search."""
    p = _write(tmp_path, "skills/x/SKILL.md",
               "see `architecture/a.md` and `architecture/b.md` here\n")
    occ = audit_file(p, "skills/x/SKILL.md")
    assert len(occ) == 2
    assert occ[0].col != occ[1].col


# ── AC1 residual: bare-no-slash args (B1 + m-add-1) ──────────────────────────
def test_bare_vault_dir_arg_residual_enumerated():
    """The ONLY honest-contract residual — bare `architecture`/`diagnose-out`
    no-slash args (e.g. `graphify vault architecture`) — is explicitly
    enumerated + non-empty, NEVER a silent gap."""
    assert _RESIDUAL, "bare-vault-dir-arg residual must be explicitly enumerated"
    for entry in _RESIDUAL:
        # each residual entry names a real prose location (path + line)
        assert "path" in entry and "line" in entry and "value" in entry


# ── AC2: fail-closed needs-human default for inline-code (B2) ────────────────
def test_inline_code_routes_rewrite_not_doc_example(tmp_path):
    """An inline-code vault path is a LIVE operational reference → rewrite-at-flip
    (recalibrated default). B2's GOAL is preserved: it lands ON the M4 checklist,
    NEVER the off-checklist non-gating doc-example (the silent drop B2 closed)."""
    occ = classify_line_occurrences(
        "the `architecture/concept.md` file", rel="skills/x/SKILL.md",
        lineno=1, fenced=False, disposition={})
    assert len(occ) == 1
    assert occ[0].klass == REWRITE_AT_FLIP
    assert occ[0].klass != DOC_EXAMPLE, "an inline-code path must NEVER silently become doc-example (B2)"


def test_doc_example_reserved_for_plain_prose(tmp_path):
    """doc-example is RESERVED for genuine plain-prose mentions (no inline-code
    backticks, no pathspec, no operational verb)."""
    occ = classify_line_occurrences(
        "the architecture/concept.md path describes the vault layout",
        rel="skills/x/SKILL.md", lineno=1, fenced=False, disposition={})
    assert len(occ) == 1
    assert occ[0].klass == DOC_EXAMPLE


def test_operational_verb_routes_rewrite_at_flip(tmp_path):
    """An inline-code vault path on a line carrying an operational verb (e.g.
    `Write`) routes to rewrite-at-flip (B2 expanded verb set)."""
    occ = classify_line_occurrences(
        "Write `architecture/concept.md` with the initial vault",
        rel="skills/x/SKILL.md", lineno=1, fenced=False, disposition={})
    assert occ[0].klass == REWRITE_AT_FLIP


def test_git_pathspec_routes_rewrite_at_flip(tmp_path):
    """A git-pathspec literal naming the vault dir (breaks at flip) routes to
    rewrite-at-flip via the pathspec sink (B1)."""
    occ = classify_line_occurrences(
        "    :(exclude)architecture/decisions/**",
        rel="skills/code-review/SKILL.md", lineno=1, fenced=False, disposition={})
    assert occ[0].klass == REWRITE_AT_FLIP


def test_anchor_plus_incode_routes_needs_human_exit_2(tmp_path):
    """The fail-closed bucket: a genuine preserve-marker on a line carrying an
    in-code vault path is a true rewrite-vs-preserve conflict → needs-human →
    CLI exit 2 (the ONLY auto-route to needs-human; resolved via _DISPOSITION)."""
    _write(tmp_path, "skills/x/SKILL.md",
           "preserved as a historical anchor: `architecture/old-loc.md`\n")
    cp = subprocess.run(
        [PY, "-m", TOOL, "--repo-root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT))
    assert cp.returncode == 2, cp.stdout + cp.stderr


# ── AC3: pinned baseline + --strict drift gate ───────────────────────────────
def test_baseline_pinned():
    """The live rewrite-at-flip + needs-human multiset hashes to the pinned
    _BASELINE_SHA256 (count-sensitive, line-independent; a hash, not enumerated
    tuples — keeps tools/*.py free of slashed vault literals per AC5/M1)."""
    result = audit_root(REPO_ROOT)
    assert baseline_sha(result) == _BASELINE_SHA256


def test_strict_drift_on_new_literal(tmp_path):
    """--strict on the real repo is exit 0 (baseline hash matches); a corpus with
    a DIFFERENT classified multiset trips --strict (exit 2 drift) — non-vacuous."""
    # baseline-clean run on the real repo is exit 0 under --strict
    clean = subprocess.run(
        [PY, "-m", TOOL, "--repo-root", str(REPO_ROOT), "--strict"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT))
    assert clean.returncode == 0, clean.stdout + clean.stderr
    # a tmp corpus with a single (rewrite-at-flip, no needs-human) literal → its
    # baseline multiset differs from the pinned hash → --strict exits 2 (drift),
    # NOT from needs-human (the literal classifies operational).
    _write(tmp_path, "skills/x/SKILL.md", "Update `architecture/new-thing.md` now\n")
    drift = subprocess.run(
        [PY, "-m", TOOL, "--repo-root", str(tmp_path), "--strict"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT))
    assert drift.returncode == 2, drift.stdout + drift.stderr
    assert "DRIFT" in drift.stdout


def test_per_class_total_count_floor():
    """The per-class total-count floor (m2) matches the live counts; it closes
    the silent rewrite-at-flip → doc-example demotion direction."""
    result = audit_root(REPO_ROOT)
    for klass, floor in _CLASS_COUNT_FLOOR.items():
        assert len(result.by_class(klass)) >= floor


# ── AC4: non-vacuous classifier + disposition-key collision-freedom ──────────
def test_classifier_mutation_flips_class():
    """Non-vacuous by mutation (AP-5): the SAME literal flips class when its
    surrounding context changes (operational verb → rewrite; historical-anchor
    marker → historical-anchor)."""
    op = classify_line_occurrences(
        "Write `architecture/x.md`", rel="skills/x/SKILL.md",
        lineno=1, fenced=False, disposition={})[0]
    # plain-prose (NOT in-code) path on a genuine preserve-marker line → historical-anchor
    anchor = classify_line_occurrences(
        "kept as a historical anchor for discoverability: architecture/x.md",
        rel="skills/x/SKILL.md", lineno=1, fenced=False, disposition={})[0]
    assert op.klass != anchor.klass
    assert op.klass == REWRITE_AT_FLIP
    assert anchor.klass == HISTORICAL_ANCHOR


def test_no_ambiguous_duplicate():
    """Cross-line (M2): no two occurrences share the full 5-tuple disposition
    key yet require different classes."""
    result = audit_root(REPO_ROOT)
    by_key: dict = {}
    for o in result.occurrences:
        by_key.setdefault(o.disposition_key(), set()).add(o.klass)
    collisions = {k: v for k, v in by_key.items() if len(v) > 1}
    assert not collisions, f"ambiguous same-key occurrences need different classes: {collisions}"


def test_no_intra_line_ambiguous_multimatch():
    """Intra-line (M-add-1): code-review.md:103's 5 same-line matches get
    distinct column-offset keys (no two share a key with different classes).
    The cross-line test above subsumes this, but this pins the canonical
    intra-line fixture explicitly."""
    result = audit_root(REPO_ROOT)
    cr = [o for o in result.occurrences
          if o.path.endswith("code-review/SKILL.md") and o.line == 103]
    assert len(cr) >= 2, "expected the intra-line multimatch fixture line"
    keys = [o.disposition_key() for o in cr]
    assert len(keys) == len(set(keys)), "intra-line matches must have distinct keys (column-offset)"


def test_disposition_override_fires_and_is_column_keyed():
    """ADR-097 mechanism (code-review M2 — closes the zero-coverage-on-a-non-empty-
    table gap): a _DISPOSITION entry overrides the ruleset class for the EXACT 5-tuple
    key (reason 'disposition'); a key with a wrong column-offset does NOT override —
    proving the column-offset component (M-add-1) is load-bearing, not decorative."""
    line = "Write `architecture/x.md`"  # ruleset → rewrite-at-flip
    base = classify_line_occurrences(line, rel="skills/x/SKILL.md", lineno=1,
                                     fenced=False, disposition={})[0]
    assert base.klass == REWRITE_AT_FLIP
    key = base.disposition_key()  # exact (path, norm_line, fenced, ordinal, col)
    over = classify_line_occurrences(line, rel="skills/x/SKILL.md", lineno=1,
                                     fenced=False, disposition={key: HISTORICAL_ANCHOR})[0]
    assert over.klass == HISTORICAL_ANCHOR and over.reason == "disposition", \
        "the disposition override must fire on the exact 5-tuple key"
    wrong = (key[0], key[1], key[2], key[3], key[4] + 999)  # same line, wrong column
    nochange = classify_line_occurrences(line, rel="skills/x/SKILL.md", lineno=1,
                                         fenced=False, disposition={wrong: HISTORICAL_ANCHOR})[0]
    assert nochange.klass == REWRITE_AT_FLIP, \
        "a wrong-column disposition key must NOT override (column-offset is load-bearing)"


# ── AC5: disjointness — no new production must-rewrite literal ────────────────
def test_disjoint_no_new_production_must_rewrite():
    """The new tool's own source adds NO production `must-rewrite` literal to
    slice-106's readiness baseline (the readiness audit, run --strict over the
    repo incl. this tool, exits 0)."""
    cp = subprocess.run(
        [PY, "-m", "tools.vault_flip_readiness_audit", "--repo-root", str(REPO_ROOT), "--strict"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT))
    assert cp.returncode == 0, (
        "readiness --strict must stay exit 0 — the prose tool introduced a "
        f"production must-rewrite literal:\n{cp.stdout}\n{cp.stderr}"
    )
