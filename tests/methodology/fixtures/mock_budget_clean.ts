/**
 * Fixture for tests/methodology/test_mock_budget_lint.py.
 *
 * Clean TypeScript test file: one boundary mock, allowed by TDD-2.
 * This file is NOT collected by pytest (filename does not match test_*.py pattern).
 */
import { vi, it, describe } from 'vitest';

describe('UserService', () => {
  it('fetches data via single boundary mock', async () => {
    vi.mock('axios');
    // Single mock at network boundary - TDD-2 compliant
  });
});
