#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Helper function to print test results
print_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $1${NC}"
        ((FAILED++))
    fi
}

echo "=== Starting API Tests ==="

# 1. Test User Authentication
echo -e "\n=== User Authentication Tests ==="

# Create test user
USER_CREDS=$(php think user:create 1000.00)
USER_ID=$(echo "$USER_CREDS" | grep "User ID:" | cut -d' ' -f3)
KEY=$(echo "$USER_CREDS" | grep "Key:" | cut -d' ' -f2)

# Test login with valid credentials
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"$USER_ID\", \"key\": \"$KEY\"}" | python3 scripts/parse_login.py)
[ ! -z "$TOKEN" ]
print_result "Login with valid credentials"

# Test login with invalid credentials
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"user_id": "invalid", "key": "invalid"}')
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 401 and data.get('data') is None, f'Expected code 401, got: {data}'"
print_result "Login with invalid credentials returns 401"

# 2. Test Order Submission
echo -e "\n=== Order Submission Tests ==="

# Test valid order (1-500元)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d '{"amount": 100}')
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 200 and data['data'] and 'order_id' in data['data'], f'Invalid response: {data}'"
ORDER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['order_id'])")
print_result "Submit valid order (100元)"

# Test invalid amount (>500元)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d '{"amount": 501}')
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 400 and data.get('data') is None, f'Expected code 400, got: {data}'"
print_result "Reject order >500元"

# Test invalid amount (<1元)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d '{"amount": 0.5}')
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 400 and data.get('data') is None, f'Expected code 400, got: {data}'"
print_result "Reject order <1元"

# 3. Test Order Status Query
echo -e "\n=== Order Status Query Tests ==="

# Query existing order
RESPONSE=$(curl -s "http://localhost:8000/api/orders/status/$ORDER_ID" \
    -H "Authorization: $TOKEN")
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 200 and data['data'] and 'status' in data['data'], f'Invalid response: {data}'"
print_result "Query existing order status"

# Query non-existent order
RESPONSE=$(curl -s "http://localhost:8000/api/orders/status/nonexistent123" \
    -H "Authorization: $TOKEN")
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 404 and data.get('data') is None, f'Expected code 404, got: {data}'"
print_result "Query non-existent order returns 404"

# 4. Test Order Callback
echo -e "\n=== Order Callback Tests ==="

# Create fresh order for successful callback
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d '{"amount": 25}')
CALLBACK_ORDER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['order_id'])")

# Test successful callback
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/callback \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d "{\"order_id\": \"$CALLBACK_ORDER_ID\", \"success\": true}")
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 200 and data['data'] and data['data']['order_id'] == '$CALLBACK_ORDER_ID', f'Invalid response: {data}'"
print_result "Successful order callback"

# Verify order status updated to success
RESPONSE=$(curl -s "http://localhost:8000/api/orders/status/$CALLBACK_ORDER_ID" \
    -H "Authorization: $TOKEN")
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 200 and data['data'] and data['data']['status'] == '成功', f'Expected successful status, got: {data}'"
print_result "Order status updated to 成功"

# Create order for failure test
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d '{"amount": 50}')
FAIL_ORDER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['order_id'])")
INITIAL_BALANCE=$(echo "$RESPONSE" | python3 scripts/check_balance.py)

# Test failed callback (should trigger refund)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/callback \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d "{\"order_id\": \"$FAIL_ORDER_ID\", \"success\": false}")

# Verify refund was processed
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d '{"amount": 1}')
FINAL_BALANCE=$(echo "$RESPONSE" | python3 scripts/check_balance.py)
[ "$INITIAL_BALANCE" = "$FINAL_BALANCE" ]
print_result "Failed order callback with refund"

# 5. Test Error Handling
echo -e "\n=== Error Handling Tests ==="

# Test unauthorized access
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -d '{"amount": 100}')
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 401 and data.get('data') is None, f'Expected code 401, got: {data}'"
print_result "Unauthorized access returns 401"

# Test invalid token
RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/submit \
    -H "Content-Type: application/json" \
    -H "Authorization: invalid.token" \
    -d '{"amount": 100}')
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert data['code'] == 401 and data.get('data') is None, f'Expected code 401, got: {data}'"
print_result "Invalid token returns 401"

# Print test summary
echo -e "\n=== Test Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total: $((PASSED + FAILED))"

exit $FAILED
