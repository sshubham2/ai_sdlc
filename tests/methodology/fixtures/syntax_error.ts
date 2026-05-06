/**
 * Fixture for tests/methodology/test_mock_budget_lint.py.
 *
 * Deliberate syntax error to test linter graceful handling.
 * The linter should emit a parse-error finding rather than crashing.
 */
import { vi } from 'vitest
const broken =
