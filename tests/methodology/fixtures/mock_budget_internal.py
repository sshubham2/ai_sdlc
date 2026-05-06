"""Fixture for tests/methodology/test_mock_budget_lint.py.

Internal-class mock. Violates TDD-2 internal-mock rule (target not at boundary).
Severity: Important (not in seam allowlist).
"""
from unittest.mock import patch


@patch("src.services.user_service.UserService")
def test_mocks_internal_class(mock_service):
    """Mocks internal class - TDD-2 violation; should flag Important."""
    assert mock_service is not None
