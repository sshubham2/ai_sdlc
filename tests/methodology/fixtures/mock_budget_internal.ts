/**
 * Fixture for tests/methodology/test_mock_budget_lint.py.
 *
 * Internal-class mock. Violates TDD-2 internal-mock rule (target not at boundary).
 * Severity: Important (not in seam allowlist).
 */
import { vi, it, describe } from 'vitest';

describe('UserService', () => {
  it('mocks an internal module', async () => {
    vi.mock('./services/user-service');
  });
});
