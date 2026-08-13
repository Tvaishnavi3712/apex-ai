#!/usr/bin/env bash
#
# Path B smoke test: drop a ROBOT XML into the S3 bucket the deploy
# created, then tail the Lambda's CloudWatch logs so you can see the
# trigger fire in real time.
#
# Assumes deploy_path_b.sh has already run.

set -euo pipefail

STACK_NAME="apex-vz-telecom-cycle"
REGION="us-east-1"
SAMPLE_XML="$(dirname "$0")/../synthetic-data/verizon_far_edge/robot_outputs/robot_output_caas_node_v2412_full.xml"

# Resolve bucket + lambda from CFN outputs
BUCKET=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" \
          --query 'Stacks[0].Outputs[?OutputKey==`IngestBucketName`].OutputValue | [0]' \
          --output text 2>/dev/null || echo "")
LAMBDA=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" \
          --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue | [0]' \
          --output text 2>/dev/null | awk -F: '{print $NF}' || echo "")

if [[ -z "$BUCKET" || "$BUCKET" == "None" ]]; then
  echo "✗ Stack '$STACK_NAME' not found.  Run deploy_path_b.sh first."
  exit 1
fi
if [[ ! -f "$SAMPLE_XML" ]]; then
  echo "✗ Sample XML missing: $SAMPLE_XML"
  exit 1
fi

KEY="cycles/$(date +%Y%m%d-%H%M%S)-test.xml"

echo
echo "━━━ Path B smoke test ━━━"
echo "  Bucket : s3://$BUCKET"
echo "  Lambda : $LAMBDA"
echo "  Key    : $KEY"
echo "  XML    : $SAMPLE_XML  ($(stat -f%z "$SAMPLE_XML" 2>/dev/null || stat -c%s "$SAMPLE_XML" 2>/dev/null) bytes)"
echo

read -r -p "Press enter to drop the file and start tailing Lambda logs..."

aws s3 cp "$SAMPLE_XML" "s3://$BUCKET/$KEY" --region "$REGION"
echo "▸ S3 object created.  Lambda should fire any second.  Tailing logs (Ctrl+C to stop)..."
echo

aws logs tail "/aws/lambda/$LAMBDA" --region "$REGION" --follow --since 1m
