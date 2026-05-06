"""Fixture for tests/methodology/test_mock_budget_lint.py.

Internal mock on a cross-chunk seam. Severity escalates Important -> Critical
when target is in .cross-chunk-seams allowlist.
"""
from unittest.mock import patch


@patch("src.api.receipts.upload_receipt")
def test_mocks_documented_seam(mock_upload):
    """When target is in .cross-chunk-seams, severity escalates to Critical."""
    assert mock_upload is not None
