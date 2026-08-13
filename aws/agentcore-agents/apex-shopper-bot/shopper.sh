#!/bin/bash
# ShopperBot - Clean interface for business users
# Usage: ./shopper.sh "your question here"

AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_shopper_bot-E20HMiEAtn"
REGION="us-east-1"
TEMP_FILE="/tmp/shopper_response_$$.json"

# Get user input
if [ -z "$1" ]; then
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║        Welcome to ShopperBot!          ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    read -p "What can I help you find today? " QUERY
else
    QUERY="$1"
fi

# Encode payload
PAYLOAD=$(echo -n "{\"prompt\": \"$QUERY\"}" | base64)

# Call agent (suppress AWS CLI metadata output)
aws bedrock-agentcore invoke-agent-runtime \
    --agent-runtime-arn "$AGENT_ARN" \
    --region "$REGION" \
    --payload "$PAYLOAD" "$TEMP_FILE" > /dev/null 2>&1

# Extract and display clean response
echo ""
python3 -c "
import json
with open('$TEMP_FILE', 'r') as f:
    data = json.load(f)
    response = data.get('response', data.get('result', 'No response'))
    print(response)
" 2>/dev/null

# Cleanup
rm -f "$TEMP_FILE"
echo ""
