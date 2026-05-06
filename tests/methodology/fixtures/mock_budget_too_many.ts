/**
 * Fixture for tests/methodology/test_mock_budget_lint.py.
 *
 * Test with >1 mock per it() block. Violates TDD-2 mock-budget.
 * Both mocks are at boundaries (axios, node-fetch), so only mock-budget fires.
 */
import { vi, it, describe } from 'vitest';

describe('Service', () => {
  it('mocks two boundaries (TDD-2 budget violation)', async () => {
    vi.mock('axios');
    vi.mock('node-fetch');
  });
});
