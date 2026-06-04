"""Top-level pytest conftest for the AI SDLC test suite.

Adds ``tests/`` to ``sys.path`` so shared test-support modules that live
directly under ``tests/`` (notably ``_vault_isolation`` — the location-agnostic
vault-root isolation helper, slice-110 / [[ADR-101]]) are importable as bare
modules from any test file in the tree, regardless of per-package ``__init__``
layout. This is the single place the shim lives; individual test files just
``import _vault_isolation``.
"""
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
