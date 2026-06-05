"""Unit + behavior tests for the post-flip queue CAS routing (slice-109 / [[ADR-098]]).

Companion to the concurrency proof in test_post_flip_queue_cas_concurrency.py:
this module pins the single-process contracts — the writers route through the CAS
channel, the bounded retry re-runs on a stale base, the no-flip LF output stays
byte-identical to the prior safe_write_text path, and the CRLF-on-disk edge is
pinned by EXECUTION (Critic B1 — not reasoned "tool-written LF")."""
from __future__ import annotations

import datetime
import inspect
from pathlib import Path

import tools.slice_queue_claim as claim_mod
import tools.slice_queue_writer as writer_mod
from tools._vault_write import safe_write_text


def test_queue_writers_route_through_cas_channel() -> None:
    """AC1: the three RMW writers call `safe_rewrite_text(..., expected_base=...)`
    (the CAS channel), NOT the non-CAS whole-file `safe_write_text`."""
    sources = {
        "record_pick": inspect.getsource(writer_mod.record_pick),
        "write_slice_queue": inspect.getsource(writer_mod.write_slice_queue),
        "_cas_rewrite": inspect.getsource(claim_mod._cas_rewrite),
    }
    for name, src in sources.items():
        assert "safe_rewrite_text" in src, f"{name} does not route through the CAS channel"
        assert "expected_base" in src, f"{name} CAS call has no expected_base"
        assert "safe_write_text(" not in src, f"{name} still uses non-CAS safe_write_text"


def test_record_pick_cas_retry_on_stale_base(tmp_path: Path, monkeypatch) -> None:
    """AC1 / single-process retry: a StaleVaultBaseError on the first CAS write
    triggers a re-read + re-compose + retry; the pick still lands (bounded loop)."""
    q = tmp_path / "architecture" / "slice-queue.md"
    q.parent.mkdir(parents=True)
    q.write_bytes(
        b"# Slice queue\n\n## Pick log\n\n- slice-001-seed \xe2\x80\x94 picked T by S\n"
    )
    real = writer_mod.safe_rewrite_text
    calls = {"n": 0}

    def flaky(path, text, *, expected_base, encoding="utf-8"):
        calls["n"] += 1
        if calls["n"] == 1:
            raise writer_mod.StaleVaultBaseError("simulated concurrent write")
        return real(path, text, expected_base=expected_base, encoding=encoding)

    monkeypatch.setattr(writer_mod, "safe_rewrite_text", flaky)
    writer_mod.record_pick(
        repo_root=Path("."), slice_name="slice-109-x",
        picker_identity="N e@x", out_path=q,
    )
    assert calls["n"] == 2, "record_pick did not retry on StaleVaultBaseError"
    assert "slice-109-x" in q.read_text(encoding="utf-8")


def test_record_pick_retry_exhaustion_raises(tmp_path: Path, monkeypatch) -> None:
    """Must-not-defer / Critic M-add-1: retry-budget exhaustion RAISES (fail-visible)
    for the non-regenerable provenance writer — never a silent fall-back."""
    q = tmp_path / "architecture" / "slice-queue.md"
    q.parent.mkdir(parents=True)
    q.write_bytes(b"# Slice queue\n\n## Pick log\n\n- slice-001-seed x\n")

    def always_stale(path, text, *, expected_base, encoding="utf-8"):
        raise writer_mod.StaleVaultBaseError("persistent contention")

    monkeypatch.setattr(writer_mod, "safe_rewrite_text", always_stale)
    import pytest

    with pytest.raises(writer_mod.StaleVaultBaseError):
        writer_mod.record_pick(
            repo_root=Path("."), slice_name="slice-109-x",
            picker_identity="N e@x", out_path=q,
        )


