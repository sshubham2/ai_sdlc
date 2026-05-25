"""Vault-root path constant (slice-068).

Exports VAULT_ROOT — the single seam routing tools/*.py filesystem
references to the vault directory. Default ``Path("architecture")``;
override via env var ``AI_SDLC_VAULT_ROOT`` (read at module import).

Per ADR-065. Leading-underscore-helper module per UTF8-STDOUT-1 /
``tools/_stdout.py`` precedent — auto-excluded from PMI-1 inventory
(``tools/plugin_manifest_audit.py:148`` filter).

**Read-at-import + consumer-freeze cascade** (production-correctness
semantic per ADR-065 §Decision + design.md §Consumer-freeze cascade):
the env var is read EXACTLY ONCE at this module's import. Downstream
consumers that compose VAULT_ROOT into their own module-level constants
(e.g., ``tools.slice_queue_writer._INDEX_MD_REL = VAULT_ROOT / "slices"
/ "_index.md"``) FREEZE the derived Path at THEIR import-time value.
In-process ``monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", ...)``
does NOT propagate to those frozen consumer constants. Cross-process env
override works via subprocess fixtures (env injection at process
boundary). Pinned by
``tests/methodology/test_vault_root_constant.py::test_consumer_constants_are_frozen_at_first_import``.
"""
from __future__ import annotations

import os
from pathlib import Path

_ENV_VAR = "AI_SDLC_VAULT_ROOT"
_DEFAULT = "architecture"

VAULT_ROOT: Path = Path(os.environ.get(_ENV_VAR, _DEFAULT))
