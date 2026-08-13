#!/bin/bash
# Upload CRE Underwriting test data to S3
# Usage: ./upload_to_s3.sh [bucket-name]

BUCKET_NAME=${1:-"apex-documents"}
S3_PREFIX="synthetic-data/cre_underwriting"
LOCAL_DIR="$(dirname "$0")"

echo "Uploading CRE Underwriting test data to S3..."
echo "Bucket: s3://${BUCKET_NAME}/${S3_PREFIX}/"
echo ""

# Upload all JSON files
for file in "$LOCAL_DIR"/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Uploading: $filename"
        aws s3 cp "$file" "s3://${BUCKET_NAME}/${S3_PREFIX}/${filename}" --content-type "application/json"
    fi
done

echo ""
echo "Upload complete!"
echo ""
echo "Files available at:"
echo "  s3://${BUCKET_NAME}/${S3_PREFIX}/complex_submission_001_mixed_use_portfolio.json"
echo "  s3://${BUCKET_NAME}/${S3_PREFIX}/complex_submission_002_industrial_portfolio.json"
echo "  s3://${BUCKET_NAME}/${S3_PREFIX}/complex_submission_003_hospitality_retail.json"
echo "  s3://${BUCKET_NAME}/${S3_PREFIX}/manifest.json"
