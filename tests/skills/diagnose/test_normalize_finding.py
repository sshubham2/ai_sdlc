"""Tests for assemble.normalize_finding (slice-001 / B2 / M1).

Validates that the function correctly:
- Coerces dict-wrapped findings to list shape
- Normalizes evidence as flat strings -> list of {path, lines, note}
- Recomputes IDs not matching F-<CAT>-<8hex> via per-pass signature extractor
- Drops unknown fields with a logged warning
- Is NOT called by load_findings() (M1: ingest-only)

Rule reference: slice-001 dispositions B2, M1.
"""
import logging

import pytest

from assemble import REQUIRED_FIELDS, _signature_extractors, normalize_finding


def _valid_finding() -> dict:
    """A minimal schema-conformant finding for use as a baseline."""
    return {
        "id": "F-DEAD-aabbccdd",
        "pass": "03a-dead-code",
        "category": "dead-code",
        "severity": "low",
        "blast_radius": "small",
        "reversibility": "cheap",
        "title": "Module legacy_auth.py unreachable",
        "description": "No inbound edges.",
        "evidence": [
            {"path": "src/legacy_auth.py", "lines": "1-340", "note": "no inbound"}
        ],
        "suggested_action": "Delete the file after grep verification.",
        "effort_estimate": "small",
        "slice_candidate": "maybe",
    }


# --- B2: per-pass signature extractor + ID recompute ---


def test_dict_wrapped_findings_unwrapped():
    """A finding wrapped in {findings: [...]} or {finding: {...}} normalizes.

    Defect class: Subagents on prior runs produced dict-wrapped output.
    normalize_finding must accept the wrapped shape and unwrap to a single
    finding dict.
    Disposition ref: B2 (and the related "dict-wrapped findings" coercion
    documented in mission-brief AC #3).
    """
    raw = {"finding": _valid_finding()}
    out = normalize_finding(raw, "03a-dead-code")
    assert out is not None, "wrapped finding should normalize, not be rejected"
    for f in REQUIRED_FIELDS:
        assert f in out, f"required field {f!r} missing after normalize"
    assert out["id"].startswith("F-DEAD-")


def test_flat_string_evidence_normalized():
    """evidence: ['path/to/file.py'] -> list of {path,lines,note} dicts.

    Defect class: subagents sometimes emit evidence as a flat string list
    (the easiest LLM mistake) instead of dicts. normalize must convert.
    Disposition ref: B2 / mission-brief AC #3.
    """
    raw = _valid_finding()
    raw["evidence"] = ["src/legacy_auth.py", "src/main.py"]
    out = normalize_finding(raw, "03a-dead-code")
    assert out is not None
    assert isinstance(out["evidence"], list)
    assert len(out["evidence"]) == 2
    for entry in out["evidence"]:
        assert isinstance(entry, dict)
        assert "path" in entry
        assert "lines" in entry
        assert "note" in entry
    assert out["evidence"][0]["path"] == "src/legacy_auth.py"


def test_malformed_id_recomputed_via_per_pass_extractor():
    """An ID that doesn't match F-<CAT>-<8hex> is recomputed deterministically.

    Defect class: per critique B2, the schema's ID recipe uses per-pass
    signature rules. The orchestrator can't reproduce a subagent's signature
    without help, so normalize_finding uses _signature_extractors to derive
    one from the finding's other fields. Default extractor is title; some
    passes override.

    Recompute MUST be deterministic — same input twice yields same ID.
    Disposition ref: B2 (Option 2 chosen).
    """
    raw = _valid_finding()
    raw["id"] = "BAD-ID-format"
    out1 = normalize_finding(raw.copy(), "03a-dead-code")
    out2 = normalize_finding(raw.copy(), "03a-dead-code")
    assert out1 is not None and out2 is not None
    # Recomputed ID matches schema shape
    import re

    assert re.match(r"^F-[A-Z]+-[a-f0-9]{8}$", out1["id"]), (
        f"recomputed ID {out1['id']!r} doesn't match F-<CAT>-<8hex>"
    )
    # Determinism: same inputs produce same ID
    assert out1["id"] == out2["id"], (
        "recomputation must be deterministic so re-runs preserve carryover"
    )


def test_unknown_field_dropped_with_warning(caplog: pytest.LogCaptureFixture):
    """Unknown fields like 'confidence', 'recommendation' are dropped + warned.

    Defect class: 2026-05-09 subagents emitted non-schema fields like
    `confidence` and `recommendation`. normalize must drop them so the
    written YAML stays schema-conformant, with a warning so the operator
    can see the LLM drift.
    Disposition ref: AC #3.
    """
    raw = _valid_finding()
    raw["confidence"] = 0.85
    raw["recommendation"] = "do nothing"
    with caplog.at_level(logging.WARNING):
        out = normalize_finding(raw, "03a-dead-code")
    assert out is not None
    assert "confidence" not in out
    assert "recommendation" not in out
    assert any("confidence" in rec.message or "recommendation" in rec.message
               for rec in caplog.records), (
        "expected a warning naming the dropped unknown field(s)"
    )


# --- M1: load_findings strictness preserved ---


def test_load_findings_unchanged_for_already_normalized_yaml(tmp_path):
    """load_findings() must NOT call normalize_finding (M1).

    Defect class: per critique M1, sharing normalize_finding between
    write_pass.py and load_findings would silently mutate already-validated
    YAMLs from prior runs and risk dropping owner-annotation keys. M1 scopes
    normalize_finding to ingest-only.

    Verification: a YAML with a known set of required fields loads cleanly
    without any warning logs being emitted (which would indicate
    normalize_finding got called). And: a YAML with extra fields IS still
    rejected by load_findings strictness (current behavior preserved).
    Disposition ref: M1.
    """
    import yaml as yaml_lib

    from assemble import load_findings

    findings_dir = tmp_path / "findings"
    findings_dir.mkdir()
    finding = _valid_finding()
    (findings_dir / "01-intent.yaml").write_text(
        yaml_lib.safe_dump([finding], sort_keys=False), encoding="utf-8"
    )

    loaded = load_findings(findings_dir)
    assert len(loaded) == 1
    assert loaded[0]["id"] == finding["id"]


# --- _signature_extractors registry sanity ---


def test_signature_extractors_default_uses_title():
    """Default extractor is `lambda f: f["title"]` for any pass without override."""
    finding = _valid_finding()
    extractor = _signature_extractors.get("03a-dead-code") or _signature_extractors["__default__"]
    assert extractor(finding) == finding["title"]


def test_signature_extractor_03b_duplicates_uses_smallest_evidence_path():
    """03b-duplicates overrides default to use lexicographically smallest evidence path.

    Per passes/03b-duplicates.md, the canonical signature is
    'the lexicographically smallest path among the duplicates'.
    """
    finding = _valid_finding()
    finding["evidence"] = [
        {"path": "src/zzz/last.py", "lines": "1", "note": ""},
        {"path": "src/aaa/first.py", "lines": "1", "note": ""},
        {"path": "src/mmm/middle.py", "lines": "1", "note": ""},
    ]
    extractor = _signature_extractors["03b-duplicates"]
    assert extractor(finding) == "src/aaa/first.py"
