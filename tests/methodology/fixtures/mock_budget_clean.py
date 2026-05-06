"""Fixture for tests/methodology/test_mock_budget_lint.py.

Clean test file: one boundary mock, allowed by TDD-2.
This file is NOT collected by pytest (filename does not match test_*.py pattern).
"""
from unittest.mock import patch


@patch("requests.get")
def test_fetches_data(mock_get):
    """Single mock at network boundary - TDD-2 compliant."""
    mock_get.return_value.status_code = 200
    assert mock_get is not None
