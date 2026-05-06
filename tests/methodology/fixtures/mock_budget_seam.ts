/**
 * Fixture for tests/methodology/test_mock_budget_lint.py.
 *
 * Internal mock on a cross-chunk seam. Severity escalates Important -> Critical
 * when target is in .cross-chunk-seams allowlist.
 */
import { vi, it, describe } from 'vitest';

describe('Receipts', () => {
  it('mocks a documented cross-chunk seam', async () => {
    vi.mock('./api/receipts');
  });
});
