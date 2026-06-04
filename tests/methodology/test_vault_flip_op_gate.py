"""Tests for the vault-flip OP-GATE (slice-111 / [[ADR-104]], implements [[ADR-102]]).

The op-gate is a DISTINCT concern from the location-literal inventory (same module,
same anchoring): it flags un-routed in-loop-skill vault WRITE-ops. Pins:
  * Non-vacuity (AP-5): an in-loop un-routed shared-aggregate write → OP_UNROUTED.
  * B2/AP-15: a move's active-folder SOURCE does NOT buy a deferral — the DEST governs.
  * M-add-1: an out-of-loop write → OP_OUT_OF_SCOPE (exit 0) WHILE a fresh in-loop
    un-routed write still → OP_UNROUTED (the gate goes green AND still bites in-loop).
  * Non-over-flag: bare mentions / reads / bare-`add` (slice-name/prose) NOT flagged.
  * m1/AP-16: `git add` (incl. -A / --all / multi-path) detected; detection ⊇ classification.
  * Real corpus is GREEN (0 OP_UNROUTED) after AC1 routing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.vault_flip_prose_inventory import (
    op_audit_root,
    OP_ROUTED,
    OP_DEFERRED_TO_FLIP,
    OP_OUT_OF_SCOPE,
    OP_UNROUTED,
    _op_class_counts,
    _op_floor_shrink,
    _IN_LOOP_SKILLS,
    _IN_LOOP_SKILLS_COUNT,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
TOOL = "tools.vault_flip_prose_inventory"


def _skill(tmp: Path, name: str, body: str) -> None:
    p = tmp / "skills" / name / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def _classes(tmp: Path) -> dict:
    return _op_class_counts(op_audit_root(tmp))


# ── non-vacuity (AP-5): in-loop un-routed shared-aggregate write → OP_UNROUTED ──
def test_in_loop_unrouted_aggregate_write_flagged(tmp_path: Path) -> None:
    _skill(tmp_path, "reflect", "Step: run `git add architecture/risk-register.md` now.\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1
    assert ops[0].klass == OP_UNROUTED
    assert ops[0].skill == "reflect"


def test_op_gate_exit_2_on_unrouted(tmp_path: Path) -> None:
    """CLI: a real subprocess run exits 2 when an in-loop un-routed write exists."""
    _skill(tmp_path, "reflect", "run `git add architecture/risk-register.md`\n")
    r = subprocess.run([PY, "-m", TOOL, "--op-gate", "--repo-root", str(tmp_path)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2
    assert "OP_UNROUTED" in r.stdout


# ── B2 / AP-15: a move's active-folder SOURCE does NOT buy a deferral ──────────
def test_move_source_active_folder_does_not_defer(tmp_path: Path) -> None:
    """`mv <active-folder-source> <shared-aggregate-dest>` → the DEST governs →
    OP_UNROUTED. The active-folder SOURCE literal must NOT classify the op deferred."""
    _skill(tmp_path, "archive",
           "run `mv architecture/slices/slice-042-foo architecture/lessons-learned.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1, "a move emits ONE op (the dest), not one per literal"
    assert ops[0].klass == OP_UNROUTED
    assert "lessons-learned.md" in ops[0].value, "the DEST literal governs, not the source"


def test_move_into_archive_dest_active_source_deferred_only_if_dest_active(tmp_path: Path) -> None:
    """A move whose DEST is a per-slice active folder → OP_DEFERRED_TO_FLIP (dest governs)."""
    _skill(tmp_path, "reflect",
           "run `mv architecture/foo.md architecture/slices/slice-NNN-x/keep.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1
    assert ops[0].klass == OP_DEFERRED_TO_FLIP


# ── M-add-1: out-of-loop → OP_OUT_OF_SCOPE; in-loop still bites ───────────────
def test_out_of_loop_write_is_out_of_scope(tmp_path: Path) -> None:
    """An out-of-loop skill's un-routed shared-aggregate write → OP_OUT_OF_SCOPE
    (gate-visible, NOT a violation) — so the gate can go green on the real corpus."""
    _skill(tmp_path, "critic-calibrate", "Append to `architecture/critic-calibration-log.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1 and ops[0].klass == OP_OUT_OF_SCOPE


def test_gate_green_with_out_of_loop_but_bites_new_in_loop(tmp_path: Path) -> None:
    """The load-bearing M-add-1 invariant: an out-of-loop un-routed write does NOT
    fail the gate, but a NEW in-loop un-routed write STILL does (the gate is not
    vacuously green — it bites in-loop)."""
    _skill(tmp_path, "critic-calibrate", "Append to `architecture/critic-calibration-log.md`\n")
    counts_oos = _classes(tmp_path)
    assert counts_oos[OP_UNROUTED] == 0 and counts_oos[OP_OUT_OF_SCOPE] == 1
    # add a fresh IN-LOOP un-routed write → the gate must now bite
    _skill(tmp_path, "build-slice", "run `git add architecture/shippability.md`\n")
    counts_both = _classes(tmp_path)
    assert counts_both[OP_UNROUTED] == 1, "the gate must still bite an in-loop un-routed write"


# ── routed / deferred classification ─────────────────────────────────────────
def test_seam_token_routes(tmp_path: Path) -> None:
    """A write-op whose line carries a seam token (`vault_edit`/`VAULT_ROOT`) → OP_ROUTED,
    even when the prose still names the in-code `architecture/` path."""
    _skill(tmp_path, "reflect",
           "write `architecture/risk-register.md` via the `vault_edit append` channel\n")
    ops = op_audit_root(tmp_path)
    assert ops and all(o.klass == OP_ROUTED for o in ops)


def test_active_folder_write_deferred(tmp_path: Path) -> None:
    _skill(tmp_path, "validate-slice",
           "Write `architecture/slices/slice-NNN-<name>/validation.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1 and ops[0].klass == OP_DEFERRED_TO_FLIP


# ── non-over-flag: reads / bare mentions / bare-`add` NOT flagged ─────────────
def test_read_verb_not_flagged(tmp_path: Path) -> None:
    _skill(tmp_path, "reflect", "Read `architecture/risk-register.md` for context.\n")
    assert op_audit_root(tmp_path) == []


def test_bare_prose_mention_not_flagged(tmp_path: Path) -> None:
    """A vault literal with no write-op verb is not an op (non-over-flag)."""
    _skill(tmp_path, "reflect", "The `architecture/risk-register.md` file is the source of truth.\n")
    assert op_audit_root(tmp_path) == []


def test_verb_after_literal_not_flagged(tmp_path: Path) -> None:
    """A write-verb AFTER the literal does not govern it (drops 'completed slices
    move to ...' / '...then `git add` it')."""
    _skill(tmp_path, "drift-check",
           "- `architecture/slices/foo/design.md` — completed slices move to the archive.\n")
    assert op_audit_root(tmp_path) == []


def test_bare_add_in_slice_name_not_matched(tmp_path: Path) -> None:
    """Bare `add` (in a slice name like `slice-NNN-add-receipt`) is NOT a write verb
    — only `git add` is (m1/AP-16); avoids the slice-name false-match."""
    _skill(tmp_path, "commit-slice",
           "Slice: `architecture/slices/archive/slice-023-add-receipt-upload/`\n")
    assert op_audit_root(tmp_path) == []


# ── m1 / AP-16: git add multi-flag / multi-path detected ─────────────────────
def test_git_add_dash_A_detected(tmp_path: Path) -> None:
    _skill(tmp_path, "build-slice", "run `git add -A architecture/shippability.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1 and ops[0].klass == OP_UNROUTED


def test_git_add_multipath_each_target(tmp_path: Path) -> None:
    """`git add A B` emits one op per in-code target (not just the last)."""
    _skill(tmp_path, "build-slice",
           "run `git add architecture/shippability.md architecture/build-checks.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 2, "git add (non-move) targets EVERY in-code literal after the verb"
    assert all(o.klass == OP_UNROUTED for o in ops)


# ── floor-shrink + real corpus ───────────────────────────────────────────────
def test_floor_shrink_helper_reports_shrink() -> None:
    """_op_floor_shrink flags a class whose count is below its pinned floor (a tmp
    fixture has far fewer than the real-corpus floors of 11/23)."""
    from tools.vault_flip_prose_inventory import OpOccurrence
    tiny = [OpOccurrence("skills/x/SKILL.md", 1, 0, "architecture/x.md",
                         OP_DEFERRED_TO_FLIP, "t", "x")]
    shrink = _op_floor_shrink(tiny)
    assert any(OP_DEFERRED_TO_FLIP in s for s in shrink)


def test_real_corpus_op_gate_green() -> None:
    """After AC1 routing, the REAL corpus has ZERO OP_UNROUTED (the M-add-1 gate is
    green) and the in-loop allowlist is pinned at 11 skills."""
    ops = op_audit_root(REPO_ROOT)
    counts = _op_class_counts(ops)
    assert counts[OP_UNROUTED] == 0, (
        f"real corpus must be green; un-routed: "
        f"{[ (o.path,o.line,o.value) for o in ops if o.klass==OP_UNROUTED ]}"
    )
    assert counts[OP_DEFERRED_TO_FLIP] > 0, "the deferred bucket must be non-empty (AP-12)"
    assert len(_IN_LOOP_SKILLS) == _IN_LOOP_SKILLS_COUNT


def test_real_corpus_op_gate_strict_clean() -> None:
    """--op-gate --strict on the real corpus exits 0 (no floor shrink)."""
    r = subprocess.run([PY, "-m", TOOL, "--op-gate", "--strict", "--repo-root", str(REPO_ROOT)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


# ── code-review M1: a decoy seam token BEFORE the verb must NOT route a raw write ──
def test_decoy_seam_token_before_verb_still_unrouted(tmp_path: Path) -> None:
    """A `vault_edit`/`VAULT_ROOT` mention that PRECEDES the governing verb (a comment,
    a negation, a noun) must NOT buy OP_ROUTED for a raw write later on the line — the
    AP-15 decoy-marker failure ADR-104 warns against (code-review M1). Routing is keyed
    on a seam token AFTER first_verb, not line-wide."""
    _skill(tmp_path, "reflect",
           "Instead of `vault_edit`, do NOT run raw: `mv architecture/slices/s-1 architecture/lessons-learned.md`\n")
    ops = op_audit_root(tmp_path)
    assert ops, "the raw mv must be detected, not silently routed away"
    assert all(o.klass == OP_UNROUTED for o in ops), (
        f"a decoy seam token before the verb must NOT route the write; got {[o.klass for o in ops]}"
    )


def test_genuine_routing_after_verb_still_routed(tmp_path: Path) -> None:
    """The M1 fix is behavior-preserving: a seam token AFTER the verb still → OP_ROUTED."""
    _skill(tmp_path, "reflect",
           "write `architecture/risk-register.md` via the `vault_edit append` channel\n")
    ops = op_audit_root(tmp_path)
    assert ops and all(o.klass == OP_ROUTED for o in ops)


# ── code-review M2: a multi-verb line must flag EVERY target (no single-dest collapse) ──
def test_multi_verb_line_flags_all_targets(tmp_path: Path) -> None:
    """A line carrying a move/copy verb AND a second write verb must NOT collapse to the
    last literal (which would silently drop the copy target) — every in-code literal is a
    target (code-review M2, fail-safe)."""
    _skill(tmp_path, "build-slice",
           "run `copy architecture/lessons-learned.md` then `create architecture/build-checks.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 2, f"both write targets must be flagged, not just the last; got {len(ops)}"
    assert all(o.klass == OP_UNROUTED for o in ops)
    vals = {o.value for o in ops}
    assert any("lessons-learned" in v for v in vals), "the copy target must not be dropped (M2)"


def test_single_clean_move_still_dest_only(tmp_path: Path) -> None:
    """The M2 fix is behavior-preserving: a SINGLE clean move still emits ONE op (the dest)."""
    _skill(tmp_path, "archive",
           "run `mv architecture/slices/slice-042-foo architecture/lessons-learned.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1 and ops[0].klass == OP_UNROUTED
    assert "lessons-learned" in ops[0].value, "the DEST governs a single clean move (B2 preserved)"


# ── slice-113 / B2 ([[ADR-106]]): SEAM-AWARE op-gate — a CONVERTED `<vault>/` sink stays
# VISIBLE and correctly classified. AP-5 non-vacuity: each of these FAILs if the value
# EXTRACTOR is not upgraded to `_OP_SINK_TOKEN_RE` in lockstep with `_OP_SINK_RE` — with the
# old `_PATH_TOKEN_RE` the `<vault>/` value collapses to the bare prefix and every sink
# sub-regex (`_ACTIVE_FOLDER_RE` / `_UNDECIDED_DISPOSITION_RE`) misses. ──
def test_seam_aware_vault_active_folder_sink_deferred(tmp_path: Path) -> None:
    """A converted `<vault>/slices/slice-NNN/...` in-loop active-folder write → OP_DEFERRED_TO_FLIP.
    The EXTRACTOR non-vacuity proof: with the old `_PATH_TOKEN_RE` the value collapses to bare
    `<vault>/`, `_ACTIVE_FOLDER_RE` misses, and it mis-flags OP_UNROUTED."""
    _skill(tmp_path, "build-slice", "run `git add <vault>/slices/slice-NNN-foo/build-log.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1
    assert ops[0].klass == OP_DEFERRED_TO_FLIP, (
        f"a converted <vault>/ active-folder sink must classify DEFERRED (the extractor must "
        f"capture the full token, not bare '<vault>/'); got {ops[0].klass} value={ops[0].value!r}"
    )
    assert "slices/slice-NNN-foo" in ops[0].value, "the full <vault>/ token must be extracted"


def test_seam_aware_vault_slice_queue_sink_out_of_scope(tmp_path: Path) -> None:
    """A converted `<vault>/slice-queue.md` in-loop write → OP_OUT_OF_SCOPE (undecided-disposition
    ledger). Proves `_UNDECIDED_DISPOSITION_RE` fires on the EXTRACTED `<vault>/` value."""
    _skill(tmp_path, "slice", "run `git add <vault>/slice-queue.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1
    assert ops[0].klass == OP_OUT_OF_SCOPE, (
        f"a converted <vault>/slice-queue.md write is the undecided-disposition ledger → "
        f"OUT_OF_SCOPE; got {ops[0].klass}"
    )


def test_seam_aware_vault_unrouted_aggregate_still_bites(tmp_path: Path) -> None:
    """The forward-protection ADR-106 promises: an un-routed in-loop write to a CONVERTED
    `<vault>/` shared-aggregate still reds OP_UNROUTED — the gate is NOT blinded by the rollout
    of the very convention it must police (R-32 write-safety)."""
    _skill(tmp_path, "reflect", "run `git add <vault>/risk-register.md`\n")
    ops = op_audit_root(tmp_path)
    assert len(ops) == 1
    assert ops[0].klass == OP_UNROUTED, (
        f"the seam-aware op-gate must still catch an un-routed <vault>/ in-loop write "
        f"(else the convention rollout defeats the gate — R-32); got {ops[0].klass}"
    )
    # m1 (/code-review): OP_UNROUTED is the failure-mode outcome too (a bare-`<vault>/` value
    # from a reverted extractor falls through every sub-regex → OP_UNROUTED), so the klass
    # assertion alone is vacuous against an extractor revert. Asserting the FULL token was
    # extracted is what makes this test genuinely extractor-sensitive (red on the bare-prefix
    # collapse) — restoring the "each of the three" non-vacuity claim.
    assert "risk-register.md" in ops[0].value, (
        f"the extractor must capture the full <vault>/ token, not the bare prefix; "
        f"got value={ops[0].value!r}"
    )
