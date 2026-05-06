// Fixture for tests/methodology/test_mock_budget_lint.py (Go variant).
// Clean test: one mock constructor call per test function = no mock-budget violation.
// This file is NOT collected by pytest (filename does not match test_*.py pattern).

package mock_budget_clean_test

import "testing"

type MockUserService struct{}

func TestUserCreated(t *testing.T) {
	mock := NewMockUserService()
	_ = mock
}

func NewMockUserService() *MockUserService {
	return &MockUserService{}
}
