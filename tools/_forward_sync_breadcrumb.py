"""External-drift breadcrumb sink (slice-117; [[ADR-108]] round-2 M1).

When a forward-sync gate classifies a divergence as ``external-drift`` (a
sibling slice forward-synced the shared install/venv ahead — R-28), it emits a
WARN at exit 0. Because the downstream consumers (``/build-slice`` Step 6,
``/reflect`` Step 5b-{avfs,mcfs,tvfs}) treat exit 0 as PASS, a False-direction
misclassification would otherwise be a silent PASS. This module makes that case
**forensically recoverable**: it appends a one-line breadcrumb to
``VAULT_ROOT / "forward-sync-external-drift-log.md"`` — the EXTERNAL shared store
([[ADR-107]]), so the record survives a merge (NOT a worktree-relative /
gitignored path — that would be the slice-105 / [[ADR-095]] dead-write class).

This is deliberately SEPARATE from the leaf discriminator
``tools/_forward_sync_base.py`` (which stays write-free / leaf-pure per ADR-108).
The vault write is routed through ``_vault_write.safe_append_text`` (R-32 lock +
``O_APPEND``) — the safe-append channel, so it is **VWS-1 ROUTED** by
construction and lost-update-safe under concurrent gate runs across worktrees.

Underscore-prefixed → auto-excluded from the PMI-1 / INST-1 inventory (it has no
``main()`` and is a shared helper, like ``tools/_stdout.py`` / ``tools/_vault_write.py``).
"""
from __future__ import annotations

from datetime import datetime, timezone

from tools._vault_paths import VAULT_ROOT
from tools._vault_write import safe_append_text

_SINK_REL = "forward-sync-external-drift-log.md"


def emit_external_drift(rule: str, source_rel: str, detail: str) -> None:
    """Append a one-line external-drift breadcrumb to the external-store sink.

    ``rule`` — the gate rule id (e.g. ``"CAD-1"``). ``source_rel`` — the gated
    source (e.g. ``"agents/critique.md"`` / ``"VERSION"``). ``detail`` — a short
    human cause (e.g. ``"in-repo 0.84.0 < installed 0.85.0 (sibling-ahead)"``).

    Routed through ``safe_append_text`` (the R-32 safe channel). A write failure
    propagates ``OSError`` / ``TimeoutError`` — the caller decides whether a
    breadcrumb-write failure should be swallowed (it is advisory, not the gate
    verdict) or surfaced.
    """
    stamp = datetime.now(timezone.utc).isoformat()
    line = f"- {stamp} {rule}: external-drift on {source_rel} — {detail}\n"
    safe_append_text(VAULT_ROOT / _SINK_REL, line)
