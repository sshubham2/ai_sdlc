"""Fixture for tests/methodology/test_mock_budget_lint.py.

Test with >1 mock per function. Violates TDD-2 mock-budget rule.
Both mocks are at boundaries (requests), so only mock-budget fires.
"""
from unittest.mock import patch


@patch("requests.post")
@patch("requests.get")
def test_double_boundary_mock(mock_get, mock_post):
    """Two boundary mocks - exceeds budget regardless of target validity."""
    assert mock_get is not None
    assert mock_post is not None
