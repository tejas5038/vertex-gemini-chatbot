#!/bin/bash

# Test script for Vertex AI Gemini Chatbot API
# Usage: ./test_api.sh [BASE_URL]
# Example: ./test_api.sh http://localhost:8080
# Example: ./test_api.sh https://your-service-xyz.run.app

BASE_URL="${1:-http://localhost:8080}"
SESSION_ID="test-session-$(date +%s)"

echo "=========================================="
echo "Testing Vertex AI Gemini Chatbot API"
echo "Base URL: $BASE_URL"
echo "Session ID: $SESSION_ID"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
curl -s "$BASE_URL/health" | jq . || echo "Failed"
echo ""
echo ""

# Test 2: Calculator Tool
echo -e "${YELLOW}Test 2: Calculator Tool - What is 25 * 47?${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"user_message\": \"What is 25 * 47?\"
  }")

echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | jq -e '.tool_calls[0].tool == "calculator"' > /dev/null; then
    echo -e "${GREEN}✓ Calculator tool called successfully${NC}"
else
    echo -e "${RED}✗ Calculator tool not called${NC}"
fi
echo ""

# Test 3: Web Fetch Tool
echo -e "${YELLOW}Test 3: Web Fetch Tool - Bitcoin Price${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"user_message\": \"Fetch the current Bitcoin price from https://api.coindesk.com/v1/bpi/currentprice.json\"
  }")

echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | jq -e '.tool_calls[0].tool == "fetch_url"' > /dev/null; then
    echo -e "${GREEN}✓ Web fetch tool called successfully${NC}"
else
    echo -e "${RED}✗ Web fetch tool not called${NC}"
fi
echo ""

# Test 4: Email Tool (Stub)
echo -e "${YELLOW}Test 4: Email Tool (Stub)${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"user_message\": \"Send an email to test@example.com with subject 'Test' and body 'Hello World'\"
  }")

echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | jq -e '.tool_calls[0].tool == "send_email"' > /dev/null; then
    echo -e "${GREEN}✓ Email tool called (stub mode)${NC}"
else
    echo -e "${RED}✗ Email tool not called${NC}"
fi
echo ""

# Test 5: Conversation Memory
echo -e "${YELLOW}Test 5: Conversation Memory${NC}"
echo "Sending first message..."
curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"memory-test-$SESSION_ID\",
    \"user_message\": \"My name is Alice\"
  }" | jq -r '.assistant_message'

echo ""
echo "Asking about previous message..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"memory-test-$SESSION_ID\",
    \"user_message\": \"What is my name?\"
  }")

echo "$RESPONSE" | jq -r '.assistant_message'
echo ""

if echo "$RESPONSE" | grep -qi "alice"; then
    echo -e "${GREEN}✓ Memory working - Name remembered${NC}"
else
    echo -e "${RED}✗ Memory not working${NC}"
fi
echo ""

# Test 6: Reset Conversation
echo -e "${YELLOW}Test 6: Reset Conversation${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/reset" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\"
  }")

echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | jq -e '.error == false' > /dev/null; then
    echo -e "${GREEN}✓ Conversation reset successfully${NC}"
else
    echo -e "${RED}✗ Reset failed${NC}"
fi
echo ""

# Test 7: Invalid Request Handling
echo -e "${YELLOW}Test 7: Invalid Request Handling${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"test\",
    \"user_message\": \"\"
  }")

echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | jq -e '.error == true' > /dev/null; then
    echo -e "${GREEN}✓ Invalid request properly rejected${NC}"
else
    echo -e "${RED}✗ Invalid request not handled${NC}"
fi
echo ""

# Test 8: Large Calculation
echo -e "${YELLOW}Test 8: Complex Calculation${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"user_message\": \"Calculate (123 + 456) * 789 / 10\"
  }")

echo "$RESPONSE" | jq .
echo ""

# Test 9: Non-whitelisted URL
echo -e "${YELLOW}Test 9: Non-whitelisted URL (Should Fail)${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"user_message\": \"Fetch data from https://malicious-site.com/api\"
  }")

echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | grep -qi "whitelist\|not in whitelist"; then
    echo -e "${GREEN}✓ Non-whitelisted URL properly blocked${NC}"
else
    echo -e "${YELLOW}⚠ URL blocking may need verification${NC}"
fi
echo ""

echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
