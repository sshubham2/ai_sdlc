"""slice_queue_writer render-contract pins — slice-085 / ADR-077 / M3.

`_RENDERED_FIELD_LABELS` is a genuine single source of truth ONLY if `_format_entry`
renders FROM it (not a parallel hand-listed copy). This test pins that relationship
(mirrors the on-disk-contract pin style of test_psq_2_claim_machinery.py) so a future
label rename in the constant is reflected in the emitted queue — and the
`parallel_conflict_resolver` truncation-shape reader (which imports the same constant)
can never silently disagree with the writer.
"""
from __future__ import annotations

import re

from tools.slice_queue_writer import _RENDERED_FIELD_LABELS, _format_entry


def _label_prefix(line: str) -> str | None:
    m = re.match(r"(- \*\*[^*]+:\*\*)", line)
    return m.group(1) if m else None


_ITEM = {
    "name": "add-foo",
    "source": "synthetic",
    "blast_radius": ["x"],
    "parallel_safety": "NON-OVERLAPPING",
    "effort": "SMALL",
    "risk_retired": "LOW",
}


def test_format_entry_renders_from_rendered_field_labels_constant(monkeypatch) -> None:
    # (1) the emitted PSQ-1 field-line prefixes equal the constant, in order
    lines = _format_entry(dict(_ITEM))
    field_prefixes = [_label_prefix(l) for l in lines if l.startswith("- **")]
    assert field_prefixes == list(_RENDERED_FIELD_LABELS), (
        "emitted field labels must equal _RENDERED_FIELD_LABELS in order"
    )

    # (2) the constant IS the render source: renaming a label in the constant changes
    #     the emitted line (a parallel hand-listed copy would not react).
    import tools.slice_queue_writer as w
    patched = ("- **SRC:**",) + tuple(_RENDERED_FIELD_LABELS[1:])
    monkeypatch.setattr(w, "_RENDERED_FIELD_LABELS", patched)
    patched_lines = w._format_entry(dict(_ITEM))
    assert any(l.startswith("- **SRC:**") for l in patched_lines), (
        "_format_entry must render FROM _RENDERED_FIELD_LABELS (not a parallel copy)"
    )
    assert not any(l.startswith("- **Source:**") for l in patched_lines)
