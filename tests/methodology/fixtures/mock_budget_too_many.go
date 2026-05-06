// Fixture for tests/methodology/test_mock_budget_lint.py (Go variant).
// Two mock constructor calls in one test function = mock-budget violation.

package mock_budget_too_many_test

import "testing"

type MockUserService struct{}
type MockOrderService struct{}

func TestUserAndOrder(t *testing.T) {
	userMock := NewMockUserService()
	orderMock := NewMockOrderService()
	_ = userMock
	_ = orderMock
}

func NewMockUserService() *MockUserService   { return &MockUserService{} }
func NewMockOrderService() *MockOrderService { return &MockOrderService{} }