def test_no_flip_queue_output_byte_identical_lf(tmp_path: Path) -> None:
    """AC4: on the LF no-flip default the CAS write is byte-identical to the prior
    `safe_write_text` path — re-writing the CAS output via safe_write_text yields
    the SAME bytes (no EOL churn, LF preserved)."""
    q = tmp_path / "architecture" / "slice-queue.md"
    q.parent.mkdir(parents=True)
    cands = [{"name": "add-foo", "source": "x", "hint_files": [],
              "effort": "SMALL", "risk_retired": "LOW"}]
    now = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
    writer_mod.write_slice_queue(
        repo_root=Path("."), candidates=cands, active_slice_num=109,
        graph_path=None, now=now, out_path=q,
    )
    cas_bytes = q.read_bytes()
    assert b"\r" not in cas_bytes, "CAS wrote CRLF on the LF-default queue"
    p2 = tmp_path / "via_safe_write_text.md"
    safe_write_text(p2, cas_bytes.decode("utf-8"))
    assert p2.read_bytes() == cas_bytes, (
        "CAS output diverges from safe_write_text on the LF no-flip default"
    )


def test_crlf_on_disk_queue_behavior_pinned(tmp_path: Path) -> None:
    """AC4 / Critic B1 (EXECUTED, not reasoned): on a CRLF-on-disk queue the
    EOL-PRESERVING CAS write keeps CRLF — the documented divergence from
    LF-faithful safe_write_text that `.gitattributes eol=lf` prevents on checkout."""
    q = tmp_path / "architecture" / "slice-queue.md"
    q.parent.mkdir(parents=True)
    q.write_bytes(
        b"# Slice queue\r\n\r\n## Pick log\r\n\r\n"
        b"- slice-001-seed \xe2\x80\x94 picked T by S\r\n"
    )
    writer_mod.record_pick(
        repo_root=Path("."), slice_name="slice-109-x",
        picker_identity="N e@x", out_path=q,
    )
    data = q.read_bytes()
    assert b"\r\n" in data, (
        "EOL-preserving CAS should keep CRLF on a CRLF-on-disk queue (B1 divergence)"
    )
    assert b"slice-109-x" in data, "pick did not land"


def test_shippability_catalog_pins_post_flip_cas() -> None:
    """AC5 / RPCD-1: the shippability catalog carries a slice-109 row pinning the
    post-flip CAS write-safety tests, so the guarantee can never silently regress."""
    from tools._vault_paths import VAULT_ROOT  # vault-location-aware (post-flip [[ADR-107]])
    ship = (
        Path(__file__).resolve().parents[2] / VAULT_ROOT / "shippability.md"
    ).read_text(encoding="utf-8")
    assert "slice-109-add-post-flip-vault-conflict-safety" in ship, "no slice-109 shippability row"
    assert "test_post_flip_queue_cas_concurrency.py" in ship, (
        "the concurrency proof is not pinned in the shippability catalog (RPCD-1)"
    )


def test_cas_rewrite_crlf_release_unclaimed_is_noop(tmp_path: Path) -> None:
    """code-review m3: on a CRLF-on-disk queue, releasing an already-unclaimed
    candidate is a no-op (`wrote == False`, bytes unchanged) — this relies on
    `apply_release` returning the raw base text early; pin it so a future change
    there can't silently flip a CRLF no-op into a spurious write."""
    from tools.slice_queue_claim import _cas_rewrite, apply_release

    q = tmp_path / "architecture" / "slice-queue.md"
    q.parent.mkdir(parents=True)
    body = (
        "# Slice queue\r\n\r\n## Candidates\r\n\r\n### add-foo\r\n\r\n"
        "- **Source:** seed\r\n- **Effort:** SMALL\r\n- **Risk-retired:** LOW\r\n"
    )
    q.write_bytes(body.encode("utf-8"))
    before = q.read_bytes()
    wrote = _cas_rewrite(q, lambda t: apply_release(t, "add-foo"), always_write=False)
    assert wrote is False, "CRLF release-of-unclaimed should be a no-op"
    assert q.read_bytes() == before, "no-op must not rewrite the file (CRLF preserved)"
